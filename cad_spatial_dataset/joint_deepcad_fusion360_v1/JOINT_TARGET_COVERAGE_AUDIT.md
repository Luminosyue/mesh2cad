# JOINT_TARGET_COVERAGE_AUDIT_V1

## DeepCAD geometry_pack_v1
- n = **2194**
- parts with freeform-ish target ops = **0**
- parts only Extrude/Box/Cut/Union = **2194**
- ctor parts = `{"ExtrudePolygon": 1201, "Box": 989, "Cut": 843, "Union": 695, "Extrude": 521, "Circle": 521}`

## Fusion360 geometry_pack_v1
- n = **602**
- surface_valid = **602**
- edge_valid = **601**
- parts with freeform-ish target ops = **0**
- parts only Extrude/Box/Cut/Union = **602**
- ctor parts = `{"ExtrudePolygon": 438, "Cut": 335, "Extrude": 314, "Circle": 314, "Union": 276, "Box": 180}`

## Fusion360 STEP freeform parts (37)
- FUSION_FREEFORM_PARTS = **37**
- FREEFORM_PARTS_IN_PACK = **36**
- FREEFORM_PARTS_MISSING_PACK = **['132294_69821e40_0000']**
- FREEFORM_PARTS_WITH_LOFT = **0**
- FREEFORM_PARTS_WITH_SWEEP = **0**
- FREEFORM_PARTS_WITH_BSPLINE_TARGET = **0**
- FREEFORM_PARTS_WITH_ONLY_SKETCH_EXTRUDE = **36**
- FREEFORM_TARGET_COVERAGE = **0.0000** (0/36 in pack)

### Verdict

**Target language does not express STEP freeform.**
Joint surface→DSL training can still help analytic CAD, but will **not** teach
`BSPLINE` / `LOFT` / `SWEEP` emission from these `cad_target.dsl` labels.

