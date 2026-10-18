# Copyright (c) Manycore Tech Inc. and affiliates.
# All rights reserved.

from typing import List, Optional, Tuple, Union

import torch
import torch.utils.checkpoint
import torch.nn.functional as F
from torch import nn
from transformers import (
    LlamaModel,
    LlamaForCausalLM,
    AutoConfig,
    AutoModelForCausalLM,
)
from transformers.utils import logging
from transformers.cache_utils import Cache
from transformers.modeling_outputs import CausalLMOutputWithPast
from transformers.models.llama.configuration_llama import LlamaConfig

try:
    import torchsparse
    from torchsparse.utils.collate import sparse_collate
except ImportError:
    pass  # Ignore the import error if torchsparse is not installed for SpatialLM1.1

from spatiallm.model import PointBackboneType, ProjectorType

IGNORE_INDEX = -100
logger = logging.get_logger(__name__)


class SpatialLMLlamaConfig(LlamaConfig):
    model_type = "spatiallm_llama"


# separate_edge_tokens_v1: sharp edges travel as a second geometry stream instead
# of as a 7th per-point channel. The markers reuse never-used reserved ids so the
# vocabulary size is untouched and every existing checkpoint still loads.
DEFAULT_EDGE_START_TOKEN_ID = 128014  # <|reserved_special_token_6|>
DEFAULT_EDGE_END_TOKEN_ID = 128015  # <|reserved_special_token_7|>
DEFAULT_EDGE_TOKEN_ID = 128016  # <|reserved_special_token_8|>


def _splice_geometry(cur_embeds, cur_attention_mask, regions):
    """Insert continuous geometry embeddings into one sample's token sequence.

    `regions` is an ascending, non-overlapping list of
    `(start_pos, features, end_pos)`; each region keeps its start marker, drops
    everything between the markers, and substitutes `features`.

    With a single region this reproduces the original surface-only splice
    element for element.
    """
    embed_pieces, mask_pieces = [], []
    cursor = 0
    for start_pos, features, end_pos in regions:
        embed_pieces.append(cur_embeds[cursor : start_pos + 1])
        mask_pieces.append(cur_attention_mask[cursor : start_pos + 1])
        embed_pieces.append(features)
        mask_pieces.append(
            torch.ones(features.shape[0], device=cur_attention_mask.device)
        )
        cursor = end_pos
    embed_pieces.append(cur_embeds[cursor:])
    mask_pieces.append(cur_attention_mask[cursor:])
    return torch.cat(embed_pieces, dim=0), torch.cat(mask_pieces, dim=0)


def _splice_labels(cur_labels, regions, target_len):
    """Mirror `_splice_geometry` on the label row, masking every geometry token."""
    pieces = []
    cursor = 0
    for start_pos, num_patches, end_pos in regions:
        pieces.append(cur_labels[cursor : start_pos + 1])
        pieces.append(
            torch.full((num_patches,), IGNORE_INDEX, device=cur_labels.device)
        )
        cursor = end_pos
    pieces.append(cur_labels[cursor:])
    spliced = torch.cat(pieces, dim=0)
    return F.pad(spliced, (0, target_len - spliced.shape[0]), value=IGNORE_INDEX)


def _single_marker_pos(cur_input_ids, token_id, name):
    hits = torch.where(cur_input_ids == token_id)[0]
    if hits.numel() != 1:
        raise ValueError(
            f"expected exactly one {name} token (id={token_id}), got {hits.numel()}"
        )
    return hits[0]


