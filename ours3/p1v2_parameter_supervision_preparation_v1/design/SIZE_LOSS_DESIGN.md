# P1V2-SIZE V1 design only

Future objective: L_total = L_base + lambda_op(t) * L_op + lambda_size * L_size.

This preparation does not select lambda_size and does not train. The first supported fields are Box.width, Box.height, Box.depth, Extrude.height, and ExtrudePolygon.height. Token-weighted semantic CE is the preferred first implementation if AST-to-token alignment remains exact. Continuous regression is design-only and would require an architecture change if a new head is needed.
