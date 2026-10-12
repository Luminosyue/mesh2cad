import argparse
import sys

# Required imports from the Multi-Agent-CAD runtime environment
from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_global_loft_part
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_000 Candidate 0")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Configuration constants derived from ARCHITECT_PLAN
    CANDIDATE_ID = "candidate_00"
    PART_ID = "CADPART_000"

    # FINAL_OPS corresponds exactly to the plan's operation_sequence
    FINAL_OPS = [
        {
            "step": 1,
            "operation": "LOAD_MEASURED_PROFILES",
            "parameters": {
                "source_path": "measured_cad_spec.operations[0].sections",
                "section_count": 14,
                "vertex_count_per_section": 10,
                "axis": "Y"
            }
        },
        {
            "step": 2,
            "operation": "BUILD_GLOBAL_B_SPLINE_LOFT",
            "parameters": {
                "input_profiles": "STEP_1_OUTPUT",
                "max_degree": 5,
                "ruled": False,
                "surface_continuity": "C2",
                "parameterization": "CENTRIPETAL"
            }
        },
        {
            "step": 3,
            "operation": "APPLY_SOURCE_TRANSFORM",
            "parameters": {
                "transform_matrix": "geometry_constraints.part_local_coordinate_system.local_to_global_transform",
                "target_body": "STEP_2_OUTPUT"
            }
        }
    ]

    # Step 1: Load measured specification at runtime
    measured_spec = load_measured_spec(args.spec)

    # Step 2: Explicitly call the required semantic builder
    # REPAIR: The previous error indicated 'operations' is not a valid keyword argument.
    # Corrected signature to pass only 'spec' as per runtime contract for this builder.
    shape = build_global_loft_part(spec=measured_spec)

    # Step 3: Validate shape against architectural constraints
    is_valid = validate_shape(shape, measured_spec)
    if not is_valid:
        print(f"Validation failed for {PART_ID} {CANDIDATE_ID}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Export valid geometry to STEP format
    export_step(shape, args.output)

    # Step 5: Write provenance linking candidate to plan and measurements
    write_program_provenance(
        output_path=args.output,
        part_id=PART_ID,
        candidate_id=CANDIDATE_ID,
        plan_operations=FINAL_OPS,
        spec_source=args.spec
    )

    print(f"Successfully generated {CANDIDATE_ID} for {PART_ID}")


if __name__ == "__main__":
    main()
