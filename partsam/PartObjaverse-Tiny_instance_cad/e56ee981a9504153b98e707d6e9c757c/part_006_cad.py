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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_006.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_006.stl', 'source_sha256': '6f35d96f624c660e8e0e713accee20820d45f733e22ff4a3e8c27cbb80142703', 'input_faces': 1064, 'input_vertices': 708, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25506025552749634, -0.25954151153564453, -0.27523273229599], [-0.08452759683132172, -0.08900890499353409, -0.13855628669261932]]}
GEOMETRY_BASE85 = 'c$}r32b2^=*ZzA3MAA!K1VLa3vLGNiN*HpIAUQM3!U9WX$w69jkSsYkWF<?^J8aJ6Ajv^M1PKx(2+G&D@6)q&XW#!h|MPvGQ}6S;&(>5|S6APz?w;Xo(;{8^0FD1EqRpCpqMEn9rcueN1!$xDju<&0xNq3!LxzpBX*o=v{<CyRs}3#Obg^lpwF!ZJ`i2FM2(0M{tQAr{u#6)xWax;IBZ7wX8akp+U-BCV4GQaP_+kBnhV?b#lGVyrFXO0Gs*Gcj<A3>IW}^$v-`k!EH`G(g6GN)&W6zrUppEIf;cM3u5=kA;nwh>cOXg^`zVk&B(|5pkpuXpW>ZY$Z9~r0C_hzWZ{+A=-MEgYwo4$6ZTcl{eXd&+BZT7A9wFR$FoAt)$PZ0GNy)=FI#C!>A`<~yon7;Ri@KfgBQD6IG6SuSF)G4)nXXkocKkA1>F+SaEvmdi1QM7;VY>N5$mi0WM{fnnfUxRP8ulN1Z^j($nB&+Rv`ZZ_2YHri_UbFgt!HiuC${sc2C*93{INwE>zI#dX33a>rzaG=~%(-a#PHWsMEn@#poM^|hvxw<y7doV<{n7RmX8%&V6tzG4yPuQH?JcT*#PqYh;^Ws#H+^s6iO0k^1buD#&I0-|wLf~_@uu$>)yV9R({Yd6S=F5Vyxv1<KedYirmuHga9E5($#}Cp*S0>V#qs(qmbbH`_i45N&hWaXx=%Ia_QR98e@}9A{VL0jsQt8jN6p1Y)ctbicxlcv_l#h(Kic<ynC)m!+nT<kX_R?hxCgA|;~UAoUOQTxM_SFVxc+<goxLaXagT0e`cBmM&7Y*^JimV_XpWc5nm;K`xt&`D&ZzsVeba#Z8CNw{?T_<feeTbeYO&%xg71QF&2ufG9@j@Z4y&J8a+<!Uax(AllzDufXUW0ay_RJ9t}AYyPua4wkNV!r>^lpj<8}^|idEZj7PN7F_#V{vtk&4i&b|}v>t+9mH~+pkMU205^jp(+!?(s+ANj=e_4S|1@u|SRGujm;#^=N%(|4i1H4c{Vt`-y}+JUdbcUtq%-?!SS#J&UD_2s3YNN&H>Vv$$%YZ2_fW8d1Y9(;=1M}6x!>c!c2HChy>_Fv!s6Z=0-j8c!6XC(Xj7WS><;_v&8<2<+NYqh7#ak#Y3^u4vFi~ZHzv$_AcF8Jop>{&eiyN1Q7$JeuACLiBc>|66e+dQ4?#|0i%&tIQ^w(w!~{MCDp;db)(m*cj56z^AXh#a3>MR|Pkm5Ef_(Y`Oj?T=yKW1a5-4jzY(J{Q+7&%MH2|8w@O`H;r9=0meT`S|_TB~qLhe!eySZtoKwuh_1U;y4EW%KH-^5-Ij~n3sLMzu2y~`%U&A?2i}o-+qI~{U-aq;|pI8+!wEoo7U?(xASmsygCovm-m^zH^Uu1?+%?6zU%A=_WwQ+FY2$h@%dhRTdb%bvd~<&IQ3=GqJH_prtgZJ5~=#`)tPynb9!)+>N^XrHb1ZB>YAYXo_nRZ-S&;+RNt}pFwgVl6=OvE6PvJqwGf}j3-)k-98=@PaooF$`w!om=dMNUd*==idEWB1`Tazmw|o!UvCa#9&j#*Kzft0Nx!$;WyL-aK@pAX%^T9Fdo;kkWo;{OP-*t5tUl+Qy7WF+Z$8i1ie0{Qf@21-9ul*uk^_{0Ouz#m&oM?Y&k~xlEZ(yuwf9_IVuLc&25$)IL#(uGYXwm<;x~A_b{io=^qhoRYd}#J4vE8yC@^%AniT!e>f57dAXpyRKT}M1auFL&>wUn=Gp~-T81A6gw@TWMrzY)cGJ+SkL+~1pzI1j(rFZcJ`eSAIobF<iAC-SydZN1npXQ%o+|0*r!Jkid<{>BP?{VKZu%zyRgAkVKU#QnT=FGj7O#z%dv?R)-wK$8fwA6CBo;9s6M9h#cHmG{#4R=&0Tb&XBm%Bzm{|L{5>XEW2c@~V63W1del`iuQa<6Hea!t+}zc2MkB8Xxt&BY)xTrc^iAjn?(W=U*;=NZnt@m>Zm@&P_4<Y2|0j*DvV2U&sTlA?$m%aD6Lpd#_&L{^VUO#=%qUJo_n2<hUI;&Hj)>+^-+|C#k;k{MYPn?jq{z)f@Btd)Pif^*w9<!}@!pc+q~ki=1!E)r(VoNB=dPZ%bE<746R$j`RAi=#M_FFSj$IY>eu=D_7(EeB+Ynr@LZlt~aDmwCK-Q8n<8Uoan#S`UU6n10P2TAM0(+5h?b|@y`)nZ~v4zQuSR07Vvo;a#HNC9^anZ3EnOC*L$}h_wUDTV!yQSZu9xMd9~=jYtIhu-@|31pL)*`T>tl(W`DFdKXU#3Q#kKnKKT2dS=N0V`<{$b#Qn0j-VfMco$nj0^~T<<TtBle@1xIe;{MkO73WtPALonX)mol!R}YEvD~*r(uD=%X{<b;8>x85RDXOm(=*8EyD$Nr`{kxAipN_2>ulnBI6FEN}D;lf%uJKto&;6S%TD1ReHTSFD+X&Tn&s@NHIOD4%)pxYz>$=wBc7o{7Cp-B#%|9I{+Q0V&=if8OVnqA>lg#buxqsl}oHCF5*}O3yU*reN*S~DY$JfdyXTIfrzhK{5Ke(SyXFs`;m?wIzY22TWDvIN7`Fg!6{P&i>317>alXc;_cu{}edcHoLI~l9`j-Wy8*XWWY+UZ=LugiJ1N2|WO^jp53PHdDQ+AkW;*SXHiBSkweXY=t3uMj8dd-AbwFBBu{&)v$$u~B9o=cJKb|IEB7b$+Jtt?R{~gZaFeTwTonG`@Acs6L42;fcp${-^O#-}yL*kC%NH&-2!oQ&iu#PD_`Ntooj$T6{c?+(=Y??|3`kZw)$=AlhG^$n$bvV!UV{_mBGS<8i9*4(iJFU-I?D*M3Y9uK(<Z7}a-_xzFQWV^g$ff6*TPdzGb8qJ69zwTTNOMf=_Aa{aO2M2P(je8`_aJ4}p&_u^0NCkG{o{yZDc$1$LX7$2wG$@O!z6651Op2_q*9h-^q@r0h{^S5nHF+R?jEBL-|Wfd_#u7|z2{?Za+eB56Ja{cQ?#Q1m*KIV18m0aB4YA$ZC_ysXP)A-i>jBUgIhA&0^G`=-I!yVk8Qm;k*G`^Le!!q-6imD;%r}3@+EKkS#mAf3TgHJt6QGLg_m%PqBaXVS{T{lng_?CW?sQT^((|H~SK1fh~&ktX6{ULYbRbR^%!1Y5f#i_nC>>BrL&)Hbj*RO2gcxOb6=>Lm>tj|wGi}tZj*8bcTCHf!!H|L$I+ag8#gZa6-yW;8yF%BOM<b2hugBS;ARC)HhHBJ)kc;9dy+fYx8k7s^3`|B!-@zJ)=;(30ztQa3>msVW=Rv|Gy`l!78JSQ-}7#~lu8@xZovxxE0oLhLFhh`At<9Ixf>-T%b8mjR)_E;kBXDwgrwOHKGIu2an>tu_&a{l}K)_iWv>rqeGIi6Rq$EK*h>#yG8d5*7s_*3rh=7I65@0_Ev|9hucQNMk59*@r&MvMA|*YWWkTs~54x6eGjeiip5slNB~PuTCbBSF-EvyG3}wiR(=yODf;IUh}n5!;;~$J;A6oR8-|+&>qX!R>j{pZ#yX?>uc3&-LPa$h_h2Tla&z`F>O@xJlGc<6HG-ZDha5zG$^S{=R>GeRr(+UdH!4-11*Xo4$1)<UO;2+i}N=_c)gC+7K<?`#5ec<8kPeN#2*icXa(w+?RPy^K%F9jf~>HOb=Sj<A1z>xG%GO4ZhWXN1lm%9AAv&{fKvRe;)Sa`onKUtG>H)N1ji3-foSXzwaBjYK?e*SKk%ue4oGewph=*DzL9r_)V-2{e9~`!ty=i?ud1x+gY3U=k`XqUWM<zyI!nUy=!Z6{T3U=de!q=P44I5g`z)}uN|B(wyU+}`$f0&>_M{~>v^x`H;X^09(O%sNp7diGdcc8Kj7^a(&N<moW{4#m+Q}XzQ)uN^V#3`T{qwV!Ry+D8lwF)zIESp^*8p@Maus8`_^&ak9mVUW9^r=?;_{pcD499N$~IdJmwNVw{nGE;p<RREYIHy5uDHJpW*W;;|QL=ua9w_n%#wu*EjW(Ro^wG6#JiD6TV&^?@vl3C8@q6%LDdDyhu=e@0W+!FEB4r)E_vH{Zns6``X({?C1SjwBx=wmh<?2ey(l#&X3#ix_abe(H~ddCS1SAxOmZiH-4_~3YjkVtI8)_Z|_dgPdz#-`&~oDb{*~yx&2q1e=Xm0`xdWHcCC}+aO)!HeRtnj(a%r$`LU~0HL+de0?*s~Yo+Y}!qwc)nvP<-?$BktZm)SHO7s)&SzJ%&$Z^}zhp(r%zls+9d{T$&uPP?Ct7ATUtIZJo*K?L(|Cjn=yIPe`xj&OO%lS5zpCf9O$H;LT{hae*i8_&De2ylwe<QotuC_D|_d_E@|F!E!aerA(Y}e6XK5utSu<U28p6ol`319EU>jV8nPthMwR3WZ^w6$p8mEjTRA)JrC?M|x0e=nC&%s21Jtm6HtuRhlQt_zFAe0DcUX5a7pa?M`NzTf$!Zym<Zn}(he?YkfM=K6l;mm^nqUhf`|=a;8LRc>eCUeO<KyU)0OPkDantupXBGoXb$uSdM+_f~%Am*dD&_WjN;{rUr5U%r;-m-BKAKQHh*znq1RaQ*f2{L(&N%Ju!uFTK`$-mc&IrBBtlowf4((zcG{_XK|DmuGzkZr|_xGA>lSe)BuO^xMU_zTf$!eOQpUTV0-CTC42rd*%7%9CU~Czu$SJ?b^%Fo&3%h{p@zWE=-W;i@RzVx8rwS=ws`#kMqKt0)I;@z7AtOVEHci*1F5nhu44l@QmF5tL3@9{6F$`ALN(UL4V)6E(dSrd1ABkIxYD+ulr`Wx&4#ZMLTJHwBz&ht>bp89_RJuwC{M_I`DW|*I7@%bRMVYy~H}r-?!S=V|w#AY_2T&lg78!1M7Qme{f&y8wY>i8ixw4xSe_1#Ckw)(VY9=evP>QvV2F!Rq}n}Zw+|f&KV=uE&jfB|JC*j-rscD#Cq8B9q@hY;T|>F@AvkUIv*_GHQ)`8yY+q~ydv*U-NW*}pfCH*-ABaw-}2o*9TMw*XT}QL&a8vtK0>=ynDf=2edW5&&-We2mU+3IrpLs3QZN2DKR=2J6ux$apZlkIZV%u8IlSe2>MWA?W&Xak&J6dm|7@vPhg-h)#S*a&_Y7cPzqUlI!ySb$alWqHOx}0<`_}q1<s3gx-F8{tcUb<8i{ie+yN7-4)Fm+v{=RkJVfmg+7sdEkzP{qVxX<<Xea}~S9_4ZPH%07M8sDlv<45j)`+TB(f8RGBp1C<M2J-V$S4_!d)%QGY&Ursmo<!Am;dzwyr7d36ug&jMyz_az;A=nQ8_u6+e~uFM&&}j|0WlG(@7=SJ&(}$xiT=1IRKz_0Nc6|k=oJ4wT{_VpXO1>}d>TIy{qbDA$$5MBHU8YRwOqgZQ2yRa*ByL4>9vCWOb$7p{e3I%J;M9!PA#~dbdC6WSZNIJcfqIPzR&U<MIXugz772T%oUrD_h-R|WYyP4@%LQZbC)EkzIV}9&Tr@DC#t^Y9L&ctWpaXOzdL`A!I5V|ylDRvzpr-Y92BSeo)Xb~UFh5|R<!>u-siOM9HaWqr|tN;)2epSqWz8qc%Ce47$y2Y;tt=h->4fY+AqTIBfUTKb=LCTy}#jh4~L8K@#JX2{{B5;d>mzSu>W?u7$47}>*DyP@vZa4+OKODx!<qWi1E~4t>gN2R*3QRZ0^H;&Dml+wTQCpe=|*tr(@W2o<EaDiSg9GJ<iYJBZrCc^gNx)emK6zcb~WCJf4f&IarOaW9|8Ta9Z27@`=B1<>y~3b3f<plh4oneQSJ51#&x62FmgD_pN-Dz9{dP^*-^de!OmN5y1O(U^zdBFE}$<^}WG8_`dkexFpqg>LvL8*A<qi`mWC(^8H}$kOa|w^8<WdbPb9Z?Y|z+`LJW#IMIHdhFpJb%UIEVWG1e+vQCWZyMH;y=Y_XMv}nKKD)z7QeTL;bw&A@>(Gp@DT=>4Iw@}^)(VvlaZWqrne16e5{v4iT`1TjqU)SJRF+QG$9oZjnSd5PY`AyriPmGUi$UV-VJ2r{&ai8DC_XW?s7vtlpKAP)4St!QGv930s=T*KH<Ks&A0pE{Qn8fXB{QlFE%-<W)(|6_Ppa=NAOFx_--&gwk)_g9?&-I<-1H}8#G`_Vi-OuNtb~6U=fj>=Fef@_H?61z5DC&oC9@B3A6DRz?SMdGCA7y1bwZqtVJctoK)?@C^^NaSqAKE!j24j6=wZGsXuOEkJh*y2rxrMloiHJ~rH}a%&|1+^&4f)Oa>ZWL4M;`OmNaXvSfB61Z-xw;t?*!io-}n8@l>6*!UBq*2%h&Cl<oAmPu<xEcoR9m?XA!FJoY+M?-*&#e%l%J(l%HR%e4eEGdP-By%h!KN5cOAH=Db`uDNfYK_i6RshhtRVTlO!!f8qBAmhXB!74KgbMu_$=Z07kM6eRkouj4%G*wivn)E^MZdHY_Cc-415XvcZJREbzo|G=+2Zi901y1(yPu8;4R`pye~-&zm9O6KwOe=qQeeXV{$@x3+6cQz~_zb|)&uTQRo`r`ab<6G;cY5X2e&-{+p3H!GutG@g2DZKYwk)-<C#W`I6)sjTjcT8=A_ny-dMEl==%=xIM9xvK&`3v5A4v!P<hw}FWT$A{F50>x3`!dIpqoSYA(?hwPaXn(hc9Vm7-YnQI`mf`AVh&H|Xw~=LFT?Aci(ABgxmW(n=jn0W$5{Pb!O!otbIZm4djG}mFR=df^?yH}Z{=Ge#=(K-@Q(LYBE)t-p33zDrit<Ke$Dsa-fok{_-J=>vfpW#7zbA~tozpu6#J|1;`O+`s=L@PPwxKg-|8g#uZ=6m{tf=#rMo15kHI<i6Zswoz6-y%^4&jvwv4wsY>NCH3VinnUH%Sb6TZK8ey04srN3{je_D*?@u}WX+*kVin(gI%WhM6Y0v+XjrJrxzSGu!>@%U7&DbBAnzVCajExDim-xu}wt^S{E$o}2;qJA3RYJV|5zw_WZxfZ%MS@pemPpyT_Pf~p+o@0A=%uZB&7v5iMKaNij?Qdzu^`G$f!F}y#!S}l!a-Oz)$8dh%u2<|GE84&GJ+7ziVnl!P4PpOAl<2?vi+<eBD1JWWYbT}>Uw?l-Aok1a{+#{cb)!W8e|^XIvyPv{{yH+e<n#J)%}CMCLVmC1`DB9_2iHLUK8I_6=?KyPopbrRAG}tKkE<I$pY`;bFUH3+CO>a?%WN?|o=^GtifhAoF+Ps^{QSUqf0P^tJcoDP4H5h6&RU(<38j0>{Tj~eGOc7g?!WUQuLClc;{C9mv&}xwf6v6eZ(Wf!p0BGxYsB}Noiq7;pw^}U_se=Nlns8F{M-)mgTL>4jtAcr`knk<bZ=faxgM6_`-q4f$*S)?cz~}*AN-Rb>VMOauRBfe$BFuOd~aedtFJz;7p@e3o?-c(KdQ5j_n5wRmgD_x&Rr3z?>rdG$0_RbMAdie9q~NAK)mWZ@VyjwvkzlM{X8St|Mt1)kFf)shfn{){eHZP>o2-5zt`<t$?G=P1G#>H@9F)!SU)(bvG2ZmPp(7S&*V6yf&86F$LTx{@U8ssnA?H3TY0$n9gyX_s}2>v>v7E2*vI=I-|v`SKjr7P`x}bug8T0$?C)zNuOsgsnZEXKnJ9H$S-w*%9i{eD55COLc`JR)&vUT9?vgQFe+&P<!S}t{=~3K%4u^dH{~7x()c1`;o&)@xIxLIauUh-LelhlazmtORgzx(u-^5wG-5Rw;KlMTEduG;(Q`@n8H+<hXM~>(EB~oJ4b{zU>Zhv`Lv^sA3l#%>=9KP>&e2YT3pZU(j{5RhL-*??F%f9EvX?eYitBi5Ob8_o<8AI9k;Q6`ryN@)!HO~_&n!b*9eB*hx4A&1x6u<AYd~d->@%uja`{KM`xPCdT?fU!H^Y*Lk>)CO=v%a4O-v!?qe`nKT?4upu@8EU?o4@z=RyZercf2Qv{c;yhtMgoc&^?^b<55S&em&`I`i@4!kE;9Sob=fIUALp|4e`5dZOQ}F*J}SFf5+|Je%!48Xz_8ieeKRxGxj{4e_U-}t25aAowjS{UhzA0t^NShcT7Dfez&fLHZpzvYHM@5?sfb-XlK8k{5$g=r}%sP_?@*jsH^GgWdg$0{&+^V<^8XaBV6q7qSof`t~GntBz63?RZaN!=kL2EiSuQDIriKB%Fl7E-?{hvj^{__;wh@H%^1eNC!hXO{7&C9XOQVTX1x%<>(~2kHm_%nE!V{Q(>Y|V>1&&A$oC-m>|FoMG?}-H{B1s`cH#FyzVY8X+Vr&n^+aCv935i%4*0(PEu5Qu<U?PcDVfFeb$cn1m$V^?2h8o&TM{eUA027>9{9fci?*A-R_um2uRSX_n!XdhS-*|=*D*4b%(2Z?(bz?!WYPk(kRaus#vqgav-H3J(-;FP|9}0{7!}G_t^9xcw=psoGx|`_97onqz`N|4w%;hbp$EVPjKAeEN<L^Va0%mY>x}X>bSwC4@OGmVwrSdYqwe?6$~I;y#PLQcWt0z$vQ1;{r!i9@E@_mhMq5pdvIB+q2NdE>M%iV2wt=17BVCHNsVv1dS{iNTHp(>U$KYw;qDHA^6#Dl=T0*mdTY~9xpVDcHx}+Jv)xh+*tVYRbl-el7rBR5}8)b^|;hjcl0{s!(1iaZO>y2{CD2t#cz>B~~jIzck;iyX*30@CAh2uiUWIpsK@O<zgqs%k<RLB^oN;cMYVA447cSgPGhAy{rA)aIBLaf`l5ZAYJA>M{UTn>f!gvNz<fX0Qmsm6tvPMwP2@){T71{xRQb{ZGr1sWG(2MY0O6yn@=F2qCZT!?2vX+Mc+jt;e_&RgOVC_^##=VScVK#zgffWvW|_9@4XcnZosWgcwCTqd0Xrb0~fx|6YAA7M_B=1}HX4$Ql4IBz;Z3xPX<Kf*jrkGY&4sq9k}4fFb>@jok#5&_)+jsSb?eD2VBL+3hab1)TRI`8RU1)65WpKDx*D`;GZ8*5yM`)XW>k851a&!Q0jh(cV?&V~3JI~U?_?OceL*|`uewR0h!W#>XX*v^GGz|Mtu4GM7)6yk*%7vi>1+E3yP27hLh{u=8JjhPB@DHP(u(5~RZ;JijDW0XLne1Jl1Lm^HFtp!d8{t$&Yi%}*S`?A0&+fa!2pb#IValpA>MB_r-Oyfd45B;i(zU2kyL?Ql<#`$=+jdSuQ@N_#D;)dAfN^JKa_$c%w_)|Ogdo2p_7L-ZY51NCEF%Lc9<0!<3?VP))tvKW`;(=&?Ex0bm`adYdnNZ4L?04gsQvazCFN2o>Oxv7_?H&g2MIokZ7afz<I4)Vh*-?lCptHaM;QT1FaD3`ejxtIK=q7Lp@Tbs?;7`F-P>AOl<tI8n4Lz%IA#Pw}&1+|F0Db@+1}6PV;ZcZ5yC_@`G3iTNDi5=9Ogd2ELmJ1VHxzauCLO78H^iia6yA%N^t{52Y#fs|Ryd!XW73DVR346)w4K6Z5R>*$xDaB}*S1t1ZR419xWb1uj!Az}I0!N6ScSVICLN;iKE$LK6>etZn6!n$AKN)5eQZnR5r|1UC_EN1X^_H&5tIIHOXZ0+j!DNTd_?1z^p?WC5tEKrxCdg=VG8d@OnO=2);5kwzfw5Aonz8JZK)iFn6#6^;}DYuE9^i_`p%Zhx{YJfNeUm;I3~TVa4=%hi3;~bOgcj01Bgj~R=9(WW719v7qD|o`plNfBN3B!Rd_sN(!L58K}`CuEtRL*I41o@;bR)dq<0nWgP8Pdg?k|;9i{L=#H800?q=hdw1>i<*f}PBVN2!Fh)H`YJOMFjKZWxkCcSS<<$5-bN$Y|sXHtHAqH!T^f}HsP+ytBerM#Gcn79;jWfyQMaCs=@#qx-WFCkYB1YZL8gHm4XhnV;+a^*<yTktCAAn+>ichK|T@4!!?loy{OCT@vb`4HR^oCKx3n1q<PG;(DRaA|O5DCNb<h>5QtR}KeX0f#~<FNPu}{s*~oEchSrI_MDaI`A^+Mes84b13D-=ZJ~hAy+;Iw*#j@DKDlVCN7Iy83Zm1t`4QVSRFC(b>zx1;OpR_P|Ax#5fi^ht{e}358ePB2HpT(0lf@f0sae0dGRmA#9fdp{{(jdpMg?dJcF3H9CBqaxE%NkDCNa35EI`-uABtE2_6Ndyf_Lmu?;#AOoez8yb<6{;MLHd!K=Zqpp+M1Atvr+V|@nh1wIF*ym$^VaV6x+zTisW+EB`iwGk70ZLHsbz2FH@%8L^a6Q_fI4W>f81>Pv|7V!7bYvAv}Z=jSH-ykLqwz0kd2ZJv_DKB0?Ok54QvLCn_xGt3PVqL_<u{L;MQYV;lCgsOWHr6i{PC!h0L}AL0N1z`lTplrLMujOqW`u?-+z&Bnh{BW~L!jAhsk{m?X_Ug>AtpVg@KeO3nQf^|`H^DMwhAX9COxV!<;SDY3<_69Oqy9?%8!|$9)&{@lMYar^5Xz#4qGa(LrfZ@@G``t5eh#?Oq#`(%9I}|Che?n3S!b@3R8YO2K`Xs>WE3RDopt?EA*7YLlKh>R+#eRU}#QTDsMnc8mI6I#H5i5|Am+|t1Xo&KT=HEQ{gj+NslW``SCb3lfqvhCe5ZW<;QH$2!%%>CJj^AhL|*$!jvC#LE{x(jhHlA;a7-B|6@yK%8wM2_Ez{DV$u@|Q+_-F&7yE^#H863ru>*48maIE#H8aCPKTH@x5AVkb3+pp{vI)Dtio>)lV-D}GUZ2#N&6~%0Ws-Gg(*Ltg#Jh2x`;`0C`@@V2Rz~^8><scIs;6(lJer88W-Z`@Q#3+gA<{Y7ZahMDVz~8X+?!8FII$JRyYJPX@7;YBPM;Pr84EkcgT-x6h4KRbg9CW7neexX{p>6F=-oxk0K^bR+#c)GPI1snGus#RhaT(Rp>Q^2OuULq;L+zr2lHEOnLEN<VUx{5r|2bD@=KDIrN2=%AFCDc2xKnV$#zJQ(im`{aoR!h)HWIOnI>;^oGKN5tEKkI45FKO<~H58g!$=k%&oGDolBCCG@41$~_U2c31c~V$!n;Q(im^t)Or=#H6(pro31S`isJ0h)KsPoC`6jU17?LcIak>qY;y?RhaVPTIg#nm3t#54N~|7V$$;pQ(im|t)g&t#H4i;ro31OdQ0JPh)KUzI5%R_^a@j6Ob^|va4cfd^$Js7To3(QOXa?ZN&6^#5;5sTg()vygw{|v2VzpE!e)+y{;Kc{#H8PXDQ8lCJg0FXZfIjo1UCf#0j0e72V&y3$dwhrZNc53loz`pCVpjO?GJth9s;GjI0P~AP2|co;G5vl(52wf;K9&m;KASvP|AxJ5ED1Gu_l9?f*(OCFFry{+#b2ID!4tk7nJg1FT})eY^;O8Z@?p=lov-LCiWs%y1`!XIOuZlIPg&D3-D0zB`D>^ONfbE*;r45TY;ZIDK9=jOxzK<vL?7AxHpvYVsFI6Z*8n2z;D6hp&EER_*djg%8S3E5Kn-v1Wy1DhrR?42Va3wUc7>sxV??_EVw=RDU|Z!Q^drbkt=I~JA?Z`DKGXxO#F|Hbu9QF@MNeRJQ;ikxsvkY9Teh8(6!)6;4tWGa2WV1l=9+L#Kc`~tmna9!Ox+T7oQ_0?v7kp2izST0;Rkdf|&TdjrD8rd+-!!dhitRZ^)ID7k@(`o(x?No(vuX{Tn<6d>u-8@j7B+myPuz*aiLzN_p`w#KbP-N+;L_?hmEB*dH;m2K^RHIvY$mlk($F(E1AhftZxu8(B>GF)#AuFonAzCLN_P<;PLbg7#D%f|zue!jvC}K@TZB8ZoI$;lYSWyD5ADG3j1~DL?LoHd6QzVp4i<WHIH(e8`i-74C(Ybd183AICro*;9EWV$#tHQ+^x`J*@CJ#H2wA4@FGcUExcJN%tvC`Eeh#nZi#HlhS)5izz>Tj669);ogWz$0|(uaV)g3J(b5JCY`7-<;RK8BMMJIOxj!F;fP6lD0~Gm>3)SNKkkRNR`@AmQhIM>G3Cen$dh3T_d!fLPGQQA<Dd?EDo;jCsw+(SQHLH?coJgLV1>gFllD~jDq_+D3R8YO0PUdgbHt?d-pFFgj|Gq?M=BhGm~_0tlpn`Ki`Y|n3S!c!3R8ZZ3O%OqWW=O>6dr?^w3ouy5tANNnDXO6Xg7ubLQG2UjVz}8_zCjlXodSDCY_+LhIj%v50r9d9%wyqpi$Bpr6|+}Ze)~}Mri?U4YvLk2yFol1eb(<sc>t=q-_*#iI}vN!i^A<HdeSOV$xy?+Ypo5!Rf#@aC*dn;B?@Uh^rdoQPU_3p)<kDjk4G%wV-pr*59f^Yk{kRt3hikJO?r9T!j}SCS9WNa>S%76kdp!bdka{5tGhRxF%xKFBGndxGMTcJlB{iyN!|zJq_Mzl-Wj^0@cCR-{wN6fJwhqcq-y4`0P~ZHww>2Ogcy5orp<yDV&U$G)3Xlh)K^Vyc;p;9);&3o{K&be`JhBKBN4hv3>}?XOu*vJc8Z_TYsa^-GfI=g*Y$tvBLKelRi*55iw~J_#QYB{5#@%*!J(xhYC}lA3`%KoDVVS$Ka2^`M`M*-!;n5M%fBI0N!DgXxdlkZLsyXyU=^!yWroTzbkwjG3gzJqY;zFD7*tP=}z!g@DA_~h_|B8KR^#E{4-+Gs|w#md>4HrrtdhdxAAwHNDtXkzvmQS<L^C@<_FXFqpIU`)$ti(`tDO8J{O43Sl^A>XXEcgk<JHi!nQU-_kl}bTXmq-!SnFhD$qdiK74*Z^e}im_z-vl;`L~A1GI+1`4N*AP&fcFX&!|G5tEiwcs^p%1q$y&ybpaO9$@6?Tt*oL{Rr$f%J)WD4P6CpW|Zbe*<)k<$;MpVC`*j<peS?^c&<@r1zj7VOTeX#zm=gmqp|*|F?TddBcrs3)>F6&V$yQp8Ah3|(f@r0Ya1}tsg8Q2mB3%2&KJ;{V5;*a>X9}94>XF$C?U|33RkpoOj;gX!N&VWzbPn<{R>AS4uy6G)3%)04rv!~3!~IAN>%7*;Hu!t(Bj|{Mk$N^E{pxCg1=FnhR_<|hTsm+R^YEN9vz{Lz|^np=-YPe|3G|(KD!t?6Fkp2#uJS)4LSf^%ovk`Mp+4UgK1uD#M~fV2wsdf>2sv?8R9Rn&yAo}z@Zr17SKB28Q8Za(2n3wZ2Y(4&?R6xre%$?1-ci!$|!3w-$_3Km&a$eL$`oE7%%g08n;E9)7ZD-MhS&Z25-jsQ~_EV+@^)i9+2+;^?%)(`XAjxXyX6K)&G<7XD#X{3pLPEf8^4p#Rv482V;F}H*czr&^HgX{{hszI0*'

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
