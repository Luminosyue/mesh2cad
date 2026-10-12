import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_global_loft_part
)

CANDIDATE_ID = "candidate_02"

FINAL_OPS = [
    {
        "step": 1,
        "operation": "LOAD_MEASURED_PROFILES",
        "parameters": {
            "source_path": "measured_cad_spec.operations[0].sections",
            "section_count": 14,
            "vertex_count_per_section": 10,
            "axis": "Y"
        },
        "description": "Load exactly 14 measured cross-sections with precise vertex coordinates from the validated spec. No resampling or interpolation allowed."
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
        },
        "description": "Construct a single non-ruled B-Spline loft surface through all 14 sections. Enforce max_degree=5 and ruled=false per measured invariants."
    },
    {
        "step": 3,
        "operation": "APPLY_SOURCE_TRANSFORM",
        "parameters": {
            "transform_matrix": "geometry_constraints.part_local_coordinate_system.local_to_global_transform",
            "target_body": "STEP_2_OUTPUT"
        },
        "description": "Apply identity transform from source measured coordinate system to ensure placement matches original grounding."
    }
]


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_000 Candidate 02")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_spec = load_measured_spec(args.spec)

    # Explicitly call the required semantic builder with the loaded spec
    shape = build_global_loft_part(spec=measured_spec)

    # Validate the constructed shape against all validation steps defined in the plan
    # Repair: removed unexpected 'spec' kwarg that caused TypeError; pass measured_spec as positional arg
    validation_result = validate_shape(
        shape,
        measured_spec,
        candidate_id=CANDIDATE_ID,
        validation_checks=[
            "V1_SECTION_COUNT",
            "V2_VERTEX_PRESERVATION",
            "V3_DEGREE_LIMIT",
            "V4_NON_RULED_CHECK",
            "V5_BBOX_CONFORMANCE",
            "V6_SHARP_EDGE_RECALL",
            "V7_FEATURE_BOUNDARY_RECALL",
            "V8_NO_TRANSVERSE_STRIPS"
        ]
    )

    if not validation_result.get("passed", False):
        raise RuntimeError(
            f"Validation failed for {CANDIDATE_ID}: {validation_result.get('failures', 'Unknown error')}"
        )

    # Export the validated shape to STEP format
    export_step(shape, args.output)

    # Write program provenance recording the candidate generation details
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_000",
        runtime_builder="build_global_loft_part",
        final_ops=FINAL_OPS,
        validation_summary=validation_result,
        spec_source=args.spec
    )


if __name__ == "__main__":
    main()
