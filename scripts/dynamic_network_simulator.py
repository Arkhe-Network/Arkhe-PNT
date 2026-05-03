#!/usr/bin/env python3
"""
dynamic_network_simulator.py — Mobile Sophon nodes with coherence-based routing.
Models nodes as boids (flocking birds) carrying topological addresses.
"""
import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

@dataclass
class MobileNode:
    """A mobile Sophon node with position, velocity, and topological address."""
    id: int
    position: np.ndarray  # [x, y] in 2D space
    velocity: np.ndarray  # [vx, vy]
    address: str  # Jones invariant hash
    coherence: float  # Current coherence level
    transmission_range: float = 0.3

    def move(self, dt: float, bounds: Tuple[float, float]):
        """Update position with velocity, bouncing off boundaries."""
        self.position += self.velocity * dt
        # Bounce off walls
        for dim in range(2):
            if self.position[dim] < 0.0:
                self.position[dim] = 0.0
                self.velocity[dim] *= -1.0
            elif self.position[dim] > bounds[1]:
                self.position[dim] = bounds[1]
                self.velocity[dim] *= -1.0

class DynamicSophonNetwork:
    """Simulates a mobile ad-hoc network of Sophon nodes with flocking behavior."""

    def __init__(self, n_nodes: int = 24, space_size: float = 1.0):
        self.space_size = space_size
        self.nodes = self._initialize_nodes(n_nodes)
        self.time = 0.0
        self.history = {'time': [], 'avg_coherence': [], 'avg_path_length': [],
                       'delivery_rate': [], 'topology_changes': []}

    def _initialize_nodes(self, n: int) -> List[MobileNode]:
        """Create nodes with random positions and velocities."""
        nodes = []
        for i in range(n):
            pos = np.random.rand(2) * self.space_size
            vel = (np.random.rand(2) - 0.5) * 0.1
            coh = np.random.uniform(0.7, 1.0)
            # Generate pseudo-Jones address
            import hashlib
            addr = hashlib.sha256(f"node_{i}_{np.random.rand()}".encode()).hexdigest()[:16]
            nodes.append(MobileNode(i, pos, vel, addr, coh))
        return nodes

    def _compute_adjacency(self) -> nx.Graph:
        """Build dynamic graph based on transmission ranges."""
        G = nx.Graph()
        positions = np.array([n.position for n in self.nodes])
        tree = KDTree(positions)

        for i, node in enumerate(self.nodes):
            G.add_node(i, coherence=node.coherence)
            # Find neighbors within transmission range
            neighbors = tree.query_ball_point(node.position, node.transmission_range)
            for j in neighbors:
                if i < j:
                    # Coherence distance between nodes
                    coh_dist = 1.0 - (node.coherence + self.nodes[j].coherence) / 2.0
                    G.add_edge(i, j, coherence_distance=coh_dist, weight=1.0)

        return G

    def _compute_boid_forces(self) -> np.ndarray:
        """Compute flocking forces: separation, alignment, cohesion."""
        positions = np.array([n.position for n in self.nodes])
        velocities = np.array([n.velocity for n in self.nodes])
        n = len(self.nodes)
        forces = np.zeros((n, 2))

        for i in range(n):
            # Find neighbors within visual range
            diffs = positions - positions[i]
            dists = np.linalg.norm(diffs, axis=1)
            neighbors = (dists > 0) & (dists < 0.2)

            if np.sum(neighbors) == 0:
                continue

            # Separation: steer away from close neighbors
            close = (dists > 0) & (dists < 0.05)
            if np.sum(close) > 0:
                separation = np.mean(-diffs[close] / (dists[close, np.newaxis] + 1e-6), axis=0)
                forces[i] += separation * 0.5

            # Alignment: match velocity of neighbors
            alignment = np.mean(velocities[neighbors], axis=0) - velocities[i]
            forces[i] += alignment * 0.3

            # Cohesion: steer towards center of mass of neighbors
            center = np.mean(positions[neighbors], axis=0)
            cohesion = center - positions[i]
            forces[i] += cohesion * 0.1

        return forces

    def step(self, dt: float = 0.01) -> Dict:
        """Advance simulation by one time step."""
        self.time += dt

        # Compute flocking forces and update velocities
        forces = self._compute_boid_forces()
        for i, node in enumerate(self.nodes):
            node.velocity += forces[i] * dt
            # Limit speed
            speed = np.linalg.norm(node.velocity)
            if speed > 0.2:
                node.velocity *= 0.2 / speed
            node.move(dt, (0.0, self.space_size))

        # Build dynamic graph
        G = self._compute_adjacency()

        # Route test packets
        if G.number_of_edges() > 0:
            n_tests = min(10, len(self.nodes))
            delivery_count = 0
            path_lengths = []

            for _ in range(n_tests):
                src, dest = np.random.choice(len(self.nodes), 2, replace=False)
                try:
                    path = nx.shortest_path(G, src, dest,
                                           weight='coherence_distance')
                    path_lengths.append(len(path))
                    # Deliver if path coherence is sufficient
                    total_coh = sum(G[path[i]][path[i+1]]['coherence_distance']
                                   for i in range(len(path)-1))
                    if total_coh < len(path) * 0.25:
                        delivery_count += 1
                except nx.NetworkXNoPath:
                    pass

            avg_path = np.mean(path_lengths) if path_lengths else 0
            delivery_rate = delivery_count / n_tests if n_tests > 0 else 0
        else:
            avg_path = 0
            delivery_rate = 0

        # Record metrics
        avg_coh = np.mean([n.coherence for n in self.nodes])
        self.history['time'].append(self.time)
        self.history['avg_coherence'].append(avg_coh)
        self.history['avg_path_length'].append(avg_path)
        self.history['delivery_rate'].append(delivery_rate)
        self.history['topology_changes'].append(G.number_of_edges())

        return {
            'time': self.time,
            'avg_coherence': avg_coh,
            'avg_path_length': avg_path,
            'delivery_rate': delivery_rate,
            'n_edges': G.number_of_edges(),
        }

    def run_simulation(self, duration: float = 10.0, dt: float = 0.01) -> Dict:
        """Run full simulation and return aggregated metrics."""
        steps = int(duration / dt)
        for _ in range(steps):
            self.step(dt)
        return self.history

if __name__ == '__main__':
    sim = DynamicSophonNetwork(n_nodes=24)
    history = sim.run_simulation(duration=5.0)
    print(f"Simulation complete: {len(history['time'])} steps")
    print(f"Final avg coherence: {history['avg_coherence'][-1]:.3f}")
    print(f"Final delivery rate: {history['delivery_rate'][-1]:.3f}")
