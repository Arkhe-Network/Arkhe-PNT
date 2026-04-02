use orbvm::OrbVM;

fn main() {
    println!("[OrbVM] Initializing Orbital Virtual Machine...");
    let mut vm = OrbVM::new();
    vm.execute_cycle();
    println!("[OrbVM] Cycle executed. Coherence: {}", vm.coherence);
}
