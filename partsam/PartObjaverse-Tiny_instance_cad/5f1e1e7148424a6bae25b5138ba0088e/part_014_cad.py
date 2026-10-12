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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_014.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_014.stl', 'source_sha256': '5ca36faba08bdff6ab552401ea9de0363b4f3e5d06d38a699b606c1edc6f0b0a', 'input_faces': 468, 'input_vertices': 324, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2707403004169464, -0.1254376918077469, -0.2613515853881836], [-0.146910160779953, -0.007073145359754562, -0.14295640587806702]]}
GEOMETRY_BASE85 = 'c$}r13z$#U-pAJ;qb8S`G`S4MAC<f0GSZm(qg1XFM_1{O870Iqj#P$SA(v2YAvC#kLCPpfVaK?RTNg>!e?_GusSc^v(OGN%K5Mu4Jn#EF@AJN%=l6WS`?J=6?X}l!ueFiWwQRXGC4cIwKl3|HPGl%$qM}Muqw_|N8ayyBzxe|r9*U?`kDEVMXZPsSJ?D;y8m%5_keio3aAbpPq7B*)y1GHrXoEq+M~)iV|ABjkkIc<8ymSAd`FWb>-`9Ucp1y9_s%7h@(N>L`Mhl|<$3GY8Dnt+Tes7CbrzEn((_72!G#Y<bcr5wc^PY~cxWj1lOpfqxGd!;L@7(3-G2w+>lGb|V%$%~_E9a1Kr$X{lFJGrDFTZ<Gc>G|ebspc9vfnFrKjrs|F7|%cZ|Ytz|GUDYZHiv^_}cjHAa^T_S{dXqc;Ul6B!BM5dxG3;+;&xv$KR$t>B*A+uI2~4`)we9-k=3uJ@W>ac=`tUTm0%hm$PAw*KURD;2YnUa;7JC2f4GV`N|-Vz7Vdb+VK6ZAh-3j+*who9qy0s339(3;PK~Z&p|gV_xP&?UV9cUf^XUMn#Z#SdCwb%yQfZj{iw>7*%jo@oD;8x_yXZ-NWlx9o?htnV|+gOYoGDTSBX<HuI6#yLpiT_>Aly=IGIg3Lys1D`udY4LGCO`Srg<6?&dCA?OoT%_Ui9GP5!B?ym~rY7fJaug(tdhTp{D+jMoma8Qgb3kv9&V#G|`{JXVyyI>_UX)4v~mDE<CMl9clp_dWHkJnxfjy>>`ArON*-yClf{^5L-p>e(gDYX|3#dR{rvvGB<Yy>i@Tj}?2@kA&OJy|C4;Ah+%2^U<aH<@5dCeWRl&r{w1KUiy6-y!*N%OO1!OHkAaqKOW$P!^uA-_M*r8CVTCl$c3LfG2i=Li|I1X`_K+`RzD;CwN2(rZ+M3tGEe(IEzjGTc6g+@tTU7E^tkFk{l_eleo6XlpQov*l0Rqin_l{{wg-beI&Rz2ATPWqHQYWYx^4CH{hlKAxogQ|9$)Z-%=e#!yM5C(dwlxJeL=1kzA_`oqbG&Ozxzt&`=v9t26^now3R_#cr2XX{cirjAh-D~j~)%z$GNTQjv%-7vApmT@(-WC#p7K+DhYD?yp~6Ir-a+*+*{s#6T5^bR;+&8OYfX@Ajnmp^Yeo|wk;*pFHZU`+k)Koi{*(;!V7P!?8-R#a(9rcx6h6Za<?d4A9dY?;vl#6u{<_fp2M9{B=c_U^E*QP_WU(Lu7-v4t4N)FAx?hF-G1;DIkIkNp4}1RAGTZ-<b`($S9iR!L7t2E2s~a~usp~Uw};DDJ$CO6amu&c?FpZ<)0^+H%$B=?yl}wHF9dnCop7h$`Zr|$#`Xqz?5!a$1-a9f{0Bx#{abI|6XfdfFUx~G+Ay47{Sw(7<Tk(M@heKz=k)lULGITFo~TKF#;r59z1J^^YNhzv3DUo*;r3Cdrk4b{Z6C{H*)eZi`}?SAvX64>3b*?x_jTDv6;8WG=7(L!D#<z)8zJ0ZCpXDD>E;Oc*U6s6((m2jtdr`btdsF9xZOw1mVH#Bp>X@YcIwIdy3lggPc=){Pxn&c{=Vob*%zrw)RTRYvrzU$@h{p*x_yt#TQBdgkA>U)hWfkgHxk9d?R(tmA@A|nGs5lrE_OuTcWwdsdB3<%$@?W5t+qcje;>`*7vgsQ!kw~kJ1;i;CjEZC>i*FD>L~NeIV;?szx#LX4RJev;qIqZL-&o9Tk4e`pC{ZO|05aCGlcu&YO~C{M1gRBe4fkl>L2S5XZ))-W!_nC$G_!?yUB0o*E=%rEcfRZ+|3G?;}keDo-6ZQc3zB`Q4-{S{o#cTt4Mp={ZbnHr7MKn{gU&~Ou1jOaDTsAb)4*1f4f*X`$n}<_Kne#!tH)fHCinDz2m~|eos~Z%_~Q3hui&C|N1gMU!{D`HO}XpYo-gg=Nk2#oNHneg!}vdEw9KrGmQG!^G+{0?>M>S=e*+_mh+A(S}fy*_pcf(`wGkb{f6a>g!}u4V>7k}xxasaN2i7Jy9d}OObh4t`DE(D{=sd){sC_H50<NcgzN9rlzoEb{{F%8Uc&8ojvZzH&{?>@ANV0>Taf$v0l4~Ok>t1gjg0mOg52M4z@tZn`}>E5oWJ1y{sA68vM5xa*z>YKwA|Lm^636j^{G0sILQ6_z~lQCh1(%d_L;F~7KPg1Ns@h|<^KK+u8zogE}phj-m~vlkoW0f;jt<*Po3(rp2T+wSH0KC{Qc=Rc^-JY$1HC>ajWFZ{&q9vWWOWNRV`EYA?wM%YK5#P<+n<E!kvnTWWSxcR@S}eg(sRFm-@VVr_8UpoJUh0m3>H;eR5tHLp>|6lINOxMBaCK!lUIDZ}j--Po$nV33tzCyyNk)EB6Gs`gY-lAXhiSGr9=hc2L^q2FmHYUE1eN3)%m~c;3-VWxXA9k?bF`sDB&wA$4V)bXviWtd{a?$+(I&rhR^y%)V%_tizX6e#5(^9S)z6`Cg57J9|v#`%5k4d6Oxp-d_2BGBDd~H>WK3z5WNOXN6@_&aY$Txh{HF-oN!K$@;mmmfW}89*?`DD$4rSq^6Xg_q*&*y3CbzpuTXo#%Wo%JIa13IyYU)IS}{q$Cgi%ea<X+(@&)QGZQ`TOiT~=`;xs<|MBVJaobtOtus75JZ@{>F7+6c9v+`J$oN$Eq=&|*(^|%->X#lGpRrsSpQ>GYc>ElEc~6l0;|K1xNDq&Py~(n#$e=#Ok4pYJZRI?Yo*wS^$@fV)mkN)jm6i9xwM8;tDyN6XdHqklevHBsU1gu+X3BZQO(uWA5}A*yUyyYy3EuaVv}abX>?eP(5gI@4`u5WP|Edux$GN(yjL(xbLi0ua%zXK@MtGceVf}nxxZW2CA3sa>Gy7_U$9d9^GCntv|K5BlzhW6_x8xbJ|FZj^&Ac!EJzdrVyFNe1`vUH-&+x+Uh5PI3H=KXr{<>=UA@bYz+F{PcaR0pqch^!Md*1v&&bgNR=S_IxS>g75q<V6WgWLC!&nJe<kCn)|)pA?D<?#XG`p0%0-x=h#{+6qr;r3A*U)~qw{&x&`tebGVuW&lbe#3IRudqCtRVx2D_8VEH^26PB;r@00Y#ZYKegK|mHa#>>RNe00eVu_{Nq>&n=<O$C$Jfexd1XTQ$zF0Un{tP&hh=3wbAEZtJ6||M6MR2>T-LeIYsmM*oc@w;@VFhpesP|V{<YkH@5AH0h5P%EvdkB_zYl@Ovcu)O<N02Z9WLK;r@U~#ABRhSS?>3v<v$nf2)46(gzsZ;+s-~eCfv5Odx(9@R^k49c}(`JmizMsuGWO_>zwPkEy(@;g~wJ4_s7q9#v9xpKXB*SQu#lVab>xmAD)<B5N@{)vJP18w;SA<7=B*WM%Dq#{e3&!9Z;&>PRTkJ-SFA=(73%&zDqds;P(5;PQIVO{qrL{HcGgE?wi7S?MC7DyyiU4c@1vQYd&vHe$KP8A#yG*Yy`L8mmZgMuFvf`8m|8MRJi><md*Du%kB3ucw&}t|9j3*&aH6&912&r94-#dYc-)ru1|hc9Gusxw#@6o8y_wX&FeqEl==SQL&c$a{Y_l@b=?EoLi2Qs%ty=pd20Df!u{{eud`mk{qM|{FDAczU$mEVf#v@D0<Pfxd0{Hwr5_gVkHfYyzbyC1Av`gN{C1o-k#mIQ{y2xLT;cwCa~<bRxPRV+$9sqKyX$3sS?-@V;nAFMecaQR?g(=KylHuM_<5b<hf0FnUuWR4^l-bW62A9U4)>SyrtA|e_tzhIeCx1qf1O}Ghx`2nkDl7UH8fwom3iTFJ73`O*M$4yf7f*(?vH=C8clxtTxqNueT4h#!w0Mzt-|HFb7Xypr&1sL-K>LrAM?5WZU%SC3-{NJnXDVX?h8NHgL>V_3H|N(tt;C#9Z^*&6Uiz~4eB5Gt8oL(AFKcUUyToL{lEIF@z$AF|9}5#yuPl(Jvt_$WAR3(2K-E}jnC)$QXL(23`ZB@=bGo^dIW4CdCYIJ(c1VC{H8XVjh{$beY7@yDrHVYN8qoZ+^Ohrd}|#|bhJk+;D_p%!}T0k1%5M>@`l2$;F%vF{Q=UZ!jmYw32BCPhv%a+@!cse316S<?({)@+S&L~Xb=1-{226a_%Zl#=<WDAI?T{)MO23wZKLCUbSZv`jv-tRff-*<nSbgbWf?7xH++DO3FzZ^qm%HHxSoQJ!<#bN=@^W@h&Q@G$1uXO4&*CORD=y9e?_zdegbLr(2Dp;lsN$%hEJp1N$6mF8`|r7v=x2`?bQms9zTh+G_)0d3hg-w9fG(0F$KLJKaPH^Ls(V^o`%*7_yJsZjOaO_<66S_DyZp$DyXCW;<X}D{y6%{uxoTw*U_G+PClb%%+*52;nO2BMysP^@Yy<2b#x$7$!pY%^>lO;zD7jmN-8=Q-%dw09WkOBd5u1(#2d}W*VIv<B;DwP_$(c1q}RkhrX)<hnp_(`9=#afSI5ITdeKe;Xh)-W;vM{Gv=_b?zcs#`jw^MPL0jOB-lXGRv=CoO$E`Z1qmST?&ItHvTtC9Srt#Yd_cW^T*WtUM5qz$W<y<d^MYu;U<>kUEale724<v0mzcv0DbRb@F?}6wu_!-n|Agb_fX^R%bl`xZk5P1i|%kj+jl725~GXm{94ZRoNm$Zk`Y52aBR|a2+>%R1Xx$dXTYhS4xv=P3tjtg|8>ZqlonU2OfqB<JFQ}HHm6*O7LWoS*bGQKkTjc<xJCTen@%Te?1-Y!8?&|3If<WE5x;u})`6!c=e(F+5-F3jYw0W(?+Z+KN$KicYIqHciorQ8civ#b~QN+Hd%J9(x{NV9AJ&u5?6vfF8o%Sp5BZ?u7JFUxw+Pt8cP?4Ce7H-mMj5AH!5<9pMl-2?s99ex{qdl_k#^{1b0-y3#^k}=UAO~xC3i;}Tm$BkuoDH(GYkY-sQ_1Ad20Cu;MvDgPq#rLHD?na|{!@JV2RY|ifPG8p`&9ZJv#zZyJEHnQyG#y`->u#i*>%Z%mrK16Q4L(yxORihOtk2*&gEEYNlCo@>4e*n7<dL37+LQdYCFw0mGkyg=6K#pl(lHyKi8pzFMNgu$@z?M?HxR}@tK)O@M|2kcI~`x@n5W}r9m{lFODu!W!<)RvbsW?2oQ@lHJcWM_Z_;Br=IgkcF#ZJ{|3tq+=i?3kM#o~p=Iz9FYr^>Fb^MHegD%FK{k7R=cO;BA=Yr4BpU^pYa}F@)fi{HkW-s~+dJ3J3H~TNM4{JvlZ}yER(4*)QyxAw3{o+l8@r63RMZZQD;Qvd<52PD?8vk_QcWt@8jxgT5+Y;yx=+pR$`UUzu=|-31mj`~=h3n3Q@r!hPfqsuJ$5+*5p3!<qM8f#rl<2?kzu`}#U*Nx>4CDW;BZK-GJx$tm+DCPCB8;ztX5j1KYwIYFn(}JHjqgOhsze>?T8I2+sI&35jz-IKZOb-gU4b{6iMMSun=t+)YSK?~ZTy8gnxUC!d3*yMWk@d*$ZO~MEW-F7QIqdSu8qGyM^m%`S_a=nM-u5tfxLEISVkEC9cuD@$F=e2v|f(3L6a!k@D@5M5H_z_H_Y1d6k+^v)Z{zPwee+jG(=mV74UU+{GlY>sLgBE9J3b9Cyf6J{R96MzLL)0G9p?RHQe~dI?gLeKOe|z))aGn*37$zXk+v|zP{O@MkHND{>p3DsX2u4KcObyPh1<HtfM(vA659)I#Nha3FNiw+FZi;Q>e*zifiL9(s3o)8co4prXxanB#_sxgG&hGkD?~uQLc^uUF+58WoU%5o9OtHbfY$}T{jmH#($0eiT@g3S?6yR5p9ARZhXCntedS+o7b#;=DM8rjUuA;P{WPCDkAG+Bh=<KYmm9N^WNxHXhnW^m6CUJbF?$w@cRO5LKf^Q($k3y*ktl&pjY9a&@qzqk)%!Lx6Mg!PMY!ENP7r<0^beILH~iz!S_QS#jn!wrj9k}X1vk2@g`m)uhDn#hOgIAguaY7`YPV&8~8PpY4Wbtu~x@A^ew#6mvp?2Zp54XuaI|_jt_LahwjH4{S<HXFy7?f9r(==9edCZ@kV#xjedfEk8(`jLpt8o;iB8{Mz`XP7UNC+_sMJgL9R`GKBi8_f5f%%2e>wVFW1JGaBb?eJ<u=P>67i;<2AzgO**!qE_w*RPsauwD~X-3HT2aUqKGyqq7U99R#UH>u8}fnW&fxD%JtVD$E<Oo|JYUfm*LOc!Cz+7QGb2(&gq(DzNP5{bQy1xz1!^M)PDeu(440'

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
