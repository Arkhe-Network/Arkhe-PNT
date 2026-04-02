#include "orbvm.hpp"

OrbitalVM::OrbitalVM() {
    vm = orbvm_create();
}

OrbitalVM::~OrbitalVM() {
    if (vm) {
        orbvm_destroy(vm);
    }
}

void OrbitalVM::execute() {
    if (vm) {
        orbvm_execute(vm);
    }
}

double OrbitalVM::get_coherence() const {
    if (vm) {
        return orbvm_get_coherence(vm);
    }
    return 0.0;
}
