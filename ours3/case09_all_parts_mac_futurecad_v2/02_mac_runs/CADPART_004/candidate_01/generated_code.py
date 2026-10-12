import argparse
import sys

# Required imports from Multi-Agent-CAD runtime environment
from case09_v2_runtime import (
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance,
    build_profile_loft_part
)

CANDIDATE_ID = 'candidate_01'

# Final operations derived strictly from ARCHITECT_PLAN operation_sequence
FINAL_OPS = [
    {
        "step": 1,
        "action": "LOAD_MEASURED_PROFILES",
        "parameters": {
            "source_key": "measured_cad_spec.operations[0].sections",
            "expected_count": 10,
            "vertex_count_per_profile": 12,
            "axis": "X"
        }
    },
    {
        "step": 2,
        "action": "CONSTRUCT_CLOSED_WIRES",
        "parameters": {
            "profile_type": "AIRFOIL_CLOSED_LOOP",
            "continuity": "G2_TANGENT_CONTINUOUS_BETWEEN_SECTIONS",
            "parameterization": "CHORD_LENGTH_PROPORTIONAL"
        }
    },
    {
        "step": 3,
        "action": "EXECUTE_LOFT",
        "parameters": {
            "max_degree": 5,
            "ruled": False,
            "solid": True,
            "loft_axis": "X"
        }
    },
    {
        "step": 4,
        "action": "APPLY_SOURCE_TRANSFORM",
        "parameters": {
            "transform_matrix": [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        }
    }
]


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_004 Candidate 01")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Step 1: Load measured specification at runtime
    # The runtime builder requires the complete spec object, not just extracted sections
    measured_spec = load_measured_spec(args.spec)

    # Explicit semantic builder call passing the COMPLETE measured spec object
    # as required by _coerce_spec in case09_v2_runtime
    shape = build_profile_loft_part(
        spec=measured_spec,
        profile_type="AIRFOIL_CLOSED_LOOP",
        continuity="G2_TANGENT_CONTINUOUS_BETWEEN_SECTIONS",
        parameterization="CHORD_LENGTH_PROPORTIONAL",
        max_degree=5,
        ruled=False,
        solid=True,
        loft_axis="X",
        transform_matrix=[
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
    )

    # Validation against all plan-specified criteria
    validation_config = {
        "section_count": 10,
        "vertex_count_per_profile": 12,
        "coordinate_precision_tol": 1e-6,
        "bbox_min": [0.08538278, 0.37045926, -0.14880942],
        "bbox_max": [0.54961485, 0.75112563, -0.04094299],
        "bbox_tolerance": 1e-4,
        "sharp_edge_recall_threshold": 0.9,
        "check_topology_integrity": True,
        "check_planarity_alignment": True,
        "loft_axis": "X"
    }

    is_valid, report = validate_shape(shape, validation_config)
    if not is_valid:
        raise RuntimeError(f"Validation failed for {CANDIDATE_ID}: {report}")

    # Export validated geometry
    export_step(shape, args.output)

    # Write provenance linking candidate, plan, and operations
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_004",
        runtime_builder="build_profile_loft_part",
        final_ops=FINAL_OPS,
        spec_source=args.spec,
        validation_report=report
    )


if __name__ == "__main__":
    main()
