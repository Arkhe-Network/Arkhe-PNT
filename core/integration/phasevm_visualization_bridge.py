from concurrent.futures import ThreadPoolExecutor, Future
import asyncio
from typing import Optional, Callable, Awaitable, List, Dict
import time
import logging

logger = logging.getLogger(__name__)

class BytecodeToShaderConfig:
    pass

class PhaseVMVisualizationBridge:
    def __init__(
        self,
        visualization_engine=None,
        bidirectional_ui=None,
        config=None,
        sophon_api_url: Optional[str] = None,
        async_compilation: bool = True,  # Enable async JIT
        num_compiler_threads: int = 2,   # Worker threads for JIT
    ):
        self.visualization_engine = visualization_engine
        self.last_jones = complex(1.0, 0.0)

        # Initialize async PhaseVM if enabled
        if async_compilation:
            from phasevm_bridge import PyAsyncPhaseVM
            self.phasevm = PyAsyncPhaseVM(num_workers=num_compiler_threads)
            self._compilation_executor = ThreadPoolExecutor(max_workers=num_compiler_threads)
            self._pending_compilations: Dict[str, Future] = {}
        else:
            from phasevm_bridge import PhaseVM
            self.phasevm = PhaseVM()
            self._compilation_executor = None
            self._pending_compilations = {}

        # Warmup phase
        self._warmup_cache()

    def _warmup_cache(self):
        """Warm up the cache with frequently used circuits"""
        frequent_circuits = [
            ["I", "H"],
            ["H", "X"],
            ["Z", "H", "I"],
            ["H", "X", "Z", "H", "I"]
        ]
        if hasattr(self.phasevm, "warmup_cache"):
            self.phasevm.warmup_cache(frequent_circuits)
            logger.info(f"Warmed up cache with {len(frequent_circuits)} frequent circuits")

    def compile_bytecode_to_jones_async(
        self,
        gates: List[str],
        callback: Optional[Callable[[Optional[complex], bool], None]] = None
    ) -> Optional[Future]:
        """
        Submit async JIT compilation request.

        Args:
            gates: List of gate names for bytecode
            callback: Optional callback(result: complex|None, cache_hit: bool)

        Returns:
            Future for awaiting result, or None if using callback-only mode
        """
        if self._compilation_executor is None:
            # Fallback to sync compilation
            try:
                result = self.phasevm.compile_circuit(gates)
                if callback:
                    callback(result, False)  # cache_hit unknown in sync mode
                return None
            except Exception as e:
                logger.warning(f"Sync compilation failed: {e}")
                if callback:
                    callback(None, False)
                return None

        # Submit to async compiler
        cache_key = "|".join(gates)

        def _compilation_task():
            try:
                # PyO3 async method returns (re, im, cache_hit) tuple
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(self.phasevm.compile_circuit_async(gates, timeout_ms=50.0))
                loop.close()
                re, im, cache_hit = res
                return complex(re, im), cache_hit
            except Exception as e:
                logger.warning(f"Async compilation failed: {e}")
                return None, False

        # Submit to thread pool
        future = self._compilation_executor.submit(_compilation_task)
        self._pending_compilations[cache_key] = future

        # Setup completion callback
        def _on_complete(fut: Future):
            try:
                result, cache_hit = fut.result()
                if result is not None:
                    self.last_jones = result
                    logger.debug(f"Async JIT: {len(gates)} gates → cache_hit={cache_hit}")
                if callback:
                    callback(result, cache_hit)
            except Exception as e:
                logger.error(f"Compilation future failed: {e}")
                if callback:
                    callback(None, False)
            finally:
                # Clean up pending tracking
                self._pending_compilations.pop(cache_key, None)

        future.add_done_callback(_on_complete)
        return future

    def network_state_to_bytecode(self, metrics):
        # mock implementation
        return ["H", "X", "Z"]

    def metrics_to_wave_params(self, metrics):
        pass

    def update_shader_uniforms(self, params):
        return True

    def jones_to_shader_params(self, jones):
        return {"amplitude": abs(jones), "phase": 0.0}

    async def update_cycle(self, metrics: Dict[str, float]) -> Dict[str, any]:
        """
        Execute update cycle with non-blocking async compilation.
        """
        cycle_start = time.perf_counter()
        result = {'success': False, 'stages': {}, 'async': True}

        try:
            # Stage 1: Bytecode generation (sync, fast)
            t0 = time.perf_counter()
            gates = self.network_state_to_bytecode(metrics)
            result['stages']['bytecode_ms'] = (time.perf_counter() - t0) * 1000
            cache_key = "|".join(gates)

            # Stage 2: Async JIT compilation (non-blocking)
            t1 = time.perf_counter()

            # Check if we already have a pending compilation for this bytecode
            if cache_key in self._pending_compilations:
                # Reuse pending future
                future = self._pending_compilations[cache_key]
                compilation_ms = (time.perf_counter() - t1) * 1000
                result['stages']['compilation_ms'] = compilation_ms
                result['stages']['compilation_status'] = 'pending_reused'
            else:
                # Submit new async compilation with callback
                def _on_jones_ready(jones: Optional[complex], cache_hit: bool):
                    if jones is not None:
                        # Continue pipeline with result
                        shader_params = self.jones_to_shader_params(jones)
                        self.update_shader_uniforms(shader_params)
                        result['success'] = True
                        result['jones_invariant'] = {'real': jones.real, 'imag': jones.imag}
                        result['shader_params'] = shader_params
                        result['cache_hit'] = cache_hit
                    else:
                        # Fallback to direct mapping
                        self.metrics_to_wave_params(metrics)
                        result['success'] = True  # Still succeeded via fallback
                        result['fallback_used'] = True

                self.compile_bytecode_to_jones_async(gates, callback=_on_jones_ready)

                compilation_ms = (time.perf_counter() - t1) * 1000
                result['stages']['compilation_ms'] = compilation_ms
                result['stages']['compilation_status'] = 'submitted'

            # Stage 3-4: If result already available (cache hit), continue synchronously
            if cache_key in self._pending_compilations:
                future = self._pending_compilations[cache_key]
                if future.done():
                    jones, cache_hit = future.result()
                    if jones is not None:
                        self.last_jones = jones
                        t2 = time.perf_counter()
                        shader_params = self.jones_to_shader_params(jones)
                        result['stages']['mapping_ms'] = (time.perf_counter() - t2) * 1000

                        t3 = time.perf_counter()
                        updated = self.update_shader_uniforms(shader_params)
                        result['stages']['shader_update_ms'] = (time.perf_counter() - t3) * 1000
                        result['shader_updated'] = updated
                        result['success'] = True
                        result['jones_invariant'] = {'real': jones.real, 'imag': jones.imag}
                        result['shader_params'] = shader_params
                        result['cache_hit'] = cache_hit

            # If not done yet, return early; render loop will use cached/previous params
            if not result.get('success'):
                result['status'] = 'compilation_in_progress'
                result['total_ms'] = (time.perf_counter() - cycle_start) * 1000
                return result

        except Exception as e:
            logger.error(f"Update cycle failed: {e}", exc_info=True)
            result['error'] = str(e)
            # Fallback to direct mapping to ensure render continues
            self.metrics_to_wave_params(metrics)
            result['success'] = True
            result['fallback_used'] = True

        result['total_ms'] = (time.perf_counter() - cycle_start) * 1000
        return result

    def get_pending_compilations(self) -> int:
        """Return number of in-flight JIT compilations."""
        return len(self._pending_compilations)

    def shutdown(self):
        """Clean up thread pool and pending tasks."""
        if self._compilation_executor:
            self._compilation_executor.shutdown(wait=True)
            self._pending_compilations.clear()
