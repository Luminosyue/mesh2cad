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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8fb088daf56f434c9595b2d1e01ba2ea/part_005.stl', 'relative_path': '8fb088daf56f434c9595b2d1e01ba2ea/part_005.stl', 'source_sha256': '9f8cbe2dfb616a7afead006843ccad7c57ba8c5f0655710757d04ccf88af2190', 'input_faces': 896, 'input_vertices': 733, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07868551462888718, 0.07526223361492157, 0.13288864493370056], [0.06583569198846817, 0.23795413970947266, 0.25788241624832153]]}
GEOMETRY_BASE85 = 'c$}r31#}cw;O-|l!AWpiEWtIn4Q_=3MT(V0f@^>j0))XKSRuGBt|1gBL1v>6FF^~GrD$;|4uwB^zi;!uGwnO)o%c9r&iC6dckf)Ed+*$BJGD=r!BfG%lFFU|&q~#8sVL4XyW*+%`}$27Hqdu`mC<7-yD7Pa@BHV|;Evrobn5A*_$yPq2l<X4=;vME;@xm?UGGX3@4;jICiwLq-EWNFAYZ57s{hFGzTf=uL;H{Q{r0(BotiZ(S!$NAWSM69fBfhEEeVeBGDprj(=w;{*(Tq_w)RS#&;`YXuNJ;>#`#%!HPhg0vj&Us>WvEVPPM+uhIn#s7U9+XmE&Yz?|WE;cifsP!rR_HIV{4z8Y05$Bd?s7eaF3Yy7RLZm?*+qR@sHGFRCrV+dgXNW#8JSiU_YXDw-hve*38KZJP>-@YcRL;$>fZ5qnO2f46(ANN;E;?pyQ9X%X(|i8$G}Z0wJ6uvy~`{`74k9=+S~7}?hkKNP;A_Cx#yH{!mx*NOO*b_3&NU#%L7d`&wPFZ;@|sfcHiZ;ZjenMved-*-gB??_pI^c-<VIxQ8>%f9xcw<sS==V2(Hgh2Q;eMNfoGuh*0U(JzT)R&f$&JbRS?IO~nmdzJq@Q;)f_fzU*I|sij;(1#O@&A7Gyutt28||l9=LFf;I(dojYgc2UW#87N9`aLo0Pf$T70P+iJrTcFD%IdC=@y~=ls_Wk*SFS3`RIjEzXh7b%f3FVHOkZDvdEWptPj$Y<LW8Y*V8!J*Zl{Gc&t7v<7MBPx3q}IYM*I{M`=Bj^;JRCm$sl3{E8bz{Mz!>ak8&Z`c=fQ#@vsWef8-lluy>`F$Ujru83c4q>1>Ip~Vr;KiN?}Lw`Ci`&y|m_V<km2EXAue7{dXwCp>QI-tKTK8bREmI3~gp(6d(a5YZ$^_Wbe9a<7=C&<3q>Nm8Hbho1oeoY(7&GQQGU;f=85l_b$lyhJ91DBuwjHqARvCpXAjyHs__Iix;gs^|m*I(sCdpPpI5MJpWjsDrRTD0ujY$z|aO&+w{P1h06l?Eby-S;n}e;wn4W%uj^*>{9ve6V>3M;rXp$50=`tBAi_Lk}Z8*CP?{#jT=#m1!YJ&#=u%&&=-)zPjly!jF81_O@;(;yIg7q|?!R*?EJ1Hv;3s;*<p0*RT6w92?p?TK3h^=h5%h&P6&~ZGa!RU(}1^ZCQiwNO~#CSuNf?QTA<%en$H9e~FfT?XX)M`d0^050)8A5dXPklyim9bF#0cHp4hSyK15#e84jCeSO@+DA~6S8;SJCq5oNXPlsRmJEW)gfoR#+3KtRSag5xKadp{Xl+UNP;o`noIS$cx%q=haktKKGMA=t^nxNkA{S#$~C;2Mc<&!^<uaP~3Z&_Ll@xHW18~kO}Fz)z#=5wkR(*HFK^&8gXoa|eZ*P_4VOfiPfH5udopA!;gUpeM&7x~&V*Wg<k_ZHu`d2EX^girEEI_v8~wR5H6uYZj8vprw5>}!>qp*$~jMSd?8Mme0kCCbyW)nV|pH7iAVDxa;12LEPO#GiUBO7<NIX#b8%b<hti_kI=OuN_0VoJ@$4eYHd<l&2oT@#Ht*>pzB|JkKcx-xlyI#*Kl;6J=jXErs%3ZjF+Cb;~rSr+~PR#WM=wn<k6=YTwU4C;M8^Vmu$u2gJ(0S}nb}ukODiQT8ok`-%FpOp7)6TCv|SZcg`$GQ<<|1nqq1Qk2hx^~i6A>B#58xlyujdEFD~zMF~TTYto}HAbZ0(zV(-*>|Mw#PhM+-dNeUmS~LhKf9kO`?}{7;aju3Gx(0W4>5i{wL}^2TV)mUmASgX*Y9Bdr`txw$-ega1=79c0s4DXE0lkyd3c_NdBw`UW#Sr?XSa+=vac6yf%aCYd6evH`}<+MYHCINbKV>j=`0&9%16I^HCFbuMpMx5g32Zt!sqUZdBBKQk+N?Ie~ITpi6*EA{Q<(~*(J(ZebF^m_VsS%kp6`=lVo3czYp`X;ddhq;rC=h``ec;$`C#p<*8+iG~8F2)L(qoTb@L^emjeJN}xQyH2^%1h6W1X_Io_aq3Fz5*|&y;;dy=Bnk4&ba3SQU@$pF6*Y?HW`%R(^zSa5+>A1Es&fs@Py=brUV7ys85b4iz0MC(iO04W_jRuQy(;tsal6^JzXynIzU!=ir$$s6d0OotwDkJ_w=)X!n%=h$c?kJy*vvEIlp@>I&`XN-r)8!iakzb`)*|+@h3D332HA%8>8*>%$)|hUHN866}ZJYHN^_6Qc;!h11`L%ToiIIIJVTZ`CT47s~?CUeCpx?z$h&04A2;;nE%W$kmrj|iEi*WtYss_qwQX$0uya}GaL0yr~$U6r_I$JzLdpLL{M)qwPnuzpha}$$f-_mv^);VL^8RMyV6ZPIw#eBHeB;i}jq+tGhw|9)}D+BMNe&a7C$-e&RDdx2mnnlXK)&TPaOP*7RznVMzY9A19vyv#EFV{kxzQZpB<#6f_<_}%Mgs;`ghVq|0J4W_xk7pr0)-Or2Z#mNm<v6BLr0grXl98V7!AQ?pANYefzde~PM)vifauMQlzKqF+@R9qFK1be2L-_TW-&z}H$Nc|zafGki3;nL;2gH}|ul*vO8%m?T@_Hr9zV_=u)YqMthVa&ORq>pS8-exv$3Vo>w+iYj1ntM=tC`~vf7VLLvahvrNBmD7M;PKMahmh<dm?_N-c;c`60u&e4P1?UcQ1+bq(6c7x#0rRSt+yd^-3{#PObPZS@xBZIZ+P%<Bj3REkb{5(-PxAqg(q#_yRe_eJvAC<GxRi3SZAW8sqcp&dIXx*fJRX`g(MP?ArngVZ5z#7UdRR9r3^aQIwk{_D`%M#&`%{{V)RQw~tGfeXZ+Ij6XGZM##Qnd0sL8JKBaAe09ftjHg8`Xm3w*z^`;4?YvP3%uB;>?iJ-(%@gCvC;w!FUra~4{Ai1iedVnm#^>(qMEnk)$--9?Yoorb<Ipb?atL4F;fZ<I*_Fw%@7Q$~^RC)6BMjl+H$r_B`;2^S{d<oHzv48Wzai_A4gQJzXb)|sMaaGyGz{}1zXb+gTXr7xvfUr)f0K&vnHJ*t60-v9$0AFGulQxhI_t-b@T(O^_||vDc&L^>4!@-v!jBk?a#-Sxavu0`x47@c8JG_@JCQ8=)>^|+?^#b9e68ScwA&}WA`JdO56s&R_cQpGmqpQk+H{RK#D8QN_D9xT!~E(%l<@VxPGSEc-w?Fhy}rU%K1ZS)GPh;EdJ12?+7$EN4Oh`_Bfstv_f20{l#dp77VD#pFNCk>DUABc^GCAmD-FXizr0&7LiTN*qp+{1)<pe#ToS(4@=wHH`dYH=EAs|oU9i7#gzP)6+{X8VvF~U7D-7XRdSSf!c^KMftvN`4`5j>*p8M|&zV$;k%uA=Y67j3crXZf|8?Y{Wb_?^atzUPF{6;Sl<zp+q0QFw)q41TE^k@%VzheIBacw91^*ZdEMgEg)@JnY#z0@ciA^VokC()mmc%a?>v<?2u93uTTuYxhMZ>`c6`>~<#lVx8!hIP2oszijr&s;@3KP;8kqJI==EququF(|hy#ZW$P>ma|!-i!NM_wO?JO1>T#&lh^LeID8&;^{K=q=+|9?HJj&j>>{{_oEysvab~AgmNhP*)IF~bL?Yk)83#xuU!lO53ECV{|0Ecvj+&@7CKC%Q!g8B@YOLVv7hFhEk*W~SMRW1(A**nesh2BuT8<c^yQ81qTI%GMZc)=W3<7ay^-@ecZ|>JjtXDD^WuaEpV$S@!;aGteyBr~k7Eq?)99<mreQy-R?!sM*Zo$ad=}oa%f7XJ8|+&>xQczedmiw!B#Clx+#Me+`--C)%AsDN6xr8rHo!V!<~_UYYgNLq?=}qcbjOW7+l0S;q{x?=6Z3Azp{2rCZ}$=TvITuc`OKdve9QJ*m<Kk0j`_mHCh+@r2tzq9iI#n3^CzTpL-`chR|7AjzD`9M;&F6efOHl-gLcw1Y^%uE?q9L~>gJUq`_{=*&~Dqu+ht#k`+)XVqb2ftC>Z|DXU9dj5A$MVU%7Bgl!MYKKc1go`U>A+{|)7E8~w!^?uPUfD294^ehKaT?cZC3KV}B<TeEhG>^oL^VEwXWpCP<9I!2_^@n}2x?}0_ax78npdeN~yP|J)HzVc;~NWY`G&ERW)_C`CbsH2_K>k9uo_Dih+HBw|>8OHrjx5IYX*H8LjU*lmV%(D)!w~2Vx<i>tuYSR>h-xvFMO1Tww*;i|S#ke$kF~{?n!nfY)hIz>RGa|foX8^*deh~Sx9&H(8@M}Iry?naNe%eC#wvO&1yyC(4K0RYLi+lwoVW03+qZHY<WqFF{!n6%`+1GlGz`o(2{Ah1&UTqTf)qJ+NuVdX4-1qfq`0JO6`>IvB-s$Ntd}R;z2lQ><rO3WIneWLC1lkSZyVS&fpZg@-*S`qD&)arPgm0RF@z(p*M$x}EFF?8Z>_IvIbA5wIe?m!-PU}4d^VyTB!q<C^z&z)5>lE3y+KQvy=9q7nef8xA>=(brez0Z5Sj4}g8p^rK7}QI~t?SXQ+MquU@17$2j)$S>k0nRg4dLwrkl$&8kdIj#5Pnw+<TvRS(*HVfo$x;%M>-3wLOd0Z3SVgyi}t_71LZ$DAN<poMLgQCGteGV6W5A-&B}xJP`h)A>?@1fqrWYfXgByb&!atzeUA3h#$EW<q0f$rcvieby$laqBjOKwg>vrDFGcqCEZ4ce-P11n*4v9w4#&G-o}4;O_*&WVB43s}WsonoU8{vZXAa6|^m62@;o8+`|F@C;+;b5B;Nz>reZ%c|zK`yiBKwXp<1r2v^fiXpUt(WX!MN^dGaUXo8}b|MhWYH9TEbTvd!hZG@<DxNjb16z(`zU8lf8zd$i8Ob`-R<Y?XqwAa2VrEhUTc}<O;%90vn(nL$@HmXS%Nt<<>YO_CcEZqdjzX1dH--eES&Mc{8-nh?By%obQeF$LGR2!|xa2E2pNSe1fbgvadboe%9^oc7v~aV!!5G3i|O~`*IOagF$Fl??$D_zFMsm>LqhSyX-r%ToU=!2iC&h*K9-h{2xU+9pyt&?|Y^%6Xox<9reBt@0+YsG6`SxDua3Q>|uCs@Iev2Hmn5l+ps9sXAS%RBK(A=crI@ooMP~Y97a0A+u3E`dZIe^2e(CG9<(8+@b!*%5x;sf4C$OOWT{Bc_==dnrHoIJePu;sjQd@y*=1iJiS}kaSRU>1qxTXKzR75jU&qc~*pIn1VUZ}e{!fmGa?r7FtPknFP=xP@^``2D{dg_>&miG@FB9q1&qv|;p01<t_3e2?Iaq>6q{zN{B_89^9@Q@UmU8VxIoN&)L%kPO7l`ohRJ6}e15qypYYATq|BQ0pGATv&l^1y4>4&}SvTr+=MZ~Y?vY?y}-<T`z`_Yd4POFOi9$!62+;{UZkuS@0JQtK7md+OOAM1p5qE`>he~z~nzP7pu`bFpn)K}*7vqbpCkHtLU+XOg8_SJcRAf0dO+702a_Cb5Nc?k2$<L_pQ@{GTVd1=?FDYEZ)Fa-VRyApQU*Yv`OXLmvTJ*dhIao<NakzZ?v+E`y!Zm5ZNc)Xp+uhs$k+m^M{0>yo=d_jL%KMwUfAz+HQ@5!IAj<$A2zsuzpAkyC`Mda7o$uC9r)v8aBj&3!L;kDuD?+rsR9&Y(zvhbgr!MO1?Fh%zDD-#gUyFzx^w;uFHet+;_KYQaZ%Hh!hkzbp81H7kbdTgTb$M_&$cd<{ap0!R8@qhgb<?vu4+S@p7gz$R~L4GfEVEQKw7x@~ci~MRY$EV1?Qs6bxk++&5yfV}e>HN3{&$}%>hY7!EsK~Eo(^6z#KRXri9LaB&ee0U4XwSKGqd%R^G(_YpXo|?M;?@}T+vJq5@MFD1zN|-oN4~;)4-)m5>n6sr<&#hjb@E?q?2LCni^C$^vn=OiU#WFP_?9KxVrAb}|7USu?QUa(um4;M<HMTkhWH(4ucDkMPB!>zNSG*3%Yq3hhWmQ%#r{Lt83tc(J{|peUp~7b{JXa(mpfGqzFrUe`?js$8GLKe8rY}KoGZ={Pn(Gtm*RF~e2(cksL6kno26rzZ<GHhXFV>%kS70GFZG6s&y8+~^0dv~YVa-f@f_C!)8V-j(qowTJiP5;v|H?dxO{W_NegdkKQ7<ge$>ML!<+m^dv^Ke_MGOM+Owhsj%e~9{Y8uEH$nKO{$*=(bfWld>W^0YYk%RJ`)}>?lSDjSAB%F(hHf_a%7G6^$NG%ucYC@_7T>SmQ-s&IW;iGN=5fa5o5vZK|F3bzb6f!G(Kzn8eDk=M7Tz@OSpz0d5&1Wbt9te-GekV5aa(;*c&7M!RC?j7{ni<L)gS9Gb-O##-{76_wZh|34jsP6%D(ye;_}VUm$Z0H&lhXZxmn_~>3Qe!&Ck2E@TTXTerd^U@!9m8RqEWBEADT4UOV>Xo-fkV!VBflJlNo?wQryt^gKxadY=X2v-@gM4$6I;|8n`}d4<b2&nsNMd0wH-?GPkBo8~_*-#q_u`R4hLqsN3rLQV5A$D=okMLZX~V7&DVGWgbK(P;nA3!|UD8@yC}j)=y1-tt+j?3?G4Y2i)tNtbV)Pg=fMe-Y_0&3n^))4bQ^o9DfbFlCttZ<<#t9uI}DoSHB4tG^F4__mLG(Qe#PFWL_Ka^Wxdg8E(lXRPd-*AXt?ypC}B=5>Va&GKNR$GEO>`Q~*^nr~j$v^*tz^SVhJ9=k$(?^7(E7ca&ce7)B~j29jlPqg@`l_LFnRE(1^FUHEgd7bF;&Fe&$Z(b+b+=s6c_cg6g9p1;`o7TTB-@N`!3vXKg>i?`+Ez;jUkBHxPaX_r>D~AW8eN<_NaiCJz8u9t+BDDX;IM3+v&HDo`-@HHI^3D4L7I*ix!Z+<d*j6M8-@L!!^3D4jX})QHLyhmVPNcj3K&&rbb&i#NOL!yHZ=N4eZY?&f7i!+OiP<82OTjxRhe?NHW#7DC<nqn?MQPzp`$e`XsT<JVjQd(H-@LEo^3D5NYHHq%BAs!kQNL|)Zo=hj<8!nBbDyMckxk<7rhPd_VSnM<-ZjPi;W3{3F5kQ#=<?0`fob8*`+=#4Hj8+FEs1s9A)H%w`TBI6UsO8>p#9u9Cw%k%r^`3*f4Y40{-=JSg-wJv@2|ezAbiV%y_i3@$2jlu&HKY?zG;8h<(v11ZC)j}i0^BQMSk@F&sf>Ftl5qC1@nJF`U`j6f_7!x-*)-t{cV?T-rv@J{Se-?udZMITlm&9SVueD$H&UPd7t0qoA>!$zImVDdaLhNQ4TNMu%9;dbByd;t)o%D^LC>>2L~g(>HURTDopt1_aiRf{C>pco8OOEjyBmQ;(fYO<X5?g^KmZU{2s^Uo8RNOeDix8J$R|`wXcC9{ra&#V`SgqgL93#R|MiIz7OF|@24y=9@|BFOz*#3zWM!^%QwIOvQ(Wed`E_Y*muo|alqx9-`}}>^ZPrOZ+?Ggy>kTN=cW_sw`_=wG5DtUi7sEwhxw3o$W6>keFy9izUjTE%QwIGO!H0eJ(U)R;Gf!x_BILUXI;MeJ+I3*zvoSh$Ml}p<(uF0T9XnH|C`0AN5|e6*|+uGjd7&(M~sI}w(S)6Gru3F|F8Gs^#ApK+~u3zkE^e*3SZskgY*o^5G(u2N{c85b<d(0**CxUPYa(Dzb~@%Di~o1Z#oa)^3CS~^n7!63Ey;{LGOB5_{#p1*ncQCDn|Cr=PT0unR(HE?$?Ph#A7;l;quMrF7&_`!dLy0&~A_3jgfux`4E?HJ|E)p|8+jZtLJVJzv*0xx-?4omIggh?+w0-k$ojR0_lkT5$A$hd=$R*<Y=_pkjNO>H=o-{3vW8NlNR1|ZYRw*o!fEw=5sq~@te=><SD*K<im9C$hLi(@GU`Ku+FVeAx8E!kFofCH30X$l8SiD=bdK$Eqv>wd|2Og#(NW&Z$5vO=9|u6xqS0ED@%@Cd&Otdc`%o6J`a`_-gF+!QNvI8%Gy0x-#y9{WAGOhM!E}b!nuollZ9_SpXOM9Q~1`<2=tfD(_#$1>0DfzZ#oy}^3CVs)TA8ygqqIXX`MXao6h^WeDis~wD6{LeUA0jg>ODj=<>B25jbbiFaq^b<v8N`$sgyI*ZdeG`{whFF5i5<(dC=ZH#&;lLV8T+C)4~6Ly?}P5Ab}+k$J!PzUkbi%Qv6fObc&1x2YGJDtz;KQI~IfnGNaKoCD{6uLlbMU*}ip|LgoJ{ePWbb;V;kzpCDO2;X$h*5#Ye*}8o5Ia}+}EFmJ@MQ34rUO6^e_APNC_`S+#ADpYV`3T>9uGr<9&lRVIH=Qd^3vW7CY&$(e__pxo`2FvlHqo-LU+y5%qkrg)^Y%5ugl|4a?efj%s9nDK9JR|gpQE<ix`y&Go!@r(mgPM6S@33(?AyZIp?%z}A1V9lihnTwspo_FU53BlH^uLFG~E(y@C!Uac{QIcRP}9qK*WE-7r%?C_&!SZ9h(>6epmMkwOt-@0PS?Vs9%Q?9xeNt?-QiI?~x?gS06q=Ij<RLh{vI?!+GG>eeiq029tzuK3DJZ&FAV}zWH3e%Qv5^w*_j#x3oBq@+p%XCHtDE7s}_>CFHwPDEvE>F+bb4BTDv_iFS<FJ-*_6dxHezYvyu{!!@Ty$-eDUAM~G;awz9pmry>xzeB!8cR@MLeT4h|*bwus`OBhZ-;tp+>hEq)lI-hkX5oH$7DpQ5DOnryu~Boe4(n4UROG|-dkU9t{i!|1i^}_xWM6$gpTDmg5ow4=&5ZSRD94jdJ%n#-kO99dnKUF?_Ek^*-sU2HkK^*K^@<_?CGmHcZ^?__6YA3rqF-M)D10Rx&m$$JVYI;yJBs|Dza1(2dT?=!Kb2}H8T{pVe(7beqaD^cEqq7+p*Tk!l{rTC^%;jyKKo`Q$-a_M66MowRiq(&Q5*Vc_1sAR{x`zcUZvvqsyFgP%f4-92ehZt*`s9N5|7`@sdcj@$-cEWeqW>&%7p#V%^nAZHfn@+<$pg)_SHIf(N9a)HTYWo7x;YPmLVP`_iBu9)2rimb4M(~x4o~A-|7E!BU<(?iA7NEExRWf!rwT7^at4^W#3x44t~cwt^vv?x)kEMw-f#7aafe>JC<Tzs2vz+^iTIhJ8OL;QTDZ=l`;Qu?<;(5wKx2SxiKHAw=_!jReL1HlU4Jve^#L<%JX_=%qQm^jFx?^(p<FH(G`+pUoF`Y=cngAjg)=GF9G#6dI;93pXb5fHy-Vw;OuDGcXa*}-+x;u%HV%`3IFRqiL$S6wIcqT!6?u3`%unH92ocN^oW*yZS+L+$1AO(WM94Y6FwLJEz#hg{hQ~LbUb(dj>dh<cf@))TZL%Zx1?r9eW#xgCHuAj{65z5YFnc0D`n<l{`Tl8*3*S9A)aZcuphMibCm4s)7PRsPu*hh9f|dkj>-OsvTsW%!1LTikgxT>vmPsQy_ysy`|7kk=-1cVBsS?}_^+-Us(pFCR^i*9zFk=rPi1g_=|8#RG@buk`rrS_m0>>rSO3YCy7g-R|NbXe=6_4WjBnR?UQQlH{h2(B+?P6n+?V`4wIBI=a#Lzga#M1BYG-nNay4puay4=}YD;oCav5qPav8FP+JI~!m!>u(mnM5tTadlURjKXBRmt_JoyhgbD)mRQO72MgiQJLghdP|xhdh+(PaaAhN1aX{M-HIQB?pk_P?wPBke5-{ke89yQ@4=UlXviPatL)FIfQ(SdW3w8e1>|Ke1;rLjVH&FFH*0NFOqLj?~reipHN?rpOD{EKat;))4M@4yMdjTlXFn>l5>y?Q%jHwlgm&mk;{;)Qfrf|lIv5Ok?WINP`@L$Aa|nnAa^47q7ESUBKuNDk$uTysguZK$pO@v<N)$)>Pqr#@(Sv9@(S`+>aXOj<WTA<vQxvzq2&F%oP3-bO+HSJpeB<e$O+VI<OK3%>Rs|>vV;1J>>xj)z9&B-zoBMG2Yy5TO3g`jUQW(RuMjya*@Ie|>_IL@txPUP_NLY)dy{KWTaasz8&f-z8<X2m`;yy`J5h&{JCS=)$CG=J2T`Yz2a!ip=aWa1CsWsuCzEGVcadk37f}zB7m-&`&yrV=w^7fNw~_Zz6Uh6>2dF9J1LR}Wi{xYEFzQuu7&(G^og6`qrd}aOlkL=0vYmXAnoK@PK1z)zA0>xSW62@pJ=D|WJ>)IaU&&j@%c(oa%gI61RpcPDMx9G`>d$12JeHS}hf_zAhm-qJ2ax-byHS56cO$o_b|AMWH>I{BHzhZq)+aY0`%tTreaPjhWy$5qC8$NnCCK@xdC2+5*{GSx*~o6xf84-s<d1I9zsVoTFQ^a6FUa?)e~|B!Z%{9iZ;&rg<H#4t=cqdQ9Qh3ODESQeFm*5aFnKq1BY8J@J#`V;sf)?$$?K>~$m_^!c{zD0bpd%PIfy!)97NWr6UiFcpE`o<Paa9_Paa7gNd1vKklcsbk=%#ejoOObjohBvkldc!lv<12lw6lukzAKtomz@qo$O65K=vkEsJX}%a(-$?a(;4d>SqO<o1BUIlI*;k{13fH<bTL-seh8+lAlwrk)M<AQIpB{$hWD9<lE${->wvDG&PYNO+G<AMLt2^MGYnIB5$N_BX1-JQ`eG%$qT4U$qUF+sk6va$)l)~$fL+s>PWJc+=V)b+=bkV+Kb$ZT$B18xhA<hwK2Ioxe&Duxez%YwK6#$ITy7oITtw_wIn$kIV-gUIV(9kwG=r!IXBgdoSU4VT7{gST$oyyT$o&e+Jszz>_hE9_93^X_9nL`ccl&{cP00yjwbgfkD*Q`k0DQ^&L&SI2T^|^2a#7$*O6C{H&M5fH<5Sqa`Hjye)2)`N$OGZNpb}BG&zENo*F|wPrg9?jeLQ8o%#p)I{5+hG5G=c74;qY75NJ_og4TIIjb8qJ2@-agIb8}K`u%yO)g3<N3B9GN3KDwN3KC`L~TxPL~cX<p4^7qh1!$ch1{1qh}@Svlsbkyl<Y^HO!gyBrOqNxCC{ZUBhMu-r*0uHCvT!2Aa5e?qn;%1BOjwik&lt>)FiT<98bMUjwfHD-XUKi-=aPx-y;7-eMkO_{F<6R9r!i*3pEGXc{w=?y@KQ{<h;~U<h<mf)Jo){WG`wRvKP5JwHdiOxgoV9xgohVwGX*9`FrXR^7rJPR6lZ0@<8eo@<8$^>OAr&@+9hN@+9&M>Q3?u@<Qq%@<MVj^$a<fyp?*6yp_C{nn>PD4yFD^4kaI_ULqeShf}YS!^x4<8{|lG4E1+%3^|H=nH)tvMZG{iMLt1IBA*~1q{fjClJ`?}@_zDm>JjpG@=EG%@=Eez>RR$*@+|5C@+@)ybs9N<Jcc@fJcjH`9Y*#g_on_t?oIAO{ej$t+?Lvs+?L#gT94d>T$5UbT$5amT83PXT%1~%T%7Dl%|-SkyHhig-N_2|gBw^OzjcE?C%+{>rrskzCf}z1PQFdPLQNrGAtzE}$cf}gYB)KPe1dwAe1aT8-9`=}+o-F_Hu5U!9P%pieCibPd~zUl9669YfjXExfjpern>?J{kJ_2skKC2olH8Ttj@p3Sj@*P=jogInLoG}8Ay=RlAy*(5r{*LVC+DMPAm<}zqkd4p*~kj@DcN~B`87QU`8D}3>Sgj@<eSuU<eTJ6RGoZ@oIpKJP9R5750InC;nbbvaPpyV*IufPx|3`pucB@suOcs^E+;P{Yt(sUjqFFALiQsMq>d*KB=?{WBljS;rS>JaCD*2YPp(a_L~Tm0L@r9LPcBL>NUcULNX|<wN6t&mNi9RpNp`1N$nNAE)Y9Y}<UCYwavpL4YE^OpauI4hauISxs!Fa%u0`!gu0?J`?L%%u?oJ&_?oJ*+9Y-EO9!m`%k0l3E=a2)*3#rS<3&|^~>&Yw0o2fg<o5_24Ir&#=2>DlX81)!Aj2uZlLyjcJQDez*<W%ZKaw_=-^%nUC`62ZQ`62ml>U;9v<gZlcd#11a>|}R0Xb!SF*^^qB>`5+0EkiCwE>EpWE>EsWtxv8=ZcJ@KZcJ`V?L=-%{(;(y`~&$XsxSE`@-XUH@-XsvY5;jWc^Y*#c^Y{hbp?4IIheYY98BI!4JA8uKY25G11~4<p&lpiAs?YekdKhhQWMB$$>*t;$>+(bR0lbge3SZ!e3Sfu`iA^~{F3^W{F3~M>U_`iiJzUEE*;c^oQ|BGT8x~XoS*7V&QG>bYmhDEiqyvBisV|<Hso65M$}H^M&#zyUgYNF@2G>w-;ujhN0Ymgt<=e6D|rNUCV2#T9CZ<S9NC|`g6vP8PTfYHPM$;EN1j7oN<BbcN?t}iMqWl<PYollCvT)ikT;SyQ=`e7$u_E;Y$I=?o+NJ~Z=fC}Zy>LuhLG2hf1&On|3Y3u-9lbMo=sg&o=py<29X2F6R8^6sbk3#$%A=0xj%I{xj(rFwI8_$xhu6BxhuIHwLQ5VS*125tK{0$2ISi0YE&O`HF5=Nd2$7ENoomlNpb;dK5_waZfZ7iZgM878#xpCvm4a;p6N3$C%>Y;Aip9%q24DyA^%CeLH?6`oqB<Mo%|d19QikLEcFaImVBCen0%Uih`O76h`fusp6t|h<Xz;Q)V1WD<Q=@6yoS1zyoUS>HHiERc_CFJFC@>P`jcmnf2NKk|4bfD9Y`Kc9zyLy9zwQKyOFKr?$q|=?&J>CrsNLf*3`P>)?}4hovf1UP`$}@$d#!Ua%Hj?H9y&lT#}lbT#{Unnu%PHoQLXs&y<Isot%aGmh8No>_&Y~c3w{YNber`Bl!*WHu(+t8TBgp8Tr2Qzwe^%^K$atZ`beCBx(vdiEO7vlkMcg)Dz^x<gL_Q<gMh@)Q#lT<i*rr@?!E#>H_ji@&xKs@&vLkbrji``~%fW{(;<#+J)SVT%FpAT%BBuT9aIi>_IJ0_8@1b79wXRXQbvMXC$Ym<|3yjyHT?#X-j#*3N@?pzyF+^j+$Lb+d2}Qfts6~ft-n&pPY%Dg<6=Lh3rYKK=vdTr}~hKlWS00lWUNhQ@fIzle<y-le>|JP{)vmkSBh-I<<F8=b8Th^uG-J-+#_APBHus1kK+x9($F)>HjURv_r6++Gli@)3?G+Cl;60ovTXae*k)hsCo'

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
