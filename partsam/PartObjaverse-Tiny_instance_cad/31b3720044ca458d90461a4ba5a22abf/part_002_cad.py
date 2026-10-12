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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_002.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_002.stl', 'source_sha256': '99b728444e43e0997b80e732375013aef048c8974a7c9f92c7aa53c45677f1a1', 'input_faces': 1358, 'input_vertices': 719, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1296284943819046, 0.07054149359464645, -0.10629698634147644], [0.2493009865283966, 0.43973493576049805, 0.10842175781726837]]}
GEOMETRY_BASE85 = 'c$}r2b+}Yj8@FeM5Rgs<#Gz9VP*5ZWL1_u4Yv?}GQsO8bA_9W+96AL=I?m8iqLlH1jJ}9~0Tw9w;y2G)_nNc!V*dE9@5Af4e)s<Q%-U<O+6m1XrAeFHqyH54l)BTn%k?@Qk3?oqZqM)@gNOF%)?-Ndq=6&7p6tq(KSpQ2)UrvlwqDP0&*+lfdkpC|xMVed$?83yDOt{6vgfOVhYs$N)cMuH-Ft}tVwe6ydc^!8y}JzT5!)_Rwc@ko{FO_W^S|!@fBcgvR)z4od6ATu`hTc#zLsd!K3heD<z^{Avhn7Aryr^^$dw;l^!kSh{Y<Ss5{=yMugf|7_kL&o1HQ?>)=Bx%hO1ol3GJ+|%OAAZy<gj>oKV3m?)tR;aZ5tK>GyiS^&Zys36@Q9=0D(*@2_$!Mf~vF6J6y$;FIt9s+jVFfAw&c|A0?^=*hw<3F~kBCcpO0{c68u`?~XO-_(C{7v)Dg%t>*!=L5cJ&wtwNPuTCaZ~F1IYRV6+JGED~!x;u{Q-1nqbbkGpUFAIBQ%*E{KIMlttV(f?hd}PkuKgO{v+lQjsy&k$y8UN=QNF*z52`-?-6Pa~10yae-*dO@1+~A^`*eS0J*@oDA1n7Mf95z<e^0p-<%j>Qq4NEe&+74+W0&6V-G9`6!=Vl;KX_)8@&ls|t8#+RPuKe`-QT_6biXS<ytte4qxTN#cBnl_l@qE_M%SlwlAez}pHTY^_eks7ufM@?-7m@a_A0-@9PRJ>T^(0o*T%iB@=bj{U!(ncZz(_ePF~#()26w~iT++j?bp9Fht3~g<beA9^hw)O68OPO$G182BRv+JO_XnZlOH&|XSeciFWasB|FzzflE9BFzO+%*t9%dThfhvEsP^~QeO12g2OHGh?#h4Z?q><}@#FcQ)z|wiJz%HuC)eAUlE9CYI<;Qazxd)^uKm7R;iHrUemG^&R#(2+ubqz{&+pe=`O&2JRQ&=IzFMc-rSmSWvy~qy*LJP?|Gp1*sDAvmmulZ|>&R-AH*1CRBR9I}@tWs}Rcidav;6}#-Wpfa<D<*G4Jiryh_|3R-bnX*YgK)`+4MTH_t7mW3H)H@4x81udbGFpTa1pV_KloV?P&X+9C>%U@-r<smoOjS<c9{<S)=}cz5+Xx-z(1^<!8LG+F5>}YTBJC3H;!s7k9YwDgS|de3Ks-eOURyQ4REdqXpHt2xK~_+q+0cy?v{cs!w2Qf8_^ik5>H}{nooRC4uj+TvxT9Cr=&a`zKb_<1JiKmpAU$RjOY9xuv%cpH&(Ptx&$_%4D_vgz8n<laj!X%p0-WnICQO`uRlp#y9zq3{{lxKYC5i^WE*#xV8OYrp0>P7CXOOwa-IiK3B){_fNZ2In(AVKbm2N@&iGi@<XlOR(|-QCdv<OoUX^i#NU=V%L&~pqT3_sTkSubOP7<Btn>dZy3AQlaQG_KKauZqDnHux>P3}zvzW>c<QtjnEXQAUkM7@Z`zzny=B&=&_oAw&XT&SY4{Ui(&AZTJjrKTw|C^Qd@4xP>$6<p?$<F<TZnV|?);hiNLsQD>;~AAfmw)Ehu&U2*Be(1Amv=h-$kc(l{MNm+pJ~q$m4B~+s(-lCZ+bj;+o1gL(XqOHrVr8MWa%=UpFXqlBiGXFayAav`QOgf?VP!-uFsAB+E0J^q8{ICbUBr(YJcivoj;|49#_*#Y5#*yRDL97zAk6MKZ{j6Ol_;j!^WGszjof${)ub4eI6RC%c*cx`Tp+;=z0$LSLa7&3{>O!%pm1QSG=j_iR}kpNUzto_jfO@<;*`beP&7mKT^2dG-rO~wWKc+<r_bqKWf)XeSBr~`aC{qkIU~{ME6JLx3up&t^B~kBz^uXbxI%C!iQ9SqwDlK68fgBo)<+6DBpjnw=VyG!*;s-4MDyB?4PQ~(Yi&O5*@GYoBA8yK3?08AMc*}YF+nNKdI~Sa2`F6I(1ckU|5nK-!K2A{n<%6KgSZCKckpFt{q#HAHBI&x6iIos(m80jwnC8;17LV{l@9vJ^zTl?#}(OZikA!^tw8$jPis3<ks_Io!)=s=OlgIebKM;FC5n6>W7iaj}B_4=Wq7gy1p}J>+9&jzv_NzbDsA1>Fd*UEA;-pY_I$4tE&2Xxy%&pcj%|{djympp3zpX3xxw(XP(s8S(WtpDe}w-J@2Y~rLWU-9MkPJ>45(Kk4@0^SUgDYZ^Sm8e|WaOKHXM~^=_ly|IdZ=^~>W|R6PP;SJCV3$dcM0w@Gg=dsvUdCp#)Xyk?G`pCt<D>#sg_ce=(8^UL<l{EA)*==1tp<+Z;xs>|K-yz>2vyXkfH8$C|_H|uEs@@+NW!_WP$@`Jq_==1Te(R#h=@}k;bG~7`8mk;Rtd2>}c;nvM{Ib8;P?mXUbxtDeRgspl#$vsJzv#yQu!(D3X@$daY<@@Wk)%nRMFFO0tzq7s0AK=mJ+rb}|AHDLnzV2+@Ri77@f2+#(ub8L(E(4YCFY&9c=Y<dS^<So;dOf^(RF{A0n9g7KzCJErbKO24{iO2`FVW>Uudn-MP?kf=zoqLLtzBK`Z>*$ze<ppNihTT(%8xc}to-2GJGwq=_UZb(*-iP;7WZ_1|5>`-UKpVL4jFX&+)CE%Hua1yr~L_a|Kj=1ukwQ{FC5b2?%Gk+K0iIG_uJ-sU7zpI>iphM>g(vMw{-nOU+VmUrFA=$`Ca=T9#Fnn=fhL)Yrn=BRZgT_I^7N_&mLCgUSFc}JxwO-diJiNe1G9<`hG3*40XK0oVAr79Wp}ici|gq{6_=blpjtX)%Bb`QSZ0NJYD|oCMw^YH^al0==`-Mw4bZLDkpp`to-2lF&``c_cXekE?cyp{~vwdH*S<}|GE2=A2~E$<wt7f)b0P)r^*k!IZXMU>eqMc`Eya%zsVg{PT;Iw52Bf_>ip4Z^>O|ByRK)m>)PM=;}NAhj_dlo<5Sz=T357R?aN(GKlJb4>iRbFX;<x!&ZGQb#VmS!Zn>xH-!Z@P{a>b4*N1@ugY@{HTR@kSamvR|Ke(}+@}rY7>hbo$r@H*Im2`b7c=h$?BlYz0?x?2gw{)OxpFX{HJLh{r=jY0)%c&UE`^_{+*XKw+ecyWbjIQSkb9MfoIdnZ=)a$E%>^xUJL+v`~@#EX>+HdHaSJZxkJ+JEg%;kB`psx>udA&zn{TR8d>$5DQ^8JBQD&Mnzt8V`#xsST~*Z410Jn9@jp$rFg`xI=T`}IOiUH`?^b$h-P)Z@O~bGqFY<ka(`pdR1hbal@==V@SEuH&jcC;O@L!{z7b`wq*Gj=lJyGvCwnywc#gq%A24{K&g6ZgA!Yhh93HDBt)G<ZqvOE>V4qZ|W2M*K<Pooywfm^E<n~AHxrqSbr{&AGmnc<wwTlb(IrIs<bwd@1OJI3a4+%xAWuswern=?fiIs$d9hAtNci<o#$Qk$M@gLdco<3LM`3(Z|h&5$PZrscbU_V*Wb!FzMUVhzm;!%lON93+ExG1<*(Ny@`J?#E1kYME<4}&CO`W45aowf?Q-`oesJtXmmkRgy7tFcIG@N56rJSqJr9j@l^=P1<(fpkf5OO>PT%a;&X3oJ{79GSu677)4XsP$hnp^0?(|JN*!jjc`JpY-UB??qJAX|g-+zC?N~dqy!OoAj5Bbqq>$Jc32{o=f@4maNmctKaD{wB6A6;J4<ws6!akuA_x%F|`e$LD*oPNALt^Bx8ez?yL_x!!TdP73L?ucZkAD_Qge%!b6<MY?bkNe~YGVXM>TX0DrxmE%{T>rnzoxW*LJKy+rzG-JW-}v$T>$_azA^7?~YF)DZ$l;<ZoW2<kc7A;PkRN&JydKXP4!HXrKl;WUmml2nwW}Tce`gCP@}nhkt#taP9qfGL+xey)?0n;!{J_gs-1BtgDYfp|et1fYWlldnPp$m;JS9K0`iiT4{H2Gg{<8hZzD>)WzG*i*-}oj!eCM`qx9de+?QDF{$){buztCOXZd>~&^n?4CxqQ#id+vF9x{5kp+xHB+vCQem=c$!%e3KtNL^+v0a-HwONA9_fD>!|gY6sg7x0}A)>6_!V^Nk<R4|-0z=0)ecs-CtV{WjxrryrjeR=)A$`BSwY@An~t)i|{M=#VWdoPNCDt$gE~{OBI-n|=(}Sel&353C)(-07SCweyW{^23GFo^<w0xcz<IFP0y<R#-j%jV#G`($z1)ZL0pZA3QK%h0~Asi<KYmNAf*+3g~iJA3|SNUy{fVY)iY!>6`Vz&NsfDZ`KDp-}oj!x}>11okRBzg%kQkJFjs1rk(BlxKDoIoyT46?Emk1b-uQJPv=JJd>y=6NteU<E_!?U#zcOw`IxZNH|IM$KYo2^<(u=JogcqGB;T{OvTK}&mN!~jD}nFNGj^rZH{;ySkIxJ8{kfjj<0Rt|_jU5p=iGkU?TP)Gebu-PCe?L~&p;8MK3`aV<X`_vr*Fomoo{@TA6}~cP|FVbzRax8AJ^0EV9qZGlJ#|k?T5xDJN@|i#mbNS<VW+=cdrjc^6K$s`N4lPuXOtH^})(FzR3^NYv>w>!9#E8>jcY>jt%SUwC)XE?GR1Auh(bG_lJt9^(V68C3k;qZluP)?MGXj)AtwtR=OO{M}e!qtWV@eJC<MO^v(Im&NsfvkJfDKIxl#tom`*D4`gWR$~Wf)JKy*wKhV6rs~y74M(OK1%MX6GMzxQ>V~51!KT{W%AM89Kp&$KrfnK+3^m47Ak*w+Udk)JF=MS%P`eyyK^W)d6R=!z3?fm%lD*2(gz4iG2w5Mync;@tX)!#GVkiP%2{J@0{dOZyHca;+il-1XtmLLA+uD)J9nB*?M`z`(4!19A%KdIlp`iHvD<5TOZ^M&n)FL_ou{rGv@$~V5r53U>L>i58p*^?9bk*9O&>xcFuT*no?^+|Ff-+%WNeP8g`827q2`mv>n{9yMvE1iCP-LvxJ=WFuA-;H&zGfy;Gn$Vv%#+4smXRQ3VPrm=g8}93n2|uaz$M%DJE2;Izb2gN4T=`dzbNBln&#Q4|`_U|y^nLV4<J|2WXrRimeg8LK>hjM{b?4`qketZ(XI`S$y)x6?{^f_3CGw+n3#fe0zwf%o|6AEqJJ^0SCA)quv45_6{5*SFUw2u4;Cf3nu0mPnyXR4h^T~<)@SLW4T$NhluFu7h`ntvPJ^fdy`UI{eyUQunO0RpCAN=c-DnHnBt-F0jewdudkFFW0+w-+OuIrz$=bpN5dBCq-BJA|d^^ct&_pN+$ehG&vZb;+@-}))pwO`IJcE0iLd~<ze*C*~<^@*RS=4ITF$oH?$yUbONIZs*n@#jKTe*F1fn;$kL@}oDNa@9Zne9y`^zMUVxez=`;T_Qi&Jj)8FZ^l)4Yw5L#{K&NFYZCdv?Xy=VEN8|Yclk?-T~hTm=h;zvT<6E&cMBKQO5|6#u*&JjpYvGxao@_1-%q7Evm}x4@3D8K(~sXzS^37d^W)Evtop=#yZ+{SvX*CQBH!;@?kYciJ!$0|-_AGZ&A{Osixc_LTIF5!G3QM?KYpII^5fT6#kYqO`N4nsuW;?xtS6oqlN0&=TdNZK(Mn^MC(JK=+2x0dwp8C&nDbF+#_5FXo9&zREu8g2!u8Yk<Ll?KFA}cLwr|$w;P;mkuK%_lU;nE_6P{meKYo6>eKq0v%l6IrEBN=#gy%=wkDni3`7z=7*Y?f%HyHRW;rZS6&G|i4|F?wK54LZvA3R0xB)kp@roWr;ddBw6^-L)6XTs~N2YjxVjBj6GJ>ZicEq5>B^`Y&X>pkP!*N3(rzn+|bKjHPN?VIb>P($x2*ZARj*!JVs!|Bo}-@ZP#eRI8SeEa&`_T%|uGMsYtJNFB=AHQFCCDSR_JmP-D_RalBaD66s`P}c=zPaBCb;{~0CqAyOXH&j?e`ovV{>%9G{hjUG`S$&t?VEhhcX{0H!~Lo4oBPwyto$xN{(N|O0aw49`(@iV_sbzqA?4fm@3wF5$Bl2_zuUgaj}$7b_iH_WuzmA9!T9#`2iuS5H!S6D2lG6{^3C&*z|3;4b}-LdY~MU@39P}lpXXS<d7cx<UP1fT^CjDlKQF?!pD)?I$&U=zzWsdc0iWkx#<!o3J>ZicXj#eC4)OEvMD5$p18v_t-!s1bJka({zQ5UX?tbL?<O9BWK6$Bj!tw7PQpdH9ndhapAAeqoZ$DqP{rL0P_H}i?SkIGfKmNQI-+rEK`*yzlJlXc+&!2;>UE|O^54U~uJlxZ&oogJL=j{*pJa0F?{e1ob-#pL1(%!Xxn)d~^AAetfZ@-VQeLLTNA7T3@-`}dUYkZpbDYkFkrx@RU|6=>`_b;CfcD1v4A7uOHeNdq9aQFJa`zG5r@0*Nozn`-G`1`CG!(HpPc^_x{=6#&;?e}-KZ}LM6hr8zy@8fLWypJ=!{r=AOO@5^8825NK->Xy@<L)osW7@uXk7<1Sy{GM){LttzuJe(3KWqEu{jBlr_qnzofB%~y<m%t}^ILrT{c@<nMAvcIzWx3>*kqo&UwA)m`{w<)@$L8Nwr}$NKhATVU(EY`+c)p`jc<PsVEgg!0qVT(S|7~!3AS&(PcXjy{e$h>`S$k@wr}$NtCqRiE&f~-|AFr}9@^)gcYGgW`{w%)<J;ep*uKe+7EE!qgZaM2_RaS##<#zpv3)z={(i>xO}=MhitBu5zW;f^=ldVy+us*G;9L3j_eBr*<VT7eanE1#eU$B+@2T(~_@2u4$@g?U<!a~n{KdDw`!c@$-Iu54P4{@<do$ZN-<uiV{yxq2O@8?DP4_(IdpX-T-^&@_{=Uxk<N4QrbG4`W-p}^U_kPB=zYny1lOMS7m%AOz`j2mauNZnf?P=G3E#Lkg((`y`<=fx!+P?WN*ZB5#ytZ%hqgNh3?QCcBJ*Vx*zvslazyGv-lka)8@M-7#GT)=xzWE;2`1bd%wr}U#-@Dp={Cn3ID!Gm;ejkc&f3F+q7j)O(d=G5-@$ZN6ANbzb^6mTwzBjgflOMh{%)MVze|-BpYUA7AQ3q~6{fX+oT0iRbY}moAiG2SL!}Z?>!}pJA_F1BQ<C}a>y%gnpUYo>oudI4KwEXBVBUd`}&G@wQjc@V;kK8z;_E&SCKJL}+Hm4-;BUK8obLE@*+xhq^znSY_390)=i*HH=JRXURp4^_ET^#>Jh?w%nXySh&q|a0TSN}vv#mY}V^Z)m6gk%~StHbD6Oh%`|li}IudvLK>l#E3S^kujO+#Br)_lC!!W8ksyBy<8i37(10fM-*OooEU?lbo&SW_WxoCdT3&^j-KJcni7>-U9DMkHOPoF(npr&{^;tct5%W-Vc9*o`m;O=27$nd=&l=-45^M7*C;}!l&Rf=sEZdybnDBe?lG3qNm}r@IiDpyp=XQjP8LC!^hD>@NxJfbQ3InH;z6LeH)$uZ$>|WH^Y0-UGN_G5PASU1aCq&!kgd~=yF)<FrIyiz5~Ave}Ha*KY(|kd*NO10rV(*0N#jx2ycX!qbuQk^wC;$JuGu=x<`+3(Yf$@a0(iMQ{Ye0&)`qtbLe^a9DD@*7(N28M>oJyhiU9nbPhZhj-dPD2>coP3H%v+9z6@6hd)LS!XLvM&~*;p&9>+oSlV_w?JK$(UI{0o%itCC!(wzPyciyUz6uY3d!Sw69&kCdEWDQX3!_WmFgy@Vf(ODK&~|VKxG3s}*V7(L&_(bPI0@|!C&BH|_HaAcj~0P9(5{Qn1@I!cKiU`W54T4<!tLQAXmME92$`#^&=v41cp<tNUI_O?2f+Q{E@%(93tR>*2TNbCq;Ex&;id4a=pgu2xGNfjyTWDB(r{V05Ly71GM7<?=wNsd97H?8LAW$p0xk^~Ky$;=M{DR4(fRNKxG&lV?hAKBJHs8};%F(jIQ$Tr1un-i=SK^{`Qd!%V{kq=4_Xi|#Bn@^J_0`m7ew>I1vvIc(46oia9%V!TsRhw#-b_O0B#C*N4vq@;Zf*FcoaMloeWQe-$iG`@50;Ao$xmJ7<vjm2A@FBz$f7C=stKmyc%5#uZEYQVR#ul7##=?hC87h;7)J}v?yEx&W&b;bHh2&OmI#(JDM4m-}=cF%>ZYGGofkVOmJp29W1{sLau0fI0Kvp^}uQ1bf_1W-xeoV^dUGs>_L5=)IUCcFPavXoGf^v8DSrs7JV3g+@r6pUqV~JFTuUg-f%DYb#yHJIy?oP1W$oyp)=uG@D6k<yaPUo9)?fCr_tl^X?QpK5xg5-gRX+t!1K|C@O-!r+7IpncSgIwo#9ew8MqXj1<eI#fit2x;EeFYXf{}WTaH}O{BSNf2bvGg0cS(=zz1U;pAw6;gz!pq2fPxVi_U`Q!bxa7I0-I^?)Pdg3Gel4Z42*(UqiFPufb2EKY27i31>jRgC&Ij!n*?h1^<R#g@1$pM1O?;gdg&1&EnN8AzT4%16P2Dqx<0D@E-I<pXNPq37^(?;S%rwbUQo%eh=LbzXz{C55foOOW|d)SQCrAgzy1$IeY-#ht7fb!Q0UO@HTiRS{$AUzku%cYJLIU>D4+6-U+ux%fqeV%xHQzGyH=`>s^m#3E}^uzrz28zeexCU&G&`>Aaf1g>Rxyz!Jg_;|+x$hFhV#;8ySsw3tux4!EvQYd^Ry{0=%Beh2;tT?Q|sFF#^z^keMwqg*qViZR|qcX?CC-Y&-GF6wQ@>QKh=P>$1#?I#%fqUjuSLHJMF>W*XX++l9rq20|~`<1!)EB$2V=3VCRUHa9`<@C(;^o#>D_sg?3lxN(SwPF}+$uP#5SzCllG6swLQrDv5tX0Js$4Ru|0NQ&1b8I&89&MjQ{#<m9FLgZ>UWqRErLLdLnUl+zduF{|!#rI>*=EkZ2frPQ=N;qWdB%(AHgD?q*~a)1eZ`wP-d<rmie_|-&y0*;(d(Yn@qC@}E*kZuj{hk0L-evIb-r9?K8b$gm|x#8|3q&%=Hm_Kt7s-~>io^b{1$ELnC~rF4@9>+)`#t^AEI@9sq0A{)*I0ozSQ++2J4gPR>yj^mGw+?k7Iq?!}=#0@ujYZ!UxdZzSQ+|H*@kG=H=Uj@Q3JLcrW?FQ(|>q7K^vNnnj18A$SNJM90EGxD)yY+zIZCPKP_ggVAJoFgzLE1W$(7q9@?B@Nx79_&EFv`WGyk)2CTfwzG2V>p1>p@MiQBycs@;{tBOje?)WnH2(<SLrcRF!rAbu!`a}1Xbrd^{22Ni{1{xor;kOBqZC>IE<ld(6S4STY~Q1NI)tA_KZYfQkK!$bkHUS>S7Fg&4t|;KV(|YwTI;|P!oQ#uVF}^y(dS_a;oE2nSVH(8Gzk_h>fj}87lnJH$Kc-Z5%eGU2>g^!YdN20(UGvUVKVLd1l$1K0ylu$qPyU>a8GnI+!JoYzUs5Tk#HDo1GgbROqtc$XLZJwsY7Y%D4NSr=Unu^sEpnJ5x>&^zcSW8CQi}+r<fZ{iFNe9=oI)>_+@km{4!hz4Z?NcifAXeBK$ns8GasafewaSz)9$2I0;^Yu7#Jt$I#>OG58<!7x*8zoMRm+N93e`ax&-Y6Q$^@Qq0FT^if;pbX)qq2GNtep5#8q+97MiX|y0*khMVgG3LCm<cpfMNZ71b!e&hqHtU}7+k|k45FSeizd;C3Cxnv;;Z20_2}1Y>LijI2I4kuoz#2A+^=JekTp5-1s50BahrL?+z=z>pXfar{h=XN4DuO5cH*3@{@Zaz)^n3Ugd=0$~UxR-}|ABvo@1e3D-9rmIxHsE{;hyLbxF>uFm38P4+rpJtn?}N-uffuWOMR*9|5DZ}(M@nNyan9}Z-IBAAHcid&Fm}8{$7KZpqt^%<S(H<(tlkD;i9PYUs1M&57MW-;DhjJv<NKvtb?Whp2ZV>1ib}I2z$|Mu!Qg*ct68`!14g=XZlk;%%TtTq0)c(=*MRq+>`BR;8Exycocj9m3}+Gwr~;p@-<jA2umAIbj+8D^sVS(cqzOIT@7!7ccP2no$v?jYYF=c!V}OB;19^3Kz*eDIupW$QR%<JYzs%|)6sAQ9*I5+i&k~;BWzcN^P*ljFZ?h4D*g8_A^bZk{r5ZD!uQd9@O}C=58gAdXcY&KV!H}F0zCkafKyQEw-mO8{q$uJ7VQK}8;*C(m+|zi=t6iRyck^tFNRm63*go8BK9?b{dI!Jp^M-}<d361(tooE;d-d_Up=;k_tU2%;r(!1v??r`)xmk$&I-#jw!HM`PlWJy=<o1%@D=nvd<DLWO21uYTlhz`3M`t%!6Vqt0=Gd^;5P6+RQhcn+rlr>mz`kIcVTJ69gg|3gT56_fycuO(Sz_pcon)IUIi~;U*p){yYO~&0la{GVYz3N`@-i5VY#Q55SIJ+S75n!&j`!?x`c4lqeJ*I_vXUia6c}5gL`mcx#!MAIdY%f5|(@G?Qk7Jcm^T7l@Q)T2uIM}@cdXzkHug@xGx%l`@*f!m*LiMH8ek54NixC?$w+QzTnk55xxM=N1MR&;qIs(?he;ObHnxEr_r?V({LFy7hDE@3Vj@Y3Vso748I6>Lnpx9;P=ss@cZz2^iiMY^Ke?9))sJD_*wJ~_*u9WIt^|G_d(~w^XW_BUa=Syiz$Tg`)F_YeRwL`5}pc=MW2Dk!p+e%aC7((^qg1oBk*Tlt@Gf|;PGfzcs$$)eF1I+7eXt;h2WfMX*egG2CW3AfpegB;T-T|Xczb~xFI?hZU~P<&%)#2Pf?#w^QUk=pVq2yKDZhB3fv5S9qk48qAy=(Y*c0JRHa-qmVAsi(X-yvv3HiSd6s&cu{xKrJeT7%W4jAuzYFbR=0aWON?qE~%$-WitxB}JnQOvNqm{j>b5pn;`hqugE(>=@yLwaSzVLi>o;P)^5Waw(^QNvX!s!@;X?&?`Q5x2&G>qeFwBfU~_p{8gSBO@$eKqo1qb(ilp>SWcw=Z@5?9H6)&D=BV?I7mqAj&p#wiWzREb=(ULmtM9=qKLP@$(7eOY}`|>UevT@hDo~F+S@venks7#&ZG2yJ$AY_|L}t5cN6ci;wvvn%$c^zl3w51-+^BQMeG=z?(XMg&U!7c~j@R@Obo$H+6jw{tV6QOI=U$vfhX`^`)*qO<A8r$2iujF|22zlO5~ZWY#~?d5-l^_<eMeFLnK##GGu#ynKle9*s_cr;sn4Jr;Lk_5RzdSu{8LCoCbH1N|MA5Pry~L-=Rn4!-bpw(r0<(W~%H_&f9?_&fMRLiht>72Ybg*TACh5yC5oX?WAv4#T38(B<$Xcq+OYo(j()gf|i^@r1Xsy%OGn{ukZ?e~W$(i{5~5u>BJ(`UfHW8!VdMr$hKIksU8%EN;iPYx{HvXF<P#C4{fwZGf-9@1nC|(T)y&o$Zcr4RjD(11^R3fJ?#o(SdM&xFk9TE(uphXThQ!9K4?G4)9Dg3eSYUMsLAi!<l_rGx#)%24HE!9<*yl_;GYN{5V_|eG4uNS3!rtRp2u0s}TDOz}?X@a2fKuQ)UkKnS*&~>hKVC6qUJW>MSh%FM1Qc4S$1v2Y&-^KtF^xz_Y!n^Kdq?ivAaU4}KjU<V~H2gNSMLzvv{m2Rsm+3J-+GpmX3c@GNvCJPTfrZh_asQS@6l3g7ak&cj>84aS7%AFzaQAv8UGRfzdl2F(uVpwDunReY&yY!&jVkei+LQ`XgM=%29Y->~Ri_-FJwA$*k({)iAZYpL)WLfEXC!eK&qIU&575H@R|@K!?jzl8Ajgz!&<@Nei{xHjuiEkgKVRMw-1*%rR+)%q@c8GZ-t2#dCNa1FNG!_T3m;OF2HXnwc^{3u!yeiSZ_R)>qj)zA*GXgdebWV;<a1N|DF0bfF89lFG}a3<EK04!P)mNx9>OI`oFu~vx=g?qrm(Kq4Y@LT8*_$_!C`|8gAYQkO7Vel~WyHX$Nzlwyg7nT0=vMu}{`t%+6Kk#C-JuEuF!OyWh0B(+!fSbd$(MRFha5=O%Tn-MP)!+c!3~dLC_IL0Mw)?}2&`a<l_$yTU?JKs0J@jQwSoBF)+OUaZzBHk4MLWXX;GyV1cqsfP+5vtO9>Tu5vcD(c#^?}u2>FevkMv&!Lik_$Rr>E=LikH`G5jUG5FG%E_H%G^w)??N(b{lRxE5Ltt_7Dx18`ZmCfW?H3BQE)hei83coExu;RWbd@B;V?RQl};wuSGbPr{<*VQIrgj``Avz7=f`H-S5%ufiSSfoMB;Al!j{HfDe2;f81jxC8kO=~L-HdEWLioFDxXmJt3NZz23SJQ3{&i#Bm^Q?{GHezX?shjXK4;oNXqv?iPu&V{}N=Yk(c`@*7)9lU_;#_$C63wQ#25xoyzgde3ZrF|czom;@th9Sp%3DLKr)8R&NdvreB9)1;_2EPioV_yx~UkmsRv>n`zd||m~l>5Rwgs|MxO9;z-{F|`cyVr;1e!T!J_vqPRxi9y@axb18mizC5u-tPufaN~>Em-cY&%k*J;iiP}7(#e5Av_PA1fPt>=~x^?kHbe|aVQoW&~*+z$@WQdg+GbKsaTvqKX&k8wnf)F_$b?=8{rL<_oYYc=bltv&$j3no>bn*w&+(L%_rE;ar78`gyTGfo^%}FG4^qc->j#er>Ns8j`JwLJ>n>H1AH7lLEb0S?-RU@=mvNrEcM>Naeu`z%klk(5WawZ0bhVGqF=!m;Y*IPE}{Q{Ys8{zEb0)#%?RN(XhpbYES}+aHQ=hmGvtX@g6qbjIlrq3KSMMpPqeLro3Y)DeYVA~i&vMr3I}2#e{cJFv^M-aY>ulo^{q{wsedi%Rg1DrJp=3~Kv{LsI`C_;crzBm&^H|X7TcmB2ajM|bhv|GWBWDA7|w6x|IZ_Y-$#eTqC;WH8N%=0fK6G$$Qy<)+&C7`#iAbiw1b~zTePx+8?r6>f`c2g-Iy|jo5Z3~Eb5~#I=C9!qE9)vI@_XE9NdKMCX`Wy{Ybr95yBPF%5Vkv3G@Z{3HTMX9$b&IUSU5{uhxWcOY|wYC0rh@0+)xMMC-%#DNDFnBd;%an$&+}pwyklU9QIlmqcby>L2-@Db|ZU1`qASzdB(5(*4g9IDc6pHc;dLSV6N!>D1qs^2Pp>zoa-t{?@eT{{Zei?1}'

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
