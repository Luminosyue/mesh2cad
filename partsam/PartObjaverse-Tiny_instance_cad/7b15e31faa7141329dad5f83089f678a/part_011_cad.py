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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_011.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_011.stl', 'source_sha256': 'b7278996d74ba1992f713b81cda807e273207871da072efd228cf2bbdff464a5', 'input_faces': 1344, 'input_vertices': 837, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1794046014547348, -0.09321722388267517, -0.4342834949493408], [0.18247263133525848, 0.035104721784591675, 0.15055270493030548]]}
GEOMETRY_BASE85 = 'c$}r2XOt9G7p`lDBtawx6&X;1NRk|-$vKH4NN_-cWEg^ET2LfQ5)@P82T0C2HaQ0gl0-)Yktjw4RBoNKpHoyF=Eq(4vesVj({JxSwd;hc>gr;e)K8W?izEN?IAybSYxQ>{$5D~a$>I#?n9#4wn;rWW?b&-!jFUn8>YveRjb3foq-BgVz!_4YL&v^vCKRX;SD;d-as>*<73kC}p<hC~o^SL@=+II5wc2&>+tKy=zSXXGNB4EXawW?ajw|_m;kaRO|BwIDxFsZR{A<rPSHraytySt=o_s=SX#DTuCtt7q=+XhF0{+R>+K)WG?rZ)2+h?>N9rs7DojRu^zfR0Le>>r(hqdo?A201^dHuBZPpy)6E;rJCxMt?FN)s!u6#tFSbUUF29Rq$C-_8%2{87_SCgq2RRtxyf-rh;JAKlYC$@atecKgOR?Z>BIChadj8Q9;%5pyMfby(V27&;s9SK-&cf5h*Hj#f@GKXjyWAV1o2miVUqmPOC{ebav8{BHvJj%nY@H|?AJxa1Q8^*f~+oelW3A8DKIsNXmB+xez_lOO;1yV6dLSEb*6$e{D%8^1028}G<`YyXY*!|VD7_Sb1!DByebJbCzt-#7bf=X>>#pP0L!<QMuVu-(LVodf+4?Or$Nn||(`{;1zK{b1*N{Y-x7Ku2k3%;$Q$p?XiqxKwN%*lzer*`RN>yZh=9zi+l{=X={FKXF)N@%y!q{x5Mt=Z6*-NOHXx-(D}qx7Um9d+ViPo+Q`1@$L0)e0#myzTJK}w!Iu@zBnx7ekYUcSKHcw?HWJYrgmVv#t-A0?b^QCuIGPTZf#QShw$z89g}ahZ+z2!C`~eHKl^-{pS=&rysGx!ZvFm^Cc)zyzJu=_-|(Z?n*@(<mhT-uP5ZCaT$^P3_>Z*Tyyn^@+sF6XkDS$hxJ*V_FJ(rY)1T|}jpWZ=vDWW9omYvUyT9~9x`Emcmt8LYq1I~x{f{5U_xc|{Wb&yq`onDT%Zv`RV|)kSv}62e>Cs8HV|;IZuKYa7I*o7FX?(j*+kd3}gX9;ebu=m885ud^_nm2FlB_2>wM>%rgz@cqjBnTDn0%`q<C}UyM@GwbhYykYQ@58M-)P>h;_uic<G!|w%!hH6ldRwPcKyb;>$iPVzt_H1zwMj)ofpa`IljiX$JhAw_}ac#k7?f;U)%S_w^T7{r&gMkf$_z6@V)WHkJcpLjIZT;<7?VC`DT1A-_#TNw1~7bCUc;Fj334~^%y^7@~Ox6O+8-w?`ID5kL`Q)jCfMo8Sred9()Jis|P>Y|Jh(YmhaVL+Bf;89?O5E9&5b3daUvCwrh=-?LShFHD0#w&F8V1WV=niTppOu_|eAVd-EATjPK27%lGE9Y2W0V`E2=KJ>4Jd(x0!qGFT6O2;Zv*-!b{79?SRYG3{4c8LY?hO+AS<|ImK)haz&`{O7Urdj4noRqAPaM9z1`#Sfi0F8(Kz<oNc@zxp^9d1kBBb714rz_{aw_lxh1yUEA*#@+J0aX0=x^3AwgzBdo!SIBlp+zZx&@8Em&nEc`Qg7sLwSC8?B-3!)Z`CdISi)6c8pGU*L$a&$tDboKheJAII-!5xEv2!!&XX`v}eEU3ZeEU3Z`=<WrV-3Z(j`PO1kMnV>UXtye+rQYKZ~X9C@gK>@H}%-QsmJrrkWYWwzIR^OTt@s`Pb~4*WBl+<@xAkc$;bE33zqMl7mR;{d~;r~d{a-{A1P(LzTdt|_v6mT&-;C+)LiX{+pjq1_rqhxh`*%4`K0_u+NqSF{m|6afp$XC7TR~NR}bVzkJpj>U2THf?UGxzJGxWQuXa_AtKSU{wlm|9_+z>U>wIjd_)ei<Jrfp)-@IJFkM@6D{F&p=C+XYU#gCSHKIwLrWe@ny8+}$Jx!p{yRwPwt_?1R0lG?B6nNll~s>d05e|eJqmgD&Hr20Af`tIdPj>~t8mM1xmQ$Jju)O?7xpSnD$`4C#ye|b{#%1PHUm|yznPJh3JAN(ihm!1a#zEk5P`F;`JsC}ns4f&q+N)O$R({!EqJ%3p1?>FOn^QTbCbAI3JPyFzXC4qczyZ9#G_)e)g+7GR*ANU?;d<Wk<Z{kPS)DL`*vwiP)o_x0WSLVoZxN{r5Uy0qnkoIrAyU4#?<A-mG?;VFtKE8JxwtVmVqw#N$&vC}~z2jcxPsLwcFwhUik1i@0=m#%<`{_kV<%grE7bTgG?;R&C-#bnkf7|Im{kHENCkM=w?V96Tnuh26zM22V53L_3KF8Hij$Z@5ndin&y#1c|wYhIxub#}$lL^w!c<uv7E6Mn#>lvuWIZ`~}n|h2NpSx`^|I>fYCh0S8jqkN%<$FH)aV=T~)<yKhYv=vGSr^6+-F-Q@uAlED_1`Kc?Wf5ZIFA_L`5|V7-*=8b9q8xq@Q=^=ebdjzk87Sx>WmF7)a~?GChZ^lb%*vR{k}l!M{A}2^0&1g;=a0f{eW-ow|mzQ_|b0T1MAoJz3T`3@QJobwjaW`+xO<x*mUQT^1X2}b(;BR<s1Kz{Df|clBy@%r`w{W>T&Sx{WZS5zfSLNfpus5-nuh>BuCQqe32vRdhj2q$K>1fe4ZoedhosL;nX*!pQm(_@ya|`=Hcq^cKGMBcm8_%LLlEsvqbyhJx8Se-)b$>@8{j6{YdA1lD}ZHtcyFF#eZzaj=(y7H+s(Rd+QNDzUmgqzn@vR?=(Cp^$cDw`?Y!TO8<5fUmh7~Kb-!Vb4mGTo*3Ud?_2ry@gXvPn6zWgo3l@x^ZVX;6F>SyhhTpmJSXj!sv-4T=Mm%E=MgX8I*%CNK96|$)_KJCz4M^)t@DWOd*546RTjVD_+UNw;RfS_^_YBouO7?y>M?%(@xgj5-_#SHS3$<hx;`<!eSKnl`})N8z5D0imzH+S{r`kTaz3hEO169WisYYLp#A8w5`lRVo>uH!Qofm2#y9iF&bP0}LV2E-cDSD(%JcDgzwe!oKL1jVC!c1QItMJ3^?Pch)So<CFrV$(zPDcbr;~O#kB3+FmHl0_V7tz<z7HDT{yymCTi*w5-}}C7eCzw5?R(d01tQ{?I~Mr9Z2WN9V}b9>UOv8e-DUaSb(itW91DD3wtesTAM>I1?eF`>f8_iAmy@(_-+wT^egDDu_WcLj_pY}y7L)DT_h;}Qxj$p_?fWy9|494x{Ta*mjwhSqWV;2o2kJ3?xWM*6JzhS(cRaCt?|5ST{M!Td*uM8WLdqYa`t#O(LgU-_35{>xC$xR<cw*YO?i1R+SI^bMvfX9#gZ1D$_+CBu(WUc)^;o`Fk7?iJn|dtYyMFj>xA^vbZ~RB@d*eTH-`n!N`D5C*?|WPRBlXz#y-hv#eQ&c}`@Xm3KT?l<-`n!N`CNI0`0KMt{W&_F_4^L~!{<iCkFLuWynkr<51&h+eUoqIv*kZhkLe$~9;<)6?OOd~`;XLP^^fg)^SSl{X~#Mq8s9!18sGk%%l5tbY}&Ve=dyiMPjvkk(ht_}fX26f2Q<F@JD}}*=P%Q~^*f;Ld)G5dhl<bjhEsg~dB5*nZ}9ytzVQIrF4qI$+H)lTb}!bcocBY;CW=3$i}*Yz6RkQ-uAjG6O>$g}Z;y-d?QyYvZ=RU;t#Pq^Z{FhD<KpF8<Koq6jf?Hu_1NQL``)-reo6MrIxidFJ}(>JJ}=w8H%}@QPqP1w|HyU1q`lj8p7nf%@$Kg;jBh_*Vf$V^ZFfog*7G68x1SF&zWscN?R(czf6kJ2%zaLCorWJRQX}|055E1JjPdQ~WD+|~5x-BYJePQL!2z9r=KX*l{&K7K<LV8U?OM+l8Q*@s$oTg2MYivqM_Tuk{k5KtGQRzMl+)ue*{<~*m+>9*T-nQ=P6qO==evw=Ki_5iD9?A<?by$KMdE(j>aWK<pJsfop8pLz8OXPub2GmEoSX5zdaQQr=ilP{pAz4CuFv?Up2U4EPWpZOc|R}Tdfw0YrXIT;`#He)Z|4X4$2`Yqe6OCa!%hbBt>+<)Z$A%de6Jp>9s4;+=fw$u{xQ#O8sF3t+SU4`-?yLt^zyCeKaFqdvD>kq3yoarALt+RoT~A?db0L98OXPucQwBKysPoOdaQQr=U@}xYP~h7^=|w}o*%}4<auDzj{SV&E7@ebF%9HCaK<;}I5Q))wEw}Y+K+47U;Gwjx9I$|m*oENs!`gH6fC8EXPu+3qaw#<Xg{<qjrbfto$B-DJpMr{?R&qcygps76XKIgKKJLN{fA0^@fg`I-|M~Kl?HX&tY34SjCN{qSl3<n)qo#&ql@+<hZ|`>T&AMbe<1fk{eI$0+K>K|Mebvq%&vXsnbDi1U*z|}xK%%j|7CaaPs@Fe$i<(uA4%vU{_PcVAFt=VL;Ce!jkWJgU8Mc^-_z=P;wR=8|9)NFZ*fa!>io#cl-dt3Evfy)ZgaFBUN@+i&ad&=`&HEIqN8_I@%!mw$Ew$njD3Ut?Ykf7*L~(B={vc$2mQ6Vr|EXSJ{9yAzpVY}tDCL-`XB4pjce`<_<0X%-}$7t_T%PUZ>3+S&l=G>r`}ejiOuu1)35Wk692)RE!v+ox}$#G@7*tSyW@Y<`QfWqx@dpkbe$hP(NNlXzkYY^A6h(H=Pm7_{b>Ic;`iCB^Fw=2>h|OEFYBrO*6(OPTq<|a-}$|6C;Igr?K`nUdTHJ9ifp&(7TtbalV5sEoqctFsCA;$>D)}v{-o=lYkx@HZQ8$+yRY_dB+7Qn^w;f2_B8FM{VI2*{)``LKRRJ;f9-dFO7eH7*6k#=`gwr%qa|g#k>|z#qy8Z6|2tUrcj?8=`t`11gQcExQvYXlbo-%ChYrzx;%~CQ1K-kqxWV9I;t$mIhxfj*E#T+9qsJw>GN<<Aa}OG>{Y#mpor&eeua)W@?KfL3^^9*J?XMgy{=7p{f2V=sM{eL(mHBY+PpN;(%Ol0VAoJncRq6kKzZSnhs@eYjiJbpzl=h$NuIrCxjMIMTP_lOe{d07-^mFM^;y0cq^(@@3{rF;Q#c%SM^jphudb^=4jo;J$mvOScr50*Ge(GD|*RCkz)i9&X&-+)z|G1g7U+_ikJA-3JYwdJR`g3C|>4(OSUgyq?^-}+U&tzULxGa8bxi9?lGm`G3G1}kvo1RCZxN18Ce&TvP{t?!x=V#fV>xwUMX-B}fjx(Nb9XFzvX6WONvpl74Csh4V(6^3Do^KtO;(l5@LBIcBNX}E6Lh`#zyFKEY^I)@T@;l3g@3rs!e~JZ7B)`R7?T52oko-BX@H=m&iP~@VtDHwBz9ru`8y6OT?KhIo`6YU|ruNPAZ{G7Bb>EmM<33rg136E{KXZSM&aXC3>fe|(;D=TglKi|`<h(X4X0EKmOHxmU=VZIzrqX`+@BPwF+JdrQ71K+;c^>SKic<fqERz56PRakJifs4plajydN%03Yl>6{4@@PNw>R>r9XKXC(w>-00`?u!F{_Zao^v}ji{cCFk{BX|yr2gF1gZb08OP%~a9$x>Q_zjmxJ(r&j_~Ds7q@MV+L7(U6!~0SP{onTTymU_Kw}#i2BsKp%KeSP=<HUrcI|9BvKaFqAPp5tHrCN(`8mQ+h=QYo_)|cnc>8{sBwE2}_JJ$O0d~1Eh4X?4%zb?%43E?HRwQruc2^W<45TCBm%D_B4URdT^#irtO-4#A9^UC?;wUz$)9KI#<GkoB6@wpxgZObU_Ki^LK-uLb<$pXGvU(v5)WW6}?tCAWQ&$s%`^R0gKe5>C)-|DwWno+Bg8h6jP#@+L+aSs(Av{w7(_qCsD%R0h0_q(EvYRUe7Fhcx<iLzdHm6LU`b)@#a-^Ey8;ap=S|LbXzpBN|YH=H0o_s7h7iCa8X`_ZRfk$PG^5%A4*a`a9*Sr?;Mu1#vc5^HP|-@2}g@3$k6Z~8NIVxRcM<Mg;hGVhoC5=X_it{bD#GvZG^9yq^*Tc%hi<9<4LefV?wb^du09ut!5$?TcdB{fex-@g95xMZXDC)ShsJR@HE+4zNTNq_#=R_1Nh)f@f&Z_Xp0Z~EUHKO-B(FFs4gYjSz%=c8N1KPCUqH1uI<S$9QuiNCOo<X0&W@SSV-WW2u0C+jgws!e)7tn2^it^C@5<oiOwhT>b_FG44~Xy5)m5=quWeCzv5c*JP&t?xV0s#Wy$m;L=Hv1nuM+ux@mZC}>D{rxL^u3Nx2-`AXRrR4hB`u-Tdp{!h=THiOrcT&rBkoEmEye6Amms#IuoeE>N`L}ECr^WA^67bFax9E$T0>0C6;*o%V@#0FqAJ=ZH_MKPGO8xux9|-tn9o=cKU&mGYF5ri@O%3{HJ$^k>zmB%}b(??Pg`W9XuB)%y+vZ<);jYW%`n+q3sP^BH=TW0?wwL?E_|ZInYCm$Ngna*vO%?U8Q)k_7xqiM~ReZk3g-&FZ*CXnS?#rjYmn25>>DQ5^jiUZ_8oFID=(A4a@WW$!ir-+i{(UoU(j@tw-lVU*KXJPJPI|tEp0}Y~jkgEZ^}L1W{eJkLYcjs+<vEAM)lIes*7b&20pFb0!eeL3@wvgv+x_c092phx&HvX6%^e}fhfB?5yMtes{KkC(zFF7K`d(6JxtVgFx1I}%fAEPM7p>=rqWQj(<F5Uj(z{C}-+Hbo?t^3EThG@eHn<?|SkFhrWw|K%)^mFC6>bLd&GT2$(aH4j)f~sn{u<w02b%qjTbpvHzdy}$9iGo|GJJNp9G{1!-I>&QdA>OgGhT^{)64bU=7xd!V0`a5&wL2=%Pe(nzxb7|J6mr3yh!5yJd*#*2ikYSb>#Vyf(6C@G<Lqu%ld~r_wY$w@rP8Gc1|^y=Whx%3$*XtP1O1Er3OfT)m)OlzPdc8GHs~jH=LpUxSww8{KTKf1=<fcep2VhU0Wmh$z$a?fqL?MTl~Onl3!t{e$FKNiaclO962ocIqFFM`~{N#<R!_Um|C7o8S;<pZ>M|Wzf@4?$B&;Ob*{>=OZzLY%5x)auSz|sb8A05d5t^|vtqV9_cODg<mW4+{kZ3LO8Y}X+7EHQh+F?Zc|NsTP4TB)m*4SAZIS0n3$&4T9(0xSPJelRH=3*CuE2cb`T5YAPP_c`Gdi+nz<11Z0{6Ge^Qq_i><Y}o(94paw*Ricysgw+{K=zt`RAee{utdhc9(zNMmKj0`n}u9dG?pSdb^32r|<I5&rq#F=L7!jPjsD${g+Gruo=7j^W1z7jW4lC^2a|T=f_5ab$;aTGVy;tBFFy{Q?(y=@HG9CNzR+E$^X|fet6&pc@D6~Mfv{&>Hm^;IG-jaY?S<Ycf{||H;|wB(sR3Yoe9<Cx!GKcgZ`;5l7H)j{J)5tHMAcpdUvHi-}upgzL5Mho8|v4Jl9$BcP3x0U#G3D|KE7xrnj^oZq`Bj;h~kaA6eOZw||~Q^IVnZ!|NsN_Ro{hhHLV?Zs+&JU%FN5?^{#anK5R!f1WsX{*eEtP;{KMzwk4u=Yt~h|JeVWB=wv7^NaqH=cQ*a+U=h|PD~0J_XjH^-<c`-9a72snYl{)PTU$9uQlc5|MRz9FYP=%U2iv3KDYR*_v{YLtKT!o@%GaG-GTXIzQ?6GCH{b0a(!4_{;omd>~Ex<Z9htXX8vNY-w&l~r2XjZT(aHrXQZ9R)%EYc(WhtXeCP5X($0`s(m$6z(SE4Ledfam`MvnB@!F4OeRhxT&l{7a{VkKVAL;kJ_M^22$nVa_!qWbn!h8JVYyRJK^hB{e{_%B2c9n5YR#Ms-Fi3tk&-cqd-F}HO(oU+g+K>EsUHfrywZ#AOnAG!Nl+@F>?jHYqh%WAP&hLkl718Y^MuzG9_*zXR-+W&fm~hVTM@tkBZnttv@h4`LaqN6i`-$rl_5|k7iJ?4)Iaqvi-t0D9>KQOX{5kn$T>kq}w-cXYth8VB2|4cdKBxWg3)A=b=TG#*_hjC-nz_e6e~cfx8VUA)rGsbveslx(<yK75e^)2&oiC-HA^BvxOUugdDLLl^$BTB1AFlV>I)6LHci3*Y*1%JNc3$ta#=l>Y<#Q!J-Fs3`_A>H)r_NW>{<YmYKd$O&o$n;hm--iQ9vS?$Za=>8w!pZD${s!I_oMxn2KTr14#_Y3t+dZ}qrdNz{L*q?%lmso#^>)8neE0syI0!b_dApCY}yx?SEe4%=Xhf3iM)J3+TSjJXCTt}Md^oY2PL25mHB%|kqoD$-=3HMmm2ri1buxT7dj{TjBljvc=;Z8=Dhgkeqc8FyEn#<UgdjkotCF{zoq(K+Be5x{yvQJMWVFBb+yS)EOSxX`E@VXjr7}*AH~nXaen<Vd4B1`pJjZ_IO2zQUzhC;UB1rWj??C5V10!SoRsHeCft^M^Y=-HO+DfF!)H#(`l3G*H~k)*4?p(T{TXfcr?kW0i8B2ex&BvR{hIBDM*S`A^qCkK$GE5NNjoJs>2~7B6qfJZEALDGF^&V-WxK|A%<*bT#<PAuZ2k@j{Tz4kKk=)Sl78DWR(`KskZiAR#~jDZ-!;NFe_t!q<hVS~Ry9Q+-x=0I+K;4_{9>~L<KjHXDEa2PefOEOem^`_?k9)(Y|!JCI3u(6qlc~p$E9diX~%p|q#ff&+hz*%Tl}7E(*6saH|zJ4zZ=#zhxq(G9Mit>onQJ$zuhh*{Xg+3$-l|{bL#Z`3H8?b+jpMMr~MGmHJNo38uEhF$=^5gey_KDGhUH}Ma54n5*V*YpOR81^U8a^6hA~ep`TC4x=3AG+L=9>`SzNu)7fSA`q!6Jd873IvGRNU>&y5dr?U9WLo*+ot#zdyj>F!(dasex!}s^lg)C?Ne)Q8zf&5UeCV_l2uObbaNxtc4+VOldj_j9{rG@zSrJd-AQ}TRE^;XipX-D->lfYlin|HI+yWuKoi8xMbCyUdmo$pWPg{w%K(WL)mUYAn;SAR0^#ge5;{r~;Vyfh8m8Y-#baict14y^<~?nZhyilN2fVsJU4IBleMBMqNR!)Fwia-*ah)zGSN6E|wP(U?$N6RieUBflp3D(`>jm+=4Kv*;Q4EF2Rf>cj}EP+S@<1($}Kp)bSD;5q33;B{`ScVh{<6jr(rUIH&57V`Opw4r#eTgDtW>ZA4GbZ$K6Mp3i`Tow(XC14dbcz?Ou?qWAKqHE!cXd=26F3V>t5;dqnX(PBkJQtk}&xJ3dr(vZJ;EQmw7zxGs(2_C2N}Iy@;Kt~eaASBLIv<_~uSA!_i(%!haN{f0-{@?3F5JkCv~E2`+(<<zevwdI1uX+tfvckx;0lambwY7NbPn7Qj-Wrl5%?QI@qcJ+jIh$@U=@l>5Q>|ijo?P?V-xye8GY~-yeLNf7hlKu-i;0D8h8!wZ$Ov9KQN!ZM-zSg1M}+#ayQb?^Vt48#%BfZZD5=>(Ef6C1-yd%<$QK7b73y~rno-+TM?}Qmqp8<72ve2u_9<uxCmT^Fl#Oq>o6^v4lcp`2%%NrMyww*)-{+5HF&=|S_N)I-fT1i&xTK<-@vEg2k3wB1GpsfqXcWKB=e&w+5~P2e~He9)wr)^%-6D(7NPUuMX;Gm^ZERI+EDzlTf@6<jB{feth^<>R{RyLypP<N>c(PTU*i3*;BV2?F~Z-%PsE58fS-Vi5Q^)f)#18uD?;(BF|z%6)UX)-5j_w82tO7hnm$HYh2s2ZVfYm{s=4txp|}p3AI?vH9qQ;zT`k=9UvuMSv?<)jjkn!+1MLXEhBiez!c*zrQRrBB6x<CR1`lH!-DtlL-Y0HNAG$FPeHR`F4@A4eYJWS?2d}{KgyIBrI6R!sC7|8m_uQD_#(4BoxCQ+Yk9LBU4us?31m<9O=HxhdIGO+_kgr&6V-VX{<I;|?QQ8;o438lC@)@N);6d<v_zApDU>_9^W1DZI1L3#fj%X+NUE1r8_JCWk&#$5Wc@fW8#<QP&hy=zufxhU5z6*DQN1@Yv^Jg0KOX*keRCpfxEj$lCk3PW~IuEC3{T6}K!-dhhaACL(+6t}%zm9hHt-H?5wa$!FCt?KiZa6#;9Rz>E{Qi^}$J`qa4?+jRpOE(<Is^XD-N(^t4XJtM#(Qqea$~6*)7_YlHywW#yp&MyUq&y$m*F%qq8Va@RVXfq7KNL;QNxYagyMQ=LAW6KieGozZ0W`;Xfq$T<8?E*Gog48`=a)<2RZ^)+81sI4<h>V{%7vCXSy)~9Su)_2ctb<wJ&e6f6d|cgyMc^7!LEferQkleK$UGV<P%F{5t#H9(@Z|Iv8#b_hXFJSWiHE!V};y+7Ir>XBDd&hPcs-Z4aR?)#frs=Fx}n0`w<%0sI}BHb(e6IAe_H^KeGE7@@d6S`)4hw?SWn+rVAWH({my;V$qy=n%LU+@I)&*N?GKJc9lhgbw!2lflfj!Hj|8(ezVKv={t3W786C=bOLnnRD$KgT6#R=4U^~sRue5?g77teh9w@Pe&KP)8YB(ckq1p0-BL^d;!kD7!`vvz(vvea8bA(+6Jx%w?@0fJY4%-SQA|sledU>SRY|{FggTQYjXl?<8yc-F@d}Z<PITU<;_Gtf?K=$*vgIO=&SG-?t34*F$o<5PlAV{y<zp)H~IXla2G=H5VSu$1bzqY1-}DNMBj%e!k?lu;7{S@=t6iod<Fd;z5=I<5zQ1MtU_@iv^cD^0bB^Kg|>xj!7b3Pa0|Etp?Cl~5*|ta4M2Ottr>?7XjfS2P`Cp;038VrfP15p;NI{U^fP!2JQH03&x9ADKf{aQMD+0(;Y2udjOYt+X81)yaYM8=+z@^PZ3({tcSAeEO5cXN!J`Pp!_Yo(#ElQ!m_;Zaiw=W_kw2Et4&e0w#zpZv^yv_EsBb<GWxfw(oD`3tz20aaxHaR~3VqXgxQ05gCOR;d{fPmri2;mdFLVst3w|G+3BM1|Ko`L?;Du-+yb%5#&CFW)9?ry=z6fW6i=z$U;&21>4Y&c^7VQSNg}b7o;I8mUViap-6l11X9j_)a&Jp+nViI|i$Q?$$%KI3d1!s5E?PPcV2*ppKFThIk`~2K^N}q?b@?LiQJb0?jjQAPxveQ;h-p|Q<il5`X{P<7dy}-8eqtC%-+<o}YjYH^h_z)aL_rP1+*bna~Pw^>Od1v5L#Cg2)Y{T$TULR!}hIjIMC)+i=h1XlyrsC6XTyWzc`ZatI-iGdmH@mS9-bbF|lkh&;Jcy^_9Nsy$VfYBIkFX8HJ9xc=?Hb<9>&<LaaW+Ri|L(2{Lh+MmAy{cXpZ^S=(t>an-phs`ho{=ifS&;`8*Sy_{T#fPiS0bg`_J;8si7e67vw#~-?;nmts4i>WAFiZE4mBb<i=ijFL{bjz{>juK0%ztJIgi<ALjL8wqbZXueY;Z!<%@$iES#5y8E!hjmj~idtjyeVHJw+;vIyQ?t_)?f|YKA)n}DvMYqAqSNb=vmH#*IZ-SMsgO#p<m9B;VhAXo#O1C%?iZ`GtNAY$?@;0Me;LY%QbOXE|UWKlOSHUaMHSij0T}dcjjc$Th!yD0U@J4tmp?EjC3*HSMK=;81;KS%a_#k6;m{5EO-2)$j_o6%Cz3@&n3P<Tj#n;@p@5T-E$r#}q@NHNBazyj;TKRbi#T5v}xlz?tZeA-+iC%+MDE^&Le1dU2LVereo#+X8C%hNE=G)(E^v5;!!Sv4!`tJt&V*2woeQ);DjKyD!)mHQl`WJi$el|u_^~JM<;woqbxC$I16jwxZ!xiB;G$kAdr$SYKrQ)^XKM2LA&=c?p`tB5=_$Z<Hq#L>1c5=E=j!>M(jXxdHU(lSe3dPqQ3B~u&T<|^GP3}et^cgf4{0v+kEeD6tDrh;l9Cexg%tL>hT224|$@pwVH==(!57(*U)#xwI!*#8AC3@X?cpOlyjv4FGtLSz3I{SPTRr`6B*NT629`=P|rN24CzcCKK5{i$bN8lr@jpOKgcs<)V&S#JFI&ZAo7jEPs6hDXNgKNb~UR5*?+{}$v+<2K#{3_ZUuIol^H|h|IYofK_TC}HlvKv#}=z?~Ir@ArTjSmRLW6?42SonQ(68t_qj`qjV_Bi}0wD}g>nF@C!6yJ{#{U=8FPjyaHYno7ehfsVEy$j!i{~_+uPFMP|3;HtLmAX2kli<#92Wso&tGN^X(TVrR6CLP}4t#bDW7FI>F3lOMT8vFzqBe7(Ht#=6)b-5|rGL^VivMQc72iec!rkc0PUu}&X<cfsOFf;4=G5Mm{clEeX0CPS{a4WD@LP=Qo9I~hO}IV!KKwp&qCKIwqi^1HM7zLU7_W}#Yj8)nJvF=;`*7S9-($|Gxl$ljLUBR#9<0_`{#aQXRpDxALAV-R167}`fxd}f9c@7<Zi&7Lze&9<(br(djTCOg5Q<ZxY2cJ_S~LTk7S2d0&W2`%l|Bh)gP%g5hM$6S5sGu7IpCadW;7F=8BUKr4m<2mESemSg&#vx!>Re)W9Z{>F1Gy?n%P%#X7(wDK1xocq`j2%QED_JoElD#W`ncQrs98NWFP)RV__AFli@uEJA5Vu`T$m;I1QSLF;tO?u~Pa3tTa2E0nUo%hO@#?61f>GrE##*XW*yd9B39e2b>8_2WNsGN0Y(H*k8pX-53?C{?C}`J8&2tj*ftb!$Z))@DO+qIuITN_ecA|N(aFG;kVrwh7Lssz;oRA(v2_B&)_fM2>Ll3f&YijhTnDLJ+?CpejA+tzYX_Cr}^rf#y%;X?%T)d^nucezCM{qpD7*f>%-CX@o2_C@oINoU2<a;q4-DiC-_JBGI|rf4BtY3fp5XL(cj_Q@E?TY-_T#--{2eQbvTO~Io!xbD1I8v4nGY)h5q9REBzOKKAC$ybNBmCLh%o796&Fkcj1fhJyd=E9<LP_PA2*iTo|s3hTy7jH9~PwH=abFCKQ)OLvU%h6#5eU65B3CD9(wheang7hLxruM@0%gr!=pxoxE&Q>9f8Xo~1^msbQrlef6hgpOj{WpM(n$ipvp-^An1*5sDup6#o+|ni5XQwiT;T>=24Gq0hpZ;EZTqI3s*NRx|~CpT4?|s=m8UU!H@n!>7@m@M$=T&WEG$JaiU35B}7R#%?rq;|;VO{07_y?F;wibA8ZRa6{T^gT4W`fqS8S;68k|7oqqgbUyqMyb#?9FNAla=iuG&1@tz2o3(cV{Q>@nwq_8D7o)r3#qd7#0(^mX_QgJ2&-;i2d`{^iUptF@+fw|Y8#B=b=puLlyazo1?}5KVFT&r!f1&qarRo^*7q1mR!*Qc3{0v+ctp=Bc%e%43{p<!e4x)SEgYXITYxo3w8BK&Q!@r`};9ucn$wdE#RVXfw#w8P0p|}cK2Cf3vKr6vD;EL#ru+rRcMYtHDxCEL9&O?8cK&!z@i^9pMuLz;IGFk<$3|B{Mz%{6&I-$4%S`4lLzkrs2OHjiL$sQi-UqB1NFTkdqLTpEAIp226QR7qWLrJtUT$!AbXnt5}F1RH86q*Wt3ceF7`g^Rf3dL95SntM0H+G==;T`ZX^f-JBK8t=2pM|fWSK+H{>k6Ux5~27es_MJRYsLSfxnLEFpTNrxE6oOfL%TnrH{qY)Tj;;=EjX5Ks5W8=#Tn3Sa0WO#p*Rit7@P)v5G$(AVGjt!$???rEIFY#3z`Ye0%t}u!kOX!Vnx;Y>_0;B4fHyE13rVEhR?v;(I~8R9=si%i+&2vg+Cz_C!l@d1UMdT2gk!r(5CQ<ZoK412|{rdv<cjV{3>W;xC$IX8^R&Dk{hMbiiG0&XhXO@+zM?2w}N}1y<nvu!AfVqJ>c%>hp;&hbw_)`-Qm`56m_GF8-)qQrO@(lDY!D)0Im!-LR-U);I?Q_xGmh9Q2a4E6aE<f3S9ty1@A)lz`NjY(eL1I;os1|V5RE3_#3Ykr%fhW7ETN2L(9YY-~wnKxB#4<P@E3U4X1;1pfAEoE5SM7f@m4IAp9H}2R{ctj;izM<Gfb<N37^I_z(DJG!gz8K97D4pNEg4d*P$-Hgp5L4PNKQGIRyH0am&RUIDLiV>P-N-2`uj51|L)L-0xT1bh<y5xorm2>*iq3jYGfBokHVc*RPKz(qK>#h`b{kAYPiO0W9byvjC}e($T{dumjA+*k8)_DSh}-#+fA50q~7^~py1Y&E<RT@SB>mlKMY5{lQNJK(kOR`eLW6+VKVg^$3e&?~UgOR&;!;H7M1388omx)ojnZ$Xd1Tj0a!DfkraAEr(9`DKLSb?6p&9lQ-a9Q$zIDn5#S6Z>$UD?X3@6#H;pDE=9}75i`<DgFah=XJC0Vp*55oY&1d&A>X&z&YNm>+G!i?40AxaUhNFSdoU~N*d1p<~XA`J(`?jQgY7m<`|WQ<5m{V@#Z*|*>|kV%&{;t=l`_mjo63BNyX+^s`y*<Ozgwsu;N|l_SlEVZN*=qb7LPK=M{g9eiHleyr8%@ngA<}k9~MfQQQ`768rGHqqq_JQtZR?l;X<hi?I*SYl_u*uP|B&eGx7MKaZAxUqDNuC19mhV5K2gX(iZPH<Tnw)7}ek5jTpVWzo{G(u#0#^2(uQ;c{>Vv?5#qu7}o#m9~QG!LOq|V5Qw*rLAG54dB<|dT4oHo8^5ql&40eWniU6;iBxD;#h9en1706(ByCooC19UP60oS7J#3IOQSErrQtScTeuDUIr;_sIeZhn1>b~UiV>|EBdkL4G;}&V4ZezAgUh<{wfp&VgyJdaWOxc(7p()=g$uip63vU&f%C$-2*tJ0$#8A>1N3Y71Na!BxD55Gy2}uXC%bV4or0Eyr=pe6vanLM&z0zlpXsNc`Hbnesr2hqK4<z_@l8H|&NnXS7`Jouof*d|jPn%w&Ww9q=0#ol&dig-%p=pkW?rRa-ZiNo6PqR3!~eWrHe0t=e>ZZk(;CVD>oot=v+s^GpkqS6F8ptP`;)={_V52>na0k;KLXICehRg1cfrK!|7i8AdivS<KUg`d=K'

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
