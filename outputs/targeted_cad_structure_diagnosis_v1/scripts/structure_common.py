import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,hashlib,csv,ast
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parents[1]
V=O.parent/'part_cad_fitting_v2_native'
ORDER={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def table(name,rows,fields=None):
 p=O/'tables'/name;p.parent.mkdir(exist_ok=True,parents=True)
 fields=fields or list(dict.fromkeys(k for r in rows for k in r)) or ['case_id']
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def status(m):return 'STRICT_ACCEPT' if m['strict_pass'] else 'NEAR_PASS' if m['iou']>=.7 and m['normalized_chamfer']<=.02 else 'REJECT'
def failed(m):return [n for n,k,t,u in [('IOU','iou',.9,False),('NCD','normalized_chamfer',.01,True),('CENTROID','centroid_l2_error',.02,True),('BBOX','bbox_error',.03,True)] if (m[k]>t if u else m[k]<t)]
def failure(m):
 a=failed(m)
 return a[0]+'_ONLY_FAIL' if len(a)==1 else '_'.join(a)+'_FAIL' if 'BBOX' not in a else 'MULTI_GATE_FAIL'
def distance(m):return max(0,(.9-m['iou'])/.9)+max(0,m['normalized_chamfer']/.01-1)+max(0,m['centroid_l2_error']/.02-1)+max(0,m['bbox_error']/.03-1)
def feature_list(code):
 from collections import Counter
 return dict(Counter(n.func.attr for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'box','sphere','circle','ellipse','polyline','spline','extrude','revolve','loft','cut','union','intersect','fillet','chamfer','threePointArc'}))
def all_rows():
 out=[]
 for row in read(V/'manifests/cases.json'):
  d=V/'cases'/row['case_id'];p=d/'result.json'
  if not p.exists():p=d/'result_inherited.json'
  r=read(p);out.append({k:r[k] for k in ['case_id','object_id','part_id','size_class','seed','status','metrics','family']})
 return out
