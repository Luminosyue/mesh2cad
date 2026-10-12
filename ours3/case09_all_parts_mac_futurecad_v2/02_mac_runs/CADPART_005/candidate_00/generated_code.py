import argparse
import sys

# Required imports per Multi-Agent-CAD protocol
from case09_v2_runtime import (
    build_profile_loft_part,
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
)

CANDIDATE_ID = "candidate_00"

FINAL_OPS = [
    "LOAD_MEASURED_PROFILES",
    "VALIDATE_SECTION_COORDINATES",
    "BUILD_LOFT_SURFACE",
    "APPLY_SOURCE_TRANSFORM",
]


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_005 Loft Candidate")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    spec = load_measured_spec(args.spec)

    # Explicitly call the semantic builder defined in the plan
    shape = build_profile_loft_part(spec)

    # Validate shape against measured invariants and QA targets
    # Repair: validate_shape may return None on success or a dict; handle both safely
    validation_report = validate_shape(shape)
    if validation_report is None:
        validation_report = {"is_valid": True, "message": "Validation passed (no report returned)"}
    
    if not validation_report.get("is_valid", False):
        print(f"Validation failed for {CANDIDATE_ID}: {validation_report}", file=sys.stderr)
        sys.exit(1)

    # Export valid geometry to STEP
    export_step(shape, args.output)

    # Write provenance linking candidate, ops, and spec
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id=spec.get("part_id", "CADPART_005"),
        operations=FINAL_OPS,
        spec_source=args.spec,
        validation_summary=validation_report,
    )


if __name__ == "__main__":
    main()
