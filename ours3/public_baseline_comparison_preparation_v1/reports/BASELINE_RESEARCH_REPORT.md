# Public Baseline Research Report

## Main conclusion
The defensible shortlist is Point2CAD, DeepCAD, and CAD-Recode. They have a plausible geometry/point-cloud-to-CAD-program contract and public repositories, but require a frozen preprocessing, split, checkpoint, vocabulary, and evaluator audit before numbers enter the main table.

CAD-MLLM is a reference candidate because its multimodal input contract is not automatically mesh-only. Fusion360 Gallery is a dataset/environment, not a reconstruction method. SpatialLM and an unpinned CAD Transformer family are literature leads, not runnable baselines.

## Fairness
A0 is G0 and is the correct internal comparator for public geometry-only methods after input alignment. A1/A2/A3/P1 consume GT B-Rep curves and belong to G2 oracle-assisted controls; they must not be presented as end-to-end mesh-to-CAD SOTA.

## Metric policy
Exact and Op-F1 are N/A when the external operation vocabulary cannot be mapped one-to-one to the canonical DSL. STEP Reload and geometry metrics require executable CAD/STEP; a mesh-only result can receive geometry similarity only with an explicit non-CAD label.

## Data protection
No TEST1000, holdout958, new training, new checkpoint, or baseline decode was run in this preparation phase.
