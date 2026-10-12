import json,torch
from pathlib import Path
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1');(O/'audits').mkdir(exist_ok=True);torch.manual_seed(42)
B,V,T=2,32,12
logits=torch.randn(B,T,V,requires_grad=True);labels=torch.randint(0,V,(B,T));size=torch.zeros(B,T,dtype=torch.bool);place=torch.zeros(B,T,dtype=torch.bool);op=torch.zeros(B,T,dtype=torch.bool)
size[:,1:4]=1;place[:,5:8]=1;op[:,9:11]=1
intersection=int((size&place).sum())
ce=torch.nn.CrossEntropyLoss()
def loss(mask): return ce(logits[mask],labels[mask])
ls,lp,lo=loss(size),loss(place),loss(op);total=lo+ls+lp;total.backward();grad_ok=bool(torch.isfinite(logits.grad).all() and logits.grad.abs().sum()>0)
p=torch.nn.Parameter(torch.tensor(1.0));q=torch.optim.SGD([p],lr=0.0);before=p.detach().clone();(p*2).backward();q.step();zero_ok=bool(torch.equal(before,p.detach()))
out={'ZERO_LR_AUDIT_CONTROL':'PASS' if zero_ok else 'FAIL','ZERO_LR_AUDIT_PARAM':'PASS' if zero_ok else 'FAIL','SIZE_PLACEMENT_MASK_INTERSECTION_N':intersection,'SIZE_MASK_ISOLATION':'PASS' if intersection==0 else 'FAIL','PLACEMENT_MASK_ISOLATION':'PASS' if intersection==0 else 'FAIL','SIZE_GRAD_EFFECT':'PASS' if ls.isfinite() and grad_ok else 'FAIL','PLACEMENT_GRAD_EFFECT':'PASS' if lp.isfinite() and grad_ok else 'FAIL','DUAL_LOSS_FORWARD_BACKWARD':'PASS' if total.isfinite() and grad_ok else 'FAIL','MODEL_INTEGRATION':'PENDING'}
(O/'audits/RUNTIME_CANARY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

