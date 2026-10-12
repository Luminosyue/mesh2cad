import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    build_profile_loft_part,
    validate_shape,
    export_step,
    write_program_provenance,
)

CANDIDATE_ID = "candidate_00"

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


def _extract_vertices(section_data):
    """
    Robustly extract vertex list from a section entry which may be:
      - a dict with keys like 'vertices', 'points', 'profile', 'coords'
      - a raw list/tuple of points
      - an object with a .vertices or .points attribute
    Returns a list of vertices or raises ValueError if none found.
    """
    if isinstance(section_data, (list, tuple)):
        return list(section_data)

    if isinstance(section_data, dict):
        for key in ("vertices", "points", "profile", "coords", "data"):
            if key in section_data and section_data[key] is not None:
                val = section_data[key]
                if isinstance(val, (list, tuple)):
                    return list(val)
                # Handle nested dict e.g. {"vertices": {"data": [...]}}
                if isinstance(val, dict):
                    for subkey in ("data", "values", "coordinates"):
                        if subkey in val and isinstance(val[subkey], (list, tuple)):
                            return list(val[subkey])
        raise KeyError(
            f"Section dictionary missing recognized vertex key. Available keys: {list(section_data.keys())}"
        )

    # Handle objects with attributes
    for attr in ("vertices", "points", "profile", "coords"):
        if hasattr(section_data, attr):
            val = getattr(section_data, attr)
            if isinstance(val, (list, tuple)):
                return list(val)

    raise TypeError(f"Unsupported section type: {type(section_data)}")


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_003 candidate program")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Step 1: Load measured spec at runtime
    measured_spec = load_measured_spec(args.spec)

    # Extract sections according to plan operation 1 parameters
    sections_source = measured_spec["operations"][0]["sections"]
    assert len(sections_source) == 7, f"Expected exactly 7 sections per measured spec, got {len(sections_source)}"

    normalized_profiles = []
    for idx, sec in enumerate(sections_source):
        verts = _extract_vertices(sec)
        assert len(verts) == 12, f"Section {idx} must have exactly 12 vertices, got {len(verts)}"
        normalized_profiles.append(verts)

    # Step 2: Explicitly call semantic builder with plan parameters
    # FIX: Changed 'profiles' to 'profile_series' to match build_profile_loft_part signature
    loft_params = FINAL_OPS[1]["parameters"]
    shape = build_profile_loft_part(
        profile_series=normalized_profiles,
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
        final_ops=FINAL_OPS,
        measured_spec_path=args.spec,
        validation_summary=validation_result,
    )


if __name__ == "__main__":
    main()
