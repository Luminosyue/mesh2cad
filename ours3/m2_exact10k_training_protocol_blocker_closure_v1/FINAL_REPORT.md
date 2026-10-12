# M2 EXACT10K Blocker Closure

CURRENT_GATE: `M2_EDGE_PROJ_ARCHITECTURE_DRIFT_BLOCKED`

The historical Original M2 checkpoint contains `edge_proj.net.0.weight [256,256]` and `edge_proj.net.2.weight [2048,256]`, while the current code contains a 512-dimensional latent attention/FFN adapter. The state dictionaries do not match. No model code was changed and no training, optimizer step, decode, or test evaluation was run.

Training approval remains `NO` until the architecture choice is explicitly resolved.
