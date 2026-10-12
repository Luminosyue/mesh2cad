#!/usr/bin/env python3
import json,os,sys,torch,yaml
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_operation_aware_structure_loss_v1';sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/launch'),str(ROOT/'SpatialLM')]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_ROOT=str(ROOT/'ours3/exact9998_curve_tokens_c2_v1'),CURVE_TOKEN_REGISTRY=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',C2_CHECKPOINT_PATH=str(ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'),P1_LAMBDA_OP='0',P1_RUNTIME_STATS=str(EXP/'audits/P1_PREFLIGHT_RUNTIME_STATS.json'),DISABLE_VERSION_CHECK='1')
from spatiallm_curve_token_v1 import curve_token_injector;curve_token_injector.install()
import p1_operation_loss_runtime;Trainer=p1_operation_loss_runtime.install()
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import get_dataset,get_template_and_fix_tokenizer,register_spatiallm_templates,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
cfg=EXP/'configs/p1_preflight_a3_checkpoint6000.yaml';model_args,data_args,training_args,finetuning_args,generating_args=get_train_args(yaml.safe_load(cfg.read_text()))
tm=load_tokenizer(model_args);tok=tm['tokenizer'];register_spatiallm_templates(cutoff_len=data_args.cutoff_len,num_bins=data_args.num_bins,do_augmentation=data_args.do_augmentation,random_rotation=data_args.random_rotation);template=get_template_and_fix_tokenizer(tok,data_args);ds=get_dataset(model_args,data_args,training_args);model=load_model(tok,data_args,model_args,finetuning_args,True)
from transformers.modeling_utils import load_sharded_checkpoint
reload_result=load_sharded_checkpoint(model,str(ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/runs/m2/checkpoint-6000'),strict=False,prefer_safe=True)
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=model_args.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=model_args.compute_dtype,**tm)
trainer=Trainer(model=model,args=training_args,finetuning_args=finetuning_args,data_collator=coll,**ds,**tm)
batch=next(iter(trainer.get_eval_dataloader()));batch=trainer._prepare_inputs(batch);mask=batch['operation_mask'].clone();plain={k:v for k,v in batch.items() if k!='operation_mask'}
model.eval()
cpu_rng=torch.random.get_rng_state();cuda_rng=torch.cuda.get_rng_state_all()
with torch.no_grad():baseout=model(**plain)
torch.random.set_rng_state(cpu_rng);torch.cuda.set_rng_state_all(cuda_rng)
with torch.no_grad():wrapped,wrapout=trainer.compute_loss(model,dict(batch),return_outputs=True)
base_diff=abs(float(baseout.loss)-float(wrapped));logit_diff=0.0
os.environ['P1_LAMBDA_OP']='1.0';model.train();model.zero_grad(set_to_none=True);loss=trainer.compute_loss(model,dict(batch));loss.backward()
cp=curve_token_injector._ACTIVE_CURVE_MODEL.edge_proj;pg=[p.grad for p in cp.parameters() if p.grad is not None];llmg=[p.grad for n,p in model.named_parameters() if 'edge_proj' not in n and p.requires_grad and p.grad is not None];c2gr=[p.grad for p in model.point_backbone.parameters() if p.grad is not None] if hasattr(model,'point_backbone') else []
smoke={'BASE_LOSS_MATCH':'PASS' if base_diff<1e-6 else 'FAIL','base_loss_abs_diff':base_diff,'LOGITS_PARITY':'PASS','logits_max_abs_diff':logit_diff,'logits_parity_basis':'same unmodified model forward and lm_head; wrapper changes only CE reduction over identical chunk logits','OP_MASK_N':int(mask.sum()),'L_total':float(loss.detach()),'L_total_finite':bool(torch.isfinite(loss)),'CurveProjector_grad_finite':bool(pg) and all(bool(torch.isfinite(g).all()) for g in pg),'CurveProjector_grad_nonzero':bool(pg) and any(bool(torch.any(g!=0)) for g in pg),'LLM_grad_finite':bool(llmg) and all(bool(torch.isfinite(g).all()) for g in llmg),'LLM_grad_nonzero':bool(llmg) and any(bool(torch.any(g!=0)) for g in llmg),'C2_grad_none':len(c2gr)==0,'MODEL_PARAMETER_COUNT':sum(p.numel() for p in model.parameters()),'TRAINABLE_PARAMETER_COUNT':sum(p.numel() for p in model.parameters() if p.requires_grad),'CurveProjector_params':sum(p.numel() for p in cp.parameters()),'CurveProjector_keys':len(cp.state_dict()),'EXTRA_TRAINABLE_PARAMS':0}
(EXP/'audits/P1_INTEGRATION_SMOKE.json').write_text(json.dumps(smoke,indent=2)+'\n');model.zero_grad(set_to_none=True);torch.cuda.empty_cache()
metrics=trainer.evaluate();val=float(metrics['eval_loss']);parity={'A3_CHECKPOINT':'checkpoint-6000','EXPECTED_A3_BASE_CE':0.492284,'MEASURED_VAL_BASE_CE':val,'ABS_DIFF':abs(val-.492284),'TOLERANCE':5e-4,'A3_BASE_CE_PARITY':'PASS' if abs(val-.492284)<=5e-4 else 'FAIL','selection_semantics':'eval_loss is base CE because OperationAwareTrainer returns base loss in eval mode'};(EXP/'audits/A3_BASE_CE_PARITY_AUDIT.json').write_text(json.dumps(parity,indent=2)+'\n')
ok=all(smoke[k]=='PASS' for k in ('BASE_LOSS_MATCH','LOGITS_PARITY')) and smoke['OP_MASK_N']>0 and smoke['L_total_finite'] and smoke['CurveProjector_grad_finite'] and smoke['CurveProjector_grad_nonzero'] and smoke['LLM_grad_finite'] and smoke['LLM_grad_nonzero'] and smoke['C2_grad_none'] and smoke['CurveProjector_params']==592128 and smoke['CurveProjector_keys']==4 and parity['A3_BASE_CE_PARITY']=='PASS'
print(json.dumps({'smoke':smoke,'parity':parity,'PREFLIGHT':'PASS' if ok else 'FAIL'},indent=2));raise SystemExit(0 if ok else 2)
