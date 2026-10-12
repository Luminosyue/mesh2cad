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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_014.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_014.stl', 'source_sha256': '35987364cf8b76a808f2e4f93266b6b8381ee3f53a9c41c0eb9542f0e63aaa76', 'input_faces': 1068, 'input_vertices': 709, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25749123096466064, -0.2593590319156647, 0.1385655701160431], [-0.07480373978614807, -0.08919106423854828, 0.27524203062057495]]}
GEOMETRY_BASE85 = 'c$}r32b2^=*ZzBkq<~~4DGWifA~{2YfRb}o7<S3oWyz_@IU^u(KuJpySaR6joB>fpM07BaksJhsZ*JeGXY0=TKj(kG&-c`Me)pN)>gww1+trD;ZHo*U^J)BFG41;7QVX9o(ljdBwS3y>z9FFlgZqyBaM*}(4lS4E(|@)uZ{4X?+inhRv^Jr1pS~l5LrT|nm9E>bX6Xv9(*1^qgogAU)@yi3pT6Wb?LA~<U!Om6K<^QKeQ}u@AJwYhs#3OsYm)1K`CnFF6O0q%&qnyv+cis+rT0#!H1MhUW02*WvmTid*4FhrL%wmVjpb_z`Qu6TLSw%p-*daQ<r_PC$Ev=0r<LXFSl*K}DcSP>Zprmyc>})d&1zgv$KsLddObNS@_KJ2CW!UIcNc7EwO>1X+iJfz_Xn2m!t(ZdwS48d{u%qC)q3=I$_n3ZkGB7(Gge%5NRn7S{71|8z_;tyBa<xOY?a$;kIP;@I>GY2@a_7Id3h~gAMq$z^xJ~mTz|-eWKsVH2iO06o~hPvcwV2jmV36q6!mY;$Nu%MsiOXG@>st2W@pPc?fr7>6)*R)<0;Ypi078?de+tQ-S+a2e@n6Yed*HEYW>=?%a*S%Uwm4v-^deZ`Nrm3$3^?|#qjbQ?jBd`*T+q<w%-U{aYn7*m@vumy`z_%QR~;%^tOEM!i}S%{p)&hJ*V#<74=7Sw)UTq=av|^dN20%3^&>TVa$K}=92Z?p2&_o4p5K3|L@ecd~^C|@oGJRzP}#ZPwCFb%ePawpD)9o)I%Oe@ICPT{gdTw%h$5s=k~n2@T}#(nOFF(Y@SrBo?`zdTJ>+37NfS`_C4_Z`?ur^%hwjRidXB`BmUuf^1?5*$*Ny3#l9yA$E)4X@b$$lxcz94UgoLgdsFy0_V3>-S1sTD_a~y?%(8!3z5(CvH?7%4%XiHPJ|f0LiwoR-qyG_gJQ%@|y!^CvF{0o4MsPdf+x@2hyO;e-`x3-B3GnT9YGc@UXWB3G5_}!Lzn`1#;pI_}y<JB57~bA;OA<so4~-JO-Jixz_FW4XC#d_ysMC+@Z!}Z1Q=id?>w#~tSASNEmw(bs<Vo8%o_!+ns<D}U^BVhh{oW7X;O$Kq87;=opILZ$Bb4je$G%o6GcO-EDq8J-SLid|o@s`t-@PQ#^0g}|iRyj{^!?*!lF8e7ntlKA1>b=0->!=hmhVD6cK>)T9N>PxRf>PlojX<a&4UN6@u_wEH%ax~Mq|tOuDp?;`kM26oK^qD^Kq(gqy)!tzeU9e|7K0g*UvN(>vgSqz<I3Ko+#lTjJJF(Pesvw&y>#WcPgAHwyXJH*7*0X$`UWOD_^MPdwzZ>+N1yG<m2c)ueDxt=Suc7txXi;_UQ`C_ZEkb@#)>YLM(5OXY=tKZs-2_Vn2H7&*pmI`}a%F0o*^iDzF||pQ`%isr#I-!WX5ezU$I4&Py-mihA_9hUL4Tj!zQxY-z^(xBlov)z`A+wtQFZ{t2R<5kFb`%WDM1i*}yhX!+Wt4soKM{KG8YRUuZkzjlAiH=|p}iuz-#a6M%XiS5!nAM)}M4PsQ^bLAzU*M{vA+w0EsgwG?H>qLw7E{?K%@1V`1A3TFjTE53wAxgAo*L?Q(trz{{?%t05-HSy3n4=3>zWdQ!(LdVzULIHX#*6;Z8}8uqRE^Q1AB?RdEZ<$Fzt~=Hwwj#J#|Me+a((fd^UUZDR{M>+UD=-!D$ZZF@17bW&QqRzHMo9{`>^$UfbZJT)$;B0kyf!NZ`Z%w#r)9kzwRpLljgc2Tu<d5yu3Y62=vP)3tyYi&GJ2Vo*Yw<mq-4w^KCl6S-9}^Q_ti6Yk9wq<y{^B<>M-1nYCWGeZ04R$>-^}*>~CXbbi6hpIpJdeY|IQz~}qAUyJs89aq`kHBPiYosagI&Hv;)`)Ryre>xw_8wbzuasDQ^*Og&=s_GkuBiVnwIz{!p-_K)hvLadaUDMiferPl^Nz}8UAh&mpk*NBfmcQ|FI^&B3)z=1YXFqvJyz1*kHt>1j$}!PS_vzuheEjEe!ne;Omv@Txd#cp1e0Pp+v8r!gufX}I<TkNg-qo)-KV)qlBid=7cU-H*_PSoh^8B-1lW5VN1IIa^^jj|a!3bW+^|Y!UCE8hFI-jS4XNdmsPHN71Y{wMYKY!$Af6EBb55}h#`TTWzu-x9=o*3Tl&*XOH9l-gdVpq|AeQZU}OXZtc?etxE{O9;g=VQEi=dAh9@tMxIkH^PL*>@h}`CX+4DXQ;I{gmgq<-JL&udTko`DtiMg6bPV{n-EZNSx}sK6uRi{qUO@)%QG|&g-eZG)lDR+!oHm&w8bb`qx*re63E)WYL}h(b2r$Y9^|_d7}gSX32Qf*TaA3{FWiNwZB}m7x8*0e_{FNiw9PF^z*aXf4o#&znfw32QT64DtrF$a3*i>5cci)gZl#fXN$%4zEO7u*Yisp_ruorQ&r#C)`|TaxyABY$e%cmze*7GJX_6v?GI%=bw~1feE7{c;YXL|<9cEtQNJsTll^@^#)$PUI>g6mMCL@*_k6d6{YOzzs&D4}gwMauhhn|@&*ypnHu+7|Z+_E<&!=;ec|6RV#_gH2Hbx!K>3lms-yh2L)Z*)Ddw%GxIfUE4t3CVn{1Co*>58a7oo^psc0H-f`8?9TJ0GWy2D4w6>$m5bp1l2eduucm$8S0x_1nIC)XTX4THf#5=a<j=ayw@<6ywnEr#2AdQ2)C(@2~Jxd|VHiovQj~(C3^728>Nneb<yyJWt*;Qq<%A;5HxcVSSQBJ<SgCJnnw4MAi2`9nbT!J8ctGU(eT=m#^9~UiFQrH`)KFUYw}^*K@r7F*RdFI~#MJbB`<=BigwGzaJ|ZE&3rxS^j-!{wUSgMmqU?5qVMck6tW+^K)p5=pUorQXaP%<3#^>yLA`iDxHu0=-;keo!LKpMD(ZY4HsWGHQg`z(>?SW&oiHYBl^=kx5x6eh91$MTFueCe7&WjKlSzX`1*JH0@0s_GZXt$CUJjO>&W%@PvQKzvA@-yX4dlD&T<)J)$L8^+v9vqVQ&9hjYa>Y^Rc|vmal(|<9YbH9_MjwRR(T<Tmin{b9r;B>bpaK<?(rOd5Y?rOSbX6-nBSc^}Y3n^7wq$ND}q*sLsm=Pe@dKkBRwduOSJdp7&$9U0eIdtG;Xg0<Ld!*ErQT?seebZ*+(i?d-(;q5su5M%07+uT{{aML)R0aJ^PZ^pCsuR9t_VqJKQd&mQMK(LY*+T%5O??GpXtLf&>aSugs>c(Q@V|AN(`f9!m&&zURw#})YjFMno+=pTLfL*Bp1qeTCB=AYp4oaYPCKi+%O+0PNg^NI{FI6ro7!Q&kBL+>H(FVE#WGS3J4_I1ZWzOMH4=qHv>=Lalr^cc?T-M-7}e{WO1|Kcijg7a9uvZ<=?x!0WiE^jBRzB}X+_v;!*qUw9=4&r{gd?!xzjV%B0es}#Gqx#yp*{s2FqCMu`uX(>GmlN&L$5-ZYk|V!pkJ&hq^Ip3QqCM`MZMh#-+!gKdUi_8&;ld@(8!wZ%ANDK~=e0oJb1frZS8hvSf8`nLIgWijYy0}@RLi%oXI+bUUaK`a%gf_@m(IuatY<(J*Ryw*%s+v?J+C-&gtyCnE@NL;!q?j76xXNb-f-S8txJmQYj+Z^ySl6v_W`s$?CZFG@z3)Ee7k>)l&!qp?kmN81M~h2?#F5u5AptyzFF)1A+_JMp5uAD&P?F?-qyMQy9aUn<<(f#*J4|7{kQAL>yZH8Zl~*y;#~jg$D)33Xi@gp-w^W_zkl_boIm$w-}v%|n1|cGchxm9ulBSl#LFMqD&~9IfP&l)m$!-eq3vtlEn@y=tS-Rg@aN@neg$7Iu}rkn82*C$Yhrz|A8p?|p}yFU+An;4>-u48g6Pjc-@aa3dL7T17K{C2EdGU$TceJsC!KGfPY;~u>)8AotnsPOI1y>}f8%r9zN0aso^-x_9{=$)*RMHw{1?7#)nop^_w~#XZ}9b3X+9t6&v+cW=XA6B&5irawy#eu%ll>QCE>d(-sStT_Ph(eE9*^uo?t#oQhl?<5xx&RaAC6Qdj~GW{rQ)oe(m`r_WMp2^>}_5%k$w3R}#c}3v}T5aJD<5J??it;r8qrmnhoPtr*Ww!e@&08dcxr^=f-WJB^s^T+jAFV!irCe!k&qni?nC`TG@~x4hgS+VAzA=lgJX`^JlQmi(6IMO$i!^=hxf_<rQaYef59i`U}0L}#&Hb0FW3*XACL5$)VPg6B&O=8N_lJNxkRmD|UPcK%(T&x6-Xi1m6BYw>z#%@XZ5aUb6G;m2aV?yB!|KO}Dv<INoNn)B7PF{1t2=!ZOy2(2G2+IcjU&%fn!iS@cxByc^6A)@^{?(=&`R21vg8}WSwJvLah(^aP@&&!6r6u#NB3(vo@_Y&>VVv688pslFilj#oUr+wFjZ|5KPq&LKPGf!q`-+r!YFJIyZKED@VCdRX;X)2!w1CB2p*WK=b<I9cv<mSmpInM6{as2_umn-*Yd_O1P_%b?H=X#Fr7wz%3FURc(IKJGiGV}FOPz$+TxDRgx9AB;@_j#TfaD17UZt{FG;P}#ijI(@C!13jN?<g-HaC~|5f63QP0mqk7XA!SA;P^7}{LvL~eCb=qasHemk1x~H$@1L+$CtK|pR0N+$>YoTy#)6|!11MJevj81aD3^la`JWs9$$n1<oQqFakP6s=l_7?#W=f@mk&5zywygsA8=fF#_)SMI*tqPX|!icYaZt~FWbHgzI`4y`y5~&^F6(D2ww*UZ{zw0{>1Mo1@U~?Gt0yEx3A0Z|KK>%!oK3|y-`S>mjiwKyxfb=$Huz1`1r+n*>!(D`uUQmC!KHK2bemM`=@qKF~17*?fHY=wHJ?v<yqx(oEo2TI|n_DRQt{LjUkUM-=43!>UQP+*?&;Xx6K%Sj_W!bF6Pzl`s{nc4~TiVyK@KZ-%4V8)A@G4!8hOACgwBVD8B#h9d=C4Ljrxfo(R5f(F=#l^#=O(eY4Oqm~RBhd0K$)@8{q0ayyG167yKkr5BvPHWU}W>(htq_ns%O9|L`RKDOr`KR@XFRls!t`}XyMJ<oSHy~cmvxskjt8tB{Cr{ACEdMaEI*9Erk#`S`|A3gIq?|U*_k@q13eE&SZAKw?#2F1zk4fO5nskwYT=_xv1%%5%FfbXAg7e2-9|964Be|z-=*ZX{-yx$AocsXCp=Uq?saC`Qj5!Vs6?+#Cu_vd%A@2YTG&hz1G@cr+N)Z5AJjL0dUZwC1O>s<IoX#SZ0THf#5<MshRPclNz@%*jnxYMeyKMIoX`M|f|PjEjRoT&P4`#pr}UE@{X+aV{<H^w!N73;<GLGSU8qQ!dge9a6oQ^a~dc$f3d!CgsWz0bn%d}non>TA)p*sn7)PONuf0-uj2f5GRAZzgm7gU`wPtAW1VZ<|ASyydCL_q}sHJgxfPF;942n*GmI)z>ed<o+D@PqOOU?=_jDZYHU|xveG7dr$n8sQTJl`S9Mzj|r-8-{;X^e-|&>d0{i}mlsiSq8>bFa5Xv=tNO0ZmAIbzdt*d9@jP9d85S+tImG1i>D0ARqW-rBbKcwCN%Vs&`XlytG))op|Mm}W$GwK4e>@8#`1jkDMgM4FbGTotd?@-y@7kKRVo}jQ9*lo&bRp3{X7S5BZwbjJ`bTfDmFGW4GK>Ck-x<u~=ipQBhY7uT`OziB_(|v6=a;pdPqlg5<Z&A4+t<Zk@%+^_rI)<F6zJRax5&r!IQV@%*M<wHRbSsblHXrilaQ+Vp5(fG9h&9WWYssvIr(}s!<i)2cdbn3aoap8QT2@%%aBiwCy097-T8WO;h}iZ&bVScp670h6YVU2gU9XJ&9S1LOTOjnsg&h0s_%U~hR1W>#nGajJsNO5aZ{s2J4@Z>^$Zv;`oa8RAMfYFK`El1`{P-6_7MG}Z`67Do~=dyc#glx?Yi@c=pXOEGd$il)fWAu&sxpn?OHX_KgO+I?Eg_p^pDxLG+!5#D=zv+JM=ftOH1YD{I((w*MH+PF|X4u=i=q@evbVfi$}}KezxX356Ah@+{xQx<Y*!9TiSlEX5zl3XUTKEK6!OQp7#TNd)^Yx_v_s{KabVdUQJegZ&rS8qyKs?QT06wHgWzb77?%dntKT6t2y0LRNvL*Bff7JyfaqyjdFZn%}i>Nr21yD2+mhqS4E3@9?#|T(OZ=hM0+9%@O-&#kvP@Y?c;iRR(}4{^d8q^W|sFq1AV)HY~Ptf?nn4$^Xy_j>Irvwz3tx;?{V3_yJI%_UBHXK*l%-|?-vznd|LIr1$*)NZbtKD)i?gU!{@vB>WQka?VZTyyEjY3tG;JkHuhWQj8%R8#acd27r%%S_0L+&$KA%qDWd*%McDuSN|IQ<@NRBz$<qm{@48xt*WdqGoa)=pA3b4Pt^H!|;p0<(Y{>Vr0)2bG)C=eJZK@>qW1w%(pJ(8_GUPB{-#r_UqWZ3LlR1w)>Xxkf2A=PGYj;XgeG}J--s(*gRp0-<?xcnZs;~E7$K!uo<#^%G{DPmuRJ<zM<C)%<uZztO;zWD!UY1_|f@r5%sXQ-#qDZXR-ZmN^k0Iwo`}Nk3_&O;=p%~GA`@O7T(PF#YFOTx^^*U>`Xb<jVd&5tO?e!#dWdGZ}Vtci}-s9u?X_(k9*YZC&zdl?m+Hc@Fj!}D+Xs7u(<`>oH@bl~2GkLvXqviMs^zHXRs?Ff`jQ>ZxKkWCTpNjW~-Oa{xJ@c}P>lEAfE_g#+r)anMzK`qX8{&G$Re1>af0xo?+@|yGdGD~U+z+i9iR&73T^C+&osY%!i{HolB>wBN5uLgI7LCPqleU(hv$~Pb{l`(D?|(l{=l&l*R$S-WzBXyJxX#tTYJl-}OFlOY^zHh07vc3T9wFYFwSDiZ0rI`sWw_53dX4kg?w%>C@4mQ)=Pf(hB&)t@&s**_Pf~sF*Y&vnZ`VmweI4fotxAmq)i;Kv@bOi#OuVRP-j{rxHL66MXlJb+I3DxG3O~L9FF)>{Y=5Vccn+2`M)(!7p#Cdjy9|7n<O$cJRo}CepYwQ5{35sa$(MZoJ(4Q7H!t6pGF~T$?R7_%WdFrcvArgqzZ;DX%I#fnfc^Sg#rC?lPvrCR%uQmu4BYo{PhH0Cf5G!AH{Khu&%d6J@9_P;jJbLH?BloL6~6!2A_K3-o=4sH^72ibd|cY|r~u!8KP@PV=X06(y<jc#xn$LMpABKZ*{MX;*Va1lzC&2N>KlER@Ok0%%2=`dNBsO#&pka_EWaiz&#&GamZJLlyK6Z=ySpc;zInAQ=iALq6U6fSj&NT6t8$#!t_h!T{w!0J&%Z?vb3GHzig}Bx_(9?OkGmb=?4Lg)=dlx~aQ{pyB=V;oJBfWfFZ16Q%07bIS-p(-?!y>1ocm{5S^1p^e0@e~@jZyXr5?AhV+Zm5j%yX)7j~WLDAw!u@f^@@XFA`0-(XuE?zeWG#CJfhgZQ2k*SY@p7GB|f0{H&*-gs@@Z}k>^D@GlMwr|4spI^cf`9ApCXYryxOC|94u}yA8tNY7%7|%YI_xCe=51x<s+gUe`?+e5CzXw|;PSkI2ueZh#zF(Z6C8+)HPC3N&<2jxGyT97(YgpdDA3JW~dSa@{?<wHxu~p@J5jmG~J29{D-zV?7nD2wb_ut1GGnwn@Jzad?=N><ieSB}?&ky6+cO7TnpC91sC)>oT?YDjJzzO2JLRa*7ZcpWc;yzwF-~KLR0{h<G1ro%#%|4FTi{}*n@iTcW_rp#+zp&TaX$&uaVP~9JFMJKYf1a?s54WfOt~hl+dPlRbFWMca?nl?kAoj7m|9ia*_1M4JQ0x~^L|q;aDe&$2K+8JZ&sg3+-Xd%Bc42w{`yoq<aXkn2i|tD1qd(ohy7)M%0pH&5@ICPT_5WOy*Nb}m<Hu2ezpoDdMtooF&hU=qdwOmc-y`ddA4ORGx$W&^>Uh(d-HYJ;mHU`FPR!i>Pg;LJVT=4e`ki3Q_m15rzNgmPRJ45eu)-(Q`t=UwE#C;qe?qNai+pUY&p16oe%~E?pWBfVBEARL?kBPzu^{04?pVv$qvwe4!L{dit#NO*%ax+`v+2BU`9_;ODWd(wQh50bVdDFAtz3-ddoOMm-?MAspIh@h`~JVb{u7;eUT8lTu$TY7q2+7kD~a=$d8wA=o8>CW@29RdwVsz~aks>AXWndN`DW}baeV2|s$0I^>wB4RUse{r|NGD>#}8WD<-z+@_Wqi4!17J_{`%qT(`Jg}MO(Pn@?G%#^}koa^4)p1@_oM}*Z6o`ZiZX&<x_kg690aJw(f}KyEA!tUV(onK^ykZ0jnQQ{vwwjbKmmacVjtkZ+~)D_03Cv$E(YmuST)|@*2-?@AJPSVRSBafRF2!Y0I}2|7ymBS$}-Eq_U<_c~i@$_3N$tlNn^vf42VjKbbMG>i^e2nNjJZ>NWpw|7J$k2&bk+`ARf22K<JvZJDu2qz>>&-*2aUB@$|a5BthjzH$IM2~4^dJkj^}MSSIBXd&>&;CE2+C_Zro6yh9UQWrEU*agl2CM^SXg3ExjfJy5>vxDn^bAd@)Li2%Jf(w92!=dkj!@(87q!k^kV{CRX7k6;^+L7iH??)kS<YXpo;AEW%ZUEj4CLIIa3LXOv1CuU;?g1|Y?+24^gdPHK1Rn#Fu7#ceuLU0glTL+(gQtSOMcJkJ#6wVsxBE&V-?op}cpQ;d1y2Oim>Pm*b3(rX=L9bVlYZ%7{RB*fcsrQ15VSP75SZ3q)Tc9iWtPT;_!Er_aSe?NaXF0(@kbgL;`$mF;?FcL#K{^L;wmV_`%s8$I=K*sIJpo{b8;d6(#eH*zLN{_cqbR)UQRB=FHwk>LW_dGpfN_<<>W&AEedgE6yi9I3vqXi3voS-3-JdU7vi!S7vky~7vd%w7vdQj7h)F*@iG+Re^H3tPA<d~oLq<(IJpq7a&ocihthTuAMkNqpMH!&JPU<*6Lcha6L<>>@eW_f;Va91b<K5hA#UpALcGmaHaIzN9z`KOjzUcN^&<zj>3tO9Z=lpZ;?lnUsjbn8hYRsr(A?m|8rM}x<3c<Z`aYQ2RS<341}+61r!f!4wrxWp{u(6*wzZLO+48=UAB8wCG$)wqoS<>NREVpg5Es?>JVNW+i$c5;x(!@H<L%FcLYxt$w9+3f&=<MEZ=(<wMB7TBeL2C|P)eX~YF8t)tthxKN+WD*3-onC6yo<#4x{gBj4Z)8*#X{-Lc9;U0lW`<5M=|#OKm!ad}TEXu?JcP>;Z3tRse4V&-ayFw9kC{2MY1W(Cr%Y$KZ1sYilrRFNHfGChf2A9>k=-Dm=o$G3j81-*IwGde@Q0{ScG3Rk$}|(oYr6jhOT=M;bSAa7@}%;T;;sq(3O!1~F-Gg*zc89jx$P#H3z@M>{ws{X*gVPL4_MJJPs6V$zNZ2O%bHu5cd2q}Lp2+|0o-X$ytJG>%DsRJbi-(qM%<BPJcL@VAIb|5SLQgJaS$3Kwv4O#0A~#sd(Oc2+nTF=<PM^CBj_;Yi~)4vtCNDZEqTnDi%w+u5<N^i{YEV$v@Z-iMg<s=|hYW70_q7j$w=`q+`i0}+#URk#mg($)&+Lri+hk;a`I9FulYc$da8>CXzcM@%|E;jV~DM=HD@G3j-Mr#m<%ovLslC&#2u9cerWF==;&`ywW7r|{c|N$)t)xQByd($5v%t#M5Hi^3fdlMYe18)DK?3LijBdQ;(94vtCZfd4>#j7K5<1WI}F6U4;#G}d0=d*B7o{@?}R<<MWj%fT<9lowwjChm`1c^BLt{5_QN;`fM&-$$<e6#PE8D3tPIQN+ZF$dygOiQraH%8RWK6F<;cdxIZ<7eNPu7lBtnz2H^gS5V4}uMiUtLaw|I9t1uQrM!3^F>zVs%I4s*;9^k9i^UKVCnHz304IYxKq)VFKur8dV+{sB0xy9M2QLAyh5iX%3)YY;DKBa$#KWNv!Nb89pp+LcASV6*xw0kr18@l_<;4<+iBpj)+ksQT-Jp~gyCEiiqOtY`KLIa;egR$v-T=J{-T-zYS5jVdq7aXQJ_e5hUxZR#yoi{%B64MGa7Az_DCNach>6cQSi6AFfO|nHFZM!A{7hpV0DcBu2^|Su3HCs*gFWDk4pz#G8BvHQK%asqfG<HQFJ3}STnV|d9k>#>9F+26ImE=@Iaogje+LeRQeF&3O#ED99Rhw1UIQHkUIX3?y$Rk7&g@{NoJmYN8%#Nq^5ZdRONA*vwuEMPr11j8q(>B9j+peg!Y>h%=5eGk<wuH1`zicAVp3CK%8w>AgTh4-lWGc6e$=4H6>f!?w7tTVAKOFUa-{Jh#H2?RUWJ(Sq{6Qdlje1#G37^!Ne3!?9x-X8!jvB)p_vpehM3f$Fy%)F^n}745R-OQnDS#+XbwjjFF{OtOyRYNNh1`d{1^evr|@vZq(c?HfS5E&VaktD&@2j<KuqdXnDV0&dQ#zTh)H`YO!=`VG^ZntmmwxSq3{O8q>&0!evE{^t?($sq$3r+h?q25Vakuu&^Ht=g_ty>!jvB~LQg5&3o&Vs!jvC_pt&4ryb>|#DTO_VNuv~|{1^p&N8t&GNyjOC2{CDm!jvClpl>Q%4l!wFg(*K~hDInHjF_~q!jvETLUTLPcnxAwQ{l~sNuw2}yci9SIGclYHkh;_m~tiM#RL@M=Fsfm=HUCtm6R9nBR?)w_&8$HFBPV|_$BmTEsgsjCLN%#iJ0^Ug()xo04=SshM3f)Fy%!TG)dw1h)LTj{1#%;hgup_UVMoBxLDznh)KUvnDXLR(AQcT4@68lMBzxpq(3T5dGSYRd4(N_NsB8?d9gS&Md7Z9Njoc?12O4iEsZHJK1P0As&E8i()9{cUR)1#C_EG~X^6s6h)I7^nDXLJ&<_=MA|@@VFy+OP(9;U{L`?db!Z{I>KGo8g^5RqE#}x`kA|~CaFy+OK&<qNXL`*tX;b_F9KPyam@n`5q3TH%2T1H{Yi)El^6%Im7+FRjVh)Ms^(wOq%Kgf@(6^=qox=CTmi<_XC6ds3|bh5%Rh)I7@nDXK;(8>yDMod~kVakgYpyw3si<q>J!nqNXzR=Q`^5P5R$8`!vBPRV?VakhNL+@&7+z>HoJuu}=%8!4d5I2TWUTln*_<Q8ah2ZbOZs?a_H+UfQU+_TiZ&1pMzab_b=3xB+JPdpfN_p`fV&eA5l`e35a5E_7#b$_!uR2)Ug0F%<g;HMp6fyC6<jTe1^WY%pSKuJ<Q0Qy$Q1Bm6%8P#>CJuG5{s;~QKY&tRe1Mp^6LMv7a3^pJDCNZ#h>5Q|SUZESgIhx>FSbTZd;z&~Dfj}o4|F}a4|oKW^5O`@#D76Uz*LCG!}|$59{dPOdGQfq;x5RQCBa?5t)P?_TOlUC>0tc~d=uOeN_nv(V&aR)l`Fs(!Tq2c!TrD?P|AxTh>5R3$AYO4Pl5L{cnbIll=9*e#Khf@E6aepf!jbSFSbEUeA~g=8+;qw9ZGqzJ7VHX$d#+Xm%xLdo4|v>p-{?;p@@lZKqrH#5Kn{m3wRp%8I<zkGsMI_kSi;Idw@GYDKB<FO#HWlwGa4jup3Hw(T$k+vc|d&d>K3p`ZahMcr^4bcr-W(N;xwLs)H$KQhuc8NTiJvru^6lx?N#6V$#+M4@6AbLE+yJlkQQN^5Y)p2!-z<CZ*>_HdB6l2YIre!p#tq_EwnkV{d3~XBvNsn6!z)lpmWwcPJc$n6!<;LlKj9Quq(Vq<a;n{J0l7THyzXN$I(f&6FSWBTx2MxCLU;AcZME20`;U)3`Na(q;-%eryH}Q@9Ue(zXhZKup?M;lB`*eycF$$8Vt%6@G-6l%5;eO!=_@^5g)8TOlS5R+#c*Ff^|-jXNSHZKE*d$2QQN3im@y+D_pR#H3vmzJ{1|pTd+M_dyMXpCBfs=SDVDek_PQIZ)v?h)Me>O!=`7G@mn#yCWv;q%h^jPS9Nn4?;}ZUg1#0q+J!hftYl^!jvEPL#HeJ3^6G^H?o=XV<F_pK?-+3Oxjmr%8z}aZ#&c2jhM8D!jvC-KzA!V3^8d(g-0VM?WS-N;%?vrP|BGHptHb<zH-}Fia1!`a4=`3{O*fmHP+w3_HXoeq_L<Y5x*xuV-)@!G3gbB|3*xDM`5b>4)jfM5pY(t?>)rCZy+YkqA+bw7U(U76A>q(jl^4gCDm89LC=8a`^t1*nG2l?wtw3KoeSOq{suZn;i-s84e)gERPZ#!(^2m<=sbnDAtv3b@EOFUr@^V<GvE}&sc35o^c(OxUmvaVmAcS*;99=Yz*p8l7lQ5I)<M^RN!Kd;72-Ac+pnMt6mEc+w7$Z%5R=waxGrMSI^cQWy5PBp=V5#1LRTuh4)Hp)k+`bwn0(h)vO!-vn2Y#I9bah(Z34D`s|sxht_rRK)fH}nn6$CNbr6%*R=5aa()Se3hL|*~!qn!h&{tsE7Gm;<3nP9PZ7mF~0^aKTZL_b$L3e?@zVf@T9EJW0wtw3SJqjk>qVN&KNAb5upqIhFgMS5ILHs-Fy#oCW90&G-V-d%p&9Ts(;LYG&;7y1(qm7%OTfiF}{La&Aa1F%t4%1=>ztcn-20n~sJ>U(9%j0h<fEOdC_ohlZ_&q7o0^r(MS6OIDa2V>|2tMpcd*7-6>MwwGRKVYsz~2*BM_dDKs}5bS@L|NHhZGJ&Ou7TS7#s#(gm^L9un1aC;R1+B^DA5uaY?k1_#a>S%r_oiKzo8G`Eu4|Un%Theb>QUT%%XxHSK+9N$_mn-!1o*dC-;MroP{1`pT!!+2C5fQqxzOLz{so`u=7Z%?+R<6t0e#v=(@sudMf#MbO1yT4uL{mm}Q^UW8>vK}UmWnQB;$v=aC`Uz>XRN<6fO!VM9VHUR6`w$Gu>!JmWALJxvzT_0jSq=z)-sy_a}SN1>;g7<){Ia%vDnd|#XxP!NwbT^oOqh*FeL&3wrlc7t&i_jkvp~Jw`u2yJUD{MdUWc=+4s0X~lxBl!tT>_<XMm)#IYkXxK)Bw}Cn1ZoE+8De7b<TmV0gu8q4}(?*pGDtN|B+JP5wF9xEr(77uf`af4P6eVeOlL7sz6JDr{MRoPUh8!8(<uK2(1F{iT-K`tqcC#_cud*<++3PEpTNVPdc;~xEPMVCD0Y%aEzbb&}!heEga5#8UA1Y7qDsn(KUxA{tsaT|5APiqyA;}kF~UqV%oOIWPNAi^!<-s2651gS^FPR_L{-'

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
