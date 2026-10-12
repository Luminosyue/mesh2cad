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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_008.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_008.stl', 'source_sha256': 'a79211e11f27257199d16ea20ce548a79da787d3eeaf293c3ae1728a33283db9', 'input_faces': 76, 'input_vertices': 60, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3667924404144287, -0.4454134404659271, -0.38309434056282043], [-0.10235119611024857, -0.29742342233657837, -0.10542004555463791]]}
GEOMETRY_BASE85 = 'c$}@4ZA@EL7{^a}YuP|vEbE{{ZXK>5g(2moV<c8*7B)ny!6llh#ZeqO$5z<f!e*-3W@eV{!(z+~(Q2~DA~7b5nlN52HCYhm3M(yB(KKq<he^n?EPjwg?|IJu;<-i>W4z?a|9Ahr=ef^$&Y`Eimee#W6PJU<MwWIc8I1ABVpeuA5bW*R73itjyYH}x<&w`YUC%!DRIBf46FbQIoE?FlT|sA~;%w^lI9-afvpd)uY~TBQcd#SC{jKeLdIFl?v%7s?K)WxiuXZW!a+h*c`LEY1Uc;M*=f*VgfAso1SLMB9*SRJg(KzW~`nTlYii+o&Pm%9Ea_&3Q$9IySoS&NIs@g`y{mvrN@U!DFuI$b^x@Ye=#OJR%$X5&Zd_#FQewL8^@D~$tgMaGEH91e{%#z68HzfSyx5fJt7o+4ioF-rSB}3$Yx0ihXg^p|Tyws81aoN}F*M0SbmwdmiR^<8m%$)4AA(oJRcGOOO=#@0;PjW-O$bTcvP=ENgS@by^o}ux_U82vepTuRK1<Y~T53lPdKm6zvjSs)A&dI)dtSce=p~&Ji<zM`s>JOb9NErN|cf@61%?pzs`k`6O_m*`|_SMxl<FfDF);%rv-}{h4>*r11GHvMpTPCp&CQGIb>;B}xtn9C>yY63Xqjd|#$LU^K|MC>|GrKt|_kp#FdF#I32i<4Oby0a8ldecy_VsnteecBYSLOBcrfwGRuUIBO)D)-ph88NQp3v4qhUeLmL*!d3Hu%YxUJ(6$q>aX@H@Ap=c0NMurxdG`@_hX_eiMDU9GH~ft8AMW{e6GtE7B8_VxQO-#lG2oeS+$4_)zq*|3}gHhpUA@>lgEkJR|ns!s*L$9)H(_Sl0trz9enR7j=GI7NI&?Jx0Iyq)K_7n4!<T({G6Rd-}#@pACEvGx$H9C134M73;U%rpmt8;+Qq~brv!1^B2Xswq=gWesX*`X7C>j(l~a+F81+jgJZJqUADwzU)g_WRIVp{AbCml^?Gz)?H?SG`;ff4JVej`T0SiIK`rYXmVLbsEB>eMAw!<?=1XHf!|8HpAzGB1#u$%G?R4pEmyQ;0@=MphKU%tK|JBjbQ2)OiEha5ew73hp3TgtchNePI;2bUT89zcraJE9%fUV#XXfe11Tnb$e=6Vmf6s$mPU<F(Ny&GHr&W7fIv%zL)7B~%>4$T6mgL9!)a4xtAS^_QtJD{cDQq<}|aJEAWz;<vRG#i`;&VZW1dfgeAqYZP)0p}xZ==U0MF~Wu(+t5?ag<3cn->gFK1!saS&~;!7crA1TcrCaP>IA#BXwae#!MPFY0XKp-BRFq@)`K^JYoRsZT5uJ#8e9c-K`X&r9{{_+8=-En8@1|wCA>=HazkstHK@rA^?*H?C+7++?$@Fm!TCOD8Q9liO0lN?(@)huuMqzyH2iS=>qz6*kUa7^E!WDIlCLG5e&wcUfBQAPKwk-e0NMM5(E'

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
