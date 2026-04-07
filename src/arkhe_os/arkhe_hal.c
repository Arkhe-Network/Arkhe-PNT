#include "arkhe_hal.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int arkhe_hal_init(arkhe_node_t* node, const char* rf_device_path) {
    fprintf(stderr, "[A-HAL] Initializing in SIMULATION mode.\n");
    node->bram_base = NULL;
    node->tpu_base = NULL;
    node->lambda2 = 0.999;
    node->current_phase.real = 1.0;
    node->current_phase.imag = 0.0;
    node->fd_rf = -1;
    return 0;
}

arkhe_phase_t arkhe_hal_read_phase(arkhe_node_t* node) {
    static double t = 0;
    t += 0.01;
    arkhe_phase_t p = { cos(t), sin(t) };
    return p;
}

double arkhe_hal_read_lambda2(arkhe_node_t* node) {
    return 0.999;
}
