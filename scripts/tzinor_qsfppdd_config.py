# -*- coding: utf-8 -*-
"""
tzinor_qsfppdd_config.py
Configuração técnica dos transceptores QSFPDD-400G-ZR para a rede Tzinor.
Synapse-id: 847.762-OPT
"""

ARKHE_QSFPDD_CONFIG = {
    "node_type": "tzinor_repeater",
    "blockchain_anchor": "847.762",

    "hardware_specs": {
        "form_factor": "QSFP-DD",
        "data_rate": "400 Gbps",
        "modulation": "16-QAM",
        "wavelength_nm": 1550.12,
        "launch_power_target_dbm": -8.0,
        "receiver_sensitivity_dbm": -24.0,
        "link_budget_db": 16.0
    },

    "latency_optimization": {
        "classical_latency_ns": 1000,  # 1µs para 200m
        "quantum_latency_target_ns": 20,  # 50x ganho retrocausal
        "pre_ack_window_ns": 15,  # Janela de pre-ACK
        "buffer_size": "1MB",  # Buffer circular
        "jitter_max_ns": 0.5
    },

    "coherence_preservation": {
        "phi_coupling": 0.61803398875,  # Acoplamento áureo φ
        "eta_correction": 0.45,  # Correção de síndrome
        "phase_lock_loop": {
            "reference": "Sr-88_Central",
            "frequency_thz": 319.45,
            "stability_allan": 1e-15,
            "lock_bandwidth_hz": 10000
        }
    },

    "handshake_protocol": {
        "type": "retrocausal_qhttp",
        "ack_type": "PRE-ACK",
        "timeout_us": 9.25,
        "entropy_source": "QRNG-ONBOARD-400G"
    },

    "error_correction": {
        "classical_fec": "KP4",
        "quantum_syndrome": "STEANE-7-3",
        "interleaving_depth": 128
    },

    "dwdm_allocation": {
        "C21": {"freq_thz": 192.1, "use": "ETH_400G"},
        "C22": {"freq_thz": 192.2, "use": "SR88_SYNC"},
        "C23": {"freq_thz": 192.3, "use": "RETROCAUSAL_QHTTP"},
        "C24": {"freq_thz": 192.4, "use": "BIOLINK_40HZ"}
    }
}

def get_node_config(node_id):
    """Retorna configuração específica para um nó da rede"""
    config = ARKHE_QSFPDD_CONFIG.copy()
    config["node_id"] = node_id
    return config
