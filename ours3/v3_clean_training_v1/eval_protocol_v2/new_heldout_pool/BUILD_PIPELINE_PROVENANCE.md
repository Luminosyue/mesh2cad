# V3 held-out Phase 0: verified construction provenance

Surface source: `STEP_TO_TRIANGULATED_MESH_TO_UNIFORM_SURFACE_POINTS`.
Curve source: `FINAL_STEP_BREP_TOPOLOGICAL_EDGES_SHARP_ONLY_TO_ARCLENGTH_SAMPLES_TO_FROZEN_C2`.

## Pipeline
### source CAD / STEP
- Script/function: `scripts/geometry_pack_v1/pack.py` — `freeze_cad_target`
- Input: cad_spatial_dataset/{DeepCAD|Fusion360}/train/<id>/{model.step,program_canonical.dsl,coordinate_transform.json}
- Output: geometry_pack_v1/<id>/{cad_target.dsl,coordinate_transform.json}
- Transform: target DSL copied, never derived from mesh
- Unit/canonicalization: frozen coordinate_transform
- Seed: not applicable

### mesh.obj
- Script/function: `scripts/geometry_pack_v1/pack.py` — `build_one -> occ.tessellate_step`
- Input: source final model.step
- Output: geometry_pack_v1/<id>/mesh.obj
- Transform: OCC tessellation, trimesh export
- Unit/canonicalization: source STEP frame
- Seed: not applicable

### surface points
- Script/function: `scripts/geometry_pack_v1/{pack.py,surface.py}` — `sample_surface_uniform`
- Input: tessellated vertices/faces
- Output: surface_points_source.npy, surface_face_index.npy, surface_points.npy
- Transform: area-weighted triangle choice + folded-square barycentric sampling; canonical xyz scale+translation; face normals not translated
- Unit/canonicalization: source points -> frozen canonical transform
- Seed: geometry_pack_v1.constants.DEFAULT_SEED

### GT B-Rep curve samples
- Script/function: `scripts/curve_token_v1/build_dataset.py` — `build_one -> extract_curves_from_shape -> build_sample_arrays`
- Input: source final model.step and read-only geometry_pack_v1 coordinate_transform
- Output: ours3/curve_token_data_v1/{deepcad_train|fusion360_train}/<id>/curve_samples.npz
- Transform: OCC TopoDS edges; canonicalized; arc-length 32 samples; sharp filtering happens at C2 export
- Unit/canonicalization: same frozen Track-A coordinate transform
- Seed: not applicable

### C2 input and tokens
- Script/function: `scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py` — `process_cad -> curve_inputs -> frozen C2 forward`
- Input: curve_samples.npz (normalized xyz, tangents); sharp B-Rep edge map
- Output: curve_tokens_c2_frozen_v2/{deepcad|fusion360}/<id>/curve_tokens.npy
- Transform: curve-local frame xyz + tangent + normalized s; log polyline length; deterministic length order; sharp-only; max 128 before V3 adapter
- Unit/canonicalization: local normalized curve xyz + log length
- Seed: not applicable

### V3 JSON and tokenizer/chat input
- Script/function: `scripts/spatiallm_curve_token_c2_frozen_v2/run_v2_1k_gate.py; scripts/v3_clean_training_v1/{build_clean_manifest.py,train_clean_v3.py}` — `run_v2_1k_gate.main; build_clean_manifest.main; train_clean_v3.encode_full`
- Input: surface path + C2 tokens + cad_target.dsl
- Output: CLEAN_V3_MANIFEST.json then prompt/target token IDs
- Transform: V3 M2 GeometryPrefixAdapter turns full C2 tokens into 8 summaries; full target plus eot checked against actual splice; no target slicing
- Unit/canonicalization: token positions, context limit 4096
- Seed: not applicable

