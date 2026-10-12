# Visual QA

Viewed actual diagnostic images at delivery resolution; each has source, original CAD, original overlay, source-only residual, CAD-only residual, fitted tool, selected CAD, selected overlay with common camera/scale/coordinates.

- object_00019/part_008: new Strict. A rod end has excess CAD material; a box cutter removes it. IoU .8820 -> .9114, NCD .0021 -> .0019. This is an end-material correction, not independent evidence of a recess/pocket. Residual volumes are small (143 missing, 77 extra voxels), so voxel discretization is a material limitation.
- object_00016/part_014: a long angle-like part retains broad source/solid mismatch. Capsule-shaped boundary cut gives IoU .5074 -> .5835 but remains Reject. The tool's capsule shape does not prove a real slot exists.
- object_00011/part_005: rod end trims improve IoU .9094 -> .9804, but endpoint structures remain absent and the case stays Near. A cylindrical cutter is not automatically a hole detector success.
- object_00011/part_000: two accepted cuts, IoU .8596 -> .9622, still Near; visible source endpoint appendage remains missing. Metric improvement alone does not establish complete reconstruction.

After semantic review, panel 6 labels the actual BOX/CYLINDER/SLOT tool and whether geometry accepted; it no longer labels an unconfirmed engineering cavity as fact. Source-only and CAD-only residuals are separately visible, not hidden in an overlay. No image is presented as a new assembly or proof of semantic ground truth.
