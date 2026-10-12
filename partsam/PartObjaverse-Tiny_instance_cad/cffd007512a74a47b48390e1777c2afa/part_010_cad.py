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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_010.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_010.stl', 'source_sha256': '34860ff0b300d09ae209c55b4d299b011f399b7cdd1d25d7a9e89736a37ad0c7', 'input_faces': 68, 'input_vertices': 52, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3702528476715088, 0.15610405802726746, 0.12844277918338776], [0.3914848566055298, 0.17207345366477966, 0.13207219541072845]]}
GEOMETRY_BASE85 = 'c$}qHT}YEr7(UyaKl8VonmP4r+BVm8IZG`HcM(BJvWvRts+Mk~l-edrRN$?26%pQOL3C9h(M8aOq?lbqP*Kp2LI(X2(VbT%b>8nhJAUW1AnL%&^L)>qJ?A~=d>p=5w<E{R#Mr{Fdv7I=I~k)YVs18?NR9OOCekf~!)I-*%+zUQ@N&<QL$RYaHp<TV`x5Eilz+G3-;?b0hYWvmC^eFb4;~vz^(9E(A3v2&a6Nr8KAhmsft`_%(bg0)E*SqhT-3v^J1@I9M9&8o35}=2b6r{VmDx{<J~y8GFq=Q4XZ+*gyCSD;>4DX+>(U>%CvwI@N<X^(n_ufk*Jb}T_l4f{R_RCAWq#$n(3dZ%{cF1P|9m9YH9xKTHC_5YzYzMsVb!ncvj3$wV&0AcwSP^Q`O~W+XW6UfYr4$8xF&LD+SPnbm-(%YuT0%=s`;8O^P7F99{u7`^&4^F@A$r;%&Y0TKl;P1_ES40^bd8~IbO@&r>0B)?4roI*{Sw9^H}&-40V4rUHZq~i=2Ze)cn4$!avrd_M_=CC$=hbo?lUO_O1#4foH1T&R(1Pw+S_0(`A0dF7(N|#jN`Bka|C8x}3M(CG?&r>b#mR^Q((ZJv!x4^EG|_97}}$?zDP8Xu9c-DYx_F!pD8L9gI;G@Y^{Vw_MF6(#T-;tGR#2UtP`Zo&S9`SI`#lsxn(=%*U&dR}g4@_QO+0`+*|v0oH;OZU*;&R|BiSDW?JX1-xiG@_;t*Jn%xG6TA?-6j%&S+2y=8pvv)E1LiZZ23ku17zPi3Z{yVrY(o)m1%|;%55XJ4bA*>2YbZeFL$l-caG)60L?Z{>2JQqFfjhyAu`a?gU=cW#+p>1z6~Im472wst8t`gx53t^HcJ<gdLN8lCcQ5vpa4R^W&%&GV>;n%1Tfl?hVc>S~FnB940v^FW6Q{G?$i%tlW3O|8dEmL=E?^<J3%mqa3SNrL5+Kb{39JH-b=&N2$DcmM*2lPcxYiFd{h#VJVg2V-o+U4hShthb!CxRdJHv6p^!@_oln4m'

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
