import argparse
import json
import sys
import os

# Import semantic builder from the required runtime module
from case09_v2_runtime import build_profile_loft_part

# Corrected imports based on ImportError: load_measured_spec is not in multi_agent_cad
# Assuming standard utility location or fallback to json loading if specific util missing
try:
    from multi_agent_cad.utils import load_measured_spec
except ImportError:
    try:
        from multi_agent_cad.io import load_measured_spec
    except ImportError:
        # Fallback implementation if library structure changed/broken in this env
        def load_measured_spec(path):
            with open(path, 'r') as f:
                return json.load(f)

from multi_agent_cad import validate_shape, export_step, write_program_provenance


def main():
    parser = argparse.ArgumentParser(description="Generate CADPART_004 Candidate 0")
    parser.add_argument("--spec", required=True, help="Path to measured JSON spec")
    parser.add_argument("--output", required=True, help="Output STEP file path")
    args = parser.parse_args()

    # 1. Load Measured Spec at Runtime
    spec = load_measured_spec(args.spec)
    
    # Extract parameters strictly from spec according to ARCHITECT_PLAN
    if "operations" not in spec or len(spec["operations"]) == 0:
        raise ValueError("Spec missing 'operations' list or it is empty")
        
    sections = spec["operations"][0].get("sections", [])
    
    # Validate input data against plan constraints before building
    expected_section_count = 10
    expected_vertex_count = 12
    
    if len(sections) != expected_section_count:
        raise ValueError(f"SECTION_COUNT_VALIDATION failed: Expected {expected_section_count}, got {len(sections)}")
        
    for i, section in enumerate(sections):
        if len(section.get("vertices", [])) != expected_vertex_count:
            raise ValueError(f"VERTEX_COUNT_VALIDATION failed for section {i}: Expected {expected_vertex_count} vertices")

    # 2. Define Final Operations based on Plan
    FINAL_OPS = [
        {
            "action": "LOAD_MEASURED_PROFILES",
            "parameters": {
                "source_key": "measured_cad_spec.operations[0].sections",
                "expected_count": 10,
                "vertex_count_per_profile": 12,
                "axis": "X"
            }
        },
        {
            "action": "CONSTRUCT_CLOSED_WIRES",
            "parameters": {
                "profile_type": "AIRFOIL_CLOSED_LOOP",
                "continuity": "G2_TANGENT_CONTINUOUS_BETWEEN_SECTIONS",
                "parameterization": "CHORD_LENGTH_PROPORTIONAL"
            }
        },
        {
            "action": "EXECUTE_LOFT",
            "parameters": {
                "max_degree": 5,
                "ruled": False,
                "solid": True,
                "loft_axis": "X"
            }
        },
        {
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

    # 3. Call Semantic Builder Explicitly
    loft_config = {
        "sections": sections,
        "feature_semantics": spec.get("feature_semantics", {}),
        "placement_policy": "SOURCE_MEASURED_TRANSFORM",
        "validation_criteria": spec.get("validation_steps", [])
    }
    
    shape = build_profile_loft_part(loft_config)

    # 4. Validate Shape
    target_bbox_min = [0.08538278, 0.37045926, -0.14880942]
    target_bbox_max = [0.54961485, 0.75112563, -0.04094299]
    
    validation_result = validate_shape(
        shape, 
        checks=[
            "TOPOLOGY_INTEGRITY", 
            "BOUNDING_BOX_CONFORMANCE", 
            "SHARP_EDGE_RECALL"
        ],
        target_bbox=(target_bbox_min, target_bbox_max),
        tolerance=1e-4
    )
    
    if not validation_result.is_valid:
        raise RuntimeError(f"Validation failed: {validation_result.errors}")

    # 5. Export STEP
    export_step(shape, args.output)

    # 6. Write Provenance
    CANDIDATE_ID = 'candidate_00'
    provenance_data = {
        "part_id": "CADPART_004",
        "candidate_id": CANDIDATE_ID,
        "runtime_builder": "build_profile_loft_part",
        "hypothesis_id": "H1_LOFT",
        "final_ops": FINAL_OPS,
        "validation_status": "PASSED",
        "source_spec_path": args.spec
    }
    
    output_dir = os.path.dirname(os.path.abspath(args.output))
    write_program_provenance(provenance_data, output_dir=output_dir)


if __name__ == "__main__":
    main()
