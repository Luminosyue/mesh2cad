# B0 SAFE20

Status: TRAIN_SELF_DECODE_DIAGNOSIS (not held-out).

- N: 20
- eos: 17
- hit_cap: 3
- has_result: 17
- parse_pass: 17
- exec_pass: 17
- step_write_pass: 17
- step_reload_pass: 17
- status: TRAIN_SELF_DECODE_DIAGNOSIS_NOT_HELDOUT
- max_new_tokens: 4096
- decode: greedy

## Generation tokens
{
  "median": 113.5,
  "p90": 4096.0,
  "max": 4096
}

## Primary failures
{
  "NO_EOS_RUNAWAY": 3,
  "STEP_RELOAD_PASS": 17
}
