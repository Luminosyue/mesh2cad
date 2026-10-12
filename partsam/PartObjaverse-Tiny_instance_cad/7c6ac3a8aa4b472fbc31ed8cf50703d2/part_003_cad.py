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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_003.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_003.stl', 'source_sha256': '0ea32d860fd951539ce4970819ac8946a10343c7ca0ee2e82b54b17f8c52d7e9', 'input_faces': 640, 'input_vertices': 399, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3053734600543976, 0.21582511067390442, -0.29323863983154297], [0.33104005455970764, 0.3104678988456726, 0.27260175347328186]]}
GEOMETRY_BASE85 = 'c$}r21$0zbyT4CxcPlzTan~XN2KOXb@G!w$g8Kj!C{pCZZE$y5icdlk0)ZqH`hAqz04;@5C{CfsWuNz%bZ`FuyVhOzX05%RCqH)fIdkMa`<ye2kk%<v<+9|bsC6OyUYgq_EK9XaRxWE?zlbq|`t%!JarnrI0ai9US3iC(3F_1~q-%gR&YE1RZ@<xfB1+Y9lnU%$t5kVMss1A(#zce<?=>Q#Z$Fhc3m-bV-@APD!0?g%-u+&>TJ7599o5Q|cT9EsFMl$;TLnkGxtANLbve598%5vU&T$R2+#9yj&ONn;oHO#iUORUUUU**7d5>{^_|DGVvDe~luAL|Si_fxit55s0_U~=yOJ0AJoqMN*#_GAX^|g$Xdc#FMcbCm#(>Zfeg3<qNA^G<ctrP9_+`B;fWp60s{2Fsc&mGO$+qt93)@Y;u;Bd)%j*iiDZ?#G?{^Tr4M!v0{P2bpIcJ2)OLh=G_WW3-wBe(W;5C*+Aa<`|4{N2eKm+arOER?@*bmM}({TE)kcv{P?VN+zgENXCG&mH4)*xSX|HtShE_c?3I_8MF`R?nT~!|dF%u|SNTdwcJ*bNA;jqm2CVUFrW_zeqiIw{B=}clWrSr;NP7WZ54@UB`|5#u7WXQsq2me6ADs?cDQx@R!DN7pJqgm+#54L&iAyKeTht(7642?n&K7`loNX!}z>kY_oIM9czw}kB_!<t6NH^p1Wo}kp2DY#3Fsacnf5)_mdTRa;=_wZj_X~XyMIz?r2%x&RuWbZa4OCa7R1$M$Ory=hoAKcJ4g+c)zjSRa5QUvo!A^W4X@7a@>?D{iU9}Zf%wI`MBK?J$Fxwmi{+J95crM&o9zH%gK|*`n-K3>wl-d*XW-+uhfB}lOm1r%U6<ma_v}@-R~5~VX?P%U9i%m{N}WlyA#UT$GNvf_$58}PVFW6jrB=-?p$`n&RrWGCFr^1NiqApaQrdwf}Z<aA$IOd(L3H4|C1|r?rgX_PS35N!E!tV=iOxVA22^jj>mn=?R@wm$=j~9*T)KsNjz=uw;0(kjtR0Ivd=!-K+BzZ=E-(@vocQ4-32#FJ-qkTIX!pXJSKJc&Re_QdWXfza_jb&dbRV@SUtC1|0s2Dz!}+oh0aR<8TVy<+zT)2d2+qY*Cj#E9d)zGzfTRa&r9D$#@SO{`rp5GM$et!G?w-GbZ@lLKeVHK-ad0;^xVC!pfL8jF}}NZSs5==>m*~G%~fT8cAIYG&gFHf2S=o?PK%R#Wt9E-oqaag_0ykQeY?wXQo7K2J@=N0lloa;c%+^?ix#xk&lT|TDI<T_N$OtZ<;RV2IuEmRZ>RRh^xQo%M#c&Derb$T=Z@6FkmrYtamHko`j)=R0X_HZt0|v9!MRh<ea$<{@mZ+yW@DVI3#IP$axO4(?;bhMTV)+$Y@b5kNnSq9e0_U*J3f^>tj#JTryjZsx7uiI|CuGEo;=OHP0t-y>q!6VU+mIz-_&5Khd1N*8RHl4D|K&nz(GB?291}xv?|kKqkoopvfL`AzcQA)ZHJ5>U+btbPRKbs_Z^5hVe}t=Q~Dn)aoQOF$Ct9)><M1u^ESyL=kM8+QF`ufRa(xw&?5Hv;;MK~mV0NT)Wf0Cc0EkaC;cpW{P&mi+*=}poX-h?M((@Pz|MVhrYGsStH}hZOGD=->bdjYa;cw>P9zw4>y%O_t%etj_4&H8ox83E#vA#Mhwa>RbYYw^PQoL})4hr{`me|%^NMC!joe$Tp5*JZ#pt=?#XMsk;?LdT<L%?n-Kh8~m3t3lxnhsQe9~9aCG$*j_b;E=xiinyI3wS+PUfXqkDt?XD|e)fGjCeFo;zzNN!|Of*#%>qo<GZe?-C$&rFYgVa^CKh^ZHe<uTE>Zb99o_JNLH3dhV)JN0vJ>JX#;eovV#3_i;#!k?#nT<sR=4Yvhd{$~d)tGuFqM=B<3*HtQ1f+;KjWY}X%y6ZPENI*07fN?#bcvwi{pJl4*gIkL%iTXEIiUY<&a?Bmm)yKe?a9p0SR$gRh<WII;wm89p+6eDHc+oNNmo_ks?uyc3cxe0pi3q2;|<ehL)&mHOimh<9ykqgH9j4f?%7wbT=cw>Dc+sW}?H0^mKud_?8mrrNL8F{>HU+c4Hv3l;Up26O}*0yX$ZuP1p*VpU$VvNsQW4avY3$vXu)_=<p*-s_Dh&1{KW{~U7>g%VB&&534mo?o9W4Q;r$aSYy!ZBl<>?!4XIrYu~V|%VHBiE7W+q;a<b-AgWcN@}g)pJ+9fig~?itCK^IXpwIU%iJdF+Nw|S{Y|>7Ppb#J}Y_X&olMo$~)qwjQ`W!f9biW<}1lJf4@%8eStZo{%<P2*%)VWDXHgICvVqt_w2fIJ+jvBHpbz4WOeAVU(cOqdQ0vLJ!p)dZXDN(zK4zcfy~dH=lUMebJv{%a$UQ-@R+eau6P-zZ|Rf9`E~Y&Ecc7Kr;YwoU&#8O{L5>s=jAMNzTZh3WsK9Mh|JSc`;6QdUqR}|<W2T<%9<S}<5Y>X&ud4K1NQmr&mB{Lw{u_PJVx&QqnMnhNj;PF+<Mhj&d1g567}4Fo$_v)onZ7|vRmrLg`kUi?o08jT-QD-bir6|Voo_vhv$zs^2zn(ye|CeoSr*7t(3gV*f?Xkx4xD8f-|>c_1qKumz}#Cr!sPDQX%_1bxz9^W8@EpNM0e;86)>@k^AV#nUTi!?EIJXUmAZ(&)xki$@x3?`Eg^Mi_K)7dFbRZBk#LX>T=zlUm4qZ*fFUaZ#Nt^KG&3olApMBz}P-7ipc$My^Fhyyh@<VKR>v?#n{fP!sL7pO|j0%vrmw5y0uwie6E#CWInlf#dKr*r6;BSglC+kABWaOnU}h61uWHb@6CsjZ@;xp&mF7M8Fe7}_-Rncr~}FCQ=^Je2a=atuBnW(xa)qS|Hv*z9Z2rqf2hn4tMoc-tWVG!sRQYHA2G&RwoUSK3yv9i=15te0o6_#=i`{Gvi|K?p4M~EwLfLK>)(3y+~rOs^PdcvqKx%Som=J=O@1`<iN&REtXgB#0rwBw*Y699Hu6Y$&gRY4DaP0@-1qrb1;-lOVa))!pH1E4tg&AjPLbt4oe*b?lTMybI)lDGXDm13h^&9ciSfpESQab&Q#QI_jC1T;$^Uw5<i7R4$$GxHbJ6JE=c$apdwqhj+)^oJ{!_nQqVc(Qq%-DA$^BPnmwfLVBljNuN$%%@B4mHQ-Yw&NbxEF|PCqEmL&&`Wf7`i#9_7!SqpHb#$sLxY=Wh34V;+^<|J-b29_7!i38$n!&ue#4&pq2;81ty)@tH?C5(~r|<KO5c^Z(b+&l&4~e82SHKO)ZP|Hoaax7V-7>bb8|7MT}?zm74+@l}_3)T=Z`?hc(Lb#>R9C?hX<Qud#7YNVdKdS;P%ZHF_bjPZvym3dT)KaU&hdAWzw;Za{6GsbyU)~J)o`>}d+qfRDo&wDaoa(B(V&e;CBXGuNm*?Ec4f6Y4SAN^puu|6w!z8rLJrhfcbj$fpH{^0wUp8MxZ-gPnSjQ;mzzT{Ywd9$AT=Sz;u{kH45yH=nauM=kM)^q=S$&t`{zn=T&OWy9y4jSWsE%PP!uy%)y_1Un*cy5`TGjH+qyB=jM_q}<GbMGGcyxf0zPV}~~gZ|u+Gg0<$!<~oq+zL-2*RMDC59qmnp60L5{yce}R=Va%Jx`ve<yv#v=wCse8+hJYk$Uc*r@6{yvp<(BY_BYr`$12YzR`N_j+XmD&$I3^dhYGo%XpvS&z<WdjC$+Ot)`zzzG!HiF-}I0<iGDaXN(gg_r<Ps!{d$hxg+<*j>y^<jBzsiWWS7iY37g2`_ts{-@89e9{*?tsh^KZB^u+rcYm5Z&U^Q#?kbPv^A<TN^*v;`U4Q(!Guz)%e}4LRte(5C6_$E3<!+3gds8)$dD^l+qmBM`m&*NGqaUL5+=`O<kGEC|`+0@uI?FBXk^AN2XTH&M-?%F>ug)*efBd<>{<{hX8o9G-O{wQ)rX?BuHw>5hpYiiVJ@?;7`xYHfFvj6|sbj*#i+XOAmFuP3)8K-hyYp3*I$xt&ypjLvk~$xr>b#yih9*fJ9vu{EEVs{xa$S7X=9IDi5#1&Kb=YxZeI|~Q{hhh`F=L#OwWZ!Vv+gw3r%R~R&&BCC8~yJrmj12Z%s29)`=kz+IWpMDr(To&=(skofu4W)O!CljtMuHOl2x87E~~gv&s|mJJ(1^+CtLO0e;;a<?z77nzha2gpH8dx>AC;8sL#4}!07+M1nIx%?jfT;&qbZ3(%R2Ot;J86$C}Tj{ke7RH@Uya_VSRP`=3iYXO}ym=l<ubzO?0z>f`&LuezR0I-%$O=c~@IDxcPK|MOK()o;AUdOnfotDYShqKy2#=c~!fO{^t#srpNK|J&%Pj6Y=)@0VAd)ARr5J;EdMnN4K;w1=bh+)CR?=98tC$LP6#e(RVwKUUA(*C$E+jF@xQ7^l<%$v>DKXY^lkT<W>gcivc^JwHjEym|0~p8Kl&Da(EP`9)(K-kV#COC}omd+%S8^Y`Ar`1AMQzj!u2ll6b^{gG=!xo_>?XZ$SnXUh(|o+Rg`f0Fy?E7Rii+<zbKbNgbAyh%f;8*d)O=(#sxfYj$_52E$lnfj>YZ!bsbxog=|nNQxY7pdot`>o{o-<0o^F-~ldyf>MUX@{PB!iM_iV;hbBaSLR7eZFA1(SQ9887FD`Y-9aDi<LTKHLGXj+|RlmtzM*WPwRrbXK}VzwARQQmzH_dvgezO?Z2ae%uhxnY&Y_^^4{5bsQn&2cWxOZ^S8%|`;GBiPm}%`A0E_m|9fZGx&V3a+^)QA&)?_C_2v6B_I1afd#mn}>r2Cj33~3#QP6mA>(Bk~Z9Q*8<MrGMo+Zz1ZWlSP=kC`tWL}r6`f+2qDObom@c5IXdhUNe?mJpR-j4@Vkn#B*g0JR4`5pp!^7jzFTzN>(-RI?d2<|~A_ZvCy*&Ut%$Mo@&-?Jy4K4~nM_w2rwPOs6Q_w3G;Ga~i;{rBw2dDW)Uf9|z2#yBB8<-JhP>azTUk~_mX%6;g)zvVurcSRYe$R0Vbv$s2^=l*%1uke8LdhY+;i?v>!<2rLxlH-Bz+qh$PMeDgce{ZR8-sv%V?hGC+{ilb=8vS{X<7?9Ote*SItd#ycg5&hu|9vE1kFVp6@k8Ip_W5PaMI*m2^G5fj;)#0x{`Y^9^Y_00<B4KD_3tT#7~c|0bmUy(F8r>`yO!R{W%Uo&z9ObV_2cLN|0`mHs{fC^B383{<^Stf#3sF42X#Czg<gCqz6?g<%kbqe3SW+|fM@U(_(~X!uf$iu7<?7J8ph(Q@ip))z6M_l<M6fkI(QCWhp&g{@%6X|#^WA*1H6E5z&FB+_(psaOu#qcn_(ip8Q%hv@GbaOcnRN%Z-d|9+wkr1GQJ((0k7aY@SX5md?&sO{u|$gPlo@&C*xD#ReTCQ6@G_L#Ye+y_-K3#{2m{JkA*+rWASnDM|>PU9{z-n$0xv_@d@}e=)<Ss)8Tb|I_`!ya5p}Kru^o+RwzJN5Z=I5Q(gdG$5m6FANp|Blz#w!##K|E5B`L!raUkF5m!xl9{2;Un)2N6dt5c;x!^TiHRU<scerZGbHJ;(YRa?2|KO@APY3^vtEN0H{1#VDc{X?jS50|Vco|nsc^3E$uA1`9@Di??@=P!ZS50{un24*UJT*+fRa2e{Uc^;Xo)TWbRa2e<#^b6f4}j-!)s$QC9Il%3w`6hnTl@_?i@(8N!&v+^{tCw6ukgQNH2ydK5}v_d;xAwn{sR9CM&f_r83Tk~Ts7qx;Avbn<>}!mTs7s-$xh<W@n`S^{tSN#kK<4AC-4~l1b+;V;*ar1@N4`L{tzC)AL0+-SNH?`PxvMNCw?Cu#_!|z;351T{s%mW|AF6y2k^W2?{Gi<JAMc5!|&j?;a>bU{u@pC9{35q2mkn88vqBwPw;{GAowXh2p<eT!w2In;cUDmJ_OFehu}lu=lD>(6`YH=!iT|m_%M7poR1I3N5BR62z(^`0w0Nwf(!9ccx$)_Z;iKsi}5yiTet*oiwD7f;X!yXoQMbGA#f5Ng13W9@pgE7xD0QPcYw?B4tNAyfk)sS;Yz$C-U+V4JK>>lH6Dt0hHLQ7co(=9?}B%Q>+r64H@F_}hIfY^ygS|lZoqrsJ>f>YCmsej;bC|$xEb$-yWkewg@?nfcsSl0Zo_-yec*Py58fB<!29Bj;7+^|-Wcw}8{<vjWV{Jp4^F}B;kDsZyf$73j>hZYb>SGiE*=QS;(>U5I1aCmH-O{u2DlSWz@2zQI1O)zH-*#jrg$^x#+%{I;S9Vv-h!rlCcKHy#DB5=nQQ*S@5&3mYpr2tSP1Wohr)t*DBcMcz&qg`VSc<L-UWVucfmWre0T@EJ<N-@$J@a?csslm%#F9gLtrjE1P_Ke@nAd%=D>sSwlF*17H<R7;cf7iFfHB^ZvnI6E%4?rE8ZM$2D9MJ@TM>`-V|>FGvQ6}#xM=u7;gYm;|=ioFcn@OuLo1&_3%KL0uRLN!T`K3UI$uu9lSPF^U>P;uDlj}gR7?eBlsFuO?gfD3Rg{e4fr>%n(`0fOI$VO)!_?VHRaXdU$|<@8$mT6ZA4Sv5N5y|;!c<zcj8r{nvYiHcjZ;!Gh8+0mEludHRYAy6I?ar#o=RIHRZ+NBV0A*Md3qSHRTTY09Q?U5%?#rn(~V9KCYVb3h*ATn)34S4_r0n<=|ahHRWaD@3?Bp%fLIhYRXH)+qi1VOTpi8)s&Zf#}Wa;Tl}u_TlC$7-@<ppkMZ63EbE_n?JSz|{_k2pSc#^*G8}+c#;d@Acon=B9E8`xtHQx}RXjUviD$>F!6A4xygD3;SI2X}R(KA)1{{Xhz;nXkcuqVQ9D(P;bHkB%Zafbhh3CQZ!q#|RJRfX>=fgjMZSfEA{4fa5j~9T!cmcd148aTHg<w0p5MCIz#|z^%VF$b>{t=A8Kf;T^j(8E=0XyLiyeJICi{iy#XS^6*9CpEr;~&DV_=k82*bOg%mxSH%l6WcD122V_hCT7pco`Umm%+=zUU*r&9CYF3@bWMmFOOG%z3~coMc4<gh^L2r@$`5G*a**nXM~OMjCg9;1W%2pg7xrJxCLul|NJNqfOV|o$3M2GfOYW{cuE+Er^M61`gj^VEo^|N#nVA2o(|6h8{(Pp%&;k*8P5Wn;aTvkusNO;&jwrI+3;WCOkD97Tv5$^f3^OZ6aUJ;DW6VL?uMOlH$Dr7;<NDiuoFHXp9eeQ^YFQ_3qBWL06X9d@Xuj;{BwK`Y=_UmXTnzaOne3m!DryJVK6=${|pA<pW&avw)m&`C$J6v3H~u`iGPewgDvoB_*B>&pNda`&G0GsWY`p+j8B41@JaYY*chLPkA)5JvG_1pA0LJfh4t{E_z)O~55Wh+y7*vx5Uhg_!Uw|I_&|IBtc4H2`@@g${&+uF6Yq!jg*EWLcpvy7-UsgutK+@#a99lw$0xu>_yl}BY>1D?$3Z7P4j%)n;$!g9unImJcfrcI3-1Lh;l1!MSR4<-d%|LPPrL^#iub^~LkHd+?*@zD-S7xl5s$z}!3y{&d?YN7kHovea(GvK1T2e>z=y*!cu4Dj6uDCVcmKu7KR>DtTE>5P^8R0%uf6rZEcx!@pZpR$q;+a_ZFzS=N?}jjuB)q^^<UTeRaO'

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
