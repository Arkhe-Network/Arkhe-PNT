#ifndef ORBVM_HPP
#define ORBVM_HPP

#include <vector>

extern "C" {
    struct OrbVM;
    OrbVM* orbvm_create();
    void orbvm_execute(OrbVM* vm);
    double orbvm_get_coherence(const OrbVM* vm);
    void orbvm_destroy(OrbVM* vm);
}

class OrbitalVM {
private:
    OrbVM* vm;
public:
    OrbitalVM();
    ~OrbitalVM();
    void execute();
    double get_coherence() const;
    bool authenticate_biometric(const std::vector<double>& input_phases, const std::vector<double>& anchor_phases, double threshold);
    double calculate_liveness(const std::vector<double>& coherence_stream);
    bool check_phase_clone(const std::vector<uint8_t>& fp1, const std::vector<uint8_t>& fp2);
};

#endif // ORBVM_HPP
