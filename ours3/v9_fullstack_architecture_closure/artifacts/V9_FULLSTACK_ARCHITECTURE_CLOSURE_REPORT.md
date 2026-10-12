# V9 Fullstack Architecture Closure — Evidence Audit

## Outcome

`CURRENT_GATE=V9_FULLSTACK_ARCHITECTURE_CLOSURE_PARTIAL`

CASE09 did **not** reach a fresh complete XCAF assembly. The internal pipeline has multiple blockers in addition to the external MAC quota: per-surface primitive selection was not executed; fuselage and vertical-tail shared topology is absent; full-part routing/reconstruction was not executed; Qwen produced no executable construction plan; and optimization/grounding coverage is incomplete. Therefore the external-resource exception status is not applicable.

The V9I gate was stopped rather than substituting the old CASE09 hard-coded `PART_SPECS` path, a historical STEP, convex-hull/bbox fallback, or a main-wing-only STEP.

## Evidence summary

- Eight primitive fitter implementations generate executable OCC geometry and expose geometry parameters, support/domain and residual evidence. Radius/profile-scale perturbations change freshly written fitter STEP files. The CASE09 per-semantic-surface candidate selector was not run, so Step 5 remains PARTIAL.
- Automatic geometry/contact grouping covers all 10 P3 segments and emits 8 groups without old `PART_SPECS` or GT semantic labels. Hierarchy remains PARTIAL.
- Main wing has shared OCC topology. Fuselage and vertical tail each have real BSpline FACE_SET output and real CAD boundary curves, but their independently fitted tracks do not provide a common boundary control net; they do not have shared-edge topology.
- Three evidence-backed feature instances and three provenance-linked measured specs were produced for the core parts. This is 3/8 inferred-part coverage, not full CASE09 coverage.
- Local Qwen3-VL received the requested OBJ/pixel/spec ablation inputs. Its full multimodal request failed HTTP 500 and the other responses did not yield an executable permitted builder; `QWEN_PLAN_EXECUTED=false`.
- One real Multi-Agent-CAD provider request was sent. DashScope returned HTTP 403 `AllocationQuota.FreeTierOnly`; no repair patch, post-QA, or acceptance/rollback occurred.
- No hidden fallback was executed. No historical STEP was used as a final V9 part. There is no final V9 STEP.

## Gate metrics

```text
REAL_SURFACE_FITTER_COUNT=8
SEMANTIC_SURFACE_COUNT=10
REAL_DESIGN_EDGE_COUNT=40
SHARED_OCC_EDGE_COUNT=12
PCURVE_EDGE_COUNT=40
TRIMMED_FACE_COUNT=10
FEATURE_INSTANCE_COUNT=3
PARAMETERS_OPTIMIZED=2
GROUNDING_FACE_SUCCESS_COUNT=2
GROUNDING_EDGE_SUCCESS_COUNT=2
REAL_MAC_CALLS=1
TARGETED_REPAIR_ATTEMPTS=0
P3_SEGMENT_COUNT=10
FINAL_CAD_PART_COUNT=8
FULL_CASE09_ASSEMBLY=false
```

`FINAL_CAD_PART_COUNT=8` is the automatic part-graph group count, not the count of successfully reconstructed V9 CAD BReps.

## Required 20 answers

