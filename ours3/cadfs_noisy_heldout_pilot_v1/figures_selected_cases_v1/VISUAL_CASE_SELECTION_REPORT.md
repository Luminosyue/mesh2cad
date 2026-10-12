# Visual Case Selection Report

## Why the old gallery was less informative

It followed frozen-order/random-style coverage and was dominated by simple box and cylinder primitives. It did not deliberately expose the three M2 program rescues or the geometry disagreements.

## Selection rules

Cases are classified from frozen per-case OpF1, corrected GT-DSL-reference geometry, DSL token count, and curve count. The main figure contains two simple sanity cases, the two clearest M2 rescues, and two complex bottleneck cases. The supplemental figure adds all three rescues and three geometry disagreements. No model output was regenerated.

## Main 6

- `cadfs__00802498` | SIMPLE_GOOD | OpF1 1.00->1.00 | Chamfer 0.0269->0.0269 | Both reconstruct the simple cylindrical primitive.
- `cadfs__00820019` | SIMPLE_GOOD | OpF1 1.00->1.00 | Chamfer 0.0203->0.0203 | Both recover the simple box-like target with similar geometry.
- `cadfs__00830309` | M2_RESCUE | OpF1 0.00->1.00 | Chamfer 0.0191->0.0102 | M2 rescues the primitive type and improves geometry.
- `cadfs__00826947` | M2_RESCUE | OpF1 0.00->1.00 | Chamfer 0.0585->0.0495 | M2 fixes the operation structure and lowers Chamfer.
- `cadfs__00887702` | HARD_COMPLEX | OpF1 1.00->1.00 | Chamfer 0.0221->0.0221 | Both miss important topology in this complex multi-feature target.
- `cadfs__00982874` | HARD_COMPLEX | OpF1 0.50->0.50 | Chamfer 0.0467->0.0390 | Both programs are partial; M2 lowers Chamfer but remains imperfect.

## Representative 10

- `cadfs__00802498` | SIMPLE_GOOD | Both reconstruct the simple cylindrical primitive.
- `cadfs__00820019` | SIMPLE_GOOD | Both recover the simple box-like target with similar geometry.
- `cadfs__00830309` | M2_RESCUE | M2 rescues the primitive type and improves geometry.
- `cadfs__00826947` | M2_RESCUE | M2 fixes the operation structure and lowers Chamfer.
- `cadfs__00984691` | M2_RESCUE | Program structure improves, but M2 geometry remains imperfect.
- `cadfs__00804541` | GEOMETRY_DISAGREEMENT | Programs tie; B0 is geometrically closer on this box-like case.
- `cadfs__00890175` | GEOMETRY_DISAGREEMENT | Both program scores are correct, but placement geometry remains poor.
- `cadfs__00948858` | GEOMETRY_DISAGREEMENT | B0 and M2 look similar; B0 has lower Chamfer.
- `cadfs__00887702` | HARD_COMPLEX | Both miss important topology in this complex multi-feature target.
- `cadfs__00982874` | HARD_COMPLEX | Both programs are partial; M2 lowers Chamfer but remains imperfect.

## Takeaway

Simple cases are reconstructed similarly by both arms. M2 improves program structure on three unseen cases, but the geometry gain is not consistent. The remaining bottleneck is geometric representation, placement, and relation modeling.
