# P3_XPART_20CASE_V3_JOINT_OVERFIT_FINAL

This is a joint memorization / learnability experiment across 20 diverse object cases, not a held-out generalization evaluation.

Training used Demo5 frozen model weights only, a new standard AdamW optimizer, LR 5e-6, context 16384, dynamic sequence length, micro-batch 1, SDPA, cache disabled, gradient checkpointing, and balanced round-robin sampling. Warm-start 20-case TF audit: 54,241 errors, 0/20 zero-error cases.

TF trajectory: [{"UPDATE": 20, "TOTAL_ERRORS": 51452, "ZERO_ERROR_CASE_N": 1, "MAX_CASE_ERROR": 6652}, {"UPDATE": 40, "TOTAL_ERRORS": 47242, "ZERO_ERROR_CASE_N": 2, "MAX_CASE_ERROR": 6505}, {"UPDATE": 80, "TOTAL_ERRORS": 38970, "ZERO_ERROR_CASE_N": 2, "MAX_CASE_ERROR": 6190}, {"UPDATE": 160, "TOTAL_ERRORS": 33657, "ZERO_ERROR_CASE_N": 4, "MAX_CASE_ERROR": 6041}, {"UPDATE": 320, "TOTAL_ERRORS": 15111, "ZERO_ERROR_CASE_N": 5, "MAX_CASE_ERROR": 2700}, {"UPDATE": 640, "TOTAL_ERRORS": 6, "ZERO_ERROR_CASE_N": 15, "MAX_CASE_ERROR": 2}]

At update 640: total errors = 6, zero-error cases = 15/20, maximum case error = 2. The 20/20 TF gate was not reached.

20-case free generation, natural EOS, generated-IR parser/compiler, CAD/BRep, STEP readback, and geometry comparison were not run because the required 20/20 TF gate was not reached.

Target token mean / median / P95 / max: 5694.00 / 4114.50 / 12028.05 / 12029

Full-sequence token mean / median / P95 / max: 5742.00 / 4155.00 / 12066.30 / 12072

V1 to V3 maximum reduction: 61.05%

Manifest SHA256: 8e9886566f1080c7cb11a4dda259a1c4b397d6e2e42928679d1269e2ee8de481

P3_XPART_20CASE_MODEL_EXACT_PASS=FALSE
P3_XPART_20CASE_FULL_PIPELINE_PASS=FALSE
PAPER_20CASE_RESULT_READY=NO
PAPER_CORE_DEMO_READY=YES
