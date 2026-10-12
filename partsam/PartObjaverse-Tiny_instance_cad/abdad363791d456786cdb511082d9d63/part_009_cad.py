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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_009.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_009.stl', 'source_sha256': '7c2a3002e6203097c414a8b386315401659b58b847bad351c8739a9ae8d004bc', 'input_faces': 962, 'input_vertices': 571, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-4.332510471343994, 0.3520197868347168, -3.7855567932128906], [4.32015323638916, 10.849968910217285, 4.862418174743652]]}
GEOMETRY_BASE85 = 'c$}r33D`|l-^Taz7&2rYLWW}s5t)a`2}v1}5Z=m>M6Z%5y}e4OB$blPQ#`4NCXym_j%3JC2xUITWXOX@6kgxD*Sgnk?f*INb$!?O^<L|`f9w9Qz4qQ~?fqZtob$Nej%~ALFY1~9%6p08@3hU;!1GY9_lkPM`V1cWc<(+#Y7Q9qY?@b4`}oi5gbrQWckG_#4fBRqd9=@v-h-<&2~}zOSfeU6LRB7nYVgp(y$1ArYVf0d;J5De#E?G9AJVVaz&@&8wSL3eH9~c()d)Qw`ak}cM_oe3^PLODmBt_Zy-XO_bo-*g&0T+fuCnkW9cp|ROW}tfd0>s(K5@0PX`eRar&tO<JSNw6w|zLVQTx%#2Y1I(_>o1!_5`lylV0U?`@VAz#8UY2OJx#n`;4PqL#f(ZU$&2IdN-8ndNP{r3#GdLjK0~*ry3vY%kc?~Em+<i=ZL-E{n^a*%=jP?OX2_5_PsI_t{>&~+i{DC>$md~ZuW9P?XPY98`{O+-jF-&_>m1SX+L^z^<1tWzLNi>zMo1x@&?*h?Q&M1FZ+djt{+|1D+|6ib7X$k&uE=-5q{{M@c}>DXGu0a{_8*btGVOHKU}YUuUv(T0e^6n?E1cb-*DCSqZtFWA1c`-%k{&33gpn|YkIrqo;TjSo%Z8Tu0HFw_eOWksjuhh+tUK$(0ID>dv^TYZ6Dgc_d4Cr^_v6j<3Hrl;~1^o|8(Gbw(Ze=#vT3t4D>VlJv|@MAvx0n=iRzn``*@n1<o5^T3XLX^v(*w>nz*L%+r+anSt?%cD-Kv#fAjN!3%$={b=qU=K}5PjMMWPpOE)L;QHGxF!Mb=@3p}7G*8#_8d-Mpr9eNsnw$APo9~K#UfMomo`?0b3+nswMh=TPzL)sW_{WNDasBX-BgP;2)@HY#Nb76H|8CEIw|#uTphDWOyK|4*KKjaZ?MG+NKI*oQ&TUv&`!}vR<hBnF=&yb6Lbelb`$(lqMYP}HUq=J|zy6T%x7Il2whzty#`vW_Tju(SRppB6^X6I==qFUQyY{^sj+_kiv%gR=-M;$N!-4j5@6^6`<ksH;{jWJ>{LlODciYGJ<t?uJIoS0`p#PjBwC~l)zAZ2g{iYhf_3S-?aeHFB@fRMN@3v2j+-Lk;m)E0xs9#4jZY{@^hM!n*=y*!M^%b3me81gKp_J{dFWSco4b%BH`u!98VyXOnvk&O}cd3QB&R<99d5P9OpxaA7-nZaEw|%tvtkS94Ti>>iv<RDVlX+hHHlNd%>zDNH`el8&e);XidSrdM9);=4bzJ&(9kjk&m!)s7)A~v4k?>{za-9v?{>8q<_r<<N`gR<wFZUtRx9h3(<vN@Apmv^A&yV!&^I(1X{7Bz_-d-G*TaSatlh&7c()uz_T3_Z#>&rZ8eVHeHU*t*uydqEf=M{O<??>cG>&rZ8eVHfy_99REzQ~h*_aDrYe*Yp*`r{+=q~DLolm0k}Jn7%B$dmqgMV<`L>~F?R<jEwTdC&Jno=oyZdzmMbe48g<-<J!%+&5ZZ?i;Ny_l<sgv2V1#+&B8?75hfNz1TNeU+x=yU+f$Ge#E}fzkacA^!pL}M(fLcqu-C%H(For8~y&pzR~YT>>K@l#J<sQFZPXo|6<?hw-@_He|*Hg(Z64@Z}i)XeWTyM*f;(?p22;i-;dZgMkl{|Nw05jyj@ZITdKaRpNsQtweO7>y;DC|>+@fTrSfl`ebH?nTJx>h=k<OkM?953<*1%F>xZ9NbxP;)L-TUSQ}~hMnR(py@yZE3E|Ha6^2Ss6(aaM00{su@$@?#wFP_4Wu6!`R+deU)pMDO!ZEf<q?Gs<GHGbya0)h597hO)(e<E7`N~-=N*%Mb%^%LoN?n<ijMm99Lma2d2%l^a1^62+8l3R?Y^_!m2;~9_7{Ub2%*V-M7rSeM+)_FcrX^)=&jF}B9xzCB0qgIydM<Xxlbx``@4Sn?b8(w_Nd3~Ob_XYY1-~H8D*N?>e>HUNBqgkJu{dWFW&jzlu`S8qGDu2_PI-htYTWLRfPv^?+dE+IHpK<-jis3)UQu&!{^g15i)9Os%ew$T49ZThR>v%@z=^+F3I_wRb5jbzgv}aES?)OShy>2G?#YgFUA6nk#gxgQ#(~~=6sr*Cr&G$UNtUeyN{@WHDi>2~A|9D*A*P9pgek7Xynz_z1dk)7^_>nwm$8`I59y{!gbL8AK{d^?(FMRxmzMl3y4hEiw1{L&kApOYddV0N3Z?oRlhiWYjj9cRJjQxS<=idwTyeIkBtu*sqtIU44pGekkyJ9K)Xw`c9xk_C8bdNhe(cwSn`AzaCp4ammK2dg0VEoI}GW!JSH|l)CjKiKE_4pi}udg$nw)b2rKhklr$@BO0{z3P*`Q?<pxAPU#&*`S;T|bev$&5qs;pbdG<LVEAej)`!8?@iGcS=80zpv@%!HK&6F#Y(XQ|7$$DxP!w@X*ZQbw2gnYTeKJHYxqcjU7z?v0b|VsP#X~VdlNn{<E$hPtRM~?I)CDcibJf@R%OwQ~9=iMz*rr4|kuE(vLQpYVK>q=<}{08Nb~4Q*H_P(LpN${Y0P6TB+wnteZ(b*G=oobu-E5x@mp6Zc5*-o7R`>ru6N)>GvbnP3hZp$NF;J^nI~z`o35<eP67b)|cz1?~8TQ_r<y?ec8WUH<Ns>o8IP2%k@0YdL=OL){nG))jTJ87wYFEv5Ef68;zeQN5GHQ*c|95@m8}h^?8>!Oz9`CHZy*^oH|cN>3f@t>GvZ3)uOYmpHZN6;C+eI=(0qgx9hW&Qu&El!_9Rz-eTS(`d*D+jKBBDxqv@(cknuMotdw%f6Ks>zW2fq^PV0)V%~T9@wN%$*WGf?^`n0s3g(UcgEI7Za(zjx8-6k7`2IT5^@psK{^3NRAAdh^Ps7YuD*xxZ&${jX^<qK0y|EO&zps$~Q*F)fBjWlaoyT5seSiHr5;_-4<qxWR-fi!%FFQM*h^6qOna}Eckn#PPH}!q>xY1nC!*kBMe#V*d!MtkQmpE+Zz3BJn0{)4k!Th=2_@O<uQ~Ke7jkKTmpjcMGPdu5jedP0jTpv%Fb?vTBlbfe_POLAVlknZfm(QW~<#QMra^xfJi|5?;<#RsN`0_onzI=}ojhB34@<i}GwSLljdYkcO9<aX51L571zR+=zXRI&tOn8s+WgfG>%wrivcP-VvTnFjPbueDc_;Q`KzFcRcH{AEN?q96q()Y*V)TEeJu}`qR+$SVX8(;22tS|Q=iOB=j>VCvN$NF-glbB+BxsS5G+(*SrPTHWyU+fc-eC`vhFZT&aKKBXMm-__i+kJxd<vv0BcAwz)BlZc>x9hC+<vzjp#XiCJ#XiCJ#XiCMa-ZP)VxQpqVxJ&=*}vQ;B>CJYgtsm-*D3bl)=%1pZ!^B!=UZRy^F!OKZF1iW`#D1T{=Rf>`p>!_@i`^Q=jW8r7vr@rKL;iG_H)olZ?`^9e9n@-{hSqA`hxc5=e4l(`T5S9(|fPmkN-LPfvLK`q|cSYx1TGc!@HT^k;LcLB%hyKqy2x?-+#!@#nQK*ixXciIp&U!{oI}8^K*A(T9e~}@#p9IB%hz_<InW}%^e^6y+K0y{N5mOU*v?_kN<tkvIeK!@v+}mM5WK~H@u6xP6w`^-;*Ty{GP<i)hyHX{qtUpX1e2Szn_UnpWo+%8!gNX+?V}cNci@9q41oW&IO(y`#n`wmGgo7vfon)-+oV(D6%~(;M;xOXR|K^uG4;RCVhTy79I8C#enaR!_rHs@_&-g{BM1k|C4;?f9uQqFMXT;tuOPx^lkq4`w{tH`Zj-BU*><`7x~}!MgI4Fk^ikP^S|$l{O|iB|4U!?FY|wr&-@?V*VO!e@Zwti{eEI<$wIClpVU(SPT+lgAmB&-Q!icXj#mr2enz7M`uCKKhX)mL{ltn9X1y;nB;bdyncq9&6Y2%qx2$Q-UwlVe;CeRRYtG-+{4V34_w-`(dq<5|vIVd63*%RtqJQ`C?|0)1=KiO*_{;S}T|Y42<M;k0dtiKiUT1zcdFj9<w|#ujdF^|Hf6U>w_r^SL_8-;n&l$M>sT0g|*|$odAFp#aJ%3)U`hok+C{V_Hk1)S$pr3G=y4v@8*9`O%p7F5$oj1I*{-1&S?KZ&t{@WodaGe?J{?vXXF)MJtq4_!Ve223tUJmrrc%b$(-W?Yl=Z8j^-;p0#9~kHG$m7~i+|)chaQz#9H~sf`-^^qCPUgJ)eKWG${EnIAw=utCT0hL+H)VU@7wt3b@0)AQ@19A1!u;+TUe(py@Aide+^U8ax_<cF=f<DfZ(YpsBeSj;|I^$*x$WcMrkn9ee|NXr-a9(h_!EB#oHzdTRO9D=|8SuHuHDW1c6i#6!1X-Z$Nc`@qQP;ueY|`d^Iknx;@7}^jp$;2XMcO*i9q|$HyM9R_m5mZ{A)||JA0REfquMJ_ZffA$Ur~gw0h?E^qd=m*I6KJ{IWTM*LlV>zk_dUln9JNG>`FLejqRo-g}dcKW;-{oWtv88oyFvSKxYv95a5$XBG#p|Lx<(&%SaE+J_z}q2K=u`*$5nPajC-hb!gQ*J=H*{ksm)-ukwEylo|uU+x%hes2w*y6pPi#4dW?L-ppF-)HG(v|nhRhvQ%C?{oe3tD2hetWkZ3?q^ZWf+_o_pVUA7r2cJt+5hyq+K=+@aH646vjV>Tdz*S^O+UhqJU4#5+upN(Z!^8+u2>2`+O+6Cx4r#)C)++jKg0f=($F1SQ~8k+bM^IGKWhJeX?L#uu@rtdb}A8QZ~sn7^l$y7{_Wo{@qWD-#t-rDzM>z0qMsA#hpWU6y6vO(@4<MT(zn-X{jmLeFpitw-u^up=f(OS{~pZFW8}UDX57T{FMazwTVFo^()XYLcuRA?BF`uJ%-hzNc|OS(?PZ=%@|ovD{rj5n5qaMFGS6FI=6UPOJa2uO=l%8~&-?w0JnvtR$n$<bBG3ExCGx!AUgUYdf05_?>lb<6Z!hw^?~6R|pI790-xqn_Kd;F1e*YrR`@YEYem^45XB=B>#z*XXtuObz)|dNU>&tzw_2s_T`f}gvw-@_f|9Zr}*FUe=_x^pI!F{iPzhd8OeYx-T+lzg#e?4N~Ykj%z_1lYmuiswmd;R+o`(A(C#J<<}#lF|SezEWM`xpCOe;mZV*Y8K{d;M`1`(FQg#J<<}#lF|ud6!v_<+>n!=4a{q>jizeK3ZR{Q(^0ib=>#GIxc;?u32BMztWfImFvFr?fT`PSFG34x9gzqi*-}_vb|h4!(!azeaZDy`f_{%>ukrszaqQ(a{Yx<Z&53ZD!IL)-ebL-e?kTm|5;7_Pskpx_rLllWQ`lt`TzbCvU+Kr*GQGds??*_SLIgLEkkRoQk8Yf&}ynwV%;*dvMOa+w+t<(N<P*tL-VVWn{~_3JgTIzZW)@c%5R>jTZW!cdek#@%g|%09B17!^jAzonyFicUQ;DknyFicUZ?c>G*h<>&8td9)-6LTs8WS>%g~!tsm{7(=*_CsW!*Bgjw%gVw+wB-Ic(@~17|Lw{~$vj;Jnp$7}}ikR@-6dZJf7i4nuF@yj6A>T88sh&S7Xy&Rc$mp+`7xc^rl&IB%$1hVJFOop2cX3+L~c!_Zxv%U>Oa?&Dlua~OKiGxLVJWoS0e8|s#!A<kO`hoLn&Z#Ov%ZOVDO*<omy^H#@UXgAJb1Bbgga|!K1hIZw=J>W3(cFtRKhoMb4Z?`!Nt-*P_#bIb^&RZFWp*c8jIUR-`=DeY98G3;8mT(xlhx4}AVd&4Cw_hBF?&kdMau~XwbGgr9=poMKL5HE)Id7<2hL-2Ng&c;~;=I*#7}|{U*3@C>9h|qY!_e-W!)^|D=UjfPuIootHhG4jF?uCbykMGP=qAR&1z3k};4!FMhJLNejVfMTm2G6`PS1G7RQZ7n-Npi5MTV~7G20x5ey_?6>exc6Y$iiDdd4fM$`&$oGYfb%85-v?n;nKOX90gnhAyUuW0#SaG4>_-D>C#89`mKc(05dMQC-^zRh~~X42{wouFAj3|7PrY@<1|lFpqiOVdyg)gCeSI_Y806{lmk2>?A|Cv+U&9Zl|u}G20zp$NR_ptWf0}@;98D6}<Ol<YkO~Ltaf@&A!&KZh0NgT}oYBVO4%2Lw9(_E5T>8F!d)E@V8{>S|0P0!_f7f89$8Y(;Q3a6ZA0t!^p!Jdzw6m3?0B@o^}}ePtF16;xRI`A3dD!5%MF9Jw`4`F3IP+AM2K(H}D(}snV0&ljnbk^IL>mgt4CFlH`&+-xI7`euUSD`+HQCUgTc9w@3N@7AF^HtQYx4@{K(I0M;!(#Or-ZmENj6OosNSSAuijoBA*dxD*-sAdh+2Vd&%R1IPCvLkrTw`G$~(FxH3sFEX?*kLlwuv;fb6b4AF|C+XqZijs>m79kfS7vuOn$-3o7Io_+754ZCDf__J@82bW4w=!Oo=ibV9W(SYi>ix|-`26GjSgOiO@=CrNOZon;Ag^F-C3zKj75iJuy5;ZK|5rSI33&-~-%_40MvgJIg#0xb`Z<qT;_&CppO{1S!N+@!^Z6X-4<6p%5#$k!Jx6|#41IyeJm>HWoO{dx-uI#8p`4##?EhKvvy2TTKSh3u&*PJ<Tkg;2rM)U|sxpoY?Wjr@RVJx2kqqsuN(WWOs`5G+dXFkCRC!62kz{B~RmQN*STgi29@AEpd&&2*zkAsJRWh^<JskfU`8CGIu%ElhcQe+O$G0K3VXO_0dxZ>bO%KP7CXZ(9H6C{t`7Xw6U#-cl8EehsUM53Z(Zg}0$fFn=&ExJQ-^rNms};EwW371HOXQb0-Y@gGk>rt#jpA`F$t@YPeYGIBU<`A8zbX^RP&@~nIR6vL(D5AGF`U!3RLtdls=Ter8)RrZ#>ev5x2O|1_xJML9jKjH#<Q<Z)cfd-WxwO8Z`13*bB(3GL9Y{!?LckEbK*MQBtzTN!*z`#k7H~CudO4wBV+gT`1a)XjCEqY3%Lu&aRRS<B6%XmdA`aif2i`OXBhgiDvMP4k1AKm(1ofjQ01a3=gH8ys?1X5q$;P#(AlbFvCTy?^b(Jmr^-j<kJ#T_wm(aTzE2OwpCg}REQ|eoK>mQSc|87o^81Xv&*RRJp>ycrxJ+^;W9N9>d*t^Rvwh7W&tYs1k2_6<X3)cNzmtDwER)B*OMaIz+gAoTgRu-AcanUP<9(XPog$xN>~|hFn>?E_+t)1eEXFX`pQ&<%48?Qssb}W@Dj9m2W1Gb}okzu7exk}>s$3vLKV<wOkG(|2ITrA^&&Z$gJfE`7U*x~o-(~i5fqa3ni#+~A@`sEq;PIc3KVj@6UdJC~=zMy(u0P3tGIoX6_A&Wm#y;cm^U3oW`;_%X<V76EE4=Qj<f|O#>s86GN+DH>unx|{I=C?F;9RVObFvQ3&N?`qb+E@eIE{61HrBy8SO;InI=CR~;M}Z(^Rf;u$~rh7>)-;c7vlXDAoo_Ktt#!w&_1d>rb-7@+L57;vTZxY+EUvy)|<yZ>hzJHWB3m;v@<=7=Og4t7%RfD?L_XxSRRgZM{-BT3Ukc6le;sPi{sym+>5cCoQns@4=|RU^U{;tld*Kp(L>~i81pz^50f8eERA#5mE4uFY@EjkIl@>D&S^JtH^$&$e(xpU%NRV&^?l^~7=wp-zn^?RWAN|{^dR?O3?80`2gwgI1`p3h7jhTI3UK~9lRGo^oGN#!au*poLY1g0cdK#_8Tz6sFR0Q+mDXhF^DM2|*Yi}{cWWMVC-pA&Il|$)c)k~So_ommILEYM{VponH&m0_NR=w8R7*E?a6Q(+H?a<`!#em@*1<Jd2iIU7T%C3BEv$oUu@0`yI=C+D;Hs>H>$47Sz&iM5*1?Tg2RC883h%E8d9!*bPpfh!%`o&wRen(AcU4Z2p_|zD6l15UXBgYeV>dZ{G~yT@B12E484u&Rj|@eu8prlmG8D0T9Ot8CC}KBp%oAiNVs$wFd&p44ZslC;Cqogd$$8mDh9XvjbMy-tidc2d*KRTtv0FHI2gp#wYH=R-lA(yz=A0fRLlLXX`8`I4B36}ieVhzMtUl-cH!>8l27Cq%lc9*+%;(_<8H!kAJ{u>=P{f+>xj8|GBKEl|XH_{*hJK;Sm#SP)C5sGQqRL`b&Z&|~hAv{sWM7M@w(m?HbC!CZeSYEad7f`E&yz*Ya*jF2`gtnaUsEL=iCmSdtb;G7nL7B-G*bs(Ofz-xA8DozzLaL_;J?yL9egFt)WQErGj(tp>)>pxgLAMBzK(TpZq~thSO@1~9h{SOaCX+g>8yiSr{UkUc-|`NH)QAvGW2UQbSWA76&bpW3|&r!t|UWaWazhK=yzo3S~7G!8M=WC-AIOhPlm1|L)Va@tI2az$xvmkDj%>8{*ZO>eAdAqvkv~0b?`#g!Jn}X{)Bb#N34SvunwNbI{1Co!SAsSewTIdEY`s@SqHzvI(Rngb9sNW$;H$h-=NBk)KX+<88Wmi8CsqUtw@GeCPOQcp%uu`5E)vI3@uHDmLx+<kfFuN&?01LAu_Zu8CsMKEk?$(eT~mDIL^6;ca_ieHENvRWj^Cqso&81lh6BQ>I!;z$Cr|qG6oOt`&Z<z7=wp*e;IihWAKm%mXnt=1`j!5C3z)d@Q@#3<QQY{kSo3=f6G`J^Tv1N?-<L*9I}=SMJxyN$$ByrvFn&yHjtr+<z}AQNQNSohdJkaG8C~~%s=bMP{eXF7p);f5zEfGTup|q;j@i*7SD196>|>{?{6t`DL(J;@Gh4jm*KMy5AStZa#_9y@bHe8Czt0t0T1tcMRG;HAMo(*S0-2Hy8;h+pc1(f-y3+y2^Gi{_zuBCeh866e4pSUSCk`{<GVFO@pM%Rkf8<BjW<n|{A4I%$ScSvCCDZC{=q|TDNZiVcX6uXDXLsghUQB*-egtslA(wp4<Y{)CKu-W3J<xcD7h%#-PxSWV&r0ck8!W_cy9}+xWCfOBL$g53i7_n@t7GL8z^Gv<9&|BJnD3MxbOTN2k10<rP*gmDq<L$SsaUZsThwU%v1T8qw;Yaiu0JM97`x-=wl|wZWeV4J&aRcjvI6`y&~+h5EZelDz-zFpVJIOe^O<eDmzu#PKIt_+wF|)p#IF*Rvx>>>0^l67Cf!WAXNr>rVbv!I`|3J!T)3(+>do|U)I5ovkvahI`~P}!B4Rc9?Uv;DC^*1tb_l>I{4qLgNL&YewKCcGprBd{XIjzU6rP)G@&*oLmQHz^~un>WN2+N^j0#o4jEdH3~fM$HX=iBBSV{!q0PzAJIK(MWN0fgv;`R&CWm>S;7Y1gP^GdeRaggCV;x+bb#M*V!8KV2*J2%f3+v#USqE2T9efk(;EJq+%d-wH$2zzS>);z%2bX3YT$Xiki1o_6zYzH?Ro+%*Jar-&I++ZeN`_7&LuZhoGs)2DWatz!bP^dlfeal-hK?me-ylO@CqrK)Lti69$B?0KlHcTgg7IwQooz~n-cAqiZ)0*}#^B*yZb)v(7(Be!^~v=agNJv#F1apa@bJFZCf8;R9^U<1$+t2F4|$*txejCSkQ3^W>oEoo`Jn;10b}rxD;kj-F$NEL<2LebjKM<=X-00w7(C>Y=H%v#!9#AjgM0^L@Q`O(l3Owc4>_k5xfNsZkbhc`TQCL>xhPByGxiMU?{@O-jN#eFJNq^n`W8LBzZ1z58H0y+c`|u2WAN}^PbE)f3?AO`Y2;~)!NdDLgFJ&VczE|`l4mjo4|!lZc{*e8kQ1hmr!WQ&`C$@y5@Ya?D<+U9Fjh*HlB&EyhK{CJLX}bEQH&w4AfLQJhK{9&-10j4b;fQ`rI;!&k)bcsE3V2&@<_&zhme29kfE>93wh=pElV9kuL9>TM17O@T9Ma&6BYM2j`u#AJev14f$d6>OEFfF_gR8mf_;_eeUBoKVyt7^wDh9c{@edG$lw3rZ@Ij{|51oMGWh4<?vbrkU;ZD5cWj#j->-Y=>VH^>OX61n?|%S7|7|+'

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
