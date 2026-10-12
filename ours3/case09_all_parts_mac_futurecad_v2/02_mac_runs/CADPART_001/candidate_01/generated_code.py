import argparse
import sys

# Import required utilities from the canonical runtime module
from case09_v2_runtime import (
    build_profile_loft_part,
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_001 Candidate 01")
    parser.add_argument("--spec", required=True, help="Path to measured CAD spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # 1. Load Measured Spec at Runtime
    measured_cad_spec = load_measured_spec(args.spec)

    # 2. Extract Grounding Data from Spec safely
    # Fix: The builder expects 'profiles' not 'sections' based on the TypeError
    operations = measured_cad_spec.get("operations", [])
    profile_data = []
    if operations and isinstance(operations, list) and len(operations) > 0:
        # Try 'profiles' first as indicated by error, fallback to 'sections' for safety
        profile_data = operations[0].get("profiles", operations[0].get("sections", []))

    # Safely extract transform matrix
    geom_constraints = measured_cad_spec.get("geometry_constraints", {})
    local_cs = geom_constraints.get("part_local_coordinate_system", {})
    transform_matrix = local_cs.get("local_to_global_transform", None)

    # Safely extract bbox for validation context
    target_bbox = geom_constraints.get("bbox", None)

    # 3. Define Final Operations Plan
    FINAL_OPS = [
        {
            "step": 1,
            "action": "LOAD_PROFILE_SERIES",
            "source": "measured_cad_spec.operations[0].profiles",
            "parameters": {"axis": "X", "section_count": 20, "vertex_count_per_section": 12}
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
                "output_topology": "SINGLE_CONTINUOUS_SURFACE"
            }
        },
        {
            "step": 3,
            "action": "APPLY_PLACEMENT",
            "policy": "SOURCE_MEASURED_TRANSFORM",
            "transform_source": "geometry_constraints.part_local_coordinate_system.local_to_global_transform"
        }
    ]

    # 4. Execute Semantic Builder Explicitly
    # Repair: Changed keyword argument from 'sections' to 'profiles'
    shape = build_profile_loft_part(
        profiles=profile_data,
        transform=transform_matrix,
        max_degree=5,
        ruled=False,
        continuity="G1_MINIMUM",
        output_topology="SINGLE_CONTINUOUS_SURFACE"
    )

    # 5. Validate Shape against Plan Requirements
    validation_rules = [
        "VERIFY_SINGLE_GLOBAL_LOFT_FEATURE_EXISTS",
        "VERIFY_SECTION_COUNT_EQUALS_20",
        "VERIFY_PROFILE_VERTEX_COUNT_EQUALS_12_PER_SECTION",
        "VERIFY_NO_STRIP_FACE_TOPOLOGY",
        "VERIFY_BBOX_WITHIN_MEASURED_TOLERANCE",
        "VERIFY_SHARP_EDGE_RECALL_GE_0.90",
        "VERIFY_FEATURE_BOUNDARY_RECALL_GE_0.99"
    ]

    is_valid, report = validate_shape(
        shape=shape,
        rules=validation_rules,
        reference_spec=measured_cad_spec
    )

    if not is_valid:
        print(f"Validation Failed for Candidate 01: {report}", file=sys.stderr)
        sys.exit(1)

    # 6. Export STEP
    export_step(shape, args.output)

    # 7. Write Provenance
    CANDIDATE_ID = "candidate_01"
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_001",
        operations=FINAL_OPS,
        builder="build_profile_loft_part",
        spec_source=args.spec,
        validation_report=report
    )

    print(f"Successfully generated {CANDIDATE_ID} for CADPART_001 at {args.output}")


if __name__ == "__main__":
    main()
