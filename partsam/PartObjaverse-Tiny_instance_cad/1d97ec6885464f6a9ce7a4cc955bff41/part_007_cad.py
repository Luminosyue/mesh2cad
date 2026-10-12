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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_007.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_007.stl', 'source_sha256': '174ed404b70a58b574286d524431357adf8055afc2bd8ce8c0dd7db93ca35362', 'input_faces': 728, 'input_vertices': 423, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3832690119743347, 0.7996311187744141, -0.5559215545654297], [1.9080816507339478, 5.173337459564209, 1.1549208164215088]]}
GEOMETRY_BASE85 = 'c$}qt2UHc;`|W7#4SU1LSP^X4uz)&tBNmKN?71jNu>&IZq1d~k*tw#{*s&%?(NQe1E4J9LnpmR5LSpRx@A>xTz5nm6_ttvrJ+sa_`|kbS?|gIinKR|G;_vrWu96!5Rnh|O&yLrqp=qiW(n@O4!4XkmgM%aMj2Ja8hgMX0^)I_$+_h&H|2{diXl;UfP;lhn2=`{XyYG-D?zMFHAtNKAA_7NzKQbaHSn=%xheZZE`N+_~QNhm7H5%4$P)l#%QA?ks|3CgK;4Hx!KmE6ss+RAU{iS;A)^E~lMKXjpqN`*|pSbP0>diH`g|}9Y{V06z<eRFu*K@xi-*Zp<AfHclye4|yyTaSs=X@!8^BCzJo(<%C=C0bGB;S(rcja^BKJYzGKNJ4*`ae}~ODcFvzQ44n<TqD0&X9iGYvIi$y`@fb^9!j{ues;8e6LQ5jAv@LSJHRQe@FNg=VV;%lJ|Y7uT^dt-?FyLc$UlSClVLj7j>PDdoS_kx^vQRS$I$4+?L9?T2o*2VSx^bZ&5+Uv*j!NT0ZZL7T)@M=fBd&^u+PKpDny?bBE6|U-uV05dKu7`xx)}Q~7@1!;j_j=2pU+t$WD)TU%?$d>Lzd2ye}KEAwNWE)Jji*@Sm&sU-CqTYmdh@&qO#Pls)i$Gqw;^JP{|MV|P7P-o4#Qm4`P7~;<jl{&5Fucc0H>aVCX?++Mvbb0Yz(~3QS9}nTnj#ZeS?QL*;XFg$EpS$9R@i0+%$MM1N_sgg&^7-4Ri0@YKt$g3(0_JW1N8#-+=Sw~2iXIPT9z$A4Z~Wzpb(N)yPmTlYp|@*-^;yoiET0q8gx3<6$~<d-c*;E6?qnd37MLZUm!FmSF{(ci-oE$EJNbNl+6fsycjMnBu3sgo)7tr7>a_Xzf!~mXc}xFZzHj9m_B;Fyk~)pBi>Pz-9pUwp?oy|=VnYV_%74hX`V6T@U%pW4acuM!-VFbYdM5lN^=LIm3h&5_lyzv#8!zink4g|;Tc02EIn_(f7cFhM@Os~5)cJfUj{p63<X<}q=gY`j_fW6?NaCM1fM07;rB3VUXz-IaN}cxFL$R(rrV4Mm<-vL6_C)H`Qy&X&Rk2|n{xT%Lp0m98V6;faew1ex_NQE3h1bXT!?>kv@Uh1x#J}B*`PncG>uP2i;#+&lxaQ*Fvi_}q-r#(C+fnAn-os1g$3Ej<;mwqWQjeLxD9-=sm9QTSj>3A2xi0I^cBrH9)~Xe#=Uj@cTjO!M@J8TkS?7+VAu<nIz!}89ZYTSU_A0l0*6a@C-|@55ukDJHaUD<o5#ABhRqA)-%{nD{3%(WJ)SqEJH|m4)?o1P`<J-v?x5WtAA8bcEfv?^UeE;6EKiC|DgttEYiFrQt81r1w6ZKtxEc>VNZYlQ9)bE7X+mygMIl3PE!sZO&%@WOI-D^2)lGpJ41b)n~@V$M%3-Z0Z4Y042c7GwC>(!UuoO(%kN8!FQt`(bxzRX9&kDrQlxbdN^6Z2qmtltOY(9fugxUQkkah##pmr^^+Ix&Av$93#oUyM6E0^{a<D!f(n5w3UDJ4kPJ`U`oV{wDKgn~;I)O=1b?Q57+t&n8@#@70Kre2z^+iyBJL9qTx(_*yGopngB$?Zpm(U!DxU^&H`~RWt7?-pW`jysdy)Qu3VXDDmc3M}^moe&C1Al6c37(>R{PONH0(<h?Ka-=$^#^qBe>x5!+{WAm?o>u~gX;T`cgC6DcnC$7`69VCzAVa#2rr)^!t|29c@<J;d*&&_(^53d$pt8iMzwFh+vKfx3ESAD^_mwE|rE3{R3)2qDXw?zbD+)QuDW7|AMcw<`_;$L#yCzj;VyoU>Kf4&WMRy;1_8pd_3SJxVtPp|UA>pO3w9&;P&*?s4Z)L-^b<QY*P`HN4MarGH5P|tLZTl;{FYx!lNo+&$Vyv9-F*9XY?p)c@|{Kl&fsB`Wh?7#XJ)N{SK<k#wqLVOM!uhxU}96AQ)SuTug`KDo>U&RP-X*gaZ@`#M9txdvxMzwkv_t)vD^W!Syuewfn+rR%}K4)$LU#C6hIba0pd9_1$ZQ4ZP?S(F*{^`50KMq@kdafSBxbuDopYjdnbN@bx*V{e@A3jTXJ#)OQD}CHs%tL4&_;qN4@b+!st({@0zt%X^fAb^apCqE5X&UA^9`{p@Vv{j%uMMoLp-p7pG~>OCNS&zxk@EeYTMF+;xKvp3{OY|#@}z%<>%{IA60cQ1wnmPBVz}^DgAs_oKX9YeQ))c+<$+g(cQnoWi^P42#r;9cWXWU8UG68Tr(s+c_7Uc3eR;RUH=cz&^L-><x1Od+{!fche?4E}jjBn9WgZJ9qRv$xgg2YL-6DBbt;F?p&KK~#hwqSeQhh7(7b%1~m$uz3d5i8roiDC|fA{%_jQitHn4cUj!s~NR?vy;=T)?=+*I_>Yse4q8XZSVLS*EXxj9dPAvc&KI8};1kCA^XU1&;UO8^oKbg=E}z<Ch5^_nGmLn4jdNV=`~OtNktGcHAfN#=Ma-pH`fw@V2peB)`6=(lPn`*$e!Jt-{;PgJtFOLPK~fJWlc(?qlV;Z+Q3#Z`5|hJnW7=F5@M46W;8eOY+zkwmKo}{OcZw@0f}C3CuVx^Bd9^<33!A`LA&Hl$>8nY{F}Y2B7{L2S-W$D+9sbvq^sIpyyG^zdr<d(o0Hy+xYD=uAUMhyrcXtl1EF;CG+nHi9&q+&63CA7qnlFb4RT3_8eG0j(mI0N}hl?#8>Tubu}~Lti(T?kNj=-BG2*G2c*vMb(pum27{lSDDz{K+62D#Kk)tiKgsg>S}KmK(Gb-6Tl_)ElXD;DEh$iVvu>?}QeW&b#Mils<IVH<yv#$HbKnEgaUMO7ljkgR=nWj#h%Yj()*?aHr(u7DdM=j2xUUD=Wn9-x9M|Uq!s~s!f0g(wmw%+5#aURNaZL|NTuKSyZ5K;OyftLCtXo^-O2Ru{jzpcSYF?B&6Y2@CwedhbolZ)fM&8DV_uP+l*mnx<!_$0(x3bFO`g<#3hwy&B;Ez?rb)oWr)l%o)Uf_@DsHa|pCH$xujJu;F>Z$kaqI@1Y1@WnSg*W}5U&6jO74=NISy1vfY`I;|(`VB#5BnYP<@)FIvi=*+6yBbiA@Po^Y8xc)pxGEVZ7AZGSCe&auQ3<-uk^!ut{fvi+6OKc-mHRkW&gIsY4K&o63p|jMQ}czoFwyU>{tojr5e`fn2C7a`2)N@`91cZQAIAv{KsxaJ>Q$C=h@&h5?^f_>JOfQabI?WFShOAU320(Ri(gj*=Jn$fzQ(z*T<=DGbFz0VH{V&Vw^{v$7HB@$Fy|Ja}s>Cm923^>X>~N^%PD-{l%BzIVk=P;^$Stb#3$8Loz>m@8fv$vz|V;Wt}+uAAtYjfqkP_g_FYf{sZ-F^1?dFU-c)cv+W!B7~z5WIUjOa=JRyXHxi%8>%zDeQjdPOxbXV=$ME-bGueO4OC^N2Wh4u4>pU<@{99HLdCKm=`Sm$O{IZhWgg45z!2Rvza=T@I-q%9@1NS74QKAj57q6QNZ}-`T{DV{XN}aEKktgIX*3Tt3*_X5*TY!IC4d-vqXjyO8mX^Y64-a9Tf4V2fYrowF@xOP#`Q^V%u6NquA*iRo5bR@)(Q;ncOGM(higw5RcPX$^*29l8gg1w*lREX#OxaiUwaYQ?*j_TO_28zAYZXn!aYav*cq_D`>_0}H{ivtnAgs?tS1-su>~|LR+)c;+(7myozs9Ajh|kd<>&oNPQu(~Yf&6U_N`7<Vf^?~~*aO68`6GUzA?v{^lLdZKG|u-CgSLsUaUXEJw^rafTl%v+pK5nM<G9@CBR=|P?EfdeU_Cr9i2I^7{jW;hnK|TrkmK-c>`V6ESZ}d8h1Wu#!`}tfu|L%ON_hLFTG+3ATxDF_T^Hf?W|JhpeNscoZ@nolyixvdtcR!PWj}EoE`|6NZt%C+I9z8JmBzU7$57AO{aEMIU4=KBtj2vp{hhLJSeL4R?}c@1e;X(BsSmD+{2!j-y0dGV)M@(E72dYX7xjeA#_{?#!h5mUAdLIvK773Fi+Hmq&ePFVev$JlydCOXKM><St*}exF{umY=gAeEzr+8$BFDS2JL1Rm#C0k@0MD)E`eObkgkgQg*28r$bRg>Sbdh@O4_nH<XH~Z$ergcb$$%!CB!8|z@VCojpP5`7*Wb-y7}vEgeC(et`=NPz415U-g<s2$Ulo5pgSYB0#eH3Pf7vH(2VyawE<d6E(Cu>GnVEBtCm)`Rjgp(>{@g6S5d5+e*f)lJCHHCef*Zj*-r>G$Mwx4pzwlAa+ucy?Kh;WXmpmWNz~9AlQ2#94uj()E!IwO9u>Kp~mHN%dr>OIFSDatx+}Fx+y?c#3rQ6{Ajd?Eno-MVoyf3rO8ie>V8FJp4x|{I&f=bvQ^0`WWZHk}p4j<eP*kk<hzWOA1ZQTg0la?E|%JD4v4)IgJLH&OY!1ecjFT77|*Bk4(mxruRt8IYrMr<Vfwc9&L{$hg>Um*?a^HPSaTig0z#1DLd^SWZZoOh<%5Y#hyB=?i&Tjab5AB*_%u{bX}^~C%9_u%cj2EoVE>9TKV>9bM4S5aIyx37?RGiZ+R=EyF19;`lE?(-cF*I+)Yw8rtaJvdc-sgr_n!;>+eN!=xn{SJ7m8LorIoGEf&p_kr_`m5nSQ~#l`tV7f77t}MS9`>J$6R^)*2XCD%h&)doVSoOTfjYaKl03Fm74iQ0z-8nqbre1>X^nOM^;N{%FmLv|g;Hf5cs)n`&BJhhIpgJXCU`UVAY6}}`6W-u-16R5+t2&Y-yh-q*je!UiFY{fob^kc*GdWRsC^pe*M`E9-(KWv<hgSi`}xc%@|<E%18+W=jr)P+-Ekh}t0cUY6b0Ws4^EZ%=?%a~F2Fuhb+kNZ86FKWZY5W&htw64$9mNP`7?tNe<J;W)E(DRczcu0n18>X60fiJ2cL`kK;;5^aJ+qxr&njJ2lKf+=h{2;1^>4X_5rtenFrg={+J){5!jzEW?-M(7>f7c{%w&*Pw61%b%8L{U+6N{NpBCCe|w*y$p2^*?gw5C*dTQdkHUPGiNJao=Z|%D#*X<pnjb#qb(M8xc<n--kAcWD>@l9pe83w)*oPgi8F)YN`Yd?gC#ZkybGeR~G1tI*VSlhrxUZGt{B#d|XS`?78{Cy~?ccn_e0t)#<M@4sCF8!#LOtJi!}^?CSMK-hj<WI|)*ew0d8U_<^UJzX2fq&uz<WYR$XD{*WPYxX_qMHjVt<a>6e+%YwZQxIHc?o&VcX?8YtQ@!dGsYXF6VVY;#@jm+^0ve9+n-)ytVFy{Hw5^+k(<($oxMZi1*#i@?jn(7MJG~^Z56O?|^;S7SLpqd`<`iU$O{}_m7t6r2dRx)cMSY{dRJ_oic9Q5y*e%D$dh{09@a{ix6H9$Nio@>`&~sW#bXw-NZT{UIp)ecFe-KmrmfmF2@78UYMy1Fs}VC%uncSS)cmMMB%M~mbj1IJx$i3QGONjZ`h9e^EYwn@;PWd=Ck}ftlN4!<$7xM*@XBDyuVG^FY8mQwOM#uMcj`$yvND!1@?cof^X6oc^;jY`P7P}qMowbQP1RtxIS73F>dT<obSG_Ql}N3hCE|%Kc>yEF8Q@D;H^bXurDR|#`##yLi`Xn>|@FOCBISR2<k7@6~0IQEc=Ed>=^jy1$dq+`x*P>m9tns;e9dgghAUB@9@2cd7h5vILEjJGH+J-KQXR<B<7*fr==2a&qAG1A@Kd%#^RUbk39JOrr{~9+xb^zA2x2e;CHwY0obnwRJ6-yzv{v}ZsGpTasQ?quhzD)@cNrJsB>86emO6G>x|zayk?@F#syYN{@Q&oZpY);XC91}^T>3Wh&;1aVx9L}wpr%EF!6iO$YHo|{BZ9w)^n`z#x^`xT0Nr07svZJ@XtEq{_u*Myccr3n~HG@w#4~jOWiB;^=c97JW~yP={B-&*gD%$PvsqW-Z@te@ArDFMSRn-xITUi!FvhUt%$eU!QUSTM#;E^w+U~%UJ3b6HIw@^tI`h4XHZR?cN1FRxqIU&#5;0eJ)8@{d9?T@@_#vn^U?WSEOoBDgZbH{A%C9=CuKgp?;_rC$Nj4Fxm(s@=mX?$^gHhBet0YIg^a)~)YC2r?<-0ylX{HckH}NyJ+8B^HSivFmxkZt&oSO_4Bi7=%#YuV+NHtAR5#h*v^mAVyP_UbFCg#PY$u8fuV<!UJ!Ey0easkIN_cw~-ur1U2A`3AGEY_f{&d9)=kKT@vOj3e!5eMzV0}hU#C^+PPyFsas{-ERotPwk+2__meBEd~?{_aD_YY=zec`pq7qE}%G1!M^HpKBRIgI<#Wz}T8=|6j;{_eFf|L?2G_0-gwqW<NbFz$`dc<yM}4D%3<-)oFIE#-dR7HgoMlrgw(>Hb{K3w>e-9PhdZ;OjrbdkOC_99PHOSZ`htave0*#-pB7neeOdfYmt81dKcMo$z)?g1kT1{+NN|t%2*lz26jBC$`XeI9`{WGS6C<lj4hg&l<!JI)MFcWlfn+{hO_*{|N3gZQ-l&p5*NgjC&aSura-<yce=v%s`&+M&djQ@RsKwhu;nGM+#tmo)47$$1)#b9v;?&FHI8Ux@KO*@6FbS5Uj%&akvhKe*j;#7xs-@kHtshX@2=V)qVi`o~=PGd4Fq^asmJKarkvL9`A3jl@{Jn)f?+J&l|k|kF6lQ9&{4xc5b4)XVWz={9aoG>&kJoHTL<$=J<WRP6p<4c7p6nHs2P=)BOebJbUn7D8UbZAE3wL`qe#1_Eo)87u3^uG_E_lbK$*ugWiarUmEi{cDuZ1GyDhQxFSzuo&VyA=fr^T!6%+Wo{I-Y$+%O4k!R#gJU^B@i*<fs80s(30@uf&40#@LbjIIFm^s`r{|j5;J#cyy_-aLQz1|lq^P}~fg5!PiBc97V#>#z{l{pXNZkvqxG&9P|Jclg-f2%5fzt~qvo~NwEEAaO&1;*fbXOF~t!muOAKlUfS&q<Q|c{ATB<jEM%_fg}QN&fn0z>mFxbye_%tXpgHQ{?fv1mANV$NT@3mpCqC2Il82?lbi^`SAAv{@7<6(@tW2-YST{a~k{|?mz$iEbmdR<M?|5ds{c`Cn;^^dS`U2D!g_A*9D`?aCv`j+^dQF`|9F)VZ4>+R^u=5dL^tMhey(3Syy`+@$YZI8);9|WZnGK9OKqX!};6pvK+7R9K2Zq?+t7@%i($dT07w#f8#uI_~w=OJl4pb7}pJX^xFeBO5Gm(d#U6Fn4h}G*2p|JFmYVx@w<$b=DkGfFsBP|yYM%je{Tdt9`^r_zcO6!xp|hovNP1#@@plvA%XwxPYe~Q{$=<7`#&)ZYxsZlCx(sdH~Ihl6T|k-8ag>!XJ>2Az5_WwXX`@Tg<5Cgmc*)WLGBx8Yfjvpn&R3zTNC0Y)D-9IZ1sujQ&ZETrqYdA_0`E0ayD0DS89sO>uhC-%TiO^SI$;~xCAxD<#e{<#Koy8F1NFlA}&Quaq90d%M+KUrnsWcR*|?OwVKY>*x9^@RbPu-YiIK&_NLaF^WBuVDYXuq-xkCzs1<g$a?VzSSoQhoQ9EbrNZgVB)p524&Q^t3^%XR=Of}8j*-8_u-i0xWuR*N(y42mtm1eK<l;P)WtopB=&4=SQByLE*tC060R=uaQRpsYw?8*7d$K%XTtomHemV=+OvFg>oHqK@^TRmdcH{;wG<l3=UbJU8TI}xkCJ#iy`rxp8l%x6%m$KJ!)3bLLY#H!EZY{giAKH_}Tb^2JCxG;4e*4B)@59h57dv&gq<adg(SDz~rt6ur3)<pr%R{?%@Ay$1+*6zvrJ^8sNo5E_H)~0uL+1F+rzQpRhRp)07j$MPF>#|j6oEop1hV!HvKbIj^{nu=@$kpQK?0OWg$~pJp{P^&*2XXdsRN~xb&vEvA6d_i}-^ba$bGF{Zsvp2!@!g13-^1AkGHw8|>IYF%F<psO-<`d`vwchaE%^{<8_XOb>{Xs&&K62-82b=@Pvz-JtomNgHk|Rph*dwDdS7SjN8FF`qZl`uSoIN%{odJZ#5R6sq_d4+>`3+z)Kz>CvFd}_6b>U+eK`9O%n`;uoX4W-3Lp;P{Pg1Z{fYZi>p?vm2hgA1#Qll;)0=**FOWEpS|IsgV$~1fce3>X><3W`X3ay`52ZeY9tE-=L@k`hIh1__V~5hGA?!ow!!T;2*{k^Pog2t^&Nd_mu<E19b#gX;Vt;CitL<!!h#OH;TqS37BX*;vxO~p`Sp!zR8@V@5oT&k;UTKQ^)7j1wpJ$BXesi`H#3!gJ?vk?|CO%9}aaWz~81XS`ihJyA=ZMcyQ`|q!_Kf%$HO1w2*7t$<12x4}bT-!<z^;r@TrFp-PrW`h#eL&!-H5wUQ(Sjv3nC7prnmvlHimc%HN_2bw(-Q{sSTok(ZtczqUqaMV%5i!Q@-^h?nlj^zBMCmMy(M&tw3CXnj1ZROJ7xAft>Q~I(@y)m`wV1g!l-x^Ym>i@m6Xl=-Us(KTtbN-!>6%qIQhFS;Q8#bM);p@nvey=;^=2|58(&@~td=RsFx@ly8mcYh%XLr*8qo0o1zDw<zK$YC-fZjyR6m82UDycsjLgFXM^hsm0T`$;7H(L{9k@NE}G5AAK{34QkEkX*uF@)GE-^zv-*$%aK#Qou#j58FQV!?I7Mk?FfBaL%fFCR{FM#cp0@H=-X=I)zmi8w=Kk5s9E&w4DlIim+5I1aTc|I>1k>Ds`@N)$~PbS>cg1E^vy<WqZUBlCJ|4f7De9{5-+3{N8gqbFQu04<s#xm)E3dVsl=*ZMo#$_MjS>hkiNAgZcELer)7xCP%B4IU(r|9mm#NoJ4s(pGUhCOTT8r_+79}*fOrA5HS}#7@ic17=-WKvdDK?ZH#@PN+7|kjPMl8d3_X2G{E}K0JuN|BRsWKl@~s7ZZNV5H`W8$aOwC5$5{MJ1O`>l}#7Wc^(zn&btEpvsxr}%jwPo~eF0ty@kW;>mCLT>KjJ~xeZcnW(JuOLGl3E#h`kcP1z9c#2TN-^$W6VkVwt{#CwYBtZD)Cfm3+S6kY*L#>-x7!usLi8q%ZZm$v(vW&#0RLQ)6*x!PpG}5r$y<j>YtEPzO|&UEg92-z6~WFN-dba%_5#fErGtRB3?x;iN38TUQaFC%QeJnsI8%I3y4*pLQeS>K^#GCG<|DD+=^OzdRmOQ7`2l0^bh)~`eNjiZ~N%$KE|Zcx5dPZsjZ-IQ;4Tfn@ZoJiKD5R^ldWnWNHcYZ6WbOYRl={F5+F(4$#vF#1E)Fp{GUYtLh(+Q@;7qS6{}oq;JEBhfy0!-{uj|qc)4attDPdZ54g{f%pe%*<Pj)r%+3wZ}W*&ZzrdG8%aEpS_FM-PTZVYD|+fe>_V*=J-ts~RqsMh`L>h3?qtk9`Zkw%F15w<Z9MUKYE$T26mb-_X!<secpSCK^lcXLENTns+h*d;)OOL+JH&UWJ)oxr>8tARkW;=jrLRpH<4fN{i9@Lkqi=JF=TMtR-;#-wsja1N8;Cbh%l6VvY^P?YZ!?HhzmlBtErd9P+DQ7=gt!T{=Jd1>aUp6h^z<%$Red3H%C~LwbsJ-L(zn^fv#HIcZ!yF%)W*}dNa9FpQS@yr@mOl(=-W)<nbc;{w~fRbscojGH;8XgyF*X&(^u8sAg6rurmx<NX-eM)6Az{qO5dgtPop-6zO5i$K`oiSts`DXE!)eL#4D+-q;Dp%>X(pHz6~TENG*iEH6U(4tqDCXKwN-YA$od?zN)?eIpy1S`nsJl+vwYT;`!8O)3-^)lc>eew=u+Hs72DZ3B(hqjiqmMi04q7N#A}X{*l^7dU}QU3bh;bG!K1M{S|V`x4QJTE@QmuTYuvI)CSYHDa2E#O`~s##EH~a(6{Bp%c*61xrBHLwI%dz9I@(WlT*I+BJM?PAbqPzT$5S@dYYFwFSP>n^frA}eO_|Pw>|WA4`a5|w<W|&sLiKual~=dCegQv#1pBFp>MIovD7Bew?yJZYIEpYDsd{cAL;2e;%n5d(9^HztLm?jQ@(l9S5L;&rElL7e@m@DeTyNEp*DrS%_N>lEs?%0CSFV}+soO+v#HIdZzG6RKargBtt)X?YQ5;22eAjWn)EamaV~0m=))@dr275jln*nAXHbiy5AnqD)F#r0>BQ5i#nOkB#4D*K(ubdkf2Nj7k8Tp*q;`!S<)BZhze!H{;7*_18RJPGx)67v_APw~Cl03;Lmws(PoOrFKEx8oQp@&cBJo6O6X`=AV%3i#r+nx@+<{tG`cRd)Dm4#!l#@6oHO1X?9`{2HSoJx{Dc_E2z(*OgpT2D%-au^?eM=%vqBeuREh1h-EuOwDC0<HxI(<taPNBAvz8xYyMD1sK>L7MdyGc*K5PzYTgT7U!uaz0&PT$&4Z$mAd{tPEpeQ$EgpGe|JYT2HRA|6F;6#eN;tookhls{g?Uer3!ADvjIR+Zjq#2U4n^zJGBQ@ut``E#27oo38Y`m>jKFSQNyXFc(HYDx4bnK+r+BKotAcpbH+^k+BmZfYs?=M?cNYKQ30BjQKY9Q5uZ@keTkQ~rES|5X2xobs*?{j0;6-t?yjvFiQEDS!GB_obHYSx@4g)OymNhQz9GM^5=uowzzRFZxr8xD+*=-hI-5RbPsn^5+HpQ~f7;ru?}`e33Dy>Cdmkzf#*ve-08Kq_&>^{6zc{wPgD93-K@1*3qBi#K)=arau>mFHk#0fBqu=i`pZ4_m21-wU6|!IQ>)oJ95gqYV@xfW9rbidc^gp`O&x5#I33Ipl=<CJ5tN`vK?_dYVGJ-6=K!bAg6pQPh6f_b$VKuxG=R+^z=P_RefP{%D30_^)+K&(6`@-f2VelzGV<+Q1kc8k+bAi|EK?j*8lvc?$xya_#bNhuiyO7Ka2VA-yGu1^*{bd#@{cu`rTa1>HJUqAl6F#6@&I)FVOmN'

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
