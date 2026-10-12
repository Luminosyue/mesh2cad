from pathlib import Path
import sys,json,numpy as np
root=Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(root/'scripts'))
from curve_token_v1.fit_curves_from_points import fit_line,fit_circle,fit_ellipse
out=root/'ours3/tire_part006_p1_inference_20260919'
p=out/'packs/PART_006'
curves=json.loads((p/'curve_diagnostics.json').read_text())
for i,c in enumerate(curves):
    xyz=np.array(c['encoder_xyz']); kind=c['type']
    f={'LINE':fit_line,'CIRCLE':fit_circle,'ELLIPSE':fit_ellipse}[kind](xyz)
    if kind=='LINE':
        t=np.linspace(f['u_start'],f['u_end'],256)
        fitted=np.array(f['origin'])+t[:,None]*f['direction']
    else:
        center=np.array(f['center']); rel=xyz-center
        if kind=='CIRCLE':
            a=np.array(f['x_axis']); b=np.array(f['y_axis']); ra=rb=f['radius']
        else:
            a=np.array(f['major_axis']); b=np.array(f['minor_axis']); ra=f['major_radius']; rb=f['minor_radius']
        angles=np.unwrap(np.arctan2(rel@b/rb,rel@a/ra))
        t=np.linspace(angles.min(),angles.max(),256)
        fitted=center+ra*np.cos(t)[:,None]*a+rb*np.sin(t)[:,None]*b
    c.update(curve_id=i,fit=f,fitted_xyz=fitted.tolist())
(p/'curve_fits.json').write_text(json.dumps(curves,indent=2))
print('Exported fits',len(curves))
