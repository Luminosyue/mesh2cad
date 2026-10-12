# Structure refinement pilot

45/45 completed. 147 native feature candidate attempts; 13 selected edits, 134 rejected/unselected candidates. Significant improvement 6; new Strict 1; new Near 0; unchanged 35. All improvements are relative to previous completed V2-native output, not original V1.

IoU median 0.80027224 -> 0.81198239; NCD median 0.00946166 -> 0.00946166. These are paired subset medians, not all-209 medians.

Near significant: 1/20. Expansion criterion: >=8 newly Strict OR >=6/20 Near significantly improved (delta IoU>=.05 OR delta NCD<=-.003 OR improved status). Promising: NO.

Frozen 20,000 source points; original CAD sample seed and point count; IoU128; tessellation(.001,.05), serialized/reloaded PLY. Strict: IoU>=.90, NCD<=.01, bbox<=.03, centroid<=.02 plus native and STEP pass. Feature gate: delta IoU>=.02 OR delta NCD<=-.002 OR new Strict. Additional selection guardrails: no status damage, IoU decrease <=1e-6, NCD increase <=.0005. At most 3 rounds, 4 proposals/round, 3 retained features, 10 primitives and 8 Boolean operations. Residual fit uses PCA/CAD axes, closed-form primitives and deterministic bounded Powell optimization on the original occupancy grid. No case-ID branches.

Counts are rule-supported hypotheses, not independent semantic ground truth. Feature type counts count unique cases and may overlap. Acceptance is based on actual native CAD/STEP geometry metrics. Semantic detector precision cannot be estimated without independent labels. Zero fillet/chamfer detections means not attempted before base/holes were validated, not absence. Occupancy uses the inherited approximate scan-fill protocol; source-only and CAD-only residuals are not exact solid Boolean differences. No new source points, transforms, objects, training, P3, reassembly, or assembly rendering.


Semantic review: primitive-shaped cut tools are not automatically holes/slots/recesses. Source sidewall occupancy around the fitted cutter must average >=.65 at three depths to retain those semantic hypotheses. 79 candidates lack that evidence and are marked GENERIC_CUT_OR_END_TRIM; 11 accepted edits are in this category. Their geometric gains remain valid but do not demonstrate recovery of true engineering cavities. Final detected feature counts apply this semantic rule; feature-type success tables preserve original proposed tool labels and expose semantic review columns in the candidate table. The one reviewed new Strict rod is an end-material trim, not a confirmed pocket.
