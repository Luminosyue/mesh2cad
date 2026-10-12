# P2 Design Recommendation

P2_STATUS = JUSTIFIED

Recommended target: **SIZE**.

Keep the P1 architecture and operation-aware loss unchanged. If pursued, add exactly one operation-aware, parameter-group-aware objective:

`L_total = L_base + lambda_op * L_op + lambda_param * L_param`

Do not use an undifferentiated all-numeric-token loss. Start with one controlled ablation for SIZE; leave `lambda_param` undecided until that experiment is designed. No P2 training was launched in this audit.
