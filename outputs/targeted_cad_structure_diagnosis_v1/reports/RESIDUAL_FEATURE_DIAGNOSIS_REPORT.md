# Residual feature diagnosis

45 frozen cases. Each initial/iterative residual includes 6-connected source-only and CAD-only components, voxel volume, bounding box, centroid, principal axes, aspect ratio, CAD triangle-centroid distance proxy, and nearest source-face orientation/covariance. All components retained in JSON, including tiny ones. Proposal minimum is 16 voxels; components over 35% of union occupancy are not treated as local features.

Detected case counts: hole 1, slot 1, recess 2, boss 23, secondary 1; unknown/no supported compact proposal 19.

Through versus blind is a measured span hypothesis; it is not independently verified semantic ground truth. CAD-only material suggests subtraction, source-only material suggests addition. Rule edit precision>=.65 rejects models that mostly damage already-correct material. No smooth spline or dense patch soup is introduced.

Counts are rule-supported hypotheses, not independent semantic ground truth. Feature type counts count unique cases and may overlap. Acceptance is based on actual native CAD/STEP geometry metrics. Semantic detector precision cannot be estimated without independent labels. Zero fillet/chamfer detections means not attempted before base/holes were validated, not absence. Occupancy uses the inherited approximate scan-fill protocol; source-only and CAD-only residuals are not exact solid Boolean differences. No new source points, transforms, objects, training, P3, reassembly, or assembly rendering.


Semantic review: primitive-shaped cut tools are not automatically holes/slots/recesses. Source sidewall occupancy around the fitted cutter must average >=.65 at three depths to retain those semantic hypotheses. 79 candidates lack that evidence and are marked GENERIC_CUT_OR_END_TRIM; 11 accepted edits are in this category. Their geometric gains remain valid but do not demonstrate recovery of true engineering cavities. Final detected feature counts apply this semantic rule; feature-type success tables preserve original proposed tool labels and expose semantic review columns in the candidate table. The one reviewed new Strict rod is an end-material trim, not a confirmed pocket.
