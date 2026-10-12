#!/usr/bin/env python3
"""Check the Curve Token stream end to end before spending GPU hours.

Verifies, on real subset records:
  1. the patched plugin returns (surface [N,9], curve tokens [K,256])
  2. NaN batch padding is stripped so each sample keeps its own K
  3. the CurveProjector maps [K,256] → [1,K,2048]
  4. the prompt carries the surface AND second-stream markers in the right order
  5. the sequence budget: surface voxel tokens vs curve tokens vs cutoff_len
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = REPO_ROOT / "SpatialLM"
for p in (str(SPATIALLM_ROOT), str(REPO_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("CAD_USE_SEPARATE_EDGE_TOKENS", "1")
os.environ.setdefault("CAD_SECOND_STREAM", "curve_tokens")

from spatiallm_curve_token_v1 import curve_token_injector  # noqa: E402
from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_TOKEN_DIM,
    LLM_HIDDEN_SIZE,
    SUBSET_DIR,
)
from spatiallm_curve_token_v1.curve_projector import build_curve_projector  # noqa: E402


def main() -> int:
    curve_token_injector.install()
    from spatiallm.tuner.data.mm_plugin import (
        EDGE_E_TOKEN,
        EDGE_PAD_TOKEN,
        EDGE_S_TOKEN,
        POINT_E_TOKEN,
        POINT_S_TOKEN,
        get_cad_mm_plugin,
    )

    plugin = get_cad_mm_plugin(
        point_token="<|point_pad|>",
        num_bins=1280,
        use_edge_score=False,
        separate_edge_tokens=True,
    )

    rows = json.loads((SUBSET_DIR / "curve100_train.json").read_text(encoding="utf-8"))
    media_dir = REPO_ROOT / "cad_spatial_dataset"
    checked = []
    for row in rows[:6]:
        surface_path = media_dir / row["point_clouds"][0]
        surface, curve = plugin._load_cad_separate_edge(str(surface_path))
        assert surface.ndim == 2 and surface.shape[1] == 9, surface.shape
        assert curve.ndim == 2 and curve.shape[1] == CURVE_TOKEN_DIM, curve.shape
        checked.append(
            {"id": row["id"], "surface_voxels": int(len(surface)), "curve_tokens": int(len(curve))}
        )
    print("[1-2] plugin returns per-sample shapes:")
    for c in checked:
        print(f"      {c['id']}: surface {c['surface_voxels']} voxels, "
              f"{c['curve_tokens']} curve tokens")

    # NaN padding across a batch, exactly as the collator does
    from spatiallm.tuner.data.mm_plugin import _pad_stack_clouds

    curves = [
        plugin._load_cad_separate_edge(str(media_dir / r["point_clouds"][0]))[1]
        for r in rows[:4]
    ]
    batch = _pad_stack_clouds(curves)
    print(f"[3] padded batch {tuple(batch.shape)} "
          f"(true K = {[len(c) for c in curves]})")

    projector = build_curve_projector(CURVE_TOKEN_DIM, LLM_HIDDEN_SIZE)
    for i, c in enumerate(curves):
        feats = batch[i]
        feats = feats[~torch.isnan(feats).any(dim=1)]
        assert len(feats) == len(c), f"NaN strip changed K: {len(feats)} vs {len(c)}"
        out = projector(feats.float()).unsqueeze(0)
        assert out.shape == (1, len(c), LLM_HIDDEN_SIZE), out.shape
    print(f"[3] CurveProjector: [K,{CURVE_TOKEN_DIM}] -> [1,K,{LLM_HIDDEN_SIZE}] ok, "
          f"{sum(p.numel() for p in projector.parameters()):,} params")

    # marker order in the prompt
    msgs = [{"role": "user", "content": rows[0]["conversations"][0]["value"]}]
    processed = plugin.process_messages(
        msgs,
        [{"angle_z": 0.0, "center_pt": np.zeros(3), "scaling": 1.0,
          "min_bound": np.zeros(3), "transformed_points": np.zeros((1, 3))}],
    )
    content = processed[0]["content"]
    pos = {
        name: content.index(tok)
        for name, tok in (
            ("point_start", POINT_S_TOKEN), ("point_end", POINT_E_TOKEN),
            ("edge_start", EDGE_S_TOKEN), ("edge_pad", EDGE_PAD_TOKEN),
            ("edge_end", EDGE_E_TOKEN),
        )
    }
    assert pos["point_start"] < pos["point_end"] < pos["edge_start"] < pos["edge_end"], pos
    print(f"[4] marker order ok: {sorted(pos, key=pos.get)}")

    # sequence budget
    surf = [c["surface_voxels"] for c in checked]
    crv = [c["curve_tokens"] for c in checked]
    print(f"[5] budget: surface {min(surf)}-{max(surf)} tokens, "
          f"curve {min(crv)}-{max(crv)} tokens, cutoff_len = 2048")
    print("OK — curve token stream wired correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
