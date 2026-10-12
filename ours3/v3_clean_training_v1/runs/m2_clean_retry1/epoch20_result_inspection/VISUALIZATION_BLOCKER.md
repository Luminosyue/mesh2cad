# Visualization blocker

The saved epoch20 per-CAD file intentionally retains metrics only and discards generated DSL text. Its `step_reload` field is from the known missing-CadQuery environment. Therefore GT/predicted STEP galleries cannot be reconstructed without an additional frozen-checkpoint decode. That would violate the no-re-decode instruction. No gallery was created.
