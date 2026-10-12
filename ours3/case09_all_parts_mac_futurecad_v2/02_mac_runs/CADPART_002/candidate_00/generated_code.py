import argparse
import sys

# Required imports from the Multi-Agent-CAD runtime environment
from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_002 Candidate 0")
    parser.add_argument("--spec", required=True, help="Path to measured specification JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Configuration constants derived from ARCHITECT_PLAN
    CANDIDATE_ID = "candidate_00"
    PART_ID = "CADPART_002"
    RUNTIME_BUILDER = "build_profile_loft_part"

    # 1. Load measured JSON at runtime
    spec_data = load_measured_spec(args.spec)

    # 2. Call the semantic builder explicitly
    shape = build_profile_loft_part(spec=spec_data)

    # 3. Validate shape against architectural constraints
    # REPAIR: validate_shape takes only 1 positional argument (the shape).
    # Validation configuration is expected to be embedded in the spec or handled internally.
    is_valid, report = validate_shape(shape)
    
    if not is_valid:
        print(f"Validation failed for {CANDIDATE_ID}: {report}", file=sys.stderr)
        sys.exit(1)

    # 4. Export STEP
    export_step(shape, args.output)

    # 5. Write provenance
    provenance_metadata = {
        "part_id": PART_ID,
        "candidate_id": CANDIDATE_ID,
        "runtime_builder": RUNTIME_BUILDER,
        "hypothesis": "H1_MEASURED_PROFILE_LOFT",
        "validation_report": report
    }
    write_program_provenance(args.output, provenance_metadata)

    print(f"Successfully generated {CANDIDATE_ID} for {PART_ID}")


if __name__ == "__main__":
    main()
