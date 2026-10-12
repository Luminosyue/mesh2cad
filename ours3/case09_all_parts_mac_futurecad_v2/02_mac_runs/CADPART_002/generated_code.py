import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part
)

CANDIDATE_ID = "candidate_01"


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_002 Candidate 01")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_spec = load_measured_spec(args.spec)

    # Explicitly call the semantic builder defined in the plan
    shape = build_profile_loft_part(
        spec=measured_spec
    )

    # Validate shape against plan constraints
    # Fixed: removed unsupported 'spec' keyword argument causing TypeError
    validation_result = validate_shape(
        shape=shape,
        candidate_id=CANDIDATE_ID
    )

    if not validation_result.get("valid", False):
        print(f"Validation failed for {CANDIDATE_ID}: {validation_result}", file=sys.stderr)
        sys.exit(1)

    # Export valid geometry to STEP
    export_step(shape, args.output)

    # Write provenance record
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_002",
        builder="build_profile_loft_part",
        validation=validation_result
    )


if __name__ == "__main__":
    main()
