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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_008.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_008.stl', 'source_sha256': '2c7339099dfdfda243c59aef347581df26e5fbb7b59cd3d783826ce199994997', 'input_faces': 900, 'input_vertices': 523, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2730939984321594, -0.2991793751716614, -0.2727009952068329], [0.4114905297756195, -0.09402504563331604, 0.3287442922592163]]}
GEOMETRY_BASE85 = 'c$}r23D`|l+sF5LNQPb^l~Otl(jbjWnof#WgVLaRc#P425T)oSc{OPe72!~kqIpmm4oPL`!Sl!vIgOe~kqnh@-)H^q-C6h9?{$6G_qnch{eSDf?z7K*?_r&F_CAlc=T)j)H*o(B4DOnC#GXTs4FYMq1$BeIoqP4^*0FQ%Cf$49kqBz#efg(4{DO9E+FqFm`UZD4>eRV+$6k$^CmWsGrCFoK$wpmz^y<^AefR5o^y<`E{8sI6?%g@`dv|T$vvb%#tm$#bH%=aZc;n=N<p1$s^)Q9h_5GL33N<_A?**c{4ZZVy^)vX{vH@j<e)8p#*!Tcn<CAyybmKkyXY=tjZ(I`Rmp=NK7oTqO`?R=t_0z;>c3kGRGrM7V{{0_pyClxf{5r>r&pmwX!u)nkd=@`Pd}{wQ-20E+HD6aSwb_z5KmGD=UVOUh;(T366R&>8##gB`EjAuMOMGtF&a$|Cte-aVHXrL}Y`n?G`kGH>X<1q9{x^QK|M83VKfc}n!L4J<;?5uI>-nR;J%6mP=TGw02g>5kfA#J8uf9G1)wkz=_MFt5xcsfJ`Kxd9w|<oW_ciCl?SJd*{?8q`c6RLfgI{!>sBg~)<Lmj54rb4c+rIVFCf>fU^)oi!<YRr!Cm7m(X59X<ezbq?*fAsScv)YMm-_a2SwEVunsi%whU7Qz-u!m5Teg<x`)m8={h&e9*|GlG=Vlf9!KQI}KRsyK>^NVypW3Hwte>nHUs31>^*YTg+)ioLm%MzE!>@?-ORsvm!t=?qC>~$qv#l5U`Pb-K9_MG85Ax!pJWag%8lOCNZQf74e!`r>y3`L^kDgKJr|0kV;?t`~#QM2f*Hjexx*Z#@zQ$*k*2|BlUb@3=f1Z0^^@Da>rx*I!RtLHLx23@c`MNgxe(IQ8<`nw52M+eOpKJDUte?E}@QOlT-`B>gukooyjlF!5cP}iD^HUufdhwd4jaOgegN{c#f8FKY@ls#U+uTR%md5$%hSir9`swqp_l|FB)A8kn=WVcb^U^p!-RI8=&*!`?ipSUZ%w;Jr|J<Uv<#B%L0Y`c9(RseHetDdq{d1WYAD!nWKDsVUyzU2^kNTQVx@QajJef1TJkC$u+}4Ya&Jz=_eiZ+EYybSIKe;^CpV!)pkIo+xANj=RzP+Tp@H*A`$ND<|sIS+ljaNUK-zK(q=i4bmKg{oEt~>RUwJ)1n=x6_Me(pNwXY_in+0ENdFzu^YKYjS_6@|WT-^Q!2@!6r>y!Xw%>Ef*)^mp;WEjKxT`H5bhsVO)6=k4du#ri>=HWh__bY7Ww^))^@zProo+cEj$p3`}_X%Fvw%U<+QyuZ40MWL_fn~jfrjlaF8S8p=At~}OXRLzS|Z!7cX=Ml~iZhOtkU;Wa{9`O9kIk$S}dHSjmv3_<4pBMOgp4)i!H9q*emzQUDpH1a)erfN&o!_Ug+g{f>UY_dfaY?=PUA*6{Mn$2Y>u`s^ov!`d`|eS9M&W*o{M>{7{+!*<+n>ow-^cptAKh_LU-z?(S6}0Umu~m>L(^Z&<NV~dz@5+M-{Hoq?mnY%e_CJnr~2tzhfj}-S3in>q`%wF`h)%J?xj1u<C6aQr&vEoRH-QRb^qIV^))`-`z~)DNH41>kMmPk?(eo=c9%CVCEs)L)-P@3$LqXg<JH&rY~2Cgen>vCu{_RCaa<z5^e^u?T0d#x)59mk#;YG4_qPYcUPso~<CtqT(2Xx&=$-%Smu~Lv&u^pd_U4(O>Y7+Tbzfa~-kzF{oqtN#I6pXjgO{iEHBa@^r@R>(uYMGN{~)if?EGJ2{oFxrzp1bF+W2Tc5TBmq{LIX=z0Xti(?cI+on!n1pP3%(4<9$J&`&*nkGK8O^ZtnSQzN%~zP@kD#H*jQ@#Iq!k6#o|o<;Ha8lRo*{9x*LW}YOz)w`ab>vXSQSNZ06zvf?_AJt{zBj3hrT{d2Q8?SZQc=d@-S03zL@7bY0#rnZSH;-jb8tm1T3EcLrAAI?j=WAVQ6R&<QXX2@=C?3Bkp1O+S@ijjC$`CKl+)<li{mdJGd%otGHStkhHl93-;<YXtPo72bS{L!@nnPWl*~R|+hOhHO^5|b;{q)R|3U51nuIYNC$Y;HwzODy?fnS!#`RN|Dym(!=l-|F#Jl5}2$BWnXgWZ0#t}xrz&sm#)<eU6;KD7HseY=0M)o+U3&)H`?df%6${ZONg_x(57j(GF^Mg3@gxcawP|G&l$+3ESwykWLu=kua?yB(cR>~_rjUleb*qw|d2j`_SOif23N?i|Ol`+Ms&_3ix}^@F8H&xrNUJj`29T3<hZ)lWZM+xe_ptgq{q$X~U6dffKax7)Y(ouc>;HpcsJy%z6}ofQAR_(gU7^yu{1y6}tYYSuq~`}jrMKd`5t=l1(!=UeORe5<~lZ>^uU@n*iYeo?%cZ>=B2_j<_Blg}6H>*t;N_VdpA`gs)j=JU?_Me*kI&iYaO3g;Jnz8haZ-%~9g_U9Sa4@Exf2lefGrpUMPW<68n+jz5{De`swv-dDBPhEdnU)P`N+x4gQlQ!P0KdoOBZ`PmIkJhX8op0Bl>f7~a=10FS{k%}$&i|2b=JUum^K-iSBkujp_Yvzy-!Jg(_Yv!BeDXTy+wW7>*Lg;L`+ds#(Y&-1-+qs4@t8Xf=KG-a_4{D*v&Z~;_46Iye&0;p_qg}I(f3*7M|FKX+`At2`?&S>`*`G=@8i}_nt1zt-1^b?_f^if_aCeu-A}-`_aCgU@#$_)xczMJhZtY)hh*w;AI{vLvA*7KQQzL5vA)J<+l=(~b9CSM(I=g6?nhZ)kE8nbew6j2`+>(j<)06Ff6VyNaV&Y-jhp***4O)Q>f8Hu*4Ox4ALrZqhmmjYALcF`<?a9IJ`BFSpIPLyK3Ct~&&+)>CiXhAessN;j&pUH`@PoJ`?u=b`@PoJ_~ZxUy!k=zV;A|{$4)lMc*iB0H}LKK>U5_}?0gkeanE_|{rMuF`|ax6`}0LU@wtO0c*iBWf8O(1w|(<G!utArL4Er?!ulGY>+!s|-}JgmUOLH}2lRQ0_4Rp5dh{f3Uef0^*4O7X>f7f#*4Oydw=a9|8_f@uUh%dceg5Lx=ToVZraLvy%dD@@ztp$S%dD^QnKwW3&U1Z!SLE~jPJR2lugKTuee)N2=bJu%w7x!nRNp?Yw7$ld-m=&`uk`t;_4WCw`u2IQ_4WCz`u2IQ^=-U;o@@Q+`SRk`Zae0AxAmjv*Xo<+-PYImp#7KLeu$pe;}<=zH-7ZI9^XE%&)xHlf1dFB0qg7U2h_K}H?Y3OXI}l;J5TiY57yV;Kd5hiFJb-Y_Yxg9czH(mrSa|WH%hB-_1-sHAL18%Pv7S5KNbC6#rV<hRq%^`uVQ?S4}Lzz+fH<R@$K(tQg@zR;hpFFKF9j{`yBP{?|H1R@tL}Oo|xYwSwEV8)HlCJvcAR#OM3eGYrXhIzo#;O^m{7&qTf@U_OzF0k#BzARXSplw|(_9!Trng{<uwx^VjKy=NISmZoA0ybNwck75W*C&)mKwzn}YUaek}y^YiiR-F8x)tF6et?y-lx?U$~pk@u66I(hNA(uOMvx0CF?N35T@rCI)cla-tL+uz(^ajgG+V;6tdN#6UW=N+&(&QI>?;&T&9oj-NWCtjWl?)3fb7sdM7+_t<QOi!;U+@Hx#6Fx2Ub${k2Z_mGPy8i^P-qeCy%L@Ip?w>7>FLB5H1;5^sk!7*|=V>oKckJ=*_pu2-KCAvJ7oV&(+223EjVdej1N>}<fo}U<KJfNK@<4Z7te<}GsC<03Z~c{V@z&S)U{TYRarvlk^U01oab?{8De~Dr>f8OJzTH3R4yUe+Jzn_scm)Suw=(v8z_;f^s&+?jKj`^peLdfj%?JAN(e*XS+i!aQTVK!rVC7_g|8RX3`QQ8T(SF<H$4CA;7oVOy&D(E!y<1<e_w3H4UY=21{g(OpZ1DZ)eKo%G_ulr^&pcFnRpD{bc~5;i@0G4@=f&sWx2^YA9Aj23ss8E_K_IPKP&eq(zTi(d#FT%k@qfb6?S%i;pKzRf%rXDpKjAng%%Mrxjzo`u<u6Q*4%;zk6Zqt?ofNia=!x*5VLK#jjnIbh31Mp*w!_fF;gi@_L$ncmeAtc)+fis^xEb$tD0&E-2wRQ(Zg*NAJ~(W9gsl?#FSrt1g6;;(zv^tSI@?MxCNT%0b>L*!_T_c^@|u9LI=p`!-uqy3s?Y1{^BUm>VcRQg2cUby`-g4Mu<eJ|g?9~G?XXorYr&PnRx@n7pu5An!26?n!UynPyP~z>Dr~a>x);13IaEe#!n&^$Xr+Sv7SIpyDi!Rz5;TByA031y;eFU&)zBKS?C+}dtK!vQzt&^C9%I#c?LLg}!`QwYAK54WLU)IyzTN2WhPOMl*I~R4V>Nm09*pn7SlxnS*#O-S)?>CSx(i&7{HmhWU_EBLpu56*bBt=EwO~DFRnW@t?P2Q|wgKp!@Lgf+&v<{vgkKKZ6vn48CVX9ZK(9%-anUKnJ{t0{gc~15jPMg-8=i3E!x<BPENqW3{s?2j*N5#|#;;{e_?7TIrUq_Y^jcyEP|GXmRQRf}T@kiksPr#FFNQCIFGsJ0FNb@ex57Q(N6^RMN8mdWPVY=OmL~i(IvRc&ehqyCehq#XeGh&YejR-iejOf#J_C<}`=fWk{ozLgr;i7Yr3v>$d%?QzgcpbH)3B{VrT-E7G5is{2rYvb!OPK=@N)P|^lSJ__y_bS_y@R3!fCaHV`;(%qYdGM;Um$b;3MIt=t*!>_%!qk_%ygB+6rz7pN^*B)8P}*X7Gt{W3&m}7(N6&6g~v5iq?Ru!aoL1e-0c=6aEVQ2L1|Ofv$q}SPCx;+x)P7hD!fKbRPU6{0X`M{sb;Zm%-)m8gwnZ2L2XZ2Y(C8hlXgSgkx#K2cQSS2f&Tc!{J8ovFP#evGB?0De%egS?JmDS#WdoRJb{O9C`wL9DEph1bi5rL=S?Ka0$8#TmpX=IQ>3wEKT?eGzWhHSD>H4dMt%yUfdbDc~hFO%&m{WGXD;TWsV*O%RGJ!JcTCQpC;UoCVVG46_)v-dcw^IAH!wL1Hvo0_JzOZdKdnQYhAb+O}HUV_$Zq2Ni^XzXw|tcTfr$>b*{f=a1&Z}uCqho8no(MV?UG6H(W=;tI)+<Ps^FVc1<|_0set`OIY+^SoBC(v?(ll8Z6op7CjvnJrNdd42vEDi&lk2e<YtDnHPk=Vh#{qj_SNEtaH2Yr|1gi4!OSM+N+#!EP6am_!OG(*)-u(X~HMaDsz1t0Ut!G%=J*2Ye6{2HBg!Nuf(|MI{bCaFT!h?gM^ncPYEwzE)$-|d{>$6i++YKEV!-`iGQv;VZAnm_4*aoYg}080b!jhgmpd<);UL5=OtmCyM%Rq6V^FUSm#M$olAvvz7^IvSy<<7VV&EB=c5(O9hZge(y(<$rGFvX7QPU^1Z@Xj0^fw*0^bA=L5IRa;Cm8I2PYg$6CQ((gU7&cq3^(N!SAEf;rHRU(P{A8@K`hhkA?3=?}P7!{}VX9KX5Ef_-3>_tou&*`9Oa26t4AX!VjW%z@m4<uZHabUiUnlMhC(Jd5!SrVSA6)y$U~oz6ig_YlM#u^KYAQuahSH9$E^EzQ{H%3wc1oz3ynZE&34r5U&;P61E2u?sb>J1JK9e$9awL<zXAh>$<=Xq7TCl^BUn}!gdj_yBr>fwujsE8sXJp4etl;b<%_{LSKSK+p~?=I1a065Aym4IY#fJFTqR0mJQo<^c`4qNdeEKzXaYZ;k0hTu{7Z`(eq)^3k$d%ebE*Ld;$Fy@ZRV?@ZPZGE1E6H{Vj47&A{)#GtoETH^^DJ4*Aw0KjkawpAWY~Z-(2!7ob<eSCgl5efssuS@|t;e~$d#f}fzDf!{zUz!S(>xfc1>B0uG>^t+Ou^6m6*hOb6%gl{B2<^AdJPtMBEk@G0>dk%hx{zK%a{51Uuu;eIOlYDEEpYpBrZzVtFLG%ZapK>qyy~t0w0sRK#tUQXGpC!Lh@NoLW$y0ee{qf|iygT_y+npRmZ-8$gKjnV(`;nh=H~QVkPkBH3`;oKqvjsW7Nsgl9;NkFi^mX`ka#pTQzO~6u`3m|s!2Qsh;C^s7^eVU;ydSzRye~N`zgdv`EOHcm8y*M0j?RE*khAh0<huv?DW6CG3iu}UQurqLDzpvUhWwQ4(XU6&%CpFQDf!KUr_-NKe#%Se&wwRI(Y?r5+Fs-+dM11(`6*vW|3dOpZb82dTo2tFt_Mq=qD#qH)<t_J+&ZW&ENh>3u&j4(fn|*|6dp_y9!C>?hbBCoCOnNMoS_NdM-!Gc$o*`;J1Y6<y5wJpf7UI+y0#J4^^dTwk%V;}C9G>LVO@_2>zYki*LA|W_7m3ip|GwYg)c=VKVkX&-7WFY`bSvTHp04Y5!N+{u&y_RbuA&R>jYt40|>8X8}fd_*M;reu-%AW0Cx*p8^+r(CVU%X_rh)H-yd%C$%OMoZzE<_!i`NzIDV4;t6`giKZh~l7s8fhJj<ByQ;a<TXXy_P-=lBfe9@<fkvaxb%LT*?rj8VzXlq#N_&4MKX6#&Qyn*o>7;8g~&r_%94a7<vA5!Os#5_qIpHk<ijLo8sd5q6vYz{R}WPBoHS!(P`ouU(oy?|Q!qFrIB<5WD+vtg;@EXL1bOt?K`H^67nmpWdePSN(nNFAS0=O@HGPaTV?b1`EdQpbG8=QAceg|Uh7eEL#H2kI1^LQHFF>56uMo6|oPK7;=0cxS=Q>0g7_9zLD^%hV|K2wy|YLTZ$H7BVLNC3uVBh4dHU&4-uJe+6#}yomm_)F|}`ze3E})Y1XH7M40r!4qu(OC4u2ekNnW*E4nvd?tOVV={G$UQf(N)F}0QM9j<7QHEc}*h1>~nDLJpTSAR5GX5fCi>SAhIz?Y3wgokwK~1IfrH<3^L|eg9M@z<AGA7)avFqWM^renxsZ+EwF&|K))bjx`lc{3?{sP86qK>(Y&t**bImTXu=hBxtx=^R+bHucw#un7nh5kA8PlL~=e;!^-_#FCDM{oSzjJ2f35!5N#n^>u126fILMtC+gE`VpypNTgYo=sos7>PfUvANXPhdM<^65EPex}bevspD!q(N3_`(UI|vjGaS`gBTyg*m>0WAL<kxM6A>?o;t@9GlDv%Qs-30W>Cij#wRc~n;M5QK9sSU)OZhdiVh|Ad}`@~-UB}swz*+@7oJT21-uX7r|56R+YY}#zf;0_=Oi3&C8lq}d6y&{ccR}J?_9Vq{cVBsb_9+)6C-);Ah*ekNq-pqr{J;l$KbsH52L>YZ!0{8zU0+|yhXPVlO|`$FHMZ}d*XG5)Aau!XUR{vCoz-BZ5#Rrd>{Q`@RRgM;*EjtqrVw%3p|p3A99xbgf|l-c?}`&A&d#%M$SFqA@qMIXUR|aHe#M6=dtAYJN<|0-v>WKU-BA_KbkS&-x%8rkEVYMIZJ-RzY%jcIZJ+bGba7+c(=iK)89nSlAmyQVxA%AC&_UWeaUMCp6DcaB4eZB5%eXmjrbcG8%_Ql$Xj$Hv65GB^6pKHa7S|P4)>-ndHqV>q8*8OhTJxxzrxe#kAUaUpN%&Wo<@HI-bQ#f{eP3Q<R`p=n2X6-^1GNZ>9@w~2wzP97jl;Tgj*9chny#o<1h4OO)qQYzXP|9zYe~azOby<?}cTJE`4EHmrsIaE&eJj>+cuf!Sw&;eFn1~nFD1G{|oI1iw=TCWq$q(9S@66g+(X8qC;WPd)UrByq~blp)!a48Mt}#U3fcvVVNJd!<R5$3ZKgyDZGRJpKNaj@pCxV>(SZpY>xMORF30%^kVp8j^%oe+b_ib!ght1hyJp#twC49tHZV;;l@`mCj3L#zGnPu#)N;7Yn1Wd85909Y$YXbT=aKhD~G&mi5nL!f&U6yr4lz@i5TIHp}&RkEyM`_7`AT`Zu}d@Hd4b%##b`-Bfe;kCj2wH5&jw8fc^z<fVZQP*LM2CJ5Z@(2Tgbz`U|`bUXT6&uZMp^SHnNSYtiNKTKEfe4ZMchgg+14(y&#)pV1dBFW^=5%i%B4Z{aWDKhR&{Kj5k*PXC6b30FsVDRC@KxEi`M;kX*SHR1F(cq{xB`W^fgT!DTLe@}li`Ww6%PLw#^2`6~pDyZaCg(e)JQbRyrcoVh$3U7kfq2I!7&r6ilt@Pji%kqEz$!B%o{RigumHy9U3tu@e+*b6X*|z8HBEMS;^DN2#*y=U;))o8@1W0SM'

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
