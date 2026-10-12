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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_009.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_009.stl', 'source_sha256': '26b3610977c6320d3a2efa28cc74303c4d5520710f89dc51b3672cd1c278dcb8', 'input_faces': 648, 'input_vertices': 388, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06677393615245819, 0.4226114749908447, -0.006434602662920952], [-0.0022777169942855835, 0.4999998211860657, 0.11385651677846909]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@-~LauAR<Kcb`26G$_OF^M?x4uLUbl>L_*XwL6jVAMDHaSE<!{XL?Xdq@KdH>3>jryGZ?*%KFXW(eV)wR{MY|o>s{}gwf1^G_p$Tc`|SPQ`<%0HmO%f4g<KT;)KDH(nBilsr6@)zp|~h<VbQS>p<yu%M@LSuQ%Z?%{N(A<ZoRq&_Onysl!<Ob!eT<B-CCO5yu(|#xtrX=$3(|Qhm0OHCVEJi;roS*j0wy2V}^x9hUI>)<I$ppyUC-jyJ@oNfB929w+niO3VV;{s(Px+&9;Wlo48-JYH9d2?BH+fd%#djjpE|#b7zTfIh?Z3Q2p||J%+D5+wz<7*?iPDUHqF5#n)G-Nqud}%`}PE;iC9j<#tkEui4_D{CkhX;;Z%-rM@Z64fW$@qW+r;H;m899aDzXkDr403;vY)%9+V~rC)s-!JqjG?as>CBkg2Vf!}M8#L)-6K%8S)yQSS<&ZGbRFU$3+(P{7x){r=6?{_jj*7#)jt}#+yt9(?hSN(ZC{Oup5zV)%Ev}<WPUwplJ7{=|Go5V2(go>|36vsFuZkBN{XZoQ2<&_wR2O${e==$Po`yXAGIL|DZ(oVqjT@q){YPl}U?$``lUu|;)ane&Tp3Vp1fBuYqrZn6w*U>Q){;{i=_Y1FOJk=5P#n(2~k@%`d3u)K#)VdS-FhlyI|L%QA`k#76eAWCI^Wq&KaZFh|;U9mG@r-@EQ`%4U5nuZ`OX6r{o=JSAstf8Dd?)qw9-C!6l__@OD>q!FzBzfFv}-MJaEJ8gu)B<>HLSOcr!_QLd@W&t_?EY0WWKbj^Tk&!H6)HQ^)ll8FkO7*^c~c{y5xYZufD={S?=xGA>-kifOg9tlkw54ZZiIs=l*Cnr!nf=pTfMqZ;d#Q{>C`}{949e+1?cGZV$pZ1g@3-=-CwzC%8NE|JY5;uj||G;y)jSah_2?;#<nj7hf&&E&LB1B!86AiQ?;z&R&yx>)o?#eWmm*<kjXynBQs%h;!(Q)Hk<jEA{pJ{)kiQHS((8x?Q6FUhv(KKU$#)+r>Xn0r4w5k~q3g3yGsSx}d)6F^og`<&vM42Pd|Pe{Vec)1WKH;mGuDw)tspavS;iur=z}yoc+(=P7xm`g*}%y8-?0yH?t@jQJ~7#%+a@#J7gnV;oLD5np{e9sNw%jQZp6h_C<nOvc}oc@yij?se4v{XXV*Lo?)glOGZP({!nCzMYa`>nodjBR_rY58C?bu%pQHsSUTu_!OCs`g_Y@UH{NM)7Do%?M0mN?vl^STp#%U1+cC+50bo9Ue$m<=LyEStS0No+_fsMYugUFUTe@Mxn6T`C)DRYtmGV#dDM3mNB!bkW!y|oZ=^qF{mEA8r`ZqjzgUYrv`-LUb)JkkPi`R(&GD%JU^v=6Rv;UBJyd+HW*fx!-HUm@=#MxVm|s15nyeT7T5I@Qk>^^e(_5uK^O_=l&(4_l!^I@N*2hkKeO?Ochqz0BEcNviiF4r+)<w+-<im_C@%2XgkmpTm%e<(5D^TAd0Q388dF)qj=83Od%fft(>MirG^o>WH&{K%>OPu7nUNkDjcHLR$973Fsk>YE=eu4RYF+=i1j|fJb0>5G$zP~4Vu3vAIVw<<hXhp79T~Psk)v35oo!^D~)cWFxAB6R#Ozth?YzeuuMe46ad`qWeSYI(`;J5R`_{{5#`KqOhuiU$Y_#baczM1c?7GE3ghVi%dmHPUM#i(CC4&&hLks`m>F%k7gmPCI_7MAf>2M42Fr>e-G_-eQ>j|kjiyIxH9>&iZ?RqhDiV;=JG^FYZ5_50T1>r1SNQ&ExY(w`PayFK<I57+I({`U6GW~|@7$djaS$!C4=74g*(Rq*`a6e;tik2oW~;=3RH-&IV;(^NYR_4NqsCrRzH^Z8p6C63i&ujGlka535~7=Zifha}vO+9skt_dUhWL)NdlYP$IP_$KIo_9EnYr+E0uPjSC+{QaP<ubL8ZU12-09=8oeyRXV(eoHNtIF>Ab#CiN6-@dKat`9#YK;~UtQVRLmuqxtDS&R5}J!HM;3yWiX&aII++VvcXV|xB3S?U+xj(ME<66@mKeesp`{n2it!5FszS5SXh9rSa{KJl%gXT;Y#eTBTOJ#Dk}EBgfEoOeVXzCVERana$gO-A01Xoq!iG9B^b&SHHjo8-QxRZWBceh{v!dF&Rc-)IH=H@z_au8~+5)_LM<sw=Md`FHtz^`~X%&%}qgzucRG{?EOEI5T=9|C7d|pQTG&!{^i4wtn6|sn0%*_4_;$@sl^;xoA$i{C+m>v!;)p80Q|rh#yb{`Mh)o_Mh$jP=DGJJeRi8u&zsVME!g9u+Ka`n{DgsF9wQlIy({L9OnwZW+`0PvY)UI{8$5V%u#69;Ti6a2^CQP#(G?DrB5;r)}$w!q(A)|<a>@%{=Np^;T+b*#W8sP-+mE(a8ADW1$E#V_-VVbKP08#`ECCR@%4Jo(EsX@*#8}M@s&MeFm87~%YJ1kn}#^CUKocK*D$~1){CzNM&(;a=A3zmKeH;vVeSpozcpo(ZC;t&O5(b_;!*#cr;NYi+!O2TekA(iPz&{6sL2xFXC(YzdLkdr-IaOQ3U!3<nT32SS_%1cpf%$2eq^;@F8hgAu0H(KL)gbohf5rFTm{4#^(CJl7D>C7oWiKD&qF`k&Pvbce?Jrb{3{6i%#tS?CC=6wxNp|JgnUa+7hg}Vg!_KT0_+drJK^7)jX1&KvY#lX72>P&dSid6@hRKZSG=#_J<jQr<gID^V${!^hkWQz1^afLMEDoi;kv$Cl4k4cJJYe=pLD?UhBjS%?SLodcdT+)e(z;ZwEJ#3@@L~A>`Nc~P`_mx>?dh^urH-If<ONS^8aLa<Y&qHh~rWY*L%$Y@7?9A!mlwC&k2sWKPndrqo3APtc$hZ?Zvu(vO#>mVz{m~o|`0I*E8ZPC+=h19{XZn-F!lP?FRNw{e2M50X`lTU-b^m{~WS29X_ACtnVtzbBO8SR>b-3G3K%OOvxXmUOf8qW((?HzJ>QV?_kvDeO3*)iS^Y!5b--iqJH#B$sco9ANcmzxAmAqc<%kw0`Z^r#q&9zOZCX&xZb??DZdQdzpmc5NSvKc80Q1aWPG%_R`{`V(4VJ2<9+$|HTXwYBOlg%C;4D)e@1+*;Unpfsr@@VpLEL-U%z}Dd4Abf`lD`1hyQsz=IhHH$mjYa;qO?1_^}0$haSQ3uh+#mIJK4ddIul)AG2{?e2>$=Z7sgi#})nAJ`wxs=X$8ma~pH$G`x3Lw8M2-u%B4I>WuvCaCg1buY3>dx~plUt*`bNfPOZbwLf3|zRNIf_EqrQI6qE&r9mq8pMAAuz3AP#i?1bWcz(#)C3&UnX@fWcu6U1Lvjfjjmx`d>MH<>oIV<^~&iJ@a>d)>7-|sQ<XZbDo+&8R!%Htd+GZp^+VVL*AFYunFv=l$@{KvZEZn~|nFHb_8n)Y~Kxb*g0xvtlX@tkj|hJEtS>*DK2S7INId%@>P9e&DdoF{}A+GOi%N8%Cxm#dhUNpYyZDH+$*%R}<PYH5RZ6UyR#cfk$$KlbBV>HnDm(yp3a9{bX}H1V~UZ?Vs0jmot3^?;4Yhh?2*zO-$r;wxEius@6}DRH#^7Wki9VBBUn%X76gYd-w?Wze4i4Us>iW}rX3ujx6S^8RRPI0*jk0Qk?wV7;{Sg}?nLJdZ_%Y>;+_IKW@_5zjN@MqoT$@2-*lm&bZh?sUNU-l#b7waJq(ZrKMUKTQe!Q9q<F;xF2a{Who~e8(BMu1+3!-YZl}e060Lj8BBOT(9yVZMFEValg=-zC#|aNfkfuyh!ssAnV2KZxLUAQ3P?edCK_c=X;_4_dE~$`x_Y_Yhz#WwNk?{U%Zbig$tnF{`+ygdz+!%^tVY8zxPh8qte%~Kd)IMzM78nTO}z7^RhDm^?&w6yN}0X9*>5iKF<lw&4)<7Da*bPUvpWAyuIGUB5__h!FRlYeWpu_T(4f_<tn+ZmMgK2?C!0TIKys<uO8lq{p3kGiDRmeBfeh$P`>k9ZNf?MweYvt=jWG~>r%Zfi0^eC?@g2N-ujOpjB!?{OqT04>%9=a=?=`-sEODIqPoCe_$#i9^QC26Un%}$>|@rgDUuJ?if6@Fqo$)je$E(&i3eBOj;CID0M5O=m!SUAG~`3+tLtrjef)JipG>{F5#y04zLFG;@gMj%&drW@gg?#~@xOg7^QF~nhB(QcFb>O);eEmH;|lR>d0<{vZO*jy^UeXxcWO!ht$lBauSMV-NmX92xAoPLrP1zh&oQ2rvQa-~IP&L$1?Qpx!^BsvL?F)3f3A{#I{TtOrv4ZQbGam2KW{wMnw_OTmg8QipB|6=iF&`v*3TPHWkqH5Kc+F-^}xEb-s&d%s`B>Ea;aZ<3G(6jJv>*BJP5yb5aI+hNy_Kvos*Pugdf^wxozHR>y}~OU7Crnub7MepUlay^|e&27yVjhzWQoaymy!mH^g~D?TV<MhIUP#>!96PMd1J49rHD>kN76fkIUqG2k*uGG4C8TJ578&@HpnhYXt67RV=9g6V{{oO;Plx(Trub*K4|FmiQKRnE2WujE_2Oq4?&4zNp{j4D!Kwt?Uol6+5)+KN0maR$+c;y<IB)k0-INH)PAYw%)q~zw-c$=c~g>w!ZqdI_j^yx5d_1ehq|w@M@~G^ZpFt_#DJ|wmXJ(y<LZ|jKKWbZ%oSP2ff6+wCIcXmjMUSF3%_Rn@8k*P;uM^f9QJT&x+3Syr+&{gZ|XMihO(QEc31>B#5t-!~IJQo-6Cxv^W%Tj!(fl9ffl_vrm8256AqPie@g7IGZ}6{;FDt|N4^nmIqgsh+m={_A8zXDIc=nFY3X4={Kow{yG)@=$hzH)A!=5$zI}X$vjWvd!?nY+Y;M+Q!bTQEIQN$aT?S{{v4|#zSia7Vi||!{-|$mCBAiMviN!5zbHyK@ztY=@MFBu|89N6Hy?CDoIX7<{x_1ae^&UoNPON;_5GDGU#(7xuj_Yke>@e7^MSQ#;;Xyt(C+J*Q>5K)sp4ykqtXA<H#2Sh-1h_Qw}1X2`<tmlW5jvb6ziy4xa_xj9~acGi1_NmN(s`gy#wlBn1cID>P<YKUmdVe`d=#q*LABd&d-m3S|I(&DS&<scrS6xMHeox%{Nokde~PVe+i%Gb?P@4<oQqwtS-L(b1{tPwvL+kmBZ%St_!PoG|u5C_JBVa?_cU3XPh6lX#oGuV~pptigk|K`0BSOke|;h;`^Y`SM%h$#uh~W{NRXlFxT_q>ro$&=QYd57@y7G92Q^gm6h+kAkWX+A54yW@%^Sl4B~&n_o0@E&Cy3~d~I4stczx+4%yaMzc`KloN!3X=UaF#wBRoGs~@|f-S{VXPrUt9;+tH4n=9?wf5g68e?Yv{i#s>hc6^kmhlP#L*2@{FU$!XrF}o5Iq<=|E#n;|GNBv2?#W!aUK%7K3%**Fr<UK{H{uTTor7_M=`{R1sl}7wF_tDSPv*Ifc7R(V{>VSNXdMNQtohON}JK?-ns~Y1f<4~dxe4Yd6U6*=w?QH4i0%x>)$Py)=Th0+*b$E^Md2d{A-qyzdXT2Qjn_=r~S(T9gnMdTh)USKYw(Y+fTMGR*H9-8l=l?OC<^9V#XJ(?r&n|)faNM-6X7M#IeD7v%ehSy?Q83ZA|CZuwBjs~O#w=;);{%NU%)8>7K6MgbKf4a=uD?Cb$EJV!2JN;)f7(yO{l)KB@s%Eq=udjXF*1)^PNDwPu^5L&r*Xe1wm)Be)%o{v@;PFI_*y9P!Mg1`iKEw_^o?zvSQfjFxAm10?Xh0G*5cg$NpG~<|1-u@y**k!uedZ5?O?r__T`L~e)iifzIN*+=DkVHIH}jR2mGgqqq}9mFTQGq#GAGp;}B9Fe-Ge!Zo14D&tXi3f0zB)v^oQR-uqqI+p@oD5B5!yc&i_xKlS`FZGH8xo%zojbB;|FpU-L5TJ>-a|A#w#e!pX`FbmHQrOcZ6dFKGBrd|2`vD+|ikK(X@E-ee6&n@blaGd9~wo4HI0rn;9pkuO6Y9Fsn5uf{prEg2TXZem4Uw@19(!B54wWUKRiyu`F{oFVk&jTl>V4d;2NGVhn`>o$%8SlLF6J_*InBNU=V#QC~h5n2zAlIu@D=zC&4NpLS_#UL!85?Qaf5r0#>bLb8E`B|<Yw9%w=NLzyL`XlKPGB7R?ZbXpqGOo&+=o?nO|Dm4@nMMgd~Y&G?!))U8CwTSe7j7{yQh-h=l2WxZr}ZF1M~fL)U+OP9@c8PmzG<KDK1KQi0z+7RYSEr{r~@IR7BJN(Vs>&Z~A}!)2LuOMH!M?f~dX8LFAUy*5sCCcWOhjJGmT-!Ih|u$d$;|s13-~$Q4)&E=#RXE=w*&twSzFcA(ZK8(M_yKz^z~3zCgu@DpkwvQZ3vL@iD>iotJk^|Jyk&CiBkn#JI{R9A9cvM1Gp>`CrIRmok*{ixl^{m27Z4DLzoOzuhUM)f6kBl}bR$o}N6EC%<W29kS_2T*&F2arRlUz0=0!>A!-Lx+-wk%v=<kcX2asKMk2au}~YjN=hTKW}`3Ievx)*^Flp$J@}BHsjxt^JA#H&3w6YJ`F8rGrtCZW)2u!m|i7vVRA`oHF8O^3$+5-g<OKgV0&s=vOQU$mLe<UcM8;jY^agn24BuCKj)Scxn+v6=jE1A7J~;<XOah#!>F^#VdMzvVsZp|6m=DO6nQLl9eFHyDs>BaDtQ)lJ9!p)5p^$l5jlyPPEI0Qs99tSc`Nlh@>cTh+;Wh5hWZ`(4EY9&!M{+m$iI*;P}9j5$lp`<lD{Yahq|5oAM$bP7V>d&Hgz32o18&iMb03nQ5Tcb$UCUB$veoKsWZu&$?K^ac|CbGbqaYkc?FBXlUWQ7r-qWl$-P(%4x|ny2a>x|!^mC9-KY`dZshLNQRMFAp474Ap5(sNspP)ofz(;#f#eYCB60|MI5mkpoE%BDkR!<n)UD(Maw2s%Igz|v`8QvevlzS~x9p@Ir5+?7C7-9BA)hB(sW-@0@@p1@Us8V|za&4SULZdsKcs$7en|e4`XBP2<lm{s$-k3-qh^zTBVVOvkgt+2Qq#y6$>*p$$mhr>shi0s$w#Q`$w$bU)Yarn@;>Sc@;>q|7K4{kCzF?wC$bnkk{V7PNghD$MIJ!*V=>r=8c6mbdsDlTy~$qGZe%aAC$&4-liZTpliZTrn%bA#n%ssuklcpsOAR6WlG{^<liQO!QzOZp$pO>^asatEHIdw#JczoSJcvA$x`8~D9H;!duHsk>o|9YFQV&sgk`Iy3Qje0)l7FS1C;v*mL$#9ckpHH>CRee8ny9bIMlrYs^(EOT23Ms%BOArwiqwZ>qZnMC`X|{a2A84!PBx0cPSoGXMlrY;^(xsY1{a`SBpb!xxAe}D-;$qGPm-UL?@^DC?~!j(Gs!o}m#F*5m&iX*caeV}pJFjMg}RiSLY_;VNS;fMXEAsTbtHKV*-RZkHk19Seq?`gGZurtr23G*B-f{Ulk1b+s9t0@a!slyxhA<9wI#V4xjMBqxjMN9wGFujxfa!zT#H<X+MZm8T$kFJT$kLK8bEGLZbI!%ZbEKB9Yk(HZc80XZcFY+jU#s?_n^)p_aJ|*{JR%?&0_HA+%k{4hq{)$hkTlPh<uuSg?g5Jg?x+pEBO}r0rd{~0r>;<Z*tz=@qwQWuFPU^a~6ZWs3x)(*_&E}>`iV<tx9f7ZcnX9Zcpw+El=)5{)$?L{1v$a)rs7J+=g0=+=kqWT7cY&+=6QCDJ}Tf;KtPFWTO~dk9v=66obE@-Xt5vU`OgDvQZ5FMDGXkC-MvGDe?>QT^556Q&Y%?$!n-{$!o~pP~*wdspF~f<niPv>KJkqc?i`^9zqVH`jdmmDzzC|B{yO**p>Pv*_B+GTAy5*T%PJiE>A8)tw}CJE=8?IE=6{vRwp}>9jG<P4&)NlTI3RBCu$wC6S*|CF1a+>h1!_xLM}&bLM}(HNNqu`NUlO{ORhq$P3=goO>RK#L2f|ypngsEAh)BACbuJZQU2Y_y091=oLg4rmT|e|0E@xN)L?Qj>nF1qtW)=pb#e~%G&zTSn|g(On|z;oi+rE_7xe-8FS4B-^aI&YWAC$LF}OO5!Of`6$<4?CEC%<ddXf8+2UEStgUKVPZOJ3ZW2o)PW5`j|PUI+ZEcGjLEIE$afgDF3M{PqMM;=RUMIK9zp|&8$kRz#$$&uud)OzHR<Z$X2<ZyBysw24%xgFKmAKUS>!A+?z$VM^Pje3`C6oZ}ZPz=7#e?LsVPTo&lL*7qbM*W7Iw}&ocF?d04nNOWYolc%co<JQ>o<NSKMv<e*!>B{Z!^nN8LF7K<4pf!gf!vhZh}@Ly&SJ2M>Pj||D^M$wE0CS3<;l+E;?y$a;$(YjDY8AeFx8P<m|T$RKrTqOqn1$qIr0=%s7}hiKL!_|mL?Y<7oxh53z3UZ%aMzai&86+i;{~`tB{M4OHyl-OOne{8<5MAD^WejmB?RE+mXK@H>7qUHzc>B29sNnJ5k4xJCXZSSCadaV{*$9YASUlIhA~jdVqY4e2vB6pQy=XLv`{`<Ugo6<Uh!dskh0G$*-vQ$*;)oseh5*lZ)CxjXk|6_x9@KqU4$^27gIyM*foQLk%GNko&S2Y^L@no5`c7gUO@F(bN&-Xz~Q=81e-2L~0ayB6%`3mOPo9K#e0OkTvQ!vPPax9ZQ~0o<@x!Pa{vIMv|wJr%*?dr;sO6!^xA#@zg%#c=C8^JMwt)XlhgPX!0Pc8+j19Bh{JQk=!J=)S`Y=pw47NjeEmK7K4AJ?kE39-bP(UHgo}b8+nuR?|otui^1RKmW|Yf)cNFv<Qddy<Qe2i)CuHC<XCDnIhH(vI*dGm+>hFa+>iVfwFCJpa&u}^a&vM$syn$JxoU0+^tUVEQt-d~uS5R*F>+DK_aBM;zrUIPYjxY-td_gE{_`b!pnqXw|IXd?3&@Ss%Q!(${tJvdKBE'

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
