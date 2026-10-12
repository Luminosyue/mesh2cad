from pathlib import Path
import sys,json,random,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1'
assert json.loads((E/'diagnostics/path_gate.json').read_text())['PASS']
assert json.loads((E/'evaluations/baseline_fixed/summary.json').read_text())['complete_case_n']==3,'Must finish corrected checkpoint-2000 evaluation before training'
import yaml
cfg=yaml.safe_load((OLD/'configs/train.yaml').read_text());cfg.update(model_name_or_path=str(OLD/'runs/quick/checkpoint-2000'),dataset_dir=str(E/'data'),output_dir=str(E/'runs/quick'),logging_dir=str(E/'logs'),max_steps=150,learning_rate=1e-5,gradient_accumulation_steps=3,eval_strategy='no',save_strategy='no',save_only_model=True,seed=42,data_seed=42,do_augmentation=False,random_rotation=False)
(E/'configs/train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
source=(OLD/'launch/a2_train.py').read_text()
source=source.replace("EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'","EXP=ROOT/'ours3/p1_airplane3_debug_fast_v1'")
source=source.replace("ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'","ROOT/'ours3/p1_airplane3_exact_overfit_v1/runs/quick/checkpoint-2000'")
source=source.replace('{250,500,750,1000,1500,2000,2500,3000,4000,5000}','{60,150}')
source=source.replace('in {3000,4000}:self.args.save_only_model=False','in {60,150}:self.args.save_only_model=False')
source=source.replace("            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True","            if time.time()-started>=1200:control.should_training_stop=True;control.should_save=True\n            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True")
anchor='    old_init=Trainer.__init__'
insertion='''    class EqualPartSampler(torch.utils.data.Sampler):
        def __init__(self, dataset, collator):
            groups={p:[] for p in ['PART_000','PART_001','PART_005']}
            for i in range(len(dataset)):
                from transformers import set_seed
                set_seed(42)
                batch=collator([__import__('copy').deepcopy(dataset[i])])
                active=batch['labels'][0];labels=active[active!=-100].cpu().numpy().astype('<i8')
                row=lookup[hashlib.sha256(labels.tobytes()).hexdigest()]
                groups[row['part']].append(i)
            assert sorted(map(len,groups.values()))==[6,13,25]
            rng=__import__('random').Random(42);queues={p:[] for p in groups};self.indices=[]
            for _ in range(150):
                for part,indices in groups.items():
                    if not queues[part]:queues[part]=rng.sample(indices,len(indices))
                    self.indices.append(queues[part].pop())
            save('audits/equal_part_sampler.json',{'indices':self.indices,'groups':groups,'microbatches_per_part':150,'each_update':'one block per part; three microbatches accumulated','seed':42,'optimizer_state':'fresh AdamW; checkpoint-2000 saved model only; no state borrowed from checkpoint-3000','remaining_update_budget':150})
        def __iter__(self):return iter(self.indices)
        def __len__(self):return len(self.indices)
    def equal_sampler(self,*args,**kwargs):return EqualPartSampler(self.train_dataset,self.data_collator)
    Trainer._get_train_sampler=equal_sampler
'''
assert anchor in source;source=source.replace(anchor,insertion+anchor)
(E/'launch/fast_train_resolved.py').write_text(source)
exec(compile(source,str(E/'launch/fast_train_resolved.py'),'exec'),{'__name__':'__main__','__file__':str(E/'launch/fast_train_resolved.py')})
