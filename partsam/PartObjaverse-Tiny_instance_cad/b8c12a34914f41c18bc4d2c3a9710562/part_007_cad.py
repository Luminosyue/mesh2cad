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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_007.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_007.stl', 'source_sha256': 'a9d081c11ad30c052b05c90a3e2d905c5fbe5b198f69afa36c2b0a0b0f037b5c', 'input_faces': 960, 'input_vertices': 564, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17774002254009247, -0.07913236320018768, -0.3054896295070648], [-0.09182177484035492, -0.0036563295871019363, 0.3974818289279938]]}
GEOMETRY_BASE85 = 'c$}r33D`~5`~LS!gPAf#h9hLA(qzghGNjByr8qJrg%Fu?`bw0P(m<4x46i9snTJD4#!NY0N=Ji2Nh*rU?|shtJnOsna{kx#zkWa0b*}r~_qzA9p0n24Yp=cbc`vP7<h-PaXa1G*eyY>_T;wLtlTSXch&QC?z`=dG_Z(ES-+*BmUZIpO{}d;;>~K%(`!c*C-iS&)dJgJ7uu|PnrTV>YtyDc!saOAjg9mo&*R}t^9z8{G((TbfJ+t*e4|f~TGyAymO*h|IJyg3&_0Xu$|MFiRNu^f&)AiXH-8bkxL9av2-GZ^pjP6w|wJ=rQvtUXOZCjtxLstw~EEqr5)acI}JsR$~D1|MqHu`Y<oy)wRiu-tP6Mulw!%rQUpYqqso6?i@jGjF5Xv!ZcKf(A9u1o2W#H;fH`7|_oY-rcaRJ;#L8vlj0CjTMRQ*pfBOO5|`^tJO-dic;m<DX{qaJdF^{p}Drw#LLCXyQa$<=m4x{&ThYz6q0OXmZt*p4?;f`2O%5fBVEjMvvTM+QGZCrSa#-Uv=<ofBS?wuQK(X>~Gq6`(r78=tiSQ4;-51Z=cY-m8P8+n0}0Q8)y8Dj2@pka+bdxB6U}o@7tpDEPp$MY8X8}&G_y2{du|Z7c%`D$vMsB-_GdqpRZ1h6R*u2qc<>mXs+omtDjnC`uAg#zqVUst<k-vW;}Q!<{SM(qlXHb_R)5W%`|$Xsp)skC)C~O;SXtlZMO>_nfSlfpBreORU<!1;oWtYq|W=K->y{r$wm(s&S(0oO%tR4I3lIT``xiLRqv0pjNS*m*b8R-x37`XlM$nbM}M38UJ<XN(d*;?tK<hM{nw)=&YIyy-?Ap9heqFEu8VtzrSxdWG9RXnFN`t$b?uYJf5{ywJ#uB1>EE_PjDF`r(=Si7G~=+S(ZhEWr$SBB&KI6A?XYN6D*t5p2aJEY(Id~^V8&IA{ziY*=-#C53sT49?=<y}FnVnF)|5Z~*;tc*E2GDo-fG74A2Uq;b%-DNW1c@wtTyo%j5hugtC<G|r}Sh8+Otw46KAH;Bc%qW@`*MWZTutf&o4U9-wu(!MvsU7PWeMqo-uLi8r?fQG}Uh5pI$I=Zbtve^ow^})Qq3fMi0$0d4_kNp`D4p=#|C(eo5vtdbrqe(=T<Wn0o&iWbz;1e!f5d&@rQj#xzd#OX%r2CjL&Ndlkl+{`&JH^Sw41J=xN<Pjv7o<6mp^@Lx;J_^h+p_*WP`TEB6ozu%L~sW%*7<j+6W+UW6rn$PpMPx2b-tz-H(y!lFVotEZ%joLcT-_EgP15Nw~UYhG4SIIp_505n8*Q=k;jL#KD_e%49tNm^ApNs#r`Cj1@$4$FUFnY4hs7!ymg`UTM*j#t<ZQD%z-bRnEOJoN6r5^RZ`rMqrxV;s9tr_Q$->aMNTM#|Z**X64AIs18-DSpAd{;$NZ}M@|KDo?zh#xOu#?>67$0ufF2CnNE`o4mhfqs0+=-&Lgnf~z*>Wcqzb6vzn*EaFHpg&@+>)1<;Og;^b9{Q=t9RGC}sf?b_TrYOs_-24<&+^PO&3Z7e8a+11jAyMk@)G*<%rjm`<A2`h$sOi<X+K7uCVpMUbF-U_f0)rj@A7>a53w#r_Zpji*YT6Q6@Ac`nf`W;++g%*iCS|4*J)+y{ob^LUf0PA_#ZR#UTFHGCQbqJdDe^*JO1;dA2ZjB_IvDff7AZW%zY%jFaO?@e$eQ#ht2h(?HuZB^hj;f4zbtzoA1@d=*bY*FYTGki+?=x9{m#8-p_omKhDhYkK51(M)z(p^RWG1Z{RO$?vL@ajZ%4rCK){%HrKC?pHSmRjsA7s)O|C)x3BS+>}%pIo?x!iUC$W(d>@m4A?EW66HPnZ@y@1H`SGZ^E>^S7DQ@&|<YY>Z<bK19liy;-zoVI%-&)T${dK_TUO!WBG{QW&)9A@5KbZAK<B`Vyn$e?OhnR7m?<uY${M|jX9`0@KzmZBtk8IvK&#%W$%}D9-ZTHUi$B8U4dbs{FGrzSvo>ouh`qac(VD!+KO=kWde!%$q8$G!-ndxtbP-FCP%X$8Gi+uXF$#cDFpGe-kW}GZAdMIMrCpP)K@lQ3n_xo*`{&owEGJ3evvzh*Oj$C-lwA&Y^ze2GJCjMUZ7N)<VZOwHTd&B7A$$2vU-zz!U=*i+mGX3r2>e@cZ{}?^=v&mEQPqsCB{4UdvUaK3-_$-CLmFY(v|B>S8wN1Ne{*mvdr}WrT)4z6}Uu1M|x#?expB!xT$S5<elErT{^|m&8w7F?FZU0bpqlcE6e$@5}KUFoJs%L1=*HZqUIvi-2MvtE|dVGG_lpa2}e~RDl>aJhog!h$6t0!|!4CwLRzrCC;zUmr3cCJXE-tgH80bTvc@5`pu)gL+e@A_2xUf*nDpdHYo&99yAuUB==KX%#1fUa@WANu8ZAWmrC_<*kYhyGX}&^1q2*Z5xU@@aLApL}X@px*G7l>uG-s>jE_Zv4G!&j|D*x_;m2fzts!e7458!1tZ@Odw8d<CuW1-#2#Pmw>L{*VQ$?#_>wD3dY~EIH>b|W5<sMbp5`rZsQXtULlXkr_rfcpdHZdb@5K=EWaN5Xz$a3@wxQeI)9w-(UAdN+riseA}iph9b8@GYn<r)f3EYlL$cR_fUe(5^+>xN!F(b!1G=_b<go%-e%)Rdj&AcIPISVUVEk`41$50ba{hck*F0U_#@9Gsb}{ku=AP+qXVvZa{5YHy@K-r9-0%0kY8!|Xd2w(+xAR-W`dI<L&P%RNe2o*TSSt`edEw=NZpY^jHM9J>9iNV_@ik7eR4CBSvC7{DbZs}Q7yV<cKc8@kMFCy=B~;6dH`TRYTwU|gIPt1;gYoGvtCOepuj-notK0a*3BNWir6>1inf}uG+0pI%jBf8QU*4bP*S+2M4-SlnR+9s9Vu!+M^+=w+0o~5qUv<dx>vrCDbgft8#5WEP#1FL|9nkIlBBN=RU$^tTs}o=2L^ibz#Mkkox}856Z>rn*(9t!%#);)<7U*}KXRNN{R`v6x0{Q5?p}HL>%rmOnapLHjkH+zaA6gUWN4+ngYo2!gSDidvUE^z<=!VTHJv{sVcm3l~_2`4`2l(}f<Ja+~x*eZCKa%CwHI5yhBR&qqiPmnBUSAps>bf3#yJwbPx9ccJ*LvOfRwsV=<g!4$dcC;1j&s%Rc;>oL-HvBR*LvOfww*Qp*qOn6I^B|1*ZEm>dp}}6w|>1JIl9fqiEr~Eesa~Mz&Nz)E_6F?Rlj*$AkXBPnrU^t@2jrYi>?z?*XzaAHBUFb>NfrdJ%jC5zH(Y!*JG;N>x=c9)%E&vblYxDeA~_%|J{axdUf6F>UQ0WZs%3j&#K#b($TeEH@@l`Kiarhu)lb|aCLpYP~En_<G1aPKOQ-;I+e$7V*~SytJ`%cx~*5AvmD(%XQA8i`Sr0xI$fV@RM-BE=3kjetLt-t>Wt55y%!Vdbh~~=x7Xt}eG}<)UDsKi`NYfJCXr6p`@U@leNOx(oJgnZJgmB1PmZmZNT<g-4G8${bEOmCK8HH-|N9&l%wP43^4EFEX&=?y_R)F3ZGZcm;<UeBrx*3F>Q4XKdCVC<_P*(iA3M&S@oBFMXMB1`etRtK_(!+n|Gs!|oO6A-y1l;8-RsfS?f$^I*8_2MesFc2A5^#Nu2Uxx>2#fcRJZFZ$M4Qps=M=*tJ{2z4+!L`^R27ve5<;BKFYr)kxtk7-0J!q<occYUv+o>cXiDt+`Cn<f4P6Ty57H3xA(`ZUP+|Yxj(9I@0*U_y`QS?-cMcK=JV~H!SPV|bRwOu>jBm6cyRpg`oSx4W3V4tpSZex&PBKT25<FGq|@zluEx>*1jp~Lmuwtoz2xe4y|lP&Fn`v2uCD7n)$Kf=t79UauIowF?Y!#v-Swx9<E%ej-L5~&7Y^j9>*tGfT|cX?_oJpw66thZpQ~=~FOJ_`&#UgP=P%O9C;nxDU_0x4>*#jAMYsF9dcSjYd%r_>pO0MKKEGEuzsi4IL<|3&NT=&_nd)}FI=?BAPS@u<tLuE_`km)N)%Ch_^KqXOV>4F<@{EtoomRKczvy;d)c>tSI^911qTBnp<G<*68Qt!CIQh8G(a~uy2HGt&dT%0~Zuc8ir`;~{JNp3ftTBOh2puhvR@Z$7)$P3W@5n?tUH2<gxAT(YclS3`xA$2mA9vp)dZ=?S&)2G_)pZ|6bvs{u*CUZm*ZmyT?R@3<-Tfb{Yo1O%?!HjCRiof_q|eumZs#|2yG~~Qbanguj&9ezj^EuMQ{7%iPCo9wnU}j>Fi++aSGW5o=sGXydfU}?y{)>f*NN}$A4Ue%3SJj~9ZjUubwAVUdc7Z6oJgnZzNqT<dUyQpKB|qQ*PWY>v%eY{e`KXUPjAz|iFCT|_o}Yfo%h}=iFCT|8>_C@o$Gh^nQgt~c~L&j{&V>0Wh(>iw)V3`I$ig}Rk!Wt_}%^U(6G6IcF_63)$Kk%x_zI*{Nw6&pC8@6XL0-&y%*4Wb-s1;ao!h%H;f77Y4@)j-R_T}+v}b6o~zsaF^!|wyW@A?n^;}%vu-}l`;_>Gp}{<L{ov?!eS&V^YwPo}qub|YjidFt@tyZa@hjT}#+6=Qu5RChpxgJVT)(bv--Dpr_o|NHeP5=!j$1b$_dQztuH1n<bv@wfx*ky7z6WQ$;p)2HP~E-<cl_@AMAhy5=H%nPXN)&Gyu#mZy54YgyWT*z^Nizn-;>5p99j`*2Yqjge$jhd^}FwF(Jy*$>%`aR$EX{h=g_Dd-_dQqYn)-*1M%&93P-o^Ptoml!G4je>wb~ycK&qYyYIonW5)&h#jc+n-LB_V*Kwumb4R!9b96hd9KZYCUv;~0=H%o49>B}lHjt<8SGc<UeFD0jC)p2ib=?n9-OiJa-~C;Ljid8`laKp*iAd3KFn@hN<>+=jgKozI`+*nf><6lD^Ks(4zYhtQtrX}-yT9S+c0UB&u7@4J`#TnI@rmXBIJ!UP>bgIsy1n1A|K{qt|E9XV-#LEwcRQ-PzuR$j`~G5aB9N!Hr>kpws&1dh*^hN~-H%n>{k@Z`+xVFagYCn9sjKULsp{_UuUy^!UaQ#~fjF9vtJ~kzpu4{-b9LQMR^9zwnXB9H`_9vWIQG8p=&3lZ1Am=WYu-cqqcyU-DEpJ!E8_L)=KIqu5#^s^`ajL;bL0QlpJvs$`MUq>pJq+Y&f(?k&uieDKK=&Be`bGv%l>=`9)Q1z=Us3*yhskuE0F#9H^bmx8HS(B{+!AF6v|;RR}RCaOgvwL`{7b1o@>C8@GtQ!1sB4v!BZWq3}1>T3J!-$d2KwxYjP}josU=Lcx3iDgR?*Hfpg&3;kgzJ!QaDk0Ne$?7Eckd0Q>-+bKn`c<WPawf@R>6!=uC&d>dXBPYApUJ_pY(@H2P_PXX{U_%1wWz@zX2c%-icf1=;c;E}!(^yoJ!`-#31+zFR5kG>Kt2H%foAvg<O5>I8Y6nr6`;ov}cWjr;(3UJBoF!>3dgiCJUQK#TWxRi;f7?^|lH&WkDywf?BvK-VYm<K)!&p_}Icqu#;z$@Vu;AOykaOvwF^r7JE@G^L=0xyBTPXE1)cMZo^;kgVvMSp&V=O}m>ei<HVr&F|%aLMiO3{$7zpK!_TUg{Kl9xi3#xdc28e;v;n@I$zi9j8vgZ{Tb290oVRPvQ9v{1ko|&q*)|{|?Vaa25O{9_d5DAK@GEOa~{yrA$0|z_aj4^!0SST{xDqv$UV!-*Cxc1+fKRg-Z_W$U|@|d=;Ka;CT3tc+P@*;FIul0XxFa;`tjq2>%=YC%6wTecGD768sPRPdvxL?eOREd<eb*KaS@cFb@9^&n9pg{2M%<f-B&g@Fc-?aLKJ1bqYq{lG}Xh6r2f<P~U&x&v3jQPaJ#`{tBLD;0y3Lo)zGW@MU<`fm7fs@Vp8>3txw4D;R@6OaHwJe~9C)c=mvq@bP#$f-T{D@Eio+haZIR1LwmfhhD@M><5<|+7nywZg>n&CO8EC5T2G`6L=<`_ra&&@5ASVPr{{78`D>Ucfsf5nF$VnNANrYwuR5c^CtK({24qifcL}S#PcHf0Q?0!Q@~#E7x6p`wug(SDn7yLaPic|Cs-fe3r|0=CcHhKyTRMw{qPI{uY=!>rwJH_55e;kcmw<?_><s`aB1@jw58y+@F(#M0B?rhg{Li889o5d!{Dv(ws`IbtHK|~^8i>EeogkL47r4|KX>rmM8Ar%Qs^P{D=906UJ5-QWrfg-p<hB-F7!g^|9Yk@2YN1aSwl<N-=5KPp#R4D`ge3G7hTqNvfdm{oGAWBDI17B9K8o+kDw1kzn8Ku=#QYcrmQ1+7xZS7wM6fT-k7o`=q=GJP!>j)^0(yqDEsp&I2C?Ko~yDyXTg8qui|+Hd>#G@d<r-X{zvxbuk242_!WE#o*CdQcov?I!B62c@XP}j!9T{c6#NK256_3-3iwhybHVxW5Al2gZh_Cm^A;F`e}d-_n1oAibEs2r30!j9N}YnM;fwIB0N24k!ZROy555A=7H|iAKAspj8@>fk68sJx!!s3p2cE?9512E<@TquS2j7Oj4xa|jgiBvvpbrI)z^CDv1<rwgh38XnD_nB;kvs%*XBaLyETB%oO!(XInczaW<Zx+*i7og&^~}UG2YeqcW#5yB;4b(aJWIe;@U3`OgX`f-@T>zj!dK&Y4_pafhi3=47ycfe+2CUMUfO5}{6~&w<9P>M0GHhMQK#Texa78hIt4$6ug9|zjKeqL*$XD%EAcD_*TDDU`4Kz`UyNq~xD5Uy9_eqvD>4jUfF~3D0G<h72rh?9U+1U41y9hQ3-P=Uu7yk43EJrdZM2KBwY1Y(+GrIyY^F}ZP4Exk%fZj!l0#wg5d4LDmg89qZih?RFXSP3489i625=92AD*4y7w`>uJ_q;1cjAeIyWyYXNr1=UaXf3lZSVx1li+Fi8a&Iu&G3_Wq+bP#XBaNI{Xm_9Kf@)rpQuytD11Mj<KVCG-FUWv-@t#R-sAAR)V~eSX7DilG#<%Murz!#o=xCE_$K&g;MZ{J>k{<0U>^8qc(#Mz!lnEeeJ=bI{ka{_9`Faal%1lTPSHkRki!{b3!aBd4rR$huq6CzJl}#D8HVS<Be4aGz`w=w19&-H%Ea>%SO6|%;`tdY2$wSP90f0fOPP3n1&hL^Og!I!9$d<b(pQ34!=+3-hrx67TV6b+!E$gZJ4gGSqwNloLp@>(Hh@bGHOND-7Q85)tHFkF50AtaydHivo^s&ra4A1SF2ZYbEO_4gFTaUn>C=kznP4Tjl!+$;?=A3>c#42k;2C%>2kXF#;3)uBgI|uPAXpDx0MBJ$4Y=fXCv^(8fJ<(}s8jH9cqKelz;^Ik@YDhOz^mY?26l$m!BY=>5MB*W4X`)79-anZ2Y3xUwZQ)H26!5R_rPo6xgHz}Z;0o1uqpg{Jhj2m@Y?X3z+rI7VJfi&-+@aG<A^QT9o`?$P;egn9z0FKR`8*CMuSV>qv6BA1#s!p=Jb_dH~26-kAv^RTi|I2j)gytrw=#{-VRS^a3Z`9o(I8~;GOaG2B*Rw#M1#B2bbKwpiaRZ@G;ca4L+IUckxUEH^9f@nFub2Ps8&PxDq}Q&s1<d{3Sf&z}MhY@w@|WgO9`09efV{4xV}7UU+vrt-wz3d3ct9hu}-#3&1bn(${ThpEk5nH*#1_Y{8e|lEX1#3;qUw4o@erD||1WL*PH~L+~%a-{F$OedHlH0saM^9pDN07(A1~kKjA-YyiK7PsXzx`~<!M&q{DJd^w)=;1T#rJg<SP;p_2i1CPNaw>PL$a4lSNyEKQXQ}9>n{|L_~;MZ^|`;|HczlVQ<=Lq-<d^4Wa;K%SIc#eTNa~QrF&&%Lj@MCy>1M|XP#?uw-3zstS`~wz-%SZU{V1Bstbx+!<Cv7x=z8233@KU(sP@FsjOT#6H+2kQO2%Z;DVXz{+Fg!n47A`qFMjnDQ;Q8@f3YLJ+pr78ryM^OR@kn0@UJhT2=WFl>xRi<Kd+=xa?Q1;0fEhUqm$IMfE5Xm<zu=K}%Ak#ee@;JrjCVH2l3O|Q6D$aq+;&r^;A!~fc%)9jKdAo)JW{7%Zt9n^Kd4hM0hhAe<R^GF{Bu0B!A0=mcuIp+;Ir`z0!P40<EaSNf>(r>1*^fOub-d~1?R%c;wb@^gU`UT1>6mn96lfq!KdMpLk;Q_ya8SdUJbk+E;)=Mw%}rTH9Y0OO7OXOc7s{)a(D`YMd7>goCeRs3*wQ!61+gaoyH@5C3pq>CS@1sE5WbeQg#J>C0HJwz_SSa0Dd)|Dqs!e8D_6a_9<nbt5Js8=M-J`jHFEVn?(Ny{Zh(uqf5Ey`6;^sJvVw`%8H|3fnI{L(&$oN4qh5hS$x7Pa(p|Ua_Dzb))f7A^yZYcLT`%RhO$oRt<dkItSfpa^q!RUMemCK7-fUd`=UQV*$DJO=%Xlm8ePhVWw+yy?9UU~pC{qN;6phU{uIYU;g5r(;E%%xg8zXJgbxCrh7W=d2FJk%!$*K);UnN9!Drzk;lsi4@Zs<%_!2w{9}P}|kA^=3PJllH9|OJs9|M0LoCp_u4*nd+FPg_q@AB-=rJx+=0&~K1!SjM1JTJTem;+t_UI@GdUI>0Acp3akco8r+ya>D~m<L`IUJT3!F9t6O=7*PrmjVmIOTo*4SHR1_%YudBW#Og4;_%Y&65v(v67Z`%Gd9|IW-JJHhD-l8@l5{<HigR=Ys-0UIY+qkduz^X%{jtlthVF4cAO(z#zQO4YsERjWz09{yyl!ET*gNy&g;ZE!fSixS{wqujbpi{S`e=Vv4qPQYfrrP#1byo=}pABiCDtrn!ST~cMwasjL`>(_W-ek%XNJ-@opxTaG4Vt6R$C`gv)rpk9hYHOSsGfb%|G(Si)tlsYkqe#1byoR4?N7B9?HOH|i6wKCuSUMz;~~Hev~vYqkgRdJs#v%rgy$*ML~UyK>GXcn^+c{%Od04LL`+%pqOyci|l2GB4fEdAD<paG8r9<h%ztN4U&a%{Z?a=jhzlne#ex&Un6~{4DYYcx{datN8d$91B+S@tZjotnTA=Ij#<`3D$=T*7ETN9M^(h4>p7g*75P%Ij#f06>J8-72XJJ3U36z2W$ct?BL_AITpO%$6IkMc(0Fl;`m<pLtuNjU~eCPfMdbFK7Jp^f_;3v7srAR`*;tI1t0VAt{e+K;^SR77VPfh4|3cc-VN*w?*@;6ZQz0(eY`Elf_M9PJB|fg`gn7W1@H9n790zPef$oN1#k56#vBV?=i~J_7QDg7Z{xTESRSkaFApyVR)Lp;hrnv^5d0djI{X@VMX)BkBK%sg7W`UxCGdK9C3t194!knFDtIfrD*P6(5nS*tAHRp=yWl;+4sgLoef)lo1^fB<y&Mbn_wk1~?hhZ3{b}7IBS(>(|F8dA<G=sp_ZME^KiY854F2rff9BiSvFwk)TerAW)+yPGn;fZ|#eFi$z5fBp<&Dn'

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
