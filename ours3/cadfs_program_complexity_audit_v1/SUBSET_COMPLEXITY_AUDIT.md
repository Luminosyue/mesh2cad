# CADFS125 Program Complexity Audit

## Conclusion

The current geometry-verified CADFS subset is strongly biased toward simple sketch-extrude programs, which explains why the reconstruction gallery is dominated by boxes and cylinders.

## Evidence

- Parsed canonical DSL: 125/125 (Train100=100, Heldout25=25).
- Solid operation count: min 1, median 1, P90 1, max 5.
- DSL tokens: min 72, median 125, P90 154.2, max 510.
- Simple single-operation extrusion: 120/125 (96%).
- Multi-operation: 5/125; non-extrude feature: 5/125; advanced: 5/125.
- Heldout25: simple 24/25, multi-operation 1/25, advanced 1/25.

Complexity scores use only canonical program properties and never B0/M2 outcomes. The new galleries preserve the frozen held-out outputs and change selection/layout only.
