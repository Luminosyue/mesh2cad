# Size Mask Canary Report

STATUS = PASS

- Automatic deterministic sample: first 10 CAD IDs containing each supported operation, separately for TRAIN and VAL.
- AST field to tokenizer offset mapping is used; no numeric-value text search is used.
- Negative signs, decimal points, scientific notation, tokenizer splitting, causal shift, and geometry-splice relocation are represented by exact token indices and response hashes.
- SIZE_MASK_FALSE_POSITIVE = 0
- SIZE_MASK_MISSED = 0
- Cylinder is deferred when support is below 10.
