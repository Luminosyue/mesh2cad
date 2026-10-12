import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    build_profile_loft_part,
    validate_shape,
    export_step,
    write_program_provenance,
)

CANDIDATE_ID = "candidate_02"

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


def extract_vertices(section):
    """Safely extract vertex list from various possible section structures."""
    if isinstance(section, dict):
        for key in ("vertices", "points", "profile", "coords", "data"):
            if key in section:
                val = section[key]
                if isinstance(val, (list, tuple)):
                    return val
                elif isinstance(val, dict) and "vertices" in val:
                    return val["vertices"]
        raise ValueError("Dict section missing recognizable vertex key")
    elif isinstance(section, (list, tuple)):
        if len(section) > 0 and isinstance(section[0], dict):
            return extract_vertices(section[0])
        return section
    else:
        raise ValueError(f"Unsupported section type: {type(section)}")


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_003 candidate 02 loft program")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Step 1: Load measured spec at runtime
    measured_spec = load_measured_spec(args.spec)

    # Extract sections directly from measured spec operations as per plan
    sections_raw = measured_spec["operations"][0]["sections"]
    if len(sections_raw) != 7:
        raise ValueError(f"Expected 7 sections, got {len(sections_raw)}")

    # Normalize sections to ensure builder receives consistent structure
    normalized_sections = []
    for idx, section in enumerate(sections_raw):
        try:
            verts = extract_vertices(section)
        except ValueError as e:
            raise ValueError(f"Section {idx} vertex extraction failed: {e}")

        if len(verts) != 12:
            raise ValueError(f"Section {idx} has {len(verts)} vertices, expected 12")

        # Ensure standard dict format with 'vertices' key for builder compatibility
        if isinstance(section, dict):
            clean_section = dict(section)
            clean_section["vertices"] = verts
            normalized_sections.append(clean_section)
        else:
            normalized_sections.append({"vertices": verts})

    # Step 2: Explicitly call semantic builder with corrected argument name
    loft_params = FINAL_OPS[1]["parameters"]
    shape = build_profile_loft_part(
        sections=normalized_sections,
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
        measured_spec=measured_spec,
        candidate_id=CANDIDATE_ID,
        required_global_surface=True,
        min_sharp_edge_recall=0.9,
    )
    if not validation_result["valid"]:
        raise RuntimeError(f"Shape validation failed: {validation_result['reason']}")

    # Export STEP
    export_step(shape, args.output)

    # Write provenance
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_003",
        runtime_builder="build_profile_loft_part",
        final_ops=FINAL_OPS,
        measured_spec_source=args.spec,
        validation_summary=validation_result,
    )


if __name__ == "__main__":
    main()
