# Visual QA

Inspected source / original V1 / final selected CAD / overlay with identical camera, scale and coordinates:

- `object_00002/part_009`, new Strict: rounded profile agreement improves. Fine source faceting and small boundary variations are not reproduced exactly.
- `object_00010/part_003`, new Strict: long section profile matches more closely. Irregular end boundaries remain approximated.
- `object_00006/part_003`, still Near: a visible source opening region and rounded edge details remain missing or simplified. IoU around 0.95 alone is insufficient; NCD remains above 0.01. The previous best geometry is preserved, not mislabeled as repaired.
- `object_00008/part_000`, still Reject: fragmented/open segmented source is poorly represented by the available compact extrusion hypotheses. The inherited V3 candidate improves on the original box but remains substantially wrong. A smooth preview does not change that conclusion.

These examples support a remaining structural/detail problem, not merely a polygon-display problem. Open mesh boundaries are observations, not proof that the real object has a designed through-hole; further reconstruction must use corroborating section and surface evidence rather than inventing cuts.

Renderer comparisons inspected: toaster, robot and kettle. Surface-aware shading removes point-sampling grain while retaining real faceted profile walls and stepped revolved profiles. B-Rep edge overlays do not show tessellation triangle edges. Curved edge sampling was increased to reduce line/surface depth artifacts. No evident clipping or unreadable principal labels in the inspected images.

The two new Strict cases are prioritized in the 10 Near-to-Strict illustrations. The remaining illustrated original Near-to-Strict cases include inherited historical rescues and are explicitly identified by their fix type. Numerical Strict and representation acceptance are not claims of exact recovery of every source detail.
