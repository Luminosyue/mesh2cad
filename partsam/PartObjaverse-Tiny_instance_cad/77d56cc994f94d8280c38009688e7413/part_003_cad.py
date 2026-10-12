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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_003.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_003.stl', 'source_sha256': 'b119089ce32c81f86a53f8957116b8cf858b048ce3a7bd2dc515603edf882f11', 'input_faces': 36, 'input_vertices': 35, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4999999403953552, -0.2880246639251709, -0.19141268730163574], [0.46197274327278137, 0.3962821960449219, -0.15094375610351562]]}
GEOMETRY_BASE85 = 'c$}q`Ur19?9LLW#r#Vem-IguQYcDGp(R7oDVz-CvVH6|ip^$RvBq645B1Q%GA?Y<JUqU1Z)`MX767-T6!tSCV875A#2IXUWt5JgM{Q2H>76wrV4&TrD@;kqC&hH-1jYb?*3K6Z1cqcobW*mgDUQZM<8c&W4^u|+%6GPW+#La!yEWLO3{F&$l8yO`xe0}j$Z_;;6^&Rg&>hr6<{=wu(GM2bJnCy!)zbkev6{mjcYHTP@#|Jw?ezoI}U%jRNYje>p7^Tw3IjZ^jH?NqI_N+N4`8~?~yD%G<{qNj2=3k3=_1sI@?@>$<4__~RLVlCS8$mrI`&NEEBz$A@xyZj7d0Uac?4Rbo9(ZQTKACuwWqGuA;cJ_dh(E#OwcwSE?30Np9#2BTf4EWj!1ETz7exM9b1UE4PuZWUdN0-$@!G~B_qF2Kf>`%brox{pE{b*Gf4jTJ^Oh1>J`T*7Tlv<yWj|e5;(6LdeE#drHBpa?B0kuik$sZR@puEiUU<C9bvm+KvH!vY?rYP5WqF@u{Zx+UpYi16I_E!Y+}CG*EX(yID|eQ-&UWYI`=hRmb6<a=<>c?4&)pX1LA=%>;t7opOYx*r$9_(V`B+!C)?M!s>tUaUbsy-t!qT~PoQu^VEY-n49a!DMQr)zWsGCab&&TO6VqdKO(TZ1KtnU7cBX&Yqucfa*e@uD;n8})@TR#B<!M}R~I{*6#U@wu4b~}`SS*rot!PU?@a5cD|_8m|+v<~bB??PwX0IdNxfNP-yTnny3XUz$<fthXtJHamKcCZWF2;B*81S`<pU<K@f?g4wiP0+pICa@Q}59|duL-&K5!7We~+yZWe9ssw3+h~tQY<9)*r(e#mrt^;}|A2m<S$R$6nbow|<x3llIN5imm%vVjsSfkePYhL?l>'

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
