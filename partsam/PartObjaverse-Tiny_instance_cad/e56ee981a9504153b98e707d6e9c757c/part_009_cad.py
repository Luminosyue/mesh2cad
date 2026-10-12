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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_009.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_009.stl', 'source_sha256': '10333a6a56c3a2c4983425ba40981f4f893df6663b335ed49280929fc495e5ae', 'input_faces': 880, 'input_vertices': 645, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26545268297195435, -0.26993390917778015, -0.27297988533973694], [0.5, -0.023394376039505005, -0.10682296007871628]]}
GEOMETRY_BASE85 = 'c$}qu37Aji`~Ev5LP!%zII^$V*Klmv8A7stCI(|S7?kB?k4j@pmV6Q-WH;8FSuhJ@$S(OL5+#vJD*fK)JokIP=RM8;d;PE9Z?5aP?)%*Dd*0=F-tC<8Q4#I3KNc?ducX-aako(qUJ`;VuLu{hQ88nq`$vtbI%3qsFj2tK=}+Opj@>#$ycQ;6#hc{@M2+bmQ?7wg?xlhC%2hVX4ICLWHYRdJzmYKmqDX%^a@d$CsgD^PIVwtCm#<T+c4ebxh04Zc<A3>=TQ<S0@^|JTiGk@e4-*FO^gcmoRsX}$Ljy-2b*`a{j#nJrUJy9qV7}iov(l|Y$B#Mq%0)*HE?=3XmEZ3Kmml$Js<(VAkiqR)GbPzuzS2$TL6jfrpN{sMDc<}_H=(QcgjO!$^!4i#9aQ<D+t5|{MsSg%8>Nmo{W9l{Jn7X1^gzm2=?;Dp$K_2al;&-Z(rxIfJxVuMA5QT4C%EoCE@x3+r+mY>k(rflfAqsKZudJ}{__u$z3o(b5W0nSiukFlcdV4|^}n%a3ioU7l4Nha*8VrS{8eRB{+q7aV;!8x<y3ty#oHdGhpMoy{3b5;V?X4nm*mZ_bOX9-zxjO^uD62C<IS4D<==|nenA&sr8)VHdu>pD?!(^vN;hIII&nAAFY|sY)XVt|loR~D1=kyYHC2m?Pj~$g_7eMH;Vs)c-jp6%z`7c5!E6n=-qx+tynax+fUf*z=cvc!wH=${?N{jWx~#X4Nzwd}yB62G<W#zMd@9|BuEuAuXlbr@P9EDkK8=zkSijaQ$y=}aLUAtVTh?8_RWHDP{cg51&I77n&;@iA-%zb5*{`E7^E^@O&-@3xPQ3A4npSVzZ#-`%6-o2<*9?B|=w^!=3EudM?dKgmbYo7sH;ziTp{qEW7k08f<@<DRT$CP!?#AW&bzJ`XLp-n1PVvJUZvVQ31h0SWLX%nFx%3O~I8nL@-B#;r<!JWD>0!scarEl}<TraX<@O}6PuKhg-7<eT<c*8cP3S@N%j(^T%Q><xUGwvZDx81Dy#r2rRJ_*ync-Z2_sSu!|LrYz9bJ48o#BnIz3+x|Z8UoFxHm3J7tn)h-8*%X^LJ=!Ykod+g7ZUHezxxJa`fQEfycdZRJx^f)!(T0+`d}R9QXRo9@LigI!`-#=n|JNhP~|Q=GXE2y>V2!fUe?b&Z^4oX?`KY8%L#E(A_x3mFE0Co;#?;3wi*0&>e@T*<aU|9nky_Jutt@K5x9tzY;nB!s7?M{<I$1JkI8xadZ>@6xk25zwAL7+C1{<Dqf;y9GBD5KB3L)Hj`N&9G~Hhi_(KiSN+;t@;Hz4ZW-RVh^-}9Kl@6CH!jv+7kE93Yqr-L7o`WFtGI~lrx|l?*yr`L((RnAD?f{(UvU24a`C#Q;_lN`97R8i&m$!!?bpU_<P?r`QER`~&sNkMd>$Fsa-TPjVn$zX|D^X$X#R(8LU;YYtSy&QI25nV(=*|`u5_QjM;j043UWJNJk8~+@dn+7uHs_e`HR=VStByN@ioh*@;(sXG)q13*?<$?I9e5ta=$mde!?3^^V4pO^)~L&#y@lcUB$&b)P(nwgckAMxGOyf-JOqDOYnWeXKHa&x&hstk9VHtcGh09*BdXT8x0oh^~TpM@SC$gg=Y2N<Bg-zgV4n)#H;#w-p>v+;<&2#`g9dvbK(--7xNX`t;Ki#G(JzP=$Yw_qhD8X6l+KD`PDqBm17-i%k^F<#(q%iVFsT|jBko&YVkVLjP?ANw7A=kp6C8H->B)<s9nzaDHtjr?~Sk01JK=hw{~VKx4YaPum4^BWQjdq|63d0;&S?A?DCEWr5n)Q@o+4XpHFgqqmKul?v960CoU&%SiBZr=%GBUyYbCljn9j{7wPf!>F)d;a>_Z+g<5XV;|Se`uHqP&nC$4mVdr*w;~0qhoXeRPt;JF4;=Msy9PP!QaXE1x?edlryfBQ<_lHWI^u{rGw>y{f`_Ec@1Kt00o+r)wRd##ht8@Wf#Wyte%26I)_2Rwpb@g-A;=S<=ZrtqXMz0$?z429gs3+@gd{Y*3{=duY*5U;{^cU+YUZKo+jvhEx_@s9{DBXmv#zWvXKR<^`rD*Z>>ngrhj{=S!3_q*ISLqgXcb*OrTuz^bS{#)w`Yq7s<NUArxv_j@Z9EvuPV@6p%Re>UzB|LwLrY)Q;%h#b!sTQ>t;fAXbuMS*7rVUiRk}Tbb$9-Dsp9BCtTXQXReGD$-QM^b`;R-%V<LW`7GI^?yBF&5J($k#HM*YNrNtL|0J@5A;OYi0XHNw!zDf^5cjF7)eCmQ8U!U&Aw_RIqf7caSyp(QqU#7*&=+c7QllzJ`9{jqy|E_(&??<}-pvQ6JJx3RH3{AIke9X`JXYy-tv<iH{?-5os*Y%p?`8`6hyIQ=IZoF_?i<f9Q$k79>u4>~!=>~K)9s=95bG^Br)8?bn1#}g!;ISY0eZk;M`h15jpu5jaXTIh9<qm7{Qn~@%U2pFn<@Z)6!nN_>*VTBiD=y*Z;Zf7{{SkUF#?s^4YLcS|DkSOgg>FJu@eOS>xcq~$+BzIc%FX(UjrzRKo$kEX5ZP{M>#&hGmEU(nuF%$1Bi~U+4-8qPt*chqZJa;7h&CSV+MjU#X^XY>T<HdMH@+)cCUSW<_4q<Jp{w{>2g`B!{om8$1>J<M;$@tC#?kHZyS4pY=@xW%efaGceh$a^#NFSa3w3T$`5)Zn_Xs;%XmJcayu<pAmijteC6V<JGxYu1r@QeD_Tcu+dsjbqrQ!XBI-jU@_+({Ax5Lx5^N-R)#ger1PvAi=E(hz3yD#Va)p<^~%V%omE~Q)0-8h!L!uelF)yfGDTgCc@=GysI=@xW%y?ysB&YxUcUq5}id%pd=Kfgz-eoB8X*c!<?o=4pC%)xGsF0Pl>&i_icua(x$|HjvKIe+YAZ9FJFG;Xps9;^o?xL@Z>>H9VG0Ce|#!mZxUdl1VUw@-`LogR*Ev>d(98!uPiUsHQ7vjcaX_d$kbY0q)?`-k~GQD#N`ybWDFkGS&`dZ<30Q`GZyp6-qw40hMcsZ-U_#mB|8=TN2FLDp4#%~22eeZhh^wC7X5?#6fWPmXRhxvV|Ei)ptUT{OC)Kkw%l<LIG;LfUh^(u2_5=la^MxSZ71Jb%=DgdR$1tv%0L%^Gt4$NoCu9S?rpeXb8}bl$TVw-+4n#@A{Q;ams$y{5l!*>K-^&JU!d@At+<=>~N7{oCndoG;(Ly;?aJQXJj7SWkPeV%8qV`JWxCz5h|V0o{EbX*`_s&)%-T*J>8c`KRyJ-h+uDEm3bL{r!(mclXl~O}U(zv-I~r#a8pUHwx(Qf1q1RSAM9vfb$oeqrGQSdH}k+&JXJA=%GFd`g=C$Hgq?R!+LVPmBSBt<7kiV!sEVrfkWPTYSsRPpZ|UDKdm0qd0t%`_JudTN)JGH-&e$Sa&(ccC$~eLhnKbD@%>M)V_yGTJ6~kI%hlsr+z*%FdP^AEdsn3gpsTpsS8{UxVuQ5yn|FVA)*b7$Uyf<>*QdMhWBV@R{U&#5?Y*v;HHz1-nZIf8W9_-aSl{&NF>l<J9#pzom!KPS?rZORt?!C(Id=ov`*WpR(A{%j!MnU}-iy%RpF<Bqch~u-wT^DAyQF_#7_pL{=hs};zDL;ayv6x5cG}*!D_uZ$zh`|K&HFCix4Y~4rTUydDqQ=1;nzcI{d`!A+n;Nw_FY5i7IgQ!VV->P+PG5n7Rko#&zzCyjh9vOA)oV3O-uCp-yXD&_1#mo_L~zw<8#cwXY}tT(1Xz3?||E5`TQ5%G}Y^8d*290H=w)YKeH#7pB$&PUlc6C<?K$=zPtH#_1(=X@idn&DkXdSYnIRB=vKB0$=-U++W+wRa_@HSJDSpM=;}L~t3TE)(K{ZL9)#|GpN%}{=*HrG+ILB%3+N$tT}|h5n(})K*Ke^&T<^t1?R%wPcgKU$QI5OL$8F?#OI_B!hbrC7T&{h;wm<xYb>w&Bb!sHq8I|fC4@$S7tMOo78pO|yXSbwj<FoZ++@2Eo_3z!#?c({h@7;FiznteHV{@$bU0dk_y7H&h^FBXEB|ffy@Am2L_rd-@I=cC2wB`q~^Z@JCJ~`@br_v4R?svmATe&@Z8f)MEl^%*`-EHUQ^^P9=?40Hwr5hQuwBI=>T|igkUmRM>{i<;8u+~oKLFn%IOnINnUvodzJN}g}pu6M$>I5$5n?Bm_K+J+2*gvT^Q?&WJ<jf97zg$!MU5fbhu%nC2r?lUtSQ`@@J(${C|J?|53%Wbs_w3^Q>x*l@8&SFi-EDuuX0G?ImU{bd&*XM)`$ucPm2-rn8~a|;ekbGCUH?yf+|fhVE9t+(ne}kHGd@xa>-}99lhTB+#{I2MdhKqhUR`Xz|ABK2-JU+((d~|=lV4oFo8r|)<1d#v?SgJKKgs#?HR1BpMXFa9caJ;yEv45zrIjDLs_UwJ@h$7d>F>1s#>#{vUR~ukq1)Sj*ZON!4rsdSZxDJQ?hh@0Fm8CNS6BIM=;r#GshWS5XCCqDu798hpQ@GW^-t)`2~Ai25ocKsecOTc_cv^I%9(`s%SxZ}^JiJ=hyGZdm2Oq3AN1<xiYcky{u&!%k9c*}UlY1rXEo=a&+V~~?l`RJles-gH*0Ov+8?OD?x?1t{r}R@e!s5Tuk^r<J*<Dh`GXDX9QNu0`IT<W&XMMAzgU~B>uA5yt?bXIdCLzKX{G6^e5KoMwwxk8^xJs;KCo%@$*lB1{Rq6@KFWHHN=Ll;{kqC8Dx^5N4Lvlm=&`JHarrFogCC@`o;@kWTfSdc<tsf1-A4I-J@gfqZ*@G*<ur-qer59SwCoBQnjUJG!r%1|p4D`>J<x+HzbZfWnxl)JyzZ&;MVITEF4}YX_O%<1Zk5@ZqUFzh+tCA4o9ceP4!uru-ER|qc63v0)ctm(;FnIlo&HY#Z@TMG=%J3Rt9bc!Rj<AJSx2`f-cHrVk55<SD?I>R#mlcNe}+;kI=Z>C#9^<0thJR`?^^P(*PnrP)g9d!o0_Wmb6O4V?<(GRR6CU(`iOPaFEPCyx4*(6tzTBlIb43FCzJo1uKKHV0bTjiue<)-8OP;J;P2k9KYhCEPv`==>rbDq{Aspc#(t~ODB0^Dr5n(dKSRS;vA(*!)=pRdp{?cz<Ez!|&r$2sH2+^-&${?f>sQb!cG{U=PmfOeZ@RnwKo3G!{`BjvKkt-vbSr9Ok~Z&@{`rO^Z#(UE<sDt@7@n^A->19&hi-3Y-SxjuSN;!7tHAAi=YZBuS3k2)^Ml!-x}zIKYNu=Qf-WL!a`{-VLdR-y{=22L_FL;~IeMu63wnDdb!R;<uN&sdYsbC1eeWl%SDiDwdZ6rDo=0srCU|u-?@c~8o`05~r*kH;9+<85OX&u5<p-sU`mtKPTz%SDEnco(t${Wk{QAGjpI9%;_9)$5536Kw`v>>e{SRGii`4w@>T@GB|0~@-)lu_*DAx%tfAlIXzh77FQM%Z-QX6l6-JS168lK52zDoDUSLy!vD%~I7z@R>?Z{4MjXXwTsJ2XFwhy7T8dyN)f^Gv|e#i`X=e64o}J9;p@nC2fNI-1L=J4BDWPj}-E-LwWLWmS&Sm7fh`DEp^jRXy(W$2z)ocAy?#pYDzy=w^v1Ena@z9S=2bvj1;3*49;}o6y~U_4tYNSF5hC+cocS{)sPY>%6i09{aiVJZ&8g9Q~d3J<GIp+nV|h>oName)j9`zR**gb?Sxgw%@0_=fkuo9NjpSrnSef`|}Iv%AbDSUEj9#aCF-)qV4-i4?=g(QQP}+z3n#X=a6^%ar>dW{emuH^J(W0D>|U*%AbKD106lIcsG}ib;E8si1T;Yqn%rf;S;$1qi*T@tWS5xE%YFCcV75(x4&(sa=(^e)cWPu-SG@vTsyCw-~77rn>Y~U{@$#tomcG-KIZ(lDr@K4K*crO&K--ibGvwaE%z6?drs)If%7Mq)6UgqrOz~7`7?BI6W4p;!xXRotq(VI+}~fWpTo!RV?X@TPdn$EUG_VA0J<BO?~?TVC_j*ptm$riR~}~lyKwFK$gjJ8n{dR@E$Hs~#HYLS<wh#EGk%liH^1)BZ$fwHmrqxI2;TZe>zB&!*WGz^_-dAZ^Xu+-u6FZl9*48|eb=~`60*`oqp^p)x;64J|E?t0+lg7}R^dwryt=qNfqy?zt8G$NdgxG({aQKGAJ|#tH<fPd`3?NLfPk+(0(#Kb9uvPm5Bd8G-9UdsgH~N}{8la}uLCQKBxI$Fd+}O+^K>-(XJn;BuWmp$+AcY$<<Isizn{0$^!(6`^{*b#^7nl%A*=kZ?$7^DPX2!6Ymd@RUwcH%Y3Dna<?FA~4fHoK1?8MzKbW<jO~^_Qblt1v54{cl<gc9Q)otj(N{bI_`j+n8?yhNxS?T68++SBO&3^b-e&_*TezQO>_K&YUO1FLOu@-;H-(h|IRl246TlUhGtmc<rSMy8h{_*D5)p%37e?IzkH6Pu2edAN<{_&}F|NQmqYW}+A`^K|dzHdCc`F-R0U%D^9e|>QC`_>0n_l<wQZu<J`Ur*fr`qmRy_sti-ZusKmUw{0%T7M{u6Zg<8o)<6uZfB`yKGO1=3;B0^c9G)=S?S{4&R=MHd@cUHTU49Gtn|Q?o(H|UeU;no&#!dLm)~eQ(9Wto0=nUAPhiX${{HLluhOZ%5!%0+exqOC0d@s?)hNUhB3ulN^!$@)5}jcI%=({9N7wrQ`X|%%>Q(!{{*&pXFd<G#%K&}_eoNYEY2N`afnS&QgS3Z0k&Sshi4CNc16BdADXpQjvcRg~RdHP&SR34smQPwCU@q{|*|?6vz;fW1(7xlqBj69www&1*^MmIEe+F0#ygb@a1XvQh3i?w9SOdHU+FAx!2>gJocfYhWU@G`$(l&%~`Ua#C&o1wIOxoQr#(QDRsa?h4Kf+qzdt_R?v~|F>;MCq1q&)>J2u^Xl3EvQY3BE(x=hC(UH-S?uUV;w@>wr^#tD~=kCBQQ<X3~LY!PC(9i@*!ug%Hzcflq)}mR1dMsD|-T9(n!<<9vjFf|r5MD*&GbC*P3|&jHVaSHV3m0xN(&kGhKh%Y)~U_P4w*FECp+=2Tt^$|O7rPI>MiAK`8AqsX@xxDWg?@>~Jl0pE)}p90r|Q(7kOBRm04>8p{4@MG|gas3H!4frA4n+VJV-z9Cgv?O3M_%__L6PO6T2Khb#?gIZu+M_TYcaJdU)LKGg?+EZPIF+>-^$>0Zr?u!*7_TveKZ0*Tp6$TR;NjBOPh*`RECqfMWA8rj7w{iYCan#GVOS?<jD3f3MtB4K2->^{7!OWk{a_f+140{|)~+YBu|EhO!8hBHXAAHk`1fHvcdi4!0;e^nKIUJ2%)J`uUtRREF4n}-=tCIRHo^kn`N4|;i-Z4#x*r0sgMTe8B<&~Q&){dmc+EWqJPv*g{0m?LcrC0WHGvJmb0AKS1H-}9+<P9F7d#o`APIO9yb9)VIbbF5`-nA_NtgrW=SH7%0w03Yno|+$4x!qkp2I!Q0CR#<Jw;I$VPWvPh*Lda1MsV|o^PaG1AYtsEv|nD{t8a`8#v(u55J1*t0;qbgsfwPw2r`G;2pu+0|$e*lQu|N2jEcfPSS=;>nv@Yv{$5!26hJTj69=J7M0l+<xsi(fo;J1gAV|<1#gRc2cUeauPZPXyeoJYU<`N{@Ce`t@DAupC*W{TpGKn1gk!)*gO3A_2OkF>3!DHR3m$`VsN87aQ1EE*DBvLQDDX&NfAC1~*MS4TUk4uu91K1Xd<bwD_z>_>z!Bi1z{dh(z+=!C;?1SCM4v{2j{&v<9|Jxf*c!Yw%2E7fTu%TW3v2=20&P;fnWvr2&<{cr+(e%hZ;b24@R8z;aNP(#RlJGE&rJ{q!lvL&5i`Y`<GML~L42yTx1>#m5q}dn9sEu3iNG1)6T#mAP6K}fd=k(Cp9DSy_4YzNgnhu@0-p|@^1TL}4E`GUtH3wGUj^?5oCw|xygTp>@b2I}fRn&`fcFGW0q+Uk8)$*|2JZ`;2HqDu0Gt6H0PhE!4n7@yCmxh*-!f?{fD6EvON*1X3iu)TD)1n1nTN;WIu7M1z8u%fQ8w|9q%D=U1o%GqVrlcGtpt7mz7qT+;8G8tkL&p;NAbnDUW~GdPnR}T+C1P)@OPxmk~RZqfzL$RJn&h#CO#Y2gmXOiO+nd&lfkEg&jii}pMiU(1E+#7k~SCR&P7>sa39^j5coFuY~UQ=A`gEX*KeaN#V6x>GRmKeKFmQ|=0GR@mb7=JO#{9MK0;bIX}y3igTF2<R@y7TDDZAbdl~o&cok_)q?HBM_3)0kCTt0wD35A~rELXn0smgwkJ8QnFMwZ?b`+d2(Zf@5or<!E7nD{+T5(_n@OHB9zS5ckBfxjbw2#pS!WG~Rq*aqv75F^(EAYvyz+vFoQTLO;;^6sY+EdaV3Pu4=?RrjHO<*~2s(-n(Il$TAh2(wD!?%Rh!Rx}eF9UmlPp5Z4(v|=hf;W>^Pg)0HJ8<gzD%8IUbrZjW7+e6J0pBYvUD|%&32^fH6X@R)=o|4Jf_=ROxD`AeWgP_W2Y;1(Ev*f(Dfo-BZw;iC1eO6WCDZD_hjq|T;`gNeA?@)n#ynxn`%2zh+GyZ#aO%r(^oQ^ycu8sDh-)}vOMITR`H0he#EN)!S;rm0u_pW;Jip+!mIKxVKY_Zg0<VM9y}#mq!XLpWNE;(<An<kYZ=_wu{g+V&@eR^Gg?~SVkBPq~+c{KPci;f<oYHbj`$aH55X>Vb?}|Kxt-vFJ<A4Le_sM$>NLvqF2Yy!Cd1*I+KY+JFxjliy!CT8TQ(AXm7x2b1t+KRwz;fWFrPYx30(gB~cL?KqS^(>Tzb(s}C2b{e8F&$y_L#K7z?|SE!Z@ucurPQrLI24}nGSp!e4Dh-r6mEA!Kux)(Qd+O;8a&$)Rz~rApWhq=bE$(U?%utX$z!H15O41O3-i8_`VSCA-+f2Zo%={jo1(`hc*-j76p%@*h`xTi~)aN+B>NK9n?+yH)%f$9ydQ@>?r;fuD?QCh&PjUbduH{*a!TWOiM#Q)6iGq?WMJq)&y7=yq~;hAnql64ZIb`Q9WP_@KN%fVbb~ldx59HM;X9<;H#yr!8l%nu}r*%w6fC51D^%2BCV*j`oI^#*T8q{fs4ThOY1MVUH#D};xw1<3ZBn|_rPD4)(HM+1YZ!ZN^?e<0jvXF0^_VIur+v5#JdErHh7q{=cN5E7@q{E_~u1=UgQbGIzeOgH(*}ybJA`LUQ-Fb0Y8Ruc@B6RJQHK}7%&9BNm_!mPk`~@t1*r@0TaL}HV2S?0BOW$NLwmxJn&ucSi$3X25>1j&8G!OUw|~?J*AD1))_beJOc6S2^<053o(rV_6M&nt);X|z{cPe5!dR#mf&>}>x#fe;5no{BY5v6%nzPRT0W%bLmF`!r)7~|7HP!kPlit91ZD?+TsW`VoWE>Hqd!{b@*+Ji(ufz3_L#IXz&zlkrR7F?Zln>X`B4<<MUh6lxwOjCIssn-?<lPy(i<X;IPDK6(oLihA0n-rv~j=y_*iNEklqhz#A%(2M0zCBh%b^hMetdPa31(a(&i$4F4Bn8eliQ`vyeudzNLL8_zX+913X3AcBF4d8gbe;K1cfJNF#nj+LwaQ2!vO_?@Rj{>0cv_IPJIRk$xU&#0$!R{w=XM@QE<y#iZp5<MdoeBVIt-KZ4T<b0KeYX_ch41=a#@BdsRVYa*>V_UF<_FO4+f<E8bNHWoMpe2lbcq(>udJob%FNbiI+;*+Gk8OF~vgl~Y;8D%2UCnAkFonM9`eJIk150*9|jGt);M}X70VmQ)=BW*DDnVv}RiL?&5hwg0&>;)c+wnYJlfsaMs`vN1t+rqaEfMvibW)!=pfCBtijEx_G7r;|7_6`HLfUm;XUJjfMJ`Qtd4DfaEPMDjo0Goo-oTs^84fs4bttqs&gae-hr!|Y#uIGT|z-djSwXq(s9XPGIwD$G}4hN?-oz`{>xDcH74B9(B1s(*aJ&E?FlfdiXwCB;@_XjW!IPIylw>}T74t^K++ynjr{(|5&wg#{)IMqwf9_N6k!RZV<3gc!J#uafoN726e2uOSHBeX3C+DG`fhd+yJ!b0G*-`+xB2`_`kgz=ev5^x+iolBn%<9(g*IdFO>5QFg>gS@fGlLPq(p9H7AbVGl-VGc}y-yXqdkI*mTbe0>9c{m#LlsKKe>6}s?SQVW5XrP}4Vp0e(s)9HXmIWUf#%IUzz%k%eaE}RW4Nh$sgmw(VTqWLFT8}VZcL@7~(;Uo>c}Pglg2V%;dn|A~ctdF~h4I=**ap0!v}eNjnU^ph_$0w+$7#S(;M9gLXb0gC@CwpOh4DH|SP7iUERJ#sp91e8_^jCn*dDwQ+S(S_96Z0Y@G#yZ2#bN&LLbTiOM+L1Uuy$fgO@_SO2As+*`)m?c)ub1+r!Dfe*>QYr}JAZd_p)0{28>hIItl2cQWlK!Fwg)eQ<gnr?g*zH^BQ~%(Msg11F!8kD3Bs1ivWnIVE`CCH&IEFX5W-3OGH-&>R>FoCw|s{(ceI0Q?Ji&k@0A2Er8ZA!t(suqk*C#4`fe3w#j9=&QhX;5%j7M#1L~!q3117{Bd+eZlE$T3hhBm9Pmoy~m@rrUDOve;_R=`0PaZ5jf2=YSS>_tKhY<wl)FQ0H?O?Li-4JfWIg0Ey3q7!YLj;AJ>HQzza)zO7JrsVKMNJ(biSKMc_lJt%A>xgk!;}%r^zUCnB5xo(pw63oH*#=LC9}IvCg+JS6z}`8Mzt_+aGe0Bj7NAk%EYdmZ6kaOz7o^oKAnIK4xoy|x*!9yskuv^O0Crh%`OwpsALO1KHUm9*Cczhflq3r^2r^jw_)w80zWo_4?v;D+F5fhxeF;4K87?OOv)aC-JAB>1_6u!M&jxHeD*aeBt6CHVP+u)c@4z;z3hO}wkLL4w~w5k`S`L|PYMcW}zn5BUfq!D(F3_=o{c^zip^P58El&&4(2EO45SH2<~%KL;nDcZS~ydxO)yO#5Vxu>b6r#A$!0J@si|dGH|WSP9$)PO)BtcoVJ$pDb;r;PV&Z3~(B!w69+V-UX*I{4>&jMjCON_f+>X;7V{>&uCps1}1@jC@oI#b35U?;O`^t9pF-MTktsE3rq*6F`0(+G^E+6>muqSJPSTjTD0Kje8K_Xl;>;YBRmft4IhmLP6z)GK8*ve1%Ds@{Sderoc2N5_x==&^bGbVd_D<&CyWIjiL_|oWbnbrHxf7#{3q0L6G&wfk7yT`Ej;`G>wlT^pFjErCA9y6j{i>mXQSRb>ogMo`4MSEyBsv9<sy~Maa47hQR069e+e$>'

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
