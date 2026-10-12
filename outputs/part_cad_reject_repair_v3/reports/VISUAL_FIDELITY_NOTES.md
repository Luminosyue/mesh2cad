

## Observed outcome and visual limitations

This round adds zero Strict parts. Seven numerical Near promotions must not be described as new strictly qualified CAD. Of the 124 repaired source parts, 122 have open boundary edges; 44 produce no supported closed-geometry proposal, leaving local parameter refinement only. Open boundaries are evidence of fitting difficulty, not proof that a part is impossible to reconstruct.

Visual inspection of object_00011/part_018 shows a lost end protrusion even though main-beam IoU and NCD improve. object_00002/part_002 still simplifies angular details. object_00017/part_002 receives a rotational candidate that remains visibly inconsistent with its asymmetric source and correctly remains Reject. These observations show that missing small features and wrong CAD family remain blockers alongside source openness. Numerical Near is an analysis label, not acceptance for training or assembly.

The overall bbox-error median worsens from 0.025329 to 0.029367, while NCD, IoU and centroid medians improve. Three cases have a worse weighted score because ranking prioritizes promotion from Reject to Near. There is no classification regression; all prior Strict and Near outputs remain byte-for-byte preserved. Keep V2 as the immutable comparison, and use these outputs as diagnostic experiments.

The next fitting investigation should preserve observed protrusions and holes while reconstructing supported boundaries and selecting appropriate compound structures. Thresholds and original input meshes remain unchanged.
