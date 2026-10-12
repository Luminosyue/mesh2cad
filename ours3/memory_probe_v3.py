import os, sys, json, time, torch
from pathlib import Path
ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT / 'ours3/p3_xpart_20case_compact_ir_v3'
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'SpatialLM')]
os.environ['CAD_USE_EDGE_SCORE'] = '0'
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer, load_model
from spatiallm.tuner.data import register_spatiallm_templates, get_template_and_fix_tokenizer, get_dataset, SFTDataCollatorWith4DAttentionMask, IGNORE_INDEX

sys.argv = ['memory_probe_v3', str(EXP/'training20/p3_train_v3.yaml')]
args = read_args(); ma, da, ta, fa, ga = get_train_args(args)
tm = load_tokenizer(ma); tok = tm['tokenizer']
register_spatiallm_templates(cutoff_len=da.cutoff_len, num_bins=da.num_bins, do_augmentation=False, random_rotation=False)
template = get_template_and_fix_tokenizer(tok, da); ds = get_dataset(ma, da, ta)
split = ds[next(k for k in ds if 'train' in str(k).lower())]
model = load_model(tok, da, ma, fa, True)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu'); model.to(device).train()
coll = SFTDataCollatorWith4DAttentionMask(template=template, model=model, pad_to_multiple_of=None, label_pad_token_id=IGNORE_INDEX, block_diag_attn=ma.block_diag_attn, attn_implementation=getattr(model.config, '_attn_implementation', None), compute_dtype=ma.compute_dtype, **tm)
batch = coll([dict(split[13])])
for k,v in list(batch.items()):
    if torch.is_tensor(v): batch[k] = v.to(device)
opt = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=5e-6)
def mem():
    return {'allocated': int(torch.cuda.memory_allocated()/2**20), 'reserved': int(torch.cuda.memory_reserved()/2**20), 'peak_allocated': int(torch.cuda.max_memory_allocated()/2**20), 'peak_reserved': int(torch.cuda.max_memory_reserved()/2**20)}
records=[]
for step in range(1,4):
    torch.cuda.reset_peak_memory_stats(); before=mem(); t0=time.time()
    out=model(**batch); forward_s=time.time()-t0; after_f=mem()
    t1=time.time(); out.loss.backward(); backward_s=time.time()-t1; after_b=mem()
    try:
        opt.step(); after_o=mem(); opt.zero_grad(set_to_none=True); after_z=mem(); status='OK'
    except RuntimeError as exc:
        after_o=mem(); after_z=after_o; status=f'{type(exc).__name__}: {exc}'; records.append({'step':step,'input_length':int(batch['input_ids'].shape[1]),'loss':float(out.loss.detach().cpu()),'before':before,'after_forward':after_f,'after_backward':after_b,'after_optimizer_step':after_o,'after_zero_grad':after_z,'forward_s':forward_s,'backward_s':backward_s,'status':status}); print(json.dumps(records[-1]), flush=True); break
    records.append({'step':step,'input_length':int(batch['input_ids'].shape[1]),'loss':float(out.loss.detach().cpu()),'before':before,'after_forward':after_f,'after_backward':after_b,'after_optimizer_step':after_o,'after_zero_grad':after_z,'forward_s':forward_s,'backward_s':backward_s,'status':status})
    print(json.dumps(records[-1]), flush=True)
out={'records':records,'config':{'attention_impl':getattr(model.config,'_attn_implementation',None),'use_cache':getattr(model.config,'use_cache',None),'gradient_checkpointing':bool(getattr(model,'is_gradient_checkpointing',False)),'cutoff_len':da.cutoff_len,'dynamic_input_length':int(batch['input_ids'].shape[1])}}
(EXP/'memory_audit/memory_probe_v3.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out), flush=True)
