# continual_learning.py — Pipeline de re-treinamento automático com detecção de drift
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import json
import hashlib
import time
from pathlib import Path

@dataclass
class ContinualLearningConfig:
    replay_buffer_size: int = 10000
    batch_size: int = 32
    inner_lr: float = 0.01
    meta_lr: float = 1e-4
    kl_reg_lambda: float = 0.1
    drift_threshold: float = 0.15  # threshold para detecção de drift
    min_samples_for_update: int = 100
    evaluation_interval: int = 50  # steps entre avaliações de drift

class ExperienceReplayBuffer:
    """Buffer circular para experience replay com amostragem por importância."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self.priorities: deque = deque(maxlen=capacity)

    def add(self, experience: Dict, priority: float = 1.0):
        """Adiciona experiência com prioridade (maior = mais importante)."""
        self.buffer.append(experience)
        self.priorities.append(priority)

    def sample(self, batch_size: int) -> Tuple[Dict, np.ndarray]:
        """Amostra batch com probabilidade proporcional à prioridade."""
        if len(self.buffer) < batch_size:
            # Retornar tudo se buffer pequeno
            indices = list(range(len(self.buffer)))
        else:
            # Amostrar por prioridade
            priorities = np.array(self.priorities)
            probs = priorities / (priorities.sum() + 1e-8)
            indices = np.random.choice(len(self.buffer), batch_size, p=probs, replace=False)

        batch = {}
        for key in self.buffer[0].keys():
            if isinstance(self.buffer[0][key], (np.ndarray, torch.Tensor)):
                batch[key] = torch.stack([self.buffer[i][key] for i in indices])
            else:
                batch[key] = [self.buffer[i][key] for i in indices]

        return batch, np.array([self.priorities[i] for i in indices])

    def update_priorities(self, indices: List[int], new_priorities: List[float]):
        """Atualiza prioridades após treino (ex: baseado em TD-error)."""
        for idx, priority in zip(indices, new_priorities):
            if 0 <= idx < len(self.priorities):
                self.priorities[idx] = max(priority, 1e-6)  # evitar zero

    def __len__(self):
        return len(self.buffer)

class DriftDetector:
    """Detecta drift de distribuição entre dados de simulação e campo."""

    def __init__(
        self,
        reference_stats: Dict[str, Tuple[float, float]],  # {feature: (mean, std)}
        threshold: float = 0.15,
        window_size: int = 100
    ):
        self.reference_stats = reference_stats
        self.threshold = threshold
        self.window_size = window_size
        self.current_window: deque = deque(maxlen=window_size)

    def add_sample(self, features: Dict[str, float]):
        """Adiciona amostra à janela deslizante."""
        self.current_window.append(features)

    def detect_drift(self) -> Dict[str, bool]:
        """Detecta drift por feature usando teste Z simplificado."""
        if len(self.current_window) < self.window_size // 2:
            return {}

        drift_results = {}
        for feature, (ref_mean, ref_std) in self.reference_stats.items():
            # Calcular estatísticas da janela atual
            values = [s[feature] for s in self.current_window if feature in s]
            if not values:
                continue

            curr_mean = np.mean(values)
            curr_std = np.std(values) + 1e-8

            # Teste Z: |mean_curr - mean_ref| / (std_ref / sqrt(n))
            n = len(values)
            z_score = abs(curr_mean - ref_mean) / (ref_std / np.sqrt(n) + 1e-8)

            # Drift se z_score > threshold * sqrt(n) (ajustado para tamanho da amostra)
            drift_results[feature] = z_score > self.threshold * np.sqrt(n)

        return drift_results

    def get_drift_score(self) -> float:
        """Retorna score agregado de drift [0, 1]."""
        drift_flags = self.detect_drift()
        if not drift_flags:
            return 0.0
        return np.mean(list(drift_flags.values()))

class ContinualLearningPipeline:
    """Pipeline de fine-tuning contínuo com detecção de drift e replay."""

    def __init__(
        self,
        policy: nn.Module,
        config: ContinualLearningConfig,
        reference_stats: Optional[Dict[str, Tuple[float, float]]] = None,
        device: str = 'cpu'
    ):
        self.policy = policy.to(device)
        self.config = config
        self.device = device
        self.optimizer = torch.optim.Adam(policy.parameters(), lr=config.meta_lr)

        # Buffer de replay
        self.replay_buffer = ExperienceReplayBuffer(config.replay_buffer_size)

        # Detector de drift
        self.drift_detector = DriftDetector(
            reference_stats or {},
            threshold=config.drift_threshold
        )

        # Estatísticas de referência (simulação)
        self.reference_stats = reference_stats or {}

        # Métricas
        self.training_history: deque = deque(maxlen=1000)
        self.last_update_step = 0

    def add_experience(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool,
        metadata: Optional[Dict] = None
    ):
        """Adiciona experiência ao buffer de replay."""
        experience = {
            'obs': torch.tensor(observation, dtype=torch.float32),
            'action': torch.tensor(action, dtype=torch.long),
            'reward': torch.tensor(reward, dtype=torch.float32),
            'next_obs': torch.tensor(next_observation, dtype=torch.float32),
            'done': torch.tensor(done, dtype=torch.float32),
            'timestamp': time.time(),
            **(metadata or {})
        }

        # Prioridade inicial baseada em reward absoluto (experiências extremas são mais importantes)
        priority = 1.0 + abs(reward)
        self.replay_buffer.add(experience, priority)

        # Atualizar detector de drift com features relevantes
        if metadata:
            self.drift_detector.add_sample(metadata)

    def compute_kl_regularization(self, old_policy: nn.Module, obs: torch.Tensor) -> torch.Tensor:
        """Computa regularização KL entre política antiga e nova."""
        with torch.no_grad():
            old_logits, _ = old_policy(obs)
            old_probs = torch.softmax(old_logits, dim=-1)

        new_logits, _ = self.policy(obs)
        new_probs = torch.softmax(new_logits, dim=-1)

        # KL divergence: sum p_old * log(p_old / p_new)
        kl = (old_probs * (torch.log(old_probs + 1e-8) - torch.log(new_probs + 1e-8))).sum(dim=-1).mean()
        return kl

    def train_step(self, batch: Dict, old_policy: Optional[nn.Module] = None) -> Dict[str, float]:
        """Um passo de treino com replay e regularização KL."""
        obs = batch['obs'].to(self.device)
        actions = batch['action'].to(self.device)
        rewards = batch['reward'].to(self.device)
        next_obs = batch['next_obs'].to(self.device)
        dones = batch['done'].to(self.device)

        # Forward pass
        logits, values = self.policy(obs)
        log_probs = torch.log_softmax(logits, dim=-1)
        selected_log_probs = log_probs.gather(1, actions.unsqueeze(-1)).squeeze(-1)

        # Advantage estimation (simplificado)
        with torch.no_grad():
            next_values = self.policy(next_obs)[1]
            targets = rewards + 0.99 * next_values * (1 - dones)
        advantages = targets - values

        # Policy loss + value loss
        policy_loss = -(selected_log_probs * advantages.detach()).mean()
        value_loss = nn.functional.mse_loss(values, targets)
        loss = policy_loss + 0.5 * value_loss

        # Regularização KL se política antiga fornecida
        if old_policy is not None and self.config.kl_reg_lambda > 0:
            kl_reg = self.compute_kl_regularization(old_policy, obs)
            loss = loss + self.config.kl_reg_lambda * kl_reg

        # Backward
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Atualizar prioridades do buffer baseado em TD-error
        td_errors = torch.abs(targets - values).detach().cpu().numpy()
        # (em produção: atualizar prioridades no buffer)

        return {
            'loss': loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'kl_reg': self.compute_kl_regularization(old_policy, obs).item() if old_policy else 0.0,
            'avg_reward': rewards.mean().item()
        }

    def should_update(self, step: int) -> bool:
        """Decide se deve executar update baseado em drift e volume de dados."""
        # Verificar volume mínimo
        if len(self.replay_buffer) < self.config.min_samples_for_update:
            return False

        # Verificar intervalo
        if step - self.last_update_step < self.config.evaluation_interval:
            return False

        # Verificar drift
        drift_score = self.drift_detector.get_drift_score()
        if drift_score > self.config.drift_threshold:
            print(f"  🚨 Drift detected: {drift_score:.3f} > {self.config.drift_threshold}")
            return True

        # Update periódico se sem drift significativo
        return (step - self.last_update_step) >= self.config.evaluation_interval * 2

    def run_training_cycle(
        self,
        steps: int = 100,
        old_policy: Optional[nn.Module] = None
    ) -> List[Dict[str, float]]:
        """Executa ciclo de treino contínuo."""
        history = []

        for step in range(steps):
            if not self.should_update(step):
                continue

            # Sample batch do replay buffer
            batch, priorities = self.replay_buffer.sample(self.config.batch_size)

            # Treinar
            metrics = self.train_step(batch, old_policy)
            metrics['step'] = self.last_update_step + step
            metrics['buffer_size'] = len(self.replay_buffer)
            metrics['drift_score'] = self.drift_detector.get_drift_score()

            history.append(metrics)
            self.last_update_step = metrics['step']

            # Log
            if step % 10 == 0:
                print(f"  🔄 Step {metrics['step']}: loss={metrics['loss']:.4f}, drift={metrics['drift_score']:.3f}, buffer={metrics['buffer_size']}")

        return history

    def save_policy(self, path: str, metadata: Optional[Dict] = None):
        """Salva política com metadados para versionamento."""
        checkpoint = {
            'policy_state_dict': self.policy.state_dict(),
            'config': asdict(self.config),
            'reference_stats': self.reference_stats,
            'training_history': list(self.training_history)[-100:],
            'metadata': metadata or {},
            'timestamp': time.time()
        }

        # Adicionar hash para integridade
        checkpoint['integrity_hash'] = hashlib.sha256(
            json.dumps(checkpoint, sort_keys=True, default=str).encode()
        ).hexdigest()

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(checkpoint, path)
        print(f"✅ Policy saved to {path}")

    def load_policy(self, path: str) -> bool:
        """Carrega política verificando integridade."""
        try:
            checkpoint = torch.load(path, map_location=self.device)

            # Verificar integridade
            stored_hash = checkpoint.pop('integrity_hash', None)
            computed_hash = hashlib.sha256(
                json.dumps(checkpoint, sort_keys=True, default=str).encode()
            ).hexdigest()

            if stored_hash and stored_hash != computed_hash:
                print(f"❌ Integrity check failed for {path}")
                return False

            # Carregar estado
            self.policy.load_state_dict(checkpoint['policy_state_dict'])
            self.config = ContinualLearningConfig(**checkpoint['config'])
            self.reference_stats = checkpoint.get('reference_stats', {})
            self.training_history.extend(checkpoint.get('training_history', []))

            print(f"✅ Policy loaded from {path}")
            return True

        except Exception as e:
            print(f"❌ Error loading policy: {e}")
            return False

class PPOPolicy(nn.Module):
    """
    Política Proximal Policy Optimization (PPO) completa para o agente.
    """
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.actor(x), self.critic(x)
