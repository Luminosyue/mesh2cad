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
    parser = argparse.ArgumentParser(description="Candidate 2 for CADPART_006: H2 MASTER_PATTERN_HIGH_RES")
    parser.add_argument("--spec", required=True, help="Path to repair specification JSON")
    parser.add_argument("--grounding", required=True, help="Path to grounding results JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load inputs per runtime contract
    spec = load_repair_spec(args.spec)
    grounding = load_grounding_results(args.grounding)

    # Build grounded repair for Hypothesis H2
    shape, trace = build_grounded_repair(
        spec,
        grounding,
        hypothesis_id="H2",
        require_grounding=False,
        grounding_enabled=True
    )

    # Validate shape before export
    validation_result = validate_shape(shape)
    if not validation_result["valid"]:
        raise RuntimeError(f"Shape validation failed for H2 MASTER_PATTERN_HIGH_RES: {validation_result}")

    # Export valid shape
    export_step(shape, args.output)

    # Write provenance with exact metadata
    write_provenance(
        args.output,
        part_id="CADPART_006",
        hypothesis_id="H2",
        representation="MASTER_PATTERN_HIGH_RES",
        grounding_execution_trace=trace,
        MAC_GENERATED=True
    )

if __name__ == "__main__":
    main()
