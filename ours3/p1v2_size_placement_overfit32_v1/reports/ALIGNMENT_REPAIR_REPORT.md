# Collator-native placement alignment repair

CURRENT_GATE = COLLATOR_NATIVE_ALIGNMENT_PASS_REAL_TRAINER_CANARY_PENDING

Full response tokenization with offset_mapping was used. Placement spans are derived from operation-local serialized response character spans, not scalar-only tokenization. All 219 frozen placement fields aligned to at least one full-response token; no missed or ambiguous fields. ExtrudePolygon.origin.z passes. Response parity is 32/32, mask intersection is 0, and shift contract is recorded.

The real DataCollator/Trainer canary has not yet been completed, so no training arm was resumed and no early-effect signal is valid. GPU 3 was untouched.
