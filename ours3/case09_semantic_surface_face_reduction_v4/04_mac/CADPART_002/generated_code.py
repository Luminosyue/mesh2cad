#!/usr/bin/env python3
"""
CADPART_002 Generator: Global B-Spline Wing Skin with Caps
Adheres to mandatory contract and architectural specification.
Repairs module import issues by enforcing runtime path resolution.
"""

import argparse
import sys
import json
import os

# Repair: Ensure the directory containing this script (and likely the runtime)
# is in the Python path before attempting imports.
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Also check parent directories or common relative paths if runtime is external
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from case09_v4_runtime import (
        load_semantic_spec,
        build_semantic_wing_skin,
        validate_shape,
        export_step,
        write_provenance
    )
except ImportError as e:
    print(f"FATAL: Could not import case09_v4_runtime. Ensure it exists in {_script_dir} or {_parent_dir}", file=sys.stderr)
    print(f"Import Error: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_002 Wing Skin")
    parser.add_argument("--spec", required=True, help="Path to semantic specification JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # 1. Load Semantic Specification
    try:
        spec = load_semantic_spec(args.spec)
    except Exception as e:
        print(f"ERROR: Failed to load spec from {args.spec}: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure representation key exists for builder compatibility
    if "representation" not in spec:
        # Fallback or default based on architectural intent if missing in loaded spec
        spec["representation"] = "BREP"

    # 2. Build Geometry
    # Contract: call build_semantic_wing_skin(spec, representation=spec["representation"])
    # Architectural Constraint: Intermediate measured sections MUST NOT enter final BRep topology.
    # The runtime function is expected to handle global fitting without leaving section wires.
    try:
        shape = build_semantic_wing_skin(spec, representation=spec["representation"])
    except Exception as e:
        print(f"ERROR: Geometry construction failed: {e}", file=sys.stderr)
        sys.exit(2)

    # 3. Validate Shape
    # Contract: require validate_shape(shape)["valid"]
    validation_result = validate_shape(shape)

    if not validation_result.get("valid", False):
        print(f"ERROR: Shape validation failed.", file=sys.stderr)
        print(f"Details: {json.dumps(validation_result, indent=2)}", file=sys.stderr)
        sys.exit(3)

    # Additional architectural check: Ensure no intermediate section edges exist
    # This is a sanity check on the returned shape metadata if available,
    # otherwise we trust the builder adhered to "generates_section_edges": false
    if validation_result.get("has_intermediate_sections", False):
        print("ERROR: Validation detected intermediate section edges in final topology.", file=sys.stderr)
        sys.exit(4)

    # 4. Export STEP
    try:
        export_step(shape, args.output)
    except Exception as e:
        print(f"ERROR: STEP export failed: {e}", file=sys.stderr)
        sys.exit(5)

    # 5. Write Provenance
    # Contract: MAC_GENERATED=True, part_id and trace
    provenance_data = {
        "part_id": "CADPART_002",
        "source_spec": os.path.basename(args.spec),
        "construction_strategy": "GLOBAL_BSPLINE_SKIN_WITH_CAPS",
        "validation_status": "PASSED",
        "metrics": validation_result.get("metrics", {})
    }

    try:
        write_provenance(
            output_path=args.output,  # Typically writes .provenance alongside or embedded
            data=provenance_data,
            MAC_GENERATED=True,
            part_id="CADPART_002",
            trace=f"CADPART_002_GEN_{os.path.basename(args.spec)}"
        )
    except Exception as e:
        print(f"WARNING: Provenance writing failed: {e}", file=sys.stderr)
        # Non-fatal per strict contract interpretation, but logged.

    print(f"SUCCESS: CADPART_002 generated at {args.output}")


if __name__ == "__main__":
    main()
