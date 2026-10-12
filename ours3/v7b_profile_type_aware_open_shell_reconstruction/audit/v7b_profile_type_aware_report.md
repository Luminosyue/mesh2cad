# V7B Profile-Type-Aware Open-Shell Reconstruction

`CURRENT_GATE=V7B_PROFILE_TYPE_AWARE_OPEN_SHELL_RECONSTRUCTION_PASS`

## Routing and reconstruction

| Part | Closed rate | Open rate | Route | Builder | Result | Faces | Edges | Chamfer | Hausdorff | Artificial edge ratio | OCC valid |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---|
| MAIN_WING | 0.9167 | 0.0833 | CLOSED_PROFILE_BRANCH | LoftBuilder | SOLID | 3 | 6 | 0.004171 | 0.095502 | 0.000000 | True |
| FUSELAGE | 0.2500 | 0.7500 | OPEN_SHELL_BRANCH | OpenShellSkinBuilder | FACE_SET | 2 | 8 | 0.012144 | 0.196382 | 0.000000 | True |
| VERTICAL_TAIL | 0.3333 | 0.6667 | OPEN_SHELL_BRANCH | OpenShellSkinBuilder | FACE_SET | 2 | 8 | 0.010299 | 0.253038 | 0.000000 | True |

Open-shell station profiles: 18. Their graph topology contains 30 individually ordered chains. Cross-station correspondence rate is 0.9667; four B-spline faces were constructed from usable tracks.

## Required answers

1. **Why is MAIN_WING suitable for closed-profile loft?** Eleven of twelve stations are truthful closed cycles (91.67%), exceeding the configured 75% closed threshold. It therefore stays on the unchanged V7A `LoftBuilder`; its fresh BRep is a valid solid and Q1 geometry.

2. **Why is FUSELAGE open-shell?** Nine of twelve stations are open-shell profiles (75%). The source part is non-watertight and the segment graph shows real open components, not small closure gaps. Its evidence-only route is `OPEN_SHELL_BRANCH`.

3. **Why is VERTICAL_TAIL open-shell?** Eight of twelve stations are open-shell (66.67%), exceeding the configured 50% open threshold. Four valid closed stations remain recorded but do not dominate routing.

4. **Can the 18 open stations establish stable cross-station correspondence?** Yes, with qualification: 18 open stations contain 30 graph-chain components; 29/30 are represented by tracks spanning at least two stations, for a 0.9667 valid correspondence rate. Five neutral tracks were found across fuselage and vertical tail.

5. **Does OpenShellSkinBuilder consume Geometry Analyzer profiles?** Yes. Profile perturbation changes the STEP and track correspondence perturbation changes it. An invalid/unordered measured chain is rejected. The execution contract records `PROFILE_SOURCE=GEOMETRY_ANALYZER`.

6. **Does runtime re-section the source mesh?** No. The builder does not import trimesh or accept a source mesh. Source mesh access occurs only after STEP generation in QA.

7. **Any fake closure, convex hull, bbox fallback or cap?** No. Forced closure, bbox closure, convex-hull closure, large-gap bridge and fake-cap counts are all zero. Sewing is disabled.

8. **Are final CAD edges derived from profile sampling segments?** No. Each measured chain is fitted into a smooth B-spline surface; final faces expose only true trimmed BRep boundaries. `PROFILE_SAMPLE_DERIVED_EDGE_COUNT=0` and section polylines preserved as CAD edges = 0.

9. **Final type for fuselage/vertical tail?** Both are valid `FACE_SET` results: two independent B-spline faces each, zero solids, no artificial closure. The topology API reports two one-face shells in each compound, so the truthful representation is FACE_SET rather than a sewn shell.

10. **Versus V7A forced-closed baseline?** Fuselage improves sharply: Chamfer 0.220415 → 0.012144, Hausdorff 0.617150 → 0.196382. Vertical-tail Chamfer improves 0.015880 → 0.010299, while Hausdorff worsens 0.204292 → 0.253038; this local worst-case gap remains visible. Both open-shell results avoid false solid semantics and remain compact two-face B-spline representations. Artificial-edge ratio is 0 under the measured boundary budget in both branches.

11. **Next step:** A — improve open-shell topology/sewing. Geometry extraction and routing work, correspondence is 96.67%, and both open parts produce valid Q2 face sets. The remaining issue is conservative boundary compatibility/sewing (especially vertical-tail Hausdorff), not returning to profile extraction or expanding Batch9 yet.

## Integrity

- Runtime remeasurement: false
- Historical STEP reused as output: false
- Raw QA metric rewrites: 0
- V7 contract regression: 35/35 passed
- V7B plus V7A regression: 39/39 passed
- Total: 74 passed, 0 failed
