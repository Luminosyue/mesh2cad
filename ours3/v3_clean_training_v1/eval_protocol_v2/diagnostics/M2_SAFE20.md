# M2 SAFE20

Status: TRAIN_SELF_DECODE_DIAGNOSIS (not held-out).

- N: 20
- eos: 19
- hit_cap: 1
- has_result: 19
- parse_pass: 16
- exec_pass: 16
- step_write_pass: 16
- step_reload_pass: 16
- status: TRAIN_SELF_DECODE_DIAGNOSIS_NOT_HELDOUT
- max_new_tokens: 4096
- decode: greedy

## Generation tokens
{
  "median": 335.5,
  "p90": 2180.0000000000005,
  "max": 4096
}

## Primary failures
{
  "DSL_PARSE_FAIL": 3,
  "NO_EOS_RUNAWAY": 1,
  "STEP_RELOAD_PASS": 16
}
