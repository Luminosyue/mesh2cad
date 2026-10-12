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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/86670b8918b3487092e86a60ab5b641c/part_000.stl', 'relative_path': '86670b8918b3487092e86a60ab5b641c/part_000.stl', 'source_sha256': 'd1a71d38fc6a912951150a3d4bed98122766537bf8fa89055c27cfd594ad075a', 'input_faces': 906, 'input_vertices': 588, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14129602909088135, -0.1962238848209381, -0.060101769864559174], [0.14128831028938293, 0.47903040051460266, 0.10772213339805603]]}
GEOMETRY_BASE85 = 'c$}r31ymQ=-~R{fMG@ETQ82L97JDoZ3v5x*FLtbo7;B+pV4%1*3dX3Ih+U}Y7}(f~VvXJ1{ct~@H~Zsz_xC^Nf1bxZ_q<=cx!k#P=l0w=>)SL<+8hf1E27-+Sm|L@Qxp+0D>;<mJ%fh!?cQ@pxq*Qr9TXSx#lIAt+oElAUq1(BxH7s#kDf!i2bHLymZ;UsqeL0CM6W?XLxTbab{!Pdqo?pa1O6P+Gua=~Cm^tA^3Nr!czBdiE4i0ZgVq1#zu!b2e&jrKAX#iL&tIvVtXf>ySn;!U;?_a(zeSU;pAK#ye%7v?Cf`~y@{;gPZPFzA{ghbpjYqXElV8Sjf>2xONcMM}N)$gUZ#M^vpY<+b<f|KcQ~GANW<yA4kK^llMRWWL<2-~KnMbi-W-q7THi*(Uy9aW9s`*_MKdUSHO(%a(FOHukFQsqg&8XA;y{pObtMuUXtC*uH|G{n?|471B`gwxu7`opAuAI*q+sL<kigu*m|8U^@3U%OgV#`mV`+fJ(r1<%MQa+Uv5C5ioJ$XjHb-4!T|6SNDN^i<j@{JpzT+St&!|3mNJY+w&%LV%T4bx`O-~HIf>6bcsjqazFTVMKpmT2~8UcbiAtMW+t`{heHojl{nw{q%}>GuT|as0<6={f38CQyEilOg2WDttIc*9$HZOuF2U(^;{M{fSZi52W@#rKR-E9bISBbw-qBzu5!Izfv(B<=+U;#O2WWbQ1YHqUgEnRWq_ba2okWt?!|v)1MzWK=ok3I*RA9p&MOy`^5uX&JpLS9C}q6M_TMK`L^b_IDPNF!|3l9Y-PV-Tgt!D&80)#RKAtuMDeu~OXgB}o`~Y>=C8Pc?&s%@KzhE$2=+TxUBvhGs65^0_m<>qUUv^uIW(T$ihf_ihkUb0*JG4^)35;g{rWnbPVw$bDg8NFN2m79I@wIR-jW9#|6(!rw|SqWbVeBi=ssGg<m=@p?xuX7cOOZ=@BU^#`3dc}(9fH*@pE5rk9@P;&C}!;cs7{)0lUao^u%hE@2x$G(RK4jv7dd@s?^U>xfDsh=G*%${e8!DR6gp2sT}|FxM6f(g)dP3QGQGy-zeRm>VrOQ{&>26^dRyrGaWrg^U1Lwx~~Ho=hGwGAxgKX&qUG@9(-TlBKJ}GJY7lkM0r<{^Rw`3Jf*+&Af<2ID!}nej^9D)*LX$sQ}fBp@q^l)pr41Xq4bqT4xIm^dFIgdGC0g6f8gUd@|$PaNb#H3n@_qtiG1tibFM!RAI|6NCX#Oy8E~EQGb4)n0p0Hc`Pws2Du3O3WeB(Tg`ED-u8T-7Jt;;0?;#xj)%7zJ|8o<HuaD@<@xO=8qjEw!waN#uAKYL$mCw8t3n-n5e~_>GN1sbwKGqL+^7R@kV(I6_mlsn0N4W8IyLF^`Xb$(AN9j~3!0|s6*+%i5rZ1-Z?%_<nxhvNZeoh6coYmVI$+wm7b}{w+s$n1YQTb?}=(+3dn^6C3G<re4QnJ5J+QXOnL#^X}_QM8oKM>WB+KqCm5BquAQv0`M%})1g4Q#@Giwf&Vm+h;P+Sdnm*h%r<f2DHLC+25=*mbH`TJ4|9DE)(ZIGrz7Hc|YJ?^clh%*p<O)2peRHa8qY>4)9fOMa<m;dGzRgO`wcUL#)%`F@bnud*_duIsyu<12>^sz({G@%WW7oP4wEeyY#f+>`WNtO{ev*LO7F_TDh>YSNkQ**|=R+Pn4U68XBP52sUIr+TjTTgvH7Y{u6e-Jb5p>@k$o+E9u8z~i&2zC5}>&)wFuG^fA!=zjV+x@#20znqVJb@)80=f)Q|N?*&Ah12O=eJfqxKXViMefEoc$p83lGd=${AE?|+&v^Eg#a*Zzykn_+v|ZcD*EW8le!zCQJLOaFxtx5x{BbG=+q9kQDL(}lk#F0U{{}rjKNo7pikHsm5Bi<T#e7tkR0-_O>GZ9Afc&jzsD5cNJve@|d(m`%m{+KU+Hm~Q9k!;vuGZ3%{q_BKk#-vC%h#<*z8QL&#<!GyHO1HF963tmGSiXjp>n7SUpMnoZYQ1El5f>2&%SF2*VBoQ8&Q6(Z0!H~xsuAWd0B3!i!yOJINGQjw5-{<Kb-U~mfO4QPAccdKdIl)KHMc=>s6V?FQZ)PwRHW!o9v&jcQ|$aE$cM<+h?BSe4I1r?^^DQ<#H>$kkYRk5kdK>y_&DvzcST}lySl8Gy&<j^L!y;B>A>Q<H$Ew22uXa*^&L|?<V!-^b0v{qx*Y*h@Ok>P%rlPWZ{0hdvO}C%u!v~4?oV&yT21XFFmj|Uw2<V>Q}9WS*V<~UX3}Q=3J^*R^^S<-z%MKbNo4(XdE~9FQN3TE7dsu?@i+AIw}1OeC6}b$@KgyE~E0XeidT>+2%v3%R$?ni~TmaHd1}-)_|U)RWd!NzvctAJM&Y2%8yy-+ivm`ic>vQO6TQ#j=n^`G9cIL)a7qHJIwxxT%_tmf1Xbs3TOZKl}AYr*Q-f>?K$L|`W>Ec<bOfssaKl9evgYsD4oc5V=143lQ^Bm%L1vKPU_S@s8Peo*KVYzdS%n{$58q?dU1TE%QCu;m_<}RHpQ3kD~~sit2NxhI6uwV_szDQuK(>Z_e-Oja5`geb36BFLhV;QoQ3_XPSnq&^tal_U(`NR`T@173+2Z)_$#;D6C01&l|$$I<eNVyaXq=Yp2|UsxWoPrFDf_f$OI|}Bk>le?~#e>ztMd$m&2?p?C)>P>j}&&Y#;ZqAGe;zsVhF*4^-YwzIH#6`Uk6OP&B2}dp+mV&710ldHx*DHx&P6oX)w7G%r`aWuS5}qq=eYC)y6m&*ZF2Qv1rKudC?y4gco$lHkpL3#V|p{_DxyA3Axl?;1h<fIcCF@~=A7;(TW4&E*zUips%Or#i<^s!#K2tJv4|6fd?C`L?kZuOm+U#`DTm1v#Ic-_rPH#x>ha*S(vM{UR|mFH=Lq7o_%;jTvZsQED}&aY6OZ$-Ym2x-VnyL2B>Hm^aklDNC=?I!F1^fadjj>`U_X8J(%Un;tXxx|N@B{9QxVQ2w{iqjA6*{E+?FKd4^m-HuQ_GJ0Pp-y9vw?PXXl9*-gtIDXLOO_ZOP9&}x$bv$2p?HcaCXO-jmOwe-nQ~HzeNGfOJ?kw`P#8U_PxugqE?W?tCQa_o}Zz$fwIGq6l@%+=Qr1+DAI6se<@wy1*pagYhKfFHm8~Ty`8}0npXQ@7`O^Q={F*f<J|Fa#{D{V+Cd;ix$ZYO;nP&&3%EjT|T7EpYp!7eISy>(5F@86Ef)9PP+b826|zJmHa?VC6Gwlh^Ye(s&L?lB6TpmNh9e^R<;y}evNzq(NQm{-5?_4+QNc53tU<9eIx3+H>#P-@p|Xddo2>RLNEp2g!1_BV_%H_6xgh4H+#QEx8KPl=qqKAOjW#}`x%de8-qU;H?$$N9~ipPd}v?K?e3#r@LK)V}Vqo734=p2lBW-AIlfvX$p8YvXBr(1XJGeh(ez^-<6$nxCp&{^I!e-}CxOb>{NVHHhQCO`>*cHEb|5wQpHpc%JaEHLb60v-@&>_O_;aXghzO+g;`!oc`Tl8n4Zhe{wk->BRoJ=ahfrSaE8{ilZO<wWiVfN9pUu_2fl;_7_*+=UBfU-|xL@oX?`S={c$&7jyZjRmfMbKBay`S(cCDD{V?}{N3xRJk89XIsGHKIQ=ZWc%R^*7w4zQYZ^ban*~phmM=RqwXdK4o5p2jLsPmh?b;*upWWeoqqR*a9ews~@|D2;w9lfi{zdJ`mN|+2MoCoPtbJz|r1rIPhj^dKO<ijjf1p9_&h&7kdSV?p&;Hs4i&8(w6kn@3jm8Bv_z~T&=6IIlU(ZkDvKe%P$JsvH$hRg0@IKOlM?8*qS<B<-k2rq5iKCaM_O-bkC><rB{+86fGAoSR>C&&<9!n4A@|m)S@3+fQ&d=)p?3an<{DfCoY3J7}$mvf{%k#|KosiBiZm07q^S;H|R-7O2PRFU9Y&}fnX<p02@jo8t=Xzs2$IqRM{Q{2MUp}0{`9GV5^Z&!3`mZJg^1e%zw=|D5OE2be{M$R~m(;%Z*&p1O`g66+8ybI=uGiSF`-$Qkzn7=`Qs<l^U+EM?<!j~L%<cW`MD_#Rd7achk@BN%=|;Yuza))2O4gygZY$D?<L?dU{i=59X?~|Bd6TaNe4+ZIZ*?Qz8lrOiOo3FMMzvDpn=kXR-(v^wKcauIrFp)UpKm3e&%AQs`S6yjyiPlim&@mM5lTnz8qeeF;|Qvswz&LT?0ny<Bj~w1Wv2A?qyy}C@#cMu23dGKEjp2Wy>sN|)ak3QnzDc0pZa<0{Bw%0IF}^fs(O{$yEShS)e~!KQS#L`(X^kS^_WWKZ#$Z_h4PoR3)OR@!AkBg$6g>`|51$UgYALA*R6JveCtfDn-o8>=T!2iEhJxiGl%+B{l)-pk6)&cZ?x!2@fF`%9q9gCOOdaHwx#E5%)Nkhp);qmEi?Bg*9+5riMdbV{M_SxO7qJ%if>fo^{|;+<N01}Z7NT#>}&QrPNe6nJt#%#sIOyq{*kThvDChjwGsJ>Uno5<b*RsFx{qP*?B9r`aojxTNAZod`8l1@`*@x_r!MW2=}TSs=jjEh{u_(?QU7NCx<&ICWtJDsAM`v|DgRpSaQ2I~q4|~WoM7+oYRc_mtOMu2b2;+$34!!nj4IK5-Q5}3uY-2mG%Md%?_xCWDdi4wJBr^+@vS?B$=5!-N}zHd7tZt5giPccZ`W}>+3}v|;W-mxD87@*``nJPl#c3jD2CH-M$bzR-p2cd3FA2a(1S-(`$k0L7;eA!cG2IjUCHh4c`o+*^f_jiPQ?BVoSzV?Kc=~i_rskwl5aJS<8kfHW1eq5pTY6(w6LqsMrB`)e`+h&!+r<-=|1iap!uo3BtOrWmO69$bsWv}?$EwepHuonWy?ZZZ<r^uQhl?P8&CDzsG5V<A(tj`dvE=o?oV5jW*xU*i|fTKllm?F+^V${-&Td!J7)@0d~5ID<m)p`-e<UzCzjit!oICG&!ZBvkgqSfzlQQt=LPRmEq+h+O?AFRzVf(35Iy%Ut7+d(wXImg`RK>*G45XE_4=BgoX(X9dXC!jMeO%;Wq+?T&#SNUez|S!b)N6O*m^9rZ_bS;Uzw9Y^;r$B&HII4*O6}w-N)sR_dB*@k7>Q3m5rx*sO5F%dYEoG`AVjIyv~_3iR(|f*eEKO9QEk=TA`zO+;LgR{<n2hA8gGJaeZjtiF|!<bsp!kY^HXt-n_#5J}wn*k&pLx#`O0qD1OGNySSeGqIRS&c($DUc4y+~@B0noe(69M`C5WE)f2PmJ?<w*XyhA5D$xDf7B#1RQQM`w<g1aFxISZFT|Mc{=~Q@6`<7<e`IKKH`UUTA=Jca{ro11qefOdDzg8-dpL?4|G|w?^zm25lb$tuB>tpwMem-a<`MUc{9!H)X+(Yp@b|+ssF_NE~l8Jo1LN$)R<2m>LftmMGdZ&&@P&~JHw9YkuYee->IT*+O+EA{aS6)*(R!1N5^<_)A-#9d%eC5|O8t1grm#Ds(fwlR%R}PS`wl=t3yRGN>Ud&t`7k#~`9_oMR-DBrt|3r^C#q)w*o;?5i{($ReLN1E09-7bX&DEFY?fSsEJP*&2ME9fY|HA9sGnF`<h_>Xbr%Up4?CeC((JXv^0r?GYk*^wqX}zvEY$o64IfkB>?h*JGl|!9d^C|t>$EZI|Y42+A=ed+`^$yPqgFkb>mwWge@&}gSek8sE_w!8`(f+dTJf7;ImSz>zXQRvr^0i9kxE^+W&-M0bCiYj{<Nfe<v$%dPx;vBnhUcjM=<BNT{K3ItI{CX|xIMNl$n*0)UeoA)cQ>GNvl`u`eFN?O$|+PoFBax@opV3WhtqDM{X1K!2kfVRPwQ)QNqzE-6%kZE%9o<_{>T_n?%aNn-iuG%{|8RkW9O&oOwZk_7-Hw^<DT$-;FV}QUzxSZOkHpP@yD&)$MtTIov$DG#Ovmmx%NKVi!G*weL4+?a{uQQX@A{(kEy;`Ig(=S{Lh|LKaD&7_Wsed{9X;?!ash_NUA5M)0$m&`T4Y+=f|JM?6mXE5A?I5?c8DK_v=XYME~q+=bP@XR8Oq<Zrknr0=KB1q|7(|DgV1?xSn7=p5hz#>hO9W??L|YZ3VbpU>%y`+gd!~elKp%{M5cWXf4$TTd4*7zI9a_Qn{YkvK*dV_rKID<LWXxM<CZj%fG?2y8or#TE=@?zy7QKn;H0dNbSWeKAe52eOW#$$d}urE!)sJ+`rhjUuC=l<@aChz5XNKkCgfc<7*7BgQfmN$#<4~x&Kk;wdVI{Qh%jqy-L2^ziG$#y_Vb`>ivA^J-yt2Dr;u*`+KP${>PX4VfD)s^5uSBZQGpo*X41++PjzEdr0Gm9)Fa5Y24AuRN?o5(m18H2_Rn{*UUbDaeQeUR6g?fERUyp*|+@uK^lLpqj>Kjjn~@wJmkycyFRQg`SN_g+BbvKk>(G!ahLc#^lN{9A6MZz?*q(z%I{sJd5Dqa3%}o!<}KE>%RIix^PDyvsh-L6BAcVZ^DSxKrG8q=^Jr=Qrq1SlTzS5yu1ezfsM7pUJCmN~WwyFyD4mq|(MIp0<jeC+ZB-BUrFp6Dznpw|9;-WDBwwEQruatp04~p;dAVF7?s59k{8_2|i}zWj`L+@}ljbAx{M^=x=PB}hUWsz#_wLgC->j6K{C}+%DlOsn5Ayor*GPU}Dy>I!>rdKWk=HNkt~PxBMq2M!;c?{4>nZ(7PTqf&)?ZeE=Il%BHQgM-?|<%P;dCN@@cS~KNxY9Gt^2GD2g#S$iP{r)-Y=Kdr^b%-ye}fHXU&GW$+sr8<mXr@JGURdvK(Jp7b`UukT0*V|M8{uwKe`8`_ejHE$G7gG19tTDUqM|-KBj1<$XyWPo#YV)z^!Cd7oim45uUQOIXpbc)XYQF?RAkqP*{+WOU~CEbX6IH9~nkA??HH85VMUY2QX0ahmtlq<tRSkMsOIq<tZ+d<(7@(tea>OkiK$zw$f4&q3PnvThz>U)neO$Cvlb-X`(*EbYIk1M>0yhqRBUz2)+d_x+3x-sH>sgvKA;cpfe7HySRdI2~!<(suJI*V7tj?e;m9zj(f2cA06nU#hgoLeF1|Zfv)|YRu2c^+MW@HS^_XU)sO5nztg~{1iv&r0n+^^E+~UX@A&s>(BnkD7$^;6yI!{%Wj|9S{F#Z62HrCzgoGuhSLd~X15=n;>-KtDZacPZs=$Dx+C-1?Zev|oagxRetx=3oW8W5uS~zj@ul|yM)Mn-&*DSv-Y=y1X8!|r?-x{;+nkQ{p2BGVh|`hYYghqq*+1by`|T<3M^bzxWQyJU5#vH}p7%-bU(A4N+%Lu)vwM%D>m9gXk=_R>E`51jIJJP?`zCYVKu+gY4ZHVNdi%lLA4~78tk*L*Khk?KGwwF|@_RkC{Ws1}ma2B|2la<eJl>`^sT@+y$tV|UurIxrRLlACx<z{LsRhj9d4%+S*7n-q_`!$m-<!kN(&V;#|Eqbd<LmZLPw%aiHfih7-+R1dUwVJ7yB4HzPJW+mjH}81gv6tE*KOuazBwqw?)|>et__dpSkI=Mi!hw8u%B4Z?mUB)=MJZH_8sLv<y?gI>I?g`f3rVdG1iCYJ8eDf&U;u}CbR!@o!vPTtzJ0Kr{>hOKd(~eDEDj9`4-#QLOkE;Y}lQ*QS;Q`dH0H(cIS3%Y5H<}>3orudmOKKrSnL(r16~2A8vN%myErucwbXG?_|8ZLB6@KwB30sEzLWQFP+QMbMt&(KF4L-`v=eWrSo9wRO~-R#oL`XGtM?*Upk*=mhQpnNax)2#S8hm@;SOW7qHHd&hJg(^@@DnPj8cteEEE!F?%`3m(D#}V{+2@OZi--_QIQe={%=;<T?A&c~RS$PvpzzOLhN@wBC@<qiUaAdEG0WcQxyj;e7|`e5~&92d`VC^R&vRKIF^ia?M$jIDP3Hud*tF<ICrMub$`l(m7$(KaqU-T(MO+iTr<^Lw^2<)0fUI8;2F@zvOey+AL@8*Q9gNM&ZKb%jc-|!4)~aeD3;VHI6Tx)7I)}e2z^z*KN8F;`x?z4qT}dLcV-%+*GD={-tx~daFpzk9;mYVkO6y&#^z>$-Z>%T~B<#`IOGdt5NUxzNB;YT0&tuKPsQYS6db1bEVR`ebv1V`SSVy6kk67ukUWbzVsb|Ho7JG@^=STp%I+E^qqp~6~(^%T|<to<jdbjr1<jp5qht9jxT*@VSKnu{=dG<`0Y7gSN@LULk7A}`MVFLeJ1v$??h~i%8@UBSE2;?u`hj}Vmrj`S^hpn2@T=$mA`YjzL0$RyBN#1l+%&Eqp_V{&+(=2ZnQ%C*_Xc4(Oe&LI?{JNs@GHYrSE`jYoBpBNZ$?VTR(F8(sxGIJ_kBqE`OJ#UoT3&{2i0Jv>5sFcTf7(n&ivhNvWfHaeV2!D#bOB<4fORS*J#FeCfL_rR6yGrSH7Vf?=Fb>ANuFX$0Sw^c|V$8Oy%(-I>1dH0MY9PEDP5i?1tx*S0SwpD$1S9h|S-*L{^&y)XH>RC14#95N|6lwJX;KJ62x_?M#p{nNg_mH)p!?W<nC>i_lAzPyf#;*=b6Lo<Vg<^bmg7l!5p7lRgr<^&f6J3}*qox$m$>A>m1j!*^c2>#~4`q6<|1i@dR@4#QcpP{e8pTX~;FTn4?Z=lb>Z@@3155X_NPoWn0Dfj_`;2Y5E;2Yoz&}-le;8V~<@G0<d=tb~x@CoQu@Coo4=w<L3@M-9N@M&-ybPG5Rya~Djya~J<`Zstvcqa5O@J#Tq<WM*{)JP5<2!ef~K42fj^@aWg_63iC&H|4B&x5W6&jYW9?f|a_?}8oy3rzs;0>?tngJZ$Fp=ZIn!F!;Wz<a>^ph@6;U=w-|Y=YyVPr&iu1JK9d1K^#|yWpMRZO~ibZQ#w&b6}zC!JEO0pmV{Cz&dm+SO@oo_5t?=cY$^VcL6tsdV?E-D?qD*D}akbi-C)Svq3X~vw`0!tZx-&p_jn#z{j8w;A7w!&|%;i-~rG!-~r&4&<5a^;Cj%C;CkT7$)QYgD3%<`C5M{O($Hey(%_=Wp#Zc9v>3Pu*d1C1Tn5*1hgJl;gG)jyfJ=glLo0!cgI%Fjz^-67XbrF%xCFEoxCFQqv@W<5xGc00xGcClv>{mNAK>!f!q9@?!r<Hpf^$Lhf^&hhL34t$fipt0f-{00q0V4Oa2lu!I1M-hGz&NbI1}_Ya3*j%XnJruaB@|qe?rqj(}UB3ouHY)PT=g&-@)0zg%AYigXRF|1Lue40Si^Z`N7qp9^mTWF3=8Op=-fHcY?cs`zD9MP!qZnY=S>QKY%}he|KQb>cA|5;F8dyV4-EfCBc6rhk8&AS{AH<>q5(bh1LcOZ33<fZVI)5n}P$Ny}&|yf`xVi3vC7t05?VYO_8sr@Kf^H4EIqF+#K2s+#K8;L2wUfPjC<LAZQ?X5O^GPJa`;<3WDI!<PZj(038pW03Hkt1P7ul219#;g$@A^22X%aN|oj$TvO;Au+UXtp$0e%912|m4h5&&i{Qo3?cl}Wt<c-xt>Bx<;S=;b^fvfA*ujzYK3Hg4M`oef!4BZxp=H3ogUdrJgN0TDmj_pXRtHxAmqifl0j&%60Bg`jU=8e*9GXI#KpTOZfIXr0z@Fgx&^qAy;D*qe;D+GF(Awa}U~gzGus65?v?{m(xCXQ$xCXciv>dn!xDtZk($E6n(%}5i-@rmMf%Ah4L9>7hfr~)1f{TFNpxMA~;1bYW;1b}H&^+Lh;NsAH;NoCcXkM@@xF|F?SZHBz${MdIg5Xlg;SZ=gv>4bOtU?QdRj>=x8SDbi08J0h08RsS1g8Q2a$ptfz+VW0e?Y&0e}I2NKZAdQze3-Gzk)wN-+(`W-$Gx4--2I3pMqb3pF<yjpMxJE2)+Zo0lovi0=)pf0zL{o1wINs3_T7$3_b`w0X_&m1U&;j1U?Bp4L%7z28{zB1Mh`y0`CQHgf0hf1TTfo1TO{8fDQxC01t)wfQN!xAPBAntpTnDR-uK#D%csC8SD)Hp|E~em_-o$EIC|<K8Ah=KL&q65bT6BL|RS=f(t<lgN1s43xNwF2(AY81y=*NgpL5W1doKy1CIpHhpq<C2S-D9frZ9`qroxI-QXDT2IwB}2JkxQKJYs58mI|g16~V_2d@Q3K@WhVz{{XJ!OOsr&~4yIa0GNSSm+{f1b8A;2Tug|gZ2gY1N%d}fc?Q<(8gddaCvA2aCxvRv^dxm>;laOb^*UpSj9S4u+U@RH{c!68Q>k@@z4R_@!+1&mf)UXA80+W4_Jd%25aDI%750k)er<%g_Z+X1=m*ovj(mW^#<1lH;4Lxn}a(-yMsG|`$2ny`+)~Rdw>Ul1EGI{1Hq%9Bfz7;6QDYH0yqph9V~PqI1IcRx*fb4ybVF{LFfVSLGT&qNwClx;4|RM(A(h4;A_yk;A`L{s0B^}UxZ!-Uj$!)UIz<(488(>1pNYj1pW#Y{oq&pEciDE)<R&R1;M|8Gav}g2dxIq2d)Zj39brm1sw@)1s)BZ4;~E;hem^i#(=}Y3!xjp3&9JZ>%a@Zv!QFiv%%A$Yr)gO)1Xn{Y2c~QW#Fmc$<RpfWN-*H0xWbQI0W1u+7H|x+!^W*?hN*XdVxK`<)G!k<-qx&uHgLOj8GSFM(|UGRrF<oh3)`91+RpT2d@PG1?>s`3)~s%1MUoN3e~_(!S$il!1cj(pjE+jz@E_BV4=;yo?u^SN3btA0NM{601ko<0tbP|K?A|#z>}e)z>~p$Lnna$28Tn#z(QAp!@+By+rVqUTM-2BfgS|!0Uw2)0SmnhJ_<esy#_u7J_}6(p9LR>UIZTppN3um3w;DW4Sopy3VsOw3>AINXJ`hn2!h`$90aGs@AHAvf%8JEg7bnaLtB9>gIhyKgIj}xq2b_g^e@2(g2zA?fX9GGL1%+Ufrmq<gNK8IpwqxX;DOMo;DO))(8=Hd;6I@u;1Kj9e<BF(1nms&1a1WN1UCYghL!`D2Iqw42j>JkKr@0Jz;_f@(RT<Ix)OW`JRABKcs95{v@^IrxIMHfxIMTDv_7~A*b7<*>;-NN^#lv`1vdt_g9d=xf%`y%z<t1@q2s`#!Be1<!BfC<pnrqsfEPo<!9v%77lT(pw}MxJ*C7br1>FPQ1wI5l3Kn__d<Yy5Jqz9q-48tr7J3}KAAACO8Z7i7_yqVq^fOrKd+>emEd;@@prXyc!q0*g^aFXp3OF~kGB`K5BD6KQBDf7S7#xhY-3CE$Tj(foTW~w*aBw?tduR~2J-7pOAh-kA4>|zs2kr>{6Z|LIa7P5e4WW&|4Z)?LrNO1ZIiNYgIl$i(RtK;Mf-gWtyA>>SHuwT~60|>f64(Z954M3@L7RYEftx|Sz|FudppC&o+ksnvJ3;$^JAns6M}r4~$3mxo$AYIp=YXey=Rp^Pg{}h6122KD11|xuKoGnMx(mDsycc>1EHoaR(hm1RW59dCn~=WHC}<2g3cMLXa4d8;I2L>ux*sg`1X$>Ou+UrJ!{At?FEkN)3oP^%I1&6DD%$OH{4Dq<G&fiT!MWg71m^-*g0=y-LHn$PAh-&&9k>d(CbT`cCb$l?1Go;jKGY9fAKU=i5!?~&umOT#cW5cFJ2*Qu2RJ+UqrxiM;YS3)anK83p_9OI;4x4ecnsJd+6wFsZVhb)ZVhe=Z2=bA3EURk3px<o3p^4!7CaIh0-Xj90ndWY0}EXOo&}x{T>+jCUJ8u@F9k<KH-n?W=b(w;MAW}?2!dZie}Z3ve?dk4`-Ptc=RuvU1g?a7mIpy_0ccHd0dNs$9dHq_8?-*y4O{}+0NeoesRV-HEYR%WEa2A)tEf+}5d?36#)0EdZ?+%^9uD;f4+nRHwgz_tcZIeEw?+NviXeChbR>8Pcp@|eJP|w-Itx4t^<XA~;04g7;053f&}i@m@OkJt@Hss1^9X`pK!1T>fE`f}#4~opvn~L31gC)(0jB|{g}Q;$g407wfJ@-{rAH9_Kw%Zn?*W2f1G)vg1<%Pq5F8Bc1`Y-fg?0sZ#q$`7Ab2WtB6uozE_5b%Cdz#-g5dSg4dC_Q1n7D2d6aJgg5W1mQKnCzX}}@~z6VVU7D4b$XnJsZl;2GR!I4k{Y@l2s5d?=qhk}RV{zDN2FN4kn&&7Q%LlArfngC9~Jsg4F10Mlzgx&<-M4mQ6L&2fA#zy?@M*O@yIqXXgi;{zHQwPT!Y5rgTON{^g6Z`Lq-Txp%{!9DgwyFQ}R&rYZ9KQ8!nogXNQ5=*16NgQ*iJfBQe*oKzip>'

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
