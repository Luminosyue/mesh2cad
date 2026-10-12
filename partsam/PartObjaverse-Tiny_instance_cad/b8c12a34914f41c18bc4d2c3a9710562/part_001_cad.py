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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_001.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_001.stl', 'source_sha256': 'd840d564eeaf2fb1a9b57614e4513a7a103103ea27d10d9e188f5089387b4348', 'input_faces': 874, 'input_vertices': 690, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.04964253678917885, -0.03464378044009209, -0.14984330534934998], [0.050331030040979385, 0.11769571900367737, 0.0825849175453186]]}
GEOMETRY_BASE85 = 'c$}r32b2`W+Wvc%v;<+vLBf#JE<xgQ2@Ob+tfGj7VaZ66oEdN>Ns^qIU3S+MK|u+UhagE%MBs82bwu<ECR7APg|FUvpK7|_@qf<$e4qE!d7k=JO?7p3S9Nu5HMdLqELjU#{9jq?`JeB<QmeUTQOIKzvc?Y>J$6XH0b^>67&Xaf#c59e8C}+?TgNWX`K<BQl*;`FjOjPJawC7`#seExj`vp{ICAvZ(S1ks89BQD0OGCt4jVH-@iBw@jvAoiRq7|!iuc#48t<Rx|6l%>OI5*tc<Aegl?E;zNFlX)AKZV~#X~#6_iWwc=HU$R^B*QRbMZ(&@FL^V+}t|1pZVFekSG6e=E488IqE6D`_7d*|HjrH9=y4O`OSTvdIrA)PkGB*&qd&)zVg&F91DJblBb^G0^6D2+vurh@ce^0n%}zYDaRV}7xU#Ap8TpEyXoKEdHJBbKGxL(np@i@@AcI4YLRvHd+Vd`4tw~);wi-K&Mm`k9yzf^*W1py$io9g5;HX)^{I!42b_FEm;di7M?CfUsM}jQ|Kc$oZpV$@K|K6h*u%pO65r9hXI}4h8E);;<rjWV^U#Ef>Hl<n4VTx~aCv<Vm+k3r(Vm9e<+Dtn`UH>r4|(#J%c{9mI&PmQ|A+hLX})y7H-FQ6%XB$0T@QQeFRquv#r1O9L0m7x<@IvP5!cJ9kGNh={l)ci$`RMgX=ic0{DYfq*1GHX>zbcEmfFn4?I|ai&$_u;w@1TBsxI&2ztXuq-%oY(K-~w-FZ}GuZ*5qxP4nA_Jo)|o7BS!Qwa)L~K9Bj;Q+(XI`E_~z!n3)YpN=vwvO%|ZBq>4j@TLkGnpZ29?&guw!@2x-^DsYIRdc&z8P1<8Eyc~PRRcNy#?_iz3*OWBu|24VuD6x<LaLhw6MAy|`0tzDJe<60yN+jl*ONayXf^YFpX>bL;k~(>C1?1&*6!u=-PKETe<aL&{3E(P!8xTg55=Z&xkpQ<yLouwcrL$OcD@ejC75^F#Q9UVq_}zTuhE=8b}93XvCMxAaQpmzINi;yb9K3W8oi@=;OiWmfAce(|8l_;H}}t~#`#O+&^+AvtB}4fVtg=Mjt_>*@xgF8J{T^?0f&qJ?vx|?yHg+0-yJUcyK`QmzZ)+5yHk$n?@oP0e|PFH`nyw(=<iOuiT)nUmBi(Ta9_QBTR*=7i{iMPALj6NTzb#L?I-`(s`<qqnRn00d~H*{f9h`2_d|G7Ec5euxj!ToO>y&J<wVY3$j7|h-A%fEs>N*7yv3DNHxKX5#{ACx&2DZ@dHik7&+qW$_xEnaJoyTbKf_LK)cIRn<Z{v~q`P_egMysjwwS+mRP#`dvz&j{_7pd_Z{_3s6&CRIPgtUPB#8EW@<gheTbI$VFW=$%4{65b+atMsN?Iu%{vejyr|k{h&cQ>!Z_wqOKE&5072_?qUHUZhDt~c#S1+&E?Y!)WzE7-AUgPUB^pfWOma)2A>rlxQH@8L{;QYJ)<l{DIsCoE}Pq^H)^Qmrb`FOmx;(ciz{!E6xZ>{_LJ^Af7wlh!uo`086XPv(8b(V8|VzZ@q`0VjqpPtt_{YVAPtu_breQv$EHPy}i)ebUG`k2elRbj1ehh5W{5B!ts*{U@2d6SrTn#1idw)Yxc&Z1gej{=uc-Q51F5%aa#(%d|pScU7kWRE9*uzv#cV&Cfe*l~?Dm*bw{a@;dqj(dj7anEo$?m1kHdrmoG+;i&F8vNZ>p5w~#&?%=>QRY=Y_2w7jq|**!oHSgHlTJBeoOF&W#!2UV#W?AdBgRRmK5f8rX7?Odj-L)6$vimfDV;w!aoTF#f6El+`)c%N-S6xiQ#H3<Ikr~wa%EH8JhC+(=YRUHzR&G*MOShD%Io<)&Y9xo_QBme{`8D+{_wmN`nZ>NZqPh~$4`gPIL$mhXPTSa_n+i)?!V*7AFk3J<L7lAKkv5E+}eF>r{*^^Q{CLZ=4a-i4>|va$;);5cQcrOa#tVM+CM>aYkDg46EAUp`nJY0oqx)Zl{$XBl80M$D{=m6{G1AJExc5pSIa!BHNTcS#m)VTF%Beu#^c7Gt4s8Gz4gT!9bf-hs+-##Z!_PLJI#~-iMCwMtR0^G{?Q$oFZhDT^YES}|J1JykDAYbN6lxzqvkW<QS%wY<$T7JBj+=wKB8YcT+VY0m-8HRzH*)e9yQM~<;Z!Csi&OhnDdhJ98->*=a}{s{nX*2pE~vYHP^fPxCKMr{56;C)%kB6_wc}}BK!4m3;frczf;*mn#a{RrsEUJFVy$v+n2aLM>Dv;fcw9?%zXSgzJC_yU7*|H>`Tl)|Bcrr-jCHhkZlI@Gc)yd@ZV}VU$@V}1brQ?sZ~5YSpGNeFQb3a_kU#Ak-0j5`h(?~_u%&k!^750&cEnCypEAxP_Ju*v*%c)`GwC@-Q3#oDDxiq(%jrWe4qQp`E8#3;Tu`F{O<g|6KWne`=9!Y;Zf@Y;8E)X;8E)X;8E)UhRgSTQ;vM!H}#S4`-aQ+eRE#&eIGpPeczNL-}g;@<omv<zkJ^}<;eGa({6Ho#?(jL{|*=Txl@j~&%-6_P1E(P^T;c@{2Jfz{0BU|s|fQ*o-{YN3iR8p`8S(A`K{l;*Ph||(x?(s^>O_-7HWQ?cDkF}`*U;t(!cV!y|s|$k>F>XKXfp~&BM2|bN<*FJfE-HX0kr+rJAp59#`GNgB!-8KmHVQb31M_b89`n|CZc4QI|ib6!*uo`BL26YWfG?|7*E_MYhFE(Dj_#YK7*-zD#xVK&2kcD{=oaJa};gmy`WXPyWcCW0)7X%JbfnspIr<KN-R2o5}6$@Pi|n_vUuCawLuWr+#F(>_-k4{m3at^drM%KXSO}M~2IOWVq}{&T&P5aq21hi*sE09C`ZOSe<`l0dAiUrt`c4JW{VH^J~BGb$M*e7~NjeFg~a8ePXzME1CJJb-bR_u+3<F{Q6m#59Is79&mpYasP~od>t?H_-S}BV;b|wr`#|4C6CbM-#@_bmFH_@diX~Nncv&5xmC59=HXwlo_6$KTio1Uf1UZa<#fFQSFa7%`KLe2{7TJCH@Dk&XFhwMhli$><8sd=czEEu^2~qX{QlGpnn&{X=W<Ro-s0x=o*B%Cmfz*(!7B+|&Vfdr{MO8N%m;A&?P2l5bU8mw=Ib?-?|+A1n1XSG@Bhe$Ihk+zjoa&TtxPu$zi@|n@_rBZ_e$pDo{jf#yVlFh@9fn)wBq;+x_$a*LHjq^;^x+{(#+rB`Wqf7wV2BZCwlVxt8ZccZCO6wzjA9HxlxMGYboEih6lHoW1hkHZFo}CA-bHn`FtOa;QQ9_$gIW8m-2lZJe^hZ(1W$y4&mCFZf*@)&wRuI4-XFhoa@=MhKGkg{DOHdZXdh&`-AoQ-g}+P$!xmC%_F||n3v)E!SK+WZ@HW+4L$h-E3)wObS$?|sP^tb`npVcgwLxM<~fPC2k3fU#r!7~^A_+(mO0F~bH9u9yVGBnKduAUXTf8cZf>>c$h^@(4-YI%;QA~{@aFGPgSq`K-zQB@X&xE!JeTu3_Y1>=6UH-tncKl||AhKnPTq!|{Gl>Wf}<Ty<q2qBFE^J{w@#*;+c9~VUq9&K{&OR^oNwYiJhWyc^Obw}`aXWJkG{UgOK>?MzRwM}hu3F*h3jv4sN4iDCz9yNZ&h2$e7|4k4_9o^OPAlR;cJ>-<@R@Yl|<&*!#w^Z=j);Czh^ez|M5Hy7;dkfgYo<{kE`qMb=U3Ozbf-*(2v0V)oWlpK|d;%@T{)qt>t`Q)ki-94=1f<-W}urg*5$qwZ{}?e*X$TFDhJmn(xm~x&GVvx)^S?y~;dr$istkHgfw6jrZ{IkDHhm<LhGGSgd&<*LPe_N$y{Uhu_Z5`HEE7<>uCB8C=f5L{I*}^&`xu@pTFH`|&AVPU0(g@8Eu9xWDfb=0Wa9R+e+^bot}sxIT~b`8vE^e&!?iItEWvY_5;H?GW>=hdexd-~iXBWW0yl^A0jUyPNOZjdyL`Zn-|-at3lc7;YE4!MriIgW;hG$I+gNp8VE~FPJ~e?GX8Mel5O!ukySo^LnbAhfb|#-kaAMocswR7HC~`D8<d~bCa0wd@S9~!}n(`(R_SWPkw9Tl%=e39v+$gCcpPx{nAsPK*?jwZ|3vV$F80Q?SuOeJa`{`N!Y{f!8@6sIOOH;9b-O=+u5oA@GqFRtKexjd(a7P&#dvDa;&;|Kiaw5TYk9@m|KaS^6ld{m_NbSC9vycJ#KgJ{MK+ezje5n-#X=p`K{q{e(P{CzjewH^Ht}#V!rB>Bj&4y%lA9O<@=q(#rvI8j(ESbyBz7Fx#%y3%l=}x>@SAP{$lsNqPgtXhRc3!xa`-#2i3cAfAEec4wvJ}mvwsT^2K;%xE!w{)4tbSj-Q6h@zZcQemdod@iUxSqL+?~ao%t_&Kn*z&Ud+~xqQBa*NpC?<MKHL9`&5c8w%*-iszu=@;T_wUB9nZ@tie0>N)$_=_Gwz@f>%!c#hlO<>{}vm{%As=M{#_d4=I}Ug4itlgknFAH(H5$AACkV0}HsJk4-9PcvN3(+rpMw7{DchUmDMPdZ%88?9O8hU(*rd92}b9_#<*$_x5@<$O5lk74>aVjga|oQE4O=iyE{VjdnSP-nP~i}wY?quvV|_0?Ryrx-5ZQ|$dUMrtnKgIYDxT)qeSBfn@a-^&b_?`4L|_cFty-pkq+8KuulygwQ)-xC8XD>E1GtqvFOt-;^E)?B_v8!q3Y4VUlHhRgTp(9+l!bvfdF-*EX}AHH2nbGgo7xLjw5y!sS#v0f3HS9pwWPq7|ixLgkjZHU)Abj{}btvA1C8E(JT9Q}*?OQ2Wpu{ti+VM4iTjN^Q#_`Fu~d#mBWPrzI6^>FL&kD2Gi{je;V^NV#M!{xe=UHrxII{y!kb2+0DGTq#MzBTjJ+|JgmE6m0EkHh8q&#upzi*>EYr0bf?buIh*y}VCOtRFgDtRIH%mYB$Ku?`O&wGMB%T!%O1$aQ$|sC9V5<vP46N3Nfn<I44OQ;u9e2aj4m2aj4mH(aitn{wp*>O%2Jy8XpEu;FqY*l@WH?35$cfkVyDPu9m1>(YkHb?NZD?o)MKtcM#e*TW5$>*2xNm8R?Zh;?|wqt@ZiSJzyw^BW$u&Ofd746Wkt4u;FWJ6QXM&Cy)^UCD6ycO}E4*2BT0*24{#>*1yxxgKunBiF+Xm+RrC9J#)2jw{!<O*!IzcFtGa&xXtU+2Qhj?pAWHj*Gt!8ZQ4nXt@0Qpi_?c`=C|ojBZEy_e#U%-z)7<2YtQe-$M<Te-91J>dg69-ebOeBfnoy&adx3`S;dHv!a@ZIu_!7k-cWRo6Eo3+PP{j()q>Te+`#^|Fwciy4<M!3E)xt6HI=&KLK3sPYC`!Ky&%`R>Nh#FkJQv!)3oPT=olxi+<shBl?9?AF)5d;iA7dT=W;Ge9>Q=`iTDGlq33!(++a~q~UV^kKtnffZ<X52ga?_>ormPSit2zmT<Fobi2rXGKR~2GWL$0+>RMjIRDKH>24m*sLuJ@hL{)pi~F0{pA#Nv>E}=|G>6k;6VlyW?(+$EKEux~v0un=xnIaGmRHv=YX6eqa{m%|)cz&#sQpV7*YkKJ_EQ-y_frM?Slr*lel5f0ey!knpXUDEmpFghbLnm__k)GcUgP|7pCNeEK11-ReTLw2pJ8~xtu_DD-wlu2j|3jI9|=5aKN5J<ek8-?ek4<l+>d1HBlja2F83oDF83pu^OgINz@zpfnR4WQBvVhhAIY4T+>d0+k$*=v^%46CopzS{lnj^ql=7zO`$_IowUaV6kGxo&>l>_^?&fm8t37`Ux1-oMYq;Du8&2M%x!jlQaIr7fUVK3JE4feDaJf&|;bNb#;c}m_UH5t2|K+}A!{xqZJH4mofnW1;{%fbW-xZn0`?<wFYQyC|YQw_~kMh2E>xd_RWZ_xnbNM?LyUu%>%YEGr7yG*HmkVvu<;Z>G;Bw!1@Ih<MqxPkP%YEs=;~lshx$hlZ?t2fPZ^H8<xep&aY9Bs$)INN0xeq^(+@8-{d>3H2{4OBUxC8TGG0vZSEZxoJcL#xePjWrw_Y2_i`-M<_{vJ_&2N7P_gpV)BPw=Sm6Fh4C1dkd&!K21c!{zvC%8}!zsgE2d4VUAjIWIX*f=7*$rW`p=n)=9b($rs$lcpRwPMUU;`>XRm!CZV#WVrmEC~_M4#rH~v%kPyU=X-K}#P?8!M|}@9EWq#0;(IH@qrSKLaue56e76-E70dlwd`D)u{Ep0U`5l?V#dl<Zt;4u{@m-tY^1HTRn^9bj_-@W{`Q4n={1lfXzQ41s@;EBL*9-P9$LArx69kX?P7plmJ3(;youIXRCUf!KqT%wp#n7%9>HpNP4UgJ)3LdrZ6g+CZ3p{GQ%W%2gWy+E3U8X*Ay~}X9-et~9?mGpK+IMQok^4?fedM~CslQw|Gv&y2Gt+MJJJY}UIz@eN4j%QrIe66f=HOA^n}bJvZ*KC-@6Ap5@_TdesPD}Um*1P4a^&~shRg5G4VT}WoATxN=H|TQ_vVJn@6Ap5^1E`w<#*+#edKrL=6cER%1t@)yK++>`CU19)OY2k9Qj?jX$SZH)5Y_zEtLEHn^P03S{8+zRv~L(U)MjiK#=}3`p^H=!jQWEU;orX!v=N#um9A-Z>kQrRrnZz`~_+z=&#V*@V~+j@Uaf`v8O=(H1rJoY54y_zlHxVe9jmS<Z~&_9m9G9apE@+$iELg15Y{#K8MPmO@*(0tk-?)DUd%2Jpq3bzMl#|s&n~Cg(M#<u_UCOfRBygV|;^SQMunBkUs@I34aQ{zY1rm>*E-tx8Q$*r{j?J$1(fkx8%Q4;hGBXL65_~2j3SOfd5W~n<|`xo`pXLKLk1${zDZ$P~ipWQ20x#J{MKk1$_tpb-Mpm*aDpiKTCy|z+M6;zgV@^t17%6!+r_kew7xdy9{eN_%kY;Rv{Dmn#-R;oHPTzhAJyTg{;slE+3EhDg6FB==bp7!T0g8QXBR`Ab$*c9R3*mm(XkQU&6=4u+lMOaO`;aQmXti7QK40mWIz~aavwzN%%~h-wfz<m(M_)beb!T^a*G?m!F0>X<PVq@TH+8;prMJQehx;fXgpLoV33yjkE?d!R7lS-XHBi{$DCIQXvuA5T1A*F!GNePW^@Y&sOLgF8@B_@8iBCUmo{TerOzgGVali&<^k&;mbqI!Oz0|+X31hz5{$YXj%9zxW|`5Uxi-^KLk41<(D8%I>?nq`WUpf%MU`Fv?e?~N~)+(6k5dPD<e)?7@o#?8q?oKAiu+UIPUL&Zik<*!aNn8f<Ec;a}g))>PjQ63a#SuT@mk!I+5S5&fzT;RwIyK1$`5qbS3<1=tu<eBcLncNr%Iagf>JV-vBxsp0qyvc~z$mRd@^fCj2id{0v6=0sM#XZ$h`hS5l#(3WX5J7lc-TCoKR!M}^rcbU`5B8Tv9jX(#wD&`JoMQFdqKsR*qAzfGOnRuxu2m%IEMh?6dJrI8MUz5qWAz8<tL{Br#E1?W)t7vSqc>%fn~wP^%x2)`qS?};_wqj1effvtvahwrCCk_y$K)!<W92&u3DobtT_T>!rTd0s)7kGxe;PG4ved=m2X#qT!ZcbmY;FGRWhq5a@9QKyB_1@P3DX$-9itpQJC!eXQ^MjH8ANY4(<22X7}1no=u7(89mEx0B_kZ&n;8T>NjAwL|~xIVNVJoQ1khgO19z7^1w@GFsre44uFHmfj2h2kodP@xsHHGC`h$<QhAQ}A2zQxR_iZ4IAp@iC@Cr@$}3nDsRDDR|-w!AM_$Z;SFuLLY^nhVt4%+rVew*wdg>;py4ww;n!Q$<y<<J+v&;4<EGnncW_0^3roG6X}^q3!?8Qqfe7|gzt*6pfa=){9KGFU7=m9hvP2gDGV(H-w9<_fR=}^0AB!_AHF2oDlaq#d`;ZLbYIe3j-JgwK!1e)0lqKh-bt9d_QhQLJ?IJ7T=xX#!Y43~{|bRT&G)Wj-k%l6t^wa4eJ~zc9X=jD2I_;SXCFNSwnN{7r?H*pBHN%_;px22;JTf`H6u@R&Xc%bPU2o6e?o=#EWT$+H^W!MxMM*d_}K5X_}-=YH~EE#pF~;d&@}k!7_;bnzVOlBNG^xehw^>ML;l}NF01e^bPqhu`9H>SN#BO2zC?Yh8nh~WHTYuCqVUvjTH_ueEdl>1d=6-KmoJVuX*T%pRsHj-`sPz%x2vw{D!y5T3<UD27?Wv?UJFfuUkkqunhL)Tem!(E{CfC}&~*5X@EZ`wry-Dk4VnR;Mb(x5ZNse4-0)f9W1u<VW8i%_|7>U<QVTu@d@R%l@566n5y<C3ApZz7H+*i?=@Hz!vn(ESs2|nFbB4w@>fhAwX<lxg*Jiw>dxM^F^h~37h2g3a?N#XEV?Pn`_V6|W`I^wV@HOEpLl?nUhA#<S1y7m+UlKkJfqZu8>+qy+!IN4p{|4d~d@OV`d@Otc1oEY!Yv4=6SA{NtC!G&p6}~ofGCXMu_!fwFgpP#o2;W<UHY$u#p*xh~Q=pCENvp$8fqw;B9-j17moJ7m>00=;h^ImGz>~(nlWukS`xeKy!f*F+AioWo)yJL!`E+Prc+wK^r0ZP1BI2Y=;g=%50Ga?#+7zC2n#;FCoOCq&XvBM}FkXe_Dg>b$T>fpuN%y(@$B2_&fnTA*G8Lvn$HDJXVF%K8AdUPb6)qtC0@BFORAHkEGob5T{xIUCdtLq$#7X}R|C$P$R5%I^!_PumGW;gQGoVMHN8w*W-VCV8yAgUAdIWwZezOs3@@_)=g`xZ4gGieNzX9>}Xr~#_>F|5ePV1p7;Qx&_-3#3XzZ`A*HvBTgm*d(mgN}p$OWn6+mHq)O;_{CpPMQc`Mg_kL_bk>wE%uF+Z;AAl$V2{)N-L=JcW7akua7usLwGty10Vf~ntdYTcP*}0A=Ix3@?5hx?K6x0ABg8ddOc_Z_?xcuyC{$Rrzqnl^e%i(q}PSkgTLWQzlrk5e`0Z2H=sA+3nINfv@ZM|SNaW<NB#?o%en)-0bdyHN^MvM*MU5>Un8_(BjhQJYgZQ6q%5vWOI&w982LXD{}!GY`TrtL&w^4uepZm?ho@)Fn?8QFkZyr5fIP9#9KMIoAj-2Dn(BM_Orks%^Z_OUn~`S?bTzz%JlUbyeC*dC&l2cjcuJ!@anOA5OOR(ibRK*h@|1)=3O^rtCPOE|)BNB$AI}j;hryS`Z!1G9!B56-M?y!y565pOLMOmi#&2svYrv1hZ+k;~!B50*=R)WB9?nbXw>GpHd~f`=BeVnjT>N$sbRoQr-?oQ70pAh7Z2@f#zX-ow1zic>9>47YeGa|_ep?$_3w{-Tn*t5N*G8VI&?@jL$n!ch6TT|)l!lgqe_YM^+N;nK`UHHX7*4AQZ3$lzX^%oH!V~{fmG_sA{iBHg2=)W?Pxz0Jb{_fz{5R^}{#u2j&?E36=qBh9_~l4j2HgZd0cqo*%ixD2Z5VVs{9vRFf)0bH=L$W)X)Zv12jaKDeu7?rzmK%Pp+CVBFGch581{d=;+0jX0$<7%Cv6RF1y5ttag0->$6P)Yancm{mGG(XD-b6?331YiE<X}+(h>00d_3>`7ql__7!}5<@C@`>_?K0fjr7?_Bi~Ae)+#&(tpooIe%lJ#8h#J;D|O!QLOa5Dh3^9G08jUDSKP;4!Ja^#*2vcy?Ma@laX(yt(*E!?m!@+r=VM<T@nT>_;maeQ+sE_iqR?XSJ|EAgb3^mM|84Ocn$k&QkT;8u=g^d%6=~!j@$q~*3p6WyaUaj8AA#nDuZXk?@FfsW0E>sOh<Fnp&!^*|3GnZzuv3NI&^_>NeLTl*0&NPv8+rCa55Pa~<N0`7Xgm1*$a4^S2>wMM&*Ptm_Jp76<2n9|zK3&t^4)wqraTQj4^QI>rF{*38a|@JS1LT|V|~iU{-E-Qk$xC?$gfjjgT?6^kVby73a=vlRiu$0s=_Fwk3t&x=TsPg^Z`gC-%^EVkp2wP$Ty~XBfT5a$Um;avq*myY2<sTFc9ejkw*Rn6<$R8i%28CM1`eDUy3yH>s8o@^o>X(f5@WmWjH;IH1c1na2@H_kw%{8YWI+S4{79YtG52d$Mbs9OYj9%pUfY_>7<lKzMS&@7*6*i5Bat#w20yK7Dyxiyb7I>-Wh4+N2|~W>3xt!ev%3Sqz8~j{zVmfBfU4$$oEj86Vf{&jeHvwnj^hA(#V%pp$yW?AdP$h72=Q{hcxoPs&oF?$LXYT$a`7&i#|@jh&;dI-lco^GV~(+XDW12;Xm-55GVgR;-sBj{!_$ByTUh7$1blzQD`CfJ1XrD6^g{L7LR%8?;%cFBIcq09dXiPG3@)Qd*XQ&nn4@5d{4wl8^ZU2?+M=o@!Bf<ONF}77VvcJ#;6<lW{8)7FAi@bPQDo8q)p-J*!561@(GAH!0{8HHC(<4;-q!pNt>g-%~4nKjdA>^pxs^GMx69H_@?kSd^g0YZGS`ik`~5!)I+@<gI0I>8i<p|yL=tQ>!6P0pThCSL#Mj@bBL2pbNOzFlTL)EIu%CUNh`q9vFoF5<ZB{c9mlT;t>yBy5wDGFPM(fE19c-m8}X?){%q(R_=)h-;AbLE$FNZc@`;Go#Bma#ja<Gi;-pRCNxQ2MfDVDDW6wg}$j?Q5HjY0RI?v^2B2M}eyp7{0L3_D;Bg9F2yL?l`o1!kgQRfz5El^kTvvB<B&}5gNhdAlWF8>nZq(OLU+g_+U=~(zA)N34cG<<LPUhrcO55V_^AB%VZZ95ja2%hRR4s|9!8S!M)Ych0-%LfrBod8eTQ-!CY?cm3uUTdMN;K#s^hF^{N7}RSubPYVMpI!Cw8XEa4h>t_Po`gQ*@>38eeHMNKys7ikh|{@@0ULvJAioy%Iso14@~aWo^>g_(h?DMz*Uu7*pEcyKSRC(!=LyA0|6@J$T@fd}YO$wh3_WY^(sQf5FQ!nI|JVOT*2Dj3oze3AA7;s4dbfMJe>p;x<!t`!(mosg4abU6|D%afS(+JH{{t9X?XC'

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
