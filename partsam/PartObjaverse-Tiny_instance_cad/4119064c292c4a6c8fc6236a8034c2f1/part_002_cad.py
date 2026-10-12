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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_002.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_002.stl', 'source_sha256': '9e26de1243e4140b1cb51d85fa22301097d9a5979fa806c8a167ac07035c39e6', 'input_faces': 592, 'input_vertices': 645, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24567194283008575, -0.4999980926513672, -0.19913159310817719], [0.245648592710495, 0.4864616096019745, 0.29218876361846924]]}
GEOMETRY_BASE85 = 'c$}qt2b4|M`}P?lYLwB5auTC=GV0)HiEi}HVf1cvf+PAbI$<!lx*>WQ-NER+2f<ZBlpsowDBs@i^Z5SveCzwx`quw1>s`+?&wcN^_u1#1ch{SUTEPj^8Tj|LF`|2!t#88(L)(`|I%8nRsQz6eJN7HwtIv=iBem%I-)Edzw{e|_=0V0lV_2RJ9s5N_<tc0C3GY-oPeC(Jr`}QhquTXq+dHa5N3DO?u1CL)O7GXDU7wEX@4O|y4J&At$XC!DZvHp_B~w-K6^c5uPuHd1+SMA(u!b`$YE0H!bjLqwqefqA=yvz|@SnL^{EdCvH)!408M?D)qWC*8TcNiq3IEIow@REB`8R3ZI{NIi_+>tHP@`2lhv@#)k3}~wd~sN#zjRjk7x~@eZ%6Ny`Zz=V9)IH!boc2J(cN-ckBUAgwZw6HM0<4K+*ji7uiPE+kJs2C?XWX=qr}<W3Grt=o+I^q7ACqmzqLm<i*}qN`u%Xxtvd-1$me@!MoT-4%7XY4Lyt?jW#360qk4x^q7NJ`?dG4Kex>-2Zzj4?3-`tCv?f-*_ofN_Z{of<8JCN0d};*$yib?Q^<=y(@txZ>J-U<G_*v@tS5@c*uS$HYV+JYLs$LQCGvIzX^{?-j`qa+?|K*oY2(}K9_}0`<C*|*iX%<Mip_k>pJKuc}-O0rJn{mIyaVNcn|9RXm>-`?lt&lg~IDe&^E9D-#?2WVY<SM!UY0rD&7|jl^Lc8pS-t&~)N8{QGlsjb`;*`aG_wQdSx_`g|_;3GqwzThG(YW58(>(spwT6g4V35b(T~J7L_xb?n$9M0?`vKhu>j!=7*PG=!3va-EY1!4I+pl)YeKEF$q1*|0PW<2ZMm@I`ga4*@@pn?^mUcFq<@e~8|KWVm`|Xqa<Xr!2ue95O_p78G{@&x!-4r$Dxv(m3$9)|YyG7!6Zn#eL!P`9kPOEUV&)`iSf2;q4MN-eWmC*mXvsKEQom}c^jPZGNBTM5LiL+|DC%(})c7@#E+N0sWFn*iFsW)EQ&HsEj^n!Svjb%BdKK70w9)Dx(z}a#gr+P!L-XHCfIEVNfyE}+(l}U{D?wAE}dN=pPw?5U7`Z%p?dEyu|ii&QIe<=6KZL#j0e4ex??(f%rk8WmoCiU@Oi51<5!+m!SpLV4jdpUG}O<VN5Z{&X2kC%FMf2XEWFZcXHkM0XSE^*B81)|#{4xE*8n`Xju^6qDk?z<B%?QirN=c$jo?Du8z`TZfD_|~}dqB~j2itY@}eL?Vaf8@Pg$B&7>kN0b9KdFy1bd^{Cw%1bmUff90-9K|(6ik;y@}%>usp!6^OQoJpw`ypgQ4JAi#++T!4i9omJNwd>72Re#`%{+@e}A=-o;X(3^-H9j`^8Z1?oQG#xd#%(O1Zs@dUR{IjpxhG@6~@VF7fRdnLOoMZGVvX#>*sL{|D`%*Pehp62g9P`RHR(&vV1kKe0XC0fQFH=Ue-WZXGRrN%Zp{<UZP|dU$jv&0}ddf0guzQ=0wVp-_o$N1Qz(^<+CcyBqkVoks5y-I$5?^z|vfPvZQ&6Z-U<d!*e*u2?VkciS51<B*rEHK&e>|C>dgIBxAk65qWM1AQR-%^5Xtz5XepI|tCux^vr#ZU%LOznvKQ{Cwrz;^!|0{}owq-RbY`lJBJ`D7tl%{cNTdqWkw`72OQIk9Iqr8u@2#dXH}B+!}-TDFo$~#QSb<tS8syzJDh5aF3v!{VQkg75_gk9S-z&+Sur4#+~!{8_OdWNI4akpr2dJezQO?iSNuBf;cAnJNrX#(T&ONq3_1~Xv}wyNV(g}d;FbT3ouT(pV#AWZ7RE6o}a5Zp+7h+_tAazM9?m<<q)37f6+bzXW~AWT@8IF`Vph`*Qn>}RnV8?{dJ1umHPOa%<;r=$`+j~?ew&d*S}ekINaCXp7_@EH&Rb?VtMFq*)PN$mH5W#V2^H1t^)s^|HO+vk^R)%TvAW7IdrQz-bbf>rEPM3RUg5>C&pLyj`_!>J$&b(XTtc$c{)~f>%u-yd?Ws&l<Pd13q9KWRpQ<{C;gpK;78G&XGx^J?H@}b{<FdGAA<MVTG&nAdt**N=o>LkHa?s@CD)NO3i?ottNqhXi*9VLhwCaIBG143OG1fnysss??+4^_>&gMSUjH)7Qy;f+mOY}!m4aS&6!K5W`KR!{7eToV>PlYrm0KaY-6;d~Hh3ScI&GkrNdtZQ4m@WeTTjaKkS_%K1&%i=nRu^Hr}Wg{>atbdYxB<QgJ@6W4I@$fA&FD>DfFH7=Sh7h9G3XT=!Y2hKS3Td1`XOGe<yt)y0eV=VP77!XQ6wD(<xr^uQTnt(^8*mzd`>JdDtjfUUVbsD)h0tq`e&fROHXl3kL(Q%T4@vr~G~VH1w4{_Tl+UvRiP~0nc?gdBdchzCU+DFNyKIbLFVyE%Qtq^otnJn;Q;^ZfD+#>)MMvX<e>{_8+hg<KVOy4?D{fN&S7b*T~=QNsg;01Vewm3Vtn8;kh05Q0ir+T!J{iA%9vAzn1uJ)kUaJ2j=Z`jZWdcnBs|J_#4iUzfVv0w5Pw?Ow>PiH0qP)@n!jY#7~kh&2b|<x-;<z`VD6|>J!HC_8Ytx#@KF%f1cyRo=4=qSo^zr+Q+><7vpYU2XFi<N2W{pt-ePbqc+AfDOyS1@P*_;oY5R_zif~9;*AM^t6vxSe9cwyw~}W>{KLrec6|EH^1XA(z47O?mU=nsT(s{Z<bS(nD|w#nOG^&~`nw?pp0|C&pch4+Hztm8<?p`zq5s73c8V>M2b?Q?pzlFmwdX~i5bWO)y2Wv9i>%T<Zp9YRqtU;+!%TVa?6$=`@r@?QrM-RA3wYu?^}Fp8{nrf8-y=W!qu)t=e4W!k-_P-_nN6<O%#jHC4vdS8?X{#|u%6tNdRZaQFdkdsL;inqet%$m<LNZi=jmx&$2aWXLoOk&pE<riuv~XoPiZ&n$Wp|Qxr00zz5?Trazo(18vT@=x1+S1@5ce6`|pQJ-u9&_F7+`V_e7j3o1}m7{Z<v%JJA;1+0N_QKST1O@plPNd?&24w42>JJ>m~Szu-%DRO(}#NQdhh#(cgutK=a!-$S_$XV+KAd&y!COMU(4L^qpp{CQvy+Nab!JTEOm#ou0B8u4><aRbYBszphBb9pNG#~@$X{%y$H?sKWHI~)C-^-Ye0^7&@J=+<M7Cp$%8oHl>azQ8!fk|5FDKZBvq&vjnf;ZZ(WXK;@l$NM}V&!PW*c8n)GHumUN)8pu8CY(TC{@6vv-@cpi@lsBqg&y7C<~G(*tesN6#d6)RX2ePP2WEP7qiF7C^8J;ap@$%E7#&;4^%`$ddvt3}zje}XFONz;U{d$(AHG4pH@PwT2ezC4b|U2egZuDYgd+c2g;$=Fdd=Dm{RHyAwQ#xUW|^7L8?*nKKMDRTCt^GjjC^b591s5%5%5pN^|1*ZMR#)7f&WqT3vQ7}(T#{K&|6@g#I5$7=ytR8qPw5lCtKuT(SJ`Xx>XGM*=}7K<^G(&dtDp;gZaiy19}gvlUUco#NT%cy5nM<#HMZ!_!Jk|4tCawh?C)TT;TQERcju>`?nhTV<hsnn=)A9_!G2`3%oAt>Jhnab6*AM$2dOOfAFk4Uzt*&+z75GTwVdaZ35`iFyD7iEfU?g@vV%rtfE{uXgu#MK5w%vFpha|f{b77XRV+g<9NPNdGYtRXb9b`gZzKJl<0Qv2HOJ5we}5_IBw7<-0v9N7dyLOo_FK*#;t+zox@vXyk(bJ41FW>&*qpjQqIizo;XI$Y|G_2z4Y&vK!11DCG^K%F2XqL5$EHt+oPXrI!<(}3G$Ddr5f~vLq&JCARqcWgrR?pPb|7Q5c$WR94q~SzxJQfe;P}XH_ZJ%OaE)e4-wsYh&*HF`d6M8-={_%e>Vzw-~MsNCei=qe5c%d$>-+SgdW|0q%iW}i-mY!w_yBcS6(f7&v}%?qr1H~%e>NxH$=CaavYVQ3+AD*d)5o4V%{i_R&=}Xsg+Xy1!!k0X<f-z{@*^yINPOeUrc#G^m9MRyx$3Zb3@AAl}`FS^DJ~X&rH$%pY@6rL^tQtf5eR;azD?N72RG4e{229cA_sXAi8z)>s#`7gB{bPzF~P$?(ID{(GKrsN&Bq+AoF;;&^O|5wjV0(XvRYK72SI?P`CbW6eICcaeP~Pvs|Aq9=hW)zpdOTx;dpF{4L}+f1){Pr*j3MzdIn$sd-?U=>Fyp=Sw>zMSe5(^g#Qig>D_>xHqyJ{Wptl6y$g^*Y}8Dpt|VJQ09%`VEBKxO6D6zd%nL@7a`vc|5N6*#(BQKCki94Rvag~uO8ajbpBZ*@iRboPF}q#*Pr+;^oAWoHwW=P7VEiK^!yz>{??9eqB}{8quiZ%AN~8|BtJNFl0yFn?c+A9gmtLoRiZ`DgmJt5G%xzwf!pQ;UYGTvE!IJzheBV2@w1VuAlkFSVCsCoT3eDg{N>V#?w-ed!Hmv?_H3SJPGI{uIY(d~+-audePb}!D^?DWcC#MznjLsuM%gLIZ*LN!pJ>GO(kZVbkNG41oE2Cfr)L}FleImd|HArP196{M?wu)rpTT(54M~lDs!c=aDehujy3KLq^M1!Mk7>kpr|c)Oes*@g=+=D9EA1&`fuC}TZZz13JhNdb=0|rQP75s8S{{yg2lk5Y48pk1t-1==HDS`U!1|c0Hc2~J34WX^`a+Du?dBKIA9XDceKp2KzB`97?p*wFip1@QylS=$#XSE_P0@{RsjxotRdcy-Zd?Y@%_bNh`b%~}o_{~?C;5B^#x2f`#xkxlZa<&ssZXJUxL;+fjhF9zu}k9nx~IXown&Gu5<ddZx&2@-)@d(Aita4ObMAh*2m5Gk+%Xbo5&YfKiDt?3mK?h875vTbgP<?1*B|dc=i@o9qCc&0zn|z%UCh63)<(a4`eFwuHwDLU^-bjGrZ3xz|9bROzQ^InD|gN`75~QEk4w20@4K;0bmP&llHcrkF~|=onnJ&a^%kc{2R!FzvOzD-b(<#^#wX7wH$i(QlYYpT_&)mmG4mRWzTx#yx!%>aL^lgXLH}l)JXiiNis5-^b}T~l*io`BY0sD}{hd2HyqxICi(o&X@ny^tyRI%I-&@3fKgT$k_Zi`tEWyNGvCh6H6UN`S&exOgZH$q2b2Frnaj>!WWdre#!+gYzIg5UI=Cp=V-W|-F+)=YI?~Ojxq+&ojSRZF2KfL(}o$Y3(zlHX@cDa?Oo~MROe{U}=(q8^{aesZ$b<jQ=Cqmzi=fQsi&x5-$ZAXd2`|ckw1pWKSc2R-4(<2+6hl$(z$>;01Zr{J0JP*FpC;J7K>)c+4_v=o#{+@DQ9L4*)c=H(1U!;-u)L69>>ru(hiSGaWUbH`g{pAkOtrdJP#vj7I>TmtW%J+TjFGBOm^Y0WMAiDjU{Y8nKqPtt(PZa+pcu(E%%hC>pfA&xE_jImXmYaoj&L^WL%jbRWER?vumY5gB{w=ySxGwTV<;0jjZU1tLeE#;+EoqnAWwHMpoCkVTHtfsP36uW9m@sUrU=!p?|H#!?&$&E#s;8cv_MqKT@0uD|Pv><F%<JxsohJTinYZ7b!hPTM4EiPHTXTO}ypL@Y%@BPZ@}wI0V_qE=0e#7J^n>|F<9&RzM09r!^1Rct6t1`HIr!ISzc8XD`n&pt<-C9~2kW=i<t6B6_mqYH9nVGhma^Sy&kU@;)qjm#uhX_3&M#!XiS?vvjS**iN71c;+@}j#EYF)6z5#Kju|K^(1oNhm@iPP4!TBx>^Sru85$93JRjJRv70{mJ6XJO}gMQq3k`>n#-$`_1Ir>v)a#7Sj@k{6%+5gt8fqBG_MX+COaGh{uA&jFo_MeUSh4YS|cH=pmG<SAj{f*!RG7fQPr<@a5AM^hA$P?8wiEjML^_;j8$g8i1&k3xL>on%N+Xm=SoX0I(hW7D?M+er^ozVsNx$8XaH|E9o(Ct(k?f?F$=<Ys@C!KY@(GC?aiEbt0x@*!XjBghP&&B(W@tBciHuBcRQgZ{_!M|b*?)%yvqTBWHUi+eQ{vzdGhHjl^fA^0GeeM*|{ezh|LTAhP&^<84<L|DS3BAY5xq<EGuhAd*_Uz($f$ihF*cju$Ho376{4K}f#j9ZdvRO;fot>PICm4$T)IrdVV2tzqp~FSDp4OA{{kbt8@og@Ob-U-#&HU`&KkK8Wi0)g!`OAlxVd9r#F?2uXDOOYs87Eok&mevg%tx$lZ7{FP2;C@w`N(J8ZrOR6#PxCgCv^^)XE_xTE)UeLKH25`jDL5qtV{X-Mt(Eq9Fuh(`@%Wdhc_0pKU$Ik?NMWw?28)7Ij-p2AM0%8KZ))(;5vEj1z4{xmL2<$hcU0TX2fH?_gY!e-9PZ2T4B>={m5F=LUfDq-8Q$d-n3!3=zhj`kCc%9%U5QBC%$oZgy_cU1aj`lNOlI}#wD3$J=Qug&7&LbLS#H*$H$89?&ZE`qkGtYsnrnkpB<d1*V&47^4MW`&hBEKZU^7TcsTm8$KSob8tb8Jl4AY357z;%&A>iIoex-dK8E+jdbJn*NV#lyUShdl|0XTgxBks1x)Xu<f;~5<=>G0iMEBjpdWFAMCDF}|OST5aH@a-bdt7QYbTb0u#)&nMuljC=ew*{Yr1dcWDj9*iwuH}5u{T(UdDjqe-*Ua^i%l4(-EXulFur+h48{*dTSFg%_tDL;1LMH%ZMFrL>$IAV`9kqgo^qY&NI8#TZ=M2uJ;otsKJ@$kKZ4@|>tokzg8kHCDdGalb=r5pc)q6<7Z}G~7K46yRu$2$*L*L=e=GA$_u}`6lMw5B&h_dTC;txJ*^Ko)A9Z(9Yth}DJfG03G1dduM8dx!*6W;>%`sp5G#&AGF%S0`h<si=8va4Z!|u_+DA$QaJ)<zMH!6RHycc~E{(o@3Jar!8H2mbLzt!_coHuOq$y0ylx`X~S--PXfajfn+asFWKbkU6*$e(7b!dSN)Ge>my^K;TJx!fl+<1YAb;JL~d?Qs4ed@uB;zhM1jR3y$lbZ)d$%AJC7k#E-%?2|q^F1jx%*PROImGvbnNfgd=yyE@ZbfdHA88gcMq_Y;|dFM$X@wW$cg3dTr=-#zb|Ci~p{=SsYTheFJF8;ZTM0ZkQzF_`)RpPj(j(Kz=$rg+c&o+_yiLnRcF(*j`*7?hiqmDddT?&_c=*vD1>uxO9e)9t7As;V5UUNAP$?^z!b?zPPzuw_~L`Yg0-`ew@A<kruCtF|nMcSi#9h~2}&v8+U$Tf1kBRb=}QZMeyd|Zls{B&C|FWSWYmo&Fz|HVv{9_Qfd^1Q*JWY~W(OW=IjS>~~OF_@QSFE6@z1M?&2*RHa!<TQ)G`NU5<k#FO}aDOA3B2E<dgA%U8K1-*;p7`#bH+Wz7&4<1mdD5x=jjXfVlTSc@$b537iR5$t@(a*IF)lS4mB9X2uCxaN{oRWtu>Uk8<AFebcThH5?}dEOUG66qYKeJey@Jpma2=-qLWytvR22GFjQ`D7PjSDhRz&~2jP=iUMb^R1r7hq;i+S?f#F$6CZs94{Dc>Fae!|Yst@@I0?U-`d@0-=vTc4O$n776B^VG+h@Ux7Qt>;6b|BCUd8`)dh&D}UwbgKi_RgC<n<$BGY%RKe8Zu`-nE?DNNkMUC>>BsGv`w{0q*cY~X^u>C>xdWbZ%{A2#CsFc)p6gmM7w29&g+lMebH%aT*Q`_k`by+;JL(H*XY)uA(cK&z_kNRH`d@cl75GPBUC1|Oiah83Y2SIuH9Fpr=gJ?|M0D#g#_jfG8}r<<%|v&8$NS~Xnj`B?PTw{tcN_A#S-rB9Yrk)cI3MECfA^>+y7O~4#F>Hlh`nPB;*T1M`XpiA8?sW?#r#XAK=*Uqc*YNi|7I%mnOtwFgmIVCdKKc=!#K)`ZYkqTv)ESnU%)uZ-)=n4b)4M~J)ZgJMzFMxG3t!R-$--?<JE5Gp|9Y6Q(Ifgbu(N*xjlI<Xme8Jfy_5N^>-gO#C+({1NcwjI^^wexxZ$z*Pi;=L$=B~iM1m!_C;5se=$yu#XifrRLIl0xgIsW8rFq+r;ZP-r+cCs#+lpFi|%}n`L7*}eQ`5ucG1n-$hX#!zftb!O7Q=c>tIO+BY)0}@RVyUEFpQ!PCDA_Ut^BwzH(y_zc2Ehv!o*S!yZgSJ$GaM%{SmE_TRUzfL;OXb-sx=QEsyJ@qz8^)Vq)UtxtR5AIJB7O&6TIt8^Rw8L)0<%ugZXe*f?9JpPVvF!o2sCq$mhi+t!``X&0cu%e<nb+|8oaR<)DRIcFhcQ)^m{YC%8UeF)$+}+YnIG2*S5A;i%M-S*J&x!RzH1z#g_j5N#N<FPhE4}_Fha-P>i1oy`zUYa4*#e32{AR}Z-+nO^@ur7*bf<q;8Sh!C^Fn{hexyVasi!@x0`xyPufG+CycE~Y<8O^xBiC!!?JT-A0eR1vx()5$e5fam)jkE*^}}LBcY9zx$_zoj?}RS(#+jE0`@NCR5N8+9Vb)5B{h@qmaIRz_^YihO*oS^p5bYX|JmzaQ8}qXLIQQX9!h2`_@f+UX2=?36@Lu>gCBu5!v>u3`lIuAS-=LoFaNnHn%+GdaoUhnA75-CrzH9J9oEzB4^DoCZ&)R!Q@`{sejVF$A;3&?2_TCEr-rSFPe;4Nx%e$U9PUIRnkLtXjo;)q)eFuxnIe*`)c(lU?jC1U6-Esc>-4&EOlIInF>x_QnJ#-@*_t#GMML+w~Rp=S94rbNqg!W1K7j!?*@3pJAQ0hN1CC*iCLBC+<UyOEM8G>`T|Da#+xl5q09)NSHJ8^%_6>Tx!nlv8zHRMm{=VCJdb$*?I_}95E-MEijmw9gi^d86$MqD}UYgR9Sa(q0`lg-3=>@&qZx_`^E74rQxWiaobg!NCOMt#iB4U9Xi+ROtdN@M@ERxS7+=eg^p$M8F#(v3X2U1OK5*Z8hA!}I9p{(G@*630KK74*93uZ<jaeNt|^33%>qv7Kv1OB{R2O2og$abxGh$a8m(d32*^PMlZYmPziLzdPF}Upk3zudR&y`dN1~VqNKD51dQ2uuowQ{{hd>FGHc*4RFq31b=@Kjq|p~OO7+EgyMHD(J>eg_U8KM>px_D+DyFA6UWFqT=voJT1%i$dxL$Gi^K6dm(9yO{^qedt0jI=tfyRO{Zxr#^?!uxs>R=NoLqwSwe=M-e$RsQ9(LI%si!lg<_TQy0G!kKG!WO7x`W5x$h#N6oA}tv<L_)di{Dv94Tb(2?@OlASeN-`IP_J_S6v^%|BEpmf8VMySnqRYi0&-lengp{G2d9f2>wOT@7T5XV4djh3XkqS|4Q<Pxnv{sedzCe8{%X=%U3VX6W{r_nw%SPyTp0?t>9)@hYa82@weKxllC`v?DgpGnRR%Na)w}?sVnlEz2_L}pSA$>7wjJ^U&s5^x41_)SL~JN#5cdBCyw=JM){qNJGKk-*IXBU(+R&TY#Zg#oh-9uo!8tx5c+DY16Uhh;dg2`Cqe%P;~6v0e~?f1Og)M3bA99dC(P@{&w+m-p0hH7G0)i^<Bh*)uhi4OX&3ZAurFigYl!=`d5<TK@!}bNe-wER<!<Ef;QU!|o}~Q+%vUb(T>6urq@GUd%ZT$9dDTdk9sZU6hMq7j`rjebBrn<1-+TP6XU*hXi+|rokH1~zBl2+Lq?n)G#6FAjqBQbb)yx>bU*h^nmNHVVxr+K2^y9vp3Gw@?Y?jC0Nq1DrwTj|AvhfSouO9z}{e#j?;2(o=uRFB?+PP_S_#eT#ikqvE=yr+_ocr#=b0D!h<$16>f92JO;dh<BV&S4&F3(FZTZ{I&R@I}srx#$ot$HNpG2__3hhe|Z&fLSJ`-YT5{<tv&`UH$O{Hedh?;z{VMf}X1uSH!#e)zB-{*`z>|35cmUEVr=3;G7mvu@qNdhU>WxUM(sPgCEAp5~cHH&<VkeHwREL9D-CVEd1HiS{X0%B#;=h~L>&?<Kl35AE;2X&|q6?F;{dXn+47N{{gTYWn`GCwZ-`s_M#;8tIHq?E-!>twsIsGydOyGTrst|F54+hm|S*KmEz{<{<TID*Iho-2{fwMp+-?K=MuMvvtY_(KPQy)4V!O^Hs_o68|KwBiFczT;p@{fyxFb+elnbzKQspruj4CdUB1A$gk<!s4Qa;FmVw09mQ`bTSoMef1xaqvdlEivk;S#XCco)Ohw*7SyN?UG|h7p8<IDqZ*F2L@|wzO>v|Hy$iw(~Mq(=R5M^ojcxenGud8gmvKqwU<Qn^tYpg@QKv}f1o5bJ9Z<1#V0;UN9k5jf&*}ue(<W1ExVJPcN%tfxT1i8k(<Si25J41<`$ve|$DDg+~hRT{N>p&bru5lE32lC#;(d50!`zh;B977yUo>*BDWrc|a$^TN<_EOmf;uiA1h!1HS_*_>fb|-Ei-@xy7Ck`f0uPl+WO9t?~0sfP+AC>hdjwIJOlzg1B#X29+G#^GBKt6!J!-zx43o09}EIY9UxyE|r8Z(gR<9Cu1vy*41PjX^H@?bm$D!T#GlYg)Nc%rVe9`UOL;4>7TrmQ7R^RC37$Tc=4KdE9ZRJMtxc~9b8a*b`tw<z17ERML1JdS)PaW}cfz2xDleu<QoBwh~!pQS$AuWTOi1i8*9R}AD7ANhRZMe_ONGl>_-XOhoQ_A~Js@d9~_vRlfgEBg=eJZ(CkpXv1Z{9Gjr`Y#{N&ni4)0E79r)-^AobHDmKZ4gZJs|Ij6xyIS#8Yhx#JV$<&T*uJ(1>+r3c2wDHn&#2U<`GX2kCK<t?X4`5*q&Ush0f)-h{ehG>Fd$Y2=NZN#>eDmi2o2DlQ&W}MOh7+=97uL$u;gFudSYgmddgaL&*my`+=IqNb;8Cp)}14DJx3sLX0Fgl@(LgPT5FhgOqh6wj*yxpKipW<V6{y8?6gtj3ggHj3kd_T{Zt!Spj90h~>%WsP-Mi_iPZ~G0n59&x$B3PSd=CvdY9TViEE%@}$HB<b#zt$~qEzkej^DcR?`C8&VrYuCY0JHf4DdVEm%74f#{`-Mz|=6MrGsb}R^=KP7)n)BFX|CI3RjN~kP|_&x}{w!&q~`V+U3YurxWpWGqtB6rAtB<>{FIEp-<vi!;l(KN3_)4Z~>D#X0R{N$(9eR`|xG)?n2$_fMlza_pU*Ew0|;_1Yi<kgf_Rb~>uCf}y4kFqtyI^@5qc-NIpB~BynrmUT^HpKemE7W&ZD;q)6e5A78#8~2L^4rRmD!WP3+^6h&VrSw~a*fN$HTEO_MwOjHStVjP`3PlWl(i(bB9Bquxu9$z@f^9vQ{);Kkn86=C7*rWf0RmqzD47A<Qi*{hm)5fRwl2^7-fhl$-{|>h$+dtDr>K7IB^*Hs~~+u%`mbm%Srr(7)-A5QxLeuuc?<+ytJ|=$~qF;5lfS6EJLo*CQqi@A_)DYHqEcFf75-T9;0j1JPGj%`4#$WK3MS|l#L=zAU~k{0A+vCG=E0iL;j5XPvS1}P!;zpWls#C)}HXQUF4zsJS+&N`BQ$ji(KP&ay_2c<NNQ3705M~Cf8V<T#s2A7#O$oB#$IkBab9+M6666NnAqHe7u1%{}2P?{yO9l#PQ_g=^sI?Os=sEc?7wRQOm%5qav{ec@2JEkywWOOJ%0Aax~4$6PuH3Ttr@;{99$ki8f91j>JXeJ=MKf%lCe5Kn{4I^OSmKGto4!L##oru{-&_Amr}*%I*?Z)9y3p+^0`0u{L>a=Bdwl={M$^-<WGO&#&rQR9Q-8`u|Us#L!CwFwL_O6O(5n&q_>5o|QZ&u_$?K;v`~Ga-GX`PAf(Hid^TWPC>|L8f%fSR-YYF)|EJ!Tz@YezgvpDBrz9xNpeeBRbmNZE^>`|$xDzIp=n-7*%W2Hlr^LEV!Wlip3cNl<fT}4XPV~ii57W#@-6}O>q6{BuCXt97xLaT%?B!LuG*-FvRTS11mW+g#98E1$q&#pk5_htIEOfkd=_KQp=my!*o%BIu`jU~xyDxHeaTxZE2pfnvT$Ns^0xe3^YX;H{9ZF<4T*Kh>(Zwou{C*Xen;~q%JwVUK|D<UNVV5-WtWNZ<j0gfQ1%b;9r?r{U`66P@|DUaDf<ucJMx*zepY7DG;c$kOWuY&inxe8ihKxh1-Zr%<Qlt>4<YYB)4YYUJj${vdu6~he?iPbu1)jD3hyfWL%%mcFwHX&ACo_(e<sGrMV^T~Cr$H$LCB4r4CKq=<YoEZHa751uO=T$tU^APya%x?d0EEkLF`W6gS-z-^C)F2l*KB$PmATXYTQhImt0@#-)yg=G|dkaUyvUrKS+E`evo_z@elGp7=H)x7xEqC8)=%aF_7E!{k}`n{4#M7xyJM48n2LFCcj0~+#iIsjT{NEzEO|7J~1=7#+u~yh&^eVM-gk1N0Hmgnkj3otTE9hZ%p1mS#o80mAzH<xuNW!vJ44;Z^<=kpA7UZNB)7|$(I1AwS4@n9C<mGqj_3>$0BOY;%5!W8?bH`u_n1io|c%ITw^-&wB)I1nt!P*nX=T%QV=teryvhWfZY45vcGAXr%wQUL#|Ep+(i97%_H=9S6M}3Zt~oWU6GiPTw^uzisTW*w&WUHkw=g>QkGv?X=Q1MjmUc`>qI||)yZ3tHz8Ibufp#&AvPj!#P4YSxi2|QyhyI`D*0*hOEk@|1z{~nuM^!SW+vB|oLrmce&Uzp+BCnXaHX<U%GMIsk*_7+O4Ixy@gDhBqD#~KIqhYDuK6JYV;GIEi7&}tlj}ZQo95pTpOb6TJOl9|xi-y1i1*0v@ft&T-Py@Q$aBy%&#kP9^8emIp6*KCm{^RwF}cpopU1?RXqu-bmL*S19!ji2UWIW&iG|5S$@9=OFQBY}s^4&B#b}zRCJrM{O`ejbc@diC5z59W8?EfU0sPkhPoQ{^vI)fT0sNDJzsHl0BYq&)rukUnzvTb249y#`-t}pk7bT`9FG`+@rg;itO7axsg^5MT3zOF)Mv&JdA4(iXK9u|i*5?P-u>tvT;xO{}ysnSL59As@k$)uD8$l7Zf)b<){(t>1oB!*dUT-oy{{!d$^PApn%fN4zRFkv+y@?r7>kGX<W+YJm>A~?vJ&QB`7Z;cQ9s'

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
