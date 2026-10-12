import argparse
import json
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part,
)


CANDIDATE_ID = "candidate_01"

FINAL_OPS = [
    {
        "step": 1,
        "operation": "LOAD_MEASURED_PROFILES",
        "description": "Load exactly 7 closed-loop profiles from measured_cad_spec.sections. Each profile must contain exactly 16 vertices as defined in measured_invariants.profile_vertex_count.",
        "parameters": {
            "source": "MEASURED_CAD_SPEC_SECTIONS",
            "section_count": 7,
            "vertex_count_per_section": 16,
            "axis": "X",
        },
    },
    {
        "step": 2,
        "operation": "VALIDATE_SECTION_COORDINATES",
        "description": "Verify that loaded section coordinates match measured_invariants.section_coordinates exactly without modification.",
        "parameters": {
            "expected_coordinates": [
                0.0202645,
                0.040356956666666666,
                0.06044941333333334,
                0.08054187,
                0.10063432666666668,
                0.12072678333333335,
                0.14081924,
            ],
            "tolerance": 0.0,
        },
    },
    {
        "step": 3,
        "operation": "BUILD_LOFT_SURFACE",
        "description": "Construct a global surface loft through the 7 validated profiles along the X-axis using max_degree 5 and non-ruled interpolation.",
        "parameters": {
            "max_degree": 5,
            "ruled": False,
            "surface_continuity": "GLOBAL_SURFACE",
            "repair_policy": "MINIMUM_PROFILE_COMPLEXITY_MEETING_SHARP_EDGE_RECALL_0.90_WITH_Q1",
        },
    },
    {
        "step": 4,
        "operation": "APPLY_SOURCE_TRANSFORM",
        "description": "Apply the identity transform from part_local_coordinate_system to place the lofted geometry in global space according to SOURCE_MEASURED_TRANSFORM policy.",
        "parameters": {
            "transform_source": "part_local_coordinate_system.local_to_global_transform"
        },
    },
]


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_005 candidate_01")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    spec = load_measured_spec(args.spec)

    # Explicitly call the semantic builder defined in the plan
    shape = build_profile_loft_part(spec)

    # Validate shape against measured invariants and QA targets
    validate_shape(shape, spec)

    # Export valid geometry to STEP
    export_step(shape, args.output)

    # Write provenance linking candidate, ops, and spec
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_005",
        operations=FINAL_OPS,
        spec_path=args.spec,
    )


if __name__ == "__main__":
    main()
