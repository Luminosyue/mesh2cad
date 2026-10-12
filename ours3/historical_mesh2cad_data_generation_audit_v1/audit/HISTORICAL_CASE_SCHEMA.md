所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。


以下来自初始文件清单与实际manifest。file counts含版本/引用，不是pair计数。

## partsam_cad_iou_top1000_v1

角色：DATA FACTORY; 2000 attempted / 1994 CAD valid / 488 qualified / 468 final; no 1000 release

```text

python_candidate [matching filenames=9302]

  scripts/pipeline.py

  scripts/render_cad_examples.py

  candidates/01b8043112e74366a21256d5e64398fb_part_000/cad.py

mesh [matching filenames=4106]

  candidates/01b8043112e74366a21256d5e64398fb_part_000/source.obj

  candidates/01b8043112e74366a21256d5e64398fb_part_000/reconstructed.stl

  candidates/01fe14f50de443e4b11ad1fe033df666_part_000/source.obj

step [matching filenames=1994]

  candidates/01b8043112e74366a21256d5e64398fb_part_000/reconstructed.step

  candidates/01fe14f50de443e4b11ad1fe033df666_part_000/reconstructed.step

  candidates/053b8a4984e340ad94f3b563594ff09d_part_000/reconstructed.step

```

## partsam_p1_training_v1

角色：TRAIN DATA prepared; 13 train/2 val/1 test; training_started=false; 2112 candidates

```text

python_candidate [matching filenames=7]

  probe_partsam.py

  scripts/partsam_p1_runtime.py

  scripts/finalize_partsam_p1.py

train_json [matching filenames=18]

  partsam_p1_train.json

  PartSAM/geometry_pack_v1/611b64ba5c9f427aba7b20a8f4220a27_part_013/training_record.json

  PartSAM/geometry_pack_v1/5f1e1e7148424a6bae25b5138ba0088e_part_020/training_record.json

val_json [matching filenames=2]

  partsam_p1_val.json

  masks/VAL_OPERATION_TOKEN_MASK_REGISTRY.jsonl

step [matching filenames=96]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/model.step

  PartSAM/geometry_pack_v1/3a5ed2b8d5c5468897e797dcaba508a1_part_005/model.step

  PartSAM/geometry_pack_v1/f1150d2342a8470e912942c49e978f28_part_005/model.step

mesh [matching filenames=80]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/model.stl

  PartSAM/geometry_pack_v1/3a5ed2b8d5c5468897e797dcaba508a1_part_005/model.stl

  PartSAM/geometry_pack_v1/f1150d2342a8470e912942c49e978f28_part_005/model.stl

dsl [matching filenames=80]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/program_canonical.dsl

  PartSAM/geometry_pack_v1/3a5ed2b8d5c5468897e797dcaba508a1_part_005/program_canonical.dsl

  PartSAM/geometry_pack_v1/f1150d2342a8470e912942c49e978f28_part_005/program_canonical.dsl

surface_points [matching filenames=30]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/surface_points.npy

  PartSAM/geometry_pack_v1/f1150d2342a8470e912942c49e978f28_part_005/surface_points.npy

  PartSAM/geometry_pack_v1/3d55d8d947c2402498c23c1d6dbce934_part_000/surface_points.npy

curve_samples_or_metadata [matching filenames=139]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/curve_samples.npz

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/selected_curve_indices.npy

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/curve_points_sharp_xyztangent.npy

token_cache [matching filenames=19]

  PartSAM/geometry_pack_v1/2e588c7566c54e4086511411763a3e29_part_000/curve_tokens.npy

  PartSAM/geometry_pack_v1/611b64ba5c9f427aba7b20a8f4220a27_part_013/curve_tokens.npy

  PartSAM/geometry_pack_v1/5f1e1e7148424a6bae25b5138ba0088e_part_020/curve_tokens.npy

```

## partsam/PartObjaverse-Tiny_instance_cad

角色：OTHER; faceted BREP conversion, embedded source triangles, not parametric target

