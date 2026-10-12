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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_011.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_011.stl', 'source_sha256': '7afccbe7ca10e9a68365ceabac8485ab8618a8ca6912243012e418096b847c97', 'input_faces': 20, 'input_vertices': 19, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06206256151199341, 0.28328603506088257, 0.12095789611339569], [-0.01385122537612915, 0.30421245098114014, 0.1583738476037979]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?2YqL~JeU|5K$wR?grO|8s3bEvwOB8&ppub604xpyFnY3IsBb_dBSRTOwR%cwadMHmm4doWnuWTKf_hqhQAtr^UVMI0N-9X)EitD!6)0Yukywxl<ZBpO>L?g%>L}DIkPEm#Zdi3}{eBS5_w15AkXmr_?m-aEz?A?NKX9M@GKha5?9zU)I9u&Huz0j0SiQmw*CSx@b!DqT;tp$1g2fruHXa7kyI!vZo6qbIHs`_L$q@7JZ3BxRXh;ByCz$mf0E-(eTMib#X%7}>I8|^6Ogl({#T)ALAntiv4|R|D60rD!y<mG2YE2;S(KxmkEWXeZtiIvSIfyx8`4DmQ3b44s8$F17m?R+Ln#B<FCBE+ii{EIU4|b2Y9mG9FT@Z5)WX=Qo_hSykeA~?s_bl+61vclIH$?pBUWoZmp3DTRKM@NtKWiJrzY=d|fW;>s1H1pggN=}I>-f<N7H4<}7H^2xf!NCt*8>jEOH5#M94agh*ax7b!b9bKdkPpC7(kd4m<rPpk&+-t5CmW}_9U2TLR1noGN3pK@`I8ZDEUD#h|L3~IiYMGD4PQmO;DN{N^?TlAes%zW`?pEpfn2u0)W_zPz++TLTN52n-$7thhh+$8;U_}UMS5EW%EMWLQo813qol=C|eN9769S^Z$>5&W?V%E0yKc*2e|-2*NGa<$U57AX2Bypz?&5u7EC}`2&4_cp#cD3-0IN'

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
