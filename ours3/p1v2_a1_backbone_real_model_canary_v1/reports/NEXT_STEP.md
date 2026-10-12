# Next step

Repair only the Canary construction mode: build the formal trainable A1 model (`training=True`), attach CurveProjector before strict checkpoint restore, preserve A1 freeze policy, and prove at least one relevant trainable gradient is finite and non-zero. Then restart the full Canary from a fresh GPU audit.
