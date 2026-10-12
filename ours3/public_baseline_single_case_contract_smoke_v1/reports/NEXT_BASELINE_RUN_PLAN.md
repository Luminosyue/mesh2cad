# Next baseline run plan

1. CAD-Recode: obtain the official Hugging Face checkpoint only after confirming storage/runtime budget; run the official demo on the frozen VAL smoke case. Preserve XYZ coordinates and apply only documented normalization/denormalization.
2. Point2CAD: do not run until an official or separately frozen surface-cluster segmentation input exists; assigning a constant or GT-derived surface id would invalidate the contract.
3. DeepCAD: do not label as mesh-to-CAD baseline unless an official geometry-conditioned inference path is found. Its released README documents CAD-sequence/latent workflows.

A baseline may enter VAL1000 only after repository/checkpoint/inference PASS, frozen adapters, no GT-dependent alignment, and evaluator compatibility.
