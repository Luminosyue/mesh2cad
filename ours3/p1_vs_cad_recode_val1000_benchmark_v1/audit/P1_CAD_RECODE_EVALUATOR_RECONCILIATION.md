# Evaluator Reconciliation

Pipeline outcomes are comparable on the same 1000 IDs. Exact and Op-F1 are blocked because P1 uses canonical CAD DSL while CAD-Recode emits CadQuery Python and no frozen semantic mapping was provided. Geometry comparison is blocked: CAD-Recode per-case records do not contain Chamfer/H95/Volume values generated under the frozen A0-A3 protocol. No new evaluator or prediction modification was performed.
