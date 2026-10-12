# Reproduction

Interpreter: /data/miniconda3/envs/cadfit-env/bin/python

The code has exclusive-create guards. Do not rerun into a populated directory; clone the scripts to a NEW audit directory and change only OUT/BASE to that new directory. Keep existing inputs unchanged.

1. python -B code/audit_v2_labels.py --inventory
2. python -B code/audit_v2_labels.py --workers 24 --tag FULL
3. python -B code/inspect_v2_protocol.py
4. python -B code/test_v2_audit.py
5. /data/miniconda3/envs/spatiallm/bin/python -B code/finalize_v2_audit_complete.py

No model weights are loaded; CUDA_VISIBLE_DEVICES is empty in replay workers. Per-sample subprocess timeout:150 seconds. No source-JSON fallback. A failed worker is explicitly a failed audit, never silently omitted.
