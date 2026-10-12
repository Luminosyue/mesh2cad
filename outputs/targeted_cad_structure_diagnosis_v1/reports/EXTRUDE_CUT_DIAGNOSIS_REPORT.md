# Extrude + Cut diagnosis

All 61 audited by source/CAD residuals, AST cut ablation, shared-grid base occupancy, actual removed material, and five closed-section topology checks.

Base-body supported/correct by declared rule: 8; base-body wrong by rule: 53. Dominant diagnosis: BASE_BODY_WRONG.

Cut position/depth problems cannot be distinguished from removed-source occupancy alone; 1 cases have harmful-cut evidence, explicitly not an exact position/depth diagnosis. Cuts below 16 occupied voxels: 54. Missing-hole positive evidence: 0, slot 0, recess 1. Full detector is restricted to the diagnosis subset; all other cases receive section/topology and ablation only. False flags mean no positive evidence, not confirmed absence. Wrong family count is unconfirmed, not zero.

Base rule is a heuristic diagnosis: outside-source fraction<=.03 and (base IoU>=.85 or base IoU>=.7 with <=3 compact major residual components). It does not replace strict geometry gates. A low base overlap means adding more small cuts is not the first remedy.
