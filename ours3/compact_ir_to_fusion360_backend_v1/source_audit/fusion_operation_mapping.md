# Compact IR → Fusion 360 operation mapping

| IR_OP | CADQUERY_MAPPING | FUSION_MAPPING | SUPPORTED | NOTES |
|---|---|---|---|---|
| Workplane | `cq.Workplane(plane, origin=...)` | `ConstructionPlane` offset from `xYConstructionPlane` + `Sketch` | PASS | Section origin is dequantized and remains a local sketch-plane offset. |
| spline | `Workplane.spline(points, periodic=True)` | `SketchFittedSpline` from an `ObjectCollection` of `Point3D` | PASS | Point order, point count, and periodic/closed flag are preserved. |
| loft | `toPending().loft(ruled=True, combine=False)` | `LoftFeature` with profiles added in source section order | PASS | No profile sorting or re-sampling. |
| located | `result.located(cq.Location(cq.Plane(...)))` | `Matrix3D.setWithCoordinateSystem` basis/origin | PASS | Uses dequantized origin, xDir, and normal from the semantic transform. |
| translate | `scale(...).translate([...])` | `BRepBody.transformBy(Matrix3D)` | PASS | Scale and translation are applied after loft in the same order. |
| xDir | CadQuery local plane x direction | Fusion `Matrix3D` x basis | PASS | Preserves local frame semantics. |
| normal | CadQuery local plane normal | Fusion `Matrix3D` normal basis | PASS | Preserves local frame semantics. |
