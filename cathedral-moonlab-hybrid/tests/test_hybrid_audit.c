#include "../src/moonlab_bridge/ml_audit_hooks.h"
#include <stdio.h>
#include <assert.h>
#include <math.h>

int main() {
    printf("[TEST] Testing Hybrid Audit Score calculation...\n");
    float s_value = 7.9f;
    float integrity = 0.95f;
    float score = compute_hybrid_audit_score(s_value, integrity);
    printf("      Score: %.4f\n", score);
    assert(score > 0.8f);
    assert(score <= 1.0f);
    printf("[TEST] Hybrid Audit test passed.\n");
    return 0;
}
