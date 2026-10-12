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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_016.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_016.stl', 'source_sha256': '396584349e2a4e882c12dd3d2d352ef7d2abae627b4f4a0562cb8f9089779dd2', 'input_faces': 790, 'input_vertices': 466, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19996227324008942, 0.1643330603837967, -0.047602660953998566], [-0.004446983337402344, 0.2505083978176117, 0.17384225130081177]]}
GEOMETRY_BASE85 = 'c$}r22T+tr^zA=Pm=os2s352)Di|=1t~p}PIx5ChK}1Z511gGHF`~jKn8gHQ#?ORe4!di{S#@1?4VYGUO@I2H!!o>juj<u%R&|{p$II>8xBCkNmfjt*=P0J(Pem<y>7Y}!+%!#%{8}+BaJYZK=wZVr)*SCQ)lMrczWS4)5uJN>^6qP=1!~h>e1=aP=I_$b;L><R0~a@g%Lrfp0RJK52mAW_3|D^ZA!8>FPxmK|8saxR{cBgxdiC549#!28GYtQafAXf6U>LY2<wUyb5eF_eOIPFDYzay=k3jK_3%tZPpLiUv)Y{xnd~@z2;#>c;7vF3@9`Td6!f*0e@>u`rE50Gx2l?ORka%rKd*o@?P<+j6KjIfPKs_(cif?)xyHBa%mM8qD4p$`ZNNLp5&jWeR{vz@Erww~;edEsR5^p&4RN^hEwZ+#u&5?LR;RwlZjCDtz=MTlV{J6eb{yx5{_?CK$5$_g`{PkRs=jJoa8|$`9{OpxcXQ@cU_uVadwCm;3hp>%^w-%Fly+=9Z>6VD~_6*!F-#4H%>UqBn@!y(lmpoCW;D2yIAJW!I-}H(lG4IK6#7`T!-`2Obc?JJu@9nm}7LrHuXiiDe2fbDi@l8d`!LOvtdd&%ikU#Dd&O@^STWozT(EqA@e?9*#()Yg$!Z*}H|L585k$lq%pq>i*kY{2W$z#l!2mAGBb;+aE-5w*~A8rqS(333vF)hu3{9dsVZ!`_wCjBjz9sA{wP3G0__K1;r2L3oNe{Xjj=d*mnEWUBoMdW$tCV5QJ-^DloQ3HMM)=BnDtNcxTy<A7+X*Xl9t#8eCRN~FM3Ps7+K3|dl@^kd_$?%O?{AH0?@1=UuH+{<&<WFpl{;XRp`(hgVkNBpk`6Z8OMRSYvHSLr5n)7*_+tkY9o4r0D|M{-i7psr-Qx8o;{=AN;r&-xZiO=;0@w|?Vzdl@R>sw-KO1vf5U(S!I?Q5*}%|P^F&U!iL#`&+1e|&YE|E;fOzqEoc(a$n#(4QCXYvt>k&#^B{#~@G6T+(M#ark=AQRqXpnmGUWo}$iy!%=5q7o77!f53O$h5SBWv0nO?Wp>!#_X}}8M?6B`ERS*jaWzGVZu=ec4sl0+Hm!vJ!ixAJ^~5)R4cubu>#tprf0&2tuj%ar)HCW6_BVf7Iafvx`qT4@Z(hH5gRQTRZV7*1Q=I2X_Yv<Oh&tCcz`O_Vp`Xz~SZ|IKGOsrKH}o^FJ<fxd8TVWImVcXKA6NUv*!udI(>Nz-F47<Kf}4oXxZc-3377rsdL8jjL(rdr#-;LgiL02m>ofR6HQ8TFpDXb5g<-!M*OYlPd~=2N=x5gf7F*xit{d_+h>fz%V}3jpbr$H3{e7H*{scEc{Gu-NMSag=UiW2~H%D=ct#97B9OrG-+XGqrgMCqt?|8W`tb5PEuU`Q9-40EYet4e7d1%i%I|ojea~pUHeyfV`uf;W&e1}e=Z$o#(pLS)5#5LBj-kT#CZ*48}&NzYo-$#G6ZRh65_n$~Y{F3aruZH^I`pR<@_lG=Qh=08T*H_^~=)<D=@Wb3ENxxPkVqHPa&<D#A>BE2i&&v@1wx!H#`0W7J_3`5+>Hn-Ra;`FbW40Ka&umxZzM-#+hwnWa_u+ik<vOxF*pGU)PDTExz5$Z=k3Fb=avxkr(Pia4n_uoiJtr$6Psle}uhDNOudg`F+p0%|t#8VXc*~m`a{si}-H!ST%*MP4PgY2O4{t^O#<(s_=O4@c+}LCb;!pB^-gf&6d>xB@ypHFKaqV&Go8B@8^SZad^;>DWT-WCF8xh~)7_KAt?YNE>N5hXThWz8A<vOw!i9$Wc{oo(pB<I<5YaQbMYKcA+t}V|~-LMAz{2q>V8D7abv<zL1JRucP&$A0_q`s#s(YGgUaDH<CjOW^}2&}i^9rUwX^J%ue>C{H#xAg2F`Q4Y}eD?Yi@s^JbviKi)z07PHCf^^w6m_QZec*VooSzI|OMZ#?(;eixupU_i|IQEO-||Y%t)=Ng)c<QIJeS+emFI%lya09f$bC)Xb5y|n_SAgzZ9!M`vqqVflDBm@`V$+6dAk*rbEv1xMgEv`@MFKtmanhRM*N~@IG^^8a-TFfz}FTs|J8YNf3~g)#dZ4mE&SARa(=ACX21{Mko7*cIS77IFZ9PhSniWn|H+uQln2gR<U72_CIq6NgNGr%(|EbRncDawPqiti|9K3a@4x$CT_vvIdcV{f*HN88$a4|bg?Ub{74r9=`lD}+{P6q=agpoM(7X@))bF?ttavZ)pO&^gQD@>^+;3mp#CxoFH_V%HK3!7fJex<fL*Mp1Ks{?t;XV9C8|2Ryg?P`7LE;~5fjWb3<2>{;#@qUqi+^F>sFQnbeO>Q?`fE>;>(LrygkR(U&$B~EiBE2fJcpCu7p*4e!5C2=>$-Ls`!)UbR;jyWJ=9a<0pe5tm~HEuKjp)9_hrZmTi@8J9_n$9m+MiF^u&H$n}u~X*_|lgSHT1Iy!ji?@s6eCdN*vUjrxE5hQ7Vt5O3=n`P|VzUc%>sk?!bowSUl`4&HLT8-3lf)Tw>-z;)+Y4S7~;I1j#4@OdGyD&J!ppw74usZ-OPQO~K|IG?YA@VVezCHUblQRmU=iMGCZOi|o#m-@>&*Sl4~dOKD?Kidz+^Llh~%sbi*_0$QI^Q=uN1pnENEZ3tYZ|*Gb1A5HA@?0=H{Bcfv$Dvqn)J(bVEKk3RZ!Q+X_l;+=@1`+d#JBRkq4^}^y`t7X;{W&l6L}o>+xSo7YYT2*y)NC+fAc%|i4(It-%YL4Fz=BjI9F?D$@QgodL_Og<Nos_S<a8K=L`4_>)`h{%X3*f@IZW1>{q!Sja|3mIsW|)=B-=|=g{|*oPSHP>!{xqpQ8=+W+MLX6~rHWhd%rLE9cWZ`~rMF2eoOQ@|-e9M8Us&9p@n>754$tTKG$5<GiJM9h7;htVaKrJx9FLUveHy{X*g2uLHkoIf*xK7>PXog|LsW>?GdOx;Oe}Ohf)vl_lO%sU!R;i;$;}ulV}0=2-8M_qbn`>xp^G)y-1Bu~HA|gQ>dvIos>VIH$VA>&>fVsnhaeq~y2WD~tYzzCoV4?J;jePQ(vgh0j6D7KpFC{E{s7%&dIHwjT5Q&*EEoU7P#+Nj>JBkCL<O@6c$8w=VugeC>E2#P91M`Hcx@;V0cfJ;5s_kM&I)=H=&N!^G9-Tj&<V^K<%t*Xc5g_!j#{$Uoy8uJ=Oo5MOgAex49r;gHM|IZJ%A3qCI!JKV*3{|Z9=xx2$J6OR5L9*B58#|_^3B#)uV0MyC%A3ghW?0afw@s0d>i?vUztjqAU1M&>MfIi=gmONVhR)}|Mhx1U*fI5FKgFcrojr06%DEjPG1nbK68h!in8F`Z5ot6Ck_u;xY`#|b3bbT$pUcEKy*^+?#H6Fv~^U+kY7tVj<2jZLf-fNC;C-J6f%f#1OHbQ^8<vA>WpK}rBy)yzo_lR^9Uu!f7`KNr4{O0<5B)@4xdE{|=g!(;;OT6{Q>oc;C3msACg7-L|`&Wvuy~I9RZ#Tqx|7mbg`g8MUisT;=sZ0Eo65?z7+FZc(*;Rb=fYe0kvvC08Ykm`7`(-zL^Hz!14%9?^?>O=GQvnjM<#I**s|ko7{#1P9!}BL(-uRy4ThHYe-*hlS;*I6p#5YwbgL$L7oRmC|3yH6F&yD;g%*Zn-H}aorD)m?j&Jtf+_s;?8bGtP7;Z;yizRU3Y&qh5#Z<9m^?mB=zA2=_4tLlOH`H}FWuZgdRy+@tvOyV0K{Xl-#PVgNEBY(9S;v4P5q#omre&Xwmi^#nCleJjat+wJ@c0a;;C+nyup|bd<F2`kF^SDpq>jgCA-@6KRCN0IhPM;E#Z&>Igc`V}wNxWuyn1Jg#SmHJRlc;CpeeunIuExF}ixJ=a?iS*g{wDFpZFQthbKy(K-#f=e*{>ICu<wq^;#*s|VqaRElz5{#T6}$S^$WJ^GLH>Nu<gIOTRqenFah(<Jc)jeERA_R`e5GB{x~O}Qqi|YJ&`AM4E80eKKAR^_V6FC!+KZW#5sT568Y~(VO<X{pr3(F5dYSM^Zaot@&`A>x;nl^{Io&v*VlwUazE-na|eEpQsP^#`boTDa$oehe{u9-%pb_pdnEc0^>4hK9|wDxS3i3KeG9k^f6`$10UuE3^k2m{9X>6-sdg>wd-?O?n@3#2xpHoc{M$|=&x~p~=bikJ-|ZB9XY@yJbQ}HOtBbGK8-hCP-NAL#K2dyY2Y;NyJQFeR`^~7QQFZj;Wp(7494o$7{3!Cj<b7lPO61uTD!%1)Rpjq66ZPCgymo36>VG&5>v9;6eJ}Gf`W!M2buOBK{Jh?ct9|0LoHvh}60Z+$g?h%P;CzPn!MS?=6YBqa8TP&0A)J#mBkFV+Dfvx_#c<Bus-jNMmDu05xiIgQvY2;q8v6Ec5%hUf5#&i;guZQCi~PO?;k!P~avm~#eZUyhnY}Xn;M|z^@KnqjG#~RCzU&u2?knPR&O_f;UliYTdZDb#`uhsRKZ+AybM{QJty9xBiEpku9sQi<hV|M<BY)6N%=^=?sHbl*@=SKXyuW#3-~A?G-et$IkDqrT&t!k`EhXoo53}Z?p7?&4cmE2UpPw2d&-KpY8!Cn(f2my9#{*Tw*T+7_{Vn!S^m9-N_$9hwA6NCj`FvXtd0OYkc{or2=WVt<e0wAEe{e<LJU{G{`nO!hdVgMy`|zQ6;u}UrqCZQTAiv-JeYX2<9e5D+glrPuym39w`9Xi&S2aKQF_E}V%g#jpeFMbTc9cRN+Kz*ty)p7nssaB}Ec#j619ev4kNo|+;rgmr3-Mo;O1#wz{nsuyBEHv4<k^20^{mmvH<rJKK3w%f{NqP^#oz0Wa}ux{{=56)YpcRge{>?&JL#VI=3P&4p8JhOeBD#x>!xy;H~x3@O+PNa_51?NTl5Xq)h}LrOV3|$ejW_NIZ54zJlppne&GVdFOCx5)FBq<fzNki(GAG+@Hx(#X%_0V&VWDv7V;EGLZ0svu-;uWu&y!H(Vqfik$>lR?0Z@X#GmaczCquHc|W$nyzP3R&PrD?@9`a&_a7tX4ex{eE1vRwpa%Ns{tfFb>xKMRE1;gTH{c&lg&+3&9`U>M!u{}ULG=0hY4J1eC+0v0T-Sdd5nu0pL*flnOo$&bPkin4J>1`}^@5-K(Qezm>2FtJ-k&arZ!FLo`*_!p?|TEp*MG}}bv1o}JRi!7Z(Z9U%lm-VOhX=@k?>#nAin0tIPs58#(4`r0e?l&xGeJ;LUG>?jo&5tGoHVjN5Hpi72mXB7V?Z6dP?#PTDnv6EQ-Or=bgki|7sFnoA@vM0omc_=_tPG;92Ca^AG%&&O2n^@4nzZ9zy=o#l*LsXpZ|&!g9oS`mtT+%~1f)@#3>ji(m1f{QOcIT^sRJemaf*+!Wt*BMk42KBW-<^GWf|mwUo5l<SQ6wYJL7s|+!hkZ0>E#5db0zS(QC_=ftYk-yg(@r_G1!gri0d9)mJ<>xD=Ple^ZPH$Kc`5i*=`=YQU<Zsg$@kU?#K6B$!+*j*;gkK_Iv#iU$vV4Bgsy{p{f1ff|d~>$GlHXD#2>D+R6yM1AN#mZK@QqExw|sNCh`vlfo*-w$H`DR{Iqe<%<>kcJ;|JpB05zA1uU(3cm34h@2LJXC_!VZtZ*}V;t`}pn=&2^+8;5p8{`ZB>+WM9P8&T)xN2qhs-|}-Nll^?;NxP5y`fc&e`zPabTzo;~|DwZx(+d5uv`7BdG5C2^;!^bg#xwX^gR<negm*{&mQBSs8nG^IMiTs?b&#jjbL45z4|!%*!SCCh)*#Qv0QeDyHc5Qr4~XwL2YIwj;WF>vKJv9SZ(m%G)vAkcIT8f_Qa<?Y9mO}^ye+=zvjhCp$MYoK(olT;DLx-*y%NON*UuB*&^HYJiz(t84(&y}Ljs=H$DGAChnSH6*B|ijmPUN<TUgKH-pJ#ZI#=d(c0~N@hVXYJi*I_cQGBBtKEG&{R*P?#vlH{KjfQVrFxNJ}mMt)=-}V9e5IF~a(FWpcIX@#$jw7gZ%UAh5iPmum{PHvS9)jPWXwBQekFml}EhE19*>lusXa_%cEPhW|B}#ltgJjIxa-sOv(X)^z=Sld%0r)wh*+I^q>Dw{n`5V9Y)1P^x{-wv*AN)Q<Uw#7fRx675<hSBm7F5mJpB#4)KlLm2u}TR1rl-WW*8c`S<Go^46#SwSk>}SD$RE}WKVJ_n4nLqc;<tEY@y!wQviRnTxv;K>-tZfKo+bO6Y7pP>(|F_$og}{D&+OtGza%Bu`o>pf5I?RI@_cS3zU4t~?#n3nx$cG9o@XuP`UzX#FvNns_13cZ#_fqXhjAB>XV5|MP269t{#Mj;doJ>?PQ!X<FGhUlKH^(zc%sfiFA)Ev9P$^(b!SQ2gZOMk5dQ?{#B}To{Iq=`S@PEihF@?C{L$smpGp0Ze_o*Yn$r#RAtf6A_tx;I4Lh5q&jBUHH{Q-8d8{QmC)xUjuxiO!uIs%&%yNEax5Pf~o{ads_r<sFErb4e)j*v-hr~BGOhKQ$W8hmX;#*Pzv92~ce9z&?AJG)^t}cyvFH|+#UZ=(i9Wd|H^2q<bHtyH)h2VR}&6N62Gk)|4<PTUWzID-JTt~GFA^)x!;%h6N(1(;<Nw&UqTNl)`vTPP#8|jVy4_L$f9gcYW>c~GQK)3bHUU+_3_;WnXsk8W&M_yU4myWlB<-GN7ihca+Z`7GqOMG*^k}|K>Gh0#?e|aD5i(fVPx%<zMdfW~mkH<=0FJFSh_tr75`wpI;zo*-tb3L*n{Kk94Hzy27{PSg~Ct>Dv+w05tx;^*TAijPrf7UuZ%TAN{3m<U~@8JD8{Y7i4#Oo0_|F`QPe}kt}WZt=jvA?DM;Jk_An@$hLy!D14kLz6cOYt22@BUEAReZy(`8c25ec_wePL_Gkp22$GpG>m#t$C_q-XdKv@1YRHA8dzxFL~g&_+uN2Z}IsH{dqe8c?|CZCC}mlI6qDE!7sc*d_&ZD%-hC=`yM2|@e1E>`13ApN>1@DuR^fiRyR@4`o;2l_>AX>af_#J>+AP=;QsSsF!BUl3$Wc6^A~5H+vfQF>dSS=)A#!cTi;|C2j4Rwi?8>5i}fy@g**fBd;5(0r?Da5E3Q47DA&t~>+s)xMEvY^;+sS9-f4P$iua|)h;NaM{9V?=f0iHqgwi-y9lVgo^`pPk!{?eQr2*pa$BA!!^Avf?mV)mcjQCx4=+E`_$g^;S_*&Cq*x$T|;cNB9w=8nWyia;(`ParvW_27h&pG`HN*{T&V%mryHviOEnd(o5{_p>(@o3NgtAA=-->cUD?>{xJWv6Mi(??AX#U9jpWDl|z)kyXtH>LhWZc1*<p}0A<HMu#t1+@*i1-T`)9l0gBEwv-LEx7}=3%LWiGqoGJGr23Z2e~V`C$%@ZC%F%`Ke-Qi0CgC70C^~N40$MdRQmXtI+i+yJeE9~I)Xf!Je)e1Je+Kz_9L6fL#TtuL&zhkKID<)pE-P3m(qdcQRJc2zBcRX%XKU5Wz&aV?32>&Hht^PzAE*$>9aTYL1`zOed)w~Q`+8UAKP=EmA10kcg1a~&FnJIiQ<;jCU%+UN^uKnL%Ym#s92rT#?-phhUB{B8q`{3r8UWU(nqfJ;lQD|VEQORwWsDHE43rrlmFJBxyWiL{+F7EtcK!j^c=|9$OY0zNorZD1Gy}@6ty5Zqt;T?(&SR)N*szSrjK&eqSVsl()|9S9Ex*L?a4XFUo@y%=NAseFE|uG<52t;^<VN|<PTJ}{twgwWHl6L=TKbOrbmj)P%BeQk}H#)sb$G!*%xPOC9*Twg<6rE(JvPc#Z~OozlDbuqn0BVBmdB#Maf0kJH=`!eoIxod&?faApc4Io%(|Of<676LvbpH;z!iK$dAa+sUOHnRZpMuYsDWm48=Lw^TOneUgzXcTqu2%pgK{@kjronoH!I$r8<+VlIu`i$aTo|sa41seXq}<xH^a8;?!c~;^c1{hT=4;+JiLi#anVl-_tl0KcxOnen`H@q4+K}m3)_cpZbV=pZu8mocx@9f6Sry6^G)_RMq#-)Iwx66l)xcbKC4qZVtuyI24!XQ0z)|BD<2^sa47D<Ob9_<ObwM)cWK`WKU{!vM1S%L$M>ZIN6b$pF{C?4MXuus@m6=+}||vOY$GohvYxVcc}NscgVM>cgeTNzi}wOO}$UPO@2UqOn%J$d%&UiDTm@W)X!w4YX9EwYsK%WxyfoM{zt=5{FR!I{7Hl6<=4v3%fByA&P%Sqp|~2=m0XirgX&7IL9R=6x66FaDsD_|V3+xBskkY%kzMBdr(!Rvr(Ndzs$vhSn_cGnt(#ruJFpw;sz$CrbtF6T++?gVKiB<<y?IB?PtMQt^^QaFYYxRvs4vMcd7hqdD7I4XkQb!qoRK~vsPoAYWD9j2*+M=_O(Y*BU*=GJfkW~6^l^%sKushkkQY+dk=JqVg&c~_9Ezt=XOO3n{W%m*=TIEVp?Dc}0eKlYl0)%o4#n%K5#;sctyBwnD_N%=CF|sC)XU^+<f|NtuTU?LuaGZN&yz2b&vGa}Vbkjq9EuNeC_YS0An&HeP!q^8<Z$XjayU7FL$NQ_Og3{re5w9qU-EeBbn<xe#PktF4Wmvchmn_1L&>4sza<=s*H9zLYseeZ$1dt-Y9u+5`@NY%@g@$%Td3>FTgY+Lt>ifJX{t^>O}<XOM!rtIM7>HrLp?{mN<K$Up<W@Ukdvtw$;srC)U)K1<U`aGWTgkmhsgWW$2RH?>Or#7!{i<0?RJ@GYdeSH==8CY8b#erjv}w3#*kN$=TO7RbI4Pu0puy<Kn}$dsJ`S0<Z;yTWTg|y<H&w?ndj1vL-C~aF_*fS8bn@9UP}!luO-J)myngNA;*&UP&bnIkoVeUp5wh7isLyHAERz2E8Rp^x`nJXj;!=FS?P7M(o5uwb9szIaT4_$If;CnnnFHKK0-|<A0Z#$P`r<NlDv<+lX{4}le~etpS*#*$S(8jE~4%rFCx#QZYR$p&!R??XOTnfGS6`chvJ#(Bbd6Bx{|z<yn-4<UO`??T}56_o=u%Yo=u)gokE^Uo=goSPbLR*1hOur6UZ~kA=Gg;>l(*(EA_MKgCF~(bdpWqCb6#>*G5L4=i2PcT<)9F#Wwr6nER}Bt<AnGK0u8nE8Sz4d1e$Jq3*TIJXea3Q{(M2&!OTZ>M?TF^!K3#>7xyY;{Mcz<o@Jg)St-1$fK!4$fL<qsa?oZ$$r#cWIu8swI4Z<Jc;T}o<tr??L;0+9z|_S9z`BOtw$a~?n|vk?n~}Kbs={kx1v@cw<0&AmLxYL*QXXE*C)GC3y|H&6{-2i70IQkxyhx;C8)W`CCJ4&6qlnGCYK}IQ?rrn$$6+6S^ddQ&O<KBp?D~@J$Wd3Ep;h*EqM=hH+c_vKQ*4L^e}lp`4ETV6Vy}W6Xes>^W?MCi`4Vvi{$GZiZ4@7kuQ@|I20eJ9wr}Vt;abOAEfRkA0+RkE+y|Juco#quO|1TW+(R~=cH=noMby{HtoM3KM3cb7AEH)J5Y0x9msj9xygCS`KkHH`N;*T1;_=-g{Z~Ig~&yyCCNp|WvCU%Wyp?H7qTPSm0FGLO0G_=N3Kq;OKnT8OKwi>L~c&*NcARnBzLCvBX=hEp!Op7Aa|v9A$KLWpbjCoAP=VgL>^3br#2+JlPgmjkSmj&s8z{M<g)3b6xEqpmF!G5QrnP?<jEY0r&0Tpr;$Ub!^k1zaO!AsIC%+mDtQTcG1ZT}n7oo2NM1=^M4d!lL|#B0OI|>pPaQ>`PY$DwAcv7>Q~Q!<lg-o)WHULK+KL=Zo<VI!o<W{Ytxuj#o<emaPa*qLE0X=mW2mLcW5^?^CCDSmCTelAi9Co}jy#CmjcQNsMjk-TLmoi(r4}Xol7py2$wA}@>RNIHc?We5c?WqPbw7C@IgxsZoJc-GJwZM~)~Tn-I{A#2`7AlZp*T5xT%um3o+T^2NWMzG#-aEo^*Z?``Bx6bzfdoee<9zXrjT!tuTYPZuaHkt50X!kk5TuMkC79otH}xEZPcFRZRAjDPI4%@H`R{Zo7|L|gWQx{lj=aONv=c9ORht%Ld{RELaszDNUlV#K`lhCL9RtDLas%wO)W#NO>RteBsV6vq`Hz@lG{<MliQK|Q0tQWkOxwmlLwN0s2#~Z<e#aX$v>0FQG1Zbkta~Qk|&VIQ(KV7lZR6WlZTT7sP5zda(8NFa(8lTsuQ_2xe2u_xe3`r%Y0UOa47anAC0Kxsinx}$p)%3*+BN98p&SdiPXvDiR6VGiZ@WFkvEW|sUhTO@@8r{c{6!CbqRSpc_(!-c_(=bbtQQVc^7pNc^7#rbpd%R*+QL9wvc0~VdPlyChBbRCh|tAnY@u4MGYoLk=Ijakk^yfQKysFkt3;7$dTkVRDbds@+#^W@+$HQ>PYem@-nK4yo@}LI*2@vJcrtiJcm4!I)FTrJd5f}o<*KZ4I<AaFQ-P3my=_tJIFEQIO;xf9Qgn>k$ixBlzN1Gl$=D>$w}mM)HCFB<O|efvUdl&Y{jzwpZ?3p%s*!NU}F0pNdB+inf0H4*?#Bv^j!b_V=(UyIo0Qq^ba%H<fc_ybzl1*EImmU'

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
