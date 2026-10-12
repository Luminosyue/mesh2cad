#!/usr/bin/env python3
"""Run remaining 9 cases while school_bus CADFit continues on the sequential runner.

Skips school_bus. Same tank protocol: frontend (exclusive GPU) then CADFit/STEP/assembly.
Uses the same GPU lock files so it won't collide with other frontends.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Reuse helpers from run_all
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_all import (  # noqa: E402
    LADDER,
    log,
    run_backend,
    run_frontend,
    utc_now,
)

SKIP = {"school_bus"}


def main() -> int:
    cases = [c for c in json.loads((LADDER / "cases.json").read_text())["cases"] if c["label"] not in SKIP]
    log(f"remaining-parallel start n={len(cases)} labels={[c['label'] for c in cases]}")
    results = []
    for spec in cases:
        log(f"=== start remaining {spec['label']} ===")
        try:
            front = run_frontend(spec)
            if front.get("status") != "frontend_ok":
                results.append(front)
                continue
            back = run_backend(spec)
            results.append({**front, **back})
        except Exception as exc:
            log(f"{spec['label']} exception {exc!r}")
            results.append({"label": spec["label"], "status": "exception", "error": repr(exc)})
    out = LADDER / "logs/run_remaining_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"remaining done {out}")
    bad = [r for r in results if r.get("status") not in ("ok",)]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
