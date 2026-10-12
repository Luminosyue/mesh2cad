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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_013.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_013.stl', 'source_sha256': 'b22b539ca095be347b0bd13c58354282fcef68f63b49ac18871564e3ed23d311', 'input_faces': 60, 'input_vertices': 56, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26785677671432495, -0.12484315037727356, 0.22118063271045685], [-0.12173257023096085, -0.08914774656295776, 0.29909759759902954]]}
GEOMETRY_BASE85 = 'c$}qHJ!n%=7`^#xP5rAH`x9;Q^51AoqD>PKK_>@`Hj9Ic8qyc6NL!Oq5D~I=5Ctclx+sFUiXb$0aZ04Eu7ZP3PJ)7y_}%o}*SzmOLG;4moSu8%xi_ce=9Q;B-hkK|5m9>Uy7I;+gv2fp5KCr#akgqUvU3Z!U1G57%c1z;#Y-2;mtA5>+)2%tjcPr0%1E8AolIqnRBgV#Sg*`oov+WB(mz+Z*)Yj(T(2yc^!NB=F=I@mGsa!xU&nwv%7geui@5pfM@#ax^PP8RdVB%D8G5?z<cn{gH+uc%{k5)dtp4oS{1=_ql2@Kgx1D@#U-&#<`Dbs$-`jGkn=c*n;cNNuwS4$0|I@wTx>G;O=lyVB<y$$dAIoR`a9`V(^}~Jb{H!1DYx%4n?yLNj@6Xnp`cXdbhx;nu%3=Lj>y=-c-n99TJ*!>*&~Dpu9&PzX=8J7T@0t7B`QdBlXZ>?u>xcEveQjUXKliQtkLi|U|M0c`nQ!H*9NxcL&-+(C?_cHc{*}-BXTElR-aqsC`L+I4KJTCT+P=Jh=6CbUw%h-!c)ncr2qEF8+rL)nx%#Ckhhpcef41;fSAQ}8-&cQ$&M-kJf=@sv2~k1{9D^=mO%fc1o+RW61#k{JA^-Q7H!vr4oDjx*7;_2iA@?c)F`VltVVrOXka`51h8}?)1s{PPg${x<&_U?KfYc#y7CMXlL*N*630<g8lF+h~<LD&{9RcT|^Z2|GbfJ1GpqB(bul$_Hz+=z_bQ=e9=r4!)FnA1lm~enF1l|uVfAjkYJHh?XLs&Ba?t?x^*hdI}2ci80ALf0SlX?fii+L~R{Me%(=Ng8V=h`detCA2NKxzTrEw+c$F7O^`7qpvDo^rVZo<F^cZI7mW$o68!pR|9Cd!PJ8S=N`jJmr%e(dKS(i+H)a_BTM9VY~'

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
