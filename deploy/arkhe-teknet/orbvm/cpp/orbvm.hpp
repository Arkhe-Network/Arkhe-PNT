#ifndef ORBVM_HPP
#define ORBVM_HPP

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
};

#endif // ORBVM_HPP
