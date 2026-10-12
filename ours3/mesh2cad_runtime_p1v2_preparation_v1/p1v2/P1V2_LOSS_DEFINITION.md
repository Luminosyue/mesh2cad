# P1-v2 loss definition

## Operation supervision

`L_op` reuses the already audited old-P1 operation-token mask exactly. P1-v2a uses `lambda_op=0.25`; P1-v2b/c use the preregistered schedule 0.5/0.25/0.1 over 0-20%/20-60%/60-100% of training. No TEST-derived adjustment is permitted.

## Completion supervision

P1-v2c adds no prediction head. It uses the existing shifted LM logits. For each supervised position before the ground-truth terminal EOS, define `m_early(t)=1`; at the ground-truth EOS position and all ignored/padded positions it is zero. The penalty is `L_completion = sum_t m_early(t) * [-log(1-p_t(EOS))] / max(1,sum_t m_early(t))`. EOS means the frozen tokenizer/config EOS-id set. The term penalizes premature EOS only; it does not reward tokens after the true EOS and does not directly encourage arbitrary sequence length.

The canary must verify mask parity, zero penalty at true EOS/padding, finite loss, and gradient connection to existing LM logits.
