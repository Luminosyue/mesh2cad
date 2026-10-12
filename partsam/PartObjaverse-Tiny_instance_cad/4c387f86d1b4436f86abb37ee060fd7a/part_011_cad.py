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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4c387f86d1b4436f86abb37ee060fd7a/part_011.stl', 'relative_path': '4c387f86d1b4436f86abb37ee060fd7a/part_011.stl', 'source_sha256': 'a75ce0ce205139c24fc66362142bec714e382101ed289fc6e811219bc26ab85f', 'input_faces': 748, 'input_vertices': 487, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3434407711029053, 0.026742517948150635, -0.0563606396317482], [0.34344086050987244, 0.19875264167785645, 0.019706733524799347]]}
GEOMETRY_BASE85 = 'c$}@A33v`y|NbYuDJ@!C(bx7^YO7rkqB6BBA!=94W2d%|h%I3vK|^YZ1c`0Ll1K;<L@MR6*RGaQiie_<(rQsu{pNeV_dMoI^S`eD^}BxF>%Q*KbH68N&YU?jb7tmT4eXHjKgAXPS3xN}rGM9IwH1X_P${m24xJD(a`4dL+GB&JcqxTNPXA0_+^Ks&U~exaRGC(F$k5=y6RI|KRBblQw`xsC)nVf%giIJXcEGp^Lxxh`X5i@Hp++7&Vqnlv<99V5-^Mi^4XW34gggG1|K6cCJbH0qFM0kVyZjAvhM!$6exLh`^R@S~C|9GW>Ga!`_$TL&Qbewl4qijQ-OnDL7kSC@q8^w3pR1*OUN^44eEn5Y9uO*WrC{Zi^xNs4&H3zxTSYzjrzhl=YvJx?Qr^Rt^D9~+{dV+?<h*J73{n5jhlcoD^Alq@@8<eK%3m+#e0=lqBLA&Pj>!MGa6r_byl0`<?u>dO*Vf$=xw`fGm$~Jx71uTKyUYBqMLiE+a(QQOQIG5NB+eVZdysN{#dmW=|I8oF`RRfpS4y0jA<B;q<a}yy79X#Ni*n0dk#{ELmMhCwjrF(YV`91dhZAQ>dGmOYJEqoLA=MM|fX73{rZH0a+kc8&%QsY)%1;mG<2!iI0;&9fD3Pm|hp&;!2ei)?^$gt-E0urUSLAAm2T9_0&DNavi{kdbytpXW9Q|O=l`j{L@weuIYdJ4pdX|)z-@x^RzFscX)BP3a2}kEi<>T}7{?6{COXc+ioZm=ZAeE2M`Fv?IXpL09e^1`u3X@``@`Xo<+|~7%=m*Eef3o@fir6X2O^RETTdsxHpOkBPj0Z<{GtT!7$Q0YHenE^+d+utV6Ovo5OdQ4MOa30aM1FWcy4Y^!KMVHelB*>jjL$7sl5PZxziYNROPn{CRX#7)mKF7A$JdEm+2p-JjQ?_%=jWCyms*d@E!U2|nked<GA~PN&%WDV34c41w;LHCwyTD{H(Q+7KM#{~?QFR)(f(Km*E3|$a?0H$wfVW_+M&i{bIrfc2o=8h=1!^o=l_^5+F5+aPO1Fm05N{_*E2Ik{`Mm7pMzav#d#DyTI5=nwcO5e0WsotYBSFJq>9|xIU!P%Z<J5UT_N6lzN~n#MdTG8f6LpgHjjR*O%91%x%VsQb?S)mrWXt2^1YvmTrc-jT=(1$>vO)X>>*Kq^VDeZ_a{qmJ<)%N^3I^lIMF{b1-N|CQlh-Gd?&u%wmp|F%9k!La-~{$gf%y}t3($XCHAZ0TrPjP7;pD|b+M?wpPy8ZtNM!xV!x)<;C$aRuIF(JaevWwT-hw@pHNhkcg%ShFUkeZ;k>1vDDSHGR9yen<1MA!QU5NF+x!*fywnQOKYANQ<Vua_B3GZ>71tTv`^hHjcJ-`9qCJW`jq^>-xZjEv6Z@rJoxaIhzw#<FNc8{NXKCW^iZ|!u)xPi&k=K9Bc}z0*XPu*>{f?kBY1Zv3>5-y6YNzc|c~^yeV!xd8Vx`<X?pkUD*Yo@(x3fti&j(u7lFMtQ#kf@tl;AwfpWCSw68C*&W&zIq{SJ%vY~IH0T=ODT)L(YO5h+)mq)P29(?%R$XY+HZ)_NSJH;ePsnUf>ev+@96Ps(IT^*C!z6XR2xmLb*ST-!v9L;ZQ8RF9dvo{r%>`lQr;<w6&!9=+L5eBI7$D3$kIPs|+kt9zbv`R^)A?Nl#a7RT37uY9WYIJ!q36!R{1(Ff9YwL0B`MgChcX}gZ(VSIkQmsj3yg9uUHS?lpek>67Jcr~f8g2&~Rjn?|zA65|k=4!uvqqTl#lbwsKxiUNW2)DDhDDSSiY@>DjDEdymKW>PS>d~6z=lfBf&KsrU)jm2w%FXc;_=V^nbze)V9`}vA;yiNpFC(=_e?Obgm#mx=sr_?Hb3b>FPm#vep8Gs6E!>aGcWlAehtSDl{5$J(OtIGQI@nsY)0LWEs^1+tTh!w|`Yc&GPg|yles<o7Nwywe*OTg^fAqfXlcnRk{i-;B-A!w8KIj#<XWh=V;<vAoEVbwB#-e^T?&Jn*d-VGQMLmvhD~nv&(UOn*)i|+TZQrr=)^=(KYKr-fGrsD2YkSOo(1Wh66Zyjs-tNoYe0><5vCg_(wdS2wQjYQ9_&JX2y`Q*F>W8Iy#C|yv)7MJvoH0iH){8b@E46b@1u>6uR^5;!9mfG_ykFjPldRiy53VfwOaEz1lC}M+n#0dQ{(ec)`To2I*HiM)8f!b1=ch%xU9k~7uFJMYe-;w^<+^o5x3<&uP61Kg+0;*$#<N$H*dMKT4c*#K_3w#1p0X?JQafFfMR`}%tkqIK_o>YNQ=p>gZ!M|~*W()@j<<7q)JmzJyS5a$V_2CLa(^a@_N(3fmP_0H`)|>H_5Hfbt?k$Ml;h(#H#Sjf&!lWo-W_(0?*qsF;r=h0A<j>IvA)#WPNnWijQcrDq;@)=iFT@^qvEaYRQs$HxqHy7IB6W3`!(Q9oVA^9pKc;|#dnL7&eKz`Mf<f)CB%J9tFIiT+}Z95UuWBw5%U-A*S6e#?^oiu=y$#6TidDS>nYlA+-GB?b`I|%a(A0rF;aiF8zge)-kf>Tcu46ha)(d(dDeDn2g>pF;$A1s+8(E0Rnbm$!;5gKJ?T3|dDnuyVb=CILcDoged!x!ZI8ZUn#kSSwQ17vojO3|uJJXdS=-|(=__*MzWQ{JWxIODPs!HYGfzN0p4`0uM%|I?F~`rKV{&=3-+nG6#*Z=Io93TOd-RzZBDc5S9qk+DpUeJgi()yq^^Yt0MYw-1{i#0er1|I4|8C=WS=(bCFNZ5<p0z#Z@zvYbim|rG91o7uD`TwfF~^Vdp7(sIJ?3~b#;3JC=J<4{mk`gL_VMgk)-BH3PS5x^&KGMt&GSVa{3_1cPV@ZIjq_1zC(cKwasFD{X`a7IoW4}#w)0&Lzm_0=+pZ5z<9cFkr+Gcmjq8ted~yBJd-^Sx`V-eH&A7f<+i70kTw2shsh!v_<wS{9)^?iLPo+lIYN<WA-nu?0uS?s-^;z#zL*(}Bx$ftuOXC68e|M|>y0x9={X$tBu}0*!`-^VekF4!C??(>3VUo3-=KafU-0!4z;(q5c?vK`XdhU;N^dxIL&HJg_xc|!i$@gD%c{=B|`?cdi;yS6H&HMYwv~||)n)3n2*o<{jKb!LhW4<AcL(Dg{B~{m3+iA{ETon$jm)eQ>j9RVy2C1Fq{KuFtS+{G>m(*o1xV&wCr8KLREOOg?%-yejvb8<t{7t(VlPvWE=6gzw$H~@qn)5>?Eq{u1o?<?!*X@`hwFmQ0tw=vEZ=0{GI~Jr!#}V^e$F3ZyesezTy6U~rnrr*3IK_4cl-X$At~sxE?r$lT_sqldcHU^+FLOTc$!+s_$6I0YcFpI4wsSZ)pYK{6?JN4H+A_JG2JcI`{kg+!Jf}$ei{}?Jw?DtQ3VtuuZ$1a<wI6dm_U9(!Im_Bk&vVxA#Zsm5faf(c|JU=H@qA|;C+2gXvwrzhYk!*0iK_8jDfK^|H$A!id9z_hsXgX%tMb<vsUFXB?y_KMyUGDqchNsD5~cb*&(UESQhD>a+mqX$yT8ei>hV0kuR1A}_dM@=J(247ydOYrf1jX67D$uEiJ4a_!ny5zg`;(?G;96l`wdt0P|oj!@OwpbzMU44W*u+ldlEe+R;~x{Rh*r-OS$<TMm=*Z&3fF;_co3OkEQaS_dI59doScT|BUOw`z58!nYN-ouTI}2a@+eQRo$@3THbsg<sSNIleInO`z!Z`7b5@H`>wYuZnoBMz8}+$x0G|dPgA!>NV)m`&FynY<evA0KUC`}`hVw@&DQpq@9~^rHTb==?Y*Dc&oA9tkNKX^;poTjween5*?OyiIBzP><?^=ojr#EYT;8|OQEPcU<)l=<`94!`caF>3-e+pnZ*lprgG4=A=<AW9oiPQrh~KvNrE0ArTlnwg_p9p35?id}&=sC2u5XUcwYVPJds<gW=oV{xJmawGA+E>v9#~!ZV2ibX%=gB6*%RXXoYFazw~OzC&iD3YNO@$YxE|^^f8{)|Cx4F!xU$KbYo8t!-_ewJeR-btAY_~P?HAAAHAWv3<z0`~aQ>mf-yeU;l=IUuBG>1{$oZ)O;ya7`r{0|JUB~&hmb*pyUO8z}j`o}PDVMU9^9Sl)QNDRMe$E=di}T3jeIj>f^1SYo-JDmyykGcrH@|;rbywut;}m|MpC@gw80U@hiGH!ax7SmfNxAu+Ux^9eyk|InPb^rU@4tnHWLo=Kul_)^(>Z-Km$!XKaMjVcyzRS#BV!5Y<M;A+(zpx!ex$)>&a3nh<JY}9MeMJm*Hg|5F5}~M?00@%p6A#ue&aict6o*^hmWdo{xr`nYk5!ZPTXZ}zb9WcC|laE(e*eF@)gI?{YeBLm)G4n-`#RAkCUe2Il|!{#<`;pfB(vJhM)WPP2zmWE^!=P??mzQ_1Rh5t;f+dB8{IH*6-ME?FZMy0lZ&RZgalvnCLf0NHK9fI+uIx5c!XZqJJERe&>Gk_t|0XAML>UwNifATl9lAr`Sd*4~pgQjB`~vA2(F=k7L|)e($*`fb%Zxd7K~bAaeJCNjs!|$X?3tN$xD(VeL0{Qhk2zesOAtb$``%_jrEW^fKr7Q$)Y1VcGm%CFT##7hU1;|5*^9*N^_o<0EaQaCOxMeoma}&-rB+kGDF-c)mI~kaK*8HJ_tBIli|#znCuP{v-Ii>bcka{8D_#PHR6a<L`+1zvF2L=S7<Dww8BRU(NZWzI+~ysn5?-={Gr_*JiJ^J?_HqWJ%)z^Lg#ir<{lD{N1*AEcZiv0DoUUp3UQ}axlL)Yt%K%+D>(8JMkV(X*-b1m+r{tFTOw0cTDly_8rq%Z9<l{|6SST#PL#_Xi|Ced#LN}NG?CT0Qd8XJnN;r$TA*pZ5GJ6drY=<{Od2*NbNVj=h}1gd#*kAe9s-7%I&m$FIG11;PU&sh~wq-OXu<9zRu;_l@aAV-yO8uS=QsIe7u0)t0#H!bqC*zT@~-}`^tt@c>iaf<n<nXmx|nd<Wnx+w>@9~e|^aP;M-NI$NWBS&&}`S_T2M*{Hp}cJFXSu#O+;x*8@zr$T`;Yxay_L`QsGMozvG!`IaDYT$CM4dEB<R%=^_fmB-tYB+esmb9sFCch^6{&!;}mx%|FMeEzQeiJzOQl;V14wh{fWmivI8)9*FOw$|fWZ(z$k>kVwVx!%Ct>N4jwJMOi%(_Q>3=b6v=`WY9;>x*XH&bIcCqwW=5%D1lMJmSb2DL4CPc^y74F8;&6ZR;-Vxw-D*U*)mxLYY?YYvGH#iT=^P@aFgYHCuCTTi^1p9P3-`xw*c@liSv}cyinN7Ef+l-{Q$_>svgzZGDR;x2<pS<hJ!Kp4_&+#W^OBbK80+d+zB6TW<EVC%3J4^5nMlPM+Mh-pP~O);oD}+j=KYZd>o<$!+VMJh^SXle%{#=eG4=>Vna7Uge~CPSIb7aBf>yrU!+KT+>d9^He+I=KI=>SzI3T8O^UDe^=@<pL5%~HEsVA&dvMa<Zl-HTXW2lT{9E;dt2TlDc6+R{9f41&FjPPOQO8<);4Y@=K1QAr+j_xwwufQjo|rGnHX`sb$(Pz{JrwB6YjG-FLGyoDdp;_zPaZKZ}EDwgG;2`yiVG4<!W;-@AsVdXYmfvZ_Z!Z@%7ffN{%S^`9+?e;60eOrMAfbwLZ|6YXSGfbx+aiNx8YsPzm(md{qwLug&+Fj>f!Q+j>Q}vjvww-Gu8obt1u<E0YqWes)X@=lt)TV!u517c)1<$>xjVywH2h=lXqii(IKzRg^b#Wkn9>joR@#s{*GvKb<YwuVz%|`5SU=er;~g+_(g5t~8p@&wY*Z#7pII|8<XaFO>3MPI39G^9M@xthmYLcQ%R6EjQmU*>hKqpowBUq@Cybzjtx_-)$P@Z^@MrzTE$3qe7+p`^DUzn5R8Ozdg7v)uV0i!S8>}d}%{bUjJ%ef|PGq!uem7;;p%7yxo7gP%3}m66Y6u21?~8KHz@#4UEn$_q=Db<x1C<q962_+g$(kBRmd^$BBOM<Xcv9`K126#rfLrF6Wn2&VMX0N#uPa&x_x=tk)I4b6Kw|e%sdTYVO&b+tv@;b94Q$C%3I1R{na(xothOC%3I<_T;wp%(Pxw{I;!^ruEh0w{3m3^U({=t?RJ^rB&wpQs-7!SV>VxZ!5)>VFN8o%qgUQrsuxIe5B9+*Anx_KED4KOU%6t<uP>KfNO@_hVB@;ZRnO4?S!IG!2*W74gJSZUPJi|y+vJN=qIDxO+z;fT`}~dp{riB-piQ67^(p;2PUr$Ca(#u0j>oR*M-*slQ#g9`+yt5{op>}X7HwPAFvPpz9~f91S0l@i0ebdwc&NZb<n=r5b;M4aW!~#aCPi|HF#NYHE;z(RTX+ArYL0~;{QU#rQnsomGF0^AmS1baZz|#a9M1-C`4QgA}$Uu4<>hji-X^Xh)cpNg2^j`OM*Xuh)YAnRSYE<T5c!~9uFp;4~_$W1rg7J&jyo6fM<a<h<GY|8kl?%cq%v)A`XI21e1>g2Z4t}#7_7ya6kAE_%Lu^_yG7Y@G$)S0El=fL_8Kg5j+v?8w(MKK*W>b)4<cP|C1r&=@4-gd^UJC`Zo$9o(B=f!sEg5IDWAZaUw*#2A%|-Y+NJ!4NZiITR_Cs;FZAS?}Dp=i$cV2!}EX@_%nq)5BRa6UkyEn{{|+11}3NS&*ATaNyKkK#O2|Yz?IPM@({5vMBEQP8B87t?gt(P5f6t)fX5mdU}zlN2__!|9tRGAh^N4ZfQO*IDewsJm+&-r1ULfiNP~z|A>wWD$>7O2uG=8u42XCWL>vqee*$j-Zh_<d2}Jx6L|hzR6kHU?y*NZ%5F*ZN86U(2;Q8SSSiyM7kKe>zUM%9jFiw60|Az7O7exFBBK`$_4@~|O_!saki1<4E8kqch@OAJ-i1-ZrH266DDEu^dKl}hhd<-H!3qK7$je5^Q#6Lj9Zum9uHMH9e5#ND`AHeT{@1b8Fz#oHuhrfnD20zAm_!>^<;cIw#Fp2mBh`27?7wn7ktu90y2oZk{9|azT^W<}gxDQ0!3qAxq1m{~Xh`0wt+#T)&lMeuQ2X}*ryF$eMA>uLcvEX6waQJj^D14@&S@5qQ;%Im{I2t?`J{>#{J_9}-JRRGc0Urw{9|xWR)*#|2cnFw$3fR0J5if*i!oLKQr-3uUyCC9k;HhBpZQyUfdm&;MJOfO=3G4#zfrxV;;*AjTXm~J~{1fnKaC3<GL-<Ev^5WnR!9^hAeDH!`^1R@D;8zNZ*xT#P^^UkSyezx`m^?qYEVv9rTng?5Ca3FNDf}jW--|_D2>uBC2-iDe67dU&_&)p=_!h2r_aWk&5b+iGMes#j@2)_^=ON-#mg^(&5%@v)aqw|m2M=1Vo5bJ1cf<FC_v3oH8=eCu-wECg-T@J3!nc9R)4`eGEfDcWcnX+&4VXL$oDA3DNnrBjVDbd;O863Z0+>7wyac=uB94ZC1ty;bjt0+!h^N3cF!@yQ6z~{`_;YwDm^=vlIk+1{{26>WnA{2e4BQDK4p83A*NHpB2gCb;$%lXkgGWKcgOoS(d*W7x+8XK(?*;CK|GzuDFPMA)xI4HfMBE2H6ihxA+y^`mA|3$`0h3P#j{pZl#9{F1VDcz%7&sClo(rD`CXWTr1uue#m%$Uk<ZHmoz^ftR4e%5&c{+FlcoRgN0pA8D-wDnD?}CW;z;nRl2f%y4haln;@MB=|v)~ipa}e=m_zz%mH~2F621I-peg{nc0Bp{Oi2s2X^J4!UO#T{7PV*jO^19$+;5ra-OL!od{Bv+ia3_d30Nw{o-U}Q6?f?;g3hx0X?+*SH+#Vus2k!<Z?+R`QZVM5&hKRdB#C_rY!Q^AW<~)hGCwwq`7??a9Y|fvEd&7sqL&4-T!9&55AmXWBZ{}Xa)8Mn=v%utEfoFr~L&UKV@gj&g9v%%Qp9_u$FNKH`yxz>`5+LFj_zW<)1}2XJn{%=lh&Uad2~G!ZhluyVcY(>j0q+AJf`|{p_kzh?;KSe}5b?M0Jz(-2@VDS&5b<${_-lwb8NLxrJ{p`1{sJQY7~ULA{vr5da0Q6?9e5Eic|Pzv;J+0X@gH!S&k>V*BmV>ZQehF7^m;STBd!9k2`>#MFAJ^-t_=~_f|mi4mjc%USBHol@b|&wg}@H*e<9++aGL)WhTjL1h@V2lx8XOz<X6DA!B-*TOYrkx@>AeT;O`*fZ<ROmLgIaJ7yJmA{2<tz7ZQIB&w_sgCf^Mv-vK7i1ZRP_L&TfmTfpQS!R9=VI2FDQo(v|}!Q?B!YvC*4E5YPTz$?IuA>tVLLNIwWI0ifiBAx-C2_~Nco&g>Y5%-3V0h50Y?hOuvh&#Z$fyqAucL2ABh+Durfyo2FEx?~Z#4VLK^Frcw@UHOAVDiD>uHexS@dWrNF!><x1n?ISaesI(FnL>WfAFUeu?qJGlQ#mZ;KmSf5qM$nyYNEr!r+4N_uz%Wh4J_ALB#bS;^uIFus_<@9Nr52F}w}D6_~s`n7k*LybrhyxIIMN5k3%1J_6hk+yx@;0S^X~hk<*5M?%Em@JKNETyQw}ONe*@d=Z#@8F&GBDMY*qz8Xxv0lW&l9wJVIZvvBNfYZQRA>wTKE-?8Xa5i`^M0^;22uywgd>DKZBEA4W2PVG^z5xCaBK{eE15ADwY|eLy-}7Rx0sjX~PV-t~@;YGhmf#xT`Vg@nyc3u_0PF{D3K2JfcL0-r3T^^!3=ubiw+EBA12+OUgou6MZNcQN!9L&y5OF<-ScQl?!n=UU`-08+E^#Y(XLwIA`Cza)-z9DX{|w$6Og<F+8F(N>JOVxmOg<Gn0vrSpkN0{rKPH|44}(twlg|c+f#*QP3*hs?<gsA##oz_tI75ksmKj<P5wC@a*T9#6m*DT#K*Xyd;#Kg);KkVXDu{R`M7#pN2uvOiUIEr2;w1P|FnIzv3A_#>-T)CVhsS`))4|KZW_jYR5b;j<b};!q@J{dni1-Zr5SaWh_zd_vi1;l02$=j^@LBLVi1-5h7?}Jx_yYKQi1;G>1UM1Ldoz3sm^=%-8N34`-VZ+rCcgyU4?YPIpMqZolm7rd1wIWCABCR>pGSL-!cTy+;k)4{z$dVuyWwAh$&<mm!6^{&Ncb0E@{hqI!ObAza_|aZ@^`@H!2f}WpD66~Y(q@`2lxs2Aw>Kq{3V#2o?-sPZ{iXVaYe5;&pgDH;Z@;Pz~nW-fgQZ^6wmwr`cFo_`A5&diu50lwEv~N49NPI!;HE-i-H0>c+(mhC6Dnxn*7$IS*h|ra;ur-'

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
