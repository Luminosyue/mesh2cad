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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_004.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_004.stl', 'source_sha256': '416c0cda161e22744afac52ecdf6e90dde8e795e4ae8cc41117dd2a0b62fd4e6', 'input_faces': 648, 'input_vertices': 391, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.02255709283053875, 0.21306991577148438, 0.006351057905703783], [0.08448673784732819, 0.27174150943756104, 0.14138109982013702]]}
GEOMETRY_BASE85 = 'c$}r22UHc;yY>gciWO08(PKpsv0xDUAYxZEb_F@2Ac6t{q6E;fqN1o^!yqEYj=iJkL1SV!Xe>dE$Jk?ye`ASByv+MN#KX6~yVhOzvesVDZyvVq?0I*YJu@u(_qMjNSMXC;Ir2W)r*T6?(MwsyUWpEfh#Eg8Akrl?JjP0?D8Bwvs44vh_w7I2N{Lot9mfVlj)`z=XK?Hg=<euja10EKh>92;>K7I<HbD2gjh+x0P~b-fjSdeeIBx9PwxzSdwTZJK-tfQtDO1n{bL;9WkLzs-oqwUTejK}HhOTP%#TB}*#YTyrai!@@(Q|v?8`F!_Hzq9-Unv$WzB=KcrmJb~B>0JI#W!59Aigr;;BxUFr67JCzd7>n&VMVuw#O*Gvbg;;UA1P(sQ+O~k@}`z=D|OliuU+Di<9%H(eP((7vH$x;B2XXwF2VL4iw+CbGrE2s^6AL{rG)orxH6$;$2uFzSi0oadth5mGdu|1V1Mk=RKA4wfx@N6aG9u<Y86|iDQVihyQ7p_*!8;x0zBbuUDIV0`W&4OtH+rVX3vmS8~3EpPPvGEBA2TE+fQOY<+NEx9Sq#Z2cvCo2|%a14s0i@0MioM+Bh#WBQ113S9*M-fCR$`ERAaw7a9=|1qtIpHbWq{>Ou8=g(Uf$$1=Xi^S2YUJ^f}$;+kE{^OU?p035jH&jR#Us<&P^=CMuz9Aa*%in^(?C(UW|MhQ6#Q%Oa+Mic%q111GN_=JM4a9%&eu32YYJvI@Gm)PYEhLU<sQnVl_Lw57OMT-Sx5buuHZF=r9AhQ%mGqN1Z}yh?(yj;JCy76IBl7V6qWH?wh<Os{n=%)r-sP`Wh=w<YKkGT-91j&=xl%=Z#jSzVHyrw7x%lZL6QsWTZM1)RGpTPfy1}2*OzNw<;-tP>sm@&S1Fxe!w{pZcN0x=(vMJ)fD=WU?(WTjP-pW@|zkWaQO+9nq8yiY}^P-K*r2W@#&k}#(9kl=OBlvC3!S7u4BF5*`Wf-@b_*(xz(J!6Wz#lqpvecg*i~7ITSu1hYy^E6iOZ>zy=s@vJqc4lEc&<P`V-BYyzI&w9_wvSdy|G?f#1BeG{cu(4YwM4Piyzq&dF!yOh_6&h6F(#9hcyzX_M!>mPh5%k{es2U(!0Pnbca8y0peW!E=c0{o(KO#d(`*)T6`sS0Is*%G58_<$BFMdp-6n?{Tna&y~_u*e^UH<@u$A(Bgg7(_$AZfN7d*j`k%^|WZd5G2mjETAyV&;^SG`vQ;Yg9YDj&pVrlrbpZg(S4)7PA&lG=lqEU`NoI?B8v_XA$*8tHoc2Zv%mWuk$zJa0}PvW|AKfy0sD@b(z@E;}KX2UKye(N<}`eS?(@eTVEw_Ey3p11fJYh6%3dI@|}qWI=hvv<q!ANk^Ic{a#HrI|RdF*~?O9`64D|7vQ8_=_LHHzvX#bRYgtjU~RRx$h23-;^C8zWTb;?jru#99&nc*L%c2>oP&Kgj1gQ?UN43anBg>O~cBHpOG51U;N`I#aHtmOB`jl=RQkc>*FEyP01?{ieK43OmxA=OBg?;w^{mH?pHW(x8;Y#Fa1t@wZwX~v%-35rxw|8lK5&5<g-gV<oQLI_=<W7dHC|fUO9GI4&V4E#!2`cIj?rlCPM06@|E+Nx6VH-_3Ar`uT=_0J9Bnzl;br~;;Zp*5Pzbp<Uz9=6e)V#4%a)z`vAuK6Zqx>5=YH=yIJD@9Umq2RwK_D*~271+63RpQg7WD@eLCqvZcP`1^5f6A`gdB(T}zKqa{v-4u}&vMDnIx%M)K&xKGY&jySnRjtA75BEP>~1LNUFKE~}*5BRx8)L%DxllbQYr{Fwkm@no}$irkMMs#m?v~zk7$(yzz8@}6E@zq~@9g*X;-q;rm@jyQJ9otyM_g;+nSzhq-qr_J|HzUtY6zNATX1(m2lvjOly{nv&pM9s{$InOqw)nU~j+<AGm*W!d$p6wX#J`ax`!)4gZ{*>jmy92+@@4UroEOML$|j7@f$y-t%ejpDgS=&&YZpAGOZyHPF>Xg!IV$x}UK3yYGzW1${($zx^}xRJwj1VqfQz(88Lq(}iR&_F7n8iH=lrnGef%G+Gf(0%-i#$>-=tmYjrf5E#1H=ff8G(qe^7I)_!Y~_{!aa8sKi$u+>mx^+iQ!j%qoX`a=xp5TZ*r3n}xjX-zD))zj-1~j~?jvb{Ejj;_FcVZ?7WxFZ4|b(~-B#qcU!_L5E~Nt8R5f|9W`HdZjjhg?(;a1ICYMlFSQJ&%SeTed!Y4G<q1ub5z<~IlkBt^KN_+t}E$-_{xQ3wCClg%|-kcP0{|WSj-pOt_haoIm3Q+jvSxd3%}D&tZx;Zu%7gPHP14>8ns{Io17YBKjqmR?V02&^Fn>F5`Jts%wNx}EYX8wWxuBQjzWHv^;pL)=fXdQb{bQ?r9H~H@v<LODqWTO#uXDW4sGJZ*LKBWJhXj|{<^yt^<O$8pK42)FIrnS*@r6CUEp^ec?|R8&_c}L516NQuVI}GeFgvZYUJO_SFTr`_N(lFwO^ve&zPPl<5{h|AW8hz4Uo@}516NW)8Gfc!u2kkFXP$N>=FE@kFgF^48eK**DaRcE0r*Azo;zj)H?nQzfm&ovwjWbzF>-NutfAkSKJr&Y}zU3i8w62Qsp;{hmAIv*OktTucljL-aSgh_)q^+e64a7_+5_6I9HxqFBL6b27b-D$K`xY+9Zo+m52XVw2WKzbWicM4=p(U_v5}i&PROZ$!3h7Rc~dzHI)d1-!~iMtyK)xy$v&xE%R@l_ZIU#WsUf%%TtVp9yigC+y6uy|9{}un1gkxPq`F{)9y9;cT@aU%<o9?mAWyg-`W@Rv`Z%HGykR<gJiy_$DYA|n}YVwi{Dtp*BW8H@^O&s)f@+6-#zsvuB-bK$(zz;7yN+hIPa8n>>svO#q&XPTdb?g8{)p4fc?I5{x;?j=Y^^sTaNM55a&G>FZVT*OFrsPIRd}tW;w66r2(Ex!u;Xiy(05Ywb}&#{NIRg{|e_FunW&UslQ>pYP25vpDnFcigI6JJaJyuCDX2L@Jk%We7TS*{j0`)65n)d9rDn|$5h0BxEFp<eT?%`E~`WbpGJHe56QD>xet8qyE0O;Wqzr%r^25)2>z6bSWm9ZfY1G*;n!nXMSQzIP`_~fUmlz)zrQsD^XN@Sw6kt%s^xVR?u$$gE~_o$D0>1i{)Y^N-|QUnnLS_Tk*UvP@lA)nf^Vmwo$YMC!N1qg&Q||mJp1H}ZyNdx?R0j>y8Wb7n$+KI#QZvY67BRz6yJ2}TlCj0KN<ff+dJZ`DNZ<VOrER*rjd`+kmuqUhjA{rzf>89=bM@;;_umr_?dIz-^)k*ZN)H7rtvu`_Yu~yM(NV;+Nzp(-b#Lsbuz)Gh_6&va9w|1-Dv5nnS+ssQ#M$~DhDFYP%oVK-5nXv>iepA9(9jK`!hXo|C)p6QKgOv{^dMrr+K_fhWz_C4(P8kO>*V;_0q*x&aPp<Z<29ku9yu!1?^W(my!DBWpCmC-U<0U=q&wZ?(h-*4J)*t<J?fuW1XD$-azED#Wn0d4|$2N9<@atzS|}FG5YlqUx{mm_5|I*dQ~?|e9g8B;``^}espFR;(JFTPGADo?R(|qIZ1t0`$x-uF&`KxzE*cR=Bf6zT$kp_=dc~<7sKh=l4qmCY4~*pqaTBOb1i+XO$6e+&ynjj7QdfqIev`wr(hj!nYA9{FA8}ZktO|W&b0Yfju#KW^%hT%d8)3q6JIGk73+Vv74q4_RebdyJcnw{(j^au8*NZuD*?ZGxQqu=ZEyHD-{N`v&JMJHTRhI|=7#eww?m$vWTO7_e7t{fu$TJk^<$`SeF*PcPOK8&)YAd`j+PzKzdfR`?^>6N`_&RYx0dpk_M3a8i?8J+;y%(Q9P8fV{n$S?#q+Y}oh9poxtTZShsO}SZ|Qy&{S_66b?ET~oHw8}?mJ}?P`{rCuJ@>))Hig_#=bkH8shx*9mcbrg8MM{59-=@SqIc?&ev(hu<m8}%6Kp<wNSqS)-j`#hpZ>&7j5wT)D7=>%omT!^=jwB;2%sy{3~I&&(6NH$#T9Iu0PtsVR&A=6^6W3u$MT>l`#10kK%pch!4_!B^LQM)x!Fj;Sz#%qh1W^`)<H{IlD~sWBN(>J!jzk;oTR==d9<5GjA>0v)2*N-Dhmju7-#4e(ZQP#BmKlo*c$ue&r3sxUHLjb+qvP$yqNvkMuo_IDG%9#YbXYE#Z#eXQUxNt8U=D+dIH7e1CFd1n$>w2Euo*iudgsN}muvZJ7Al<FfFp-Nbc09gT6F#dZegp&dVCAEYTxxUM?(5=VKHkNCR{XlKcAjPu^U*q<(4igozMMA@gA+QwjC`Gt!2lQ}m`mcF)rGS-vEzF7BsPow^b^z)+s*qpHRP2-lJA0s~EdTlPC{<R?F;h#^^K2xs{+|U0r4cAq?8}?DFqu^IalK2_lS3`cD#N+uRWTyD0nc2wC#Z6g7+F2?D`D)}O?bW7ll=|jr?Q$)B#XbrBRW?n=vwE}_{4?<wKhp!T@3r<v9G9`Ef6Es8sGc$KNB(ji{wCxtDjWW-%HkVsUm^cxZo=m}ujL;@zE1X%^O!=r;Jh0j;(6I0@58i?R%ri#l9C6lj6a?`htEMi`+DFx;$<S*yT?xIYdw=Nzv8nI-xql{csZayPUa#0!lh_uw*<`7;ja;=Qg`I}ciUV`U+c#GRl^vWr>5Din6I^~qaVjyll_=!7=Ewv{$BXLPW4U@U;BRNIqBaEXA$4|xcExUM6@S=oXOHx4`82f{%e`^x49|zUt>yRoLIlYdKFt5??pCbNPI)kef0Y!TlkAl!cPh)>VKPu^*s9yp5KkGyDZ12>24o6Hu&JZooN^LZ^rVwF^@6_AkOKR5?^`rv#E%m8i(tu?_ShjJq!8a`#sabD4h3YxWqBv+l2hgi$(qM0k~fm?%!_3qrUSB<g<G}sh@Ew1O9}MxZVMWk<XkRh;t@Le0B4QTua}y$`g6MHCyJRYRpFcgR`Z+>93BtmcBAM7WoO7DdStsya9iBf5fl3EZ5Rk-%Y_dbiR+{)Q70Q@VVSCjLTeQ|7Ljp82;Z|Fb<W=a{n^ie+z$aBH}M>i23DI9`6^;UdVsHgd)CX(+~B1_rR}P3-xOl(0;E7JlCHwp#ByE*0&3B=r8-0yDjIPVZlimho*xaik!Ewzf88B5y!O$&O0)qh_CDk#e4fE{<7c8=!@r9W!)y!zxoIEV?D>hFWnv2<+U9B^?Q)`h5H9>;(R&IxEGIh^1Z8)gLOeooQd}EeT6wK7SB!BlHqS2j`pwZiG4*wtc%L+(YPNSO~?NHyB(;n43_$Z_ZP##lki*K#(aGGQ1(TJbq^8e+HCAYe$BxAdh-~*&rqyaW2z$0J)Xi(_bIx*b^d_(;WM!gw>^#L<zH-Zzs<jb@p)ja#K|x?;rl>x9NIb6D%aBgcOB+FR;}C_ewRqZ+1(7|b{x*H)vAK$h|t@3jvMTY^{i@l-0z|);=M=GeAMT6F6Gbacz@MkE84^Ri}~7P=@)}xH~dPq@ZBe=hl~e9NG^P*5L|Da2+U8r?-8Hh<&`?qj#~PK-**bXBbat$KcbjxVBht}S-h7Ud>?-B5sbH`D@{fG5e`_db~GyDYsJ%Wzl*Ac_aX0J!smK!NIQdlvU7dp!(@Z&U06)!m-&Pz+Eo+lr(#oox23OL;Qhk4BG#RE(RhFPU?=kbwKMK7ZI{E}Q61x_Z57OyyQ%OC?}IhEVLV*g4?i;$zP~%3kLn*nd)njsmva3j#$TP|sK22X?h97ocs~$&davcYGpsm?eg3{XsK4zI){W-xFke2tg&%eu<3Y>C_<3!E_n`bc0d?3`=|{s0TlnY0u<rFAg!eyB?65!T=!<>z){0msmpZ_|dl&oR8NL`l52_=Mu?^b!EPoIBp*H;1D-i!-6rKyr2Kd}x89m2iy}i^yeA5rUh%<f()}4v`o^UD$^`H64d^cH#!{>9l!Sg<@|8*k#xaT<U7$>Qpu>|kW{{1eN7ccG1xSxUR`l|)@rIl*ny;;*k@YC*KJ!w%M>-OH~@b}{HJ<JPl<Gp&xS2(ZBHtdIQ-#B9F7e0q7@$)hMM!rTI7Y*_E4#Rj;Yhho;bs!@y8{Y@-JHlVk2+wOHlB8dZt}U@oOj(QP(2h=Wzcwb|`<rQnHRfr~emP%8-M)x(<Y$bB?df<AP;orsRNjjBX^(C2ovv>Ze14xYZl8$pxo!#KI1I-9W!ezDXM2```gJbiK3nO@q0aq_{FT*};ODK(wF^>LP)aNIO5kXVKe5tH{ijg>|9@gNzV-j;PpsTpyZ>MR#LB};QQ8!gfh;=rrn-=Ole<wJ$=%2usCCF4$gQXj<W}S+)XL;0WCOJ<*+8yNEkUkMu0;K$fGd&9Q2!+BMQ4TjAF^I_en;;&@;mY~>M!JH<U7<W<U8c6)RW|^<nLH?-p!)(A?jJOuE)rS$XV2b<Sg<g>JIWI@*3*5<Td1#)D`5F<oWuPrOu(QAkQHuQrD6b$tlz=<P>r$br(66oJKuNP9txi9wl!eZ>5^ZTgf}A-;;Ne4^S_V50G=Hm&iHf6V&VE6Xf&M+vM})JnFCHJaRtu2|1r^roJMZ$&aajkROv@Q~x2qCV!-sv;u!57iZDABGsN;k^BX<7WoTu18O~T1F{pfDcOnKg6d9gLGH++b1!NSaxe05>QM4<awv<=A=JU-5ONT8AUTLUhT5AvhHRvEBOA#hs2#{7$b+b@$b-mzsZGdz$z7=ia#yk&wL002+?ZO4+?ZUOT83PkY)4hdcH~l2eQhemW1as}pwGyEk$<P&A^%RkPrXXMPrgR|j(m;$1B=dksJqE~$muLPucsa&>zYMgPhLgcL|#Q+MqNW*MqW%^NnT8zN1aceN1mp9Ue~6v=p0&5h7^=B1;t1WB^$}X)Od0*Ih;C&98R80O(ahy$52zqG34pgRPuE4ENU8g7CC{sft)~IMBPeWL{6seBqx(sQxA|=lQXF~<V^B5>Iw2T@;>T$@;>r$Y99GG`5ZN$e2#pXY9?PM-=aPy-y%Ptz9v5)Kc{{qKPSJZ>g(fs9_w6;Md$L=isbU-8q_byHOP&q4akki&8bf0=44lD3$iP@Ewv-LEx8Me&V8u8$bHBosl&-5$zjw`@^q?34JB*jY19z%G;%yOh#XIjp^hQPkS9}(<jLf4>IiZ;c^q{Rc^r8(wJ&)zc^I`Tc^G*B)r~xW>_u%%_9C~Y)+V<m*QeT%>yxWeOOdORZK?V?Ys+Ju|5l*Clm8~aq~0gLB;Tc8Bi|+eME!yM6ZtfY&PS+w$VbQ<sp;g6<fSY+FQKj{>$-}(gglqJj69b-le(BZldMtaku~xZ>NN5cau_v~tm_zZ7}=ji=V8<#<YDAK1*JQ+FLemHFL^N4NFGccN)09tC6A<rlSh($sFTS)<WbZZ@+k6X>U8pGav*gUIglJeO(2Jmqo|9>QRG-^GC7t!gSwhLgS>#6NnSu+PTfXcPF_ddM_xzXPCZWEPR^#DBWIIOQ7@BEk$<G#BL7IfNqs=RNq$IuPJT#!L48ktLH<D1*ZL1U*4c_h=hD>j<kI9S)EeX}<hs;G<htZ$)aK-7<S(hN<S)tXsBOvZ$SSo9StWNbDE+D4)GlOQ`;fiKqo^avqsSAeVdTR5!~_<dV++bm>Ky8H@*MJ9sz#nmo=u%bo=u)bjVI3{&!EPTXOQEllgV-9Db#TC6mleW966Fao;sR5p6pK@M)oHUp$;GqA@`$tk^7N5QCpKck)5ga$<E}O)T-o~<O)<<as{$ARlk>5^H}FM3iKuU4fzrEF8LAp2K6WM4e}Z4Y4REJe(DkOesTtNBRPY-kh+w-kQ~jTa~yRES=YJbIC3O)COMKkk*bj=l7pyI$U)?>)G)HH{^Su<U#dUZmpqU<j69IsjoOFYjqIg-z7Kh^=-h+am)wKgk2;v#k34`nlstgkpE{D<pX^QbA$ya*qK+beMIJ;QO&&xZP7NdvC;L%D$bRH;)F|>e@+4|3c@lXlbq0AVc{X(cc{VwTx}2Ou{)W1a{0(_Cbvt=8c`r4ayqBCyJw?tXU!?v>zDWL=dXxM!`5yHl`5yTx^#%DU`7QMW`7PPT3aa0eY*=(IM=eb*N3KS#Las(`NUck5NN!1OMs7)NPyLeIp4^$*j@+5-Nma?7<et>-<eucOtUlkjzGBhYub@O1l!$^dkwxdR)By5WvJcgd?8i7hEIRvAy~(<cBKwkqsT0V$#*%}{Q>{MV|E5yECQl_tQKQMxyoM<1SaK9Okm^JBVVeS}!Q^0`L+8c?<DpSOX+>>7ZbfcUP+C$OQX7yPlB=`mT#ed@T#a0VMdw=7#^hS$+EgcUZL)#tOg50~QC-NoHYe93*H`q<B+zEm=HzDNb}Tx#r@D~aliRZB+=l8*ZbNpXI+5MTt*MR4jhWxpEIN0hwjg&Rcd+P#4lFu%EGV6+uGE%fSF$6uA=!~!lUkizlU#;H=aSTF<dWp#)EeaC<kBoU+fr+hZOIj=waFF8_EZDeo?Mk$k6e%aSCvI)2a7&-V9~isL8(lwL#<1$LvBiKMs7-Wr?w-zle@C$+>6?t+>6|s+Lqj#+>=FTPih;oC)tDQM)n}9)YfEOJCRj#0JQ@-fINcQkvxJtR{1=J#<J+F?`tMfyHGomyO6)6x{|*nH=#O`n~=Yt)+B#HE>A5(E>AAOqO&!%B-xs5MJ=xU`*}@Rp_W!Y|L9zdMQ0nTE!l=#idunOid>FrPcBEcqgEyB>Oi(5SE5!SS0YzbK9A9gEIOCvwU=c+%F-{)Pi5v$*E$yYtiyck+SDTdP1!%Xx?A*@JNr}DuFB{B)wyurt8*l^m-2a^taBW-xAJ*kt#dTBr}BAEuJhL{I!91F$r0oUR1fk5@_4FB)-`~v-^VBMzTLmKRWW<(|L(sa`TV0lH!4N`Lz4gZUl#qWZuu_*3u68Ik-dNK;(A{d46I_Z37w&5O8GD97Z`K'

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
