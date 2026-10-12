from pathlib import Path
import os,sys,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_tank_allparts_exact_overfit_v1'
sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts'),str(ROOT)]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_REGISTRY=str(EXP/'data/curve_registry.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',DISABLE_VERSION_CHECK='1')
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector._DATASET_BY_PACK_DIR['XPart']='xpart'
curve_token_injector.install()

def main():
    import torch
    import time
    from transformers import Trainer
    import hashlib,numpy as np
    from collections import Counter
    from transformers import TrainerCallback
    lookup=json.loads((EXP/'data/label_lookup.json').read_text())
    counts=Counter();block_counts=Counter();calls=[0];losses=[];started=time.time()
    def save(name,obj):
        path=EXP/name;path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(obj,indent=2));tmp.replace(path)
    class Milestones(TrainerCallback):
        def on_step_end(self,args,state,control,**kwargs):
            if state.global_step in {25,50,100,150,200,300,400,500,750,1000}:control.should_save=True
            if time.time()-started>=14400:control.should_training_stop=True;control.should_save=True
            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True
            return control
        def on_save(self,args,state,control,**kwargs):
            snap={'optimizer_steps':state.global_step,'microbatches':calls[0],'part_exposures':dict(counts),'block_exposures':dict(block_counts),'last_loss':losses[-1],'last_10_mean_loss':sum(losses[-10:])/len(losses[-10:]),'elapsed_seconds':time.time()-started}
            save('audits/exposure_checkpoint-'+str(state.global_step)+'.json',snap)
            save('control/checkpoint-'+str(state.global_step)+'.ready',snap)

            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True
            return control
    class EqualPartSampler(torch.utils.data.Sampler):
        def __init__(self, dataset, collator):
            groups={p:[] for p in [f'PART_{j:03d}' for j in range(45)]}
            for i in range(len(dataset)):
                from transformers import set_seed
                set_seed(42)
                batch=collator([__import__('copy').deepcopy(dataset[i])])
                active=batch['labels'][0];labels=active[active!=-100].cpu().numpy().astype('<i8')
                row=lookup[hashlib.sha256(labels.tobytes()).hexdigest()]
                groups[row['part']].append(i)
            assert sorted(map(len,groups.values()))==sorted([len([x for x in lookup.values() if x['part']==f'PART_{j:03d}']) for j in range(45)])
            rng=__import__('random').Random(42);queues={p:[] for p in groups};self.indices=[]
            for _ in range(1000):
                for part,indices in groups.items():
                    if not queues[part]:queues[part]=rng.sample(indices,len(indices))
                    self.indices.append(queues[part].pop())
            save('audits/equal_part_sampler.json',{'indices':self.indices,'groups':groups,'microbatches_per_part':1000,'each_update':'one block per part; nine microbatches accumulated','seed':42,'optimizer_state':'fresh AdamW; checkpoint-2000 saved model only; no state borrowed from checkpoint-3000','remaining_update_budget':1000})
        def __iter__(self):return iter(self.indices)
        def __len__(self):return len(self.indices)
    def equal_sampler(self,*args,**kwargs):return EqualPartSampler(self.train_dataset,self.data_collator)
    Trainer._get_train_sampler=equal_sampler
    old_init=Trainer.__init__
    def init(self,*a,**kw):
        old_init(self,*a,**kw);self.add_callback(Milestones())
    Trainer.__init__=init
    original_save=Trainer.save_model
    def save_checkpoint_only(self,output_dir=None,*a,**kw):
        if output_dir is None or str(output_dir)==str(EXP/'runs/quick'):return
        return original_save(self,output_dir,*a,**kw)
    Trainer.save_model=save_checkpoint_only
    original_checkpoint=Trainer._save_checkpoint
    def checkpoint(self,*a,**kw):
        old=self.args.save_only_model
        if self.state.global_step in {25,50,100,150,200,300,400,500,750,1000}:self.args.save_only_model=False
        try:return original_checkpoint(self,*a,**kw)
        finally:self.args.save_only_model=old
    Trainer._save_checkpoint=checkpoint
    old_step=Trainer.training_step
    def step(self,model,inputs,*args,**kwargs):
        samples=[]
        for labels in inputs['labels']:
            ids=labels[labels!=-100].detach().cpu().numpy().astype('<i8')
            sample=lookup[hashlib.sha256(ids.tobytes()).hexdigest()];samples.append(sample)
        loss=old_step(self,model,inputs,*args,**kwargs);calls[0]+=1
        for sample in samples:counts[sample['part']]+=1;block_counts[sample['id']]+=1
        assert max(counts.get(f'PART_{j:03d}',0) for j in range(45))-min(counts.get(f'PART_{j:03d}',0) for j in range(45))<=1
        value=float(loss.detach());losses.append(value)
        assert bool(torch.isfinite(loss)),'Non-finite training loss'
        snapshot={'global_step':self.state.global_step+1,'microbatches':calls[0],'last_scaled_loss':value,'elapsed_seconds':time.time()-started,'peak_allocated_gib':torch.cuda.max_memory_allocated()/1024**3,'peak_reserved_gib':torch.cuda.max_memory_reserved()/1024**3,'finite':True,'part_exposures':dict(counts),'samples':samples}
        with (EXP/'audits/training_steps.jsonl').open('a') as f:f.write(json.dumps(snapshot)+'\n')
        if calls[0]==1 or calls[0]%10==0:save('audits/gpu_progress.json',snapshot)
        return loss
    Trainer.training_step=step
    import spatiallm.tuner.framework.loader as loader
    original=loader.load_model
    def load(*args,**kwargs):
        model=original(*args,**kwargs)
        from transformers.modeling_utils import load_sharded_checkpoint
        ckpt=ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'
        result=load_sharded_checkpoint(model,str(ckpt),strict=False,prefer_safe=True)
        trainable={n for n,p in model.named_parameters() if p.requires_grad}
        missing=[n for n in result.missing_keys if n in trainable]
        assert not missing,missing
        assert any(n.startswith('edge_proj.') for n in trainable)
        assert not any(n.startswith('point_backbone.') for n in trainable)
        from separate_edge_tokens_v1.common import set_deterministic_serialization
        set_deterministic_serialization(model.point_backbone)
        (EXP/'audits/weight_reload.json').write_text(json.dumps({'checkpoint':str(ckpt),'missing':result.missing_keys,'unexpected':result.unexpected_keys,'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),'loss':'standard CE; DSL operation-loss patch not installed'},indent=2))
        def dtype_hook(name):
            def hook(module,inputs):
                path=EXP/('audits/training_'+name+'_dtype.json')
                if not path.exists():save(str(path.relative_to(EXP)),{'input_dtype':str(inputs[0].dtype),'weight_dtype':str(next(module.parameters()).dtype),'autocast_enabled':torch.is_autocast_enabled()})
            return hook
        model.point_proj.register_forward_pre_hook(dtype_hook('surface_projector'))
        model.edge_proj.register_forward_pre_hook(dtype_hook('curve_projector'))
        return model
    loader.load_model=load
    import spatiallm.tuner.trainer as trainer
    trainer.load_model=load
    os.chdir(ROOT/'SpatialLM');sys.argv=[sys.argv[0],str(EXP/'configs/train.yaml')]
    trainer.run_exp()
if __name__=='__main__':main()

