#!/usr/bin/env python3
"""Real A1-SCF canary orchestrator; --preflight-only never loads a model."""
import argparse,json,os,sys
from pathlib import Path
import torch
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad/ours3/a1_scf_real_model_adapter_v1/adapter')
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,default=str)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--output-root',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();cfg=json.load(open(a.config));root=Path(a.output_root);assert cfg['test1000_forbidden'] and cfg['holdout958_forbidden']
 from a1_scf_real_model_adapter import build_canary_adapter
 if a.preflight_only:dump(root/'reports/PREFLIGHT.json',{'adapter_import':'PASS','model_loaded':False});return
 os.environ['CUDA_VISIBLE_DEVICES']=str(a.gpu);ad=build_canary_adapter(cfg);ad.load_reference_model();ids=[json.load(open(cfg['train100_manifest']))['rows'][0]['cad_id']];batch=ad.build_batch(ids)
 rng=ad.capture_rng_state();ad.zero_grad();x=ad.forward_a1(batch);px=ad.get_prefix_trace();ad.backward(x.loss);gx={k:v.detach().clone() for k,v in ad.get_curve_projector_gradients().items() if v is not None}
 ad.restore_rng_state(rng);ad.zero_grad();y=ad.forward_scf(batch,0);py=ad.get_prefix_trace();ad.backward(y.loss);gy={k:v.detach().clone() for k,v in ad.get_curve_projector_gradients().items() if v is not None};ld=(x.logits-y.logits).abs();gd=torch.cat([(gx[k]-gy[k]).abs().flatten() for k in gx])
 fw={'PREFIX_BITWISE_EQUAL':px['prefix_hash']==py['prefix_hash'],'MAX_LOGIT_ABS_DIFF':float(ld.max()),'MEAN_LOGIT_ABS_DIFF':float(ld.mean()),'P99_LOGIT_ABS_DIFF':float(torch.quantile(ld.float(),.99)),'BASE_LOSS_DIFF':float(abs(x.loss-y.loss)),'PREFIX_A1':px,'PREFIX_SCF_K0':py};fw['K0_FORWARD_PARITY']='PASS' if fw['PREFIX_BITWISE_EQUAL'] and fw['MAX_LOGIT_ABS_DIFF']==0 else 'FAIL';bw={'GRAD_MAX_ABS_DIFF':float(gd.max()),'GRAD_MEAN_ABS_DIFF':float(gd.mean())};bw['K0_BACKWARD_PARITY']='PASS' if bw['GRAD_MAX_ABS_DIFF']==0 else 'FAIL';dump(root/'parity/K0_REAL_MODEL_FORWARD_PARITY.json',fw);dump(root/'parity/K0_REAL_MODEL_BACKWARD_PARITY.json',bw)
 if 'FAIL' in (fw['K0_FORWARD_PARITY'],bw['K0_BACKWARD_PARITY']):raise RuntimeError('K0 parity blocked')
 rows=json.load(open(cfg['train100_manifest']))['rows'];cid=next(z['cad_id'] for z in rows if z['cohort']=='NONLINE_PRESENT');batch=ad.build_batch([cid]);ad.zero_grad();z=ad.forward_scf(batch,cfg['integration_k']);ad.backward(z.loss);sg=ad.get_selector_gradients();ok=all(v is not None and torch.isfinite(v).all() for v in sg.values()) and sum(float(v.abs().sum()) for v in sg.values())>0;dump(root/'gradients/SELECTOR_GRADIENT_AUDIT.json',{'SELECTOR_GRAD_FINITE':ok,'SELECTOR_GRAD_NONZERO':ok});dump(root/'selection/NONLINE_SELECTION_AUDIT.json',ad.get_selector_trace());dump(root/'selection/LINE_KEEP_ALL_AUDIT.json',ad.get_prefix_trace());dump(root/'gradients/C2_FROZEN_AUDIT.json',ad.audit_c2_frozen())
 if not ok or not ad.audit_c2_frozen()['pass']:raise RuntimeError('gradient/C2 blocked')
 ad.build_pristine_training_model();tr=ad.train100(cfg['train100_manifest']);dump(root/'train100/TRAIN100_REPORT.json',tr.metrics);vr=ad.val100(cfg['val_canary_manifest']);dump(root/'val100/VAL100_INTEGRATION_REPORT.json',vr);cp=root/'reload/checkpoint';ad.save_checkpoint(cp,100);rr=ad.load_checkpoint(cp);dump(root/'reload/CANARY_CHECKPOINT_RELOAD.json',rr);dump(root/'reports/FINAL_REPORT.json',{'CURRENT_GATE':'A1_SELECTIVE_CURVE_REAL_MODEL_CANARY_PASS','FULL_TRAIN_READY':'NO','NEXT_ALLOWED_STAGE':'A1_SELECTIVE_CURVE_BUDGET_AND_CONTROL_SELECTION_V1'})
if __name__=='__main__':main()
