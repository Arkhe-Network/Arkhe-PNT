#!/usr/bin/env python3
"""
Sophon Hexagon v2.0 — Pygfx Integration with Sacred Geometry
Maps Sophon network coherence metrics to parabolic hexagonal wave interference.
"""
import numpy as np
import pygfx as gfx
import wgpu
from prometheus_api_client import PrometheusConnect
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from core.geometry.sacred_geometries import SacredTetrahedronParams, SacredCuboctahedronParams, SacredIcosahedronParams
import tkinter as tk
from core.visualization.sophon_bidirectional_ui import SophonBidirectionalUI

@dataclass
class SophonHexagonConfig:
    """Configuration for Sophon Hexagon visualization."""
    # Cavity geometry
    hex_radius: float = 1.0
    parabolic_depth: float = 0.5

    # Wave parameters
    base_frequency: float = 2.0
    coupling_strength: float = 0.1
    coherence_threshold: float = 0.6

    # Visualization
    mode: int = 1  # 0=volume, 1=isosurface, 2=topology
    color1: tuple = (0.0, 0.164, 1.0)    # Electric blue
    color2: tuple = (1.0, 0.0, 0.5)      # Magenta
    color3: tuple = (0.0, 1.0, 0.8)      # Cyan

    # Performance
    render_resolution: tuple = (1920, 1080)
    max_steps: int = 150

