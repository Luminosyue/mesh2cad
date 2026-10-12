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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a32b2b119948c3b905a21db1098f45/part_001.stl', 'relative_path': '25a32b2b119948c3b905a21db1098f45/part_001.stl', 'source_sha256': '0955b704ad9ac9c795cdbb740aa5aa5566fffe19a59215fa3f504bb7a668da9e', 'input_faces': 776, 'input_vertices': 504, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.24669249355793, -0.4703822135925293, 0.38636431097984314], [0.3106309473514557, -0.3933101296424866, 0.4885684847831726]]}
GEOMETRY_BASE85 = 'c$}qt1#}cyw{;aZxCWPL+&z%s%>)nbFaa6~gFAtsjRy;m5OhKscMmSpxJ@89Q5ts-GU%&Ydslx|HT>WD*L%#mYwx?yt$WWoS4z@rTKXnW;UVE)L23Kq4+os(B}tU@l7|%FKWs$bp8mtj4H^<COPN(&{L?VBdAnvUJIPXjG`4sz|KUA{6|Zh7UbDA%@iLa;y$25)F|7NbZi9#Q@)vr8?gNJVEBf$0-G}%q^%7Moc$TqLE?LGh-txcvmsWAXu_E+R9R+Qz2gUv+d`cRcDC$zbEvjyR`J1ZS##vO|dT^(zyZ#!c>X!5u(Z1C^wBImG)g4v)sJi9v576Vk#i;s&mkDZp!6#L>PVAz#x30{I{`X4JYX4PRV%!{gZ;QIKa7tCT99^L5&i*GbZbU9scYI%`>h|4!s_uyV740*RhF%~&`d@58`&l`mr+ujUV>@0>)$OmgtA1KWKUH<tn)2u;Vkg=c-iv<vRgBi>!5W%L_0#g+Q`M!Bnc-(-Jyo~AsEPJ%PoRBJbG095=ep1xA*$}W{vG2ctEcL=yp_<;j9BRV+o64r3#y;CgD!(E)$ge4)<L<{ab32K(CwGef2DPadfocHwA$YJr7!Xp+Evw^b6xOrPc2oq1$09{jl(d%(<IDGjqb>2#jR+6_Lb_7RqhEtn+!((IXp1#J?OS|<y763?KH+c-3$6TU-VNaO6^DT?2CCh;R(Hk_ieo{1s%t_YG_5gPsX618xK|8?sZ-5$1!38{IR{kx>^>RsMl@B&mgX>iC7OECZheluh<vWOJTlFPQiNU+#BsH9!2}uS@7q0Q*~UaV0W~Sn1lR8?nnMFy;ODk<hf`cFdlyH$cXjhAB=c=&&B)(q``XI6N+&^g~zLU#e=tgrrQT)h*8HI6NdRMdBV`%tee|QXGZ_Dy{2pJEsvK%&)ORE>wN_Cdwv=E@BG-%k6G9H(R5c>o1eDVbaQ)4o4c6D$a6SPwk}8Bk~$&JT}xnn4hu&=jgw*hq(6i9?N(r&=gSkPU!PX*2<XcnV;+B0Qu}dybHM-9cJ$MAE7s?URT#HOR<$3?sPWh@L2J;@hV%*gxXij1m!>-!mN(?V8NCzh)1yMd&va*8I^%r(zQ?d`Eem$T&w~5lza<{)c4%y(Ubjr%jCGj#8`_^cfcAX`VV{P#LtMd!;AcB8<gM&iwY_ENVYJ`76yx4oiab|63jdGf$3Dup59h<NW9X;K(>Oz1(@$VstzU(6tdER+(exDhNm)s4Zx8mzdYf>;FfW$V+12*edQq4cTLAjGx&!eRzli=ra-g3L%i-t3E9gHY6VBU=g)#20H{j>;p@#gMb@#r|^tR{Ye%9W#xs9qz;dc`By1mzK++S8rRduIl0_L|uHLSPZYYn>9ejf9Z4EIyZ=R~w0B%%MA$8o-8dWiWw*BW}>CI;PEs3P<#cAR5xp*u3pNB_ebVqX+}fpPcEGvvXnYkAOgsoEAp9;DPSk%#hsW1k)vfb|gd3jW+5f^{|N1nz5hKOjHh=dd3~zrj4t{s;Z%!+qbi>W4wMA8Uj4mU;o=YWW5IM>oMf{n`WLe)<M~wk^Yb<gNqj+#y|7^LF47o(G!6qkZWV&^Hak`uR~hQLjsh53qjHwK24J1ywaXC%7`CRCQZyVYMIYr}glE?=PzED7D#;XS1&5S<~&O<{S6XlGGTt`dsAGu^Rqt%LIKwFXSPw5AKh{vp|pBi9AG9#r-R<2mIvoq4WM2ti%4fRo%MrJI<3mRdH?{E`U5N*l1W+mR<$n|G-fAQzISvZ%_#OwUp@R@>%T1l7*4yvJ((jhz0(qFQV$sTPKa{kh(qRsJQ>8yYC|}p*ylhVf`dMz<oKe1mfNK3g_Y11kA5rN#v(QBefq#{7gLGJ}QHLM&v}i%W@^?b?d#LSp9l)>)(#zTxt@GdCyZBex^8u{3QP!dH4$561N!h)%{DnUYB}w#k!jN3HfYV4gHM1g6D@Kg>g<M)qtPPcVoT1z;mw@UK{atDUZ0`eNg*%)vJqsG8D#rcH1uOqqII4_iL>2zGl+h_ciL)BwO6i+H1OdJ->kNI<Xz`uDuek*KG?{!Jqz(kk7CN7<aS_{rgvhpAUTD|HA%=i|-@OP0i3xv3EEh4xdH-hqOSR8#GkgyJlQP9zM5*KJP60ue)B=t<JVshfS|w-ar0@eKf5-{9m5~=lKUb-`e_gfIrW^ApdeI<lna=^m6yH@6rUq&$6B1XPv|7r&4L`yYXEyZn<vgXT;Wcz3wWIg!4+yfc0$ahJG4Y4fkcMj}7?`yN&!;35?h4mKxJz_3PicqZitbdTD$PG3nYoYPxH5v$&tN*L3%O?Dz-rur#~+JmbiE6YKn5Klmff!+Ln^gMD|pKgM1D0sXIN7_ZkQ-#5rl$3?i0Y#4yNc?MwI>r>SBj@bjDr@fAS<e47%SvdkapAWV3*)?S(_7R`ctV`F#>vj9l^mtzFmJR*)4uJor=XQI>K<FLkVExSNfc(FK?tU+BJrV19={WSC9sO9Af5mgfxbe{Q6;yRsSX`WXeGxnQzwrX+_S~oNGu0&c-#e4qUMk-g>-GtBYlViY?i@8ZUa#Bldf=R_l4NM_9G4pVi0?brzb7OAlWJrAG}?;&wS5Z4owXGCDbWt=WWiMEi#;)JT}PZ=w~bwe^YBP<)gN2FAdLIRcjNhE(%t6|bz4xaxSzGxbocr5gZ*>}#r!tfXwY5#cfp^G`LHkU%rxZ9TEB<tzy0Ja=pNgUH`iZSKQrf`pIqHAkK4SE=K*t(hi<bmFV4>~dfghc7we?nd(3Z(VC1>aN8|e-b$jxTSPw@mhW7TgKF0S2kNN0l)g<h@d5vTBx;4um(1YVu-S!c>t>#Gdb8VqPx35fv^R~`u%vVGx`k7o7agFs((ChZ=fjG}|<Nhd3UWopueSrVtzunU7&f~wqpR%8Dp7aVc_~YpG75Q(t2;+KP!2A|+LVvXc<5sX@9_LKO^YG&3*e~97FmBf7SU+R_MElQg(SLLYgYLSNfO9EehT6ZSOE~&jHWT?7a|C)y2mF~;0Q1;50{ih1bl0P5SU&?D=>Pmm#CzsB^s(Cwx?|caoJ)0l(f`&}hV#MtZmdDKtgC`NAHRj?ieYQe|Er4FkH5Z-(d(|HYw&aPYn+Ge)*{ch8Y4diQW|tuM+x(5ORtXW@>&OfF5Snz9-jj1D$jc4;leho|2tLV^tx231oGCfrlGxdUb)_%!+QJ1_S^Ge-1}2iT{-9xZ~0in^}d}!x2^aK;}(Bq&|O>0;=I~gAN%_FM)-d&3jW+(9gF?53FGoRnD+ea>bC{$qtYho_m^3B-|whv?_cKjnr?1yALWnd<V^E%-d5O#e9o_eeYa^O&Xe$6hWnZ$e+16qo{@;x*B^1^xrFDdMF-JOz1~>Qi@GH0b^C5#=#v^@-PSr{xc_SJYtFMy<oWOptT#Tl+cqD=JjPGNKAIgCZ_xX;$9-zuL9DB)r{L#}?#M$(ZnQ5Kh5T<=g86OR$)MZ5w!-}=q&VjB-9^KFU&{Rm=iz~9^mC<}@jZgNy@qT&CnsD%{~NL;{x{wIJ&n4nVTrh(wbyj_`*QcI$mi_YxL^1VM*izvgP+}UVjn%l`>dv0nq5G9pRdS6nj1#{bG^ZH!gJ`>SKf#>^FIdNF@HzAKF^x&44DN#Kkmdny?7J;^ZSzRIiFVpVlnQ>*;o%Am2tl-kbr)6e8Y2fo(9N|oQQrVd8+=nUbHvp*3#ivZ@z(Xdfm|^0PEz`GOUyP(51-J$WMuzIQItMg+AdU*Uw@+Z?w9HyxrLbKR?vMeZliS+P5gD`s1+f#JuEu06(+DAwM}n@O<(QbX%X-=zrpa7`<-&av$rk!VNsf#y^DrmyaT@&p*`j#I^D<{25Ucd3c)IpgZe$;oRHYCBdL?dWiG?WCcTe+wCayKl~`ptEo>gFPmPVpTNd(dfiz(4)bCQ#Ch1{8T`DO2kYcT7o$G@JJwa}Z#bXJJV*btGpOw?{@YdEdF>^iPe$TgeU=jIIqC!QqkT76um$JU_K)ai-HteYdrfyu+J$~xz6M=8ho#P=aL$B$f}bA?8K3t|y8At)!)Jr;eBT=HP1V1k|Jv<we>qhQ=UZ&bD{6bb?>n2=;eUqos_qIHj{9$$=g{|LMEk2t;3vQPS(ju|b?v*KrDSXL-zAHxTe9N*tNs1LQaBs>8B-4P>(>hBcKh5Ich^mv15b)zKYHguKT-2=-d5Wluh(tq8sj|VIcZr}K-Hc0`pDa<U(r73S5=pe<}sXmnr^F9Fz&zU?mTPyyXUb6{ZLU=w}wX}4+BeL9#<4YTwOL9-bY+LOTeEszvF&4{TcRq$x`S?dmoHjiF~Fjjl3OfWqfa??rQxc?q|9*=AiL@6j&bl9P$|ZuGV8bm-<zJeygS0zx3seLD&Ay;wn`pUaw2Z@SW2U5sBxe;Ht>agZq45t&Q_=s2BPlKLzbG^SQ3AH{$Bo6z5fVs~EkmomblZ&fUJ|Ak6#pe-aGsd7j&Szu=syS`Fj!{ZV@U9sb|0fw=hHz%_0@{5)0@aa9g8oU4`@wK1+&1H6|l*%o8aTffHoTpEsZwQn8li@LdR-X`@+(Cbq8P2{KPZ9K0wwZflN>oAWzmt0wXLq2&PN+U`ebjf26=JD}CoMTDQoqn}cKdq@#8}+E<@V{;AIK6K3JC1SRjlg;PXMOm8xDw98=&lCcF(o_Z>yH$1dR_awjP||SI<W!zUr+?=>h-Qzy>33=%(}L}?3a9@H%<fn_~m%L?%My-upccCTEqWB-Z<y^Jx$YHvqF&1SNJ=cZBtvres`p}1pgB{qo4injo<&BzoR|Bdt2VD#Pdd<uEuqEtQW@J-xK+_bilb<?mgDwv%ctu@9*0A;Ed{r_8&06u8@W3Cv*VXo1Wh^-Ta(p*4^I|Iu1fVhkUSpDo0?yoEm00|D_gt@jNzr1oV^n;LnvRSkEm3Fz-X#q5t94(7y60`2Q@)FfWeM6EW`7VC3P!aOB~Q-LNmL=ll}%x~tPbjJr|Bymy_3akb|_?Ryk;^K-AY?sTl5?*8b9f3I<*3PO8Vb&Ojx1=hopAVWWn;&<>~b77`oTxYVU2Hn171M+sYT)aVFHW};0`wY&9@AHr!K2KV&cw?R4nUD6L7C|pC3(xr{7a$LO&a|y<9HZAQlbpD}e8D;CS{H);&F^I<-Mt<LEJXhKoN1|E81q|kkx_p;Cq}P3hHt`t@oS=vD}7vy_I&=dIM!j_W0oMUH8%|Br0wuh^uzA}uD*#edfk@0BlhVxyx&<Omcjo9hp=BV{epZ>T8?=sIvw#Y@xu3kUVkD#d@gldmt*z1cAv6UD{IiT?=9B6$5h?YFdXfZJ;QtVyq0kWy+;h%PZ*8!Hhl!feUlr{!xK9hbnE`FxSz&LnBP~>-G5J?ybaHvkt>nUIX?{h$W~`9`Wcr4>pb}*<mdbbtdlvzF<&{BVn62DhWr;^i@aU@f%eTJ(a)7i=!bt7uxH(idC4D){LJWv@4D}yo4;F{b@%%qb@O*iv+h10UK~Z<>YTuO@H>Tlw9AS9>o>>#I_M8S!;T?8PjKIKRVo7g>>22$?~0nPeSdTN)8+#F;rBXQ+Pel_O2YR;%LYrlUf23@{h45B?|OLz`=ZT*IK6J!m%$ist|;VrS0d)iCkW@^^vmc!_f><R&OTSrkM?~py;qDu=kvDp@735}zE?5t{O)JlS~o_oYu_>K(J|P+2X3ODl=zNk-xmx&m)}BueEu<fKhbpUdD0Tz4dYITf&cvOXE_xfqt{(O!l1XBk8!)lVjY_PE@Rf+-?yoo|1M+J-RrPeJmxV2z7yJR-bFuY65xNa&saaFa^XCA2HpAm9{jBGF-EUj#%{zqZ0Lh{FD4?-1B&4su2>~juUq~}i}@-Mjq_yZZM4sB{CkR~yHe$WF5`QkGt>ot`rbl6x0@Susp28DAC-i2EZ`32tKbEkw?9_lxv|DQ!?@bI)pTdZtmr3aDx43V&(J@=Q#lt`kJ0N6kCMnw%41mPQ(vR~$PlcbrwftiKi<HfcD2!--$N{!k}z%yi}5?*8|d2iXXnD_xIbQd5C5ZELBCKQ^R@IN^7hXJj2mf19>#q_`<+8EUztJ;x^s08Jck^+i}Sh27x-`byRcbz?_cWXzYCjncl(riud3sk{_bzq&F#&<2QcgI_t4+HRNef$3$t!+|F7R&m~{7Z`14k(ZvOp@SvR*g|9-}-yW79*13yi_Q!?xSYH#|Tl391Z7t9{3>aH<6jCmM14(-kF*Czd6?ajaYGU@K~s_tA>H~;?4tee}Le;4P<y9o1gE!far)17&@8lUTCE`x6V{hmoTw>STO&#b%0ZLkLOZvLI5NjJCu*Y6}vx;qbxH=-ZY??27DxxM-KpJv@1uis`>H~(GRth?7woh=x*-(};zyLlA(oabX)pAVuizkBokRCiXh82Wcky9GaUz5S`K{oTs#|MJ^d4}oWYs%!6Y?(@WU=ihO)H2nI%$@d8lT}6~jm6AsCka~C5{q$dm;-7{;|LK2U&;PHV{(E^<{lEV7zp&y%cBSM|N>QbhRZ2Eu9`XiC$*+{EO36peNX$<z^i)d8K%SBHU#KM`rXo*Hn?y`TE_7KbDV36zn1U#iXQeG2F$KBMb1S8oQtA>56LXW-Wo(Vf3$xyUT2W$Ia$lwRF;+jet4dwOS(&`5t}f!tNuEzv7jdRnN@`+q;xFV`B(Y!+QyN_k3ec97n3lW%W3!THWxYMMx<oA>Hrg5!>yrD?)_~ZUypd9RF^*o0voduNPZ9FUy1IzRgFGkenW&{EYB|WOl+27NGh@y|UBu%_o`v<+)U3n;<o#)DPqdQvXFOxb+p``(&5vj!AFq^P#v06af_I^<5wRC}7sgqKypgUh;{27o2<thhWg>cz=OBt4<YLT)$TPEEkD4bjFL^!2+@0K$^$FDa6I+wdr)><eKY1{10mL!nBbBm<@hxKfU8sxL+K_kA)kSRH<aJp0lEiPf;Jbyf6{0TuZbe>5R~LQ{A+N`JD76X1?&Mo(n@^lTzKynE;(YR1N;yE^4=}co)P>*v<Re*cNX?trhFs_cl~RS=oApZ6EX0E3KD2oeE#y9ovn#omt}f!7MBYkQ7jbS;ii^0F7)tIUiX5y|$`i))gfY*eF5($QK8y9X)EW}~$=foX-;~l)DYfZuZN}q6UHCeHMfkdqysNG*e7#0KNmmzsza!V;`$Fvz(M5h<DamB`F7OHCI8VQ4lCNaF2er1uQRF=sQwybZR!S4b(S)%H9!T2&VoUNsqKIQ1{eDfpkoDX$w0E>!BhM$p_JwWUF;<JhOUQ^xU_SC^w4Em=BmYx^Z6@(N`C!_55NDGAPFo9N5At@jH6gYjZ$}hy&rnKF#@&;e;HPL?M+_wYMTYG)+pHu1g*g#%7hxVmoTX&(yI90$W&DCCr%l9Hikjg2B-s8WK4Yx=h$6m;jHfU8VAcmJr5oeu#yACEK-&yrPx1wf;V$_MU0uYJUj{$LdR1ygh`*3qX)8f2LY`MCbr@?M#w+*@3ATO2<m5LP&s_3-tPi5rmpGApG~*Gzzf_8YzB{N1UQ~uHKk+VkQTp1FJU{Clsac6t$%`qa17qsIcm#hT!FGd~mwbf;+g#!e^0BlHBF-hZD`hBS64;M?BW(`iX!38gy(BuwzcJ<tGWbhfUBvS{c~RDTQ0qu+N#0c{0~qT7wiCQEZN-Qk$iGUky&x7N|H?Qwk-yN@MJ|HKSFnCUDYF^VY{o2jMj5tmY_pNPt_)iRqR<5ICBybRu>yGmrSxGOeHcS!>cYP)<ds=JNo^DHEB&2ETM%&*xzNWcWjc8f>z9-gLf=Ceo8Wn5*fJ7Nkmq4M!uNqnY0H?}QWLzrQbyC?(Tqp%g0y8JHXy$#!FH0Eg?zaL+dSe)@;S6kC(a{(tdt1G6v22dQ5Sv}Qc7oHTVfva&O{N@9HmT9ik&!+e3nu|8B-|R3GPQ*d*W#F!n746wkLlo!FH2akbIQ{+j8Pf^0i6{V@zR;U-0L&Jtjtw7nflxM0`x%MTV_2QOn0{+9nV?lZVnahd6<Ju2RAoYdG5p-jg;z;w<u#v=t`$k(XpHUP<7Eb#;-8&E!vY^;OJ4IAh*P9>)3`YR`#l$=@(9rDgEvtou{zLM%=mOxtW?7xHl0LW#4<7b;~9<6gsdg8xBVPvTtiinNs^_9TBR!S;$+lKd^>KS=(H_0`nEiJQp})3%csPM$>D8{$s#B%;VcCC1#Byfo`!)Pjlr<YA0=4S6u@`x*06rBqYO5XL=(F$*ryCSs~aO>m)$c+Qf)Wqjw9vVp#DU~GcRGHgj~bC_Ia4Ao_Dp^5rXYJG{7$d}U=M(j(zpSCr`F!EKxPsVtV?Uqs(agHQk%6e^T)rdpLYcm(A$*Zw`QG#}sD3M=e{5#0cvYtw@M=|aw=0fnAGHlg}GI>qLIh?#Y>kewmi9^X9L=oqDr5t8_hZ(=%<7gX6Tt!}=w%Wvz<mqWkO{`6RRf6pzF*W&q3AP=?i{w{miz4nIPb<TgiWo)iBg0mcn2LN1ZNrH*$;UAMwdBKDKTPc)(Lp{{Dcc$AcIHCxrnJ>3jw5f%TzHVzXFXPec9oc({FYLVGVY^{S@29UY-x#C$Q#M9`4H2RH)1>!$$ePgN^LE14EbNQ9VV_NpP`gJjA;*J7Q6**O^H*<bJFHPY)XDxf-RQlK_0J^V~qP4V-`G{3|l7RE%GKZY>kMS$eS>pDdde<-$`vNaU%I~+WsPLCEu%*V~q6}+wGyghq1O&N)Y1<qSk`Ch%Fa+3)b&Q&~6iRk|!wTICF5E@e7_^hAkU0p1he1TN7e7@@ce9AvPi3P1{c56!K%V9VhN2pRSZh#uUkz1#eDUD`F6N4%%`NTahP9u-zf%B6mu#9Vgx)kE1Ptc$_?|3|n?$0(oN@wr0fa<dbQeMr=mDgSOqoY2;4YjuCg0Z&S)q=HMvX2|kIo>BLBKU)q`zr<40KN14f+>*^x@7zsQF>xZa0iHYP56?+E8lz}k|K3;}xGO;oFc*e7Zd@}1tsX2)|$PY1|bxNtHl(F=8EaMS89c`J3zT}rB*kXv8$@faI9U{h%N7Htlc!)fjDB}A~DQOr}8pbSmAZ_D`4ary2wuLyJ{19zNiCf55D&+v<J-~K?kDzTVaUFRr+UgO<lBc9C9kCvHO6KKn2|OL^+o|m(UM9alTQqSmc?ub}G{k7~8ZvCZ5z~+lqb-p58+in6tBHZ+2WUG)Tur`@Hj#tDN?F3Vmrxr)UBv9Ilphi>CF`}wPfM`<O%$5o>m}H>6aOYZL)!)7c5*M}y6+NV`p&!vK1hab7_kQVGTI`D!^rp1c7PZ`F5+6DlwIVDSntO;J&E4rp5*VP|HS{EMerlU)8qoz==gfpKPW}~E%ZC_40#n9HZS6LauG{^#wxHAxxgyqi)mX%97Mj1@d^7`F%M!*DdmJxPAcUL@htfUrEH{qBW;4WR!SSClqHrUpQn`hyly_P5!|Mf?!2x$uMvEKQbLpxKpaKBNhzCY-%Oj}Q<WS{Q_67S2=Y^6o$<QUyhiY)ifx&M>z45v!OtnS^D?eG&uavaRBU@BT(^hU2!2t<HBmD7dDibKw);x?Nc=?pk5WD><pJ>_`E})*8%nuMyh2_;DZk3NPT*(uu~;cfl(LJso4hP@UV!*3`DDd5h1X5tHG==4lwnHgt&~SfyT`(J;(hWCimfBtbmTRHKT~YaWnA~1*9hKB!Zl4L@Q$p%P;4({T=$aK2>wJVPi5Gj(kA!=r97nlA#H-+QOaG~@6slCIb{s-fBvgRtWKW5YvN__yR4T~Y^5YzSBlpN9>cb`lu}%&mypo51ltLIRk2-T8-X$8r4?Hl3D=e3HG*GKY|%2Vi{>?gS5RyfC0tjL*9aafV@+IUjvjF?#9r>ty&!Ngc>wtx?gwqJY$89$B6uuI0NX!f{SNc{j9m1$i(KFe@)x>!yT@xqJ(2t#_sk}aS(fWJl514#gEBJC1aW4FbEc1?)nc1S@&H~NDg7tLT09Fov0jBm@DDsQ1^<ifYVj;xLw<y%7JYfoy5Qp6eorpuU(^NfM=msR_V*)S!FoLNvV!~qaUM%N`{~Ad8Tmi)@8WpEpPJm0qCS~r7x!9k@|xUNy~%6x+TvX6HMxe%kr!tXZ7Oi>mZMghSb_E$<Q>?*7)Q)YbJ_*gCl`7rYGQuGSt!m=G0zXEiMcDlxfgR{<9rHiO<rEcIn|EXhP)klZ(?`y-sCfhqsV8H|49rX|C9U(aWlC~#yR_n7)SnA#<`b7d`zB1{(<<M`~&$%;!E<6<nM`3$=}I1uig;vlD{E;O-vxaE#s`XNsK0M=_@DmNdEu&U!(r#pZJC?8U9D9<|~aqtI}WjUFpmHBdeCaDaCJ$q-4r};*UbP#b5NK{{eAjyJ7'

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
