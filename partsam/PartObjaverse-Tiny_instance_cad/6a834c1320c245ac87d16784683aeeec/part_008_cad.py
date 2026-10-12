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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_008.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_008.stl', 'source_sha256': '9306cb4bda5c8536587a0fff4a8a4fc555165ebc4bcf26bd22480b46242df9db', 'input_faces': 471, 'input_vertices': 432, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23319308459758759, -0.1410539597272873, -0.46218323707580566], [0.17720620334148407, 0.09583637118339539, 0.28954291343688965]]}
GEOMETRY_BASE85 = 'c$}r233N@@+s3!4rWmT4s#4b&D#pf4a}l!;VjeFMMGYY+H624yF;hbkS0WO`98(QB67xLIt*dCw6hUkH@BO~dxz4%n_g~-ozO41E=efVUcb|Rs*=G(RO)_N6EBL3dcots#o+u@wl#j?OhK3Is+&e5hvTXl|;ps$f;`9Tb)2wxHNc(hRs2JhbBRn!}kY9D1U(KFX{rqiyJqHXLJg8g$t^)@32v@v*x4x0#l1KLH77;E#mkjv2qQC9yQvSA4w*TW#HrWM7y-UZEr8_@&>B_~eT)!#T3JoQ0-}N(bZGQ>kqTJOZ${l%n64#rIBX0lu2jU_yiQDNtm+NN+9wM*zazUV~^Y3%cE8p18E7y)^u<{b2i@mmEaL;zy?T-F$+-To5fVp<F-YTl^-~P06(XblVN8eqqKD#1=kJI<^RAt^cb`O28?7yeX+#a=*xUK%Kv&mk#HugKO+@8DDX-hj>y6E2OU9}qO-rCoi`Rd;KV{p&*h4atBUU~Tpz36*uUR&A`FO#}^Tdu)9`zf>{&B?D#vbL|EsO5FJjn_^H{4e~2cAEY%TYc7Zc=R*IHQ#GHm{%Y4-<WTn{Ws>1XFDOMqrEP-?!VFIc3eK-eqssDpT@aU1HEwD_<YB`aWS?jEmvPzp10$U$=j%YogcL$o_5(!<2b1n%^xv!70>hRotalX#QS5fHN@?k-|VCPcR(P|w{9uKZO2{_7kf3HKgAF5ez7-fFZqjxTtBJ!c?)kC%*TPR{fXNKWF+n!vWU5VZLUx4m&)T=lJ+lcWd~lbd!2ZH$Q~3&<9u?oPV0B3J+IH+0xQ&K=Y<)>MNBC30u70aojZxUB7(V{Q#+RPI9}lTqug&X$Cv8ucb^cqyRvb8`LG!J{6m8j`d*O?T)*IJYDb&go46MKipTNA<z@8wt7zu>a~`jSvtwy_x8sQ01Jam3EkNAWeKT=q)fT#W`|3A4(m2>>)+X-CTFkPa8eG^jM_PDWe{R1~arTsg7H-rV-1gVRUx_~zH2z{-Cm#QiT~<=NSxQ-!YjDryYJ>9=*QQ-sN$qs(!pF&lSuO1t%Qd)Xf9zLkClJ@8E1UN(Pp);-xc?<P#S?cX{$#HA<VL+c|JYbs-o7H-&*eLkss7Fn#6@r#aed=&#O=kpbN%@eG(P&SFL?f>wC4Jba}%g;TmW&cY+dFB9#K2at|7$r#WP}v->XgYO>gYnL)(8v1oOf^)Q+uv3UMu{2lEZvY5wc|(}>&uXv@6lck%Su{|#}WH6gBzOr!Q~@jf)K#Pb<WZ}Un#O`1dXxx3Lk)Z3lqc{nqHdA=LO9skVd`JDOtIo!{1n*a9ufAV~e>%%-l3UlA9+>WaSx6?0#_us}FEnFObL)=++2CvuXdR%{g4DY|~S`gQ_`*ZzAe!RZFcDC}@^@wXVM-z9nwQ)Ox@)CDGTF&GAa>`8N4|Lit_IX`--roLQqjrX#rv5mNt<}w3Ti1b)Gv#*h@nLcWt{)u9$Bk!acs_g+H=61z_NI1R8?JCWNs*&@UNxh7N4<w!U%Bi^;wd$FzZ^FCRI)ezB015*FJ2w%wcg;K^*DchP;YRfzHVXS+VtwY+$hw0aQ$71rCyZ3KGs{k!9S>9iRF6MgB$f)wI&0}XKdhkIBfy%7k;-Rh#$C2^Ub+$9nb$krTY<Y`5kdvxns;5g!d)hq#?I+E0uXbdgf>HQ@wuwEYGXI`_XlS@M}JkmUn0n&(G<<%p-od^i<+;l}=K9i)M5^A)ISx&~~p^<DfV06pfEiJ9ozO`uoINj-TSMX~dmPqW5^?TCF3=X0E%IaXWK!4k6xGFu%H*uVZ|cP&@jGv{Pno-+hqVS@(jtJvq}tTJH3psorsU<OwqudMef1&P7={`tLk5lepOaIrH2<)41tV-}3d(+A7TNWtdC-8vO8th2PFO-@;$kXWl)Q_tR4jK5i#8VSe2<E6_9!Zr(8|+AD8$Fq-?Dj`{M|%xmRbYF@6sq&IQndRy<fGsVoE``0CV<Hk6+dF5fmwLwXAU*LGtnC}bbkK%TE=18IXk*jx@x$7OD&po-jeQ-VZIOZPLjh@`NZuI2hW+;zC*@?s*Idf8fGzYhDaM84m?v=M18)@dE`6lLb=Wu)9?dS6@xIVHiU6<PLRi%E~ubkxiuL{!s<h)R4FMV!X;}@RqIcT0ZuRZ4dwC6hJBeD{AFBe=(Z00m`d$~=PcHHB3C2<k)1+QuTI0GK=yd8ImdG1Ht-)Xh@ye4ij&s%nhrTwXk>3&ia4znH~LSHeD%QT0^p@%=uhuk@N{*|pk^|l_@4-ogs$NciSDYW06C`88%k+U@O>Y3)5m#e3BW}a)oLQDT|&0v1|4!4tj;$i-Lgn8ngx#oKP$TjAb{HQ<9a=WQs-|&R_h8MIy>H+2X`eE=5+D}ByPpIDB*pH8UOX}0Oi}bpsKenh*%%ksEmaC0%@^-p3d70{`YsQzfzOMeKx&G9$W#;}n`(5DrGEuSSdeJ#6U1tmbnX%@2M{s54ZMyM!8{5TMd@XZ(UOLYh<L~tOhq)tYyqP;PXQAtU38>x}AMwt{+@5_5&F?7#`Fi6?L*ja<Z=$)Mj>o}V-?Hy`b33k^5qw_}VxxLT$^_!t?-Ph?n;)++w_`gU&+R0otufc@y;d?W84*Rx3*EPmx9<+-Syod&T{nNH^>W=kz&z*=x?i?+TSWEt-8YyY&Nz<NYjPRdzS^2k`M%}xztoQH@lNi4-d@b7uAu8`TZi@3j$_O+zK#qSOxN}L!gkb-7?Mm}8@4LOJkACerRO@$+#dFv?~5Xmk}TW3Q#L+N7g^&pkEh-t*K+RXmL&7|*n_L^^+EPRd_5CB@1&V)Ly}@F+qXdzZvR1}c=P<RXUfUfuf=}ZOk9iQ@p%>)$NhS<+S32O8}aq}jc=(P_x|$7Q0D93tufcTdArPsmj0Yv!+dSVwPvnqOZfUYsn2F}KefJ>_<FRCeY2%M-`?iy&e+8kF1n`U>*+mpHe1HCeQv&<F0$0Zwdw<yR~W?0z1p0&?-$33>zl*5zL<;J*K#~3?h5E-X-8zrMfW*c(fqs2{TFYGF#o(N^OEQGnz^WUX{WjW+CLR6+}+O?m5DoYwV`$#C9Yt*H0Jv&AIC0Bf9|*Ec4jvtZhKPcDAiwyBJPYSKwM8K&GYB{FWmm5(mbyUyxwEx&WBa#I>EK|&r~xPPs;H1Lz^l5eCFIzZf8S3zQ3PydY_rw4;LZsY@LJondRKhcl;d27IO8VH}1OK@{pO^LO#|l+x^r^UT%C8x4&@AQ8U+WPvZKkTaTEztJDOpe>%{@jpe$>)8M#&aphWk!pv>0(=)$Z{TMCpzyTh&-a&l*85=|GYx|CJ{l#I#U0-hG<JI0%+@E<P`8jHy*2m1;x!`+l=SE@XDd(AQ@aOv8vkrRWu6!vxp1W@G_!Mo+^}8;lnz^$FKWEajC-U}PU4X7rU2%DKndiS)QJSAG6#vvR-}EIx#2uM7>@m-OPj1XBgS$@5;{Ie^f5IC#jx!=*`#KuGf@z85TTgB?bJ2Fx8scGp64y@r&OCTAaeJmOwv+p3q3c)eQWUi#w6BP}g0eGz7D4qQzBzH*qdmk$m9zXDsn@DsX?<)5nGblgn*7p5;&$J^xSfNOm?wTh*Ex;`512pg!_V6*WaR5T$7AM=s&KtuQR22tQ#R4({b%WX?({oO*Da23=P_Rr!spwAvn*VTJI&|49WH(@v0yRRPb$afrCaCtx!=DDT(55>Zu>lu`Qrmz|F{dCHym51(e|>1p5^+NE<XPpX>R3nhwyWTuvk8BOt{SLl$^}x89d)GxK=Qpxbb|$bu{x9+Wy6zJb!R~=;q0G-5dA3Zg=y(J?MVdlY3rQYeTwjrFyaL#y84v|L*1<_x1YX30rxb>RX;CxB^S@d@L}9@7FSB<mbslz`vbpdH-S`T$Z`V`x;kFdFJKMc1$+6WAL|W3(W1?pMrb5Z~B0veNXQ0kHJ0OH+{g3erBr5TrBjX@u<e{7d*K=VziZ`{~y#F>xFvTKyWRn6wNcdzwqR)%V@t>AeQU@PHjiqy$z=<9PJxid&u1Ly^^?Ao9jF7h&K1fle^pLSI5$h(I1g5jqB}S@_p{{orxCS|6{%{1J^^}^8Mt+y1KdEzWN03HxKI2^^(4B1l=Fl$~?4i`}j*M==V$h;p?V=-rJ~uC;HIw+*!pp#mpW4L3ABrKUI<M3wLkg^My~XR5RCi731Uc#%;7*gKN`@?DWR<ON*9!YezgQOwTEud+#ha*NX-@>Av-Y`mL4uxeD5M^=WSDr#?0>_21w|f1E%1#+&Pn{&?0K{n4v6PcYXT{rR9C{c*Q{c0h`G{6$1RzW@7ljD_p7j#0hM7H=7UXW(D-*^`TgV`#a~P?u$W#i;Em-niq(7M6Nrdx^oTs6PgGZ?C!861;KGdSl!?muqm(<+``;iW)1Ey>QorD=`+1arSKA;2*Sa%m<JD8{Fu><J?=z_&a}Z&+io$_@`R7*T$`J)UPc3{Kgo6d&eUDIi{6`+qS*p@3$I|Y94>*f@dja?jHZ^^JuvScaO6NH^$Sm9b??Irw3xq^~U&oP;ZO_+85`iS^BA^9pgH1cR$;_jx*Q0`{}`retNd!-o8D{#GC7letuAI^b_rC&2sbo(6IA#-|Y+ur_XNwtm+i<@qhFD%f<Vp@Nv@fDA9uNcilYwZsN|Nb>b}i<rS{4`GoiP>AuY0?WgBIBB~$n?*@N<lb`oaS(|F%_tW#dJ^YyGZE$|(5kvVpA#@$jbAz|u&*z=~op`xN3oxIRhtGGNs`GLUKA}24FHb9zYT?7%({nq0R9W6GO$#v}*_^m7%N8ErM`?Utb<3B>zx<p{7JjZF^E~(0Tlj$p=68Rh>tg4<cg*`t;eI~6u+hS?URswjYw7ddjQh#EFXevbct!2oO5|q#&53E$PVy<;!b=pIPQGSgvV~_GKwQ5(V;6bsXUxBM@O9m~*|ROY&t!hTku%>|3-7d^xmeYf#;s_6=BXq3?<M9>;rCVs-?Wx_@rt`?eXkc}KK~s*e@#fBemb0mnRiX#?LIlKJ#DXRMVLqSWnOa<y(iJ5OE6!Q#_il6LH%^h3uM0d3D2t;@w7j=c~mi8-~H(pd*x@?-F!qF`fR_Rp3lSQ?EB60S$x)+uU8Cy+lSvf+<d;-!tp*r?0ubR;a38fZ<x8s!Y_WqywJl03qRbG&!@w$Ew}JQo$F`MwQ^$|Uaz3%)6P%ppnf8aqkZ4I6bqkyp13Xg*&Yk8T9DWG$347#=QLv8ekX62u_yUGtHEoh=l2z}{-*PYcDgb1u|Zs4{0iNlxw)~w=PI<q!W%y1_kE8;k}TYJ0$=ate-&fl?+)>MgXJ53ruECy6!Uf??{^`awpw@%U+(9b(<v72*OH%CFE7mZ*DZpvfAMv@c4^-tTCZ8nm`|ud`>E!eneMmUJmXfb|LYHauX3t6^9GOjy}`9iTP*z9ZGJysJTIEsnR&m_*zda3PB!zf#mq<59Bbii_VRq5yo2Vy?Wb><>l68X<H&(MEgbu)*fDG>wKJ(NbG%0o^X}90ay`w-+<1St=Q1Bp4F38gzwc<t_w{aW9OrKgr}1|_S!L;uKJCR$3y(WbT$>R|`<G+GTITyBX@9o|Z~rwg#PZjZPp=HPJJ(kTrK}>a=-JKmr;`e*AH%)>>16MK|J|QXR;lp+{nN?$vJc;;lXrFSp2#Jn7nk}RQn{d10eDe(ab)Eskc%Q0lPU%O3SI)a4BQ`H0=Wd1r}7-xkJ(Z`LMl&_S^%E~pN;G%RZOTqS(WWbWtS=r_d)hSO>wkid~X)GAC}cc@bc#%hr;V1XU8(i!K)*eLk@(8B8TF;D*MTGD=AePUKTlz{9R6|kKwtHKNI}BeDIHvm2CL^XUK)5vcZeOZOGwLJ=AuV>J9G&soWFZ1G&CbJ*kH92FL}ZzL5GHo*(%KsZmlR;G>a8AP<L+L>`Vj5k3xiBJw2oWMp;!UsI|UyasYzq27NA5d^P|JVk1{R1|y$auo7Z^m7dQrCdWEjXV-Q7I`G{I7sF3@Tth-k$;g|0-p(=iaZs4Q2BSMKc#+y-$woo`7-<_veG5|Uik}C{R_0G{3Wt-7qaqe$or)ZN$rKFBA<{tDRmTn9C@moqtm74Ln=EVl^4KgAP<%rBK19_@^DDyVep~Iy`*|e^@mg*1gSg#-UoT2)Fi2&A(fXxD$j%egd8umTq+J(`AT>K@(N_dMoEp9ngFT%Bc$?p_!#7wQnRFffmB`wsk{h28F`9Sl+<EK<rqlih45*}tE5&-t$|ct2dTUko{0Q|)CegJQh6Mt@>uvt<RwzGrRE?jkA+l@hR;R*PO7g|1f+5#r1C&`Kjg{SXMTcIo&X<@oLfqrN^?Lee*&rO3;z^Zd46PH<bpz-hJ`31^(DL@@|Vb8!1E(#mdYa337e&|I*xt>&jincoC!H2JTr2Bxt>L&zJOFNEcGS45WEO-A!HjoKXRgMYlYMrNaX~KQ#8gZ8f*f51@a1vugdqN?n*t9dM<TCDh*Qk59kJtE4T1j<;VDZ6S@WdRPb@?8Km-G(4RQA+{LohvE~jwtNa9?|Ath42;D)Ay1q-1ItD+2d<^+Kr1C+0SAFjR+=Z<CHSz=GSE#v%ek#9@d>`we@)fBwQdc3B&tbXBFG4C`fS*CWfP4ym1^E>6B}nBLkjgLNSCL;LyWr=LjefYWJ#L^q<=0K^tNaiAU*sK9+XWxvPaq$HZ$LhTydS;}c|Y<tcs%kp<RtiV<Rs+1@U_T$kyGL8kyDY6!nYzHMLrJy75O;wY4|>5<p+>YBcFv-J_+A}yhFS{=bc1820w&+2<v|gzD>NJlPV`eD(jHSyWmO4yO6g?t(4j<6$`1n2{oJ0#wKv1&COWOW_;gRuF9*WhQf!zS0WEX{vIBS{5|pzNabblO~}iTH=6pl5xxa^3)X8Rd@u4w<iqe(<Wy|e!|>zC$Fa>0Ln<5lj>^XVrSe7iS@C{<RQWvoB=SjYCzTfq^|!6^ypfJQ4p~X%yy;jfFOte9v#(Si!BV-eV5!_6{uy!wbzYQSPWk}p<<<EQUJkh&YWiV$YB`_4=OHVpoJab{>DcEAmdZcFRgKDnq%z9S86cHEf>a)i->bU8kjew$>N^ARS><$6?*#i>>2CzPz-Pq;>M|e;<n-{5kkcb)f>e$a?5ZD;kjfG8fyfca-KDz1!{7sv2ckb=;(fovAeFnp-y(NIc8K@u=74ua?uzfLTve)tRC7q>mXONT;8l^UAy<YsN3M(<EY$?wSgH}cDLfcC81+pdm7Bp^A~!=0fmE&nuZCO&xe~lGawX)irOLwt;FXapqaOjLeg{A*SA;i4u83U0v~CsP<&n$d`zp7U$|kp2c1Y!{kjicFdsWv4Qn?*meWx8htDI9RH$0bA4!93ICvr|K&j(UD3p^`w7Uay3%B=*u>PIU`<<{_a$gPpvOLc&EhPOjjuKLkgyzh5s{7&Ug@Lb4BDt8p`*G*;RY8f4|tj@@t;GMBuDq!5z{C5bR-x;LROO=IGE(1@8th_X`Km03rY2>evOF}B+Ul3Ck@N~#KrS?cIg|9;1EfoV61FmwQ{9+}kV0eAxVC3%bw#eO)JHp!_cSLRqsay|IxgDf(S9n|GuE-7H^^qGQ*Me6<u7z9~QaJz~h#Y`iO{xaGHarlyHgXGiFmemz9`NqSJ&-%YJ0f>R4uLmC4neK~HO2CqVqB_0_0ZqS@CNXD$n`LGDhElmmg)wn+yUMSxdU<&Naeax&EcKkt&lq*hrwGThaoqE2O&2@wnHj^E%gn&F+2!42z_k~sqBDMZV&H(+#b0Rya{q6<SLNLRpE7!t0Gr4t#d_4<?2#3;i2&6$f3wx;GK}WAcw=lki(H%!kZztM6Lt3BZo9emp*TX|LMO2c>klGDG1Ad4&eDs>!Wb<H@}f>xgU&&G|8myv*kf2J)O*R*wv^1014*#Qv'

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
