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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_015.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_015.stl', 'source_sha256': 'a8e69474230bd9ad1bb09544d110e7927082cbc2d054e341fd0049d8673c912c', 'input_faces': 1120, 'input_vertices': 653, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06844137609004974, -0.14106354117393494, -0.2639009952545166], [0.13168390095233917, 0.058547407388687134, 0.2070743441581726]]}
GEOMETRY_BASE85 = 'c$}r31+Wx%)9&Zs5D4zJcyM<c+$A^!*+X!bg9jK~g9P`*-Q5Qb5a1995G*V~g9Qst_@?`L=4JM)_g3AymsD3j{hOYizm4qfoJ!pqQKKa>@GpaLZsqGUyGk2|SX?8C(YI}{h>qX4?VYDvj{#vu0_F10_0wuMtW~#Zn9<i5l&wwM-rx7iR>GI9RJ&r?a{02g>)tD(S9rHp-FvlZE4*@em)>n1-n&D1kG4+yO_9O{bNLEp&*dBJ`+xiw$7zDyYSiX~jyE@#*&;qTrp&&wj`vj<q}-a-bd`9cqkq5hF;zEdTyNJJ&5t(uknq6WV(TUL4IQyZyuW3mS;Fn4x7KR@v&(z6-pA;3g<EHi=>BHkUfb2z|LutG-)e_)t9J$E_Uk4`wO-;$%I(aLx2gZ7rRG}+T7fU<tK3&<lja8=R!9As&$epb{eLt+5HBC{SH4tkoXo4-nE!IM<~Qn!{8<~cjve#7a^t7iJCy%)Li5czN0r+-KIpjl(zQVS96Oa;zBAf>|Be2r6KyH#UtfxGuG(0+adQ&*l?dhj<>$4Iooy`YziOs+jMRD1&d(Lmo{amozrk3Kw2pZx495*71pn~&VQtTt5179mFZyZyuO6J#@xO3hxs^CWNWZLW2auoOPCK3NDveKR{(5lxek+VyY##UZPUJ7S6VhMn<yi3ZeL~vrD>WSa^a<^+)ioFTyEOv5SXRFr&);#F9@iLN6a4e#kp8;d3N%8Uy#3Ig=EaboH<j|ho#Pm{B~j4+{kcNM$2Z{MO65lfZuQo;V~$X6uD%`8PODa}l^FkSA;-0|6<2O;${%uE(+*pqbqj6Xul(Py)=0n1MfU=le|IRxZOP5kns@)Ea(i?wtpAs7&nS;`Ou6~*edSin2byoyKY%)mwj;kuH_i9Y8H+j-*MdK)tNG@>uBfv-vCg|)w`mBsXMThH*;hmJOJ-3XD0yG&+qL}4jp^@nJdIo5Dfiv1hdT9tM89S|M1I#~$WOxc*5%ph5MHJM^5@i3?)w}I{p#`$+7qLP)(LF+Ymv66>aTiS^UM|H#`+1$jjxYjy`9_ri*7G71o?Yw>T%73?X-U2MMLHG59e_GDe&hRFE@K8!8o4|KdU}zN#tkEsdWNZ4rqO2Wo~fJqpxSnvmyL+a<sqlbsV>t5B0O)Iu^*@5aV`q+d@6g!Om#^?IT*>>OWDrT`d9HpX$YFFE>+|IBv6+%Kh_tqK<n$E^d$YldBDQ;h%AxjCwMJ8$)d6{!R6?{lTm;7KV&xjp`VOU2hj?drGyz`dJ!@aj5=CxizDha>MF{^>gjU0`L6VYwuv4cR9DfyWZS!@c(;wf%mw+4!>f4EB>h5{IE-TFu@ay=f$Bo?#3yoGpPmE+qzPylV<?(Pjtrkl*t>?o?x>}+Wuf<2DGQqKFs^#6d~MfKMU)m=!vslZq?3<@p*eexi35kc$Apn3vF$WIr80ntb<$Nc_J{6NgpdWJMX}CDNjkQ<1hBBawBzjjN7{-n6HyZlv~|1<2<U9O55pMY|ZzMk9D$u)(I5ojXKHeV%?s+jq~DYTeN3gIL57WcJw!PKGgs2+BR>0t$7(yr_g1rt95J9&RdV?dCzy_!UL^i&p4{wy*}7GzCr%AN%Oqtwg38)U%cFHkKHT_&ZDlwl$)bkVEy;WgZ$JV=4zgMovd0B$BjI%+<0<ko41{2_%Y-kJBjhhFd6eTa*cB9(G85lt6Y(~|EUPn8UF*;VXAWAN0Wg^tBmnqRt4)n&aFA>TclF%-x50#<90#0$#rON8FtpojXm)~+GFQB4qk2q)|<cUDXn*4mvU?VXslbi5#~Kx2j%vQoEXpT#q_v=UCnUZ?N8CKZcTpia=Ymx@MxX1zTKq&^0}U^TO*a5Wv0$n|1_@l%a`r}#_d#=+1_>N&oSgw2>&KE>YPoX?eQ=EbC%X2_orHl<2Kx*+$fFfiGTA{<j)(a+~Rt+ciqJJ)M-A;+n!*7)tYbKs*O5x8)JO_c**P4SKx2vp#HA*sQ>T9nOcw6RU_d-ZI4kgpxnJa_{^Oc|1#yl8}s@wXh|f__iQu0=bitj?Wb^_UYddV9EWl1TM_G_VQ1xL(u5fQ6&p|DJo-Fc>;H)RwOM>9=CRic<tCq_%mr&shHyRyTKP|d@7f3cyd<vA2TG&A8M-L9I!E8B$1(m=9^BG$x_AAXW<%ts{u*@-twEiqVdrpu-JPbqTOrhGx*v63oKkLA*n;^=cle~28%@^XI*{SHa$lTRKPk`A4CB-P1IFjTFW^toXnlLnOpJ51naZsJi!p9r-#;0`Pd>o)b4e_$+iZiB+k<gmGuJfId}B%u<!1Tb7`HP0m75vTq7JVo)|{wXCvfrARNc>g{;6GG^X<1+lv}IH<2rElH;hB-gWwHMV_h|xg!Zqj55Bf1@<**if4|GA+`iBj?Vq+B^Ef1dax;9aj)RpXnU242@jp|vZmhN#=bYWJe(oOx-<ccpvM!_M2l{VOZpGTB+?Vweu4CD9DYpa5F)uxA)VUTFb^gKU4&Q}2=x^I$lQI7@(4JfuBE8%=dIk5FU()Dt&9Uv2Tf1?6^C#VpIy-m$sC>d+tgGd*kbiZ7a&uT2%zMg{Xy@4E%8dzK(9SFgFkfeHO;mpQHjZ2MPqgRRaph*6^ms1qP!Q{Ik%@dhH~LS-#rny4aRTP~CC2SwE{yZl+RBaDDRA5rZ7?q%3nKqmie1`|c1bkf?@OuN$~gz)le+}!oc(D$#uv|%M%0{W&)vP_G%rmntk2IQF#fR?EBEDp6Ea`Eo^_Sm*UN$TEr{dpOr`uk*ORT^p<ljJW3~R3BUo2UEwsPL%Q0H#&qZ3t-}X7y?GO9Mc+b1QfOJ|vn6s#It5_u*w|aE&v#&;JoVkXMgKtYI%ww~0;7NKYH=1QuZrx2g$~(?MUv*qh(&rkf+e;<IytKY}LgNYvM~2iN{q;F7H=F;WpV!QK?=|0iK7K^V_;;*;`iXleHyaMd^LC8$njbv;*Kpl#oWSSV&ABjcwTCD-20p_&JR1||(bYuCt&$PoGjd~oKfM{|9cS~&bJTCUa#%=vN+(7Bx}M6-QC}m!Qf<u3;B%JtfA2i)Z?IR@b6)OV#{xAnBmeMR<;FsM?_vE_9qZ@bP~_LyuXXHH`7jRM_Yc*&T`DT~-)aaxKmHK)t!Cr6-BV&7Plx}YKHU?X7h!d=-rj8;sQpM-4(oq%V(`W*2WXx1M?=<s@ODY%{&{ybKhV5Bc-M3NHUIEmns5H=L!Iq&m0J_y?Dp32FUW}RFIG)O`(L$EZX_z(NBx@zA?wX(99y|n?GWa-(PFHtg%={QKKdySy!=_YQFdx?ZAa_un3wkplm~vvqTF}6z;29Vi*q5I<6t~$hWTx>r<b?ByFLTiQz|!pZj64J6_Nj;Ur+VXX6*8wcfL_^m0S0^V}2(cM4g0-duTf{uF>z)j5s&Yo<^OO2S3hG?rU{CguCPK+uj-V7ZygHC;Rbz*S*xZuGXF2U44c$nr}X>g!S<9+ioHK<#o~=ey^*>ygs|@-;6s5{M2alH($qdA$)B{d=8zE0_(Q;na;X>aRtryKgYWDp9t@a^Qh=P?O*!yA>21Bsd9hKeIeXPl@{Z3=yqtGwej&iWU@2h^<H<<aT+v4d7$-X@ayB12TyO;_86n<fq#9YgT`rVYQCN8F!<)V?X~@7UTD6#Y7ltIyvmJ-rIZIU4G7`x`ECtw4}R=OJFR>Drq(ytt_k7)=~tH>;D0=BtK(2*sDAHiHJ^p+<eQ|*txA)T|HlUKVQbo`f16G7?cdsBofMne8teP8@<5Rh;6G<k?u(gN>janm2LA1yaOH>Ig{+6bwc5&qaeE^F<<b!D>$wHzQLl;Mulo7bC*7z#c*n##$=kW5_OJ6&%-5ksp?pIb)bGC{gq!&*Yx~XLR)bfV-a^|~Vr0nm$G@^zGu{7uYpkCHTfz5+H`TmR>o70TN`gm@Z=(4%Z(!U~?gD?ZwXw#B$7mhjofDz_MT&jiaqx%TXry&{eGB&Khk2>eq=CjMF~5O2E5W}TR$uE}oT_yKlWvA^-?Bp(hqm)W`P7{u;}aOLrk?u4#qj-nyC!JQSLJKyeyf6eLe}T3VwIK8j*j)y{2J=qzg}L)b=Z$MPv1-m;r{OipkGDGqE4$C#k5Y<1Gp~jnj6C1{svDiL!Hml@@roE!h5{y*5&4w9=L8->#Elo|K#0SH2=4#SXXP?o%3?5Zzkm5pN9O;+mn}-I^8dV&+ClqYW$xv3O9H?v1SL(dAU8~62|R5*Gczk*@e6J1v5t-jQ`)?6)da!1w#7ka^IVxIIp`e4&iP)jmpQ-&N_)pXdU-DpKm?Z^W|=(h5Pd)$N2ER6G)x7yz<n|wf#oS4Iw<xuoKRs#0x{Xy?pbYkaasbO%)v<K0o`0Pe6O>pQ<W6ST;ZA%e@Y}y!ZvQC)!Z(oc*h7dulAi^>d2_9yM!C9f$TKwVig<Bk0$nVRdvI(oIlqj=CDcjSn4hKfQV%^EIwgJ+1$t(Vmd?(<e=R?Qe$&jQ^^GA>4YII^=$8HGZkw48N@HbnlN=-o*`dd=j6>{V~@)jKinejkUigFNVyc%MD&9-TCtGywFsSdtxTWdHEFdE9Z@t%Gu7~;^k;($y2SBe-jJm`?ifC+$bF-q+kB)S@d_BU}V94-t*MuW_VVt=gmh$^XtULb*A1Wets$20qc2K=>4T=j4nE!P3EAT9e%;{!{tl8yzACKxhTdndjH<q&XSk#JIK)Hc)t3(c7(QP@&x?OQm_!l^Weum%5R?6d^6vVcz#}Wp|5xReJ2_sf55Q*ntw12=H=)H<gd&)K##lYta7{mXyjiyqTKvp7<h-Z;8ETVSN`HUe#c4j`e*eGhK$gD?U)Q6Ew$#``Q|7$zN&=ww|k}eX6M%<HUINi<j1Uz{$|NF%G+P#LsGPJShvyIuMv@&Z}a-&Z#7Q2@%u>R|637!Q~WVne|}Mnv)KWB(uoOLKg$A)^XN6&9{<hS6E%NMEY!KO3jON42>h=)80XZdl^dHs{-|{h*T8rt{2BeKT5FQ>0@aY;;~nx_9h>~$#=-X?&J^#s`Bo>#b71D$%FW0(;2a0z*@CIc`8%4Or#6l|=IK=L`Z0#pMElc~{Ym+Rv>4~zop9W}Pn28Vr^GsG*<QJwx9K#kpC$qF8&5_1&%~Ur<6k#E*29M%aojdd!1;S(pwK!T_rogX*6sr#<Lq*Ge1e;99M?MA|3LnVZ6Q3+r`HV4FZ+-Fu5OQfiTuJbX6kW!zrr|Ndam5RF;ck|w=l+kRozgY>yg$8#7}_s{GMo*cRjfI!5cl48`1A?@#Y&bw<)($-a?(Dtu)`t`v&}74*VWnI5YB_l$fpc6HN=@R^f)Tz2{LNSxfYHwXNJ9kNGlN1deHY%!G3^pXW<p<3i=u#Nyy}&f&d-hrKaAVat`<vrb~%25dx~nrG&OoJXa4p}!02>-z=n@5}xkYf%5ML36$9A=qRX@|SK_ZciB$!UKs8g3o=c$MxNdj^nP5KTqpy^<!O)kAnLD6a~+|PxFJ%4}pJ}q1;}%Ou5lAg>obF73D^hT{tgh9#HO^U2(pSzZF1x-o{t%uQyP+`T7Ii*YHQ8Jp=bEH{!R!cy2ip!rgJRrVrKMseOsQUZC~)JGF1ZK;=OzwQ{rgER1vhJX$C4&uHWu1C;ysOvCTp-%nR=%pW#L>z^r!&yVFck{1|&b%yU-eCbYsbN$%qGGiP*+yPHu;PX1aZ!~`@yimEntbXpacwex)*Hvy0?uq`c9Cy^q%@~(4K7o>Gf6dOQ^ZPmdoMA4^h|imQ`-9gkitlL(RK#&-PYcQSA31>Ujbknb?=l46qg>vFe)ZV^p1v&RYi1EWu5Djh=p9dgyf}C-BJUmKpSYmo<Lim<UH`+)L?ylb^~e3J+$z$6@8jUT6r)MDMc(ybG>RI+of81hQykC0(mLS5`1(CWkoRTZuukA(kLY_B_O=VSKDQhNp5k>Ituv@JzP~;F6OLQC0@_n56W-5Bv3HSo9s05_4&}aw_#BxL-~R_br3`4DsH@Qa82gTTxnWJoto3uZ#5iQi6Y!3+&zA)6dsHhA&ht9(aR=%c)xbBc_)fepJ%5jw-U&QW_TeG(Ub827is>D-zoYix{uQ;qa;so*%;V2xQGd@6<iFo!dDnx{YZQ2oi0-;yuoAvk%svr(XgIF7uNLF|kQgh$8|)n9T@QA|wt)BiH6P7Ke(X!g@A9&@cOL!r^?>)hHkuZ|dC~7S>fBF&>(a0Lj$mDXwOH${O4HsuFZRGhi@oQ2aB5x5<M9&8P2MkjV{4%P;Bv^f<6>UE--!2l3ROjYzgf{ck9N_1;8uzT-gybMm;in;2F7{Ub+mKDBJj7T+j{3E_<S9Bll7gw<7`C!jCTG|0PE`S3K+NV|59$RkAijb=3EFjX3WJn-z@{)F2xe9`>7iEAJ6c9SK9Q-jk~utX*&k^l?OMQ%FSe3a9;fO2z*<2)Y*Rn*VT57Fg`c7fakuZb?m((@SakxI7_t-uVZ$jL3r=T&Z*p(7!TtUc&zU)8F`B<w;H8GJ4?^QxGkux++NlP`7a*geXxPy;HSo69p0LS{6HV@SNpU*X3p5?uXPaZ;eE}DjE;PN>}8r?dWYuw_#T}(uBLLM*LLLdy(zQ8aPY$)HQ#7Z6aDfnQ0`ve{BNrwzw&0(kMmmd{p)AreXTCXmU+)3-*<Bl<GhZwT-(`uIoe-ryK*a-58S=Z+}nXVt;;JnYV^T<Z_Nfgr`(&Q+)lm(^E={(=KBY3LY<n6F>W`5%FU%O!RJ4~Jns8|c}WzuLi?4V0mh-zC$y(@Z}3bl(f(vrL%7>tJ8lKEbK)s*K0nwW+lO$szkyk;Fu%zkDL10m()&j6ubOxc%36J;9{1S-jKi{NhrQg~w-EC(bsXyC?z|G`=>>g`2uAXAM#N&|H?4*1gSFwXms{ptjDME3n3u2@s55-Oes1uO2-o*T&HLq7DSz^Az4Ev(^mhpJWFzouy|AA9yf~!&F4{)9nJ*5;?Z6}DmVc#k>&z~UPwXTZ|KZzFr&Ub-JYjV&rN{M`K8$>>b7Ni%j6((AYVY~$+guj?x?E1V#dYp4UjX^F8Y?&67uL^V0lo)oR2!n)zS;)kJgFJxcjpAuZ}$%KHL{^{d-*xk`FupjArP$HSC7B7v%V*2B$$Npnb?1@?pJ7}a*OLBc<3h`2Y<8Kc(0K6DJ#yzLpU#&qfU-V`a7h#;S)cP?*?xc)ZYn>o#S!+PjVKVpD*mqJGD-r#Gl}IvW!;VeHgCi$v>ezZyupv#g`+$bi%co|Ez-EXZ_)Kah-ot8Qi^(ti7fA#>QIU37+6Sc(5++zZJSGH@U6?lg^`G9Y-MFN~8Bd|JK`R|F*TrzcCH#XY5DhXWFgYI+_#XcJ7}L?%oI8eg*zL2Y!69_Ahw$#TK0h<2UdmZ6|og)82U%Jh)T8-}T2Hhv&K*Pr*Mv9_JnB|8VnZCCzv1?1{Y&?MXhy+a4=z5%7hLwLSjP-M8vGizo}et?&r%INN#pfX_ZR*gKy7BQw`|=iQ$;2J-VS1OI)O9yfTUJD!UIo5A^f?vAq&{~-AEMf$t0fA4C{*U})keY;c0cs9Ea-ex1#L(3g_9(x)~*SBF*Zs{F2b47gcQaALvVEr-@b&{kF;qLSNe|X(d^}OS0t}X-qDvSQE=-;#r<6qhjKD&}W58Lrpp?<1C;3=|p@s5LKP9`6Vb<#E(+8OsHc-L=m9<-0M73;OhW{rPJqwoLvk}lBq=Y!2#D>tJJ!g_u%f1j5dNk6XB<0dMv`Q|?ZP^Z9YeSg{C{o%e4-fiGgZD0RJ2PF1wwZO-A#dWx8r+p#3)m5$U9}!>c+mYjO+&|tg*LL~`DG%hC1b#Z7wm(pNvvTY4bnse((4L%W^|<Dmd8ohPHm-X^o1&eu7ooq)`{BM;B@n``^HJ7&`)g-ejrvg*XnnJPq~_Zr*CD@OEA6j+q>vsraC;;2pYeV6cG1z!@>`M5zh4Nxe-g@XEzvr@`t1+kyxxO${&pVEA+>X0UW%VZ{)w?6{q;BcUAaB=3a*nknrps)`!%#@zp+@`lQi=|tuy&C`#VVg9>P9Z6#aVoH~5>3%e4N%=$dcbi=)>Y>+?H(585C0S&tj6_%*l@OY`kXmz3K}6M}avt;h9E&98L=;VG0GS<C8i%_*7C&h+WQlk`y@9D@1smCBAfPfLfi$5*8z@)yoSdp<=f_b(WO{5E6o-uKsYm0Q!7AV1+z<d;2(es$jpzCZQ`ZBNWWd$s<tU%`EM@qXg861MjD)-}|haZuNZeWsn}TmRk#FZWTof8TuNMzQxHb%JX$YaOdWG(9hk0WJ0YP2ZBT;Av}sU)`tNpS6H;dwc5;Zstv{+?>)IJbeyb&sM9hdo*4@7<}h9cwaR|Zq4^aoe#b)4CnjpR+=BUu`Z-epwU>=>3bAB-!y%1&KGwC>YV-)JW(>Nw_acE*6|tl7x>&uc>k_<XU+FVe*-==o4&^v>@-?=pv+g>v>%I};CW{D`&}BROrzY6OoRJ!tu$KSu9r`_@%%cTdwY%Csr8RFQEu7maX)Q1P<e1sN7Qkz1GQ!-5A>XYI>+naeZa=y82@v#!3U1QbL!fJJG8$wSAg&Dr1}0$716Id`%%B;*LcqRjK8OFxm69{-`Y>&XdQorL#T6ZfxiFcTR#-z8FpfuciaM1n=3aCo(*Y_wIr9;u}WMAA3jCjM++wDfc%JO;N6b@=$)_Nn55g4|8C>?b<PkxpIxl2-0qYN-&bdUsr&oJ_fT$@!1uJqslU<BHp4>l?I8&@_D}o;^{c<v@2`SJ1swO-P4EX9@jg_CoLILl-+&*Tug`D3OkL6b{qIBa?N*hs{;x#Sej96^Xuki4x>!F?vV%uV#`6is!59A_c>iPi-hn@O4A+5`VLJcLiPKT@H_lXUmrV)2s%8goegCKQ;Qq{-Z!SEI>rbj2;BVXGy^M<m(f&Mjz;~6!`ykzFpudyXgFoA$zdPBvKjXM@_OgC&{hi9k>r(LGb?`2wmHQi~MgHL1;1T=ADUaF=*VXIyz-z9??_CN1!S(RnGw>yaHQ&eUzc1Mb@CQeF>hXSli2G)|WV^6V-YNI(@S#1Y(tuCtJPzxrChAwt0q#$V-z(C_M*R#W!8^X!-#r57B5_}s_C5HM$I5+6KHxs`q8)gHZ^o;CeL%VKa2R;t!(5y{Z*iYpId+$K9ISQ|aUVST6L^-VbG>zZx8{SVtfrsW&4HW27cB+vc3JD#4GyC{pH_fZexkpV1kD9FZmP}TM>Fg9h&H*u=w9$G$M8M9JDxKSgdEqNFbMVQ9|Ny_Uh4<y;l3Z}5gAh7BKQAz<-fQ8@pbT$k@&vtT70bYJ2#a3@2%Cp^YXiYCs-pGa$L7x=9~M<?TGH0Z}RWvj1CX~Ykvb-o`)RQ=ic}Ge^wq?W@w#YD*T<DRXmwqzl{p`9?|eeIf(U^0i5r>*zVuEO)iA%{m?4-Jb8Wyeg|4t2KhM>>p1x0mPLOTmsf61!Fwh)|DMjiTQ4NvK7i+kz>pTo{YQ?6jE{e6d(?S7I%FJN?kk1gyWPLb3%u)x`UT(W_fml=c+LqX8jAd^DMH4<JT(gWKXk+U8}8p5)>wf1=c~7PkA;87=UW*-JL?Y&86R`c8t@VO@ID*=zRxas7~_^OGGrVAIq#!A?)xpQW3`E{_j&8nsF3yq55`h%rtG5a_wnyxjSGpula<Eb5AyF}?Yn8f`zF{E(*6aR_TYTDi}wfIzmsi{1IP7W4r#wRu#9rQ*#qwn@b72s4-JuD{R!HC0^jcikF~?|3%Q?vSL-hnf%d#>2hQIqe9iD&W1V@0_e1!1vW7Ju$IUbs?^E&bVf{syD)(`|O!x0$w_eicyFljNw&r!pit#<vQ=eOnmSdC~ZRTUXpW?a|{N^#<XULcX&y7oez<ndKm44o_`1i2>csBTX3(xKR`_n+QYv7ObDmUftVe5wc)%S{b7v~s-9qCwXBZ<*2-18^jy1_91<Ny1ge0MDLfAuHd`STaZ_y6}d-*E~?F^nRPm7>o_U5dH{O>{|`=z=uSx#@FJ=cdj<pN%>Pb!PgE)Z$Z7XQoa=AD=o6brPEB81x^*pkq)Q^zW#}M8~B6L@g#dA^q1;pv9-APDq`OCi)xttkmC77o{&mU6i^EeQD}4)D`I~P>ZiYU6HyDeM9Ox)QxGPThV_<-HO^z-<;Y{-I6A{DNS@ZeLL!KYB#?fYlv^-soBPJ+%{~N_-54N>w4N;m;Df5+0(De?6-K+GY%%lOnfoV7#8!4b1}|?`0So}$<BEbpWZW%={dLJ6MN=bbWHj<QNFAb(FT23lrQT_bPW1f)Z&vy`LZTOC!tRp<;xltorXS3lrQUCw0kay&Ox6u%9ry<bZ+`Q)Zz<LcXX_UW9@08o6t9)ZbDt3Cb~BLx76ZmQP-xfPG6O}I&~GA=yLSssmoF4r!P#MpE?75Ch82-Dd<yDi%&+Kf;tg>T<S#BvFW2z$EN-q1{3`+eKcw@(eWIMO8-6#J{om2))D=l`+o?7iH^eUajBzFC!kM8oq#$yeM;(->~nIOXdiuHY9Do8`tsCysmsz=r7lZdiM|$fCF*K4(KYG6rLIX`kG=u5_!iXls2kCDq;5prnkKpnO>{5%_SC(oyV2Tv^4ojrv}bMcO+3eH!nTO7Pc6Q-r=7Ju{i@A=i?8k(hw2;~@l`xyRfS_IzMN-l%W>?*=l9G-e$JKn44%2mz_}Hlf?9kc&%BFv*NNyT^s%FSSy!TE-HHFqHTaq9*j<zVhJ9J9qGer+iT;XS*0<<$j{eoLV~!niY`bFz96RaQQOC|WcFVE*j=gnkth3J;$HqBU+_3_Vb#^R_k2#JsqB)k?v8awsaKL!SCOVediIX`dk4}A@9R@l!o+f$<P4o=<k<{YHQO}^BOB20-eiF6#3DgUy=hH;bp&v~>hx#YSexx5tKbpE9w~6lQST`~^?nl;@T6`bsKI~^d`X4>K2m9KU+8vu7?6>&7)Z&LwkE9+)Ka6@D^(5Lb_EpSce}+-JEW)ut<Pl^R*=YI*_Hz*ZP|voZ+}^{}j|jH6FZB>w1dr2`x*IKm`^I+GM|{V=qL(-UwfMA-C1;%0lb4)Yd?LqUF&6zbW0%L~wiwj0sADlVI(ZCg@o{M}n3Is(gvF#5mYA{Vc#g#(OT{=bSxoA5<f+)dcw}iAr(=F>?h}tX4!6f9i%IRaN!pl{COQRuBI*>>X=tK-j%B1zOY?C|eauPDHf7}YOw{SvhfLJz4f%KkmY8uWvP{$o$z^*=>V#~6O6sK4!iGE75zDa=^b-F-Exw0mTVI+*-h(;a=?77Fr|wNZgt|9%fBIq6;zv^VryfWXJ(PYl^-$`;^rNT;Qx9O9`%;f$Jb?Mb$wpC+VEy6TK8$)K+c}(U5cLrDcR1Pi>~jbD-qanayVCck?$5q;rHPK9iS9>}e)b_7>S2S)`%w3!A3)ucTKeCKvFNsp`?Ae#J@eR>ygRoE`_s90+;i+Vn&`_k(bpXN%dw}__ZVNJ2@ldl-=%*^E&dtxUFzF3(Kl$19lJvInCuGm1II2h7JY}Y=)WC%MCQhK$R1LQ|C9Pp_VW(?MGt?%{yn62$L0z9EcOrkC+s=db8>h43&-A&zaaaE>?!?g_Vo>OUVFB^q`hIzGj4xO|BCuC^#k%3j9+ma9#Fqv{DSRv`}cxvbhkaCy<pDI&b8w=$BxoVe3x4Md(XDhG|^XRqVLdtWBz;Y8!HT4;=k#IMG5;7yITB9`jn2vU|uZ7?zR}z;vdtebu5hAQZjb8g)vU<(U}=1r%p!`oscFv1<e;GudRXk$Wl_LrI$D!b!PHJjHA-WqZa?lY2Ry(hv<0Z!lJTXEKlww=D()COfCK#_mTJs?KSy1<{YL!MlF6f^<nBAv~`ZHAzMeb)3LRTcQal`6TX0Y0rwR)m+=DX$=oLKJeuf9^pmM2_eaL!2T@O^wx})Ui|^)GZ*K2KW|0l?<PD(-?@8a5x+irTn&|K7n^J#A{VlDwV^zs&lht*sEaRq(Ytw{RqOQb!g_U4jiMk@S_$th+L|uiv4y~GF&B&^e6?d#O<BE){(S$dlZo+-Vw|A@~b#=z>wvODdI^&X#HDp|xadn#T7St_RM|^k3`cijh>~8DJ{W>!iU4yascGThrQg@~vOg)%2g^go8n0h?5_>s&TOg)l(3i(L3XC&EJPwZ;({plrVh9{mtKZAM(bCy$!pX1p!hbDYAP4s@+MaQm^?IGJkE_%CTXBqEde32$RO&GNJtMvICE8tiH>NGTAg*<r~Xlcl$UINDAV{`vg26O`EoMPS<YGI;JGCoBu`)s0iw@bW@Iwp@HUgBS9Cz-R2`HRRU{*_+XE>G-g@xRkV@1tMl(Tf<1O?2!hvWXrpY!&xe=FzJ-FXCr%K36e+re~Ww*E2n9U?$gv_%YNIsQc6Rp%&kox<7SC`sR)`aI7nJYvy;QZq4nI|AS+lxNQXEu4MJ7yHYo2PFL2O$ovuP-$aid!G6r79zz?!eWhMO$BG&_#|x5mVqA|_l*g6r*%^!FaI8FacE-&amnX|Yo`rEfn&^`B1*vl~FCVq|;`Fk;v?mswn|URuvv}g1%q_reWvR0=&dPjuTW;<rJeOnN&}Zd-S*WwovNFfb%R?@4UV35qJ#l`T@WSL0m!TI{*%P~3{I~S=4cr4OGrzuPn|ps0)`q^7@#TIhx+i@XYViY%FZW;3a(|9+Y&hdCj0ez!kER~Y{L$pIsKrn6Y@0+A?ml~nUPHfvdJXjs`pw3d=OWRE>22f7vy<p^^e2oj&t0OQ&|fpYJe!G@=QZ)qsKtM#789L_{-I-!nEQ}<Vg{cv4dy)}6aN?E2af$o{gAP{?N7!pssE&wXXk%eOL9~27{U_r`S)Mr%dsVvI)8J2InHg?zD+LrmVwU<x0!Q`TI>$<u22h$WX?0{(~NI%|7T=Z$gVL@_;G4sN0}E%ew2DIwXg$>U45MMc7j^!tY?mF-@w?_2RQ#Wwd}WqIUA_OZ>DWvZh$$meLDRL>VPL+!u^CT<v!D>g-vDb>HupDC7((yemHF^b9y;8jN5xK9!fUN!-sOeY1}r7Cb}PeFY12O9jL|2bNL{~-MDW*GRX~Rp7>hS9jF^oH{!m+iZE_OZBmPG$-G7$Exs+iJd-!2HW|CynzCLlZZoM1P#0i+5w@cyw@aLdCb}4{2y=?jm!tPP_C0ki#_qPpw3^HjlWSlXYCq$~jJt4OiCfVclNaW(%TbH3Pb<e<KgYcX+Y(OZCyQXeim^sG=S;TEHn1i}QH!5T6a6Diw9NHN=B=fk=80!>zpdQ1lX@xRrObD?t>k_ixlM8pF&2G<ekZxh&M>}2eUR}%?(1$l#C+lM-N;`0gWPW;weY*#c7|H~E7}>>yTp2z>7`xAJn=F1L+Y-lZDjojj<<XM%DFp>CVGXZeR5rs&x~^amiu!lYGG9vi>^a0tOB*LW{gG4vs59*4H#FT72-Y(7&qhg9NZ?BmpP)dG0s6PtRwet#=N|2tNYw0d2+tVc_+_G&3O#jN1n^%`K=*+4QhENmCu3lEZL5{6Inazaf~H*B4g3=xj>%d<vIN-W6|<C=yx*tER>#~jnb2gP8NpG7{UrNPEY%lwF)wp8u^(ctR!Psi!Vhh$oz`jCak7o<;lvEi>}VNCbh{}tT^*bYGFkk%gfkgT%4AdZ7NP*lG_V&n^+w7L3D1$`57l;Zf?(ZiHp!gm!&UFU7B$jT45fuGUKY$l{`5`+4ic8O>QsExC-MsWR*Ou7I`hkwP}@joci2Wn_7Hb`pVRGspa@h7&oA<@5!l3-h#d{brZ%7IA@Kit1|X8uQ9DU=eI4nZ12EWba!fD{TYiMK`m@7W6{&7h0S6tdJ(m-rHn<dpcb}<vFJ_I!gf2hfouc0=$(vrQ?Fwzwv2h}s9hFtY_?;osh2TlHT5!XUqQB#d7G()ZDH){)vU3Z@m`wfJv7nVXj_=SkK49Ui$6%)#y)LhuIOKwcaU2AS$f%i*b^V7?d14e<vz0g55}S|kxP8uvEyXoPf(v=j;r@EK2Cjt{oO<MGvniA`#k(Ok8_GSKU0gpK>L|FzjK?g>(s(dQwzJvSac-yP4+R8`Yg4uBh+U(K1Zl`Q6HwZ86TlO&Hav03)|}0e#drD+tjwF#(w6@_RWm<Q}5-r{p`<vGSO?fkJMYw*wx}U(suAzs~E4LUhm0~?Yp^6;!U)T<hz+8eP7D`C3mJ{i^*m&UP`u#dMvqYA4M&!KV#9osfBf5EV@0lFh66_-#gZsaVy5IZtuzM%>Bi;aqI`jnp1b?e$A;nb9-<4iENYTE{xr6qgbO0W6>QMiyuJUg?c#kaMlqvnelMy>D1!qF>km>&*Rw5q+U$F+@q&67F)tOo=)xNE$7@U=XTKx!*K0d!u*BQOUTz!ujM`~nG>L&Og)+LbZY76RL?e7i=RzD*s(Fx0~ov8#?XZIBA0j(P4qPSUew~-h2b6}x)Wn}+X&X{#CR}|+leOg*P5)Ohqq=O@!^g&<Mwc})?_U`d9D`UohG_1O>_(TCLZ04vD9wLSgbyIGxGZM-%@|exFJn+bNX=VI^0%|`dd%FZ2yki8hW(&M)Y#dw4!d#*xe?)8ut-agR!f{H>Q_dzb6)5lX=1_QVT2LSOv0Dj4P7Wpe{r%+lx6?j@wHxu0SiteS{TZT#oImL0y({5o%%ixK9b{JdE=&Pjqa?`NF>ZmXL=&H+3Fr*{1+=OHh|!Kjhd|IF4nhT~>#@7U#~LLy7Bio@HIO;rxVC%et4fC~HuzUvf>6Yl)oGaz1aRiI#hhJm1LqwkYh&v$7mto)hJnw>tYFeTzdAEx(P#p_ga!WYqGRWIjLp$Y-EMjNQ*eq8HLcZ=v5ry@|2xH=g?}q!z!JUUIj4V$oBWx0qV|a(dam#}m81Ye^mXElGYil;7d{^YdeSYWWUbzIT`3Jmt4t`QAsq*OAZF@>yGcyO!V8<@33GF3;iUY>wrmmpCc4__&T`VjS0#CoC7^?9@3Ji)C>vBYjThXQ$3e%gLOt>63W&NkWtT;*(_}i%%V$J}$NRHwJWc>JJ9|ed-U?FKD8l(t?gXCkv8^zQ9=Q9&>`^693`YdB!&xyZQoa$oA`uFHqm0zQH=;|8eXc^>xPXws$mPUxk6cV|(6_MGN~9f1-(w#&M3uG5++w*jMC<IX4-}5>scT&Q70-Iy?0@VQ5z>ZWsNQv6$$Oj8ii|HMa?`TO%w=lBoZu|7GTvfAa3B5%NFK{NH<q{@Imx&(}_^|NIeF-5Sy5eN7{Z^Pl|il3&gi<9`6^aln)'

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
