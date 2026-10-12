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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_000.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_000.stl', 'source_sha256': '6ec519b4736f22f84d7076e90ebd80742009824c8973deaf4d54d89d89095579', 'input_faces': 752, 'input_vertices': 523, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2828182876110077, -0.5, -0.283674418926239], [0.2845400273799896, -0.26327258348464966, 0.2836438715457916]]}
GEOMETRY_BASE85 = 'c$}r23Ajzw|Nr+zh)S6ns7~Wmq>xGjr;r9yeG^d}Q!*rx+kl)3At6)}b+{^Hri%=9H{!bYnw3iA2x%57>09}o&swj~w$Hl#pXdMletJI7`*q(w)?Rz<wbx#I?R9H;ckvPxJ^SY(Z_~4-?;T#t^CV95DtcL6`##aVbJu<~d-r)d!#mUX@<(-i^H$ATK9J#Mc>^-LbnVx<Z|04W%$py+A+ts#^Wn$(KGC;h?+%ak?b22J+dKB^*EQw$d!%EZuBo4^)vaBpMx@RaH6nu||I0sRQdLMUICooaN)vUr?J;_KRxzVP2W%Df@uNF8EDZZ`{MgQdg$+a}AKqg8xlipfc?-sFuP^6V|DiNL`M|^lxgkHM{_hhPNI8k}vCSrb+k>B&yaC-zIf38*3-j-iZ?`gjY)Y%mY4vPcZFO$Qj|YC{YAHWCy4faEKgy5Y+jM?z$PbSDbJO{0`5ZUl=HvT6k$-iojV6!t^2eO;b3=X<-}~x>FZt2Qj})4`6DLePy&s<Y$+TO0>nGlAW83Ep+n$LkZLRM|jUVm$l*y00SR<{RSo;-|b3=YY{r<}*o9orGT4A^yqQ?j1=7#*3`mYYm4d?ruZ`{qt_sEa_UDf7O&-jK}ratP&@gsX@+WH*cTVVcv`eQpxIa9iu^NQ|zC(Vxyu4&70{OH)LOgYIWPZgxKXSu<1aznnhLwwS+bHe$NE$!`ff2fN&ZgR(ywjA2u&mLsU!H?s|ciVCzdEE=r&UavMldry>uV1pa&2L;k?YNPTSHGG2FTTHh)ti#<ulg<DoImFquX$v4ZpaVXZRz3Jk{{0+Yy2er-`_UZ{H%TqKe=sAzNybG){kmC^c!Z%S3juFpF>Ug(c&%h!|j~-yWHa3kRQiSt}eIO)c>X1^3&R9OmUO1zP3;7zTzf7nzMa<_<SSXX5{3C{D_`!^%*%P|GvKK!}X6%YHjoJJw31XtxbL+^XEKseD241-7+RmeZ5bUFO*p?`QE_~^1|oq-!*haZphd3jhs1jg=x<*<m>(W+w&%0eeFNVaW9zs_+zv4!tLV~WSM;RgZpJnmdTHO-Y_rRKGDQK%X34%wokmvKg-Se&ii&<xP79>CYXHnwSD~M6HI=*e&#ycZ|pdbXxh;HtbSC-&q)o}rRD2*=;q@`HUG+GYt8v<|GCOH<D~l9p7Aq%J5H{gvo_p5(fvzJzWTxawQi}&PxNkPecHiq-P`1=AM~Fad)xBI{P}TO|G%K7EgwJVKVD6nfA#}w(&}Hkzxi2xt$(ai|23xn-`-|TxIZNBd&2&Vul>Qxe!}F(Ry1D|K3{)F5A(D7dcM(RJxspWzP9z9=cb>3e08`TVh1YOa`CktVtJKJImtTn?DLcJO|&R9KdZ0p5U*8eo~MbGBUXox8}IW^cJ9CU(MSKxHtqIl4_jWDM|YY$zn>lF@%;~NzTeu8!}0p389%D?ljDzXHpfkVxytshy>^^mRMkB1V>jim3YQ;mT_Zc}`|2mFoB9Mk$Bnmf^3~sC^Zn=cnSP<;M&g#o&2wG-h(6y(J-*SLZ~5tdxS#lqKQ;YN{h*&$`*f`-fBl<&__`-PTW|Y4elQL!UvKgwldZ4M@#ODK7v+Y0eU3-QHCtrrbMw7^xIaWkcDMDx_q0Fs>Tc_^td{?;{YrgzK31%}AMQWi?8>Hm^^=>epBz=$mOp;CnMZhK?RAL^dC|->)z|Cg-TC6eaDI~Ol5p}9dcE$j`N^~I%uTERjD3mRfAgpBNrdxtz881%bsWpK`H|fXZ9R3IY~RStZ`9XuGBT%8VOqY9lWxAwqcs2QQY*vPH*u)BnSZLU^^d*OVt!h_UKckXKSF-8LNoguOQF3^pPJ`~`r1Fe1E1uX@^{{4{G^UoQ$DfJ8~m7#Z<Dv%{PFc|zK&xf^K3qTO#6A(dXt|#Qej2-d?V$W+JBF){W&?Ssd)~1-PbJ-_vhr%4yJtdwLg11I+*ffxeqQ6_s?iy3Huzy*Z%3vEn)H#9sav4+&^Ql)v?b_eC?lpyE@Cm`Px5|PQLcfDEX1!cPvS}zU9j;%?<f_zOnbqEltbU>+9z0^(8;P?z5b<>w7^jJKw?&<}De$%sepKrZ6Xby^`;?xAQ{$;ChW{Z}MYT_sL0X|ILT&ybWL5-(PUZ%%c*WF3btHzt?B9op<4D`}_BdHu=dfDlQ7QPjr@j?yDb+Z-4OI|7e045A=BvJ8i^P@%<C6>^QOYfPEia*4(_uCY!cc7{0#I17-ZMA6(zOGNyd>_4>x0{9ybc->V-p@4NcENH*$e?{ECzdC{xq7L&id^8E1m`gIzZ`&Rv+|JS-@Wm>+D8`nDd`rb;uU$>%tf7Sjrxx0Cf4SXG!96y-9ecyeP=_gaqm=o?-k<JtB`xt&O|8G2@z+9J}r`z`@9Uu0Ox9?;4I&MVj*!;*D|I7~e!^GD^?Rycv_Cs&&P@A9o-0W~ajO{+l=Hmy?wcN8zezbVy+2MZZx0z%6IllJ8_>K1c$h&^DnHT6d?-#sd=R^2<UE=4wYvx6f8Fv{!p4r--*99AFeegZ}WT(xxKHsjG7Vd}1`wy7;hx!TnVYJ?XRcZMj(f?aJ`Se4Ne80tF>rZQM%b`B%d-y)}iM%)0=3mWutv+hs1MxllM9E|J{qaB-n}2yn+s?mqu;+{K;U})`Y|DS-0pt5?I(=^b{_*#1K7JHGzIcJj_aE(-2;UdUI?vhXD1OlXwFl>h^Yu9!xz@?o{!G3%udFS9_anByJ(e*2UwschmXp0HoF9GrAv-?rZM-p@pLh%ZvODcOu+O%)O}&?Qv-8iIyX<-peiYy9w<j&%uhPlR(+<{5%a7nEs@FF8{>DYd_p-a1c8lEcA3HC_k599HV$}UMf5TN~9VI?~h<&bgSz`0?J^W~=Y@7eqF0(%2?_Fxj@yFM*`S?+MZ`|c3Klc1i<9mz`@o9J1bt3%Wxij<*GtY@0%6~I_zsJw1XY$q8`#o0TMw6fH^O7y6+IRN3)BU>*xgp=fk9XU#!IYn9X7hDE@W(1UUg7Kb5ZSld^tagly_3xG^f}eBt;ttk$A`piZSDR0YUPRM@0(P&*YTly%=?J?{_Xhf>f861>`z}e<(xLv_VZO=+jU0#sQS5^O@H&pk1~EFufk_Ww@kI;Gk$!X_5F>bO@1QhsS)OQM@N2P{N<OK`luf}V*SJi<!yb2Wg0&|Zkjo6EPJP|55A}V)I3|CHamu!a%U|4%-%;UZGG?~_}(=$?ftT0(=b#1ns(;6k=^y}^9tWzjsIX>^Bj!reA)V6j<@|bcD`LN#*gC1_f#<X@i{jeKk;L}ZJ+DQ+xa`bhwm*ZZSwu|$~QIV?cDF`yZ5{L?)|I2d;bRIxc4J|k^2$fz2DU@a=+_wo$)6)FK7IT_pNK|a~<n}A7q+!fAxd+>l-q+h4XdZ63ITXC7iGGmRP}wE#Z89z9)MQDGcZ9^F7}4g~GIaorgpQZVu<`b2ie8^$z^ty<mMaKdpRyE>~*qH~1Gn*0b4~wBzbL$33n-7u@o79_5s;^P))af%ZO{_=;_3#=XQ++YajMxEGx?q%fSX<DPeYR$9J}d+~F#((-kl;QumgbvR$=3EuW$tHb#^?nO@jry!gkydNF<yC9q&tp6~t3+l<Z7t?v2mcu;6JM7d)*K@Yn`uN9(j4<`t*1?WH`=j<c;Ct$KzTWn$AJ!T_`TgtmK6>Or+Yj-h>L09R@{_wtjx_r8MsvR>>Q}VyN%&Fx_=ja|{sj$2nd254W5>z-D@=b-Kb~RzWL{-+eWN21#!pOr*FNu->@nkp`W}8XXM-I#p4n@BzurnaJ~vur#~J(xzSr=5lb@`3=Nsm@UF+EEIJm8?4}P+X^^*genELo7M;bp;eWo1`_x)hY$B$o$zxQ)fe!TK_<3|rvF~?0Fo@Kvd;V1UvA9~&7$8x4k4)=%PIf!56IoRinDdGMWJZJIU=WMdaBQ}5W%l5oR_+}haKbd2FZ}?n0FUlP`C49dG^8|c%o)EqF%_-sgQRgA*yYmo#;xgkWhOV;DyAK=LaTPy;pIA}Lj>GH9yk(BN;fS4YjQ`clL)7;Rtsi-1ubGE<O+Pa0M(%S#efPN#owCucOS$t#{37#4{37#4eD^t$Z1AJ;-RGeC?sHIm_qh|4<2-l#uUbqszB_NnFEVe(FEVe}e0Sb{yq;Z`b>1V?ci$tD{TmzKeNR!}eNXXj7;W>N_aOD%_aHy{s?B%bv+&*btYnMH)_30f)OX+ef_&$_FUWV^`y%zKPdEL_eGkPi@*etL597P<x$3*`xzV1#o9}@|-lOr|_vlDwC-eQY$a^}z`<@=j`f5)2eh=0G@ZEKQ=&6V1gzxuYT>{@-mxxuizPm1=evx&FvP12<sk43(_|E!?`tJHke8!9O!}o=*^QiBx^91?MI!}=Atn<VwY&H8S+;u1Q-F2sAJa=KZ9|r4S_(j&i@QbX2;k)Z#{_n-i_XnMS#z&2?`%CcM^}58op^L)pqw9X^yX$_@*T&?8`=PEYs_(8VMmr~S!u?R!E!B6|EhD3DS{&|&x-P1Ik#*5On=B6ZLtS@O-(7c&7dBZMK3`o2R^MF*4)UFK;2_^w2TqLdxjcM*gLQ2DBJ0@rMb@$L-F58f(GAPP?XT<V>bvXe{^aXcq_scm_UgOq_L22NR)pI}zYC~e<hwxL`zylNOTRm)?|yfP&s$;ho$ngzyWceuO+H+ac76G7qQ3jx#B0%iW!m-SyNvqocbp*K`HmChJKu3)3v=xA)A<e+_|Eqx_1*7HUdyGq;ri(JvLZg;%hY$jmj(IG_p;=^%l&Xa)bD-jyWjiNcfa?k?|$!#RK3d&_e1^usJ{FCF@9+eKkdBuz8Uz=_f7Bqk$$+}>i1Li-S4M~ueaOta=z!P?|#qqOMc>q`-y(fRp0%d8>z9&o|p4|S$+5Wa^lA-c0JhneyzUy{W{hv!|t1Nzo+9D`JS%6`#s(D`JNtc+tB#Iy2SCm_I(`R{q7$<G%c+@!Tte!cmF^%bM@-*_0|0euCMzOlFbgT4)>p6{{z0e|H0o^YfZR61p6!S-Tf7b^>)98+ux#}4qFrMC%WH5eRsb{e8E_o@9Za0-`!6VsrAa5a6i%gD(buYRiZO%oBmQ{KMcORA0{z;=-O~Q1p969i|n`Av43s&e1rWw`0jq5c%#E>)9SDLh472)7n<3@>@#xrF9p7{Pf7hE`;_t{dEs`@eN*bY`=(+?2H5Y+?!GL1cVAX~-2S|9I|Tc_@ZEi1k=cjx!q+|6SBCHIEAzd>Hs9H|roOvxEk5pYGv9Id#i{S^i;MQ2wLaWF!M;0uci&xfQ`!7*`vm*?@ZEiV@pqod54Vr*8&to@zQOZ{=ZDWX*q4a!?n{icUZ0=V&voA;zPs-+w%7XZzDo7oeU-^CuPO+iukPDa-`%$v?T}RvKCbQyb$#6z8rwUyAgz7acdEX-?=*4i{DN@*(S5DzyZc(bPUJiLY1Mc4)2i?8r;VTZD(!rAAFu1{KHf;#^9s}2NB09q?k`L`U)@)X@9ry(u87%nQ)i#E`tE*a_1*o<-qbFI;dapd)#?}7UtM>c^__j%-ZO7o-`UsgElH%6ulv9glU_E@VRt{d`tE-6*zuv8!sn~|+XLU($F9D+k3CX)v|V3x_SLKJ?yHXunrMCZxu(9mPpse5c750Ry#V#y-wW`!p1w7lufJcAsPOvMw0i3ADc~3RJ%xjH&G(J8-*;%4_FEk9{PpEC{w1j*Q*o+S(R;XK=vO$zls~Hf{wo~aul@h}6^`rc*8ac#3dev{9U7(LX+romLbx(|4lH^)Tp2D)2$w`l!J?<ZCE+rJa3%C?ShOKr3BHvOehPgC7M%@01<y)FiDI5tJQXK0tp1Z>Swi?X^jG*dxB$(EMaRPh@C39IJOS>Eo&tA<%b-%PGU#mhv{aOqvOTNoJ<Fo+!3FS4^c8p}JRThckB0}N{o%pzlZ5c2XfIgw3HVVs%d_=tLS0M4jnPNo#_+@Fv+%?4Ky(~D5FU%Z0gr`WCxjE|R5$^@hE9ZEgU6t+z+>P6=pb0M8$1B+irx-)g&PsVrO>jlXufB;6rAT-odM^;?-Ige(Q&Zov+!7WAesedab1L^O}t{Z4Ma=8CFuK8i4(NP3Htg(;y2pk6?hO@02k1|2N4r!n+f#qZbWC=<94_#S_Uo)=hN?J(>D3s3p3DX;2H2Zv?1J(F=8BXHf?h@<H)nbX|z)o{3u!~)VE7<A4t1NJN`}|8wdXm7oyL?&(gmO3E@`>;Vx(sxC?wbdK!E>Jcs*B?(;d^?=#^!@Bnl?JOFM)2%m!vh6i(g=MciDqorW!&-c^EMIR6K`Nz2@L|+WuBQJ74iM|`Uzux8k6V1suc|Qs#(B-h`;*68`vasIo!ei0*GER;O!UNIauxQ_mljDi-!)WV_ljD!Dj#0v;(Nkg354@A(oA7!<_&szAEczn+9{dU+JP7R$4}$xn55WE5Ug&>d(Kc`|_z9v7_rB;O@IZJhI?Ovch6ullPKHI7dMC#sVHuyK4@jRViI##z<?l<POX1?F$VkOJ&+2r~vS=rG9{fBZ+ybo&i=F|ufa{?p;Ck>yXmR)=_$)&BV)PVPv>bdfd?O*;61@&?3BQ1LhDG0jUx4Qm!X;=AX_xM33>JL}?hemFKZIw&I|$*w&~5Nv@F~Tteh-WO2}=l<DrQ5tB>Dp^A^bPqc3AWy_;2_#LU=Yh3Z4!3Ks&-c;9_VASXA0d_yqmtG1{#={1`kRodwT_zeab!U&9&2to{W{2$x2sT}l(eWzbS^8TeGRBz!7d43%~%#?Qk0XsgfQeeeQwHoO4tgZ6-X&^CPtVGotI^7vW!E&5t#_$~NB^g8%K_)4@Kd?kD;dJ23hTnsG^7lS>tgm>~!3943tdzES$F74Ut`!?5D;%&x;>G++{hu}_dUGxh03d*aCo&i@#m3eL|?m_<p-vjqTd&9lpIQl#shu=h}z;D8H(RuJ(cp<t7UI@=Y--qYGlhDcVBzQ3T96T8Ai9QPVgj=Hb!Y$$Q=s9qCc!g*6L(j5=aKf|gChhnU?YYvkEFqkYPKC4KG3d+i7`Pw$INT5Jh<1QG!tKzua634LwufVIU$hV07aom{f=9#C&;*>|+=XkV&bMtUY7@c_62ecS{bA9e@RRTeLU=kl4Ho?Xo(``dgx8{LV9`zRT6hZ~ybIk4i|&Va!QT?XN6<sC=wbK>e4G$Iiv9wN9)OR+-x0#Q(Jx`q&G2q`D<QlN{TLQq2Csux62kAKVo&NieVK|y=mJ>uHFyy`kq{n^4uM4<hKIvF2;uwCdtlKf@O|)|gzzosO|a<I@GWpHLO2t>1QtCP&V;KH!d1}nu;_Vk75IEYxEgvXEP4%G4X#ZH*GF%LMel&?!*>zFt<Za6(Qa@nxF;bz0v!sAz7CIo-yno@(1oz*E;t8H62g@-te%x&S+ovZ3BH;TZihYui#`RngR=<XVdzMBB>iz1A)JjagR|kK=*RF<cr_us5#0=L=Kk482!BBc??n&52e?1?62b=w;h)jN@L}%%p9$e_2;n5U9~RvSC*jWt;SJ~}Sac1%0bWH2FF`+mMW?|_;I|0j7to=wXn*(xxE~?h25k$A)`Z)@H3;F#gm6W)He3-tGZkl`*P^vy(Ffsc;r4{^)9911=m_{}_+>(P209%UT>;O4a|z)*bS*5p1<r#%A%wp|cfq3H!e7BZ62iyOBe3Xk_!#_OLii8#C@lIN{0ICKA-o6O4U2At_rRYL!t2p>u;@y7J?s<0GtqZo(UI^>cr+pW4Ehu-`VjmK+<_3Ti`Icf&w}g1<p|-Oj8!sb?PLsF2=9d7Cxl-`Ux#0341JXlevT0Cigts$F-CVKgqst>x1)E!ckm3joe;i(5Uz<{17E{4rY0eLAt785Jr5Qw4_AcGB!nxV=fa|wz!l&N2;r;Ht6|Zb;H%*43E{?Q6Ik>fxG~&}5blCL42uqdyTEZmcmnzwEV=-m0M8|azd*l)Wt<T`6a5mF5Uz;s@lK9W!a9x#?<Is6ql;kCiSS~05+OVi9S)23fJef;3E}(E`(V*K;rrpc3E>9lEwE@UxB*;;5U!49!lG5->hNWRa0IOai=Gch;L8c&8fZ0Gv^HD=zLpS<qV-|XyWl9?ln`!>wt_`_!mZ)Q2;rB|5wPeR@JsNUgzyqH2Nq4jOW>~w;j=TW%G^j;^lJEQ_$os90kj<~ngu@qKS2l&L5IPj+3*nfZFDKTKUJR{a&0rL*2=K_eTsic#gFI_SoBv|^k=wAhRwSO{T}{S`btW_LhHeDEIIb)=r{0J=(p%Mu>3pu_t&FWz*kV;>(N@U9Q%?CTdykc`GoL==w<MQu$+_V&z#?{oU`T#pO5|m|HAnTUz3VYrH`Zg;Ga@@G!;Lj;yd&ZA$%A;3V+AnMKY|OmtpyaR9u;g-JaEho@F`KXB=-Ie1H%>i0+1^o>H&tDDyhXy%Mg5UJlE#r4ARPRpCp~3(%^toUi=dQS<`%JkF;oKZ}1DtqNBq=P>>93a;lx@Fm0*87HsRW%P^7@T-&my?3%d?}w|?FMp<QeFOgt|44j8KmLY)EBq7fekpBL4Zak<n9w$hz?Z|K-*J6~_fg(YT$h6!;{f^tto=r>>33Y`TT}n`mQ?)iS^dMayaC;U{sC`+KSBS5MgM|7fw!e%6Z#MO7u+zzY6J8ySVH(F^iTLtj&~Dvl)4J9PVvVaXA``Q`b%Ax6T&|F3GBn`&~5NG$`NjsVe5J~+5o;Az7xF(z7uYN-U7FPTcNkY$5O{Qo{AeYto|345U!un+cK>F&ClWsZ$!7E|An{0+tK5&=rMRZyg3zx=x^vTIGSPgX7m_*j5-Rhq8@9|t?(LnE#)txY|&hJGrS#L3$Nwh3O7w1<1X6ZHn=`|2V5V%5pAAvvJIP4&nS8y+8l0qcSf;_#s6Rb3)ho>WPRC7`yaZx|1y2sQ21Z2OO+LDB5HZ}DYB2oE0+3C7E@Qrtit;r)A;|='

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
