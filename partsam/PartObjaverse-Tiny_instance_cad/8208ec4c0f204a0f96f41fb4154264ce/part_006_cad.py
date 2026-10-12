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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_006.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_006.stl', 'source_sha256': 'c684852e407bc729c6dea44ad3a19b1fb51f3c92e61a1a95d28040bbab76ffde', 'input_faces': 742, 'input_vertices': 479, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3249225616455078, -0.21695832908153534, -0.11711475998163223], [0.062133390456438065, 0.47109392285346985, 0.09637409448623657]]}
GEOMETRY_BASE85 = 'c$}qN1#}f>x1G=g3lby*XK)J;9D)r60u5S<1Swn~DZz_{pc$kTch`%%2TMqE30i`?1h^D0R%na2y!p=F_wVJtzO~+ZkFK-!K6}ob@0-tOZdO|~{=z%EhJOXMChK>Vi!7sQ$}(u#wWx>zgL-s}7+ALN_d~rjKhf1c7tU_hx@n7cURsnkym)xTz-|MI2kXUaepjt{pkDmDegg&#=+d`yzX9P9N)PGMdtij64~*>ceT3zgs8qFjpkA?LpgvOnKmJRv>M$YsVxk3(G|gtzQU0=^iOM&8<3+c}cA2eEyEt-^LNj)c=$dIiD)IIk-4xn}%op7mL;Xg;M!A1VKg4&mIYig5FA(4BJH#hH-!FOr=*~hBD0ft*<)Y7?zFF#5KU{P(`X^KFKmS;C`*+=-XL@?jJ-;(^XOw$u;|bA&MzvPx{1}G#!Bdk&x7}~3&~dp5;?wqzb+3=n=_}OdyE%vtOtnGcrq@NDf*X*3Vl&b0=j$L(hrK&Q&yPHgrNMaKUQeL^7_!V=*LqW5FkIT(yi-kd{fo^z<hrd1`sKIsD7X3Oq|ctWbveYhY$o+LD<50!t{c>~$nMg9=D>m|clj4_qJR2xqq}anbnn~W3x3Flc6i?p{a9)9mP9w*;nG_+8Y}IYm+=$JjF!05^B2oF8Iv3NGryf9@zt)#b2(o7p?yv~lYTTq@@#e2wPfhp)kotL+H*oTgGy|7Z)bf}M$~6v1?bUzm;9@Kq`_RNpHF(|Gs>=#a$;*PQrC@MX;9Bf%Ou_$({V+jn{K171!bKk_YKof|5neoiC?S5Ch-UVenH}|1nrb~p9X8)b<?FcaSoFE-u(i7+<56<Ge_JOcim21%N{Q6Y^=N`x-&;==s}0t$n!o(5nbyx2K~M}=O%aE=F&?f^q2N5dK&R*GosvmXV*!){B|7qPX})MY&=uf<}`wS^xzVAU3cm2G-+pN{2|eeWkvRhp2oh-UAMdR)d7=boD@8W`~}OQ{dXov`@3|Vy0)?Z6v-PDhv#}dVTHsu`AVMG9JLzxQ@jqyxI8+2hr6!bgs#0GA>+|Dbt&3^*gct#=8M|W4ldn6UDFEnlyWD|z;jjY8Y}tsjGCve>zk&d+>4)9N}h2Y_sH|E9fNu<jFI_bMn2r>uG^_=;g1(eo))7}pQ?3Ei~fD=w-R?{81ig-)kVth>6HBDyP>G3ts(k%dDhMDy55EQpeaKItM`JQ@4n10N7>rD65Vtgb!|x%nZH`G2<WVj8Kp`4m=SF-PRwgtC9e0ACGNU5n);5*bL9RXTjRN=*fDMgWRmuCUTcE*goLf`<ISbpx8%b(DL!!fXYpI9k4P{3m@TkA;(f<rJg-WYc6RAb>RR94($4lvb&zM655`-hQ^uQ1*Qsj@QptGJVrn2yx_Pqxo2~Ln{q0HBp*QfC^~)?!WVe)?x*DGM-J4pH=O-^2C(d4#F@AbX#lHDG>w3wzsTksCW?C)2?=Z=4F3?e*@?8!|{K5-s<$2=@px@gV80X*A!t+u$+CtaLR-7--+rl5u`+KQ_g14@Xll+}Cp?_-~!T6u`YOT9&r>^ab?ko2l@kO4<eGb7IyVl74)l(t<=zQ#t`#Y|Yd@o<0m-Y#nfN>t$WQn`3E$W1RDPL6LZP}n3iIXMX$o8X*PsgHHqU*orM*Q6Km`5!iif(hA2a@mYa@XxHJ^i_*QtsH>qB~yK#J-s&0_z5K{S9=@Pah=pnRONQ**Htebu4Hk`CYn6T`SU8=8K+p9r6sQj`4Y-n2cMOZn|{8ol~V>Do;T>#9ZQj*Kd{NSv(PXN*S4VMv)Yp3+9hNd-^OwKbCkkyN;V~M)i??H?IBtS-kzl_ZSZ)8p=4-I`u^UlAWX<4gdVop8Dx;kZ1cWp5Gc^efX^<+Rdfcx5@Jw3!6a?OJ$e1D}y&m{o|WLUr-L~*oE9!r_0qx{g<Y~JgpEb`CYoc47#>4lk}JUeQoH$8xXJMlz5kJqpls^B>TAiVKv0JT_fwDwq&N%$FaN&;`4;a{4#3fJs|$ZT&U;J&c!AE(vPBRD?gnREEFm8&bV?nPTHyQ2hr_?qxQ=6z&Gn8f8tBTZ|p1kx8v_HiFfHXZv*pT+ll@1{CO{l?##AS>TeVnkNii^BG0&l<ATl^vhO%wA4hzb;y;TXbx6*W`qZCLpI+l--Wi!&N*;UTS?Ap6i{oz6KGBPg7v0QsW~Su%a7D(Ot<5Otzs8)EdWP<l_A{bKB2S(>$0R-p>zENVKy=6QVi-TwV`M+lQny2VB?rc5&^BprN8!eZKW<8Xtx<OwxAqG4q5s}CS>p9S4H-WR>LSnk0@!yt6+(N*8EDVYBZ!akSuE{xyt?Q{>4#{y1;eEu%$8~KTz<7qi2k&atpD0|Z|INu$vSLq8Y$;8$A>S_{`VVUy?s_u)<5U42WKVzT{euj`1!Iw7%x&p*H1-ZUs%}&@eh&^|Go<9dF8dNGxkykMR&BBhWVav@fK-+Z9Vi<2aig8enZ;Lwql~_+MMCiZjN`QF;BOT5#1S(74s`P?Pe+WcN6s~+d|sGk^79qn{Df%K9^(BKFwBOpSfIAbR(!I+9%oAiSqtBBYNj3^w*-zGJlQ7--_<I)Lh!fUgJZ8ly^Q<bUg(7piwa>UY@tem!jJ*k4(aRj*xg~Tvg<6?~U<)(kAid&U~UfqhBXVIYuw(cl*ek$p4~h2f6Q~9p#?QjQB2FWE?vO^g#Y>nV_e;Ci6|Z+Dh8T82tBX@$;p@x>oY9t?s(n&W`nA`C!z?_Ydf0zLx&e@_5TR*BNqEbUkS?#`)HQ8|3-Q9YOxe-Wa#xJEeT1>0ZQ#-H~&K7Mw-)ar@kM&`b5lyzAzVegCf#(7UZZBJqAca!$~GD2n=A^^^H%6pF|CdFjq6X{T>Go|8PQH^}>)aq5`p&WT|dZ{Z(h+}c|m7F~OOOvZx|{89SdrJIj#^S$h`%nMt$1ksJ~($eqd+D*G;JpQ_0bX^O>`cMYzp+0&W%I)3~^D9rz-BND!T$FpHBhCqz&Pg8a@hH(9_5V60@kesw{57o)^yz&u4g;~CXpvn+x6N-a&#QH;DDM$Q+EX&$%&x7W-)sAW)bl~O=z9K8si!08lI)KTM;PYkhMQ>T(cLg#ZiR~OSa9XA=xKvx{dPt)6x|3-hyCu!C+uq*8i;QDB?9$q-V5iDpf8bUW-!LdTkHe2eYH`aJ4X`Hp9kdJXm3^t`Qw{l9T*gY_@%osKeIfLbzEDOh;|;oQgo;9*LdEr6_KLb=810X57~zK>Mi5Yr8}Pggz<2$g6tRO>&c?)#llhlH*e*+oFgY7PwWHqOPz~SzS+Dh;!np*J<U}&W!~E-g@|rXD2I6+>M#4LIVMnaoB!8n=R&ijUiO@Ypl2$F^UCm&vR@m$a*1w!GO({TX@PxtTL9uK`^Y$ScnuWYF~OJ5H5~6>d#<3KH&Q{*9W3L}NE|KegZAzZ*+=bXLgal$Tbo_V)zUr}-OSZ(pxjraD%OEd7od02&@WSh<Q%Kj*eAN}?G%iY3hi;e?Y;{8^rlT1ANNzx&eZjbmC^o9Kg#;AM=e4AJ7LJ*s+^pwwayb!&zL*X{@RF9vW_`M42NFh3dT>XXsp}48;b5I`2p?x$J<d-{_ph=U-cpC$#c6)*I!^fnAZ=>ymL0Ff#-6K!>k#mOZ>#@h}RzD{Qpa8d0uC<51zOG4CJ?&!{xaiKbQ5zo?HX_<M`#WKN_)*vF@CFk8|Da!Pqxb-@*RWG!c2~UYH^G#~p|MXBoUVjXs5SDX};9xi%d!Zb#(9`}oOH$e*DazGt>yFS_Hczvz07nsP2T`wYRnOOqM;{0w-mRfc@ub4Gr`da)n-kd`5MIiBOC==#BFh);=%miiA)5Z$))g7lYTTLzqqTI@ichI6Hz4X?|h+Y3%cd_Y#a=!dSz`fp1g4ZZbO$bTpW-w9jh7TtM14dz$$NEzq)nk=H5-+U$C-;52xQeWfeU!?zxSrc&{?sZAZ(RZE^-4+-q{o*h(W1lLt|0u@&IrK}p8_550GxVCZmr1!pmP!3>$JRlw*9PrxY;Pg;%e7o|{kIbsx4*oSdFlLpmgvrx#WDV8rp0=mI2Ge;QC{?K#sHZw&UM2?x5qA)^RCvYkJR6uzaH|eUxam|LqR$38Sw#Fk7mv5F1ohzD|z0zzQ{BAJLzxjD*DS@{Hx3pd!CJ`&-#<tm)EZs-MK$X-k;5QZ+w6DiV@wBR1o`D2JFkun%$0|{G&J@Chm~+SxehVbaVYsoHt&s#dpZ|tr7oa62{4xaTt&Jsv!TiaMb6HuRNc#Um4N$L4IhThR5Z+Vb)E9JWH3#JkcI+!FRTmZ)E=H)#gr+__bLUO1VF672Q@ZPQDjw_x8#>b+%fK_~EtYO5W1TWj(h&?j*W1_zKnsvxKZO4*yW-`Pa&K1kHQi2x;f9%OcO$@#yyhXlMO)I+WY9G@dK$g_P^~_~DQ|cUS<%VaciZj$ynP-TAbXd{@#6^q(&{?ycyyt9z0EN!sP|T$8Sd?s`u&2KK~09-a(+Pd$`-`v-|PZp;?lXy%Rc$-26Duk1PlddbxzB|cS*l<Vk}8}(Va7J076$oE*S>V+hUkBWzWDMZc%<}Y^99h)*?oIJug#1{I!=z4a%_i0&A$@gtNva9G?MPJ1C9U^(`*@BS&>@vhp?jgE!Ls94@-X0PC^#bW<ec*jLXE=JjhQ9e6>Qi)p%nv=)nH!>Kc`ECtvwDBgo%h<Npgqsx`*fuk8Si?%wi0jpAH#XCS$%w8{JS3FgOhQ7n^ISF=lCSi&0<ZVkFJ7w(;nrTRUV0Mj2a;4Y2$8h)Mxe&`0lbIJHDf*U57j)ia;+DD(6|}3cs78SMU+tK0K%B`kNQmCGP5<_^#7=t*qbrSEZ1Dbf}y^9dBkszflzRe;+NnZNN0q9f!7{o-w0DH)f1Re7={6KfMR#YJaVlaTt0-$~6b=lX$&Zyy*7A_YmJZQFJY3vgpoFYw%o|r;BdB3=-Xur=~oYR@WExT(u785=UJ;Z}?Ry*C;;;-(TZ$Al|P&^530~-x&_?L_3Twy+`otNYU+~uTjr>Lq)eQuY&j~QFz`04$*b*Jox^X&kyzVIwiVu%WXL?ID8Y4r@?;2C!EJQC1N1T&6OJE#*~G=;XU%~J&gD<0mzfM4|?1T(TxgAWIZycRmO8=d5QM_5RP?fX&30d=b^v0TwE#j51Ehp4EEY9c&(@CwoJECpZ)Dcw{=YmJ+K4D!?UfTJL{aq?>xGO`aC}(x?@f_^vegKmk1TzUL{0yGrA}GrA$t#ziq;oD=<#jj{_#`LBFlR?<CRlP|rUmBY!}c=ytyp)U)3?(Y5+v@;$>y=!AMM$SvOs?fvnc!|?Bna=VU2yFLB1NS^D&N5t2zEAh@8F{0~jDj>e*-xBXg8zQ>%TpY${;vSTH&Rf3I8`=M2yZwfG7V;9^{vr<g%?+aKvwp+5>Tr5I@7*HE6aQRv``h{`clHL1w+~}QcV-`odS=Qa_0&go5Z$(G9_o{H5B(C8GE3Uc>4Wy4Q&r;4n^WZ+s#UlPePw;rb9XoSUCueM0>*RP0gQ(n{*xuon{23Otz8(OrOwIkkj~I$$a5zQd77^fUEAt~diEQS=W5z;g7kaq`N%(bKE}fzk7fUJMC3&Mdkn^SYf@{B=+9OmfBhS1|7`8#eCGIZBJ$s_fqD*KJ6!5hxiIpyd4qBFFr<OB)6AbyZYu+MlCHHBf9N{osnZhAwfbdO!Kz_w=Mm5!q><nKG~X=HXGJ5=h_%@NJ<IJnO!jl_=_!=Ev?1Ezs~)m1I<{?tzAOaow&D!lGY)r$?)@#EtLzC=>fbyW<?cO#d6B){=sN$_4qiWtuJ2!f@fNxp^&eGjjKp6kg81m}|7qts|I*I3KOf7!>e(-Ls~_w9OFtTyV@0=xa(~?DFXPP-Sbw6_XY)?zo3n{-Yq3J~|29snaaHGE#+7ZsqDg{_`ysx3W{m$i%S3lHK|5=wCt-dC_{;YU&v9#C)L(S_>$7N|jxnfz#o_XMf@4h(^3>Dzx#oq`$75a?x28^)IFET`{QXLPPje=HME?7CF(2=wpDFo{*1$Suzlwe_Q)Y?oF;5L^Ud!`(%xmrASkXP#0qw*F(e<@cue-N{&00_7c|Fz>(^`Kd&SU-23wz1$x}NKm&0622ULNb4Ufx^IyIKs-A&aJCoynhl?q}n{T!VEudtT8Ue-?tC9PycM@3RB?hz)3m2lb$TOh&uaOpSj3DFXR7bAIj02t8vp`5nVqI|Jfh%*Fm|t=obg>$V;cBf950ul5DW@3Ajv1AOqijpsgM?K^^=`%bx&qMKPG(Qe~AV4lAEwAj7=u6dztthMB`c6+x8&y_Pw^#8WsO>BqnC0n<n9X_l_p2)$X8%aH&=bM7@Z0)Cl9{Z_1_g<8%<wktFcBucm^N2sN9p$Dx!FWztiTB{{#cqk7VLZ;a(Qoh`-r^L-)sZwfZ&>@g#Cz=T>O3Ijd7KA~R2>n2x-0bg12JFbhT}WB$GJj(I6!oJs&uI5kN#N4Hm^pWE?&qJ6^VG`Eb@4qTkJhkphwJvUfUbvF!Gk@w&6D9FLn|0s4l->mU8u1ZLDwBc}dXYykwTm4E;3vOZ!k0{Z%@v=nmT!<bN~>^Ddw;zQ=XxiGI=ZBY&0>(7Odd?{**ih;@FG>z?N~>%1rZ=5gM$TjxWG^Ee;s-wqJn?(~!XHA5cZeJ5}+;#VI)d-fcT_XX?xDd=(j)L)%Mo_QUhe|;I_!8*rEeLc^y*11>WJkGsZrM~!%d+H?G&G!l7Q_sbB<>bkT_iu*ha>k0T`{qMCOs|akSm$l=J<r=)Z=*gQ=X2X=AAHY9&;EVh595DGM(8#3q5Yki(9VPW*1Gqv`5NQRX1y0+9)A8_;AmY6`e^oVZj5J#^?o7cc)nj)?;}#K$NPwGy}wAj$NP)Tdf!3&dc5zfUWe~19`8qX>wQYf_jsQ&lfv+K7IS7pzr0K4yKcRgNx7cyW!8I~<nwrsbEbJCx?Yz3_y^wm9M=1w)Ys#E(7vs%e5bLsE{ynMACRZdP|=-bR&t+xD)qNn@0*g}<9$=TpGr9%@2C3P*@*XepVgbq5#8v_eQjVd%y;X(Sgw1#7wcuVi>@_izxOPIeaHVW^yJgfpOr$tTkqX+pT~Q*whZ6zZA&_%9YPLDJDcNciEi#sgZA$?Bo^g{ithPdZ@!Ba-Tr49l>6c?;#XwfB=H{K2ke82LU&X}p3Zgt^PNG^^E<=MHKIEnmW94N9(e};h4_&VQ2$xac3~b>k?-!F-!b$lb@98a=Xa0h^+osmPGb8I4n3g{^0b^0>#pn1aDFgf4i?>!g75wMCbs{RVQ7a+G0;7}&uE46$?pk9)?#?Bq%hI#1qz6+<-z<igU8Eys0a5K-Shj8`d%d0J-!z?Dm_5{B9YK@`r)}g`pfUA_TRRmK8^1o&)rg@|L1&r=N$BoOGS4+%8K~K$K?CJ-eHLRzG@C`hj_mT(e0lOLvM%o9rIys=&#O*uAe`S_>3R6*J<(DUug$ysiZe5tZB;9Y1y^!y14y`wi4Ap7ykR7X!oe}zxosHs+B7IfB!^#x0f{(z0`MR;AC=zQ^@V)D~Z#|SCX$L&LUShhg{)Wa)o=zSChvQkB}?;nOxy+^4+XQEO90I8p}3XwvU)Z9&On~%YLLOzKFP(d=dFp;wEy1apYUc6D>PSOeV&WCzBteDZZb$iF`l#2I6A!4de@Hicca=B%ee+j2KNmjJ!8Z@g9~%5Tl6E<k4)4D4OEqX^Jl(E+St*zL~g{d^7n$Vj{V#jSkWjKWEuB;#J~V@~h+*iOJ*_$xjlGk)I@wC+;VYCtpw8K)#-QE^#6GT=Fr*N#v8*rekP|_b2uy?@t~{>_Hw${;gXdd`nZ@n&Mg*u`4lxyes)oVib84`(`Lj@o_Z8=Mfi>&m-SR+)Tci{jrgzcoOj(c@p_~w>~>hQ~bJRw}>~1*T`>@rx34_r;y(uUL?Okeu;RJ{1W+LVm$d_@^!@Z<m=g&>u8G4B#t4UNj`$upL_&)A7UhVAM%dGZ^=87w<fkDZ%y9Ht&dyL6#vGumc+KiF!HwKU5H)DyO0kd4kaJTz8^wUd^m9|d3)ylj@X4<t+#5uRO@Cr%Zgc6#InMcm9?ylWd$t@v`nWdUX-SI5U~n*5P4Oa;s&ucxj`O6Q@kNf@dh--YZ9xF*Cek@Q@k`WkUWs}E=^Os08Q~cG{tihb@JTgIcbXLB^D*mOJ0bkcnM+<c?t6J#H!@w$*a>8uR}D*>yXzYhLG1IZ$wkPF|i?eWAbJ+#hVfvkT)g&il%s7Vomb8<TZ$u$!m~TqA6aASem>v+qx7@@%+R*<oU@1h`GrF$o+{q$^FT5&=k)_%uAk&JRh+Tc|P*u#1iBs*dN7didUd1UX56tyc&5eVjc2Y<n@X5$m^4b5*v{>Vn2n_6mL#!M&6wKYntLMh)v0xvj1Ap6mLSTOWuV1OJWW3FUf<6mB@q1D-uhQS0pb<%uhbjvVNAu5c`rV{GL39e6(dh5C;>#Cm&4Slcu<h*q7W!-kGL&II$mjIC(Fc;sc2z$p?~;BF-QmMLw0L_zL1G@)hJeiF?R*k{_Tcew_Fd`El|yG{sL@c7m8d{E0k)d<$_8`5u<Ng{Jsy;tcW`e74!d81fjl`)r!x^WFMpK27l@mMtYtApSr;fqW2gF!><zZp5DC-N-u-ZR9rgWe1w#ZD@*jB8HQ9BJWP@Mc#}3+MTBO0OBa}0puoeD!EBMjktn*8u>Ds;=71D$#=59chM9-N<2<}l>9XD4EbsD%QVHW5Koa`A-~}D&se!YQ~VH3aR)Jh+(EvLxP^QR`+gg7KKVBC?ZhSIu5qxPxPyEL%id0OkZ&U@Ki+zuy<piMqVk>O3V(OIc7&$*9ohxPDEr&8G+y9N`tNy7>37KA(^uCsc)=9+@`63K_%q)BnEKz$`IwkUuIwb^A5%Zc=U77DNk5UM^o8UL8NZPFSj&deA4^pJQn$FJG^IyTSN<8I(w4dT%V<g;OjEo%u@-rC^3=p;s-0L)Gip)vYthm$UR^ItKMlDTxfecLNL(82pMOfvMbyc2k@uyZg}%aS<jMvyMyEcAF|FxWBagH!ntmiPn(^bvmA;&O9Iq*ECoU&fm_VLDKaQsOD%x`9Sw);_*<SkV7{7|zI`Ww`6+ec$^0yL|HrLHp`~c&Wc8d89xaC#+qGhLf{WPyBevSS`@~iYuvwnN2#Zmi({$26}`d7*0c<n0l-6f`2_K?2ff092W|Aqdq<VsT=|En8U_@4GB?^W|xT~pc@<Y_pUzaW3b`<0)}GF}liUf*Zg8V%Q7eloR{<O+|HALaeYEcZ6=yUlwQ|AW4|{)xV8o%w^how-zQJKOLm?H87jK&~`3)(0_u5bs$@eI@H_(pNkexzd``S3I|df6a-x$Wzl-*T1G;QNx;$np#D26*G+2ls=eTY0Ky<eun-E+A``t^P1A0kt^*1eZ|$9`;6Kf`ig%df5SHQVjHWmrN-M8n&N6~tNEnn_ZZ>`@-gI-$Q8~dDt$an@d>n%mQANNlA2m$!sw5nKaw_)@go^Ck*L<jUPR?*A+{!W#kpddkxwMfAu4?=`B>@-*OSlVJ#%PE-$Z>5`6lYSiF?R*lOLj~efJ!-Bh;=?OCeq&KSJ)(lz)d@;X}q<B7aEzJ?p=Oby-iohwV6#b&q6QjbQtzHuGY83}p^AcGSLjhB@MyC!1v@Eh}P~Ke<a&emQc5wHc@UDzuW+Ycr-Hb>+7qD$VBRE8duKN-IyUw0iUvFGD|&ygYqnA=DMtCvRd|1^UX$Qm;>4`BllAkQb$|tPo==P*;8_a#yVKvy&_IV_Z>kbv*~KDf6++mzs~8?#p;@UdzerIjH3%uS`=sh?axpRHomEsI)q6zKbjDLR8Pumb?^w*R{5^s%)PK-mk8=B3D{Z`ij?JJ(S;`ek)pK-qW7Gy00!{l-8NPi!1CyYtQ)pyr#5n<VqVzU-3}t-I%X4wc_*@&r7bftn?MnV_8~i#pq|HmY3Y1uC9MYU-3@lO6y8r@s8xZi5(f|^1r8b;(Y_?E8c_gD)t+4rG?X1ydk;LZ1fecWLYq;HKhLyEtt82sRxh;@Y!6~3|cUC73<G9W!`L?0P5b13!q+(_cSE;r?0N%WShFix2uh7uy1mbyENrjW)2_T=S!ZATw!L*GSOGuk318(!U9BfJ-?fukCusgK@Dq7e#RCg&rdy&JdpRP^{_nSGSe?eE6;lhFjn1DmcEM@qF;!0Ex>0g!hAk_{%p*rbhTC<wCt8;u|(y+AXn(^_0P4RXo^3l-D1phVp^KwS%{h4xXS7B6=tXTS(eqZY~<N_JsWve>X~R6E%Tw4ky?794^8R6X~5SSxH84hT6UTI2L0D=n!4v5`8&p3CT^kj7ky<nso$V}lla!M>l&WpEwy*_|Du1L@#^|{`q#;KkSpBIxa;KG=)1VW$;4@Hd<Xq4jGIhTS_|sRpF)2M{g#$>aMN3oD{U(IRNn8>zoVvb2D!qG<jOYlo{i*F$z6T2nZAo(W_$_e?LeNvveK5NCoe%>f-$A3e@kpY{w;Y7ZMbENsST$##IgnS8_*w4Q~DzEMZ8yO$LTL3KTLj@F$y1P>hFdA@f|d!-zTQ>0>4lGQG=y&8|TVbTxsdt=0!Trm8|5h`IVY;PHDc>e5t#x-?MUlu<VHjo|-XF$d#$<D$fZEk1_V82LB1QB=RTZ_ZXvmmG3y?mG+cv<>D{hVxF=+9+9Ww^D3T>&+?S<Ni2Ic%T&0QWh;L_Es6Sm;s)X@H~u62)#NTs`J>1cHnprf{ieL<M{1+#EB+-hBl&3h-FaU|n&MxOD@>)HlfH|8NxvrjcI02W`RN$nkJpqojo5;GHvM*tZ9%OcHHAO${`utn7&D)IC%H>g{w|fPu~(|>U;I!1tHgi)sqeqqXaD0w&pSW=^Bwm)*IK#$^T#|b8vDq5b}H*Xb&xBm-k!Dp0!ocyt^'

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
