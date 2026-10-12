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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d7570691b670496bb670a9fc1d28057c/part_009.stl', 'relative_path': 'd7570691b670496bb670a9fc1d28057c/part_009.stl', 'source_sha256': '8cadc6a0fdf311237fbce68e1a3a999cac7b93bcba597c2e62a0f767ceddb37e', 'input_faces': 1114, 'input_vertices': 657, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41374075412750244, -0.025252699851989746, -0.3782176375389099], [0.4248253107070923, 0.4614996910095215, 0.2189166247844696]]}
GEOMETRY_BASE85 = 'c$}r32T)X77o{&KDwwkvuuWjVtQat~IV&QlC`zM(2^B$6QM8SKpkmJ2=A0D+h8DA84q(Qdp9<zUefC<8?bJ-w)Xb~ewZ2~eai4v{J@<CgUB5@03>ouj_^*UkzU|N{g&Js@ifmdwEi52pSpVJup_K*)kFwEniLd_qqqEz4xAX9^(ZaORE`0(*dxyBx)w$FQtnK2ea|s+0GAzV@u-}l7J^{*a?jIByVDUry`3DDBUYB*NS<6*dy_~BqLihjppM#|Y<ALy7M^r779F8=!h`#Wx>*}>}RWSV0D-SAP3$wi;uM<naU-usE+b@T|sUZCH*h9)UZ#X5sG25M+;@`L|d5qT+B)|FBMEIJmS^PKNXuq!;e0`~jl4oy?6lq`jP72x&954QigURBzIS&6z542ByC%)ch{zdTvuH00<?#KEBr3SYM@r_Hz-jdf%i=f_IqtX6UQE6|En0`RUozP!=^NkHR<aL!#JC&N^yCBc*%#z1EV!yQ4jq*bKy`7WAKkBwiY3jii;_G$&Qe?c<*6)`*&l|yi+Cus@PB|#P(Z3$@e;X~nsb(&zQybxq{GIoTug^DD+Nai_e{`ADX)Lm4kNi8wx*S)M)Tuw1Pu4+yyAJYaI4JE+9rA9MJSS?xACynp>)ae=T>AAjP-lx@GA=FqBN><BaV4}5cr4@6>#oQ=oA;GR`_FCB{_7K|NB5*G=O?4&H_qvISafS)wBHga?e!-OQjht5A=H025#xPwFJAn@`QZ1D#(Z8%-Y5CpbHg976n@VOyXD_K$OXS$Q|VWGR#E05wR{fLKjj1Z{jp5)o6cm1AJJU$n0H;pepr$P^^eYaTk?O(D%XMONJjV__edUNy#lf>W?NhI+q06?Zz$PU>NK{r!FXrYz`8%aA@ifn`FcUxd(K0@<%aE*I^TW~-#9-B^I4&~)MHrw3GHojq5U|A9rC}&-9!6cucdwJgI4G_%Wbr;_7d~Cv4^Zz>aP^|*Dr{#U0jTHEO!Zc8jq5BGrjpN<24UGkM>!%OTVVgzolROfOF#Ouh)}2sm{%@e_EUt-<)YA##_Ix>}SKi1o-_PNFJS5T-L?lvkm=D_=4*<DNOc>sVIE?!Pclhtbpu8^ODW*V+YH+Xz!azd;RlO$p3va#uXQY^X$fQ_}f}y-v$(w@#<GEgC92o`_p4T+JBji@vdBT1M7NK)<xR@-*_np#%1n;`7AyQ_0*gp`BPVT%6`yA#UcNQTe2>uT0<~Dg{Pr?zqitF>XwnHztU9r)teyy%<<CR{KANOd^2L*pFNZH)ndlLul@GA%%hjL`1*U{$dlX=`}}MpTrbPvYgfb3@3rv5n9mXLPX|eU&EE(877xXEi`2yYJlTu$v;RQ&{uq~W$2u9WmdzjirmsewUk~HF()q&A`2*)<*1R|m+jqzO{0hW64%{a92mP*2@Mm>LomIccKGf<oL7p6Eah@BVN_+FE>Zm8;2iASUOq`$IE@<!7T;@mbaZLKvFUXJaMmtKs=AO%B9<--l&r6=QOK=|MG)TY3s5JQZlB9jAe>m=Am7a@l{#hIK*NYNA)$S46Pv3$2$j=T~-w*f1*I(O$edW~y`=rlZ_>n`f?z$1UE>>MZo-I3ZJ>K-kc*mTF-!u;Xo?GZQ{0!=8VT=6p<1yYt2jE9^#r&syhks-Z^5i&#@y>g4RQ~r-OHt2n9~qbK{sZxicJPhYFJYfQxi9-)Yc>n{!!}93hU!(|kBAjt+g26l@P++2Pdp>h-jDMWR}ANE)5*xc^T0Lfw{=Nek9S5QkDovGdEjlFhZjSUr(q6^cXBWBP2>B*UsD+S*?yeVW2z2c%e@iTqhm16^Gv-l-qYUL4_QZHK4bh*&t=y6y$$MI;fMCUy(Nz!`)OR)jy`DLDG|>Ji`QU3_vng#=kJpGwbk*s4?24wPnZ0XKQ$#1&lTgFp}qZXj4MlN_>0^zu9sW6&llqQb)%o#1NV#h>9~H&*F>I^j>yxkJL+6g5$$)xW4&T7;{KJ*74`d%#D4HSCF`!8tbjb_&)_^c5ruUb-~#{Ha2c1mw*k*x$t5u^`#AB9;l1GBbNZ)F{kJoyXJb+Hn_5)r(MM&#I$m}}p1X@>UG!znNIkl{`Ot6Bdz?S_oKa7i9B5y-H`*6Ch<#f<3;fqtah^P#iE;gx33+l(#J<Wq68DAD@QnvNQD>nr)Z>^Dc|MfDb-FDF)-mpDlH@rx9_v2nQKI;T(vz^hPqE(|THv})e<QxJCC`C*xWAiry+->z(by+`%}|f;3;4N{<+?ETU5e+rHmT@0V{V*3=FG=reBSrypTzoZ?2GHV;~nHFvklKnt6t!oyqFAs=40%ihlM1+>A*Gd%@<>(9#ivI*oU{1(EdUf%%_b#*5%Y;_?w<#UA&KB-RmZxo|dC=J^uPB{pvHsV;+J!T*H38i2b}}H+<(+INws%OMXM`jmT4_f{fQNU?ci%vH^9@j=(;=ng{!;=sNh-2V%Un+;BZMU5Pp$zm<MX#UA7R%C%+4?}q!J-ab3-3z3WAFFS<is~oGO-_&AJ$iMdm&VfS_IQMjssK3)wJO>^gj(!VGLBA7hQD^P92XS3bf?uRR=EwUM?z0WyYafr|{&gn+`!;<%@*k*+bG6!5*>C1E1JORh0oUD&c;p{40PT-s9!&cuBLCZ7s6S;Gp1VF&LY=F+!gn~2c{_GM=0P{H6Y|f`j{V@=9rIS%1NkriC-bQfwZr|oPkXeFa>P6|EQI_k+adqP%6P8+ohJ30iqye8#Jt4wL!cwtpRIyCCrjfwr0!YS=jH(TM!NyHUo<==b*7#yf&4vFaG#n|Q1WQq3ZVU_wHVjy;h4{U`H+9;PRV0FjO$D5p9}Sz^+Uh27fYSmu54&O@f6-?ZN34&ls)`+SCK#Rqs)V@S{C@Pyl{UB&LZ_23ul18e>2XF<@U!V-;?j>q~GG#k>Bx%<Trdv6JHxY8S^~uHl8cazZKuS;0F5jSSI}%d~T!tj;?rKD%o1{=yTpe{?m(ap3J<5=j~4C;rIU!_ZNdv>eSX8MV^AIF+YV@;JS!jFTSzrI{4{$4%aPTiS~z2;5_%oxujoYLjG)cPSZv1!}Z%8zUJkCb9F&QoDW}PkUw}m&WE-8a8AC0ujM_5^Xh0J)af3D_KVlx{X)S|tnaXin4j_2Fwai!QO}dH@P`@jzB`XE?ic0Y8yikQzhmxUA1(_){axMgey4>O@^|WmdIC$L{(7x&URCo)`=QS0H#iJ+mi9yb2Rh_8#z}r%e_zydt`YKI+J${<@<INYudyzLmLJDDv_+oD#ZZ4@S)B7XTA=-iS?D)r8~XLAi+aW`!1)uE8`n{u>hLS+Q2&pgsAqdw<k8p1e#^WN&!5$cpw6&B<j?(D>d^}4h2Pc-`^pFHjd!vlk9`8h)vc+tHw^xLR@&b_iGBO)9?r2V-{CLrf%Cb{Xv{<RH{u%)EkeINalL3MkKv~m!}Zm;F|MNqkC3OS0q4Vzwy3B5QSr40?zpa#N8@^Q-U@%qB%G^1Pf8wB^hV@A@*eZk#U1r$o{jdM)2>Q?r{l4II>w=W;CJ!OHH+gp^F%D#A4<bK9DXI^)lHoYzh?)GYwT#rpL%38^32|W{p_<I^Wy{G{0^TN89&az`7?Qx`1;+Q;m<YVIb?Mx+85dle^<8?l4sXY<R66nrX>tQ{@1<X>+@j#eU4(E*X#+uNIjkpI8O|T9>_nb0`~LAL)eGW%`q;whG<{TN!q9GY=k^br}KUEXPn!~b&)5&Ce9O&Wth*9+Q{P(i_h!4K49IKl!o8bneQ()$hZuFrI6pRHuhnOV98_pPz3Gs`XWzA1<e1ZH)o{ZA*ba$(H*OS^_})wd@aLXJg2Q|4L{2h@r~`T%K91>??axb2k?g<#<;#b!af{x33+bS!E<%yFsak{`z+e0Wkj9l>*0Qy^*H<!MKKSHuOR<`MATX3xAdzu*p2nwe*pPMbi@7Pr;X%K9l95OxeMrbL?iLFJbRF5gA>-vXEoL(D}3X}oVZ^sDJ|_ypH1-dVtw_U#-ZP4(a7%>jOUXyKa4je3jSGpzOM{}-y6QMVkOCwy2JzfZRU9K_1)qyZ&g2|&L_cWZy%56febjejXnM0&v)hfWpD9Kv;59j?`LD<AvoWb_`ttB5bNG*Cg$gd7wQb@gZ=qyGVTjAJ<)!z3)&Z}EWTkNd~I10uE*Rj(7swL_?~mn{`e~N`?MDQ@9=}_pOp3$D<gk}%vkpwq0(OGQvRQLHuma_=lNtE{GJIoXA10xU%n9L?K1Yc{<161`ANC4zFlx1)O<!_9S3U2^U59jD(NTYzx?OZQfL3dI1i^~MV&40i*J7Z0rOdKAJ)ZXC;ZX3u@4({$N4aN1@e?J;(B~!FL`w9mxym{=ZJk3eope}UE%9%w!?TorD8sZ&qtmC(dgGF9C>ojMV@bKF%NCq;v5K{gFMTzugvE%if_C%9qrFn#5@$meCoQ<U*>~(OWlL@${mA#D{n!+Ekkj?8#M;`oApPYfyJdBZE+a#wD84sbY}|oXXQ||kI064@>D@R`}-sRsXFMleHzxWl0W=KuduJy?mme;e#nz{p66seoZCsQ;BR_@`(}-7xL-VPfO;w{K%Pl9sPhhdZ7V)^H77sf^8kI<ul!uSJnnb-YQk?b1n(DIf-%qMt0I4=Pcr|e8pAQJ`DIbhPMjOYYty7(b5Ho@mH0c0aYb`Hw^VUK{?qt7g4whe>)u?4JdbAZ^XkpWza&4}U+akZw+V!wo(uWkr^7GZ5cB5y^OWRqiN!oO>Vo-kO&8zzY%csW6>y#}e}VQthr{2E`>!G4w)p0_1$cf~^b_-TA_e|;d>&%B?TqWf_X_->D>2^l4{#kFJ0`vsycBiLTZaAoBLVICoMSw;7V{hhU!RE2?Tu@Ppnb;m@O@Kpo-E9IO2(CQHO95s7WeD^v+z9sISzhV>}OrCF_OnnWDM$AeGGnC<k6*#X8zx(bI2>yKPc>!^>vzRkNcWdF9h|c&c^d+)$6#gwd@an&I{D}a0B*3u>jPw4fl8L)p9&P*mZ=Th|i7n;U%!Xt=l3`#&gKi{vg(OSrfD$fzQXZbH{OAjG|u`{hGE_lX2;1G)A6#gR$QlEIp3-Yy^MeJv@)K{e}5))gw;`J|EDJIE(!=-5u>c@jlw@js34HR0r+9f5QBj@qDfiuY`F%j^}OTx^dViCtZ;zejM^_JdE}wT`<p!?%~{c_7>O6wleSw+`>LAv<la0Ci;UgF8$h8SeL1#IbPleZ&t_ozqSPPd_(@3Ls5T<BkFAO5!YR-qS#mG@*~fVckuVW#6HZK2jgvl_t9GCTUf85_Gq8@8h)GisIz7IN$K}~68atHi1jL;EWWlk82fEud)!ByH=+I6qqr_^bi%wj%@W^SXE2^Oa+SllTw~FG@G$Xp4}PKFFT>$q!so{NBkj<>GkkN@2&{|m70lbG5VYTQ8=qf&w8wpF!4UC{4ma`n`NjuWudab;f8{sMPn&7TKcX}8&pLwo3vUx&SCf9x=Xl@x%@y;|%?tCe;v+t9^nZu_=B$U`*Bf=_8G-97$Q^kK&%xi(YI~sHT*c5nUBlmnAN#|9?Fhe@9sCuw;8)C#acy_NdM)jY=c2dy(0<i>T&EtqpZeON{g^Cx9<GoL?I&c!Jk)83dF$YbagDb{ou?XL-e#A@e9rrMLj2obF|M<b@caD`Utg^Q{Lfo3-d=CTHwHICo^Y(MVd^X7;orecuEE$R$uE%Ss|n{r^A^aH_z-!1G{rnSV?Ol_laVLyYJ6VdP!xG~UPB(2Ane;?z41PD>{;=(b?Mkw^|oSt6HX()2kOzcnh!r`BHDi%j(P4f1N~0ikNnYX@qWC+SJXLhJMye-gMAXQ2=m!=E&Olq;72Y%oqbm!zxg@(4e5paz6;>rUyAj*c>wLd%|V{ncj&iI3id<lY|O){n;4f4=Z`@fi#)g5;r&sj1ia508jAW$;W@;ldxrOY&x4SE5c<`hy@`HX2f{!3ANnnv3+H);fPcoNFNyQqn9?48KlE#S^#Hy@EBI5FV0|lQz`3-!_;IPf!YSM@K5jlO{&Yw2we`nwU#O5OzBw;^<C^+7KWB#EeiZ8<zW!QK{9T}X96rzS{d7#)&peI%b7x8({rxofP58Xs{6F!vgeT%_DY!oxrzVJR{B>4*^VJQgXV@at<9-DG16w>l->i8?+OIwg-=_dRADHzG{T`knzTPGa-uDeY3;)^}^gHhw`rXn-@|gOxgI}UNo?CXr;d6tnZBT!{TNu}#+nBf2Esj~wn=xl$$zv$e4E+wugzK)L9-k{llz?CAKkT=+W;}o1&4T)e;d2$ke<LMNYX8j0zikNoE62n)J6%qcdR&KMyd@fluX9R(f8jp<KH?N1`BNWngYQrsd14=+{fapFqYk5<+1{9+3!}x?%Gbv8Y6(wiuQv}7Uw{24_Tidbcz(zOU;A7X`O7Us`>;;po3pOMeW!=B<TouYi9AUku#OoGXQlr_#nFCO27K<FGmH4f%=YjvxMH85ZG`tDmmVIK`fol%9_Mq?uNHGgeC^o{w0}4p`|ZpD@%4x7WxTpZ1(B!w4*2i!_Y{5cNa@#<z6$xXe#di#!%&$|)Au>Z|NaS{e;#d?dC*d3pndixILCfm!~2)9Q{W$5i}mV!7xN!C82v7s0{>D~=~v&RvH0foJ8<8050?C<Sw+xq=}7!N>**}i>75ttM~36`y)56wH+0B^{42(yo`$}d|LPCTl4rOd+Q)dJ-=OXAzm>xIrUl@A$J#mKn-3I3dq>?l$$vQ#zHK4+`FctoP3wm|sc%vLko9;TxZ(?c3%=K3ezh0%-)f0G_H8hqy?fyt*x@L?zTG68GYM0$ufC=oLHo>iq`z2usmJ{2Is95@(eD>0oDXS_;XCSao~*RTKDXQ!B!8bIoWuK1VE?R05MO(K7yGByF8DRpBhS%v{QY#qc=X$75%RphjCE;c#yr@Bz_)LX=N$h_IL|Y`JuG=*A~0{BC$L^&iHEJ%SHF7!@}G-9`vIP~E;^PG-&D2-{H)_~uI7%weeGB9A<6S*tjv%3vOm`AM1c6l&ZAM!{FZpGE2BsI=5?jL-aDJLPd!!x{^%Nb-*o;Z&+|_Q#qSVshx3bi7How-`#R=fkAwL7&x6G`W_yTz7<d!sn|*Wf&2xw2{CvF|>mFABAg<GAn1|=-$Un0x@^{;a{FR1_Z@f_j`3LUCxo1}&=f++q_y_R!R{h7}SeHHb62$L@&!tTP?zn#UoEKk9e~A0$?J2k}`WHd_Xx<;EhT<G3YmfFPZ($x@Pr-U6zc?WNt7!P^T;Y#D1ONC6_(wA&N&ajm@r~uOVLuNok8y>JLi=Y~u#Us+q<w0~q2inGU%~$Q5sP^)6|-O3A9BR=So7N050PK@iN6{B>OW^k{_vOZPiuF@&l@7X*5irz#svk?zE>f%zjY7(ty6p+w!!?oPedM5GQTf`c`z-Hhre<i#<k=r@@L<GJdqsN?=<YUqzUkSQ}G<TDh})AHWYc@`Qv@oug^HovlS9wUtksXvtK*xt9mwQpZ^KYvBCqe9}XYdEBQ;l#QH{V!}*hG8T@bfUYst#59e*ioZ@RYzF}M|exm)+9B4mgFRsU(VHj7^-FWf$JcQpY8SC;ZS$y;KBB(R#HOX)Gx`FnSqc9KSo=JY)<G6V2!*SRrF{dz}FQefHJi&Zk^MoH?5_w|dur5t5VIDS2+#~J34MRPJ`rsVM+fjVu#Xax?-eMg)H4@)kq>R*Q$R3F2ht7KVU1sBYtiyVy=M!I_nuh1Y>;-T>=lZ-`{4@D*J>JFhiI(?-_(sR-*jEloxbJ72Bfhy(Wt;;gbIAG{N=1pUxj3V}aVz%8x&iPnUco-OUk&wltPB5p9-fm;aoz2z1OEx;SwD=|*S<Hqq~AluvA#(wFs@Q}c42>ZfWPk!@~_(@zLxJU_SIlpoZFsF;pd-?=aA>N$bY^9@|$nsed5KwINuD8XdkkX&pGj!2hXQFW!~1zN1g~T)So+5d~L}h)MGap`8{rmZ`R$#{i}=@@|-@8_61JkK6`5;>Q5hu_6hj=veC2!`)!Vw_{L+;QBS1|*e4n4qy5!%z8|cG`)L(t)Vcm5_H&sKJO{qXg?^p#;&U7SKDbUFWk&l}<?(#w&pKmmk-vwA=gfH@Q0MkfJEZ+PJJd5K8t1^clj0j2;O`OUOL%TEem)|;mI==l+6XsXk2SiAZw`;b{c-I#JU^#-qy5odyzk6IJ-OP$@AL`#xp5)%+f$Ez+n2`tryUkQwNXXXc?aJgFy^cd-z7iVpGm;`xL<Ga+;#ffcBy9_{?4V3y^elgJcqBnz;nx%?wE(C&&1dI;QNHSOino8qmtpfv(Da$c;C@%j`+s@n=oFl6MSDYLwx<Q6r6h*YGWS8$DrTSeNcb=K#X_k807i59-lKbs*LwvtAfzJ{Y|`Ii0O~#0j)3cXPJ!id2TSq<<t`GC*$wtsd<*-xp$i*+E==QeR48C`n~*eo3!^|i*-rJO1}mCPWBkrf`h2Pef$=wv(-8N-TVX2$BQ=b`8`aNUk%(RZX|A&|J{DIoCBt9SPx@#k4@scMdLm=s~KLK%4`tbwh`^86vVvmE7VNt2%fY`{Q7qIUi-To-Nlb<f!_~wkH`0DvpEbFziY;+;?FIJ_Km*}6TjpU<hiyGe!i+B#m{(uo6J{8Gx&>Ej26G&A^CoMYFbU?*C&n>f4kpw*$3Xs(f+IdWbqB2<JD_Jj;CnfX&n4Ew)h=F)DilJqGjHDU&FcIBs0GMcd(k&tu^=ze_bH_b5r35oW<u{uRh@WI#(XTH>SzBbUkmNo_bwl#Lt7zJ4_w%JyGr5EcmlrWW1?mjA&nMajf{4K8LE;rWJkQKc75J>a2<P&!)(^==bwo@wK4^@i}#m`S9~kpN=~3<8zSeThVW^r|=6n;(p_PiS_Gdi0>LSQ|j4y1^v1<fS+|Be#i10zkkrCbQj-vrW5jnIwSuTySRVG8@&hLo4nfte)paD9C`9o^!p?l{;O>GUigG)v`;We9mY3hkiXLa*8fs`ZAdn(OHw7|nHn=o+CRqUM5ews@x88Ei^SK=Mg63Gr#bjt$K&<zU)iCaVMWp2lykP^$&rHm4^E+;)$Z_zRm6N|JBfOH!r&Jy&HJ|->gjg@evSL^GlV05;;Y$MFDHEe{(X6TPra!99BIGnIR5TZX&U;SFjjnRZrL-|>t$^41b(gy_}ner6ZNd_Hdp-ArE`zSzT)@tPq@t!Kig}Z%V|2aZ(L=*_#UNjef2ns>tac}`B>j_*l%~%q8__r@ZY&3PeecX@jsDgxgPcB+==fY_0G0H{8BBjKkIDA_kIS}hTp6do;$m*K%Nuc@M{#udC~&En=*#<fp07@Q@z$b`-yQC4~4(NfO-btdu-aBoA9HYR!hGd7b8!j4hyCJe5G)oXzhgciZ8lI+9&?R=d<DUG0%ru!q?xG{jRI90{cH?qWDH#FrGU%haiv3VYV+BqFx(D1ft)s*A`3rqgDT1$L>x`r2X+MnCE~C@C#0cf2`7hf7&M(Tq=1wgyZwL)A(Ms@%<_Io_K!Moo|BmZTkfN1w7xUcJTVwPjo?^2TL(;U(?0cg828p?jx{{7af+1|1LN3S00S^<;#k1-18Xo|Kb|_WH+>5Tve`XL)RF5Px_9hN!sgO|DFH0X85u1QP0iM@ZaAMUrV{YQ1-JS5#Ja8@EX2T2Kl{K>e4#+eaMRM$g^WV#(Oss-#_!zt&sLh8vc9k`SybEo`mx}@ip2XIV!&KloQs)C+Htv>vaa_LrUPk{>ieKx5huPUc-LCU%DLo`3`>Xq@ByKQhZ%jxlRq=gZ}Z2f%v<rX~Hmk-_)fR+PAKZdKx@M{q+*yr@G5N|8qVY8(wDqNn<7d{ulV&%e)l$4oOm{p?fUywD<}C6Fx7~9esdtEzKzRGtID0?n}BxMew_|RaM|Ot%&(t?T$PJo{MiZxnX{)E&RvV+#meo8_Nf+MxNsM{ZE(++E0##pYJi&rQbz-AMwFK_<CEM8+lH{pMLJ2_J%Tzkl+25_{Ms#(Qk<g_#W^_{TgY1riz@yrr8fM&jWI-6@PtAIS&mt<FIe1UV}fz3+v@*kA2uKVjbrBe4Ki%+r8^wKeno@yD8sK_`cWSZ~qZ2?TgjGx`Yl{FTPe=?uV(LJHszM2mbWdtF8CBamk1c;s-{_eOWiy4t4%A!!Ps@&pFdK<9h6++bI5bXZ$X-Jih0xulNzZu}*Kvzm>n+Nn5%J`^wd*UYj=fqJ671@Y90voW}D<|KmP<<Flc1o$@)#d^Bpa`0swneOu=}9R4`FE#kX1!TJ2PEzYGowc$4&A@gR)G#d3k3x^+7WV`kHYIcpbqR#R1JY~?|!FiQ!5PY87rY!irzS;2v{PM5x{MmCF+F$q$pZ5#hxSkmAmms{qGLFH0yY`Y1;$P<XK|T87K3u%Z1gYocLioW=a39WGB}&>iD1y)L)=xtFIiuzI&e*vM{3HX~_o+DUh{r#_D(~aD?(DuAmM3sa*lYQ;K!2;Blq*yH_ecNtKPm5D<NxX><yEUzt?~c&n{tPrmKw6yXj)DiXd!Y=vNN?J*_qso+JfAS?8#8<OYJ~b8c6mf52OZ@2a<<SL&-zPgQy|oLF9hap=6~2<bLE%)b`{~<fhby<fi0e48=vMmB>ZOd8jVrJY+j+MzYeE8rY8fLW7<mzaXEct|6Z$uc8hkuObhpwkHoKds5xWO7&z<aw~@73e@7{3gkT00%WB{$$7|SsMW|yE0W8Qov3BWPUM2rBIJVP9Mt?|rP;_i$d1&!WJhu>Y6EgDvKK>f4{B?&QeScpas+h>S?Mxz1bIC}aUwN=oJdZlULYrvpHm-^pOe2+f0DnG?QNjy`m|>#E<trBmmt@pHY3*~x2AfMTa&vp6!)h3l6`r7_GTy^KpjFJK<-N&MD9!OOzlVR$Lp{&Lva&oQ*sk>VQMjQVe%&pq4+DcC|QN#FVs9_6^h?d?Z`^ib@-N{_#E{#`5bv8brpFdc_MW<c_O(R)sw8W6}cO^BSUdLY6WsVa%pNFveGhSrB3A1WM^tYvNKsn%|TY`NY;@XQfrYLl0B$iWDjyrhT_509^}E~7-|Gr>3VVuc@snNacUy@IQb?unS7J{iu#=Viu{B6o&1BG$p)&frA!RP#i=F8#mTj(^~klzEvc=^Ey-Tg?qn}=Pln<?)ZXOYyq5Yf6dS00$p*3qwKLg+>`rY$b|)907A6-Uf6$=nTKd3He2t;_D)lS*D)|ca3;7E967?-v={fQx@^<P*@^<nJ>O}GkazAP}veJ&^e&nvydgQL;rqt48rOxE0<YrVIS;u|fjG@?@>OuA<cc=Cw_o4<;dy)gmVbsCoFmfC<hOBfGIgUJsp?C}RIC%^C6!j+g6!{MI75NVN4fO~44fz*UT^qmnT5(ohFU84O$vSE+vW{Gb+LBy{+=}W&ZbkN{_9T0g{TPaUsC~$Ncy0JF6t|^%klT`LQr*cl$$6;-$a%@>8dO~y=?uj;sMp9h$om<J_ffBs_mShNSIF_?-PB8DrQ6B7$@8c)$n(e}sr|@GyOKwe{isdJO}W4QsNQ5ha&KyP@}K?Po1wVBC01KvrX@Bo6wjrOC(k8Mvcw2#Fm*h6Jo5!pdy#|5eW`)up_UkEi2>BU<i2b(fEq>~KpsPlBP*Rl9z&kMP`rS;g}i{gm3oT2m3)?ZhkTZNpZbP;pZt#ci~NqP@!C_@n8r|?gQ_FvAeW@pA(tfUsjbL*avQ2Qxed81)sNhj>~D!4)NWKivLCO#Zq&BqZsc|h#kHw5$qlGQ7>e^#Ym#g7n#@mC*I|CXR{U9m-XMP_r%?BkQ^<$ON^da~ALSlC%6)y5{%VHe<<$LTrTfUs$xEp5<R#=q)ZJvI^T><HM(RkiQa`eh97^p?R@$E&N)D%vCo7#v4kyP_SCdzB46)QD<XG}#>LT(Y)-;(KN)BZollgBa^K}7RP0MGA{FcaTiA<KrV~J{(bu4d*#tg-k8H$~#`N&RWTk3BOY)gKvK_8Qqo+rO1U#1=)UnU=+t|T8JucJni*O8;BeaKN{e`;H@Ke-LHF}V%djaq~3MlMgSO)gKaL~TT_M6Sb7T%V!13B$z_r5K8HQcIAP79!^)XJsh1r{*RrEljp2J5XK84&;*5mgJJ;=G4yQ=HxEaQRFV<vDBsHvE;SXL*%vOW7O;9W8`~kZY_JJtR*Ti6qlyvCYL5>rhe1FnaS@p=sog1=6}yne3yENe3yKJx|Do^yqP+RyqP?k+L=6?97JtN4kCAAC~iS@CA)H+S}+t>rRFAAC0C{vB3C9?p_U+5A=hLmu1j?xD{Vqn+K612{O8{`Vm_s{t@77q|4M6E)l-A@Ds604e`AhMX<MuDw&mO??PE1peK>zgBdz8$lJl)}rPche<oYN*KvsI*YVFQjt?zlRztYEKrN6bmdqeR@sygF7^0ngZJon0zvy;nEtC7o)-KdSpZsbM`#je!KWLL5y)rss#wxQaRZOBhFs5)n#Fcc?IFO!qVd#Fdqd&rBa>&T1AA=D^x2)P~ApWKdIo!W+6ot%&AMpjy$oR6HHp*R<{5?N^-axQW)hT?M6`eda|$Vy9*mF6UuBmc>hlev{<B`dYJ>et??PJ7m_)PbzDq}8}eat@R>x0;jYoHM0etmd!_=UC}jt2rObHBq|OYK_)%4V50VTGL}(bEWsRzk5LO6Y4kZ@19X?!}B$_)gH^uJ(!zk^q)OhmU~ud4XZs|!)l+`;NGvnv;NPuP=VJ<1)lYPuAS1nwo3D?|8uQn=Jlvlo$rd3-X+h{)OY7JZ5(wQc^r8fL-8(4JfJ?LZX-V=|3@{G>)SwcQO#r(il5P&MSe!!Yl(%_0O~Aq0J#Ho9JvG8K%GW5kf$;fo2a|UCh|$Eah_x-PP0To8)zx&1F{Om)u|83DiqhH{zv{ZFLfD;yD$`2q2?l2A!nefIm*D-iZ62B_L47>S6I#C3Wnk#)By4jvJbTb*@rxcY9J3H&!<i$&nF+Gn#c#qsnnC?RI-B&G>z=Q`K@a6ciyWq6nCVSB6lSBr&cHTCkIjMlIwD=gBXfOFckNqRw4Hym!oDNmm@#rdZ>AS%22$Mx`Mou98DcUjwX+$`jAJHr&9-!r;~S3=aYAkZ&MGFZ<DjxKvT&o6gQ`;d2h~8JeXRQJeV9t?MMzI8>#)tM)E{z5IKl*t$4I0Mp|M#bu3wFBzZhJhB}KJLtaQ-PF_e}$xytFx`n)rypOtvypMc>dW?L6e2#jCe2#pBdW(F6e4qN5e4qS^`j-5PoKF2tPA7k*+S-D@l7CUNkd@{jt5BTT62mP#$`WI!<H%#kQ>fA8DdZW{x#St-rPLMVrR2>v=r5-w?5NqvcI4kS2*uy18Och2+JIFke#cP!lKP(flKg=Bl>C64LcL8+Az!3kAYUY(q#h@qBqvb!k`u_=shi20IS<<zidR$Tl2?-#QKQL=$kV9f$kWIZsH4ae$l=uC<Z$vZhT;h77;*%8GIa`hGC7VqgB(X*LS0H;LS9GROkPLcMcqr@MNXt1Cnu86QZJCtlJ8J&lkbpUP@j@tkUvu2la>A?e<a)3A{0AN)&6tfe#}mGAm?Hz&P~lp&dKX6H#G-22d~ZCj4W1pvM{$&Te8ycHh=s5ZdK=Z)~@s|S?Ob|aXsc7D7|GhC$~6fO3zr$;Tg`c(qmS0evE6PbdS{<?co|K-D0(-Te#**ms{<D<=i7mXIbr;S=>`fBdzvWB=?}wu~vIhaRhaw&EGw&_|HC998Mi=^Y>a%Jb^mi=I^zmcp5dv=I^zpcoB7>&EIQN@oMTyveIoff3IuBI~a-&QumRSo**A2pQ4^4pCX^9-XNbRCsXf}lgam}ugLev&#CF;=j1okujDu657b}e59A*V#TxH1YOibD^LAuAp79!A|F-(KznM?zH>>>L*uT<uR`tANy-HtN)&G*?Q~H3cG{tJ{DOU57!ueBr(P};~a=w+Gw3`2uTpy(gR_m3(wN<*Eyq#;W_^>6+mbk=Fe9aP9sfVa$@*(nChT@IX!(^qK$Q#L18H#6HVi|QkbrX3#c|Y|qc|SRcdWoDwzROVjjCzgyjGSgQwls#~*Oquhy+XZ8zCw<t9wNt+*HG7z*O2Ek6i=saByZ$gOlK&LVkn+OolTxZj<uS*Scc-o)b-@W<PFsQ<PGEl)Fko&@@48>@@4Wv>ND~~@+WE<`4idR7W$g3LU9J$zjLivh2sC{T_OKRzDbQI-y|QQt|1>GZ>7#BZza#8PA5<2T+d@DHZc^>p-v*tA<v}7l4p_^P#2RIkXKPRkXMm+QV)=Kl8;g^laG?GQy-GAlb=vOk)M#iP}RJD;cLa&xE2}6*~nR`YTmQ*wc^iQi<{)n<W%Yraw_>Wbu0Nac{g<)c^>Clac0Yro5>PcEMceKm+}}^|5^TLEu$skEXFiTOt%Hk;OkhbdOgY#V=U3f63waosAI_e$fGS0PBk(VPoj<?Pa;pIjv`McPq0J;HH<on97gUz?L+QC)?3x8XDD`MC@#ZL+=|+d+=?7T9Zmi-wjhS${tU$d48<d<M)FAVMCv5+L~=BBGC7(YL!Cg5AxB!xQ6xk0IBFPq9C<jk2YEQzhpH$0kn2)i$#u!asb$E;$we57OHo^qOOe}BgUCUgyS5C)?HP(&Py@(L)CSZ5as#q2btKuBJc2rrJc2x)8ciNgj-tkpqsUXKk>si5Db#V~Dde%#;pDO8V5$!}nB0+Cm)wzDg<70kg<O<cgj|$d$Pxvqg{eizMYtY?8Hy`V+mhRI4Jt4c*I+1irnVseSsQ1nBiWf;j9QRfkbM`URv=ekABy{0qPHamGZYW8!~m)vwKv(1>}iR{R4;08a&PAKVkqup2@h%@wJ$l497-Kb9?ZT&8H$Hl)i;cxco5Z(Jc!(#>PhZS?qD^B4h+Q&8H(K*iknfr$X*;nGlt?uR^x2MP+Z><)v0Z$9^^J;12vFrAP=R6l0!M>p$x?#)IsDB@<3{L@<4JoY6o&Rayx26ayxQ8OH`y*r8Xot<Q!FHD0ZVZBRAt*xG@yhqShzZB3H7SuS(R?WThp@mB{6&70DG@M>(n+*^PZDE^CRJmT<8|Wom6|O>%8=OKKBxOR_h$GufNmlcBhmCH$#fsGZ4O$W5tD$W6)Bs5QwoS$8#t;*wMsa!InzYHT`&;_}qm<nrV?)RyEr<knPga%*x|YEQC98ynkv8U9cISDJtSQ=d(1|NI|o{;&V?-=9la|I5ynT>taOQyy*X)bp0*A<I_2=+{bpqe%N7x_UP8'

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
