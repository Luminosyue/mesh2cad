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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/614459e9cdfb4a06abbf2d6ac962a08a/part_009.stl', 'relative_path': '614459e9cdfb4a06abbf2d6ac962a08a/part_009.stl', 'source_sha256': 'd231a5071c725f82ca711337e98a8a4feb0d0ffee257975921a11df4c7e7f972', 'input_faces': 582, 'input_vertices': 411, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11575839668512344, -0.10314984619617462, -0.21830399334430695], [0.21337823569774628, 0.03563199192285538, 0.404974102973938]]}
GEOMETRY_BASE85 = 'c$}r21$0zb^zLs6PFf@Z0tC1O2@)KF!^P6#?i2<I1P^YdT-*W)5?lr-TBK;uFa%2=NGL94aJS$Td2{ynO*_Nmt@YObpRTjM-+VdQXP<q}oO|yKtBvb<Cil_slSk{-*|T}-08LZPOY_l&gbWzeqf5xZVtvDgduSQNS3gdj-LOT2#%(;bA==1*t|0@v3<#*G2UPA>J|IvJ=+<w*paGrwcI-ExYl!lLJM|tI;_wHCb_xq|ye?R#WXV9ibfG|fl>R^bN$W_#+G@rAY7RA0h3+}vP_x~+6H2XtN5r??%p|_G^Gor~cNb%nZ+7z(-(GgK__pOa4=7&?Z;d$P{lvEiXR%5Ajm^<N`S#;VjUZp~EnY8nOaHu2#Mff;i*MelF23b$U5R7q-AjD!O2jT1uc<%A?L76nzJ1>k#5vU%`DAP(@hu}(iEnTCK;qj|4TB%BS$tcH#nI}uKI1d|F|o*h*oU3c|G+!(^*xur-+%HA^beT3SzZ?@kN(|nBhRdF{*>1_DvEEfeII$IeTDu;g!tBckHxo6&bvkGQer0J_&oh?KK5lF;inFl{<dX>QO_J{4=P^|yDYwbVHE2BFunL%gU2$iz2G3kkMl<V6FJb|cZi$+ZJuUyX7~}eH@nu;zB=o{@8xfskVAa?y4;BWZaCs}&3({yy==9!!p~Spe9QGs(%*>b?B+Yib>?Zj2!y{)+v1v!e!2w4UAR+xGdvV|ZY*=qbw6l6Io<qk>t?M`1Mz>Khxi-2!k^s&c?QkiD*2y|h?n1I9*a7p+bO<r@&x?YY3ToGH~bB!#n-AX65n=qsrcr;lj2*~ZeaZ<Z4<v|O7x$<>7eWT%LurE_-Br|&C40zZaaoJ$4f63^?iI<<{5Dk<9hflk$n*yF241*(};g{9{kCPmqhy}!jJARag3r7mtB2xR1x&|EaukVRw4OP`MouV__q4zu@4uXk~mt!OYjR{M%`|#llf|)H89@~e`8&K-66i^=Ds+o_r+TnH)bRH{}e3!%}ezCI?1?NWKQJMEXlo|$s3~1+9&t}>q`E%*RL+hcuP{ny3Whk6?Dnfx5d21e2YJo{$_ZZSl4;kyl+T<dz<v)>m{zqxYi7>B!6pL_?G!$lBaR!4aO~)*{#2R>SG+<ukbCEI%6Gg&6D~&eJ%F^jJvs<jB8DmO?;!&7_67y->Ad8?3ma4iju#%+gE(^o}c*kt?TE>>ow&OXS+Y*Z=5hk;>VS7^PT;*vR4sjb^+8U@+tC}lnZqmTM&MQ{aCM!UobEFMx$&J->7m0`=L`H#x1`H`E>J#|6>sRQbW*xsE#`CsRn<+VVq0v)?$5w8z6r9mvRo<3au31D9|L<b$=QwZ%F+u$y>nhW#SymI}!VEYX_`L^<O0)+Z7+wGqN-K*RkLn<2hh+`sqHS{*N<Bf5YsGJS(?C{%12I{~TfBTZ=xy_0eN0-oJy#A<kbXaUQ<)Mn1Ksz+bTn=ku;Xn6Jl7%=h#l<bS(~n{ONO5Z9yl0myUaJM0Hu-z}LYBfjM`@~l=H`|#;MM`irz`iCS=Vn6Zix!$_@_V!uj9J8h?b4=zjp{e+0tA930|Ew7>uR+bxKdF~ne6v)0@hyI%{&ee~rvu`AsxSR*t$vXBmY5#m>-|&XeBS?w@2|ng^Os=pEw#6ZZ_W-s<XRu2MIDJ_FFqgfe_w(7gbszp*C*XaKD=+y<12}8Em`!i)W<VS=B3v^CGjm8N{Vkg_et_M^EQ(H+Q=H>8?#G`Z|!p&=UB?d;#((u-R;`nxYrDE3P#Ow-EaDlR`A!w<9&DA8~)06;_GSlqHf7{W4^)T;n%%lmHvOfIV9uyOhrB!4~cI%=W|&8?pB2OW}BxH$Jp0h;uxbBVZKr0m%H{i0#_kUoj=4k7k!ra=B7l%*_#^v>=CgNzwUMP|D5RNTT<VJe{HnvAHCiQiDMo28u@SAu}sDdpL5vN*S5TuI96jk;(zfxB5~IZwz~G$MtF;FyYz?nX2uDaZ|kh$>)je6&i<D+nb#YC_?y>A9V~vOu;1uwkJ7Jj?XQg~A-?5xZi%Cnx+A`=V;RKhx87}DPTv;Y2KR40JTb4T<&poE6>j~_oRu+d&_lQQ+7DI5H`-No%g46+C-h%93Gc^ow-Bdx3-RqizNr6<B&nN`uMP6q?v3l_B(Ebf-^9-FkH(@7VY=jLE(;ak+Puy(*ZxNIIQVZGqW)7#ACx*rO+tO@g-U<hytLBa+AP8?pMU%3i9(#EA>!+=Yr%gTjro2pF7a&(LNTxH2N0jvQ>{j0<ZqlroQC;u4xd;czHR;AsPnTnOI&^Hlv`M@Vn-xTdyXiHZ~XKKby(j}>Y(i@i~SSy1b(x<l8^CziR7sjc!v6)-HG`9CrW%X_Jdn}oc)cW>5fYNx581kuY1I|)hZyqS)hi@OHX+T@yiqxU!SlE*RO$hBv0*TN%4*I0~X5PT}UtIs@}f3_}bvLi`@L3&BeD}e*?drCcdR)SH$_p#CbKWEb`0{ia2kt$+%WeAK5?p^IpiO{A%n6Yi{vv+ai&_*In%M8n>`-SI$EGa<MpvCtMNVK4z}?c4H;(+q1`uulJvial5UUFZtT0NS;>9LioJz(tqh7>tdsCyzeO2M=id)<ge#ifjXaAiE}c4HSw)K{Eqy2|8Gg!jQ7#ib*N8@OAB1b)z)uDo;5shJ+0hX#<eWif_xstV4w7Bj`eD_8+Ay^EbF4T9ELgv??s-qKgqcNo<I2yh;J==6ZxEaF22Qj3UOM;pl+)#pq?Er!0+}R{p%kR-)wLRKA+>9b+A>wf_d@2!n*j4^tV2|4WIWd`t=B`@8!FQ)7B4l^B*a3%((lQZ>u%3&-K>Ja1Lku3_oF}%-6PjJNCm1?U>A~@Rx=7eH_l`Y}v)v8r8w|bn|5Fx72>(TT1xOmESM-mvh)Qps4u9nFjOR`~(AW_D_Rfz#HfG)StyS7X`{bw~cx&`B+;w6yM(Ip7{C)Pn^#wTBASjTb%irciJ6u-B(7og;?K~Q{jJUF8fo<(_G%~_GEL!x4qafTl}o+asSX~72>B$n&ax5$9ADU{cmEvQ+gtw8gb~K`7gKrw&#f$_w_)$FMNhcfBXK6=wB@t_HEy3ILE@Tqkr(cjq=)g{`{CWPU1#)llcE$r#`2HKdxe=)G1Z<I5*!iDoVx~d_(4|EzByu89Hl%^zU&I_mjhOh;N%@+2lH|8I%`(&;9V5Zh?P05PpTZ;j;cIM&WtkY%%ygA>(A6a}OlGzPyb1MslyIqTbQC|A`C|-|ina(=~rf6+?V$dc&0Ywz-Vw$47P0|7y6*>)&&AZ4<=*BS6;0IQb6uCn0T6hrlLo@vR4X!@pT`lJp;wggR{Qi#Tx~W&fCivml?PVd7i*=@D-8ojxGWbsw59@{6yf8H+f)pEP~$9dq^V4O)l0)<M5G3Hd~1k##YyroiV{tEMA<;0GDkd0n&3i9mg(?w5Hv&nsK?1?WHS)(p2i(=WriBtNx5*3ly$_Q|sq7&kIiW{Jb+5&iGq#n+F&!~Hhz^DP_JV_e=3TV76c^9@UO_jyg*g!x|REOoXnN<^J|Zbd!`zGGyZ^4IYk6tD;J`J83h-x2o-DPu4%o|DF!3~_G$rF`q9&T}(iUT+Q{pNwAezR;uB;(B`bpj+Ln`F=t@SHvUF^WA5O_GvG^KI??rx|nb7U>_E{i2OV58zX<u&keL(m*MvthWF!)*0>*={0MP6UEAckuZ-@`kY{lCD*5~7*|9%czQDZN@02*U)dO)qlkY9}f3EQ|uN>WQUGsU5_&+~d>AJp7-&to{^%y*_C4Pn9tk4R{Kc+~Wt8Yfe%#%3fh9b^Ek9ZlE*Hg=05A0`a3h~XB30Rk4JD%5yc*nc$A3aqjJlE&Q9RJ<@w#Hw4+vp5q<@eJ|V%(a=#5bPV$GNVfy;KSK8+S-OwO0?1x%%Jk2i+qm-fbP5jl%u>i*ksw*;~$Aiyn>p*c%m)f7l&-4mozb>_dH1HN<)Pp{u;Vigd;Gv0a_`@9qbuA2v|NwYFV|=duf}-RfX|E`fEKZHfQhesKEQ`RT*uwO1hagV8hod+V;3=#4m$nPgp@`^TEQFZ%DhTu0V3Z3?_!=$n64ka}8sBuE`BU;4*?Z=cwn4s@%t{m+-j-289$k8yo4#w~r`t<Khjp@`pOhU952{u=jPe~d)`np0ZKIt(3z&oQQscB{YfuovFH1*Rbm&o}$NSX}qBOm|xsOZIcvS1BTp=PqlM)a%hgTu)y|B7WT95YZQtaSq&>g?i4kyX|MIx%9j1qJ>#8u5F?ze%OB8KXhDyI75p_p3dh5qv~q6b+`WV&oNhD>;8DT#I64k_i07fBL4#I*Gm5z&BWJouE)43l4L(vypH1e-D?B-k9aUj^4Q^x^YHOzxBX+y;fd?=l`Z01b8p4@e{~+7%hpD_?FUPoSDdTwTz9icOLu?pp%L=Bc1^5Ti-U-h+Z*R$pV|0)$vYnY<cN)~>u4k;pgskU;C?T<Klby@Q{P=jJ@E|s7kVvm%z$%<V>^ramTD?_+AmkYIriHX_?@HYN`A#=;CZ>vHTXwou9Nw$UXSORO1I!A>~vd4t;ikJZCNs@k3RdsQCHt6d|L9<@@|zpE%fzPpXK`_Yo|;29xnSm%<H8l`@v|Ni1!73!@gM7%S?6E&Hr|vn9exg>=PS(dsz?pzRdnM5#KMSdGOu+V}5vuanE|8fBB+&B+pAv5&u<ceDC%q6rY11dye?oGocRN*|C3izC?V_WwI{TWi1c8`u4J|aE@I`hWm5++CNXE&bCHR@tnB&75Z=cBJ;8rv>tZ#ZHov0E^*A~xc<^N8~90{T9Yd~<nPD7L;dGZl{ltvFMQrI0lqP@H2V7oZIRc5J|LgDc`&a*-nh@~@(<!C6_;^sd2hzL`PItHylm~?<9%B5E5=Qi5AlON@VQ|g&*KvR^F!>1vFB{AzFF;-_*%>!SuZVP3h}MKHbtCu_g6_jEtUB8t52oBWn_L?FXKj9^xyLmaXwAJdY$q*?)HA?{hp2fzx#9hDXE*eI1~IQ{x}cUFTr}zxAygwe9W4qq;B?}zT(^dm@K~SR<0our)_rlOB!Nd9UOAR)pzbIXMOYvxx}}uDK5V8=!VQ!^Yw>+XeHuzzcyLsy}c;vnXLnSj~Ka+wvR3C7DvB50H05FDu=qwxC{U3AX!h{sD%DKA~COuL#IgmZ+vU!zwmj%-nz$8@2tD<emRftEf+S#yyhRpd^@a^_?9V+QMcP+yIkw3hc-w2;2^hk(OS1e{|g}!$5J2>pO0kjfcQT)M4Xcq@OQ5|VO|g3qi*Nz_<Z6ud?WEX=6jOQduKyXw}ck>9)DQ9eKKyp{#f@<dobVbtB@ysXa44(hy(Kbz~RWpZ?gE-I%%=5oPOH?_&sXl^YwJ2kk3EUP`7roa6jhsb4I)6X*@EKk8g3r32KHs<Hw_JLl(hraW&S}*Ow0y-<W>rkgM<f9^dk6E1s9vPKN)q3FZ|&N#<n<iA0<gYmiTPGCT*>nu9tg?<4)S!t-&TQ+h7q6nTldjhu_~D(`&szvhScSIxT^*Lxw}7scyh9eYOMyz^KLzk`YT)Vhv&omr0ghIT@p2lnIoa$qIa@zgfNfBqKF7t_~az2b^sKkTf5=d9ivF|R83w@dtlVtB4>w;Ah|bQ$wqG7I@v+U8b&XP#!^9hh(GdHBBjMUw;>@BTiFdwj|ci5qnr_sJJykmr^Rc)vfWjO)dYSoCjc!S}P?Chl8S9Y)>8rolN@F*)+=oPa#9<dOW1M}2Xh*7OwmSHCWKS~k8y-Zjp^&o~U{SZKKuuD;pkJ?eShOMI>5S^Qnyq#f8lAMv>{ee2v%yx(&9OMj=YpD2L+U0fI6$Z!GuUyMZmxTPnh-`9&6cgD|>zirJB<p1n4{L4vLm;FaD-+edS`rF$lV0|~-#6CH))GfY!>Rs%U#beQbR~6i6j<}C}tXIX?OYK5@`g-#)tYfC_636KI5b=+m#6G{5R_0}G^B8fWyJFm7W!-$OaaQ;XN}`_SpJSi&sW0PNKOM(&L>8=%wz>;^eqU)h_t9;>M!H@&PY!*;yvmftyow#cech~NC%#u7OEs*gSvSIMe_D$Dh<sa=M0|dZVW<Cp)zjI3UnA`2&Ceu`EoTO|IQENI@f?&3zUB02iDUEFDRC@MGM{jLzi3kzNF05A&J(Wt#8UHT@r_}5u}?RRbIZpPT*xiHnJ`oOo7T$6zg$Pj)0~ln`F?DK_+dkk|B#Cb)f&6~D>^fWZ=JXtjwd2VOQZQ{-8#Aa6FOz8AE$o*pV0Lv^Z)fv=*pHa^}qcmbn6^BtZ}sEY>F3Ae<d#>_ouca_b0caRwlP1m!g&?mm&vH^OFO}d8xU{dCA_?>|}3pdPn<_>PyW|R+^3MOU}xsI0KvFjMO~jjAS2bCbAFNi~0lEi=2*{nw*ZDicN7!YFe_=6y%iTWRB)Rb^a*!q^2Nyl9N-@l9Q9uuqn<#)yX-?1*wI|1<4KB6gQ!EA}j4oZbEKJ?MA*vy-MvyR%$0-CBLHnLw-fh=mE{)0ai_MZR$_t+T@nh7UY)X4%GJK4&?6C5VF#q<nH9Y)G%^i@*wIE@*wh9>M*iWlRTC@gBng&I-9ICl01Vvl{%d~l{}t0jXa(_hB|>fhCGz|D_QAa@=$U=YJYM+at}7eU8#M@UCCXjy~#>L$z8}6YB#cl{0p1ncGS*fr5(xb$gQbu$gRoEsLjdE$c?E@$c@Pjs13;t$aSdo$#uvz*c4Zy{!CUHOs+((K&?rxKrTtGPA*9<PBqBI$%U!4$c4$J*c4Zz)+1LV*QGWhD{V!tOK!@hxGl94xh=UDbpW{+c{p_vc{q6_bqaYT`8PJjqo|X~qsSwubIBvf5!CtQfz&AKd~y_d9(5sE=>qaR@*L_c@*MI+>S*#r@;K^1@;LHLY7{w&W6Y$^A<tnf#X}wETUSTx&8D~`n_>%_;<0Rsr?V+uNgYal<7jWyb-)9f&I7EPVsC0TvNt&&H9t8YxgfPPxga@^T9zD0E<!C&E<!FqEk`au&P^>tR+@*Lo1B*FNlr_CsX^7eUvmCK$uG%&QG1jBBA;PX+=JSY+=JY~(ds)|b4P1R?Lh9pK250>a#L~}HpL^UW68f$H&Vxv$8udavMJt0T}j?WK1x;dKg!pNQ?Mz{OU*;hOAexzAqSBwQp=GmlB-b5ldF)cQp=L7k}Fe7lPi-8QS*}vk#kYAk#mtVP}7k!kiT$WtNs0j`~5cg3;8kiBKa}-F7*)kF8L&NH~A#_0QFDu0rF1jQu0pnChBbRCh`JmIC%kiCUr7-CV7UV{pM(s9Bm+*Vv{<9JcIpBHpPS46i=XrlP8d;P-l~;kRzx|$r0qa)IZ5{$*ZWl$*aiQsfWnh$@{4n$@|HtsJF?d$d{;Z$x7dlFOjc1+TYZBY>J;z-;ke?zf#qi_?52}|HyOFoBSg=Cp8~AC)tl$knBg!P7Ndn@*K?0rZ_XT068-`6*V_G75SY8O-oiyaS~OXcZ!w%MNT5$q@E$)B%h`BAfF|NP&<%A$nB}k$?eH4sP)M$$aNhp7uBCypX^UAKy6A^+J;<~TASL2T$}t0btL&0@@Vb9b9OYF;y>6FuVqtgWmCMKx{<t|98KLtjwT<W9wi?kr{TG*&f+v|igjvUvQ7@529bk!{syoqE=H|FE=Ddvtx7IIE=sLTuFNyHD4Sw`YA&)rITJMlITP87P4Nc}s?J=+N*|LykRMR*k{^)oP*0NYkQ1l}$O+^a>P~VDc?We9c?Wp|bpd$;c|LU}c|JLkI)fZZo=BZUR{9%xB6$>>;$dux!>9wvVdTD4ldN<wxi7g7o8m!iipNnWkd;m$k0Vc`Mv#@xB~K$qQCE?p$SbJZ$t%d)sQby=$a|@$$a~4hsh7yd$%)kK<V5m0?Z0#U9Gl|P)O+O9<nz>L<n!bk)UV_l<kwVnroZNE#h<A;$*L(%P0x><nw*lFot%=KjGCF8jI2>pku~yr4XV!Z_iTzEQj^F^Z<3XsB|juzW>egS8ba<uZcA-XZcA=PZ9!IAm)wk8NBi#_ufwJ|C!6BTY>Kl`{mEI#e$)bFKXN|pzq39co8pqx+T@btiqv1o70IosqsgtwBdC9nN03)j*OFJ07qTf{Otq31ljl*_ljo6_QKQMr$XlpK$Xm!Zs=7AV_*(Hts!mo-@elL@$Ul&MsKv-W<gC;Z<g8?0YEiN;ISbXFoQ0g8nu(mA>_PP+dyqeAP<0LX#HRQO^#S<_`2zJ0S!n|K0{I{{hJ28`kGg}rkGz?>fvj{sc{6zyHIl4!B6${hJarU#Jb5^E7<o8(2sMm6gxrtXm)wusliG*eliZ6sh}?@jfI5ymfINmejXZ`tl^R8!N}fYqL7qciLfuAQLf%T<OWsP}Lp@I3Lyn~;l4HrosOQMX$nn(E<aqL7>Ur{Eavb#rIgWgS`kH)#e1-a%e1&|Us?PWOe69EeH6>X!#m}k9$f_xRO4Z1!DSkv%=ldfz#kZ&r$x1JiOE_9FN2@?BN3KAwO07k%O0LeP_$NneKy5^=MQ%hksO8AzIG(|#IEbyhqt#<mT!~F_88*emsX^o*#wkuMK`u@XbhN^bR>aYYQUl3>>{FCYaTRI>ausqlYE^PIa!qP=axk?9wK};vYgB_x@y{-G{FzO0V@K;w4OLptBbkrq|LcFH@!ya7++TD1A8UO3m+oI5y8dObBi6rPCN{2@LVaJPC3F0zzKE-%W}^Kcki;RO'

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
