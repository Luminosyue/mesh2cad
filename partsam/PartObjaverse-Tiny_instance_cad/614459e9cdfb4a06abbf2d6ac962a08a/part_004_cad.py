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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/614459e9cdfb4a06abbf2d6ac962a08a/part_004.stl', 'relative_path': '614459e9cdfb4a06abbf2d6ac962a08a/part_004.stl', 'source_sha256': 'f6c967ea60f762c71efe9f331a02734e6b5a4a48fd96014213a5f50e19f7523a', 'input_faces': 1087, 'input_vertices': 694, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20094119012355804, -0.09930668026208878, -0.40718793869018555], [0.20132231712341309, 0.03911823406815529, 0.4877031445503235]]}
GEOMETRY_BASE85 = 'c$}rZ2XGX}7wtU~#^jvyl9R}Y3>tD4B8VIogurAFIS7V~5Lrk>!ID9UoJ2AMA{tE2Mq&YDj7bKQgL&KcoPk}}|Ev1yJzTfWPlu+vr@N<TcDaoMnkM-nvxZ;!wQg53*yh#NG!?0}%-V?HkYRm-f`^tKIC!*|mR@}I%hCw{z~%uRytEP8*rGjyhX#cdt!67)qgR!pKDMI0289d@={~UAppc%y%5TuU|IlEUKlG>WgM(c^7pqjYqK~aYaUWZ#?f>#uN>>-0gX7K|QGNO6-=%&oF&kCAsnouIJ^aEQmibAalf%!tN_<0WDdqJp_2F;raa#HMm0=F4Cpz(}`q>fLS$uQJI`NI87sR(EX)nI>NwO7E&&a;lq+Ei(`1a*q(yrO!x%jrGO~luZY?XSnJ?BvWK40-|m69!#`X4>IE<X>ffc~_IK)VeuNqO^FG1N2i&0MLcYtRkpNB@FoHza7K_|M8pyW06&=>HF1)5RZ}DCNzDIZ^-eSSfF$FMxiQ$&BktzEt|JC%prIUTXN$%Z-!k8smRc#<8o0`u7bOBL34b@wHZ8PKh>bg6k@T>vFb)Z`-pI{j8l=>No2B1wU@OT$gDMm3|uQ?xUXG(LqxF^KPl%nK4m($HC2VUHXT+QeLZk1Lc1WkonaP-NHC5z97DN=lT+NUr%~ge0|Ww#o~|u#lttVrj>r0L#v7Je1A%OBg>y7<+{R#U>rhDqTRXo7l=RlcU*7oqv&Ucomih0Pvd&i|BQB<MM!ylz&$B%Z+;l#kZ@;~ly5ayuFF325ZZl~1N8)-!*%^|5Wat$^j|-4RD4IpeW-s<A<Rqf#nMl+{dV~C(@6c=#sN~lEi4wkQ=2N~i{J6|ms|{&`u)pdoRe&Ze^r|&eva2zw?)^Y|0iosk$Mi^M0xt(`Wbxun!B&BNrw4)`YZ0EoU2eiw5B2T<i3P)Xy-uv>6&8wgmB%?SdMxQcONF@7xu(DwESZ0F>dcL{*F8IQGc<i!QxN)8S|Kf{;`-4>8H0He%pEQXEy39<=X~g9Zs8tdH)dIPv-q<IL4X2S!fW}RmcUjJ0=YE*yCg!8qV9|+p|wZJ@e=PB<*&bD)s1r2K>k@U8Ve$vAC|rp{PHgJjQJT>T&k#h4NqL*~MQPE9D&xy1>t|uATfjzs$Eh{8A}8N%@KErM%tj1V3Z?2GXvvLVR2PHt2tnmeDc}dnRJOK9oTDc}p^iI)0G)jSTrQUpa<HN&PRgV4a8OL;rKVSS0?xHt~(9jHv%;Tdb2?`NY@LXMo??XSw)kw_*K+eLX2U?RH(MFYp!mx#d0lHN6Am&vk!>d2zfE-}pPyE<aEG1LZHh6kq>%QR>%H&&7Dg+(h}1IIN$ckI?RgOX8b@BV>QmbGAeOkDW(7FG}KiFZUE*YZH%pj-41Le{R_j86W$UBd8~6x|BC71Y>+Q#)<!JAGYr6oy)|xjjSi*V=kzVeWr61u6OXk0n*OW?il~)GvPnzAii$Y72muz1%5a0!J@NjiLalTh<>&iJXFectcH4qjzjsUK~moA+zS2oAByr@nuee~f7CyI5X%2}dARsLHTUqH_b$plZ|xh-q8(BGQ(?^e%0?KsX074-y&Es}#BD==_WQ%%>4*BG!^GFNG=<-D)ktY?)C`n&G(taL7nXg`+Q;;E4N(4%!DHp;Y$)%XUI#v(v-+V5DBrdc#(&IDvhQhYeZ_aYOas4oz<lu+SHphQAPL&lDvp!-n(mhRZ6y;<h@N^a<@FzmV81<cReZx4H(APedW3oLHN`h~j5Xx<n_tECR&a=~wb&=mBW+J%tn<gwsQ=KuP+2GaE8xENT8Q%Z_DzuTqbp$_D{H_%K6aveyN*Yp=ue6_VNyQo6t4IDNcdM8Px6y>T?PB(rh)K3j-4V}&+E4Ie@-LRzxZxrDc@)NO%K1}{GL*OmV>w-`}o1P_QU+xpPg$<qyCML<hf>SID+e1ToV59F?e2Zf42GOfPc1@T$kD6HLh#M`{N$tTs5uqQ)~BBd@VA4KPf*f0OP#y3Cd6QmUXUmZi0Cn`w-<54+Km3`>k<b^tcPZRhv5EXKaLe?j*opmr9-&+SEk!KmG>lkC-t;et-8Ml&^UmexJW&o$Jf`;65sQ1@)YX>My_FcL4fx?3DQWgXywP^!x9z{!_%Do_tRxh*o}!aTp$ndi*}NK|5X0f1e2WGn&bLr`LVy;Tw~;j1X;q3inIrxhOv{EL8gEn}~icnS=h+ZZ}DO?vf7cVRksmr#~R~o$3EO`kC8~`uEpD|9}39aY)|<e$Tfu{$?!hBkgi?)bsZ37|~}BaKE%paX`wQySNGW{lf$`-p<|L@Vljs5lwbneC^ir{kY#(OL=pkmZ*Gt<X-X3OG7rx@B5^Y^7aj};v4;Lpu7$B>+Lt~cduV7d0KpPTqOLt@lsw-`Wo#f&Oy6fC&C|)UE0-`wuN7zpR{Wh$e7^a@7{*%s^cZ)&Ddt*>(y;&w_-f%Pul?HTg7dW@@b#{=I-lL-lPBJf0Oc#ws~<~8-EvHTmA^wdnbwb4lQwyls}O*(cRa4{@EdZ*h`P{-}+xatA}rXjh22Iai;jT*&6C^*?+Hl{rbwcaZ=B%JL2oXNj-cc{-X59xL(M^Hye$>{O12P!NWf?W|Mn)E#M#cEAONKC;!Dd(f$_S?l%Jc`A|&CJ2U<f=RW@C?&PSa@E!QIz4nR!G7IMA+D-Ix*A9$-(tl+99n-GGxvwAX{tIc>sC-#`M~nMXk2d+Fhp$&Q<$Cqwr4!wKbH~jc?&I^V{G)ML4-2oNp2nxexBVR=*QM#@65V~X;#-+7{aH4Q+sET5zqCHbX{Cqn@Eg8c{Kws}-UjZ*bp-{X{k!8le0$q8`292IJ$$otDqL^v9MT_~5rgt&lH<A}{<<aOUv>k=Ic5;%H~VGu=iVB$=Qk3+pK*hy&vDZl`y{&iHm^HUzxJ0m=C@8X`r{b1*S)-LZ4~O+unfQ7aYBN-?|hvJe!WY$uE2;m_xn!U@*4MD?=Xzp%P&~ZBQhnr`+E099{Ywf+cb~$X|#Fg;cE?_VEr6<g8TRMB>1H!LVY)T_}2Yp?6M`g`}S$^xUW;?!+HoGj`4|HhkCA0#Qj?%#PfdaoHEhf*IypOK34Td)F0gsehv-u{s#A>ZF_grb2O=3uf8<_^L4Bp%55sROZxNA#~V_fzBa1NRw@7aos6e#Xd91pVy1m2>qN8s%yx|5{*7q&YIDq2_nTO6);>A43CdNCME|Gf$9nK>i2j_Nj_dHoI9R@(^)c4}?qqkQo<%z9&sP%teX%;h-Pdjx!MbgJ4$p=6RZ&m18_+B{?zsEb^XuEb)S&|Aad-#RH+?+nNm&;2RqHPqH{(KE4_|MdEmrhOTGTT>AFgZMWUPnR%dX1!m&uLtDQ$QT%*!SHG3I4Ke;&T{SZ}shX>q-}H=ZX4=VD&=czMi=ai8---x>!!`U2`X^$z=HR9VzhCC?oXf5sB*OWRYT|HWR4uXnUzon-xrb#m(&%BOFN{{J0@`)=l6;v22@qW?wHV|}K(xX=B1t#<80&cKiEgy&VG8B&ik|4H~mb?h5m|CZ}A=^I%q$@<i0{*8V9@-g(M<`eAONebMS@{^D3^BDhZ4jF$teOm*^ZujxGNAAIT&H4oM(=#{x20K0aZ%nH!_3QMlaWlT+y~Xma=exC^*ix)RyLNxiaXYXI<x@C4-XCnamhE$&NA0I;sOQ|GeeU<KRxOEqzp8~U6yLtBCB`$+SNf?X&i3qoZnSH9kMSITt9+Kh9^<A(tj4&F=!5#JU59_S;!O|#YfI^m9`>X7wyK@c|9-dRy38&wrCnobAja+AHXiL-zVl%P^mAo9)RVTp=Q#5{O*>NCqaNc}CzQWb8STC=j`dc#BCe}KIrQ`L4(zK*V{ly$N?~63{58sL65mGOIp#g~?GYJnd-&nq@!V{iAnVhy-sW+C8O64ue)`VpJ<y-1&eBgaE-S`Aq#oYmf`?y`e&$S%{uiu`^0C3<JI1E)n6Gd3)7L%}_UMms#~bZ7Z;$$Ob(D6ETAwk0;lZfq)c~pA?)5@^NAdn1_1iK%-0MD`TA@JHQ}{QG<GIUNx5e<h(68U{s7GJZSL%08yDGkO*#*4s%`JD+-M0lA9?v7kW^=E5|E+nkTmHf9*!PY+mh08&TknC|#5cIVIv?KavCeA`k^Y#S;G4b`v2K@rmUhhxvFML)Wt8u-5$!%30Dn;_?EgP&=>H#eJp03a*wMe3_}2ccRey^8x%wY_JnFgk1L{e4L414vte*Gvm80T2GG4>{AJEYM20O6dMXtql7mt#D8t=BCp7=|+kLwqg^2WI+yvHv-fOR^gnD}~V1nS>E5A!@}q159TvT&9BeEdAFtM58I@Amf>U$6BT*Twfhd#+yM8;94x=lhi-sFwKlKM%lfcMAJh(>&rk=6Pe@H{Hc^u>5C-{CqG6=B4m`?8Ee}&p}qZ#@MUk8--8f{lxmbxj9^X=iX7cFZlV?7&u;h>$#?VVEq?HqMpb#crJwO!#-^J7nY#i(GO5h_5k#!+fga6J>QS#SG2GAj*r{XpX%4qpKj+?V%?O*dVDq%`(CM;;_F+F<2~o-0j%2*J;XPwG{w9`4oCUn@b$FicVd3RF`l0ritl)nUVQ6wg#G%(6*B(2g5dX?4ZqXg74GZM8V8-eUfza&+K(l;`&!^cyyrLA@8R3}Xy{LhSj_wVW#XHK&SHP+d<^@>nmH>x*6nYYFUxn{Xd(3&<CdZR-V;~2kAqQTB=++X!_c4JBloz^yZu=&TyM&JSm)cfpdR{0@8MVv{C+?WX@+($7U4d@_a*vTxd_ZVKR-G?loS8k=f|?~xPRZnH-6uMeZ~4*e4r5O=^TT0FWtlYRcJPhL%pnMcSU9o-}bB%_J{aC@xE&L!_H$L;Cr&=8x4Knx7dww_~A>m^fT#r>=WyM;pdbW;u{rW@xD1DNcKHF>^}TYwczvf<~RSB4_MC|c4EGoT@&9vu^{H<>17XJui6;%7_}DTdF4Q~`}kPnY%bgaU%QL`f0&B<rM*LZGa;1kvsJmzL`1t^ud!kuuIuhp@ip@hp5tYMab1p4=+BK-xUSSa(a)a!;HNWDeqVXK-xlpEzHRw=>;ruc;k_lcZnXQn8#j*QIldXbae6TB3+`{)ph}+OV|^Z{|81QQb>O<n7e_t&=c7M?H9UN)U2A;weQ7a1Z=+HF<ulw5y-@#OSMVO&t)g6)F$TWbp#b_nc2|PCujTxLb?&nr^X2tu`TrU>ecCzkoi9Jj_~`bd*sthY>&-ZNFu~n7y?bN-*%8U_NscUcpGU36HM~F2|MvNjpNlQu8c%)JQOtYlo$xm-h2Q5e?xPE9QBTfrte-D6J$&PCGK^>U7_7s<nakbRj~3fo#!ZXvvE2Q>Fiv(#aQF4~X|V5E&m(&v{MDaOp6~NIee3zF9~y=7n@VAPmR&@<qidpF`t}<wv7dyG!T!GyzQZvX<sVc`aQAIX_F*0;CE~jJ+0br8PR!${Ko8$`sSws-sl}*g<dbFM|C$l+Z+l;$|Md08jnJ-H7UN$n5&oc3ScmCzV|@O-h<bht#`7i9Q`yHHN8`n}H!Owst2J%$oTdNm{lWUaWzt^p9cw3f?8D9!%TfQGS6C-c!*9F$dMN|_X={k@_;n82ZT2hXB_tz1&vp=BD|Qd}ONJb{Uv9#89BqjA&ynq<pLY7z_*kDq%`SfEzqOAoxq#0jzZXJz>wWT8BtD-$fbaODtmi(z<Ni|lIqWw2<6i{pfxemKO`Q9@*ghQ)|J&!viHq=jq;K_KZ`vN8mp{_)aSiWv+?Nc)fqE|Q#QZu(<9&Dn{BPrCeLhV#O?+$rw4NjOAK^Pzf57|9Z}C_^zl;)JOO_J-KXe8A=Nb5hZzVjhpI*XvhW8WSIcXc}&+{wZhcmWZ>b`!g>(Ulg@)!p_a4|lw<;jimW8dQW8xn{0<4lYC`MruYzXpB%`f-%scN6<?@kdMKx~|mR?>@iA)^khT=gU|%<%YX&`*H@?d$BdfXUGxpt<SmN`suq<d~JL>`2A<1d`0-qW@j;;aYr!z^c|@;;JMuOHulNTnM*v@bCzMKM-N@%K0c;?3GXdQ2BZJEv%=ps2IcA7?<V)?r+Kmm+U4gF?ZG^JA2K5l{Y)5#_tkCV#kZ%cj{flTtZ{HQ>Q4*bdFKW0>zY5K{|jwPJnk2(KkYJk^xw#Q8SAGle63Ll>@z7};(M*2#KrFGR=?$s`@IKz>-&7GU3-yB;@d|4j(Kd6_J+G}eSc_7Nsjq_9KYE8x~%ckH}75SexDkx`{48Jz)h&f`W|LLi1^NO%f)xzOhEa`Hr#jgt?zU6pt*RTc{69R`#RK8<34qa9)|wR@W=T77K(LMvp25mU~ZHja1rA+#ZUZi-y?N+E#u~FRDQAh`n1O1VfnltwI=6oy8Fh(qPS0soW^~cy0Aw-t^V8Fd|C9r)|(^S-{M=}zggp>{dQk`M~8wa|7aG<cRMY<{`^nu8z0fGt>D2$?(0_5!_jU5_}|{^W|`QR=$pT$^B4zhqr<a5ysz#3A{PCx`&vKeh5r0!KXlH19VO+heKpB=%x|XKQSSY*-lObmXGVF<Bkv>ac@OdJ<^hlL&PvtAxAq_NO;NPl{8FU+dF}(+Lp;}PQJW$??u(q6F`kj|t#-{x6L9~o8Ycd?_s`Y8FrU*;d|Q{w9{to0q!izJpD}HIxL>B9Ug$nPdeOe<=Yk0FwUrM&>mQI?{BQ5Eld7PevgySC_Bn{<Z8dI3xYuvJzZqZ8dHCj!mEdO$65sy&MvwAl><!6du#I~y`5R`^ig%^{uKUC{LKcn}e{wnT&8NMPFA}p<@*=b!E5YBJReWdD3ZXJC-ettMho_Ri@7F#Y@GM{BiTu63G49GZ`PnEfzTPL(?OLi_>0R)@mJ;7N9=>inEA{BpQIEaBdui{#_1Ge_OTYiyuA_P$`T4*7bPO3F{(rB_IJjk^-~Si~J>_}v|2uBZIjxUL`Ltt~i+`si*7>1X;+xOx$lp7U?>(HEbH~fiA2UgLeRd+&;e@>KXT~C*t>6MY2XD_4U%x+9d?QV7_*349Z&WoUzstBX2k(I+8XcG4Z*fw}o6R!ey{MAE_*R~S&O8TmSQqiFya;Uz^CEuk2A_EphLuP0DjfAN??P*VybIf?+2UJy8d_K6Y1sdrgYwMl&?+IX!#OVkKJ!Bi=7(6ml^<d<Kg5<T66Kj^VlvOf8M6uHnU`WRFU5@CiSq4sA^+`7Lp<M$oJK#H-(oPo#di5J$}=CvWIl{z)pgX*{27D!Gv9pX+vv=<G4({$!~7hb`8m#$ci}UiN6UnK9`o))_{{&&9w7h6@%{<N0r^5Y^Mx$m$}iG}BfrSG^o{t=n3Kp?U+9DVs>FNL!#pLOc}k9*IZlYrye2IGc}+&P{P43Sll5t68S%MeR{{7J2Oz&LXak<VUrNGf-jvo3c~kZVrQtKr%4D9EqpI%-_xr`T`VN2p^{b!wR=$>D<!ila1fO|dCiA|&`ON#$nfK-FHBfwg!%fMnH=R@Qy>!|^XqS0qCiBYd6-L2l9-7HKG%YL?KJ(Ue=B?@JCZJvBx#`Sv(|Rq0&%8LDd2xEf#i%DuHk=FS<0t*G`>zn+%CFM~AivJB$bov8kEb&q&w2fb_*VX&$^1P>->WA)=9m33&)q@&%nvk}ALxAKeG>DEd_tZ1g!Z;+#kcYgb><&x%`%Ix&DkvDY2<8<`5NYP(*3&hn3V9}`Jx`?H|or9wDqcudYBJsFdx!+umODLPa4dh)RH%ZUouMaoXy@?hkDY+XqS1I2J<kD@FpnFyiIL1>&e>!KJz?H=6M>=TES;tsL8xg$E=R<nMZ0ckJN4(1fTh+Ci77(-^xcdtbEiLA?PRbT21D)YFWmi9_GPnU62Rs*kGVM^JcY9$eY!xO+|U;+3L)*wY3h1&%9iNdAY{Fk?@(vYch}5o^3hig?YbP1oD3EY4)T4%o8@4Cv1CsM0_i+SgVM<Vn<v&`pG<GZ8`FgZACALZ{;oP%v&}FUqU_1b2h9z=XAGF5A&k6Va$uJ^a}Mbk6LFQwXMz@lxN<xHVt{#W`+;AUgl|=R-X2=uke}It+i!d_wWp-q#ovh8_WaOKV^i^ym5nh<4&J^;#+y<I`hn(FW_5w={ob$jjkodxANF^=CM1+)<*q7X|NBB-HFeqg`1vozrVEVkMQ{-zBS4-PhQ)LJb7pLPAJd3dXste`sOb1nV+xe$j|@gGe2Kve!i_qFns3u>&)}li;lzf@?3y!oeS7+pghkJnASOh(24M^eVgYFY<I)Zf1Xn?c}_tO4o7*OcQAS0!SQ4k+U0o%o#!2#73ZQJo|~|qFShaX;q&~3Hu+~ypXV<Op1*MPS|+}AjzfFTa~w~X!{@mVEfVKGY#&x)etAwr=Q$C5!Yb6yb0u0HoGUR-uR(d9ThR{T+=_#~b#BGrxfRQ|&aLP?x8mr%89vX;So_;IpXX)1?K96};q%;$Rs!d4^uycX^PG-uozuC#7e3GRXg~2>&$<Ji{j~OhtOqeK=en(tKNnwF_Ib;9&L1tlR;~t~vo8*z9-cGOdhwjm&chfVo=ehN<6M&ETj!Vzo@25-If8nMe_bu@e;k2!>6>$-q+RQIs_!?&w-?O~ztTA53H%J-IzOfPV&0uE<I(QeGU$J(59)7u0_&6KuuPuAvUfg-c1zxu{%Fqz;_t!VpF%yA4`Y0;)<(NsPNV-k=VkJommc&B#%)wHw0nCZ@)Fm>x6X@c!*E_q>w6aU^L&}k^JT{83n<U?XgbfMIYwT`I8Ql<aU0SD?;AJaTj$!W@>=Gbs3+Sa^uKx?l;53zapU<ogXiOHQxkDrzl@Xe#%R7@&AN|vqyI#^0U6<^e1LX&{!ZulJ9EJw7>7IBTKWASF>czXzfcd)@o7hKj?eCRj&aC45B*G-jQJY(4t{)ZY1gRV$iuh!Cqw<eRL8vh^BMi&xk8iY3eCM=P@d-sb)GBK;<eLKj^`7#XE>i|KjwYfy+77^(>^5?-_~yq#$n29?DJkJ;jjII{s&e-f6Ap6-#Qnmjm5c0M?_}$)^nNXD2>NC&@Rtinml)DkIjjG@|>p5bDB0YpZHqRcdMkHnuRew^sW2X3>bj-x3mStx6Xm;JO}FdS_J){TLSBU`VD+PT(mgqx6ZlnJgK?bM|@+S4bQtWy_xS(0sZH>RFmgYoskt$KhLq6Jjd#2R_V0+{bhX2g?_%MF1{n|A>Q+guEh6~W$L2*gfO{Yvu_g2%d^JlC(qC7JU?qc)Ew8#^R`+5&fA(90^rwMgK^uk1K%ssxAqO|ec0ZlHOhA{f%+#QU(0c?EykJWd<~xSH9mI6eDPec$#cParXbYMbHv&To+A#1Z|naG*LyDl<KMqGu4_P2^t04me7{t?KgR!ZS@dUApr`+{uawtg7vQ=AN1+}wDfXXD^Wc{VML!ocL4WGD@$hx$bDS@JIUe(SYP`qzXq%p({MU(Sck4p*$H&C?T7F^h{f1y1rgri09YZl+X21UEf0~)-k52=v|J!ph@Av0m{KvFIKV!CGd|F4MKhsuVfAHb@$sdL5y>MRM1GRGZZo2!9ox3m&<0Dc3ti|Z3_5Nn9w_6*~Zso@Eo@Nxhg>jg<2mZ1z;+t{Tab2YjqMqFAupVZzeC!$Y^XL@p8^gAuKjWX^ddI|LekWhUx;mEW490Ue-shV|q5SVf#W&MTmh#%ct|&jXiTIB8C2$UL8_v1g{%&>#>tF}wWhUm)_9z(j?`nl}=;dDE`|A0F#Mhoa#yRM&JyE{fV3cnZhUZaOH}t3fDDj<Vr=$LwnXw=KJ_&wizW>+Dj&UfzKzv&g2kys`Pw@To`3PLsl4;nNTGYh+W?qSQTdY7m<(r`0?GEwn9dEC6ug5ul70UDczQ*(W=G1k#E}r){=i<D-ZRrk-+w&^u&kG&xR@#OB{E{5=`%7c2hnoA)|C=4Lt`?wO$E`Tj&wppY;J-7V)jNp(+_9nj0Y4943#@_q&AOP!t%osRnQG(v#;M*YpTk5wS>~bqo5vWpNAUH5eXu@Hr$YJX$5Fq3QGCvdt$fojz~f(YNZ-KUHmri{O~e%`w9Hzs?r#5-gEG}GOaJ#j<<O_%|F3__p<LN2mH*%VEr*o1yfp1MSKMSMzD>PDR+>n@O-`V`BPWm_GZg>BQ2dsf!5jRR{E?cPtU~d>UI@iMFchbumL;blm!XD|%aBJ?r;|sMCsV`8lgVM!1>`XDENT>a7I_|Z5qTbYK11<rY6N*Uc_wu(S?LV&O!7pA;*r$xWTnH%Bgq39ii4;>k(G8O2ayA*?Z|=TX4IDCX5{A7*5u~oRt&}MsU68mdyw0c?bP06J2{v-fE-NjLmf`;Lmot(L>@#QM_ouBN1j7nPM$+vMs<*vkykJjucdAvuO)Ay?j~;{?_wz4>WcN$oz&gro#Z{#9b~0j$a~1!sY}U9myoxUW2uYDvE+@^NV3w^<c;Jt)M&EOmE<+#b<|blb>z*|_2l)uw#^L1+o*fUd)V)7)L8O1atw7Nc_aG~LtRH+$2Ma4XJh!Y`sLb2G=(=@aLpCh8H%q`uaK{jFEbQhq+TK`Jx{(!zQ9oYEA<@tSMpivFXSw)PGxpQ0cu{d($eGt<O<Z9<O<}T)F$Mf<o?tS<o@Kr)b8ZL<e}7F<e}tI)V}0V<gwHt<gsLfI)ZGFr!W*xV<?_V4Ixh@Phcn>L+wW%L#|EjL{?*{#xx~EaWZOhveK_!;ACWPZ-nAEUeMQMr4Pt&$bT^u|H)ANka~~&kbIw^_z&t`vQj7c5AqA@Bk~LK2kLY32eMk+O5c-}dU<ovdxKL^Q;<`U^HH;s^N|ZvZREn_64WB(66A8!+T_}t7sa8jZj5ooc*Yock3=Y*KpjG!KpsWyOCCiIp$3yf$o&|Kdr~`*dy>0Qn~=MZTT|<iTaz18{m6~Ub*a_Jb;%_(T(7#$(bRF|(d3Z~#UmJs`%?#ymG&a{CkHVUccXSCD{VvWM()f|97t_Q4kR~aD6USeOs-BYMa@huMb1x6PtH%yNli!2NzOt|P0m8jL`_M~M9x4>PR>A1OZ}0YmYj;3l&mxfS?LetROB?&WMri&$Z5zKsU^r6$vLRi$WLAO-S52DbGX)hZdc@FD9%GIM$SVnPOV5TPWGi%A^Vc6QEQQ_k#%ZavQBP9ZA@-NZoyF8mKs1-+J)Sf+|3owT-Wx*6|bm&la+oVzaoF3Ch-P;At&{QrX?pOr=#X4rz01nmLwM>`%o*9eaKa*e&nj;`qVb$`ec7<H*z;#uRlX^Q-<Qs)Btj4azlpV2Gqvn#+-u&48?V*wa9hIHK<j{HOQ42ipx_gl9d)CmnRpc<|Y><=c48y=OSlwMS5x`Y7TNHa%O5ya%OT~Y96xE;^e&K(o|n^X>v_!HF8aI6RJ*bLhe9qMD9TDPHjQ%PVPl*OYTMPOYKJPOCG{dJc8QB`}=!}(tZrZov3ZdO8v;4$mJM{OHeD3m6r7W{ybG&n3~`F`}0?^^^8`WikjB@`!ij!MomK2$RBwBeR6w$_{8^%PrQd;P@lNHdpzO0iPC3o?<&vS-fa{=Whj10eMNpr{!INs{!ISS8>;pK#Y)qWe<WvQD9+AMT!>nbT!>tX>O(F?u1>8=R$8B2om`LVPgdHLJk&L$16?tkp?EMuaUbeW<UZsc)b8XS<c`!1<c{P<)CS~6<XY64<XU83YI(9R*@s$;>_g7&iWaVD=8EPF#kHwAxi+~9wGz1sxdOE;xdOQ~wIsPTxd^o&xd^!cH7{9dE^+~K9){v<)U4!e<b2fJ<lMa8d<?}!8H&qM%ahA<9Lq5j*Pu2a*C5xYb|BX$w_+%6$53pib|)+SiEJnLrVb?cCJ&+xB@ZGGbH!L{D0L_~lstwyoIHj+ggTh4v=4a*xi7T`xi2}G+L0Vg?nG@w?nG|FP+X5%i(HTFNA)Eu^&$I_t1%Skpynp4cQ*BYmWrB#oP%XjQL}2_-vbp}?~sZ!P;+VD-#Ha$qUP1UzoRP7LM^C$f2UQPlUh>y{tm1-Keep({he8HDQYF{`#ZMc>Qr6({!XsADYY3{X$$T9`@CZ7JzsGEwK+ME+SV2AsV%7i<d$TAYICwbxem29xemE1wF+5j1#(q#MTX)s)Y9ZK<l@vK<l^K))B<FsdB}yxg&B&oQ?rq?lWo*|WTi#PHC)f5%C2a@P+Zp)HNDh7H|5$J7>X-W>yqoTyy6nn($vc2(&X~g8szfi>ePDV>SRAx)TcJ0)+09}2Qm}~P-~ED@OlCmiaRnCx2D!5w<fow)+V<kH>cJlHzzk^DE4P4u0t(Hu0t;4iel7~)N<r<9J`WkV_K4-xGJ?YxirVIDz!SfI>)Q3+c;KbDDJ^f+=AMO+=ASN8c6O!?!{1Srv{J%IKFm<;-46bgQ%^^LFBH~mgKJF&eZ1Q&g4$iX5>!fb_~Vsss7~l<US0=-5HA8Fcj<5I^;T>C!L|#hoQJALvazeIaXYpT8&zaT#WNtjarpljog9SgWQ2U&=td}eW^XjJve`T8Hz_xyO2ka$5MNd$C3?(;(k;++0MD_$57m#8bl7_{Pm}HCU@pM^{2KYx8vOOXDA*(?L!_w9_@<d)EU%1<Qe4g)b8Z*<lfXa<Tjkk-VDW67>Wx}eaJqX;{puDxfzOcQHzjsk@I?eUk7;^iVL}-EVT)>I9X{mauae}Y6o&#@(_mNQPhECYpsl8C?3a9Je{F9l-if9bObq+JdHY*JdGSiHOOJ)Db#-Cew^be48@bE1IPn7uag*x=P?xT^7_6G6d$4Pr!FV&CvT$8Aa5csp^hgnA<v}tCeI`fqE;afBKuMckbTKEYHqTPoSmABoSmGNnwOlFoReCJoRgg2>-!qY&rn?06_uz>sb$Gc$-&enWTkD%!Q>F?5ON54DnoHNbrf0YIC3~Sf}waBbvk(&c@;zP9BL?8=``{jawIj397&F%P9ZCuM2;daqRt~PB5z<QK0w_?w$|AJhT`L{_}LXFTydIuihP=UhI*WQhJ2EGgnW{Gl)9gMlzfo7iF}Z}o1u6GbqRR|c|LU}S?M71eDYwbFL^Mz0@X&YK+Z$WPR>KlM$JmjM$SUbNzOvfLCsIjLC!}lOwLCx==FVl7i1_dMQunfMXu$F#?)5ShU8Y{o(#p^sFlb{o07YcM^b~yN<+va$&;y5$&<-*so~_g<i*qo@?!Ej>N4^=@)qhU@)q)ThT@IXIb@}g<c;Lb)F|?1ax8TbS?LCHEO`g@0C@-5q#h?LJw-Oj@zfLKc=9oZ;=|OR$x0pM!{n9Jq2!h1VbsRt#+>hA48>!pJ;`Ip6B&vpP`i=4agHZ26wjhgCQs(P&SEHDNL@@`NM1@^M_x)^&rlpg-9nBbZ>4T0Zzb=fZX|EyyzXQu-b0Ng$8!GmFcim8O|r>(ieo6=M?FT~M?OS7Og_xHImA%BmO6|)jB~J-p?EfRB6&7>0d)d-0>^p*bs>2Hc@1?bc`3(t4K;=w!*N{0P`r)0lf08-w2c}^j^p)jV<_HBJw)D1j;5|9ujRExQx}k<$*ZYr$ZOcfYU*C{X4mKW4X)VBP`sU?cq4Tgc_Vo>bqRSjc_l+}q$}o9BdANr5#)u`W#onA71Ryn738(l&E&P@^$f+^sC&uV$om<Jk1`Y=qHZT2BJZSbB=00|rLHD#CC5@%l4HqR7>XU#NV0>x*loNPGZfEbC|*a6AV+Y#)=^iGS8!a`QP-2#kxw%epQmmkpC@0T?k8U%-()C0PCZKgg?f^DlzftWjCzQCjC_E)lYD@@kGhq-j~qvhCC74n;~0u}yJ8nLhPs6uLtaI7kXMnTsEf%_<OS4u<OSq4)OF+|)DzTo<aHeP6V!|36J)0=9#OATFOo0v&s?XTCtoMuqFy22B0r$sBtIbk$xwWkdYo*{<z0s2v(%I1lbpY^)C1%LoTszYIC324;H=x+oMk9J$54Egq4*RvhJ1>An4x$NbrpFJIhq<pjwa7xD4xww98O(84kyp2t|41<JfER>hbt~oZ&QzuZ<Fs(PmoV=j_)uOztFy~gBJ|NFByv8GZa6jUMDNPMZU%Pe#}t(oT2y?^-uCEaw7FE`7Y-vk$R4tNdAp_mHZp|cUL^4-lJY6-y>h9o+4i+U!Wc)ALhJXU?@JrP<)V~cquiSyp%kXI)^-yJe@k5Je@q1p?DfKoIH&jMx9R%BQK}!ATKAI+V{0$G8A89DE@<?_$l=^`6>Ac^$uC-3-S~4JBH#<)R*K><ge8C<getUUI@is=shMYeNO&DR>`DFUy)TPenT&jtn@eX8}eJ~@8q}S&)WAj^qHafM_1ixy`ZV7%1_Oo6?;+dkyR-Eo8D#e-{gnX3*?97`_wb!`{WzcgXA0Jc<NGeJb4jyCV3Hg26Z}l26-}dDtR(_B6S*hB6$)uj68`vg}R(Pg*=ODl4p@OQLm9Vk$-l@uhazUHL}t_$O+`X7>fU)J|+J{eocKsR{D<on*4$KiTsiJFZC1oU$VCs^eb6~;^b7drjs)ir=+TNoRX^1Psw$hgsRqS66#yB3dKKAKa*7`PC->`GzCL(DzESBI2A*223MqaMMhU-Vkpi`%|On;@|hWm(@|5C(~;9qy~t_E$*AfcP#n<I%R6(D|F8f3>i1vj`&rH7f5!UXKk0eY$Nf*9ch&Xn;7>r)q$(#-^LG8G{!%?u{f)c!e*i>Oxw8'

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
