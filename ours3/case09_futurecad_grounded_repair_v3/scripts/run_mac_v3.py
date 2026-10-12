#!/usr/bin/env python3
from __future__ import annotations
import ast,importlib.util,json,os,re,subprocess,sys,time
from pathlib import Path
import trimesh
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';V2=ROOT/'case09_all_parts_mac_futurecad_v2';OUT=ROOT/'case09_futurecad_grounded_repair_v3';MAC_ROOT=ROOT/'external/Multi-Agent-CAD';PY=Path('/data/miniconda3/envs/multi_agent_cad/bin/python')
TARGETS=['CADPART_001','CADPART_002','CADPART_006']
def mod(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=mod('v',V1/'scripts/end2end_pipeline.py')
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(V.clean(x),indent=2)+'\n')
def load_key():
 for line in Path('/data/home/cuiyuehan/project/pair_agent/.env').read_text(encoding='utf-8-sig').splitlines():
  if line.strip().startswith('DASHSCOPE_API_KEY='):os.environ['DASHSCOPE_API_KEY']=line.split('=',1)[1].strip().strip('"').strip("'")
 os.environ.setdefault('OPENAI_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1')
def client():
 sys.path.insert(0,str(MAC_ROOT));from multi_agent_cad import config;import multi_agent_cad.nodes as nodes;nodes._DS_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1';return nodes._llm_client(),config
def call(c,model,role,system,user,max_tokens,calls,responses):
 for attempt in range(1,4):
  t=time.time()
  try:
   r=c.chat.completions.create(model=model,temperature=0,max_tokens=max_tokens,extra_body={'enable_thinking':False},messages=[{'role':'system','content':system},{'role':'user','content':user}]);content=r.choices[0].message.content;u=r.usage;rec={'role':role,'request_sent':True,'response_received':True,'transport_attempt':attempt,'model':model,'latency_seconds':time.time()-t,'prompt_tokens':u.prompt_tokens,'completion_tokens':u.completion_tokens,'total_tokens':u.total_tokens};calls.append(rec);responses.append({'role':role,'content':content,'usage':rec});return content
  except Exception as e:
   calls.append({'role':role,'request_sent':True,'response_received':False,'transport_attempt':attempt,'error':f'{type(e).__name__}: {e}'})
 raise RuntimeError(f'{role} provider failed')
def extract_json(text):
 m=re.search(r'\{.*\}',text,re.S)
 if not m:return {'parse_error':'NO_JSON','raw':text}
 try:return json.loads(m.group())
 except Exception as e:return {'parse_error':f'{type(e).__name__}: {e}','raw':text}
def extract_code(text):
 m=re.search(r'```(?:python)?\s*(.*?)```',text,re.S|re.I);code=m.group(1) if m else text;starts=[x for x in [code.find('import '),code.find('from ')] if x>=0];return code[min(starts):].strip()+'\n' if starts else code.strip()+'\n'
def contract(code):
 errors=[]
 try:ast.parse(code)
 except Exception as e:errors.append(f'SYNTAX:{e}')
 for token in ['load_repair_spec','load_grounding_results','build_grounded_repair','export_step']:
  if token not in code:errors.append('MISSING_'+token)
 if re.search(r'(?:faces|edges)\s*\(\s*\)\s*\[\s*\d+',code):errors.append('FIXED_INDEX')
 if '.obj' in code.lower() or 'old.step' in code.lower():errors.append('ISOLATION_VIOLATION')
 return errors
def execute(program,spec,grounding,output):
 env=dict(os.environ);env['PYTHONPATH']=str(OUT/'scripts')+os.pathsep+str(V2/'scripts')+os.pathsep+env.get('PYTHONPATH','')
 return subprocess.run([str(PY),str(program),'--spec',str(spec),'--grounding',str(grounding),'--output',str(output)],capture_output=True,text=True,timeout=180,env=env)
