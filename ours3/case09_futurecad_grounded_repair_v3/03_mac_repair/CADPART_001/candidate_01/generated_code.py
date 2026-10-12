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
    parser = argparse.ArgumentParser(description="CADPART_001 Candidate 1: H1 GUIDED_LOFT")
    parser.add_argument("--spec", required=True, help="Path to repair specification JSON")
    parser.add_argument("--grounding", required=True, help="Path to grounding results JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load inputs via runtime contract
    spec = load_repair_spec(args.spec)
    grounding = load_grounding_results(args.grounding)

    # Build grounded repair for Hypothesis H1 (GUIDED_LOFT)
    # Note: While architect output labels primary as GLOBAL_LOFT, 
    # the prompt explicitly requests Candidate 1 for H1 GUIDED_LOFT.
    # We pass hypothesis_id="H1" as mandated by the runtime contract instructions.
    shape, trace = build_grounded_repair(
        spec, 
        grounding, 
        hypothesis_id="H1", 
        require_grounding=True, 
        grounding_enabled=True
    )

    # Validate and export
    validation_result = validate_shape(shape)
    if not validation_result["valid"]:
        raise RuntimeError(f"Shape validation failed for H1 GUIDED_LOFT: {validation_result}")

    export_step(shape, args.output)

    # Write provenance
    write_provenance(
        args.output,
        part_id="CADPART_001",
        hypothesis_id="H1",
        representation="GUIDED_LOFT",
        grounding_execution_trace=trace,
        MAC_GENERATED=True
    )

if __name__ == "__main__":
    main()
