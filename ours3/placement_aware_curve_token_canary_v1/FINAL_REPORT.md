# Complex15 Placement-aware Curve Canary V1

## Result

`CURRENT_GATE=PLACEMENT_AWARE_CURVE_TOKEN_CANARY_PASS`

- Complex15 leakage: PASS; real complex: YES.
- Full V3 pipeline: 13/15; one noise rejection and one no-sharp-curve rejection were retained without replacement.
- Placement descriptors: 403/403 finite, dimension 17, deterministic hash 3/3.
- V1/V2 interface: PASS; old M2-V1 forward regression: PASS.
- One-batch loss/backward: PASS; exactly one optimizer step: PASS; clean checkpoint reload: PASS.

## Method

Frozen C2 remains unchanged. Each 256-D local C2 token is fused with a deterministic 17-D object-relative placement descriptor through `17->64->256`, residual addition, and LayerNorm. The existing 8-query GeometryPrefixAdapter, SpatialLM projection/interface, prompt, splice, target, and EOS remain unchanged.

## Scope

This is an implementation canary, not an effect experiment. No formal training, decode, held-out evaluation, or model comparison was run.
