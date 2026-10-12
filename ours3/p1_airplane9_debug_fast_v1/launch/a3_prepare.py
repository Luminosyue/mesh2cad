from pathlib import Path
import sys,json,statistics
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
import a2_runtime as rt
rt.prepare()
batches=rt.torch.load(E/'data/collated_batches.pt',weights_only=False);raw=json.loads((E/'data/train.json').read_text());inv=json.loads((E/'data/block_inventory.json').read_text());tok=rt.AutoTokenizer.from_pretrained(str(E.parent/'p1_quick_overfit_airplane9_v1/runs/quick/checkpoint-2000'))
checks=[]
for b,r,v in zip(batches,raw,inv):
 ids=b['labels'][0];active=ids[ids!=-100].tolist();expected=tok.encode(r['conversations'][1]['value'],add_special_tokens=False)+[tok.eos_token_id]
 assert active==expected,(r['id'],'target truncation or serializer mismatch')
 assert b['input_ids'].shape[1]<4096
 assert b['point_clouds'].dtype==rt.torch.bfloat16 and b['edge_clouds'].dtype==rt.torch.bfloat16
 checks.append({'id':r['id'],'all_target_tokens_in_loss':True,'sequence_length':b['input_ids'].shape[1],'supervised_tokens':len(active),'surface_input_dtype':str(b['point_clouds'].dtype),'curve_input_dtype':str(b['edge_clouds'].dtype)})
rows=json.loads((E/'airplane9_dataset_audit.json').read_text())
for row in rows:row['TOKEN_COUNT']=sum(v['token_count'] for v in inv if v['part']==row['PART_ID'])
nums=[r['TOKEN_COUNT'] for r in rows];rt.save(E/'airplane9_dataset_audit.json',{'parts':rows,'TOTAL_PART_N':9,'TOTAL_BLOCK_N':134,'TOTAL_TOKEN_N':sum(nums),'MIN_TOKEN_N':min(nums),'MAX_TOKEN_N':max(nums),'MEDIAN_TOKEN_N':statistics.median(nums),'token_definition':'supervised block targets including every natural EOS'})
rt.save(E/'audits/data_gate.json',{'PASS':True,'blocks':checks,'eos_id':tok.eos_token_id,'pad_id':tok.pad_token_id});(E/'control/train_until').write_text('10');print('DATA_GATE_PASS',sum(nums),flush=True)
