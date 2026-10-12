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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dcf35ae14df947a9a700b8bcff8db57f/part_006.stl', 'relative_path': 'dcf35ae14df947a9a700b8bcff8db57f/part_006.stl', 'source_sha256': '0ecb5a5d03f24eb62547afa8e5aeb34e21ce551990ba0f7e63115acdfcc6dc6c', 'input_faces': 1200, 'input_vertices': 622, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13810867071151733, -0.47523099184036255, -0.18341082334518433], [0.25693178176879883, -0.3150395154953003, 0.40828996896743774]]}
GEOMETRY_BASE85 = 'c$}rZ2apv-8@4^WWRN5|9~8+FMKTN-$vF#$93)9j>L`c=$$}*DNKk?#2_gbJND?GT4vQ|nCPWbxGwQcbKiBNe8TPOG>-(&F>b}msO;1lxcTZ1GPuZq<s?<3x{jaFC%RXQAYz@njc*x3Wjq5*Z%;3KLN0%Eua$<~?&G_=4r;A#3Y}ux3j5W@hT%uq9(S1jis1YhrYe2OUWkV$fj2Ja$RPW)vMvUs$U;M_shmP)_=#L)Mdu0E_-zA@{RH<yJa;dVR=R*IN|7A=pf-`&b!MH?qH}?KaG_teSrn)}gDxB5$;ehX+%XCdNVTby5qi2n8|J6s+=bCPO>-^`gKYy!J*9mbx-yW7NMc+LhGWlEG@#ELJ{`{?{4vjXy<Db{`pAXXVFWvO6Iqsa!#<$83(efO=7UkQQ3mZQa^wW(p$Bi7qACe=g{LZuu+v0q_)9>LFed}Nqtsne^X*=Tl<#!&gWBka4xyE<M-yVAJNL`<AjVqe6Kl?wEf5`LejF0ozgXP|-X^#75$vA&KSlg~wsq6Ed;-M6MYwOEe|6%nb#R{wMmA~)*^tgxb?vFZdp4^+waSyLGzRhvng)`ob@;R@BfNyPGYK|LTq<$z>Pvbk@^^IL_jvHE?bHD$*+^Tb<{c7b?^zD&tubX^4f8f@={`yb2@%8B_|M^NO`gWG@ulxPT?JmZ*Hj&Sn%I0`U{)|E?`tFub^*WwaKm2L)z5aR*)jgoc?eyyhraWH%`fmL`li&5dd;Im25K~mk(|Mxt-Ey@5Q)#1oYgyft{k5gy{eF1W;6489Yj=9ilrKE_u|59l>%37k%6ES%lcI0GRKnDoiyx^|>wR<Frk`9k=@?JKf1cT8{JIIow|eS05b9pV_|BVsu9)=n)6fiOr^(-nGrmQ?2)7@g{*%9IJ}+y33=O}&L-QG{>1}Q2;WSx|Z+rdG`u@D%cgr<Q*}ru;-tQ+I+y9>N|J3VcS2?BWcdt-CT<@wmKJ73Znr3{v$xKro*K7Zk$89&hcYUo6CZ9;@y4(HN*V$e-%D39JPT9W_bHne4@)gp2CcSdi-=4#(%5C%4gFDH(808mgnxb!I&Y<~E{r7_SPVFOG{q+#p^SSY@Aw9N6^_Typ`Y6ul+vBq6c=Bbm?+$$Yy5G0IKE1{0q(86v+pWF+_!fVE2{qbf?oZB#BQ{6XXSlnT=i9WK{q-68s8O`Pv|Y;nL*>o++K)CczTI!4xo%d1<{!%7=>6k#u6O<YCE-qsDBmq#I7Q#-Ia$y5NBmsFHyJ<czH9#WW><WDqyKs(tju-E@4J1QYk7Xn8RgqEs+;n=X|t<;JIhA@^$NZAlexauBfZy~^p$d4_qQMG{15N=>oYQ_ucrUtwRimW89CQH%6C5RsO2mj?YqmmoAN|zH8H-M!G7DEe_(uYfBbr#mZ!KWPw0`BCcRU>*xHoRJC~2FF@9h?vHHKQe!-Q-j|^?0^Oox4jUOCmoF0!F-#t6V95;M^j$ZfiU#`~c5k3A`E9S5EUl;3k<I8^EYgcxIXx}-#La)n#+UmC`wAz1N!VN;kcPH$8E2Z<YKb`beO69lLH8*~6JhZkvss6=H>N{yPpNR#@CwiQ;8^&t-y-ylHRQD^Bznk`-NJ{nKPMoHGhS!a6cl$%@CtZKzJDca}{j|XrZHMQYMf~l`xi>w^500PCz(3yfw>M|tuuD<?&>lKo#SM+}t(`ly|JLkhd@KD6t5U3={2f=NR1em+knw}#r!!>f8z%khC$(KQS*!Vso@)HyIB!|~jPHKZNb?Wnt7-Co{O^@1ov(HGY2#Z9Ub|@Of5!!FxAStU-=&aAZ(o|P^|RsP3X{*Vi#ndX5wHDa*_q`jmERiw%QExt(+^UA$}RPCZ(NpQ`D=7iKQInEznofX{2%+8^v<;jn!e@z*Ns+q)|B7sz0Az#ossK}Z}01V$(&b{L7UBSJHNlg{Jrg0#t%Q2`>63pO;A5D9$MMUFG;aHL!Mr2%Kh(k<A;W3Q2&q2ubFaiKXQ*wIUMKn-M>odcop#N30>o({K(ctDV4{0Y@P9~Tv<)|BQHO#?P15u>aVV8e5*x?&L;h-#+ncJugG^LP5#zjHx?Ry;#!lx+xiF1zglzS+Z*QTxcBE4Z6{}Ps~;G*of&f%7=J}xQ~t=6FLa!l)pNe_3uMuL-6riBlRis_`TqKe%-?e)&gVPJ%BJYMyEdBqUC+-`SM%Zi=;n#n`}^{j=9%Mie+;>6qI`E>)f9c}i#a;)^89zZsDGr2j<?^HzGBX6XM=hE`m}TPG3Bw2<<sLbK8Md#(DXO2%}uG^tnZE(-x+#Ruh-(c=6-AqjLb3RWPG+}rqg_8wJ^T3=pTI^wCZU-U53my`S+}^{c+EDy$>$AJj<m2uAR24vzA_$Vl!s?>n$=qgSLnHug>t-TjcDSLw?`dSv^JHUU(%wCEuCzrrs~^7SsNI`p;KPdT+k8tG|{fS3BdoRqN|@{H3A#MQUsMEuC~cPc=a6xk3)(J3Zgh`{s);>2a(5JKg+yZ``ifO!GOm<z?f)sLu<bY_qg}23DD-eopnbzN-F9zfCpA?YvsYtL%SkJ#U+1e5>bNO+RY4&fmTqJH@1L^NOBtwr_O3BjY3LhsJ67CmqxDHM&kT#~sm6pI`EwP`_Im_218KuCG&|l^%ELF*BZ79gpkt=7>~!UfJ>vHR<kTG39iJRMho?wM~1Q;~sCU{raU1dR{x5^)i3Ix6tHcPbi`Jq#oYcq??&R+exLz_5Kw<uA@meYnqmGKp9PM{hC2EX+B?Xrnb+KqidV~y|JeDujMn;cYbeB*Vmri_Px|E=(IEb!1emvy6P*f2lr@4lh1%FTF>9N*77V}-pgo<PqZE?wO9Yi*nxHZ?W+1-E$7*$L+bk4LuA(~^<S$w%;Z0|iKfqt|6_--CZ7(ywH`K2({lD+JI?quZ|gcni_V(<*LjZdb1&BRUu3!Qo!yVTXpWnwuGU-VIh`lGIewnM-XfnbzUud_cC}LU?GmMK_<d_lvHAY`blMG8zi@fuJ8Sxw@`U=$HoiUd+ya07SpE0vd7Ub-(4_bJ%dM4BzV}=f^xdCV#z*-D=V?Cum+1JMYmxEYku4XSzo*Hm<=IqF%af(w>&Cy|O2^y!I<7kNK3Haa?hB!UxsJv8eDA(s2Yh?PYw>>H9-4W%N$)+c#qK+5$`#*Zg~^|B&uP|4$CD-tjGwf=lq!Fe?~Qv20pG2EINtBu+mC2IdG)&6<&K!+T4m2_K6z*Bc$NCJ-rvu^wNl%)qw~YG?aVml<mtA`<UggbjwgF&=<{ZH>T2VUpMSv|_dT7bIjd%<pL>|`txn#0<{abOYciR6Q9`k>nJ2jU78&2UHO%;t41LYKD0Jd|O<(P%@!gYo%)H3XS7wdLfAShro`n3H&-;C+L`$7_HP!h>Bwa`2+n3%l_cgcaHZy-naQkUKTPN%Mv*<aUH<n(ee%-7(-}o`TnI|NyTci2U?x6jy<nP+=uJ70MKix3Lb<X{2?wbjD4;kN@T+-xk<w&jb6ZgLQo$nYw(&!;`T>JYnYfV0FcAMjd=9SR-+rTG{?_Ard<LB8N=D3mF8`k>!uhlN*n#s4)PUBmzG>G!u%?H-{`)R1q1=IfBG=<jr`=hfgr2RLp>^gscw8zCp`>E#N@aON`uV{Sh<_=wFyY!n$AFfeV^WWGiDj)Z|?&@<tvQAIeac1U5<GaoNj`yc`j&0TahbL%%U;T&n>+u&feZ>Ph4!<zh_;$Z??->7wCORM9)7I2;D50A1?f*Kd|3f2P=jq<S_|7|j=yTkvIDP)T+)~r0&!E@qkzK}jpMORD&b#z^q|ATD5B;^k_*R)XZC9;+*Y%>YE7e~$RQ*vyj33_dminW{X+B@|)%0C6Z7|0v{fD-nj^)jD4`0k>eCvlax}MDQvNNT%`sX_9{QP!iO~1E;@tsa#O`j*VK3}hYUj5F4HUCCyO+7@uo~r)A@#;@ns_nDQ9?k!e3tIkk?R6bv&VJ+Dt#0W2gmsU|Cm(4(@kh0v{?|;;tH~+#-;USxH7;H9`(A&vo;`mt%CCJ{=j~<dnS2taozr{<eW&w{2_Kt$+>b76c@ECf`uz8(mVfkp%_m<Sy^hoF={n)|n2jc%#Z9$6ym?3a>7BI3cfYTr?@dB$E=BpJztVcB{F0Wl>_f)4o^7J(?=8C&<<s92I!!X^6MmaX{(1Gf+@EW%OTrWLjBlqauH#ID7mOcz^aIW3jd6N?M~u~RAbdc}Kk<1z?k_{MJ=|=t#pwKfx(+b3=(Q-nUJv!_71e%S<SFA@C2HyY{YdU8-<feu@27Wj>o~J;knxkAYc@^P`w_l3ZiJc@x#~~v-S5Ib?TSk8jX(CV+EMAf`=+(D$T5HVr1fX}=ji;oUx#BRMWy$~$<Wv$(dB2oE?7=)UC}KVic0U@e}m_n^j;uvTx;#Y_>|JyXBWh$l-{`?&-2B`D^caCxK!tFZ>@<w-~Ub3`*@GC(dDUGRp+aROGcL`yRGei&dKvp^}M)>w*S%RqWx8wHT~Yy(SG*RIv@C`$c3nKrr)pYJWEPN`PTaB#*cioIXa)n4ZYuWzI-sMel|?e`|oEZPe<i*sk-s)MQaa5)myi-y8cin<C&=PEbVK2d+GKgQTg<U=sY3&-<zV2o9hkZ+XeF-jcO;U%SX*mlJdWmMe|wuLZ_(o&M`Cpi5%*)EvlRyS{Oe(=FFz3dRS2^YQ7XcGfeYexmEjhk7lMlc)rtehK>&-R$TV`?np<U*S=d9<y&vJQonk>sC?X)Dro+>w??PWR!s9hdq92bq3znPCTc$S2kE%<W)|Z+?~l}R>Fg-u+e;qR^hNc3cWCVt^{W&&zO^-nj(bnPs^eAu{^|$D&(H@0HJ`vZ9O^Pe(>K=pd-!)<FADuWRLgUsmflBh{G#n`$p}r)I2_tKQSV<*jMDrW&l6_9sP~K3FK9l2`-?San)=+oB41pJ^6fhpb^b8T*89|nnd);tayse#D9N95MDLHC_5K(c{AyJG_S9y2e@Q=2(@#3D<?Pii%J=S@_HmuZhHG!oe7KK?&%Lha6~Bq}y8dauu|~_&dAFu#o{%sgjb4|<A8PuEU9|pdWYzX?;-c0k^ALAoQN6zDuWLT%blwtPTS4zrl~=!K{{F)UTK>0xyWsb|`Hxdu=RfwjwVM9mHm(2b|3vxTJjy*WSo0}*@;yD@wt8LOXn4`@d-FGI@=i_P>r>5VTYb%EP@9W>-<t<Iza7wd+NU#in0g4zGo67E<6GlDGvm3{{&$^!rd?xvr~RM$Tvj~BjN6gj$Bh5Ly!YNo^#k){XVDqWCom5Wjl8Vs1M_yb#pmkR->%1<{;T@8Z>s;$Tz!ujYnl66!iuyz&EJF11rxFuKlmIG-koEomNWXfBeJ5M@gI0jsnJpM4?Nd|M~v9%?~hKajM_fe&Qw3}++;U+Rr3ivXF2y*=y3zjW#JX8G=1PX&OW<mr@z01OP|&D|E{a&6?jgx)?U=~f#*%n4?b^(n`hl+@(Db*CZsN6{NQu0bF;Xn4?Gup{sYg~o*#I=b~awvZT!G<x>d-2-;_7_T>sd3^@HmG_z$cb*wfSxu1nxQur7iBz`Deri!^;;-6L}G8{<E)PIB_TrVp&ccz$pl#`A;gFwWe0drUsTb)G7@J}`b@T_`g6nDK+_NKWl9Kk)ZQZ{5lBgX>hDA6%z$fBWSFfB*H?!R!+~_L_eeSU0l<_uA|4r`|f7TWiW*e}DAW<vc&Qj+c}^u#T5-weddVXMSC;7weFoA6!37_|DpIe6O6WuX_Fi>y!6~8{b>!wC}&A{=(^+k2k*IyCqib_t%eIQs*Jg(eI5PTz7SI<vd{i9$2TfD-<<;a9!7KR_=hmKCSwFb-sPHn&!j0v0Y(~Ua!B}9q`w)=O_HM!}!+Kj5_|8F0b{I>7b?$tXDhTzt!}?b?<S%YWl!BdBWZ1apvCz*45n{^VPqv>+s(FIz0Vv;|JI6Lwyp5LhHeG{>b{=#t*(1h&0Kke&9WVy}pm;lZN-&`QF$2qcv932j5ftI6>0~-fK8j=HUn4gVc$*{`L?l*+T1Q$~yIVFXQbuus?a*_`&xtZvORJp1}JW`}eJGRKMFiQ1j`1K>fh`CeIJPZ%XoO9F0%Of8c%7Cnq(1@IBXs8+zP@?R9*Z5TpHWRDz~Y+d$iSuL)W|y)z#4x7(1D;fmi6zK?U#7e44euW-#R=6#~)d+#5efN!OVi}(BPZ$%IK+rN9X65|+t;C-U!2j3@#zIsfLJM>8{|IM<R&-qfCKJXqhoW1-(f4$iazta6t`EB(B?`=Il_}<p@?Ey=o-`ftZr+(nQuv?~&=HDQn-Y=a0X*+pmXo~0S{P(>2f%nwzp1D!y70F%6Tz9wg0`-IMyIZ{-bzY(RujqXl-&tK+>mlIV73amL<OkosC)C=g`2^nMdw%dezSHQYUa!Eug2?qhQq0Gm^tYBLxNmLhLm!#+!F>*$OBp}7FCw9672^l@QMjF2Yx=;x3-{NyAEkKQ>qFEJ?mtX7M*YA(5NGy0<3F%((A}Uu`%K)1H*~&QdXJVfurI~#bWr`kJ{D)odCe!d&!^?36w4XT`-P?t?4OCO`&R2Sun)&>css@Nhra(;(+BqXI1|$xGRF<<3$oWeVf^5}qa;7L?`ToALn)nCc%*Io2lgYiY^ui%?1M`3JI>c}@3!unO4!{={lGpeck?rcQaUf|+89kA+_&cWf&E?KQsYvrhlB=G)er0+3;nZ@<3{g83-4a7=NsI&c6*=JPhg*$6?awh5ALJGe_$US{sa5y{`oA$^K~o!srj(4&z?M2@7Gyk4yROpYj@7WDV5);SVaB6enNX~9rc6z5_4}fzPFFjJ<dMH`a4ogZ@-&a%Ny7y=^V{}#NQ6R{g$5pz<$fj6_5DamA7xxY2QTs;J%mk9~|*t7jIvv+wb}j|8?>9oqB$7-)U0%z`j#wenvCSJups|udMGgy?wLsZS*@0d~e^ZbtBrhIz4yY@4Go$sPD}y8ozA(aJ%tG{q^SU?@jUp`+k%Bz`kF%>inbr`t<e{+m}Am^YWh8rta1G;n<s+J}?ejmr@@y%6-i_mrnOJ;d}d{gTB?Pyp99-?l;Ac`LCC^@7iA4{FwiGdHc7M{J_3$&kyeFwwmtK{Db=*AHR6aU!O_$ef;3Q^dvv9FWudK_gGYYvhUrVGW=tsf$`s6GTHdSan&um=wp99c>D0J0{cJq*F)02LHyu8|0F-K&)*$Y;J7)Dz_{uz?q&SoIO+a3O#R^alkXV$1jd=cIZqf3jx)1Qs2>;~tWHfo@%I<+`wPzxewUGyKJZ<Jm3OeF4}ACG-W&Oe|N46E*7Jkkl_dFr?@H{ni;N%qZpCg;;iSL6c;C4=6}uTf_+5;hrO!!!fAPMrN%8~V-FSZRyBn*;96fH}JD?;#@Ewrn2fqVyZpEE4e-C_@l;j7#OY;2ScS-KDFHiaF$NTQd{VUyR|Mm60t4i_%-&J{j@VhGaug6dOudnyrmeu{xX@5O?-+9^J9zX3rFYkLX&kue_mXtp59hqD8r|9GIotnMl@6-PJ_r7=Y{NQ(RNq*ovIJa9?UB3)`XXn1xM4wjz-|=~V@H;-w4}QmIKQ`x#zaG5r3OzsgU15?R_^!|$v-6C<9=z`soiW#<%I|&W7}=HatiSx;_mZ9;{EjjyeegTVW9`oR^H2ItbK$d5`Fr1idVcUb(4_SK??Br`eGPkO-n0yEwZtTek-^Go4e0Ir6jn@g`O%a=g&q9F|F2JBD^{vd;s5Ph*o@g?EGsrKauC9)Pzz24$Dj|vF>q$|VK_6K3(XGaf^(wj;hb;=v>==TE`+v(3&AbWwr~r$4cZ@W1NTF_!u{YbXfL=6+#T%=cZb91P&f<^L5IOZ;AhYt@H22Xv<BP_u8wAdvvF;z6T(#q;oN8{I5(UYje*m`snN`EYB&p;3(f-PLvzCU;Jj!CI4_(LEd*zT3!^RI!f-RR4crWFjrN0E!+p^%a9_AR+8u5WcSgf-XSgRi1nvnBLZ5*L!GqCm@L;$jS{<&=wdqI*KS>DZL36`-;B;tOI31h@O%11kv!YqxtZ)G|A6x*=kLHE*!<o>Ga3;72S{N<@KZQ1fpMqPVt>IR1AG9yr2X2S9huguO(9Uot_-V8!{4_iO9Rv@62cm=Ffp7=3BixZ|BRnuR@fs(_077^O+8rJOcS4)Po!};D6}Sof1X>z?0xpH-g-gMC&~$JfI4ycQMma5fJVtd3d>nokeG`5cUWHDCSHa`aGVpk~6nf86E(QN)sh)&?gU_IG@EQ0Z8i5bOYtVl18h9Yu9v%pHLhHeu;D+dva6`B{8iK3C#nEhVaX1fZ!Fk|RXlghWoDO{mP6ua2ABD5RCD2B23HT{=HvAO40DT=^0KbV|f!~C$qore%ufru{R2RV|;f3f0cp-cay#b$tucO6dm9N9aVpW^M#o)$hFSs$>6CDT-r0?}4ggX+#-OwR$H@H9A3GNTKMVr8F;YR2aa3i=PS_-ZRKZ@poABA(FY2jS(efp>L!~2BrLG)etAiN%31+Rx!qT}I}@EEidJO(a-N<S>YZ{gqRn`hwP;ZM<n@Tc$*bPaq2eit1GzY9N$c7mUUyPyr>E^srnI@}Ddg%*cv!6nf=a7nlznhGumr$^Jl>ERq`RyYTo7cBwjh0CH(!DZoA=mNMEyc~TKUJk#5UWea-<5B5{@%$DpPTyPz7l#+1=imkKQS>@|6h4niKRnNG;Ue_S#&8k19@-P`N#CnS2)84IJEPs;&Tt>JKimgyg|>xT!S&HbaDBKOS`jV>htNmi5S#<e1?PbOh*6b(_y-}pA3X@~hu=Zh!|%Y$(3S8qcr-c&9t}T+mVh6F|Db<LKm3CbK8Jn^pM#I0N8qFIHuPP18$23)79I_EMZ3UV;pS*FxH()Ktp(SHOQ9v<Qg9)(AY2H}fTo8tz&X(za85WMnitLoKaQ4#ABS6`t>D)13UoQV0$z{41Fwf~pz-hxxETFY`e89bcrLmCo(q439)&-GKS9sKpTGs_pVAKt62f)RdT>4Zp0Lb;WxngplZB@c!q3I%{QoB_`58et4SLr~ex?vkhgOS8eg+Zto>PRqXBpuR=yPxfcpy3emS>GjG0D#(nK-^^5m-X_7fVC9DSv+o7HtJLg(snX;7RZlv>n`zIuianF>)r>-=B;FqB;1TlQBcIsBa7@$`~VB-Z$oy_l-;C8Mj0mz@n{vV_Iw9xYwF-QM9jbob1auD%u4WZSNan+xy1h_OypOaNWeP(GF;PxC7i3?E-g&`=Nc|esCMKHQWYnh&F&5!WGc+a0U1gv?yGZx_*QZei)VOBs?~;J#0>lF^pql80W^|Z$ppy#=v8Yk)r2)W2Ue-t_uHw{tb(kjY%Gp%lgLcvW)AZqhQhHzA=Bf@4g`X4*E7MdLSnGo+7-TcDSFmxF7#d+N$U=^Z<MeUX8vDuZCBk%i$I9NOTlD5-y6Cg^R-fPzO>k{}93#(DU#G_yl?kJ^{atZiYq2!sQbqe`1tlJTJ$1Uk=|J|MPQy5X}XPX7t@VguVNVa3Qp?m3%)EE`^qcMeA6}_cCGceka@<Z2^mRvy$(X!d+>fU1^(L@yBqkqTSJMa5wVmP6)RogzKVp;JR=bv@~1>E`k<@i@=%CjBqA6H<}C14HrQ3!}+;R!ZNlLVqB?%7DNldq9<dL?`6VruM<5KlYH+J_U@0ubJ2OQXt|i=d#kW_{}q<|v*>4*vgigY`Q9z;-QR^*petd~HdgZ7K)5ySur+P4HGVnjK(sB|25t+#fv$w#fH$HW;EnL-=x6Zfa0Sju&aDC=JRhA0&xa4Ahv38TDfA?K3NFkwk?T~L>t(~Y6OY><@o#owTuY3X65|^}csgpsq7C5ba6>})J4-|O8&r-VEV>B(2A)m`KTinHN{l^;u{JR_p|jvwq}hbthBv`Kqf*wN`7K<V^1lSvh9{%f;K}fj#P}cjBYF+~5sryf{RWm0{)G@uAcUu()8XmV-84e@c|y1zDs@_q-@-o<!t>E@;BTnY`GoK=^m%v~JeUxkg3f}cz%$Xc@J#qELil|`_#<=={0r*M{e<tLd*D4>zq{zq@LjkX*HW%oHA46~bTT{z-GxquCv*LF`L63OLihwBe1;JI3jGoO3jPU|>-`hIg;Uc8<l3j^xA1R-@GUd}z6GB}r@_-`2WJW49fa^Kv>rSQu7yhbsKsyL|0Tv=bT#@T{3C5;H6c719R^Q^$D@Pc@$gVWxHlm@3Y`Lvf~TT0;hD6jsf6%rgz!#6csKe!yc<4@egq$eKk>Ci;mhcM=r8bpaHSYkdG@G82oFam!NcJtgzy@43cLp1gzkcO(dIT0!n+CK_t7)(2k2Gw419)md6f|Uju8F}{R#dHeu%a!ZS*19>TmcD!T%A$KNG^Y(Od9sI1W7vpQXLV5yG#cv*1_ZC(v5(6Yx#iv9#Blgz#2ho8C$YPeWJ3t7*H_2;rB|@$h)s?n{L5q{OI+RzZitLuubt2;oYEa1C@6Tmx>3PKBq^zMB%loeAMS=uY?rbU(Ti-VYx_cf-5s1BVFVi|8k?*B>qt!vCWG!T-XK#HdPtc!Urhfewd9z)R63@KSgKx&~fDAJ~BIhBv?)(f8qv@K#^n*h&cBA%ru<Y6#~>ufkX9C&CiKkHu;TS4RJWC4_6D(obsAU;e|d30I5N5Uzy&49onh5_2$7@eA`?_!Mbx$0X0?gb$-}a2)-|n+FQdN1upEo;M0tK&Ah9^GxB-=~G*+<aw#^MsylHjlQuFon$4?Z-w9R^%-wIEG+Zo@@N6HCR_l{jaGrH(3iaD6k+dKMz{!C!%BYk5iWx^g`3isyyqri@7YSYCE5q}`k41zCM?ftW6`(K7vQ(y6X<>``B_-_0(uBOL?63={%a*aQw#rtO26`+!G(*`*G9x7KeG#uM3=@SKjRCpKsUe}=ri8>fbeQ`YfSQbg77i)PE7LpgYe&ku&mYGp>I7*Wb&=;WMUmC6aA_J`j~Hx=rP|ql5iWea%}RtlW;$@CR~$#<*iu>d+S=l9nea!*WZL?KacG78H&CL%l;+V+w{GqYQYl1x6oKvLbxVgHdwR<EZPIE2~S0b!NWNIRP;qy%GQ<N*(qOoRLYc|-@*maJFsZ;7-b3JmV|Iy^aZ#r+#h`revvW=XGpBOe2I~t5H5?BfkmH$%feOB7I0O#CE5dS2|tYvg`b9pp@ZOI@L)6y4~BauMl<v&Gz>olHzkC75yAt}LGU1sJ&+K72JHbq19vBco1-n@7Su&^LbwVcTpBF{mxlAA`C^mziHN30^TDDS-~owkU{zu)MqPL@{4sh8{un-u{tBOl|3n{;QT`JS#i&kzL-05>0*`~=LN~*2!E4b^;kED;+MZ~7^iwz;=X#po;-4mjx1gKh%^Z6RA^avGJQ1A$PvG1p62fH&;d|79)XP2U=M;PoK1m42p)MQ;N6=MP^1c|+{^%-LbO8KVVq{K?ENB`y3!D~>fz!gVXm&Ujei$tZKMX&DR)rsdtD*JbYH$NWxFgyD9)R{oJHY+W_GkyVJzNj157+0|^$6i73E>c06fVlSg$UtnXbhYU_Wl!2ji!OqP}ivmVQ;^WXfZT1oSEw+EMrlL#3+e=7NcAe{yawYBK$dg34IN|1TRL*!;9gH=v7O(B7DtKT?$`=m!Yr1%iuX^V|WhSgmY@bc{RZ=Mm>l&LL0-4;MwS_@T(kqHX-~vA$$eB3X96QUE#NIX+n4r`WpNib+?ERzCZ}yKtF?Tz{R;Ha-F>WO~tuy6zBRqg*Jm5C#L^a+Ge7DpBVop#%1(t_%iIEFT)O87p)K1g?}Jl$^QpJcnSInyaQcG2)~HF0>224AcUVIgug_;g+=AuzT~&?SC)ow6GC_fS|6^@`OF}M@1kGBci}9ts{g_g|9S%!`~!dg9{vHoNeIUi!h6xn@MY>+_(gOo>c9^5K9vxziAueDb2;H#T#F^JcMXJP4kmN557ArjEz*35E`&dX-y?+Q62cDpBJ9A!(Gl=)xF;bTMxTSj@XP3z@RwZImkHso3E@Uud%50?2;o-<;hE?Rcm~&aCL#PSA)G2!Rjzj`LO3gG!CB$#gm6Yw+CfHs3;#+8e~I3NKSuYVH{qMKn|*}vhlKEZ=w8@sL+=s7>(CeAb@1zi@Uv)h_*u9zD($8+zlHB7#wGMPdI!EkyE#q>A3)!O55U{ex$t&)9U(k}5T1ZKutVFLKnV9md%}I;9)xf&LU<4wh6lmVpfAJE!1K_r;a%t#=-2QUaGe-cX_s{f;o0ab@N9SwA^Zh86P`&M{elp_he{j0$8X^@wA-w3R@!J9LO63`)Iw{c+2QQ8-P(k34OH534Sowh9;+c-0R0m7+PAQTaJE<t;eQC>o#;MzC%hf~5Z(@NL*IknqkV5fUx&BBZ=lb@Z@^>G%J5kDQB>OZqx=^B%hw0~B81PP$Km6&^|OTVK6E?0owmM@5dI)BMxsxn>)>_tho=eQc7(8vPJk!S2W&#PGTH;K3|An8E26#NC(t2iFL($%4jlv!qR)&YgeRi&V6Xp7B!su1U%*@71XTJ@0>6c;(5Gg@Rp2@39(WGyqF=yY&}Upi_;*zL$?yCYj-~HphGXICzP?nQ`Il&Kv=-bO_SOW1hoQCM+Vm@LJwf<s^zqo_^#@^ZjY7C8S^zFUAM@5XguOKo;ryudJ#YO)Se|P$z*p#-JK-zvT6B9%@^i89Tj(};8-2`srWPKDj*Urv1{V&YkH#cFvkU)8-;+M(J>v_@8bF)oF|j#Q{eS(hK$HKI`I8m(KL!o{%jnN0{r@scO)L2$$~Mi@$TMr={XN!fV$C2sX{`SPF@)ih'

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
