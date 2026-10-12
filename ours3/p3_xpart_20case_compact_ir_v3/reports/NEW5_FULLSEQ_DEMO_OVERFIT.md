# Demo5 full-sequence overfit status

The V3 Demo5 manifest was prepared with `case_018`, `case_009`, `case_014` (Tank `PART_029`), `case_010`, and `case_005`, using an 8,192-token context. The required memory gate was run first on the longest V3 case under the formal model configuration.

The gate failed at update 1 during lazy AdamW state allocation after forward and backward completed. Because the gate did not pass, Demo5 overfit, checkpoint TF scans, free generation, and CAD generation were not started. This report records the result as pending rather than claiming exact overfit.
