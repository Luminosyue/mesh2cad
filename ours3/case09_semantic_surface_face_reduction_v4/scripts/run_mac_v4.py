#!/usr/bin/env python3
import os,sys,json,re,ast,time,subprocess,importlib.util,shutil
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'case09_semantic_surface_face_reduction_v4';MAC_ROOT=ROOT/'external/Multi-Agent-CAD';PY='/data/miniconda3/envs/multi_agent_cad/bin/python';PARTS=['CADPART_001','CADPART_002']
def dump(p,x): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def load_key():
 for line in Path('/data/home/cuiyuehan/project/pair_agent/.env').read_text(encoding='utf-8-sig').splitlines():
  if line.strip().startswith('DASHSCOPE_API_KEY='): os.environ['DASHSCOPE_API_KEY']=line.split('=',1)[1].strip().strip('"').strip("'")
 os.environ['OPENAI_BASE_URL']='https://dashscope.aliyuncs.com/compatible-mode/v1'
def call(c,model,role,system,user,calls,responses):
 for attempt in range(1,4):
  try:
   t=time.time();r=c.chat.completions.create(model=model,temperature=0,max_tokens=2200,extra_body={'enable_thinking':False},messages=[{'role':'system','content':system},{'role':'user','content':user}]);u=r.usage;rec={'role':role,'request_sent':True,'response_received':True,'attempt':attempt,'model':model,'latency_seconds':time.time()-t,'prompt_tokens':u.prompt_tokens,'completion_tokens':u.completion_tokens};calls.append(rec);responses.append({'role':role,'content':r.choices[0].message.content});return r.choices[0].message.content
  except Exception as e: calls.append({'role':role,'request_sent':True,'response_received':False,'attempt':attempt,'error':f'{type(e).__name__}: {e}'})
 raise RuntimeError(role+' failed')
def parse_json(s):
 m=re.search(r'\{.*\}',s,re.S)
 try:return json.loads(m.group())
 except:return {'raw':s}
def code(s):
 m=re.search(r'```(?:python)?\s*(.*?)```',s,re.S|re.I);return (m.group(1) if m else s).strip()+'\n'
def contract(s):
 e=[]
 try:ast.parse(s)
 except Exception as x:e.append('SYNTAX:'+str(x))
 for x in ('load_semantic_spec','build_semantic_wing_skin','validate_shape','export_step','write_provenance'):
  if x not in s:e.append('MISSING_'+x)
 if '.obj' in s.lower() or 'v3' in s.lower() and 'measured_v3_spec' not in s:e.append('ISOLATION_VIOLATION')
 return e
def run_part(part,c,cfg):
 d=OUT/'04_mac'/part;spec=d/'measured_cad_spec.json';data=json.loads(spec.read_text());calls=[];responses=[]
 shared=json.dumps({'part_id':part,'semantic_surface_graph':json.loads((d/'semantic_surface_graph.json').read_text()),'cad_feature_graph':json.loads((d/'cad_feature_graph.json').read_text()),'probe_qa':data['probe_qa'],'constraints':data['constraints']},indent=2)
 brief=call(c,cfg.SPEC_PLANNER_MODEL,'planner','Multi-Agent-CAD Spec Planner. JSON only. Use supplied measurements only.', 'Plan one semantic wing reconstruction. Intermediate sections are fitting constraints only, never topology. Preserve leading/trailing/root/tip.\n'+shared,calls,responses);dump(d/'cad_brief.json',parse_json(brief))
 arch=call(c,cfg.ARCHITECT_MODEL,'architect','Multi-Agent-CAD Geometry Architect. JSON only. Specify one global upper and one global lower B-spline surface, root and tip caps. Never edge-wise loft.', 'Create executable architecture from:\n'+brief+'\n'+shared,calls,responses);dump(d/'architect_plan.json',parse_json(arch))
 system='Multi-Agent-CAD Python Coder. Return one executable Python code block only. Do not read OBJ or old STEP. Do not build section wires or use edge-wise loft.'
 prompt=f'''Generate the program for {part}. Mandatory contract:\nfrom case09_v4_runtime import load_semantic_spec, build_semantic_wing_skin, validate_shape, export_step, write_provenance\nCLI: --spec --output. Load spec; call build_semantic_wing_skin(spec, representation=spec["representation"]); require validate_shape(shape)["valid"]; export_step; write_provenance with MAC_GENERATED=True, part_id and trace. Intermediate measured sections MUST NOT enter final BRep topology. Architect:\n{arch}'''
 raw=call(c,cfg.CODER_MODEL,'coder',system,prompt,calls,responses);src=code(raw);program=d/'generated_code.py';program.write_text(src);rounds=0;logs=[];step=d/'selected.step'
 while True:
  errs=contract(src);env=dict(os.environ);env['PYTHONPATH']=str(OUT/'scripts')+os.pathsep+env.get('PYTHONPATH','');p=None if errs else subprocess.run([PY,str(program),'--spec',str(spec),'--output',str(step)],capture_output=True,text=True,timeout=120,env=env);logs.append({'round':rounds,'contract_errors':errs,'exit_code':None if p is None else p.returncode,'stdout':'' if p is None else p.stdout,'stderr':'' if p is None else p.stderr})
  if p is not None and p.returncode==0 and step.is_file():break
  if rounds>=2:break
  rounds+=1;fb={'errors':errs or [p.stderr[-2000:]],'required_contract':prompt};dump(d/f'repair_feedback_round_{rounds}.json',fb);raw=call(c,cfg.CODER_MODEL,f'coder_repair_{rounds}',system,'Repair program. Return code only.\n'+src+'\n'+json.dumps(fb),calls,responses);src=code(raw);program.write_text(src)
 dump(d/'execution_log.json',logs);dump(d/'mac_prompt.txt',{'planner':shared,'coder':prompt});dump(d/'mac_response.json',responses);dump(d/'token_usage.json',{'LLM_CALLS':sum(x.get('response_received',False) for x in calls),'calls':calls})
 ok=step.is_file() and not contract(src);row={'part_id':part,'MAC_USED':True,'MAC_RUNS':1,'LLM_CALLS':sum(x.get('response_received',False) for x in calls),'MAX_MAC_REPAIR_ROUNDS':2,'repair_rounds':rounds,'MAC_RESULT':'SUCCESS' if ok else 'FAIL','step':str(step)};dump(d/'mac_run_summary.json',row);return row
def main():
 load_key();sys.path.insert(0,str(MAC_ROOT));from multi_agent_cad import config;import multi_agent_cad.nodes as nodes;nodes._DS_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1';c=nodes._llm_client();rows=[]
 for p in PARTS:r=run_part(p,c,config);rows.append(r);print('MAC_V4_PART',p,r['MAC_RESULT'],r['LLM_CALLS'],flush=True)
 dump(OUT/'metrics/mac_v4_aggregate.json',{'MAC_USED':True,'MAC_TARGET_PARTS':PARTS,'MAC_RUNS':2,'LLM_CALLS':sum(x['LLM_CALLS'] for x in rows),'parts':rows})
if __name__=='__main__':main()
