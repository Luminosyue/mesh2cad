# Public Baseline Evaluation Protocol

- Development split: EXACT9998 TRAIN/VAL only. TEST1000 is consumed and must not be used. holdout958 remains untouched.
- G0: surface/mesh/point-cloud-only input; comparable to A0 after representation and split alignment.
- G1: geometry plus predicted structural features.
- G2: GT/oracle CAD geometry, including A1/A2/A3/P1; controlled upper-bound only.
- OTHER: incompatible contracts; reference only.

Convert output to canonical CAD DSL or STEP before Exact, Op-F1, Parse, STEP Reload, Chamfer, and H95. Use N/A when conversion or one-to-one operation mapping is not defensible. EOS/MaxLen/UnderGen apply only to sequence generators. Mesh similarity must not be labeled editable-CAD success.

Freeze repository commit, checkpoint hash, preprocessing, split manifest, decoding settings, operation mapping, evaluator version, and runtime. Run one smoke case before VAL1000. No retraining or large downloads in this preparation phase.
