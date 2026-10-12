from pathlib import Path
import os,sys,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_quick_overfit_airplane9_v1'
sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts'),str(ROOT)]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_REGISTRY=str(EXP/'data/curve_registry.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',DISABLE_VERSION_CHECK='1')
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector._DATASET_BY_PACK_DIR['XPart']='xpart'
curve_token_injector.install()

def main():
    import torch
    import time
    from transformers import Trainer
    old_step=Trainer.training_step
    started=time.time()
    calls=[0]
    def step(self,*args,**kwargs):
        loss=old_step(self,*args,**kwargs);calls[0]+=1
        if calls[0]==1 or calls[0]%40==0:
            snapshot={'global_step':self.state.global_step,'microbatches':calls[0],'last_scaled_loss':float(loss.detach()),'elapsed_seconds':time.time()-started,'peak_allocated_gib':torch.cuda.max_memory_allocated()/1024**3,'peak_reserved_gib':torch.cuda.max_memory_reserved()/1024**3,'finite':bool(torch.isfinite(loss))}
            (EXP/'audits/gpu_progress.json').write_text(json.dumps(snapshot,indent=2))
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
        return model
    loader.load_model=load
    import spatiallm.tuner.trainer as trainer
    trainer.load_model=load
    os.chdir(ROOT/'SpatialLM');sys.argv=[sys.argv[0],str(EXP/'configs/train.yaml')]
    trainer.run_exp()
if __name__=='__main__':main()

