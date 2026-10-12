# Near-pass rescue

Original V1 cohort: 63. Final Strict: 11; Near: 52; Reject: 0. Rescue rate: 17.46%. Of the Strict outcomes, 9 were already Strict in the preserved baseline and 2 are additional this round. Do not attribute inherited improvements to new curve fitting.

The original strict failures and geometry-supported hypotheses are in near_pass_diagnosis.csv and each case's diagnosis JSON. Polyline approximation is a hypothesis until candidate comparison supports it. Multi-section stability uses 20/35/50/65/80% closed sections; open or inconsistent sections are explicitly recorded rather than fabricated. Missing holes/slots/fillets are unconfirmed unless measured topology supports them.

Pause policy fixed before fitting: >=10 original Near-to-Strict, >=1 additional Strict beyond preserved baseline, zero Near-to-Reject. Decision: PROCEED_REJECT. Reject recovery allowed: True.

Baseline remains a ranked candidate, so unsupported/invalid smooth fits cannot replace a better valid structure. Every new finalist is independently checked as native CAD before full geometry evaluation. Profile recognition uses least-squares + seeded RANSAC circle, ellipse fitting, rounded rectangle/slot model and line/arc segmentation; a periodic spline with at most 16 interpolation points is allowed only after analytic models fail. Full geometric metrics, not visual smoothness, determine selection.

## Remaining near failures

After initial full fitting, nonexclusive failed criteria were IoU 38, bbox 26, NCD 19 and centroid 11. The representation upgrade plus local fitting rescued two additional cases; this is modest incremental improvement, not a high recovery rate. Remaining failures require structural/detail diagnosis rather than cosmetic smoothing. Final per-case values are in near_pass_rescue_v2.csv.
