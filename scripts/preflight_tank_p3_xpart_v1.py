#!/usr/bin/env python3
"""Preflight checks for tank P3-SAM + X-Part run."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART_ROOT = ROOT / "Hunyuan3D-Part" / "XPart"
DEFAULT_CACHE = ROOT / "ours3/.cache/xpart/tencent/Hunyuan3D-Part"
P3_WEIGHTS = ROOT / "Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors"
SONATA = Path.home() / ".cache/sonata/sonata.pth"
TANK_MESH = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"

REQUIRED_WEIGHTS = [
    "model/model.safetensors",
    "conditioner/conditioner.safetensors",
    "shapevae/shapevae.safetensors",
    "p3sam/p3sam.safetensors",
]


def main() -> int:
    cache = Path(os.environ.get("HY3DGEN_MODELS", ROOT / "ours3/.cache/xpart"))
    if cache.name == "Hunyuan3D-Part":
        model_dir = cache
    else:
        model_dir = cache / "tencent/Hunyuan3D-Part"

    checks = []
    for label, path in [
        ("tank_mesh", TANK_MESH),
        ("p3_local_weights", P3_WEIGHTS),
        ("sonata_cache", SONATA),
        ("xpart_code", XPART_ROOT / "partgen/partformer_pipeline.py"),
    ]:
        checks.append({"name": label, "path": str(path), "ok": path.is_file()})

    weight_rows = []
    missing_weights = []
    for rel in REQUIRED_WEIGHTS:
        path = model_dir / rel
        if rel == "p3sam/p3sam.safetensors" and not path.is_file() and P3_WEIGHTS.is_file():
            path = P3_WEIGHTS
        ok = path.is_file()
        size_gb = path.stat().st_size / (1024**3) if ok else None
        weight_rows.append({"file": rel, "path": str(path), "ok": ok, "size_gb": size_gb})
        if not ok:
            missing_weights.append(rel)

    try:
        sys.path.insert(0, str(XPART_ROOT))
        import torch
        from partgen.partformer_pipeline import PartFormerPipeline  # noqa: F401

        import_ok = True
        torch_ok = bool(torch.cuda.is_available())
    except Exception as exc:
        import_ok = False
        torch_ok = False
        import_error = str(exc)
    else:
        import_error = None

    ready = (
        all(row["ok"] for row in checks)
        and not missing_weights
        and import_ok
        and torch_ok
    )

    report = {
        "ready": ready,
        "model_dir": str(model_dir),
        "checks": checks,
        "weights": weight_rows,
        "missing_weights": missing_weights,
        "python_import_ok": import_ok,
        "python_import_error": import_error,
        "cuda_available": torch_ok,
        "next_step": (
            "python scripts/tank_p3_xpart_v1.py --gpu 0"
            if ready
            else "bash scripts/download_hunyuan3d_part_weights.sh  # from a machine with HF access"
        ),
    }
    out = ROOT / "ours3/tank_p3_xpart_v1/artifacts/preflight.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
