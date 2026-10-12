import argparse
import sys

from case09_v2_runtime import (
    build_patterned_blade_part,
    load_measured_spec,
    validate_shape,
    export_step,
    write_program_provenance
)


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_006 Candidate 0")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load the complete measured specification object at runtime
    measured_spec = load_measured_spec(args.spec)

    # Define final operations exactly as per ARCHITECT_PLAN
    FINAL_OPS = [
        {
            "step": 1,
            "op": "DEFINE_PROFILE_CURVES",
            "target_instance": 0,
            "params": {
                "axis": "Y",
                "section_count": 7,
                "vertex_count_per_section": 16,
                "coordinates": [-0.94818646, -0.9332669, -0.91834734, -0.90342778, -0.88850822, -0.87358866, -0.8586691],
                "source_data_key": "measured_cad_spec.operations[0].sections"
            }
        },
        {
            "step": 2,
            "op": "LOFT_BLADE",
            "target_instance": 0,
            "params": {
                "input_profiles_step": 1,
                "ruled": False,
                "max_degree": 5,
                "semantic_role": "BLADE_INSTANCE"
            }
        },
        {
            "step": 3,
            "op": "DEFINE_PROFILE_CURVES",
            "target_instance": 1,
            "params": {
                "axis": "Y",
                "section_count": 7,
                "vertex_count_per_section": 16,
                "coordinates": [-0.96255791, -0.94626848, -0.92997904, -0.91368961, -0.89740018, -0.88111074, -0.86482131],
                "source_data_key": "measured_cad_spec.operations[1].sections"
            }
        },
        {
            "step": 4,
            "op": "LOFT_BLADE",
            "target_instance": 1,
            "params": {
                "input_profiles_step": 3,
                "ruled": False,
                "max_degree": 5,
                "semantic_role": "BLADE_INSTANCE"
            }
        },
        {
            "step": 5,
            "op": "APPLY_MEASURED_PATTERN",
            "params": {
                "pattern_type": "MEASURED_INSTANCE_PATTERN",
                "instance_count": 2,
                "source_instances": [2, 4],
                "forced_symmetry": False,
                "hub_generation": False
            }
        }
    ]

    CANDIDATE_ID = "candidate_00"

    # Explicitly call the semantic builder passing the full spec object as first positional arg
    shape = build_patterned_blade_part(
        measured_spec,
        operations=FINAL_OPS,
        candidate_id=CANDIDATE_ID
    )

    # Validate resulting shape against expected semantics
    validation_report = validate_shape(
        shape=shape,
        expected_operations=FINAL_OPS,
        part_id="CADPART_006"
    )

    if not validation_report.get("valid", False):
        print(f"Validation failed for {CANDIDATE_ID}: {validation_report}", file=sys.stderr)
        sys.exit(1)

    # Export valid geometry to STEP
    export_step(shape, args.output)

    # Write provenance linking candidate, plan, and output
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_006",
        builder="build_patterned_blade_part",
        operations=FINAL_OPS,
        validation=validation_report
    )


if __name__ == "__main__":
    main()