1. **Are all eight Step 5 fitters real implementations?** Yes as fitter capabilities: all eight construct executable OCC geometry with real parameters. No for the full Step 5 gate: the required per-semantic-surface candidate comparison/selection was not executed.
2. **Did fuselage traverse primitive → wireframe → shared edge → pcurve → trimmed Face?** No. It reached real GENERAL_BSPLINE faces and a real boundary wireframe, but not shared edges between its faces; the result remains an independent `FACE_SET`.
3. **Did vertical tail traverse the freeform topology path?** Partially. Real B-spline faces and boundary curves exist, but shared-edge/pairwise pcurve topology was not established; it remains `FACE_SET`.
4. **Are profile-sampling edges mixed into Step 6 design edges?** No. `PROFILE_SAMPLE_DESIGN_EDGE_COUNT=0` and `MESH_TRIANGLE_EDGE_IMPORT_COUNT=0`.
5. **Does Step 7 share real TopoDS_Edge instances?** Yes for main wing (12 shared OCC edges); no for fuselage and vertical tail.
6. **Do pcurves exist on both adjacent faces?** Yes for the main-wing shared topology. This is not proven for fuselage/tail because they lack paired shared edges.
7. **Does Step 8 contain real feature instances rather than aliases?** Yes for the three core-part records: one LOFT and two FREEFORM instances with support/affected faces, parameters, constraints, confidence and detection evidence. Full CASE09 coverage was not produced.
8. **Does Step 9 aggregate primitive, wireframe and feature parameters?** Yes for three core parts, with `SOURCE_MODULE` and `SOURCE_ENTITY_ID`. It is not complete for all 8 inferred parts.
9. **Did Qwen3-VL use OBJ + pixels + measured spec?** These inputs were genuinely sent across the ablation modes, including the full multimodal request. The full request returned HTTP 500 and no executable Qwen plan was produced.
10. **Are Qwen3-VL and MAC roles distinguished?** Yes. Qwen3-VL is the local design-intent experiment; MAC is the external multi-agent repair provider. Neither is counted as the other.
11. **Did Step 13 optimize every applicable core part?** No. Only main wing has executed optimizer evidence (2 parameters); fuselage and vertical tail were not optimized. V9F read the existing V8 optimizer artifact rather than freshly applying it to all core parts.
12. **Does Step 17 use orientation, adjacency and feature membership?** Yes. The V2 descriptor/scorer includes all three, supports RESOLVED/AMBIGUOUS/UNRESOLVED, and is not nearest-only. Runtime evidence is main-wing-only.
13. **Did Step 18 complete residual → grounding → local patch → execute → QA → decision?** No. It reached residual/grounding and sent one real provider request; HTTP 403 prevented a patch, execution, QA and accept/rollback.
14. **Does a hidden fallback remain?** No hidden fallback was executed in V9 (`FALLBACK_COUNT=0`). Missing stages remain explicit blockers instead of invoking fallback geometry.
15. **Was a historical STEP reused?** No historical STEP was used as a final V9 part (`HISTORICAL_STEP_REUSED=false`). Separately, V9F reads historical V8 optimization evidence, which is why Step 13 is not credited as fresh full-coverage V9 execution.
16. **Are all final CASE09 parts fresh?** No. No final full set of V9 parts exists, so `ALL_FINAL_PARTS_FRESH=false`.
17. **Was a complete XCAF assembly written?** No. Neither a complete assembly nor a main-wing subset was labeled as V9I success; `FINAL_STEP=NONE`.
18. **Which requested steps can change from partial to full?** None at full CASE09 coverage. V9D and V9G independently pass their scoped module gates, and the eight fitter capabilities are real, but Steps 5/8/9/17 remain PARTIAL under the full-case contract.
19. **Which step is externally resource-blocked?** Step 18/V9H: the real MAC request returned provider HTTP 403 due exhausted free-tier quota. This is not the only V9 blocker.
20. **Can the pipeline expand to Batch9 now?** No. CASE09 has not closed the full loop, so Batch9 expansion is not recommended.

## Regression

Fresh test invocation: 99 passed, 0 failed (V7 Contract 35, V7A 16, V7B 23, V9 5, PhysX V2.1 20). No V7C or V8 pytest suite exists. V8's existing immutable audit reports 45/45 checks passed. PhysX V2.2 was not available, so V2.1 was run. An initial combined invocation had a V7B import-root collection error; rerunning every suite from its required working directory passed.

## Artifacts

- `/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure/artifacts/v9_architecture_status.csv`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure/artifacts/e2e_dependency_matrix.csv`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure/artifacts/v9_actual_runtime_pipeline.txt`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure/artifacts/final_summary.json`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure/artifacts/test_results.json`
