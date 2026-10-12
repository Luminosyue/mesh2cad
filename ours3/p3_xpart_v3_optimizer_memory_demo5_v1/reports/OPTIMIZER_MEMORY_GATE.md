# Optimizer memory gate

The independent experiment used the frozen V3 data and the longest actual model input, `case_013`, at 12,065 tokens. The formal trainable parameter audit found 1,347,197,056 total parameters, 1,238,440,960 trainable parameters, and 108,756,096 frozen surface encoder parameters. All trainable parameters were runtime-upcast to `float32`.

For 1,238,440,960 float32 trainable parameters, the direct estimates are:

- weights: 4.95 GB
- gradients: 4.95 GB
- Adam first moment: 4.95 GB
- Adam second moment: 4.95 GB
- master weights: 0 GB additional
- estimated Adam state plus weights and gradients: 19.82 GB before activations and temporary buffers

The standard AdamW baseline was rerun on an available L20 (GPU 7) and completed three consecutive full updates. Peak allocated memory was 25,293 MiB and peak reserved memory was 31,292 MiB; update losses were 4.1304, 2.6131, and 1.9929. Forward, backward, optimizer.step, and zero_grad all passed on all three updates. There was no continuing allocated-memory increase after the first optimizer-state allocation; reserved memory stabilized after update 2.

The previous OOM was therefore caused by concurrent occupancy on the selected device, which left only about 30 MiB free at the first lazy AdamW state allocation. It was not an attention or sequence correctness failure.

Environment audit: `accelerate 1.14.0` is installed; `bitsandbytes` and `deepspeed` are unavailable. No stable existing CPU-offload optimizer entry point was present, so CPU-offload, AdamW8bit, and paged AdamW8bit were recorded as unavailable rather than installed ad hoc. Selected configuration: standard `AdamW`, GPU state placement, full-parameter training, context 16,384, micro-batch 1, learning rate 5e-6.

`OPTIMIZER_MEMORY_GATE=PASS`.
