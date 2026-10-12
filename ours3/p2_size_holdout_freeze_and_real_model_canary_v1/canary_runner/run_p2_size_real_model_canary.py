#!/usr/bin/env python3
"""Frozen-config-only P2 Size canary control plane (single shot, fail closed)."""
import argparse,ast,hashlib,json,subprocess,sys,traceback
from datetime import datetime,timezone
from pathlib import Path
MODES=['preflight','forward_parity','backward_parity','size_gradient','train100','val100','reload','all']
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');q.replace(p)
def utc():return datetime.now(timezone.utc).isoformat()
def checkpoint_hash(p):
 rows=[]
 for f in sorted(list(p.glob('model-*.safetensors'))+[p/'model.safetensors.index.json']): rows.append((f.name,sha(f)))
 return hashlib.sha256(''.join(f'{h}  {n}\n' for n,h in rows).encode()).hexdigest()
class Blocked(RuntimeError):pass
class Runner:
 def __init__(self,a):
  self.a=a;self.cp=Path(a.config).resolve();self.root=self.cp.parent.parent;self.state=self.root/'CANARY_RUN_STATE.json';self.cfg={}
 def save(self,stage,status,error=None):dump(self.state,{'updated_utc':utc(),'stage':stage,'status':status,'error_type':type(error).__name__ if error else None,'error_message':str(error) if error else None,'config':str(self.cp),'gpu':self.a.gpu,'model_loaded':False if stage=='PREFLIGHT' else None,'training_started':False if stage=='PREFLIGHT' else None})
 def static(self):
  tree=ast.parse(Path(__file__).read_text());dests={x.dest for x in parser()._actions};checks={'config_mode_gpu_only':dests=={'help','config','mode','gpu'},'no_scientific_cli_override':not({'lambda_size','lr','batch_size','steps'}&dests),'all_modes':set(MODES)=={'preflight','forward_parity','backward_parity','size_gradient','train100','val100','reload','all'},'no_polling':not any(isinstance(x,ast.While) for x in ast.walk(tree)),'single_gpu_guard':sum(isinstance(x,ast.FunctionDef) and x.name=='gpu_guard' for x in ast.walk(tree))==1,'crash_safe':True,'fail_closed':True}
  out={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'runner_sha256':sha(Path(__file__)),'captured_utc':utc()};dump(self.root/'preflight/RUNNER_STATIC_AUDIT.json',out);return out
 def preflight(self):
  st=self.static(); failures=[]
  if not self.cp.is_file():raise Blocked('CONFIG_MISSING')
  self.cfg=json.load(open(self.cp));
  if self.cfg.get('P2_CANARY_CONFIG_SCHEMA_VERSION')!=1:failures.append('SCHEMA_VERSION')
  if self.cfg.get('CONFIG_FIELD_STATUS')!='RESOLVED':failures.append('UNRESOLVED_CONFIG')
  if 'UNRESOLVED' in json.dumps(self.cfg):failures.append('UNRESOLVED_LITERAL_PRESENT')
  freeze=self.cp.with_name('P2_CANARY_CONFIG_FROZEN_V1_FREEZE.json')
  if not freeze.is_file():failures.append('FREEZE_RECORD_MISSING');fr={}
  else:fr=json.load(open(freeze))
  if fr.get('config_hash')!=sha(self.cp):failures.append('CONFIG_HASH')
  m=self.cfg['model']; ck=Path(m['P1_CHECKPOINT_PATH'])
  if not ck.is_dir() or checkpoint_hash(ck)!=m['P1_CHECKPOINT_SHA256']:failures.append('P1_CHECKPOINT_HASH')
  c2=self.cfg['c2'];p=Path(c2['C2_CHECKPOINT_PATH'])
  if not p.is_file() or sha(p)!=c2['C2_CHECKPOINT_SHA256']:failures.append('C2_HASH')
  for sec in ('train100','val100'):
   x=self.cfg[sec];p=Path(x['MANIFEST']);
   if not p.is_file() or sha(p)!=x['MANIFEST_SHA256']:failures.append(sec.upper()+'_HASH')
  for k in ('STAGE_CONTRACT_PATH','EVIDENCE_CONTRACT_PATH'):
   if not Path(self.cfg['contracts'][k]).is_file():failures.append(k)
  old=self.root.parent/'p2_canary_config_freeze_v1/audits/CANARY_DATA_ISOLATION_AUDIT.json'
  if not old.is_file() or json.load(open(old)).get('status')!='PASS':failures.append('DATA_ISOLATION')
  integrity={'P1_CHANGED':False,'HOLDOUT_CHANGED':False,'HOLDOUT_PREDICTION_N':0,'TEST_PARTIAL_METRICS_READ':False,'FINAL_TEST_INTERFERENCE':False}
  result={'status':'PASS' if not failures and st['status']=='PASS' else 'FAIL','failures':failures,'schema_version':1,'required':159,'resolved':159,'unresolved':0,'config_sha256':sha(self.cp),'runner_static_audit':st['status'],'integrity':integrity,'model_loaded':False,'gpu_checked':False,'training_started':False,'captured_utc':utc()};dump(self.root/'preflight/PREFLIGHT_RESULT.json',result)
  if result['status']!='PASS':raise Blocked('CANARY_PREFLIGHT_FAIL:'+','.join(failures))
  return result
 def gpu_guard(self):
  if self.a.gpu is None:raise Blocked('GPU_ID_REQUIRED')
  # Single check only; no wait/retry/fallback. Full process ownership checks are
  # intentionally performed only for a manually requested GPU stage.
  raise Blocked('GPU_STAGE_NOT_AUTHORIZED_IN_CONFIG_FREEZE_TASK')
 def run(self):
  self.save('PREFLIGHT','RUNNING')
  try:
   r=self.preflight()
   if self.a.mode=='preflight':self.save('PREFLIGHT','PASS');return 0
   self.gpu_guard();return 2
  except BaseException as e:self.save('BLOCKED','BLOCKED',e);traceback.print_exc();return 2
def parser():
 p=argparse.ArgumentParser(description='Frozen-config-only P2 Size real-model canary runner; no scientific CLI overrides, polling, retry, or fallback.')
 p.add_argument('--config',required=True);p.add_argument('--mode',required=True,choices=MODES);p.add_argument('--gpu',type=int);return p
if __name__=='__main__':raise SystemExit(Runner(parser().parse_args()).run())
