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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/02e777bdc5114b148963ed3def6ad471/part_007.stl', 'relative_path': '02e777bdc5114b148963ed3def6ad471/part_007.stl', 'source_sha256': 'a0fa42ca497f2603a4b41f780306bf51efa1626e57904201c7a28d82c783512f', 'input_faces': 720, 'input_vertices': 431, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14157164096832275, -0.5, -0.1657794713973999], [0.16578169167041779, 0.41560953855514526, 0.1403449922800064]]}
GEOMETRY_BASE85 = 'c$}r22UHhF`|p<+HN@V#t`#*ZcC2A-Q3DFGcNbKwAQm+CRV>&GD2gRNR1iBTBA~(wwh&{B4HI=^ioGNzF^N(CJI{PqX70K7oO|x|eV_CF?87iSJM+x5Gqard`{etuw8H;YSL(VCDDt4LqA)A0lvbvVnml#vh*47-g@n#<Q;L(H{c|+3XWt(F1KpHq$}EqOqo$0Q?9oQ`XcyGVqk-xXG;#9O$pIn5Cr%zYiupeam@s9O?VmCxAas;{UAK9&CJoeP^%|&i)c?nSAG0>(ua=d`w0_|WOkHnxA7*N<e|?hty{6<c)u(^Gf&AuQ<k$X4CcjzKeLh_uenx)d*5#XY{c&0>{r<)~<X4Zmli%>DA5TBOe~J6OGN>No-zPJ?+5Mx#$!{LMe1-JqGlxjC=1S$&oT&Azyw=J`y07uY)7^C6+2wgXg=gF%{km!#{k&ZXUOuoGJ+IQf>QVan@_giXrS|`xt{WWLN<Uxp&Xn4@P20}yYeqdHzrJ@5l~)EoT}98;E`|JNW(xTY-+e9U`iD8>*F5jgbGbT}NTKV0Lrt-t)ytj-nOZ^pq<UOupRA<*$>}4tN6%QgoB7o;bxg7SYW7Rs4>g}=Qhl%df1vuNE!aWjJPv1y{a{ualuqSdtjm<zU#Ialy6?Od<k!#aqk5Dz^EOgFuiY}m_GpuQ6IpqE+3O7Q7f+}1t|he=P<{8VW{B~lt)D^TYdo)$A>P;gGdiBtWBph)L+a=0Q>cHGR%N96t%p}<QaewsJ0Z5y>V7kU%H485A-2<8oN$=hdESlu#<zuTQ#)UVP~56dZX6fu*XxIGpnl#Lc3iB-HFMYzy8d9oajD<R{<xo&Hx_B+*XLHC`pre|k#t=m_Lx{+eYk@6!>n${#QUnP%j}>y|FPaNu^#Q`YoqA?ZGTOd`gvEt0sg!>>0&#T&#$JidX%?8>C$~~OgKdC46m9l)^9DpL-W*ldOA&-cR!U&rTfp$Oq1H<yI?u>=bF$ou|3Lv8GGoyw`*~~rw5hS|B9mdWzD;oDz&Hcr_`U;rS7RxoabhxQ9EB$lgews=|`ykk?yHdd!k!X+^Y9)9~IkUHoBKY*Clh0itTavCM_j>*GDSv>QgL<>KS$;MXcYr)Mg*4|HTxkoliDWKe}Fdr-=0{p|3)zo$<w_dX%A_yC}}LB_5ID|Dj3kus+{<M6AasQ)MUVfz48R*TtMvij&CYN2GDj4n9uv;`*CpDW1dDB-3++giC(q-UPa~-VRTe?wd54@~um)Ap766jHdE_w+>73Gs*oRwP)Vu!_s_-$mR2AhnG~|6>vC_ey_{DL(=&6jygv5xVDl1{d?!1^BL6sC6f+G?GL<ql=}H;FR32Wvk;Aok?eO!Y`+=v%QU(U=`8tGucmz7JxWWG${*@Qc~$#vVv_v49VnkzOCBUj?U|iJ<877do+#C`_TCbT=bFtErSbX+`Eip%ekbqgkBidt8WFD!O7-0P)<yky=c(k^Kc2If`se)EgHk+uT}T)G&U?rDF4$y#^Tgf*QhYwC&Bt$6;(lqo)@4yX(PI|x7yH?WD@)^Rb*!~dYUkqhTd91Pf|6fpaBnr0KU;gR=(j?K@jQ0_^&Y97$*D9Sjbg*d@4WA<`&Fs^uF+n5r2g;y8|4M#?^5J<)(MK$?Ig9Qaw3hV^S;m@gq@)N(R_D{<6=(hz~8U$nk9(+pecXzytJwz`B}|$pKmSRU&B&%NpW>~oKE#$A0_$CuP0I-a4l>h`L&l%Xx-u(urOY{uR3%*&2zn0SModSE33$DdM;zO8ZX8F%^&DJXO+l~lluAWG|Hc9NFe#0^^*3uB-NuXu1WdESwFa{UdyC7(JSo`>oNA1kD~T>eYRbCu3ar+=;z~?ZRh>M-?P?@tCW|Fa?_>qM*Lbnul@^?{i!*WPxM|xw~OOz49ul@t>k|hD~^{n_BmfCCEbk`$K71<n4U|U(c2}}|LuLspGwo5ZQ?lU*FL1@G<%0{6XQ)^^P0z7LXoXvKU>H9@^w<qnJrSB|J=r)Yb{dpTOa&M>q)Kiz%Al^&4YhayjlUiTcmOCJcr&3#yoGS9@nEgJiZssj*;T$=1s~=YIfZiG0u&RqiG!V*F1l}Uw?l07xj;;>4o)TdlbJAo=;mwt(W4zy+Y$?CO?T1`(L#t@%_V=%qVfZT=Qr0by9$Tq!cHqehaCdBJCx=+9HSYk1MFG<k#2K;qhc8tdqvE!&b_BW`{*<sGO5OPu-^RvbtPbEsaa8LGKHrA78(l`oyzzzlAkUQ+>BDuO!7fSu3~X6#YE%<Z`ipwBN&M-kP1JE*IlL32o2U@x?2W-}TL1TK_A<GqXvrU0E#lr%}BJt&@yj9xW34O^rB1`CqvlPJT^~yH2|K3hm!apOxWKzqMP*^Zs35$*=wCyM_AUwYTIq5_?iVD&c&c{{B51`JCcGIpjHCs%O(v%EM-G&~$O!_4a4^xO;aG6Q4^7y-e>Ntw+fzQaqeE&)45p?SW#yndf%UcxkaO`b*<=?i}Sk<<X(aQu`--ME&pjcijC9VO;cnbLragzmFgIwU^zhc#HMV&QEz*{rf~OZy_F(POT^&tWJaacnk4hUfV+PV7mR=U#v%aa*nS{J9rNC7M{zMvV-sU-d?8n!2A7R+I5Nt^Q+U7$Y0Av<Ew6ZPUEX?FFnOujE8&Y={==H`Gk23{cQPM=Ii^cG1I+;adG*b<@4HVLHi{0T)$fs2fIHXLD!W>N`5u|2CY}Ma_eW24sS_*{lKyjqTgsbUGf_%PD<sq@8d#6zf<1vtHr9#rRRvKM1J!-w~?Y>E3i)TYbCo%<+Z@>p`za@@A&l}8qXKU#hUt*-Y;h02J#ylW>I-%_9Ge(V}I=h-a`Bv^Pls0PD&=fIbaj7f2eOD)nBJWxD-Df{MONRp`NmTB+uj8v{jN{Tey<mYgX&PMbwVCxxD_!s3CM+{K+D5+?A1M_&#~#JMtTiJLZyZi|#@{U!g9hb{0H#lYYO{U+w9+#|$LD@?{j&Z`|L&<IjJ@VyT`>U1pOOn<v$yp9!Jy)8Bo!Sc<nUJ!t)-UT#e5S>;9!)uX)VSdlbsp5!<C7N&C^ZE!YU|1KZR+c~vEH~RV4ZV{s2=skQI#qGUQ5n?-)mIDS*T<4TpDn0M7_xn;mlxW2LU3t7Ijr!31G{&}HD%De3pGViZ5mG%`@e@3ro^D<$w%-^X)S2oxbGUy-O<w;OpU`+|J)X(_5%nk2?>%@U)nn$%;`3qMTYlfhD|q=yXNFQeehZgL{d4neX^NMXHzdCqIF<U->{VsC^t|<s_|Wyi;mhUrjHmo%O$_7Zo%hs&_LOhcZ{T;@({6J=8gG5IRF9tdg7T3oGmHD3_h8#;d>#8Dc%>N6O2jH2pIeQUVjL>|-%}n}-Yi=!&M&20vq4nf>WtOmJaw%~4xsXrudf#8kvZGo=Xg`AuMyj+jkrm9!&vMg`HhlYCh+lCM1E(TpdGqR`Pn#-Lw+Zp=<R&Rl7B<Nwe<VQV`|5OA>=<3On&DaRf#wFI-&Udwc>bbqpt_h^_R;fzj-S)gzCE+Lw@J{Q*CI{dqEp_f%~2J(e#S+K2qy?t&`^6%P`7IW|AiP%`Yzn)BUFHUMKdO@%I+mcPUr?StrK7kzAbG=_;2$Qu6=y3$@dFT{cpzN6D>2>sZULJ};j%lipuS^<U`yW#nrdDb2eplc;`ed>hHHeHcphn>*S|^=kujXdP?5@|XPjhMo)Q=S@u7f4o2EiJQsy7d}t9-&vphK8fCg=6Qa8{Qg|7yh7_z*SQPp#dy}IgwXkzzSb+6{LX$E=ivH)dNK5KXI(vYG_C(#73aiA{gZr?pR1SFwupYU*<CsxvtIFa+52_%m^pl1nmcfd*dFWE-&9_|7Ae(ZrTszcVO>8f`Sk+r4646<(XHZq*M98F_i+!y`T4H1ubKOrpKJF!wN1RQt4e-453#a)yQJsZeV?DZwHQQxLp@4ytEbJPxV3i9A;0;e4#k7n`Y6SN=9$FHr{<^mqDC~O`J&dT9V^DUOZ}Sr|GP_mXCLR9`Ix_#{a?n4<7>@&PI*k(I&`}f4|8&9{i$>vy<O^`&>UJP8-dd$zm>C=pEIN^Bfqn6Rs65>I9c~hF5jvpkAuCHc1Uqsxjf(hT&}s3k2Chs|6b*Bk`@?8&x?Jxl3S90pBR!IC(Y9x)A+gQSv6i7$2ULlb>PIV<af>i%-28g?<G4I#!GQEe>|;Awd;4tudI4<jryVW5I!y!TkMj?H{T=Pj_N^@U!6aZ*4z5KedO0B?4ohEUKXHn*LSB#<&CaEI%#gh1Tn6hb8^+Ed4kwZ<%d_a4>AMhlHW{n<NL1zNmRe_w#9BKP9}BY`F6SQZYdrjI`DWHow!?^r`oA7{ym^m={;gxDHpo&??8vV_K5MLPXCS02h<va_lWbwx>l8+3pM?3k2LN*Q~5eGx5i$nKj#fTK<!ymaGw;1J%6J2nYFT(?8iB|Ywq)X(me9aq;^`rEZ#51gX`<El=sv#iTlO=)I+l99Mb$~-vQCD7O%te>X6I>;{0`88%ptD-43Glsgw6yCxiL9O1W_drT!^(f%YBRZ;uX2{g5@A-Y>52UP*rQlM6gAWGMW55#GPnnWFr=&iRkX@8kz#fx`F8-J2(h<Es|DM*Cu|b@xOm-g-S-LO*X2o+!qNxqStX&;1V)#r7Mn96HZ5|DKp6_K(q{1LbXF(PF;e#e2;>^N{cBi=`)t_qG1*#p5ip^C77{&zjIVl5)#W@|*YW)B08~+53<*ulp3Dd}ZvLbVzDv`>V9hah={q{`cR}uAQfTGdkw*dYtd4_@1g=wB-6dqv(5*>zvnN@p;Wfhk1YP+<aJ?NBeU5IZw?!<bS`;alRkt-jwRm>bdjthtDb`OV7Is@6qhe$>O+Z3*x9Ay_PPO*VNH;-eg3ECyV`{6$qwleXWbs*)Qu$FYxoX|K3RD)i2iY?;5Ggk4Vq8EtvATa&_|&sekt7@b6EdTaQTXuU(PyxOys4Dz6khN$+dzn_?+qKPaU=DNkDM%97vN?^{Lr_h4oIrzv9nO5Hz0>HgC$rikq{i*KTMaE0HH>Nm@`rMzGTRORahoJ+Xyo!hF__o&owjf?TTG<7>~FV2y4eLCes?aY;<;<%{$R`Ytia*vAbbcG(GeT!cBj#R(W`yR~)ZK->z*iNfJOMb3eR!x=qxqCW4$NsB(s`$Lxku1vp)<+lQ@?$=wes_IPJ53rFd|yz~Taw>7XH)OT(7dpYgr<q@v<_$R^VQhQG^w5S=JRvCQfJb{_80}r^Yh`|Rnw*NSNVI?)CQ$X{qKBVuQ@thY`^Q!1Ug4`y~|0L;;{Br%Fjx`ujx`dp9k>w#f3V@#BnkI^fP(C);}i2L-4IpR6e%bF=<@tmFM}#EB2V!9;3)go)`9L$EEojmyg!jE{_SvrSkZ$;kq1lT%Je6__&m~d0d)zn-<XDjaa|A(K^LhN2%>5(z?y{&i#Zm?tuxEZ?%k>C&c(v)YUxB?yn>N`|maDZqoX|7+NMnx^LW-ne_95)yVI>UtF0}_;<-N9vRZO?2qQ(OA@wZi1DLzYfN#Ve1!Lmb1sxNgZj-n_*%NJp1{wKtc6OZ)IYwy{5xOVicG2fs<Dx-%SL93?Q!Od+T(Dh7+01zk2CH5W%9qzd-$GfbbCsEXPv2KF5v5Sk2?H&g|p5t^as7Cls0~*G~d7Fai-tyV~Xw9!<N$bFk^3DQ*5Uh|Cr9ll_Hb)It%LrvqEF)XXE)CevXU0r;aYc{|><~MXE>Hbg2ckZ`UJJ94~#&vsF|s>@hEo_pkctEdD-@ekZll=&SL4(6)Rh#phKrj!=Hk{7Re@`%^*QG*^}9`$DY4^^(<S-K+Tc@bb>SBjzdfn{jRKNojmr;k(G5a9$7Iznc45KEE<npA`F9Kh5*3>yF9&Sl8)+cX>Yl=aO81>Z2LduY2xrzw`H0q4oLS$((*BwbSgC#^)El=e&<w&yV@JXTs}~(s&ijp}%i2%T>!Fzw>^_`(CX$l>4z?(9$mOeZ>Rrf4^>gm`eG|b!KOl_`F&cf8V<*re=xHt3(9zbzt)KEOEYD2R@|lBG$!Uv&3;Xn!llQ3jOEbv!wWszs=8q*DKl79;_SnZ}>V=FHn&D&OXIBy_@e(VrFMc?SI{m+M^v=ku9~qIo6S868Ag%5gq#zZ<G8^-q22H{5uf*PCO{DSJF9-9&;mGoEO&TUUVL7#WX!7w%=;V_sQzQPN&57C~x@w$CYZF635HR=I2mmy(Oo_I9KoS?^xP{Es|fU!oO!Iqs~e7o3;2p+*n%iwCHz@=I2mqbPdVx{QaA&Z!5{KT|Uvv+h6)C$%NnIYH2m>AKB)vlvaWQgg=pFPWI2y|NWmxj&1&b^(T^EO&kCJ{)yy0yA40s_9Kk(_t0GM_uyMF#@C_Wfth{{z7D<wJqEr6&V(^O3Oxco3QmIV2OowWgzg6)1n-6J0q+GLfbIhy03U)Tf=}3X);9Ld>@@To^emX^bMQIvW9SR;WAGE(zJcaIUx0JK7h#MaLZ5>lf*(N7f**j-Lr;LugR^bBVB5F0oq}eAPk~M739t!13C#eX1fLQ5h4B^WFEGYGLr;T$249Ar1D``5U4}hI*~jQ3=Xal=Zl@oedwnC^{|ef81%9W^-{6_PL0>!1n1epZLBBhFauI!Y0el1c5PSoC7y1Bv7kmeL9()IU6`Bps#&|H^X4^E|R@ycnItw}tJPSO+w!dt<Y1@CcRdnO(2E7TsiFz5^|F@HmqU5vfL+D3PckoBx;<h!mt+{P&p&Ga?xI45bxI1_NbQqZFWbgp+Sm;9VSn!w781R?iRnX($Rp6b_zrj1f7POcfXA8_ap*XY#v>3PsxG{`zH7KjA8m<`^h8_nqWBez4G2lPJ3DAY$1n?T@WbhjBZ0IoXZ189p<9^Vd;C|pPPz~G#>;-KO_5yzbV_X;77+e=z+qN3e2GGXf2H;lEw%}Ia&d~1Q&R~D&0Pq0Bfj^9K0Q5_60C);?6?h6b9J&)64&Dg0z#G9SP!<O%xMutcS{%%baY5TkK~-pRunKMftpRQTZVzn?ZV&z(#@HKL4eSkW2rUe52(AQWaaIY}j6Z-TfSEDA4c{8@ZSWT8Z15KFV(4h_VsI#o@nC2_@L;env<ui5+z#pmZU^>+eggIc*RrhwRE2&5W?C1lf~!JngR6ooD|vBT8Cnrs8C(il9L&@mTnbzW>IP=|0k{yj2sA&KX;E+ya5-oNa0NU=IcQaIIdExcWpHJ*sWh|@xDf8aIMuc&+n(C?FVqE%0=vL7ZS%2hlx+i{Gr<GF!O$phFnAF(6}$-im2Iu<4yt3@XE4UiphdyWz!jjsE1WBU-zr?c0)K`2-@+IdapU?F%#3kax4h?P%#3j@H*Smzxp8Bhj<POrIyeG46Fd`r6aiyA3C6fL)Cb%N+6L+aZU*fD^#S{!-#fq<`$2=je&CVNMc|R(8PKo5Gr;Sizk}C<)1Yh&(s0fA4YUrJ8RK&BwFZ|1H?pl0v?sJRxHaOSCycSZ-BEO?KlC&3XNV7f7~?k33g9;2+E5k~wV_4euZ@`Sgq8(+f?Gjrfi-A-Xf1GkaA{~EaB1*wh$j{|zrh$sLnFWuh?Qs<<GC=#L!iCEP7Do!G45fTH?$?R6SyU~5ws21iMd8F#&s07P377U+6>$f+#1>e+yU{|8pil@=t%JA;6czC;6dOJ=z4GncnLHOyac=z`Uboe{0Pe8?-8yUe~g%H1pXLYQ;5-;Fvcxy>kjP$?F8-v9uDmZ?umFE4r4r4i0QE~#v!&%fsTRd;4$F-P=ByL;=4bLac5|4aBakKXBcB&Xe+Q2)4njqy=)r*?F!YvUBNA&^}#K`)uE-q)xob7t}O0f!x-;?MuVdf>pNhKm%$j1gAM@?L41#cG43zSf&MVY-E3<QZ3^`UHwD*+wglG)*Mv3#H^O|V31eJIm@}1NjLX_q0$K%H9b5(M0c{BO0Jng)2DiriX#r#05jqIm5!?$J0`3J4f-V6Ef#*QCg6DuEp^w0k;AAM9Kgqae{13Dym>J^|@U;Y&0M`@dSUniycDDII2SK}o2Z2XI`+!G+CqRdThhx4?fH4k(hJeGsvxGT03&wZ>jPaMSiMGvzP6jib3!VvH3}d|1w&l=y(7E7w;Hl8b;HltoFvda9iQph`plw5;<DnD56VdMR&?#W1W5DCVL!te_Ogn>_`huDE0uKcTy5;4OK-d7ZaU66AbO3k=xCgW=xCgi`v<0{=xGuChxFpmaS{=-k<sEliGtNRT+5z5yT$2T3yveo&&@kvS@G|6`Flc{p7&s8x4IBvWBjlq#Fvg$R_9?Upv^}^9xE{1AxE{C~v_7~RxIDBbxF&K_c^Ko8(6Zo?;KE8?{wfS(Tu|Zr7p6s_CBQ|&6`)nX6~MKi9^hJFPiPA;(~e5szK?M`XfGvipUBu38l>dyD;W=l&QbFAp^QVJkxJgamGNR|vXZyAWxNIYkCL|+W_%mUa+$MtX3X~1OzXMj?X?+Kg0^$Z+nY0P=$4o7oV`3_w%7k0IvDB$9t<7@9RwZ)4uy^chk|E7CxDrTfoFi{LuY~KgCn2|z!Bh;wylLOf-V3v{SwS{CYb4B@FMV97~?4DQg9S_y<1)mT@Pa%Y1=yJ3g~k13UD}d9ylC49Xb^}9UKfD2Mz`YK!<<>z+XUnfWH8DfVKs905^r!1v~kxDU5Md+jiS=^@nYnZCeYy2K@uf^dmRU*TC<fRl!wJCu3%eUqao%Oj+(@%ybj@C3u&TmlJnE*MisL-n*dh!1HXIXq#?ZSKGc&c%J(d{25dSe+KRYov7sHNyaRXhCvrVCxRD%*Fxuk*Mc`gmx4Egcf%NOux*TOQ*9e=TVLpS=u|LM13Vr)9l8O$0d-D?F`fXO2cC!LoB;g-JOMlu+7;XtZ5j$44<3(uFy3H~<0{*h!5A;JZ4Pt^bQO3Bcnys4M(76cM({S<_S&}Hwp}pBvCwVcSnww32Jj~EYUncXYOn!gJR7<YJR3Ysc%Er6#*;8lCt)5>g5R0fb1?7c;F+B~z<338jay#cV9fFg%QIWucph2{-3;9d-VEMh+X375+qMU~8@vY`2i*bQf!~dTG2Q}Q4`vz(-U5zs%gcQ+Fvii)HQ+TEzi1faub|t&+c17#!5GIw_kx-31IL3Cpa;MQ@SF)S#yg>L;5a<PPG}5xC)fpz21lb!E@(VB9`|6}(Y8-*>kVV<XInR@7xYuG7uW;F_!DSH@F(CVwiU3gvTaphjGIH7fSZH6Ks$oFfcrsvgZqI;!x)c%`hiD)hY8O!492*x8($|dZ4d3{miJA8aRaEATi!Pa#wygqE$^EJWA;shedCB%_&1P^&~?yw@H+5n+hT27ZrgU~3h;Jt9CS5!HGVe^#`qcZ6__dert%Eej6ZbC`|k1~jBy#L2iODSR|dwoJhTb83C6EHjB$Qw0Wj113g`UbpA@dK;8;B8PcX*6LgT=3c!po0tlhujnsGinOBrw(v?(7nKbR@I2V?fHfNdW`i-A7|m$A*?$L)jC`TkG;iLShV2GuA22fO~)-<1DsMf}Y=_D1CWAF=rR<Y#SBKCu7C4lHBY$+hx7<xL-h'

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
