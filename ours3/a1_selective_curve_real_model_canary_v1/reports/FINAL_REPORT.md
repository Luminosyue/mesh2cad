# A1-SCF Real-Model Canary — environment blocked

`CURRENT_GATE = A1_SCF_CANARY_ENVIRONMENT_BLOCKED`

The one-shot GPU gate selected GPU 2 safely. The official SpatialLM import then failed before model loading because the frozen `cadfit-env` resolved user-site `transformers/huggingface_hub`, whose `hf_api` could not import `requests`.

No forward, backward, selector-gradient test, TRAIN100, VAL100, or checkpoint reload was started. Per the frozen canary protocol, the run stopped at the first failure and the environment was not modified in place.

`NEXT_ALLOWED_STAGE = REPAIR_AND_FREEZE_A1_SCF_CANARY_RUNTIME_ENVIRONMENT_V1`
