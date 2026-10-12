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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_004.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_004.stl', 'source_sha256': '6544b535bad4c5cf272817a2c61c30a2d5d2a55a1ab8e0b32691e8c564d4b288', 'input_faces': 1028, 'input_vertices': 547, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18708568811416626, 0.09739413857460022, -0.10764871537685394], [0.1770634949207306, 0.4999997019767761, 0.2595798969268799]]}
GEOMETRY_BASE85 = 'c$}r32eeZ~+qQS;O+-3}Vn7j4iV6xMC8C0W@`6ecDM32Yq=O;>5di@~igZF#iu5A=gmNe%RX{pHKzb7uUj+Q}%v_VRGdcfS|N1^$&$_RDXU@#*o!PTzW>1!NYo|_=)6xG5JF{nH{Ay=e$C1e5<aBzq?$)Dy%hugXckbHP<7895{4+YXPW`v)zUOgzIUg5m)w+AjZpA8ki&bh<p;$?8u{K@0_2|~3bMr3UTD2CxdW(+TTSxrv?OJqg9XT%kLb>uKy=6<3^!E4uFaKqVR3Xsu_Z^8+mv;W2tBMXgvq&_s|HO9Xm+pH=j=d%RTBiIL*DBwaH@8Y3D3)QCXlPw;<p<7|IOtAqe3Or_NY9xm`Ju*T*Smdxznw?i`FOMB*5%eJr}7W9-8nNQ-?t{?dbb~bY}1jH(i`8TcUJ65Qu*{uw_hE1owZ6d9DXawT~Fs$A75fhewXxH-08!AJUr^Izf<<sHkE!*O;t~4X_Gfn@_my|Z+82B-~1yfr8mBvK0NG-DmQ$)^Q@G7r~B%4s$Pl9bh&@8-KX;T>JL><-|2UiA831C`OcUrGgI<IHw&oi=HGU5tIB^xqRzkLst;50ecqv}o`EYfl<#|Dth&y=a_5yF?Adf{Ogs6fb1>262g}dZ{-m#y-08g!)0}W$XaCXK+V56We~-5YR#xTiO0RtX)rRUihZp~q6yv|sOn)!UGtEeJ`QgbQsq5^2{hw{_^xiJxj--^{+w9_TmHv}lv#X}yhf1|n*FVtkz!r7Bqwef>*WcIY6Xk~{m-$KgOP`sQlJE38qVfse&!>EEu%)`rq4{aHx&3gpuaqB{vte?g+rKnR)yJuOs&Ca4{9vXh)%W5Xador0KKFO)>)CyuzWz1mDBqjVUipC&pG{ZCizX;PaAUi!XWfBqtES+Go|vffPuE-dq2@oHQr}C~Axl*H@Vt=ncYd(beSM4{z3=|1w>Z(|2k(YX#-z`oegA=S>b!hUeY(}{dymvoexUoy<5j*-Pf@;a-7!_4K(9uLO4GDbe)z^Ks@(8*(^S2J?VIWPbo*W%2R65xos#eW@}+fdKfJ!3Zf}K)FG_UzfyM#l`^z`k<xcNUH~dIS>BB{)o=mA+<C}8BrONB;xoYAbmCxETsy*1g&s#}-zy2{LbbY=J>wdn$zxsT)KB@B`QRo--J+|w+Lx2CNbUp*x>g%?7oN9-mN~aT5KFtQGe0*tJsPl4$wNk#nd)@=8yw84B`TN#3RDL*JUzNZ2k%cP%(B)dn4;Cn)`++n~RX)B;)pY*lI_P{i<O-zZ`zHSxa{J**-F1I;@!oc~@6Xgr-!HYwEl70v-g%Wzrj)<&LlZ8j{GEB}l^+VtQTIjYgE0$LJ?gdEr1DSrS)G@E*-3p~5BG0W`Alo4eBX?ox*gpbt$hF6<#c=NF<tqg*Q+W&l*7MQ9pBylU1AEp|LAO$zwg_k+CSXqM^(RvrM^x~!4Ivfw9TD9Tq?c3Uy?pba{IxD`Sks=<G*v=`FL-yI+0TT#t$92sO~%Guk{<$_4w)w-47T2O_d*b{cYuY3;wR!c_`P<y8bmftyk$6IqEw27fjIKbFW6q_f~mSx1VV>^m!bqqI_q~tE#;P+m%xNtFK%x<%hBk)W_$J&P+_f50&n;-JL$%@fltJSqHYc{otYJPQ>IhX!bf)?u-n&KdjtG)iY3JruMJRKdtIhbfD_rd_KSS%Pv;eH`@OjpZ+aS{Ogs8E<ZRg|7mx6r*d88htu!U_i42b`us-SSgZ1J(&+YZYM#Eo8edhuFMDcrp5{4a`{p@ieDi$t?f-2>qRThW!8kwHdexo-=a%hq=Mz47>r_hR8sC)bocu)lCGzY0v|>B`z5kV7`N5>}D*xc6lj^*jowwGgb~0nGzCPJIsrxZ-{fzRX&#9>ym#cJFe^I{g%q?}k<~eBlfy~7>yZz|%^u^3E`2?3N)czCBu9)<n_tochAVW+(-fP-7<vPPFC_mJ&wyMA1zee|;KV1Al`KEt<vgl%cp1rj{zNPLjcz(tCt)}a73%+^Y`F7Na$;UsZo*oaZ%d^9sKG-x-_irB;jL9cFT0dt^xxQ*ESF3XAPon*U<%in#)b};M=^yO$!G^2#eOG31lD@B}Dc^VPJ9Qm`xfbd6@W8M9@K;Op_d95=YX45N8p`+A|5)`8fmhzq<B<!uR;l`w_)<TATi?}w|7_|$a|%_{^PmbjRXL%BS#`Ufe@*$J>+5&x>u^MW|CJBv^apdP^nsN%mGA7_xYd21Mtw8idDu<2SA1`u9B16=eHs5=rs~-<zq;;bJa7AEJa7EyJYx0_>U%PNbiQEu-b3e9dkbWo7n6^7=K0ex<>sla{6L=4>iaO`eA_qUeB(#w1=~lf>mK#%)K~e3=2wnM@2&g(X?Omi9)-2fcs{hYk;=y@I(?}sm+_=;^Z}L5cYXNMnERJ;Z=658j;=4h8TXp|+W6l38}+#Tjl`Yq^ufAa)&1++K6IPgH}|zE*U9{pt|#LVGp;bc89&&*|3no%-gvj9?w@M)RQGG}_ANcHT=<24o_Cz6#)H0lMOFLpHSMO`#e~A&tMe+_Mzv3Gt@`RY;Pfo6#v`G(j_LF-f1;j8PO+?doO1BS8h1N%E+5z9pc2DWy9(y0uJd{8fbzpTO6&T(-b>#Xo@UDTUTmQ5yI`?Zdc2u%cD_nq_fORhgPv#fecIzY<@?TM*7wEp_x1hw_Lh07o{8gCJ^cqa>;C+?;cC1SX!7Ewn0nSLrF?(+j(U8xw6D(R)$8A?a{K&OU59X^NxJ^+mnz>mHZ?Y%@BUK#kiY+ZRi9vBxX$OmF6}S)>9DFtnSb^9X1Fy+)xW_wH7^d{JFnBXJUL7Gg~x7*$sa%34=mrVpZECw-ScAl0jJ<FoqpP%Dj&0sVf)c_4E*SNNd440e|+y}xmEprUGwgBr;o0O*y-Qvrt0IovVNUAy?<oyGcon~t>-Lv`w1P+v?wLtJFuNvS8>kN*X0&^M347Y^wRC*;ooXJ6?!R~x}Jd(uV{blui7{Lo>>pE{OEcJzFGG${hsmt_lq1;<#uneJ0^YV!@6HO?~lpH^oP-MGgQ*!KE_LC9U#u{`Ad>Jy;%n^<0az<AEwjm7}bNj-08!qe^dR5cabM1A2VKxmb>+mS}!s4O*2oleeXk`&L7{*6Yccj-xnx9So5+zk0!q=Kf3;t)Ind*b6+aotV@JK)Af0k$sTmyr%vbFx;@zblshYx9-pSqW8_WseS}M<)89*jJbHa4_tz@_V4YdoU-MwP`~G!uKC?JQ|AV7C|4X-&AI!c)j~hp_K2hz|ROJuLs{4&|t#x~=c590IzJ5Kc?w8P+YWjY;(M0)ycZ%uz=*QjK|FwWl-=Ml)FYTIEub<r-KT%!J$qV%O{FMalkJ|E$Y9}>6RDU1zRnq0&n5X>E?(53;{V+uPtH*2qxAyAq{lB)*ez$7McRK#1$3H(^(f))C6IA~Dx9j!NNAl=$`yCpi{Cr(v`=#xjMk{~OyRrV#<0Dl5r)MU{_;c<IQ|T)v#HQcSM)`puD?%~;xNnEL%XPxV7N_XnKc>I0ZHYtN^>N0{T%3~cEiz4~|2y;Gn0gMWvm_<onO|L}Z<2SAyZ)h0yO*Todtb<)(}$N0be~r!%Y`K=`N7uztWbX7&6>)m-}4O#%}>b>XU+0MjL&@$>X5K7MSrz_wcC%j^QD~@rs(G^ADf=*;5(MEC?!8Iz`rV{TytKB?=DKocRatZbo<fkHs#Qwl>ET-)G_%-zu#F2->2mJri5eDn|AU>+l49n6=TlVJb%r52irIA9irEPal2XPkMmjQkNV8t&3d)%J9`Fgcc(Y&nP%NG&i`+&A7koSZ>Jt-^lZO7rd-yIodIvGbm!wc*-iIr&u9KACZC0R{1<#`*`AnulJ@BStNeo)KXA65>My*zj>o3weL>)hC)dQ3+v&dUe=c>{8=H@Q9~2$u;D>wM(|*w}_QmA?&j`J4Q#r?ex9{)g(d)f`PL1)S<ET@k*2m<3V4hC@-k6y5;YBA^zwOPGeqU_<`hAmK&)|Cn)pNmVzBA@J1S=2M&x`#1V|?@8$IS1d>D#`f#v4IT-k9&jyuUE(Jkk1eDy98d&12ewS>LwXPjL5H{k+aNWk<|;^-R#?mT~=(V)9`f$!@pdWB=-T->ROQW9rHL)V?o*yMlTgm^HL6rd-Cc_I(%ba$NhoZ*l@%%j)a(Z|r=;IrJZ;Zy(U*c5I&H_5%&C>2mXS(DkhFbbobh_s^Ce?Vq2$tNghB-}0mVe}$WB-8b&}V)@bMi!=K(m5=@Wvi#`tYyYs%m2W>EZQnc}|E@X2eO}S$?D-=@V(M@FYa55f)Zh3!H;s&`kMZ+XAMGwT>ObFaobv5)MYfgW_4j0rLmH%?psueyZW)oFeS4g<t(5ZP#ziC2f1}!^J&yWx)Ff3ud)zf*ukz!@Y2g-=RXTfI7p^l!m1mCwhkP(i`S!T6K^Nu6jX!PQj6eH4I$fzfzP&eI`Elc9+c)FnR>NkfdfVgeXYvPCdV736wy^T!<^`4?ofqK8%?pfg&kKI(q5QacknNj!5PsY|2tRHfgdaB#GQK?z`XImFUtrG@Ek8O>#E+XN;>XPsO?rEth#xmk-1D3+*PhQV9;NfK=f49NDnD)>ZTZo8^tH{pf3?>KEI+zFfFHL$fFHL$fFHL$VA9*`1Nd?41JC8s>xlMx2!7mp2!7mp$kF0+R6h24OEA@3mEKyPab7K{eS1A;`P<5O`VH2{KRvF~SGYXaeg8(wJzeBmbsg+=BySt#$E`bgwtnlrf1~-7C^1iIp^`D{TF$Fs<;Sgqt;((D4RPyc)5a=4Zk??_rUfd!wJzrj&Zhjhb-cUP7sRwHQ_t3o)%ZGY{V-v%YL9X2kQWB4=V9DBr{#w-4BqKZAGiLAAGiKlzt~b$e`{Sg&SzcM`1ZQ4@$Ge8<J;@H(e&23ZeT=3<=gAe&dH5By|rE)`1GPqZ>^u(esrG<zP)}P^{w@D<J;@!&XV`_KCHCU^mxy#4}UaH`_}sf+c)nQjBmeRFuwhM!T9$3g{W`6UvLWi#&{(5y-C!!-kTWTes2;;-+j4K`@Kw#h02e6k8}QeJsz~)`vl$`sruKr_e4qOlpptAsr3WBU(9+B6{w=;qxO5N!2G((x8Il9zIk6}eEWTw@$L6zPWqf`UBP}o80YhT(D?TILF3!+2aRvPA2h!GelYO(U|p{D9@BZJ#~Szj8+{*Y`Q|;W@$L7p#<$<YM$=pGVT~X69=84`+PB^pJ5A^4{H^!SfmidbRr%ZRsf!O$zWtuv_M`8+@$L8Q#<$<IM}6x(yYcP!?6w~*_pjl~xAzG+bFb<2*1iH~-hG|k+P4t(t$ho|xA!dsE?3p%+xsP^EK|O{Ps8@jJ`LmB`!tMi@6!lWIibt7_J;&c{h{|oTKh?yTp853$=-hw$Z=ioGqv`sIL#VuP@h}-Tbv%D4etBe?31y5vk%Ak_C6fr+xu{gZ|}pg{pdcN9LIIJ);=QJH~WYJjY@4)$JTzNK$}j=kK4br)=}dgd%u&@YnEQewDw0ib<Zf@-p6J8W*?XF?R{LvxA$=w-`>Y%`(__k;D-y!xA&Vlh5yjyTKm(S+m4!7+xyu9bNcCZReS&2%?rx6_tAyMrP1pb);>MkH~aJg(@N^=VeLP(eX|eH`1bxo<J<cWjc@NijOJtQKeYX5xgS2KeQW<@pleONFRw{Y{aik~LH9p3dg*eleVfL&_icu9^w!tM+AnH+d%vjh?fs%o&Q^LnW$j<J{pkMH{@s+?`(PsjKjqu|W_{0I(&?@Jy2iKn>qdQRzpm|@{kqQgwe)(HwSU<5&HiEEmoxOblD!Z4!C~dw`=z74wO`u!_I_#O+xw-XzO`T4_M`jIvLxtnp|!8uH~*Qf?(f&EXByw$H*S1;-?*<(XXV@b(tUp~P`<st-S*A6-O2uhe*Red=WXBYpAY>$K==37KKxLdP1?79FJSv-9mDwc?*(k%PH+ES!1m4fKa{gTQp|nCI&hrN`w`>Yzk>*MJEy+~>vtTsZ`Lb}Z~u<N_M_=<yspOu_U};e<9>%?`O)8@;M>1L@ugW1lV16CV}1oxc<ZLumOdN#1|pHs$?3Fd;ra=XnCk06Q~n81`*QzZKLL8~+2<?#-+lv>>3NUiJQs<6=s5UQ`RXI_A|d=NA>4`(UVtuxpY>>c9$f}Y{-X0Z7JnWg{4v@c7JU_#f2ksoIT8;d@lPa95yHnJu@(I<`VZVIQdZ>RJ8u!fbtBOR4WNDDRgu409*NV0@bO4&Ll>gU;fIm9ABj319m4e@+Sa4>9>?O}qs~&lRm3q@UduU;<*su&O?eNA<4$s3_o>%?R~_q6ZZD#q>)iTMufCq-I=;pEKj7L5n`<Z9hGTQhr2cnEEBY@i`IM(j(W<c2{}0Yp^cpPntl-h-B<jGcNOKCk1IuR)`HB9)wdqA!b<hg%1L`LA5-rcUN`80wOw{B0yexT$R)(dVzp0Dp4Oq%4N4-T;!PiK02fYhBq>=nY|K@sBrK}2QIrv}dCiU`ACt=C&Pd*b(?fU!$@(`^8|3y8dJmKpczes(gJmEAPU#HGDNc$(psYoOFq#<A7%9K?OeGyJgojmXh9N(tSlCN-D*XJ*hho}#ha(<^SqE}%lry_L{O$T44&eutMo8vU3k^Dq|=XzA3tQXOWa9Zk=8h(jm$?qoh7ESN^{AKbGeFc_sZc!J}E3lMPi8_g9fUlC~HhL3IM;ggb^cL5{M_CooO0d)^J@raYorHgg{7q6MmY^%(Pa>c7i9~m_HM~0VnLO)%K$GC^r0Icv2zQHo);SXIqjljWl+_LG4F3@Mn~fe_{zl3c-V=$V9{u@IJ`;YQJnNw~;H8mR>FD~dq^`m}sN2VAZ}@B^eu>0p^e1>TJRO|@_eMWPXTU2ddn7sn9tpQYo51bh8fZQE7wWVJJqnkId{!wEMbPKrB5;1RBAg%g62hg>I<V;5a4EPd+8nM5ze@=BCxkyk--bVfKSArjpTIrPif|9OBl<kt5pIK4g4@8I2;tgj3Ai@=0wMe~A)FU20_TMvL-WIr!C6o*oCSUqEd@Uc7ecGTh2YZYyKrgv4MMml+8^!-e?tgQM?Zt7!*kG2;5qO#v<Ey5o{Dyar@~{=Ht<;ZE3^~54jqSfg2%zV(b{ltxFPxi`~lhseF1I+zllB#zX?|+gr7k3!cV|C(8u5$a7Hu>oDoigJ_@IS(-XqE(L!(`zRTQ%@Kfj;@KbOFLbwCk6Yc<yLBD~=z#9nR9q4p;2fPQJ1Mh)<MyJ6)!$;An@KN{|bS(S}yb1jZHtk>&A)GJLUmcFb_DC!tgy%+LKDrOx4sYjg_7TFrMdEMtIC>a94zEU+z^ma=gz!joE<6(c%vGn)2;nax@fErhoewXCPoVqYebny+A^ex?9R4DN)2GrQ{1}=lm1fZl@MCZuG!2{w&Vl~p(VPR$g8mLm2;Yyy8T4oLclc*`7a@EQ{Rch>pGKwZ(;N$5Lo>h<!hfKt;6FIuE2y0R6|T*3_zJupT@9~?zd=XA-@qL_y8Vg1gN}kn@!h{e2)~Vf2EPrzi+%yW3paALk4A)Wvq-c<$D?1t<KeaFQg|(V2|WRypsidYgdd{PZXR+hoRzlp7@QSOK=Z%}@Z)F>_;I)ZnguQZ=R&2e<l<O3ZK~w<BrG9(oe<tc2(LnahF8Ih(OvLj_&f9<{2jayJq<5}m!sF<<?sgd4|oH-6}<vqp>1s?gr}n4z*FI_Xa~3}T+r423Zl{<7UWnsL?1a04#AVq-tZ)N0NM~X&&vUX@aJeF_;Yv=`X)RG?uS-}`@vlz(H1R>R)$5NfXl)K(Hw9=I4hbF&I+eP)4=Iq51JnKz^T#PaB4Ug`V^cCE{axwi^9(l!mZH`aBFxJItCsEuSGY&x6mu-2KWkmlMt5qmV|IdbO$UUoEhB%O9(%L{tQb9KZ+iOC4{r1zrYg0dC*O;sI<#Gw9j{7(YN6|aCY=vPja5`Ql@AlPjVd^QAg2cp5!_=<D5+YXwI=6*C0LmGTP3QJZ~25g0_RZz*Eri@Dz9px)$C7-$5_Iq7UIautVP}eW*hSXCs6Qp$TvTeP|&<xCmMRE&>-ubHRn-d}vxYADju5{xlQE!haIN+t5w$Hh3B#JQ-aDPlm^$i{Y{G2=qI61pGO=5dIt<hAxMP!DG-3@ECX^x)m0k3QvSPqFv#Ruoo=|i-sJ{UU-+IbrQS_4x$5K(a+%^JQp1V&xL2B{ovW~6toLG1)ks}_oovG;n9&8k9I}d!d>AiXjxdaAY28063q%f3Fk!9!8zefs0Ypjr$tl4Y2gfna2_-lELs%K0~bS|gNwm05yBs$t>F*huhCKP*YHMkEo}PVji{`DZRA)u6CvCltpr!1Pic>Kf!o6q&?)c)cpbV0UI$-B@4$EHKQ41D{4bgfmJogvuMqqwoF6R$=ZC#$Vb}{7MDxJ~;oN8@I5(UQmA)e#$HF%V;Y4&BoCr@sr@@opPK5AB=w$dKxHCEy?hLm?N5C!Nrs(HzQ@8;-3~m57M#sR7VLv(%o=899Cxo9sy|AeC7f*03ywA}ZgoE@8`v~E~=xq2fd=Q-iAB2BGC%`|!ThP()7I?j@?^sU=ZzhB%6T*Gbu5e%YEwl<;g}&o0LiiapC;SYY56uMUgR`S);q34uXa@KZI2)P=&ITu-#oz?E4EhpW2Chj6_d-8}d%+XYui=UCPIM!@6V5`PBK=4fLby5F9&QegMkm0d;brJLco}>Wy$oNbUpPq!-$kWgxXZC{W<oeSnjg+jzmS~}&Wjd=^TIjN+;C3#5i}kA2>gKlLi&gYgm9P;UWq2cE8(xvN$}V32WThw1Na$2xD@&kTna9Oc81HqrO}pfX}BcX6fOxrjW&RvhKr$%;bL%6)DQdVBZ{KZ7ZgPg!xF;9(1T8Lp2AO~KRL;D5H5*sagysSTpC^PB%h;j8FaIgd`*N)aXm$Mb1eRD(oTj4Mf?_#cry}((IRLIxCs1YBm$AY=@W^W=y&i;ct83hydQqbqgC>FiV%JuZ2`Xz4@U>V!{P4<;T4fsgMNw*f(LO9pAy2gUFTUFeH^Y0*NQ|<v=I6@TnPTv(II>mEeuNthtVRigzy>kN%%>w%Nas=5&9jx2>uA|1AhenhY+rX2H;w7gGjVMhoAv?2>dNN6aE%Hg6@Zpz{NdU<-06S2scFEha18}(Bbe9cpmyaJP+PU2p>RKzz5({u6A&W5I!c~6M7*Mw<2*f66Zbo9iQk~^d@{3K8jv|FObhsLU<#(2HptwK|h5*rET>=Yr%cs)~+_!nh=(El{Gy2z2h6`hwz7_d4muxfEI!az~>yT(q7LI!Yc{kMD#422q&RoI0;^Xo`KKMMpqERozair&Tw7yKd@+ZShN~k7p{SphikyEp|8LtBk{7_i|A|cYovJ`Ee}5q7a)WSqt)QTaB;LcT%CFsM{B{gxUY&6!sT4|UO7VeJwkXOIs_gF&qBY2XTb;1Bk%#Zgh#8~hb0K%CTK&r3H&8G1pX3UgwBH(!H3YD@J{Z-Lxk{c^b~v>zK0%z&HZ@~y#U{XQ>W5;6P6Iph~9!Fggp_x7}5XAH6Vn~5yDqdNqZH&g)e#@z6$^7N$xLxB!q+LblB_<2ok~r(HihTxLPFgq6ugXI04R&z5&0%{hXf=KJRFi`}sT}JRe;Ni;jfn!(S4@&CqsmJMOV&=xcB@xH0-N+!%fxEeXGa`p}YaO|%SJ(n%iM3!Cx3a5nUD_;K!4Gj|X+^9$kZXkjOLJ|dhCEe;pwJ~VR~;b+kIoaDKWu$dnT_eBRf$#W~=$>=O6c`hcr8$AH;hGkrKfcw>qdxbwhn|PAP#=>8tUwV?q(!wjzMV{obw{RFe1Rvr)G~;&R2k1Rd^4MNj#{T!X=geFnHFJg3+;3*?kde8CsK+(e@Gut<mHW-iO@uR}7d^@I8sWQm`#s5XA7L{;5?+Qb@FdTzgk|m}^R=uVJ)e`gp6Fgw{Jk6tXCs8`6T<JISzyuT@O$u3bTmAgIt(R*za@lsp!?zdoaYYo2)qLh5yDA?@NV=Ryc^z&UWG+}ghhk!UU()t5S|GSK&!z6;8#7#eb%dl@M~yp_;oZFnj6jq|K{irzUb%>zJ%t5MH65N;mc@#SXBDE%Y^Xv=zMrSecbni@Nl#l+>HK9co^CgZ45W2|7z;$*P0T-EeYZFgs`6wu8;a)(VB35_*1kO{3$#God{2)9nT<y524bgg-=G}L?m)}bO=9&9)b^%{xL%MKWKfpCps9d57*~@7>o{uhtlo`6T)-Q9q<m?_Z&iaHkt${(Y|LB!n4r5@Lt;PEJC<HIshI(d+m?D2KR@%x!P_wLbw$nT%8ckiROZH!WSH^(!MVc!rRe{@OF3&dI??wFGerJmub6;(c!RZuZs!cp=eXMDeZD7+8!PXe}VepFW|vweYietQMhhxPpX`$|6l*hljMK0*W8KuAE4NO8T&H{_g|)qJcOe^ny6blt-QN%QbqogNyBaV)q(Rr_V$VZ'

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
