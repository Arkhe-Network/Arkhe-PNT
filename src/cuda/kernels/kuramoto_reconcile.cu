/*
 * Arkhe Kuramoto Reconcile Kernel
 * Arkhe-Block: 847.813 | Synapse-κ | SOVEREIGN_OMEGA
 *
 * Standalone CUDA C kernel for high-performance phase reconciliation.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

__device__ float adjust_delta_threshold(float dream_alignment, float base_threshold) {
    if (dream_alignment > 0.0f) {
        // Aligned dream: relax threshold (allow more divergence)
        return base_threshold * (1.0f + 0.4f * fminf(dream_alignment, 1.0f));
    } else {
        // Divergent dream: tighten threshold (more sensitive to noise)
        return base_threshold * (1.0f - 0.2f * fmaxf(-dream_alignment, 0.0f));
    }
}

extern "C" __global__ void kuramoto_reconcile(
    float* thetas,
    const float* omegas,
    const float* zk_lambdas,
    float* order_param,
    float* delta_out,
    int* vibra2_trigger,
    const int N,
    const float K,
    const float dt,
    const float dream_alignment,
    const float delta_duration
) {
    extern __shared__ float tile[];
    int tid = threadIdx.x;
    int gid = blockIdx.x * blockDim.x + threadIdx.x;

    float local_coupling = 0.0f;

    if (gid < N) {
        float theta_i = thetas[gid];

        // Tiled O(N) pairwise summation
        for (int tile_start = 0; tile_start < N; tile_start += blockDim.x) {
            int load_idx = tile_start + tid;
            tile[tid] = (load_idx < N) ? thetas[load_idx] : 0.0f;
            __syncthreads();

            int tile_end = min(tile_start + blockDim.x, N);
            for (int j = tile_start; j < tile_end; j++) {
                float diff = tile[j - tile_start] - theta_i;
                local_coupling += sinf(diff);
            }
            __syncthreads();
        }

        // Coupling normalization + dream boost
        float K_eff = 1.0f + 0.2f * fmaxf(dream_alignment, 0.0f);
        local_coupling = (K / (float)N) * local_coupling * K_eff;

        // Euler step
        float omega_i = omegas[gid];
        // Pseudo-random noise (deterministic based on gid)
        float noise = 0.01f * (fmaf((float)gid, 0.1234567f, 1.0f) - 0.5f);
        float new_theta = theta_i + (omega_i + local_coupling + noise) * dt;

        // Wrap phase to [0, 2pi]
        new_theta = fmodf(new_theta + 6.283185f, 6.283185f);
        thetas[gid] = new_theta;

        // Order parameter (atomic reduction)
        atomicAdd(order_param, cosf(new_theta));

        // Delta with ZK-Aggregator
        float lambda_k = fabsf(cosf(new_theta));
        float lambda_zk = zk_lambdas[gid];
        float delta = fabsf(lambda_k - lambda_zk);

        // Dream-aligned threshold
        float base_threshold = (delta_duration > 3.0f) ? 0.05f : 0.03f;
        float adjusted = adjust_delta_threshold(dream_alignment, base_threshold);

        if (delta > adjusted) {
            atomicExch(vibra2_trigger, 1);
        }

        // Mean delta (atomic reduction)
        atomicAdd(delta_out, delta);
    }

    __syncthreads();

    // Normalization at the block/grid level (simplified for atomicAdd)
    if (gid == 0) {
        *order_param /= (float)N;
        *delta_out /= (float)N;
    }
}
