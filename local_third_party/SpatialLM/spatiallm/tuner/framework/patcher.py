# Copyright 2025 the LlamaFactory team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from types import MethodType
from typing import TYPE_CHECKING, Any

import os

import torch
from transformers import GenerationMixin, PreTrainedModel, PreTrainedTokenizerBase
from transformers.integrations import is_deepspeed_zero3_enabled
from transformers.utils import is_torch_bf16_gpu_available, is_torch_npu_available

from . import logging

try:
    _is_bf16_available = is_torch_bf16_gpu_available() or (
        is_torch_npu_available() and torch.npu.is_bf16_supported()
    )
except Exception:
    _is_bf16_available = False

from ..network.attention import configure_attn_implementation
from ..network.checkpointing import prepare_model_for_training
from ..network.rope import configure_rope

if TYPE_CHECKING:
    from transformers import PretrainedConfig, PreTrainedTokenizer, ProcessorMixin

    from ..hparams import ModelArguments


logger = logging.get_logger(__name__)


def _widen_point_stem_for_edge(model: "PreTrainedModel") -> None:
    """Widen Sonata stem 6→7 channels for xyz+normal+edge_score CAD input."""
    import sys
    from pathlib import Path

    mesh2cad = Path(__file__).resolve().parents[4]
    scripts = str(mesh2cad / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from spatiallm_cad_frontend import widen_embedding_stem  # noqa: WPS433

    stem = model.point_backbone.embedding.stem.linear
    if stem.in_features == 7:
        logger.info_rank0("Point stem already 7-channel; skip widening.")
        return
    edge_init = os.environ.get("CAD_STEM_EDGE_INIT", "rgb_mean")
    stem_seed = int(os.environ.get("CAD_STEM_SEED", "0"))
    generator = torch.Generator(device="cpu").manual_seed(stem_seed)
    model.point_backbone.embedding.stem.linear = widen_embedding_stem(
        stem, edge_init=edge_init, generator=generator
    )
    model.point_backbone.embedding.in_channels = 7
    model.config.point_config["in_channels"] = 7
    logger.info_rank0(
        f"Widened point encoder stem to 7 channels (edge_init={edge_init}, seed={stem_seed})."
    )


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "0").lower() in ("1", "true", "yes")


def _attach_edge_projector(model: "PreTrainedModel") -> None:
    """Give the model a separate edge projector for separate_edge_tokens_v1.

    Architecture is copied from the surface projector and the weights are
    initialized from it, but the parameters are independent from that point on.
    The shared Sonata backbone is left completely untouched (still 6-channel).
    """
    import copy

    if getattr(model, "edge_proj", None) is not None:
        logger.info_rank0("Edge projector already present; skip attaching.")
        return

    stem = model.point_backbone.embedding.stem.linear
    if stem.in_features != 6:
        raise ValueError(
            "separate_edge_tokens_v1 requires the pretrained 6-channel Sonata stem, "
            f"but found in_features={stem.in_features}."
        )

    init_mode = os.environ.get("SEPEDGE_PROJECTOR_INIT", "copy_of_surface_projector")
    if init_mode == "copy_of_surface_projector":
        model.edge_proj = copy.deepcopy(model.point_proj)
    elif init_mode == "random":
        model.edge_proj = model._build_projector(
            model.point_proj[0].in_features
            if isinstance(model.point_proj, torch.nn.Sequential)
            else model.point_proj.in_features,
            model.config.hidden_size,
        )
    else:
        raise ValueError(f"unknown SEPEDGE_PROJECTOR_INIT={init_mode!r}")

    model.edge_proj = model.edge_proj.to(
        device=next(model.point_proj.parameters()).device,
        dtype=next(model.point_proj.parameters()).dtype,
    )
    model.separate_edge_tokens = True
    model.config.separate_edge_tokens = True
    model.config.edge_start_token_id = model.edge_start_token_id
    model.config.edge_end_token_id = model.edge_end_token_id
    model.config.edge_token_id = model.edge_token_id

    surface_ids = {id(p) for p in model.point_proj.parameters()}
    edge_ids = {id(p) for p in model.edge_proj.parameters()}
    if surface_ids & edge_ids:
        raise RuntimeError("edge projector shares parameters with the surface projector")

    logger.info_rank0(
        f"Attached separate edge projector (init={init_mode}, shared=False); "
        "Sonata stem left at 6 channels."
    )


