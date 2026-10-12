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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_005.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_005.stl', 'source_sha256': '74c7b5c41039e5dc44641becbfb93425d8a5105eca731b8f46ec6ebb679fc428', 'input_faces': 178, 'input_vertices': 131, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08522355556488037, 0.39260557293891907, 0.027506984770298004], [-0.04071788489818573, 0.4211048185825348, 0.13821369409561157]]}
GEOMETRY_BASE85 = 'c$}q}e{76*9LK+<zYe9Pez$r>wWX@1rHuALe^ISN{j8y@D>b9qs^2_VGW@Y+Y*x}qnG)?OSJ%4jSfARGVX=f{f{=8Ju^Cw~Hf+njKi;>U%V){5UGmQR{k-1a=X;+%_w;&KOHO;=P^KP{Y<<Xqg!7#k6Y9i5S*5kCqNK=L9>1b=oev9^Ts+*qCvRr1Wv&maWE-LvTg!{eqQ{t{#}=nV$C;yxSC&<j6|PvgvTU(c@XW&H<yOwimll><`Eg9*h{QPah}byuCi8!MbPzL)yxi0xJRtRY8aMsvfJWupB{!Fw6^|b(xlwt?A$Z%J0?CcL$tNhz>{Slo+TJS3&3n}T#_Vjlo+VE_C3wxV(~@gP?%OGDT)OX+p5(=^nhd#qM}*{UJ@=}8k|T~&TtDF3NO87)LzC?DpEOEdyI<|o{EMC9M$<DnkLJxgca!tzM=wim{(P<4r#4Z}V_cXgxqj<w^}MsMG?4syfrI29S(_=YS?0Lp^LlaP%8s)XH``KM<$gbOlHAzoRQr5!yMf}Yb*Y0~f2y>Z;(G8BIgj!E%iLJD?<~d5x3lCtdS&ZLIp_448**J(YAwZC-fla^^``CWb@AS3<Hi>01^Xm7Qi9b!wJsaU^DfybZd@4KM6N%VPjbV0&Pj3Yo5V8|*WWFbT=!ld)Yd|A{o0XM_4`$>_#YkAJh!IQl6=93c8Y7Ocgs1M_xcBKtLt`fvgB>&9;y4G`&TxS-^gkr`IUtv*A8lDD6YqDRoB6r|8`Q{C#B94^7Wmcsjl<gj2eowZDDm3*ZiXz$bEi&af;+)STni*jvqgf?#-t^IYaT9qMy|JLq(3_-A!tJ)O8!hwaz!~<oaDX@_MpI;gZ*!$NhgazlP%4gduh0`pQua6gS!e9VG7`)J$=f{ajuL{h=4X=XaLk##_(Sb%@ez@_yT*tM&D}swuAD45=m8hkjd6am}}@jp9c5Dm%IV=<5!WCq5)O%bn{ac}c5_eBR(&F7-Nl@wki@iklD5Qun$2P`%`)BDMdQHPxQH4P1Nk=X#P?475>PkG$g`dG9|+&U~)8$o-E!P(PO!H=kdm{=S^Zuaoy}%y#wjzPH*&adzjBom?MlY9e`LB+2!0JDueIb050M^`->%KGWc}KB}sP;+k1kugjRz$K?IoXjS|8?yymuJw0xxxDnE$iR7kulIy>J;3W5d=yQhR?)O#Zz5e~W7K$%Q-=%)8lWS@vFMO<?_u}AclHa^~nBvBas(OmE^z$UwZ>8HQuI;OJko;p8$&HFIC%J#ZCKt(1?pODN_x{UYd`fW^8n5o>=hqI)`+Ue%wa-1Rn&j2r9j3VPSzSHFnd1h@^#@b!6xX&kI>`0wE|Q!D4Rw<9)V$*&d3L?JZqK})_hwKF#aT*9YntVyZ$b0ys~=wrWK77!zXcT+dVB>EP(0jDe+4Q@`gdP}My34UuRy+h1|N*xnX4UFAhIux$AG=UH5T3h64?X~L=MDxCOAXx0B;Xx$aA?~<BEXCA<yF~LSKYV<N~h6=oh1#Coer?L(vaKCvq@X5A;3IiR{PK5q(E=B6s2Hj=noOKg`tyv&Et7f|=a&7I@4OiEM^PAV=UlGu#h35*`fqL!QrN<?0WQM}C#77=1B1kr!|+LB9l@$OE~Cp&y1$<gQ%3(Dy<ovOg1F<5k}YoyZ|vJ<<0>=a0EUFk3vj5X|JBcY((&1Ca;7`y=<qc?017$OGYB;r_@Axt4N8!4r^6&@Dn<isNNqg~%m1j^;`PPedoO_|@)%z7IN)1Gs|F2cZ+W8&_}iz0n0=u5Oqu0bMuD6y-6KdzNVALGUQ#D4aJ49)KJT4}}LHS8(ZEdGOiDThXmX)^WTItP*)EjxAhsz~`V7c{Eo#`gC+6_v0FZeh4~|Q@AFgpNOs>=1ReAv(cqsraX_C+_PAar^54)^Kjl&ct2zdd^Eft@+z)PTsiQW$Yorc(Qig4@)mUE$eVGT%QXvp7CMnfaZNx!0iDR<T!YaMMkn$}uJP!{qYKAeBQe`dbR#j7d){)7S#pu5z;lpuaNZPnIC3t06g(Vx1=o76Z1@c14d_-PugCF5uu|j=IG)Uv51x-s<YX=ly@pQYFs@kivFJoj;z~oGhAs?qC1JK1=#nr~w#Q8FStcV-f@dRV<Ge}mFyzVbWOx|z>s)KNGT_sY*P>gFyavbXz}`S!i{mV=>EP4Ri9CWU6@4l?k^6GRppQW(@^G$k=*OY!i<zdOpN4KYX3FrG$vsOJawa?jIRocq!uuj;!Nm-g9G`Zf?f>at!+$??`QgL!AI08hzWi~@^GtvK#`@QXD@%@__<O)VaI}-Z5WU4;bM_~#TkS>'

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
