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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_020.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_020.stl', 'source_sha256': '0ce0aebf587613b014e8535077b28459701459fdc48bdc5ca154c35413769012', 'input_faces': 847, 'input_vertices': 490, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18318957090377808, 0.12561990320682526, 0.015068277716636658], [-0.07194578647613525, 0.43294548988342285, 0.24517154693603516]]}
GEOMETRY_BASE85 = 'c$}r22T)Ymx9(4mqKG+1u+3mV%$VCOia7^{Mg+5B&U%bv!W_ZSVnY3cn83_YjHs9ubDJIGn6qB?`aUl`uimSAb+1*cz8`CLue0~s@r0Vz&C{gKrQu%@%`a`gogto@rYw_|OB)e1WLTfTprM`vLq?mlY~ok{e(R!^9a^;RV$w!vV@vf68X7pHR1I^fTEX6>%9=|B4;nITNWeh<K|^{5DSzXD{zHRO{6l*OgaoDh?OwUMS6Oo<kFw_R=KtY8my{~#hliYqS6XW4`MOFgZatvXytJ?QZOwXKkiRF*Jfzg9S5o}ik;>xNyQSTy)aGA6{Kj#M#Ic+mxL?X2cR`%wg@~X1pFN`QJ|CCz=`&uG-*>(sam)$v;y0(yCw^<%`i8`@Y=XZ<M#R70L+Ya+-5`Fg!c4?3R!GWQZDHcK#P>!$o7aoO?^d9E=93cN(qP>|rS@S9#c#Wo6LCIz?s4=RU7jIM^<3iD>W9Mr`MH!gFPs!F{^#T1?{oW{lpj=H+GU(;kL!*+j{4{B94o&&Vu3$)fcT9(yQMznF{M$TG1=w1wgoj0%kP{@qFv9%i{EnXg|ydpDILl$@s;b^FIAN|mKAAHpV!Bwz4m2AkpDMdk4e8Dnjz(lu$OU;ew$};<l$zRj0gSfYw=t554$Ao9A=evS+c@!?OjRA+hdzayX-OdP(GoqTvspDLHx#+MEJcA$#t#X*=3wqCLR&L=C@heWfXqBOX6hT4}aI5Qr@<#-Cp_cJ$B)`EBukSzx`!AXfrm5-#-34@_hKR^ou2GDdHUMB=xt{zAAnrAr$o)QylS&O_e;DPtQVrF0DX4KLw&)EoY+qvj}OI(JZ6%i_vt5_>C9Ho26JY$-hnOj`GjHqrVD1lk(cTCaBM`bP`|dI$)2Z-?BLw`7bzUr(Cx({p-9gOS!yLq+g5?jgg1BwIseh(;*oT+PPYYU(^%vJ$E7h-%6vN=B5}Y9*-oSw%YJ(OLr#8-|zjf4kTtoc~2jSZ#7CCk>7p%a#YGcv`cw=qnlEH>(7tkw_I5u`O$_{k$$ukdM<u_{w~y~QjP<Tesh{a(q3CstduwYxi5aB%~#C3HE(vv@A6zm{L9s(AFcOl>=w<t59Q~tmGWAHO_FDG@13aU)}v@wvrN)n%e!dA3CfB3Tw90yWY{Qvn`t2W-Q$_WH?G<cr-HlqEuqEsIr@!G@1<Yt-wtCu{}qb%MvoG|xvwwg>FCjDZ{Ap`zfq=w)KlL-3UMO3qP-<&ZI|Dr>xS~lStO2;<DJyUVrz}~)xs|$KhrR7w>3kYWd*KC{e7#+IJe*QM*VyI!nj?20pr#cext=I$&WU59>(G3O5(RCRFv}Omjk3e`oId}w`SU!Aip2e<(T+myb!1CD7mgttG?vH8ebautbp}LE7Vo`(PDz%lJAUM*K)3|)Zd6G1plbMSU0LIknv`Fmm6`qWyas7XUOl&OPtZJLYd^cX15m-N89;5LE_k!A`dm|%KBg~@KXF*>GhZ|->bxk-{Xn+&C6F~o_@I{*D+o_6u<ud2HN%WJ^FqBU6eO_A#a}du;0zNf$}Y_7@wVPN_(w-7sYR%^BU`$9xCxI{m-C2p6M}O7w$MI|2=cO_^l1Tq5j#Y%6g*P;u8LqxBFFOJX`O_ir@CUI_Brb9491CHKGu|Y-h}`Tz*m?Tlz@U(|^3gw{0wles^0Veq&M*jC0d*nHSbx;V56Q&Q<xlolWv!AGjRllN-qRHvg(}M&f*3gz_%~Fn-Fs-6rj77K*$*(Xd|(PLla<3!jd9{^%(2_40SI?`+W#|9K+z+0oUczbv&!BYut-*vI`M;m<!1d0S&(9USoLtfSw&qpP&btQ#1g>-(Tz7T?ACwlN_}v_%)hIgwq)x3Tx8jCaet&Zy_ZMN&^~Rwv1Wp4=YwiQFoFbF~Iif6d+o{k8I;<XQXXFL^dstbqE=D1r6rXq;SEt5*hbmi&@9#?Gx$PrbM+;sm}Fzs1)@u4@f0gnEu1j(u&*YmDb-1yIi!&aysOH}8{vH@4+N`G3rkAN!YfiSoNP8IkAf?BCCeq@EV56a0UzmvXj=Z_zKCO{mXEuj5khbVD$n%V~(e!4vI$wjAfTw?B?Z`7Co}T<VoPai01575>CU*w^a2V}G3RMf|!`w8YV!+!4q0S^V}lZ<3`x7i(htpZFktZ9@O+@^}0ltS8ytBL3iO;<qiCCF5Cd`v(3>1(D|(gJqr61D@l$Ve_zF-+h0^(XZ89iSg!KeXIQU7mvknWUhEa$|W|C^;xU>0RGSs=&!>OIIn)QBhJCcSpVxCMjj^K6~FnjE7rX>Q#VVTG<Q%R&j}LW9OWwWMaz+l_^u<cUgfPM^|80RhWIxU(XOaFST`P@Lwl3v!M{3gkE362YM}mo)5&?m>JGnQEpkn+=aygM7<G;#{+#rf=PL@yc(Ccm#BVGAL*m#c{K9^5<S4G&tf;hCpYHu1X-9{Hh%>vU_|2EwV*C`{gZ}ledQ;*%|G>OH5QTb<=?8zo&$6EAO*SLWs5S8C{Vwy!d}FQntv~J~|F06!-eRj!zWzq+gSV38y4v62Xm6FQvR)Wz;$_~MW0%7JVGrhM`?$z|`JZ~>T>Y|~tPi$Xa}j^vf>Uzc>HDznES!z<SN_8KUNMi1FMY)f)bm#XtXG-0pO)Xb{)N1`pT>R>-csUgF%yx8M@uo^|Bl4EF@6m4Hh-kFNB8-L{V{I{>eKWk*1;|JrCs*0f$*<+D{<^oe`4Ku*AxBt^^43Gy+muwqY;6q=ffu0cV^7q=jhiqw#4{x$9YMw6@Yq9nJ;k+Jpt>9;g9&vVJKgB8_s*v{4o9xBw_sb*|}c)Z9C(-PB&3LYO0J+?M^$y`D>ii-!>|0y`x_nn@g^1F}b6j0c{Z{G_Q;kquWrdhatZ3zn+J4?3MJgp6EN8!+*b}lsC_{%6PV>X@u(*nGAoGwvspPRDE1GV7K_~Q&vXH^>frk9+rK;d{3KE#*gMz3FD#npE!qS?Sga5r#$c*FX2CwTk>i5hF_0fh4a9(B;1cUWk)?<HWa`8QCjg^3OQpuY<I$XYWOBO`gPk6oEtZ^mH6gA)5G7aF80|R3wAjAjV^Bye?TzmIlzQG+^mK5q2OcOZyx(}SgzY-InJ>?Vx?a!>EYLQTd=<;B_oc{NAVkJ=i+=)pftu|o;TvxJ-(rT{TfF*`pw(tN*vqy+A^+;o39Xm(mkwiZ9>Fvd-fFZM?b`MYp<92Xo-0&ep~&Ua$T)YL##{TSHy2=xg`Pp8+pvpueI>PIxr(5($TM%n~#07mp}HA?PqY^Y}+v2-VKuaYkN<j{=JIf{5^L6Nk_ji^Nfsh?Q<~h`@Wt;J+n5#Iu+${!qIQdIacD^9@UY&=@U*M&c2P(zm{bscRBjaz8R&wzOjS!uWlSi`Ol5SZ#mLj#<`Ip0sWXXOX_1uw@Bhx&l$+WKUHwf*~E3LT|DxzyQY-4%}l_3)1x@#^FtdcXDMGI5%W71ak|-Mp4!{H$at`B-Hq#xpM>)1&d5Gvyx)%cx6TEB2Txfi^{Vh&n>CU4+G@R(ebaJkGxD}75%&dcW}==M;Wv&C$GViEE6%-7Rv}K~5X@8W39F?(USWu{;+vc|EYFw8`k*B&M7y?r!}<2u7n{^)*(}80>x=7p{y=>T&P1GRZ;r~}vx-1VPeC5;@4)?$=d_j5j?BZ6&-;P6uM7;qdbK<Rc_<Ni1ND4@ek?Qyc{}n{{MO`~(vOz={ZXGKi?Ck3-XQyhJ*XerTP*<n`|JBoN53(rIQG*%S7RLg+Mj+HCl5Et{;RzSM)|eba6YjW!TG0BF!Qq)>&&?sIOmM(fjk`X#W^a=5LqA0hXN44^seg|SFLeB-nuK=wWAr<^U{;z9R1ql-l*rV0WyCL|MsZQo-5K{+R;d?0|Q&4{I17XH;TsMJP^|Yd0yHE_3?3AEOBc3;JWYg%K6stjllUNsUG4_Eqe{+GUI#|UJLnLnicbIWg*-@KJ-Q&!Yw%8dK{E|8lmp2C!Q->O6^-Ex}*f^bF071b8Gj$SikcZN1Tv*D4%sef}`JN55l;0S$D+Iue&WpdtImDzGHo1#QAv^`>b9P_wiNpp*}@gAP@D2ApVh@h~u4%bJS-8?cLynd`>(p^V#6}(BhF6c?&aP-mYqa`=EYl5NEoxoI~{S?{UBU%7psZ9*E!SlR?T`cl|P?K8qUQ{-y928Ml^%FXA_U8zt+erDqkK(=&Y(zgDn0*8kDv(B53{5NFy(oX2h_;yGc*x8k>qDv5K_`L%fdeDFTvTpEG(<f^^}^Yym)tr@0aA2~1>=lM(55ohUJ_&vwt{E!=d?S=>H_i-=Ib)Aw?pDuZ2{8%C$ArFPFqWs21QXlKMGPtjKa~AQ-U6g*c4ylIc%HvMKe?`N6=)_|(FKl_@5r@zHEXPLRxscldl)upu&u=~EE|u%X>=M5{#Dw}Z+=%nioXz6574t;92D{_=_WKpce^i{TZ<bn3@Z5OsGF&(62%e|4s*iKvk~xS!ZXNn%%LJ^St7eK{zjs3X_V^(fCw-?P{<tZ4?ycpD5G_9$^+^oCzIlBvp1X{mfPB_Ihja3onB~&mv}4fTN2TyQw%lGkKb$cN<tsR29$kO7QFQen)F(RRU*`~e-~g0gyiferbGzj}%h=E#{`_a~T*&_$^7FF?;(XqY`Lf_8o)1K~Lix(QQU1hctZ$#1V_eN^g7+2!hRA#}yVgdW4_(l|uL3cyf~zABfyuZZ&e9b3E8D6d|9wW`x-Y)q`S3U|_&eOe{f_II1){S{BhNAE;olp-P~vCxK>3xO(Z63u;XWn68TG#wgnj?JJDy8S{uD3%rMN#bew+!Hc67cXe*H>)Jh${N7KJ=rMEUeNQP0zL(5?sP#jizY$92Dd!}xidD1O@lcZ{EWld#Sd-Yb5~<ndT<JwMC7Z;yyWeE*U%PHdi;W!~#sb|HS(%2<cL_L2Uzwp%ZL`~8ksubcIibyw@QR{Yk${a6Q&zLImGwa04s3!lbyvt___>W)Tzj3*dZ6}v2v-*pT@{Ucqlu38^Ro~?cZP|t=zSRV>D#CkcjC;V6M;QXAe9nPV%x}pA6e;q~rdWjkfIwStGcBs#oUN|S%+9J-1eCV&Y{^+l5zUY@-jqu*BPAS~CcCLl^84L4yY=1oew^m2_kO4TKxZRp7@f&7Gd)p`B`C+~SSPxHTg}*=Euj%)G9dY#AG9JV8oXGsr@8)jKh(F&S``2)sb1ff!9FqF%bVa*L?36s)|N1C?Yn2MvmxCW-zbpCz<&#<`VSeVrbNB=I;Loue>qXcetgHW=5x=EU1KbzCv`TyJ+jfdyzcUB*c{6C4{P*KqQ2y5fJijtU@;%OS@f%zG@cyW27VJ9{7Nh*U1e^n}uf%<Kwot@RzX|(S*Z!Dai)X{%uL+*3JUxm0ubd%%Tk~=lw{_-j5`WbR;y1_M#lCjR8}GU94nTeigrWTTn|P1bqd)S{$`kXwa0MBMw#R)D|GtjrpP`x8i56`qe!EK|?sxK+SdDqm2<^@6Ec=<c&tjR6)*H1@|Mt#!Z?)k$&j0tSBM;UPta};W;XTpcRS`c^4$QBU0oXUjl}GtnL3n=H?4pb-`z#Omr@cje&Tp6f%d*yt`m`v9^{4$b$&aOr3)*$4HJ&p!YmDbw51nw`h4*lu`z1uqjkXEj4odm1bMYKL{}JrNe|#0c{qYL4i_e+$&<`kY&5v<XrI^&my7h1I8^$m6>*y&mzHE0d!(U@1o|B*5CjD&vaT5L+xX;x}mXrO(nkhm2=83(q&UY_^e3y<Bzh#R*=AGLUjPn625og$WJZF1^^SRx1ChA}C37)h0bd~eAt-S^DJ(^)&f6BB-{DCzP=Xy6hUvgQ8@%FKz`1L}&F|TVcl5t{oDhGd%Gy3bvS-dx&Q3mxi?LeG5P1nfp3KmEFO)(gU9^WOtZFhduGweF<7rr0Bc<z)*{MKpx@t(TYFuXSmPKWrn{=hosGzRxy4elL~aeiz&+BG^e#`(xI;<t4=hdle&#e0zQvEsM>T@3Z%`B|?MgE;N|;lETO!qIQI6+pk2xP<Gr*n;v0-BF(B5c`j%C_fVGxwhY3#=GvcSo{{hD!6|<H$%=L*61mS6Y~u7H?bz#J2e1t$}U0v3(uDOL~}$3_}vfTytKF$p10I$E`I&zOs?lnn5PrH4mgfOd#my?4$W!Gi{D(MKKiTgP1&z?cQf)6JQ4d*+y{B?VYO#qJ#DDJ^EJtvIrhnZ$+N4A>`%5s9kEV#x*`7meqX#L2Ir!i$>P_?`pEvO{c{xe#s1gCZ-2QO`||r_JonHNQT|dx^kcf~*ng*<6u+ey&I7h7e2+Qj7|Orsj`d~HOsvo6wxFJmD`MR!J6GCko45>d>Lug-UHx2m{<d>6%IC<Aewi>5^Y~LQ_`77q{cVlbGT+VH+8|ENJN(|G4DQEkv_KvrN?<+?y&!(grwQ7-FdfEE>sYz(uwJe&esfuTZ=jd($9m;o2jyormFrq<cVr(hrk01_3*W;S?~<_YE&Z@h{NZI#pYMzDoUr9x@#_QkB97BCyeIE@Rs7nQuGoLwbljKO4#8ioGR`G~+u%L9Pc;0~AL0CSry$0|wc+Bov_Fph<>h)=mn<F~#Bb#NiTjkR;rL#{t1Ze;AB=hJpBZ_p<c4|<K7o0ZeIL#V&(n+Fyzm10D`_yE2X1+_SL)Lw5$ork{<41B&)pTjrDR@=^KRGh{Mm04{4YM>{;KXKoR{ux5Wjw{ImXY-mpFgA&K19T_#Eu}S8Vt$rB{gf4L;v6obX;uU;HQh2UcPpH4MdgxoZ)>Jx_mpXH~@&?~AAW+9UJM%Z_tnLRa*U>j&}cFK^<yE{E}5)5B!(8)x_8dH(#uIL|CTCVqP&_E|mRi_9a-$|H!=sxiJluq0tWdbL*kmH-=`dv3`IofIa1t?p2)d*ff@yMm}0h?Bi3=236#ds_9Wi1X$Z#$j4d<T+>v;@sx?8CVtPfzN&6FIEZPeKl$#<;^9!h~FGG68*lUFy3!RcEWY7b&%iU4ROxz(hza9N>~@lCCmMkwRauy|NaimDCs8S-}bIL@>V-g)*Zb^w5(T_k>03(fkf;(Ul-s$rF~BLD-OcBVqPKK_kDCief+lJxjol6`{=ar7kz{NyO0Ctih`fwq@ELBA^z{@RPnpTuV?uO&!wG1vCf1<h~NGW?}2QmqH)fBXA}SL`vuE_%eX%-_^0?S-?O8=g?;c`x>I9Zm-p$qPl$|j?O7d^uaFyY%8x^R-_%6;y7whN*3KVLf2}I~d$VF4zPJW)BHZB*Ym573qY=jE)turtpU;E5Wh%MH(Qk<xg?X{-5$^lGr9~cmdte?dy@Yu@T|=DpK^Q06XS_$q@jX`JbR2`cow+FURNMbt{KmGim|wnc5XUJ={PwC?$LzT(;yhk2R{YlXYjNINu?FM$a<urhix;uqeSVAko#0I<A8-)s-Fuf)j(%H_G|2zuemJK++aP}Zv>o>k^YY2~)CR6ceFk*Gbsq)d{#{#z`1ju<pWB<Gy)Or&K9jTHJC+2#AHU#(^5cJCzJH#D``PP_ksr$=oNt3m;yz=67vgwUK)?LqhkeslI@WQ1X-`9BU(+6Bg}=5N_L0bkcwUtC=Wgkjma|aLoj&N_DzC+F^a;c|rkBFH+WfKj^?kWzzUc$YVE_MqQT(<|!RSYi805|C5aQe}jr_E!iR)I|FMd0pKUjEO?P3i4epr94d)MMV>C;-&)1@)K=eTRd`<Gc^@Q1X<^U#2ecutvlh4?Mu-ss00-dG0;Ekb$k!pQ&e%<z{96~7kBeAbV|zR-FC>ObH)&NBt>%XRg)At-+o-&q+|v*7*IoM7ak0oGs5xgE|?5q`+q{sp*ysoogZ{azjQOpeERcKe2PeuIbjt<T!wy2D@Ldk+tH)c^1e<n0meGc04%BX1q?J*qzTBl0{sE#j{`fH=E5BA>-S?UMM*rlY^I7sYp>XCI4S+n68odRqLy{Tt$OUafH(@gLk4zwWwD)){ljL&$&O<Knl6$77w}S`zbR*kJgdF5`E(^{_8Tb{D@faWm?FdpVw0-)e$-7JrTLa55a{rM*SPZw`Kkd_FCY=a7xuP#@pg*w@C+!u`nk{NlHz`-b{dnU3#6{<*$W;ykV)`L{mkj_2ZMcZuKXlpFIge`CD2vPOyDqI<!g=M>hB8GR9FNK34@4Ryp{SV{c$SRLhkl2HEcy&clt|HQ$+)(`n{=_h`@*=N*eM~BmOTmS28^=jX%#8r0JG-VmITv~8|!>8)Xss8=e|NE!veJcNdeX8zVx!V8sQ}xNFlrBlJ=G64$=HwhS#m6<6;?30W8d&KfveG7GrGJu@jv#L)|Bk76KD9GhX<zbu@(G&aqcp|)sIAFL+mZK?4^Zoq50GQ20pwWnIqCrNIr2T~Ao4x(W9mHeWAa<-T=HA;duo63d-6-_Wb#Y$E9z|WEAngVV)AS9KPmQsx{SJ*yo~HmZ9(=Ym#3B?E6qtRPcBAN>`F~fb|t$}oyl%wcWQRBJGm0IEV&Z76}36J6*-i;fUNWhIh6dIrns~TTG9korr1jDNw$)wQ2!z;T}hroo<~!>oVt~~oV<}5OIEs>ypbG1okNZwPopXBPVGbPPOd~PL#{;rz%iisA8Hk{GR3c{HBG7GNAW9aeN*aqQ~Z)z+mt#!6~Cv}Fr|)X#c!$AOsV5v@ndR5Q|f$Ce2-enlsdl@tNEwqrqUw(TltI76c40^kd-ba4<y^D$H+=Akd+=H+sM1Am&i&J$x6?Wca!(f6rZAABP+d2K1IGoeMG)Ren5RfR{E6ufc%j9H~As?KJ_vAKKV5DCRyo!$VxYnPm>SR6tAaFCa)*!)aGQJ+>)Au+>+dirnm%E?ExjIU&zW7XQLh^D^u)7-A7h>fUHchnHo!u<=8RP6c45jBoAcY52h(zOx;ahOkPFZL*B!FT}4y8k9v!|k9?W>fc${{cbR&he3=|iJxxB%zKN$PUP4_@UeEqmLQ_17+LAnq+?U#l+?U*jT7q1Heb9!ccs$jO?8f|#rw%3$X70vQSCLmSFXL&7S5q&OFSDJisY}SK$up^=$fMYXnbbDqHoV46{&pt+?v*k&W~SK06x&AKL7hofx|6(v{5SP3`EPPs6ZA7#sb&HzQ=EmS*opd813QslXwduQ7vx>kDDp1y1nMO61acrXm>fv%LG4BE#Wwe#DemWxmwq(G|Dh@VK~wyWx`Vufd3i@uoZSRfxya6(WFcoK=cOsmNp&LUB!6PQR9-&O6z`$#BJUxOrcNM_CU>I-lDm;RQG1Yku>GBAihEN3L+(l5L{t2S3HpPqOmP9~JMuf`rU3Jhmt27CK~r3anv-0JY@(`MnE1EiBh1ep@)7cI>S*$CavN$lavQQQwG+7$+w4nI+=04@+<_cPQ=HWVRk_GYQ(T@}fLxwjo$5jMV4JJc6qlnZ&P+9tGm}p-FRJ~gXo?3@hm!}BeW-27KI8^eU$QUT*?^|FDK(PZl)QzexS$ED+OK#hwKFv<xih&TwLG~Yxh=Iixh=UdwH&!IIS(~6IS)BWgQ~nF(G(A)4kiyI*P;55>yW*v4ag1Hes7xM+SD!NTGT_-E#yPwIwq*fOC5)N)uGNH*CCHcv02nG>J0Mr6g!(@H>fAcH^@h+JIF`LQPePU7-L4!6fdF<B`+dRqA3ohb|!abUj|d#l7q?JsEx_p$VI7n$VJK5HK^*p>omn7)PdxI?6VM>;_5WTrKsLyZ}v?ohdwJsQ=FGtk(`&Di|R?vMb1yHKvr6ioQax&T9BNTT9R6jT#{UqT7hg$v1Tb&k6M#llV$4B6gQ-Lk{gm+QY(^MlKW6=k^7J@P!EwWkljsCHAdYzR!5NC$^H&w*Po_%3{CNLn&NP37&(k%G@N>p98Qj*DLz0wOFlqOpeepcy-vPJPEN6_R6F%L*-pMqy+OWBK2JSLK2MILMv<d9f8uD0mr*B?myt(OgUP|1CnIT!D^QD)i*l}1;NOZL&=ilMhLA%zH^$Hu*Pxan*B}?B<|P*<yHInHUC2(<{N&$rz=@{#4{8STALO(Sb0aM^A2}^KV~Q1`=B6nwLd{1mLas_v>_yE=&dT|wxGS|iwIsPD=U981;_lRD<nH7ks+Al>9#2y|ho*QeO>q}$J+jh<<St}CYD=;oxi_^Bxi@(UP4PqO1@c33VG~r%+rl)(?Wq3bcI1B4G30*aan$MLfE4SLVnNid<RJ1`>NxT^{&p-)@l<L!c`A86HHJK&yn=dwyn?)jrZ}3KKwg((p((bOrg#H&A$bFN8#S7|jcia8$VxAg4e}XkGWiTS$&|VVCD9b0NU^;sb|l62(-a@4o*<uK`QtRjcc^yq9r8WuZSp<x73z7i(m3)J@^<Pn@^<n9>PYee@(^kT@({8YRjo~4{9Ex;4LXMWlst`EgFKB~ms*%ymt2&lI33l6tkj8|j%=bS)~J7wm8R8F|0zyG%}7o|&Z4ERO<8D)OQ%?6YB_2layfDdYHo4~vYA?hY$kiq6jz~EC08LgN-+zyBeg17sTcY8+NXE}btAPac_Vo%wLMvBck)(p3^j-xL*7jtPu@+Aqs}46k)x?&$<gE+DRwr+&Zk&7^#=I{%Y@SukEC`XEA=CfBu}OGCQl_Vq%I*ZByXoFenWjoenZZ0f~xgYvC?+r{N&cue&p8Vj?{5vrCrG#$vvo@$VvmqN_&xekXz6c|4CEafu=Z+rr3`fK=vc|rUsFFllxQ0l9f&+_a_gh&L<BikEX65k0wu`t|3n#PozeZl`bStBoCv8k_S;|Q$xv0*O8TOA<ri7r0yjv-A`6}oUHT?c_;ZG^&a^kc^CBxc^5g7x}6+Jo=aUoo=YA;9YP*J_N01|J;~2Bs9IYUE1gDuMxI4e+?ZOI+?ZUPT9jOzoP(N<oP(U1Y9ePQXQOIl^)C%M8#xb6aRF);veMGz0_191>Y7`PY9Uu6x21L@|6cpr(iGchioekm|D<jt|0Jg|!4zkpZY3*?AuCgyk-D3#OmQY^99fxS7ZXfzI%+gonc_$E-5@JHPkuzUr&w7NG#B+eS()Nr^qnRDBA=!yUPTQjD;-HzI+d(+A$b*fJ#{;IJ^3W{4f!PbBTccZ398mmSDNBl)Yjx$<o48#<o4t))E?w6<f_yb<f`P~d1%2rDgD!wnm5H|sU65=$#toL<htZ0G{yC(e&l*&3$-`dLT*a!PgXjd+?3pmrr4J{n(RyVp-v$CkQ-1Zk{gh{sl&*>*H&+u;>sqx!&TayI>?mz&R6j?>TFZ$J7UEV)Saf(_sEJjQV*I^-#aT_PTgfneP^wB9yQXG`i@)i6zW`4>U(g-R_Xv#>N|ABrKz5#)OYTR)jN5mYTf+(j$Uynb(WU;9$#@QYGbm};#%tW0E&NqGoaX=nnO$d#z3(fHM5rbO@d-qYBnwP8wSP2sCl&1ZypqvrxqY9t)``ZBca%z+Ez>bzC!Ubs!dD%9z*d5>NhR*-M!-9@AMT{=6F!-P5nt$n#N%)rEwU0X*f2OW^fp*890`eW^@?a89DZqW+E$fahMk_4)aB^g__QkI@c7dx!8o7kD890kL*lU>#Q^XR-Bt^Co5I!LT;Mk;?%n2;^bn~Cgdi(UNNdO*_pA5@wdhJcVf!5j-}WNn&PF@1oBeya_V97a&j1TKRJxNk{VB5NnS%W$ZN=JQ!IjdkZO<*lCRMeU!}&AuaYlO_meM?FH#SaFOsiN6UbM{$<$-yWb#dFBKaoyR*K!Bo}ng^&yZJBSCChehtL!cr7k58B@d%6Cl4c!qK1)2k;hS2lE;yC>Kd|6o<dzqo<g4P&^Oa*ivLQn8Ps*u2=Y4eUg|;eUh-w?HS%Th?G$U>-1JATH2<&vJ#Okh^^RZr*Z(Z{|NP~@KUH-6Wpqlc|Nd~Xb#o_m_Ds2%|3hB#xT?2(+J6DI#?Hz'

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
