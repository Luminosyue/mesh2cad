#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EXP = ROOT / "ours3/p1v2_cadfit_improvement_v1"
SIZE_IMPL = ROOT / "ours3/p1v2_parameter_supervision_preparation_v1/implementation"
sys.path[:0] = [
    str(SIZE_IMPL),
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
os.environ.setdefault(
    "C2_CHECKPOINT_PATH",
    str(ROOT / "ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"),
)
os.environ.setdefault("P1V2_LAMBDA_SIZE", "0.5")
os.environ.setdefault("P1_RUNTIME_STATS", str(EXP / "audits/runtime_stats.json"))
os.environ.setdefault("ZERO_LR_AUDIT_PATH", str(EXP / "audits/zero_lr_step.json"))
os.environ.setdefault(
    "EFFECTIVE_UPDATE_AUDIT_PATH", str(EXP / "audits/first_effective_update.json")
)
os.environ.setdefault("DISABLE_VERSION_CHECK", "1")

import corrected_m2_runtime_audit  # noqa: E402
import p2_size_loss_runtime  # noqa: E402

corrected_m2_runtime_audit.install()
p2_size_loss_runtime.install()

# HF constructs the model before the runtime CurveProjector is attached, so its
# four checkpoint tensors are otherwise reported as unused. Restore those
# tensors after the standard loader attaches the projector and before training.
import spatiallm.tuner.trainer as trainer_module  # noqa: E402
from safetensors.torch import load_file  # noqa: E402


def _tensor_hash(state: dict) -> str:
    digest = hashlib.sha256()
    for key, tensor in sorted(state.items()):
        digest.update(key.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


_standard_load_model = trainer_module.load_model


def _load_model_with_projector_restore(*args, **kwargs):
    model = _standard_load_model(*args, **kwargs)
    model_args = args[2] if len(args) > 2 else kwargs["model_args"]
    checkpoint = Path(model_args.model_name_or_path)
    edge_state = {}
    for shard in sorted(checkpoint.glob("model-*-of-*.safetensors")):
        for key, tensor in load_file(str(shard), device="cpu").items():
            if key.startswith("edge_proj."):
                edge_state[key.removeprefix("edge_proj.")] = tensor
    expected = set(model.edge_proj.state_dict())
    if set(edge_state) != expected:
        raise RuntimeError(
            f"strict projector restore schema mismatch: source={sorted(edge_state)} "
            f"model={sorted(expected)}"
        )
    source_hash = _tensor_hash(edge_state)
    before_hash = _tensor_hash(model.edge_proj.state_dict())
    model.edge_proj.load_state_dict(edge_state, strict=True)
    after_hash = _tensor_hash(model.edge_proj.state_dict())
    audit = {
        "checkpoint": str(checkpoint),
        "edge_key_count": len(edge_state),
        "source_hash": source_hash,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "strict_restore_pass": source_hash == after_hash and source_hash != before_hash,
    }
    (EXP / "audits/projector_restore.json").write_text(json.dumps(audit, indent=2) + "\n")
    if not audit["strict_restore_pass"]:
        raise RuntimeError(f"strict projector restore failed: {audit}")
    return model


trainer_module.load_model = _load_model_with_projector_restore

from spatiallm_curve_token_v1.train_curve_token_spatiallm import main  # noqa: E402

raise SystemExit(main())
