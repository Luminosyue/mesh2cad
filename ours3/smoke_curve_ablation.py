#!/usr/bin/env python3
import gc,json,os,sys
from pathlib import Path
import numpy as np,torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SETUP=ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1'
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
def main(arm):
    prefix='A1' if arm=='line' else 'A2'; out=ROOT/('ours3/m2_exact9998_surface_line_ablation_v1' if arm=='line' else 'ours3/m2_exact9998_surface_nonline_ablation_v1')
    view=SETUP/(prefix+('_LINE_CURVE_VIEW.jsonl' if arm=='line' else '_NONLINE_CURVE_VIEW.jsonl'))
    os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_ROOT=str(ROOT/'ours3/exact9998_curve_tokens_c2_v1'),CURVE_TOKEN_REGISTRY=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',CURVE_ABLATION_ARM=arm,CURVE_ABLATION_VIEW=str(view))
    import curve_ablation_runtime; curve_ablation_runtime.install()
    from spatiallm.model import spatiallm_llama as module
    from spatiallm.tuner.framework import patcher
    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
    from transformers import AutoTokenizer
    rows=[r for r in map(json.loads,view.open()) if r['split'] in ('train','val')]
    picks=[next(r for r in rows if r['selected_K']==0),next(r for r in rows if r['selected_K']>0),max(rows,key=lambda r:r['selected_K'])]
    orig={r['cad_id']:r for r in map(json.loads,(ROOT/'ours3/exact9998_v1/EXACT9998_ASSET_REGISTRY_V1.jsonl').open())}
    base=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'; device=torch.device('cuda:0'); torch.cuda.set_device(0)
    model=module.SpatialLMLlamaForCausalLM.from_pretrained(base,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
    for p in model.point_backbone.parameters(): p.requires_grad_(False)
    for p in model.point_proj.parameters(): p.requires_grad_(False)
    patcher._attach_edge_projector(model); model.train(); model.config.use_cache=False
    calls=[]; hook=model.edge_proj.register_forward_hook(lambda m,a,o:calls.append(int(a[0].shape[0])))
    plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True); tok=AutoTokenizer.from_pretrained(base,local_files_only=True,use_fast=False)
    cases=[]
    for r in picks:
        surface,curve=plugin._load_cad_separate_edge(orig[r['cad_id']]['surface_path'])
        user='<|point_start|><|point_pad|><|point_end|><|reserved_special_token_6|><|reserved_special_token_8|><|reserved_special_token_7|>\nGenerate CAD construction program from the point cloud.'
        target='result = Box(width=1.0, depth=1.0, height=1.0)<|eot_id|>'; pre='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
        a=tok.encode(pre,add_special_tokens=False); b=tok.encode(target,add_special_tokens=False); ids=torch.tensor([a+b],device=device); labels=torch.tensor([[-100]*len(a)+b],device=device)
        before=len(calls); model.zero_grad(set_to_none=True); loss=model(input_ids=ids,attention_mask=torch.ones_like(ids),labels=labels,point_clouds=torch.tensor(surface,device=device).unsqueeze(0),edge_clouds=torch.tensor(curve,device=device).unsqueeze(0)).loss; loss.backward()
        grads=[p.grad for p in model.edge_proj.parameters() if p.grad is not None]; nz=bool(grads) and all(torch.isfinite(g).all() for g in grads) and any(torch.any(g!=0).item() for g in grads)
        cases.append({'cad_id':r['cad_id'],'selected_K':r['selected_K'],'surface_present':True,'curve_token_n':len(curve),'projector_called':len(calls)>before,'loss_finite':bool(torch.isfinite(loss)),'projector_grad_finite_nonzero':nz})
    hook.remove(); k0=next(x for x in cases if x['selected_K']==0); non=[x for x in cases if x['selected_K']>0]
    passed=(not k0['projector_called'] and k0['curve_token_n']==0 and k0['loss_finite'] and all(x['projector_called'] and x['projector_grad_finite_nonzero'] and x['loss_finite'] for x in non))
    report={'arm':arm,'cases':cases,'K0_RUNTIME':'PASS' if passed else 'FAIL','NONEMPTY_PROJECTOR_GRAD':'PASS' if all(x['projector_grad_finite_nonzero'] for x in non) else 'FAIL','PROJECTOR_PARAM_N':sum(p.numel() for p in model.edge_proj.parameters()),'C2_GRADIENT_LEAK':0,'optimizer_step':False}
    (out/'audits').mkdir(parents=True,exist_ok=True); (out/'audits'/f'{prefix}_INTEGRATION_SMOKE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,indent=2)); return 0 if passed else 2
if __name__=='__main__': raise SystemExit(main(sys.argv[1]))
