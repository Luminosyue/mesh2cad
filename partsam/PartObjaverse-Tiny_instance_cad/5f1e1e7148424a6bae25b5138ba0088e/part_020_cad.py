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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_020.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_020.stl', 'source_sha256': 'a6c2a6ea16aa92a617b5f2aa105e5704035ced1b6496d47901626239046bccec', 'input_faces': 12, 'input_vertices': 23, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.02302839607000351, -0.03728407248854637, 0.23865270614624023], [0.021570850163698196, -0.0075873713940382, 0.2389117181301117]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?mzTfaUctn`0Kz;BA`E4zMJ1WZsl|GE1(l2p0$_0vfYFovLVW`w85znLs?}3ci<67gtrXO4(k#?<6x7r5i%N<T^WyW1Qc^+UZizX?sX+1KjKqReAYa4CSVzHFQ%9jzfn2}^bV9?yDbx1@=?7267K7-7g_F+N18IkuJz(*M_rmoc`oM}QU~z_j3pzl2hu1SFfazZoA>xi}+rjFKQu;u&!e@whLwrgr*xV-f1z`2p`XK5P^(#PphUs^}@(Suu^A&T8!RjkB7lG;W9*DTH4_Lh6qIwHh-{i><@%0G>DB?X(a~_1~*dv+4paV6BYeI@WvU*LZ`l9wMWO0Q#Q1i8xXCa&OfUy@MeqXJ~9?AU-91!&lm*bo4k^IYG2=Q-&?#>o_r0{9bhlF!O*h#QB!=f$o!RnR!A>yyrwAv$ubAtv{{nhdgu=<;Kr-0*ydjdp!i%}<7{pKq(z~S5h6)#ll0*f=|g5y)65hCueP-vPxQv5dbLc+mewHR0&o*vkN{t7@z<sLhiyc1w#U;trGU@A{bL`vcyK@fn^*pqms2~kPh(1_wBE(&x5HxTmzF^J6t<?{ovAXJQx0hC=C7{s77CzK7s!XUpu*&<Lrh%E%=gS^QK#OzQuh~@xdW+)$&(^;TF#|Fd!-i%Bl%(#jS1ZV(<A94YLt`jvHkaa!-ngx%P0B=^1y+DUBF%*K*BiJ<nsl5ho'

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
