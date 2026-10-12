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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_004.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_004.stl', 'source_sha256': 'a5954c04e6aaf6f593ccdc72ecf46e82b9cb64b399c0cefa4a671b1a081807f9', 'input_faces': 920, 'input_vertices': 723, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10081617534160614, -0.08408977091312408, 0.10268881916999817], [0.128603994846344, 0.22225421667099, 0.49999991059303284]]}
GEOMETRY_BASE85 = 'c$}r31#}ci)V6zqyGvMPfQ6uoyEP7ryDt+UI0Ow2jRh7bxP?g|IKfGRrEzy%bYQW?-50*xd*8`UivG{}&-d*)_q<QuRI011tE;Q3tJ%i&;>Ay|$$vSuc7H$VT&ISnQ6$&WYXN=(2KDIdH}JQ<{f61J)a=uLZk^MxMT5p|Y+8Ue!l#Shz|I4F%G-S^b}j2u$nMkCf54ytzI{9T59s1Yel6eL1N~zBf!%%k`NjO4uT1e0h3qBr7qXAC|1bYb8dC%_<JqX_7<G;szpV;sm&3<Nbv>GWbAGJ|{<&K!_RYzS*mun+yPJO24varW>Z&_2lKl(Cqv>aduMhi<$QKdpmwC9A^C_NM@_BBGzk2yj{<&NuPH*(<#=g-!a6kWjukT0s?+(<K^z~-!;^U2tX5aBKa3}fp`&0L^U!oiPuAoyp*w5CIkE<n`!TD=xC$VpCDZ}||<?3>Jdy`S@I~OG6@@S_IvF{xGX*(ac?VBhr$G+m?x2?{;{nDGg{P#z19%28-sBP@;xweJR=WKO8uJc(J_Vtx7O+McgM>)MwEGhfW;bV93&&dKL|IEX-@^KgR<l`Ex?s0mp!nrN%@9e|JH4@BV-}Lro-+o{KAJ_hSNj|RLCL{ai+s%Aj{mMuw=g~2nIeq;Md|Z9CA0Jn<AKFB|qvW?pu3x|NoL>KYDV)oHFY^jccVxpkKEA)nzWK3|)bIJRC)p33%D!W=P0ATEO3rs*UG|L?wd8uA*v;w9GpjaoKB?+Uxl_JmU+X@Neb=U0p`1SNXgThXUhF$+=Hv6#n>pn8k2*;{A4c){YEAk`{fu&LAYUunP>!20%PH19^TmIfi1W9XtRwl~|F)j<c_!sCZkOluX2a*~+p`|o&h=Py?op|S6q0^L_SO7z=WpkveI;ODuTe+Nt7~I9Zs&#T__(vyb3GfWZIVxTJob&QI;XeKZ6nA1>%v<0&*x>|+?z=1&3734j@DcEaJw(CL9SP?qU@XZTCd`tH%H2OMQV~yNGWNTjao|n<FBq^Kf$-noX=l}<v0bFiXYip>a*=4X@})cuIBtp28D4uY132AcWVIq`s=P6__*y$o#*4$NyENYc>&j(Swxfb3tADz^|@vQ*Mt3AU#<u9x6JGtm3yt{e1E+o`Bw{F$?f6vOD?CqgD>|d&UVY#cMKmd^^iZawC5Ww+1H9S<o?YpnVb6wy-Z^EjfK_Zesq23^Kw*ax`O@SzUw&OaU=M+X1%iPo4-wxekVt&)BO8)i$b|P6{hfc>3PDW-`n*vgzF)f+*gKc3)i!~U2pbXtxj?I9q(Rp{`Qx7*th${=YG}x?E7sl|G<pwYk_^ae#~~6q~20}akBrqn$*|Vnw-DO_JMu-k9d4vn3D>fU`>>leaFxMt{)@EUOA7>Y1lVcz2fp{M^p0e^_~ZpbNb&0%FhQg-r;<ngt2dotjP7|>bzKvZy&<Gp1a5bu9rQZq`&#PE|`4hx-ydg?%`6OrH3!$e4Ynzy}K^W<@(fac4glgwp{A-%1FMxMw7=&*{|y4deA3Um42nr0rqv@8bO@zm%{tyz7A#Iak#Oxx7knlxO%1B?7L>Q<iFQ~GVpmBmo_ct`m9z{+PBXqxlhZLW8dsCL5|z*t=z|L&o1Qj1KyA2bO~*Iy>zcJ?Az~6m3lrmSNf$%JtTd2sl!}9V+Nn$a`kM$zCN!O*OxKFPtx})%D&@jIc~4cBk867n|)uv`OjU??b*?!yVPg+arPbk?OaYR+gZ6^4o_g;<-WczmvQ?t4qlkg<w3o<-WHR33*NxKWA1S|UuQ9{C;h?Pd0ft0`}z5(+s{h9t-L#z>nGF3gWN8=)jP|-Uvq1&wA&Ad__&qA`T80I_s!w_3ykFJqFwXn@|X$2*mpKr6Cw3-hx6Cg)?{Bh^{yM|+gs|{$mcEo)Wb{p=ajX0+@a@=&%W{L8J~|mLn68EIc^1Uz2)i8`D=G-h~KW_Y)=2U>^%N?yN!>lKhMR!>77x=KVvS6zw@72p7rL;SxV~dpKapr@5J?BymQF)ecF$G*TXl`&+pDD?XLQQnVkM{hL)b~$H>;7eP@1eNuT(Z)bqt(+1LA(UBu<sKa0;-3;#ZY%lWS+_gj~=l77<Z>7LhJ&s12(YlEYwar%ynWqh?Z312VcRD1R{|A?8K?$q1caeUN|nJV!ePhY)`#<+;7T%S|qx|jp<b2*KdL)bTK#pCmEWjG`CZ)}*t>CgG|@9o}Yq}`^S!@lX8n6Ia~_A5U}wA6S1<oZcedkO#DwAWJ4A$`Sv)=RGM?W<DGCyCiN)BZDwwX81ZTWrN-J}>P>;b@QgH(TtRWK|FPu&M0pwkdpFT*+?8{g~8S(s$U;{iuHNlH_j=479pl=Hdo{p6$(%Af>dceOcHyZ={cN9rc9mCvyG+BDg&|!be`@d=^#{zh1NcTyIs<ay{trn@r&2cDcvTE9Zdr(m&)$H{SC4{yTXrm#0^})p4#%&$?qR@6&A+$Huw7eNxJO_w9<o`G5SgC*Kz}?@RyLZpkP<uNpadT;s~FpZD~g?~=>7AV+dZ-)iCrt9mn9UL4NHz41=&gUh2Yv!8Sl``X0(aohi+MC?1Rg!6buuh&|hFMqcfChhs|ME<${P8qNE8x+9xIHduP2VLt|aD5uHXAb7$rs+M2(|;Vx&r@S(d-k=-TYIrq(4;<V&mP3bdr_A2)id7zi~nwBLG}%Y^c(h36=eRAGwmSH`^(ufi<JLM&_K)U_1QIm&#Tu<9!G1}UP^n*9xncd?lRsCd?WYEmbn9@zM66UYF)2gW!-#_+l}F!T;@L&+MbZ}8_B*FFi*xYUkcph{KJci->jC57k_`w^{=fP-H-Dr_)5lGFP6)7^eryF*LNAG?jLoD{dbw!xBI2%`^ag#d&kq)rtUo~?dhE4SMroU`?+h&Jm`(gCu03}CuE*5^90`)+J23F`<7muUfX!(j;F7WS-|O?A2Le%WJ~&TIaeLy`H<!nEd5Wx?(FMFi%I!&b-%#=ATRbc*CQEMMWz-%dTAfd=V*C(4o4ln>gj8RmvMSm!zj5f_j|B!CcZ55i{1~py=nR4i=QP*=E<q%OL_7-rJW7g*M)!oqq~e#!jpIBau(~$&spc>I$VF+gdu*Me#4kJ?NfVqTmC+u$<HZm(tLS7x4qZNsvT-6?)zG`!&tvX8hP$Fc_8@}Y2ff|=f;mZ(#|Kx>&Sl9ZG3;}&BCPKS|)AB`E1<A>0D1YO8O_2+j6=F5r?FGzrDr2E4(?UFY`&}!Oh!CeP*rO+^St^v+6gsY!4GIHR8Yb=@hqJX=lFdv#K{O#iz<7@%s1Y{QK>fdh7Qv7yn$Q8u$Os&%Lg*UuRCqDpvKm`9=9ER`qEtsKdJU3(sG5duwT*UG_C%#dt#-*K$AZ<7RxH9QEP#10%&RQlHrqwyI)P4|<u_+@7=w(oen$mib(ySDPwU^;2Medrqg0H|G0x;QDg+|D`YQllFYDBOkBOsJQhB-@Mv1PXDZB8`6odH^wK%xw^crqvg2Kne?Y|MH{U*Yvr1}KH;2{l=~Cy`L{ltf2&r!9-|%kOX^|65r3=l8-btwt;%m43h&2y&(7ltv&>TN_w;9X`dgLLcs_f8RXO#}0|(1>t<UX8zx;#St^R3mfK_`i^`t|r+Jo`gpM8CKr;VH*<6(Vz;-Q@GK_Tw1T<x!LJ($}j4YfSq8M}sBov;4wBKxjK9cBGw$4lvlYuktM&yNFnJ<OGPp^P`aml-bYG^MP2{P-d1BbE)ftRMKsDL-Cc($>G1^!?(E;PjdI$~>awQ)v%TjYe43XWkwotlG0#|M3W`cB}8QjpXB?|Iv5%llvw4u`!%~>1}b^r=w73gY!w_&*y7ooXqv<3P{ZJI&*)d)boN+e%`rCmY%@*m2V~Mi|L1o|Lola%ldDda-voJn`wWM@kgG#PX7IRZ}Fcukn~ly@j9FS!zuIcbc5K}3svIvC3DUKsh=0C#IJRN*DK7zUNX*4e_H$!&BHmrA7OHTz5FrJ>U!B%ClBPG6IGXW#6EqmaQfG+11;~zN=YX3@j6wJb<;H6Ilb$0>ZzQrRbr{P@Y4Jo)VEd_e|1jIU;pUGzBwa+eaFZ0yxwVq&6D)sX0mTQeJ6h2KuO<YE&KL>&D`%fRtK<euXR)MpXS5m(NndSd~W2O&VQ$jKV3J*h@Y}MuTPkrdUC&Q)O*9eIv$SomGP49^+WPe<|%I9J)Ut6tswLIsAMx()#oOB_jB11&vw|;cR$~aC%?#grhjJ1M|o}<dGoLzJ05$#MAn_^*OUA)-f)KB;_-&dtF`#byv!NZMSSIXVfPs=KE@~d_L(wYxHCnLi}8;>`H)<%`YYL2$E9xHJuY$-+${CBYp<NIGJkRV?s1p#F$wqcrq5L=Pf&3lr@0Pxmj2)M_YBMXy}`dy&L0Qkj02thb94V|UhtN2GRBjx{6%M4wSTQ)%b9ZjDDzggALcLPWQ=>wfg@*H-FN!kdD8DI^GCDcrkPgvuVc{VnO66^+cz!_h%-KS`oy2b>6Ly%8=sVYb=+&elUjUboMx2IB)-xwX={qIug=HazS_Up<Cl?ql>X4QtGbj^=|5wAW&Yxr(3yR8UT@y%AwK$lZRtL~FZ2fEk-n(B_o(_p)~N=pm2xWMNw;rcyyvLBPVVE=o1{F-{LWS3xa6NO8PBuLLkncx_swPYT@gcheB#(&_o}Dw{1Pnv*q`;|_(tPm^1jI4Fs{GqAoqv%h(>Y!?|#y6k7*jmk13FxZ|xRwePx{KY<N@h8M>RxskiEIC62Gmf3<b@B%gCX<UQE)ewX9;%KX}q;2+6nRyFRQweb_=zHq#h`c%dnMy794Kf6=N`=YubXXHLiHCxINcb&nUn1Ow>UsbLLE!{*ezy0nn;+J0>XFjVXtj4}Nes=iQ5nq{in0p$sudYA1GPjWY3q)`|>sz*nUulH+jXQC_r!{SU+S9jZtt{_V+9u-i>x;%pdUc%Kc!v1u_!hpp{^M9bSIVi3lg)%nBt6EBdZXLy+xM-O@+jjg*P!j}J6>Mn^-Ftu>Bro@I$n+SmGQ0HH~J=6!^b&$Adat&Z{5B+E_M4qjrY#&vP>WAE8|RO!Tpx!YgE2uSwF5t*DdQa)>p>2`g@n<^>X{_^>Q|TB)&4PcKbh-AHLd7?1|q=KAi`1dvgXhI~~VQS};y~Gdh2<EWhhqx*)6e?3ip1vTFb4-+6<q?xR>=xsQy+C4#KZ*G$|%d}W=}-lbWP<$dk;mHXO=ZX@|9{e$B|Z}Hb};Qquu+Ic39uN+tVbC{H0>6hHTF@EQwXt}TWxQ_c{#8>;bDuI^i-M-pS+LufdU+Guf{!i<WAA-bJ`|YNS<h_pa+;RKrbI0wg&z)FbdG5se%5%r<tIwTSUw!Vl{ZHOJUv~P-d|3-$F8){l(VUNuyl0H{mGsUb(Q>`ib=QlBCB3>{1Ydo=8%rNZyPEly%Wn>T&f^4!UxGR8E8_~&OeVfE4slE=$i6zBiS?E7jQOA#`#;UomsMt89bdV9b$q37Y9je4<1}Z|*5WJUI<xB^;w$4oBU>*ir!sDI78xzRI^Uc+LGn??pRQ#KB)u|@bv9oq<yXeN+U9la|1>|%en|3H#@n&JGTzpUUS<EM^#u6pINu0<CHW}x0=>n*l8-u%*b;9p=cCL!%;ZVgSLZMG?y1>V=P$;=jO_n3Kgym>(yQ~MEBV=1=UL8TMWsB-yv*^qqWH=@&a7Ttd}ZDj>nrm_ZEJfut}?H5r06W=ROX?vzB11>yZ4a%mHBe4ugrhlzB>Q4AM%&-DD!l;ug<$;)2s9MR-5Fw$~u7a>J9Ogbpv~@u{^#}*BKnM7PJ4;x<u{O?5pb-u79`5`#)vfL+gE7@>kYL^y?4BSJqXGRXusXg}M%7oUXRes{K1(cV}N+=P?`jFSNSv^xcyeTHU|)GfTu*`T@HuTzsY9a5Ow7$5r|z!*PRswI9<mKbG|By4jg`lE3<1wLo+JSzVVilRRC_s;uK_n<_2g@+#|odbLqYtnPR7N?+M$psp(xAI$zw<5K4g@zr(sR!f#zT^BRO8ur!ko__V{Qp@WC|EKZilj}>Zu9s2sF8e=?Gh4k|YIPm8l0M7WSJ#1`lvrkUz3jEhv;Wh2a)`dn>N@JJ8!WTBj;@@2B!6Xn+ju%n(kt@?v&||=ugpj6N2A48->c?2BIQx$BaYr_gXQm)b^Dd|g00%KzVnY@%l6#&P_X6oeeo*T>N;v2k}kKpUfSI1?5po1%nqHGTi!2GJ(gSEFa80`t?JoWy@~yw=9T4NN<PYb$N6fQ)AGEE&T?9vmn&+K)9Sn&<D=MD-xIlgbzY;FKjO4J-}$GUmhI~G1*g^d+B-gTTHU9{<M(o0<@xCB|HEl@|2kTx3bDFR%{!UdSLZ=`g&ZMP_o-$t5@K~fYHQ1iue|SbWo#<GGJZC{`i5BDclzP6Ay)T=X`dWobsuRXXM|YYFZ!O9?5poL^?_R?z4AWPJQE?l^8VEMt~Bqj{po#cqTfR;uglXmp;q<p^zOj^PviOTy+f_8i{3kseRUqHzn>}jDB~8_zD=^vSba}jCrW(fy|%gIg5;x)bN;>@YE}Qn;(MW1^=!^g!2O8&Uf#@-YK2vO8hy%2zoWeOcU~C8zL7}QA+>4_881DUB>5}*3iNbS#aH$r7=33;KFWRux3BJJa2;PDzOpaE__$cgsqCZBn}taJ%Dlr2U%kSrJ-B^!|Atv+iyT+k2V(kd7hl;oqVM0e!m3@leRcnd`C_k>Q`yI&4?QZrvhPJ(bz+58J2WD1N&d?I8KdeW@zwn{pWaIT%6Qc*n{*|oQ|Alt)p@0nEz3%2KNb0YabiBJU&_1Es(sp{O0TqRpAXBe^lbm`{Y%Elx^i4)-ffiYEcqz=qwMo~NIvR%^0aB}y8^EAbH}|tqZhk_^2A*yaeetN^)Rm#_lE}7yR-?3c|W?kAIy;=E&D(1A8U}0{h#LPu5RqB<A1Y9f5|^^mh97auiqw^!M<zwW!Vqso@e<!m-OnsxU&g)U%tAJ&h7v7zUiK~q*vxUTJMpotgfT^_et6JugpV@CJ)5N^Hd){MaBtr67%>*U7xhCOewyyKBhOVEaM?%zoK!YwtWAf>~A!Kny<F1XFX!L<gcs)xQxY;UfFM{C0)7N>U^E)uCwp#JwdLYdw+|+OVX?RJWo87^5<#A{innIT)6dFd}Tc+)?ZXR?mRbJY92?b`%bl}LgK6IHs#u^k#?cXe-CtGUtQmD*6Yo_K6aGM>pzc^@?0J)=_ATY|K4zw%$FZcmT_&>`tlu9#>>+FgXhU{mHEEWB2@ChIMxgwx7X9xUZj-u3fpyQZ{x$(#A&zK-|P0Zr%?x3-Os^!k&-?>*4b9ok>~L6V{%@-uF8J;%hA%mUOuzNvOT+fWgoKJSML{l$7_=R%;hrAM?Y!we=6nqBHyjqtKUBE>1#I&NIiE8k^SoN3$Eqst?r}FRGEGA&!Y03%!9A;J%xRc_{x54ZRBwFwa|z1J)66qziO<tyf605Vqe_{?x?v~@)_P#p1&pD%6qGU%fwgrlYd(!<w+hS{cN2`S;sE0PL7N5xp_BC=IIkROFq3W$nyrzJFU?<$>&~9xlZo)%b8zE{V4m}T?0Qz{_b)6u7k4A>g+f64WDN6ymmjQDrMyPr!oI8Za4brMzX&yS6=pA9ZJOQR~zMLU)_iAN?2Ovv3`HZb;t9_`Lw3^%6@)_cU{RRMF<~HZ?#p%U7<~-Jj!<guFA*Q*Ei&i({H%4d==lBUhcaO$0h&5Ddqbmw14LlyX0TGhWP6D3q#t9uYB*I=b6I3`hA4s=KS?m?cWUBDftYO{i1r!<J>>kGmMk(vXt*Q94!{IAKMRPdoS0qdwiZJ*xlE$-B+1^y-C5o`kjaoKj%iz>*D^d#Bnu%eY5)wnFn3jC(nxn!#8@~U+(Wy96fhR`hPzh^sHycwX<?u<+~VHqa56h)$ef}or;U^o`)vN!}E0e=n>+N#D3Zeb7cL$>hVpSpZa}J`{Z)}E8iKJ4>GW?ewSp<skzy+KK1v0@|?XjTk@GXWECA(J8@O|*F{m{E8kDK*5f-d<vT2=&u#fmPcJL?Rqz?vpY!Y<`#*ip)u6)`&--0F6ejBxRs6(%;4SMz+YZS6b*!&^N2+{}=BW5hzAHO5llyu7`D=MU{vb7fXX{)%U&iej9!a~cnu&eGOWMDgJcZ0xa_wW^75I+lL(b(brN10~Nc=6k<h$B+59B#s>OA}Ar{nS-v*~ylN3Tx6-$AM0_qp0O=AVs2cV+*_jOS9$*G(jS-8=F;4}2l_-OiTs{qy-5Jg#=l$tvHKj0uo@&R&!2vvZBKyVDaSpVK$wJH_6wq`&DABIWotQof5Fwn_G-m=DCibwuvJGeu<GvRNL!Zyj@{^Ld#!rpb4FQ~r?q8S`snd_3u&l1*jbaF73A=8|$|3zqcX3&{P}?V<Ebm)33fZ0EYyFlpyr;q1F|Rg!uh`>(XO&<B!#nlR4aaWlKDtG|9Lev4^xzPbOEc3Y*L+|OAHO1rrkE%)ihLF_x*HRtnkb(t^w(1IqgZ{Jp)$Ip7XYLb6sJn1*fPLk{U?Wv5HK6$h6O43@cYs4aXkGv<l^k2=-aeDiFKbb!^`h$IYa$U-KJ&DX0E`_o0e&45m`7Hg)qe%Jwd{jmrR~y+H%l8!X9!q(`;`2U7eO4%^ca^ep|7-lwgY$Rji)G%?vY_<KUDn9^tJn2pJz!^j_U++`<a_G=zsmLb&`HLNqvX0c>h+fWeocEw{s+T2e>2Gr8Sh1evF`{g$=AVtzqPdMtD7Z#_2IJ4^v^QBFI_>`#P`W2&)f1D*tcJNA;+!zW<{KK{@Z);(;wpRVx4^#bA7rRYBEn=>MQ-w)M>Kry}hFJcdhF1_pkN|bz~kidWU?cT4DtI`lDdEj!lxu_wyq%u<s22Mcz;4%Psvy`ZMw!YURhAk2CFR_D$Pv`EK<t#;gDAW8ZP;F1I5`hqlrWrPE~HG;}q;$I(AelKl_9DcLti`%1rcD^Tj;Qz}WnW|Qo99{y3D%QMo*dU>royid?saF&c$n`M;r!*L(Y?a0^56`obn*NB#JQ|Vvj`@exXC4H_-^8M?Y^74MOYkn!ul-;tPI%7Z9d!|eJgQ@xZSFLgfsh{~}WWD)y0Pi2r-c^!)3ttDyKHRbE`8!dg)Kz)!yuX0#%R4r!D<9`mCE15Iw2b&+9k@Mf75B>bBU67DfBIB;zqGxAd<X5{mVI+ceg2NqvFn}e7tJ<Bo*SonN`JPiBG-?r(mY9@e59-^x^~O>?P##Pe{PyX=J(~xOTD!%gYS5<^1gVpKw;S*8^6AcBkIhSeU1^!WgRAQH}NYZmG?Q-)5<t{;(1xux!#(e+gjsEoWCRG4e?K3koouQ53)Yiv%EYnZ9{qAx2t_t9`9=>+sX5Ja3^^WTznk<{RBhO*P6-e_hzEUvfdM&L7p2~#`AN;wRM}+Tb8Uck6(Xk3a4*%f%A8i_$KKSE|B%ZrjuoSy*3`6x7QcQ-;I~=*-vzn?}2@4^1Q(Ob)xjQnFGY{_p99RKT002(m2k)LXzz8_~Fii)O0m1iI!gL>g(}OkdUcqTC7_C6C^!K{(t=wB;|@1{lESbBu{KHQ<j)Gh#-!JJ^)99_d@T3_kwpr?}2xNqY%V*p>M%=!LOkyy@X$blOl-ALMwyIf;&PxgFAwILjA#{<H0?_W1&mIqzl1g!6Tt_z$3u{&_BTe-~rHa-~r%<(Ei|t;KI;O;KJbS&{E*+;2Smx;&;$SU<%^Y@csa&24{x01!o4QLlCEewgRUDCx^BKCkH2nHU}pLCxSKwlhy?%0>?)X$AeY{#{+voD}ueiKWw7)z!bz9yqaLr-@zI<1+)P;1vm|~5;zSw8Powz2L9J3+73)X{M9Bw{0UkeOhNn}S_Vu(?1JV7QxNa8Nf2L$mH<-_zl632QxGSCHwv5t+!`7PZVm1Ood@m%9tvFv9txfeT@5Ck2A&Ka4IKj}9RwZ??gwoF?gy?9{mUj?AAHRwdJcRId=|P7d=|VXCe}kYK=*++fHy)-@J4Vr^b|N8ya{?5ya~J+dH}o`yahpg2zmj02z(KG6MPYT3qhR6OSFKOFa>cn1aTXv4kqmdZUgQO9R}_Vo(P=+o(NtGoe5qG-T<8jo`!a?0YSVSx)n@%0K6T15PA%J5PTeZ8hjjl3VH#23VaTF9!z=`d=7jDx*vQ7ya&1$yayZw-3^WcZ-Q<CldcDE0<VHD1Fr%*p^L#z@Dk{J@DgwkbOxAoDmVx{3pxor3p^b<96TL77}^6&S_3>7+y(m4Cfo&_DMoKYFG0z_gdjc)eF#1b-U^KXZw3E?AkGeb4$cnF3H=Vv3C@imE)UJ+C0rid44Ms0LEI7g3z&j90Gb|5ngC2eY}h1-2SMN1geizyL;nW123Le$23G_Zh3*HF?f@4B7lCdA7XcTBt^pSY7lej_3xa=zt^ofE&I4Tu&I8ViAohWVfqlUFpsT?7!1<x8!KCZJ`N1U+#ATt|!DYc!phv(}!1bY5!1clY&_`f@@EGU^@EGtcXj(7fS>O<8PA~=WGN=!jf_MfrKbV4eBD5%&f_Nmf9GHT*5Ht&zg7`ORRxkx|ap<pL3gSl4f?x{bq0rJ`3gSu73SbK2dC)3g3gX4k@?Z+$cF;m#3gW8J9AFCKGByd~cu*Udg802A`phOwdLB$c+zH-Ea3}D9n5YIl20aNr2L1>70{jp7GxQtyGdP2nsJE9eX-RMfa6V`=a6WKxXjgD?a4qOSFsUz?v^KaFxH$ATk9>Z^aY!?I95*A%Mf%0|Upc?voJgN~oa0l}0qJp%IysIyBdzXHht*NXq-QnZYT$F4XcYJyco%d%co%pBbQX96cs7D~40Jen3^)MV8yo=c1$BT)8-PjMgL{Dkpne|t_~AIDgFTKr808|J4klgeQRcNc57M0;=d}~(O?t+o9?qbis18Z{LC=6Gh`T^ff+>id&`2=p3NQt65Ofllg1D7Ug19Plr1sxEOYE>o5P!n&`-4A$HJhkEn1VP3v>%v)I2&{jn1Z+xbQG9^_z&oKFa@z6bPAY)xEpjDn1VPnbO4xwI5l)An1VPVbTpWP_yarx`~mz9IsyC+9N#872TVbn5xNOXL0ka38%#l58F~~<dI3y9Tn~B|OhMcd`V>q-+}<WZ+!y)+O!^W`LEH!W3QR%V8~PedLEOtGLEIDi224TR1Ns(BLEIhs985vn6?zX$LEIVY0#gwCLa%@+h#NwWfhmYfLHB|wi0#m=U<%?4P$!szI0rNcOhH@>Iu%SoTn_ptn1Z-DbRw97xIc6?n1XmPGy+UPJOp|hOhG)%CPDl+e!mC&H~1nn9DEUc96A$x9K0Xe3A`U12yFol1P_DO0S^OrgH{KVb^w$11$P4vgO2maXB>`0dcfnj2T(536CUL}f%71}<Z)h?aNeZ%J?h~;>WS)*bOiK1n1Xl|^Z}THcr^4On1XmL^bweXcpUUGn1Xl$^dB$<aUk>wn1c9En*{MQ{QesF8TbbD6!-@CH1sg|H24U#2lxnhEVMazEVvJXxGhu%la>UN)&{o)_kp(b$fqUpChg*JtS%@E=~9ofEk)T$cX*u34xB6LL637kh`J%Y1ExA8od&%FrXZdRjRsQ?FNAIeQxGqLZUj>hFM+NDQxGqOt^t!S0aFkML+61hh?hebf+>g>K*PWk#Pgx6z!b!Dpew-?#ItP@#519xU<%^t&=4@`axew)ROm7=1@RQ<A}|H<Wat7g1@U;B1o3d_TrdUkK<ErG1#t)Hd@u!Z8|W4=1#wg8Aut7TZJPw~E&P5m_!iiNjsTnB?a=Pv?ciW&6L2ti2=sUG5O7y$Rd82uJ7@(kX)7?PFSs4JD|DboJ_B(a(#0OfU5s*(Zu2PTHk=3PK9BR-hw~=A=}`|iQBPEdq&oB_n1Z+o^g5V=xCQhtFa>d2=v6QUaV_X&Fa>c<=y@<{4Vy6O2{7qVa7}O>=s|EDaARmRxG}f^bT7C8xGr=zxGwm2XcYK&u)FOMM?&v{Bf)o|ufcb~ub}h}?-hO~PKY2b1}zIN25tiF2yO!I2JHzZ9SbHM3GN1N0uAuUCjiGG9pG`?0Vo$~LyvMcMEOYzdz=gL9cXs1|IVE_5_$vmR2y0WdIMYmTpIcgOiJ(VO5<nZlF-ax3gTQg3F55KbYRj{U<%@NHVNXC(BxnW;$+aoU<%@-&_rMg;>6JSVA6PC3gSdiFE9mh0-FTC--FWoJTC;l-_u0t9UikL{2iJCOhNn+ng&ck{27`IOhNn&O7HN9Nxy<A_?;f~lbbc+FPa4LztHz!3St{P7uW_)0^JEt0#1$~UJJbrUJKp@eF@$LJ_Duqd}r`8@l|MRFa>d5czwWm!F8ZR!F9mhp_9R+qrs&8z}>;_zwL*-N$YzYt3Jv@dJW|wJ!|`~oM&+!q<d`to!1_mxBK0myB^k~o{~dTLDz#*fzv=YfYX4}LN|ibg4098!Rf)7pqs#%z~0c!U~h01=oWAmu>0Ky@mA;|+kfvzhz~<A+Wvc=LVO8&%l6;<7vkFpV!M|py)U#Qh>Jk0fs23}BZ&Q=ZNQ|x!G2%^IuUGu*Fe{T*MK9T8^EO7!K4Slk>Eqn<KRQ!qtH{}qu`U!b70al;FI7J&^_Q2;BC+-@HTKbbQ73#6*wHc4(bH21BXJFfJ4EHpg~~LS>Q$B1<>i>1>m{R!C=xZ;JM%l&`jV7;0|8@y~FDOwZo?%?h7pf?h76QZ44d)9s%_O`=K3-KoGBht^uzA?}A2xBXNy)A&5=rQLqU<0zC;niEDWTL3|jx4SX2985#}_$2HrGAl?WK1#bigLl=P;;o1Zvh{K?B!E<p9!Vtu>p&h^-P}j2&#LJ;Wz{|lQ&=KGfsM8Px@lNP2@GjKdP6Tl@^a%I}>L?mPybrn=ycu<|4?!FO4F(6}JR_j9!LxA=5eVWP&=7D4%C`d=4UWd~cHnP!;AfwhXKv=0$f608{sJb=0Vd4}CjAvmniou3ASTMtm^~)SA&4s>i0dJU+dvzE+kiVmTZ21;dqV#J{}vOuW1<)|Ke%H|G>eI*(7NEJ;2O~K;2Pl4&|=`y;KI=SU^_G`G(R{$%8?a8oGB&}X!O5Wiy1dT(}0tKQ$sU?Q-d==^MEseb3u!ObAgM*L|JG>Xi;!Qa1{h`31}X032;7WMsPl`H#7~{8=MxJ9Gn)MA|?_;6G4-MlcQb|A&6}VV)uW<@e#yHpvl0=P+v(9#3`W}z$wA$pt->5z}cWhz}dhBJ?gX|g1C50REE}qmIaqZUDrYo*GCXHgjNAJ1UE(yS3?k&f|dZ6!1XAFATER;&JOhkd*ga!M-ZonrU0i0r}DUFsSw0T5yS}*#PJZsUR3^iHm~&Y{$Kx#!T<iF{U2JK|KXtemvOfRd;Vo$OkS~@gd5jOKxK(JxEH@D^QE_6+W!C>!W=X'

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
