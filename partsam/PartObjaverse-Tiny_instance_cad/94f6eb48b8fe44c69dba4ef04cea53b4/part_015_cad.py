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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_015.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_015.stl', 'source_sha256': '17cd73fdd22fa2148c3147d7e9c36c2779a809b5b831e559d1e2cdb9ae70734f', 'input_faces': 729, 'input_vertices': 601, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.11795748025178909, -0.13867855072021484, -0.49999764561653137], [0.11803159862756729, 0.12856049835681915, 0.4999997615814209]]}
GEOMETRY_BASE85 = 'c$}r22XqwG8}=tb0Rcg(2m(V3MUW~@AVcrcrAS#yLTFNx&>4b=f;3U-I4B?>2$6&u%n<1%2??D977$R74k94oyYGFUS?A`zp7WjW<DBO_zdX5l=gz%%XYbDL(xFY3R|;tSucUTi=E_ND>u4G&msUWF2pK(g@PLpp?|wXTe1P_b%;}%w3qR=Eu0xLiEkc`EZeYlm0i(;+)63Nlty8X&UM_UR=&_^wecX4%=z$@WH}5xWOo+(Gg!LO4B7QDkt7^4MdW{N|^vU}F<G&oD3wlKLU*f4RH}b^?3-dmlb}8PS_u4LV?cpD3^7r9EGB+YS?53afN3&#mC)YyK_fT#<UYag{A5n_icb~CK{(ac~<MDoS+q3DYJJ(*F$L$AQjQ5-O{4&m+o7-b$ZbU3R7VIbYOuT$t>CcVh-2PFp(ob_wip<R?g)Z{>;<%l{xXz<BIA63cKb-Sh&C}hv_Hq>0_j=B|b9<V}dHn7Z?mYAOWX_%O@zu{XKL3+re0;~9xq{ED%cZGG`<xrO|6e?dcb{+O@ywh%<LT??++AG%c!5-<{lIu`pVI%NzuY_%drGO3_pr>h`+d`tJkxyn>ipMy-On2*>pXdk`7O?Mx*6MKoxfXLbm#UW?+!W6>D|t_bF=A9&Tl51cjwyD7c$oerC@!k`M=}u|F}+``M6G=`MBQjB3wTvG*<q6bH9??pAU_7*RhbBtDpZY$7f2<ICpLb<=857%)65tH)hIQzdtlhX&?8+R`-1Q^2i)9?se|Ve+-UsuXF1^`fvSb{|j-xx#kvG=iHpL@vdC!_Yvp69!YWMX8#d<zU{u9?9PqdQ8L$-U!Kb2mXF&v>c3td&o^JlqqA<1>o#OaypmUZy3t>It?{f)vVG`;cs_1c&c}q!llj2n{&Uo^!UH+qIxkArAGGkelE-ka_q%jd$%k%}xpzRmcz^l-)UV%hx~w1Z^|4?-xp(4o`MCBtdEpmb<#`^vo}%P$yxvBR>+oVnl)UNM5LxHkPjbF|d4WcuJYR=XlzdT9?*HSLmz2C!V;+ZFebbe^4d*)6n=g;X_+Y(d&OLEi)cj|4oIRPw-x+6LK13bo%(*kpzC0<598a@W-|_x(<IFu%8MjX=%3Pb;Cr-&{aPGz9G;?mZ{eG{K&*a?bwROLe*W>y9pZR)UT@RV_|5*=rBKf$-uBq$cF6W+<t|yiJ9_JRW8@_zaO0IMN(=;V7>iI+-_j%1roM-Hj`8#QIrMKI<SIH;D%G~O8bib1SX3di09v6stM;_H#=Krok<ZUMnQP<%!nVV$~el6F3+Kh8b{zb8`WStxJ(xfBT=6~=FxqWWqStSor>-h3H|54{i)Ixc@Tiw&$x!G*~d~zM@#0dXO=0?P})v|rN{d?WHH=J|5_tpJM`!_#b&5!HbDem0tk)7-K*2x2Izcpx`9Otx1j05MM4S)W?{eMsPUq^0#*nOk)jN5V^o!pzV9@jay;jFv8nW?^$TmMmCUz;Rz^H!&Hckb!1e+|$3%Veef&7N!A^X@xt)i*iEc<SMIc>Mbg`&k|z>%qy5QV+NAytGSq=UPe5y`ka9-MLps-g(d=B`?9baj|NY`?wzDc0{RN?%Y7`$<$9Lx7(fBtMnha)%(SMckV5YI+$N4H<4TWpC|jv?W13&DE&mPAHT2UhSMI8cPF=s;d~#gO;hs5CwP1^?p;!jJ9IPmGqi~^o`#cmS)`1o9k+(_1Mi*)_LFNz`zrmka!=*{#APHa_3KRFyx-NM{&H{k*uzR*tv8R`p#$o1qiXSSdmlaGZm+*nn)`Wf-C1{TRpeavtxwG3wN;ztar+fJrmUaekayps^v6>&+h(5k+w!<t_)YH5q6>08>j?$q{5rXb+(;Uis^qyB%G?`v<G8zyfn4txeNd@iwusC<Lpmn9a}&AM;d7<Er_LwQG7l-H)<>>)nRrO4-*>9ajeX11{v&tRp_A)XT5}$9_n5nmhTPj_J?dZQ{!Hn*P1f6?CA)JCx!(H1es^x(Oo^5Kxz#e=om)3JcOJjKyxw7%TT`zlx^sQoidcR;zLTUJ_rgT3-!}4qJJ)**m$`RDtlEA`8?Mu)n$lhy@hC=m+Q=xSKQ|A_+_}E_+V9xH?N8iEb+<P@GG*?W)-_4VKODeylFuvc?bBUkt`Cb(RK^*(-R_*yPdgPkt{cAd?b@8{pZnpg(od@d_vgWnY07yWFB0Q^967mnWuVNx!y72$W+K<xtw4XS@OizRZ?E)Slak%JUVidUS!d#{<H4@nF2}i<y7;6!HyXaOll!?f&7E6cKieVO?`)~mH;`K`TJ3k|p1L<=?#*~|$z4ZVkk0K#K2CDCH|KM%xB6bGV+7yZ#_MHbqPvc_A?Kcy4od&E>7!+CeLPC3Z$)u#v?(XY%{%rYk3-OM-XEX){;WGUkUR6@<W}@~x$pDrnx5>=b>!Y=sr!^V=TGtLx!>;be%xt)Cs^kC&T2{>qexSJ{WD>~ad&(BEzb3m`%b!ZYh=ARfBiJJo!iapVXRW$jz!-5zS2*#*8!PpSCW-}8tbAs-&tDLvB#e0ajs*_^=3EEx!;|826f)+ew;eFfn2*)Ki!?{p~$aP<^45sZwTk!sr}>Jxq)0ex$C6A+<83u`ib0nkdWri&B(@F=jF>wO1?PDUiUcr>JPnT%N*n8<kps1GPf_Q{nvZlk?Ti`<m;-hKY7c`+?X)txN_V#IQN`P#c@w_{e%pg+mA>46dq^oV?N&<MdiF$!?x}A_qem>#LC>hb1hT8N#<tb+_?YuoL|3$E!`#CA1))W&*t+td3-`^$=rIFbF1{{1$qB7{V`t`9@m!li>xO)-!F>d;~DkhELlIp=Ig+e729P$_f}r#&aKF&vHtqw%MX{0<NT?b*PORgIWOdy&({+k!ug)N=x1TsPfx#Uy#G5;VLSb7Jjo$*t>0T){MGk*3i3W_!@eKoJZB{E_-strAlq#(y3w7Ri$}}-x*gd8^|Q(P#^V0Gj~_irX>Wg%gWKQ9qMq+J&sO{G&-6|a^6y(*;OE(lM?5cPr*Qdm$!yy>f6V#tP9tUex{H<EPAM~j*I8E7dC13oQ0c)h^mG2@G5&J1Z+4~szI<&M&NnNM=dwSt%KnzjyMxc`FYZs_wBd3dI^<N2>nYJ|M6jQJTBUv(8|>%2%%Gpb<#9%xR>r}2Jz|aY<N->5^rCOd`*GfFyX83B8Fw!E%e9x!lsxmiTSaTg+$_;RSwD8U0rLK%?cJu-&z$?}SDhZ~uf17yq0G%b>y-9RZhSUx7oYFnO78h=qB71#oo{9TGC%I@I`J~M7NjfnwYo=TuBVMs>(sp~bFJ5R%HzlmUba&nfA?9Xj+1+<gei6G#(nud_%u_wZg`re^7XPxCEm|x+~;-P^eVqkFy&PxH<~@?ee2)nc%O{dWlo;?`eQcBBi{$IYA#X74Y}Q8fYMJ-v;4dLo>#M?oNp>7`(tKY<n_>Tjm*9C`}6b8UybGSpm`ygk2|bAKfg3Tcu_vy!cyh?Pv)bN{CpJfi@g3jxjplDdHuH@4CMP%z0Yv_F-`dSvF8VulstVBKTqw*&-aTm<=$H5Pq=gY`bd6$$ul9@oomI1@$*{ybh$6GJ6({u(PAne*Li+-@>9)}I!<n;o{D$3*IQoV<CeM3{kbzc$(<XA&Tzi@IKThpv>$Ma&+GBxWA0pwuI{&vy|jxwuAQ88(%s%dZr1<xlsh+(TSJbYcIO`C`q61;-MQh^f2Y=YcdjG%d~x%F(of{t?Um{7+`9z*Y1jFZa=yRS=6pkvG7e@)A+G=I8)Y1fs$cUy^T?Q!YCl`X`5S-T`wm}cGL5rUsGQ7=zxFD1Oyqk1*i-&;V}86kZpgj&#;D_l+|#kVGH#mFJ~~YqH*Y~4x8Qtb+-&6D@TSVRc`F{{{p#&8iAsMKC&*mC9jcs{R_rWa2eRK&#?z`|%UmCFLm3}$!lyDfH_le;-<l(zm#x8zPWsEuQ?t}@EBU$1jb*iz{_FFna^5>d8BaYUT;_V`Mr!{{H{a=R+{}#XJN=EDRiG2^%YLb#j@$j`^7+(?xuDdsk!P-BRDM_HTGt#&O8XNfcz>7cMXE9m!G&aQbcs~X%d#Kw>#{46%6MwaFZ1iT2CbCy^)BPwUfVz!PjBbl{CcqFbM?Bh=5P!@-jkJn>g7WC_4|M+N<X!AO*o(4O=)i=Cd+-VX75tkn|2!CM;bFDS;<#6;pc_1yHk|<a|+AczSvu7Z~SvqK7VN;uc+hMY_rVGmS3y&Z(5vN)lMjRw?)zZ=F2nhOTK?K<9(&Qf!xkpTIr{E)dX%|{DR+H54f)6c1(ZnPoaxSZXvgt{;rIh(W49Jc~g~nG<GcE`;%MVIpHri|EQ++=SE(6|Il;f*JOXWUF(@T&eb0OB=d0}sq^ys6`6Z_ms0z=Z@0{~JpU-UHSueid;ch-_TRIK_ruv|@cR@EuJXKKoHbletm-#-9mY11>(;qG`||90V*KSc`fp8Jmgufy*1gB?kL2clI=Q#dQqDIf%5kuf8=2ZWxs|ECx7;nR|Kuy)cby(^QOWZ@iFWtX$*t<#Pj7|0337ak-R1N8?v~7rf`87I=P~L5ug^Ds<@=@0=IwLmR_JnGpY3}bbmw+#IOkpO9&+bqjX^T^bYFH@$$MiR_6s=X&W-5qyq*WHQF5(EGj2b)bfS_^H#i?MT*>Vy&dr`xjwtmjR_1x{+x4i@pDyM3xI4=xyK_Ar_y4;LR?bWFhVtVgB-?SNPWu49Ki}h;a=zY1DRTWAeFrPY_10O;_uGd(QTlII>BEnskk^&^T2L8o-=~>UM|bYqx1D}KsekApug`9Sl>TUg*7Cf!+br9A@;&77`Ry;>-~QP}&9zjSn}46)=P&m}?@I8ScU@~M`O6gEmsWf2Xs|oSepRm@bi&<U!+zE3fBLLD_oN`-lQ%`FkKEI=v{FYmj`995U}~~Ex2m0$`!wstN#(pu<YuPxa&jX_f^uGV70$KDyGPvT<;nXG-#0q9FiGi8-Ou^HQQ@-}l{$5r^L@cg<FB>5#rv*ola>B^+K2FdZ%`rSd_9$U-=$w#pd42lUqR;HMn(3!bMH9L?Z+>b^R<y%>#r&2>z$Rz`>q)+m3j0I9>@2kKANTU-}`b0?~6u!sE&XBKD;k7KUDf@PwT?_v|Ue>_V%koc)xV&wvro-dhmWJ;(4MnU*q%geTg@Us>gkLm*21XBi}(~+<yL)_bojVmGLp0{Pmb$mGSI0j-M~e7u>7ld5-b>DPL;G+~cDK^x^v<#rvxL40@N}-}z~U(ogN-Mt=VSuUmcVXT}(QKI#&xj$6f2+`i{4hm`&=`;zYyw!r6AeB*G2-(P#0OBn}k74Mg<tn-g4^}F-yYpcRXYX38MzhusS{jgGJSOPyE?VPvIUv7t<R@d8~*hiJ`sm{v<ett17-&W7d<mVSN_fqA!#&$fv%zb%O8Mm@MI6t~ZIWH}sIbZ+xmsHM6tJ8?{r^A%oZe4+&*B+Kt*XO+=oWE9InJ@e1BECLPd!p3wPUh>p6_ZPu7yU>hzW%>eOR1yfEz9}LX3BXPJ+sSP9~GrM?(|yNUwsv(jE|oGTh1S6y8d?y=I4vv;py&mYc$d~$#!qQr>?{IyUG2PC;OI*$~wQ0DDS`OhZZaIWwnmtd}$%&e7zq;tf!x~5}S`G{mBy`?~i%2Hc*c1xp`ZDenT5MElugqreX4at?zR<PW>VSWUl{XD7m@1*Gk#`0X{eA95+*aJKGaJuL|q<are=g6Yktu55|FxO0Gqf;dP!kIK`cNyU*qQ0Ip-c{J<wNH-9*-w72qNKfG`DK6h@`IKiK9NpF2tIqu=awX*$|hDv?ya{E=X{}p~bqU5zp%W*K*43hT&GUwi!3)Fn==@qj5#)}vH<yMWHX-YnF%L@0r`10PI>mTk`+h>X7IvK&dk40`|I$!TU&v-pdijlc~Wpb)JH*f#L$G!9m?~|SUZUom4AC|7<^Lxq9Us=~%UQ+73%=3+VJvg~mX_)*xv=(_K*<D9lT7o|(js3j#0(qu7zPzGZ$Cocw>*x<M@c4?5p9k|8LHs!oCl7o@=JqGMPs-o_M|<N&;4d=2x=X%KrvJtB;>*WQ;Lp*mKFRNoIQcgg=e>%l?H6;d7qilod@1M7eEITa$agF|qvXpuw`NyAt>h~>_e|+~Qps0xu8qE#qU7IlZVuR)tmGEz-@cio<g3u1*54jc^6xmem$W&g<f~EtP@TO>z6SNRC%-89TI6fOb}RXM9JesP{_^D;P`~RB6a3}cxB?N%ylg~2i^pyBmur*1*sSC~;kYB7#VPq_)Tz=kUdgwheVO|SN*;~+LuMZEmwWoPIH=@XQK#wS<4PWb_M=uM`pfn8t&)^H7US9DcCwOhL;dq#r})k9{Hf;Kv7Yhx^5r{_uX}pRUvBmreOk%m&`(^)eEA-<U)(oc$=`l;rtE)MB)=aKmrv&A@^e4Ralqrkm)8j5c^%VRj)RkHliSMNJ15I&CBJq^=4KCGKfXFnemHNW(thvXGS{&lGUw*L5%EgCqP+aPx{i7D)sLGZbMNn!_A19Mw?pPe-CX>96kUkx6i=4x(!%4^$xWSer~kfu>p7Wg=)bQ{i>q8GtY4BlHxItT?-Sy@eEIy>_<h2iW8#&30q53dubx)&7C~Fw=j-J5snIg`RLjHHndQZ~Kb;!N_t892W%&Au+?+XyzsGU0S-Lyd_Vf2X?E2fzD*4<%`F@@KMwpVDO-smJFEm&7(^^o9`%^QTzgKd-ak`Qp*d=of>(iHSO_8~IbnFEspLB-5hqAGxk{gfsdo-Rq!AgC@`5sMZvdryIgE;THgg<XuV>UnUXUaXlbW?J3{6_ws$<Hq?D(xFbbNhC4)0F(_an7Cnk5gy%nK<|3$d`v^+oP;E<aU)@y#Klvq~u0uYi^&r#9nu<RcX)r%>cg6`|77o=lwz-tXrpj=p4?6eK5{FKK5$~ynp-{>(e=I>H%(F=lghfu0=lQ=W}NrI>$9M=~k(UNlKlfRi%5v@}5@O|5j7Fp7kpw*X)7(`$;*Kd9*(p%=I5F<Gf=H&Z`wrzW3+k#@Zdq_x`MowfT5++SuHFJl{t}Zv8k`=Ej3fX~7+oZ$+LcwC(c7QsS9R=ryf?7TVACl}HNdpX2_&5;?f$|J7F_Yge!P|NE85*8?>zx6tGO_B>$nH^Ah1!Q}bC<oUrQ;z<E4;sQdy;dcq}N#F$VXoxsm=!Q@>@psvUUJK-(iAUr2ec(gEeZa$njtLzRx*~K`C{gG#{3`e|*bBb`zJk9cE-zGC=pA?v*cRF+v>W~_n0ya-H~44xR&XASb2)erxE#0&{9SMra9emAaDI$`1$cRI1#oqEHE?zC2k>^_RMDq?LL-Gf78)Tm2tE=#2pk6Q2Yw;cNYp45$le%SQsiZXmco~SDK7;kUkqLfUIq~_hX;Yz;CHKq*1}i0=43g16?hfeEQc=x_rV(J3m**b3-&<7{UPE3LZLzfg@(WffCr$>5cn`K`EYOu{@xkSP>lD-;NkEg;Pyi8gxbPeg6VI2q8@p7FnKR<2zVfT0GR5I!ZFDs!Q>IH{zPE@M}TS0Ym0e(Unm$Nt`8CG@Y-PVl3?-&0n9r1wonPd>8MZsJDB_rF!@a|`7Q7*)EEhW03HdZb=^RyzECUp`(W}G;7;(a@D|{%;4TnxbD_HMdhizD7N}bfZOAJ@#FgRigDZpIh1Una3$6lh0ImYADpXylnouxA+z?(BTovsbLd0$0t-x)-AGpSXxF0+W-U%EA9t7_i@b7vi?g{S_@bB6r?+EV#?g(xTZw_t^ZtNQC#t?BWcqMQxa0!UGIJ`2rGRCwxyb8Dq#;7>F8n_z9w>U(sL&P;8VgnuwHoz?*;<oUH;D#9Ywh(c9_y=HT4%$P+?I7X_5b-H^D)<!mKKucgoF0ew@iTEo0E@U59;dazwZH~E7~BQk86FG{#<id`MBEA908HKxOkM{}UKdPW58Mgd5ncjZ16~$h0$dhc98TAQ;`o`k7(4<@{uh}1F_=XBb|8zmXdsKYNFa;&EqEljgHTnW_V6-b^0&a`g~9E?HH9j|--H(i)BdSoAn%RH3xNya_s(96I2>LWTo}hA4o4q{!l}<gA>v{1QDE}n;Qax-*P*@7dqNw8ng}(8cZP^RgowAnH-KY=VujYjw}H2z&3d#UUk6_aUI+dGB3==|`z!jJt?+f=b!g}8y~uxr{{a3G{5^aH_<Qg|i1;h`O7K_UuZ6yWe+yp;UWs$~79zIb8^9Ydro@Zj72)rJE5K{Q-vieK*MT<yJ99(a2;L0d6x<Bl0p1zh0o)DV1KbV#5xh6}Be1h~B6jvv#C_mBz&%j65Bx(g`L=+6_w&Tg>jL5gcx=GGuN{c@!ehYXd%)zsg3k(_5xNc$AA^XGL&Qn&v*0A~3HWL732;gPzpkOzIrLhJM4T&-MVwRkJ3_65a==@I$#a5pqJ0khOiZtVUIX92agxEwIQ|XzY4B<E^#=Sp_y(9>UsV=rA(R!~5={Ocn7k60JR6vt>SV>w#IFiZ6MjeNoX~mrBlsOK`9ttCq31%^AmV$dMg9u>IhaJ81^x_7A`TSZOsKg~0K7DqJP;g+_5tumU=pzge+VXj2__LY4P+5F3FOy6<fY)0mx4b8zkvS<r~FU+{tlQt4g4qg0z^C!ehxele9|@UCn4fQ_%-k~jBz4FeAPAXSMf9P6*$fB6|9|OV0z6$uQvu_9n!ko3r_%V7TO`S5h9KjiWk}?bQmH&0*?kqqx}(x*bCnbCjSXcehKUa(`)_jgmwn-{eZFXG4P$>ooF`(BCah|4qg@_ejENB_-$~p0DjF&z6Aaq_&XeL3H&m633w^|Qoz5ji;11r#l&miKY`bPSHm}hH)E{bua`H$H-a~Tx4@&pTfp1lyTIGQaqxKX0ij=n4#MNW2f>Hn@!)vOH}QC(zlFxZpMviST@?BU{scTlXsXbBi1<tR=V0>L;4i@o;9r0jfak$yf#-qe3VkLtM`#8_{0V$6crMz10ufJ#h@;?NfTO@OA>vQrv%#N&r$NLf{B!W<IA`KZ;&PNObW$h{{yjV$Onw+lz8y>+5B?s!TBxs3OS)YPr=MFv#C?P&;%_EF#FHW7DG>2g_-ZiuMlktTVDjbQsbEuRlhBVsTi`aBd<U5P2>3Mo6hwRuBEASe0$w5XwNMm9JRQCXJRMAbH%4d{#-SCwHGCGBd>okkQ!x1gaBFZI_(CxGmtgXlVDj<cHsH1paXX0k1BkdiL_9%gzR*_mk^BcRc?_6*F?beu9BM2<9r9Q(`8x0f@Oq)fLPLcb!H0l*355yuh7Sf05(>xf!|}Ub_&u?+u83)^O@fER!@#so$6`*#V$S;D+-D)1g?uc|oyNj~h<8E6#~|YU@T1^u@O|*3VEPW@ZlMJDDsTdLEqon#EqF6L7Q7j}2)+co2)qnF9{jDwYvl|0m*6kJbKwiYbHTIW3&69%E8(AlSAv(~+`Tw&@<ZVL;A8M4*BB;YT*>#i#(59Mo_w!sF7{%6$k%{>0LQ?80>^+C!@mJ929JX;1uw<95T^=V5K4xK&tooVp4P*6gUOGB*Mk$`2f&HogYfg<^Qcc8A+$j#QfMAL8Y2D<z5z^r0vrwh6(UZ7p8$6kDkAh2xSPh0!y({C5OHJphhXxqVDc_t^3LGKV0wH{L*38eL&2Ye=Rm}tLBu9RJQdy<JOw@&BJK_E4DJo?1@8pz1s(+N2p$CP0Ivw{0ImQp2&QW(T|;ZYYl3Tl3&1OYE8uU5M+=P-3WbM&L&41<;ui3MV0!+2SL5g6rr_%EJYe$N;OgLN@XFw7;3n`E;1)Pm6Nq>Kd?a`Pc!b95lROeW5<C*;76~5>js!=*L&2dqXJQY$8N4~T88{dGb#N|lAUroXH^w3m{sx#lFPJ<Zm^?o?KjtbBUJy)P2u%Jan7lBU{4Fqf5iogCum%r+h_eV46DltBHarVB3);L5FA6>@6en~BBHjtV3?}~#Onwc#6Z|uL2KZ<2C-9HK<R5`Q0r!NL0hd9)dcuo>dxGB)ssyhB5eLDGf`h<i;YGk@!Bz3MRZ*`h@=EaT;7Z^g8t>W2qu|}a<U_#Z)4=2_z$Jxrp>pu@;1WVPh3NkgeoZL5kO2<{*Al8LME~P)HleISrQxN(rNOl!;`bopdhj~nI;ct95Z(Y@7yPQwD?;_*?}LX64HN1Q?+5-+EUd0V-QnH9dBg(EC6o^$ehZ!x{1&({JO{WixClg?7b4Cr^h_N4sZa()91y_%7nnq>!JmN1{|1wYUqZw$G(Jvtq1PbdZ17jW*}z$Z?ux&;CG;2~egqNU6e=Xz6%{H75f>2pQ~d4<+T8-*gkJ^U1pguQQ0TePeTev;&;y}6LjS;TgUPRh$!~zke+U1L8vnqbg98KDvj(t;-w0q4=MP{JzZt+Hem#Ii{3`r8xI>$OzyewR>%ag0_aD7B)s+7XJo8_wACYnYWg)SkeIJ<V(B@To+=z={pnPI^L02E`{{Xx+eJl'

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
