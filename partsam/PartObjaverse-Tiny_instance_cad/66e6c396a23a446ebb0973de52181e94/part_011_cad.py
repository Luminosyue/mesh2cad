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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_011.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_011.stl', 'source_sha256': 'ce45fe9342f6d6ffe922504fe3ba0cd144119fc81216f060dd155c7be594dd6f', 'input_faces': 842, 'input_vertices': 509, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09483310580253601, -0.3233487010002136, -0.11016745865345001], [0.2783378064632416, -0.23578700423240662, 0.24133966863155365]]}
GEOMETRY_BASE85 = 'c$}r21yod9*#6JhVk@YaV_-L^sHh`~9q6@lP_Y9AEQ~R+z!vPW0~-Y_IH({XSQyu9jdibz-R*bwexA7uuKQo>zrK&V-u3)=*zEJ}Jo}u%>)9@I7JCI>Wt2r5H~-^WOHoARR_v7t-sAm-5Ayb{F~(=IPRTEQ@nzK&9lLe#?4?sCC;=4*d;1O=U$LRSqT3MHiq-TLhm0NXH{NT^fU)BTdkep%*C=0a&G#MV<>Re=U#V`b2G#V=m8<Ee>Hn8sc3KLiZ!M#mYHF+*dL>3vgU_(TQoXuL-;!W|S$uEuc)45pos?t3*LRJO<xNjEMo9l^6X~0(t&-){?rX!PA3RX{mRzsk_ehSEI&K-t=U5_rMK^M@tS`qo=_>&-sq**h>JJIE{Ph#pT^e~wmYaQhuTbNl4abFV7<5LKH@zw<^HINFJ0blsUuB-kt@yRFzJ%A(SF<igJ>O<*m*peANMD)P^{Vt2<`0wgZ}vDTeDkI<GEYOczQ^RxZ!VO+K4KU0|0`^zEdMLulx*+qe6k*;&I;Ks<Lw~n8!iRQ>nbOlWuE5C;nFuYFD`xcRJ3fb>Xd|fy39rSqDMDK-}FQJCeI$o)2*Pa$8yLiTGoH_J=%M9N}wzs<t}|?@do6X|CpC-$DDrfBd5xG)HcQBxT}vnV`Tj+(Lc)J<qPC>zV4L1zQrrlU%sPXQ(OPXdena~Vu|eE2X$1brMq90evhiMKTY8c;YS}r{}j$A$I-I6x%4eF_2}nAHBQL#dzMPyuy;Q4Q5Q^*-@jcieN&QxdZzA~FY}+8fcl@MA<u^mLuES`T!FvP^CJ4K`&Oa)?C()exggZvHD8p>=bTHdY?nC{^*?gkBJ-*_Uizx%bhOK7bch_^HWAV{b$KM`p^~YcNw#OvHR&6hJx9A<IiHkTwdZNs4!Z!<Z;n_Zb;?ZXn^!wxeiplXMCKW^3*{pg;ku^q0QvKtXQXecaToJH>(R9`zx4&r$m_;;k>%BHxem(fHuRRhK6M$^_4~ncJ{t%7pnUb=$j9~0Q2f3seWh>`*5muuJ7oRO^PZLY)b4=(ymMz4`lkl`s1>sR)fcT~{mNWF>6^OuMg1pQu9oF){E)t7XE@q>sl`#LwRCav=bxsaz0FeOI#S(oNnfq78~JR$eL&`!Yo7G=2U=lWc=X*a%Z=P2eN%8C)>qfga(x+h?vlRJZ$9des<BM|UP8`zS>L3IsK21s5jh@##iVa>&WCya+F#~r=~7qvrV%rdzkgpj&z0@b(pR23qP?R($vh3k>YcNl&!!F?wqkr-rEki#5cNlHMxHKHq^}&@it+kYV2`}+&RF<SZ)Bbpx5RMy{iUV}GS4$}FrQy+k^7Q<(kSWcU$&L?=uel%IMtt)fc115_1DZI$6IxphkEWL$a?gnJE0$&2TI=@ABghJ?9q=i7NDMS8)bRpypkC2KNm}1wO@nsBkIa=G{^3ezOiKh`r)NL=3nPn)YG6B>QSBL`Z3f<MLzZ)QU09~<FWP!d}9fW@869vpK4}KlzOk5^v&ynFis=0!f(4D_aj5^48CDhUR*ct0NE~M>mt%O%_)cZ+$l`fubk|UdV=Ol-)K56*P+p2U}A=T(2telq;F_KJv|)I|MR9wUv*g_eKkj0+<zCBLq5F@q5jYq^c(9jPCP7q<x>deiN`ZJZw;%$rEm6fK|kb9L;c<-aNVGTa-LfPe#!dHMNdoL*v1R<-*{2>zajn>>N#8$e!v2Z`w3l={CT4m^18;fY8XF%C-_DW>;tRD$bL{SRFb}GHyQmudpXASRBiZ^(=d)_XG&kWRY&@!JBjGe4LXctPy_h;YoLD)2FiAsZx4iDB|GYwUl#4T;g5XMwxfTXwjj?@0VuC}U$o6fO^rhN!Xsrph7au%ZGHW3z9HWU=^MQ}$@<NQtE2pnGfB4dR`K76aq>^#buG9btt*25yl@`=`D3!YCAvPwY0zcqE8HIpMH}I|Gq2#fjW1(f?I?%qp1g|k4acFL*4fa%S?(hrr(*EucqjgsugrySc=r_btdGTbxqZ*zn<ECIpX;r`dfWaQ`E+tZo)14K+WLmyeC2Dl^HN70f<JP4f~{{E313g&oRk;-=3HoRu>|Rxp5&9h@t3>Y_tZca+%I?PrLV76A9+@6jqzJu8P}a0aY0_U=Mk)nA+>qkd^pE$%7*rCaXxRmPAxC4Wbh3q?J(}Su42B`Z-DYy{BYgyt@65-@r_Xbo<dl^1xh8_`YL_nZ@&IdJ^E+DxD53uzxnD?H(WQ@6*-@cCp(~g_Gajx!h5malgA-XuNJ81$_=!)>JHqW>a<5bX_>Ge-oU>6yKkXyTGR>sFkMA^7ldNoY#W63a=*0{%7OLn;fp*A?nn9KS#Td3<OhG-O61?}HP)l^RP;lmB;;>uhxt@?uJp}Z@0Oc&F%O&0!*wgwMgGH9VxIR4MEQI<(a&oJB-#2#?>aaaITgkHzPJ(fc==0Tf9W#T<BLsbZ(1wlKN;)OR3r@fE4?wk0sYYr<MyMUo9f{2X^ehLI)rwubwPjTxQzCeJBohxuZj6wqb=^s10r!<|H7AT$K5<KHbZ+&j(IW9UtL7~VLn(#`Lm;3z1#3hJK(-B_ZIRWe-}TmavJS&c#nSGZ-MW=S*{mlLSwA2+ON<q$NZRwU&<oCOrKExE7q^6NF2^FlfR*#L$hEXu74Q$=hY?4dTMpScune)XzN>QX7u%KGfUq%%N2gnP|VL^S){Kn@5^;@6z8g(_R|0Neq^V^{5KVqzB$;8`JZ(h=I2I7)L$_x?#uduxL-JwLY_x{Vt#&m$NRV&@{C5F#!8ux|B9x_Ctwox)w)iYf2Z2wx*h(&xc5xKyt>s6^=!Y7{bc)a%%8fQq;Gos1N&b0hnTlrJdx+)*|>jI8i4$-_eY)`8liu9Kh?h<fP8o^(g)~}PtAe2uJb7LTW}@Jj|JY+*T)}_<F3YaMZY~5hWZbTK|lP}5&85QooqV~t?SD)aSZx@`LB%YCAS~)2|tDP>u-<svw1S=say-^4c<5P<7c8DmSBAukMzSnxo<Y=S=kEX^`a>9&mM^Kdm737ErSQ(oc3oh^3Oj6?M+#Tc^t9{<Kj^o=loOcaPFVG3;ECX#JGe$MSsTbL7q$S{y|w8f%%ql1pO9sAVYsDX-DB7R51U&beOlM6R0QD3*%d3H_q`6vB)PTH|meOi~E%48MMpoEBePF1oihzK|K|>VjnBxj(x^*3*}Fb#(8z;N6gRXkI}9lU(o-%60zQW-XqV(J!CzGfmd<=?f(Pi>o!IHA;*w^l#(LL?|zt}KP}gEDYpG)8r2#1&6-(Lu>NY{{u@yP=i5v6@SFBWKLqB&IOZ;b`X`;hezo{>lC7^enNiQWC_JBUE`jTQXp41mtS#ox^cvDPZ_JrtA2tkai~4n+Q9h+A_Teq<;g|MBd!0kiXYgw_L_PlBP`=wA@OfS`IDWvsw_$+v)nUuA|6Do2=a#`}Z{P@&cYBEP`6f!=GIJW*JMJs?)#vk5@be`Y_i_%nuZ;~syFTK%Smiphtl5I=Hg!av-mkI$zT1xSQ!-~b4=X$NqI|LMIB&<6!MNYw55G$@xh~A>9Ps|4<RP^8Lr&}`&3w@h1#ck#zBnfsyX3)qtMw=HH^yLmgYo=nSp69O&oSHwdSc$z|A79{*`ps$+(172zo7o-*U+v@&oEE=7P=toOKp$m0#}|7juw`_rS%!CqrkUVzxj$uU#&M5`^K2YnBNC0OJC_Z9_@0tg?uX3kiL0wLpk4!^Y`FANSGVyvFj^+eWn8F&%?c>Z;TE>d-HWb{ZGcA{-*|<D-Nu|`>a|4($|l!fPJ!mD)z%tbC5sJQA)L`c;DB0iS$kD|3Z5ckKkNAV;l0xd>rHJi+w?#dK~$0c!T*?ejDx|)uM6T#OfH|sXy@C>X(FiX1&9CqvHYY<L6PnS0$Xs^15K(7*P14%qNov?x&TPp?;-;^wkzMWdE3_x5Rs#JM~fCWiFnB_BN3HpfvZ8zH%1(j9RW0=IiuUs3&m&o<|DqL%T+MqWs2==(jqJu-`4734hvd?0e^XW1hSXmcAvlB;P07#o79XY>%<;Md5sJZnqr%L>=EB_Q3u!d<E(+bWZw~W=G|^P`-r0f6*K54e^!h+ERF*^!34y(XOB8v3~_0lD_dsA6$2Xhpfk9h(h_)ml&@_bFfZ!#G&7|%*4Fyc@gWO)*F=XKN0I??JM~n*0AdX^7(iN{orrG`@z$hFG=4H?-LAdSI5};`nz~uGlg!)zG0VN`l@9#^0D{EeX3<a>6?ZR$90pB;(fwQd+A%g<9)k%LP6|rF2zy4?s}|?HN~;cyOcov?$M}c^f2^WP$`su6_cTU<3DAjZ{TycVdO{j=gM-(|LtJpAB6LVsec9On=ed6Kjd19`8l;B%JX^IFy|HSv)8KNx~+5Iy5BtUzNJ8Qly^Ri^_75iuK&XY`R{y>bzS{B`k`cf^mA35tJRn{=WKob^8r}bX@zhf+za3Qups<#3Ak>OEBw@U=(l~}ao?ZV5dGkF1MLkwhkZG>0riJnK>w`p!#+~E8OCMdT<o878)BVD!B;NeImO!l=Iid#H+DUWb+;@(^7L+wdS-OQdUwKoOR3coc}^;d^3j<wpQGU`Z?mJ{$|R$IMz%&hgWux1N9tU#_4RY?P*0C0c)$0cJ?am1LjEn<VLyG<9piNy=W5fJyU1sH4~)z7o0x~ok`ruw>v_z4{TllDMsL*P_Y?d7t@iS|YD|CB)4B}qkG0EV|GhH+<+ESI{;;FtSzBK}WGL3@f=`&|ql_re`?$Vp8(jArd`tDA7{{oII49H_gns+F2L0e0qGEmw#<*7;B(JM)@D2On{-Mb8;705x#ziuJedA%sXMJhpS-pQO#%Tn6z6Vw=XGZ^LABj9mR=~M}=YP{`_y(TG^m|7m&sSrRe^#Eu`^?7YD|vj7&$?`U?(j&k^_2(ZaPFGE5T9qX84usBFP@L~IbeMa^@Y#RJM@v;u>Z{UL;lwDwp$;ZSGM>gpI-eiAG*xNJXtgu`Baa?d}|ekb+Ky-+V$%Z@(&z=bx}V6^%wt!aWU0Nu=NcId@o&M4c>d}XP|rtKF2hB@4aB_n_FQ0S_Y{&PbQnNzP>lbeWYDnimh*YS0C$_`>i2lHtO$l1^dH<OSm6Zn1g)yp3PL#^}MZbPI`dnwfD<$em+Y7iyOv$D&7NIuFOR~wGL!xmnrXjl()YB$v5PJt*?~+!uP1xWqI?~AoTx_5L|cZ7tHh6V3g<QQ0Du&F^<buV_dB7o!tMyeK~X;+BIMo)}7lXJQqi-M?D?$VqK5vj`3=-0r~UuIHR2h?ibs(qd$Y)`8<+{dDVF*e7;XmIt<2o|FH}8bN?~Mti(BR&mQ>xebE20XYqcZK^U$()fxG(`um)%Z>`5t<#KEWe|k&gIV=G8$EF9-5Bs7pj*TO*zCy#%|E)SAPyYw;w!Y$k&q0*;lQBOdj-dZP%)ofne}wb#%t-hf&!Qi0oXOxD2Jybh=LO5jW5_3}1J3iiM<CD7Com7sZoq!Br@YL^Q1}$;8F3HucKC42|1;6(pH8#k=P=-N)3GZ2(1Exw^IT{34N<Rg-A|o)E<X$3`d;GDH@V-c{&C2&Demuv4>^);ebX|WOO=x+<vycKO+x<1_F#Ntz41BXn)B#qzHiYti^M#9cLDtt$@gs4ozefBE}{N;U2uPY-4E;K))mw<<Sh232E*`tI{zxJYs`Z2I<pG<#*S-f7uTJ-F$d0dXRf2X^?7{f9rVA?pJ?y3dg#yQ3g*d+`{>X2I2WmTwqsmwKf^qU>w*34k^|P=g6GJ8UlYtj_l21MJ6_<rwfErtiS=`$voBFU&qb!`+i~4S?~qUGVmue{eXP0H`waOQJc6(;vVFvLM`PbJyz)x1^$p4RT*K0JEYANgzrZ(jfNxg}=h7<QGt3ji`cfBceYMCs^yl(ExIZ3)Z`q3Vq7Pq){NMjXKE-=xeBLamT$c41YGd6wl*WD%qm#bb4WHMTzsD!o`j(Ydu)nz(@SgBaCh04icH(~e#!o&!S{7u1|E2@_;n`)(+oD<Fe;$GJ)vOqddtA25w(H9nkLOjrE+_JAu^avHEdb~I-nmgez6$ow3zhLcd3_=2n=<3QoI3SboUL!9Z>FyfDU9}B$Npo=5fyLio9G+qn?JzU$K=6%ZR!i0OI1hIGpsYNd&P{;2fr0ZzvadAsquQh48D2xKCGkeBjf(dH_|ulDvA8n@)+NFu1U7Oh4a(&-45&GS$ULiejW39`A@tb%uxaTW_^DZ*XW$Bum8=rtcI_Y<mYtj2cEa}&HNm}9F`yFs4JD=hv0KwV_0|wU*-D~_0(<jTi&WDf06UB{zv4q0ltzS`?+O`5%=YfHPEgLc%P;g8y;ut8|a(q8|T(UJyrF%pN{uQvGw(q)tI-%obcXeYc2F=x8}&-`kphkHu5ZU0{hI%Nc{c4-8z^j$MAWLVeoe3Q>-rX^uf7Hxu1mdkFP8889IaS*?e(-&(r|*|7w=u{BKM(a6aV1KJWB5=JUX2sOLP+lWHZtpW4tI{`EJQx7KrGwHC;;bACRL{EV~pjr7g*jl){Px6n6i#OLOp=!a*@@P14`uNCUI-p8%yc8As&m+wO{Pqy#F_-=!*elCyl$-c<HP8*cx-^;1Jeqo=y*B0eV;rw8Hx+&qmeA92f_4&e5+$8fijcJE*A3X=x<$DjSZ>jSM^&IM*VC$>&jr0x0J78Rrej(3}xsz>u>pA4#=l2F3(Qg%AV4j4w#(V8^9W%^-(~D#0Y<&}bBYo5I&Zz%YKfEuURv6<|rVHB3^P8zqSc0u@@q=%quk`DR@&jLC96Nu+=c;M&^{p^}4E%geozgAiI(<4X-qyF~X?X(QoU=RHTQ(K-lz)<F>#MU?VO$RR;@mr^7p}|qW6CjqoPRd<LH*BaVqG^WfalQaeUX3WE$FxFj#wAN`=fr3ZMg6IH^p<}XZWV}cTqn7F3iKiM&wzf3E%4`p11W4%SNN0$Hbw%&R!@Vl!A8sISu<*&|s8zIE4D&cf`1dd87Y%URCeU!RH@6hN3@x|HeLMN=3W=hHv;b3gu%P;<={m2=q^UGWxB56xMIQQScKYk$*o0@AsaM%5Z;IYh*iT>zjY~14g5N?mtAk5`D0KBgevDfzSO_hnx6&mAB(i5C8tk_#ht7NBMo>clF_OsB@yNuYZX5Ert%Un760=&|ZH2tGFD%=U<;Epgf=7EiU_Hc}w6#^r!20T(^^5!hiWD`g)%L%#+52G0$tij{7g)Kwk};hJN$jo8h^`kaZ@{IYTn!|GRIbuaujGdU#$k9ejlQ^4fWrKao?A&*>1n-;N4I`A!z}^R{<rSIhb6AMV3y<q7e&zJBpn)WdVKdX2tEHtgH2CSpClTY!4_cTM{I?XW+X7h!z)UdzDGN0bgh@cDN;=EZKvXGCy@{onF^DEjk{<*2`CcZ{QZb?jq4E07Q0N2&cb!~X?e2`Y&BHpw05$%&!3?ugS^ch=|ka%<uLH4J$sG)b`amD633Pu0v=@3}W3Pk!EQIBbvWMr}erFL;OhKL0*JiP@H6p6l<GMSqS9L%aBQDaHZ=<8A$a|Bl7#D|=CYy#nz0xu<d8KCBD=eUYU+KA+O}K7e{kCSsnvN#);D!vFVk<jDSL*Q+C_hwqcE_XV{|B>LfK9n2rE6DU9DIM&5!d=73*?1uT!@f6DYHAkMQ{^x9c%PV}IZuWSVp}b1pMBn%=8h$N&o@==L1mn0%Mg1<guG;bx-t+8_gP;8*@>y93{nO?W_tmi|e<s(trk)x8)q!L6VkJLU)Seu)$f?*XL%eMM$$>D%msS7!pBxN#`TzPS2d*x4{;&V!pq`dP9W5F&1UH~oBR3#BQ!A03$u+6v$Ti7TsU^u($xd2i)*=hLOlT%0{Y!8*Y7Vl{f@Gl%WTC~#*~q!5Wyrb6d8tlhC+3rvAvh<s5IH9~D?@M|Y7ufCvOTpFS!hwRJ-INo1i3J|EVUw8XkBtya&2l8a&2-$Y8SH57UYIxSE?J?mFz-oM0O$9qShx1tw9!Ag<OlQr<NxRElw7io2)12qh=us%}mZm&Q4Xx;!8)?aXhj!1lv*bknP9?sP<%g_Im+_;L_Bx<g)DF(hR}XsSU{u*^kv3f-6&9$S&-o$_&93sCu%VZLYu&oS&MVoS*DSwIkcH4UW{(<kHN^ky@Etnb&Y+osRszkJh2Bv=~pFO@5{Q?3Wgwv<T6@@2ABQYD@AGasagyIe^@Qnwi{#T$cJ?0SkRb79sd2uPyXC^%;3Qbt&~3c`5lQ^*#A0`5IMR`x?I&{13GhS%lzs)Rtrsf^*XAN6tyENbOCoNG?L1LM}pXNF7UVNG`*15aY3mT83PPWmYi+@25^7PvQ0UQ~QzklOw4i<PeT!Bt!6VY5@5-S*7+MtK<#Tvg8fq=~OX()A_yN{<`!r7A!(=W$G`or>29o=u4eJ?o0NkZX)}Ww^O6Z+sU`7cgVNNY19{F(a#^1^l=ev9Xr9+@fDntnnq4zJ%V4bUh6!$!+CUvd06LFH0ND3^R~{zO`NBj*iP%bonbS#XK?P%U>{l6!eFkI@#H>KPqNVVWT6JK&<<p0EoWCP+Gue~i*PMc7=j-%1izvFMgBrfqy9zq)uNjgIj9ZDImiVVf*UggkE3=YcVk`S7=nYeI7nSc^(8MP`%t~fKIA$K!C9!jWMAed_>BU6OU*&f!Mp{F5UkK^OjgJr6lfE&(5hq+f}d*|qQyxqrcoD?g$^K3Bllwn?!^%NhZb$L=%__k>L28;WIyTv@&I1Lk0CgWdXg;k3OS7Yfcl*LoNal)?*)IR29rey9!W2aoW?mbk|DS+HJlvIdD)jCcrtYlc`|v97K60tsKs3B9P(W97U~}I7V=4k;CSjOvd|Rr-&$PJ;tn;Qe21LC5PX4}LcTzLN_|LvN`6m$L$<E5_YA=wwYVYXjuy8Wf?rcVl0UNiYlh%k)HL!f@_cGAIhb>GKD7zC3Fr2F>Nv8{Ao6_j30?YHJ;4whLET1<AjfJEM-8KHBOlP>j21hoXURLs8>wOBF#hgFhTt94gJhu#$venPsXpYTWH)LZvd}DKH*!H;`rc8H-wXbx#cM6Hi*cq3?<qs@L+TsyL-J$lTe48GzdWXXp#OpE@G<oY`3l$YV}{^M)DZF|@)1S+$+4oG)?zF52ze`cF*Ss|nCwfPMxMrf%9kN{5VaS15P66e%e0uF#XyGO-qfMwp)A{*+Kb$a`&w^mM{;j+4~F1Q)HdW!<W|&n<W}Tn48g4#g1b}OkcD<7cPF2v`jLf(k%c}W3;j$!OMXced*VxKU$W52WD$aE(wjpT+L2t7T$DP9T$Efvi|W)~)IsE4<Z0Bo<Z0wk>K1Y+IhuNsEHs`h^a?qe{D}HD`4QPdy-OB)gDmtm`6Bf)^)^}PYqHQ=WTErPLQjw{lh08j$U<Yu=g5h=^gSz)Avl>DMizROEc6UHnY@X5fV_#kmLYg5L-2Bj;C0lU<aOlr)Qx1JJIF$plGl^P+0U6;f+4sWbtze>8(C;Uax-!Xs@Tg)P_xs|&TEvQ*0Q;l;3~TGvL&fi$W>UTBtvjHsx!G9*`Au6EL7~j_SElW5xH5`ne0j}M0O>+Xi=A1j9Q3XjQmA`<|gOnHNNnA;<{fLf}c=dlb?|9QJ<29J|y2Gr&1r2g<c{HJwg_GntYymn0lHlG>R;A2YCng<--iYLDYfdAaZ|dZ*p($x&5h~$o<KksjbMJ$!)34$Zg5)S~R6Lr#2%u<G$RSA-Eg0JGnde)@}^J;nbJpaPobI;ICA%hkm6NB@3-U{+nfgP=)`4-wXbwr0=tWh4vzg5L}rdxIcB8F8$eA@N{aZF8x_s@CIr$S?D9OP>U}8nO(5;xnA&bUHTq+oO+oo^qemJ{ea*|Y9d)^vM&AIg5dqsO}g~=5`wMoGz8D4t|iYVkEc#0_o4QrP9^swccm^TcP0NpT}KwWo-DKtS*R=7m23MChKo&|F1)67FR<oNmpS$!x1ts!w<4Ee2o~=Wgo?f3BSUZ+^$Gb2*L)g7@NH@;*}ArGQx7ZY?>z)t-;D_Nrv{OOxF-Fnot5-=EQ0$|+bZerWCVLs-N~Nh_6)%Wn{{iTHYXd%9@K7R4{}R};GWcQa!>MVhTwD5`{Z-vN7S!m>sl4OQtSUewU|e}M4m@BF$8bcVixt77KgQ1tVOC8`>4C956HX7M;U^jXmOwViXr$b^#S=S`5i;>V`?fnl{q|S2!2LAPd?9lpD_gAqi!bOBfq6yB41*^yk!XfK)ps5`jY&C{GIxl{F&|iPW?*$%C>!H2>wQWOn%I~zftdz?=h!u)DPq-+PHdaVPXjO(P9+Ui|S3@E#`q1d#EeOLJyGlkmDGF<F$yP?x!9g@1t(hVx1QA734LAJdq)I0d+ZfIe%{fL+~2ve)4`^YYjv2D(VXID)J=iO0v+YWT9iolgPuU!^y+hPs133M^e4X-fY`Q>O}HL@+|5C@&e{Pi@J)uih0bU4kM4GitoR3oW*$O)1t5z*%*Qy8G`j%cu)=0!sNpIeFH;qeTHCnEh=fzT8rXTcd|Rn6lVy|!w{T_nvI-^oRuNif$B(hAUC2mB{w2>raF=x*`Cfe?d(i#OYTheVhA=;J;+A#0IGpJfIN^|pFEH}nCecB(PDuXBdBZ0YxwgKRClsF`*Z}g5_tr<1+_T2IQv&{d1@|d9&#?Sj+%*_iT$o)2+qq8T$<`YE=}%EZA5OwJ{3HiI*i(x+?jnnj3Ia?bpqK;ok5*Ip1^W5s7A7p<1vFFIFKQD1$7{KAp3d+bq)C@^*VJ8c@4+xIyHv;j~1V_I8A*)e!-ugrpAzCIDV%Yg10jSPhtq}L~TK~j%z1|;Mxqq`Kh_c`N?)v9a+b56`Z8)7ss_Yp~WfcPKMyk)Z^sM<P8kLq0~sSnR<*GNj^qSWC%{79w(=eFH)1p7s-Dy1mDo&0#&6Zk&~FWYST8AA$TKoCwV8^CU`n^E<^A*hTuTzX7XnCMIb})Y-%WZHhGRsAI)J14yNuR2b0$`1V>QKWHb9Tf|^Jc8cU8KCsPy2$>gil6!KN_P3lGRMfUqmhTyvl!4~QbvW0xhW}I#@1Yc$dPN1q}mHnH*5PXm!crQcnBAYQ2JdYZ{5ImY8cm#DiS?FA{&~aoVbrf|RS!f_x=xp+Aj^!wZ;IRzBGpWJkV2<ld>Jsu~>RRd&@)DL?%MiSU8bLlpJwuHk3r!{`bBxb01pi6BNxsQ(6+BAYBid=<Pi;^3Cr_k$l7)65PbB*>1dpK(C66I@U<j^9?LzLtdh0O+SEIHkS0g)7+mW5fHMD3>9YSqK7CMSNgglxdcr`=tR)*jsRDbdj@^0!x@^128svp^p?cYmXM!rftL|sN+#&U-kf)|NBoEpUtJd+{VdY=_MoFTY7bqsk7$Dlj49=SWYG_{&8{R|*DFV#txer6DCN3B7&Ba8czXFFXc`^^8Z|5b7Nmw2{RGW?H=fB(&le{N{|n-jFU{{7=a&vseG-^VGLwEx5+-YuSxmHz<<>)&G'

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
