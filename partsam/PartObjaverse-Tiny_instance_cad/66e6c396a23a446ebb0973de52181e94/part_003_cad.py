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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_003.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_003.stl', 'source_sha256': 'f9bdc9974e96fc47656bec6e6ee9b88b464e66b527ce1edc19d96a1d4ba7cf28', 'input_faces': 969, 'input_vertices': 534, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11740231513977051, -0.3685324192047119, 0.024251848459243774], [0.10409228503704071, 0.006183058023452759, 0.2526766359806061]]}
GEOMETRY_BASE85 = 'c$}rZ2UHbF`|aHab3#DOjvN(p&Zwwu4j3?JIU<-bCyb351;y+bj|wKtI*uqxqlj5CXFWP9<}i+9p1IVsw||&#eRr+9?&V#z_OG`^b#;ZOtE-!Le0|cTch~S!MAJvy@rkISX)0yc+_kZRBS#PH8#t=M(BZ)r%|(3m^HUeM>D1b{n?)O|O)MD@II8c+lC`ZRz598UEN3m*Z`jDuBl`^X8#Xc^Q29;!3>g)e;*T28XLw-BajEK6tCh1>EnUt!+4_I^lU3Eh-T7!-ikJnQjw`h-YH!w8$K|ISQO6GdtH+e;;|?5GzHNV3@vYJI<CPk97mIJLQ&oK9`abck1&g2@GZ*|BQ>1)*-yJbhPS4<2IbT&*$?sU3^`!ERcbUa^d}}V}b$n<i`Hj(k9+rA+sGA_aH+>VzAAcKu@kGgQZupoe<!7AF{Mk&&f3k<v)670dd~5n-lvC!-At`@xWAU|iLnObW>619gzhloKDYs{MoapvgDPKQcOMJ(tFOuJ!TmbdF@HIw`mj_Gvx|{1h<=X?Mh;J?3Qm$8bu69QGjz24iZ=5NO_I7uXdTJkw!tb75+RfZCcCXZDdeTAh%O#;7ZiGrbjoF9A*ZRkzzw8%JOFi@UMgD6qq+N};4pM(}iv{`nW<>o9-;n%{ino3j-|2(Y-~8YaE9F;C65pI3jPa8B-a%>Sn!Cie1@uQh9;_+#v_9T{K+YF%J_h3`{+N_M(qDZ2g5Nb64_VryU;gSMzN7A8_^rLgH$FEMUyFQlRs5L)#CQDgMEMt59Kv;1mUgiHQv~^2d0dzB+&m<|edd?n#E(58<(sQ!#bca&6yK~hM9Mdg1*1N*K8SDi?S%TQ50w1Iyqm~Bw7iT5JuVmeWqzXgdWrgSUVZTa$*<)+f%86iF705udjEv<%Yx%5zyDP^ujbhm^;!5k$~iP$`d9l}5B*YbviSB6o27jF&3~jlZT7yXPt`kDq&$5#>R+U%_=aCADc=#<0re@~5`OG1v|El7(vL<tE9yDqvXpQ9s3_%Y<$pmvm%P7*ak?)->c68P>T|rc<hSPc7hl_*U3|x)L>UjZ`%&kl{rCRZk9oHO?f=hTlHXD5n)r6cAAMI-$#2Fch_A0GDfzYE%1XOAjvN)=Ja`n>8_-3r%dEd&d?R|q3CW*feYDh5--G;RuSh+$>WLUv<}Q@qs-2W$pRxeH&q(-ZW6>`=+sk>)PPN3>x`j$PwoBb5{@A*f5#P2TJIX(ILB^ruP99uW(7$qBM(0~wWnT2mjdJoPqg~&Rkao5|u!!%dTt({RC=wvoWes??Pkz6@2kJ9mwA9C%d_#O|@@#1zJ-Ir@fB);^n@x^imi+Y)pUr0%;D4!kLw>Jwc3khP7?iWtLwxO3S+r-+Uhy3*7E654-ZezOj9Q5LgkhdJK3zU4{-oaUJ$xmOI;uC9dEuDcReUYvZ>hiSW3uGernbj<`@cqecJCqM!I;_>=lyq?w1X{b8m>2E8Pvb*dbuvM_ZZZ3URIPpyFTjk!iN5G{<>G{b23QAxou_WDH#trKZ$R@UsKAl)r&woxV{u$D>wz?d7M?svE@q;-`XQU>Td>LK>gRPMg9qM<-F$nLo$yX9xLI$^u#=hoO2?rZ~xu|_o;zFG9JwJ3*g6O#5gP-BKftQE#a4+B>iHm)l9~TQK_!@jsoY<?|E(_f92ZZ>vJq<pWE}KeH_(2kiYsx%$M;ur2e}1w>_A5Ri%7mYevk+CMU$#FLuLxZ{Z>L3$1yK_|`>}rF>(+2*fd;&Egv_LvUXRUwu}ttKD??{kw=d;tC_4Tn>RhsNp3!&%bkVzv~i+@_oJ0@9&&2k8aqI|FTW$X|^<E-f6eGi*Igvi+KCz7hKo9hB%+oE9o!Y(pu_o_p6R_9!wL}vIb$?4*b4b@?9t|^|9u)W8MwB5C6yrl)q!=5o!O?rugQCV9X2KM(IcW+e+kry+Yc@>fb&tt*>1ghWn?-ahVsk?@PqDAMS(u&V-RzS4^FO{8^Tv-@|X9A2ax&{GBIoUz?Z#<2-9)<R2X^<IwKqz&dJPeesPeC(+L#4-ubpmP7u&L*#mGuezfj-3o|ryY>R{`SM-4@0&|A!rwU#?Z3nw{Z-}pE~!tuXVPDK&6$a5eIwBg^B`vo=0%l1#5cY4Bx#=pA&5(j4U|*v6~@EWwOG%z^Ag{>dk*Hy!uA&=f5#HyYwP-Be*F=CBCYReI8)-SBl-GyDW|I|&U>qtoLB3(N7~aqaL-Q3m*gwgYke{n>zuIz#W%9{z&Jb*D%WM5S_}Sb%tt-@co~Pr{6{;a-0*i>q@BYr;Xb}39{%vm=&#E!q@KpwIq(gytx~U5nPnV0){hn6anV!S!IAhJ>(4E1;g7UQ{f*s?&|f<%qnyA#a-Y>!=a=?z>@F(4F+UpP|3z0^*P&P2rJN0y5g*2d;JOY!7vDHjPSzWG>1*4hocLqno2M6E5S=y-{dI9P$~j#=QS$dF6)D%7Gy?vMdAN_PF))wrR2SbKuvFUFF|#Vh`Q3`hp9SSRlH!s7ku&_EV{o4;ABMQ`>~*yGx(nuoe+Aqx-kcWS`l%`U<xvO3jlZJAH^ZE;ZhSZ=7V~bR_*%$US>GDhg4fG=GwJXTbwnI>ZzA)^;hG-h+-QRFQ>d_s`C>u-0=)lZYAx%0t<c$R7-wanT?3?^wnC@m*x}`g^-NqhX$ME?$;j7aCe&>+*VR?z*t)G3=9lja)ZeQdeC;Iq#Vfar2fMes_{ML)V;&vxm-3Ak=VY82t4^Jh^UoNJ^>9y{_|^hR;u~!)BF^;gD89{gKh`r@Vi7lNZN%5wt--iDJQU9n{`JMzn|#K)bVV`5;lN7pyF|-6**2-K%tyzVD>6@PTlUL1)N2PyT(!;$7T+3j4A-@!skF0oPLTNjvu^46QpSTGp^NWW)LVQ<U>nT4m6^mhTK1MWphZS(5Py|Le7$+W|HNDC=D5w0Z%CVU;%`or`Z%^65Z{>G2+v^`6Sqq{L~lcW|GARiEI1A8>V1>N*Pr43t3}<Ba_q6q;5S>3@e_~xk$I#6eE0X#{?=m-jFUJo@ok%mpOyB^*az`8;TQ3(eSOg{UIo$bSItf0Z>%Z#ZLRL$IptOq{TVWTw7LO^&ktscZ+MSIISG}dp4#WHQS$pav!9pqIuFG9_S-Y@t=a0!xH8;pO8?rmv*K&{FrSP)>rsC0ZsHq>?-2JQN~8V-y-<FGJ7}LqjqsdaEHlcv@kZvob@(}%M~+f2A|-!#{zPaUtkX&-!+*Z>w6uTbPIw+H{aAeC=1rMjwxG^f7nQv)zLxH!UD|t56y{gOMED<F*GoBX?<2ldJTAUI(&q%)p_=%5B~yI+dR^MtnmG>fr^<eu_jSdK;%6;@{;fL(zQYaUvwTtM7rk*iocBqh)ZaGGf%{S8HsU)ru9EXQHuS`NY+eK9EIouc-*}V6TdPkQl=C$S*L!EX#0P8pbf{;gAQ^Aw%uuXzx?kBS*JbI2_Uttg<JRx6`1TF85f6_Xm-~p#@1Xd$gvr={SUKyW`27}&?^r$-<1<qP#>vD&DCcb#tV_4`$9*c~+Xktp^CKBQ+T4POOEdov-xhXI&TDU73;i1wE50?d-zm`?b<w{o#vy;dIB7S1{%XXfRfEMhdmWK>(_eSQdDnG7Ihn3W`P!pCXy<jl$e%X?>xa+|$J6?nr{$!aXMT0~8|$DPZ#T4a@72=Ij;(pcx2J1^`Lg5z##^+j_=ble^*2wwiBIcmrUlRIK`(d8_3n8s<4><xLdK6a`qk02zGehSe;G9~-;G0u#J87D#C>g0AfAtoMTqa1&>HKd$kx(d*2^_e{^G5e?_>W$e_iuL`Q5Ufk$=}?5N~g1fp7UD?dI66<2mTwC(NG*tr7pvX2g2f@kD%E!OGHZ)(c5^E_-xKe9iak0`Z^ML^~wM!{1V1zSOf+9OD1`IVitG2|VY%>V@Z~55eMF@7==s$Jq&S=I<bs<2Oy(+2|OI=a+A-;OlsPG|L`9d`njX{+@;ChfD7eKQp?*Z+|fk<K)aHslWSY+z)zGlIzkJEW^G>p$mxn4}36Ra@5ASEqqLTYwUO#54wL_S%+vPR)}wFzZCJgM-0YEsW9;!_n+fF7&;F9Ue8&4ZJ0BjiyIF^Tx$6DS~+jyiCC8oYl(6Kyu~;E@xr<;$OY@hfEwcKnQO@Sar8lb%n@(aNcrJ5nXks}Ci|tF(T~KpyPcBu)DGRj`ZhQL`O9CBa!kL>c>W4mDZb&?8vCgEmLt9`FNFLDhb)rwX2$-Wu_bo3_!;AIy<<wF{(Hj2H_PXi>oq6b!uo3e1o4dm15y68`)L2TdhqoLh$lC(|EV7<hw@z(M@aco++{!3Jn1aH?fPz+U-qT9FpsVuS|!J`BC-G3com*6ZtRCY<B{~2(QZ4+e>5I`w@fl$Y@W06+>zW}e0_Kq#O<!rkpH!}_?q)1jGrH;(4N|*mGb*9hasL!n}GJIc=}iQ{UF3iySIk+sSzc<mbgX6zx~WrJRkX#7vKJUEB2R?N}-%yCs)XETW9Gn&8^@n@q5RMuPq9~bK#tEyTu>VNPOF%V^{xEpNSsgTj$%bUX8ts`cKJ$a!wAFb})N8V>}p{#5X&{WBgR~K|8MwTrTAXox!}gw-bI;b@BCo?0E0M^{25fd6^u){R`{2OJRufhmVNwXyJzS+woDTXTogwuD@cxdRcAMGjXE$+OHd=-yLgmp`H)kFO_^*=OfN1k3oGNJrMtY*4rlrVcqidy!b!Yy;`k5Q2x`C;v3uUAU>aUMO=CoFTU>e5%*v1IqLsr4Sb^y=Hr)9xDWmnjPvFyi+#W7a)^`PI*ISt`vCs?tnjmB7T;Fri^O?buKcKH&c{n6U)9l=U;TX0o~}2=|G95wWa^D}E3_K<&9ZVowJvFa_9-@Ae631%)OTC~jKeZ*#J76<hH+j4&-+GYPvqY{VW`w+L>8R4-SEZY_xnrwUAtZ%?bf9|d`BUFDZj{b#OJQ9#COc?j`6&*3)WXXt08~hU6>bryQ3WfvWjnHpCS8B`UR}hv;lug+|iF@lXbOi{c`m0U<cw+jy+fp)O@r~@(;Z#zTM>t_J6XrMLEMyiEkFYhWAis?{fdY9Li~Ak^a@W4%8MD5Z^eGP1?tHydK(T)#Zh9z6^P!9BZeXX#c$(#dnPV6XWo@H`@QOr}*Zl1ngrpUJE}iJIcwoZ=#&%(J|}?9{Vcs&c1Cl_PvYtmixYO;+go?#eP!0#(hiUvR!<wwl~IC*%rS^`L`yaoV#}sXRL#8y~(A-H+S}w_B7l2oB#25&BHkSr5XC`Wge7Y_O^_3tNjD|_f2}#XW~<dw?;=dwDXf&vOdr|KbQAY)(w8>UrRml4QB_|z2~pPcX@$zL(R`<|Ll!WPO&NC+cS(qT<VW~a;@H@a5-ME5%FQIdy@D)nu@RA8ixDJs)NWM^fXM$=}}&uL$wQQ(Z9oPi*F_c;eOHRI{e_Z;#*g)!}|`7TWwBD<Zu21_nn{X?QL`CNx53}5z_wMZ_9m3i>U$sW?MY}-5t6|{G)}%ciex0_j=wJFdmM7oh$9*_5=OCCIj}RudNi{oEIwfv@eXsd0*!d-@fOmw2wA-8p_FAGE~ZK;DUI?=N+w3PVo&(DTxn8#pY-q>!&%Azf)1XuUVNW&(~Vd&9kNak4f;k4%Y_wiEngiBJHVn4@Z4&y`3TLcIGqQhfchL`rP>g{_9`ye3W7Je|)=FDY;(bO=hgG?%ohzA2?CQr?xO0?f<Q!__p&c@%$2!9{rwo$#nVsD?Ow>woAovy-mWV$?qqn7d1S8K{-MDL&U$84dqm=gzFj^A--|wnanSHzX|ZCbQE9jvjy?zCe}sTj#h^F+po$#o1N<fZPKl&QoiBcRLb+hKED<_Vv6`DcA+2BMWG$OXPGSR^Ry(!?Sm}vOBI+T<7C)7^l$EQsDG8q5-+sfKK<3PV?;*Or=y$r_9COPer`1y<!osgEcrctL;V*QIG)zG>Xk6xe~yR8U&l$iTyKGPXqgB1!8~`yN;$>L<9T`cTAbHAo%s4zAM|^<@=+*1dXyaV{kXAaJIar(D!%Pv1FRGBFiw6yEAvN7=qmkX?ep@0_ys)Scl|y}j>EfQUQ|dJF6|Sv6!*JZehF!P{naI`m%as|{zmD+QV$P9>SKBglDMiRwHPSJ8>`86IhMGheO|>3ko^A!Vqf&rG?bJ5Yk#S?^&y^HuWv*<BxDVc_Nwu(w3~6?KQ66r{pN%Dp1UEgH}gE)FR#7CzC@itDBleBmERv%9`_xWztL_<qg%-J6bQvS)TIFSCyh5Xr5p$AlP4?cuQ|%69f!93A2AN~hb6_gd;6<nv)V5CULxg2Sw)U#Zo_k5wn1oTM`kY>XO*mo+r3>;fBWqEqPCWJ-XAa&_4IXWu2kRL@juUT+B1(1QclOi;_HRD&t|XJ9sR#~miRmHepdUuCP2!`FahIaPhI%7A2ROEJ^RtW;eM>=xj~|py!%Og3i}<zcncdWI<yk@Ekj2j{}At>`ZCU<PyDC9o(2w=^X87hx_5a7v}e-2;kdp?d<W949NHn@lhI0TgCp^r{s!x0Eq$*sN{z3-A<nexjQr1Djlp#<8L8A>1p648*>{q(&!+`=E*o4D<MYsB@$FFw$Np2!q(3H$PLIKQBjhpK*?-g&xvnlgSSL)lwgUZLb*fy~mNw{@pU>}ID~E`_n~(csiT+qWc-<1;+H(o!b*J07uB-WGNPXJ4N<Hnj%OVaZd5UkVP!9e3GtQjzo{_d3`yK4J|May19fGC25r3jzW}TXe_Bq^5@{c-&a>f;!CHa!pAx{3<3)kCLn=QK1ORm@aJwNK{Z4=+L?~wjAvu#8E(&xmt`ewsAf8v0(;%8hjM|8^zjH@qhD90&MeCr2S?Eh3rk9PZhQhYro7VElujZyyds-e;j<L9HC$=~6}=bbD4`!zq-+X3xR&bk}oYY}w@NO|iE9hT#;n)9TbfGQYoKiA2lPR>JrZAV<J^5J(m?lde+#@n1~cpj;cANgCY6F=nv4*ff&3*t<JWbw_f$rvXQ<<QQBH;1QfPyORZ^w+1k^Q9eL1))7}enUKYvr~LW4&0ZmPuk+VPwtDaKQ(3C8hHnx9UeF>5WO}V>-GmXP)^%A5ttu-*!Mb$?{Ku%4I(g4-S8b($SSORn|Bl6>@qGP?Km_Vje~!A8P<mzmdSd?sI^0Ueex*mmtM_<>#g`!eA|i!h}#Q`!7oyCp^UfKZHPa%B&^S0cV2|?-gAU#^LJQRA0E3{>RHcQuGjvwDg4n+OT~W?jri|(9oO3^&oYev81Xfi({kT5iXRnUzr7aUU)3m#=bd5+@ZW}`oTZU?F8KSzaw*5rJxJ=G1M6Gk?Q{5A_OYVvwql>bQ5W%Gcpg0GH9Cd;qAqo1UqLe_wU_o=6eQ!&&=12O@B-_aIwr<jl`N|<{@<ftD&|7Jm+%o^yPkySo*o78{yJu-%rhh1Z<wdcYRdkMaljPc)@Ll%+uc5)ed=bmi`t_R?*}b`@BS8k)%JKV;d5Tr)#m$XdGDtkFOL1-W7$t*JUtfQ%(xN#yLJTPYQhezbIoJ2{&JMXdvjxZ<&EOI6qk5!bgGBvqxC`Xy&lSbkM-gVX*Xk5#z>4e?6c|HhGD$f?nk2j1-nc6Q|@A3_j(6EteC9F9W^gYdm5cxv2J?vK=wJzQ!}L9v|0x+E|$E-bHTk})W5=K@%4FOXwRM=DEGDBW*N7>nGt_(f0g}D<4LIanqIe&oHt7=?zc4BBL42Th-1g1&@Zb!<vR$iQbBoMvAXen_p&DV?rG?EJl8j^B=47v1w)X(eI(vvEI1|K=V$|)$-i4~?2z`c@2M@{9U0wLiLXTsllOSq*7-8u4c`m!^@+_y>m5V<@#-qye`%j<V1LnPG}@==75GJp%D%5zp*HScIhy1B-ra*T4(%();JdhNZQwui!8*4m_W!kXA@IlFmVF58l<tU=SLW@I@#%X7_stAd<h`f1=8)|7o8`~T`rquIbC;AK;RN-;cWv6jV)9+6F|*z-jJE(;-`e`;Ks?;(Ci`|;>o@XUgH11haa#!cdD{Krct5%Si(Id{JOY02K{9{s8}U7ov19}M&WW<$Y=0S#_f~E@urIi+8NM6+nkdKmbSFHI8XM&~K!4H-`}~><{PR;WUp`Hh>ouP(6W<YP!}Ivuws_yse=YJyE|%v=Gx8eVBRt(8zEL?;-oM*^e(xHv1NraPm;FNR#yjlm`p1ZGeRxOKvG$;u_};b4XYuVpeKG!59mIEQE$ia`Q2mj-C%3f;MI1Zb41UxVykF{(UFMg0Y%tE>ETfdK^(!d-VOG43{MR~R-5c(Y_KJQ5|6E4d2eQV^!F(zE27cr?*&o%<VqIY@>x1?9xsQ0C(`y^vTjd@ozLDiL?nh^?B3@-Mk$=>5d9UtxvkTu*OizOUIV<*)+_$1%rd>ffS<B)3v|qz8ze4Wfd*n`q@SGT4N5-4}<1O;PXo~Nr;-h8!=s`Ycr{<5ak7&bpO-Aw{_*Fh2z8&0!`{3QJ@Du#yJ%DX&c6@)*w3y5@eeOcpud@z*A?MQ%Ou_t{F<0J4n5){LeJZVmujP{Yt2cB-Jg>MJeuou!UwW=Io<|}di*JNKmvQTe`HpzIqz;}7L%$>5rVqmWTG$f)_hg9!_PieWZXu!r{O9xVT}*U7i38?>&hUqN%Y4yYdf`1qxIg@Pe)1iNKB<!&n{!9NFEj-2$Ag_Q@4j4y-+l$&2W_q@<?Am>Ag<TyhVTAvCL;g9vKWt*pI{#OxFF69tbqHf&ndhQf3_a$jXqsb&W?Yuz6!sJe)sDyzHRVz#`!-HH+qgm{x%cv9rrgpSDKwxqWrvXaNqp7Put>=_>MYx@EkNe5Z}EgzC}IjpTj!PIS$v=^gYhY=S?%p8_!vdf1vy#2l0JDlU0b@<!0dD@5f8~>)a<aqc(|e4Ld09W^QhP^^)gK<lnbPzI(D=!gp&%p6`g?Q)=V;jWRD~oaninvETOT9KPGha0Kg?d9}p17JiL=r&Gl+zh>j_547J`<GZThyZF0<$+O`vEr#z>(+$UW0*{K|?+L!`7vCPT3+sW0o*1Xa17v*aA5C1>-TLr-x=R0Ax0l9yv}*&!H$Rn?cDB}Xpq!3Fk^j(3ti!upLfr73h4aqNgzwB}u0;N`>)^LIh4nMvyP0RA#J3KufajFqIpgd5{^ze*Jj3rkepO!6RLY{cYyJA9`BN5Us-K_w|No~f1FQWX{V7YW8nymk|CHseMbj>(qz}~V<PYS})H`IQ56GX%f2X8BsSfG`vV(kvdXlVkKluzfhPsBVbUQhQ9LuD5CzIkO)M?};<S|T&dod|4Lmfy~T8CVQ{6a%gyqo&323ARNIQ1e~>3VWFIe==A1IUe1Qc<cu)gb$mW2p{uEV-ct+T8+HNwJ-}nQSMU)C96genfprend{^1a)!(tE4zL)s>u^>_&AbyOIC3K>x9TmEI@+OTNjZ_$c)l`6ziEbt`!txdpWkxdr)(2K}gkRZ={e`YU-dxdF8+xdAyhwFEggIXjbLcWMi=JK2*ufb2<bPMt??P9Dglcs_LpS?L4veDZHhir-N4Sio<{B`r`Na!Il;lj6bDk>tVTIn-t3Ipl5B-Q;cL-<cF2q5eizdV+j}e40t|73yX374l1J5?SeU@=NkJs^$d#M$X{`%}LHdcBbYcJCn0gvyhdlIGC0CnXL40vPz0GJEg`!#VRSbI3X$i$fWoUlj6Hn2l+1fEcFaoX$)CuEcq<?9FyY1)ScwR<Q>!{<Q?Qi)G_2m<RMIoYg2oXYm+}{&@yDDDsFyYQoNr@aRhZYc{gKa1e4;SOp04m1IPi4m93c+mq`;(%P=X<OU*~lOU{v!GE!Zs`N*#1T1<-DQj3z6`jgv|*HUB2YsnrKsEW}ZOp3#(c5)awj%t$Q$PcNH$PdZsouDd4r)N^^Ld{KfA!nnyk+YHivOrZ_R;=_U`7iPXCdCJ+N681sGpOsxGsxAbEy&f#@fuXc=y)c@BdC+fBghq~4agP9IjOnHImsEQ*~uBm3=hItsP5z}WEZL@*@c{++MJx9T$?(OT$|jDN%45<e6rHt$m7Wym=xclz9HWt=d(anOwY%pxFgk<taLEBBY6^a4tWwelDdr?N!~~OoxG16&!qS`^$1z%Y4UOMc_zizs8`6>$jQ`~WToH8$>c9o71O`)SaC+id1rD)a&~G~a#qIZ>`aO?P%Y#P<WCl;irt@>6u+XrAuGL0enq}bJxf-4j(nSZgGuoz>S6LJ@<Hkj@<DPmbrCt5JexX%Je%B`NpS&cZE^wfZ4Ihow_>IH$+yXNCdCt|5#$MEKk87j($-`@azknvazpYj)V$<h$ZpgeWH)j)Ej6ZRV^W+>!;jMR)QsfxWM`@?*_m9GT8mtjJdH{5Txwgg(zWEd<bS9t?*GGM#fAkMMmETYsBz>&<XhB-<XhygR2BEX@>p>u-V0pFnaJNQ&}?Lt6u+RVSg%;=1@b*=BJ~0}k-Ud`fV_u1nL2|!nOurmja-UsYS4HMtdinU)Dh%S<Vw^E<VxgR)STp8<jm9z<jiCX)ro8&|NL>{*io8=oQ|B0>XK&cxo~VM&7Wqh=I2;eT070yR@{)<O-r2%ihs@*#S^IGwbZ$$*iPL*R(eZIou`U_&R@l9t}D%#X71->Y*5;ftaMVExG{;bL}_H2*b>RuqjX=IShSC^N@;wW*cH#%c7u9}8c$YwoUHUb`4agm^&0sq`3W_dtn>@{3HcpW-5cKVSn&^Pc5-&!0~BZAec%U^;`h{7<oD!f)Z66Syv}D#ivOTqBL6{tOub6J%6dPhz9T;-zoz~m|6n~{Q=gHa@f@%DyRUhy{=ZD}q@+wK>2*pvosu3gDLz3xOg=$AK#e0GAn&2xB<~@grCuPPB_~o3krT;#sawc<$(yK4$(zVas58k+$RX6x<Ph>Os*OC1+@0Ei+@0K#+Kk+iT#s6ZT#sCxT7_JlT#8znT#9T>NrkAzsin!q$&Hy5x1v@dw<33>)**K!_n<Z-_aOJBb|Cj952xD5!^sn=qsbG=Vbq!AF!CzuQt~QtG<6F(ntY6Uh<uEEje3E6jr@{&ll+qWg&IfxLViU(OnyavPCZS2PX0`NP5w;IoHBPxSfClG%Fn=K#Xp$$5%~u>qXkLvdwM6x@5$Gx2gujSr>J|#r^uJ6XUUhy52=adhva+Iz2tl3lhjS*ljPs2OUS>Iqo^U|DDooeF!CbuBx-l^B=R6?OY$Ic7iv9n7qTz4I@y=plv;}1l<ZBllD)|_wA8s*gGq7alvI&gfLe%LfLw%HoLq!lm)e+ImpqtB@fd0=@)+_IYDe-EawxS2Ih4GR+LyeLyplScypp_;I+47Qyqy|G-cCMBT}3`hPNGJWlgNKikCFc%|4qF{{+sM%fxaZGq&PSA3t1(_#i_5zDk&~aeNI+MaRusUvPz2UQq{bz%cQuOC3S8$V^Z8cCH16wQ%jJ&$wjCc$VJF*R5kzIc&xY}RmFmWOo|&ZDXvacaiKbo6&IskC#$45FZC2zCB-?Zm&ht9&Ov=hR!MPI>OHbbiqla~l2uatiQezzPvpncDDq?SdFmqadGbN(B=SLWBy|uulDwGOg}j(NmFi2LN*+sXN*+rNqI#2q$br-v<Un$7YGrb7a%U|yc64S^+@4yF+@9QqNpX25#f6y^7o=7sD=k1SNcNx>A$yR$sCCI+<UZ8F<T=z8)WPHx<ZaY3<Za|5)G6d6<a5+e@;UMi>O%4j@_p(`@_q6X>PGSt@-ymo@-y<E)T87-$=|6-<nQDx7U&;jl@#Zv{!La%aXG4rQ{|Wx*Qe$t*C#in7AH3)ccPXicOnN;E06=pLDahBAo6HxGxBKiIBI+HIC5~BSQgBrcw$PLLhVQGN$y8(LiHv$Ay=jrAy+1QQr*a&<nq*l<nrWJ)JEi1<WWqDhf%AOhmi+Ri;)MA`&09h`;+@pbCUa#ZPXlO8@VerE4eGVH8mZ%HMs#*#lZ$VR$P_(n5>fG!qoF*l@zC^9we)z_%C{q<iE&wsf)>X$qCe{<OK3A>R9qF@>XgPc`JDxHITfHyqwybyqvs%+L^q7JcHVvJcAreZ9@(wk7QEpLoHACAva-CT#Z_oT#Z~ZC6%QXqZTGBEl5`CK`utFN%bPvB=@5BAuF9j?nNHQq<A`$;x*J2<Td0N>Nau=`6~4Y`6~Gx^&I&f*<yj-AgiP}JM}(UCB?4PCuEfryHKBzRZ^Ub`X^Z>#f7Nf$to!>OI2~UER*6|)coXH<i^x;<i_MS)cWK$<Zjfa<Zk2uYA134c?30(Jc1lT4I+n-=Tk?M=aW}Z$B|c%mr{etOUVnV6Uht7i!G_KcrlaWl_@ETI*U4mJc~S(+K)Vx+>Y9W+>Tt2TA5srT#@QYu1NNxmM43WyHHz^yO1YPN0BFxS1~DGKpjS2Kn|r2AcvCYQTvnUkt3*m$r0pms*M~@o=fdYo=cueZB3p^9!_mQ9!~b7Rwet9J5URgJCK`G)03N%Yfx1jufb!*MX7hmDk*lRCXiK9{Egl&@;CBZ>Q?ewax!%tIhlNix}1E6e3`m{e3^WlI)i+iypI}8-bda{9ZB9yUY3$(Q~Og#l9l?9`;$9Sn~;@OBX=U#r<NrDya&{0Qmj*pk(JgY>*Su)USy@?$UVvZsME>)$U~SE&tg)%n!1LpG={vIypwvBypw!}`i^{t{FJI<{Zk$*{z}bGR!Ol&&y}o^Gf`d0naJ6wxyaeb?$knLce0gQmTV<gq1GZ-A?wt}WS!iS+J@Yc+?m>q+?ni84IulI2T@0m2a(59L&)RFGpX~*Gs(-TE6B^q8>mak8_4Ua3(4!rzfu>Ie<iP`t|YG}Z?vS|4>mF>-jtH|Qg>0K$h*jEsk6vy$z!QQ$z#cFsqM&Z$(5+}$d$;yP%DyuA=jjOk!zBBP`i+Okf&28kf)QkP*;(+koPjJ;&m%sK;A^&NDWQXZlP>frSsCX^E~#0(ug$u62X2`8lI*f!`aVD=ceg*#mlKvEve%~@l5J)OX|2%Jf7-jNgaoZ2T?m%Qpc@ge`<3}>Nr>2nOeh=IxiHrq!zWL&LhP-)!C9d?-W;|s(Z=Ld8*h-eXFI;YsK!=WGyugD9%Q`qou|T#hIv=wbVGHSfd`-QsdHb#;xPLm;8)l`xxi;@m}&X?rmmV+{}B)&p5e^arEc?=4V`;ohJ6qP7|wVGkz=WPgdF~O>9@(j#{5wpZ5>NzCIQw_jLce|Lj5PkNOTk`_F#_;s5)a|NX=~?QdR4DeHeeIQR9*puTI+oKpU$UXp*bsiXe|*iz<Z'

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
