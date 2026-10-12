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

PART_NAME = 'part_022'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_022.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_022.stl', 'source_sha256': '8f803e216e9bc19982cc8cc2e7b00c999720cbf2bb2d9a285ea8b689d0641d9f', 'input_faces': 794, 'input_vertices': 512, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49997398257255554, -0.3070014417171478, -0.19791527092456818], [0.18748900294303894, 0.2797674536705017, 0.19791148602962494]]}
GEOMETRY_BASE85 = 'c$}r23D`~L+Q-)`LW2fU$*HXg4Mc>5ZAhF>h0t(@wqq(z$W$F-H_&(t2`SZXHiyXY(!1ZuOQ{s6l(0_&D&(L-;(MOGe)saMd#|qRyT0%3y08C#{qO&MuV+p7+WW1yPS+n-zMAL%)bbYgd$vLH3eU4~l2^?e-h1%SyL$E>Qg6VZ`}4e0v%38eoOENi8#>*V=MDEp)b7=LNYBBwua4Eerccw_m&I!L88~?8;2s0+7&y3BZ>zWO@sA<BjXvbg9)o(D?K+JcG`uW!W!=kS55)eDKPQ+aWS%~{wZJYZebYx4<BeLU3miRxp6=P_U008<JorJBKZc&c?@c<A)xB9`O0)ZEHl`>_Pc*r=Fr>d(za-L+F8=tw<-Xo?=qK5A4q8#%Dnd^TZC8@jpI#6;-c*x(zYn?`m)2#SUW=o}A)WPzo*XnStEV$-KF(r=AB&>&Sh>C-J>KrEte$Gzzc^C=d`F?Hdq0i#^|kL8N9t`JD-7>9p4Bra>2=0gPq%RYt%uh|`9;_MSlPSlqSh1WYCWkD<JLtTZ=kE=O>7#vF6w-W9-PmKJwn$v)@M|Ks|WY3(u4c3>2aYx!TpAwnAkP)c@bSdFQV(`MRfhVh_0U(t;_u%=<0dVdf*?-`gtx=oKLNLoKMm9^QCopzJfkqogCdCUH1>}!^)4BMCqv`Yty0i$bG2%qKiNF$<?9bN^-yD=-h9C&N_4aqAR~Vcd{O>>-ETUq5Z-0BL0a@L-$*<@tTk>_m$RzdDZ;n;*c)$3O#e`C86WWT(`L>N{^Kd59#sE^|R~rI&6;A<KmxCE3|&^>P;bC)_+Wo`R76I^H%4ThIF}~(UZ4V53Mu4t$A^jo~Tu$$kk<?3FQ|(i9a);YH0n5tC|$Lx~yO8a{e>TM-+#2)-QT`><QufkolRTGd}}e?nCVtUHRobBKMot<$e=g=CJk$^I7iCt$VkGp6ksI6-Vir1|Ju?x}4{j@(1@-L*Jj6klEs%|5%fkLb{y)WBS%Dq4R&u*To@S&Odr)z}hYDc~0}b)4Ip|F3>ry9Dgw1!v5gB&-v84oKMk%_nPvH9{9%>hu70_R&kV`D4kj8>T;el${*bSfqzEm{CiEm3+ci0tMuSK)#CD!kS@<Jdh(_Tk?YsGtY37!eyz*;y}KWayuMnO>lNtg`f6SK_4U=dTrbh}_0@Xtz8l{=bp8{~hZRTZsiw7xTs@de${&2b4g9^by3AXzb$+R<2k()Vy-PxVd5>tn==jrzdqmC$t;>86UC#%t%X~=R+A(w;gL$ZRnTMk5`Kfi~&zYY}59TL&&iqt*a6gP`5!$c3zqBszFVXe;OY8FfN_|*2e4cr~YhB*&qU-m&*5&=49(Q5rK1?@l9@6E06FoKVg3$dIYdN|kq;vm>o~&FWd>!Tcg4X5xg6Qh=TaK>$`tzIC<$8&(Kfh`H*z<mLv%60DJgjy3JRIoi^Rw2qUw?kqx?Yd|{H*oh{oX&HKH=}PT9@x%qU-OoIl6p)M%UkGb9A1^WBUz%pVhj2KMne*@3UIhe*JwmM_237-)D1lb-eoftk&gxCjK>Tv-^An^IYk{JV(!&|4P^XocWKQGylb}=fC*X{EzpVwkf;6P8WaB%5MKU!~Z>u(!Jk?m4@^#`=b5m;`h+gZPu09?F4?U$CO{MN9(%3UXRwrAN#st<a)FoQ+~Z3txNyZZJR%f>aX>f^6UOum;RZJ!z24^J*ND+zt)5EGrDV5Pki_K`fR^zkCqiUdK^8~Y<7{Wr?(&SKaX|jwkAr~{>;~H{Q02zr_s~OpZIF3KOa>8IJ)?gqmK8F>#L<9zvxMH@h3(d{WR)$Mc2nGx;|d5Yrj6;z^{%sSdTj1U_I)1y$AaHeU_K4&2D$}{i3JPGtz%#J%2s<tv+!5qNmZ1`D^<7&9A8Zz8*stf9(GJ4O!pYeb=~t(K8EuUHqB*p3CaVMHSw2{h}w(#h<!wR925I+8XLFx`!@)Z|GS6^V$3st3&4pJ&vyZnR%1SqWo!e@u!FMrcZ-Vf6-&;!SN1gw=T*ry7s3AT(B-`{i5sji>}u%x?X>5L-(~&=TmfjKGW;ZT^n`1MAz3Vwtma|k@o|-z8?}phG%s>-?T3CO>{lqv>wdoduF~D)nDr|<<FVVN)P7q+8S%3o)^*e^O9Km^Xkaw5k2R5e1GKXsOMdD{k*4FclGCuns1`(`6jxaZ(7%WZ~N3wqWWjHO^x*H`4+54&9~I*_E}xebJ6uYkCn|@6?MF#=e)nrbKYM{*M5DxqU+-g)}!BFvL1E3@teCAM%|xUm-|!noX>Ac5AOfYkESE<f2GHiKj;2ey7W(exOz@hf33%qU-#E~u>Mug%#2*W(qqb>vwo#Z|MdCGU(V|L%R+vwi$8JtPcLS#>ls&t=a15Z&sT%yJ)Yfe{NTsgZTUQ@^vvO~KfQQ+q+fLLd;Pml%<4rih5T9<f9CI_r)KlFE?S(u|Hk>>3q+6If<Eol&QZEo@L6ZKPog{ek)9<Xy=#p{+2=s@Pu`6Fe7L{pnHAyw=`QHM`TbLax4#gz-#}OU6<zOF>#|?b^?uXnnOnl=O>|G4H?7Ng6FsihALwfR>EBtu)@A)(mF|nPIAfCk{_OifI#R!PZHcR=UOTuZ${*<X<LGJnWU8$7zgH?f&F?EjPrUB;(SFgzpRRe!%Ito2oa@i+*0ol-dJH|?=<$%>+dk!!D1T;~uZur^-uQRj{^@qp%3NLgh@N=5Z`$=IuUod-)x|G*Y*K03U8mRj+wAx8RL#>0v*%OKC8Y;*PjvM?SL@oZ=Zw~64v4PjjMjs>^h~Wn_dIwVD*Ep=^x$|~om1-Sa(=|0dZvG<Pr7wm|9v@mWk^r9nUvL2lRsDbc>ldS`P<Nb<1I`5-&0OGrzlEKOsQQI)h9WnZBf*I6H_M@MXfV4b#q9U;}TsTZ)WP&(0b(jWS(ta9C@Ein^qikzlpBzx5V^iB~kaY==y$6z0j>R>iH5~KVPEj=S%dQ=WBAI?`IBpFE#d`A9R@~q9@R0Zp5x??EiZfbeRvLr|QpI<@T3(CAywt8FW3DM9-N&m;dPduUX)KPaoU1C`$Ln3@>!`BzpXp*4gVF_&dFpozKaN^$T2o3O!za^2$)3n|wX9Ve-mW5qf-M{Q_6_wk`4B^SaLtUr#RQeWCR93%rk{&kw$y(EHtg-m}?!rSSSi*ZcK;@%7}2@P0*4KOf$2@}RHh>=!-#nL6H6d%c{^KN`L+qNmk$@v7qg*}pCseZ6)MFO1ZG3HyUSyTX3mKlRGJ+0Uci+&WKX@w&GD^Q-mt`DGz}rLQM0&M#{fp(ks%T^-UF-#I?(?@$=-|BkO`+O-PzFY)!*MXkd9OMN|Ar!d^V$D*gR{X5oL<Mv6SXWDLE71HnY_4tKbSB3iAMW4F0*0_4I-!oIP+w%Jg@%Kk>J3G|h8|>@p3ucG<C($!?yM_A?-SAvw|6%C5|43iY>5s1ad!tHTj66T+Ip=4LujibfvGh^rC*At1ROIz-<LmnRCa?8%eSOpD`ufJ(EzI7xF?D|iy1GB(9eh2m?oZJZ+@I<CEByWH`Kk0^exmE=F-MoVDt+`^MbDY5(nrr#r3Z5rJ!h_pU(Z#g2Xj^W=(#F>Jy(^k_nR|Ul^)Dh>7(bW(u27wee_&adRkpCJr8qqnYX`leKWt;=hdT;^D{^1{tR?AKeaCNGtkxi40JU=16|F}Kv(lK(AE4DUC+-zSMxLIqvmJeSMxLQtN9t|YJLWN)cg!|H9vzsYJLW~nx8=*H9rHtnxBDR&Cftr^E2q9=BMa-eg=LuKZE{ieg=Ki{1jc!&m3LdpL%|3Jv%=;h5mY>-0(XuUV4$|*{JMQ^ZN8~{&c~L_D3-KPZ#cL^uPMkg(l4!{eS;-p>3Y|3S*)L*c{%*gw0(8wt!nt9G}Ij;Vs#|8ypB9U}BJoR$yzm<XVEQ;De}b4aS|C)_7zME$K6m9s{Yjyu_T_RrWE=^Ra)P&-<D9hlx_p$1>07lCyRF$d};hkFP(yEN^IdBNJDFP2o*UG&6A}*cg5#ydl^KeigM%z-I7EOk8H79(V=3zKI4VE(I@#UkbkjybNBC+WKGv_z5OXGEoIQ6@H3|(@dNQo(w+`egb$Byb86afTzJfG3RK5iBG|e@Xt(qZel(7Z}@unC*TJ7r__E1eh$CM?BfO#e*`<g+k@@E4)DiJJZ|DP@Xzq4O#I8lt>EqOP9|<NaXr`(ejRu%*b#msHGeX(+N|$A6CZ->;2)Xz*u)y}efS#qYVbYyhtz%qehh!j?Bfj+TfnXG*G;^c=jY!fXSwb90evm5m37(cWMV2f4gQ&lf17v_oDQD`P6emK*WvpF{0u(H#PcTBf*ar;;CsgDFMI>r8>o@oboxz4pG2<>^xHta<r7T2Y_9|O1$>Q(O(rISufQk5Cx9=*S5vzN+ywvF#Cj9Yg3rM>n)uYjOW+Ie=fG#d7vLY`TMur8PsaBlxDo!5iO)?;0aFg&$o58RB$uLJ3VkxYHqvh+^_IVHVzY^-!B^q$nfQ|Ym*gy;Ztq1Cmx7JqZ<u(|L=&(+yfJtwSRXze-)rC-a2v0ixCFcu{wALKU_GZ-eLVHiFQLyH^mv2%*NGQQGy*Syzl5hAc$L$u9-eyWjp*|xJ>H~V`dUvXunYVJJdcA<I=l<pU8s4I8oQkU{|<kg{4nrdxa2y4!{AR+doS1po?v?@I2=BVd=IcEe5kXZVQ2|F!|@HLS5N$Q`!Vndcn|WO!JFZaIs55>HWbej_@1EG&G_y1bnr!ZXY!3fxd*2^`{|7K7#{b&eF8qk#M36O2iw9sf~~=}@Co>y0jI#H!rOvvoEnR9unqhfe3QYc@JaAC;2)hDiygo}!YAXK2u^}`z;i2jJA5LZG2o*Pzn$&dsd<zdyL~6v4?c$cJ>U?B_hY*sHAASe+k?Qt@O#ML1@?FNV73QS)1Ml<{RlV~ei!-Mz&|^DEZbwL`7<?Rxt?RWmJ_J4`HtZA4tMX9vG92&=9oAYtO8$VBHzS0;2+>sz*E6Lz~|wc11^Kxm`k0-Q{dLKoO+8j;irIAz?$$m_~wH7a2sz?XYn++^(>{{Vh#9d;3;4Y_*{H%fy?1%;duvK3b(lh^s`tMej5BNum=1c)qerJI{8J8ZxQ*o>0$8<cvX0H@GSTuY8QZS!>f^B==c_rUrY~+XTr~bR|BiV7gGB+xEOvq`T34-KKUi|uy{87O!(<wHTZmL7lTXSr;?xN_~wycMh}bUz|Z!=_vh)}vHNpAb@QpQyr~KMm-@57SKzZvylSEu*Z|%P-W0q7K8xDf;Hz+(Z)jo$I14_Ld;{=GcmwzqU_<x}YG*p@n@Rp^6De>8{AKc2g3aMq!W)8D!&B70?5xl7r&Ry$PXAj>{0nRjPdRljqdkSEJHGDpviv@_p91^9ZCzgz_k*{<C3hcqKfEusw}9Q@z1Y4F{3qPjjWE$0><gD%FR(X!1hsv^KJcz=_X5YkZQXbi-M|rW$#n(0!N*fO0{kbuDcfDaSKzkJy+6mpCD#;e27i^>@!&Z4WhO2+Q3<RJ|BLwy{WlX&fKS5zYT^zP<G}Io&L+B<xEZ_!-o-?B6J1TzHht@wr~p=kU+nq0@?ZtH_0+*<@pz}EBA$xq<>^z09(Aa<{6-To&;IW^d@K*IW#T64EuQT3Iv&sQ=qJ(VCVJdNz4W!7_TY8!0VW2TXbHB0OYS7FC43;Yt-zDv?b%L(55b=^@w|z@fp@?q*B<;E{CR5c0I!25*-nE+@In*CCLRPIhD$C9J_s+S_F?cL`1vL-@cbW(d2st{#tTgx2bP29fgV^6em=enz>DC2GI6en6F?7so{1Z%w|Jt{s~nzk=qJ$U2725;z4W!7cHp(}f0(%2#5G_Gxa3X%uYuo9Z42;3cssU7f}`NinwVzdFW_I{l4}S41wM`1zk=7oN3y*Fd>6jbg#CT;1K?=5<VJ!Izze7y4UU4ZV0$H40H0$nWT}a7z~A5*69-Mq01M%gn*+{(AEdSrEOlxM@f4!Zq0evh_>Fq$R|2<q82%r8GoAi3o!ks?Cj2*QOTiMSrW8*p`V9IUrpICGrC%Cu@c{f=d~==tbDi8wa4!5XwIyKMsVTuzf<BWz2k3EtddpYf+3&1pKe_MdXK?|1zf&jcS%K#OK3R{{EWon>eFc5o^?V0kN`8;y+e3aAJuEJUOKz#N&ZT(v<J(U!sacF?G5S*a?5D?m>MdVHey8KxN&dg|u(%8^xkb)87vb51Zx6ksW*MGk=!@vHhaP*Vw|qYN9gc4Y`Jd=vaV1=G^PP3h$FmdPPI^hrN<1sk=hJ5=J$6!W`5f}!IKFSlAEbvo?<<|$9A};KyzjubgI-eOKJWAMjy>-?=&^%(%O5iFh>3rKqu^G57|r5XxQ#I;5?~Lw#h!4Be}_Lp?HKS;_%IWLP4og2@C3EJz~1m)@IGK)xQ)@|E#3$3gXbP_2;9c~<Sh<`k2LXsi6r<S+{Os<7Kg)=cpd^DhTFK8yu~}=XPKyJ;(YL8_ys0vn>ZW%16*=vfoH?d#&Z@}6MjBDF92)9zcBBZEhfGJcfh|j@tuiH;8wWgz5qADH{tmL+yeiGp5KDs!DD9Mr<<q)R)^O$ai)n{U{$!}Vqh)!nbcMVPj_mn;;D)rqfd2uRHxqZ8Ya#)aUoa-ZsQ{I7SDm##d98bF8my@26!&~LVOoF$71=H=3Hb<Yy-cC+t}{;d5fFjKj8Tfn1OEwzXUVzZTPl>KfrB%r-`q?J@Bth{FfdUcflo>0c9WmrFIv%)2Z2oXBT>gK6~h~hkDC*<M|of3;)H$J`+EJyWo=B4gLt<N9`_fr&F^FkE~}mefH90FZGu1XZtXC2>zRiUrqc3?t@EiKll^;S8Dfxd!3qncx27{>2ru4hp4yw0NeJ1y~T2QKDUvV=jSaR#Cu$x@A(z4^g0M0aMpH!zUAm;@i_Pq>W@dS1g~hKvWcUfkH^6!XX`4W9l=uxUnOTBM_KC;XU#|GQ;A-c*q7zy*{%jwho8Z-Tmh^Mmt1+U0$k=sWw4S{QyGt}xjcQU(?jNl<+Du`nfMw!1mA9t!^B(QD!AlkgKxo)P`e5&a%xuLS%p5EK8NUWh<eLs;rj|a0=NF7)LJZqOKui88-A49GH3l#Q--GueHML=(Bla8me0et4Ll0B{$HuJSPYlkJa88LS89u$^-E1Lo?`TQ^f^k8qtr{^h2$-M5B~*EfwP_hCpQl)aMtrZzVGQJHST&AI_vqK9^X^{3;B1@EbfNyBcJc=H{Z!E1oPp)P+I`L<J1)3DL|Lw-c66))bAs|9L?fh_>bh5IQw1V<lX_7!1qy`4=#6V^6})O%W?0e$6o4xB>yg&#h>9nkbm3R@7qppIrujGM{1XV?>aS0@GL>Mywml0<*FU`d;iPYV?Xw@n-}^Y*y_sge=g=$zH52~|M6I->nqsblX>OLKlWdUEwI0R_5KG0n_>O'

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
