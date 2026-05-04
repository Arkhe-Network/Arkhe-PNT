# orchestrator_v160.py — Orquestrador unificado com as 4 extensões
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import numpy as np
import torch

@dataclass
class OrchestratorV160Config:
    # Deploy físico
    firmware_path: str
    device_registry_path: str
    tbeam_ports: List[Dict[str, str]]  # [{id, port}]

    # Fine-tuning contínuo
    sim_policy_path: str
    continual_learning_config: Dict

    # Oráculo dinâmico
    oracle_contract_address: str
    validator_private_key: str
    rpc_url: str

    # Relatório federado
    validator_public_keys: Dict[str, str]
    field_data_dir: str
    aggregation_window_seconds: int = 300
    checkpoint_interval_minutes: int = 60

class ArkheOrchestratorV160:
    """Orquestrador unificado com deploy físico, fine-tuning contínuo, oráculo dinâmico e relatório federado."""

    def __init__(self, config: OrchestratorV160Config):
        self.config = config
        self.running = False

        # Inicializar componentes
        from core.deploy.physical_deploy import PhysicalDeployManager
        self.deploy_manager = PhysicalDeployManager(
            firmware_path=config.firmware_path,
            device_registry_path=config.device_registry_path,
            orchestrator_private_key=config.validator_private_key
        )

        from core.ml.continual_learning import ContinualLearningPipeline, ContinualLearningConfig
        # Assuming LoRaCalibrationPolicy from field_transfer_learning or dummy here
        # import LoRaCalibrationPolicy
        # policy = LoRaCalibrationPolicy(state_dim=6, action_dim=3)

        from core.ml.continual_learning import PPOPolicy
        policy = PPOPolicy(6, 3)

        cl_config = ContinualLearningConfig(**config.continual_learning_config)
        self.continual_learner = ContinualLearningPipeline(
            policy=policy,
            config=cl_config,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )

        from core.oracle.dynamic_oracle_client import DynamicOracleClient
        self.oracle_client = DynamicOracleClient(
            rpc_url=config.rpc_url,
            contract_address=config.oracle_contract_address,
            validator_private_key=config.validator_private_key
        )

        from core.federated.federated_report_aggregator import FederatedReportAggregator
        self.report_aggregator = FederatedReportAggregator(
            validator_keys=config.validator_public_keys,
            aggregation_window_seconds=config.aggregation_window_seconds
        )
        try:
            self.report_aggregator.set_validator_key(config.validator_private_key)
        except Exception as e:
            print(f"Warning: Failed to set validator key {e}")

        # Estado
        self.deployed_devices: Dict[str, bool] = {}
        self.last_checkpoint = time.time()

    async def run_deployment_phase(self) -> Dict[str, bool]:
        """Fase 1: Deploy físico em T-Beams."""
        print("\n🚀 FASE 1: Deploy físico em T-Beams")
        results = await self.deploy_manager.deploy_cluster(
            devices=self.config.tbeam_ports,
            max_concurrent=3
        )
        self.deployed_devices = results
        return results

    async def run_data_collection_phase(self, duration_minutes: int = 30):
        """Fase 2: Coleta de dados em campo."""
        print(f"\n📡 FASE 2: Coleta de dados por {duration_minutes} minutos")
        # Simular coleta de dados dos dispositivos implantados
        # Em produção: ler de portas seriais/LoRa reais

        for device_id, deployed in self.deployed_devices.items():
            if not deployed:
                continue

            # Simular stream de dados do dispositivo
            for _ in range(duration_minutes * 2):  # 2 amostras/minuto
                # Dados simulados
                observation = np.random.randn(6) * 0.5 + np.array([10, 9, -70, 25, 80, 0])
                action = np.random.randint(3)
                reward = -abs(observation[0] - 5) * 0.1  # reward baseado em gap
                next_obs = observation + np.random.randn(6) * 0.1
                done = np.random.random() < 0.01
                metadata = {
                    'gap': abs(observation[0]),
                    'sf': observation[1],
                    'rssi': observation[2],
                    'temperature': observation[3],
                    'battery_pct': observation[4],
                    'hallucination': observation[5] > 0.5
                }

                # Adicionar ao continual learner
                self.continual_learner.add_experience(
                    observation, action, reward, next_obs, done, metadata
                )

                # Criar e submeter relatório de campo
                report = self._create_field_report(device_id, observation, metadata)
                if report:
                    self.report_aggregator.submit_report(report)

                await asyncio.sleep(30)  # 30s entre amostras

    def _create_field_report(
        self,
        node_id: str,
        observation: np.ndarray,
        metadata: Dict
    ):
        """Cria relatório de campo assinado."""
        from core.deploy.physical_deploy import DeviceAttestation
        from core.federated.federated_report_aggregator import FieldReport
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        # Dados do relatório
        metrics = {
            'gap': float(metadata['gap']),
            'sf': float(metadata['sf']),
            'rssi': float(metadata['rssi']),
            'temperature': float(metadata['temperature']),
            'battery_pct': float(metadata['battery_pct']),
            'hallucination_rate': 1.0 if metadata['hallucination'] else 0.0
        }

        # Hash dos dados brutos
        raw_data = json.dumps({
            'observation': observation.tolist(),
            'metadata': metadata
        }, sort_keys=True)
        raw_data_hash = hashlib.sha256(raw_data.encode()).hexdigest()

        # Assinar relatório (simulado — em produção: assinar no dispositivo)
        report_id = hashlib.sha256(
            f"{node_id}_{time.time()}_{raw_data_hash}".encode()
        ).hexdigest()[:16]

        # (Simulação: assinar com chave do orchestrator)
        if self.deploy_manager.orchestrator_key:
            message = json.dumps({
                'report_id': report_id,
                'node_id': node_id,
                'timestamp': time.time(),
                'metrics': metrics,
                'raw_data_hash': raw_data_hash
            }, sort_keys=True).encode()
            signature = self.deploy_manager.orchestrator_key.sign(
                message, ec.ECDSA(hashes.SHA256())
            )

            return FieldReport(
                report_id=report_id,
                node_id=node_id,
                timestamp=time.time(),
                metrics=metrics,
                raw_data_hash=raw_data_hash,
                signature=signature.hex(),
                public_key_pem=self.deploy_manager.orchestrator_key.public_key().public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            )

        return None

    async def run_continual_learning_phase(self, cycles: int = 5):
        """Fase 3: Fine-tuning contínuo com detecção de drift."""
        print(f"\n🤖 FASE 3: Fine-tuning contínuo ({cycles} ciclos)")

        # Carregar política de simulação como referência
        if Path(self.config.sim_policy_path).exists():
            self.continual_learner.policy.load_state_dict(
                torch.load(self.config.sim_policy_path, map_location=self.continual_learner.device)['policy_state_dict']
            )
            print(f"✅ Loaded reference policy from {self.config.sim_policy_path}")

        for cycle in range(cycles):
            print(f"  🔄 Cycle {cycle + 1}/{cycles}")

            # Verificar drift antes de treinar
            drift_score = self.continual_learner.drift_detector.get_drift_score()
            print(f"    📊 Drift score: {drift_score:.3f}")

            if drift_score > self.continual_learner.config.drift_threshold:
                print(f"    ⚠️ High drift detected, reducing KL regularization")
                self.continual_learner.config.kl_reg_lambda *= 0.5

            # Executar ciclo de treino
            history = self.continual_learner.run_training_cycle(steps=20)

            if history:
                avg_loss = np.mean([h['loss'] for h in history])
                print(f"    📈 Avg loss: {avg_loss:.4f}")

            # Salvar checkpoint periódico
            if time.time() - self.last_checkpoint > self.config.checkpoint_interval_minutes * 60:
                checkpoint_path = Path(self.config.field_data_dir) / f"checkpoint_{int(time.time())}.pt"
                self.continual_learner.save_policy(
                    str(checkpoint_path),
                    metadata={'cycle': cycle, 'drift_score': drift_score}
                )
                self.last_checkpoint = time.time()

            await asyncio.sleep(5)  # Pausa entre ciclos

    async def run_oracle_governance_phase(self):
        """Fase 4: Governança de oráculos dinâmicos."""
        print("\n🔗 FASE 4: Governança de oráculos")

        # Consultar oráculos ativos atuais
        for resource in ['energy_gj', 'compute_tflops', 'bandwidth_mbps']:
            try:
                active = self.oracle_client.get_active_oracles(resource)
                print(f"  📊 {resource}: {len(active)} active oracles")
                for oracle_id, confidence in active.items():
                    print(f"    • {oracle_id}: confidence={confidence:.3f}")
            except Exception as e:
                print(f"  ⚠️ Error fetching oracles for {resource}: {e}")

        # (Opcional) Propor novo oráculo se confiança média baixa
        # (Simulado: apenas log)
        print("  ℹ️  Oracle governance ready for proposals/votes")

    async def run_federated_reporting_phase(self):
        """Fase 5: Agregação federada de relatórios."""
        print("\n📊 FASE 5: Agregação federada de relatórios")

        # Tentar finalizar meta-relatório
        meta_report = self.report_aggregator.try_finalize_meta_report()

        if meta_report:
            print(f"  ✅ Meta-report finalized: {meta_report.meta_report_id}")
            print(f"  📈 Aggregated metrics:")
            for metric, stats in meta_report.aggregated_metrics.items():
                print(f"    • {metric}: mean={stats['mean']:.3f}, std={stats['std']:.3f}, n={stats['n']}")

            # Exportar para arquivo
            export_path = Path(self.config.field_data_dir) / f"meta_report_{meta_report.meta_report_id}.json"
            self.report_aggregator.export_meta_report(meta_report, str(export_path))

            # (Em produção) Registrar hash on-chain
            # registration = self.report_registry.register_report(...)

            return meta_report
        else:
            print("  ⏳ Not enough valid reports for consensus yet")
            return None

    async def execute_full_mission(self, mission, **kwargs):
        # Stub para a missao completa
        await self.run_full_cycle()
        return {"status": "success"}

    async def run_full_cycle(self):
        """Executa ciclo completo de produção."""
        print("=" * 80)
        print("ARKHE OS v∞.Ω.∇++++++++++.160 — PRODUCTION ORCHESTRATOR")
        print("=" * 80)

        self.running = True

        try:
            # Fase 1: Deploy
            deploy_results = await self.run_deployment_phase()
            successful_deploys = sum(deploy_results.values())
            print(f"✅ Deploy: {successful_deploys}/{len(deploy_results)} devices")

            if successful_deploys == 0:
                print("❌ No devices deployed, skipping remaining phases")
                return

            # Fase 2: Coleta de dados
            await self.run_data_collection_phase(duration_minutes=5)  # 5 min para demo

            # Fase 3: Fine-tuning contínuo
            await self.run_continual_learning_phase(cycles=3)

            # Fase 4: Governança de oráculos
            await self.run_oracle_governance_phase()

            # Fase 5: Relatório federado
            meta_report = await self.run_federated_reporting_phase()

            # Resumo final
            print("\n" + "=" * 80)
            print("[RESUMO FINAL]")
            print(f"  • Dispositivos implantados: {successful_deploys}")
            print(f"  • Experiências coletadas: {len(self.continual_learner.replay_buffer)}")
            print(f"  • Drift score final: {self.continual_learner.drift_detector.get_drift_score():.3f}")
            print(f"  • Meta-report: {'✅ Finalizado' if meta_report else '⏳ Pendente'}")
            print("=" * 80)

        finally:
            self.running = False

    def stop(self):
        """Para execução e salva estado final."""
        print("\n🛑 Stopping orchestrator...")
        self.running = False

        # Salvar política final
        final_path = Path(self.config.field_data_dir) / "final_policy.pt"
        self.continual_learner.save_policy(
            str(final_path),
            metadata={'status': 'final', 'timestamp': time.time()}
        )

        print("✅ Orchestrator stopped")
