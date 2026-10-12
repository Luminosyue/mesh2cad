# Long-sequence memory root-cause audit

Experiment: `P3_XPART_20CASE_COMPACT_IR_V3_AND_DEMO_OVERFIT`

The formal V3 probe loaded the frozen model and `case_013` with the actual dynamic batch length of **12,065 tokens** (the independent context audit reports a maximum full sequence of 12,054; the collator adds the expected formatting tokens). The batch was not padded to 32,768.

Configuration observed at runtime:

- attention implementation: `sdpa`
- `use_cache`: `false`
- gradient checkpointing: active
- cutoff/context: 16,384
- trainable parameters: 1,238,440,960

The probe completed forward and backward for update 1. It failed during the first `AdamW.step()` while lazily allocating optimizer state, with a 64 MiB allocation failure. Recorded values were: before 5,154 MiB allocated / 5,180 MiB reserved; after forward 12,895 / 13,348; after backward 9,896 / 16,480; after optimizer-state allocation attempt 19,335 / 23,540, with a peak of 22,593 MiB allocated. The GPU had only about 30 MiB free because another process used about 21 GiB on that device.

Conclusion: the observed failure is an optimizer-state lazy-allocation OOM during the first update, amplified by concurrent GPU occupancy. There is no evidence of a graph leak from this run because the run stopped at update 1; the required three-update trajectory could not be completed. The memory gate is therefore **FAIL / INCOMPLETE**, not PASS. No 20-case joint overfit was started.
