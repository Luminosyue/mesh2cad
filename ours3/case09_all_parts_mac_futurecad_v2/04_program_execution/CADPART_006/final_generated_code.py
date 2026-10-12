import argparse
from case09_v2_runtime import (
    load_measured_spec,
    build_patterned_blade_part,
    validate_shape,
    export_step,
    write_program_provenance
)

CANDIDATE_ID = 'candidate_01'

FINAL_OPS = [
    {
        "step": 1,
        "op": "DEFINE_PROFILE_CURVES",
        "target_instance": 0,
        "params": {
            "axis": "Y",
            "section_count": 7,
            "vertex_count_per_section": 16,
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


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_006 Candidate 01")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # Load measured specification at runtime
    spec = load_measured_spec(args.spec)

    # Explicitly call the semantic builder with the complete spec object as first positional arg
    shape = build_patterned_blade_part(
        spec,
        operations=FINAL_OPS,
        candidate_id=CANDIDATE_ID
    )

    # Validate the generated shape against semantic and geometric constraints
    validate_shape(shape, spec)

    # Export to STEP format
    export_step(shape, args.output)

    # Write provenance metadata
    write_program_provenance(
        output_path=args.output,
        candidate_id=CANDIDATE_ID,
        part_id="CADPART_006",
        runtime_builder="build_patterned_blade_part",
        operations=FINAL_OPS,
        spec_source=args.spec
    )


if __name__ == "__main__":
    main()
