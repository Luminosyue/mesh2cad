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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_004.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_004.stl', 'source_sha256': '599aee1ca77e16f50090844b0f81e36814832fa05b9468d72af38cfebd075526', 'input_faces': 647, 'input_vertices': 473, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2924056649208069, -0.44820547103881836, -0.490466833114624], [0.31439125537872314, 0.4001050293445587, 0.3345900774002075]]}
GEOMETRY_BASE85 = 'c$}r22Xqz1-~RW~!B9ksAdpKhp$9`17Ew@Xp?7kDgkD1x1eTfrQbNa2mKsRtHS{HvKtivfdVfd}L7E_<l=sf}c`ixz=l`7ld0)@@p67F)470PdGqY3n7}zjvx?CFmE3DNiboOylSxr;nqvg_ug@g|2)h%Rj`ThgHcW61pSO0l+PLo!R1KT;YVcMvY!6AdYg_f-0ELp32wUT9>CA$v@9TM85f6#!?;1K24@6va0h{qq?v&+B`&+k%Is`{68`j;;29PRvH{+Gp51pU~~^9PmwRQR0e+KJohc+~h~sQB83#ur69uiveFYkF_^hxIE;jYqvMiQl;({HVUym0GXc#mVn&3nX9TR#*IeWQGGOy;GZw>m7S?QmJ$KnH|bE`v!^cT>t!%QZsEwOZj@fxU=fF>&_g>-&tlxy!<`mZ1Ii#k>cxGaa`AbxcFAsQc-=pTk_GKRzHisAD8<w&wO@R?)T@)$lsMUNz&gr8YlO);_Mm8KQjF_`TN|A;=5jL7vE}M>xBG0Z;xG4{#!Fn%kLr4QXcme$1%Ci^giOd;@(~rKkW=$cWwaE*Bp;}iw=<dwS&h_$?x}*q@K+y{zsMXel$gV?T=ZKUMp}8>3*0Df5@o|@_YCfl3t&3M(Wql$07egF>+lkazFe`8RS0nEOX?#`p3D%*JtFCavQk^#^S!7B&NJCJ@nck`91Kw_*$*Ia$nku<GAjnlSp4~^gi(y{4-YSb7N=m%_p5u{^J$px@PrE$S3f}1CoF5Cp)E{`<zRVa&KEA>5aB8B%QS^NPMl-WVDBbCAjXZ#_&7%NWHmyJH<=Ah4_hYEWWx`@_$uG+MC{YH=bXGf#PdzZw1SBjRoSHYtWwEO&UtQIn5g4TZ_s|J?p=0IwtwYWfEW8cx{&WH-opz^L=#kxTH_BOrDRPeKztrF<*Qm^UIy`@8+-BBiC~d6<=@n1L~*Y8|e?OK9$9H8ds#At-^lC<vA`ch4g(#pnl#zJ0$g7;)e7OE&APDQR_wpNx$bB{F__XN%;~BZxnxERQ$j7YwcDe@!c&(qy5x*ctrBw?<>BQeH#3IJ>|ZvrfJ02ugybw9Pgz5&0~K`d(u8#CH>RgFADA7cn*K3Po(&N<=Zd$oY;@{*MHq^sTV6=+KKV&Ch?t<221|t+-G<Wofe9(uQqYrs)zBMCL747O_206-Fsg(s)=v?vHP<8J;QscPvav$l;_(XtK{#mKbGq|R~JG08H3Q?+W29dnw|~mKTjj|sa^AxalrXH>Ztg?O_%3xWW6EnM9Vn$DEgft{X)O@LY|-d^eFfd6VYBqWJSBmT1R}>n;E!YUtjc>yk8tef37Ld%e{2RdTF;?Ya;#1T^Mf<jF<Y?npZlCdb^B%I_E)*+;2#^qbNt5_-1UB^mpd~Kk?ni7Rhy8&04{qUle}tjW^`_HH$Au>Fe#rh;Qr}7M{|#`i>M|%hY;#O5gl(HJ;Z|P3rqYK9MWX{%d7wi~e31^*JF5ewCIxQu-G2ah4i?D5Y<3+|Zq6*Gl~)ojoFc=XVFCURK@NBHHLU{1L@>$^F(Fh4wkMzxdjVUeWURHzCr#oxc6VxAycz`3nz`cBJ*`f%KPRFfQj_A@y$@xO-TBZ$2gUtQV<}AlI#aQ+(|%#w~Z>c9LE%A1l5)Dyy_Jv($8HpUxcp#W#ix!*##mc;BNV(jWQ>{<jaLpK3>PBmZ)V7=NM%V%!+}6z@rnpRS~;a$W29tKypvM&f-q@w%ip*KZSF_txjFT2g-F`;p>XFW*?ATRGk?Zi@6(Ct&<+*HQ9wZYhK7rYkS+8Q1qaC4cvbobY{rM!g-}liHuT67`xV3;d%#@V_Z9?+e$91nDnEgQxQRwHQm@Yt9noPe{G_o)+J=El8e|GyUgMe)obcc#p;0m+QLDT|zzAn}c@r?pKs2=BD`ioqFQyX{zFV8=gh-w@Oz+`n11coLSmHe3yR(<UeXC`tQsLw3A+sQD0^p@^P1z^ji3D;_FsN$;a&14Eet~58tdHzPnosq)$wM|7s@25&!(+>mw#3|Npq~d?VlBy|JYk{A0gk-j{!*)PtG781lJRO4^}o&H~BDn3*5GF$DPxijekZv^acF%6)Pn`rVbqG7h?@P88o5d;;xu>;%c*b^D$?CnG#b-rugA1;p2Tw-sOedLHI$m8YRRxi!oKZdZ`{ah?c7`k$irOFp&liElRPhV*xqi?8)qCC}aUad-G1{e<*4j-cNKKTnkVst_c;-XRI~*|5E&w`Mhjzj%T8&R#9iPNsh<zBOkc`d2+4$<NuLrHtdQ75z{@p$p{sx+dh=E9vI1<b3In+>i6Gck-UsBUYhbwC;FPuAAnf_?G_<(ym=a&)~VIj}%|qiRbAKt|h)ZDL{PZn6)U+&4ld-Q~2I-$vv*UJTJ3EN%4)1OYy$m)dTO5#=c13ubi|WE#I!ql7HAINWY{%@@ZKE^WwOSd(e+C4mj)nDDMT=gZJ{DbZ7Yy{_TrWPV>z_;(Nyp_d|b-hlB3mz0Pr4>-wLS^7oje-6_jy?)AaAeefdkx4n0~zWu%9_3iJS59z({mjYSaNO}E^BmKiecyGL|j`8iQ$>M9>5-`uo6|hh0$66XI>F!U({M-nW=cw1MF1}UQ5A(`X_tAbvZI<_nb#0dPFVpNO?a+NGSbY6RcRZK9jivo+lj_31TTs?1&cv@If7i`o;%l!noy2p!BKc^!FUdU8IM@Z_e9Hv*Yc9YKSS9`4T=1FXqwU`zzBRZi)+Ni2NP2zeV)z_4w6!Nuuh+U@p86mU<~_q7OL}v20P;VZ59_Q!;o`gAm4F{v8S9HO-QXAZMLt#B7$^I;LOl$)A@6e+#~CC3rL4Eym3QDhf1?Zf(XyA)zpS!N#dogngK|D9h<QzHsm<c&z`WFXFa-T+*y0$;_n{&0L%r-<j1Lzp!`~B&_Wv$}JYSd33whsbFFT?<HU7kW(zp?wvR_+Y6+}5+9uePMw+!vp?;+NSy*EUs>UR;Fu%2o@ANkiEkNM-JuQ4t?=^UN1U+5dpNx$&=-h5mqFGWfEJZ+Fq_f4t#h1Ykr9E<ipen)sp-`!)B_|De#m#6e~-j}x4*+R7HgLQIU-j}<<0lWvZOoRU%>rkucLOkC}6U2AFEFsTN%bVe}@~yn}#n&6hqF;>p6YVEmaq%_py0VHU>Ghr&#kU-PCZJt~O1pKZKfG4_mvyE6yYsw2zc6=+uT`9l_r<}B;+v1QAbkg{%gsmeX#clM!#^K>5%<^ll+?rMEaK}u9Wrh@ujCNldj32rRXYp~Kzq}Ff!{3z>$Gg=F%HbQAineFchWD+S%Im1<L*@S^NGIjcO;6hkEw=zg>%_)Uo}R<XFE4WFTp;<!Sc8+=YiUa?s(4KL)S>Xu$;!|+P5VA<6Y8@^i$LEUMtoa^SZ8UdPqJGir~7zv8jAxRC@8vKYvQ)YgeXW+}OGn^U1)+PYy^wT8VlND|RZSuMaTsT-sMk<y$S=;5lvyOywIspJ6}XSi;Fv>C^s>e)zg!YX3n3_E~;el$h$ekA6je&)PY)|4CNNTVH*Gc3Y;{!vp`)kG#Io)WA6S?The~zPBIgqiZiul@HsqcDerPl)e?V2G6DF9(f)g^5=X&d)lK(N?-G?XWQi4k<#~$Guo^yhf|f)JI?3_qW;a-^3RP;>ASq|*$3%Pq$+=g=@@6mJxX0awYX0;V)da^<?M(32knd7H&Wdf=S9w5wXUa1pVSrosC)FSfAfvF7gtmIde*l1_ko3vr^^4PpY#VSqGhUjc14(&@4o&cRsL2%L*CcgnQlL)$|wJN>?7RqOXceU8_`cs4?meQfBj4c_yu~V^0f*<SO-inFc0rif2oWg>|aLg09mKF=Es;ReP_mC^sgpCYed6Vp!~j*Q2wjK#JBfrE8>y(M#(YQx5@NOe678oJb(N6;NCD!eEWD}l{$;}iEUi+`u1_jbR>yyAKzTlpWwQ-ane|^P3Cd-aoE*rxA^vP+uC~s>22e@vruN)XR*H*^ks#y|6+TOSf?6@Z-4K&SA}8!%l7{A`u6vidG0RK+unml%<stmuQXT}#%9BMb4!b8DUWSD@%r}nve*Bw_wUpW;@jWXUf(`X@cQ<7f|+q4%43^vxYI?aO8;SgGV>7fx6Nnt7jC4t&40A0r^w$nUox}gkbNdgTP*eC{%R)XT}_sVuP?!T%v}`oF>Av?*~fBz`D?26i}kFGtV`_kI%kDvvd?PzKSVt=?~V0!=`ymv>s}svS;{+N{XEg`&BV9Q8};-dJJ1em;5?zl2H8h7`|jG2sy%c5sYTxs-#%Y;1{IclYy14xY*<`;`+V5_whDaP{MlX7g?w!DZ6j@@`1bj^zG9>J`j9o~Z$q=(l=@q+6X|X9d{>?exUOxzV2pXNGiCjon<q;ByNY&`eNFp1MQ=O<`<-1~S0vx<YZuAyHe1BEuXmi=-AKRpZ;XevyI?)_WmRc+_H~msd!n2>nHg%zzO7#A&McHOTzn($BUu-_4qwK)@^+N??)p`dB>mObv*q{PT}XfB9-eQ{ALY8v2JzzS1F`PY@7KV(&*uX2v8^|~zJ0yv_3i7;59w{|P1ozoyHoZ%?>g5yaC>*ke(hZsy8_-JAKN<G>)Y4eR`v{g<nOk1x_KzK`2V%8ca`3gvOM1X0cVNN#s9DUgq+pIx9>mbWh2GcJB4B2D5)m)sWM$gJ~5-D-x}{uV;`fEW3QyQ?T46WbBS-?Ke6Vv#`?^@-x9C{&vWxOX(z_xgAtN0%o5)`)#R#_BXGSg*Snqv=M1*}9KB9}_|A4y&Ph5~$t99sLSymm`$BrJF7R#pNLssv;@kI~T!mJNZ{MfVhsGeiZC}f^tgW1v>V2?3X12xtnDb2o*}rye9Vg?P);D~N+|QB8;@kJ%4D%57yKVb*`p$efU$yP;IcFAzzt$i7fMd7Id(QP)QTVofLf7T`;+uZQq~1(@p46K@FHC&<KBQ+{7T;BP7xvLU%`4-lQ7sYq+x9c9d>7%{_CKwS58&JOOZC8tGJf0lU5z06e`253nTUN_{qEQB&-cVW;?CuAo@m?}3BSW2sXzDGdGfw-2hGJfn|*&c{Z^#6?I*i8@51|J?j5NgZO~R3Pt2x?;=4M&k?~Vc^VF34`}))&<QI<qb9Er*0rQ{2zjO%evI5-SE|LlTwRxnpbN$h~)l#l>*>G-_z8v;n|2l#B=e?XbXSVIPo1uR2=a<8|e1GoG?+(QK-@c#k7>0dBzaHp!qlV9sa{c~2uABQU_ALwHT)_2oJ<ipyVjZX_uEc)XiS5YWcD~@66o>M>Z-#kdJkFzy9M_P~W1LeMJ8({6tbT&@wsQ^bmpnMnnT2x@cibSPpH>RzmbpGcd)%B>zJD;=SH?N*zz*nNP439~u*+E+e&us`UaNg%Kg;d&rTBW-a_oCP_m}b-6FZ4-KbNsa1|gsB1<%UA^L@NR+FiK;D5vdwM=v@E`J5PWQPNlHjs5qyiSRG}EcI_zY>ahT#TCduU#0U>{(e)iA6;S<&i@Y_m2#WSenCBM*^Bhe+Ms<tdfi^~n|c`O|5~s_p3~7gG9J15oe<v~_vnI@chzSbq&z-1k^WvIj1QG@p5?lG2lZ?_|1#%v#5q;TZ5Ur}F2nk?T~G1#vg>hvny?(_N?-Ry{n^gloPUjiZwBLeHykhL-p+(r@r~2*m=_HQ#{1%j<GAj_qS$8*9*O7I>MYVP#rdFB>#m#+TEFDS_XUrN<M|f%lX;H0uL!=&u+0;^zI~qH_3iTnuWvu!{E*&uzUlSt=cga8Ydb&n`u6isYgs8=w^*@ANuQyP+_(N?S=^WH{MS{bw)pn*Xe+}glylc4?4vHj`L%I!GOoKWPTs>>_UGfJzm!;uavqq0`RDTMI3F*U4Z8Xr`cELv)2+n9;@i*Pt=uDd?l%<AYkCaU&l46LL;p<uJ%FAa-)q>vA22WO!F3(?R--<u^p$cZ>_h%RF*qN%itiAdQLm8ygB93EnuzZi^kEL1-`c)^_~7@uj(v^BC$X-%=ES+H{X2?ujnLk0-(6_6ug9nCFIHqB`F_KSD~b1y?K=>6L?xVO+P@oVFa+ss-<dcgPGVdfxD?~$lL(A2t&`yAe}wn<jax_`H6Q)K_MMFDSZB<G?BD13tcO4KfxLe$zm|CKG~bMQO7<KW&u1*edne*7)`hn3e_UY>oL7w7i}TZs%aG5wjM(S%pC<1+v&kc@fA%%U`X+cWzW;i51L+fkus*YWkK|l%4*A%=YclTNgP-4x^XrR?QJ?9bAb;EUQF^0X*q=!H1mCS3$NS4FP!03k+8L!D-TydFr1W)HajdT{VP8(m-U$05cN=0J_`V|M&-IpIAM`%H7jxFWg6F#CtoZitzVy();P>k(<+u7r;JId=hW%IDcV&8!W!M-0GC<0yRpETB{Vwc_R~U=(w9kuq;*n=a|DZd{KRX`nuV_ZuN6|(e#q-KM8Rbl>0Dov!>_de)aUWZ%ivM5V#civN^!iYoe^vet&oR0$_Wx|(*J<fzoKE>%yx-&L%Z^}ws7M8TpV%`k?(2^NXGDEQ<Gw;Ilry@S_(rRPc<vpu;kh5~iu5DP;XA%Hb<u9G4;EiHBQei^ivH$2aR&L=z9%$`xRKAkCzw~6+wfeDl$QB{_G|*?lfD1OxDZ-deEau`uKIP6-W(<QxC{0~K9z#RH%84vzpM8a-(?N#2S3M2>_Zl=fcu(18@}zkN_~qZzL}#Lu3NAf=CA7yp**(lGqqm}$b7=+@-d$8h+ohTmIPs)a0cIb8aF#&9=|C59Qwf+ob$c(k@<%9ya47gw(m<_RfoZUh3{0YZP8eVUkexC>H84hH9b6tdFcH4NZ&R$`^77nN4ei`hkvCA%F`hh@15O$if@ehNXoC@&m!mjW`{3i-s2o}8T-j=8sMD%W^2rc`uD)T$$^S8e=twCL;A%%rQVEEB{A>l*&pe%e24FBe=9EgTw0bL;%hncVcnA1+9ucC5RdeC_hBFEcBw7$_ty`Re^7eK$L;E{xK0XRU*L!L9DR4Ek7OQcE}4VtCe)O3FL%wH;v27;N<COJ>&U#qcvA@T&UKxTUOV?gO5fNsP4d^a)e1WpnCh$OBPB9)zgS4qRAkn2Y2CY|_#|4H>OZgk`zO)8s{DU_5*<*b>i_kVXt!#zp7@!e_!jjZ`4;&aL-Bp;Cl2s^a!v>IYjRHVR}96W)FI?h@>J?f@>KFX>H_jSatw7dIfi_gdW3wK98Wz#jwdHD6rZG?BA+Cmp`Ih3A)lvSBA+K;rY4auldn)OlCO|2FchDqo+h6qCsL1-6UoP@N6E*?an$|fIPxCqHu4_w7KY+=)aB%L<VDoE<VEBe)B)rf<POy8<PPMD)IT+FMe-jS^d|Wa@@a<R&D4$L&E%2PA>@(dHq@r%HstculH~H_g49pR1<ARn*~z)cIT(t47>Yk)DE^rGDfwe^A!<o-A@b+crsU7bLDV5+rPIkl<Ou2xveKR82=ZKNEV(~*0X3GabT@ecc_DQVS?MD3Lh@khP;xhFcj{1b7itgcP;w9QFoxovsEf!yk@r&fkoS^rQ~yI&`jC8^{D_*}0e(cz=849hXyA!&7>cV=tCFiSZ8d6kay4=dhT<Glb-f(a-^ofpW*QZWYf)>Hm3AW6A~$C!4x$bs2a#Jd6!)i2BKIdxpw1^NT}7Tio=#m#R{A4(I=LOSCAl5ByhH7sX<7wOq-Q8jM=ekOMT7pOAru$n-^!EAGtYty#SN)L$qmW9sRp?>xi3R;N9sUwM{*-i1bCvZCz>%7yQq!GjhNoWP&|w}nXGg+c^EmII*qJ!B3bERayWT7LvaYTJy~flatOH}wFkK$xeK)?S!q{t7jhuA1zBkoav=E&Y9X@HPsv}9{i&JBN(+$v$@QoK<N(%nJ%-|LR2SLBdhA9GCx^3+x-k^@p@xt{SQmX5irZ4Vkh}0c+fu(Ew<R~F`jh=x)~3{M<Zir%;-#MUe8m$hsOQKl$ZM!)$ZN<k)U)Im@;d5CveHEII`UfTDe_u!H1z^GnjA&FNRA?}VklloJx`uUT~9qvUQfQnQ2fdhB^^))^*s4J^Hr=uvF1Q1e#gIGAipEOp`IeYA-|?3k`q}+uNjK}rk*ALP5y^^hWrotE%hAvEjf(?dWEb)aYm1(bwF?MxAJc=?Nag$@^Vki@<cmNjG^`=D;+@|LtacBM^?IoyqLU;x{thze4Togtn@eXb@F3s76<q-*~bAbLsnXu>_aX~)ya9OZKygqjM|;5le?3@rB)_?Oa7c%hFpea`kbLSD^=Y?R{mD}fcJHk{D7RqP`sbIkG!88NnJvYBoC*KBah>=8O~4~Ozle!CO4<HBR3~k^+YyL6!3&UwJNzP)A%zK_oL1t&tjYEM_o$pNB*9=g8V&sG(+(u>KgJS@>FUJc`7-ax{j=LEjgSVMvW$ik*83j$WzFZsjJA7$>SM{$5L04y<^i@hT;~QTB2)OIZu?Owjh@!x1vrYw<1rVt|w0*Z=hZxZy;Z0D1J$OMSe*x<wzbAOEDC8_QXO@M0jErLvb**Gr2R<2Qw7=Q5|Fl$520p;?fMo#i?pMEzaMHi&Ec^RVXe@eN9&SH(7<^BGiA#Dijx^z9p+rT!N~`%@Pd7<rs=9Q8SV&k?S~;$Jsj6yyUzbQ|d4jPf0QEOrb6&E8R|>LSD&Ge8_=)1Eq(l+a1aK42ol@iyg`P5{l<h!yL)`7>cJ-yE~HiJrsvhzjY+<lPLa*`Z-x?R!8z4i{hMAHLiL0VHB%<8l_2E^1h8?@7|8$1JwQG1LXPCNb-DgFY0iz(qM8ga${<9a$|C3YE^P&atUeyatU%yYBq9Caz;<2rDmdLBWEJ#rTUZelE0z$BP;!${0+GQbu_sF`D^MV^4H}0)T!k9<a*R_veGbeJ@S{-DdaE7Ur{HMzaoE29Z&w2T$iD^7IiFHX$!K_a^za%Qq;oaQsn#^_Bxd2q88SY_d^sHq?Xl^_fHg;r?%3P_gfUVp-#|}_h%H3q;AlX_j43)re4;P_kR?7_lOk#L4Bzu?;|Nz`%FsJIP2YaQrv;s*^#_YrFaH4!jZhMrFao_p(A-8OtIQ0+d?&|3&|#V4s{lJ4tYE^n5@)~th6+FJb4^L@mOkc@>udnYEiP%!sL<U5!52&5#;X~ipNlkk(HJpk0FnymLrcQkD^v0k0Sp-twUBig{*WXS*^L$`bn*$bkDQ<!V_{<;fcGRxZ??5&)@QU;v-KS^8AkTgzW!&;zv&yp2+0+TOLnjQ1$8gUBwe=Jh8;{`zKGVp+=I|kfW%}$Vyj}qsSYm>&Z%YkT;NbQumUT9w6@|@1|O0r3cBo$+6UZWTm^vvE)tEtz@Oq<W1zY)D>i<OUO%j|7#hFH&Ua>QM|W})Scv=EbB&UEIF3fR(!%!?+Kn*=82x32=qiB#sE*uq|PSKByV9T-s*{M)H&4I<T>O))B)r{<gN_G?WujpeOMmFEvZeYf#fFS>YgY@tw{|e2lCz&SMo#!Pqbwy?ntdkuF3Qr8H%Sd6wjdcA@^au%wQ<qMBPH(M2=@DK1SV2K1M#8qE3%ekC2a&pL!yf1Nwx&kC2~`4>J^Rr*0!}C(onKA<rX+QU{Sk$syFP<Pfrpp|}IJJ=y#GIxrM>_QXJHYidh!OFq}u48_f;)yci7wW-y~-gZ!%p|}V&H@OJ;6KZDiC*&;DbmT1L3=G8%hGLDHSxf#;ae9X0tkm4(tmHh@Vq~Q?$x17b^N>HIRw66)C4WZF$58B~7A4p4L~&0vVki!vI>`a#($u2l(&RFp_>NkQT9jOkT#@Qa_GMWsG88vtDDFgUOYTJefuVR5wIf;SH1a6&GKS*S)EQ)@o5-ul$EopTr7y@QsPCyS$nVLYc^W`{2lPvZ;(Sz<CLez*e$IavPgZ)2{G9xZdX%j6Dft;Ww<Ed#=VmCb>4_$u_|6lpJQ3K?ktSE#|JVN}EcrjR=dPvtpN850W$L5!l>ai1XL9=CU_G#5deuKXFY`1qNEBBsO#2_>tO7#'

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
