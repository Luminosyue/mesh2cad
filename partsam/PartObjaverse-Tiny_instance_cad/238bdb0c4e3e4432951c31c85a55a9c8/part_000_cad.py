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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_000.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_000.stl', 'source_sha256': '90c0b3589aae5bbcf00109fc876001a70ebc850a97a426e86d891b902188985e', 'input_faces': 1412, 'input_vertices': 897, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.426310658454895, -0.2966662347316742, -0.44961100816726685], [0.426310658454895, 0.3591820001602173, 0.4896734058856964]]}
GEOMETRY_BASE85 = 'c$}r3cbF7K+plMqC`mwqAj(Qs0YQR@2!kLwBSC`XEI~lBFd~?9RtzgBy95zXQ4BC3VNpRqM1l&4f|z{`U_Sj!-&NcFRR3|VbNsI7y6^hEMQu-ab#-sg%zoWE=F49u=KptLtl{o9$Dg=17LzI#D-)YGV)E26!$wT0J7Lnyc&ubPm;VeO?$WDsx9j4uX|dTghmV*tY;w(}nKhe@Y*Mp!X3dckCr_O`WWu0{lZTIxyv>jsri}3NDWiu>8sW8THM!#Q+L;Y5s-1ar=Kte=MZ8T&u55RBqsP?8=WZ4z^0(f;F_6bL9ov*{KR01VRDN`Hg{{Fn*)@^Q6TKI_ADOSs_ikvM5}Q)#aVp-L8<i*OJiaZMry4Z%`?s33Gb&GfUUpMxoZ_qA5oV69{9#lco3wL7D6e?*&B*N`*V~g!bxr449b4{>%41&?c{?=DSJT&}+t+Q`9hooxcYP?I(P^!4aDj4rqVmLFufGw@6D8`ePH+FYvqQ%*v8;MJPi|WunJ30I3+2ha|Gk{vui3vw=0}(O7v2x=EllUh#dUI{^2GhQ;r`7}tV-t>49tzp^?sf^FrB9s%?$VNTFdVrUl^Ttm>3>sc<Yza;|yPt8<l6B=oac9JKA?;n#0!RM&((%T7>)G`ooHJ{&c-PQF-jy&Y|O#yy*ILo+|rxZe-r5NqGAw4_h9!JtlXyr`M!qQLoqJ&g;$hNKVxLw7K4&vvy@i9!Ha_;~4v~Zg$i>F}a>6u_3Q5jhcrh*YhwIyK!mMJU6+X=ds59mPVZ~$vMrIM4fjg*XLcV_4|)Tp4TSV=k<V>XQubRS~pDYtQ$?HO-*m7UYE#ICBEMtl{@=?YNI(VViD^hxw9TVRQ@5!^?GY^XT6;{_R$tm+ez+h&yqe*rE_(?u(`TkB<l@(PI7%cGP%AUCBC^gD?JX^wb+uXk=Grao9(o@x-RJ4>93BL&Yk{hzv<lWx7+<Z*)Nse&eS~%a-;IW-5(3}k9F|3Q};Ky)BllfQzQG6JN<7PpWaTVKe_3jDtcDrb;{=II;C@S{+e80r*v-C2b-(wl+MliV{>(#a&nG~&DHhD$yq;buC7NqH|w*>_4P>SX8pJ0sOyW9bA7S7y1wXKkFT#UI(N2TU0<AB?;mx2adNf)_4P&P`uOVWi_Z1@(bpH9>-nj#FNxiS{rlB!{`^mr3g?O6s;2X-18+p;iD$12<*_OM`t$kMUnBFu^Zo5NdGgBJ{CQrYc5YOj8l4;JAN%>M^t?@0zdkoAH|Mp@TUPVud6V06qw>seCWg1?P+NcgKeaeFDo=dcJ=}k6AAg>oc{MjGPt0u*-k#^KOV9JcOW(?k%9FdBgvY;S=<>+%$@TcjQj?cOZa=x+{@6eF<wWiua%cZ^-kBY>|4pv<e=?&^cI5FT*T*+G<E^Dp^T*`Q{E1Iq8Z|#n?##~)eU^si`AvHcrMII*@$_{)ws+Gl!8~>>zn@Q?eS2g+pyZ5DUiwt}_tw}q74MDAk1ie)`nf0H_Vdl>Js6qCHn$Gt`RDujO<f+2%oFeRZ4t<mtFH9(`>H>>F)BZL{<vWO)R(6=`T1>+ZH&sBm6;OkpZNZMKX2Lh@r_aWx%W*A_K)>!=;vFPhWgw5gNLVw`maBbiW=YMYW(D;xv8k_x4GK>*qPd?sQqJewSQu*c5aN?|29|qKX!AUjZw$f=IZz+YyGz&YW~<<&7aur_clb%Pm`<pnY{G%4WW5H`yoH?@>}};HP-8q7h44K*xYaZ{JZKeMCKbZvV(c5`yM|(d&A<$e9_pPV4ke`qMv^~?fJ-j^O|L$y!BW=zkgs>WPaZJ%R}4wLsdV||K+ohdCs~Op>eA1_3wAr&VME{?>=f}Fi+H(;paWpJRO<evp>{7^-v{0-!=5<$h_6*aQ`!@?NQ^~T#cWMkJ=u&{U%r2pSry4_Ne`1bG3gG$98Rt+W$6J`#<sT!`q^cug%r*jqMw?Eo%PQT+N?Yflk{Z=cmcl{7in*YFlug$4az|T>nk3*MBGH{Ia=P|DBxk*Zy3!{yRDAgU!|Y@8qmMCfDn~le50ran$<n<gA}2*XzHNvp(DXpw@pUXZ^RiTK}C~jjz{#Cs*6A*MBEh`$w<;POkR9UjLn39bdivJGq)adi{5DH9z(GA1iZK<oa)Nz5Y8n=a<R#`tRhNzxL;<_20=^A8fAHe<x@CvD>NEe<x>sv*W1s-^p1&O|I8}Cue=O`$4V$PR{yobG80Exf)-u|4y#9U$6g8uJ(^!|D9azf4%-YxjMdj{daOTfAsqA<Z6EE^*=S~kAvygtKM%ixqiP%=jQpI$@Tk9PR{c~`*YR%M>;ppGwsh+?;q*hJTJ9BSG^ykbMsu+j-%cWa&n#<+g!aLq;vCJ+UDy02%VevBkXpn=iWMZ##hh1om_9fdhV@rXaA_@)jHSvUq7$bxpREg^Jgbl^G82_*14Xa&hzJ1b<+9ZNB-WM{@?plJrK-emz~@inU}nMd@xULZM8o*PHfDggTdU4<K&EE^W_Kk1jorL@Wi2DZpLwP#xZ&9j}h;O#+m*2;b3mZ(YYCi{OG!J?}lF2if*3<bNjk<ZeADp;PI_r4ejT9?hfU4KkMA=XY$OuroEERV`m!3am*^1^LdMiJoCfeM}m2(Y~S?yn3*%+^T@nx(QyB_7QG%dzRC6YN9(TNlAdp03<~uhe5l&i^f)C7hWaNjADJ7qJvLX{leP7>9qDm;SN$xQXWsa~be=hXM<`FMyYGW^d*^wfJhuFgbe?r)Q+S**m3B*e@cy3;hhA^31?l|gt~sBEwzI}6zklLLsDI+`<9`2f3q$==^B>ro?mxKjq0si!uJKWNdnybK<%#xV(s|~!vk!*$^T0iR|4xNM{j<vM_4C>Hei9nz*2(+QKezDSP=0jss&syId2)Z~cs;qn&x>^27uwEBtv^nWGyG7fe`@HUbe{G2{h|JeJ16@2xm!L8jdS|!^uHhcV&PE#%;E#mc`D!h-J$)w|L=63^}seiAANX!=sX&~%|9>5?Rlhga~_eWUMd(GC%JD!C^zFcIpdf-)^Ck}Kc&t`otyK;<obMca^}Cy)%mD%J-$94O|H*Jlk4-*$<_Ag^U>t`d^EW}AMO58=c64*osahQs`Jrqr#c_)&sFE69Y>vyc6-$MXvb0KqutNye6;&VosV`Lbw1j0)cI(SmpUKqcB=EyzAkk>+Mlb=M>~!>AMO5E=cC=v>U>Q0?)Gx}-<$LCms`{4g~{#tsB?2ZlBXWcO$EovEZshon{k|+aZG;nlkz))<79nt|KVV6ulqVT*M0KXQ)_nz$4L!(@K7)}<2X6v*!;ChABSGoyN?_U=Js{z+`KOGWQzg^g5w;$tMY+hZpLwP#xZ%SUWHKq#Jk(~hjMdV$Ya+w3+01b-LWs-f6U+MTt7E3xqfco<osS{a{b)E$@#s{{#^Ckz{&Z&(&p;9fs^xltKClZ+`!5Cz1WVUo*OthzjvElKR0l4ey_LtK|MEca-JL5Ts=2%ay7nwZs6o<`}K1JCs+GNKR0l4wg2^V11DF<S3fs!ay5VSa|0(=^V4~5U|z3!ZfwU<&yAg&=W;ez&yAg&=YIC*s^`W|&T~bZtLMf}&T~uqdew7dC+E4S9Y;Mkc5<G(+T*C68#_7Ab?tso&yAg&=f*Zy&yAg2jjx{@JGt6^{oL5e)&9}Xjh$TWfBoFp$<^`I&yAg2%^&^T*vZxW)X$BREi%*hLC)v2$(_$>tK5Drj@<d2w$9Dx?#$2CpSxDM{T!hAx%zY0Dz~3AG(T5=j#}mR^N?m7{W)r#o6lRCTz`&Q<@WQOCfA?iRk{5fuh~xhc~O-+<Ll3h>RfNX{=BHlo&BRf=c#hN|DDfys@yrg`g5B)SM$gD+@{L){M66QQo9%W{q_A1xpV)cb8~$mckX|5ZmwVE=j!_(otx{U$@Tq@&dv4LY^T2e(Yd+4n{o90kIv2g1G#hmqjPhAV)lc+|IxX*|1r6~|IxV`-?{(Mx!Qi`{zvC(|2X$QI#>JOx&P6*I=;^RkIvQnaqfR~uI8t6|6^XSzW*`f==&d?o9m0o_5F{|&GpOtTz&teb8~$(xxW9=xw-zD*Q@V;bZ)NiW*mM0qjPirV2-1{|IxX*KQa43-~Z^`-2a$d-~Z@bjqlw5=v-~TbN{1rwSS!ZADyfH@7(|BTpeHM{zvC({y6tPI#=`4x&LXr)X#re?0+tF`?R+r^B=zRpW|P#+#i3<sa3)LPOkfp8?Z96zsc#Js<F<WKif;K4)%9))jxS}l@(F_ZBGBhMH~H}d)j|pu@U#A?`vY0Yz)2LWWVU#j<aU7pKsW_DmaeKm-)FFN9WEslW$!a*`M6$KhV$3&rQwQ;qRX*i^Ka(=Vrf=CmY3=NA<V4>0fWBzu&5S@^WxHb?)^4bHa+q{^WL^G}y`f^vAKs#pK`l{q5^*__@C><r}v;wEvs>dF&iNxBFA&c7K}u_le6R`;*((MV>4(X?bWnZ$9qleJ@-Sn&&z<ua`VFF5j}K{x+w7^1|QzeEXr$>$UlP4=fAiRmnFV3hf7-+wo2QtUr#^pWN=Z#`)6EiBtXV482|_SN)SC8{|awx4GG#5~cinc;hvp?NPbzAM1HAC#t{6ZU54YGt?i)?l+V7@%!6+NX>MfSi3*;dY#;iPo8}JiR`HUHaGn<FZH+cR4VlS1(PSfTo?NOg3it7!%d#5^^kwu`TV)g&F9Zeo-EeeABWGk>)d?4-EQZ}0{-}XeqQJHdrT&;+`(TT_<X+3&FAxNUUZcIy;MH`uXFSHf4iNFrupCN;rj(TH{UO?<J>$iy?&bSFX-HSf5GN!Z&?vFzR8{OuYPcO<o1(0+kg1gWl{Ub<j(%7{Yy^d{wLS_KY6T2PUP_=*T*-Rb0|A%{+QgEKlLBXj+&n)*Yh(uYg%@2o~I5mKSyl}e}B#78SBE|UsJjLevruvJmAk;^Zg^0+wUKdCyMs*$2Z?^Qn~$p6M6EQLVj+(Kc#c?{V9`YwD;$~`F@tp&G)lRzWN4#{+sWAsoZ}5i#+!5O#gnye7{WP_WNaKoKNSb=ehm<n$FGl*Gyi0!HTHyO|Hj}6=wdc?Kioz{p*<jYX8_=?VniPA9JGizs=SDk1g(+6Low|?i}A0pJhkQACv3(6MMy<=X!pcT+h$gsae^<d7k{fo<HAinH9bsktZv34_%L9Kl*v>u34e$qt5O9hRF+e&x!0$ZtrvEw)cPT122TW&#QC0pUGpDv)_#BZ*r&qf)kS>`;$BUM|OFvMO1%s`+eR|{5*AfN%;G`D!1z-d2FG-ow~oto&Jd}lOp?*JN*}ROK+#spWO71J=4YC&d~+^=cwlXQ0M0OlE*q+ksa0F=H`B5c2EB}-u^;(zLCd@|C1e>Z*$4-cp*IBRBpG&<i-4Poc`pt{~Z(j*QK7rn_NGK*SUGlX>$D>-pP56YI8Nub#A{`ZnjfBx7WFOu4}hbJ-64nd2VcTbsp*5{9OW_>+RIf|8;JjZ`*Oy^M5Dj`MJ&2^M9S2=ks>|sO!7U)%9KHX8p9ey1wh&tj{Lb*LR(p_22Fvb$xeoy`R<f-O0Ir*<4-Ub#AVYc7LktyUxw^*N&sE?@rG3-HxN)m(jU-U&fB3?gw<Pw@2R(=-hd|>VCk<_5Qqlp8tJe{*I09ukI6^TpdS!pP+MRo~Zi-o$Gn1?-O*c=efR5u;Z)u#dNOEJN>?xlk4+Zy)UM7XWdZOah*H+S-p>@b7wtN@1yD5S#Q;Sg3g`oQSZAsxxQYg_uX`^uSfcQx5R|$em<pK==$#D=J^SE^7*x)>#xpr|JcE!*-`yX?u_54LUz>l*xcMdnC;A28@_)q{og+tzJD08DEj_E<@SES<of<W<#u~UEsDOMA$RU)+GIuFU+LUz54m%HrE}B&*LR}t&sFa9*Z1ctx3Bj%KX-m#AlJVyByZX7_t(#_bZ*8ccb;GA-1Oi5nV;+DX(rdt)Ao_;=X)x*<C8nj_f&3we_8phe;n2GNheqR_47$5H`}xE5C7-t=c_7r`s?SbD!2VNk?ZHZCRfjUV<U^EKQHV&f7ZE~Z{*JNXPuk%A*W<Icb>PC>*wJqa{U}$=XU>_Ts?=^x!wNN7y3U}zh7W-^?pHOt)J`nFLZ8SugTT>7dp4cYh?9wuHS!ga@AkI|Kj9k|J1MT=j#0?o2&Pmbnc9!-fz;m(_g*c6no=RKiBV<soajU-p}>>Zi%;>`1?n_-{<7!xRC4j`<&d&ljW`bpR3=m)Vc1j->=lUIgTsag<r2ZjyjkA-9mrWbn&72TUKA~%~-F_ij|3t91{4GrV^&7GmQR|rehlZU;Rnb`VH$}_W$=cO^ZAqkHuc_YOz;K;EV7DT(}f}%&RB8dWsT%20o2HgJ;3#@GN`@^&CIvdH5`R4u2M31fRwi;ZMLP@h9*{;bZut_(Skv{2_cIB|gck8{s4HVf+#NarhYi82duJtydkq>PU%Cpv1>}bpvb<JK*i{Hn1(;25$vh<E`)nY>6lEt6+2dD!eHrex+B<U<=qBZ-HM8TjE#a*TB~JHF!JN7H`YG5MS@j`PXGRp~Tn0*YI`ttMC>4ReUX6gRjL`!<X^Z_$v4kz6xInSKz{B_)2^^C7uJbap8-24!#sF!I$DMz~}K7@Wt>sd@-H{pTV>6XW=6JS^Q~A{3);g@al|Lr{VATY5X_%EB+h)3;ZAc3;r|w3I7@Y5&nSxh<^{i!@tMBh2P-c;-}!(_$mA(Jb|CYzk*-lU*X5$7x;1f7(9v}!;iqv@gw+W@KgLV{4gbc$g6{1ed5&t_%VI}-w!{+_v8EE9(*6ZmlEF%Kg4(AyWmb-_&&Z1{{Zg5KfvFE+wu4CT(}j_#kawC@oo4PxC!5aZ-yK3&3FpFgQxHf@GX1;{x&84rdJibwc}i`%ENMadAuwvgO|n6fu-?t@KUfOUJ5@OmcY-(i^F1gal9xjf)~Zlf`#$3@ItU4UI;G$^Wz2Zd@uvghsR+IkK_NveEu8rT}u2P_&5F!{ud?wXUt#UWF0&OzYX|Hw1wXX{AJq09|OLIw(#eGzd~F1OTb^FE&MIuuhSNu4)}W7!aoB325sS)fUl!1{5{~W(iZ+2@U^ss{|oqP+QOd#zKXW+hk&o7E&MLv%V`V033v`|;nx9QN?Uj$;4jb?ei`t^w1r;;Jd3vQXuzMPE&M#-Ptz8D8t|uR3l9Z+5pCh&fImZ9_*uZ8qb)oV@aJg@j|F@QZQ=2Nzerp7Rlu`p3r_}o8ExSyT-HWeH|2a47LDimPTIoa@jU;Kw(#tDp6{V8EEUi5k7x_eiRbypw1s8kdHxA)VflETAEYg;5YO`iw1u)(8sAS_ST3ID`)CWx#PfVFZDHwnp6{kDEE&)9U9^QI;(7i7ZDFx^p1((1SR|h3xwM6a<9WV~wy<D4&$rMP=8xz3X4=Axc%G+d3uEy--#}aVZ@}NCE&My+Z_*b28SuAg3;zoEJG6!W1bicH;eP?&L|Yh-=lQ#|h56!nzLmDHKs?X4(-szr=lKrWJDBg{%{}kx)m5+yeihzK=8DWCITv6>Tv!R0%TYnu9#{a+hZllH@k01nlz4Gi2``SHO^KJH#H+&dabaa#cp)yVj#tGS!<xA8B3yV0F06wKFU5uRabW{o*a&aLer!yMH=)Fv!e)3=yajB9x4>Ic;@42(ZM|v_+fm|eU@KhM8gGMNO^GL9b3B1x39rJh#IK;lFNckAVMAPa87{1c3+v*-+PLsyTv!Vi*1#{vtHCO`FcTMEfD6yVg%xmNd0bc)7oLMx!%I`*C1Dx7BwhlR!-Yk0VKKY}UW5`a3=86g@%)r{1|=SYal8QS4zMF$l>e<0?10OBka^Y(cEQJZH7@3#AJy@ia6DcUzX(pmFTyW@H{zGzb>I}d4t^=T3BMGt52xex@dj`v-T-d|XW)(ShHx6*5Wfsg#V^C_!O3_%ye^!C*TrkY33zS%Vt507F<uLf#cSa;;Ap%CUImWCtKgY%IG%}L0Egli;OD`?_<48*cs*VLFAoRc<#9PbWNygXI))M-1uNsD@DcEQd;~s>5+4F9;lhfz@LYTdJ_we>2jK%@8GIn#AD)Bv$NRyucv)VfxLhyN*MzuV>1zUPf=h|lflYBK@k?O~TuQt?Y>7*WH-OjRQsRwZTU<)~@_61gKwL`v3fK;p5^n<A;8Nm^;nld5cte=LrNl3TSK?CQ_23n_lz3fuIWCo6?_o7uO8jD28kZ8U1xw;m;x%9iTuQteEP_jkSAm6bDe+90AD0rp0A}D);+0?wuf&2}5yo*T@$+ClTuS_WSO}LAuME$^rNl3U#c?U|s_<-FO1wHOg-eOogjMmX%y)6QcF47&80?G-JL1BExLi}@8qyke$Aw*SVRQURuO9d63HT`f1pXK${s?>+7e0tTf<HuwKLGE?AHeT}_u}{A_rSYx;hp$B_+6Cv9q@KsxDdYszYX4s--a)Mx8Mu#`ILAP&clT_<4JrjoQ==L=TPFaypsQqdOf`A1$*Lsz3T1Nb+8Y9!aMd~di510ejI**AIFcuqxdoW2>cvBf`0}-#XrLj!$bIC{2)Al3-{v(@lPo6kKsOCxEKEz{|N5JKf?FGUHBgSL-+yyA-)s7hwsGShq?Is_zp^ZyH{<zh2t8pTEkX&Yy4{162BTxz!rD{Zw{}*o8!&km3T9}DZB!2iZ_9m<4y3!uo2!EZwMRU4e`rhef%=K9=sH<hu4L5@Va<ycnMw`zZhPGUyRqH#A|xB&D+;oyxIyk<6H4}VG4g2-vl?{oA8a4_&e}z{2lx)_$DrV1Ahx&57*)A@z>$2`0My<a4r5C{t8@;zk;uUtME1W%Wx(BGX4@=j=zMjfI0XId>JL4?NtqLUsw048mx*}!>hmx@hW&Gtc+*k7r^uJ3-C(tJiHQK5mvw};^)Hh__=sFSQambmx1TtW$@Cl6kZxH3D3q$;w4~lyaZkh7R8I<Mc`R@5xg)ZUMRy~-(($>^G_(}r}0Cyg>pU{|CF{+&VS>d(-z8lVf-j<p{y^)zo0FY^~m^_w1u*M89zb$1nZsguV@Qp?K6IywoukS<Hu+VW$iP5gtk!DKI5O!7RuUZ{4i~ytbN80(iY0vXZ#b|LRtHae@t5_YoGCtXbWZSGrotmP}V-<AJP`e+Gl(xZK14v#^0wcl(o<J4%$Ll_l$3+EtIv;crI<Btd+*!qb-#6)c6Oqg|hw{-$h#}>$UOSw1u+18{bP?DAxny`)CX0`eA%O?fuMmaakK>-IViHDCe{BH)#vy{5SqKZK13e#y8Lw%KBnFMO!HAk@3y6g|dDb-$Gj`>z(m!w70Q78sAD=C~KwhcWDb{tu(%gwouke;~QxUWvw*+4sD^VmB!zqEtIv=_<GtxSu2gdPFpBzrSaEj3uUb|{t9iOtd+*s&=$&CY5Zl{LRl+~zeHOoYo+lOw1u)(8ec|RDC?y0Y}!IuJB{bi7RuUcd^v5QtiQ%r(iX~kZG07Np{(!5SJM{C^}zUA+CsU07=M+vP_8$|*U?_bd>8*w&UvqXfbZcy;NQ#s@_w1D>{Urhyfh_Vh7vDFiJzO#ALn;|&R1TY^y;`*U%)RZ@e}YQF8mrlfqw&k#J|D6qr`uPzvDmSzfj`8!87=8c;S3L|HOrV<HCP&q5P6vm^UXfaAAI2SP&N$!3*ORVKH1-0vDFTh3DYHvbeB3UY`A35mv@4;*}`z3t%RG0bT{xz^mZZDDhfeT?{XQHSmjIO;`gLR>y1NRVnccVP*V6{CrCMJW9L*JR27l$Av|4;aPYEybvsa3-jT^I4=Az!*}67xbQDr_y;aLjZ2CDO7=VcEB-%9{3rMW{sZUSPn7t#l=vxl5<kg#C0?C<y(`1#hZ(+CX8(RbAIU!8-^y6I@I8EuS1)Jy`$kGUAAAXy5|6_bxRm&RWXtgX@PA-7{tx~ad=dW({{t?;|G-bf#rSFbclZMSJAMW(#n0e>!W{fh{BO7%{~P}ouEhVvWepIn!llGB;A&h-JU?8EONkeRui{eTMc_JIO1v0+1D6sn0pG->#7n`qaVhb0;09buyev%NQsU(~?@Dsc72v#D!~79{1s27n#9xEOaVhcFGyD=?4@=_0(zulPTd)i+CH@X9hf9fXgy-T?;+tT3ygaW_T+Ze6c^mgDeICRA8IN;L!=H@DIgjDD#^b*K08imk;@`oqa4GR`;Bj0^{Ofq$HC0?n{3QGmml8h(PvBDG-@<QjDe>>&ceqsgS_^;1rP9}1_>1v4*IxLW@i^CBDA&cb$9+EyE8<e(f51w(l=xrp0$fV`A6NyK68{fY!==RI89r;_QsVhC@~(g4QsM>RCAgG$!Hm4?qPUcJepnNi63>8DaVhZ_ybzZX|2OXQd|XQWZ+IRqCH^O@fJ=#=frW6P%ysd~TsJb|PF(mQE|lwyxLi}@8uB&VfeYWqg+Jo+yni#>tDE6;{APS69E;DyZ-D*q8}I?J8$JN<0o&j`@OH2n-VSdLYvaxF%P8?f89onW_%57_AHtJxDxSor!Lj%>{07($zX2ZrJL3cJuCP7c74JxixAm%?x1II9I-240ScdOX;@jYMd>cLs&c<iqli?J6GCm59#z*0U;ShW<-Us%@``|rbPrL`-3--o);n%}K`1SY*I1(R$Pl7k%lkgdECO!k-0=ME@@Xz59{Byi+KA)H7^Ib~3F}xgaj3;1AJb`zDo$*fiwXhd{Ej}0y!3X0b;V670J`qmBC*o7#P54y&MmQP25g!f5;G^-Oa2P%m?+yFlz40!vE8Yda8n(i(#+xv&Wqw})o8V38a|L}GFz<zjneS4End8D+@a_0)I31sjPl4m{DfnnO5Fd>Xf!**Scwg8F?~C_@?eLy>Z`c9vjSqrd@Im-U*dHH>-w4OyH{vtlP54ZFE1ZXK#gD*)_z_&@xUdfMU8)XqTzD0JIo=Ys#arT?VRyVU-V64}d*MUiID7~`3eLbs;gjGTd=h>WOyW1;li^%^GCl^*!pGpln0GS&TEHvt7I=Hu3U811gkABT_(0ePABc~K!|-8jgScF?4l(x|;4<HZN&GN=3!H}Ef=`Dx;M4K(Z~#6Y9|*hR1MzOKBi;?~1l!`B@OH30-VW~oJL4VjF0dco1@8~X;{EY)a4J3yzX{I8Z^Gxn1Nc1rAgs;YKZwhG7dFG|;8(#m_*HmY*bQ%scZdD(?s$JV7VnRbgVXVG_zXB3pMlST^YA%%65fm_@wsp&J{O+_Z@_2a<KX~&JU$Ti2+Zdm%y(hC!2EB=`5|l`IA5A`J~d~qw}1`s=e=W*<<)cWS^PQt8Td5*4890Hg)hRNgiqj4;*Z0}@W=5-;UoB?_`~oa{9*h-O8kEK0DeDyFT4-G7rz_cgWrwc3Gc%1#BYap;KJMR+wp~P0lpBwl@g!t)jqHGd-XB=1mEq|Ua$7RkML>Uv6<r41ULepfDea*@ZtFN@H+f@yf5sC_r*KFYw!+uYj`Ez8gB|4;Z5;|@Uslx8{(g4_<R@t6yFSQ#y8`0;6!{5J^_xwC*Z^3Fnl;Z6kdl9#jmBryL&a;`(199SH0l1cvr8wcy$w;ig$&*;Ou};r9G9gjCY~kh4GDdrQMY=#2@f#oL3LxV`-1@>Rzu#;dckx_tNKH{+;o=Y2VFQ#z)W|!T82U(H_MZ;`e)XpI2kxXndGgL%q5a-hmH;W8nP(zk~K2jAeW%?V*fsd>HLvj3IuPS0lZ;2Om!Rdao9GH3(l2XfLGCLjIlc1+*71mhtOpU(fi)2hkqH7~;2kb(>d1;9$JJSN*)Y1t#(Sa0t9T;7Qs^#xmZIc0a~9-k)}V#t^^NtNC6HgahzCUiJ3sW;h4$0|&xe13riL9L6%<n|5!;H{OSKAI1=$=ha-Vu7iE?o?i9vY9^e4_k`EMc>$k6dj?|}??Jl<;~VcuyC-9aPxoq?SKVPZyt7xGyqW?h<DFr5I6dH#X-{S><DF=CVtnJBX?JD}@opXC8D;Y2{jrONyW1Rp;#%)od9D9>PxGJ518<}elc$d1uV3hY8U8aF!GF2m8_WLDjBXtZq`%vc;r*X{QDBpNDm3<g0L7V@Mg'

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
