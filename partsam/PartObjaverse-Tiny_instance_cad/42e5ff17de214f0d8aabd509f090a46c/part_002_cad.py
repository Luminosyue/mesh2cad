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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_002.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_002.stl', 'source_sha256': 'b343fe86ad2fb82db581bc304057b42113867086c1afd8fdd3c111bb18372ebf', 'input_faces': 80, 'input_vertices': 82, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06892698258161545, -0.367936372756958, -0.40670880675315857], [0.06749289482831955, 0.43569064140319824, 0.01295750867575407]]}
GEOMETRY_BASE85 = 'c$}q|dr%cs9LJZ3h)RNZ3)I9_Fa%K$5J^Q=0u`^1>x_;M7`-HqoDAWDnlL*1hm-l%R8ok#HUnXak1Qwi!Bvz{Kur<E#@aM>oH1tvrzy3^{=WOe_E^m{wKKo@e$Mxv{hhPt{PxUVo7Kb9A{o~}DSgJns3>nqqVSO{(y}Z^;i83E1;camR=7!i@agK*ZPR8=was;tmPy5-nOOx39igM;(6QO^p%HRu_7X>-BO`ag5=Ukh`4ci07i8&v!D|_LS$ca&d~}2y6BZ$_l>h71U7vy$U2(8RSEXjf`9xh^pL*4!U0DKOi#~W3et7g*YD@ObM*qWQmq?vs;x3b_Z>@u`He@#A_i^*#ONHt1UB7x8`CF|u=vO-1@OQ3)?`#-+5#!BEG{&9(1mkM&`<$Y-e1ELrhfIbqmxmhtKN@MwXJptF=$@b!v+we#`WoZaxr_e#2@Rz7l6WDH_Rh{Pk-yqmZ}#Oa!6(UAcI>Y+`)bjeGkC5a@=hb)`6&3(ral<g_3jkpSNDY&^ZYCy>!NMn1>dzP5Wcfb!TjZ)e}S(&C^~?4`6{flJm!;g$TKY+zLeen8jWlBdfX!TX*a%spO(K4>-yUq_|A3l*cW?Rcw>#pSAN>kgy&7VVLXp@I((Nj0{dd0U2N>5&nWozH`|SQrc^cIIpz#A{E*ml=)Zl|7x?{NIDBo7R*(Gm0+7ev7-Y=n!cfddP1$nQ>`Sp1@%-}b*9Bk8yMytZmlFivp5%t-aYcUDAm*>f{z<OKt!7_6uGOM_?8gRiTtE1(fGVNCHmk=`<lCDp_;TS^Lpxepg!!}{D#N<kGe!SGV-f17>A@9Yo?Cy}jr!@mTJV)a`TOC&Z4rFwddXq<lgpZg{Nv9YMgH$=YK1%prkqH`eZE3}`OXp4vu4|PQpmsbbS?R6<YHmJqz`-4VchrpPGFtNiuc1$*?@I%&g@xd_O*_+M%~<BgZDye>sbvwVM87@##Vv(#oXMB`%;&o4ppzVO89CUe5GwKe91cn>ma%9fv=rgkGfLJnwkYa?p4&Gl32G2^Diuguik3LxXO&2a<eZ*Zu|;$dn<J(?l0Y8<f+_dJpbyh*UY}%G9C44w|?7Z_SI6^sL%E)!FPE$P@h`PptEM*nLO7xUxMce{T1hvTB9CQh5lOK4xEEp+M}z&d>+T4KJ6cG7JO}Z`4Q~%Qb`=w(QfSL-5{aA(r+`?Mcq){D)g@@cVOLe716)Z=)}HwTyGKb_y_Mp|MNwHFTHW|bNKgr3BEn3_!#+e=_Qwt=W@w$@}0MLT@l9pp!X@%ZBhF%Vf`zYqHbj$AECcm(ung}%?Yaz<})V&_24W!x*Pp|Pxplm2*kOnRXl1j`*zE9<6O;IiF4Iey#Vj$U+Q`J%mcXps=skQrx<yj`c17yp5<$iM~j<y5c7WKeeCpw_s%AKZ9MepxTJXMsrBfle{E!Em_9Ygq^nc^{!?R7?7#cei2C238sqdi4A5f?2l2}s#Qj;jGxuli#oCjZ)R&pm!rY5_I0x}C4&ne-U*-U2KMrCKR(EF7Zp<Fc-W<ezS^F`^v5sQx$4vSn^C;$c4&u?QLCmBw^JwO=9K;E%1DQz&F()u5au6%5!OWx~%nI{(4&o%%!OWyDF()y<!a<zO8p=!>#+=MNfrEGw>riIWKFpJtqdAC2a1g)1LEMG4D>JDZa~I~$i`bLZi<vZ#*^~Ks4&o>d;usF%k$OzjBUO(`*2&DIvCOgDH<E)mf;Ett^f~4T=5SUYX3`$aq(hiVQ<zhDPT{PP%n_{Ao}tH7J#2dP*27<qDSAw2oyI|IW%XyaS>4<%9{==L=g&*UqMQHtJbR~jY?<%O)pI>P#BA0sv_JYw=q}~!dKaVo0dQG4!~'

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
