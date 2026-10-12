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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_010.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_010.stl', 'source_sha256': 'd4ee049aa6f395f92d7029fcd684848c9f37227b2b2590d3ed19f5b9cd60c9bd', 'input_faces': 1296, 'input_vertices': 717, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.060518838465213776, -0.1735791563987732, -0.2509348392486572], [0.11301188915967941, -0.04760351777076721, -0.13351121544837952]]}
GEOMETRY_BASE85 = 'c$}r22bdJq)~;)YC_zO*lE|nal0+N@0fi<=1_`2qgdr!%h!Sm-qynNOK|%u(MRJbKz|6qFOrv7rD7J~C9*hVc!_nJo>fQBst=|86?sKm`{d{kIz1E_;_S(CvtE;9%n|%38I_`hBIv1u^uD-9S<H)0!Q_>mNfArYFefy8OYxv0VNzV0ozWir&e)}%%I&@8P#yJzK^y@#S@8~M^Q>r{L;QlH#QmPCXF?#Ii-oty17~QYG_|1DiIi`QiA2X=;$o{eIJL}f2TO%d4YK@f1DgTfE6^XrsK<7WVG?Le{s@mqGvRyiS=4iY>{L;pFKYTXd);#}0yFLHSkIox&LezQS!L9N2o!1BD*!*B>nKM40e>Wi>-^7RSZ{dGEe+<mA`Ttvd_*}URn;+eL`gmU6`f;xR=B1<Y?^pZg{RYb|^Sw@Qf6m+MuhXMXj?E9gUBMb3ty3z)<~wcP&U>AKe4qIK-SFhJ9IL;rqFev!-~MrFTqM`#2j`4C?eopJ=y)?O#7FBVZL{@N@VETieB-t1np~Uj)O`B1%@0pFlwtFu1*_%lhiI*ezJE9T>=QXQ-`QHpeLVx}ZS##w|G#pq{@~|M+x%$5?HN|T$$jqY`Kp2Ir`GWGLt3=;Hea8t`#s0zJF}*{`}2HPU!Cx0U2?4crE2c@K0Lwyep~;PWAlU4Ue2o@&Yt1=M^|o%f1T0k3#_j{bbM)^AN-(h=700Obs&AE|KA<DGS}vZ`+Sz|^G#prc+<}&zVT}R>+jb-$L0sKYrE?}aE-s;YOKh$`GM7+XWRT>fsUCrKV{Ow^t`-3xBADWQo9_RAKaMg?zaZpeZDjNs~npj2rqT}q23<fehyD-n`84$eeH*O{(ZvcJGcKcuWv&?yyNTV@K1Act^NZ)XWRUgp^Y<be(<KXdHW|^^$UOhU!Ij~^TX$Vb;tLME531bc7Bj!^8@8Ky7RPW@^;_;TyQSO<_DI(>F&?&g|_?p`ImQdY`$}Tvo$^?cSeTI5AE!gw?CaHif#Ax`D+t$t^UFSZvD<Fu0OfghWPoF7OCO-x${r_H{Z-V;|E`CW{o$#jt{(_ecTprd=npSUC;MAgM%C8*nB4=kXI+ARYTwY5B40AYxBb+Zpzyaq0EQ;@3&gR9IKzd$r+m;&iB&^n;)Hg<#@dB?H^U&^HqK0>-ygQRQ0|6sp@;as&9N<-`oGx58n5buYZCc-x{&`;f_7CeZE;&b-bB(#0P$P#`Vp5xI86d^=qeD<D=u=&9wR9A~(A0<d})u<L7TUqf4&M4;HTO_QQ|Q`TMQMfgGD39+~NWu6;k#-){pu=Gy!~)?In=X>Yyco4?^I9dd1caNXV3_)t>5Oq(AFev$WnQ=WX;*N4G|dvk1l_=l6HZGOtWAsIG5bZX-9c;ED)uJ84&s&9N<-}t(|=|f%L>swXd_`1IFP5sbUA@_Zm&x`!UA~xTtHa6Sl2QD1RwANWuC2#*nLtA`(?o=rdvH8J56Z7gv-+jk7j{<L9&b9f@t#k6?Q;L1<?zi6uZ_A5k{nWl$KaH=CyTTd2`}=%%wOpGY7~jR+&jtSUub*Qt<l6jT*VXRvOtb&^UQh7)8aXyUeE5+wHb3y~g%dVEZE+!=@6BIT-<$8$4<;4d;p_jacjVf9=l-szZGOtg^BFcjZF{lf@xIsps=o1ceQ#c<`o`Dwz5ZAAjj!u_^Fq}(zNw!!`tBXRK52L&*XBF(4!Pqyy#9{(ad!eob8UWL?lJdsVM~J@zVUr?evZv|p1*Y3=BG?=o?-KYf37?p?|ZLb)%RY%sb909TgR-o^+#sf{6LFw?z}ENVTW&?)|nHr`v3m<l+QQEpE}<7#0M5na((lC;jxz@Hb40E6>EI(?uJ=5Kc(Y_W1^v=%U$2BV=Ko*Y`#;gc(%<?8GlEX%?}k0`|F#}M{_){{NTs#@w}5A^7lj4%Q;rRz?{=IKbpKQ!{&#l1dhl1UO%Y%o=^R7q4mCb?R{TRzSF?{zK{@~(;(C42X}2skN3UfJyqXZA5?uWUe)(Le^q_&cu&>$)(2JJi&yo%&tFyF`}}%tXvF3RHkWkAcS^c%UWC7SG-C6EUsiSF@A=ZVZiIh+Fk<!p(ZoFt>|1<i{5XaW-x9I<BYWq?r$tNd^wp_YHe&OGTL!wXXJwf@->d^^6HaB?{6L`!?)p%s+D>2Jo^GCN_50R4ZSzCTe$TM^&V!eH^}W7T^*!IzZ`Nn0Z$6g%G}q<__pjo7$l#sveH$M4QLfd0Y`rx;t;6h0n;)#*Ej`}%J|9(m&sX)m&p}n+>wi_>`+QXOJzv%LJ_l8Oum7nZs<~#Tub<0)60!Qb)|~SB=KGG0H@=DAyw>&2dcO30#O6B-)>`A8l5?|cet6j9dFylZ%LA@&&a3ndM{Is@NcfaB{=qR>Hb14=n7sOFebRmJ%UQoSV)Fx4PPz5FzwPVu;0?2LZN78pmu#D#a;aga%?~YHpC0df$A_xEcRWD-z!UHL#xeNA%81Q(8b$M7f6BX;{OiW}X%U+r*!_q5erH{?EB@aNSMC$B`OY=BxbJtywY%c$IA1>zvH8J^mE6}~utc8k9nUl=mSyt;jn3zdSIRF<+&X4`SW!M=^MkeeyRWBqt6lN)+UZ>?V)FyThFasJ^-pG6{pPo%$NS#rpsMeE4yyXz`4Cm#^HqKCb5PayJ_l8O?|g`=@A=eEdwkxm_&yATj^tW>j)%1$E;~BY=0^vP_0{**c~#%@sUIGHaaVlbMpFx&wfVsTqfhyK=4nE_`P?TyW&b~2pLHhfmjY*Pe(<ZY*7#uhkt~}ZI9esIKLb~Oc71bP`tA=An;-mR-YKiUd3Bb}PkFDYTYu~o-}?%TyBM+g&f`nn^>*anzWwGrn-j75frodx@Ap#C-M)ERbz8*dhx4CxU;p~DyW__(e3j#W<p)3bB`-ehj+=dT0%fO1tUl|HGoV7A@11uVb6=Ltcdp&;9?vhU>((*r!>B;S>K|(4eqShGe|P-64lJk_vHDA!TjN8;zst1w&e-3M#rxhmpz3?Rs_&g&QuV!cM%DM$0af4gRekULlB(~mGt>{a@44GI-#LGxeee8<@<Z)k$+Y=_)Gq1qzSlphzSlq04>Yc`$JY;cHO;d5(N1fQ#rxiI;C0O-R{xgz*)~7;&A&5ke%fo_`RaSefvUdetNPw?psMd3H>&#HaiFU2`KrEm9H{Dh$BnAK_x*a<-w~^SEO^T1hcE8PviZ@ass8$A{VZ|qS*u^P-zlrVERtpO17F?b-~Z;gtHd|CHa~E9akkA5fBSl-wa((!>Arv0^yl^^5u307UGH;E{kvYBNf-U^*R0PSuRCk=&2e~w&vCf+gR^`4ee=1X>zm{G>#s&^e(>;%);bCG&F4j>qY<0$oO{*k2Y&y~TF2RR%<r4?y5F^pSpCMS?(xYl#rFEfm-R&ZW<AlqS+BHj)+^)d^-BAuey~by*H@n}2|nwy_RadNeX~9rUw^(N_^Q7Ce9^wHuRmWBd{tk6zG&a8zb<ue{5YD=>ja<A>y%I0xvx_l4`|;U4+L+1c(1SDINnI`&G((xJNn0$;~DLH$1{u4e09w6lJ>phrFVwz_04yV$Fy&b$3nSJ?Tw#z=6Fy0=6Ek{&Un{X$Di6a$Dav4$Di6a$DhGd(_CL2KWpC{KPUJcKWpC{KSvAC@a+e4Jg<FoJn#AH_+R_p@qe|C{qvgdBMCm=N3?Ig?`YqA-!Z=azLVfnKh)v&eZG0k_dD&I?|0fa-|rH9zTX*Ne?Qf}uCKqJCitqp{(h=`U0;7cP4KB7ZhxoyzSQ@9?VIoWX_KCCU#B{spnY>b!8z1@U;I2Z=PR^t&R2wg>$5L@9L@O<?VIx<X<MK5*WrAN_Rac}R%OvXU!QY6NBib{j&pIzzW6>g=Zmy&&KGIloR8AJIUi+weLhP2rhX{8VPE{bGw0K^Z_cMVJ-4~OI=`oVbAB%&p7VR!H|O`F?`68aIzOp>bAB?x=lrDh&H2etsgu5O@y?fO-<&TszCORIed43Rr2X;p+MFLw@Hs!MeRF<T`{w+x@%8!b1YgzH=eM=5>+AE|3BIbY&u?qr)KB}Xu=~E$?*-cTelMujcz=AKo8Kc6e14D6zWKdF`{wr!<Llo$5`5|hzv%4NF~>7=24~xR^E;0A&F?s&K99Qf)$c^w_kJge_VB$P^E*_6&+kwvC1(2T^E+39&+lB(6C3vX`k&v?v~PY#OKEUoe|-O&-|4h(ey590$nf>E`Q1?a=6Az{cz!q3zWLqI`1*HG?d$sbcTer>`ucZI?d$sbcTeqm^`FW1_cOmEC;0r1tbOx4wf4>L)W+ApQz!V;57o`}&r|a|yYkKN?185vuCIRg*S`7PU;E~Ff9;#!{hiI<yS}<^LHp*qg#@4L7PN1!TX3rX<m+>D9YuoAbrhbjuDeL^i4T{mc_43G%(^k`c(%<q*N14|TpyBh?(PG=e&G5O?VIaQv~R9&(Z0F9#rXRA7VYc$`uZI0d&kdb>-+0-{g3v|^*?Ei`yYs(@8)_W?VIb7v~R9Q(!O^+6288kO8dILzMe|^y1u@iO8dILzMe|^rhfFn5&m)H`ZVpE>(jJvu7A_Mx&F=g`uaER>-zfoJ?(qvTPBZmeRX}H_RaNyY2&8(U%$DoTlwB~;Q0Ew#L$){2YmCI>mjx8T@ShX(1G}QZLYV}zPa8q&?DRR)%Bm+H`jk^-(3HhP>1V3Q$F~Iub;i^SC#Kwzp8xi`c>t7*T>=~Tz{*4T|eRaTjlHe3D@5$U)N8#{#N;>esJNZ{&kh>oV9PRbJo7O&N({&OMl;T-L>}3b=Sd8U;F!+>$<gXuImm(e(=vDt{d0Bxo$jd?q%0k*Rdz~T*t0`a~-?(&2{YI;#YnBZ?3D?zPYa6^VN0u+Bfl`NtF-A_nUVgf%eUP1j_gBBT&9~p8|fueGuAL^%L%cP`<98a36&BRsDqfAe3+FJHOXB=<7G`E788WuOwVI^`NicxNk-K=DwBCn1=rSY}P~NoAuN9`o0_O>v(<NjrL7^_^!6T*J<LNuX`T!^_#iRNc-Gply<T2!T9-W?r+k*xxY#K=KiL%F9-Sdv$@|&`{sVD;L33a<L9ZlpG*7Zey;H2FC2`Y7vA-g$~X6m1v<ax`s)6*1fToYv~TWT)4sWXE!1+4Z$EhV@hRWjXQzF0pPkd<pntz{-=Fr){e#*!|E~7UeS*RCEZ0}}IcneB=cs*ipQHB8eU8zjQ~vSdzDw<!`z}M_Grm4F_jPLD+}G*(>ON5IoA~IFw|)EByN^}*-hHWu-}mn~6TkN>|NAocai{+5d!62WwaPd5)jESp9P*7L_w6S5+_xL-lXA${=iC>peRE%MT8~<XY_C7<<JyPf`_|mooZxd`v-Zt>%?UpDH9I%9J>(lN?z7guxz9S(YQQ01zj5EU_RW3Y+Bf%oYv0`W9d0qy|L<~ty7s;MYm{&9Tlai*pS$)=ypuG==bQWP6MXKw4<4B3-~ap_0PUN<1E78LcL20+{tkdsXSu(BOyB;n)&KAQFTQtQ(#4bh@#60)Xy5!@1?`)^tDt@JcNL;<obitrf9FB_roQK^zYC##6CdpMjsNwVzdxXS?>^SYzqj^@=g05Q4!*zov1ZI0bpsE^o{BxLaY{M^ddL0A4>9FGqxL`fG5Fs9t3UZs`<{Ar{{Q~wN0D)|>!e-K3Gfd|j`MNsadWb(|AE^O^B~$CmggkqQM6jJ%MTJ$6YT`ca}pCo+rTx6X^8fKgT%~12f+=AX^T#T=Mb|3eHyMR|3>WbXOgQ9Tr&136MF>EW^kj}qiO7MBU&1k9LfC$`e~BO0dgNfABS%w_n(fd|8iWG9Le2^?t~v9cN#himK@2=LQlh6$$cK32~Q(;8@db5BKLK4CHy?OozchOZRCE8M&Z}Voq$e(KPKisXcB!fg+7=-Y#Q7DAx3&Z^e(tNF`dvy;A+IQK_7-Y5z_<h4Ywg?5c(wCgP4ivv+y8do<_&R6Ny=dhTx}(8Hf&rml1OkJp&IUrZw6gK1s~i=q0!{F;&r;@Ylph|B9BOm)r6_o<^6!(i?jjThW(b>5bWpt>`{jdLzQvimriYlKU9?1iXvfDEcM5lH4iib8wUx8FSGBjQ<p3($IdeJXe4*7rh5gBjyqGQTQ%m9!5LEj}X%v?GHap%#-LyxHmD+qR+!m5;Gp12tP|q2z>({Ps~ts1RNsf40;wGN=$pS6MTl4OX!bqdtz#$wc$&|NPmdl%sTfNW7iaI0oNqgLG#0sb2Dq3XiK;$xuwzautTn_ZK7YW&NU<VakM*Jnp|1iM1OExmYgqG+rFT8caqbc{_Rfh&SK4y_tpq)3QNzlpch16gr#S$qZdSr!S@i;8QlawN=$$Bdbl$&BhiC!e`20TZ-qw^GZ8%sKTpgXXcKrMF(c3e@EgROMQ6ezi0OoGglEzZXNf(;b|+$Lqc6Ze5+h?S`X?+s(~B_|tqIpAH$U1OmK@1#iQdKdw;;DX`Um6RoSw-~jqBN#oVyrv(KNU`xzabH2Vu#P+`VXo9_mi+Y;*;DkoE2dYRq6;aw4pGqRZjg<nBYy!Vz-UppD^|$bACs1@9yGOSA;*;u><FLsQ@{iIKi8K~D?+i`RY{jlj}l>GY21DOh@}JiQ}Y2R=&70rVK$gqWG=F!%s58_})sOkxh9`{0elynrr%4-xYx`fs=|{UQ5HxGLK(klP&X1^-E|^oVFR`lTkh(j%h3(l5=)y&f$IOHMU<M6@3)Ils~)qI==%$(0@veV2YoBX<S58a_zw4D?CUb4hOQa&#5Eg50y{Id}%SjnVty<>dB4`@(0*mEI98MISXLHw7&R%X6jZGto3Sg_!Hm!f*>>UPKqd*AY_;O@?12W)r#%E=J7t=r!;rVh*C|@N>N0e&}_u^jJlDM6@t0J(f(5h^D}@p9az^qHW*><n}_pNpe|oQs@!Uws2K)rAI_7!oA2XiDtpo$nA#?f+a_C_o7L#<Ydt!q8s6U<gP}iz>*`mPokgFFYl7O3Y`qECifh=36`8s=@HRm@G5fqq66V`<Vx>|o`mlsw;cK=EYC?y8u~3<j+nyeLRg-Yn1$#y^ig4AlF_+_liiqYXbPN6%r)pDcpEY4XdU<(V#=eN;dEk7p^f13#MD94;ZwvML+^v@5Hk#o!pDf&idKZL=k?x-mWQQhZl`ZV3&7Gdrx|n6w_xd+VT`%xb8r&5GUlRRF#a3Kos3R}r;xh|-2zL_7mT@R20WSEf#{R)CUQ@rXW(PxzKL#yPZIMj`aS$6F$>Wp@VCTBFNhYWFBTFr7oBJNBiW5fK`X&?iCKg$g;R*BgVu)^5wjWHX8MDeMrdPrGcoCCCftaa`_OuDIx$i7OZYxwDx$Z;QDS5*6fKzKaz$baqs3r(t{`ikXeD?cW7h_K7%oh%ta+l}CApkJZd<ei+=kqW=<TrNd`JI&NAC&`<NfVJ<@E{IC4VUTBwUo5b<v06kLd5B^!x4bdiwPvv;eUq>A&^p7jO&uY$Tcir_xU?(5-NF`X&`!0^du2R7dB*E$M@M(WUSx#=9lD4c@@`jzTlx^NjTd^h;ukF&^@KCB|6ze#WR6S_vM`dT~G60ba!XAC3-#)0xkU(C6SQ%-eKy3w$T@^9u9z4BV4>cqjTju``%&J<;Ou66Vzmv=Y3E`LhJA55LAdS%o%+r!ya3L+imk==165?Qj)(z6V;2*k9;jdHys#EqpA=T~B{OPs0n7-1YGo`W8Ht-d>1Kh3m)0tYhra)p5B7+v8&Y#;dVMcXS#&CiYxw;#-p=JURAUDA~;mkt6(+<L12TxZIlUr((~&lI-TaLXL1a_S`1oH<2U!MC`felij@M$q~L7d+uY$&HI=f;Rj>Sbxn5jx{@P&L+m|Yo8;z+N{;Y@F|HSTOhli7uZ`tYPIl{6rj~F+*>_29z53J?E)jbaPjc%Or<U+PV~?MyCn~jsC&hStl3Q;)wS@oSxV64=TrN)SgR#d^>K&z~@VwY#L6Tc<0kwqXH;IjoTW2G+gkO$5H=la*sU>_U_6SoiOfBJ8VmV_Sx87K42~T8Sy^PL>zm7dFQ|~ghgh$76S~+gLR@4%{F19c3NOto?FH__3*mLz9H?JN!!VP0F-ICqBZsZDgq=z3z>%mX+`tC#P!S}(}pvB>9;1AgMvfn=7Av_=52+xPRp=050a09dz+yJhE)`P3SmCzb+CHPLXK71$q0NNUU0Db~}3Vs4!fNp{pz#pO?!ym#$m@CrfMR*9;LF>bH;0fq>cmn(yx&VF+K7oee6Y#I-W%yV40eVEn{Q(}rW6^H#Sa?1<4W19LMPG&2!W+;Kya9d#eFc64o`*gU&x6OHUEwis1GF;S0KUrFAoKbv58>nJQTRB#7@ZF<hMz{Cfn{9oVcbL=So-{L$DIeFwV4z0@BW_TzAn*byvC=fCFA)NwdycW-gVr1qJP8kI&-L(L(Qv<`!eb*qn7ZC%rTiyFH%#sU#FJ5zt^dCoIc5=UM{tSW!^nRorkC;JeC@=PsUPfF@5z1_5PriaAoGO%-71)l5Od?hmzeq(Lbmm^Y=#LZzLyg?#E(g(WkS>6~2}^FZ26aa%6iwy(@jXo*daONvzEKlH|y?^zDA)_md+m>%bkv-$9P>5qe$v`Up9)E$c&b){o}o2=60S`h6ccvi%ZkimV?mkt5sE|LcffM~<+pC+CPiM~<+}i<!)undAr;p;skO^c-uF^k{9yu{L8V+@1N{5bXw!A*Kpi8?FLhq4%Y4ukaAwjlK)-hKHap!b9NN=tFRAxHMWBE)5q%Z-fiNN$9n35?lx^2^WIPpm)G!;Cs;K@ICNQ^d)#Gyazo8?}4wP@<Oh%Eqo_0?jHC~cpUl^JPzJ~E`v9~=h0mFJX}86)j#0!%(Vfi%%cH3gqNeU;N|dMbUnNmK8fy!Pr_%=Bk&nG3*852!F$kk@E&*>Iul+7_eYz-{o!(`tdr%~7XFB}GY9?%UXQ*GuZPE=V`2FYRyfK1&Lw&;EZ=EUlicsHqJ`il$?o?F`K}@S?<9BoesYJSqu`?C%6DGT_Z*icM{<v$8Srp&7okgG$&uXk=xq2HxeL)H@FH^4(M)(fxg*hs;f3T5MMuKv<X%C4gGZ9v0<8*PAx6GSiZ)Glxdkz)=q<23Cow(IXW>+0s-tD$p2W;R*TB_@xfiVn&md+Ax&^+Mn3iZYcnLA9&|Pp#Vn(4IV0r#EVuasfdlWGn&^hpH#7sw5!}9!jVuaskdpa>a&?)eFVx)gX3)9O(8N0e@DlF%Q<lMp_bQoNjm=Wkm_%i)knf^_MchY~C(L%%yqMvr6@4>a`k3r~cxD<U*3w;>Q&v=(YtHKWBnjgIdF2MLXXj%9s#;E{W5x$%8xCyNW4`#pLjdp-{v7ZN{bKqat=eyANiM@mQFVEl0nj$=!`Fsa@FT9TVIT{@Wf5?1Whc1Q7GOs>lo@K)Qm_KFF--vykdD0JU3h!n<ypBE#XVUk((KYaC`a2Wd0%y?2r_o*TPWm+ieG6Vn5AQ@*!+lv#m!ebPGOV$E(I&)xz<MXoXRw9}uVwxE0L_3$(A#U#C9r&^$T3y}K3`_CEuRfl$g4u{8<u0B%IIad2d}vb+60!E-Nfx?P8c4-_7LWT;o5B1W=<F`&30+#gyDj07i3NtPGUQWIbpaE+l81DhRd*BhB;yQ9=7jcP8c4__E6@8;XQ2cVNMvn%Jx;}kKsF+BX=?<43A@b9CO0(2DUdaCk&rw`#f{PupAqGh?b4x0c;OoP8eR!_HyQg;k|6{Wlk7A$@WR+gyA!6pJ7fI&SE=@IbnDY+k2Q3hL^Fuj5%SrKimD86NbyNU5@!<_#@`XN6ZPs>)Bq<oG?6w?J@Me@XA=uGqJ~9bTB+VHfAegj~!?>JeQcMXj^y(F&EHp;i<$thE|6!5OaN!t2ZUN+%fj(5_>d28^e#0TLJwm$z{oVfL!4wY)jsC<O-K!y8^jCCb{|v`~bO~&`06x$o<4|^&7|KAIUw8ZihRO`zksEmK@35j-G-Klluxf9hST!<O=U#dpo($pv&P`$nA)Bfsc^;6M6xDhTL}OB={#{Zb^3aZ@3*XjnJO3JSQ=aqcxIUZbZyoXlGcSlbGkwcJN)q1khgabHu!i4uJ#2v_~hyFB7v8eFm1Esm0ifCd1M*<rs6(=CJh4LyWy>Sy*x;_Y?Fp#=i-<kD}e+Qsl~*i+;!WOU`GEx#({AQF3RXFT#@Z9b+z<V|s|(>F5ja403m%d*D;#E=O0v)5-0Ec7=D4djb6%UQX^LGzecH=5I6~eKCoco@gKVZ(^huMDK=s64M#&0@om>9oiA@OiVAdFWiopA?R?p7crC3sqheDo<S$TlZjb@u7;l>W-vMoUO`MYnhOsmrY+h5&L-wt^n181G1bvp@VCTB|B9BQm)r9`#-l4>>5cu2t>_$BdSfnQD|!Hy-guj_6<rIzKyFvG2fT;e&(VwUDsqG9H28C3WXweiG5$ef`k(_~d9Dy+E_yHAhnOztWANR?bVR$rU5M$64um@rGaMZa_a$a3IvpNP%mj22Je8Q$=sI`;F~iVN@M>am(Rbis#B@L(fpdxZ9{m~aKuj$(75<(W=?~FcSm(Mjb`PPg;9BG+qXl8fxrMb&v^D$?xn<D`a5A~FwuyelI@g@sZfH-qEV;6_iT>ocEID7XwtYqK?k1-v{o9k?eUUXw-dkhzAy|5*6}=!j8<w6aK`)3Fhwmk(3%VJ8jF^Gw4R9A?Mx%$}fy7KlZ-++{GYJjD(}`J!HiIV-GYUNfuOsFi^aXenF^`~c!tW6CGkOGmgqT$HCHQAzWXwhXf~9AAGv=bT;8b!8qAg*`k=)kk-Hd-Lax0+!Vf+h{D`PHt11vdrGv=aw;0okQ--sTDB}a1iqi@qgJ;|MmhTy}jcRx{M7Tc2ZHfx^fN_Z~02hexmx5-_LHihSq+XL+lA0YQ4dL!%NT5_kMx4}2E4qha-72DtO+H=siVd=3G^p0pYEIn3%-VwbY4ij?-Jq|Y`<^^;Fe2ADg(e3aH#2i5nz;6=s61oUJLd;+2@38Er{`81wb@(N6TcW+;zsQvy5v@VL)FM}UMD#cMr6svHpf|xa=nu&i9>BKb{6>$6?uTz6S9(PBJ^G~&xgqoo_%OM%(BY=%lHA;t=o&ag?mOuF@GNqhqIKbw<n~7U!|#wQy(3yW+2y9>-iF=`%X6jaGtoZqZN!v7i@>djnT;-nOAu2W%?HmWW;412E>6r1Xi<1GF^AC;@HAfU0JH=wJ$5TSB3cBN9?MUUh~5Uvei}@#h_-_lk=q;nSCY$;a~nM(+8(Y>uJnlLt#EI0Z$eMOHOL)+4uK^{a`&V8V97Z}kBGhr4<PpqGzd$M<PJwaqhH=5cMbY1{06!2qnlyL`HUVBJr1uSw?8@<exF?F9noyKF1a_OZ^81M#PmTg!8a3A1YHcva}u){ElM91AtoRCvf*SmW(Rs3oR65I=xgu}Vosp<!$payfNp_L5R;7t;0natkDh?Di8+qeh3_Y31o}DLp-ob9$$bBF^Yw+Pm8<WIO<s8vbN=T)88gQj*MIcb!Q73lGyS)1$7f!R)$(rQ?$D-yoP%_dWB<#KA)}_s*8c$zI3Fw'

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
