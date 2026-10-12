"""A1-SCF selector runtime. Preparation only; no training is launched here."""
from __future__ import annotations
import hashlib, json, math
from dataclasses import dataclass
from pathlib import Path
import torch
from torch import nn

NONLINE_TYPES=("CIRCLE","ELLIPSE","BSPLINE")

class SelectiveNonlinearSelector(nn.Module):
    def __init__(self, hidden_size=2048, query_dim=256, bottleneck=128):
        super().__init__()
        self.query=nn.Sequential(nn.Linear(2*hidden_size,query_dim),nn.GELU())
        self.score=nn.Sequential(nn.Linear(hidden_size+query_dim,bottleneck),nn.GELU(),nn.Linear(bottleneck,1))
        self.hidden_size=hidden_size
    def forward(self,surface_tokens,line_tokens,nonline_tokens,k_nonlin,mode="learned",case_id="",seed=42,lengths=None):
        # K=0 is an explicit A1 parity path: selector is not evaluated.
        if k_nonlin==0 or nonline_tokens.shape[-2]==0:
            return torch.cat((surface_tokens,line_tokens),dim=-2),{"selected_idx":[],"scores":[],"gates":[]}
        if line_tokens.shape[-2]: ql=line_tokens.mean(dim=-2)
        else: ql=torch.zeros_like(surface_tokens.mean(dim=-2)) # frozen zero-null rule
        qs=surface_tokens.mean(dim=-2); q=self.query(torch.cat((qs,ql),dim=-1))
        qx=q.unsqueeze(-2).expand(*nonline_tokens.shape[:-1],q.shape[-1]); scores=self.score(torch.cat((nonline_tokens,qx),dim=-1)).squeeze(-1)
        n=nonline_tokens.shape[-2]; k=min(int(k_nonlin),n)
        if mode=="learned": idx=torch.topk(scores,k,dim=-1).indices
        elif mode=="longest":
            if lengths is None: raise ValueError("lengths required for longest control")
            idx=torch.topk(lengths,k,dim=-1).indices
        elif mode=="random":
            digest=hashlib.sha256(f"{seed}:{case_id}".encode()).digest(); g=torch.Generator(device='cpu');g.manual_seed(int.from_bytes(digest[:8],'big')%(2**63-1));idx=torch.randperm(n,generator=g)[:k].to(nonline_tokens.device).unsqueeze(0).expand(scores.shape[0],-1)
        else: raise ValueError(mode)
        idx=torch.sort(idx,dim=-1).values # restore original B-Rep order
        gather=idx.unsqueeze(-1).expand(*idx.shape,nonline_tokens.shape[-1]); selected=torch.gather(nonline_tokens,-2,gather); gates=torch.sigmoid(torch.gather(scores,-1,idx)).unsqueeze(-1); selected=selected*gates
        return torch.cat((surface_tokens,line_tokens,selected),dim=-2),{"selected_idx":idx.detach().cpu().tolist(),"scores":scores.detach().cpu().tolist(),"gates":gates.detach().cpu().squeeze(-1).tolist()}

def selector_trace(case_id,types,lengths,trace,path):
    chosen=set(trace.get('selected_idx',[[]])[0]); scores=trace.get('scores',[[]])[0]; gates=trace.get('gates',[[]])[0]
    rec={"case_id":case_id,"nonlinear_candidate_n":len(types),"curves":[{"original_index":i,"curve_type":t,"curve_length":lengths[i],"score":scores[i] if i<len(scores) else None,"gate":gates[list(sorted(chosen)).index(i)] if i in chosen and gates else None,"selected":i in chosen,"rank":(sorted(range(len(scores)),key=lambda j:(-scores[j],j)).index(i)+1) if scores else None} for i,t in enumerate(types)]}
    with open(path,'a') as f:f.write(json.dumps(rec,sort_keys=True)+'\n')
