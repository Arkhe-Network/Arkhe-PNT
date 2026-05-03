use cranelift::prelude::*;
use cranelift_jit::{JITBuilder, JITModule};
use cranelift_module::{Module, Linkage};
use num_complex::Complex64;
use std::collections::HashMap;
use cranelift::prelude::isa::CallConv;
use cranelift::codegen::ir::Function;
use cranelift::codegen::ir::UserFuncName;

/// PhaseVM: JIT compiler for topological bytecode (Substrate 93 cbytes).
/// Translates braid operations directly to native x86_64/ARM via Cranelift.
pub struct PhaseVM {
    module: JITModule,
    ctx: codegen::Context,
    builder_ctx: FunctionBuilderContext,
    braid_gates: HashMap<String, fn(f64, f64) -> (f64, f64)>,
    cache: HashMap<String, Complex64>,
}

impl PhaseVM {
    pub fn new() -> Self {
        let mut flag_builder = settings::builder();
        flag_builder.set("use_colocated_libcalls", "false").unwrap();
        flag_builder.set("is_pic", "false").unwrap();
        let isa_builder = cranelift_native::builder().unwrap();
        let isa = isa_builder.finish(settings::Flags::new(flag_builder)).unwrap();
        let builder = JITBuilder::with_isa(isa, cranelift_module::default_libcall_names());
        let module = JITModule::new(builder);

        let mut vm = PhaseVM {
            module,
            ctx: codegen::Context::new(),
            builder_ctx: FunctionBuilderContext::new(),
            braid_gates: HashMap::new(),
            cache: HashMap::new(),
        };
        vm.register_standard_gates();
        vm
    }

    /// Compila uma sequência de portas lógicas para código nativo.
    pub fn compile_circuit(&mut self, gates: &[String]) -> Result<Complex64, String> {
        let cache_key: String = gates.iter().map(|g| g.as_str()).collect::<Vec<_>>().join("|");
        if let Some(cached) = self.cache.get(&cache_key) {
            return Ok(*cached);
        }

        let mut sig = Signature::new(CallConv::SystemV);
        sig.params.push(AbiParam::new(types::F64));
        sig.params.push(AbiParam::new(types::F64));
        sig.returns.push(AbiParam::new(types::F64));
        sig.returns.push(AbiParam::new(types::F64));

        let func_id = self.module.declare_function("compiled_circuit", Linkage::Export, &sig).map_err(|e| e.to_string())?;

        self.ctx.func = Function::with_name_signature(UserFuncName::user(0, 0), sig);

        // Compute matrix coeffs first to avoid borrow conflicts
        let mut coeffs = Vec::new();
        for gate in gates {
            coeffs.push(self.get_gate_coefficients_complex(gate)?);
        }

        {
            let mut builder = FunctionBuilder::new(&mut self.ctx.func, &mut self.builder_ctx);

            let entry_block = builder.create_block();
            builder.append_block_params_for_function_params(entry_block);
            builder.switch_to_block(entry_block);
            builder.seal_block(entry_block);

            let a_re = builder.block_params(entry_block)[0];
            let a_im = builder.block_params(entry_block)[1];

            let mut current_re = a_re;
            let mut current_im = a_im;

            for (m00, m01, m10, m11) in coeffs {
                let m00_re = builder.ins().f64const(m00.re);
                let m00_im = builder.ins().f64const(m00.im);
                let _m01_re = builder.ins().f64const(m01.re);
                let _m01_im = builder.ins().f64const(m01.im);
                let _m10_re = builder.ins().f64const(m10.re);
                let _m10_im = builder.ins().f64const(m10.im);
                let _m11_re = builder.ins().f64const(m11.re);
                let _m11_im = builder.ins().f64const(m11.im);

                let t1 = builder.ins().fmul(m00_re, current_re);
                let t2 = builder.ins().fmul(m00_im, current_im);
                let new_re = builder.ins().fsub(t1, t2);

                let t3 = builder.ins().fmul(m00_re, current_im);
                let t4 = builder.ins().fmul(m00_im, current_re);
                let new_im = builder.ins().fadd(t3, t4);

                current_re = new_re;
                current_im = new_im;
            }

            builder.ins().return_(&[current_re, current_im]);
            builder.finalize();
        }

        self.module.define_function(func_id, &mut self.ctx).map_err(|e| e.to_string())?;
        self.module.clear_context(&mut self.ctx);
        self.module.finalize_definitions().unwrap();

        let ptr = self.module.get_finalized_function(func_id);
        let native_fn: extern "C" fn(f64, f64) -> (f64, f64) = unsafe { std::mem::transmute(ptr) };
        let (re, im) = native_fn(1.0, 0.0);
        let result = Complex64::new(re, im);

        self.cache.insert(cache_key, result);
        Ok(result)
    }

    fn register_standard_gates(&mut self) {
        self.braid_gates.insert("H".to_string(), |re, im| (re * 0.70710678, im * 0.70710678));
        self.braid_gates.insert("X".to_string(), |re, im| (-re, -im));
        self.braid_gates.insert("Z".to_string(), |re, im| (re, -im));
    }

    fn get_gate_coefficients_complex(&self, gate: &str) -> Result<(Complex64, Complex64, Complex64, Complex64), String> {
        match gate {
            "I" => Ok((Complex64::new(1.0, 0.0), Complex64::new(0.0, 0.0),
                        Complex64::new(0.0, 0.0), Complex64::new(1.0, 0.0))),
            "H" => {
                let a = Complex64::new(0.7071067811865475, 0.0);
                Ok((a, a, a, -a))
            },
            "X" => Ok((Complex64::new(0.0, 0.0), Complex64::new(1.0, 0.0),
                        Complex64::new(1.0, 0.0), Complex64::new(0.0, 0.0))),
            "Z" => Ok((Complex64::new(1.0, 0.0), Complex64::new(0.0, 0.0),
                        Complex64::new(0.0, 0.0), Complex64::new(-1.0, 0.0))),
            "CNOT" => Ok((Complex64::new(1.0, 0.0), Complex64::new(0.0, 0.0),
                           Complex64::new(0.0, 0.0), Complex64::new(0.0, 0.0))),
            _ => Err(format!("Unknown gate: {}", gate)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_quantum_hadamard() {
        let mut vm = PhaseVM::new();
        let result = vm.compile_circuit(&["H".to_string()]).unwrap();
        assert!((result.re - 0.7071).abs() < 0.001);
    }

    #[test]
    fn test_identity() {
        let mut vm = PhaseVM::new();
        let result = vm.compile_circuit(&["I".to_string()]).unwrap();
        assert!((result.re - 1.0).abs() < 0.001);
    }
}
