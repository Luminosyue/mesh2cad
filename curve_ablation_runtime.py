from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np

_VIEW={}

def install():
    from spatiallm_curve_token_v1 import curve_token_injector as c
    view_path=Path(os.environ['CURVE_ABLATION_VIEW'])
    arm=os.environ['CURVE_ABLATION_ARM']
    global _VIEW
    _VIEW={r['cad_id']:r for r in map(json.loads,view_path.open())}
    original_resolve=c.resolve_curve_token_path
    def load_filtered(surface_path):
        path=original_resolve(Path(surface_path))
        sample=Path(surface_path).parent.name
        dataset=None
        for part in Path(surface_path).parts:
            if part=='DeepCAD': dataset='deepcad'
            elif part=='Fusion360': dataset='fusion360'
        cad_id=f'{dataset}__{sample}'
        if cad_id not in _VIEW: raise KeyError(f'ablation view missing {cad_id}')
        row=_VIEW[cad_id]
        if Path(row['original_curve_token_path']).resolve()!=path.resolve(): raise ValueError(f'token path mismatch {cad_id}')
        tokens=np.load(path).astype(np.float32)
        if tokens.shape!=(row['original_K'],256) or not np.isfinite(tokens).all(): raise ValueError(f'token schema mismatch {cad_id}')
        idx=np.asarray(row['selected_indices'],dtype=np.int64)
        if len(idx) and (idx.min()<0 or idx.max()>=len(tokens)): raise IndexError(f'selected index out of range {cad_id}')
        return tokens[idx]
    c.load_curve_tokens=load_filtered
    original_forward=c._forward_geometry_with_curve_tokens
    def forward(self,surface_points,edge_points=None,device=None,dtype=None):
        surface_tokens=self.forward_point_cloud(surface_points,device,dtype,projector=self.point_proj)
        if edge_points is None: return surface_tokens,None
        feats=edge_points[~__import__('torch').isnan(edge_points).any(dim=1)]
        if feats.shape[0]==0:
            hidden=self.config.hidden_size
            return surface_tokens,feats.new_empty((1,0,hidden),device=device,dtype=dtype)
        if self.edge_proj is None: raise ValueError('nonempty curve tokens but projector absent')
        proj_dtype=next(self.edge_proj.parameters()).dtype
        out=self.edge_proj(feats.to(device=device,dtype=proj_dtype))
        return surface_tokens,out.unsqueeze(0).to(dtype)
    c._forward_geometry_with_curve_tokens=forward
    c.install()
    print(f'[curve_ablation_runtime] arm={arm} view={view_path} cases={len(_VIEW)}',flush=True)
