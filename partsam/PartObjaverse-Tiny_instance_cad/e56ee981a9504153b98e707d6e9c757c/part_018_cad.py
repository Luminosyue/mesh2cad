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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_018.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_018.stl', 'source_sha256': '3d16d0ca2d661d33646952dae350ab8b549d8dd5230a437404c54c2c4135bcf2', 'input_faces': 1060, 'input_vertices': 700, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.24730001389980316, -0.2604529857635498, 0.1385655701160431], [0.4022136926651001, -0.10553935170173645, 0.2725723683834076]]}
GEOMETRY_BASE85 = 'c$}r32b2^=^zM6x3<?qyB<P^zoCL`O5+pA<vqR2lL88DAC8MB#1R0Q=vt%0B8~{;3L~sy9KoAflE3a?guZMf*{ogt7yvI3pzTf?}wz|5y>UNl(C8ANP)Hw|Pm*4m&@8W`<+J-^pH6w>HqG#0bzTJBcD>Z1yXqWMZ?bAO;7c_0%B%-~`7-5Vp+@t5P?ooxScnVkR^<m)>p2EEbM-7kaIw*2*RF9tI*Xuf9SWn9z)~D-`o>p9>QkgO(Jmrg)@Qm~PKmN;Tbs;!y-Km<E`kvj4JxYD57x6vCo=KZ*-|zT)^Ca8#M(?tHv(Bh^S>GJF$M%DckNW;57rFkX$QV_>(Iu`AKe&hM8^xd7e&8!3QP%esddclLzSDl+f~W0vnq4^|>-&2bwtXXl{ZRXjz3e|3l_cvM4Qt!J_t}Uf*?u6?Sg!xesN;4!b<v*;<80sK_)hy*SJ=Ke;(W4fKNwue^+%tzeUH=r+}pg}`lXJ^_RTqW*sojWm~7wQ`E715caD>4e>>*ke&x${QnqhC8O}eS^13P8H=caL{-i9XY(H>#Bmewvfm7;u9ol58@BVwIWcx;=>}TxlzWc!u)&B-LY~RRJ+4fDe@5|84_Jhyer|ou}<C{K$>;LOIt;Xk<9o&A=OL64;ei+LATej2o19yLklgG>P{f_UnKjZ+n|9Ez+Y{#>JeNW_EHUG^<2YI_&+4mJcpY%WZ!8mMpK76MgXT8ik&i>H@htxR0_np{#NRFH5$|)Y7R6p_lJ|4~UVC-q`=c9A%{~DJfeFMI?>=?VgFX|`uTP%r{^}~IqeqcEK?Wpf;H{ycrn~l$@@elOB%;P-${RBB~jvt(vKS7RzC;b)f|2yBP@eeeA#P#>JRQbUl@tFIwzop6#W-Ipn@vUs%>l~Lb-*k>k)2H0dnhXhYf4xnfaev^4#`B|8KiKUpZ>Q#`Q9HHm8!OtX`Ds+h%KqY^+#j^_zxmEMcd2aqzQ}5J9`j6X_Wl3lhvs>@Dz@)wRZZnR$2T0`ndiBh*uMAALUtbZWX+l)eRIzqUKg$YO_aXRU&r=?3vb3t-*BI`k5}Nr*;wiOle^o#KkxBq<=^^{=hdm&YP+6AfAcs*ZauF2J#l>8vz1Pgeqcfy_FLykQ2W*J_h`GHi_*oZ{mL=i_5(jZQ2p`#>b8A<zM#Eb<8CvqKOsk=JTB&)2;SdG*%H-!IOF4fwrd(K=bQf*_5<hH59Me0=7q-5^0*jhqj-GYC}AHL|GwoZ(l?LXx5wYVdv3DyJr@t~x_&+*N&4Oye&mNSiK?A74fy!h7?B`-BU4t}_f+W}ui6>%6X!91w>Z_$vnx1{jcXaJ+Q~V{_B|zHbpNaLwte$N(-_r$OnGjn$X>NyMxYeeKUy<d`hhDic>NCAq4w98=8^6D(^fs9wma`Q=ZAi))HnqC9k%^|yTozTpUtz_-?3bckFP^>_P5Mc<71A<ZTr55Gt~GP1%o`V?u}97<E^!U=SigzY8?D)huFTad~dbC!Au|8zGqA~wO^j0FYW6V&xn?G{{ykZxt(=mxP8n|$M-ot=Ci-gSnlV>>1y8k4vy#Xxwh?~J<iVg2)=n^lkJDjM-2k(XK$j;N8!FV|8mZ6gE#SZXU$gi!+oc|*S(e7$(U82@4|eiesJU=Zf8Iib^R7tcnHUl{ZL*F^PRlvjXKQZ>G&9*zzFs|PW#BW-l9jjoeVE{9i>{IB7OgN$Jl?lSk({yFq89Y-7k}*@0k?A>$LXNMAgnWZ`-~(-Jc-+K;vI|y-XPzFMXr$diIkB#7W<a^Q`~M0o706$-!Jdu5+yNoqT?2lj?t<d?h|#XKo)Oee*^M&I1M3sr?Er{*Tvb#)i?VpHBYwELQvL`7g%yJ<aQ$Q2p6;kk@su1!^4p-RE#SO)4H&{meC)&llaNsPPGoYsmRz!vsA(SF^IeW{4UG|Hl{jJaW6g-rp?&+c$4?()*RY53lRe?NtB0qe^prDBj>Wujk`9zki{wD;z)2b)LGe@C;Aj{_onL*Ik(JtP6kdB=%Qd)aSLd$?TW>nf<G=JRf?oZ>+hf&Ub;sDct`f&(w8bxF1@-5vRHR;mPW{CFCDYOqA=(m*Fz|?gRF9m#6IC$<p_we9YI4#e<2`Hx{3_&zr%4$??+nck9Le_I<I^_mup{9-qL2)zQ)qJf6(sS@DbGsy}DeaGrb;nWEZXUV+c!RU51R8+}gjedV|h6Qpn6Y{|Y^AWr(;-M`uQiT+es?Rn)hf936tA8PyN^S}8#b^RLqzr=Ds*A`5XzJFb7_HSlQlD-jj4d><m;#E6O7PDWaly0ZmFg`C2z7?zd6NNcHe41Oe?@8xof5*9KwcWXUdA%P^n;`wb_n))>@VMG9GfRCwpSmBY?RtMc%i~}7SJl3`x(A;hrzhF%_)Fj9dD44<S{LEIGe6Dcx4Hd4a;o~_zEj_*eTVmJ<s$vu!12HRN<U{94gb_a+YenI!Z&kr{m}j9YxlT*$^!ei2U>LCd06%z9=F|#c>WLgEJgZex6Zs?`ix4JzGp%q+c&okOOn2?<ZWIT8+#<Gb{g!l{lNXm1nCDKkFkC0IyheX-W+wfeuc(y()S<Fz<!zPv8w&cXLy`Pei)<rS!W6R!-__$es1W>=gk8JPN;FnT$Jk%%&Er580O~uf9!%9A8-D6&bPyp)%f_Uf5G!7b*vg6^UpRs-@e<Y#>bQ1!`JimcB=954g7<z$DXZL<71xL%JZRCK#h;_;Rvo@{R=fd-sRP8-<&*KjgQ}*hW!cSc>YH}=K9Wh$Gi>qL)S&+pYd_*nZolB`P}hM$H#dg*oOVUPWC-GF9ctI!S#D5bG};9+deMA=zrP2a9PcB$M?T?NzL<sKi`kGe=r-@$NAdRxq$6^V{_T_Hh5`Oiu8TMFY~;;upn9b=I879zR5E$N&3MW19{%&^(U%!I#%TR-Nz<KKVbgL_gRqx;#E5ZV|YB*_KuUj$GMJO)h<^0{(CKX-rj5(qx#u854ZDsooLk#^0QIGdqRzaXCv;9%Bu14b)AU&9aD`@0QocE-l4|FDDej8)dri@_;`?4eRY?s@$o<UhS$aH#cF(<eCwS)LyeE;SV^vbYKj^k@8Ab~e3L#=;}e*5h}T87p=x}B_a?KSxf|z!NkzGxHjQ{5;yTd3p$hl2<6!pJZ|3otT9x}#=n&_h97R*4AGp_${kCr=N#7TBk&pWlSAz6|)%x-Ax^yR2`u=oJ`M7v~j+VZ0<}>!Y$EyCA+rH)Fl2lCf$2+DRAIHo&Re#Jn$2ea#Po?_f%M!uk|K(lPpCHzq=ln&!{`|cb@9)f9>VD0*R-5}d$)oP?0;lS-kMl+7x-QHQUDs`@$K%kWuc{yJhps=nH|68<-WGjc4)Z-%uk&_iwCDYOe}=wa3-g_P5=>;@e|@^T?{j?f#x#Au*0Te*GvG6If9LmhWIxRvb$uJ|JN@+L?ZoYy598H1g!!R7{Fwb<kFR57{ct~2e`^=sFP!&7^}~FpzArkG=T(s=_I`z)_rmuTYsCAD{O{@IW4}B5&h@{qR#$Ex&)J;qhWpNTJ^8xvb{|w#$0g)ftD?tw#}IDki<7GTa6dE-eWG}LKH}>H@1J@3^M)5=*guv{`NmIUdHh?IRPBfRq306)#`Ai~@IW2Ma6eQ(zn{nL->>v~3G+k8WzlqAM;~oc_jiu(t-C?p-<hA!V1H75)t_+RnTO`QdF;Eq>bf-Kr>dc@O9Nl9Z{T_(bYE6rKKljFt8okWL&xPM``*rD)pdez)&d^4qhr<ehU1&ZMyu<Mz(w|bRp+Yf2gmnLnXRvr2QB1w+UHl}AMS_pPlH9AXKMCP^~3$pd>*`v_qSErcsZ{e-*@8!H9p~fC{KR1j>lo+2>rPUd_R2WIQkE4=KX!PMX!r6KQymW@8J2LqrYCKVSecTCCI*a&yiTUU%{padE9b-V_(;KryM$F@7LiY+)u-8`@TGvY~TDkhU*VW&-1M?U!NH16L=h^x99tMJm+_O@5G|E?;mwh`M%P3?eP!b`rPq78E^6NG9M;N-)ywc_Wgb5BuPKmcMi9c<%MeBcs7pxp5s+JfgeZleN(C{@oKxdTJn8UraP)XzPIXge>RU!Q2oJt3+|q(w(GBum$z$dRsHlwzsBvX@29rwU6GFaQ!gb}_4BtYd>#AZ8`b|{@GR$nyFKGnKMQQ<>*O_+)OL-R8#$kRv_$paGjA#8c^kD|v+qLwyne?1Xw}axL-_i+<}B5J|E3;Xzg&wL)z80b@O9UX_tka-36*)f)26BZoA?~WQ|cqNU0;QQJPt`~)O<5XzU2HrX{74EG2#I~UmafKgzD%16u#ao{)XDF=gW9*Cm~Ap-;2*#f<sEH?Rsm^<@zz*RX;sdyYO|+pcl$FyR_x!y01m5{ut5k@bypn2-SYTx!%}uL;1$1HF&*`ORwgedH6N<3$4`i|NS5Ndh)&bYCZ?*rSSD+*!uELU&{9dVe89>&ne8q$MihE(~a8?TVI~6o%s1!*!uFfs>to^->Lc&Y*CE+6Sls5P15pxceh4*zwkMTKWu$@_TA_6NZ9%^FW$m=P_HlVxmeo|gsm@MzWrQ3Y<&gs+{O%BUw-HO6}G<2Nq#;*hOIB}T0Rd3r|b1)23qs^E^K`nD;jY9vU+{_e|w+DA#8maY4h=R!`7F#NfzF(@b%UInw{r8;p=G2PR{>f>&1V16W0%0FToFnu^+ZB0wZhj`33938-e}|=&#>f2=haq%a2Ir<6HZ*{oaeWO%&f}jXcBc_x*|Ax9P_BU#5AE+i6kF_6@9~VCf+H<=$53cVop(-rwq7)pb|6@0_oLfq!@$emSMir$+mKc|12aP}jY_3jgtTalIY-9RH1%+|JBS>N?!>Ci~`Fo%MA)`~dvWb<`@?S-YKvOZ0tHm>+r$<M;~}t9}Nvx^3TccCor|a(u(_o%aeRq_=%<&(HOBPMGhEn<qm?+xIO?ukJ$~-ycY=?^{27%k~4#a~S7(Y~8!IZ+=@{`N6+Sb32=s>*rDMy$_eF>q-Bmvb?`rXQ}H|$M<fZp{`erQx&=XZ@2XGw=h3+eZH|0w=*_E^~do&(M?r<%yaCUcbn<!dH4bNq36t-KjQIpo{KuyjbVPMKZly}_%v9f?nfLy&~UZ7AMtE!&Gn<s@O4GK(I=(veb|l9@7pINN#A*I!S|qlg7kgP`w11>#YsQdG7I-}be$NrU3^{{JXq$0+AcotGowt^PqSoRey*}-bE4Yrla2TsXK}prjT4pGuR1kWZFf#QkMsDUcD@SC?#BN7UHU!|z7Kxr^M&XAxu1E4>-)GcKU9C`Kpy{WrTIDk8xKxOKREIcUthg;Ek*j?ONV*<M?X!HzQ6WVzFzv|R-*LHb&dJ@?a=QD(l=huf%i|&#Y^9LKIVP-eVpp&`Bi)zpC6A^?L6eX?WuhvM*5yrWx1Ui+oDxJ@wuTfb>j)u&jBXqjfqQ-tM=dQkM}WJt8wt0D8v4SddaH&U!U^z%)MG_d;)Wh@^#DYa%y}+??sd^rN+nWyysK;T{S*|;W_y_XGCr_J|>=fd!jO_@$uGN%j<eyS~WhtJN<dS?Rm`Chd)Je{cCsh`6$c}-QPL>?K-jlV}1Cc`}dzlasP8qQ}x6B(EaA#sqClEtm=pRq5EHBCLfn6E%o!UFh4Z^7tH5&M!VI0dbl5|-|$O5UNO(q=gT2K^HcTtvg3Q_Zc+UY_e0Nl1}@_5MrBavUt>S}o)0pr^L22*Vm^*TGU@a3<z?I-*H*s2`{w*f>3g>g<NaC^pCbK0QZ>F0O?Np-`X<I9nCeub^gRocc)d4FOpw0+`F!N<gYl{zUk5%ebN0rme#YkKJTPNjtm<d+o4npnuZmIq{Cqp#PbDvimVWS`k(>vz&pV;|*|8?K6Fc#^>Sv+byuSJjR^wp)xP#Yko^Hvio%{S=lV?*$H9p=IUasGzsT!Za!3=yKai_i-pJ3lpyiQkEQRCyCwwTxHA0Mdk@&6gg{?$Tie9VZ#d|y!PJvBbY-oN;|v`}^)pUBlbPd=!n-zSIfb$sXizL0%0S1tV<6@I|+G5>u{)^h!3hF+&(erO#X+`#?8`x2pb5$1>TOtCHOdna)|UwS=B`a$QttjlK-q#u~QlJj}~qjAzVd;>WDPj8<reNWpm{9Zx#O)=8<7kkd<{lvP7(l_%T<@~>P(FxVgKQs7x;PrCxsy|0_@%?hdJF(LD&Roaya6v}CPg%U3w~Oa6p*$Amhn_d4-Oc0E>@?@G+;vV$KlpYepWml6Op?AI`P_)Bm>_*)+oybf&+vYn^aG<avEMjLjP$+Fm-70W_x!kOf7(1=FDw2@R_!-`hyCBKB&zy(w(vYJa57%{p6gZle!2I7Sm`^T3kNo?wa3kWcn|jn?~8`6OT+xo`6b-}_IC%=IEVY8d3ep_@htkfdXLe2^ceDXrf9h?f=iC`alv~mq4QmsA3A?!h~@oqzfjM&{Z-iamHk)WFTnSgf381IUmDN-x!*@`H_Q*spE9Q~&xfe{BgglY@1yRI0@u&*I1KoXpD#V>lPrDDnem*5AGS}DzQ0mEey&xeb)xjmWv{bev0j4oL+^W!s}(POZ|`NiPDhuEQ~uPUyuYQdtNsKg_vH5p&62UIKX{)o^!(rHPub#J|Ij-zYJZW(jHolJ|K6q#`MGzh+|jE4&ijOePN@Czz1Yur;AO@Wsz15s@q325kEs0(;ClqY?c3D;8o%e`{PTFD+Aq(7tNgs{!BW+K|F+G1{aIy^>ZjQ`ir+J=IGy{m{72p|+>bcp<0*EQ{eB7RKGE@g1LD+uqIWd=2A+3?K2N!x?VPQ{CaC*9<M-^g9~?4K-6#6jy=D7m^=9h&%JBn^@0^d;=Vkv<C-t78aglwqR2TJLqT?H7JE`{%jjHdmKl~5QZ(F(~OW${4D_@6fXqF^>)42}0*Dz7~LFc)_?WzgV_nK*W9hI*XFMa=@WS(!Oi^QpRW`4!@r=PqZtNK~FBj#t080E*+<ocuU>HfDa!1H`xmT2XdNQd^XsQvP%y2bNtw{b%H0epTMIP{C&-$!5Zd2?Ti-rwx}Jv;x)c(uR2V+GiMzF+OHdFc+%+uD2d{?6XTevP$ie|_se<@`K#rP?olo7$Y8C(h^hyJE_4`~S^Q-)9L_FU$KiZ-$z0j_-GT=X1<x)OXr(-UrxRh1=hKTAeQ(-~aDPb-wV;sKw*9Gn&tjn74tQwb1`){k}c?K)d7Wefz-UI^0g0Ydo*go=K9v?{pOV4UQy8-&pG6_f%(XjFY|}&(i`Y7sjaiW!~ldnRW6BRewoFzV6C5C|Ua6yh}MB`Z^>^-@IOw^V_O=@v8ogeVoUBFBhx!YixbaS4H0CJhr4Q*PpaZeg7qJ7Ct^-2<7=O-}!!)<9nRXBb?`TU$^6No3ccGkH#}_6p#O=jtO#}_&y%ZKHifIJ$EhW=j}e~$@gE*ecV9yecqnx`(NgOiOLVXU(sbQxAQ?W{XIVTzRHc%_xOyj=JD|wbXI*&EimMB9?ya7hxWI~Vm^*o*P-i>mhj7`sPC6KzR&T|PfznDJPz+p*5AK7$iDa76g55}AN51y8L^c8d{fo;`#dGKbARx;Ug*9%-45=L<2&PDaTm|GCVSNP_<T#)51!kt#wXl&=85B*@I%i5D(vR{Mf*-aeb>I@c9!t^3gwfd`?!9k>hW?uIKJuBcaBTx{k*@^s>REB;wyE4_ZNQXefvVk*#GUN`rf6dCHv-8_Cwn(cwE&FeGZcI6p#PG>gv4g`2IuH^z+;3bL>}cppJ_#^LcJ(B)=CI`d%u0!||Qx!z<2XJ~vRuF_7k0u7C5X`hIJmE&D#_`vT55hxyL;WX;q;J}x(&s_)x+%d_vndv~Gy{B^DKcKt(Z4$F1tUtHVvjbkeh%XJrQJC6NE2h{hJ18v6JzQ5iP^}S}#@4wr=?_}?zvi;!I>s<d#_oHfEZ_M+Pt!?7;_pI0FwSBW?g8E*zx9&*W_wJ8X-?R4A8O8p=X!X5pGy7`W_bphPqT0{8mbd%G`V`rI@aR3RAL&xxLk}Fe&+R+DGd>$qU$Fg0Bkj-E{O6N6Z!CJ#_Wdt9C(GmOUHF#md!9wA@3VV)*Wz|s6tLUz#9!d^VB2QwUyfAQtAW<dZQmE{tgcsmRr>LEr~jkB-}>PIZfDwK{r%R`!?{15Q}O40`MdDnDabtE_RZSo)cMHw+Ly`?y&sio8T()Sa7?yiK3~OtiIFOQ2A_S){Vz6J=fmrJx&DGKYF(ID_wjx?zO%o-9<qJo@@@6Kb^qnVwjaE7`_=c>Bh+7)*uTrWs!TcS3cxBEj2uR<uHsKikV*d>{h$A|MBfVkSASZfY?+GxpMP5-<3_h(?6k@j=pJx&t8dw?5(Rw=90ks8l|oj%B`(8Qi$Yukh4^2q&QPn)8fp)^5?md;oZ7I;eydD}?gmc>Z?noXtGzEQ?d)b<0qzX`)+!%b+nZw5D{62dE^Kfi{=ncu+{oZU{FT9lI6DgQ=P1NM6ymyWF2tX>xe(8Gb0MDV=0g0bn+tJQHy7gkZZ5<tP>4&S5dUCsA?^*O{Uk1eG5*eA?GOGAT#)w5YX3WoG3i0@60kGwG{!@r8^A-s&hevTMaP+Rl>60jC#Jbj#-Kl^Vy!i3dawta+A3BxBdt~5K_M=QLQH?_WSLc|npH+Z*SMHT3&Q{0DpRd^j++bd2sanvI&Ln+zo8I+fkK=Og?NF%g}9-?g}8#jg}8{pg}9i(g}Ac8g}9Hwh4@E<3vnqF;s6Tqdu}eo-P~M=$3ba7i6>fRvzw16=??H$U^=$n;g~mt<^neb=KzzIfxZDQ19pyIY8;=`NNdjVGH?t_;#gIOW(HRWQ_e_d^?#nF3!(43n5htN0Fyq0da>4@foZKrA>UAYq!qzbh^cK_|La6fScfs22&OR`Z<Q~tvI&KFI|}h$=pyi5@BtL!edJr)YhslGD8z505Wi`aftb6iQHTR5#5Bh{piiq%h}S|lfk)8VvGy~M!G*XI^mBvxsf*j1k3#$nbQPHTRTh1F6Py+LI=HZl_w7Fv;(jQ5v9I~8Qpzf+P>9n(Gl8ki_tEa_;0!3lX$)S=g|VKg5PuDiwoP2k;Qh~zLYxz2gcy&nFcwsZ3!o5hbaCIRp?{gcSx~B>?f0>7X;6q=DEY9j)ZSCHxe;8`&4qYA=ExMxlYQV_D8yT#1HoIt>rn<`zSOYV%S-1J6yjyjJm6*ErO*$+OTja&^19VlZA-7B5Pt++VlaOMK4`Gk0FyQo{1IZ(wt@qQN#g_$adAxAUvPFe$E0^%uec9l(x!sDBPOjUI5T3>-(9b`u8U*RdV-f49FravToW;AbHQ~HlXeum5;19l;1Mp4Nrwu~;pUk1zUvkDMNHa4a1X?!9}CWcnDh_VD{kQ8n6#1LWd_HjM+JKkleQFG4>4(^;8lo8lLUY2;+S-#;5XeIlRj|0;(mxpTM6!on6#nbHxQHFbiLwcE{;i?3tnz;OnOXkEySd)1=mMR+Ewtkh)Gif`&}H9juZTrn`6>{T(7u4V$wE(dm$!mEI2D-(m!3VxV4L8(zb%XF*qhYA-FbT(sqJBMoijW@M^@Qrvy)SaZEZ<a85VJq>o*%cmQJ3c7l5&CT%7-8)DKsu2<aA#W87T!7B`oNn-@pK}_07a0A4oJq52pOnOf6G#AID)4^Af9}l1q*N0MGtdE%ZXM?pF_-F7)Xj|||@OWq(cs%$zl=9+r#KgUkEAN7PgJYqT7h@3<mqf0t2QCRN45hqS7%}l7<jQ*BL*OP*%8N}96aQkcHV6L#9u4gX9u1xZO#n{<-+)qHyn&dwA9Ce=a6fQ7l=5OcV&byMl^=u4f{Q{aFBU~id<40&5%>tWC6w}FOT@&N4S3+o;IYt1@L2FPXcBlD_!gA%;w{9)gOMvAfCqyUp_CUB5fguaT-gx(0k}An@?vqs#3piObFc|+52d`=9x-vyU~LT!g2zF-g2#bpKvTdoz_+247jGjb{sg)5AMhvOWGLmuWW>akkSiO5D}hTvDKC~nOne-<vMu;HI1);EF%mKHZw6~S@NeLW(C*-g;91a9;920mpp+N?LQFi?#rhaL7JL#)dGRD-;>yUC&A^qx<)D-o%ONI?cCmH_M}xaVDKB<MOnl8??F7CCo(k;=o(i4=JqMlxz6Yh8c@O#-m~tlN$4$`2f+;^XhW;&hBx2IFg2y8!-5~fnV$vsqDL+1e_7WV6m~@9=%8xsssRb8COzIL$`OyX4EVv0`(iVa#Kem8A5Ih<&={mua5R+~ad;>A*Q^AxUpF;Zzjz>(oQ!wSnozS#`iy|g<3#R<&hHequ5;18z!IU4{K_3bpi<or1;Ax0Sw+Oz4nDm)o%8$>W0|h4{Cfy~N^5ZUOdcnmJlco|(`7srAtKjyCNxKLR8XS}UBX}HQ(v5;=AST@=_%>qF=YlCeK8FqyoQ#-sw_wVTyP+8bmqJXMMlj{aG|+8=BN3B!6HNKB8}yOjiHJ!z3!a6Tbi3fc5R<+TO!@HzbhO};h)MSdru?`Eno)2$#H8s2Q+`Yb-7dI0V$z<1DL?jvJ{CL`G3i#pa}bm65PT2u4)A>_<;?rgT42hRlot=85I2NUUTlb%_@cqO7EC%y@CL-Be!))=ll~!?^5P%RK7w~3CXEwJc`*)JTCfW-X%WGc7mGj-3vPj!G(s@t#R%vn!Rru{juE^GG3gY+PZ5*e6ij*XCUk({orp;j1XEs2fR-2RMod~vFy+N!(4&IeAtr4jnDSy9=&yp;BPRV+@D{|R(*-|6O!}u_%8P$OqXh3lOqwK^@?sLSqTp1BNlOT(yjTKyOmG*(q@4s)UhD+DB6uTW(g}jMAts$E_&H+IJAx@M-hqx1yc;oTieSo%DbNoEr$J0wMlj{YGSCx(yCEj+Dwy(OSLjv2n-P;v7Q7uX>1@F-5R={&OnLDxbiCj_h)GWgro4CxT19X=#H1AjQ(mk9jS<`vF=-FMloxwIe;2$JG3jT5cOWL6EBHQQ(hGtqXI_BT1Rq3xyoN$t2TFOd4r1a%2J0yBA#eoL4~_u0hyDR>4~~aYUW`XfJjlfw2Ob2z2c^7t4>55Ba%B;41h_tw@?w3&#MfP{5#a0KkD-(oKSoS^#9$o*J_2q5odRwF?hL&N?hH<ZQeI3%Og!AhngAXS{u@ep@o&V$Es-mWfm?zbKq)UaKumnY#o7jZ1Kbo!d9f*CV$)##6l{W9L8pUTfql?F!9H*@l=5OSV&X9_)+F#4@Ixr&#fONATO(JN0JjD=f>K^=gqZl2i?tK@7PuAkiox6peB5B206q?G1Dy$O1MUXB1MUVs38lPv5;5@v7i$W50{9V>^5P@J#BGr)%YfU0n?NZqHbG2$+r`=yd>h;WN_nvZV&Z6nbuu^_+yOcp+yUGJdKcUSd>Tr5@ib!MNiNn?;7Q;oP|Ax>5EHjYuB-rV4{i>nyx1Hu@n0_19^k*gJ}BiyA7bKIgY`3TEVv7FF1QQ07xV(S7x(~_a^?Z37kmx*kv>Nvtu2`HV{PaX!4Zf_YY1+SnDisT@rX$Sf+;@+phE=TLrhAa8#zq*F+1{PAHnqzlXe$O`LR1Rv-=f)jF_~pV9Jkmp-Tm~KulUwaA(A%bp<CPCS56*^5aVA2*H0NCZ*4f9H#u319`Hq;0B0EdkCid*aMoy{fe6+CT$?tG&m+*Cb$)1Qm<eiV$ynolM$1y5={AV74%cV4-u2n=SB`wetZ*ovY+5ah)H`2ru^6w`iA=zw?a(XOfcogX3*t=+aM;bCAb@6()xl=A}0M-Fy+T@p?<-S5R=m9Mh;Vcd<%K9zu+c_NqY&V{MZYc)%}V)ASP`snDS$5=r@8pASSIXxCdg=j|HDbOuAYy<;T^~$%3CCCZ*4f9H#u36M1rg;O2-)dkd!g*c+P7{fd2vNjnOr{MZq?LU0$vq;&-MLQL8~@BzdPz-yqCGuJ?;f#+LgmsR#a&wv+MWvEpKLkEJLpUsC32G0k70UacGAY#%1f`=j|9U^!UV$y|z_aG+SE%*##((eWDLQJ|-@O;Gc(MRG6)_9boa|hG|rWY*SR(TJa73}=10`xs_1#o$2e!*E0lfEI?jhNIW*g#DB(s;$MBPM-Kum>^eyMoIhCM_$t0^$njBQd=^b-~i_T&(-S-&^IPRr0u5Uvo1%KcnCK9zQowh+o3XE%-IWq?y3fW+r&VKO??~_J4++27d?s9=sRvcj)t8=sv+05R?8SnELt?^d)|F-YP#><yYug@Y`0M0#^CY#riJT`Pq5se`tdW@j2+fg6Vhvg}x)W0AkYj!Eb{LfO8=xrfuhfUKV^7G3k$je?UxnM(}yW=g~*vELO>Fm8#I<;ObVXWR<s|?|_}3Wr4m0Ce1APO~h~Eci)8O6I=-~X+>~#a3ydx#MQCwYS1cziz6m2CO9`@(zgX?L7WABB&PSBD!cgoCeln`dY5UHi{Eu3T@PN2-<b`rjF{eenuXt+h2L@Bk4o+0_o7G(f%9Tpd7!CXuimd(kM`GN8?*5{g|MAM*v1U}9{qkQXhy-65tDu>crjwqMS|BOCS50Z6=Kqrf@dKnohi5wV$y<wQzK4|J`$g|mS<^8&q7Op^IPRTtCWM52UoR96{`$~4g=@4)<zerc%VLTA?s(wtx^J78l2YJP8zE$fX)Yxwti=ZRmMW+37&+QbS8L^RR&vSDs&o{>O`R)>2UB=)L9Ju8ccO+p&sc+;7eAY=2+zlbe`Z`h)HvRbGmrn=0X>M=YoHMz5vs<I$}Gd&t1&5E$-x|Kc~++0Xz&m8M+X>z$$+1w;%g62|uGcv!F}Cv%q7ZpMj@hJVrxjfT>?!qHkYf|B1)ocO#)gz>TeAyw56qq36N*te@4e$~P|7)h=e57w=+jkmdzPqRo8J8sNp)=NZsR;9oGdG=8KscC|52rebbR#Xb>N#n19WyMXDKX0XcF2J0sV^Ky&7b#Wcis;Hj>^WaN^mFg1D!Fc6@W&oG5N>Qu)WU%fxm=|L`(L5TCbwV7`$mPzF>i_g#nZEi*_Yj8qk4?jWQ-4iG{$>}et<aZNA{wQk_wucCx7)sWOrYKv{|nEdtz!'

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
