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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_004.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_004.stl', 'source_sha256': '0b330037939da7eea452a0f0c088d6c3b5c2e0c9fbc92648592e6ef81a2861b6', 'input_faces': 1164, 'input_vertices': 766, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.17530708014965057, -0.48079103231430054, -0.11520543694496155], [0.3458224833011627, -0.16939677298069, 0.24993136525154114]]}
GEOMETRY_BASE85 = 'c$}r3dAv^5+s5~PM43wx5(h=8G?`L3O%$0EsW@iJlri&3r9#S>B2LCADszYvnWw}tR!$R@kmgc(_x-HzTF<lZv;TNM@9XosKi9RceXaZ1=h<uT{j~1A_OD5UTo)Ae%)hc;)}XoVo80Gl5(T`X-hfVh`gQBjsc+?;y$AW;#c^H!S)ACYMZ+c!``!R=NX3qw`gZ73v1UreJ37~>czsI6&b|8d>(j1h+g^P-b`rgAyY78E1$y7E?Rs|#+SgRCR_*$fTd%!7WmwAp@n61R7t#jw-dsoa<*{{NtQSmgnOP@EPyJ{`Tu*zVz@}u~TfEHpU%P8VvYz?bB;y}nbW5_H{%)(do;~^DZK3=FfB!tLf3|mfvYxSeXk1U7ow75Of9$ExM9+Nwo?Ri`Yhd&{s_stKvpc+TG_H^OEv#RD{777XbL5`T{``8a(YGEB>DjmRIvn4h%zwlBtE&#h{V$vj=joH%=#MQ3=_yyWJQ&w+C?C?(7A-mu&tE1jw4W*U^ThScFS~{Q-jsqJvf}<}_k_QnyqovOzt2TyL*Hjg>WxO9H6Zl;XV#pyFMhmgOb#6{uUA2%Z$214?w>#RY5cf<&|zcf_+It*UeVJ}{1_TP*~OoZ>)yFy>q6hpf4_Vpdd9gzt3!G29BlNPhO7vE?zj2kdg{i%mxT7e>|J}}pW9{Y;!ysxU3bUxjO{l+l>hB1yW;*E2hR-Yoj%?f*H0FBIW!I*IkO}F{g-*B$@=8K>u?#P7j82lSx;L~cY9p#vH#6vJ)=weZSnnix#7ZOJ>_u!t?|FBTEq84{<b5xNIRu&+Varn_MEgio@YYu4?=l%EZ!8~|B}N$j34KdTg~yzJKUV7M;};UCrQstf6C||{+*eur{(W&^hJ|DO4d{V>|@T~v&BD7)>G;kJ^et9jUjz%SL45T@up<mtI@{jBb#mx?N8_0MlYGUC8U3Foza&M*c#Fsoio>sHg9Z8)-#TMX7pc+Y!B^!vnfWe_D5K+*E_DKJ)E{9Sx^7w3UmD#S8->uo_+eXxy~FN8PYS0kBjT6Z(g@6l;``_MsG17q^HHsnCnu(*zVB&Keo!~FV+g_*>}`6dhZ2ceP02iFV70+89OC@9ZQ{i<(|;ze)NdBzBRrrq<h7`G1s@A?LvC?0}G5kqI*cs$bD;E&%CftSfBn^{JNL=Wsh*4>t8U}!>P@~dcVfTKcH4fPapiHxlZo;H~jZzEsX1_&G(1&^jfuze?s@L|L=>8f7y-U@8|t#=6ahoGjv>1Qo0!Zv1TDXyT&<ly<IdbbllThZ87@4_lES0s%_$W_K*SLaaH05qfg2g(z91{-M;gR(D=;uUXAN%_s<E9^UOh2jXq#Z=)B18oyX|)e+ivO83$&W>-m+-L+710VL)8Z?s#oT&zM)r_&e_io$sk1pN(JtvnS>b>;6P@Uzq&hhR}ZY=n~h{H;fBkPf`jP|Ks_?*PqLdoBPF`->(bp=b$l0A76ECD9<x(;(E&EXI6*&_vbcxk(R4MdhKKJ`$)=z)mMi0bIHp_FSU1BXgplmBd%v2U$HcF97~or`VS4?59L4M8~ysq?}hSLdNO{W%9z{X?NFZc*BQNdi3K4&WqSPnl{x>f*`YiiJZ$t6FTEMkk8F$I*D`MIFg2w2eLk*d4tsoJNT2ja{C<}?W_o%^-?22VXB<1*HS~8izS{U398O=Ke7x#^6Tc5;+_-K`vYs-(snI9zdM%`XQ82Ej=T4oOtY@F<6Tfd}+%$G>DF1(zjJ~JJTOt2*qvQ9}^lj%Ch4NRqGp=X8-RQlL|CVX-`)ua8@=HT{sm5_VWmorQA${0FbN@Yh>&j66?QM<TV(_Zael}fi?#nZ3uL<R8H!!ZJ7k_ST{Cvv3?31{DY5w?iJ7es}Z`DcG%MLjbso!|=aFp)Vek59dV8@|Iz4h%zFP9nCyS{xeO3(hTWVHVK=mU}Z1?D=LLof0~r0$hHx<69Cu|cGsQftk=WId%q>A0R++1v*+`d6PH(!1w1`s}6)L;4*<k3{*?1`j$C>97Ce;Yj}r-ye?hr?q-C+CSytXn*IO=D6g)HSC|W?NFq@-yPBZCAS&<wuWK<$afA#`O`BO9E|k8QYzZNyF{cvea6@Wk^awKJP_%B=bx-7f5s1gWkvc|caQe}*)7_?^|Sqv{yazaNBJ`jJP_?KT0hdC`OVsWQU1(wtM?`Q(?(T{KCi8=&ujD?=e5=Kd2MxlURzzC*Y<Pud2MxlURzzC*H+i(wf$UuURzzA*V*q^4xf*cI?PYj(=Qxs^k=VL81mcmu~OTR-<^-j@6Jc<x96kw+w)QT?fIzv_I%WSdp>HvJs*|dosZgY&qwXI=VQsTA-_8xwcnnP+HcQC<#*?!_S^GO`|bIt{q}s+etSMDf7<<=j~}%T`|bH?{Tr&7^De8Pxz1nu>D**JyXi$n&%N^PkpA^BGp-iy3i-XXr;bGW&z?FQ>F@d7;V6G*pU0y8Lt91r({~+;^pD<pDAGT!R-`{=YK>_B^hF0F{qx>B82R@uyfWIqta!A4)k_B={Tp5|`m`ls|K@+QBK@EInHA~Z-y_=pMb~KmSD%}4lDaMYeYQQcKhpnG!$^NhkNYD1Dd#`j7v)bKvT9$*U*c{vZXaU24KF({Sx-5|c)O`X*x!-yru=TaDZd+U+Hc33_S^BM{dT-*za4LS|Lu6wemmZ@-;OuscjHa_?Re9EJKiq4GVHhGP5bS5(|$YNwBL?5?YHAi`|WsB{?s2CZ`yCioA&?Bc-zv(_zSf%$E8Cda~-R{bWXCKUj4$jp1wQlosj>@;YXtU8TSr666qgt`f#Mb`H90({*;&6MEl#dH2zL|!~SWz4@LTWZ8;R_Ur;;RKdgGRf8}B`PO=w={F!6sAB^;GDjn^A?ea)}>b`LYBK`B9KM?8v^1rMofA;b}vLgLwdPe&<c8T`?`^El9|K5Z9qx@<48%O(()r<6}msr0q%I}?C8Q0U#?Tq`=UThy8Z+?Zj$$I9ejJL}>g#C8BX@553P5Iq;d$nxHpMAPzwBL?5?f-}IruU~*?P!0#8qxkrj5qBsZmw_Xi`#_#HA+YOD-@6R*JZpZzgN{<-?TsFLB^Z*-)*jMIsEN=M*7`&)BfI!H|@9MP5Xy8iuT*_X8rd)XU6BS!e$=3<A1Y5`ocWs`nGKJqL4mj#F0q<ssTqL{jZ%d^VR463i~%7KOE&xE!j5GpT7U0X#X{P4n_LE+I%Q-f2!4q_Wx8Z+JDcx2P6Ie%{v(BZ&oJKpHYD8Tm4aCf7;6jBK;+~zG;8Y^I4JpYq-8CfBMi~(f(>(qWz<f?T_@|!+6vFsf{E3>6_|C`ZMO4>s#jd-@^I#t=O0BPuV%z9N+)AzI`-uPO|Rqr!Dh@{RPZ;%i*{8Q|)KG<?!44srED8GFlA}`|bTy`R#bi;kWnGQ+~+r?x)J{?x)&s@2A>t@2AS|?x)&s@2A>t@27hI?Re9Edq35FJKnV4-cPmPjyL6Z_fzd}Rxj*7xgvahtG0G_NVnIwL0iLqdwo-WHx4`BKPOpt<8Voxa2|U-)cNi8Q0KSfR^@ls$@_0#6sfEH>GRu0=eOfr<#*RrmEY+)|8lOkI=?+HbbfmsR{2v~pzHh_>qO>v=aJ5DuiN_j=};{?|6Z==IzQL>9Qo~aUgv)jUFFX>Rwg<>_l1mq?g@_{dtcD`M-+?Be~SBs&d+@$M}B)B(fMB*bs#eTIqokyKlhy+`R#Q;=b!d_R%HIXy-og|D?|D1eJV$Od)?6a7j!my;g7?|*WSN$e)Jsq?R7?v|CI;!N9MQpJDndrM}B)<I#w;5$KD@Res_OV`Q81|`tyAqeSbvHaeuUaeSfrmeSfrmeSfrmeSfrmeSfrmeSbvHaeuUaeSbvHaeqY5aeuUaeSfrmeSft3ukVl6ukVl6ukVj`|MmUR`t|+M`t|+M`t|+M`t|+MexLgOX#M*BIPSaf{gL1EPFKJGovwcWJ6-+$ce?uh?{xM1-|G7Jzt#2cf9F@f|D9j`{&%0Ne*Zha`u*?x>i56%tKa|5uYUhqUH|@fe)ap``PJ`#=U2b~onQU_cl)V+|2x0>{qOwh_rLS2-~Z09e*ZgN{r-1()bD?%tKa__>+|gu)bkrw*Yg|BujV(LU(Ih=UC(b=UC(bgznb50el@@0_D9WcIKP_TaDFwv;rwcT!}-<xhV!fW4d++$8%|gA8}9E_^Bc~u<~N*Q&2PB<QS%$lujV(LU(Ihgznb50em%cY^D?uaYW~*hdj8h=)%>m1_57{#tNB~!SM#@4*Ymf|ujX%^U(Me-znZ^wel>sV{A&Kz`PKZb)%E<X^Q-w==U4N$R@d{l&adWgonOu0T3yfII=`B~b$&H}>-=i|*7?=^t=0AXt@Eq-TQ{!M{H+@&YW_B3Z6$MDRDH_ox<2Lnsy=0PU7xbLu1`6?s!ut;s!ut;s!ut;s!zH7SM@39SM@39SM@2Y>-v=QtNN7ltNN7ltNN7ltNN7ltNN7ltNN7ltNN7ltNN7Hb$!bDRej3&RedV$(%a1Usp{`m*Y$U&tNOdub^YD>RsG%hRsG%VkE*{rzpB4GzpB4GzpB4GzpB4mUDw~8U)A58U)A5;->d5H&adk4&adk4&adk4&adk4&adk4&adk4&adk4&adk4?)y~rcjs62cb8w)-<_`N?^f6K_l&FR7+pPIWOe;~k@KtPi>$7nFLJtizR2n7`68#Q=Zl=Ko-cB`dcMf%>iHt4tLKZ{->aT4a(?xEk@KtPi=3{WFLJtizR2n7`68?9=Zl<QJzwPf>iHt)SI-wYzk0sN{k`h>BIno77d5VH#;1CI&*|#<J*(^I_nfYt-*dWpe$VOZ`91f!>iIpVtLOKeuAbj>x_W-keXe?b&*|#<y_EMFoAX6Ke`|I9{H@jX^S9_Zp1-wz{rs)<>*sH+uAjfPx_<uF>iYRxtLx`)t*)QHwYq-(*6RBCTl5^y-&((Z{?_{S^S4&l&)-^IKYwd={roL@j^}T!Uq63q{rdS^>(|fUTEBk&*6RBCTdV8mZ_#r+e`|I1{B3sEmS&u*=k1-Y&ugpe^BO(Jd2MxlURzzC*H+i(wf$UuURzzC*H+i(wbk``Z9i9^*H+ih<)Z87?K3{;pB2Ya>1Lf^pG(#y>w3MR)%AKq=U3|ut*+M_T3xR<bh=t^Xm!2b(Cv>}Z|HQj-q7i4y`lRa)Otg=|7yLV)75%ItLycKR@dtd-TtWchAxj<Z|J^fwcgO}zglnTK3A<bbh=t^=<=xbhVFCKdP8?y)OtggU#&NE`PF(ur>pgbE{|Go=ybK-(0y-ey`l4~^@h%`)*Cv%T5ss~Q>{02<5sOVba~WzL-)CAy`jsm)*Cv%T5ss`tM!IXSL+SkcvI^QonNgtbo-;$8@l7J)*Cv%T5ssi7q#Bd>1w^9+fTLL(D~JRLpMIvdPBFLYQ3S$qt+WbzglnTbhX~l?WbCA=*ELuZ|IJrT5ss`tM!I1zglnT@~HKOPFL#<6W7D=dPAqH^@dJY>kXZ*)*Cuqtv7Ukms)S=j+a_*=)O0#-q7i4y`dYoYQ3S$uhttnzglnT@~icR&ac)RI$f<dbh=t^=<=)ehHgLAdPA2-tvAg0wd{fT_grt2xzC<hZ^kpae(#6X^?N^@U%mIk<yY_hu)2Qlhs&?t`(btc-Vc{wz4ycE>b)OU*YEvsx_a-2+aLAb59e3!{cyT^?}y8y-uq#7{oW6&>-T;*zk2V7)75)F-1nf~`{DfRy&ul6-uvN>uX^u?)75)F-0@ZK{czupdhdt(e$;zETpsn_5BIt1y&rD>)q6i&e)ZlDmtVd2!|Ce1A8s6~_kOs)OTG8Q9Y^)v50^*1_ro0*_1+KXSMU9BpR3;c;qoNE_oGSZZA5MF-oD`C>YgW&*DLCEZkO~bA`#`E#pqWNb*u8fdKJ;lH&?6j|9clvzN5b96^?n{wK0R;;CBX5Fo=po7qq*BXdc8+q8nN>ws#?hpo#acAi5Gm(Nftygy@VW-a<iKLv%$e!1m5;KN9Tsuf#QIvaJGM!9#w6|LmK#^qUt%Ch;rU9Jc?AE}oI#GjPFFxcJu5Zw`C}I2=9#-U_S@ZyiJh**9{wCU0vr;aB0UP2@w9em@7}<`7W;?I+J{&qo~aj3(Z7K};nMp{-^60b&Z;>L3=#xF#l{y%of&ASMta(8RkYh{;4c+6QbOK}<vw@0lR7h{<TD*e<@jzS(w$_CB@?mh}_-Lf^E@2hlQ!TE6Kc?Y!u<;4Sc8NZgJl_*4=fMEgx}5U~brb`S@HI7@E%++pBQ_%Qf~;B5G8`U%e>-x}f!+SM`Rk<Z8*Guj!Ve9UP1gQyckr<n0c`)c$~@LG7w6CKc`U(+B46P?hSu)PB@2u-}TgXl;MM!SRUgNXKM;>{PtRYXU$i`d?tD2FEA12TSztI+oQW_vl}v~M)=&I)2J@e^7G+fNg#(Zo9>h{42Kv^!`I!6*KK-~jkQ_=8|g_(MUIll`OrL*#o1O?V1k>9gN6dO6y8*e>{^m*AgzrhS@oPR>2)Bkld@li;iHeo9P0TM@+kAchmKpv?<nSrFrhVQAuA8N_&EINEZy4<lYi6Yt3&_7daKzGwT(#2z&9mI?lb+{9kAD}A$l50T3^ns}QBaT}2vtts2Z*Pm_8iGFB;AHc;|oqkQ>y}>8pz2R?wE8#PP*cZepa?T|0Of=zp@vbCJqLqyqkMz$SGula_Ow4E(261~3?PA6!?Xu|Y;J4u|L$pPcevN~8ifD({i0y5OfoS5b8IyS^6HlSlV7vHI*jAHv8@3Bxki<*V&J)C^GIo8_Cl5IUMHBvsZ@i_6AAF-pzZpTSB7Q`h&h{UO6=>7py}+LEUhpPhHTWv>_W}FD`@m~}&ESF;z)O*%8WBS)E&CLV(N8?%FHIjo(S(2J8E=f(?HTO{&c9cPPtauBZqCWwoRh+r1Ti;=p~P6UIYGP^#Asp&ns}E6@e(l<?R~ZnA;zGI_e2o8h?mg5W&0SmUlIHbKCuf;w(Y<xSi(>6^R%U3;~=UMK3YTHY!_b-wlyZY`$iL74j138^pg<Y73>D@3V#h;3ZE9lo*=#_=QQ$8LleFW?^3+Ef-!m}@jaSsJAqfwk0tmOG1GpGKGMG`+7-kjXw`#g7{ma4)#+CqP51+NA0hgqNxy1AJW32etHSpFL~FEI5T)o-iax?UwztN!TgEI=3Qe|^#4EVdPw?ZuX-mJ?gIGp<hc=b%$B89qUBD$oXEebFlK3sO8wF8PK9~IRS&xHHz#oTK0UN;^(NB1B^4&uG=NV1#8~Aa~Ejh<LK6j^QP__v_&UWF_cRT&Jb3R%=ns)u5Z?Pc0@=Q$ejWz{sJNTcU;J3s~TTt44VkU$?9Wx=kFL-M#!O#1qEqsS>+QMJ;O<Q;a-?W8a?whvouW1XPO<VZ$w1v;2y)B3rgBVQwizfVL-?Rm#-N`p0{C)6SKfz1HOj}Ue564Uh?-w&6ycJkHmf+v`ru_}M-UB=OhIgcW6ZlUO-%4Bf3$*2L8^zx%_$GWd{A=(__}6gx-UKi64VSo#?^f`Bcmw#W;AHr#@Ezbb_zw7a@L%|OxEyQ2n`4Gc+{}0od=lOl{xp~#ON^y-#+P94SYo^hzXiMrehXa2r{F)n;S&Eah6T66x5KA^6W~+e^}+k#_2I?9qVQsH8H0k^UgDg}W?YWq_+@~z;Ir@ue>aH5L2Lmx!MDKAfq%iz!Ef{p-ryT9A-n_F4&DJi348@U3H~m)2>veoYw%0>*YL|@1}}>lE+M=Dct5-Wye0S$yd}Iocptnzyck#%UJU+~Z!p_8TtfI_@E!PK_(bq!_(XVnFb&=wUKzX|UK#$kXYfzYa0%g?IbL%7J_a|#H{%ihToBI&F%x_PJ`;Wn{2YD^eyMNp65ntM;q}0K;q~C-!I$9U;ak8>@GbCj;9u}_@Ec<WZ-^N#A-osZ1KtZh0vrw>0q+TRhxde62Cs)#hX3sw{L?pFLilFzWB6wHIB+z49K0@g54<kC2zW8P2>c7r;AfuU62fP2yyW;z2WP-%;1Rwkh<Ae62z~_L2>%284gLrGI^W>6zTpzW+k%h5+rr0!FTlsb-v$@J--aIpKZhTKUm7!bNz8Bw;q}0K;q~Axzz5+i;B~=!;C10ez>DEU;9vL#Kl2Tj5WWz63%(FO27Deq2HpmI6y6423A_eg3I4lh@K?`p3E>+!UUK|0!42>Yc!WO_#K<6~fv>@*!H<H6;YZ<xeS-yk!zF~@4c-aA8~!5r9Q;N2M(`u}M))7#Z}30h*ToFV9Qk#G@F&1-@F(EIz@hMA@W;Wf@W<hmz-!=@;J^C@Wxo1%Lih$S6TSgH3LFU^1-}bSh2I4)1Qvi7f*<h=%DnLrLip<(FFAfw!Pnuh;}QOL5DSA?4}J(=5B~)`3;zXP(KmRtZ@7f;N5F^SkHDV=)8Ws;=Yw<M^WjIq!|<bUseuSe?V~Uu{BF?JK<<V&2W_pRIs7ir)->*d7Xk~w3&EuZA!ut962j+!bKvvf&wwM~&%j%Qw$9KRUIDZ<gbHw}1qj+&frRjN94|S3Yr%E!b$En7?U_0MSHa2fSK$Z2Eciiqe&3+X&F3eC*8yw6>%gA|hryqQuLnPbuZRBvo`wGcms*yf%#qvLmhdiMr&ywfC42}tIF_hY3GWPcgm;El0Iz~qfJ?ndQ0A+DCWNm8*TUDqhl7LR!{N2TJN!g#NO(T*B0o_B5-znJL76kQwI1P9I9_u6CV^AnQ}76vT8`9l)_}H#vj%<!JOw`km)eV<t<OjZZwa=5w}cM`pMnpC&-N4bnAwEzgJ2f?AY5u7g0@Z~A-oP~Yan&tO+j1hXbP_l+L}gfcs|h9F7m;p1|eu`6cWN`fwmSg3vTNU1K~s94}rGM@DRKlm;x^cmzsc}ts6)Pw>3LCeyhOM@YQ&POKnc({3n9r;S=Hez`gK&aH*jQ%KW^osR_RwybXRkd=S{*Pt??euK_>s6SXkmXTVc_qW&dZYFUCZM{a9d!aIQNVu>1-@Il~Hu|%y(czZA{mZ(VyF9)W?616AcQd1I?`D$BZ622N-1z!yx0QP|ofY$_Tz-z+ufEU2?z@@e$DD%d))+2lZ$4idiE8qn91U$l}mLqkXm7uNRtc0HgZLQ`cTxu?Ywk9JXygAs^Pt;$8_XB&w`@v^|wyrW0z7O0B-v^f(h@h>LNC>|jv^9|1;f+CC>u3zG3D$tugy#Wm9U~81Y7m09Mj;`51~?r)1Kt<x1@8-Q1~!2=gO>(vJ)tyQY5{__R$yxbwq_^CZyC4(z5<VMsm;lp|I6S@UZMskd=I$GOVrwgOMOgG=I3(}!mEQ-;nm?!f<53*!dHUJ{X{KH_(|}4KT-b@F10K{nKQSwE#Ym!$6|>Zmhge#0Qf+78}Lzh8+d83R4h?@5-v3*L7A_%H74OJz-90i@Sfn~@SgB$U==@6ClVe5JwH(c5-znJL76|^O$Z;y@si^=790m3hex>7a-@#46tp#*rSKErx9}5isksQ+nv8_-#$ZD~QGXHM9qbD44xa|vy2>>89&i_Y4_xXSf>H;`MF_7B+ImQJctg<EIvT>OfmPtuVu|{Opa+k^r3N8rYZMZ~Uk9hcUxz>8C+ZVV5W*XQwieL{UJ@)0FX<<02!c`vI8F$+H9I+e?}1C;OYjJn+MLWsj{#qVkAd$1x50P7&x8NM&%>oYX6NE>C4_eaJHflbmxAxZm%>kg-@;G8rLJY??roh*_#@!Mu|y3^cz>{8EK#cx-WqHLZw)UA7KfLFOHIkn``a3m@Fn1Texk-CytALE2XrQc-vZv`Cu&2&rM4p|^@0Bg;oHHj@a^!?94|S3FMy-rqwxqI6vQ<_?28%vH)gnm@K3>i;7@r5{~;=RMw6&WzKY}&K9KfaywYbcA^a2Y9Q+gb0MB3r&v1zf<f}kV;r(gv!7F`)?*`8if1~Y&_wx*1?HS%5yqc(h)|d7!ywXSbPVjHyFSMQTKAyp=Jj45fR}ojEJxO~9Ug@)g5WXG!6TThZ+cQ|+GhCuP`O1@1crV)9@Jb)yTfskxKhU<qdwK@Td4~4_%Ms<#deGj2SNd!rgl`6ahi`^=_Y9Wx43{WNzOv*L{siq!c%{!KLioqvZ}5-dk9!7FJi{eY$d^J+;oWF&#4CL^62dotzrr`byLtx8c!qZa%MdAOU1)!VSNeQJ2+st6foH-ydj?B;hD($tUukj*??ih&Ug@)*5WWul8NLqQ(KC3ZXLu*@N}@Dc2ihOvl|CO5!q<Xl;cMaTJ%gn@!zD_QuM|0jx1+rVuk=|%2wx5U1YZqL^9)|$87^@J`K}<R@V2x+z$<-(uL6G}&Y-P=xA6>?^bBtcmL#q~dyMu<ywYbSA$$dR8omPlsAsT*XShTO@|7T`@JDDb$18o76T+8)r{K%rtv!RqJ;No6ldm{Ag+EMtDPHNbln}lI{1Ltc-pVt0xo5b<<>b4ZoWfhuejl&&d7lve9(WS|9{eHCU@^~diDKj{Mo!`H2A&pZ#pv@cA$&3T1AH<3LC@f2p5YS0TY$yj&1o;fD}5Fb!ruYEhra`F<{6a7?wb)s$ybz|!kf~58?W>cz7YJL_zrC$yoqP<QqS<F;H5-Sw8pd-;FUfL2;pymC*W_v8+itcc!o<9Azu-43U5ezK3?fFpAbF|JPw}+f50<%iD$UPCFHw=oWdK>o{Lxd%q4`+0l$UMf!Fs8UhEkzaWVNWCa3WGY0t(heP$EFXMx|q<^Q317Hx^bp3x)<ldmv2h1a9~CSK_yJOi|OzDCP{*Yyk*@(iyB79t9x-Aj8WUg;xz2KY7c71|8=J)XgWp5YP&$ybn^!tbX2243kSd^-3Q@g>@H_+6gC0-oU#1;|%`oWk#<Jq@q)nMMeI9n6NOdIqzJ{GQPy@{=z=Ifd7u{Tg2B^BN(1DtHV&6<*sjDF0vBwTXP>%STS(wP?SJSNaH_0v;p2K$`-;!!wxIGrSg<m&k{9JMGDMrO#wS_$2Ui_#}8u&)`L#;Sv{-?;>&vzm4`pywXSb1n_g>Gqeft8lJ%mJ;QGUFC;EPt4@17Ug<NQ5dI2y6#fdlnrASNXShTj^5r3?@T#<5#w&e<j{}bqN6^N>t9S-;dxlp9a}#;cZl(PaUg;xzEO>-Cj5Zd2i)Zix&+uEp3y9okH`5-2SNe=0gpURf!AHYy@(kwk44247zFg!Kek1J{@k$@zFMx-L186V6D|-fI+M+Uf1breG+V!+Y;gvq42;t9z2jS1dZ}1ET|BG{p82Mu46#iV$xDG8wAJLu#4-#2u&%!Ht2IZgd>p=T2hITFOXYfj&X9(dV!Ts<i4g6TqT#3bWS%c=bZxUSmB?=_vmzr+yU#*?`^y|jzI^8q83@^FoxFDBXl-Hy|?mT9PWAXo>J1jHl-v0o+A7d*'

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
