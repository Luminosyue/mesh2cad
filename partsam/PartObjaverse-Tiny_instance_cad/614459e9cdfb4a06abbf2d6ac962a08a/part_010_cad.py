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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/614459e9cdfb4a06abbf2d6ac962a08a/part_010.stl', 'relative_path': '614459e9cdfb4a06abbf2d6ac962a08a/part_010.stl', 'source_sha256': '4612cceed61bfa4a85d11225523ef943a6345a77b9d84a62d2a572f4cbd137cc', 'input_faces': 818, 'input_vertices': 536, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.12922319769859314, -0.10155532509088516, -0.21198496222496033], [0.2162719964981079, 0.028899598866701126, 0.27133017778396606]]}
GEOMETRY_BASE85 = 'c$}r21#}hHyTvDHaCZuWw807~ZY6`$Vxh%#kO09oI1KLY5Mc1)P9Q)S+_kt)i(7Fm@;Kk#)86~m|E=}bd#rWV{@tCEZ_a#2=FH3up;cqYNv+{uHm!cgA$y#Hnx;x(EwvUA)~!c)%dqbGJ9X(3pd}Yy{quBcjXKps8w6+(TEC!HVclDH3o5Axm2O=;D4!nGx^uT4-I{l5*121&Fy&Wj-l2QgSHFAP=3T<Re$G{-P|<vPq1^fO0s8;(UqaQC7Gs<c)s`z0x9wJ+f60DKso8g__->8++tp_`e($47_2|puJ8>hU<nx42@KZk#-{}2*tJL59R(xmRXYtL`YbCxrWTg1+vUGctZ;#5cL4DSOC!_xGOyavMvWl<2?IXT@Gr#zH-IH=$^KL&J_f#<I&)F*Vt#NG;e@)>%zU|jif8*!tT`nX3g#n0PqMZ0v^~_QD+)aFKOb_vmJbR`6R^2q>o8MW8KjDtlw|b>O{JmqvHy>`_s6HF3PaTo^)>IsKz-{rZw12?=W1sk1!q>>>(v9M~rw{nG--}~(JcBs99!q=ddn?6vF8+!3$E?{T?XFx2@uxq8-|d|E#)f+0>$%eGl{mrI#Me)LI4p7QWES7u8*j6GE}j_e=}~*1_%GU{{*%8C%6Z%j6W<v=!_Rltv=`r6reR#2&3s6-Usw1I-of9Xi|-bg1%JsRjJKwF#MejO6W>hyOnm)FDa45vx?jf6$S>ksIckb;mnnWg;%rzXdDg2Q+b8ixRu^B-amLTLUNjZoICCBSp8J&e+QfF^+xj2UPP60*#3?r!{<D5)&%rC=J1cMCxb=^qJ##;aZ$B?^P~uN^#W&a2-Y>tGtu_2SIo3%1o?4W|O|s;m@Ax!dtaGH_zTGXp{rw;CPd*i2YkEO^tMxnh)%J;RXSyN2c4C;EmoX&m9;u(m72j=~4&yW1U8(OpxP|&wfAmX87OC%+e~bFd_eg!GU@EDvk57C^+W9y;&Ua-2sc$z*DZX*|!#ZitjAomp-50VQ^2>kjf)d9}RziGd+84y{R#|-adKvM}J#&|epJdZkInOaw#COB9%Xo8s{v$@tBW+#O@7Y1xV{fP??a@C*z#sgh)VFpf+bvpg9NIaekmSdy*uc;C#<@17p!jyGDexn+B0sU4i?8jOi}uGZg#0H<u}+Tne&Zp(aT3uL`HzZ5{eveE=lvjwW478az7;rTg`Cfi{Wi++${j|WMJ3Rl8l85^&kG(!oL-H^w;T4^B|lI92<P=+49++GVDSz5PR<<T<hZ&OBXQ$DIpjNj^leXmlYV;p7wR8MJw|@NW$zeY-+0$&v>dm=O!1Ao&k$$!Ygzxbx5MPP?)evpQ|!)IInO-Jaoo*s5GUP;iPD}piN$vozeAq6uKp8e$Vc(Dbj@YH=oz!E4e|9WKbj!zeDZ9Uw6j*M!xAso%~A6E9U4e{w?I7cHEq~ri8C#+)HkvQqJHtGze#&;%~&PvOqvjW&wC?%+wXo#gg9MOVf?RICjF>?hVNz$lK4i+_dBIM$5SBA@jI)eeyhpL#sBVG#5p!n&dYvVeX-;*O_2C@zx3;+JuO;Dzu33(p?*k3jEDLIcSyXw!SG+rk$Ge%3RxuWm{e4Jqippl5~s$)9lpNP<_z+X_=Wi9k?J_^`tBG%uSQFJcUw)=&vJXMe15rdwj6Ied@FmsNXbvSX);gsk#*3Xbg$9=tO3#<Gol{q|L~iP6YFz3#1CtLc7DvXTH-7pE%`C)G!kF`^TR@^zk2O@X@8++;+x@<qI~0Msam3)kJHFJvKGykel$<F!*LsqlK94j-N^sCPKc8vtMsGu>5}xLLEkF975x%ZRQko4-v$2ozL=+nUSgb7?F;|vPFeSivi(O%J4^OQd)!M{-)i7`XyzG+^G#b&@@WN!NqqO-aKt&07VF!K2^e3)CL>Puj1u2r{@w0V(f+HU7!P9)kCFELFc*0{ab>aieX_3i^^J-{WM0^_r^)zq|61fXuH1DqaJ{;*1oc;skmKsN?&G*8mSLP*0ZXL*@;VaVTD=nOtk4eq+pHDx>iGi?%RI7r&ywS6k*neNiN^YQ_4H_Ix93-zIZN`nZ4B1KDqE4Cfb!_~MUAoE2SsDte*YNl-qq}Y{9d}9IIrrDkhkDy=@%zn4C*g5ZK<EW&Ia)ZpMZZpuZ&wg!#mVB&mf=8+WOVE^It@LuJgvZ>$vV@xr}x$JtO_C7k(}4nEvS+{0Z|VjxlDa#QDePJaTR%mGiZ)x@do_^D=(i7SAQG#<4%qFMWzkl{~B(vt53F_I>0n;}Mzf*6|VI+oK-(tyj*B__*%V*N<hwK77^11#+Asub8)Slf*B!U#{cYw{LLVUyEY@Q0FIH&pm(px0~S)m37_z^AqA<eCyYKXHUQpX=mKcINz3EkOw=i`0lmLIL{A@MNRrz!Cz)dd%j$i{5TWii?9E95Bt^GE9E-iHc5gwWzR}K8n2Q_KJ@Cz;19kcarGY~5ud)%Fl3&zJKcAPKO-mFdG4dcv4-4~_0sH_OML57KRGWg=N4Rt>1(AI;<{6NVYGY>%Y!(bYfFE*Yx-`&I4*j`cV2k)-J2zFUR`eE{$<E88PCqVvVQ05e!3+4BddQ!v}ego=|^|{>19&CePx_i>1|u2-9xcXc)oLXKJG^<Zos@RQ5`<_C$3&7#@E*`eTVDI;9-~_CE<J5UuS-b%^^O%)pK88so$*p7O8iyF5+{2FayitI&+~u;<TAA?bJ>!lJn9IHbndD_Lg<P9=`_jVo6i9r%(^%Xa7y?Kk1vVTT2|PLTdEe&=!bOY%j)nkv)<hy+v#GZ+y((Q(3St_592QXG{I1hvm3h*>;GthU5NDZ;UVcPV{H#Up;M@?B|W(4#<O%0{fyzn$*|yPVgH~k@|MA=2G8T)enB%jxz7uun*Wjj~Rsc2UZQ0^J(-@@~j1og@5L??8meLL$_gGO+-6eO^|-EFXlqOyq+Y!z4@}lH~vT<zO!)_=a(bnR%<*`;@FcTk<WLU)Yqp6OMUCnI@BL~sf)yKxI_Bay0QWBvu?zF+|`*fZuJ#WXlM6<gC+juSJ=<b+KzVix;Rbh4GxhwPV3$9Gqe}q-d7CqEAB&n=FO4gnyqIdZ-oz_oxF~_JNL?X@O<z7-EEi;>t3oOXwR@GvcI*4g-d(1*vBxgDu-d+F3?fNzwMmGaTEMLMB-d{k9@8_hdf-pfc&@Yi1S)-0e+sO-Q;+Yo3{A+X5wK(MJvvg_Ulb<Aby*lu}=<(koaca+i3rbyU5R;(wlsJ>&tU#kFzTC7C%2-H94+b;D-3_{YUWQu8=rZRHIFPev0O}FL)Wb+0SQtj15aLP7XbVzs;U5dHA&r*0E(Tk<ZklyU6Dc&m<3akN2p5zC7xmjF9?Hw%A7{Kc61Rys(Fyb9{X(<WJ0(nCM-;zOk|L1d01LpFF3qwD{t?SD#=#>Gy54pI;?%qSXKC6`pH64TS%u(|9?4xvqHrax<a$PG}{Jll~KA{227@Xk53nkHc}?lZjD3TXO$#MPIM?3Fo!>q~za-NeaJc!O5aSyUOzmD>5Z~-bd>z=gE9=>D!&sW1myLpj;o#era*s?R)XO;#hAPpJv01@V`AbPL6jWSla3N=D`G#H!IgWKi^$2TztJ%q~zbCZ@mn}{a2*`X{YvcX7tzRpC-xg8GZbGH?-Fji97cNp0kw5g5xePfaebnZ!VR%@pGad>z0sqI(kn$U%MLwe^t;7`TYxRWZz=acjgU}yt!juA^w59Xy@>#4)WQ)F5}Ih@4g>DRr2?E4DSCoe~<QOXo~y&fEXDU7Jc)ZmuOFqIe6~5xB%ks%idZ1edo6M`o>SMBo9th?A`MFQ-AQwv!0_1*5M(A5NF_exgHs<BDeVZc9#h8^=ePI`}y1UOFo@OuXp<T&g^~DBwqe+a34qC%d>u~8}iew2;#ITE%BYgU2&i5`HXKzPr`kB^J2))vl~+1PM8V%F{2dXd-qu-d&xRy(6_Q4ZYMvl9S7@J))2pTntx;8V<s(&e&N2(+_3`Vfxc7eu<U2d;j<iHU+dFA@@!^$7vt;OhmTH|&$W6<-rP^+Q2$Ox@tvDhFn+F8!u*=n5zmeL=fd+b`bNzR$Y;$Al27MY6`b#uaGdX?Q0(WA!?&(KlyRkvERO5kj-L_#X$?89cCQ4^XJs|S`K>ATv4ir;xNzy~H>*hgjolCMd|*xu#GiFgj_WpEEcaFB=un*RtuDA8aec7c)<*lcy}^FF%_n(I>iOE5;c{MjqkKpG{B}*Hoo@2`_*}m(etsbg`T6b)o--D0i1tjVg80d*VEugA9Q}Cz9p?3U7th^qwM3i&gK^(CV4qw!Y|lS(K<-PObRQ&+L*GjCyR_3-b^&oWgu`EdW2CfiTJgPpe%h0Ae`steEWWl8zEfg`%wKzIXIYnwh3%35&=qKZ>W}MveQjAw@wK`ww)pybqt|l3r``P`@$E?+(f)-AQUCTr%u~<*eVLq>9^6lk>kjISe%XH(<NQ%Y>|;B3Mf{J^Shw3O#lDEX_ufPw|DB9ai@tsLn2a~QZ@|eAAK$6A1O52T%VYAnX?N7G9Sie!Ms1m2Mvb1xTl8+p=RfPM=X?3Q(I4+Ee(dFUz0<!PhwBS{H|P+qYi|Ov-==S5UxerXe4ggew}$?S>vi}$S(luAec(3?!uyNxint%8@64-#akwx$?k_X<Lw{}Rg!MB?Bk5<0zNx2_{22LjNq*c!1JIstqOcyG$Z^=$H&dmQ>%Lp;v$V(kFc9b4xiaoc(_X-Q{~NxQV#NqKe*0(G&p))#kLe4b{Y8J3=drfuXX`HGM4!|j?+HAAR+wDZ+*3PF$a!8Kg7Y<R`1QMXWSHN0Fkf!OIPv`CtC9b7aiyKswh@TG_yXo#oJqJ}TRw{Y+Y;-4{EmAi{%`P&C$;cCD{AC!Kfg~d#1B6%@lE<p*i2mai`aOcJ97;385SbfQ7z6gJck`Q4)rGu8Y@5NdalzqFXx{rKmRaG@}NgdK>MpqL%-J@iu<rSQ_!BIPh@=BhbH0uB7JW?F<zCB>#SK}8pdawj&fdFo>>^5^u6~E+SOkqj$LR5;`4ch)A*g_$DwcEUV!zj#m5+5-wN)7aW$#+PG8@>UKQ8zd5t8FUKqYsx*pcI%uSD>9kcwdgLe5lcuqy%SsjIO_`Ejmvs2E2-)tTBE%#44zP@$mB>H_`PK=*a^c!!L{<7!)isu~xk%-gO!hW^Fb&Q8t@a=fV5NFTK7+>GqIt$~o;V0Y|)3@TDko}kus|xn_&*$NMr<KC<vJGW%|482~Iu*|u`tHViK6e3pD=Fqns$0??o4)sc*&2LrkDvd`670i|43PY5rxzkl+vXV0yLZWZH=VxzIX&`x!ohgny%_D}b8;(AU%UtO{0+&G=a#$hT#>$;>y7lU8|}(^?t1=mQ}SS5z<$VGyA=81{@HGy2k*<)(Jz0+Z{K3fUk;zoGmU0DB@ZTjZ(e)z-Se#+ov=PkeTjC`H}>3?d10O}9v$NAN5z);sKx4med+iWXm61K>^JPW((n2N_~xlWc#itE)A0}=Uu#%j_APqJVALD13UPR!Wej?ZeHwjpX)LVI?~mhihc!4a@A=j7{PMoo^R+o6@mytPYrH?D@69i3YxN1zKlHtINxPCC?~fX-Lw;Ud#yp)jMc%i%^xcPbG0ua|?eX=sFO_k9IaLSqw=sNk9-oVqxh(sKfBYh?aJ^epYKyOL)&C&p>+R1y|DSznOf~d-)eWe>^dR1kjQJwxYkIynua^(T^@YB7->S#yjQ*u>_WB$1(Y=G``6V~`?SI^X_hejXrRcwViS=b_XK9a4-@C5q?WP~`^}X){XwB~9J#n5b{`<X3-K6~neK&JP9QRRD*@u|)z591J_H~RC&kvl5b^lo{8E;mGD6}X4Ks*oJ5`pz9BYbUiGvxVApscHI;C8?D#EEqW^%KB%GmQ6}FUGrQ_~Tb0|G|%ufBJTs!q~ST?1enh_pW#UyvL;P?W?_cZQt98@tHN%T4_hmJ~9rq`|!Qzkmk$Z@%(}QKj-C*ANu-(+_=Af!SQr4#&5mS?w6M9h)Lh++*{^_rEQY^nCH9MyI`DzU665N9&|9?;^mX~lIC~Uq@B)|y*TclOYq$ITxvgGdr=ze_WRiTe0{sFiRa*{tb=}Wb_~Vy|L9g&pSLoO(L;PQ-)`IoE!~gy^gMz0yqQ|#xGk`LSXZ)PKmV|kd@sc=dm8aOuk>5bJ>TnJtL#I3e}lev-)-khhUdWLSpR$*$+H%94(<ElEaLzC0_(&04|qPK<L8E5M*7iM*$DgFWW0}Qvmg2C_&uK6)7KAAz`D_-Db^+W&ab~?eY-IQ``+a6z4uD);rZAveYuD{@V?Ah9)a)k(D(K;cEA|q=da6%Goy*L(>}RR`bB>V-#F9^_uak1@xJHARkX9^NxyZ;nR^TVXh-T>e7|Fky#qgWTlD*g&N3g3zV~ok`zrEKaGM<0^Q|SZWnMVTx=S8x`eyD?-uEc*JTUwL+G*lFfj-DVKI!Xe4<i4g%N+6by*T!yC;NSUZO%(MuHNl2+S3lc_r62Bn-Kf729I#u<VpPIg-zd%!h21(cM+-Y`C4c?__Kcy-wb+=`196D9OG4be1D0)T_6PS4?6#Z?@^_Fi8#DJwG$P__n_jvhX48qzNfLb4!++--$<Dd<L8eeGM<e)?~tF{v9J!`+#vgCi@v?HChiL&F3Ngqp8Mc8u8c(O5ud(xXCB_4h6dsLVD#<LzhIms-741wXWvKUzi<&8H~#^gFMZ2NgmvJzP6z$`?wuvRJ!&EL!<#-MZxP>Pe5M?Q@4ronC3)3m*T;4F%jqR@{)6L)Z;g4f%D0`K?>rbKzMJ9^o}YAy2Y=C09Cu|&oL5cu|H6*w7w^6}e^T^woge(>-GBFuR8fa<-t@gZulq~#?0l2lufBWnD!z9|->C9>m2Z3WBq?!yt8pFgt;&tW_uS}v^Ghp~3jIOf`~H}bJ6w+IK1zf0{rv>q51#!M?SBm4e!c+jrGkp_`vmDwKYYSEjPnE-hbzB9eXdJp`6}2S(l;VL;`<eG=kNFR^)&CW&Q>mkc`+&*`tg?w_&&_uEE3=7odfatd{Q&ApkM0-`Q^d9ZAsp=dhosHT}IVus8=z!Ummm-OVKa%t&L|ekG$_mR)X*Cd#&S>(O)^g_ZuhPI%9kb-`o<2=hc}CVBeCu0P?W*Hm+X<FXK59eebxgF%0wWWkJ+`8IJLJsi>dt{91UW___BV@T<RJ#&{VwO@fgBJ;nXTkJnDy^QW90EP1-|TCO9W?>$E~x{f&I>l+Iz$$8mpCY|*2PglqNdyYSFzUxc+<;R)R9{pmM_VdkVlf<_?zgRP@R})^~d?%Li&vViO$nzirc}|jA^5%TxdqMhIwGH^b7S|uQS|zkI*$w1jXB#=LS)IOK0oVPM0}z+KcVFYSyn*$!bQQFR-`8@jahRv{joM|9hxg%<A3fjC7;hhw%X3>hMGf>zrfUBEQXnt-g}&3N&nn;go^PaVzruGudcJ#g9G){Lh(!B8)I>jWKjW?E&VyR;`TSoWd-#~IZ^azI`}7(ye)Y93LuX0c^|j@^oWpfce{R0H^0`#W(^79+J;cxW4te1EW-f1l_D?>K`4v0@@n<wb`x8u)ai!%wbkx_^c8!%dW{Tk_eSIq=3%+L-T?Ba^(FFe9rz2$i^zLxN*VmSuFCyoav$9`(yLrbU^0{27jB`D#xnI8<%c{zGx#h#)&&Y>)_j=J0KYx8O>ED0WRr*%+_p^Qb#m*j%d|UTs`{vV4(H{8;9Eb57ni-!1Izn4jm?Lps+{O5DyWqINucW`6I#)68PIW{751otW?}<ztm%g@SU8KZ&QuB;_-reIrUKjN7eGz9$Rq0<X`%pY*?%&_<y7|w28GY?!g&LBdYNpiJIt+wAWemP2*>t@0i&1hI*Ymov{@7!~PWk$Jts(yBn_(1=n|`9)r#LNtm3}b;#~}VsIi)>Xi2#hJw`0-%QZ3|swM!MHzI9<D`o+7ixrKRd)A!ETxmN3pudmHHiM;h`BEEZIGTQlJmee=f&%*g0gm0Lm=E-r4N>bn4GW9>N=k&etW2JA8c~NTt&X?aaF<M{7IuN`V^%q4{5kFyD%nQ$FJGJ@Mke_7B|Ks}Oe*O*d`TZh&(n#qS>-uWH>w?!Ww&!1+Dd%Nm{Tbuu#9HKS@HO;Hxq7EVLjC^wC1aZU$u52OwFkbI1X^mXb#tFTeNm=#5A{F)=}UOw|J9$q6#t?4|MyQ{dIxA)o3Eud^;dFja(U_>8n`_9i3Z(BenO6+t|P~gcTu;Icait7D0WyBZ(&jV8+8@=H}VAPB=Q7uJ8EZgJMvG|YUH2DWvS)JN<+wH$rY#-$rZ>|s6UgdkZVwDlWUOcPzR9fkOxv1lLwNQQrDB0k~gp@-p`_VFN@-Z)cWLw<gqM@`%-@(_a&F2eoI!GpInMunOdA&nOuu%kZX|}P=6&iAa|j*C3hhYrH&#GB~PKwB`aM*o<g2aokN~ap2nhh1a%B~1i2Hn8@Us?A+-s)A-O!Y61hCN2(=iw2s!uHqEquyi;<O<B<Cf6&!V^xwK};FxdhcDmmm+K_8}{sK^{c5sawf5c{7XR6V$Wh6XaLav;p8(<m3U+Tx6x+l9Q8zsAb7Ye<BBw^HNQ6UUG42cXDxZMHa=4sKdyO$UUi}$x26%dy@N5Epi|70_qa-0`h9=CbH5U<kjRYU(0Ulaq14T(%;F)$ycej$ydpjseh0!lP^(kkd+=FUn1|JZYJ*`ucs~~E1g4LPo7VmL7q>ZNF7C<NFGA%P98$;N;Sz{$<3%gk(-fgQOlBRk!w(YB-bF<p&H~m<kr;6<ksXK)L+O-Cy{%QtFkDLp#DZyI))rUF2$m_8g(YQ8o4ob1-UUfoVt;$v=cd;oS8*&Dr$3bDslp93vvQ-LTWp5LULm2aB^aDdg@$qdU9dvR&rr-U+PJ+(xv3S<O(c`$5Z!_m7XDwC$FJiCo8>6UPE@MZ^#b$8Z~|_@HO%WY67w<ia!OQC{D_sry?s&Movl&_*(7+K;Kf6kyTOrk(!*WG&NZj#j#lw$D*bn$0Em}rXj~6$D^hrD@{m_NB$fDO+;2jaT0oI$x2g_laK?ciOGRvjT)D%k^c^Wz6$`WqWB4m;(OGmWTh@y=|S>6@?jRm-Kb;9-N+57{mBi;^{Ca!O3RSzk;_rPCzm7Vqh=-NBWIu{A!i^5QWKE_$#JOh$Z^Q=Srn(CrY5H$=coQa&QGpS?MznMi(H@FggTJigxr=oh^(|9xh=URwKusXxh9L^R@B<$R^)=z^5lZ#Y*cm6kd2=eU)P{9<m=?^)LrE5<S6PMauj(7)gdcgP2NFX!J>E>btQQjc_(!@S?PYV(!J!J<Vfm5awK^;bu3wFU-EErFBZiesinvr$t|dr$t}pusI|z=$YIn5<S=pv7R3?NF60REIO<Tc(kbL|<OS6E<OSqK)M?~J<moJmhfzn6hmqS;JCWOy>rxw%>ypb*%ahBHi&Be_i;{z>xyixgJS>W{YX9!hv$7~oPt8D1PfklsPEJcsO-({hMomObLQX`E|Fy)SCZ;AKCt<9_EQ(W7Gmuk~Gg5VOMshZ4Ub52f$=S%+Srq4>79uMxLC!(W$)dP7br4ypP3}#e$D()>bu)Pr`55&C`55^P^%eOIIb8r$-B&198bnr_mz<8QQ;U;za&Brxa&B@FY9n$H^3N=a!>B#UO8bz*$kV6`$Vyj}r;+DTw~*(Nmk0cN|Dbp(bpv%bc>_6$Me$MUakA2@<fG&x)XU@}<U`a;<U{10)IH>#<aN~bWTo@T>&TJRiR4J~1Qx}EsYA$v$sMU($sNg|)Mn&RawTdlawT$UY7KH}a#3m>a#3<IYHPC69%Q9e$;HUQ)CjWDQsiKACTcZuCUR10V{%e*Y-%`JX=ZY4@_P-MimZy_r_=;wRTMv>CM2t(_%<~$Srx^1sOib7D1JaKOjbqlGiqP5DvAT>RUikDKWQk6bI==4&Oz=#T|-vtkUNm4Q?HSylXp=+kav-9Qa_Pzk{_@r{z6sz{x8%3vMP%I3i$Va;4c=%r@oez)EMd=at!%2^)2}{`4;sf`4;&hRoyc@<Y&b%sIkbZD1J$eLsmucs{j<muc`6K@p!NBnnm$rs=7CLObsLl@*dzZ>nVOuRrdgjl|CUqqdsC${G9rP{G5D|MezyhJ+jin<P+o))NbSw<haxZ<hbO|8nhl+X*segir-T6kyTOrkeY$4isEY;isFmZK(Z=|&r#!$RZ;vqH9lDt#aF0l$f_uIsrkvOD1J_@PgdH5tcv0f)V5@$Ey=1Veod`ORz>j(4Mp)wYAdoTif>U1l9gs7tD<-xRqgu~E8R}sM_xmXBCjDYr|uvtT|r(>o<&_oo<*KW-APs&NuEd^$)dO)bvU^nxhJ(3xhFZC+L5fZ1v#ADltpnPYBO>pa&u}JS!oAyb8;IN#XYDI<R0YF)N$m|<f+sJWTlJ9Q^_-_)5$Z*<Eg{Q<H`N0?aBSgt*Ld%t;xSo%aDH||41!L{*hdmMR5UYFj;9HashHK7R5m<inCC&lCzN0QPY#tk<(DqlGBh=QB#vsk&|lw-UB3MQ5^WS#Qj?0eJu&8f#g8eNywr&HZ>7hX?${QaxCrNdkOEcjAHMf;s6%K38;z53CJm^DalGRl2ec~QL~YiW+!JNXQt*LXC{9`%}M@-+@0E+taKi^J9#pT;<eOG<hA6})MMn+<d4)h<d5WJ0Z?_HpjfF+PDcKYnw$I`xg@m+xg@zE^=EQJ@=$6RS?M&g(s|^e<dM|nWbYneB#YuH)D7e*<W<xt@+xvP^(a~C5ppzn8}$%*8+k2tCwVP-8Fd|b8F@A}l02I{jyi!njy!-mm^^^ol-iNplw5@xO0Gf<p;jV?kPA^ulM9jaP>YiDkh4>Zk(CCMvy(GYGm$frV^NcmW0C*Xps~rSD1J;;d-umIif>Y%l5dhPQy-Bplh06Zlh2S(QtyyYk`GfKkPnj&QlF6zk`GYT-u(bSD?UzD`}pH5iZ8GzzE4$q`uqH>SS?CQJCHSU7V30z7IJ&)E^>RaO}$B8^tCMhTJ}<HvdubssSn6|$;Vg}-=}^dEB%XnpL~USihPB<J>cJafbA@bCx0znsCB6;$#u!Is4--vr^&O(`>D6cN*|K<lh0CLkk69OQD2gkz9OF^pQpYiD}78>`kw6V>Cdw$zVNktLruY=_)qFHveHN76x5v5M`WeX$vMdds29lv$SJ8O$Vy9)mBuBfB!AIR6u+aYeg8Wa#eY%Xl9fIr|3$t*y+*!4zC^u9zC=DnJx4x8K0^JSe1v?6dWC$5e3a^vkCM-`DE^cBoct&GF7*Rh>1*;`@;w&CSE(<^N?($%lB21&$V&H-m98O2lV?+xla<aQ&n6G1P9!TGNghn@O6^Bh+LPRs+?X0pZcMI9ZAz|6u1Re~u1OB1HYbOY>rvZ~>ycYhdyrd_E$V2p(y3&NJcK%vtaLni2)PxtKUryOveIA3t;nURKaxw63sMV{3zG9u3y_uOBIhHkueOC&4TzOG_W$%>LjU_ueV0P>`wyc3`)~SxozC|+KYxw&&zI{$tHxD(=dYXHSklQU)LQ}VzX0_sgRu'

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
