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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_002.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_002.stl', 'source_sha256': '865c1d6abe6c4639322c25568169bb1cb6279698beb287658baa03341d74ef65', 'input_faces': 960, 'input_vertices': 590, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-34.801231384277344, -18.729333877563477, -25.56500244140625], [37.064414978027344, 11.484025001525879, 40.36996078491211]]}
GEOMETRY_BASE85 = 'c$}r3cT^SE7w-q`iiiz6jujh<*uciv8<yB5Q7<a?XzVTOSYq!T>rK?yHP+Y}dyR_GXcTp@$6jJ@kG=Po{NOl$y!D=Ieb@JMzYOQjoH?^+=FG5c(jZy#ESmhwrwzN_ruexEnnv={vS<S%`}XhFF|uFDUOx=+(0n+je+fRjQHzF6+IVOKwPF69BKvjh>t9j#uiQD<zl84Jxp&|GeIt6c@7=dkB;~audiINq&--<a_#ra>bCGf(fhF`ZMN8<z_5a6zY2#PHn%23R74L5ISy6KHc2piC-i<{KIM;%Alt`Sr&xLaCntO<s*LNLF?UWnkyZTdZ_bkM@HF+|(qpx_G+9@|Gw&&&DRlgYg`AAr)#NVsA|K?oFk)Lxta%dW-+?rU0+c7WxA-UOw*T+>U*NbR}+?sTw6n}4@t(?0m1n~N}#t(TO?T{PIPx11`rLmlwOAiGmS<mL(ICmdDRFd4z6!j$9Avd=D#O=6_x98k0vVq&t-*rsulv@Rp@pf6SOUn8`$ja?#rRK}`K9$_M;LEw$c`oNxiHy=t-*-j$=lf%`SWbDq<Yl=ZcK#d6?G9S-CY0K#y-eDVdCIw~+kxV|{;^BA9W^&6yeh-(Y`?>~;Wv`k-|q0ky=aHrD4JRNKkgLgdeqX=iTl&=vt)f<R{Biqqpd#kCDb7|BY!TMczN@Dl~nZE9Pyz@lKep}&b4PFJd@-xd%QWnKP#nEZjO7){qGtdE#KR95cjj|QPk^Dhur%0XfbXlm*jdX$+i8<dHJvMLrIr61})3P>+?FTmt#I=Vd2EN72Y^2uV+ZBj83_>;(0+{|Lpsv9shdSIB(*Y)hRbKc@;>UTSvxb=iF5>hhv`hvz{b>|5);hi+DfUo@1qdYE0z)tN$=1ol|Zc-@)6Zm5Jco{koO(XQi{5Er;B+5Ab+%{Szp8hWts!zn*+cRr+ja59jvn7Hwjq9dcvSk0tqg0~c_vtr{ZxH!S!2P>0-#YR&u0tUR1^D_dPTPFs!0WI5#Ks_%I{t$@~&NBIYFo-oeW<mTM<Zx22mjdVrxTTc1>n-zF_H)Q7AT_Y2>qn~`~<&;~2?YTeQ?H^U)?Oj)zk5g@_#_g-QQSA?I-yL_4bA9m10M2`aX0#k~^HCn&E_18ohW9DSTUF=f)!ZoKC-q^&9nQ_=0dhPR`!kK@kei;VgLwJ1x22tBTQc+Vqb?-39C9<DYiVA7#ZAep`sCu}uSdO$cFL=E4dnf@)Ryg<cYw#S=F{U`v{OFYkH?9%;JWl%i%33BwCef!xK?xX?PVS(_N-XW-M-%z;^m)wOyih;$tCB_=~p>-EuX>r&kXj>>X`fa6iA%w=if+<<4#)|nRI_G8I;d*$PIfU?|0))3t9it1?9L{dBDeV$hBdgdB2!z>q{PdTaK?m8+S%K<VLkq0lZ&2#8l?rFBik#>yFejSPr@2w}sm`#+~5Y_H2{%c*!@NbF;OF9A7n~bju+(=H!s$rPBn?t@SnJc*!=<+bOq}eCGXN7yML-`#ER>ufMx=*YuV{ZoC~L>)G}==kC#2xE(v>T}-G$Zng2^ez023<lLUN+Ml;Oq@`SsD7oo9xDqX|#|@Qs`d*Xm%5m4va>%s><IB_X+T=)C&)U6;al4uPxP3L(a<%35jpz{0^|!^6^t1ipL&e1Ful=U^IOWEvMci*zfrpZ3O2zxpau1N}3ne!XrjqYX{(y6HP&HXTrc?pTAvfPg2GjEHhyO@ERC2voATO`x=Jw9KymjZE<P(?k{&vSE=W(LuR=RWCZ?3abBwuu0_ItILsV#@x8uCc$OsP7Y+k@`P_)nhUPN+j}{9CsK_uIe<oa_BMOFM0Xa$63$w)#pr?w|es^1Tg0<@(kY!Q(>BwSyxn((?L(ry;z)&l|~c)bSM`?_cGIj`MM0KRnF2o^5%O>n?5lB+j)1QzgH$)5j^dwukb5cfTykxfMN3#^>=jg)E2MdUYa%`#C(9tWTd!($6gia6MOZWAAs|&*qNn!TkI4+Hvl>T=!Y1LvEy=U7Xi*{x!+>&Xe^FY?#Ax$c?Hx_p`Zo3g>$206Fg7#>oALl3VG2ugdM)V>vf-A5U`qZ*J(qx$E=4ay+-5BJC)-R&|cFvpY=kqg&+ooe`eVDL1Y@k?Xg`o}Ak^QpkRp{7pg2DZliZ$G>^wLj_)sg!`-khvoW6&BFp^eHI?%+?e4n`=w!d&2q?%s~7mZY2I1GxxRP|ucymw`6|>QH<~@?^Pv9w7|FMEm3F3u`&tgUw!IVIkC;yzaqdobRIZaxkC5YA$<0AitI+b6@6GbO9&K&jE_Zl8cFj|A<F@41c<0=_m`d8o9LKrUem-As+x;TBj+ti<bFS5^ApN{_Vt%Jwi_66QZ**A9xqEJy^iK+Jz7A1y>v=or&sM!Sw{wNcxSD=h?yHpCXtTRAuV<Jc-y35~JI$l`I{B--^ESEuyyY$J<a{ODKRQm%4@z#HugdM~`6ra)+%L5pM}4EYeyX{-u7q4a%<RIs>)VsEp8X%le1MW$4GwYrx4cS7{#Oba|I>2vdTPycbMEdmgpWJdI!n$!YToXc!TomgV_9CW+@ZWZdesGT9#eALe=9F<J^Gn**ZoT}FR`_doS&84b#n+WZ>($2xmCrK_3y9q`S+{5WJ^Ae7<0ln*H*rlyx3n-x0PJ;-^F#?I_E9lo6m>qg=@n1(%(vMpUxxeZ%35jd|Z9ZlPu;sW}RqMM!v5Tx9=V(_t|Q0OlTO&>p8!)w6pNEtWVqluG?yE-Q2)+ThH{p^i%yOvV6%4eEfZtr>Vg8#GYA1@~9ff|KRiWSNXhca(>_ZUg}PRD>6R+Od;17<0W@>j+NuOT1v;<j_M};v+k|*U-=q*-E6I{BmMXDFgZ_e%`4;f;D{2Ac{4Ar1A6o3lH<5=HO?XTuS%{(+(Umhl%L<ofO=7=oaK<apS`Qb{j<B4eBYNda$gyIgO4NKv%GBA#Y;SHUAN!LI976d=q+wXOa55)Q-@wsAN_{OI8$<c!3tj9dNE$|iO*y_WcQakpybw)IJy4(FhIuBqF=cm-MO~#`1mUKHKhIVo29?IY?67cIU8huE4h7spB%rtYRT`f?keLU=X*I1E4lII1RpO(pBgg1Ha<l9wc2nwpD4L&O(ALj$$r`XJUO^M<MCA<&&EI7Wjw`nll?irf_#sXn`=_Y{*5TY_1HdINxpAsoLo;Sxn=K{^T>xzQjaza<NfYx=q=}6H81s~I=A1T2IuZh)wn$?*>yQTDY-lCU$T7Fi(Fsr=a=MuDx$S4ujV1Md3nuelU$eF*(&|~)|B}GCAX$d<N9yT%qQ)XO(Xm3_9!0DYOa6qm-ee1lI`)A<JZ;fvW!DD5BgKa$(Vz3Jm7dYa>?@6a7*qRGF0RFD0kD+QvbI!k>lzw8AnFSNjyHyk!2(=bz9amvIn=L=I%X<`Fjoj>pZ^fHgDwkof^aAS<PK%8}ss}mPf{8<6bfzKKS$UYVJ<?fybNn$78wv-MLKi*i&*{pyc|SFgd@3@8#<_bJ`Cw4)^tzaj4|x*(y8^wao*$j=DD7m*u*)l<OlUw`#rPaj3m)%hxH^mh`gU@8075t9{wU_XjQ`mitLB+J~<r)!emYSq)y#<10D0-~24&#tP--)!e>6j+Zz8X)E_1hbzi_nz@a~znbgys`2uceV4B<%n>27A5&eF>o6sEPl>6{?RT%kxqCrY>EA|MWqc~Rt{bxan5=pEGv=AK;w~8{O78NTFZ(^FbspY6&vTMD`&X_j)I2Co_Iu#qT-?rOx9rDZ6Xbi8++Dl4EI)dS+?Tw`F3YzrC;Laq&F;x$zaOe1d4tk&zg%vvT<7hS+}<y_nZh}DPu|S^p#2`gxv}v_nWuerNXB!)=Gi$9{DzlzjT=$UDYqLGmUcq?Id^@mBI9tT&Ew5%{3Fl*xhAxby0Wqk-`A<R`)b;ny!^#poLix}r0!PsmF1OO_kSVd>P0EeHLq<ve%wpP%l(*=>zCK^^4hu`JdfqdKTwW~3BT|-RCB#yuq>bYA<s*hm77ZczZfk2spR_T<<bwax;N+F#Y+A%5BHmzyF6dZ`TC^p#r^fGmz)>#uHpVybN7NuvV636T5bpP4|a(%QV*3}UuMd<TA|Cl#qO3e{=6^AxKeT}?@Ae0{oAMH+&xs5>poQO2ek=(cwY179T_Jh8c03Ynh)i9jyaw(PC8~N@0joICH;e3FK|ohs;gK9%OSUeKVtb<lb@?}yea2}$5>v^ah})5r>tB@v^^8-m{&L>`%#OKyx<PGpDJ=6-<veo^L#7I+p9Tu)m$X&nX8@5cPP2r*O$kwW}1IeZdaX!`mk5}LCu4X$ad+iFYxn(sd9eSR?Lw0mD~<5CGA_KF7o|!XfD~`S=-CFQgU}PUul2Fj!WGCtHWfT^VVG%S4!?08ZP6?RpknA*N8llZ|)`EqvjDyWnB4qUE_SoTp3qoGl(m>Q8-q{)wwG-_<MiZE&X45lZ>m?9W#(yH_u4_^t>YDPRX?qtEHVu&1By3P)k{#$>n7|)x6PYS<juGJdff&GgkUx#CqumHQ!lT`XO=$=VoLx$%Az1XC=4uy^-a8BV=Bn(@CihrH9FWS8~_SD`dZ%d&hag{gJVHxr{?4w_{O%<__ZL8P<0z<azi02{O*rJfXhzjN#mMHoeq&)K4`}sGnM^&z$Rj*OKdg)MqtMsLxu=cYOTY*?i<Yj`M<=|94&(Uz?v3s^=GNc74wEk<aD)6*Ncs?Uv-OJ1>%+zm(km@SC*n(N^9^2z)K$?R7;NKT58pP9x(dHrkK-E#nBOx53lp=SuF%T2k&8nib&ZJ$5CzZ?T`flk>ik>mIjd`JuNtx6Tif<yUu->k1{;+eXRwS-ChL_rv)YGEUa-kp5J1yIpnJ-dvUQv+wkky!IvOA0^k<pO@w1c5!Z0cqQ`*(K}?kDY<=FuDi@VY56&l-s3x|+cyk3pDMX~@OYe0OLFesI#2Fn60RGSJmI?0{I|M1S2>Yfj@z3ZW!_H7O;3&MgZZktJO^GkMfz>wAgLcpZmp}u``7F_T;3nqzFX>H)Ok5B)x1R$*<X8ab8h_dj<+k}`d`fxuK%@LEBQSFGi;*l-vt3Oo|Rm`_(|HobCh%S{>7YqO!D5b(mw8wzRGcbWIjADd5vpwpNab;v%qeC-@$I6$vjB1K90F-(lS~9a;xPzB%a^7YWyVQP0iO9t<KB4Ts)8N%9>jG-5oCDP095(b7c9(V>!3G50>NV--&X6pyXz{*>Ydm^%Cdik|DBP1#WQrYVKMn_qkg0<ox_ZU$t4r74D<I%5fiU7JgPDaX)B(Ka#ql<W{>wa)0z<AV1gD2bPjNYh|e?N^bh6m3p%86Ti2jrT;A38$C)~$zAvTWjvf&$Md@h^CU*wmvY~z=GHNp-#EFAbC=fuxnFqko9t&L*GEUo`R-;DeokV%SRnf=e4C6<CD+SWll$M1E#>*uvDMPgnAcMCgn2E~e-h_*$#3QS^{rmaa>_%m%X7W7Cpfp(y_4g-?QkBSYHs_llzD&~A2`>#&XVu_OXl|ya&;ch-13ogy{RmpFdz6;UbMUPf1NDyy!wVq=Kqtum*Yjr-Dz*jaTgxQxn5+EycdUgJT*_4$Fo|?b6~B_B)PvhIzYZh$+cIhdAu33TFQG6g+gVX=gP10+*8T5kw43GobFvXx1Y9_ehxY%{i@{F+A>l<57px5C-(Jaa-ER<M;RANZWXOB^IGrQNPe%8tasV@G7qfe+WIJ-H?t-u<N0Ry+Iup7>h+NO2_<*u$u0A-ZF+OAe_AWg7e=g;=V?lAZ2m>Y|Ae{HPM=NO4|@LsGX9m^J~&wR?~Xk(|K0y|VP39Ld%i#aD!)@mo{x`s#<}ZucG-`9^QBHGxxQeFwEr{%|DOH03AdB*JmRYy&m*)98RdC$Q%}wlp0lWV!gCgF;TUPBTYc&0<I!?|pycMO4RU<_a80)3?cY*I^0$`vAJjbAJN|5?zs2qjf5!XuzwxQ$3FFhMDY^FLDd(mO%Oh8xi&+Q9^1QXxHCWywir7-zF|WQ#o?CS|DbJt#Czo-5vkSjBrRL^?&hp&Km6?wNS6Hyj=Vj1kK1<1s9M}2x&3*0Vxal`qj^C&VssBo@MGu$y?~_WNZ|usz^KDjvY*{Ub+`N*Rj|Z)B8qVDn>&rO)vO(tGl-$f%NRG!$b<oZwc@DJeiEN*m_c|ia4VV2O^V1u)^7m?fqvZUc<feNXw{KkU%emcr9*+Z8m3{A{9dhH&5I%osy=P1Q>M_s5nY+%)djx9!WIMNS-F(5hmVRqCZU^rbe3j$90`o#kK90@wy`(?urr>#^ukwy(xj(J%BRRKUA1lmxpj*bNl5545^7ol_cW|!F%gN8-T&|_^+*!$uR`>b(#)>;E??*)a%<Jur?&4uN<Yt-=@;;c)eOb?e3wXQiIu&_;X)(xiNN##na?GvyJ>>lp-v^Q_@1K~J!)4yu$Rfwx=p6n|xp_WZe!svBd0smIG0!7vpGIeN%B>Yw_&ot@$Vz!`gK=xz)8yxB-e8)%XYx;aIWE6=@p1|8GgwEma_+8uU5>Z6)#P|ra?SgxJjYC)U7j1C$tmLy?`f!c!h0G<r4n*Ixbc(hmvwhiSPr>%Os+GmCKEU}-qw?L@+On{MJ2aJHRA2mjP<fzqf$%1?fFKIdo_PLQ0nT23$mW0v!vto!TV`yp74H}H8GZRyPT)gv3ZyIyrbq?g_=@NhiG#C&z+vfrxteE$0;{HmE!v%^TSxFPoAaoB;GG(`5E$jGGRQAo+0yqO0MPC<@%%LOqrLxHIVzqZvE};P>0<5z9nBDTZgW5uD*Y09lgQ1`W~ZoI*#+N-iJJYOV&quuTq<SN7~ungxAxkP@KR2t9%2_H<u+>-{&+p-j(HNJ>%`S!aMT(ubLb83(I?|S0y+5JeL02(Lt8Keoxw0-Y+%d?#uFf%E^1GnNIP0s%FOtGLKc~2=6a*RVLn#YHpmJCH*vPkvtEd^6oCJ_kZsdEBSx#6>pY#GBZ_0ZpSi;OMOyuZA(X~w~J%tdwu7~bC13$WS&~dt>}$19wx}Vh(0~LjE7_`&V)MT#@YP*zM^(BE9chQ$4SPa7F=BN?iu-cg7y5Oj5{Sa)9#Y>%u<GP``W^*p^4k6(?ss8KK{h-ub5K{N?lQMqqQyV)YvcWSKc7=OU=vYNSqseeC0FVgEebM%koG1@i^Af*2$PSH<tF1_ueti&3cx6@7qPZU$kGU^LS3k&GwJv?*+m;q)fcL@mI9GpFi>@zu&ISmfYSuRrY%pgWFMaOTQrdJ?wydZ-FrRdxzb_`R^SPa<g7%8HW*#Jo$6f8_BC2k>^pTN6UCta`SLW8ULwL$@4}%xx7D`d8D^fZngU;<90wP&h4PVcH;eIO_f~BIbU-0v+-w;<k@|>9sBC?L(vYowdDbiEAv8A`QDU8l8&oIUF5p^SX&uaUb?*hujX0i$##XUk^78d<>c>MQq*Kub1m}?xt{E}SJubRmgjQk<Gh@5t9OLdzn7BhgPZYtz?N}Y+E;V@9gR`)xUA>8jXAj=w$!ns9dcu-o97qIjb1WOGww^y#Qk7Jg~<Kr@74J|IlJYif1(|7D|-d`yQI@CB`?#TuebCc`=oQqjl<EhT_Gdo{xxS#c`lc^?z3oz+$yw^+c&4r;aqQ>ClxPWCP4nKO3AGgak4%s)=4|dCS^;!T}G`xBtMXh`%%wSGObf?wfC04d)k_{I=Q>)3hrlpXu~v4xplZMFRwK$$hoyCYvv^VSvP=leZW*tZU=wArsl?g?lKQJskh{%j;Bk~PSpvLf3sQpFK?3MuK^3L&wJhsi2qT%(r8(<&Jl_J6p%vtm*CES3fQge|J9!YhLr#R{!_qy@#`=kUNzyh!8O5!AmTjmy5KxuKX`qxA2=U844e<_4{rqa2N#7m0T%@qhc^Wm2M55LfyqmP$$h~A;Dq1xP1L?`qIK|1w4T0+w#66QS_qyA?h7sm&kgql=LYA6h;@j#FhpDgA}$6Imw=Z9m&A6KfPVun0WJn_oT#0~Xq&uYqVH;m?<a4NXnh)B9m(q@TIYJ$4)QvQwyO@dmAqD>ZLfvCDG06s?+>m4?hF4J+!wqQegeD{d=&m1d=&f)p4CJ6890-NcnNSOaA|lOaA|Njd<Zxk{3CoZ_($*}_(AX@@B#R3@Bwff+{;rq4xBb#0rAQgufp)OU~(^T0Nfw$1tw1i4uI!}rvsCx0tdhgz*B+AlY;}`dEv>y<jKGRa2=iuOzsH|faigGg2_F=<bGg3{0?!2`2AQQUS;ByKVIeIl^I?JTn5V|<g{Ekyc#$hJOcg$cm#MYd>MEx_%!?&_%!$x{0aCK*w;fmvxhK=H~?M>8~|<w{}$W|JODlvJODfwz63lMybB%;-UYq{zX`qsehp9UDf}9o!Be~-I0HB*yaYHW*vC`)p7v99__yHd;6Ct?;67kCd>z;gJ`Vo_d>s4~{u=xgoW(;tn};xoI1pYE90>jn-WvQJco=*jco=vod>(iy*n;l{Ti{#p%ivq!G@jybz$D^AaO%rK=+hElBYwLo$16KLE0{bjI6K%2B2EEM1}4|QDZm~O{Ywt_1e2!$CkLm4h_k`7fXOR?vw=e);%@LrF!^L~H}Euwcq@D}nEVWQD>w!sz6-w%zKspMi_gTK5OFSe4lsE|a4v9ph`1TN1(^JMa5HcZi1;V?crf|T;Ge+DAmZ)t-@)V;!P~(x5b+E6zhLrQp29D{*&*UG@Csn^>fkb910t>iuMZ|~2(AMTgNW<G8-U4cfa`**LBwU@!C>;-;IiNx5b;Y7@mC(g<bQ!*g3m+5JK#IP<iCJ-fZY)BIQRrGc`xuda8HQ1IlLv9yb`!MxB^6+8=ezP?g7pXP6iR*)5Py+!sKVc_rT{N;%)FPVDc&8ZQ$t;ad&uUaA(w)?r;O#8{PtLfXTCiTY!Tg;tX&vuovo128cK{M4S@t0ro)MNeL0Bf{4B0>A>kwcf29u(hzZTcqlj&b*DK*+zTR}1D^(-hPpEcBHj)W{|S!)$Dr=~2@&6ih?Ao>Q9VkIx|9o?9GnLt4uY2lmq*<Rf{4F?h`YgifP0|sbc2XTLBvt;W#DC~J5dnvW{CI?cnmlOb>|O=_z^^$5w(fxQAX6IGT@Bh(hzZFxB)g$cPc}~wIJep@Gx)~>P|g~xHd#w1zrtY4RxmqL>vSWXM*Pd=Ri%$gwMo}A>uRe^WgKSJ7*x`EfDcSxEt(7-B}0`kA{f5!+U~zqV9Buh?_#hW#ARS6;OA|K*W9!aSC`ca5B`S6!=X14@7(ceja=tb>{*^yaOVh3!e_2j`}h;QQaY40v`_V4epJ)GaMpr2N8$BgTO(kJ0TEpPKY=oJT*8q>P|+8I6Xw{15X7`g}UPd5$Ax2gW;vYrBQc+A>y_W@sIFc;9jUZKSIQdA>uvo?cnXGJ9{AFOAzrR_<itw)TBrFOq>!T&I`{2&V#y>7a}eT5jTc^1O5her!hp_1tJ~^9|azTx-$|Yo(&OifNutGM%~!}5ubpF@4z2{AE74Q!Dr$W5OEQBX>e)Oogxr%2t-^JUJG0cb*CysToWP=h1UkxM%@X8h$}+GMd3l<Ak>|r5OGR~_%3P_)uX$pOJ~4$!6zZ&jqoktEvP#iA>ug@u?Zgy9*w$VLd0Dm;wJE>;HIcMO(5cO5U~#T1N))w=n!!#i1;yT6V;=~s7n{XkHMEA;=S-4;2o$hdlS_i;%N9P_!96E)SXoj@mPqsE4&@J9qLY3h`1F*Tn?TSoD+4Y97G%l5$A%Z2d78f$psOYf{4q)bAWT8?v#ayTSCNL;BCQeQFppP#A6`hU*U_vi&1xeg^2e<#DBvtfiI!%{0$Mmgosn4Hc>rFjk=T<oEn@DA`XU^1(!wL35JLpLd22qF5oVxJCP9aaEN#&d^UJC>ds7vcnw5+2z~;50(IvQM0^z@eha61^cG$OOd`$<5toFAfJ0DsN<zftAmU2!n&6tKJCz{f@(^(;ctvnU)SXfgaTbX9oricza7xsqcMx$bM0^;25_}SM=P*RP79ySnp97wQx-$zR9sv<|hIa*bMcwHP5jTQ}L*V7W<xqD*AmaQGaT<6ka4OWKH26&XFGPF=ei?ij_2o*Ux<h;&eh3~7jz--%1QBn7h-bscg2$rn%!Y`ELBt*4t-!5NcRE1CZ6M;R@IY`N>P}UNxFSSc1zrkV3U#LnMBEx8j)1oWw?y5EfQW}e#IxXIz++H%W<kUoA>xDZ{owtmI|m`+YY_1p_)G9h)TB4~Oq>=XE&$I5&WE~F03xmo5jTK01UE$8X#f#-gop>hhl7Ws?hJy6r$WT5;A_BZP<K{A#Css(v+%3ntEf9?A>w}^;!kj@N1xy&!6f3W5OFbhIdD1DonjDiAVgdoULIT?b*DH)><bZp_7Kkk&VoAh86tiF5uby{g2@kq&w=+s#H-<J!Q`{RtHIMC;=%9{VDir3!Qf61aTvT2m^=g=2Cf1T7lh{rlcxa}1gC?D-=a2AJ$j3}bOoGHcZlD^<KWl9*HL%kAmURH@oxAg@Fvuq-4O9|h<Flw7<d@!&LoI<5JcPw-Ui$Tb*B?V?1G5DgI5GsMBVugB5n^6cZ9bFw?^IR2oVp2h$q5_f`_8+OoWJkfrxj(H-a~!?(BkyPeQ~t{2KTg>W&Q&zk`UqJjAIU5tA1Hdw~l<#8u&y!Q>6VRl)Tj;s|(0F!>;G1h^kWJQ+R}Ouh;{8N3`K-UQzRCO-?_1U?24{|)~KO#TV{H~1Mu`~^<+=nK3Um_(c&BF+X61P7w-WP^ykAz}^g3-(1F((sx1IYfK~{s2sV4txcC93uV=z86fs8vGl01w=drJ`GGh7(4~sA0qAm?*t|f19t$|hloSrRlwv0!J**75OI2VIxsoam-HV0t2@LQ@bi!OO!-IrJP!O3d<!D}3w{cG3U%i%i1+|RyaB!(yc~6B14O(CA|3}H1RjLCGY%pi0ug@?cY$4~JKsaZJs{$q@b=*Ls5?C&;=vH{Pw;`@fv7t_LBtCo;`Q)fz`vmGtcQp#i1;G>B={ui&P9m$CPe%J{to;OHR%IB6MI9%{_sLz@~U8eumKU*f!70*M}X^q+e5^C;Qhellfiw!6CvXH@a16gP2l<9brA7B_%Sf~-{5`VQxNeD_%ks17w`@66Nvadoa)hgcs4MJ_@jr2_ygP<?2WoZOd@{jAtJWnRF8<suYhgvX^40~{5Y8WH}HP&dWd)dd<B?%3U~o{5=7h=-XBcf0o)htf{5$F>x0Qd!F9paAmSqM!eH|B;DowETnwHOo&iiwbtfY}6Mu$?AHr{eZ=voygotAy;v?__-~*^TM<C*z5b+xLBJd*Aoiz~ge291gd<b|5>dpj+cr-+8!h3*wpzfFu@hFIRJbW;CFzU{Dh<F}Eyc)g`ybyI~HAMV7M0^--fi2XX!w~URi1-2gCio`m&I5?}6GZIeAx`y(nA{)i11<^?SBD#5@;cz^;93xITX=ggc^`0FaBqls416M(d_H&#csfM9621;hz7M<-ycHro0zU;NzX3i1{u3g;27dx3e-FL}z6TLMgntB+e*ixO--n2=!=Hl5ZSZyQ1&H`4{4|(+Klmtk8$|pod_9<a0r*$&42XCvd=i+vFL*5Y2Z*>G+yy4D3vLIl4H4IXR|At50VmWQ;+pW{@M2){jNszn>=5x6)F!G&Ur?7Gg1>-YK*TrTvEW$Lof{DGIf!^4d?$D(>droh_&11nC44@3KI+a&h&T!&o(Uff9*w#)6C$1p5zl~+0*^x7nE??mfQVPbt4RY7&n(IQ_wshq|H|cm|7hM&OY$GPsK1%?weQ5g=^d>7?<Mdi4N}lE!}#;8C%*)Dg5HAC{trgdi+u'

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
