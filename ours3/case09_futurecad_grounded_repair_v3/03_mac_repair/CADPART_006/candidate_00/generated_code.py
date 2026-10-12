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
    parser = argparse.ArgumentParser(description="Candidate 0 for CADPART_006 H0 MASTER_PATTERN_COARSE")
    parser.add_argument("--spec", required=True, help="Path to repair spec")
    parser.add_argument("--grounding", required=True, help="Path to grounding results")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load inputs via runtime contract
    spec = load_repair_spec(args.spec)
    grounding = load_grounding_results(args.grounding)

    # Build grounded repair for H0 hypothesis
    shape, trace = build_grounded_repair(
        spec,
        grounding,
        hypothesis_id="H0",
        require_grounding=False,
        grounding_enabled=True
    )

    # Validate shape before export
    validation_result = validate_shape(shape)
    if not validation_result["valid"]:
        raise RuntimeError(f"Shape validation failed for H0: {validation_result}")

    # Export valid shape
    export_step(shape, args.output)

    # Write provenance with exact required metadata
    write_provenance(
        args.output,
        part_id="CADPART_006",
        hypothesis_id="H0",
        representation="MASTER_PATTERN_COARSE",
        grounding_execution_trace=trace,
        MAC_GENERATED=True
    )

if __name__ == "__main__":
    main()
