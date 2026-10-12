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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_005.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_005.stl', 'source_sha256': '62d2a7b812e78157b563c2b4bb45e4f8255b023362640a368ba1d4f380888947', 'input_faces': 824, 'input_vertices': 716, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11114159971475601, -0.20232266187667847, -0.49999988079071045], [0.09894797205924988, -0.012402012944221497, 0.3764703869819641]]}
GEOMETRY_BASE85 = 'c$}r32Xqxx_x2}244_o05%3DqI|9;#p@<Mf5@`Y=mrkgmcN{=?l^&W9N-ixx=)DCPN<x<ssvurb1VoV+1VlvtXP^DdIOqKDx7N45kG1xCe)l<h&YanE=FHr=d3~dsW_T&L!T;VgraZ`2EzrO)C|)&k8$-Jd930!F+o1CO;zooSIiyej9G(4Pt7g${!;GQEs1jYf4eBzmL``3b+TE*{DC;ZHz5l?$13UHW*neQxZsa%W)MrpP;ScKBDXyFNT=Jbt)yn$bE>+ey#`pjDFAEJNZBWVqq4xd(yGX5n{`u~J#}8z_w!`ZOW0&qFHNs0wAvJeCxFomNd}HL-m*sZ4zpcl$P`>%!FTWx6>-qDhTo2`&>FZ@b!R`r)@4I;Fq8yLr2fs>|<23wJ+0SwQEAM!8-x*J^qn3~H=)N-^<I{=CeglW+ot60=RNq>;=Ugb?oHSVaw(j?we_qzX@tysm{-)+T^$%Vfr}%DtG~cODpk<umJL9)B-x<H|JLC83KE@wN@1xcs@8P3THQ)Ru%ZX6Fv1sgZ*}vx79n(%qZQhyvLkW|m4*O}D+^_CWyRb&~<M?NHNZ;OEZI9f)<{LHA_J{JVz3cbMy6XAM3LljHHDlj8zGk=F-$zUMdTH8TttaXb(0r#3y6@D%(tM{5fn(9^?;0z|6Fk~`Q(el}e7o0)Kq%j|cC8BK8zb+oA>T-CqSo`=^x1MhM>K!z_JBNYvk}+f!ZNwem>;kH&g+{4lXiH0`#^o^+xM!bD0PExOv=Xfe{`GYt>)YBUY7IUulvK|u7&cga^vLnZtD4M=Uflvo7q=#KXvLVzCY&?d3~9hZ+x<q$62SkTL0l=Pu30Ln}63hE$grO!EM!!hw{yu4^PN`c2|*p@XSu0Zx5DUke_Q+QqGIjcGWq`w>954?8I4le)p79&-<ZqXUGrkR(-2>njEKp2m9vXg>t_^E4!?NziMf<p8rgf>xrrPzNj&B-SEM8#&48eD%TBrYjO2_eZN`e2Q=Tw4{m|q{L}f~^RD~OdAId^oOj)K&b#?`QTG2{#n&Cy4WH&a>xS+->xQA{W8DZ;DyohX^W4&WXP(>T3o5=d4+EO-%tNbO9`>Iu;QeBq^y@y>NxKaD)}Z%Oyz|Ofo0IcrmFDw1eY0H0g2}3He)Q~kDBmhNQ~I{<-@Yu@F{4yA^>{IVf+bbonLieMvqzZ}Wgf1|qSh1h$JBgh{sc-yuzzn1pI@w#y6>!$c5(RrJzw&9d`-@WfbN%CzCV<2ojfb&gQfeWD$4m_6^l^n?~K!zltCGfv(6iu@2uO_O86fw;qkN$@OjsKYh7fr>~A^zrt9VPXcvAhU5>wq!G8LF>05V~%kvUg_SYU|{@}h~=|1iYM&L2~HM`6G`Y%tH;}0gPzM1&<s!+bsez`m@TlbrO&iAz?@SXXC`RUhuXMXCwGe1q;cjl+#qdr!<TykC+3-7akDV5i;Q%z3G{tMpQqs%L;|GMw2|EA_U>%Z<h>whp3zH@%#!)5(#&9@dmm-P=6_)$48&V9kseCNL4cYJ4F;l5yMzH?u&=LC6Od>obHohKH2f8QD@-g#xsxyt=C8qeeZZy#A7-49M|%J&`3_mwMlJfwdpgX||5&%WL6tUNDfYExd9vR~r--)g6L&!ZiGUa6b?Vw0>-K=Xs=ZCM}7@v&dK$!u94zwU3_CdVIq^$d?^M5`3<JaPQMsZBh8Dwh6Q>ZE<#PqpH_USXXHPSkv?GrI4rGq&zyoe97<ucz~T-rp=$o+tQL%w8T(sj~99G?-xz`+s*#@z&F{Hgf+J^7DAG&iFLnS!b-V><1er^7BLb8hL-QUaaN*<IEIq9n8_ImFvqaQa(+N|Je#2fAtB{_w9R`*Z+}AIlojEzTUB(n40gb8|Lt(%6N<iYvg)sJX@^fyX(~-s_(8#PuUOpZ}2#W$H+SS;XBubQ%_@P0{d2%6s7);=c)C?b!}?Cb6p4fP33v@Qa|qJ(P~*w|NSp`UbQ*S>-p;y56S((cjlo}PhbCu>T%(E)P3iAG&JA29{-n*>oIU|9G~Bt-}897CiD6GnSJw*7+xQ)XXNwPXRLC(&h=<&zPa_FydHgykNrB=qoMn_9_?86%?Z6yyywgA34hW6elL=p=Yw^7B=^%eiRa1bwfuYw-?Znj-#&|6-+bTqQGDO9Ed1Q!k5$$sE4c?hXTi6gf1KhyUv|e><-TLiZY$Rf-*?@({~o`v-)6%WxqXMu%J`i+2QRl_jTpkm^-D6}$6L2#AJ5@tvkvmQHsHJSb7W?DT)~UcJpK-s@tn|qn;if7Cd&HY9G7*jiPDcfFEigaV;b>sy)rt*JANaYeQWAx?4NIQ+Uwi(=JPmL=a=h4;8ZQXzw~;<^_<sxrOZ24MOnwpMjhq#Wx@BSE#v&9k-WaWUrCvtM$w;EONDRdoXq2y+Md_Fv~oP2upTK&9S*#qJ|`p;l-HL5-^sUb=au8P&4PTLI`7}gMxLkn8LY#;)%Q=VOQ$EweE3GT2`S#=4c5$~u9HR=p3l2;D(i!DTt4{0S<|?mi5+Bpg1d4m^T!J2=lbl(!u{O3!{f>ObG#gP)d<di{0i^C#`8Heeyft9+}Es@J~^KQTmIsCgZGg3gKPZ#bQAkdot@(~;XCV?`RF*0V<Y>{{IRb_a-AzaV?RTcMbfuQrpWPZc+7r|Xz823_c}nnzsy7S=gr~ct=mb~%_wzmxA%H+j@Mdsn~x{o{1oMQ;oEn9<NnN7r%Hc$aJTpRvKBVPdH9x(=Z{=`JiCS@Q@&XQKJLqAk8|?62)@a_b6wc83v)dKS9yO67P3Dejpz50^X&ijg10OCJc;@b6gZ~T%^9cR_;}8@vwtAxb1?5gUcbf^;&I-sww>~QbNBIiiA+rKj^8&2{)|c7e`GygZ*uM7<5{$f{adGby^7z#?=QalhWEcEnXlg*TRGo)i`S2#752&cz<1{@j?15Q9dG~eC7zE(hHjO|HD$Fjf2{C;od5QJmMZ<2(;Ca;H6xbreiPTEc#k(Yem3|2*0vPycntXNy3zfoNwVK@vz2~~jmzb61wNa~^&Og>ua61?_sV$!-<gNb_yeOSaz7KwaQzR?JtU8J)I@b28Vh*6dOnW*=LI;w@XmvBoPV<K+;@zN9prqrM~vnAPpZuM5wp_d^*9_p)>R{XjGX8GfpP3F+r<0*<b*t4>%V=J`QRK^;C?qAe~G;*-tqhTcINREN=osLGx+nT%KSI%x2DN{;5+>rXPd|K_}cS%obf)dKQVLV_ahU&S^7|l_qfbh)wd$1$m0s!Zo_qR*4qUY<a`cxZ^`@p+sF0kx;0gvubWMH{9z^8Pu|Gy>%M2-?0Sp)X<So2e+I7A;(p4V-YWC4F8Sa)budnu@_6lb)p0$fr+AOcaC~Q;fAbp8&#P6qf80j`tL=1|58pXo&iKtM@XH<NIxMQj*KeCj$~cXo{p30sxLA&l%US2|WS8^b-?FrFT{v~{r5ERVep!R_f8WB-jpvIi`Bu|<T%YKo?Ds9QSnlVCTYO!>cb;?XN(<z5VV-$|^GDW^`TnfSc|C8M2kWHC`z@0Ewe+L%sP+6LpRAjamW9{1?ceZoSnO+jUB4Hh)W;dWeJBIZw|h@`Jp1B#ob?Q4JvVB8&hy;yG5`Hr7s>Ja>pbJ%;o`z@Urm$qKd|pH-xr<V>86g8=h1|3RXm&GJ+5F1d|dB_WyyISsQRPyjZD?>T=N4zCvOdM|7%lmznd$^Z&&)3{TjFUJpMURj^8eSN!hQJbWD!ZT7RDNU#h_K@c0BdKmG8ny?6M%oH<^O$CrFk`hh{2c-{Nu2wz95j_gvdM~pL2>>&5=tdo@w%6S!hV=L$5cLXCx5q@4;ypi*dyx{swo+!s-C9LN0ynUJ1)%9s|zeeQBUEb@(8dB_ntaIKayOisF)Dd~!eemsSH@Kfihxq$Wj+yLZ9q=X0m*>TvK9%>2-$9I%U-SEfmq*FZKJyVDFW#S6Mqlpd;1eEy`vji1e|3|-e?j6_?{(oD-C3C@#)w;Tp4h|NbN{$s`;&f=^$ZScuk>S2Pm<S*FSa^w|L!k*-Y5Oa^-sOMQ+|H5hU=WVi|66;1nC>ClX$zEvC_8&SCYQ3e<J_B(?6fAXP{Grl5dtfna=g>&UuY~lkc4aMNabf*7){(K5Bm>eP2xNbUx1?OW&@4NBYKBVf=n_N;9P&D|ZL^eZkHg#rZYT*-stFzdJ-UQ2IA3*OSk;=F9MJ=Hl<wPtWsv^@(+r{aX7^%IE*UXO)!xjn_BG=TCbq`_{B<8)d)sPw?+DPu}1<PL7a%V28ouADBnUcgO!AC+C0uY=it9SBt+_#${8E*Dkh`pY!`fDE*r+j`KM0Wl)aS%J{Z?FBJHheRJGH*}w1B0Ip9jL#=b6#=LHIf3{s2&w#qJZuYIm+m$+8ewF+6-`no(-)gr`*2nC~zArs&tGCYPCqHsOWq0!LwLhiHy4hE*Zui#5=(e4Y_cHr-(PdnRzE$}9X`4&iz4bBHU0WqTx4xwGZ`OK+=hgX>s^1}w>mPG$ySHwJd14;VNA{gMJJ0jJX!cFtLY}ubdvQI_9@(zcb46MH{q*EMWxqzFZ;vZJj?3y@iGLq&x<{?^*|1^qdXL(poEPKs3jE$Lb)zyKv*i+5|6s#)>Un9ES)Q-p!PVT)ruOo<d@pnTt@<mKdRhg}$>;50oh9mdL7fA86WCwZl6|}n@z?%Jse^Ct^euHgzEkJG`Q@ACaaEtG)Y({4Sk}#e@6^p&e~jO=y)#o8zqP0zzlX2(rCPVJ6T9U2-)7%hUYD<zX>arVsWe`#|FG9&J^k?A<HGqeHjh>7Un@n<6aS{M>iONk-@omOqqrZeGxo(qd7rY&jZ(%F2;=z^Opa5|m+@l_dEWhw@0{Nzzsk>nHE~Kmc5(&&yMj`EmGfm6yduw|wY;;EZ_QpL=ZU{)N2UJG`SJx?s^kA>s=WXDmb6sQ%hx6OJwu@wr9S?atK|6&z8<5VuV2#md-wcCYTbU=HCyp<UW|wjWSxU~8Yt(*D%+dCf6T3`)Xg4$n$LTDb){~`x<7}LZ%nVG*5Pq>{@pfPd1ZcDDbM&hZE9(CeW(^CpDXMyimG+^bF!?n0pIE0IC__lKa-F1E2nZlS9=_j<BU*!t7AUde_(tbwLYbLZc%(^J@g-zbvEF;bw2r~JTHOK5$gPzahK~eDngy--zM{V^*jUn_kK*0=e6avQ*ysUo^4Z(E36K$laC*7^PYEe%yX{Wpofa@)Xltqdz&&&r*81w{!djNA?tkSD(8>-k?&u=0{mRp^U^l&I1Q^CKezO_q~zNRVr8AJ?#RdS+G~5udYb-Y%6_ezX}m67*`ban=dZGE{+8?5FTRG?u_|}?`|SDEitqom8Xxb6OL#ny)7URwg6Gev1kNushtF?dm>j2X|1jx0&#Ok!372I5yW{x1MN%Wo+q-hV{_1@d-`r4L_8%-0!~HL=#QyD){2ZR#O!0&M5puuA!qU=r?$_@3>&Oz)ci-c6t0%`3C|_0PInRMs-X7BTjXEgb_XIAl;rtxAq;DqQ+a&w_;xa!s<ja3Wjz9CVO-lc*&s>({@35ZF6P`=0lP{!izxtHtQ;S4?&YiGa`ho6?R>*!==RYR58~W}Ixm}mJ()X`@L;6;>GSatO43xfIr6vE})uA@h_s>n^zc0J8g8z=8;&AEvX6%x_wP-!x57u;NKW-rB&%G~yhc?>OVZU#0=?5=AlD>VP_iOyxbgAs8^l9$r;y519-G=PnzsP>y{?ZSg&dC0(+uYB_a*FSZzR7=Y_fB2zr%OIwufu=jI$Uck{Q&%6ooif&F73FVE*~a($8Vk~%XRBuCVKbl^zUy|nf>jzc%0b=a{tk9C33y4u|IDD*P(Kvd=G2+B93|cx68y!-(Sc$rqs=-Ablh5s!|94Gv6X_-R$2j&W}k-kp70^O8>#A`3c_h?(`o#*kys#8(Wm~Xzy($egA?ao)6K(xDIvR<=>M|_u+a*SHy9>$-k3j?#lh|t}lJ_SY`e@fJ1}0|C_D(ydQdte@9R0#(uA!T(>Wi<T`3qKEVCwuEG6`naqB_9elnPMR9&Fzx0jvkvz_tjo9zdQ2OSj?8<z$v)p*L-|&1tb^aa?zWe<ezB&F|={wh>iN6zed}m#9eB(~DZFK!P>xtEg*Apu?M)7T|Kfxh=rSGg)L9AECP}Mh{@cL%0xFmgNJ@+T@dLGbx8}|kO=7;R#z7xQGCs_H3;@h}S89Up{b=}1GWovd1-cIxFkE0IDan<gw`i~y)`)$oPH<aezq4vf~Kae4ZT;~FH3(EVcFGcmuVf_Bh)O=$+zdy7!-|CuUb|~M-eIZfyvrqF=FLV8Lzcv3J7u5Y58B;^~cCnta4*va`zvzuKa$K74PyST?{%9P~@^@X}zguqpmGtc`oi}>x<BwK-r#_bEJM}SQRNtwO?mP9dbRYEz=sxP>`$+RqAKiEA6VQFs$JTtOK4uFo->J{#)%?7+axdR+kDr(GU-$j(o+*C7$h;|3zT-Rj#ucrfvWHVc`R3SritqNL<vYHU@6-AT%-DJ;r2qXj#drGA^IaeLme!B2((gM$`R2ujJH5VJA1&V<Kk@@wKlb2XH;3}A{B^c?eWxEi-|?M%TOViK={2EzV|$NeukVgi%XfSy-?*yvv+3&&2SWK)(*|DO?MKUZedPP}e!hD;H>4lEeU8_6`_b}UANi)<PtVLNL;04k=L)ay_M_#y^+$d{?|;?JouPa)!z{&j``7Z_^MZU^@Bb#=yX$_Pxr*=hujRWw@`HLErvGk-^34~g72mCcmhX-q`Mz(o`QLcu(UAU=(TeZRe=Xnjk#B1KSjCE+2<fN)b=>Q_<Ja<CANhW*A2WRAsgVAr(TeZZLCbf2<lFi<vz|T|$`2mdt@!RZwS32S@`GAGM#+-tA^m?|Q+#)xX!)*>eB+w7{@0&yA(U?w=&$(h`mg1?$Ax@r_(OG_pOD7ShnjCEW<2io-F05ecjpiCZLOc+PdidW`S#(bitpB0%Xj-neo*Vjj9PUlly8){qxkMT(emB;Bi|gM_G2Yo+Y!n){T+6CeYeh9zPn%K`?Y@TyB9Wx@~!2qw|ITG4qCpuU*uc*INL2+6Vg91KiTWM<J9t9ANjV{kFo2IP6tByM*gy1->tKj@A}9O>ixXZZeB?Ltrl~<zT1zM@A}9$Mr!?xt+_IkZ)JIBh1Ylc(emB;Bj2z0U-|jYP`){QgyOsXYx!>dk#Fh!_x(F1q`!5v;=BE8`L2)rfZopq<6tP?-g(gW`ffj3zB_M`AJpsM{O?(Ge{-DTyLHg=T_5?zC~f@s9p``f(;po7`tJC(eAh?5PwU5ifAgu3ey=#ick7_#yFT(Qtsh^-^m8HoWm^^BeSX&RT_5=YeVkF{(?j{@^{k5Tj#JBb>yLa}A7{5OFNE^#Cp{J49jBK6@AC=g`?L9WlkfcfiSvHI$gcX%`vL#-qSDvD&sy-^@#OsJnAdmr3*XlAjUks(y}mn7;0LvQ--2U@yuN$9@QoSjIGyj;KFxQ&Uz;<u@iZ*F)9btAf$!JzU(UV7>$~~zEiK=g6`Aby-E|LsKpUs?eP8#T@B6ks9wVy70gwOheS!U;o<FzwT(9ru!#8GX`3<(O@cM2(eBVrMoOu6W>OS5-__hA+JSjW9zB_;5Tl#on4y1T}cRcU|dVZttZLja<!?*Qu;(dtjJMTk+djH0(qh9~t`m=AuYsY&%=LxUx9xr^Kp1(W(l-GCj;hXW=IPreQuldgV8B6Qmj6HnL>$~d`{D77pm{2&~>;L<F%f7AW?;C!>>$~~zgZlXKzQ|b7lJm9qjRDPfu6JAW-Rpg&>O0q$?z`8Q?qfa&b>ErKNt%!Oqx<gs(S4jRW0mT==S%ZteWI2Bx<~7B*Yo;Hh$$i>vyt2A-pTWy_8^n~IU4#u?Gan$|LQ;OQN41N|KI<##}YAyw?s66RswGpL2aKx8-N=i=Tqor@EQ?^M6>~uE<_O50h8`V5ch$$0Utu!L}(vyALLAg9s=*ADIuZ<m~<(ExDl9i4}y3&v<Em9ZBwAb!NZX=1)2)BMVuA!Ihb@8g19f3^caFT9{M@>EZP=9<H7OBSp+=`J}Tm}h?!v0eF)+aVA7Ka;;*1H!I#mt68aVRE99(%UIw2QaYMv>FzG=A@nkUR83gfS=zQ=Ew5^3M1}{d=TIdb%B@uT-B!Nj!Ac*IINxwl5Cqt9KchHssO$H|;Ck1*3{Jn_ZMC<^QUO*790F&NA5buTV0RM)zBhbCzy~sHN{SACq#1jz*z@*<Ih&O>re?br*h8_SvLEG2R!{Ecn`5O8J{6NItBGSO5w-Lnq!K9B7#HXNX;J?v!5qb)I3ON^{e}n%NktxhD(!r$vMGzkclNw<h#8=>@gEOJ+Ci2L;iMDibI`W7!2+b+tI+*ksg7`d`G$M?H_(yox!8y@(4|(L>L)&%mb>tDhBJ_0;KY&TY!#Ieq;xlRXFb?9M(e?xQb+kP~9(j+@_5=6_<Pql;T1>=!FzKsd9K=82GijkP4&vX@b{|{}ZGRz;yuZ+PAABEq#6F>AL_7tPz81zo{3||_77gPdevY=M;4)}?2}<5e(5K+1$RmDJL^%<E7|f*k!#Ic^;xlRSFb?8>(Dnzo9NJ!nlJ_$75AYwzBQ7hVs)&qW(zg)AFAQeVieVhYS)r7Z6@5@!9%xo@R`inxS`}PDM0F8az@()R#9?64$_V0Y&@ABUXe$8C2F`|@0?_K<+9K+SC<!L5fgpYZOj;K~TpC&uTn}xPpryg3ky8m;5B!OUJ|Y@Hn}a_^+xyT);6}(H9*Vq=pznj<N6trx=E!Z1eGvOa^cT?>8V&A>wkT+0aAV{Uk49c=XcRaKIjs@V$c@H6h&zcGETRcC2HXQ}O`%P|O^`$U8S*}cHU&3D&c}!t<i=nh#N9;<7tsvb65I=IA3~dfn<0mI9P-*hKLme>oOXzo$Zd&z5DyYDNkj{12k<bowSu+)w?Gc@ROH1%TY+04Cl=8GxgD?%;*lc06wwCS1w0mQZJ}+zZIDAe6M4O%ZNY7k(;LwRxm~ai;?G6Q710se5Bvq%Izu~xJ0gd80rEybJA*qTX9S`ja{FN)#QzDS|0#rFbb}5APeEHxXg6>-<Pa}L-WX_4a8KlnK@3FhK<tBfhKNNX`a&)69JCF9_67Gv4)HSNO@s~r4?xaDgoRuS`yiezVyTEY=y>ovv<-pAf#Z-vyc~Ixp+mq!kTV%E9=YSO58@Rf)`*w}O#mmMZ5DJIcp7qu*CKBTbQX9Pa+V+xkeh&g5H}U~ln?0MZZMNpLlD0VCVdA%907e5`~ljsLL<Nt$jJ)*0Ng}Gl!z=~(kckzm%yY|5yTmxS-??fdj*;ioDn&%K%>APiHM<R3NY#02;vN2(#i<paOi8`7_{YrhJ(YAlM5OHZYiRLh&*7@8VKUdVAARc;!Myy;1+1h4b243gq+;a7GS@Kjv@+xNgE@GbAn0VM-XR+765ldTRv!ZaCYS6gLVXW5b=qK{9w}e5X3paqzw_o*`WEspP(%-G#fY@a`Hky0S^-~L_|q2X?p~5AuwrM1o7+8lHeg|D-L}f{5o=qLx+HeiWn@S1emlPg18`<^kW2ZB(wy0FxrYiBf*i#DFz)3o-1Ouh-ffrcLZ@!Flko=@te?S@NBew2z?X$CUQQ6&IZpBF-t^qFljdgaS<?S7X+~n+8jI!ZOx!Qun#%SptHaUA{K~f4JPf4AbtZ(+6zHk7}^@V0Bx<Hg~5f9(+au(yjsL65&glWpCO3LgGt9Ch|59ygIA%gAG92}9CG?WSAhc}5=C?ZlMX@<mj;s#KoFOKb^<4&tuwR?xD0YSLleQvMJy8$3nm?iATA3gjYANZg2sZEp{*yh6u1;}dP0|hH;C9MVl<fa3j}d(FzJ^F;&-8=!5h&w2Kp}eUF3{`ZUnCrv0lVTFzF-&aZNDke-OmApd-QS(KZTN3tS61qoC`-+eK^>F#$|E13_FLOgbGwTn{<{ybW#Rq4mJ^kTV{-4ZKp^`;$dXhb{!K3gfnT=ydRO<PfhzUH}>ojz>-au@Jcnu@B;{V&7Xtj5C-?ry+<<FzHkTab4&*@D{XL(7NEd$g!YXz*WS)Yl+Ae#!OlsL7W*(`VN9P5}FHK3vET9k>E(=6oJ+P7Zg!g#Jf-vOpyca1;O7L9K=C`^GQu?N1P8zImGitB#M}T7zJ-Wc)f`B&<~)az*j_E5<&k+D=->Y(MC;I&`wfO#AW!TSHW+GaoaiMgn=n?hjBXvaeWb+X&#7J4c!PPZ3tcst_H0Su8)3*uZjLkg#Ej(5@@3+fgI90;A-I2&<)_t&@IpnVCugn`XFrpE&;9seGgm*yaBq&(--MB=q4~qE5}a%u7R)Nb4?^v0B=TLTcO*)w?zCPVupD5yeV|L&>w|<E8=@P4(NB_>okW%d;`4!ZYZ{^FXBCD1Mqv`Y0xQP(*0n{r|l<0r-CPg_d)lA_hWnFdg1i<j-q~uy720Ozl8n=Oqv3&gKZ~4zW`4H?}es-Q?Nbp=OV_7s12<Nt_^+{S_@1%(Zdt)c_MfZ`k{VzL-&C9AcwfRh-xBgK;Hq^0FQ%y1}5DBu7>T$LM`xE@OJ19@D6NGTt!4>5mljYgR6qaKu3W|w}C5T`;pMm;E~|1&~4yt*q*qei1H#TK`VesM|gM`K92xzK|XCi6gnI{6ucR_1-u2@5|<TGT0}W$88GP(4-dlUA>a+jr|kzq2ZINK*F!geH(*=hk|K(WC<QG6CLQ46{`foqybk%aeLrX%xF2{ebRBpdwk3W`L=h3iphdx?eLdV8pZkK7kx$$Ag7yLT0<VE4gOjl>u}?%{5pP1@0F%agxCcJRf|HO>+jocd1a}9ogeHNLuq|;x5s@MaL0<<K0(XOU0h6u(M`HWV(5~Rl;N{R2;1$@OIKPOzA_|DeC!!OWw4;b+Xs5hSp?>hE;HA)I;APmBIJbygBJx0A1Cw^}aC?020A7N8+P)q16L355V(1d^5^PKSv53|pazL|zbAWR~vx7<7dbkZfw*@akKh*C+=pyhU<Pg6qB8!Nu&{x2utvuWUpId<wkWbrx1Z@fa2)qEA08YTR#L*%?6p;z~GB^`BGc*EB8sp*S_#6YChkmHvxzKswdB`DtNkq7ajL;0=jNoR_rr>7aImoB&qo5yvqrkJFbHH=3Eit{E`kS6Rp#OkLn}q+%?}zhe3gTJFr|lb|pT^)u;CSdP@GNXg{9m!{0}(Hve}P|s4}`Ps3TLJuJ{ivWwEYS6L*5Cr?E?QM{9i>phdu*82k#7L-5AbHL3})%^J)8|=!d+cXxj+BFZ^Fb{0aR7{3m!*IP2<gW(wkC;hay~r=cJ6($KaVd{6jyMLdN*20sO_3TI6WXQm)d4d;B?{xJF>?=adD!B2$$yNEzI>-=zL3gRQsL*OIepTk)1gfUYPKY{)Zek9_yh@TL|b~x+7aApePnb5DmGr<qTSgEgv=<_G=3F=S8*9hYC2;vI};<E_iQwZW?2;w6M;(Z9>-3a2H2;v<G;=Kss{RrYi2;wy83Gg18<5UaiVKC`YFzHD!=@~F-I(Qc}1wovOAU=*DK8+wghakQPO$T3qo`<G`)3I--&Sy~jGZ>$9E>7Y&Pk_^)N5MyNoN0)|sMBH8!l~N<)bar8<<xeMr{;S+=Yn{<i0Gza;kh&XpZ>42{{2V4@fgbgk(R!t`e%9GEpLdv+&|KbZkmyP_YiAfxO|aTgWfh8{{wM}$Xf'

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
