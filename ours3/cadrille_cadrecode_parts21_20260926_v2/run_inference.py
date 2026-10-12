import os,sys,json,time,subprocess,traceback,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
from transformers import AutoProcessor,AutoTokenizer

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'cadrille_full20_20260926'
method=sys.argv[1]
shard=int(sys.argv[2]) if len(sys.argv)>2 else 0
shards=int(sys.argv[3]) if len(sys.argv)>3 else 1
batch_size=int(os.environ.get('PARTS_BATCH_SIZE','12'))
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
tasks=[p for case in manifest['cases'] for p in case['parts']]
tasks=[p for i,p in enumerate(tasks) if i%shards==shard]
if os.environ.get('SMOKE')=='1':tasks=tasks[:4]
output=ROOT/method
output.mkdir(exist_ok=True)
torch.set_num_threads(4)
torch.manual_seed(20260926)
if method=='cadrille':
    sys.path.insert(0,str(OLD/'repo'))
    from cadrille import Cadrille,collate
    model=Cadrille.from_pretrained(str(OLD/'model'),torch_dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'}).eval()
    tokenizer=AutoProcessor.from_pretrained(str(OLD/'model'),min_pixels=256*28*28,max_pixels=1280*28*28,padding_side='left')
else:
    from cadrecode_model import CADRecode
    checkpoint=ROOT.parent.parent/'external_checkpoints/cad_recode_v1_5'
    tokenpath=ROOT.parent.parent/'external_checkpoints/qwen2_1_5b_tokenizer_clean'
    tokenizer=AutoTokenizer.from_pretrained(str(tokenpath),local_files_only=True,padding_side='left')
    model=CADRecode.from_pretrained(str(checkpoint),torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).eval().to('cuda')
    model.point_encoder.float()
    torch.set_default_dtype(torch.float32)

def current(meta):
    p=output/meta['case']/meta['part']/'STATUS.json'
    return json.loads(p.read_text()) if p.exists() else {}

def execute(meta,attempt,folder):
    status=output/meta['case']/meta['part']/'STATUS.json'
    try:
        proc=subprocess.run([sys.executable,str(ROOT/'export_part.py'),str(folder),str(Path(meta['input_stl']).parent/'transform.json')],capture_output=True,text=True,timeout=60)
        (folder/'execution.log').write_text(proc.stdout+proc.stderr)
        rec=json.loads((folder/'EXECUTION.json').read_text()) if (folder/'EXECUTION.json').exists() else dict(status='FAIL',error='Execution failed: '+proc.stderr[-2000:])
    except Exception:rec=dict(status='FAIL',error=traceback.format_exc())
    rec.update(case=meta['case'],part=meta['part'],attempt=attempt,method=method,source=meta['source'],folder=str(folder))
    status.write_text(json.dumps(rec,indent=2))
    return rec

started=time.time()
with ThreadPoolExecutor(max_workers=4) as pool:
    for attempt in range(3):
        pending=[x for x in tasks if current(x).get('status')!='PASS']
        print('ROUND',attempt,'PENDING',len(pending),flush=True)
        for offset in range(0,len(pending),batch_size):
            batch_tasks=pending[offset:offset+batch_size]
            pcs=np.stack([np.load(p['points'][attempt]) for p in batch_tasks])
            if method=='cadrille':
                batch=collate([dict(point_cloud=pc,description='Generate cadquery code',file_name=p['part']) for pc,p in zip(pcs,batch_tasks)],processor=tokenizer,n_points=256,eval=True)
                kwargs={k:batch[k].to('cuda') for k in ['input_ids','attention_mask','point_clouds','is_pc','is_img']}
            else:
                ids=[tokenizer.pad_token_id]*256+[tokenizer('<|im_start|>')['input_ids'][0]]
                kwargs=dict(input_ids=torch.tensor([ids]*len(pcs),device='cuda'),attention_mask=torch.tensor([[-1]*256+[1]]*len(pcs),device='cuda'),point_cloud=torch.tensor(pcs,device='cuda',dtype=torch.float32))
            with torch.inference_mode():
                generated=model.generate(**kwargs,max_new_tokens=1024 if attempt==0 else 1536,do_sample=False,pad_token_id=tokenizer.tokenizer.pad_token_id if method=='cadrille' else tokenizer.pad_token_id)
            strings=tokenizer.batch_decode(generated[:,kwargs['input_ids'].shape[1]:],skip_special_tokens=True,clean_up_tokenization_spaces=False)
            futures=[]
            for meta,text in zip(batch_tasks,strings):
                folder=output/meta['case']/meta['part']/f'attempt_{attempt}'
                folder.mkdir(parents=True,exist_ok=True)
                (folder/'raw.txt').write_text(text)
                code=text.replace('```python','').replace('```','').strip()
                (folder/'cadquery.py').write_text(code)
                futures.append(pool.submit(execute,meta,attempt,folder))
            records=[f.result() for f in futures]
            success=sum(r['status']=='PASS' for r in records)
            print(json.dumps(dict(method=method,shard=shard,attempt=attempt,batch=offset,passed=success,count=len(records),elapsed=round(time.time()-started))),flush=True)
            (output/f'progress_{shard}.json').write_text(json.dumps(dict(method=method,shard=shard,attempt=attempt,processed=offset+len(records),pending_round=len(pending),passed=sum(current(x).get('status')=='PASS' for x in tasks),required=len(tasks),updated=time.time()),indent=2))
            del generated,kwargs
            torch.cuda.empty_cache()
summary=dict(method=method,shard=shard,parts=len(tasks),passed=sum(current(x).get('status')=='PASS' for x in tasks),elapsed=time.time()-started)
(output/f'SHARD_{shard}.DONE').write_text(json.dumps(summary,indent=2))
print('DONE',json.dumps(summary),flush=True)
