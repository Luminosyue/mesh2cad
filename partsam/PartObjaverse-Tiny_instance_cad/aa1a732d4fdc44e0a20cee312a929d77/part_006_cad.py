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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_006.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_006.stl', 'source_sha256': '346b4ade86401d9271e769a30ce171941333a537289414113a64c14731502bb3', 'input_faces': 1304, 'input_vertices': 795, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18999764323234558, -0.18626345694065094, -0.42077118158340454], [0.180228129029274, 0.1697869747877121, 0.149697944521904]]}
GEOMETRY_BASE85 = 'c$}rZ2b2`W7d76~WF!a@1mwqH06{<n5dnpfC>calf-;09hlO2o8p)D_fQrbFlVn&jJG;P=;}Rr~B*|$J34&k0s#`_ZbN=W2&-d*)b?&YEUcaucu71_iT@CeXrAnQ{l79uQvZD*ON?*&esARHoSUsb<$F^@36;q;1bRUoPve4;I;pDoF>eO%Sv3gql3b&4mY1O@OId9>Q+k8~Gn7447uH9q1x9HNmYxmYsq*rUvDJII%W7@Tdj&ka6mnmDin734sV%`DX|I5FOP7^{W8tjU9FfjCR5~06*zr*n^J)E>b=%J-iN8Ea-`B<R`{+M*gty?M8WSr(TlHIy*{hb}c{#D0=Zavt2fY1Ze^B*<*?>^ry;?(?ozgrJ1eJJ$cgyBXzt+f}WKDv_8&T#6G(8IO&8SM=19wBt=<;RA<?~N#-2OgX>+7nvzscg?*d5t*1FRpA8{_o8(jyITYyU@eu`t38?xhNoX|N8p}4F7fMrGL9#$Bg#RP9yZtYvqjgc)uQ+D6siyvws@Z5_({KtG!128n+X~@l{=K#Ict25PEpu9b>=2L0=}w{(fS#-<NwyNa#CWHT(l-XA9k%_2)f?UcnZ+@1w>>9PhxM@xmUgaNOwULld?Nd&*ZveCt8n7NM6fY{u_cROnWnXU6e{avj?w^woYNzEyvr(8JAQjQF8J<u;0VUtBl)t!QSc56EilH+XE_deNS}?Tt9TI`2sR=oiL*1JMoE3Hvjz*`M1w#)<JTyP*-^yZ!81vE8xqW<L-AWsR_R$Y;b4XCEVU-`6vZ_<=*ESBv=X-7wC(|Hi{ra$MXq_8VTBM(9>!zd5enti4iTe4Ke+CZ1d&+LPGVyj~tIT`uA+YG#b{@SIsf4`sVx^t10=!cq}G=N;oZ^0r>{o3IZqYVLPfQK1KSk23N}==7Gw!oPnVBaZd(U7`D*yk;I((|L<Ty+v2!y7qS6zEHIH&0oyCx2&|#y;t5c@{h0JwFRO*sV|s%!Y-i)YWFw$C)0s>!arq-(LcUfY37RfNvq8EuUj}<*s~Wf^H{3!vxGk3n9)wF?b)Ef?Y7aLK=eSN`#-!T^(O0giu#pe;=1tlSZ(U{i%7lc215@tEiCm*OHKcRd4%rGyU5V3n2bUX?o2Rr@8UG_dMq~IjGz6sxbFPb=NWov`c<I^?<SgY_8*bg=|3UUf8KWK|IuPo|6hX8L)I2U58quc<K$Xy9@m~Yq5Dp)J1ocj3ZeVLe~LV5P5SPLq4(b-^QV84p$BSAllivVJwx|jsVDSct%AvJ-8=4Ykw3$jPj&p3CuRPe-qhT0kFi1zzSGa#uQx^HNq_m_hm82)qeAzM2^e~)=xU({XY@Dpz>;x754_#i(1W?&6?xA(dc)YS)grUd{g?kV^pN+C%!eOdFx%Pan9!}dr_DI$(~CUmJ)X(v|3GXdk>9+9svGU`En6+}Sh#2}Ll1veN9ew6OU>gAWEXnq{1u^li?^5k)9-|g_dNEnTesfbBKKds&k?uo%QHsyNAVaVj;~k+8E;>YWVarAct+kYjeB~)@bCDo(0!k_IBMv74~zSy;Kv{Dck96+g@x{GQ1Y13&V*QbKQnN{UbpVwF<0DI_>PASfA6d#;{G8tb?_b|e#~VtKE0jV9Cz#CxTj)#hK|kN?bZWz{u1NR|7?rte?PUD->u{~4F7P(+cKXlyJ+|aK76o2*oS8@{QY&$igDr{dED?1rQ8(rX6Wh{hJP^mx)>*+w9^cKt4VG-9$rdq9It=uCt_X;l`m}g`#Qfb=Be<9S&jbm4ZJ7jk-)0aX8*?)68Ycyw9`JLos9;FJnwI~$2`A9Yl=K?EzDw$hXwUT-VQ9jZj7J6oM|(Jz1HP}hF<RN>7ricFJpXK<7WOO{HxqC#%G||{vSnqVp7C7_fP#)_S?`+@;>>>2t&6#i{!X^tHKet9+)&-=-!y*LvGy{S5N4^)OQSjf2AVw{yciL8UM9c<$fELGW@N#GYLI3udoq6IOLHW&jl|VdMHPd(5+g>jX0s`)k61PoSba5f9?o*AHJ`e5yyYKzP!)3a~(9=6JJ{1&*$!9#>shF-k)deZ2JFvQtDX>9X0&hb{4wt%mX8iRlb?ft#;`S82X9Fa(?+a#?S-*%6TW;HfY2T{~aU!`$d`hr84q&!NlVGjW~5~%KQ1sOH4g(qP*TyKR4p|+BFoqwQZB3d+VMNc_374;y$DO?fVGbcPp<Mzf7#m59Q>2uWskS;zAFUd|>ul@~iT9f#)MLe#b0wzB{?p7+2mL8RUFdZ<nEmGyl6;#2Yx-&_io(3*EV2HFV#^Tbt!|vCG(R=!4Tz@6gwbpEE(|zU)uTIOpdIJ-E1)IsU7CBlNIU-_ZSyOUZV=UC<cM-bd+#?k(gq<23tS-d}AgVP2<0@jEE_1G7DyX5)8LBcuNVz8|Fj#7u^6WsH^gduz&=@%w%%<9uAg?9X52eV~7IdDDOP33-2YrI^`oNkMs^R=S+w?<><q-luJO&x~)?mG^t`>&)?RtRjBLy=9)S&1Hoio?+%0UyV~@-U-xt+sr>#mu-;t>Sn(^9V+xt^s9z{*yopV-fe7-!<L^2-P)Pj?1y&>3f<qli{T&0luqcubhpj(yW)YkzY0B1WuC7wDMAl7A8wAHQWu5pOF3$`zxYXcpZ0pt^go^~^&dBy=cV&*`8&5;ZF9egYu3r@=&I4r;S61*-nEIL`+jdH@9UnPGV@7F8li{w7BJ$6qRY$Q#oshG@`nHDR`L7SI(3v?j~Rs?xID>-Z>5b9_XB~ghYda0;EA{&2;59#<W+yA+VcMJl?ldveUop?-^FuFnC;(NMCidStxdgqI-y(d{AtF|{O$@l9)=paFIO?42XC%4=7sR^Tg!yL=7BN4_;v?`?vFle&PR9W$@`YM1x-Evq4*u`&A-Tq6L|MGp@#}hGUxHw3rj@3{t#o_1}{t&dU&tTi0{kZTIj*oN}J=hPk|-!dOd62Z!8)ney0aI_c8Vx_-L`bzk2?Ic|8vD3f)_~s5zdakBi^wq0wQX2a>AF`)qc<p>%$~p>%#<p>%$qpmjFyE1l23O6T*Y_Gj~*ZYP`9l+Nch9f!?pdcSP`QaYc%v_G4tbbqq>NVk*CJGy_^Jfi*CJfi*CJfhpl<`M1B<`LZwY#!0a#pV$mpUorscrRy=^Tq12X8*H%uG_=%wmx2#w{?7$pLIJ~e%AghKkNOnJgkq4<xd@-<ry7^<qhr6@_^Ra^{$VXUGKg}7v%H$y;;^&B>RQr--X|!Gg9AkWHssjIz_e#`=cXL-#tm_p~LY<<0I+4S00ep+aXhLQgLS_J<$D&WirkInHP5dEOg7V>k$U8WR|~Y*mD4-^XC9c=g$GO&YlA(oj(WA{_Ht`*4c9arSs<ix}EGffYNzB)c!0VzKCz;Lmh`bPf$9~lUiqaQui}^{-F2Eo<As^=T)t<=MuW#SiaTmVb3dc9F~W*&YolFeq;Gr9~aBdIu6Uvx}7XP>v6*Jv-W5CS)Uh{pY?v(^A_EHmbZ2Pu)MAPS>D$EEN|=fv%IbSS>D#|WO-X3FU#9HKFiy>A6VYj`(@9U^l`EKe0?5Sp4V|$p4V|$p4aVRd0rnE%k$cw<$0~M=U}=$EdT5NVb903&gKPu-LdCpT4(pk`gqy%G~G`2JWU@jn|E~k*}S9u+4DE8v-wEtY(CQMWb={sXV3ApKYNa+`;9%v({b2yJgu|mc=~wRb3CoH=Xkn3>^YwHXV39`59Isl(AZbDSEPPBGvS2T{=re1mnXH@L3$u|sXXr~o8|MYA2tcyd!~u-52UPu|5wt#YwS`}mvOAdo08mmVDb>DU#jRAe)q@7=W&xe$~YaeZzK$@J|^-wpO2Kz=Od-_`AF$}-qAXnca+ZO5vB9_Li@9MLAR6Tf2H&Muj8=%ulLLHztVaB*ZwU3>;7c<U$>LxdEGxO&uf2{=e0k}^SYfZ&uf2{=XF1@Jg<+7<#`>S<#~O)EYIuqvwW`43(M!aoh+a0I4qy*{jz+n+t2d3_GkHA@0aCmeY`9`>+#R>u--4rt2#c*tJ<ICPpz~3sr!NDPpix+ah>q@1xn}d3zW{^7bu;-FHkzq4>~@}4_asM3v@eK-cUM!U!ZmNzCgF1<r&>h_P#*3hrKV*aadl`{_K5$_Gj-4v_E@apmp}XK*wS43zW|Dq1M^^0v(6FFVH%BU!cz~%d1M~?+bMM+4}+=pS>^8?PU2``?L22IzG$Wx;-p!>-a2h>v6)~7wF?<`CR+6e6HiO_XRo*%kz4?S%c;C|4LcS@z35PXn!^@=;LMY5p*0jU+Dg1?-6u6*?R=-&*m2$pUp4YpUp42-`M=3{n`AY`;*Ntx}9u((ec^*qT9*dBWQp29zpjrn~(H<+4}_@pUqR+pS@qu$Hm?+=<~?tHQhh#{esrne5c#P<~!}r-Y@9mW%HnJKbr@&Kbr^jak2LcdcSOb)c)-Kg5EECzo2#Ye&I!)H|JU1PWFD`#r12xU(o%=-Y@8Rht1b7<~8&Ef^H{!zo2#YenIQ({eq6q-Y;l>cAud8lf7Ti{_OpNJ}>OPLhJ1Pg4Wsl1s$K=hv<G|?-#T`yFbzW|NnJ=!rm|F_OSO0Iu3ikp!dt(FL>*$lGhzyF9iKR>xH2IXT6Zp`FbJf|5-1j{P}tzrStVd(EqbuNVSu%7lQtu^+M`+`FbH0pRX5!{-5<i(EqbuNcr>iLQ3cBg;X5AUP!f{uNPAN$=3_1_Ve{Zs(<);Ar+sm7gGJt*9$3~uNPAB`FbJMPQG49#o_CPl+M=+ss7>Xg_O?M3#s<-^+L*@KWDhsLGG8WhtxV-52<v%9#ZLiJ*3k4dPp7ToLqk%j=6Twt%ufrF3)GaiKhPbWx0NGeGNnB>ne47#vYX8b5m>cxCX>ay>@3)&$US2$F7exb+$fJA6I;4=|3!&(H`%xLSp=f3qC$zwEspXp@-fWd&uYqw$4+>Ve33~9JbC=$6@O{wf~fca(=II+h{*u|EYAo{!_<c>p%5=+4@i2{>__&9tz(u$HU;Gavm>n*3hkeU&wjC+AX8~);nc|9$uef=;3Xz%XRo~JvIH;WS4qeDr21U^{BcZuKpwMAEs<G+7mkVvCzX8XBxV1s9et<S{GyJ;Wtxc{>fIrJTGj$tB%9gyXrV>y{m2yTkjg|-U`>9xei?GY#q4L`8sf=2dC$k_w8l3nsM0raHaG0;Y#Q0!}WgI`f#Q5_2EkQ9gx2Zyo=2^eBHQ?!`6*!ovj;JI$t-gkC(3-uR2-g7xulC()ssRO6T8ODV=|BrF8zimD2h5R@$F^Z>8JGzPHl*W#3!r_OtJ;bo<%&R(ikedn@hFzPHltXWv_Coqcbm+sVGS(*EpwE8Twfy_M4W_g1=p*!NaCKKtHEw}*XirTy9WR=R)K_f~qp?0YM%v+u2R``Pzax}VwiR=S<+dn+BEeQ%}Xu<xyO9QM7H_GjN)>3(3}TWOtrZ>9T(eQ%}P$-cMJ{_J}z-9PMmD;<Y@Z>7fx``$|Xv+u2x&cC<PaoG1(Iu85ZO7|!G-b(i;``${&XWv`teqi5Q>3(3}Tj~9>@2&KH+4ol3pM7tokBfb8rT5Fex6<+1_g1?7?0YM%v+u2R9QM7H_GjN)>Grelt#lmry_NQ7-&?&HhvxTIR`4e=&VtDq<0?{|>$gsc<DQXO>f^_67y9L;Cxw5e84tD+9xY_}D?K>=d-%^0{@#pP*H(-W$D3)o)Y*PR?<H@gy7f3p-tTo7zA2*KprmM@|NR?64?a95pL2GuxjB+<eeqEE`%1nPPkP|V4tf9CcJanYdZ5mi@;<0!J)v6<ipcm~&uxyVe>qCt_mvtg^{3ZloL2I=8rMTLhs*n^(szXJzc)bUt8Rt1MACg<9TD+;(+h-*_P6+OLqz?vbMijxm!?AZ-nl08Sahx}5%sSUMSN?<u#mf-E&uWLk#t|Rfih40njrMht?y+&c8%K{Ne?w@Df8T~*Fx^|5@?>ZKB8W&yNK_fnLk0a^H!9M(<%GrNV>1#R(U@=vuuKKUi?`$MACiLH;VY);5P|I``cIA6j85#Ta1Tbuyca@yaZbQx*?Jts!?;b)cYj3``K#KW@98hP&>OEZ^7?`?n~EJ&ey%4%lUBDSm~d(0N#Tn%6vL2LAEpXZh1dg;T<{O&OR&KlYWu(@AkPopL4P$igA)EM&1urtS7gdQ%2}k`k&<Q<*v)*d6?Td(H-Agv2rMq?u#lZ&(GW*LigK6;9p(FpW7?Z-F|PyG7<Ga>s%Y%x@sr)SGw}|&6}1e`>nlvpIISWD3b1Lbzp;ASMB8fN>~2jc{|Mh>9;CAk{)Q$#Pm;fKR%*Abmi}zf7;Y5<d(-f|Cwxm`X%zcYwx1*k#u#PDm`Eyh>zs2bmbqOpK6=C|9zb+$n(CS)HdU|dd}Y(Ne_MV`FcZF?dSf`mA|#H;Wqd933M4Quj_>^wz<!j)#Jmh5%p#l*12_czPP{E;U8Ss!)TAyYomOgvG6;yA7Za>iKK^`OkL;J)i~t-N>~2YqG5&}h|UZD(Plry9Ehwp>5DiMjpGW%oRjy(i>4X=p(@Med0RA3>S;ff$5my9p@(gG{VUzO_^^zRyb-M2-q1t#k$6L2BG>T*teWz?SIQ&z^ILPFhccv*?|(nt6f*RG^TfOL;L@c+_h+~z+gGu<q3ih21IzAgcelr1A*+nPJl_uEc>Bf0yLElM(EZDc>~Qy+ukSc{d@BYRx>c+4wn%!gLLO;fIo8;(RqOq2k#ui`G={%w5BFEP@(-_EXY4mr<5^-vz3+V4Pb)X<aG%Feji-qb^}e$Wf7PGdU+eG>uiUo7xGrkkNsOdheMcGo`nq8LN>~2ARe$U-uJ;<d6C>%qJ{1gqeZ4b(ozLMPT=jH^d%T4{TbdY2_w}|7e>D!dztWX|cvZF}(p8@HeKs*Mk{;@HV5^}cFa5_~<xluqYpN%?uP<NqdWn(rK#!V+znU+&ztXwCnlHG&(z(C7uK&{>=*mC5W{}xG)iNhW(yf@pErzc8hx@C14u9|3DM{}0XjQwH5J~rSA7}Wh^T_@6`GtRA?b0M;99G48CZ?<VE~Tq+7^s?@5K&k6X>t3LjOz>eoa<I}TEkyoU(8=$U-0+E9h3W2_lH&HBt+7E(f2pIb(IIWztUg$pOCtmzpBhih@@N5Sf3K-*(r47$x!9a36XSlpP+P=C%M1UmA`jgww><%1}isBh@^))x7-|G-}qOw;#zF^Ecl7DiBmFIIjlA<T>pd?iS(y1@;{-~{)7Kt|Af~2rQZAC|Lxz<%DB*J!+fVS0)7F$*(r2<kAY9YXF6rLQ?3HT;J-NKN2go?UIyQYSdV~@!N14$b%AwUd?xCIpMxKC$`Pl01N;_zu~X<6z63S`r#QpVKEm_h)V3ecKEg{bz5sQ?Ti~?qNNi8|2lxVP(-7DId_9i239u<RwfQ*OP1qcK8IIvA;FsVbr<`=kKfqKT$yZ>T6yQB@YTIbEkMIIGZF>sa6Q=e^PHmomb`#bIkHaxE1~vgdj#$lseisj+PS^~5725h2Fa@02HV*A0yy)WdP$#?zPHjGcb`#nj$*Ij_(Qd+e;A?RVUjrM1e-FQ*z)|4CVH*q_3O)?B?|_5BN5VD)_#HTv5wMR0SI0^?1~>wI5^NKJW5B6QfqfGARNznGQ^9|B%52~a;7{PIVOs;70lp2k?Z7qQJ7L=e+z!4Mwtc`|;0Iwl1l$LH1h!+qL*U0@I}JPreiF8`z|-KTU^@pq3w{E&Gr)7;M`8ONcn171Y{|gi!S};<0GJHE8@4^b1K>MgO9Jiz-vV1AFbVuO*p>hj!GD2mI&ca2kFZSxP6z)1w#mS0;1ggQ51b4>7Pe8q@!+GtGXt}^_+-=xbGZ04)CqID_;l0>^SSsE)Cmi?cp~bAue*2>>V$<{d=Kh`MO^#<>V(BzJQ;Pu_gwsU)Co(u_!-m*KXmbPs1ttV;%8AOEaT#*Q70_z;>S=YEa~EhP$w+m;`>l1e8<Iip-%X=i*HAr@J$zAgF2zt#b=;SnBT>JLY**=i%&tFFqex@M4d3Zi;qE_FsqA?K%Fp?iw{AaFoTPKhdN<87axo|VR{!IiaKFN7axT>VP<eb8rNxnFS&RQ)Cpg9@!Y5r=5+CVs1xRO@dBt5{?El<N1gBu7cYc5VPO|9f;wR_7cY)F;rlNB9_oZ;UAz?PgymiQL(~aBaq*8(C#>k=Wl$%q;NqoGC;ZsOOQKF#&c#chPWXX~zk@pAyDt7V>V!pI{7uve-*Ry;>VySdJU{A$ueo?0)Cpg8@m#1AzT)E9Q76pe;#pBAOzYyAP$x|7;u%mUv|T(M>V%eyr$?R8<Kh`nCrstynNcT915RVQ9qNQ_z-df(fV~53#A!@-g1r-L#A!@-fxQcC#A!@N!yXMAaT?RzVebwbaT?RHu*bqioW^ud*n7f8oW^u-*n7i9oW^ut*!#jpoW^v2*!#mqoW}G(*ayN!T>fU4_5f_eX-p4-eGqKKX-p4*eE@94X-xNny&r7EX-xNly$@`}X-xNmy%%i6X-xNky$5W>X-vn!9s?V38q?ii?*<!j8q-~2?+P1n8q=L&?+hDp8q*zN?+6=l8q@7zZx0)B8q;lIZwni78q-m*N5Mv%#&j##Tfs)0{#wA^0yg3_rdz_^5;ppyG2I&W*02$$G2I6CHn0(=-)!`ID5pnaZja=I-+&V~1t)9<ejeL}Em?@?f~^_&RoLEyA8BvG)(o7mH8{250@^{C2W=tz7W`YZN%>raA7Nhj5;g~Kj%}3BP52SM4PU}`;O(%D^0@&&!ou(+Yzy8N+bExF@FRQ+zJyWWQP@WL{0Tq8H{eUy3cMAzQ9f7UcNP8m2Kufwcx!A!yt`A{IHi<R9$FHwTe1)@1X~;MXO{du{jo=4d5`3TeZUF(dS3XXf}OAiIN^8T-(ef&lNxryn&5<k!3Sd-<zvH6_!&5106c(gl#d5?!fN1zgTM!28|7ocPFNM3a3J_VY@>YWIZahy8Tb<R0Plfql+R=M5q<<;!k*wgv5oS13O~Yf@FnaG-W%H}pJ(uUhVxbq=cX@sUu;ACzT@-2DernDzVDHoFdCe&i|2*U6ZjF9g)d<*@Lt$P`P_jYVKMj;b_DN;ZIsUy_z@O_FJVjYme@x5T!tTE0r(QO0B?b9l+Pvj5$1<4p&#6jZIsU~_z@O?FJXJ|_Si=G+=d_FJMbm!0Nw%HD4)CVBP<SI!cO3wu#NJ$55N03Z^dzLx`21VHpH_!B^&h<@G5v_*e(IDfM<g3BJdJ;7T7KWFM_`e+n>P8;51*6tu5v>;@MG%UjzOLo&&ZUz-!?7V7mpp0Z#KO*=XMF4E{e9;&*_zz+Z>$9`Fu$Y1mSL_rNQ{_7^Y(yfSQm1OEcA4%=hk-{7@jdkTCEUKh4!z^CB#Vfz>O44m$d$VT^1gTOyWA?~py{tHe%WD8ib5O0V=+_oi>FYyMj(al6d*ooKkNZWHDX~gSzr0pNzbMRWQJpuj$UIn&Cz$f5ze@ZsGe~ktI6ovRh;3IJIAsgKXcL)Cjh4=&DL-3-o-3LAZ_ri7;cpv;V*lq*wg1-veP2g?tS75siya}ESwyVJF;56qx$6QNT!6SKhU_W35aPs*VeuO@kjj%t^2i_li0I(AH0PtAghv2c`F~ASN|F-0FXsQ#IblC{I0ZW3DPYV19-*edry8_<>C!c%pBP`*v5q1Wa0KbQO6si*za@h#m01JUrzW>!D=Ly2);B>s3&>w^cUHx+q{YSVLoaV|M9ywnUZUgU#n7x1r;B+51&m-^u2p53&N6db}o#1pIv>p4|j(zk+EQ%QoTmw$`eY3Hj+1N*0#G;tpfpOq;-xtJoL2MHRTO9g|a4tB_GrxJ{{6x4IobDlKA>J&+YK3j);ye(p1gH6D1>&thEaG%uv(+Q-hX{{>4+I|s{2iR;vQ>z;3bBaOINX5qxdG=g7TeIa0pMxyX!Kzh;3{w$pKB3sEn*Q*?c}-94yFN)2hVQHbNUK!5qKe6j+_4hH-YE2<^Em+CV*2Ro*%dyJd0BnIy^IQK6pW=Bs%<c;C67@hPHhJxF0;LEzeyR;6iY(Q{p``9$_LlZA06>2|Ns*%a-Rf8*nZ-72+=ge*rJxlr0{)AHsNWibXNs0v-d;<diuMe+f7XoMKVTjKCkksZXhI3jnu(Q!I*^54aVa`i}ZA6L1bV#iE!QfIom!A)X#M0sK{`toO+CxgKMPIN8W2J8%Jber)p^FgG~$a~|09z?L8VlNa{9u)Trf$_INs*oYUwm?#Q-9lQ|ws4(;*IOl|KgL}aX01JZ`#<m5}|2c7<b7CB1L%-#KJqK(rqu*YE{T0|UqJOf(o*g#gsd4U80bc@7hq0R$m<2p7cp6}4@HF75ftkQdI%TzUF5U;O1TXEBjSepZ+zd{I#!OjY2%NTA;_!EYi@>SSxh@Wz2Tt2i4*v+a9lRLEUkTtsa4N*#11<)qSd^>Z0S3V-7G1L+0^`BSM%PX;;2dy@MLDw+a1}UhL)Xs-zzyJ3h?fMe1*dIj%$EkP2d6QU?2+S+@E|yyXX>jQz$M@`chVf%6Bq)gXFel6a-JE9JV2a&hyCo4^Eu(K;61Tz58zgC8bh>wYT#(_m(VY%fFr?a{2%wo;~-21&w=xu6Sx$do_CEvdq*G+ar*r?744mhwi0iTbLt091*hj#qdYR+D8wR8<DY!80vChl!??@~+zd|F^(l`$4#MN$)K+S9F5pUVdX93|Bkw!TVtf+s44<yR)!_7;Y%JP47HuU?&sWZQWV~~TMVzkFNjQ#4I9}q^R%&w|;6`xDS+s2t;3;s*XVkW$z_Z|8(Y9{Dwczx8ZUWjn0c|Bt_g)KNUjQ3%x+ge|<2a3DAWr#YJdT5K5_lfui&uf`!N+){-*Dh)@ZsP?fg{0(f)4?X03QNA3^)pW82I<VvEbi>j{{Bs9|t}e_yhQ4@M*vw!KZ;w2mS&+9egHmF8ECFb-+0Ab>O>zJHdB>?*r}y-v@pOco6&$_)%ao_)+kaz~kU2!OsIvfu9He19%qv5AX}XbKn=i!@$$vVem7+-@(s-p8y^MKLLIOco_T$_yOR4@B`p`fV;u>fF}VHz>~n20hfa>1D^r>6?_KxPr#qSe*&KZoC-b#d?IiX_(bqA!13U<Y-y_w90Ok0ma%F9CxSPy<-Y3zr+_!IWm_8ne*$l8%VTQ<oB`g<mVMC}xD4EH%f4#{OagCZ%f9vl_kg#x<+*7EJOJLomgll9@CbNkTb}z4z!Tunwj3*+foH(G+j4A01H<6mY&jOY122GgwdL6D2K)oOlP$-3SKxW@cDB4WIss3DN7?dPY6m<D-qM!WUKH>U__wyaR$Bu1fj6<`wf!w{7x-7U%mqz=>%be@GIx9hoC#jvmbs=Oa5{KxTjr+vz-iz$Y?;ey11E!5vt{n90UQTj*_OGo8t{AYPi>i7D+7mtSF&X;{uDR_yoxPzcO~FZ@ao9*Re;06>tRgS1l9%r0%N)!umSkj7}H+>8-ag=G5s~LF?b7%>2H9|z}sL<w*dOVJ7P??0k#5<!I<s{Yzy84V>$-d0lXK+bPr%>@IDyRy@1i+?J?%MK<|SwPS_i~8+cb>Pw=kboq)06oxs}xyMTAWzKFNB<v48*i~?_N%W>Ko*b=;{Eyrnd;J4sk+H#yW1vUZy+?M0?OW;@Fb!<6KKL<7h|IC)-v<|R7xX+g3^fO>>@CvpZr#@f}@Q-adPAdSbftR!8IQ<w{8Jxx(jlHVCTHsZ|D*~&7R|NkAaVTyjV0rLL;8lR1fPaE*iPJMpdbUaN2&>vJ_)XLaYuYdPZPW?t*)RBA)CuXDQ2ajXgmg_P{s47Cx+WBVh&mx%6N*1Vosg~x#h;)~NY{ko|DaAt*M#EFQ75EpLUDRFPIbawE^ebv*vG{^s1x>fae9W|8`#r+!JnZ{NY{hnPf;hNYeVtJs1wpPq4?jZ6Vf%I_+O|K(lw!Y3hIP(O(=d3bwau(6u*NyAzc%S-$I>`t_j6&piW5FgyPpwC!}ja@jp=~q-#R)%cv95HKF)L)CtSkFZd<Y3Cr6r_!ZO%Ke1o%tEgYacqdM4%d1*)O**XuuW8Bk?2Dn(T6<d0U)z%32hg_zl`Xk;J05z1Q|36Ol2d|~Tpv#Vb2xqXPwVHaIAxJjex>LCmR#?@$tg9QvH>>oS&BO8>zp!+-j6tCu2YsfrMgpAT5`>KHA}8Hr*+_;S#k|H{qCdRiuBBbexuRvOnNRt+7jsWTbq8j({m2`T~EKM=vfG9JD}6E5PD`o&oJn>8$G9>=N9x^mYxICGYNX0LBGT4xdlDLpyzn>OoHqy;6vIb==3~;o}17!4SI$_&micT1pWS_-+}auf_{_HZ!>x>@g?O9r!)el0dEAJ9));1r+np<3{J@i{x#}pozlc9F992a_jC3!z$tx!{lWXAJ_tAvd_5hHQ&s~L!B>MX2kr!44!#7q2Yd<meBci7`QVFyA@D`uOM#ofmx8ZEAs*+H4NlqWlr<>CR{*zx6Yc_E0sb3sFZgfZ3xG-B3&0lx6TlaPF9U7{CtL--3iWkP`N1haI%NV1@iD+(z{h}(1pW#>5_~A|XYirm0pL{d0Qg|wB=EuD!-3<#hl7uD$`q&k<dlgh#K!_>fR6?L9yk;Hd+=ev>EOe_zXMJK{|<Zza5DH1@DafA;3L3CqtDZ)lKo3)fz#MXvE_Inya7(*?GIayN5X61v<+>$4)_G;Ybmx}1pE_x3ASAhyai6%Ji$39d;q=(+s+660lpmDt_J=Ez6#qe1KtFuad^R&<CO3^_-bss9{3b|8Ma*vybAsswp{_d4Za@RZUK5yNxm4{E&yHtUx97c03U*H!M2IO4B%_vvjO-IIN8W&ConVk2Ka0R+NmTb8~N-3z5>1#KHGp9!O2EGJAf~NlZ||K0keRUjeJ7Dbl_wopS{2w;AA78O~8L`$;n1ONx)3tWFwzA;A8Of7*D5xe}G@c_&5)|27V9c`!etr_%ocpd%(ZI)1;E;;~CD&Q}|M!lPw$0l?V0QI2YM~8Nl<P&vOGagXcuw<^jF}o)vwV6ZjH%D)d!WU^@8zjXoj!WAqX6JGQ)@{{}t=zi7+r^A0ct{H!gnw~N3V;HS~IXMul$hjBfe0bT&Vg7F;&UI)LAaeM`M8~i!O>wVxu@U*GqxO|TB`44=vW2~kH+TgEZOlAjW1ka1H_bM<8crJ{wyucjbFQ=0EF&8iscxvR#mx1ZQAK5a0rA98a;Ct7W`REbw3HT*j=9jy`2jJ&ynJ+E@Z-Spe-<|_r1*bV^wk_u<!dc*i2b>ZF9s=L*l!G{*2XRdhU+9#>PMHfl2u}0qZd=Zug!{k`!tXrrGC0kTYi&6%u0>qpaTt3mfhpj$?GbEGcn^GzQ<9xB4|oime2&78@EQ1Q9NR450q|eZ=AVJv!D-v$*q$&AuJMgd`Q0h;z*FFJ(buEEXQNKrp1}5m*^meJLEjEM4*mo7@gp!EoP17Vd&1nv8*6dQ3xS8hN1~6$0Ox_9M4M@Q!aT?`b8*gQ1NYl6#trpT02l;6h2y8~33DPZ)vx8TbEJClad+9#1zV+ee#B78WWD&K_b$#a*QoBX?eVoY-_ran+`VNrCzk$5ynd}Tv`*gneQnFd`t((*^?v}QWRR!'

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
