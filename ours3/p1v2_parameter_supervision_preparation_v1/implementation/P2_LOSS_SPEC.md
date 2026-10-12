# P1V2 Loss Specification

`L_total = L_base + 1.0 * L_op + lambda_size * L_size`

`L_size` is token CE on AST-derived semantic fields only: Box(width,height,depth), Extrude(height), ExtrudePolygon(height), and Cylinder(radius,height) only if coverage passes. Base CE still covers all supervised tokens. No origin, translation, center, direction, axis, profile point, or generic numeric token receives extra weight.
