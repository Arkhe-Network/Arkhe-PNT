#include "orbvm.hpp"
#include "coherence_biometrics.h"

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

bool OrbitalVM::authenticate_biometric(const std::vector<double>& input_phases, const std::vector<double>& anchor_phases, double threshold) {
    using namespace arkhe::biometrics;
    CoherenceBiometrics::BiometricProfile profile = { anchor_phases, threshold };
    return CoherenceBiometrics::authenticate(input_phases, profile);
}

double OrbitalVM::calculate_liveness(const std::vector<double>& coherence_stream) {
    using namespace arkhe::biometrics;
    return CoherenceBiometrics::calculate_liveness_evidence(coherence_stream);
}

bool OrbitalVM::check_phase_clone(const std::vector<uint8_t>& fp1_raw, const std::vector<uint8_t>& fp2_raw) {
    using namespace arkhe::biometrics;
    if (fp1_raw.size() != FINGERPRINT_CHANNELS || fp2_raw.size() != FINGERPRINT_CHANNELS) {
        return false;
    }

    PhaseFingerprint fp1, fp2;
    std::copy(fp1_raw.begin(), fp1_raw.end(), fp1.channels.begin());
    std::copy(fp2_raw.begin(), fp2_raw.end(), fp2.channels.begin());

    return detectPhaseClone(fp1, fp2).is_clone;
}
