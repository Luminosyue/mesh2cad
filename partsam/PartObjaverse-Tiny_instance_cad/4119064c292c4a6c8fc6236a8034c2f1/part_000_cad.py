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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_000.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_000.stl', 'source_sha256': '85833a4b21f6d44ddd071ac551e2381391395ff01d7b35df839e75e7d2706e50', 'input_faces': 756, 'input_vertices': 384, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06468062847852707, 0.3762228488922119, -0.07580508291721344], [0.04976075515151024, 0.4812847971916199, -0.0299729872494936]]}
GEOMETRY_BASE85 = 'c$}qN33N_ZyFNi^)hwnU4pKo9vmk<Fo`MK91o1^g#FR)xgy5J7f|w=YGX+H{HC1uY!Q7&1Xz{654K)?jQrvUi=Q;QP{=4p7>#lqK>;0eSd$RYt-*@kK@3X&?tcG>Yo6k$Zzsky-I_ZhJucBC1Nbyp}#w3o3i;hXEH7X(1Ln$V@_0Pt|T|ep)*4INBt4#149Fr8C=ohT|g$!xz7ohqLiBBAp7&U5OeB$63OK%r7A}PkylZHkm#F(F}*Kgb)K&@XRK%J=mAO96JLvY>A*m=Z?<v@iiElhCi4PR@0)+4{(VWBgmyy$APPgh%?9jVns*JhLwU1_sro%LDG|Lu11^S&4KfE`Y0AKF!PXIT7oOE(_el=e>5OLSMKkQ<in+Np08{ksd>q@N>Gbp77Dt>U-KQ{ekeMOP+w`cytAKNj66Iv)PFK9zCR&vMazzz}KgOscR!#><TmUG*O%?X|LXL|1!t6<ycPV%)LU<+HPHP59~UExHjkHdj9X{N`ivw;)P%$GFRgW6mqljd!u)UzxvYm$Y9rQgr>zqMsz57HuSc=i0W=E5N@JnvL}s1Kqit@i#dq?bUOyx5)h8A0hr7$6CpJx*~rOU0K*j{JXyX3~_(;1@yQ!$ji5c%(G)cn&_^TBQXz;4v2p}HWlp?vZcN1xd-#Iun%<4#o}MTbXMlg`J{^Ij<uuU=g-*P^0`PUw0~ttd+kgX@{0Rvvy9s@QQAB6+>?4!TW=R#4Nb-T^f@czI&Q2GUD?_eb>gW?oZ9BGqC0;bi}qig!Tc<51HHjf%)|6ZSuclwHH=%kr})u)znA!pLRU6Pzm#I|6M6&VUiv|F$8FTD^H*=w&&&0q>rKaq?&>vO*4Nc@lITXxF4W16XW~bDK2UTmtrFJvumkloq6x;`iujH6>f&GV^TD|9He%kcS4Ev)y)FHmxkFJ8_kM-{#7m;<)q7yQ8ZDOg#uKOLTK#aW*Ns1=y(@7E+9#uawCulRzv!1@5Z8Sl&htT8FLiDm=+lRxp6hwZ`Z^Oo6y3PCLHw)12T)g@4+ULe!%?5Te?k1U?%?N*v0s#<RZu_IH)7vEjYIo5|Ml>{M0EYT$ygVU1>(nbJ5_YWXD{Y$&OV7#+g4X}weZ*2kE;%&{$ExS-IyMLd5hSA@%j}6h7W_EN_(;2=e&`)^ve}7Z#Va0p3AMo`rpU6+N?*?Uu(B)1Lipm{x9sreyK7EezqfD<IpCo%iY1yb9DF*XeFN=>6LK~T^fyb**Qh#K}{%%aYqHBZs&h1`8qaVke@3L5-@MWgRt+SzZBg#3tbuiA@*0eQ*_6JS~v$fJV*S#3q*JA!?@1!`K6vUrM~Feu_+R#lDGx)Kea5{`%XeUvmfF-O@M9`-H&>RzkvOo7rH)v5Y{ELEzgb3a&GCr563<oc?W)ivP5@`t^~d1Z&;U$^Pzhne)XS!;D7XB(Up4NV4lCkxvg{v#<|#PAJ%toL#bEwS$;f!zDK=jyINxZ`g<at7g!ggO*-bi*a?|G$0*dZ@zqV#=U<=TIq8YKob!&L&gacQ`<Cl54+Z~{I9>1JL|0<5kF<<wXxF(L{8Yrg(?70_{np@p{QQ15)PFjjXO6?~@O)d$^MCe7vhJF8L3HPuSj^AF{ixd#UyE*>?2di?hmLw{l@32cuzy|8+GGD5ju73|1Lu;f{2@FS{Ch#)fjE`YcuwiHd~kj&*opWLY{ojK<P%+6hjZSzk9E~!j5RX;7M`o?>A%G|(Vcm44m-{oh=1)Pxpyd^g~NYtB-*dN1ARWv`T99H2af(Cx+}Xi+V}2;bEHiZ(e(`GbuJIi|E8tT{wSV1TKGBa-?O`OM2|)Mj>qS*FZ_3ju7qY`9@;-Zy{&F5x*m>rl!LKY$HNb@MUTbv(K+@E=BvR1=xdgs{dZBw>s+en&ZVsof5onN-fbNzx^@ZAYa`wt@h_Q^CH+?5o}e%EfIfGI=#GlGSGb1aeAi1(5M4Rc1miBfi}>4j65ZH`eWB!hCi&{+maY;^!a1ft{u=Eghl#GOz<oejRt4vBNDa}QjWbZU*&T51oh>W65sCYiQRFD*`I~hsrCt<o-cOcdUrz`VU0;QG^w<5Qezd*CMK`+Ega0aPQ76kjUm^O3m>=bX-Pn(LHm~@%`8kh$>Ks^8bmwc_KaI6z5dYif%OxId0nUN9SvUtyyF}N1ID-0|u^9Egw!P?%GN@<Qn7-JL6N*CLoq}^d1NSlG;Ok}b^O=ire(uZ0zV35UbUl#!rS(?X|IYXj(bZbGM;Tk1VjVBNUMg699Ohv&&!5-diSAIF<Gj6+AN3PFLv(F$Z{*u%9iCg^14LIt_`FDdhI4=V;U$uH@e=Ug<qYC~woi1Yy{||1#=e*oFS@p+GWNx(=7{rPZP6Wd_aUC{KViLw?p`eZHgCbct56Wnms8V4*Ew&>Y8B7Rkx6KOXgKP5(nZ8m<4UIZ8{Z4-djt0$wc=sX^|8IN-#@>Jb7@+V=+3`Y%>VPxac*RVi0<&fxoQOdiSsn%%p$DwX2jFcz<nY!U3BM9IM4N)<#wYk(?nNZ@xJu?Z>axQw-(Acg$Lq%epn9oy%85gR|EN67~2fb%ZZtyE7f+Re%|dxoSt1ocMY3}dE1D4kv4I~0<32Z%tPW{+`~#aM0b`Qg7&4>VBXgKogwW@9mhO0!}G=Uus-xI-WWIUM$B8plKJxUKM;?0;xOhRa^if<PYV3R<)EIM)t@Khu0g)KD--qE{M=m8y(giryz#xv8M767G1QfQy*=viMV#o4kecv6<pAcPbJiSbpHdI?tbd97jBB3gMr+(>ls6TyF0YbASE6{on*0FsmcOm&uCb_p)eHAw=cDzr<mV}$BhEi?A2#-kn1y{h4S9K8!+F@Nl<4Xg)6stU60Cc{c{4>XH5m23&<FKg;@%7yXIwn$YBHWXj*da1YYBC+k4AckAIC~#y2QDlD$arFsDJ0f#-b~~9)KT@y7<21y?2`UNjr)ANy?X4cfF|Sj{P`SjS``_|D-2P75x|9+XwxOIy{{S{qZ!Md(9T$o_aIS6#04D8q`Ay?qf#lpLEd=MWfCy@5giP(Q?t9(<@*dZ~No>L(RgXJ6Qk9%1k-;w2lQP$<OC@!v1Zy5b<B`HBs^nj=?#gY=U0BQJTc{KF)tf`R=mrN@Vc~GJcD$y#LHV{9RwC%Fm}ev0f8PV!sTVA-eH5;?!g3<DAd`UW(wcWX$umy{Mlx_mag=?pCbV;6*s!>RlIIYsh=fwr!|~UOS<$N1ZEcBjmYe{F9t0x_S)$voWqwppfW#xuTf=)1RPD`V|{3@#^h)&U@qjR{T_g%yW%yi03@sGZ?2wjgmOGkH>tb<9ofaSRE#K6L~p&A7bB)>pE1%-R8tPKKUMXURe=c&5JmlIpO%8nRP!_em)a<X*GA@y~n+}QP{7z|0vx{qyAqG9VmG`<MaCGJ-8R$at)C7LslTpB-|gAE(iLH-oG8zF@HGf>gn4alJ8F3ADj)l<K9*AR!7l;Ti_fk%J^rVX(jV^iT8iU5yW|Hp6E&e+!I`{@8kQ`_p$W_eR0oMQ!#IftAC)hi(HQSkMPI+A^crSna5Aku}}XDMf|=i+DQMgjB^*?yUh&iEc(tf*cXRT&&tu~J;hHJ;#AWT@jd6o?|r2Ir+7{|Uv7v0px+{79y<hL-sa82{pv~ILDH@z@^TE@iS{LWM9aK1JB)hEnTI+rI!Sa_P!r_aw=(X}Q>G3Pea~F@e?A<~uO<)TB<|U$AJ;bAXOuO2M#y*tGmuxi*@)+Zt|LXCkA0!-=z#lDh-ZSt@to&&NCLhW9qg8X`9hqI!lkjkVUH4}fAe5|A9;x9LdkEFB#w=^&nx?puNHDqbY&O6FGrlf_tokF$&zPe1pIUujrzRVG)3C6o{fWzP$!dDif$D1#eA0Z#yPg+&^XbXdm+x)1DJ=Rnd8O($b)?D;~ds@HJ%{jHQbK&kxwxH5i3P^2E?Nd|HeJpIGZz3KG$Jhv+zF3i2i$$_?_GzerBD7|D4T}MUSeAdOL;Zmt$XEUD_?`i|6JF-j{rPO_6qi+pu5O;Cbru=_9%}AI}A+j(d@-^(oQS^}PS|c!>Mk=-jE|zaiQy{yumwQMSc2=|2?hjnBH^J;H{~qU+Cg;QR6gyw6eZcup5T>HV=TKb6F}y`}mL>EB`k&Y$zR|2XPvGq4Y<A+Li6@xJM1is<TwDBd?_;rtwNVy5VukKmkth5h1q(PfsjyS@|kTqXnO>gU}=cXUdEf6sJ0e^)I<d+##v@0*GH((`6>#D6I3r%oZfH(1six}P8FA$kMyeK%8dC3pb#OWicAOT9el^7#Vt)sOv!_c)&I=1Tv9+%Mmq$M>49eMMI)2Vve$F2+0rR+%ULv(esBFAvsbd8X(_9`1{fZ}Hwfr^I~ueDn+C6_tznS-f~Y)_XSM-1Qam-ISRj`jc5W4}X}1dU$b6bY*)Y>UJB>PjzSK1@gHMp5t2QSEz?Qmqa(pHALP1=!x^{X`_X*9>o!lv7iRNUrZk*x?Z(9=4T(@8|?L5B>uB`&L{N3{>}ChUGIJx^HXCh&ZXc|qN~ktuIl}7;W=0$6YcXOFZ25;&WB1KnG%nqJoagdFV2Ah#YK0l%0iqj1@Wg&6J1k~uW^*;(!3+^^NioShi<^RH{u2KX}Cu@XD!7!P`dPD@e|k<`~A1^$oJ}P(bdU(pC8i+=jzAzMAx$rr&d<SIT`j!bm#a^sKZxy-=){}St8@E&BnSvxQXwHKb{v|J&NbJ>unD16$y2h%4eScN|PPP*Q@bT>^t5Ex|hTE_ZFJy%G6w(pKlrewJo9>{cx|)u1?1NXI|_wiKBgI?9;G2h$l8dbl1%y*r%uP+%aaSitf0Jdyexs^&}no8u(G))x`WqwqO2l<NnYD_nBRrL{|zUP9+oXlZ{?GMAvfpysP>n>f|kT=4(7#gnIk1@(R&8Z_YVyaIbiB5_%`hvz}WE_nA`<L|3X}U7Wvvg!#PokLV7ruYPO26LnQ!rHse*)msH)UtGN?x|-Dn=jtZJuYdAdbk`8nmBV8L=0B_2Drxte?^}!$c>nVzQgl~E)UE1w8Tn4T0=*UL+*za{?mw>|LvPJ^R?opY`t{6`c9Gaej>}=l>xZ+VtMS;6#_$Y0H_KiV-H5<`bOmfh`v<>@?%=*wyl3NH^fWnJ+E2ha;P`PI)~n?K(Osc9HykBqA)b40MOPAW&S>Rue>1)f&JjP!$k*xZ#JI;7h_2klIcEGc4gRZUiSFt!8}+}jIrh<o%B$t`Nt~1Fk4ebuNv!DFO`c;bAMyR<O3@v8aSm&x@jhP*yC}MvgLB*Xy%Ej_rNtU)pNex{J980v4G0z8;B&#)yaM$$;}+Vlz;i^ofxNU~#hl__!E;CPY>oF_$101iJ;d|WvEmQJ>8K{U!RMMjwXD>M<NjRHU9Qr|D<1b)XSemDJ7?l~s+PNqd+%=Oj%SHj_f`B}<8uV@bU(u1<7`9SUM#y-;^~6txH5Vd+N*w|tND?at3p}4-(CV;R}sHD`;d(5{5U~$XBh4k`qM?2hwORKvvCj6N}j-T-?a&T;&{&~{T$D=jo*mw2*N!_ANCsW*#q*ellV5Ey`x%x{2r%CdC}Djw0G51vA#_!i|&|-dzY&;-){ts7TtA*_q6%NaQ|5_Rdgd8_d2CA-bcAsFNgmZxCd(a5>Ri84vDUH<L_0oGjLCspLf0JLvhbkGgGi$XNrjKnvZ*_E2AIYtK6<6y5sgizQ;($b3CW7==ylvdtI$2<2};2>7qO1a8Gt_T!_3PGDKJM;rFMy|4HoM1!pntO5DTMqA`eb>Ywm)i}&7QS5eRP-y;6qytn*`-(Nd&M{SVy%kX`{sF#U)n>Si?<qG#j!8=m7#{E>$jZ@9=9M=Y;&R;l1*YDtair!`u-V5cq3P0U&{_Ef1eV6)A!Hp8fKzu*a_s1gsxYp3~As&5jC47IW8!fute-ZYt4}Ndx>bny9alDt-a^B;)mjyrH2VfoZZAbf0w~DUy<Gp3wb=;$dABUeyeDD1Z=e9cHwCL(?wr?4Q{d@2Q+VAJR<r&@^J1>{Z75_irIpU1N`Wlt|MRz3Qd#>}>Y@B;WvgqoGa;VP@<#8`+d_;7k*-)I@8@|Br!xC>oug1T-ScmgpKN7e}K06rygk0>?UYh96o&39tThnn4%!(FWYsTLr3>t&qyR928x}yZ&KU`~x_ko|yg`e8gvvCgSZCAt3m%PtZ#<<4*ZSd2A?>(~N-`Vnr=*koRzGe{Lj}`eE?cd`4x#m|3f7ep+tmwvR{2t0t;I{mohqC?PW~smNIjH~GXw=oim!j)0@%t=8D}nRpp8po{yN&gEWHf(|*-La+Anp}f&yr~0Y`o~Yy^hBhZ9Nk9Z-2csDK+xYld5JWroFFtDMO;%{&dL_B~9Xg|EEiF4gObuy40v)(Es;OmkOIPc$$`<_&#}l@(+k!<R6fiHmxwR5Ydag5P3mj3G#yEd1w~TOMH(!FS!RXAGrs)!oCXqDb#KM`8a+)=2M7Rn7o>46-}!`EK6R6yaLVQ#Z4<fEJ7?xUWB|Tu_AeSVo72}@{;5#u^PEbUW0utEJv(HUXHvJu?l%9@?yja<i*Gf(<*R%DlmuAwBlS(J5PIkEuNo!^V45`>bCy^9KQhP!j7j1<1NDc%el>q#T%Gb+q62wn&frJ18Elj(6ll{Z(>byZ}LjS+T?!3s>IslRmtlU8<5v0Z_K_H`Vt$E`;u2C)*-J<?n4YD_aQG&3*>qRGKU&8i>q#Vsx*t2WZ#nXSCYEzzYNDO!@02I@n*c<%-`2-UM$|)w3dqX{TbMdTq6&mS-gp9)rkSbX5<0nb%`y>8xn(vEy;t(+Ywunw<B-Mz82OawkEGfUW=%a*CO{PhLHP{`_V$Uo*~SkG0o!j-SV{S!Qxffw<`TrrEdGL&he{rF6?*$7;gacuje)|77sJ6r)i<YZseil9cdQtY+5j}Ik6jgbMiLCp5(2F9f&>2JCOGwhLQIn@4>znwjhR)w;*py3?*+$-iX+dyb*arT1T#DN9NF$X7P4zdD``0@gVjMqQ4;Ow*O#`AI!P1<7v)#n=}6wZu4UC0j9;67D0?6k09?&vv_~gx)8&OQRLy|y@)a7-HH8(G35QohY<&m4<mQ5uZ3NS1IW9QcOpiRcOq|3>`mUDycMlC*RwZs=s~l1AGbX1da!s0_U%A_9jM#>yKww2oC`aiaK;<X{JXl%i^bziOExW*IGQ|`Jep?lk){nK4knH!A51=!m`py17*9+lk0&2bj3XaUK7xHMj3ma9N0Rp?#*+6X|A-h({t<b1S~S-)nmIUV79Zx8r(F*g@5jFV=&v7j+y6k0Kag`_$1|Am4rcz5Zu4UC6w_vymPDLNo<yENv-l*_#t_F5r;?8&pGcfRo=BWRoIyT?d=4>%d=7ak`&u}Pm_j~^d^j<Qd^q_KVgmUP@<Fr&u4e*s7(ui6c(*+5da!sr`^M8>Jayau7>+-Nb799bj`5CT{-fOH#p2UUTdY{`oq!9;b@DWt#pjtelQ@^SkbExr0^(xw>BObP#pFxLR}iO>uOOerz7|d<P9vX8K7pu{Paq#lOd}slo=8jMdZsalRGP)-xaDcrgT<$??-cr*Lf!U1ljG0iT-fo<WxR8l|75p$vG^j>)|!?<Ttl8go=&rPwrMMgtBGsKSCg+Nt|eba+(cYUzKMJzaS{1O@+ItRVJ2}Ac_#UMVg~tq^4Y|6^4a9mY3W?gbmlONX7LqndD``0@ulp$l>U}dxBai=_$xUVc08*Y?`r0s={7GG&oOO>X<5Xr<XPm)X%^pX+BV`&;#TsV<ew3DkZ&RGC+;BMPri$oL%xfA9s63iftW+Sf!s;VB6pInA}%LiMZS!-oa?!qIV_=Be4|^Qc0E{p6Z>wWzfII_|JykJHqM0|&rZg>llgCOn-`03H|?Nl9}^Fde@vcBv-n=q4ik?P50D=x|C)G^{0rhq;z9D0<VT3x$&ZkK%DxuvBW@?(N4}f*G5K!tPl&nXpO9~%<#Ii9nZr7o#do>oY1f0r_p|SQ`rA+4_J5e;ALd-x@f>Ho$C>{=w|TMnA=6Hn_BruO^3Tcl&@6t;w6nzX#4pLulm9?GLH-@_D)9vQRq`{$L*!@3kFu|Yr-_HiPm_N|{G9wNa)Y>s+#vsgwukGvhdF#ov-lCWJnee0_(}FXNq;A)+y2jT{Ii@3JD&55_dN4I?KUqKKWEw{(@qgDke?#|hGy|^O}kFKMZ7?Mi~LvOCGy+EyTnW6cge31&yimtzsSB8-XNYMzd?SDc#8ZQ`S-+c$iFB5j`j`L^Bd-HlxFcWZh6}EVDYQ$dzJpKQn&qI=lIt-7j`_i81F6Sf5UBFEbcPxXVZQp-X#B#{4&krKbiJ`_?UQ;{4x16;?LwSh%bphlfNXtLv)efA^(MaEqqFJkv}E>o%kd9@8rJ`FO&a9ew%ig>v@?uT%=k2id&v`Jy`rM``)F$yVPy}4><k<&V?P%W5)ZK`9F1=7mNR4+7r_r5g(F2BEL_w_&w8J5#JCWlD{GM@Bls`f6oJ$k7()n_}Svm+4c|e=j4AW=xbqK;veLeS^OQfN96CwUlZ?>zb1b{yU+E!&m4ZC-Q)V(dD``0@t5rTlKx&&xBb83_^&t@c06ww^Bc}bUXOpxi^V-nd#fn&LfgW>$t|<^KQxQ~X<7jf;0MIN$v<HG!o;`a-X6f>L`yHu&lb-^wBpD^vv@)FwXhV?le`ppF``0VjJy!hin|a$|HJiskNhv@^(XmX<j>vmwCkY&>*YOSAz}fKfB7%K@e6P+?07z4ydN<CQXc=B7mJrQt%zwQiSLt_Bri&{cz)Boh-HZHlb0bcPb@-SgXlvnLheIef>@Tk1bIdFweUk?S@I9bs}f6+S0%4REJ|L9+?!UE>sgdJ6r|<n`rCQh_29*N@g`Oxdb#=c;`m;i3p<`NjJFK)|Ilq-EFNH51=IY9<;eZWtI#Z7+BB8uODsq3OJ1E=fxHQ^Cb0r}P4ddb0P@P@b=cR!hQt8!hUE2#e&qGY1Bq401IcU9s&GB4Fo%k?(p-N#PrDv0?!&%5^yfp}_OEh$m2+Xo<I8w`nSVpKd9ip4(`uX6l;}_1lst%L@oJ{kBGx7Plh-A0K&(yPp4f<3o4gTuePRpp`sA(I*TOc$7UXTnTM?U*w<2#w3?gqv-h>v!^$cPTb!gSN{&t>rJy^UZ`_`ntn$&IowK#q)&V?OMUB+9N`L}VK7mIf{O*5?vF@(Gec?X)s8=DqPY)%XzZ%*ElsF8m}Y)jP0+mg2<b|-H~-kW_b3@3Ic4=3+R>_Xm^yfd)_d1vzWv<_U)4$Pr7tufc%&eN_3i#KB5M)cQ+y6r!h;|Fst?0A|p-sa3d+-+Vg9&K7r(*_c|kq;#AN3(b*(>fAEiQULU$-{^}$p;a85POpMAn!wrChtQY%f1#y5~Il@$p;Vzk`Ey7OYBG9m;57IKdxs#=FpqgiR*9YY1f0r+p=$4`fE$w_TQ1?cjR2y@q{woQ05=$HZK+*XIh+T@x&<dc=C}ni}yFJ7cqhuMIJ%!AjXj=5@U#Q<T2z4#Bt;a<P+G}!coL=<fF)k6648-k`E@1Bp*yZh&GbzIg&ZV()x4#?L6&zuy_yl?LmJ%sN4Q~ar|DK3p<_&#v8%>N4d?5#V46I*0hPlG2|1;(`XhSZQ2mxFya{UVdTS!W68%8M-a!7k04JaP9jewpUl1%rVuBQr;sNTCz2<VClS-glgJZkX<W}V<}iUan(J@pY1f0rW7s!_{$i-x{)ce<A)E_4o?(o481qkYn-`0Rb@s^PmG^)8PaXa1pYCD(zx#jq=)d;-_dhdo?|Int^`C!q6xP|(`r8d9kNH3A7iIUX-{dL(0b-`phX'

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