## Audited samples
### deepcad__0000_00001503 (deepcad)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/train/0000_00001503/model.step`; exists=True; sha256=537c5fabb60c355e593108d596c53c33a5cf24527f20cc5d007a7ca6f348903a
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/mesh.obj`; exists=True; sha256=8cf6bd7bb07899750db7fbcfc282b22329c31db9eed1329301863cdc9415ec8a
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/surface_points.npy`; exists=True; sha256=2ec1e48bc7c904dcae5e73f779cc8864282ff2c21039d8ea66d04dd20eb57f19
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/surface_points_source.npy`; exists=True; sha256=a091b8f96dc0426bb27ade202128d86ac7706786b6b758de6c902735c9ccc1af
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/surface_face_index.npy`; exists=True; sha256=81bee2e6760f7a3c9dc457befa1d3b43ce0413daaf0d724596267b00f13ebdce
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/coordinate_transform.json`; exists=True; sha256=3d2d907f7b913bc01f385873503cc3f53d20a3f74179fbb5788add0008ec0ec6
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/cad_target.dsl`; exists=True; sha256=07921486af7a939a3b5fcee8dbe25a753744e3b44b4031b628046b2fed48d0b8
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00001503/brep_edges.json`; exists=True; sha256=76a04caad686c1b67b2ceb8995c4e433cd06cd91bd70f1b172a05abe1a1f5643
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/deepcad_train/0000_00001503/curve_samples.npz`; exists=True; sha256=3fca45132dcde4ac89e9408d4ac3d459ad6b7cf0708a97961235f9b7985d766f
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/deepcad/0000_00001503/curve_tokens.npy`; exists=True; sha256=3f111acf56afd83fd1f082d38750908f9a73b23ed554a9e76d50969565ff824b

### deepcad__0000_00002522 (deepcad)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/train/0000_00002522/model.step`; exists=True; sha256=13ea37c8b803508c7bf92f4c447c8dd1fc9072645ebe8bd474fffa40a11a965e
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/mesh.obj`; exists=True; sha256=07b7b3ac65974884fe32fd70fec69b2365fd5922f4b029679744cac5d99ac7bc
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/surface_points.npy`; exists=True; sha256=674a0275efaff7df4157f1086dc2471022c644e64ee8ce10c19ebaeaaea47ca0
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/surface_points_source.npy`; exists=True; sha256=09e23c243cb46dc2a42b24089d32a697868aa300646036ba30daf574980b43d7
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/surface_face_index.npy`; exists=True; sha256=f70b96fdc338425861642789e89b0685293d49ebc1dc7ce6d87c8ac626f33e7a
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/coordinate_transform.json`; exists=True; sha256=55c413318b49bf6376b3f1bd35bb2b0ab48e6d94af269b8e92dfeb0f5cccb049
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/cad_target.dsl`; exists=True; sha256=12ca2dc8efda90e67d7a5981e4272fd6661c4cf866636077e7dc5d90863248e4
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00002522/brep_edges.json`; exists=True; sha256=c69c7c0a3a9581ff1d3889e4895eb887f533476e665a3b7af9d9b0dc02003fd2
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/deepcad_train/0000_00002522/curve_samples.npz`; exists=True; sha256=89cd8e7437c9a1f6fb42ba56551b9f8ccd9a197b14882d1f7f5e4824d3792198
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/deepcad/0000_00002522/curve_tokens.npy`; exists=True; sha256=0ed86a6638d7219c01968f53a398e7106334a29ca74776476a7b90a71d143864

### deepcad__0000_00009722 (deepcad)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/train/0000_00009722/model.step`; exists=True; sha256=9d00ef8c3417453a3b47a638d8aec422512bf85c1fc884665000dfcc2ceb59e3
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/mesh.obj`; exists=True; sha256=532286d6e64d9034c04e68f4dae9193dec1d0157876d7a527b63e5453797bd3a
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/surface_points.npy`; exists=True; sha256=a4071ca24a6f78f52efe8583f07bf23cc9f93e757d76424e3c11266849c66e72
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/surface_points_source.npy`; exists=True; sha256=c5738c7dc4a06e695d82b9c917e666a4eda610d10631881b83627e9c108f3f20
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/surface_face_index.npy`; exists=True; sha256=9a1ed543bce331428afe03d3237cc7434d14eed42871bc8cb88b507286323b1d
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/coordinate_transform.json`; exists=True; sha256=fa44bf697ab20633be82511c52cc2b6f9a330e8cd293974ebe434fe4870dc4c8
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/cad_target.dsl`; exists=True; sha256=da16f29dccfc9c9970850c17d88e552a36211b994c4c95e255bf8ca3b3c74a85
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1/0000_00009722/brep_edges.json`; exists=True; sha256=a74e0f2c18cfa63a236f60fa3dd01f1626130b2871a53d81904e767fc0ccb69b
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/deepcad_train/0000_00009722/curve_samples.npz`; exists=True; sha256=362738e1e8d7d73a3e04adabfdb0f15a2f770c882babcb4057c831d175322c62
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/deepcad/0000_00009722/curve_tokens.npy`; exists=True; sha256=1ca8b20f39b5683e268d9e904057abababa77edb65cc9cf535811c9d67dc8aee

### fusion360__117695_cb9a01fb_0006 (fusion360)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train/117695_cb9a01fb_0006/model.step`; exists=True; sha256=359680e6558d4b3b30ee23baedb0eaf4aaf8257eb5e07e6b01e5abe62e6703e1
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/mesh.obj`; exists=True; sha256=1ca2947803c242b755b622eba0debbd622319fcaf5009e937cd2365bb834af53
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/surface_points.npy`; exists=True; sha256=363d8ccba5d4f5f36c48e7da558c9ea614f8cef32bc2372e2a9292510949560a
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/surface_points_source.npy`; exists=True; sha256=eb993041c1ffad18f3cc73fdfdcbefc83b453b091a3ce9b5aa05712d92a745ad
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/surface_face_index.npy`; exists=True; sha256=c3de52635d069453c8ec0aaeaff19508ceeb0c8cbc8f3b364cd3e87b97cfc243
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/coordinate_transform.json`; exists=True; sha256=68e08587020c89a8ac6f9a42eae77bd5eadf9b91570e379ab48d306f8cdf0228
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/cad_target.dsl`; exists=True; sha256=71418195198280e5938c37df196fed7a4867b3330b8b7a70c4a629a14548613c
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/117695_cb9a01fb_0006/brep_edges.json`; exists=True; sha256=7e6fe13accc7e742de01ecc061bcdf9127ee8a95ec9f76f1b37f0d56df0b7ab6
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/fusion360_train/117695_cb9a01fb_0006/curve_samples.npz`; exists=True; sha256=04abfcfd1c1a817c48c1a1d49204248c40ac2175b0efaca77a5ad3c46cb95f92
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/fusion360/117695_cb9a01fb_0006/curve_tokens.npy`; exists=True; sha256=12589a6dcd600753b5dc5a877b3a95cbd57736509eb8fde621c684a3f77148bd

### fusion360__122424_d612248e_0000 (fusion360)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train/122424_d612248e_0000/model.step`; exists=True; sha256=39e133d60ef104db4b9cf76df19e04c9e613639b4cd49cde86b52eae8d90c98e
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/mesh.obj`; exists=True; sha256=cfffae025cd28e33468ecd484ab16993fdf4d0e167082731aa8fca4010679937
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/surface_points.npy`; exists=True; sha256=12c65dc12afdaa9cae2a992cac1a5dd409d723d7bbef5e7310913c1ba645da93
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/surface_points_source.npy`; exists=True; sha256=309710d79dc5b125d37fb7c7bb5788dc309a18648d36468ea332eb7846901723
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/surface_face_index.npy`; exists=True; sha256=236ed6bf8ee5fb093c004bc1f660dc95201179aa89599aa3fd008b0e17da5767
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/coordinate_transform.json`; exists=True; sha256=eb3ba8ae41c7d9e255b56eb24f9cc5f96f686c96f9042423cafb9b1e28333698
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/cad_target.dsl`; exists=True; sha256=b8fef91287c1ba93fed22a0169ee5c305b3680db1fb4ad90a133677f4b70f92d
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/122424_d612248e_0000/brep_edges.json`; exists=True; sha256=0a58c2b69c2316f24b254651f83b46f612dbde1c0b8edcf6274605fc5c5cbcb6
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/fusion360_train/122424_d612248e_0000/curve_samples.npz`; exists=True; sha256=df5430093356d4f51922ac2fddf786a72b7dfcbb013f6ca13f288bd2e58a1ea2
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/fusion360/122424_d612248e_0000/curve_tokens.npy`; exists=True; sha256=4c2e76c7ad1009c3c6d07df7b2fa241a492807c129a22201a6935861942f43f0

### fusion360__123754_6d71ab4f_0000 (fusion360)
- source_step: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train/123754_6d71ab4f_0000/model.step`; exists=True; sha256=92a1fad23dbb36e394236651e5482fb2766cbe63afc693a7039cabe77179e5ba
- mesh_obj: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/mesh.obj`; exists=True; sha256=f8290f0d13d7ef31545ca79d342824cc3e39b288290328bd376b32013d25a34c
- surface_points: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/surface_points.npy`; exists=True; sha256=8488ee91e36d353e18991f5ceb7116b77033dfe86911280056af1cb161be2563
- surface_points_source: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/surface_points_source.npy`; exists=True; sha256=c2e3587bbe2d4ad0e162ec786b171578c582efbfb1bac15a6d28d2d28d45f2d1
- surface_face_index: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/surface_face_index.npy`; exists=True; sha256=b03d105d73d7cea8cc27344cb350d8e99039c8ac29d72b03c81833cc5d1d735f
- coordinate_transform: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/coordinate_transform.json`; exists=True; sha256=0a7cc2f10602ed1f4cf93ad5dc903a4a6026a749b14fbc317a2fa7bd4bae3fd4
- cad_target_dsl: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/cad_target.dsl`; exists=True; sha256=c1b3e7713e3fdc2b4979446c2116417fac64c895329c2af4017d6c5392fd08fc
- brep_edges: `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1/123754_6d71ab4f_0000/brep_edges.json`; exists=True; sha256=3860242e4b8869463e2f80cae17c4da4993d0da854ffa14fb465e73717f96a6a
- curve_samples: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1/fusion360_train/123754_6d71ab4f_0000/curve_samples.npz`; exists=True; sha256=de4b2badb5cece0f19c628224e705c296e4274df1d75c77c162d6568d369acd1
- curve_tokens: `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/fusion360/123754_6d71ab4f_0000/curve_tokens.npy`; exists=True; sha256=251d3c7dea9504402a242ae274ccf94fbc7206dbc14ee941deefa37c85103995

