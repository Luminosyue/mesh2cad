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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_009.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_009.stl', 'source_sha256': 'd4d8326d39a30d9c8696320c94ed2f05af0ac56fc3fe3559484571b1d84ca2ad', 'input_faces': 44, 'input_vertices': 42, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4167429804801941, -0.04199531674385071, -0.067745141685009], [0.0625101625919342, 0.25392383337020874, 0.21116818487644196]]}
GEOMETRY_BASE85 = 'c$}q`Z%k8H7{*U21q-MMmEpf}-6~bXglXN3Ay_kIf0~VcK!^^tos<l9P>N&fG`m?;X4FYkFjF?G%#9%fX8fcBE=bgY(r!?7OO`d!jA-J<Lb83>vh2RkdEM%wiP4+9`91H`bKd)&(|gZ#IgPOvA+MR@{XqZgzE~kBl7vOnc>SBo*LkbwRrt0TL^6E3?(*PkD_(W2G>97UuC3Htz0Pl2tk`nP7TK~CTUn)lliyRZw$fkfB|qP@vD&Nq)o*%yUOk^}pP!{Hn3JV!S043B&|A=MpZcMjdTGdMB&yE5kBHjMXTOKv7ug5eGXliG&AHOw;W!MsvOmYXa7h^Xp=8u?tf*}!y2HiNUp0Ch<BG1q7vW{ncL$n?N_p*<s6RYU`s!!{#(NL9g2OYUUz8*3oPD7K`LIFyA4X)~{*iWKB$PWW?;F8*vHYD+Q9oppez|%Qbv(yTq0i8C>2J-cN4~TceQCkphTyllKfw4^7r(&zg5OEMP{qDPx{ANT_`%cC_o)Z4uFf0iQypxQ{#F<2YhMq*R|a<tMenm?^?NP2zi-NA_^azqVE!v5`@zaP1F}x&5SZJz2kWY6m%jHp)~S_#at!%f%Lk(O&F!4{8OCqSmVSq0H}axijw0XC(+~QUgQ%1LldPBbXCLmLeq(S6_5EUfFBtBXe(~59$^)Y*8Zq*1`+4}rOXn#UX*E6Y>(@)aq%nwm*<biwi>d8}@5}s#a#fUdqF%wR9`y5ZD(XkJpS*~A4TbR4AA{&8a<%0Gd}Eaczp4p!0!QAsgnG{fy0MOz9U<h~&Y(}nj^{g3f3EQ|=5OvfM|A&ek^ZEW@U^oGQOEK7m2;@y=<7q?exeH;%ahOLnIP7q?2jKnz2j5ye2BJK%opPhpuYBNiuCI$(T98C-=Hw<mH%6?6YCchZ{t2<gS8obkL1ezI&H^(YC}8Q;4k>2AAPLNM?Y$d=)k;@0_>OL8Ef|v*FC4znwJW?>SFW`^f2qERhcL1s3H^XG4Fp=mD?ZgsIouyQ8iodVU8YFrj50g^(<y4YvL5v#HU!#Vr^wkV@*_|YLd=irn4qK!J0UgHE{;(4AwK5(^(UrWKDdUb(|g(=&@jqXFZN}JTrlHJZqC4Mm^|DlE^{Y%rvn!@pv-_=}8=<Q<>vgr?R#%C$P4#PU9e*#EfGd$2}!66IrJ*Co>aSPiCFMG_y8yf25Q3n5c(A$cspiq|0fDu^1op>HY6gF){i>{QsHvz6Q}V+w@xhz7#H}iPopzJVsRM+(Q3^_y>vXvYP'

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
