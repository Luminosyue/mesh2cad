# Near stage low-rescue analysis

29/63 improve the declared final score; only 5 satisfy all strict thresholds simultaneously. 34 retain baseline.

Remaining failures overlap: IoU 43, centroid 34, bbox 30, NCD 20. Radius-only diagnosis does not establish a sufficient repair.

The local optimizer uses warped IoU64 and fixed 4000-point subsets, while final acceptance uses reloaded geometry at IoU128 and 20000 samples. Proxy improvements need not transfer.

Three single coordinate sweeps and structure preservation limit reachable repairs; absent or inconsistent closed sections block profile refits.

Open segmentation surfaces versus closed CAD can create a surface-centroid mismatch; this is a hypothesis requiring case-level inspection, not an evaluator correction.

Low-yield Near stage analyzed before Reject. Continue authorized bounded family alternatives on original 142 rejects; no threshold changes, no extra objects, no assembly.
