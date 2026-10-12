from pathlib import Path
import os,sys,json,hashlib,copy,zipfile,shutil,collections
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'partsam_p1_training_v1'
sys.path[:0]=[str(OUT/'scripts'),str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
os.environ['OMP_NUM_THREADS']='1'
import numpy as np,torch,cadquery as cq,yaml
torch.set_num_threads(2)

def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False,default=str))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    from partsam_p1_runtime import install
    install()
    from transformers import AutoTokenizer
    from spatiallm.tuner.data.template import register_spatiallm_templates,get_template_and_fix_tokenizer
    from spatiallm.tuner.hparams import DataArguments
    from spatiallm.tuner.data.collator import MultiModalDataCollatorForSeq2Seq
    from canonical_cad_data_v4.converters.cad_dsl import execute_dsl
    import p1_operation_loss_runtime as op
    cfg=yaml.safe_load((ROOT/'ours3/p1_operation_aware_structure_loss_v1/configs/p1_exact9998_train.yaml').read_text())
    tok=AutoTokenizer.from_pretrained(cfg['model_name_or_path'],use_fast=False,local_files_only=True)
    register_spatiallm_templates(cutoff_len=8192,num_bins=1280,do_augmentation=False,random_rotation=False)
    template=get_template_and_fix_tokenizer(tok,DataArguments(template='spatiallm_cad_llama_sepedge'))
    coll=MultiModalDataCollatorForSeq2Seq(tokenizer=tok,template=template,model=None)
    rows=[json.loads(x) for x in (OUT/'ASSET_REGISTRY.jsonl').read_text().splitlines()]
    validation=[];hashes={};object_splits=collections.defaultdict(set);cad_ids=set()
    for row in rows:
        dest=Path(row['surface_path']).parent;dsl=(dest/'program_canonical.dsl').read_text()
        fresh=OUT/'audits/reexecuted'/f"{row['sample_id']}.step"
        execute_dsl(dsl,fresh)
        a=cq.importers.importStep(row['step_path']).val();b=cq.importers.importStep(str(fresh)).val()
        dv=abs(a.Volume()-b.Volume())/max(abs(a.Volume()),1e-12);da=abs(a.Area()-b.Area())/max(a.Area(),1e-12)
        assert b.isValid() and len(a.Faces())==len(b.Faces()) and dv<1e-7 and da<1e-7
        assert sha(Path(row['source_path']))==row['source_sha256'],'source_changed'
        example=next(r for r in json.loads((OUT/f"partsam_p1_{row['split']}.json").read_text()) if r['id']==row['cad_id'])
        feature={'_prompt':[{'role':'user','content':example['conversations'][0]['value']}],
                 '_response':[{'role':'assistant','content':dsl}], '_point_clouds':example['point_clouds'],'_system':''}
        np.random.seed(20260919);batch=coll([feature]);ids=batch['input_ids'][0].tolist();labels=batch['labels'][0].tolist()
        response_ids=tok.encode(dsl,add_special_tokens=False)
        assert op.locate(ids,response_ids,valid=[x!=-100 for x in labels])>=0
        assert labels[-1]==tok.eos_token_id and int(batch['operation_mask'].sum())>0
        assert len(ids)+batch['point_clouds'].shape[1]+batch['edge_clouds'].shape[1]<=8192
        object_splits[row['object_id']].add(row['split']);assert row['cad_id'] not in cad_ids;cad_ids.add(row['cad_id'])
        for p in dest.iterdir():
            if p.is_file():hashes[str(p.relative_to(OUT))]=sha(p)
        validation.append({'cad_id':row['cad_id'],'split':row['split'],'program_reexecution':'PASS',
            'relative_volume_difference':dv,'relative_area_difference':da,'configured_tokenizer_collator':'PASS','source_hash_unchanged':True})
    assert all(len(s)==1 for s in object_splits.values())
    summary=json.loads((OUT/'FINAL_SUMMARY.json').read_text())
    summary.update(program_reexecution_pass_count=len(validation),configured_tokenizer_collator_pass_count=len(validation),
                   source_hash_recheck_pass_count=len(validation),object_split_overlap_count=0)
    dump(OUT/'FINAL_SUMMARY.json',summary);dump(OUT/'audits/FINAL_VERIFICATION.json',validation)
    cfg.update(dataset='partsam_p1_train',eval_dataset='partsam_p1_val',dataset_dir=str(OUT),
               output_dir=str(OUT/'runs/p1_pilot'),logging_dir=str(OUT/'logs/tensorboard'),
               eval_strategy='epoch',save_strategy='epoch',num_train_epochs=1,gradient_accumulation_steps=1,
               logging_steps=1,save_total_limit=2,dataloader_num_workers=0)
    (OUT/'configs').mkdir(exist_ok=True);(OUT/'configs/p1_partsam_pilot.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
    for p in [*OUT.glob('*.json'),*OUT.glob('*.jsonl'),*OUT.glob('scripts/*.py'),*OUT.glob('masks/*.jsonl'),*OUT.glob('configs/*.yaml')]:
        hashes[str(p.relative_to(OUT))]=sha(p)
    dump(OUT/'RELEASE_SHA256.json',hashes)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
