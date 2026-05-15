import asyncio
from arkhe_moire.bridge import MoireArkheBridge

async def demo():
    print("\n🧠 OTIMIZAÇÃO QNC DE ÂNGULOS CRÍTICOS:")
    bridge = MoireArkheBridge()

    # Treinar e otimizar para um novo material (ex.: CrI3)
    result = await bridge.run_qnc_optimization("CrI3", temperature_k=4.2)
    print(f"   • Material: {result['material']}")
    print(f"   • Ângulo ótimo encontrado: {result['optimal_angle']:.4f}°")
    print(f"   • Φ_C máximo alcançado: {result['max_phi_c']:.4f}")
    print(f"   • Selo temporal: {result.get('temporal_seal', 'simulado')}")

    # Otimizar para BaTiO3 2D
    result2 = await bridge.run_qnc_optimization("BaTiO3_2d", temperature_k=10.0)
    print(f"\n   • Material: {result2['material']}")
    print(f"   • Ângulo ótimo: {result2['optimal_angle']:.4f}° (T={result2['temperature_k']}K)")
    print(f"   • Φ_C máximo: {result2['max_phi_c']:.4f}")

if __name__ == "__main__":
    asyncio.run(demo())
