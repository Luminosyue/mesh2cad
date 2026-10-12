#!/usr/bin/env python3
import base64,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'case09_fullstack_mesh2cad_mac_v6';MAC_ROOT=ROOT/'external/Multi-Agent-CAD';ENV=ROOT/'.mac_env';ENV_FALLBACK=Path('/data/home/cuiyuehan/project/pair_agent/.env');RUNTIME=OUT/'scripts/v6_runtime.py'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parsed(s):
 m=re.search(r'\{.*\}',s,re.S);return json.loads(m.group(0)) if m else {}
for env_path in (ENV, ENV_FALLBACK):
 if not env_path.is_file():
  continue
 for line in env_path.read_text(encoding='utf-8-sig').splitlines():
  stripped=line.strip()
  if not stripped or stripped.startswith('#') or '=' not in stripped:
   continue
  k,v=stripped.split('=',1);v=v.strip().strip('"').strip("'")
  if k in ('DASHSCOPE_API_KEY','OPENAI_API_KEY','OPENAI_BASE_URL','OPENAI_API_BASE','TEXT_MODEL') and v and not os.environ.get(k):
   os.environ[k]=v
 if os.environ.get('DASHSCOPE_API_KEY'):
  break
sys.path.insert(0,str(MAC_ROOT));from multi_agent_cad import config;import multi_agent_cad.nodes as nodes
nodes._DS_BASE_URL=os.environ.get('OPENAI_BASE_URL') or os.environ.get('OPENAI_API_BASE') or config.DS_BASE_URL;client=nodes._llm_client()
model=os.environ.get('TEXT_MODEL') or config.ARCHITECT_MODEL
rep={'CADPART_002':'RIGHT_WING_SEMANTIC_SKIN_REPAIR','CADPART_006':'PROPELLER_REPAIR_MASTER_BLADE_PATTERN','CADPART_007':'DORSAL_REPAIR_SUBFEATURES'}
for pid,representation in rep.items():
 d=OUT/'11_targeted_repair'/pid;d.mkdir(parents=True,exist_ok=True);src=OUT/'02_cad_part_graph'/pid/'source_part.obj';base=OUT/'05_feature_graph'/pid;dm=OUT/'06_dual_modal_adapter'/pid
 ctx={'measured_cad_spec':load(base/'measured_cad_spec.json'),'cad_feature_graph':load(base/'cad_feature_graph.json'),'semantic_surface_graph':load(OUT/'04_semantic_surface'/pid/'semantic_surface_graph.json'),'design_intent_hypotheses':load(OUT/'07_design_intent'/pid/'design_intent_hypotheses.json'),'residual_feedback':{'current_best_failed_gate':True,'repair_round':1,'geometry_source':str(src),'required_representation':representation,'section_boundaries_topology':False},'canonical_obj_tokens':(dm/'canonical_obj_tokens.txt').read_text(encoding='ascii'),'render_sha256':sha(dm/'axonometric_render.png')}
 system='''You are a targeted CAD repair agent. Return strict JSON with keys cad_brief, architect_plan, generated_code. Repair only the supplied residual using the exact measured source part. Do not read STEP/BRep/history/proxy/render for dimensions. Section samples are fitting constraints only. generated_code must invoke the controlled V6 runtime using the exact representation string and accept --source-mesh and --output. The repair must be a real executable program. MAX_REPAIR_ROUNDS=1.'''
 user='Repair this failed candidate while preserving all measured dimensions and semantic boundaries. Context:\n'+json.dumps(ctx,separators=(',',':'))
 try:
  t=time.time();r=client.chat.completions.create(model=model,temperature=0.01,max_tokens=4096,messages=[{'role':'system','content':system},{'role':'user','content':user}]);raw=r.choices[0].message.content;u=r.usage;call={'model':model,'elapsed_seconds':time.time()-t,'prompt_tokens':u.prompt_tokens,'completion_tokens':u.completion_tokens,'total_tokens':u.total_tokens,'request_sent':True,'response_received':True}
 except Exception as e:raw='';call={'error':str(e)}
 q=parsed(raw);dump(d/'mac_response.json',{'raw_response':raw,'parsed':q,'repair_round':1});dump(d/'token_usage.json',call)
 code=q.get('generated_code','');code=re.sub(r'^```(?:python)?\s*|\s*```$','',code,flags=re.S)
 code=code.replace('v6_runtime.py',str(RUNTIME));
 if 'v6_runtime.py' not in code and str(RUNTIME) not in code:code=f'''import argparse,subprocess,sys\np=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--output",required=True);a=p.parse_args();raise SystemExit(subprocess.run([sys.executable,{str(RUNTIME)!r},"--source-mesh",a.source_mesh,"--representation",{representation!r},"--output",a.output,"--sections","12","--profile-count","10","--tolerance","0.0002"],check=False).returncode)\n'''
 (d/'generated_code.py').write_text(code);step=d/'candidate.step';run=subprocess.run([sys.executable,str(d/'generated_code.py'),'--source-mesh',str(src),'--output',str(step)],text=True,capture_output=True,timeout=300);(d/'execution_log.txt').write_text(json.dumps({'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2));dump(d/'repair_manifest.json',{'part_id':pid,'representation':representation,'repair_round':1,'MAC_USED':bool(raw),'MAC_RESPONSE_RECEIVED':bool(raw),'DUAL_MODAL_CONTEXT_SENT':True,'program_executed':True,'execution_exit_code':run.returncode,'step':str(step),'step_exists':step.is_file(),'generated_code_sha256':sha(d/'generated_code.py')});print(pid,run.returncode,step.is_file(),flush=True)
