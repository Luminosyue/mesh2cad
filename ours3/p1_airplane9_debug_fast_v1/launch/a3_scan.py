from pathlib import Path
import sys,json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
import a2_runtime as rt
ckpt=Path(sys.argv[1]);part=sys.argv[2];out=E/'scans'/sys.argv[3]/part;out.mkdir(parents=True,exist_ok=True)
if (out/'summary.json').exists():sys.exit(0)
model,tok=rt.load(ckpt);model.float();rt.torch.backends.cuda.matmul.allow_tf32=False;rt.torch.backends.cudnn.allow_tf32=False
batches=rt.torch.load(E/'data/collated_batches.pt',weights_only=False);inv=json.loads((E/'data/block_inventory.json').read_text());batches=[b for b,r in zip(batches,inv) if r['part']==part]
dtypes={};vectors={}
def hook(name):
 def capture(module,inputs,output):
  if name not in vectors:
   dtypes[name]={'input_dtype':str(inputs[0].dtype),'weight_dtype':str(next(module.parameters()).dtype),'output_dtype':str(output.dtype),'autocast':rt.torch.is_autocast_enabled()}
   vectors[name]=output.detach().float().reshape(-1,output.shape[-1]).mean(0).cpu().tolist()
 return capture
handles=[model.point_proj.register_forward_hook(hook('surface')),model.edge_proj.register_forward_hook(hook('curve'))]
tf,tokens=rt.teacher(model,tok,batches,out)
for h in handles:h.remove()
tf.update(PART_ID=part,TOKEN_ERRORS=sum(not t['CORRECT'] for t in tokens),EOS_CORRECT=tf['EOS_ACC']==1,checkpoint=str(ckpt),fresh_model_per_part=True)
rt.save(out/'summary.json',tf);rt.save(out/'conditioning.json',{'dtype':dtypes,'mean_projected_tokens':vectors,'pooling':'arithmetic mean across projected tokens per branch, first block; fused is equal-weight mean of branch means'})
print('TF_SUMMARY',part,tf['TOKEN_ERRORS'],tf['FIRST_WRONG_TOKEN'],flush=True)
