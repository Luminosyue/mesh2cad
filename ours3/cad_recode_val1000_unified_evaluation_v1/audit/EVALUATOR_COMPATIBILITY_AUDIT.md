# Evaluator Compatibility Audit

Status: preliminary; inference is incomplete.

- CAD-Recode emits executable CadQuery Python, whereas A0-A3 emit the project canonical CAD DSL.
- Exact Match is representation-dependent and is not directly comparable without an already frozen, audited semantic conversion.
- Op-F1 is comparable only if a frozen CAD-Recode-to-project operation taxonomy mapping is verified. No ad hoc mapping is authorized.
- Parse uses different front ends, so the outcome rate is useful but parser semantics must be disclosed.
- CAD execution, STEP export, and real STEP reload are representation-independent pipeline outcomes and can be compared case-wise.
- Chamfer, H95, and volume are cross-method comparable only under the exact A0-A3 GT, normalization, sampling, seed, failure handling, and denominator policy.

Formal evaluator execution is gated on 1000/1000 frozen predictions.
