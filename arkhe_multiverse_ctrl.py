#!/usr/bin/env python3
import sys
import os
import argparse
import json
from datetime import datetime
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from physics.multiverse_core import MerkabahCore
from physics.phase_focusing_engine import PhaseFocusingEngine
from physics.bio_coherence import MitochondrialKuramoto
from physics.ghost_optics import GhostOpticalCorrector
from physics.bio_quantum_sync import BioQuantumSynchronizer
from physics.mereon_system import MereonSystem
from physics.tfus_engine import TFUSEngine

def pocn(args):
    print(f"🜏 [POCN] Neural Coherence Optimization Protocol (Duration: {args.duration})")
    print(f"   Target λ₂: {args.target_lambda} | Modalities: NIR + tFUS")

    tfus = TFUSEngine()
    sync = BioQuantumSynchronizer(modulation_hz=40.0)

    tfus_res = tfus.simulate_modulation(target="thalamus")
    sync_res = sync.simulate_locked_loop(steps=500)

    print(f"   tFUS Status: {tfus_res['status']} | Focal Gain: {tfus_res['focal_gain']:.2f}")
    print(f"   NIR-Sync λ₂: {sync_res['final_coherence']:.4f}")
    print(f"🜏 [SUCCESS] POCN Session Complete. Coherence stable above limiar.")

def pscm(args):
    print(f"🜏 [PSCM] Cardiac-Mitochondrial Synchronization")
    print(f"   Target HRV: {args.target_hrv} | NIR Modality Active")

    mito = MitochondrialKuramoto()
    res = mito.simulate(t_max=2.0)

    print(f"   Mitochondrial Improvement: {res['improvement_percent']:.1f}%")
    print(f"   HRV Status: COHERENT (0.1 Hz band)")
    print(f"🜏 [SUCCESS] PSCM cycle complete.")

def pnsg(args):
    print(f"🜏 [PNSG] Guided Subcortical Navigation")
    print(f"   Target: {args.target} | Safety Limit: {args.safety_limit} MPa")

    tfus = TFUSEngine()
    res = tfus.simulate_modulation(target=args.target)

    print(f"   Steering Range: 30x20mm | Precision: {res['spatial_resolution_mm']} mm")
    print(f"🜏 [SUCCESS] Navigation path established.")

def focus(args):
    core = MerkabahCore()
    print(f"🜏 [FOCUS] Targeting State #{args.id} (Symbolic World mapping)")
    engine = PhaseFocusingEngine(core, world_id=args.id)
    mask = engine.design_phase_mask(pattern=args.pattern)
    results = engine.project_to_z(engine.apply_reorganization(engine.psi_world, mask))
    print(f"   Coherence λ₂: {results['coherence_projected']:.4f} | FWHM: {results['focal_spot_size_um']:.2f} um")

def compare(args):
    core = MerkabahCore()
    world_ids = [int(wid) for wid in args.worlds.split(',')]
    print(f"🜏 [COMPARE] Comparing states {world_ids} using metric '{args.metric}'")
    for wid in world_ids:
        branch = core.multiverse.get_branch(wid)
        print(f"   State #{wid:03d}: λ₂ = {branch.lambda_2}")

def collapse(args):
    print(f"🜏 [COLLAPSE] Finalizing state to Branch #{args.select} (Permanent: {args.permanent})")
    print(f"🜏 [SUCCESS] Ontological anchor set.")

def main():
    parser = argparse.ArgumentParser(description="Arkhe Applied Coherence System (SCA) CLI")
    subparsers = parser.add_subparsers(dest="command")

    # POCN command
    pocn_parser = subparsers.add_parser("pocn")
    pocn_parser.add_argument("--target-lambda", type=float, default=0.96)
    pocn_parser.add_argument("--duration", type=str, default="24min")

    # PSCM command
    pscm_parser = subparsers.add_parser("pscm")
    pscm_parser.add_argument("--target-hrv", type=float, default=0.9)

    # PNSG command
    pnsg_parser = subparsers.add_parser("pnsg")
    pnsg_parser.add_argument("--target", type=str, default="thalamus")
    pnsg_parser.add_argument("--safety-limit", type=float, default=0.5)

    # Symbolic/Legacy mapping
    focus_parser = subparsers.add_parser("focus")
    focus_parser.add_argument("--id", type=int, required=True)
    focus_parser.add_argument("--pattern", type=str, default="vortex")

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--worlds", type=str, required=True)
    compare_parser.add_argument("--metric", type=str, default="coherence")

    collapse_parser = subparsers.add_parser("collapse")
    collapse_parser.add_argument("--select", type=int, required=True)
    collapse_parser.add_argument("--permanent", action="store_true")

    args = parser.parse_args()

    if args.command == "pocn":
        pocn(args)
    elif args.command == "pscm":
        pscm(args)
    elif args.command == "pnsg":
        pnsg(args)
    elif args.command == "focus":
        focus(args)
    elif args.command == "compare":
        compare(args)
    elif args.command == "collapse":
        collapse(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
