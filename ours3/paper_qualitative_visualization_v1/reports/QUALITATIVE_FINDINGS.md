# Qualitative Findings (EXACT9998 VAL1000 only)

- Surface-only A0 commonly preserves coarse extent but confuses operation type/order and over- or under-generates steps.
- GT-BRep line curves provide explicit profile/topology anchors, improving operation identity and recovery; A1 is more stable than A3 because the smaller line condition is less cluttered and less ambiguous than all-curve conditioning.
- P1 chiefly repairs under-generation, wrong primitive/Boolean choice, and early termination on VAL cases, while retaining residual placement, scale, direction, and parameter errors.
- Remaining errors are visible in fusion360 placement cases and Boolean-heavy Cut/Union cases: geometry can be visually close while origin, height, radius, or operation sequence is wrong.

These are validation qualitative findings. They are not a Final TEST conclusion; TEST1000 and holdout958 were not used.
