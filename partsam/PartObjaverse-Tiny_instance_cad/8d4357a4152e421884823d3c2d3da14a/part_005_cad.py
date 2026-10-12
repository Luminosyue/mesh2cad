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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_005.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_005.stl', 'source_sha256': 'f3321c67bfbcbc0b5b7d500b1faa8c065ff2702586a05b62d8b152444c53d5b2', 'input_faces': 686, 'input_vertices': 423, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12239214777946472, -0.49999991059303284, -0.09268073737621307], [-0.009537573903799057, 0.49999964237213135, 0.06573466956615448]]}
GEOMETRY_BASE85 = 'c$}r22Xqz1_s2Ih4InK+Iy@8z(nPv|WDyL68fl@*qlEy0Ktd11MQNdgNR!T^gCe37kzy7V0Vx6sqCj{c@>8T~6cB^__TKxQuy5dh&j0-XIp?1F-p|~*J3BjXc6Q%8iE5oQSEwO><&9CDU(H>)vSE<rH$sik0}@6K>Ng;<#<1bzf{a4U=}(pO+I4Ol)h);vZ6t;DACTBDA*`V%tZ__(uxg&LnD~T|34Mn3j!)=6fOtfoxWoYtPmJv|e1PLuu2ZXaHBapqs(B`Q{*Qlooi13#I;W>QrSFPyk;`2-)`vT#eXBfkyZX)yE{AWNPux2$l(|)<AIJL<uegzwoZ-%6`1X9p?RVATcw>a*QQZ8fWI%rVMtkPQgrUs+``(<v<qs_+{?Z51&l+brzvA|ga~G)ef}1lg?c=x{HKm`Q+}Yyh)~>?RpE`p%zvAYOZJfubE8J**Sok4J^8E1|=TY2>u;qNg{adFqx1at@;@2Dr;NA`knVT4g?D(@)B###FX&b}+u`oWq2AlSB`-kT_kLT#A^=|I-bmDm55#jy{t0ey2Ida?$jZ?TEpD$%@EWCG~dHHZYUr%C^@OD2+{~Mp*%-6TTq&@7<{Z{fU{+Ih>_DW`MFE}lE?(bvnX?blo=c{6Jyq)#!Rvx!^|HItxpCRMF<ahu#E1b@7bKCPHb0ht8Id1*+0o;yjp5f-+lM5wJ@Fh9!pC_iLySSAxko#%e749!LU-F0iEazKdr;I<i-FCB#C%FCEsZTl2`0D}lUvY1bN-_`C{J-3fxskWD^fPqI7H*eZT=**&g@=SQw~rNNZhKpE9=mUE;hBqfaopiwWgHUfEC_dTYyT=4{}IA{HR5);ucP;cyPMtI|I7}~?*aEuh>-kGkL7sl%$N_-UEHcai}U-ztu;43anEya=ihmJ6!*SVjnB&i?l*s7ZjGEI^Y+#JAG*0`<$n3RHwB;bGjsnI`TTmGD#qNCkuLG8v!tJ0(&YMn{Rwl^F3SD1PR^BizH^rJvxv+edsc%Da{X#Z{^$(3j-_7S5bol}G5H*M!F{VrNuKLrGS1Iio4H;8PCGf@+^w=MH9yVqiu)^FmOS9bE6thv`~&5<U5$-y?%6v{)&X$q$0p3}l}}xCbF=cdJGdVMvt+$`?q&A<qdySd|ER31e_!72=EmP1j`xFGXXBV#y>G~ImyKV;pQEtB%<cTq($DYX1Gts9uf&7fA$^6P+93U0dULg#d*A<1#sS<ns=4%c=`gvDudUn0?Y?X(d2XMPd4>6=xc~iw=lDFn$2<%P7yeBjzApCs1CnR!v&=mOev;42=f5rwcX4lpujM-K7w-M{z3opLXM5?o?N7R1itE?QE}XXgN%KK*eLi@mMKd=x{43*7vjfjt#m%@(Ip5mCy{*!=J!#%5uFqTZKh3v2>2qXH4&U~q&!gh{=g~^9v+aqWcX0jlZhf}#WA2Z({wS`mKi;1cgfIJE`jhg4tdq5eGq;2PmU*61`4czy-d`o-^Ft)Zd*TNO@BOvR|27+Ty1BKml+1r{U+uQi&t)<X)#oLf@9ie{i~GXu7dLI?_T_(*``3p%WE}=K3$2v+Ey8`t>zVr=K9u~W!}vNXZdbY?*YRla4eogTew59%`=H|b{Zw)N{;RltpUv)%c0bML+I>)QZ<h)(-?aXlWxnO>VwRKhH7}Qx{vWMzf#*Tfci-XbaV+CQu0Nl3p84;)lLGj*;S%4q;WFk2k1)5R3uf@Ruky*~W%?N5nP)iO*m9t+n_G#kINnzw<y{`HdwoB2U-#_w6Wo{YNJhYXQ}H`x9@^JG4d9+zrDZ;A@peI(KPK`U3wz0VMV^)8Vn3j`n$Nb{Cq!T5(mJq-&&!+TS;hS;GFJ8lC*$S3^4?p{aiz*LH|Ngh@ibeXpU?f;e~s5mGyYc@x4RuJ=9e!rx1WmPc)MWZ$pO6XkIapb_?4W$_*z+aZ@kBOj8#8-`S{&anH!0DW&H0~e4YDSJyGIo{KVXEotOSkY$@^j{sdfKAB-v0q(5DDO8(rb37r3CS>ct+GB>ZRUd{OvGWq^&AG5fh{*)CyKL4^Om>c_FyvWCkJiM6u*Dp%=z50^>(8NeN->Q;FU-!WEb<fyenz{MqyOJlm;u@|GE-C!P92w7Dt-G?HT9moI4lDlHzUWe6iBBrX{kLz`;OlNwD<u07eVyNa=Y5XP`bzq<sBs@If7{L6ey*2X$NZHo&i~Ok=4Qi2+)v-w0}DBBfN=f3qqu(GvEqtIo-(K9e0S#>nC|9ZCi8KvOHE`xY%eH$;sEKVHMYN;=kfPAf5*Sj&oAE&cX4aSCK-p%s>$d2ip@NG9k{))8s}}dP5AZKB~S6HBl&zYCkUV1Rpx_#Ca*K*M~#^K*Chnp7Zf*IkC6Sax?h~DDgEhOMm|T=Vx>RDo|gFI2jzT6EuYNCKbxDmC-GFkeM)hw)QcC~+&{`-?(O(6V4tA4KQ&11JJ=_flkRWga&So*hwqmR=XULGGdHX}0qdLf+coBP&0PWaQ#0jf=GI?l1MbU4{>u`d`=4`sUJvU`b93W^(X#$DFDuvgqxYph!4We4n^V2guW^!J+b=2p*nY_y$z0!$DX#Cw{12K*Kec_GHTz}Z4L3=D&W=su{(8$wf3ANm^LEr^{`}exzuU-V<yU1q-&-x8-{ghNjo}dzA37`6&8-#P<^Fa080Ya%nZ{h-mn!Z%eKcTSYR>MkQ9egEd7O>Xv9r@%+`7_+kLy2_kJmR}v4+BzekuK&IBYoA*D5Xj|8pnLbHhj;#(DPTl>P^g6kZ^HT)3N0zRKJxE64RL{D+^P%!tu4ZYw+S^|dnY3E#d{?&Ce;dA@ma++}WznkxL0Mhmzf>9^%MOn+Vg*Pj=>i~P(VdmaIQ?D<7;?K#C5B-|{XL;C-98@Z39ACdT$kuq;L?csIL=(SsT-Fh-UYo<;OcXRU^b8q4iIj<}0gkQYR*ULMy&muk#d$Ei|^km8N>9VCVzo$!oE`QANp8oCmeq^_rB=Irbq@M`~_&VC#2TK0w=g)9_);W&%_l}bB$-E`=@LtuCZf?~JlI!?q$TTinmyrD7H%@cj@V==W_jl%c=FdMX$8A?&43)lbE-<%W+VUO89~!~ut8;%7$)j_#<e5pFckc$_<%UT=gBPZ`xmkXtjDO4}jKdP<)?4LdJ~wE_`#NvT9Em@Y#N%dX+A<E2(}V}r<vd<1Zf*ci>m~Uc7UJ<Y7Q7|>(VzRi8N>Xs=RR<Ko$;7)lBeTu+#lb*TC(p_JT$MI@B9UPe=#OS%X#VR9=N{lS=TyB|4WYN{QmD|@%Srloth}eE%Mj$03QFI%&YeG0^*H_yCu)KSlK^BHj(^SGk9M44xU=^B<@*sjnB)Q`S&{JFLsvevfJB>`<Zo@xt;GW&nsi)rFrR3;CB2S-e(&25$48ntS6a`68ZYvnX^v%zen<K+Q{5<c%;OC|ANH#eSa+TiQCrlxM}+n#m#Y@1NJBWj0EPsshb1d8~BrkGPmyk81Vi<arJ&ly?^kPh?V0GND6q5VUAzQ>%F!1YQTFK#m(8hF1Wd8N1EIpwEdgE!%WGezc&Nd_lI_sB)MN{`&GsD{i-+T5IJt6mU7?0do%yDQ4*gNCi?{S{PO%A-d|g-Ys&b~ZN~Qt?~qL4`*+Lrx;B@um%Z&ab7PF`!;PLrdEaGZ-C%Bh)JEb9b?DC5tISW#?Y}~Vr<CV?pxNZC<jHec?jzlLjtbzfgv$Dsd|B4Fsi!5+A9H1WeyO#rx5rP(aWh-XI(&UF$186A`;fW+Vn_bG7{yLV{Fdo*-1z(nZf>O}@_CtG^<3rV_K_KqzgWMdaCiKG<HBPH4-SZ5{(!ls_^?@gyaoq^->)v~Muj7B9N!^bc;~D9d9))N`<}#&W6kGD-o0|%%>y`(XJ5WlH#eGWkae<h9FLE;+ir=kb4m6alZU>|{;!`3A39Ff+i4LC0yx$m<B+++&5b=9WPkY0nRx+x+dj#2?_fZ@-Sn!gV`q-d4d9gu$~Yw5UmlPryoQ|Dp{%rk{&eUs*XxfrdA;?1u~70H4(0JN56k^a=SC^HPnkuNCBOE3s`z8?uUhnwdD8L$-|q~SU*qaNX!SkH^F@E3uedjDYry+_v%y+<ew~`a+|#O+JRh!oQ?9?Z9vWl%GuPKoW2#5uwe{Bb)ero9|JZu|W;1#2*S_yi+}Iu#@O_8B%v8Rf=7Adl_Ys|&xR2QR66N}9_jfaN2y=T{Ex9hZkLX<8N6eGql1IDWDX!n|{ILzCKid6Nas7U3yjoxKX!|0gQbFmDcHhtD`hCB(pYxd~_R0BH_>RZlTjU4f+P)>5Yx@@e@GpdG`ycPZ<;?Z{mE!vT%0DhdK2OtA0>AeG_u%_M8{D)D%Xnz}Qh)QSe14DZKf(3=r_o`bjEDA~Q*r%$qnVK+&*l2Q-7`}1uN^AmdFzY5JRWtMNq%j=ZAH|U{LkH%d8qc!qbdvU)R?&+`(gjAENQ3h|FgNa|Mz@zRk-&2WrdxS{igQ*R&o8ktJU>;=8ruWoZZdbgK<;eZz}Fx@UdL4JHn0RkL0*-w2}Q7)+L>rIA5JxSg*XHTV>v9@0k_X-zR(9t&@Ig@1L#nOJ#ht=ObUEc*&zbKi+sl`lCIcW^?WN)C!A|{MvJze?)B==Ry@^{+!qm%kyMzW#QU$u{|}1^v6F_uH&3}{NBvW`)~;#S9_lIFY3fxe?Q<k*MzzLoNga4E_t-~2A+f?e4Wj@t7ZPH?|(m#&$sz%E}1|0zSx&OYO##NNjYxZf-Zbsd++hM>hD`j&spa7jR_KO?5WNE&&%aHwCWb{J+&`?tUSMty&mxWzAvH|bL+S70)Gz>dz0UL>F=Gq@113?zX$V<H-+o(i$bo*dq?d(UN+a>*LfB+lIL~pJ)z?IdqSf{Rp$EpM!VS-xo>FiEwj1y-qI-ET0T$O?<EwsVs^@P1ozd+C-EWj{@M6N_Q{HysjILLtSZmNy*Kgw#9T96=J~~%yzlk?G?BUfUf1-sWbS+aLcs4s6!)L(67c&F^O@3;Uwhx{Z=Xl<YwwwT{SNYd*x#lZ=TW~KF<0)D`*WXVfxk1!yOO#7UftIwMdG#h;oe;9_`dhp`}rPkFn{cQezPLNweJNiy9<B6r2h^ln`^(f@op}|T>t*UU+{tKE4A-C6t|x(E9?J*2eM!NES|akJ&W(;AmKfi1pNL-acg>V!0&v_7M+CSxljG>D4T1)JMuNjn!~>KdneDQ-!Rv|-|@A-BhLYY@w~P+c5t|xYu_sw-+j$o|6a+Q?v-`7P1V5PQz;&KTb^^lef{ss^Uc;wT=ySZaedD}W^(=PEdjspQrvquBjER4#<+W&Pyb%eb0>%VZYyn3!0*S*<;!?J>falBKfKBJN&WjrqiSP*pY1!^IPiCC;GP-P1An)6ZS@r9Z}$)UT@bkW!K8rS#d+(MlkeHqev#qMZ^ci?^Hz?F+3`^UzcS2KEzio09>X9DHbRY<KCYh_5~M#>KKUnxgX;XReqva!LB0R)PYg#meHiK31e6n@C&HiM@>5_F!6(B{g`VJwnM-4XG6nIe&`V$`h*^U2bCk;+I|e-izN-5M=0nU}#HjXE7aSzzG3Znr<8$<JGWs$dzS30ggpvLfmWsBM5VsS00{mph;=vZep9D6-#i`r^Ho@gjLQV^9DfR>Sr1!!ny#~J0RPKW<M80ISrQ;_$mH?dq|4q~n2OkbjdcR|Zf@JKDLFa={WiWi=ZK2zO2SZ1q9O+mBO7fFX_JUS%3CP#WRZqSb+Kc#tjun7k2)-9ayeBl3<I#rv2{5mVlb?!mJT$dy1HUJ7wn3Q}nk*49q~qaJ{nKDnHivGGm^O$xYDj$n=)5=&T1$x8hVTMlwo4bpd5^?7Oofr24NJngOohK3Wh%6~9#lUGzS2}qgOOeco9b#i3H3Bj(lI}1?!1M0MScGc=SX@j{AJL@7C5#N{z~}M9GeecX)0&JNWTqD<s8Qr!zaB0ZOGr`*iz`l@MnUpaK%vF7qG?1lRrrO!a<^+f=}hQuJ~Pu*#)24ev7<cK%a+CZO?<%baWo%Z5AZ{Q()(fN1VzYu&2<M(eS504}(7pZB#tPQr`x^FN`)l!2031)NU|*(xXsLh8_%m7~-3uZWxZ=&apm-i-kWJtfh-nIRa%%98dXloQ96QfVy_@TOv<8XtJv4M@z(4MXr|MIlwDBmJ?br@^hn({Q4*xLRW>K8+HTNkM!?`_<2xw9@jB9u3J^;nmEqy#-n3V?kXr7;(SQAaI81V`rs<=RakvjOgrct$Xf-+$qDv{A->X7-ZsQY=Yr)x+cSu#*fS_8wl|Iyi{r)OT8+T9qU%2q{$v=<1)5*e;m<_OWU!ggQ=q9_;;JLP0-t^Q4AZ@i?s3mL+;XhHW5XSLCP?nXbe|a$B<m5aMejN`AF;H~tqhX&%7@%kN9*-0)GxrXscsO?lg>x2M>`xliE*JZ`4D^s*w>DIhWYUcKI6rm_9Y#wgOdDfhG;5FyXr{4jIuFw9r$EdocN1qLv6`#jJmQg(ig$WFN%^F>2TyO3L}0FM*2&XN1&<9fc_HtN5_sk_7nUg@H4<l1&Jmr<LJ;JX+wS}>L{iRjC3RDMu?~K4afRA)*ZSLVjDm=KwTpk#Wr!ZZ-RD>QP&qb9PM6)Uk934ZO2}RZUDbKSRGeix}z=Czk>SLp((B|w5qQMUJrACbTPzHObPg;e>FrC`wuj+3x@clufadz*e}r6;9qdXoWQj?0d^d7@)y(-D}ix64*w_EueeSn(63Uk+8CQF$afKQ@tVs&j(O49iEHgxEtKTH1WjctS6wR@@fzUdzvx&9eA2g^ydJRYhWMmCh#`Fnoa#?Q6T1nY^l$J<Kku~p9)7tX@s*~s2<p!w<|g!M)ZIkB8t8u!l;xmLBmNf3AE2qMfOEP9?SWOm`B2#fx(mjz7V<xjV|0Rk3H6<zL+IQbtBjKT^3YV)bJf*@z3f<X=o;`_!EcWEdSH~J3j8XFSM8{-40w648epZ6m;6RB(luc<5JRzrps9QYx)gLU;>mvrWeMmK@Pm=RCU|4`FS+7Mf|K76<%`fS!Y}Fat3x+%tQpFN;7y^4o5<S`+=Ole-4wbh;#-3g>ja;4XZT7}84V-d4%P;FqTzQy*$g_yv2M@<;CBFvhVFp)NW_re7iA>$yQou|%H61sf={*qoOFNqQP7H!KOTBKVtP2{g&zffJZv*!NUwrVv7^97fvfs;j{WV}Xy{dl84XQ#&#^lwS0R2gH1VE}jX|3?;E#q8e-C^#`r?Hig=3CJ%sP~RqYMfXO(psF!Pi4m?y+EF!Bsu^tD#pTew<@T@W;Ym4fa0tYUsPrf1&MP@bAJXW+OQHO@pK~oU&t(ly?zBWmu5Jgn@TNT%2QR(3Rl71wRdWD#2InJ0hm3i<7??_7>W%fWHoUh%06__-gnRAA?+r5gP+d<4<ES#C1J}fW<%$M4i%9E<(8idJ!}o*F+q#x8W;I<s6i&pjW}CwjB^hd?<XSsZ2(>6nZKAHLhH1P&d}G*HDt5;%Y;>8hnbWh+`y!SA?zzKhqGahWG=9e7=eOY>1x;Rx#)ir}AHv<%2|*M?K{!k9@@2qa>enG<+(vkcY}k(3fxw(*HQ-2g`zg3G5Iwl?R~@qR*FL2at>S$M6q96Wb1b2znlTvaN_GJqte7r-7w`tNMY4tiQ3)vk(&tO*X}l^>qsT804Mh;xW*4f9Q<%gW$))h)09RqF)1{qv6Nm_=C}Q5cD9_cXg}_*bw-G!8*A(m9t@_-+>KAp4srXp_~W34P$x;dLI14@QHur*hlaW!`}ur8~QT%Vd%qXdlj76L-?d0p!^5=q06Vz54(&!5zah(E=b~{g2Y#v%C4yY6S>I##PPZ!hK@5gNc?$0qG!M-dw}D2gHL)MbT`CC!GF`SabU~fD^2BE)JMRd0Ud?9892ULD~YX#uk>2<lj_spuSL6gV9UVPq0JiDdc=%F-y#tICfdY7r$JYOPgWiAm7rDo>KNbZs3ZLjjz`CO2W2$MZqRE`mjZhSyc@<i8o4Ov9z(8U1Q^*K%%Q9BzXDt2(*595j*Va&!ATEu>~;7X;rD|LMO&(G<ziHJMA-_O_TufKTfy%L>+V<_O7gp+Y!5vYejFIJZ42ENF~nYl-xk`0rhTc}pSA_>3f%?P7BP*`R^@Ai`0i*EhjShZJr#Z&jADj>lRq2f5a>myBi+lf78t)I_^)G(lc1@-HZ+x$p<jn?1zrw*3ut0Rp{qGo7+SIV;Pv6FcEypWIQ+uUA>bkKi9ZdWbWZrBbHi7f%6uq`LKnsH^T9}0GI)E%ZHVQ8uQZhvP*#Gjh_VTEUif6MfRhe~pBK3*AV)ZKE*y*M3&PI}mIpc%bxKoN6=g-}s?c=YvWO#A2for&MxcBR`Zf5fZ5{Ah@FQGtUU2fGQ1&n$J%2<XCJb$BLDxb|F>qo<;FGS4G7|bZmmh|<&!G+Z1sr<{{<H9lfE9%HpsonodZ3FSrWo2ii#mEPEe-twd=FRw7x$o#9^|cy*cYHnqK(Q|($(J_ICcSOV)>y9KnKGo%Vj*87vu+_G@yf_70U^p6Mis`pC9>yp@}s>AF0pk`CRF`82e&4K3y}q{xnCtV4>jj8ER?BoUQ~v97enkbZ<kR346mQ{tC3>#Kxkeb&1xa7SMfQ<BUhoZG8~a5^;T8xyFK5L)|N=YXT$v2J{;^FB-Sp7(;rO@-)~p@RiPqu?#^>A>+}y)&hN^^_1>iQLTe=gy#I8{*}_BKY9mm1pH$qy=CCfBit=xoLt#ImWXPdo7N6zQsm$-%p>Va8vg~~tUsm'

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