```text

python_candidate [matching filenames=2120]

  scripts/server_batch_cad.py

  scripts/mesh_cad_runtime_template.py

  scripts/server_cad_status.py

step [matching filenames=2112]

  3d55d8d947c2402498c23c1d6dbce934/part_000.step

  3d55d8d947c2402498c23c1d6dbce934/part_002.step

  3d55d8d947c2402498c23c1d6dbce934/part_003.step

```

## mesh2cad_stl_00

角色：MESH archive conversion; 940 NPZ / 89 usable / 851 truncated; historical references use obsolete mesh2cad_stl path

```text

python_candidate [matching filenames=627]

  rebuild_all.py

  cad_results/0000c32fde7f45efb8d14e8ba737d50c/part_000/cad_model.py

  cad_results/0000c32fde7f45efb8d14e8ba737d50c/part_003/cad_model.py

mesh [matching filenames=1341]

  whole/0000c32fde7f45efb8d14e8ba737d50c.stl

  whole/0005033c6f754d00899127df5e2388f7.stl

  whole/000a1e27b41d48c5ea1d17ba21ed6c40beeb1484280c47626964d724c7d7db4b.stl

step [matching filenames=626]

  cad_results/0000c32fde7f45efb8d14e8ba737d50c/part_000/model.step

  cad_results/0000c32fde7f45efb8d14e8ba737d50c/part_003/model.step

  cad_results/0000c32fde7f45efb8d14e8ba737d50c/part_002/model.step

```

## ours3/GPT6_PARTSAM_REALMESH_PSEUDOCAD_DATASET_V1

角色：PILOT; DSL pseudo targets; 100 valid, 100 rejected; model metadata conflicts with API blocker; generator UNKNOWN

```text

mesh [matching filenames=200]

  samples/pilot100_000_0000c32fde7f45efb8d14e8ba737d50c_part_005/source_mesh.stl

  samples/pilot100_000_0000c32fde7f45efb8d14e8ba737d50c_part_005/prediction/prediction.stl

  samples/pilot100_001_0005033c6f754d00899127df5e2388f7_part_010/source_mesh.stl

dsl [matching filenames=100]

  samples/pilot100_000_0000c32fde7f45efb8d14e8ba737d50c_part_005/canonical_program.txt

  samples/pilot100_001_0005033c6f754d00899127df5e2388f7_part_010/canonical_program.txt

  samples/pilot100_002_000a1e27b41d48c5ea1d17ba21ed6c40beeb1484280c47626964d724c7d7db4b_part_001/canonical_program.txt

step [matching filenames=100]

  samples/pilot100_000_0000c32fde7f45efb8d14e8ba737d50c_part_005/prediction/prediction.step

  samples/pilot100_001_0005033c6f754d00899127df5e2388f7_part_010/prediction/prediction.step

  samples/pilot100_002_000a1e27b41d48c5ea1d17ba21ed6c40beeb1484280c47626964d724c7d7db4b_part_001/prediction/prediction.step

```

## ours3/partobjaverse_llm_cad_pilot_v1

角色：PILOT; Stage A 200 objects/2112 parts; Stage B is deterministic template code, NOT verified GPT

```text

python_candidate [matching filenames=83]

  scripts/stage_a_partobjaverse.py

  scripts/stage_b_pipeline.py

  scripts/stage_b_summarize.py

mesh [matching filenames=2222]

  split_parts/00200996b8f34f55a2dd2f44d316d107/part_000.obj

  split_parts/00200996b8f34f55a2dd2f44d316d107/part_001.obj

  split_parts/00200996b8f34f55a2dd2f44d316d107/part_002.obj

step [matching filenames=80]

  step/POBJ_d75e06c3ff8f44f9a9b163399e43f0fd_PART_004_v1.step

  step/POBJ_d75e06c3ff8f44f9a9b163399e43f0fd_PART_004_v2.step

  step/POBJ_d75e06c3ff8f44f9a9b163399e43f0fd_PART_004_v3.step

```

## ours3/llm_mesh_to_cad_pilot_v1

角色：PILOT; initial 1 + 3 additional cases; code authorship/model UNKNOWN

