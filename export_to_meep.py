#!/usr/bin/env python3
"""
export_to_meep.py
Exporta os perfis da simulação da matriz de vórtices para um formato estruturado
que pode ser consumido por ambientes de simulação fotônica (como Lumerical ou MEEP).
Gera um arquivo de estrutura de índice de refração (HDF5) ou script de inicialização.
"""
import numpy as np
import h5py
from pathlib import Path
import json

def create_meep_export(vortex_params_path=None, output_dir='results/meep_export'):
    """
    Gera arquivos de configuração e dados de matriz de índice de refração
    para importação no MEEP.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Parâmetros baseados na especificação
    pitch = 1e-6
    core_diameter = 300e-9
    dn_min, dn_max = 0.02, 0.08
    n_bg = 1.49 # Índice de refração típico do PMMA
    nx_vortex, ny_vortex = 10, 10

    # Grade de simulação espacial para MEEP (alta resolução)
    grid_res_nm = 50 # 50 nm resolução
    x_size = nx_vortex * pitch
    y_size = ny_vortex * pitch

    nx = int(x_size / (grid_res_nm * 1e-9))
    ny = int(y_size / (grid_res_nm * 1e-9))

    x = np.linspace(-x_size/2, x_size/2, nx)
    y = np.linspace(-y_size/2, y_size/2, ny)
    X, Y = np.meshgrid(x, y)

    # Gerar perfil de índice de refração n(x, y)
    n_profile = np.ones_like(X) * n_bg

    for i in range(nx_vortex):
        for j in range(ny_vortex):
            cx = (i - nx_vortex/2 + 0.5) * pitch
            cy = (j - ny_vortex/2 + 0.5) * pitch

            r = np.sqrt((X - cx)**2 + (Y - cy)**2)
            theta = np.arctan2(Y - cy, X - cx)

            # Modulação radial e de fase do vórtice no índice de refração
            radial_profile = np.exp(-((r - core_diameter/2)**2) / (2 * (core_diameter/4)**2))

            # Δn é mapeado da fase de 0 a 2pi para dn_min a dn_max
            # Aqui simulamos a variação de n diretamente
            dn_mod = dn_min + (dn_max - dn_min) * ((theta % (2*np.pi)) / (2*np.pi)) * radial_profile

            # Adiciona ao perfil base
            n_profile += dn_mod

    # Salvar matriz de índice de refração para MEEP (usando h5py)
    h5_path = Path(output_dir) / 'vortex_n_profile.h5'
    with h5py.File(h5_path, 'w') as f:
        f.create_dataset('epsilon', data=n_profile**2) # MEEP usa a constante dielétrica eps = n^2
        f.create_dataset('x', data=x)
        f.create_dataset('y', data=y)

    # Salvar script/configuração Python para o MEEP
    config = {
        'resolution_um': grid_res_nm * 1e-3,
        'cell_size_x_um': x_size * 1e6,
        'cell_size_y_um': y_size * 1e6,
        'cell_size_z_um': 3.0, # 1.5um depth + PMLs
        'background_index': n_bg,
        'geometry_file': 'vortex_n_profile.h5',
        'wavelength_range_nm': [400, 1550]
    }

    json_path = Path(output_dir) / 'meep_config.json'
    with open(json_path, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Exportação para MEEP concluída em {output_dir}")
    print(f" - {h5_path.name}: Matriz dielétrica")
    print(f" - {json_path.name}: Configurações do modelo")

if __name__ == '__main__':
    create_meep_export()