def _chunked_lm_loss(lm_head, hidden_states, labels, chunk_size=256, ignore_index=IGNORE_INDEX):
    """Causal LM loss without materializing full (B, T, vocab) fp32 logits.

    Long Fusion360 DSL rows OOM in `logits.float()`; scoring 256-token windows
    keeps the CE workspace under ~250MB.
    """
    shift_h = hidden_states[:, :-1, :].contiguous()
    shift_y = labels[:, 1:].contiguous()
    total = hidden_states.new_zeros(())
    n_valid = 0
    seq_len = shift_h.shape[1]
    for start in range(0, seq_len, chunk_size):
        h = shift_h[:, start : start + chunk_size]
        y = shift_y[:, start : start + chunk_size]
        logits = lm_head(h)
        flat_logits = logits.reshape(-1, logits.size(-1)).float()
        flat_y = y.reshape(-1)
        total = total + F.cross_entropy(
            flat_logits, flat_y, ignore_index=ignore_index, reduction="sum"
        )
        n_valid += int((flat_y != ignore_index).sum().item())
        del logits, flat_logits
    if n_valid == 0:
        return hidden_states.new_zeros(())
    return total / n_valid


class SpatialLMLlamaForCausalLM(LlamaForCausalLM):
    config_class = SpatialLMLlamaConfig

    def __init__(self, config):
        super().__init__(config)
        self.model = LlamaModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        self.point_backbone_type = PointBackboneType(config.point_backbone)
        self.point_backbone = None
        point_config = config.point_config
        if self.point_backbone_type == PointBackboneType.SCENESCRIPT:
            from spatiallm.model.scenescript_encoder import PointCloudEncoder

            self.point_backbone = PointCloudEncoder(
                input_channels=point_config["input_channels"],
                d_model=point_config["embed_channels"],
                conv_layers=point_config["conv_layers"],
                num_bins=point_config["num_bins"],
            )
            embed_channels = point_config["embed_channels"]
        elif self.point_backbone_type == PointBackboneType.SONATA:
            from spatiallm.model.sonata_encoder import Sonata

            self.point_backbone = Sonata(
                in_channels=point_config["in_channels"],
                order=point_config["order"],
                stride=point_config["stride"],
                enc_depths=point_config["enc_depths"],
                enc_channels=point_config["enc_channels"],
                enc_num_head=point_config["enc_num_head"],
                enc_patch_size=point_config["enc_patch_size"],
                mlp_ratio=point_config["mlp_ratio"],
                mask_token=point_config["mask_token"],
                enc_mode=point_config["enc_mode"],
                enable_fourier_encode=True,
                num_bins=point_config["num_bins"],
                # Fallback when flash_attn is unavailable in the training env.
                enable_flash=False,
            )
            embed_channels = point_config["enc_channels"][-1]
        else:
            raise ValueError(f"Unknown point backbone type: {self.point_backbone_type}")

        self.projector_type = ProjectorType(getattr(config, "projector", "linear"))
        self.point_proj = self._build_projector(embed_channels, config.hidden_size)

        self.point_start_token_id = self.config.point_start_token_id
        self.point_end_token_id = self.config.point_end_token_id
        self.point_token_id = self.config.point_token_id

        # separate_edge_tokens_v1: a second projector with the same architecture as
        # point_proj but its own parameters. Only instantiated when the experiment
        # is enabled, so baseline checkpoints gain no unexpected keys.
        self.separate_edge_tokens = bool(
            getattr(config, "separate_edge_tokens", False)
        )
        self.edge_start_token_id = getattr(
            config, "edge_start_token_id", DEFAULT_EDGE_START_TOKEN_ID
        )
        self.edge_end_token_id = getattr(
            config, "edge_end_token_id", DEFAULT_EDGE_END_TOKEN_ID
        )
        self.edge_token_id = getattr(config, "edge_token_id", DEFAULT_EDGE_TOKEN_ID)
        self.edge_proj = (
            self._build_projector(embed_channels, config.hidden_size)
            if self.separate_edge_tokens
            else None
        )

        # Initialize weights and apply final processing
        self.post_init()

    def _build_projector(self, embed_channels: int, hidden_size: int) -> nn.Module:
        if self.projector_type == ProjectorType.LINEAR:
            return nn.Linear(embed_channels, hidden_size)
        if self.projector_type == ProjectorType.MLP:
            return nn.Sequential(
                nn.Linear(embed_channels, embed_channels),
                nn.GELU(),
                nn.Linear(embed_channels, hidden_size),
            )
        raise ValueError(f"Unknown projector type: {self.projector_type}")

    def forward_point_cloud(self, point_cloud, device, dtype, projector=None):
        # point cloud has shape (n_points, n_features)
        # find the points that have nan values
        # `projector` defaults to the surface projector; separate_edge_tokens_v1
        # passes self.edge_proj so both streams share one point_backbone.
        projector = self.point_proj if projector is None else projector
        self.point_backbone.to(torch.float32)
        nan_mask = torch.isnan(point_cloud).any(dim=1)
        point_cloud = point_cloud[~nan_mask]
        coords = point_cloud[:, :3].int()
        feats = point_cloud[:, 3:].float()
        if self.point_backbone_type == PointBackboneType.SCENESCRIPT:
            pc_sparse_tensor = torchsparse.SparseTensor(coords=coords, feats=feats)
            pc_sparse_tensor = sparse_collate([pc_sparse_tensor])  # batch_size = 1
            pc_sparse_tensor = pc_sparse_tensor.to(device)
            encoded_features = self.point_backbone(pc_sparse_tensor)
            return projector(encoded_features["context"].to(dtype))
        elif self.point_backbone_type == PointBackboneType.SONATA:
            input_dict = {
                "coord": feats[:, :3].to(device),
                "grid_coord": coords.to(device),
                "feat": feats.to(device),
                "batch": torch.zeros(coords.shape[0], dtype=torch.long).to(device),
            }
            encoded_features = self.point_backbone(input_dict)
            # add the batch dimension
            encoded_features = encoded_features.unsqueeze(0)
            return projector(encoded_features.to(dtype))
        else:
            raise ValueError(f"Unknown point backbone type: {self.point_backbone_type}")

    def forward_geometry(self, surface_points, edge_points=None, device=None, dtype=None):
        """Encode one sample's geometry streams into LLM-space token embeddings.

        `edge_points=None` reproduces the surface-only path exactly. When edge
        points are supplied they run through the *same* `point_backbone` and a
        separate `edge_proj`.

        Returns `(surface_tokens, edge_tokens_or_None)`, each `(1, K, hidden)`.
        """
        surface_tokens = self.forward_point_cloud(
            surface_points, device, dtype, projector=self.point_proj
        )
        if edge_points is None:
            return surface_tokens, None
        if self.edge_proj is None:
            raise ValueError(
                "edge_points supplied but edge_proj is missing; enable "
                "separate_edge_tokens on the config before loading the model."
            )
        edge_tokens = self.forward_point_cloud(
            edge_points, device, dtype, projector=self.edge_proj
        )
        return surface_tokens, edge_tokens

    def set_point_backbone_dtype(self, dtype: torch.dtype):
        for param in self.point_backbone.parameters():
            param.data = param.data.to(dtype)

    def get_model(self):
        return self.model

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        num_logits_to_keep: int = 0,
        point_clouds: Optional[torch.Tensor] = None,
        edge_clouds: Optional[torch.Tensor] = None,
        **loss_kwargs,
    ) -> Union[Tuple, CausalLMOutputWithPast]:
        r"""
        Args:
            labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
                Labels for computing the masked language modeling loss. Indices should either be in `[0, ...,
                config.vocab_size]` or -100 (see `input_ids` docstring). Tokens with indices set to `-100` are ignored
                (masked), the loss is only computed for the tokens with labels in `[0, ..., config.vocab_size]`.

            point_clouds (`torch.Tensor` of shape `(batch_size, n_points, n_features)`, *optional*):
                Point clouds to be used for the point cloud encoder.

            num_logits_to_keep (`int`, *optional*):
                Calculate logits for the last `num_logits_to_keep` tokens. If `0`, calculate logits for all
                `input_ids` (special case). Only last token logits are needed for generation, and calculating them only for that
                token can save memory, which becomes pretty significant for long sequences or large vocabulary size.

        Returns:

        Example:

        ```python
        >>> from transformers import AutoTokenizer, AutoModelForCausalLM

        >>> model = AutoModelForCausalLM.from_pretrained("manycore-research/SpatialLM-Llama-1B")
        >>> tokenizer = AutoTokenizer.from_pretrained("manycore-research/SpatialLM-Llama-1B")

        >>> prompt = "<|point_start|><|point_pad|><|point_end|>Detect walls, doors, windows, boxes. The reference code is as followed: {code_template}"
        >>> conversation = [{"role": "user", "content": prompt}]
        >>> input_ids = tokenizer.apply_chat_template(conversation, add_generation_prompt=True, return_tensors="pt")

        >>> # Generate
        >>> generate_ids = model.generate(input_ids, point_clouds=point_clouds, max_length=4096)
        >>> tokenizer.batch_decode(generate_ids, skip_prompt=True, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        ```"""
        output_attentions = (
            output_attentions
            if output_attentions is not None
            else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        # compute point cloud embeddings
        if inputs_embeds is None:
            inputs_embeds = self.model.embed_tokens(input_ids)

        if (
            self.point_backbone is not None
            and (input_ids.shape[1] != 1 or self.training)
            and point_clouds is not None
        ):
            use_edge_stream = edge_clouds is not None and self.edge_proj is not None
            n_point_clouds = point_clouds.shape[0]
            point_features = []
            edge_features = []
            for i in range(n_point_clouds):  # * iterate over batch
                point_cloud = point_clouds[i]
                edge_cloud = edge_clouds[i] if use_edge_stream else None
                point_feature, edge_feature = self.forward_geometry(
                    point_cloud,
                    edge_cloud,
                    inputs_embeds.device,
                    inputs_embeds.dtype,
                )
                point_features.append(point_feature)
                edge_features.append(edge_feature)

            # Insert point cloud features into the input ids
            point_start_end_token_pos = []
            new_input_embeds = []
            new_attention_mask = []
            cur_point_idx = 0
            max_num_tokens = 0
            for cur_input_ids, cur_input_embeds, cur_attention_mask in zip(
                input_ids, inputs_embeds, attention_mask
            ):  # * input_ids: B, L; input_embeds: B, L, C
                cur_point_features = (
                    point_features[cur_point_idx]
                    .to(device=cur_input_embeds.device)
                    .squeeze(0)
                )
                num_patches = cur_point_features.shape[0]  # * number of point tokens
                num_point_start_tokens = (
                    (cur_input_ids == self.config.point_start_token_id).sum().item()
                )
                num_point_end_tokens = (
                    (cur_input_ids == self.config.point_end_token_id).sum().item()
                )
                # currently, we only support one point start and one point end token
                assert num_point_start_tokens == num_point_end_tokens == 1, (
                    "The number of point start tokens and point end tokens should be 1, "
                    f"but got {num_point_start_tokens} and {num_point_end_tokens}."
                )
                point_start_token_pos = torch.where(
                    cur_input_ids == self.config.point_start_token_id
                )[0][0]
                point_end_token_pos = torch.where(
                    cur_input_ids == self.config.point_end_token_id
                )[0][0]

                embed_regions = [
                    (point_start_token_pos, cur_point_features, point_end_token_pos)
                ]
                label_regions = [
                    (point_start_token_pos, num_patches, point_end_token_pos)
                ]
                if use_edge_stream:
                    cur_edge_features = (
                        edge_features[cur_point_idx]
                        .to(device=cur_input_embeds.device)
                        .squeeze(0)
                    )
                    edge_start_pos = _single_marker_pos(
                        cur_input_ids, self.edge_start_token_id, "edge start"
                    )
                    edge_end_pos = _single_marker_pos(
                        cur_input_ids, self.edge_end_token_id, "edge end"
                    )
                    if edge_start_pos <= point_end_token_pos:
                        raise ValueError(
                            "the edge region must follow the surface region: "
                            f"edge_start={int(edge_start_pos)} <= point_end={int(point_end_token_pos)}"
                        )
                    embed_regions.append(
                        (edge_start_pos, cur_edge_features, edge_end_pos)
                    )
                    label_regions.append(
                        (edge_start_pos, cur_edge_features.shape[0], edge_end_pos)
                    )

                cur_new_input_embeds, cur_new_attention_mask = _splice_geometry(
                    cur_input_embeds, cur_attention_mask, embed_regions
                )

                cur_point_idx += 1
                new_input_embeds.append(cur_new_input_embeds)
                new_attention_mask.append(cur_new_attention_mask)
                point_start_end_token_pos.append(label_regions)
                if cur_new_input_embeds.shape[0] > max_num_tokens:
                    max_num_tokens = cur_new_input_embeds.shape[0]
            # pad the new input embeds and attention mask to the max dimension
            for i in range(len(new_input_embeds)):
                cur_input_embeds = new_input_embeds[i]
                last_row = cur_input_embeds[-1]
                padding = last_row.repeat(max_num_tokens - cur_input_embeds.shape[0], 1)
                new_input_embeds[i] = torch.cat([cur_input_embeds, padding], dim=0)

                cur_attention_mask = new_attention_mask[i]
                new_attention_mask[i] = F.pad(
                    cur_attention_mask,
                    (0, max_num_tokens - cur_attention_mask.shape[0]),
                    value=0,
                )
            inputs_embeds = torch.stack(new_input_embeds, dim=0)
            attention_mask = torch.stack(new_attention_mask, dim=0)

            assert (
                attention_mask.shape[1] == inputs_embeds.shape[1]
            ), "The length of attention mask and inputs embeds should be the same"

        # decoder outputs consists of (dec_features, layer_state, dec_hidden, dec_attn)
        outputs = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            cache_position=cache_position,
        )

        hidden_states = outputs[0]
        loss = None
        logits = None
        if labels is not None:
            new_labels = []
            max_num_tokens = hidden_states.shape[1]
            for i in range(len(point_start_end_token_pos)):
                # Every geometry region (surface, and edge when enabled) is
                # masked out; only the CAD target contributes to the loss.
                new_labels.append(
                    _splice_labels(
                        labels[i], point_start_end_token_pos[i], max_num_tokens
                    )
                )
            labels = torch.stack(new_labels, dim=0)
            assert (
                labels.shape[1] == hidden_states.shape[1]
            ), "The length of labels and hidden states should be the same"
            loss = _chunked_lm_loss(self.lm_head, hidden_states, labels)
        elif self.config.pretraining_tp > 1:
            lm_head_slices = self.lm_head.weight.split(
                self.vocab_size // self.config.pretraining_tp, dim=0
            )
            logits = [
                F.linear(hidden_states, lm_head_slices[i])
                for i in range(self.config.pretraining_tp)
            ]
            logits = torch.cat(logits, dim=-1)
        else:
            logits = self.lm_head(hidden_states[:, -num_logits_to_keep:, :])

        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    def prepare_inputs_for_generation(
        self,
        input_ids,
        past_key_values=None,
        attention_mask=None,
        inputs_embeds=None,
        **kwargs,
    ):
        if past_key_values:
            input_ids = input_ids[:, -1:]

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
                "point_clouds": kwargs.get("point_clouds", None),
                "edge_clouds": kwargs.get("edge_clouds", None),
            }
        )
        return model_inputs


AutoConfig.register("spatiallm_llama", SpatialLMLlamaConfig)
AutoModelForCausalLM.register(SpatialLMLlamaConfig, SpatialLMLlamaForCausalLM)
