# BATCH_CAD_NATIVENESS_RECOVERY_V3

Gate: `BATCH_CAD_NATIVENESS_RECOVERY_V3_PARTIAL_PASS`

The stage completed a uniform OCC audit and source-evidence-only reconstruction experiment. Geometry quality and CAD nativeness are reported independently; a valid/Q1 STEP is not automatically CAD-native.

Baseline native pass: 0; experimental native pass: 2; Q1/Q2/Q3 experimental candidates: 6/0/2.

CASE01 and CASE02 produced compact semantic-surface candidates but failed frozen geometry thresholds (Q3), so the historical Q1 results remain selected. CASE04 and CASE08 retained Q1 geometry and reduced face complexity, but remain COMPACT_BUT_SPLINE_DERIVED rather than CAD-native. CASE05/06 did not achieve reliable global freeform fitting. CASE00/07 improved source-derived fallback or deterministic-part coverage but programmatic-part ratios remain limited.

CASE02 label conflict is resolved: the historical SELECTED_BEST is FRAGMENTED_SPLINE_BREP; the prior analytic label referred to a different candidate artifact.

MAC was not used: endpoint returned HTTP 403 (quota unavailable). Deterministic results are not reported as MAC results.

Historical STEP hashes were unchanged; CASE03 and CASE09 stayed frozen. VTK rendering failed for CASE06 in the server display environment, and the affected panels are explicitly marked rather than misrepresented.

Independent tests: 31 passed, 0 failed.
