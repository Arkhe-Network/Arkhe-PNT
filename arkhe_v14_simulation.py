#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arkhe_v14_simulation.py
Simulação do ARKHE-CALIBRATION-CONTROLLER v1.4 para o Bloco 419-Ω.
"""

import sys
import os

# Adiciona src ao path para importar o controlador
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from arkhe_core.calibration_controller import simulate_live_burn_v14
    SIMULATION_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar o controlador v1.4: {e}")
    SIMULATION_AVAILABLE = False

if __name__ == "__main__":
    if SIMULATION_AVAILABLE:
        simulate_live_burn_v14()
    else:
        sys.exit(1)
