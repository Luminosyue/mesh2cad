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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6ea331125ac747c1b8640dc80d90d4cd/part_009.stl', 'relative_path': '6ea331125ac747c1b8640dc80d90d4cd/part_009.stl', 'source_sha256': '0760e28c60219c8d250b6cca66ee88df5535c5281995ba4dd96d9736278593a1', 'input_faces': 1280, 'input_vertices': 710, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.05405792221426964, -0.48681381344795227, -0.0752493217587471], [0.2115047574043274, 0.4999997913837433, 0.07854147255420685]]}
GEOMETRY_BASE85 = 'c$}r2b$C=s*X>UlcXw+vxH|+IXK)x?8$xgm4gs3MC0K$b0XjeeL4vzAZUfBV1Z!Y$nPFaJkYR4`TI-~{Px#|L_s;k1XZ^CiqE4M%yXsWi+p1}z#F;hxmtPBcfAUlMdYUGYTFb1B4hS6C-#=hP=^?|$`Dp2tFaPNp(xP4SR-Jsb(b@#x-T@>01AVKTeQWlq>RZz6+h=It$iSXMdJGNh9Uy+go`XgNxcm|QdJYS4{av(5xw0kA6^fNKPc;8O{+H4<1n2lIn`*n%K4;rCQS*vA%a4j)It)MAIpu5bR;*Hf+cU~H?;53i=WXX=@h!G@Xdky1?Vk=>BfdRD+Re(pnh$>dlncbS2Gv)-^V2WNca+T$<>}j7Zozm`Hd5npTyCp;Yu;1Jw|DKL#$#{S9sczZ%C|l!6e7O!a3K2Gdg!XCZQ396ls{z_{MEZuds|~aj5AY|^3AO|&ShuSIJLgJ(OxSDKl_Vl<rj!U`(abypMJDX`5PYNz7}>?*VSI!QvI0ylW$Sut8xVXzzxCT+wzuDzO(9O<y*={uUC0^RYCdY&RcO`-z#8VX4FAH|DHyE8dO3aer^oEB**F8gmLC?3BT89+;6MmDnHh@?a+V!Wa_$(L7~XoUt^SSZ_yq8$Hoi2{Ofx#Ul$6gyjhEc!0$6qwRaBArN*y4Sc3lN6~K6YeT;ekco6qH<agEHZt0`iJ7bTa{jJ}xs61TBvO@I}eGz`!X~;vx(<;x-?N0bpGUK`{hpYOr6?lsNccwu;AKz2=WxnzW<2-i^^^oD5%D+8*;#k#hQHQ#&<I%9y>bmz+D&P6rEsQ7ny1HLSgM7-j7aNBBRJxBm=c^X$IbT}Qnrgl*6RM-1#TDWI9jw~hx-~#Q<1vrcv$@qgI`%h2Khxr_VEvU-d2nuP2R~#C+Sh8V?#pthAN=vTFrHU_QJ%j2Krh_yqV{SYZG|Srdd{PDX$s8a#u>;%lJn}i)-CN+9?aL~qyK9U;Wyf$+M6?m<G$(_R{dCf&FDX16Z)Te9oPNX5cOQ?8vIhzv3?z^uwLHYfL|z+YHw}(SlyQ`<}3Vpr_s--vh!6QcBS2_{MREf?~NQPpN?}G;ctjSo;%D^`PVk*QNDA~LDcQ4%vdj7$|&F5csSNkgcEg=xxDhNYn`~?!bMd6?QLqIpL|uYj{fPYu4_He2G@<;4Bv7yQsw`0d-z%Nqs}uH!v0oeAo?lWANxSgU$DOZ9E|I(|4m)jIi|YGzopqw_|FSs{F7dw{ireMC+~BN^TA3rFU~ztXrE#d^6;s?%CpV61?^AV#=5AV3G42k1Io7*9~!6f74a#ewuf(tYp;A;>F!}a^0kKHt37>3soL<5om}=K-_|K-q^EBVPW!|5@xEa^x^L{qy72yO<vYCl(S3`dy=FPBe9drQx^HXXeP6baSoq->kEQW(^xt(p=DlTU>{o&3;YXfF-FCjO_B~tii>QbBc04!J<y3WO+jax<QUL4MIr}@-^{F`A@7kVNFX=NcQSAqQML!clvF>)yM!l6wvQ7Pa?lacU&s4oRY9xc7Y69ww`;X;)3ivDYp#G=KQ_pex`7Fw}{I}RE|MC9C$?(^{S^gv6@_f48)7P@M#(bGCFZq#gDV}AGryoDRgKvla$k!4r^lGm~|B87u_OJVf{vCg<#5}I?9>4BuhVh$o&GDLdZ9z8p6JB7Q-Ycr+-L@i!^6h&9vA!DDTcp<4@%(6?d@$y*=BBkO&&3KW-&!dE`46ZSrsgZGIQltU6#GWquh=I)l|cKt4Y3alOts9*4;zN{&hvmJYkAD?oJ**~VkgviY=IRpo*TFEe5spH?KAerRdL;`cU60{e+Zsai>kr@_!pj!&8MtEUDUvJqX%&R&#CIrmaQJIn*nv$t(~e{d(-B)uB8~BQ%UB9dir+1lE_1{461I;XWF8l|Fy*Zh8@Rqs%}@b&t8k?980*$+p2C}{b)^I;`!Ubig9kR;lA?US9Pu(@yB?Q)x$W)x5D{$P;Xp!#1)=TUSXVt`l6qCQ{gYort;&gHyGEQRu}WzXS-eH;oDI7Uy`8zkbl*DSqG0oKS5t`t_bXl=gYa#xNbwNN6XE9sFQgU(7wxkjQ_!Etn2DQ@Y7?x+e4mV9~d_a{gkYX{Ulk0svoQGY>ekY2<kIegqjyexw-J;@Vqu#-l%a}Y6c@e_iN+1JY@3{PhUUJ+lSv(<F~#H_R7Dd{Ao2W_J#}4&-PcSpHoRyz1jALV*FRq@_8MIb9lfK_@jJKx5XQK`S$arkx!ogozud-^D{3k)=Py5<e^AejHljMH819e@Xfn5)Z5D%YW$9_>(Ec*1;|f@8Y<7){wQ4cKorKar!wj)%X;{uilCq7qg4L2ppEFKdryofbQba%z72k+>^wLAt*&eSX*>MH7{B%3#kgOeUFg5>E%<)Ta1LC$AMJftdp{rPYktA-gZnN2k#8Gu*6!)YKi_{YvE)a-C4JvDo__rPJn44Gk9^0MbZfn?t3PKA{m1);{<SF!vER-!jGw;6Fn;ZS6TS9l^W_7`+wEj{&d$7sed+cg<n2G~1C9?ZR(Sf(W2=zo{I}G)vqc<3`)p0o{>(qhcSfH;`^gQlzK-8e`?jseX|&f;<2n1&TkI#N&!PR>t=Kmn55jsWZ~=L%yajcVYZlILB`>0%@_A8*8(u|v`sRvwzF3Rw#J;!k3i`i?`mq&wggX3k75;skGc7s)#kqaMHRLCS1^1QdD%MfjTWDW;IL4pcp?vF^IIld|R{A5Kqwc`Jz6j$#UsmP8UhppZ37>)MCQGNTYq@(L?T3y+KZhP;J@$Hz_P@^L>(IgxUjCll=%>n4bzS@1zxdplg?<L_!0V=OACR9qOVNH=DDu$h6Z+{i2lusiHLm+d-tEfIzW%1_=dba2oqnl|@~yeB58F1^Q1@jCDvS1$i=wU~zN!3cwJL4L{4Ktr`ahjn^<)333fk{3j{WLYJLI{aAKGUu$$mPh@o3p<Dc|nIzGOSP0ndfE4KbeTIRD!o)j~b|)*AhPzJt7F+^^bOR&|8m9`$ek-xB0)P5`c(X)p4o-9-CcgK^zA50RhpYmm45qu|d7N4?#di99%L7|+zj@ISOt^JN_}1=sC}_gfqdqfsX{W}%;Qc<wl^ti$WCy6~+}kbf;xP_U<O?iF@l>705yJ$?I}<PVgdwC(Wf=bv`Uciz~zUDZS9`SACL;=Vct**$&pnboM1-@0O)QS_59QT;d^skW*1Hx}W#g=^nad8?a7jmI${9PNL)iShJ#7=yaqggiVd8mHRdc)!ilH~;saYOhrutM(Ji$6dVcU&=RU>w?$aoeuK8w&A{(R8jdizd4Eimo<HWb#YCdPpo;*!Y^JD`ApSmi>i|yzoY*T`BZ({Iyg3Y`p#~z)qOd_mM+A)xQ6Q<J9S;@?Fy>Bee8YYq0S@Jq3MpgU+aqpXm5BP>AvxKWc2mtk?tFxM@C<N9_haEd1UnU=TZE14bP(lzM+5P^T_C14C6OGkF+~~U_3qFWB)%<bi+|kzvvNFCtAs^s{WmRuP`rsy=JMp7VmG^-=Y1<`dGhJtKj{FEAQd^6~y|o-p9Ey(LbCoysos_9z=Tj*6kax?>)(a_aXayNBd{k$87b_srO6m%Y1gI@tDeDpHKQR!qd0^QVH$%Y*p=TUy>=`THt5g@6$m`z5J_9R9)Ft2dVbvlBv-D2E3nRUH5gdm*0IQ?#o_tk*9C{)E0I47~{8gON;h5Z(zOOX@vK0bC!TV&rj94Gsl-5p1!ruV(c>?tL^mk?L9s#KYpKST3Y$$N)51nlgFxk#u-#@hv#~?KllUdJ+>nJ`qQv}-=)QV@}LUGk9BIBTpQ~&eT^NS>(1FC=O#~IU%&SLcC5#`wa|Z>$2fnEIi}X5V?-T{|MLgTdsvnYp1yPXX^j8;Gu7S}RUg+)G1;r$>^B<0KiUlQXl;V`6_YnbKZ#4C{p(Mv-W&s3@9?ZcE%oO}Pv2hSPjy}E@=2)Aiyh#fuZs40img=r|JRv$dw_lTUSG8zTFZ7v|1Z1XzW!aU>dM@!C&sxh2=!^J5#s4PgV&*bP|zYT|9Tv*oBQDcuYN8@B0o>N;dvL*8|_cDL%r2_6zu88*YmVqSVt%OdaVns*j6t;{+zJ$td}4E9Bi9Kz0Ya>H~`nZTo=!mVvW@6FRSkm_+1X;`BLMnYOi$~j($qMP<5`Y!+LQxT*UEz!8%%cT)ppS8ygD0Z!pfWn`cLR`sO&)mGfy^)K$zf+}9I-<n6UT_Mbap@VnwX>{wlBou_Z^d<M^vuIo2?`qpD+<Y7!HRnNB6tI$uVAL{LBVZ7h&7m4;KN~!#q&mP^Z>c_qw<8Rjn<8QnG^>byT_kL0$se1ioOB9R#%kX^o44-%CzB9I%%BRC`Io5Bb?eL!+!2J&WbCIWS4}XS!x~^5vO>3WBXkWA=>Lf|5sw>O61IR-%)=5w(_9fFn+*f-u&S^ot@qFJ#{~^we=D$+oeD&op`Y%=m^E-A6_OX)3;J>JVeR$&+yx%zSIQ&<9UuAg%yf4)4B<ph_^8YaFLQmhhew^C(wAe&Dz5M!@ly9rnS6$a;IfH)ICh>Y7K=;j!@j6{I*H-5)=X|!`n+fa78HRJ(yNkHrX3?ns!}y#+_st<ctM<0VpSG&|9dH@r`5T`*Xcw~Myjt*gv@e0zarUnMs-DeluW=vv5A(IICEoX*eiPSChWB%vx2NLu{;J#X&pg7uk@_Xx*WDY3@n7Tla4h%R=l9@m8HD{ONB4D}zBBL%^1tpNp8GxT!#|!1;~zKx=g+2ppr0mvFwXD*)PK-3_(jgD`myXuw$amfemtP+)-o@Js!wa|OZfWv!IW;5r*H0D0Ch5C=0;E7{_YUYpN%`J{n^_575aI36#1-^1h4NNyg@&wKVn_H>xF$L{X6=6y%4i_nWwL>Bda}gs8@SGd>&yhG8FGW4`O@&=g24DSFzQ7&pdR+`a1D#p{H*xy&2D!8oBU(=7>+|XF+My)#ub|->@$IjO#wd`#H|Px2XHFMtwp19HVfq&fgmQe{!Fls^1}vRsOZC1s8ex=H5=6pBJ9Rxn+n+`St*uTkJQxsP${foe2HhK8gD}GG5)6wOV5Iv)LEpKav#BwczCFCll&fJF^I%7hFt(evX<@Kirq%{XEzQ9D9Z;-`+W$@|{ERdPkew%kJshFUO$HyH--;G5?ny<Jq%7^<$|!8+BDSGy0!U9Ou;x<<&l^^~#2Rc;0Y4c#AxQ<b*%BJKle*_)YbreKcb{JJ+dsu?)lbExv`&f8{3_Pu@t>Nk?Dw^YeDp&u_=@zRH~97-xFCzpZVry4=fO(@4#ixmPc|-}|O4`ajkQ?<c2fr}lq)-iqk|OBw8|IqPG8n^GO)oK_Bbn2-6@eQTR8*bj#uR_&dSEzJLXtS=|>p!@a<q1abvR9Ee-W1FCTiiSMzy$$j7?WgwQJQ<DiaJ)bEqUy&nf27(!ZK>PhesirwK9>&(@$~iA%hnRB)c$E5+8OtiuMF-h`4E+7^A#)lc|8YyKIGq;s5izL)(HFd$RTRq(<=2v``UHX_#F++sM~YH(7wubyk35~CDhB`I|Tit$f))it>hTyZ8e_nzBuRTzVlsD?Eh<DFZJ?kR6{?Pi-&po_QSp4PYXw#bQ_QUXBWeLWx0xe95%FXHyzKxcNwu?6_|<k*4--q&S7WN_#M-Oaoys%RC{ZpDtLeUc?kE1PUxrX{zxzX(`cOA2Q0+<bvc&dx(Al4`*mb^t*&dyyBzHeucLL}_&VC?>#w7A-}pM(=<Bbeb>H|p+UV=AqvNk@cpaU<H}r3O9c}b2hVdI;M_cP|MBc9VL!D<?jrYk%Y=M7bmh$a?9mjqfwGH!iZY$PNDVzh%$@k*E)?UDRe~H(px^M0C2J371YSmu*?=<=^_8tDD#HhEAH_-mldOUwa@&1h6HxBKuJ-~X;_hEylZ_b|<>v8-CbzXIJya)g0c{LvMPyeWW%zp4O`u{T}p38SP;q$L4f1&?FgVc4+v3a7r{M#XMTsQa}Dkjk`<wu>tbE?!HyuW%StMZ*oW+4xi4ykjIB~ec0n<wr<`;Vva{O!>KejmOM*(@0Ed#7o+3-w<L?{n76qxyH0YzM!28N80DkIyA-bvog?)l<UXkrJPK{z-o#KCiL;=Zp76(^=u)!27O_bnoHU8vwuG3p_8HXUBMA24kFw(&PCUUI*vH=i}fnJB#P?FBMdK=eLQ-PwZPfzsyasey`0y`xAKI-r4$h%zLZ(@K3GBb3CwrgqPp>BKoh?67SPy41qsl1AJ2u_NDSG;D5#Q*Zxx@yQgp6yc6Sjo(7-m4N0+EjpG(xFPNhq;@pxuCH!s0kpF2-)p%^d>6C9>Py%_oS_bF9HJOxe?}Pl?yAKWX^qrx6UwUvVoD+`afFI89`2?QCI9C)vKbK$Qx%@c@^Vqtu^39vm;ksjz<6QBmEXI=t-*eMOFTr{VtAO@L-l3n!^r*MMnz(M*KIH#h0kwbH7S+Xd*Ih+^I%UFq)vgDBG|mZ**$a?|wvEt#s~xy*zahv&wr0CM^XzO`80+N}eEofFZPHD=e#zeg?Q7;j-p02G_wpa(dv1>GbJTU6f3(4M2NuG-%qx%jZ`vN?<mXeCnXi$D&+zr{Q)${AoMW?hLqGgpqAl5c<o~HZ+Lu7xnhShE{+sp1cp9Weoy<Io_r0$SL;J7DoB3%vHGXTgk!U~YZ`^OhuV}w(0{p=aypCu;2lv}62;<3<1>;G6#M?j0`~+M;{?AQDKl<k>|5m~0AcdzO5Bz*nzpi!-zH=O2FE}@!#p~buQ{e|DMt-*S5BKz~=g`0XZY1(neLC7tI*9$DRv+ZQ<!rRynjPb5*BN#GFMR#`qK@w0S9|*A5;(UzUMxp`hAe<T75TR}8KcHy@m-95TH<qU$JnaK!*%*)lf(aeHtOyDa*SsWzAxdNl~_F&oZrLHe@*5mU9jrk+$943vy9%a>r<@6{Z`1p&)@Uoz5-Ukw_twt>&E*}e9-<%Hq`C0)$sdg!Z;^RQh9JrTZeHTK7;xh@gC=yMlq~Ud~d|Ibe7%I*Y{Oh;i3_qzOyD?zc`=ys{7SG!nb}oj&U*%=5-t4f55!kK2}EFVmG7z!HLjM=I;1hsp}T6`LbTLB0pKSq5a83UiW1^0pHy96za{s*UNWCU%>os?}B|`!cMdw!_VC~zq;>C`4{rD*$?+sd>8x$m%W}B=3BeG_C5W+tdI6!oHgF@c{E&&U;F6*{KfE{J!Y$MI<_8$e;3ak=ehDLJ$>_*dsx4D>Y=W>9f5xV-)}LqPPEiVF;0Gt?DVUsd`mwEe11RKIo*Gir*BR10R3=Z)h?ev|FwRDzkbGQPv5>5?Jbq3;B&6Z>-MO2F9xggo}<pM>YQmi8?Agt2b=@7gNbLW>vcV-d|R3UI3HH4soHB(9PsU<(0)&@x#~KZPAFfi6oLMi%vq=Yjy|P)OXJPxr(=xj-!}KG@{Q+k-8Y`YjlO;k*L~wT-017)aNRea!;QXv4v)XC;T)d8H}r2jhZ}v1Vf@B(xUE{8^6k%i!*AI@_3yZF7wzqXaNR1G=BxYc@y@HgR;F}_r*GTd6Mke@od2hNME;!_aKCk1Myr3H^)vj31(E-AHRgHxS{n3Y3wgUj)#-+>=>In6-E!TD*Dp1`qpo(x;JR;ntA1>~eD|vU#)qT-3y<b|`qr|uFrKIs8&tbm6_sz9#P1VEKEU@_eygl}b6gbqFIsz{YVThS?SuAU-skR9{b(O+p#8w}xb6@iw9i=w<N05H_*;Hj;ORR8Gozok3!~Kd0=mI3unO0`^bYy_r-$;jwQDfW?1k0$DlOLrq5t%DwC|iaT#f&q;b{M`!yVN=X7M5~Kc=qowVvlUs((LsB<}0^a*VT5wnbik-Z`k}M>W=~fB$7Fu4~PTeELpM>(Mc92F9PnjDG(4L-nKOn~i=Zo`vtX-pjYA-H-m)K0*Hj_hOvc^P>Hmj7z=z|7C~Yra$H@|542Em!;^Z!srlB-@a`g{8<@P9a?XnhTozc@?h^7;^|v!G*G_d$)gxg-!?rL`gt>ECF<`g#uIrE^H^w)>fhY>hVq>+Poe$goS3h|AJD#EDEyMImwEa17Qo+j2m4`Y;(hA6*B9Y_U*AyQXV#jgR=&043AB&ey4=&ZRXBoq**6gLaxbm&ow;A!RqZS1QTeo*GNXO(%gQ%LwN~G=vH9juzU5FG)K91HOFVtY#YW1v#I8{FZ*G=X`Pyj*u6wE{_Met*(Y{zK<ayGQFi+oNZGt@KDx&gcYt;ws|8539?i{}FePk5I|KthAKcN=B_uG1`^6lYQ;7<+4_q@kOqW@Px_fgMx)OF1(qtXA@9`JvwfcGg<??FGs(?3xCjQfW7D^487bszjswYN0Qh1YcxZo-d!gzNTbrq-P~Z5;AY`nvKR1@L<nXNNz~|BUSDKUq<HFFoyRj5CQz`C9#zc)#FGlKrZmH4`w-mt|DFSzo7AzTF(4e0%x`^?tYQO>X6zXXZyg`T8Mmlk=f{&rHg9zQN~My6+hCK#fzYvc&G`n*(m)zCN1pd$6d=@FVUh-x704?N|2b#_&J*s{S3Rk}BUhwXgE6|BhGVbnv-g&N={og+a=<F2VO^EVH&M-?D3*@@;v}sQS0(+@XBux8cacoX_}PzU3UopMMPI<=8#7PMu4Z9aR4GNmws+zGDBs)AEq|cgFJo{RHO$gCBn$pr7D8VDRJ51N0M|2Mm7vc|gCe@jPJk4gDuL4;XxlVf+cs1IHraw||6je#;u->Dw~ogr9cTOf~MH*uy`{vt#|fBR}d#_l^BHt{y-7qkhaSrX2gxeCfV%zKp&;U%GFcFQc!|m+l+q%joO#6@OjBd?oM={Tt`Y=vxfqH_n%{Rgn`ap9`iV4>?AwbA=^#v-0hUUh=unJ;c*DALTiuXT4df-;?D|{-_^&{(UEZ)Q|2P`?1Bwo&4eYqMu-W8T|P5ML)s%GWhZ9i++OjW$@$ImwsL2`ZD^4{u8V(gKsg6Kf(H{;&<vtd3NRqJ@ccy>3)LmfgAkz?}5`#@I7#YAOAgY`U$=VZt&y32d-b&_&so=Z|Fb4_rMLl#W4N^pBEHMf9^;5(ftJ9OEmcL-%F&Q;CqP%KmL1(^b>q9(cs5_FHyg)@q39z-_U=8?<E?1i(&i;>Z()R5A&n@3D%v#k6(B66RbOfAHVMCCs=m|KYrcm*EOy?qi^Ux!MZc}7Q^@x{ElGo<nuqukM1XUju`y-=Lr1-&k=(k{~V#8;5lOO<DVn?b&byvqi^Ux!E?mmTMXkj=EpMr4aRTyonX9g_?@89*MBFd`^Mi18h!nDg1T?~ouJXze<v8<kKuQM34BBU#@`7Vea$d_<L?A*OEX?jYWQ8P?i+tsYxMQs)#|?SceO@e|2?ek8-G`uz&DJ?_`6!&H~y~H=vxf!jlZik`ugu`<MZSByV_P>|7#jkrw=@6tLgfGxgv#@S?kl&<9|v+O!-gOAOBBj^so4T^*^Oiu6))1&;KorlwEx^t(z-qF@)<egzHngkn58hP&<<AQrl2Fl0|!v+mJgkgafF9$pPe%)G_3d<Z;xoWYL-AapYOl#pGG!5b6?g2ze<(coB6zc@cRibr89!D*|27m^y;om~5dAB@gAlwJ?OMQ2UdskjpWI%TW80%aBV_dy_?bkxP<GP_5(=WM66rvM<?8{fTTQ=cd*s=O*W*)+Fa7=b%<2=OAaLRwQR7XQoylXC`N%Rw8F1XJZIwr&c9rC+DKpAdA)_=OX8!)+6U3=Vb`zqt++qBj=|!AnR)&KSQ_xL%0#O4Oz4kxe>WLHGtfmJb*fqJb*lkI*u$li#&=vo*F_PPY$LoB?ps3sf);=<OS5BWYH1i1>||uK=M5DT!!#)hHxutQ*tJ125M7s268Hfa8hbxa#C_)s)a0Cg`AlDp9U>QmJt4|A%s6s%aA36KT=DQMN5z+gg;Py$r8fvsb;c-@ITbtWC`If)SP4q;cwI&WC`J~)U0F);eV-_$r8ffsaePp!WzA7WR2{@5H?Y>lTGAA)LdlIJmf^=B-Fg*B;;fa;pEhO<mBWO)cj=80^}6rl&(lkEl4du7Hvc>NNz^$PHsl-NgY7$NghZYMHU@T9!MTW4JHpG&!&cwXOkCF7m!8gkwxc{7n0{NgojXvlZTL-Q(KYsHP)OVoY568HRuy+CbER^bqyhWg_?mZA^bZv6<I>~H)>L{gz#l*VzQ{L!^;fei`38Li{uLo;j`3F<g?^6)Q{vd<kQp-<kRF|sqe|}xekA22w$RpAzvb2rG6t{C10a{C0`@op#Dp~LB2`-PQFS0gCYEsDr@p7{}z5m^&v|LKc||=62dR2iO7k#4uvIzUsIEjC4}E<2;sk|$;lGJ@2Dxr62kwZrX))U|E;;#t?-{3G!6e2KMg~;5Vat=AlGdnhVakSp5&j&{?viwfn1;d4B>v%+2nrY(bR?Hg<OZD8Nz+2L&$x|e$?jV=3IY%4B_-1Ycf6c6<I<!9rX=aLO3n;Px7D4Us{H6QEDM_A?BqhL%2QFpX|^3Z_g0!OdU-g&HL=k5H3sgBm40l%2Lyj%aV&z(~{G2OvS0~$?bWK;{3P8`S)(u{qA$cDanoN@29SK!4Q7zia6>$>QnMP@&ktOGwK`iGxDDd;nxh|=hPSE=j1;a!jGtr$&bjlJ;ryNA$;8xm#Du{<H)~}uTbxiuaIw0ACPa5uQG)1QlF9UlAlojBtId)a>YyPTk4<WKbZ^R1FkvP?~2ks&|*Gd3E^<+3UWAk6E%jsiF}Z{pL~#fmLYu76(^|ssQbzL$Q!6J<PGHI)D`6A<Ra8!<Rav~yeGN0y$s>04B?s71LT?H*$m-B4B_(3o8+iGLpXvOPL3dNrfwo{CLf|6Bp)K5r=BIBC+qcamNjygxzlUrBx_2~uU=!qQiGSM$EhdC$H{xC`^bCA>!};a>&eTg%gM{gg{eizg~@v~sLa70hVU=cspMbCBN)Pg)S2W!@+j(T@+k6HS4^Y^Q)iQBb1sGFxMGnj4pI-350XpyKr8!zC4|GME6HKxjnpmVjpPH=!{h_xGYsL2uK1mLlzNzal)RO?g}jx#n!1v_np}rknOui_l=md}c9bE!j=G4vnmUiVh&+#Mqs}4Q$m2M7<2aw==<D-4hx0#&xz_7JSnA~<bFbG=Db`mh=31|}FxF!jbFJ6sM%M2}=31}k1FZK0%)4IyXShBtk*`xPlCP6*d(4x*{|n3W;ScIf>hI*6<YUyM<YVOR)UD+0<VfmjawNG4wGO!n`IrWkxje=Y-a=hR*5_4tn=5v>;yCpr`8c_S545!pSVDLWbsc#Pc_(!jc_;Za^&I&$`3^()zAK#63)FMu3*_C@UF6;5DC#<L6uB+6HMuSM9Pdf)?HogR7j*|Ymb#U?gS?fziMoxviM*aUUe7$Qr@zG`@5iXeJ?2YT=JPmnug`A_&VLK$TCayStd}*+wO&6vSzkMuYrWo1vmQ?~?|OaS@o}Gjgr8II`?$|Y!mmB%Nk3Bw%UR+j^&!<sen|e6dV%~ac@K3rc@H_78byvKx1+Wtw<Dj|pfZ=|8NxfMyU6;y3ZHO=!xb%kpbdS%62fb#cJf;C4(c}Y4)Q6ggM5m7iy?f?6_=?;s1EWGax8TlIhMSNYA3HESEn{4S0^9gJ;}WtVF<5c2ydXCAa5XVXPofJr?BMv1aqe6za{6VC3B?D*ILf!TINWf-yNL)9n6tl52si!r<gCjer~b8UXou?uaRGopLpa~KMxDbdHE{!JoU1V`+OyQh<e1weI66uOpWz%pWlQdsH=S3=RM)_)apL&^P#YuIjVC`^z)=}Fm)9<m^_goJe|6MJe|Cdx}Cg`9K{-sVx33P-$^}Bj^$pqnIXK9x{17zyoS1-yoNmAW51iv5S~n(N1jX`O|_9nlZQ~pk%y4`YVPwyUxsi1HIN)Y?nfO(?nfR>9ZMce9<I61i^Cbh6R6Y46Ueiu3(2#{c4`#aPLA=Ij~MD^att||A-tBlk-V0?fVzgffINjdpFD*;k~*0@lH8v<n%tk<jyi<gj@+8sm)x4%oEkuGPHsu<M{Y@OLmf<RL+(u-PVP+}Mx8(&Mh>FRA_tM@Qtjlq<Vb1^Ifl88WC%}U2+yFdCC?yFqb?v%Baf#}A&(~yrH&*ICHqtRll{ppsO`ut$Tg|0$u-H9sLjch$Q7t9$rZ>Iscpy=$yKSn$yLd<sKdy$$Ujqq$Ul<@Qs<HflE+XZ$&t*pa5YzycST!<aBXU7a&2-IY9VqJav5rFav5@QYBq9la$#yla$#~oY6fyavM)6=*_T|3nuA=5T#lNLT#j6wT8vzs+=^P3+=|?bAzaxNMW}hHWyyKTS*gXyS;^_B`N-+Wsi--~smRHxnaRn?NvRpgNy*8m8Oh1WDXH1WDamQ5xyfnBnW%-xnaDY*rO7$T1*ql81;|CI)yPH3B^kngt{6n^L#;*@ZA<P$*7pbDG1S`RG30^NDw@0gg@2}&(cJ4rxE8gz=3ZaIRjGwF_j(krNG+(j*ROB|s;}l=@4}U+r8M{cAY7ALPIK=k!Y!!PHTV7_>`!f_x%VsKq10ZQdw&y_{cjp|0JRrcv@&@BxrXMh?-~r@5)5H8LpT>TFF6-E3pFb_3pp({9XTyI1vM2p1vxP_IXN-eL`_OIku_>E&HbOS4>hG0|M9HiMAS6oMC2sYOynfw)YP2h)a3Nk0_61M?9`&<?BqPulH@$({LF2B<~u+A5>!8rx$xus=<7$HuR)r7PKEX7qwoxBAF}8q@&Q*8kGf(%L--&=_%K7*!4N*q5I)HeKE)6|!4N*i5I({XK14l0K17bC?kC5Rw=jgaQV)_3a;#e!!rK|bJE;z`gZHqLA-tO*yq9{Ce3JLJmm$25A-sorf_#GayoVvYiy^#&dW3w0_rHT7yp0-5Zs3};hOTJL5N^T{ZpIL9$`JmEA>4=|T%RFammzFn2-jf<*P}Kd*CThKHYRr=cVh_mpf({l;aGbxgnKfCt<<LEro0C$L%2IbxGS|0xe@QJD?_+5L%1WgF1ar6xg$fkJwvzywGO!s@4o{>xD&MtxwmW1M!TX9LwGE8DtRn<I&}egI(ZQ_oV<v<lDeL}k{rVtj$vKL(AVpHy~nx`j-rN>qsS|$3&<<T!PKebVDc2|Xz~>DNNR8LNOCV~8*(plE9y5Na4Yf`ALtbF7xHB4eGNRBd{=`mC*LJ6WeqH4T`Z-q*U55^x)Khf-Y18Vom9EDlYa|O<#@i4r;@)@<=(#YZ{fDQ-`?cjtQFx2u9)SDaSY)Z)KKya@?xr;yqLVo6&tCWsdn;a@+OAxYHBEXH93SjiyT6pNu5BRNghw_PaaS1N9{oFM{ZB`A-5-M)EPcn{DWV3x)1cR2A)oS<cbLDO6p_sN^&?u_#svLddR<pr?G#z_B8%2{2#RgSwgrSz5e8O<i6Ai<O!V1z6{|2hVU5b4DuNAH0omVH1a~~D)K^dgvZ=RFoZXl@C*{&L)~a{Kc|HEQ8%01&p6?|)J-P$b5K}+ZVJaxSCeDNE2$wS_kJb3h&t2c-rt0$Q^%X!`=RhyYCn^E{}k>+ZEte#x590y8o4d`JL_q>k9$2%=Xw>Dy3yC~Bd%|~w)FKL!Tq2+)k=-<cuooTq^{K5&p6>8)NsxH92C}{o5Cxo56LUY52#X?5BRt6FRa!7$iI;PrAl4?%fE$xX07%m_hl^#`@3S4D|#}7M^Jwuk09Hq^T{^yJZczu9(g%6n!KF6&V;j$=niVM$$c)0Ho4DH(X8KS_O*c##(EFqwe|WJUP%4L<X$hr)2O3N?)4=+hU#x}uSb98NVK)dy?$FWZ=zp)z(12E-=a1jcm8dhAJKc7d%o^*K1G*l?)hED`R_*ULS3f0&t1!S_UJ@jLcK>`LcT+lYv1AD!jm|jujEPO&s4d$&-`1sCGXdt?9W;eZsv-Qu6E5$2;omY&<W&E<RI!T4ID(i?TQfUV(KmOVsa=$IF2fP#qn?9iR}L)c_R5As*Lp?{w>^s<L^#xLAFwdk*(xF>O^uNc`|i2c`|t}bqRScd6_HLQX{EL$dTkV4B@5J+2p0<In;^dIpj&yVdP2V;neQr;p86FX5?m^%N~s8Cini(obxU!^V*Vse`39S;=Jnh6U6!wm3h_c?KbOCpL@MNLs-9^s2!*wn)@6s+@88vbD!abJ5ob6_c>o!e_bHFlp04~O1?{#y3x;*6M5d8$hy(bpTb|LQaAc}Rk#&v$!c<+Z-skN15NJpu<%IgWRv^+EIfre*W^BL3kOq|ncU}d;T0aWrJv`8<-EV0x|O=t<bEA3yoDNRa=!)_j-{?KxnHLXZ(|6rqb?<{BQK}UF}e4D;d#_aCin9~*hU?0az9^$M^Jl^d$1OTJG!E?E1EKdJ28a2GK9M^gu75Xl7n0^)D?rNgUF%-$f5(uLDV7Cf#jmDDB+4?)UxDaWM77GaaWY1R-l$8S0I<CmLS)lmZ6p)mmwFX79|%Z=XXU;YCdXFaz1h)YB6#la$c%0IWIXEL)c6$PBxQ^c-&_ZhHz<DRHxRZmLu0C*QZt>*C*GbmM80ZsmBm*#1O8{5UxZmL#{+FNG(h*NX|pePtHTm;gQoE4B?EfNI^|Q%}Gu}&P2^e&P2{aEkw>j&P>fq&P+~A%|%X2PRS6?KsA#ykh4>Zkh7C>Q%jR`lM8svSpkM{MOW0KHl$W3HzYTv)+IM4H=))iHzEH-tw*lMx%`PCT!$g-N3BivBUfVxSD{uSS0R_879^J<XQSpJXCtSh<{+mdr>15krzR&gxoaXRL-@T9LijHqgz(=!2w@Z3rXiciNvN5~qFKmE$jPah$;ruy8N!LEX~~Jm|MP*SBufat^FauIpk^RT2q&YLot%uEikh38ikzNWfSjJ3m0FRUm0Z%~uDOy7;mQo*stn<p3}FkkA=yH1;EGmFeN34XxqrMI^8Vzf^z~fhsfW)4^#A1CtZAbI0!Q}eubGYi()(x6p8v9itFQPULAPp}M18hla{Zrt2%o|xfBhdmY?FN'

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
