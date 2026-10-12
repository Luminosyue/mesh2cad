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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_006.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_006.stl', 'source_sha256': 'aa070564a66d6116b425c9fa435a8257d29e6bfceee391f85139c56d4cb46254', 'input_faces': 1352, 'input_vertices': 778, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27186304330825806, -0.06524032354354858, -0.09019896388053894], [-0.009271237067878246, 0.49867260456085205, 0.011662472039461136]]}
GEOMETRY_BASE85 = 'c$}r31#}ci7w>xpcX!#rVF_-*8(9_>3l5tAg9L&sfdq%J&BEfE;2|)9;1Jxcad%jP56)tX+rskt*8NxLZt|V;&U<|4p8LPQx?NpeRb4I9o6oOdqQsdM{+Cbjzm;oe-v)|8mRiZI3=9nE-=j-lXvsc(hd7k<g3~|gBbu~o?AOkr3{-{{=^7Z?C8S6dSCMMne2e(FigXJO=^xUmPsiYpu7Sksb?O}&Xz<XWPJIK7xM-zHzCNyU#e7_0uK&k>DUBwm<-48ROKsV9ekFPBu)dVMH(h7u1^-?qd{2MjUA>z!PdawB@Rf&)?K~m%n6LG$A+NS?FY3|Ub(s&!E%Mx{D~j#3BvqI%85b+!&mESN*IQO*?*H==;a6o4+*{Fy`QUV`M0_RXViB(|%)Id~v0r76e~f5nL=NU%R*QD4Tbhb;Z=Wp82Ug_$9nltv_B&EAFZ_0`$ahy<A<AncWj^7G;O<Qo`M5s6IV*UB0)l(mBo@czihRwyT_@2#J#fF+k1NY_=I<|w<5hnhEy}$m9x^XCPaLn7<21MD$tC7%W^g|wkK*<Ro@E|1cAdH3JS|Q$pEE(^xyw`+`|<vKfcb)~g1ah&MT_zbyO~$Zx6a&eYRo$3m1YX=!Z<3QmNGB2LbO{u@Q{yh(mdujLPfi^6zxU7xvtM;-mJ42FLiVn_v@ZX%xlE)d|NccBYc`kmi>Btd0y!UM=>v6l*jd5MxI}BLCkM&5cTSq5BklH%uhQ-JJb>}Yb|`iI?+yjR<!6>uil*b&cWP|4LzbguJquuH;VSCI4{&!b(xpR${h1q|4@~Aj#b<bAv({WiKUp&n8WSMuwV3tt5q@P!3RaX`aF*qFL#5y%=`QCJX_!u<E2*0jqy4u>UUq*Bj&YxeOBfj>WS?=n9r`@B+Oe>72JjSuciBPM)1r@#PNFu%oXkTCVIvEN;U5P9(=xgZargOV?zv|e>vFupJ4unL&RFHhvIlW6^}4~a9<p+C-@<+C!ba`pB1ypJfF2pOPQ}IDca%2{MRo}WL`PPQcJ&`)R;${5aXp_KDeiKW9~CW9Iw8T*A1mqAoFg`#qp}>H`fq9<}>z)cDv<#ZrO-=K$WHDarAVm!aQlqW#;*#=FGzU(M!=j56*YbxzuOO^DzFrDB?XXc+1KQYf|2+zt@ZWw&$5=&mBcvx#Yi5^jq$2%-zivnDdnkYnTTOoKIZ6>m%}Ac_W!?fuer(@F1Mu!<ml`5%qYtE@kdJh<V@Tb47l|-!_T%ehy&n+fQ(<Lr%f<FEyFpOS(kxbBi{J_Ma-ve9X?pf<Nmj^4+hqF`qM29GA=QJdaPol*}();r4$WB+gT%@Uvsw{`{hT_p2MCoo>%V=Jj{Z6#3Uras4^(Ft74V>{n@#j@#en7W4VZX9@l>coUDy71VQXsc2`}O`_lQw)?>sM2r4uxNftkr{7NI$FnUG`@K_H9IujRIdiplj5w|zn~HJqR)|J^K~aw@QzP!T-zPEORoEl;o3x48uRHHV=1GHAi1F3xb9*vs%ug!wL_Nn(@^z#55ayZd2<{0>CAe}qka_;g-2VseiT1muw8wsPi1v8yG~(m>sTK1{1tZMk8_&@{y0TXEzvpu!=6;F9@p{($D8|b>@Mq>ngTh5SF@N-WzRXu|7WH_m<k%wkmEz2UdWiX;WxFr>(|gLr+<RGY_m7>qo~R6HXPB6`>d9iF9?zDP%&#98T%S2u^uIf`gL(NmV%%MrSMfY~lT{-B^mQJ`w~vns?@A@cML)M$^p8^Z5%Z_5c>ZACx>ny|{%F>8^LeKny2d=H5szc_TcRGl%^BuH?=Bbli3ad><J~Fd)jVRqZk$K1MhBT+pEFJD7wdqhh|WCuBayG>X~yS;x}CXCqe#oV3fsaw_leb_9yOfnZ?}QD5+TN2$2y>wk7d5Dzvv%j^mD$yXuJ&j-6oD#lj~2#>C7`f5c5huznsS<!(`@l?}+&z*B^D=MCKbD;ylt;SK@V`$po~&Y?Nhw#%Rn_ADU*~uXoM>?6+d1`TSDux|z3jt`YOiw;ZnzBRewhT~-{I>vAnozvtg}XlD{}zPM^u<$2P~4?I|$UveFY=Yva&{?wj~5dEp0_=WkW05R?w=9?!=MdsUXh<fC@p)D`QTx+#b^z*P4e4n*1Kk6wa&M)ofY+FS=uQD?azqQglj-KA>m^UvbxEis6=YQviM+C3kk=M^>&tffniz50#d)iOT6K&x==FJ1v3V!7cUypL!V&1>IIKSk2qHepve14@^F<xCFczoYpW$vykt~(mmhj^YprRX2!UTU5{X)hu_C(qA-mONfH4>P}-S#WiCAn*75cIGp7iT;%9yi#->^A}a;h<sdkJcnbM4<FC#e5co9e!3Q|WWIWvxb7%exAm~4%roa$CgyXNNPaH4FrRtSDWZSWrmgw9JYfd&ABT(n*W)sC`-?@OpI?i9R*To>^X~WY7?;7~xV%LQasPZA#k}<y-tU9+d|ro+V7~ILs9(!lSG3bLX%O1Kobv<Dih4AyH}gj+#Cf6Ox~clLXYLcq{eyKzz3Yd19`X6^tMa-ruRing(PF*Q@75Ik<~>n``TixmPGUXx<SWBG?+6~>xy?jBs9$`TU#uqbJ-Cjzrn#8o`Xc9pr{oWodbCp4cwJhagL&*eG2gtm+ll&JQE8dqtIX#`*^4|+vZcVh9Vy1wjqAJe+t<UwpDZBq-MzAJw(yE$xu36f;c>tAoO#|Fd>-MvcD;GXyit_M_h$0p^ZL<s=BckTFT8@+?Lt?X|5bmvWu6Q>%Y51ezOTS_LECnUdF|#)&F8f~d?WLryLtV@^~GCm74s3n%PsRHb_w&P#g>`Rch{3e%yVuK$K@T$>yKL0!@OH4U$1NOI-@TRL;vLC`xbeBBDvOig?awO^U)>6I_w&^gO9gqPv-x<74321y!Ji|V&1>2Xuk{RixSj@dH6@}H=Hl7C2s7O?++EM=iW*!F<uSD`sp3T*DsG>W9A<Qiv4>1d7aT-lw|&DtLRS;?g!KqMVXI@=5fb5?|P7wdHtJ$>+<>%_1_`EuaAwf^xO2;%s<y&WuCWcbuaTOC3w8BetOz2JY=5#a-C88&0+q$gUEMdeb)0m*Tr%8mf0uT)AlAm&o+3<eBKAam7dAwitVr5Xa46MU9@NQO@7YmyM=jdkNu)OQ4RR{zRyDDOR94{zsHH^8u!rI%sb2z+%@PBKj&?mz<hCcuK(sbey+bhg!!w#M82o+g(x#u!WWDEx_)r+b5ojLoS(R~$ajAX_n5g7a)|evrwKpD`Ilw>rLd^SbE2Dg9`%M6=Xx5%@qU-|7SGYz+>Fe7CFOoQpNgMHHz~}c?}_$nry5Kb`(4UhS>IOFug^Tn{Z`@0UcrrNB=XZ7TPWfjx0yGO=6<+TILg8cED`(FKG)>;8ySx??^%xPAJmQCSMAv%xb}EHw;%hJTq$&s`{(f0n1s0Ab&JQs(SFyutxFQ(o_8A-TJ~H02G0ju{gQuI|KQ9A%>CoOv4nZ{EZokUfpaXp&>*g7K|y|xxXi=#cW=+fyEtTl$d3!>{70BS7+=rHv7Fy`5%;H0AotH|ALgZR@x1L7B%b44jnZ;GpZo+@7d{j1cjvjYNAP{0b#p&Uu089_`AZfqO^9o$?nYVak@MtC+2sjw@0MNjEcIk+Ec#8e*AK4S>ep&+wDhyL$wlVd=ka{|F;2{9E$cDfZ^e8(A0~X{_ohqMFrWT~`A;+W{YSHT%#%OeV>y4H&*b|3vT*;*T{7Rym29g8S6XD^_esk`IsaOm;OgruBHxq059c@B$^H4^mYC<>AwM&(`kvdLu?N3@n^*+nvY*Fs+wXiIJK^?j!T)I`@?BH5&$jSZ*Ll9xY0me<e#@Aj%&eQwcWrVE^M2uczN0@S*E(e9{_!4LmJruwOo_DAgYnfeTwjq8SIhOBZQ+UMig8qKTkDVKGp+S&)AAe?{Ug_bjT4#Y3E}=s*^}RA-wWe<BErNt>T;d0GHf@-ORQH)&gRoZJt+g3r;X+Q#ChS_7r^z0P2+xua*OrKo3TFUXYD5H@lM*m(9E?_n?*hDxXJv!?qGh-KiZ2q&TBp0%Uy!cuE_O_;OmQ0>n`)sb4B|-xURYK?%!qZe>s12Z7K7^<G6mT1IqqZT+fmGqJFjT1q;`T73KNdU<%LwsQSzw9p?Frbwi(CeV1jPVEu88Da-j&Q}Vim^GH=np#I-1^Gb5L&dBxQJC5}sp3C`Ds^7|lxc7a{S(g1`eel}qm)y10TEBL=wsl^O$;tKq6UqHH`gx><x99r}&&x;r9zJIZu4i(2K3-gB)kmLqay^52d{6lE`}3cM3$CS`&i#+;oxZUb=Lgib_H&xII|T1sRLlpZXzN*Kt|d;x>%;U1{Jh|QhV!%35&PBm{TprJKlb7J8<*wle(2^MmhnYDNN!&T>|Cw`@%7l&0XvuLKs>jt1K;tP*81)1fa{MIoIiOxk5`@Ze7(CnXuEk{$?KZr_UoFR%j;TvJ+|wboy+T5d_A`7nw{&m`t8>>&+R;1|K%0CMf(G8dMrHKD?Z*WuX!HUUc61zW4~Vl|L%Ut#^dj2B)8u$*?9c@lH9NTe#yqatKW9Nq)hL}{GcDN+hz9hec;Bnmi@-}&yDT;{(f4CE25oAZi)MRPm>82u0<|cln{4q9XDBUZ&N;R;x=Cv^(RI>;Ofsyu8QMD{q7V6n77#@@>SIT9pA$BORgN7FY3{4`I0N!IA6V!lljS#H$?ku%@+6J>V=nU&Fy!)vMx=Cs~P8w6#ahcCcj^~{`tD7=jD!J7QV4B*Wb1Z-_IO5!M_u>Nq1AUGuks=%+GQB+^@g>OXMrDhdP_N7W#|G_Y@p2&TH?08k~RbGWP@8Y3Eu7Zf87SGK%}zo)4~MLVlZD{5!z9*Vnn<uKXhSv7xb+aqoXMOpIg3!Tg@J=MHXvOi)izUcZ_pU(b1t=Uc9P%=iBHm&n6>i09h^u8H#<^TG8z3BND-p;Vm6uMx1!%yq>_wBIZFzQ=sN2LH|d{Jw=I+CTRW|9&6(QS^@z%I%k2UDJvCVIXtYom+zI$-0St(9=~LEw%^OKBlzHPdnE)^L&$B4fEsUvgJ#zVSZ}aW4NAYD@FU2==<)PCa!1AdrQpEFJHn%|NlA#$CZ-%|5Kr6!vE>R`K`AwPckJ$Z1+4b*T17XkMEG?eYiiFD=SNh_Pa1o>|DXTisy2CpVS*|=Gv*^;<$8MJ(6pfZ))DN{JlnpVSKzjYlYP`ab;gAalD=e$9Ua1z`rM}nRAKxpkTj}>#0;Rj@nb^-jD4$f7B5^FE9@!SE3?#+;f5JxmTNy%YCg2UyoAc<a*9d#d*=Nt;hq{X1KY3LU{g2uHN~?^$)_l`c+?LIgj!W5bJ>QWQX8-{`TAtsf%jD-<rYSH!SWe`a!!@dVo0I^+WhM<ImmVJaXeaa^>pH{AHBrXC*0f<xLmfZzk?f<xzNOO%qqAL<{c9UR>O_d!PAne#RQy&uFLQYT7(}Tm_h`y)$zAi%#eH|Csw<a;?d6UY{{8o=yCnjT#on^HUq#RpbpjE$%~=7H`oH2S?R3ac%Po(N2Aj53h&!bbikv*UuNTd_=uXHZp(OjO)o>yuYYNZ?e)dZz~rXBieJVG}qrM51;R2gZOz0TsgYT($C&($(f%%BI?%$M2!~ncH}3%Pw$zN+jDtdUokG=TJQm$hxxeQB-hu?=6Q?$^c;K7^{m}!8Atb`fB3$yZx=BxD%vl(y6!z+r>ZblQs3eFll;r)-PiJC&0JYCP#mvXH!t7Erb2$XJ>q!v{O=bf#I^R0Nn*eA@jP0G=bQTZ`J#ll`%6BN@2bC@>v=Yu`$ySXj_30#Zhwk;JYK7(h;`3ZErQ$m&WEqF(=zb5R|U_y%{ne=2Qwdij_dC|v$fc6a%J9cl@(ln+~8rtcPqpDy}HuU&#F5w*K;{DpYQuC3^a4?>2c-*_&X~FTpj&Nv`4|ZXXko)UiTzd<_B5U$?rJUNu}ine*P{I!28XWQ9P&UEx?mJwp>qLyC3uO*~LhnCn;WzG;^iVUY`Gw&$_eRd|oKi`-|(Q{`Df)U$i#&=gLK5-P0sLhU+Qjq2%&<s$m{_YwZ<WOE%xS4oe=q*Rl?~mn`6Vyc2o9QzJTw`2cQTpVbkwnD?#6{gZi8keO=>e&zeIOQ*zmxg@_*#IkP3^Qdw>AFyugX{Yn?rZ33z=j`SnQJ>`Nr&;EYc6$Kxz=@(g-U?}EiuObVa(h3G=X(D8r<WL?Yn?fNL9WZ@aa1Qa=lnd+x&GWilg(Va*NE#snu_0Rfy?#EqmGMCh^yn)h;`nRtqRu@d64@#tWRID|6|2?zeyu`eTdyTL*!*B!W`?8ekdS1A@0@^i~DMC+1z|wZ?^DtM;RgRH#{x)`zd|=K+FA}x;qiKGev*SPa8a>rkRg^z}LaN+z+l<|MGohy@A}H3tMt~Zhl}MGltiV^}gKyl8+4FewNoMaAo0tJP)7YerD?n=KDMI{pU13FXH*;4}2ZR`J(jja{bwz+@9l&#C?~#{s!~EoP2#5K4;2a6IXh-5!`*}FY*4$CAnPRs;7!hh$~Z;@$U$=;+WU<vCJQD=TrRtFXlHM-+vBt7QX!s<`pV(KQA6L#=_Ode4iP5LiC&a*(Pp(sy>$SQWnN6GoO#j7$1Hv@SDN;SXbRs*LxD;T39P_AFKZ|lI!W#j{7a-keG+=OF`V8d=*9icpkY#ze%oF{)78-UncRquSzc0Lp9oy5ZAL06#I4O!S5l#*DdR(x1%5Lx1xjR+nY>d#dea9kFZ?FCD)%Fv0TU1-MP8`v%9(f3tklWU22k?oR4+GRihxc)5i6w10qB_zb57VX6?cKFmS<SGuJz;;q%nvC*J3Hf<E&5MXV>v#%i7fdHI^6e(mFHzWx-*%KhIY?I2O#$vA!v&UTskOZV?$T%Mic?-vJ$aeJ!7^0<Jj)wl6{KAV%@+dSN{)O^0X@3&Z(5ZAVL73+-q_A+iy+;6<T1%yvCb3MmGK3=T1`Y-diJ%9Yb{p?#uJV$#ZZ*tmloswKHI+^cFah-Bqo3Ye<9=T$tE=-8){v|~_^<GoCp6FpbUU3I_{r?|aeK&Ba`8-mpOk0o;*E<&#=bfirYi|Gh)!hI8yb$MwvZw{;*Bi?Dz7s^g<VvCuf_qYY5a)$AI^lfD?fI^I)j7Y&Ek0lRom-F)SLQqw{oq}fj_Vmy*RoE=^LbhMyudo?e*KZ(dzEU%<F&)xUhF^YHh+(9TTc}I1oJ4Y^RKJ&dGu~7f7c$olj~WrTyTBk3x3WXq;Y;g7QX+N+*ZH$-)GEMSFyGqTtDuzv|pR_h~NK>-p2J`eA`dV)7*DCf5Tp$C%(A<0oQ(uw9GempqIJ(0Y68KZ6Tif)EaTzp6Z!-{TXpbtUn648a~Rh{z$Iezie55v@w^sJ+H!fJulOc-}h!a%ln-YD)y@$=IgkgmAO)~q2>A*&l{xYd5i0#>U)Um|5SqSy9%D@ZQ<4GiE+_OCFbwC!L<vSt<THg^8E5{-tI|=t5Ls%Te$5$Fuwl9^(^;qE^R;eTkpx1`%lT0O{XmPpPr+8Isfwqu4m+|!4@90me-%jXZd>ua4r8$%l*Hd%lm)H)dmj)cl}%0lMvSy*Nrf9{mXF6^TKx=&kK6`-ORDh>#f>EC&-_t5cd!6c00J8<!|%xj{a?wnJeo9c|9+lYKobwZ$kxlRmnKf!aw!r{yE=ck)@tm%ebCXy&^67+4l2w<m@BCU9vqLHgi9`@`*{14|b0=b3OY~zCVe{9g`4OHbskkPxMyaukC&&p3fP=`P1smG;_I5Y8z@SFmt`oO@99UYnG*cefk^b^?HuC)L*$6-<K8~VBz{`e!f$4YSCt{dE0ZotsXfp>Q{dMAD^F}-&1)P_gHAz?+jd*xAo-jWMn;fE>PyATbvMAFO;2V;kf_Qa&%vmAU}0+vYE^KE>ERf(Ft*H`L9#WT#k#&H-jf3?um?yu+)S52YqFPCn2tGofU4W$2Pv&{}|u+dgSw+vwU<y+?%ZRbW8oXzg6G8iB5=n)aBOW#dDME%!Ne>aSiWJlrb(|7j4%;clzYaZPzvTwdMTXknOr0&u!ObSG81v+wV8r$HsAg?0;stAFy+IKcJ-wWp2CglH7jZrPQv(_d)ji8F2gkiC!z=e97(kp5*VM%=1UyciFkT@AA%h!QWNc?gQ;S{ywnS6RyX0pX|+Zh}&zs5A^&G?pidL>$lzaO8(t_Z{a>s=6NpftL<FgS1S`5^LcN(Z<pMD->&KzxIMP#GH*Wz*Kd2i_>SZG!dv$N{|;t<o|4@DJOyrlp3>f3;(Xh4kmUB~AT8U8`3apDo}nw}o6leQ{AK6z`Ae@*hwEuGnxB`q&*$sZ!?J>_1zuR5AN4^cIN$c(AfDUa8|c4e<m0kE=SpsW&ebHhJ?GlFe9rZ>*va2n*q_I3Tt1Jxat@6&pBM7_=&l;f-1h!Na{K!e^<)pux4ob71ayrwpGWcUyKeh(zU}>(w_iEI?eE|8@S>b=d#@t7{k@7Nx$V7*oy+$sTDC8I9@yR^X^r>IGoN4a??cYd<b2zEGw(TY+j}!Rm+#G7uP4m2%v;P8wRKO<x4qYu-2PrypVN}tX?ssAx&1w@>sk%ww)c&a+ut{OuQIp4Z?tpyzR{JZ7`Mmvo>M=ao%3z)ZzZ?Czx7CNdw(0xZSQYg84_9gGyc7C*$=#b+k0Bi<$cU;?{(FnUHp7+dygH@ZSS%51sd05``tm`^+9~EYX7~%-T1ZO_V@g%<hJ+xo*T~uxBpHdx&3zv4cz`ag`LMgr^xzkzf*k2@!a9wK8)+J{hs2v+L!ZfzgtQE-S1XG&-wQ^+wWzP+kY=}uZ-jGo@~FzX(vw2Hjlgfy-y9>&D{38k|MeNccr!sxjnYux$Ip2&gCAeayxCmyGd^U-OVNQZNIzOx%}PD+vyF@3)}C5o=o@ncOl#Fq4C`IduTi#-Ijl6_fF*NQ;k0axBnihS7&bjJ=8U`Ds$WKwtAgde(!#81dq$@8od64+kY>X-2Qv9dT}}5588f@mfZe(w5NP3&bR&EtrfjL!#p44@9*l>i+mqv`~BU0H;nIRKOg4)oKsEw4yCND#@zNhyP77q;A)ksd>tQr2;UPjxBp)6X*6EkU)aAZi021q^M2bD66dcQ-2T0R<o53klpCWW%*Px5Jwt=koNxP%LUQ|e6z-l5&bNI>A-VlK3U}fq{JdrRu0!+h!0-D{@q0P%_yzplyKjkb%Xy0SsC6=OzU?~}eQ|%jKHI)ykz6mFSLCbr7V-CK;P&rZ>|B1|BDwuL7CV>Uv3RcdGB0^o?ANPZ=j&j)FXFmq|DH!LF+gzp_ehf4zem#c1T(jN*W_xOiR-t29|iv1_fgx=i04lGcTMrU!d33iOu_to2>#voPBtF@y%YF%-#gj3{NBm?`;@7camT#!G=0bSaklTu;`zB?{w^*hKi?_g-YJ&z8sDcW7mxGrY~eF_y={1%&+`k+?cbrrbK7@lp04l3x@-R~PIB$g3eisYXBWR`dopw)x6}Hao}J6@^y0bgJ3Tv>-{~nsK1>kY_T8Z5_U{JOsQLU{W&8fn(>w8abHB;&9_?Iy_vl{xe4MDy_T6JVw|)1hZiwRVO>Ey=YIB<jZvW2nJC5%>CAWX)Y3K4gPkr~>KZUn_cPhF4yHmZu=+Tz>gZk}Ue%I<g`S}kEr+WM>f33-t`o%$SP5Mvv6eWd{S?Siv^rxD<H91ZCg#T1ikMjRlf2yfWxe8_f|Nd4}%0qOlh8;2N5d0a#p1~i1?FYMxJel)1^xr6x`X%B-4%UA||BdakffGyV;8<$%l=A~Pu^jNkN&jHlj&vRv>9X)ep^GBUVT!B5=Y`ITI0dXI@|}ojzfR=IoE+d!Q6_a(Y?l@JayyF4z)0tYf2FW~g>9dj;;#z(E6`UEpN74{J`W>)27Sep^A!9b_+gCaL6bg=9J!AZ@CTt!K<`n$^%ot-Ym8+cjAu45hv6R?{;|UTIP_!av+(<%&q5!C-wk~f`WXCP=wr~=;157wgMJQw3i=kxUcf(xzJa=K!C!;Ej(y*NKL&jhZM_bE6#5?=+fDeh&|lCO|G+;+ZUIAQFf5Z{`Jf9RCjCia|3P7$4qWD@LzxSjxC_1*jP#H21)z(;mxK2)tUPo9#IlTdHN;YruL$o0O;*w{U$By3)!==>N<;fXS3!<1bQSPYhE+yf3OQB4N+G8(d=cov(3#=0Kxc;jS7HBIVNFK*0sKSg2hf)di&N;&<gk8-Sn~UZ{RMvClp6<r68<9mUFiGJe?fmhOm-VNq~9U_0DTv8AgzPr4~XBPocLSlx7hYJv={!pNmG7$2Q!LEdy#VoM*1U+bVlS;F6ob8vY#_z9LN_m>GX)n=QouV#CVb~Vbb{#r^oTin0#?~mr18ZTmq~TJk9kA&@RNXtODj!39xF2rLKgWQpl-{xERidYKY5WZc$%QAKZif7jx+z^d0C6@OO|W<4dr6*zP3CE<s<y+`9}-Ip<K%1>~HAK96xe2Yw#fi~Mt#XSY#y67hL3FEsUQI`rKq%vYN4pD_O@{*0J-Cgc&Lb1f6jw?fcaaBdcYE&%NVFW0}4h>MuY<oZz(ypvIHbHh5oQydIUzKyA@8H{vYSaan3gfe11Q4ej`+ps=heZXZo#iL-PBjEc%_e0zpx|?A$Ol32`NOy+yLw+li5o-%gtN~)uKSL9%g;<u89ta~H0Ix!;h-*PtHLRhjtRWcb>M#}g)lf#P3N*2rh-EqHIxy0;;cGzGKwQ%l*MrqCjZqDZ&ri@bF=q8pF561`8HeK^XzJf_@NJ=kF@7{|8x4y#Y$^Oa=(UDzH7o{x1#}e3=D^25k3rdF_&Ly_DEl3LGIS4=4Tt|7x);jA;D<vGM%ifiFzAUWn+87`IvQp3;HN?FFl;@Jdp+_<#~QXBZQqV#BRwBwW8kBpC!s79ehjpRvL5iE(0`z;7km%ssVEx^-wWD<vWf76q1U4<8h#=)&4)mR=R_dlU{hQhMq18E(hXsx17M`(xkGv!jPwi`X*!QbK?fra1WRF94#N_|Q=Au?d?`~|CK%~rupG!Kh5WMM6#K#xt89v;CSM7@qG9Dtae4T%C?hKYUIK9$__EL?;D3ZK1YH)o4BD6haaqKLV8nAn=f<`_LKlS3ZqjKHXMoNPofL6e==9Lpke>~4dKl%T1gF>qBb^gIC3H&UJD|xYGb}UWWTw2#(B$*LQ+YbWvLH@pDkGK}o_JAgPvxc2rlRmUp(_|x80CdgM*0UF4>2FaQWrLDmkrzefU+Vm(j^t14?f5*2~Dg7@=8LJFAtO36+pd3kW&D<AjY8pctPmw$d@`B;&kY@<mjJt(8Ltz<j{$blN_4<IiV9lCqYgkXkuxglR&3JP7;$QpAkM6bQ);M@*7qhJU<v&KIG>^TpUI@<-m($OpAk+HpQi3<uDdxzUb$2(8ThfF4`_DG_fp*^Wa#rg2^^z1<wdg?J9=4%R$pVGNDW!UnZ0}p@}DkcB20iLpz`qjGY6Td<v8$g_ewBI;Ux#&{{xqB`?Z|Z!m1UVY3Wd1}z!I!=TBxLmtIlVB^8bS{POzdKltg5Z6b3JFxmFZ(@oY!4qq0ikpJ@LpR1YRPF~&tTkfN9ifSJMNE1SG_j$GNl$?$HXSkPncx&JLM-(Z<o<~qDqD<rCUO=-6YGzCFNFRR`cLEyg6@cZ?vL_Kh@~dK2DT8}(!SP#ErMSRwh8eTXkyC|uS5QF=#}6UM<QO1oJeRo=5WM|5J!TogdTx-DD)D<;m|8l7LM(^B9GVr=&l&E0npu{TVss7LzAC?vLVpK+9Q^_JGL8wI0#1iR~YF=u=dDriZWvU&`qI(5Qm`NAn*|AzJ`rO?2kAEY=}uuK)e8&*hu)k&<haHh8_vM8u0??xu|1-NzX<941gX1zr>_hBPLJh{$}{q*pDpR480lSDDyTzliy-0BRvc`v!TiV2AhpzX@R&U^e|IQ-VHwz+8<?Z*huu1KVs5NP*+RvCeT~Z&Q0*Mp!-92fhJGuNJqqeFygfCY*YBYeii&u=&dMQ0lx}*m%`5m+u%1s??l;F_-)YJQMML-D>S`NrFX4~9qgY#labC2{~t6N>0Izh9jwVn=Y&rJofA3@{2PUJ8fXXnBj^`s6J2<oqb;P9VVf`5-T|Eo`$z_#20As`lnOp4baEU+YWQ5x3XVBBe0J!cjSFUN!`?aAQ|u2$zOJc^^b-fiQj@<8-_@{w$n!@m%j(1GB8SSxL)VA@1)g{mH2IaLvSF}(;KSf2A~ysv*>J-qL5Cooh<H0}C30w=fyj$O90K+ebO>|<Xz~qFZwNH8JC1L>A?hdg7dTmC@WzPuqKtC(BA2$A4?Q28*e1l}Z$pz^GHeg@ZN#J}W82AyDQ77B4Cu*-X&dV6J%}3_x)fsK6wg3eDQNQ1$eoCMvW<o<hn|Qy8u<larI15*!?26+6hDUF2)z(7<>ZE5h<cWT<$#Zbj&*RH8@Z8StHH@fLz6Gy{KosCEEbwr2y`rTE5u|ykx$wWF_pIiYX>gNYtXqt=ODBn@_&YIhu9BBxo*_!2TiONH2F5B95>q224n1o4aK;-;iIu_C*-z)ro5k^Ye6?dOg0laGZ8O>?*-iqS~7|UKo3ApfMLOin;{+m(+oQT9gKJp;tj9?$Qg*79)^v8mW<*_D5JOqd;qkDm~y5Xwi0>-;z?jHp*8p;@WgLH-vYk{p3cdd{1N!y4Ex>5x;0{1mI;;)IaEg~#Ho-^I=NxZ5T`=i8f+kRYv}3F<YTeF*3iUOn|Lht8w-9An*4cF*?w3o_<r~^@Rtqy2l_B#S#}3@9yte*a~}I#hxj1k!(gkR4?`b-CVvk5IBe4AP(S&7PWrzlVZ8>iEV~Umhnxe*IfwmBLwo@78n9N-YoL2WlOKV7tbry=Ygk5<r#0n_z<x)dJgX_53mXA`*q9IN9jr4V&WbYP9tY=BybRt2?LtgBr%^BQ>)78iQ(j4MivNZuw#^i8gAtzzPVou&nb0p$b^>gViIaZ>zZIIwXMml6-U_|}G5ImjWF?S8x*B3CuK`vAT$WS3!@-(7<<B+zI0wh4931a}g(HXb5X9r4iBWy0ps!+k$*!WVLPmTavFhYl>Z{17@~y}ri@~;Ap(UgE8uT^fkgsLbQPat~u#;obr;&3Sd6e@2IoD9%1C+gnmh3h1@*9@j$?<;<j!9ofO!^FBsb8ZW^0aMX)Ir;JfbQV@R)0&xWFrlmWmr$dvryjOl+z!1g%S6JCO;H@7IZC?Nj(&OH5PgU;-MzC7<?$|SqvjR1bPT^i1k3+1LHdcree+w0avlj5X{pt&^1s`d(_bbx)6@F1>%v2rEZVys5~Fy_R!g&v!NdHuN>cWKEz)zcBF}Yfqn&k2Ko%fv=Fwt4|@eJ`*bG!2I%VOU#WK@cPHj0X_})uac-T4mgnV8oNweKpi5$VsxJa%C80Ya#{(S!9f6!6aAKsJA|`8%ZCfK&;p;#*g_exsn$R_oL!R!LYC$(cOu9O9sw1YH`pBt?`szcIZ-KHFh?`>D8mOlRVyed<<^7>snBt~5R=RHd4z?b#)cw&X{gLZIZXd8dsF!q@gYUD5O+?%W`4ge3ya#k2w8tN;1=tG1reK>Fh$n)DLEnTw4E+M}MC^}vGGko7qAaD8W75Qqg1>-XfgFnIdYl%T>TZQ?sk{|DmD6??4O?cI)5-cM>UW}?Yzf-F1o1NL?<hFMOC5ZFc?^0PYz%V7AfAePmVsZyHp`%CzsJBxD~QRzMBT?wkKEr%80nYDP44`roruR^n}Mb_4a9zuA}1;Glfj%A1L94Q(-e8hOmQ<9>4ETlq5C2p03+=OYl?aXAZ`Vp40<xQr}8O?r6#`$MtT}-fN9$)C|`}3?meeM%lp&G$dPTGjGTec0}-#ryt#?_8HRqOKBTpU&fN}<Z|87r=-S}qn?QGf?(X2ViQ;g_w{=S9Q29cXbuel2bPq#*m0`J{`y!TQKRDSIBBwiY7GnQx5qC%27pxU@U+55M^0C-QU+A{jwiS3R_C-cI2iidKQg~vKrg#A?mx)t+0X`D?tYJ@~BN1PK5x-~HHEe$Yn*3Xoy+wQv`ETJrLz7RIh&6c!H2Fu!d4zf;PlB>!(2~)8GTj$Dp^2qHSu*J4h{;}}ZemU_^6#9yeR61G^o&FI`4rQ$&u!>;;B>$L1u<>+1$i>(I_ms@Jj(fi9ExwE><RQ4Q%pW_BDN3Mmdfv-><;RY`IMIw`N^T_9ndQ$>qLl2zrr?2k(V6(ln8M$_!Q9ZoxE)#=tST*z=_HCP^9l8mij%$|0(om*n5oUMdUq2eaF!5SI|%3>HXg(C%=cB1U3;d>5Yh`K4z+K6Y8PuN+Tv)0lo=*h4b5c#?r8Y;H2q&N<oy<J3?agK4%d$v6+r<+vUWz1+i^TFnTXA&&lsDes_N3^N>%u8<0=_2sHUjrrh5#Z|1?TfZfD#tpKN(<~^OWbY7js7*U@`LKEAHoJY_l5R?A_n%3Q)u^!dNI@|>IGu9}&U!;4?nJ~JirRPz4R`#Hrp2umer*)p5@mnFLW7>~))B6^>Hqdo}uC;V6r1v*;jU9pO0^JkQyQyaAdm00J&sG<0qkFuCI7T{FdhhxR=8AmJOZoIJm)-+Y***uqFP86*_o0m5<v&4u0Ws;P@OPl!Bi@Jn+h7;KNWVpV0h;Ri7h0Bo1}9IyHIT07<UGm=aB^J7uy)V^h)K&FihqJ9M!FNWp>lu3VTSz*?T@&VDTm_m@Bz?2V;g_O!~<ag*zZr+?^EpiDf+4b%I=`whhbc(zv^S0x|-^4Yna=xa`0uKKRMXHfiDC7(ZRkfV&Y{{?uI7c20F1}UL)_UgFVF$p~>$um63KhIsOMau_-3M9Da>qv*6ESTUjRgF6ia(6Ts#nCL0Mp67gvGdC>E)%|_^r;2Y8Y%Z43?-iX}e&>K;{1$s8NosF3IpNO|0H<6QdB+9nHh<^a5_!0aE=<z5ceFL%7<kL9Wr*?kRDV!XCfPRGiByn>50dWejCeSIMn?sZDh`LgkbVuxqyvMM$(0?G7WxZe>k<%PG9kHJv#LW@^0X7Qy59nxU@;kAQKcLBW7<LrpJ4`t{vEQ92k2CBD;y6>;5oq$4;Nzh8!XJWOi<s=0VIQI65FbM9g<V1pmA!`k2>l;&D836L{VzO~(??!1mYV!0_y>l6f!qgRWW*jizvX>(vXOp>ZH^;{{1#~POQ65Pzkw%y75XapE%;N=e<3FS9Qrxh@do}Y^i^y}TE{jNYlu(5{zBcf|2be+5uXCnpfebj9&r}L8dxYa`CZT&w2peRfGsf2k#!D^^CBiq>>xB5=?uupf;KIIruu%wwt1oRqI|o-raPEbLQI<20_X^Avjw`6DgF`lR0fyjl~LDV!&gE4r<3E#U{@U9cx7x$>?AlD>Fr=tHV1kR_zA<dA&x^l2S$7>^jPFCM&2CMw-|aev}Bu+_t>!Ai0>iZ4EDE)Z^pL7?jqg{9S2WkzE0NU<KX)kHpt1k8)8{j5$21WV#uMG>MI6a6lIbXMIQOi(9awkQ_dj=$A9CP4&j)dL(Ahngq-3|E+gLE$+3@NU7))oCQUg$@KsG^Rbh|OXTgYRP6Q)Q=G;Sn4n|xBRuyw(KDMFq`PeoXeK#L{)d$BtAAW+VjQk?leAF`m^~n5jU=yIbqc6vq%DaFMLS5_O2SblWnbhRN;Rj>xuZNE?mF<SDH*t!O!$&|DF|0hwHzSrh963~80dWPiBOG(ABG?JcQ_|aT9+9qy_E$hX+rTS;kH$WUQ~3kz`#5wA;uz$SK55u&uq%jTz%oOV&jTF;T?F|tsQWdxy#jp&JP)>ya<C>}1irmt(+ukdO^kBaLX!`LjzTVN8;WhB;G1LnP-tRZp+lhq5tB7Qegnjf;9EimLQ6(*Z|L5poI!|tLyw34!?0oSy}=tncZT&wPG|UE;rAP+)47IN2P1vXRPQ;{HiMzb4~N&GN5P+m{tYqtF3@BLkTV?H9zgl8ru@cWU7)F~9`rAUHH4O|A#(g0I-Hpkef#48{<m`N?At(5$Wklc{?WG%##3ovNdF%AYXSBxt$$X)yk)FWSNtCt@N1ZazOh!E#{cL)DmzABL@WOXwImX0'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

