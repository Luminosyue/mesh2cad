#!/usr/bin/env python3
"""Create per-CAD length/EOS/parse diagnostics for an existing decode JSONL."""
from __future__ import annotations
import argparse,ast,json,pathlib
from collections import Counter
from transformers import AutoTokenizer

def parse_ok(text):
 s=text.strip();lines=s.splitlines()
 if s.startswith('```'):
  lines=lines[1:]
  if lines and lines[-1].strip().startswith('```'):lines=lines[:-1]
  s='\n'.join(lines)
 try:ast.parse(s);return True
 except (SyntaxError,ValueError):return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--decode-dir',required=True);ap.add_argument('--tokenizer',required=True);a=ap.parse_args();d=pathlib.Path(a.decode_dir);tok=AutoTokenizer.from_pretrained(a.tokenizer,local_files_only=True,use_fast=False)
 rows=[]
 for line in (d/'predictions.jsonl').read_text().splitlines():
  r=json.loads(line);target=pathlib.Path(r['target_dsl']).read_text();ids=tok.encode(r['prediction'],add_special_tokens=False);hit=bool(r.get('hit_max_new_tokens',r.get('truncated',False)));target_len=int(r.get('target_token_length',len(tok.encode(target,add_special_tokens=False))));generated_len=int(r.get('generated_token_length',r.get('token_count')))
  rows.append({**{k:r[k] for k in ['cad_id','source_dataset','difficulty_bin','k_valid']},'target_token_length':target_len,'generated_token_length':generated_len,'generated_to_target_ratio':generated_len/max(target_len,1),'hit_max_new_tokens':hit,'eos_emitted':bool(r.get('eos_emitted',not hit)),'eos_inference':'direct when present; otherwise non-hit implies EOS because only EOS/max stopping criteria were configured','dsl_parse_success':bool(r.get('dsl_parse_success',parse_ok(r['prediction']))),'last_100_token_ids_retokenized':r.get('last_100_token_ids',ids[-100:]),'last_100_tokens':r.get('last_100_tokens',tok.decode(ids[-100:],skip_special_tokens=False))})
 out=d/'length_diagnostics.jsonl';out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 kbins={'low_le8':lambda k:k<=8,'mid_9_63':lambda k:8<k<64,'high_ge64':lambda k:k>=64}
 summary={'count':len(rows),'hit_max_new_tokens':sum(r['hit_max_new_tokens'] for r in rows),'eos_emitted':sum(r['eos_emitted'] for r in rows),'dsl_parse_success':sum(r['dsl_parse_success'] for r in rows),'target_le_2048_and_hit_2048':sum(r['target_token_length']<=2048 and r['hit_max_new_tokens'] for r in rows),'target_gt_2048_and_hit_2048':sum(r['target_token_length']>2048 and r['hit_max_new_tokens'] for r in rows),'target_le_4096_and_hit_4096':sum(r['target_token_length']<=4096 and r['generated_token_length']>=4096 for r in rows),'target_gt_4096_and_hit_4096':sum(r['target_token_length']>4096 and r['generated_token_length']>=4096 for r in rows),'target_token_length':{'min':min(r['target_token_length'] for r in rows),'max':max(r['target_token_length'] for r in rows)},'generated_token_length':{'min':min(r['generated_token_length'] for r in rows),'max':max(r['generated_token_length'] for r in rows)},'generated_to_target_ratio_mean':sum(r['generated_to_target_ratio'] for r in rows)/len(rows),'k_valid_runaway':{name:{'count':sum(fn(r['k_valid']) for r in rows),'runaway_count':sum(fn(r['k_valid']) and r['hit_max_new_tokens'] for r in rows),'runaway_rate':sum(fn(r['k_valid']) and r['hit_max_new_tokens'] for r in rows)/max(1,sum(fn(r['k_valid']) for r in rows))} for name,fn in kbins.items()}}
 (d/'LENGTH_DIAGNOSTIC_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
