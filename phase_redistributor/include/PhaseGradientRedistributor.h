#pragma once

#include <torch/torch.h>
#include <vector>

class PhaseGradientRedistributor : public torch::nn::Module {
public:
    // Construtor: n_nodes = número total de sensores + veículos móveis
    // distance_mask: matriz [n_nodes x n_nodes] com 1 onde o enlace é fisicamente possível (alcance < 100m), 0 caso contrário
    // initial_k: valor inicial para todos os K_ij (padrão 1.5)
    PhaseGradientRedistributor(int64_t n_nodes,
                               const torch::Tensor& distance_mask,
                               float initial_k = 1.5f);

    // Forward: calcula coerência R, termo de acoplamento e perda (para treinamento)
    // phases: tensor [n_nodes] com as fases atuais (radianos)
    // alive_mask: tensor [n_nodes] com 1 para nós ativos, 0 para falhos (EMP)
    // dt: passo de integração (opcional, usado apenas para depuração)
    std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> forward(
        const torch::Tensor& phases,
        const torch::Tensor& alive_mask,
        float dt = 0.1f);

    // Método para otimizar K durante um ataque EMP (executa vários passos de gradiente descendente)
    // phases: fases atuais (serão atualizadas in‑place)
    // alive_mask: máscara de nós vivos
    // steps: número de iterações de otimização
    // lr: taxa de aprendizado
    void redistribute(torch::Tensor& phases,
                      const torch::Tensor& alive_mask,
                      int64_t steps = 50,
                      float lr = 0.05f);

    // Acessar a matriz K (parâmetro treinável)
    torch::Tensor get_K() const { return K_; }

private:
    torch::nn::Parameter K_;            // matriz de acoplamento [n_nodes x n_nodes]
    torch::Tensor dist_mask_;           // máscara de distância (buffer não treinável)
    int64_t n_nodes_;
    float sparse_weight_;               // regularização L1
};
