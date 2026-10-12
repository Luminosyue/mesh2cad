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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4b57e73e82ab400aa307adac36ea0e5e/part_003.stl', 'relative_path': '4b57e73e82ab400aa307adac36ea0e5e/part_003.stl', 'source_sha256': '27f0b03522545337e6f63514799d9b92a7eed5246a233fb383383826b5d5e6b1', 'input_faces': 1648, 'input_vertices': 892, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06261426955461502, 0.03166209161281586, -0.5000009536743164], [0.06260517239570618, 0.1485530436038971, -0.3376794159412384]]}
GEOMETRY_BASE85 = 'c$}r2ca#*x8?I*tR8W!vf*>&DphN+YAIJy-B0+LSmYj3WLr{{6ND?HBNL1nyB@RhRl5^S-Q4tgn6+uw$d|glVPSx%o_uRXl@4U~v7Bw~1Rn^_q)m67<ij<i=>MyrvR$$(3e?yN)B8?}LXJCiE{kyd5(63m}-b1{e42~~<TBp@%RJ(37uV<iVSi$xk`nBs@u)M!ug^uM4zU(j9u~*;zecSYG-K%f=4&qm9)4gAZsNb)1o8BFwp9__Ht<=l@R|>!EAL0Lh{Cir8GUBN<JEI!D+GArS`8;XvY55#VlWw))S1Nqg@pE5T73;_SRMPPyzYkZw*Bc+3kM;vSFK%(t<Ht3exKh+pBVT-M{@M=|+^o{$`*$>U{NQIV#m9cH_C2T9IO#*$KX7Zg<G=pIirDhFe!=rQV#^ch<9GaE{Nxp}<<Y+9w;4NP%M*9*uVs$Ebm@xN^0@xI2|JAPJUX+`@dvM3Y?Md)Reif+%j5as4dsvRv?R7X+7I|ng=5R(xs%)RgE>B05?dbahu0ho$Cf9ux?0FduaEEEA1*oN?^xLMJ3Ms!V9I;*o%{|JTOXTV`@uykH#^^p@5#PH`3Fj^kIhH>;fKpqdYylo3iD#WH?p<#6{kE0(wY9mYK|Wc9sbP8@7*rzW7BIt(5bJJzki$Z15Yhfeth@!vH55}yuFu7KS}xit4-!O{@jA`vA@^#Ppsb(`+NPh@;iQTcJcVw->dz=nH5`Ne{ZDrl37kZy=KM7mS6h;Pt`54<qtnKTKPTZ#T)g2AM{n)5?lVrg`?A)`sq9GbH_ik?sT%gZvXh<i%;&3ZHIw<r5r!lYv97zcBuV8^<%q?esL&|O8@EPHAcJA{>yc@#nxM}PzL44f3YyO-D*EvbKkDmb{j6{QU2>Q*TmMd_Ji+N-4<KVae-n}9lv@0wMM(b_jKF1HMX8Zp^T0nXi{`-Y(2Yv&sAGv>pA?}i{qSpT0XHl_V>DemS)?HcCz&Eu}*m&<yvjD6Yck@wLP}{q0AY_IR2Jb*Tj}z`{Ab-Z8O?Qo<BxA<=ptj8l#<P|LZy1V$1KjvUG&wFD<T)`=yPSo%}mjcYM#NbjkX`qje2GE=#H5j-Tb$uH<~3zrXjXWc|?K*@o|VwU3d%XW{W-vE_-RKb5?HZnoj;a@y%#pY(y&`-d9kzjY#c|DQRA@0Qa_@A{;V{L)F~^T|=8ezYIhHpTe8kyd$z#HROGIG(H@w_>j0>wN6=ZvLbX-2QWrQ_i~UjPhvTZ4aK?$@>25Bh7qTuQ1B*pS5C8>~RTIx|OUSSvJb>^>MM&yT^<4!Qi(8W6SS9a3onjF4qFXcaLMyUz7FylSiBR=;LUm*M5@p)I*Z;==z~Nar;{hFplqo>&g0|+v5!1J-$|Y?d$a64~wdN&i(qelm7VD1SkEQzxQ|2KRd_lr}*J{`;6llF7u;G@86;F8M{3p)(=n3uFh+@wm810W<JLcUjNuhA6I6l>5sqS_>nA24L^M2q2q_P95eliHPm@+-ey()41e~EEq`R+q07nn{=5qfU;i#Uz4mqb$lZ%7pChYP`HL)1i1mY|zEky(=7iyU0%=t}%v@~xi;5_J*%4L#xOV+w+h?fCwadx*{>2kbpZ1d^y>4%$k33&cm2=h@Rn8t?B^ZAB1*)F^Jz@Bsa{p8He0q`Lhc7fy<u7ws9haR~`a1c%(n00_bJ+01Bl@d+Zf<n^;OyV}IQ7}SsXFd~Rfg}`+gJImPMYagb#n5F^j~E9>Bgw*{HX^VKXAXZ<A=+RGsiJ}cf87$@=9`k+>tIudQaAiM*9zLFQ<GxUKL7lC0T!GS0lYUURmi~pY(x{U*%J!qN>l=b|)DA-^Y~SXS(4Bhox4>rOgk9ALuz(`Lj1TeyGEp-m(26H22Eo<orm@DTc56g`M8*N2HH5zNY+&3st)sJ2N5H_w2c#j&J-m!w;^0tkUP2X87UK<<#-5^S%0Acc%0<j&I5Rmy`4T;};vg9?wIKJXezQBcJpz((CcuPOtqW>2*7?%A<W<9{;D+)%TVzseW(&wF$Alr+y9P7d>hC;co}1dfPPH^i!`;?cs-Orr)`ks<+#p7=G}}_R7z8#Z2G&W7WSFEi(MTh-J!e^^Njdr0wP8qt8bR9$rq)kIUNE@ZIx~mEOG$A${b_;XNI{Q7u&uE9ND{`ks>`)$h%7&G3T@TBvruW}4v#a(tx5p8^-uxb*O5563_Eg35o=9@C!_R=>CUdNt1E@7mq@|25OA^yf@J+&-T=FH|^T`e`>B<G=QU1rMqGAE<sEy75|fqdlKGdpSAZpJ}GyyXS?@e<kb31qYkHJ}=nm^>v7yUbknfJZ^iYJmK=oyE(eFfI2R17bY0~f`+QyR=R5XC*D)-@RJ#)e{h{TUcFDN<5Kr}SEt^-?`w?b+V}MM)x7W6Ftdx1zQW#Q{m8K8hVSNMrPsbrA3Autvy;!dhtB*!=&QX6v3|JAH>w_{yl48UGO6}Z<*wmJ&y&h8uuj#(l*Nwkj>98=yPT}wC208WIBcbNeVxAVhbo`7v(#}pK0YDV55DuG^4tGm_@2CfsrKJvoayhXtd67Sj=G-t_hprT;7OH!*;2y~mnf$4pPOL%Z>af@NSRN~d`g{CeqnVT=&wDuljASDtLA5VY&QLWQ>gE~VWof6P5Cn?8-Doo2GxI4{$cua^Qq%<WSp7Lz@DmoR`}KMJ?l@aa{j!;On>la=6Te0uYX3Vj!ym)E30-=>tn<BESRAD`o9}~;AB0OPw;&+pX;+!{lEXSYFEB39gOxr?AYaG{T}lS-);X^de<kt|Gi*)=X)8K^!2Ch>+4VL>v6+Q?~W&=52yDlKi5swzecT0i1owO)2RA6chU4)<y6PF!A!#s{?bw%-#WJp-?M+XI*#Ke8h#-2Hsz1{-ps$q5mo;OKQr@ha9bVs`UllGf1_ACC;!t|Rr{Q`&+r5D{#M7UOuTC6R~xl;(m&VHy#K=2*QJp!pS_Z-U$Lc;K3L&_Id8DHqT`3tTvGK}a$7>IADs7#ns-fg)bKs0@2Gk>xXkdw9sX0lH^lwpq_ir%o)?;!;YzZ8>sFUzeRsadO7Hrl5B)v8jg!x&|D1A0va9O>*WXe`wTB147=Cc`B31tL9~ypOt9tGb*{H4u{M*~NiLL)omhk1|eE;#4hVRZB<WGAgIp04m&df*88(8Vxc>^oGK8|*Iw6Dt(H?&2Z<Lm3ORZm?>&X1(-Xry<q$E@_)chgUw(b~yJpErLxpR6Bue463A=S?fUJD!j}crB&l2c9^i`pYJD9@Kt#(QS3y$DB3&G&fW~dM9M~fgUNH`PjJZ>bxAOv96WTzqmfPeSLlI`ucvH>wnwV*Z;1s@5k-*_;z}?pIYT{kFUO8I91>A15K`}deGPB_~AOw8TV6e`n>y9{cu0!`q}R(pZk5!?VQaW-FZyqU-TQp4@T5HPw0<frhhD(>R$;D&3x{r+N#RQea-q?&7AMm^Gn(OzMQOoWT4@@^G;TJ*C%~o$PUNX^Gl(QBNJl%a27S+6?g2B={LWn#tq*v(`SAu((Qq2R}H^w>iDl6R_*hforbU5ZQP8*hVRaYv>0QipTA9&GyNmeKb1q(=bmAP@2NCE`PKh2)6>pFX}&VcSuUMw|7p~9k!MuRCQkY>6^!dW*I)9HD$n5urhmAms)r{=n*N=6#`Ruc`lQCr{|_El?dR4C)4%zrs<)a~3_m#jM|D0OKif=C`w9J^&ZnWCvl|)xlzCL!*Yl{_ckic|r?q`OPwVER?{}>9?)8b4-tDJWdE9=j%k!X|;|B)pSM7v(QSEyUo>%qO{e<BM8fR7QcFsp;`rq5Cc9rU$;Ri<#Qpe@sXfvM|cdL3X_luc+nMd{04vP&x{O_}>{j5{-x}iNY>O0@t=YhI@;QC7Y;Y#IIId|PL{Zb)So($s+Kj{75xW01JPk7h3{?UG*fOk)<AD+LcUTpfv)UC<;jpGep=VPaLebW1ftgGvkQ=ivzMw0grerWjadCf}i`a1pgJ$0OX*6da7q05E@!~f{A^7EWE{ZAsQ9~E0*_<>W;tNz>UhUw4Wqx$dQ4-G$@@IbYPMdu9PbL|oHCn3}KW_H?xzl)l$2p;#<G3t5a&dbU9p^~c%->qjWz4qPo@$=ty{6Hr4y_wW`#B=$@8nNxuA6aSoW1d(3VCH9@`mDN>&+sFv-OgTS_~BcBD?fDA^v7OR?X%PjGoO3UsBx*Bx=s!+9a7Etem(y1yf2B*^FHmn<Aasn_4V__ZJVna{UZCGWc|o@UmCvKU##?Q{gdARR#TPFmh{GXMEk*gS(RUNld9)S&juX7*dA4H9pX(tLxLK|{yJ~?p0*FwIB;p6>A#spjWZS0{ZZs-+e%J(IDhHmrTswlY|7v9wJPVPtgjmFt?0hX$@!5j%M9ObZ&rG@en{^bQn!Soo6@LpQa_)<52nhl${$eoLE(Lo&tDfmMcI(kepp|T#Ah9a_C1fXsdX2umvH^*H5^~Be{lV}byqp*^|}J>-|4D+z5YS_n+`ea3f%QD+FzZZe7zn(m(yNXWBK;?+Uve--~PSf-)<V~4P5`1zsz+D+W&irvHrm=PxbZ2Itur9jm)mD!>#fJh7?r&%c|!<+c<R|-=NAF?EUL8=X-nXR_&bmdF==PQP+XGJ-EJZ|J<KyKX6?6aak@JzB~S8m~Q&3@2hd1`E55J#`(y-$>#UY$fB+Xn2&Pv(dXs=#+mu-`k(Sk|6%z0x+2tMl$lT8_A39c?wk2=-56JDm{}hEoR{luH@&{@-8tAy&;3PQmB;4y>g)C+gG`_6c8|{!F?^mo`=<=H>P=l&N1n6t*UyoCX8GOg-UU|qAFJ!|xPoT==<6>3FspvJPWI2Y>c8&-<)6B1`dp{!`N_n3Q|Ixxi#N^h<vL0~?{I$?=daMNAI#(X`9JD=x6U<v#%Dbr;`)qxahsNy{@}D~9Ok*a`@JdE`9eP@a?5`}jgxx5$SwbmEsX0uHy=Ho-`ba~@Be41;k)+*tRu30y^hHJUasFlC9Wpx$8DNyey_fdVBL%D>vb>g@73!K>im<eAL-K1ET?{s!}Dm{*UzKfa_ae<6lty`=ZCJfG1Keko6H|3@tHq#zgN%KRmyxNIX|+zsrkF~bMv_8uO#bFXkwN}&+l3JyU)R`{N3lRR{34uD!)5_Wz~;6-(}U0`&`VffBjs{s(*KVh;@7upR-uUSKn7!?Z>^ZwAzopU$EP!dmmx7Pxn65YX9#1q1FD~>mRFsY2WT&fdeUw`>(*C&zF$Tf#o~Y`EIJ3Pu9MDy`+8ndMQ#Sp{#tiuitE6Uyo_uzJ9ZP_j<2p;YyDGQdpHU<Bo(_-@eXt(_7b>!6}UbPWi3tUe~v-d$n(0_qx7)-TUCPs!n-U>{9u>A2$6>2i5oPJ8b&ab-VWM>-JEuM^$6%Q{NZZzP>NezI`8I`|f>5i|y5%-(}qgCGqur4ZeLJl*A{!XX};f&i7jPaoV@<<6Pgmk8|^}?&Ct)JT;v3x7G3WH{WCU?!3+217>>bKGgNC`_M>+pK2TR%>A$J>-%5r+xN@1uhWPBSyIQTH)}q@^{sgW?c4JPu5Zm7Xy2YU(7ruy;QH3QfhX(Yx=wkld6gtS^Ca50=T(yUqz_e`S<k3v=6RC%%=2j9o)=2ulRnUHe0}G8t$8r*+w)+qZ_R^g-<}6^(_8ak+PCMyf}a*?WVBD_6}4~AE4t~ec||w9HLs|BdtTAa$C_7k(_8b3+PCKw<I+x6-)qh5+P=F!7T=!NwS7HL>*iz4>)O7Z-k#UBeO(?;&lQcGe5`qI?c4L)ZhC8eJDj6p6Q@3{`FYp3=I34CnxA)ldw#yy?WRusSkEuCZ$H1#zWw~dO>aHFaDD6fh4$^|7jAm%`Gs3f>-j~bL8O^e9_#sz_U-38u5UfxaeeFgj`r>6Q%QWDH@W#(&!>|3I{k+knmgsUo};<G^&BnI_sv$$_gc^Uv~NG}bJJVT`&{38-WR^UsFl&bc>ZYn`uU^lThBvnUq9b;ed~Fs?c3??=b^UmuIJoQpml7!)z6EyZ$B4y(_7DlJv}!$zWrR=_VsgW?c2|_ZC|I4)Myyz<YPUTw|)JbUHkTPdE3|NgUbiBi9KF=oq+A@bpqPA*Dct-UWef3W35}TeLKCqZo&55bqn8qsPeJab-2E@u0#9wx(@Bz>pB91a<+ByvDT#|@mXi0eS2L>5})+`_&RM>do$P7Xy0Bx<EFRP&$#KW^*`FT*Z(B(x&PI^z5XYZkhQ&&zqOu9`}TS&*SFSFY2RK?<>qg#r_#Q?p32SNT2JNXZ?C6nI7Fql)|=VBUO%RNd%c<MyX(_#AM9ZCch<ip@%8#Qe0#lI5})*u_AhmG%4x0l)4sjlPy6<IKQ|w1y<c4Um7SdQ)_O?Sx7I_tzO^1w`}TTB*SFR~y7^e^A+>L>hji0h>mdU-Dt2~!YrUxU?e(IrZ><+~^Rd^9R(@ak)_Pa%+v{DmZ?AWCeQUjIp!Ix}zqMXBiO>35?c3{hllY|fZ~963*1BTXx7HO$#!cyBv|H9Q+rD1UtbKd^v+cX<rE`7X)yQA3SH!p1V+RUu>E@KvS|9HE*7|VQx7LTdzP&ztOR4UTZ>^uVeZ5{?`}X>I+t=&iUEf+iZ~IBoTkGd--!0E`!<28mU!Z;a{Q}pw-Y?L;{eD4U=zyM1JG9=X(7ydXh4$_DDcpRl_bL2Ep6unMx8Db`eD{42{3P##SiVjleq5!ulaKYjjP~vKWwdX<FXQ^w`!cR?y)WZ_ul2r+o8Ed~M*H^rGT|m4^fub3zP`15_j()OeqYJ<-Roz3`+X(bPm<nxU&;2}^@rd6s>*4-&!v6)eJ<_W?{m5NSnqRrF5Or4X1$MQ`}+Md?c498*}j`TRgOMRIj#5Rv~RyR7tCKqrMKVjvwi)3AAXYe`)r@|aXtI=G1`M3Kk@DN6K!8VkI=sTeqz9TL#4OguhhQ%ex;k<dcV^3t@kS<BlGriewY0|srK#nN%51sPl|89Pa4?YTBWz%hqZlu{pR}C`>?jJ(}%iTbA0=KUhUiO^J?FIpV#%R_j&z;@ANa;E$<iGzJ9-0`}X_Dwy)C%<Nf`ea$4_AYu|ovI=tmU|Jd(!*U{nI?|1u4G#}vPZ@q_Z`})0d?c496+rCa8x_5M-aUAvfNy~TFPvYC}>D#`$K2zsoy{B*cNzz;I>D#_8PvpO4gB;)5$H4aWz69F0_c5@2oj%;*-$6z_=;MWN@55mG`gx+8kF^g&+`gPcjN{9`5Vo)Ph0wmekA&^(^uc=VhZ_0l`D*+m`&yhnHq<!2JP%6Z>wPou?R_?q_@obJy)eu;F6{e}#An|R?c4i=B=Jcf8Ch(&QBM84@a=t0Y+pa0)xN#YN$^;e5wYd8eS6=PNYzCnjCP{^wSSCud}|*V*SGe83DrwC#>wB_X9nNiXC_eg{#YlywU3SKTl?5}hUXaP{4Q&s9M`w^$+@0!s#8vDA0F4Y_Th<)FXs66K0n&G_xTA7^h|Spm$i?O_U(OyJiRk0-`b~0`}RIXk>~QN^wvH|u5ayw6i)Ms@~wTAw4Y?3r98(R-`?LTiLdut!%wom(>tSQIr&@rN@?HTS1LGTiR0V*R%zefx5_^){~RYDdtWSkdta>Zs78)&@4Myt*1lWeItxE@^0D^y(!RZ~SK#_#$G7(l)4siLSTIBSc~1GQb&{Tj6--~(L)#tm9pBpbO#Ak}XP#R39N*qoP5bt~YH^bahho21=N~#*&GdD9%b3S$PxiiW+PC+G^TY=nKgqsx`1ZbY;aq1`dcCimUI%OYdR?gY^?rADdTSrN;L<;rIli^ep6grt?1g6dm#cni?&GI@dmq1G&2uXKspF0x$(vIBu3vAd^m_k5T~6EAzf1e<D;OF2_)K!XfA!DF`f+yt_Wp$5H(u$K)7t+~`}Y2akwFucZ|$$BeS3dJPwqCWRR4X#Ngtvfv>)zuc8gIznMWv}{T@U5_ga2r)z8WLZhhLmu1|cuZ)C*EU;A!-T7I0Bf0F$t@0?TLYprLFE0Jz>tncnidFpq=*Yy*;_T(DFr<}I0>%sPQJtXm^oOO-eMPE*Mp?bJ>G)Xj4dop=Cwu#wVR80BPn*7$HT}uC7Z7o`|Z0U0Ue|w8QT_jqD!qNE1tMo&!VhQ2bQz)&NLa~H!Gqfq(3~r0If!o5p(Oz(Gco-o(6zvHQg@>R$;34o}v>QAa9)xy*2f+iQF#zp^c7Z#=Ezx)3mT*I~G29S-75yLlD*Ulm=@hSG3E>hRr7wFFO9*E~pM^8RY0+okwD42t6Yx{85B0)6I2HONoC;2drh(JJnb7CpOmIoGC|nYr=T$o2t5`y~TneQXQYe-XZiF_08^Nv6)^IDhGa=j+jf1<w-O+Y%ceoGQ9_|D8jYdDT1KJ)IZ4QgJfIGk)qtPGz)T^`wELsT`UEozL`jSVnXa-pHX;?HRoRT3$SpHJLqN!og^ss0VxCnjvQ~L7jlt;7~EZP=sOP>_(O`rUfe?N@hI*dNqpBPI04W&=^BZg3yL+F!ziNVzUVEUv!7K1oegXoj`*bU^^>VB(_^?;c6AUw;fv=c1a5^hOf6>doX6n>RHI*Yz3{cskV5za_|6HZGX6Ml+*CG4Xw38$j}2&bdZ2xp?72$!U<%%YE!qdev41Hz4H_rk6Cox<-#wPrM`qE+CxqfsXsmC-lh%J3^_8Tb|WCA28~5<JbT^b@aQ3E>JJrR6<}C4@_(rQp(Vel#zfAI^ck0Ox?SqtC<H;hbnTI44{H%?B5N%b>5oW#EeF|KN)79Iw*Pyox1+UrwR4SPI1w!len}ve77ymOzWaCE&T_A$iRugkR%3<-1=ago~rEz{TM_Xg)X(oE6OmXN5DP&%>GFEa(ex7C1MW7tReALrcNM;BshrxEwr{HX?0hDj{5)HYIJVI3fHRS_Xa%u7<t|SA*-Kb>O;i146hy`Zio2t{sh9=v(O9@LO;Itqcd?lISaNNw_fj5?mOb?o}%NXF4G)>-VS8pI#?~%c7;>vT#8(KU@&bh30^B!7rlO;TK^)niKZJh0p?UA^26a4E!ow39SfMf@gb`O8=Qn2p37ARQgX5Lbw!K8ZHID!T45#F|Gz)6|^*5n*LUW5Uv{2C##~>;i~XEgm67Vc&1lrdAK}%ShxiJcqaW<`sz%yI9!}QDV&FXD4dnPC!Cr7CY*&nCY+moC0vZYBwUXEG?RW*obnW>pEzZpZwObTKM2>QKg{IcH{iE6pg-u}UZ47?Pk+$$Q=8+U`%F!u7RRIpJj1K>E%+_^jBtQ{B3zQbAzYaLF@t^~eP9M!7A{L$7cNNq7S2VR7JiX-EbOQ43Kyci3cpGl6|O`(ok9C7LV1eN{)9`>&V=9KcM9i-p6nY&qmxf@IzGQ0&9iDWS`xxdqR||E3#|&j1;0TE2hg`+(aLZDev=Tc5slhtHMBBZ4X%T}4cCF&qAlUJ@aKf^6toFE1)dc1+a?jhA4X#V8izKA<KSB8TW~G73i<|I1+Ga5S4RVIfV!wo2sa~y8>2Pg#&C<6x@$oQw~0n4v;kThZUEOstHE{QhG-qQA>0{l3wMTBqo2d8;mlqY!s*c|u!Qgv=p<M|_z~WR@FO^dH}TjAO9-cpYDTZpm3$U|B_Z4qje|SF_0d{zefS-;3j7XS53LE;gF6tyt<mamb&h3gLU=wQ`~lh+{s5kcwty$XAE9mFkKj<uu@4c#tD><39gcQ_hr{jA25>vLDOwk93b#ia!tLP^XlHl?yc1mw?}YPul}cO5O9)2@;VWo*_zHXpeFDA&UqGeZT;Q|tIaJ!sIYRghnif6-pYkTQty6^XiD(={bE6sI-0*gfQfYtN3E^RAM|c?gE?OUc7jA^U12=+Oq4nTa@KCe^JQUtW2(Lg}!>wtHD+uA|yefp#pdY{z!aj5&EFt_5?<4pjoYJc_1WO2~Ls!8P!kN5@ZC6-AI8Rhdc$J>uv-l?n;hE@gcqZH*Z3p*<yP-|tZtwuKJv;!Og^qw{!6(t3@JYC&SE;n`l7#S8Gy-3RYx`6PH$$($62cwPOR$7+ck}`*Av_R02TKSKN6)|#!u`=xu!L||^aLy++}@YiH-sgGn?$vyPw5dpi+_X=E{^7gi^In~N~QlCCxmC9!{8ZkKlEL=AKVpf1b2n|qOIV*@N{%2JRLrUZiA1(#k?wn{pbpK1^vlS2p=VckE3be<M2t;2cLvbqtdTV^I7;TD*fs#A$%T92cL&8qM6`}@MSa)d>KygCicAqLiqb={D8iVmVn=eZ+VnT|GY&AhtZjE7+#3>hZn+=(Qfc$_zQFZ`~|!VodxfLZ=)yS+i*><Qt6*H3E^w#RrnfQ+NV_dYH31vA|bpOZ3ZufH=!NjP4GUnJG>7*i4KHM!atzH;UD0i(EjjG@b_p}_<Q&`+8#a*??Icud*BVe#J;_O5dI<><Iz%RO}G?%*sE0f|6xM723j1h0srPvD*gXALU=1W1KtYHL;Jz=;0b6~cmg~Z?F-L^x1iJEE%2}CG5A;bEw54;3*I7x4-vxOp?=uUSnwSo{I*YpaAWj1EFs(uJqb$)cR^3X62kq^v#^BlF!VeuAv^%R2ulceLodS;!X3~ASVFid`aLWmT+5d@b_h!dzY^8#KBYhMS^OUf;kM}8a9cPlD&tF5J`3Mq%n8Fc;DhKw_#pf(IvM^JK7@V&AA)b9yWpGf3tpwSVF}@OsEjY|2;ra5Yw%C-i$0|?zPv~Xw?!wyZQ&0I;jhuf@YnEVbQ63T{sY|y{{g2+q4XpyA)Ffh0hSO>kNyNp2tS8@4@(HAMUTT0!cU=lU<qL_x&f9D{vGcN_;>hX%-D315MCFJ$!Hup9*%>vp{3w#@IkLq8NUt^!fntRa2q%aD&tocJ`4ZCn6?%E1wMezgAc&ppcCM4;Qi=act3m{-2z{SpZ6;L6_yZ=LuLGmBZLp2hu{P73qBRXCDHHT?-<WY62k8j!VA&H@IrV!+74b1??$`8yWwMKKlm6NL5IN+_(yaA{3Co7?FL_kPoN#(6YyTNDZCfnh}MEP!i&&X;6?BRU*gy|fe>yJjWTFTG&`IU{@JTk#>bxt;UQ>ScnDkz%?j6o^Pw_6=Hs()2J|2-A^b1ixA4F4vtFf#U<u*;=uKEcxHc-|V{JlsDB2Dl3SUQmg0I6*_>{`{_yi$b7Htccg<GH>!Y$yQgz#7B*YH>HY4kFD8h(iW0Y8MFNugB6&1VSVENE&t3!DQ@59fe$qtC&);e2RXI3Jt~eG1M6XGgtob~rOC<7Q?)3qOHgge8O@;H`rnz(;+FW9v~uczHBBqm9tXa3i<`8V8qvQ=r-46!3npQW<~u6T*YhHt=A$I+_Kp4(CE;{LRH@;b+hTu!QhGc;CSPz)yRX?uR9WbE4N_3E^s}jK9?g;X!B|JP7_4Jpg|T`+Q1eEcOw?#R=ioXh~S~eYiC|i4cxQ7sB!I1#~@p0ltIohVQ_#*hBOfEFt_P8i6H*)1W`X62i}-S78a^bm$3KLO2z=7nTtAp&MZd;k$T?;Jff8bOL+{-i)?^H^U$J636Zj2;t_@$bfp#GO!2!-K#VuEFt_0D&zYvgz!Xk2s{xUf!2aYz&+7?a8LMMGz0uD+ya&Hy#=3zTca|*w<d&pq50un@JO^aJQALS4uvPdH_+?w4frl9<NIAc3wwP^%fepxS+oWGEbK>n!hW~_Av^;83LXKkL{Gyj;h)im@XzpLRL1?sd=}2gxgZOi5q<&90lxs}M{~pZ;eu#BxFB2z%>@^N3!vHI0&pHQGn@y`iar5ng)^Ws?q}e$@P9s~N8$hAYv^+L8oa`ncy3rh2oH@$el#cA8O{l(M;pQE;m2O3C145RJ7@}6Liih0&L7_p!V}QJ@C0}`S{)t^_ds*OJ>XX8GjJ=oIV$Im=6n`ziOTt-B_Z4$%?WphhoRNrVeoi#5Ii2<hkgt1gKwj9{<zI&;s4O$u!L|rLbxH?8Wx=dH-tM8!pqQjco}>Iy#OD9@1u9%`*6w>O69zgk`T^>J_%=nv!Q9=Y;aEWSvV)07flD}h5cwM*bl#m`rsGg=TSMYJkMw0r_oEWgz!Ijo8f=pQ|JfqDfmmYIs7Hu!<TsO=|KqRB7|>xm3m-NIrj*Q{sN0mghfZdqCH{JcVW>Ma0|{8H_={jFU|)y(Mj+m#{HY<U0BphIYpm^Mg6d70a&5{zg2WZ%x@n-eTc4%sh^e9pXkpq_4zaPE&4d7{vUIEL}eV;$15YpGb7`;KE5w-{9j-k*X<!c?Il0sxNbiMX<r2y$8~!vM0+g6IIi1g0orc?#&O-A^U&V&Fplf?pOyZRm2q76mkjhL(f@pj{p&yapXjxi{&<c4D!L-3|E{2aiw=$H??V|6^jNRQ2jLuq@LsRdoUmwmSX9RMy^QmB;5&@td(jE-1jg&VXb-pt<MLj#IozD_cQ4u<?#?*77ab3eXFT1D-iB{8Ztg|XQT}xNPT^;wS|}Qoe2O1>)#v5WF8NtBMx#UE(QqHM2iyk^qJ!Zeyo?Z@gZ6^wz*EtI@KpHIXe>cTq66WPa8E+GJK78G4tGHZ!-FYn7ecr<It1<we}aAne*zyNgwLYO;j{4f(fAo%hc1WL!Q;`<@OXGE+6NvBzmEpt_u+VS85|G)L<mRFIdB9%gHDCdz~7;t!r#HCVvfxzLikEFuAyttCGZ+}96Ayn2aiE}!eij~2;os^cX$*$2<-xQ;rI<AglD6lz_a1g=n?od{EAnF@XP2~SVFiA`aLWm{6BBvu@{yQej}<4yh{J#v-p1z!u!y5@ILq}bUgeOJPjQSPlLZi--o}1_oDIeUieS+C-_gezE_2C0FA&B!sXF3u!L}F^gCEW_$BldEFoM9y#h-Jm-8mJEnx}a*P~k3tMo3P#lK4k??%_ayWvIXICv5KF**kR7+#FN2QP;A5W;KGQSe%LDLM!qMEhGx2q&PY;RN_KuTp7?uMxtl3E{Qq%kWxw9a;un2X8?C2XBBkp>M#O;IF-jZTD+JcxyDaqs`C;a5FeHD(yQppM@{d=J&xD;jhuJ;IH8g=rni(yczux-V9$r_re$8R9>Zj!V<zwQEBT<3E|Cz@J2KMZ-m#Q<>B>kJX#u#hu5Gl!E4}EXeoFVyaFu;uYkWqUx&Yhmw6NW#xg>9Ni-IrjnTSrWB5r_`p=Vm7CuLx+6|wBH=>K+jqrN(V|YEh30(|tg3qIS;PdcPUKPTB;H`!KfPX}n!b|BtKN7-~yh^42R3d~|qO0MR@c(=&gx^5d!V<#O(RHwd@H^-RSVFi4x(SvLu7Z9IO9)p)x55&_FZ&Yvp0I>)zNkL$Q@WGS;_oDcyP(bBE^uKqHC!0}n|>?(^KU}<2lQ+B2lyzu0X_;}MK{A&;d|%>_#Rxyt5o`DAwsw_+7#{#Z$UT1Tj0z-6~cMZjj)99OXzx7Lbw7N4@(GFM%Ta+!f&CgU<u(m=n7auxElH;EFl~~m%$Rk<<TXugm7VBV&4{)5Y8?4g+8SV`7HiILbxN^814ucK%ayQz;_rIr2pR`gfF2R;Y;vgbUl0+zKm{yFT=m1=i%Ssf?lOE78E3eI}yT7P#G7R@L9MX`Xl@!<3T+__$zcJ{1sfpr&Pv*B82d0LU;=L20R6xfmVlSzzfiK;05qfv<AEs{v53We-6(=E5ftjsp!k_RCp|!4;~Bm^(BrSeF@<P(Rd9_jXn>jhIe_D%J{O25FUtjfd|4>(ZX<5I0q`@OAbB@d(j_Y3E>BLN8tysytsXo@x^(G+pG9R^d2lB{3a^n%bSGo0JJka0N#dffw#e_d`e}kNks^kBZTXtdExqSAM_=-4?G5~0FQw`Mk~V~!!yyh;F)j;tpkVPC1^Ex2|OPS!1LkhXnA-#{1I9h{s<1Dx#1w(%a=Gd^&*7pM&niVNi-w;B>cHosf=Hr6T<z_j&MJ?GFkwx3}-`S{L02>;r|%ZF2Vo7_tC@fefTkY8Ga0B_bUAzmJqIj%J@}<5blq5g8RdZ3E`z^6L=}S9IXe}WBgi92<P!BmGLVNA>11s4flpWBZOC@Q{dI`PILym6Fz`0fDgcD(WUTNI05|}PJqv&v*7daA#^Hy2;PN`g?GVg(Z29ncplmSo(I3@OC0;&BZS|LMlm!i`Wl=Se&AJ_8kP{=jmr4An-Cs{4ur?S-O#FVH@Fd+18xLYM7?lDxF{;)V^KZ}S3qTatUw4iL|=p(!d=lf;jZvlbO1aS-hpm|cfj{i86WTSSvZSNX*oCxT$B)Qh1Q2#!Q;?A@HlubItHE#uR%YC*T7+PCLD$jq9OPod=6a#pM$TU^WiJ-8FV^)2HuZ;1n-A;ph0*CybA3FuY%{Gb>TViNMGXEI+74>8I6MIbLgw^bMQT{(kEdF;Seh0Z-@{cjrM~_!|l<^aC^88nhmZ4mqlg#Ez4)&BItcsLiknmF)Shc4l3jCJA`ltv<ln-9)tFW$G~5pi{UTezX{=|d`g$X62h6#<*=xXznKW(dT4LB9y|*D3?2nfBZRl2tKqHix9CpzTlg3B0Q?L58+sQ04gL#Ffd7L3MbE?k!hfTO;J@M9=q~s+d=p&@--N$I=fU5>+tK&n?eJ{$U3fM;#FsdB4<UrBMk6iyuUBa?SVH(OG%GA2d<&KF{T3m-2i*<tfj>aU!5_fyqut>5;UL-w4#IuWif~`JH(C_#4fjDSz<uCRXhV1u{2tmBeh;3Ej)f<~VRQ!^hJQov!@t3QqB6e!$!Fn5Xi-=~I1M5ECfW*q6CR9?g9pQ(qI2O-;ce&|cpH2e4a0}w8|Xp!27C)W2j7D4p;zF0@FVmL{0RON-4Fi>|BCK_e}%83tKjSKH|QMr8+Z#k65axTg0_S|fd}~#&kchJ;n$<_H2RNMX+c;*_z(0sSVH*MsMf9N^<_$txcS?xz`Wc3h8~YZ8c*V%wDsuKPlvw!yRaLa{V&aJ<6{5iyV1PdP2}p<d_wl?^7x|v$wRYd3+2=Q0a*BQ3j'

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
