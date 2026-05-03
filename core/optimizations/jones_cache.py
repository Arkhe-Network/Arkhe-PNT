#!/usr/bin/env python3
"""
Jones Invariant Optimizations — Substrate 105 Performance Enhancements
Implements LRU caching and parallel computation for Jones polynomial evaluation.
"""
import numpy as np
from functools import lru_cache
from typing import Tuple, List, Optional
import hashlib
from numba import njit, prange
import threading

# ============================================================
# LRU CACHE FOR JONES INVARIANTS
# ============================================================

class JonesInvariantCache:
    """Thread-safe LRU cache for Jones polynomial computations."""

    def __init__(self, maxsize: int = 4096):
        self.maxsize = maxsize
        self.cache = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _key_from_braid(self, braid_word: Tuple[str, ...], q: complex) -> str:
        """Generate deterministic cache key from braid word and q-parameter."""
        data = '|'.join(braid_word) + f'|{q.real}:{q.imag}'
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get(self, braid_word: Tuple[str, ...], q: complex) -> Optional[complex]:
        """Retrieve cached Jones invariant if available."""
        key = self._key_from_braid(braid_word, q)
        with self.lock:
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, braid_word: Tuple[str, ...], q: complex, value: complex):
        """Store Jones invariant in cache with LRU eviction."""
        key = self._key_from_braid(braid_word, q)
        with self.lock:
            if len(self.cache) >= self.maxsize:
                # Evict oldest 10% when full
                keys_to_remove = list(self.cache.keys())[:max(1, len(self.cache)//10)]
                for k in keys_to_remove:
                    del self.cache[k]
            self.cache[key] = value

    def stats(self) -> dict:
        """Return cache performance statistics."""
        total = self.hits + self.misses
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0.0,
            'size': len(self.cache),
            'maxsize': self.maxsize
        }

# Global cache instance for Jones invariants
_jones_cache = JonesInvariantCache(maxsize=4096)

# ============================================================
# PARALLEL JONES COMPUTATION VIA NUMBA
# ============================================================

@njit(parallel=True, cache=True)
def compute_jones_parallel(matrices: np.ndarray, q: complex) -> np.ndarray:
    """
    Compute Jones polynomial for multiple braid matrices in parallel.

    Args:
        matrices: Array of shape (N, 2, 2) containing braid representation matrices
        q: Jones polynomial parameter (typically e^{iπ/5} for Fibonacci anyons)

    Returns:
        Array of N Jones invariant values (normalized trace)
    """
    N = matrices.shape[0]
    results = np.zeros(N, dtype=np.complex128)
    PHI = (1.0 + np.sqrt(5.0)) / 2.0
    normalization = PHI + 1.0/PHI

    for i in prange(N):  # Parallel loop over matrices
        trace = matrices[i, 0, 0] + matrices[i, 1, 1]
        results[i] = trace / normalization

    return results

def cached_jones_computation(braid_word: List[str], q: complex,
                            braid_matrices: dict) -> complex:
    """
    Compute Jones invariant with caching and fallback to parallel computation.

    Args:
        braid_word: List of braid generators (e.g., ['σ₁', 'σ₂⁻¹', 'σ₁'])
        q: Jones parameter
        braid_matrices: Dict mapping braid symbols to 2×2 matrices

    Returns:
        Jones invariant (normalized trace)
    """
    # Convert braid word to tuple for hashing
    braid_tuple = tuple(braid_word)

    # Check cache first
    cached = _jones_cache.get(braid_tuple, q)
    if cached is not None:
        return cached

    # Compute matrix product for braid word
    M = np.eye(2, dtype=np.complex128)
    for symbol in braid_word:
        if symbol in braid_matrices:
            M = M @ braid_matrices[symbol]

    # Compute Jones invariant (normalized trace)
    PHI = (1.0 + np.sqrt(5.0)) / 2.0
    normalization = PHI + 1.0/PHI
    jones = (M[0, 0] + M[1, 1]) / normalization

    # Cache result
    _jones_cache.set(braid_tuple, q, jones)

    return jones
