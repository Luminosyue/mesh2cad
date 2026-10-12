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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_005.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_005.stl', 'source_sha256': '149aec5dc2da814e69a8bd83fb2f095f6bea801a8568d56dd9fcd8f04ab2c9a4', 'input_faces': 804, 'input_vertices': 508, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04428192973136902, -0.14797936379909515, -0.12171468138694763], [0.10261829942464828, -0.030387431383132935, 0.05111214891076088]]}
GEOMETRY_BASE85 = 'c$}qt1#}cyw{-=b!Gr72VQ_Z|lExi^J2a34*Dw&gkPvi$0KuUHM1UZ{lAsM_aCZi4WME*hKyZ6?&)z*>^}qhN)?4po)>&tteNUY_SL)tdx0>;7o-$Q-4S!x*g`!)ZS;}jgk_=jQZM6T$Q3Lw=2bLW=e5{9-MR@h+(u-PkXzAO<LmRD)FXrbT*mq<xZ%eUS0o99@wiF8(HgeR+-a~s08|mk-_(r`42l^X)VE^93{SCW#mGad~TPl?(ZJB8KU;d?2ITVbEJfw6^-#wz+_TQ(p_0v+}t#Ji}w=I1bFZ%K{_%HgjOKHo~0SV%lf1>b?@fUV0t!MO!cjI^86@SN*v3n)X`~HaEDMonh#3;nS&>nntTb$C)YFYM+ou?Ie@1t@*?OGNo*ZMR@{P@kn>m`r5@mlTn$R})r@b*ns#A$31+ma?p?rW)4NqC#5jyNd;rQY_lMTFN!q(Xh~t(NO-ISUGJ|I!HgRB9)2v|hQ9PxZ$;<vuy{Nqah?Jdw}(D-y?g-X`_ZU#CO-d|T1Z^~*{e$Eo)bQvaA&V(XPsp}gwV2;{R4eBAPQH-2bg@w1-vL;WV71Ap$r4zYi}DCK&V!@@f*r9}U&eIV`R4Bsid<#=Pn&G;I8;xgn@?gQF4G&tVOJ66sRKTFYu2h6;_wXU>-{mMnRING93l8^n=8yOFJ`7!Wcc@^#Zq;{<2HFh}eJ8TEqd1|*kX5LzRJ;uqxs=_-D4-noKUJ3m=_S|kWZ%rBpf6o)!<bLhCgD*A^{NbGOZv6B^l81fzY>97K)dBH8r$znm50rj%K5FIGKF*=`cr&l3Xe8G=x&=p?c`Yy*{gT2<;@HbHfq&teh_mA89y9OgHbL@n+}VQXYjj=se=jQjj+a4kZhWf?$Ukwhw6o=qH{$$uSp4+f$*8Yy8PvDra`f-+e0$vZG1-`B<=tjpt5iec+af0;-}?o@clv_7ulJF1JuoZcv{?<leTMB4Z-08^6W<;8om))uvA6ubLCQBdFb-eGx$#=pk{I6?c3?b&eb``ru3d3ly#DCE+|Rlw5##9IYvCO?vbwd~zkC{h)H9%Nl+>%(GsLIA{oQWF9sUsdVj}Xnv`((GCfr7x{$phPTh@CBucf$#{I{Rq<JP~;&Ld9G&FJ6N3-+0Lt>Z6f$LF7A{;(}N0e{XLdgc0YZoFp$sjof%EzIjbBEjcai~i2oHrC8rt(7HDZGJN5+nb@duU{1MJRX8^G%y(T`dStJvh4d-H-6F&)YJd4%ma=FBXHm9RZ!1PHMhI*6`IPpvgYZ5^`T!!@CzGBT+7qEXxC3oz{h8l`1T=3<vQE@Jjm0YR^r+YRmC{>$p${l0<o<})5Mv1{r*cC2bQ8ys7Ib3>*fAGj$^($TX~n6*B7tAI1j70-_5@R`o%Ie1M=ULB)oOkTEw{=iuu0QBly?bfpL{>d#st)MpeQ(IBX}{`Rp~^_kk68Tq-Ez(EfU#@U{)HsAqw^$iK#J#5q}Hi^Sd7OYY-16(zhqbg9(W`TKxaGp})ew%p%`dB6J#<o`=)@plB2m40x%m<#^a8?1wShHS^U2tu5WLnMx#bKn6puUEJlBl*SLLHn=sLpy|G{<j_plItALdcZ$#4Dzp62kX)VU*umfKc4^E+ob=TiA~WCMaH52kH?3bdB^<mn6Dy|cA9x@<3Y^(cfRg5^LoSco8`Jc%VC}ESPTC3cjEcT5)&<cqu;C(d+{~2f1^y8f0kbd-|aM>Bfsqu&+^~`_<p1Ixs5~e`nr**=hO!)-S`vBk^k_0(*Dkpr-aw;UIPED3HA+vM}@a=A7Xt|ZJn9dQbuFkuCniU<GbcYJ2xDH>-O(QoZ=g?Ztc0hO8ipqLA)<ZB!A1VL6|?nq7f$`812S!Zn+nZ`cD5M?PLGg0Pz#%Ax>zOgObm}ol$09D_mT7%g7d+%)HZ49dXk3Uv1_cEzTltVr8_$qOro;pN>brd~9Sl^RE4aUO5!k-5!ZNo8Q4WsGf-DZiqkHA-zM!vGwVv^=|ykyyCBQj+gOf{m}_=nvBGAwe25_&&F+#XX#wXzc0pveL*v{L)Vj1Pkl&ltUHBjBfdQp<D^I7{bt@#upH*=ZV5Zgyp~uB^GN*#c#Z~EMScIui1}@56RC&Run^kk>J*9ZY%_kBnb%W~#yb2(ljqejFCXHUnuU40)b|x;UT=PPqu70yVBc3T6Yg8(t>o?a8}qh(yM{R5uAn|YTO=>rr%%#;TD7V2JlZ$a+ULgql}VmA>z6(<P8_qJ3-73YS=!UFxa|Qmub=LRefRbo($4zjzl660{f>Mt#;uXK{x=Xm;XC^6&^6S1%SGYs;ZxDSk%KWFeG(D>er@ER?K#Fv$N}&lZs2*QzvFBO_z7F2K6;n6E6u!h;Ci?Ibw&jupU7}&7yD<gLvr2g!Km-2yck!Z$7DR)Y6KvDn>pyGfm1L~pX!YG(Ni#<{;9WI_!qTNubxlb+l{<_TgUVM%-vu2yddM#p0cov6TNCR%&*zD;eJ&HiNCc=e)t~`b89#21P|nM2l4gT;!-c?lY3GR?O=Y)lY<7XF!Q?ehm0%zrVsX$>HZMjari0rX~{<=zTWPj@Rs2_+}h1vW)tEhf5Ln{ye{@5#ap2Lq87U4<Ki6~5+xs7U<~^G$4`j!<eS@losCm~UzJ1RI|IE?k1cc73V)(H=A$&J@P6~AgYa6P2$^p!l{TPVrZ)kfDID`%9jt5i>K4Q~-c|bDxn(cb)00`@zqWzg*Y;>7*161gFs^&=Lj9+mz<X)MBf{(VRtfJY8!PwGo-Bv|q?+iDCi$`c1<i&3kDPc<$zE-#=+;f)AM3z681hK!;T%~O{v#I1`lNgN;QeJuHsPK1?_!+wPmpy)kN+t1x7OT>_osYmuy4FNS$KVHeT?@TWl{do5B%oVSYHnN<GDNUg*b(t39o%xg8A`Hn$;*DiTQ3ze$4aJKjHp0`bgf|(dW{Rw(1v!x4wRkd9%y|jH?cv!3VX)ekL+V#<}H5GvS?=7vj0y7rspVQeBegTko+^`b8^+^9RTIOERvl*`{HCnBfK1lWzTl*Nc?Kek<%e*7xUK!2etk`_-p!!=!yO`+yJ0w-I>_MLSh2jQRL+7R>*7Dy=f}T92+c&uHC3o?mCvmQoMf`70RzYfeji$KZ;>Ye6s3kF|%QA3q+G`sszfVZYobt&C?!j#k2JoNt}mR!RHYy5$D%%qru_vaXi2w=MjEj3e!Hr1Y0{t&aEoptVa;uLSf<>?IjDmUN-;zr7gGt6x^Uf0Z61yt7s&hvawqFy{N#-G#TE(;R4zIIOGj=@F;ZCK>0J&>Yy$EjS_dcFhl#ch~UV^l=RMusp~=dIiS$`O4rcT)}hr6V@+1$B!kVhxy95u@_i~@p1AR_*@H+Uz&Dk|DWp%uf_cmVQx<sumA0f`PH|d<ZrwGW3gO+uruDrxL(*tz7bxZ-2>}t{!@4^Q~f2pbHRJOpWK}x{b6ag4gUT7v0kT2iTlK8;46>CI$5$E=ArNgi-a##6Z@VV(U`Z=C5OuW1}(xmGX62f&&Qh!MVGINb)DnNvL$vQ`u7axqYG`h54bpA?vwtq+dN~P86dniCkF5R-K%2Ujd(dv_@6przn|(g-h<)>%n^QiCcGc<Idx7r5F&BIPP#o8dVSC7qQ@4H{f2Wp#+&0@#59TXJlz)a__V}~m?HdYzfErA<nd%(;v`0GGPkF-ZvM&Q@Aw>L?sw~%-V=m>a4*W-4*G{2{-QmnM4SEX$zyE7_s<z+9w)Y_>RlzyKLsM)+NW{n_QE&u#JFOA+2>tuBmAcXjt{n5s;F2WRsXNAkBI-~{djLb7bm<HdjfoX>L6*S;Df^Jb9NoUIDC!wr$?{h-?6svj*+Fplx<7&-l4R;T&(c+xqf3L&hO2Iw<KN?UON|#{QnFT-nMnQ@V39JpdVgL6kbcJjQBybB)(OfDZDj4C-OWvf34gvYA5cS6mwYaSIA?7<Q?)2{x{ADuMg-jPx5%E?UeYBUpp{v`bNq1e!0PqEyVhc8YOv+Ya_h%Zb{UuE85>;_lN)J7uZjXo3>HnWD11;tZ#B($KLmN-x+=d{v$F9Z++Wyiuj+tF1)2(g3L3PUZpn4^|nul<9kp1?JtwV%)CCZ8tUbU87B4E_Z9J%-#|Oef4N54j%B%a$$hei;=U8k{x1AxFX6RC<Ak@>D7jwvm5qegpUlC2b$Jb`m(#zK@V3<-q}{B4R+%dKT=7GkZdZiYEMAdfm+z1JrqCq5wxj{(mGKJ@zfU3f&uBYB;#^-OytOFKV{O&aA^*;sao;S3;XgY((9Ao#MPptLye9XxPdX&L<Kk=S7whI!(ZVl0i8#S&C5~lUCqL2Jb?`YaO8;6?{x17#>zyRT_iB#w<eUwqeQb+ABLAXi<oVQB7n>&bh-|wh|5`Yg)@`<>ZhQ%zuXcU4+RST9iesOewrH^2uXtYJEmOPVefe%sfaG7Zu<$y^zuh0_lP=y;DJAx)1D8pCwYMdOx7Fy4IBlm6l6GlTR(R*?B&=V#XUROP_pXk7nup`O@qNMwiI>|4e1s3*)2-d4d{jN~-8y1FnL2K*nRl$fdA>a<<r1lXNDJgY<0al_zviAQ`eAFtx!C~Y@ak!4H+!9S!rQ&-U_7r&kapAFcR~KoewKW+X<KBzcKqar_^hwB?@+9-e*Mr6Inpss*-#%7Z!J9*@3H=Qrc2y>L)i|WFy0z24R_;bmchQU&XgH)pV{M4-wS<Y{k5zcKitQ}TQjf6d0?d=87JE6VC3^UH`ezWCuII{e4L5+f3Ly5;YbGYx3!;(dc7Zw_`^$#l>Xj6A3W=&UB8F*rC%7@r)C)DH@`G<#P65Yh<~*q&XLj$mG#Lw&W<=4CSo5|@RE#k7w`Cx3+IO+|I8MC-X@H<LMyN@KlXl-nRhhv!8zKvx4PutX&?N9y|IrOR7KWN7jG@TAM166&9aYo{BZ(t4&Xh}5!*_}iSBiV<7Y0;wWr*fAaN(22cOf5evI>#c}cH)4dbUwGTws%uTD4fwt{=HpWhgQ{U~`y*LdtxOAe9zo%3%Z{<xud&#e_5A?>*SA@aB3{mYr9s_^#jkI~N75jgir_Z;V-o=LcG+i|$>rT(%%u?$JZeXWIYE}Bo1{9U~MBb8ilkNGI;qvON}#P<%tIsc6_cyBKJ1@U<f<~;wQjG5P5=bTNWaK5g8$2e)30pA;zWu5KD&ntoR)f|!8eN4P#;&!|*JECR3Wv!NakHoKd9p}z5lP1dbp+5<4@7oaPhb25^-)U`@S$NC*{`el_Xfju>kIX8(zIrF--yP2-p3Nht@U|3FrJZdpr>r&e);@9g?sfEVF&`7Juk*xyh~F`_9(j=G+!}a4OgC$t_-D5W@0>mh^W@?|(*BOqMZvEqjP^W;`dW&WM4ancq#d<G%kZ6XY8m9C)yMl}aJY;I7q9;nBlXfpdtkhKS4KPB+lKGH^=4z9B(Lpzf%T>0ajXkVsv!>77rW0xnfL5T-oiVw<NJ>N@idtyUA%SjE9^&iJ)dFrx2CUxdEmKowV8K)f3f~ZwcCx~dKT|>1@|Fd%R0z2sXz8@VQDbWMb||>mJB$@DK<!+cS~Sf@bhZne53En?oz*V9gxr0Ww<`mLfMyFN_GLCgTGJsW00)-&fxCgcYMe9sfj7AV%P4A_?LTPeed*knfNaYfPYXoyg&NnStWMz0Q7I++&DMrhxy;dYy94-hhZP9`3^xlWW{^Ew&^zBZ#EA{{1<gFe<r+>ezc_>1%75#;q@P1WIv<z9Rq&nEu2qgOdDb5EjN1OoXx)*=7+qKaNmFsyzfl^D(&O=Z3^n!awys-vHdu?&&BD;f93>yk1WpiFEbPM9iIa2Gi1^tiTmhxJg0e|;eEMUj9v05umy3l_Q3hlstXIvymjy;%o}MEXGtDG+u_gOOIZ1yrC-^J{3r6<>C;eIPc7x+@LXrKV}7_WZoQe;I^esKeP+uUlHZy{)OXK0e7E{#6V7ozALo7B;d|)vjW{pMcnSWSR%4$qv>fuc+(v!(2H`o~xk2)AjK7EWe{~b{{H<Ez@2vP3{#+L<d5T~^(C{_d;Xx9fXUBS3PwkyQBhK9GI5%h&Epc4DR?ipfOT|NBZhW~$_<hW`7#W{h7LPc|>%(rGALVb4JO`x`UVDT09qm{XeE&S27XIFm*yq=^V;@l^hw!$yVVK{%>aXxI@%p#ITg}h4vq?e3e^ng$2UujB{L6nh=Jvc>Hxv@y>6r=dFO?_C__4*6hQI5(B<FK2TY22K3%*0S=0isjZ{e+<BJf;XogmMVi`U96!FQ~D)7H50&0k}muxfO$nb+Iz#k%`z3H*NJjurgpcUVWq%tw8zH$a@F9dNGB^-*8kSa?gG?mXY@CG&}kclPdp{n(`7m14hY2LB(O@xJCc0^do=JKnX!{<F>qJjZ*xu|3D&JaeRu@jHDm@*GhY>&3yWc<-(m2tFbS=S2G!V_(o}BJ%kfF3+{?)jOO=rkRfT!SgZygxliX_&XP5-(b1j4E4_aJMzr32<Ls<PRhB4^T8V2m){*Mf8WA)>^kef_w9^!<o?#hYcE&g9DYb`TzB~>`nN_u>`Mo|#J;8Maqz=Bg5Qkq#n#nV5T{i})Hl%!{r1aqj)!+{>y+c_8}JX$xUI{2h4;wwzyzF=@OMPczrTX#dgmGs_AhDTCC-)m?)!(G8HLx=<iz>#(KnN%Jd>yJ*0mA%uC}a$?1yawvm?%oR`@Q+@5|b;T!`aY5YNT?F}vLO3E$9O=L_$2<M(=_zte_dU*wg~Jx*JE*K_gOu&n6UGLdMX8(#45_!Q&HwVx!f6>lQEwkikCtrrxBfBM62{r)fi@)^zzJ3ht!=buuD!*Svox7Nnx;GeoL^5=fo#cL@mi|w>u+U4f&kMGOYNs&0WTUXJo9bEqZ@;txQ3opX=h3{3|+QDuM*lp(Zxb$wkwx^cx_CrfC-+JpfA3M<q{`u$P`{MDnl8>!$GsI7Bvf2DR{>%T>1ML&kMEos!OT^in4ex2>9k+aiw;bq?`+lCb*UW1p-pF%e%YA)|nb&i@k@H8}gNYdD)!M^<@pbXn=GDXZh0sp$-?Jaj`}Eyg-1zKAagMov0QxbaH~1q#I8Q%Z7vE_;{J|e;>h?U^vJZ31(|WDuRx_`k2*EjL&v2ag4<Cu=<>pSjM>Jm{`zu?qv550)FP#6E?uXwMOq&3HR~zA--n+KD@s{%N&wU>A?UEUYUurbILyfu<Vdm|{8y`S@F5x|(<vhgkEhYN~r*AF%ZX|jE_y+}qx3>O<eV=V9_yTKj4tV4^p09Hoz#sb==l=nT;Da}Vcl{3b(Vd~vF3IuWwUhXcmEeu>dGI9oK~dP>)JuW&J?~l6E2a(Rsi9{E$aORSL_0^M!tb8CgyMNw`H17K556xhpN{?DhbQ3q-NADHD%!2>Kj3?$$GP#nR`5^v20Xt5y6US1yaV593!b|(4UqrgkH|k@8P0h*-)aTEy4A}vsWs|#B}D?_k3c&_h6=BhPb0jRJuC95*><-ZU-S-s*RbFN=DjBw5GVKtzH@}d;rC|svLv|W$=?lHKIatPIiNkpK~Mh;W?o-61JA|B+;|U&EdV}ZH@<tfD1d(GUl@GzB-ATM9kg3wG4OlNyY-`s*M3Ti?|B!p<98jFQt&^N5x)x<h40Ju@nwa#^(%rr%Lnc?^ID@txbNmQd))Z`LHIt`d_LN<QWfw4O_9%X{C>~!tS0W8oB_Y%;O{yd4Sm2T-NEk&xQ}vnZVKM@{m3<bGW!Z|pF9ueu}hCcn0d>@o_ODXbsXRA2em^!?aQH^7uhjyEbNE)g)k2|&qU&Re=#t@?Rj5S2J@=+8~F9H@|@bQ{fc%za8r2e;T0H{og(nNl2J~?zxW&G&Dfea=LmTwyd$d@#z%wA_-<Aw3GsjZiup0ue(X=i)!8d?-sHpYBnCFz?#8>mPt~f2_5E61;kC~L@cxn^8^(WyhQd4MbjN)7aLBGhzHa}zAaCTCFXf9GBj1ppwd`6zZ___5P^3H-)c^l~S}>sU|LC6<R4-ro|N2i04jVZfRNX<X?DG_buTc~}ZOA$Lsq#~X#FL9B@4_o-#}daAE1gJ*XAB3+6qjJg7IIt2D;#V{D7i@5TPUIQi=?e$44{wV?6h52>D`n_`iHYjajS?GH;-6xorx7!pSHr2Xe*psjVaoNXxFD$c}*eO>bjDKq$Bq$?Ly?z5T{`rg)7j{g$prGGulHb3Xh^xpwD3Xsd7I<nvzqxEpc1=D4d^Ve#H3<$zg~OaeiW@`%v=JU-^|a<QMvuHF3%=XGmSz<*4h@U+LC{RHs&UCsSE<+6p(I)McCo)NSa~fVeg7#uSBpsrwT5rQOD42T=DT?nk==r7!(mWkIIA)qP4aZ^d~VQjxeK%M`9cTb0+Q?M<!h@{~&K``W~c%SK$AI16nhCFx&@yt02LcKIqhC9%@!=$D09m1kg?(y57+c+e*$c@OFo#3hJR6DwVrIs<V{mMPqXc4dn4DMn6}wV>{1NH5}E<XaG{=iJI`S`aJUnR)=R@*SvQ?&!ss16i)@U`j9gsIqYy=CXnGA7?6CNqedxYlyqhc9pH+bzNvTGNc`CrESDrh^JDwBUZYWAw#I!F@~#bh^ee4`60aT5OQHA+l7@rNIlVzb;K=cyUNy)Ye;?~aZh5UC(v&q@dWZ+DXk1?POg=St4+Q+u{Ze|w0jaOE{}$BS%de_LtKM=Hu5!0*JWcI<(r*;rHS(p=izl;wCfOOr(K$DTZg(d+oL6MLsMBJUgt%w3~hxo5G$@2ZC7~)=C+c3quRcRhVg7AE<rmp?cBt9O?DCb=cT{0GttgWoQk&6DTwnDmmshFG;*nkJ*d+Vr_lcMmzliAYh89`=9P}uC{E4OYAq;8taM=w^Qp3{Qp%ApNdI~!yBc*p;(GM)G1=V>=}6q3c0Cj4L%uz+TF2BJq2>a+hG$&$huUN8Fl2)v`wdx0?BaHj-$i?&$-Y8S_zyz{8M4HXDb$OI4-qSFGqK|K7_x%g0b<3aHRLA^>-JByGZJSc-<DXd>rLt7;<A!&MqGiCOT*fcmAC@2C+%FsIf*SA)*}n;oV-4l_Mi1jl~tiGPF#h!B6U&XqO=Q8TZoHNm!h`tUInO2QU5~hisj-xS@sKY4vND0De2ixp2YdtR_WOWX^CB&C;9X&Q`g=!<cNm;zeMcflzog?>FxAW_73VO;@PyflRHALH*JMy5Gzint?*1@#l_H8cpI_eB6yz})KSD&nD2h(sB*qQxoXH!a#zV6B|go#M~S!5R(LP%(-h@@Tf_UsY2w@DZ&5BWkE_Irn{3E$8lKbNXpbdUy1l8)^;|2yBSqov)FX+z6OS>Z2krip?&Ot>HYCuHVZ>v2-7w-|w1*Qb9Zg?lZ=wt%A5EW)6oq#hGR=^=#KUR3cvW9N@{`F;r}i`1>iWUNew4{<o4Mpw`B0OudS4h%ZajHcxw7XQ5<=|q4I%F;TTD@S8D)+ktI5qVaSO;VpdDhe*HSMxVO2hf+ydgYw8JS1uc9bCkFuQplNd+kKZ|{%`eZ9@g?}ejTpVpzxxynT3j0$pC0<H9&SVdwD7=KC@IJ~?`X6GM;sSZU5zKKGxv}g=)&C=D4`=&dWM9oCKBHmW%q2cSTjApx#@`9*jl>)2bAoLVP2ZEWkFzZ{kvmIU;mgE|yUu!Crj8?yqt9j5cOQLk&{o)~;XL3z^(kVd&k^4zen@?u_#yFM6onsC6#ko{=AEbHu9>*o<dwcf{FL|!^-ba@#E+=25I-V*K>Y{t1LAws2Z-+x-=*F|e3$qRMd3f$R!VQC-a~wdWeVRkHd^-#xlU2|Hbvowl)nvmPVR4V|4=J_mmx8R?4~FjMNxPuMd9g`a6=lA3n$lzxGD7-;-<tcDGIMPq$6#GJJD8Hr>*d8+6qV0wi^;b98G&ReRi-8+o^Z3ei8KDPQ8P87jZP}vda`RhB%zq&fLR!uhqnge`d%dLtaxqC06<c@oVBY6oubXClSXQ5@*Olio#nB*+g66ImC+dp{;N&+6vd8t#Byqc#6W?C^hJFgnp|0s38Z*DZQUq=~cw5=zoMcCoor~4->}`A7$J)`fnwUryWP11m5o`uS+1_#B1W2^CsdOhTJ#gt|51bU7WK2B3AkY{gi!`qVRFbefpfB{~7AX#7dtgK27@=<$)m%at}=09r6z10~CcXQ0_42zj)1Kau3MeV)<RRO#-<;X)An<KDSsNOT3w7x5#Za@sTXMMy#HXE3{qnfWq4;*XW~Ust2C8NMhHssIX2^xD!R;&J=}PQ-VD(UZ)bfxT(xBm|Eq&kha2eh!^tuU~*HLle$LDU0YZWrOy$cV?B3MEBh=(;SCgp*HRQ-K)r={0r4#Ajl{Ev)%~Z_cFmu&$ZzB|3SVYFs{Xu4Tj50F<<yDvbJ;r$*-Lzp_GNNQ=&yX$Gkb{KD%wlPB@&0S%yr!%`W>XL@O(plH)JBUvR4o*y~tFyh;q`9JuE*-PT`fbl|Ds$lK3U@OJ1w=D?>gIpQ7!goow=R(pLCA<t49G*SsTE`U~-U>W|cl|3q<dpBeWf`On13y#6Dv`^@rpyx$Xw!uzOC5$_{jOi}GQiET2U+$q|NSvH?-JfFO3%X)@%Go-yCg@_ebf!M_<JBV26Fyel^wjXW9ucNK-0Aj`cL0jSe#EQE_`wzxaxC_hso46k2d(b{l>CYJJS*Ez|#EM%+Tj808)F)S;ysKQ<WvMF>SE4=BWLv0<5*MXCf>Me8ZCIwb!o-TJNn7EJ#ER=mTj89<U3pz$+F594G~HWq6<G(BV-w<vruJ$=-JQ4}+gG)1UPDT<uS>G83sEb(H>D)==}MfJd3GfZ;x)>*sv)HfX-KW?GQ@evHzf9@DBO-Z6S2~niQ5r3qs~CA^iRY}dl*v9WLG1X&5$A{y9o6c4P_q<{WJX(_mR93#aB0^747QOtr+JWuT|Hiq`!+xNq?o);ieaLO8S%{_A>dEB3613wHL7xKSL%PGK}_QYA==z<MoRBjd&RGF#7v5f5lCp{TsRJCjK{*zp|%MCXk;-9b(9E+Ai!*yBgbRIQyj<aS{3`Jcc@ixEby7v_puS(e~w-P~14$<H<EM@k-C5jAxvA)RQT5$<5_83eTYJDxbkJrAHG_A)Y}zgZ^V_yReP+5c*FcH^juNXQUzdswUqd<cpD4<;|(b5*IUFr*IjH!oN~yC(cg0xykmVPD`AYc5{=RnxgP$4LSvJ3i2f=3RkA2Wt<YU2U9C<l*t}NY0i2LrahT@Eb&0b8caNxd|&bdi3gI;XGlSEJ!$tPSHi^irGGE_^d#;{K0kTIdC^wbk9sn(7j0GkUBfkA#4heDd8L(|WXK!hx3s^TI5l6qrB=3zmu%=C^!>q@E}VjOQ(D={EdRm#<|AK_?VxZ8Q(q=)|GA%<qegQKj-&P^R?n}RFVr*K){qv41bSfIX-iy}*u~YQUlU@*52X$?+3l%25Vt3;M^U)E2iB^3#O2A?rYPKpqGF9CH<a8+Vs&4&Uglw5N|z=s%{&!W&r}_9b;!HQ>#$xeh^-!YzUuHgD{(oB!Ud>v5$B@qNvXpasadADbi}FIU+IW*kWWXfbZ$ew(Z}Vh>{KjIMV~5${6g$aJ2$x;!~x{JS(gUnTF?$)JGLNhK>q;V=Yw(IPa5w3fjN94eog&~_%-o!>X(K*qgM8N>JP*&zh@@De++p+okabTIEmLKlY37tnfNpH2j=^pTJf%aQtgt7V?~Xf%(Tl=GLg5iOmSI=6_<usap?`o>VbMIU7T&>vOlryinA@1ZcLntSoM)_bB`3+Q~r1VE8GA4sdsG6?SE|h|6b|-Gd1&-J&joZ{%Fm&d20Edo5J`{9Ymj0Ur@CF0$oPjuK'

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