```text

python_candidate [matching filenames=19]

  scripts/analyze_geometry.py

  scripts/evaluate_round.py

  cad_code/CADPART_000_v1.py

mesh [matching filenames=14]

  inputs/CADPART_000_source.obj

  recon_mesh/CADPART_000_v1.stl

  recon_mesh/CADPART_000_v2.stl

step [matching filenames=10]

  step/CADPART_000_v1.step

  step/CADPART_000_v2.step

  step/CADPART_000_best.step

```

## ours3/caddsl_advanced_pilot1000_v1

角色：DATA FACTORY / prepared TRAIN DATA; 800/200; seeded synthetic DSL; generator entrypoint UNKNOWN

```text

train_json [matching filenames=3]

  dataset/caddsl_advanced_pilot1000_train800.json

  splits/TRAIN800_MANIFEST.json

  integrity/NO_TRAINING_GUARD.json

val_json [matching filenames=3]

  dataset/caddsl_advanced_pilot1000_val200.json

  splits/VAL200_MANIFEST.json

  audit/GEOMETRY_EQUIVALENCE_TOLERANCE_FREEZE.json

dsl [matching filenames=2000]

  dataset/cases/pilot_0001/source/program.dsl

  dataset/cases/pilot_0001/canonical/program_canonical.dsl

  dataset/cases/pilot_0002/source/program.dsl

step [matching filenames=2000]

  dataset/cases/pilot_0001/source/model.step

  dataset/cases/pilot_0001/canonical/model.step

  dataset/cases/pilot_0002/source/model.step

surface_points [matching filenames=1000]

  dataset/cases/pilot_0001/geometry/surface_points.npy

  dataset/cases/pilot_0002/geometry/surface_points.npy

  dataset/cases/pilot_0003/geometry/surface_points.npy

curve_samples_or_metadata [matching filenames=1000]

  dataset/cases/pilot_0001/geometry/curve_assets.json

  dataset/cases/pilot_0002/geometry/curve_assets.json

  dataset/cases/pilot_0003/geometry/curve_assets.json

```

## ours3/chamfer_synthetic64_from_canonical_p1_v1

角色：PILOT / prepared TRAIN DATA; 32 Box+Chamfer and 32 ExtrudePolygon+Chamfer

```text

dsl [matching filenames=128]

  dataset/case_000/base.dsl

  dataset/case_000/gt.dsl

  dataset/case_001/base.dsl

step [matching filenames=128]

  dataset/case_000/base.step

  dataset/case_000/gt.step

  dataset/case_001/base.step

surface_points [matching filenames=128]

  dataset/case_000/surface_points.npy

  dataset/case_001/surface_points.npy

  dataset/case_002/surface_points.npy

curve_samples_or_metadata [matching filenames=21]

  preprocess/curve_000.json

  preprocess/curve_008.json

  preprocess/curve_032.json

train_json [matching filenames=1]

  integrity/P1_RUNTIME_TRACE_NO_TRAINING_GUARD.json

token_cache [matching filenames=4]

  native_cache/case_000/curve_tokens.npy

  native_cache/case_008/curve_tokens.npy

  native_cache/case_032/curve_tokens.npy

```

## ours3/p1_cadquery_tank_airplane54_v1

角色：PILOT; name 54 is not proof of 54 complete pairs; 20 py and 20 STEP present

```text

step [matching filenames=20]

  assets/XPart/geometry_pack_v1/tank__PART_006/target.step

  assets/XPart/geometry_pack_v1/tank__PART_005/target.step

  assets/XPart/geometry_pack_v1/tank__PART_007/target.step

python_candidate [matching filenames=20]

  assets/XPart/geometry_pack_v1/tank__PART_006/target.py

  assets/XPart/geometry_pack_v1/tank__PART_005/target.py

  assets/XPart/geometry_pack_v1/tank__PART_007/target.py

```

## ours3/p3_xpart_20case_v3_joint_overfit_v1

角色：TRAIN DATA / memorization experiment; 20 frozen cases; update640 TF15/20; formal free generation pending

```text

```

## ours3/toaster_p1_xpart_v1

角色：EVALUATION; initial report 3-part smoke; later artifact counts not equivalent to released pairs

