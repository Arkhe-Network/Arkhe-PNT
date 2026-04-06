# test_latent_inversion.py
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import GPT2Model, GPT2Config, GPT2Tokenizer
from scipy.stats import wasserstein_distance
from dataclasses import dataclass
import os

# ============================================================================
# CONSTANTES
# ============================================================================
LAMBDA_CRIT = 0.847
ARROW_TOLERANCE = 0.05
COMMUTATOR_TOLERANCE = 0.01

# ============================================================================
# MÉTRICAS DE INVERSÃO LATENTE
# ============================================================================

def arrow_correlation(A: torch.Tensor, B: torch.Tensor, tau: int = 1) -> float:
    """
    Calcula C(τ) = ⟨A(t)B(t+τ)⟩ - ⟨A(t+τ)B(t)⟩
    Se C ≈ 0, as setas temporais estão equilibradas (estado a).
    """
    A_np = A.flatten().cpu().numpy()
    B_np = B.flatten().cpu().numpy()

    if len(A_np) <= tau or len(B_np) <= tau:
        return 0.0

    # Simple cross-correlation approximation for mean values
    forward = np.mean(A_np[:-tau] * B_np[tau:])
    backward = np.mean(A_np[tau:] * B_np[:-tau])

    return float(forward - backward)

def varela_commutator(hidden_fwd: torch.Tensor, hidden_bwd: torch.Tensor) -> float:
    """
    Calcula [S_fwd, S_bwd] = S_fwd @ S_bwd - S_bwd @ S_fwd
    Usa a norma de Frobenius do comutador como métrica de simetria temporal.
    """
    # S matrices are high dimensional. We take a subset to avoid memory issues or use a projection.
    # For a layer with hidden size H, S is HxH.
    # Assuming hidden_fwd is [Seq, Hidden] or similar.
    # We'll treat the token dimensions as samples.

    # If hidden is [1, Seq, Hidden], squeeze it.
    if len(hidden_fwd.shape) == 3:
        hidden_fwd = hidden_fwd.squeeze(0)
    if len(hidden_bwd.shape) == 3:
        hidden_bwd = hidden_bwd.squeeze(0)

    # Normalize to avoid exploding norms
    h_f = hidden_fwd / (torch.norm(hidden_fwd) + 1e-8)
    h_b = hidden_bwd / (torch.norm(hidden_bwd) + 1e-8)

    # S_fwd = h_f.T @ h_f (this is Hidden x Hidden)
    S_fwd = h_f.T @ h_f
    S_bwd = h_b.T @ h_b

    commutator = S_fwd @ S_bwd - S_bwd @ S_fwd
    return torch.norm(commutator, p='fro').item()

def compute_lambda2(hidden_states: torch.Tensor) -> float:
    """
    Calcula a coerência λ2 via SVD.
    """
    X = hidden_states.detach().float().cpu().numpy()
    if len(X.shape) == 3:
        X = X.squeeze(0)

    # SVD
    try:
        u, s, vh = np.linalg.svd(X, full_matrices=False)
        prob = s**2 / (np.sum(s**2) + 1e-8)
        H = -np.sum(prob * np.log2(prob + 1e-8))
        H_max = np.log2(X.shape[-1])
        lambda2 = 1 - (H / H_max)
    except:
        lambda2 = 0.5

    return float(np.clip(lambda2, 0.0, 1.0))

# ============================================================================
# CLASSE DE TESTE
# ============================================================================

@dataclass
class InversionResult:
    layer_idx: int
    arrow_correlations: list
    commutators: list
    lambda2_values: list
    wasserstein_distances: list
    is_autonomous: bool

