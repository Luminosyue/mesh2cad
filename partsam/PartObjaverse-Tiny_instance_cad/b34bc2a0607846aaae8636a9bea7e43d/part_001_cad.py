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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_001.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_001.stl', 'source_sha256': 'fc50608856b0bbd76fca83fb8c677d1ec3063b0ff71420fbe9b8eb496bf96b1f', 'input_faces': 1128, 'input_vertices': 742, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18644699454307556, -0.22168731689453125, -0.09287767112255096], [0.19259661436080933, -0.21548667550086975, 0.21745078265666962]]}
GEOMETRY_BASE85 = 'c$}r32b2{>yRLfx6;wc!jKW4G2g#s<(<o6Th#*O1gJeXaWTXWQ<eX%{O;(cR4AbNwK_n?bHi%-*2^Beh)lcu!U(ejN?z)$=-t|87{$+LT>Z-4M$J6+!jG1y;-oL`u<4yj~eODdJ65VO#wEB1K)357`9s8Djx!0g1>n@YaKi{V|Y}TN0%OtD6HKbUFj(uP3Q|ysQvFe?w6)PPn)~RQoetp`#+_q<*4jm=0)9$6d9skSwc4^nE<9~k_uUe@>=}5&Ar6a>4|BwG}|8EHHs}~QXiYG^ph&%mKQj*2{pHsQ}OZ6G)<<8H8=SyyXa$M!sf<=o|o@4q4;_>1qCz^h~OV#~%D?L)>w6~fZTPnHL<6WIE%iS%#JeKt5GRfWZWAu3D7g(iozn>=_=wkjJ&`Ce8Qe#J?m%9b#tv1K4`KWGR=eG%|>E!MUrPi9`UeBVAYmZ+zJvE)&nZ041>3?C8%A=d-y<_I*wcqxu{vXV+(9H9VU-qkc9@Koc$?yMK<@R@#mYDwYUsJhN>h`Io{f}pL|0_GZXU6~HNtMSo4;pRqOD9Zj*<Nnf**YgRkURA6)_rt?>3`=wb==6y(^i;%R;H@l8GL4t8RvUTbe?P5`zCKPPme!tmofQ<sor?*ru~4=W2u4MA5Xk@>P9o4C*Dx~xb6F_G5PO9b^kpw3^f1!S5ZBm6*8IgWshm5+m~tkmT5nzk)EGrmlp<ehxv?-t+Cnklk}*bx1<^C&EqOqR?WY)u)`GNw-nL&8_#<CF<&nIxY~|0`_XNfL$8w`x_kS*dnVP7Q*QUtVD8VSyXVxB)Ijc!)2jWz#^iMJNZw6b%yDPk*r(Rju999o+40LhH9sY~&PomB;eG8~`AX$}J#n*trgH0iIkVrL(r5H>k2Ut{%;}^1)I4W=f0LQFIh)mZ++BU=nZKuQQ2khE-tKOWn{B-w|K6SNr3P}p|7hOQ+f4ser|EIta<QZN`=v>$eWXeiGjDd60sGW?zN6v-(|&GWH6Ewc<=4#dFFmivzv7)0!Q5YO&bXBArvLrVs@(l{=T?(vdR9N)K2J^X&QE<c{>bXH3rzbzs;Kt%+qstnbASByV-GDh?YdRa=cVajQ{U`;532s%Ax%vEu~!sO?IZPSoBHNn&ZF8p1q+(GYEQje_tR#AsWZ-qJJmef*=#cpZmCSFy<Pn-uO2>-q}N;Bqo)4Y?JRxXyY+rQHIOIHd-q#*n)W@u+Z*gB+IFK?KNozpH#k35)!grz|Nga$Dz~TIYwD_X;kfF@`e^lF>BmaizgIo3^}BbN{-0dCSDnYk4U<j#!VC3rhmA3H()noa-r#z$9_f;r9LN)OU}S+crd`97y}@~K%HCLJe9JUF&N~nEH$Gsf8fW~O$G!fG4^Zu$xkukLkE1~kHU8+i)?OWRyQt&3n@5|vYR_z`+Q(1DygIhGiR$0&P}kH+=c{`9aozgyO7r*S+Nz(}fh(r|*dHdVe(Xw@CY$lzsHXE{ZB1RZD^^zhJ2eNcO%3FUc^J~(HRq*N1wC)Oi<vrR4J)k2xuvhE!*0KV`naD}F?BUfer~<FZ*c}@*7G*|>`e3bs!V#Fe0kd>bKH}E?Fp_2J5tk((;oHPp5S=mFSlH6{x0(M9yR{Ic6jyn?{liXv$c(>lg^bBI=^{*t~pN1aotZ=r-wQ2$o;Cl+wJJO)IgqC|955GWsZA#gYM_a1239(PtQ@gbEuK2pU#-K^>`{=op0I=nzko6Z`Rscrmi}@C+`W)o0BQN*v$VPN4Nhu=Ixi{;p(_<_EO&c)tCKM9+`P;K`>7|t`nb{`FFDR(2uJ?e^cMA)Xw^G^{q7C{9U+>p0`@376tP}d+M-rzLm<OMR%FH=hk^vtp_J%{jOl1=zqk$8_amCG*G#{uB@q(&U^LLyt#SbF!x>VtjE=HV_l!|?qkbW(vNrIxM`-pkBX~2KB26s+t!vs>bTYm2bP-l^|Pt=cDFoZO#6&?s`jy0zBK#Py?k?b@H{%dj(XetckVB{)jW(CYUaVu6XPr~c8HnJ##dB7*1)Y^oxJ{u%Iy*DHwN=WKfm6nn;gg!>mjB2Zj(QMe7BnC<wv~z*z}0X<BJ|Ob>8ijx?An{?-#ye`aQW`<#yQ)rhdBD7U^-0US{f~pC`uo>}K!z*PU}zKhB|Mrfxg?XQ}bHXRDgJZ9Otgw|_Z{SNAqf(c|2``wjE=FOyY2(Rk7IW?T(NsrIo$t4!T<M>;Bx`}IH8SB>92-@-g!vuk!y=huziW9Hed)={@V+t$>7w|@sU9w$S2Q=hHK^E&@FwkeqV=g~RwyVw7SXVg5$|4B0I(Ar*A&wq^;rfxeuD(Lg|d<9dt?XSw|^-#HtS8s1b^mr~`_x9tGys96!NU2d~ey-+G?XBaT%)YjgZ`b2l_nfKQ?tTC6QtRQV{XI=Tt#9m7`>1VEQ$MZdS9N<U($4fZ>f)~8{M*UP%>3B9FYHq1ecV#7KL7Et>L=Rb%XiIuR`&A5eyKiXk6BmOK2rTe8dmkLBa;rRew^vGy}DXHRps%&FL-tS>+QSLy3O{CW4zNgmB$Xh<J~vjwptz6Ik3dkVe94!)xUdlsHun6yNgsm?mH*Ub-|fAPvz14CB5gN&!njSV|gF&t~>S&{kZOJHO@TVYExDFc=j2l{@7zisNBx5#MDpcLT_~*tq#psng4x8PdyLQ%A5M^WNoJUaSL=`pI&ZPUSR5>yR(rxUrvkSd(GqB__SIN*5vBuJlfyZ)BW68&eUgjcwse8yMBJJ?k&or=f|$^)%mg6RD1W-{!QL^Z@6mSM!e+Jx6^;Q>O79S*Lz-H?ML1I!{aN>_zPWA?W2`ydG&ef6<6(F>TM$T*X_jF-u>JAr&VsPt#9g;Q|gqf9`A<*z31sOj;K8L#ANTfeB_|3=CkGB-ufZ`-}^@Ie%so+Pe0z9JG}d!ZM)sz`HC*vYR;Fne7ovDe&v{VzEW4{e(osf)ulhDs66&<FS8$=SZg(YYt!>)J-dZ!>HOLTZ`}^AqWZB8e`40B+qIk;XKZENeP-T{6w&iGecB>#z2C3KZ$H!2dt9$Z)cm+Beq3%I*YbS&xQmJ{H~-yNc~$#(fv8sprrf31NzG2)>rSazRPNU?=SF5VPG|T;Zy!CHS+9rd_j#`$R=h=x$Gtq;+rLXJH4jedQ|9%hNQN&`)&Au^HuiWdRju2HUorb7{&^#nyA6k$^&Ee@QmX3z!4J(m$I50+4bG>V`pMp4p4h*Y%9{I%c&2}Ms`YU9Dzk1QMb4|-PM%=aPxR0hm0O!~dF%h+7~Rjd@n&5`YmMHi9`BicW}n6?j@%iX&sfEQX5Yo{AExsGmCU}2On7Cd+DF@eH1i)D)>G%!O7r@s^>I7Zk6%x$A0JiYN!)ieDX+#KuQ<l6|LDFOJJfp4)^xvVf9tg!YCZ3*WUlYl-ebD`rIz0M@3L}-n$PLO&AN^MGD7F)e>LkTdbqF7A6sJ9VWdn~osXYv_E9YLZk0#!&GPPNR$bh#*2&4&&FhD;#phHWdv%XlpV7Hzw+H9PDw*W1^XaElZl8Y4?4#JY6Dp5c*S**OKXtdO^}KAZS+{Ph)a~AS;(Ge!2{WJZa;vwex8I$XlT@DAr{sypb@LN5&+hW!>bUMNea$+z7c|iMzbDOlwojJZ9z2ik#17u`{haxA`}SGQbthK(*KKP4|6RP!+Xru}Jl21Kw|-g=GP&)Kv+`31%zSolyiFaqUPtf#uziDVYCSJ~!F#>5W=)mbwHljwi|k0=rskpM472{-ITckNxp36G?)+Y4o0{jpZZ-QWek$KKwNIx%X7*$3NN)AG-2AJ}y0ymqyEVOi9r^9|t*ZT$s^)bzd(TzXKE{4@%3j<WoCoLWv)*-K;33sdyxM4U|7lI^r~BWz*jwjMl-wGeXRFUnGtc&_`*r^(S9tZa_|IE{?IQ>FdGk5s@)o`CCVJ~9&kmJ4({DHTQP$LLTY~c({k^hze<5~ik;<J+UCq9;>cvz)R@r%Gy+v|Q(EZ$<V)kQf^k{wDq`GDuy5|RO2|lh!_FK$-SFHJfE$X~Pj(hcUc2wufEVF;@&JDK&*Mq-*BWoT}xxXKyKmEEnc-+{li_JQZ<UhSRIG^#tWe%G5i<fOy<8S}6S?BJMIbM7Jb>_b-oAVXjF-rAs&Ae#VTdduSDtEJWH0vt<c74^qwJXVc-TP`~-Ot92X8pwKmfEcL*WqmD^?zqi3Ej`3B=bDW`ZmjEwT})wYWAa(^XpB)+}+#7?7K*f!<&NhZ0(+I_MLP2U6n^ucYE{irfdq%b7J4+pQzgV`^$cQ;HKa_M|Vv(^K3PJWs^EDk1aOq+`jbWCbeH?uQuyBcC41}=b<Iu{0}Lr+S@;tGV9!4kwx|Ij866H<aa-BRPEbz@m^=JuWVH3t6Nd;{lQ|NsP@h)*Jqo*2hQH8*8kjV-g(K`b7Sy)*<-Sq{bk)#N42;9u449AbY20KyVu&7edLbMwK4d3t;T<vd9#yp=<%eCH0v{7;-?Mjyqp^4y<U;;n+<ARo%_wZ|0GYeXMaUUeWr4Me?_~W+YlU2WbsWi|IUs>8`OL@8Ro6?-{05A&6M9;=XQ!}@BDeptn<j6397x_sDfF~&X~7Ud+Yw6W|)3TXW0;(w|FntygwDse`>v2|0k}P`HxpvwO;kVZM(OwR;^gC=J{CDLuTH_$8<j{Gn#!AKQ?;3TAw+pne`UQ+)MT2=5J}vmwWRi)!ttIfwvCH6YD2yQSW{5n$M~B)~o%z=Z{lstK1n|!Fyk3aCJSN%{k2T+(@5?*Q@==K27BQIFEceH8q{w-|ykv`Kpeo5AN5?)~WFy=x*M}bUF@R7hM05^;5j}E93RorMnKv6Z2eTo0(_#k?QM$^Xc4JZqAFFxuovLUvI7Qsea-)u6Xy=kKeUU%|GifGVP}KevALSWB3YlzT#v5S)1PajDGR`+Vs|^dz#mS{ds2J`FWak>$mrxM-PfmN-y{Kqn{_P%l~FJ^&wump~|g-dCdEj*6N7L?E<yTzKB%(WliwB#Pjwx`@+p}ZH<~w>Zh~wpvwLF8GYoyn&5efwED-Km&nF_Yt(Ub&-3mdthH;@{8Ml3GYeGze!aCHp0y@8pH{uqW7EqM*P~GGuTMV@*X>06(E9iD#5~{gfthDJGI33Coy4!+^sZk$e_E~D_uFmeKlaytosam<%)j+U%Ie_!yOWBWeGy3=v0AN@?B0DsG)EuRk2|lm*%#42yR268=6d%Jk;j{<+`oTtRyJ529KYSA?qM^|l)Ab->(kE@^Ka#CmYh!Ryz|zu^m1$d=VQ{%3s0M!UhaQRAe{U6Z+@P5KZW(57=P&gC(%!6e}!{v{yVRyn=kyQPrCgK962>Po!tNYRX9()P7-d<^TBZLUuV<wLmfzyQ)d$M<M&g1ys3N9skv4M_o-97u2(<Xmv}$eKJq~i^LYS!%(+!+y?wRB)N^;uSd~Xded?{-PpYp{>#z*Z3&<07X<;7k`rA7DDzzVZUJ%dx(@J&T*^lAeuLEiFIz3vam;0Xw2<QIuxNz=YAJg<ho$>R;I;1}MdE#{pp4WtPzy2ip_vh!Q`-Z2NI}JMbPEIGc|2#D+z1)3Z$fWf0*paa_(#xZKo->@sU-v#Imgcy;?v!Sn+~=pssl$nR^T%1Ek-08JiodfmxIW#5V@+MMGgbC-zdkG*Z`N(>)0bALeir99pPz{oDz+kcULw!5Fm*WE{L|%Xo&Pi4yFZ*cOXbm}C(ZhdR3ETBc)nbo*T;@GS{_{I{_}c2|KHEuQ8&W5Uq3^6qJD<k`}H&2-mf#^+^-Mh{yg|~Ae=i*a%>9bY3gS<_pb~7al>^rlqc$HxV>LL!|na+LMTsM7eaZWu7>hNT@B@l>qsb1)Z1|XeqHtFEp*@Io}95PxNe<ehs?TlPI%7)64%*_$GqneFRptp*pL0sKC^C}^?lz9o)>#_7E^~KH_EB@k$w$K9ga5q>D^#^YsExUhpm~b-VLr#zyA1nxUPnCzy74jsjK1Kq5h=Fsh{E8ub*k!Qy=_1Tvx-nUpEquH}pDZI8QuJ_mAtZH?AY$+^@Ic+^?(Q+^?(Q+^?(Q+^?(QJn=qSIQQT03y;%(Um%=QhZFPWkF)bh@AcRLW0$IR`(@GxW*yFWc&S>q4YQl|9KCjZNwA-Iliud@c+vW<%A<w0d7md-FjD1i=Zsz*&h(_p?Me+y9gcRoYe{h3`gPUM!*w;B`}H$Td+KL6_v=rZ_SBzn?$@6*$EE)GdHB9GO-{WH=kCzyo7Fso>TsHzI-D3!s1Ap7zYeF#|IO1ZIi1|Uk4=+PSHpSY_0>?Gc)ci;CthC)=hWN8{DkgfV@U%R1=nr-p^9eR#=F~#)O<G0W<LKGDN%fpTF>KanDrbvlSQ?UW$5nJ;d*Bls^ebTYSwLh>w<-<|7uyh&uN$GxiGkH{d()?;d&d+6VGSEc|))Mq{$!j>Q9>7|2%&v_wR4RdE)iha8BJ0=ZWXn;r9OXYx2bW_;tpgpYZc;zn{>3Z<@TGcijo+{(Wya_v>&t_v>()eyF!;a_Vj3afM$82<86uC`~@Oxw$UKuZ^4^oFB{TVAf}R$n*1q>)Gk_f?3a2_vci5x9h#8-rC<6pC9Z$da{@Id~JK~`N4G_xxKqrw|oB`3-%MKvCpjA$gf9Z!FB7`nKU_d#?KS=lR6X5{dybD{rVZs9qLJ%oH~%mLv<`o&UGP8PJK(0bG-=X{&gWud#(%N+^>`2+`le_bH7f8^ThjB;eM!-ejdL64Cj8GOw*q0PMY>ychclb@_E<g!vj*(`aC?stk1}sZBv5l#NXF`9<F=g+~4nsJaj*nHuvg4IQQ?<BE$Zj6I}n%^^?u|cXQo0Gre`|=V@M#_1lNmTbi8pmL_Mtxns-C2+o_^I_6!coa57jc`UNU+ouc9O-^s#!nr>`X>#T>P43^fx7<20c-+W^O=djqf#NEUUi-+Kw^7wcr#o+<JTX6h9-g0B_lyjl7wg~w@3<4!jtJ)Vs&BpL`*zP^={?>=9==|5UDs7Tu8tph_4BCPMXiSpmdWkk4oA~FztOq%x+VwOJ1y=p?ZbJr$7!#hb_Yi!2j|W2Kl3dklhYYbeA|-~gSr2B-Tli|?$1wraD2MzpYsxXyu^&)c>MDipIIO!*xp}P?t-Bz_t#;pev$d=aj{?QAKT3jw)gjY^g#7R>bP8A;%|&tq}p@+idAa3G}zw1?}}xet8)MT&6(eJnVKJ-ceo?gEK}#jf1YyTg_Wwk|NQ#Wc9r|j$K5x}tXAiR*OA=W?N<l;_g{C4&w6)_Ixer5+Uw#f_g_D^ir&9YJucoCh$pvNr;f|}Bkt@e>(z02zbR@TU$4f``&?GGj2qQ?<o!fvee%X&KmPlb@m@VPspIngY;@|oDo?zReCq6GwcdC?J>Kq)Eh^{z`q*n_x2pd6{6nlz7nS>;qj1W;zD>2~^D6OrJ5=s}?!~Hm%G`G+o+t8op?LJp9qPRBd8A0&2X+SA`=6(BqD^+Hb<XFt+(YeBgYEs#xy24o(m9`(v-3B0gSr2?MEk=Rz1$xUpJTLM|3<a<KNsqJdtJ5nKVRyWd1F_wz5h8_=dp1r_dhplKb(7aF!w*_?AFYu^2Fz&H_zW4JZ|Fi?YAw}IiH_*7Zll}9v9y`u=keVqvnC{J2*oZs`mc(P3$LjsP_K%Uz|ht?p6Ks{UE2iy;sc}-(#|GouqTVx8*k5t8>10W^Mde^=}RJzBlJyuf0#rGv6z;n|0Rt!`}B9-H{Vj?tfp>x_U_E{`WVXTh8nY9yiMOMy>ky?N{rH@6TH8i>f@z_if!DTB_Xtp06``m~QWXU%180{lVkL`JS?4?=X4d{Z_s=ZGV4MwfDc5oyh&;`rpfr{o(DK#OpA8uY6Rd18P0+J#_n@ya&`g@V#{_YoP<GAHM%?zf{u8{dwm5^3I?-Do=dBzG-9CkN<sqw`v<T9{>CM*6Gf=AASeGE!9iq{_h4j<wonA-x;uLPE@)7y97@AIS14{^ZN#Vo|qqg-@y4IMUCJ8odmn@eAR#AcNJ1r>+$=)!?1Xro;QBC!FG12Jn=gZnNoHC{4RuB<O4Mx|NRAL=t-6PzekbC{rTbdDBL}n4yv5ry9nq0?_D^5J*3<7dm7=~|2+-og{CU^f0rYi$7B4C#}B=Adwvfjocq5UVD}oW$HVW9g!9DjjXXd5U~qmSCA{AmNaTKd|94KVFI4UQ-%APS{_mwYNlSJA9cH8?H&(wU({|JFp3%zxZL$B9#mZ@QY8Ut^842Z|@9F=POxH^PS3f0FzI=sh|9`(FbNh}A|2>xfbOZ^XM#5+DJ+Syb_$>Sh5<ZU~gvAfT=i!S;_!52$7XJ{w1YbtNpWz?D;-}!x;LnlpRs19@egeJ<UqQlg{5UNB0UU=vMZy>GL$LUM_yT+m34e_5g~fNlAH!#m@KJmxEWRB+3LikiyYa2C_-1%FoQj0E;hSLb4e&O23liRluY=d)Yw>lk_!@XEyc!9w!rzC*SHi2{6-am)z8n^R4_*epi-ecrOJMOu@KSg&5?+WefW>3*LU=wBeg~fii>JWvz;luC9Q<uqd=@+ho{fZO;xl0JY4A*VIuf3WPl3fJ!BgSMNO&SX0Tv$zPlU%K;j#D_So|$`EIb+szlpyAi;sfegkML(Bk>WixC4)bUqiyf@mFE-q402c7!n?W4~E4D!b9LeNO%C=9~SQi4}f1m!oBf6u=vYxZ@32%?t*uP#b1QG!0nN6GyHj2ygJ+rei#WC!0&^_Zzg$M0R9&VU&gP%;``vs@LnW56@M2N9}7=~UqiyZ@P4p(d$<?e76~`TpM%Bgz>VQ2kZ>iu3M^g}t^_}bgmd9}VexEmF8B^4e8ckmrsc8t5AY56dn9}bzYL3i0$+kZM#B5?1F-lSct5-z2`|Ry!{X!N#qbm)JOUpIi@yYqfcqlhj(98hIlLj>3KoABZU`qM;fL`jVR0LN7%q#1i{OvK;+5eda3Lg|4=)3Y7lre|cOl_y`2DbW1kMKEiG;J@_rl`&;Vf`wBz!9p&W(i2;}v1?r{VH&eI(oo?+S~*4tIiIL&Ed$7%aX6o(FG3!XM$MVezlwkKiwn@Spf~Sp1eGkN<>kMZ)>;Jg|5PI3HXR3D>|Mg~gwSYrqYVa2x!2So|fp4cr3>55tGT;^W|9@OUJ=41W(6-w!W?4<O;I_-C-VmBHhya1s(Oh~Eo~SA)eLfyEz%3&Mqva0IUbi#LTMa8)E+8h;iRZvvNwt03XZ_%pD0W4JP03JI6QYr*1;;F53&BwQSC2#Ys>i^Ii`a3%Z+So~?Y5?m1p7sVfk#h-$U!WEEkdHhLOygpnWE`o&1;Wc6LdT=@TK_pxkZw-sLgX_YrkZ=_542!=6N8wILxI5kp7Vis-_k_i}!QJ7GNVpB&0TzD&ZUZ+*!pZn^u=rzeGF%1;XU7Y};+f#=@U<jQ!XMy2C3!4<82$iWg@h;LD`4@7@MPFQ!oBg~u=vYxZ@3*2einZL7JmkQ7OstiE913b@rrO|xCj!?i9Y~~-vj4_Ga=z$EzdK+;y+m)i-fNs;ZyiUSo{N6+=chzD{vPUUj&O!g2hL|E8w|Ecr4xr7ViL$g$E(w9(Z$DyaC(;jw0a}_+zkmHMj-b7zx+HOT*$1!nNS)NVp1K5Ejo1SAokR;bM4pSUf9S41NF!7sl^^#cziT!}lTK0{CsP_$_b&I1dueg=d1rli*zNJxDkQZo%>|1DpfC8wuycGs5Dx!s5AM@$zs^xD*nugV%?}JHd6}c1U;_{u(Sk4;}{3LBd<`ZLs)9@D}(468;?j5*Ggx{v7@T3E!6Fx!ey4i|2!HgYzTd(s)T&yarqvehdjW#2dikZQzD*6bbjld%)tu;GXcSNO%H19u{8)Pk@&r;e+@ASo|t{5dItqXUO2W+z$zh7lg$N!Qv4(1Dp{FXTz();-%qia8@LoAFl$7SBCS$cOv0@cqv%CB%BY<i-hywC1CO5a2_}}63&GegT*Vsx!^mH@a=d-SiC5FJDd{<XTdAL;^pBiaAqWY8(st!F9+WS--?9q!5@Uh>%#ZI4<X??cq>>u3fF;KAmO%nCs@2YEZz|oZv(f5TOwf_Zw`wm!!~?B621#B1B+*e?}C3$@+5o;m-`iA@eklr@FpZY1z!b=Pll(!Bav`l+=0b=!+qfwk#KXo9W4GV+#IfpgsbAUVe!gvRk#=u&W#s=#dE^B;oFh$KbGg2U~#!G`3DJqi-gbP*I@Beuzz17d>G$=?}f!zz~XaZ@v-m*cnK1oiVuRtd%#oSQAl_I9)-nQzysi(NVqfJ7#6PucZS;_;bwSsSiB0{41NX)*Tc)f;>F;4a7`p!1AhP(FAUd!A3?%Z@%v!$0&rEh5)!U}=Yhp@!4=?#kZ?)-9#}jFToNvhgiGLe!{Rw%@lvpO9k>Mi1QLD$ZwHGHgI|CLBjH*299Vn{JPY24gpc7TVDZo4WAIfZ{5$>!EH3vAzw@_nW+Yqy&ku{2h6}(CA>m~FF<87IoD4TY!X5A^EZ!6D0QW({Bk)&Y@d@w<coGs`i7$u655g<qLrC}w{Bu}b?hn4eGs5E8V3F{RBu~OW;#pzw{IE#)ha^wJ-{W_};`v~a@OMd`gulh}!s2;gk?=oBo`nC#bHn1fV3F`&NuGqS<9EP!a33Hn68<yElkgvSPB<s`0m35T-;+EE|AuFVGjksxEE4`E$&>J}_^t4*+y@AYguhPmBzz11`$O<U+y~r(gv%n~+IS1N1=su9cuTk?*Y(;+_yHuG1HT`>pX+)KB>ZKPC*jk$T<?X&Pr;|*%}6)}-vo<Kfm7g7Nca_eBrM(+eg*D`gj?V*!s5;07H~ZzTn(=ai&urK!NrmAeRwfgJU4tFoE-`OYk7V<EH2mef06KaNcaN&Ei8T>_OI*0$MK!`VOV?vEWQL5p9=4Umm%Sq_$XL>06Y_(h=fPuJz??A@Mw5A67G+;fyJA_{o!6nxEuZqEM5=p2DeATt?`<$cn!EU+!6^l#UFvitHMp;CP=suUI`Yj05^i4Lc(?NhhXuNa9y}I5`G*n4vUw7#h-x1Uw|KnpGU$2@xie8EO;P10|~FgH^Sn_;C1j3Bzy(G3XA^^Ux9x^!da3$m+P^xcmX&Id@m9%hd%_1C&T4n8woeT8^Pio;3jZ)Bs>J~1B;J<hrnZy@KSsdEWQ$63hzO}C-FnD_!qGF4Osj~_$2%h5{~0Pz~bM-arhDvK7oG+i+>BBfImgT7x8~!@xS4V@C77%9{&p#zYd>=&mrLt@jqelKj07HPmu7(`0udzZ}7+PaU^^U{{|NS6+Q+ZMZ!n$uVHbyjvnD};jfZB3E$0iwk%wh>*d|}1MmY}7w<;Gza)7QK7-5kQds;nd<K3W2~Wc}!{RCMH25tf+#eqWi@yT*hdUwRmUu^4yan76u8)Kt#_Pf2)!>KWQb@QEUK|#`4=x1Xg@i3UJ1j2OMT@_Me?-Ec;@`pI7hwOoD0~**jUR`_cf#V!VDXvoZuos9{2o3L79S122QNgzZ{x#Z@&54J@H8Ym4(|nvcZ0{lZzADW@%FHIYxq_86(rmbZwZSxh5Nz1k?_lS6Ii?v{4(4f33tJtg2n5?UEmjya9g}KEdDqw{yZ!`5N-<(LBg}~8L;>|cs9HV34e$mfyJ-DAHrWC;lJ?TU~#!_{l(wHcOv0}_`R@rIk+HP9tqdPZCJbsToZ1JguCJ0VeuhwH+TRNeiI)9i!X)Wgy$gPjrbl|{3I;?5iA~uH^RG-@CN)6EPevs0Ix^FyYNq8@r&>-cpVaU@e8o{dDw;5BH>j094!7JoC@zm!aML!VDXRP9q@J}ybV7Niywox!CR5=8vH0Megs|vZ$ZLm@vmTUx!#<`e<2q?1D}OgBjLID`>^;lcrH8|2@k~Ig2ns81L4j{xE0<B7H<i+f}cdfkKpxT@rU6@;4(<KFkT84F9a8cb0Fa){4QABf|KB%El<Lq;c~qZ7XK9XuPegm@O}7MSbR4u{yr@J9=s3Ug@m`_3t{oM;jQpmB)k%z28)k_SHeq?@B;izSo~FZ0i1$_r{k}{;{D+1@MI)B0q+fqzYI@+#~|Ui@b0j97x*ps4J7Q~FT&z&Veuib_-xpL-$BCL@lCM!hwygz3=;kZ{{j~O3;qWF8wqDk@?5S5!r}$ttZ)PgSHR1|;x*w4@Z(6h8Qv5Y?*=!6yCC7g_yAb^O?WW;1`=L^&w<4^!s5GO@eS}2crg-Qgs+FicfpI`w~_Edd>t(A!VBRANO(5B78Xy1XT$T6@GN{MEWQJt1;>!^Onf^mz73uU&p^V{@vX4<8hASV4icV+Z-K?n!s4r8@wxCk_;n;a2p<iL4}=H7U6F8WyfZA`3T_QQg@mi)Pr~Alz}4ZhNceud3@lz4z8}6D31`G}z~V`8M)()Ylkiu#)N5h!&tShU3&-)3_&Hd7A1uBL7T*e=gpVTOL-<-)d?kDcK8S?(;7eig1@Im?6$x*~Q(*Dw@Md^55?+N*hQ%kqtKj8G_+5Mq-1w=a3^_CYpZ;Hc|L;F}Kh;wIkH5qJrT$u1@V{*MUtftYc{P6O7WtfumEphtlZ(SwQmL)~0qK*aAp'

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
