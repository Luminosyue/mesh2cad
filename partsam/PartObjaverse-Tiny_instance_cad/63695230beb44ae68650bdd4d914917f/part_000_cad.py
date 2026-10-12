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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_000.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_000.stl', 'source_sha256': '433aa3c96c84411e65a0a8d1da4a6e17e86d95975d8c6b41ba191d6d5e69c3cf', 'input_faces': 760, 'input_vertices': 563, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2173590362071991, -0.24220705032348633, -0.12246628105640411], [0.31441980600357056, 0.11407774686813354, 0.19324110448360443]]}
GEOMETRY_BASE85 = 'c$}qt2UHbF6lH%fV?f26z7ZS|F(Ib0jblzI3Z`!yOoJJ-Z5A_T#qiCjsF-z7X~mqztm8Q29}J^n&W?_5*SnWR_w1gtXV*FJ-1~1=RaaNNs(Mx3Ov@(jX}mQ2E2>RMb{pTYvZg7^ta)j}dJY=WyL->Ue!mPDVbeTCSN~FQe)G1?T87xPVcIC~9z6$lALL!l?p>o-ptrBxyI1(2A%nX9(j|OQkDf|z(6!&-o|Zm1tm}ZD)^DH60Tq4i6-)ct$JqZL|7EhOVD`OyHbK>;%-($p?cRBh)KXaf0`!nV`xTm{-9&e8@eth@p~uPfA&>Se-RSq_jQlR#eV1HcR`aN&KmNPu#ve(NUJraB>76HzB7NDPrF`w&*~3bArQ3+~k8<vi`+D#EwU(4S1N!lKqHFU8i|(56`)T?8#my<#k6w*ay1w})^jLkRLT8;4JLI{poP+*w&KgPo#bc+G|Jj7z<kDJ&u2GjIy<=4r^akrt|BNM%OZf%5L!aJ3bl0tpqT2)7Kp$LcliYXQl!H?Kgz};rABQ7-WZivAH{Fv@N&1ZIwo3Vv+Z~hiLDxh#p5#XRq(7D@<%h0;UaHU`X`c&Mr9B-tqfw4q^g+2^JOceVX)g3~;qqMC$hW5Smv>ju&E|DYsZY?BLsHK1PDtN)KH4X1Eh)!r)tKd66kR*M3;yuBB=nOZNZ;wU=tiTbCq;MF4HmzOw{4L6OuI<^S#L?-u-<yq=P320{?e~`%1e6Z^Nr9QqkBpH&W=I)pO=YlgmgF{?e^&7F1a4R6zS&#OMP5tza~g~4)ulZduxI`chrt}>BpV<p`Y3{Nz#}28G6e+D1UmBU#0x(m-a|IobW>WN%;*ar`lUdZ;aHS-wT{5dcjSiJI=p8A?0K~DC0tZoG5-`%s(W$K0Zv^-(EMn_`mtkc>?2ZllY1A$<TG8pI!>R*TrR0Pw(>EMW40^y8p<zQr?+P(hl|xcHB4KNA7Dne~poL*fjmPq>n$mTFS}XN7~u&YXyDJkPQkQb|>oDtR?gw?^a2_R2;EL?i*1Ry3s&%{eA6)a^Lv!&;ySc@b_Q#O1^oYkBMF*cE03qy+qnmFY*X_no<kocd{wE>(f7?8+~HqrG0kyl5yecbPnl5-^;i*+MJmr^;~uk`pBfi@?3`#Wd5<=*aiJfCY0aaL+WFE*$Le%R>p<-&z|YhJ|pHp_fI3~?K@i{edS5er`4D$e(66+`o(d2Ec5|sqNP4>@{9j#ZynGVe%J#48gxqTzpp0ri^rsV$I|ng<+<u!N|gNjeK4<<%WzWKY0^~DwJ+^t9&nz2i}}ZMGV~Uwq#vDKm&p9!`nezUyDsr7GhH^RkE3`;=&msn<axReTq>BiGW3?cqorKCL*`Gj?O#VlU;aeKn|=74m6E>3Md+?-;ZnZGSebv!6(^ya*O$t3g#9S>GzaVzU4KzU>Z9-Id_v0EyyPgx*U%&A&o9!yX3R8{vu&aHt9@IZ^=QwD&^@pBm3*0Q%s~4_pqxSl62wn3jECQj3x<C8D8|=2A1U8a%^&4#@WptDJdWpG;RQX6<6%y2=^w+H1A5Z=C~4>8=`o+2$__oa9_m>zzpNM9_>Xv=(NAQaG3MNp_SR>=6J4L%8~t)(9NHn~8PbOpm3r7~7Loh9?%#u6qAvWS`gTDx_igA42B19OI%wzkYtT<s!F_`RFwYmc0Ns5e*2U?|R|uvvp<jF;<Ha1AN6K-&Pk`<RUHbvLK4ul}7d}MlZ+Jfuf76pzif)t`isw3#41Iny(vO-V?c};2`<-qWJ7xXS#%>co*V}f-eHRau^-GUEAnoIL)DF7;KAC5<fZQ^_8E0A_!MHsw=s0;t#=BXnInq~+mFG3$E=-nu*_+|My`uLBmiff;Ga>!mX0l#5>`&!+9Uf_s{^TNQ2jhCI)Kkl);ko{31OF<ROZ>_nauMy)F&69Z;PO(wUJ$xgVk`9Y6+}0WoPz%4(<1TDP7bWseUCv8Ya!!P`+TySJm-~z7(c;y4p;11#8-8w-+*pDh3@#Y1LcIoi(i_5cHAW8UEB^mL$)oV@5&Mfy&Lq+2a#?-{>oBLj2(LYe6dn~TnA|fqpBzRdufo&A9{v)a$jRcTBLs*h53DF7xY_Y8}te%q(1t&<gJ1Sp2)b>9L_0{F7TDCpN`EpL^p<xh{yPjlKIozydUX3uI!ffs=h_$Vf)4{&`;LId|hnrJgI*JCv>N$%-i}8oexO6tz8K{Z^t2mjXH>K)}1E0o^O`)uNim>{c^59>XWCD!~<HFdGLpaT~W?cH^h+*=QmTooo#|dH*0*AavW_6!2ff#K>D}^qvd{|7Rr4ct$k4bvXkN`+J<5By!ON+7>7+UPZ&e4A@0g{2>PuXQXgaNEBIT<c<7<f9gkm%ZXX^7J^cb{AG1k8r(o|&&@1{&JZf}uV14$vhw(Z7f%Kz2e;=8LoxPVqe|A~Q(bk;rA=h&*f^I9fTd-$&X&>jT3D8IXv>D?uOxnrm8Ug*ydYO;RFb)2)Cjz?WDSqPYI}rY|HURqIvC{9(TgkD4uk6q_M68kW+f|kI$GPJo+A-joq}OVd5Px(2y$bqC6YE~V8`7Sxh-J{9)Y&HG1o|vY_*Nf$5A)84%joBJbD-CmA?@rca!~rqSP%xi<RWQL?chj>XSICopy#(?9*AEo>9tWUG2h+kfN>N!0^{1FA<}m~hjOMah!VYXE$C^AitY;QAnUSu(g)>U>>=^6tIvMSt6scc%xlb7O|u}LPkw}P^}DCk-~5_G(z~J`imr{wf#-Ue9pgRsHRxf7q#bnkc`|P}KktUVsSeip_7xFtw3`9_b3gGD`@>y`V=qNO|A;u%m~d#0<a1?*?tKmM-wrbd*I#42MeUVwqTjhH&#R4l0R6`h*$0}-GK$|CXA+@b4wSe=3-K5z_g}IRy4FC-chvb$=0AOw0X?85+Bt8`bou>zC+OX>V7@5PN$T&aiT!}KbLDEeU%n>ruO(TaPuPjyHyTKM?#%J8^oLe+2KH(BFK?9l?tch9u#&{{`qN#qUhA1oL4V`*-8|sjdIWmrCnz^=xwN15-xlbD^Go@9rG+xioNJar_qc{}J!AM(`Q2v`^l}SP-(hnQm-<DDZaxf#AC3wZKh(~^pNtB7L^t!rO8@HrbV51)3D}?CX+KK(VQvWYf~6-*`iP6D*X(xCPvpnE)HE6MRkgOzwQW*QeakQzr&d4=J?I+7+uccmMyNmZKPt+4tp}Gw{Bx@u>RBWV&oOEu=I6Ml*gqc(M7*}%1OET{xadZ|2Z&FC{zSag^AOU1X(Ih(j?5zcX>Ky04;U};y#00}>K`;3diPDT&v%WjwpP;DYY4sDVEAG8``8cVYXJS@d-%T|j`?jt1?V|T;=JI`Hxh?Ba`-|IEiL<VBU471FJ1B8(5LyxeoTLsQ~cUUpB8%21lfN&XAQ!7e(m8tw5JFBp?H79gF#8qr}x3Ww|~zq@atIUCv#$dn|Y1&i<z~Y=tl0Gm_M(NL);brdN1x9iE$J@bt(L9qv+<8PT$S9j=A$iH|o4bJeAQO{jzcf%4s$W<N8qm;`0X`pf7lf`UlQkEd91TgXntLT<J$=7kBt)zyXQ#w5G>o9J#hG#C&*gF!UkVmpEb)>E|KPt6@K*JvcQ_$}Lz2df_veCmUx&+<x@|*11<ch-1!_+4G$qyA$V4JwwEQTt6g1ABK3w)nvKU$Nu9@=*~rm-)i>9{!w#^Ze)5Y^|b#{0`2_Y5a_4sV}AY+g?Q4hGs@}8{cY7qjF+oTp>KVFaimQZzjOYQ75Yz&FmE$HF~_HYUcETl$EPXk^H_skBa8H_o?K1tqo3O$=L_1V(^!Yo-^IA_-VA-#Cd}Kp(({~cBlHQSF;0RLq<!>S!*EV<#25bXIsxZM`x+yCSh;ob+|GqKr|Mn>=Zv$COM5zNcb9p<)jTcIb3QRYG?M+XKEw^@FCF_Jt~(luc=hzlofy|?WS^#GYm53UNfcc#egpmTE<)PJ`1hdb#v6Bu*Ic8EqW$N@qnzBIF^>g#%Xy^3V;XeE|E{YSCB3U&ACy0FJ)U>aX83KvAkodtr6pc=d=ACFtWGW5xB5q{=jqntJS1HOl=Jiu&hg&oLj13L;l7dK(mrO9^Vk<x_Jn?S1pIvPsb%P=CpcF<hW(bY?X5ho_TwYbjS45Q&p5JN?rY?_jPyflO8n?3>q2_RIMH>_zfsQO4^kif+Aq+rG{8Q|Z|rxv)})k_;~e=8`^_q0xNp&ch@+Pl$N5HGPo(#JwN1)f6N2>f|HZk<y+Ru${oxQv@96gidh}i?$2lR_@$dAZf1o|R-r;;;++)#=vPH4aipha`zL<#f-)W7pUz{-!{?K|1()&lFeIkBD`}7=)@*_JVzRsCnbbVS?=mY*1zjQ?JmT}?u_;NeaUBW(KeIu0LAsPDeIViu~LilZ-5a_XEvCj<-LEL1vf&MBx<|F%OoQw8p2|b{ttOrI-p1*n4f<E#B{9$oz#CMfuN&9NM&*5BS|6|16&34N<wYI=l&WoJxeu#Hgtb{&l8Rq}X!7^T5$<v_cc#d%qkzLN)^r6|HyIiuK>b947kC5|T?05dzG>eQQ=kSL(M>84>mj2Z<Vm|S$F8!@#@W8onVyL8ZT`CRz`2qNQnJ(CW?bt2nn_5&w^e5vk`{rfP8Q&UFHDaWko7td`tBv{uzm)sB5_Yc_z2kL>$FzavHcP#7#6mwk0qt^orIcqjtPVXT9!N7#`rlZP7kcnPoab^rG;cp#hx+7^eXJJxW#@M~<2t?EQ2A}%`~$i(-FPXtNjI#UDf+z^IDhZ?TFN&{9DqKvru46C8S1Mi&Vru18_G|<kNTa@Bj>GJ+%3e%=dpixPRhALe)~_8dYU`(q5ZF%mh(_;$8p4mos*V}UZ5A|o6U964(-CE9kj!xpzCd9pYF<kMaH?S`bNYN1F|5F?9mSA8GkQ?{^5riQjeKU5l20pwnX%V4tSodPw{-$t3hwr5dFJ<G5n*{OF4hh{&Qlzh|hrMKX(WE*o>0jXmSSQbbAE!>ps$7`eY5~?aiA)AC7&p=HVr}>p-7{c;0Ln7rx8Up4+o6Ks$%aK3p3WEdFCuYAbPv*7+yd-|D#^iyvz9YRUPd=6ONRN9+&&LY!9T#Z1xb^pbWq-e5nWeLaSLs#r<ZOU>)+6#4D7Wtw1>8;GO!byy|8Z5QPIhc?$2akQ_Gtmnq6YI2^aZ3sa7r^M$`>7XC{XRfr{jNTjvug8d9Xe9i<?FQLTYrBSy7Cql8jNATGFs?#tjuO;f`HOz-H;n(5Nh1WgFEhu!ho4-0FibF074%ENAe>)qDn1l`z8&#%sly}T-|;x#S(qqsh!Im{zWi>#VxZve<%naNZo>PqBIgIduU23@#?C_dx&8XVUp68xua^Y9TB{xy7p2j^V}lmsd2$vN>|Gl5S(2$W{QF^c`E7TT_SR!>AwK`yt(D-toT%sQR_L$HvpZt^Pn2?vAHxxcRU6Vx^qB+Ep1%)(-)`{eBfr-sN`JY|?2`Iw{)M5(UKKxbEnA6l8W!y<dPJhc`P#WUa-O688-;U=qnU8-yrvPx%kquCh<<kq&VS|)lyR+XsyYz;7lHV5dPDf-{+h!?Po9tQKK3j6>C$@W`O@>;XQ}MBv`=Bf1^4tred3-B73{tZdO$|p_x7LgTP=s2qiHX$Es=3}q@#=rZFH7#$e)0DVZ{ct^Yt2t^9tw1zNVEIe)}~CHYtgE-W=0Z%5Sn4dbf=@AFP?M0{;97y8Bb9zm{&D__r~2%0&5n2J5;u;i9ZxT7xt=hxYD^bN*wMaURyKAM|Wqc&-tf#XpT-$3P!G2m7F6J~Ga<GWDkkn%Cug#AWh%cfEo>bE(Y3Mu{m{FE55hiq3t3b|5?IAGHH|nt1rFwjo?_^?m5|$6($W({<f<`n?D|@5RRO^W0tV-YmmXy!Y#02mABZ<z!ygJo+QO*OnmBU-q4a=g5t5ojDTa{`SLcw0lo!7ya5|%#$Hm=ZGFy7yI$9XArN<ih=H)EbXlCXoGol@_4jU-dLpnYp$d>c85m6Z~w%+)PDC6X{Wp=vAzyFgmTh1#&-mRZbF}s7we_(5viXsET6oe(Z<xma}5t3B<UwLgYLc$>(l3+az3QJjfI}*hV)0q%Y0-cty+k7KiplRbNXq-FDZJ78<Jn2eI0tf#fwGHk^|>H-QURjUhVc%=xG9Ey)f6e#ymOw9rS6}Mc1A$mHn0xJ6y(zmfjcbQ2FH`jQ>Z_=jKKH_s0xrFXKYw@^9Nmn=>BqMdBj((UOjMA6#yPtY6xWNSx2{eU>wOGM;B%L%auQUJdKVX@AUTZB{`a5+(DL-tBjZD-A6M`VX;)KMPdAd{K5Q^me@wKc>BnbA;p9pg&&2I4ld!DekR;U#!!96FqA%^aXpM4<9P^a7L8J{wnzZ^cIT{hk3YU9GcO;K`&HT)(MAm6waI9d9A_o{fBm5F&pPRYYRbNI#K3Xd%olF$96jOcX;os6+40XVozu2F-zgUafR`|wMs>dzcjm~AB>ypWL)SS0-*aFGXC_d*v}gq8$*BMg>&^n>*YO?zUKt=T)yz1SZ6SPS3<lJm?Y!U)%6AT&oR@Wmso@PH0_4{bNv!nPrQzcf4EAvhyE-b=I@)Kc&@1JGXLv;O@}_Z4D{#~5`XBU=Ru#F1Mi(jU66UesB{#1TmahpujaD881I{6{yrMvL_2gAKQ#Rdq1+F?v!&jbW3WGbvk~*+(bm$x_R_22-?=6u9+@A9bDf{@{fPFczO46#)4+LEj>kA3+%*ev&6B^dUl`Fw+R-r6V*MX;0Ov6C3y5Dk4#zVtxFqqNnduq)t?*&!x3`Ob=xfJg|9aXD{;id%A?Z8DiND!*<%I4RF6*^<xEj9CI^+v|KzY3X-hWKibypzbAuVpQtRJRNG|um)Aig)ZPR0DZaqo=p^v;u@A2=uRs}a)|<ruN;<vF+38ZYQS0=j>BnRkrSNzzWP6_JR;t_(&wAzvfpxpJ*T`A7J@#(}J}zSE1JfZnYk;^x~&Q2w5FQjR|MmdwMt{s86A`4#C4r5`8lF#0vh*^TsC+~N>v|2o+*kB?l6^aT$~oZ$Ma9Okd#U1VM~<}JWHpHv6wv#v+_&)H?2a`=QIeVfuq?+BB9j`6i8^hxQVf2l3y>&2(+<ak^JzilP^AJ@2j(Bs-kyO@Le$@q1CK7jka((#>6li?D#8;=sP&l^?*&sFl=Sh-K&N$5-K;Cr9&e%KFWyovGyGfLd8_gDeHi+qdozaGQ!Tt_d-`mXnJ$M_F*$2s}hD{?-hHz)wTTO!i`ofq#ZXWFqI3@n3szQ=bB=B?t;%RQ0w`kru!=k?s>x!?6d`k&%(PQM!G3g)z`lHSzfah~^P8Sd+z8PAobOh>uCt?usc+9z9IX&<v`W30#eK9my@B=3#Q$1Rb5?oUX6VY%$1jH+$0&TTJ==lZt*-n%yI4ZUwgSugbK2QXe*48^=(=rY>BY&lsUO`k~Ix4=f|>&r`gWVD|Peb6bK^PH)J`KXl>_32z0&oyxb-oHHGfbu_jLN9$6=aXZzAP%lv82Zxe5+~>{#^M|&(?ooyu{jyvV_w1gbt8Tmz8fm}0rA?9M8p}(%b{N~)|WWY{Bi~5-+PYw>x*jE`bIbUY=)k0CH7^j(jtzp6$bs#FNT!+ECcpS!w=y+KR8zA2Yt0a&z%Es-*Iyh7w!s2+_@-PzK3+w*e2sfue%xVp+ETH{4*gM=a~Q8M>z?rvHvXD7w4Bpd~hC772kzv4esE3gr-&bel!~OyfvYpl$)y=bbD#UB{_ZYp1kZ_?0b(ikon7T`j)IWM$BrYk0_3~`Ef<OAA5BcddbdGf4$9HtQTc3pq#bM@xCngGMTq^7v4{3kMF`itN25omI?ccGl4iSaf=@-^|@LY`kfBg|36QUdK%t15Br)1^I?q*xL()~-&-x%hJMdfNaA2)3D1>$_}y03Khf_`pc~QDAKZq10pIOv2Hs0)Uw2`DSML>ct+&+A9JqZG{NWAu|2BWL^YvB|kC`VuaK68_5&R)x3f8rsbBM0pOvXOE`gAGBD3cF*je3Y9^(4$2je0_VGEB~CjGu3!Ug6uIxA-LUg)?^se7`e(H}+%6_#VyN)>zuvh<%6jD?`!#`D()tTLj@8Dob9}v%o{d^F=y~u2=f?JkmFl^I$XAK<v9d{fBnW{6zK<`VW&)PW4~0-!>-T`<%8@asINx5B_>%5aO+U{C;^~vczZl^c;AvJKDs3%N~J0XR*nC)vW76`e}y|4<)ZaT$+?k_N(U5x)@)MV0<qe;)i{5Z5O_OoA3(bXfpTD3ySi4y*W5n(fecHd&!RXK1XMZZVWqz_kStxN#EN>$nW`IP)>#0_zreSJ^25qVsfsb^E--^@ovU6#d*i7>G)2#(EywyZ|DI%p*zY?qhnu|X*l#1WAOd(rNmWe@7<ysd|vI3Rnk62hkZ!DCk)>+{N}><pHUZa&ebco)W>dA$GQA(8RWZK?c@Z^Go5Q-zHgBc-`kFat_^~29LyoQQ4QZ$>Upn9JDaiIC@1YNct0~D0pCxSoF%#*o*jNNJqzZ;0t=Bo;kop?+29WPz2@&oe{l@%`@R^?vu55#eeUjnf2R3@bC$WUQBLR;eDCee@8TPMMm<*^fM3lr@EytJjQBqB(RrM+&x%1i`&EU$qyhApzSu`^2ol}AkMH=jbrawxjiZr1F%jRx4`F*IB|>jE0(wwd=&@H(PL+aa=ZXb!E?xYZ=*HjzcpucKF!b@Sp?iLnb=TE#D!<RQ$$7liIX~(X&{y^muCdVdxzwMBi*Ej!6?&2J(0jRsiM~7=%F*Uw{@;>8;!KyVG4uuR@I6|Q&G=sEC+KDw>gRTdZl3Cb?*hCY!f)@k$NT?;9=PxQ7SLxb5kE1UeUbkCD(pkHeZY6S6IVc=ku1-vx0@;JkNwta=;!g>qvqF0<~?UrjQMSQn)Qd^JY>c`)c-U3Tf3>tylUn+jQYIFiFVlkCQ|CN>Lc`LpHNTZG|p##`h@a-^Ml?%lXDFFDNnrbeen?OaNkGbE_*F+ypQ#Bryq~RzAWvJ(D^<^yB&>kqC)UK|4bz2nY7ta|EZl(ez*OIpT?h-{fMI-{$9bHa~98QYbfi2nLGjSMLp+Xp6}!(`wv&9RY)In7=Fe5g){eYq)*ci^TWZx_%8d&Y20^j5qw85ea~<y@7PtOKbQ{V{dEZ5zZFZybMd{rF(6vXagI)d?**Q%#kks_V?Ib*5_*;r=-1GN_<p~b4n6cJ*2Nk_G5$(5gMM!$_7Rsc@3}J1WI5AiozrjSl6ld7_7(I&rudaJN098hoinrHJ>d!bU5sme2JFXMbiv<|<SdSJfjI{x?r@yDf%m0p|CGPu(Yw?`oK@Zv-!-%;f%mSxE8@F~Vd?SxSIwF5s|GFb9y=-KjI=-he!<w_DSqu7R`aZse|8Z5zGqe|SvTx8pNX#7r{jHJ-9)?}^nQLp%HNE?r_mGK<+;s1#V?6I{~F%Ue!VFErVlA{Rm$Iy3x99X=-I%8mf!sq)}d;rPuWXYcd{&_=B4%O`putUDN(9H{NMixR_{vxSAT+4CBXmx_fN3O*sQ6^vi6n@A-afL$X(<=xB=~M;K~&DBl?p2k^2+NlKYcapebISScbejc{$<(8+bYLl0*l&GR4PH8%C~MZClMUKg&EV%Wj!!^6JDcG{tKWvy;~#FK<~zVoqXq@|@)EL{D;sg~{E?v(gmzA^MT~v7SCO#j9A>gjkzcjl4E_1ENmefV>s4BY7+GK9=pZY>H)*h~ebnygrGh_+(;7^2y{wX^Ph&>f}0~rw&c=Kw@F?!fc~Jn&M@MCCF3ysSHhV2Tk#QG{q+pyO2*LUqn-U46z3J81nAK^5osg+iIzO-<GC$JIj71{z$Ay{v&xwVovfL#I(em<O<!%6=o$*OP-CUxHr*<TwxXRABeSxRmf9(Nb%;x0W`&X5u1=J>`UH@d>T#h8I~<04kz{{A5Pwx*o0hRZSv0KEr|`tTavdSwjyss-kaEmTwyqQZ}Lc*;!}xJ$fuGowrmG+BXJ73!oB1jthpo1vi>y1M-#)z6;2@^O+Lr6tkzsq+_G$zJ+T2F+F*)*CKe}Grg#p^@(@cAi<6fkFGkEtuJE=Eycqd2n&Rt-bI9kgp6h6ePo*h7oET27upjww@`0B9LhMUZybrM-c^~o~mUSckOzcPAkN5bQ7)Jgxd2?b1^5*0<iM7dVl9!_?UW8bRya>4mP4O(2WgwO$mLktf^rtBvL@Y&KiuVX2b|CLSzX_r#K9r{TG~#IT(d?UPG{yH2Z<F7qZ|&i4#qSZbk*E0FJ(}X1X^J1DDSn*zko-9LRhr_DiJ!?IlfNY@AAQT;il_O;kJHc;&tzFTq9-vAxhHuMVkz>x#1h0(<fZ8AC5Xz`OYpbiFKCL#5Z93_oJu~AIGH$=d@}h+;&5_>1Ibgyz)0c%@<`4#(KN+Z5f_uMB47K>e6*IP_^&j@uUht>Wj3qq3q++|;I$p(J2-D$Af6|0WTkImStnw5@=oMkEeo`)j%7a(%ai{=o}XwZ&rhC>n1ehUc{*Ym@^s{nHQ-$hT$$o$i6_a=k{=*$B0oUBk~o`uC3zIlAde!SM;u2!k9;X{Jb5%Rk~p4xCUFpPJozB<Ux?$#e<2@CG{^^&Paw`FpFr*;ZX$P*ClXJRCzAg~yi5KUxjWlfwY57<@!Z55<hjX95bfk8$SV`elUFAHiCBmHC-QbQ#aj{s$raWmSJ;faC3!bu2zfX19>gx>J;?hIyV_FM8pZn(yOS&IP2QVhRq-oU`y_CjDUADO+{JM$DvZ%m$EM<|i0ib}vAmAHqj0sBI`&u7kCu|pBQF2O50}$Vx6+SS5TnSWm`3q~#QntO<on6viL1$1vrh3e#Sar>$Pbg7#5i)3{0K3D{0R98n&Q6`uaN&vuGwIUf6*{^DZI+xSIDoh-4$2!RU6CdTlOQdDX|TCQ}R~CP;!NB$y<>(CN?2&Ox}Q4kGui7POMI@lUJoFUXfUdydrsNn&Lh-%#-<Sm`C$bOPN=FI3|3UK9E+4<D(MqQI}Ycye@e&ViWRa<RQei<RRo;h@s?N$h*=M??h}vuCNh#Vau{wmdmo&RzKagY$r|e^)$t|5pR%hBR@n_++|s$Rn{@fl4y#*rzw7hrua;n;t|A1@(A*t#8Ko5dy)4fZ)lmDW!WwJYSqD$=tWez7q1s0_aZM&EK6RTyb7@)c@^^3#9rhrh}~(5_a^qTrOr<Z2M~La_u})U#2E@F6Gz!n;}*r|5hKYX*}f_9j=~qjBytryDa=buB2Qv}<ozZlOG{LGTK-o2F4LYNze~QKruZ!4O!8UeBWQ{T6C=oj$*U22lJ{i$RwI@ruSV`oEJW^2o`;y7JP&zJq8oWm^7O=88u%^xZ+c!+{9kG}$p0lzYXjaUSNNJ-nc|r&%xD9?;%}wDqA9+QxRZPzdCD1x;tt|^a)mv$)H4&sQ_fNpPdR&0JmsuL@u9@^<m)+xQ_g%8pG-WYrJf5Zo^p1i_+FxmT;VP9z2qBdik~N{wmwh%s-?!V3jZU1B~KZ{{}FSMD^uJ?Ei1W=T&+JEF*8x=nQ4j_Bo-zwNbXDYBlji$k*2s>uhe)~^JfKOee(KDQ-P*<QDR~8!mM{uq9=J#@?u0Ua)rgo6;>fHMjk+HO`b9z1rRHcSKvJYm^XmG|F-O=@=MEdTjRZ`W!Z@Z$g`7c#4O|*`EwgkmGPWq-6Y>=*#gVfQ&aalOgu?`n0za7ANf}DXyP{VX!3=`_2lb$FU9||?6PGSsHu7^A;yv~Azwj^BVR$jfw-4^1Nlzk5%QhniNp)!7gz_yReP%TE#wAG)$b1RDfu1pSHutGugEjF0du*5D^oltu@HG7-b?WpRyV!1?4D&2mJPIQK5-WLeDYny&E&htFB5+wzfAs!c#r%Z@1^)1%kEqDjGC&)N8%gukK~_-AILwEe<r>s|4jal_>BA+@1=N%Wt}YRPfgY1I`I<ub@EfhW8|mE_Yh;r_mD3jPA6YLK8)C(yg%zOjP0!2J(SpiJe0g1u_1Xq^7<@8Jx?QIee(KD(}?L?usnrbzbU&1(<uxl4`rHx#8KbWaV+zVWu6YarqawJ&e2l+W+C$}WS$6KQ)xC6H)yH;w4M33GtYcpQ)zx9p4L+R>>Tr*W1d~SrqbLa-qce4?@#9YlX))lno9G6n53nSiGP^yALe<)Ybwnf;sY(!U!OAHQ|5WgYbwnL;u9^^k6$w1OXm5=YbwoqVzQR%-_M!vIrDttHI?QW@oz2F?;kSXL+1I+Ybwnh;x#RGEdIfKe=yHGUQ=l<5zlC;<K!aqU1Xm7yr$9|BOcXK$Io%*JI*}Uc}=B>C2rAD$JK7;+s!<ucul35PMoWyj<+Suw}g52@R~}~pEyEG9fzZtZ#45P;5C&dgxF0>oioCiFN}GH@tR6gpV(SU9f$3iuRZg0;x(0~9<ha%I;Mk}FPM20SL;GyuB!_3eY5Vma~@adL0*7qvJf+WvmU>(A)i8bmXU>N)S9gDoh@~peq=*Fg>T5!wRc>f75?*0jBthdt}yR&Ui*jZw!%x_tm}uE?-29c<h4s&&lQ^AtoPfQZ#(lG<~5V+yux3<i33(L-%94$%4@$e7Erk3oA_WE^DSeZXkOdFxIp19TWZX*l=+r2&q7|?#dtyC0b6Q3v7GsqGtUBEQ)%Le@wU`B!^wP3=2^mPD$QPEf-N=v*u;FBm}dpAsWeB3r);Tl$!_M`%{&`;O{KX&ykSd?SB^5@QRdmnYbwoO#QV0?*y=p<ooAjzUQ=nF5?|U<<C{O3?@#8r%xfym2jVANYTT2|e96pnhu2gZ74InYa!ZYe{$;*@ndcSLc`+tZSn!)TDLwP0XWk6FUX*DHa!jVgZXV3%!90qWwT8`4mK7vcAg^RuW6KH<eaY8Y*37bz!~pW5n)+YAS>+OK<oPu9k%^|2BihM}Sf>8}x?V&#^30ay(eO`UI`Z6>)wHY_F^GJKW&V~mB^D>IYFS;&vJmr<dstT5vNXg(<oPXA|JUIR#8Tw7tOqGz*?3|{^3Ik`v}^)#HThc0CRsL@IF|gQWhX2<OPoP|&9cRots)xa=Pa9V*%#t<@{5+)tj79}=uQ5IWf?90JMpUx{FY^FEc=bPh}_LelixBQVrlZ}*0n*FohHsEA8c6-%c6*5$XhnCxp}$&pZ*umssGe-Y2W=1pa0jK-+z|$ZO$oHS^x7RrIt<7ich#%|Eb{aZ?(c{{{uP$&Sd'

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