def patch_tokenizer(
    tokenizer: "PreTrainedTokenizer", model_args: "ModelArguments"
) -> None:
    if "PreTrainedTokenizerBase" not in str(tokenizer._pad.__func__):
        tokenizer._pad = MethodType(PreTrainedTokenizerBase._pad, tokenizer)

    if (
        model_args.model_max_length is not None
        and tokenizer.model_max_length < model_args.model_max_length
    ):
        tokenizer.model_max_length = (
            model_args.model_max_length
        )  # enlarge the tokenizer max length

    if model_args.add_tokens is not None:
        num_added_tokens = tokenizer.add_tokens(
            new_tokens=model_args.add_tokens, special_tokens=False
        )
        logger.info_rank0(
            "Add tokens {} to tokenizer's vocabulary.".format(
                ",".join(model_args.add_tokens)
            )
        )
        if num_added_tokens > 0 and not model_args.resize_vocab:
            model_args.resize_vocab = True
            logger.warning_rank0(
                "New tokens have been added, changed `resize_vocab` to True."
            )

    if model_args.add_special_tokens is not None:
        num_added_special_tokens = tokenizer.add_tokens(
            new_tokens=model_args.add_special_tokens, special_tokens=True
        )
        logger.info_rank0(
            "Add special tokens {} to tokenizer's vocabulary.".format(
                ",".join(model_args.add_special_tokens)
            )
        )
        if num_added_special_tokens > 0 and not model_args.resize_vocab:
            model_args.resize_vocab = True
            logger.warning_rank0(
                "New special tokens have been added, changed `resize_vocab` to True."
            )


def patch_processor(
    processor: "ProcessorMixin",
    tokenizer: "PreTrainedTokenizer",
) -> None:
    setattr(processor, "tokenizer", tokenizer)


def patch_config(
    config: "PretrainedConfig",
    model_args: "ModelArguments",
    init_kwargs: dict[str, Any],
    is_trainable: bool,
) -> None:
    if model_args.compute_dtype is None:  # priority: bf16 > fp32
        if model_args.infer_dtype != "auto" and not is_trainable:
            model_args.compute_dtype = getattr(torch, model_args.infer_dtype)
        elif (
            _is_bf16_available
            and getattr(config, "torch_dtype", None) == torch.bfloat16
        ):
            model_args.compute_dtype = torch.bfloat16
        else:
            model_args.compute_dtype = torch.float32

    configure_attn_implementation(config, model_args)
    configure_rope(config, model_args)

    if getattr(config, "model_type", None) == "qwen":
        setattr(config, "use_flash_attn", model_args.flash_attn == "fa2")
        for dtype_name, dtype in [
            ("bf16", torch.bfloat16),
            ("fp32", torch.float32),
        ]:
            setattr(config, dtype_name, model_args.compute_dtype == dtype)

    # deepspeed zero3 is not compatible with low_cpu_mem_usage
    init_kwargs["low_cpu_mem_usage"] = model_args.low_cpu_mem_usage and (
        not is_deepspeed_zero3_enabled()
    )


def patch_model(
    model: "PreTrainedModel",
    model_args: "ModelArguments",
    is_trainable: bool,
) -> None:
    gen_config = model.generation_config  # check and fix generation config
    if not gen_config.do_sample and (
        (gen_config.temperature is not None and gen_config.temperature != 1.0)
        or (gen_config.top_p is not None and gen_config.top_p != 1.0)
        or (gen_config.typical_p is not None and gen_config.typical_p != 1.0)
    ):
        gen_config.do_sample = True

    if "GenerationMixin" not in str(model.generate.__func__):
        model.generate = MethodType(GenerationMixin.generate, model)

    if is_trainable:
        prepare_model_for_training(model, model_args)

    use_edge_score = _env_flag("CAD_USE_EDGE_SCORE")
    use_separate_edge = _env_flag("CAD_USE_SEPARATE_EDGE_TOKENS")
    if use_edge_score and use_separate_edge:
        raise ValueError(
            "CAD_USE_EDGE_SCORE and CAD_USE_SEPARATE_EDGE_TOKENS "
            "cannot be enabled simultaneously in V1."
        )

    if use_edge_score:
        _widen_point_stem_for_edge(model)
    if use_separate_edge:
        _attach_edge_projector(model)

    try:
        model.add_model_tags(["spatiallm"])
    except Exception:
        logger.warning_rank0("Cannot properly tag the model.")
