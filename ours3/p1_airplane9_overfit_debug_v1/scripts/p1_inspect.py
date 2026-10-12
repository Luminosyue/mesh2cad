from p1_debug_runtime import *
tok=AutoTokenizer.from_pretrained(str(CKPT));raw=json.loads((OLD/'data/train.json').read_text());gt=[r['conversations'][1]['value'] for r in raw if r['sample_id']=='airplane__PART_000'];pred=json.loads((OLD/'decode/checkpoint-2000/xpart__airplane__PART_000/generated_blocks.json').read_text())
for i in range(min(6,len(pred))):
 g=tok.encode(gt[i],add_special_tokens=False);p=tok.encode(pred[i],add_special_tokens=False);idx=next((j for j,(a,b) in enumerate(zip(g,p)) if a!=b),min(len(g),len(p)))
 print('BLOCK',i+1,'GT_LEN',len(g),'PRED_LEN',len(p),'FIRST_DIV',idx,'GT',repr(tok.decode(g[max(0,idx-12):idx+15])),'PRED',repr(tok.decode(p[max(0,idx-12):idx+15])))
t=json.loads((DEBUG/'teacher_forced_case0.json').read_text());print('TF',{k:v for k,v in t.items() if k not in ['all_gt_tokens','blocks']})
print('PROBE',json.loads((DEBUG/'cache_ablation_probe.json').read_text())['traces'])
