import json,os
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad'); E=R/'ours3/airplane_fullseq_14bit_ir_v1'; D=E/'dataset'; (D/'DeepCAD/geometry_pack_v1').mkdir(parents=True,exist_ok=True)
A=R/'ours3/p1_cadquery_tank_airplane54_full_v1/assets/XPart/geometry_pack_v1/airplane__PART_000'; link=D/'DeepCAD/geometry_pack_v1/airplane__PART_000'
if not link.exists(): link.symlink_to(A,target_is_directory=True)
reg=E/'curve_registry.jsonl'; reg.write_text(json.dumps({'cad_id':'deepcad__airplane__PART_000','dataset':'deepcad','curve_token_path':str(A/'curve_tokens.npy')})+'\n')
ir=(R/'ours3/airplane9_14bit_compact_ir_v1/ir_v2/airplane__PART_000.ir').read_text()
rec={'id':'airplane__PART_000','dataset':'deepcad','point_clouds':['DeepCAD/geometry_pack_v1/airplane__PART_000/surface_points.npy'],'conversations':[{'from':'user','value':'Generate CAD construction program from the point cloud.'},{'from':'assistant','value':ir}]}
for n in ['train','val']:(D/(n+'.json')).write_text(json.dumps([rec]))
(D/'dataset_info.json').write_text(json.dumps({'airplane_train':{'file_name':'train.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}},'airplane_val':{'file_name':'val.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}}},indent=2))
# config is intentionally 32768: no target/source truncation for any 9-part sequence
cfg=E/'smoke_config.yaml'; cfg.write_text(f'''model_name_or_path: {R}/ours3/p1v2_controlled_full_train_v1/runs/p1v2/checkpoint-6000
trust_remote_code: false
use_fast_tokenizer: false
do_train: false
do_eval: false
freeze_language_tower: false
freeze_point_tower: true
train_proj_only: false
dataset: airplane_train
eval_dataset: airplane_val
dataset_dir: {D}
media_dir: {D}
template: spatiallm_cad_llama_sepedge
num_bins: 1280
do_augmentation: false
random_rotation: false
cutoff_len: 32768
preprocessing_num_workers: 1
dataloader_num_workers: 1
output_dir: {E}/smoke
logging_steps: 1
report_to: none
seed: 42
data_seed: 42
per_device_train_batch_size: 1
per_device_eval_batch_size: 1
gradient_accumulation_steps: 1
learning_rate: 1.0e-5
bf16: true
tf32: true
gradient_checkpointing: false
max_new_tokens: 22000
''')
print(E)
