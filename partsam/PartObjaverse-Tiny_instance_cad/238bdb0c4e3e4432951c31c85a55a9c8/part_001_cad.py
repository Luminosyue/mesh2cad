"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_001.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_001.stl', 'source_sha256': 'aacf95d97d49cda906e8218815ac6b51e7612a06a109dc4badfee3e3449347d1', 'input_faces': 96, 'input_vertices': 87, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4016762971878052, -0.37584397196769714, -0.3771570324897766], [0.385869562625885, -0.0036044418811798096, 0.12857165932655334]]}
GEOMETRY_BASE85 = 'c$}q|%Wq6k9LG;vQ*E_O+fh^Xm?{Q+c#U>cYi=K^Odo@m5TOk-A@Q6kNmJ^^BSb8SVq+m8SV_Fng@r40BnYJ*l~`EmA7Eo);ha0)bKHC8NQ9gG^8L(bX3pGu?l0%u2?f)}xk%zDCjGlQ<F_*iVU<l><Zw9JvwKH4R<Z9uZwhgmo*g_dwsp3KHm8uoq|duE9NQ7~R(rfP5x=+0<BjZ(_C&k)ZQmc=8D_qzdrvG(eQa0vfiQhN&tFyMSvtSWbJX*%M;1K=-TCnIW0w8jM_6iGufBe4@np%^kkUI(@3r|K*AxCrd_?7q{<?Q6uj>^`Z)lxwl;c13t9?=Z3+4DTrYSucaL28l^qn?+*TB!j`J8BdXZ2zpWY6aT-Z;`@dQa@mNAvym;GoT)>QVY@;okR3|Da3hjU|O|RbKa{D?M2>@KQO>SeM!ldE+*}Hf)=pu7)%3t)9<MlE?gTuSG(p|2mR0YQEnTzZkIiYb~!nsl3*5`Gd+EuX~lA92tJA^7@rWYF}OZN;%Hlbfq`8EsR^e?ya}Y4;hY|_nCV>KS>_*!#!yzxA)<ul2NM{eJFe0hwys9F&eOp^Y!dZ(;JHlZC-o&{G-*2@!_>czJwp{J8HhpJY<-!J8Ep>@cYZX+z-M_{h&YFY<fM=o|vEWu1f)nC!QO+b)JpEEv6TJGPU`F)r&rnyyz3ji$0OO=o8uVK9R@aeIoxZ?-Thvvm!&varpJZlat%*_lvJT@JZ_u_tLtgJvnB2zWx}!HwUeruRlp1>yPaD`XhV3{>YxMKS|?Y{Ymmzf0D+*^~#>lXVT{}pWGXT=Mv{B?RVVE`<?L8ey0`OOL%F&<6hqHxR>`k@p);#6XQ$!o$%6rC&ridJMnpGzY|`%UhesPnm%NE%DI2*_+8?lNGp>*<wUwIk2vNVgoso>;_UYQ)g#XG%Kv`EDWm7Gn6)2@aW!%UxEkDyTmxpg5!^&;6|Lnc#(rcY*blBkHh`<ZmB@N<C3qRK4!jKPLuz0jcqzMW$N*9U2f(c;#%;(ta2vQCSr2XphmZ~65O^K35xfq(9=Qs<9=rkB1l|DdK&}RNfIE@R;AYG}<6>GKT9Z+XUC5bW7dRg|1Dp@eLrw?hfpd}5z`0;2ig6LGSvZdZ<YaIGI19x%6X^nHf-{i$;0*A1WFB}tI31Y_P6s=XPOt+!j#e6S64D8F;yM^lL{3E(f!(xb)0%@~JP*a#OKUE&1UVaA0-l0&gQtKeAhW>}!2DpGLMs)SgUkl!fD4gsup8&fxRh1}t%WGYE0ML}mEaZ>;~=fI$QooVxCUH~tN@pT7a&W)3&8Vfg@P%muCzb>Mf`o}>_TmS80Bx;mtE^OztOS8A{+`jSdY+2OeF`|7ulUAzW@jXHf8'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
