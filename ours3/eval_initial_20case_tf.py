import importlib
import json
import os
import sys
from pathlib import Path

import torch


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EXP = ROOT / "ours3/p3_xpart_20case_v3_joint_overfit_v1"
CFG = EXP / "config/joint_train_v1.yaml"

sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "SpatialLM")]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer, load_model
from spatiallm.tuner.data import (
    IGNORE_INDEX,
    SFTDataCollatorWith4DAttentionMask,
    get_dataset,
    get_template_and_fix_tokenizer,
    register_spatiallm_templates,
)
import spatiallm.model.spatiallm_llama as llama


sys.argv = ["eval_initial_20case_tf", str(CFG)]
args = read_args()
model_args, data_args, training_args, finetuning_args, generating_args = get_train_args(args)
tokenizer_module = load_tokenizer(model_args)
tokenizer = tokenizer_module["tokenizer"]
register_spatiallm_templates(
    cutoff_len=data_args.cutoff_len,
    num_bins=data_args.num_bins,
    do_augmentation=False,
    random_rotation=False,
)
template = get_template_and_fix_tokenizer(tokenizer, data_args)
dataset = get_dataset(model_args, data_args, training_args)
split = dataset[next(key for key in dataset if "train" in str(key).lower())]
model = load_model(tokenizer, data_args, model_args, finetuning_args, False)
device = torch.device("cuda")
model.to(device).eval()
collator = SFTDataCollatorWith4DAttentionMask(
    template=template,
    model=model,
    pad_to_multiple_of=None,
    label_pad_token_id=IGNORE_INDEX,
    block_diag_attn=model_args.block_diag_attn,
    attn_implementation=getattr(model.config, "_attn_implementation", None),
    compute_dtype=model_args.compute_dtype,
    **tokenizer_module,
)


def audit(lm_head, hidden_states, labels, chunk_size=256, ignore_index=IGNORE_INDEX):
    hidden = hidden_states[:, :-1, :]
    gold = labels[:, 1:]
    errors = []
    valid = 0
    for start in range(0, hidden.shape[1], chunk_size):
        predicted = lm_head(hidden[:, start : start + chunk_size]).argmax(-1)
        target = gold[:, start : start + chunk_size]
        mask = target.ne(ignore_index)
        errors.extend(
            start + int(position)
            for _, position in (predicted.ne(target) & mask).nonzero(as_tuple=False).tolist()
        )
        valid += int(mask.sum())
    audit.last = {
        "errors": errors,
        "valid": valid,
        "full": int(hidden_states.shape[1]),
    }
    return hidden_states.new_zeros(())


llama._chunked_lm_loss = audit
rows = []
with torch.no_grad():
    for index, row in enumerate(split):
        batch = collator([dict(row)])
        batch = {
            key: value.to(device) if torch.is_tensor(value) else value
            for key, value in batch.items()
        }
        model(**batch)
        result = audit.last
        rows.append(
            {
                "case_id": row.get("id", f"case_{index:03d}"),
                "tf_error_n": len(result["errors"]),
                "tf_supervised_token_n": result["valid"],
                "tf_accuracy": 1 - len(result["errors"]) / result["valid"],
                "full_sequence_token_n": result["full"],
            }
        )

output = {
    "checkpoint": model_args.model_name_or_path,
    "description": "20-case TF audit of the unmodified Demo5 frozen warm-start weights",
    "rows": rows,
    "total_errors": sum(row["tf_error_n"] for row in rows),
    "zero_error_case_n": sum(row["tf_error_n"] == 0 for row in rows),
    "max_case_error": max(row["tf_error_n"] for row in rows),
}
(EXP / "tf_eval/INITIAL_20CASE_TF.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({key: value for key, value in output.items() if key != "rows"}))
importlib.reload(llama)
