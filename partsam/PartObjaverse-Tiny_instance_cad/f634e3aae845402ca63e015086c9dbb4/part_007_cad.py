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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_007.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_007.stl', 'source_sha256': '4f0de95e90637594db65dc48e6c9ca630095b1af86add8b0c1f9dfab917d5352', 'input_faces': 316, 'input_vertices': 265, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3086753785610199, -0.22661805152893066, -0.34212684631347656], [0.20542317628860474, -0.11042486131191254, 0.14164939522743225]]}
GEOMETRY_BASE85 = 'c$}r033N@@9>z~1qB@uwMNv0YgND9PLj?EqNolIQw8}HI+*A@n(;z_~MUSCsEJ{73iEAw7sYnnSauOFIR1!rE<+i00CB{~(!~XC6o%_z&Z+ES?-n(mk>-+ic|Ln8(K6~$b?~3>yl|sTa@e0=tAG@%mUp-AD-LHjd<C4<G3?Gt|-YRv}_#mwY&*^3PqF#M^#`h1>#%XUvBqpT~NsH*{is+QwAtKThkvuYOOj<(f;E`#GNtAa>NJ&p(dHS$~QAzCI&04o>8|iA(JkmAE^*_GuWnJ*}Ej(60eJKw*LhhM7=6HcBZ}8iv%6!+`j@<KDNeO>HZicg+pVu5DcMZMh$UW`#B2{i4iOsj?-qxGS$&HiS_LA#=lKU_3<GD6)Ezh;+Mm~GJoXhq4r#<(o>aE<WH;ye3_f0e$?aR4b?_GbnNL6p;R=wVTv}nhF%+bD_%k^gDvLaQzl?UoGy7S!ACTyRhUdrWq^HjegRlSv4_1;!3%I(kBsyAKr%k9ti&vO6Ou~=6RiTtY=M?dA<y04Xcnnx9>>aE<WH(&g+jOUBu9PP`wTraP;KwiIbk*Xalx9VNJH<zi#CFgRzJT5s8tmhUPWvco2?4DGndhT)_m`~*LbC>f#{qqxeZk-P<oCC)1y~|YVS<VCd1-ZPQ<vcLn6K%>=`%%v2dU-#}d7wYN8i{d9=ZT!l_40Wl=YjPzuC8NU1=f$02lk`yz$f;3_T-LK=H~Rdd>`q{l0}YlIIw?_dk0_GtIEwmhj?!OaNd#2>q@iQshoe<{@ktH`dpB6t3TF$*QEY<J+&S6hIWwWTDM1>?W7cl{&y)?=H{A6XMfQDz<rmBT(7cR%uoF*>2C6lNn#$>FBSbfeNH?-E1$QR=SFIiQr-@7s~vNAHGUuS%n(tZwm{T(Kf>opKNBbVS)5+X`&DqHOqIL7sa9&wy~ERZZWLrW+HoD|&vSFhfih)YeIc*cq;|||;Ro%xRj&or65}{6-8Zwi(4JfMdQ=|I4dkAqFZ1g?PqccS=F@m1OgzWgQyuF>&aLO7ce*0#CNy=_%ehr={IZCzGh=0lm=~*kDc34Qz4zIPId1zp!TK?!Twg2JkKdTibA5M-$ghZf;o32m=hlAl-V*CmZ<5J#YdxFR`6=bvk-8$UJ9C%YKL0UQ#OJ+~8@Jo@^<c_*<x(*pQm#*o66?C2l(!boOS`t7=hpMpT{ZZ9T~h9i)cJiqa((F+{Jw^i8{a-9_KlopiS^^U+9=;`doCuPmz*1TUjB`Zd2XF2R=xkxW;_p^C)Vd<Q)h0rzs1{eJ^4J(&5YGz-B;1Y_X8>S=cZ!3y&bteG+LayoBKN2*Ty&G``z=A$gT6ioa!3O$KUeg9=C1XTK$)EYrNWtg{IrKFRXewx9SbEYa#Cs&VT=?e#ce0ad0)SH<zUNRP$*p_4@4V-;aGE=N{|}v*tRVeP4L6FN`@GefE7}Vqa*JxBKkt-+ErUl<O1giFRt4JU8ke5&J9Zb5TFK(0Sjj;iCR%k+^Ty{my>2^ojb5KF7GUH%mo*$|*-b&6s1N{_As&acT3;^W0T(+S!hj2kyIh&;k4W>+8BHbJyZ+;yH%9i|x<FZ$0;mH4obNui3Y*_<bVf+K;iNs@%XnHM>6O$n}~rV*SQCa|7pt@!DfN*EaPL`LnlIyA`?j_gf#Ra`W@NY-PS9FGrR8KTF@qpNE`pP5+qZhaz}xohP2NJ;iw_<yyv#!}eUiZ?yP4y%a8f2bMVNjY&Pk{+4nR=anAYlIQ+uFNyKSgq5pu?W{N_<y>EWO6*rDH*h|iaywa@#eJW4=Kh>4KL2v=t=@aRDtGmnovq5XX%}*o`2)}J`8VYIc3dUqzna@IpIUfBF`w0)xvN%OsVX-@zdx+XO?+PHQm$><ExvEa`NUWFJjl7xeg1lTuI)<1dJA2n%C!eB@pY@!aJHjIr(~;gZAEadGQZY*rz$u5njhQqKz|-A%vR=8w&bXCf3=A_Rk=4hRXmp#U3qS_86oB&?f7a{uD{TL&yV)FRG+&xTa{~Hl;o&#J!QyFWqx)B?~idhUgS@W7wxaxuv(S-8$2VPmz2Bayqm4cy;aZWsB+JYo;y{!QTV>-&-+ad@%~z$*Te8TOUnJJb;RdL&nTXII<FG-#-u#n{>Iikx4sW}msMTG+aK1J=iazUVn6rFQRc?o4jcIOQmzlKldZ~K?FQs3^E$`#RJkXrw)p<EubmiI)B(}H8=uQfJ2=K=W;7JvC#FR^$5k(L3}46YPCPgItrPd%F+iMq$gSTs=JuW<*F~;}%@_9#O<2sY&+P1&XFa-sn1AGY<18`%t)`UP^FaG^$0~Dee@FiLsbzI`+*dmpB7T3#`HhWY{-xZ!xj^je70%qdsTZG5{caa=-|ZiWcAEAT_x-htV}AU<#=PfN<*D^P<oN*IF%RBMznBN)R{Q$maPd2Ppvd(*vqkQU7wc-Ev);S)K&~n`M!c2p$nkv5=|x-YxqtaAF|LQdR_1!`m3gY%NPdE^A5*%ozA(Iq*N=;J%%|tAtE*JGzjN>gRj%!6ovo}t(Ir=v8{;a(zL47~za!4!Hr>VgPu?c-=(c=)>Qe4M*Kw69_uRi^gEEgevqhD=_RP#xwx5w9=2Py^xNiBX+}sdps&c(fFrR1hN}Th2bL01{lpFY7s`u*QI0uXq*^At^Ts!X-{l7bRl`<drqIh0XuC)uvR^?{1q+C_*|DiBXm3#f-_uhZBQ|>lZx&B;5p*!C3R~gSoncu}%*ECX9Elf*Ju>DDfLV8)Q{*%n`C;zKI$+U@T_y7J$W+>}J3e)otaZiYN9Mfi|vrL)rGvG6LKNFq;UX5!O!85^`s96Lb3VxAk7}E<7@oQl6zd^*WGkwJLIa3z=OYoO?KMVdEcnz*u49@~*p=L3B7`QLfaHc*GaVpbVrY%hG!M$KF-hU519Ndp-1k>M{vYE~?t%QFKCjSR`C3qyf7q}PN7zrN%UWay<z*mA-;{7G?5#ZiT$xQJO@vC6+=OE&-O#fo~jA;e@B={uWUjcs=yb9O63ts_Vftq*W$>8}+3z#Ou-vmzvPlQhbPXtfU#H$rk5JVgd?+gwGcY${WlMeuQ0S|<TUxvQ~ei=L%J_tM*JQ_X<JR1B4d;)j^`cM2c(-@|1@FZ|IaCeA!2z&;32zWX~JQE_G!*m*60-ph%fwoHEW5CZc{gtUc{9*7srgxZrgNT2J-obrNgXci+*!n{}3qB7#3p^Vlej6g53;zu~7krT^jVYFi&fw<gYa~P*1rfJ}h@&Cm7`P6O0k?;U+d#xmK*TK|;-+vnxGC5L5jTK{YcoYKHNpHo3=V}q0w%8q4h2_+*8!712qv!%Cch6%UIk2E6-@pBn7k&qGB^ZY8(bUx4}pj)!DGR+@95PTUJ2Y8+!Y=R?g}0N5x)cx4}yqC!PCIx26z;B0z_<`6~xwgLOdTLUdZ$*{1Ds#9|EVt)4*vMb2>Z`O#T))9c;Bjd=VnH)-$oS=831l6T#EKuP{9Y*WroaMD&B0&I&pg;xw_RsNE^>Y2azNehNhFvE9Q1e+KLUC&1&taky6kd^$J*JQY3@Og;-d3;ml4p8}qO`w`b*YOK+JX%Qm62O_=~BCZAz*Mf*2f`}VJ#NiO}V-WG<5b<9i;wK^E4iIrCh`1v}+zujc4H375h?_ygk3z(aAmX|ZaTvS?xCc{zrW5e-;9E@eVfYpNlqUEH(>F}F;Xy%ye`E?~d;xx56HI=TDF-6n2PR(+5f^~TmqNtbz~ujgh;zZ@A3(%=z~oyYVjtLtzJCM$1pEocLn6M4%m==W_kYBAiGxvp72^&DSKt~S*oQt;z;nU57)u4b09=4Msem5^Q~MQ|*9zps-!ole`UzesNbnt|5XRra{hDC%GNv66@c}UThY)cgn0z@z{4tn(8AQAbOuhjkHo@fEA>#eu{pkB8a4EPH;~^1WL$)9M6W+gr@e+ri{u;&|0=|xG_JjAM57*(lz`HP(>+nKwA?D;dybMh3U&p*&M^1d0=`z#L@XA4ge_;w`{2lxYO)&W}rkxP+K`{9yh<GoU{C$XcH<&yFBF+bsZ-j`8z~p%laWS|UeZLGY2bW_!B;p&$iorkQ{a-L%;!xDzz_>%fH*rldxEOu73C{=TV=On}d%=4#CpY28z|{Ut%<E0$#K)O_V7d#h5+wLnrh6D)VIJQjC^)RrpZyoff4>a+(ct(Glk%0$pYir9m$0@1KkDOqRHpA}?8inh|KcA`-%7PV0N*9Kxc'

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
