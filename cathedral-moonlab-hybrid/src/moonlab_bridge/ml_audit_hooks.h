#ifndef ML_AUDIT_HOOKS_H
#define ML_AUDIT_HOOKS_H

#include <stdint.h>

float compute_hybrid_audit_score(float s_value, float integrity_score);
void log_hesitant_operation(const char* op, int ctrl, int target, float delay, float jitter);

#endif // ML_AUDIT_HOOKS_H
