#include "cronos_scheduler.h"
#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#define K_COUPLING 0.15

static cronos_thread_t* thread_ring_root = NULL;
static arkhe_node_t* hw_context = NULL;

void cronos_init(arkhe_node_t* hw_node) {
    hw_context = hw_node;
}

cronos_thread_t* cronos_spawn(void* entry_point, double natural_freq) {
    cronos_thread_t* t = (cronos_thread_t*)malloc(sizeof(cronos_thread_t));
    t->instruction_ptr = entry_point;
    t->natural_freq = natural_freq;
    t->state = THREAD_RESONATING;
    
    if (!thread_ring_root) {
        thread_ring_root = t;
        t->next = t;
        t->prev = t;
    } else {
        cronos_thread_t* tail = thread_ring_root->prev;
        tail->next = t;
        t->prev = tail;
        t->next = thread_ring_root;
        thread_ring_root->prev = t;
    }
    return t;
}

cronos_thread_t* cronos_tick(void) {
    return thread_ring_root;
}
