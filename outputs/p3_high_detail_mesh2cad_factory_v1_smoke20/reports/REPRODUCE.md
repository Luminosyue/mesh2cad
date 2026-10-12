# Reproduction and scope

The result root is `/data/home/cuiyuehan/project/mesh2cad/outputs/p3_high_detail_mesh2cad_factory_v1_smoke20`. All task writes are inside this root. The delivery archive is a sibling copy. Historical inputs/checkpoints remain read-only.

The source object manifest contains exactly 20 frozen full meshes with SHA-256. `config/smoke20.json` freezes part size rules, candidate budgets, evaluation and acceptance. `config/factory_config.json` supplies the inherited evaluation implementation; its old output directory is unused by the copied metric function. No historical experiment is resumed or mutated.

## Runtime

- P3: `/data/miniconda3/envs/hunyuan/bin/python`, GPU 3 only.
- Geometry: `/data/miniconda3/envs/cadfit-env/bin/python`, CPU, four part workers for stages 3/5 and `P3_CAD_WORKERS=12` for stage 20, one BLAS/OpenMP thread per worker. Only scheduling changes; each candidate budget, geometry algorithm and seed stays unchanged. The server resource check showed 180 logical CPUs and over 800 GiB available memory before raising concurrency.
- Python bytecode disabled; P3 caches confined to the new output root.
- Original P3 checkpoint `Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors` contains all Sonata backbone tensors. The original loader referenced an absent separate Sonata checkpoint. A copied loader initializes Sonata from the copied architecture config, then restores the full P3 checkpoint. Original code and checkpoint were not edited. See runtime/p3/model.py and integrity manifests.

## Running

Run `python -B scripts/run_pipeline.py --limit 3 --stage replay`, then limits 5 and 20 after inspecting each stage. The wrapper chooses the required interpreters. Resume uses existing completed results; it does not recompute or overwrite accepted/rejected decisions. To review each stage separately use decompose, features, cad, assemble, visualize, finalize.

LLM decisions are stored in `scripts/p3_plans*.json` and `manifests/llm_structure_response_*.json`. Replay consumes these fixed decisions. New model planning requires reading the new geometry summaries and explicitly supplying a response map to `p3_install_plans.py`. No external model API call is claimed, and the runtime model identifier was not exposed. All numeric fitting is performed by the stored geometry code.

The supplied archive is an evidence snapshot. For a fresh experiment, copy the scripts/config and copied runtime to a **new** output root, rewrite absolute paths in a copied manifest to the copied source/checkpoint locations, regenerate the canonical sources and decompositions, then reproduce the frozen-plan stages. Do not remove results from this root or rerun preparation over it. The preparation script records this original experiment and uses its fixed original path; adapt its output root before using it for another experiment. Exact byte-for-byte GPU segmentation is not promised across different CUDA/library/hardware versions; hashes and version records identify this run.

## Metrics and interpretation

Evaluate reloaded STEP tessellation, 20,000 samples, inherited approximate scan-filled IoU128. Strict acceptance requires IoU >= .90, NCD <= .01, bbox error <= .03, centroid error <= .02 and STEP reload. Near pass is IoU >= .70 and NCD <= .02, analysis only. No failure-driven relaxation.

Only strict parts enter pairs or source-object assemblies. `assembly.step` uses canonical object coordinates; `object_reconstructed.step` restores original object coordinates. Transform conventions are recorded per part: local_transform maps object-canonical to part-local, world_transform reverses that map, local_to_original_object includes inverse object normalization. Missing major parts remain absent and listed. A partial compound is not a successful full-object reconstruction. Whole-object metrics are null when no strict CAD exists.

CAD-derived exact pairs share the reconstructed CAD source; their tessellation remains an approximation of the analytic CAD. Pseudo pairs use real P3 meshes and are never original design ground truth. High triangle count alone does not establish richer design complexity. Synthetic assembly fixture results are excluded from dataset counts.

## Inspection

Read reports/REPORT.md and reports/summary.json, then tables/object_summary.csv, part_summary.csv, candidate_summary.csv and family_breakdown.csv. Empty accepted/pair lists are valid negative findings. Visualizations use fixed object frame and camera, deterministic surface samples, normal-based shading and source-face segmentation colors. Empty CAD panels mean no strict acceptance.

Historical integrity scope and any changed files are in integrity/READ_ONLY_GUARD.json. The guard is a scoped file hash/mtime comparison, not a server-wide claim.
