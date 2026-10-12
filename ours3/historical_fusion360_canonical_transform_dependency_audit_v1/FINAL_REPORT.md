# Historical Fusion360 canonical-transform dependency audit V1

**Gate:** `FUSION360_DORA_DEPENDENCY_REPLACEABLE_WITH_PROTOCOL_AMENDMENT`

Historical canonicalization uses only `features[:,0:3]` extrema. It performs uniform scaling and translation to bbox-min; it does not use normals, edge score, segmentation, grouping, labels, PCA, rotation, reflections, axis permutations, or sign flips. Therefore Dora semantics are not required. However, replacing sampled XYZ extrema with an OCC/BRep bbox is a new numerical protocol and must pass the designed 602-case overlap reproduction audit before expansion. No Dora, training, decode, or asset generation was run.
