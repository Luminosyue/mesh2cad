import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    build_profile_loft_part,
    validate_shape,
    export_step,
    write_program_provenance,
)


CANDIDATE_ID = "candidate_01"

FINAL_OPS = [
    {
        "step": 1,
        "operation": "LOAD_MEASURED_PROFILES",
        "parameters": {
            "source": "measured_cad_spec.operations[0].sections",
            "section_count": 7,
            "vertex_count_per_section": 12,
            "axis": "X",
        },
        "validation": "Verify exactly 7 sections loaded with 12 vertices each matching measured_cad_spec coordinates to float64 precision.",
    },
    {
        "step": 2,
        "operation": "CONSTRUCT_LOFT_SOLID",
        "parameters": {
            "builder": "build_profile_loft_part",
            "input_profiles": "ProfileSeries",
            "loft_axis": "X",
            "max_degree": 5,
            "ruled": False,
            "continuity": "C2_INTERPOLATED",
            "alignment": "PARAMETRIC_UNIFORM",
            "global_surface": True,
        },
        "validation": "Ensure resulting solid possesses global_surface=true property and no additional fillet/chamfer operations are applied.",
    },
    {
        "step": 3,
        "operation": "VALIDATE_SHARP_EDGE_RECALL",
        "parameters": {
            "target_recall_threshold": 0.9,
            "predicted_recall": 0.9456489456489456,
            "policy": "MINIMUM_PROFILE_COMPLEXITY_MEETING_SHARP_EDGE_RECALL_0.90_WITH_Q1",
        },
        "validation": "Confirm post-construction sharp edge recall >= 0.90 using predicted_sharp_edge_recall metric from measured payload.",
    },
]


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_003 program candidate 1")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Step 1: Load measured spec at runtime
    spec = load_measured_spec(args.spec)

    # Extract sections according to plan
    sections = spec["operations"][0]["sections"]
    assert len(sections) == 7, f"Expected 7 sections, got {len(sections)}"

    # Step 2: Explicitly call semantic builder with corrected argument name 'sections'
    # The previous error indicated 'profiles' is not a valid keyword argument.
    # We pass the raw section objects directly as the builder handles internal extraction.
    loft_params = FINAL_OPS[1]["parameters"]
    shape = build_profile_loft_part(
        sections=sections,
        loft_axis=loft_params["loft_axis"],
        max_degree=loft_params["max_degree"],
        ruled=loft_params["ruled"],
        continuity=loft_params["continuity"],
        alignment=loft_params["alignment"],
        global_surface=loft_params["global_surface"],
    )

    # Step 3: Validate shape against measured spec constraints
    validation_result = validate_shape(
        shape=shape,
        spec=spec,
        candidate_id=CANDIDATE_ID,
        operations=FINAL_OPS,
    )
    if not validation_result.get("valid", False):
        raise RuntimeError(f"Shape validation failed: {validation_result}")

    # Export STEP
    export_step(shape, args.output)

    # Write provenance
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_003",
        runtime_builder="build_profile_loft_part",
        operations=FINAL_OPS,
        spec_source=args.spec,
        validation=validation_result,
    )


if __name__ == "__main__":
    main()
