# V7D Common Boundary Control Net and V7C Rerun

## Outcome

`CURRENT_GATE=V7D_COMMON_BOUNDARY_CONTROL_NET_AND_V7C_RERUN_PARTIAL`

The topology target is real for both parts: 3 shared OCC edges, 6 pcurves, and 6 valid trimmed faces were created from saved measured open-chain evidence. No sewing, caps, mesh resection, GT input, historical STEP, or profile-sample CAD edges were used.

The gate remains PARTIAL because the vertical-tail local constrained refit regressed geometry: Chamfer 0.0102987825 → 0.0235079181, Hausdorff 0.253037655 → 0.470549851. This cannot be called PASS even though its G0 topology succeeds.

## Required answers

1. V7B independently fit each measured chain track. Their surface boundaries were not constrained to the same geometric control row, so V7C's strict matcher saw large endpoint/reconciliation gaps and found no shared boundary.
2. FUSELAGE recovered 2 stable seam tracks.
3. VERTICAL_TAIL recovered 1 stable local seam track; a direction-reversing continuation was rejected.
4. Yes. Every master curve is sourced from `MEASURED_OPEN_CHAIN_ENDPOINT_TRACK` with station and chain provenance.
5. No. `PART_ID_HARDCODE_COUNT=0`; Part IDs only index inputs/outputs, never select endpoints.
6. Yes. For accepted seams, the identical boundary pole row is written to both BSpline surfaces.
7. FUSELAGE OFF/ON P95: 0.117804242 / 3.90735977e-17. VERTICAL_TAIL OFF/ON: 0.0618047447 / 0.
8. Yes. FUSELAGE boundary P95 fell from 0.384530528 to 3.90735977e-17.
9. Yes for G0 boundary compatibility: 0.174436543 to 0; however whole-part geometry regressed.
10. No. Vertical-tail SIDE Hausdorff worsened from 0.253037655 to 0.470549851.
11. Yes. Preview edge-to-surface P95 is at numerical precision on both supporting surfaces.
12. Yes. V7C rerun produced 3 real shared TopoDS_Edge objects.
13. Yes. 6 face-side pcurves were validated.
14. Yes. 6 OCC-valid trimmed faces were created.
15. Both remain FACE_SET. Open boundaries are preserved; no Shell/Solid was forced.
16. FUSELAGE common-control-net blocker can be removed for the scoped shared core.
17. Do not fully delete the VERTICAL_TAIL blocker yet: G0/topology is constructed, but geometry regression requires continued constrained-refit work.
18. The blanket V9 wireframe-consumption blocker can be narrowed: both parts now have wireframe → master boundary → shared edge provenance, but the vertical-tail geometry-quality blocker remains.
19. Choose D: continue common-boundary constrained-refit, specifically vertical-tail interior/extension optimization while freezing its proven shared edge. Do not expand to the primitive selector, Qwen builder, or full router yet.
