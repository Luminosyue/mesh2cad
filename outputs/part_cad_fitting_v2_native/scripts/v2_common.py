import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,hashlib,ast
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def dump(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def score(m):return 10*m['normalized_chamfer']+(1-m['iou'])+2*m['centroid_l2_error']+m['bbox_error']
def status(m):return 'STRICT_ACCEPT' if m['strict_pass'] else 'NEAR_PASS' if m['iou']>=.7 and m['normalized_chamfer']<=.02 else 'REJECT'
def failed(m):return [name for name,key,t,upper in [('IoU','iou',.9,False),('NCD','normalized_chamfer',.01,True),('bbox','bbox_error',.03,True),('centroid','centroid_l2_error',.02,True)] if (m[key]>t if upper else m[key]<t)]
def first_plane(code):
 for n in ast.walk(ast.parse(code)):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Plane':
   kw={k.arg:ast.literal_eval(k.value) for k in n.keywords};x=np.array(kw['xDir']);z=np.array(kw['normal']);x=x/np.linalg.norm(x);z=z/np.linalg.norm(z);y=np.cross(z,x);return np.column_stack([x,y,z]),np.array(kw['origin'])
 raise ValueError('No native construction plane')
