from pathlib import Path
import json,hashlib,torch
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
inv=json.loads((E/'data/block_inventory.json').read_text());batches=torch.load(E/'data/collated_batches.pt',map_location='cpu',weights_only=False)
counts={};tokens={};gt_tokens={}
features={}
for b,r in zip(batches,inv):
 labels=b['labels'][0];ids=labels[labels!=-100].tolist();assert len(ids)==r['token_count'];assert ids[-1]==128009
 counts[r['part']]=counts.get(r['part'],0)+1;tokens[r['part']]=tokens.get(r['part'],0)+len(ids)
 gt_tokens.setdefault(r['part'],[]).extend(ids)
 if r['block']==1:
  features[r['part']]={k:{'shape':list(v.shape),'dtype':str(v.dtype),'sha256':hashlib.sha256(v.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()} for k,v in b.items() if torch.is_tensor(v) and k not in ['input_ids','labels','attention_mask']}
frozen=json.loads((E/'audits/frozen_inputs.json').read_text());changed=[]
for r in frozen['pipeline_and_gt']:
 if hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()!=r['sha256']:changed.append(r['path'])
assert not changed
(E/'audits/conditioning_tensor_fingerprints.json').write_text(json.dumps(features,indent=2))
(E/'audits/gt_supervised_tokens_for_status.json').write_text(json.dumps(gt_tokens))
print(json.dumps({'block_counts':counts,'supervised_tokens':tokens,'frozen_files_pass':True},indent=2))
print('CONDITIONING',json.dumps(features))
