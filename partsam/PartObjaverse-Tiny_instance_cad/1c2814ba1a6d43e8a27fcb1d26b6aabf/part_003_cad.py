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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1c2814ba1a6d43e8a27fcb1d26b6aabf/part_003.stl', 'relative_path': '1c2814ba1a6d43e8a27fcb1d26b6aabf/part_003.stl', 'source_sha256': '3c86971b65fd32a3628451e9c81702182f7e0fcb2e7dc0b8d920e84ca5602d77', 'input_faces': 56, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4446643590927124, -0.45467835664749146, -0.3999258279800415], [0.3337043821811676, 0.20510420203208923, 0.42601168155670166]]}
GEOMETRY_BASE85 = 'c$}q{&1+LZ6vZbWt){-zHYRDJroPms`7pRKib@~>p_{0Lf(sF?v3<c{Xlq_As1&kyXEy~m-MMfh2)a?*m557Ap|*bX4{^~u&vWC;WCYO(mvipP&5y}rGNfAZ`NQJZN{Y9cCnIZqA!HdMES9X+Vq?a#PtPqp^oSuRmy31f>a{D?>mIQr9;at5d#07XXr_zx^Xa^quFtm?TeZ3A`PQr@^T}G%wkWsn))p-4GlfFlJd@3v%jUnX0op>l_TcNf+|p0qwp8)5_`Iaa%TLW$?z~(rek^I`Ip_I}dy~65zM8A^8$0DsCCxnNo%ua`%gt%uS^cuE$v2vfZFkQ5ROgw`^XAmbrjD=X>b%P5T;+@DAMbU1&U^NGt9!oly^yQ?_V~>=IzHzrzpTtNhx4BOFZaK2-nZl59PVo5b4izfxU}o!?a<|tZeGoKJ{Esn(mfv~@9YP;`n@>sc|KFm-s$*iuFk7`&Q<>2&ZA8oU(MBdmCw1#zuma8rQ>t1a@Lf2=5XG{uXf#T%~;zoeRPzm0(868Yp$zJhH|m$ueL_vudcSU=l=U@^UxmpsC>`^F7HP#wcq6hdbzyt!&FD8BG3_d`B<V<L(mX>7#e{NyL<?J2rTwd^ilBHhtY?@kY3)|ho}ajhv5yXAk{%=0N#KOLI+$vfIa{g`yl!t`0Nez1{l(hQk|e0gPw#pog*W}acBbGgpNT+T|R+60T%lt`Xu=5P4p%h(oayOsj|>h@ENKc)i^W-pMhqf6E2@Zp8|`04t)-M_8IgUFr<%D9ixgtkHS|g9&gz9r@s!rS6d$Bu0Im$C%b=^?oWOvR_8}rt@Jr(+e@$eq!;7~5c@}x&nf'

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
