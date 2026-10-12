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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_005.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_005.stl', 'source_sha256': '107b67ce31547a0c3fe72785d36310a5e48e8e383fc070cd0e8b34681a19d6d2', 'input_faces': 920, 'input_vertices': 719, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06906937062740326, -0.08408977091312408, 0.10268881916999817], [0.1374800205230713, 0.2213083803653717, 0.49999991059303284]]}
GEOMETRY_BASE85 = 'c$}rZ2UHZv8}8kMu4xq$28?4)nAV)zoU<aLu7k=df|3->wy2mD1BwA0Kro|-g4xC#Fy}nRb=Or_SJ$l9df#XE4@H0HeCJ;G)OmjMOigulrLOL(W_xtblGRD!e`S>LJSQ7IYpp0E<W`)NAkTm?UPC<tYmD|AZ&LD+FaFteX}7*zd-OLcLCVBR!#o3r22^TnuGI9mhLv2*m45RL7!%+zda!T6Fi+vP^Y97u{NV?V@bL5e@wsw?+KpVyb*i|SC!7B-|K<9T1$|aR;-Md^EqEN>;)hyON8b`^sn(r*eeOOheO{P)M5sBWG5N}bgTsWX%LX5#-yNvO>9o7QkUm!nJ1SJKSeN5(*fw5#RwukC-?r!%PJfC=BE`EKdYHa1`e?iGEk_^hqT>#7XTL-o`R3@Md&OtvZgujlvvZTLj4hK&e%&#*Nk4Z;5WaPd$976*-hBFA_j|gPj=Q-U{a(wxk>YDVZz5l7Jt3Mt{}D;wD<7AWZ;7kBlg|IK8>ORmawK1w%;jL|>_g?CpL(!`@|lo*Hyzi%Jjd5JlW&<-{1Bzn&V|n_=UVdhVH=iGxxDU7<*dwhCSQrmI-BB!#gMNZ{J2^8wmbdzlV3gXF6o6N^3{a;6i=Ocm(EMiwv2o&i@!hlpFVOrT_<g#baJ{Kq~oTnq;!;f+c(m2yG~t9@yw&|kcMnx|Nd(~ivPx!+KFCs8u{uImFiV_lb_<Nxg0otiE28<yK{)r*S`mBpmG>-n94z)l$+~e$h!5EpR&ykQ29*zO21RGN0F~gLVI%<PvxwvoWcILs#Ly~;ZM070)Jv3=c`T6!tL;0!FVd?yT`XsymK`V@%iqJqxgygrE3c=N%>a>)gxa!e}meOn!JI^N$XUW{W0%WQM@L~J<?pcIh_?f1L%7<KPn${!9Ui~=c5m}9V~po<$T+fe5H1`B+6gia+JQ3T#I})t}d6`lo#|nYyXR}R6dD&xqLP~q3<mhPOu;PHiqJ@btPYIe~^5=>KZyP^>R6`#~}&iTO6xU`&4h7qx@S({zATT!|X%(I1)<n_4`3Flz#^<Pd#@YF3-v%$+xarzK7x$`km4-UsK7~(-v|2e({>mcklaX^4p!>MER)FgwMla3H&UJ=sXIYyFlrG7(l*u!FL|@C+7y_TRORrZ_VC*HGMz-^*KuCRR!|Rm9p-m&wqWR{Af!{bNU`RmXdD#e38D-RXCd4t@9enU(#VN@AnSu*Xff${?Rz<XO<d|tn~W=f6O9nsGg^COI}L8GGm7~{myAAm7A@@1olHu&m}GI&*SRQ{G3kw-_)*@6OP=Ew`3*XrZ(hu7Ilv6apaM;R9~F}Io^@N_vv?T+sRi3rPA-z%U38rN^~syoqPLJd9)}%<)fQ}$ydwOTtWHX|AEhUd_WY%4@g-|$4QuUnU3?ZE&C%rEueT-dplnrN#))mDVE~B^Q8Q$L5}1r@8^u9^xHm8BfoeK^3`DvseM@k22wq0J)f<i&n>Oo4rjKc_Mo{OCSUbvvxJWOsXF%?XIJv|Jv}L(_VGu_-kN-^*#>I=wgxU#K5Daa<lDkrDP3hrA@;{)S!3AVimY30)ZUaLomU&RH^tI?wNbm$!jG*oYA4FxCFCnro1dU|@Tn?~GvPk$KYK8fK6gnzlis)Y7q#>js(<C)VDdHZEbG(fU%Rt)C8bmI<qZ1Xb1nDxlv(U!{M4H)<?(aiH1f6EZ>b#At5dF0IdmLNzV+=}y589;ByhP6s7$_|6iMT#dcQp7Q(K&4rBORnr@o6IAN@$nUV+=M`+4>Q-c2Jvn~B<$-hO|CVY}@gM7|#GL&sCShn^+<=F9PWJUmV5?3={(Qm+U3T7I8d^!fcX`d;y_MZV>FBWkbK<4$y5+M=&3DE+Vh(sj{N>K`7jj^ABj)GzdYM>+m*FUpS|vYhi3ox*;bGJIVvrE+^{n@GMoVQx63Qwi<%&rO{Ev5K7kz7M(FCN1Xpy*ra{?(mJ;i*jrR`8NBw@hXzWIc4M&K5ngnbiLJEZA#1FkGM_qDCOEgI$wQ<KOZ-|AlIMg=~Hyve%>5E^frwPw&z>9-+lg><KIr?dBf#5Jin;@*K*2dV{iJs{yvu5;gL(^E9k$re`@o*Y(yHzm&O4#@eui1`B$8e!jErKI#FB5w=6rw<Ab#}_v2@4$v0Q1Nb^!{z-PX04iDt?y)SXO{dVIz{cfJh`H{z^T8%lr?=p(7cX~nXU)`36{Vv_vPn~>)j`Km`d}5rj+-k$)aO5YdS0(B@T^B7LMM$-$FUVJ;N^|{sr&9Y-#$Dm~S`nW2`PVv^-q-g1P353%%gXJ|GnIXew|dEUR1WHsWt{%q)MWZ>KF{s>P$5p=Gsk>tFW;khK9(aV$3GuN?McP>qYh18M(H>9W53j48XvTGYuGQkoaZ?X`MCW&oWs5}{-~i<$+w)pMDuR->Mm~2*}l>EsEo(_t?enECvSSsepr5PpV@WJf7LVOYbKsQC_SHWy9+$X@uhK6Z!(j7%a##5{|$XZ{Z8NK#^dshBQ#!VZ~Zxb)-IgBH0~)I+j9D8Z--O9eRy2bDm$}3?-<P!G{<&4Z}d-ELcc%JnEOZR<JZ&sN>-jPS^qTiytvB(j&F6M`cnQq#pSt7BVUU@$@ei1QCyyTx{@!CC+f0FoX(bt+}<!==>uQVIAvZtmc{`M?cDCGVfj<j_iN4cjC^^VR0lL=|5-!2A5?dmc>I4+mVDj0a0-2%dO3ry<cX&IsQq?u`#<?5jN*I#dOCf-R+IlA-#$KA%hXFv?`yc;DO*a>^+I!hM80iM9V&PA?<k%ZEk45Wm*3>^=xldB{;sgF^zBydU4q+H|GDf}>dn_zj1S7U>71W{d{nNMy4+us*vaHumsF*GYF+MnF1@eX$Dh4NX#CNi`*A*>zM=6-+gFDB>COgR4iC$4`@=Y+-N?%M!FZxf9>n>a|A^Y9f^qD>@u$>jZm+nW>JQ?0{2zXRd_DIPzRq>n&Erh#6`anqLay|CTxb9DC-kEDwmSb@BH#08_G6xA7$1~`Zwo2?uL_s@umU{py^kPYYneplqxO!YbhOzO$+x=Qp>e>Rbn1M1U!PO!B<26fXF85H>+Aw5H(b}$BGvi4oClDvH26Tz32c1^Qu|ll)?HxK-?gTd$v20)(0HOfyU6+Uct_))GLgq0ZTdH!|NL{CeC^Y8%8$AAJsx+Poagx7Cushwg^jwE!M{_LuT#ULX&$1y2_auyw3gesJwIs!IX?Q4o;L^QXK-td?|q$)t6n|C*Wt7*oF9xEmiP|bj~X4N`Ka=IPsZ^uB!zr!E{{ukK$SxoeEanxA%y4EXEt#<FCF=MWV*%I>sP_#%kyEap*Q)N#<w#)d4Alo3y))kukv|0wdLbV<Ct>#1Ks~<DGiTPId_Za@jvbo`RcUET%I38_<Esj;rQ}AyuecO<@vUf@4*~uZ_@l+cbiDQ;>_cKwyrXdx6z|H{$JiSjw$!9bHDpD2l?{6{Xc(Y`wZi!Zrwkd{0jXtjKf;(Sn_`qbal#)z26<3L%!8#2Gx@V<CvbynT{vVpY>H;L+STuKbD^ydAzM&mwaX8Cwl&*n%($*?O-wT_1jJv`l)^(b*522)wAuI$@N<)iN4QMocr&?h2-n~f1~?Fy(+hVHQPY)GtGx1TCp$9+tq+0bRS|LC)Me5`M$Pt@C>7Vt!C}X@#Xu((OW|(KAz`TtNU}m_&R$U<y)GE=t)hdW#|{99QnHO<(fw6Nb^9YaMBd|{e-I-t}ohv)syM`<@r2(>)YJ?oT+qfN=J*UN50a1Hs8;AMe_JLHF=UzeQE2alds--PUUPq=EL^|Q?in;_v^Qles}yPkI%=VCenE|Z@Z0-KPwkq7nI4pCK}eG>*WdbS(@i)xn_~C%&d~3ooK&jC*N`{fuHAfcH{BwQQz?tUz&Gmeq(|t-*dZCyRvPLrFz#EFB(h7mF5*%@<8&H+5DWu{@hGc-jAW<;X0@eT*&!pznJ}(4f*~G^9SWtF!>6u@7e>E$Dc*j$k!}9uP{$;!uK6z3UGY%BdcpMPXD8gp3_;pU(t0+x$%nod#MEWrR$55xGaFnu{XCH`}|@1Lu&V$b8fnxnVY!t`L;U6{@YvB9@H#o5AP?DuLOnD_-}s>pe5Ae_-URzAKv`#etKW&-HzvTm_I1RBmAh`iyq+lzw2`@hfPz+*Q))^_l+;ta{Ki7g?)!_JP)zYE8Z3*-|Xo`^A@Y=!Tt2UGVcICKm2lm)2o~2OMbcb^xRK-V>*z*A8?xISBp;bJS0^iU!A&weCxl3+5dU<Xv&X#y{I-~G`Hv4oX@f&xc!fDAYZZl&hw((`Pe_SW)!7^>y%~BvFqu5rFtaKbGq%}dVK6fzMkVMmA~fml;?Gov$9`o58uz`UC#MYE_)mHyNXtB$H926@_htd-;~ayybb$rqMsL?*R#-FTyGIv4hgwOkY9T=jceA~9e93HJl}70+&LAgd~5@+@o{Gads4bvre^3z%G-OKkIFi)AIw_L_Z`i~4>RgtO4`<;hW*I>;Si(#V)xaxL$;DX@;>`{9(z#yzWI552=f!=`3?)^`}e`LzN7AX#qn!)wWRN-+V>9JPiJQtOulrTQe1Nlp!79IdLCu{{{4Oie``{P>$37^b9efE*A%`^*q`SF1oo%&FXZ8QLgX6mkJ&c38TC75^k!GX{$)$(L&ufpr6oG{G3rOkj4RzKUZo)!`-^h!(?O&506$axDtSIM7h=B-`lWLH`aLZx)MBojv7NxTHfTlj3hPJjTj~8w?cqYpDwMy`KW(6TJb##d&DVwW<V4D+I%)Qm48GicIxMZ*!l?ax&>OTcYCpTZ+O{xiC)$b*q|$X$8FsKcDefPY5Ld4EKKXjKFlr|+bN6mxRKLI7AYZ<2Dxo?1wlJ#qkyg5ovITD9a$XU`<8Y~L{aP5+yV}4_sID~O>n!FK%5slElpp*2r2bWYe&tyGS5o_Z<z{F0YyCQyKHHzSf4A~;;KxVEx4KNu*skE~*L!8WUn^G7gFfT_TCeWF_gVArv2TA)`#p}=S4##Dq4ULknRcNg`?ehXd}P(Q4DCVduh6=YJWguy-^kaS2XOqh<GI{kd>KW)JWj&5G~AY<oVC!8zDDJyM%DB)DmS%XxSvtEX-5;-e`x0C_YHU)(AGX6Uv+7=p3+~sg3IT5b$_FB(_@$V8<m^-*L{DZa#M!}j-~X{y6`&D)$jb==3?_8^54~@@x(l8^tJSUrhdBBKgh7(+5Ky-arFD}4Ltv!yDrG6U#lMu1R3_zgmS?Yf7b}AFYW#~F8`0d!AAX8U65lO{qBiNhVe&RxObdkeSNt+&Zxg@UN6QO)uYzl%=-r9adKCq@rL#Lb>?`ZdQ_92k2kExZw)3G)uY{)#}h3ja)MF)+Wk!PH@_?sDZVtGs1?1)m&XltuW1q;ztnIp{|#Q(();%7rn=9MpPN;kI+^?)^)s{|CHKjx)Q{>XWf&hUE<-gsZhl`*zcBY-TTl*KkI_?iXY6;u9^~7GyHk9<73aq?F?c$qbLlSicUwYzns;fFFOaYP?L_%e-+S_W?0AV8^t<<schGU;!pXPQtxvwvxF4l&cH;JCiRn(h+9(T+&+7b8if=wSmg7%6!{hdiVDhae&ylZv8^HPe*`4#_?l{w^9qI*&&opXp`irhJjoOu3aLi1@cJ(rTrct|6oX*ZPYFEmu?|j^p7a7XU?#u1Uygqj*ea_xG<M`093;9Z^q8Z9r4~YmhDrfz5BBwLv+m7_*X)AOil)q1<@>Bx3JoUll`TlKsCn`^i+Mmm_Sx(xIq7P|7zBT^{%8%`8zIhbCUykkR&r99Wn*H@<GUjt(&^)7js$Uk7uRVXuenrlw?zNG8bI^9mr)7N*w}*CjIQ{vR`1+F9jq~Z8K>JtZand$sC;QU4XZPjt_P_YjxN7(1an)RQTDVbuEMcp{4fEfAeYny2+P)@*8<mgZb2i+lJk?uI!;Q*ciyyhdsJ_%fcUKtIukGHK6-Mnrd7U@HsQu_!%0(Eqx5^zOjM}I5^@s?g_H6g%excj4uQck{`cE~;m&XBROndU>aYL`#hvQ4*j5*YOrBVLP*=KP&(l}<Rww3%$<KCQu)XwB_QqTFEe0f||wl!N#=}6<SbwXZVXOhNqb>avfzohGeer+_zm#zy+-Aa-4S-NhT+chR%zW&<Ej3PhNb^Q5!PDi@#>;2=&m*)xQ6Ne&=`j=Mrc%)H(QEpv|H0r1S`BJ}A>)m8unlIUXx&K;x3Pe$SY2KwQYrU3^C(i>rZzMm{{B!*_^5yxe#qT`(^8B{(D^6dU4_lqu^Yc(?{;aNbpnZq({e{IfFZ<H`LBC&=eEI%GZBm-|FUt2j=9=VZx<A_3kbUWX%2v1+`_lcF{@EkisQu{X+0jPrM47ZO+NeF4>#Sy9y084tm)e7FiHbIAKib0RXv220e;xVqeX-q_?~Coe+<w%+L{4A2@7B+yL>u)lyD#6rTb&2-I-mU9;G0j3Vf{Xw6k}A6T0V_^={bgWVt$NK{n`$0<M{G(l@5E@m!89@7Z1l6)vvbdVT@5dswbbs7}dMA=c^dQdc5@^#;6`GIljag)uUGbdyG-N=*9BJ8kMsaREYdc&&?9L#TwO@*3moGs9!5_{;`Jr_tF^lv;RDu;<vIK=kr<2zVsYY?H$d&{G2oXbgWUmYrF5p8r8eL<^}uG^JKkYu60y?@_J~=V(Ykkno@hSj(tJTx6OO%uQRGgJ+j?8qx!OjxUMrQf349_jxRmWH-~$XpK1Tq{Q2bDg053}nx|NKov8MG<R|0$g6-2cKCke4ye~VnH?2ol@)V%<A+KwwZ_1FLX*`@*EzYPOEx$C3GpcuUkq(@Wv@W9sbR%CL53N-OurICqSZu>NeQEtj_wwiXp<(1}?%8=i(oYM?m)D_mj~5(YUblMa98dX@_u*U^OuoEcrawAEzP!Gs`&{Mt(zv8|$U*lx^17aRog@3wI-s?BQNAyd)(x%6W!4+ji&CI6`SQ4A+uCNmQ8{b3+jD$*Jv3zk$CuVmtp#t9FR!;MzBZ08t<UPGpK|`C^<4GtNA{(4;s1PTU0CT{kj6E6-C5b=LcY9Ctv2evf$KTry0(6J2>J3lxV5tn`I*+uua4#T@;dwPv)Px%AG@Dv9l!M=PG4I0w?u_=KIMG^ePj51rF{j;^f>mVeG7W{ZqARq&tbwzKCZMcLce;B(~<U3m<QkB_|m=$rOh*rFYn**f6m91_j|yX_jRZ<zHxkv^VVbU`2B!H(?-g-G~U{MdH;zv!f~Tf|5A!HCtuztWB28KGG^PLjYj=NnKXgZm-g*g+OA?>+UH{ljAUQh7o>fO=i^HIh%7U=b9`w(l9G2X=SSMVq;$W)=}7yXY=Qss`AYk#^yrVAzO?^JJO72#m-lOZ{m#C;zpGhcey>2<52lo@NWQ#(%$BV_Kd+JYr&*jk^8PbvKbs!Yi_@3(#aYL0U|(MEj@?YYydO`wn85qFrTuue<|o;g_Vt;k-s5~q*AdH$_nVCRwXN7^PDk2jXdaM%vr)fRgWbuO_dP0cgUHXce;~z=eXsU>{TjymvTX%|HyiZ}%bn$%zPxX<K_sUm?ekPSZRhyXzEC|bnSFU5>60`*uC(vevg`||FJB)^X4{g!{n+=lTCNmeU)l$&RBFoa3rYKCEg`MQm-pG~_oCUC_V?O-d4I1ZJb}}f_6e)6cWz1FzwG;s?S7{H#$EPtI?}#n>)tEuOZ%M7&#rSi(!9c2`6b7f_EB3V7NPmQyieP_u^9Q8<`oO7vM=oqSFO#+&$OSs+bHto{pYrcejH!guWq>>#POwl@BjJozIThp`H}Y3Yeg1t`qDmpt!>y=qkd=i<^BBDb1ON%^j?5IGoI6z=1Z25$sAvL@4&q14wthup6G#paXQlb4wmz8I34Nz2tA?zzrQ5S-)!AWvoF1Wp*?THzBG@rT<FaEP38AKR(g{!zb9fVJC>h!OXG$$Y$2yFy`N$o`Z&R`pT2m(@uhLY`d!&ZpQZO`v{A*#&-8xQC0F*P`IV};lb>ndV8R^oGwnaDnat@(^B;4?o7>X&Q~Ucz+O+!|UwU6jE9gwm_w{8h_`2}3KebzP%M#m-`jO&Wdb?3S)pvWdFTJ0o`;Oag)ZX;Fi#h#8!BmgR>FeB%_8i@A)K1hM$G01`2WzE!<je1=>F<it^8)#OH@#4K_NDjZtRuQ68r7G1wRfUXeOU+lB^uUO{n?2|^`$k5O*E=6OVcmxOYbM@Px9@c^riP1wK}EASN`3}*R_U)>A2QxW7(J9m$Yr0L%y0fjQ5pw*~0rdy%Wio-@8;!q>!KK`M|rq<je1Gs#A`VFTV$>)Vs*>Kb)fXYqeg}`M%QSE$2sipVa2wgWfxp-%C}KUCFmzT*&VkFD=32%ry`4<@Z~)e|<O|>3vw$E1KVH{W6KlK_9=3#}joArz5>@t5!J0$1QrC<M%ni<3M~j8eg>Ef93bBzuo5ROUWqm<@bLzhXfvvr1yxmuuJSGzo+vu=XuTZrI;t2e*QS}Eq6+BJK0;1-#?e%Q*JSUuPf4f&E_RD$Tuf7rt5{;s1@hmYYqAG`_YyHiJXq~KDDOqWM6v!TK(Wm^Evr_ZEb%kety*F0@b^DxhLm;&o1_*_raB7*Et>O{c$Dteex|^0(cxgS(L}g#M-n^T7GZcoZN-{Oz*ijSw_Bg)r;PvwLHLho)X9DNbk|xa-Jt&eji`2@s9UrI~}F>p{=7=alZ%&=Kk~fGrw=zd=S@T-NT%ZF@N%V$uszRt++oUU;g_5mcaw5pX;5=)BB5-de?b;d!dn^>F*2_SkLiI`>g5DOZ(#>`SRZ@FgI(-`v_Kd;rF8UzU6&}{pa$20qO58D6<yu@s8xna9)<rfwZ2iP20@xH6ou{@ICS^Rh;Sk^hf1+|6oKbuGefU__=Pc*)+~ueBJjO<;PZXF7KO28_E53Z&RL6_B+S>1#<awedR66<Iv2D{9el~H@*({n8knpAuSKJ59`P^bbYWM>c#sZ4;AA3u42>ad5LXD68V;OQ^;51CxnsW`fjQ7<&aVS)ucu|&Mk@Nb<0&pc|LG@IQQ>LZE0OjFF%v7Yej?D_bboq2H)$_ywSXK3Ga(KdywZ@j{|uhXp?=Me%ZscUZnqiiRU>3j&nLU3-a@%fC!3jOHO0|#b3P6b2x<Wo8Lt6`vDQ___^BfNvB)%$naM}sy_H@hP9gb6B&w<Q*ly$^GNq6LWC*)+12<@gm~5c|Me$A8vRo1|MgFVOmO%y1^5wseuOg6R?tD<R^Ud^Zs11Xnh1g`Ks$gdfSsVtz)oNVS{|%`|1q&<1&biq27PB@7D4b?=zXxzW8kykz0lp@z2L3T_28}GSm+vXEI1q*2@VG@hem;ygI7SU;1%Eq1i>qz(cqQf)zBEQ&>i5_;CKYV$<Te^Wbi5IJ@6^;1L#}u1MqujHV5YS;GY~=D}jFkmxZ<lmjyS4dVrgPJ3{@y9l>tUiC{OdH*^}<8$1>|3p^Iw5c(UqA-E0HAKV7q7di>t7wiSqz+T`$=uB`RI0!l$90U%A&H)F5$3R2DW5C0pQ^3Q(Euo{qEy0DMEx<yvfD42FHE|Gp$;3hM@6b|U5d?pL4grfGxE8$e;9B6W(COf=U|;A8urGK9G!8riya2ivEHoax06ZBQ0iF!*1RVz!+7sLf{0p=?_!qDv^e+>$Blx+A^$z$s_$KrW_$K%`Gzokhyd63Zyd69T+7mnn+zVP2+zVVC>IAM1E(HBsVJ-xIgCO`6G!A?U90d&qM}en7JAj3j1y2LFgcb(31XqJ9VDYaAxEi=2v>do0xHq&BxHotTv^{tV*a{s6wt^o)lfjR`AEDR4AHk(f90Wf>5S$8K02bO8oC=<cAlL({f<3@pp>@Gs!JVMBz@5OIp|!!C!QG$@z}>(Dpv}Ppz+<4T!DGO)pgq8|z~Rte!QtR8&|kn^z;4iHU^lQYv<=u790KhH4goKQ4h1g;?|{w*?*LzcZUtWfKZafcKL+PEvHlJgn%~4Mg5b)~2H?uzcF-Q+cHj{Rf+s*nfrX9+PXJGb`hq8eryvNP3iSt11#8d%um+w64FpdE`#^sK`+!}cZNRSJR!|pkD{uv9UT_7lBlM}l><E6QuwDf}1K)xsf^UJ3K*PX7r-P4x6QC2o3E*f1!Aqedz)Qh%p#8vez&oKcz&pWr5Crdo_5tq$FNBr=F9f?l^MGBzrJxSrQeY=&R<IK|KQs$CKR6%M1Qz-;I3Ktkv@*CJH~`uTEOZh$02~872#x{Ygf=xX-vl=?v33ME0eAQj20#ZvJAwy+e}#4i{|X)q?E)SQwjc=Z3T*-I3RV#WuUA-CE6gGY?how=?hmdHtqB%d8eAV-2AUIG2AmuE6If_AaBi?8G&|T4TpXGgTpU~pS`1tX+yq(?+yuM^>J454J`Y_6J`c7b2u_2Bg44kJp+4aK;7I5=a3nYaLGV$i20jYj2K^1Z4ZI6F61)q%7diyI7n}ke2u=YXgAM{810RBVf)9arLq~yyP6Y1;Z-R~oZvt<C27xz#<Dp~0@!)mPK=3;7S_Hu>p?=_%;LXsf;LYH(2!fYDyMvd2Ezl}p3%CZ<46Xq#4=oBV4=xEU2rdbBhUNl0g9|}(fQ1$S7Xnv@Rs~lFdqG{nLT7@#z>A<s;6>oW(9ht*;IB}#iTNwI%#TnXS{G^t*9F&smH^iQ*Md5OYk_M*i-3hz1J?xif%XRX0ndld0}D+8&j%+$&wvxbC!u%1LT`glf=@tiflq*sKyQGLfDc2jfe(WZK`(<3fe%72f)9fCBM80#eG0w+eu5ylkOONu2WAljH;1+ZHwXU;9R(J;2>dH}9&{6U9(X-;Cs^oq@Op3zbR#$h90^?qjs%B8SAoO9bD@jDbHSd_0I(;x3A78i3HWCO!Ih!?z?H%EpswJ0;Mxd+Ye4&eYk*y#y}>TvYS13wYTzo+?%*omlF<HOp%!pSa8c-Ra8Ymp=m>BDuo*fOYz7yH4g?nmmxc}omj+jab_Q1j7lif#7X;Tw5L^f94z2@shPDMegY!TegY$qtn>Yy032y*6C%7(j8MrPu1R4zv0WX1W0WSeZL6gBz;H^KxHt23>GFa#V@NTdUO$F=V!_Xt(!{DRP(_o=#;G^JE&~sp+XThhyC!uG+LQjBCf{#OwfrTCf9|s?T?g1YH?}zRJ?+5RL?f~xtr$7_HLX*HL;6&(Va3XjEbS-!TI2O7F91FHWSA(tKmC!J-(1qZY;N{Ty;N{?@&<WtB;Hgj_@KkVnhySe^w1<8(F}DX7`=M8%I#l>Ng5V7Zg43WPtu%ZV{1Dm-EP~)q&_-Yp1iyyX1dAZ}6|@3a1i^nmoxmaper)0(_&ihriy-&_RIE=NKoFb)wSiN>8=+^xLid6<g5#iD!ExZV&{*(V@G@vPco}#hbUAn-coB33co8@Z8UYRiFGdi&1iBKu1iTcw8Z0y(ycE0&LGU_gGI$+$GxQXAGk6d50eBBM75W~W3cdmr>l0V-S@1JxS+EF#KSG;=MG*WI+7T>*;O|g3un2;4!1D&@0Oy5{1?L67G_f`Wiy-)KXdAEyg1<off<+K)g69P`fpbFx!MVZtp+VsM;3Cjqa1n4m=ooN5umf}$*a7^;#M%-pg5XEc!eF6dP2v%P;L`|#cR??KcY${z2tEh>9efUa7y1Ew7yJS$)-7J(v*26~tX;vmz*V8X;HqF1Is>eNM?x2Xg-!;K1UG<o0t@{G+yGnx>Ig0Y&JGpp5ZUor@Si5uo8Uje*P+M3*TF}j+rdY{3D7y<1n^vFFYsJ&Uubo3UvLd*A#e?FVW?P>D2&g7-y#UU2t5V92;KvY0`CDYhfV_vZ3$iuc86923vCE?2hW4{2G0X;giZl(1fPRi!RNrQppU?>zy(aKAHgCBt_T%t4;2vvcSjK12`bhkI^nb6Dkctsb3jwULg#`-5c~&%;OkHi@OAJBXjkwFunz46*1^Z2ox#V!XQ17{XTUe01Hd=H_n~9J_rZTbXMz6$zl4T^UxH6UyMRxEFF@VE7r?inzTn&7yU-BuUGM|wV(<g-ztA1vf5F8~tXIGy2(Ar%3>HCfYp7V05G=GZxHZ@f+79dn_J)oCdxIw-2%Zj|02VqKJRLj(It4rfJQG21D0C_~6g&&6foFkdL#KgfgF~P`;1IAM)D`Rp9tmv)9tj=@tpFYfZVPn;w*}XOiuH+l_$;_A^cGkI!9PKdfQ2T2MG*WBUNra}_yvOC=g_6#=irCXIpBxjJSNtiU=ajYg5Cj(Ab7ZmgWzAF`@kXyE(To)7D4bo@La(EfLB3FfmeY?L!H2*!R?^=!R^2;p!vW;>w#N<=R*U)LSw-5!3Ur>!3V(ipkf{39zF|hY+~&IZVYa3`rlebdj!G#e}pm6vCskFvEU%+AaD>k82T$X7(5O-7(5O<9%=!P2Tw#0JOtVmJOtbgs)D<LTOtVFuCR*rkL?J8heP{=hl3kK>w|@s0XGI$faV4Zbp%%cw}lo5w*~t{D}nvNvCt;qSg?bMbq!bq!R4Xn!6FE52DO1j5bR~*Ah;1U4J?A-lF<EN5d;^7MuJ5UT+qZpa6V`RSOmc)=uxl;f<M692L1s42Hgez2F_(--3u0)0v18=&(LFF5d`Oi9s-LXI6HJVSOme@OdJGfg>C{1-2fIra29AhSOme};jIII2Y-RC1%Cm*M-coPx)S^v{0X`l{0Usj#CjGig5c&R4ub#0_e;Qkf-gfY;LG4G&>G+^;K9)H;KAUI(30Se;HFS#a8qy{Xd$rB>fk!y$xtt_&_&?M;1$rr;1%H0(68XrV6kv4RIGC-2!hL*{<juV4nc6kAHfqk3|b#N3_KKC7d#Z~0j&e}0J}qLf!)FVpf$ll`+)m_7eMEOg(iX*fVV+Uf`y&{Zv$_E9szFwZ~75>bT&CSW%>X5UjY8^pP17q8UBZW@-H)P3r_#bifxqtZ4&O$`6sbHtT_DmPYjACvD&BnA4De`F#'

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
