# physical_deploy.py — Deploy em T-Beams com verificação criptográfica
import subprocess
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.backends import default_backend
import serial
import asyncio

@dataclass
class DeviceAttestation:
    device_id: str
    firmware_hash: str
    nonce: int
    signature: str  # ECDSA signature hex
    timestamp: float
    public_key_pem: str

class PhysicalDeployManager:
    """Gerencia deploy físico em T-Beams com attestation criptográfica."""

    def __init__(
        self,
        firmware_path: str,
        device_registry_path: str,  # JSON com {device_id: public_key_pem}
        orchestrator_private_key: str,
        espflash_path: str = "espflash"
    ):
        self.firmware_path = firmware_path
        self.espflash = espflash_path
        self.orchestrator_key = ec.derive_private_key(
            int.from_bytes(hashlib.sha256(orchestrator_private_key.encode()).digest(), 'big'),
            ec.SECP256R1(),
            default_backend()
        )

        # Carregar registro de dispositivos confiáveis
        try:
            with open(device_registry_path) as f:
                self.device_registry = json.load(f)
        except:
            self.device_registry = {}

        self.deployed_devices: Dict[str, DeviceAttestation] = {}

    def compute_firmware_hash(self) -> str:
        """Computa SHA256 do firmware binário."""
        sha256 = hashlib.sha256()
        with open(self.firmware_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def generate_attestation_challenge(self, device_id: str) -> Dict:
        """Gera desafio de attestation para um dispositivo."""
        nonce = int(time.time() * 1e6)  # microsecond timestamp
        firmware_hash = self.compute_firmware_hash()

        # Mensagem a ser assinada pelo dispositivo
        message = f"{firmware_hash}|{nonce}|{device_id}"

        return {
            'device_id': device_id,
            'firmware_hash': firmware_hash,
            'nonce': nonce,
            'message': message,
            'timestamp': time.time()
        }

    def flash_device(
        self,
        device_id: str,
        port: str,
        baud: int = 460800,
        verify: bool = True
    ) -> bool:
        """Faz flash do firmware no dispositivo via espflash."""
        try:
            # Comando espflash
            cmd = [
                self.espflash, 'flash',
                '--chip', 'esp32c3',
                '--port', port,
                '--baud', str(baud),
                self.firmware_path
            ]
            if verify:
                cmd.append('--verify')

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"❌ Flash failed for {device_id}: {result.stderr}")
                return False

            print(f"✅ Flash successful for {device_id}")
            return True

        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout flashing {device_id}")
            return False
        except Exception as e:
            print(f"❌ Error flashing {device_id}: {e}")
            return False

    def verify_attestation(
        self,
        device_id: str,
        attestation: DeviceAttestation
    ) -> bool:
        """Verifica assinatura ECDSA do dispositivo."""
        if device_id not in self.device_registry:
            print(f"⚠️ Unknown device: {device_id}")
            return False

        # Carregar chave pública do dispositivo
        public_key_pem = self.device_registry[device_id]
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(), backend=default_backend()
        )

        # Reconstruir mensagem
        message = f"{attestation.firmware_hash}|{attestation.nonce}|{attestation.device_id}"

        try:
            # Verificar assinatura
            signature = bytes.fromhex(attestation.signature)
            public_key.verify(
                signature,
                message.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception as e:
            print(f"❌ Attestation verification failed for {device_id}: {e}")
            return False

    async def deploy_to_device(
        self,
        device_id: str,
        port: str,
        timeout_seconds: int = 300
    ) -> Optional[DeviceAttestation]:
        """Fluxo completo: flash → attestation → verificação."""
        print(f"🔧 Deploying to {device_id} on {port}...")

        # 1. Flash do firmware
        if not self.flash_device(device_id, port):
            return None

        # 2. Aguardar boot e conexão serial
        await asyncio.sleep(5)

        # 3. Gerar desafio de attestation
        challenge = self.generate_attestation_challenge(device_id)

        # 4. Enviar desafio via serial (simulado — em produção: protocolo customizado)
        # Em produção: enviar challenge via LoRa/serial e receber resposta assinada
        # Aqui: simular resposta do dispositivo
        device_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        message = challenge['message']
        signature = device_private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))

        attestation = DeviceAttestation(
            device_id=device_id,
            firmware_hash=challenge['firmware_hash'],
            nonce=challenge['nonce'],
            signature=signature.hex(),
            timestamp=time.time(),
            public_key_pem=device_private_key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        )

        # 5. Verificar attestation
        if not self.verify_attestation(device_id, attestation):
            print(f"❌ Attestation failed for {device_id}")
            return None

        # 6. Registrar dispositivo implantado
        self.deployed_devices[device_id] = attestation
        print(f"✅ {device_id} deployed and attested")

        return attestation

    async def deploy_cluster(
        self,
        devices: List[Dict[str, str]],  # [{id, port}, ...]
        max_concurrent: int = 3
    ) -> Dict[str, bool]:
        """Deploy paralelo em múltiplos dispositivos."""
        semaphore = asyncio.Semaphore(max_concurrent)
        results = {}

        async def deploy_one(device: Dict):
            async with semaphore:
                attestation = await self.deploy_to_device(device['id'], device['port'])
                results[device['id']] = attestation is not None
                return results[device['id']]

        tasks = [deploy_one(d) for d in devices]
        await asyncio.gather(*tasks)

        success_count = sum(results.values())
        print(f"\n📊 Deploy cluster: {success_count}/{len(devices)} devices successful")
        return results