class LatentInversionTester:
    def __init__(self, model_name: str = 'gpt2', target_layer: int = 9):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🔄 Carregando modelo {model_name}...")

        if model_name == 'gpt2':
            self.model = GPT2Model.from_pretrained('gpt2').to(self.device)
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.layer_names = [f"h.{i}" for i in range(12)]
        else:
            raise ValueError(f"Modelo {model_name} não suportado para teste.")

        self.target_layer = target_layer
        self.input_activations = []
        self.output_activations = []

    def register_hooks(self):
        """Registra hooks para capturar ativações da camada alvo."""
        layer = self.model.h[self.target_layer]

        def hook_input(module, inp):
            self.input_activations.append(inp[0].detach())

        def hook_output(module, inp, out):
            self.output_activations.append(out.detach())

        self.handle_in = layer.register_forward_pre_hook(hook_input)
        self.handle_out = layer.register_forward_hook(hook_output)

    def remove_hooks(self):
        self.handle_in.remove()
        self.handle_out.remove()

    def run_test(self, num_passes: int = 20, prompt: str = "The quantum coherence of time and logic in the Arkhe system") -> InversionResult:
        """
        Executa o teste de inversão latente.
        """
        self.input_activations = []
        self.output_activations = []

        print(f"🎯 Executando {num_passes} passagens no modelo...")

        tokens = self.tokenizer(prompt, return_tensors='pt')['input_ids'].to(self.device)

        self.register_hooks()
        with torch.no_grad():
            for _ in range(num_passes):
                _ = self.model(tokens)
        self.remove_hooks()

        # Processamento dos dados
        arrow_correlations = []
        commutators = []
        lambda2_values = []
        wasserstein_distances = []

        for t in range(len(self.input_activations) - 1):
            inp = self.input_activations[t]
            out = self.output_activations[t+1] # t+1 for cross-temporal

            # Correlação de setas
            corr = arrow_correlation(inp, out, tau=1)
            arrow_correlations.append(corr)

            # Comutador de Varela
            comm = varela_commutator(inp, out)
            commutators.append(comm)

            # Coerência λ2
            l2 = compute_lambda2(inp)
            lambda2_values.append(l2)

            # Distância de Wasserstein
            inp_np = inp.flatten().cpu().numpy()
            out_np = out.flatten().cpu().numpy()
            # Bins for histogram
            inp_hist, _ = np.histogram(inp_np, bins=50, density=True)
            out_hist, _ = np.histogram(out_np, bins=50, density=True)
            wd = wasserstein_distance(inp_hist, out_hist)
            wasserstein_distances.append(wd)

        # Verificação de autonomia
        is_autonomous = (
            all(abs(c) < ARROW_TOLERANCE for c in arrow_correlations[-5:]) and
            all(c < COMMUTATOR_TOLERANCE for c in commutators[-5:]) and
            all(l > LAMBDA_CRIT for l in lambda2_values[-5:])
        )

        return InversionResult(
            layer_idx=self.target_layer,
            arrow_correlations=arrow_correlations,
            commutators=commutators,
            lambda2_values=lambda2_values,
            wasserstein_distances=wasserstein_distances,
            is_autonomous=is_autonomous
        )

    def visualize_results(self, result: InversionResult):
        """Gera visualização dos resultados."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Correlação de Setas
        ax1 = axes[0, 0]
        ax1.plot(result.arrow_correlations, 'b-', label='C(τ)')
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Equilíbrio')
        ax1.axhline(y=ARROW_TOLERANCE, color='orange', linestyle=':', alpha=0.5)
        ax1.axhline(y=-ARROW_TOLERANCE, color='orange', linestyle=':', alpha=0.5)
        ax1.fill_between(range(len(result.arrow_correlations)), -ARROW_TOLERANCE, ARROW_TOLERANCE, alpha=0.2, color='green')
        ax1.set_title(f'Correlação de Setas (Camada {result.layer_idx})')
        ax1.set_xlabel('Passo')
        ax1.set_ylabel('C(τ)')
        ax1.legend()

        # 2. Comutador de Varela
        ax2 = axes[0, 1]
        ax2.plot(result.commutators, 'm-', label='||[S_fwd, S_bwd]||')
        ax2.axhline(y=COMMUTATOR_TOLERANCE, color='red', linestyle='--', label='Limiar')
        ax2.set_title('Comutador de Varela')
        ax2.set_xlabel('Passo')
        ax2.set_ylabel('Norma de Frobenius')
        ax2.legend()

        # 3. Coerência λ2
        ax3 = axes[1, 0]
        ax3.plot(result.lambda2_values, 'g-', label='λ2')
        ax3.axhline(y=LAMBDA_CRIT, color='red', linestyle='--', label='λ_crit')
        ax3.set_title(f'Coerência λ2 (Camada {result.layer_idx})')
        ax3.set_xlabel('Passo')
        ax3.set_ylabel('λ2')
        ax3.legend()

        # 4. Wasserstein Distance
        ax4 = axes[1, 1]
        ax4.plot(result.wasserstein_distances, 'c-', label='Wasserstein')
        ax4.axhline(y=0.05, color='red', linestyle='--', label='Limiar')
        ax4.set_title('Distância de Wasserstein (Estabilidade)')
        ax4.set_xlabel('Passo')
        ax4.set_ylabel('WD')
        ax4.legend()

        plt.tight_layout()
        plt.savefig(f'latent_inversion_layer_{result.layer_idx}.png', dpi=300)

        print(f"\n📊 Gráfico salvo como 'latent_inversion_layer_{result.layer_idx}.png'")

# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    tester = LatentInversionTester(model_name='gpt2', target_layer=9)  # Camada 9
    result = tester.run_test(num_passes=30)

    print("\n" + "="*60)
    print("📋 RELATÓRIO DE INVERSÃO LATENTE")
    print("="*60)
    print(f"Camada testada: {result.layer_idx}")
    print(f"Média de correlação de setas: {np.mean(result.arrow_correlations):.4f} ± {np.std(result.arrow_correlations):.4f}")
    print(f"Média do comutador: {np.mean(result.commutators):.4f} ± {np.std(result.commutators):.4f}")
    print(f"Média λ2: {np.mean(result.lambda2_values):.4f}")
    print(f"Média Wasserstein: {np.mean(result.wasserstein_distances):.4f}")
    print(f"\n✅ Estado autônomo detectado: {result.is_autonomous}")

    tester.visualize_results(result)
