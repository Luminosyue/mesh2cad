# P2 Size Real-Model Canary Runner

This is a single-shot, fail-closed orchestrator. It never polls, retries, uses CPU as a model fallback, changes batch/context/curve settings after OOM, reads TEST1000 or the frozen 958-case holdout, or launches full training.

Run `--mode preflight` first. Preflight performs no model load and no training. It requires every execution-critical value and hash to be present in the frozen `P2_CANARY_CONFIG.json`; missing values are blockers, not defaults.

After preflight passes, `--mode all` performs one GPU safety check and invokes the frozen per-stage command arrays in order. Every stage must emit its registered PASS evidence before the next stage can begin. State is atomically recorded in `CANARY_RUN_STATE.json`.

Use `--help` for the explicit arguments. No argument has a hidden path or training default.
