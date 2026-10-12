# 历史 pipeline（纯文本）
所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。

PIPELINE_A1 — CAD-first / hand-written demo (5 GT cases)
hard-coded CadQuery program -> CadQuery/OCC shape -> [STEP export + tessellation STL]
                                                   -> CADFit baseline reconstruction (separate target)
Evidence: CADFit create_ground_truth_cases.py + export_high_mesh.py + datasets + provenance report.

PIPELINE_A2 — CAD-first synthetic DSL (64; advanced1000 separately)
seeded parameter/operator templates -> source DSL -> canonical DSL -> execute -> STEP + surface/curve assets
Evidence: manifests + source/canonical program and STEP artifacts. Full generation entrypoint UNKNOWN; executor recovered.

PIPELINE_B1 — PartObjaverse / PartSAM mesh-first
original GLB + face labels -> extracted part OBJ -> deterministic geometry fitting/templates
 -> CadQuery program -> STEP + reconstructed STL -> geometry filter -> 468 final PartSAM rows
Separate branch: original STL -> fit_direct -> canonical DSL -> paired original surface + pseudo-CAD curves ->16 ready P1 samples
Evidence: pipeline.py / build_partsam_p1.py / manifests / three case traces.

PIPELINE_B2 — P3 / Hunyuan3D-Part / X-Part mesh-first
existing object mesh -> P3-SAM segmentation/bboxes -> X-Part completed part mesh
 -> geometric profile fitting or CADFit -> CadQuery -> STEP
 -> native CQ or Compact IR training adaptation ->20-case overfit (plus Airplane9 / Demo5)
Evidence: xpart_from_p3.py / feature_runtime.py / CASE_MANIFEST_FROZEN.json / joint_train.log.

PIPELINE_B3 — LLM-assisted mesh-first
mesh -> geometry brief + feature plan -> qwen-plus chat completion -> project DSL -> CAD executor -> STEP
Evidence: llm_planner.py + PART_005/PART_019 report.json.
GPT6 named pilot: source meshes -> UNKNOWN authoring -> DSL + STEP ->100 reject; metadata claims Codex, no verified API identity.

PIPELINE_B4 — implemented image path, run provenance UNKNOWN
single image -> Hunyuan3D-2mini -> raw.glb -> Taubin + decimation -> STL -> CADFit search -> CadQuery/STL
No CAD ground-truth pairing manifest recovered. No verified CAD-render-to-Hunyuan chain.

PIPELINE_C — Independent mesh + CAD generation then pairing
UNKNOWN / no verified historical cohort. No inference from directory co-location.

PIPELINE_D — CONTROLLED_SOURCE_CAD_DATA
DeepCAD / Fusion feature history -> source-specific compiler -> canonical DSL -> geometry/program supervision
 -> EXACT9998 (7998 train /1000 val /1000 test). Keep separate; no modifications.

PIPELINE_E — other conversions
mesh triangles -> compressed embedded arrays -> triangle faces/sewing -> faceted STEP/BREP (2112)
NPZ full.ply/part_N.ply -> extracted mesh files (not paired CAD GT)
