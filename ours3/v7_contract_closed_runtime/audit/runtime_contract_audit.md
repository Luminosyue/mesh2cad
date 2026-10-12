# V7 Runtime Contract Audit

Audited producers/consumers: V6 prepare, V6 MAC, V6 runtime, V6 finalize, Batch9 runtime, Batch9 MAC, Batch9 finalize, candidate QA, nativeness verifier, assembly selection.

| FIELD | DECLARED_OWNER | ACTUAL_PRODUCER | ACTUAL_CONSUMER | RUNTIME_REMEASURED? | RUNTIME_OVERRIDDEN? | USED_IN_FINAL_BREP? | STATUS |
|---|---|---|---|---:|---:|---:|---|
| axis | Geometry Analyzer | V6 prepare JSON | V6/Batch9 runtime | true | true | true | OVERRIDDEN |
| span | Geometry Analyzer | V6 prepare JSON | V6/Batch9 runtime | true | false | false | BYPASSED |
| stations | Geometry Analyzer | V6 prepare JSON | V6/Batch9 runtime | true | true | true | OVERRIDDEN |
| profiles | Geometry Analyzer | V6 prepare JSON | V6/Batch9 runtime | true | false | true | BYPASSED |
| sections | Geometry Analyzer | V6 prepare JSON | V6/Batch9 runtime | true | true | true | OVERRIDDEN |
| profile_count | Design Intent / MAC | V6 prepare JSON | V6/Batch9 runtime | false | true | true | OVERRIDDEN |
| representation | Design Intent / MAC | V6 prepare JSON | V6/Batch9 runtime | false | true | true | BYPASSED |
| feature_boundary_recall | QA/Selection | V6/Batch9 finalize | ranking/registry | false | true | false | FAKE_METRIC |
| semantic_feature_q | QA/Selection | V6/Batch9 finalize | ranking/registry | false | false | false | FAKE_METRIC |
| cad_structure_q | QA/Selection | V6/Batch9 finalize | ranking/registry | false | true | false | FAKE_METRIC |
| selected_best | QA/Selection | V6/Batch9 finalize | ranking/registry | false | false | false | HISTORICAL_REUSE |
| historical_step | QA/Selection | V6/Batch9 finalize | ranking/registry | false | false | false | HISTORICAL_REUSE |

## Confirmed V6/Batch9 violations

- V6 runtime contains the CASE09 `stable` table and part-specific dispatch.
- Batch9 runtime derives axis with `argmax(mesh.extents)` and silently clamps sections/profile_count to 8..20.
- Batch9 maps REVOLUTION to extrusion.
- Multiple hypothesis labels collapse to semantic_skin.
- Finalizers rewrite a raw feature recall to 1.0 after a geometry gate.
- SECTION_DERIVED_EDGES is constant zero, not a BRep measurement.
- Batch9 SELECTED_BEST may retain a historical STEP.

## V7 closure

- Runtime consumes measured spec and construction plan only.
- Failed profiles remain PROFILE_INVALID; no bbox/hull substitute is emitted by Geometry Analyzer.
- Each candidate has candidate_execution_contract.json and geometry_trace.json.
- Raw topology metrics are measured from BRep edges and written separately.
- Semantic surfaces and feature graphs are explicitly HYPOTHESIS_ONLY.
- No new model or new MAC calls were added; the existing design hypotheses were normalized into explicit construction plans.

## Batch9 status
- Existing real MAC attempts: 119/119; valid: 115.
- FULLSTACK_MAC_VALID=false.
- Batch9 was not rerun in V7.

## Final audit answers

1. `measured_cad_spec.json` controls the fresh V7 STEP: yes; span, axis, and station perturbations all changed the BRep.
2. Runtime remeasured fields: none. It does not read mesh geometry, choose an axis, or regenerate stations.
3. Geometry Analyzer profiles are real `mesh.section()` closed loops: yes. Invalid stations remain `PROFILE_INVALID`; minimum closed rate is 1/6.
4. Requested construction parameters are fully executed: yes for V7; requested and executed profile counts match with zero clamps/overrides.
5. Different hypotheses use distinct builders: yes; LOFT, RULED, and BSPLINE_SKIN produced distinct builders and BRep signatures.
6. Candidate geometry collapse remains: no in the tested CASE09 counterfactuals.
7. Raw metric rewrites remain: none in V7. The 0.32 integrity fixture remains 0.32 after finalize.
8. CASE09 Q1 attribution: V7 makes no new Q1 claim. This gate validates contract execution, not whole-aircraft quality.
9. Batch9 real MAC status: 119 attempts and 115 STEP successes, but only 41/132 parts received candidate coverage and 2/9 fresh assemblies were written; full-stack evaluation is invalid.
10. Enter the next research stage now: no. First improve real closed-profile coverage and complete fresh contract execution for every required part.
