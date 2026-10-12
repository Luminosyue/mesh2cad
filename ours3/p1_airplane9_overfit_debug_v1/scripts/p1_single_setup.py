from pathlib import Path
import json,yaml,shutil,os,subprocess,tempfile,hashlib
root=Path('/data/home/cuiyuehan/project/mesh2cad');old=root/'ours3/p1_quick_overfit_airplane9_v1';debug=root/'ours3/p1_airplane9_overfit_debug_v1';single=root/'ours3/p1_single_airplane_part_overfit_v1'
single.mkdir(exist_ok=False)
for d in ['data','configs','launch','logs','audits','decode']:(single/d).mkdir()
storage=Path(tempfile.mkdtemp(prefix='cuiyuehan_p1_single_airplane_ckpts_',dir='/tmp'));(single/'runs').symlink_to(storage,target_is_directory=True)
train=[r for r in json.loads((old/'data/train.json').read_text()) if r['sample_id']=='airplane__PART_000'];assert len(train)==6
parts=[p for p in json.loads((old/'data/parts.json').read_text()) if p['part']=='PART_000'];assert len(parts)==1
for name,obj in [('train.json',train),('eval_memorization.json',train),('parts.json',parts)]: (single/'data'/name).write_text(json.dumps(obj,indent=2))
for name in ['curve_registry.jsonl','dataset_info.json']:shutil.copy2(old/'data'/name,single/'data'/name)
cfg=yaml.safe_load((old/'configs/train.yaml').read_text());cfg.update(dataset_dir=str(single/'data'),output_dir=str(single/'runs/quick'),logging_dir=str(single/'logs'),save_strategy='no',save_total_limit=None,eval_steps=100,max_steps=2000,overwrite_output_dir=False)
(single/'configs/train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
code=(old/'launch/cq54_train.py').read_text().replace('p1_quick_overfit_airplane9_v1','p1_single_airplane_part_overfit_v1')
addition='''    from transformers import TrainerCallback
    class Milestones(TrainerCallback):
        def on_step_end(self,args,state,control,**kwargs):
            if state.global_step in {100,200,500,1000,2000}:control.should_save=True
            return control
    original_init=Trainer.__init__
    def init_with_milestones(self,*a,**kw):
        original_init(self,*a,**kw)
        self.add_callback(Milestones())
    Trainer.__init__=init_with_milestones
    original_save=Trainer.save_model
    def save_checkpoint_only(self,output_dir=None,*a,**kw):
        if output_dir is None or str(output_dir)==str(EXP/'runs/quick'):return
        return original_save(self,output_dir,*a,**kw)
    Trainer.save_model=save_checkpoint_only
'''
code=code.replace('    old_step=Trainer.training_step',addition+'    old_step=Trainer.training_step')
(single/'launch/cq54_train.py').write_text(code)
manifest={'single_part':'airplane__PART_000','blocks':6,'initial_checkpoint':cfg['model_name_or_path'],'steps':2000,'save_steps':[100,200,500,1000,2000],'checkpoint_storage':str(storage),'reason':'/data has only 29 GiB free; new checkpoints on spacious root volume, exposed through experiment runs symlink','unchanged_gt':all(r in json.loads((old/'data/train.json').read_text()) for r in train)}
(single/'audits/setup.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest),flush=True)
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',PYTHONUNBUFFERED='1')
with (single/'logs/train.log').open('w') as log:
 proc=subprocess.Popen(['/usr/bin/python3','-u',str(single/'launch/cq54_train.py')],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,cwd=root,env=env,start_new_session=True)
(single/'status.json').write_text(json.dumps({'state':'TRAINING','pid':proc.pid,'gpu':1},indent=2));print('TRAIN PID',proc.pid)
