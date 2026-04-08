#!/usr/bin/env python3
import sys
import os
import argparse
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from physics.multiverse_core import MerkabahCore
from physics.phase_focusing_engine import PhaseFocusingEngine
from physics.bio_coherence import MitochondrialKuramoto
from physics.ghost_optics import GhostOpticalCorrector
from physics.bio_quantum_sync import BioQuantumSynchronizer

def focus(args):
    core = MerkabahCore()
    print(f"🜏 [FOCUS] Targeting World #{args.world} with pattern '{args.pattern}'")

    engine = PhaseFocusingEngine(core, world_id=args.world)
    mask = engine.design_phase_mask(pattern=args.pattern)
    field_reorganized = engine.apply_reorganization(engine.psi_world, mask)
    results = engine.project_to_z(field_reorganized)

    output_file = f"world_{args.world}_projection_z.png"
    engine.visualize_projection(results, output_file)

    print(f"🜏 [RESULT] Projection Z complete for World #{args.world}")
    print(f"   Coherence lambda2: {results['coherence_projected']:.4f}")
    print(f"   Focal spot size: {results['focal_spot_size_um']:.2f} um")
    print(f"   Output saved to: {output_file}")

def compare(args):
    core = MerkabahCore()
    world_ids = [int(wid) for wid in args.worlds.split(',')]
    print(f"🜏 [COMPARE] Comparing worlds {world_ids} using metric '{args.metric}'")

    comparison = {}
    for wid in world_ids:
        branch = core.multiverse.get_branch(wid)
        if args.metric == 'coherence':
            comparison[wid] = branch.lambda_2
        else:
            comparison[wid] = "N/A"

    print(f"\n--- Multiverse Comparison ({args.metric}) ---")
    for wid, val in comparison.items():
        print(f"World #{wid:03d}: {val}")
    print("------------------------------------------")

def collapse(args):
    core = MerkabahCore()
    print(f"🜏 [COLLAPSE] Collapsing multiverse to Branch #{args.select}...")

    branch = core.multiverse.get_branch(args.select)

    status = {
        "collapsed_branch": args.select,
        "final_coherence": branch.lambda_2,
        "permanent": args.permanent,
        "timestamp": datetime.now().isoformat()
    }

    with open("collapse_status.json", "w") as f:
        json.dump(status, f, indent=2)

    print(f"🜏 [SUCCESS] Multiverse collapsed to Branch #{args.select}.")
    print(f"   Final λ₂ = {branch.lambda_2}")
    if args.permanent:
        print("   Status: PERMANENT BRANCH SELECTION ACTIVE")

def bio_sync(args):
    print(f"🜏 [BIO-SYNC] Initiating bio-resonance for Operator '{args.operator}'")
    print(f"   Target: mitochondria | NIR: {args.nir} | Modulation: {args.modulation}")

    # Parse modulation (e.g., "40Hz" -> 40.0)
    try:
        mod_val = float(args.modulation.replace('Hz', ''))
    except ValueError:
        mod_val = 40.0

    engine = MitochondrialKuramoto()
    results = engine.simulate(modulation_hz=mod_val)

    output_file = f"bio_sync_{args.operator.replace(' ', '_')}.png"
    engine.visualize(results, output_file)

    print(f"🜏 [RESULT] Bio-sync loop complete for {args.operator}")
    print(f"   Basal Coherence: {results['r_basal']:.3f}")
    print(f"   Induced Coherence: {results['r_induced']:.3f}")
    print(f"   Improvement: {results['improvement_percent']:.1f}%")
    print(f"   Equivalent lambda2: {results['lambda2_equiv']:.4f}")
    print(f"   Visualization saved to: {output_file}")

def etch(args):
    print(f"🜏 [ETCH] Applying Law '{args.law}' to World #42")
    if args.ghost_correction:
        print("   Status: GHOST OPTICAL CORRECTION ACTIVE (Branches 91, 7)")

        core = MerkabahCore()
        branch = core.multiverse.get_branch(42)

        corrector = GhostOpticalCorrector()
        psi_corrected = corrector.apply_correction(branch.psi_c)
        improvement = corrector.calculate_fwhm_improvement(branch.psi_c, psi_corrected)

        print(f"   Resolution Improvement: {improvement['improvement_factor']:.2f}x")
        print(f"   Final Resolution: {improvement['effective_resolution_um']:.2f} um")

    print(f"🜏 [SUCCESS] Law '{args.law}' permanently etched into Arkhe-Chain.")

def sync_thalamus(args):
    print(f"🜏 [SYNC-THALAMUS] Locking bio-oscillators to Strontium Clock...")

    sync = BioQuantumSynchronizer(modulation_hz=40.0)
    results = sync.simulate_locked_loop()

    print(f"🜏 [RESULT] Thalamocortical resonance achieved.")
    print(f"   Final Bio-Coherence: {results['final_coherence']:.4f}")
    print(f"   Strontium Lock Status: {'STABLE' if results['is_locked'] else 'DRIFTING'}")

def main():
    parser = argparse.ArgumentParser(description="Arkhe Multiverse Control")
    subparsers = parser.add_subparsers(dest="command")

    # Focus command
    focus_parser = subparsers.add_parser("focus")
    focus_parser.add_argument("--world", type=int, required=True)
    focus_parser.add_argument("--pattern", type=str, default="spherical")

    # Compare command
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--worlds", type=str, required=True, help="Comma-separated world IDs")
    compare_parser.add_argument("--metric", type=str, default="coherence")

    # Collapse command
    collapse_parser = subparsers.add_parser("collapse")
    collapse_parser.add_argument("--select", type=int, required=True)
    collapse_parser.add_argument("--permanent", action="store_true")

    # Bio-sync command
    sync_parser = subparsers.add_parser("bio_sync")
    sync_parser.add_argument("--operator", type=str, required=True)
    sync_parser.add_argument("--nir", type=str, default="850nm")
    sync_parser.add_argument("--modulation", type=str, default="40Hz")

    # Etch command
    etch_parser = subparsers.add_parser("etch")
    etch_parser.add_argument("--law", type=str, required=True)
    etch_parser.add_argument("--ghost-correction", action="store_true")

    # Sync thalamus command
    thalamus_parser = subparsers.add_parser("sync_thalamus")

    args = parser.parse_args()

    if args.command == "focus":
        focus(args)
    elif args.command == "compare":
        compare(args)
    elif args.command == "collapse":
        collapse(args)
    elif args.command == "bio_sync":
        bio_sync(args)
    elif args.command == "etch":
        etch(args)
    elif args.command == "sync_thalamus":
        sync_thalamus(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
