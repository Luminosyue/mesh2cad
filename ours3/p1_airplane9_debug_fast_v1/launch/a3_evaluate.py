from pathlib import Path
import sys,json,time,subprocess,os
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
import a2_runtime as rt
from a2_runtime import torch,save
ckpt=Path(sys.argv[1]);partname=sys.argv[2];tag=sys.argv[3];out=E/'evaluations'/tag/partname;out.mkdir(parents=True,exist_ok=True)
import fcntl
case_lock=(out/'evaluation.lock').open('w');fcntl.flock(case_lock,fcntl.LOCK_EX)
if (out/'result.json').exists():print('REUSED_COMPLETED',tag,partname,flush=True);sys.exit(0)
assert json.loads((E/'audits/data_gate.json').read_text())['PASS']
rt.EXP=E
original_sepedge=rt._load_sepedge
def aligned_geometry(*args,**kw):
 s,e=original_sepedge(*args,**kw);return s.bfloat16(),e.bfloat16()
rt._load_sepedge=aligned_geometry
model,tok=rt.load(ckpt);model.float();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
part=next(p for p in json.loads((E/'data/parts.json').read_text()) if p['part']==partname)
batches=torch.load(E/'data/collated_batches.pt',weights_only=False);inv=json.loads((E/'data/block_inventory.json').read_text());batches=[b for b,r in zip(batches,inv) if r['part']==partname]
tf,tokens=rt.teacher(model,tok,batches,out);tf['TOKEN_ERRORS']=sum(not t['CORRECT'] for t in tokens);save(out/'teacher_forced.json',tf)
print('TF',tag,partname,tf['TOKEN_ERRORS'],tf['MIN_TOKEN_MARGIN'],flush=True)
start=time.time();result=rt.decode(model,tok,part,out)
result.update(TOKEN_ACC_TEACHER_FORCED=tf['TOKEN_ACC'],TOKEN_ERRORS=tf['TOKEN_ERRORS'],EOS_ACC=tf['EOS_ACC'],GT_SEQUENCE_NLL=tf['GT_SEQUENCE_NLL'],MIN_TOKEN_MARGIN=tf['MIN_TOKEN_MARGIN'],checkpoint=str(ckpt),inference_precision='FP32; TF32 disabled; geometry matches BF16 training inputs')
result['SAFETY_CAP_HIT']=result['SAFETY_CAP_HIT'] or any(t['TOKEN_CAP_HIT'] for t in json.loads((out/'predicted_tokens.json').read_text()))
result['STEP_READBACK_PASS']=False
if result['STEP_EXPORT_PASS']:
 try:
  import cadquery as cq
  shape=cq.importers.importStep(str(out/'prediction.step')).val();result['STEP_READBACK_PASS']=shape.isValid() and len(shape.Solids())>0;result['STEP_READBACK_SOLIDS']=len(shape.Solids());result['STEP_READBACK_VOLUME']=shape.Volume()
 except Exception as exc:result['STEP_READBACK_ERROR']=repr(exc)
result['PART_GATE_PASS']=all(result[k] for k in ['SEQUENCE_EXACT_MATCH','BLOCK_COUNT_EXACT','BLOCK_EXACT_MATCH','EOS_TERMINATED','CAD_PARSE_PASS','CAD_EXECUTION_PASS','STEP_EXPORT_PASS','STEP_READBACK_PASS']) and not result['SAFETY_CAP_HIT'] and tf['TOKEN_ERRORS']==0 and tf['EOS_ACC']==1
result['DIVERGENCE_TEACHER_CONTEXT']=next((r for r in tokens if r['block']==result['FIRST_DIVERGENCE_BLOCK'] and r['token_in_block']==result['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN']),None)
save(out/'result.json',result);print('RESULT',json.dumps(result),flush=True)
