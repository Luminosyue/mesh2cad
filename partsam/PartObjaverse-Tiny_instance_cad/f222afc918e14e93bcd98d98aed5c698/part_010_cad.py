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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_010.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_010.stl', 'source_sha256': '443b5ce34aa7182cec4e6cd3f3725f2a50f6f2f177e799d4907be3a26379e142', 'input_faces': 78, 'input_vertices': 77, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18180665373802185, -0.36363598704338074, 0.1818237602710724], [0.1818075329065323, 0.36363688111305237, 0.8181819915771484]]}
GEOMETRY_BASE85 = 'c$}qI%T7~K6g_=l1wkGb@PTp>v=mB_hf)wMLR-M9>BIp8qYacuVgTEQXbcGhXEO5#{01H1$k#xINE|RSsfmfv4`8Zix9c2w_qk1s-ehO3yUyO{wHLi1mGpT1qV#l#jk>LgH$EXKYK32{XR`U_g-kBIvi8I!8j3nS3SZp5b1OCP66@k=U@?<h$Ogu&!1z)m5V8VGtJ!=uy>f3gyO<$8k$#xVNImx;y_S*h-6JC*YbY49HmrYrYUCE)uf=!XNwi}5J;M8A`EOANeNx>0PI}>0Y@6N-yYc;!p4f5H3(xa=PWonRV&6#@KU=;!>1sbpSNq}leE(cG_OH(ODgL8e7q3xQK^I%$Up8HQK6vYt58cTB7~76I+?&$*xs=Y&bvTdxTuSHrnS31IaavdDd|jpUbr0vUud8&vZegb61HSIdFY$ew{(HB0Uxu%ku6@OH?JK71b1_|?3%cPerdP_>_n_wIzJhM}is{-XO6R^(I`<FL`Th<681vZoZ}<ng;UA{+bq)U*^Vrul{G;xZ`v<z=pAV&d8~$Os_7Bswf0(Y%#dLix=!SooUMXMSgPNcF2fE=OrfdHwo%@98e4mC-jCt()G<*Wx@CnoTx`t1TdF<;NK2i6^eFB~P#8UIJeJY*LqjcLmDce{7S!62I?G=KeT7LDH(q*4~66sOs{K;P){<}|p<i9`pvvLp9GLpa>;Bzu)>?SY?K3Y7Y5M#je;O#Qb$ru4%0gup~q0U0hD00pskMMFCZ^Jv`a2Y>?cfuj?aT#4QCV&^fugd7ecqhh)_sZyzF$KI1o{-TmV+ME$oN|K53l{rb;&B;a)P+%#Ku$OE2&3RJ8GWehLk;nei~#PQ@EZ64#%6)j;DZ>O1I~iey&gqB2&=)5$f!bps&Mb^=!Fk;KGbv|$BR5K`k}Z7?;i9+aW~%G=uI2$yaxA9cnrJ?{35UpybkZjfwkajtQU9!oUjSJ34Q8CA6n5r!js^X(}=uA^r;7ZXhB^IYWk7WfV>9uGKk(aqple>#Ocq!9=)nZFNvSR*Z?pDei~zgzyWaTgFyf2ae=3jF1O!P>0gV(XOjwS|7h?^`_EH(<$;__|5&AxRpcGnRJV8}alW|99~_wCRs'

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
