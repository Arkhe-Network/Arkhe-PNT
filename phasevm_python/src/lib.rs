use pyo3::prelude::*;
use pyo3::async_;
use pyo3::types::PyList;
use phasevm::{PhaseVM, AsyncPhaseVM, CompilationResult, CacheStats};
use num_complex::Complex64;
use std::time::Duration;

/// Async Python wrapper for thread-safe PhaseVM
#[pyclass]
struct PyAsyncPhaseVM {
    async_vm: AsyncPhaseVM,
}

#[pymethods]
impl PyAsyncPhaseVM {
    #[new]
    #[pyo3(signature = (num_workers = 2))]
    fn new(num_workers: usize) -> PyResult<Self> {
        let async_vm = AsyncPhaseVM::new(num_workers)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(PyAsyncPhaseVM { async_vm })
    }

    /// Submit async compilation request, returns future-like object
    #[pyo3(signature = (gates, timeout_ms = 50.0))]
    fn compile_circuit_async<'p>(
        &'p self,
        py: Python<'p>,
        gates: &PyList,
        timeout_ms: f64,
    ) -> PyResult<&'p PyAny> {
        let gate_vec: Vec<String> = gates
            .iter()
            .map(|item| item.extract::<String>())
            .collect::<Result<_, _>>()
            .map_err(|e| pyo3::exceptions::PyTypeError::new_err(e.to_string()))?;

        let timeout = Duration::from_millis(timeout_ms as u64);
        let receiver = self.async_vm
            .compile_async(gate_vec, timeout)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        // Return async task that Python can await
        async_::future_into_py(py, async move {
            // Receive result from Rust channel
            match receiver.recv() {
                Ok(CompilationResult::Success { jones, cache_hit }) => {
                    Ok((jones.re, jones.im, cache_hit))
                }
                Ok(CompilationResult::Error { message }) => {
                    Err(pyo3::exceptions::PyRuntimeError::new_err(message))
                }
                Ok(CompilationResult::Timeout) => {
                    Err(pyo3::exceptions::PyTimeoutError::new_err("JIT compilation timeout"))
                }
                Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err("Channel closed")),
            }
        })
    }

    /// Get cache statistics
    fn get_cache_stats(&self) -> PyResult<(usize, usize)> {
        let stats = self.async_vm.get_stats()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok((stats.circuit_cache_size, stats.gate_cache_size))
    }

    /// Clear compilation cache
    fn clear_cache(&self) -> PyResult<()> {
        self.async_vm.clear_cache()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    }

    /// Warm up cache with frequently used circuits
    fn warmup_cache(&self, py: Python, circuits: &PyList) -> PyResult<()> {
        let circuit_vecs: Vec<Vec<String>> = circuits
            .iter()
            .map(|sublist| {
                let inner_list: &PyList = sublist.downcast()?;
                inner_list
                    .iter()
                    .map(|item| item.extract::<String>())
                    .collect::<Result<_, _>>()
            })
            .collect::<Result<_, _>>()
            .map_err(|e: PyErr| pyo3::exceptions::PyTypeError::new_err(e.to_string()))?;

        self.async_vm.warmup_cache(circuit_vecs)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }
}

// Update module initialization
#[pymodule]
fn phasevm_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyAsyncPhaseVM>()?; // New async wrapper
    Ok(())
}
