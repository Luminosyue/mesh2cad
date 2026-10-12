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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_003.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_003.stl', 'source_sha256': 'e3c471e3cfe24f0416fe6c8e63a75f002f0c8539b0ff54e267b901e55e6927b5', 'input_faces': 1104, 'input_vertices': 615, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3001576066017151, -0.4326651692390442, -0.08064356446266174], [-0.009537573903799057, -0.04973211884498596, 0.04145466163754463]]}
GEOMETRY_BASE85 = 'c$}qu1(Xz5&~ESIZVLnn4DRlh9o*d(0_@-#Jh(K@q8r>9bdlihgA)i4++hL)hX6qWB;j?{_chG+|K2(8ytg@Z>Z|WoSKq$g_x6N(HDkmKG4PkkXm;oBshp(^LnNUQV)Sd@yKm>V?fc~K-g97(kyLs4v-R{kjceCy7G(4@2IpwkzE9iUIZC^7l<iP5M_yNs4n2DJ?cKV2c#q!g+6!N$b+<n4Exu2u);-%>cFy93isf|`$(7eN)b;=P7vIW)`$Vw|2P7|1V|Iu(?@Wsj?f*4Ic{5hN?W*J6>o3|JeCWLTAN;sU{jOe{E!s10Hu&cedsR=)wO;)n&rsf+{dS|;xrauI_D=i>{#mnZ*7U~V{Y3l5P6hw=+yUil4p^&p_c4f*CQS3=8Tj8i<yQ}afAFgf8vjGsD2?B{9sDOoX@1NR-IX^te-HnVSX)*1z1>0i*A2k8?5xjaoT=9%RN_p{4L*HsEgvJ_etnKF{NaWAoW|AvT8Y1ZaAxIwy`TCtpFbpDt@+B35&j)E>{H$I$sqOnlob4-v04ts$MT&ej%UxibDFQwO^~0EmlK6|Rer3zv3Ul{`I|9%f8W(R@ZWf7kJ`hUj1=wiU4noA_;}v+mwRh^3i3wA4S0@<i2v>c_}}BKQGI{S1of{D-j{9RLFJSCmg#dnJcRpZ?Tq|)E-_Z)6xt8IcaPn8zKUU5K7)3FuhCn}$CbFN-pAc?9r$a@QC~$KjMMUu`7`+NGH53+)1dsx8)YA8{>@D@f7bGDxElV)x9juzUMJS_^SxaGesIP8Xcv`7X*pL1?^`iZpUa(pV3gV~mmz-Pk0^(JciO6d!~*7LIiA;ZI-BsmJaggS<h9nfInO;y^ZDZp@HOiC(7uZ=*7R)?!I$i%aeNso&DQ7L7=ieY7NgwW{N7G@qv2Tauj*<3-6eJ|)%XvFu-ryyxw%@6RNhl;5aKVJyC3~>aBIEK`M&T^K2qC>QEGB0wL5eL|IaPWr+Y*>eGXruE{L;f))wVc{Q8sD@3v0hi=IZm{upbH)^A+!=AqRnpF5!gg*Run0PkO^{n}`rPvd(YGz0%vW%T!1;Y&pOM>RtHPph<E%~JWbeHt4p!rxs-pUZb^>`L`p8H##L)?4e*mF4Lo)l163zwbCaZ=5S_19@XZaq#6fX?t)lC<A_Jd@Tp#ZqHSEeZ|tsyR(b|-}A49YELTx{|YY6zo%Y`73e=j;s5z9+EtQOS}#VXyvR?#6k1>IGnF;I=R|JANtIp42XmC!I~reaGx|lup$XdFdgMZ!bOZIiuI}-)+}v?9qa2do(EEC(bkOqgZg9bW^F;KE6s_lJy}U_-_}Mm~zCufn*YcnL4fr;5wcd?YziEGTS4<6l#}c%w&Hd{i2;lAZX~rF(<AC`jCHM*zQNMLhFIWHXz<(KUKe@YUev2kU{x7A_{F{~fY5DkWB!U0k+S(sIt&UF8=N^?9e3yb~SGgwrsO|7v0^IlGSdDKk8)B-?2HrO%o7SVZ%g3ld-pn!+{ch*mZd%UCVj%vK`P)=i>@ri^|E?hL?;|lk{e7~umRp54zp352Ao|OIlJm73X8i^JX)m<5quI1Sdi*cI|Cti=Lc(FaG=JlsD{np=hVr@2`DN&1@E7|cpY>koeBnL!2>gmES`OYH4tw?ft_O(!ByO~J?&@(5{Ehu+4^t0oKlUBE3;uMN#_>fA(fTrz`N1Fl4sqrc?WplRx4=Iij(Mc#OC85tD=sVVzCBUP**~+8_7~sZm*BrB4g8bhdA$|RA^)Gg!*f+x*;3ovPiNr2E(G&^@TcKgFGWrv{?dGyN18-vJ-SjIfdA`0(b}gg**?TidI9l!HSQhA8?D}=oI5?$`PAIG2mGxqTJP=}-$rWrhwlcz=|9Z-kq@-Lc(?3A{B-@a-TJ>jf$<@D2mFJkVZLsFb<P)lXg`dD;Wc%>Fq&*<d3Hd5uT>uXefbu|_j}Nf>Xg@d`NCI;q4j64L%c86ga2u)`n#LW(f06#f7}QCJzJ(>TFw>7-${+}bJs;JPn$Q2zu2X^R?%9jXRU*O(+avSa<?C?<DU2N&+tFAc{ln~lMxc%n6#SZ`2pqGE|K;NPyUsNV+QTi=Q&?M`?vqna`^9PpzA$f_3S#oc(X2r|Hi*j&L3XtxaUi|2>$7sU_3mM2j!D;0oqB|n;1`0t<ik?lFozw&WC6xn<DyZyWKel@dy2j{<!PZm}vaMTWJ5uD-O};Z9E<P>#CYhqw&xg`dq80;l2;Eqy6VAf^lYfB<?%xd-Sh&)3jb(e@#Z5&WV)wKP|Hy{WSvq^~PX*+oyt#H{Qtc@b`5?dya$kxo_fF_-{{%=Q@mW#^%5DuO`U{ga-Qex`+CmT&i=lI18#`eYrBrbiIGp;drj8UG=%lA8str_M3Jv{PVxX_`mm_K9}#{K=$8~Xm8)0)q3~s?GN6be>cw`s&T{nD({P#6!YxzZ?)Wv)ji<9q%g+e!SxnsoPWCGxr)9-`@eWl+na0o5AfeS0prZPU$p<a7I%#{KDZaQMmaz3fH>7Jpd1e6@o0N1+kxZrW2~PK=F$G>j%*J;;u7-zrWV${*FA{yW<BPkv~e~6-u~Z%&s#<B>;14s+pXtRbMUd^<2{S(C?g~Jh6nX|&3f0SX}dZWhVsAj2IJnZeK79Ts|o+aw~_xe=e6G5HLD|^?wnYE?)|hNkhkY+qXFiTFMQo@7=NP53{?N}m2uy3rO=P=*IyXOo3C%8JR9x6dMvU6_=yL#+}y!+Q17=xk)O#;u+Ew1*7`CFlYi6<?en{$I!>B7%OFneMq1A1v18g!j8i4xpZ6BxwCRTao~9W1LD!Y{XP&I<E?-Cy#5t6X^I$C<_dM(JfX}s8^J#Ma@;1s1{?CLMuky^FuJ!UyPL#v2MOqHNV-+!;)XmB9c@)Oyk8ySV>93I;Jl{KvP(#bdUpXuI|2AkG@40zczdg^4_$4;t{c(9)wEq$r;J;~?t}9Hw5BkkC;Qu{{_lW$Vx;`;4egl4BFN|aEt}gW-oErSx7AWURQ`)P4lEf&tArYES|CzGde?86OMQaa6wibP~9^b`4J_oy_<<q_Que0jE<T&bO_EU_{&0c`-eFE)p-#BeQMwJK38{@m7Uc#yu)Oxw+2hZ``y(1X$b6$@Y-?tzg){|||o(=3@{u3$D4s-4RzcV+=d14*Z*WG!_`#R^t`h5R3ymwrkrM$ha@Fel!J;E4`{A@3Y@h#D1)K`vP;4A!#`Yk*j<<_PH_}GiVA4fYe!`k4!V<uqz89W?(L__#5D+vGpX6XC1D@7IXyJn#r{+x^auPlo=+XtgOi{;gJ?mm(Y{!O~09X`5+_rdJ-w7lHcJ6_iG38^OP{j<eKJ%wbxs`~HLx}W3g8wdQqGk?+R)=kp)R`0l#+75g%N1o6)Z_0E*znYKtnb=iND?c0Wzy3=m{D*x!s`it&`dsGNa`4Yo=2!Lq{SM~en%UsL?DY{%f4L9)QN=%M`*0tcb5Z?2&C>S;Z}BV2`#r_3>2-r+YrFCv7=?Y1<4^It4U&xy4dkEQyQJkicdF*cd%iOGddsvNj45lwLj!pCRqqu|Z<JEsM_lJ`qW^e?V!rycbDWlQ!b#xgq2CzU_UL<)>wcK>zCV)aeckDMP7mabnwj;vJd3^aG(YdlVf{3GjXsyz>5l<{yfN#5=F`{hKK7U1zt?f!cX&7UXI{V8_HW+%Q+YGq)RP+j$_jm-_Md$SK2A-H=ic#iHN8+2_#uO?>vO*6`l{Ok<=st7ozeJr7GXW}ZVKj`V~>uhUyRH;5Bs||QQj3+6Yo`RvEOB!DTz47e(XC|dfQz4d)K7Odv`tLI<&ivZ@!8K`1{8-KgNec+Mdn0k9580&b{!s>c|ILo}Lv8lsAJ~o>KoIM|9qC`+ovoEVZ^P^Vs^48ozNf<vshZYkbe4>OUO_;JsziD(~xob(d>s6|7UY{(<_9+KF{er@yfdE|FI2(dQqe`LTK5k8SjM-6hlO{-<ZhTkv&{9@4nn*YdqOuDqv9rW<Of&ORfM_qXb<`Eft!t@-iiorgGC;$R=qEZai$_Rh%9<^~x59yVR9<*>9h;ve0IddcLPqI_s6#7XAT`+6R3(0<`>kOBL`RhJ-s|Bl*^d`r?HKev`6&XES%e#|_Hao@|u(XOt%!n!WcQ>^3tcMzx62kZ~TxPf)g&Is(+nuSMezqol4>**7hz)#Jm_2u<$R^Ih@OYjlN@m{uNw({P%wX~laSr0CX#(y5E{m#7n6#GfXhaf+-3t*o+Gs?lYrLXet#&@s}#(g9&d81S?#+fP&be;c&e_0;m!(=b^Cxd(AzI{JnKR7hAuHS6l7*GrOe=}Fxxmm6w$|3SS=7peA80QDHfd8K}&@cA?i04Y#6!~A-5dCOQr7qh3bCtz?4|mdfG;4N3zb5ZWcoqG6^;&(;@-EJfI5%#gUM{}V_Z{D{6yQUGz;7H-S^ZNc1HW%Qo@>oEU2lBhgIB@dlNIA$yTss=mqtEMW1rdo+(0?U&Y=G86=Sr&c-ubJ^_FLM2aL}xb1V(y-6v0K9BWqA@^J?}!1{R1G3>|0m>Hq%x$F)2m&CZ?b6vpvNZuP|U_7~edvu_`D{U7YSG^t6>wbW@?FqzBTV3<%+LS@Z2iNAK;Gd_!^G?dG`=Z`!n-M=_chql>t&_Dp+l<6}OTjEWZ;3TY`Gx&)-)GanXDc~1kaxGnIgGomq5Jvn2|aM%@b)~%*r)Fco=q*l$K8te;%XkeM?cN4ys!OVsINBFw7>XD=SBRy!%=SLO?{s-Qlv+mDkYKso0s*uJfBm5KYO3&68&dsyIqhN&wD&b+nf8x8ajX3yzifhXm6dz>bz;xd4c_=>a$RfJ$%}J{G}e?J>f_=`s20Zc;CO`$GZI7c0BLU0@DL|-^sh!XDygR`=fio3Gm!M^hTA@@zX4I81HZUF}@k4EB+9TFLP1*wRcK9oELaDBF^aMm@n3*!aAyyS9x#w;>b_G3%Wk>U7iR2zr?7=^s%%&z1ij<zA+!q)%4Z$XnZ)%h1|=6F;DfKiE=m)Pw(q`b9KJj8zw04x!wZngs^hn&;Z_@JtOWLH@&WZyoY)y?`qu^&-*jpn{3_;$%lDl$^*PNKWTydKgM~Q+vP>S?o$`#!1=`;uO-I4k|n@j%cb+Ie_BVJ&txrt{Ind5=dE}Q^I&*Z@Y{JF^5i=93IEN2d=}k{_{BUrz8NJ$;D2L?&hOqo;<8>7Bmdw2rt1*zt4aEP?<?^N`_#?0BEH>z#=cPAQ?Lr!+aGJt-Y%ZNd(<ABNBJ(y*7oenat!>`<y!tmgFi41&)tal4`L$Df+`x{{b(KbdBZCp|Njo09gR<Y^svT@+J^F(I~noQ_>s@)gSDObA5Ku-RcWEtmn&xVDF*_0-^68FU;fFb^?6-M1|Ux7&Kz&g==^T;uFu)gPt(kZ3iP-0<KO#Q`-R8Xl<$+bQ4YnLYB{(+)dD~3AmYa?uIB~b(dkj1QB!y>F}A7d3u%=1w>*gQIl2J*805`A|3LX%H>PQR<^+Ln*bQ-Fb=7ks&*%?YPVP>(l=qLChI5mT_rNzBh4s?W*t#F=oqZecy*Kh=y_EdjPl3FDMr$oMbKXXs_kE)-EAJ_h1mj^ul;+dSbPn-@vTA!XGhfs4^t3nzzUnaKKeDa%Q*X8XsLvkDv^?E!_F>=e{6_dsc!2eG(zVO9eqHO~|4$l?<LR1N`>(IZTI9dsRFwbCu3FBn^OKc#&Ao>4KQs@@-!&2bDVCvs-OI5skoWYOkMexh0rSF|p~z2Vo|n?!<LU%{XfM?7z{@&r`}Va#J}Y0xcyc7E#`(g(taAbFG&%A=vIh3`_B_}A=!sajT=Va$41N*Mb)V)Op>~f7$bT=M4||Ske=$eqKz`iYaNonDmG@`N48HMqsIQ&7uy5QwBl5HV4fyx*mS{Pw4nh1z=P_<itB3QW5i!AU8-jAH_uX7=pWXk#zJHs#$WJiV5B|L$zz_L@?HvA|=5KJGl)tmC$NUE;X#KiZzrwt6c?jOWdSbuDTjiPZp8Jha&cE-~erFW9ue@t_Njz_X<@#K%=I0Q<?gg}maP({cjAO`;f3C*ycQ^HU{ms@Z?~eNt^YyC2sNYp<;h%ab`g^J_+AsWP=YStS9Q#*`I_mp~`-kbc@9383cYnM?dB&dte&Gbnv(1ugd~?qaSRZAGh37gIhW)*$_Tc|r0e;jQw9mWEQ9eidBTj7W2bzV#kpJdx<UgZF?`uX?fd4N8Q7;LG;koXXK>qLjf_gcYQ|rZhrhxMPN;p3^UJO&-9hDLJdA0`SS$Z7$#hHZguZi~vW6gezZ%lu)F|Z%`xZd`rf2h1U_m%RV3>UTi8}aU7{(M*#?XB__ybs3Ri*xa2R}g1%O`Nw@+ywvT-|~G8>n@x3_4DC*bB5}77v`{0c%Rt51AO{my{~_$2XV^2KzZI7g?_Q3HsU<MdALyr=T@$rNs#}s@pK=?&2v>_)P9^R{IU__XRKex2J*(sL0CULEz}{9_ctjE|KrCeNAqt`8vakFH4Y8ny|E*)4)1VzW1zq1hx%BD)GfL`8ehW&K1M`jU>x_g5aqp{lWh+4cSY^Sds&65(RgEWR_vd2!FiL-oBeC(I^RERMKpi+wjTN(=c##SX`sKcAfxi;idxa*w;ZeQDc*^tRz%C^=WykX6M3UOuW{%{UB7vYFN+r6SLi&(rPKGL=QGDzjQ^+4MXN94X>8>^cmMJR@@9{Vcu$FHI8*sVQxM;Ljd5le_Csvm$oUHVz!`G`dHX%f%=u_eAn*CK2lM;GQ;VYcKa512yp!fd<1e&V-fQ<4^8RTx5#N6AAa7QS5C1iLmPE_vO#}Wt8%MvdYb)mEUcX1@J!_Tso=>(kkaz9tgnl>LjOK6tRvY8$tjp2vYwpGOTxQ{F3j=vyqrWjuW=I>||Joz;JFXMH+_&yV^xv#lSA6k*w;ujwQ$#C&SMgEszi}rTZ*1=c|FE$*|LR^F&pR**>&#bqbbaM(o*8ipjevjlVhzOKKiq?U<`_53J&keh-MzHNF}AGJ^_6FMTIHSNk8j#%P4_i@kNGZ9Asq+YZ};Pz-Z8%UyR25;IUaiBF2{Y&9z=c`uG4*K^Vd#@Q=u8=_rh<{o+~y~-Z>6?nv_Hw$GC0YiKD!8ocHCstLs7MykMTX3I1t$Ja4aGbzjI;{y5f;*ZZP><!`R%XvUp`*iUuLJKi0ely}Zk{-tBV@7Rj>i+s;@pVpnGm-5be(7nAY?(3L0eR-Q8pN@Ifv(ydVF)w?jq{R1eS@8buOEO6J_iWx6jPJ;NyDFnUc8rC6GRM5{8T3T=9ev+j(sttQ9gOpW6GxPHu0woV=i>XAPCKxl|2`eo{S9V-cdTbzCx$8ST>sd-k)i<exf0(^rD}$KS;soc?ac{)$NJ56<6H1sr(&I-cm>`+2YiF)a;y(+-kj2!>yTpT?~Cv1{)%(`=_`8+-!nSat6%tccd>uous!DW{^!9v*1evTr<M0@E_(|7BLT{7(E{*}^|PyOYw)c<p+Bw}Utf8n1@h@w&wt^a>-jSE5hrm^tY`WR*LLE&S`*(vHrkBxulVg4&G)l{$p4KF+8%sGi(%jChzq>qy~F!CCHU$Y(f)mlb$``eCIRm2c(1W}=X=c;|Ht?)z+a5>X+J}G=X;Y;`Y683bi9Aryz~9bSBkvjz0&5L@0I3{yOno+gYOp2qT8{LdUyuTXB_X3M)Dr`?#J;S>fg{A_f64J-*f#5Qs}tn@>Iut9q-pR?|i>D*JnYTyZ>r?bJg<ddx~r9IDF6Oc(3<;>IL4h4`9yiro6k_cGPdmFx|&?mFS3bFvos{%{%uiyqU`??`<;^^*Cm5PmTL25AN&S$0(i&>z%eA^gY_Yzqi(}Sv@xV6Zb)!oJ)Vu_VCaE@7PyyjroN0^XtXY-`_UCJpS`hoF_Z>ZH($Z_&fG_JS|oz?_t08)~c%SP5$#!aSrC#NAmQj1b@fAlPggu;yd=KTx&{!KVAm=3FZ3gzLTfw3!Gyo_*L73FKd52hjov<r@V9D%vbm@<`c*Mn``wt#5sxYmwjRQPRSgx5OEy)gf{QoCv+Dcs{H@h4_ws|-<dl04?X0a`<6EE+_!X1e~0g99s9Ijc*j1itI#X(j(t?)>{IZLeOH@z?$f#|MdCc6NJGr;cdKc?^A~6jf5-l|%{%wEU8lowp6}SNwt44%wGp>5?(5w5_E&<xbDw<Z2Yip|*oXHuehl8RZ|_@v7~jP>_WwPnCM)kecd&Wqxr6z-Dfm}d=h)+wt5XHs*LfbXJw3jwa-4VAynAdy_%Dn7qh9~=6n;<OJg=E@4CnLC^BVHb^BQ;FgZRFn#yONv+0LexbI0w7<2aWwLsw!Q<T!7#dFOeP@1_^?;nE1~&u^cM{eo?gxUb_p$X~y*@<!X8=<m%N;kzJjM#OiVf4R5DM1042nTx#hT+im6=X##{pYh$3<DBjb?>wg~cM-hfJkfRI40y-+pnuVH?8`dNL%;Bj^H9&C+W5VK<9zlD?>L`z^)H7wj&o9fNJ;oR&Q*=gh4Ed$jQJQR_s7xoiSJns<lk}5>-~HT-!&YM!a07fzS!R@y;phX`Lg@SMCG05(Z0T2m3N+B8`*0jzT>>x=W*k^zuEub`>CueP=8l)<9nhiDG}!s&dtpyNf5_zF7NAeN8kJZ$GLp?R_s5OIfeFr3g0;x3I5P|!}(o-%{#v<a2LpedB*WQgUvg?XYj5}gx|IFH}So}<_MH$ljqvreb3YB{A=twf&I{Y36wX6cf&bO&wsFP9JE;H0q6G^Ht+l%!+)X(zAL|bMAr$v+}!6XHx1u8jt<d&>KndE$7lc5-8fI1(;n~dsq*Ukrl-sx<qdBgyw{lcj>tR`LwV=-C%*sw)_K6)vIf?%wecOD|MF7oqkrJ<1K#!+tmQv16Z{?Dz4((P#Cd71NL}ZfVexS8)*=MoQ>;0Mb;~A0zdQ9-X*ox2=l3~(CDiY&oZk!Cyz_e@v-5kM-^?cbKKie-`hBlCc$V_c@04ub`JIxl!B(8FM&kQN;~9Q8XCAzZ^|Ir8Dw}tHPvt%THWK|Y`uAF2c*plzzBP*@@w{$)ceHXa>i0$6sj3~{gPHY{C~t;O!S`ud`m-I^)^)47yrk}n8a<!j`Ja_g-ub<mKTCxE?!>*}wtg4qeL6ztGjFeNl{W{C#P@9T-t^G??iqpe;q52!y<GjFu%9f|@yYq!o!Mi&{!TI4cY5`r{mQg;%HGr5MJ*Rg;u#@Eht>f<F%?q&Z2iCgiD~De|5raTEmWvr(f_~Sn8vSQ<)NA-xh(n7kk>QVA{8ykNZgP1Oes3rKho|;ZgPO1=(5zpcOdRSz61G2#Er=RY{_D#&7(b;+;C!%?!0C)d9l}6GLiOT+QZ3p3-A-&fLi$PiN7cRJ^7}@P033flWC%d5{rb>uN(Pr>iL!|ka{K_%4?@P{Q6UmAs$0}0r3Lz;nYnT!(_hJ(4NR=Y{2sQnQ4nzS3k2{E3&+$ep@k3>a&a`(k5~dx1ycGk|c&SXlu!D$q$y~v?K>@!5&K*Taw<AA+*yoy(h29K%a!v8R(ONTzbYV%<GC<lE;#?mK30!mYj=NB(Wv2$t5ONg?@I7Dok%_Nmtr6XjdWEH-N9gYlZucb`@e5wWO6IE=7KtB}<vsm3CipD~LsU^O_aJHYavl;<f=kvuTSSN!*sW8L{XRyhiLIl(yuX(Z3;aL-N9PrY*W7u}Bk3Dp^vFb|vbLOe;aV9PO6$X+octOcSmk{mT&#vZN3FI@9h*ZY;6LK*s4vUhKh^OrhO}_E>W3h{qDIBwoq-7)W~>xvc?s9qrwg>?2-Bdn;ud>tri^w(<I{tmmb~;<Mk9o%GvFdmrQNCEiD$?Zl!tFz!C$U6$<OHCt#4-b8yZWe@MMiS|0mUfy#K{WlSBV){Z$mXn)6dk(oR0sI`6^<d&DlsN%$#BVBP0)5w8vWVPT+Ed9b4B$mCqaH;(iuPcZ(^~S|Y1?=i%S!YN;u*9D1;iReUi8QSzmZHI%(R`%=UV1-J@YDhGw}}EJ6ZOdY44!Do_Ys;HnThzQg3GZ7MArw*6o&ny4=HSw=u6PsAn5r$A%5e{~+dH`h>J|X_qYn(xjhNB3FZ0w2XBHX_ur_BHxm6WIU5`I=Lk=D1v3|&1#@;OAMERF(|cxF<q{SW68G$<_6(nS`uvFFO?-($OTaw#Ib0Lj!PVu*Tkf*YDs%bY7+~WiFPXbX9~DaD*Csuq!axz(XLIdIdN^`s^sej*rMA|3tySIGWj;d)#=}c_Z>m(rXE4Q4Sn6bE;H@w#395X0Y3SeCi)v<k)-s?OkV7~mSm%ypY}Ht;gb<3qrY(ZXeT31Nh~@6{gM$&dRRc3=tR`Q7a}f1J`r&y`X^#NCn6U&z>dop5xk}l>njs+1npIpM9~hT9YGmSp9uPhy~L8AXs@CjMG<}y@g({SH-Ppe;?~5XyU=eEv84B6n&?`@BIW7RntXZs^q^gfIFvY)byl8sUUGF<SAxgUw$rjP#yHxM#J#A+o=ZHJ*N)>gy~uej8BH8XyAJKq6feuK4()u@t5^@V9Y)_J0p;ywxq2D@CrTvCZvb&GK2IIStIx8?&vGmuz~v=Bo@t$^>l3$Nnqc{V?MORLKrA{IIk7`{oy3zqC+lWeKc}-KyCu0TNkdN7-Nh`CSG+Pz6HeCTH7%)UU|n5?oUG;RS~ASQI=mG*S?9O2WVL~H`%H53E-=fIjRw~Cl9t{YNXJ@(Wo&A(BZ7cMzc;?7jiLySPZ>*}_|&Hi=)Wxag;?VJ6_EA|MYyx%#XdkS-0=YWI7RsD<i-AtTDbcG_I--*$$}t)|0Q>i_+R3rL5LkY2=;Z}>mEh;9843Pl=f6hDiTkoZKnwzn|u!9iL^yr!SEMcAQ<*U;>q;Q7Yti;Gh&hN>0f~S_w;E<TXZYpX2k7@+ta^2`9{ReE$Kkrp1keXAt0><d9j;N3)ecpwz25))J-j^OWcCComQ7vbV}+9mgFIBO50A$LlG_&C6*<Rg22TJ;C`~WX_jOnj>YRTF<nH`AJM0vB~yZM&w})8N?n05GSNq{=r;zm_)j7y`fuZFn&3FR<_)pvlk}1FUjyu4DZ-zpP7nlqp7?ia7qN)ohXy3Kg+G(aO@6$k$I%vkJaKOFWr@r3TH!|1E=ydUI1PQ$(5_AqpD~mdmfR)xf?SYQPVQjXqiMfjy6`z^i@r-;){;a_t3}&ROT>7!nBKsWDzx3SYf*#`B@SgA;bPMcB{qmf=b&FGaSrm&gTRZOj#{{c0d_))@V^H^o5a5pkEE2bq#C(0<Z@Z^z<_PiE<+LiKc<PUMlJkJraiUfn;_`_$lHFx+iCGwpYd3y@yLIsJT<<ytD9_VPl;{rvhlSYUN*kA)e~&Xmx<34`)P~#=p*<XZ9lQi$s8kdMaCfDbM(nbEOLt1$~-0f2<lP1#<p`&1WOF5&k?L2!K3Iqf_^5`Mi5IG=i;>wn2*c6_W|}}AM<m7&*me4lH6}Bw+Fm75!+chw!u-%i?q-5<QfuJVY_ZfT$Q$)xE1YI^by>MX>o{K1=ym4C{-EfTl&Qz7A@mN9Qut5`f3YqPJi*u9}L^Zq9+7FzGWO4BlDA=#Iyv|<2gRrw%`_wnV(~GevY?-ThJcI@kGWI88as_#%~;RrR;MC0SkAZw%|%Zz{1Izp%U?Q@?uXT7VZ&kJAE4CivEeX1@kI%$ipDab25)bS~w;-(dCJ!(vBpSc|Ink3H@Be!d0YSBz?bUT6)&ItP5oQl|BHAmi2|KzeL9-mNc<t?IX7EJuT^PNnL8Oy~LuI2BdYM2<}Hcgm?(;<&^%s)=m>HiuQ8G-b|mR#LKBAZ4a^NJH$WJ=V#hmEICGehxTT2QS{vsaLpFRJ4*k*sN)6$U!#48J}-%1(&rju3%A#jgS^I1+fKj6d-;h!QXeF5+j7sF^b_uH>LkIyH)(&QujE0}#7-Uz`53^9osBv!vFLAzMdu>ULS2YB3GHn3DNbCRJ}KxYI3w*sl#-U@CN4)iBkkObQI2+EUYn6PBYk3!7w%mU^oJneC$vS!2>zNTI)suqAkNz$#1j9vyyiZ!aDva!7X1gY=%>UY!OYWJ@?wk6FSJFUCw|KMlX85@y8D~gJSBgg{8L`HjrK3ZHn+=?4b<BL(s$B-C+(FK!7C`+c<lyWx1Vu-A-A5~8S3@q_tWPLxitZC1TSO!4aCdnw}k2I$qgd6n0gTTCG-*gN9yjxgJ_FvwPYXhdfMG-FQhD{&qC@2^gBa)AM5xD@fq3+XdkBRqt61`C#atg&#`14@hRFi7X5+g3uueHBY%Q%-toHj^qog6*A%s+1nqFzHg3=BB)vTC_QaitJ26ft^4*EMlNYWQZP6`=Td>Tf?0+C`LHUtB1IbJJP~w5C%b~<8XxqL+X@AdW2`3Kcvt+d-Ke;BfZ7g~w(~Ab!qGwUQXPlX|f1{p5e35B379B4bdJgODH|h@oY5!4v3*g00L;Zm`Z!mOjjybu5zw#xBMQ0}#9gkRIgar5$WqNjE@hfaeQrhKc3ob>wC`EjdkuMq$FB#(`qtERi;M;tr+bka`n;FEnDHrJ@*WDl|dN%QFUUQqeKChomEL=KE($a1~+s5_jo0j!npOTgJU!PiHHs!Sqh#T<Q`IfXKH<xx(as`P+X9@6W%4@SQrr4Kw?Ofuy^f^slxPNI2jvox$#-i<Vy2NXflE1-g<8vMriO+I9%9xTaYl@=*Sae*@*Mh&{d@WdFoTk5B1|9jV1&Pa1%lfS@wb)+jMa1)Iw<On*oPB*=`Yq!9juNX6+gu5@&0Ku0T(s@EzXbb6NpiMbf_+8C7a6<laa+cD8KY$lC3Bn1X;HKVZy}Ciy5O6<M&>M;lVzSw!uh&5^Hh$u@UnKf$!lf3b&%Lz6MFfqAFXw9VoS#ef)+a!vFP*xX@XxG@Dc8n0b8&^+s2}kP=^qQ&`uv<%h(r_c2;7ElZ2e4=Vw|HVo5h>zcp};q^G4VI32NY9}HmOf@urRLR)YwOI{nWlhY0+_l&%VV7WdyZM#hdGoG}oY~->rmW^Z4PE9OaY3jPfMFQ+>j8}x$WF!8Tc532StSiBJElEUdbBXAam$sX_7;!P$MFQ-Glw#zYGp!-9=)TnTEa^erkp6aBA4)^|^r2o!-7N_3NZn{R3W(Jxz%Po@Bf!5AaX(`FeXSA8uP^T>F;>tPJdjv8neSVZ6WyD*H+^i}nzozIFLn*uttrjvQ-ij>#%Rs^lw_K4wP*`2Pb{4DjXdN^&@NA|Bymylc6utN=OHf1x^@$%qFs{WW<I2xO0%pQvEE9v?2C|-wj=#L7Ih-Vd(Cm+8AZl{SL9v>@PD%J{Ym>3`_Hog{uQx(kJq$cv2Ta)Ipw+ku(%7Bq#zbu)sj-Q1+S$o_^KsG$Q>asICC&;Nv|FZ`%@4^u<-vdO}Gb^)C>kEx;k-@VAzs=f%du}ND=Z~m?m6XV&O8-7W~f2`wIh{=(bG1ME)J0TkKDiOXQ^tE|8NlkY~JVKm-@!a~~ltM0}E3p7$he!IfAZ)rl(+x1_E~+>+QsU4+;}T$@^+w>E9T&sYX+iJuYIrk3ZeO<V9C$_qa8G1`|{CdY`65MN+993j3+EZk#D&RFsfwb)0AMIR1GyFn3rnsSCdhv|Qiyx3Q$g}WGFU!)u~zShe@=1KG+;v>Yz$RDLGa*Mp++q91oAL4U_1;IW_`!+@RI!qINi`--Kb%<XPi>^t(I>a@}zacNST`x6RS2dYlo4)meVZR}+Ph0de`n?Hg1NGTPM7In6+Gg6ZO$pzYw&-wTkv8;cN4^bx8q*eCnmC-eGI3@4S0;Zv2>7g}t5H`bZ~IlFoC`w#u>HhtNxKr`R%2hOME{fY%NO*u-{oV!%*V9CL1;5#OFOdDY_2eQ5y5w<zathA{G7T9vFL=v3CTC69I#{uxdY_H&T8d5K`=PM!j)#3W+h*mSfmF1v(l#qCCrjK<iY}Y;mYuu8pLJDe@7{1NosP%0=Qd2;8PR-8U)>j_*det)Y7-R(iWVO`UbIx;3t%8mONtmwE*r0`~5ZQyYv(LIpv!1wJuJxuB6N#F<tT*#(ar9=GYTPESx;!V?NVk`U|c|z8K4-V(?dA!LQf{1=nMG7;zZwIstZD>c+&!S*KFB$JrjLuzejTK1=)^+v8c{bHu`3W!sf@>tTOr$@{itpFYO%OvaMoL72B&QH#BnI0bpp#fb+{7bhN0JCh~Z$rYz9csG3nU#2a1l_iIWJJS|?oqmEtnKppF*NL+;&Gr#H14XdR(b<^?!6Jg~c{~&In1Y<(E{r8H*73ews6&ZY(U$ZFv<3ge{5_yvMf{0*{)hSy@l`(KC+h3OyJ=r#9qc9^PAptd5ZZKRYOx=&oi`?Lk0b2@>~`cf5w{~AOdqkEQ4c0wO+A>n0__UCMsQ`?tBHeXS0EO@xWtm~p>5;JytV*&;f7JKCN2<gonU*c5S)@+FXCRbhXvSOseQ!TX%8dUi(FUQGKSqF-cJ3Q{Ab#d{+hOp?=jE!c%9%3!SIpvKWW?eHGR?sgBR`!(^eCw4gPvv+JNynEyrxp?}LEf)Bj3<En~dYv*3-i-?Q#FlE1>XVf)%?gQ>4DKejEnUd^E3kQo1`f8y@zpPY3Y(f+|Z=atcawiI|}2P@W>A2HRd8B4zPHG-}G<YT<w<<}<0{{kmK4lD'

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
