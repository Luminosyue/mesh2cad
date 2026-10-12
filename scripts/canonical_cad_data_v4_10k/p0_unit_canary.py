#!/usr/bin/env python3
"""Advanced DSL P0 unit canary. Operations must be admitted one at a time."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.Geom import Geom_Ellipse
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.gp import gp_Ax2,gp_Dir,gp_Elips,gp_Pnt
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.STEPControl import STEPControl_Reader

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/canonical_cad_data_v4_10k/canary_execution_v1/p0'

def ser(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def ellipse(d):
    c=d['center']; n=d['normal']; x=d['major_axis']
    e=Geom_Ellipse(gp_Elips(gp_Ax2(gp_Pnt(*c),gp_Dir(*n),gp_Dir(*x)),d['major_radius'],d['minor_radius']))
    return BRepBuilderAPI_MakeEdge(e).Edge()
def reload(step):
    r=STEPControl_Reader()
    if r.ReadFile(str(step))!=IFSelect_RetDone or not r.TransferRoots(): raise RuntimeError('step_reload_failed')
    s=r.OneShape()
    if s.IsNull(): raise RuntimeError('null_shape')
    return s
def run_ellipse():
    op={'op':'Ellipse','center':[0.,0.,0.],'normal':[0.,0.,1.],'major_axis':[1.,0.,0.],'major_radius':3.,'minor_radius':1.}
    encoded=ser(op); round_trip=json.loads(encoded)
    if ser(round_trip)!=encoded: raise RuntimeError('non_deterministic_serialization')
    shape=ellipse(round_trip); OUT.mkdir(parents=True,exist_ok=True); step=OUT/'ellipse.step'
    w=STEPControl_Writer(); w.Transfer(shape,STEPControl_AsIs)
    if w.Write(str(step))!=IFSelect_RetDone: raise RuntimeError('step_export_failed')
    loaded=reload(step); p=GProp_GProps(); BRepGProp.LinearProperties_s(loaded,p)
    if p.Mass() <= 0: raise RuntimeError('geometric_sanity_length_nonpositive')
    return {'operation':'Ellipse','schema_round_trip':True,'deterministic_serialization':True,'occ_execution':True,'step_reload':True,'geometric_sanity':True,'serialization_sha256':hashlib.sha256(encoded.encode()).hexdigest(),'step':str(step)}
def main():
    try: result=run_ellipse(); result['status']='PASS'
    except Exception as e: result={'operation':'Ellipse','status':'FAIL','failure':f'{type(e).__name__}:{e}'}
    (OUT/'P0_STATUS.json').write_text(json.dumps({'sequence':['Ellipse','BSpline','Revolve','Mirror','Loft','Sweep'],'completed':[result],'next_operation':'BSpline' if result['status']=='PASS' else 'Ellipse','training_started':False},indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
