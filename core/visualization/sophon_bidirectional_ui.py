#!/usr/bin/env python3
"""
Sophon Bidirectional UI
Provides a UI for manual adjustment of shader parameters and network thresholds.
"""
import tkinter as tk
from tkinter import ttk
import json

class SophonBidirectionalUI:
    def __init__(self, root, config_ref=None, engine_ref=None):
        self.root = root
        self.root.title("Sophon Bidirectional Controls")

        self.config_ref = config_ref
        self.engine_ref = engine_ref

        self.create_widgets()

    def create_widgets(self):
        # Geometry Switcher Frame
        geom_frame = ttk.LabelFrame(self.root, text="Geometry Type")
        geom_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.geom_var = tk.StringVar(value="Hexagon (6)")
        geoms = ["Tetrahedron (4)", "Hexagon (6)", "Cuboctahedron (12)", "Icosahedron (20)"]
        geom_combo = ttk.Combobox(geom_frame, textvariable=self.geom_var, values=geoms, state="readonly")
        geom_combo.grid(row=0, column=0, sticky="ew")
        geom_combo.bind("<<ComboboxSelected>>", self.on_geom_change)

        # Shader Parameters Frame
        shader_frame = ttk.LabelFrame(self.root, text="Shader Parameters")
        shader_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Amplitude
        ttk.Label(shader_frame, text="Amplitude Balance:").grid(row=0, column=0, sticky="w")
        self.amplitude_var = tk.DoubleVar(value=1.0)
        amplitude_scale = ttk.Scale(shader_frame, from_=0.0, to=2.0, variable=self.amplitude_var, orient="horizontal")
        amplitude_scale.grid(row=0, column=1, sticky="ew")

        # Frequency
        ttk.Label(shader_frame, text="Base Frequency:").grid(row=1, column=0, sticky="w")
        self.frequency_var = tk.DoubleVar(value=2.0)
        frequency_scale = ttk.Scale(shader_frame, from_=0.1, to=10.0, variable=self.frequency_var, orient="horizontal")
        frequency_scale.grid(row=1, column=1, sticky="ew")

        # Coupling
        ttk.Label(shader_frame, text="Coupling Strength:").grid(row=2, column=0, sticky="w")
        self.coupling_var = tk.DoubleVar(value=0.1)
        coupling_scale = ttk.Scale(shader_frame, from_=0.0, to=1.0, variable=self.coupling_var, orient="horizontal")
        coupling_scale.grid(row=2, column=1, sticky="ew")

        # Network Thresholds Frame
        network_frame = ttk.LabelFrame(self.root, text="Network Thresholds")
        network_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Delivery Threshold
        ttk.Label(network_frame, text="Delivery Threshold:").grid(row=0, column=0, sticky="w")
        self.delivery_thresh_var = tk.DoubleVar(value=0.95)
        delivery_scale = ttk.Scale(network_frame, from_=0.0, to=1.0, variable=self.delivery_thresh_var, orient="horizontal")
        delivery_scale.grid(row=0, column=1, sticky="ew")

        # Coherence Threshold
        ttk.Label(network_frame, text="Coherence Distance Threshold:").grid(row=1, column=0, sticky="w")
        self.coherence_thresh_var = tk.DoubleVar(value=0.35)
        coherence_scale = ttk.Scale(network_frame, from_=0.0, to=1.0, variable=self.coherence_thresh_var, orient="horizontal")
        coherence_scale.grid(row=1, column=1, sticky="ew")

        # Apply Button
        apply_btn = ttk.Button(self.root, text="Apply Changes", command=self.apply_changes)
        apply_btn.grid(row=3, column=0, pady=10)

    def on_geom_change(self, event):
        val = self.geom_var.get()
        if self.engine_ref:
            if "Tetrahedron" in val:
                self.engine_ref.switch_geometry("tetrahedron")
            elif "Hexagon" in val:
                self.engine_ref.switch_geometry("hexagon")
            elif "Cuboctahedron" in val:
                self.engine_ref.switch_geometry("cuboctahedron")
            elif "Icosahedron" in val:
                self.engine_ref.switch_geometry("icosahedron")

    def apply_changes(self):
        settings = {
            "shader": {
                "amplitude_balance": self.amplitude_var.get(),
                "base_frequency": self.frequency_var.get(),
                "coupling_strength": self.coupling_var.get()
            },
            "network": {
                "delivery_threshold": self.delivery_thresh_var.get(),
                "coherence_distance_threshold": self.coherence_thresh_var.get()
            }
        }
        print("Applied Settings:")
        print(json.dumps(settings, indent=2))

        if self.config_ref:
            self.config_ref.base_frequency = self.frequency_var.get()
            self.config_ref.coupling_strength = self.coupling_var.get()

        if self.engine_ref:
            self.engine_ref.manual_amplitude_balance = self.amplitude_var.get()

def update_ui(root, engine_ref):
    if engine_ref:
        pass
    root.update()
