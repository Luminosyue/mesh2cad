# V6 Pipeline Reconstruction

## Evidence-based paths

### PATH A: exact geometry analysis

`source_part.obj -> v6_prepare Geometry Analyzer -> measured_cad_spec.json`

This path wrote bbox/profile summaries, but those measurements did not remain authoritative at runtime.

### PATH B: dual-modal construction hypothesis

`proxy OBJ tokens + axonometric render -> Qwen3-VL visual context -> Qwen text planner -> generated_code.py`

This path is real. The prompt, raw responses, token usage, generated wrappers, and executed candidate STEP files are retained under `case09_fullstack_mesh2cad_mac_v6/06_dual_modal_adapter` and `08_multi_candidate_mac`.

### PATH C: mesh-guided fitting (actual geometry producer)

`generated_code.py -> v6_runtime.py --source-mesh -> trimesh.section / exact_profiles -> OCC Loft or BSpline -> STEP`

This is the actual high-fidelity geometry path. The generated program is a wrapper around the controlled runtime, not a direct CadQuery/OCC program. `v6_runtime.py` rereads the high-poly part mesh, regenerates stations/profiles, aligns seams, and fits the BRep.

## Classification

- `V6_MESH2CAD_STYLE_PATH_FOUND=true`: functionally equivalent dual-modal context selected an executable CAD construction wrapper.
- `V6_DIRECT_VLM_CADQUERY_PATH_FOUND=false`: V6 explicitly forbade CadQuery/OCP imports and required a runtime wrapper.
- `V6_MESH_GUIDED_FITTING_PATH_FOUND=true`: confirmed by code and V7 runtime-contract audit.

## Removal root cause

V7 intentionally removed runtime source-mesh remeasurement and made Measured CAD Spec authoritative. V10 then gated every builder and blocked direct OCC bypasses. V11 required Structured CAD Plans with exact refs. No adapter migrated V6 dual-modal construction proposals into that schema, so the candidate source disappeared while the unsafe geometry side path was correctly removed.

`REMOVED_AFTER_VERSION=V7_CONTRACT_CLOSED_RUNTIME`

`V6_PATH_REMOVAL_ROOT_CAUSE=MULTIPLE(SAFETY_GATE_MIGRATION,NO_V11_ADAPTER)`

## Fidelity diagnosis

V6 looked better because the runtime performed dense source-mesh profile extraction, stable seam alignment, adaptive sampling, and candidate selection. The dual-modal model helped choose a construction hypothesis, but did not directly author the final geometry. V12R independently reached the same diagnosis: `PROFILE_EXTRACTION|ADAPTIVE_SAMPLING|CANDIDATE_SELECTION`.
