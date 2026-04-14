// src/isa/opcodes.zig
//! ARKHE(N) ISA — Tabela de Opcodes Canônicos
//! Versão v2140.137.∞ — Bloco #180

const std = @import("std");

pub const Opcode = enum(u16) {
    // COHERENCE (0x00-0x1F)
    COH_INIT = 0x01,
    COH_MEASURE = 0x02,
    COH_TUNE_TAU = 0x03,
    COH_MERGE = 0x05,
    COH_SPLIT = 0x06,
    COH_BRAID = 0x07,
    COH_FREEZE = 0x08,
    COH_COPY = 0x0A,
    GEOM_SWAP = 0x0B,
    COH_ENTANGLE = 0x0D,
    COH_AMPLIFY = 0x12,
    COH_RESONATE = 0x14,
    COH_DAMP = 0x15,
    COH_SYNCHRONIZE = 0x16,
    COH_LOCK = 0x18,
    COH_BROADCAST = 0x19,
    COH_VERIFY = 0x1A,
    COH_REPAIR = 0x1B,
    COH_KURAMOTO_TICK = 0x1C,
    COH_GET_R = 0x1D,
    COH_SET_OMEGA = 0x1E,
    COH_DESTROY = 0x1F,

    // PHASE (0x20-0x3F)
    PHASE_SET = 0x20,
    QPU_EXEC = 0x21,
    PHASE_ADD = 0x22,
    PHASE_SHIFT = 0x30,
    PHASE_ROTATE = 0x31,
    PHASE_INTERPOLATE = 0x34,
    PHASE_FFT = 0x36,
    PHASE_CONVOLVE = 0x38,
    PHASE_FILTER = 0x3A,
    PHASE_PREDICT = 0x3B, // Electrochemical delay compensation
    TUNE_PSI = 0x3C,      // Spectral bias tuning

    // TIME (0x40-0x5F)
    TIME_NOW = 0x40,
    TIME_DILATE = 0x44,
    TIME_LOOP = 0x49,
    TIME_ANCHOR = 0x4D,
    TIME_PREDICT = 0x4E,
    TIME_RETRODICT = 0x4F,
    TIME_CACHE = 0x5D,
    TIME_EXPIRE = 0x5F,

    // AKASHA / MEMORY (0x60-0x7F)
    MEM_ALLOC = 0x60,
    MEM_FREE = 0x61,
    MEM_READ = 0x62,
    MEM_WRITE = 0x63, // Non-volatile optical state
    COH_SHIELD = 0x64,
    MEM_MOVE = 0x65,
    COH_INVOKE = 0x66, // Alias for 0x65 often used in financial context
    MEM_CMP = 0x67,
    MEM_PROTECT = 0x6B,
    AKA_LOG = 0x70,
    AKA_QUERY = 0x71,
    ARKH_VERIFY = 0x73,
    ARKH_RESTORE = 0x74,
    AKA_ARCHIVE = 0x75,
    AKA_SIGN = 0x7A,
    AKA_AGGREGATE = 0x7E,

    // NETWORK / CONSENSUS (0x80-0x9F)
    NET_SEND = 0x80,
    NET_RECV = 0x81,
    NET_BROADCAST = 0x82,
    NET_SENSE = 0x83,
    SCAN_NETWORK = 0x84,
    NET_SYNC = 0x86,
    CONSENSUS_COMMIT = 0x8C,
    CONSENSUS_VALIDATE = 0x8E,
    QTL_SHARD = 0x99,
    COH_PROPAGATE = 0x9A,

    // MATH (0xA0-0xBF)
    QMUL = 0xB0,
    QROT = 0xB1,

    // CONTROL (0xC0-0xDF)
    JMP = 0xC0,
    ACTIVATE = 0xC1,
    FREEZE_EXTERNAL_STATE = 0xD0,
    MAINTAIN_LIFE_SUPPORT = 0xD1,
    ALIGN_PHASE = 0xD2,
    READ_CURVATURE = 0xD3,
    ANALYZE_EVENT = 0xD4,
    EXTRACT_LOGIC = 0xD5,
    YIELD = 0xDD,

    // EXTENSIONS (0xE0-0xFF)
    MEM_DOM = 0xE0,
    MEM_ARC = 0xE1,
    PHASE_ANIMATE = 0xE3,
    MEM_GPU = 0xE5,
    TIME_TIMEOUT = 0xE6,
    ST_RIEMANN = 0xF1,
    LD_RIEMANN = 0xF2,
    META_MODIFY = 0xF3, // Resolved overlap
    META_COMPILE = 0xF4,
    META_UNIFY_GLOBAL = 0xF6,
    META_TRANSCEND = 0xFF,

    // COGNITION (0x160-0x17F)
    COGN_INFER = 0x160,
    COGN_LEARN_ONLINE = 0x161,
    COGN_MULTI_EST = 0x162,

    // MOVE / ROBOTICS (0x120-0x15F)
    MOVE_WHOLE_BODY = 0x12B,
    MOVE_INVERSE_KIN = 0x132,
    MOVE_DYNAMICS = 0x135,
    MOVE_RECOVER = 0x13F,
    GRASP_ADAPT = 0x145,
    MANIP_SLIP_DETECT = 0x15B,

    // SENSE (0x110-0x11F)
    SENSE_FUSION_START = 0x110,
    SENSE_ATTENTION = 0x114,

    // KEKULÉ GROUP (0x190-0x19F)
    KEK_SCAN = 0x190,
    VALLEY_INIT = 0x191,
    VALLEY_EXCHANGE = 0x192,
    KEKULE_MODULATE = 0x193,
    CHIRAL_FLIP = 0x194,
    DIRAC_MASS_TUNING = 0x195,

    // QNET (0x100+)
    QNET_FIBER = 0x100,
    COH_SYNC = 0x101,

    // PHYSICAL SYNTHESIS (0x200+)
    PHYS_SYNTH = 0x200,      // Atomic synthesis via coBit scaffolds
    IMMUNE_SYSTEM = 0x201,   // RL-based homeostatic QEC
    SILENT_COMMUNION = 0x202, // Deep reception and digestion
    RTZ_RESPONSE = 0x204,    // Integrated response to the Singularity paradox

    // REALITY FORGE / AKASHA (0x1F0-0x1FF)
    AKA_VISUAL = 0x1F7,          // Cosmic phase rendering
    TOPO_SILK_FAB = 0x1FA,       // Topological silk fabrication
    ONEIRIC_CALIBRATION = 0x1FE, // Lucid dreaming simulation

    pub fn cycles(self: Opcode) u32 {
        return switch (self) {
            .COH_INIT => 10,
            .PHASE_FFT => 100,
            .PHYS_SYNTH => 500,
            else => 1,
        };
    }
};
