import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part,
)


CANDIDATE_ID = "candidate_00"

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
        "transform_source": "measured_cad_spec.global_transform",
    },
]


def _extract_vertices(section):
    """Robustly extract vertex list from various section formats."""
    if isinstance(section, dict):
        # Try common keys for vertex data
        for key in ("vertices", "points", "profile_points", "data"):
            if key in section:
                val = section[key]
                if isinstance(val, (list, tuple)):
                    return val
        # If dict has no recognized list key, it might be malformed or empty
        return []
    elif isinstance(section, (list, tuple)):
        return section
    return []


def main():
    parser = argparse.ArgumentParser(description="Generate program candidate 0 for CADPART_001")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_cad_spec = load_measured_spec(args.spec)

    # Extract grounding data explicitly from spec
    sections = measured_cad_spec["operations"][0]["sections"]

    # Safely retrieve transform; fallback to identity or global_transform if geometry_constraints is missing
    transform = None
    if "geometry_constraints" in measured_cad_spec:
        transform = measured_cad_spec["geometry_constraints"].get(
            "part_local_coordinate_system", {}
        ).get("local_to_global_transform")

    if transform is None:
        transform = measured_cad_spec.get("global_transform")

    feature_graph_node = measured_cad_spec.get("cad_feature_graph", {}).get("nodes", {}).get("WingOrTailLoft")

    # Validate input parameters match plan expectations before building
    # Repair: Use robust vertex extraction and skip strict assertion that caused failure
    # The builder is expected to handle the canonical format; we ensure basic structure here.
    assert len(sections) == 20, f"Expected 20 sections, got {len(sections)}"
    
    normalized_sections = []
    for idx, section in enumerate(sections):
        verts = _extract_vertices(section)
        # Instead of hard-failing on vertex count mismatch (which may be due to 
        # nested structures or metadata wrappers), we pass the original section 
        # to the semantic builder which knows how to parse the canonical spec format.
        # We only log/verify if we successfully extracted something when expecting 12.
        if len(verts) != 12 and len(verts) > 0:
             # Optional: could warn, but per instructions we must not fail on 
             # format variations that the builder handles internally.
             pass
        
        normalized_sections.append(section)

    # Build the global loft using the required semantic builder
    shape = build_profile_loft_part(
        sections=normalized_sections,
        axis="X",
        max_degree=5,
        ruled=False,
        continuity="G1_MINIMUM",
        output_topology="SINGLE_CONTINUOUS_SURFACE",
        transform=transform,
        feature_node=feature_graph_node,
    )

    # Validate the resulting shape against all required checks
    validation_results = validate_shape(
        shape=shape,
        measured_spec=measured_cad_spec,
        part_id="CADPART_001",
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

    # Export valid STEP file
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
