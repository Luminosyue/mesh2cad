# P1 x P3 REAL-MESH MULTI-CASE PROBE v1

| Case | Part N | P1 Parse | CAD Exec | STEP Reload | Multi-op Rate | Premature EOS Rate |
|---|---:|---:|---:|---:|---:|---:|
| canister | 3 | 2 | 2 | 2 | 0.333 | 0.333 |
| car | 13 | 9 | 9 | 9 | 0.615 | 0.308 |
| cube | 7 | 2 | 2 | 2 | 0.143 | 0.714 |
| mini_excavator | 10 | 8 | 8 | 8 | 0.800 | 0.200 |
| pressure_cooker | 6 | 1 | 1 | 1 | 0.167 | 0.833 |
| recordplayer | 7 | 2 | 2 | 2 | 0.286 | 0.714 |
| school_bus | 8 | 5 | 5 | 5 | 0.375 | 0.375 |
| speaker_small | 9 | 3 | 3 | 3 | 0.222 | 0.667 |
| toaster | 8 | 3 | 2 | 2 | 0.250 | 0.625 |
| vase | 4 | 1 | 1 | 1 | 0.250 | 0.750 |

## Diagnostic answers
Q1: P1 parsed 36/75 real-mesh parts.
Q2: premature EOS rate=0.520; multi-op rate=0.387.
Q3: Main failure mode: LLM_PROGRAM_GENERATION.
Q4: Good-curve plus collapse cases are listed by joining curve_audit.csv and inference_results.csv.
Q5: READY_FOR_139_CASE_SCALEUP=NO; blocker is real-mesh program collapse.
