# CASE09 FutureCAD-compatible Grounded Repair V3

Gate: `CASE09_FUTURECAD_GROUNDED_REPAIR_V3_PARTIAL_PASS`

## Scientific attribution

- FutureCAD paper mechanism used: true.
- Official FutureCAD code/model used: false.
- Grounding mode: FUTURECAD_COMPATIBLE_BREP_GROUNDING_V1.
- The implementation is a compatible proxy; it is not official BRepGround and uses no pretrained BRepGround weights.

## Result

- Targets fixed: 3/3; part Q1/Q2/Q3=1/7/0.
- Whole geometry: Q1; Chamfer=0.0032745094590042375; P95=0.008997589751742745; Coverage02=1.0.
- Sharp edge recall: V2=0.9456489456 V3=0.9560439560439561.
- Feature boundary recall: V2=0.9961568025 V3=1.0.
- Grounding: queries=10, success=4, uncertain=6, executed ops=4.

## Guardrails

- Five Q2 parts retained byte-identical STEP hashes.
- No P3, PhysX, part discovery, or part graph rerun.
- No fixed face/edge index selection in selected programs.
- Uncertain grounding selections were not executed.
- Propeller preserves one master feature definition plus one pattern with source-measured instance correction.

## Artifacts

- STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_futurecad_grounded_repair_v3/06_assembly/CASE09_futurecad_grounded_repair_v3.step`
- Comparison: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_futurecad_grounded_repair_v3/artifacts/source_v2_v3_true_edges.png`
- Grounding: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_futurecad_grounded_repair_v3/artifacts/grounding_overlay.png`

## Unmet target

- Sharp-edge recall improved to 0.9560439560 but did not reach the 0.97 target. Additional tested edge-dense candidates reached 0.9735669736 only by failing the per-part Q1/Q2 hard gate, so they were correctly rejected.

## Tests

- 31 passed; 0 failed.
