#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import sha256_file


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--out", default="artifacts/abc_hard_two_case_demo/sketch_prior_audit.json")
    args = ap.parse_args()
    ckpt = Path(args.checkpoint) if args.checkpoint else None
    data = {
        "prior_mode": "no_prior",
        "checkpoint_path": str(ckpt) if ckpt else "",
        "checkpoint_exists": bool(ckpt and ckpt.exists()),
        "checkpoint_sha256": "",
        "device": "unknown",
        "load_success": False,
        "silent_fallback": False,
        "notes": "No local sketch-prior checkpoint was found during environment audit.",
    }
    if ckpt and ckpt.exists():
        data["checkpoint_sha256"] = sha256_file(ckpt)
        try:
            import torch
            data["device"] = "cuda" if torch.cuda.is_available() else "cpu"
            obj = torch.load(ckpt, map_location=data["device"])
            data["load_success"] = obj is not None
            data["prior_mode"] = "with_prior" if data["load_success"] else "no_prior"
            data["notes"] = "Checkpoint loaded with torch.load; run wrapper must pass filter arguments to use it."
        except Exception as e:
            data["notes"] = f"Checkpoint load failed: {e!r}"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("PRIOR_MODE=" + data["prior_mode"])
    print("SKETCH_PRIOR_ENABLED=" + str(data["prior_mode"] == "with_prior").lower())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
