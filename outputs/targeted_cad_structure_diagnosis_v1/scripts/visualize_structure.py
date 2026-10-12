from structure_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import trimesh,html,sys
from concurrent.futures import ProcessPoolExecutor
from residual_features import inside
def run(row):
 d=O/'cases'/row['case_id'];r=read(d/'result.json');res=read(d/'rounds/round_1/residual.json');vox=np.load(d/'rounds/round_1/residual.npz');source=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);before=trimesh.load(d/'baseline/cad_mesh.ply',force='mesh',process=True);after=trimesh.load(d/'final/cad_mesh.ply',force='mesh',process=True)
 z=np.array([1.35,-1.7,1.15]);z/=np.linalg.norm(z);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);B=np.column_stack([x,y,z]);center=source.bounds.mean(0);allpts=np.vstack([m.bounding_box.vertices for m in [source,before,after]]);xy=(allpts-center)@B;span=float(max(np.ptp(xy[:,:2],axis=0)))*1.12;mid=(xy[:,:2].min(0)+xy[:,:2].max(0))/2
 fig,axes=plt.subplots(2,4,figsize=(20,10));fig.patch.set_facecolor('#f5f7fa')
 for ax in axes.ravel():ax.set_aspect('equal');ax.set_xlim(mid[0]-span/2,mid[0]+span/2);ax.set_ylim(mid[1]-span/2,mid[1]+span/2);ax.set_axis_off()
 def mesh(ax,m,color,alpha=1):
  points=(m.vertices-center)@B;tri=points[m.faces];order=np.argsort(tri[:,:,2].mean(1));normal=m.face_normals@np.array([.3,-.3,.9]);shade=np.clip(.68+.25*np.abs(normal),.3,1);colors=np.clip(np.asarray(color)[None,:]*shade[:,None],0,1);col=PolyCollection(tri[order,:,:2],facecolors=colors[order],edgecolors='none',alpha=alpha,rasterized=True);ax.add_collection(col)
 def residual(ax,key,color):
  ids=np.argwhere(vox[key]);n=len(ids);ids=ids[::max(1,int(np.ceil(n/12000)))];pts=(vox['origin']+ids*float(vox['pitch'])-center)@B;ax.scatter(pts[:,0],pts[:,1],c=color,s=1.4,alpha=.6,rasterized=True);ax.text(.02,.02,f'{n:,} occupied residual voxels',transform=ax.transAxes,fontsize=9)
 mesh(axes[0,0],source,[.3,.59,.83]);axes[0,0].set_title('1  Source mesh')
 mesh(axes[0,1],before,[.87,.66,.35]);axes[0,1].set_title(f'2  Current CAD | {r["before_status"]}\nIoU {r["before_metrics"]["iou"]:.4f} / NCD {r["before_metrics"]["normalized_chamfer"]:.4f}')
 mesh(axes[0,2],source,[.2,.5,.85],.55);mesh(axes[0,2],before,[.95,.42,.18],.5);axes[0,2].set_title('3  Before overlay | blue source / orange CAD')
 residual(axes[0,3],'missing','#187cc1');axes[0,3].set_title('4  MISSING: source-only occupancy')
 residual(axes[1,0],'extra','#c74637');axes[1,0].set_title('5  EXTRA: CAD-only occupancy')
 mesh(axes[1,1],before,[.65,.67,.69],.2);props=res['proposals'];selected=[a for a in r['attempts'] if a['accepted']];p=selected[0]['proposal'] if selected else props[0] if props else None
 if p:
  # Draw fitted analytical tool occupancy, not a new metric mesh or regenerated assembly.
  idx=np.indices(tuple(vox['source'].shape)).reshape(3,-1).T;pts=vox['origin']+idx*float(vox['pitch']);pts=pts[inside(pts,p)];n=len(pts);pts=pts[::max(1,int(np.ceil(n/8000)))];q=(pts-center)@B;axes[1,1].scatter(q[:,0],q[:,1],s=1.3,c='#29944a',alpha=.55);title=p['shape']+' tool / '+p['operation']+'\n'+('GEOMETRY ACCEPTED' if selected else 'PROPOSED, NOT ACCEPTED')
 else:title='No compact rule-supported feature'
 axes[1,1].set_title('6  Detected feature\n'+title)
 mesh(axes[1,2],after,[.87,.66,.35]);axes[1,2].set_title(f'7  Refined CAD | {r["after_status"]}\nIoU {r["after_metrics"]["iou"]:.4f} / NCD {r["after_metrics"]["normalized_chamfer"]:.4f}')
 mesh(axes[1,3],source,[.2,.5,.85],.55);mesh(axes[1,3],after,[.95,.42,.18],.5);axes[1,3].set_title('8  Refined overlay')
 fig.suptitle(row['case_id']+' | '+row['cohort']+f' | accepted features {r["feature_accepted_n"]} | delta IoU {r["delta_iou"]:+.4f} / NCD {r["delta_ncd"]:+.4f}',fontsize=17)
 fig.text(.025,.02,'All panels: same camera, scale and coordinates. Residual = frozen IoU128 approximate occupancy; display points deterministically thinned only. Green = fitted tool, not independent feature ground truth.',fontsize=10)
 fig.subplots_adjust(top=.88,bottom=.06,wspace=.05,hspace=.26);name=row['case_id'].replace('/','_')+'.png';fig.savefig(O/'visualizations'/name,dpi=125,facecolor=fig.get_facecolor());plt.close(fig)
 return {'case_id':row['case_id'],'cohort':row['cohort'],'image':name,'before_status':r['before_status'],'after_status':r['after_status'],'accepted_features':r['feature_accepted_n'],'same_camera_scale_coordinates':True,'source_sha256':sha(d/'source/part_local.ply'),'baseline_step_sha256':sha(d/'baseline/cad.step'),'final_step_sha256':sha(d/'final/cad.step')}
if __name__=='__main__':
 rows=read(O/'manifests/subset.json')
 if '--ready' in sys.argv:rows=[r for r in rows if (O/'cases'/r['case_id']/'result.json').exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(run,rows))
 dump(O/'visualizations/manifest.json',manifest);page='<meta charset="utf-8"><title>Targeted CAD structure diagnosis</title><style>body{max-width:1800px;margin:30px auto;font:17px system-ui;background:#f5f7fa}img{width:100%}section{margin-bottom:40px}</style><h1>Residual-driven CAD structure diagnosis — 45 cases</h1><p>Source / baseline / overlay / source-only residual / CAD-only residual / proposed or accepted feature / refined CAD / refined overlay. Blue residual indicates missing CAD material; red indicates extra CAD material. Same camera, scale, coordinates. These are diagnostic figures; historical assembly rendering is untouched.</p>'
 for r in sorted(manifest,key=lambda x:(x['after_status']!='STRICT_ACCEPT',-x['accepted_features'],x['case_id'])):page+=f'<section><h2>{html.escape(r["case_id"])} — {r["before_status"]} → {r["after_status"]}</h2><img loading="lazy" src="{r["image"]}"></section>'
 (O/'visualizations/index.html').write_text(page);print('VISUALIZATIONS',len(manifest),flush=True)
