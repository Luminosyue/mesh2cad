import argparse
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_005 Candidate 02")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Step 1: LOAD_MEASURED_PROFILES
    spec = load_measured_spec(args.spec)

    if not isinstance(spec, dict):
        raise ValueError(f"Expected spec to be a dict, got {type(spec)}")

    # Robust section extraction strategy
    sections = None
    
    # Strategy A: Check standard direct keys first
    for key in ["sections", "profiles", "measured_sections", "cross_sections", "geometry"]:
        if key in spec and isinstance(spec[key], list) and len(spec[key]) > 0:
            sections = spec[key]
            break

    # Strategy B: Extract from 'operations' if direct keys fail
    if sections is None and "operations" in spec:
        ops = spec["operations"]
        if isinstance(ops, list):
            # Look for an operation that contains section data
            for op in ops:
                if isinstance(op, dict):
                    for k in ["sections", "profiles", "measured_sections"]:
                        if k in op and isinstance(op[k], list) and len(op[k]) > 0:
                            sections = op[k]
                            break
                if sections is not None:
                    break
        
        # If operations itself is the list of sections (flat structure)
        if sections is None and isinstance(ops, list) and len(ops) > 0:
            first = ops[0]
            if isinstance(first, dict) and ("vertices" in first or "x_coordinate" in first):
                sections = ops

    if sections is None or len(sections) == 0:
        raise ValueError(
            f"Could not locate valid sections in spec. "
            f"Available keys: {list(spec.keys())}"
        )

    # Validate section count matches plan requirement of exactly 7
    if len(sections) != 7:
        raise ValueError(f"Expected 7 sections, found {len(sections)}")

    # Extract invariants safely
    invariants = spec.get("measured_invariants", {})
    expected_vertex_count = invariants.get("profile_vertex_count", 16)

    # REPAIR: Normalize section vertex format before validation
    # The runtime builder expects 'vertices' as list of points, but spec may store 
    # them as 'points', 'coords', or separate x/y/z arrays.
    normalized_sections = []
    for i, section in enumerate(sections):
        sec_copy = dict(section)
        
        # Ensure vertices exist and are in correct format
        verts = sec_copy.get("vertices", [])
        
        # Try alternative keys if vertices is empty/missing
        if not verts:
            verts = sec_copy.get("points", [])
        if not verts:
            verts = sec_copy.get("coords", [])
            
        # Handle case where vertices might be stored as flat list or separate arrays
        if not verts and "x" in sec_copy and "y" in sec_copy and "z" in sec_copy:
            xs = sec_copy["x"] if isinstance(sec_copy["x"], list) else [sec_copy["x"]]
            ys = sec_copy["y"] if isinstance(sec_copy["y"], list) else [sec_copy["y"]]
            zs = sec_copy["z"] if isinstance(sec_copy["z"], list) else [sec_copy["z"]]
            verts = list(zip(xs, ys, zs))
            
        if len(verts) != expected_vertex_count:
            raise ValueError(
                f"Section {i} has {len(verts)} vertices, expected {expected_vertex_count}. "
                f"Available keys in section: {list(section.keys())}"
            )
            
        sec_copy["vertices"] = verts
        normalized_sections.append(sec_copy)

    # Step 2: VALIDATE_SECTION_COORDINATES
    expected_coords = invariants.get("section_coordinates", [
        0.0202645, 0.040356956666666666, 0.06044941333333334,
        0.08054187, 0.10063432666666668, 0.12072678333333335, 0.14081924
    ])

    actual_coords = [s.get("x_coordinate") for s in normalized_sections]
    tolerance = 1e-6

    for idx, (actual, expected) in enumerate(zip(actual_coords, expected_coords)):
        if actual is None:
            raise ValueError(f"Section {idx} missing x_coordinate")
        if abs(actual - expected) > tolerance:
            raise ValueError(
                f"Section {idx} X-coordinate mismatch: {actual} != {expected} "
                f"(tolerance={tolerance})"
            )

    # Step 3 & 4: BUILD_LOFT_SURFACE + APPLY_SOURCE_TRANSFORM via semantic builder
    transform_data = None
    pcs = spec.get("part_local_coordinate_system", {})
    if isinstance(pcs, dict):
        transform_data = pcs.get("local_to_global_transform", None)

    shape = build_profile_loft_part(
        sections=normalized_sections,
        max_degree=5,
        ruled=False,
        surface_continuity="GLOBAL_SURFACE",
        repair_policy="MINIMUM_PROFILE_COMPLEXITY_MEETING_SHARP_EDGE_RECALL_0.90_WITH_Q1",
        transform_source=transform_data,
        placement_policy="SOURCE_MEASURED_TRANSFORM"
    )

    # Validation checks
    validation_results = validate_shape(
        shape,
        checks=[
            "LOFT_MUST_USE_EXACTLY_7_MEASURED_SECTIONS",
            "EACH_PROFILE_MUST_HAVE_EXACTLY_16_VERTICES_AS_MEASURED",
            "SECTION_COORDINATES_MUST_MATCH_MEASURED_VALUES_WITHOUT_MODIFICATION",
            "SHARP_EDGE_RECALL_MUST_BE_GE_0.90",
            "FEATURE_BOUNDARY_RECALL_MUST_BE_GE_0.99",
            "NO_GEOMETRY_QA_FAILURES_ON_LOFTED_SURFACE"
        ],
        targets={
            "sharp_edge_recall_target": 0.9456489456489456,
            "feature_boundary_recall_target": 0.9961568024596464
        }
    )

    if not validation_results.get("passed", False):
        raise RuntimeError(
            f"Shape validation failed: {validation_results.get('failures', [])}"
        )

    # Export STEP
    export_step(shape, args.output)

    # Write provenance
    FINAL_OPS = [
        {"step": 1, "operation": "LOAD_MEASURED_PROFILES"},
        {"step": 2, "operation": "VALIDATE_SECTION_COORDINATES"},
        {"step": 3, "operation": "BUILD_LOFT_SURFACE"},
        {"step": 4, "operation": "APPLY_SOURCE_TRANSFORM"}
    ]

    write_program_provenance(
        output_path=args.output,
        part_id="CADPART_005",
        candidate_id="candidate_02",
        runtime_builder="build_profile_loft_part",
        final_ops=FINAL_OPS,
        validation_summary=validation_results
    )


if __name__ == "__main__":
    main()
