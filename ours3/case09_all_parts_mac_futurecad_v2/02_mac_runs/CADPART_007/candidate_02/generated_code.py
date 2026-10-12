import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_dorsal_feature_part,
)


CANDIDATE_ID = "candidate_02"

FINAL_OPS = [
    {
        "op": "CREATE_PROFILE_SET",
        "target_id": "DorsalProfiles_0",
        "source_ref": "geometry_constraints.profile_curves[0]",
        "parameters": {"section_count": 7, "vertex_count_per_section": 16, "axis": "X"},
    },
    {
        "op": "CREATE_PROFILE_SET",
        "target_id": "DorsalProfiles_1",
        "source_ref": "geometry_constraints.profile_curves[1]",
        "parameters": {"section_count": 7, "vertex_count_per_section": 16, "axis": "X"},
    },
    {
        "op": "BUILD_LOFT",
        "target_id": "DorsalLoft_0",
        "inputs": ["DorsalProfiles_0"],
        "parameters": {
            "axis": "X",
            "max_degree": 5,
            "ruled": False,
            "section_coordinates": [
                -0.08555275,
                -0.06249000833333333,
                -0.03942726666666667,
                -0.016364525000000005,
                0.006698216666666659,
                0.029760958333333323,
                0.0528237,
            ],
        },
    },
    {
        "op": "BUILD_LOFT",
        "target_id": "DorsalLoft_1",
        "inputs": ["DorsalProfiles_1"],
        "parameters": {
            "axis": "X",
            "max_degree": 5,
            "ruled": False,
            "section_coordinates": [
                -0.07076584,
                -0.04338443,
                -0.01600302,
                0.011378390000000002,
                0.0387598,
                0.06614121,
                0.09352262,
            ],
        },
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CADPART_007 candidate 02")
    parser.add_argument("--spec", required=True, help="Path to measured spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime; no embedded coordinates
    spec = load_measured_spec(args.spec)

    # Explicitly invoke the required semantic builder with the plan's operations
    shape = build_dorsal_feature_part(
        spec=spec,
        candidate_id=CANDIDATE_ID,
        operations=FINAL_OPS,
    )

    # Validate resulting shape against measured invariants and plan constraints
    validate_shape(shape, spec)

    # Export validated geometry to STEP
    export_step(shape, args.output)

    # Record provenance for this candidate generation
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_007",
        runtime_builder="build_dorsal_feature_part",
        operations=FINAL_OPS,
        spec_source=args.spec,
    )


if __name__ == "__main__":
    main()
