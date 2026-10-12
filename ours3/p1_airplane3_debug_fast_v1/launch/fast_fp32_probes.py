from pathlib import Path
import sys,json,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
from a2_runtime import *
from a2_runtime import _load_sepedge
name=sys.argv[1];model,tok=load(E.parent/'p1_airplane3_exact_overfit_v1/runs/quick/checkpoint-2000');model.float();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
part=next(p for p in json.loads((E/'data/parts.json').read_text()) if p['part']==name);plugin=make_plugin(separate_edge=True);s,e=_load_sepedge(plugin,Path(part['folder'])/'surface_points.npy');s=s.cuda().bfloat16();e=e.cuda().bfloat16()
msg=plugin.process_messages([{'role':'user','content':prompt_for(tok,'',0)}],[{}]);ids=tok.apply_chat_template(msg,add_generation_prompt=True,return_tensors='pt').cuda();rows=[]
for cache in [True,False]:
 set_seed(42);t=time.time()
 with torch.inference_mode():pred=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=s,edge_clouds=e,use_cache=cache,max_new_tokens=1280,do_sample=False,num_beams=1,pad_token_id=tok.pad_token_id)
 tokens=pred[0,ids.shape[1]:].tolist();rows.append({'use_cache':cache,'tokens':tokens,'natural_EOS':tokens[-1]==tok.eos_token_id,'elapsed_seconds':time.time()-t,'precision':'FP32 decoder; geometry quantized to train BF16 input; TF32 disabled','scope':'unassisted first block, fixed 1280 safety cap, not whole-program gate'})
 save(E/f'diagnostics/{name}/fp32_generation_probes.json',rows);print(name,cache,len(tokens),time.time()-t,flush=True)
save(E/f'diagnostics/{name}/fp32_generation_summary.json',{'PASS':rows[0]['tokens']==rows[1]['tokens'],'lengths':[len(r['tokens']) for r in rows],'argmax_rule':'torch.argmax, lowest ID on exact tie','scope':'first block only'})
