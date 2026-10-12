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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_006.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_006.stl', 'source_sha256': 'fa2179bb9dc39620b17e7011b061045c325caf96224002cfa88f828177af9e56', 'input_faces': 26, 'input_vertices': 30, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3125220537185669, 0.19539731740951538, -0.14151377975940704], [-0.17695912718772888, 0.3867211937904358, -0.0002793803287204355]]}
GEOMETRY_BASE85 = 'c$}qFZAep57(Uyay1Cr6rOq<fuUW0gk0d4RM$jM02BH{5ZRl)*INL<1Fs?-qnNk=fq&O`M$|RIXwDM|@`Gw!u525v=ADJc5mj!C~Jm**%1yKiHp65LGz0Y~y!+ozUT@_#?Y;7X(pM-3iiVzw)VkD(bPf0<p)4RQ>_=JKOpwqRC)frg_Y=;!2l$^5UIlZ|aORCwjJAaqOYPRINJtZDT(NVW2&q?+DjzX_f*1axAu~Xj1CGN1A6E|DUW#)ffTDb)AFq!D0wJhkz_Q+r_IG8~9!t4HVisH6o!_ZThF3x(OORpA2scv4ZYk;0p$nqnykWU)ZYOycVLKkMUCZRVoAK(4AV|X4l2OnW6=N5dYC!rHV8hpgIxEt6XxdvToie)~hGkkP!uei$ex#S6|`&@5s!}nei^ZyV(fI6e|QIBx0eH41HvJXBR-(N&MJ(bWUbu0Y+nip-*$7)BQPX#@PfAvk)Z|4Q*q9nkd)Kp(bzO@v(aP|rMl3spBUt*1$<<D<reKmeWU;c`{%)hO73is^3)C?c57CM<3Lp_q9e2l!5)?xT0ERLhjZ$)=-o~nKb`5kq*2Y-tR^$UY0rq6`HN8FOy4gE41gx@<8`XT}K5205U4#2<V3ViH+jSrC5f3hFX=QTLj7aP-qJY9Alu%RA0$(`<?d-G5-bU`b@U!2W+guJf?mVd@Dg1+_*OYD9#p8=}|ac}mVu1@T~EcF7NI^_FZ<)~AtX?hBuu$`=am%h8pwrU#ho>zyrD+r;Xk*6`=v0@adNY^s{eiRFm{%RBxlK*=Y=`3pGSi^&IJ;y-K^_+*wu|baYazyi>Jd$G+=aHNnIYw}9<UEYyTF%2b58)Wjc?jph978z|=3LD&kaLPE&efbNIVw2k*AA}aJcwfe=M;6E2XStYBSwyOa+u_>r7M(1)t`RBKbMFDSN@QHeRK8avhvL;+3Uy0V@p>Dvci?*xQykrL-HM-cv|H'

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
