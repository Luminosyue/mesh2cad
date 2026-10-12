#!/usr/bin/env python3
"""Train one held-out SpatialLM arm (B0 / B1-native / B1-budget-match / M2).

Installs runtime patches, registers EarlyStoppingCallback, then hands over to
SpatialLM ``run_exp``. After training, verifies that the best-val checkpoint
was reloaded and persists it to ``<output_dir>/best_model/``.

Environment (set by run_heldout.sh / run_heldout_best_v2.sh):
  CAD_SURFACE_POINTS=4096          always
  CAD_HELDOUT_PROTOCOL=best_v2     formal Gate (cache + early stop + best_model)
  CAD_USE_SEPARATE_EDGE_TOKENS     B1* / M2
  CAD_EDGE_SOURCE=gt_sharp         B1*
  CAD_EDGE_BUDGET_MATCH=1          B1-budget-match only
  CAD_SECOND_STREAM=curve_tokens   M2 only
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = REPO_ROOT / "SpatialLM"
for p in (str(SPATIALLM_ROOT), str(REPO_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

FORBIDDEN_INIT_MARKERS = (
    "curve100",
    "heldout_curve_b0",
    "heldout_curve_b1",
    "heldout_curve_m2",
)


def _read_yaml_model_path(config: Path) -> str:
    for line in config.read_text(encoding="utf-8").splitlines():
        if line.startswith("model_name_or_path:"):
            return line.split(":", 1)[1].strip()
    return ""


def _guard_init_checkpoint(config: Path) -> None:
    model_path = _read_yaml_model_path(config)
    lowered = model_path.lower()
    for marker in FORBIDDEN_INIT_MARKERS:
        if marker in lowered:
            raise SystemExit(
                f"refusing to initialize from {model_path!r} "
                f"(marker {marker!r}). Formal Gate must start from the original "
                "SpatialLM base weights."
            )
    if os.environ.get("CAD_ALLOW_RESUME", "").strip() not in {"1", "true", "yes"}:
        # Extra belt: do not pass HF resume via env.
        os.environ.pop("RESUME_FROM_CHECKPOINT", None)


def _min_eval_loss(log_history: list[dict]) -> tuple[int | None, float | None]:
    best_step, best_loss = None, None
    for h in log_history:
        if "eval_loss" not in h:
            continue
        loss = float(h["eval_loss"])
        step = int(h.get("step", -1))
        if best_loss is None or loss < best_loss:
            best_loss, best_step = loss, step
    return best_step, best_loss


def _step_from_checkpoint(path: str | None) -> int | None:
    if not path:
        return None
    name = Path(path).name
    if name.startswith("checkpoint-"):
        try:
            return int(name.split("-", 1)[1])
        except ValueError:
            return None
    return None


def finalize_best_model(trainer) -> None:
    """Verify best-val selection and persist ``<output_dir>/best_model/``."""
    output_dir = Path(trainer.args.output_dir)
    state = trainer.state
    best_ckpt = getattr(state, "best_model_checkpoint", None)
    best_metric = getattr(state, "best_metric", None)
    log_step, log_loss = _min_eval_loss(list(state.log_history or []))
    ckpt_step = _step_from_checkpoint(best_ckpt)
    best_step = getattr(state, "best_global_step", None) or ckpt_step or log_step

    errors: list[str] = []
    if not trainer.args.load_best_model_at_end:
        errors.append("load_best_model_at_end is False")
    if not best_ckpt:
        errors.append("trainer_state.best_model_checkpoint is empty")
    elif not Path(best_ckpt).is_dir():
        errors.append(f"best checkpoint directory does not exist: {best_ckpt}")
    if best_metric is None:
        errors.append("trainer_state.best_metric is None")
    if log_loss is None:
        errors.append("no eval_loss in trainer_state.log_history")
    elif best_metric is not None and abs(float(best_metric) - float(log_loss)) > 1e-5:
        errors.append(
            f"best_metric={best_metric} != min eval_loss={log_loss} (step {log_step})"
        )
    if ckpt_step is not None and log_step is not None and ckpt_step != log_step:
        errors.append(
            f"best checkpoint step {ckpt_step} != log min-eval step {log_step}"
        )

    selection = {
        "selection_metric": "eval_loss",
        "best_metric": None if best_metric is None else float(best_metric),
        "best_step": None if best_step is None else int(best_step),
        "best_checkpoint": best_ckpt,
        "test_used_for_selection": False,
        "load_best_model_at_end": bool(trainer.args.load_best_model_at_end),
        "early_stopping_patience": int(os.environ.get("CAD_ES_PATIENCE", "4")),
        "early_stopping_threshold": float(os.environ.get("CAD_ES_THRESHOLD", "0.0")),
        "global_step": int(state.global_step),
        "max_steps": int(state.max_steps) if state.max_steps else None,
        "log_min_eval_loss": log_loss,
        "log_min_eval_step": log_step,
        "protocol": os.environ.get("CAD_HELDOUT_PROTOCOL", ""),
        "init_from_test": False,
        "keep_forever": True,
    }
    if errors:
        selection["errors"] = errors
        (output_dir / "selection_FAILED.json").write_text(
            json.dumps(selection, indent=2) + "\n", encoding="utf-8"
        )
        raise RuntimeError(
            "best-model checks failed:\n  - " + "\n  - ".join(errors)
        )

    best_dir = output_dir / "best_model"
    best_dir.mkdir(parents=True, exist_ok=True)
    # Model in memory is the reloaded best checkpoint when load_best_model_at_end.
    trainer.save_model(str(best_dir))
    keep = best_dir / "DO_NOT_DELETE"
    keep.write_text(
        "best-val model selected by eval_loss; never delete this directory.\n",
        encoding="utf-8",
    )
    (best_dir / "selection.json").write_text(
        json.dumps(selection, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "selection.json").write_text(
        json.dumps(selection, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"[best_model] saved {best_dir} "
        f"(step={best_step} eval_loss={best_metric} from {best_ckpt})",
        flush=True,
    )


def _patch_trainer_with_early_stopping() -> None:
    from transformers import EarlyStoppingCallback
    from spatiallm.tuner import trainer as slm_trainer

    patience = int(os.environ.get("CAD_ES_PATIENCE", "4"))
    threshold = float(os.environ.get("CAD_ES_THRESHOLD", "0.0"))
    orig_run_sft = slm_trainer.run_sft
    orig_cls = slm_trainer.CustomSeq2SeqTrainer

    class GuardedTrainer(orig_cls):
        def train(self, *args, **kwargs):
            result = super().train(*args, **kwargs)
            if os.environ.get("CAD_HELDOUT_PROTOCOL", "").strip().lower() in {
                "best_v2",
                "heldout_best_v2",
                "1",
                "true",
            }:
                finalize_best_model(self)
            return result

    def run_sft_with_es(
        model_args,
        data_args,
        training_args,
        finetuning_args,
        generating_args,
        callbacks=None,
    ):
        cb = list(callbacks or [])
        cb.append(
            EarlyStoppingCallback(
                early_stopping_patience=patience,
                early_stopping_threshold=threshold,
            )
        )
        print(
            f"[early_stopping] EarlyStoppingCallback("
            f"patience={patience}, threshold={threshold}) "
            f"load_best_model_at_end={training_args.load_best_model_at_end} "
            f"metric={training_args.metric_for_best_model}",
            flush=True,
        )
        return orig_run_sft(
            model_args,
            data_args,
            training_args,
            finetuning_args,
            generating_args,
            cb,
        )

    slm_trainer.CustomSeq2SeqTrainer = GuardedTrainer
    slm_trainer.run_sft = run_sft_with_es


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(f"usage: {sys.argv[0]} <config.yaml>")
    config = Path(sys.argv[1]).resolve()
    if not config.is_file():
        raise SystemExit(f"config not found: {config}")

    os.chdir(SPATIALLM_ROOT)
    _guard_init_checkpoint(config)

    if os.environ.get("CAD_SECOND_STREAM", "").strip().lower() == "curve_tokens":
        from spatiallm_curve_token_v1 import curve_token_injector

        curve_token_injector.install()

    from spatiallm_curve_token_v1 import heldout_geometry

    heldout_geometry.install()
    if os.environ.get("CAD_HELDOUT_PROTOCOL", "").strip().lower() in {
        "best_v2",
        "heldout_best_v2",
        "1",
        "true",
    }:
        _patch_trainer_with_early_stopping()

    from spatiallm.tuner.trainer import run_exp

    sys.argv = [sys.argv[0], str(config)]
    run_exp()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
