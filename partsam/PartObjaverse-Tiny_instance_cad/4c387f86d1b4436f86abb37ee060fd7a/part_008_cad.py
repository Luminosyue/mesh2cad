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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4c387f86d1b4436f86abb37ee060fd7a/part_008.stl', 'relative_path': '4c387f86d1b4436f86abb37ee060fd7a/part_008.stl', 'source_sha256': '9e75f71d7c869b809a8e6b36323836d89aba7d37f18fbeab9ac9fcac0c5721b6', 'input_faces': 938, 'input_vertices': 641, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10434188693761826, -0.11183822154998779, -0.08751522749662399], [0.11556202173233032, 0.1846001148223877, 0.061235614120960236]]}
GEOMETRY_BASE85 = 'c$}rZ2XqwG8~#5bfFcM2L0W(Xgn)$JYnEP>AiXcWg&rwVT&h6my|a|iYbs4xkS<jP3vCHi5s)gK-@fnjY?z&||8xH5_v4)RJfD4X_wLNS@7$TWb4SA)2Br)$@Gq~izUkqc3#%B0L^>nL7}9M}WUnsW1{do$V0eJ>iTd)-r*pn+{zZ7}0Aq+TBBX1#!CeN0RI-Is>0Tiu)E3gc|Dec0o%(g`Kd5Ur@#}Po7~IY45ANA%KsWE_LgmVo47HUm9BLb7`@j76k#`du1rv7fmu;z8YG;^N+^aUPl+TVlW8q)gnJB*VgJ_qZpW;iDpB<~^ZGFGkrGB5>J4Kxj#`h4lKdle{aSruuIp$6A^8<s_cVv9ANOedi^_|gI;`Q%gmD>3EMK7xF?)v2<_1~t4U-cK1Z}D!S{=M2`t=EY9MAfzQ#VY;Xtf#PjWt{l^Q<43&o)yRa{R`8h%)asc$X({`^wiyn@`umr?>eW?()w*pM!`?Yi|@6o?38x0cNzk})^M%IU33r1zvu&h#qL-wpYlZ=KR+Z<eRr|2iRzE(34dEG{G6v3sJ5;Ff8I^q9{ZVe<FtP^=7GQDn?0(J7wGm|eOFLY)PMQL#iaw0A6ej+-;UqSdqex(xElz6^EmXwS7}Gc?>hE8NYu|~uOHI<iMY8~)RhyyuV0K8xz}lXmb(i7Pzo(?&v0j@>Wwpr=IwD8Z=~&JEK5u@x4-+up|#pSlQzH~v*@tyf8T1eL~W;5q5c^Mbo=e~W{o%d&ZX;P^zZ+KHqv%(zQW%h7&pP}8wH}_Urnp+?}{FoXzpL*Zh~%)^OnPJ`<=J`9-`azrU~jP9QcE7N3rYC+D_9O`_=E9TT9#7{iFo^y4j9sx#8Efot+u7C7S!iJ~|EB!Ff9Y$6bXTx_zta&;Kvq6I*z~fB8n=?cw^pnVtl{eCUvMt)CyX8SRkXfqYvOo#1!eohZ9e%XNnDY}!<}--w>5$DOUz62IT|jWeDc{SwUmYoD65LAA02<+rTV-*q>!N9*qdR!{J2|Bp9mdE4gVDBq`w*6;qQ*jR11(gjiecxBxl_n_O;w7jDL{JH-g&~in}Y|#E$m<Rr)E1I81(L~K>=h#nCzmZja_lCBbx1MyV;WrG`c5rXlKVQrDy%g_v9CggD+v&WDam`tKg66IL>S4`W&$QDR*S>y?c1Y^DP=CMDQIs!!26>+JT#sv8orHM5elI&<jehTROuXOme)i6K{hV?g{5_SChi}iW(c|>~8u&}6pgl{UoU7Y)bacF5|F(azSwH6<it<SXu>JW8>v8I|_eA-nuhn-pNP+RNUfp<e|9alWYCX<YcKHAPsO{tY_POq_(<mNq?sp@yjBdZjmN(wq?=H_*T8}MzE|l-n65~(Chnlyxk~!dK9*yxNNA5ZL_d-|Ww4P#RaeNKT-c|oTWpA9hznn?eH)(s0PgLI++xDRD&w+L8wEfbqg8%z4ZBIvEyOuY8bj6w5-}9s|>bbZGe#%(vSGQdY^m}(_$N3!>>#OTHX&j1(Gq=C9)6{KR-$@7j=v=z}p2@X!JhvydgkR*XTes7*YLjkf?Xq#^_IEw{LhEtA363+jv#ahUJ$^kCvd5X**<SXCty(T2Wt`vf_4y>tbI&^i{>tsz@5bPrdR}(@av$xuVxhL1vusxVT}R>$od0Hhh&*XC3fCb+;rrU(^{l`Cu6x1iSikn1d~l1FKQ=wquif^Z+JNoo8EbAgqwU-6x*x4u!(UTP^TahhMDxU*qAcovI!?y{_s_?495C{gj5W8LGxII2$2gHE)-OMoHqz~}eH9#QZa3S_C@pVmcn9PA=atZp6Q1h0VcUHZ-~Zr<{;s`FY3xTt63TDsu6gC2^Og3CtyUb$Uw)(8;~4nIsxXtEJkAstfc-tWJ;vN_?vMcWU6CtL&(v8skB`{q(%*T#B*w2jo8-fBdZiNlju)_hM%vX{eoZ;lA2e6{*YnREZ3p-L(lO@a&Yrj63T@AKp)uxmvzJ_{`Cwa?0)B)|^VS_)bBpTjci4{1AEO^HWY%(ye-7cib>TSLVfrhS8+KraU*0~SkMrIqiSVE7LY@Z|)OPbMjNM`0Un6U0%{S+|-YCB?oA!&bVidObr!G6p?di)ax2FmG@>kK1e{@veGo>Nw^(;rfY#*(kZTYM3Fds**Z1prB+zFwm=i>uthqIOR`1O4D6Y{S4Oq>Vz{DS(Ici)cf2|<00L(sqBIpF80j(mGoR<Ac4vDx7#HA9|%(F5Nb_wzQi+lM%h9W1m~kIR^S>KiHN;k;1wl=izba4E_!NrUs<xre%4w)54u`L+MZfoQjK*|wSU!BgrxZGU%*kKi}HjN@rwL;YP(w?Nc0eFu)a#Xlj>k}jZsesiIHs&~-uIkv9G_;k*_PyN01x9ag-cNNO#ABsF2dK&pqzck86e2=`lP*dB-*pvqT@qyT$<_(cAr>1IN8`s0|{Yq8zylG$E4*ueFx;@6VvYWM?w-teZs|oi1!<lI3Wm({72*CA5*FdyesR=mF<~~OM<-dyletAQWdt-Jj<bUI1+CGjwvv8fYH?8)U{iB0=K63szWuy7HcEvZ*{c;!Sgz}}|>Gh+1BJMM6%SvoC_m_KTY2@jy5Y&^Vhwhgr+e!63MIT{&9hF_%)7E~!=7X);U0l~xyTR|@(CzV@-i-23gVFv|dt-mEM#H~49p~rU(=gtrZG?K({ek}N-9XEG+_g~th8y``?TogAJ8-vN7Z@97;JBI4UH8`$x)FY(q2D8quOT05Eys1xxpJ}QymhaMg#Y;_>{sKKx?iqr=k+}7%!BdCnG55WCovx9=V@0o-;AVV+V9Sf`oizGa<ArP$8a1kZ5qHonMt?P(IZu~*>|q_8{>6AJB$Y_!u7mlR0zZPQZ5IM-*YGR`qu~>%;P%;@~Y{)Xmg%8*R@%%?Q^|_`o8;IXR!-w&AzcE6Y{5NTU_@xF9^TZbIlW1rBOJqH~S2JLOWbnJiUkGu3MgHbN(1lpTduSy$1PHVYgpi9eJd_v;KM1ljuPEpTCdtZL(;2XLKv%ZNZZ$pKu%ZJDG-VF#AT_c#IznQ=$L6Z-@VTBdy0Vd6FKd?jalCx1Epc;i&BDJL)xt-|i5$<7gvoH)pGQ_}z8=alN#swzh-4((TpiKWpHZhxSV=;rGaa{I2;B<4N#D^^HquG49{kq`vE35%?Ehp`Ig4kpE*w<2t%^4Dz7VF^oU!YT`clliquE`%;H))9vq)3*|ExLH+&GAV06))axl{WPtj~=Rx|$_8OW$j*QLmI};bduXqv1%bg53|GvuSLZ0zFvT_~T|3yytYwzJWEftP&boZkbs@?h^AL?h(_H_JlLw)CGynm{?ZKHngz!mr-zt(zewXPsfUS2>w4T6zBr_La+g4>{csRyY4>`a`eMwLMMdp&U889NXCwJ!+eE9OT%tB-2?C;P?jBCpaN((UnFU9epJi}#TKVK&^a&^LyZ#C3DnHnf{<B>eNg;`klb7}rOg9LvplWlxGiyZvx<nK^&#lV9jK>8L#u{>2W+&)|y~S0_d;Gv}3iS&)`@r>eTloL7$Am(dP&@-8#?ukA@Bu9phCm#Xh*iShQ@A84QB->C1jWkNpiI?7XQ@DlaoyW@9{Z_)COy;XGn!??YCkG5mMnwp2s?}q4ngR$vT<j;p8$e+dU=3#$x;W}zh2=a47PWYGC;k@}G4*kC6*j)8jRmJ)4N-ymfBf|>#^IG6M6@47zTjOza{qkyZZ@pe}Kdh?0G47<6_k`BQ`LRSk_-T(LPhJ<+{qlqd!B3GA<HkQ@aa<2fjr!N(KE`PMt=8|1TrfvJ|8f-Pg=%))PJ8ombNu@E*;?IB&xN<M&Hd;*UmF$9&o=j?GinO_ZyLbwxD(^yw2iC%{9C0lo)>zIe)(b0O!dcK(!90x`v&s|bNlK%hx2)(cym5Gqn}R3@!SyknwTGXKK{JUI~s!=+Fzb8Un0+k?a_H7-~EgI^$G0n%W?4I>*07j^f~UED))rHG&}lb!B5(5jyFLQP;NW=vCRtX@3)u7Yxx>?uwQTgTI=Vt{p~|Ns3+%4^^N&=kw3R4;Cg0szwzdNakpEk+vyndZk)MaoIxMzc6yrLP~V8MA)mjkuKDaqaSY{~4Z=KdX53dN`@Z9`LNM~M=H_wce)L`cI1ko_|7;P)?M?;sxNsaxg?eVJ#<;X3lb(;9rBjdA@+||=o_Eq?zVol_gUs#k?wtnh5Rs(wwa&xUQNCv94Sqh`-<~?7UY{8EH^RTZ3gu5+#&-4}48QXq@Y|R0_kH<)E4S9;9+YyRUprs?4f*io<N&{Ro)d<4?mKUQx!ru%C(Z}$2l%xc+tV0W5Ps1{e9q7l<JHZ}{q=LmB5gPO%a+=1o}f}a%<blO-@$c@y;W=dy;&!a&u+|{*y?=WK>f^H)pun71IJ%pXMO!%?q0Y)ua5Z+`}}O>)K6!_JcbSP9kyZnUhR|5<!57iPDJSTB>R6|@Ed=8z7eqkdA{h8pYQyl8n*x7aR2)0`>ubI>&b8z`S5F&c)#+#JgJm>lVAPJ2lx2`oBe#>@fBa%&rj~(P4_nXmG@o$bZ+LiJ;~$S(EjWF>S6!dKP-v<eYF2oHRJttg}d2aj7z1<7uWXXc;#4768qKX_cH32uZVux-VNi{7lD=Zvu_+*_c_L~C7ycvJH2M(ethU?Twi%gc2K`WDx8l_zs7!KE!89JKk~<B%!J>eFOFZH*IW_jd#RuM@ow|DVXO5+Z!On;rsj!z*kQECoy+~h{v&UbeM_Dj58Dq2`;X(r=Ua~#NB?;!Z#nL4ktqj;nfsB)sWEV{`qtw;*|&@j$-ZSA@bpcBZyA4*earac*z^Mazk%95w&vB*K7VH)6lTs_j&H8GS^E6MS!k&Cmo3#k>~~<Pk?Lm)z`X04C>*~Dr$?Fl(Kmj&R`$_(XlL-(IDS*(e!+41kUk$Uru>Qdke;J)-E=sWKHsp8&yM@4)i*X8sHe#<$m<C+$NBXO$A3qy&8Ww69&rU88)xp{<Z*B8yK#Q~=sQn&&uf1D$n%=pdw$gNmh)z^Z#i$eGrWO6a|-f*uLI}Jw?Py1v*o<(_MXSh{pdT78?VN}x19HFyH`vw_oMGR!IkFPcly0ew=hrGf0kZHyGGQVg8jz4x;yM!oqw@)c`(KAxaReVqv)lnTE0M%_PaB@n3i|^TztBIwp{199^2J7Ce7C4*LYJzk6-8c#xwNu*_K+5r$|=JC*Kd6seYAQdOcv|tcUxof6J=x4D#T)$=`Q$zQ(cIiSm}~F30|B@Nb;b{W7)&;JL|;bo!jfxIYH<y!c#w_u?wE)wf*lCHvOvJ@0j+Ip2KOjrL#P&Nk<j?>f`vy)HH9mG8RLHDCz*GOf`5aUSIJyvcLS`R2R6b$PFc)wf(H`+Vzlvd4S9t>rD(+qOql;ajfHJ&rc;>s`aRou@DIGkhHCw_fKLp9SA?UtrsM48G+)!WR4h&(qQeA^*>H+v?|s&Vqll1?t}xtIz$6rm6J4#vNh9eNFl?OOXHm_eZwBB9^Lexu0@(o}s=Gu@u*tRV!*<+0&ecZ@DkCCEZ0m-^Js3Q^kjzH_E(B%Uka6oCS+7Gv|Zve$ZIgeVI8QlJ6hA_nYcl?>7$}UFMf3ygzmA`5pDA48!)E9f|os?|rWNmit^I?@0KT`(nFi!E*er|NXVkx87gduBO)K2G;v`m-qf%ee3=Es1kV2V3`MS2e(0a%e;Z@)diHd%rp3W>wJY{_al_I%x@U4^Xc=G|CuNG+oiry@g%NW&OF9(5f!BK{mvsTk#CPOV4Qh!1-@n8#&+Z8N^`&a=53r^a_Ky}b^gaaW;A@uJd&gO3H1%v0nKOQ?w@*Ic4fW-|7vzTZz}o>^8ojX;J(u`Pv!30AM=_K(a48|W6=-66IYw_&^O=ZytHz)IS+mFW3C3C)#iNj&8Hc=i|F~*h>Fm0+y2vYJx<-N>ft`gGB4-zt@C*H4I@$hMhM2?fz@$+``s#(x6B8+yKjeYnLo6ZKMdb8-)MxKME#ceN!zX4C~uk1bjH7iZ<!Z$b<KmnTjx=m7sNcGWj@ySq%nNU{H<}L1?sWP_u4~dqx?YMbH+9pf11vNZ<#lCojVENI?ueVKKjQpFKs_~1M^QACTjk;+9qM#YtsPNkCu6FpKqP_cBko!@|O8?SNH~$5BXH<w;$<;JggWC|M`6MZ^w7IZj3pGdWId;`FVSn2;8@3JCE{~`FvY^U)+yc=Kqc63*cLx7ubVhaok&;I~WIQu^;@OQ`oOY!?!%|u(jC$KVmwL$6-BiK031*zV*3DmlN>kw8#D$H?_RI+FkXn&tGiC9-+MDd5wKpiH+ub^W~wfN*nl==S22ABjE3Uh4CTdTJ+bCQ*b|FdEVsQGYjP{&!=oJZ)`N@o9}s+y?jbsS4M_v{l?r|m`_+X6Z383=E6@=0_UBWFg$O$9Dw<s^fR=az0?Hwmgi{BZMg2UK96&snhM|YT+gv&9<CF6j>0;DCdDw0o;il{6LaGFGh;n`u9H&x!RUM)?X$i&#-B}T;9H(28VyRrw>*FJ)Lo^%^?9Xp&<2$6Y3$efe|6~Z+PVi~{?+oF)aP5Dt2)bNgKv2bYs;7meq;fxYkId0$H&b|+st|5d!FmbJP*F*`LCzp0@M?_Mc1|1MrDlm^Sh?j>nZ!Z#hBNM*$3b9eAzbcXa27L^Jv$D54Nixf^{SIsQwr~qSC8xG(3ps5tB>ddcc(x{-n8B$947w);opgKs}b{<Hm~a@GZ~NosT0?Pnq?)-o^IEg*ZRILJsU#!t!`O-#%5Zn>^im=zh4~jD?@$HuC4V1INjh)9@|N_Z|73z`quSbu~LuWBttWr|>V<!upw4-|BUSD>~~A^~;~YI;cUv;W{FJb@-O`21Zmv_?Gnvvd#hR;J?nnzF|CkdnY`<d$JGnOS4v@o~?JWJ!zA)o!m#a!cSU<>z`HmF>Wr3MLm}F7(U;+9>dlp9{%|3Sie`HHJ+DWPDDK;HY0E6^hcfyJFvqqZ+RW%{O1trv8)^M+<u4hmUSkE+ZLn#*l)2;?9eW~k9EEcRo}Xf#c{uMjQRNTt$VRusRZA$e#ZIKj{1$ITEA^>YCPxut9HzP<(2(OQ<Q)EwYIaZ*hchA?&0uj{EPLL?ww^-Ll(nt|G`l$|3i9xUh8<h1od0i|0MgC^*^43X!uKdp?}N7V*Qe98|qJ0U+Z@^aOv{{_sQ)s=KM)scT_75^;p&~`F!j8C0Ff3@K1fI_1kw3(dUl#O2<*p+#W}fcZ>D;ll$srl#gGj=SSB!O>uqF@D6;-`YZQW!LjB%@vYbL`Tw)ND_=>Jx2^}PR}1AQ+t828OKRS_s?>*{y)&-6c6Gyij=MGL*^c$S#=zZr|LH2!4dpHC)|}x{v3~vHTjyqT#hTmMw=T{(bVsbYJ(JhbWllsrqg*(jrdf&mjT@KYe-VQ`AKhQ)U)=ZaqMkjw;GgJ-b!Z7G<FveG9iZ#uPviWKJFXkF#bu5AuY6ASE#su)O>msK{e9~a-L=ccncLsDj?uHX0?HRFhI~k$)Kq_GcukZqJOkt5zyB=K{d&_B<sD^^SK0p7<HB|*BF^0YzV()_n*&f!z*rnd>-Xz(EO+8~_&3L^@9uh2^V4V=g?e7P)OV%akLRO*&yMr!N3Qd9_neD*mbSootwx<`TJHLM`16P2dT&=HtdF|52)<<<sk`a2IKO=0x>IMiMEGs5;XIPAS#zx?)2=vkp7_?gx?{hGzp;pxcX$qJzPZ}$$My$2!#LoWpwH25#oQ==E*SZI^MbBNmG!s!*|PrD$eTCboF~3@ye^}7yx(!hb-%V&c9gfQ6ZX`t8*k1B-@0O1w`}f5-@0Yj6Zp;}lQHktvb>Hz_8}|bTh>2&PQ}EV+tas>+Fd6h-rSGAb=Su9)9@|px7|;Fi#NBkZymUM<DK~bIxdoZ%W>gMmpVax%Q|!S(~Rmn1IOb!=d<~!Z*%bkzvGna;XP4R6U^=JTR-oq<VY~Lzi++0JE|+n{}PV;>~=!))0v}Rg1P;D>-L>VlTgo^%gDDOAuTkIHcp5CI0X4q@c`ECH<^ig>OaDH?eJ*i)$>^>pCh|}UX@ys;CCGP-XmBPo#5B+d>_G{{W9veyuV<d<w-F2ukU>aW6W*8`hD+HSbg976jnd^eTod(63zYYdtbwt(O7-!dmpZT?Gw%0ll=Zj^vFcN{^I*4?&d2{kL5iVpKpDi<$rv>|B_sf<vkbMvcyDl|N7p$aYpV={I9%C_O0XjjWd4x<$JHkp7TMXxxakx2e}6u`o5X<JtJGqEIa*<Bfgj9*_daiU%T<WC#&y!@5$=>-h1-2t^wcjUX^jMi~2^_-56(21mQm3=coJ_^Tbt_qMgR{L_L=GxsrX$`&_OUec)T(3v+ZDveVq}zW2!NzYm9RdGE|wcjr!XfBD{1GhD~vTi$p3AD{2X`TYNR5AMi=oqop`-?KB`rr)LYSl-L?e4Pot<^8^7-}-*v)B5UL-z!Y^E$<a3`<C|#Ju{o=b6I0rJN>(7?_J$a$DPjbR}J-l|Iz2~tBd*?1?&1edH+#ATi$<6_9qt7^7gy6vHq{cO87zbb)Mg~@K>z!+ZF@g^4?{#|7$9($MLEf%7-Mtzg!s4p;|qL-{Cy`d->G&BvimU#iD<~pOZoBw>NXF^z%P>2)|txt;f|h4eIUih`;~2)?=%k6@Jqq$P123$^PxP=>JnU(C;_w@cZ3GJx5DwJ?^o+;itZ)zH`zQw9n!N@GCafc?^5+QR;iHZS(j4jDtVxC-~=TsqYweQ+@j<AK`gkzI^I?>b}H&&8QClZi@Zpc5@~4fdA?h*6SWWi0!#N4bSx(?#BJ86Ynv(mu*1#$_L<QXrsRC&>56}c2IrS@+o+)Gx!?H-#Wng@D_Uha$I^1|I3qjzII^))+yHd0P}rqWAR+O!&)5If%)MdIfHt#yumufgVnIEuCB|kyz^yylwb7&o~Jj+f%kU*>WcFD=i>Ro{*maf;q%~6-;V3aN_k!T!~NcB&QR|0y<wq-A(6%iGP-v%z0xeE{PXF5ztY^R%>S=fnk$yB@c;Ts^QaVt@vS!^sb7;t`;#Nd{TRZ%seQ?!5oFO`WYKQq-sJ8K;V#t9WKjoMv=g}txd*i)S+pxzbO5;rc_2f0D0K)~bU0b`8?xv~@=)?HhVTgLXtJo2EINujifuQ7Av~BN+=tqa+>dS4huWRoo%`R1A>5PNgWQumh&qrwkoz!*I*dGw+cbzem^_%jAw0&A=~8cAFoe4?gey|3kVP|-E0WVQgafIm$)X>S1IZ~F!l|eql0`ozry{3e2<M>YB8!$J=O7nj2-l$2CW|&F*C2nz5bj9rOcotX?noZQ5FSVUj-2R?&E8l-okyO>zb~PFM|M%CQokdA$9ktSguh`3_o8+tcjk8YVhFcm2sfhECf8=WG-3!>Vh9(a<|5}}yBA^zXJrUyqJBvJko}s8A)JvR{0TKRSu`{G6LKDga2;wDvS?3o9dciW@I>ku@*?US>KL-<x8ynG*$m;i4B@d1;Xc%EWYLP`KIG~Q;cV3OWYIu!Hu6Ud;k4A0WYJXQwB&RQ;SAI?WYHYt4CMR_;nLJ%WYHSr(&Ty!;g-~|$f6y|Ey-OO!jaTLWYKZtNb-1w@O<h#vgl^=eDYR?@Nw!%@@sG0@y4Ij<K*KkBm5WjJoO~`B<ng)O(dTu@1ZUs`;J>-S+}{@8>^^$$a`336?H0k6?q0jcog*;vS=^zDDnV?a2IMjvS=f67jg@Ra9wI8vS=Z4U2-Xga6xKTvS=o9L2^EZa9(Ogvgjw|ykr|gxF|IbS+owhC^?)V{57>NS#%=#YjPArc$xA3m>2e5lo><4(UBqCo*~?tI+z^cjpp9yM{P-N$-nob4kk~gPNxng4`#j7sdLDp+sM<&8yLd-sYl78|B&~SZ!&~)rGS2x0xa5yoQqtIA>4%8hAi5a+=SeiAskL^O%`oN4ky=R2v?%kAd40wS0Wc+2!Be=O&0x-{3-ce07Cd7^?3kT)I)wqzQ7RPP2ERcMUAHJBTu5vW(aR)2>(FcN8ZPJe_#k-V+g;dJ|{otcE9Fl;dBh)Jk;Fe+-#RT4B;{i;X2eB<Qi=EIt<}f4B-yc*5uag*A5Kf_6*^6)HdWc%$s%$;ie4XLe$U5pD`~B@w4z#hVYNnqvWH^`yUy?+Zn?1sdLD4cwEh=4kyp04x<hyi*_W7b|8OEZA<Myu1>8<?Lh9p@7H7q*J23QptdKAwkFpghcSe!Qd^Qmo0CPWkVOlVtCBxw2xp~cBa5aaXC((Rgr6ADrv_N`2Kfp3Iz#vj^(<M&)&y_tq@E$4VHx3F)Sswl$!A&DPYmIk4B_Y0r{t&H*5~{zoQffwotllDjct*gAsoUGu1u{$uEMsi%n)wI5bjNlAWxu9q(+cM`;mR;hKUT}HPq>3(G6tL{p2;|Jq+QC)SF~c8Q(ARvv6jHa9L_Kay5?cWf{VDhHx0QF}X3v_b`TVb%t<dYCUp2j_;Kj!l4Y|U}^z!0gms%4B-zL!v6+9W!x7QeMtV7e4QbDj(UMCx|@8C9M2GT1-w5W2#=<I%Mcz*T}2j+Ci~7AV;RETsk6zV1IYEMUs4B<%TT{!2uD%}kO#1?NQUq%hVUlpX0qrH<W1y*4B@NPYh=;a<g4Uo4B?bKZ^^kTCC^!T$SKJ=8Nx-VWyocCPAb9>uF4SpirR|Yisz)S7{V<X!p*7e$?bVgYR(XD!4R%XZAxy+b5dP~a9)P+-2kYZtAs^=B;O?;VF+)fZYPV*C;QGxTN%PLsKdy<^N{dV>LBXZWYM<dLF85p;c5Zz&s)MpsG-#AWYL=BP;xPba7k({vS<x*Npf+9a8YU)S+puy^mDRkR&r7Drwri~)IhSRoQG2Iv+yH^a1!-8`8v-%Netm18NxBt1abn;VKLN2WYIa~81g2D@CNE^vglm$2J%LR@D6XR@kYEiR#M~0as2yAhVVk_T=GKl1nO9_Xdm(fa({+!18Q}$Xf|>K@@EX;PpKb~MbnZ$C1+s>2T{|JMKh3t$iWQZP-=d%XlZgNIgBCPm|Bl4+LGLu+@2xao7$Bu8cFU=9>x%!LLE;Qoll-ZUd#~QM%_vlJx<<6KFSdGQ16gMUz0uLe;L9b1VGaSfHP7vQ`3;suv}(-7S2iilPn<|9PobbLpXN;^e#V(f0uthPrgh3mAZ%gEBQ2aFIjXS`84?#hVTXIe)1`*o4TJIOI=UhPu|b(uV)CarLH2cCC{SHAd8M7&mxaz2oIqSAd7Y(4<Sb|gga1MkVWf~JCK_&gsV|YkwpuVtC34EgbP#ikwx>83zI)*2p6H+$f8BbMaX3s!mX&`WYMq5t;i!7!qccxWYJ~hY2@Y9o#f@@Xyg4ofbcr%Zt5<w=uhO`<ewSBx2QMCqR+{<$S)YesRN*LZy+q1ot&DSgCSgq8bTJWOfE#O$PjKyZAKRDO>Ro=#Sk7J@cy1bcp-H$bply*B6%@+HFXVnH93L0hb(%LoIpO$5Dw&hg4`Pf@*bfqIgtE0L%1T<PPX$Npdv%K0z<ewwK};v?*Ym)giAAo^HW2~p}Ysk&k+8EA^au)`T_X^-XFYS2>;CxzC^uF7ClG4L_Wz7j-$qtMP1}L@{)k}_X$fF!V9P)$<wH#s3XY(sa>ff$s_swt_<Ox4B`INZ^@!#$^FS)sNKn3$aMqW-+Kt>rUp~%lSRKI2a|IKyuUy3ol}G}Q}dEDQVUY^lJl}$L56T8hHx9|S7gyhavSmxhVV@4EVAe(@=WqNhVWkML9*yo@?P?<4B-dVXJk>iw|T(N!fyi*!a=<E$w|)1dz&DJa6X1`IcimMRo>f_V+hw~2-l~!B)8<fO?`%N1BP%zY724;-rF=}2v=bU=b+{#=jDA*4t^HC!4P&+kB~*TlHKHu)EVTB<dp&M?`?#aQlqF-$)bbEQRF@h;U?5pWYKEmCgk!A;Q|5g?}dZ|yzyax{HFz>>B;H&_YBk`WYJJ^2J$Bi;Y`$GWYLo3OynSja29HDvS?AV=%-}S6yz-AcLqZE0afmWghi9c56D*-!iT9pl0{?4qMOK~8_0*r2N}YLs2j<mJIIH~#~8vVsBvV`c(Uj@vgmE{3Gy|D@I&e=vZ(amLuvq7LfD{}ft-PTW>7Pc4f0z9A^e6KL=Ivf2xnnGykTEFAip8sV+dcOULjv$n_i+GBp+nkU1A7dW(Z%U9wQ%P8(pPdBVXhGUu6jYLzVsfho6P-Q)Qp;bKl>P-*6x9Q!kM(ahvW_uaf_v%4b=lBI`<IeMt&7vHYv&g)h7j?v2m9QQ8}2z44JZ@^~X1`D1?0LoPx6jQknDCtQkJj#`#1T8CWQ8x6hDn03l`Y-C>@r@V2<8;8Ad+Z(67amE`3y*rS~8>zifGX*|}c;gFx{*obF%Nr%Uk<}X|soBUS$)%{-$)(7}saeRy$wjFd$wkS9sUMLGlWkOkY$Io)J_!J4BEJlP{y~08{*8K^{2TduYApGC@>=Q&@>=qDR44g6ayM#cayN1#Y6Eg3a(-$)a(?nN1NzbcO9=l){hj<9`FrXC^7rHw)Yaq_<jK_O<jLfL)RE+Y<Yv@P<Ywe@)Gx^8$OWi&ashHqY6Wsma&~HYa&~fVYGrb6atO5+IfPuC+K^nFT$b9DT$Wsw+L~OIT$9?CT$5a%>LAxAe@X2@{*v5=+K=3Z+?_g{+?_m>>Ld>(PomBwPa-d%E+sD@Z=r4{Zy_I{{y;uLzDWIpe3AT^`ZxJ8IadHQZ2(w8*iNlLwv*dYTaeq4`%-(5`;x~|$B@U7mr)mymyu(rTgWlw1Jp$F0rD@@W8`1Rcc?#+?~q?mFOy%8Q>1|2B1;ITrT#^h5Kd2hM3xZFKz&S>5dN5YpDZDqhWaO2LO6h$M3xYKMeld=EAl<+&*XdLE7TL@E9A4(UF5UmozxxVo#ge@<>d9`dDJQ7dE^n)Z^$Fa4r(WIc*B4cL4p5Y|0|~V|70vS{Qk#G)^GYRcQ$|Xg14^Z#n0glQ^`6$@3|(04vLdym6Gv)0J80Wa{'

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
