# CASE09_AIRCRAFT_END2END_CAD_V1

Gate candidate: `PASS`

## Result

The source-only rebuild produced 8 semantic CAD parts and a fresh-reload-valid Q1 BRep. CAD structure is PASS.

## Source and provenance

- Source OBJ: `/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj`
- Source SHA256: `ec3b6fb83ce405bd4c6cd41bb506ef9e5a8995919fb32ab9c40411f400e823cd`
- Old STEP geometry was not read by reconstruction; it was opened only after the new assembly was complete for final comparison.

## MAC provenance

- MAC used: True; parts: ['CADPART_000']; runs: 1; LLM calls: 4
- Provider: DASHSCOPE_CN_OPENAI_COMPATIBLE; token usage: {'prompt_tokens': 12743, 'completion_tokens': 9056, 'total_tokens': 21799}
- MAC received only the measured feature graph and measured CAD spec; raw OBJ and old STEP were excluded.

## Part discovery

- Real P3 segments: 10
- Fused CAD parts: 8
- Labels: FUSELAGE, MAIN_WING_LEFT, MAIN_WING_RIGHT, HORIZONTAL_TAIL_LEFT, HORIZONTAL_TAIL_RIGHT, VERTICAL_TAIL, PROPELLER_PATTERN, DORSAL_FEATURES
- Unassigned area ratio: 0.0

## Geometry and structure

- Geometry: Q1; Chamfer=0.005624; P95=0.014706; Coverage02=0.994700
- BRep: valid=True; faces=92; edges=216
- Strip edges: old compact=64; new=8; reduction=0.875
- Feature-boundary recall: 0.9830899308224442; sharp-edge recall: 0.8381348381348381

## Limitations

- PhysX is a soft semantic prior only; it never changes measured dimensions or placement.
- The fuselage uses one global loft feature; wings and tail elements use bounded profile extrusions.
- No design-history recovery claim is made beyond the saved measured feature graph and program provenance.

## Review artifacts

- CAD Part Graph: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/02_cad_part_graph/cad_part_graph.png`
- Feature Graphs: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/04_feature_graph`
- True-edge view: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/artifacts/new_true_edges.png`
- Comparison: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/artifacts/source_vs_old_vs_new.png`
- Final STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/07_assembly/CASE09_aircraft_final.step`

## Independent regression tests

- Result: `28 passed, 0 failed`
- Command: `/data/miniconda3/envs/multi_agent_cad/bin/python -m pytest -q tests/test_case09_end2end.py`
- Gate: `CASE09_AIRCRAFT_END2END_CAD_V1_PASS`
