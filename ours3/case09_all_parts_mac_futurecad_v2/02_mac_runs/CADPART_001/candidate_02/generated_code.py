import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part,
)


CANDIDATE_ID = "candidate_02"

FINAL_OPS = [
    {
        "step": 1,
        "action": "LOAD_PROFILE_SERIES",
        "source": "measured_cad_spec.operations[0].sections",
        "parameters": {"axis": "X", "section_count": 20, "vertex_count_per_section": 12},
    },
    {
        "step": 2,
        "action": "BUILD_GLOBAL_LOFT",
        "builder": "build_profile_loft_part",
        "inputs": ["ProfileSeries"],
        "constraints": {
            "max_degree": 5,
            "ruled": False,
            "continuity": "G1_MINIMUM",
            "output_topology": "SINGLE_CONTINUOUS_SURFACE",
        },
    },
    {
        "step": 3,
        "action": "APPLY_PLACEMENT",
        "policy": "SOURCE_MEASURED_TRANSFORM",
        "transform_source": "geometry_constraints.part_local_coordinate_system.local_to_global_transform",
    },
]


def main():
    parser = argparse.ArgumentParser(description="Generate program candidate 2 for CADPART_001")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_cad_spec = load_measured_spec(args.spec)

    # Extract grounding data explicitly from spec with safe access
    operations = measured_cad_spec.get("operations", [])
    if not operations:
        raise RuntimeError("No operations found in measured spec")

    op0 = operations[0]
    sections = op0.get("sections", [])

    sharp_edge_repair = measured_cad_spec.get("sharp_edge_repair", {})
    chosen_section_counts = sharp_edge_repair.get("chosen_section_counts", {}).get("CADPART_001", 20)
    chosen_profile_vertex_counts = sharp_edge_repair.get("chosen_profile_vertex_counts", {}).get("CADPART_001", 12)

    # Safely extract transform; default to identity if geometry_constraints is missing
    geometry_constraints = measured_cad_spec.get("geometry_constraints", {})
    local_to_global_transform = geometry_constraints.get(
        "part_local_coordinate_system", {}
    ).get("local_to_global_transform", None)

    # Validate input parameters match plan requirements using semantic keys
    assert len(sections) == chosen_section_counts, \
        f"Expected {chosen_section_counts} sections, got {len(sections)}"

    # Normalize section data: ensure 'vertices' key exists and contains valid point lists
    # This repairs the issue where sections might have empty vertices or use alternative keys
    normalized_sections = []
    for idx, sec in enumerate(sections):
        # Try multiple possible keys for point data in measured specs
        pts = sec.get("vertices") or sec.get("points") or sec.get("profile_points") or []
        
        # If points are stored as a flat list of coordinates, reshape them
        if pts and isinstance(pts[0], (int, float)):
            dim = 3
            if len(pts) % dim != 0:
                raise ValueError(f"Section {idx} has invalid flat coordinate list length {len(pts)}")
            pts = [pts[i:i+dim] for i in range(0, len(pts), dim)]
        
        vcount = len(pts)
        assert vcount == chosen_profile_vertex_counts, \
            f"Section {idx} has {vcount} vertices, expected {chosen_profile_vertex_counts}"
        
        # Create normalized section dict ensuring 'vertices' key is populated
        norm_sec = dict(sec)
        norm_sec["vertices"] = pts
        normalized_sections.append(norm_sec)

    # Build the loft part using the required semantic builder with normalized sections
    shape = build_profile_loft_part(
        sections=normalized_sections,
        axis="X",
        max_degree=5,
        ruled=False,
        continuity="G1_MINIMUM",
        output_topology="SINGLE_CONTINUOUS_SURFACE",
        transform=local_to_global_transform,
    )

    # Validate the resulting shape against all required checks
    validation_results = validate_shape(
        shape=shape,
        measured_spec=measured_cad_spec,
        checks=[
            "VERIFY_SINGLE_GLOBAL_LOFT_FEATURE_EXISTS",
            "VERIFY_SECTION_COUNT_EQUALS_20",
            "VERIFY_PROFILE_VERTEX_COUNT_EQUALS_12_PER_SECTION",
            "VERIFY_NO_STRIP_FACE_TOPOLOGY",
            "VERIFY_BBOX_WITHIN_MEASURED_TOLERANCE",
            "VERIFY_SHARP_EDGE_RECALL_GE_0.90",
            "VERIFY_FEATURE_BOUNDARY_RECALL_GE_0.99",
        ],
    )

    if not validation_results.get("passed", False):
        raise RuntimeError(f"Validation failed for {CANDIDATE_ID}: {validation_results}")

    # Export valid shape to STEP
    export_step(shape, args.output)

    # Write provenance record
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_001",
        runtime_builder="build_profile_loft_part",
        final_ops=FINAL_OPS,
        validation_results=validation_results,
        spec_source=args.spec,
    )


if __name__ == "__main__":
    main()
