# Final P1-v2 loss

`FINAL_P1V2_VARIANT = P1V2B`

`L_total = L_base + lambda_op(t) * L_op`

- `0.00 <= progress < 0.20`: `lambda_op = 0.5`
- `0.20 <= progress < 0.60`: `lambda_op = 0.25`
- `0.60 <= progress <= 1.00`: `lambda_op = 0.1`

Operation-mask semantics reuse the audited old-P1 definition unchanged. Completion loss is deferred and is not part of final P1-v2. Size, placement, SCF, non-line fusion, new heads, and new adapters are excluded.
