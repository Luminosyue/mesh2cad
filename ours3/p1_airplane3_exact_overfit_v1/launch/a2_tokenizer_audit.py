from pathlib import Path
import json,hashlib
from transformers import AutoTokenizer
R=Path('/data/home/cuiyuehan/project/mesh2cad');E=R/'ours3/p1_airplane3_exact_overfit_v1';initial=R/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'
paths=[initial]+sorted((E/'runs/quick').glob('checkpoint-*'),key=lambda p:int(p.name.split('-')[-1]));rows=[]
for p in paths:
 t=AutoTokenizer.from_pretrained(str(p),use_fast=False,trust_remote_code=False,local_files_only=True)
 h=hashlib.sha256(json.dumps(sorted(t.get_vocab().items()),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 gen=json.loads((p/'generation_config.json').read_text());eos=gen['eos_token_id'];eos=eos if isinstance(eos,list) else [eos]
 row={'checkpoint':str(p),'vocabulary_sha256':h,'vocab_n':len(t.get_vocab()),'eos_token_id':t.eos_token_id,'pad_token_id':t.pad_token_id,'generation_eos_token_ids':eos};rows.append(row)
 assert t.eos_token_id in eos
 assert (h,t.eos_token_id,t.pad_token_id)==(rows[0]['vocabulary_sha256'],rows[0]['eos_token_id'],rows[0]['pad_token_id'])
(E/'audits/checkpoint_tokenizer_verification.json').write_text(json.dumps({'PASS':True,'rows':rows},indent=2));print('TOKENIZER_FREEZE_PASS',len(rows),'checkpoints including initialization')
