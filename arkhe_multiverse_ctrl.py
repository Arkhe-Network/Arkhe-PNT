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

    args = parser.parse_args()

    if args.command == "focus":
        focus(args)
    elif args.command == "compare":
        compare(args)
    elif args.command == "collapse":
        collapse(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
