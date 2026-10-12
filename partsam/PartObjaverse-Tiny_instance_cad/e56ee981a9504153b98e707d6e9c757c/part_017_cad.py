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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_017.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_017.stl', 'source_sha256': 'dad70b05cb237ea13e8128688272fed003b6af34a39ad48c56456de943f747f6', 'input_faces': 880, 'input_vertices': 644, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2656349837779999, -0.27011609077453613, 0.10685936361551285], [0.5, -0.023394256830215454, 0.2729555070400238]]}
GEOMETRY_BASE85 = 'c$}qu2Y40L*7lsxdogsBLlLA%@6Dl!p>t`W4<+;xLMS1Wp%+1=34+SGNJo(lAz%hVAPFIWG?8|^D2RwiFQWc?&3gCT*(3k|{LlC0KI?hk^X@%+)?RD3nRB>yXq_QrsK$RKwOehLH4iq_G_ssps5U+#DthREh_RJNMaKBFytYn%5|_5?(zZi)pEh2LEjKV??0~3p_5I}<4ys$OlE2)b(NWP+{YLd29W^k5^mqG>7#kt<u|xVrMu^XE)vj5ylD|gzO8zPS|KVSDa;3a>CPARlZ{aaQf5|?l-VvzRzkixO2d4y%CfL1$-r|<6Tg@jXyX*TqTxGrOo+SIa-_z6FdH}k)>B(u*gWWFJy1(Iy<97S^xxUmj=(4`mKh4(70SgpA{ZZerK5Codr_{Bc7ZVkKpj$mym+c$T2W?$nWF2w06O7%%?S~Ii`m4>`!u4y6Npbrxbw703zJLB^zHhzGsY;yJF5z|#mE<_QynMo~`=wqw@(k(bx{tV>y<IrYe{g-N2cXOPfsKne4lNF`e)`umw;pWHdT{?O&dcWaxxXW>DRD5qo`XEjwf*s<9jTkpWjp4<N!)&TmLu-?OWlHQAU=U_CbFM>t1Iy_lSgxWQg0=@<0Eyy)Mb32YjvL{y8A2jU>(+-{-zCQ|2Hm9bjQ=H%l54c{n`IHk1S<gT<yhv_G_8qj*ry+(B*xtAHrF0T<?T?{77AcF2|2~r#<V*h3q)%MJIB8e{IKpZtj=l)~&m3*&oyo<Vm&rW&PHM{YQNhy7Bm3Za=JWnlit#)#CO$mpbh3Zy-+<u74*bS@8$DQKZQcWxPSxp<6Qk`QGL@pdIO_7Fv<-J8MUxyM2Fw3Y^EEKTCCw2dP_9N51re<&}11f34!Bxt%#z54-a&bxZ1{koR&$xSc6KpK!;=sQennTPMps&b_)b&a3C)_{@2l>K-Rj*P+XCqV4?dlzrb4BU0UQ(05<3^#F7yZV73&9^A3=8yo!?pNCUzT_1Iw^NaB&bw6}D-lT4|&1dJ!FYlX}%<V&W;`w+L`x#tox%2MTW!|kEbGe<;_0!yWl)5E#<Wb8zllAF)Pul&E>u|9cTi0sjOmO$tEIF3%+p>k_&ac#UsUyEy*JfNleQugNFH$$4JM(vFHI9GMM8zL{P9fGW&p%}Qi}4_J1G*d!=7QJQpU6iil=-_bAGZ_r;DkHB`sY55!;1x$J1=J7?{vG~vxSyBFM6hRwyvf2PFL~{J($9}%)6F%6@Px&na9s5!~wbvUFOj&xQyF<u{z!zf33zO_GiI1J3fBoSL!BoXP&n0&;A@-&v8S(q#l6o%*Vm4SnpNwp!>eo_=eoyyJb(g^J31c#Qy6KIA3yKfbNIx>|bj`x&5ERPbzs?m!JLorK_!5a{M3o>!dqA&U{ID!To<0ZtI4upY(|D*XU}x+fVCZD#zto+5z|Yk-Bx2bvb^lp?z)LxELSr&X?5v&}F{#IW276?6u{TG9Em-v+pdg!+Oc5>FzvA-GJ`wzgtW5eUo#?x$~m$F2?<u;g47H3*DN|y3DVB?<ae{1wwZ!?O2boPTj0@%AH548_=D33SC>gINhB`?b%gZ*Oz{n?#`o`{}{Kw_D;Mqze104{m<{kyYr|O`-c5Y#r`J8TaQ_+Kg*=()`~W)M@-wV<QKXDUFKJR#_NKiFNkyJSL%M~&bnGDiO&-+Lr%N%CH3GR(B-<?a38n7viE8Cc#ygdJs`(h`}N%ZnapwSJWAa<&AQB^88w^R&;NX{G9F^4@%bit*(rBk%-AXH=lCV3l)NmD;QQVzcv_ji9$kyWzPYL&>lbgwDf98uzI@;G`*H3(>YF=p{jlx(+<t0z3$Q;;zEtx#cmwa>{dVkC@(4X>urBkc?d;Eb$#eVMd6aqpx-(DjR^oHayb($sr5>C+Ldm0<KZmVbOGoT;=SAu!bZ34Q%fR<7cT~x{SC@I$%RWzWk8?xD^R1_Ru1(`}oXnRNc8Slyvj*%};@|orKQEbs_q*e7^+>UGD<($Cuhaw3Wq!>8hxxvVqxQJ-WzAb->-ybl%6PMGhS|DtE%O<79)rEE+2>9pdDtFz9;NPw?yR>9cH6oY_3ypzJWAb!?(C0g{G6=S-J|63AG*xry>Pzov}h&HQa7eYDRB-y>}>17q%M2id6#+sy3BhZv<}w~82jAum%4v*_&#^Ov?4WFzmoNgdz^T6IZphI^KpD?#3^}{dH}l2qcQ3ye$Kx*cDFlU`m8hjob#-)l3(N5VAj_)Q1Tdv$Y|@vqJ6vFd6c>zy3C^y^T2+OU{-js$DK#1>(FH$jf9<CKlf!NkN?n-M<aEUty|qzs(DP?VC!0skCi-HH$UL}_D$X6&ZE>d=+61){w!M$)Vj1+nMcsAdgu2l^R8?cZvQ|zC68WR=25HC*4BghFDiMIx&>Y4F}UEl{X7}aLzO)G7d_?o3%zbAx)nN^-$yJDQ}Sqzs=&{&Vb_$rNL_>OtdkQ;*}AoLwUT$Ko6wzgc-!yxd!j(sPn5h!UFOSK$Kr0<x{>ROlJ|e;$h-e+I=55l2PH33H;^xx7bAGY)`LCLmAp$m0Nq))%g(fQv*>9hFJ9f*2kVdF_7D5j`Rmc0`Ma_h`(L7%GVjcdxoq8^p^ci~DognJ{Of9J9{UaC_bGDyk$HqJ*Cm<9z?`PsPMJc=IxKY!y3Av6o^I>bq=`x%rLIjGudb6@{ahdGkIbXg<+>#E82suDTQ@$8RMttU2UiSH)=A^+OZ#~^uscFohox>nmw60^9_Hug_ckbb^y<$1YPy1-!yi6W_G_;$^JuIL<NNA2l|1_6DzaXzgre&WciZnf^hXbrbB@+*o2^@4bym+U&`s#he%JYPTlXKWrLKF>^`x3gUW^G-S?@PfIS-gKqPd+X<(2c5)Ps-9E9Wa?(J*eu9ILL+US009JKy8?S>xuZ=OyS?^gQLf6u6t8^-sGi`SR*czG|J}_X};-s`-L$L3hqq<|11UB<jlfQ{Uc?-={2^ubgKLUtxa!AFxh2CmR_GayxxCDd%c`_PngWytdz+N2wdooprVOBl~@dv9Z7bcV4ux-)-I8n(u&n{99dqWZn2k9Y2A9t!wvls_Um$m+t`*O>U>g(S7c`OI?TVJRjXOY~8=UvhqA4_29b7%JYcUIuo~3iQk{ed|7$^#qTvvR95ok)t&uu&Q1G$gnwr#<@r?0Hrm#;VX^z&x|MIRt?RMt)#uHE1Ngnh#Er`HsouT{zb6`1?4UdTQrD7$2i$p-x^<j&Cy$*f+PWE4=%71a`o&%LXER%_Q|`P-U5D<x_x||{zW!l$HNSaHTemv4QJ(9iZbEnVugU|t{^g(Il>9<Bp*!d8!Bx3_p9FsIBKsBIC7$coR^MYlH=sN3F}}{keiSy<_f&@;+wn5fBh~jgN%whtr$s66f3*84tS2l~-{(9|vUNRip7Q?3tnjg|2SU3Za_39x26UM(t?hWOf8f^x%J^AV*8Z%GNLAjaNj*3`Re7IgUV6guopx1upC)w^x|5guiMFn{J*B*l(u&2$x#QrxAFK5Rk9%#}L3bXd9)RwgyI$Pm^`&E8e*Yok7V@*Lo9*+bDdWFn8rQ$LMR}j8RXED?>e43V{ijvgvh_f(?@lW77rF`E84rUO@_v&oOnFakE*)s=+T;Stdu*v&u?3X(*!s(iTt7p&@*Z32!H{s}J+@xrCwu+U7N0z%jKeZN*m|Js0OftP)J>_&b*%FqULS|PIN{EVw!1gifBC-hy?}MF3$L5do%fm0&Hb?n?mS9ehwi+uKHQPpx!*y34}Z1^_p4$x^?QNK_1Mn})s*iM%;;@=4nDg6uo7qJ8gyq~%=z5b_57_kp7I>)(VhGT=J2^8ZMX70otf6h)&q$N%J)Z7H>EDuy_@f{KgaGU-%nY;H0Ab_?kL}XNj=c-Z}od6=%&==yn9xg{qK8L`F_fLSzXbc^~YC*{i)VV`JTv%ILqf_-)yzN)8hG@7ige-52(-E#pi73&b))J&zP-zKd3GG+SdKh9e?8Ha{ZhGxnCGRUfo&GlVVxF-9`C+R_cD}&N}~N-#wg{P0IIfdKR7gwKhkJGVh>UQkU!D>y<b@`8OoH+n2g-?oqz~mAVGq84t~~ayxg1Dc_HqZ8i4u{_<4!`1I<|_?&W%pI2WNP`;P<>dw6WbU#1GW(xA}ALR2mbRD|Wudg=QdSGcw<#z>AH>EDurJd`zokg+A?+T>uhwgkIS163z&l{%1K`YjR{VY;J`Q3%ob?DB%(7FgePu{Ps{C-0l^?aB8`OuXVciy!L_if$0mz3;|v(ydf&i7f+t;@e1cei8ij<faP&HTsQ_tk@oZC%fuS@|7{)cw$%-=+LDj@y5E>zLagsRy7t^((Yv|1-U*^w;cKmi4rks-H`L+iBOkomcVG+z^#)W7S97Z9hNilH%62Ess{%enGcp&a`!_jc(UB^#{prU8{X|l^s9mX0tO~p7R~MzSdPsaqHUclXm@J7wC1qRod4Y`xITaA8f?B|J+Tbe&E^RV{Tp6H=$cQo+|y-H}z3;*<U|&WASsPzIJzHid&cUgTJz_Z>o{v_D6qm`j}gn{`jE>^3_an$H$0Nbr~NWdhkYD))#L6%I@#QrN<S0((hYdsmDKG`zqZmUoYU+^-rg!xch5noN&yo%l;bBt=en3KK${Q-kqfA@JH%;%^iyW+MadC6&>~ep~HW#F8!Cfv1>o;sPErbGs&%M6}Z0C{c|&=y8Sn`Bvpq$Qa3XcPj$DiN4HdT*}l{RS9W}B`&<4h&&S#A&%8=E&W_>raQ{wQH>6(i;)z%3!Q;hvJ&8PE>)KQN?hfsHb=khvI-c*ljo$~$_Px4n-~YoYTMuUVj{SKWgWqMH=JqqPuHQIz((YIEcdTz;b?pD8%Xah*m%iosazTkhpyKzeFF&WmA^6Ev*7KH5arf7&%XZ9h*VuolqaCmA^f&7dw(fu9b2V-^Sl6YFcKk6<SkKof$?cC<ciQRv)Yi@9&V2rn@%QK!{4s7lXMeh8OL523t2^;r<2!4|FD68ZLvT`vty@yZef2!~Y~8p&hW$tTQrDq7?H?~}>%m!*)PAikV(Z%MNlL#0ed=-heH*4K<KLq@<G+4=TQ{XH$G=CH`7-Bp;C|f+O;yIH)N8($>W-T>pd0&HBa7NT^kDTYia+|dhOPU<+Z}cH%d5+LNj(^7b5xm+9^J{y`_b&r{YgjN{s#t+Q*@aZYvCkrXY)Lz9dk%5*WWTv@iXx8L5_2eJSUX+dvvG2QHMCrQkVVp=raCR<}|+VPnVVWOFj7Z_e%Wr4yRd<PE+G7^+TyjUd))g-2SPL6W#st>N5UPw+by!bobY*JNJ!!&i&eXGSTgSu<Hw+N6=;bgGc}5b}n60{E@m@>Z;PdF}dqGTfhGsuZNpDrn~h(j@#^i=fX$q&-1(6x>0(*nlF#;_#e@O^$~N`e0g+deH&!3KSkS~aQD~$dVgEjA2v|h4=n!B*0s+XDe?5`jz1$m;&wW}qr}In%X|g@Uc!3sST)YjwGA;!UILewa=#jUptLV_ebz!X{x$z%eL!oaUs~S3IsQ%hC~*j^^_{ol(`uC(e~<3ON9s#gD)IN~GXB8_RaoEpnL2);>yK6|{#%=?v3_!a5+AAip*!<#OC7Es+d*mHtIPOH-G8*5l3%ax<hO8x^E__1^7r#aZk%-M-f=E<>&^B29JGGxVYMA~{9CP-*}9hWLRlXiJ@<2U-Huzqe%8v)zcZ5SJai4ZvoCzSj{PazM9G&|clH<P0qD+p;?bRP^`m9$!ScD({UYHo*N@7ftlN6FV|?F`mr8!69)RwQ&(F?r9v3C6<KLq@`%%n!j>CmxN`Ae%vyW^nc)|9kQG0bAh8~c*oL`%Yv;L%)y3fvfUC|x?8&zZd!}&`4UR}mt>Lzq&K6-R#KmD>k`@j3N5`U?if2J$(H|967_2AB<%04S~>yIPqzI?u$t?TnvtNW}+m+_anAG+heN0<KiM^5B8Z0)I>(~S3GSnuCkIoAcW>3rWO5z0AGTmGS~YopGq=ds9-xW6OME9W=!t(6>~#p%j9Q0m6_Y05d!AHRz4dtsJx4)^L#zocGbrqVC3?wl*K?BM&R)Js<KwQ3jV<-%^|yzSMU_$2ISeU(pnzR*|4aXjlZN_O|ls(gg?8-FX$DgL7uI6n2lk`@0wy5s+vi|jviXI=H^j-TDGv;NHs<@v&^JI{SJf;@h*JXfFlJh~JAs<*G%?X8-_<95yX1h;NVeRG4uZap|EiQgwry>!s6ThOfr^NzT6<H|(-cNwL6#=CVLx;Z#3QE6w!GyXo=Q(x-;sQ+Up{vN^OPXKzr<BvA~Jb%CH>93=szrn$4uG{UG&BE`~x*SM&m2RdNQR)ZI4(0cg+m{`3>n3zFQ0a)G`?~Ra&OBWYzDhSArl|FM7v=Zixjprv|D*o<S@?S;uRqWYk3UxAIsV?Nv!}n%4fNNTivFf^9E>V)39r(vQfhsDKF1-DdHEr??uTx@tawDxzwXL$hz&pJ)-~ux(^RFtR)*tXc<W2uQ$LU=D~~IWKPL2m#~*#!SvwB8r@vAU$o`hSeEn7POX}YFC3Ww3^XhWEN!>dio%){n==kFqpN>DC@hNrh{FS<Q{yOb=#<N$K<I~YS<Jqfw>wDJ+ul^5zJmcT18=n4p*Apjhp7q43@0l-N-SFhgyZ-z`$9SM7?RKuu;rX)luY_0WdWEN!TMsPB&gZ%z9lv>%Ze%{Gv>(`8ljl+Q9*5kzDfLcaN8GyqKMnbJPoDZ3bZ>oAAH?4qdi*h<d;Rf8oyYHh)c#7{PyOwn{Ojn*A!FxS<wZz@Wz#~nLH%6+G@3;Ellba?8a=e;|JOf_u3NY2|Ms6oTRu(OC+svZ1-w#-rWF!a8u%LcU!v?6Vb6fSgI^MMN7!}XJ@BBgE5c3z)4&sj?GSbxco2N8u<gRW0>*>K<8w0b2>3?$y&GtOpT#}C10Dyz2mhV|{{TM)-x7d(!4trD0XKjr!-tE&Z@~|uKihy`fPVpBw*hy9*Ay|W6~gf*d>g#3uzDd}UJqr&ABk%o3d<hCm@R}k`L!PLBm6gb9#NK8SP7sXocui_>_^}YaLVKNhz;Sd;Kjr>Wre*Cd<&d%@ik&Vco>}eyAFLN+ywp%W99|$H}Fd6dm&(9@ZHGiR^TD<Bw+`ThXWWN$*6N0^$63!w;|?RfLp;Sb`-;+z#`xWaZMa>3;225`ywzI{AXeJh1~)^0H^jUpiRPx;8Z6=2-hRb3|<lS>Huql7et*<U<U9ysM7#gADqg{;5x!L!Ku6o>JU~1uZqv5fF;4J<J!u=GT`}z<->YF_@|F~4O~+VSQ)$|>X!oM2dDKW72_@yV@|FmzhZt8z67VX%7yTK2+M=hT6EjTYYgFK@HbGWIItY}PonImkJkypbKr$A_Obx8f?q+KX}}ZUG{&xDoDp6F{{ueL{3E2fN1Vob?hu{_ggL=!?b`3-c<e_kh!;nlH-NdpuVU^5fxm;(nzIx0Zzty77wF$n^pP+TJPm!>3)};~7kmS7J@`o<-}@9W2wotB_lQiujNo^DyyiX!J_Uaco-2egM+kFTw`d(%3)~L=1bKQ4{0Usnz4O3Z;D2Hq{0004oaQyn<Kw_%;8~DsYLoB@+W!W9P5_<)r!{A@kJlYSxkr78Yjyz>!0A30a4*8|z>gwNiNGD;n(*OofgwO&2=gCM_8(vfcw2$Pg|!9_2LG3^Xkndz<G?$CcLa_BZzpVounwqC*GB?7fOkNhNZf<&6(+2|u=j)w0EU5wq0Ru@gYMNHev;oKf$hQDqs~aQL+!Q#4gzll-Uc`fybX9e;0W-h!kP;k1tT5>d>5Q>JopIIiv&i2M}kKK$Ad?Mj{{Bs9|t}L?NGZzfWyFtfDZ%?0v`x&0Q-X*;QfFD!25wm00)CdfDZ)@2OkPP8aNVsH27HH81OOZ%UHy!CHmSDy5ueJc>?%YU^DQs;G=;}T=#7PzX;y}e+PY#yb(S(LZ2mXh|diXBgq@P;?@{(CDg%n<UsPK_}mmZBR*A_DQq%~_$1&A@JZkkfiuA;g2w=-gU5i!0;hq;f=|JHd*D8Vy}(WI8PKU-IB+s}ICxj!B=D}_oq-d<JA-!t#(;ML?*@zo?*`r-I0d{rcu(Lo@Sfnkfz!czgZBl_1n&#p2RH+K2Kr8XiCFtq3HuZn0RKeTVqt55tHD>HEC5^sz6AAF0Y7oIyBg)IQAYeDVJn4w4E!8?g|H8WeFj_(z7l1h13v@*2=!J1SGd|;j`HOwBR*T$G-2-pXM&r;<_MbwTnIiJd=B{g_&iV8T<CLAMtq8}sc3sD+MR|vQ&4XTH0g^8KTO<nCazt8`w%VzpO5R80_TD+1I`1^bzM6j<?~&2r{ekr!1>@)ah(aA1O9=qMZ#tPr-KioR{_FC11Eq_7B)%P0^khrAt;*wTmaroqn{3neHA#+#oOUCVNdXC;@%B}H3PN-&nK*~uu{PC;AMo>1}CiM;yOO-Xp8t$agU#b-2+|&-y&?2utUIj@D}2l9`J#%1GryUIbnH#1;7^|CaZu;!Jlh<?}xy9;J*udEX?O)%<5xKeq9%K0+<F)_cw%f1r7(Vg}64=n1|u>K*V+ea5VS`Vf}@T1MiN{2ZZetwh_1voccZr{U3#U6Mq{yC=V<JUSC{OT391sRd9;=EyVp6`bIq5$FXh)YzF?O#%)yxHUe)f%32Al0;~(3F3L^|`vG_Z{99p%5yQjiC-Dlx@(Zg8^n<SywpiF4;8bwxOD^<>usHai!ZP|euY?bg<MDz=AWsp<74g66e#muxjBn!S;A<N21b9{4t2{6-I9*#5*B8ayAl_NnP+@I=y}>hyYYO4|LTH0{M;hyhZwthj_$R`a37Zd`30_U3S9+TE7VtIjDZ+-L4&iw4DZp6ZOmO;tLaagK8u%`FY2j-HVWGex;N#J5BycczRZ&(?*gL@1;N3)7b72F3{{sJyupfn;0-gbHukkg#fCIosh_*UXdp_p<@VSa8D<P~2uo`$#jmv5Sn}Gi&?2)j)fSG*En+t3&tU9nEIQd);eiOC=r+a0`{jwtm#LEfGC+uzD>)`!_^$->f90^`nSY}+88P^bRAgnC%Qx>^th<mp}e_EkW#M=sA`v~g-90qQPvM#uP7u=h8MqvdoZVF)RNM0D93&R)U-v~P>Y%6dxcy3{3(9bgHEAb7&)(eXR?g#%u*hjdQ@DuRy7)Jwuy}+jlTOn*V_!4|BgBZOHYzVFkYoqZvChP#7D(s}NtH2<5UJ;{$!b$?)0;g*YTyG#|#ODc{4u7V@C*m}h=~a7qU<L56g?)v1e1%vLFD0z8up+>^;52UQp}Zc-N+Hj!P~Hk<#D%L`4q+L9*}y5k*-@SyWj^G%B+5&ojJP<m+JCu#nZPN(nNgk@Wg*CMK9uJ}8S#q3@(6ne_$D~zr7X(JqO2lvQv>BSP)59uu$IDx0Xu^a*LWQF0k#CE`P2jDJy1q`p|FX<mIF=jkCDHHz=_~AzNVpk8p??86t+fK0`N<4OXIxm1g-(6@xC7A>rqDhJ7Gy0@4bZQz<(BY9_8mzMm(tTc>Ni89z26c<{g1KfX~5m3VVTa!aLx!&e3|86ZitWqOd~3Y5-pcuPN*el)r(pikKe-QC<*b#Cr*ADr^9-CHO#L@1guXl=Z^?P!HwxP)0mf*cf3Gfl=Tw!p5R}EXrcB&h<fgACwWFBy6&e&q{>j!AA?5fbt0_n}q#j1j<LCjCdzuBYk{^B@72|BCI>gyQ8cV_Ko%^Z;vwKWrfxE@fm^eZSZ2kDx<tI%81i`TLI-2P)7VE%`<`bftkS{2+M+U!rb6bgk|$_Ibjy?i^6^pmJGZMo+9iD%CDe|IPK3rqWnjc5#KH>QKR2eG42BYx3JwP-;FZjv~L_l`9YKspC#-wjh|@<7lG3m<pY#|fHLBAep!a{Whf&aE^L&>&oqRC!0B8u80CXeMx6GUNR&sStUa!wYkLAmgHM8QGk{CM1L*rEU_5v-VtX2R1DtY3xqA%E3SJarqcE^MxQ?;c0N4(E6vnmz91cDab7v^9H~0X|%~rs=;56rH?w11=0H-yD)|QOGhv2kk(b{z#m<CR3BCU=4fa}0%%{4VX%M(ror!}3{_7TAD;IwDZ-q8YB9h~+g+M9|4^Mcc!M|)p>pdXy}RN7l>0mHyUaZLqae(<vzud%7Xli+k;diDqb<^-oR@EDAnF&J0G=^RD-YF3~RoP2u&{t?!6@yhs2*c6=pvY@Yog}~p}_)I?w7z<A4(t;ZA>x4PLC*zt)z**o0aqk?!Y~a+FA?Od`An;K1BLmO}PG`B#HJ*orpMlfao6aeffTh4IBR5TfwZJJy&5$R;PT)H<K09s){u{g*u6YmG7@U0g5PlFY0^cj_sK)CKVInxqL3$?43iM%4uEo6r!0q4{gdNv-Z6r(qza;Eejh}f5e+M6{@!2sNI2)XN*aJTZcY%K|?6$`1Ea5NU)aHG(OZXW4Q;pA>D}WookHObu;6?C1gx%G6k05*iei?nZ0sH~HIpSIm*ckja>iq(|3{C?h7xtT6*pDQq_~r&?Mj4&oh9f4!5wB?U_Yd^-5BNyDgt+E4?3J%!ZzN97<0Y`SmViclGsetT;1}R~5TirDbnrLDHMOws*22Clc^P~zgEg8sJ;%@-SO)w6{21b$4m=GWCa$UD<1<4YoDqocf=}_lL*SnxpC1F4fYaEfF}e!41^ivnR(~I#KL|&HQ=I_n5pDvvgdNfN+)5Y+PVe!;u>XX?N8*vfdiwb6L^v9J5qw$-Tm?>To<+Naso>;W3;5RpdmHgV!p8ad97Z_V#Ut=J0(&0uo1(2}8b8w!{s!IyzK#M;0*@9p#K&hy!WeLBbFh!!6A^X>r!zO*BM7_-PUi%Aml_W24NlKP^!%&=vw(-APJ3WCaC#mprtw}!SRb7F@&f%Kd<1@2<GuC(a347BNwhcR29^PDEv$~l`zm2Y@NL3YYy6Ipa3wfBhc$p-4d4^;FLBK};70J`K7JO+3oHoU$j4{<s=#{S^z4z{$Im5%^bSVy;`m$~Z4jqtj7mO!{va&r;*IdR5!xpHFJXOs{0@q+E%-o`wFbTePIbnj9$_Ew7>ti$z%DL62%ibNx%dQpCL96&F6LizV0&<i`Etaaa4|UT%d}6vq5XHiBu@K#6_i&&8S$RDM@L|DaLRQX<eN|jj}jK4@%f9e4>*le+SdyKL&0eb7eILdlo20|`QH!N5uDaDTGtu^tAn={*Ywr+xt*{xxS?@b7hp^9Vi?Eufu+G4U~Cry<^-pEy@~q~mIjXzWpg!t&L=d%sZM3oBdh>E7crUx90%SO^QSMcHMoKJwguJ!r+tw2y%1nFaEkd@#GP<BcntC}7Z?RT5A|Yz5#Y4<(LF+eA>bWa`$9r9{NMi5IRE{l@1Qj0Ka}IWQvKPe`^q;OY5)BZX@}OC?Ds<<;(v5_EJCMX?f(Ga5z{^'

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
