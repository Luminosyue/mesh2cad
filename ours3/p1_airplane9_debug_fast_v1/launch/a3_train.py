from pathlib import Path
import sys,json,random,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1'
assert json.loads((E/'audits/data_gate.json').read_text())['PASS']
import yaml
cfg=yaml.safe_load((OLD/'configs/train.yaml').read_text());cfg.update(model_name_or_path=str(E.parent/'p1_quick_overfit_airplane9_v1/runs/quick/checkpoint-2000'),dataset_dir=str(E/'data'),output_dir=str(E/'runs/quick'),logging_dir=str(E/'logs'),max_steps=500,learning_rate=1e-5,gradient_accumulation_steps=9,eval_strategy='no',save_strategy='no',save_only_model=True,seed=42,data_seed=42,do_augmentation=False,random_rotation=False)
(E/'configs/train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
source=(OLD/'launch/a2_train.py').read_text()
source=source.replace("EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'","EXP=ROOT/'ours3/p1_airplane9_debug_fast_v1'")
source=source.replace("ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'","ROOT/'ours3/p1_quick_overfit_airplane9_v1/runs/quick/checkpoint-2000'")
source=source.replace('{250,500,750,1000,1500,2000,2500,3000,4000,5000}','{10,20,30,40,60,80,100,150,200,300,400,500}')
source=source.replace('in {3000,4000}:self.args.save_only_model=False','in {10,20,30,40,60,80,100,150,200,300,400,500}:self.args.save_only_model=False')
source=source.replace("            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True","            if time.time()-started>=14400:control.should_training_stop=True;control.should_save=True\n            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True")
anchor='    old_init=Trainer.__init__'
insertion='''    class EqualPartSampler(torch.utils.data.Sampler):
        def __init__(self, dataset, collator):
            groups={p:[] for p in [f'PART_{j:03d}' for j in range(9)]}
            for i in range(len(dataset)):
                from transformers import set_seed
                set_seed(42)
                batch=collator([__import__('copy').deepcopy(dataset[i])])
                active=batch['labels'][0];labels=active[active!=-100].cpu().numpy().astype('<i8')
                row=lookup[hashlib.sha256(labels.tobytes()).hexdigest()]
                groups[row['part']].append(i)
            assert sorted(map(len,groups.values()))==[6,13,13,13,13,13,13,25,25]
            rng=__import__('random').Random(42);queues={p:[] for p in groups};self.indices=[]
            for _ in range(500):
                for part,indices in groups.items():
                    if not queues[part]:queues[part]=rng.sample(indices,len(indices))
                    self.indices.append(queues[part].pop())
            save('audits/equal_part_sampler.json',{'indices':self.indices,'groups':groups,'microbatches_per_part':500,'each_update':'one block per part; nine microbatches accumulated','seed':42,'optimizer_state':'fresh AdamW; checkpoint-2000 saved model only; no state borrowed from checkpoint-3000','remaining_update_budget':500})
        def __iter__(self):return iter(self.indices)
        def __len__(self):return len(self.indices)
    def equal_sampler(self,*args,**kwargs):return EqualPartSampler(self.train_dataset,self.data_collator)
    Trainer._get_train_sampler=equal_sampler
'''
assert anchor in source;source=source.replace(anchor,insertion+anchor)
source=source.replace("        value=float(loss.detach());losses.append(value)","        assert max(counts.get(f'PART_{j:03d}',0) for j in range(9))-min(counts.get(f'PART_{j:03d}',0) for j in range(9))<=1\n        value=float(loss.detach());losses.append(value)")
source=source.replace("            save('control/checkpoint-'+str(state.global_step)+'.ready',snap)", "            save('control/checkpoint-'+str(state.global_step)+'.ready',snap)\n            assert len(counts)==9 and len(set(counts.values()))==1\n            while state.global_step>=int((EXP/'control/train_until').read_text()) and not (EXP/'control/stop_after_stable').exists():\n                if time.time()-started>=14400:control.should_training_stop=True;break\n                time.sleep(2)\n            if (EXP/'control/stop_after_stable').exists():control.should_training_stop=True")
source=source.replace("        return model\n    loader.load_model", "        def dtype_hook(name):\n            def hook(module,inputs):\n                path=EXP/('audits/training_'+name+'_dtype.json')\n                if not path.exists():save(str(path.relative_to(EXP)),{'input_dtype':str(inputs[0].dtype),'weight_dtype':str(next(module.parameters()).dtype),'autocast_enabled':torch.is_autocast_enabled()})\n            return hook\n        model.point_proj.register_forward_pre_hook(dtype_hook('surface_projector'))\n        model.edge_proj.register_forward_pre_hook(dtype_hook('curve_projector'))\n        return model\n    loader.load_model")
(E/'launch/fast_train_resolved.py').write_text(source)
exec(compile(source,str(E/'launch/fast_train_resolved.py'),'exec'),{'__name__':'__main__','__file__':str(E/'launch/fast_train_resolved.py')})