```text

mesh [matching filenames=200]

  inputs/xpart_source/PART_011/generated_mesh_norm.obj

  inputs/xpart_source/PART_011/generated_mesh.obj

  inputs/xpart_source/PART_011/complete_part_011.obj

surface_points [matching filenames=39]

  inputs/PART_032/surface_points.npy

  inputs/PART_000/surface_points.npy

  inputs/PART_018/surface_points.npy

dsl [matching filenames=243]

  predictions/smoke_j0/PART_032/gt.dsl

  predictions/smoke_j0/PART_032/pred_canonical.dsl

  predictions/smoke_j0/PART_032/pred.dsl

step [matching filenames=160]

  predictions/smoke_j0/PART_032/pred.step

  predictions/smoke_j0/PART_000/pred.step

  predictions/smoke_j0/PART_018/pred.step

```

## ours3/exact9998_v1

角色：CONTROLLED_SOURCE_CAD_DATA; separate; 7998/1000/1000; references external geometry assets

```text

train_json [matching filenames=2]

  EXACT9998_TRAIN.jsonl

  exact9998_train.json

val_json [matching filenames=2]

  EXACT9998_VAL.jsonl

  exact9998_val.json

curve_samples_or_metadata [matching filenames=9998]

  curve_tokens/deepcad/0000_00000525/curve_tokens.npy

  curve_tokens/deepcad/0000_00001503/curve_tokens.npy

  curve_tokens/deepcad/0000_00002522/curve_tokens.npy

token_cache [matching filenames=9998]

  curve_tokens/deepcad/0000_00000525/curve_tokens.npy

  curve_tokens/deepcad/0000_00001503/curve_tokens.npy

  curve_tokens/deepcad/0000_00002522/curve_tokens.npy

```

## CADFit/datasets

角色：QUALITATIVE / BASELINE; 2 high-mesh + 3 complex hand-written CAD-first cases

```text

python_candidate [matching filenames=5]

  synthetic_high_mesh_two_case_v1/case_a_flange/ground_truth.py

  synthetic_high_mesh_two_case_v1/case_b_bracket/ground_truth.py

  synthetic_complex_brepgpt_style_v1/complex_flange_housing/ground_truth.py

step [matching filenames=5]

  synthetic_high_mesh_two_case_v1/case_a_flange/ground_truth.step

  synthetic_high_mesh_two_case_v1/case_b_bracket/ground_truth.step

  synthetic_complex_brepgpt_style_v1/complex_flange_housing/ground_truth.step

mesh [matching filenames=5]

  synthetic_high_mesh_two_case_v1/case_a_flange/input_high_mesh.stl

  synthetic_high_mesh_two_case_v1/case_b_bracket/input_high_mesh.stl

  synthetic_complex_brepgpt_style_v1/complex_flange_housing/input_high_mesh.stl

```

## p3_xpart_open_cases

角色：MESH-FIRST reconstructed targets; 1010 STEP files are versions/assemblies, not pair count

```text

mesh [matching filenames=2983]

  11pro_sl_trx_fg/source/11pro_SL_TRX_FG.obj

  11pro_sl_trx_fg/p3_parts/part_000.obj

  11pro_sl_trx_fg/p3_parts/part_001.obj

step [matching filenames=1010]

  11pro_sl_trx_fg/xpart_parts_cadquery_features/PART_001/PART_001.step

  11pro_sl_trx_fg/xpart_parts_cadquery_features/PART_000/PART_000.step

  11pro_sl_trx_fg/xpart_parts_cadquery_assembly/11pro_sl_trx_fg_assembly.step

python_candidate [matching filenames=1028]

  11pro_sl_trx_fg/xpart_parts_cadquery_features/PART_001/PART_001.py

  11pro_sl_trx_fg/xpart_parts_cadquery_features/PART_000/PART_000.py

  11pro_sl_trx_fg/xpart_parts_cadquery_assembly/rebuild_assembly.py

```

注意：curve_assets.json仅表示曲线资产元数据，不能当作已加载curve_samples；train_json名称匹配可能包含NO_TRAINING_GUARD，具体ready判断以专门manifest/FINAL_SUMMARY为准。EXACT9998是引用组织，根目录缺mesh/STEP不意味着其引用文件缺失。
