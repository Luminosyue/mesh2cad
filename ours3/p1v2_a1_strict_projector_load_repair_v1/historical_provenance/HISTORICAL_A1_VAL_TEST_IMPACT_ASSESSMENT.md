# Historical A1 VAL / Final TEST impact assessment

Status: **UNAFFECTED**.

The historical A1 VAL launcher installs the curve-ablation runtime and delegates to `unified_v2_entrypoint.strict_load`. That loader constructs SpatialLM, calls `_attach_edge_projector(model)`, and only then loads the sharded checkpoint. It explicitly rejects unexpected keys and rejects missing keys except the standard tied `lm_head.weight` alias.

The frozen Final TEST runner uses the same unified v2 loader for A1. Therefore the defective ordering was limited to the newer Canary adapter path. No TEST prediction, metric, or qualitative result was read or regenerated in this repair task.
