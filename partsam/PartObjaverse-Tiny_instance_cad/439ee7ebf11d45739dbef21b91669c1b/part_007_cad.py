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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_007.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_007.stl', 'source_sha256': '18587153e473543197ca23ea9e56abaca7fda480ba49e43a827d16f1f3f8bdd4', 'input_faces': 1100, 'input_vertices': 601, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0258977971971035, -0.4999997615814209, -0.259498655796051], [0.2478426694869995, -0.03213054686784744, 0.2350839078426361]]}
GEOMETRY_BASE85 = 'c$}r31#}fx`0eN7?yds_65QPehe9B@!woJ)gG(8_6e*VCFi-*n4H}%mf<thJ!L^hYDcZiAZ|`Yuc>lN7TkmzPZ|&dR9L}6MHfPQmR)gxtjh9Ztf4Q_0=Q`}UR!-AYB-7GqL%I$e)U$KfkRpBi5BF%P#8>~hI;Uatz@XM1ZHP9~zf0GU&IA1`=>C<umGdv8`*-U%aL~Zuz8(7w?9x^FwS&J8=^EpQ^a$?XHRg9fnPSBY=_T_Q(nst6kN+i!DT4iG!osRCY8ufO4#cRDxah6}zW%mX=hbgB*S7ug=j}F%uMM`Zsoze@#mALu6>p1g>_~D0zZV{nzjr`eB>5~XDET|%${mpWU4LA{i|V(x?q#{I5g7>o*L&9`pTLwSeSKreSn;iyb5F!de=ZNw-^wPw_RA=w-#tjmV=l~nRMKyKAiiDg-7U$d)%HmF^I0tyOFsPqrJPp7>*Cw4U!oW4A+py#$$!&u@r?oVZ_9m|+ok+w*PTnGe*AlgZ<l<%P0|N9Tq^0;rMM&aJ2eij>x3*teP)*O=m(zcmA~iu^JYo;t%3;;i=SW@{I~t3-pri$cKiBv(oiYCUO2Zc_j@bxGVy=fEct6qH%dF2^o@~;Z%Y2PR!RQOf}EDz@68)>T|Ho`)SEf47yM&ICB1i8se_XL?2Y0Zoz6@B7@be<@b%3-e??0^<#Wh=S&t&%H`#d;_y33F<19HSz8$t&?n`UkagXRy_}a_ka$nk{UUFZ0mn*pL)L(Dox`VfhZppS>^0`t+>e<{fVY^(nXJzrV&}ovtes!j_i|zW}5>kG9>sl#~_g-!I3DZeAjb6Q@M5_fM|Jg^cO1}SWIwe}JInsCNF8Ldy4arAK*hhThZtqKyZgVlT?}-88o6Qd3ej^)6IUV}O@enDGGv>DBqu-r{{A>8jxHDUpJ}uXwZ%n-*zLp~OnOOdJ<B)z>n55T!TZ{5POoHp4JuLO<?GOpSbpdI2qiP?FyDsrp_@+0U;!@9E`r5wr(!N^S#JJz*Da1FT<IDXzcN<7M8Vf7H5A#R66v!pM^Z5(>6JI2~`Ss3DQNMV<%5@Jem-KqG5#n1X(}}OO$S>*j5v_Lk`eyhowBwj=hvd5BT8VE2mB2V%`tCq1zguVY|K}NHzS27-TPgYc9f|T6{ET_vpdr3-VIt<qj%~Kc{T_mE*RLV<V9l*1^{FLoB)+yQ_!7o@w3Jh)Z}&)v`S9gtDX00V1M<(F7vuEENb$9kV^E$r0qBQia~zZW>V_fx`ovN{&eq!zl78o2q(6The((2kUAx^SlxOY=xvqIIT*kXr_CC_D43qTQnX7VN-s4%r#OHkIotW`3G(db~R94Kl*E>po^Y%R?zCC^w+A(^XTvuzRt&;1OZYJ$wjefA**Ees>K>x|IOXe}%n`jN{v*=y9-$tb{PIqq+-}K~0yWDsr_v_F%-Yk}UoZ_aGQ!jWxd~I2J8K+L_>rzgA%1NZZm=*KVQf;fRZyh{(R?1&vinO~o^ft=Vp|M<7tGj!%{5gGX|2@gaTXv0H*S!4#`L}v2_p2RyE9ouzPT$+-#6Q0p^YE@ek$?ITQckT&bGg1n-#k+W<2q-ebH2Vk;F_e@qa!7~k+6KYq_5f!?f87mdhs*Whkwt)yk{lcB-f>H7tMfr2)if!%?bTpeC@bL>fbt+L+aU1lXk86f9#QZF#bA#{+|}Unc_RSU+=*ZGLEcFuf(^Lq{lq-Y1;<LpT1MOr`(T|G9j)T`~~?8dMEkYr;2R#^^FZ9(SJ^lll;Al+pd%RS0=(Z$~;}3Q{E0<@wJ>0XqV8)jlRB<e~I)1Ep9=XfAj-$#Ww~<;`ufG70TaYA@aXI8tWYY%2HlE#Is(?Ibba6Cv7)rU*}j-@wGaIFH1h%bE03Zj@TgSyLZ5I(>WRC>)St76W@vBNcr{9-{2puj(IrsbeV^pm7m4eD(jM7KVMeTJL3y%l=26+#JZyMLfqGg9`IKU#B($Eo(;af_kx3dll&g$e{B)c2VBJbJoi23+ZkuYH<P!Q`BQ6GT+%zQt|EQMv3QQ3u8ekh-e;5e2kK!xvu~}mubz3n_-5857}x6u%J|YVJ`msDR9xm0W6^MFA8Ts%2=RC1LBDDgFWlF6u5Xj)nRit@jH5pL#5dcwm;7~eE!JI4f;UUO%@~h)soEDA7rN_ruZVej!WJpN6Wv*S<K<nc2V=*=RT!`E?bP$G$aPb9L;t<n3x0S6=7&dzrN3#{;A<h{Fu!%Wg!Qm9Kzy@ZCn=|9rCcl5r?2@%%DA@2)QtA^&4Fz&KjhY9`F4gcQXcKBgYul5g7W_z2jetu3CUkO1z*qC1O0ehdMS@qa6j^?m{t0%y}WybuWufHj``tb2lUTZC*kK0m2qLWXe9X=?e8O>BJ1V8Y`<t37v4=Dkv`o(tRG%ylXf)eJ83pbKlG+4jOS76FDSp$T*~7FMo0MicD1ZnhbP^Fb!q*aTO|F+3#iXNjih~T`r4!~Qg6nvHmJ8Le()bRN5ATo8{_d#E%D81<K?>M(pz#}tK%c&|M3W(n>!+;{5E}Wp-LD>YaU=dTrha6l=E^w<ewoZOq9O9H#^pChwk7#s8rr<a@}=*N%_rX`DL7H)BVNQ%=DQ5qdH3Y?TpDH|EF<k_Dd1z+y6E8f6Mhb?sSej*LUX)gY$-YELG(H)Q+zI?L6Qenm*FE{96BvQht-ZI}d1_2aIzW#n=A%2lv}iUl+>{y^Z-{(h8|(Fa7^*o*9@K<vcnC>%IALSIVE$*Y`Y?b-8I)mvUNe`c7e3KXh-p&eu0P=f(Ow|CBYpzEN&Ao?kO2t&Wwxz&*^X{c1^i+x72Q7)N8%Ma1&`hN3?|`?@KXZ&pHon^h>b|LQ#EleYdFe0?o-DZCe0)1qSeUq51=*_kD_Kjs9UgDIkp`uawZVDZfqm1Ft#tjyvYd$PsyosoW6e^eiP#Mie@_Q85-?d-$8zJ4OE`1<QgSjYNjL3th|#B+0ZU1=|!zWHz@+WmT8sb|CWzj<!D{<qIf*Z=nU_;31eo~N#Fq?v;G;oVQsvC_XPB)+$G_gKD`>m26)rDbFL*?Ng@n{TC_yly_<Jl9<R+xhd~^qtdTy-^SC<N8L4x0wIq&x+-n$Iqku)*`HbQzzQ(J0896e9|k4`1Y9C^NG3ZJbcbq2Inh_zOx7OmCpIfni#l8?)TgIkiP!SeCSR1oA?IjRfF@Y(>BFkx$Yy(!-hK#uS+AoJD=O%V?OuNw<pG)&&^9^#Mk(|u=%`jeUr}%FP|4q>GH^*&m)b`BdrX4i_as2&m*gRZCsc0p~d;o@%G&NKeeN|dl1s|d1~@`>iX{URO9p1?7js4-6HawHt&TVm%sm~g>t?*xd!D9JfVJjvxLLv^IhZf-K6j2js1ML%IrY;L2a@AE_hDz*AMMNIp18yJXm^y<gaJ2Q68>O>}6P=81%ngpSb?F>yv+du1}mZT%W8vitBQ{WIyD3X+8acvDZs>-m@q_*JB#jV-9_j>oJ4tF@4T?<TD-XJ%j5#!}YtxUhf%k-s8TOM#{XS4}OSxuAOwBTzCI4xqoMFx|4Ff^nT)N0of(JeX#3sU*F7pNyd-u%_;eq!@I%%=DBSD)eHIW%8KVi(&Uof_09D2P%q{_@s06)aorV3B!8py9;9!$QG7e{z1*iYx4x9qXq|q)<iqu|&h@kFTU<XI?)rH^aq+btjeeDU>i>iLN?S>MyU7GRU)R@y-`jxC`Az5iX5VOu>wdG|&{B04-{^E`h2*n+8Oq;y2>fr>3EI&`@F%uK{fv2wdiXOOepG3!FO$|}z3s<!zgeG{2M^)C-Z)a9=C+Y&$JK|C57!l5t}C>Zm*8`K<>mUySo1f0zE4@X@IK}GI^U;szE7E9DGo?_uCH{iuZ&S;#CM-ln){rZP+9!{?K$<it@!S9&~TrFO*<expMy4^gSH-y^h2jFm-1hEBkg50jKp<Aii)orb5WnK4<erltEF9xvK1t~7L?u=<@>D0_gN=b2Jwx}U$8ztkX`E2^)>CYtYfV372;b1Gm7uNFPnT{)*JbWZ-?KO-*#v}DUZ{&1k&@p+jif(Ym~xu`JS%xJ>6+j4cF!SzQ*@`*SGk-Z^yy=zPC*q<j;Kullu%NeRrS1<UWJFrya`4eGKa(_Ay-F;y#AWeGIel6y$Su9meT}LZ_vFY@Ca7a{ol*{)s`~-9It7f1<awkWa4=OYW!F63k0KZbW%z?-1YE@d?k1%lnW&_ien~x3Ll&Li%OV((XpaY8b!kqmV!Mh3sYA7oz{|zL2@=B+AMCCG#2fm-N6}@VQUr<iI}Fzy3G-RIcytcR7u*-=zoNf!{8Zl-roQOZtyK628TKGdmjlW(IwY`)qa;_SwA2@8i1MuXF0`j^*3?uwQ3zzs`t$jC$aHptA(~fv)f6exSkqK&#j@T$lTbHun{s!!MB!_a`mxPijZ#bAQry_b0>NAfIPhus>L}Jm#gy^arJ!-2c?L|7kAlA-?7pF757ZzD@drm2?{XxNp!O%485<D?A_hl)}EN*WGue@9w+WnYr(p{#W=BgQOqmgKRuUuC9U4eO;aVx^}^}xNfTCGH+<}+F{;Uat8i|Epq>Quj**W1kv!hZ|q#dzOijy5Z~ZFv%!64tB-^0a$nj$&3)<RPvLWa+v5JV7XCZ(;eNQu{cxw$C-~ey*SUXgRq`AX|J(ici1^~W`}R8b?Oos9x3{@(uUAhjzRCT6ll%V$eU0Y@P6wP9SZ%Z8y3bC?cy#``hUeFf>hO6UVe&k}aeba&Snl~nsX+LL@8NyBUL@+-Xol<Ze8d@!^AXoKcs^qBd_=3y^leMyxolU%b0Mk)?w98;PE(w}*kgyoztT?D3C8z7NxM4%Q;<K;cMP8I*n{AkpBJNFtu2LqwKEjg<vEeXb0X*IFG%m6Pw~9T_1*I(I}Og8tTy3D@3#%>mYj+4Jj$~U<>Yym&hsoQa$~IgoijN9G6qDz?;Ixm#%oT(_!_?r*X8+|lN{%3uJ4|&d3nC}Z+f278SXiqwh!rf-e>Q?dEdW2&--lmyf0%E%ENO;FV7kE8pn`7&n0!9OWGsg8x<^B&+B6rNIiHnokV(`d)ilU?&<n=N1S_FJoj|Yo@e{w{M6w2snO{H^5=Q0=AO4EeTMWrx3yZ~-1cApMeK81bID8O!}DUN6V8iW-#st3%i+A(+zj7N*iP1;_TV8{CmdvYo+EpCj;v??i1gV@$a{iysWR%J`QJ#-^J|0W*ZQ8ghoye1ypi`TqiTOiZ|6=WzFj}l2K3Ji;%n(si*N9JT;ut;_D?4G;q&CV@AN*1=kkkk$e-uzrhCp#-#wSNn&4bs?_WuLv%)%A#~8i4VLoqC9qHfT++XLpzw4Vk_t$vtZ#Jlf^!|KLNwNjwddzny55G6C_v3qme|>&$;N|xQM%y6V7r$H3_}zlGtud|}5P<j3B+oEjvUEm1{Qkk@_YY>r5R_+Ch}5(0`HJ_@V`Gs2_yy><zm&s!)6psL`F(}yeqUkEfbTvp_??F9yWeRT?spm!7vsA8-owl9J**z#C?~%UG5CFmS#uNe=l3U01AKq-ug~vKOn!gj`tJ89&P{xO;<VWXpWnA={JzEY4So+}@_QJq**^IEe#WkV?`NE%hf)4P_}<3m_cq3*<4Di%b~Jvs<NEG*J37DH(Ko+4BJDH&SDa60X%Z#ls8*_@l0N^>c&;4TAii-VkN8HVnK;)kc1C{N{c0io*;A5_J>!(5x8iy6=bdjMpI3gzq<!}d5Z^m_C&pWwno+*KcHbZGpM5VNpB{6>cP90d=aZePsQlJ<9Kdyl4wLlu{CddW{{iy3Fc0U56;|PT&ywOkN*K})?6dpu`-gnE{`jugAL-Eq{h(|)@$CuqagLaO59W(6<;B-Z1>k(**kq|k<9=)Lz4d3}T)cARVP9W6J`>mdP)f>aPai41S!og0_dRS$ukV=x|9nH_|Ht3RpS~8ASLSysX9CP?=2YCr%rV%{3dk?{IDc$pJ49h0wo+cn$J+qyqxE=-^~z`m*G+Q<`80hm<6kQ}5chxb4(ex2TkOZ>9E9sujDz}4zZ~n=%C96J>up-`wU9e_FMUx*)>}@Jthn!IwWS`6*3VF1zvK|#$dv=@yipCMoOY=o_}&wkce-~KUys*Qe5+78tlOS%m;9|0y~KA`{D5<XuSYOW3NJ-IR-jzhyZZzB&-DZ1o9(tqdh1IG)K7t<$Y)a<$=@C_59|Jx7ja*EPvczw_#oVGzL&VKGD{_Y^I<=Xqw-lWpY@z6`4~guW1Sk53+tl<?~u=*FHry81H`v7bwWR1(p!A*>MnS0bgGJRQLLks-x@OdxNkq#mt04AGX043$*0S8^-hVU{JJ?8`JY~W*tef(-L@g0k3UQPR+}prF9EmVA3KD44jzhphTlg%J<p<lHnmXB<}Yx+e!rmn7w<|x(JLm!{Jk#%=Ua~>rJl{G6!5EGLiqy{$$PQ&xDeiJi$|be{XO%Pq+4GE>*BX1aos8DFuuN)#B;1$9OTo!mE@y!HIV-HDfEYnfhgze8pwZqf3!<{uk3d?AKP%>=qt*}dBzAEh4n?%cDU}=sfT@iEj$v>*JGJ6PUlZUd0LFbeqyQkQhulX4D6>iHc_6E<<agH<{|&=O=Lc__l`jMwFRi3N~_S0adM#kr!K~IgVSK1=~xuw@y|8zJFS#_%-eG@5A@%Q{O1?L_)7g*^7k%1iE`GygY&RIW=i?BSvOD*lapaSd@>&Cv)zHeXbs-~+ecu0t-gon{N4^2N44vpk@O`W;kvyOVH_<iEcI+H`~%m`QWyQO!xAaKck>6-&p#)zj!&2j<NYc2lZ;|HWPY=_9y5>R!#a-hgH~_==7B~9uwHxL34XiYQXcJQVffE);5pU32l`v}3RuT&xQhLq>>tox^v$7_r2Nk5c-TjHSQGnLgEpd`SM@>u{p-Rv%N+5oXU7i2`^R~VQ?2$c)X$O@@Naa$JUMYB_TB0Z!+kXhLq1n_VPD`9_9?B*|6txIa2NAQ$1%KaHGBtlbt3k2A|}A!nL*YE=5HG2g^EAoej9V0dLR34-e~O4nXf)!-}82el;3W<3iZ$DnjNuC%5OXgM>*%tmGV0W3vxeh1M~SE>x5M|CB3t35B$W#kiN`a%r6BGpj|dK!g!e#i2M^CNBWO9(BJxh6yKz8jlCoHWsUb@{+)da{-hDu_YCPO?P#<*13%GC+}9O<>^t<k1pmc2JU6*sH7DN0dvmq2=!c8iqrK|iMm;1sh;`w;*{C=F$0+C1br?r~=9PLgHl;#83iF_zFPz6Xx|IXvDp4KtWQB}pr5xvqh_7EdkM+jAxELp)#o(u&hwC1HgnZYPg}-g5w7Zt83&!V{O5$4!e#Up$Wl_(@p(^6r8AhSsE;@yJ{?QQMyKxM@pZ<LZp35&oFz-Hpjr9i49kga9uDiXtq}R_>k^H@x$048UcX7W}@1TBbWB&H8pMmd1MmNU%c3}?cVO9dvbH1!n9(!IW{2|NGj@B5oOL+^|J#iD?RTN7o^=79J7hgLXg?aeLy|~YtYf(=(KV$s9JC6CN+eXyS#^YEwFRzPwo_reR4DN<{uJ${|OVvBL?tl*{fBw$Mf93<^bM%SSgOw#~l&|k(EsyIa(J|h#Jz>3lC-tcnypQ?r!|(79HN<!sFctlczLVxhv`fZK7}u9LKh5}n>y`^e|9_H?^LiQFmk|g3IHUmPq58jLysY~f?Rcap`sv3<=>JP@;eK{h#r|~e2=tR;(I`*#8ki4Gf5!R5PXjR?9tI+xsJ_UjU}fA_>82>pk_G5L-1oCSH51>=ng{nga1(x~Zijvm??<dR3It((ywV=?v{?}Q5lu^@e*|>qdSMCPyEtC#-@3pr?I-VPcBf?MpLNF~{|r@7{+7$Jj=4Ai>F3@?`%XQB^+CpksJFnhQhqb>7mRcIR)VCGzutBk)|0mv!C&Qt-{m9Lf#=pCpQSx<{@vJ5>Qhg55cl2aBlc_D=i10KsQ=#zV1KIY0F*!bHPq*bujrp|Fb=he5792O|HAiVR|=s1Q$0m_-W|odqT)bY_sTQW!=&P9my>udS}$KCeVemrm$f{vnZf5+wo|CL^u^%c)g(Xbk00?qoM*7~L+{w6=r30%W1LnF!2O&ni|0VgVB`~+2lYR<Jm#UlcElR*&cQky2X*m%PnkfjOX}fyTYnMS<#~Jb^FXXStojd;|6M+Bt~JDSW6T1XZ@r;7x3%ayd+y`?ynkc7XLfD^|H*jtpOvHWUNoXL{J*h2(Y7o{zc<>VoS_qOKDYA;-cLS!kL&gwjCERXoY$BOha#VgnCJEII+$mtPsV-K$d2`4yRT^PqO);di)-Qe7^LBOLErnVDe8^$j8S_5=Fz7~@V>@*Mw_=3`EM?O=jj~Gvv#8hlxM<PwByIGnE$WdfS+q1)?Js@p+4zr{Z7CiHW~Lj{1M98b_kyD1u|p&R(S$HS9e@@Nm|s~%$F#Cy`fV7-boekKA-h9@-Ke_^T{tB%+KGygTMS&?1SVqaKHOLp`Ls7M!P>Nk9nNFrLVwvZ1@A_$#Gve4&LGU`$Iz1gCCwJW<8uYTM0*FoaBY?EN+YX*<BRx!@p(`Uq5;t?YnF?>Zf5P<TLX))|1b$E-{x?!}IE1eyn?YOhY+$)P+B)5S|O3-smT@8zY}zFJOP5XLGJ+nu_mT)C=`o#KHS~cq{Y^zNZ*<Js5YN+Mo69pLXjl*cUj^QGA2zN&Ql0JXh#jY0t~^!sh#?Q#l0XY@8kQOvqw9FWyf;Jv^R`@(<a7{^mCaeo%Gsy@&8!gt6%t+*g+pShpOlit-Phk9xlIgOpRdUJ>(&wix*=PAKKkZ|+7vxwR7hs8<-j=Q3fOu6c<3%gw@dlU>1c-1{E)6`d9N?_PrRnG>Cpe75Gp^Yn58tVdTSg+J;6=9yvpv5&APjrhjTzajr>`OrU;WfI?cTMy5p5tXrz^Hdk#dqc-}+vD?N-{EsZ@vU0x@VrZbeGs!jGo&AFV%_ey0QoFwjq<cDjCyNT66@#q-H^V?D7mhk*~U5~#c1*E&=Hc}oHqyQUra<k`DSC>HLQbujiQTCo<6Ve9x;9%?sxZ6_{JWrABtqeI6Ax?*DaP`eD9fr$iLAp_){Msy;`3H#rju~GxFWMlB$%ZsYtA))4B!w{F6v!s{dU5pZ`f@&r<(a|0J?_@nXgP|Nc#6lJ+rWQ1?@fp|}7w54ixj2-T0Qv=~`w8M4wE<Rav(48`TCoyq0NZK+eqZON0Uzmg}BS5l9VSCWrYJs$9JauN@;5IG6C47C=y47nBcJ8~;>YicoaYjRm?LULJhQtD9+oRoY*gRUl@Ag`hRL|#LlO!bl{liN|Nk=v0gPz#VNkh4*Xkc+TwvN05=VJI#^El(~%Zb@xRZb>$&lgK7HjJlE>Mm|eDPCiRc$@Ww2l#-#i3bhQm3b{MA6}daP2emc12e~S>EV(K<6*Vb275N<7PqouIhT?GQ8ge*!EOjz@EV&i69k~^`B((y$BsncL8#x=>CM`p8e1_t@)Dq;p<ObB1<ObwnRFgc6yowq|UPZn^Jxjhp&f$TocFMs}+=yC*+=x7!+MPU{Jc8PTJc1lVtx66e=cJ}0=Oo|MpsJm2G8C_+hLhKlhf~Lrhm!-Tt;m7oeAJTUeB^l4wB)pGn|KVx9)@C#npgYpKgBtz4ahmkb*RJ0b;yILtH^`M%cwWV%gA@As-5oex8gi(yGG<Z<Yv_2<Ywg2)Dh&-<R7R(<R8e*sX58b$$nJTPJaBY_%7RSE%`2a9d$T)9eFS{kUW@Nmzs}Um#kCck>jy#bcW)>48_T)8aWv`DK#fKDY+1}4!IDy8Fdi38Tkk5GV%{(i+YD_kuOkHJ6+&!#p&60&B*D=wW*`YwaEjiKadBKL#WNkA>=w#KXM&%2C8bO4E(M5BHL~q`678ebuf87c?`8Kc?`KZRVV9go8}C~Z5WEnQInC&kuy`1k~5PtQ45hXk;_t>k;{@>Q-2`0CQqPR<O$^E)C=V0<dam@PAB<WaWb}DZE`YldFnuNd2$<S2)PZpEwv80Ex8;u1GyYIIaRe&a{g9)ify-^e2Tn*I)=P~JdxU*+?;JQk)e1xLvb%^IdU&@BWh-HBXTWjCUPxuO=?+kO>#qOYjQ(!PwE76Px3VCa`H6t3hGJn3i2VUYNtc|t@tl$d9n({+3B?*XD8>Uwk78$7oe6S7a(V&CMRbje_;EmcKX0je3-g{e3-nEI*~k)ZL^V~_-BUVfz)2)f#i<VM&yp<`qWzF`sDAZHOb$RJ5U>vJCFxZdy)r`XHch+XONdrSCE&GZR#PiO@2oGi~Nk7i0!A^DG@`lPR&o&$+@Tn$hpXgsoBVh$<H;YYNzK6#RsW}$p^_xsT;`~**1y`#zeQ6sKij*g`s#ebsKpz`3v<kxs(T5kNTOcLUB<KLh)}5#k;86$h*k>solukSl0dw#noe?F*Sf%kQ_ixK&?bhK+eTb+?Cpe+=chqmAZwjbSt?lxjRE~AL?SV(gox`<h~5W-&5z2m4=ePC--0|?oFLdRyvp5o7|5&hun`G5)<R8zfk9pe<7b{D1JztOMXax#Zdg7I-5M3<$KRi{E?yf4Rs!Q9`FARL-A{d;&;@=<i)JtcMQd!7>d7Aw~)86{k~Gaklp_JmA@4?@j&a5n~;Z4i;{<s8^lB=Y65CevQpK*6Y#g<GYrMMsk_L#$>XT~$x5q}$B~1z|N4C}L-EL%*bx)kV`3C_BzY9M3AHh~2{}JCfSjM4keYy;keq><i>$OOS!s8&(mv!2<kAeq6{&s6O1~#pB$r|+E=uh|R@$3flw6#lxC*r&xeB>9HH2K7+)4XyoOEI+{*j@0CPVRj>M!K^<o(ps<S1%95A-xyh2nhFhh!CsOHf~tmA)sdP+ZM}P+Wuhk*xF$S%u<C9)#l3)YoLC@5m|?SM(qhccOkGEB#7Vs>VzwhT@^rA>^UtKxzYWAUU(oxXR2>d`&|rzN#S<AEPE9D^+9c7(?*^hT=Wc-Q+#wS=4c4rNQJ`<SEpVWTo55O81eK?j=tlyZP+(x$a(;YcKzfTh4tx<=@A9-N$QOrS8!FtA`z|n?*6PkbNzRyq~eqr++SF|6Rzx<MwC8s*kI=Ld^@K8H$6b`N=_Ke`-RqKRFRK133{nF+*{BYH704isba<EDXizsHMnCi;~lklQR^jq!uSDtwK&o&OxnB&OtV)oyZ2c1@%XA3-So+BJv1w1T~5rLB2v&<NpeOD^ANfAs;y{xj3~1xj4B6L-F_2YUFAh^WQTR4`3+nO07h$#4+EMp}0LmaTjVuaz&2wE)2zksYA(w$-}6D<YDB7)Xe0D<SbOxue0#C;_K||JIL3`k<?M-QS7^s48=nkitAB>$o0s%ss7~L<T%ts<T&KG)Wqb(?7MLpic>QbXQXB!XJOyX$WWY$p*RUOIXOA|ZW4y#6b!}LsX55m$(5-FxiYyawFS8;c?fj`c?fwEHG;f}e2aR8e2bis{af|pj10vksl~}9$t|fZ$Sv4+TQU^)Whfp*9Y7wyzB`DaxEDilM{0X=d-mOq48^?}ibqlhlSh(AQHPO7ksDJRk{gqAQ?rnBlW((stA2c&p?D`Xk{rpttGHxL=ld=uax)aCVkl0?Q2e(Cq4=u@p*TK6aY}~bYz)PP8H%ej6gOZfZpu*HlA*X2Lvb^P;)V>xwWuY@wa8T%iVIM4lM9eDQd5yLk`qxAk`s|Xd!VW=J~I@*rG6#9CBLDnI(oz3ia$_Ol2s^<OD`KaE;${wFgYDLfLfg#K(0V-K(0WpOKnQ7OKwbUNp4JTPHjbQPHsVMMs7iFLTyNHLas-xMXtrRsmD-UhM`!e79i{7<kXDh<m4|NXd<!-#V@I<onA5&Kc&7UKP5k*z9By$zo32~zaW34s&@Lw--?s4?b4Bxkh4$&$XUq6s1?Y?$Tg^S$u-FJsg23?$&IMZ$&JWC)E49*av-${Ignh3T8~_hZBvJ#I447KGOA8aM*hnKO-@#!_&HUz({qO6Thy22TjYz>r{s&|3)Cm%3*_t67v$^YN7RqxN91=@)lTpDTXABxT^4d;a%O5Va%OTNY7KHBawTegawT$2Y9n$@a&2l5xi;CL29gbOQEDA>9kxwTrcrv;13l#d*XEzy^FWn%kG@j3Jc{q|w^FzKiqG@6QulrpAK`DMZv80U%HK-e`c%A{zgK(ytAEAI$jf}%OYuVTLZ9|kJcm5Tr#~qEnf$X)|4}@fJlm(gDgGrUW>Ke7XOpLrf1>_O{)s%DI)^-+JeRtVypZ=Ym!WtGbv1bjIgGlM97f(iJwo0<-b+1C-b+44y+b}mj;7utN0Tp6uaYm3&rwg2&yf!^6mMgFs=9N>xZ=e=^}ColpZuKa&J~J(rOqcSwa9-_-8o0`I(ima=^C<1qtu<d6z}1mts$>r+4oRSkyU!7MX9IAhnemi>*pNn?-+G2+hs4?Z7=;Wwr?2Qe>(LiY8W|;=@n0<x^*^-_cx2aMU5s$vpg1c8+jY=Q*r8;d&n0P|9B9JUwIIUA9xUoZ+H-juXqrOZ+Z}lA9@gq|L`CbyDvP7(=rt2WhgGqP+XazxEe!oMTX)M48?xb)MP($c821lRCS+8`CIXO-uo-^d-7xI1M*|?W$F#`W%3#774jMKaq3O-aq?N}L-JYjHR>PaYvgBCRgcg3Tk$7qTCxhoDd^=Try%E|mL}&S7ok=r7a^CYRwI`uSEW`YS0$IDmLQiS7o_@;{n$1I8HzJ76nm&i$sY1=Y(LdbzcCcwramU$CZD8UCZ8nR)H7t8yq|iUyq|oCdX{{Me42WVe46Y~pOGE%@6=D^-^uaVeyW|~F%)N_<|1bz=cg7S=O>q<mM51Ym!(!Emn9dcmLnG@`%?>&3$kte8H(dD6u<UBJ!BP%?^0De-DN0_qTVJ)k#|y0l6R6Ls5Uu*yotJ>yotPpdWgJ*yqkKOyqkQ2>X1*6?^Ay#-zWb`RqgaAe=APFw#!6LKu%B1PfkzHK`lkjLC!-hOU^^iN-a*#N=`%dC;PK)(lCwEgC6J(4>%A1?5GE-yrcA$y5&)PfWMWx<yX9&zm>Z8t9UJcul4*_KZ;k7SNPPY;sxXdKJ~A726={0dnukwp6t`UipP`3`}7CJ<H+ND`j6rX<Ox3gP4SO0F^M{sI)OZvJcc@sJcevi$CFL+MCxSnWZug}hT<vI1>`B@Q0fYDD0wM$EqN(<6?Hp#6?r4|0C^)hl6sUJN!~|2NZv=@McqN(Mc&L%9M1Ywb?1(8#WQ{CcP4cjIg0Ae6^a*8r;(M;Bj2UEbB^Mb)Olp3%gL{)?%bt#J-y}R<t+Pp>JG9>uQUyH2YEBo?PC4xV*PETu422aV!N%PAIkO(W&4}dG1O3UDAOw*OLgmP67O#k{dv?#awN+$j~Y%6=Y1-EtM-3m^r?nWd{09tb~J?ICmKTW?;1k!KN>=DYKCHehT;kg#dR5qJ1`V`8H$@S6jx>_F33=vm7zE;Rozcq{#G2vgHZg327OBYgZ!9!kNlW?nd*=)lh0G1kk6AJP=6;sAitpgLw-U2o2u&TZ~j)ChIQyqPD2i$Rv-tE4QgGoL2gIwKyF9wN%fL@lKW7blKYT@sg=pW<eJoi<eKCn)U4zp<h<0l<hX2`ybQ(h8H)d8`>A&NlcD$#^)dMo`4aUq`4TyrdY&9jzE6EXzE6HheL;RnRv+cQU^}@VSSwCPRqd3Hp|~(LfLxedoobM)lRHz}kvo(7QG1g6k^58oko%LnQG?0d$n|3)sJ<soy14(R|HayW|Ec*%i}gQT`}S|f{%1(Oe=|dQ?Z1DN6jVRH`qm@nJtdBOKo_jO*wFqL9uoV4'

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
