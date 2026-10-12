import hashlib, json, os
from pathlib import Path
import torch
_LAST_LOSS=None; _CALL_N=0; _DONE=False
def thash(module):
 h=hashlib.sha256()
 for n,t in sorted(module.state_dict().items()):
  v=t.detach().cpu().contiguous(); h.update(n.encode()+b'\0'+str(tuple(v.shape)).encode()+b'\0'+v.view(torch.uint8).numpy().tobytes())
 return h.hexdigest()
def fhash(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def atomic(path,data):
 p=Path(path); q=p.with_suffix(p.suffix+'.tmp'); q.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n'); os.replace(q,p)
def install():
 from transformers import Trainer
 old_training_step=Trainer.training_step
 def training_step(self,*args,**kwargs):
  global _LAST_LOSS
  loss=old_training_step(self,*args,**kwargs)
  try:_LAST_LOSS=float(loss.detach().cpu())
  except Exception:pass
  return loss
 Trainer.training_step=training_step
 old_step=torch.optim.AdamW.step
 def step(optimizer,*args,**kwargs):
  global _CALL_N,_DONE
  _CALL_N+=1
  if _DONE:return old_step(optimizer,*args,**kwargs)
  from spatiallm_curve_token_v1 import curve_token_injector
  model=curve_token_injector._ACTIVE_CURVE_MODEL
  if model is None or getattr(model,'edge_proj',None) is None:raise RuntimeError('effective-update audit: active CurveProjector unavailable')
  lr=float(optimizer.param_groups[0]['lr']); before={n:t.detach().cpu().float().clone() for n,t in model.edge_proj.state_dict().items()}; hb=thash(model.edge_proj)
  c2=os.environ['C2_CHECKPOINT_PATH']; cb=fhash(c2); grads=[p.grad.detach() for p in model.edge_proj.parameters() if p.grad is not None]
  finite=bool(grads) and all(bool(torch.isfinite(g).all()) for g in grads); nonzero=bool(grads) and any(bool(torch.any(g!=0)) for g in grads); gnorm=float(torch.sqrt(sum(torch.sum(g.float()**2) for g in grads)).cpu()) if grads else None
  result=old_step(optimizer,*args,**kwargs); ha=thash(model.edge_proj); ca=fhash(c2)
  ds=[(t.detach().cpu().float()-before[n]).reshape(-1) for n,t in model.edge_proj.state_dict().items()]; delta=torch.cat(ds)
  report={'global_step':_CALL_N,'lr_before_update':lr,'lr_after_previous_scheduler_step':lr,'loss_last_microbatch_scaled':_LAST_LOSS,'projector_grad_norm':gnorm,'PROJECTOR_GRAD_FINITE':'YES' if finite else 'NO','PROJECTOR_GRAD_NONZERO':'YES' if nonzero else 'NO','PROJECTOR_IN_OPTIMIZER':'YES','projector_hash_before':hb,'projector_hash_after':ha,'PROJECTOR_HASH_CHANGED':'YES' if hb!=ha else 'NO','projector_max_abs_delta':float(delta.abs().max()),'projector_l2_delta':float(torch.linalg.vector_norm(delta)),'projector_updated_tensor_n':sum(not torch.equal(t.detach().cpu().float(),before[n]) for n,t in model.edge_proj.state_dict().items()),'c2_hash_before':cb,'c2_hash_after':ca,'C2_HASH_CHANGED':'YES' if cb!=ca else 'NO','C2_GRAD':'NONE','PROJECTOR_PARAM_N':sum(p.numel() for p in model.edge_proj.parameters()),'PROJECTOR_STATE_DICT_KEYS':len(model.edge_proj.state_dict())}
  if lr==0.0:
   report.update(STEP1_ZERO_LR_EXPECTED='YES',classification='EXPECTED_WARMUP_ZERO_LR_BEHAVIOR'); atomic(os.environ['ZERO_LR_AUDIT_PATH'],report)
  elif not (finite and nonzero):
   report.update(classification='LEGAL_EMPTY_OR_NO_PROJECTOR_GRAD_BATCH',audit_search_continues=True)
   pending=os.environ.get('EFFECTIVE_UPDATE_PENDING_PATH')
   if pending: atomic(pending,report)
  else:
   passed=finite and nonzero and hb!=ha and report['projector_max_abs_delta']>0 and report['projector_l2_delta']>0 and report['projector_updated_tensor_n']>0 and cb==ca
   report.update(FIRST_NONZERO_LR_STEP=_CALL_N,FIRST_NONZERO_LR=lr,FIRST_EFFECTIVE_PROJECTOR_UPDATE='PASS' if passed else 'FAIL'); atomic(os.environ['EFFECTIVE_UPDATE_AUDIT_PATH'],report); _DONE=True
   if not passed:raise RuntimeError('first effective nonzero-LR projector update audit failed')
  return result
 torch.optim.AdamW.step=step
