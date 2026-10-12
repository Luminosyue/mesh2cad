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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_009.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_009.stl', 'source_sha256': 'fa606b7f6ee5a415f710f1bd458dd858f41444697b3195496160091342227ba2', 'input_faces': 1104, 'input_vertices': 679, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09106704592704773, 0.1996878981590271, -0.08338230848312378], [0.06207461282610893, 0.35032057762145996, 0.11052243411540985]]}
GEOMETRY_BASE85 = 'c$}rZ2b2`W7d76y<eZiyX~;o9kSHJwK@gB2Im!UL<RnN=O^%Xt9Kw>bEIACKA{hZCh%n@gAV?JW=DmA+ohg6+bN=W1*7MH0@7Al=)m7D1)zvjvw`QEU5f=WkTVHy|f0fT|St3cT2&+$2&u==mjp|jnTaW%>R!ZgN&(YIsH>_2+X_(c=8kjdSs#n{ddCR!+mTOl!Z$VeycHMh^)3bHAR^59>MhRcFb(daI0lrs<);*#EcD|COJ}KxbmcO8Du<QTwFL9s<_J?)1@0YSvy>_BPK)LERnJBjJMi%hbN}m$moh8+`V%vMuDsR`Deq4CZfaep$b{&lm|MurJjy3qvDAk#+Z4=(ztgyzhjuaWG`JxXiZ!e#waqN$qk5;{F4)`V3FJk-J{jJxvzV8G6)M1TpcXurn+dreZ@>a{g5P##`VH$tw7r1V#kCeAFv{!$3jtemwr_gKM*Nkb(+h1)0KWdf6_Z|OoiRzromG`wys{Y;!Q@k4ga98E6KL%*|{n>k~zkRtJ;ygaA{=U@P7O6h8d#my(r=WfYY+Ea~cb->y-`#ZZZ}{Olu|4N2ZAE!+Derf;P~KPL@^`9>{eD`@(d+JHt^YDTl(&y8JgMzCpw?<F&$2e)t2WT<`mg6%qu1%s2z<2>8sD{Y-b%f{7DbeI$DG#qR>vb>tNtm6^432!(eCvNB2Jtiw`iPnz0asU^Rkx5KYt<kc<qnrb-$aW<?(jt4!&<+^|$IBSfcj6mf-i6(sH`p&o-;QqXziVcl5q|&p%Y#+ZWoZdR)tCxAM(YT_dIPzP7y(|5DqIdi}F6G@kYPDEdRaLh$=!>1OoLRA)7Q*;QJ8>(y{v-@c&neJ!K3-K~Tbz~|1O{;nRMX!-pu3nBi^JX%iwHxo9hzL=A765zgWrQM`)p2t((S2u;mv37K7rPn#}c9Z)5Jrw1yTW7k~cdM7+BX4SXTtlBP)B0TbxANAd?Ak8g{4e#o*6cCxPt-{3-_^2$^7it6;0KjJyWd#7LH(0=R^IoO7xhr(OVmToGRnJmuF~?@zrI+g`3~d;e>*eE@7l6j{Yxi8{1tuly6z)!x2nFB0Oc&OQvLm>=6m&eUBbcFf1u^}MgOo_uXE<fMolk}5#@=jJ5}?QyP>?5AS3*LAFKYZQCByj|8&H4C(hWSagJYx|Kr^1?;iI~d2iZF%Dd;xL;0;?HI+|s7;zeHJ*x5h_5Dt-`{j4w(-+n_)`8}FU)H4Y;B!61bDj1G%KzIKT(|QGjpHv-SL@kx>KpKp(aPJOzuX+cpUH;tFmWR-r)OVT@M)Upec6BIK>YZh;JVTGS#N9A-<P*A_^^j4=cPtke*1N5@KxGq9AB~rh?D5#293Wtj+VzN`$*&Xzg?!h-TpDkvwsTOarG$hhn^qNIAfwTj;}!*#F?`Q^_Kffw9A&l%KOfy`c?VUCnn+f%!)WKCZQg>EYRn|ewG1zic)CzYU>tgc}Au|{DbE){=bZ)_hqd}2><(Q)!*G>=_+m4NAbX)nTmQllyke*=bgXSv%hJ7_QbidRCS^|%G=ZDqCa#yF-fmG{UrFU7jR$Qc5GAs7aNrKT~34hO7mc``h7AN@oW5o=Y8;g^q+wvz_%!ecJY0t<#Fw327c>bTAx<bKGZ|@T8O_TvBtOD+0uyZd6X6Y<%gmEhb%)sFOmr5{Gq?{cA5-Y|K5J_!P~#;xa2OmAMIY?xy~o{HwE>++&RnRzTRF`-db@Q<uAKO+ui=`Jm;SntvBzZ!_k^vXd>bqxUScA#y8*iCWtfYIr?Xc?0Ua;&!p>u>&+iFYNgs+pX+>RpC62R=+<82xZgfi-g>u7d2jvKYc=2DAC-5;D=XCp^VL7~LGY_vBYyeD+TZM1vk_<9Qq<3jhcT+VPlo>+kNUgX6ka5@|NJoJ-BaSA{^K?sul~{XQO<%}v_7r+WzY{(R7ITet1-SsEzthwE>ae88V%Qa^FJx1^Q_17V2$#_JnHWqUt9a3chz0x?aR$@-Sg8MYP)w|rMxw3IodIGxVDQc`yBAcFXFji|MadMia3J?>HYdYXoz{CWP9a(YkQy_Zzj<4xQa9YUkml%eQ-NkZ13+y5a;14JV&l7yEOe<7x?2j&|ZCCpxsX<2EXhT`c=Z0J2l^`aPWsGAb$LG+Ai*9f9bqocgTizIWYv|*u4jsPpU-g{n~|&>iv2K-iH7EX=tww6X&Cywt@evI{I6i!dgz>)0xWqqFbW=D?QYHYo(n4zD!!w^H1sZIdS*vgzKiNh3Ea$FfG4lZY%Jqi=v#f%3vPPRSkTn1{%k1`=zdLU0tdm{^&5oPc>w=-uJI1!6z64zTi)twVn^BRNft#2K_mz9o9LQujqK@^UX(p9$SBz_J{4~l(#b%LwP#v)Bf!0cu4s`ff2v;7wG?|cf!Bvd(=<q)p}pvryDR{ezykY|InH%wyWO=_)m(#b6q(L+VN^{lqd2#^z$1Fb=~V(kQ{OLMxmVFAJg`Bc<cQv#Gf&>ujVh92z=AFc&_uTU$58M8wc0zydLYlmNn3y-#^rG!k#-F_jUgRtb51*s=RykD)g&oU1zHuy&e8-$HKo(R9~&1#mkkq7MIiOx(05?`lm}D#Ob*l^?$85)^lT;z`ySUJYO55cWC;s&oFMyn8xwHx{dqK4FBjlXqV$z;6Ez@`~mb6_op9C)AG9hS)p;V9#G!1^Y%h*_p+CjcmFUR<uCqT@7I0oJpAWHqdw2QSKC|SDE#{^Lj05+XKDTTwyeN?EMY&N&_J)-v=R99<5ADu7VG$I4XmlWy%OtESMdxO9}a$w_~}p{_vUybwSALRh5yVlXh+vPZAV{+)F@}mY8uCL{4Ack@d*&;f*0j^_C=(Y^K@L4=f+mFWA3H;Tzj6r(s9Tx5dr@=BXzy#I`%|)-<Jtdp6x^RJ<E>x6a11RsLxy3^m*}5+k`j?k7C?g7I#&JV4nTTKA&}r^7EU5|G5MDNuy*dL-+>AF#cqmtLs=#!3N+*ZbbZjw=mAT3M+3lnvL?m$<{~Pt3^Ec&tHx8Son9l)xX5s<y!t?Q{bQW!zpSHeyzMc`ERV#nswQY_Iv?8{Q~%x8b4Fx_r0yWwd&?!ji2u}))jTHAbyqY@L%=5m+Gq*5NG4Jn2*xlU#|J49Y&nJv$0<4bZLe16Su)X%R7y47tgaPn76jp#(I0q7%iuN<sA4QE06L|yo2$1$tdv8e$hDYnD#pUTla<|&Y5q~zRAao*83VT80C-H&*v_y&ewLWHt=7V0q=KlB6Qqvc)Rva+^=hL294993jBAh1)nnBJoRf+6#kWxVm+Vkl$O&Kksbc|2cbM`Gwb~BO87?mm;H5i^#2cb>iWbt=Wp<9b|HSw))+T;-c#NxItA;u;Y~EY|Kb(!34haiu<EST@!bFO3h)~eVZAY{_s(G6&ax5l-}mdP<w><1e3kf^_xavo516IAZ)tL@tJCGe{zCmph`;A5=GotV(s95$e}eMvRT#Iec14G%U%VmkPnit!!mrnKeDl;Ai0hU<kLM`tF7j7w2>;$4&|Za~&(iuV@e#^%{0!!c<MFT$&^IIedu+gUznZM;E_aQ0x=-WVdk*8tCzJ91JME3~*1bdU|2R_D;l7J6v9FT?<@7{+yH2(JJ^0(p;Qv<+eO|0odl6?i#wE|Q68hYEn(o4NtM9;lrK!6>`2icjCtrvAx;bZ#+An*6&xZT5HvN!a^#|>6-5>Fsx;HHuqxI9GF8HR4(JsSYW4~j0E%3h`M4T(HF;3PkfPJj9i&36Vr-mtCBR#IW2j#J%Ug<dF&sTN{+TmyTkI1Rdi!Vn$<*n|?QJ$l}W4?<@t-Np6Hr&_H#CR^^9>)9nBgQ#bxrg%aVwATduYw=D2;<?o_27@PfBx8dsPezeL!9PMaNT72w7p$xrYUc|`4rD@u0;C$I(+Q&yQQYKi+@mG<=yd<U>`5l8SS_3{jCwdObq-z5n9i_IxWEGzJ>dGmq6!Z*Us9AbL0m6|LORd*xq!RaNWtJF+Vn4g!R(mds=_)8(q<F`?tq_hwlpb_$x6^mTIf}UG7!WmABsiti0>*e#*O=jevj530$}Ix_<kEc;CRYsLwp>ur5#13;fK<SjXP!jQOipON@UNZ(_Zg`~v2YDb;Y@Z<b(w$&-7JmjAW||0g-%f7!h|n77*0!TV{sXNa@wrmjcq$Ja2<|LDTH*RxT1_o&}cpT~#jdc*s8HTe4%xE?Nx`Rn5u%KOg!igw@jUe^z<2ICOl*-tC;O7F`(tJlKd{%>CxHbt*ftu6TI1DG#%UfmSTTa6!M{m}QV+Me?*!8f|4{;pi<F&-W(1^&nT;HSjFerAi07Y6rFt5kPgpIbxn!hb^!><_Q5ruAcAjSqjmH(8H!>3gU*=Mx<#?6qw$&UYP$`7ZrY@H4LRy1(drVZR>&e*I$H*MR0*f_dNm=BS^-4|H8&ZSJPL^>NbQ)c)gu_E-PJe{|hsSLJ-#<bjUQt_@F=w;s&H{Bmre&M%(Fzbo&%{s!$hb&{^1|HJ>eT*n#DjTpplni>1majs!sg}fDQp*)$s!+Q1C)bOvg4(|&U8teMOKj4y%E7qF2*tbugL7#W``%U0u(rO&{yUuvusW>0}t)X}x2TaF%8F}BrWLURPXrlY?-VvkVUpgDgGrHv5|H=0*Jy6S6ql)tG&3TmfuPUPD_cYC@`P}<Yp&s%K(ESU4;zY{ZabDuSwwKcNlBdo0m<LuYM0x7J!9IJV1<Kp}9^uZJ6zx)@5BNr<P@akJw7&ksPkGZ*uY00~^46>>%DY(4{+D;O-F!c1gn!?Yy1w)$+o8OjV-x!4i5J*Uj`~`8EA=VN`$;BgeY)qDK%7R2aK8_>>wM&%oC5DvZ(C!0o>m$AMN3-ib8k;O5wc#2<xh8lf5)ZRKRlOPd0+g(cuuzu$9I#nt8^ZAU$2Dndz-i4AH@5t>gW$idh0ml`FkPe?K(}tugI<AjB7+D@LX?rvt`hE%|Eu<42}P;JI3J;Kh<&A8k`;cs$m$nKg^}$fa~nV>3aQlxe&k60ewI5cO9a<`>%Hxm;U))zjN97(kpM(ScdqCKhikX#rWX!R7E}aT7dQ5gy+*Vem(3{`L=D=eNK0oj^Ka(1MB4dZ*`pU4XUraHO0pB(&h*3KPRgV-m?(n{KqwQoOc(lj5wJ;!2asNuP|QKDGh(F&#ea;FfVLL4}bd)jPo6{Z3^KpxX~_l-KP74c<W^o@bRiI4(5HoM}ohTLfgf=;>lF?-*Ow{Ue>r6hr4c4-u}2b#>w>a(SIgI!$0FTl&7U1<=Hq7d|#}u?9-oOpEQ00@aZ|8&mExSs`Y6G#P2v2??LSvZwcnD<A*UGc6qGNqwjcX_$T=j`y@G6;XSL~?J0PECu3ZVn6Klf_fQ7RZ+Bmz-4kqC9l}3Yj_2<C#rQsTCmHyA-O-NLHSD*~8;5-w*FcO9x2|KKHn2d~{x)U`#@nY4G2b2fO~2E+Clo<FSNu!+r>CnIe6}yJPL7<d^Qr4i7UiA!(Jr!Ltd_I=3jKa-g$>01#_$SQ4`ls*yvB(tgZP`Wf4)D6w?{^Xw!7p1tRtQmj!T~5OO*HBT7&s3^01Eo-ez0I>2=5Fz<Q=vc70y#nkm3{?1%e3_(b<ty{E2^)i`I~W4s;K3*&9-6UtjrJ@k9Ack*cMSKimdz(*EDyUcv6@!ePMjZ)q&fpvbfZ94wAR;&g;;W75T^Ci-Ha3vb2yj`Xm%b8I7mAgv^<$c}TV?9%3G`{DJX{+lRYyU$nk3To|wfwbmfIm7B_ci7N?BACBZG_gFYl?o?^TxfW@jcUb4-byx$}?j_FmJbLi+;7MuzruTU7slLyEGkf{`gtnciba0faiMBmt_a`IeiIrK93z|Mn2(s=B@5yS;-gSJKD?gIzCw8Pr;wfjCJGKdb>mTly&jGzd5P;`=d@PZ+~+W_dBDz_FMnYo55GQ7BbGb@2x<bi@QRe_gKDd6!w|_n1u1+bTjZ=&-k40W#sL{7x7$wdlU0)#Aoogu)eaQXU2r^6PKbsm*>^@Q>$Mt#CiU=`unqRyz+L^_h4VzN7^o)(SKn7@OlHhAAepP&qbb;*dOe1da%anwFKX72i(<mvGznM?|yI}&tv16<Fwr})EuOI^U{cuZ*KYhLA*VuL+Eoy-dfpNdEd}!c<!3q>#zRtW@28;F%ZvJ#k5~*xsrUL<+oV>R_}KmG|rk$7~fuexg~_(x&`g>dPGbJfACO9d&Tm}@1mYp9oiAh+oii<oFChHSBU?t?3kyDf3!P<zjPJ+gp;9sj-{CI-e=wu5<h1H%xf+0;{7G=Aoz3rA3Lv2d8O+M_gDAPj^+Jm$E7vFmpY>D<u5Z++sn1?Sv!rt{dGuxh~*332-)wl3+F$wPxQ3C=%1PT$As{Y_Mto#>TC(-tvRPc>ND0q+1-%x$MS<8p}nepw<Cl%${EWq{2I?u_XfK{_&2#Q4rIy@T7JG)T0M7!@?)a4{;gZ__JovwTw{DMu6#Pg->PvBeAgbK{O-OOA4)a(E`;a!Z+$&Cgm<4A1pdN>(0Yp+hjpg&T|2fuw_`rN_*+Q5`HEK3c6X;K8p69fV7&FNJRMSR*56lf-ey|ubs=&3#KXMyF8k_``bo7E^VGA0D?;KQc^fi+#l|mOGGsoA_1_VR@u5ckg(26?g7vLkZk^6MvHTS5YuUwf%nI@6_;1a<zCPIB9DicV!*R?PH`B@xe`8#Vy<cNoij8B8OZM#B?JE4Q=OuNT_7(m|zjY_<q`dh&T7w>dH=bW_`*|HS-FV(Tzh~BSK<4-s%NyfcEN_f&vAi+9IlMW(#rhlLTP$ykZ?U{FzQx8j#y9u&<a$2K9M8SSuJ>1eWBhm5YBs3C|7b^tH`~$S&35z^Z8f;U|LQ-tjw)}?ckafuhg1maSI+$C`nA9E=6vcOcT0JD+HH&*O_rdaq$+5uHs)pPWJTr8`8}35=l3pcz#Hoahd0*`?&ZtiZ>&#zBQ}6H)+g?^I}yiN=lEPF!5ix$@7_NV$5>y*^2YkgJO4F!W1Z$27*EeXn(I1O7T0i%YpesUOC`XY>&DtUlsDI(4*#F^XUpazG|t?P7(Z(~)bj@J$ETGy*SG$Po{_=voprJ&Pn5n-o9k-#!BKe6HrC;;dAD)S)L75^9(U94c+Pu)zgs^ok88#_eeW^f3+!V@#s>R4?-BL{zw+jLhn;q#_V@q1zg*ad?-j;-lf#?uO|kyQdy{Q#n4o^fdzpXG1?7E9Q)@Zx=7q6Nj`?7s`Wx?e_Uk%&j>&v~v@SMN-Z!TQ=TjffDK!|ay!jsLO8IcI`WMK8=k)nuv~Nr*?8_SOvsUi(;EnfRcfF65cNgml|EOMgzgyQqd8=P0)W3ZM<G{w7%A4=q_Plgc@mz(z*T?e4`@1`FX64QIeRu!t%KLuVjQfq-8_#Ldx$rmk89euwfj9Og{GV*ab&Y)tEAC_X8~Yws%5?hu-`sEU4b24J*l%%obHBym&HWZDb2<2%`#i6!BEGRN<huAJ{EdAi@9g&QH}<1Ecb|bb_OI+wX?1_m+y`@)8Lqs!Z{{s}L3wkZ&AymzhT6uyoTp(;@Wwu#XU|ITLvEv=4=<_p>GEgPerN6ny6P_gZ|ooXi>^dJHTEGL-rR@uU3>_B?=zeauW}LRe)}ZHJd@<9@}APi@xD+Zm-7GF|9sa9>osE^)t7mNo*VMrNT%1df1IJ?zPs}_<;{Ivf5Y4GH}-+8g4O4!ZR{I+SAL_sx&Qnhp8L<fZRzLg_09e8m6hfxZ|tAD!}}|5HH|==0^@L={OSns#{T?&c<#@;lP?Bu?EiaPYy@w7FK}1$gEzh}_&4p;?=$B23wM&o^YNU7ejo8Qwa~B4?<reLDj)m(rEbGq=zl#!d489%S`J1W<NJ>1@iXwocOrj{4|QJs&-bPhEx;S!v)s|GF%KKx#jLdL;ct8w^FI9={>Jw;*O<HDjqiQlUtfWLG6VG%&kerHd-BHjMDphML~C&goYTp01J6r~CYWa*ex|(nz0xYz2*00*Xo&Z_v#oUB%)7QZ;uzmOT^+xMzww>ayL}jV<GZRS-Zb#ZPH}#Wk99tI^SiCpdp7t&&CsvroWc9%!Ig-!{VLAYZ|{w9Aj@Ut&F{joeA|;aNA%4WJa_-x0dIa^j{az|^3`kOx@Xqoy*Q$T@>cCSn7<0W#eQ;?<I39!{TLrQ)ztCU|4(N99fSE@+cUj@^0D7N`()PV)E?3tyz$-K7u^=T@txhfwvQM08~R<|e|{={KVf{|cX;#rzRQ{yQXc1=fE9l|{Ec%3?m{u(jdKWg%?PXqjq?ni#$}W@&qetArPFh`<~a&q$%4w8=Pqok!%{paq31gMt2Q8xaX!QvyA!-|p2V)OM|t!7iGRZZ#5d2Y^nVL~<J^m#si>ZdG0)Zb2M$o)JfGt$HduM{Jdc0ax8RL)K@M-83$kBC!{0ckWNlo9>l){jJc+Kr-#G7Nc^`l`&PTZqJwqJhJe9waOV{J(xh((Z#js8{&T;u`SB1ZE?#mj~dU;4c<T){au}JtE=gQox2jP62aSqLMY9!(q=h+<IJkREyG!Op9xj1`w40z*wox_{w>pTa325+3xa}T|YavJCT>=n1*Z=4VGr+t9yKDdbSd0Gj5FY`Wo4&FFtXs>$(-Z+=&Z~G6fYn)@WDkso$pys(pt4<-D4>it7`cgN7zj3b8HM}`^;~b_hLr45BVH4(ex3vl9#%Ih>-WTTt?yF5_%sU4*B93t`)YE?pc;j5CEAo0se7nH|9fw_&A0fVR?$m3=)pq#Lxz-+u&_2dFSbJG1@Z+{(-B_X&-doFjhB!aCaNSk;@ZR*K8vKoOx$dzI;cuMp^*`DS-Z&5Jjy!@m#`$62>vK5oX`DB9b@~JT=K170Z{Tm7XZ8$AhjS~&`Dfq#OyG_4(sui5%A4n_?U=^!H_l^wC+t+-JnwB+-UI)A`%wN#o3)>Kdz@Q|=Q#A-xU2BPmBH=qoHO?=i>Lj<JeO`AO@{MI#<_QgH_yF$R}4oS<6ONb#|FeP&f!~OJK=Ah+n@at;v47utwk5$Z~QL6lkAG}=I;nxdrIqi#QZ&iuU=KGcZ}aPc)#ib-uQilont2A7{9ad_t}AcapQLxcI&&~&EIkS@(A&b-+lPTK7qgSI}!J}FzmY+zbmodB?52!4#mGa8+hY)E1twfz#G4Fv6g&_b74K6V_jGA0M7S*RUf?Zdl_G3JMhNuYkYNP<2;D*I~`xcHQ<fk^?1(RL3xbd0eL_D4Cfm5UPF1(C)V-VS~LmeGJeP88ax;N#_yi|?(gAm{!VIVW9+XRzuWTpTY)dQ4g0zY-r_kg+(UWas2}k=<r7aaUtGTgfAe=_^RM9hNx4SYM_S(o^_B7^c;okI-ppBXf5z|K+;zWD-j46XzT(&%==VQH;&&uJa6dWOWvu_#3`ZQ}_jjJ}Paux@`@U9xf`3^J`=2eAVc#-yJj@%$?+RTJEwHbXiu;*elVjhb^a=3B?<+km+}J;xUmW{g{I29F|1*B48~ppzx*`9{z_4+zx4Mf5vIZoP6=Ah&9rRBO2q}M#{@?$^K*!?$zy67VqD6}o|9|^81`;<4v#cfo$wys)xB%^v0cjYJM&$F*cChF>*1vh~6W_JK-=!^le&!MW9&HDU-blTYcqQ%VpjgpN>l2V+)M9rF$|HCeZSi@<YiuO{iue`n?<u?J|2`n^$nB=>V9|rA#dlJWJ&E~V(Jm1N+leQ(q_qm@ufkxL3WM!n(eLS7g#O~&f@v+tJLzKQC(cj*?g8C{Y2CtLw;<P;xCL>3mZclH!2uacyFcx2<hm1gVVZ-x@gBM{mf+=K@(zQ1%V-a!*euI3+DjRGDEXnhuJAkPCwLoe2aEoW+Dq)E-Jg0e@g=7JL41X_lV>q;41Ho~FQ)G{+9|^=>pHol;jjf?XW6b$ZwvAforL-lvB)J}>oeN5!-3u5|N5jLpMtjdOL|h;Rapk%2GADVgSMNJl6iX29zt>Rngf_7+zi?d7QKKXcnoC-%Ql2DYSTy3##7fOp3j&wh-c7uTtJ4C^U|JAZa@$(dId%Ba>{(hS<1X#VlRCqPF=<tM=V?u;&H@TXp7E3T$eZ{an+zYu1h`x^V|yqzQ;Zy+=DRKBD>iy1n;ALo%Rmqxkv5+eZ<}ykQKD=)80p)`^5X`6HOe==WRFb<>bU?81XRjqK5~hC)0<M6Zx9Y<JYu%Qrkh#_pl%zNpBcrH)K4CJA!xw{YH>qNi2FEaWDGxqTP=ocqC;6{Z}&19^yUZ_pq++Gkq^Pk-Gu8OudIbPM*z_JwZN_o-zDiTd;`mnF2Z$(=rl^u1+oK%>q)7cC(<gdc>kfQa2+W#54zso<%J_6No3UzdLD*DI>{GU>|pIGuk~FcNTGV+7$y*nOsNOJ;_xM;zjqR2%b#o$(WO==h9~~aYg1A?hD!u7X1}P@Mub3=FJ?CkC^@u^EkL7?E);Ta~}m*?l)m*8?h76cChHg)T!w2*o7$t7&9^LkEkmWXJUWILY#$l-Hf;iaTC`6WtQg+`_}{J-OXo9#sp{FPZJK@FdSoPL)vMWE^|T}>TARzf^UYwU+gcb(-EhmeUpAS0+Ko$TI?;<JBicLH#K8#XZm*fIKE;pB3{J2!Y!dKdLXgrLBxxQhY-(a-ubkLP{ijO>Vd?4ndV^8t*M(4H>2I0x-0QOVuusEGjV77h;B*Tl6EWVF2wzbg&RP-Gvf^)?oYg!GJxqV8KZd6HHuT-1lDwaS<qs?r!GZYlzxA4ZCQ$TQO0s&iv1y_DE*y!5$+?_lY>P+v!EYXzz=9k-e!y|_G_jewt$N<Z!yMt#`Jyk*++YQP+Y-(Gr#!kpdLm1H*JwQ<mb>H9~5^y)0zaNML?F&cJL0`A|2^BCn(=|@=m(g&54`SU%0-sMRz3@U7uK_F8u{pqFtX@xO$fCfx@m&yArvQ#FdE45R0zNSe1x{D@I(IxB`7DvkaBVl?$>zqf{m@>1ByUe@tACI3NAR{)9R|aemtQ=v#zXbS`4i5ybhaGg1qmo;W@E^yHHfCnKN6l7GSvX*p>}P=rsyYvl~$lQ6$<X_==0v2YD&3ocFD!8v&!MTjMKHKr9IZa}+yKx&iwly)_8?SuGg%qv_Q+HDx88uNY1b|_0M{*4&RxlSX-s7PF%xG8OsujwOP2XdlE6OX1(Bl=8adIw@jA4=SmcpGiedx%A5(tjpxAN3yMJ<M~J_$v7q0m%>sdmHVmlmr1jJPhdx!v5v|VBSAyi;v_hNna6nKxz_~q@93vT8iLYlnnF_r=O&!pe;B(v2gK-(-Vu%NS&8hbRFVw`u%P};*tM@W&b_segxlVJ!~T`$@>$Z?^w^@(f*xv?jyf}`FauG53;wh4ZF~;P8>};nt6IrhO*tO)2>756~v2Oin=LrDfY$k#7$`zr!9OjV&MuC7bC7tyCiX8;==SP#(ZU|%M*V=|B}SrXm{g%3U0`>lEmF;_aPQ;7;V9=XggSRJ&IsAr6FSuqu*dkEBa1ins7a+>+zb=LG5s#Z6M>8jA?O*MJFQ{m$v9I;yA<>vHXQIkJ#}jamdSGf*>45TVf`pEs}_QBHD?m;}a(&c6^0P8I(tG3fc}9oryYCK(Y}hrtPF<rlh1#QeIEWDC2i>a%pHMC6|y`<|FABGJZO9mCPeD-xXt;%!!{dy$st>(z>#J>a)G-k=sPOEA=L}rL5E5({|Qvo5<}Z-b5_^tLe9icoSp(MSDGEHTk}@yHblS>yZ|`2PywPrU@_WCRy{y+UEh|N?I|l+a$d;*J;8n;o5W{wb-(LkD)Et*&`EtjkaLty&`qcyNYnK$JU?u<^4wX^yD2!_8?`ypdqp7{1n-<mHkZF)0O8zo)6grzE4|x^U${d$974Ry@N)K^-CDuwd6f35#QhBeJvx$<f;MrH6Wt`GFry!K-xue^1dmy;EVJT{1tggpAwKZd=DK>`zvyJiQCh5eA_ck<UC`GoaZ%u3&>d7Il^I|rwBhLAo;?PcAofr*uU|{FwPkImmw}gUh?H*IocEF<#o<7&sgGd#ATVkEbVfXvGf^7|6KuTN_#wUxgeii<U29V!J>Opi_a=z(F=ppCQ!zcm-K_g3yC+;N9>8z!fgn$7f=?GUqHQ@`cM!)Lfc0y+yUAf82bRRT>mibO|%b?J4!72M`F=G5Fa4+QGVd{L?0&>{TJ~O;wKcrxx%5dh69VPPuzld67Bjy+z9fbXA@5%UPuwVjCv8V=y}AVmk=+ZJ&k%IvFJv`IRny)_6M{ZQCiWb75R3=?a03h126f`1@Ox-aKDGaenl>4_`mom?Q_Hq=MPBwaOkJ(f2WDh(S91lxmYIAPnp-T+ff7yf0{842E{$dYo2A^v$S`yZ=B<O93(zWImh&Ayv7{Xv)IwpbBLWbh-Mp0TY7@}f#4_XFOR|?g0oX{(dP*J)+0UxM}qJpJ|h$P{0Q#NXHU33v>hzEBSrAHl!?q+nrY>Ua|Zc;OJ2Ay$cc_5j^s52e;JTA<m%IoB-fibl34Oor(YyvRwou+mudBhCDv!ePI_(fqCY3jMnCbnZozg1<TkNzF8WmuvUAd}I`KLSc_h7)1$$XQz9H^JdtH!^*o&#J6E7yd5s*mQjfp!2*`jAr1V5&}L41R8q--~+A2Y2q+vqWQvF9@FAI20sm$u;YVgK53!=Qx|yq3NW7JZ26Rp=v<jC@@3)yTyq7H$%;=*dAoqCcRX5|A29pF*x0xeus?uSZ;uyl_)#=cfLIX$~jp(`nZu_7HpMFH#{OIRX+z{0Z}mei^vO2;v;n5#&A0Bi!tOw4*(fb`(YUioE_zavs{wHKXWLfjS3uLE_2*DNL>d?TVDb^lQg7$EO|3F_-piYO&`qhS-%Tg4<I%&_`r#KsFMuqurMFEc(wOH;Z^9ud^;F-<p7&pkBxFtR+54eTw)L?Gw~<>3@f5!r!8OA}H>9@?!r<eTMi9?e)Z>FEH**+G}X9r);IqdbZbA`c4l@|DHZu$$w9gKKgSQ`r(uyUbxrHBlbhe_vEKDkK-$Oj}afEk8?j4h~EYzZ8-Fw<o_WS{yFRAPx8-+<1+0Z;(zF$EFkg2!F@<OF1aw`Fy<AUpMDM&ot8fDdA<0=!db-e0{TT5u*1a(2Oo#FlkacF`J4VPi0_cULtFUUv>hz^aX{V?Ck%)EB8ZdgC!`b%NH%J*i&7^ie#aQucrWpo9*;hbuh<d95zOnvtrn1Q+IfhjOxegu`sYl`M(o^!V~bBe>Mq10Lj&?HxuN9R2IL#sU1$#_H;{NJ@hD=^(-~_hv2bI9@Icxk{R3hLWH7PA3pbT{#GXkROMW2pjHT|w`~!&{u0ue+4oFvG;d)aKB<@VR4}JTS>q<^^Q|9kXEL>ya&cx+tmkmg1;&QZ`QiQKVT!%45R|>+VX^WH$NR@yzr(K1*R6staZ>b>PO5{5bHzyVyMO}sXYo<j}gs(|HiuDjhu0fF9i4qmWi`|R50kO?A2lryz^`cK}V$t1$(uPrbkuSyjbnaK`vq+F#h*Fw-S=PJY8f=@+#N}ug56CCv%FwPsu3Qi=x>i6Ui96G-L9PV-g!`1XgGHAQNK4{wv}*-%k>pD-kE9o)?O@SGgJQJ}vMW%^2k~N8qi#za!I;H}i_y0wuiutho`-?NooPF1-%z^ICz3whSbt@Bjoh>yT!Pmu$NDYKGD%z+SFVO(ER%8TSr}}=KM@NzBOv?3z)hq56S=Fz!fhnCpIFjrF-`I{AQtXp+Jdvv7JSVD7VcI6CndMtf_;tL$K-dCm-G>|1rG|yG;*D3k07^`*h5~@dlC!RownewXgj>kv?0X8jifDj0Br}0Zb#|Pc;Y*T`9~59_bu^A;@PxC#?oK#blQ?WmE2VFf>#7&7450Cr<02z7MUNADa0|f$I=%5NI;G=Z58bpitxV?9}CD9>KO9#iMJ4MVNB6K2joX;vCjtOKO5w?l(L2XKQjG1^PVNQlzI`hq+blO4^n<4|1=<PiO<u%ND)4M82rWFNqvR*3T^Qb-$Y@+qEix!&P*JiI87Mx#%I5dPfl<e`eY}UoxJEz+1CYEqV1$5rDUg%#3)3&5d9ron0993LX6dxc|T=(Tb4gHeY4O%Gr26pnP{gXmzrEE;>6TRh?CGxL`lu-2p@+&acE2W!@xa0vcOri1q=6Q5FdyBqQe+R(!<DI4&V#SbIF4JCu3hC7P%Ra=gjvf@t@3llOp&W@j3bkcP7Xd?WYJnLH$b*7XQ8E&Jl|&56C>?1GG=j-b(+y<hByeW4r@F`A!C8b3jfLA7D986Q7}dfFi!LdA$R~!mS9xCuyH#oD0O4gX;BU5Py{ZM`>RoK0^Ko?Mu7|8Sh3C&!)YG_6*+dJaRLLN3zVbjkIypBZ<9CbFk>i6v6!{g4<CK2*M+2|HS-~?+4m~7h2e3_#w#tf!q_~C-fKGpFWd$-PXjdndab@wEGiFo}vM%O1mcQmgJ&{TM`eaPs^Zq!x?8deGU;HB42_rYZBLF-rVGc`;fW{u`9?H{UxOY^SYS71a(%%auExcIw0w2XP}*xTo&T2#ChnGH7G_N#>_*Xg2V;M3zwa?=)A-QiE9woV7*kO9mV_w$w~TL@`4-F&Py!Z2P}UE;tVWj4%!YD{Sn2*y8N7WGvY!)J|D7<o6)XC`G|ZW#&z;bnuodyv4>dJA)V<b+z4Xf76ha>x$U$^kZVSKjl87)N-UhL+tP7uCi++FUwn$bBBz)~ezP@@cET{&rzpZt2uSiUq@5x@6%=m*<4mA`TjI9l>(&elkBIaC^}jg%_fO7hTOt3$Q!{7i&z6F7whP3H{Si~$n(^ctzZD+%PYw)Sm7Qqo{{Vtj2)Y'

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
