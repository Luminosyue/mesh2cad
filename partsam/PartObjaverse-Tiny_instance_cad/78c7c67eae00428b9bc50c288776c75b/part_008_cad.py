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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_008.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_008.stl', 'source_sha256': '5b3143726ef06fba075cf7bd4f4797f639ff97d5a0543907f205e64a2ad4e23c', 'input_faces': 1068, 'input_vertices': 616, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10480175912380219, -0.3875342011451721, -0.18325987458229065], [0.2331654578447342, 0.10279786586761475, 0.012763261795043945]]}
GEOMETRY_BASE85 = 'c$}r32XswY`1Vht_ZGuoxO(&+VUVl$-up!oog{h?NAE<7GGVUXiRc7J^g23&;f`L1VGwox_kEuyBl*_%t@W+%GwWT??>^bt_nf`oz0W@ToUCcqFiBD`1OM_GpF1=jWUp)(5@`)DV`xCg;NCp~29+ETG{VEksJ{G**Lh7^H*VJ6!x(CeEbJdJs7FZQ%C^E)0(}b?w-pW?7&17d+kmbEL;M58uhXsHpa8c&s8_e30QYBapE5qhZRLs-w~e;_KmJSYJ_M`&m3@cYY91eVLv>HJBhZ8J#}>OT>RL7`R@8nnEBv7LD8K2BmbaFD*(++)?;Y(Y<u5<mujOmsR^M8B|C*{t3Y70P4&{r+Z1U6AD|1lGJBO)nA6)Z_YLUo8TCUBOJ^FjYD#P#Sv{dUiR^QljbBEMp+n)=cvs~V-n(?C^kFD3}1Nzx97k=9GTf{dzuGISNLps5~*K(yE&!md#Tc4)y5_PQn5$F4??lCRr8LGbV^ZSiju6&Zi`gwQ@_|+%x)cR*+)AlkZl~mtedCCR-JnB5^ul#JMs54DC+Gk6LqpH<!sBi2#wMy%$)j`kKI6edZU#+x$$NSIQwS3Yb_06kSwEfI7({Nt5+Ms-nGkTm(kL22q=Dk|*e~HlJF;l$N`pxF0)VFsltL<#GErouc_UjJ)9QX|VIrI-LZ?#{fzB%HGp1)P;t@fi;yFPrMET>feE{x-^^hA%>co?)xj^FCn5$$s0clGW5sd0R*qEY{h1t?!*r1qmVAx6*3>@*90XxwJ;?a`-j{FegZdso!&bv~}C$7M$S41e6!a8cW?YRIeiY2h2wrfHts>WbsvwksNbq?UI*Jb~kHz7Bq!yV@_Vbb(sG{ljGVzA0y`|Ev;@Ct?KrNryIRJ&}_%|LuVx@bA6VytU?LLVlhf0RQ!G>Koe^N9pG|$<?>g@6!IVm!6AuY816ibyW-G*~&rieY>e|q>PxSzvmyWzO}P3d{?`fdcF<MBX2vUfPZNO%2gW>o5+9BMf=Oyuz<FgZTAWsSBgmVV}YFb{xr?hxBAW0_O}nei~RZM*rGpQlN{$e_7BZRd#8ZS>Tmg`^NjPL?{WQ{x}5q}P$SJlTWCkL+wa9TBTqtfycqeaVmv0bw0(`e-F9m}c=pD4&Y29pJuQxNs;S3kfA&?s-#BPrul?1mI*#+&7WkhsId$BveuegUFb%$I8P0pg4jrfV`~%=uP9CNGb$JBZ)1xN*Mq_``;~yS?aeXHne1~(0)?air=EH*i8`O_{s_kf<$&B({uB?aui{`)SX(A8H99gIN^us;P2W$0f%-a`ssBif_MgP4khI-2FU5k7_rS0SF{u<-?P)GR5mLT71{E7TelM{ZOLEE)`Vq)~Oec^#M7>^&de~tU?&<^FwuGY^J|Im5K81q=$-5$AqmFnL===^ErY=-_lQFRsaGaLFPEH*}eem%oVE#F`e`q$N6``5nV+j2d>iybr{tl_RB34NooZI9IBNFRgov-uyVYWFBTeuv*c9AC<C_*PSG2c!FVT+iBf|5bI#0KIOR=>{RMGAv%EdiSfIm+NyO^waum>YG{e<NF+|QGV=*rK-yU^gJ9{9>MS01b(~H6ZH402g7fFD^fqV^wsk*{^$!o?yUO8<kT1S=ZB)TosC5Y;n!<9UGw~>)9^E7hVOj5O#RN@>YF3SEKxrq=NfHi=V*M-z{QI(ej1$CcHCWGzt=q2WRdy>+h}{*i>A=)sTr9c{`r*~wLPC($gj}2g*eW;+MbRNuP{DxJcI9T*SvD>iba3d9UP(k7gj;@!QP>q=7SkgWC8lCqUM8b(=*Lu<7!&?ZEEWHvZeY5^ZA7ObJV}rPsfGv=?9Fvo54C?8-*|G@z{!l;COC-nuT$cPy5m49F2TfxM~*iZVs-$<uaoEFL<GR&=TZT-fXz8`!AlRn)5mG_FFED&nqLQs@58fbw~*>jMM2+Q$(G8B9XVX?xFpEiyN;x$zSVtwoH!W42v13YE;;(`Bu3F#%V<N(W+ZU>i3%YHsN{^7BLe2xk!Cix4dY#J#j;{ora#&e73HIVceBJq`qx^1?1JuS4R{2MwMSMF8;cRc{BBr5Y_w+9M9mYxL)?l8>GLVWE{rfA<o;QGWS+(bx+UB?0*vH6;!;JYLa4T&wbweF&-R&T2GsAxW3KYg?b`Owbgok7HfW5JI|wE9NSu`u34<dW5$p7bx)e;aZl?6KkXH+3#YYJKcqY6ubfv=zvJsb_0xxIKAOKyg<ol7kopb2X+4gcr_t|zxr5c`{ArY^vQ_=puLkSqdB-qbo@T-Ia!?VS-wj7QJwMAM3+kW#Zm9a+%ctmZmRo@H`f18=^@q&W@3nZH{m*~jY#+Yo1M<On7=F~oMXKkrFmKzB($8CdTdsO(BIbePQ%wE5!egx-XN~8`!{Eo`)%P#1>u~#l3h?h=ovi+h13K=^%w4dq$o8ksJ4S{uomcIDw#Ilo8LjIcBkUE%*Bh?)>g5gBcI-YH>*vjPalOc~aE_MeIJIuy)O<FJy`HQ7^_<!cMyW~2lb31d>F4Kt)OWs~g7xCuVEEH7>G-v$dx_(JI|lyLKT-bT%^esAC*ZeufqZUObZ;VmY3Y3l``zAT#RBzrxpe$GT2(^6XFRt=&;RgRTzBWMI-bxsSGUsZnf-j$6I%cEPQU1Rp6IRP&em}=`Xz6nNUeWcWt@MRd8ohjhNW8n+J7-WM_<Qv@Wy@hjpa>{m+5i7@xHlsr?!i8Y#aSvGnDI?b?bE;I@*`PdSF;i<VU7kI)7R5<-G$}sNc)N^(uK9^=;cS<Gv`Zr_N_Cp0Ckn7<}tNXFb2RRnQKPXTbOUG*x{bzqM{Xe8<3rs(<qOzT_NyTa+HJYv?nyPfQ&Aac5VndO6g$WhkcWZ{xuz?MK_m(K_B;11rG~4c6<F(Qy;<A%7_RbP>p_?E7$^*>WuWBhi}Y*5gxL2kwL4q?_isZOmEZdCv>*InOw!tkL{*dcTBUc`?>M8*gd;yBcK2aeFty^=Ql0Ly7!#voUXsI;;I}bse%n^KZ`@Tpz;=>G?VWo~Unp{-k;CdQuzb^>-${|1sx$(fo8yjmCBP=w!XWH9loSerCIK9C>(6eJja)<YC<|M-%x2zv6nFdbFzJ)F;%FrlTI8>*G?b&(Wy-RxRIW(HZ@|*4D9vzR@#S^WRaxPxHsQ>Ua2~*J<9ms$>3fW@wFd^MnjKKJ6KXAP;lxg1^NR^I@tx*e@7*4gToQXt#U?F+UjJ;NOVA_0;2we!qD*$2RqY-s-x|+Sy9$x92MY|6COMrSB)Kd+*nVU!c`4^yd)V$JJ^D-)pE|-|d^*YCbrx_J;41L)RgWDL%Mgh?oR_O<i4YI)cBUUAxYK@4sE!)pa5V`Z4bo`0u0Escv|Tc7D1C{<^HQ^|*~i=*J%|_~UBp_%N4;VZ4N%XZ@owuT=R4Kl3H{_Qu`y^IIQ`-<rR}KY35*U3;cJ7>|Qo@H3tmtLHWD0<JHIH)DOaeKXce+t2E8+FBezdqqvfdU?|6ky_vV8}R)XV%@Z7uU;1&Y2UyfbQkNDUERlMKVSKxzCH8r$m8U>M<(=*f9|6Gq(k(2Y)h6D*N+XiQGQfwy?&cZQ{X!7oYq}+)!x49S4gA2`LTwMFWY4gJula}^t%%sf6|P4U38ZG34W4yIL<AX2Pg7_Mo(8iXiHB$j^j4?`+8s<vZNpGL%SA$|DZG4VOa{j9$RgF_`N^idT1usb&U0@68tMK@x4FYo{-4*nt*w%;cl$Yo7LN$sNE)A8>gSQwLy6+dneWKOHH+&`W@)E@mFnjXqaj!?w^egtugNQuf+Y)hF<WS6vcSE-FJXr0^jU^5bK`kS7G|OM!&@6<0^(~eK!Zf_fPsO`loz1&9^keP*1X0)U)R0AU*z{!%#k3D8}{6O**cfeJ8^A?h}slnA8saHWmIq{m`C^F89$qDX{|eS2%_GbE7@YW2;d<tPGB`hKY77v;%&B^s_lRTIUC|&3^bb4xnEnqIA6#@0*!+!JoDT>%~0BQNGtOoUgU2sOoO6BeVak_iIL@n!3(*G(E?D|Ay;B(7VC<y~7`&{%$38zKvfG+pGVLe!u$>`*qvTX#YEd<4`{JNgPjj4Dy+N{QjZqenafDd8XI)H6EYBenjzg#}oN=tDt?NdbZMjT#^av_!QG|A5mol=9$lVP`=uFy`MIG59s)F6)OzCUPIh3ne%(;ad#>Se~O>ppBiz0_tf+Hrwsf7qtOme{KNG3THE25Er9js^y0WKPpk{S)GhRHr!Sh<|M~qEU_FrPn5pOWQ$zT^J~+<d-zMpK?Q8=7Xz`iqJ277Dk6Np5rN4*qHFUa`H@7%YK3grESM$eH&|bK&Gd4LeKU~VJ`DV{B5dO+D=$F!^yK23DL*YN$fa})PBv?24PJv%8JFag}O6vN{T#W0SJ3$&EPwF++`c5y!eV1Po^w$s^XS{Fh#r44)7>)bnPpjZN%XCvMAF1=OeeOE=L%(6&QM2a6LkWHR2t6Kqu{^lm#csv-9(s-T4?m4|c)JVb%?D_I@5&>zo?I8;$8DRXYMa(q^S04-_@7H^{~Ape;Qs&NP5ANi<Oa;cR_&+o!-imek$3Y9DQ{cz0sgV~Xy+sw^?v3*e^LXqXT{DF5|w|@9qn`a%3M9pis>-VUQ4UTZy)dp<Ey6^{A5|M{}A#N`C?>;KmDt&!_D~hzoQWRUaxUoF1~q0BELXh%nvD%54Jfa;2+z8eZN9s*iXq<6TaU>w9oAl^YwcgVm)f49jN2Qid~26^7#eu8`aWvwN<bj#_6|6_(_vv+(qqcqsJ5B<nipldbVIv-KVg(I{<%JC+vUi{tfHH*B1P^&<Gvpvp3@Y?%o6VjtQCvwt#FpUpY6tg70%gud~+X0MwHP_uIyUXV^!%{rXrU->A}9)Ujd=_NmHe!~O7*Jjl<XP4xF%XLG<W8I61k%%Jn9<?0Q;a~bse(ze)V={pDh)imhGZsD3g=Fx5NQ-*6hn{f|yAKl1(34X0g*hid=Jh#GJ@Mpvz5Bg@;ap%hLUVZz5%vk67u7kh!Bg$X=fO*52U!OmipNj3r`0{C?T4sr^zs%7A@ONxXG_GBn`>Ai1a9|%KqN?6++3yTO`3G5WedP7ssyH9MZ&BPgO`fLX)jnqj{AC+)-LH5R^}UIO-=jbFQ_Nr;M`pg$@c+rc>lfx*tJXXC(VtL%stdU9{!k$%VSXA;ucq2xQyRu3{9a>s0UfVazj^SJd!ZjY6d9!c<O}dSa{fr#7xx8wuEUQ#gL%L<NBh?m^%Q;y?g!hi)zRZ0@elkx5%AN_!F*NYUw&^0^1Rn?&Gfuhq&tA|7KeSoCwC?$^4oJgUUHuHzwNRYeA@}kv&OGJnpeN%fj@-fXaV}mb*2#f)=iOb{x@}88^?UrH^=)Sf0nJ#>xg4!O_X2s7WuFU>mM_Bdz2r(3jJpvUtT}&>V)#<pc<-M9GX}5F+Jfo!1~MByBYVhTL-Xw|5jShrkQ%*U|&8L_5U7?`aLnP8lKDHH(rT6DLty8_Sfl+sAu?d%=0HRW1aaq8h)=ATu)BK^|8QNmT#ux!RU_h>q_r=Q0u?52lYSftL-1}8yAAHFH*jA53R>975v|)={m>0?1SFF+RBuG|6;`w9Cr&{4;cBI!(WsM`8g$}p0_zF82+jt>_aSkGf9tU({T8Gv97U77SM5Q|6>e%?q698it9eAwR#$S$5zZ&Z%Sf+Hu+-s$JgV&FY2u3kG<zw`0a0EpK3@M-M=wQMf3P?=zg6!{cl{S!Y%kQ?U4UL=f)@USENT?b<T<Pp7&Apt>AvhD=Ruc>z{fF<yU%Q->=UVz3!Mfp1^O}So7Q}{;xi7u#bEX{~GUiV+-nis#VkDkbcfs1<z+}&r9p?-AW3-W=5U=oI$lUkIYpW;NLoo@pzyW=9wy4;1^kn@nYumP2^w7itFIT^SVxOM3hTh-fx!H^Ple>tH)>L;{DX|%Ie$y=!$k2`C7+?)ukHBuQ2eOp>$MzJ<hhx;7`k@>ontJLEYbVHtP;QgwKs#4QpvTj2H<&e!aox6lTaw_{OG^s$C1{{h<BlMe3WEj-sBmQ#8+=NmjD_3*6^CSft-;l;5DfwKEXU%L;GBev$t+)H5^&<7L8Ohvt8Y82Ifo;`l%8!u93danzsTi|#j?^H$=%c;;#NfxB=&%l8e8-S^=?Iit^!jY3OwJ!VhoY3b*<l~ZxPUPHAVd{e1!4m^+JsgC<BV`+NzttQ8@kNK$p_9ZH0Mm;A>W8IbU9^NlFm7D%ItfO3`JK?xW!q58<$GPW@K5w>SOT#~!6yyE3R%6jlJ~$r7c&xYo?1ArnTM@oBQtxXFdl1$$ZL6Z5(p7Ms+Ids+%iLcB{v+-SX5Zaazqe%__+NKpe`2ARJ~uU=w1EG*6y}qHnelw6Q9JlP>2y72_L>}<$iJ8u&wWOpS)uhm=m`HsbId2XS`F9Z%-RF~xR#ht4r4qzHV3Nj4112}P!*ElKJSnIC|_?d-ov@JZ(bsw`)roapLkznXfXU;53w&;f0y1DI6^|<JDocJ*t2fZ=Y`gQ@o3NL0T^FpI|nE94I?M!laC&{9<*Ja0>260`<PPmcp`s)eatiISLt=t-ggG-ADT+{bDRUeVxRe!c_`n$F81q&oz(qotLFmvnXl-2*!elT9+#`!LilM<Vg7NH#q}lL-+cq?L+gt^FLM36h<UyM^NeemPa^+SJuPov@dESTqDc7h^U~cooqzuG52ivn<ByVh9>v$IZy(YF?Up&I?lZ*u@z1~P!E^OFl;iMD`0?}GSnU5;f5)JG;@1OF{n~4L?mGd0&2PB=?u*cVv9~ybdMY1A`LG_?4~h40#OgZVUNRE<%FoWjH}PJL;lzD}ne8t7w~<XXIga0OJ%t~C-JjBSWFr69LAu{%KM;fcjaskZPh5m~BUeyAJ>T1J;QPM7K2GWE*vC%$34Zy_*#C%4jo(}SmE$x7`xXsvV_z-!U-(uYecl*<AL>}1{IL3UCgZvH+``8a`SJ5!5cV6bi|OEJu<(5=B1UWeEX@Gl7NPq)*0%+C-g?3tew2lIGCRhvS*#@M--Y?jwxXV2LO)j^_Fr38)b|Ul7Y*RgU55FG`zN;M&EVInhIua!*2DIvE#doS!n|>5(J1wIw&w9?!u-kSw${T=@MC>+J~7wk3s2-1sE>8X*LL$0`6070KLos+tmpfKKm72#nD>U@e$Bq6C;TP@blxz(1?qbVX6F9zdu79T|9Vlc!`9Fc_(92VpT6pMoi`kQqv89n!8pxWN&C&bZo+@>gZ=rs&2|1Xu1tkrF&ExPI-V5!KmotPuR0s^#;p13+ZU{X&*z(Fey8q>+V`J?U%L~=>8DS6y|cGG3qO9HA9GdrRm|NNc|6$vi+_K>9DiB;|JET_CiX`j+(7xKOEE9ytFG$=n|T}l!#b${HP##U_3zX->n+9jebRh{e0HY$48IWHJKOQ7ho~#qh((??#k}$5Cyd8xp72Ar<9lsb|2QwDSKr*f7~|J-z_5hAJCT#ApZtmLe_B3XC|~<9%EuJ%r{zu-LHT#sZ*%l+tH))JD-FMFAjVOv$U%vGTNRAE3)?zqz2W6i|BLx3A9gY*p>M=_V_pi!`p5G2g>PPMroL~R{_5{-Ouqux6)igG_daW-zU69zemVY1$FZ5CQ*5GsFC9`{zc;!o{5Qw&-c*?+cuyl+0P8=3`<kNI|FLHo06&w7=Z1byG(XL|1L21?#kd~YOYaw~VT0hG9ENf2+N|T+syPIH{-Vf-eR$5|x-}ffzo{LLb3X3ljCG+XKY!DDjGM>U4;efPewC~kzrPNek;qR!9nbx2b9J2B?P2iedNB`!wH^NRcXh%1V9uSNsQk+_SPyew#auNWe!kk6XNq<TPvkGot>fKZIE#))XO+qDo3+Jwf09?<bFxxSWu8>TJQFt=`$_$0!Qayo<tq)rJWwed{)rIexsR#sX1_QOe(XW?;~y>X9B=6Y<lDg^97o7!v-d)jU(gADIQP@eMZ&*3RO_+IhTyq+pcD1PPR6)6-(B<E_H8Bn=T7)8-0#HuM%)M-C+~yor&lL#fB)8jT7LFk_)a`GG+yV_abfScUwwOD2cF;U-;e#kLl(X_ejmvk&_Iv3?NQV-eJ+k?6Xp#g<`l|TYK3uEZ^6KXz7f$E$JuURfL}sCetwASq3;VAt<J&!9K`*loz1o030L4h=!@fbV1L{G@E-hyd~Q~Dxt_OU^dr{q@2BN&<G#$y`i$-1$?G-hu{OWtIQpvZo!aX>!1K*If1`bxU&DJB8=f3Z=$pMe;y5kej{5VVaf#b`QRCKH?&eqc|Ng3Z>s;|lpC7rZB{`zL?_GT##Ml?5?@_r@Cxaip9`Dx-#&|bVq=#>;$*=Wi%w9(|G6($9A2AQ4#B&XEQGWPm(_`KU$}~pHcPpvB)wMsK*NnP;B%yEI2$`YkwW^QiVTsZxe{>njO|Ee)p>H&6gLxzGuX=sAe=GyP*Lu8<Fuf1f=f}#ykAKgf<NZJX!F$Xn?LBoqam=Xz{|etL`E&o|M841b#P>Dvex>P{Pv$;fkjQV;755j`9K5gjt}^^8DY37<?5@6_YaOlvpYPeaCYHziP^bp{NB%l~ogch(oo=627ykTE^kZ3DsMepev-<X_7w|mp-D*4^$rgz6Pmbffw&&O94n|aO__gcceTh+>k%y!D!hg-@xBh)~AJyRsf`2m(?Qs3RK3{Td3W49<2kn2fo9+vl!w19X`;*4{-Pq5mH57i_HmsxK=cV-{;a4{>Up3u__in3B;qkw~bs?%T-iz>zgwMafFdLlLb*b6>I{cMW(as$*;<@^x`|uBb!aUP28SdBWyy3Xuy0m0gyk8Mp^(e*{-{0YTIL=vq@QcpY_c*PozF7aaYzaSUQS9S)S&94H>^<SPTd4hIOB1C1;)?16KgtjLLFZFqA0lKj{E92_o~Kn;_Y+LV4){S?uns@_m%h(pUd(Y!{rLH0$sC;5(p>Nl*Tgz=ub=J%*o*zFz8M;-^RU^VHRj<Td!am^)7eg>L;GhARp08qUgssptPMEMQ`^*c?P!PhdH&js^XhyM^<N9decF1wPhz}3jQT$uz<areyzuuT=~5ooyghIpdE0uswzI2h2KCL49(X@H`M-E?r%#^a7#Gj+9QkHNeU9Kfw;ujK$#wp>U-}pMAFvsIr>fYm<9j<+nXRaQV<D{n!dl>XC;W->51*p^<WqP~Qoh&;<O7~p+V6D5dx=Hr!2kOQ)(P1z>ifp7`-9=<YKM7va}&I0HFz5Q_ciqRoq^r(-dtA;zIQs^PqvkwqwQdOc}IQoejwgQUHcGz^c$8xj=w`$K3L!Ha)y3Y-+uf@w0p-wc(1Hx%9Cifw)!5XD`tz1Bj+h!_00o=@b?L=e6j!2p$YuAvvB?8dzi+dmZ&GDj`q8~#$Bz)_M{*D&<PmltNy}x`C~GCu4fEKCFb*C_;W41KWY0J?;SmRqQ1REb=_BS)a<GG>D=`U<@dElK5yEq`$D!c@8EBIgZ9tdPy5T6*6WmfcI3T+_a~2L!~SzgKlP0VeQ-S}llE{TpVuS%i1z9`KGav=ezJ(Rzcc(toNs{+D8F|P@@!Qv{9V}CVED(Qv7faS^ObGOSoO`}KVd)p!dJBa&rX!ToF4n1gYID6?z<k}>p2$n|1t{ifs~I%`6K0VJ&nZk1@q%E)IY2yo}=*ZhV0ot!9UX!?_ris13&63>h~(5^;l!}=<nH9<UOtR2bI(3-B#JjIQ{|o;lJCD{iU7*_h390SKo|(k7Za#{QXzCiYU+fCM*Az#Qx6Cc)u~b6MskaXc+2wc@_JF>26@3c<VUztyI6@J>DBHk)Ok6qI}~LI`3I`ZX(}m&PM(5e@}O?2(B0BcEO)|0(nw%tmdI}@gDVEPw(J+&2pF@ik?^B-sv3jFnc59|CERL-nygpdu^NWKAxF1=^3s6_fhzJf$f#?cZipZz+aV2_mi#rC-FSUx&=SN8`u4pbMbd;r)r;7e+}M;bq+>8*#4XjzsD-A-<hGJ&RfoZ55W(5rqA(RW2)jkrMl_PsXwDRp38*o(C3?G+Pv_;<i|QH>rw0{l(-0=@59*n9=o&i4fvDV>N?6XXVlI^%@Y0f>E#sn{|GPZUO~DemEmOsc1!T5r((*#c>Ul1>1prs|5tx{TBfv*@BiQ5o~BOeVHiKT!-FCGw*mcuESiBVA^gxl2>(G%Mi%{QfF*>lFoe%h-;+iEBA+9lU<jY3z9NghC7&hVVhG=-ej<y$Ad6ln-=qFcy-pTANftd$7QIaVo$O)=f1`dNix%(ze<K%W2-l`oA=f7Np*qN-bI5(jOBljOsr$*I=g3FNj~K!)s8`6MXUQ+f4;jL-)IDU;3FKJv0)}vRYHPA+RkCPJa(8lXYBh3iau2Exxd*uuwLG~KxjnTKxjnfXwK};QxhJ&_xhHu5wE=kmc`&sRc`!MY+Ke1Z4x_dphmlQc8?s3rPi;#Uok)(NMpGw}MQ4#kcaTNzlB3DD8N#VNp=mt9qCb#Rk+U*{Q&ZEDMgQ~wrzZcw5Z+GRNfw<--cFuD?M$9QZb$u@+>Y$a5VleCl0`F<ZRB(e;eQQia<XV9vS=EzXiBn#@D~Fi{14TGEGl#2KMdhV4B?y9hvbKx6K^tvFEE5pQLm7%a85kM5I)KfK0-Y~KEXNh2t)W7L-+>u7Wo$Ez8eYVMB%&Cr__7odz|~8Qe9*h=eVZ~;Zz<7;o?-8`-DYnlZ%t<GK2?G`;Z5cS5lXdMURqKl20;(UsE5EMPHC#lRq$oUs4~EMPtb?$;TPOk<<lb(e7l?-el1p<Vf;-hVV>kC$eaJ@=S6#LwFIj8(Fj`c@f#k5ME6kKo%WLUQJ%l5Z+1+C5wiUw~{w8gf~-7vgmkn{QM>SJM}s>iYyvU7QIatmHFs8KMN;g2zybplCyF?@?r?5WC-8%fXX~2EV`Y1le~=~JefL!EZUAdncR{gT#o8X7PXPfk@GNwQ&ZECMP=SeP5nat!ucgN%Lym-KnTC)&mWN=aejHt5PrZAzC*o0zQFnA4nz1VL-;r9QSwpFFTXK_&oG29Qjd|3aUQvtV15yfqbBiy-X-7VJR<y*bBVBMadHx}H$%7vwJx~^IgmP#EV_~$NRD6#AEcfni@qiwB;R8QKc{{mi@qd3C*NlXAEF*7i$;<~=aWTek`Iv&FoX|N!^xtH$cM?N7{aHiPO|7~@@evK4B<=E^<>el<V)l`4B=bUO=Qu{<oNL~oWc{Dl=?ea^g3Bo#(7eXcQ0~Mau$Yg5^73vN{;m;{49KpA-sjUjVwBuyoEfD+LAnu+>~05+>~5~A)K3<hb)?!ESi)oD&sRZKMQB|KnQ1~J|I8f_!O29PT_$NHmFz0S2;d~C4@gRgx^umkk4>DzDqDZh4Xnp3sU3AaU7$<qTXcD8sviH$_(Ky)If3<@@#4ZS@a-zHhC{Y_%ih#S@b#iGWiKZ_y+YpS@aND^Z;4(F!=`gF+=!o>M645Y4YFXw+!LW)ZfUWm&l*VUm3#5J)w8VqPNKL<3~6HH8V8@IR(c_W@;947LJF^3}H`(@Kq0}j1yteE##}@4GiJY)Ny3drsUD&h793S)G}nz++@+LWYLV|Qsfd0;Ud%&WKn}$gj|RroS!OrpP%}U9G~C$8NwB)1<9h7$rZ>Qsa?pTv&kLF(;31s)V*ZU%j6iciy{0M^$A(@23hnm`7v|uFNSa&L--5zE%_~T?h8ZM@I(lwqkbiSW!|MrkaNPH`15bn4CD;VE#b_}En!dQ*EfdnMTYP?>IU)#=FmEZ@NjBF@^ErJYAJFl=1M(k5pq3pErzfkwGg=w^T3ZGT#;IVT#?+B+L7FqJdZk^Je_?!k0ER^gr8DfWEcDLDK(B9$3A<?5ProF{)Z}k`42T6Ilj;SVF;h0ej|Tlf1IJNBcCC!VF-s%hm(i1eM6|V$RXtZR6lZmasag=xgy&!fI5#HKwiucK0>v~7Te_r^%eOQ&-n;L_yqL~`2=|dbq#q9&tV0%Ke<1TX$5sLc`?63IF-8#(#y4yAzXr*gIt1Kj#`{tj_gM*PZq67_9NGGM>}dGYE5!?cLcbjBee^;3xB60wGp{1f2TdQBe^5Xv}Xv{r`9CbCs(JICs!wzVh9(a7AF@XXQt*LXC|klrYDQ0BBvxLp{6D$At!T38fqqLYH~j6Pt?@ppUAnWsmQ6=m%>Tik-{Ar8NxqMvyy)x7pCSW7bcga<|LOS7o%n)7bAO9y~y6=0u13I)V$;(<f7F4<f7z!jQnhaOyo2SVH-6s*+$O85Kc$+B75;z(=mjzP;-*Akh4>Ble3e5q-G`mNX|e_LC!!<PEATqPL}D=pn6i18vkATl+#i(lKtI32yjOihHzJRw5N8X29SGD1E~SzKypv2Ke;ElJJmrJZB6b@?m+b;cOciKmLb<9mtzPQq81<*BLC=)UG9c>;EuHn;R|HZUm3#t7{YHD!r48c56GfYcXob90rDIEJTE^NAm=5Qpq3$*;klJy2v?xCCRZTWpgPDk$StV;WPkRha3^=Pbw_7vJ91}oM`{~#M{+Z2V{$WcLuy@eLvkZ(J#r&*OKKBxOL9|c1F~psa#M1BhHxutb8;(k4~B3zhH!g^a2;xGavgFtY6EgL^3M$6D%2+AD&$JkdgMyviqyK~isY))#^kExTGTe=T4X!59obH<PHjtW;?B3`?kGkrNiIgdWI(SOU<u)9cMNyORCkPI2v4W}N}f($L5(J_AaAE$BX1|)W(b$&_semVW(aqnHYax=4`K)pqc$NABad*$C~9MB6LMp6QED-AF}6oheilB@Hi;&mCvRg2FQxuUUP_)!ol2g{Hl5569_Ef-)V|c=<i6wq)RE)?<Pe7NDC%_bDDpJw3i34aYU+0KYVuC%ZE_KJ4i!(3!^N57KT}Ini<6hQf9Dr>9Hbr~i+Xv050bMpgr_ltM>2%7Q04ctQ1_E1gwwj!(*wGXpT!q;QkPNplb4YrsRzghc-)Z;;V}&1FzOO=s5?fxV=*<19L6$>8NwFzAX!w--{NQCAK50;$f66$Ka!U+g!6bJgmZZ!gmY4-ktKw)QAd(LQiG}D2lMAy$XVF7!3<%4hHxv7?|smUAzYs!{Kh~C@1aV6>`Bm1dl<sY8N%Zk!sDpR$m7Uk8Nwztk{rqY6YfmyL>)sO!#?Z85N=ByO>RqW#Sm^u4JEfEw_pg5U<fawE+#J`AEsJlQR(l){4AV{Ik1$Ri@b^<Z1aRlP6(H!`cU(beaMxmxyY5tzSNv#UvhbBHgb7#DbMfuREnR4i+Uo2&wD_F$-&H_^9<qL)K=tH%pu`Sp3r6dT%Wv*JeDDBX9zztppt*j7{a@$d&qm3bGsSBE2-njE6EcX!h;yX1KrVv+LJn-Jf8X5lRB2%liY)9lH>EW2Sd0vL)cF3M7EQwP}`ELkbSAG$iCzX)RyE5WFKk^vJYAQuK`WmQOO-msg=o<S*9sNcnEa_c?fwSbrE?X`4IImSyXcU5I+m&Wd5%r=OizuO0F;GXW`rl#zSsuNpf!TPmGehmX#*QulIzjQOkOMUlR(~q561!UqcGFr&jj-zUCC}O7$goC3m5g_xyg(CES8qirj)+gId({`<h=^?g>gz^HGbEMP<C@qwXfhkFk7=OrGEGJA~yPMebijk5My`MP(cw<9HlPp6h{or;XHoWYIU|H!Qo6I+nbVJeMKdk7_6PBbTMh*e=V@!hdqS?<W6A-o+4JMO{f=MV>^RNS;I<N*zQVO76!H4kU{PFoe4>gxfKMyHN*`MF*1O=ag<NFItb<hFp&vzb7W#fZCHR+Jh`wo9ss|N3Csq-+vP>LA4v-_v?fUQmYu>_xFTzQGLm|$Ujjl7~l7og!55-jPLs}!bPc-jqiIk!bPZ+jPH9p!twh*!WF4a$OWk0)Sr#-dq=|Y`%A*r+)>9Jb=~1`#}s$0bH`eSaI8C?xpS<SJJP#z-`gF<-0`mmG(GuW{(KBo%8y|PKQW+E-xJomj{JnYfgwDDI)yxi$2fx_>`$#r_9r)|mLWGMSLM0Od6%TtFuw1_2^XeTHNNlN3I9MXV|?H16OP{x6fR4xORmfIEz2^ZX&J($8N#)wb;z~I9jFd+2l9jjeKvu*mOO#Hh9P{K8cU94f1KuL;VJB^XXGj5cOJO!miz32)cj;o`FTO=Gx9U$K|$t7F>*n2{Jp$zEvmQY_j`Zgs?@@s-}efHWiO!;wFtE^xd_>VA^hG0>P_}$&c0^|52cPF4<)}eppv66nX4PfFUgx3!n3I}$TOIivl+sDsLjcJ$gQbW$yJ$)tr^12sMW~L$PKAKlN*v7Q!A21n~)om2UDApMTd|FlOw1L$r0oj>LIeItWje4SvUvREz8L{$iGl!UGfX{C$fZa4tk}@qQ%KM$Qh|c$VJ%q85zPs9th#SRO$P^%z>fgzU0RSRQmWa`+76^F?l0Hcn)<oc{clX4nsJY+M3*&{TIv-?oVw<?oaMbZA|V>4x$bw2ay+0BghNLd#N#GQR$Dp{4AV}ee?@C8+j5{+I<o~3lE`YBxhuM4`B#DH=upVec8s(*`6E8&&lf<!ZWFJ$aC0UGpYT_{n;)v8N#!uLF8HFdDI2udE_0`y<|~2{~i1+oStnmiJYGN*?<lq58=6fW(aSgt|zbOv2LNxB5xr_QRk88@i?NW^4(F?&-BCHvB@2Csawf&$@3-08hUtoCHX)7uhhQ(llMD~ME_&8|MfQ${~1ie-wbot_1_=GG;5elp3fMb?*F9I>Pv4K{{zbXdL{'

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
