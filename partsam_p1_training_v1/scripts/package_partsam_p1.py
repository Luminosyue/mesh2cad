from pathlib import Path
import json,zipfile,csv,hashlib
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'partsam_p1_training_v1'

def main():
 rows=[json.loads(x) for x in (OUT/'ASSET_REGISTRY.jsonl').read_text().splitlines()]
 # A small inspectable gallery, selected by increasing operation count.
 ranked=sorted(rows,key=lambda r:len(Path(r['target_path']).read_text().splitlines()))
 picks=[ranked[i] for i in sorted(set([0,len(rows)//3,2*len(rows)//3,len(rows)-1]))]
 fig=plt.figure(figsize=(12,12),facecolor='#fafbfe')
 az,el=np.radians([37,23]);xx=np.array([np.cos(az),np.sin(az),0.]);yy=np.array([-np.sin(az)*np.sin(el),np.cos(az)*np.sin(el),np.cos(el)])
 def project(p):return np.asarray(p)@np.array([xx,yy]).T
 for ri,r in enumerate(picks):
  d=Path(r['surface_path']).parent;surface=np.load(d/'surface_points.npy');cad=trimesh.load(d/'model.stl',force='mesh')
  cp=trimesh.sample.sample_surface(cad,6000,seed=37)[0]
  z=np.load(d/'curve_samples.npz');kept=np.load(d/'selected_curve_indices.npy')
  bounds=np.array([surface[:,:3].min(0),surface[:,:3].max(0)]);ctr=bounds.mean(0);span=np.max(bounds[1]-bounds[0])*1.06
  for ci,title in enumerate(['Original STL surface','Executed operation CAD','Selected sharp curves']):
   ax=fig.add_subplot(4,3,ri*3+ci+1);ax.set_facecolor('#fafbfe')
   if ci<2:
    p=surface[:6000,:3] if ci==0 else cp;ax.scatter(*project(p).T,s=.5,c='#55738a' if ci==0 else '#1995a5',alpha=.6)
   else:
    for i in kept:ax.plot(*project(z['curve_xyz_normalized'][i]).T,lw=.8,c='#d67b30')
   center2=project(ctr);ax.set_xlim(center2[0]-span*.7,center2[0]+span*.7);ax.set_ylim(center2[1]-span*.7,center2[1]+span*.7)
   ax.set_aspect('equal');ax.set_axis_off()
   ax.set_title(title if ri==0 else '',fontsize=11)
   if ci==0:ax.text(0,-.03,r['sample_id'][:8]+'... '+r['sample_id'][-8:]+' | '+r['split'],transform=ax.transAxes,fontsize=9)
 fig.suptitle('PartSAM P1 pilot | original mesh / reconstructed target / C2 curves',fontsize=15,y=.985)
 fig.subplots_adjust(left=.02,right=.98,bottom=.02,top=.94,wspace=.02,hspace=.10)
 fig.savefig(OUT/'sample_gallery.png',dpi=150);plt.close(fig)
 with (OUT/'accepted_samples.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['cad_id','split','object_id','surface_path','target_path','curve_token_path','selected_sharp_curve_count']);writer.writeheader()
  writer.writerows({k:r[k] for k in writer.fieldnames} for r in rows)
 files=set()
 for r in rows:files.update(p for p in Path(r['surface_path']).parent.iterdir() if p.is_file())
 for pat in ('*.json','*.jsonl','*.csv','*.md','*.png','scripts/*.py','masks/*.jsonl','configs/*.yaml','audits/*.json'):
  files.update(OUT.glob(pat))
 files.discard(OUT/'geometry_results.json')
 files.discard(OUT/'RELEASE_SHA256.json')
 hashes={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
 for r in rows:
  hashes[str(Path('source_meshes')/r['object_id']/Path(r['source_path']).name)]=hashlib.sha256(Path(r['source_path']).read_bytes()).hexdigest()
 (OUT/'RELEASE_SHA256.json').write_text(json.dumps(hashes,indent=2));files.add(OUT/'RELEASE_SHA256.json')
 # Include source STL copies for independent visual inspection of accepted pairs.
 with zipfile.ZipFile(OUT/'partsam_p1_training_v1_release.zip','w',zipfile.ZIP_DEFLATED) as archive:
  for p in sorted(files):archive.write(p,Path('partsam_p1_training_v1')/p.relative_to(OUT))
  for r in rows:archive.write(r['source_path'],Path('partsam_p1_training_v1/source_meshes')/r['object_id']/Path(r['source_path']).name)
 print('release_bytes',(OUT/'partsam_p1_training_v1_release.zip').stat().st_size,flush=True)
 with zipfile.ZipFile(OUT/'partsam_p1_training_v1_release.zip') as archive:
  assert archive.testzip() is None
  for name,h in hashes.items():assert hashlib.sha256(archive.read('partsam_p1_training_v1/'+name)).hexdigest()==h
 print('release_integrity_PASS',len(hashes),flush=True)

if __name__=='__main__':main()
