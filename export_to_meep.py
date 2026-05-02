import json
import os

def export():
    os.makedirs('exports/meep', exist_ok=True)
    config = {
        "cell_size": [14.0, 14.0, 4.5],
        "resolution": 50,
        "source": {
            "fcen": 0.825,
            "df": 0.625
        },
        "vortex_params": {
            "pitch": 1.0,
            "core_diameter": 0.3,
            "depth": 1.5,
            "dn_range": [0.02, 0.08],
            "array_size": [10, 10],
            "wavelength_range": [0.4, 1.55],
            "n_pixels": 1151
        }
    }
    with open('exports/meep/simulation_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("🔧 Creating MEEP simulation: exports/meep")
    print("✓ MEEP configuration saved: exports/meep/simulation_config.json")
    print("✅ Export to MEEP complete")

if __name__ == '__main__':
    export()
