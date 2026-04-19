#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include "mythos_driver.h"

typedef struct {
    uint32_t flags;
    float x, y, z;
} roi_packet_t;

#define FLAG_RED_DOMINANT 0x01
#define FLAG_HIGH_INTENSITY 0x02

#define ANOMALY_BUFFER_SIZE 32
#define NORM_CURIOSITY_THRESHOLD 70.0f
#define NORM_DIVERGENCE_THRESHOLD 80.0f

typedef struct {
    int16_t embedding[MYTHOS_D_MODEL];
    float latent_norm;
    roi_packet_t roi_data;
} anomaly_sample_t;

static anomaly_sample_t anomaly_buffer[ANOMALY_BUFFER_SIZE];
static int anomaly_idx = 0;

void firebase_publish_anomaly_batch(anomaly_sample_t *buffer, int size) {
    // Placeholder for actual Firebase publication logic
    printf("[RHO] Lote de %d anomalias enviado para a Forja (simulado).\n", size);
}

void check_and_store_anomaly(const int16_t *embedding, float norm, const roi_packet_t *pkt) {
    if (norm > NORM_CURIOSITY_THRESHOLD && norm < NORM_DIVERGENCE_THRESHOLD) {
        anomaly_buffer[anomaly_idx].latent_norm = norm;
        memcpy(anomaly_buffer[anomaly_idx].embedding, embedding, MYTHOS_D_MODEL * sizeof(int16_t));
        memcpy(&anomaly_buffer[anomaly_idx].roi_data, pkt, sizeof(roi_packet_t));

        anomaly_idx = (anomaly_idx + 1) % ANOMALY_BUFFER_SIZE;

        if (anomaly_idx == 0) {
            firebase_publish_anomaly_batch(anomaly_buffer, ANOMALY_BUFFER_SIZE);
        }
    }
}

bool should_invoke_mythos(const roi_packet_t *pkt) {
    int score = 0;
    if (pkt->flags & FLAG_RED_DOMINANT) score += 3;
    if (pkt->flags & FLAG_HIGH_INTENSITY) score += 2;
    if (pkt->z < 5.0f) score += 5;
    return (score >= 8);
}

int main() {
    mythos_t mythos;
    if (mythos_init(&mythos, "/dev/uio2") < 0) {
        perror("Failed to init Mythos Core");
        return 1;
    }

    printf("[RHO] Mythos Core inicializado.\n");

    while (1) {
        roi_packet_t pkt = { .flags = FLAG_RED_DOMINANT, .x = 10.0, .y = 0.0, .z = 4.0 };
        int16_t simulated_embedding[MYTHOS_D_MODEL] = {0};

        if (should_invoke_mythos(&pkt)) {
            printf("[RHO] ROI Crítico detectado. Invocando Mythos...\n");
            mythos_start(&mythos, 8);
            if (mythos_wait_done(&mythos, 100) == 0) {
                float norm = mythos_read_norm(&mythos);
                printf("[RHO] Mythos concluiu. Norma latente: %.2f\n", norm);

                check_and_store_anomaly(simulated_embedding, norm, &pkt);

                if (norm > 50.0f) {
                    printf("[RHO] ALERTA: Colisão iminente detectada pelo Mythos!\n");
                }
            } else {
                printf("[RHO] Timeout do Mythos Core.\n");
            }
        }

        sleep(1);
    }

    mythos_close(&mythos);
    return 0;
}
