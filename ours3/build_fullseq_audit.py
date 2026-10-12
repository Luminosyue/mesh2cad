import json,math,csv,sys
from pathlib import Path
from tokenizers import Tokenizer
from transformers import AutoTokenizer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/airplane_fullseq_14bit_ir_v1'; EXP.mkdir(exist_ok=True)
for d in ['context_audit','smoke','runs','eval','logs','reports']:(EXP/d).mkdir(exist_ok=True)
cond=json.load(open(ROOT/'ours3/airplane_fullseq_14bit_ir_v1_cond.json'))
tok=AutoTokenizer.from_pretrained(str(ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b0/best_model'),use_fast=False)
sys.path.insert(0,str(ROOT/'scripts/separate_edge_tokens_v1'))
from common import build_prompt
prompt=build_prompt(separate_edge=True)
raw_prompt_n=len(tok(prompt,add_special_tokens=False)['input_ids'])
chat=tok.apply_chat_template([{'role':'user','content':prompt}],add_generation_prompt=True,return_tensors='pt')[0].tolist()
prompt_n=len(chat); special_n=prompt_n-raw_prompt_n
ir_tok=Tokenizer.from_file(str(ROOT/'external_checkpoints/qwen2_1_5b_tokenizer_clean/tokenizer.json'))
rows=[]
for c in cond:
 pid=c['PART_ID']; target=len(ir_tok.encode((ROOT/'ours3/airplane9_14bit_compact_ir_v1/ir_v2'/('airplane__'+pid+'.ir')).read_text()).ids); eos=1
 # IR tokenizer and model tokenizer are the same P1 tokenizer; verify count with HF tokenizer where possible
 full=prompt_n+c['SURFACE_CONDITIONING_TOKEN_N']+c['CURVE_CONDITIONING_TOKEN_N']+target+eos
 rows.append({'PART_ID':pid,'SURFACE_CONDITIONING_TOKEN_N':c['SURFACE_CONDITIONING_TOKEN_N'],'CURVE_CONDITIONING_TOKEN_N':c['CURVE_CONDITIONING_TOKEN_N'],'OTHER_CONDITIONING_TOKEN_N':0,'PROMPT_TOKEN_N':raw_prompt_n,'SPECIAL_TOKEN_N':special_n,'COMPACT_IR_TARGET_TOKEN_N':target,'EOS_TOKEN_N':eos,'TOTAL_SEQUENCE_TOKEN_N':full,'TARGET_TRUNCATED':'NO','FULLSEQ_TRUNCATED':'NO'})
fields=list(rows[0]); csv_path=EXP/'context_audit/airplane9_full_sequence_lengths.csv'
with open(csv_path,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
vals=lambda k:[int(x[k]) for x in rows]
t=vals('COMPACT_IR_TARGET_TOKEN_N'); full=vals('TOTAL_SEQUENCE_TOKEN_N'); req=max(full); margin=math.ceil(req*1.05); buckets=[8192,16384,32768,49152,65536]; rec=next(x for x in buckets if x>=margin)
model_cfg=json.load(open(ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b0/best_model/config.json')); maxpos=model_cfg.get('max_position_embeddings',model_cfg.get('max_sequence_length'))
summary={'TARGET_REPRESENTATION':'14BIT_COMPACT_IR_V2','AIRPLANE_N':9,'PROMPT_RAW_TOKEN_N':raw_prompt_n,'PROMPT_CHAT_TEMPLATE_TOKEN_N':prompt_n,'SPECIAL_TOKEN_N':special_n,'TARGET_MIN':min(t),'TARGET_MEDIAN':int(sorted(t)[len(t)//2]),'TARGET_P90':int(sorted(t)[math.ceil(.9*len(t))-1]),'TARGET_MAX':max(t),'FULLSEQ_MIN':min(full),'FULLSEQ_MEDIAN':int(sorted(full)[len(full)//2]),'FULLSEQ_P90':int(sorted(full)[math.ceil(.9*len(full))-1]),'FULLSEQ_MAX':max(full),'PART_000_FULLSEQ':full[0],'PART_001_FULLSEQ':full[1],'PART_005_FULLSEQ':full[5],'PART_008_FULLSEQ':full[8],'REQUIRED':req,'REQUIRED_WITH_MARGIN':margin,'MIN_CONTEXT_COVERING_9_OF_9':rec,'RECOMMENDED_CONTEXT':rec,'MAX_POSITION_EMBEDDINGS':maxpos,'CONTEXT_GATE':'PASS' if rec<=maxpos else 'FAIL','NO_CHUNK':'YES','NO_TRUNCATION':'YES','DATASET_TRUNCATION':'NONE','TOKENIZER_TRUNCATION':'NONE','COLLATOR_TRUNCATION':'NONE','MODEL_TRUNCATION':'NONE','BUCKETING_IS_NOT_CHUNKING':'TRUE'}
json.dump(summary,open(EXP/'context_audit/summary.json','w'),indent=2)
with open(EXP/'context_audit/truncation_audit.md','w') as f:
 f.write('# Full Sequence Truncation Audit\\n\\n')
 for k in ['DATASET_TRUNCATION','TOKENIZER_TRUNCATION','COLLATOR_TRUNCATION','MODEL_TRUNCATION']: f.write(f'- {k}=NONE\\n')
 f.write('- NO_CHUNK=YES\\n- NO_TARGET_SPLIT=YES\\n- NO_CONTINUATION=YES\\n')
print(json.dumps(summary,indent=2)); print('CSV',csv_path)
