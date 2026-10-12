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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d350186abc74076ae0c7d91d04a78fa/part_000.stl', 'relative_path': '4d350186abc74076ae0c7d91d04a78fa/part_000.stl', 'source_sha256': '8b763968cc09a6bf0ea7edcd6bfe5c708fe732d0660f0b2ce2d7261393f86164', 'input_faces': 860, 'input_vertices': 576, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5000003576278687, -0.4201768934726715, -0.24156686663627625], [0.5000001788139343, 0.4202065169811249, 0.24155594408512115]]}
GEOMETRY_BASE85 = 'c$}r22b2^=*ZzAJNfITB2+RVqM9CT4F(D!#22@mJkgTFeGGG`5R8$0BF`xp21PLlChy+=huple2D?wO-jEE61fJ9&PtLpmQvAcHu=lsw2?K$^6&pfy4)~#DrJ>AVNJ#Hv;K?TSBq&xjbju;Ya<v7|(Iu)GJ1BQ<r(r>_s%O4!}SjZ{s>H0_T)$TpJ_2?CHMmu9N`VSb<Z+J$#a7KrLZ892$GX_31eB|)H5B7Ozc>e)f@6`8!5d)MyVsPJK1JvibEnBy07;av#Vfe}L|MKTTm4fRyi8TtNjSlbCn8+OTWu{LLqsONI_2n9$?$n)}pQ^o^VRV=F@ysdTXpB_K+UCU>`rvHcK5_Xgo*or_-Qk&9j}9IaY+vH&T&;(jK4SFj_PJjC`uENb=nbyi=GWulktROvozCZH26Wns9zJw$Ab#wzcjpFl+9&ngZh<_Vu~X)I`ZetWahxedgSw21o><k!)5C`z^4dp+M`ru=Xz5a>z32;DnmDwNRjCm7>oM9#(BoIu4a9eHPtEb`65rj1{zHjiJ`b*#=hu_@phr8MJK(RgyQ2DRzn-8zZmH7QYy9nHy`=q)Q-L_KnGNFsUFwe>&OCM?upi2Io)gd|zUak%4(9Xy3@@MXTM45RC$hFgP$!P)iPlD!ed|0@&g{dC1HpXS4W8@QlkK;+j0f6Fp3=VRt^<L6^`DTJf8v?EK%TMUub6y9m-?WG-`O09<97bWixYi1D^Q2nUzIm{`88P>i0@23lO51y-=fFY&GK}Yed5k69MGLI>?`zewbugeBliyo=+Zu^Z;N?)JS*3`p2Q}6v%#-N(Ia;r_V%IZu@7tR^2V{+N6=%vXditvnE%m5W?b}S{^*IR_XX+}nJ~$#TcT^f;QqPF$qwkUf6${HqQP}69NieuWgXGu%X<aePwAK)(4{?k`0OpF4y*p$;f?$EC^KJl_i&-Do_^lw@!j15b#^xHF!3$j?fUb2zb^HU4JtD`GllN<{(PZdmvxC)@kMvK1>?(lxdVgo!_r>jr*$#&V!pAn4ZL+1J@UPouZteN;`-oq;N*F;PnKO5+z(xkX8ZNzen3zB(J8Pl?)80wx}0nDc(W^m`{&b!W<N}95zw8P%gnk*ng#VsGEJN(ng+*x=Glz_UB*QZH)$N)KX*Kq9nfX}pvSk@3!c-vifr`j$#W|D?%Kh6?!4Z_*_a+2x5bM=UB(qXEj_qz|C;`8W(wW;qsv0So{;@~F4$i7x%0beA6`~Hc-^afo2kQtm4o}|TzX2~{k+wBzaEu+Wwn?6=BzgD6GzYP53KvV_2#<qBD&P4+vK1w^+AtsJhMNrE;Gsn^yIprN7K#(;yb@h%?{{tJr_NGI*@1V^}c3aZFhKj@;bbv?Z#BP+h^>0zn;7feDcVwOrIW+>vq~r@B8)Sb=!)cygo#O@#Xs9Sn=ih5DO8%|GfSF{o~$Nd{!zwGVjnLzb^aA?HO#JynfC#?c+n=*&o<HwVpTo+0xzIymfv(xqqzo$^DZ@`$cz|IFm>0^!$(aS*piPymd#Q{&L;6b-8YfZeO=;U9Q`r+t+Pdm+Q9Z_H|oy`?{U@`gSvJ?dQDx7QJbPH?Qc>E++pi!@c>&`u1Al)%jc}vo3Fs^V-MTyy@xT#%<01?>W-c=fBr~>gjj3G;!X4-o)SWf~P048wA&#>x`|-bw+giIwQJ$or%u5EO=hH4-wtIZxP+TZxP+TZ;9rn2lpG-A6u8}mFV{MN_6{r72aCL<a3{?f8?RuPfR^a2I?Q}RC<ZY=ghu9J-Ocy-M-&Q%s=hv;m^!^IYTF!b=h&k(-Xs9@ZyKB+2ZN(J-_Y?%vZkO(e3Z|M5k^0{QJjAlv`rr=a_M$<4yjVx0w8kt={L~KjA`!y>X+>R|N8j?7iCTtDHqfKW@&WbMJW*=l1!g4nLXw9B$je+t2am{@Uw5zu`)mD?PpZ8BdSM{y+Alr$-n5ve%z~cvR~Zp1$h`6G!&{&PO~w{6PL*fBuOwbys=%8@tSNyX^mm277v<_(yyF>l-eyc)6#){(c~S^w2S*kA1_$XT8G3hnhHLr<(TECvk9*(Z@a*%>RkwCeDZVnK;xxzOR{?*R{Qa`B(bR)L~e!K>YCNT4r8FyYBVZKXHD)sl(LHo*tF@@2YC*{Ppws{`yCDbap+x-?)5#{oN}DdwTTTXmf7KKQZy8HJ*Oih<ty268&>LJ^c9q^B&|@lYgv2mKP`dW8Zv#{oSVzczU8&hkSqi6K{u1oFCf+;>U+a)|h=;E8ky#cgsN&zi&9-U!TZ-|1tC0ac)l_|EZn4IPt$v?eW(?asPOuzxMMUfBx<pZ<{)}-|q>;FSN>xd;6X}{`yBYRW|Jp@7&|BzjL~^r#my;-JUMz_leLtzaEq81A5|%S3TX4`=#9*HfTNa-o#*>F(uZf(w!Bj*7^0g#JAeZxbAY(-nk-X#+Cc(JKx<9(B-}wJ(jr1(-YtFUS)gtfF73jB<N0htw4Nd{JHf3UGB$3FJ3-4-<#*Temx@dJ#<%~eR955`{aDTHSNQ%mkHE4R&0-_$M1Xd>r{2Nb*Z!HcAZ7H>+BwR+0)$#Ma=c@+=?&!dN{j-*;hH!&Adhq2<9XE2i@L3@uhuCKG~O>>qm`WH~Dq9+c)O?l^ws?uZKee%(zRp2jWDIR50f{G1#ncwd3Y{Iy2K;w{}e1<k#anwwmio@BGbvJu+sLi9hJ6b$&fu<^mJH(P|Ta*IG|c6rEwlKR7DeugA`gHTs`tHl);FIT2`|NWa$9iF0J@kwqCB199Fjk~+TVR(xm1(OrQ&e;T(dRsBV`>o2-pf6?vwM?SuNSE~IZy1jqg23dJ2_ZxbF_P0&ROI3f-?fMtcsZTPFRexKT`X}R9^)H}X@$LG@|D2qca{r?j*#GDS_CLB^|LCBr@&e~^P~JMfo;;7}@!qxaQk@sk?eikKeO^Sj&r5t*nLs{n{e5fwx?CqCbF$a_b;&bkwHMu?y>rt8xvA<Yx?NAv?Rtt{;Ck|OKNIK6pS<y+-SW42``OZCv6<fet*ysDoVPTU?nLiymP&U|j$fK8zEgXW`JO_LY+>95N6h!boO-!|I(Ho9)lKwdou@R|;MbFNw%RA_EbR|nl$+|Dif*6N$Ww*QxSRW%&)xQUb#p9T>SpUwH(Pgln7Y}z)U7~!>gGOabXUfuZch6X=02uvyFCAS5j{SqXr6!H+In&yqQ^Q{$@SOM)}@}JCrZ@b=HKVGULbz;tibtoXE)!L>U@cApD)qv^JVKYZshT5CQfdSspIbBS!+`0PKniXQt6RtBj%)v<J8!ml}eAd`P7_KbQeARTJ~lyzsI+2_0Lz<OLY7C7JGD!xxd-cDUiRdOa8Vl`4?zU{<bdpN6;f%I|cLq<c#@uSL^+Q==OUC(Ub2DEM49kI4`14cr_4T-aFa4ymu1aevf49@*YWa$;WOly4_y#j9KmF{Xm5FPQM{04$p&5)+J^iuITIOVV(zL_1c+p{6i;`r@W8)_ziO|oQRn(&udP#&x}5#wx`SUl=IId6MtMalPAxEvHKRA_(Qhmn9sytezS?QCMPElzxHtRT+@4&r_1wT<g<^>x$8P3C$R3kN40f%Pb<3p-qqISy{qWSePXpwu8Y+^xqp@h+b7qB_OT_?OrAV%IzN78u1nLp=lJXIv>avXu;e;VPxLX*v$6P8a~>~knB%X1<k_L7KCLbb#{czY6Tkn3rajNI?#Dly_$$*)o;=USzAbLrFZjSaXUX^WhtGTSO6u}F6>7FApv(Jw+Q;r*<mvK0KXx`2(B*x;=#iZZg5!266x1a?x>I&RFrP-b-nnpZn7=vI`L%U9zoOgc*Vg4cif*4@TesWW=T~(5{JJ%-4&*7<H_`3uo9OoSP4oiSx4tL6bxYLEGWE%*YMyH>J=)~4O@2LEF5T?UD(|gLsatVGx8p>l{fHrJz0c@z#*Mt#c2g=n5j(KKuS*=ez39^3L3h7d>D_O|8Q0ch7n^z6dbEz2m#w>v&Ai-bP*0GLt;e1rpPsoJ{B;gfH(QTUH_@e@Vd`(|jupqQzvy=T-CK<=bq-7ZmhMtd(e3)%db0jQOB>z3KSVEZe`x8+`#1Cg_lK6Aygx)QaDQm&1>#%xhfe1OYg4Y5r6<=5y})`|x?{yDuwLi|*6TW>7g#S#Pp;Q>!8j4CeS!75rvAs?KAzEVkB8OGeOeejKBJMRC!e#d_7S;{wRA`BW9>Ndd}ry-F!P)e>)grw`^@ysyZz(Zy4+93ZJlvlOPA*(TbKLT0y_D)cXU~%KS$rKl<%)k!qSt^Q@t!*p35v<>SpUQZUJ5D*?Zt;-uUq)!F928$unx{5+`QIAx~SEJZ)X_j6}+t_w@5;?e*H%o@t%~EZu3Fy*ZU0?{>s{&W&1n?7~srxVG+;ozpZ``@~zT=A_cyQwx@+j9=rpc^<Lzk4-Yy1zX>}Ju8(S{qVV^emx=a7vyhCr6;B?G2iQv1}4segqau5-L@{zN475SRpOQ|>t*ZeMyy#%o&8|zarTw1%f50gUEWLBx;#G?(B(X$Cq(BxgRRT+pnK)R#5o+;SGF$uDq**G%>J=;**~@(XaCr`>>pc~{qJ05>FlclI{V7jWnbC4oD0ztl0W+@Z0WKOqgRgc^q724@qJ|L^1T+b^a$T;adi0}k?$j0m+vE6PYgHTYYFtkdyktuxgWE2xgWE2xgQH(71ZT^%+}?8%+{0lhgVH7|L!+`M&LZ!dh&gXrOW%eu&r|*ZC$RP1$54%t;==Z*5y1#EIs*t)s7?YqikKim(k;*a~^Fy`F`g68_oAqJ)R@vxxmt0*;nXs*(a8s+=ueqVd-{!xsQsouj1%(pO%=w{<QR%>`yC>-ClHQpEz=8uYX>WX91l&Z9Tz!MNj4<=K|fXkLY%NY&~j?YuCp)8XVVUzP28f`@^HbI0>u0U7yJDQTtQXr+`kLwl4J%-L8-5c6~&*>tpLtYh1fNQEObOkF866qE?)Q)!wd83|*cRBV2!MJ^9>i=`PnpTMtu*xTVMB`fRu7dYCvh<AB#s{w^kB{{BVuD1R3tx^o(x_6~m+BYK$jqDRg*Jm}4HtNFcw$k*oku7F<5e6QKMGu?bI+j=}~zJF~!#{EDP-9?Y`{pkFCm(g>#2l6SPlaH-SKDI9T*t+BsMvvre59H(ilV{p*e!%=5LwD|5EZu$D+&|cQ<O6e`VCznJZqt-;PIEtF=?S@SalSHn<`9Sbhlpz8wg2+>Kt8rE`PjPTQy>oc*t+Cn>r$U6dSuJ*|K`~v@Yicok2HQZudd^0EACWq2KM#+>6#Yxk6`LQT^rKk|LafJ+O%r&fBn<7H&hO<D|;S%4*r6&x0OwRzs2YA%AP=f0-xqHl<8PA;ji;~wz7B8-^Hi-EWLN}$MI?YfwK3NeGGmCe^1#wWplwf@I}fN;$MhQ^99Q06K_7TKA_JW{B!VW{vojz!x!>-iLy`7Kf$+{oIb+;5kAdVEBjp8TF`}mrfiwAPr;?|RmxW4Ux`oi70Q+qZ#l76(`PCErT8?@BGwxCN<ObwwhnzAzBT0J;&<_B-aq6x0~HPg2g3&|yHD{U;QjD^%KFn!<3RWTWrGyI7aRZ|;^2c1;<JvWV-5m`z;z$pw;$Nw$8YAd#vX8;@9mDsQRAI(o!2e+Z^1Vh-<`}yV;^{bVh#jvf$My4V?MVr_5kwjg})cRL5!hm=hcw$^k?1XR@!O20j|ftgBW+<>%}<j$VFpoxSmH>a@W`suJdh=zdb&wM^DD-$rycz)tY{->2nLU=)?T_kjoI-)Tf=shHyQPmgK0h0bI|c8~$$iZeaYI@ZW^*R{AtxoCb{1nt8M$ca7cQ?a84l*b06d<J=6kgKK{i`fKb6*L~~auZvH{=}3+mZ-nc-YS6C+eHt>q#^kOs1Fq-S0e=U4Es1p_{u}XiV{YB4Q+L|kLA)?yYODg+`Cd+r8r#BkUg`ML@yWc~GN#5Z@EXLd3#P+$zKs~a5o2eNZyWq=@X7o$s8a@U>*Fs+e~rcAx^GqdRq-_<uiE%)<7-2|D)iO7FrW4O$}=a8m%{ZtF2sK!KB?2CjB_btNG-ZBzb=f~fi{=WPGe2D9{&PjYb*xW^C(M>8jHg9JTAt6F}`xds)@fQzN+*o$~Z+CqcHQhh`cT$r%S0tVdh<!T+-=Vg8mwdz;)k>^w(J3H@`aMp|KiV&#xr?O48>dVimz(1Ya@cSAp>>Fm_SKsLnXm8KWlo7Gr+Jh+Up|Wf)ImWq3t+b?`EHb$A`H9$e>8i99rx_SK^l<CJ2IlK4vFFO9DV^{7R>TEwbAjjA#4YG`GNw}l)vZiDN7TZyglOSq1ii$51%CC1-Kyp6;vL%&k={Ssd(=3I|l>JeA?E<W#Kj9Szx4}TuMdgQtd|2BM@-=)6WZdTR@ya(P*SyyE@fL-7>DeHm12R_YjRMtIY;&mt1UG(XKzY9Lidn>z}cy|*^^S;WW_@nrGlhZx;@4=_}Q8kDEDmw<AhyS4Ll(L_|Gw>gkoyLC}pXR?PJLi~q=ZJNbK4<Ws!KeAp%FYt+EU`2{qU<mHf8qO?oX+Dvk5BWGY7V89RRu4FU!bf=$oPxk)BJDM$HDL5)BI2M@uXw?CuyVkKbqp#sC}9jR=jA)_%(*$r4*J48Gjkt6ecH~TPd&%{8!cIcV)-H6YxXI4m-ww7@y|fC`;f^;M07svVHjX;nVz}vTyN!i%;|Klzor?dwiPzrtA;=f8hI$oKE0Bflu?Nm5o(437i6dP}y+&!|`c;m9kFwJK@v3nX(r6Tj10DYGv2qzYd?~4=Edge*`|wW6H+iABXQDa+-pF3O>!BRQ8OrSHQ{e2b2xNKMbGd5oOolzXqS?O_epr-yEOjS1P*}|F!ruAFAwO{14;P{3&J6;(r$3P;#1#e=<JJ?^Ao|0cFF%5%61-^$Zz*PkfqRrR*B~*WlCq3T2u2Gx2GDwX$pRUyD!kTb130|2BM@->+;a{-OA8C8rViN8r=^L1n{~jRZ%*Z&%g}e=mHRcT(0Fe`kD}N0eQO|4MwCU#IMP{MX~t{0?Pz;=dE0<_{@*82`ig?jWa8_($Q>{6A_9rYd^}oDP3f+2fA!KaNlHsIq(U--}Q4&dRRGe?30U`zq^)zaKu$A5%64{}_ClzpCst{IB7AjGU(9pN>!S7nQxN>`ibQe5A6`_($W@{4Qm^@%P53`4!4C@n_=G{BC9U;J*i-=A)E7g8vbGn!luMBL0c^Mv>Dr{L}Dh{<X3_%Jzc?;0@K<T&}DY*c$$o^6jAC4*F=`NckEoyBNF#o}uhjWtV|d;H`++2y6_$n7+lq67YJ;UL)RX#L|3|8hf*2^4d&Jnm16sH|X~Ued-ZQ$4mnY!Rsq~J!Ja5P9M!Ts94#K87G@DG_R|CQ|ULAKJ|&EV-^E1gx6L!Sy>(MKkzS9tQ^OTlfxLA*P%^aa4NhQF)M>r;FnR`+TdjPb`@)<W5(IZ7@F@^mhTvUK0eJW6SE<BIeb5RV>g%&S1zZJV}3NI!D}i~OIdC3GPpw<?boP%HSy^-I-bTt#10Wp`quQtOrvcYV{2Ycb(p8D3HTAb2|N$e{3~V6l~q*sE~fd1nC9Cs%{M6<uk47jao{iTXO)dr_7nIsJf`d@{f^RSJngmr8SqEA#%gJ%t;S2?x=r;o<JVXXu6?@A5ilM86FKO%8f&B(u6?@AFJKrhW5+`O#?|~YYPATQ2mh2BEd>|D7t!W@a1ML{_5Bq55WYg$C(4$CAH$c!KLbC4f1vC=WedT%@cG1B3SYqIg=ous?Ih3T#9Ty<%Za~?ygs1MGRDtg&wNBq`tz6My#-tXU(CMQ3jdJLAJZoX{t2I#&~^)aF`pMQ$NAuF`1{oM1Modx?n}sj3Gr9ZXEt@2%^EDA7K`b(m_Eyhzk-^)Pi+0UrLtPeI>IaQ`K+=X%1(m0@KYgk-cEyG!P|t)nXC?81pl4d{Nbyw=53WVRaOHm2R}~DPJmnC?UXeO>AwdvSRVeXvM-eV25yFTP}V|OO|T;TPuA@ixC!1qWUd|QU<LR|=6(vygP&&Zzk@mOKbYfja0~ndbNLh820um)zk*-DYm#$&usJ-P+}eT7;9+Xg7HkTyL2cWBP2km8qmE!pxL$j`2hM=o;b-7y!5#45sChN8EW9jhAiM>iPcrsdup|65xt;>s!2e)wzk_YzC#c17upRt2#{3oR06*qi|C-eDPsV6NUQ(BnjM0|7q>iT<qaArk-Txp~d-9TXI>Fc-7{3E!A7joPsjJle4C`<a_0^aQZ_2vP0pEk`_1F7gE;t+Bg1UbJZiefaO^B;84_=Nj=7DqI<r(8Wa4uYr)tvD(z6-C&*qgvF;FXx$c5ny0iTb{3rmTLN;aBi^mGbRWwi4V6U#l!%nG5cL*He8OD{BpQgx6Jexw2MZ2Y80EM#@@(?cp0$tb@w3!34a4@-<b~9Bd0;uYCKJtpoSL>nLACWi7yV@RiJEEtn5?nadh*H+&5|3;Y_M1z!z*178i_03LvEfUgJl!`G4XM(`k9&#w-1Y|9+#Fo$;3uN}3^pmy!4cYA7Gms;zZ*8>~FTeC*>!6xu#?19fi26u%F*QWU@a3?&QHENS)Ff+|?jSYOfDW7%yTeH7fGv+GluX9}s)`ROh>$$A~>%w(CbuCtd8Srd!*$6g(>pIJRX-+NIv-b7KOX{+cb=PCLp?~Y>vc7t(tkA!8&tffg%nhM`*J%T5sdHEdHizpu*Qd@>_s=<xdOdV~HSVR>jafgvUp4Mw?_SP&>%FP*YxZd)_J`hs8V|4^o3b7US*rwlt|9wuKYMQ<d$c2aW-mG9b8b4Y$M%rJZq7}6_T<;(@D1mq9eelyW9{c0v}JGXBe#Q`gDcpRyQs-d_MN`BJ{&U72pZ#XjjzDR!Ji75d-X#hbHA?fzi^Gk(hS$8c?D&cC@Y<2?&CG4!Nc%h$U$>G{^QDC44G#Xjqkw6!hgozA&>8s%_8?%<gNJ+%BJI=j!*M%mA$R(JMb;|ckmy;>F_Elud2$*gO%aul<#k4h0_dPm}dAz$|@-<2UdVzOf9N_RpB9Jh0@GJXCZ2$`I9Q<)5@LzpMn=vz7onxfo0%-u@>jRzu^usOM<20CE*u?m%txk4Mu~H!Dmq0ncytAp0l3&1z>Ubo78t2_zrwx$jt3!@Co?yAv5-K;AnU$YE%+*;6<2oVenk&-}-AT3tj-%YgUw+7o}!ZSeqjBE8<(jY2@@K_#AvDbC?0X46j1Wi@}mUUWVMuu*RB?rnb+46X4Im-vr-=zocx8vPt06@Co#P0elqx0{kU#416YQH<1`m66Z;@N#HEFu3bfHQjtA<5qs~SkeQRlLd@?%&O>qVJY1XRCFra9Kls0cf5(~ohyD94{%`S}=WM>f`Fw#nO{Y#1@K3;}d5pO~13n5L&-`QH7<e`2c_~;KUY)sD11qNe+qO9EiZeIO^}c?J{h{#{_{;DaU>tq{{mX(CefzdDd$uz1i;|Q6oDNon>uYZX@~uFwnm@zbp9LR-k0ZbF;M4Hw)OHp)3H}djq}N;H_wct_r*|;T<@@0f>v;(MZ~ExIY2aaaIr1(77K0ao>$9#=$Nh^r=(&sqABU$?lQ4J*d>Z*ZPg{Mhc@cab{yc3o?{PyYtwN#y*MH^z?~mR)PT)WGw|fSEjndyUOT|k5Qe}@D3KuaiA=A8n9NMgZOUd~k3|!B#'

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
