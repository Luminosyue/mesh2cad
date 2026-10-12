# Evaluation loop audit

**Old behavior:** `train_clean_v3.py` calls `util.eval_dev(model, ..., rows, ..., 4096, ...)` after every epoch. `rows` is the same 688-record training list. `eval_dev` greedily decodes every record with `max_new_tokens=4096`, then parses and invokes the CAD evaluator. This is why logs say `dev=i/50` while i reaches 688.

**Optimizer/model impact:** evaluation uses `model.eval()` and `torch.no_grad()`; it does not update optimizer or model state. It is nevertheless expensive and invalid as generalization validation.

**Required V2 evaluator behavior:** train CE/checkpoint every epoch; optional fixed 5–10 train sanity decodes; only a frozen, disjoint decode-dev may drive full decode/checkpoint selection. Evaluation must retain deterministic greedy decoding, finite `MAX_NEW_TOKENS`, EOS tracking, and parser oversize protection.

**Current-run safety:** the active process has no evaluator flag and serializes no optimizer/scheduler state. It cannot be safely interrupted and exactly resumed with its current implementation. This audit therefore does not alter or stop it.
