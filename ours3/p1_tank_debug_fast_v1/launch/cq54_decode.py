import cq54_train as env
from pathlib import Path
import sys,json,subprocess,time
import torch
from cq54_protocol import END_MARKER,prompt_for
from spatiallm_curve_token_v1.decode_curve100 import _load_m2_checkpoint,_load_sepedge,set_deterministic_serialization
from separate_edge_tokens_v1.common import make_plugin
checkpoint=Path(sys.argv[1]) if len(sys.argv)>1 else env.EXP/'runs/overfit'
out=env.EXP/'decode'/checkpoint.name;out.mkdir(parents=True,exist_ok=True)
model,tok=_load_m2_checkpoint(checkpoint,'cuda',torch.bfloat16);model.eval();set_deterministic_serialization(model.point_backbone);plugin=make_plugin(separate_edge=True)
parts=json.loads((env.EXP/'data/parts.json').read_text());reports=[]
# Short parts first provide early free-rollout feedback; every part is still evaluated.
parts.sort(key=lambda r:r['full_target_tokens'])
for row in parts:
    start=time.time();target=Path(row['folder']);dest=out/row['id'];dest.mkdir(exist_ok=True)
    surface,edge=_load_sepedge(plugin,target/'surface_points.npy');prefix='';ended=False;blocks=[]
    for i in range(12):
        messages=plugin.process_messages([{'role':'user','content':prompt_for(tok,prefix,i)}],[{}]);ids=tok.apply_chat_template(messages,add_generation_prompt=True,return_tensors='pt').to(model.device)
        with torch.inference_mode():pred=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface.to(model.device),edge_clouds=edge.to(model.device),max_new_tokens=1280,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id)
        text=tok.decode(pred[0,ids.shape[1]:],skip_special_tokens=True).rstrip();blocks.append(text);print('BLOCK',row['id'],i+1,len(text),flush=True)
        if not text:break
        if END_MARKER in text:
            prefix+=text.split(END_MARKER)[0].rstrip()+'\n';ended=True;break
        prefix+=text+'\n'
        (dest/'prediction.partial.py').write_text(prefix)
        if len(blocks)>=4 and len(set(blocks[-4:]))==1:break
    (dest/'prediction.py').write_text(prefix);(dest/'generated_blocks.json').write_text(json.dumps(blocks))
    target_text=(target/'target_chunked.py').read_text().split(END_MARKER)[0].rstrip()
    if ended:
        try:
            p=subprocess.run([sys.executable,str(env.EXP/'launch/cq54_evaluate.py'),str(dest),str(target)],capture_output=True,text=True,timeout=240)
            (dest/'execution.log').write_text(p.stdout+p.stderr)
            result=json.loads((dest/'metrics.json').read_text()) if p.returncode==0 else {'valid':False,'error':p.stderr[-1500:]}
        except subprocess.TimeoutExpired:result={'valid':False,'error':'geometry_execution_timeout'}
    else:result={'valid':False,'error':'missing_predicted_end_marker'}
    result.update(id=row['id'],case=row['case'],part=row['part'],predicted_end=ended,generated_blocks=len(blocks),reference_blocks=row['blocks'],exact_text=prefix.rstrip()==target_text,seconds=time.time()-start)
    reports.append(result);(dest/'result.json').write_text(json.dumps(result,indent=2))
    summary={'evaluated':len(reports),'expected':len(parts),'valid':sum(r['valid'] for r in reports),'geometry_pass':sum(r.get('geometry_pass',False) for r in reports),'exact_text':sum(r['exact_text'] for r in reports),'scope':'full autoregressive block rollout on training parts; only previously generated prefix, no target-code prefix; oracle CAD curve inputs','results':reports}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print('ROLLOUT',len(reports),row['id'],result['valid'],result.get('geometry_pass'),flush=True)


