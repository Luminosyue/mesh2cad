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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_005.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_005.stl', 'source_sha256': 'c0623571f130747524be42eb8df609ad49272cee2ec7a1d3a649537c924d0039', 'input_faces': 1248, 'input_vertices': 688, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.047344084829092026, 0.33014532923698425, 0.09314312040805817], [0.047454141080379486, 0.39058831334114075, 0.11807173490524292]]}
GEOMETRY_BASE85 = 'c$}r31+<mL-?sN5m5}hzwF&7yfHa$KIg~VPQt9s6ba(frLqbZB__IM;K>-mI#SK!TfGzENX6_6BoZ<b}`qua1nss02=Ev`uXJ($BIY!rx8!ytMKUqD)2Bm%EsThMXC5b1}GoWLiex2KQ>|3x$ufY+X<kq);&^hlkt{dGf!ZW}#G*^d?ecSiRRoa`YY^RdB@_Tc2>e;7XpSC^P^z752qw%Y??bf$rjNkYDw!J#W{G7W)$&&fKQF-!vhkO4Y|0Ig3LU?Go4Tp?IKD=1L)Tw{jy;he+S>IpbqV)rzeAW+U%wm1-?+2_OdKhW_(ATdk{_ZCExt{DX8h-rGdK<req4H1pPJWeT*7s-sQ~9@#wt2!G=O{k@dBs2LZGC^2fc3)>`{Y+>t?l;cuK3*AZeVg<`7_#EKbUx>;@_)d{lG7$*V#PhAE=)7ztsL_I4b|^Pvy5cs_p)?OMaD|$}?-X^}Qq3$$z?9@%y)0-?w9x^@DYm%73y~ewikU4+JjTdaN4xvDJeOt?%tM-uj{1dG@Iv>MGCp<??@<X5&LGYb(#ARq_iKRD39o;#YK3{<srue6V?h{K#(B_ua~6;{yYquC;k~4_ExApVbc4A6nm^XR-4C=+Slq_Z6RNqxC({kJ>z;-9IV5>p|tYP+9efD?eCky8QTOtncl9)B4_W`{jSWP3^GssQd&6lt1lu)pOG}`JoPqKlV)hdv=w!``#yN=bG7V9)BnNHvJTT_>j%xPa@x2=8obU7qRiaV=J^@Y39hERKWV45zE%TJg!2Yrc*t?SgQPg>{9-gxvlTru}J=c#TthX(ks4tE9EcUOzqjHjIEEaLsRAdVv+XujWrr?XB#NKaRcQquu<(lu8!hsjFkWP6tzQ=N{TPgUj6&YM&)1cQ+(O2%0E}*JTSDl`laCo`H{mF-#$w9-@jA&XZ!YB{jjL=Pd%mh^iLE&$t(ZSdHFrAt3B6c(01c5P@X}JY@Xokl=9a$R68uosdi44O#Y4cRR6wfH4b-PTVwN&KCSqV>Z(0gT$caGVEK{dY<~ZiPpt31q;~f0y`=puxJ2=V_bEQUd{6WY>j#&#m0#j7joXv`6dzit{hB>ld3JSG{;2wje=u0>@O^#dxiC)q+f(N&@6$SpzgkmyhWudbA1+^6{^?0NpRCxb{>>R>eQ%=6%AcTt-LLS>0`iyKkbm-o#`D1Zs^^`V%5!J7#{Z72if?jA@wwO8Jif(Q<mcl&Fm0CFVRR<de`6i_I~u8-JsIQ|4r=^Qo2>ron^gXgn~JZJRqZe*iSqaQ*v9)Z&QN?IkNk;E)efJ9wcVW0SKB;OuPVOM61Btoe_21gVTJOyKWyvoJ#$|1NxxM)PadxP?RLs9qT|AMMf>Y%JKg&JOd7X=LJzgwL0y%<myVaf*v5+gC3^MC$BVD%dR>pk7Lo5)zx&2~q4VB}bjovlhWt@8HBJu3(RLHpk{>Lrakb>fRkohnuB#owE7UJ{?pQzkSs(dbc53{@zhQm<kH08S+7vcE^!j(!_fD#-{yjBI?RM;Q`SV*SPtPRk$1P`+XTeGNzdq7-GagobB7Rpp9O$I|y1PLBnDv}L(;u+yaAkt>#Jj8Q<~yY0{ZT-^XROBI^RgPBo$719*6Fwi)sJKI_?Fj`zewZXcPfpI4<D$c`k(ts^-S<K*PTqNPn89Vzm!ndh3yICC+MvBCm(9RypLDf{Es-^yWiG%^4AB}52o1`JJ0bmitl|v<NWvJ>aT}K6u<OcwZpx<Iv=LnV}1W`x;}a)UeLI@GfjTKdfIN(1RWO#M$11vRC%sz90tmdw7&PPAC<@VgT~?Eq1tYjhq2F}9l9xgkj|f;{nyk!XFDnXtajRN;>POt3vCp??5yH5`fU3L$~D*i?tdbG^arYE_$~Q;wkXdh9TeX#oBY!nC!P=EtG{M`8?^qBDH@++qYu37`!ijW-#DQ9447&CV7g=SCq}9MpUhBvy`J(vV4P$bDu456^~)9=ci}a)<mYb1^>>7hi>Wo_w^<{9Usi2*RbFkk`gryGla=cC>Zz^o{p2U@@50R5-$Ievul(wF-_vh29!{rJ{&uw6xf$xOf0D_sI97Qs)X;H}`N0aCzsx!1`DU2S@5z40`r%2<RnLLNl)vds#drEg{-Qg&Uz&DZex5GMzki+DEx6A5!6CEMK69t2ed3Hz{HPC==l9iiyWZ}D<d@gD3VmNi`ST}Kp3Li&=RJ+v;M@nxZ9U)B`OPzOw)&;eed`A+-%_5x4y&E3&9lBY$!WE7x#`-ke9e_-WM9=MO?9>Nv8M95z6b6MP@V?omRWy0*X0REHU1BLD*r0?pMg#~|DWk-{oo_Dr{|lj8V?CtTHiZ&lJc*euKVHdYg*r5o%7hPMz%hoo#mD1)+6P)cTDG#S#K#%_cn~@p*p`k$+9fgxb@vr{?8*7U+4?v*|<~vKIr*UwcB&m=lv|o-+k{=#cO<eCbrVJ3U8I4Lj4%Z^{w(WoooH@%D?6B8>aERET7^(RDXriex~@LDdiWSzrK5{@pJBnCDu<hQTMCa^XNMJc!l-DQ*{6AJ2*=Hb!oiygT+5p{jYqe_Ro~r`u-~1e}@0jdGc{Q#i#i|?T~Y&j*E_eF1Fi^(75&e`iA1$?UsMDrSjiYJNSA9tsgF{^Gs;XDdm|u!214i8Ycn&9`%dAtKv)d)^-==R{K0Cp!n^&kMgydX!py1GK1oi{-OK}bbSnblwR=z)~H{Gzoz@l#PQ^3Q9Fb--`4m!e0h=GU(VZ}HybKX%FXgms~tjbr#NW0|HC-z`~N<s<L*pS#lPLp`rd56DG$#<-uxxy*PKfGM<~zuXA5op2XMZfTS)sma-a2s_tXxdqI-4x&Iu|$&J6W?ov$_CDvVNm>l57f-qbjWs;c-N9FL7lD9@x6^6P9+e2K3#9=^G;!0y*(-G>As=IVG19khOUILG6A|8U>C!}`JUx{nQwU!(ZA>y&4PU)vpaPy4lgzTyk^Ql1vAb>2(1dA{}k^Ns40`k?Arf0gyU33>mJW{U2s8_c!7|1j6zKMQD_H<>1X$6>W+>P%|qI`!pezOVYEo}fJYs%X18SF1jctJ(O#;?&j;Ut_yv3R*wh<hOa&PkTpsGThXC*P?sY_g~d}gFyVS#?_PS^2h4>;;CQK=JA}|Wc^@MJ)e5wjnnw?%vJt3mZ?2wOwf6t<V3}n(DQ|FVS8;i`2g#Ci+7d3;l7TG;aL<vM$Zv}2kA5pvnE&m%k*!K?rOLFapm9A`QKAylIk<|#9W&{p59mZ<|NYn#_#*&CuyQQnNI6?-#XFy;l*4}k47mz?HKt}bbj#M%BFELrKj~@yx$0Poul{y_h#Gt<MjT=*C|^4m|(B<gBRDyk4mcc9Jy2RS3grd%m1Nvo3>o>74^LD`?b+Q9gp*^@1Jl*ei!bSMzxdQV7}^eZKRD4UTvm4`!{I236JQ0X>udQpZ#8WrXEzgWlpa83?8KYt<uNl@&Em7mW?mTI4_w&?H2mT`r&pQFMs4#J<qO`Ut8xZ->yYEUjA-peQ!6tX9%TPukrRp^sJZnH;_15_XAThD^EP#-+EfdRsH8CSDpn6mFKmJy6zABWu~p?%*M)-zJ=<U`i}gshRL7PMfDkb#rol@dVl4+cUs%+-d}#gwHjCF8ruB|oldJfQ6K1d8L#8ilPPkVt^ZBENAfk#tK+fI!>P8OQ@KA(H&x?d;Mdmox8r<%VUhZ=*L?X&Cdf~<S9wmiP@avSEC15pbpC9gT=7r!JQ5iDf%?7Up((ch+~;^|L~GpsG0OVE*SMd*(@yo7pIiPa>VNdC+OtMH<yl=#ep8(v0=0Hdw%g6i^IC>+YR`$Q<UgsR{8h_pJg4nweec3)^7{<XalNOd_5Xbj@aJsRGpda8?A37>Y8Mg9e{o;udpD@_^OJ1jY<x96M|dVQ*Lkl;GV2G^%~O1XgBs71Z;rL`^YuP3RQHtXS@y8?!`}{M+}>5czuwpS!QXXW@*K>{dA^bIbk=z(bn&Xj|I?qx*!|^wW9a>nx{i0cEx&73wcG6Z8b23iTHimqwBqALD$j=l760OW+RbNb=e7;ycT;@ehaNgEhUc+<xItyrzo718|MeT|`7tnWm(Eu+lUhG`j`w4Cis(F0C_ec|E6>kswcSPkjJA0`*LVx%(eqL8s|CYso)*Da=b!MMq1N|Sov8YM{DXXNZuv*FU!iw&{tqRLuzonRt_y)PDgI;IElHc9Hh*!wCk%C{X5)hcnpywF`60A2fsOa1I5@=mt4hh=^B?tNiE%?--mWjXuKS)}8(2U1Z6U><Eu(%Jl}dT;6qf&Vp6c1@{$T50p}*$d)qU)c^YZ)ho_wmV7s0wG<nOGl?N)B0?Y=(G`oX5$=j8oU$Hn#$ieJQY(2dJ#=W%_l@BLBd=g=ITuYBI(eXO5C=R;rB1v;+V<gkADjNVgu20YRE<nWc=cDxN-r}$>^<$FH0esFy|wwuScr!RA~{AoH51X5&?f1;H97x&veTj{uXezTXY&$uEyM_f{Urf-m6H8<l~=T%>c+49d(pTqk!4uezWU&<rjzeUGs|55Uziz&~F2>F@1_ImmF^8L|W=Z%U{)_?K578spa?cX?!;=kp)L%CA&pLwhwuBP{6fuF)UAJ)3q)B3$9((e!CPb<{X`pf2MyQf#FJ=^AxUqJ6+JWm*(TXuD@eqoK1z}4i6AGOi?{$F{|aHP26GbB}fsG{=xlGply3K!ek_}jGGAMdLjl1`AnH^2M@I_?4qs#xDUC_DELZ8XlWl(c@h#9P|0o4Rj*;lDU80=<*y{NFT<^5;-}LdOTGzc$=$XY+i-epNdzKj$gydr#^8MyOG0weyk=@(c7(ebW4__N?-b{L8wZ2_31TJcsgI|HXZ2DD+tIry4c1{>fSLAFtDX^(o&_$CuvQ2l6FWdmcF3z}EA{{p6xjv3&1DoyS6Nq*9(HMXm3jT|w=CqM+g%Jg9Hu8?TLZU+Ss3S$?a$$}{Gc@+=)`{a}Kuv97-_eDAhw@)I36@UkCnR6y<XAesECo#pQ+ulS#asy%NetFQKHr23ps7t8mS;rqfs-S>J52BWRd`}u#zbD*#MYPxQQ7S&LEo>tZm9@BLpwBWhoJ<-R@oBA~L#@??N{>`kh_v?ip;<*0qR;+k`|NOD{_l19<oc62Au>G<8B<h!dx6prH_W!-E<x3wsp6j*e_foOqy=!?Mx&I*6e!V!~dd4M=6(4TQ_3_u(?cg7$ap-HbKGuGD<8mMJdyQE2@mA%!c{o+<c6dYm<@@4v?E2@{c=L>4yk%<@UEzQ0m%)9l|4KjR3d(o;{c5uM75=yJga69-Dc{-puZ+XFBd!0+ILCiwoa4VT&MR$Jyn7tgejwjH?xKq}u=RJ3)7@vS|H|=>|H|>+wR}TcfA_p`q>=SsInNx(-%jo3oR=!TV}18L=2_4|zI)!wdP=@~o?Ls^`tEr(=K9s%Zr3>vdoGo<{wwEmeD{3riCe|`uUr=rO;CR4I^rpNQNDZKNt3jL-L7+;@(kN({a3DQ8+R$*xej_-=jdpC_qsW`kbLJl>#2URr}drda^Q)lm-XH2c!M<7f91OGi?aSJ_X!!gD&D!T@bnoa-?<M7ET1ahxo-&+n=RkH&zZVGzH?s`czRR5a~~BrR;stHr*q%s8QXWTjd$)31KUPe-@Ts<B%C)`<2?5Lr>D*d#XI+_fr01cJNLJqj`!s|_rsnMsfJkJxql8kXfWjEarp23cJXo6ckj;wiP{Xc@y`8!VBtTbZGPu@Bvdf|7@Nm=e(}vnYJK;4#}o5>Wb-)BP5=7NbCW0L`Ahj@KY#hQ4V3RZulb(*EZ=z^487KOtgVmpTp8#$aFX5bxUG7hw(A=`cN8r%S;wRET#WBN7yCYHY5iB8uTyulzWY4xiFtmv`JLzYP|cn4o#*|)yxdc4e&@YGAhMEt-aCbw{-XWraLD@Zdx^lQ7E^6~oc9}nDJ`w<AEoy&fnWyi>;ATW@S_3Bzo4Ryi$iUv**pze$BGX<>}&mCTILnhtgbv+0@n98pQ`s`RrTH=P`<!)ThIHNf91=q^Ji#TZR>mQ)RrIlNPhmo*7vtqr1wSNwbgUY?&>pa{B8B4uh$PcPEV(uY2%&uNWuQ~tRIfoTlIW{^FUO4#UE>;{He0(Il5ba#XIk*{J##c{)_J{zR!EhpEN@8>nkdMzMs`E-IvS%QuX(x?x*;%SL8eI$3m&@s6Nj7wBUeW<U8-*{Bx7fvh{J^*LkO8o~8Yb{eI8)MYQ$Z_kp1^D;4j&R}5wPRQ|_$FYOyYR{iqVGwZ+d-g0uI+17X7e|oMqoBi^*eeu3DlyAP`-S@8X_bT3buN&&{mG!-6>#Cj0@_hH>CB>gEuJ~J@YJY$K#`@tS?<>A#U5%go_mszZpX}LwU-1#6WA&Hk+B4Pj@;v$12Wq=hdd{`mb>3Hd(vGqIEAO|rOqB1u4-fse&-(8BbI;fl^4<6C=^k0%KTqEme7-Vj&wX*{+5FCXd*5}h_1*XXzPBgJcfKR|{+XjZ?stb1n-uSSrwA>)XMOj3hp)+R%Hw<=@$LT0`riHdl)uL;_4}1L^KJetRg^!^HSJeKGV6QSwNd=>Tx$PCsjcsRm+|DzAb<T}`Fk2G{-Z3`_kTZ4c@nnJxT;-WzVkgO)L^cB_q$T`D%HpN4i!qaS@n0nTdkkJ!1~U2E??Yr)_1>)d2;Shyz?E+7dmKt_q$u*>l@1Be5dnFO0m$!JKyyJ<wsfnmG6VIgNk>*Cysw6-}x>XN?v)9ZHK+o^L&1dlehcHcfNc2u8*_+E8j_Xu2B3Rd`BKRmFJW-)(?)&p>}RwO5@?5J&F&ORXuafQ2efw%Fp>c(D0jBelTiAtnnFWd_nOebY1ZMoJi+~Z@yG~;&F<<l1%>L%krJ?!k)zO7TY}TcjVpa<vZV<eJ3+m-~CSQc~C&{&UbB}zpLWi@8DAgDBk&QZoaeIc;`F2r`>MryWiyl9sZQ>e#d_tZ;9Ps=evI>V`l5S^8`GX#w*^LR}gx%!usw!1kbr2tnbcS2n<QN)cVdm2j8-M@|}4RfhKdU|H?dy@3$)6nRgNBwpYG0Pa`n!x%J(79f8jymnq(v2l6C~_1$?RW}b<ScjlS+()q0K&Pxe=UsHLUc`UvJEtSWa_Y(N5qw+ZOWPHbi)(@x4s^csB5&4@!^81w3{?1IJb~x~<d}khxufaL_&b%GpUzfGr1Pzt{O~2}y@uuRRc2z%yr^fQVCr89SPLDNRZsT9vug=hXp-|rD^4<AGr{`PWosSeMcz?P2%bCA4_kr>_^PK|u60WfE&ip7(_d(Wo=Tn8^jF9ilzw!jvDUUN>%QNk|;@$aOO>W9}=7WW@-Ld{F^T#qjP`oqWEc85C(2f&lep>KUO8L%wHh-Z=>$~&c{MA!i-<>b#U6t4RugtHTT0{Ar`FNo<wd6bV_rjTn%6I1b1wWY)jCH&)KhVr4w14l;Cp>&f^&g_~?Au>h*V&oh%6H}~zVO}oioQwr<>%G-4?G^F_8IzId9K&zzEQ_ZFgpH9t6vS}IqSCKFD9^l_<3g?M;Y$OZ<kHJGq2JceoMYH57Sq!xqNrt=7l!acjtKq&vvrDJ1^AVp_}5}d8DDCs=qVu)L(w2;+=V_-UFkR-<j7MzCBI8I}bM99{J9^+2E#6v|VSOt>^d|?XNR0*Z=DS#XIwOz23))cjo>2wkKF+<DGfJfj}nt&b;E_flAhQ=OKre)w8}kZ`s?azI<n%bMRrn`mfB3o<32&GmkoWcY*5T%)9nvJS^Xtrycz6l<K+RE!Ai5R2_F)&M3b#-#c*ZbH%&!!(abSzB8XZ9Pftmxbx44+*bTwWwc+}F6sPp=Z@OJna3Vp{G;mc%zF>*e55>IHd6maCf9jj<TGt|`!M;R=F{<2J7Trf8(c3g7Sw(njAMOwzP*{BZ}U0x^UZvIyIp5KznTAUeP{l^SubG!owHsb?4PdfI_nEUZFj1k&U%FKXXoWR>lXs=|E2uSdWXPU&lT^ij|dm^tg-cU*Hg?%BHvkm5$==J`tEuSuP1|iXMIO-R3`b(dJxazEXwb!AMx$TD&JXe;u)CV`tJIa(98mgch<86az@E_*1!16SGK;pUdHpZj(lf*jraTds=u=y$G5Ai;+^$7;S>E-PiMVPINc=q6AP$4XMC&viZfIBopnRrYfBXGtTXb5Hfp~fR95|~tNlGWcB?+;MydVV^;SDP+OIr`T57ws8Y_R?L-LdLQT!*0_ip(_d7O1m{uP%M@2ryw?YJi2SyvT`Ot#kMbJk%6W~Y?ztlJ8&%^=@d=jEB?wZ6M9%&a4`zO#<Z(>}`j?z%Jo(Bjs2*Qt5d`_{gEoc_D6ElDNich<oL$JJ51vu@6Nwt?cEb#~qkO%?B~%kx!lrFdr@UvT>()!$k7=l^1<d}p0tX!tVach(h#j;>ICcO7DqRf>1kEqXi2e`THHS$t<*q<7Oc<#E<g`j;M+@2tD@biXOzS*K~%b=v)Q)^!GV%Xim-`UCg1U(UKwv(D81y}Qoz`eVhf)_s>RkXQF(1E0!w)~ouPN365kch<Lt55<x1tcMK;->|;_;A9<-$xf<$PNcWKcUL{NTcWP2PwQ-oPpIorpp>2$Joj=czWjUgd#=#=vt{jd8vn7^=Z5;#RehZGyk`Bc&Eu~BEz?AKob|%t?W>f>SzjC)zE1JZdgSokUGkmv%YpPq<vZ)0J-?im@2rmwM!mk?`iB{xql>FPuO(lv<3R7<e1)be{}(x}?;WJ)g3zYyT<;26-(N=Ox6r!dia%09epFx8bJJrTcQe{6zq5|p*Q5LTmye?t>%Ki*0;;F8PTb#dj^f>Q<yDqxyUsdvU%$=D!+S#Cn*C~rKSJ^wXq@;~rcwR7o>x7$>OG-n>I%hQ4r{w{I?3-*MgE?<iqFEhDy{m2e|Z{fyMbI?RnN!&D37y_-uLzE8|>dZ>+XX?BCQ`@`L60&`m*&s8M9d5UB4fgRKWT#-XD6t((eHXE{#%t=l1{vhL)56yWW!r4&T`GvhV&rfzX}W%Ab6s>XZDny%nNk{q}@<iF;P@lrcl!<9Xc^>FLz=<zJmphB)+p|J4bdi~V2y>VzUii~WE8?u0}i$JF6eOxaH{d>Z{0Hu@cG^mEwgf8aPVB|%JyVE2s1M-#yDVe|VM+QgKWrk&B@Z~$IOF}ygY%tQO3!{L5#bF?Mg94<#OToG*pSA;9al&Yv7Z3Fw^F=zlD1FuC_!fWAAD25NBi{XRtu9x<07sc?0F=Z1v6P*XognOg?;NEakv^m@qE{&FhOT*rn@&=k6EeDsQjj~e=XGJT+S>a4CwPPkU3!Di~j3$DOCV&&e3DG#P(YSCz_%$>hZ1i>bH8?5y2K)y5kQB`dCxw%sncz&+DG8boPRKS4e-tygPsNnI6vLmQVfZujIvR$J#)~7q4#$rp%?8JZbD&k>9B_5C6I>mB51j_T2Tw(pz*FHxF=aKn7F`0bh1XCFFGi=qi{U9~CwL0n0j&ymfGeTd;7V{-G#;E4jzCS@MewuX?`h9d@b~aZ^dtBryep=xLRX?6!7Jf4=w5gYypCe{WAsz_MSp)xF?>3ve1~2`KZCEqKcLrPqo(hF;Ag`L7!Nt%1aNk=I-DJ@hQ0?^gFB*A;g0ZRbP+rmUhvZRSU@qnGN!CUKR{Q*AHdttweU803%Um00&k=kUWG1(SHTO>DeyvgJlX*s54S}t!ENDkXjZr!oEeRPGs7O#j4cm88@|eTI|*NfPoTTt6Y%br#@}v=;k7Yk8M+8v1uudZqATHr@Dg+lyaZm3u7jt>l({iwX-wIQu0ZF)Mi;;<;2^pf4#KO^<?wR0wVGmh5Bf3uF~`6jis54~9Vf@oZ{TC_C+KC^=ppzMcssfk-pW2~M}zQocqh6VUQL~LqQ~H4Y{PJ~n0_xFQ{G0C!EeK9W6Ez4(tBt!*c8LJB2)|~;qQyXN#LR}r6JlFEe;!P1~-NW#gy6TP_!956mE&W4Y!0#p=se#aE6!mCj&nl{+sqUdI9|nz5suY-h)4fkD|BWqi~2~_*>Mp#kc%y_;uQ+DEvBH<fZm1LNQ!FrfiKV!I-i+rffo2ph4K^e0T*s4;=>2gGZqC;reWA1jX<Wv@zV6{un|rJm;l8n}aTe=fKO*^{~+m@G^Kgx(VLIJ}gJ)!OP*f=m>ZOb()LLf#<M|x%}I?{Jfpxz#I=rxeqe;L+07RJO`NPfx$6xePYTuis1ni!|l<*aC^8*9P?f>=3X|Yj6r+AW8hI}7q|=mb`-_%40Iek1D-`OJOLd5Pk{ST4Exdcuph3Ac7f}{_0S%0J-89t8!n4BM|;D~;hty!?g@`Y$G~IZ>F6kU6#G1#Vt6Jx3!Vv2q!^xrPJk!DBhh~FNVqG-aBI{Lw}xw@b>Z4@3A7$u0xpd<f?u>(X^P>uVoFjp7g`q11y@9y!xiBcXivBW+zTBG_ku^G)8Xl~-Dry8;pjwoINX<Fcpy3n9tihGN5cK#ZfIAy8~i@Sa1*pO+yt(P)`n}sQD_M`3ihI<;nK9Jmtr{4OYNSBV)*x%^T5{;(mzq-|H;pWQxKaAP66jbE5iBUDrgJ13fvU!1viDeqod)`^g(xu;m&AZxHH@i9SFCB+o1j7HgGGn8{7(h7kwXo7jA$yfg8Y;(VB2&xDXlz7lJdPUf4??WTF^Oh?+h~$j^p<iTH0n{X#K(DW)7okDy<}N8l^ypYRp<A!_>aAwL^VMgQi5Q^EPsDsX<dJlYg44@aZj;qLTVG{x{cXgl~FxDMI|t^?OXTfw#98tA)l4cLb^fPHWUv@%=)E`Sz-3&82nOmHUpCLP6a9Mtqp9DX)@pZ>Z8--o|?ssFyB82(R8c{Ao3oGhk9QVb`LDJjtuXfikjoSI@d75XNe3eM;;zY0&96MYlT3Fkl~;T&*ois8&?ayT=b?xnh>qZm#TQ!=1w(UfpnI6ayIP7h~8Q^VQdJQTxkp{d}v;9O`%I2T;_rM4(cF&srP?4uYih314y!Ed8E;J4x8Xl}STTola=7ljL=>EMEJJ~R!S56=Hmo93q&&Womn^TGwt^l$;V2$~Hp0vAK`z<FrXVidzA&|Gi{xFlK_E(upaqu>f~71Re;fg4Z^zk`;7-+}9(Z^L!qT4-^&7F+`@3fF+Ep#|Y;aCtNzTplii=7-C`WzoEFS-28f0ImdAM~lGK;hJbMxESqQlVZ3wS`w}e*F`J9b>V2V3LFhLL>s^j;rA$p+oSKm?cug)9k?yr3atgVf}5c=;AZf<Xf^m<xDi?&ZUomu%fR*E`e<3WKHM0s1UH78pw;0fa0|31T$A=~K{4DKtqZq?+o92LJGcYd5bglKkG==L4-cUj9)Pxo2f%&Mws0S~7upK$1$RfA!QJ7m=(})NxHH-a?hJQC>%kr2PH26&6Wj%D40nOMp-td!a1XQv+=BM)K{4DDZ3p*+`=TA-zVIOQeRvQ&3>^XwgQrpqPecd66XEe_A9y@G7VQO(g-4;?;Zg7iv@1LU9*lN|2gCi*j&Of?AleBY2oFWOz(e7YXg7EyJR0o*_n>`8Qw)zo`@-Yk3Fshr0z3&F22X;gp;O^$@G^?wCFn$W3A_*;4=;r0qhsOu@Emj$JO`eIj(}&u)6v23ba*n_AD#?PK?lN9;2G#pcm_Nh9SP5d=c1$G(X{Veis1$51b6|w2%Q8kf|sJx;HB_#bQ!!H-cB*R6<q>vg*T%M;mz<ybUwThUXRX!*TZYjS@0To6*?VW1+PFS!z<t*It32GtI-+oYIq$w8(s%*K<C19Y2OVL!yllF;1A#}=u&tKybWCrZ-aNB+u<GX35wxk=vMd`d<5MLAAv*YMmPi?K-a?u;JxS?crW}Bx(faX-ifY&cfz~TAiNvigRX}6!28g3@ILqux&hum`yQegK8$XG55q^%ZSYa}IJyHq4xdC%z$f9aDTXhh$KXrwMf3=K5x#(i;0y3M^Z<MgK8x;!&%&RfAHko&pQ1bAPvJA@ZukuR1-b|R0zQxKgU`cXqKDu^wC|S`!(X9C;jiG!=yCWm{0({%{sz8+ehpuNf1()v5xoTe2;W98!nfg@=mq#D`~!Lp{sF#*o`tW$-=m+w-@{kYPvNU@7(D}r;p^xZ@OAhGdLF(3-$K8HzodO{Q4HTfFT;1>yXZIYUHBe)1-=LWjQ#}w3_qe6eu(}EKZO56Z^M7Vf1)?xKjGieAK>5NU(svuukZu(d-wr-AH53ShkrrC@GtOh=ymuv_z(03{0ICudJDcq`~FQa{209pKZc*8_u!}SGxTTp8T<r&1V4dai%>C~5Pb-nVmJZ%7i@~*c<7(7DTd>szr&^&jzE8fO)>lr-UIj__&ItXeh!-nWA|xyJ9#WZ90&akHpOs!^bgn+!>^-%!++DhhD|Y?1bqsdVmK-K3^v7ZV)O}Yis3}4Y3oF^d0IFToDR(er-O5&Z^OCal4wP^BwUGNxM56bkG_jmgx`fLpl`z!;1XyqxCERNO$+CQ)1a@xuQ7(wPz<L+6Tqq9NHiWC38zHk!YSbtXat-BPKKH>l#HJZzkxo7O);DtHDf3_#qgVG9QaK*H5wmI4QD`KhhJx`WS|(%geHYE!5PuSa7H*ing~wBm`G1CoEOav=Y>n5CE-$V6|@pui7`=yVz_?9f5%OIis7~~r8n9KZ4dW>JEHHx9pT1k1-LO>9xVZvhl`^*;o|UHXd2jPD)=op2O0_IfU}_~;cReLGzFX$&VnX`v%s0rH{i^$7flX(;q2&}aCSHkni|dn=SMTZMl-?r;R0wzxB#3FO%EH*3+IE&przn4a5c0FT!p@`Mll?XwuPf%f5d;sho54&XG|H44n=#zL*Zd)A9xtt7wri5g*%{);SO*kv^?Ah_MydLA6yK53pSbqE(RAxv%y8-!e~~wFkA@D0vCb{qM6}>a1qoC7lEVD>~IuZ8qEWjhRdS)VWS1$vT!*xADoZAFGn$41FZ&EqmOG)48Mc=;dkKHXivB`+#}+@<Ddt{@DOw?JOrMA&V(nxv(ZiPY<M&JAK2(&cr&~OJpylmkE2)M<M0jiA$$XVikfehPx;w!nmE$@a2hx_S{}{~mqDZ9XueIBp%^ZS)`3gH#n4)CF}N^V11<~~M162UI4@cO&I{*33&45cNHiUsj&G2W6vNLWq~;ssbBf`g(68X1;4jhtz+b`#&`t0Gcmp~U-T+TW$HLR$G3a2}=umhJJPsWOkAp{`ec=&sKePkf5AK9Ef;+)YP#@d`u8bCgjTVI~!&TA3a8<ZES_rNV*F+1#HR0N55x6#77mb4J!gbKna2>c7S{6214mMf?Hu?@+3$BN@hU>v?&>nCbxEDGE?gbA=C&0tuN$6~N5<Cap3>)17&w;n0$Kh@88T1Bx2EL6xg>S>pP;>l0<7dNfa!$w%zX|6=%fMwg&T~=>XF-d>S>TLlVK^h49xVu`hf||@;nZ+SG!L8-PL4*xksRO2`PuN}2<cDoWB5n(OZZ3l9C`pg2k%2S!296!=yZ5JJPjQK8yyEvgU6#I;PLQCv>!YY9)Na&2f**4P2l(7W@u&DXjQlw+#IbAH-}rIHQ|<UE3`J;3T}bcg<HT)(K>KbxB*%VHd+sE0JlTi!0q7vXfL=wJPI8SkAf$oli<nlJai6hbQ?Sm{t!I_e+ZvNZ^LKdJLog`4*Uo;$JHZ#Hv9(1T2448$IlxS!->(1aANp1G(G$p92ZRu$A$likfwx9G5iEg4jVPc$rFm<yXcSbUHCkD4n7a>NB6<|;f?5ecq2Rmodz2n56^%nq9fsnZ~z?u2jGF|d+<QGGujL`+8pi-cR^diUEpqLE4Uln9c=-3hr6Op;jZxeXam@2JNSKg5ZWIe1dm2X!K2|R=wx^bJRhA08~qTT5AQ(F!aLwE&^z!K@J;j)d=vf)HDmWLG%;+7;XlyVU{ehLipGUaG5i2E<Mjc>@XzQI*yvsOXZRv|9=-@4MEAo7;SbP_@CWcLbOvm6A{<>iB2Hx7|I`0^{J($9xb(#OACbHNGWN3Dm;Yt?m|XuZ!i}yS->fh6#EJROESel_z8ri02d979`~'

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