MIN_TRIANGLE_ALTITUDE = 1e-7  # Original numeric coordinates; CAD kernel precision.

def build(force_independent=False):
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing_tolerance=max(1e-7,construction_scale*1e-7)
    sewing=BRepBuilderAPI_Sewing(sewing_tolerance,True,True,True,False)
    planar_faces=[]
    skipped=[]
    subtolerance=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        twice_area=np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))
        if twice_area<=1e-12:
            skipped.append(index)
            continue
        longest=max(np.linalg.norm(points[1]-points[0]),np.linalg.norm(points[2]-points[0]),np.linalg.norm(points[2]-points[1]))
        if twice_area/longest/construction_scale < MIN_TRIANGLE_ALTITUDE:
            subtolerance.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    if force_independent:
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    else:
        sewing.Perform()
        shape=cq.Shape.cast(sewing.SewedShape())
        representation='faceted_surface'
    if SOURCE_INFO['input_watertight'] and not subtolerance and not skipped and not force_independent:
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
    if not shape.isValid():
        # Sewing can split near-coincident source edges into sub-tolerance edges
        # after restoring the source scale. Preserve the original planar triangles
        # independently in that case, rather than altering the input geometry.
        shape=cq.Compound.makeCompound(planar_faces).scale(1/construction_scale).translate(tuple(center))
        representation='independent_faces'
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'subtolerance_faces_skipped':subtolerance,
                  'min_triangle_altitude_original_units':MIN_TRIANGLE_ALTITUDE,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':sewing_tolerance/construction_scale}

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
        if not report['step_reimport']['valid']:
            shape,metadata=build(force_independent=True)
            state=describe(shape)
            if not state['valid']: raise RuntimeError('Independent-face fallback is invalid')
            shape.exportBrep(str(out/(PART_NAME+'.brep')))
            shape.exportStep(str(out/(PART_NAME+'.step')))
            report.update(metadata);report['cad']=state
            reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
            report['step_reimport']=describe(reopened)
            if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid after independent-face fallback')
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
