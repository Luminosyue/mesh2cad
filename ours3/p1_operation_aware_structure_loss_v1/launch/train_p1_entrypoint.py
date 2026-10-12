#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EXP = ROOT / "ours3/p1_operation_aware_structure_loss_v1"
sys.path[:0] = [
    str(EXP / "source"),
    str(ROOT),
    str(ROOT / "scripts"),
    str(ROOT / "ours3/m2_exact9998_corrected_m2_train_v1/launch"),
    str(ROOT / "SpatialLM"),
]

os.environ.setdefault("CAD_SECOND_STREAM", "curve_tokens")
os.environ.setdefault("CAD_USE_SEPARATE_EDGE_TOKENS", "1")
os.environ.setdefault("CURVE_TOKEN_ROOT", str(ROOT / "ours3/exact9998_curve_tokens_c2_v1"))
os.environ.setdefault(
    "CURVE_TOKEN_REGISTRY",
    str(ROOT / "ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"),
)
os.environ.setdefault("REQUIRE_CURVE_TOKEN_REGISTRY", "1")
os.environ.setdefault("C2_CHECKPOINT_PATH", str(ROOT / "ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"))
os.environ.setdefault("P1_LAMBDA_OP", "1.0")
os.environ.setdefault("P1_RUNTIME_STATS", str(EXP / "audits/P1_RUNTIME_STATS.json"))
os.environ.setdefault("DISABLE_VERSION_CHECK", "1")

import corrected_m2_runtime_audit
import p1_operation_loss_runtime

corrected_m2_runtime_audit.install()
p1_operation_loss_runtime.install()

from spatiallm_curve_token_v1.train_curve_token_spatiallm import main

raise SystemExit(main())
