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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/47e55754cfde48a49c3dfe12e393dc18/part_001.stl', 'relative_path': '47e55754cfde48a49c3dfe12e393dc18/part_001.stl', 'source_sha256': '1d1b5f9358d20318cc3ccee6af714565498317acff9811e89c677b3589c3a2a5', 'input_faces': 820, 'input_vertices': 646, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13265173137187958, 0.2723858952522278, -0.029083633795380592], [0.22445420920848846, 0.34575459361076355, 0.08249543607234955]]}
GEOMETRY_BASE85 = 'c$}@B33L?I+O;bInFK^chzQz_1VshpLgXTpppYxGqC^BN=77i$5CbBX$Pg4|h7b@7L<wAECWNsob9blH8A-yF6oU}C$Rr}7;@|IicO_kA|KGanTOVufwV!NHPMxVv4c%Gx>shUOBZ>b#B1P_LHl)Fel0>R2HIk-{ikUig#HcCHPM9=3L~0;%`e*vGK5z8y_g08BP5Q9K$Wc>9#I)$>XwhkOM2l9A7NaM|OpO^f;hl*wBS%r*ec1RZqx|`l=wXva`F{>?->!Wt$MY>)IX-gyFaOo?H$gdgTkk?`DY<ZzT#kNqkNEjes}yo2Gbx{3ONw17em>Mz<Z9+#TP|D5OZ$>7xm5CtsNXSmhNxdV)XP#{-sckK9fwC->eu&GARjMsN9K2&?~O!0iR;fQ7rEkzUnBf*4C?>hQoos-^-IaOL@pnmDstm!qG+cS-FXk^v6k|3a;;Td&u1c+OG1jp?~VPA`*nCB+PO!RH<H6edHwKWOYYboA#&-6X33TPk;u1kdoqi;ygOX<%W))$kDIxh$A5nm*MFo~<XXwyqCM(3pJ<P9<P64P7uSCvj_Y?`MEyBDo|*9p;`g0WYG8T!VDc)?>jcdW=i`=KKUiwXwUS0WKI1O)c<Sw~^&Gmjit|oEb47nSmB)WSkHg{cc=5B|3%Qfar^c-o$JhI$a(^<o{E_JRz+B7BwB(vTAk{JsN8&_o=z~&uoRc|sx<oFe3{B<rc1+}|Ga2PaB0tOPN-q_;BV{z#lXafQU#}3koDzfl7MD+nSZ&RJv*eDHsoc(z2gP_Q@7CEXJY^d9H>*a0=ub)%>WSt4X4SOiGm+mbaz|?HYOY5`Jr9Un!FVbub1-fxJZ|Z?R&#yxxSbgjc>I&%#d)Nr#EIPDYQe`%jbF|ALZ07@_j%ls!+71Me980Z>cH(uOI{tA%dQthE+aQmmU26bOL)H;=h?&MmvjBD?xMV!=0f?E-2RMDxSd%4dP+R!uGd6)BdrwWHOylLpT9*B>jHDbHNa9{N!`WeGr!^U@o*&1Z)!5<?t$E|^a>vT)Kt{-mL*qGGcmsoF~9n|4~h9zQ+-(HY21FSA3Ze>>%5fLl`n3sI9{58`iENTccfKV)~B8ljr=;7&$^GxPo27+$NL8A8P4kg^Dd{|;rT5IwXVao&@|y$A(nYm(rTpfIE=E?qo&mfn(JvzMefMD#_Qx*<kx|@k=0z3m(1}@Z=DvnPPFt|36|VF-crAk-j3@jJ}cIbZthFz?M1E@MOpTLE&XNAT`%!*Kicz6U@p5SS?br)Be{Op>%30V!x92>**)1-elU-l`&~<Jqz^@Z>vO+inu&SQ(-qY7zGZ%;jM2!a1<#AqMZXkW7u1Y-+%NY`OL;BhOSI=BORi@u<vjn3B2n+~)LmSDxybdS8+km<>tIGa>X{<y(dVA~R`e$$f#=ut4EHN`?FK%7)`?tmtCsW2zyBhiYdNpw%tPF-qjPw^a9^QjrsBBsE&GO+nTL7l%g3G7YGYuoxffW<>zM_}KjV3+tfz?cf-*4<`p9v+MZKBlcpQpGSni|btc!eH_a<IHUsg}#^F&G)KYLpj3g2*JE0+&V4;(kg-1Kj`d<~JyMcqXG>X^pd->mu~*WD|zZ}WbxWi{sdJ@J;@$Z~M`+=oQ_)gkM4a{eUeg^!B*wb5mwUy|$DbRLH_JpP{#*d*$6bxP;+^bGHNcSj~TgXBs^WI|wh)t4^%tGu;z2cNf{`M4f~`@6F47B1hF$DuHU+cRq2ZaxoRMZY%ieBt`2yZUjSGnwn(T(phz0X%M5fAaOTZnS8pJ$GbA^Lgrell$vQ=XJQ`QX;RL!Q9S*(_-ATkwbTL{X@~7?|7Z-VSL`X71Ynyef{nzaa_YS8s&LCsCq5lhuzUUZu#Rx{faVZ7uPcm<9UIvM;TGPzq!Y!^Sm`F2<(?VH~S^ICvZKU&6eZ(_b+Z|K?<*j5lwe<dty+23y*_-i?3_$Y25zot6YEloGqNsKs&Em##wRC!Z=*9jI-jN&GVb}Ghf&0#-cpuva5AL;JDdya~#ZED%im7A6_8FO?A&h{nxGY>yAS^|6^&VJ-3%vbL;cG4<5Rc^QAn_*$?x2Ti0kS=kdILT#-CJcSoRpYp!HOB=C8gfOcNCjDtNl+he%baXWoU;<%2e?mM_1jn`-1DBhoy&bzpLA|E%aT0vm_X0B#c51xDbiTbsTYrp69x&`%wa{Du5(VnfA`t7-SA0pMcwb~gZue`7D?85k8vy6k8Ygx4lg5`>5KaaDM@7pEM9!ouDd(2$Qdy40A$cCMK+$7Xr)6#x3S93n)`Q6fJJD(59ybe7Fd3_#<<@<ckA<lEJit@&wn>)CDM>zK-Tjopl=saIp4Q&15T=g90^Ayi1swWlab$v@aRZk|)FFZ#yh*~4g7mv%58}3N){HS?+mi@szuIkCdxc!p<Kjl@&&BJvkj<2URqgOkF<Wef%XX>5;^!I+tzNC3du?}xqj%&}&<LaK1Xn%9dzURMwAa7==U(UXcdT#UmWZgI(XIrji##zeCo~>N}U5W9|Ai3sD<ay7&!RyM^(z0Kfx#D`tmfzy>bcI{?F*#ex;JgjbJFcf{c4!8VcQzk4q;yrV+;NDXyS3~ZA~*L*71v)ayG{m=pO5D~#3kyn=f**os7KAN8??MVH_PkU^)q-rb9vlCl0|uYu9@!>vKyeD99w&=c~$)l(XY;&*9qr!lHEw;h9{55SxQ_LELRRD@_UKw#yoCWe_7UpJvY}wW$x<4<D3!B`-%6V44z+p-qh-Zp&keNTg3g6;#LLAb@M%p_fgdUisgC1;eC?p$MclgPRSe2^<W=1+gX{r`f&ZVE5!LId!OR*boI3Ex87%YeDFN0)-Dz09o}}R$NF3>dm}_Hx!>mbt(}bW9Z}B^Ti%&->{rr#5o-f;vmWz)yDA@S$rZ0`smJh!i|1U``!eS1F3b4X^UCwu+a2qnoZEA!<|=29T*v!8&D)F5NB4Vt+?uhXUy8R6w=??;m;dwEmBDfq?-f<=YrJmp94edl=iWhFK63-FH?-fLt7yNO+pmN6+}tP4+>!kQxBri<mChi!j`yOvcPOtn_otlKs3rPq&(#{Y;yEAA<Lv%~kBj?BDJPoS<6g$?yenChmvScXI&?4P_TaslloP}4G4C@&!+F2WnacHN9^vaky~KoIxs;X2^NU>e?Bw=@))MtNa;Bkv-1p-Bp_$8`@420a!)*CJZcj+XDrb<~+=tCv^Bl75dybqLD4%56pUvFdKOKMdu$Irh%;W$2KweilGcEO-`=^=fo)WGH>)Fg5*;lxHQWU@6&Y6XE?&bRNo>|RNkr(s0nd=t0*&eeVGdJs(lOk>TRZIKjoY|J#EU)CuL;crn{k7(1c`aul_ZRQG%=KW;&Gn$?EXR3quk}8`mRH_~<gEN3bHzQ8$H9D#%Zaz<xX$W13D~b1T8?Yvto^U@%KLoea?T8XKXCcirOqI^o>;L|{CD3*9%tP58g=9OdSTD;p5M&noav$-^>UMCVjcQ+@i=7PEpqwy4m^*(Jv`3Yb@;e@!+9Qk$-G~=8e5;&Y<cB<j_&~SCwP7v-xAja)psc9{$|h3@iB9=9zC~|uM0jM?Qg*S+8eeqFgLRA<?;Nz1@DKxbly*L=JI_$#zFCAa{b=>E#=L;vi#;+%f#_~E*!U!<+!@f%j1Uk>gIjj-*R*P_=+(v6M3Akl`P|ND7ED3R@X8ve;niRpsjveURnQf>>Gua{Z{jxwB+V~X!y#oKKZ^{#`Emoay-vUx#y8Lx0E+?|9uUQ+wGbwxt<D3F73UwLj0V28TZ2v@%e)LE+scKQ@FPSug~AIRyc#?(w<~dkDOaw<f^x$rM#M3<G;$ydX(H+BA2}{@c92$g5z3qd5_Cd{_pkF6}kC*q}MCu^Tn2{S;+~3<yCKIuIIOX;<#FFedJwuo$O9r!RJ9kk!#+roZs3c%G+~wcf2TX<Tgd#gX`ZNi+Y+N@5#@tx8|cBhsYhiuQ|WcV_C3V-V!0!r<~Vb<WkN%{9JsqgQ&-m7s2C(`*|rW`m3OMLDW}W0&=q+WoH=AZ(b*!cRXilxR15xI__iDysoJKX-j!6uRFKj)rzl!c+YI+a`sQW|5T3^=ZlgTX~{J_ryF?+j{6*+U#W?!1M|xFSG5wwai#q6A~(FR^Z4KXbw#k;*i*s%&5z-EceUl?){5u*?fj`Y?(^J!e17N1pTWoV9k9%ooIlf&OIyOld@1=Vk2Bt{O811X;qtSsxw{s>PsmR|zxeYPrDhb5r!Cj<`J+^@i`RK}ZSGffJYN^=vE(w|=Qs+IcpO|&yq`Rf{1ul^w&Y4-qF5(#K`O>a=62Q$<M$E;>6YBQUsVfy+)i`9{p|v;^MX8#XIJZeuPxW{UewIZdbB;IV!pJ3V(ypkDEDjgt)<qym~&irjDnNg&dhYneU3e^yzec%%IB&1UJ>`(_FTvPwxjSm&tukcey@V-tUZ@-oplu6<o<e&@c7>o!S9y}Z&`8`-%rpAn`Mcg@m{g={Iccd`KT8@ByuDB2|ll@$MN;3&|%39yk|2CTZ>%Iz0Tz?ZQ}bPTdr-27vt<GYAbU8eIn=B5C4{9Ka`5viCl3{<@P_|;`LV4p4)@Z^`vTePO;?*o-fS2vYx_ZUY|uBgO+y`bqZR)Qq)!CmG6u2TxQQ@tY<SfpX>F|FiSnU>kZz=aD7*bB9Xtz^N8mrt*B2HpXdDfwTka!=tU#50@syXErQPrTdp0B;C>w)$L;Z);P%uH6YIw)8gI$X{X{-Gll$d<hsOu+Pwcsd_b2MndFU^HPHp@(hTl`!a>s#aOL;B#9)3@Lv58ne%F#GWdF`)(tAgbQzHejZW<Bz^wfMX~`WdftZ#Q1Ip*%k7(S?>=$GmGtmvg^-n>pVZz9KM}d|NojbyGj8VO~b_yxeIb+9?%pu;zG=As6rB`E@Vh_J<|%b+&kqC6@~0#QIc<(=pEc-b49w6W{mRa%o>8KbIBfVV(1Hkp9PfzOT0BN>Uu(4;P>0^EB@n{+#Q=z$IM1jK?SYH(pouTnT}>S>D(XxkPxeVJWYg`(eoqo-gk(9yf`f$IaY-pU(Nu^Opz9jcu{ZMgK}}TI$j8{?Ji!o7;oW*%e%`<&ry=+;RIt&|EdI<H%L_2bNqZkzB!Yxg^w*SJiLLW%IgI(!j;Xox$aQ<9*MbE4XizN}okN{60tewFTdY*m4=`Q!Z^Sa))O-*V81D_etbhUQeFivtt$q%e8fpi}|>1t@Y%Gi*=}$zRczExxeyDmY6Slu5EXT`O-`Kxp=+t=l;@-4@7x0H+&a(9<Oc^*IBLfHIeJtVLb13@HriFv%Iu5o}aTy2XJ}ZpF6fiFSq2V$B}{Wdz235am!J;{y+Ksj9xm_k}Jvl{YIm766*hg+kc&(`|P>8wUqDEj?LnB=8fggJr7O%Qk>VvR7-9=-~UT7U&rQf?q1B}dG!N+t~@r6$202=U-zp=#RtugMDg|FSRC5J`-ZY5O0>r~wgLGn&VS0{>#{AE5?x}S)Q@cxx#Vif>q?5{@v-LzV)?!Ov8`zTYOep%eAJH|@A<VxiE9IM|MQ#}2gjz^rCls}P0lZ^67@KaZ?n{Id>6;}56I2WFLZp*N;!Un+v!=$?Yvl%uOqfx-^kYm`MA!<#eKVqebt^DNxZMB$5Z({HJ>ZZ&)1MkzV*D`@Ek24Pe=I(-rrIp`Mo`Iv%IvI_Y?KFm;04JpRa>0Cx0H8tNC$!UE8(&b8%iA_hEd#=5emrv?N$Af0HQoXZ?6F*Kghr;Q88~8@u^=Svqlv*NJNom;a?ioWJ&5+EFUbJLSY}>>K=ES31Z0j6K)ZMT>pLaU#?$Jnu=K_X|Bl`|Y{1AzZXyJyA>K=I4Ft3)dEjpHI}W<Z}9zMPeLIG!VJ@eJT~}-<}(rc>OCU8uD>H+ju`oorroGS#rI7e{tN(ykHaWpWjZ56YJqbV@s|#YZE8@#FHXdvafM_8YGMRE;CnsDZC$UPh4&(?@Q(U#y%eZli^%H-rpMdezoIdYmrMigLoZQi{$tGC)>LDd|zXk7kh5bi<z7CnD<5U$p~&w!9L#KzFIWT86-Cv^`9r|JNc%Y&r^O+uI_w}*R3tro^11ZV0ksK2hY3Scabwlu6Ag{<9~7x=jP|~Ph9&fFxLvQ_&i#%XpS>TuGH;6NBs9wG2DJn8n2(tSHwKZr>0tRqj|oVN9EK^v_FH}|Lr}Zygk>O-Yd$hr&P2vliRs5cfK=7u04=HUmX9`Y>^wjv%Ejx{eXIEjwN^C{eX6ACF<eNosBiQbDcqQy}{18;=iAY=lL!Cf!F7!&#BH}`R@%>ZvR?dC)xM$am~;5kSjSe`MUY%1+nkxr`B1@t9WiTbF;jG&$*0K8@Rmr`OB*9bDTkPweHS2T>d+5XZ{$=K3SDVbNhEL`kdR7h<V}bg|XtEIl*$h_PwHhxh$Q>8K1wX^S6ufvFFAgJJew1jX$r7Tq*OS{!*@|R{6)yAi4bW>5l`;%lWaqA8uZ>z!@Z$9Q_w?`8=+tuo{2=&{#Lk86=nThfNdxD?5&M^7Ea1yX-@;PRdSNa^uXf54!~9TJBwZ-Km%__GhE4%#thLMDz8f%;53QI%oNN6TR#l=h>&Q50}L{gXD7Q=~(e|`9-wHKzoLYe%W&^hx;X!U*&b4zktVQeP3~YIm)kFa-+$;;{0-y-{SGa_i!AzKbOmIqyBT;&M#h^;0%(>Bf3ox{Vu=5>$C7-9_RO7jCKaem0sP(aQRS=I9~R7UT>2Rk8uXcwH|5K@_2tM{n}%NGe}<fd|F-~^<3opvGg0goI!G_S>4{Ef8`BCZoZ#a%+Ht08(MM$-)~pT8=;>6@Hl+Gp@}m{uEs9Bb41kR5V=|u!Q*o_PUH@woyd*ca9%%0a``^lmh0`7i2GzSmkYM={C?4QwwM>Ay(QPGx0%i5J9`4xiN1i_BO5ZeCp(n;d;XD`;=dbFA~(N}p`DvAu8;Oy`Z{hgmmkdIlh={Y)1*ZU#W)*7ExFdJ|3cx$aFJ`iG~N%d4CLnsW27ZF-_JWvPvUkKxOp5dmrZvD$(2*XrgQnJ+~30HyblztZ^Gqg@%Z3-4mz&C_FTdB*UY7yw|U<0;B#<WuI}f*pOR0{<M!kE(b#fD>{s?&ePpNDue8&Px&7w%+rPac&Qp6XHN7UzQ~mS?ZfD^Iu4l%J?>d9!QQgLg-#fDr^?c6rxbiu%&)aiHoi=>kKeLO+&3wMV{%p_n>)4;q=zQGV3ce1WuPOFJ`AjO0558|KpXL4PZ#niWGdJsz*H?&jrJix|`Y8<M^W_xJqjtv2=a>0B9>e>FJ(sX=sAqg!fBppCw{icYpUJc2+TA=3#+maxK6w7sZt{Bu{Y-@=ckHai&jn{Mb31cy<GE&$xKI0A-huCvm9q`9#n1VRcs>6(Y-V7t<uB&-^LyD$sz*H=#^rPCah|kYoL~CcrXn|TmT`No|GF$#Zs2*`%q#0@HJQ)Hv(2(C>*oTGvwE&O=LOq&pNZrB-=3=@yS*pcf36pf`yHPbc<-&9>to5~P5j(yoQoE@lGg_BTege)XU7lYEV<EWvbcYiewf7VFUaQe{W`Z({$VD!2cHuucy5w@m}SY0^<m<=ES=xV<LvWsds6th#-2NHUv2!bjoY912CttQd|o)t@8I%z1Gqgu4-@Bwd_Gm=j)EQB{y(^#`uS3kOSz}HoqPK(43=w8UE}+=^A~v>@~81S@vNKV43aC!k4)lzOI}`YH+a2m%H{j^3!#?WXud?;hiexadwCr$=lW~%^-I4HE^_m|gi`;SI4`PlelKCf_Z9cmN<}Y`OL-6QJT92{Nw8d!+I%AFsfZT2BY!%NXG1=&^y37Sf11nRD4P*1*UBH6A=>rhLXpdPop>D<42^LH$rb16$$Xw|<o@RM=Kc;jJlq*1mm<=JiQl_;0PP&Y?QHIEXFtndQzs94=Gm)HN)oBI)JPgVEZ|S6DWrd<2me#*vF-k=Kc$Xn+xq|DPpPH5{i+TT*Mo@fgSQ3W2Yvt|ZUGVh6C&;k5x)u%4}kXs4**9&#6uwB5fJeh_;BzT@VgN4WQh0!h**UW1gqdU_=n&)@G^+_Yxp=Y`9kp5;BVj)!Q@N9-+(tl#OvWx!0W*);iJGS!C$~9fxiIHhKQ%ZM}nt;$3w)U;ctOQgWrMo0>1+u1ed{s!2KcO?(p{D?%)?8;#TnH;8x&AAmRrh;-(OB82o;47`O>U+!!Km1Q9oc-wSRCZU7PA0}<DUi0i;>f$M;4K*ZJHAz<=QFnLXIHE?bCGhp)Pz}4V)LA3*pRXd;!#C4(CXm4%QW48Y}^ohJ(Kp)!$^u1lcn6wKRw{`*J*)Cw5+hOd<BLe0kB4EBE0_Ksp8ASXLyc75#@WT+X10sGDB7O`aejMHf{5bdti1<l}I2<Bw3GW7O34RJ9ei|Zv7TyE=EVwm9+y)|k9v%sP9{dl8xC2D|0z}*q-Ur+f+!-Q%2_k+OB7Ozl5Bv)FUl4I`h`29A{2E03I($C(b?_VTMc_BUZ$iXxL&Sq2;-T;a@KCS<5f6iiqaot4@NM9+;24NF79ySj5q}I3e*)hJ{sjCLM7#ka{thBO49^4~2I~-UDny(P5xZ$j{F}mLzxqSOBjAg`Bf#&&*Mr{&FNPlgF9vJyBCrNdf?otDf!*+sP-ZvSfHwn^h;PFG0VWaGMfM`NF1Rr~65JU482l~pW8e<(q2LbSm;CAl9}OQ09u1xb5l@D{1)dBZ2ag1g1CM~e2p$0*0{;hi2zUUz8F&D=3p@ne1>6cwW8Dfr6W4|pfl0(yksSbE1sB5CgA2jQ@I~Nc@K^B3;IF`Q;ctWIg5QJp2EPX$=+{5tPs4kIL*dmS;u;Wf6L@cM6YxV2@naBiYl!%Hzq<JKqF)j47r^B0!R=8t0^S?k8~urZ_XkISWr(<kUk&|g;n$<^9^f7*^C(2z4L$<g4g3cDeefILk?_Ufk>DwC4Lk+>1w0A-1$Zso4PFc04mZHt!AIaX!AHPH;dHJZ#m~eQ@Wx;g@pbrPU=s0f@D5-S@m<JX0^bD=3pk&{AmVVpo`-jZ_X2kXzX1`CgpUS~1iuRr$H1q7W5ClP;#q#ph0lRc1J41^hKN=8WUvbU2qK;V9|xWRj)jP)!bgCof+xa<fG2|AgAV||2abk_hr_#ohlAgSw*tQn?hdaF?hbAZr+ue2ekQI3F9ef_FCj|?UjlpKUxB^g9q_r}9pDx4_rNQ_)8PZb)4@YRs`jQK5OH^SJ#cq$bHC>Jufa3@S^(b+UI1PN5ywNs8brJaeiFP1yd5Im4G|xJ?0f_w_CmyY5OEQl+Fpd8iHju`@o|Yod;(q%Od>ufv50??Sj1N(7V!;<Mf?l=pI{R4ZxW065BSqy67gRWi&%n)Lqe*q86ogH5;OTlFo{@#p9PZ}QdOM>jzgXc&c%J!U+_$+sy&%fRXa1Ks=j1ORej9F7?AIis>WoWR5e!nFn;9Qq^j}UCRL5|HmPd-w_$$B6Qrv7N|37NG$CN#6R;M@7X_@1MFDGO5!Mm;{D5^uY_2`x?eJMr)%qkh*DbLI5wC*3FIAlj#O66dJO@4jJO?}zejZHzId~>`3H&;E33weuycJ$6gn27?r^F)OE3t^P;f=r~;sS|9Tqd!IE8xw*B;q;{@!b${1Bmzmi1-Qk81NI|mhgAMEy2$~#BCtrf59h${{`*|5%+<JUx$d_f`0^l3;Yg5JRBk(3;z^6790x^&wz+OhKN6bi08vo!1KWi;F;hB;Dr$JGKhE;JP*7Iyc#0j=-0RK<M2E%dGk<a^2fpCCsF1*cp^l+1tQ)GKMCFn-USiwgNP5o&w&qtQz7DXh&US}_Q9`!ec)1vxC|mb4H2J*h;P9E8OlulGMGgCYY2<@_YfBGpCK&bzu>QeNyOD4;=3W@d*FS*_kbHh#P>qPjo|&jjlfMI;)fyPN8qo69|1oJ5kCbV2qupJKLvgkB5v!~3-C7Z2yh$lGZ1l0_?uwz*T5~oPe8;DcwaF2LtqE^0eD~V1K|7My}|c^8$iVM;r{~H2iJj!Lm}cjA?)42B;r3pSj4wOSj0cWJA%nChcJ_fe}IV3K*XmY;u45B2Ywcu1I~ho(;#9eM0^l_0(=m>8zSBb5&s*04E%5KW{7wbMEngr7yJ!)14JAT5wC=2fLDT-Ld2g##Bp#P90#5UpADV|Rw3e95b=i)@dprbG<+sF8axal9tsgh!6$&Dz^_5XeIepkA>v5*IB+ERS%|n5L>vwu4GsrC4u25*I5-R<z6T<%4-wafh%ZR&_kl^orz93}zQiK-z-xj@#Cs$b@eYYa{BQU*iJ3&a1|nVz5q}2%0sI+wI{ZEGbnvI}so+n+b0Om8@Q=XD!7Cu*wGi>Q5b+lHJn$CqE{J$P{7dkD@Ii<;3%(kh1<rwp3*n{ULU0NCOMOd(&jrs#e-hy<z$?(7MEJMhMDQ{A7VsAI=NLR0oQ(b)gC7JRL?4d9bHF)h_c4gLX$bpK@KN-Mc#dC_{8|J561)by7rqX>7n~2@56%bw1TO&p1g;s%{vR-j_-QzOp!76E+!_8LxHGsvydAhdcrd&ZcraLj_W&#4vG6GHSnwqHJK#y+_aWj@e)WXQ@OQv6xIH`y+#dWWya)JE@cr;k;QPV#;O)Tmz`umBKL{ofm%}A+ImXrlr?K`x#CzZc;6324;rqc~gO|Y9ftP@%!oLJh1uO7LU<KR{A|3>v112929t7^?*HiE};p4%B;nU#b!PCIY;d8*t!QaEzfWHU3;CsO?@Q?6(@Q>gcq3l0_NyN{=X{|p85x)X|8vF`)5WF*Z5O^58KX@2;3`9I0J{UY6JOQqNCxEBG$AYJTKY)logiiv02%ZTMe++*g{4w|wi1^b`ekVyj3;sTM7TA1;NgM+o6<YP4lh}M0N<1>O>O3^xmlB)rREg<5>+|py@Sfln;3jYx+yq=5-X2^Xd@F?gQ80=48vK4RiTDD%9+*U245#z97$QClF9#n6Z-aZl+rSC%J>UfJXYjAVpMhiGOTaPUQShnYQQ!e^1v~)U72Xfr73}cqUikeG@skko%kX~Sm%%Uj)fwIa-VaPZ2s{Yqe+QH&?*tM510rq*5x0f+0=ES}2N6F45kCwOHx8-VgBnA`cR|F}AmZO87V)1Fi}<$0BEIGKUnTaA_?hyKsN+qrxyN;czXHCA-}~9`m;AcySKScyt6=h<!9SyXUHtwlVDhG5@)DH)5BxNo^3%9?C<T*$4?YdP1Wy8A0$+xb&_41E@Kx~75b;eY17maxd>dm+WBMaRd<G&ehu;R5gMARO3!VXXfzu%36o}Xf5g&plf&29g32jvE|M$NhsrpCHMUv%zL}LF<>(}f8f3uIjuF5an_3L>TeRsxxO%D}c3Y$*fe3Jej?8!&}'

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
