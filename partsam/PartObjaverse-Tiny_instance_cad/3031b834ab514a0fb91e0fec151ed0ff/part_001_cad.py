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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_001.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_001.stl', 'source_sha256': '7aba4101d7692f36c8fdb0e57ccec241d14f522120b7ff881b6fc7cd3ab69251', 'input_faces': 997, 'input_vertices': 635, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.26569682359695435, -0.4999999701976776, 0.04430645704269409], [0.27947917580604553, 0.12694913148880005, 0.12586292624473572]]}
GEOMETRY_BASE85 = 'c$}r32UHYE)V3Q`#EgolySR>`Vit2k9ThPniV5QwKvYyj6vZ@#H7lrK4kP9am{1IDz?|cnM_qGV!-{MAy6%0O?e672=Re=)o_pSB-ma;tzFk#Q-7}o^Z<#5xtHl3`Np=4o{mj{0l0@W`T%{2~;Sv4&1P!Y=IBb-I<U+pqr|Nva4z2wI9i$P`XwSYu!}^4K)-ic{2iNi}Z}JQt5*`uWYjDpY;eCUI@7pVMSdiim3+WXWq`WR&qiXf?rmAJio5q^{m;bUWT`*U0xO7PL#r(CEP&p}fX9Mx__Lqy~%V~{Ct1V`~@CWwI;f=*>Q@v|D$Pa$TzRfF8sM)_d`IdIK*tfLoC)9fCG1X&@xx#)z_8_6A?9aIVX1m$9Z?}lo($_>T@0P&+yBtHP-lH$6e*2_#D1RiJUdJ_OzsOwnrK?WjwVXH8F7h)EW#8r72zvc#CD;F9ApEl9sNHN5`KG*m(f_7a>YuxX>z~n@egDHjoR{CIekpHR_LuFREMD7u-f<ps7i0fy=iljd&w=bG_D`a`^#6E8s3q<mw>$HBB3%!UdgM!Sd8mFl={otQ_?MTpzWw!OF8`(VC2c*n38%=nwq36)FI7EAzJ1%do7(bL|NZ1ks{(ZOm<I3TdY<{}eEIlJZr3sXqORQqO%k=|C9m(An2~Rq)GL|#?^c29Isg8?P}|OWI^QZE$<Vi1ck6u9s!V)dKY!|cOYrpss^_;J+@JYl6Scln#-01KU=@|OuDYC{&5ztTOHxL@>FJ(5R8LrHg7&(k*KhExBUf{O8YFYOYme}C>AF_$|CmX>C2=&>BP~i|Ke!Xm*V+EbTHoZ<gnW5<D3_04MZP&#ck->H8YXLfd$ksqwDnsLt>palX~Xq*Yn-h0rBC(9x1S$H<?UgyT#uK_eeHEu{q*sWG9WP{-#VlnU&p9P-2YZix_T_5+i`zd#NW~Rzc)<KjuT6sHajx%?SbVFXnl437|W}^vAjC2jOA57z5L>$3A*vtFKS0dzU<&Y<>jh(w^Kd~AHA!aU(IH0*XC2&+cPO6-#)ZEjW^qnNb+qFbMNW$|9HrDZ9dH<`zK}O+p@H$dZg+twrle&jZIC;$hU9(yqm^DvASH(t+u*$rQGGow|Ix@e49LboA!LAVb_x~^6h(`Q2n-Vp5&X4E~9#EhaV(qeS66%<eU57rt;E}f3}j}Cy@PNr}h5H7F^Gs_dI`xz1^zqr)kN@41GD~B-c~-+!pP8mv1*p$jCRhiP}qfeicK0`nor$=eCS|DPs0M8V|=^*uNRh>;IsbZCYP`l9hb(hwD_{cI(Y%>bJU{Y?!qzBVWGu2bH&uyh^^b^a}Z=<Xbx5<UE>u+oNezkHu}@X5Dqid^h^)dSb7)ezSJosrmVj@9QpWeRbX$%cuK>^6I=ZmQVLl-fD~4tetnJ1=A8T^3~4;qi??Q{t)HA?eFBP>!-QW(0w}pNqzE7pBGZzOqrtCuh56r&v{+;X?^Q#A6}m;r&4)y{Sn-5_71#0M|9h#_07j?@p>D2n8!n==3HJ~2R>g($jG<)KTX#9>FcmMt_;5UV+6HpAJve@gSrmqc$AQlZ!LO@KW8%++N_<wrpmF28Ts;;(p277D0LIndv!I<FKf2-iCSNF9nbT(m>YjiW!cT;S9Rz4d*{m@t#8lg%jNx!Qa$F;+cs(EugxnpL*M+*XR624t<Cz3#<|f?ALrFCtjp+pjlO!ms&8C3jDGsMF?r*<jLui}jpr-LYu9CTzD8d?Ut96$bs6R#zA^vS!}-=_G#-q;Iv#8_bF9l~d>Z}q@ww#a+KlF@(O2iG(O2iG<@*-$jqA^Ue5?<uZ(M)=;~UBw*Ps9RYWW-GxgNv%Z}ipm-`ct)`-b&j^^NPlyzJ*1%9mmNH~Q-OZ~6I*eB=7B`o{I&Ubh|j#&t~fjq8{c=|{eC9aDYdI%Y22n0>>#n(iCd)mu*F8`m+TudZXJdWTkP=dZe-G5YF$#(tvjYVCYc_X9>>-4Cd~aleu78}=LKQGw(e_diBo-T%m=N|SHg|ERuk|6?89H(q;Q>HFjgrQ@~zPrttlDM7w*|7L0E6tC@1`u$yn&#S0i!+ns^Prnc9@F)4k{io4a_n)>icgQ#HV@)4Uas9^qu)$aN!&c`4>>KvsMqk~B+q^E>=(XWK!sx5}eAPGJM;Lu$dE<SA(N8aLZEn-%C;fT_ma}QkH+{eD>u%HLKYhPFC*MlykKsO7^^NzrQiT&M=(XX#)#$7Dt>*WOSLpJL^;z|e_p|A~@qV^q5c$UE14dtcK4AIv<8tkFNx!d$Z+t$W`o`x2_VI<uH{KVkzVW`;9Gac$H{2JizVW`;5_^0Z`G)&+)&I|ZdRlApjrYq&U%g+peNA0LzVW$`$HXPt>y`eT=Xrbbjn9ANBUcw|^PE0@QnxLla)#$WQqoHD|MUFEy9xQm=S~*e*@e3EQtPQxYYS;z%YG_%b~Bx?9J7l3Yvakc#qs{cI%W1&@~79MeUk0NL@H+qd&7Q^ANi(-gUGj)blIjYZ=YI}^Y%w5`&NJQ<=$Sr&*>P(_j5hA@wy}Brh3huvFyKJ%k!}0cdFkSoi9;aUjEjG_a|klu-|wKKgZnPgXh<w6YP5y<@@T+_c;$)AFy9JC$FdW=iGkjOMLw7d_KR}qPunehq?TG;lssEIzPTI=Y16JJ5=A+FNM!DzrMWJ681Bf)s?s2YasLW@Zoi%dN_ZchqvT>blkp<&d+5M``7>C{zqTt`_pIV*|)6NOulm@kHd=JQn){Jcpu~bWF22WiLSS_a23CA*=D|O&QI8X)0Fmk*4mELzUf+JdM$;z@qKU4tUR6@I#R!-*423*KP`=~??T>}Nmrsc-xKOnzf7H@*iRb3`=>dNI4?IAvfnXsoA!FyRy}0D#0K8SzwgcKM$I?uABpGZu&Lqnc_c6V#Qxj8eEwm#dHk59!<>(}1nu}SS+la=sW`7YwQo>)(=VRvpD&oG9iMWGcI;0*PVJdrg!B5-{0{pKb7S5fqVZ$C{Dl2{Re0Q<O5yW<^p*Xn8~j|m|2lr|5ta1_U!U*f%hi5zzDs(uzcGl<_tX=<4@&I9{`malTc&^Fe80Y)%IBMABi(tK$9eU4>>t@lzRiCRKfjuh{W$qALdZ8Yi05%xunhZ4R<0qvSPRb&eb_HFgvOK2@e1d;WeEENUaThHr7Y*!VTP`}6nC1+n_q8d-|6posu$~q?0b*>Wp29qEz8o_zg3xEyNu+0V3o`#$S=Qy#+h|OJddM(joGhwl<x<Q9OUa+F^YZLUo=0Z`Fps0r?KqMDoFL1cTVQ(lKmF@r_a+kFulFT^(@JGlKe&QHc~%!J>Yig7iQlpoP5isg;bAaW*qyw8*R~EFYAyEXShFO`y3MO26Uk7X{)l4{T5l`sNCqRydPV)g?;~7{Y81Jdt085*Y~i$V9Y$~Pa2-%d7ooH{Ks4>_jm&Di+)^Te_k5ZFE5(O>(9go?C<-B>zP}W*SV=5*w6lJEafL*CePE;KiCiMN%fc`*XVsG+d`_p=NisiN6)k5zxN~GT7$=%sd;1eWz#@$UiOA&9@h`ru<v$`%3F$e;r>kO%D(?j`ku>F)Q!rU62jT9^=tz5KhJC4mwt?7-yBZ9wR|hO4stIm`^l&1`zGn@CBFW}qS-IBg}zsk3*X|;f&LrN&!(fOe!ohzewyDWq1_#kq|f<tQf|AC{g8Guseh02@H{Pgn*DcSv#6eM-UrHI7ug>fHJ#dPFq+r10(a5>*E7hU#ovFKPyb+lLz8GauZDA|pHe`!bEMwgV#r_g8~bB&vhUJoG}V*WW2?@eR)@-4b|2)tJ$Gfl+hOwU-C{Tob$?~wd?$)@&S;(=&E465R*}Y=EvgfLU%9k6`^#pMZ@N&N*SQTI?0Zcj-z;zDezx{v-#I&v!?-~1&z71f-<rOEH0`;{>xRFN&Np`)$NLc9PVDDA5UZWP(#&qi!$k6>wG(+ge9?#f{n0d@O>@Tc=fm5+?7P0A>te6|f#-|&0QUV`#qm5z;qkvCg8gH@{Qcvgy?h_~Wg7dFyV1BZ74+lzcsqvuHGk4Lv0UZ-u)Y3r_P^zvLhrZQIX{1|#P#h-^TIA2<N5Bf4fXV#Mz8NQ;m@Doz3jJtHbXm)O#Sw=FDEae@~$gzKMsFcCmL5a_r=_wx5wFk)jm$lJ8P->yk6yd#D2uhIl6h;{1f~43eG>I9k&N_o+tlF78+NwpDX9z-iG~GMVFGlZy<ke1_ZKy^)b)u{wF#A^SZPDaqtovAH6&AexQJb{g@x)={)ym<NTlM#eTI2s$aU49nXt`*$+wOdC@11_gT}z*!Mol^*i<D``<ew+3&oH%G>-0^EfFonthA=NYY$o`E&lDmHp($W2pRIiTiVZ0{g8NOrmz3+w$jvb*iqs>0u0Cm)_CrryUqe<v+_jkDe@J-#?AkAM@!>i8>$sw4e9l`RKV)mmf=PX&$%VZS220Ia*vVbA$tZj#)RX#&u~hk#u4m?&p9_?0*|hzUh|tPMu$V`xKsMeE%i4O2YZ(rS(=$xwu2;Zy8GC)*io|$6M$Q<YCWns@Jy#=ebP^`|Ypucs|pBpL+zrzgTA^jnAMy^f_;>e3bo>tE}37N?A^^KWo+k>c`Wr+bIwE&*;mi6yyC~`*ZBaZsYZQ$2tB!E8;x-Tr@r{Zzk{5`FG~fIv_O<;LpKM7uc`0gyyg0>q_mKcU?q2f19H1r+MQw_CsIMI%D&?%l9dfH`wpiXDYRKZza!*JvZ6kaG1uAx^7rr-$I`M;`3c<;{9ykefD#nr1i~uyF0H-qwG3gK3RkBtCl>#d>KsR$M$z#&QHjn?7NPgB=Rp;b>iolU7xY<)gz3`d6(kxu>U3dk`w(7#A*rPynTPo{?0fW59Xb_c$|!T&%WsteeS5gOEIndfN_;X<3av#fyaX>4SC+j^<%%0?(eTg*TuB1pWgR=JcZ}`XPz&i@XJ@4K;vpf7~eNd%6x(I@SNvYi9TG<F(>wqouU4l?geu_Q*!CbTiY+<`>dxf7qr(){T+_EnJfF2r2eFZ`F=>A=Ei>CsdU}VdrxqFS`=a5_F^c##_x-)n@#M0d`9PMZk2=Qd(IN<%Y(a<KO-}LF661ee#}K$$LzB|aXs(rv0uLGDmu^c&b%(|@?qb4uN%ETtqOl1;ns|ObF~&czL)blzpxei_JQ=fAoGy?e7{?vBl~qGQT;aQCC?Y{uI#^a2%&aozT(fdyB7APxAhOv^}v1g%6_^$*aJ<xpY#}xeEPK&<xR`W@%}l>Skz;xN&Q*hhWB0lr^Am9pz%C>67Mrl&q6(KXgtgF3eo(P%EcfLyZosCKX9M=Y61KP9jINWgIxcG73|;n%==Qub9`Ms+t_cGx{O{AtjObe{x<ZdLM>5`<XVK<m5(K0{8U<@EpPppi1O_k(d+Jc`F><~GW#YU{=66#Mg6f}--~`;vWWU^{i<_$_w#Dr==$1kw%(@mW9LoQ&LdmH2Pl7ID4p-<^Sp2A{Sf`}ZbSL370$my$n=bTub*LB-{SLv{gVxb(Yz}^j<0Xuml&TeBed7WJoOX%$)Cf8Z@yiE_b2QB*41Nfe1Ydz^Ka}YI7CrD2h`uK^YQyP+4%&I6DOyO+Hq?;|C#6eh8*l)97Oe4S|sv$&B)LGyP0&qCTCvG>vr7&?8kV7(0M(H;``7ZMcJ2bx1{mBF`l14M3-cL<UHQbgwNx7>R6HeH6gU#n(L0<t@9^;n@IlZlI+ie-@Y094c7AbyzIrk|B3O`&lWFs>U`;X8_G+8kDQ0qRoS<tv?Gna%kv_nG5T4Q@-M#}&H0(;!+zLT8V}Z>ApZO<+#LB?%=^rB_vyaOz8HS3w)8n}_vL+>_#GhEzh*f36;|%h`BGAMIxlsdQGLVj1}(YTvER&%_N(f?(N?-W`(sM+eTwNY-4EJZ!8f@Np!)4KIB$30TPM?ft8I<1-j_O5q<&)kvCi&@JUkvuzFSYazP2Kr*k5#N3XPv%ocQ~xt?*~9C0|M#!p}YGb!I=oV=DPwo%R0Y2~^&8W*3j=9)ax3fmGhMG`rrnz1G!leFJ~lZT4sGV1HZ}_LHkm)t0yA?#lj_yi>L1<<;HUKN~>%eDgnv{5|{69_*Xr>A8pOEAx67)06!Y<$kC67?aBVOt7%;{d>l~eF^=p)pq(E&-aVH*l(3W<>iYfxc~D)aK0UBzNqW7)OY~$b7YcsUYM@HKbxlWrD}uq^C)LBuUGAdu<w(Pe0$5w+@C+;hsKjHwcf{hiwMJb`$Ol8-_4S53Dwn;?i+qjYc3hCt3SPbPz3vFnP}f4+uS*CZX?)t?UAu>-)JSj9zO@O)riFSkJXizkHbINhRWM2`f>j|j?}el88?NWr#*%5Tu0}dBS-1lRqL@WjAH-eUpn7Bb1KG9CVKv({@&O;W+wYNA5A8I<v4!6abPz4GZxI%o>#g*pe*~F%zPaOMI+B|$I<mIbDa0p-{FTfq4MVQ2l;%9%*A}y|Nhxre;(GKb2JVm_n|!B6PB=Fv0V&ZulwJ*o{LM_uQQ(gg5P-@{<RGCm!`a#!|(9-H%C@t{T#vPTh)VqFY(aEevj`|kM&)9&RgR(?E9VI`mND?zE|KkD?#JO`sO^>KY1P6wM0|9YjW}LdDg7Q`h1=46D6OMv=1?5+01^S{Pa0u+Qi?V$W6B5I@YCn?CyDZ{H#l0|Jc+yRF7v>?$6UC_G2H<rv7{iX202Pd~RML-=6!h-d8{OEB?Xz#=?8qpZ1DAFVx??Tgx8Ac*_|{_2YN)(y=2Lp9|@Eh_w?xhq1IiiTSvk)@}9vNc^sze8cbRt?h21y#9Ciwn+G{SLu0z*~6RfqYpS-BHybkT^G~Wul)U5eWy#>>t#)Q&(F`_W@W!`p1E4zaw!k{&$96Ky1$6O*T|QT{gaC+&!&_Oe7~8=js4%;seY+PEVt`XkbURZGqvUA9q@f$)Az=<Uu%(Xzfy?(`qOmvr2DQLs6UpPOL?56y0c%ld5q5QP=tN=vs7OG*_yxqi7Tq_=Y)2Azfj7=epo*q54G2DKZA>3(#|inyzN9u_U}C4@m63Q--mW8bxAu8)p|@LJ=yQkl)lfGPZ#8U+Rd`MewqRzdA#*6hkD-4p!350spSj&_FrdF-thd#Ub`aurjjw*ddyuav0qE(@AI4A;^z`kUbya+>3r4aTGG<W?Eg8Ku9uYg4Y!+8h5c?tsk|JTo%1lT8v7BWcz)H(&GpQxj`{=Xd`(Bc@pE1G8W@Mp<Xdt&Qh%)8HPO#K)KBvO2fjZ&3*Y6Zu0Qr}wb<WKf%0tGnv?H;?|HLt|Df~bZ4KCWytaVy_B}K8$I`PQ`}tfKYRA7kz7fV%5c&2|pLravY|MV>!Rh3;&&{9XUOw!XI5Lg=(zE$KUG~xCE&cvo^`BYkywvBSrnyboZ*-gIMe<6{PhvCnryZtx)W2tud$nLc){n-CHO^(1&hNW~`f2SS&CfR`wnTq&aXm}<_mGx+t=Qk+hw^4!-gk%2-?Bkhzcn6y@>%lb_fHdb{un3n)pgqx;K%;M5YB(lc3w}0wPF9q8S<@`<-Go6@@N0x3w}QAy_NGYAAX4dx-O<Z>-c(kv}ONt6{<&F2h#mDzs}K~ugRw!`>$p#(B|2E6@DQPnqQWxFE~G`9g+VM+@FSrxIY~_>Bh5qAD!+yzoYu)dQB5_KIX3!@ru`t$MCnrQ~mORL|!+X0@0sRe7=YH`}}nO4<D-EEbrrXeY@)OgYx#^ZtP!-rhT>SRsi?2J=kw%rg0+K2I2Qtz1jbEg!6;v(()qsrUV-2(xSq=uejNl{oIb!u6b@4=dFJb#@jTi-_ofdkI(7BSl=9Z{M(1{ye`}i>vKbWJ>^1m*Tvo|g6Gk<!MN^aI1gAitYe4iuCMiF7G4J`4A=Ej_08KyVLe$)`M3REj@Q-kV|3SD4k*R<%PwQtpH)NWn{Du|*~pi!mF4md6WC8WK)$K-bY7q5!oSy(`+vLwKX1u5h5fX><lCLR_<P%<Q`x^>m&cX*ee1C4x_PAfmbKAXS7*@g>Ewm0d0$sOM(=<1;Q5;hKluWm7ry5;^;^LH;M1{`AKaf>r!LgjgLduf7wPgZ^_#Lo=XaY)^{CGqrCN*GANhuSsZ>ke_nus=%fISdIxk^=P6O`ew;Y_ekxSWc^^<>(cI*o8mz<aB`fsgsmiw~^{=|H7T3;%&T=#jQ_FwvErLKOtXj|T=)rrS={>Js-bI?3`jjp`udOn_aDeJKQM=j8nm$q)w<<runH-FBK-O7IW73#mbuBQ9u(wt8`Z?ykN)YW6%;Y8O(icVs`_i`$4f6CwcTek1Oy8W5+Q@TCR(+fNC`I43UBYo$7T6XEyD@(Zr_?=|3?tCrLZan@U?A7(h+<R-H&c`~Y)?*pEPuH$G4lTV8>gu=ePv+-B0Y~)Ly;ogcmtv3U>Pi2**TvU$zWO@{`Scxqd3;{mzCG0UXX5i64g7U~MLhpVN<Z&Pk|ZLV<SGUC()<arFvUMrGyW6e{?-1!{)D)8?VA7BKOxQ}hPDz}p-y0-*}+-CIiR`0Li2!y<^&6M24_|xi}de5!4A-DU<a@hG#5A*+Ee?K1NHu@L=`1|gVxe;XS^2LL&MYXTIlZ@-i6mfcWC$oUJE?}o~}fo5>ufTuqd+|<%I48PY3S?PsQu1IEUKM-@t)5W`WiQ7g3^y67D!h@t$f>cd$FkRD*T{cgB0VK&yePp-dO(EbuhEX9lzjxC_e6fbIqF!h7~WXMks*%pT||@Cm%<By<mW56TFhtweVvW+EpdcU_?~!81{&E8e#c@7;|ylA$NTCs8IDIvYG4@0kfr1}CG8;F`Dw)sge6$ahtE?$9FO?s!jElnKP~KzP-mHNh2>sEha4#r0FUA71yvby9f}UQfdHP&pB=6Onh7_v7_`<V)~mB|>nXA?WvPlu1IlB;-rw$#^{(Wd(cV9BM*~fJ1PsJG3Uau@WtmsE2bD@2L;<0(;?jeS~0NXbZ5=Vc>qKYap~fxIT^#L<k-N9R?OU7CZ@cO@Iyr55(~a2*Kl_W5Ggg;6&854LSil0mru?1h0eIz(O~I_oJ>9=r-^+98W<APJnI%k5eK-2`jFJxMrcyiQtJi9*Phg28{rV`c|RNB=l)JGzFZ3<J%E}*F#r<SD{bq(T60opM>{Jgsulq1Y4owz%3;nLro<fGh%FcK^uS@;J6n;a6M>aa0KcK!+S&Uz7XW10W=KU0NfPX5-dI&#CrcbLhuxX;Hl7^V6m?El>Ytvu%N63{uI<Bv<I}O^zY}H(BGgv!97v0;1)Q?=Fmo9p>@E`!9EDVW@u%w8C(on09*`Q80rEp3@!@I3l^FWTomkq5L^oC3Kr@HE(I<N%?~aME)6XRE)6aZEd(wPu85qpL_UNz0}E{eZUnA_Xo4IFZ3wOmE&weKE&z6c{sMLZ=Y^WULQ8=2g7YCtARj_Yf`yg=yMo=Io?tg{erP#xesDo(C2&D-A><?i`4Bo3EOaoq8Mp~zFmfQY6SyI`IJ7mmIQSQ68}Kh+6SOT@XaLv*E`bO@K7_Uh3+)3g2`&Te1ug^jga&~<!R4R>z~#V|kdtx9htSbrp(DXV!GjSakprP4z@5OYp;6%0;5N``a2s%2=v=VS`QWzT0K|OcLuf2m=mKzia3AOra363l=pt}0a1eAkI0!rdIa!5#2#p5|T?-x!9*J0s90*+r9s!PmZUskyqoK#a(crnzLtvqY!E?d$5r>fvp+~_&PlIE@3!vx03&2aDXTeLri=dali@?i~la0uS&`n^Wo5AtmwTR8gfzS=$mEf(=1K_RT<Irp1<KRQk%V42bz=yzx5m%58p;y5|uY-?*PecCzp9Y_Y-T<EmpM~B8p9Nn+PHf1B(A8j}Yrvbpn-Ob}1EDLx8^8ykTfhgv*PyB3Yv9Y!gJ7XD_%iqkLPkD>9s>(K1HKBr4!r=r4*mmr4*UoB2J|BM2KXj&G8Xv|ItDB>61*C`1`&xI2ptYy0p0=~1>OQqh0Xz|f)7Gtz(VJN4}xXHJmf=Y99ZZ=@G<Zi=u+?*@CE2%@CEQW=rZs*@I~Zg81f-B94vGYcnmlaF$g&j+7Ub)JPO(hJPJGq>Ia?!j)D4vg|-97faf9FAs<3JfQ9x2$AK3@dxIB(mqLTVOTmkw{lSaD%aD^6$cND8V4*(XaPT064{{*X4DJYS1uX_{1@?m$2K#~ip+&($J;46pb_fsTLue_m(6ZnT;J(n(;J)DA(DLBk;9zJ)a4=ZpsEmX18Lvb;=xJ~jC8{Y=10lF3LU472;7ZUc;7Z_%2*H)1HNc{t#&|8XE?CrA2gmE+SWVPf4#&&kSasCziQ}F)RtarX!0`$=RuSz~Mq71pOuY8R>&D>vcrDuThVPAIjnPh7950Jwf=l3-C%7zLi+0MxFOOrMXr}_&s*ht8(9Sn_LQ}w^o!vOT8^?UnPG21Fi(}qsrv;9;z_GGuXDp77#jz4-BL&A(a7?gxV48yV1fRxn(awJO`*G|W+UbVl-Ed5BGaPFH?uOT*oe205I41Zsj-`Mj@H(3kIh4qY5bO%A4R!?&g4O~L0*5*9Sod?_c~Ayi8X5);LwUjZ&|U$kE7%qF7C;DI2n_=-1TTjAffs|PLEC|+foCDFvyg*X@K2*ZqCFRc;QY{q;QZiV=wfg%cp!8dcp$hHbQZW3*dN!^AN}&z^w9<FWk(3k2@MA41XqO)1Xl%nL0f^nz$Kyn;F91{4m^%Zp<ksmeaw#bvLFOIL92qDz#dR9um`vpv?RC~*bQ0=>;^96z~i?N`c+8N$1G?s8$xgns0TO)xHhyHxHh;J)D2t<TpC&kTpFyd@nz7jGMYYS64y<MJkVU=e9*kmT;NQ2?SK%RTl1dWP#3TR^qa&X*cqM+*ag?g8RdljEpZ6WjAPls*^$T0C@1tEi9>K!9LoaEf?Q`sxvV%>30^K}HgGnatKfS|vHMEgLI}PMeF44=ekpN&95wX|{vok`mzYHePJ{jhP6NM#z68HS{qN8R(cT?|;JeV5;Je`G66gOX`jrXn2>k*U@dbSm`WE~h{1@~&_&MtT3w;pn*%5*tK%avjfS+Ove3kwkKZ1Y4`w0FC{sMgk{sMjreF}bx`ro1tqP;&6f*(Vlf**sQV2pi|{vDs6&=;Za!C%22p>Mz+!LOiCz)w*BEA&CM_YfiY5%dZ85%`(J<MXrh@A&_Wz6kvQ{sevxeGPsOegl05eunzrpbw(GdkDezq0hkg!D7rw7{BWL`hmU(O#^=he}KLNe*nLRz5u^K{essj^~Wo*Mu}ZY>~vsnEjUq$9!hjoqCY}#kP;SXXJ}V&7aVI3?F{aOV{M`B!6Mq=cqecNB?6$Wp>4n-I^uW$xVsVqpgo}-!6JI$_yF)=CBmV7puNB%LU24BJW7f2(4o)}u!u+;9}k|S#P85C&`7Yz;b`Qw2RIbRLh-&(_<~0&F+zzU;Bj~@G)lu0@Y;;rHiC8r|AJ%g&_>|8%D&+@C5kvQm(jcyT2P5+O1YOxoPu5ep8}tNo&yU#3l@3|EZ+MbWrbb`UjUzjUIPog0=|N}1iw<^i4vEgso=}tOVFcWp@+djFM^LKaUA_S20j5j2|fW9=lTr#7<v-?1eyvx2~Gtcg&qeVN83lChruEzX~=<4JNP>I8uUI`=pFDK<mejS`x#}0J_Osr_n{BKLhpg^p)SFnkn5Y!%ix>f8_-MOOUUgF=vA=L+hC!0!8gD+(U#D^p?ATbp%0;V!4JU?ptm*WA@mmXHuyIBAy|x~jkxAQw}D0eHsSat96O8alYny)ng~9I_a1?62Oj|+h9-bTUX##H656<eKA*?&^Eh?~Z6u=KLU)3%f^VU`c>h7@E$}Ur5iG{-I|rVBLf?azDX~O}IA|<*Bl@-qY6CBWE`i#>F-pu)Vl~cnHTs(fUIU#2jze4XpmV|Vz%kG{U@^bM_<M~0i}QI4eGGn#GH+4lGtN_J8dx0vgfgE|?r-Q@@LQDm8`nYPcL($gSm+_J(0yQ$i={ZHSa39S0a)l%@CGH;<Nf=<I}q#9eiC>SV!bBsHq>o{zZ9_^?W{)|3y^n_&v@tzu+S;sUC?BN;FZuR;K@qN#yLy{M<Zry&V4qn;au<>#B8)V8+FZqP63N{4><h09}#*GdH{SLdIowxb4`Tqg&qJOK)r&+o<Zyn0+kr1L~kYfK?A{oD5LtK+;FHBEOaJ#ICvsL@O0>W@CzmWRN^m$;MWMjGIS4E25-UpMLmn4%fZWWd=WzMX6PR93$*9p$eP)aS%hFms1sOdHn1Z&6GCutXccgAum`j%*aKVwS{<AZ>JF_A&IfhIp2Hb?5NG&;KPdfwqeNCm)+~<9A_V8gp2dth3W94P1lNGp2iE{sgVq681LuI|1?NROIS_)gL$iQI-$Y+?qR+oLGK&zL3u*!jEe6g7&Vvx_4Q&bb1~-7V0yh9Rgti8Eg7$~D26uvXRw7)9u1bVLJA*r;jNmWIxja>(v?HsFBeMv>6;Mw{)X^2(93j{j+5zkf_JOto`+(h`HNiE}jvGR7ey9sr^iA}&0Q&6Z$Sgu|A!u!IA@Hxzdf;Edeozb84;%mu1_yxKLqotrpd+Cn;33cmC8CswRALk~0vv%dg1;;0@==M#j;x-J%pwFgLp{S#M<lo}LU1=|7`Pia5IO)H2(Aci0j>xx3vC8&hCY-<-$Y+s(dSZ*%pwFAhL#5ltqd*<E{YJ`7TO)$7TgBf8{7u$5A6f?2M0lif`h=llo+8zKP84kdx3kQjNqTjxqMZkkt1tKM`jU%o8Y~ouAb1r;GW<f&_UoH;4aXC;4a`w(5B#~Xr~fFa5-p6u;}Lx^z|$FAB5mX(C6Ss;6u=TV6mqad%<<kRp2=2GN`&Y{6mSY4*%|F1aE+@01I6JE~-RRC4N<+AhaGra6@QQ@NY^qaS(so!rB~M9NH4v94zi{#eHrOlo#*!fffN5K^eh?m1y9=_sT-eVE>j5j;@*hU;q2AfB%U+fu#GNc^TiS|H;1goxVz4=|AB2Z<$5>7F}{w{u4j&IUs%&D*X@B;wFF'

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
