#!/usr/bin/env python3
"""
routing_benchmark.py — Comparative analysis of routing algorithms for Sophon Network.
Benchmarks: Coherence Geodesic, Dijkstra (hop-count), A* (heuristic),
            Adaptive Threshold, and Random Walk (baseline).
"""
import numpy as np
import networkx as nx
import time
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass, field
import json

@dataclass
class RoutingResult:
    algorithm: str
    path: List[int]
    hops: int
    total_coherence_distance: float
    computation_time_ms: float
    delivery_likelihood: float  # Probabilidade estimada de entrega bem-sucedida

class SophonRoutingBenchmark:
    """Benchmark framework for topological routing algorithms."""

    def __init__(self, n_nodes: int = 48, coherence_mean: float = 0.85):
        self.G = self._generate_coherence_graph(n_nodes, coherence_mean)
        self.algorithms = {
            'Coherence Geodesic': self._route_coherence_dijkstra,
            'Dijkstra (hop-count)': self._route_hop_count,
            'A* (heuristic)': self._route_astar,
            'Adaptive Threshold': self._route_adaptive,
            'Random Walk': self._route_random_walk,
        }
        self.results = {}

    def _generate_coherence_graph(self, n: int, mean_coh: float) -> nx.Graph:
        """Generate random graph with coherence-weighted edges."""
        G = nx.random_geometric_graph(n, 0.3)
        for u, v in G.edges():
            # Coherence distance: lower is better for routing
            coh = np.clip(np.random.normal(mean_coh, 0.1), 0.4, 1.0)
            G[u][v]['coherence_distance'] = 1.0 - coh
            G[u][v]['weight'] = 1.0  # For traditional routing
        return G

    def _route_coherence_dijkstra(self, src: int, dest: int) -> RoutingResult:
        start = time.perf_counter()
        path = nx.shortest_path(self.G, src, dest,
                               weight=lambda u, v, d: d.get('coherence_distance', 1.0))
        elapsed = (time.perf_counter() - start) * 1000

        total_coh = sum(self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                       for i in range(len(path)-1))
        return RoutingResult('Coherence Geodesic', path, len(path), total_coh, elapsed,
                            self._estimate_delivery(path))

    def _route_hop_count(self, src: int, dest: int) -> RoutingResult:
        start = time.perf_counter()
        path = nx.shortest_path(self.G, src, dest)
        elapsed = (time.perf_counter() - start) * 1000

        total_coh = sum(self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                       for i in range(len(path)-1))
        return RoutingResult('Dijkstra (hop-count)', path, len(path), total_coh, elapsed,
                            self._estimate_delivery(path))

    def _route_astar(self, src: int, dest: int) -> RoutingResult:
        start = time.perf_counter()
        def heuristic(u, v):
            return abs(hash(u) - hash(v)) % 5 / 10.0
        path = nx.astar_path(self.G, src, dest, heuristic=heuristic,
                            weight='coherence_distance')
        elapsed = (time.perf_counter() - start) * 1000

        total_coh = sum(self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                       for i in range(len(path)-1))
        return RoutingResult('A* (heuristic)', path, len(path), total_coh, elapsed,
                            self._estimate_delivery(path))

    def _route_adaptive(self, src: int, dest: int) -> RoutingResult:
        start = time.perf_counter()
        # Adaptativo: usa coerência se média > 0.75, senão hop-count
        avg_coh = np.mean([d.get('coherence_distance', 1.0)
                          for _, _, d in self.G.edges(data=True)])
        if avg_coh < 0.25:  # coherence distance baixa = coerência alta
            path = nx.shortest_path(self.G, src, dest,
                                   weight='coherence_distance')
            algo = 'Adaptive (coherence)'
        else:
            path = nx.shortest_path(self.G, src, dest)
            algo = 'Adaptive (hop-count)'
        elapsed = (time.perf_counter() - start) * 1000

        total_coh = sum(self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                       for i in range(len(path)-1))
        return RoutingResult(algo, path, len(path), total_coh, elapsed,
                            self._estimate_delivery(path))

    def _route_random_walk(self, src: int, dest: int) -> RoutingResult:
        start = time.perf_counter()
        # Random walk como baseline inferior
        path = [src]
        current = src
        visited = {src}
        max_steps = 200
        while current != dest and len(path) < max_steps:
            neighbors = list(self.G.neighbors(current))
            if not neighbors:
                break
            next_node = np.random.choice(neighbors)
            path.append(next_node)
            current = next_node
        elapsed = (time.perf_counter() - start) * 1000

        total_coh = sum(self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                       for i in range(len(path)-1)) if len(path) > 1 else 999
        return RoutingResult('Random Walk', path, len(path), total_coh, elapsed, 0.0)

    def _estimate_delivery(self, path: List[int]) -> float:
        """Estima probabilidade de entrega baseada na coerência do caminho."""
        if len(path) < 2:
            return 1.0
        coh_dists = [self.G[path[i]][path[i+1]].get('coherence_distance', 1.0)
                    for i in range(len(path)-1)]
        avg_coh_dist = np.mean(coh_dists)
        # Modelo simplificado: entrega ∝ 1/(1 + distância de coerência)
        return 1.0 / (1.0 + avg_coh_dist * 3.0)

    def run_benchmark(self, n_pairs: int = 100) -> Dict:
        """Execute benchmark on random source-destination pairs."""
        nodes = list(self.G.nodes())
        all_results = {name: [] for name in self.algorithms}

        for _ in range(n_pairs):
            src, dest = np.random.choice(nodes, 2, replace=False)
            for name, algo_fn in self.algorithms.items():
                try:
                    result = algo_fn(src, dest)
                    all_results[name].append(result)
                except nx.NetworkXNoPath:
                    pass

        # Aggregate results
        self.results = {
            name: {
                'avg_path_length': np.mean([r.hops for r in results]),
                'avg_coherence_distance': np.mean([r.total_coherence_distance for r in results]),
                'avg_computation_ms': np.mean([r.computation_time_ms for r in results]),
                'avg_delivery_likelihood': np.mean([r.delivery_likelihood for r in results]),
                'success_rate': len(results) / n_pairs,
            }
            for name, results in all_results.items()
        }
        return self.results

if __name__ == '__main__':
    benchmark = SophonRoutingBenchmark(n_nodes=48)
    results = benchmark.run_benchmark(100)
    print(json.dumps(results, indent=2))
