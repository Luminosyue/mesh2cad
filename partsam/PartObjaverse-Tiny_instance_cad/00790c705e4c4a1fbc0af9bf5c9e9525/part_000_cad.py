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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_000.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_000.stl', 'source_sha256': 'dabff8476f23ba43c361f8bb42469da97d4d4ae9c39f33f5ff0e6f63898b82bc', 'input_faces': 56, 'input_vertices': 55, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.156366229057312, -0.2038702368736267, 0.1585707664489746], [-0.1560533344745636, -0.20339031517505646, 0.15907257795333862]]}
GEOMETRY_BASE85 = 'c$}q{TWkz*6vqF%+tOC6)r(%-rf9d-ZC$DjLQEs!p|%!n#U*UhZjp+zZHUlhToNyC2_l4KgonC45JKX?P)`!XGl>a_5Fu$jAuV(E`-YB?2$M{H-+uY_?3r_R|Jg`=ASqYjDpvbfU#;#<R!Z)4m8*8d;@z8DV_j8Sx9#$&tb{L@%i|4A;mB&A+M#v_+hSd<@!&iyIKO>PFr)?BJLBE)maQ8)<83kV7q@KbiaCDQrj~6n=XF_4O-QRQ4{1Hxzg}t5!_&aSdk)MSsgH#A#-$GzI<%h9FG@@J(cAE~KKOPs^41La_5=9pB=TBLIN_@+@S_>X>)FWb7vUS@Mxp*e<gG)@zeq{=DjoT#!Te3+?U4=0uZ3^jMqV#K-iR<CPDh_-khe?tT-RBD0qf_`A7Fm&GWhTOp88rh^UvVhr!r9ICGz@tzo&n*kMrCEUtcsj;Ty*y@K^Xf^D#;=2Xiw0x5(Rd%kf-8KJ??x|1{@zAHI1w6La{)`~{z9zj_hoV6KI4lxCsM#TD4^BKq9Bc8&Ru3jRIhwdR$m|4MoHz7%t??lAuW^D)n%pXfgL+Tt<T`&ZPlcPsDrp&xbZJo*;$`iVw-uIuyrV4lT1^;_TihVNZ#z~@@M^vklbui_@uX@qZa@5X23_4)Ai1IQcak+(k$^$p*<eHnAJpTjpFBX8w3<9ScRclYkjExMQaA=clHysC%q?%kb_8DgC&Iq3f`^M3e-yLZmVemw}kocRIvW6|f{-8pEz@T076X01Y<qs(*f?i|dWgP#7avCPNdyZf~=+2<Pg7U$#EH^Z#Y{Tdy}8%qW~^S9r#PTinqkM>RGFMWaEQGn;FT8BMWz*j5bYaQ_IN1xG89(<#R`6KkN<)i+3$B%eU`K11EsuplcId`ga%D1-+JL1KZ%jNHn_|3Eb?uf7b?<2m}>0!EaSMnBJNY11d&Y~91pcYn93q#bxY1G0pYGEn0a4NNMGPO{n7EYuVPM{W!qZSrW3&&CmbE$>d)WR%k;b>}MI<+v3T9`sD96>Eiq89q8{rnmfl0Ir-fLfSLEgVTLOr;i%q84UQ3p1&OW2l8W)WSS!VLr96h*~(FS~!VXSWGRPLM<$z76z#csmsY~YT<0^a_S1QhFVxjUCCM%%vbPrq~7Px4gBdZ)X&S10ek*X{rXPt&vN)X-#E2?{7579$+BB#k$$z^VO=8o9nNAHTm'

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
