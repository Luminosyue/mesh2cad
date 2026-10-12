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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9f43d0ac857541e8a3a92e20ba284c44/part_004.stl', 'relative_path': '9f43d0ac857541e8a3a92e20ba284c44/part_004.stl', 'source_sha256': '49442b036b0c50079c8d1dcbbecb2c0fffac7fe3cc9e5b1825edaee06e6ca507', 'input_faces': 568, 'input_vertices': 375, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24501429498195648, -0.13591822981834412, -0.15056908130645752], [0.2211010754108429, 0.45884549617767334, 0.13214507699012756]]}
GEOMETRY_BASE85 = 'c$}r12UHZ-zsF}m1;rLcMGUZlfFPiPu?vg6iy8~oMFde%q}VZz3iepAi_ygj8pRGaSi#r}CicX*8cU*x7)^pT|GmH8cVTzld*{6KUe3Aa`}uw6H+Sydxn*WBAw8_i*-QLieJRsr{_1o$NfM>9WG_vLh)Wn79ue<1anf{^RGobBpGjBs9?&Z!R3%N3W_pf}h!2nRY_0Ze8`;v+N9`FI6PFMdHgRN3+~^45cMgk=k1+c2QDKuJjB&$&7GL?O1H63Hv(*2`|0)@qV9*V_mTOeG*`pIer4?i51{p;?ybt^SyHAp;d(N})8#z$EuHULT!Z+;qW&fxz<x7t1;)So<*@%4U+(ydRv}&+~>e=MQ`949XNVnuCQ9W}Su<tbcxKO=^k1Tv`Tz&Tcj-`4Gtz+Y;o(XEMKl&M8cVXIO@}peXukn!Tkq0zhOzj!v%>IIbl&`zFliFiA@#!k(M^k&$Rc=qG>mK+(z8v<1^3{<`mQp=wCG6Wg;QEL6h!wuvct88;C#W9nk)rv+m;T<)_1~;a`3AeQiPX-$YuO(>oBKJSMIZ9lr*J*<hH^i<Wv&#ye%eyb&-9@BH4`2TGxz1oSNJ~KTX&*%#xG%iw1M*VzRSO%`o}I}KW8Za-UVMTqjrv7$bPjd+@91Dx~?2Fhp&5M6188leIHHNeHz30wYN|`x`^jvss7v1oc}zP`|Xu&3ib2#@$BDk&EsKjjjq(r^rl?T-Xf|;I$Ae@+Oxrr^Zl!`pLUMgBPDrre#T{PPvxC`sh*#<U7^^$Wey#;Em}nF%t&S5CF>ZqbN-5H)XwqC$(N;Y%GVqWrtvIAE@QvKRqp53FIHIi)<4nj(sz#!qj>02u77qz9-rBL*U<0nv551N=JGf{`(wvkbKkEf_jC8YV@QJ+u;0avewVg#U>J?Vw)46E5znc9t@|gcU;k-3`?am9{RW?2q4c|orf@wEHgG$eq^_~>*N>!n<TrCiQ-A!H!2Z?{sz=`j^XqOL*YDbn$Ft%6D&cF+Ok}_3aqj;gRK2O6LVYh&JyXA@deqvJG+)#~4cSk8K)$x=F<NJ&)}G``)tmAC8hSW|=aD=6F^{<4_7`h&&HWW>ZqMs;v3$SX*!Swl>%h2?Q|NcNxUxTDGS~0r)IG@Dzdo79gS`1ZjW?ZReQqb#L%p-p26JD!TAuIkDx3B6yQ;fz{=UW39>ZVmYc2fL93KB8!zf>}b7sF~5nWeGEoo2Vq`VXRd1H9~ZkwDy^%Xntb$4vwb!P6sC~8-ggBK}25q_2WYthQBl)of_d}&NjF7;2nS+s7;^W!<cmo52{A%Nz)Vag=-4<z&WAA5lAuP%Bb`%fFOzcz)&r*6<V_A>_Yd>_mGtZNs+*DV;$<1OyznUv?IW&g@pp6}(aPba_PP_D;w4*f3OvAjtXza7Z_@O<u{$NmBIyB_yvKP&JU&qs{U!h#EwSNtpYL-@X(l&`lZU%oK;GUe^8K>eewvGF|RJFTI9kgGkQ{?Xg4CtofKC12xYyPW)&DV*<eh3D6to~vp6XU=DTc@nP=35C-ro|(vghnYMMFK2v1zb`nJ>%Tpo=bg1ak^CA_?B_=FzEERjJe~K)NcPul;_<oqV^7Mz5X$wRs>1zHH+>S_uT?o`DewI6)P7yLVA@aBi%ya+C1>z>81f7KF75p&&i{ET_w&uhgXz3OTF%e^C7bm1sR`5%*JIC6zDs|;?jfF!+Vzp_pWj3In#@MysD53=e2S}g)l<D2-zM=mEJwaH+JpU77inEJbScTBdirkR_Fs15d31J09_Rbfb@kIOM9_8TPGJA)47#pv!iGqiU!ILmlm9f9>t8-FneJB|AM)jtF!Bxg=egf(yx4Etn|#f|X0*Skf2&WvzN4Cbr&awZ?^s=~|L|k(&nMZ`PEB$(uE%vWk1O|+lj%BEf7AI=z2>~`?TVR0?K(b>eEB;Y?*G88<LG!M`%=F5ed-sVUVB8WRwZ!$vEk%P?}~R(yT-(`|5G=<Up_YB)X&S_^E|)Pp7OPseK>#dZfb|L=(Ub?$qU+Fq@fwS?w?5IeoM-xev_J}@%#^8%-5N`fcj1UMJoH!RPN7$&HQ|FXd$n&QYZc$Dc*x9Z{QU6tJmiK{M>&X)qi(5w<mHN&%2@>Q%QHbq8{Ft^*%@EQr;^E&YyH)3mtc`+Ztr<hm>PKy*q1{`@DawdBy9}>A~|UzPE<`!Wdr9@2pOyexBQp{fm`&U(4Mila8p%&mWH-Q9sKSX2#I{+WMB~`CSM0Z~QTW`v1}%_C1=fqy98(-$xp<i+z2c4RqZ{&-PRP@IU!_>&|k2PIIK^Ms;8zuls%nxj#KSQ~zu2AG2Sug?x40FKFLXe}9er)8jaQSI1#=U8|#9f1y47PW`%uN2vW@?_~c@$+y(+I~Qcpyg0C#{VfK%FZ!YTY2DU_4(0lvEa(0G;Kz9s=h?Ae!<P5uqTB^kU;X2}e&M-YSMDSAzhQMWkNZ)7^YL|7b9w&zvhR_@<N2vq99@6B#Cg9y%c6Sw{xFF8;o~XJ)A$dd*sz;owO=UvkH6;jo%KCI<MU)q_Fu$hP&?JPBWV8CSwi(nP0yrLeyf757XIrDo<A5@nsM#O*GCug{hE+S_e<7%#qIm|9{Kt)=VNFd*Y;(9(>eBA%%uCJ+hEWBtmS;azL?1C>f#4S$$wpq^BZiW{Z#tAl6>jXNnTHW^QZf%jR<Fd!sH$F`=2a75M=HLzN7t5{UVjdp|)LX^5tY_e*Sm#TtxS0_%BDy@0XkuzmRm-eDbCD59vN=^T$%ZYFY=euU$v|YQS@g`e{}6(+_PX{V*sy$lTv|XAND?=JR1XF9`nQquj4obRpEAjkI)JDwe2UG(mBE{U~qtw=Q2n*Sr1YDf+!r7apSaws++9yV_NL|LX7!`BH&3`xiUWebKEPO1>uW2={Zn52Hv2JCm>f){ob#l<l+VI(si3r22P0<8>)&I*;eQk>pF(E%-g_&smG<yzLVEssw&+-+zz#SvsyeK)UG~kM~XbB&y%7FZ<i$u+BW9=PPYRNA{m5Q~$_eZ-VLf=7sDhzxj82>3Ta}L{Y!}c{P*#j0eXkZheFIEt^y9myDu({l8DP1)2Lt@6djuxmTU`2aWA6@@0pPbiTp5$pV@ex)k<xyssL3^Cwb0KTRiJ(`-`##o5+Ybe)==xc>Kdd7R(sO#8UT&x?Kgd>XI%*Yi(X_+EGQbiIimxc%eb(D;?^tf%_5O*3@nz8sjw*KKfRGii7Z``F*5q044dyv>U1S!&Pw<i<=|ujE7(=eq=)p?+&}pWCDQMExa=(C()D(Io9)kh!03%j-jw%<VpQiTyL9wo^N*p5bxSHHZCxuGCI-SmJ(jUw$!+eEq!2`$+qGvp=~PKW{rfSwj73YtQw>tUgQiR|w_jk7vEVC%^x>Z8V;|-tzr7`7>H<qI!~c(|pt4>_)z9H-(?ioAjgl<=34!UvrzEgO?`enEUd$>F255gsplD|6~?DhigA&W?9rDSG-2;Y~p>C&Kr<O<4jtgLC?+V;xOJn?oDMsdE`avpM^L1{%n}cezOz&9C*%?=ABff2m4X~tR;U*gIu~VDV@oeTaBUTe}ijneoi;}&!6&p!J%ioFVs0p_f`JA7w-?_d((cWJKl%=S6}l!aI2pa)fZireEpdS9v=_q(D*kT&8B@t|G6@+GfisI`<i^toqW^tl2pN&o&z<9LutQ}QoHeU<CrL3A8Oi?uU|8a@2j16H03{u+Qsb*=jW7FIka!<PH5T3bAmRZA+OK1r_uY6Tw@hKUt#>{3S-DOy_ZRS>+$~IWdZFUQg{mWv$}l&%?s_3aqM@V!sD>Sm)2d~@civm|B6byUgdpB?=`ab0P-b|Zu}l?vwk_%pQqvcR{!$86x^>B`EUBrc$N0H<@Ipz2kr;mk6T$+@qD$<pywYcZ7TV4#ie{-M)16rzB8neuNuMoTfGV)<geJ8N_yxP%?Hh-ZF%OtrqMfIH}ucEDGn*wNXMs-rFBVm8kuMA%lnFHUD9XYu<$htK4RUoPqXl6mA_8cUE6&NX>SLvzfDJ)ANm<H4q5n*U(k5bRawgG`{n|AUX<oX(7L4Acbeaq3bwI7@i{%O=$E9QHuvRYhj=}4e6!!&*RQz1?QC{tAJ3O}>!}|9r?j5vZCi2ws1w=myn*h&UfYM}OR3+uJ^xOJm)zg|`mnFtL;J4gjH}+l&v-%WhU7lww1vNR9<2|$fYfYrUw(6s{hBXn-Ow+q%lS6DX*{TxZTgO`|LG__XG@j3vi>uN?~m<1j+5%pbBua}6@PE5v4j1fKWUxO1Rv6y`*P2{mw24`^ZwIj4*M~VS7<y8iRJenlizGR`G(Qe=s855+Jo!Qoks1{AHKoQlY#i|H7$#LgZBsOSMBeA(02$aX)@ODTQnX@eaC9FZW(4*JYbPO?H4}3ap4Jz{FenZKQyflW?AHa^8>X@Q~$Z%B45f`M!%y(b;=^&;6~p=^+h}N7XB0!zju9h&$IB`H0FKW{*I+T<p$3?ySn-2z8qkCnvUP?Wa<C2jQ8LEeipv;SG{vokG;;aex1(+@~7Q8ZBb97wsaq*4^=FD>HZt`3m04TgM2HB@8b)*T#I@}6!U%GxBrwye(p6IpPIyS$1LifRD<W86q99<fAuc;vd+WuJ}xL?f9%vu^L))?FJ3p2gVW6OH7SkAmv%>cSokNJa{kS?w9e?Z+VXpRukpNo)>xZC?P|7m2l;dM@%Y>rPtWOwS_jBij`LDqG0wGC`CN};9+`aQJklke<9x+@)c<pdeZ~CMYCf@#d8E#mK;uqZ-(e@;cguCA)K{!CrM_aFG5N}MMzhe5^A+n}sjpb~w80bDSFE3!usrq^>$AyMuFoc4xjswh?{Gbe^<TT?Bm0Vdq|{gJBkHv1UF0kFHIuL0*G#^0Un}($`<nXnX|7+f&zgMYKC5%c|DNw7@9%QgVf6l@O-`lfYvuD>sjql`lk&eKU-=xU_d3kJ;(4;v-(^eV(~w?~@(qzk*;hQ5YQL&S{i=K(Hu=iu;Zk4mJX~6j;(1uw@4~*~xxLg^JhvM(bJ<rs|7*3k*;l+@n0)2?g}UyqoUeFKkxu>1zT$nS)K|Rk$nQ(Ie#Lu}{&nnO%2&LvnSAB@n&zjaoUeQzH2KQ+L60Nk|Cjg8+*_Qlc+V~M74NyaBM;bDyf5oNcRfPB;{96M;mY?%`TgOJFP~qql*W}dYbw9@oBSUQydGMW9H;R%W-!;I_`V^lM{@qR7kOX%^&^jeSDWM9|CZlXN`1w56=}8y`zNRK_ojrvQx?9D8;{%JeRIuyIeQ+j|H1g)WXexGM!v3tf%?U8|0U<|nL*=FQ`C>YqofVxd8zmwRq89gM@g4r$d{kBp?M)Yp3k)K&kyAJQkcT);q#?jPl6-u51Pa({C@49!}(X*(>T;uHSqWB0Kb!z=j_V+?BH5Db6;-g$@Ai88y)3kjw4^1*@t}1<9S^uum3#u72gR<eZ_Y|IZns^qgV9%CEtg73qPQc*V|%$9_R1uXdEfOPwIT?u-~hM$Hn57l&>4tmwm-|PF>5R>?^*D>Q-#d<@sp&y;mKykA21WVfpMeYM=6ZwN&m$_Lbka*DU1cImP$+QeW|XUK@U$eZ}7+v@XSY^g9)Q@6cWOmwe^lM+~WQKJ{ba5dM3|qG<B9@7K_}FJ;x_@%&>Cdhb;~SV8kp`S(FhrCyhLKAQbKF~s6u`9x&z@l)3`o?<K&C3`6{%<P}|2vhuL(*ORS_>67#zxpRWUo~&}|NSRE7maQB+gM7Vl~l|n;L0e1>p<&*>wx{CUx9`80Sg@j_6N6y4g<Fa2SK&qAaEyW7`PL-D|95dE4U+cD7Ygy5IPVX2yO-K4Q>T)3hfJS3T_4+0B#0ui6XcibTGIbxC3+qxC6KgGy>cO+ygoWEOa!u2e>nIIJh%d1N|DT0k?pLfLnl@qX=$`BDg<vELiAxaDVU+=mhW(a5yvu91f0zP67*^2#y4gf<}W!fkUC=z@gxN&?vCbUf_P<HqZcY8*qJSJ#c;SCyDi6iCO3y@F#E~^gOr_oCEz1oCDqfT?7^?gExRzL1%zhftNtzz)Qf3q2s_p<H3u;OQF-jOTnw5v%#yu8=(uqLN|dof^(rifOEkwQ3St55nKd44K4!z4m}3`9sCfwAN&yf0Ga_7dI0<Y{0Mp!{0RIEMeqygDew#MD`*~A=vnY9@L$ji;J?8Cpa?F8=7WpDe?X6e{{a66JqZ2{Y=G_q3q1rjfFDCofFFaOL(hPpgI_~0f`yiVUxTZvSj8S7SZEz^Rj?ZB4;I=QtOk2PgTNkOUuY+=FSs$ZD_CepaAU9!G!X0qc89hCyMtYzO~EeU+9-k@pv}MzU}tDcu+Vm3XRsTz1K17hi6XcWv<tWq*bmwREVMJ&59|%qfW5&Dpe?`+z)sNSU?;F6ieOi0Td*tG3q^2yXn(NKA>j7l?$B^>cW_T=Bv|Mua8GbIXehWFI2hUwEVK<c7~BwAAKVc9L1Gnav|yoy;1A#@&>Zj+a29j}Sm-Kn7I-&w33xX+9l97SbSXF;ya&1(ya${O-3S(%3(f{Vg}wwo1%E^l{2BTd{245%xCmB3i@>4?wu1f+7Dcc%^dVRj!R4S2z(OB^MG;&c`V1_J;0h`(f^DELz@iAYg}wp{{R=FL;EK?Hz@iAYQ*jYo1zHRiMQ}CfA7D`ge*ygsEQ;V7Py<-#W3VWKYeJucMG;&b`WpNi>#Ja)YOqibaCLA^sIRK5PG4M8Xk)NYA5~d<e9(5G?y9oi;*Q@c)J0YH+g;E%LTjta`l`07tUqg`kA*s@%KF>^_e7{OSg4z-?0&i7-U{_pmECJkRoQs(#269UNL4mw8evQc^#cp_R+Wu6Z;VZ$4OC@gRj?J*NmVws1*@Qrs<OEt*fd`Ri#a6JRaG{p1b>8jsmkV{;P(<2!L@L_Jy>XWa4m2XXiu=vZr~>1FQLI;p$)-bg6*MVjkAY70gEE|9lR`X7S^wKD1v{1ri0V5PW^%+_)lmyI2-HHpD0h!2T##2g4-EOS7YgBEMtu&(pbhAOM*)L$w-nW8%w;g#2HJh=m+Dm9>(%DRKyyv&>*v8{h{5#-4O?&i2NqT5{TFj+}$jv3H-)TH8{{L7U~SGZ^lg!i}Izh)B^h;c1BzaxjtscTN+C%_$}f2!1KcSK4vVmF0{F^c!FCYHXZXsX<;mGIMxDQU1)8n8@MvG61Xm6QNA#ia$q;al@ON$3zeW1jm63=wt{|vV=9~@{wog_p0%;qf+fT%cy?eroFiC#eyNJs4sm&SmBHn~m2lh{$E)I=REAdzUOnWA`qVgP4_^&#1QuRH#DX25cHo9)In9vQ6fC?3PzP{R#6p9S*B&f9e`o`6d&IrKy`jBujw$Yd(jMpaM%)J)U@RS>9gt%>))6c;1lq<}I+>l*#_U)p6yddnFXFyX;dM5PO)Rt@w6(Ex0k=hLI@Se6cweD-7>f%$4>PY0d>3#vXccfZa0RFhxB}P;MX-dNnuu+{)?jPoIKr<2c1J8qb>!8AFJf=7BRBxDD6YtHhwlpY2a6)cLJhD#;_8TNfQ8yZ9n81^;x@RpFF3#~7V3oJjduDX_JBH~Urlix+zVfLZNaU<Z4g_deYQBq5&bq$;xQra`2eu+1|t?c2rRtehy@P=3oi<>;0UnrrXdzQ6)e03hy~9F3ojM%0_YSRO9l&XJv0@Zj9BPo<RyWHw+^w1lW|@W;<YG(cc2K~iLws)mvC$+Sm<S_IKIm)-i5Lr?YxI`#PK^|;oV0p_*cY&e}*sOTVUbcL@f9&Vv{f8AECFwCvnWgLXSX2P64<8{#Ixj_#|R+{4n@1jtkZq%L>GY5vRdh2~Gox`o1xiIfz#vUWp?76mSaig>EzBHHby-TzGTgn|L1LdAP4@P`2aTHSo9Nex3ubMZ6tF_<FD&=WYX^gx)mcTZqqr^<YuwC3xp>FYkbbpCIvA6zz>gJP#!a?TSS#eqXq;jD|M}aV)$9Gd~vjVaO5QM8qbZgua{u7WpHQBaTNSHt|H<vv0uSyb;I|$Hzkx!6VG#Xq-31SVD13i+BV|DC*K87Ilm=mZ9(_AlAYgV&-d+AA=m>%|dKqp)*k?Ab%!Qv~d|?!QX<HfoCCJ4i?^K#3mNH1?5|uy9KH<mQ2Kg_kuIQn-PBx7Ty)ag0CVr@m`#J1@Uzh!9Sr0zJ_uY`8RM(cp*JhR`%Ba)Bi$W_Mc1-ist`Az4A=UKg*e)`P5if=^yDrdXyJ?zHzg+q5(?(ieCB;2`^6n'

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
