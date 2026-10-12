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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_003.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_003.stl', 'source_sha256': '2e3ea427c60a61e776ad57ddb10ea630864d4825680b5492aeb369b525953f49', 'input_faces': 1192, 'input_vertices': 873, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18198518455028534, -0.4999998211860657, -0.36910250782966614], [0.19259212911128998, 0.2940431833267212, 0.36910250782966614]]}
GEOMETRY_BASE85 = 'c$}r2b(9oGw8py!Cj<!u4atz;ZebzVAi-sECj%_*4k19}!5xAGCfEj-;Mzcd6;@z_2UubdELf0)z?<9m>!xolf4uYFo^#Lln{V${*Hl+kTlI$4PnJB3#y@$qU8&cMZQWGUDAH+Jv|(Kb4e8mX>)_)328`6TjFwM7w$5+VqG4zoT^pv2DiGFnaF;;^KJyl+)UAAhqTT}C`VSg1s8hc$`VR{0N`9?QeFk?8`h$CP8qhWPxnTK_GDW>*3KjK^_WmD#(gv&GuUG%nk)Zk#O8-pieRb$r6_;<M&T9FIpSE3f<So9xa@$o^-TwDSu2`D8+75TV556x?wH@w!Z9qxO*Ul9@;LbPuvu|81c)*?STh!~a<wxB->dx2T`%d3HD#~Bj|B|KG)1MUeU%<YZnEs@w|LSTNt#U5@7b(hzZ(jN@Qq<@9FXye_$8L!c^?$~`5w|5qlz+JOIV<n^w0Mz!h<)#iY4M``VrvsDzx4ZOMg5Di9|-#HeE*KqXRN=wIyk|dAK1=*V$gTzo4q&0S>?xl_mlX(z1R-~eNmrQ6QZrW_~qwBeOj=e81zN{vl3jd4V}-6{J+@`1btDTTnCR?+yC{U$TxGm@kM^wu!C0pYt*?Q>R;-OFZ#p0@;_LA_ik5_?_2t*<BR$~&AjGq<(v24_@ewQNBUWRr_^6te%SKOUu6A_e^0Kgigpm~ljfA=`_=Xt^UXFZUul2e_&2`D5C3CtRqRKRzma{fx_=vXHtDme^dGYk`+lYWXf-nbSQY(H)W0VCUZsBqx_)`8D*CxQ-`kyi8W-+-@1<E$RWXi4{$=)Q+==o_G_XF?I2HZBB>Ob3MfsV(kF)X<<^15y!amI#;`_c6XVs798PT5bX<icT|J#BymVZ&sZ`$wd)4V78L+-p*d(k{8+8;j6t0I5&m)yRUmH8Py&D&!C)>&-%G|wNVc3FGg`rbyqzCZKt4_ouU?Q88qEnk~C!75+%jRg~|@*Tg*3v1r?cNnn4oo`lV-}DdI;m$Xv_uzc9&jEM74}Rcyp93QQ%YZe{Ygw}#6Z!DXY*~(p{OYT%c|Kr#ep1vQzIXiRC*Aqx%7NBAABd|GCCZ2IJyRu0<R8jt%?rNop2vuM_~xqTF`|94j<?3G*?4EX$bX-GBXnoHJ3ldN6wmX|s-Jb|d*OSZS3m2{_ZGj$^ZcdN3GRG<G4}nJS0}jheed4jdH$<&Ke_Xbci7iPpZiIC-&I?!d0yLf_MB+X@7VVReNq3rO?dpBSbAR6{|@`w$))GT{yLCg?N{H3A{Rt`_Ob5|`tE#x;s|S=_b(hT@&iA=@kRS%{`dM<ihO(iCttMZ%G;~oTK?iUz9>KYg&tOYmHKOe^Oo;b>Tfph9k9l!(mrN8_RSNreYC6(t$E(3w7-#qeNAb9?M}0O)_5PS?BDzB8(+!&8>qRO=lRRB|9ES$PyI@?Pu31R&p(&_Gmwpa>bIi&EHTzRPyJl>XZC4ai1Nd3TjPz!k;w1LK8-t3e!)%FXBwxXK84t)aV`4)o>Y9i887Dt)AkKHKNx={x8`k{XGA`HnwLcTYcZCecwCv^;CoFuznMEa@ci6K&Y#*3>}wt5{Hew7<m18uWqyWF^R}q}(ldN~3C{C0|7(52zqLO9nD(00u4}fPKH~C?MHjDH^@`{a<Mz$CvFsnnDDr))8d|=Vc!>SUJy%%u_^+bn`yZW(cKg1$=`7#q*w@N8S1siH1NE%>1oG)I!f%|*^0f|YEZ=DV+B#42l@Gse`8!v{x_#~VSC;P^RXWb?8@WbVzV}6Mk?&g<YWaz4U&(TY{l?cL8EZ$0a<u(?{5o_=_~ut5Ie$iUq{vUznDZ-il;wO~i1YvKC-QxnU-Na%B3<PBPHwY&@87>hh<Y}e%*V%7!$dh|$}W6-oIF+J8*|HBeqzJiGXLSP*8HU%4nHBb`_(?n_fD$F{n$ty;QE)p=I#%+uPxZj{UKpMwA=Tc-N63#|6)Wrp&yC<W?ZVq`R6zD{yMNeR`{tWS$^PENSyGy47Pl8Xg4Ll9{VdE3t!7}htE&4HH~un=H8?1`>qS$_;DcnsZU0V{HJv+-&?ww$oDNN!RIp%Mv8nRIwfEK=1e8>we;(){o)^ZEkcyzGk8BP?Jdj6)|2=9tOX+9tm|WcPaZ4ZyxEHV96hXd_8uz{?e-1*2A}WEPQl}DMo;$Z4deNtaPQN?Z}7k>$2Yj5)t<g8KXduT2U_iHWbP~dN)32?Y4?QhyMBxN|E|_iZr`|foZDyhMd536`dfbDy3>)uUr~?q7c>z0=EGvVzh)UC-yD>h%NeD~{BGfVpCQBV5u!df$60>hWtiOVfbP6siYycP+QVu*eskpF_J5e{JIlWtYqf(veYRNPS6{_`g<oUbzPY>wx2Jc1oX9r{v0s0(@Qvl~@P6!lL~Pf$I>7C7vxf99&*OIZs&lm1?v_yYYut<w+r3eM{pWu~iTt}4cwTBb?X7;GaeG-#v1!~sH+12fg}>l(YQGZoG_Pi4|M42xp4s2A&d>eXy(dI|i+Ow=R`@uMyE)mv(4EKWC#NFazA>{V`{C82M82mix7(uWBHy<+BaiFXDMY?6&r0qO)2~OkeeJ?1_A|5-<(Nia9;ap2iF~76J#M$<ULNo1OLBha``n)oc8L=H+Gwt4x~p8DdX>38EfTn2Eh!Ky{9nEi{mu4`mmNiabMmL=<$3tZFyWi?GFtsDa3wa<?Q5Sc7yZg9zs6#2x6{={zOl9i&jUN3Mu_rnf6Vs}`<)lx%V=;z^fza_Gh?}5ecDcx<6AU~k9SQnNxy7c_Rrs!^{Jdw^f%*&YFwW=y|^8&_lkA<MnY{qzPz|$`C9oy?01~c{`0?M+`gHvFt>BAusFBx%YgB_>_((0=g@cDK8G4dyM4`^%lmys3z2W;!T24VM)<yd1=-(nJW7;P;}4$q77Z7^xhRtR;gh}*B0n&d+c{HS;hTGS{Q9!}EVip1{fPU2nR)CNc*OO&_qD7)d~JGjuIH;9!Z(M1!u_Gj&M4up`b*Z|_RE>F{`Pj$pg$}tD}3W9`U8$HPJQwe67~0WdCmE4id*~3Ji0H+?c3u*>ywA~*Xd-|`M9r4b-sUcJ3h+o8-4Qfef2LxWd5D>?6-XqDg4|Uxj*!4VC5SF-?x18)l@zoUi>n~?fWhk;C|b_3HP^rl`UUOXlEVYjXsN`-M;TyJfFAsd>SS4|DDX|X*oy4x_u+%ORi_>i+udbGKl?yQ~5mM>47M>Z+1Mw?a+24&p)AKdAt6_R(*UOpGCWUbA2ptH}4jn$3FR*%Rf+#zi+1M!Z&Mtz~gSox9mqO;qoz$`9g{d-&~QF=fmk!__+N2Ud}(!f#<j91ESo%ai=cdH@n?d`j=C)-*i#5+c&kpdETyJ@cugS8|Ux1%ljp4YmD$yo9xdXC4B9C2-oxXjPb%R`VQx3{437w`yLeH{%N*~6#35%^YzHbS0coAGY{qQRUk^%b7(&vr%T6*eBaD8oWHt}$TxjY`M5Uy@hP$0CHr_@)gDEO{KtIWrG+e&`C)t>mH19~k*{TYY~9B*zD*~~>0Rg|kBhxOih9l-!si1&73TY@Bh#(6@@GBZcB^tc#_b!kc5y$sHb(ebXmvi1t(+lV_*YZ$ekpe)&h7iE7UTBEdApN8dMEb>oF_QjojI1zLoS|-7WHg0h>x3t=Zkz_6~2xzB0m%P#>qQ;9r5Iu_`X`^AKBl2KT7!V8@c^6ZISIWr84g?T-P}HbN{p2-`^+=`w#MS{;NjZ4*BoJ2wzLi{=`Ro++0+i>wmfuxBs{+F>c?y^@#5Sw7bIdOg%s6<9g6PZCQ-)7iQr7GWBqr+t;S#<MCT`N~GI2LN;-K{_x)jkzZ>HA9spuh!*9i>&5MyVynnEp1#ZF<o;0RkNcI6gOf9hd|&I++@F)5jS}TdTh0Ee$WtOe=5s!NO)4kz&!^!1vg$5>uLTp>$9Y1a&#MUG-|EZtzkW>m;c0pN)<_%e_O(=(xc=v|%KWqEdAqw~qujo8-SpMfQ=%MP2PJO&SmuY~e7@PAd_0Yx!{r|+z{immD}=8#<m(i3@G3qotXjf;9A7tSo5Ew<zTF@EMc49tcstb^%ilMMk2@s_M!9|SdPknO^Smc~<B!MOKDn+(i~Mwn+)vU)vVW_o<!gsKaX&1vImYc9)gJP34fmt8y#6)r@nYEh8NRVQk*~YU=j8b$A@^F#|ENEgQ>{g`+t-Tx#@F>YFS31K#UXsZrPlsfkze~y9v2;QvOl5(`+qIt<Lv8EQEuNTx|!DrgzV*d{!)g^PqE&rkAL~TXt!@9KV+3-U+)_W+j0K3mwa5#H$2Ae8}sAY53M15UwuAr2_!ETFZ|;Fayx`)7QS}B0-tyF_%PD#n@?hSKmN8VLTp##`POJxTlnVJVLXnydQOY&V!jPDIB-goGy4UP(;JhcMLA>k^0;{3N#y&M@qHenN@0<&T`I}ruHMQhQGSkJt@$?bN=@natiaEwN*X^3KY1A6$IIM>pa1m;<L$nF&Hb(H%ow+?%{amSPj!TEG%d~jxq9JvQO@;ed_OjjTKHzA$~=CDm5mhT;C_yG{Q3w{&arXap142Y)W^QhbK_;S@I(IP^YGh8#rLw$H@x=!M!S690Y0v!8X@wHRXaKVKwg=jtvHuoacYz(-+P~*8@8^>^H|*p7#9cm_;tHyjNA8}*10_kKZtYtT4)*WpZ4_*d~+t>Pc|1vMTqkM8o~Yc^p$AgcZT0}w9GH2$?HVhzwnUT;g1`qL_Ix+xgV}gCi2b1?cAR~SR(SZ;UU~^`FqHAFrM-GSoIIN-6qXpfAUt|@44b5gui{1IG=I+YcIL{treo(zAv7yPt6IpPKo?9xIWGEN^TeX*FK+d$|+bD&x@PN{3#yJKa!ol*Zl?TKP$`Yppp%Ubo;(cllZuQBA)BnY6-Vn+HE|K4f!(0?Hg@8JdQ>u@O+;3DEsDUo>y_7-}bd3y?7k;y&Wn1rhLCti%WT0l#}8dx2O4l=acbQxSr+va6kNgYK-uk-{kr8L<{bpcdv6fcUp5kuFD)h@;o1pdQ{^2`?jvL%IUv^zgOc2JkKu}6aLoi!dJ_8@|F5H`O0>UbW6hD)^4_+q<w~d8~)bzgrB6{Of&p#`_cB*{pc%nBK&Rr#P-#GV$O>Uf7`fld}UlXzA`RsUmX`tzA`QxUl|upIm)<j^3`z>cb<K9-h-cH-h-cH-h-cH-m}YB=RMn3=RMn3=RMn3=RLcg>bz&yN1gZV`m6JvUA{8!8C(D6@|EMP?W@OG+gFdXPC3eP*7nuotW%D1oOQ}kj<ZgEl;f=9E5})9yUKCaDPK9xI`vVGvrfKpoOQ}qj<e<+&-Yfoa^7hB>UpD+ubekJzH;7Z`|5e4?W^aF&UTgaMkil6Z*;b+oHsh<DCdn%Im&sXQ;u@p=+s|1Z*<C6&Kn(HId61)<-F1SG(T@wInTF!^*rCVvM|?2xsI@X^*X{=vl9Etb&c(-*EP1UUe`GJ%5{zQ_yxD8dYuJdz0UHLNVVQ7N4bu(ef2udEZWra)$2;zSFbB=U%jq$^406gp(fWyxz4qH^*YzA9m(Y@*U`4GUPo&a&vU+d-@x|O`v$hJ-Zy}s<i3HOuiiI+pX9!QU5<L+z|L3h8)&gFxE<8{Lbk8o7lNPUz7YH*_l4|y^}di@zItECE=RpDWaq2*g=}BFFJzaa-WRg-)%!wrzH(p47?)>*m9O4sgRkCaGxC?&;2tmbeLTlk?&F!MnzFCnM}?o{J}Ueq_fc(My^jh%$$eBiU%iiNZ&$sKYS&Y}k7}2%-bb~|QSYPL+g0zQ+P-=p)!wdpAJxuR@1r&u%G*_*3pl>=T)_6#=K_weJQuKi^|^qPuRIrUwyQiBaD3&tfK$HmT)_6#=K{`lmFEIZzVcka$yc5WIKJ{+z$r(0F5uKtc`jh|`;L9(xsUCu&v&$oYuQ(x2id;*+{bKea{0=0DBDl+9O}s#E?;@hW&7%LF5}c?E?;?$X8TE=qb0k=<txwWY+rp&XFmF1qt(vJb3@x#pBp;)%5y{8SDzdD*44Cp^*N^PtIsig^;@#9JXf`S^|`8(uRK?EeC4^Sxw9>oqde!e{UpzMA9m+*)aTmplRVdkpX9l=?W@nVZC`z^ZEsh7t_?rQb8Wjm%5!ZkaXII!>lWZAS+@W`$+`u*9Ch6S{3PoZ?DExh3wHVHx&^x&b=`tpj=FBa&R5qh*!k+Z1v_6^x8MuQzRAj0)`8f5l64?4A6UM+4#)A8bvU-KuETNim326_udc(feRUm<Q@*ke$MKbQI8OP>IvgioS%>3nS6PSS)L&VL<M_%t9H)F`9gZ(eVXlv|4$ASBbx>wDAN$I>FWXnweL4Bcx-Z*T*L^v@vhK_F)pcJ^`O3O4r#{NMFD-vdE=O56==jRILEBf?4LbSCx<T7l*A3dfx^B?%m34#8c9nI5&UTe`gHFD(Zcz2@`xQ<(%DO=(Us*Tk_{zFLryOP7pp&nx8`NryXJ1*@>iEjKR@+zCwc5VAuGRL{b*+xCtZQ|)tE_8vd}Up$<16c0o%$&2TAl4G>slROS=Xvff57D^>x3O&StqQO^lY~3qpU-=eRUnOQ6;<OCs_w>`|3Jy+gI0tJNe2waQI2qfx}O-4jg`xb>Mcsx(?jluDTA~E=OGlZr4X$2X2?6t^>ErQP+Xn^-<P=`?QvvuddsNpJd%W{3Pr4?Q)cL`)1F!oUgo>Vf*TP8Md#!m*JG7yqDpWqr8{ll%u?tVf*TP8BV_PUWVf<?`1gkQQpgNeC53ir=H4t8BTqa_cEOAD(_`D`O144&UTgeGK^XowpiO$-lK7R<vkj$MLzb`_jKT^@97wwCbO@+H)Q+jdqcLbzBlBQqr5kim{7ucA56Q~h~LK?HN|>g$@YB>Lo7eB@7xtf-r{?|oV%i`+kbMO=kq56wutg=|DOR{-1$cK5!}w@*6kMM!#B&X+bzo9f7W_`FY(-!L!x~6fs0oTiSlD~{{H}Hx*QYb!#B@%IVQ?)nu6c=ezfs~JKt==e&F%O6QcaxH>~&f%sYo8M1A0U?;VbC=X-~IW4*uUZND(uogWwszr(_4kzc8p^*(9vcpmG{H!8yar9iAZ-yBoh8t48QA@L%AH2aA`U*vaqZPg=?s_Yq&-=6)%pzqH25662=Pm-S%-**_sRnQmt;rFfU|3K3XB0q60`&zRNBHxS*vEKJKiswlX`zwO|K+t#R2ZmhPZ*6x<Pmym7eB+D!x%^(LzrZ+|KZ|`M=!^a^G++4J%J=qv<Gb^<YfoldzEXefB>R4){+c#&y7gIUA1yokW>cko#@5C98rlB7N$eX+`<pZ7Y_E#_DDr2sA5iwM8SAzFUqPbMe|%@y_bdI!ceK{ws_2Jeyc~yrL-tSanHSc3`_#`xd!B{gUiN>j<qYfnR_&fLzFM)Lct?(}z{~`GkMyw|zkylo)3_G>bK+_1?`a+o{S!XT8>0Rl`|*3N7v=mDfKT(1$j`aY`aW6(Ill$qo1e=0E%D5{)7J0*k@KhjEc_>O{`5}_;rDRAl=HLg)4VO(=Xf{E52V}2^L*1;-2XR!#Pk22DZ)43P0jQC%z9kD;`^7><MM5Ppvmv)zh8KZJKwPVT!pu|^R<li`FNVM-)>QU2KN2A`|TFx7YVoKZEv!9heY}CjTG|^iSqYdu;y)Ta>y}J{$BQdQ$mi3@=IN_-rr8FIpTyn-v{4YYs3jre#}As{~bS1h!FKT&3@qOga~)Ozv6If+?uzWM!WM9KZAd#X|y}vw=)Be+jp<Ui2DBkKmD~BcfR*bW<JmB&G)69^5fX|^~o47%6~6`&pRKdIpfaPGO=$2ebGKM!}xo4y(IFD8SHzzU6T1r&RX-lx8CTpqCLN1-yihd`H7kGTl2iO>5<6yXJp?S^xgT!!ANVK_tp6<LFDgy<Gb_i`QLl1iO3IN{?~%O$p5`g_}j`iuD|g`e<=R-9LrbguYJsZ;zn72&AWGMRkVZ1FVDVLX&>$KE^ECiwX>`b`?Oy~`~Mwc&GUw`e|^u{_bL0=7`$&!RrC{4pJD7%zY^uIis$i`UiMGlTKMnE{u%gUk2TLzKNs!qhksl4e{+0w{{IG7<@houuutPojIRchta+Zsspt<4*{5+W^4pED{+{LmF<#))ydnChFB{MEDdha)ug1RVk@Jr?%@@}9@#dEETL8X4r<~ssPuI2Pd739h`7!X{m-DAT#U;z9dHBd%e44jK{^zNA{*T|w^L(y<-aa3~PcrYpPcpy3Pco0$<*W0Rov+SI@RQ6x_IA~I#;&J2pTJKtZ`i&%Kfq5i57^sP$GcrmbzIxNI)0sUlyPd;UmcHjIqJBx^VRWX*Iyk+cKfU2#cl_6T-f_X?f-VZ+RyFns{Pr{SNpB)tNqjV)&6;99oNIi%g6VFUvqun8`JXh|8uK)@r2tq|9NfoPs95#!tMLU?X>!*F(M{f_$_Mj|Ly4=7VGx4$iaBOt988aYvr}Bp9A|_o^ktu|M>p0|5~B5qCU~d`Tsk-h!eh+vJUsp#&r^eU+5n9&+q35-?0CGPKxz1U-N{&EnmC!V3yTC8!6=vyfVZ3-fDf;9I>t=yh{Cz&X=wJ=~uq5ug6I1x<FIgr^rU@{NLY8wx|DIDQo{3!)5#X6C<qt>HA3TFRzxB`(tIffBm;JS^r;5J0SZ*VyV4W|MdQz^|0`}C+B`R?(A++PUgQYU%R_~i||iOvihOc;NlA5kKJwg{;I+A=TPxqDXXPvJkei1_^V)~(XwdWI=TKOC7JYN>)Zb&WzVwztA9yZs#Jy2|G)o9nf6Cr(}o74D>Ntg&tTmi1|vjgt*SFq5RZmV0*?mofUX1Y06&M`1wRMZ^00p9VWuD+4ebOT4ITsS3?2in1FZzE1O8WM{Yz)2Al?OC58eef@O|m~pN8%Pp9aT3cY$NTkD+(KkHOV-*3Wci3gWM!2G~Fyh_40nf285Bv*ys5DToI_JA(&-k3!?XN5SbltT{c*6vS<y1Ho;;bD^ujbHVeVYryls?Vy9f?Z6qJxxpF0Cv?^Xotc7o7_=LB7`Q0ff!bvrbRBpecs?{7JRf`#ng~7#{y=A?vOmB!x`Ch2R1l16I%@@;nSyu<bS!uZ_<QJ1@b}>R(0{=9!IeF%bv?`!#9g3c!Ck;%Py-wWt_rOWt_psrv;L<uQxI>2?g4KEPs8`6@4p)w3*HUh1C0ak0pEu{1>Xl((phWj%oN1qq0_+APzU0B!Ti62QBh~Dp)*qukAqGHj|1<9ZUFBFzl1&jzXaFwuvYOfQxK1Xb_I_EkB4>xj|Vq^`oImquXNT&Ix_|FUg#$9Uho8bU;6&>(7oVz@EPbn@EPzk=wIMx;Lml|$~rRz@pR|}@C4L>_(U-OdN6Y7tVMKY3gR&65O5gy4D>ko4EO^NYkChe1@RzgTks(8TIhW6TJSpP0`NNU5NLbw5b%f4jNlK!Kk2L|b!H0U?)bj+{lAAU0Dli&4_yde5556C1-=0;rnBbOnJI{eL%V~!qYlJlf>AIS<-vpTd228Z1*0FB^h*SB-e8ms#>L?F{?ORBy|Q5X-B&>!7>w;G=WmpI2%O5pTEoLkLEH>F65I?t9r`7BI(P=OCU^$8IrN#%+#H++x*beGY{DA|ZtdY?`MVwtVmg;0-37ja<97j_mCjv=>0E`*O9mi_k3gS;kATy9Sn0eZErPfubTqgncs6tlcs6(r>PYpbbCcHa>OjYU3+sGNa24kZblyNr-(?NH&!6C((6!*5;9bzG;Hx+f*`>Yt{sYh!A^3bC_`7Mr*pDFo8af^PHFzrY5O^y1AT+bid=UJe&e{R|9=JV%I8x{BW<*^MfHUc=ZNZtq?VzW??Z6SxOdjS4@OvKC?%?;pJ)ld#J;2MLOTo*)%b`8N%fY>%nZdolS)la&vfwju6uxr@aI2vIPB2~sxqmRW1!I)XpKE*g_Y}mlpkIM!foDQTfoFnSKtBh!0H=mN)tOU+59_Skz}rwK;(Vyrr{Mnhd@H!WE^F+Q=0i?-%v-ndd&*k{-2q+&UJd;Lyc+y7^fs83%Cvl)=f*K;D{8|ZpvQD(ietz#FurJ<(YZ05lhOGaop;drkbN#nOy{bkbpB+YyAsp6E&VN>L+?Zx#Q#9sfGLRU!kY`O3myxd2ObMHpzXlzuw4V&rTPwnR?y#^{}a>o0i7F@-i1~G({Y*3hmJ$(^EhY`Flj~bJ)D1ChZX_bfBzEgI27$l`XiWh7nrt9=Z@D9#Ot7Y!0W)_(EH$UaH7WN=cJXO_rY{uV^%N@BZy}}XM<;eXF`vGXM#;=cAeP-XVtmPEZEKw@cTMzNAUaLFQC!jFTkgv?|Ya}gR^>AdxNur`#`@1_W`ejt^ltD2cUhy0dRk4HgJD%4rr{-oC6$>AnpR~1nz|P=mO0SE~oQxna(Nb+#;ayxyK*iZP4$)+rZnQm%!V>H=+4;=9}Phi2T^zgP>nU=j-){V7ezkIuTqIJPEoMJPEuGdI!7?d>2~5!+aM^_asQa0DlJV1oeYEfjdJhf;)rho&?pI?kPM#5Jy2{z)|36=wom+_z{%uDLlewVxP|XHP{E93|$YN3=T&S--G@ICZ+n`gH{C7bsEi^G+(v}MswQ#(5v8!;KCl(5*}s>;)&43;ECW3&@JE%;Pt^+7>o(Q*bH3{UXPs32;!{>;%x}xZ=j38-+)U(OMpv)uc7Yr9j+mWTR@wGlR-Vu=HTXNBM*W&RWO=B7em{C+o0_hBZ!wHh!dgIj*0k8tf6fuf;Dh{=mv0pa6agIa6a&Bopl13g7~`5L0kyGUkEM)E`}g3jv!tH-3;E0eX|Hbyb(dX3Azou2|OA44R|uRD6}NFDEP9@O8e|Gg18m51-KPBg==4?KoD=#IEa@)JzxsrrO;Gh3gXS$oBd5pL0pRZ6|^z53AizMA#^c#A$S>dId~cP7ic2*7qAC?h5CdCL0k};A6yVz0Gbb60IWl)Pw4ned;|UDI`{^734(Yjl={k2d?vmCEe56_zM^vw{|qe-zNE7j!DsS|Ac!YH7l9X{Z%slF=RpvcK@gXPZUUDDe+-=r{uunb&RP^qLA(M=eQpJUcpkJBcpkU`GzGW;I6aj5UwV8d{ue<!3AzkC2|NM16g&Yu4!RjU4m<@)eQ^pt6Tjo?ukRp;(;$d{)i{V>LmPuBi0i^z2(AmB4P6GF4PJ#Hz6JdS{0sW^Eqo>}jlNwFTpHX6S^(S#+z_gR8-hzgsUMfZXX2aa+e^SV!QUZ>XCa6eK$n6SfEPh8fER&VL$82agPS6Vn?ZjD+vA}bg19Aucn*U2TPTf_Z}FM<SLh`0B#aGW3gS-?#39f!;1F<mXjyQ1a9-%g;Jn~JbXFQOe;|kh&=ueScs_I<cs{rxv;nvwI0H02I0N_v#uAO67YO3#2;zUBlfeIgCqgHHCxXXA$AQO#4d@iG0iFz{u{0T<iPK_yr2(e}r$!L}qOsC=Bi;ht3jGzl75qE&HTZXM8H`UFhh-4NBcZdwBf(pstH4{pPoTHJPr%hNK4~0QM-Y#IHUf_T4~I4c4+mF+mI7A;KgRf^arhWPyczl(cr$nebQX97xHN*e4s-#y4!99?5x5aJ6xtdb3Qh@a3Qh^upv}M<SckR*>)_<jIpE~rdcmj<oeP}<o(o<H{T93u{2TOFFe#1g-|(6EQv`7bXb89ixFfVYxFfh6G%vUu__oeU<NP*)cnvfFUIU&9oe!P~t_^Jnt_}WAW6c1jAWneNI8Q(jpM^dLp9Q}}5WlOl{sX2UP6wR`rXbz`Z#;MdcnQ=1F9Cl8oecg4ya`I<e-l0vm(*EPgG+*oLuvdM$7kYKt~ufrg7~*!oP(}_ZUL_VuY_&|uLNI!{tmtX{zPY`dE^rWabM_2FzFU>U+_T$aY_&C6EFpFQz*?NO%cS?pd-N3z*C{a!BfGZ&}!gNaB?WkBgyfZc)!lN8N46d8#)5q8=MDP8k`4w4sA~S8?+9Xg7_7*k^W|XHNyTR4b|W5-%#v-(v+_LkP>}{RCDzo;%}h3{-(bXFM%f4-}F!74bXb}oBmu6{oS5}?EYUL<Krd9N-cb@53U8C0i6q;0bUJV30@8U6Z#vNl;$R4x(7jP1;#^*f=MfZj|S_LP3Lt4KZ0ou1*spL1Kb%w90!d7lV<lY$ANPqhzCOZfl0pu4+O795U+u*0+S8^uK^E+<^m4}=Z2ounR9~^@I7g5#8CwC90c)P=zK8gN$_0oaVV{cIF8T6IT6HNq20jUu>G#kvtYV+OwUm7A&B=v*Ms+h_d#!f_ksU{(lgY*@R^vNW0MXCR|Zdjo&-+-)AM$^k4^Wm>G?A$J^N3OAZ`mC2W|_V4;>Gl4_*Lm0A2uY52a`S?eUp7BXlo#FX~22YXE5N1+8%)rFADY5X4iVQ@~Tf8=&8VH-H~N?}HzJX^jIZtvjiLAnpq70`3a#1`Pvu1N)#=!9FmpaUi92Cyx-soAABpd&WZJ!Li^t=oxSv_$l-m_$ipyl91B+hMEZCY0&B5>Dc}>1o1}bLvTc}oJATx|33j<09_1T0A2`<1TO@if_|hkp90e}f6|`d+~DpA;-8@B!K7Z#o3#qWw3dN%nCH#f24Y(KKy}WA?-2q1P-hJTe+cdYJp=9mJ_n_>8t3qt_#+SNAn-@vq0qJ9q2O@nI&e7nd*~4G5Y(TzPjFk`1mj}_@p+Ad_*;#Gc)7+w{FBB(>_rgwLJ;pm5GV6+5I6R45Kr-N5P$9AAa3H}AWq@oAU=Td`hXt<{gTOo^AofLn1c8ov>2Fz_ztuPn1c9EXdy5K@l9v}Fa`1N(0pJD;$NYkfGLP?K=Xhph_6FG0#guQh2{oR5MP1j0#guQqB$TK+k^2K`UChe_;2Vg@ZaEP&^_R1;1|$+;1}S3p$EYKg8zda0{;ho4Lt&W4c3#f9tBenCxadbQxK<so&Zx2r-GgWQxK<tMuI7b-+@MhDTv>N#(*h^GeG0O6vUaJXTTK1nV|__3gY*n=fD)i*`OD|6vR28m%x{>uZg!~fA4@k0`CCtggyc91n-7E1@8v$g+2%G1@DLc1Ktll2z?1Y2tEvb1wITmJv>fn+!lx42U8Fih28~I5Eq8t22&6hgx&&E5a);f0j40%3;hjDLHsfF7cd2}7n%sBApQ_~4NO7&0rY1u1#wR3WiSPCcIZVg1#wpBc`yZW7U)l43gY*mXTcQ28KLoD3gYz8STF@~I_POI1#wzv6qtfIH8cWDL7WnL5==py9Qq@eg4hE+2Bsj^peEQvUm~U-pT>{iNULkk<2Z|x2V-n7=pBMF&??|D;IE*Sz+ZvCgnkD85<CK09y|g(3|bC63_Ju{7CZzz2wECE2s{8<5<CFh4_X}D58MY@6x;{g3tAZ53)}-*5ZnXY4VoX^4IBo|3l0N!hJFn04E964U_ZDc^h0n*aC_(n;P&9Q(4645;MUOW;MU-l(5&E=;O5XQ;O5|_(D%Si!J*KM;81WQXnJrXa06&Ma075XXj*VRa2;rBa2;?hXi9J`a7}1(Fllu#^=Inem7$}-mBAIEqrerx6`&)*6~H0T;ouPPr_iC`Pr+rNgTZCMrJw`BrNAYi{lO)`#h`t`#lS_Ny}?Dmg`hpbg}?=%-N6OG`Ji3F`M{q*yMR9d=Ye(t=K+5N{Q~?EI5)HdI5#+##`6;WRD<f^YTz2sWZ)X$&!H*6pMz^dQ-N!P>q66j>w@b;-vQSLH-x?mZU}A+%>Zr;ZUW5&ZUSxw%?xe^ZUKEC+ydMRnho3v+y<Hh+y>kZnhTr@ZA;uB*g!pkQ6JhJTpwHy+6`O}To>9ETo+si8V0Tdt_|%1t_`jQ?F_C3{v6r~{5iNL)DNx+t^xf5TmxJk+7VnGTn*X*Tn+4lwg>ybRiW*`Rl!xDZNXK*m7#6GmBE#ut-+PR6``%b6~UiDTY^6WSAezvR{)oXHV2mnhd`TwL%`*rO~K{BpF*2}KLwYChJwq2%Rn20%YaKm8-YuMOF<igL+k6FEXm%yoVY9Xnz5~e2Na5Q+M6F*rx`pm=sIXfPrR+D{-u1a(fyZ;f@L``Ifm9xLC1vPiH?USSz0Ns{SUp~BxV'

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
