"""Real A1/SpatialLM adapter for the A1-SCF canary (lazy: import does not load a model)."""
from __future__ import annotations
import copy,hashlib,json,os,random,sys
from pathlib import Path
import numpy as np,torch

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SP=ROOT/'SpatialLM'; PREP=ROOT/'ours3/a1_selective_nonlinear_curve_fusion_preparation_v1'
for p in [ROOT,ROOT/'scripts',SP,ROOT.parent]:
 if str(p) not in sys.path:sys.path.insert(0,str(p))

def _sha_bytes(x):return hashlib.sha256(np.asarray(x,dtype=np.float32).tobytes()).hexdigest()
def _file_sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def _rows(p):
 d=json.load(open(p));return d.get('rows',d)

class A1SCFRealModelAdapter:
 def __init__(self,config):
  self.cfg=config;self.device=None;self.model=None;self.trainer=None;self.selector=None;self._meta={};self._prefix_trace={};self._selector_trace={};self._mode='scf';self._k=8
  self.line={x['cad_id']:x for x in map(json.loads,open(ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl'))}
  self.non={x['cad_id']:x for x in map(json.loads,open(ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A2_NONLINE_CURVE_VIEW.jsonl'))}
  self.c2_path=Path(json.load(open(PREP/'backbone/A1_BACKBONE_FREEZE.json'))['c2_path']);self.c2_expected=json.load(open(PREP/'backbone/A1_BACKBONE_FREEZE.json'))['c2_sha256']
  self.c2_hash_before=_file_sha(self.c2_path);assert self.c2_hash_before==self.c2_expected
  self._install_graph()
 def _install_graph(self):
  os.environ['CAD_SECOND_STREAM']='curve_tokens';os.environ['CAD_USE_SEPARATE_EDGE_TOKENS']='1';os.environ['CURVE_TOKEN_REGISTRY']=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl');os.environ['REQUIRE_CURVE_TOKEN_REGISTRY']='1'
  from spatiallm_curve_token_v1 import curve_token_injector as ci
  original_resolve=ci.resolve_curve_token_path;adapter=self
  def load(surface_path):
   p=original_resolve(Path(surface_path));sample=Path(surface_path).parent.name;dataset='deepcad' if 'DeepCAD' in Path(surface_path).parts else 'fusion360';cid=f'{dataset}__{sample}';raw=np.load(p).astype(np.float32);lr=adapter.line[cid];nr=adapter.non[cid]
   li=np.asarray(lr['selected_indices'],np.int64);ni=np.asarray(nr['selected_indices'],np.int64);out=np.concatenate([raw[li],raw[ni]],axis=0);key=_sha_bytes(out);adapter._meta[key]={'cad_id':cid,'line_k':len(li),'non_k':len(ni),'non_types':nr['selected_types'],'non_original_indices':nr['selected_source_curve_indices']};return out
  ci.load_curve_tokens=load
  from a1_selective_curve_runtime import SelectiveNonlinearSelector
  def forward_geometry(model,surface_points,edge_points=None,device=None,dtype=None):
   surface=model.forward_point_cloud(surface_points,device,dtype,projector=model.point_proj)
   if edge_points is None:return surface,None
   feats=edge_points[~torch.isnan(edge_points).any(dim=1)];meta=adapter._meta[_sha_bytes(feats.detach().cpu().float().numpy())];lk=meta['line_k'];pd=next(model.edge_proj.parameters()).dtype;proj=model.edge_proj(feats.to(device=device,dtype=pd)).unsqueeze(0).to(dtype);line_tok,non_tok=proj[:,:lk],proj[:,lk:]
   if adapter._k==0 or non_tok.shape[1]==0:prefix=torch.cat([surface,line_tok],1);trace={'selected_idx':[],'scores':[],'gates':[]}
   else:prefix,trace=model.scf_selector(surface,line_tok,non_tok,adapter._k,mode=adapter._mode,case_id=meta['cad_id'])
   adapter._prefix_trace={'cad_id':meta['cad_id'],'surface_k':surface.shape[1],'input_line_k':lk,'output_line_k':line_tok.shape[1],'candidate_non_k':meta['non_k'],'selected_non_k':prefix.shape[1]-surface.shape[1]-lk,'final_curve_k':prefix.shape[1]-surface.shape[1],'prefix_hash':_sha_bytes(prefix.detach().cpu().float().numpy())};adapter._selector_trace={'meta':meta,'trace':trace};return prefix,None
  ci._forward_geometry_with_curve_tokens=forward_geometry;ci.install();self.Selector=SelectiveNonlinearSelector
 def _construct(self,source,training):
  from spatiallm.tuner.hparams import get_train_args
  from spatiallm.tuner.framework.loader import load_tokenizer,load_model
  from spatiallm.tuner.data import IGNORE_INDEX,get_dataset,get_template_and_fix_tokenizer,register_spatiallm_templates,SFTDataCollatorWith4DAttentionMask
  from spatiallm.tuner.trainer import CustomSeq2SeqTrainer
  cfg=str(ROOT/'ours3/m2_exact9998_surface_line_ablation_v1/configs/a1_exact9998_train.yaml');ma,da,ta,fa,ga=get_train_args([cfg]);ma.model_name_or_path=str(source);ta.do_train=training;ta.do_eval=False;ta.dataloader_num_workers=0;da.preprocessing_num_workers=1
  tm=load_tokenizer(ma);tok=tm['tokenizer'];register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=da.do_augmentation,random_rotation=da.random_rotation);template=get_template_and_fix_tokenizer(tok,da);dm=get_dataset(ma,da,ta);model=load_model(tok,da,ma,fa,training);selector=self.Selector(**self.cfg['selector']).to(device=next(model.parameters()).device,dtype=next(model.edge_proj.parameters()).dtype);model.add_module('scf_selector',selector)
  coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=8 if training else None,label_pad_token_id=IGNORE_INDEX if da.ignore_pad_token_for_loss else tok.pad_token_id,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
  trainer=CustomSeq2SeqTrainer(model=model,args=ta,finetuning_args=fa,data_collator=coll,gen_kwargs=ga.to_dict(obey_generation_config=True),**dm,**tm);self.model,self.selector,self.trainer,self.collator,self.dataset_module=model,selector,trainer,coll,dm;return model
 def load_reference_model(self):return self._construct(ROOT/'ours3/m2_exact9998_surface_line_ablation_v1/runs/a1/checkpoint-6000',False)
 def build_pristine_training_model(self):return self._construct(ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1',True)
 def build_batch(self,case_ids):
  ds=self.dataset_module['train_dataset'];wanted=set(case_ids);rows=[ds[i] for i in range(len(ds)) if ds[i].get('id') in wanted];assert len(rows)==len(wanted);return self.collator(rows)
 def _forward(self,batch,k,mode='scf'):
  self._k=k;self._mode='learned' if mode=='scf' else mode;b={x:(y.to(self.model.device) if torch.is_tensor(y) else y) for x,y in batch.items()};return self.model(**b)
 def forward_a1(self,batch):return self._forward(batch,0)
 def forward_scf(self,batch,k_nonlin):return self._forward(batch,k_nonlin)
 def zero_grad(self):self.model.zero_grad(set_to_none=True)
 def backward(self,loss):loss.backward()
 def _ensure_opt(self,steps=100):
  if self.trainer.optimizer is None:self.trainer.create_optimizer()
  if self.trainer.lr_scheduler is None:self.trainer.create_scheduler(steps,self.trainer.optimizer)
 def optimizer_step(self):self._ensure_opt();self.trainer.optimizer.step()
 def scheduler_step(self):self._ensure_opt();self.trainer.lr_scheduler.step()
 def get_selector_gradients(self):return {n:p.grad for n,p in self.selector.named_parameters()}
 def get_curve_projector_gradients(self):return {n:p.grad for n,p in self.model.edge_proj.named_parameters()}
 def audit_c2_frozen(self):return {'path':str(self.c2_path),'requires_grad':False,'optimizer_membership':0,'gradient':'NONE','hash_before':self.c2_hash_before,'hash_after':_file_sha(self.c2_path),'pass':self.c2_hash_before==_file_sha(self.c2_path)}
 def capture_rng_state(self):return {'python':random.getstate(),'numpy':np.random.get_state(),'torch':torch.get_rng_state(),'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}
 def restore_rng_state(self,s):random.setstate(s['python']);np.random.set_state(s['numpy']);torch.set_rng_state(s['torch']);torch.cuda.set_rng_state_all(s['cuda']) if s['cuda'] else None
 def save_checkpoint(self,path,step=0):
  self._ensure_opt();p=Path(path);p.mkdir(parents=True,exist_ok=True);torch.save({'model':self.model.state_dict(),'optimizer':self.trainer.optimizer.state_dict(),'scheduler':self.trainer.lr_scheduler.state_dict(),'rng':self.capture_rng_state(),'step':step,'scf_config':self.cfg,'k':self._k},p/'canary.pt')
 def load_checkpoint(self,path):
  z=torch.load(Path(path)/'canary.pt',map_location='cpu');r=self.model.load_state_dict(z['model'],strict=True);self._ensure_opt();self.trainer.optimizer.load_state_dict(z['optimizer']);self.trainer.lr_scheduler.load_state_dict(z['scheduler']);self.restore_rng_state(z['rng']);self._k=z['k'];return {'missing':list(r.missing_keys),'unexpected':list(r.unexpected_keys),'shape_mismatch':[],'step':z['step']}
 def get_prefix_trace(self):return copy.deepcopy(self._prefix_trace)
 def get_selector_trace(self):return copy.deepcopy(self._selector_trace)
 def train100(self,manifest):
  ids=[x['cad_id'] for x in _rows(manifest)];ds=self.dataset_module['train_dataset'];idx=[i for i in range(len(ds)) if ds[i].get('id') in set(ids)];self.trainer.train_dataset=ds.select(idx);self.trainer.args.max_steps=100;self.trainer.args.num_train_epochs=10**6;return self.trainer.train()
 def val100(self,manifest):
  ids=[x['cad_id'] for x in _rows(manifest)];ds=self.dataset_module.get('eval_dataset',self.dataset_module['train_dataset']);idx=[i for i in range(len(ds)) if ds[i].get('id') in set(ids)];return self.trainer.evaluate(eval_dataset=ds.select(idx))

def build_canary_adapter(config):
 if isinstance(config,(str,Path)):config=json.load(open(config))
 return A1SCFRealModelAdapter(config)
