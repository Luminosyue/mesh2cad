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

PART_NAME = 'part_019'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_019.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_019.stl', 'source_sha256': 'fa74e1bf306a868b3de035072e3e7133c778ba17a64c2c393fcae61cc2a8d649', 'input_faces': 1054, 'input_vertices': 829, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49999991059303284, -0.2987701892852783, -0.19583991169929504], [0.19713285565376282, 0.18605779111385345, 0.19583632051944733]]}
GEOMETRY_BASE85 = 'c$}qNXP6X4*X^Da5rkJkB;yVXvPcdKk{O~1f@HG{%7OtCNt72E13`Qh3GxyYh9E&eB}iJ4A&L<}F`&YLiWpE)%n0ADzUS6<-<}`e^L;$eea_iaw@y{pR8`mX%+Rx2);VPy{#Vt>9dKQnW<4CoL<y&iGb(@Bh}&<?A71b7dmnI}3q9TZ6P(_oU-zEZxy~qOOzxok;kORUZ4u3FHMm)BooMdhdxnh|Ht_BN_Y519Z}iRshYrstefVty@6D&bYc^}tyiT<7Wp$!sqyNW$#i<L)vu6))HGL_W{l39ipX}{heR}Ghjr%j{iKlu8^hEEVPkL1}pr=Z(o>+Y3%xiuf{yIMaJyGLmAYa<m`7!A6Wt^WJzB<sKc&*txw)%8wSL@<0dhA%$fKO`vrk#FWe6%h;q9;b|JmmLD{!(F^Ul$*(i;w83XGR5lQg2S*?$>R*(4A%Zf&BPQ{dW0vI}S>>;{ZK9@uq;D{^wk;Kk3h|2>3e-cc%Qh<cl6%xZ(4_IF$Qpn_sur3q5(|f`FbXSm^2TCug&sx_Ymd*Yf@y8TDpWxBK<jmOtOgly7yFAAMmwk4w9PU4GpWy-ohkK>pJDJ2U2sj{MZ*{Lj4n<CpL_G+(hjlb&eWZ<}9_9i9H3r#GJ($WI;V?deICpE}aZ(^JY{be$htJN^yt^^0-;Lwf6A|D84N8+={k0(zqJ>WyuUf4iWM)iDmS#|u8qG!9yqaS&aPgXnr33iaSPXkF*)aR}+HgZ<azVDr1qS!}L1(Jttd5M7Ofa~1S*lX?a6yR)9WB!6dHfB&JUsut|ZsONOp?bj2%HZL)Mr^^TZV|`fHK2}#gu?`D1czXK|y951%p48VXy1L$!=-tn(4U9ua=vVY#9q1?Ycuh4v&=bG?y|irxJr(J@%C9?}kgvv5^rRjK(e*fBK8MCZ&Hs?D#vyhEd@c)Km(vCLx<8_;{zNxF=>45m?OI*83q9H+vM#e8d|l$AcL}~ON$AO6gX1rH+6|6>8hT8Pzvyvwz0oc2y`J&9MAz2^U0+uky7(t1-JfyYiLTd|=z1MlAFLNyr=sii71HrKT3yX^>#ydm)|1*_&0DLh`DT68d`nHdFyp!o>2hC#uGh8bdR<!|wSKiO>(~0IanQQ%zg`z1UG-nDi?ANNF1;>9*Xu&-vMxl|>q6^sbzOR%+kEIDA2t7-iEkgwG@nJ+^I3E~KW)BxUE+72_lf7P&Tr|9fBx97%Xu#`>6U<Q&y5YP3g~kFjBn`}(B-_E+}qgG^*LE|eNIj$&VJ;zqs}2(mve~dsjs1z@3*aOCcV;%?S4IRY^>LA^t?A;_Ukd|sq!NOKKh&^x&u90X==b<pMOM;Lyzlzs&kRnwNDJX_OZIU-sq9$o*pZkpUR|1D@_cJk2=qXbezv^yIZSxx>LSkus_h#mHX@n=<56*(v^Q|(}uUbeyaY9?x_C9Hx2jnbkX4J8-<=wudnE_Y+f&-C)W>r%kwE0ye`pG`nuG4HKgObYR7X8>$+Xh<2k%P*!iZ;x7L3(>xt}f0U!Oo$@-}GO*UV>Z?gI7eUoi>3F}eSf6-&A|5mTY_d)Cb{L&qn@~y7&6Adc8>b0x#t*-J@_0KQxbah=x(baV&>aiYE^T&bisOuG7_s8n`dK0f+<IRU+yl-3mD%Mk%DF2-`r<lLx+!E4r)c6cuH#Jkf)m6Te|G{+gcS4O%LUcVoce0+;{T#}AsGp+ic1Km8l`&s*o&V@#^D^d(uJZN!KHGowzR&9F{hggZ>ilW_n{{8~{asbPj?Gz5C?9=(3+bvq`aZ7pr0$P8XWIVvsr#Du_l2kbY2(lD%X*^hnGOE@^va>$J{!OM??Aq@iuKs(6)*Vn^|>yjtLxI|E3M19D4Hn9xIct+tS`~^{t(i2zFIFKJtvs2=WR&W`D)&Vbd|5?TS!;=`h87E*ZooR$L6c~lgeJr`SRRyU1jeaD7roGL644`6wu|lYwEmy0Uvp8EV_O!ExLaGY<2bgS#<sUIlZGV&J`p0{FayFofD$t`er;&ita#<|6Juv8=tPvnWF3Sr0DuQS*Z8gpRrx&=@XR$?WVs%zG_#W>$EQCI@_)~r)gczY4&>6xl8Mg^4I4s+aGoA5?!CKw4PG^(f4ILZtA{lb#<S$y1LKWaZvlY%~$)m?T^~eLpt_7>!bE_t=sh|<EHl2kgojozN&TESK}T3_%N`p@i~j=`g0l4_2)9l86yKe>5Fo<`E~oblG5$^h3<^}VSlFa4C%OD(e-$0UB**%J)R+5`Rno2x_y2%yhFzRhjjRh9(s<X^rZ6F{SWENU-w_@(*N}S&2MGue@KVF=(_(}Pbz=i|B$Zyb^o<)pTq1O^k%01hje+q1U>ZpO6f`EA9{YJb>$y=j-+(k|B5;M+*;kItiERP9&g=2PZZ4BmT|smUFHMy(0o(6oo~=X^G)l@KQ!NzZl8A*^yPjYUB%BmT3q1mC!$B8$0}d2!=Im8yNTcbwr{@MpPyR8daPP=e!jY~V=CkLXkGdbJv2T_x8nmnG(K8a{-N<vx*eZs2Ulh4e@K`83VLWiRC-eRhxS9QEC0}bsB}A@$4_3CaXo5X)(iB|dQ^H+`G?k{)|G!~Ju2Pqhhuv`@6}W9n?%>|n?%>|n?%>|o6<9Hc*e^+x{c3iWiDCo*Y&y(U9St#(;Mr1=d0BAiM{;!N$8IDhc3^ZMAz%f>S}#iT|HN^?W*T0qU&>-*5&=0^~qWLig#T<1g|SymGzL1I`3Iso%gJ+o_pBwQO`ZBuAX~XANAbB>P=Sj^P}uwe^SsB$|rRH)w&)}eg9Q@QuQZv|JAzk58Z#2F6$*Zf9`CrANskI*5$bb^w4t*=%M$aOXoi8>DfE@bI^8Mc)df9ir!|(PQRY0!g^ZPyV4!ZH_@GBmkHi=DSu}Hbmi}?Vm+n&oflb8%Xxcw%jdlQ&)>@T2l$6{_=}#H$GXgO(c{o%y@;M_Jf7#9@=uGd{Nqi=2j-z|7rMP)EFa_P(Z&;B_4i+NM|Aj$o@mIr^k4Kibm_m%?^$svug9Q&N_6F)>chJITul1Ymvxzk&WcZYoR@aT^KJNRUHqXZmUIt1-`2W3j}l!!rwZwK?qq%D9|+6`(c_}4{v_ue2+RlT13jwR)z85~y6TU9&K%NnRR7g_59umj?~@^2<wx^Y2j;VVy+l{zqxV(O)3Oiie%k#u=wG<s2K__lE2V3Hy^qCL&7JR+FUsHUpNAn`)+zMZLe^y-iXMe7^UeAc9Xi*mul!TzLf8Hd>#~noALw=;6Q5sdPtW9^5MB8@Cs^11sqa}2`M21&*8jSMblv|}tS6Me=<>S6U;3N-iE~%%6+TypuFqql>+_Z9`g~>m)%i;F(DxFd>(AFj*PpLx-M;S7^?A(pQ=P|byXriq^{DdK=P^4z>O5wB)OpP6>O5w3bsn?hsm^0oSLZS7qxKoAtMiy0H??nAe{~)U>3Tf%_b!yK=b=82g>>bw&tqD*@4r5|ctNIl64J5%i>~iqAzkI``%6gI{%T%@bh#fLIkCvY2IVlHu|Gpk*M~0qGxS)!a)J4*b$cI#p186FJ|7JFr$kr&sjFH9J|DFG?A{{qc}@JtUEbf(2DyR$i|&Xn`xx{@z1-k>gdT@(*Q4Zjy*|)?(Nm%;|5W$u1O2!C>2ZDV^QN!rdY>EV`&3AWzv%itCAz*(i5{<%y~fj(e@t}cpRB;ToaeRfD1Ut)6kXp3ZM*6|XnoXu(E6zRpy>KOXnoXu(E6zRpv^z8*RZx3{GH;^wSNxlq5fBAJ=A}7pAG4HeAInb>-PD~cTX<!+RL54!9V{+Pl+z?r=Z7burBjo^eA+@Z$NiOES}?^|Dq>ESN@3yS(o{5ea5hE&!wljuk`v;=h036{)cqgAD|~|v2OPt=n3d{|AFpwD80bnf9o&0@{e_9-R?i)4_*47`t1OJ&v#+5!1@j8GCt4~3yKBSujp~;_P!wb%_{`vPe@n(PRj~``J;9F{pxd8@aJ&Hh6g?;)p~TunXP_30o@tce~Vv_K~Glizol&kJyq+>)=av5-YU9tbVTs?3rbI_ex{C$2z*a3q~m*f*5}pxyzjrI@V&T@uKZ&KtjCnU=uVaUcLekeSHG3XU-Y!PE}O60g`QC3AB7%Q<DXp5dQ6Rf0(xAHzv%k9tggmQbh%!q=w5F=#hTaN8d$&3qoT|Df}Xsbb-R9{C!pK)3q5t?Eh_`-7rJv3bmi~FS-0y~`U%~hABtb|N~Za*b(#O7>-ns8na`r@`K<M%YFE$akdD{I`l$IF(v`oS&svw)*Xn9MYdx*5OV4MmC)9ZA`Kfi?Pdz`iF8xnjc$VKMtZU7mA3ppUf35@Ffu6{Ie5XG@{lcI8Ig`qdL61v*sVUy?2jWY61)g__9upn&Q}o1=UV-<UT9^Ib`gB|#czzPnm4B+!^5ExdO1IB}%QY_W)@icJHh=#`cSMK3=&|{%+wY?)-G0AR^d{|A`}-f#m4B)!>-PJ2O1I~q%GY@NT<CX&O1Hl&gs#6|6w)!TL=XKA5xV|fy7ke&PlT?&mtL5!ez&M}?W4b!9@2IH_3s?DF28exuD>s>b@{%u9S8lpNby(Sm$tfkJ{;2JJR|L@=fhf$ss8BaKenIxcd62@dj6wz?XRCF+t*h;PZnK2Pqseld2%}EEZ?8|f4kf(m(P!&JJ+(Ft~t7wKR@(&me%F-Ch@`VSz?J+D>Lb-5#KNI>-P6Al~lXXom1Z}$)v}eRxAB_=yNos+t1OUhdxKsy1Fj=yQGJM*Cl##WbnEY&=Vc-xuMcyPVjo=cTCY=g4Zj0{A|m>^@cvzQ+ixquljwT?T_f4RX;^PeSe^z`u9-DsTI7>#Z%Y+wZi*5Hj?*Y=!qLyPt-f>WYVKeT<?35qQ`D#-Kjc~*TuBw_<M_u@AIDTrQk2RlgD~&8vAQKd6(n)i=Kv_j<SDxdMQ4iVn2^{DaHGi(xdJ3cl&kO&!g3c>~5P$uT|;|zwUfJbAKj((Y1f#7<A=tb@(S{;C!vtwdi_Xi=G%zJaAqO>GC^A@gLOwC4SxUJ4f*!%)0i`pZi!J^|_DrQO|X4KJ@4xPb_PjK~LlR7^3Uvz@qEVkL>lT&yT`-L1ta`KlFVhxh}OIYF+k2dtLhXs#>q4UPrZ0YCZjXaNI;ss&Ui%s_m!#K9$n-c!qu_E4u!jtoW$k$=dm&zn7(THO_i}*1GJ^_IlO+taaI+Mc4bY)@6UT^G$zGOzClbz3O+_AzfXs-nT<K_HEm)+PAfC`}54_nfC{+%j*k0v_C)(?GK{s^)5boy(`_Wcj%#YE&1yIRj~cn>ss>lx|4jpj+CBM{RyoL@z?7@boKupSbz2Z9@u=nj-*|^jwE0G{|3&iANje9y5DJC?nk2Q`&~%K{YZ3uztg(**Y~@S4*z6w1+QoITt#&KoJ91{^N>Y*y?LJ)`XzrZS>tnF2TG6TR^8)W=c2Rx`*8if54!%niRhvCgV1&VwJy(vMAy$nwH~byY*#-o)w(=i(z@=a{+)}xUiCW{(e>|KY`z+Qn~&#CsVNnM<EEZd+5V{KJoa@_&n@kEs^^w=+|+ZS<f4+^>+IZ7CNLkgF7qM2cnIqcpYpyhmab7WpeM$EIWJRw>dL<sdcM(Ky8=E}{mh?>M(>1vC+ic}%@52^rHg;;`4t)aBf9iQe6+58bU&@X>Sy%%O|0MFcdnO@^SS7W2U$;?f5yqAN5^FG@1(@%A=c&mA6wFr&$*rEEcE+}9=n3|^gZma_1Kz-=P$Z*CF`Dl&%pmWSF-HhZ;v;ml}u60DdP+t==(3{jA;G|X8tedZqNH){g-nM8#KxL|NWnH#oJRKx>NieVT@!kKTVNEyo1AN{)fB{PGOm;XV7TvkrP3lLF3f}`R4D_z%1|>MMsL8fwzDU0`Cm$2;L4D19k+z8F>SMgTPxOuNANp`1KUGQrrL>1fCCm1+X*t<-n%E&fxu#cMUKfT=L6jF;>rFUV-9Lie?eUE|EfB9e-Cx9VzPqzb?MMTtGRcD9Qn=g8xNheU_q37ULyZ%>Oo%%;j=}rp)j!$?G`9GT=(^pD2EySPNVYz7n_$xElOR<Q)h81fHZ=PVph|EAWpfj!`TCz5u=eJPBM5{vqmq1Uv@*EX6#EUBLIjcT;>q@f>g=xRgB$d=C5*)LjUi=c}_2ISZjb3!nGl@jmJs{tCq=iY8f%&9j)BxIBx?4Q@bg%Ph_*K(47%fcni*$6!nFs`Q#wqj(YcGWbgrt0{7T)xo8#Dli9pHR@IeRs*j>kxeldI3N63vsaq=1dM`9Sry<V;7Qbt0<(Q}qR5FtuL7U>@R*PKhS#R3N6{461N?G|t10RL>x0(;uMMmR-V}8&2VM=Hi}FUkJi{APG^3~qtP3t>xxkv>%}}>4u(q#GUF6h-o(rF*@MwzqhF?l?8AStN9=N$pG@+;gtmWf*_&X1Eq^uVFYC*pgUU~4#Lw&=WJG_U#3;Y0lFU0|h7Ql|+Qq~;U0{j5#b_8|+e;0r61s(u5<$WlI0!M(~MKKa}4fX|>vJSwG;3HADFR%~zQ2c!ta3r`XzmejL2;+$ebJ@pCU4u8lN6JjSFHznHIVX^J0$w*E{{-rsfajOkKbB(8Sc*0cKY;T2z-8d`!RG;&`u4dmP*3`1c!Ku!$0&{gzXkuA;ya3mf#bm+22TJV13!kkUjx4b?@w_(#m&H5zz0y=N^uSF2JmaZ`vb2BzZrE00B;3vPtlp82e3Ez)f9awIsmT#?*QH&*crSB>Rt`(1KxllkD?i{6?k)s))WnaO~4z1Hvr~=H$&a#z}DbVis}?Kfpx$yqo_+!6?iFlRq!aVI(SXgy$o0v+^n6?DN4JHWnJbMQIvCeT^T%tHD=-v*4!b~{Q&jLqF!0lHGCJ!(`d`g1H+Ht_22C<8sFVcVVS9S1m(Msa}0UM+`=`#8@S82SL}k%F?h**HGCMwgA^YF)8L<=d^m6n_{Yfk#Mf`b%{^|DY0qUed4?ZAxw#)2-0U!yGE?t>TX?_x1Z`}Fhw+j+n~}2_ZM_VikKrZ#HhdY%Cr21(M3_H8@r*h5IE=<u_ze6#19ha#;4-JMkIUdY1Aa5$Y4}u>KN2a-GyE}%rzoa7j4K`HQfBHshVrS%nT)*2@RB+!k+TwQO@+^7cuhuIhCgAhjpCsQ<AezFaTF6N{^KytbeKz-sW%SgPatOk@+QDb>dZvWOtkd`d?vta0@^Zs3&l2yqFIdRXE8T%UKW=dd=0q<w}Wp--7TnpKI#}O0bYlqE=6Nt9(V(aMijMxwZWyV4zLz@Bh;-8tm~^&8#%S1*MUzSJn~TA@X{3ZC~5*5f?tN5i-7gPrK~jYBJf72TOU}@SEoL5>O(ILpN8;gi28=#PHW>fiq9OzPaWn%h!3VX=rDfbFu#MwdML%6z`MZTqn!N|cL47O-%GL2<??+fGkgwtEu@$YTmT-SvU4f2fJMRQQQ1<8=YUJV&!Mv76h(mNgHNHdMHK%4&vThSO|jVF^2I2df;^LR23QRI5aD5p(ZC15zoPh(VjS=x@CSgSfe(QnLf&EESK$AmxPZbu`!JYtm>YZ_+~9t2lYb%V7%T;DuA=~bH(0`DUeaa$Dl}7O`18O;zyfgd8of_(7w{hN&&?d6xF0wQd>{UPANV==ofP*{bOl}o-i@L=#ZcgV;EO3<pm;jMI4i<@D#dJy=Uv7XE^{d}^`@eHF>+=hZx+0y&I;tLKwFF9GYej`(3asdsO&d0k0XquBFyihxZmt|F5~Ymb15_R?m_ts<cvbzD0oSo-;wh>+L{5MQScgtwhVuk$}S<S7h&uHUZ3J>isxL$Y;Y+v_3A@=7CAkT*8^TsCmZ?M(4U1*4|w%JTZW&Zvj0%jh%gq9FwZr6IK^3)@ky7tl$m<DC_jUo;>arwFRAk+a-Kw6XW&yDUd7Rt;ajQfb&7K%jHM&Yi&9)fk#ZULxXh)@)GLbet;i{jywdQJI(v|_2W@SIPic6SMq7sOpt85j`i?MGj4;1|q7ubUm+@_vxs;iD7odCxaw;OPBD|!|+sJtvZS8<hMR-+2TZTVPWf8)%5yo2J<tS>KIqx!NflHaGR}R|K$f<?ATJVxOS;)_V{xp1Q!K)V9GCYSON#(tPjUvqZP&B5f23+7Wm$DpSHE@&D2zia*C3Otu0F&Uok>3Z{82m4@Ur;<4VH_4=K89jA#osRDY?rx|nR;VT{ugqFA#WJGq|R*Q%tl*(!Dkq}hM_IP*HhVM^SVYD_eYq&P4NN62A8qGWiDl=-rFc&kDUF;+Yc|PQ-GWTw6z{S`{A`8Z5h6V%2rZLi!jcKFrQ8_mtv{QxXNWNWv1SAlrKTf9OTV`m(*E>oK<LR34G?jYYy5nd?uCsL2++{add?FeH0H+{MTjt(`7DYrrv!hpNX8&$QunWsq-gt{zO|d;WHXuqtTY(^QbIJ*dW5#6TBfsFN*mtV^we|GxZumn}?j9$m<C&sZ$mCRiV#=PfvLDL|cYC6i-okO<;)#^UEkoQn<h=E^{e!fG)VnDS^Ba@RB+P9pF>oHIaWAuq604Du09Gya;2N2=ihT7gKC^8Q*l7OPQ%x4CUL9QwDiu;3ak5M9!ONYa4vZz^e?}GJF@6y+d(fgt2mjc`1r26uVu<cU|UEX6ltf`7Y#CMqXujNu76*^Df%j1)s|Bs*JV_pGIZp5SEWH)&Z|TQP<3Qm$3-Al$m-JpiM(g9pu%4m((eO{36h&!KV(q>Yy#dt5Ynb^1i^l2=jgvO(-q}E^?VmS#{v0;3g*zd3o@XItHr)7lQXiem`In@Y80$p!j!$aYTgqSc;Jp|G12EUFK3|>WxMDY2=JR-UxU}ow>-Fi?&X~X9T=Ppe@7u(R9C=Via&J_`l8jWQrSr1Hh%MAMgh7ai}{0c(bq00OSmS-VZ)w;V~BV4evzJpW<%d{owadjHc)eyars#IsrR_cScSpV1Mwt;du{mG<X+^YbovpJ^+3n#e)=A0<QzV61)rWTJU>O_dei*;I~i=rbqxE0e_g{QHooEL%^l%7T~SmkD~4n;9y^!A;=j5{TBE<0*^;f-|#raK#G>Y*5HFsF9vK29>?DUfrG$JJGW6>0qh2TC&e8Uy?{Nz2jlPCfOmo)rTCI!J#ZuVdhl0(8^DiHe1Upjpw3a0Z=v|vWjy6F|ApdLmpu%=20tk?^?q>++b}t&kar4RQs*_~yoR<mz~>aaPN6Nsmr=Y(@e}Z8@RKNC4txoGIruW*i{L+@?n&SE7`_(c@q^1~@(lkG<?9?qGmh(=!ZK6uN0hHc&QHku30_iXJ#yBgt+nv^30`tNp061*ipPOZfIkjC2{;*ijTu|i+k!fVA2<D=cnkP3_*>v_0zU%(+FXyr^?pPh!{4Pn?o*0CfM>w}q&Q2l7x)?YAISL=cosaLyl$sx2fPZr9e51b4SW#hbw2QR@bAsoQM3WJ1OE<Xt$}U8P0k7Aoq)I0X@{J4&|4!6Z;3G6tl?u6-%{)Zz5~7!d<XDt@UJMoLA`HK$M9_wdnjIZ8P~bYSDQIQvE5;O!(lFErrv6lZ$r*H<gJ63)OiCrZ=kJh@L311b!f}**Xgx6Oz{iQ$zpzr!X>^3n2s<vVfgF7!{EQ5?kS)P{wu|A6mJ0E1pkZTcZz+$cffze-@gI>0{;iT9|KLhh8H1z4#m+3<B<sS!@!S$N5KC<o`ZTtz|Fif`>WvwMK{-RZWhl?gS|0NrOecGvkK?#x$x`_591|udLySd+Un*MwtEG_@SgB5f;Nhv4~7q<{@+f~0odKghv096-F#&R+XK6S$B{P>csqDoimNEv0K0+Th`gJCxB2*B<QeP=-V)dX*cJR*<Xs0G0^XeBN{UKZj5V^DSEk6#;<^UK$M72Xy9Vk=Sy%XVg{R?FD5o05g<1T49rL}NiohK3ir`g%)xgVAL@7=?jIPVve81=7EdD-^3B&&emIW`1dWM_t{+RConePUfFgzRH+3?MVZg?5wT@1_yzZkr1R$+a^zozT_j$#GyCGe9JKT@m%t^t1uxB|Ea{A=WW2RsSBh+-ARLEtywpHqBGu^9Lw_+s!yz*XP}QTKD;x8Tj_8d_0oj4-|$Vcs;0%hn^uXzP*F0(k~EN0>K--VE3ZycG>?SBm$5AA;|5_&(Sg*bQ9DS^-;we}uZ-fL(ocx*?|<^j7fs5FQ_*{yvmnPcaNQ27I`~XZdbU;d=zxD{er&8&Ib!>Wo3XF{mT_A%|Z(gYr6lPw{hv^9;&+2Prf4zDM~O<eWs_NqCJz{z=q12~WeH$J{yu{0{su%9j9N244dHJn$v(L#TV$*Kflgp|vr=oN<8PgMUMDg5pu&MDRz!9|2APKaRTJ08fBlOK~Gb95@JkAVogKb-<gzuLHjpcq4cmbq50T!8=lPq38+h3*L*OA4MnNmEfJgI|93a_e9-Zz<%J3D4J5V0JZ^dNzs;~G4OKm#^8;BO~G5BZcAWW@EnR76t#f$z-v>~r>F+Z1+NC41FQjF3w3J)>w}v$a@g#zE@OF@`Nb3!TwXs0(^yL;(pXz*)cp|k%cEX-)HQq~#j6zWMHtOIGkhQB*Cv<IoToRrg=MDRK9p}n&LQL-f|u0Uf}AaAYa@IP!AsVI;jg2=M{(_DUK;*|%k$Bk;l9Cj?{NytOua8q{yK7wBk#CdxYz6fzV6$*UWd<dc**)Pd<4b6DGmaUf`5wgk-)Lw2a)rsuiu8RariUE4_!u+XZS}bH}8WCn)iTfox(Cx?<172LC!(s9fX(E*@B!cXlo684#G?NZTJf)|4)Q*W`y~Z6#q5%K8Mlx3ZIF;XQGaj8GOMh?BfgYoe960@HBh|m93%}A7PvlVg4w}r#XzqcbZdJX6ikP@)^jPg1jm4k~%ApvjT0+fX@_oO+i~;o95am5)sBp5#|q5JWlbH!#K-fE@h_P!zh0eIg^k#30_iX7IJ2xtta6#30{-Xmf^+e-uy3$RD^M7gn6+nF58M6qisdmPH=-ez)gNh)F}y1!(;T?x1;!z`jAannc`=Mak9g_67)-e+2FrX*&h_=0?+gD-|@G>qTm-&lybZyoQDw~zX*RDJRiIg#lOsc20S0UGDTU6a=?FqPo(&T;xXVP@Cmq{@jz2%ctzq>C?0nhPddzvUI}HDaIJ>_>hLw613VY}l*46Nz;nRQK~5I12>1mU3kT?emquAJpabq8rx>s}crox2z>?r5Dx%zAdGHd*DFeJ1yk|EzQYNeLM<Tfcu4~h*2b~Lha2@%V@H#pwf7poI@v9MCGx+lof6Y<kWq)kavs)1}9`qtdya$-G6Xvh~0mEUk{Q'

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
