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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0d1d771d8014c919d307d63ffd24907/part_003.stl', 'relative_path': 'f0d1d771d8014c919d307d63ffd24907/part_003.stl', 'source_sha256': 'a164ae3bda823e63e90e3f21341517933f5bd4218da2f7cf00b26e0bdcd66a88', 'input_faces': 616, 'input_vertices': 420, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08868688344955444, -0.3302748501300812, -0.1268160045146942], [0.1326824128627777, -0.11676456034183502, 0.004160091280937195]]}
GEOMETRY_BASE85 = 'c$}r22Ur!?w#Nr7u@}T%a#Vb1tk@ee*p=8~H!8=93L+6vRMfFx?-j8fdySxo*d4@fR75nk=rOh=*M8O5eY4j3A2Wx0-uJ!lJ@2=^{a?RXv-Y07_w3m-hnw~RnKFAS@~^Z~dRqE?ySJi{<x)JAkpqU07~F3_c$Ltw(QZmU=Jd}|E^6DkP5bU{%1C9bcmDz5{f2wjw|F-kSl7Ff#e3ke;Uk9k2@M=Jy#D~=&HIFe4={N6pgv&(48MHM>eVV)YE-CX8E5%F{>wpasJdtGQKQhxc2486^s$7aF1T&4eKT{f1m@O4Z!d9KDJ8)bcf_lCb}?7OUNP5#b|<>x%DNlt`S{zNQg5>#xL)<IBZ;oKwlZ1bpZpBIU-G1;CAi{hbPBge|9ywlyKOIX`>Lcwm%Mcv=U10*WNw+gS=v7&?^-TrZD4M{0RHK-obR_v%2Mglo;Th$_G_+m;?|KNNqk;`<;-o<J4l{xZxdW`TjF?Wf3_GWu9kkC=#uy7F8#A&j*LrG7v{R>;v`qxHhk9_KCj(W;g4!_KU)(zGuP@(apGF$?ULtFKk4TQW2ODqZ^UwWtFJRJd|)5fe=tzmIsYx^QSv0L=5kXnCvHo*!uj?7T_ulgY&wrao0AEyxDs(g=4ZW*($A$&rE*+o#XYXLcD9tv&niF2IEJ2<`0(a?U2^+@bzEL;CG{>D!}Z$o-Ar`F)v<H9|CQtxl5g%MsdsqceP*r&fL~m*isNqiNWGVjUFN(a8gu`sC#yPf<@HPMA7zP$<cWGF<9mH`498E%=ft(-ru(@ZoQJud_L1vV3JhDuymxMiFZfB?^Tz^?S4w^(@jL5DKQHm*_GmBMowz;Zv$UtlOYRR#lVi;F$g>HqxUEJy_rK=$n7OsgQRZ6OlJ#b;-#H@nKDa9DMn~yy_5CQP_NczsWt~U@@B2yS=X0Cne{_-Om3}gYuUEgg%89EBX2|v0r!u$YIxOw^HEOk)t5FAKe1jgy^$r@#+}>lR+;`9JE@Iwmj1$+h{B(eM*J@b*_R9EfaF_nCSjm|ejpO#H3m^0RwV$XZ{W<iPrCbjD!-;E~56SozyUSePJ@X<TuTe+%yWf~wdXHpoS(_)x%<bn#Fjs$%m-{8<8kaV|ELY^dk#$Dh_bYSjB;k5=FCH&_Vw&V%R9e=z<WUDXPe`ip_1QRHvp-I7#r4q(<o@k*(TQ8Wxw^|G&oM8~6<6mj+s^s2pOW@p2zTl?<<Au6YAfN|%7fC+w~sN`e*3`OdT*rk&*7uO|M)2Ls!cUn&j%(+KMl>y_lu=QJ-%M8euD5eOJ%-IK6$_u*Un8_$a#*9l<_*8Eca2<Nz$GjBc%N+j!V6tFYr83-WHYXEm!0h_J_Tbb?I+sZaXnh)}1Fs<a*mZy}<d)blJ$~W#nT^%lN)jq~75Vm@6@tu+D#xbvNifbL)|5{9MrE-^=sr;(D34UETS*^o{SFx&4v!!-U_MtFL5TRbmDmV&CI3bNd4sN2ObDStlP|kUW+}=Q$4Rs{YWKTgDgS>s4-@7hWTW<XN_HCCAT`=Z3mvI=5f-@4tcLGI0IEdRccuWnZHf?jh^LvFkj(>fJ=<)^o+B|NnJ#sf=fWw13P?&Z8|~wV30<mC|pdKO_4|KP2vw{%l`@^XO5<n5!>VOTDo^GC$W}TfqLqRZd)Q^HSE6tCOYPHDe{ecf<-V&rM=(X)s={EAg)MXQC$U*%>Bz-rG69vTcI2=fN<UhjpGyJH5lDKX1iwKkHj&^7BQ{8Yb}}vBKA`-!JpMpYXG#<bH1%F5?o~NAl$Umboo5i07^1)|I)<Zeea6(R7b1u3UM#iOV;go%t>I-LAN;)}lC9T<_45*9Yx~=F)GQXUMv@ufEK~55CgRf1Z&3f3TYSK|fws`Yp#9S^v)m@H(&8IwSQrnJ@D^?cXv_0%CVdzvPj2E>-3E@@fHd?O9$~uikhq=koSEi4Q9$`=ZIGxjmXSSn}UqBG2Vsc@A^@g09T1yDH1R=-UrmuRg00b9K&8X=nC#!Zly!mY7hvt^(n+xU5i1@((O6?HOBE_FV;PIC0C;0=(~4!^%pYdSxZP$Duv0xb=K~9xts&Y3KMrb+=32XIY#puHC!2joaauRj&8YDOnHwR!To-bCdYr&dPO_OPtHcCyeIjhVAb?a$gLdGM(c)MliQj&nNXZFDUc8`f%o2!U2iT63+dvd<>E2k8gfy&+HpZ*pKbU-1;tx$6fQeF7czQGS`1BDeJ?mwwlamFRAygaIJ2%jHBHm@mr*y9qX-nwv-chthZVV4{6V>%(5;ew%|N^!~DC<{bo^XCc5Iv$(p?W>puCMxb4@d-LANO_KG-{@e#v#T=cFV;<;T}w(>fl^v^Pd`JHFX)#BS_eQ1%3+o`m;%iMOjyv)xQH|4(TdN$rXZ<Vy4rkJ_SFGR+-;SISju5V;+_mpwh_XSJ;?_4YV<u4K+=g;G=ObTIc^$q9yUHL100+%5}B>z3x7wIiSr9aO%X0A_=akpMcl=XR;uf)&vko6?3zpMjmbH|&<%W|cIyzeZ{<;1nfWxUVV{4&Qo_4Do7iLSV|W9x2LT&ZW-=8CI1=Wmeq?&NW^1rOu-X>)7G*JVEwCF|nvlX*Q+qYpE;9b2=L`9d%0&o^zDTf8Ef>)&8pcHY;_TpJZE&kK8i<SEjexi#{<^#Ab-JT8_e{*r%rs^r<?6U}iR=YHn$y!5Ab^9%R0J@q(q+mZruy$@C1S6C*0$6T5EM&4^WU6Ohi*`+^j1@ZM-1JmSso8I5b$E%c1cZxrBWUIOTN|g<x&D`>6u=GQX3v!>Xn8{rKbl&-ThfS3{r7lUH5*;S;`Fa7#lTX^O&m1oM;R(5!tJj2U<wwrvJVk$&_xr_#WZj6*-_(!Cf1MN84=g&$=k4k)`(<s5+;{Qs+HieM+iiBbA2(DzD)XhJ@Y<(jeXCTZFZa{mh2%Z>`!mAxT|2^jbh12e?@p5YA|;i%<;-JVKh%5U<ayNdj_|X^dEVIuKEZdD2h5e3P5C)*YaA%=t<&!@w^xhg=ZR9Tn5+ZierK-#*-f4^p9jc3JjgCQ?I7=`bnjf!Kb3O)#Ql?j>k}L3T)v#c+>&jT^h2)GLpVMI*V>ojcqOnlbF2Sp>4#1|`cb^zTeyBwxcaRd$Ey>vF?Z}AlvKAqemuUyt(E2dOC9!<``@;z5U&$zma*J#_Sl!g^KRtvw=aGm-(e2EX0CVYGMn4kzLVU)@vmguHSd`me=MKO&yD|<@hy@*gY!4G$~>I^g1MUW*hs$agz2(>uIw$>8(we}^DWb`Zg&ge>wOT*+!Bz9`%}GLk>hQjK09$`%aozy+p_sYGRJ$Rz0G%$KgplDwWYjQI^y*Tr<iLqw@E)wD=YC2vX3UNKHDt3?)+drf9rVR-jVXY@TxM$Tl`8*=la{tN#S-j?at3-J^1@MJPvO=3U9lZ*A4qEzlF@lm1V9?Xgi0mtLeL?oPT?9=1S*)Nt|c)m}T7Fdb1=R-vO+RSHyCjCqGF1)E@kPp_YheuI=1#g87+!Ja4rXK`S`V<kaJw_kC6w7q2<Yt?~WNo9_$DwY|($)m`=pIgUDWw-l*2=X1$l^(b>o!9J3wOZouLpZ5uKZ7SkFH|fvu;Q9&4ubkX8gv)~UR&#v*kxu=rSb~|`uC(WI)YcT0`TzYe=9V=9GQKgF2XWk@=fbaGTpFL`b-}Vc`x?&wxHNP9gD>xUwJp7D93Rz@$KBE}x6J>7gP5y{-^+YZo(6Kh<yV<&ITvvrd)qRyKP>Z+xqZ_TsrSNKdCon|vzGHr?=1CZE-3GPUS-ztIHnDf{<*(i_Mi2=m}{RxB>vq-C$1`eB)`XHS;uep7ydfXDc<Ne=6dcf($1&(6I^j6b%^BIH(GeHVlv-a?v!<Bl`i@3K09X4Z_jZ~_>kt(o&fg*S6nHK=hpkXa=jg%avp7(CBYT9PY;miS&L%pd0adi$~yVDwY*2HF2me5yMgTM>Qv+V%eKdhxwb5a%v+Dz9B+#o%G`dgl(c8&=)JDEKIH>HC)D!WnCopT%5}~C!uuj+$sXp`BNc?J?mUiq$s5eotI~dbZZ&z|jQE|oQqou2Im<W66}MLimgmr{`_dloM#4LcOK`>24zjOuaQ#P&%cceLUE=Sj($0?gWc~c3vb;~_ej)Mq@-w$K*b!&uYH#8CGkM>(gMZEQ<8*GPUNm}x#P3Qr&j&SN9dpaz-OSZ3W#v0X)KTV|&uwY{)xxq5*^=VS_db&EHeJ%0+j}PRI;M}A!SU7&p&QNd)+B%VF7#m}b9?d~;nU^2Lq`6!-`wUiS7-dm>!EGw6?u>A79;t8Ix5%op}x!$-#fw&q|1FV^|7?y{UvjK`6b~U$IavOqOF@af9N3Hseh8jF}F+^BF~QmFKK7h1I(3H9x^|_RFwCuW`~$-7r?_?@_t^u5wV%MZ<OTm^_Sm=HfGwwd78aAVy@Tf>mmH~Ct0tfzLoDX@wK*?=d)$9k9?omG=RBfzK_)VVwKd}>=|=)ZW@n^<<EKC|MuX9Te&^fT=HD$R#E2v%^ce}zWQj{r=6}K&+)8znOn0I=6S1pT+R8d2kJ6cQtQZmujCimS3GPed2VKxdgr8ay%un7u8*w$O{ekxM-S~Qd5+za=U}CU@;#;hLdi4e5p!F)ZL+R<te5zM17w{~%E|p?16O1F3jg6;B=a6#+d2M4J=u?WUzPW=+5XJcZBKY#ZY@?w*0-c)!du>#_qx1WWc_>_AUw791(}D9WPQlnmbu=!jy#XHMkl!9j`?iAHk!HpX(67^>d|&Gj>R<Q+QaP3E#H3T{e$htsls~~mU*(ftGuV5c`13u7v=s@d&SB9d*_wZ>v2OjkC)Q8>JH{JigCPSJ+W@TFFdw}w5OE2d{2nT_cLGb+MUepuMf+2v9RvUwTqjMo3Bf&AI)43vB|#Er?J#qEs?qPw^+IFvMDkjg8s!^$rr$RtT)!l{nfMhPR^6kgt-zFFZZK;26N55o4gM^uP486mAEePv$o4RKRH(VzyDk2YW^K5<~+)f{BfM8az&XpDUIa*N-oM=`McZ^^L$gr_GGTVoh;A0R#{~o3v3$C{ht<d%v`Vfqyux?AF;>G_1X_DWo|9nS=QTGxul<$-D0jCt}OkQen`eQZ_!<5Zmr!{@;4~STrJU($5-2aTkhYW(#(}r-yL<DZ?`K+p3dQ1uVwBEe21;iTz?*sY;LC|JW=AGYP$J;RB|0>Zo4-@cN&*jJ9ZQQ`ke>&g@aqm;ycEMGY8CE-yz>KwP6S4yTOh)=4#Fqd0)PHO4gI4c;-s(&hp)|Zh2X!e@zg6C`R_5O=P`Nf^RU_st=dnt%^L9Jf}ZM{^9a{PivJb@9Ejy6S$oRm&&>kdR*G+nTff@vRJ-{V?U6QJMQ<4{Of&jW&b{IXP|u7wN2Q-^=c<lg)frt+m3p5?;FDL9o5mFTA7#3?a}gks4`-s%omUB`#Jt!UFCbly#mq?HF7c6M%<PD8SE+h@b2ZA+c)%=_st>+@|`WZ5_4Pi{2Xtaa#Z%!Gn+AY?A!H1hoqg4+cH-dx4vlZpN!nmKN-2BfAsXjhd4iek5dX;q<`)lVXg*e7k<i*zwap@8yx2Adi06&*y5_lI(_gobETzx7gCkVi_Kikg70sR-`ApFNqlk7E9Q1)<X_u4|Fz_Ce1}=<m*k2oo`YrIwZs1i_p|?LdGEFkko7xLYv$TK`CUL6=pWA9s||BKIETFNN1l*=zBZD%b$`xOr~b^qzs|RNqnKMh3jf;9l{2J0vHc}JbA)_v>A8owx-6H>pXR?gam&Nd%dWUJIUvo<^{6D~wpYF7JIu3m*}p8@FY$NE%ip&Yzs_9EaYFjxOQ7_F<*y))uiI1SdPCBrJ>S%l{o4`Ywin>|Jya<^p1HQ~db+uPGIB@%sM{wnSD#;#Jb79tx#E`kon#yzM@zj`qn&=YwY}fY+`4#@)3{{h|Lp&Nmi%kvJF25zOOIscdZc{6QnC${>kUhh_8$a)eTsi~vyVA0@z3(eb#)qg(9CV`M_zWt)ysitW^PqZNPO`Y^7jVi2g|;C>Klo_6eRVwZ!hyF=ikf~&p}T8oRNRMU%(xC)T9>NpVm4br2WaQFPZaa<c|Cq`Pcl1glpCF%JZT}ha^}0YdbUW|HzXi^0Lc3;Qx^aJYybpSKl;Oc^o`r9tY<<?VbKQFfevvn6;$Q1%_o;Je7fcOn(|kkp4MJ*MAx~xaR-rPXlZF)c*heX<%kIqsfM4g^@02SY5*!L6?S4`jgRSI_DkAtkCZbdu!Mml;nS=3v?4r{3CqQxxvZ*2AbGsoJ%YVe9|2ZYiC$z80k(h(rpcE51(`!!+rp358Vl6N9c~oMS6;16Ac@MlKi=b4TmNk3ZHZYIQi3|i7m!?(@{==o@!jj2*Z9tNq#gmmEopi&0wTk!bTvb1$@$zk%!KkXxL(~W#E&+mYF#Dn_;B4pj-gG0RBXizrnCE&=XP42A>U|j*o&*dO9?*A@E60fF`yYn%D~Xq}PG3Mvm!Vj`~P1#WgNN|4jv}W>|H@YNI5-tYM9ziGL5jHu||5{HoB+a85O_lJH4yH!Q)httiRgW7r(SV!>m<Nw0(^_A~TKoU<KlFMQH*h8-|$7fSN?p)caV*TLU~ev5;@19}C{i33Z7Pr8yZ7aJJnhmw46Xez6ij;S!xzOV*}sS3Xe)`m(ruY_U6z>0x8j+0*qM*5y2M*6-YRtz~F!7qV!Rl<424J%++Hk9Ol3r%Gy=r4-IP)WWAtN>z4A-*ik%dnbYUSOol!1sbK4_yQCHQ<+rH8jj0x(xjK@cj{A9;_Kk;_cy+ZVT;TEfLoe=aX&)zXMoHuny4eU@eiOE&OJtcDF+NsGZ*#)*5AF80r5)Ssc0ywBuNDj71Z}n&Z4i@Ee1*hV}z*ggM~{t%8%^6k5f(O~6{fCmjGy?0fhvP)~FC#nDz8LwfGeJfQJ^2ThEgL+_wJK|7vbpP=da_65fr^NH9Lqa3ctI!q<`lc1>#GaYLIBi$S}95GGdhhZI?g7cO@M`K-E0=?0&MesMlUjjD8blxJggUb2P^Wm?DEyDS0ag5kZXkx42JC2jqV5CQ*oCZA&{wk9{5=MGFjPy#_G{grZZoH|jRL?8JemCqXO7fpUQ+da9>@JM-ZP@RKxr2B+?1N!{f_*SC@@e1k0j0%F;>a)QCPtcgJ@}-lU4P@8XJ{vBGUA_Mq+csC$38>92LCsV^h=blpkG4Mwf=_dr0erAtdwE-P?B#kEC)34Z1D4ek<JYxofl<h=*;l5nf$^q(ph1o-C>y#uizLlPt=zic|4&#pe-=cUMPz~7lohK<X41|t^g})YFkmn*Fzi~uLZvXO7hzpRvfwl&Mgk@4NiUoXkwM&llFxsRs%li*3iU)pos;;C*2)92swPg+QRRSIvaqs$N7#t<kNjp2f8)ts{<VXPX3S3#Qfnqj{m6qb8nI!jWQHE6u!U7*I=Z>V5FPELJ>a+addo`B74uDP?A4Ukv&#p@W$YzzlSE)8=6>c_>SYfk!K?G7?d5LJHV&&M!|1oIyMSE>FTf!h#z7)UcxXR!^)r}zlzDP1M@-O20;76d=TFheie*Y8Jw5Xu!0Kx-^h%$0zT;i(AiNIK%B$Rgfa_sCTKSp>2F}9^T4toe<2(rmLK^kcWG#1-@+$d4xIe&(3Wy23qTivPsi)Rcf=M!y+v@WJnAk2?KqYPZOa4R&$yT_hV@5Depfen@9GC00iSdzIQe~{iH(BqINld|x<Yp|Yyh+)b^y5JnDLsf41}Hte*oA-XgartDK^@$Wroc_N&Y;;eu5@G5<cl+;N(X_55qapV3XmK-l@p@gX2Ad{3J!5sXM_}!Y92Jocws`wK!)d*naq=8{&Rwg_8V%hE;+lUL8K^{{kn!J~Xjn@EynNBhNtSZYXO)*Mwip<hO&>#M~$kT?kea@pTbL$0H5vqsY422mV-SDtjoh&XV866xSAhAH+~>6f{|cVQs)7Osqe68|X$TyFhn=KNv=O7Rm_dWW#i58+_73aSrL_@Mpmy5Ub-Dv12%w_%`^YQ=p0MhEMu9G_eHuj^m^+!APf}JOO<IeuBxr3?qFKMtTqI1mgGN7_n5;NA+ApJ5y1nKqtee;}_tQz6IaGe?fm-gT4TL0kO%@6mtW|9z*|P@~Qk6>>AE}jyO7A-M9}u-Go(h6Q4A(2Z*II9r`iio`c;0?`5#wZgQ-moA?e*rQ^KbsG~PxhCovpY*--tU{hQme2R%eIT|_&dJf8&&~u<;V5AorHVNf8lry2nL5CsFAn2L!!@veZhe12eB^`wP<Di4Ue}wfktO8h16YGV38U)=FF@vCc;&=rZX~&pWMBfg<xr5N&A<(tZkAWEH>R^T8*TOL?G?lfXYa`B~i@>h~zYkb#6SIQ%fgXx71bQg+Sd?R+$3o9WISYC=bS%o{(6P|#QLckt4{bxa26`>@I%q0mP%d}-XP%Izxw8myG4QGGC>)<<Vq@I?nTMo<VIk<(G0?<lZY)IZg~(5O0elU5HT;FpYjJELa;(O+IIfBOl`zsPV5^aD3H-&-D@`%;!RN!L_^F5^J{|sIQ`}q_>G5u|f0zqB9()390opzvnpik;Qtk-&q(^|0KMi^W+A<YvDg0@;jwN8L;4j5^uK`;Fz6#@D#kkPC&1qP6H<{B#pmRbOg^{MYoeRf^<%1@c7e47c;Q36sh`G7Ry;d094LTEacEn|Zey9j1{{b|yt5}O4V(onZb{anEv+xf=r^7!2pZGlZq?bbz8vvj5P-tQu;gjwKP0XsuGrbqeq0pTb*(+F44u<xFPsdgGq#b(;KRnNVL7SGtKLYy&*Kh;Zbr$Rfv?uzL`i1rsw7;>zNN<BJRAg@u1?|{Nkam0<-wnMLoW7CM{%aicSom{b#A6XVR{7_fI&u0gv=YAKI}-6=80jDw<?Id?2{smaslD_az_GszF>H`wfhft3f$nNpC)2S`DCzhN93KQtM!yHHG3+ojv3`h~fn)ukV-V*!kMtQB=~FP$2T{gAAB3I@qc-;i3jym3-P5oi;P-@u;F`{$j$aM?%djiZS8&Xs&%wV5P3#Ype?i|g#gaY`BYho4`UUJJ&bto(iD3oZM7tZM543|-c9R&=bc}p=9Qy-t<mZ5q&Tm-z05^BfO#jn=y5*mLw7x1%{~?!*XFC6^Yd*7-@uKndN8a`US?K$h;%@wpK4|QxFCEH%1Ich5_W'

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
