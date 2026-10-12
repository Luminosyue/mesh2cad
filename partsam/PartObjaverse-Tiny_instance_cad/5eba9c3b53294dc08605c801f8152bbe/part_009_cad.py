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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_009.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_009.stl', 'source_sha256': 'c988ff788d77dc60ec952470d59c96343e3f2f43cdd0a6dc2a16090c870da210', 'input_faces': 24, 'input_vertices': 27, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08360590040683746, -0.07387152314186096, -0.08334358036518097], [0.04588405787944794, 0.10796648263931274, 0.08283519744873047]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?c8*3N4rT@h5awYJVJJ&2D#=VvE!N8`sAOai0E>eFjGpWl>KhQr$WX>mt)7xvoLr=CrJ!z;W}&X5pq`drR8o|f7oT60k_r-cOUx-w1&SAEBo?Fs`5H#%Its>`ItsN4<N_|B6C8}vx9$hIMeNpG5dGkq$VPh*f6t*UU~xz3)gbzSh3{&RxPxTvW)Q#Oe*Z?WeEi?}An^lc_cww08yD{e@fU<{2kT2n%m<4%*u8|v&+;__oA)ba9he{FzY45wvh`xH`L>%@L&Rq<1iK?L8>|mq{J<W!O<?sWCxG=c9600#roR|0+mA&&VbAlWVD-{^5b?^J5PBQbJ+d2Dg84<y!2VybyksLbaRu%GFzq1Zy%;PWnYatYZ<wUMa6cAthRAyh!1O7lDPZvjQH|hmKC%sBKTP}vL|maacNJLufr3CVZPD2UcF#KjNIap5Hw3-e0_H3H%>>g8HhmyE;lBjL-X*)5!1TWlYr*17Qfu~O5kC-n9UQ+5tA4bDX^n1hdPuPOz5&elE?o>UKQs~Se=T=Ne4>dr^eKVkr9rlCIaoYs0XQ5T7{kEshl>Y7#2Gf2Y_$(S$wi6I#upYa0=*2xoWNX^mWY&vK!P9uqp@e9OcUa=kO{?ENCM~vVIUR-VkszF0?HPH@`a#mDJWY2%I9MM6%z=(5>R;wsF)Cx=7F+7G&__n1Z4|AX-+7c7l=VY$qmFDK+Fcj{7?*H3qombD4QFqUJy!)L)jo&63XU<s)LqV44|NAh0;t=Hi%|{vRR>QQ27$z&B!FejH`%5fCg}UA{UtGI#H7avQ9UkS@1*>;LQs1AJ9Qe422+#AlEPe059Yi82'

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
