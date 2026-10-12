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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_012.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_012.stl', 'source_sha256': 'cbbb55bb09e11cae786528d2a893789128c1751da9e251c7ea780ee2b08c4d1e', 'input_faces': 944, 'input_vertices': 494, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09324399381875992, 0.07685548812150955, 0.03522969409823418], [0.09083058685064316, 0.3267679214477539, 0.1534968763589859]]}
GEOMETRY_BASE85 = 'c$}r22T&AA*#2iRhchc?*N9m$$8$`W6>~xv70dwya~gBPhyhe&RWO4Aa~#Ep33JvlfTy5$r=I6|r+(Y-`|R!Pc>k(@ecx5R_5Aj+>FMb-Jw09L-6l=iJQDv`TxwYHUUXt*NfMD&$|H^SA00eofPYZskpUAdQV#OPe+~_8-?g20Pm45Gn&jc<A2eXJM?I@YgMoECDq1}Tjv5_2y5C6OQKS9*h40mGc#yx{4;tJrz~BD6Y>m1#Dq5?Tt7x5K{a^l<*<J+OohJuR+SMB4o6yLv`qkA3geq@t9uU6Xz3>J4J-7D}q3W9(<f}86UZ&q}dYn)>Q?>n+e)B%gXZ7U6LamuS*x&c@BBjrNU@vLb^z2Wnc~1P+yyA~jdiQbrgs=GqUM0U|5lSx?=taKr^x%2%Te?1h%4sXmmD5Z6sXW#*9tX)U*n-oy+d<`5`z$?1e^<01`O;#E(kp8o?4t6POo*fM<S2ZW(v|f)N!Rtv$NtO&@@)%CQa$LkkL{&;3*T{u%IUL)^4IF@A>TIgHQkq7t_$U3Yt)5&?P(C-mmamBuG6#(`BLhYE0iwj`3|~|X8AaMnLpy`dg%vfq%D&6Q2ob-#B=$QPf$MXmyxfXJ9CZhw?_Rvr0o~7KkLL<Zbu)=NA9ogrt;U@P3>Zf^5%LND3h;VYk!UFxAZnD&#(;SOV#@DbvxFg_LA<u*+uo-ZymQwj&jr=)ceobFBC%cqb$n8{pZmU^0gu($hS^%J4OBz8~f)E(RG#7j8s4Rb3gK}`6pkZ@?^}iov#1e?pSJ<w8yx;67Erduzpg=S2ld(emE-pDE-}^Z8?1>8(mNTl9p6)I~qgRy^>77wYLYjJZWOcxAh24<aV`CeM(vDvfrcu)tls%NcEs(t;zYQ`>0>pLJv{@SF>j!UoF^+^08I$+)Cxom9&%Ub3##ScWdWDo4Mbe+(GwydpecFHfIpGSJe*WYY+Bc<$hRv6XoyOh|~9rr23bOJ)r)k);qhM%31q5l~aqG6-$3tFP?lkd>EBSefxPIUAN&T_6Ibh{FNPJ50T1a*sr{l+r95R>gQ_HHrtKuqGmfv{X}kFoqWAm&`rws?$(|3@6A0qeYa2KTazDAKUcg;ldraQzfS3LhEhJZR)1}ycAU_Y=Lfg7R1Z??59HfcKBWF*3m<sc=u06*C?8vmy3}6Q_D9KAi<YAMRU$k$(!Y0_#_4^M&T~KC%=1i_A>`}ZQf^Sbms-Zq-*p+p<++>0<^S^&^+UZ&zir%aYn`TYzWA9`@7kHm89A2H+de<1^tNuT$d|i)BwstTp7NJ_xpO`dOW5D!!{f2<{jF5akNv4U>h<5KKCQmD$=4=*rv7H1Ke_+-&t?B>VXn7ZEqFd3+>?C$a^Nj0$LpP3|3li4Z=H6D>P>mQn|yV6aq^X4zR`8%1~+$;j&SFEhCU`=`)51fS3t@Z^8aYb^_DZ7+EERBO1>I5gv;+aV2{zacC5qY`MRF+k%BIfFMm&<@@Q2iQF<llEcv$VZ8`msGTfiXY$0DOypG#Nn!@>v-NgAMtfKiu-&2hGvphDEue<6N_n+XNJkBO{CtoR$!0lDN1zlI3(wOfnYc48}{-!X^OUjf+T%ILwsb5)x`$W;-O)JjjdDer*k?uPxn(lY@_080dXI@kJl~<Rkp7l8=$(L_zrE<t2g{YrfL&lMB`)51N@A~sr)UT{7zeZDiX0mZTd|S%%;p%7P+gcnVUyka+{U`i5`O3gTbYF7jas0eqyMugd^-<g|AGXjupsia?zV>G-UDtZ=0r%&~5$reKM)hE=Gk*(RKe`zCdhY!^KYu7g_oZ#Ius<x3^0$87OyyL!{uxDnqto2JZ;J49Fy<)v>euyjU1j)1o{wWUk*`#9PcYt>yeoqJ0z<g|ch}<iYS&uwrIvC0{OWa(>R*fV<@_h)r}<XTc98m~c6P)jy05SsR6qKcGd!*@)?|N6GS7Ry6KLL35-O1|-)cwe3N3p@s!u(^gM2+SH`TwC+rssHB?J3ey?OnB=Yn!Ca3ke^dIHt2t<O?Y^>GFAtsmFZ__bYl!_T#+dC6D(JgHw<Kfj@JDtbCje<eGQ-(51-L(-`Yblu-t(epq`Y(@8>e!6d?>%I@-cG+8q$HnJU<m;OnaR0yAjjpSIKFsMqKjnTH5JK%@{j!byRg3sJQhOQo2Q^K3_VGNmEy_UsS<Q7QlKSV`*8IHaRED0LTJEjvAIZe?$@dv_Uz+vvdMZ!7XkIr~yF=HPD-0%Io_d?tZ-H~@`L0z<OTJd|4CSN0Oyz#qFgSwp>5-k<OJ7il%A>VPTu12>8&W^9UjIb%s@D1p`PQ$=+|M_@r~1*n1IX7$@8NZwdW@gTU1av>wdDHGv4Q(lkF?~=&pYz-de#hD|7iUuuciDu*5>ulliAen^5jx$D18TS@@-wevOhH=`PN*Sd7Tq9ipRyAuy9I$E`iHGBZ~8%JCA(LyFUH44lKg?tU41${+qSbAFP)aQh(5FHOSX<Jm&HHeHQosohw#T`cL&~yvScJbAO9#K)zC?F^xy{SXP>cm3>voSKrs*{6|mb_0@qq<V)RF@$+}`dtN`^9=wwB>9B;_MauJ@p1;b2s^n{Jrg8mT^`UYqkMeN(lErD>mVBaUJnE1CSwZzPcRkgQbx{t^|K&RJWxv`~|LXqXR8Bo<1^HS#KTbC!h1Y|xg2`7iSL1e{Gm8FQNomQx9M0qPQ3TJ2sa46>M|`CIpr5Ww?;T3I*UPCt7yg;<S2~u5>nBS%`*Zv#o&KyF=Tq?PGAhrsc<w)|XVUzj7mi^+;U`KbEy_v#O)1fDnK2)^*9rP}rEE?Y-<F(@*CXnhCFE-dDSzo)2(34?857CZI(qW^Lhao2ywjpLE~5Kwxr6&p>oD#od*6ppeYOrIUmEt1`{Cs^3(5cG1ivq}Ud8ECpU)@%SA~4-ca_tBu1CJMZ63}0)}-=W4>>=~HTs$|kbU>HF1~ee8um+lnB!6p-Cwa^A=JfJUjNSR8x%i-`k_yAp0BVD(I@pLUv6=X@AqOfzi&;?LcZ2=EBh%AIG@=!r@NH1?{vQI{7@HPdh?pohvuH{(k?gibN;Jds77BJ`iARguKN^YKI)@LZpTIECmVg+8=cc19ygKt|COEeys@v>*gxK4qA`E9lLxoU@!GEGUvdA^PI^pqEf1GpJL&F{-Ztb{_OA?@VD#nWLY&X_+AhBB%`=_{R{D*n^1t}V{cvphV@6*-U60oxx2-O|x<cjWLR>n2zkb$zyi5H*+|Jic@^JB`lt*07B=_;g@~BB=xV=*Dj&rGpVRyN`(hVMK^mV_=oIXo_S3f0@)0dkUZ1lC4RnZT}2fMUa?;Y?52fNg>qo0_3+l|uPPb#%^$wwN-_oaK5b-AvTdX@clVWVBj`4Z*t+|tF@Qm%9QQTGB|>cPJ(rw<Bq@#U0zoPNx_fd9O&G2>l)`}+ace|FDN!dF`E<oR~!6Bpmw;yBOq7j4`>bN@clcwK8UKfkm>%UpbA=u6J0y5|U&^n-GoHu^vG=i0vycgY9ygTwz}yfh7TNiPq!@N?kV=pl4pn~w6leen8Gqi?nR#{Jw9;Nq)KYx4V1^jH^P-!tjPf2PmAo7ZW}-;l3IE*s=h{}^9-WT1<$KC*GU#P9K^@%3&v&(DGLP8oguRXnc`+brV#_C2sa<<pACvlLQPGy0Oo^O5p6^t92pZKzGpWwqypV@BV)EI&P$)el2X8GU^g@7vhsH$39v2VCZL@AtDV*R`(c%ky@zZhKwIxnc|Xdd;$XjJ}%S$@>ZWCdRsyvt?U;j~mnKs7wCe@%|fnn4iCCs&PIkxoLkuIo0-{(U-lO({t0YKdHM{>qq6e5>4wF$9{stmj-z8zF$Nvzn6J*QpoRCi}xopw$qHh65D~-S2tenH2Uh8_PkGs{e*x0n}>Lx%C8F7e}!D++m@u#x=zl%hu5WBUiNk!7kKWR_v>Z!|9wssOX}(}u3vL{y>@gLqp$Uy!Tq5{bZ5$^b|UXPm1}d-=xa^B@ca1icwV<}x3(jH@L3)&e~okT<+$}c|CgW1{?oAf)K9_!_&vhw!f~Uo>Vx>bJGdLSZ=)Ke$)Eg=_elmcME~sGv610^|6M0sTiuz`nV<V7S9dX{|98C+>E4Zgo7NB7ud93;8R|zGoR-u3rYJ^VQwFhLeb@k_Z%wMe{;NDe^!KK9i=4jAST4_6?zbrsM~%Mx_fD?Qnhjihspm6JA79ADS899Q_%Gj<X~ci}%AgJ0E^ggi^MACL=dluaUU%O&k^bGhZfuxmGTo1Potd}PR7!7NH|B0O)mZ=ku5bUIInAYAupZXmoKoqxX<e$nzOEY6|GN%Xd(I)>v`*Hi%qRbcb#l{X^GQwb5nA2i3rJ1tcCBVd_D$=2t>Q)YP47Ee=4ByN9>;sciO*CXb!Ge_^4m}4ea<3PsQ#sncga^uFX8zu^!kzi@~tzXc^qZPvzY#V|0(v%#PIv$H-GjEr{nclvn`xY-~saWCA`0<^^NBA9v{fJTKV~9+n-9l{387lO8;pgzmK=Uc)#OKzWIGhyA{CcP481$;#N*?dN0%aC`;+L>Ag?!2`1nCo~ZO(N51)eP-#7Q8L9a_wAmr@&F|4l(+lLA-*fdkU6xb+ruTQfQY!i8_g|&7PblSYdLLJOCy;NAYDf1gr?ldJ5w?MRCB}#Q&&NLx|EK>jmh&&Rlk+j{GbqJ&b9(dpd;Y8|s63|keK~z0^5u*3xnF%a&)@Z8j*+i^;d$E@v74WpnG(r2?<YuI`mUtk#oTy3b7w23|2ByHANDs+-R1Nxs&IO*7l;4LS6VdTdH&1ymE7Nd=6>kEocqa(YpbaIrhO7?kw3^+BT8aibmII2%dF=5smk>~Gb7*cm1Zu!lDeJu@osG*-?9HA7q-xIR!_XizG=V6*5fhx^4G3>-Cl{bzhv{w5oYwI!`XOzC6pxphyAEC<HC4+@cxzKyMXL<hkRSJdE8#vV-9h<We+#{)&<<Jw0&*JH}8+haRbQzVLz?>W%8{dN4Or^Zs77a{^sIa-8{G-M$TPB<*TW4`o!~G{<V?hoA<|*I?*oatpnq^{u^HB^hZ-UAD{Z%UZGjm(%)nM(3ZiS`|aE~^3D5@nwn)DscAn`n^K+pANCuA<2XI`Ih95pw9lypyyEnx{Zd=lTk>t4OL6^Y@!|UU<vsaI^MbtZ9lMkFT}R}Opx>tbSZn%05ypIME3<JubQ?~-I<*Ps|EfIKr~f$e&HJKqFZcD7&a@A#c$Hbt?K70?^HEOTH?CD{y)l2=>>#e^uARv@@88;T-XdQfww&*)Qzp*m<WG?<`LB!S@p7_1`C8fC><5(P^2@^_d7PQ{v8zNx8uOQWj^cWVI7PlK*AYAi=W@MOdgPM7wY)^><ywDp{-%9(C9JrO(wp|-^%Wh-|6#v<(P8q<`}z8UyX>3x|MmH=IDgZ31bud~4dk1?JIEn@$yfAp+`czo^ZHaBM85gEgSt4Fd~5H<oW4UmrMJeZoPX95?2l{C{q3WTd{t4{PjiIVK|M|*e_mH8bq?@#D_wLcj}mf#+r>Ybd|Sv$tT%3PKEdhe`>Odnj+$JEe8oM2(=YU-d?dHh8(qr(p$PYrXzz_K`RCro*R45hqp|#QXglr?!$xm3mR~OB&iM=vBH!^nNcD-J??L*oNn9TD_oKnv$TxqV(g*Ef-|;=``vUF{e$UAN;d@y>3xA(CeQ(lzi;(a5j;6N?r|-7f(@N}b;rCYg#Wt?bdG*P+_Grd_hB@r}G$-HuT};<{kT3aH;Qn6%<FR*d&d2n<Pg&{9`MCALe4=vxJx8!_`fjLy9z(v(Z4BohJB9m6_fYmt-yf|X*tcqPIDPUO-d~B`;&Q*X($lz{U1PZ3Oy4*4&Zjtk)AvxN^LZ|(>AS7g=nB_EYzW_1p+C8t9g{Y3e{%g^smA`p`An?G=@0JadKjE8%2@x>qGX=0zGsax-j^ISl6*B^qbOtj=uaQ<xNGYbWvpk-D-WMrn9+`Wtv;_Gq-UW#esA*kWGPJ@m-0&ml_+C5rBi)4|67CEuf_deKX2pmdj*nj{=O`AnnJ#stq;y!tl;`-KAo>?`c7?a8piq54#an^`TV|B_>#+YZ82?my;0{W=i{$(dgTT7J72ooudUBIuFqnrTyHa5@qOjY#{Hq;uk1U%v#ZCsof`g5zWKYn9#)RVx2+)Gm+iilp9{UqM;q@~QBU*y)4EEu@xE+BmU8*4HsJJskHUJ-g6Crg^3CT5^qSrIJG1E=f?l1!|C`SPDAmVsIZfvo^lFp1JUIU#dk*6B51vc7JdSe|)w;r8#^o`cqfn}1p2K+zz3^Xj?#Mo$v+p>+f$yzK#hY9%ocB;0T%+?IO1ZC`KhB59f8^kE3uV*Lyk$OLp_I)+{txF&O8D|TXF8Xn7hTBbRvhPB?$4ohtWxkIr#GL6$@e#3*K~eH&zp|VBbd(H=y`JTdd+k`N6Axwe8)K->y?TzM&EqSN68Y(-?ts-h-{hod5}4r^EaKt(KAJJc}(Y&9KPe6l2)?<?^|Zt#@98ScTzH3;q<0+N=o{>Tppa8QVNu#=Zli=1>cwH{FTEupTE+i(tIAxbiPaba~=Dpb7Jzl!h9akblyx(t;N3SJec+>fPM3Mw&Zzy&dYQ@O-^3G=g3Uw(6pE9I6u?*H|;XF^S|foD!FsHPY>t&Go9<xv{~dk&h<%kzfnKePOM?ybgoZ3zMXvYIX&&*KRgah=LzM#UVM(gbPiCCnaBIMrt^w&B+i$a&MRu`hVpk>(>X~kd<CaBovV~rogm+QK2ux%j`J~{tCSbj;rD*ixlL`McdW4;|2=Ox<0|>)bD?s;8Gg>2&XL+G58!$=ojbLbJ;c80oT~0|oP6`SR%@wuoZfs6HvfG3JM+0&-F+qb=5x9Bbtn1ebGb_11H4`^oy*m;yYc?L`P^@sP3)V_3F{w6@b@Isd1K{+%D(B`vhsd0f44K8L$<z4;C3*bXVz2iv2QvTZB6-|*JY-2)cVtTG+xc;uB}f)**Bfjww?LH_iZ}wt)FN~<u#x8R(8s~PBESv_jWlA|6tT&Z>^%(LXf0PQXXkwKf_UYVT%78`rk+4ht&B0ItpL6#{c;!d|i7P#Hsw+2*FkCQ4d-lS{Ym)+!!Ia7PKz77PyH$s#+vzqdkt=;}?58wa0VleeiSeBZT1V(4*j^$mcpju!0a=5Ly*n5PVm(l|Aa%BPT*|L8w2tAh<O&1l$@t8G08y8GIiqu5};31=q#(kAmxhPebp6@1rhGBLu%d2u^|i0)7d72K@#64EzN89Q*|Q5c&vw1$q(s2z(K|4|*MZ9d*4AA-FU`a3*L$a3=6=iB;6mZPZl=_%=8U>JJVBPlMJ0PXiBuTERoW-4KF{Aq3}w<^=x)%>vB{&H~N@EeOs7_Jp<uw?;qkL<k-Sy$>D-eh3x);30ksmeDs(gJtj~=nL>A@Ee5Sx6l-@qkp`Gz6J|T0>1^PLLY-u!LJa4A3*PdAAl1Of-l(PAoM)+F8Dn7GW0R{F|K_XA@~mTHTVwr9zyVK=u7Zz@HOZ&@HOxa=o9b_@J;ALuwy*jL<l}(kCD*1&@14%;PKFl;PK!t(0yQ`rNLdm=@5cHORSl|A_Sj>ig9ul<0TAy7Hoq~1KYr>phLi`z;mG8z;nQp5P~~Gi-CJX%Rq~P%YfaXxxkJw=8h0tz#c`QS)o6Hvx3t>vw+iqvqAHKvw_P(J;9zBZ)FjJgP{+>!QdpQ7;j1VEx3(^^%A%ZI1%~=oCv;(5S$Es3x11nm5dOqLtlYkVO;45!MC6Z;9KBR2*F377r;lr$1Tn=DR?Jz9rPf09XJ>vI0||m90fiEy$lw52Yd(|54{JD2cL!B2A>5VgI)t41Mh;~0Pg}HhTa4p25ZnWU=6&&;vB;(5Q1CV<0oiw=tyvJa5?B)a5->E=y-5Ra1Lk}u+Vhi9N-j*L+~Z280VJ|f{#Mag3n?+A4Le>23-Z-29AQx0Y`x&pp(E6;N=Lx6QLc!jxj$GA$Y1i7C?tXdxM9Ay`g2m-r$N*cW^~;HE02FHSo`d`Qm4U;F{3<;F{oa_NWBS3(XJC3r>p=oB>({EHo=P1K0vh2Ns$QYyoG2mIY@5mw*O?OMnBRN#H>6JE)jz-r=|4?iSWWu+XdE?%>V{!RMgKV4*r#=q>O$a18VmI0ifhAvgkh1RMe03_T8Z%r%>#yTO~mTcG>FTfjS@C%`+vd+f0ndJ=j9d=h*BAvg}Y9~=kX4&4pj4&Dac3El>t2wexB2yP1v2Db$_L<sH&jRN-rPk<f*3ylX)055=^1up<kfgS@-0S|)i0uKWFLJxy|!Tq5cxIfqrx&rJ6ZUt=(ZUru3an7M75Q5X%<Bi1n2lOYf2*DZP6$fVkXNHyoX9j14mIP-6|0%KN01Fj!>z@e0ZxMoTLN9@Df=@$_f=`1FL$`qsgZDzCz<a@)p%LKC;EmAb;Emw52*FFB6Tw2Kf|r0pCFlGbiV(cs9?{U%&;{Vt;F-|j;F;i&P;c-^a6f28a6hmgv>MnCJP`Ubcp$hxv?jPe*aun;>;vv0Ip^^n2*JMg7-5ew_UH>81nvuN5A_AN2RDRP0yhK~hUNteO$#mz&WsQ&K{J4bTEIdxNzVTSr-7CLrvVp*27-%%M?v3#M}gl%#a#a$+8HcD@JG9TkXW1JxA2=I?KyCBa1Ce-xCXcsbPTu@xG+L+Z)gO#H+U>`Gg#;r@L2FP=nn8S@O0=N@O1Dzi}M*U4<R@jdJ-HBj)fio$AY&)<G@?No1ojlo516s+rZ<%Euj;^Ex~o5ZNYWGIiU@~Il=!(9D=jL>j%yXE(V<dE(WfE5L_9$09+Yd9y$dqbP%{a*b4OpTfv18f{Q@=gNuNRLjAx(TY-y$vq4LMvw_n?(}L53KS|E#$0vl~iwME-2*Ed?e}Hd*Q=#Iyl8WDg|AJ-)ixB)bG$UAq;4e_|ED<d9E%*!g0z&XP=uPlBum(L1*1#vAhruVnhoF1GhrkD*o52Ub`=A@a`@k{Kwcr@=c7)(H&?R7@q2M*(b<p+Tb>K~s^VzcrA$W^D;-EXA(cm564bau#4d8I-OmH}O8FVCg8F((VA6Td#crJJzbRc*hco9PIY-oS*Z14=I4_Igq@C>jD^#!Zo=?KB|p@YEl!7HI-z$?L#2*Hb?BfyKn<DuQb<G}&Yrr-c@PiPZxPjE|UU2scqb7*aFb8sVQ6>uYP3(5J-panv38)$uS8*mqBV{jL6SA^hZ&|2VT;0Dkp;3l}Y1_;42v^!V^w}XxV3+)ST2d)8a53T|BfHnksfJ;LQgN0@Wmj>ssM|!9mG&5MJ1a<>wgr)&!1eb&s1q&SoE(snDeGeA;5j+|^L2|AeCLjd=3KeUGU!gU?A_V^eEd>@K_$jn7ScG6*;t-r2|K1y%9ozsq7A$lcxB=K3Ivwl{ZU>zQZU-I!jRp?@&xFQ;XM$Hjw}MxJ=Rh}s=Yaj8<G}vl#?Y4F#^5Z_I^ZneClYH;un57Ap<=D@7$Nu(RIC*q;kV%D&|+W_f?q-_fJF#?C2<IT4Xq3oAvhUY9xT)f79scrv=CT?;Aawt;0MqmU=f1vL5qTgW&?{5d<U8yEJE-ts8}o9LI^$sy$C)7K7tT@3>ptU20o4ud=h#Cd=h*LnhHJzJ`ep1d>)(t{TrMBz6|{W7J31E8Jqw;XZYK5$XlppxR!>p2t8pa+X<9i=pn<s9KyW{Jz%(Z!3UxHzz4zmp)uh7;8^H(a4dKyLhx4T8nDoH;H}`D&`pNF-GuyvZZYJ)1=n}1IUMDQLwS!wk3r)MZ7ui+bcf{Z8-mY3H%QL@Bls3HTypj|!FQm`BxnB=d=EMoEOega?AwALKo?2QaUs|-b_BnG&X%0xOK>uD23V*nImf2p*U;&bb6g8{jD5i`q4Oo@{2=%_bfx5+PXs@LMoP~4NAP3lV#zsQ34Q_{FFEHo!7HEv;1%E?XisnuSb??#E8tGh=HO1?4$wy64&ctv7U0g{0nj$!0pMZKF5qF{q0p}2q2RFy!M&i(z`ej;&<0?kGS~}T71|Cgv<A2;xD?a_Tnd~IS{f`g2RI)%x8z)x<VFb24s`<y%?Qp8t^h3w7CIU%bON{ncnb7au+U$?Q^2#JPr<Xm3!yq#=u+@P@L=dz@L1IKV1(edP%m&>aCK-^a8=Y}b%fyJ(0t&0sITG(!G)mN!P#;Dg%E;UL8pMH;67U+1owe11TVxr^ntbo_W_rORtHx{naV>8feYap<?*-W@%y_y#3oi=3u`{G&`RLE;EK?n!4<*vpk2ZBz@4B&!JWW^?J*guLWhD?@C=0DVbHGNVc;InpTRxAO`w&)O~6&4`M_1c?g+sas0999Voiif;6&8hHK?e^YY4$t?eQD*8}vK)8#p)qPSkI1)N@5}Zm<Wm9@qn13)%@>3)~($7~CE_&`|FK5rQY#V<B`YbTW7;cqLQ?uLQ4#&H%3lhav>ef(`@E0*`?90FMCof;Iv70yl$J0XGACLfyfh;QR=|Zcq!@(XMXzE%>^`nh3rQ-UGb`-UHqZy$aq9-eqX}T?oNf5Q4u#zk$Dkb6HqL+vh?b@Brrmmx0y-mjTy=wg=Y)cYqEAcK{E8P67`BPc`(3sR+T#pi9Baz-yr^!E3?mp{v2`!5g5V;0@q#=qzwJcs_Ilcs_U(v=?|3xDT`$xDU7m)DzqSTpgMpTpe5hAvg`x4J=gj55bG=5oC`g(9z%};1Go10DE+U_JocG_XPVugTP+UzR)0WUvMCFF*p#s$R1%(8+0+)29AU-0Y`$@KtsT5z{?SWXF~(Pv%$j+_c<IPxT8I4L+eAkf$M`CL3@H5ftx~oz>a!piV$24?NtqJSPj0TO})_OUZ^`q9}wIJ8fbC$8Ns8Vi!9DQCV0M~ejR;Ma5&UvarR-s8=#REXP+0m9=gWj93z6)LYG^dV@mKc=xmE~3<{nK9d2=sS;0e~9WBl=F1UlCJsfj_;F{2~7UvuyxC}Ip#X08)7ITt!8;e_>H2<&v6}a<1@tlxc{>R|vzjQq|ZT!n@RV3#jYVS7b#QM~}Fm<DkW|_p!tn@!Q2xC3'

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
