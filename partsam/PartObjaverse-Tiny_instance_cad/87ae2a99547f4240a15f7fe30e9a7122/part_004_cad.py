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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_004.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_004.stl', 'source_sha256': '1d8e6f7c07239b62c85bf94cedfe3978de3fda18e9ae42027605a167691107c4', 'input_faces': 624, 'input_vertices': 336, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.046202268451452255, -0.49827665090560913, -0.08551773428916931], [0.1137593537569046, 0.49999988079071045, 0.36384502053260803]]}
GEOMETRY_BASE85 = 'c$}qM2UrzXx1B3?#jdDWu0}x-yJ7<wR8Yi<Q85-SQ7nlSgjix6YYg_DSnyg9MH8_LAv#9IVDH3!V~w$w-`IU~_Ffaty?O8Z-uE8=cmB2Z+UM*!ZBChMx`esqE~W5a6(#9GX+OnkP$LyqN-6QtF{6j{kB+S~eB@Y*QjB!^11{{;y<?YN7A0O8?>!(owttLwbE~)iz^2~5R_}o$Vn)YA4UZfVGay>%AyGqPqYXWFaMZ|X!>-Y=p`Wj{VNGA_1nd9tub@!{$C>2heFo|c`dkxe3;6j^pn>*+8tLlG{MX6fFoX4C^VZAx^`RjLgl^j%z1}Ime;DaXs3+?S#<ITl2*q)1$e$!^Epi;`wv17f-)`HmMvkwP`SLfRt8cz1T|Lh6tsw(Rw}0D{bmh#?q^qC4r})a5QL9ORG=_BLKrhN~trtSNT6{0p=iy~~uI^XBE<e}N?#unuu9p{A$?dY|i6Pw{S0s_*E^Bp(p0_xD6qVb%W~JO-%_oKOJ3iEAy>`?os{f>i=czs^RY})x`JSNi!wx#@!<QZ<EV_bpTXzrAmDiRms?XL~((OuNjz48+CdE%|@1$$)*#{_oU{%ufO$x_f8nmC{-FSUY)*Y=Qej%K4nsi5x|E!?65w-Wwc#YiPq-#TSZ6|*TjdW|SzerbdZP`S)qbKR=kJniD=|$t9+3PszS_k)8gst*&{M?zG|BEypuMCyO(XqV;>Gp=pPE&pMmApXxGpHHI@w@&zjmx6Kb11)CEz<RG*IyR47W8T<KfeOUf7*$4OU7)f&-F5#zjA|%qz6yt{O<3TQ~nQL@f1I|<1Asl%w?p9xzT*EReQRM^f|wft}afvLiW3x!^r+Iope3w?`+Z^xW!R>j_oF0n=^*usMR~HBmJ*4^nB~ZHZ*@6lP*wuHR!tki{sP}pZr9+zW6Zfnf++~*bhx3T@A`$y-U__lz&?vCtbbVkmir0TO-yVq>^rnPUQLXpF&Q${y0C)AKQ%^G_SO!Nu=AK-^rkOQ`33AwOU5Hl0RcNq1OT@U8^vE8^u37gmlNlIjlz=OQHBXRL&3Go)Ay(tJb3|Klg_zT>nWEsDEtt^YHruU7r=r?^pH}o}bW_qmyS)xmS-#*V>F>-QyJXn=)>Pldi6APVb%OIg97#<Dp#7okb7Qb5ol0dt~ahlBhq`{QY^J|JtA9o9k7R=D$*XmPc{B0>@E*I>Jg&ep^TnuK&U;dLQ+N_s+_?x*?I?NA;3Uy7sg^KQ|+m-bdx@@11nV>iL^#9#tAiy1pWi$M;AJT1V{#+p^xa5ywBVbS}l)T#4gAx9=NI@15iPGoBCMzF9)`3%<_lUg-Ck)IV9zNmqhL(>&ML^;}K!J?shTj<(w<j=f)FUiXr&ldjG#ah38%7U%tA^+k?T!uM;^Pwu1sQQWdwFPBX3yDdB42CAoal;dp8pg78wWbXHUhe+4P9^m)KTb&gs>3Z(tybi1$OZ}v;Tg>tEmKsLSb$6qFu&$3K-M%;O4E0~Xx)jgxu`I_K)@mX3%c(=WK16(2L~+_*;Qgy^HCo5?p<b+SZb5OZg)eb`dc0dm_3v4d)(yvN&z1DtxaXuRy9QEw^{`XC{~dbB`L7S8ILe)``F-)aN4kFCCeODkDF>;2nMXO!xK9@d+x~tG&)Z51Sx;y+m+V;;xc+5Ea2&lD_vg7|-w}=;$j|-olGZE7+fhkW|AqZIPQ9;q{T#4tBjxKH&U(SYyzYI-T1?~N`_p`iANq{rS3Mp}_Qo}&D?y8RJ#-tkh3u?Vq-)hODZakB(<Ul+a~kJ={WbNYQt=1cm$it{dG!3d?diEzHE|2!($=IaQC0c5^UKmYWa|15$2EHHnQS_*=;s4S*QzG+y7S_Mo%(NN?>Q9TJpa6TbcFnq|C&v<dA@4=hV?DIN!K0}rg~Z{m!|sbf3_rDb&RLyDggyjsXkA`X<t;%rjxFH)|J<Vx*b{nB8}#){-i0@U%%gibp5-zG*8q+HB$-Kl;r)j^(LynveIoPVbNPN>AB{)rNLpUr!vZSn*3fXZ%gwztzzU<vayaizU<HKI`a2qii2~SK4*?j`3L+tS?&ileg^6KjcKIYn>FWkJGLH;j~%+6GMd*1|4`Cx%|?)}CG_U^B_%KEs;R%fM*E;6G9Rxub0auT@g20^+1Ku({<fR?x1qd0TCVeaxf4XXvZ4~7qk`u+>8jUvybsoo=J(yd7RQ;kpVxuGE%+Q_>Z#9l%7511N!Q{sXn(ZFmE!mdOL6}1=F|RY{ro<Sk9zO@B+8#SkoQNo15Uac{T1zxdeSnUkLq30Z2@zsK3cxMybc7iuFa{!`{sgCPP%%j&bL&qQ7Fe>a*A|i!LEs9Pb$s(>BBVEV{{r9b<Hhahuf?rT|YXG_E}~A4Bj7Gv+l6Y;B)WeRNe=nt9>plqVg41^1i%m7RTv+o6o%yBAs-_(V6$(%1ubOKZ)ZwU!?PR?Jwe_+h0_pecAEjZC<zAMsoab=JL6v^Dn&Lg|Mz&|FD$u{k)g=yOr&@{>5L={;NG*<fN-!S-k&V`;v6W^ZFdWc_Qt<`oz{wx{`Q@_7z7JPu|Ddd-8KL=kdMgz_T;dKhSmGRr4v|*yp6%?Ya56*W-9SOU-i9m8stiq4wNK<v1HBYLsvMFSL*7x!&=)pn5#%=KV+;d7R!y&1*F2`uI-Q$+iw#%kRx#j#FVKzn^Ybw^IDXuB<mJ$MZ?sx`O&|Yl(5Bzw@H?O0V^J2gTj=b}Z>dTk}45ck#ABN!N<(;pe`K{gLeTw@BAJXY#m)H{t#Lyjwi!SeI-*Q?f{pnmC%uEsmh}YKuzHc|*I{hjisoCEho;cI5SZc6r)o)ZPKK{;MzU(SE2+eh@?XJC&pTMF|>A_ZY`VM-2C8XIgKS&7G5}+=n#Ik9&%(>Ik~`sl(=xu3u<E{ifylmF^E(o6m=ne&ao#FDv*_fBvHv`N;dx&}NacuFjZ6{iFYVoX4?FUe3R>GVPDrts1mnD3$ipJwqE&k956Ux6OoiFAb$Q^@i}elRIWQ<!`+*it-Ok=6&Zt9^U5yrblsm{iwa_lDf1GsWp5^SMIt||Je8VrSiCqvQd3j?%@69RoGb4ANZ2)dS6za%qvHTbCG!-R+MVD_A39r$0_PWcWQ^rJx)n{8cKHK6+F)qD$#sXe%sid>^I@mZ)z_7zM#B{3Zr=6tl@nkvk=WgrPG-X6h|$>=h5mu%Sk_ZwGWRspVRD1uJZY@dLtXf#korxsd2kK+e8uKe5D0U;Bk&9(4TaiuWTMxK3}CT8$jrC57iF-M*6?*p`WcAN%>vwo7#;`(p~SBrtW$V)&9Iny6b&YdEIFgjjMUS#eGnppB6)i^R4yJ5nc~x2E|f-+zafb|K|65Lf6p(&2zrqtvRm~)i;xFp64A051zw&A4la}&b`{yC8WEado_;?)^R?!cg)B2Da*QfU$%aAndkf5gB-u@7(Pc$xV4koyZAEc+OWqw?h!M#2g>@#kNn>CxkTqr-QzCnV|ZNc9}-f?|K&Z>&HK2c>~`+Ay=CHgp7DL$mM6hk$9>$I9L4oavhw!@mwS_5ybbB*J>3@C?1HSD_jFt1Vys7x;`q3y+q3WTIU!&M$8ou5X?qe$H}CJ(vHN(upqux1)pIH9g^rPK-rtq{!<}{9-?fdwe6HyGnxBh%x>~Cs*QX!r=Dpq?R?$f}@9Ea2FL<7$dVNLD!M$EN{)dxp-rubw(pY!<lyvj{Ztp$MNjLB5w)cZr?>UKe-0Rg<fqZUB`H7#4`?yy75zja1=KWm>^5FdMFY|M8Pq&}s`=F_t_jK#1m8^FuFoxzm?&(Uu(N4N~PuD+&vA))ibn~8WU;PQ6XZ({$cfGHvtui>j%Y98hc$oBm-Pgh`w0^tZ*YsI!H7e(FUsH>ABV7r5$ou%<YV>~Try@vKf9G?aqrntjZx{3<{a^Pu=&tuZZN)6sUGH~3nXJ2f2hi(Y<@hf5ef8-Lu8+(20X_B+x69=_fSPz<3gve>N9mDSq`RJ%lqx4Vzsq?^iFUB=a$ZukZd1wca=+7pda>?$zsnU#y6gQ;TRMz%^Sh|Ea(P|{5+;%UuY2FEs?!KR^7l-={~g|svKvgNxcFY}a6CUR>*n`r>y)GXo@$}2<9oF>Vh!s)w&^@x{Jq*%e4La1&-d!>U3q;t7f-tRz1qI2hLdi7uhxSU?!O7MNjJY&+izx{lXb=XUOjCKzmMMQI6l5tJ4Q|C_x)5l=g0SIy<|UU-TYp?voYUy#+~N+<9oHbrZDRb2Ge`ydaqZ~6Zrjexz{Vj-zJdm@?AnLQ-a3F^*e*9yMC9@vORb_UA|*z2hWr4dfxs=cR8Oc(=T&;m-Du%|Lc4n<<I97{Enl~K75SwCoSaf=;rSxCG#EU_IyR>IM;Kpnlzbo*YmC3@ej^#{w`Cn9LMR~lg>}(?>K6i`uyBtBk8>L&v(c%8FZdho2Rml?_dtq^C-nB+>-8}=64Uri1Ku9R~CmalIyR8-Qe#PrN;7o72iFy-n;nsos&N=a;j(Ab;@tOdq2r3|J#0C|1Blg%k|M`-{#-TuC-q;*WY?KgxaP4ae2L5PkVTY6O_N_PswsUZ5KZ$U2WQYgIphL@Ho;P2ZJ{__1mi()IYZWByW_*QJXh_`)yB5iX7ijtR?GHucgTG)sP_4^_u%={{C~Ge|4PdZ%_8&^=Y`@CF)PL2i@0fsa3Yh?Nu9V{QKRiU|uhApR%4zrhc>D9>w{SdQ%+h;Li_}ZW**qj$<G2kjMAREZ%3#-vPrTxqrs2+9r>Sa(^p*7qtx!qjR76{mQ<07v;BC*tlJ8uYTz?>9($~x69+A2SigGN8QvN^7yLu?(}`kdUN*<r}v^}4}Pw#z)m^7mK905J+tgixj!}K7JXN@rfECn_L{$w+G;-BDYr|ne3|>dwEr&BuWq4!b2R>u>SIfOL%N=t#r>)6<v3c{Zn^*U8|Ue{>crc-o!T2bna0JIuyv0-uk6;Q-2cyR?2+56S2}x~-}feI^0?T$p5^!vfoXF6?YYYGJlWJG&1pXGdc<*_HBFbt%XaM=$62u|UCyuEd&K?L<YT%#&mB?eR8MQ!nLj(V>sS<jPuN^3!)d(kzNY+Y*+m&n^;uAo`q?&avvd9@GboPQz49+|e*6B!tiUc#|9T+qS;`%~qLIZ&1(Z_Cz$odT4hT{FnfTxT(}5w4{#XBWz^_50|L;E?_`;~e=SJ!WY%lR>*aF*tuP{;){7LW$-q%PGMrsHA1iT%18(<}gTVV@y2Nz|#!rv7>!A~2hh(%Fe0E>f*B=|GnM<s`sfi3Wj!d#RskMiY_NAN9%?`I=z1^xoQ75p^txy1j1E$|7rD4Pj?CVYa6=kG!t1pWm65&Ri2MdDw;{sLo?g0kPk|2=#^;aQ1zp1?KWe}O*%Zj^Wg><EnCMwIOee^>Yf4>3|@BZUI1fro<k2KJP=6}A<zdZMg5{O<4x9<GR2M^SnKy})~c_W_1UyfW;{s9zY$y2I}dpBMT^jLkjZKJa_s4}t%Y_%_%A&x4DyTj1XU-#+*Se+ksVUxGgc-j{d=Y=MWtw;`?$%m9C7q#Z_j3)}?$7W^S_y~GE>9)vMjkFrbPUjpAIJbxAHAaFJKeekEi4HEAKyBEe}1ImWO9}b`3p2j=&$UqO^F>sNNp?$|tKa($qy&QEFT$D|QKN&v3#he!N_dW1O@b}=afjcEW1h&AX;G%3_`1`_VmKXj~7RICCA_-m|_*ml0U<*tF--%}(1ug^s+eq7uRNBIL1YD#e=)WUqzsY}q{R8^q5n?Pt`9<&@!I+8hc?aAK{to<a;C6`*hCLXuwxetx`1`;oxR`Tde%%Awm7MoW@JwK$#CyUP*cDuq?G1l#`0VIY(SK!t$H7Gs{0+2S5?=vZ;P>E<F&4*xE5OB?E7sQsz;)mczz+jgN&GX|0>i;Y*?#c%gKr(itSH7)U`b2P_zEuiT;Mw;hrh)5yu|nkF3O&V|2%wxi~bku(_3H(OV0Wr_$#1?#EZff=m{>$o`?TDo+r52^Thrp_D_MuEX+kJhP|{H-UpM5cdr!iHMl7I1my+32N!cG4D(5#4SX>8BH#}a9|&7uGPo!k0)Gg6Huwc!4vYd{4!#69NaCTeLopWzp==2JA@B(<)@pH9$N=sI&j3FRd?4``uwP*QJwVyh@SlcHaIsd1wP+bI5_}nW5-?ig?O+RR11`$;g}*O+f{VE-&Uc>ytAl?A9uBM`@k+1-x`VgJv#J9tfoB=%fRQW~#t+~k34RIML5c5&EpQLGD7zc}-S7$SZKPI48VMW)J`y|&ctGMYuwxMG0LpfOzYBbVH#AbPk%|H<f)@q%2DXxTN7x+^s};(2gTEVm713tVzNx^;;8VdH0)r*~4eW0aD;Q<>z`qAR!A~0Lgpu4VjJYh#MH2iPw5v)Ex4;%C>UR|}vf$5xPw<)suVJJ(U@UkX_(|XiiI0Rm5;0GptT+7L@Coi`q((+64lD*<9K0s5hQy1)E{a$+P_`lb4dE+>HjDO62TlQ>4(<nRB=M=Rry^D(l)VK1CHMqCW293?%41>7ZDB5w;0|cll^pH{+YRG$9WhSAe-b{yYZ=_fNb$hY;PK#RfTtuL2RjZiPoZp0_-n!^crzn4F;Yoj3GkBOwSYbnFAlpnV)>w~AN+psl|Y+C`(^;Y1)l-l4A?~C(_v3XtR^UX4gPEJ34YE<XN{E4!kE{>TqMD7Li<C>;dx-^!T9`v7-!%=1E1iv4eo2CvB0mu$AX^&o|Sk!?0CdHi?X%guLYmrEsWIENTq?Lz)OSI2Kq|8B<zxi<%_b-;BN+BDYRL%F9G-+cmj9}U{i_DfIS1Tnxd=&eg}MlXB+8)kqTHC^IMpUB={|8H<TQn4|YC`&ke*l2md+v1g~rGIz}1~90xugJR5jH;$vZtMa&B*TO0n`@ChDZB!44$0Ly@TfY$}qk$7p?r4g$R%C>;N1$<@DX3@Ucz**q4!2^K)5>J4gfLQ)0dlUYf@Ckm=NWUAYkcF|Jg}F$A-+^{p$>9ZH7r^-3MvQFuv*8oGzQOAmX#((T@Co1-fxk<9JnZp^`8&$ig}*L*f{Sl%EsazTSQfk-czs|!iF?5IK&*Nw8vuU*d}YyQ(Z0FBIpA}_1A#3iJ{$II#A=DMx8T18pWs)FblFJm7RJIB<{}CHC$zgt4le||5XR>&VqAp(B7A~3Hh2R?d{<_i2(E!&0bZ8)1lSW0^D@fThrd32f(IE%HIgT=Jh&%#V_*Y`mxEmnu^OOkApC*wl}DRJ`xXG_fiD0L0;&?93wthNsVI8~{yXpqo@S&&M*0<~SeX9`o(}v?$>Hv>-7!ADq3jj-ufQjGcLUlQX&P`6_%!e|;30`?ur<UygtCp{Zw#N{J&e@BNS%OH!8?I>2ey^CCu~o|YKyW#@CU(H6>S#nn-5$FJ|DaXu!F=Gz+Qk@9Z>d9`2U1YaB&tDXZ3G@W5B-w?*{BB@fg?wyMT+byW!sr-x&1iujp@qGo}8Yi9VT${xbP|*z?h*PAHoWe>!}Ee`=)GMk)x*4?YyW=D>pBsqn1@HV0n|z8F{pd@=ZNU}5m#;3I&AB<==VU@nPUU<*_vo)5Obyx_SN@goKM3&3YV`zpX+0lwU5duRAN!<Qd*&Vzd8K|KniKZ>BO1>rOE=0?8Uc%~a-<w4&3@Cm!Rk)e{2e1KKK>si>>80Z7;4_^?lF?bMoFt90jFnBv)bMSWHp}-ar_k}I6w#2Kz7Wj$8#aMm<906{%@Yq)Y4hI+Q6LZB1TnsMSF6LHM;977|=US*&E!3kq+UNtn4}4}`EAm-UKVRgj3V&7j1aD@f03)>qhJZJOuO+ZGcpdoa16zXE2X6#y1>OkU57-9W54;Jmt;9RP7T8hZonQ;>Eb(@*+hGg^55w4Z0=5GW!CVOg27`;X`@`=KUkK{l9`$OEdbB}*v_e~3!)N9VL%uLPvjg&kz#jsi;FXQ!Wu%J0YTzps_6-A81Q+k-O1z%}hk;iBF97@!ya0GUV1Mv@;CX=qBwo(Kw!jJ!uK`<NO^N%#_QMzo?v1gp0rUf}hPmPmYy|Fwxm68VA6(SAtcB|(upGE(V@3D{mX-2)BcC^(Sq}YI4f(3UC%9^)x<(2FZveYXm?c*!xBuxs9nbmGEaLy=|B&3Zr1Q_la><rPtbcw)?h=-V*6v)!|HOx>X5!ST{1+0kmF@'

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
