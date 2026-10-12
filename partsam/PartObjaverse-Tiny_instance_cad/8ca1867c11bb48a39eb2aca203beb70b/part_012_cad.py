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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_012.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_012.stl', 'source_sha256': '9bfb2fc68eb9d1b740324bc24101ad3bae6abfc24867fea247706f352f6873bb', 'input_faces': 759, 'input_vertices': 544, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.028887951746582985, -0.2863118052482605, -0.3031321167945862], [0.18888671696186066, 0.2559901177883148, 0.05349433422088623]]}
GEOMETRY_BASE85 = 'c$}@A37k#!`^V263}fH-#x288l*$r?BRkQ=PZZ@224fi-Gh`XAt+5Xpgm8sqC$eX*WtKZ;?hK{;65XUoq_Sj*e&;#o^F4FUbHBY_zyG4w^ZLBcXP)~#&v!ZBbM6_6>RPC9MaB5@xH82b^~n9aqEM7nDk@`R;uB&A#*BG7ZuEGEQdalrkI?tK_v#k)hC>;vOpF{9GiG3XWD95HOM_pCY~YL>JSsjRK02=dsQ5uK<adZ3F(yXy#|(`g9ituBYtp!J1LyPg8#t4k|I0tcwGuqJsjJecq?n}i)|z@(&0Lx$@zs%Eds<t3@7{|!vV7r-eD}J9m9qA^FY*IBYA@H@Svo4yn$P{9d{z(ldA=IH-mlm9_|e5_5?_7$>MC3Nao6+cSn=L+r%8P8xi#-w^PPV`m#?=!zQ<Voa~a(}AYZ9?Im22f_su#te6mchXH<Wm-cFnTsZxJ)hYeQWtG3LQ<(t09AG1k6zc=qQdp`G(@0@>eiGJQ~V{G+vU(~M-siphw`yFia&V6%T6`h=_|2*bWrnR0RU(|E;^830!yOiIWALNVv_UWk4v(llit$yyC>$cs6Mb>flG@r6j_opN+)W_%ZPfys^GxJ3|-lrpVU%lMWR%eipI@J~{QglBo(^$`SOKh_Fk5|jJ`hjY<7wG5j*e1(br?Xe;eBJNf{<v+vm@n!SzFPT;G++24U-@YMJl(%F-BzdRAL(nW(~}&k``)r8Y~#;;bKG9MnQR?@^}VfnJFbSG82*~P4C{CX`54avf0(UK)1RAYuXDwL8G1d7)?``FD}48t;n}u&-iw-HjKfuZ9+jLn17yCp$g!#VeC<CrO*U?(&&Dk<@B69xc}tJZw9c=qMN7BsykE{5BJ<ttM!T(kU`LmHS-$XjzAIvYkw0(oJ2Kxrxco$YJlam2B3-w_=j-;z6-oLyPZ?&rj<|2`hw$BZ_Db`GZ|*-ap%eA%`d+v#pZh#tO$teu<qO~3AIkI`Z(X16UngwVwQ!a3wt1NqH#AM+yKBVF)2}<<)p5r4Si!d5gs)WHVq0(O;A@F`evSKC*7FMA+vS9<9<}t733@xLFWatb?wjKPUp?DAU6wEWg8l8aSiPNxJ8bm`UyUuDZL4Qwe2nhLe_^kO`DQ)vmBQWAW%<H4?;}SZJJL!C-uJlA^Laho=lQ%I?(_VheUJG;^?VU)+uwqG>~Cf}%WB*92eZEo0-4tJW9Db3+UCn_U)=AWxM=getLtaW@|6}BvSsa?>;J-tgfxlo+O00s$K%%cnAVc<=f1h#;Pdh4zPWGg?i1TuvOa~+*QYXb%t*c6bG`L_O!;u&7OSt;cwqBA{_up>lIx56=KR9v*BAHA`s@FeXzUmE>s|Q#dJoL|b)0_8_7mX;?I&5)$G5i57xpXei~TB)*U|9VzNc2+IYF-{?8}qZ@e#gyeR8hV4@4H%?;Cu7=Ds-&@cI7CeRJRVI3-EXWA_*C^L&1P;l5c<&DL()xZ!@veQ`e(KEMBRpXc-YFZad$*K_@x{(Qlo6TCxv%&^so=M(OW=M&+Zb+UZn^L(?O?!8A#{q@}@={o6<?(^p>;q&J!_vn(z`mt-RZC#oEvR(FdRc5o{v**JgUwn@UznyGd&*uGiSTTLQ^L?B9=5^g{>3pOA?7qW%p3k4Rxo_rAxUoQQhdt*9-j2}sQU3iR$VY#b;jV?U>s0vsI(3bnY~-`=JKQ(-=O*7RvW};yQ=Q#zvEDBG{>6Q>9dES$eVXsX!sq+2^V}7~=idjpk8$wcovi<yf8Px9#rMbF&L#RW`##HkQNL^Q54z94FLU4g{uQ%%sh-Eaj|cgv$GvpZGV3^t{2-s@^Y;TmzPK*#booFZU-rI&`{wt-wGqqpJoes(`$75ay$$zyK7Vh+eevGLY=^zK;l6lpBYghe#+{nDQdj=|iuvY!;mDFzvV89I{Gj(&%;)(*@2{9|zP}Rf@b_2DH{V~u=i?B_YqCvm_u4>X-`M%(V41IWTjjR;-m5!|{QC*6G>PxtH)@V8f8-0sbzSdLVw%MF&Ro6FmXGmKs_dSSCh^sfuNK+zljr41+lL?2e(_3vY5nkd{c2dWUphYU#rU}1b9!|xy#JKGF56$sNwfIwXA=y6_0M@y|JpY`tMB?@dp;ejExVkO`R+1}GOfO|d?BOVu#Tr?zH?mDbgQp4tfki%_&N8q%vbl;J7M#ul<-OO;q!b~nYtOWdW6sGald);xU9dz=lu<Idij`aJWZdCr>E+HqqceZ<ME^Vy#Lzcw9Hqk6w!U>!}|F$-<vYpXZ2mFb@aMDo3@>j`b}dqtiH3^D!pz`1jdv30rklfwmO&eH0EW-;4fspv*f*FR^K!COqMKP_&i^|IyYTbkMMatp1bFd$@**htiPU{;YVfTDSSSjfwt4V)_Dmm-e~Nz-w()@`OZR(bYCseFIVQf!-m=N-I@FJWAEGZb7j8zR5M$?H_%l-R{DIKZL7!8Do1u+;q&t<*IF3)4PyK<-}_eoleYS6m&lRzS2^%N&r`}J+UjvvKdt*}N@c&y_uk)TYv0>)f{|ZykiB1PqKy3Mk$#!4hOV;LIij3VPrE(#dd4Y6JJ}2TGG9$=Vrxg)TrXReFMOV_epbcE&o7rJ^Lah$w6i{Gzu@zJsc}1fvhfLo_V&rfS@?XMT|*n{zB2yRJgLv-QSsi$lCBf@e4VJyU$Ug@5I$dr>d6a6{&QFSGM}$=_oetO>GcAiUoUF-y-aC6@I^h|h@!^x=)LFs)^%?B6CdcG_xfx3Wxjf7{Yk5@Ht1{kc}??VzPo)&w$*pf8Kj@jvppnV<_8+2`E2JM*3?+HLz?HyeD|T(Z24-NTRvI7@Oge<>4_{^J;LYpsJC-7rTvA^`|I7%FjG37@cDRpBkyEb=S3-8N%x&I@8-ySZ;_vj{cU>LT$%3;-DAr)_uKgqxia7T*BX2Nqhx9O!sqR)Qxc_hx+8uv=5b7pU*>x&-_5rAu2C0^`K`6mFZGAjKWRH}RHkv9e9JHO3+3C|clX_Ew9|ExU*>ySb+Wau#HSkhyYBmCzUQpZ*1l3~rqQp&X?~gStoX9M{<lXM<8%I;U*-q4Ua__BeSWaf{_M?unXf9<ZS8xmAM?rbh0pWV<A;6Hdf@YV+|}0mWc?LB@2_h|s!uka!sp`|NRRi)=1cf|zPx=0`ef_D^x1k)KJDU@tvAzW>&>0q&L>^Z@cDXHKiZuoyDkDxtj&^LU&0T%e#QRJuU~P$VArpwMq6q7!VkKBKWt>HQ+<87(SF0GxiUZSbU9<6-}+*%)IUGVman9gl(wV(c+;q3V0f;~S0g{R*Mt2^+2YET`RcM4q`o_8zPz392HNYaH9=aB@OeFIVswtIU+y#ga%AIU`fPl>Up14q<JsrTv0jhd7uTckooCDESg#lEi|fTa@4CCj`mS)wFY^OqZ`#^d2Hi0B!(I#hGT+m<vAzA}myG@DM!h_l?_9Cc)_x!*-^ia>Bv0n6rPFNrVxL#{xADt-@2P3FdX)DL8}+vt>X-VR`q}c;(<yk~D4i$u{h!&#N9_OYn&ioR@tk0`lQq#8|EcfzrG8jX`*>oXS4wsFOZ}v=wtRPNU*o(RfAY(G&&Bh$dR%*q^C?$1_+`HLNvExS*X?Gu`y=<oer}%E^OWuW9^_-cHRs*^&?n0`eU`5@_}wR~NBBYY{P~qn)?eZC{wn)(eX{WsJ|9nUpXKvq`fR?uKWz8O)`RJ@^<dtA*?JQ`UvJJ=m-}Sv+4T8(t{dl*UN6FD*NeE%^6OFf{CadR>f@7L@51NTyLq2w`-$-RexiQf+^Cc7SHkD}l_#l@G0tp16h7Y%)y|b|&nMjH`>pF%nC<zB`+PrFUdb`OSF-zv>9hNYb8DvbKJE(HVfgI6Cj6lLES@WZ?z6&Y_f6+ZO{DD$pSSN?TvJ-7np92NU(-i_J%t+>zb|3$6@|~=D{^1F2NOPjuNdUxJ)3#nTj%p+=jHDkxi8-D3E%zlJYya2+3A=0fio3O+UkGxb?JG%uaz{um*P2``{Fs=Y-hN~$U9v-U*>x+O|p%TGorb%UVHwYC-VbMzp&+dUv6$Z2VOjwFY}%0-LtHIVAO5nz3{8<e5wD-aa%rrPs@Gr-qjq>^OKG1uy~16GT)WBJ=5x|M}`>p!DCtZQa|*0TRqCaqdr-_>9hPm+s!^%J;LYp@b}Ez59;qO<9vKPO`nhFg&UdD`GU{qOMQ4FL$)4-&)0)%@2m{jdJ{fhZ=SrG8M5^(e7>Gtr%$KLt_yeU>U8P#1)pDE{QW%l`Sq*rdqsL){@y;wXZs0%Z_j<cU-9?$p3x1Bzvsk$&n0~R`z+zBCzj>Q+Hw9g$nc{g@??IXxhLD|d!pAF`_JTs`7+-%Z(WwH9rpV&;VY*v8v90%Zl`3v@?(8l{rvZ6X1^XBG`?TV*mX+gyQfBHSbgu#Q9fC|@OeJ}eVo~^Z#rhm>K8t*pZ}iDJa5{}blG?cKWIFA^*<q<FZg`E0w3HvE?qzD_kd=;_4j>Iwtu~|qW-oz6(badB21~M434(^(;YJDk5KtP-HC1dU;WdaW=)#^U;pXOvwF#j(iB<`+!P!IeF+=|j)e{d$ATwA-v>_yuYhg@uK;_X+rgwO!5(lDf;bU61)K;T0UZe*0e%De8u$%xPiQl6PjENrv*2#v9?+)X9^gLEC~zO}Fla1z7&rks8Jqx~1YH511fB-<fIS$CX$a!s&_r+|`ac}{2KWv1b2zjcxEuO29NGum2XzmJCV&%AAMs`_c4_gU7So|)5yayV#4`}Ys}RIn5X7HCcY#}I(N>Gb(01U4(7FiXNCffI2;wFP;uoRqz+Np5YjFg+2fP=$20=UoLHs;|xF&+QJc76)g19n*I2=J-2SL0Ex(EE37OS=R96A_G`W%?F2AH%Qn6v_zv=W%~F)(QanDi4c>25ITA@Jv5+V_@f@qrep(B<G%@Dc>^GA){G@v0W|ceh{AqNNty5yWxOR^V31kAsc^lTHQGx!hXJhsJ^DgBL)jf~TS;;)Pl)29quVF93^nh*PxiYmu)-9)kE3^fZ|COEBqIVA3<-Q{XSO$kHNPiwrGFD0H(>lu`)d(g@;`2;$-h;$jHmP-szbD7Xx?EVvA~3bZP?3b+>339bcx2HFVx40sSU22A=9co29kbSHQ%cn9<#cnA0Z^ceU6_$c%Q_$c@|Gy{AboQ@#QL=gKB#3!NI;JI2PqejvRVA6On=>SV#23Yz#0AoYi4@~+xn6xXHv?DkKbE!Z>!J(Kl1zH7M1#_c7pHT|_5En)eS3?j#0qqDTZ4Z6|{1k$?KD0BK^j~1oH^HPXaDDLG2;z0n(O}Yd!K5?6q_e^6z#9<6TcLBob1?^75yblt#5o9JaUGM2wLvV_46#^O#A59c?|`la)3r?NCJ%Z7OnMAVdJs&y6HNM%Qm~&8=OT#rBZ#+YQAi7iVqD*0;GziPvIyd;2x2FKxDm7nn6x^Wv^IDm&N~J{JP;ZKjzR7~1o2x4;@$}2R}jRVptZrBz#X6sz@$%tJAk_&h<hQ3`yz;=q5Z+6>%r0BcM!zm5ybByi042*27iosn1djm2mJ^<4?GJx5qwUI^IH5HLHsp>_$-3>8wByU2;vI};sAp9B7*o5g7^mn@%Pa0z^Y>0UtdNLw}G|<lePxab0$6O(KDa+RYmEoMPDuAwRlI1F<Ok&B2J4DS`61>h!(L3;uz>aa11ya+8-PZehcRi=OgU}?hWn<eGS|b{3?RDn-*QQ=%PhuXeV%Ia7Snda7S=^1aUhphG{WWi^0%A;KASlP#1Ur_-zDnKa7_cJJQkMcfg~dao|zlk!+mTU|jlwSK+v{7W1{J2%d@KWzZBYmg951!E10_U5hGOtc5NEr{J@*p)<i1ky8aM&eKDS#aeWS&H;a*#R_<&3&9JKvluz_`PadVal8j(I0(EQ$HaSaOu7|(1oJcud>F^{^G}fTm=^2d5!b>o>Br#hm^T;r6CCf?;vm{4Jq8|(pACZ^0UtvRbex4bj00!j_*pHU(IO9;4L<2G*3CQMTpT~C#nW1xfcn7H-bl1boQY$~X@opdKbYE!N1MbsIHnq&LLH>(V7fjxIgIO-bO-n|hjGovfIr7E<!nG6={E3ghjG0R1aHByQ;S_%)CO<FaU{G$&|P3U&rvPXpvS>!-~-S@;3rT=ICz_-zHO+TbRT#)+8P2q0H)8@L2e!7Z$m#eqTd_Q_9pmmp^sbO(Q$ozwhs8H<=p$wzkTpON1ZVk^Bu^e<A%to4?d3L1L*s1=q~U9jQtSsZX8GAvkk$AaJ(Cz-2&YRjzwL=p=sc7<T$|_a7=sk`wnCOAzkh$xUYzP&AO*i&LZTIt_0H_M0<TV@LU|zzE|F1>{F!4;D6d1={&U0ErBirF9D}G?E7bBEvliGYN$ulw-U9Jt^-p$bU*3^PQfvKwkC3GB7Y_Nk&J#PqwV+M_e3A(!lUEr_-sw^TFbfDp?~Y(uX6nV?f)ql``5s;aV+i!%N+Lm!fbqYE;JeZ2I}esT>`F*obupBIG*e<?(3bwZX8c>829on;7K^9oT<nooeqB2VchTAgD2v+xE3X~NQ6!Rhv8=l&_pnuCrOL((6Qk0;Bn9da2YKspq2`#N7OeRwUbT*Q#<qw(g8dU$Mo5<$SsTf>FCD<^m_u@o(#V;`Zy6@XMDC4K3@ub5a*tT{!N2F33YbCn7fhJ1)nW}yb|bh66#IB7$;!d-i6;DeHjO@Jw6+T&xheNWAXDu)SigGO+-x{FxQhXMjbGBWsp|}<3POHVLV^F3H|`b;+aJ}zli4+%J~R+q$|LwT70NQALPEL#VqIy@GS5G=sa)@Evllus%TT3L-vd`3!jTZekJ_85^`3c77yz6puN@bSEIk>P#=HxS_prR<DZ|w7NGuA=u+?k=)a&#an7Zv<3qGdeR#$3&(Cu7Y(>w?{lJ@X{6BrhtEYw6VLWry)uMsJct&dg?;zTyXS`3LJHelV_d^eYAIG^Pz*{XfiDydE^<Zj;o&^Vh_v6_5%y}4f?t$(FAI8`W1@FP}KRu&<0^JP#7%ZMy`#Ju*XIJsuDxP7*v+EH@!Sm}e)Or}_7=St2jD8Nl7<n-d5$G2kU)17)7MBpj0qDQM0r0obGvIH*-$2iTzX6|vo(G=;e+T^@{2llQ=w<K^;Gdz_!9Rn4f!+lF0{$KPC-`^pZRlU%+u(apdf|5u$HWhy4;=<m5Z^}--+|r*limW~0sjI075oSI8uSYI8u%*oBKRWahFI0&Wt^Y1t)-r}sFAddrRFy16KQKlK_6RV3`kpA#-t_2jPymz7`})xCT(sR^X8Zn(q@)9YKA!^ZDN_zCYW>5=Phf1_#E^(N5PsQ{s!9EQLx5{zlAn+6s$?&0Q3b%!5V%6<4D@VQLyG)U~EZW0$&ARgSN8FQ7g=0E6j(OQx$WrVm^rf)RxdaEq+80Uxq#aUk3jSeF**;{0sDN@Gs!&P=~|d>);#ELSPEw-=Rgo6vQ{7MZpxrx1q(r6vTJXm!A})e}97SLa%`Dg6~7Gg71U>f?fmv1%3qm75oTHFH1>(15*%(K>q+!5Eq8t0#gu&Lhpd@pkKuKTAX$i^o#f&^h+=W@dN1BU<%@g(4W8*#D7D715*$?ga>wj3qeCd3@!vN0xb-tATA0m0;V7?hW^le<fD(or=a)26vSUZ{{mAGe+7L6rXc<iO7rm}g7^kB1bhSh2wE8Y2<!+kG!#rhTnJhWTnzmpruz=vlZuBJL0l4g0Zc($26_=pL0les1x!I)5&A2bg18Fw7MOy#I`l4>g19F1A-E>)DUU(v9`hK2xCWH&Ni}dxTn+jsn1Z-6^d^{sxB~P#n1Z+*^fH)&xHR;8Fa>c5=y@;&aTxS0n1Z+%^bGh6=BF5fI21u#6j~Bo6kG~g23!hU7Fr%$7F-Eh5nKse6<P&c6&wz&4h{#`g4P5_b#;VPEc8$RJK%yp^u0^5{m+5<C+&X~$@<A7T3hB{Op5ASME_l5i1r`-Vx$!P%@5^2tl1{0'

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
