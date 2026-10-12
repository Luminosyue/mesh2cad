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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_001.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_001.stl', 'source_sha256': '20909b2418e8943791a9a023bb6455bed889d6b6adaa9f5ba80cc60146ae837d', 'input_faces': 987, 'input_vertices': 546, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.150098979473114, 0.2399137020111084, -0.1330106407403946], [0.1587013304233551, 0.320764422416687, 0.14119969308376312]]}
GEOMETRY_BASE85 = 'c$}r33%phHw#Vn%dLc@BD5V{TqLlPdRF+hvkmERXI@sx<l*%q4$x;-@BS|`XupH8Zl-iZrrA1MBqzENxdy~o|^5*_W|L>T0&avkGeD3Go&K;jI{=YT;WBmSO{?}RmG3VU(^yqd_x$1%c*C1GZ+SpwSTLghf<)C^nvS0CtfqnW7Z#rbyO{t*j0bKs6o_xV2=lAHD3PuJuH|*PQc%R~irx!MC*S}4}CWQ_A4=o;1+<VBCLyP<N6TD0B!NdDGeE5Lg!}_^#qgE|jHz{m!Vw1vK3jdG)4sjGR*R@`Arf?b5^$pSKbF#VBN%;0oaeT1H3s1f1g)<ZI;E|_ecxF#eALsQ!OOo(l*0D=tarSyVGp*LjB)q72V+_yT-+prv{}4C)(~~@I`73Vur+2;d=7GE>zT!514m>dN6)&3^j~`sueoIpP5V!RQ&o<bxBE|<i*Y$)%yy(rsk|aFy%fQ8n{=J`{n}nwuT`(sx@AQivPK?uT<U@j|7j^Lb`&RV(VN!7}hWGP$;TK~L)F;G0tL5>w>y||E40ut6;VYwf`rf*mlj7&V^WuO0gulMVKLZ{Z|4iMwzHZiE@g=vdh~)*(_J3({5}y0B+}tF*?5mHb3SRh3XU}u&)L7j@eB9Jn-9o(FoLJoy&wy*)6i?6SyE!R-4&27iJh3}gw=nOl-Lblb@f-Jz)h!RFZee_It((QmsGG%u-M(%`wJ!5~itqMyn3KyT;kmlU$MNCd!<!%AZ}H&I*J60)p&9<auX;3Dl7wgb_gNZ?Gu7j{dRt4A@StUtRk1jqUa>iezv5+<|7RZ0;}356=k|Q&|9i~DS3IZ}kDuP_@vMojc-bGOJ|nK!k`!NY8(;ClkL#7j_<)y9_;h&^UU*?qNfI8kJ#ld&-mCq*#Q06$n4N^@?z?bW5}s`}e9D1+xbbpd=O2IFcp%Q!mANE5*xe|O{{((^EB}2lc&^!oIDS**1N)?GZ;K^Kc+vV^OQU!Oyl~~t(j+`LrQ)h6o_nX}<|O`#7aIQQcRg<TE1t)H=Ocb!Z8P-&Pn-A|@Uo8a_=;yu{9M19Taw}{ZsRMS?NqZg#-~62C+u0Cgl89CR+5Bg-aTb;5?**r(|L(;27NF)2`{VOd|G0h1(W=K8!$L_PRrf5E0=^94c@;xhI3BK?5g1FX7Jpn`(t=`P8+wiBneNqT(&e8N6%?JZZA#3GpRnSqPU*ZEPur_hQFTEEPur<e?6y_nfQulO?*A46`A;oXH9%PkJ<Q&=WP8IUwB<<jE|n{R!mx+gy-s(lqBIrgWg`0i0}VoULroZ;q1itYaf}OglGOd?m@vb-LCi7ed((keZBqfc!)3axSkUf58A%(an2#3Ke(Pl6wfXFV^dQ6^fHg<#a}%>b`A;Sg9pYx)A^6L4ruGIIOmX%54fH~EUxD_i|hF<edq0-XZ>}tJ}VFBoFC$a>tcPD#kEff@lIP~eU`<w&r&=Cu6>rpwa*IUtQ@^Lk-y@Ge+Jz0SKRW?tSxt-Zbc@(;(7IX$>V{o54iSOil@7c-jWnQ#7%s~wa*IqfNP&+aqY7#u6<S>PM?(*hdwJWFMU>?KYdm<H_g|9J}da*n_LoJw*1T0F`WJ@*CKVGZWb?^@mn0H|H^E7wIm5I`)tk9D6ail*~}YClklKq=&C5LeVpYV;w$3(wZF6c70=^Oe^+ShqqvE${b1I_S3GUvYd>h?E1tIT6+h;d(%8DRPwYN^c@kdqMy@0YFZ+GNqD22*f6Pn5(@hVbotXE&&C?V8TYWqEz&@Na!`F@eRDZ`UuIG>tr*GBYaf|Ekc!<-t>N&*XdJa)M>~lGXSX|E`ifjLC`753={IxH({1vzSwO=kX@fFY7`p`!g+4_KIO?>U6ZG6RZCVq%>4hi{a-_1G1;(89TxSm5Sp5YvlhjR|ei_bYEj}PaNqK;3+&LP^TSX}$85a)cNeTv1kPf=XYE!t;UT>Gprj-GSqvn;NCmg0KOvHTS;H2n4aWBDtd$6wDs+v4#RPuu!{YoBHDtckDZB^zJyy!d*KqR$G~tN!#^7S}$@;@W3fT>GrNIP_T-*FGyR4t-Yosx`iDW0u6uy&-<<lGwR7#DkY(=U&A#;Ng8s^`~D8##DG=bpl>??yA)>oPMq7*Il_Y6Y#Pv)n1I{rC-Zl`DjTZUhV6pu{iW=!O7i9lkl>g(^kds%XY-?>nh%JNBq97<{iB^eqUGpZ`m8auM3`@wr^8X{2aKAul=K~XNY%=*HimPTTjJpJ<}5=Y)<3@p0^*qzd3%NS?d5E7=P_g3l0AeH~h6fO&k7-=M4W`S(Uev_@qDdxaE@@wJ+8;<>7kYTi1K@zF6O6@$kO4!Na~uar#hO2gTE-4x#_VxuvmnX`jBm=kg>xo!(QDga`M|T$JeF{?ezC@S^TZo=n2Ce;qd?G0yl-lVkYR6XMSoEN<$Y0k?Hlyv)>DalKET8N1!rjXqR=k1Vdgry;I=D8EM**WaTMr?1rCQ;X~Gsp8s)>hGz=_4hQ4LtmN4U;9wQKkP#df5k0-?L+nV&f;lXAMHasn)-leO?>S)ZG6RT{IEae_cY|A{`{U=Tz^k3uD_>wariy8c#hvwiw8CQ?`d8feor%XclkPSKU~k-7T10u#JL}?=WUDYc{{|pzped(#kF5hT<?c#zhH6g7Zlg~;g-MR8N*-ihg<&PeR9iR?|a+&=zVV!U+;$(nfT#-auZ+gd)xSm=S=(%r(X#9=zVPZ1&eFHU~%mi@^JcvJe+<ZFE9Oq#r3{rP;R%!dETe@6D+RxLqc4i1JdtXT<<3+9zF-;eu%~Oen=RH=Y4uV#Nv8CB#guJKFdGER~Y{K9MJLyxBT^aU!jQ~;wFCh9MHs9JZ<Zv&*?0GeLiU7hdB2`LO%LDj{6}N*ZUzB*ZUzB&u~8^FAn!Z^5SqmB+sAwA(?gsYY)WL`{epwhsE{14#oBUxxP1I@bJA9aP33G_i79tzE`7hz{B@y3?9B$10LRoH~d4~@DK0L8~$P6YWeGZdlNtGPi=j)pSAVTzIA3izV@3oeu&%n+9&FJHM(BC&#&**7(9Hh#^B+5HP&C>t1)=^UX8)C`d*Fo*Y|2}I>OgYpCjnGQE`2apyzqT^?arM7kGI8U;8ih*Zce?et4hX#1HT1TRwW<-uUZzCS&|VT+h84U(Yjo?lpLL?lricd$a$n<N289rxw?9NQj%~rxw@WamDTPQ;X|4B#dL8pIThcA&T4Qrxwo`{`UE)#VvpP{M6!E6W=~RwRqOVx6e;4p0o8g&rd@>=J~0`^&DbxJ%{AsoI~<(&LMg6IfqzW&mr0UjXZzuhiji=aqY80ocrP0r&wJ3lo03sw)R;T*FH;ey&tZ9mc_NtQe5wcTmFg{8vc4e-0~0alN<heKV17Di>GaUxF4>4mc_FszTWq?@fEl671us1<fH!dSr*qm%i`K+<;9`TvbgqH7S}#2FAjZH(fp>q4m|G*-ybu0`2L&X`W#T-?=pD!{+QzW98lkXGkEy^8@N923*Ub;c=-MsxIXW*{1q=V{KMyfhQH!@{Pp>rt&hI{SuY+xd=6;hD;~c8rno*YGw~JAi?7cO_5C;Hug~@L{WpV$@4p#5eE-eH`3LX689b-&zZpEM@4p#5!~1X9nrHdC(ZB0CA;js^^_&pm`hFVc5XHlOoO6ic+F#rF+DGTb*S^^JYhN4~f9-QK#y`Y4hlKI959J(UalOxJalOx3HuM~i(}(K1LY#h6*QL1jm0GvZpZ-zn7W&gC=EbKUwDGm?D>DAt-vySB_EW|`#Hm{tU*DgkZWh<`o5l6~mcF=$=WqUgArII0Iutj5zhLq3y%cc!_X`#e->cC$=I<9Q9==xtZvTEE4>$bn-!E9)^0$A#U~wDY{{4c*!}n@*UFPo>@^D*!^Y;rOAM^JM77yR6F?jf1jrG^}Y7DM@R$g9xug1oaKC4IUuYF#se!=p!O@lz>;GlZYzjx$MeFT($s+0fJXJE_!)t~ybZFAcH_fLIRrGnr$Cl5NA<oG<`q@1(gadM86|2TQv$)N>7Aijg#=YKeP*~!sPE^=}Za+;GyPOfp%+Q~~!o_2C>%Fp>7thXB<;^M6&_q$HMCP&kh&m(*uAdg^AIo*TUjmY%?@g$dU|H;WtCpSC)lT-e)N$|ZY<ztD@IQ%4kZ+r`g+ZvxT{Dj9!e1!9V7z^jo@P3fb%aKEJ31^8TJ`(F>>RS%o2>wl(UyfS$CVl}m6~D)+$yNBsb@`porT%hFq;|qj>M3iJdWqjSe2!-P6xZP*u8q$9n)U6Z&QG!aGJHp~o|{>ZT+^q)r55LcKaGDGp9#L#iQD|a7AIFaS>rxy?DP(&$2z$n@IIsPYw5-folJBxfY0UMP0Z=+^si1<IGId*iCxL@@8a~^P9AeIm-)Xs`7Q8RkrVfS!9XXi0zWUy+yUf~{DR56E16U3q=}RJ1FsKCdG2-KC$ZKB{_}$iJik)b(;0r^n<B?R{9D1T3!LXM9tdyYw1ymYm@Dg(9FLLXSL!g4{0EV*Gi!ScfAJki{I$fp5Kbw$G$dzB^3H?XZ}3?|O{88c$o)3gKyoyJ(`0J3mU_))4Fky03a)F&CER}u{PmTZHD;eogs)tKwfKz1Zw33QF-2`iEb;jOzsc;A#&FIuew+Qa7p{%DrfbP1oF$I<e87I4NNp#QOZUQL=4Rou0zN7H^g0#c)0w@MqW%NfGnLpkvbMSG^Rf8UVLX@Xa3R-5=k8^FJE-$q*8c&%qgc;PtfvcmZ4|ZW0zMD_5BN;*Z=Kxg<UJ?-oNREPHFx@Br|)p`x4`>k@H^d&PjWKF$q+uT5ctnzPB*9jaFTQK5b-7U;f{ZIr?)$q?PLM-Q_d~`>+htZ!-hIJBk=Q{WbP31NPfXm@Rd0)I5}1F1zuN3dG7V#C$U}${O45)JiixMPdE69Z$)wp#b4$Lx9;#;$apBch0_Ld)MKu!PjbvA#~;*T3i&ILuN!NdjsFY8mH4j^?-Dpwgv&|P>~!)9pYGHz#kK24y>jH<&NYx6r^4wWYV`{BTEH5HkmC%vZXlO%|0VF(S8CRrTvOoNAI`t9XT&eZ^%36+#62CKPw;z)ebOAxPcq)le)|@#&AFzMqd(VL;)u^D?AIyOb_%(4FFeHDC*hNWPeuInI`zk=8?~%R{fDw=4rkxU+7__S@4%-X;|1)COSm>V_gmKYF?C+R`afZQhV|Uadb+dMGSs3w_(J?Y;WNR%adL~3txozlS?4}$=Jbb7-|pnEf%h4MUmG_*(aB^dgZaE%;6IZ&U7h~j$@5Z6;!Etxj{kX1Z*wxs$$aMj83YIZ%TBPqPRhICwNBawe%=$z9ZVj{FPO~h!<^MlPI2;J;C1<w=Ux|n5^H_nKR>L%^IOe&y24L<%ah|;{M*9qJor7s_*!@ir*-70%UoHX<d{W{->Ji7@|P!HSJpNQ|JB5m`0I&xF`UZ7<wSC}A+PWeZUOaJM@^(&&y#x_*FbWd0;eg|YCZLu&l(1kqb*$5kxRJ$9Qf-iHEYH`nGD~)aQ>M+BYw}bpTxHuaogbY5q?wHC(Ype1mkV&w{PIujB6@6`f{x$j`)1Uew|EhCzDI}!W8B{0iWmLQyxFPPJQv|N-fJ%|7+PZmDxA4w)yPy+wrN(cs~2$Vy=zO{f6~@NS)`i{*Uk-!+LIEJ?F94#!!p%z@NeYBR&&+tdkv1E^zW$;Kyo<UIbRr$!$))V~*OQ-^X8kFLg3L@ME<_AA>FW?@m5tthVT9u|=Ox>`x>1`Q-WzUDeg(hyp)WTlAl-LDn_b$svr@7Cj*4c?sw10%@lGSZ&em;U%0aIT^-SZPD%EC!7y<dJa6*7JYTfa}!=`$S-5H*TClx^lRilBx1h?pM%kj$$xOfZVaDc=vU!1EMkkk8g8Orq;_*6wrJ%lda9F_jMWx>82ko+{TrTYx5TG0oCTW-PqjrK2CsHtEf}jk6`vR3+=BcsM(h^k`V)LAzONFa9eJn1<u!5-U|lWQQ*)@nv(!;)b_{i{#D0<MBG+UG*Ksa$&u9L#?2}>aolBX&i0{-P?9K0(Uy*%&8{f0>d=Dz}y&6xhvCOH6EuY=)^iC%|oP5DpZP6uQm7I)ovM=SwYK#5=fAQ_<WJ2J_YKyLqE&4JipEFil^kQt$7ZUsPh<zcs_Mxk}wI5mF$7+j~8x%cQ*Hca^vnI7gUz75@g!6DGhr&~B(PzR-ILrUvnPSFji|znF;e4pm^Wdqr=z%HEO?bUT{v#vyOYo_T-bnt+5ql$i4n;R1|Dh4P34DstufwT0Vv8OKH_>aU-Mok`TDgk;x6`fRskZ3D;dc$#G<d4r8lNU`7VKeosxA6(cy$14#aQi!@mUM!R^(qBv0ITVfd9YoeVrH`$onu{Hj?`q*43IlHIEuBrjAmx`qcRl_KRE>xh6Zgj!!Z7Lgp`KpA@rqdNRL+?^I>>=04_EVxN!Wdp3dZK_$Ld6UcQtb1GrWXXBmz(8*t&>|(68=%rv)oZR8$`;;H6ExHVU@$Kd0&cKh=7F~!f`X5fdWURL6CD@`bBKDUN`yz6EkFM_4UZcQ|)fSy9@Z4ox^W}Q5CbdNmPI+F!`FbaZ!BcI~XTeK2S9UUjvD%{3@Dt8QIQ=v{)fPP{<+%y3b>y!RvDd+;8hR7?t3~Wh@Hq^9GWidS*eAnh1o{m)jfmKy2f<DB%hc}ah%H*VihkJXHt<wibPf0o2Acs-wcFrxGMojQ4o|g3*ML_V>@>z|PsitFIG;xTmm~IR<VwN+VSL{pMw-0S;j)R`gIQM__SDnVU<q}UniW##%Ip`pE^<vi<T}o0?nTUB!af<n-s#2srF^HVu{XbGeiiol9emI3<a<zs@70~;8qb_6*atpy`eP@5bF!PU+M=HWtLkKelOIxkthVTn@E709o!k}pvD%^=V2l2zldl-7EqWQY=!=Q{Rm8rSTtA>|y0zCT@ME<_7ZiBzvaSVkJy?_4qKBkBFX4QH)C!(zi#{7(!ufC~BN?kLx+DCA^N~(J15dR@Uz_sWgx3c0*NWI1;8Pv_Ci$yJ>^I?41>KbVRU&p%_>4qvhSSK1E&5uxiC$0bo{89^m8<A!PM;1>wMEy2-w?1z;HmcM_%wyHU^C&Vw&<Gh>Il}BvD!27Sr6y7<X<1L+mfpQ{?qW?OpK1?oe7sW$vuR1oz9+mh8irRj#9G*)cJ7si(D7ECLePh7clo?<}YKPjAZXz&iv>2PE}`b{=odI?DGkH&+g)TP?hi1UF5oxIaRUcvwu1Lsgu7u*~?gM(JR1eNn9uUQ+}+r=uhw$-z&vG@ME<_AB!#e3MYFQt1Wstw&+WUy(eN{LazPjquknS7x=N-q7N$Y++|(QI;qE+)D}G~<#`F`o17d0PqjsNhL>=z>f}boYK!g!KjB>0>4orATlCPB=O(;fC4cRR{VIIwp|_B~Uc}x4pCi!C$bUq{ZU&zl(Qm=&#)vI?DBMK9LhTktY|+Y9^mM1&!BcI~C%|tQSQegYx5K9yoCSLno@$Fe0bZTJ&S0$eqxif6=QGIvO2j^cTnE8_I=*iaqZ4@_h07Ll4`W^J*i#Fs!E)*-H9M9%S7pD*b&+fGDcA8?=3c`5<?NFi**jM<e+A#EdhE^p%&)~hzl-nLzxW>1((fd>{>7YH*z(yuPJiy?GAG|KR$KH+u%n#Z?c~RlAFD0;GyKK3x0AaAKUQ1xaoD1ZoP5n#ZPBIJqAw-(*Ae?ta{Y*|<JNw3fgh_ax?F+hF6&zCq&{m>TXb>C^AgTCJ2?`bYKuMxUc$MWlTnP-7TpDY!uc4d7r|3)(buIsH{ta<`Hzm+ufwN4`W^DukJ#_P=ScJ^<UcZEp8}sz=(piCDq@Si4sN1fqjrlTwrJ%ldWO>-;HkFghVUx}`wu+T?tsrJa2D(_c&aVBA-uYPwP&pMWB9xV=l0}(En>GPS2_64!1rxpbRq9!aCwK^#jL9XdukCiD5Z{4v*W09HTH{K7r7>%a~&5m_fqDUvQI{_cX~5_CEuy~?9CsUe-!)tZvCF|JvfT*)!pQ}hdD=K%V+mF{iTzCIQfpT+M=HatL@}oCqJe9SZ&c?;4i*?<oh1@vD%{lf-U+gC*LwwTl6Yy(LIU%ZN%<LuAk6#-P-FF__5le%NKa=vaTgg8n7m{MUO~%Uc&hnCpF-yw&<?#63+4p*l5OTi#`{A!nx4t5_qaDdU(on6JBqSzh1<C13nGVTgl%bVsC{{4Rmwz*NE87;WHZjE}TY3Y|+EvCVC^aD~Z^mm8<BPPN(6iw&+Ii8v*tNJk?I)(;Uu%Jq}N`MK^-ixnO59R{L>$Hp2N#@^6gTXOgQt{Ac3(E-}s}@8fXUO70P?E6tuNp$4m{qtxs#)VVtQMXrlnlP|fBOPJe}`K#C`quD!snEyQAsRr!LpO{~peSR<BvwQd+)aHA254rARPHk-Y?0%=ea`I0n-!oQQbPlYJlZj4#PWiFgqIcmhzWszp;Kyo<J|0_iUnlz*t1Wspw&-5O-WRcZk?UvlF>dYk3;bAZ(G?0jcUjjmC&#fSwMCCid0xW#RwuRKskZ2D@Dk27os40uw&?TVC!CLUdMP~B7JYrna}!>h$zMNWZ-&ot==aEfT*Q74KDE%NlD}5OJ{3M=(A(fNCSr@e9&VyHQM;uPTeNZ&{fN^Y;i<Oh6X7=!>`8d4-4UNt;VjrJc&aV>M0lMCb{1o`XW_F6&S#N-Q^Y=tTovH|2)^5haUOYR!R0-2k7QjP*;7lY!D{L#H9MX<*JQuQb&+fG71wbYb9*s=HTz@?d#4}sb9|?cV{iV<{5tIOiG0uQ<$F+v@72BJx}Q09u;sG{oZjQ)3Mcy+t1bFPu%n$!a`H>ckJT2v8-MY=+R1%^AFD0;1Z>g$o&3O9ZP71ai@u!LKSb=y$@L4m(5<~efgh_ax?+LnF6&w@^=D0Li@q`Cc?sv+oYaP=+M>^gmvBDHNrti7qPxRSIRC}z=isTf=o?a=oA7#z{0$=ZTkts^{XY4RkJ#_Sr#89;`D;h)7VycSx5FtDu|?kiH_>lWyXPXdXyq#UQKvh>Q*F^F!S6<}Iq+1w6Fx2AEZA&#sxA5?cy$Lmo3YqEx}^%LAM`){&t3fYKY1T1i2aXW*qQNH=c6<Cx>(_h^gX(jm-n-R0{0(z$h${=NrV3am@~2f'

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
