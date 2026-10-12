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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_000.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_000.stl', 'source_sha256': '15d41e881f8388ba7815d359bcd07414031bdc350b840a12c0b711eaa5b7b8f3', 'input_faces': 924, 'input_vertices': 728, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1844944804906845, -0.0222331453114748, -0.336747407913208], [0.1910248100757599, 0.36912694573402405, 0.006284593138843775]]}
GEOMETRY_BASE85 = 'c$}r32Xxg&*RExo-fMu+4!sk4HwXyb5Fqp_dN;k>aOkER)4S*$(|Zxvm>wHrS|C9LNFfkN=%M6l_I`DKY4E?+UH9^>{k@OgGoCXVNu$wd=A?O(fFxNI{+CZF*mA02e5)uT(kNM!QN4zZ=+~py@Y2CU#`-B4$QS=?UD&L3)8_5{lu^p~B0YNz?=h@MHBXTmy{i-{=_%5C@URiXx&?O~JgjFg;n(jraCk4vAKtgykY3hy(aPnjl=PG@R?-vd`G5SE$|{06W%c>fmU>g%x>`#VZCBI<vF*wKJ^K~6#*sfV!$q-ez9`TB=5R`{ewXT;(^m)j{UCfLL*Ny$ZFGDRBUE1#Liy-BcAj(k-W8|F_l~Mg>Ggp>(&x&*C9hHb8ULa3m}~E_U)7)TH^(%KC4b#f_A_*)@_1VhK11c-xS0JPj&k`MrKa>+&DrE@gF2IM*6(<hw$qH^{V1J@zE@BC@|@E*BC3(EO*nm-_R~`(n*6SnxtuR*{6PMU(&U>TKU4l%jesc1=VctJemGw|l_ymPs!vbX@#HJPkGcNO{1r#(yN>4cNBt<h*MCcl%b!x3d`}~j%A<W~PQEvG9euAFv7hqs^r+7Hd(T~={3ADTeO|1{ew|_by$!0JAiqpW@{MY(__*Xfdy0I&Kd7FR<`I;S(t0=Tr^o*>`QFA)$X7>xN5|2ue1d$v!;{NYpQkfiqrV?Afc+9%$oKS^e2nUCNFVamsRe1j)PHhOeHuf$vLE({>e)P(guYiDnT`E_i}G=)P>l9h$@rR%zux0LAK(8pgX+h;NWPNoIhE7gI*HGpamV?5Ieqm4eQ(icl#e-n2l?Kqp_E>Wh^Kr!6K1eqZNYWguPdo8ksmaIe66TX`RJ>1(|(y>x90LxcuwiH64N;Sl**jX#@6JkC2O8{`eyt_@{Pe;__}zSlzd~&e)7#u{mwgm^NN20eQ%EeSE(G&-cxz??JxN}SslyQ@2umzA2IpQQTqKoE;xPjZ6Nu^^Oey~Uwd1ReDjx|F1zwM^%L!{Qox;FFYuJ>b3&LafBksUi*#OPEX3!@somtON0ak;Ui~E>m)SeW_tuZ)>!o;`^G@H~_8*@oWAaiyo|mgRpM=zBXutlbMBl4*2q)h-5zE)<(^XVoYE*CblT<##*Y83;uimyNUr8~Y>e;*ZHJyjv=$8DwcQdhnDumK|y9BxNF`F);`tiQ2$K}6qovtr!*#7v$eD(34bX}+=13CXn5!_xKTEo}N`Qlv9{*U-P3H~>h&--G0T+)4eiRypD&y>H?tstkrIfTz2qaBy?e17&@nRFbLn5}%hlzx7ij!XV?d_Hu!MCYw{(KGUm0i(Iyu5tJ%`JbZ5S5sc5^6NLI9ZJmibgOWH{9fDH|M@8&-@l7;eJ)?ke#mA%zEdAlIkkTM$=7N(p#3tQUD`|AmHM1^){p1s&a}T;<+faYv@>d>Ozf}AO}_W?QaUb5$83Ck4o*eBvTPL}_vxdkJlbvZlyiTz*T!M4-vi|9nGeQL`da%ae>KwxZWoQG+>V{=K>KUl?@PYgEiavK-Xia*p4Gj%$@gxq$k*@1{^T169-pLqKBS}c#@MDOoW7R%2dW?Cz%#!7bKWCg-?f{{V?<S^`ca#oC*RN)ay#=fIh{Yol(U@A-}mTx^z3^=zUNsu`QEf8`8+u`iQB<rb2<Htf4Kaie({O<MpzTdM}JwAe9!LVT+WTx==}7&&cOS1@+7BUQ|4r1zV_$J<K!2A#rK~HA(W3+X9M3S!v7)P)9x0P-{_sNpSCZqW`D*TE@wm}pU>q+kgvYUbC$|ewk!L7Ey!2iW+LAVdP3jp?eiVi_b=}c)Au%OLG6YTP?pn2_J|^XM;pF=;|g*5{5R=)l@N{3r{LcxKjX)-N63HGman^;=Ul!~KMA#0%AM8Zt6#OD{EdAL_L0AN1^N2@n_Qo{_FhZOHwy=lZ>AeczBZ`+Y4VSx=XP&<OHQ9BDW50JmvQ>h4S2tct)u&eGArP+(^uE;yGhse?~}M+alaz_kLK`ksgj1<orY=nxLrL@->VcF&)09`r^lSWXKD}5KlC^9l`&7a9cXcbt_N*mEVnmT$E>IH%`0;GgRZb&sw>~ujt01VecnOxjn0>^I(=<(Fqc19HCK91!g=!5Kj+Z(ZU#lO|MWe#dj&7j^{ah-lze0FB;Ma8gSkI;a6RA8OBzSX|7I1p*SQwBd^1Z?I{%HM9k`sW)^DKwdRu_+FP`>X&PlB(f4$f{zJGXHxYFypK65{Fek`@SO2)wk?eE+?eE$kR?edkjmASw4elGcXxwKqAQ(i|qee>rWR1e-f57{p@iF|FrOiHi$6^?WI#)cJ?UePvkf3i$_z7K2-r|;F9JmvP}avjdU)s4-xzkW^me$%Ul%hxiiR6n|3I?m_b6w1f*t~1rYCt1u9+P}IBkJI<Qz0BV`=mh&e%^}~@CH|PxxBJiLf1|Eb{wdawZ{Hu)G8@^iv4Hcbx16uLHdXlgs@;fuBhx(cJ^FUOuVu(XzWp5JsruD*r>`m(<G6nAlCRwN=k(Xmuee%)%U}OJ-A}x0Dv)o~9Y^hmp7}5G)jqB1xyJi?-)^VxEjxjH{o%lEluy>1d|!&cwuAhnuc#h9jV_XJe$L9*%Zu{YoW60s75VCKmtDR$V}YAaUw?Rv(<j}|{hX%H&p3T=_Wd_#e?5!X4?V!;slJ8kS<kI-IS&qIfA@NBf3A$=`k&mB{qmRiIVEoWey6XNeae23-gIA6@>U|>es0n?ua9^7=7I0HJ@M<z_1`K7r{6PXuk*Z8p8K<3xZ_DG|B+dI+)v%7<Lo&TM7};`Fl{SE4za(f3DtuVnlj$$Yt^T4e{9%6zAtoK$A4FLv#bAU`|6_G?*5_V+x<`5HwriA`xp8xzVt7fk#F}~eBayRj{Cl5=kv#}uKS?v%l&`bm;3*=FZcg_{;QFkPxJ%Bm4Ewi^1VU#UFG!5jB@ugZGXl?SHINfOV1a!ufO=6pR>;Ib$ze=+~M=3=MLZgda{#mKd<@r>u53ZJ@p&Jy2^97Df#wuqV3DiiN50^JumyxAJoaWpMQPnrRQ{Cdg=Mvmmbfv_Vcyu+t0b)qHB1+GTx!<QSY;G3;C~C@Okw*T`bj4@`bzT@83jl`aiRCe<N4O5vT8&T%VsSs~+I;o$JH-q|d<ZhQ|F@+c#6!=j$ci+7nLS+d2!iC!VBf`MGOR5c}``rR&0b*5rErP>sLW?>IjnHOoi+CGBHzP9O1#udm<3xZU@^e2~hsu=#$<AN>k5E|Prjgeu(5Ur$f%hPiGa`P#{coF4aUZGBIdZ{L@-%>~If_B5b;^mXmG)Av1`!TpH9(1Vl@?t^ORB$sdB2R-@jQv0Vos807m?}!E5-~MMQ`Np`a<g4p*?V<DdbyxD$kPp;fHRk<E^`oEd<nn#@1uYNzAHr@?{p`8K*YDChRDbq;))VxI&!1i~+z&0UQhK9FDEEi2M3b+_tYtswE?w8k@-yTcb!T%vc6*zm3a7uZY$=tec_}`hQ!C_~N$=Br$2gdR#@D=ep7L|vr{0vm8g-M$VKzS?-^`qM1^GMjUrE$I|ANM?%qAuHd1&%koywDLQEXzqad#m<Zyfxa>eW;=E>G(LXIy@=SiV1oWaa0+rzglaS`VV@MSoLcEBUP#lJD*Dfyd1r#Ya-QQ{6Zp^ndi6?fJZ!SDNz~kdntU!<7Wu?pT6+&)(VG|9tS8j+Ze%5Ba|5{duJmTz<csJRTL+`MAr^v5BrP@6_A;eA_uS=imDpm-Eu{>rP+0^pg8CZ3l4vZ<BEPlgbTeJ$Prm<o&zaDw6V9QiJ*}-nmhc&hi_f;e6aX7%tyzn3KmbF4QMqYqXBjm%K;iQ7;uHUyZoU{hu;%TU>spq*VXLt6$gAcKJ{A{hrl-^SFUF*X8T6AGv>0Eb9{TS3ca$p9k=B(7>Ghz5U`i{hkT@ydV7^`vdlnuf1!?&zlp+?j(QkkloJxQvV2`^I1*Rf$Jm73GTOq52ouvt=ZI-UN;mT|1o2z-PP({;r`OO;}K5ZGx{O>_XBkDA1)!^8+!4EE1!H%xLmQ-c^tmp+#9q#Gmd;u?IxF8et}DzzWHPBSCn1E``d08`#t`PbETJj?dfhhPt?;Jb~^XVTQG>nD@qn8-`nCE<!_v<zR>9_Ia6`_`7B{M`4?aApn7Pym(TyRITM_|y}xF?hIAepm#>qr<{!q_V`SS=^gYYs*iRU~Pi))mfU#l^=btQ^&xcx}{V9FL733@Bvhj0J-`0Fx1k51c+}9z-Sr0~){+xe-ANYO2S3{`ZYXk@Ga2?-HPmVc#!|w@?&*ZDX&l^K>ldm^g&F8<j0=K7IOuC<#2@U8u+DMj?%d<mgf5*mCl)vAFl`el!3rerY72ZgGy%p@6yZF9eq}C|%%_-#j?o(~c@pw^4XY#$pF6^Y^_;?&$zeeugX#eczTq9EhuK&X(`TCaI8~OY>9Od-AS+eh@dQ1B3N@Bh*eTyH-*AgDkIEjAbkF8GMe1C$z*KTKwXZy)l!<L<O9hWx+*gtZae7(TC+2nt?zSUVy&->%YoWA$Z4}0jieCox|`|CeZd!v2T<CHUh**A)%q4QHq6HUIkEgHwA`(pA(Y$xBCR`dXsKih|EPG4*A6ZuB<?Q~shdvbF-H*6)<gI2j59e3?f2F`y~VX6nc>UcWtX6bJ0>3nMxP3@ZJP8dILr<_3TpEq5@iL~Fz0=XPZp09SEpZ5DBBfh)KH-GKU$9-TYm#<|h!`D&vN~@f{ar6R@Cmcxc@|AW4`MfIJW~KA`_4$kLtsuX5H&=UQlsUA*bsfEV#p5KO*ORZ8DtyhAUh>Te`PnbGg!7TwJtHAKryu=-_bVt{qP~872Dd*c0#-Q7?@KTF>eev6E^6MS_Dn4~GQpKz@{R71d|juBBHy#-0hQC6H*_F<{$nJ!i_d#=`!?g&81hHWBwx>2(cLa(n6lheZ^;vmy8I6<=zBd^a`SWk_7Kj0?i_B%ye~J=_P9ozzUtzwRGtY_FF1WYM}NNG^|-_Rm|veSqx6wWxSjbe^=R@ZUtH$A?hIv4l+)MRyxT^{>uRa1iTS?tuhK8$^Qf`wdN(63E_Gek1N@IUeY>48-mi^w`f8hLl#jP=iMiybh~w+$^uUv@{3YM}JcP~%vqlv8#`W=Ze=){1jd%L$B6Yv>x|V(K%m=HSzM1DP<!>Z?zQE;gP2hGWHYfE5%(`{S*N@ewe!kjs>2;@XG&T>r@|S#lbuiVV`JotnkKJyVSw7PJ$V}cpoa#+(H{Ncd`=p&-8~^VSr~kjDw~vdma#B=czP{$uQKxSnEU|_1+q3k7>w9q?nxC|*iTQH=_WetZj)`-n-)_>lkg_c#-su~0JN7y2&6obonM0Jm+vV%7^0(BuKD&Kb=JF%_T<4GMd!Ft~aOGcUI3M@2-6Nd77CDfQ`-gchU+q-rY-0Hvvo$`S*It|J%I8r2n8eb1_DtvN^#1J8E?;gZ?eeewgWIKv54l~k>v`FT9}-Kiyy(vD)%}xWo$1YpD%TQAZ~JQ2Hg3P;Xl|Dxu5WZ5-{0DC`%}619#{G8e)udN|CD{t1Khu4zj55<#C+}d#upOvy<yv;6HQ<8ijk;4qQC1r*Y2g_exQ9{kbHI8G52}WbsV?b7;o{_PqCE=iRJUfeM<7ZcecbQ=G*mVPR+bDvFqCW`40JVyI~Z0xr&aH)Gpb++%Cz!-7Xn<hp#4IYFBMvZdYaBmp^>DUG@1=yJ}1uOTOIx%f8+I8|jCyp>j+29ov`hJI2Vd<jeOR<JM{N<@=h^YwTKQ{=WMl{4egClJ84@aV_~@+?PAQXJ5X*!<X;xX6DR1ZX)#)%&|Fi=Xq}TH+;U--!OOPB46&em^(^x{!%~399@<3k@`huhPvd-{VUnG`&VY2HhN;$h3wn?H}h^+E~nH#lzqE@Xx>`O<&@e_GjKDfm-?%+Z}(Ttl>6QFiGHtHJ%-CE^^?sc0qdOQxBJ!RvQF!q`S|=xgI&JeZ#Q50uXp-(Ki}+-(&gLF1?J2km;XQW&~DKADz_WjvxA#Bo%=b(xY2hz<tshc80$uoFFywvz5MCDm;5|s`||UYaVb0b@^hKmttF?Ip6_Jee!f$mmDuUJ-tqis`||Un`ulk9e@M@v>iyKa$d{g5)w<=#m!E%aUw-~oM^)VAERX#hZTs?bx9t1Ur?18NOV9Oc@Ig*5jRUChce$L>xPhAFIp-sdGpPMvvoDQT_<U)+LhW6V$|sL|sNF}BFOQR`r6P8_t{05A*uFg8q82~P`!9{#sIPzK@0G@R)K`CTJxb$3>YNlb?kSHWscj39FONH^Crhv|jZ>*%4LKiayh}aaB+_|Z`^LNeoWQ<3o(BJm@wCu)k<R+D$K}k8{&c>|<9o7ikMEg7(z7p(6Ka83$d}taEoDAVFO5T*aU=IQ_sbr)H2coy>qi>@w0(K}(_9+A$93H8d_LXg{H1YMbIC8R^!7NdRyqki56I)X=E6+m%j3XWOm6b!abqo_IKOX}#-D9p9)H%N134dQeB0+s<J)GZ@3@@OIJsG9&R*w!+2iW6Z;!*9CpVEVkK1c6_HcS>oL_5mn0@Jef$huh3$(CH>`U({e7^La!skoxDYRC%T;;dlgP6~5bNQwBCT8w5biK*%S+oOz{9Gr!moXpp<^HAg9>>hGit~}*2id;#K1loa7Wwk~CfWDBZ(2K-`l(;M&ys!neO8sF<je2Hv?Mz@z4RVU>+=i0r<C5inF|K-eNlQ(XGRYpUw*Hrbs0v!{2ovXpGLm?-cUPzfqm&cqnR)HL9Q?Ndr9rD)GptCk7+)sOTPTx)66l0eEB`8IkFTzpUdx6wL0ZozWpB7ToXsW{N7gcOV9KF<oCQQvb%iyy|8()BR|hb?~%0+qxktpdhe{gzRBt3_tdX`J<R2Ezt=YByyNuJdvNtsX6hfv@7Zl%e$Q_E@_TmUubSMilHTvzzWjb){i{BIuQX3U&DWUok>(Ys(>2aVnm=Rv^86WNN*K?Zl;+RazC3?M_U-vIwlB}0@uipM&-lJqnm^;qN18ul`||u5+n49h*uFe}#^+1(XMFif^Jjd%G=IkDOY>)ZzBGTv_T~9AK3|$Y<MXBYGrs+m=Fj-{OPW99D~~jP#`fj;Grr>@&7bk5m*&s-(o6GaeCeh6GrsiF{2AG|=g%02W^?(ad17j_U0grXyfSrv6#LRVG<AZ>zBHfB_T~9(#)EV`-&C3}XZ!MeIW^1IoL-uDXWZ+;zBEryz1N%j{nC6t+n4A28MR09JXdL+q3z4_3~gVYXK19I%;k~hF{)`+@P0}2A#Got4{6lg#J)7I(zvyoeQ6%1G57-e(tJ+am*;b;`b#_)x#xwd6$6h^dTAc1(WfE#^1M@{S6@yq&0n>BdH$;Lc_^os=E17}9wlF%H>*bfO1?bL)`<Gc<=gi`qi9mfSDwdf%qc<s7xRJP%kzQNf2xu%&o{PxdA_kaa{%v;G;diA8}IV%dCo?TPn^FrFWQ(GaDvJw&!gU#?1VGDeZMxc29p29Jnbw^UA{f9Tg}{ye0d(Yx-*!3dEU6OV-)%Fe0AHG=d0VkJYU`R<@xIBnDLyyG*8|bwUB&yUcIqx3Fjlt!#B1Za{2bWef9PO^5uE{#*ml%z0!IC+n3i1s2e`>{z~f(jO4kgeU#TJs7dQ_dn&DWkbQf-gIc8_`SQ96HFhYE^GfS1)T;|zzP&EP_$H2hX&r~!oyUvibswtsfzwOtM2z<zIlZ*5#3=5e@eX+%igBh9`SQ9I<M}G~rFAaq%r)f8>tc*&C)k(P*T}xTzD9k@<K6N)9b;crIv(<RAKACp`=~+H$(Pp+sUg9fURr0QMh@k19BEyWnk9_KeWZ0vM&@unKcw|g>aGQxzq}qQ!v!vnw601Un2Mhtq;*(kmGtDx>$c2F-*7u9t@AQh*5md_S{LT2(2?6OX&ss8YEOPXk=C7gmQCXPrFClh(wSTyd0ku2S>%7Q4({Uy-Y;q0oadVz>`UwHJRc6TFRj;;eS5v09&?4uDXj;zeR(~g8TF3uL(;lJJ^VfU(mF)_&40XK(z-=0N}>9a*E#A%GoNwRkG(F^e3g@*i=_3HvTv`iG&|(y{(-bk(=>|mwzRI(Ec^{0KWQDPe!7M$AN#pOZ_}H7X`QL|d^o3*)}?yFCUH5X^{ux5#roFcQ#l{3lT}l^;&Gllkz8-`dS3WntmlRQ#d=;lA9+15{4dt?+P=J=H&-nC^19>S?{fV}>z8d`UcYSaOT+KUr1jCZFRzc*vX$U*c4?ip-jJUI<#pNmxXzrvw2oUFGl_lac|;q%fP8tKxF^F}Zr`Qn1zo+w<&oB*>qDRM^QW|KUDGSj{YGBrZmzAtzO*i08(5piFQj$!TAu~%OY82n&&SA@pMyM~Pm%w{y8crB(Nw?E?*M4;Q;{$KZh+P`Bm46247@E&{ujSXFh7WV`S%TczV!PB=Dg;dzw|o^=JU;*Uiw`H^H2bv-_q|e=(*DI^&tIjgQrGQYWL;ef3SV|_aDq^-N=`JM?%*J@cRSlcPI2~^VpYur$UeA`=9)~7TT&v_NCv!@U%0|Q~9Ld)3AN{_cWAeDd~Kbf3L&#<=^X2^AzLs((it#-r?*!e<!55>(@`>+6V56E1@VNQYu-L-rXEOeIiWp&(_3$`lMfl|Er%qsameW|L;$q{9~12ffav4!@-&T73C`{GC{LCI1t-HYdE+8wuRPr@UMQnE%Y&1sMvmlc!<vg-^I4jdk&7rw$SSij>fjoa}GX^ZJ{T?AFO?QWyMG6OK=i=mK6FCoXL+r%M48l&WX=*K{JDAh;z}3`OpjC(F%VS0-X=;fzJj(L%<q7>kAzOu58uacUGi_HgvFtZJ`|<JObN7`#X3vwuKIM@NjGk?dRaG*cRHs!7Z>Yw2_0WU|VQLa8K-8FtjgtjKZIVLW9B6@!33RD0nSCi-FDqPsV4npfTWX_^cmv7B~o>wSx8o2ja7a&{klvFRigZLYq2x6t;y1J9sv>g-&ts3Tz9V@8H$g7P`j4;n)_s%E4Z23!UWPA=nl=6kHYiRt?$^+(6;asza-R+u*ad(CXmc_^c1KE%<wU_8qhjxCTC}1pN+N6rUA_Rst8qXZfLp!D3&gVt<5&Id~<ug|2h(9&8KU=ivR=7JAUZk=Pcx*TKuNEmU{#WNZta;o!d57CHc21p8J9njc(K;m;~V3xQkXvlh_G;KBH8AhZRz13qgH9SClM&uT;4gX`k6I?&qS`uMCVv<_J8%LMF?&`<}@!M4z)4ql9Hp^F^60NX-mId~ejg^qXdFl-C$?%<Z#78>N>%Gef~9^4Z9)(P4a+)LrlMnXG*r{S~N(2-yrpIv~?2IsOOqZR28f>T4&gHwZ(K{J7qfzv>9g42N0Ld$^Df^%EZ4B8o52HY7u3L&^1G$*(n_*-Zu@VDS{(DdMP;9}5>;9}si&|KiM;Cj#s;CkSWR*ZvohgJZ02RBCu&I8Q_&V{-bEZVIM3b#|$!I`1S!I{A+p#k8O;G|FmoD}Q_^#}WblPG-Me5LSpQU{zBnhKm1oC2BzoCNs@E@ee&D@q^)7l(cW7FrU#!-`#2?1k<FAF$$(6+01vcU!RsdKh{Ld>DKZA@~&Z0QeO61av?61o${~FZek4D0CnADENpK$DjwH`@jdmk<eY>NbpvK;LXq-;LYGo(Cy$&;0@57;0@r7(B0sT;4O~2+XCGN7X64W3ilg?)&lnfw}N`Wt-uYTIlv9U)ewR+K=Xn#fRjVBgOh^;pjp5HU<H~@`JaD+{h|55{@@hQufZw6;{2@xZ3_Jw+!WjiS^(S$JQAvcM}lWVyMkwfFCYZZhc*Jw2Zul_f<wTApyk1Xz<r@rz<t5N(8l0ka4573I21e&Itwf`27JP*#270sAp~E6UI1SKUxS_lUjtu;9tU3rUxaP|Uj!euVmfprbOU%KxHCd<2=q8O1RMc92aW)5f?fb`0`G>#fOms8Lr;J=gBL=#fER)%TG0(U4!Q+A4m=Yf_!#sA_yp=&u;@da_2)juQt%mQEcgugDl`Fn6&w$}1&#;bgx&z(1Yh^(K6kV~_sQ3Q&qIFzp9jZ5uY<26AHln<*lERfgy5~v9blo`zy+-+Y(+_EX>c(sid#_tA-IqgMWCgi#lfY(<q(3)K#PIPfXhNlfXjl*Lra3ogDXHwgDZe5Sy2)C4YV})8*ou*VQ^7!K7`=B(1PH+;9SuB;9TIG&;sC`;M~wc;N0Lmj=IYO^?*g6a*RLsIfX6(cL$G$9srLA&w`!=&jK$(2tErv1U?Ing&N>kZ~`<6oB+NBJq^AEz5zV~z5$Mdo&v{##reAiIv;upJRdv-dKf$f91L9s4hA=cjs-UbXG92Y1f2_R1nvM`3+@2!2i*wn2ObPv4;~Ee51j|@5AFyZ1MUcJ2n_-YO%Kj)bqc?=A}>O4Ln}H!+e5zv7qz0b6~z#O+d$ib+ko3yvD=DCRzxBMPlmPww?q2L_>Kkm{tn=|Rvd<&gf0MAwf5nOrS+gM!6F2=g1!ff5Znd&0W3mrALwVW2*I78|AIvb{vP@c{LH$iuCd|~Gy?nxd>=Xmd>{N1bS(HM@Ezz7@E!0y=y>ow@Xyex;QUs(f~+VEZ3!+6E(mQ3E(rEO8-YFG9MF2;9N@2@wZUJ3zeWhIZ$)QlM`&$uM{p--J#Z&*7ic4J7jRc-Q*c*sH)u<6H*imA5IBt$fmY;(HUQ@a=R*i?Vnq*VA7}$`A8<ctAXt3I9DKjfDUR|?L3xEvca(oR_D|?M$NtVkeF%+k)K3KJPv~MteJ)0QcLp!C;xzOObTRl0_!Kk(d<uL7IuCpVybn4Zybrt=It9EJd<Z%REb3?l>Q896qdvn?-#x&ytvCoh1`P)v17C)&01vWaixmT)8^8m={SX@*e<SoZbOZP{_zrXn_zw66LhwfDAh6KE;Lp}IS;o@;pcTL(1gAj=w$GtJls6E*UH%HlTWA^ZAn;&>;Brv$-Q}Qu@c*=Ut`#q!tHCe8uc7O~ufb2Di@@Woyee7|3attb1y6uh1`n~KycOdSf-6D&!9tUPD}k#)Q-iC4t3Z>3Cqlgl!QViWgN1%lnAiF7KCFg@f>(prLMMPlnb%`KhJZI&aT6K`T@Q`}UxBUxUjbi(>fmeO9}$ALLMMVJV&4Qe5%(TTt3!VSixB)Z^cS!Q!F8d3g1@!mt;KDjAHgC7_lAmx@7@T(gP;N6LEv6cKX5N_d*~-W=Jw#)&^KTag0nzhfX7(6*^1H7?cmYiQP7>>QQ(o#UEq=65zrmr5#Zqn!P~6(3Hm#92l#jJ-_Tv)zrlY%cY^-_--m7o-v=i^H-i(v7Z8G%LC1iFjs*u;QPzrg3Tr8_2*H0rOMpcP{uNprEJE;eXi2aL!T%~8f=i>WN~8WtBfVXpB~jlck-uI4#c_O!qdfNUDuLr!0_C@lZz=3+DeU7IL|N?rSa3~f09a@`@B^#Ni><f|odmuMz6Bitz6DNz4ge>BZ$gKIZ-Re>P6Yo5Hla(wCioBNIq>gRL|gG5dKUa1{1&<r{LqT?R{R1rz!|K4u46@dgy34xVc=Te5a<$c2za>_7oq2&OTgm&`*S~j-!AlLun56{P!pWNidPnAgT4kYwRETzD-nW&p(;2ST*HbK(6mq$oEDq`p<-WE<W&bT6#FW4DR>yz-Z!C_pi9A*z_HMkVDXMWyFbqX5Lyc?La>-K@E9!S6+E@Lv8De&n}bCN{tMa+EJE-DKMuh){rUZ@&=t^T;1%H2(B|OP;BaVTa5&fttp@gjhd^_Hhk&O->wu?%S3=u>SAzFIdxH0X_d^GQ_k$y$J;0IR<<NHE<>1Ls6+9W-7n%v&7d!!)6+8hv2U-I>2fP?sAG{d609p&Y06Yzv9W3T{B=hIFA3{@sMF_r!b19YMZ-fqmrUDNGw}d7Gw*-rKiDGU;Qh%NcAk-gR1>72%9NZc_3Yr!?3OpMjSe$F(JQR8hniecVa11m#ScG5$>JJtn_$)LjScKpo{5S-sz~?Q%Lc4-ffKx+<gHwakK}Unrfzv=ofYX3eLN#zoa1!Wu;3VMx{8%f4E8|%Fhhr^{y<njyz~UXQn6FhIx(r+&EZ%90c@AL;&w~&;6C4N*LI_@N#T)2v(3#-hz>lF};K$%62*GopRl!0Vfaic$LEC^=f!9HMgV%u<Lca$u1bd-1z+Uh$Xi@MmaDQk)aDVVnXc6#G@C0a0@C5J@Xlw8ia1?YfI0}3Q+5vn9yaL(;yaF5!tqZP;V`|S`6Z#Um4Ez%O5qcWj+&WjfThYsknb2v_?%-+QFoa-DoRiR2(C%QN&B1l8=x;@Jgy4Zztb#6r_6IKl&qoOE3#|+83vO&h9%vS5U2qm~Drj|ZDsT#f;2O|@;2PjyM_KKDf?)gJEc7aL75FMR3c3g!1wIO$4?YS$V8sk8_FFL(x(7TJJPUdNd;ott3)&Yv3)~yp7~C7&!cliEpasA!z~5U@$ckoG6oGyZ{vK%ri@6`y6rLL*^eVU)xFzDM<D3&J<`JHTFIa@&%+PCK5rW0s!d&3n_<R~Tr8pjzW`)LsMF`FYy#W>>I3qL;EJCmXy#y8^_zgm^X#aws-JqAi-N2Kfap1||wa^>jwczQ{c<^-a7-%eb47exs3b-d&gI)w{;2zM+;2z-7&>z5~!84%O!85=*^fvf5j)manP5k_`1pIIRDa8NzC&n2R*MAsM{!8~XV&`9ew({~#DsJ8+shBsU_*?%I4RcEIf6D&>yHcHF'

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
