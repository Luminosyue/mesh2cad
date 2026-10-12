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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_008.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_008.stl', 'source_sha256': 'b1d73d499e9e9af4acb01ad23f63c06607bf886bb8dea471b0b5ad01a1120cc6', 'input_faces': 936, 'input_vertices': 566, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37463781237602234, -0.3643064498901367, -0.49999988079071045], [0.37463781237602234, 0.2799679636955261, 0.2492757886648178]]}
GEOMETRY_BASE85 = 'c$}r33Al~b+y9?^q$G1@VP{rU#;CCQHONpBN>bZQ$xMlAOJ*_^&M~xcWJ+bqkerPWjww<yw38GKhWr|&ywAPXXKiaQ=YL)Q>wR^t>-*W?v-W!K=U(es&$RYci>BGGE9mKew|YZo{LpMtEzgsZ%PZ&&>e6pOk4|0s-_fhj;DDD;`SQ=`)JIx3Z_zg34f2Lm?A)b)r+yXh30AzXYn_T!f)%^=?l+)chhES2?$^1C_z!mI*}seL_wU}JPZ$4lrCPOXR|(drTqXEQ@PGL)ryoK*-=!}ze2wgCp)@`#S1iN!2lYNE>dn@Eu;lVXqM<RRlKjvs6_g*N9q;|>`)xmD{CqD=X<+$L)4p5Z_<42x@UfX+DF5RJ52!fUZZz8;s$PV6Lc3P&vwhFR87nzLZTGVix?an@`|WnTjNeteVcL(CZMx6)gZN&Z`Msr`=&7dabA)z67qjW@;s^0PFTH{C`(E5<=O+}t^p)+K{DiMRwyA+#pFFtrgZM#HzuQgw>^wx;<k$7_O&)?5a>k^7eDTCRs-D^3EzNcR<9qm#)EhpL`mwHKcB}SG-sbJp{f+OLJly>Ede#1`Z8s}FlYZ}6<#>kev%k@j4KwZfantW^ef%)>y>;z3sqLG7zi|0zhV74Le{VanL-qTWr<5PMcgSY>9NGK+_6*C9;Kz@DxKe$8ZFc1c@nad+sr?LIye_GoP`~!OvhpLRKiZ+<d2Xy8rzX$KE+4V|_<HTfqu*|q?*$)d60^4(sW4OZN2qwQm>p*<N8#nlFZ^eQYM1;+zIg12?VElHo*TDK<?Zgg8&&<YX)9IxqyEm!u>8n5eDYxY_`j8Qsr~&%`=PTBe4^T^)J*k9c*Cg8wjaljml?ELwY&9;4XXdvY*p>V@~+-&`%&W$DY04~uS=949FeBl2^Ffk+4e*DUf<h4QlFPC)c)|;PUTmqrTQy8{BG^{dT*6#hkP2}YY^RO=Q$Gi?qjvxv}3A%gghtwC8JdR;EmdkKR!$O(WM<!Jkd>8Hraj*KUj36j&osQU7vpR(trOz)hoPZor>q;kA2nl)}&`9`Kx~#r|K6dx5xH_xhpMK+dWk76Wb5Z+PYe8cUyinZo;Md=yrk!)bS8u+(s^5S*!j&zQ2yA<t;mHKQ^<K?#B=R)$>_+k@DliQdK*#4*S({6hGNO*B>`Tw}0gWHU2{fH?Gln&Q$YG=$$RQY(F-q#HXtMbpt=M{m>)JbiX|D`RBGDIsNx;wcUlcsd(Zy57d77o@>-NoUij~{7~nRj>qJA#Rk<6k!khQ)!%od?oRS6H=d&M(KjW@_ZELQN#$qXvAs!tk2!BEzfQ~jN&bN$@2k8OFSp9}qp3YVRPnT1zRvbTZ{EF5`9-^DB(?M8wv8%p-RtV(vr9nNcg|nN59YpE^+(v8AG<Zt$KRP!3zR-Ncu$g_)@Z)k&aln9ZQn~jGEwbU<JA30e&2Ves(6mp)7#(CO6_0R%>QK@eQNtA&d420*Vw*^Gvd_u@Vz^A{qU=gX+L&*hT87Ge`VT!yv}1=Ro)iV-){Tivx8K>d!t@BkmNV6zE>SDUr$u$#rPZbbo+O9->2GVp1H<np7Gl4*7M)*<&+=ecsG6+Kg97K%#7;#?I$Wf!aV8v!LrPgr>Cw^{ok^`Zr{w4j_(cC^JH|+DCK+gYN&n;)!(rv$!~GuQT6@0)3zu1XRC}>+il%<zwHOlZd|0cyWj(LoW@^#O3!~|8ZT2?vP`D!$2QHFsg66&BgXf(YCptzBvHT6q4_HQJb6A(s()d?0u|4en#*lJbTVCC--KsQjoE&@*(RM&&PTDF<33dNpX;Xc&-@>Gy@~R@Bd^ZYKJz?&?AfL|&-lSj4Rrk`Q`G)?jf(G1@^i0Ss<+cA)AnQSUWlsp4>bNf$)EAyJQZiRU-WVCL^0h?yrS|$=KO*mX;53o&-o=-_F*+|McX!3^FU<z^Sf<7^z&vl{=*kCw<Y=aWmn@r8h-bH?MMEeug1R@ctVf=&q{n?AHT7^pKrH)bNt4?81rG0Z;sP_$@R_g8$P7#$0pZ&U-_laEmGerd}Mc$zwG>I^*R5dZApHIY17qs=<(xz+mGzm^J--GY?c4$=&<gm+%?pGCC+PkUw%*Ng}r;kk8_@i^lqkncb+tU^!XuMZ9iD<it6w1xir;I)STC56jHvoA=^@wPtH5W4~?#+w`<NjXUi?Iw;R74+id$LZ;_$P*4w^`$NML_egxmtkJtWL&F}6!X?%B{G`>4eCVXd}jQp{DL6-T+Q%|2)`tDHY!Qhe0NxnBg`(DlK)p<4aRE~7Jok*F|n{7X_U)9d5>!f(QlyrN%MF!;BYWpT{@$rQ}vi%tCM4kGkeQ$!U@4eAV&zsX`>Un=mSjWG)^E{o;#toD9%lP>oR(_<0-mipz->?N))eqLweuO;4zdAM7-frlfD!PA*9FE$@qt~eRPTM!fW9Y<)g-Jen2s!oRx$wWE{*uX2yT3xyCvLL+M1Q??_$3v`w=3q@`Sk8NvBmZi{gv{(zAh|WR{8Grp7Gu5J>$FAd&YOK_q;ZTXDcQCNR3PSeA;@&EagAFbAZY}`<3v!YTxXa@uN3aop0yC`0;|;_onIkq23*5C2jYn&g!})Jh=3%ERTz~7tU0l>0j@G6)JC`>SNN>e)XZ9`|GOy3I35S&2A^QyVItu{K(hc)OCLF_d}_w-RN^elJbBb&e>L-U!wT2=z!F$`ZrcY`|kL6{m9Qd_4WPRrF8qw{etn``-RZ6(`TsdmTUH^oj2o04_{X2<tTn|M09#mJfDu$*H<(Co~Gl^KFrRW@#EfzxwaqAY&R{dJjYMnq}!<;eBI82@goCu{cyV;>OR=`(QXar+T$Vk*P^%W<1SL{?QOQ7xQ_i#_La78jw82zVqT(t_}o3ZojEz)RLXpk@Kd#K=AVQ=vhgxCo}K!^QQG%vF%Nh8cB(zDyqu#q+kPURj-}N+9A4Q$`QG8`BkX({KeBLe)b^tnis<^kj#l-f<kR@Ud%8vKJjXV+o?;&_K@(5-=p_5N3r%mX=k@Ywlk9wkF6K`1P5iM5H|zVlcc$oehOQc-+UIyr`2Do+P0{^p{NS(mE!Nvjt{*<DeKQ`y4a-cj$8C_j1@~Wk)84OWjx~DTDE`F+wY`*w`sjYt$Eoq-_4h8ck6*7vEnUCNdt>c97(ceO_8i*}x9vP$|9x^-)xMdp@I(FYTxcJ6(HX_ZXEpw#4JVIP?NsXexca{7U;OaI4)5Ci9yv5&teuB&mreS9b?l%qs-0k&yX-t0Kf3nxf~0&NY^SaZy-vd>*yG3ep@NyS>^MV5JB?KJ?`z(vffc9mgJUPB+i?c>=hpSR&+KBiZ~Rb3?{vF;FWYM)?BgZ+bTc)d8$WTpd@@bl*M};8`G(!^@s8D0{YaDJ5mm3wlA(5g89!L0+PoycN}q_GPj7jqe!jEjwxR0t+&hLR<p)2${!;Ssb!O&cc0A$!1@!UZ_+IN5^m!_C{_%~n{qI-3rF`ZS<9pv}-^@P=zy5}i_VJbQ>uNvI@5XObDPoWRgnwed%l5cU_!sl`x5r_^&)4LIEZdKN-YCoZv0K$RG<i$-PtNae=Re`E{pQsMS=FC<gF26x``?70s(o|+oAA@dOjf>mu50qVH<x;@5;V_s@q<0j%uO2S_@Un(o1ayj!M9_|kI&<N#I(OoA75@e;l=rrj^9K(h2|`@kH>`nbfraE)sJ5)xY(Xgj34W@Z?Qd(CF1WjaH)<zd7MOgYu}rZyxn;BeCoMb$Qg%`9@<Zw*G&CN+4OUg1<85veyykP_sxBriRWZHUBBc0r2UG#{<eP3z<s6hqrIB!SN@I3{S}$pQTZ{af4#=T_v?Pw&m|K1`S*-&hvyjK=db)xU+VMTBy{D<H%Y#EPj~;1>i#U@zo_4jMBMtkH;Fp+&3lvBO>2(Z^%L(++PB%ARNuV+%A9*FsXp&7qQ`FEl~mu{zpVN3s9ittoN!XEUACWiPPn*Ay6wjw(|&m6x*c}=iR&)69sKBDrM4&K!Ca3GKfgSweeRDUOOm&1t}9|rI|;wtOIvL}aowIdaZ6Udxi2t&;=bu<-gQ~|!HoK=v-F8y=4~~en73n@t=47fPt2*GJHJs-&1<nseRt{OtK~4;_nQ2u{K&F@Q*A$(`iy@6a>EjR|KFvAI&Zn>9pk&_opAL&5v9&~F#gjC<-6xW<GbfUuV_Ja-5)+zQ;kb6Puh#NADOmC`H=@cct_=}V^I5#mr>7Qy!nmw^Ma~hzG3IboKNG~U(?sA&iUQ=*PP!gT|ZK_>s&t=-@Sea*LYgjcdk#2?_Qt82Zq)2S@-(K`0n*j{6w!Ys=jl5WqkMgDmG(`x{h?O>x}PS*M$#H7;E>VxsHw8TY9{z=iWD6>aKkE`qTLC^=J5eUA3R?^{w&U>)X&Lhjo4D`q}vI^>gsx#W(GKH`k@{Mr9`1`(^Gs;^*Gd?|Yp4g@o_iFBspwUogIVzYwjIru=K}U+~@g7jOA-y<O)%C=_cw#ojM--w`iWP+d>B_g}_$@4w>5+w1zy{hjgM`@2}@Z>QSFi@AR^zI*=|YgkV|cW~}!6TWjloA90cS>wC+v%$-YbY9&1ar|rU$MLVZAIEp^$0G%DOjGSR&kc<4j(_93&kZ6apV9T5=Mv%5|LFFe=Nra%pKnA*MyK2T9{;(RdM*?hH+6<;$9djjeD`@vXjAc26}R&|$N28^oN#8JR2`@D9I5z#RQotG&%2DDh_hoa^?oz@&|%$<^Zd&A?(-|}QnoaEyqV`?u5X@?dBex0WtHdPjD<7pc+7LH_{*hd+3lF~bv&c<Ec>`i%wr2yY2SI?nDCwFjmCGMHyYo4-WXYUWOmYa&GUgqrPVy>K3_Gy`+U{-?(<dSyU$m{Cs)j|kBh|fUVQg?Z}i5G-%<59jMeKdxUL8un4;$k=Q*?SuX)Z~^st_foaf%gcb|JFeCN5h@!jX%p-UP1_*v0huN%pwuOGr+pPFlrhuGbR^!$0IiyD9K^Z$hJJpWJl&hvlcyU+i_BU;VR^0;_9CEeaH^S;CQ?)whoyYD-Uf6e=jb~)0Mju+m)7~g&W5~*E(f!&X0zl`s`-|_xhz96gPDAw$ZuJ62`GQRtM%J}a4sf6#mp9-HVw?xI~yk9fE`+m*%?)x?4yYJUxvBLVk)Op`$eD{4{w3+vwiqm;-==E*(o*k#jkMZ5Sh04FAeD^(OaLzOO{O7#)jIOVx-jBNPTNA$XzBS=H?^})UzHbfhEb)PToSOH=#&_QrCw%99vGLva#lgA{DgT=H-T2qM?>4^sz8l|t-yQj>n0{X1zJJGe-@kjUL%P1R9w6a6>j8}Kt_Mi?&U%30gokxI&iVx7yXzC;bH?fCAkI1mFIPLY4$NJrVSIO;hVk8X8j1SOI*mkqXPt)e-E|tqch_lz7mr+_+HuyaBz$MRO2T*6s~F#1uM#QHQmxx_=NaR>^NjJ`c_!gI^Gs|<t5x>+H|w2@@2+<;zPsMZ`0jeA*xyamx;=NjR>F7IYZ>2Nua)qf^;)5>fsgDs&H6FpyYo`~!B3R$u9r*r&U!iHyX)l=zO!B~;XCW)jPI_OGrqfCF42y&UM{$3pjsE`t`9W6yFM_|Jwy5K^_B76>nr2C*H^}OudjlGLu=J%XPu;Xagp-fb(PW4p4w0M`rP=}T%T9&t^8}&dEUBN`_B5(gzu~`HNLyP)cEfD(%_0hAFF!Ky4Fyx6Uukj(<XdpJ#FaC+8b0po%OoLch~EN8ZOfHopryVU3t|waMw8--(BZye0QC*SL9DMkGSirjqk3n4tFl5#?3YBv?n%EzPqkF{M=aOyX(V^@2(FI)z7}kZpW-kH@>?r-Sy47^zg&&l6}_08{b_IA70m9`R;oAgzv1k_g-tO$APo{KjAy;|Bdgi|4-C+*8c~)jZw#y`+EfAyT3;WEt#mUpWNR&7~lQ9L%iEf`n=`*p2GO<?<rz^FY5EO^ZO3tyT9*9)OUX0VSM-Z9r06552$#Y-<ufU{k=&j<9Fq|zh^PN`+Jt~XD1G-IGyuCEZZLk?L3&@*BIaZeNE)p%r8_s&hK<0uT(f>=g0is$N28=gN*O~J}6P&`F&8R<Z|shze|$eF{$>l_<fV|?cX=GNcuI`ingcLhO79g@ym@~L9c5E>!(~|%0Hu7|CFmo&Ht~Ta@DQzfBq@gf`FeQzr2BtgJXVdYyGkf{TSW`A3?u>kHCMSf53mip5NvRehK@fDSAKL6t07Mu&8{u4)urg_o%1iTYzqZ7r^V#Bk(%-B>ES8625}U_O9?*_z7aTAHJU$gunCuw8<}*(O==qaJ_)m`T@;Sgqxtx!cE}r=vcTr{0bU{UxD917Z~=pHJyA+r_W-<wv3oWkHf#h5{u})#3kikViD~MKMRjVr^936D7qAm!VA#%VaeMe;yOf3!ePe8aC92{24nISbhMR+(d0?AmzB3(<W<_2?fr>fhW~``322qRxrZX$3~d58q0MH*Ap0_k7$w#v=qPv;b%fW_9~;<LiD@Rf0p36z;o-FV1lk3D0+z8Udbc%Jg-@c#tg(HJu`g}Q_(($+z-jP%=sI{E-xZb^7P0L`#Izb+0<VTYM&E}&hCf1=!XLql(dqDFco5nZ9t7Wq-V5Ic?_>PRINnDQeg|C!zXMM}XTnq9ap-h-96T9KgD1mt(D&du@Lu#7yce!b|42X8rU(y2yTB&b1JQS3(f;s2xHekDYExLYDZ1N=VK*^~&az^j#XgBnwDxf#IS?Id<zy^56P;w`a1uEdoo(fOHhm(x$Lb?t=|j<)R-e|S&qW7VV_*Pd<X!Tz5?u|igx8}V!|UNy=tuA>cp<tNUd*-@lFRDkQFIacld_1MiM|fcf+wO+!4u)J=;QEMcoNzUo&?WEhr_esJ?LV14=gzotwsK%)M9@`=fDHth3HmzA-oFx-pbYY<gz+>nT_^`XTzVO@4}zLC()JgN%$vpJ-nW6{lvEJB=4f{l5Z*Rl4H>b{5t#;`Xu}m{5aYYejILxwuRfl!_i^zaCkBCNPIKV+3-wwGx{mK89srYgipX{(4XKl@OS9<@OSVQbSu0Co`ueVXTf)&wcxwpg^U;3r-kg>F!&7HtCXUPa4B>PEJZjsIt!K}Tn+CoxEfs9(<<AkOc5@M4ugxrdC<0S9yll363z+dMxTUp!$r^tTm-I!z6)1^?_k_Xf8Rk7&XuBdCM-p`B)S=vB3uzY0ZS3S9X$h|A>YD9{F2Wvx1y!tTj45bWw;7l1HA*T0arzDgR8=2&>&m}E{f)di^8`Dv{nshmLgor(^}rsEJavukIMO_q+bf5H^YVCo6sEaP4Eq93VZ{c3%wD}1s6sO!Uc(;Fr~aT-h`_WZ&ho2R%HxVWk1b$&d+$yPhQOU4|042$)h=5ZlfP>Bk#9U?x6qgpr6cmsLXh&Ouw4(Q=0KrnsH#po3I&^!d1{BuoU6jWK0FLmf*AaB`Ct>(Ocp2a5c0FTn(;;)_`ll)zPYOb+`gr2Ce|#f)<5ufhz~J%Gjz*5x&LKDr4&wif{q6AY1^x9=#F19uA->Z~)GZ=76)q`O%x<{BQ}hBwPZnM9zh8L(9QZgsaeZqLuhu&YFM9F+Y{#I5G28A?C9}94BUe6V8d=;9Z>$h4Y}fysPu4a8a}{T$p2{DEm+$p!Z3%n6;0^$bo2HD<^r$nP@gEhuO%nsAuKeqfg}Dbygo;M<0sjv-&h2eJ)zu8Uw;IMno%GV@6oUlxT5lj1@QIkbWwbqE(KEVie)BXnD9Sd?#8Bz7wvA)`DxoccIncyWnzY1-JsS3Clfa-N4oRQ(<!tD=hbshhVvn+yKjc=UP~v(|ioevzaeodA9NgT!$iTp2-NmKoK5A5gtbo9!(MMg*JnS`t85!m#OI6@KpGH^h5Z4cr*3o`_G_H!_UAEqW8lO!VS?7+z@^UeE@z4eim&HKMTKxz5>4nPeb2=r@_n758&nS7IZVbnSB)A=I7`GzkEg!UXD(Im&0#SCmzt>+Xf#;|AddjzoY-azr&Z&zu?R8ALzI6AMiKm4)_~*JGuhi4u6Qg4SxtvMTfyt;RyN`{1*Ew{HUL!7JjLR)`#!&%e{QQ7f<+#Oep?w6G+jT0{`OszXtT*f2EFaGasAMUQ^l<J|EEEG2guc%XcsEebE%QBe69jhGw);pEe(*-A9R2SiXCn@1Lh_;j=#f#x^d%=h1WUdH5IfXZRQRSM)4=mbQeO_}hMjSRRF2ppU^V;AUuZxEb6OZ2~u;E#X0adBZQ60j(PYnos%VYrp)69)<V#CFYlxJgp-=&29YhoL^d@-C=2KBkgUZty8phl=hC&<{sJ|NqZw{s|{^+C*JPFESy2RBZysm;Zb~l6ERBr!bgZ91KkKe&$dRPBjIDjcLe<!?m-;SqtC&c*q3AIQFsI~_dvVDvTsk2L(##o<md<bLUcF$5_Ke3qI=0(CUqnyqA!vkDKC;g(blkhXD|IAdKzv;oi^wb@Q>6vh5it@8spDwTl4_jnsN37+8jR3`2GR?8J5_3vdx}+$85hj`z+cU9t=zDqKDXz-NYd6iS}f_<!^_G{Seze&GGmpaeT>lg}>q$K7^iy<@oALEPaW=99um(E=BvmhluYhv@hI~`1+t<!d?Axr(ZgwRpDxW3G+FOR~28hI(i2zbvjT_v<qCFIvvn1a2>yNq`i)OU$~QB>QbjJ-|s-3PSop!Cw!M*y3uww+Be*l&s~Y73;TE%vEN1As%)zc+p9w?!VUa9J>-`e=sR#jzdY=h5ZV|H!41%d;6nb~UC=Lo2ee)aXqF<p0bK`gfP-jhI0%pNV=L{KMt&(v5&jQFcsx1=R^JI|&g*M#zYOrSzTjz=B3u)_4Xz1SKyQUBz_rjCa4mQs+8-VWmu34B$3b)-d=S1dMeFq`nxzOAK=Z-{;2h`;a1QwMfY$v1%~FKRp=DuFiA^|<U-J2-m#6h*PqP%^+tJ$a?QjsS2nXRR=-qG?xF0$M?gy7=`x3`a^b2?=d|isxoGF^62<Jfy!+GHB=uL2TcvnE{;eci-!e!9%u&Bf)e6wHwU&eAlSjMmDC-5a$#&221Wf_Wa19Uvx03MCXSRKu0;aeH|>)>^?e=E6?yxdF?UV}<r*6>;QBAN%5BAg8`JDd&vZ$PW$<-Zi+wP+c5EnJEiCNOsL!7^S%8^bTdwb6Uv+HghmVYniEH~J=gH#`I_ML(4y9^sqhc#=NxwEpI4mLmKE`X&4Wd=%XQABBHJzk+{+|3)vuf5QdXzQpk;`T+bW{5;wYeja`q?FPRL_e7tDd%`Wy2jLcQA+!K2DzOO{^vmx)=MU&2{I93=YxrOI0=f&n0RMy@hJS+3qyL4^!~dW;1DgMVa|N_EhjYP=&>nCj_%ZY)_%ZlN^f~xRxFz}s+!Fo|S`aQsF8)J25^IitF2ZMt|1f+O-ihvlcfuLy*Kh`$iT(~}!sk$l;~bxb3lqcR#FZ0nj=l&thkKx}!#&`a(82Ia@N;M@_&N9yv@l$l96drjvj5iwbP<k|lbvuJUWI1BtKg+*CcG5>2t5aX1fM`9juU(qE<tRq;1Y0WbTHf*o`k**PlD6X7vVJcP4=;4;OcnjNbWoG_s7u};S|6030%!jAL@$EgFC`+qRZen;WRYeiYJ|TMf+Lt_hbJ=OIrI|l6;6B^seUTAo&wb_patMoqUU?TKP|<e?;e5{WXvN6#d-l-_PlPQOQLdy$%ley5HAq0bPW@@wCo`zkyexGvJl*5_CSi1YV6EfLFucqPGMze+w56XzdFZhdZJ3;ZE>GV(t*o`w@V9qZ8oX@LV(%o(sQ+PJ}1YzVP>cY@hh$G)4GRbOrn=yawF}uYtFsr{Jyd8MIhH^BK6PU!FprL5sl?(N1VFD<{RsnW(gDa(IdypCS&E^NsY$M&dSow1Pfd!G4-P{e(Uj{oWb_-!n#}FGRDW-^1C-<MrriSc>os0bPWD=I@`vKf~M6HSl(LJ-QWM4}XT9fj@(PK_#cZ@L9NsmG>eP;WmD0@0YfIdDSmt&>?7BcnI8@eQC}9wZ=F5+m?K^rCpPs_JOO%V0&x)ijF|r!|mDj2#WA{E57mQP<TB28rlYK!#=)75gv&?1Di275>16i!jsVn@C0I-jE;xLvkhUn9(y!!wcj5lPomGmt>Gcmk#TS%-xdCiv9TTg4gL~c4}S^oKtF?bz+a)iz+b@^Q5gpp`7B(BvC#%D1h+tk2CiQF3HL<D1g>5y3crjFfrqfa!ZMG^oRvZm?t{*S`@r+i_uzT(GITz?3{FS;!s&27^cJ`uToRS}x+I^44>E_(hY!N(=nOa=PDSU!Et&>W3TFF%{jVmj{*!0zUef<~!u@9QvS$06d;GQ%i=10D&92_%rTG8J!>JzfWXJm-A~?_f'

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