def audit(step,source):
 r=STEPControl_Reader();status=r.ReadFile(str(step));roots=r.TransferRoots() if status==IFSelect_RetDone else 0;shape=r.OneShape() if roots else None
 if not shape or shape.IsNull():return {'STEP_RELOAD':False,'BREP_VALID':False,'Q':'Q3','FACES':0,'EDGES':0}
 valid=bool(BRepCheck_Analyzer(shape).IsValid());v,f,_=V.tessellate(shape);cad=trimesh.Trimesh(vertices=v,faces=f,process=False);m=V.geometry_metrics(source,cad);return {'STEP_RELOAD':True,'TRANSFER_ROOTS':roots,'BREP_VALID':valid,'Q':V.qclass(m,valid),**m,'FACES':V.topology_count(shape,TopAbs_FACE),'EDGES':V.topology_count(shape,TopAbs_EDGE)}
def run_part(part,c,config,hypotheses):
 run=OUT/'03_mac_repair'/part;repair=load(run/'repair_input.json');ground=OUT/'04_grounding'/part/'grounding_results.json';source=trimesh.load(V1/'02_cad_part_graph'/part/'source_part.obj',force='mesh',process=False);calls=[];responses=[]
 shared=json.dumps({'part_id':part,'rootcause':repair['rootcause'],'current_metrics':repair['current_metrics'],'hypotheses':[{'id':h['id'],'representation':h['representation'],'probe_metrics':h['probe_metrics']} for h in hypotheses],'grounding_results':repair['grounding_results'],'geometry_residual_summary':repair['geometry_residual_summary']},indent=2)
 planner=call(c,config.SPEC_PLANNER_MODEL,'planner','You are the Spec Planner in Multi-Agent-CAD. Return strict JSON only. Use only supplied measured artifacts; raw mesh and old STEP are forbidden.',f'Plan bounded repair for this part. Preserve measured dimensions and select hard gates Q1/Q2 only.\n{shared}',2600,calls,responses);dump(run/'cad_brief.json',extract_json(planner))
 architect=call(c,config.ARCHITECT_MODEL,'architect','You are the Geometric Architect in Multi-Agent-CAD. Return strict JSON only. Define three bounded hypothesis programs and semantic grounding dependencies. No fixed topology indices.',f'Planner output:\n{planner}\nMeasured repair context:\n{shared}',2800,calls,responses);dump(run/'architect_plan.json',extract_json(architect))
 results=[];all_prompts=[]
 for idx,h in enumerate(hypotheses):
  cd=run/f'candidate_{idx:02d}';cd.mkdir(parents=True,exist_ok=True);spec=Path(h['spec']);require=part!='CADPART_006'
  system='You are the Python Coder in the existing Multi-Agent-CAD framework. Return only one executable Python code block. Do not read OBJ or old STEP. Do not use fixed face/edge indices.'
  template=f'''Write candidate {idx} for {part}, hypothesis {h['id']} {h['representation']}.
The executable MUST use this exact runtime contract:
from case09_v3_runtime import load_repair_spec, load_grounding_results, build_grounded_repair, validate_shape, export_step, write_provenance
CLI arguments: --spec --grounding --output.
spec=load_repair_spec(args.spec); grounding=load_grounding_results(args.grounding)
shape, trace = build_grounded_repair(spec, grounding, hypothesis_id="{h['id']}", require_grounding={require}, grounding_enabled=True)
require validate_shape(shape)["valid"] then export_step(shape,args.output).
write_provenance(args.output, part_id="{part}", hypothesis_id="{h['id']}", representation="{h['representation']}", grounding_execution_trace=trace, MAC_GENERATED=True).
Do not implement geometry yourself and do not alter measured dimensions.
Architect output: {architect}
Probe metrics: {json.dumps(h['probe_metrics'])}'''
  all_prompts.append(template);raw=call(c,config.CODER_MODEL,f'coder_candidate_{idx}',system,template,2600,calls,responses);code=extract_code(raw);program=cd/'generated_code.py';program.write_text(code);logs=[];rounds=0;step=cd/'candidate.step'
  while True:
   errs=contract(code);proc=execute(program,spec,ground,step) if not errs else None;log={'round':rounds,'contract_errors':errs,'exit_code':None if proc is None else proc.returncode,'stdout':'' if proc is None else proc.stdout,'stderr':'' if proc is None else proc.stderr};logs.append(log)
   if proc is not None and proc.returncode==0 and step.is_file():break
   if rounds>=2:break
   rounds+=1;feedback={'part':part,'hypothesis':h['id'],'specific_errors':errs or [proc.stderr[-3000:]],'probe_metrics':h['probe_metrics'],'required_contract':'use exact runtime signature from original coder prompt'};dump(cd/f'repair_feedback_round_{rounds}.json',feedback);repair_prompt=f'Repair this program. Return only corrected Python. Do not change measured geometry.\nPROGRAM:\n{code}\nFEEDBACK:\n{json.dumps(feedback,indent=2)}';raw=call(c,config.CODER_MODEL,f'coder_candidate_{idx}_repair_{rounds}',system,repair_prompt,2600,calls,responses);code=extract_code(raw);program.write_text(code)
  dump(cd/'execution_log.json',logs);qa=audit(step,source) if step.is_file() else {'STEP_RELOAD':False,'BREP_VALID':False,'Q':'Q3','FACES':0,'EDGES':0};qa.update({'candidate':idx,'hypothesis_id':h['id'],'representation':h['representation'],'program':str(program),'step':str(step),'repair_rounds':rounds,'contract_errors':contract(code),'FEATURE_Q':'PASS' if not contract(code) else 'FAIL','STRUCTURE_Q':'PASS' if qa.get('FACES',999)<=64 and not contract(code) else 'FAIL','ACCEPTABLE':qa.get('Q') in ('Q1','Q2') and qa.get('BREP_VALID') and not contract(code) and qa.get('FACES',999)<=64});dump(cd/'qa.json',qa);results.append(qa)
  # Save required per-candidate evidence.
  shutil=None
 (run/'mac_prompt.txt').write_text('\n\n===== CANDIDATE =====\n'.join(all_prompts));dump(run/'mac_response.json',responses);dump(run/'token_usage.json',{'LLM_CALLS':sum(x.get('response_received',False) for x in calls),'TOTAL_INPUT_TOKENS':sum(x.get('prompt_tokens',0) for x in calls),'TOTAL_OUTPUT_TOKENS':sum(x.get('completion_tokens',0) for x in calls),'calls':calls})
 accepted=[x for x in results if x['ACCEPTABLE']];accepted.sort(key=lambda x:(0 if x['Q']=='Q1' else 1,x['CHAMFER'],x['FACES']));selected=accepted[0] if accepted else None
 if selected:
  import shutil as sh;src=run/f"candidate_{selected['candidate']:02d}";sh.copy2(src/'generated_code.py',run/'generated_code.py');sh.copy2(src/'candidate.step',run/'selected.step')
 row={'part_id':part,'MAC_USED':True,'MAC_RUNS':1,'LLM_CALLS':sum(x.get('response_received',False) for x in calls),'MAC_CANDIDATES':3,'MAX_MAC_REPAIR_ROUNDS':2,'selected_candidate':None if selected is None else selected['candidate'],'MAC_RESULT':'SUCCESS' if selected else 'MAC_PROGRAM_FAILURE','candidates':results};dump(run/'mac_run_summary.json',row);return row
def main():
 load_key();c,config=client();manifest=load(OUT/'02_measurements/repair_hypothesis_manifest.json');rows=[]
 for p in TARGETS:
  row=run_part(p,c,config,manifest[p]);rows.append(row);print('MAC_V3_PART',p,row['MAC_RESULT'],row['LLM_CALLS'],flush=True)
 agg={'MAC_USED':True,'MAC_TARGET_PARTS':TARGETS,'MAC_RUNS':sum(x['MAC_RUNS'] for x in rows),'LLM_CALLS':sum(x['LLM_CALLS'] for x in rows),'TOTAL_INPUT_TOKENS':sum(load(OUT/'03_mac_repair'/p/'token_usage.json')['TOTAL_INPUT_TOKENS'] for p in TARGETS),'TOTAL_OUTPUT_TOKENS':sum(load(OUT/'03_mac_repair'/p/'token_usage.json')['TOTAL_OUTPUT_TOKENS'] for p in TARGETS),'parts':rows};dump(OUT/'metrics/mac_v3_aggregate.json',agg);print(json.dumps(agg,indent=2))
if __name__=='__main__':main()
