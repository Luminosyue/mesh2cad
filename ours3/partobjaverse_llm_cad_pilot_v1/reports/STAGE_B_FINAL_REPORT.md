# PartObjaverse LLM Mesh-to-CAD Pilot20

## Dataset provenance

PartObjaverse-Tiny; 200 source objects and 2112 instance parts. Pilot20 was frozen from Stage A and contains 20 unique object UIDs. No source SHA mutation was detected.

## Evaluation protocol

Parametric CadQuery programs, at most three retained rounds per case, actual STEP export/reload, B-Rep validity, tessellation, and geometry evaluation. Surface sampling is fixed at 100,000 points. Metrics use normalized coordinates with maximum source bbox extent equal to 1; CAD work coordinates use maximum extent 100.

## Overall validity

Parse 20/20; execute 20/20; STEP export 20/20; STEP reload 20/20; valid B-Rep 20/20; geometry metrics 20/20.

## Geometry fidelity

Chamfer-L1 mean 0.08193355558329204, median 0.08070211430033827, std 0.044106604187822626 over 20 valid cases. Normal consistency mean 0.7150929415575156, median 0.7412550685640253. Bbox relative error mean 0.16748751131143919, median 0.11153491080918951. IoU has denominator 0 because it is only computed when both source and reconstruction are volumetrically valid.

## Breakdown by part category

- BOX_BOOLEAN_LIKE: N=4, B-Rep valid rate=1.0, CD mean=0.06832840113525787, CD median=0.061414245863686816, IoU mean=None, IoU median=None
- EXTRUDE_LIKE: N=4, B-Rep valid rate=1.0, CD mean=0.04139474855871451, CD median=0.038629855954214545, IoU mean=None, IoU median=None
- REVOLVE_CYLINDER_LIKE: N=4, B-Rep valid rate=1.0, CD mean=0.1296921136073904, CD median=0.13261195561443168, IoU mean=None, IoU median=None
- SHELL_LIKE: N=4, B-Rep valid rate=1.0, CD mean=0.07816027080644736, CD median=0.06767602027099758, IoU mean=None, IoU median=None
- HARDER_FREEFORM: N=4, B-Rep valid rate=1.0, CD mean=0.09209224380865011, CD median=0.09281952530411601, IoU mean=None, IoU median=None

## Refinement analysis

V1/V2/V3 valid counts are 20/20/20. Best versions: v1=18, v2=1, v3=1. Improved=2, degraded=19, invalidated=0. Definitions are recorded in PILOT20_SUMMARY.json.

## Failure modes

Final B-Rep failures: 0. Multi-solid execution was explicitly supported and no component was silently discarded. Primitive approximations commonly miss local recesses, thin features, and asymmetric residual geometry; these limitations are reflected by Chamfer and normal metrics rather than hidden by visual selection.

## Representative examples

All 20 cases, including failures, have cards under reports/PILOT20_GALLERY. Per-case source, reconstruction, overlay, route, best version, CD and IoU are shown.

## Conclusion

This pilot measures validity and fidelity on the fixed Pilot20 only. It does not establish superiority over a baseline. The observed validity rate is 1.000; geometric accuracy varies materially by category and primitive approximation.
