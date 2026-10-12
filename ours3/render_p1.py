import json
from pathlib import Path
import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path('p1_batch_run')
for case in ['airplane','wheel','kettle','toaster','irregular_highpoly']:
    c=ROOT/case; pred=c/'predictions'/'A'; rows=[]; meshes=[]
    for rowf in sorted(pred.glob('PART_*/row.json')):
        row=json.loads(rowf.read_text()); rows.append(row)
        sf=rowf.parent/'global'/'pred.stl'
        if sf.exists():
            try: meshes.append(trimesh.load(str(sf),force='mesh',process=False))
            except Exception: pass
    if meshes:
        allm=trimesh.util.concatenate(meshes)
        allm.export(c/'p1_assembly_global.stl')
        v=allm.vertices; f=allm.faces
        # downsample faces for responsive raster rendering
        if len(f)>18000:
            idx=np.linspace(0,len(f)-1,18000).astype(int); f=f[idx]
        fig=plt.figure(figsize=(10,8),dpi=180); ax=fig.add_subplot(111,projection='3d')
        poly=Poly3DCollection(v[f],facecolor=(0.35,0.62,0.88,0.85),edgecolor=(0.08,0.15,0.25,0.12),linewidth=0.15)
        ax.add_collection3d(poly); lo=v.min(0); hi=v.max(0); mid=(lo+hi)/2; span=max(hi-lo); ax.set_xlim(mid[0]-span/2,mid[0]+span/2); ax.set_ylim(mid[1]-span/2,mid[1]+span/2); ax.set_zlim(mid[2]-span/2,mid[2]+span/2); ax.view_init(elev=24,azim=38); ax.set_axis_off(); fig.tight_layout(); fig.savefig(c/'p1_assembly_3d.png',bbox_inches='tight'); plt.close(fig)
    report={'case':case,'method':'P1 surface-only arm A (checkpoint-8000)','segmented_parts':len(rows),'parts':rows,'valid_parts':sum(bool(r.get('step_ok_global')) for r in rows),'assembly_stl':str(c/'p1_assembly_global.stl'),'render':str(c/'p1_assembly_3d.png')}
    (c/'p1_report.json').write_text(json.dumps(report,indent=2))
summary={}
for case in ['airplane','wheel','kettle','toaster','irregular_highpoly']:
 r=json.loads((ROOT/case/'p1_report.json').read_text()); summary[case]={'segmented_parts':r['segmented_parts'],'valid_parts':r['valid_parts'],'success_rate':r['valid_parts']/max(1,r['segmented_parts']),'render':r['render']}
(ROOT/'p1_summary.json').write_text(json.dumps(summary,indent=2))
