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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_012.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_012.stl', 'source_sha256': 'd86b0e2558e32c6ef2e7061ea1afc8640a1657e0caf8aba500423fd425ba4f92', 'input_faces': 518, 'input_vertices': 333, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13048268854618073, -0.1735791563987732, -0.1860804259777069], [-0.07798965275287628, -0.04760351777076721, -0.0729423314332962]]}
GEOMETRY_BASE85 = 'c$}r133OCN+J<ivcG(FbhOH4o03#S85Lqw#D&}WVcA6zDE+9!pSro52fQpC?ipwbUILIa-Lw2&zEa?Vu5ETX449d^A4bA|fh{|;JeX8eHap#;l|Ia!1yidLTRi(P>tK0Wh9ny!zRE{<5e=UtwYYN5|wlEBF)iPp@hchy>=S<JY>M-}Ag&w0`#25dht{ySwuJmyp<6&cQ(u|C(>6uC0yh%M~rX?kNlV;A#%+8!TcgnoX85zPKIQ4<7jIf_Id+I|O;d0y5)YN2eYP)3bW8VMcznbALcsJz)c8k9Jsr^==6)$A%-|h70ez)1_8*~4x#QU?Gl)L$6?L+$%pLTAD$CvSexD~E{*L-xb;#>DNEO+zG_8&*u@wdoS`<YN$?&iz(b>BOyo!XA<zupeMj5n7~Q^#RkopLwdYI{5q?`uEW_EVG9ao#pu{a)6#ayQ@d+!<-d`e1<4j#*s2+|Bm|PuqX@<<4q<TCFd4^SzV%+U?)l(e`(*+pf&Zi6qzln-dZvzICi?F!K2)!wVyN>K3*A0V9KMzQ4yydlg@fvmP(!h4{cPUZtOb)1GoS-&lXnp05@OO8>3Dy;|<-|8{-9o9}z-ylXq&*YC3P-``jn2XjY8k((d5npzO?+j`V_|7-W4n{VZAiG1IRHQ(=6zVCC-mb>{CmnTH}Q*rX_Ze_k6Twd<x2O3VX*W>9^yPf^C?#|lf<_8iI^CRWYkL_0Gw?T)Xn{Ul4jP&2zrrh=)o3hE7Ki>NbZ2$1;{m%T6zV&Q>)$h1fX~+BJ#mMIsw{KLwmp83h(9QP`IcVow_FCodT0ajia`Vl1(+ixw?2jHVeHrhqGEW%?^PW$FZodE4`g;{$=7SzD^PhM#G+UW>|GMfyH{bik=}5fw%rs@(%&rgG`M+Y4GCs!H%0V~3!hhBtx0Pene8|7Q*wxQT&Wn@}k5=cmb@yFvzPW62zSED+yA~fEXX5>@bymj5=PwMp`R3W%?EY_Ppp3t<d_&O95B%KQUU%7FmnnJM;f#I%?EF=kl2;>M47&Md>KMD7v@>PS?;BX1Q0(TLagXOYeffQ5y!Sv(nR9-P_(y_neqheL$lvuJ+N|^^aC2tR&99i1ZRcU_4Q0-GG}{g=ar2G7BXc9|+;U%;GM@F!kegpIf5RTdXI^fIm(K&l8yyEJ<L^6U+WpGxrHq@k@=URtZ#FH?b^6iuOT52RPqjZ2n}^)|K;nT&e|#k^mG9--S0m)=mz}cvKiH#;v+w<X1l@cq?}tcyMcnaHWnI7WVbIO@eiLiw^Y{-+l{~z9DCp*!Pbb)Uc;fw1Wgfq}TH@;OU6&L2-akB1>KuRbf}Q8qf<>juIFDXZ;_AmG<U0N6`X%0|-KW$!Zsw&`AvfQ8{+>OGFW0pmFMl_Q_a1Ml_yOy_kehFK9<|56d0pl28goX4-26cNYP&xhe=2c~voWe`$j$e6csCMn{_|vsa~{ogjY4j|^~Djp{Y#%J?F9DJ3Ay>+z%jf3Sw~Bp^Jt|lDRuJ$DG51t9==hc%vZZBC2qda=Pe~ZI*(d>^uA5J&$wQ!j9Z^QAvfPJ6Za^-oG(3I&KL1!@Pg{6zZP=yD^l)?#0L(ZQ~&NbE9B+}+Rn7&SAJHktkan3AvfP#@|4}5)$bK6^LV6J$j$ftWuu*+u?LiP0vGN4(S2jpcKiN$G+3<6<LgIC-F&0&!JT&AZYg%oW8iS_Qa9f`IWEWPM}K#;_~^XL_-~im{?BuEM11*shab&ze1F=zyPW+r>wj13>W|yH)9FY1Up}_f%{R`OIZ8XS|5|)BKlOO}Z@e;8>1T8vR}2ri`Tr^2yz<%}#g}=t_`{H!FYjZzFYjZzUs0uz>dW<_w=eIL-)wUAeXsO%ZRdveWgh-EKji9fAK>Z-KK8q|<9{k!_4$1<Lf7r*nT9z<Zh5QwG7qJ%=dJF`c;lrVMb5wL8+Iw^=9^tE+4rSMYl_^~o$kwZCw+Zg>%Lsqfwg}qQu2-ahVIMzM&QfeEA2$@OPVk5OWxTFik$f)?|Zs0?|bGu^NO7L5WTNzzPzt`=TA}F;l8c=^1dDQwfns8%Xq8Z-a=*G`Q6cd`MV>1{dY?DWxRQ7X`yr8{R<8U-F%})yuIFkeWuVk@A7w6_vP=bZ^`mPB_H@5*M0drZdy+kI_Ew5oS^ygIl+1_Lup4ohv>e14)Kq?yHJ@Io^y0xKIa6+buU!ri{~iam(Ni~VpFA^=yRIpN1yAYuRqsmzKpkuz9>-gK|X)#zI^_~*PlOc@QF8joGft8yKnVqd*0W)SfH$To}X{<d44vIuPji;Up}8}zI;CSk6%{coL~9;ulw@(-)c8WX-B?a=)Qcv@aFX>aE`xxf4RZu{l#~^g)*M<y-D}wdzSR|_blDl<MsD1-IwoQMogSKFZpjr#=%$jQofSUyjSYJe6Ni9+Iy((%Xn)>VZL*I<$JO2%lBgM%$$5>z4P9!`|`azFlTeVbAIJ}z3xZf>(i`!=lIM00o|AT3DVd16Ldcs|4X*gPr1LL`|`QYTbh;coEKwMb$h?`&@gpg*l*E&x!+>Gnxu@s+|SW{xu0WAudaOG=zfvrNB5WT^?jtk`pU{Y%6+XHeD<}x=M7~X<i45iNB7OXx|Zi0A8Y7B``qEa%X!LrXCF`Z<vw0T@`XI-xXFD&-Ix1>QD56v)O{Iml$GTv>s{`1YJPNI6kp%}^qU2F&T)|YvAQq!V|`UOD(%btUTfr1<$Fc<nKfVTGn=EWJm-ALeQe#A``E@ki<SP!eRAEG`{dS%xyroAeR$oM`|#eD6V>r&pI`UoKEE%eqtZ`#j-dPU9KoB~Ug@Vi*SNvwTtoNexrXk`a}8fw6ZQLY&Z7JBoW)lZug(|eIJz&-aiYF<?xXuM-do&I83&mszQ<~-^T_#vZ}0V7WnS<D125$&`NO%G?#pvA-$x(iI@_1$Zn`he-2%t<<tp>ext{LJbG<;*{9L#GTS>1f{gLO4x-ZWe%}$FHU!G&?e)RlK^P}gR($~&IbzjC;ESRN!FV1asU!L1ql?N$)^nCW^#%ljLN7j9LjvV#1b7$R`@n*{(b6m$k`p*8OE2sXO56pk#K)hjytA-J4%$({t@)xG~C)NGPf6g8M)scVal(hfvk^iJ{AI5~Q2hllje)!rIzTQWVz<&*2ABL|2v>3iCeDw)mlh85nU&7aR+S^WBg1-n~=V|XeZ3#BRS9{uPPg{a7g|BPWyG9+ssgWVK>$Rkg;L4uxE4Ih3C-fR^+#bH-sTWTj!Q1HHO7ul|CA<)Q3|<IlpmX31cmz5I9s%Eh_JQw!y=Z&b3pYet!VTeiXgpjGjzw>QW8qflt#B*2GujvK4Bw631K$nLMDK%V!i&%)@FMtm^bhd!@DB7{cn7>2Erxf)pP(PYpTOUs=izVQ7>}*j;23hC2`X};376nx^cFZ7z7xF_z7y_&-U0W3)6n*C8r%+T3Ack2&^mAeTnYWzu(=ZawPEZ3!e7Hj(IfCtxD4F|m%-c6?XZ}aXPGyl55pqQe`nb1K<G2D_`Cn4Z$hilM=_7@(B3<=C0MMBskAqhwieRQ<Ft32Hos=x_mLO-XiKnIM?+|D2yJEXz4p@HUfMcJo_t1opV5|JvF_T?UK`pP!B}jey)Cp=MqXW{y^FLZxIS%p;Wm^-zE$_w^@Lue4Y7W!5nqiuUh=XHdD@1$g2lS7O1-Mo5!{{J6?xj7I-*?Nu<M9*U!6LlEb?{$@dKzMSlkC15Z{10f(Mf8BCiKhN0gHcyN<X|BvD6{`x7hjy+3tCS=={<5<iqWf<^v!BfcAT1dIF0G{depjXHu8Su<jNBvMC|7m=$o(P{8Xa&;TJ1+K?>u8h`&HxsiQeFk0*XQ97?v)~EnRCog1104eQfSaOi;HGdbv_4!5u8dZLE5jbND(r!)pw;0jaBZ{!TpMnNCc(|%p6F1xCp;0I22X^u(TCw|_-XW6_-S}6`VPDm4x#(t5PTZ_3_cD2h+c$$gyUFqVjabC3GRfpfjhzd(C%<Qcqlpm9tsaf2g1YQA!vVi2;3L#2KR+i&_p-|ZiH5Y8^Ko$Tg83y3YXwh=yCWI97OlRL3lH|1%5PqEeKyPpwGdp!q<xMwHSQ_t`hFU-@^I}{H<Y^U!d-KbR)c&y0g&fu&5*IeuRDsucvM)x(A*`-BIW;_#^6;paHm)x*wy*;8E1=g?4~TsQVVW0sfe}U!mW@y{Ow3Z3K(Ye<en6RgYb6OH6aL4*V-I4Lr6shno}A7_A96Af`3i6>dyS3$!lWnwSn~FSrFU?a(;512LUZ6K+RLZ?q%anV8$qo^WqsMx(>w+lXm}c7es`vxyNrgK{fk>Z8rz*~C1GE`Z-+?pC2I;Mc;}>*4E9=%3-G#Jr7efae=_zAi;qz~jij`RF5XH}Yv5Ivq|RKf0mA;2PvX0@?wt#C+F48^H$iS_!QK$1r~eS`)sBd5S^n!cCZuo6tD8JLBF2?Ff%&e7mE=;Y`MSJURnjX4vaL6I}prGVJxd41EqRH|+Jf3Ec>vH0<?Oj_!efFzj`85<LdTvVO$pLcb&ScGgKOS{3fYdbk~J4i6^p`=DLnVdVE<v==;xJRXLcaBuQ;5ZV*&NDlW#yTA=S_WiUY+6=yI*!RbV+-s{4d&02qcbCy`;r)hv|2lzw3X7cHz~>wIOtAP(5zkhY_?=0lEPfl7Q%~qp2WL?hIv*DO6~77f>3bE*B4z?{LdQ9{2W6q%9Nd($&;$q9qAawAgDX=OTFJp4%0dkXSD`F4#=*5I3%$v~%_s|P;^3Z?g?4xFM9M<PJ2;!N&`bwEO<CwN2XCb;bd!Tal!cZ%_%vmqCmsAFWuZSfIF9ua$C{AbiE<~_gyepd`>`e@52ZYmH6eL8<>9Oe$wMd)VNFQxOSvy=LUIb_6xM{~MwA<|CM1hzqlV~Z2cM!W^n`<hl!fkh@Mg+F--c7eZ8Z&FNoZrZfB3Wi314H;DR2@oEzlb9SYjSP=fN$AsfGS#*!%!77WyRo$ME%L_*#v=4A-LWPlm03hb`*9gsy>CQ}=Q73HT@Keu<ueU!v|C=vw%3>fVpeg}<ckVe|m}26c<j9Qc0f-iuC#4^y`g-3b>__XG4Gd@ptTq3LiTb^nOI34cJ{bLi)AKk6o<1K@MSTtzRy$;7lqyTDh8sqL}#I^3F=o6!_ld?sSNXibmJHxrYHc7?@fBBm`G4<{0H8#)kfOH3--6c#xnZkB&Xzi0kM&itM^7y2qJa^@B0T<BA<sPjE@F0=w(L*2EgAAW+mbJ2(3Gt@nRz6Y<RZVs9U&!z5U)CV7+?oKop&Y|u>^bkCmy6Nahcqet=MAyLwsrxy47EY(`0CW)iIWZT|f4~EX>4K)g7l^rzddQ0|#H65|;OoSQTo8H_oI*@j^iH@YG4bfla93gmqJ!b|VV+8{G5_hmKK}ck75Nc%{zpi?rh0thta&BeR`f6>eOMK-&k_DHuM~NZxGKJ_@h_}tgvS'

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