class SophonHexagonEngine:
    """Main engine for Sophon Hexagon visualization."""

    # Hexagonal wave directions (6 symmetry axes)
    HEX_DIRECTIONS = np.array([
        [1.0, 0.0],
        [0.5, np.sqrt(3)/2],
        [-0.5, np.sqrt(3)/2],
        [-1.0, 0.0],
        [-0.5, -np.sqrt(3)/2],
        [0.5, -np.sqrt(3)/2],
    ], dtype=np.float32)

    def __init__(self, config: SophonHexagonConfig = None,
                 prometheus_url: Optional[str] = None):
        self.config = config or SophonHexagonConfig()
        self.prom = PrometheusConnect(url=prometheus_url, disable_ssl=True) if prometheus_url else None

        # UI controls
        self.manual_amplitude_balance = 1.0
        self.active_geometry = "hexagon"
        self.num_waves = 6
        self.wave_directions = self.HEX_DIRECTIONS

        # Initialize UI inside the main thread (managed via manual polling)
        # Note: In a true production app, pygfx's event loop and tkinter's can be integrated.
        # Here we manually poll tkinter's update() in the render loop.
        self.tk_root = tk.Tk()
        self.ui = SophonBidirectionalUI(self.tk_root, self.config, self)

        # Initialize Pygfx
        self.renderer = gfx.renderers.WgpuRenderer(size=self.config.render_resolution)
        self.scene = gfx.Scene()
        self.camera = gfx.PerspectiveCamera(60, *self.config.render_resolution)
        self.camera.position.z = self.config.hex_radius * 3.5

        # Load and compile shader
        self._load_shader()
        self._create_pipeline()

        # Uniform buffer setup
        self._setup_uniforms()

        # Wave parameter state
        self._init_wave_parameters()

    def switch_geometry(self, geom_type: str):
        self.active_geometry = geom_type
        if geom_type == "tetrahedron":
            self.num_waves = 4
            params = SacredTetrahedronParams(base_frequency=1.0)
            dirs = params.wave_k_vectors()
        elif geom_type == "hexagon":
            self.num_waves = 6
            dirs = self.HEX_DIRECTIONS
        elif geom_type == "cuboctahedron":
            self.num_waves = 12
            params = SacredCuboctahedronParams(base_frequency=1.0)
            dirs = params.wave_k_vectors()
        elif geom_type == "icosahedron":
            self.num_waves = 20
            params = SacredIcosahedronParams(base_frequency=1.0)
            dirs = params.wave_k_vectors()

        # Normalize directions
        norms = np.linalg.norm(dirs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.wave_directions = (dirs / norms).astype(np.float32)

        self._init_wave_parameters()
        print(f"Switched geometry to {geom_type} with {self.num_waves} waves.")

    def _load_shader(self):
        """Load WGSL shader code."""
        with open("shaders/sophon_v2_polyhedron.wgsl", "r") as f:
            self.wgsl_code = f.read()

    def _create_pipeline(self):
        """Create Pygfx render pipeline with WGSL shader."""
        geometry = gfx.plane_geometry(2, 2, 1, 1)
        self.material = gfx.Material(
            vertex_shader="",
            fragment_shader=self.wgsl_code,
        )
        self.mesh = gfx.Mesh(geometry, self.material)
        self.scene.add(self.mesh)

    def _setup_uniforms(self):
        # time(1), pad(1), resolution(2), speed(1),
        # radius(1), parabolic_depth(1), pad(1) = 8

        # wave arrays (vec4 = 4 floats each):
        # amplitude[20] = 80
        # frequency[20] = 80
        # phase[20] = 80
        # direction[20] = 80
        # Total wave arrays = 320

        # num_waves(1), coupling_strength(1), coherence_threshold(1), mode(1) = 4

        # color1(4), color2(4), color3(4) = 12

        # Total buffer size = 8 + 320 + 4 + 12 = 344 floats

        self.uniform_data = np.zeros(344, dtype=np.float32)
        self.uniform_data[3] = 1.0 # speed
        self.uniform_data[4] = self.config.hex_radius
        self.uniform_data[5] = self.config.parabolic_depth

        self.uniform_data[328] = float(self.num_waves) # passed as float to WGSL
        self.uniform_data[329] = self.config.coupling_strength
        self.uniform_data[330] = self.config.coherence_threshold
        self.uniform_data[331] = float(self.config.mode)

        self.uniform_data[332:335] = self.config.color1
        self.uniform_data[335] = 1.0
        self.uniform_data[336:339] = self.config.color2
        self.uniform_data[339] = 1.0
        self.uniform_data[340:343] = self.config.color3
        self.uniform_data[343] = 1.0

        self.uniform_buffer = self.renderer.device.create_buffer_with_data(
            data=self.uniform_data,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
        )
        self.material.uniform_buffers = {"Uniforms": self.uniform_buffer}

    def _init_wave_parameters(self):
        self.wave_amplitudes = np.zeros(20, dtype=np.float32)
        self.wave_amplitudes[:self.num_waves] = 0.7

        self.wave_frequencies = np.zeros(20, dtype=np.float32)
        self.wave_frequencies[:self.num_waves] = self.config.base_frequency

        self.wave_phases = np.zeros(20, dtype=np.float32)

        self.wave_dirs_padded = np.zeros((20, 2), dtype=np.float32)
        self.wave_dirs_padded[:self.num_waves] = self.wave_directions

        self._update_wave_uniforms()

    def _update_wave_uniforms(self):
        for i in range(20):
            # Each element is a vec4<f32>, so it occupies 4 floats (stride of 16 bytes).
            # Amplitude offset: 8
            self.uniform_data[8 + i*4] = self.wave_amplitudes[i]
            # Frequency offset: 8 + 80 = 88
            self.uniform_data[88 + i*4] = self.wave_frequencies[i]
            # Phase offset: 88 + 80 = 168
            self.uniform_data[168 + i*4] = self.wave_phases[i]
            # Direction offset: 168 + 80 = 248
            self.uniform_data[248 + i*4:248 + i*4 + 2] = self.wave_dirs_padded[i]

        self.uniform_data[328] = float(self.num_waves)
        self.uniform_data[329] = self.config.coupling_strength

    def fetch_sophon_metrics(self) -> Dict[str, float]:
        if not self.prom:
            return {
                'coherence_distance': 0.29,
                'delivery_rate': 0.97,
                'cache_hit_rate': 0.81,
                'ber': 8e-5,
            }

        queries = {
            'coherence_distance': 'avg(sophon_coherence_distance{job="sophon-nodes"})',
            'delivery_rate': 'avg(sophon_delivery_rate{job="sophon-nodes"})',
            'cache_hit_rate': 'avg(sophon_jones_cache_hit_rate{job="sophon-nodes"})',
            'ber': 'avg(sophon_bit_error_rate{job="sophon-nodes", transducer_enabled="true"})',
        }

        metrics = {}
        for name, query in queries.items():
            try:
                result = self.prom.custom_query(query=query)
                metrics[name] = float(result[0]['value'][1])
            except Exception:
                metrics[name] = None
        return metrics

    def metrics_to_wave_params(self, metrics: Dict[str, float]):
        coh_dist = metrics.get('coherence_distance', 0.3)
        delivery = metrics.get('delivery_rate', 0.97)
        cache_hit = metrics.get('cache_hit_rate', 0.81)

        balance = np.clip(1.0 - coh_dist * 1.5, 0.3, 1.0) * self.manual_amplitude_balance
        self.wave_amplitudes[:self.num_waves] = np.full(self.num_waves, 0.5 + balance * 0.5, dtype=np.float32)

        base_freq = self.config.base_frequency
        self.wave_frequencies[:self.num_waves] = np.full(self.num_waves, base_freq * (1.0 + delivery * 2.0), dtype=np.float32)

        phase_spread = np.pi * (1.0 - cache_hit)
        self.wave_phases[:self.num_waves] = np.array([
            i * phase_spread / float(self.num_waves) for i in range(self.num_waves)
        ], dtype=np.float32)

        self._update_wave_uniforms()

    def update(self):
        try:
            self.tk_root.update()
        except tk.TclError:
            pass # UI closed

        metrics = self.fetch_sophon_metrics()
        self.metrics_to_wave_params(metrics)

        elapsed = self.renderer.get_elapsed_time()
        self.uniform_data[0] = elapsed
        self.uniform_data[2:4] = self.renderer.get_logical_size()

        self.renderer.device.queue.write_buffer(
            self.uniform_buffer, 0, self.uniform_data
        )
        self.renderer.render(self.scene, self.camera)

    def run(self):
        import time

        print(f"🔮 Sophon Polyhedron v2.0 — Sacred Geometry Visualization")

        # Event handler for mode switching
        def on_key(event):
            if event.key in ['0', '1', '2']:
                self.config.mode = int(event.key)
                self.uniform_data[331] = float(self.config.mode)

        self.renderer.add_event_handler(on_key, "key_down")

        while True:
            self.update()
            self.renderer.request_draw()
            time.sleep(1/60)

if __name__ == "__main__":
    engine = SophonHexagonEngine()
    # engine.run() # Un-comment to test locally
