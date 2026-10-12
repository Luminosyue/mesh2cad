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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/29e480b958df44a2ac3a4ed12b7ee1a0/part_006.stl', 'relative_path': '29e480b958df44a2ac3a4ed12b7ee1a0/part_006.stl', 'source_sha256': '9f4df9bce384ca04b874da35b9dc1fe6378e40de6a006ff371b56a1060908dec', 'input_faces': 712, 'input_vertices': 459, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.011793536134064198, -0.19956925511360168, -0.12393806874752045], [0.09325923770666122, 0.05227735638618469, 0.23443645238876343]]}
GEOMETRY_BASE85 = 'c$}r22Xsy8+xB;q5k?nnFpd@xy+kiti%uA$4h|ATO)+}edWmR>5`;sdw;(~(t@lv|W3)NOm|@0@5e%cgx$o=pf8$%<x7N4b*IM_we&@<_p8f1+KYgDipjG+|UIzXZGu-8GPM%rTFeI`XUdD)^u;IadgTgBe4H@lW<Wyh&eblJ7U$+V9>S2s9#+D8Y3hx_My0)Wq-F`JomvfZvH!N&;Snr{|hJ^(NiSOTgaClIvA3mUWNKoo$pK5-!$~mf*Dd!mP_#ghul3E0pU+I|*Qq{~??!@6#wbvQP<+Jhgf?1+g-IQbEJN%oTl+VuS2kIM96+cPus2>oa`OKbsRD7dPi_`MizIIrBYfg1d?|k_Fn0$7xd8xkr`kChMYS3Eqw=Z6wqv^kGcSL-%-Oe-e+10vFr1}}dY|Xz%$XPANha~mQCJi)ybL+pFzoW(Ix%&6&|7!l`fp*A0&kp!2M{7ClW<gp`!<}uu<{#EU^Rf2*q4`)Vzf#{W;&)Q7doaTu{XAuu`o{iMhc*8mue3b&$no%xztM8Kv%S*t8$DvwH-Gayp7ws-KbBmef3Gk=%i|a}QOo1*l%T#D6^`=6oYnF;_jO*V*J<IS`M9I~G#|tFDg3QJp&oXf+nLrkE^pNGSeY85oG*N$^#0<*^t#SXQ&A5WJHYo{h39oDMz3p!C8}@K*}PioZA0Lp!)g7x*_X4P)whC<s&6M2)_OC&i)g)>m0u(MnE~tc`$wB2pZjg1)z2QjS?jr!`=IKXVEF4wM`=E}UZ`(wn+89&b%LhrRZxA$nke<Hw->ei?#5lU{KlArNWbd&PQBi}j0g04L(jqQ+!N2`Xa+o&rZ13>bvQ}W6;Ifw_f;;}B29nq;C}slr{12lzIA-#Ud<=AP_lmSWpku2uv_obc$6av-wRaVJe>*kvoIt2#Ze3S9GQ;(^={(UPkffss=Z{Pes9uA_3cB;^f|gd4AJNK(KqfcM}HaEN1waZ?Qi50>5uD%x{hl4lwONfn?|YcbeH+WHwIUjuI1U^0QEoY5BNi#YI;YZ^+(V?N-WXx6pqz$8qd$^_e@6v^^JV-@XsWl(EIwVJJPe?+3!5pY5D#g0KdyW@MqT5_TzXw0{Kh|Jf-=zE34OaZ8`vdSpuGW-aoYcTO*#UZ@zz`>0OUc+4{Lrxuu#u!bk7N<$3FzUN2i9{Kavn^}cpY(Db$uroQ=?2kQUJEKBu1evO3B@zA+HI99)Zb2;(}x`F$3H1yW%oZkq4=lo^rpFM;2KmHy3(U~+KSL*^g4w``lWAyqhpQC-2>~aF_wR8;He<SUWR)P1LkGn#9_^<DyU)QdPakzLd^{rROv^_ZeI-O1H8(qd~|1!4sKzTm;?iPVs&zWzdy`Qw<m&~O7*O=$2<DVT+e;L~O58D2nQSS5lysCGDKe`p3W7NIlXdffsH?E`o-Mn;EuWRO*s=igFIPzWASNn@I@d48J+Kl?i*Gcm+=j2$f=@;hG{%qelq5aXcil}ey&#UdzweEoSuaCavXrbeV74C(43o8qM`U#Ztmp<Cwte{%(BWGj$uU8oJOP6NIzqOaPD`&)1?Jv&Cp-5k4ulnxsS=4vsi-doq5z2pNkM?WZbGiCP$~0|nme)3I&t_)$mS?tIdfo607~ig4fj{dZ>N(^p#+fs2lxJMT8O^8NF!YQ4e<A;_k1&q4T&&O0-1Zj!^U8^u@BYabv^;|wtx$h{omrax`ewbZ{pf=Fre{x`Pn`!>x$xW`A$>r9P3I1{qW#Ey^riaN%BGs$SbX7>eoo4W{!t`Y>%lRoz^=5uWmiFesq^a`)#0s>e#5-6`uFo;dcW=lQ{eY#w@vT2@?|Z*qtq(+r@f-}`|lTEKH6S*rTUxl>$<|OP*B^yYo@>YcDi@R(SFM6_~Y&!g7jVmV$!yA$MO8Dv>b0EFfS)8!?;A>i0dAw<%{|o<q00GzUjz~eixmB=is*k{;6TO-=j4;>i4qVLOy*$wSMgbz4W@)hlfbN^`fRX<EEj$=-YltcrLkHXg%9OIbE91`xI>_jweU8Kbkcgs&98*gK=!n2CUEW2O@n!mT&dCF&(r&nUA93PaPYn>C>nCPV4RV8u-^*uGR8qjYc_7?_v6l^Yr`9GU#9XPrz?JY@S}f>`nCR=qKu1mC|8eiJPP4wP(CTdbS7a_jNiio6gd!)#teC>gU*|`PFO>f9LT{`u*jTwLC_-Uh12>>!N=ZPe4B{)lYqU6vkU~UGH6KePgOa`-NSjkv>P~mqXx}?y3FD9N1U$vFY2<?a<$!m&7_P*I4zf#_!O7BBHckn4eFE&+){3xbN5}zP%6k75x<B{QG&hZejrDm%C4~j(WKm*R4HQ+p}}Y#xrSs!zV06^Xok_LH(z($lv!q#<z(>b^Nq`k4Jir&t{fNdR^;!GSW}jqV38utp$hE_=a=$P_)N^iCT{3uaJIYeH~ZrXb+6v^bPm4@tW>s#SQwsnc3Fp=W!WOe&^2Jn%-GMeWTrWjB636vF>Wq8vcOGqqSdkdx3Sh|5xy@T;8hfJaQPuv2w%Iw{F(c@zee%C+3$AtKi@7r`NN-TZ4Jy=~nnlJ@tO=?w+gD`bO)Gi}d?<5;30qvLAkxMY;~Me!PSGKKKCszVR4O=1$b{#1-cehvztPx~31wxnDoWdcybWul>+f{58hSdHLc{U;kj8vt!d<{XDc5()({+qwVCoA-La;U&A+63_y7vYyFuG2gae_G)DW(b5`@Q9Fa)xUWNU~=p6?&pAXw{-GDn7w+jdM(fds~sJ?ZeCdOZTkd7zL$H$S+-h#T`u!d#QcIdqEBmC1_rf5FV_q3i}=YE4<sR_n0=Q$n6%tJ5W#|L5l-{3l|8e1S<b>Vu91FpY!rS%Q(DOjgJ$~{iYy|}3Q_L90-4_|7f>w%BHalO3eZ(q8n<CZn08hqEaSS`;lei%1GTBvW{%YpIv${c+@AAO^0Wz<v0F1kK+1_!|3QaM8N?b27Di&<w9{D+=cHzgL-b-P`9G0NHbSKL=zC4DZAVzEg7Bp2qFud^n9;uk!=Nx$bkORsBrZAL!n8e%@JP+im8*><AdZaqi4pHNW8A0tyT(#H(e^v23&n%?>PB<}axzqszXe4qGMP(0H6)KlO1^D6vaBeDLk<3hXo@e%yLn(BQyx8L9Pi9h5%`p+Q??Wo<jwOXE^_G7(Tz8?0!^o>HEIu5(nozwPa`z=-9n!60^`9&2l|5jXu^lx&;YyHk#f_-`Mt?<3u>iBQ`@%?VSFZxzpZ=4U5UyJ?J^E*htFbB>(zG#c}^>2TuZ{B~S_v;?sUa#wRry!ra(a5LjAZ>3BJFoV8Ge>`n12rD%IBCpjqrNes1jef_w=ge<2E%__R>ud2*+$1FN9SqCXXG&S$I0Dves{KvLVB00o91sW({bLF;|lz&OXq93-%Y~2n$8V>)U%D6zW=_%pZFzhy-!!ABPh>D-&z`^<+yc3%Wu8;73JB!ANBvHH}<X1|5V>L-)lWPI~zDZxtDIe>bA|8@4}wrJmF?$_07f=(f*x7PNwzk9vAg~-LHz`vt0`LWIl@hU6ZXir%J4feCDK}pN^TP^Ow1`w)%$Kw}*cJeiO_)QJs+9>WFrmwU$0dXO~4tzw8&BtDNbe&(UZV2mh>(uHWp<PMkY^^iy(Tewua{{j2g}_#w%<Z!#`S*1x+-T!4Sz@eKW(!=?3X6}bw(Wm{dB8#%72I&%Ju`;J(N`FFlspO5oN2E7lXSy9Y4rAA?%{W&-8?|B8Zlj+3+)B33cr?wN*J4ySg>$}qGTS?{gIa&vvCuzFV71X!gGjJ}q$HF@Js2|doI;rW63>!4PwX7HNPm0I$%}`1Emm_ir%JVPwn^rL&tq1q?;mCh`V{Iq)wlSKItLZ-ElQ#hU?&JQq=4o8la}oAIZBAnRsC*IW_vW(n`Tbd0=Mi_wJMg0$XnAb^u-%{d3vcl}5cg~4{{#Ne!8pem9EJ7TKiM{_pCKFekJp>%-(9!Mz;{iZrsa!Sq|fm`e)ak~pE^A1?$GO;sjt3SW0JNjNAgLXw;kKNA^pll*kAN7j{Dls8-B&VaXuM5Ligp)x#Qs*e|OgFC3iod_dRBz`j$r!)-7?BF%D$Nsq=(2`5o$i${3tOzRw4LViU|41$SW`b*Akm+}9nHb5j|tH?|Li?|e8$@1s<_&dbKeQ21FUU|yJ$NylC1no;nFm%@4Nmnk|gJ6BAE?_W*#`|b%3&|l_7!p~h4<MZEJ64UzT^hqdZ@4LG{@plGl{g@{_v|X7qqmhs8srx2JnY}pA>2?D5J1rFB!-(E{)B48YdsrWCd8O$c9nT}ZPaV`}#0xz~vi)yj-o4ln?f*8$!;ikP_k*4*n~y)&eYb7igKspOr1i2VUZ0Cm`yqU<qS(Lvv|7_Ut3JVf{k;+A47qZnKRPmOR_)db>zt1L^xVZP_&NNRI0rT#gz0_##}BQ7aqihA&ENfbLG`Wg4&ZrhPltYy(V@Qmq?lgUN($HOnjgH8zWH?>k6a@iT0hpS^2p!Ed$L|P?=0;1pH@S9k3Wy4t!L|Q3#6a=W~!$5{Rj2-LxB2b@(!f`q7K$Smpdc<^ei|h?l(l|WoN<|lrzg*j5D{tUz^r9>;8=P(EPUEw<~TY@>$tI`<wmyI_yIyZ-)PUHjHm?S7KiKHW~Rpc!>87dq$j2>l+(>Liu-j;~eaxUtsxg&6o3wHOz+Zm=&te)x4(jxU>5;_&h%`19s|u!tQt**WHpH`@V+bbzS7D_5r>Z#zQmf5%kjs9kysbSL0@DeQgQR`gdOGuf92RwYE<?+T5V!j9rEF9x+-!?yvsU^8&~0M5G_@#(RfXfx516^|_1mXYyly=ee2D=`qre9gB0(p7qpsHGd6%a98Xf%V)v5uAzsXZyC*7>iMrLp^B~>-E}<GH`o7)d3;|u&I5~;MEblpaE|e^qpk-muPQhv3&eikUf&V>VvlA>|7S4n>-+P1u3)-@;TOGtd96!5eZH<AL*Tnd;{DX)tvwH?_2YM<zLvkndineWTz5h>^snx>^t{(PJV$-2<^!w)eTQoP&IJdzrtL@O#f!M^)N{z+@TjfdJJDVHy>sM`sE6?@FwRfful>>N@dEkRSb%l-#m?FvZNH+rjy6g-w0zD5HF17hsE+#P!vd)PH94`q^$bAzJ{K^*^ev_79am?-PuLcs&(Z5C_G`&;@W=GjdCvX1Fxu6wP00W1TC~qvo@j?#b|8JrKXp8E{Mi%hqIG-WmmH_-Py6gV%ts3^U>`8O9>$*vbyw(pwESW_`q7r{>KA>9^XJCJ;QxG2`@eDIj@GB6o)3KM5Z(_xnTYo|H7de)b(*5-mTuPh*IB7L{HfjaJkW|ci*;6!R_fak-ng&JAF!VHbRzxLt(eCvT+{lo?#)u)yz&m?Lv(h1F3wx?k$(Io_1*qo>1XGuweYL0o2})@SX{>k=aDV&OEu8_qx<^^^smHy@LzwA{5!AR`H3I@7vAIT8i@6F%ysxx0<q5VuB7vxdtwUw7vE`py1&7DQg@Y1n16gyM(O=bh|%*H_l8{R+Z+ds#x-?Zw@T$z-}<K~=7nu37$-maH&5uiX^mNgb<3Ip@Hf=P_%k>G>FL{jHt2mBJH}}}IEogAUnmm&z1sS{X?-IgT+g4~HD2nugjJvf&asC2V;$bsSD%YLw>+-v-4N%7O%7_iaK5jP{2#h--o<sM{jw?YPY55U{+<tbzcaiA{L?2wwVc(kk28PihU?~Dg7cI3TRNW@y?f%im2#pz7xhB_{b2y|dH+D$o1@Qry)U=_82Ii<eY71^O~HBivGK_NSqH5j>-hj}pYB>Sk-pt%w5yO-IA7Zxf$RSI3ggBNPaRjSjWI~?^bOE*2V}x~3h!9>H*V<pohxGro!1;I*5kUBW}^Kcd$&8SZ~Wa=e-~g}e#-YeN$?+5!n(J>5%kNf$?zMk#QQq`J2-!Se-i%lf>Tv*$79_7_A;JJ^Z96Rd&_G1T~Dtf{nA~!-!SuU!ai>34fucgVISnT9P7Q0{;y8dPuan`K61BtgZ$?=M*fY8p?=KFJ5c|lwSBud4qFGas&9tw!#ZTaSe)O`H*UAn@zYERLcY86z;EY)`seets^*8E;lA$EOumP8l>ZX`^d!{t4V=pvaX#u>(WkK9n;VPvxuPP{4}YZPbdNrRdRtr_>F3YZerK-q)qd^F+7Ri@{5qc6b0RVCOl}1~c(vA#Yfl{ZeXqX8{no*`vFrQ0x_>gi?W(@r;uq|@yN}oO#xN)H>G1B8cJBUR6#P*$7i;<~g|PnFvmE(cEsuV8=N|e+o};+#ph(oi?kF8^jrk{#PvI<D&+gC-y039%Jp-TT{Pq$*ZEyear<KRKL3wZ7*N5x4Zq{em?{GY~Qhq`D8F%&E!_{mf&X)!}fuC?`rKTS`0Q-XDdGX#jp$W#BV|Ov09x9CSID1X}&Y^XEoLB5Af%H`y;`bgm%jo%}vBMYphDJrPj|egL>HUAv82K0hUi$a7rS$g*#u9(zGr2O#|G16r>s)zSB7NUVT({(DuIWDOqP`jaCECy1!b|k}<N6@|-rHfC&rjwAO*bMKe*B2J>c?f!@zQ7)h3o$C1%4;+;wL@7b~ayz^l{no-l{+x_FpGr;a~CA=WgW7jrH51c=(@P)cvYE5$6VGvE#^p`$(+E24=%KD}AHw&c%4XRq%TQuPeB(9uYVP@Vbe0<NRyzKc4GONT=uL=Iq<Ze??xDKOjcWS=}R^BL6Ra^?6x)_G6rX{04siF*xt~evjtk==&L-+b=T`(9YuVJBpR<;E&v*`whpP#FL-+M%&t&|GwgS-<DT5_|?l}Jh@|pr}eGaVD!5;k$PSC>_GMHj(xQJuFMm3A8BP8fP8G6Um1-e*6Z~L&VYaah0gb`0};9(H|y?2K7U-+d>lQu;=Y#NMf&L#bzZa{gk%25{s_KjIrvxk{Y*GtH)ah*KAx85;~eRM`8@9oj6XRa=(@}KJOlP~)$8Hh%;8E->sw}3w4a+kc;6A2PknRe2D~rus;=X?anpf)f2qAVf3JQ@`-{=JB=VoN6aAvczZm}m%EG@e0Q-86mAXGOE>u81^`C3`tX0Rbe?94k@>H#gb;6raypO1BBK?wJeQ#^5KabxPBsYd%{bxPbaF4EaNS{}szR0KI82!HE(i80$cJ@&CQyO9(PaLKF&KWTr<=lbu3ZwF0IJfZ}h4iD^U|$+C6Zbo67Op!xyPgj_w?Dw|?n39oKmSh0LC34BljXDPw`K4XpJJa?eT9xEu7F+ekJr@ua#i%jd2C~zTk!W$X74swr{_)Kb!X`Pntm5?F0t^%C->|0X@hc3%!2cYL+Q|-yMCkfW4!Q!|MdpEe`;Qc<9<>2$CKf=YK3_!&>QCs1zKZ#xbCmxnAyG#(oamn`eVmYyk{vf7=E69nvY{_OPt@%nF_x^Qyu4>!*Af6YI;Oc+IHnUkp2_j`gei0C&#n5c(3tx5z=3Muj^0yyCS-dbG=xBa{f30&oM0hS6co->yiGiW>|NIVg7QoIt%~CdYl`?*3$i@bL%5qH^vwHoYpB?Z|3wo+K#MA{k46%v)#kG=xq`Bp-pfud9feTk1hs3`6c#0SzLI3cjO!R6$av*qDyP_oh8Siou2#+>!^y?^*z5C8IAPOjd0#QY5~U8@C1zazrR%9Sz<WaZ3nzRu|wY@pP_ZppHAOFK2`SPcPSli>2+QCb7P*r7K;6B|7lvUmgS3m<lY|GzgHcL?;RbC^p|qty{G3B)c@*v@Xrm_almZ*+ul$7&{8<ZtFRF3t2;L^|CgDBe*U-}#--~&!T<ak&U33pBp(j=<X61wpFMK9i=`GRH8LAsM!()^e!?rJ{QIc?_n+_vSNs3^32%+cRsOd>;cez&7^PF=kpcA}O9-Dg5W*V`gzyCeA^d_`mMq$zEFoN<Av~NKK^9#{7M(-xOC3p_Ll$+BN0KKqgr`wAl0`R@r;%qdgcnkGkVSWqMOTwWXOkC_Lm0wsso#=C2awy6D>H;EP<xX_hmb3fYcYg-QKyha*OPmZCoqH~sk_Od$>d1#0*3Gy>ISmtMDiGND~51ZYBjRx0|T6ue25`Dhav1@2=Ah1_5h1I$P&WR*AA1fP%Du|8<8c1ZyN|<w}B9D&JbQjT|yQ;O%^>%7Cl2=MPA7eUO_!Y7Ck{;L0-lXUP?VmKA9TFQzL;Pyon(kOFc{$-9wHg&t(XYqsEa%=aa{g2Qq|vP-l`wEwX5PvZxoi2e}AC_?CeXzHT6dPZ|hePlj+4YI|~fUatvtELn5}xe2)@L%0q@coai;5jC1Dx{WNloh-VOyokJpA)G|rPZqVwqDRQ0$H+<KEezqc)I(&^z2vpz<qY8%>Or#T0dfp^F+(_tx{oZHNRA@UV+hZnZY7JxlV^}eGlU0Gr;|m)$b-mVGlbhvhml2xl0{pPMN5#|ki8kg21EFbfe?OaAcTuEgd0*@kX!J24XK04qCw<_<i@FyKQ;2nvoa9EM-7DVaq1Uj(ZXa2;Zp`e_%yW;Su`(MLimJ%5I#WtoGdEy@d1W#0z-Hy^*s4J=jo*k;qeUNUJT*U4B;iz3*-x&zn3tCcQAzaF@&Emgv)zCWxf{{9Zvo@uM3x<cBJ+ti;g6BB==(oe?^^47M(`^irkVR>`$FV7F|dd4IzuRCHs>LGK4cwE0aYlkTa0~H4wtt=+z>N_9AB^mt+VxpiUr*Mv@zlJ2QkkQ5TR!$B;Xbt1^VMQ(KWmvy!uuzcUcRF;tnqV>pk`A;*x1GK70FgnKiD`%ztF7w7eU4B;UR;c)6<@?p;F;SAv^4B=VS+vMAv?`JWDXETJSGlVZOgsXT!Wqlwlx{55ik}SG{T!kFK5dMa`j4Zm8{0%uUHKuxCz8_EBL>7%Dk0*yRgq_s6WYKYCC)s2O7o`p)i}oOk79oqu{9Tlvg}-MAFJ=g@W(Y5%UMGv5BrhY+WeA5cgtsw-A5vv~@Q~VsELxK+T8Atl{EvYU&cYC`!4RHA9Yq#hL>65`7EL0HZXt`VB~K!UGlYYw%gLfK<Y00ihHy{nVzOuyxhJ_BL%0KV9$9n-xdXW=L)ecxnk+hq>_;xg5cZ*dO%`oK7WF2J8e|{x2LmB|*FXs0Fc8Ams4{;Gi@qdZBmck<zR3{&n<4zA2UO;JVbO+U(Z=MF2IlYK)T3n4<K*GwQ4HZR)Kg^9)8sMai40+jdV(x^fNYV+GK52^31rcw<WTYehHzKvc(Q0Oa#wPFhOiGqxB)}B3w1PEbP2f&IhY|lg1Un&x{o}9Jd+{3kRfa{gr8BLkVR#_e`fsmIzTub)t4&1FaO?=>`QLP5bjFtM;85x+?8CHA^h4v2){BA!jGvf$)f&b3E|%igz!~rL9%EDvV`yv10j5nD(eGb(QNb&lFt|j;XBllWYGp>3E{sCgz#tlduOs}C-P_Hw+2G^KD8=YG&@;Bc)x)Vj-tx?Kv*<}97P_)5bi`BN*3)&?nE{j!nLWr$)f$pwaN7u!i}gy$fDuoM&zap;g-}XWYJmVmgM#f;f~bVWYOv5j^qvu;pPnC5Qgw}>Ls$MtQ)rTv+$1wLO6vQKo<RmEFqkeAzXkONS1YltQ%T0gzGVcD^f$rqE2!}axsQ*4ys8OElSQo{?$MTCsAeHAS}9=oJ5|)5bn+p4q^xoq^>55E+Y>l_h$$@sdLGqVPq${9YeS(L%175_*?2Wvgkwdx8xNJ;biJRWKmgvB=fWIPX<D`ln1m1S#%OvG@L9NOfE&v#SqR&?L!vrNzO=4&k%lRK)aDeJCG%WpBo6_Kd4Q~qJCrv;ol8}@Kb6zvZxPPRMrQ=qIbzp$!8hDd#E?aqSwfK$U7OriPRs+qBqGhzstPdmO6&qmfVIR+?qO(ENYQklUp!^n^DJ-MMKHW$W0i+b*Tf$qFu>#$rTyG4r+a}s1Mme&dm_cLCs4R%}LHd&dd<b$PmuL5YEmJ_F@Q^q2?v$<@L%?8<0i2kjs$$7{ZOI!DP`9<i_N$8NxlNGs&V0$vwz@8N!1Z!f_1Yi&UE|`i%T>{UQ7_z1;jPzObk-IXAgFL%0jI9a*$1xeK{FL%24zE?HF8CAIlk_&q~-Jwtd6LwGs$6<PE#c{zCzLwFwbH?rte@;vekhVW$S5whq(@?`P^hVWGC8M5dd@>KGChHxzPFS4ktS7P~DINm@AucFF2Mp*Pdc@;U5Av}z_pDY?h9!CC#A>5EUh%DNP+>l(3AzYYhl0|Ei3zG{lg!5DDkwqJk^OL_|2p6I@C5yHs7a|v72p6TcCyRC@7bO>C2$!ICAd5C9mmn8s2$y6C`!j?CsUc+1?c_l6G=}g>>W^g66!J>)UWV{Fs;qm?Q45eIgzu$l9uKU0GEwW1MJtjsk^eLh!oN_9k&AJCBP=0&*+2;IrpmfUSTu>en;gLq?o6FT7VS>%Os>HYF3k|Gz!0uQ4I+yUB-bL>VF=fx_9u%v$u-H97{cDvc4X12WN&gFhHzGfa6yJ}WokFF=(ps`<W>yfKGYRt(PVNT@;HX@TIx?^QCTOgrRE~%;(BN;(+RIL5W*X%>B;H2CfdLd-oy~zLVZpa{e!%PyqO`qmHInb^eI{NELn69c`G@ZA-sUPlPsD@{wg&BQlmOU);HA{!d0kk$fB*uRmkNT!eyx~$fC{2Wy!t_;ZoElWYN0hQsgfg!uhBb$)XN&K5{OG@aNRrWYHYt&&i$);SAKwWYLV|4CHhS;gA1>Js862saeRP*~#h2pD~0pF@&?pGil|K&MW=@>%VyW?|<^X)A-~+eEUDY`RUI}(th(~YF_{Okx4+Sj8c}=8%w8)&3p2sjsF6W>zBI'

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
