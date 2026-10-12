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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_002.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_002.stl', 'source_sha256': '09e79f4e812dbbaa71858777223170f0ac776229f7cb55d7471d1899c545e815', 'input_faces': 874, 'input_vertices': 463, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20501676201820374, -0.3685324192047119, 0.12891516089439392], [-0.048736006021499634, 0.16138653457164764, 0.23390667140483856]]}
GEOMETRY_BASE85 = 'c$}r22T)X5_w6sB2xbxEh_*S40YwnC5kvt4=B$khiUGtN5L?V*z#I^56j2PAQ9-4_04O+yaSUT<11gS=I%62eFt5*9tB3A?y;t?>J*#%DU+?eCzWeO6?>V<`Q(u6;O%X>0|7t3ESJL;rY^*54N-B=Z^q|R8Lq-KnX%;$ZmX%Ug`o%w!uItgSd%z$oWx6t_{^+17qbApPSJn3jZd<>Js(x_T<f)SbLq~*79vvk7K7kXa1R4EP#s*FbGJbC0(xz1tRjY<gRC87TkN=7rQ&4|ze>q*`GAlseQRY_ficr<Wa?-Cqyjc1*J}%O)4X}}Z-FsV$@rGUnIl`}XOObx<+uG8vsrOj=6(4`;SKVzQ{mO=`7#|S}e^fQZ@0=$6s$E0UrT;`tj6c6q`ZdEc<aqtjGnZxjk~<LR;e9z?cd!ofc^f1B>e+3Or>?B@>#EH|KK65QUDX8{M_X~M^c#*ZJtyO~K>lj4{?f0DX^J>~a^!gR1ApYxso<RXeD&K}O27W0m&`~1&K~(VIN`dzBH*{rlW`1bB@w^=>a#MR@2;qS?(1wBzu=zqtJB)T-|M>ct2<Yd*Hx>XP#^zP={Fo+aYp9<p)cxxEJphEiRUf-UBaYaH6<}k=HU{G`7R5^bvwL~<8>e15kJ%i{``k>y#CY#%y)W2=~rsxq+;B1%-5<e;@cI$bu)Tme8TrExn8AgWE@?qrC9fa2KeXPIW6aTZ$GYk;(_!l=T&mN);<_@h(9X*`Zs0ebya&3aowa1h*NOzlpMc02iN^)72@n_CdX?#MIrv~(bBIQ@?4JBRlNv*BVXxPS08gy)}`As_-#8NzI`#7r+R8U@{g|~{f153<ap)U6O1ogO!_q;l~S-yKj6=PcS**{NyGTj8Hlsw_9gVc)d`t*gj24(PR_5=Zy3-^#!-dYOTYf!HtE;Ro-Y0Bc?DSCfeWQyKc$O|quJ6JakQTB*BmSTh6kUp?w{jN$m<sOIWIpy(qzl{0g=+LpZI&G{9N@3{DZqlzxwPC>DO*<F8$hXZt&kpmvIc$zh=q#b*U!(+GeK^C+vgtYhRX@e&yOe=~o9FL;R>Bh_mYq#-He)BgdD`Jub(`50HLM<Ptev$v7qbs{7&cy82y@5dWJ_`qc^T;J>#~`qgchVf>y@TzB_H>DLdN4gZfw>DLW(me*D99V-3WAI=x#^{QS*{QF&`UsLBT^2v_P!F|zQ`t{9fAph0fWuEH#jgY_7pNL;62-nT7hVj!|qn^!5$vDcR@`&I3E7oyvQl1<iUQ+sXQJ(O}Hk5vCk)nuSy1n$PAMUa6>sHyJf37x@ekJkqF*&clUZ6g+&Z0g+52at1xk8TD#H(@LIkzzW?QH4Sw~v*6b(2i#S2gK_{HG*lnfukQvC^+vJrC>n`ZUIGuW?)E`?_(4jMoW%r7HX9)pXQZa}aT~&81&kF$e2nt%JXVUfxHlf!>&J<xR+Q@vqXash@y6>#xDQ8rWgof80d>IIqHW3yvO_>vC-!>XW(*@&8SNe}t!nUsv{mjH9&gk32ILWBj@sxF6jEP`7STh~KxY9B<fC5q&-+Li+W}Jvm<cXeILeV=CfraFzM%QhLGvJrr?bm&-oXUMhn8=TAgE^Zl@&+=;>X#NnvJ$_a9RQ$Ov9`V@E}&YTD6pFQu8=R39ZYwCugA6E9nI{w`r^QyZMar&-B9U?q1zEl|Yx2Jaye}NmWYf}pS_Ts(Vf3#~`NxvaQi*@w9igm2m67#)0K<1<C_)?Bn>NbHtZ@H|$5;Hr`!f)F5ysIGplXZ~K1V7AcK|boxt~TnEy9D)YQxyL6nixOe1Nx!&5!`oPD&*Pyi|k8vn{eE}eomMd^U)Rb$9!*9Mm_a<+!vQxSoqa;x20eA&k6XSIUpa`Mp&=1xF6MH%OSq=CF$2Me`4V`EV7g5j{cPg>hRSb;{&^4ULJ_Awl0S8<6Y4wJHKF`u`dFDc~`lPnvH*BT~=D74<}4O9fr=vx|Fj*{+^@Jx0^R1&b1duW&Q^*%Q|Qumd17OJd=KP7d`3|mWug4dMy1)v34?l!?8v1f4_zC{!OuO{QLsvMbVpxe>xxM(d$IyQ}UYhYY(qMAGZ4$b%?o&_>Hop-w^i^{o|O2IOA&|PJ$2a(@j^TU-J?Bl6FN1=2a^T@$+k8KVM%7`+18Dj1Sl=>#4uL9{1gVqtb5(ag*^?r_!*$4L^i92Lj}H)k0VFRqz3f&#5KXOY7Ghb(olh{4cFUpWp9f;nxj&ChMmA(guA#H4$~&nQPHk`UN`7m-~Ru{xH@hIu7yuR>=6O`C8Pi%r?x+BQwRk50#`fN6qhR_1Z`9pNdBQ1#^)9etX3CT7o=1E8u*5aRKYtdp^c@Uz%cZ-#v)H_!33&{MKU*;s?%we~Llgze?k`sKeNq7X72vAG7eQtKY$TdH2D7^?Ew$P&otVuitU3%Z$mG*QX>r*O~T*uagje=1&;!smiwSSDS+VUlxZxi44Q~=AA@7yZ^*}WE~3skWz?KXFuXN4@DiE6xpB3r{6I?b%6BiTWrIAJ98=eyhDGCf6^au4rHR9nSC+dAr$9(9eu8a|GFpY@4X1;OXohQr*l*6Cr<3EoL=yM^~AZEx()r)w>$D*=O)+7a3u%vll?HhX@oqlHEvyS?v3|Go$Fn}`X1eZINv>xf7&qY!|We*QFn{`PAL<GdM<5?I2%GxpNbFj%>Dn>|N8{okBLo?PnlnEZnndHp>5O{bx^g!`VJq0>n1luoQOp18^i9S{%&=VPxupgUl<O&#dGr6+8FQPhWp4T67esn&~KNzVxN5Y82#3@2Ch4CHtPAH0j`_tWYOpUJueNYf;ipY%j@c!rdjwkhppv0YO<=KZ=X1#o~zEwK2Zj2#y%EN9P71X3+DUmT%Lvh?H+u;3#*Cviaq^!elsMUL7j`)!hh>0+0V+@vxpO21bNoSeyDw`&Nlb!N7cf<nwN{dEn|Z?3-92$F)a%5D=L`RLSL+7u{PKbJ>DOYb>_LL;W?sDe=Geu+dVi(xKFCHUQ53^?F_z$_8*QsuNFxEf9HG9K*Sl8Fa4T#hfwG8vk)in3F5o0mg5c2mm|*W2N?g`OXTx+fQ4UwTZ{9z#V@!oY;Ga{Q^B$h8u#Vs=fyXr-*Bq{{jk9S*DZbndGh;(req5Gr%Ep3Z)%PHtaJhUVcccR_m_EczDir{8+zyS(yu-Lhs;O&VSAprUo~PN_6`36>>I9n#OL$B<_phFlmGNFtV^3^SQnpE)MwH`++TMe;JTxdaoxCB-0vA%P@hkU@Lzj{^LPDz_>0CPpLaIsTV-jMxnEOI9p`EB5bTqVv6ydUOXUCQSM*zQ494@^*MGn{V)84&OHhA)|5CSHjeLAgp-+m;Lw(#<U|xQIU|k}5q7I(R;4fxx@qDY!U5Ir&)d<hAr?z9=0~R3u%$fKe9l8_y#&40xf8G(?FPn~FeP7K)9h|OUz2a6OpZC*nU8^!Oj;h>2_#?tGuPF-<r;a!F0c8^MNi2r%N6(VrUl@vY3_67Tn=e6}=<&$2<QVxL$&g<H^IA6+@he@&^D55;!)*=5-_Xc?Uhk)s@4eJbha-RPSIRr|zusjC@~;wyI4P$r{Z3o(oLS5t>vd`n^89(JoUhjIGV<{l2>-Q6nWqx%i~PO%A<xqT(EpF`Vc*W`1OKKmIDfxcV;u)~L!NxzR^R!Ib;<7ne`Esg--Druzt|mdd<Wq9=S@8FT;+;<Y_id}E34w%+2Ddc{1GqnQJ0Ls_$sXs|Iu9J!|z$@1C6m>8&~1HxN3!dcCC*(PgLXmUd&_UnN}C^AD_T^<WUXrGizb|yK#s!erk@nUvKS;{tu6~@T;7!;klx1dpxgxF2#Iq%J`bQ(-D7mNsJG>j(wotH{3@*ild){!mwXWDv9`;738_MFY@90BBk+{!?K<uyQG=dU!VM0`c*Hc$@ywqOvH6tev*Ez=Mp(yqaFi)z$@uDeeclq%*Vd;%S-row#WXEUc<s~djF$+RR+&L!H*F?rYz2>dVga-{PRBI@cojyO9<9?+HZ%^_apE;U%ET$F!v7pOPZn|9KYkbR<|+VFVAtGI<MgUcnk4Ygkb+E-4*>{_lxxF;;hl1e2z8wP45j%=Zn6~b&U59usFxH>wd<(_?)J%w*vc8Y%cuiHPBa$Zo^+M8~GovDc?UULq8#Y(~Hut@m`7NwBGA+e|e-!zrmgJiXVpe-ukncZxLtgKdp<S4&G<rUy^|5id@WB>63zWdDj*9yXpN^;9<nyyaMauc^dacelqg^(-He>wez{=e%&`${4T)vSNeGgh`;v@-Y@kZg?x5zKs`(UknhP=U9Vui4c6njwT5G#aT|v`o3DYt(L_9#7G$EIJ4PeU>R++%9ka!HU0#g&UV4oBxDLSh9*dA?IWP3d!`T*ogC6&(wp}08bKXM4vEPX2>Xo<gzTvJG{`)C-&bMZtyqt~s20GyPg7eQYuko{R-J%ib=UAW1=6=(8p+A0``@mF;Z)A&nJZ|83kRRc=?)8S)Pj-wzKVR&JIy`@l=cuW@^UVF4(5@EGdnUhrNh_=u&smdS`6meZsDH<L<@Lt+0?)JN<JC`naoygPaef^|{S~VY=#%>ovA(TRQ3tzr7@yPt`%I<A=#zDA;J44hdTlwBZSGh7J|6S6Nx{0rwn9EL#^LuYKL02+TEfrgUX@2p)Tebr%&S~u>`V1<F6;eO$n$e&tmCK^m{%Vs)Xi3n`|eO0@*i9k@k^}3zL%eYd`4D6p0;;!Uo^uxr97{I>rOv_-wR@6aE`ojK>QIs@ccGok%ix|Vvd}bPG1%Eu_+F}%SDX8kc<0ni5>D$4aRdo^kLMYL^0I!eH8lqs~h@lgDtL`JOj@U>mBjG_x^N9=2;$nWq2?Qzk>w6lYT=-C+th-dhmPw8|hc^x!TY!6@4=4mGo=M+M{kfU$iq`V7!A4eb~AN;-uzEzi!c0{H}NN67qkM3jh3yi2v;k_MbmaBA?Bj<b9}dKZ*FCj!VDk+|gdo$N1sVnAadrtoy8DvJOh{QjAX-j_1aS{jgpOBcxxybR^z)H?0N#y6L!XXhp2=NmmQMzGn>jbCn-{CrTeJ{o3XK%6aKc<Ff)WKF1foZ!X%BYwkC#`~MuTJl=`>vB);;16PNmp3RHm+<%&gI3Ic<zST8(U8N}YAH}sb=KIwj`?+=zzehM@{DX6u=J_lA8e$zITx1;#N0y+@L+c@*TaRUY-QcoV$H`7uFP@t^*M-P`nIr13I~e!Z%Sjj?Qx5*&%dx(34wzSRQTV-ba9;F#hW#+b8hNg7i2a}6-?i^wCCj>P>wx>6zpp8+uSvh@+*J0SL;hZurC;~<G0wa6Sk$M_1?gAZhv9s*+YJBU4C&YAjzE2?%|ic#q#=I(5uER(_#TFS)jhlq(Ox_X|I8Ec=ZE9Iwrj!fkBNxyYK{JM2t=L<yQE*Q_~X2A9F6r#+ln|1gK&Qxf1PXYH@r?pKK%Y=@+-B}=qr8?`Y+CoT{vIDZ=r8%hvT{(D@ng@m?p>Eui2>Q^Qww}Z!iMa{WJs5OX)6o=6<cSEBY<j1J|9~UHa87)p7rZhr++23$AN=Z+6-V`5$SEJXZx`e_LFc-&0y+{G4FaIdvTBrf&&<-COV{+(VvO&hU5GjQ;6U9&vtci288fQ=U&oJ`d|*zCHFK|KT&S?jM{mFFvno<M&|vx2o`e55~UnZ+GNhq5|eSeGKaMgXgJ(1L6-$;5pt2ajKTVd|Nlc_njw$^347EJ6`CYp4k}RQDI-D;d?<;FRYi(_k(g>Y)7JR58c6ad;BB)+PO*C$2^%Q{pyds5WnUJ)U)4b#NqGDn&Fx7FMEPGi?VUuwT{T=&`s%AIv=tepK?w5RZG{SpYJ)~KD~Gu*PXK&_pj;s_O}f9`5s2UG6H_P!_sfsuauVU_&gjd{W`}9*w6D0As_F}$baoLtm8{OZ)*pyMn2y4aK8s6!ymE?af<IkKilG*RkT{nH|-P7aX$B&{2K4a$p6eq%xm>*#4){}8TD7Lh5zeOzR#I}>&8um|JXLnt9Yb^U-i)i@lD^OkB`T^YSu>oMBK#s-WY*=u9in1{yYb9?hb`N>K^vP8wU7a_Q$+_<je6&>E_7u-|mP%e=hDLJ`Zb4b%npfD(o}<6_HP!j_}8wMV|4WFy6fl@}JOG##jC6hVh+Rp-=d{WO_fK^=*zg{9dC}#q)!rsgHj66~7mleqYvx)<i$#_QSbz3(u1#zs`Lg?^Ap~QWjOl_#}7qq3Qc<Y#I1l1@P|~+_;}8$aD9<sM~8k4?KT=K+em>O1>Xc-{^wzZ~l;e)B8I8{1fPhE>|%AQ39SDO}`KJzbO6Mcsm(KH+LK2L><HU0)F4wJ{11tho#@}<tLoWBle;`TlPu6`bh_TKjC{?Wp4t;_eny(`SI^t?yo*z(YGp$*Z#f?`P|-vJbOJw-RvU~Ke`$AZPW91<(Y_cJqF{qO}F%iw?X~=x}zUzOvAk5c4PdSW|&vAFvRbI=TX&RcjP~082o%r(`|Z)@goN#j_G|!FF(W&?<@VvwE4K-`F9b@>aNnS+jblN-`1cGn>u5B?i$=jw;p4@2R-0-*k^H{Dg|}me}eCU+8(~}M;7dtd1`Lsxg}sD&Yf%7(y!OOL*ItoMxM7XO1~~)C-zCcKUcn|NWap$4dOiZMEsIRq+ey-0(IlQtu3Dnf2mo>Gi)j9Q)@5cdw0dT^ZOmlYwaBA|L@#cI3IPmItt@o<L`ge1NY~e`!!`Aq7O4(T8vjkm&5yE_v#q`V3_o4*JoPpV{P0qepz{(v+WikPG=X)_w!4O=S(H0BI?HXJcj5<j880ud^$bNw770^an#?T9O@ZT9QDlou}}K>`?6-O5BwD$OTYd+zK<&-OTl0FH|bX<7r}Z(<stueH>6+JqBZXK#q)68NoO(MfPGj$_D`();^We<HT|Aqn%A+N@V_tM-`k8t{6Cf>pXBkF*IT?_(zcj{{3mR;$X`1k5dM+3(9freB7X1?#OHf^b*c@&*Yt$HL=(huYm4#gd@-*IA5k|x4{PJSq+itv-yhZM|3Uq;Tr9_%&i4*QrC(FD0>;0wL!M90C&@gIwTAz}YK-r_3I3~}&=02lEpQF|Zd>>skNfJ2A<}QCG#GWBdK&pR_DnLrfAtv(-&=N&e*Kpp@b`O!@o)axE9=la1@XmmLV(3z3GZ}V7CW<{@rm7N_KKqt9BB3@!on&3ne>1EC&D2v|5tw^+}73Q|MyRXI~#NO)o7cjWv#$Mn~^6Ob)M0t8SN*dJu&*;DbTazcjTXqcAmPQdX~JOyo4q=f%=4;K+d5FF3xL;YZs>pZf~?Ost@%ivJbgBRpeKlp9Ozm&OejCkRO@N;So*nO`~0*rcuw6)5x*Z{p48kWa<*~Wby!-;4o?eIgGrBnnPYhK5DezsBft`<Q&%QEk6rx&bqZHHz#Y%>ZqX!jy2kG>PBi9c_Vo|)rUNu+=*J9+=*O`Dr#Mgp9Ozo{U4FPk)Kj;lAn_AnytrOn&8VuJ4QW0y+S@g-b+m*?<Fs%#*&wlgQ=6r!DL_R0J1N+D@|};Y8bgMc?@+Cc?>y%dXyYNPBL5XB%0t~jP@_Jm=*LlvM|9_sBg(a#oAY)3GPGHko%A~QDe!Q$f;)ikxCPM)@T=ucF1T)X@U<>&yo+2_fe0N_mLB+8_9{}DC&4}6nP-E6L}!ng<6g5LUy2vK6Bt_!GEy#o|69{KcL<vKOkpOFO###r_FltG)?d>qphcIrye73C&yDykmJc4sC&s9$dT0L<Vf;ZYA|^$xewKs+=twY+Lhdk97Gd5g4&lnf;^5ohCGfug&IMgLS9KtBCjN$q5eWXL(Vtr^?aIOd*iw_v4Ym53V%(07Tky`?uSM+!5yhp$W_?)9chA>Qa6#8l21}o$tTI_)U)KX?E7?@;7imC<V)l$M!QPQrd}Xtlh09)lFyNM(*$p$9w2WcZ=miYZy>LxCX!c^7gD3h3(3Q&1Ife59jGqk4rC{)1KElEgZG}e$9~WR-={tx-zT4>W|2>lcTi80caT?8cac|<qs;EZD4O8eM$=N`sO!mb<P_?5atb+_8c$9pZ>DY_Zzj*BMv~`}M^nd=N0S4neaHdi9@Jjs9^_HfAo3`(mKMbM2^~S6O^%|DGpo-y)=%gZvwBWpy@jqctN%)_kI*w_>ve|fDKy_~eFguZ+FKR&gFXAjbf260rwRK@XlJv2>&$)>+SjZ<`?7z92AcJAAp2eDG_(Gn#`{C)JhS^{9`C2!)JW<)awIvJI*A-io@ul#R4sK9SxcTwokpI<{3g=`_ontG_a=K%JCi-hZKzGiLTi%Sklm?`$nNAZ)Q)7KOUYx%`>7|%`^l%N>13go$fwC!)GOpHa;{b3o|sF`Bj=L!)J(FTypy_xyoL4MNfW%BI+;9~bzDvpJc{Z`9!2)2wjsA+z5Ho{S5e21$FMG|Xo8cdr^%-||0J5=Q`B5?F6ViQCU^&RCwV95u!A~^yo0=s>QDA(PV1;i<Ro50@Cl<GG+Ht>ft*a<MO{MPMUJ2jAxDr0(FA)KO+{5xhmh6eAnFow5P2mvfxMC&M?FZ6rp8kblH<vHsVB&L$;XU#hI)~Df_#yjK}{xSkdIJzk&lqqP$S4|$RX50<Ph>On&56!4{|rMvsoRTX@V;l&5Bxvsv?&mH>Ik{P07C0AhIucEOjM$EO|aPj%=#?e45}1Msub1qeheaktb5)$rH(osC&ta$Xlt$$Xm&K%+_xYP4Ho(rBKgP&ydfPFH<j)FOzeq8RQ&t8ubV{jl7<^hP<9Ul^Q~xN*+xeMjlO`P7@qX?M4nKkEA-2N0Pm%70BM?dRB$~QI96LywTn((BG+6WMP6oQ_GNr39d?CQ*u>u3#u=<1=))_mh43yOr1{_I)OZx>}OTjPl9VuOHf_OCCIN8nBYID{m8-u*QReGxi+~ibrHEOIe@yA96+8z-9w&2UQ0bpUQ6C=RoIuCX@a*~;dw*oIckbk;q$-XZ0dQd!tV=$uTn3QuafhqIpjQYCN+(mN!~(TPu@bFNu5fbNe-rtwkmx75gbXKZdLfaG~KH3`^$9BPiQ!KJ9#s8q*;ANvVKCn&FbmRdJC;*R{wfjAED*V)~h_%)71B-^%X4E|4-@*s_?&{3I0g^o&1sfH}y05Z?c^gRNNbOG{F_AEyxwgwWwa?TIAN$!DOL+WYhi7n(9cNX1wkSqfIc{PNPjS+8XKv@&t}qLleA}I*q)Qyp$$*Dot>AnqV*L1hN;oCv_6pj~Yl598H}>p2WPPX@bvD*O1SVQ>k0YSE(1MTgh8FhYQrH<O}3eM%zQ}Pn}BcPj;tvC%cndQ@zNo$!^r1WYhfJXoB0(1dpdqCyys@qX|Al6TFJ*NA_b)SJ4C?phlCUS-S%?!Oy6vWK$iV(FA{>ULap!jXux>|7BLkzi5IBjP}@QMUB0Akt%!_X@VC}_mCHmeW?A(K4cfFJK2ToOl?heCby)zk=<DLmNda_Xo9_|<H_D+4NdSe>NfH+vYsaRI`t6wI{6ZH6?qlc;}T8q8|pLi8*(Wt=m)Ye!KJBxk^f>%OS9gh?xksht*K&dtod2+Cz{}wG{M<Mi=ie`ACnWw>!=sW>&PM01>_L2n(9MVlUq?;$gRjtsm|o4<mS|t<d$5^<}|@AsNUoj<hC@yU8oxJVCqb&hCGvekh+X~kbHxxC;v_TNYyKa=ZN4J)ay#&xg*&0+#>ij^^#KfoFiB~`v`rb6g~?Hu0buu^Pv>iz6Px{&y3Psd(-*h$n(dMe$#nm&GSmA=nvERCD@MoQYk#|UMhuW;!Do^2KgX0+pKQctgETdX0rZ5!>KW3p^4;h@+_L*8Ps*;8RXv75OQy_D^*Q)B{!qCA~z#9rZy!vCO4rrCkt&szGt*@#=87NtxpyvxH5fR$d$=%M$0vhxns2N)URZrjjh1n$qkLxliG{gnB0pzfZB>YfIO7yMjlEYN9{r$M-HV4?n<ps?n<shEk~|HE<zP`DZ<Z!uh9hWrU~9+w8hkP>OFEg*+Bh=Y#`gP)}p31tgRc_jdQl4HYN-G%Kz4e{E#L%gL;RYLEcEsC9kFCQFF<;T(dlyV1;Wb)=Z%ZZeX^q4QPUU7;P4H2DK-726;BM7kM^$E_DETE_pF^D0wk?1$7*G1v!QqN{%5fqX`~C?Mfa&Zbz*{Zbz;}EkdqDe#Kr9{qc$>_&9Yp`8atVO>ii63ptcL+^n~T(**Z3+Cb`j>SFSI@;+)hIh{SXk0v;iDtaiBp9SBdihjC96MUGOK|V}gNZm+YNFGKLJjkr)22qEQ2a!9{1h+R@H|j*{5b{K_j=GktBj2Xxk@MKUxA|GHEqk~D*_K?F+Jjt|+}*6FyVC^Ep$XPeXOL&Gr*+i1<hkr!9d!kH1$$IST}IZC7f?r#7m)i?+mZW|TT&~LTarssMUR%`XTi^Df{##-laG++Q0I~7kVn!452c2Zhm!rN!^!^S4%B|+4rC9rUiY90?xf&%D50aN1C_$xtpv}d&Q}V5=Mub`x=$(mT}*H?HB%}49Zhfw^_EijyPM!R>S3kucRImZ>O!UPH!s1XsKb=P-^B!*emfKFNgYHM+L7FYYWfY%lk@iEm`=2gtdr38W_4@Nx|;4QQ=Pk+twlGp_3Fm;6gtsteJ3h~>n`{RRi_m8iQwnd+hn2Q9y9frE&I-v_n4^<>#|Sl@*XqwZFlx{ciwNNKA*$;U=HsS!Q!_D@w<We{h)~PT6RV&N)v2PEk(8`m!_5@mnJ(<9mx*liquNvisUNPs^lu<YE&n3HF6EAid=(Si&~ppi(HplpIn#Rz-W!A4XO3X4axOrg6mLglk1RcQdQ)d<myx>a&_`g)T-p4$d##;$d$<zsE*_c<nq*V<nrXQ)KcWK<PuanatX36wFudkY^~s*P%CN?<-f-n$u`uYWE*lZn&9G8dvbAdNor|wNpcyg13AFo%G%N9|MY+DTKG@=MyOc)AHDw1|I+f$J<b2idd3I)|Ni(hz`v+1CT=ail-w1&s`9@8Ic@Wi'

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
