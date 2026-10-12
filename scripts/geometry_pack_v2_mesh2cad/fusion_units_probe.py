import sys,json,pathlib,hashlib,ast
import numpy as np
import cadquery as cq
from OCP.STEPControl import STEPControl_Reader
from OCP.TColStd import TColStd_SequenceOfAsciiString
from OCP.Interface import Interface_Static
R=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
B=R/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2'
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v1'
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(x,f,indent=2,allow_nan=False)
def bounds(a):
 lo=a.min(0);hi=a.max(0);ex=hi-lo
 return dict(min=lo.tolist(),max=hi.tolist(),extent=ex.tolist(),diag=float(np.linalg.norm(ex)))
def step(p):
 r=STEPControl_Reader();r.ReadFile(str(p));seq=[TColStd_SequenceOfAsciiString() for _ in range(3)];r.FileUnits(*seq)
 units=[seq[0].Value(i).ToCString() for i in range(1,seq[0].Length()+1)]
 r.TransferRoots();s=cq.Shape.cast(r.OneShape());b=s.BoundingBox()
 d=bounds(np.array([[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]));d.update(volume=float(s.Volume()),area=float(s.Area()),file_units=units,reader_unit=Interface_Static.CVal_s('xstep.cascade.unit'));return d
def obj(p):
 import trimesh
 m=trimesh.load(str(p),force='mesh',process=False);d=bounds(np.asarray(m.vertices));d.update(volume=float(abs(m.volume)) if m.is_watertight else None,watertight=bool(m.is_watertight));return d
def ratio(x,y):
 a=np.array(x['extent']);b=np.array(y['extent'])
 return dict(axis_extent_ratio=[float(u/v) if v>1e-12 else None for u,v in zip(a,b)],diag_ratio=x['diag']/y['diag'],volume_cuberoot_ratio=float(np.cbrt(abs(x['volume']/y['volume']))) if x.get('volume') is not None and y.get('volume',0)>1e-12 else None)
def main():
 inv=[r for r in json.loads((B/'inventory.json').read_text()) if r['dataset']=='fusion360']
 selected=[]
 for low,high,n in [(0,5,7),(6,10,6),(11,100000,7)]:
  pool=sorted([r for r in inv if low<=r['operation_count']<=high],key=lambda r:hashlib.sha256(('unit-probe-42'+r['cad_id']).encode()).hexdigest());selected+=pool[:n]
 save(O/'probe_selection.json',selected)
 rows=[]
 for rec in selected:
  p=pathlib.Path(rec['pack']);tf=json.loads((p/'coordinate_transform.json').read_text());d=dict(cad_id=rec['cad_id'],operation_count=rec['operation_count'],transform=tf)
  try:
   d['source']=step(rec['source_step']);d['dsl']=step(B/'replay'/rec['cad_id']/'reconstructed.step')
   d['mesh']=obj(p/'mesh.obj');d['official_obj']=obj(pathlib.Path(rec['source_step']).with_suffix('.obj'))
   d['surface']=bounds(np.load(p/'surface_points.npy')[:,:3]);d['surface_source']=bounds(np.load(p/'surface_points_source.npy')[:,:3])
   for k in ('source','dsl','mesh','official_obj','surface_source'):
    z=d[k];a=np.array([z['min'],z['max']])*tf['scale']+np.array(tf['translation']);d[k+'_after_old_transform']=bounds(a)
   for k in ('dsl','mesh','official_obj','surface','surface_source'):d[k+'_over_source']=ratio(d[k],d['source'])
  except Exception as e:d['error']=repr(e)
  rows.append(d);print(rec['cad_id'],d.get('dsl_over_source'),d.get('error'),flush=True)
 save(O/'probe20.json',rows)
if __name__=='__main__':main()
