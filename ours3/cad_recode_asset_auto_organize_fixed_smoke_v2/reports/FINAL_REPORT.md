# CAD_RECODE_LOCAL_ASSET_AUTO_ORGANIZE_AND_FIXED_SMOKE_V2

CURRENT_GATE = CAD_RECODE_ASSET_IDENTITY_AMBIGUOUS
RAW_EXTERNAL_CHECKPOINT_ROOT = /data/home/cuiyuehan/project/mesh2cad/external_checkpoints/
QWEN_TOKENIZER_ROOT = /data/home/cuiyuehan/project/mesh2cad/external_checkpoints/qwen2_1_5b_tokenizer_clean/
CAD_RECODE_ROOT = absent (no verified CAD-Recode snapshot)

Qwen tokenizer suffix-normalized copies were created with hash-preserving copy only; local-only tokenizer load PASS. The top-level config/model group is Qwen2 (`Qwen2Config`, `MyQwen2ForCausalLM`), not a confirmed CAD-Recode model. Generated CAD-Recode copies were removed and original downloads preserved.

CONFIG_LOAD = NOT_RUN
TOKENIZER_LOAD = PASS
MODEL_LOAD = NOT_RUN
SMOKE_CASE_ID = deepcad__0009_00095135
INFERENCE_STATUS = NOT_RUN
CAD_RECODE_VAL_READY = NO
TEST1000_REUSED = NO
HOLDOUT958_PREDICTION_N = 0
GPU3_TOUCHED = NO
P1V2_FULL_TRAIN_MODIFIED = NO
NEXT_ALLOWED_STAGE = provide verifiable official CAD-Recode snapshot/config, then rerun identity and model-load gates
