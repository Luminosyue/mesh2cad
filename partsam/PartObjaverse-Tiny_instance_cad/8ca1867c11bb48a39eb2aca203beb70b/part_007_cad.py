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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_007.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_007.stl', 'source_sha256': 'fae1108d94ac3080b0b24b6cbb6842426a12febd933b04e980699e6997898162', 'input_faces': 44, 'input_vertices': 41, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.18103082478046417, -0.2727168798446655, 0.12508435547351837], [0.18888671696186066, -0.1384611874818802, 0.26136282086372375]]}
GEOMETRY_BASE85 = 'c$}q`OK1~89ET^5YMV4o(<b&|AKThyBc?(z2Q5lN1r>^tOP~tUgeJjaNzx<~#aAwR@*oJ+W59!;Ac7~0&}}zOjHzwyQ78ljy?Br!NNEvww!e+L>j<I)!|%&Sc6Mg=zq5f+li5jjTMzlV^SF1+ObG4u#7SnNsm$a=G<`UpylNngvZqbS`{#mZ1LqB7hFs$#(ey-$AL97qv7@|~<70_bCKZm4CsL6p^{2v9>8Rw>m%_=Y^xNYb^m0cIdbu0izc!0Bg`C-29F|h}wy`=dWvDp!dRXPNBX?!*ANx{JdvZCqLVYC`TvB^s<k(y4$+{=68E4~WnR?;-9Z~HoC!drwJ~<%YKRcLtC(kGTVu|UWie<GAeSEe?eYV3Qvb?Y}wW9X^{DU>kdf~ZG5!vTnT`90Uck#y?wa<kg$@|0Eujg4lXW3rXjMHS=^;-=KEHBu7Yidu{KkV-3rb%RZKcCjDiwtxx%j1hif#tbFbDHt}+jH`BA?Be)mJhj3tg5~6JW*o(U-A0?lUvpjb3X9;`Ec(~7g_67ynekQySu>JPsQu^Q<%TK#Cl$e|Lu7N$Mej3fY;YU<>8jds;lgUvdF4W#p~;{a%N<aRsU75tN&c<%Z2KF1DaE5b9VakJtHBs*GZ>REUY?`sH9Cv_K`H{`@18__uofSi!_HCsk@M7unX)!n!paQ4QT}1z*eLIYz1481Wa2!*aF^*PPq=*0ImZ!BAdXCU?*}P*a>b&wu0NiUC0h_7q}nEf&0NcvKP#QJ;(!K57>?D0lUF{$Zl{SxD&Y_+zD<&wt(Bf%}5ux8Ei*7z;<vg(gv;t??GC@fl-6eY5LPA_E*cw4^#cY)nBQ74b)f8N@G=Dioj?My{}X>MlvmBm{tJ!32Q%`=>'

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
