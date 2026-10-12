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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_011.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_011.stl', 'source_sha256': 'bc19b46c3bc5363c82a3db48053420124f02d7667152f9f1ded89149202c567d', 'input_faces': 484, 'input_vertices': 368, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.11336752027273178, -0.2863118052482605, -0.3031321167945862], [0.18888671696186066, -0.013757556676864624, 0.4700031578540802]]}
GEOMETRY_BASE85 = 'c$}r133N?Y+sDt%Q1d)%aVUu)h$#}|5mO{+%ri$LF~#r(RTQU)nHUqZYbZsl=Ao!#hzvvqZ9i1f`{GqYTc6fgecN~Mv;RBJKK8fPx4!SL^{oHz{_j4|+56eUy*-V{2ydUV3VT&ou7*_lUU{D&iK0qb<)i4h$)ls9Cp8#9ahgjhY5CR*y1ILxZjl3A%16o!{}IuXqT>8psQ#^Dg8c(j|CkAJljDYuA2uOwL^Sm~4Ue4^P5eothEI$p?`t;+3Jy@4)Co{$s{hAVVbTSCx9^#=v@iGC?XgrJmD|?l8_^qg*nPL>-f4S#BR5p=d3){~mou5~>-(8?-SZ`auRI>M-R`Rir-l4xaIE0-{M^@5H;er_)=BX5`vc!yK9RLwmba6teto&<ADgw^?t9|>n18Cb+wvbyVt!H)mS1VO+v?BiwSuoaZRWQ7>e&K99(7cA=D)mu%JN^Q@3Qh6Ne+L#+wQx^<({(V(JoB2d~??~g0HmeY57WlO_pygm~M^N(^?gL<;?BvcHh`so3+=It@+Yl`3b&qCuy7ASGrvJ+Vao-W!1rRXP4;rSt9qf!&{|(?3FEc-}uI4e&=R8h4uDgo8=oDS6aUI`}tc|9jb0&?PnZf>$cW-*1pgJ*1k?A%kyV{R=2>ptbNudtNz;R?krE}DCRc^vwR~dFjw$r)nn_q^bMgsUvJv<CSv=P_qN&ds5?5c_J@M3`sklW-?ID4*uU92PdLo{qjiNk=n3I0&n-We=NB)lpQ@i`wby<vBGkvTGu`ra|6fiD<89fG`5`&X@33gIb=|b|T*1HFB+>4>;|`y+uUn<ZQHRggE%!a<zLWNKWj1Re_<UV)U%9s8q<w!Gt&a;n-(TF<!{V90w2IY#ch9S$ziDft-8W`6J!#(;+7nIi`M%)3Hp7egI5*VC--tfW4esk(ubi;*<J>c|&j~(1_qcCdN@f15{Z<`3_pXb6@URtjU%!yZ{CWXad+pjy(a#yN((Y?#8Z&=+!A({_y9A5=h9gOKUw>YP`Fn$`JnqwbS$`TnJ1+Qv^VvGgOJ{!Um{r!e*Y0QS+k7tgdZEQEf1Q=gpT5RA2h`VXMgKtUHFjSqUY_{_uCepV_p#`gtt<C^a+XW|p97ZKee=#w$1FcFZ@o1ybxyMNS@<sV7nZkt_vIlhPlsgYmpI7Q`HdHBpZ49${O;i!tnuReLYukE@{K~X*ghS(g|#1*z}h#NA$~7#|NNy@f}gO2`M-s;{qmxi=wG~@WN&Yz#xnm=1$GX{AGsy?4Jugob&q|(&Vidfgz;)KqgftTch>(KkF53V_D-<cyUR2Y>fm1dx8-{#l@!KnR@}wLd%oZ?`+6|lmsovXKR7C^pQ_tfo%fzSYF}^s{88_?1z&%$ll8Oz+N1V;VKnf`6MXCo?kiUp9TnE$kArdrpRYssMxUso_I;|n`%a$VW1n(gX>tFEu<sU($Q69P@8BB?J<P9M*YY)=@0ow@oZzb;A7tn4wO!1|xu<_sGEeYv?r~pBS}o?uy}|Zf)?~rw=eBWs0Q2#^pe`(%C;0eY;Jz8-Vm^M4sqweje5K?aw)<|cGi={YIU@L;A@|t6+rL(9|AWc;IbSs`^*NDkecti*m9sYAXf&DmTOMRe{hx29*?s-a{w%A`t;4frzEL7D#qMhtld@#@Rqu^peq_x|nePd4r`vt^@Euk=bJmJ1nXfP1kt*aV?all`opWTqIyETS?khRBGpzpi?3OL_m4DR{#--G+W{t=5AR|ZSYsYF|6zcH$>&w=C=N-(J`NpTiFWG(bz=Sked+s~iE3=EFN&5re*&p?0=M>p^x$hjWUc&E^te)I=*3&#2pDdd%?!Pr(eTH3>t_S$e_260e>VkAV54?Oqwm!M<T%Vq>(DSnOpYJ=?zq{hebHaUptA5TJ*VEignXj)b$JTAYCz&!|9TJu<<OvO7>+ts1Su$Tu?w%_6E7n-oYlVws%Y1#x{uIH_dz>Q858s(zSyASatpD71_Fp^RHQ8PVbJgx-t8ShM>%G$W{#Cp0dDMdKmw;%|Kk?ey7s|8`GVQ)zIfwZP<%Ra{*3&KD9H$HImDo~je`S>t^GsD(`}F1FefQK(m-*_^3hA;u>YVG=`Y`AE3+=V>2hwEy(MHuzla0%B_HnAL4%+3sRD0b#@J-ay+;D8W-B(Vsx)}-W4#|A2cbRQM9@I^p7IjGGYoBJi?Y@e7YHCU0zS>_^((Ln|@2ij4xQYzUkoiWTF+zLeZk*+tLziX9e63z{F@M!pDboD#o%zl5loVlo)+}(z@?SN+D)nc)w(^=+t6i1(+NqtF?Y<T;i20d8nKIw#n2>Jwjm0CZ`?>dfWyyR`z}Yn6zGH$|{YQpm$$aBf523x*?rEB=J@=jMJ&6}nW&Pp4vp?Fij1=j3;XB7`epWw4T2J`SdYb;vFA3|)yBy13^By|~CSAEI_!IJ29ja{<d^IwK<(>aj@Qp#oSUn>?5qu?X4f7BFA^4sG@hs1jIb!~yv8;XW4}$M*62tnlXfIn|K4>5RlC87%Q}^0^)At@b55pGhlle-$5<+_;<v7dJF?*lPH|i(v5&XXvNb_^wnO~bdMcPjT^*6@{AC&pV*lIiMzK(g(Q@%SO^Ub>th4vceOG{jMQ06P0<F^a<<?~o=-2s_zHjUY7_xb$l%DRIx-;9e9@+$?|yt^muJRtK8y|a*C!+J3L4Lm6I&;L`%Z(^OeH$FWe^OaU#3iWaSaz0Jgp8L-B+J)0;(*AJY(I2DI&NSJ0x$hjW{?(c^Sv|S$tfwbAE=@LH+;`5GIVdVkwjQ|eTo1~j@HE+a<Gypf84Eh3N!K%c=X%z*A7<anIG3EhbH8|MY-8VFb4zB(eDj?nSETJ7`;_}{odf*)aaqj_nQ#8N^@`MYo*VF;=Z5>;_R{`y-`W5C_KyB@|E+UoQ=q(_@OeGezGGQGkE`q)!+Fbn<$7u6<2>iSd&f(*?@DKj?MFOj=SH6uf^V+B%i2G#ohkSUS<Ii|EBO5TMLW?>$fM>YF#l9>p*{Z|F*-C8e0}sF=I_2I<k6lr7ru}3>)@^@eBb5gulFQP+Mb^e#kvc=&iA#WKl%H@Q3vg5p)`B_HC|`T3qMb|Z=(Ln&qa6GeO`Yh?7{(|J?d|ad~#6cn;(C<&F*_JFGiP^!hQMoh4He6kYAa9n)&J^(dXy9U$H|nU-SD!xUZHvgSB5g=YY&thT{LX@c!dG*SEJ6+8da6E%~(2fBi@={H{AI)J?~F;OA<7p71BaKFaTZ*DGvaf6+2S>gO&L+N)orNb~4kUok(bYKF|${C5fM`FW!3(=%kgmJ}@YjhV~jd47x%``N0Qv_IT;_D5g!o^)K=%u3Sw<ok~L7_*)V{~h7>2}rT#_t%~|GGD3SYx(NG>txA%Ght$y-PhODvi^JCz30npsUI}@lHFIEZ?^WQyC!@7<McgR-HSp$*Y;xLnHO_S=Bq_towxh$CEumW+H>F8UVFGCS=Jx!JNx5)nR{L~-hAINUia@+&&le^eP=yA?dO`pyiBa0YSq*6T$KCH=b~@<crKKm$MIa$>GS7K+;=_~<-YT|DEFPuKl9r=o^v{V{#=gx&gY!@zT<hO)923*^ZW03p2>aZbIbfZj^~q3-<jX}d@{eDj^~h0-#K3AbIAPsj^~X|pFeNpzVmrw{(5jcZ*=<3d3Qc<e9L#NE8%%#r0~}>FCX?_9#}z9XcSV)Dlx-te>y`=`r<18)0xpt|5txH(=@p0|MyR4#=8_{G>Hk&G2jW{anMoVap1Agk>Ii5Xy^!VH26d4aPWuVp->$>6g&tz1Uv}b7djB!7u*{<0Nfkg3)&w{wGX%#xE+FWduTs!dvHhSU~orpXXr3+XK)v26u1jG0vZF30C$7Ng1dn~fQ|=$0PX>u0PX?qiLr#*#u$ovQ0-u=PY2YGYA0JgJE7iG!))~r!~9SUx6M~L=96ky+x&LL{8R1jdb1uVkA+6M-mD+W<DfmkJuxoIK_nCs-r%Nq??s{+iFcsEVA`e$+EHx;ZbhO1i6Y<-ygyCSeNCdRi)jlN<1-5TOhX&$X}C{w5-p)^z%9Y8p&IxEx%QaC`a-plt$&TscdCuSG*597g~6@yo?d$#*Hdkb>*zRIVB9T`I|yS7LES>&dE?rXxSncr+r1lOe2p=-VD!@qHE)V`UbyxYuBX}t*R;miTS41`Tch^H!L9I~UV8@DpFzFb;PbZVds~bx1almW`UIm!g)w(0Fn=ddZ_4z%K1bpk=mjv<WH8kfFx50L)yrV28DOfJU=w;CLHQzr@+Ac2R0QR81m!CT%2%P8;B_Q6kVu4X0#n@rrs@V$-3F$*6-;$AnCeDw5_COuBX}l>Pf5&0P>zQ#0LOzDL6?9RftNv7ftP_3pliSh;1$rd;1%HI(AD7O;HA)&;HBV&(8b_|;Cayb;CbLVPy;*%JPY~>couj%bP9Mn_+#iK@W<e(&^Yi^@HFUT@HFrY=ttlg;Mvfb;F*}4*$B#;pz+{M;4RQa;4NS`bQyRV=EIGkybZbnybZh+x*WV5bFdXbc{6k&cr$n-bRKvf>b?;{c|CL%cs)1?IvqS6wN64%PJ~VcCxX{Or-7%TzUvT_H$Z2DXQPgk|BJ+TB)&&b{uX)-{4F>KnhnkYXOY-RVi$?BE~XV-jJM;nk}jsyqr8W36{7oyR&cR<e~TQuaXr<_F2+1JzYot}+Qs@o`%uZn#zS-MAW@#Y|4d<hDCJ__cJzh5FXv+S%(3;6_m}sxjEm*YM!!BspQyg;V!WTQO7ts59M@hFUyyju#k8vH4S$LERI9ldS0`MPL?DUoB)XF53GD{%3GNO30Njg2AGGZX=ATpT2kis)r8OZ@99#tNi;<vzi|zw1iTA$nia-m4n~-Qqq8@^B0Et%6HqfTvmbiwtok-#zB*s9;g2#XdLx+I-qAvZRJ;D9K1E9UZ14*<eF$mfL>_x(xL_ugF@Obno208{D10Dz+45r!++z$7kTmtth1CM@In#4OK3Mg-0l<`x<;-b*f;L^CZDEjD)oZh%c8E7c(7m8YSKn%fn2Z2XI$AU+KCqVxJ9*ApVpd)Q{7>PQKL|e-AUr_jy@PpO?`+;ji>w;;UYVfGm0M`N6h1LSUk6iB|C|4n&LTf|)z}3*M2DA#e2Dp~(`dX+-DCRR1H6M(*D{ZT1Y1F(7xDd2}@@5TDeFs_q+zxr^JkqtNU=Hca1@;D)fEEQ8#kG{_9;bVt541nH54az60GRIIiVEAqCBc=Tjlh+_^`Rl)`rzi!7U1UKU}$4-Ft`EqU2p?%WoU6Q)lxR5pVdTA4um!a2ZDp3Ex<wGX3!9DGjKy_BXC1-b!bI!b#QrTF>rZsS*Q=VEVvxh7hDcp0a_ef9Al$Q&%rJVJ0n|x!xeTe((|!3v@^IhI1KtBI1D@#8Veo@9t9l-9t9o^jRKDb4}*q-!_l{4=qG*O13`H>GzvT%91R@@js}l_#)3zHb?Ap+9UKYm42}eMgti2C1h<9O1Gfch&;YOo?xei=uIdEs0jBG=s`6%SQ|9ZRGT$SV`97k|_ZsEG2+BneluIEfSB5qK(>aY$-po7YCJ4$+5tQ2?A}~)~z{3y`w)v&Z*8t_A&@gaE)GHFIfi=`4650bybvT%6G&mab8VS|GbidF&M)y-QFyFtF>HcmArk~dYS3pqa`>Q(g{X*gqiN_?0kwdd6i4r7yNcfU)k@%Z@_L{`M5tLs+Uw~hMpFw{IKLbC(J^1~oJ^()g{{;OP_$Tlk1m%B{_>n{&iCpL{a4z@<=uPks;2Q|a*Gc?J;vtEj5tQ#k?}6`w??P{b?}9xf{vz=wi9et(!GD0CL!W}5gMUL%{%?iVozDT)Lg1p{f>2*@L9mZwz8bn%eQCWZH^BP?Bx(^p1g`F4@9RSSTx>1^T<qEa<f43(#1Xp2TukXTfw+cVTLW4hd<bo5+e6Bm`_LNJcCp$~eII;~#9_K-T}<n^7}q0F-^JQe^#?~rxV*}G|4;u^_07wmKLmt-xaz!8d`xe@vJJ_V|Ij`%!k7LIAwNF6tRH!M=r^VEAD$t&Zv'

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
