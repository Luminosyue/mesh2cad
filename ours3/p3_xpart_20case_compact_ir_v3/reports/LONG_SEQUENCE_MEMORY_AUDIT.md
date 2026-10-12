# V3 context and memory audit

V3 preserves the frozen 20-case manifest and all validated q14 sequences. Full-sequence lengths range from 166 to 12,054 tokens; median is 4,139.5, p90 is 11,927, and p95 is 12,053.05. The smallest candidate context that contains every case without truncation is **16,384**.

The dynamic collator produced an actual tensor length of 12,065 for the longest-case probe, confirming that training does not pad every sample to 32,768. Runtime configuration was SDPA attention, `use_cache=false`, and active gradient checkpointing.

The formal full-parameter probe reached forward and backward but failed on the first AdamW optimizer step while allocating lazy state. Because the memory gate did not pass, the 20-case full-sequence overfit is intentionally pending.
