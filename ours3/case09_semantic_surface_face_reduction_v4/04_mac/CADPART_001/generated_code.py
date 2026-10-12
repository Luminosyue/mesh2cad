#!/usr/bin/env python3
"""
CADPART_001 Generator
Construction Strategy: GLOBAL_BSPLINE_FITTING_NO_LOFT
Compliant with case09_v4_runtime contract.
"""

import argparse
import sys
import json
import os

# Mandatory contract imports
from case09_v4_runtime import (
    load_semantic_spec,
    build_semantic_wing_skin,
    validate_shape,
    export_step,
    write_provenance
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_001 Wing Skin")
    parser.add_argument("--spec", type=str, required=True, help="Path to semantic specification JSON")
    parser.add_argument("--output", type=str, required=True, help="Output STEP file path")
    args = parser.parse_args()

    # 1. Load Semantic Specification
    spec = load_semantic_spec(args.spec)
    
    # Ensure representation key exists for the builder contract
    if "representation" not in spec:
        # Fallback or extraction from executable_architecture if nested
        if "executable_architecture" in spec:
            spec["representation"] = spec["executable_architecture"]
        else:
            raise ValueError("Specification missing 'representation' or 'executable_architecture' block")

    # 2. Build Semantic Wing Skin
    # Contract: Intermediate measured sections MUST NOT enter final BRep topology.
    # The builder handles global fitting internally without exposing section wires.
    shape = build_semantic_wing_skin(spec, representation=spec["representation"])

    # 3. Validate Shape
    validation_result = validate_shape(shape)
    if not validation_result.get("valid", False):
        print(f"ERROR: Shape validation failed for {spec.get('part_id', 'UNKNOWN')}", file=sys.stderr)
        print(f"Details: {json.dumps(validation_result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    # 4. Export STEP
    export_step(shape, args.output)

    # 5. Write Provenance
    trace_info = {
        "construction_strategy": "GLOBAL_BSPLINE_FITTING_NO_LOFT",
        "validation_metrics": validation_result,
        "input_spec": os.path.abspath(args.spec),
        "runtime_contract": "case09_v4_runtime"
    }
    
    write_provenance(
        output_path=args.output,
        part_id=spec.get("part_id", "CADPART_001"),
        trace=trace_info,
        MAC_GENERATED=True
    )

    print(f"Successfully generated {args.output}")


if __name__ == "__main__":
    main()
