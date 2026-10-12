import argparse
from case09_v3_runtime import (
    load_repair_spec,
    load_grounding_results,
    build_grounded_repair,
    validate_shape,
    export_step,
    write_provenance
)

def main():
    parser = argparse.ArgumentParser(description="Candidate 0 for CADPART_001: H0 GLOBAL_LOFT")
    parser.add_argument("--spec", required=True, help="Path to repair specification JSON")
    parser.add_argument("--grounding", required=True, help="Path to grounding results JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load inputs via runtime contract
    spec = load_repair_spec(args.spec)
    grounding = load_grounding_results(args.grounding)

    # Build grounded repair using H0 GLOBAL_LOFT hypothesis
    shape, trace = build_grounded_repair(
        spec,
        grounding,
        hypothesis_id="H0",
        require_grounding=True,
        grounding_enabled=True
    )

    # Validate shape before export
    validation_result = validate_shape(shape)
    if not validation_result["valid"]:
        raise RuntimeError(
            f"Shape validation failed for H0 GLOBAL_LOFT: {validation_result}"
        )

    # Export valid shape to STEP
    export_step(shape, args.output)

    # Write provenance with exact metadata per architect output
    write_provenance(
        args.output,
        part_id="CADPART_001",
        hypothesis_id="H0",
        representation="GLOBAL_LOFT",
        grounding_execution_trace=trace,
        MAC_GENERATED=True
    )

if __name__ == "__main__":
    main()
