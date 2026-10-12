# Airplane3 FAST vs Tank45 audit diff

| Item | Airplane3 FAST | Tank45 |
|---|---|---|
| Base | airplane3 experiment checkpoint-2000 correction | shared base checkpoint-8000 |
| Parts | 3 | 45 |
| LR | 1e-5 constant | 1e-5 constant |
| Micro batch | 1 | 1 |
| Grad accumulation | 3 | 3 |
| Sampling | 3-part balanced cycle | 45-part balanced cycle |
| Gate | FP32, TF32 disabled | no free decode; TF scans only |
| Trainable scope | full language/projector, frozen point tower | same |
| Total target blocks | 44 | 2226 |
| Per-part exposure at first exact | about 20–50 | 65 at +1000, insufficient for long parts |

The decisive scale difference is target coverage: Tank has 2226 blocks and several 77–109-block programs. Equal part exposure gives each part 65 block examples after 1000 updates, so most long-part blocks have only about one exposure. This explains incomplete memorization without requiring an LR or optimizer bug. The exposure trace separately reports 2925 events for 1000×3 nominal microsteps and must be fixed before another continuation.
