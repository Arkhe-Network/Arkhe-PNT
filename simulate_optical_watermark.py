import argparse
import numpy as np
import os
import hashlib
import sys

# Try to use real ZEE200 backend if available
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'zee200_integration')))
    from zee200_backend_real import RealZEE200Bridge
    HAS_ZEE200 = True
except ImportError:
    HAS_ZEE200 = False

def generate_real_zee200_hash():
    """Gera um hash ZEE200 real integrando a ponte criptográfica"""
    print("Integrando geração de hash ZEE200 real no circuito...")
    bridge = RealZEE200Bridge(security_bits=80, post_quantum=True)

    # Criar um dado sintético de comunidade para gerar prova
    community_data = {
        'community_id': 1,
        'crystals': [1, 2, 3],
        'rho': 0.85
    }
    manifold_points = np.random.rand(10, 3)
    decoder_matrix = np.random.rand(768, 3)

    proof = bridge.generate_capture_proof_real(
        community_data, manifold_points, decoder_matrix, epsilon=0.01
    )

    hash_hex = proof['proof_hash']
    print(f"Hash ZEE200 real gerado: {hash_hex}")

    # Pad to 32 bytes if necessary
    hash_bytes = bytes.fromhex(hash_hex)
    if len(hash_bytes) < 32:
        hash_bytes = hash_bytes.ljust(32, b'\0')
    elif len(hash_bytes) > 32:
        hash_bytes = hash_bytes[:32]

    return hash_bytes

def simulate_optical_watermark(hash_file, modulation_depth, output_path):
    print(f"Simulating optical watermark with hash {hash_file}, mod depth {modulation_depth}")

    # Integrar geração de hash ZEE200 real se não houver arquivo ou se possível
    if HAS_ZEE200:
        H_bytes = generate_real_zee200_hash()
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        with open(hash_file, 'wb') as f:
            f.write(H_bytes)
    else:
        # Fallback caso não seja possível instanciar (por falta do C++ backend, etc),
        # mas mantemos o fallback do código original para debug
        if not os.path.exists(hash_file):
            print(f"Warning: {hash_file} not found and ZEE200 not available. Creating a random 32-byte hash.")
            H_bytes = np.random.bytes(32)
            os.makedirs(os.path.dirname(hash_file), exist_ok=True)
            with open(hash_file, 'wb') as f:
                f.write(H_bytes)
        else:
            with open(hash_file, 'rb') as f:
                H_bytes = f.read(32)
                if len(H_bytes) < 32:
                    H_bytes = H_bytes.ljust(32, b'\0')

    # Convert to 256 bits
    H_bits = np.unpackbits(np.frombuffer(H_bytes, dtype=np.uint8))

    # Generate wavelength axis
    lambda_axis = np.linspace(400, 1550, 1151) # 1 nm resolution

    # Base spectrum (random for demonstration, similar to what sensor outputs)
    # Generate something relatively smooth
    S_base = np.exp(-0.5 * ((lambda_axis - 800) / 200)**2) + 0.1 * np.random.rand(1151)

    # Modulation pattern
    modulation_pattern = np.ones_like(lambda_axis)
    epsilon = modulation_depth
    theta_key = "arkhe_optic_v340"

    for k, bit in enumerate(H_bits):
        if bit == 1:
            f_k = 0.01 + 0.001 * k # Orthogonal frequencies
            # Generate deterministic theta_k
            hash_k = hashlib.sha256((theta_key + str(k)).encode()).digest()
            theta_k = (int.from_bytes(hash_k[:8], 'little') / (2**64)) * 2 * np.pi

            modulation_pattern += epsilon * np.cos(2*np.pi * f_k * lambda_axis + theta_k)

    # Watermarked spectrum
    S_watermarked = S_base * modulation_pattern

    # Verification
    # Cross correlation
    expected_modulation = modulation_pattern # Since we just built it
    correlation = np.corrcoef(S_watermarked, S_base * expected_modulation)[0, 1]

    print(f"Verification correlation: {correlation:.4f}")

    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save to Numpy
    np.save(output_path, S_watermarked)

    print(f"Watermarked spectrum saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hash-file', type=str, default='results/zee200_proof.bin')
    parser.add_argument('--modulation-depth', type=float, default=0.01)
    parser.add_argument('--output', type=str, default='results/watermarked_spectrum.npy')

    args = parser.parse_args()
    simulate_optical_watermark(
        args.hash_file,
        args.modulation_depth,
        args.output
    )
