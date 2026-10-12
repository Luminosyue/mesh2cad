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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/649dd4c47d6d4dd099e518d6393e7c5b/part_006.stl', 'relative_path': '649dd4c47d6d4dd099e518d6393e7c5b/part_006.stl', 'source_sha256': '006fb2766d714eccdd5cc6de1466f782d9636dccc495d813f8cf3bf8134b30cd', 'input_faces': 766, 'input_vertices': 496, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40562570095062256, -0.12852540612220764, -0.3365379273891449], [0.18115031719207764, 0.14154833555221558, 0.4999997913837433]]}
GEOMETRY_BASE85 = 'c$}r22Xs_byM|9tKq-O<2#PQwU0Uc;2c&mYL_l$9p%-Z?sLYR`D4-yqh?D>!iGhS3T7ZFs8cGPEslXuE5cOIR8*<Oy-*aZpo^aQ?>t6o#t@oLCcD}RsxA)nnB){D|-F0_yOa47-%|EvBeXEv@b`-LTTayNln=owP;PEv_k9{@DDyn_`51rq&XP551qpV5Rl*)q!j~_U$a$`^BrZJ5wSNBwo88dFexc;MG95ZgvVCA>%KXUwF+aEu)|JcFy=PLD{Xi(i#w`z6I>z@DPzXEm_{QGa5-=nn2^gs)xXWlx!$L%-Ex7YN4qy1~Ty=QO3EVpkp@oPVrc`@7Yn^}AB*uGhwz3%p&{a=dTytTAHGvT!Om*u$4n@fN8w$CzsuaU=>K8F66)V}X%zEf`BYVpRM{gz)Fz9;<!@)Vcj9)3F8?K^pL`Q!=v&r6<`W%fz_ygGkiUnj$lJ=`l>{Em{RpFc&{;rK+_w>HM*Igx7kRtx`~{g&SvzHeV0j$2kAH+X!V_Je!xH^%EZn0(UhTP<F@v)}Tn;m7WcBL71=zjZJb|JFJ8xO`b9a&&$6UOp$sEv56sp6p@x&bV^<jLY$Zf$VecarsWRk@kTV=ZtafZ+Oz}hsL$Pf$2NritwFr#qRGR<JvP-+WThearv`9(#Q4hd5z;1ll7VL&`G!N95<KGaUI{<<1>yM$S5oI-`&lqoB!0I9JlY(EtgN-96zwTjZru6sqNbL?)v_$yZ^rQBU$2K6Tih|$&-HA^u1q3_*c#vbxZ$D&fm19XWjkx<rF#X_MQIc^67ur|M;xY|D1oN|2t|J{SWS2nPvF&KbKGc9pAU3I{8aU{`5`K|LqsgxR2}4xli}U+Wy5E_qc*N9>aIWmCI*b!JKm14{n_=ev@f>U-g}N+wlF(?l$)4Q2XYs*gq%Ye<1CfOlIG1l;!rVX8#)ddB|_xl>N4Y;XC_qAoG&!w_9I2<F1b{JzeUyb<`Pm{jKzkQs=EB&$#QK%cuS!Keduk=isSt<h)KTM}FB4y*YmvzEkI1K6Q5dz~+q8?*98T?ve9x^N!Q*{(Ce2%rboXpUbEJj_=)^M1I-l1KBI(eBAWjX?OpF*$Ia4TwikeTwlWe9Pxc)_5Ksgh}Ql0ZW?Cf_hrw@ar>d`V5IL{2Sff)qyL`lF|xmHY-rTYb6|=-u5V*iqi)uLv8M0Ld!+BoJAQCO5o27|!A<!08vXHQ6_EaH_*0a9J~pek;XC8a<uhK#w>F&3agQtZ(EV~<UVk9RJud&Df~N26hmpRsAL7TZPtS3W%Xj!G+VA1GvQGw&4cFIY@A?$O_hzQadAB~<7;o^{m{V@wxxQG(N8_($yjKn1v;GrfT;9x`*>2y-lglTM;|JHx6Tf%jc0JyaH;?GN>n4fcWA@fN`U5g{x_!?&pZI;^B+v6dAJFwl=^*~oSvrsR`CswdlV`$Cvwb`9`_|TZy#F4)q~|lGm66}-J4d(or!+9yTeolN_P&(5j7!>kediBK`#SiGr2VMlJH(GB|4i{?5<k-Om{JS>HSGt-{gy2GYvPZT@wWX*&cBozjQ5|d?tX^+zCPXFGq(RxqrI>FPP2V=+IN@!92<5@+CR>5TWddXdF44hzLaX>cL;3J{>VR%NdK#nr=D&f`}?H}E$-lZZsxsc_(SLJa?h`oQp{){{QVc5Cy<<9{4T9ijrmQ^M;>dJdw%`Nzv%UAb^T|HdwxUy&_QY9AHn~b_KQ-Dd3XFFYtzJ^rG0PmH{uWSr@80doBXx--K$HU+yChNA-~(URH<9`4x|0hdTH);<w^dE{v=ACm~DEUg#4HZY3_C9O};Ar;Gt>8x=OynahFJ*@v^Q$e#~>aeSr1mN&b@dvs2ycE#${^*6n>E|1#tC%e=7OLViqB>Cf1K_(AedNOiBbkRMZ9w+|j2j(>^#gHqk=(35<T_8#f~<yH6>X#ZTQdmTplo||`HH2fh&)1-ay!kv6)-3Hbk6TgS7lhFEf{J~i}#s5|N{<T}hZ!>$d`+N!cqce8P`oAIP(b_oi+c(|fUgzGmtHd91&u;fRx7IEazvJ31vOeE8{o#vtx!0{PDO!A<$DRAekk4~>r0+aOTW2QW*OvBAdW>;}{3fp$_md&N**|yon>XfuvSWnbl>5n`T-TCniQg``*<GKI-{Co<4k5o!Ec^L8rax@`F8BEx@<&{cs2l#MK}P*U{+Q}}-1F#5s!9FhcDc_}Us4T@yI_}bo+drcacAywpO4<8YUFuM_P4e_%lsr&rTxfV?(@r+R0ZF+%Y7bslPcqP-({RHNtLKuqSW)>LzfJ{<8|#j`&h{DR7Ka>|NF%Yck)B$m*aPyzD3T9pUw6ouBN%qm$2{M<vt(1NfpKC`s=xU`;y_)K6HI?{83}2KJ2Suf3wUx`+p$uK(>rG(O5qrKXe|+bs;uU?rS2?Q-9))>^q&OzQj+(kJtyiiHYKm4zLf%buczzs`#OOM(P&wL;H;EKmLT5#qYM+xW0t^i0hOuVUqX}*AaihMDZi8J0XAYAmjStPnf`QrJvsM*OObg{fO&}KVdxWo$JdFdksIPy>Wf<C5#h4bbWd8sNr*c3Ek%;yhQ%7Qn#Z+<$fk%EP2f9NXU<=F5`0Ue-g&fUal9;I*;_7bsq8~t`{Lcbe)pp`V&SQ?VanCFJTn*ckV;j#~eQ<G0nXWy$OTqk9oi0Nf<=_+U9*lLT~ar_eF<Hf2fc9BDr6(5}p%3;=U{7N8ESC#y=r`#QmEuzJd51(v15?e|&xNnD>Fc_-OG%_qWu+@qMk$``Gwu;`dpw-M#+3@m0m|J$<`-J$vJ;(9c(l`)zN0W%8K!+ury}w13{XulB}Q#5eDsJ@JnjbqL*uMEIe7GUR)W`)yBr8Tu1zJdb$dOHv>6c_-vYJnvZXCCFcWyL+7kR^M&-q3590w@<o{8@dl!{hj#TXKr=RW5|zqUJJ$@7oX=Nr+pyqfV@ZHxzcm=-)zI@c{!KQ^Rnan<K($N^#1MWExAvK+d%%Jyl?Mh`p)xsr0+bB<9p(k8~t?NhlhOUeZ`3s!w)@2hx}zmKVuJfljq`9bMSetKb|Ph^{e_D{SO|9Kk4?Z7O&jV_j`keA6(gk{3UtczFyu-uWUhnc|YJg*(pc-=H!3v&OYOEeE-VYM*qDhz4AV7#U**~)$BgrS3i2v?T7jw;fMN<Z>>0$<?g>{e=Y3?V)tjcj~ko4So#^eH_JUP&#5hjA9|l3={xW9@vYd8jXeHS#|_`f<3DxG^vUD+{^hS5{q&yVz0b0SMt%J0hqBzh)nXF<LBscZFB-mYS#9zc=l%IP`S~WdP8j`n-aq4q`XA{#{SW!So^bcymvc+T+jzOOZ}JAu5i?I4KEKzC^qu#^&T~ZIiKXO`=LO&1C$ikWzu8}R^sVNNjOT^0Z$2+r4SzlEu5)1Dsw}tf)H%|3>KyieKJKowH+{3bzpX#@xUmj%ik=q#_2cgP2Xe|AzEl5PKJ^dz(Nm7OkL%34H~OVx?s0k2w;H}PE>C)@*`9GZexO#7WA6S3PhFSyy0xOn&+m7bcgGLy50SpJKRD~8#>AsW-7;=VJ*zi6YV<$jrs0SBAK{1k@A!}ZkZH_sM$waQKQzA)erSI21J%CDbobNRUrqM4YKQSl@qYe88CSIpneO@ovg1sj>q0J{>x<+2D;F`2>pd_-`dRtsBSw7=Og8*beIoo&eenI2GLN|X@4UwjR9r)TxxNIl%9_5@|485IzvEZvdBolSz#+L`@m7d7`X76!q~SaLkMy1X=knSAz5Kr0|5#z8|K8)14d1!GMEcJ4CG6j8<o9JBlzro|D~H|vkMy1Vx!RN8@%`nZq&@qR_sq+3UYEOlNc_g^SC?hH<!<3OkUV=k$$47#bL~5SU*S9R&S|&r{GKlCpBKN$B<*|mHqJ7A*>9cWhWuuK+_^pPZJhT0?MsriKVy7AY0yeqqtBbIBiFip>-!4J_0OHWwMOTgE`DIg<xToHh2M>L`&Qcx-2Yx$ZRGi9@l-i)s;+Xk53a2x&jAyomKyE%7kN|W^}7$<?Y+-@so&FBY4^Nuw9l-zP;1JHSF{cox<t1>l)X{6|KgpoM*F49m+x`;PJaKezjd9gob|)>_t~{pXw7qOoA&1}uCG7G#eJ-Q?pSxJoBu{5t-j>>`nYlT>-ty?e($f<Q+tvAxsE?co{KkM)>^042iiXqrJrA{<;UO9I^~f#U7wP5_4Azn*TXZlU;H;cuHcdK;`jV*j`n|PwOIEj{n#o!FHv3QX=S|r>3#HkIDTjzPt=g}^6wk-b)N3^bpQQF6XW&g>c214$9d`2R^3l;l^MEy=WjpM-#=VBLFc)0S-=1A)~Nf5_RGh`DnGWx8SMvdJ-kHw2U1dWp1rMS>CgXFY=zdQ<#qr3({|{*-al%t)c!LCKh^EaB<Xqgb>AcYf=_iF{1g6Jru&z*Opn`|wo}hn@L_2myX}zp#Rkgym@-@cywBe*&Zy6YG<_V$53PstozwN_(uWiDaXOsarhLzdxAeO8{IxJq`|W?)qU$i_oV=GR5cjFfe~ESaxK}p6uiLH65dY_ysXG4vkDd=-Ql}*CPnfFDC+q1|A8EhZhuZhIYqvq?KXpsqGv)b0+Q)5`^QO(brFy)@dg}G)A2(&E9#6_?z21TY`pG&i_J`Er$qZfhV1YlxpD`&(`wK?tx_SFPF6;4B+AdwsGQ;(H_OGcYew}tJb^Dpqr2SK+<@dM;K9KjQJ)17j`CD`o|Jy7%Z?}ItTi0`aFY(7Tm*>qz(>~Cjf1NM>kL_e%7&-7AUFScRiT`X<IX^f2s`L9k-z|Qlb-FHA^lrV5{lUZHN1c`97B8od8ylS?{;Ix`r)-z^bpOA(B7Vin^1kJ*ZMr|68#lzia$WL!e%9;O`@&7}PxsoPwZq%GeV|>Db^7zV4$}XFAM5khU)3XinP|x$e^`$zHh+Eb$Mu&y?~T>I_iAJ9`{#9$e%{qppXc74y`=rT5;Csao#i}QKSTUN@;=I{{iEy`;}(gZG(+;2iqpP#!Zq<99J^c3<MuaYzltfcUgnv<8~kg@LRnW;wQu#QD0P^cr0X2}F8<ST($BFA^g0jDsI}fWzy2+%*O%iv=a=WPMRI-(tSfm=Y?poQ{bI5o750kXX_n+)KS0lyZ~T+umpm%(Ltfmc>+i4MM*O@3rJr9M)b+8Sqs8}RNPYf%^<CY5YA^BsUM}sYRGua0^8oP|o|gQRugN-mdI<UFNS^L*$~=~uB>vI+q|Q$k)V}Zd2B~LidYV2TN3YlCqi5k}Y5(~}na8W!<h&?!R{X==Wc|EdPmcRQo(($Bwzs4Xv)Px^?%N=Bnj`-0-=sd*N{D~p=^b*u_mKC^7akV>p{g?8SM$nwdaR82zId7UdpvWsU$c_<-|dp|Mvd0<5*&^{b(Q29u}A85wZ8Z_PRRSW_GRZAe(kxEr^Um%{(+{A#4k5Q^3;4~w$!z?_>B)q`zDXeIv<UH<9@00Q!AwY<vWPqqoBS{`PTd-?`uc(6#v=tGLOkiWZwHtlzOh)Df?>XB-vO0eOuZm@7L=!FeQ)dXYsSe|Gt*q_X0yI%D%U4hxo0YlKS^Osp}v3=8*V{%F6tf%8_yP%ar3TX(@HSHz?;<^ykuk|8}Xv@U?ngJQ<h7f1tF~;rtZc|KPQ+B~QKnk|(C1o-a@4x6*#$ds3f`b!5CPeh_~W`%l9JnU}wQ7r)W~X+LeEoY!-2ihty$^k?pFz5m3nj*|PSCESO#y{-K~@j~K%+C=gn{6x;XH%p4YdW7VEqs=Utud?Fji<SDm=F@fXUVcpckDihB-*LM1e_&(r2XemLU0&}qftyXm|GT5KU!JJ@?-}^K_@~HIDqbJg*QtrT2Y2?Rp{?b*j~{v6_h%MNGukhWN!;V|L-)N^<nQu)eKrN$?X8+O^nIM;hw_)GpvU1!DWs3%+?V=ad`RCnIlj|AHZ@az&rrBrhTC`UpZ$ORnc>c3jlX}E&gZRgz{r!HBfmHJWat5-y>ow_cb3uKxzG1s%zMyi&vSwGQ!T^yU0buJMR((`=XXa<j~-gVvQ*q_6}MvgyZ&@und+aTcmC7)VfFr3e>&f=!T<YD=jTOP)|+<BMc;zw!XKb-!%E+QKY$n5@gX`3eFs)L6`lo8Ltllb!LJdDC!-VL$?z2P6<F!(@D%tBbUOS7JcCgDE;<u_7ycOi2>uv8PAEQx&WDe|N747;qwo>*J@^P5AQbOJ7s5&x!AjS{SM0cK$5({nZwSTL2*uY4#Xk~?e<BqBKq&s6Q2ZUC_*+8p*M#D$gyJs=#Ty94a|p%%Ar!w%C>~EJeu+>#hEP13P&|@QJc>{}mQXy7P&|Q9Jc&^3Clt>{*Td)SNVDSvp?D9WcoU&Gkx(2<DE^dCyp>R#K`72b&%+n&*k#8lLh%7Y@peLS5}|lCp?D3Ucn6{QFroM~dIA2zj*E7jM04Pi@NRS;yc<qN*TKo~GIRyJ3|@?W0xyP_qpRTMa0<EwPJ#EL2jRVNHlg?&H9beY&*3}uKggUMB$qQsTbQ>k9NU@4Rm|-w`s&Q}C(QpRjLlgOiZ`L_qQYxN@g8(vRCrw}K7r;$h1Z_q^XNtRJe);bWPBHy%X7pR)I-hj=gj}-d=8=);2``NdJ6swK7<~C55cMEb~qJ|N0Z=qcqzIXUJ56mYv2TU8@dDD24|v&VP|Za=vnwIpD&?7_!4{u{R}<>r=y49ba*403U7p0qVe!bcnP``UINFV32+>|8QlhNhWDeHuroHr{q1{+PIf$J$NhFZWXEH647THWJD#><k{t)^c%M*wh*113q4-}y@i&Cx0HJseItjMBVKw76NNH0z30B_ScI34q525%jGzz{8wrH=~dF@C+TcCMh70G<Bw04wmEnA1$F`Q6-Ei{?$NAR6$H^h!%cEs>`7~c=$JH<6%)ut(9`;<^zo$spCR;lt8KV@q-eTyiexIC)9Yln7(+rf>{CU7ITE?Nh!3qOulgCB>>qL093;Sy+ZxCC4TEeIEZi=y|zMd8wnOO2@%S{g1*8^x9FsAS3id-Pd5dfDMaUx0n^a5M%U4v#{Iz@y+nXn%MR+!uWg?hAKCJHcJyw&;^^Tetz*5N-h1L~Fsd7-LPwSc!2zi>k4D?C4?1oO@7JzlwJB<hzQf2d^SIo`qH3es;WQsXuKJ9R?4DN1!9&5%2(XAUpu>jrM_i!=2GCaA&wR+6Hb7*F)>W_2BAg4Y)e29*N4?@t_?g3B`r%=x#@QJ30`G8>3Iajp1mtHXIFCMXSJ7;WFsMa2fakv>5yVTmZcnE&vxs3&Dlxe_=v#DdxBob6N`DgO-Cma7DBNT!C6SbFZ`}S_7^LH$dxK;kBx`E!xHkuWiL$(Jof_Tu|H>?PG<{9mRvtfmZljQ#=YCX@$>C#lz8IR`^_2>_cC)!sotXXPqnViS~n)J_GlJd!XH6r5&vBIi|ED+5zqeH$fZ2P2f6cG+YO+hE|2E!H=M2;78!%=mT(ZxFA{pE(qU;7KW9Ug4N!k_K;ezQng2_{aIZD)PAq__7ZRjzEiCB>PECHimLBQ<10_?pK6cm1S?g0XAJ%jj;D^>5HALf;k$<9Q+b_hnd0)WbKUD;Ul%*t@mQ3w((>?AeAf}~hW3HG!M*so$NAava5c0cTn%oFwtySMt<X+zE4VBAG~5+_7VQf^3-?1`g!{n*&|Yva`mea09VP83LnwX_Eet;h7eVvEMd18s0XRQ=A6g8)4}JiB2z~&57_9_93|B_$!<FF%Xmhv$+yre4H-VpIj88J|a&TMbUCm#6Lh++^wBfVEO3U&yZCrWU;J3D;nH^2hdT>*?E?N<;3s*o(!xi9C=>2dhxF~urTok?s%?sZH-;EZ6?}iJaCE$W^aXUPARJEfD`UG4BZiKdk8^K<*3+#nEqdnoy@H6NO@H6o9Xn**5*k?yOJG$G^1APwe0ry6Iu#cbZO(^a|C?0^m01trsp*^F*=ak}S(JoQpb5L<tv}IKIoK@TkeIhD+jw^1AR*eep35wO8Q67C1tqNCVZXQJ+fggp-qQ&9j%xPIdv9oR!mqZJ}CE>zoUbrxv54{)82Nyu^hYP^P(9&=*_#w0+{199Ttp`_v>!Z!!`ml4ZD{X@|gO#?1m9~T1!0pi<a0m1$v<IxTH>|V|toC8GNB2cvj0*3;>a*I{d-2&}rRqA+jn57%Ro4x*AF93YJ~Tg^pU-OlE5c`om8$*kK|U*X_PZwNgYbiV--P3-Ygk9PBYjcN#p)S2za`Ja_t=q-&x-S+QE-0Rw?w^gOL(0XewJQGD2|Sj=itFn@_ei`8dj>>C|1wDHSHJ}CC5~KX@)k3o54xw8aN47&%#Poo*LvE0uQDigYeXGMxcY>L9|iaieuzsEbAF-e$=U#(pG3oxFzkK9Ifcz8hAZ@ti$mK!h_Igco008an)f=>*-T89L>+IA-Cd<wr;TF2&z7>Mib!G@LTA+@LTXW^fh=K{1Q45ehD6rz5$Pi-$rM_Z^Q9uA{-B=qFdlp_!ycAAA_%>U&GhoTj<a5Em$ourGLXJ6#s+wU+_Qh_vlyf_wZ5l2<+7QD0Nn!H=$p_Uy*AQ`ZxSHecOb74S&tpHlbVKE!1ceIt!jftv8_);fc)ICiGo+BbtD|3#)OgWh_dM!$;xo(H~tk`H`9_jfx7_Fp3&0y(=nQbH!>-l;(*F&ynKm=ufUW{fRkOdcw5^POwIlZneT|MsYkEXNA|8;<wT1R(MS+9*>T-!fROZOXz4Tyyg{;L&sR*b42l5=zpy6Ii+|t^;Gp;g|3EI(?;=3J0{riCZRYMeFu((52A<RgYcK=HTX;TPxLnYCwv+G4!#WUBNXf3WuxDq-&x^zxr+ZqZ(HH_y^6m@uUX-D!io=}hpq5?W5w^I?^xk?%ZewV6W~ek9CRi;2M!Q3>F+*t89Ec5Nv##Huw#ZD(+I`O(UtIWct4r}?}x9VC*iB`ALtM8A8-)Of`jm0LUB6%PiKD8@tyg~Vm`CT<;<_*FVT}$cs(dSh-O&f^`kfzU1^2a+e&J*l3F<Ha|U&rLG6~g>gcSW74&y6x)fajub|e7ci6Ghj&p?K&+PaDO+$CWY49RK@rURR_(OPs9Uq|E(H-!1_zZduJ_G+sDE<xo4E_zi;p*!RLh<i*+(a*-U%;2(U1%D-3to&af)~S63B|9YAHuK0Q_uzQ6nL_$7Ly6ZuiEhnIuHE-o(FG3x5L}u9P|vF1OI~l3jYFU6N*oxzrm;Bv*-=@EPNjQ9X=0#?yB|YgyIW!TtxpuZ^D1USI|rF6?iwg3*HScK^MbIU_Uw)_QRhLia$nQhd+itLZ`qV!3)vJ@IrV#`YJphp6i;+xrE~P2*ocGif5zq;MwqIbQ`=GK4nMuPEmP^-}OKJCqBdf)Zar`#((fL@+ZwdZ*u=+b30e)kDa=A%B$|XtvvSs)J6ER`VFM@-~1|{v;'

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
