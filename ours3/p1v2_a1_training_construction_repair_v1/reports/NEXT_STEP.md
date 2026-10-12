# Next step

Audit deterministic gradient replay without changing the frozen tolerance: control TF32, gradient-checkpoint recomputation state, RNG, and mutable forward caches. Do not change loss, lambda, schedule, checkpoint, or method. Repeat lambda=0 parity before any operation/completion audit.
