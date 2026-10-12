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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e5436e635dc4336984c76a5f92c7141/part_000.stl', 'relative_path': '2e5436e635dc4336984c76a5f92c7141/part_000.stl', 'source_sha256': '3d1760bd837756d9efb9c30f8ba0cf1b14d4bc66643a3216392cfa0726fed5d5', 'input_faces': 1058, 'input_vertices': 577, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.031604379415512085, -0.18259161710739136, -0.4999998211860657], [0.04705113172531128, 0.1532769501209259, 0.2658187747001648]]}
GEOMETRY_BASE85 = 'c$}r33AjyF{P*{{W+n5GA=fN%ktqsCiAo|GB;`s9mCTXk7^8#?$q<*ynE56p95N&dg;IvwoF<xS^6uYSpSADVzkA;Id7uB^^ZcIgXMgY7Yp=7Wz4r9z*e+M@5}y56$@~50hep28*z+VV_DXm|dkq}ir)RH0Y5n>Sk9b9lFaMm*xaIct9q)>GL%k6-?(a3I=fE1xQfplEz*RMBr`CAj(Sd^p_UPCB(Si5(62DE4hX?iY{XxBZ^zY?w*KE|JN$u1Im)A}mnfgEcS5V3@C@o`~FY)i^u50OQR{C{wwk7e?n>XJp8o%?$h34<$pIV!kUi(4%d~+8V|I`0WJ{gstxBiFKj32+crb!>|I?4Fn_Ag&F=~pyeo0vYDR^9mN$8K4jcwFtf<9dHQI8XenN}21;{^NeJe%oDh#gE-sa$TYy&CF~3)Xnd{8p>b!!S9+f=>>D#S3X&lSk8>a$7Y$|wQ}#8#Qam=|8S-`?$b?|n0y;_II%6kkK)I6Uw<mmkDsk++9A5GS}1)CKmKj`P<pTZ^2tW477M3uXZ_f!0^#&m9(ux*^I)NH`i9nzugnulA6q|kq47tjh0>>Puzqwx^>F$jhnAaqUzr|CAIFca=@LqxapW`8F7XRnkA>3Xd)s;+PxP~#pRq6Ozw@i{V_($_AGdTK(;vJmCWL&iX%*|&n;j}owD1p^CZF4mhW&#_Hkxv74VNc6_~^!D$929gXS(xsdGa)WJ!w7s+`{<Yn=gjze|)1iO!{^4P&reN{BHeXM^A?Q%~!r@+H2`OCVjmB_8I25TQ00mJZ^0NQsbvD-j>vlf7EhAqMxzrNt@3f^VTKvqxh~Ka`?1w;GbR<YRAC8YTLTRdh`0<WBoE?LgjRRR*#Y4a^C&<bmOnSaeXpBy6?46`si)98$bS6rIqIQ?>TxR(T_R*?z5(zvkpeBzq)iN|G?k(O(_3Z#irJ8e8BX#=!FZX68(%i8(&ZKy{V0-Cyu+=@LNNEFuoR#4f$T1qPCwe+iu(azXtZW%qQLlH-vrWjd<%uA>V6c=Lheddd83Tt8eR#c`V*}pz+gZ{r#NDr$Fyee{g;VzH4{q$DL0<3H*PChx$X1f4gTw{UPJPFym*nI}`4Q_|dc?nW1*6Q{3j$`@NOoyZK-HZvKzfnmx^wXTrfy{?3p7nik4Gqwt;9&$wY-GCzhNj0^3%ae<$H=C1I#aQ^2Hh3X-F{G~RZ6H8W^c3X1O$wWVjA1nNt@nf^jO*Q%b{H;0P1?THM=~EN?d3<sO+aFS{HGcfemeB8Ve(dR1p?Zi7zif&*ZlPV<6YE*~!Fje$t7pyM-)tVvA3p=%)sOSz&Zj<ud<t|3)mxCyKk1=*3-YP8Dd}-z9omL}S6W4Tel0m;dt$wL?Q+@iGxa;OK5^@Tc$eriN$U+?*ITsK>8C^OwP3$#ujn<0Cnf7w&e#1ahflpZU-zrPSN+P%ciW_7{onbz|Hr3{oM`)DlkJK15PfUfQ_04u^Yu9Oo@ix!uiW|_iTy|W!8&lzOB2lT|67!qcwFtrY9Bb5=to=Zj3-O)e3w36@0kg<Uxnv4=j-{+`Fef}d^NuX`K$RY_DLS=tMg0XtMf~I>g4gJ{HurT2=&j_V~ro{XwN(G+PMxT`q5dd;)#B&eRZ2YbKr)=`q93tALmEExO;oD^v-wbqc3k6XZnLWFFQZSdAV<4<EM67z9F%k&W~Q+YJ13^zkjUp)jGlXdYuqGIL`QbJ>z`6p2^|6@#TEAo(X)lo{4?Y#P~VZUHE$4<;}}&%c<6H@sf{>G5Md&w<9#}Uav9Qq~9@f{r}4k+66!3_`BParFVWXj<$UgGrn5SJ72Hoov+vPfv?u{K|X3d?|i*JcfMX%$8t3`etMS=)`$8zessyJq5c!!-D9LZZj*35<9lVSAB=bW)VfPDlckU1yY#W|nv5{Mx?YI?Q~7bDU(6047vKAGcKEo??|FS@vh-2>;JD@14L9k(N!e=t-et~_L_fCk@D{WGgj^xtTe!yhTW&a-=*Nc*e#_{TIfq03x9@E>diLqCzjEOwvpul&u~7ckl{0>H#F}vW+^b$UI`V~Z`kpH{8vprMLw<Dd+1Je9-(C^&<I@%!KbEm5oW5FB>-QTT@?(4RTK~rz!};uq+V$XlJr9M-Q+0@02SwBW4EeD|CG7dI(X?=VZn<-S$*1lEVZTM*K4x3zpVhls%Vg;@RyS>#Bz>%5p2tnQpB))aKcMYslYZ^2aJ#>8|7_zQ?G|d^^q#S~=D6)=TfgkQVYWO4yM~U7pE2>i7sZcG%CzZgR5pGzPb7RDgdf8X`X_!ytK&)2$MJ*y|L&m2%->(?7d{W-$MJ*tXKG*LNBdqEzF(yLV1C1oP5gCxvh>am)(Nj48DjFesn2}lzrWkmgE!%j@#CGxhUOpV$7&u9%|G6NQN~aGpw~=u+-momeBz%BvFTSV4UJ#tdsPQpzvQon6aDz?4#xK~JBRa0-)P2f^tDGq>Ak*1j2|oAJ><uV)O*9|GhL1)`q4aBneiJRGCq_(da9Tm*ZH@E(>GXT#&5L$$00x7`fEGx<{u6Du^E@xaeaJiIG>u+GL0Uc8O~>JKjX(f=^oB!$3(LpiEqmc*W3DzkDBcsQ|!2C{jl|;!z(8B_hbw<?fdxRkRR*2Xq@qPoix5Tv!eBxH==0=%y@~8ylSxVTXuh2(g*h;l^?8cM@$=N@^j}McizNLcjp)9&+BOXXszeW_>H~rp&gGuwKab1^6q=gI9pj{N1`9SrknBO=T~k|^u3yOjUQdsCzL+E`q*xhPnQKD-<wx?m+_ZYemj)D^esEh_VEW+hmQN;rN)o{S!7kHoZfb`fAq%AuZHrurJMEd=n?XxYpR%Xq~7;gD4&diGwu0n+3}qr|Gq5KKhw{YU7zTuZ_B&Z<nvX--J#$0+}!219Vcgo%Gs=wy*}=|b9XX7J=fsZLirb~_g2d!>7DP=dlk=_^MrSOIny74_57HBOn;45y<o?6?RmDp;l~!dWBm9prw=Fk@s%&z`JwJzM?>jTkJ<D1Z?}iiNAGE9eDBV-A>XU{gqa7t)jf`d^51uZJ-@d<5b~pQ+S+-5c_uh+qj_c?h}AnAN*^2knfd+kZa;<d8M)2WdwlqNVSi;SI}Z$gDV)!y3O4=0zG0v77%RE?P{?0e*IZ9{dG>_r)0;Bx5tIKdFNghug|1BI$Eu$jV8-2yjp6j?drmOzUL{Yc{xfDDnJ&JY=YxEXt$QIfem5+8$n?uH8KHH)H)%{C`}@Q9rM<K}dKiCi3wvIBqCm)xXRXQ%`GbdcG5KA@b=l~)AwRwHrp!b?w(^SyOgUyQ2+d>K59YD27WFp!x9Jk@&wqUQkSWJaABBEbJafwslkeHiw){hf+UsTfX#Te|6aB0*FO4$!b?q9uUT}VNz~0PczP>*ntFUccvg0~G$8o2unwYHoUh&5#CHuXxMW-hvtvBVndP~1)=Hz7U;(XmMUZ;PaYniOw@pZe$PDEz3Owxa1-P#ym_qUABhirN^|2SXIKhD?lPmo^CKSBO#{&BvZe}eqg{1fD(=AYoWYW@j)HU9+psQD-G)%+9WqvoH$SMyKctNADRy=wjmd^P_B`Kb9PNU!D}=j-_=$VbgTS?xQR^{74{WwpD{_<CL8e7&x4zFt>2U#}~I^lDuZq*v>T;J9jC5tLJ{D}sE~x+2I&tt*_b*A;=U))mgz>x$rasdYtAPPMMkzFQ{*`Kxt>_JeiBcU)Jf^<lj1AX^@_&UC(BXU2M+vgJ|hSnUVTQ<hyiE3yB(^>FNPZR6|f0_W@N0_W@Nf*>DtT@d7>t_y;E)OCULb6giVUtbqEUtbrv{MB_qYO}i5SJ!dQ*Vl2**Vl1DKI%Fy$VXkr1?kmwob&Z{T;QwgxY)w_#?Ntmy05iOudaXNORu-(SJ%JJ*Vn&Ur&rp1)OEV{-F3I~^>w=TgX{WHtF5o@8#rIzH;9({g!&2J$8f&BkKufMAH(_jK8E-7Ion?9zKZkpeU)gz7SEgX>OP+H^?ke`y}FO*e0?7;@YQ|1z*qP2g8bEeydb^0j~Ap@_wk&s@8bpesQY+9dUYQ!s0Vc)FUUvT#|z4%?&AgdsQY+9dUYQ!@YQ|1z*qP20$<(73y!Pq;|1x}eY_yOx{v4l9QX0sb+z@N?lU`I-)9bdb)VV!`aZMw)I!=Ze1ALRks79a`o6mJ^?h~c>-*}?*Z0-4+WugCeV^a?`aZw+LkqLM$?^OGKgaV6{2b3OoUfl>xP0{U3;Z0<FYxvAi;POWtgoKqXy46m&ezXzwC~cV9?Cbzq*Kq2vW|70WBYmdc~i!ZeT}c5TRC4pw~GBX!{(!&uQ^{oU(4aUe&~Gld@b<R^R@I(Ubnt_4(R+G&jJ7b*!Ve~Gve##jIn#`nQ^6`V>(|y$4q_Xe!JdM&sDV_v<tp|uB!du`Q5kEZ9eKbuk-bD-qb0xt*@RJM^7KJ`Kag4fv=xCS1moy`1<)cevaqk_&J`BJ6}H^clqo0e=bzE>D6<8?FZumUqAQPeo+6p2O3|$hoJr7I{mvj#@FvTIA6c#kWr|JT_>scCE`;@7+=44;e7qxMf!@()>rR`IA6aXlEZiJW#Q}hLjqsD9}=t7#;!}$`zl$R1{hzz_u_p0-b?)Z4{Un%{!HvdmQAnTw@I%uaDnmF`$Epw?+ZC!zb_Qzquv(^@=@;#1^KA=g@Sz4`$DN>vy89bgVMh1KUvQXT$r@p@O8bVpB-&|{l3<;_l&RK@5(6py-ly)6LY?PPt3ceL`JfH<$T?*a`^7NiLd)r;H!QWy}MyXvi|RU-T%F21MP9udwtpu?n9=%l96njI$w{|__VKWK6-w`&oRH@=a}D|uje<Hznb6DM@ANz^62+1@%8(hv0W+FSMPH=U%$^8FO=K(`u$Sp>-S5Yuir2A?#N@0tKMsMzJ9MYmR7)~*Y7nsU!7l~{fpc3==XB*^?SMAZ+97ApO>AV<Ncy1XIo#tFNCkx3Et()Y(1#;jPvz+CWr6Fh4a;VCh+xo=GC{1uh(79&#~@$a<46?TE9hCby{qWr@m8gzWz?Z`T9GBARqOeg7fuv3PF1HokEaaeWwtlSKlcFzWPqV`T9GBAierdA^2VDI|b+K>w+M?x-M|OzAgxSbzKnTqpk~rdQjgf1nr`}QwV%@9TE8Ie!li~IrVdppgih&Bq+c7P9dm&^_@cCtM3#7Uwx;LKKO{uUwvN_>s#k#Q%?0gPU^qkzijgff7he^V4c>c-76+P^?gw4g89bR-xEdO9I?dgr@u>5zRN$B>r><F@0(Je{oD9CzK2@cXsJ>4{Zwj)Q`T4CVQD`&uazpj%;c}X^HRP^-!b%6+mVlV*DZ6Ue+BMG0k4GjK#zn^+QgK9PLqGq)~DhB*C%cD>ovOSfA>vW!Oha;{CJfRUP%bAB81nXufw7n;kEF3^fg#C6J8H*@MBEG^G5qI&X4JSO!i|MAv^^g2T$<hDL=-e6JgOw@OXGE`ZO&1EIbyD5yDRr!lTeB@D$203LOo<?f-_Ier!c|z^_twhtUt=!|(<4KX{~{*P{`ehv)(Fn-#Htdk%d9mSaDdP-fu={76IVq7T9na;!A?0>|#-b6-E|qgTT9;Ru=nAN8z$gr>m9Jga%w7C#Rm+z7oAzLMiLB7`5Nt?#Ce@5UQP2#-Pg!lHfPG4N=j5A`$(eh{q>KM1?}sZYJs=eJ&<ZG;bd*}vbl<I#liBD|UqUW0xFyE<A!2(R<w4fHGY82lA{QN*g$<3-eGBlsftYV=|FVe0N``q2*h(k4H)am+ZpiP(;}mGp0++u`k`dyD=leNp=6GqjnE-5G38M`e3v#O^D3eSj8=SpEPm8nMTgbYG$$z+b{e*hkU|Z=<|lpkKmYz=b1LC9UwqeiZWK8bY`^A$$oT{JCdC_%rlkSVB0<vmsp2k6eD__M-tI+z`zRH-sA#!cEY8@KtDjG#^|5J>gl+2TKSa_iPA%isps$QVwAW;ZM+9u!Qi(o(*A-5Uz(dfa}2z5yFq44dF-NZfIk;F~6-FA$$)Zd~ZTs+)D^IMf1b1UYeo>;ihmi^kVp8+P)bf+=CFl4{Z+L2lpg|TcDS~E#Sh0u=K%8=tr(ke$IH?25&(>gSWt&(JXi~?9R8Mr_d}|RDS0vv;e%3eNLjMU{OhP5<P*x5q%9k0iU36y+#OU62cqMPvKALPa6o~_2|c5_8LG~)(fl9Bk0GlsPsSKm8AO+Jpz9S|A$KY|JW8zqYu}E<y<M}MR(p8?j6ZKclJi>!S(3hy-6=R7JVp^y_OIjk3JH~UWW)zK)b=+=<5>*;im}UiRitN>~)Q3cl2KPUix}>(uh7y2&bb>;imNabhHQjH2N&s1AZ2sg5C#Dfv2H8BiU;<;pv3%{b&pLez+xC7#1x8Pbb|BLbw;&67B^@(IT*DQFsRFW)i~v&?wvwZiN<wMT^0r*TSvfe&i`S3%wSW_1RQ-7VOF(Ea%4W{BC&%`$*i8kY4yvRMI`lw(tQ$cn2X|jK5z?d4Ki!H$Q$MgnuT4&!T5w(Vt+^AK|m`4}|dde%$OIqn#h^(VJk=8{ziw4TNx8LbwfjJ=_Lv9kFGWvP#~fH*uWSr1_q52>(FZv!s&{z7hQa{(<zaOt&PIQ@8`#5$*urigtoUJHt|ke^7sC;NQ`6@bB=S=wGntdH8leuiO0i$FuskXIXyp&5`VOyqUJWnQ{wDw5KfXDfe%*ukat}t+0gfIkYn@A^aC*>r8n>Z%^P(Y<Hr}x6>ZdH(Jw1!fnu>yzKTBZi}ArvipPZ4e0M)cApWx1^pA25blVchb4qNQMU8crRd)Y{1@AQQOCk@|8JZ8*hUDyj%L8G!wb;?@ItshddRcfA3o?=T?8M5GtfzJ20RfR4Nrt)e(d%0-0a6bLU;?h4Bi5-KnKDr;KArV&+=gSJ<sYa_&s<wItHE%k3$E;<KUrwG*9u@YJRjt8^WT$MJ%_3zaoU+BZTiFgsT(6mlDEXdp3jzdNzc+qU}7(q8GuU`C!o$xGU@>{N93S0oc{gC1^p|)#q{aes~P&#?p>s6WUt%d2|*$$lqsw!g2QDi|&Ur(1YmygnqT3zPF#eTt6I?&{u_*6NBg@%iw|NK7P{>Umv4QMaRQK;c@f_(HGG1@FH{)Iv$<`k47JZN5e662pogmSQtW`jfKY$L+F1)D4+0t|2MoFvExScEqE{N#?5BxV>AA8>S{UTemTCI2i{_yc#C}9ydfM%_rq~`6S@`N1ZNP!D~YWMV|FWJdMo?8F}|NUU_ZY{SnBzGFMFH{yRj@RV_kFz<9-FY5*-3(paak$@BsJ_c}QM|i1%sp_Y>N`kw2h*kJxeF5dMw$o$-0GXUF8tXggR`(g-(X9%)1fH$|JnP2m=3OSlCbC4|3@*kj4D^P%}+(OhsoIE4`Q&<HGgx0n4-*v%)x1JOZV_8cYrHTsR0J&y^?+$LI<c}}!O!n`M39qk&)o*RYlLf?;M&!58Yp<hR`=UCydP^lAPH-8r(gdau6!NvV_GZXsNO#0eP{yrOZb3;`>efdcCxkgy_6D<x)KYW$Hi`IcftHK4m?DLJxuQEr;-0Q}0lN1}mjZ?DEeZmsLSE9$^eT<z$#9s1o=UL$ujJH>bEu`JTm^(zeYf>zWo=C{^1pA3@PsnFGzfbf!xDH$utp-<x%cJGs@^EqVU)rZQENvn>3Z4l+iuQybg$tm$6Z(L#oadwtrOp}<!rxJkQlH-u!gqL9rJe2|gbSgUz=hzvXhFCj$IVORX3XV+BSdb-R&L6DH_?-^)sx>jh#18f8%4c*L;TBl6D`M>D@&c$K&!zu;I8O(a98+!bUXY${55(4{u++bU#>}*qpo4zx*BbUUISl4UvGvsh8xp1&DghD!ra)5xw9E*++5m#dAR}Y`8y#jbMJSw=goxh#b_b;VmLpV7tRmoL36>m_?vLkgx^}j-@e?BifApkBAiMH*Ysn6AJzTn2S3Snb$Fp4&HT6tPxKa8^sa>cMIRu9??dl`oBGj6`Ulzo7Of3mfy#Cr<<%iS(S~qiG;v$X`-5NS-}`Zl5Ps0JdYfliLilz+()_xs?ngaBxIS6~t`FDsBcC62{P;6sL-^N-4dHJiHiW-KKaFJbhY`Cid@y3S53>Ds#D?%vUn~1s(2u;RY+sBPPvDYl3zuN~BFZV{Ed*Z#mteaNEc;dP>!PY3m!VbQTK?az@S_@96~5Y&N45TVLTkcOr&lG^v+$j05m@xP1TMz*b#N3d0Y~9hXeqcAd@WiAz7}qdmW7+cE&OPSrlMuxtNB|cG!-sNnF^yt;KFbde*10w*4yx|LW{tqDN{+b6kHN6j+TIn!$r|za4Kc4h+Ya`%64hA415`FS`n=V%h-{zUKw2gSB9l8REpU2CD1Ccgzyr)s&G~I6)wjy%A=Lx@^A&TD*Tim&-n2&x*UGQk6wNZLwmzd`!T_frRZY#M$gVWX=pikI(a?=?_pc=>_NVw-C)UcB>9TYfoHJqba*e@vTqmm7wrJczWv!>bTTaaKF9u|yI|S3J^PEchM%IHo`hd!yFYa_865^cM;+}#m%{C-qt<8|EOT5<Kk}ft;aq;Cq}VYb>c)_a7a8}GPBahu{Ok9P(!QRK*g09|;sPmFPs684BV3w&E=B)?C4|eN7hnnD3aDIUR3L;aq7k?vTnSBqE5S9;TyPDzCYl?T^GN;_JH91^WqiNr+41yB#D*DLoJWLHQ?kdWuxM#m!i-V0BrG9Z9xV<_2$w~R!V<z|(892Ua4ED2+=TKA%Xv`Ff3l8{5O(Vb(fVwQU!OcnrDV5JDcbM{+V*?Sy~6nu+BiR23a&uglt(Xv%kj6eXnFWj{#FJp3#ZbS)zKQR?%BQ!O@&X>C*>S;j5UJrzw}Qz7oFzs?%WjR?-IhUKZ>?uTYO=UetE5DRlIAdM;T+as9Q7M&^&M+#*%P^e%zcqB@f}+DfZl49jyk-IsNh!yMB-mUJ|i$c<qSY&qT!TCps6F5WWIk0xuySVOc9wNy%P6R7uJHn`l+E3M^wvenSg>i<DjX1wYS?e!Pgj2_N?36F+vMAHehcc*Bq9(br%pkF1X_LH~$YUK6p$csycxBikqa_=4kn!7+pv`LToJ?BE!}tH@(0yoT)`{rHCbz9BE+wSF8RzXRkYJj{>P<g=Q*gwOf$3;F#*UO!SFOQ{p#x7prFovcL<z%oa*WFB_&vhefN)i885d<k_W$Nz(43%|%5Rxx7N7}5tTdG@?tgE>z6QVqOU{8%Al1$_q=eHRwp4VR2q{g&<Bu;?=QTlghEp7rB#Kc*7GBhWtZ2>2oNUicxnJK7QM4tGM^z@6Z>GEULDXdAdLT#pdG9_<KU58sO33*QRggZ6>%f%~G5!+qi5=(F%}cnUfXo&wLM?&eaLbMb}EdCG5t`Dg`Lv@|SQ5*C&H=Cl7icpk@|k4}Z>!!HuT)6fy{H24YhA@~XSVYEB^Fr1Edg45y7Xj`~5d_zK8-arV;tD_as%h3ApWpD+wE?faFkJj_D*RjIo2;nsJdN>Vkjou2khC875z#ZUjXkWM++#4MZ_lAd|Q{Z9nWOOb(8J^>1_mw$>@M3fsyck}J?uM7byU=&xUGQG?9e6Li2VDX0ftRDNz{_E`#uZ(Fz5*|Rm!PL%xi%3kg`S4p98`)vUK%b1mq9DQW#G%uim;g<VbMzPWpEj^1YCk+2+P`}ChLIOoVU|hd&xe+=6sF6z~?T0%prtF5W<i7G24&fe%y&Z20uocI|<=h=oPT&<!~*yCRzoq30EenPzM#^RH6#My9)bPB7|$BSHM?Lj@pFqTyz0E7nU{1QuIZ10sJET0y+nN0e&1E0Y458MIVEQ!o$$v@G$s!bT<4vEbD|_e(d(+D0&1w3ZFu=;8XA!^e6ZXd>;J^J`Wd3u_0X8*P<y_|7KhKzX{>9=uhxj_%k#M{tW&IJpz9O??HFNd*BU(@H%uCEV>?E2fsuJFOJx?k?2}<J-im)iSB}T!iUkL@L~8QdI~-X|A?M}e}vDW=izg(tdGu9-<J?YSpQartDuG9Dsa`5?6#>&6iry8ixxwR!o}c!B37mS{vm{aM$f`O!=Iy{!Joq)qaVQ^!|$Mb;CJ9mbOW3TyX#rum(g|bI@(gWBIzolFGsTH3Sl>g2)lVk_)hdC_$B&*o3DiDC-jy1=sZ|-Hawesggds2q?E|@fBUbJvj54uiC*YGPSSgZKSxR2^QfO!@Nr7Vc6sDJy?>3CVs5BkE-N|j{{ZWx^br'

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
