# Gallery-20 quantitative evaluation

Protocol: 20,000 deterministic surface samples (seed 0), normalized symmetric CD, normalized H95, surface voxel IoU64, no registration.

Strict complete paired subset: N=12.

| Method | N | CD mean | H95 mean | IoU64 mean |
|---|---:|---:|---:|---:|
| Ours | 12 | 0.010054 | 0.032163 | 0.580917 |
| CADFit | 12 | 0.013692 | 0.038845 | 0.371324 |

Partial CADFit assemblies are diagnostics against the full input and are excluded from the strict aggregate.
