import copy
import json
import os
import sys
from pathlib import Path
import torch
import yaml

os.environ['DISABLE_VERSION_CHECK'] = '1'
os.environ['CURVE_TOKEN_ROOT'] = '/data/home/cuiyuehan/project/mesh2cad/ours3/deepcad_official_pilot1000_v1/pilot/curve_tokens'
os.environ['CAD_SECOND_STREAM'] = 'curve_tokens'
os.environ['CAD_USE_SEPARATE_EDGE_TOKENS'] = '1'
ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/deepcad_official_pilot1000_v1'
sys.path[:0] = [str(ROOT / 'SpatialLM'), str(ROOT / 'scripts')]
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector.install()
from transformers import AutoTokenizer
from spatiallm.tuner.hparams.parser import _parse_train_args
from spatiallm.tuner.data import get_template_and_fix_tokenizer, register_spatiallm_templates, SFTDataCollatorWith4DAttentionMask
from spatiallm.model.spatiallm_llama import SpatialLMLlamaForCausalLM

cfg = yaml.safe_load((ROOT / 'scripts/spatiallm_curve_token_v1/configs/heldout_best_v2_m2.yaml').read_text())
cfg.update({'model_name_or_path': str(ROOT / 'SpatialLM/models/SpatialLM1.1-Llama-1B'), 'cutoff_len': 8192, 'do_train': False, 'do_eval': False, 'save_dir': None, 'output_dir': str(OUT / 'runtime')})
ma, da, ta, _, _ = _parse_train_args(cfg)
tok = AutoTokenizer.from_pretrained(cfg['model_name_or_path'], local_files_only=True, use_fast=False)
register_spatiallm_templates(cutoff_len=8192, num_bins=da.num_bins, do_augmentation=False, random_rotation=False)
da.template = 'spatiallm_cad_llama_sepedge'; template = get_template_and_fix_tokenizer(tok, da)
coll = SFTDataCollatorWith4DAttentionMask(template=template, model=None, tokenizer=tok, label_pad_token_id=-100, pad_to_multiple_of=None, block_diag_attn=False, attn_implementation='eager', compute_dtype=torch.float32)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
dtype = torch.bfloat16 if device.type == 'cuda' else torch.float32
model = SpatialLMLlamaForCausalLM.from_pretrained(cfg['model_name_or_path'], torch_dtype=dtype, device_map={'': str(device)}, local_files_only=True)
model.eval()
ids = [json.loads(x)['official_id'] for x in (OUT / 'PILOT1000_GT_CURVE_AUDIT.jsonl').read_text().splitlines() if json.loads(x).get('gt_curve_pass',False)]
rows = []
with torch.no_grad():
    for sid in ids:
        base = OUT / 'pilot' / 'DeepCAD' / sid
        pack = OUT / 'pilot' / 'geometry_pack_v1' / 'DeepCAD' / sid
        sample = {'_prompt': [{'role': 'user', 'content': '<point_cloud>\nGenerate CAD construction program from the point cloud.\n\nAllowed operations (CAD DSL v1):\nSketch, Circle, Rectangle, Extrude, Cut, Union\n\nOutput only valid DSL assignments ending with result = ...'}], '_response': [{'role': 'assistant', 'content': (base / 'program_canonical.dsl').read_text()}], '_system': '', '_point_clouds': [str(pack / 'surface_points.npy')]}
        try:
            b = coll([copy.deepcopy(sample)])
            surface = b['point_clouds'][0].to(device=device, dtype=next(model.point_backbone.parameters()).dtype)
            surf = model.forward_point_cloud(surface, device=device, dtype=next(model.parameters()).dtype, projector=model.point_proj)
            k = int(b['edge_clouds'].shape[1]); base_n = int(b['input_ids'].shape[1]); surface_n = int(surf.shape[1]); total = base_n + surface_n + k
            labels = b['labels'][0]; valid = labels[labels != -100]; eos_pos = [i for i, v in enumerate(b['input_ids'][0].tolist()) if v == tok.eos_token_id]
            rows.append({'official_id': sid, 'surface_raw_shape': list(surface.shape), 'surface_encoder_output_shape': list(surf.shape), 'surface_token_n': surface_n, 'curve_token_shape': list(b['edge_clouds'].shape), 'curve_token_n': k, 'base_sequence_n': base_n, 'total_sequence_n': total, 'context_fit': total <= 8192, 'eos_supervised': bool(eos_pos and labels[eos_pos[-1]].item() != -100), 'prefix_masked': bool((labels[:int((labels != -100).nonzero()[0])] == -100).all()), 'result_supervised': 'result' in tok.decode(valid.tolist(), skip_special_tokens=False), 'finite': bool(torch.isfinite(surf).all() and torch.isfinite(b['edge_clouds']).all())})
        except Exception as exc:
            rows.append({'official_id': sid, 'error': type(exc).__name__ + ': ' + str(exc)[:700], 'context_fit': False, 'finite': False})
        print(sid, rows[-1].get('context_fit'), flush=True)

(OUT / 'PILOT1000_RUNTIME_CONTEXT_AUDIT.jsonl').write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in rows))
(OUT / 'PILOT1000_SUPERVISION_AUDIT.jsonl').write_text(''.join(json.dumps({'official_id': x['official_id'], 'eos_supervised': x.get('eos_supervised', False), 'result_supervised': x.get('result_supervised', False), 'prefix_masked': x.get('prefix_masked', False), 'finite': x.get('finite', False)}, sort_keys=True) + '\n' for x in rows))
print(json.dumps({'n': len(rows), 'runtime_pass': sum(x.get('context_fit', False) and x.get('eos_supervised', False) and x.get('result_supervised', False) and x.get('prefix_masked', False) and x.get('finite', False) for x in rows), 'context_fit': sum(x.get('context_fit', False) for x in rows), 'supervision_pass': sum(x.get('eos_supervised', False) and x.get('result_supervised', False) and x.get('prefix_masked', False) for x in rows)}, indent=2))
