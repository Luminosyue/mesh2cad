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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4017fc4184ef4c2782a0231113258a17/part_006.stl', 'relative_path': '4017fc4184ef4c2782a0231113258a17/part_006.stl', 'source_sha256': 'ff425a5a26d52c6f5ab26690fdc5b222ac5ce4aa4378ce7f30d36af42e562c35', 'input_faces': 744, 'input_vertices': 661, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08576394617557526, -0.2561507821083069, -0.24035689234733582], [0.15504086017608643, 0.03187155723571777, 0.3247852623462677]]}
GEOMETRY_BASE85 = 'c$}r32XGWeyR}CkG8infNh6VSPBvjo&Pe2}MIaG{Kx9l9axhU~vc!_X5=jUNgn$8&L0}t94hzPB0b`O)GH})JIm^HE)qksQ-HWU1JbTpJ)AM$io}SsVf6KJqxitLq)lRwc6&_Ph(^Sf;<<dq4hmRQ0CwO>;Aw$P{X*tAK|J=H`O~=;$UA?qX+IJ=U1`qEOUh-?bWSx*&CClk0L&CyGg!dj27#7|)SouwQ4;~(z>JRVVduVX#=TbFlR4%7iEnQBZp#LxbWlpVv;e55{P^!AVU2<Njwkq>krOto95Z@VC;wSMp<~pI&Dls`u^h0U!t?qlz$lsTj7vFKHI`SvomHg(&4ZEeBnvKLaKGj41e(?3P*W|d?4;AIOrvE(nt8R#IbZvKB@~4?AzHz)S%9;7>l=!8>#dpN#hrhwZajOp%-`da|_3@29DSvPId#q@?N~r&yGg2RG+hXyZ6-vRcTvPHp%1;#Eip+CP%87V)*5<dpoZ{)5wXf}x&p*X&mCt9piLd>50Dj?2lHa)PLjH}j#dq9nAm?jlFLF%s9hht@M|(G4zGn>%f&XsycFBLOE7~h<UHBVsZxEfZ0QG8LRD5Uu28d6F;&Q%b0DP@b2RSe6XVl9I@e|*=_NVwp&c{-|RSdp4zb4`no=@U$9QH-|*AJi_%k{u{1;Ka6-<a`S@;l1GH>Vd6-;A9oan`<o?`{`kG}|RD{eid8KV37VeO)<qdmQ3$zOLTsQGSnLoPVaw@SEM+DgA28K=iBZ)umq<7tZap#qDA;;$iI--+UE~<99}!jVv3HKjBNKeEx~;(l6YWU#pDzIIa)aY3mQk3xBGw>XWAv@?Xk{c26oK?XJhQK>iD}q(0WoPv=#BGkrDq^Z!^Q=d(5LocO*~ZN9ef5ZcYB6#T?SG7ii^=!fQoqVT5;SRw89>y#8#j&<D6=4<cf;k?q(ui?b^N4`gYcu)ZT5B;~vXTP#Pt8$Fc-0(*}K))Sc82*s#@Q0V%B<C55IG8Q7!rwV%t;Flq20357b{hCsGfVxoT8wk{e|N~|E*%!h=L{FmsQiw7@8F+4x>Ecsozad9?Y`NmrNm9U{1*P~1u>!@X8&yS(`||N^j#r$;XkajS;~pJEA=;q-Vom^R1EzpS0cu5g)_)MKX#qyu-cN}S#lfvUly;H{EhO<`C1>Az^@m!Mauu7xg1vyT?Bvb`5ox5Wf0HJ^X0SiPC*<u?@P4Lr5VUS{@8latc&EhTK%c;y{|`zo?UxZj$7UCTR+5Lep?*8!?RyG_kWanx(WrL9&zO`4-87ieA2HT^5^%L@o1g5q@HHknmauEgK-wVV_y#VWm|0&|4AXlf8KNXzE*JF5-GPH#*x+LiOtu$PL+PEeTc;PuRcbuKiW5(Z!=?FFuZ@k^`<Q5TkGpE<nK@q*RjXw=Z>+#+dap%Ycl$$V^&}Ijq)v%??q#LIr9YC{h1h#&Zw^NIWK7ufxk$cgZ%LMhCWk{Yvq@I>-zVZj34*BVMQK8yN6xCxXODB?fWmz%Te-(_>S21xE>8GEcG|5j1b?*-4XG+R2$csZ1A-a$D*X%eugFO5;Pp;l(>R&yl~xdZ3ss>SC(V^bc;J8=NmB;<#brQRL;k7SMpoIVW@wRt&-o|^+&S!$wS0<&fPA)e$6~A-+$g6<@mpvEyuZ4AN}xZYkM5tB5sa7zR2%W3G;6oT&G;6w_@A|J^VpF54ewUG;V#2XE|ECcPOXzbmVsyo+o+}^PX01s?9fFpg%a@*MQ&Y)*kc=#NVi$5&pW9@cUz4GKZa$`NE7ijrC3g)ZhGg0Q1PJDhnkJ;R(`DtaV8?-%5KF?clu^ewQBO#J_>-wUsH(?q@9^{l~g9j`P$w%=1UzqQ7knKz){smhT%c-bnpjx4uFCN<$_}eO}+h{8{^Jo3F+GA>VV<fN!2EiFMi6VHc#|zDfE~@@d9oDL*0}@%d%H%{Sws(Z1E<;Kz7L+|2ciPnS{Rn`5?PJXS<|nKfI(AMP!_^N-bXT;qOalyi2<RMBpTztM>PjFJgb&J@H=-%`$&->f@L+TC@|kM)eIB;U_;|CE#;@jI^5KYuCZm~C<0cO5!~>shJV5pq8I0a-toANs)eK0QNp{Sox{q#*c4L=P!{<5!6DxImk)wJd@5`LYW94MSv{nnfPTI5Gn7%k@CZu_03G_XO(%t;~AyjV84)|CY^&ez;>D@?Uu-<v7meJt*a6qu=2Z%0D>bu$;%7wJ3-4hEX>J^G6VTM_4H4fvu>Ix!sBD)2yh|Qr_ZQ5+8jdeAmKRlHZXQ<K6AM&&%x_L)X~qsrzo*FWL;gxo<Mo>o;3t-b;#tf4T_f@tQSJ&)6tiIj$Pt%KT>Ku=~arKOT|s9ukT3at@Muy1MR>`OSQ=8gcMWkaeorWDU;iD10q0K+17WX=RCTt%C2$JW%>)N^|Mw&T-3azM*$S{d<mqpKpScV|j1Jahv3YUngRPw2OZ|tV<KJz<;)Np45MNZ&~;11u`NIkITo)-=A{4H#m)TNya&QB`zP)|DBtTiLcethf6&U<GShEl5F#}n;1v>iT&^oWs1l6TY_<SE&=|~tivRZ2XOyoE{e1H`i$RY99at|!Y}DB^)b(I{ruj6dPe+?`_AVTE=s>}!8cy!!??<F5!da1|CRNkwq^TR`Fjzp&&|a5@ORehC-p0h@n!UUWAn8)#V~&^JqkbLN{PRA-&^{#>q4^4H`k$`JNGYv-zD+~@ppYdy=r|2f9NQO9B=bWDc|Kg2L7}y=x<?#F;2rr*z#MqA4omTkv;AC_a4CYv{!fWjk)3S*?f8g<NH!4<R4LBrhGqR>67xkUz)*Ra%YBoc9oZLqrdnK>#DB<Wt>{0pJUvdye7U@`q@4y_hq>J-N<kS{*v!epM^DX-H+b@-!(Tt;-)8HK3^LFKV7iQlloTn!`4mUUokL$RzUx;-oBOl88cgc%+I^g?$)xC8$6He%E5KQm4omfez98e#e9$W$LxiFGHROC=fr!QZ@?a#Z<?<qKBiR`zByUuZKK+}6H?w8U-*6Ra-MvaEXSXh7xg@I5ph|8^_4avr}#$oJ=k|}UBx=HV-A$#cNp>fwKnGSwb?h=+IKa^yD{!L*5$_E1Ed~R{Ux5pKTmDG)~7q#YsXLUn-yH6d}lqZ->htQU(2&q<~OtHdGYnG-Eki{73(+c{yF4t6meAQd3785l@I;1*`yqYZ=-!uekS_bs?qYf0<Kf$%M|!AWf0E~7jQrR7`}Vn*4`|@b+bc?y`Dqz%k@Zmb#}eycsC}dM?80*wdFVFkCf|_Q3<|#{x?H$e{Y1G5#RaXJFLsoOqTv*C7iaMm*#UbUUUcjE8Wpv@tBva+^22FwXE%OJu<VOw#C7jh<V2P<rMrh<uJ~(;y%M#Nxxnj?3X#4;=H0l;6HgfTgnaDfa}{z`uDQTk#Zv=(Qn@c!yo(&t_!cqV_&OeANU3Rrbt|hT$28%XSMt0t}`+ZJ6hew{pajfG7meREynsS<yZK*J}i^`Evm}6FpI1e-%LtOl={E8g>mpE0{-%fxW0_U_%+flLOBmFpr6n6IVQTaH+=VeJCE1>{`KK+@xgWB^-0YCr&g~;zlldVc^{yhu@m9PZN~hzzZb4MhTYdDwUhI8j;ss6OIzvZ*0F==w`;G<eVtayf$_dH?znvKn@ITe(<Gw(F)p-TtKsKrutdtO?1gqo6Cl31Zr=eppRD7s4vKD${8QQ|iQi}p{9E_1FSF!tnU`Eyd{0X|Z@OXgwRPnrzdkHUe4}+M%rl1`qQ4(K8YQ1+o|N-4IzPlb^C=1bzq@eX_049SuU7zku79-aE#-V&_nO1+TY06_<LOw;hxgt`Vq7=HJW%Jh%!kGW`W#0_THN0mZRl?ZSS0=ir^Lsx;9aEWcyyITyPE^vB7d#gQjY0+UB;uC^$q+&d1X9m^SK^)`r4LXAF@-%qvOYa;3t(qJ-@(u&kXt7mf!jv^P!a<{^xmSY7NBG@0IO*wFBt4+L!eAWB<sUg7x8NpVy1ee%uS&aSfjlaZ=y;&&4;3Hj(qP?qb|&L!aC7yR61C-)iNa+0M%uhIPBkhkl-iGG1KOPf2{VhfnSCS%CGt(SbhaA7kTath=tp!~ePIeyLA39rIO#D)3LnVm|4Y75&Pm4E#4~W{JP=w2Uu3T@l3d$0*ESVW%*^IWx<CmUize^v`>z(GRy>UgbGnw5BUCE|#_u-@PwkY<wa8)2jKC?9*xGUSZu;ro8kkXYO@!pKtEGgLyj=>k8+j&axk56lsV4zh)QKW6j}PAx$ywMAg8!-rh-ktyCxU6W?%YFK2)HygzbeNQe2bCjG3#<$9;DeJu5{s&ri9*?){7P0^0oI$+-_%MP^rKFn{fr|oU|wL-iOMz^#1Rxqx2=1lq-e_bX1i72U$V?+SX_wG2XC;pwt=PB^De8bTn>fVy^YjzB<*E0>)w^~tu_;V*?JmzXD@i)JO?>amK`w?YvJ$1ZkYm1xdlO<L(u8qyt58uFbwl@8OK61aLZG9x|ZVqj2Ki@E1XSE*iKlhW+->`1=b?5&R_n&ETU*Ig)%6?wixh`_Hgr6&eT-RJz128Y`Y5{+BU(|mO?g!1#=8W?~jK{e-F%R^BZ~PF1``=iuqv(HLC%FC5F^i>sKDRKBWvzkhWAV2O<n!PXxV~i0fbrX=_&l4x3ci(88v6)o-%B~Jl<LUeGkChK{y$xlI9nk>({1rDgn81aO~3v_jEnb(n{_MDmf!U|;--c7obK6ww7Dxb%5i@0Hr+OkGS|hv%6a(O!&9iw63m~jZSdXmzZQ*o((SvC>-Md&-E7A-iZ|LJ<)wpfOm2hzx+WIm`gvzt9E`)mW&CObJKB6#80J;|Zadp?orO8C?tpLBx*&0O`f^@9+h)4w_%c^a#raNXZL6nsddQDbP9OT?qi|l?aNTq^_>cTmc-{QFg+0!>GRZj7ZnUt))3}H6XeGioMy<wrzB|`ZRhmz?jjwwzFt1kp)gN)_fO&Ew<{vH3MSstJt|cv;E86OUzh~UEv-vPDT|Q*XZ_GX66hD3|{5LVkUzYPpu`Td9pE!$$OMJA^KZtKFOThKCJ?0bb_r<pS=HbkUL%%_``dEcIKU^9hzIk#C=G8k`CupTR``hAtzdri&gbud)o7Z2+e4y1gY`%VGwe<7U3y!@$r3~qZTH!L{I~qq}U++4{JAHS4w{ONqPL%I^b(ib4-VFW9@>^+&pEnfO@lmM18D42}eUJX*D(*ymPF8^*j{QXQ0@oXEfAD_P)9pX6Y4f!%`A1;9)`HJ^YDF+EjEJvozB46{w7c<uzPo+*MoK?1!s^=UX`VSP{lR!$-{xDTFfNR$27JdAl+&I4e}4n<9i1;>UY*MR+@rC*{v{h@e!SPzUZ1Fi;ZpvGrndS!4(^bCVhw6x&wuw3+I@NpTYfVh^PX}0k*sgD0;6SLLd%TyGE3Ev`!Vf)6!t4>vA-?7F21=kPJBlXm#jndYeQrmtT`LXzM1nd#+_NDP6W#FLcH2@AGJ?i@m*t{W1bw(aWNGB=eW&!gZqlOdUij$1D;oS8}QkmtrYB|8WrhtKG8-*OWgF~-$vN_&$8!;PyR;YJI~+4eRNv(EBc!M-{>dw%>j+=^;z6xx%k_f*pKV@g#E?DCboK-2b)MgbUbfrtB-bkp7b~UV^dpxBNX$Jqk8iQ&-S&>9hbOTEi*0_zf^UJzx87=wAal#^1Mnrb3&dYm{ZX%#`Httn;*ZDeMn0SK>jYJaX-AiwfM&FN7%nw#{1-53-LT!V?X&2vRpJ@O(|b*f#Vvj`pJE}`?<e!E9c>MhTM03e$F+Leuh%A&ink_umsERFnyJ0Ia&z!&8i++<ynr=h4V?+omHOgrFCp0?UH%}vdVLuYUjAm^N9YH`|#)7LwkAOv*mY=$NXSkybphQUWvOo7312>_fUMJS2{eejNv|B@rSnhn9cr1f8O?Jm978G|6cm1x$lwfxQ<Yc>!nY{*PnmFypbjz>j(N;uN>$H^v(73IqtOer?D?-{I%LM&c<uTv&Z^K&p4ZYxW6!O--hosTIy{TO~iBR2H2-?mt(nbe`ob?g!6gS828x^@Vs7|)f;{bAMDE>?}q1GF&p4#O~Ui>6g>ZOF3p2_`>d3G9qZxmC?}mC{6>G_xbxpje%Dt;;p-Lf+@Rn0D8Exl_~Tp3{h7mcN}g-$ZMvfUf<o|~MTxDFU+d5x`IEZKK8>|;q8!(%I3E7BU$8%&u{id7$IpWQaWS6XCY-eU(SgyPzF9vKe%}>xpJ&Vs!gKZmo8XsTB>OjdJG@V#??`ak;?`oH_|7p`ot|;i_3kMD@LgMcw3dSr&+UK1A2CDTZ*iG_;(dnFh1ZJjcTo0S%xp{Wo<_`I_^qDH^L=YSp4%GZPr(0}B=@8G{`vAe#XMAQo%rte2Rc8&^XR~2`0n{?JmzO@;4$&djk#sK=;b)y(${j7kovlPGx4~s95WR2r@r+h{5Iv$|EJ*kVuhTtm2cjdB;(Qf7QTDFby(Pk(R$=q?^%ES9iLNgEeAi(*roFQ3~lk8>&;7Be#dG&S8{IcwL$!9)g^BF*z|bbaqtNIv6&^m^Gr`E$E=<f>z%k1ybsgHf&JCOwcyuyCjCU;y%_suYx}{k=Z*K5ZsK{9V{rXV^7lzP-b1^M^_a1&=O)j3S}*QlpRoOPTYlXa^ObdC>1N5#`NW99{N^06Y_l!S7nwiH^39&@rM<6sP>!3AKCgpTDE6O?M7!@Oi22QVbS3;tg{2%v53VOeR@uv+-cr{4j<@vLj(Qm8b4SM2wsNfQ$7H|98Pa!)XB^D>=dh2_H`iA2`Tm>H=kJqf@A~3fPl`)?oK0|Ctz!e5Z$xr`ZwuG^?l^a>hH_3k{L!;~*Us*EZdKMlMttsHY2&WoI&z{vd|nr<4(|2F0QgI*;J6d;9QL!%c5(aKr~$TeT%p*PGqVh|<u_ZMkoai%2HNtQ1u?#iql05S<L~n3dbM+?Ex#iS<H!hsuLoB{J-b&xf1v-lp7hN;t+#o`$2=1!`#f6AK=`~KS+fseKWdG&!`5Dtzk*-v{SI6HqQ%8`4T#(+zI#0|1p7A5IQZ6)P8csOD@lFazBa2G*H!RciS)TnunM9-n>nLw`OQz=<o?Xj*Y0Zpv$6i_w#HVD8HW8gGurO!h0&k2-S90(H`Fr*{n_n*t|xt0TBpr7KEA|r@{V@jZ0m>jcLOW!@{F7DVzJzJJ1#YV?|#2@j8lBwF)Y?IzqazN?0cAPB4R!BTi)sMd?6(s`(#|FIalNm-#C(fxA;9w^pj7?Qh&Fv9sdUPr?2PC0AFi}^Ywor=cV_x`^Gw5&P(5u!B&oWKT_UzF*0R@&vlU%hW!UeH~Q=+j>72AR&V<5c*daLTCwmQ2gl>R+>br>dHU|-e)iL5ve&ci_vjBnne6pUH(1^aG<Vy5ZOciy{#)_%^-LI#7WRv*44G}`rDw-@H=<7N_G}lU!Z7SpCI7M8vt6`br=cB-`(Qt5P9D6E6uMk|YidRKBR9x>fn)n7@trj?@3ED$|Itx7{_-k&Y~{57D8A(tiu^4%qW#`ymvS5lVaU(<LF+YM*2CHn`j4IH|NeMxsplLDzg`Qp<64X_BM*JfS7wV>xWDUb&u`ujlQ_HL=(AnS*=Hrr`d<3(b@grRhv=Dx?eUDiSs3Hj%1PhdUap36-(mHo@16&iypsD1XDocz_7&(qZC~NOZO<@!9Lg+~`$5N-;r9BcDI)#c5oGtZEi0v;J9dZL&#T32T=(L`ZS^;@V?H#zhuiBP*H-SY9VzSK^ZARh)ffHY@inw#bUPWJj>`4K*Yo*cUgSQuIjaZy$;jDQXYsunqy7Nt56(NA;QMXDK0}+a;=9&b@wVeGohiQQ_bT4=xJK~}=vQsZCU_p#G5!ep;r<culXv5Np1m)VQSQ|Q&p2CC&OrOn9}|E$%#M<H>iy_*U7@?M&!g?7&-+2EFy<5I5&G`-`s*dueL1fsc(#kyyn)2o*_XaM{#}+z|99@WW~-;^|3vz;VZk?+Y{U9C%`ChpnErZ#XaBdRV;|cHx^AnF*5Z`(b4T!XTm4;yF`wwW|0Dm^meQXM?;G~|kIyChY_34~=8(Op&koGbS|8?j_y1B(>CfhQ$6n9&(x>}Kdl`FHiSORmHHKG1KWWr=pRHeA7=`DvD_8CF%x^ARiT3rnh5LK%+gnqPVPCpWgG5{VmQBID8baT_Zmf&(?l|%v`HMA{I5=`POti&k(_6e>)|bA!9oJ)@*|CSdI}S6jpR8N(-S0V@?J=(PT#XVv+tDb(^<_{adwrf@Tx+`<+3QoMo%Ac~%f^Ye_G-5i{VEW?tNmHbtJ)mQ(?N~x^*@h&V{12k_CwcE>>KO7TZ(U79)|mk^>-xB`sK5Uwsv`W5$_+~@Y!!`m&>2TcRX&5`@+OZcwSPaB;H4AGadOKe}sRm6`t!=$ekow`g`&9UI|i;kuxUA7KdhwuwUAjzWcngJ;rsxg75ylmDxNL@AoG&KjZH#!hPx8+mdYYpM!m7^ULi?wm7fBzOfky->B_EoCAENea#@|cdsjsVL#d0O`rYH^y7Z=;3M$M@5KG>06gC}5@HW{`r3{^<oT&q^|tudtk!rBWM($xUshW7v8==bc;7uf0PhLh4L#^tj-!)5p2I$!fqiklKcMf9Wt@|dfA4WA-?cUZ@6#U2eMs7K<O9U>@hZH>9GDk=qd#!HYcdRR{xd~<<6(CE&TR^w|5|h3if?ZDP0Dwsn<M+xuIQ}Tw@!W}`K@d>B)=m*AN-*8cyI9bA-osS>l-`|DUl%W187(4N&Q_7>cC$zOv-Wm^#$G^s5St8Hh;<Q3`BjLuLhw!zTahL-i&erc^uAr+I;M@nKdl&9Y4h(4l&Cm4p!PvD8KFslv6iQ%6BEeH$MzUJ)`~Pv);ct+F?)w$#3NxDZVqL7UJX;g!h5cCE)YpUO10)Ux;sg{ZR5-;UVxR2IKt(uWpzRI}JejRV&H!Gv~e<a$fqniSYTpnRaUi=G)uT;NLoo-?L>y{jGp`D8KY;yf3wH9r{U^7{u>o2gIQ^;^R0Pi|;M!g1EKezG$ZFD2MMMyI$dWmc!@1tv=Q;zR&#T4f=cACwTsM3GacprnN%9&hiA$kLq!rJlFP!XE|n9w6FeGN7VPkJJdh67W&)!?l{h#H+W955A(m3W2&tj<4iR2f4dCjJRXSO4}4gGeqUg{Ex+?ncC`1yXp|pW7SE^e;JpaF(tgyxL314UIGzJK6MsfI*@of$q8xnh!vC_Ze0?dN7nrWw@F#CXIYywYR~?&vLp#6j1wXtgu4|M2vX!q*sw3ACWBfnx{Wrt6Mhubq1iZ&MC^{8>t}kRhbUeen?tZUc>&)l!r!yzp`jt0)E3rhfXMX2Q?$7^I-j?6t&wZXu4RC$n`}W$j2wZ1NHMaYcxNa}f%vQcNiSKE=ZD%XrRSv${Zjdd%HW2qy+Mg4WJ>%oJ(E{^x`pLF(jH7%m?>)s{&P=TL^cB-F{@m{gY^#WM-M-o4yPp?3GhqGZ`gZ}=HQ(ZQGUifTFSJ4t_PDLgDC<vGht(+O$Tv7{g$J@e(G%C99M^dG?PkdJ(bYT_^)FWt<Kp8*x&PO%?}i`H1HZ4Rv<CYu=l9^aXAhyA3%pOcodiGQ3H(m!VoJ1}XQ5;qxB6q0Q!7-SS6Sa3NB(VZ(JpIN$v&NHa0-t5Dih+f|E4@oa^(F5<zy*{IJ{Veb;#UHC?~EI{M9LlPwy+X`dhKBeys0r`_+1>Rt*<Ail!Ewnlfp*w2<B&KUr6%`sddF|4-HjRQn(OWW8p!YX8@ttXKEav@cRqQ6|ODH0Zw?SS7`msn^I#caSfWw=*eTN?l1-I*h!OJd{asf9hbe(q82L<nGiq<nH8#)JEin<m%KK<m%)K)Nja28<UmRBv&9;q}C%>B-dtA{4KR5S!qvlCF<8qid$2Al9l!)SEDv%QXEL_OIA9997rC*q<9{630Y|jS!p6!=?3yZ>R2Ylk<<-jrDw^J<O|e$WTjqS;0xrN8j|8asaeTN3zL<mC*RSakEqIjME#PiGz(cJ#p#$7=cax`R$88%o2*l7k(K5o>*T*RB*l-ZMaU{Ceo4(iR!Q*(Y9X@H7aCY4#mAWxCsE&%lgLM@&&fy0XP6YfOHG+m%l|7?^HJZCRZ^Ud`kbti;;*Rh$to$%PJKas!E?yYq_`Tj47nQFpf)2L<c`!pveIGXj^zGKif2$Kla+2D&meDRQhb1#NLG4=e1M$7r1&!RI$7ys@@4W%YMM0Qm*mW8p!vv|$vU+xStnPfHX$qhmRy-!liHYElU$KnpInh#gW8Z>gIs}Hk6eLVjoN^$v^=>Qxd4-5KWbI7ANeb4Ir3LzUuqSyFF8N83|VOra(;3qCdC>x4_RqOvPORHg{1fo>L)L-N{XLRGo%4OBR`~m@B%CSi~Nv$n@RCi>I3ps@-6C9@-6Ze>V5JR@=fX!veHZBo8;5f^W@XygG`F|Qcsfil9Q-s$w}k{>Tz-cc|Y|SS!q0ZKY0^%3waZH7Ig}F7I`qWFL^Mz9knaD9l15N0l77~BDFTTBH53ci|j{!twEn?V5R%WugO=L6z`-)ljl;WQKQMz$P1|Z$V%6cl{(1_$lp=dlfNU6r*0&VCoiP#A}jrwtaL58Gj%j|EqOF~5%maJ>3Q-Z@)jn=vD6#nSn@B_-^offFR;?X^i@*4j7f16bw63@I&u_w9Cbc<965wZ@gOF}q0}G9q2zGtYO>NX<Z!Zs8ca5*O{l?SrLD+K$YrTj$z{oY)KX+Wa!#sFR{AA5C;1B|#Xi(RWFN9GwJ6z_T$);$T$<dB+JfAS+?yIiRyvB@n>?IJ@nY%<@{iQL)D>i<r^!lPWTl_Td&!rW6#vGg_%4%TZ!c&8FR)6A^Hb}Rm6jvtCugG8AZH@`P%D#t$Qh}n$w~{7Gm;-_(6nTg6yKsg(7-AwKE$Lrh5CxD^cXpXyopKiDkjC}s2|Bn(|Cc;k&~(SHL%hIax!@alj85GTgl&(r%>a`Q^*sjC&)@?k|&S{q^9Q79@Lp+r6yTvdvXtQxzv=MTA13Nth60jX>M|1ayBN#S(y~)q1GiU4It+s=c6_tD=k3IM@~o0OxCFG<%eQ#YG$(1Tx6yB$=>7))V$;j<V@7B$V#)2(^4~1vyhb*Br7dK_M)bz79po6=U`G?oLY;lv?IAVxeIkNS?L^d7jmc6)Rj7wI)^-!e3E*Qe3JZ>`VaXjIgc0A*9)wY;yTm{<T~U=)K=t1<ZjdeayN1?br3n2Je4|=Je9nax{<t<yob7*tn>(Z5BV_l1o<%e9Q9Z7Ir0ta@8lcgKdJwc|0JhN11*{ctdinF)av9y<Vw^=<Vs|N+LmmP+fcib+mO3Z`;xnmgQ)|^!Q{czk>tVTQPgQ<rL)PS$YZE;$YaQ(sq@IA$rGpx$P>uZsf)-;7n7%xXHp}`Gs!ck3&}IcQ>aVGO6QZ6&LvMFPh?U&i~2oT=~VJ8@?@$>9zmT%HOWfHlP8hCqmCmFOHJXaX)N_S@^{QLmPzq&>QJ)MA>`rYFeb&J)InsW{mG%^fvKr?YU-Do0+|%|p$;SuWd1%(iXBXfgQ$bZN<+v>dy#|4J*nNuJ;|M!6n9`!+=<$Qth75>X-9G=ayzO&xgEI`lj0Ukid$3Lla&ULm9`|eCO4-xBR3~ErPd`kCD&n6T#Nb*xfZ!J^=oozaw%$UveJ^|QsffU;^Y$KoKzojPVyH_inCF_BxfUMrRE@KCBO56<{~T2PFDKX3#^jj*G!84p}rw2{hRy``5u$v->9$1O7D_?Bj2IA$alyWsK1aekbkEBME;q4l$uOFO17wn$QC({8cU8N@1kxe?;`J{#*lZCcTm@ncaXPH*OIr9qp54i(d6~imE`qgCv^!~>3p)2yox%Pyo$V(x`@1#yqdazyqdg>x|qC-97$bBR=R>5Nsgi}Cr6QgU{V}GT|r*KvLdM8lOxFUsN>1=$aAP;$x6Q?&mm8sjw4SXkD-nxD;-H5MIBBZNme?7th5g~h}xUlhpf~=?oDn>Z9{HLZc433Zb~jetxi^2lw6!zj9QdjjGTc<@mme5o<F^1QhbqmnXGg>`6786li~>KQnJ#a<Op&Ylj1(q{$!=y$$iNF)P`h#avdhc<*C)lN-L1dlZ#O+l8cc`P-~NweoIzbiCltQlKM4SX=}3kc~VIx#bu~X$z{m(nG|=U29lKyAuF9nc0V^#T!q?}NpU~wK(f-Y<bLFlOp2FNBgslHke8EpGb#RwdXud5PqO<NlH$$OIO-j;(nsVt@~=#aZ!;<WgQ}h_{Xxx5R;rVg{>}U<DZb96_zLwg`3iXt^(A=^`2h6;S?O`|0rG4n#gnK><VoaN)T87M)QQxiWTj`w6Uoz=6kF7HWTk(RE%GTQ#c!zUxzrneR-D%h`ZYN(xe`;u)Krt&f?ShamPzrqOubT5b807Yb8>wq#XVBf?9>#Jnx;`h$<xRanH2Y<b|))sPwqz^LhV7Go|??mG=MsUJcM}$P&<(akcU!xk%y88rlxReXKF8UFP?vAY725_vOl#U*`M5nNpVYRC2}RUMN1~djhPfzp=Ks4%}1_6E=kQsE=jIR{fb<bT#A~Vth5@r6uAl2AU7fRq;@1L?N9DN4Wsrahmj{yXONX{CQl;&$fS55^#ECE3V9#-RBF0Ny+%zTE4@rs`jUK&{D`WaBR*m|N?$N3_Tt}E9>q#^vKKiowK7?0O>$mxVQNKkVRCM24RUUBL23nZL2@x_HL}tI<d0s^^!!|aoSyvN3+hK!NwGJ*ugKoyEL2}|7IIo@ezJc{uQa*R{&)XNiU0RcjZe+?KbZK>Z`xn$@%(0dYFVFO^6_t(PVKR2X;S}FFS7&$sZaj}#H68#'

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
