# Compact IR to EXACT10K semantic mapping report

Current Airplane semantic AST vocabulary is Workplane, periodic Spline, ruled Loft, located, and translate. The old target vocabulary is Canonical CAD DSL.

| COMPACT_OPERATION | EXACT10K_OPERATION | SUPPORTED | LOSSLESS | PARAMETER_MAPPING | NOTES |
|---|---|---|---|---|---|
| Workplane | Sketch / plane placement | NO | NO | plane, origin, xDir, normal | Workplane frame has no equivalent old assignment. |
| periodic Spline | Sketch bspline / ExtrudePolygon | NO | NO | section_i/spline/point_j/{x,y} | Frozen serializer emits no spline construct. |
| ruled Loft | Extrude / feature chain | NO | NO | loft.ruled and section references | Replacing loft with extrusion changes topology and geometry. |
| located | placement transform | NO | NO | transform/located/value_k | No equivalent old placement field. |
| translate | placement transform | NO | NO | transform/translate/{x,y,z,w} | Cannot be folded into origin without changing frame semantics. |
| origin | operation parameter | PARTIAL | NO | section_i/workplane.origin.{x,y,z} | Value can be dequantized but receiving operation is absent. |
| xDir | placement direction | NO | NO | section_i/workplane.xDir.{x,y,z} | No old DSL field preserving frame. |
| normal | placement direction | NO | NO | section_i/workplane.normal.{x,y,z} | No old DSL field preserving frame. |
| 14-bit q | decimal physical value | POSSIBLE | YES ONLY AFTER DEQUANTIZE | q -> metadata dequantize -> serializer | Numeric encoding conversion only. |

COMPACT_TO_EXACT10K_SEMANTIC_MAPPING=FAIL.

This is a representation mismatch. No converted target files were created; polygon/extrude approximation or STEP import would violate lossless conversion.
