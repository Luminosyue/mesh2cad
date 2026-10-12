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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b4484ff850e4580a96eb29ade0c98a4/part_000.stl', 'relative_path': '1b4484ff850e4580a96eb29ade0c98a4/part_000.stl', 'source_sha256': '9d3977ccb27d589a23dbc5d3c51d4a5b4fe9a78bdee78133d33b7660d0b31811', 'input_faces': 1104, 'input_vertices': 739, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.003927095793187618, -0.14395415782928467, -0.28172487020492554], [0.04784051701426506, 0.07316772639751434, 0.24690446257591248]]}
GEOMETRY_BASE85 = 'c$}rZ2Xqz18~48#6a)!Mm%h?M3n)bt<j2xNjnZ2v7b&46lz<=v@d8pq=!6o4rG^%IN8kns9qC0vS&C7Fh=_oS<-N}{-`VUA{LlHH_r>#^@8^CqcXoDmc6N4m=GvlJ=GXFS;@`X4;Bx!79c!p*6gjlK+OS^HL;LpVHKfvjK_fic+w9Xnsk1+68`h$uM;oTa1o!MUq(^jcO+EPI-X8{6)Ps8uj2;@@eL%N?(LH;SAKE=~NUwlDq)+!jy#k-h)~NbXMZIddiu#xO|K-2zfg<=*^9?!>P(6LbLQ<o|*4+mjzQ5pwA?)XGxy$Jrn|5`oL;LV>-hTS*{cz(z{`;tT^GSVWF7I~vF<a-5YUh92<@BvixrXxgRexn-FaG>NUspb6`#bIU@5?Ihaix!nuE6DLTHKXhPdU<o%BdIbEz<9(BGTVT<NfvK*ty^3@4Xw(-`ihB<WpnE0M56I*sk%$98PcS`iOn&+e`DE`AA<o)rWn(=4{?CW2X_t>DG0f%YV;ZiG6MR7h*r#yt|CbX?c=z)^Yeg=|3Aa-Q`~$vx+|ZXDmG9^tJt~**7k9ai!OTYpkWu-sks<IeoL7@MS*!s>QvWeo@S7uD4wJ8UEZYwk_}P;&pS`|328|``@3kh_|cyztvv+D&J_Dy430WTRd(`pMB52nM7*#7<Ja^o7k@Ots|G3^XKcKi#T1Y3x}P)?{YjJU%mYgDNbMeE|iapzw7a%uJpS@XLGrF?>+9ye{+_Z{JC$!38(LG8a0*kAF%bL)A!a&pUCw(IQEp&*DC~l&FP0$J?-?ZQc+|1c*X>sac#GF$QW)H!}EQ|<?V1+<TE-(?C(1dlAXTqyXL|VzIfQ3elpjC7M+&jN?)ud*MoWI*ionNO=>ZZKWE+U%Ew=%F8kImzq+=o56I2F;k)O~f6;k9->r)$T=|<*!$dvb-E-Wv-EV`qp3MadPq?;Q;MDY2rT6a`C+dICmXj_&t|$Ax^Bp5x+ihNkeQ%RAZvWEP=Jt=}^s$TF+s*N8GME2;hv81&dT^P2vu6LEu6&-|<KymKJ>`@u{m;LRXTR%#!Oryh<qPav>$bVef9jfOCx5;^##R1&I{V%<(SGcF+D3Bwv8Lrb<H{#@b^g9N&E0;y@QsC2UFGz@`LR#5w{8=hzBd2GSNwTurbO3%wK+VR^SPIOgmb^lAA5}C`n+1*RZgqq&f%{rr?Il}=dUWKztEFNu7|=czHsL6t@1`c&PQqg=IYqKT%McVcDmZ(+F5<r?-H`!mA+48D1S~38S2d6u-10w^1fGkfYbLKTHb}fmu3GhSA9O~&graLJ$pIR`z!Ss#D4tuu5$V}-{5wjO&_txRS&)?L&b64Jk^ztk#`K|lTs_#)qdJn9LwK(pt;(u*1hyNk<X&(uH!N`&lKJd#n=9=GK2lB|G3Y`p})m*y1gS~UFH9*+dNL6*le%M&)<dnd8@X#e%a+LAbkC~xPDn}E`7p(U-}#O|8{@AzDj%EpK=K?obL~D@Qd;|!;kjn{ppucbsWAa+ez_i>}yGH@Nu#taC{e?`oigZAI|N@<zMtH+UXlHtN3^sJ2pmgzE^(pvIbp?<8nOCRmbUD56?{Dc3ZDYZ}zV~=+60%Si;BG*s`NPm%DwR&sZy#=l;RB^wALh+_6(nQ7__pr**D;?tsJh;(8~2>-#g@zVy|_xPGMXU0<EI@5lAd-}U>WPTwe(F8YV$X`((mG-u!YH0wB5J$Gyv!TyE;+~0anMD!BpM>6|H#ZXS~-8G5(KkxSHeYhTPe8ATot^H$ho$d5L_RW;-J=p)X`#Gm?l+P=Ulj8g9d^F$XU)$Q3%Om$!@r`-ycwB0gez1f8-s!!5oX@)B;(A&*ccRnx&FVRr+ew+~+z)8s<@oqm=T>k#)FzbU{55}d_Vptlh;d-=-F#m74p--PVcmM>8gFP_3P*ANjY`endKq|^`!nr$b@sJy)A)L)^;>en>H9v2;(k_M-}USBqD1?|^(B5G?}z{Rc9D;fK8gLI^|@cw!}D^#<0~iX)7R~_^IXo;)!8@0g1FuK2G11z{Q2zzdB3WM@pk2S!>p89wEHmQGx}^a&C2=s?-ycU-<+SX%ld%5C!M|(e45MWJzVLW_<LRU{o6$S%l2vhvQOj_ylkX1e=GeO``&wH7IS&Jp5}IIKH4Gr$JC=dj<u5Ja{DwYKV{#N`J+Afe=8);<FY7Eitv3;7P4<$NL#?$>$Q=Oqxb1G_VusFE$4D~u6)$#`%ypgeDM#g$mgr^?(;>?diMTtjeTp*R&HlT=l3}u-`@+lAJ=nN=6>IZzIDp!d-Got_Xz{Dx_o`<y0u)MzA<8)`S&&UjZra6d3(K2i~jlFLZ9>T-L!QB*F(1_yj}gjPV5_#Vpgyp@rcu#|1D(STj=ru_D63#<MfRjt-j@aM}E)k(CbMR`TtaA3Fq5BU7Xhg3k>7*!(+#~j-#hA`+C_p(O!=VU(1#{oa?Jv$OLCQ@n<j0{jqiQ2%ld@zs<bAzMxd$=b6j(rbVZma`_W#@qStDiymSB?NlCjm@<DHcP(G)NG@m2kNlkf=tI1}zJjSS?9U5d&7V6o;(W~LG;#hM`i0w@-Y-Oyvsn0-qWy*PdF>yZz~wRZ1or(nzvTHSeP6?<DbDlSPG2W%vh%#t-c1#Lwe<1Mdh`DlKAN{{yt$dnYdlEW@9_0{!uNkTj_=pZk_p1!oi>ZVKj5^uA1Ph<D^B-T0@s7Le-Qh6*#!2DulsZRxB5Le;q>+4RZULc?~phyWmDPL9zNstV6`sD?ZKEE<m2tvkDKf~U%c^Q!k^cJ>sgN)A^MH@IQF&ePd1A7d~>(c_iirCz8PL~r_(o*@^CxXBeLvq<+HX{k~r@^<MjH-<?Q>4?%l%Q8x&LD>HCWb-z+kb>&=>XTI8RzwqMl4BQcJepU%FO^#dN?=%de_ar*l8CYv~Yrysce7zuGaKJ!o7%k9(K_H%I`v^a{#XJ-DN`Fz)tyK?<#OXAq~){C0#JTH99qIle<EjT3VtzDwXXIUKkKA9fv+`B63>sQr}^ws*2zIR3HIxa__Dz5bU(#-7ZU8afjiAlmQIDz{O%imOt6V`-{=laRrozGKm-`V22wk}TiM$lwud-kqRXJ5NjdNY6SwPCl@H*Rd_`ZU6`^LCA-pb6~f`!m_uZq1~y38H<r=Ju(zN)-3|8&9+EOB}-2b)($@t~c+NsENGYTtD*h)%uPX$9G#0kGHJJnOAbXw|-sJ^Y#$-^;<z)POW1UA75*Gn0OxX)@<bSx!B*GaqRmW1Wj=sM`LG_$R{*piu1hCcb#V6$Y1v$r;Du1`{mu0F8sOc_&VYpaE5)~?vTk`{&bvokzHKA**0t%`$M~&cBO9`#p89^|483LzhqzccZad>&2pLBfps7!m($!6CGx)>#mB|l{!dXqd*VcTdEJZ}eA4M#vL4Vr^>5Qfd92WHxV{GW<LivJFNp6$%!@ntx@<<x<a~^MAyZz}PNeU@nNJ*-o}FC2+J3zIquAH;jovTnf6`f}Z`{}{&flK>b~}B4YD@Ob@M5lf{7EI<=a<ZXZ8P`z1^=b<OQu)PFX=CQa}6JtHg!{+zGn62dNZ)UcK+K|@pw#LkBkFxBA?qkMEcJ4IDg-PBvJnDFSuXT+D3@uc;K|S548GneVU=k$xh!u{relYJ?Kh*eXyvX=zqU;`u<eWAL^Y>>~Q+#)^)sHUwHYQuJlQ@#JHt%6_;<Vet~g$nkyfD#UZXYqvJxC@BLYv7h0!P?3?~{QE%I}itR=Y;Qrh42gP#vZ+*o3<r`9dpUdChTRfK@R8)+UlS71mx7-#^7kVk#=^Hm6^ZxoHr|ot6{<S^0J@_Lk?Q#0%xY>NZcq6jA{U3XC`Mr@%IUns{82i?W2kV^eO+OeVwtMHcI4_!vJLvR%BQo>&(Ciz}>9s>~?0YwecI#_7=CI4JpXBPF{V8Gmyur5;+ig=zw3DMr!nd+;yYhYd-yzQD*lG5?1q$(X!AutS@6z{eO5Gs#tCP5X9!nSLttipnhE&?;^tD^r#D0ZtPj>nS&M&La08tOegW|ZJZx-bAR^-^dPG3vSCE8(h8n;j5cu1VH{`Eff#QAt4ihb|hXJWqwPvi9Fi8%K4doB66YmIJjd3-06L_T-^5$8pd*n>`Ap6_NvO>ulro)-Sd`g~k`{SLZ(KiaJ~vNxCCJe4lCd-EKZ-`BVn=Wm`363=Od_vh=K)uJOGN8h;+_Pt3@xPH7XhqJFgC?lTZOsUG(HKSFscz*k!9sAmiF`U2Fw!0Y5Kj=L}w6_afeqZZ6qW^g~O!zmFMLTbIg?%l3)eLbQyKp_|9cu9PQBU6?@?V%|jWZwPmuI3p8)HQ~Y&a&_>3cWEux~Z!=<<E*Px5~G8Z>kJEB10Zy^XRRbmg<GzNr7u<F549;&5?4)i}hJ-ufmF`$nVtuJp!&R33L3jcdEooAWUqYxLBeepUs(UYm^@y3%X2O0w^3^pCqdv9T*f`JcG=D>i1O^SDdjKXDw7C;g$fUFl7EAJiz=UCwc_+|GTWDX#SXF?odF=yi8Jj5;LRXTunGc}7-X-w567-tPS!qTPn>bEk)I)PLf4`uY#O`M%y?ce2Yj?pzkvsYd^~^3kv6PZ0i}E?<MMH4Jyx=M~|5>mB9%eUCzCiu35c=m)$_cR79Y#&Oa9yF~AF`Pavb@q@RME4_BTyU3@@SWa*LI)QyJ%I|M7^Ptl=P|gfLo_+tFG)`~TDeiaqD8Kamk1q>9&jK;-jVLaj13XR>`R5b$<?GW$+?V~9e-@WNS047Qh|27nPeR!@-rgtjjVR5&_vwyVuR0&KXKAxub$&@-J&&ZXo-ekqoELWfN;{Xn+McDawp%+NrG47@DDBfOkJ8@sKX=S_9v5x&`2#K=$3^=7KhxMZliu7QwwomC`>!%{xV^2aAnrRFS3c<UedboKH>+_kmv1e=c(2KLm+zldU%X#wvXp)Aix1{F>rHFA&h3wXv0V5o-TqfG%be{{`r1e_PSBbRbot)<@uJ?EeChUOJ8ydC)xJ_ryZs}*mAO5?KQQj5A)gyAU)H}qddC4*dOIH_J&ub^ue~;$eXT&0NY}sWNvCh*uP(+({ZdXieP6z;qTGGjx_m3oN}PAO+<va&?3)oKUB3726!BaoqNvL^3S<}UCVBE%S3Y?Mi01$Y=ec|%%Msjv6?gfjH5k{~3P)W2&8MQj3f-FQ%ID_yV*JqVLW*mDZ|oM=@y1~XUFmNu5cffCdb!e@*F3Iql=S@@m%GMw(%07~U>x$*VVA!q5BqxG=sm9dmnVpECdOkK{t(gsw9e)#k1;<%^fRshbmec(na$^mHQ<r!xces^64%X^b6x4JaXrL1JZiQpy>D!5_RT(>+~pbZrWjZEyW{eWVVQY6W=73(<)b}F6Zh$#mUL~`{}axysCZYs`OyB2=soUwzTJ*}@25`>x$5&$ety5>8*t9GT{HO^-@llH8l7_O@0JOCpXiG|>hjg+26p+C=LU8;L!(^JG3@-6=LvTGGz@b+2e8X8eLN?z_qTq!>wd(@F`VB6sr{bqEB&7BEB&7I)qYR<YQJauO27A#kA6@3YQN{rF_C@sx*&b^x*&bE|M%sX$G&>K@C6-ZU%ejbIiHJs)a#n`mFt?3>*xY5k2<b~|I+vw{!8Oz>8s;mnZG)|h5ynx7XC})Rhf@EE|vMH<5F23b)1>|xyVPoAIZ0KA*WZyOTK(p*neq!mA^m&r&q>f(tl~ZCw+Cimp@qe%6L!u>Uh#9P$R+J4ux+Oh+tnG_ex(K_u9TP?v=he?$rzKOn6njNngE>v(qd0akj6tH#;BYK2G{-JG6b}K2G{-`;@+VA7`gm+O71}`#5{M%6*)@UrIZdzIq>Lmq%&;wy)gB+4(5vg<T%yKF%(Wa=zI4E9Z-yUb&BxzIq>L*PA-7mg$xIIJ-WT`#8J&%6*)-a3g-tsy<Kf6>iVI`uxEh=M#RGUpDghW?Oun@)eoLzWN-)EHY2{%5x8Ykwmdw<vEGJ=oRtaS9z|Y>k;4Zc9rKahCZBq^|_6?d_McW1JgF~b`}j4<t&j^%#Tr@|CA`ezWUrr`s(u~>8sC|{3U`#dgVElRicL2uJXLgEZIn;SDueqB_l+6l;>$$so`R~%5ypCtIy^1QWHh~>hnPOFFg;0uRag7O3f4bD9<6KuRe#=N+$|md7kMzyh+qUyCWNTJF9Pq`39x0i1f;HQEzaKCA?kb`Ks+J&sTlHjh2Y>#r^zN`s(vrUvT>+qJ6rb1DnASBE9llTKej9Y3ZxarKPVvm$rT7xwNnBaIszG`MLDf_bJj>->2BV@;*iS>iZPwtM60n^ve4byPV4Ne6#FCQBLK(hV<3<1!mcKA|K`bi1gL>Q_@%8Pf1^WKV|2yyic+7QQoIWUwxlqr&r#mNMC)QB7OCJiuBd@DgLsFB7f!mkyUo5$VYkK<S%zr_{w`X+gILmNnd@>C4Kchmsb9{s0Zb}p*A<ODe`f@XY|c2%)a`*Qu^xqN^@>WkzRct3SWI6YR;`7wyV6KmA-nPWv5r}v!wsh``Pn#+1K-r5!W?bFZB5O?5ppKjreB5SKcoh@vTKZ%KK>PtM9M<@jXQOmG|9N{1B0k`hFa~`aaz^FG1|D^8Vd7|0MhB`+9SJs`<+E3;s*z(fkLZJj#3keZdQnUYS2&b$V^7*x$zM`Fo@9iuSpnF#GDf1^<Ey!dK=wSPN>2bqmV83+b!#E~KyaW72==z3{@;!dK>9m<b6Ye`S7%^ws$x{zYPag*wl~zv!-*cdN`xF;1q7?S@U``msul7vqy}3iJ9Cb$*LhzZCoWoM2u*q8E8Ao)0Xp%Dy_!NBZhKAL*<0Y3HNVr?$A3*sd}UM_*iDtdmjZ?dXe}iTss$KH8I3?5p#Iq_55wG8gw}U!B*aFNqPpG7rjFGES6Voj0{4R+LAXe<gi&{*|$0wkVG}kL!>r>a#*DuhX$6y)KULl64{<Wj>g<^(Ik2%Dgh^tMkgd<{?o(%6vBItMl1xUzyM5HBSm(nJ?!xFNpFe^Xt5sZ;9<H^YH@b$#O2YGJnszHHdxvRB>*H+6FOS)LdFpq*vwv8q4alug)9vFYCd+I{(o2mHCI(vKZkj^BAT7(!9sQo7vZ}u1d~pHSg{c<y7WXYAg1N{Zi&t2Cm=itMfUfug>R`zB-@Nx8j0Gug(`;kt)(F^Gl`w(tOkv4@5bY`L5De=eyeJmHDpv$`_(OmHD*(H;b*{^8EXkSa*Q=x6)VV<@#5aWM7@%D}8l-ueGuQ`|3PlYh^9=)p^BMh1w#$G7nk%y@5!t%v<)Y3TI!P=j_kZQ<PJg7wzvKBg(1Fqn5rpPg_eAzB*4^`Y+AXP8=uFEAzmu*oEw?^U2M`1X2IWd~!2!x!7NIUV4$WA|GWwy!2n1-=4Tm<fF`!m;Ouh<X7(%`=!jow`v_1zA~TRSbb9LuQH!sKXp~qv$9^mnr(^gs_O+h|0K$<tVfW(x*oxJ_*~SRvJOJ}>N*JNYjQn^;@j&%6#u1l6RTf{@+<2yv~B;1?JDay^if$?a{kJ?58s-??5pcaq_3_k(JvMg`6%m3j74SGSJ$oR6+d9#C+k7+)paq_SJ%ZD&D)A{D(h>syj?_kWj&6uB9eV|U5__%DEsQV9-~cy@RjvM(pT3LNnc%0q~BXB%BiellD@i*N&omD>e;;>%Gclxaa~l_fl6Op2bz)Iy$;k)udD-=zPb)n`szARJAY*zsGYyE4pjQ;I#7GN$~sVcyUIFH+gH|s+P<<5)ZVVL4pjQ;I#4?wWgV#W)pekDKFT^!JH4_F)UG#W9jLusWgVzpeq|k~osY5()Xqm)2Wr=|vJTWvudD;L_e)s^YVVh_4%9BEvJTWvudD-=zPb+7E|0Pf)GoiW4%FVRvJTX4hsruoJH4_F)Gm**4%E&^SqEyDM_C7ImtR>2YWvDMP<y+|I#4^kvJTWf?#en)`*<nqK<)ii)`8mTm35%@c9nIV_I8zZoqE!nB7bE)zVy}g_|jL`<J;+#_4s!F%6fe1tLyQludc_JzPcV?`s#Xod%Nm-{LU8=Ie+DM8>FxPZiDpweP)XC%HLanul{a>^wr;OkiPo64cd)Q`MyH^eF-C~8~f_-QE1g8#C?eJ`xVkxfA2#7XMjkr{BDNrE5Dmzqzq$U{XG!dSAGvf`s(j~NMHTk4?Dg3yB~3*#qU-qzh@%-mws;qzWO^Sc0TIwhroCJ{z(hhufU8hKX{B$Es!J-*|fY`@9vJDfFYCqNqzNC!1S&5|LZ4U-hcnSYX5J)0h9fhN7K%DsQn7fl}WG#E}ltf1#oe22(&Sn^iyyMxHhy0xHdQxIs_aF?h=U3&@Z7wz+Zw#K_`Mofn%T(z%k&F(D7i>5#W*F{s`g-=x}fZxK|)rKtF>H2a|pc{tVn3K|BsR6Fd&Q8oCiox(U1*yau`fyat>IT?<YGFNdxKF9&}EHNoG26QGO03E+j$1>l9?xd`Gp(D`7}c<>zXYy|Nv=sfT&@D=DKFzNT;E8v?5;)~F$;EUi3&}(4QTi^>|3qgDXnhGYp4!!}t4ZRG$4ZZ{20=@&@4V@33k2=~7-3KQ1gLi}XK$F3w--7pmcOr<lLbrjpg1<lz4}-1;4+DRWApQ!v4otcV{1td0bSZcscmRUf2VD#%T>|!jryz)9q07LeE5NbfNr9LSO@gifufX<_psT>7o54xo=?LN(2;!;G?ck~4IOq;=9C#XZ7kC$r!88Q%WCZbE1o3_Z@d0Qu_yG7Ig7`b=Y4CU8v(R(kv*0rb;`7it;PYSuS{-bFKR^&~(}Zr-1XB<vLRWzk!TF$h!TG?s5yW|*Z-euIb3r?RbAdY|h}%G0g4=*wBZyldh<hN2z0fc)X)~}F+zr|k+zs3n8Vc?T?t&oh46O(54DJd22;39=8MFqNv>Ny`aCZc8e`r-O=?CEc;4cuwG0<Az7;q%i0F%}QM}mhSh=)R(fQN#k5yXw5Ey0b!%@M?(Lfe5!+k-y^e*$d_CT#^Ktpp|w0h2ZYe*(?~%>m8?&IZj2&IW!1ngvYyI`|E+2SNN6^ffT)o8Y&=IiZ=sIl=NDadv1Bn6x4|J2)6x0UQi2iy$rs4FQLsj>;j3%Oi*@L*EBi2EPZb4t@_@1zHna1^gkj4){ax$I$xVkHP<gHU$3<TpQW|Od1ZZ4ekex0QUorLl94d4hGMIehnQA{u=Cq4gmYWUm}PHLVJM+L3=}cfqR3CKnsIO3xG-A0T%&xf))gm76Oyz2a`?!cLIM7HNm7)!BbJz&!N4+j{=SO*FZc*5dRj4(wT&og#HSCKa<eP2;w3L;y*nih<}07cYi?;r$Zls|A0P+J_5fN_->^@lz<inlhWTyKp%lAh)Y2qgR2H~bs(xEh}R;B*Fo2SNvna^fj_`^NvlGuf$s$B@pd5YB8U$li1!6zGjt<@_%MPv6?z+d9eN9T8%%l!d<$#^VoM-41!6xm1x$Jad;@9sL+^n7(0kB3;5*nK;(~#Cd^Zpu(>NsX`FJ4K1Y$!VW&~m_f_Qcy#s^|%Af`ZPgHHrvS0MHxh?hVYftP^epi{t8kWU<R1~?8pD-hG6bD=Z9Gf>vK2;v>kv)~=zOVDVK;7j0M2;w(03C*2JFa>c{Xbo^xaBFBMa7So6XeV$xaCjiz2}E!pDnc89D}tLt!@<qLT?5e*+8#mN78(u?$F|xch-*S?fNO%YL34w1WB;?^Gx1Oa@fFk=)#DY^=LYZwv=!oW&~?zY;I%l$>!35i>%fzt<H5tAeW2sPQP6nkc<^|%r+DZh@FKLucm(l!1o2Vm32-it&^*u+;CDPif52z*f56}Of`0%XgDwFd1Mh^!f#cAocOr<lJKFtr=o;{L@G0nV@G0>BJR*o|Ll1%}h--O75P$3uL3{*h*MN_Jr$MKKr-A1{=Yr?re4B$H-VMD3-VMG9rE~8lJ`?vu5NFOLl+MG<2;%b4s^IeAR?ya9c}})M5O;un4DJ9f27MP?47|)Ef_SAz1o2X6K`;fe=@CJkAAkQCoF7~b+7a9leMB_`aTRDdI2`>#6$Ei1XfU`C_%-M|;3FQPr=ahEzw-z!iqGU1#osG}i-JEw5VwIg2RBC_)W*?I5s!wBf%XIsg?gbq!KCfMUT`gFTQF%&a82}6wGhNX2;$-B%c%bvj(&{#qv4*6erh=WMtlw4I`B2{Lg-|$?3)%Mh(~DjI9R9-9R}9H#i4z`vM(!+ATAb&qR`>cC@^U}m~=gu^eA{Z*yG9Q%RC6;7zFVb2;w2oJm4YV!Jdr1Z!m&*5P~=#f>?u6Kd3>Efxi#PUx7%2{sSic6PyPA2|@fDg7`7?1^6-eSLh$$U%`){Pr#4BzaWU8Lmz^lgMWwq4E`Pb4Eg~44E#5O_&)Ss@V}^o`_N<XNq2(pgD)e9PeQkYNl$@Kf(v+rQommSLEIZb{28=1_%m>KXf1GeuowC<*bDB4AnppK>jZHZcxUjL{4)sR1n4wy0(dcW4tOy*8M+&s49?^cdJ{}a*NjXE;vNX%8&JA_+<=w`QxKPd*9u$)+yvSI+yvYVS`6F_oF|j02hy(4V&G!9o^(YlbJXWD)bTQ0V`QDL#4%ZkYm7WbOK}WIO~)}c9mk#cD3q=}NAa1s0Io;Xz}0YFDS#l(fgtuk3xVGV#Or~0;1NOmgGU7M&(KU@QVmS{pGPnSaT@era2ohN^dInj@KfmDVA7w!Pr-jdAA<h^KZE`Veg^&>dJjxW`}#XR6W{TOAifPP1TKW@EwQ}r-bN6gKoHCRlXx)nlqaK)B_86*xK7JHnOOGQ#Iippz6GUg_APuSj>dKTBk)JK9!EQ_)5M3MhoPgvhrub(F<^NuPeBkLp>_rx1RV+<1P+6G!CqXy!w|$-p+VpvT+g%OGw~>oP`XYN%X@6P|EBv}y3h4P4}ksP{m^~j{opNH#=ZR(=tl4s@FoOt3iL4eFv^gEAf|hC`TRvblOd+(7^Ee^rNAXJWjvRW&p?RZLl9SjRtA$60apUcXDXzBK#PD$>6y+S2;$WU;x$kz`x<;ErspHoz*V8w!K9Q|RphxEOnof%r_>))|4f>!2_-)neLL}DXcO=mTqk6oO4<xcK5+uB8O`t=`Yv%qAWh#uyp15vjUbLf5T8a6pM^$%&w^8-{lTf=?-9f|p^@O5;Oo!<;OpRv(1GBK;49G2!B@cNp~JxE!50w3BM`)IA&7HAKL_UoXM+v|X9EX82Y`dXS)h^NEa1%0{@~2uHxR_HLnFWuI5w{%h-uvPHjdK+jH8I<7>YC>l>B^18|BFuixSH|miPqpH26034)nAqqi-kv9eNgg7ROs&3y9^lgZMA#_nwSv4e?XxO;5(PiTFPBI`}${y}ZT|r$MiHGOmfl^14a<1N6Kn<N8bd0D8fbag8Q^1J`ci%kV~kFM~%Sh_gfA0%r%)Se}CTFKA9M1@S-7Y+wpv8o&PuegO>vQxN|F%>vGX_C!oU`~><2n1c8r^mQ-=@y}3dPsCRPoHY>Fps#_ifiFSd1e4|fUjm<l_5+^-pF|KJM-cZx5a&k_=Y{3~)4c%c-_RW394Lpp*C2idea(|`KSKOFG^;1${)JfH;}FaHAmViBRd71$=mmoKZv^pA2;zs(Yv70AAEB4PKZ5T;&w<aOzV0E2Js4{e=YSpu7r@x`C_a;a6o2pI$r$Sr%keOA0cd_O-9wRHhUN$7$8or<WgHLU3xV(jKA+b_5PyXr&Y4LB@mrZh5Wfu_3(lKK=oow^pZGgX=tbyQ@L1%35!<A4TtpBrhn@#72QLf6Qs|G+^WY!Bqp?4<52LX!v=5{4nK(-z8bTXDbAlUy>q6fGzlD9Qiy*FtApS5@MqPY}ATEa>&W9lW+9Q<e<!eWMeT~n=rxC<^5X4E)i{K>i3g~k13h+n-@hIpru&mQj2;$Lnyr8S0OTnwbPoY18pMt;i2&KCI5_L}X`z1aTKk;N717Zr|{{^BCG!ohn90`tsHUKxk@rXhY4~EtQ4+i%`5O;%q2<`^{1X>Q<6j~Nq4qO(T9hwiE563n;J`;~a5MRYHrsH}Q$9E6-D)`$#d;?to-2>i(<Glbu91C3mjs<@O9SQylTn0g03OWj03S1I88e9@w!qGlTAc)^Z5RZVa29E&CXN<(xpii}o=aa;A@ADMxXcXGa6YwZ-R<s*xAMzfGSl)9H4|238dA~+{6hV9p8VNoIJ`Rln9|xa+4hEk9pMv%Sp8}sm5RZj+1CIswg?<8-ZLTkZxI2QlC4#s<v@EzjSchf@>)^X+m(&*TB8bN$i2u`sQd|5FL3{}ME%*?4rK7#BL=ewM5Klr7kA*G(FF<=8iy-a`{R-R{TpC&iygpFQq(CeQ#MD4c2}FAYaa#m&8|Y+k8*pprBrxejaBFZY=mc;pa7*Y6a7%Ct=uB`6@TUmkPoUGmpMb-l)4-&&z+vF#2;w@>CE$Y4LeM4PC8#UnPJw6|h}j6@<<O77q?N$S!O74Na5C7BAl?Tp4<;=O-Ur@`Al?lv112p6-VNRfEeYNU-T{3VyaT)qLA(W89J~d*30f4q3A_PX7+e^2wgH+1UL1&TJfhuA1y4Z`Plhf6lO}*CgC{{3f+v9|LKlE1f+rw|XF%tJN#}uQfM+6zr$ghxq;tX3!LqH9E`iPkH}Qz`sxh=Jn6wSJF}M+eI276%913m-Z3S)!ZUAiwCT#(30IrW9t_S@TO!^799=I-o*nozC4R9T3b5F+kL&v@#v?#bBxCnx{7_>N;^j&Z<u#O-u0WAq8Ed?$CE{z}#hL!;bgUdn7f=SDR%YiE(h$})vz|@wh58Z$u-UQtUCf)4GI7f)(c|^Pox)n^i-IH++63cUwcqeohm~@XP<Gd!`4gJ=W(GL*IeuH=)bU&E%fG4A$A*Md5rbqN;&7e)eq@BRcz?~7qbD*=qq|3o`z$*~MDbQqaGPa+BAU+H|046;MJ`6qtO#~kTuR;*VL1V#j;BaV1Fljq*IJg6}2Dk(GLj>`A(8}QV!0$sVf=NTb?}MvAD}gJa-m5@sf?G86WXhZQ|LcE2o$-(E4>i~SkXrqwd)bonn^{7&j73Z>n!Qf*WVK9z|7a5B7#j6z{|Ac0H4^'

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
