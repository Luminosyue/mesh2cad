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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fb5b1704b464f5c94b667f1b630bb39/part_005.stl', 'relative_path': '5fb5b1704b464f5c94b667f1b630bb39/part_005.stl', 'source_sha256': 'ec5af06e21435cdddcffa31baedc4040c2243881e3ce5dd9374e546a4f7b0ca2', 'input_faces': 804, 'input_vertices': 570, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2733779847621918, -0.49997636675834656, -0.23355217278003693], [0.2733490467071533, -0.2603157162666321, 0.1695922315120697]]}
GEOMETRY_BASE85 = 'c$}r22Xxd%^zLP<siBzOmJ+~JgY8fQ3!#M;Lny|fESTm5f&qg~UxVo}9aD{$UJaOLO2A7solrxlo6sSELkZRJH1~emNV9tHyz~Ea&OP6cPj{|HqgjolT?lHGF_VwNe@ZLs!+S@i1uBY&oQjV!yw8w`u+Tn3tNk24!b{0RzWAf*+_oLt1a<LJhAX2g^zJh>bV!A|mJ0Rz)~-;+QlamlArV7*{@i2GkluZS->m0=p?y?;X#bw!ebm2K46Nl>#p3T<#WKe7Km3zj?Sd`KxbrEhx=tPXU8pkZ{l*kCKQ(flnQx!GeXXf~(QlP$op}RRn))dh6HNU^t(KYk*P1Rc^+Wd0H}&rhiZ%6Tb)IJG$1I96^`}G*G4*TL4{d1XSF{f@^=~|$XzE}6FvZmGIAN}-e=)~=Q@>u`rKbMAMe(No?C(~X`fCcTH1$Ikt}*lNi@L5g_1oOup!co&mzvHuw=c~%&6nq!+n45>yN)#9+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5+`cs5{u^iGd~=_7X}-CA%s1s!6ZTKkyGC^$J=~OH;@g8RuhaX^l(Lu2@-<(}x0fzKzNOxZ+d>_e>m6xm;yY{ZJgWC?RYsfUYrdTCx}BMPrE!VFX1>!m&QQmC{`M`ie9f2hEiJ>yx77J`(9CyQA`NwH^}aF9*L*qO_3ZRb%J;kNH1n;o!G{d}bgePX*L*qO(#4PcI?*YneoP%>KU-!u&3F4!zAJt14e~2|v){~jrWG~z^Z7v2e9f2hE&bnIr|n9XeP+Jn+#5q3%e?dE`S9g@CD#w++n%NFHuIhP_ZaF}KLwcPYrdRsi9A4`BioIsyUct?+~_?9f8|2+eE4#{QoIc3?`*xp%vUBhNH+8{*T+B1@-<)1w@jMI`73j8GxJ^DymlJ=Z9UBM;mi3-<wsX(|7DkNG4qwyhYfYC#Sfe2YrdSX%x}&4m&<Q7^DT8JZZ-7tV0qJg&DZjkkHyG$4BF1u)p=F;Iw|=|t;Gur{?(Q2k9)Pw)DO)br}vdxc`uvgyL~yod4|ho{n31_KlYwaelzR8?0e)({rB+EAI+Eh@8Qe&QvYS&-Jdy!$d}hI*>|r;@a6SO_O*P=>g>l!rS(hpwe?8z<@HPU<$QVll6`GG(tLUSl6^T}UcY2tTaVoRl-4iVm-FTIOZK(($lXtA{gQn-UtYgFe5^<AeoE_?hcD&J>zC|n>yf*k()uO)a=yHN$-cH8xqWH<l6^T}UcY2tTaVoRl-4iVm-FTIOZK(($n8t(m+Z^=^7<wF+Ir;fr?h^_zML<wU$U>QM{ZwQzhqy|m)9@Z*VZF<Kc)3c_T_we{gQocJ#zO`TEAr9z1{^iPo?9L-fwvLc;1wK?RnF~$MdE~9XxM(_;}v*@bSFq;p2JJ!^iWchmYq?4<FB)9zLEoJ$yWGdiZ$W^ziY#>EYvf)5FK}riYK`O%ET>n;t%%H$8kjZ+iH6-t_SCyy-d4{JiOL-toNY;p2Hz^X2y&9=<f+<o6pMzBJ$D_ZuF*G~eX+8y>zi-{kij9=<f+<o6pMzBJ$D_ZuF*G~eX+8y>zi-{kij9=<f+<o6pMzBJ$D_ZuF*G~eX+8=m8AoNw~`4G&*?zu^~flJxZzy1%pU>FOlSYdJ;jUPSS8ZTN|Uw4dS^$#>0adV%U~xqC>cr9#AM;ah^!*)R0RVN%B!@~xj&@$+ukEmYr<=pf(zdK=%jI-FyLI?H7`Lv^+#bANJWr}^WmQGk5wnvEC5-yQWX9HDj%YqQ_xd)lwF`DyB>V`)F~ol}#jj%!{1<<y@ei`hTb=Mw$B#HORPpV&jj{4#UtbL1?2l6+U^FKEA(9y{oG?U{Yf(tb0p=lm8^?bLqzcjP;N%uV;n&hl%IQ9s{wCEt;<i|@PreTPxK?L)~|4({XQYLi6c=1e-n^?UB8d`rKFb7((apSZs7Nb0|<{xli~`;;u_Xgr7Q=KaoCLg(A*TZ(+=gR}hnaXEv7+7%s1zOsPt>s>h(t)cCWmvEi9o17mOMDx&DA)fP_o#*~XmRe8aGI1T}kGjo%NW%rx?{53q_vv|s>NKB5>#Os-16-$DY3iqK)hrr+M}U)jYtmDyV+&}UNcFB9<NTiI`1zyv+X*y|<?pfIG!MU53+Xa|@+)Ngjrx0cJo)yJKNAhUZ#jMrUVb-;+TF=RzU4#`=U?nIjOT3u@)fT-{M^~pcQ$P=Qjq<SDLmhD6dXx^&sm6kd(>)v4nDqQJdIDI;=JF$F}&Z3`RTf94Jglb8oKy->O`Modf!&KFx9uWjM+?@i2TpHxXzv+8h>Z`3hZzGmB(RjXdLxpPDS4D^}>98I2C+?+TE#4zV&crnr}+ci|eV~<tpSm(w_3?J^So!lz+S`A6L!R{JCDANS_PW-fCR`!Y1-<-+oEgJtd$z*Uz_v>bq<+jXpl7_Ko(@R4)<!j5MzQq|sKrugpEb$GfjQ%|oR~4fZ$erhFw=9U4zZnm_yP!uUKU#?pMYcMZfi9OC|5jYu;1;nUflzheiVx3Adm7|Y|c;QQAHbiU)pFZ?;}xF%ymoo@|g-}>)pAAKFi*eK4=QmT`o{=W4*ul%d=eP*Lt<h$z5<T~{}6xRDz%Q*6F-LI`k(fQgq*cQ**uJ`Rnm$0AOh3Y%^!e1N0*D+h+h!magdR~;rGrDsekAH3Um#!t>Qg9W`H_f*uzToTmwwhCDzvb)j=V%A_-!g11?>B*c*TR)N&fmB?8T@)de7s#NO`tkC>hW=9>A?QG>659SG3?uKb|T-|YRfdeuRLi@zWqWp`L1;KZ4n!&|BgnDX#Q9u>vR9}cjY=>!+)W6Y3#ce_2&L(7&Vi&hkecGtJGqi54URZecI&)+@I+@&z=2Te4T9Dko#kq!u?OqGMDNnH0JzXJP(zRuV`IU=6u8c!)Kh|a9=p}FGmyh7o>Ckff#xZ<A`D3(cu=4=dBHKe7x*CAKv5n_V_lx?}}{7{+S1ST;m=Xe0vA>?ct5-{>>5AjK}9p23}uwc@LrEY4k1Uzs}2ktq<heW7_cXW@O)aAdT+>{l90wL{suD50X~X@g;QNasDEJ^9x^ENPbKw-f#Oz@|DWA5%l-4U|feM@qTA{kD}xMi+#t{DdgLNW{%YR_LrP*{S<ESwK|rq?fJUB_XqalI<x;*sYNsno4RtHCed8~@8U_+?=QRYc($8EzGLHhx=tzy>|5{c=lltw)K7bQ4_yB*a{k~0<U5Dkcz*Wa{%h-|^M_vCpI@IE@?DqMw=S{qdfGpA6Xjcb^Ee#tOTP8)_|=r>--q{mxEuNQzS)*g-Gsh8{sSiS@s@f=^VylbKj$k8*-v)RIB33o#e9RW#IUc7<b3N+zs02K$WI@{>sr;Ih18$a0epS9&--<Dp1}99)`7fVYXs#xdbL<Zf8WEta{JpWhH;a8SLDhudfyt>|FT)WJ-zS$+g~+jwBFawmo>ID9hc(&Gw0_z!}D-;sV&s*`4HZ(|1hefUf<|_g62Dm`0#zs*E@OLY%`4W-#6g%)&3N%JJwY8mBmTq+Y-jpeT%DRB+ru;cgc4iKF7~@Uq<nGPHRQ$yJPW^#D+RwsauSEOWMAj`h4YsH_wNOV`+VKE@R(1#mRO2eNXCrrDYW7pWI06rgioR&QI%3$7OjOvDnPl#!d5;Ib99DbHYd-pRa3BeWiXV-Jjc^kK*I)Rr+`RdC`3PzomZHpGVDiw7$aQ|7agQFFX5>#yFHS<ZHe)hR?fY?Fm{pmA}|`zV1l*Hft<>uI-n`us^iw6~lZ;9m{^pRtDc{9moC5Tax#?KYoSYw_Zx%`8H-J-{)kXfb0DCyx)Gq=sC{OW-|K^e&PGKZ%@;Gprhtgd`{o+bKHz6yGWN!<N1)WJNeEb7njlgp2xDkEtKnrte(aFn921^$58(*@xAGJ!Cq({Ums5R(R(mkaKr6--|<s5^6k?aY^L$eKA(@PB=_GvKF{NLzf-3fd{@K8od0S!_w#x*y~l8sTgvAvX`><EUML>djhp1VnuODMI%cu2R61a+pKY1Jw~fq7>x=!P(bv{T+1J)($FKxrzBYeCmUI7CV!x?N2B+wJcmAG#O?@rj+GYih|DRd-J?e+$^ju~?wgT(m89v^_H+Y`UTEqE4b!hw@JIc~?z0!X@e_k4da-FCe{Cx2z`xgI8l<zwGZ8Fsl*?{{cFM4lm*;J4AtF+n3e#Bs^WBK%Uz23JL%1OTc%>$Yb)?@5DAGN>6pSSi7GheH(`PMh>Onql2bKf>S$kew~ZEK$YriH<GG~C4dz45)lckYINXEu*drHA}IV9iACPoaOvcmB|RDQzFWmGh%QdH%QmV++q0_+hDB=iAzg^}Z!-KcBDPvKxGR+hoo!*n5%Qw;i9$@1I-e=lMA-i9e4EzvFR!wQRNCw<hf6`X8q9eakcC=a|Ir$p<IS<@vCU>$h&e@8{Qy-pcb~JNw^7^YIR>JzMWv{u#^HfzdZ-nfdl&_vk*^aglvjS3CR77tPZ9mPyUIpIHk#sNctS@O-;6mEXf3OP)mS8t!C2+c!K92UVX#b!+V6^YW%De_y$<d1JkAAIrY8)55lTUz_K0zOwEK)wkB3$m{P$_AOa=^XI5|e2s=W-*tWl`*ZWw*5|uimAId`g6O!M@yR@%e&aYlDQ_>m?~E@&zN6RtwFcjREsw*CTl5~xI%_xgGy4ZVFMss?$>6uWz~fvhVW`1RJI3d|`S#%kKXM13$E$-z8T`bpyx;G~jMV#<u8Ca#R);a9+4k^p6+XiAwsKgc-d9faW&hN8I$z31_N|M)rt!Bfir<)`^PM{i@%egCBuVdE|K7^;v;C`NgFmYzkLR^oJq>j*o|<nRwwLEaJ+ANQcyu=X{Tcg?v_;&{a-$-tpBq!S{@ZN){o2@AI*<1F6MS3`(v8>2kh6T=eM`{yfXe>UoAkbY)ML({eu(STIM3r2_YZ$hw|F!4$2s#N*ExNH{bGgaKFvD*68Gm`7=O<gIh)^Ow7$yyfAx}&YfB=J+wMQO&dM~d<M*gVL!EC+dTyBi_8Qj={n32K2KKFu`|<V1&+8P8Q`zf04hw7Z`n9$my~ne=Zu5SNMqf9K&-nYCKl3Pm&-;9}jsD*6A)l`!CvWKYtNE_Ij}3JkT^?~i`^}+zSGEjvpW|ro1fQ35&JUYJ_sO;mfAjbUKQ+{MEq%)Ui8{sK=Qb<7obqNqW54k^t`o4mwcd9gKYQIUKHksybFuHL!FNTo?+P8t-`8*G#rI<oX`EklGoQyCaeN=%<%OZ2wtu6e&3x;cQ1V@^UUEPCCGvRom`?q-9(`%ZcO3t9Dvf`Q*WCXqDbycrUDkX{wpo;~_^0u_D*G>=_ao2PACY0c-go!2aa&Vgdq3}7`mbR;m8cT@TwL%C*MA(t{TYA2;JfmTAYb|6^BTQxbFJcWD0h$F-_At-nyHlU7?H^5(fh5TKkoHCnthkwUQ^%JU=Po$k6n0tKCo|zIAF-PM!e(xcS+`P-jhz>`)Izs$OZl#g0l@>_v}yMkDb8B`@RIfzlCqxu#W5dkEU^O_I+<0&t~1|`!#FX&+Lb<<Ks;`Mei##U&%b5>xX`xM|Hiu&Xb-!O1|BBZv?fAX5ZT65#LY7rSW_C_w2hK-lBZlFO%s$L7AD2eEUy#`1dn`E%<)&LN4-^lzQa55*$2#TIJ^YquR5d?J%7$yI&s8AJv<DyYEaoUy65r-tW@S^t&DF^}BQ*qCEBC{Z0wJr9Up$*M-S<<mBJ^ICkFV>%fd+hB}UEZ)tt8Mi=M(#`WSl7ZiSed0*U+Zy$7L2Jg27`!5b~|L^so`yXd;DIU)X1^9PI_viBOpk|cg`a#*qw`88Xm-4fI$#t%L=5f24ljn2vmxlc+ucn2Q_N~Cjb>bQSjwt7XV|w3}5Xb9y?kIY1?+C8QevW#)-<1(Gp3d{^J4TM<{f?b7j{IGf4EuFO|3mk&w)K_ye3h%t_dhMR({<iarV9I$UQ!)L{=@XWl5+|B_T~J$Da(%TeEpwM)llCSu!j2Y$Xbo_2dtueYf%^7x47)pjOXjs61wlQ53SDo4I9e8<GR0@d{-YoL%y@j8>ik^qDu353=iP%TZ3yD@-58+52Tp*wly2+d^ye=eaGOlbiCFhHF-RbS7kq}!#2Hd4SdJPHSa!s52*MB@bSj<;C^0moT2UO1B~;n@}=W?-w~D0<Jrrf`&lNCkLyz#K3{n5b1n%qjzg|nyx#&}@qXw1%Ac=<()8ZO8eEtCxgU5wB!8lDbNVzie(t7q=jVuBO^xG_?H={t;nTvn-@Uo0zP(Q?9*0l&_;*(AoTv4^?P-7hebJrb{2u8R{QGu3-aBDbU&-2@kN0>8pRYX4sgC0v`_{Ml_&z5?3$9;1nER8OiPynfm3ZF9hH#yu2l@KEJdNvg?#}tc*71378A$ocdG?)|_&L#4V?K{t^`6rF96)sxdvDHv=}X7!3jX^f*Y8KZCDg&|*XCMuT()&Ta{rquJU(0JQyuH!!JMCbiPzKLdUF4F4&nOk=J9#V`;_|`JC^6kqa?omkBvW-5@h(-Vsi%Uf8tkOoq=j(Q+$-ZJ$3(7Oqeu1q2~WoEG*#v>z|6%_6zvm{!_7sY9Ibq;}JseV`v&!=qvDJ@Du1;@DuQJgy0v@_uv=cf1w$?n1$v7ixB)l;SlVF?PI`R;JnaFV4)wudBOdmxic{L2VaC%28$4!4<Wc3v?f?+0Js|XD}>-m(CT2JwZN6Yeh9&V&^q8ia2056a22oxS`};oS40T*ht>f5gMFc2f`$5keZi%nxxl5t1)%xC1;8Z`g3CcmfrXX_mjf4pmH`(57lUR87XueZ2rdN81QuEtTnL;2S`wTYnhjbKoDHl%vw(&E?ZvEs|3wIXh7kM)>H-V>11$7U@Eh<Ggy3_~Ghm_Hz~{h+5Q67H4}*oy1`8bto(CR_5Ihvx7d#Xk2JHn714lxKfFr>@pe?~Yz{Q~@z(T(S7Y7$c2+j@756%tF0?i5*nh`8CU181wF6PA{_@l!55-ju|@JH}F=rgd;r(mIPz}dW5Geh5iMF`FWeGL|>crl9*oC6^^5A>75oCjP4`WY<r3oqsxP+#a5V4-EeLd%1NRtEcm1EAl61HkQ}HgJ1zFhXz;^gD16I11Va90i^U9S0Vg4BiCY2~7qIJr3RsJqA4vJ_bGwJq11uehs|=ehq#Fy$gN?eh+;Peh<!=fz>Mmv(PWVLW_chmIY@7=Yi$~=K&XlW(5}ndqeYry}_TnSSx@<2+jd7GdMG@UpWwhKYOt%U=f0!LdEs#DMIiA=riyG@HOZgu+S&qYv7a6b6}x|z^kAKp@+Z+!E+IU*Fxukg^mTU1t&m<f)l_a5Q0OYVc<}3I5ZL*4(<u<0d54X1MLA8S{z&loDW(UEHpPbAJ_+)1uV1}*aw^wDy~gAq3^)jHArwpXeDSiu+YrlN?>njCa};PU~h1Cgx~_uJYb<kz}hva077se)E6u?04%gUI1t<!8Vv3X?t~EB4jKe*2Ob5D0t=l9)~+dnM?;;^O<<ur!P@o3i4dHM5WEW^cq{Z6Sm<f+R`72K!8f6=!8gHIps&DJ!0({%!9vA#<Q+5*ScKpY(1PHHUaaX*;ip5r!QQxjq$331hl=aPeduTSLZ5<#J^<ebzd#5+3%v#wdJ?RC{?8%=&xala3!Mv|4~|6$j)$%V3rzsWgU3ThfX9P-Lqoy6!Tq4&V4*$1{lGtZ{dX<+5h1uELU1`~9k9@R;IE-Yq4~f<eZWF<g0;_fQG{SWgy2HZN?@VhV4>N;g}|kt1;C}i1)+gpp`F16!EK<Oz-_?YpzXljz#-64VC{1#_-E)0=xDG|Cs=4Icp7v+G!?uXdH^B#SA^gcgy4M$!F!>pV4=Ifd%=4Uf{!8uA3+G-fe^eMAvg&kcnfqZSm<xyE#UJA!50vMZ$WQ@Z-H+^uYhlZe@6(u4t)o{4!#5Z0KNnM3nBQP*MHZMdkDdg5rQ8<)4`9xZ=v_WZ^3B@!7rgNz%Rl7AOv59o&{e8Uq%Q%0i6#%0bYs_9ET9R03moGLhvGl;Kc~ROAvzRKx4skz_Sp7mmvf@)L0E&4vhsb2gg9;!9vG_W5C0qy}`r51EKxELVpAg1V<nQ|AY`c0NN2e0NfoR_<Mxl4hX?55P};+%Yhq%tzQ3K@2m*H^$~*WAq3Y&2(AS!3a$nI3L)4ZA-E>g4_p&m9U-_HLU2`RA#hc21%%+z2*DO;DX;}x5+S%Ov>>=FxC%mWZG_+k&^F)(;D!jn-$0vyzX3N#2yTWD+!P_W6|@bw6}UA*a9e0Ma9eO!gy0_#g1bONz}j`Z3qtT9gy6x@8Q{U-sb2qG)2AW?|ALTtI&?pHI(UlLe`~-LXd-wDcrtVYSm;Ku(Dh)U>%c<SfQ7CE3ta)844wpC4Hmi_EHnl@2|N)YcmhIjG;}yP8f=FS1lz&Gpb_A3^;uw`8bhFiz$4X&R3i#H3>=Q_QM$Y+v<*jIIJ{w~HxM-j!iz-PL1;e+p5UQs{H(@c=m78tH6qj)1sx6^itVFxd85#FDDsBF8;*KEqsGthBG7gK+7EyyxUd?h#rqTJ8L+<^57ej$y$>#o?KO3IHPN;(@(RPdk9wz3<21YnXnO|j&%hI0P>qvn6oQ@t*HGi08h+5b;DXrhr_1w0+k(g|2=6ZHokWe3@b01QDYQQYPq6q(;<y?GpeMl9)wrWZHRxYpA8fCt%d3XAKFITd_ZR9NM~&m~?x5`nv_An)a6UDTsgWO=3a+ZgpK4Try1@Ccy^1cc3fksFUOsp()H{Y6$Kd^mwy9{J3QuqzHIAr}7kU(2S&iFjRD#|D=fU<$y1Ytgn+JJ$;N3#KBdBo%-fgr!iuOn03C^v?AvL~$9tQiWaZ`<o&>P^~*j`bWR}pP<BQH0+8>n{(H4eeMiMEH){xCejITi7HW<|*bJqWI##&tEyL$85zVtaXAUU{_5iM*WfuA!b2HJtFSqwPVoKL}5-_<s$>zxm1mO#y$Y#vf{wgI)z^$M$l%ymDxp9eLT|T}8bEsBr+^A84C`_9^fLd#mxQBEIBf-48CS#_wvBfnEW7V|y80UKzCYMxHmkE2#G?YWxcCceLG)_WR)p&Z5R%HL^nYflI4#Sq%&H5;zOCTXcCAw9SINEbuO&-d@z$3-2=8?nC>1@C0X4W49Wap?kok)VQcdN$3S|CTuUM%PWbtnUI$W-UZa#jT*b*T}0bGXuk)ZVDXA{ml_$N$>0)doL8eb^fzz@Y%i|MD~`4qke318Z>YBmHFm)}kG9EZpA1j1__ITyuLnqXf{UqfPK~0_vtR|=i|X=<qOF2F1>RZI+kqN8;GIL;ooK%kp5U+42vDOIG!Q&ajWKGBg^mV)h3#W?d1KM`E989zZ#3!!phf_^F=!iz_JQyO*H*)>MjdE0xSkpl)Tj#`53Y^vb#-}l(Y7}7YQr0kdUn*X!<&G%(P$qHPjG!TV$}E=IuR^>4=`Dc2GB|1`q<t;m)8Jo>m#o|yh*4RgBmgLCZp{{w4Vr%e#@Z76g3(_r-HvxW4aoRq0_)tY;UZ~YmBy5<XPcOL%k`eF$Laqw4I9fQ{f42qQ)<3G=;{3o2xNXjb_jp;3nAKOqbUTZJQvk3A`Do_X}$L0&gbT#-e>JJi#s0n5D+I(AnTtYRpxmC3FtB1-7@;<+ViH7RYM>Zw~6sLXBDQ=A!Lvw4V)6aBDT@snG^HAN-vf3)E-}jRUvF_O`mbwrJZLd9C5aq24^ym<MkG+RjJ&`S1h>sj*OvcF;xO@6}kMMtkUDa1ge)*X6ZG+aTlx!CQ=a3sGYsyd`M62<;ca6Wl?KrD}A9#)CVnk)TE==rV8zZ11GY>x8x)kk<j;GSpj&8cX3Nplv+b$HNmGtcF94F3{!RAJkZ>MhJ8TI2hYQba^3Y8;rbQcq>rPff^2YE75j2+AoJExT_kg)aV9X4ep`FS~a>u*MPfXdv{%4ceL$_ysq%ppx!FfSOsq_+O9_X)$jz{)L5rRPw0AZs2Us9=mp&XwqbiOU0yG=wIR<2Zv*PBLydLtHlpo%v|kTTaBnp>snG|T2=1rG7B%`pH-md)dtY5%U$pIwyx#COquwUe*aUA2+9slXB0RzU)!3>=7&Hm|lN#IA_z}7d+#lP2)aCt%w*8S8)XFP^Psab-e@*`1AMs8>G5km6a!cdS)buT@sf)JzM{7Z?GK+ga^+qQHJ%}$7Ge-G8#zD%a'

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
