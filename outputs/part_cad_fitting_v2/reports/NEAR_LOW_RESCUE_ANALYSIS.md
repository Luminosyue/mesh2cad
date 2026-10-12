# Corrected Near-stage rescue analysis

Corrected Near cohort: 9 Strict, 52 Near, 2 Reject; rescue rate 14.29%.

The initial scalar-serialization parser defect prevented numeric candidates from running. It has been fixed and affected candidates rebuilt with identical parameter values. Initial reports are superseded, not treated as geometric evidence.

Remaining failed strict checks (overlapping): {'NCD': 19, 'bbox': 25, 'IoU': 40, 'centroid': 13}. Baseline selected in 5 cases. Successful methods: {'coordinate_descent_strict': 6, 'coordinate_descent_balanced': 1, 'axial_profile_refit': 1, 'local_search_alternative': 1}.

Three bounded coordinate sweeps and fixed structure limit the reachable shapes. The warped IoU64/4000-point optimization proxy can disagree with reloaded IoU128/20000-point evaluation, especially for thin geometry. This is a limitation, not proof of a global optimum.

Closed-section extraction can fail or miss topology. An inspected numerical Strict rescue closes a visible source opening. Open segmentation surfaces versus closed CAD can also cause a centroid mismatch; these issues need topology-aware fitting rather than looser thresholds.

The weighted ranking produces 2 Near-to-Reject changes despite score improvement; these are explicitly reported as classification regressions.

Continue the authorized 142 Reject cases with bounded structure alternatives only after this corrected Near analysis. No new objects, threshold changes, training or assembly.
