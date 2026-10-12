# P1 Toaster Failure Diagnosis

CURRENT_GATE=P1_FAILURE_DIAGNOSIS_READONLY_COMPLETE
CASE=TOASTER
DENOMINATOR_39=39

## Scope
This is a diagnostic-only analysis of existing P1, CADFit, and X-Part artifacts. No P1/CADFit inference, training, optimization, ICP, or historical-file modification was performed. Formal P1 and CADFit outputs remain untouched.

## 1. Aggregate diagnosis
P1 and CADFit are both valid on 39/39 parts. The failure is not a validity failure. P1 global CD mean is 0.287389 and median 0.262690; CADFit global CD mean is 0.008950. CADFit wins global CD on 39/39 parts. P1 high-error quartile contains 10/39 parts, but the median error is also large and there are no P1 wins, so this is a system-wide geometry gap with a smaller set of severe outliers, not an outlier-only failure.

P1 normalized CD mean is 0.270567, median 0.258987. Mean centroid error is 0.452586. Mean bbox extent error is 8.462862. These jointly indicate shape/extent mismatch, with placement also materially contributing.

## 2. Geometry vs placement
A translation-only centroid alignment diagnostic (not a formal output and not ICP) reduces P1 mean CD from 0.287389 to 0.163173. The mean placement gap is 0.124216, approximately 38.9% of the original CD. The remaining centroid-aligned geometry error is still large. Therefore the primary diagnosis is **GEOMETRY_ERROR**, with a secondary **PLACEMENT_ERROR** component. The extreme bbox extent error confirms that this is not explainable by translation alone.

## 3. Representation and topology signals
P1 operation totals are `{"ExtrudePolygon": 39}`: every one of the 39 programs is `ExtrudePolygon`; there are zero observed `Box`, `Cylinder`, `Cut`, `Union`, `Revolve`, `Fillet`, or `Chamfer` tokens. This is not “excessive Box approximation”; it is a stronger primitive/operation collapse into one polygon extrusion family. It provides a clear CAD DSL representation bottleneck signal.

This pattern is consistent with missing holes/cuts, missing curved boundaries, and wrong extrusion extents where those structures are needed. It is an architectural/representation diagnosis from existing outputs, not proof that every individual error has one exact semantic cause. P1 face/edge counts and CADFit face/edge counts are recorded per part in the CSV for topology mismatch inspection.

## 4. Error concentration
Highest normalized-CD parts: PART_009, PART_008, PART_034, PART_005, PART_002, PART_004, PART_023, PART_006, PART_029, PART_038.

Largest whole-assembly surface-error contributions (GT surface area times P1 global CD): PART_018, PART_017, PART_035, PART_033, PART_020, PART_036, PART_034, PART_037, PART_011, PART_019.

Large-shell quartile: PART_011, PART_015, PART_017, PART_018, PART_020, PART_023, PART_033, PART_035, PART_036, PART_037.

Small-detail quartile: PART_002, PART_006, PART_010, PART_022, PART_024, PART_026, PART_030, PART_031, PART_032, PART_038.

Planar/prismatic quartile: PART_011, PART_017, PART_018, PART_019, PART_022, PART_028, PART_033, PART_035, PART_036, PART_038.

High-curvature quartile: PART_001, PART_003, PART_004, PART_005, PART_008, PART_009, PART_013, PART_014, PART_015, PART_023.

Curve-aware priority candidates, ranked by GT dihedral-curvature proxy: PART_001, PART_005, PART_003, PART_014, PART_004, PART_008, PART_013, PART_015, PART_009, PART_023.

## 5. Requested failure checks
- Excessive Box approximation: **No**. No Box tokens were generated.
- Excessive primitive simplification: **Yes, strongly indicated** by ExtrudePolygon-only output.
- Missing holes/cuts: **Likely representation failure**; zero Cut/Union operations are observed.
- Missing curved boundary: **Likely on high-curvature parts**; prioritize the curve list above.
- Wrong extrusion extent: **Present as a measurable symptom**; bbox extent error is large.
- Wrong placement: **Present but secondary**; centroid-only diagnostic removes about 38.9% of CD.
- Topology/operation mismatch: **Indicated** by the one-operation family versus varied CADFit face/edge structures; inspect CSV counts per part.

## 6. Representative visualizations
The gallery contains four-panel, same-camera renders: `GT X-Part | P1 CAD | CADFit CAD | error overlay`. It includes highest-error, assembly-contribution, curved-priority, and small-detail representatives. Empty requested categories are explicitly recorded in `eval/part_classes.json` rather than filled with fabricated examples.

## 7. Final answers
- P1 toaster failure is **not mainly a few outliers**. Severe outliers exist, but all 39 parts lose on global CD and the median error is high.
- The dominant problem is a **39-part systematic geometry/representation gap**.
- Largest per-part errors: PART_009, PART_008, PART_034, PART_005, PART_002; largest assembly contribution: PART_018, PART_017, PART_035, PART_033, PART_020.
- Geometry error is primary; placement error is secondary but non-trivial.
- The current CAD DSL shows a clear representation bottleneck: all P1 programs collapse to `ExtrudePolygon`.
- Curve-aware geometry is most valuable for high-curvature parts `PART_001, PART_005, PART_003, PART_014, PART_004, PART_008` and for the large assembly contributors `PART_018, PART_017, PART_035, PART_033, PART_020, PART_036` where curved/complex boundaries amplify surface error.
- Dora/curve conditioning should be prioritized on those high-curvature and high-contribution parts, but this report does not run or propose a new benchmark; it only identifies the highest-value diagnostic targets.

## Outputs
- `eval/failure_diagnosis_per_part.csv`
- `eval/error_contribution_ranking.csv`
- `eval/operation_vs_error.csv`
- `eval/diagnosis_summary.json`
- `eval/part_classes.json`
- `gallery/`
- `manifest/readonly_sources.json`

## Integrity
P1 history modified: NO. CADFit history modified: NO. New inference: NO. New training: NO. ICP used for formal output: NO.
