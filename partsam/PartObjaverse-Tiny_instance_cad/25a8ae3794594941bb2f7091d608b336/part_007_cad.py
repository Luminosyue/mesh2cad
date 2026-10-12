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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a8ae3794594941bb2f7091d608b336/part_007.stl', 'relative_path': '25a8ae3794594941bb2f7091d608b336/part_007.stl', 'source_sha256': '327f6ab093fc36a10d06247b1c44bd9d972fe3f5cfda6500ff2418409f0bce0d', 'input_faces': 1538, 'input_vertices': 879, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[0.047415122389793396, -0.40851911902427673, -0.1573754996061325], [0.1246718168258667, -0.38716036081314087, 0.1678289771080017]]}
GEOMETRY_BASE85 = 'c$}r23AjyF`2Y94*DOhCG<0N+%(HOFJS#M+W6T(#0jXP25+#|FdnuXcP=sSh8H$7mbt6+r5lN~3=iTe`Zg;P}f6w!Oem_0m=leNd%R1|<{qD2Z-FtQ0wn)j6-!XrRIO{h=mYllRaYWZR`JJb`4;<X9YxhCro)|DB$+^zW<&XN?tvj@8`(Tpuv@@(^x9)?w4lG$KQu6K|HA<F^l<d)e;NXFspLneQz;4|oZ``@>pzeu$P|wZ-x+h+js!_dW*+}KmWh28Q|I0tQ5<^Jc(Rgk>8B6lUgBubSoltbkhOqqDuoYpsv*hW}JhHjyD)+V1(wE0Bl?u-b5B*eLN2|089Zw)<Ja(?*v2z_yJWCHZj|`}8-uH)MZvXKbeSCRppJDEJG*91F%{Lx9cg8H;7?!7x`8Mw6d-|F26eU0ZO=uozHpCsj({DiNI5qdi!#voz&V!xnJZrA+>l|F>jz79@sGG;~{c*s}>n#b*^>ao05BKMME-&A5!QYRS2l~;Reo}L$`p3gKy<Gbzcjiua^NbI^^Y!C2NOSY}gGbyv_V0p?VR@wTq0sh`sRzt>P9Amh)OBCDd3^u-8$<Jhrk~UokNfiUdI!yMFL272$F_f9>SyIo=6yHsH2u8xUT7XkJsc0sPtgDAU;X_QrT;Sb%yZAPyFWAY_W9J%Jo?2E)6b`ke7QG2v8Mihx=c6oIiXc(|8}n9cN+gW-#uQvYMAqGQk6|^p7EEP$F8es&X)?+O};pJLFV@9$Evz{v}sm1k3R6{fz17+F3s!9wY}z%+?UKa>zLemxuTmp%XXQ5_7pPx7ph|VS^cGH|9t_|{<jWhJmt5Uyk|C(ukYl~S7!I+>4!fzd4a5M9`CVtp<54~YWdD<JJ<6%UgfZxM|07>+e_wruYTIJ|MRk$XZ=3We8Hc-JiagMBDYRz9rd@*mD|lTqCfcZ)MoA6JlgIne?P-Jx_RpTyZ!mtWo{lTy2Ic9A8Xw_vU|I~|Jc{Q_BwCzzxMgs>%65V{bR<zw3e?P;=8gecE@>tZD0Mwdu3moxxLm&JSCT#J86IU>cq?Mz3i`(zWGi6=l}B6o0reN?61R)-z{<HX8`Bvq?zWt8+~j^=JPaK!F->@*Prs`+CF;gZA;zyIk(6Ey}F{HFHdc;$jxI;VK<Nc{IzM%bt*P3;?K{U_D)(YH;<P4(R^<>ADjG4Z8vvH9XI2gLte9vuYDxXYLmZG*UeKe-R;hE{NyLTT>H`Xk+19d+D9*}F?qiRru~dMzJ8+F8@YM>_>}{p`INu?`OGH1_S(OfYx`CvkL|dBxjR2royY!r#Ld&+_vh)gUUT!*J>U5Ay|24@bmswoov(e<<g0i3*Ijn5>n<zz)?HSv>zwos<9)fVy8=1uf%I8#yLtS&o&NRDuM<MY8OZhf%F4a(D=XJ=MhDF`@B8dMzI9G4&jMebzODSGdLen_rtF);avi_s(LD`(<F|9~ys&azpV)c)=D#O|<*79$jS0(R{r;O0I-Z_O(!%oi+cj2&<$Am{PcPHJx1O|fuWs%9RNjeUd93D^w6Ol;&z0L0n%`70G>>e{>N_rxyr=!=(L)RU^FaOBxz>;7+P|*%>^$D{#W7)dMwW|a{;fRHHOJ=6dE}9weB+GHSrl5IntS8VDD2LIoyR-o+8mbaaZG(`rJFmqC7aL1_qm;G9oo6~ePZQWpMm~orjH5je`c1cVdK&I4D`=&4~&Q7?&V)NzHz2+TIGLV>ekM+KJ8rV)6TU%y`1;e`LuJL&p>XEN5^lEhg|15@V?A*pnvAs&UK#cJn(t-egB8gtH&iUevV6e-jDqCz<FfndLG%io=0}B=aHA|JlOr~IPLz)1O4mx=|AJqt>!wr#GI$j?1gUscCN?Q&Qp(FoDi1B>u(<umdBpFb!zDQR+*m`mh1cn+Lupp$L}os%s)>3`P9lYR^*x(mPfK~NDJ#n>mlRM&;6fw%3?D=cAj&=n6TX0pL1$hKk0Xv`q4br<+ShTXgk-R69YLvN87o6UOV@Wmz787?;R7C$7dIw8a7Vvc-iA&J_C8t@|(i)=(>ubdFrTSGe3>C`*WRtD|ZI2921sj<j6ZUtRJ2Kc=un-d9n4N@BTv|=l+A8d-or#+-d1d49$oAJR!9IG3~~N<*7G!ni@9F)E#MQq51R=Lvvm41>U!7rSLrVx5<~E_2u4u6)TVbTykt!p4zzS)X;v~|6`8(f4}<H^Ll^A&h`F=o$GwsdGzALW5e=zi!M{c-dE={&`++);p4pFFO#=C=N~8ci|kzM!Orz~1^O9K!R_CfcHaNK+;_6`X!}ZI!}9phR#U_J$yjv7jDK(872=U8U;FMa*}2}ovUBfy$!@>ow+Uf+#&?H8b0^=QV?+CYaOu?0aaI_Y7M92Vdp|VyzGtjFc7K)7JaX@ECNC24zc2UY>^y$pz}T=n`bqlKuzsRv&b$3bau##*jE4UCw{xw3JC8LvF(EA1`3&^KeA;<*^0c(joca&+!~DeGKIi7qj~n~%3t4&O*D@nQ^QPM;g!L0&Gj?<4Jbry+|NSK^kC$pOA}n`~ADj@@PkQ8a)Bn(m{#@@<S$Q-b9TAqNFWoyKw4Z)s%=+Zmf97+w&*r}$YvnqAJJ<2sxsKn<vu6$OpFGe%d7yuC?LT^R)(?H}tM`YkT<0gyp7{yn%#WArc<NaFlLz|OaoYWpM?N#-kG06<=Bbm;n(v>r<=p=5JXU+fh_F0*HqXScew@Z5&G@I}cJui3UrawYn*QxPeb%}WVR`BuH%tueCvAiof2C_pewuN1DR0Ja<<Z_VMug?@ktq|y`bj-w#vgkjukU@m`LXi&p1C8!a%WABiDCWd{G?YY;O3D<=DCmF{}1FnSC0(KGqQ}E7}ihvBZJNP`(i;ikF7Xt-k0YHfqd5fkzslI%(RK2{q!1W`tKR>y>DblVbi~rJI<n!VR`!Q(Gx@aNqNewZ&w!azi(MHKX#s4bLYsgJl1d8#ISxMs|LCKNBZ35=1y62A61{H1oC|4UJcD3Y%wXUpUC+~O#P=-GUwe3wCDMPoyX@DeKj;M)_77_KaqNm`ug|A!*hy2ezd`>VR`Dt4wFLrnf<VtpZC8v$E8(s-+ePX*ZXF6uJ>K-T<;G@Uq9yN8JC;+o-5gT?Ah|>dHUcBCZCYgcb~`3qn%2a_8Tvnyh#p!dn?!W&Y#&=y64mI^9M4ww{vYD8K29|Q!AYFwYPJx{nUykKk0wYW#`^_QmeYTQ{Ug-&b|I;b$9bf?6ALoE7$h1{k=om+qt$+JvYeBGv03LyWZKkUXKFpxgG^_u6OCLKW*lrRx96n$<B4X6v$aG*}1NlH21zwI3Mj?&&NQ{`Do{QKE@9`W9IE-OaFSz%DwfNm3!+kEBDr8<lgx8d9IyvzT3H;?}7H5@9_=8Or2-rx^pehL#<rD4+A;hhjyMmrIT5Y9U9^0(I1ZbzR&Gkzt8Plzt8Plzt5dgubA`V&@tcj$j<e8WaoN43iQMED6(mksjGe0`0C%zwf+O`ssBJu{d@VS+`jdmod^0S5A;v2>pds$Xy513^+q6Py<z9N-mr6BZ)olvU){H0=d3sET-O_c_N+G|^TwF(jouf1>peTy^`4#Ude6>vz31hHF8J1acCPC^JJ<DIAZNW7`D3i_xa;?Wo$L35o$L35o$L35mvh_${gVg!*Lt)2*SgZ5cgBtL&701To$LJAxz0}@*Pj<OXWqP@7p&a-dBMuPpBL<Y_<12-WTaUa=>8Mk7h&b`a>K@k<<XN*P7UiP8u`=Q4_W)Fxo*Ef&i;x(uJ_-p+`Io~w_juKr#T%*`*Iz>o$L7RT*n{Cb^Ljknso%vPxX0LAm@3Lo$K=^JJ;ty8S|E#dAqi~sYCWl*ts)&_v>MK<jv_*!urX0@&;f3898{qz;kvx*XQPTuFuWwT%Y@E?%i)^-;14l&v&fcd%k1k>HEy{nv8o^`aYNL8wunqe|<eH&nUBSN?1R!=kxjc*XPc<4=0f8^8zdPo)=ho<hd-S|8c9#=UQnUUn}>Hua$ep*UI(y#uo21>(EB*pJBg{ojW75j0wvlZ?BpX)=$Rhyr%!ZzcBk&#<OpSeMffg^>5`~|5hHWc%6Ap-E^1vTy69F=Eu%;e(YT5$If+rygcQG@czjI{gVg!C%60e=9B$Yb{;KRZcJDn>9%7^SU=IpdCdBJ;%@(Z(!ZU@*B2cVmS>dTIwh<hum7W8`Q}Z}uRzZEW#@W+*}0xyUas@s%Icpy(7(>J-M{AFnEHwCn){Ks)8}{7kM38ubKS3Q<=%dEEBE$C^;+P|y`R(VT=&nDr*1iK)*I}DimqDd=F#>3{!?SQJ{FJv>)#h@=ibln6Y{#b?r-#dez$V3eV3cvJhrv387KQ^GOpa}%k_DmoqON&R<55bqgeqr&$zv>Z~pCE_i5O<cipja@4936&pwSn|LoTa^uuw{JT|0{@4iPMXP=3k>pl=W*Lk*cZ$E&Y>;44$eOV7UlMDJkum1l9R_^`(1y-(gm2s?)zaRET*}3kIvU6|V$i4BiZ^X`Z--w-i`%+%2<>sk_l6>=T=U&|wtYhlApMRf~oqP9r?rUStmk-PO+6Quuubpds+PSXl>|ED%cCPhl=UP93_W#59wSEFQ^%MA9)Q{%rkCzFZ2hH_;qv>tk+*w=3H$Qf+<F|7ir{>zf&ZnL0eA>Crr=9D32Kr|n?A)7&U)q^*=D5pOw|1^|Yv)?G(OUQUKQH~*x%Ok{UO%t4H|N(M`F+R5&b{NJ`Mev#+mn0uMGy8j@7wSuGtcbHvU6`=la=c}A3N7|yPfO0J@CHl^RaVp-;~`y^%KZBzJdPP$CXk1N%K80neppBA3N85R#xuqv$AsC=i>|-=;o2;H~Qzz%Ds8Ba@`+g=ej@2&b@iFa&O-3oc&RO_hsKgV4UoaisX69pEGZEu0QYCx&FLk=Q?kZiL*@JI=ktIeJp{TeK>Zm`<m=r_caA__TdC__Q}|}u5$wK%f6;S&b}t6{A_>D{v|ut{Y!SP`<Eiy=9urRIobU4W9K?QR<8F+>|F1Y*ts`9cCPbd<+_h3@V>gQ!+u}(HAQcl=WoycB0JapMRu<Hi((_cHP^KpQcTYNA3N9mDt4~>RRZnV|6}L6pC`}{`&Cl+9P;J5Psz@8A5ow^=VR>lBj$VTaoV&0$If;CPatRiPb}LH{_(S)$IiX^v2t&ItX%i=1agjhpdaQZ(&phcuD5-`<UEH8<UEJ6bA1k_dFs69O|JK2t=zjGYvp=BHdgI1H;-R2xjq-LbA2ul$a(IN@y1LycPiEQjmOS)Ja(?*$v8C2%`<+iXU;qBKij$2zm<FaTe-KN=jqvQ9vxZV_j&DHKW`w{eMi^LHOHk!)V#0$e|A>x^>5`~|5mQgSyG2?F!{zi&3Vmzay!?3HFmE1YV6$GH<Evoo5wyYZTjIpxt;5May!@i<bi&;PoBPbi^=n|9_BfVo$GTJJJ;tdcCOD^;!Qtu^Yq*N^JC}w9Kp`@IYJ<3eqv6Bsq<n5%=_{@%g*(AmYwVKtkh{oP5nH7o9UnDR(7t>tpe?NZk1Z)xH(^*HT~;zNjul)l6J1oB?JBNTr&3MN%Q^i74OS)RXf+`s&=l=Rqfn+uA22PGe5tvUgG(0Am{n7o$G#>NX`Gu_;r2D^LIPf=kI}>=kIo|&)+ro#=~=PJJ;vnf%ZHHk6o&});*4u-!lDkpTW-c{#a_6hQ3_)vDmrpV@c0G&CR|0-g<w)%Jt`+^qJF5-t#_xdn@<azxkP)>-VSE-pal9Pwz1K<huU$R_?XmywlCotIqI!PujVDPX=<nhvS`gxq0O94Bz!Mkn28JEBE%n&fo3k@li8;*B3kY_E%WBcYR69_KEv>t5){SgPnUnw^q&V=CL;``P$pL_jBv4@@^i_($#-`v2ySFV&{7O`n7_|S9kVbzpUKr-^#uItz55P(fw82+<Bm@Z$9l@=hM!;=fy><xq0-_F241EoqPRTx!1pyYyYXm?=i>aR7KzX+qt)Y>4Ro&9=Y3pyzJb&FZXS0^S<oE(d(d{>vho1^*U(h-gU5KTa!;~;lB=Axpy73a_>55=UfM!yzSjw_d#j@cCP)~x%MB(wf{#tnEHvf^sPheT-PCXuIrFMKdeJEj~%Y;yI$D2UM~VU*9$w>>xDC~qdD%c(LejC0y)<aJJ;(-pgq?SXWT<>o?gC+Y0rKtJNK@qcCOb`EBE$O-Py_H^K1Lo6?X3Jcd~MCzmwe$>k7^F_g8rPwXEFRuVv-lel084bw%QQHu*p1eZAj*V&|;i>|EDxcCPC;&7CaF1N)HzIqNz**L7W>y{_wyoHg?{m){4a&sDA5d#-Bb-gDJw&YAD4zxjPrJRh`keLiUC`us6<%Xw4hvo`t1W98m>tX#(vozs7v+yA4Zef`+E_G9OEKj~}D`b77o*tzaY3FPccNxd+@%_Ch{7qPD<kaNGt&h>s#pgsF)QtJ;i`SQ{J`L}X!{;k}bfAWlcubKDN=kHeT9TzM2j*FFhb@Ij_H~02eFrRj=^BKr>J`W8x<L~~O|MOb8_j&D{=h4p4x6C*PJZ3%@`-K8I&q3^5pM%)B_k8fP@n-z>2b*!~?}4#$-H&1Cx*x;Nbw5Tl{{)j?7-;5`{Umm-{oA?rZ|Az7MDuv>nCXZ8NOrEzh3#CQ3){Iqr`9~O#mt*Nzp!(Ceqraj?<m@NqB-v-nEBED6?U%sE9_kNS40<2GI^6hCTAaro$Ef3Kzpm7Xg=1r+@H5|y+3c~x*sXJV*h&g^L|_GTlaJE+&t<WaP!z*#ogT77h&bzz6kP+S4=<NI^W8@b^dEpHn{)p%;kfb+uOO<e!z4$Pj6(kw{q|2jv>3<+-bJi*WS*(b#H91o5xq4^tHEhyS+1MOK5w|z4m|YH~sWH;csu{-nzQNY17a6J-+sK?#<8hKbd)}wAVjBR_?ZM>-#O4`SOohKc%VTh;lmlogSSt{fbNp<&S#!ugL6G<^StfWLB(NxyJwPcVy<Ok{CnPgj(P&;TCW!yfxek?u0)IcY+^7!Z9TL5Pm=W5c~k%5q<#ffVYP`!1v+z!uP@L@V0O}xDDO}ZUfiC8^hu?;aYGFygFP1z6%ML#;d{N#o^NM9r*3=9dJ=R0!Q5PF<cZbme4(T1H1^_0IrW0hU>#oyZ{`9>*2S+_29Y*)xq=Px4_~z!+GIrk#HU)d=q{fEPg92UI-R12;T(f!Eemer*K6iTmdf#i&uultH2fDN=UdV-U1eH1viD8BjE?}PO$i6@PqKfNcedqJRXn1<Ke0JL-17ib^HPNb$A5c0UiN&!|#K;!Cmooa96ks-UjXhcSgeH@LI5V4OsjxxEy>Z5-x$4hQ;rIOTZ=ZqHsyL6kZJ0x-W${giFC?@kVf2xIEq&?#x)r<9EX4;WBs$xCCP=gO`F!@gBlbS5i+}lfupLrm%Q(xEcHi{va&=F#HHS5(!Hk)lTSc$DEhfCv;sxHzYJTp#hHk8fN49VDVgVsiZ`$CsY9mPs3-x^YO*_40tg-9)ATM4^KkEFCpQENH~hmfM@XDQ6yXzF9nx{cPGZb$}t|tC6Du3xFBsSzy;xANcatW8myoB4J7;l5<Y>1zrz>9-@)JF<Kb`Nt@tE(E4)6TRrvGxBzO{Y_dF6Fh=g0>4dIsX-AK3w9)+XKV+|yn;TV^B%s|4QJ6GrWb0oYCUkz`Aw<F<CknjfyO~)r8;o10VcsBe#z6xH&aeW^NFU94!3NIwPh1Zhbf`lV@F*pK`#@~QP!?W-Y;92ld`~-XyK97X|K*DG7@8GlWPx!a+Pw*amE4&BZj<1Ke!)r3t&>AGX90?D_pNF5PhK3^Hws=dpE!-5p8*U0aNccC$cn!D)HT4@3K7fA?AAk?y+u&`~&_N{pZ9-j>jCaPj!y@6w@K0coa3}l&SS0*#($%^Y76~Vo+s^$-##4DMc`9uu!Kv_2Bs>HOPsC@#v#H&Q_)=JFcOqJtsUP9jVDW2`jD)Yl7s3mv{p+at2z(u!9|`xyN5iA3@7_rGX(YS}KMEhE);A&HFOl%|$wtC=;(x#*;qv%dSR@?9e}YBA4e&j%NcawXJ1i28;A>!!a0<R076~UM8wqFQ?}x%eIUlm&P2r}T1KE)9pN^6630%&B6PybN;1lpk{2+W1K7)S?>p5@+?+%NE|H2=KMZ($1<g;bRvyo?GyxDmze3|i|fKM={%lH}i4DWH7`pchmwLXQPz<a~Jsi!B9@P2#~yonmxkA!bYHu{pfN=tbCgsLWV7hV&u57&enA>o&i@T+(l{5HM>PlFfW@8D_hJ8(t3DqImRooRffk?=-Gex;-1e4Nl%_(oV<+I+=p;UDmtut>NLStGa(+zbh~!e544!Gn<SWc*cF=VCGv-hhNZL&AsfC9uxdAtd}g5<ZE9=iu+abKp1eitw9oalABK94>^*+!f-r@G|D}V|W=nFQLi!TqOJv{xSS9$LS*^yb}o@M#4w%ui&pZPDhaNIb4p@IbI7VaqODGNpL&772FOUh7W>=!7t#G;mI7c7m)Dkgx2Ca@D1<=j_VF2{52B(89xLc;<)~dgnvcCm++JDCHQwFd<+S{htGlMaO~eh!mlIYB6xAQILE#S6227)FQPuA4i+KdDfm2C>thNMei;eBgoNKk!gKJs@Emv@{t>(m-huCgcfg16!|);a7bJWN37^J~z(=U9(@6LqTx#ndUJK`>-rB)A;T8BWco;Rb0$&YlJ*_~(dJPrUYpZYs-vRHSw)DCztk-Vg2KdkL&(xM)_l0$BAY2~51Ye@gbX_5=YY$;vp9t@w?J;;4ycvHF-V8s3zYaeG_rZ(6ec&7MTj3kwe7MwNK3)rtraq^@Q>eeuNcasTJTRd*@j(goPN+{pz3@TsAle8I!=J<l!UO5^N&F@FNq8(0ei45cmNm2ZgZR7fyPOZgB4J%`3wOfT!Rt65bgeF|>v`eM_#yZZ=Z5|)AS~;nuCT0$y2F3d_7wa#d<8!ZpXNNdg3Gyah1bG4IA2!4E2#Y(_~Yb{^WHgdc|YMi)ZaJMqST!5XpXDYf_R>!tF@6QQ~l(jzQp@ys<-}`YO+5y+n>HS<GWxvUhNa=AY)6sSC53UIp&Xe5)#gi_khJ8hqJ>u;2fF$t#C3DPC>#s@yB8Dp0Lz#R%%l`3!H_&?}hh-d%^t^l1DAM6M7CG1V0DMx$<seaP<<ZjD)Kr;d_wqi%57R{x19$z6gI8o`+Ax--V~b<?+gJdAKAJE`wKxcR9wt$E(94;o4;Pz_sBfNVo<5BHRLg5(!VlN5c9!CnDi>NcdAEd=Os*>s%Z}!bgzsaU?t&p9;^0$KvJTv2anmBwQ3OfQ024TuJ6{gL8ErHz47a_-F7+_(LST6$$T0!r$P#;9VS#Z;<e>xEzmPc`f`O-UJp2w;^i*w}FS?Pr^gs;rK*&BFAPp5?-0m$M`mU9lVa?w+#t@g@jMz2jPPpztc$g7bJWUKMr4n&mrL-knl`=HaweSJQE4OhJ<g&i^4@Y-nS#+o00GW$4GbyF2{ZeHLwz10>6iU2#e2x--F*y=pB3}J`0`+uf;!v*TSFTTj5XPefWNOAN(^C{t*cu$G?HUp|*}A;Y;{`@Fh4aH7B)|6$vlHhrmOqp=J0=SnEl+2QFXo%gFUhUpP70NceVq8@!D=6BY><Nj4I$kDrE5Q)j{=;d;qN!sYOb@I`7)SR`CD*+@8VvXSr?wEY480^W$vgg3%Z;jh6@!M*U?;a>0!_|5PQa9&($R5&-;vyPGQC|uf%A{U>4FMt<N#}n}P;P<G}3FvL-YX8E|WUA?Bknjr$bxbn;0R9gA4z(^U5`HMjNca(aExeXm7ZwRWnq(v#!}r1asC!|NaF-+_;ciJr!WU`#BYYA513wNQ=N$M0m%9Ih*TPvi7nZ?V-&yc(u(-U3@XgfFKI%#8W?$0PW2whFH?<(%FH>#w%Tz!8sIPwXu@V0QE|E|rsb?fS1)mPj#TVk!;f3%xd;~lWo`8f?k#GYfTo<1XPv^bsBH=sn67Zeymx=jW?igQ>OTM1h!ne`39DEym2NE8GPl5F_k3qukBjF#B@L_x*d>B4}kAn}uTkr|+7Wk8dKE$8HC%_Y!yXTPb03_TTZvZ!kYa!ukcwM+I^H>cDf9DvNdHfCuZ*s2A^(G{|8D9Z!hPNQ$HApx;p=tPANH`5&0jI$;@a6Dwj_V90ycn0`Dm<U;CSFT^6A~_r-vJkfN8w}OQE)o`KAa9`;6K6{@NY=?0unxhABNAsr|<*tDR?)&1>OyRj(-Aw4u6!XhCV{VOOf!i_;c`c)X=j?xHaA!ZVflaYr&1-e;p&?vv@VQ8Z~tm3Gcx-!F%AZ@y+mNYUpbuyqE9my?lr7CD-rsEqwoPq2}~ju!d{I8tP217wKGIv@Z2pBP`b+xlV}>=e6X+Y5NvD9DW)JKZS(H;c0LhwL1=93~TL<L-XlF{MAf-3g=2P622Cn56`FeuchV-!`H&sBjKL-D0me0-4h89M#6DC1J0n<<4AZX64tela8dk1($)2na5?-;($zJUa6SA~($)2taD9At($zJaa1s3Tq^s*a;oI?#lCG`^g_H56NmtjC!n)3MbN>EW_*u?}WV|ulnDZc+*TUzK@KO9Me3rUDiiD5hU&F`XpYXk~o&!JO-C&XM1-u6=5>6qL&z6EGlZ(q(Q+O@>JL5kJA7xCx<3GVa@gBcZf7d5ntxw^;cu%+|_0$&$@5SSAoEqATgl|eV+DTpAoACQMM`iz#>|J^#p&W_7%aUyND~XSB42utdXD0GR3C%;o7w|vfE4bWTx<IZsn}lz{uS+p35-x~@^CRK4$wtDfaryVF>3b2p8lH{MglEH#B-8|NgU^K9z?1NK@Fe(MBzzpd0PANyj)c!3;c6*H!VPhmi-t(JDSivw6mE$Zgj>SV6#4Z(#;?H(!UdVTYmjgjB)lovxXkG$B)kF%FU42GtC`28NVq5d2;38HpJ}e!BjFBsQ@8`%5eYX#!W9!Ljh8~g)$pcpHMlC?1a87{t%`)};FI85_;`F0JRY8kzY9-=f54B!KftH(Gw><6RElw_gHlMi5)!@}3Ezu1gztqr;7#EU@B?^D_yM>L9);V$H8a&vO(a|f3FpACfv=&4av<SPlZ{IaeTszF<166xa4HfWj4y?kQbU80aA&+d+!^kIcYr%kLtT(?*Mz>ukKi5QBk&%)8N3JHjaP(s!(V2q%P*1e&V;t(`S8+kX=*ng621lr=SIRM@oI22YPTd_2iDpxiE3r)N4O9y{u&Y<gV%z^$HU@N;W6-=NO&*)11x?D-V1+=gl|tVF13C;HD3w79liqzKZ=B7_}y>}?t<S7cY%B09pD~tZ~OtcH~a+N27UtWi`Rtv!aeaaa8I}!5+0FkJO`YE^FvsCJuIFIkAR;=!u{~U@L=k`9}<27?*cyo_s6@!dJgo*e}((Q!|`+QaCjsxpKT;Qf_wyH9f^d8;Qio!jA;noAMVe4457x}%v7Jk-{5=Uz0}h;NVs^4ajBu=)Y2VrarhB*2Q_s$(f*@^7AN!pz6}2eUIu@Hgl|kS63&NThHp(Vo`g#-{11K+m;53Uo{ukv=fkryjc*nbZky193AIe96W$hXOPfwexEH<*?gf8{e*%99Z$QGEarw-fc`ck32^Yfi!8#X(kZ^q@+zJUd!;@g0uV%a!Zj@pqTs_4|_?Kkk7vW#v6Zm}i1Uv(u1<!yd<89%|a9zA5To<m9P+7b>5^jOFgj;f)S|H&EkZ^Y-+yn0fcj7qpK*CSqAHq+;FX9{E7vZh=W_T-{lVd5zFDDYtgBOAeam?}{;R*@W!rS8Y;rblcwn+FvB-{~i1~=olc0|JWA>lfBb+`^(83~t0!l$VZse{wh!wL8_d=v>!!)L%VIQG+!@Y_hZHeMI54c~>=fVDpELc%v9;rvLr3=*z{SBERX&G8m+bNGJz0r-Bn8{Qr61`j~OPa@%gcn`P-wKWh455r%ChrzGnTj5vXvMI);w#rgtdEh+MP1#KKBz%s4*NxY;Qm$T4h4nfs+!t>Px24YX8ZE5XapB&0N4O((rfUFUT_*^4!Rx?vs5xC@2<tjTSl24TMe)*bQ8<E2Ek<}Pe2Dry3Lk>^;nU!K@HqT!cpN+yuMLld3*&decTtOlk??IuI9oym@a#zV-=xI%ZIbaTxa7il@T|DxS^0N2!Z%X)S&{IqNcaZ447?rRiI;)PaBl2G!n*br-i<ehn{#gHx?Nb;_QFT-Zg4lw6aBeB_<JP$D-wPle-eHk9*Pfy2Xf8~#b1So!mr>`_pc;hJs*V6@qVx1&%+N<b0zSiaAA(+SbTJ*dKjIlW`y_Q2a>PWn6TENu+*t|32L?k?<Fk9=(B`APw3CYalb70q8zhlNxTOV?uSd8e)wOoNcai(iA?`i_;DoM6AAan<=^(l|AwVjWv|i|ycgVye|Lp;e^bv___zNhnSDsIAL-g;<8lsMi?VZmTuNwFLJN`b5+u9^3Ez-nB%Bw&1mB!u{6AhxF8nwCJAMiN9iEFXgy+KPNceqx3H&hrIKBja9A1vEftSPUknl!aKF>y83#TCA0(f3nKW70XTn`DiK*CLM`OHmHuFgdh{!aLw6eHoPDMrFS)Ao1xXZS~aF8m`r9Z!d+!xNEkYy5p!=dm>sZj9dtH-;M_;d_zrV@NoLKMX(2@rWVeLHKfb5c~qZ4t@dNf^USkz}Y!wa-6aw;oNuuxB$l{Hxe$FPz}5_UJtIv@oSBQ??=Mz@g{H+j$eBu+ztuX#;d}$;fhGOBoaPJ9mw%M$#MS?J_%<a;VJlZcsj>>3KD(`3D-ozcjK+$)*SD<k#H5f5iDLAt^yZNs2E-WuMAg!8{&=NhHyLlUbr3nDE=7yDBK$f_d&va@faMVw)!IBXYd!`XW*CdE%3|mohinpw(g|Ha>Kc)n>#br)164TD-wPj3HQNU!>y^UK1jG967Ge!huc$Iy^wHsB-|OV4cDg5IwRr7kZ>m?Tm&x(7l8}oQh$YcEqsug%zzKVU*l8Yui-cFx8OJ6*YTS0C_EPuE{NBJbKxcMns7~Ow*+1Vu0mawK*cllFPt+|9p^;C*Cn(K-+>o{i&5V@knk5sco*IfZb*IaLc(7m;luc&@T1iFVI=$=5<ZKBpTqmW&%saQec`^;{nPl%@YC>1xYY4Wcvo2bH`@Hhd%uJ~2R}?b6~l|bdR+CmkD@Nb_h+gTVXY-$sWtIp)Lk+96i!Rz3lf@xgwNxDz<=TY;(x&Z!Z)QDzc$6NNcgsda^ctG*TUDsA150Luf(OVmGr#;UJ1X4r@`;R4<&RD-U?5HTfr0XIq(Gd9VC1VKM(8YKZb;VLc&#2jD#ED|H2~S#<<K&V<g-hzYT5<*UdC{b&>F0NH`l3PR6f?li_&cJ=?ZOO3t5h^_Lp0-w;`H>R!hYUE^H+Bm0~Z72JK`;9mTeBl}<ae;rche_7%_=jty<YTF{K`~M~+C;pTF8RfF<K6L&ca#-zo'

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
