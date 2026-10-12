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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_018.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_018.stl', 'source_sha256': '6a3b5bc973d03c95b6ab95e6d8a9770d21a93c4448bf06d81fb706e0ca8ca652', 'input_faces': 587, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1397845596075058, 0.23731693625450134, -0.023214250802993774], [-0.030716687440872192, 0.4254430830478668, 0.1087007224559784]]}
GEOMETRY_BASE85 = 'c$}r12UHYUw}lJLf`b7A##W4o5foI^RuMBnWkghH1Lg>VS<9S7MHF)zP|N`Z$AE2)h&hKA<Ct~SF`z!`?9EK~zusHxt@oI9XMepto_p@8Tek{D|2EmOJ1Y1pt9;oob8=i+MbU=6;;2N0g%9u7Gc2O|;Gv^zl>FjrUs)RC8`#djvyBp^jH%QsETU(4rTV%`UcEglx#}wQ9uhu0y!+tLA>qBkG~cKDz=*I+Kca8<p<$VyE4$TkbJe+3an+5}{U5*bW|m-%e0=0^rmAg<-D#YuCZA(#HC19$#Mf`C4d1If{AVl0H{^B`-}rTm`09o!;u|CDi?3_?b&dED6Od<DIq~(oeoDOlW`TX0ZyGlwP4XX!{6q48&LO^Tcs}vfFRtS2mmN<Qzu$=q5^wu?pJ?YT;+yuyOT4mnviSPM>4@*r8hLV55nrv>UVQbTqxkx--;y;o`?V5ZUn^Sjo8O#8o}qcfS6aUmUk&PiK;}8{GD-ZRPsKNuekFPIm(s=8c@0JWG0}*Bdp*fAzrKZ?_@*2e#5ZlZi~0xuLY|R>;P*BlzSzF~GQW>6{6j;<H_Sh@&&m&pMIPS`l1Dk)7XJEesNc~U>niDr`dO#>b1dS691-8~Jp9l;Ql}bPKz!94i}ij8#kw9jAb#0nT$gNz5&tzO;@A724?h=5es$Noy)y5cycgy72YR9YU^Dz&gCvh~E)Vi&TozwH&kxrz?F#%^%f#2sP$Z8&;HvaT-)f@xrZQ)cXWUoJdv&b%=B`W7&%1pkk3MJ&<_#H#ey&bNf9CW?{)<JBKlTmktk@OtP1c~#0fSIa_0I6i=9hSLpW3)yb$%D$;B^E2sksgFc4&=t4ZDpz{&tdIdD_%!UW08k_WvGd@zqr|aK9A%19=AK!@Qqvif>H4hCVcXxkvIp+=jm0$%%EPJ{8{(ZzK72&PkYe$Sv`eD(I)~uWFJ<$&&_u?P%nG6o!3U^o;oGx>FY{eYMO<@r?!ZT(r8ckL*LdGw-{?QxR{s9R8}sl1F#xI{I8C8ufdoSgp&{c$)a;HK@mY+yU$QHE@q*AIx83kf(4j<S+0H^Nz2A>ry@hdB(oOeUaD-d78FIo}nKRAKpXiH}z?TdMY=^_1f*j^;Q$#H1!JhTOl3x!<&4FKeQJ8zng}6t9(wBdfFyqAAbL`&&t2DRN@VrR4ZS(l#1)VNQdit?m6N!t|8t&2>axAy7*?}ckJh7(~xJ#M#S&CdBL)u%82#I?^6$Tj`@r}FNzai|GN|V+58Uj6k8&`ss1eVq3%}XSrLnQuTDVU8r|P#>FX~i;yUhjw2C*KO~Se^4nd#SEkqvo+qf=8%3@u9zNo+aH}rYK1mwBWHqo-rhW#TYUcKE4>k4#3{>hcG57T|b*L}meXWUr?^M*AS-`Fw-)>|kL{_w_Dd9v2~kN?{Wthc8P>KW?=e@G<a_l|<!_0evrf8u`Bd8GmB$#F$|Q-x8;)9xnrVTrTi>joS{`~zFet3QBvI}cnh-3#=&({AyNgQ79-k7&f--nrXyKPa1=FmJW_;wvj#Ay3o^>?`-V@Ix~Yzak0#A!qn6=1aWp&=$;lrzq-FucChU!pPsd5d8k$sHgT$?4M;ncS)XxZ;{9TJ+5!*AL5&?D5$5#V?N)Xh;OvVK2g<qxR2JKLj0V5R_B8fxCj2<c4?ONn`RFXU%x#e&GNobDt1RbyMs}`!)(m!-bH+Mc?R}F-G``uXfwp$E{gcir;w*$UDTPFTh2Y>xf|%iEvH?U{ZU(lqn}A1cS@cq)2!-LUpx@s6kf^tI#xS@_-#kw`!q$Jr}m4lHXDTe>-|tqM!fj?l?Ct|;d4!087IDh&k;3!1@_ydq2il66vp{qWIyhs6M^CzZC|5r$<0yES3T-^dLMZlKH$A&xf}B6`F!Mks^44<@i8jy$MkHNw?iqc_jObBb74p1FPI&Ea2Y&*CxoE>&VTI?zXs#8eEY59t93qDy>BS~3lRURyyQ`Tbi=wj&D&vhzhu2Hee@IG;E@Y`dy|3qcCN^C&jru-5<2ubunOWABi>lL1M-Y6E`HXzWZu^j?;-OGh_77q#k`?8Q2+KE$p7O2?u*Wz*w4Asw~N2I8{*H{!QW~W-!Oj<`Z@Dcl9hkP9@lZf2l3U<li*kHYPDW9-)Q6?QWNVvoFD6L5+=S{(H-w;X*aR1G*`sebwoc)B_sZcGyHz{Q2*~Y_e%V0o%qI{CvjbDPNGh`!s6@gP^bCD1=LyA9(k7c#C{8IfO$Q$iLVsIdy!J^wd7ZOz27Ez5^rH$zYNGf=DGOB$EaV8>4f#pOou=H68aXr7V#&}il6nKpzMFV$I@5Y*`Yt)TM(amYMbSKt)KA$efY2s_4H@|2lhq0O``awO2tusfltU^W+UcxkHEaMQ*dtdm?OUV0<MesXaUqeeH`M8*2lUg9>e}Q&{urJi1%36ij+k3qaFMSrBMHfRQTl^qn<VuP><Ua^uMYX{QQ{L<XsSckPG^jTaS9|D`Njgl|~<8%VNDZ2crIU_UMBS^D5DE(TCGNwo3dx55&8c!gWmhCcggOcbw<719oFS+!o)|2lMK-CZZ3%r^Ppq&|zIOyGy*1yh?o4`xW|mVI8hZ%5w3I*U&eU>r3?EWE|#Q?um0ItugYa#$w*Jb&&sAD%SgLGW=XqabNcj!+P_K-)h+h^PQ_$Z`+=TUzr_w)YP4lU-gA=Qy1sPBTvNNc0rvyuk<(WNxV{|kX4<!v!l_UfbUymf0~fTqzk})=<@;o<0hzQaS-mu75Bt96mUlVnod}6_C4aO)AM0p?Vhz=wD=bB^?BSl??%M8Sc>?bwule$Kp*@TBR=c<nr^vp{|=gkdJ+~`zqimgoy7H3{qp0!m_1&6V;P*cs$mQ2Svt~cz3TE$=+EJP$iws5G$|DOwvrzHFnm8^=vN2zk17K{rUBNKZ3+6hq>%W!8by&OE^LeV2eYFdKHsyRr^@@co23r}H(@`p|Nr<rKTUxu@_czEzOGGe+!t^9;<^-hD1O%S{h#m0>1UlYrjmh4mcB6x``P^WRrIISeewVE{82lfL_JS&eU0sJpbsmyh;R7j$$e<IOZ+oSQP133SZ|36a$VH1?U5%9`^PY?VS>~%#Si|X>eyGo8+Tj!#%0an-`^p9P-0pkp5MRd%5~gp>FYD_-eP<@0O!N23h2X-hPdw0Ke1lhQkyNWqrO>?)T6fhwMqO~Jf}>xN}~RrpT#%SVVx<(WxYz=L&Wp>rH151{QE=VXFYe+>j~H=MRtg<pY{^_eB^TYUPkfN)Yh2y&oQW{{SxHod9DmE94{KY2>GwIK>o;E=+EM@n=JQ_+SX}@_$x;t&uJ%I_oPy|UhAW*@|YXDAip^Tb@E)*r#d43lr8)zzUae@wF#EKX;3Hh|8?tltUDt?@@Jj%b<0UTYPOf+>*qAWeyIHs`@HM}_&0MRf0sgt_qd*5c^!2Qzv0gnBT~dS-3h>Y-#fwg9)Nj+U9m1lWvl#po4)YfTf%Q>O0e{eO}e7bQ-`Au!#azv7VeHZx4R?%bbrJL`5@lZa+PSjH|lJJeW=ubk99q-VwGQw>Mil=oaY-Qp3gNyu{7Klr!R_ca0^5~>n}t-H_nQ$ZtRVH(yj~Yd3s!YrB6HL&%HEG{7)%}Z&(`jG~#+Q4v25e*#~`2-5F=;8%hp99`hR1nco-jUvWR0^R37At<zY1{oc{YQ~V3&ZCiJvRo}kz&wD$#ZM3{DrmS`KcY$Af2<EN!C;B;~H1bDwME>&M7m9x_oA~CvgAjkaSd8fA%^Rej$sORInvZ!;uM%HL@5}SK{A%%U#EGw_cR_!8o}4BAr#Z;uh4W2$G6jA9F;jf~1{L|eJ7V7A<B@;n1g<M!sl@yB+hEye<yq=@(b)mWGbs{&jMHpO->^Cg{yv)!$)C_1@$b+dCEYw!^qL#|T*2HAO|h=W)lk2o8TvNM1%8*G@v`27Bala}r5At6Q}N9kBCxJK(@_5gv-o<?X^1cJa)SK&!5iY6R!xQ<u`vd9owoK{ufVz-l94B34E+4L`%AwnY)3slbK#Hl94_jffIKhSU|p9-FSYcQ@L0r`zu8ynF)WU^+;67oaflx=7xD4SxZd`iB!2Fcc+2ak{9G_v;u0gR`(scViT}(XzHa&k`1XzaNSu9p<o|mVeEqZ#`Rw8YKMuZnKOOz)<c>Tw7qgzYBBH&kqn;(`v#OMtBRagY_=e&O5&v?zihWWB`OVSrBR5ZxdhY#PFKQPDKlhDJ68Gwh_~zg(@W1>RDRH*%#5W!1Ik4^<_A`BB<)w(PzCTL*0xuBH^HwpvL45OT;v0sog?~3`i1_o9#aH%o-dB}-h@M}K{IAz>U3PP%o+~TF*SFyPmApp!khx&2Yg!`WZv;%1&qXG|Kav37e}lJZ=?SRkzyhA<E)yl+h%TuAul>AUF=0~Qy!ObW+XP=(>MQ;&cf?O;AEN4xlsum+BmefHsPoxJTrU?#<k_5p_?;6+NS-Ek=>Pdn*6}TKW4)%Mh+kZDmc)ntS|@pGus>&$hKUaTD!%d5VdU`{vq0ivUWl)}oe96o8m#x;dF1J^o%J;8Eq>)4;+vZt;e8r3N#Z;<iLZ0o%KdK}An^khA%Elf@Jp5-B|2&LI;;NIbo0i(p9H_cZJxtp=8K;avCi_oP-cEaoemwaF1Ls9e><{Bet%Ja#1B0P|8Y=H`CPH}I;(x|c`#h^RBM6yr>4TMP<5undp8o_@FmoG-j&70H%&FcPih+_@$p5`pR?oX@0Rtd=3i?if6`a1YyOcK-2b1~TJ8V11e{Cx-oSsbg7^FEdQx}Q^tD#=#$1~yeyi*7-}T@*-vIN{R}-GVA9EpEK8L1?Z$2H*K3oqJ9d`tIeq^1)B_bqGnh|*%b6paD^ob?%Ib)vqitjAM>l{2S{eSv7d&LZi^Bl3(YF`~()<Zrw9xlFdW;pMo$Yv7XVwm{)^SyX(cf<AS)))O*RTA|?eP1kjdWB)$+u7kemqnkK`op)MjXdri{UlFH6V&6qhkd&iDe*6BAbv$M{EExa=MS!k&wB2#Z>mit^sW3ezQ2`}J}V6!Q2(L++~?l@5<l$Q8p*@=G39)Q++WJ7=kSkKLjC8%v99<h;+u+|<oj5l^iw@{3-RZMS)EJj<tySVg<`Gyob&J+%j>9qOkF6S%O{GjJGz|bb}8A<YS1doyJbDk;a%v%_-N$MdVck&FXxr|#|ZJw{^{^r?3yQj_F(Z1fzz$e4f@Kcs;FmWnZ>BPBYa&F-=juiy~zbp&uUx5kB&qAFMk+u|M7W!-dFBlwdV!+`!2(OeHHbrN-|pZS#^F9D{&1*if`(^7x(FjA~=7h1tZUizu?zM!n`5b#W%-0A<xZRsQ-4xYVl{^z`V^yV;|NYF1~5t59C?+cJX0<tDovPY?tS3_L7RCjXa8@(!0CGk926J_LZgo{f~6?bN^rcNJkw{kN@wFbY#!0!B+YAOJf^qHnLad@YZex4vm{r+mV}-TT%naEy;e=V6q=Mh}x4JMD9)<K<-ZNM;%V?M;=C1$-~Gas0+y>$P=kc$P>vksVm4c$qT4P@&a-!bsagDyp$SGUP@j}-9%nYUPj$XUPfL`-Ai6g-bgi(H<EW#Pmy<%4^c0Y50Q^kuaS?FFHrB3FOaWOpOCMUA5h<rACUi~ekT7(eo56f*h_xa_!IRvvNklfp;wY@Lw2B+Av=&AspZLz<Ra8c<Ravv)GFkn<Py}X<Pzl4)EeZ{<Wf{Oaw&3IswcTDxiYmexiYy{=BQ6?MQu!OMefL<aXYFfxgEI$)s5VO>_e?V_95%3Rmpm?2ek^>gWP~xiQIr(ms*}&mt2!thFp{ELM=&lAy=gSMy^P9qAFx3vOQJXTlV~{@lWozH{_q>57Z~*59C+W`{Y;T$JA@&$K-p|i{yLco77X}o8(JW6ZsPPEOjsWEcqC9C;1rp2z3+r2zfs>p1hx&NL@!xByXk~$(zYrsVm4^$qCdY<OK2>>O%4wavW79$B`#dhm$9fqo@POQRIQtp5%e#UesW6FLGCE0J$r<1GOEw1KF2D<EB(^vZh|-rsR5=qZZYj>P2=Z*QGWj*Co4U4yVjfICIpdRv}m6uh-_#xB;~xS<~j^2IOYcmgHvS)>J=oYqCEzi0n`9MD0%QL=L6)BZrdvP=}HGkOxsmkOz??s1wN%<dM{w<dNj@)CJ`6<f+tH@>KF1>QeF?@;vHd@;vf%>N4_lax`@{IhwqPx{<tyypp<`ypp_udWgJ%yo-9Ayo>w?^#b`1@@eXI@@euF>I3o>@*V1*<U8ba>PvDu`8o9y`8oL=ReSEf<7bV(P#wtH(D)bCk*p1kv(YO;&PL8bElSQo&P6Rj&PC2gEltixE<i0sE<nypElbWzE=a9RE=Vp;twk<QcDDKV+3d`rv1{h2L-nTCCwr6qsjbNV<REHCauB&2hsMFwcI04kCu$3FCvtnL54k-#fT|}4ko~A0WIu8vY6Eg3a!YDma!Yb^YE5!;vKQ5b>_v8`RwTQVt5KcE)yO)kJy}OCMAe?_h4@+HoYW6wZD{<R-YfEV@_XuI@_X_N>OJxc@+0a^@+0zH>Lv1B@(t=)@(uE3>M`<V@_FhJ@_F(Z>VEPW@=0nU`6M}ox|y6p-b39=-a|f2O&}j8CsWsulgZntapY~}Rn$r3RphzUDDqtL80tXs81i6hFY;h=7_}=ojNFadf!vK8$f0ptsxP@MSx;?B){{M`^~hPzeh;cE*@IkzT8UhPTt0IYqn4yrB9|nWqq>q^IY&7TjVp6#T$Sohu1c;>txK*>cA>hFUC0%vRmc^{g{Xzeg~)k0G|o$PBIhON%N&l>(o`pMX>uKEZL+2f$aTn#sLjZY$W5rN$xX<uI5cig^(SlEiQJytnHoy&Og2#akPYO%)IsFF<RR1u@(^+)btE~GJc>G=Jc>MyI+Z+*JcT-kJcT@qI*&YyJcBx&JcB%$8cm)|o=sguo=uLSt|Z5hms2;8my_31cahhVw^08eZy_g9Pm`0#N2yoHN6Bf_JLEL-ZE8CCHrY&lPBxRDQs0rElHXFlkl&L3qW&WPMgE(rz0>^7&l-QD<{)cB<FC|QWNm2tgPM=54UO~AD?rXewxi}H+mUUl1<AJL+|=Ua+~oXJXL5dWF{&%M7`cMYzwbR2I5e)FIT})%QR|SKk=s(e$!*EMQ~k-mle<uZ$X&=G)NbSuvVlY6P--wal-!ltiQJXkncAM*nH)$BAP15=Q2odq$iCD@WM6U<YD;nxa%*aHa%*xMsu#Hpxhd71+>~68T8&(fT$`#R*Cv;v79y7;7pCSU7ba(?YVS<h`B~!(1^S+xLH<a6LH<a7O?^auO@2nbOMXUvNWDRRNWMkAOuj|FN<B}$N=~JoA*YhhQBRW3kxx)l$S24Lse8x=$=j)i$=k^XsLA95<bBj_<bC8F)K%mi<h9hf<hA7a)G_4w<gwJj<gw(T)G+c;a&Kxka&K}7HIN)a{+&bP7Sy(6P4(m!<i=DFa$~Y5wFcRfT#Z_uT#a0YL*t^#zwcEVm!KBl(Aa@mjO;+R=g{~!YDu!D<;cI0i*RUMidvamitJ3SN_Hk!q*f<u>O!taE=#RIE=w-Xp>cj{A##3lZfYKKZgLI|jdN1-l5>)CQS*^=k?lA%E~xzbK39-KV;!|LSx2r(twYwd5xFM0K8MCW)Fxz2TakUpZ8$XUNNrEnv@^LQxeL`m?n3TC?Mv=K?oS;;?oSS<Mv}wHqp73FqsbGf<H!@p)2LI({%ve*9kcyU|1A99FV#l-zvVv?|IgoP{a25czw>%#u7Ca_(!Wg(?V2mLng3~jI9FKfxbj~T`gu?'

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
