# Numeric serialization defect and repair

A candidate-level audit found native CAD parser failures caused by NumPy scalar repr emitting `np.float64(...)` in generated numeric expressions. This was an implementation defect, not evidence that the geometry family could not fit. The initial 5/63 Near rescue count and the first low-yield explanation were provisional and are superseded by the repaired rescore.

The code generator now converts NumPy arrays and scalars to ordinary Python literals. Regression checks cover the six native kinds present in this dataset: extrusion, extrusion with cuts, box, cylinder, section loft and revolve. The original restricted native-CAD validator is unchanged.

Already generated failing candidates are repaired by replacing scalar wrappers with the exact numeric argument, retaining candidate IDs and fitted parameter vectors. Their failed code and execution records are retained beside the corrected records. They are rebuilt, exported, reloaded and rescored with the same frozen evaluator. This does not add structural candidates or increase the eight-candidate budget. The Reject run was paused until Near repair and review finish. Interrupted executions are archived before resumption.

Candidate records contain `numeric_serialization_repair`; per-case pre-repair results and the initial Near reports are retained under explicit pre-repair names. Final counts must come from reports/summary.json after repair. The final validator checks every active candidate against the native AST validator, including candidates that were not selected.
