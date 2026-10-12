from p1_debug_runtime import *
from p1_debug_runtime import _load_sepedge
import signal
SINGLE=ROOT/'ours3/p1_single_airplane_part_overfit_v1'
pid=json.loads((SINGLE/'status.json').read_text())['pid'];cmd=Path(f'/proc/{pid}/cmdline').read_bytes().decode()
assert str(SINGLE/'launch/cq54_train.py') in cmd
os.kill(pid,signal.SIGSTOP)
save(DEBUG/'single_training_pause.json',{'pid':pid,'reason':'Stage 9: near-perfect teacher forcing but free decoding length 13 vs 6; investigate inference parity before more steps','last_progress':json.loads((SINGLE/'audits/gpu_progress.json').read_text())})
model,tok=load(SINGLE/'runs/quick/checkpoint-100')
batches=torch.load(DEBUG/'collated_batches.pt',weights_only=False);ids=json.loads((DEBUG/'batch_ids.json').read_text());bs=[b for b,i in zip(batches,ids) if 'PART_000__' in i]
folder=Path(json.loads((SINGLE/'data/parts.json').read_text())[0]['folder']);s,e=_load_sepedge(make_plugin(separate_edge=True),folder/'surface_points.npy')
stats={}
for key,v in [('point_clouds',s),('edge_clouds',e)]:
 a=bs[0][key];stats[key]={'train_dtype':str(a.dtype),'inference_dtype':str(v.dtype),'train_shape':list(a.shape),'inference_shape':list(v.shape),'exact_after_training_cast':torch.equal(a,v.to(a.dtype)),'max_abs_diff':float((a.float()-v.float()).abs().max()),'unequal_n':int((a.float()!=v.float()).sum())}
save(DEBUG/'geometry_input_precision_audit.json',stats)
print('GEOMETRY',json.dumps(stats),flush=True)
cases=[]
for b in bs:
 c={k:v for k,v in b.items()};c['point_clouds']=s;c['edge_clouds']=e;cases.append(c)
t=teacher(model,tok,cases,DEBUG/'precision_probe/single100_inference_geometry')
base=json.loads((DEBUG/'single_checks/checkpoint-100/teacher_forced_case0.json').read_text())
save(DEBUG/'precision_probe/comparison.json',{'training_geometry':{k:v for k,v in base.items() if k not in ['all_gt_tokens','blocks']},'inference_geometry':{k:v for k,v in t.items() if k not in ['all_gt_tokens','blocks']}})
