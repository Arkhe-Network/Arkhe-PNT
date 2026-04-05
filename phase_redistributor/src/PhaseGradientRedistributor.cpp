#include "PhaseGradientRedistributor.h"
#include <torch/script.h> // para otimizadores

PhaseGradientRedistributor::PhaseGradientRedistributor(int64_t n_nodes,
                                                       const torch::Tensor& distance_mask,
                                                       float initial_k)
    : n_nodes_(n_nodes),
      dist_mask_(distance_mask),
      sparse_weight_(0.01f) {
    // Inicializa K como parâmetro treinável
    K_ = register_parameter("K", torch::full({n_nodes, n_nodes}, initial_k, torch::requires_grad()));
    // Garante que a máscara de distância esteja no mesmo dispositivo que o modelo
    dist_mask_ = dist_mask_.to(K_.device());
}

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor>
PhaseGradientRedistributor::forward(const torch::Tensor& phases,
                                    const torch::Tensor& alive_mask,
                                    float dt) {
    // 1. Expandir fases para calcular diferenças
    auto phi_i = phases.unsqueeze(1);        // [n, 1]
    auto phi_j = phases.unsqueeze(0);        // [1, n]
    auto phase_diff = phi_j - phi_i;         // [n, n]

    // 2. Máscara efetiva: nós vivos + distância
    auto effective_mask = alive_mask.unsqueeze(1) * alive_mask.unsqueeze(0) * dist_mask_;

    // 3. Termo de acoplamento: sum_j K_ij * sin(θ_j - θ_i) * mask
    auto sin_diff = torch::sin(phase_diff);
    auto coupling = torch::sum(K_ * effective_mask * sin_diff, /*dim=*/1); // [n]

    // 4. Coerência global R
    auto complex_phases = torch::exp(torch::complex(phases, torch::zeros_like(phases)));
    auto R = torch::abs(torch::mean(complex_phases));

    // 5. Perda: (1 - R) + L2 + L1
    auto loss = (1.0 - R) + 0.01 * torch::norm(K_) + sparse_weight_ * torch::norm(K_, 1);

    // 6. Derivada (dθ/dt) – aqui assumimos frequência natural zero
    auto dtheta = coupling;   // pode adicionar omega depois

    return {R, dtheta, loss};
}

void PhaseGradientRedistributor::redistribute(torch::Tensor& phases,
                                              const torch::Tensor& alive_mask,
                                              int64_t steps,
                                              float lr) {
    // Criar otimizador Adam sobre o parâmetro K_
    torch::optim::Adam optimizer({K_}, torch::optim::AdamOptions(lr));

    for (int64_t step = 0; step < steps; ++step) {
        optimizer.zero_grad();
        auto [R, dtheta, loss] = forward(phases, alive_mask);
        loss.backward();
        optimizer.step();

        // Clamping para manter K_ dentro de limites físicos
        {
            torch::NoGradGuard no_grad;
            K_.data().clamp_(0.1, 5.0);
        }

        // Atualiza as fases com Euler (dt = 0.1)
        phases = phases + dtheta * 0.1;
        phases = phases % (2 * M_PI);  // wrap to [0, 2π)

        if (step % 10 == 0) {
            std::cout << "Step " << step << " | R = " << R.item<float>()
                      << " | K_mean = " << K_.mean().item<float>() << std::endl;
        }
    }
}
