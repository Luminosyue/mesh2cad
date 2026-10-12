import argparse
import json
import sys

from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_global_loft_part
)


CANDIDATE_ID = "candidate_01"

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
    parser = argparse.ArgumentParser(description="Generate CADPART_000 Candidate 01")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_spec = load_measured_spec(args.spec)

    # Explicitly call the required semantic builder with corrected signature
    # Removed 'axis' keyword argument as it caused TypeError; 
    # axis orientation is derived internally from the loaded spec.
    shape = build_global_loft_part(
        spec=measured_spec,
        max_degree=5,
        ruled=False,
        surface_continuity="C2",
        parameterization="CENTRIPETAL",
        apply_source_transform=True
    )

    # Validate shape against expected constraints
    validation_config = {
        "checks": [
            {"check_id": "V1_SECTION_COUNT", "expected_value": 14, "tolerance": 0},
            {"check_id": "V2_VERTEX_PRESERVATION", "tolerance": 1e-09},
            {"check_id": "V3_DEGREE_LIMIT", "max_allowed": 5},
            {"check_id": "V4_NON_RULED_CHECK", "expected": False},
            {
                "check_id": "V5_BBOX_CONFORMANCE",
                "expected_min": [-0.12910143, -1.0, -0.19125488],
                "expected_max": [0.13422152, 0.76752925, 0.16985282],
                "tolerance": 1e-06
            },
            {"check_id": "V6_SHARP_EDGE_RECALL", "min_threshold": 0.9456489456489456},
            {"check_id": "V7_FEATURE_BOUNDARY_RECALL", "min_threshold": 0.9961568024596464},
            {"check_id": "V8_NO_TRANSVERSE_STRIPS", "expected_count": 0}
        ],
        "fail_action_map": {
            "V1_SECTION_COUNT": "ABORT_BUILD",
            "V2_VERTEX_PRESERVATION": "ABORT_BUILD",
            "V3_DEGREE_LIMIT": "REBUILD_WITH_LOWER_DEGREE",
            "V4_NON_RULED_CHECK": "ABORT_BUILD",
            "V5_BBOX_CONFORMANCE": "ABORT_BUILD",
            "V6_SHARP_EDGE_RECALL": "FLAG_FOR_REPAIR",
            "V7_FEATURE_BOUNDARY_RECALL": "FLAG_FOR_REPAIR",
            "V8_NO_TRANSVERSE_STRIPS": "ABORT_BUILD"
        }
    }

    is_valid, report = validate_shape(shape, measured_spec, validation_config)
    if not is_valid:
        raise RuntimeError(f"Validation failed for candidate {CANDIDATE_ID}: {report}")

    # Export valid shape to STEP
    export_step(shape, args.output)

    # Write provenance record
    provenance = {
        "candidate_id": CANDIDATE_ID,
        "part_id": "CADPART_000",
        "runtime_builder": "build_global_loft_part",
        "final_ops": FINAL_OPS,
        "validation_report": report,
        "spec_source": args.spec,
        "output_file": args.output
    }
    write_program_provenance(provenance)


if __name__ == "__main__":
    main()
