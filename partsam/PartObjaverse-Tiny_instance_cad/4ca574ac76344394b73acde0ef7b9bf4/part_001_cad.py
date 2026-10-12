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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_001.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_001.stl', 'source_sha256': 'c20fb051fb67a7c3f821ac00b4c1f4612e86ae8f5a8bc1a9bb95b7610e381373', 'input_faces': 812, 'input_vertices': 560, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16089405119419098, -0.18756911158561707, -0.44015926122665405], [0.45066478848457336, 0.17216825485229492, 0.12365695834159851]]}
GEOMETRY_BASE85 = 'c$}r233v_H`^V>oQc)qbr<O|*`&Qepw3$|G->Q~cdo@DsYD-(i*t)1K)`;zj79k?BMTlewVkZ*RekrP`meSJA|D5xF&oy&0zdrxx|Mxua^Zm^Co_Wui_ncYo+_atA=E+-3qkk2&fyF*-t2JcE;svdkHZEe+m_gwYqiYWz`H4#_B7E@=I=@5L_MLjTv~k+_(Ebsl!$*a_>JDu-ph;*=cj$l-qsENtH~jq(qxwg1zeT^Hqa&C<`on%BBiMG;hK=ghbiY!qrh9_>|M)ME4Z&S2dS5zIBXr4@Fs5d+w9V-bzV`6=O5vXxA$<3hhxYc0FWc*pErqWS4kkaV%w|Xb=9gZ+?I}~9{0hTt?Q{8P?~Vx)zPX~xX6}1`Ny>EcHE;GFvHwp`GlbUak;Hwy$@0xkzE=JE3cl@2zaxCJOXOzj@v6QYXD%P(%;n2^7QG~V->uWs@9fT*PQF*~e!$5$t^_#ysn6|q@_lu;>~qXtXnTf}uTKeg^tJZ~>=o-{-dQ@X9}e5bsrqs}-r!Th*KVfUj#n#^DSXf2CyAoYueMAS?O)wb{tMZ*`m4UIe=Z;O&*h{3-k?<B8=2pWevLgLapHIjB~kkkS;E&6$|pJb=B!HzPQFoS?JAMC;2Nq!$#lxI?#Oya|H7cPV*PDfLF37&y~VnoRo}m!72j;%c#D&7Y`(o*)H!ge@V)8r)bFG2s~!Cgcd0&G=2M<-Q#M=YOZDZvtG=9fBXI(qU#IHY*NNi)*Y;SSsxQ}}ciI>l|MtOR{Cep<Nlw0&9J5gz@6<t*ukU*_kCTGpoqR1%=o;b2_onrquLZR~67!9dZ+Hh#ohQ6T>-=dD<%zhv$m+{^m;HLi*SFPQ=9j*4+h?nr>ig@~u^Rblt3)2}ku|1RpHC{#dAuxblc-OH$4O4U*{QOqk1sZa#u>d%_{Qwd#5ldbm!RXlv*cfWZAH?zVxCqNru_3iqxKh`7rxgWNb`7e*uVN(&iG~Gc<$d8^K2%(l4$MM6LMMj?(P*5t$EC0CxovZUYlTD52`QMgLlzh;d}OtPq5C5>dW=u9h^ez?pj=uwa%*Vx%X?Dlkfg*?lvc1D?Dw17~jHVI<Df~6Kv~E@#T6m(zns|IK`m#pIs}>$v1<$Zx{8wF^~NB&Tka`;`*lg^7^I+eNOf7oIvey9n0n8I_7<0Jmrb~ihNvWa{2N)17CYGm-@x^-(7H|@bzE&3twKJy#*queRG|BdA*(8Ra_Uf<Gtf;bx?d+2k+^7V&04;EjQZcOY!A=Y1Mq>Un{px<j3=a>dW)poN$rWMQUW6@NxZAeR*E1zP!KZ@^QYazP!KZ%8%=(>dX6ku5seJs<&AteBY59!gtSYo$BOkU7PL@`?rb`zWLMH_15Fnzb+tr{kzwMZ@e9o>f~!HZzntX{`;ER9_NcYcy_wzw^EC3qW$1{yTo|o1_)pKX~k->{o3y-=?=besT@6zwXI5dj=lV?sGEGARDGQ9p2@AmdU2O*u-4i>m;c||FVlBA`SN~keiAHvPs?7bgx}};)s8;K@2%W@x2R8%3CY$vc>h`{>g^f*lUKBliQa7WwdB*H4%&e4ldZn{$zAgA*Ri$tymoqx$deN(+Usw8N_o0f|3<XmuuhCq_2qGSueT7sQE>G#>%6GGzG=}qF^*4jc8TNuao-YJZ@a{Ejr8^8Q7c6IpYMzDxZ^j8y6OwutE_caee<tgl)q+8(Z4b2;6`iR4E+&ZFKfJ%WcAJF-Np4luT*xo*p8}kG2O}EpFc;OCwT{N6?JG-dyyFbr>~28O5Z)Uml!|0!KDa4yQ^65#`0dvg`b?3X!CELpmm!VwA1RFhaS*;rMYbFwap=Po_f28{6<6|eebz-LgY6+p-DFXU<Inr)$bCmzBg*=YU?<qZ$_N{mg?mZzIN@dxNmqa`)Hl~xi;PE`{HWQb=Y+$O^h>OuDB2D!|RLoTI~;QzUR%MbY0z4TKGnu52$^)N;|Ce&*h{3=D;EwgulDuLXqdqsMs*8-(|;2;k(PydTCNZ+~2fi1rAvA=kk%?`($4n&DSKF--|`)IsxDN_OCI*zdTx;2kxHZ#B+_ltLGlEZqL0!$JM9aVyAIRU(GLlHNQWPa$J62sk8Le`SSZ}{o$+gXoj?=>v7?fz1HJ0J+Wh)#xH$!{L)v)DSdT3+K=lyIjx6WKITjM>ip*N(cYbAJbc|@Ui`jNXX&f;l)hRwe;#E$NMEg|JFQ2jFo)yK<@?7^zIwd5eA)imvN2%}^CkUU>lwZ}U((MtUnwmYggLE~zw0axbEvcQbFClvxz>-&qs)unSJxGMb-w(*GJff+^XQ2&=)R@Qqp$V8IH&PTUmd?^Q_=NK^Oeh&>v>1v4Ni6Q`|9=W<baJ%>nE2l^LL)J(W!3ISL>tKznkDxPwA_5(+dTP`=NS2^83pDNc!siNc!si$TPkxy$4b5r+#0#pGsf7pGsf7pL*j5Z57+f{ayO%{as(*Lp-Od&kwnL)L*~#aJ%r8=MZ0Z4Z062&n@nXIrN;OJ}<#npO>^*v8m$tl;=a~tIvnhSDz34d6efv_pxr`c+}@ocgid}&y?qOPw%Uy*kAcRWpunPt{3Wi0C$&y86v;(-azkKLip<Y3PTGKzWRQ{cfOhM)%P~iSKr&XuYM?e^*xgN-L{9s@y+wl_n{x^pK<byIWL{C`etaRc%C&zj63M$>kW$1brrsmw~Tn6^>!I`*4o||c_QiGd^NxH)%>1!$5HzhQ?k+>eABhsmPgC^M7$p{y+yKZ{_LJ&KFkG+Gp)Yi3KGu?dWVlPZ0!fv9pdC0r3cIibI7kRnIx`zdg1)1oO~_MZ1Fu>FL0Ui8~I-r?K+&xu=@JauzBM6@>CJ+eGv^0i~b&r67Q8fnGZ8<e(k>W-l}CIdJl5FrSOfJlc$I}rWVPt`ewCh(L$>}5#Q5&QPI>s?4QY8y;(CeY<|u+bf5gvMep;ME)l-=$6ab)ZB~ZO-x%__7=MR0Hs9Rs6?uFg1=#ZF(aGX^Wh_dk_XeHTkbn4ddcW2uY_HWf8b{Lkv#O(*chBOj<mWj+@7?A%-fQ*sQ>O5ZLHkmyzBY0@y&vrUN`kF@7`-<%N*;)^`IpuRU-MlT^>gciM?}9VVdD8+3x1v6i^12sHx$0Re^!dsH>%X7=lyo=6Kw7GRi-?7{)n>q^WEhCmMHr5%q%E;GxecuJkr;z-5`JMPO*;kz>dP#sx+hT4Lx>6TYWR59{I*nT6fvqsQttt;`_W-I-cGqz&8p8(eG-9>(KkJp*<+i*;?YfGkQ&@=L7iK+Nx`;<8cShr1qZ;72iv=gJaiQeXZTVIO}-yrcu;BxT|=-W`0ng-V4Dud>!e%TmGFXHh<#V!q?`POR)Lvb!tC%S(MGc(~#N^3KI7#v*se|SGn%_{k#L{`}(2xQ>?!Becf$Ney;1=^*EZZt{>UzW{!=gJfmI~*HyFO=v1q3)Ed3T>U;Yol3zY>sqkm?rQbo|Ya8QZ#QD4=ntmVJm_+T%^rQI=dneQCYwPpS{C+co&b#V6sC~?+SkXRTUaF7un|w%q?dxK`ys<~f&t4|pYiLhC700Ddxk&jR%%I<U?k%wUa}Dy3o}+m`ryUjjY}hE?I~%*_&^n2!dDL2ev*%yCtiG(j^u0sdQ~TJjZR^dqqXV_yUz&b*S+FMB>YMcf$xr=!o~`}XQ*^#89%;`r^%(i(qG+8z*Gc&L{U!8%KTfCX1AKNPqW1&~&!kv=v(F6juk=o^wXZc@_(o>XJez;yQ~Eur{xZ6*FYiqKmRhw*_-{6+d4zA?pDcVmitfMO<#Whyz1mi1qjwVdeaGA8%kS43XPYl=#ZloK`YhYLdyi+)IRCgEV_To_jW1@|)~7Edo5r6%+_v7NuZ?-vw%+uCIh1EXW3g_{2Oa5suk@$V@91(p8<DpuPgHN)dFM@gOzm-fkk=W%U#6+;I^*|u*0o({{Qg%pY}Xm->!B6w*O@7Wj!_*t+t#P_&2H^&*F*Okb&gq&*L!q5J<mu#{RAB^uFsy;|DildLAK-d`$hrV_1Sm4t?;#a6>awm>6^=6wB0YXsb2_RZ*atRKl1yy|7wBzMSJsl6pgc93EO>B`nncuyKhQgTanLp-}JX1=Ca*4{p}0>PUFOV)2wlc{5Fei&k26N^gP>hg7nSpU)Y`#{Ov!VVtY>T`;|Vn)j=Qjn8xYrY<r&Z`x9Hyb*4ajIv?-+LG@9d$NawXJm$^!C-tj5kNJJ&c})81^O*G2=P~U@!Q&#&`TL@t?mN+YZGOvZROjT&v<{cF6uuF^kk-|$HFp1&A$<4F`E-6ocOYMRUX{N3ys8EFqV{VVh&uafKghKCNg=l9VWZ{(%2TAjSSLofH^b&9^q}?AF_HcrAbL9;m-2iref9a=?K?q!u|o8_<Hb34ztdy-J~D9`J%@K_eM0Q7e6LY``MpN^#?4OR_ed=^Jj=;9FP1)J_0{h|(l<9vqjmds<|$iy<@=F8|M>;cqWz`f_VFm+oBVlvW9Eu^$(whd&42fev5vm-J<IQx**-1IVVvssFaL2}|8cI+!H=?>e0RGe2duvOeNFY{_chPY<h!FfQ~kG7{Z-%iGUSle*Lzc)&EqtF>1$J$i+Xx)mpEwkjTxgv-Sj$n_SxD8w;b!}&rBBeQS%#VSLt}`{Fde9n;xozF*%L$jQvOazNDpIpx<w+JtQB`pV~+|f2A*<Kc%mS<~u3+Q{FSEzI@LheQm@x@%y26>;7pc-}_x#TYL4rgx{~)i=LA!PdsGx)%Ozq_M?W;{ri)9wsC6LFK_ubU(K(+-%$N$?>Erz$<6e8X)iin)%Uh<cf#sx@jdBx+3D1;-(Nn0#((<W8JoZ3!j^yYWghKvUGkqZL>}Lzp_x|SOe?s}=5K8#eEm;T-2aRgZL*wve}4Gp^>pz(X}13Ql-1XkO;{-M44Qb*=8u0eLu~&sVV})^5If$<Hxk$_(jmWbt-iQEXf1xoa`M@ImEOY~M*cH>#Pg(4Y;u;9?<tab)aF+iBCeBK*?gy*eDBlLBQ}4*(IJlQ;pb}Kvi|5Wr}4m-<MF)R<)rQWtrRiC>Kh{x>37<Qx9I!$kPjT!q3X+ZD1CJu`h8^``h8^`s=j|c&mTe82j#k|`trIeeRUnGzM5aX4ohEMpVC*a&wgK7x6)Uy+y3^-diMLudiMLub>5#}S?B)t%JtvhURnRDFW0}{SMC?8FYg!LeX+LnX3l$^{yuHPMyhjSfAMz&MvpDx??=q7<QvVx>F*9w$@lg-V7vb4+kX}7U;6U;BYnNiA=`S^ChYxE^z%<P^*f<G`9;4I`F-hyvYgIq)tBdy-&f9S)tBd~-&f9S)z8&lIj>b;j>p?AD9c(;?N#r`LI;rVuV>ZG!q*R#%(BjlezZrL)%Vx!$J6xu+qGeqt!^XdM2dP8_{f&ucw-=)XLUZZjYoepfZj_SpJ~hQiL6ZhK3QzffBQ|!b3V(K$6aHw_&XcZbIR7Q@A*aa_dV+$+w!<CO{MmKC7u%Nq-s0*yPnJECyTn>|3mnOH(C50n0E5B2+?o(KTlD8wvm79E#d1;D`bm2tyYS^_tN?|4j28pstDgG=o0HwYtqCJ`Iii$_TwJXbIanw;`c7EF(%tO9(`&n@%K;Kyd}cdOFt6VPvdM?df)Xk{5IrkvEAtXL#ZA1{EgyfiE*?@%eEeu=je8NAGw-*d0b|PWa0aonB;$bg~pHfFupI&*~X)lj*JrRzC33iPygY<*H>JoJU!#+xl8|;et&Ir!&W!rKWk|`(|@$p%~QLWsDlxy<=DnkESd7p%Oia6KTYZTWTTq#R^Mn9y2s|1t(9Y~kC7ZG-it_Ij#InXc8+Mby`w$<hRumq-=818uXvvvTYc81(R+xu;G;fz^>jLqmW{WK$JE{v^)O$VW;<RZuUE7;56+=}&lRG-%RbqZ#slA7>9}e2eLWXqoDIY{jR`l!@7CUn%WUKEwc8}ld!yiT+xXr6$ahzawbv&ob{(yw4Ewz7TuJR${bFnH+wihDF7LL3r^UGDcA)o|V`lHM`r5Ekd#t{3_sMDN_`SR7?^(@>Pfy$GaIMQ8tM9J^e0RgXXRQ4i?TR0;`m$f?>*XI^5Or-HK+l)44aItJC!M`$^^IObccpi-{nt}lH;tV(w~D6mD4-S72K2N1r&HYI|D-zqr&EI({ICAgsV4R6|9}6}sX76gR*gk%Xa(@cE=^+t);@)f2Y(7K1}zRQ27VD*6l`GsAZSr=VYHhJ9S@!iHlUw?gRpO5XmK!)g7}<kAUFtYKtBf?;K|T0z%L^2$Iwr}1(0_s^b7Dp?4J)B2wsXd3!$Hb^Px=vXhCpsR_oF%N<c%vCBUz^NSnKed2p@|eG^;)ZHq(egBzor8##C`&gIcxBNr*p(+KTC@OcQ@lt(+>rZKcRxEA}YDvO%XQ1Bi0*)Dv}m4C+hHshTx`g|waaIT5ZWScwS8pyjAIe2@{Yp{Ry08-v>bwnuk3&p-Qu>UUXw+s8OLBFBsGZeWv%YEF?#^Cxm{^F<^uMg*V<f{j51a5$Rw?Nl|>!D2pXk+jew28MIXFS%>JQnj2oTH#~!BOB@(67O>z%!vUz%#*fptHeqz>A=Z!HdAr&=_zucnNeVcnNrc>)AQ806HJc+dq%bxfTHP@wm`G*F0c;ywBnIxaI}(bC{oRg`ow(v$5}DXnycq?E5t|04&eddC=#;i?MGE^m*{t*mnlh1x{eGiN!kTdhj}M9E**Z+YQh-a2(o5pSRlrO#*KLZ-yp<H-i(Po51oMt`1!T=Hq#yQ5&v*gL%JyYBUzEe}MUCyv=6lKVbeDZ?g{i1kBg8=A!k^^)KxiKh<cP>z`nri|5<|eF~Q6h6d%n%=ag9a*an{k68T5;vs_b1L%G51Mn}<pTWO?@3APyYE+rUKQ7W2!8|y-SOl>s#^NUz>2qKnoc~}tg~eDFA3!^TKLA&OmIPM;zrdm;i?{fEL0<<~2UmqQ1Xl%zLEiv}f!~340>1<95A6x=5B5Oc1$)3Pp>KhCosXdQT#tfzJu^{nu7|+9#s^SmuKU4{u<x(X!<P9wgnka8kB8W2Kl<5^KIEJpL_Y`7$Ir-h7@r@;XZJCue`3zLmI)x{^ZWwlnyY4+_dv`&*CJpS+VFfDa>?~m5&0@2*Na#yKe{L%*FfavYbOuZ57*ya#C%L;urA9WS7r2F1p5`izH<Hjj`jFE`r_P$#d|E8KwkwnWzm(zf51Jk-4)yg`W|>1i_ch0hfV-b2Y(5j2>y!2B<wc{`%FVj$LG^6ZM$GBUBOMTJr;S#KtBUdMcygUiC{k7a2K6(@8KB2ag6+Y3kAQ5?H=&L!A-F}27OJ1P6EG*+*QEuVS5V3Fcvxi%+KE%E;@I(wgU6>tDlR`KdupAex7!A(Rs{O2lMm28uC>`uIk9u3i(<gmj}5bkS_wcIJZE%%Fr6%%HWrw)xa-<UxVu4*TCJOox$C~gP;-MLEwSVe&B)N7SL8;9&h7wt^>e4&xh!TYd0_-Pcw{{Yeg_Wu1d&P3AtJz*8t=jfLw!+s~hrlL$22_2Ri0KM=dzFN6re+O5h6MGSG_PGT^$<X5hNu_o3au?}JA}KLn2k4~Gr_4+po0z6~D5;v*J)p?xeo65CvRTX+Pvx%L9LW6_qyFz8SVx4|~oAr@|pZLWjCFR=(=;f9vCaA|CFEob3U*ydUm+!y1m1Fdc0-q_|^%fh{|&9x?Y7{)sa`jLf)V0#GaB6%>j2ct$KaSY{Ar}C(a<Z{?9hq_2Ei|w+gQ5zgXZPckY>LR%owrim-AvliG@M@w)e7i1km4Utlu7I(&hqeO`M=eG}M}gl*t?NSTfXg6f1*jX`9yy0Yhk^My$=7{lXeDq59D509S#Sw(A!sRZA#f<PCO8xv4($aF2Tz5L08a&vfer?b0e6752J?Pjz__@U1oO{2Vn429UC-`QQ_w%x55Rn!RgkX=auq_ZlE_yQxj6ItB)_kG1)T)u_aJ_sYyxhI?a`RK_o02kCE2sW54@HE6r7(Apy2$NMSjNLGA$TD!8ss+g7YyJPgxXY+kb-#1<*DR&Q+i<gR6imL0<w_0zYw){^cU(!TE3KQ}Ayr^09Vz!FdB{n+NAo(8AzS;9zJ0a4`6|i}aR@m<Q*((BHtkeSYN2kGhn?@ju3Rx&8pIg8CMPJ`d*kzeT=pQR`rgKLE$Y^%(l)^(l$^l|-&8Xm<?bJ%*f|OJQvJpaI|~7+WRGb4k>`D8}|T*1==cIfKPM7JH$4z+6o**L3h+a2j+sI1QZ2BAZ1Hi&M}nFxQjdQ{WTm_d5FIdIijLo=2ZtuUh)Qi2k^K2i}8yP3UFIF<iy5a{V5>8~dh0&w?}1W*_uAI2CQupy$Ci(dGv9d+-hLHRx6FHSjs;dGI;#Y3Nz-Y4927ci=PN3($+;3*bx8%iv33AI5nTb-D@f3iL9Vk7otO%QY6v^RGnzT$h9SzN^p=S1<S)_PqgJ4L*Z?PeYf1Z=lUh=r`cgXmbv_0(=R5U4X6xn>dzq=tb~N<n%#Tf%*E}?xJ<cb(`zidQEoGy5_nAd=hO=K(~VVnomK#6y(anK0EOF4t$n_eYT>Xt>}YuB#U4c<Df;r@$9SUGX8!A8V%;U2+Z{xFxPe9&EP~9JNSDb{xc7YjnEhb=LHDP^PzFz`Cu=Ly(|v0*vH~1^g9IS%LvXFp$EYi!6#W9V{sn+aJ>fRdKJty2h8;lcqf=2(>(rL4*y*S`lW>@VVmn07LLL;*E!%h*zXJIm*6B8>rqRt@!-XnkEP&fY%gT78gsH5^TBy7i%po1O_-B)$hj1Gmm)_zaxO&Pg~$<&eUq?%62_7UpZAdrU1Q<Z*yg&@!V9sz5VerJ7~6|cU&%|c&2@=|*JGRO1`8))n`;U<3j580&IQlMXOp3mzzgu%6zF8|6tDrE1eWVN1-bzogIr6X^T0f(7kzqB1I~QC??A0~pq6WpGX{BMkYfY#Ex;HSV0;F0#vyMUa;!xC`P_U1T?d}XVkV2x(67O}SbWPO6`BCP&EhVL>rfx~M;3SR`5k=5`Fj>u@c9*d_9H%%`&~yn&ioudtkHSQH3NJ}qjUZ;_$;>hxqU*TbDir2Fu!i>(dhi=nhE|6`yPcJ24BR!m!X%mXV;Ys<jX)V&U}sWb07tp3{FOy6lezc0LG9E-2=|XxDP-x!B;SjZ0HHF4`aImy#PLk<MBZ+fsf!A&q2?EQ!ut8(8J*C*zbGj74RMKPtdF2pTPH^*T8r1*<I*8Fz@3S`scb6?8Cn2py$E-m~+r)4*Ix)+U-ECxE=zZ!@ftL$H4cH_b${2K7f6*p*i4#n2VFp6X07ceqiwn^k?vX7RNO@N4V|+n=E2kq#-!3KyaSTg8zNMZWgPc%fYL_vsk>zq9uzrps#}80Q3LD>VH_YU=a@O4CdMs%(V}gYY*@{P`=IoKdG%*gdx9<{@(<*g|-2=1$Srh7K`RA-bOS>Zm#XX?|{Rh?}54Y2KPq3aA+Ga*KT00y}(?%g2TZdKwE=900&}htuS7$O~G%08?$J}q7I8%&{E)9;9%&B;1Cu?SUiv5TmTvj4o3R|(4ye_(2@wwB@mp8BRCg>76lgrmu4}XMNJm{5j8Qc5HKIhYb@%rs0}R*t_|k7%CacKA|EsWT%JWa7I~og!TIrd9%umg1r~)g`o}e|_Us>L7xX!>3tSk%If%ss7Gqg_1|0+b4E#BQ^K=&Pv*^NN7=rUq1n0g8&hKh;zVP#>3A7-%3AhG=^UDa%)iqi(e7!VBaBc*x4z7;&jS!qGBRIP?I@kDltRpx#fK~!G09S;%!EWTKh~WGZG!Xm}xB`OnD+tc~eCKOyutw{y9+-Q4{qQy2A36@q*DyZ^20-h8xkiBb`sC~CLug$v*MVT(*C6!A|NlRHeMf4~&W%Xu5bzMRjf4&Y4?@03=s@s5j3p8p0gk|NL_)`b+q3wDMJV)Ra44AnSyn$5BUyBWjsSD@fIEUau$aN(D;85(OoNVxegz&6{**;07Nb~HgMI|A2CmBDCW})n&Oo<=&w#hGxWVEyi!21^Z3xa=SUhI&JBvpM&JPisAF%k1#eEjP^0Bpb1r*Ek-~LzN&;Iehqta~uV{mm(`=7yC_k5k@^8Zm>r?$`W>k7ND1c-w#!0!;+{{TF~tDF'

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
