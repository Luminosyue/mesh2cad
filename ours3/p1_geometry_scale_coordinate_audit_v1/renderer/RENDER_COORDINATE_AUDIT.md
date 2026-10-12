# Render coordinate audit

Renderer imports STEP directly, subtracts GT bbox center, divides by GT bbox diagonal, and uses fixed orthographic limits. No per-method fit/recenter/rescale is used. Small P1 panels reflect prediction STEP world-scale collapse, not a renderer-only bug.
