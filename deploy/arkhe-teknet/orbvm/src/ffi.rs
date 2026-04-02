use crate::vm::OrbVM;

#[no_mangle]
pub extern "C" fn orbvm_create() -> *mut OrbVM {
    Box::into_raw(Box::new(OrbVM::new()))
}

#[no_mangle]
pub extern "C" fn orbvm_execute(vm: *mut OrbVM) {
    if let Some(vm) = unsafe { vm.as_mut() } {
        vm.execute_cycle();
    }
}

#[no_mangle]
pub extern "C" fn orbvm_get_coherence(vm: *const OrbVM) -> f64 {
    if let Some(vm) = unsafe { vm.as_ref() } {
        vm.coherence
    } else {
        0.0
    }
}

#[no_mangle]
pub extern "C" fn orbvm_destroy(vm: *mut OrbVM) {
    if !vm.is_null() {
        unsafe {
            let _ = Box::from_raw(vm);
        }
    }
}
