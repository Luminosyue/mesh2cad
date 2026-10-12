# Reproduce this frozen Smoke100

Use the recorded server environment:

```sh
PY=/data/miniconda3/envs/cadfit-env/bin/python
OLD=/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_data_factory_v1_smoke100
NEW=/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_data_factory_v1_smoke100_replay
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$OLD/scripts/bootstrap.py" --output-root "$NEW"
cd "$NEW"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 10
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 100
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/validate_and_report.py final
```

Bootstrap requires a never-used direct child of the project's outputs directory and refuses existing paths. This command sequence was not run a second time: the actual run used 3 → 10 → 100 once, preserving the same source selection, code and evaluator. The bootstrap copy helper is supplied for reproducibility. The historic source tree must remain present and match its hashes; the local delivery copy is an inspection bundle, not a self-contained replacement for that tree or the Python environment.

The run is capped at 100. SCALE_1000 is a next-stage readiness decision only, not an instruction executed by these files. It needs a new output root and a reviewed larger source inventory/configuration. The same group-safe provenance, program, reload, evaluator and integrity gates must remain in force.

Surface and curve caches were intentionally left NOT_BUILT because no cache extractor/schema was validated in this factory; no placeholder geometry is supplied. These optional caches do not affect the execution or geometry gate.

Runtime note: subdivision voxelization of long narrow triangles can have high transient memory use. One observed worker reached about 19 GiB RSS on this server (about 0.9 TiB RAM). The four-worker setting was used on this server; do not assume the same concurrency is appropriate on a small-memory host. This is an observed portability limitation, not a geometry score adjustment.

Final case failures and candidate failures have different denominators: the former count each source once after selection; the latter retain every attempted hypothesis. `candidate_outcomes_v2.csv` records that distinction. The three canary cases have also been reevaluated from their final serialized artifacts to check exact deterministic metric replay and coordinate round trips; see `reports/delivery_checks_v2.json`.

The first supplemental delivery check hit a NumPy boolean JSON serialization error after evaluating the artifacts. Its incomplete `reports/delivery_checks.json` and log are preserved for traceability and are superseded by `reports/delivery_checks_v2.json`. The correction converts the diagnostic boolean to Python bool; it changes no source, CAD, metric, filter decision or frozen core script. The authoritative supplemental entrypoint is `scripts/delivery_checks_v2.py`; packaging uses `scripts/package_delivery_v2.py`.
