# Curve100 sequence-budget audit (B0 / B1 / M2)

Do edge tokens crowd out CAD generation? `max_new_tokens=2048` for all arms;
geometry is spliced into the prompt (context max_pos=131k — not the bottleneck).

| arm | surf tokens p50/p90 | 2nd tokens p50/p90 | total_in mean | GT tok p90/max | GT>2048 | MAX_LEN | inexact | inexact∩MAX_LEN | 2nd tok exact→inexact | GT tok exact→inexact |
|---|---|---|---:|---|---:|---:|---:|---:|---|---|
| B0 | 240/4973 | 0/0 | 1096 | 1054/4715 | 4 | 3 | 5 | 3 | 0→0 | 361→3102 |
| B1 | 240/4973 | 93/637 | 1279 | 1054/4715 | 4 | 6 | 14 | 6 | 109→612 | 356→1373 |
| M2 | 240/4973 | 24/102 | 1139 | 1054/4715 | 4 | 4 | 5 | 4 | 37→94 | 358→3162 |
