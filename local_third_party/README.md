Local edits on top of third-party checkouts. These files are not in the upstream repos.
To reuse them, clone the upstream commit below and copy these files back over it.
Downloaded weights were not included: SpatialLM/models, Dora ckpts, external_checkpoints.

## CADFit

- upstream: https://github.com/ghadinehme/CADFit.git
- local commit: `fb31f63b79805fff4c5a5c6fa5f8b2f00fe86536`

- modified `extract_planar_contours.py`
- modified `run_pipeline.py`
- added `dora_edge_prior.py`
- added `scripts/abc_hard_two_case_demo/audit_stl_meshes.py`
- added `scripts/abc_hard_two_case_demo/collect_artifacts_and_report.py`
- added `scripts/abc_hard_two_case_demo/common.py`
- added `scripts/abc_hard_two_case_demo/download_abc_chunks.py`
- added `scripts/abc_hard_two_case_demo/export_generated_step.py`
- added `scripts/abc_hard_two_case_demo/index_abc_files.py`
- added `scripts/abc_hard_two_case_demo/render_comparison.py`
- added `scripts/abc_hard_two_case_demo/run_two_cases.py`
- added `scripts/abc_hard_two_case_demo/scan_step_faces.py`
- added `scripts/abc_hard_two_case_demo/select_two_cases.py`
- added `scripts/abc_hard_two_case_demo/verify_sketch_prior.py`
- added `scripts/synthetic_high_mesh_two_case/audit_cadfit_command.py`
- added `scripts/synthetic_high_mesh_two_case/collect_artifacts_and_report.py`
- added `scripts/synthetic_high_mesh_two_case/common.py`
- added `scripts/synthetic_high_mesh_two_case/create_ground_truth_cases.py`
- added `scripts/synthetic_high_mesh_two_case/export_high_mesh.py`
- added `scripts/synthetic_high_mesh_two_case/export_reconstructed_step.py`
- added `scripts/synthetic_high_mesh_two_case/render_comparison.py`
- added `scripts/synthetic_high_mesh_two_case/render_mesh.py`
- added `scripts/synthetic_high_mesh_two_case/run_two_cases.py`
- added `scripts/synthetic_high_mesh_two_case/fix_case_a_status.py`
- added `scripts/synthetic_high_mesh_two_case/write_final_gate.py`
- added `scripts/synthetic_high_mesh_two_case/execute_generated_program_clean.py`
- added `scripts/synthetic_high_mesh_two_case/geometry_provenance_audit.py`
- added `scripts/synthetic_high_mesh_two_case/run_gpu_workers.py`
- added `scripts/synthetic_high_mesh_two_case/render_effect_overview.py`
- added `scripts/synthetic_complex_brepgpt_style/run_complex_demo.py`
- added `tests/abc_hard_two_case_demo/test_common_and_selection.py`
- added `tests/synthetic_high_mesh_two_case/test_synthetic_demo.py`
- added `configs/abc_hard_two_case_demo.yaml`
- added `configs/synthetic_high_mesh_two_case_v1.yaml`

## Dora

- upstream: https://github.com/Seed3D/Dora.git
- local commit: `a166e21e900cf1e1230a67db2efc8b5a2c022e7d`

- modified `pytorch_lightning/craftsman/models/autoencoders/utils.py`
- modified `pytorch_lightning/craftsman/systems/shape_autoencoder.py`
- modified `sharp_edge_sampling/sharp_sample.py`
- added `pytorch_lightning/configs/shape-autoencoder/Dora-VAE-test.yaml`
- added `pytorch_lightning/configs/shape-autoencoder/Dora-VAE-train.yaml`
- added `pytorch_lightning/configs/shape-autoencoder/Dora-VAE-ours1-test.yaml`
- added `pytorch_lightning/configs/shape-autoencoder/Dora-VAE-ours2-test.yaml`
- added `scripts/run_inference_demo.sh`
- added `scripts/finish_setup.sh`
- added `scripts/run_demo_now.sh`

## Hunyuan3D-Part

- upstream: https://github.com/Tencent-Hunyuan/Hunyuan3D-Part.git
- local commit: `e96be065375438962375b55326416291342958a7`

- modified `P3-SAM/demo/auto_mask.py`
- modified `P3-SAM/model.py`
- modified `XPart/partgen/models/autoencoders/attention_blocks.py`
- modified `XPart/partgen/models/sonata/model.py`

## SpatialLM

- upstream: https://github.com/manycore-research/SpatialLM.git
- local commit: `8913c44d84a450c53e9340b13317f8cf7144a738`

- modified `spatiallm/model/spatiallm_llama.py`
- modified `spatiallm/model/spatiallm_qwen.py`
- modified `spatiallm/tuner/data/mm_plugin.py`
- modified `spatiallm/tuner/data/template.py`
- modified `spatiallm/tuner/framework/patcher.py`
- modified `train.py`
- added `poetry.toml`
- added `configs/spatiallm_sft.yaml`
- added `configs/spatiallm_cad_overfit10_ours.yaml`
- added `configs/spatiallm_cad_overfit10_baseline.yaml`
- added `configs/spatiallm_cad_train100_ours.yaml`
- added `configs/spatiallm_cad_train100_baseline.yaml`
- added `configs/spatiallm_cad_overfit10_canonical_ours.yaml`
- added `configs/spatiallm_cad_train100_canonical_baseline.yaml`
- added `configs/spatiallm_cad_train100_canonical_ours.yaml`
- added `configs/spatiallm_cad_train100_canonical_edge_zero.yaml`
- added `configs/spatiallm_cad_train100_canonical_edge_shuffle.yaml`
- added `configs/spatiallm_cad_train1k_canonical_ours.yaml`
- added `configs/spatiallm_cad_train1k_canonical_baseline.yaml`
- added `configs/spatiallm_cad_train100_canonical_sepedge.yaml`
- added `configs/spatiallm_cad_joint_j0_surface.yaml`
- added `configs/spatiallm_cad_joint_j2_sepedge.yaml`
- added `configs/spatiallm_cad_joint_j2o_oracle.yaml`
- added `configs/spatiallm_cad_joint_j2p_detected.yaml`
