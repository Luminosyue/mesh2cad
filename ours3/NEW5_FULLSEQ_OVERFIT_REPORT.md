# Demo5 full-sequence overfit report

Demo5 used the frozen Airplane9 checkpoint as weights-only initialization, with a new optimizer and scheduler, full-parameter training, dynamic lengths, and a strict round-robin sampler over five cases. Exposure counts were balanced; each case received the same number of updates through the stopping point.

At checkpoint 20, the TF scan had 5,287 total errors and 1/5 zero-error cases. At checkpoint 40, the same scan completed and training continued. At checkpoint 80, the TF scan had 57 total errors and 2/5 zero-error cases. At checkpoint 160, all five cases reached `TF_ERROR_N=0`, so training stopped immediately as required.

The checkpoint-20 and checkpoint-40 model weights were saved. Checkpoint-80 and checkpoint-160 weight saves were skipped by the explicit disk safety gate because `/data` had about 18.9GB free and writing another approximately 5GB model would have crossed the 15GB minimum. The checkpoint-160 state was replayed from checkpoint-40 in the same configuration to run free generation without lowering the disk safety floor.

Free generation was run with empty target, greedy decoding (`do_sample=false`), no ground-truth prefix, and no continuation. Tank `case_014 / PART_029` completed exact free generation: 1,529 q values, natural `E`, exact token/q match. Its generated V3 was parsed, compiled, executed in CadQuery, exported to STEP, read back, and matched canonical volume exactly (`abs error = 0`).

The other four free rollouts were not completed because the Tank rollout took about 20 minutes with the current generation implementation; the process was stopped immediately after the Tank gate to prioritize the requested Tank example. Therefore the final Demo5 free/CAD gate is `1/5 completed`, not a claimed 5/5 pass.
