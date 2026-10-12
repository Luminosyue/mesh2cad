#!/usr/bin/env python3
"""Frozen entrypoint for EXACT9998 A0/A3 deterministic VAL-only decoding."""
import os
import runpy
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "SpatialLM")]

if "--variant" not in sys.argv:
    raise SystemExit("--variant is required")
variant = sys.argv[sys.argv.index("--variant") + 1]
if variant in ("j2", "j2o", "j2p"):
    os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
    os.environ["CAD_SECOND_STREAM"] = "curve_tokens"
    os.environ["REQUIRE_CURVE_TOKEN_REGISTRY"] = "1"
    os.environ.setdefault(
        "CURVE_TOKEN_REGISTRY",
        str(ROOT / "ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"),
    )
    from spatiallm_curve_token_v1 import curve_token_injector
    curve_token_injector.install()
    # Standard from_pretrained constructs the historical edge projector before
    # loading and silently misses corrected `edge_proj.net.*` weights.  Freeze
    # the training-time construction order: config -> CurveProjector -> strict
    # sharded checkpoint load.
    import torch
    import spatiallm
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from transformers.modeling_utils import load_sharded_checkpoint
    from spatiallm.tuner.framework.patcher import _attach_edge_projector
    from separate_edge_tokens_v1 import common

    def strict_corrected_load(checkpoint, separate_edge=True, device="cuda", dtype=torch.float32, freeze_sonata=True):
        config = AutoConfig.from_pretrained(str(checkpoint))
        model = AutoModelForCausalLM.from_config(config, torch_dtype=dtype)
        _attach_edge_projector(model)
        incompatible = load_sharded_checkpoint(model, str(checkpoint), strict=False, prefer_safe=True)
        allowed_missing = (
            list(incompatible.missing_keys) == ["lm_head.weight"]
            and model.config.tie_word_embeddings
            and model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()
        )
        if (incompatible.missing_keys and not allowed_missing) or incompatible.unexpected_keys:
            raise RuntimeError(f"strict corrected reload failed: {incompatible}")
        model.to(device)
        model.set_point_backbone_dtype(torch.float32)
        if freeze_sonata:
            for p in model.point_backbone.parameters():
                p.requires_grad_(False)
        return model, AutoTokenizer.from_pretrained(str(checkpoint))

    common.load_model = strict_corrected_load

# The frozen decoder implementation is shared byte-for-byte by both arms.
runpy.run_path(str(ROOT / "scripts/geometry_pack_v1/decode_joint_j0_j2.py"), run_name="__main__")
