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
        "op": "LOAD_MEASURED_PROFILES",
        "source_key": "measured_cad_spec.operations.PROFILE_LOFT.sections",
        "constraints": {
            "section_count": 10,
            "vertex_count_per_section": 12,
            "axis": "X",
        },
    },
    {
        "op": "BUILD_LOFT_SURFACE",
        "input_ref": "LOAD_MEASURED_PROFILES",
        "parameters": {
            "loft_type": "NORMAL",
            "closed": False,
            "preserve_coordinates": True,
        },
    },
    {
        "op": "APPLY_SOURCE_TRANSFORM",
        "transform_matrix": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        "policy": "IDENTITY_PRESERVATION",
    },
]


def _resolve_sections(spec):
    """Safely extract sections from measured spec handling list or dict formats."""
    ops = spec.get("operations", spec)
    if isinstance(ops, list):
        for entry in ops:
            if isinstance(entry, dict) and entry.get("type") == "PROFILE_LOFT":
                return entry.get("sections", [])
        # Fallback: assume first list item contains sections if type key missing
        if ops and isinstance(ops[0], dict):
            return ops[0].get("sections", [])
        return []
    if isinstance(ops, dict):
        loft_data = ops.get("PROFILE_LOFT", {})
        if isinstance(loft_data, dict):
            return loft_data.get("sections", [])
        return []
    return []


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_002 candidate 02")
    parser.add_argument("--spec", required=True, help="Path to measured spec JSON")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    measured_spec = load_measured_spec(args.spec)

    # Extract sections according to plan constraints with safe access
    sections_data = _resolve_sections(measured_spec)

    # Explicitly call the required semantic builder using correct signature
    # Repair: Removed invalid 'loft_type' keyword argument causing TypeError
    shape = build_profile_loft_part(
        sections_data,
        closed=False,
        preserve_coordinates=True,
        transform_matrix=[
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
    )

    # Validate shape against plan requirements
    validation_config = {
        "section_count": 10,
        "vertex_count_per_section": 12,
        "bounding_box_min": [0.02840433, -0.63370264, -0.0283466],
        "bounding_box_max": [0.98673195, -0.03653008, 0.16582209],
        "bbox_tolerance": 1e-06,
        "sharp_edge_recall_threshold": 0.9456489456489456,
        "feature_boundary_recall_threshold": 0.9961568024596464,
        "symmetry_check_method": "GEOMETRIC_COMPARISON_AGAINST_LEFT_WING",
        "symmetry_expected_result": "MISMATCH_CONFIRMED",
    }
    validate_shape(shape, validation_config)

    # Export validated shape to STEP
    export_step(shape, args.output)

    # Write program provenance
    provenance = {
        "part_id": "CADPART_002",
        "candidate_id": CANDIDATE_ID,
        "runtime_builder": "build_profile_loft_part",
        "final_ops": FINAL_OPS,
        "spec_source": args.spec,
        "output_file": args.output,
        "hypothesis": "H1_MEASURED_PROFILE_LOFT",
        "asymmetry_handling": "PRESERVE_MEASURED_RIGHT_SIDE_DIFFERENCES",
    }
    write_program_provenance(provenance)


if __name__ == "__main__":
    main()
