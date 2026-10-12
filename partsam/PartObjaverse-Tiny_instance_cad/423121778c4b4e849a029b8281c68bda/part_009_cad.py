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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_009.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_009.stl', 'source_sha256': 'a86ecc94b39ad58160ffc0ba69d7fbe745fcc7bc868694f57461362f6be7d343', 'input_faces': 1206, 'input_vertices': 863, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-22.900501251220703, 53.759517669677734, -36.732601165771484], [24.506933212280273, 118.53144836425781, 12.444025039672852]]}
GEOMETRY_BASE85 = 'c$}quceoVA6YcC?z)MCXCzqTNF5!}dA;(LQoR^%DoRtMsf{37~AR<eYq#__mfyF=&B<HwhP!JO+KR{ns)#+iTnLpn5-sP*WPMxl<>FEg_XKB?eAyqa@{t8;B(iPb-ptWU@WU#VXWBZOAJ+OD*QRRjWpAfLJFi(G4zuux<N~=x*YpgY?c%QzbdXFq#Jyg7AzpBN{go^ijcI4=hJ%{ypc4VKv#5e3YWK>_pj~dW(cwc3gs9L3BnNY=&WkSz|{vZF+sUp}jeykExIy`MrTU+VKh?76nCO!59^O4m*w;?`UxOp0~qw7ivzhHPf;$sb3q$3@j@Ka^tttz9~->y_B7uj~7qs+%kb#BdZT3FZiQ2soHnU9Qmp*`pSEnPO!R^RN*$JS<khWWX%jLhFjC2`7~XvO@3R$19zxU&-JQ2XzivEO@L>iF_KI#h7;Hu%^Z!CG!UzO7LT@$n%YJ^t2~>Mi`@hr!2E8kBVN(bn&DV&3qNgAcdz`bVq-ow?rL@|GtGK5oQ`fsYz-;^3{Ga=tMgALkoJIW-@{`C2mrwcNbbpr)MHw9>Ylx53A+q%P;-XD#OQicI(Vhc*9=*WWspoy!@S<vnf)ygf|nKUR3E`2SF&CGnv`IcvK4=<De_Fkjfqhq8B+<AM)^w@3fX_o0nA;VV;wM|}HCt7H!k|ER(1<639Ed>F@#gO3j$Epe9j^4@RY!{D9!3Vc-a`o0Ap1Fx^6<}F;`Xy;3wIL>u{zHV_hAHscW`aAct;qTnHQ@y-%9~ykPb7B{+2jjdV;A3xj>mdq0684_2=41Lke`=(}*_BJ)OMN>Q;^VdG>v`_%E^=NDugeMEI+!ec&%s<j_TrNs-s&ZMcyiz3Za((E1TIhL9mD^g@UbcI|2)0a^W|A`9e1bHaq~9#cyhVw9{%i==6?QR@TPyfa6frJ82(lf@R8CU|7bJ|mosYmFB3jA75-b&NqO4tk$T%T-FEX~@ZoLe>bUtR_}JZ*W&HT)<E^=VA|DAKsau%OEB2|x*L)OwbgRVIyj4$l>u-s#`4IScCW&u-ceEmxf6yv^PUEEmIrumWg^%wa?71$Qw+;;UTo=vTH|{t0^ACg9{!#Fu+#Nc*>sj*=@cO!FKD_=(d0tF^@cO#MXC0~Nxh{wA)N%99by?HbcJt14X_3FIA0ORyt{5M0hVXIJe|V?xVeroNIwZ%{ymP(YljDYsI94+`uKmR}iPIvL=Y6R8D0uxoe1ymQQ1ezx;cdJRHLu(K$OqNydXB5#hff_W>WPE*p6Tzr_maH+&U??`!!IOz-h0k*!Rz;)b6()}d(Y(cdoQHp>-RItA6>mh{Plb9Ln*)J!zgDMe5Ao@IbZ#L8&g-VFZfWjkmr4<`H1H6KGeK^e_Gx0)%EarPsR=2c~6e_9yijZgy+4g`8aszy?Xv#iGL*xzyBlS|0}@9Ke<ri=>EX+ZBNHsysi5K;A1C*521aJEE7Hg-sx{>e&d^RT*QyWH&%A@I({5{7<>qEB3He<?pMUYN3Xo%eI9T1uHnlc?_ABz$H0e*6{^a|yY!0pdAuocOg>!1>#v{F_)&=;{&b9#ALnJA{Dtem2CwTmdP4a4Cu2PI7Cr9ebv;|~4?RE1TR&SSS9bGG{TRGc{~sIvy8gk(zwYU+w`W(>@a0#1EB&`a!pHRcYMA(IUe`}(rTAOlJtKVYSEZg4Z`p3%?jyXl?o25+AAWAG95=1kKdSln#Xr7hN0Pf9A}xz?e>DQ$>G!ts@=m`Od<eXAKO;_P)b=EI{acIcCcAlk+_1qr{oZ#Be;hXq-rBLvbKK~%#<kqMb3ZH>KDu3a=e{y{=RRB^e5~tMiC^`bro`)ZMDro=x*d6hM?0eV2zcF&I6T@N-A{Ioi*`r%lQpmV^ST|;ywh*Td)q0G9-n^M&ExO1Q>SZs{GD;A;qQz$4c=+L&UxcF<4VKdY1a&Y-JjR(h!aQm&y&38rQ5-97jL~e?b=jty+t!O@wA&xdBE#-(>X8jy4^H+-EKy~+o(4i^%-ycvG@LO8mjE(o%`S5o%_F;;jiz1@ajZ`@3UU+AH0V(9|0dZChuF54;Pj9v*u$%_Da80zkk5T!Rz;x=EEgFY3}DA0k8ezOTo7sFZV;gEdKllW2(COSlQds?)3NiTjjui==HafENS117xM5S@VdRzysiCDNd3f<x=EZ7^Ez_*XU=<^>uGppiL>&wyq|SH6MT39o=1!$OkR&WG#}OecVv8_`55?cW*J{-KC(6<*BAX>Ck}YsPu9G(PI${Gr{;Bk+ljN{baTJ>G4N)5T@Mi>PHg+1&Hd^@^JYDScEH~_Ut5oBc6t57;PrUW<n_4EsW<R?oamGX<5@kf(Yzk#>T!)zPK<N)xW?r5xW<XE$G>KL%^UGGA5Sr^7sksmBfgFC+9UM?-mIUf9`_mbp!rx<ske|mF0M-y_h+O{L8;FV?#g|Leu(Dd;NxqhU*Yf_&P#o!_4<c83Lo77|E8;DT(Y)1&%1`+E5q|GkweRvkGxio=Z)iytfE}rHp688M)xOI$ooh0&iEbgAI+QnF(;1Ef3s(nljBBzl=n=tr857ps;KxI<9f}T<9f}T<9f}T<9f}T<9f}T<9a8KF|K#~&2fD*l;_xPp7#!Y8{qm6y;Vf~oAj6VeQJ^aXnsEYhVXjcL%%md;LY*4=5_t+_lD-pc>~QyjClqpzMfCOb72|f(eF3Q@Yl~{_`d>jT=bJ8NtH{u`H1chR~9}#@p^f#A7kE3^XB|m47@r2rg?LoP4nh_n&!><G|ijyX^y`+pEmd!^D$$-OY^$k^n91ehxNP`cpJQKrySm#uLJMY|2A)Yb6(CVr#X*zt+muovh<VVGi2Ug^S17XW8FmaA*>gK(9d-I!R!8*<B#=%nBlM25p+LR^G^S8mbW}k{}Ag4@n#Lg|LLO=zi8{5v<_vxJMSq@Py9p1j|CFbksWC>p4Thl4-W7;SNwY65~Qt?wV97@cp&AO@K_!`?!f=Jp5nu|G9R5=tT6j+o?XUWKYDzjd1w9#<A^YLbNr%tb3CGXbKIeMbKK#?H^v=Kd}G{UgEz+unm5M_nm5M_P8?&r;P@Nk1;^hQFF3q0UeLVR|Bn}(B|Pq1y`H7{FzQ*aXK6l)buoS4YTn+C^)fv!)A5gH_l~E)>-DV2Ij_IIZ=-s>OvlmZh4r$?f(6_TgwH=A_tmaj{636y$tm*$Cu;C`B%J12G1h;lm3E^^K5nn$Unh#+jWngCJ|}Yf5*{#3o`>H)Ek@dUX#mHur;g&|TJ_pUc{dD|{&wQrf}Ag90N>Y<t_3(wWM>DN$A7I?VY!Y)<-87ct?cIG(^BMltUSD;n~&vrLEe)EE_nRyF&mh-@?Q7&N74=L%GYsQVzQeLwVuno{YOO)AM5jm_;1PSi633RRs3(&_3&2T^xfG1-bqiKaPNxD+x=vnJC^hl_k&^!{*?He=J2>C3O?SkhWPKx#r}4qi?U92`xB{$ilt=!OY=)cOFewIu!@_vMs|~O9y*Zh=HpwQ7rydeGQI<EXILfW`JsI!Hy`P^PxuR1AAR#Y^U?FYr93anJWl)#;p2<*NqPP%%H^>xTXMcN+VOeCUreg%=Iu1k2|v6s`^U1ZFUaRrH6ruUX_w0S{=Rk0$EH@7`l)+O#)Dr9A8j~|`Eb+GGQW2_FZ1?_n=*gZyR`HhN)`xlzB-nycef2bpng#-U!y0vT&Y{i^LXaq<D5Tj-U3_?FF!5*d*=Pl@Bg=h%v<@#N%?>7A?F1?l6R@_?MCr=MGvjY&-{%}!Z*q)^QGWphnESTdWn>OeLdl8Rg&_IZz1-J>A2m9U7IcI-D%&c;O67t<G;Kh{oxUR@_vfQxNqdS*tV*In~#DI)tV&pnQeD6A73c<RW$FSDsDbB6!%raL65(+QSPhQP`R(dZG;cEmHWp|oF?mnDTsgMcd5@gMdki!j`#`dq<?;7cO^F;-Yk5y-TcaK-tKln;vD!|#!(q|FdtjBQp&SH?q@sCMu~HEyWF>fi^=?H!;#`2LqB0}0qG~~UZ0cs<9H9u%gWa`vP*dTWJkGP*RoV|^VZC<!Y}FR@sED{uH2sshs$#TKDH?;{_iiA_sOU5pKw{~?fz1EPi82R)vr8Odhp}LKb9Dk_2v@Q`To`SL-^LBWIsNZdPW5|ADwtbu6xeu$$os~@)8+u^i0XZ=`Sb9dp@|ZG?ypu@l33Z`f+%pel-6`{iGG%PFODfBjmZTpFW$`@4P|=ug}X$EdChhTQErK=j;Xcw^IurX}C%F1N~)v`c5(N{{-c~BjtDasVILaT-D86Ti(U<J3`8TTlnx|xxV2oa(&|&a|D?mDeun^>RIy<@VcHunQ{beAAil8{<b=<?Q`7d9pTOMa(LssG;f|)MAe(^Q*U;n@Mb;Jb+LV}i*4}wI!0gJ%KNq=1+wye6|0kj?<-r~4;<gTAMy%s-fs?X+;5sU?>D;7{mNtV?&pQ$_&hIe-nlO7IpzGub4t%O+va;_Qxdm(@sIj(J%lPZlzF7GR!)xFW*xt;LV+bk__*r5!N)b;8}=^Y&G$?Uy!jr}yjgFWf8;scjrd0S>3z$7#`~7u&+KQspXq(h=i~GK=Quv^e=fiI{!bC!Y+s^n5XWebsQqGppZ1Q+;nUu6T%*0C_LR@lr=8`vMmtOGHRtzf$K`r>+wo|IHF>%G*H6iHPo5(CVdfuaK61RS`2XEBAN#9*1;;n~6>;!pKO~fJn)&Ek-K758@8kEot@<;3K1M%B^JYIMQs|W@Ie&rXQvc&q|3dwxc<8kd`!AR!<C=s3_rpR}&I*4jlRS5&XIdOj_3OAiM!$~wfqY(OKd}3L@xQfE;!mt9?PB0G^LC%qGOn5Sv&^%o{wK%r>6fy<(J!_0_hH^TG*{LWXD`pr`G4KYe01tk^e0Ei`Ktaf=QsMp)PH7wqyJ3(Z9c9~Kb-x{emHo){y&$)r~l98G5Y_uj$@23XgtFH#&{$K-W<Qsc!%TojN_!<A05YWexGq1AJ1nT$N7E6ah%_09LIh><2Wv#&p3{c=QEDu^D@S9p(SVKyoU6U`!=2`$myL67LmARc${lr$RYi)v@>{~J6!sV%okm&ChyJjYlP2xN7m*0mgjk;NaKUdTd`!mZ>>OcnU89jfye97+LO6m2p`DI*CX;^OmXIOjgx(AvERA9h<*Pq^VaQ4vLAKlO4)C*{~XUtg{)`geKNO;jPvu1D9L`$Y?gMXN>;fZclVUy<K>(s^UO2r$UH#8=gh}1mf~`TGtQ9xR0EEQf8VBDp4h&DTn>9#N@?~VTu8=u4~Fu*g#Gk<=Is)t<T-k8iHx@k&ML$H#ypJXZDSrr^ATen#_{)=hvED_^Dvy>XC8*j;WH1z`Hgv)(B|0^$C#JXeAt+m)4XlW%W2-6m(#pu%*$!sZ(fd%=QA(I@qOmyIKR)loRs^~c{%p;nU`aKpLsdvedgud^{MCO!n%Hpc~Q-q^P-VUUkjhQ7~i+CA6CkI@!k6p=L=b<juyKp<K%P$%Sw5=%Kd!p2kw7H#%vcp;Y*oMJF-&dHS&%q$Jcl4U}-m>%$th%_@D{Q$8L<2`LX6j_<4&|{)c(Hb_Vgkn~<B!6Rz+Sr_Vdf^TwfdtK|9YHIw<+ueIg5sP^|EUdK6Iq&)jCmU)a={y-wdp?PesH=p@-cfGmi+c~b!d^`L5%(t_j&wM-Am(P4V`}xebbNP(<cKgIKiF53-yq5}A{(;-m=zb|@!WYv1K07%B>%rF~zR&syr~9mra9p2t5I65$H{tX5Ss!8BXMM!OKkkiVu8+{V568!PQ>a#(YHnVyPnmpFuS5MgxulzS)|*Cp{hf8~zYKr9-ZaYa*Xz``#XoM8GyI3}wC={X&w3o&#(EsB>$$Isd%e$7Z@V6@OS0{=F3IOv_tAApE|1T;B$vl$UDADAy)GFBZ?2QZR~8k2tn=#YLhG}9K3Fd{dF>xTy=mTA{~hV|*L?K0;jh<!M;Y<;x<9UO2)vE*=<7x6;OrN#&gHS2$~w5_&Gm6wPj}a|dtKgh9bN14p6j^E>u;{hho74y{IUD|-m^P=C-2GpQ>FedjgjZQ?xFyn#|iMgzvlOOykLaSD`NjB=WFbn(tOz1H>G)V-<0OfeN&n@_f0wRjeS#2d}H5KO!LORsYiJ1o6@|wZ%Xs#zA1+{_DyNt+&889NA^v%{#X2qKEwMo)OcC?qsN0uT)rAZxqXcNDD&^M4}{C_v!6uH=h6KnZ2Rmd;o}<nNoXGn`)~K|W3j>8KKr#euFrlg_Vd}V#eP2fwb;*RUzVG9@3WHge00AS+dliXIKR)nEH`h)_uH?<em?uPIIhorEso=}UyJM0XTKJg+h@O)n|JTm;<!Hhwb=IAuf_G|vtNtL>9b$U&Aaz&v7gU=EspQAU(3zA_iOR>^4YJ&_2aW&i_7h^UyJ>G_G`I$y<aP=k8A8pjCW}u=UeO;kIU>`i*j@Ru3M!%#y-^;c)xwl9LHy$vxj%>bLQ*lv(K5&(`TPE=l9v?%=vxxIkTV7K4*^Ov(K6H`|NY(`rZ8KK4&hU&pv1N_u1#n{yzJh+0SP`vz-5<`<dC#XFoIh`|M|C-e*5E`}yo=W<Q_(%x>NpH|^LV@e`KHyn5mSo_CH0K9O=B7$)QTwdtMj4mgg_cM5zReZEuRI6mJgux)&&K;K7jIefmG;Nu$KP0;rjoZsiW3=fa~hF!g{lxO^M8OO!1%6k8$SH$1vI~O+}sw?}iOkRKgLf_GNj_dmF#>3ac_j=&X?{4UOB|d+j@2B{>`g}jdywCSjd_14;r`X@;J1O=vzLSdR@)+NF(RX1S-{*TV_A|a0qwmhxHoiNv!TWv3$MJo><MZ&Y@A%mE`HqiypYQnC_W6#F>tXYw-|;c;^Bo`CKHuwcexL94xcolf>$!R7Ih}Dt;`@9r$^JgyOR}Hwy<`Nu`8_6mzsdFG^BpMr`Fsb;em>uUx_RCH()Xua4r3god2>9Xd2>8v@)5(|95*@s#<<DxH^xnlzcFsIE1Z{lXgZ1ez0t;<xZi8{xF_Wwk)6LEj7|>7y2VH7DzWzY?%2({zf*Q!7x(wbTt4%A<SoMceNXMVUas${J=e?iJ+<e0>3NCI(@T6~{=ww+_0qgKFQIvJ{z3ER{Db3f%s)8(#{7eA99Q2D;e-O>e`deTv%Pqn*QLS(%Sb)n-z?vSZAc~Sng^5Ry7+v*&*?tj?{hhPzTanm<NJL(+E(J1pU?M6yir*>uhQM6JgJKFIM@23q^wgn7v4%KBIDmoS!JDZRaol3*c|!2g7MjeZ_!t-qtEXZFmL`|LBarub7M8fiLK4Y-|<DW3m^YIJs&q*BM<ZR`w8st^Scx5=kvQ0d_14uo#6aFzdOOlZTIN!PH?^X{O$zD_4(Zi_VfAO36AgcyAy2t{JsPq*XQ>o<am$%zJ#0C@9oIV?Q-1wOSzsy(+_jIZwGeB{W<OluII@A4&wI#c6!g(_4_Iu*XQ?D*!KB-6^`%o`zm}LeSTkskLUCIDxCl5qrb1h@r~bCiEG~H_j5eF>-Tdwzt8XI@Ns>9KZo=C{C*CX-{<#p_`3M~eh$a=`TZQWeSSZO<M{l34#)NR{T%i)em^I)^@yBrtKxh=SgX#+e#H9cgx}a+zJJN`hkWncLU=3GU)q<uUojsY0KRHNd2fu_Fa8^Zk6x`M?}z-Q<ooomgpYR^Cih#Qn0(LP{=D38=RcPBKyUdS8@s>o@nU~Vd-qs&`F)#_;3rEtV?+Ov{_R-dqpvNIaz3~$^I)@u5BJI}zwgxWqV&&KUy|eISt!rNpU=y_kxzxUzm(^~E;(7&uS;E)__?adclw{bE$g$5g^w>BDetQVZ_0jvy~10?<oBjxo7Ty`ntkw(wUha)Yis5AK@JNa?y^_-0>axTugLW+xkY}5D&f5BOS~w2e7?j9pFAu3Nxlbv_m0%t$}{r4)?3*sv;E69DbL1wwK@J8;p2_&$#tJxhxzD&?97KU=8*QH+${OsfK|dr2X>O<-hWBHqu(Zc?8|rLemMAo_)pHsytP^SC$Xdye$Paf3LhUV{_(?&<-3wXxg^e7@wdNgDD$HAg^%|V|Il-FW&c~Le9YUwWRv@C$+Pm^SB-o)ua0tFgN91I)r9}h@8vp9+KKOxgb&|4B=vS}yYz=sz^_~^_fPU*d|#bk$~kbWoY(bDvVWtg@S%NoCC=83@_oqUo>Fgn<MMl7Po(hv#mFxsn2*$y{paC%`!jQSqf;bKn%DXF#3Cay@xG4Gj{Op+K?5oOx^HE_OU3h2&v$3a?~k20oR9st-xGc%p6faz<@wzK{^&%x|3By^*Xy|O_UI(JE~7e&f2RB5Kc~I;w>iYmqg6`y*rN7QKlAoWdtFobc<JR*Ki^Il|5n1=v!y)I;iKexfAFzi(#do5^i+8dOcg%#-HQ@uRwnsfthZ2}{L*iUk54bhJ@uc&?-7yvr^aa6H+4h!$duCZT<5}m$dXnSwlB64|NGy{^V>l9@Q<D4ek*=e_<8~HUwKLHw;NB$ewZf0hd0Ud7)ca9+7f*1h&<Otv&#Oi6~f0h?3L^I?=boOh4tW<Nu1ENp|bB~Gvd5?UHB72WdF&}rJ0ZH8o>J~La!dU%D+dK=_&C~_*LGMbN9%;#9PA07k(!1$^3hTKU!PPYnQBF#Ks@vb|L;>Jt@zDsdB!X3-CVRP=%MONWDyv_j#jsyzUw9{f_wCYotEczb)5sjPQ~Ea(&}<7s_=!|FInR`7?4qEWa(kThU^x@B=SMJN4@wIp15SnYV7`k^8OOTk^fYC+C=t9#|mf)lc?G#s|g4Ka@*;Cv9)F>>Phd(PXv{w3Fv9@>hEHdr(gJYIo&+E7*Y7&BKvu!Vm5u@3(7}_<4+GtjD~SeT`h-@waaAI(X;{=ELol%Xjx9R{Y89#TyTb|MTS~{<2P7o_MJiRhjQROs;RUZV8-k-&E#fy*A2y^5*`#ds=yZrLje&3AqxhSr$oJE1T7?r|TygiKIWR{ePlyV5R@7pJ=R*RKCjp-)}Ug`$LtXR?xDZR`RpLzbNS#6x}H(_$?)GD0vfl0q`rzXReZ0q2~do30PKYC1rx5O9usaP;y<Rw}-w4+)U}}N}57f1FoqgMM(|l=D?4sn13mq7Wz*YZU(y<Vh~OYNS<`iX@Q#~?rrEhz}0c=YS1-+|EDCA%6At!BXCQqLnSSsp9ZG;qqUOS(5-;~L7u;%TL4o$ikluf18{2`yA||Z;95Aw)6lhn>nUlgq!Dx{;C4#tQ=LOM2F|XIkxI$q&<`xZosd5vAUYTjoK;B<_>;~KO!+8(d+2tE-x$Yh1YHk!l9E|Uo`-%Jc(#(~l+1yi0{k-kZbAPJ{2TK83Oxsy@=iv6(h=agN}f^D5V`|!8zps=bcAjI98l+yP04?j=q$h;kpDmE0QfBM&kX$p@V^#0Nlemh5WfMA*ATic@Lu(7oK*4|^eN!eN<LR|0s0Hz!b++rDFt2Ah4;eVix`B9AWu=~QovszZZdRb;FCD^Dd-Ep)s>V`QUkgq@Rv%?DA@;n7WkZ!{YuV59{{e3Jk_B00hdJF;?Tu__v6?Hplbl1!7<K4p9em!<ZC5+pg#eQDfv{%3Fsrh1(g&~QVzNjFy$+Yyre4v=Z9Y*=z_qN5Vst34EPAjaRT}{a8${XAblbxdLi&)C5x0Shh7Ry={9^w*9EQ(zdF#1fhqnn#3ubN@G&Kal<b1u0lZtuP9;a74+AGDDX%01oey{i>|M}Fz?7aBKBS)nehP6bK<@@VjB*@>J_dY7JsT&L3<!$u8x(v<;iF2r1x5D^3O=UrVI{qSqPqtLAA;{;=<dMB;Cm9fFK}n2f5LG|p8-Cg^aLD}bWh+NN_Nq+92DI&DEL!_KT*;oD7ta*A>Ij_bfci)-InBOhP>oUxGCZ`hu#BxQ0XH|x&%e{2ns%-@F^v|gQEKd1%IvZS4zS`(OrXr4<g1_&|QJQhVOCcKEVADw?Fi0;1f9J5$GPkKPvfF$@rk?(LurADExzxQ9;q;f`YFod|t`$py<It!50)B0*>@x;4AR`7J4-BIK&+f{iF5pxOAM$(9Z&Yq2zNVt%IUl1qFYm@Rv$j21P#;6uejA7VstAD)=yeo1nxay$`WJLyQ=73h;Lp%@<kLn4sv9LBZz~zNlnSQ1sBC;HwIMuVh3}^w^-_bMQS2JrMYkl3|EVdL-~z<R1h59q?7ez6d=O_ytN=@;3B*-~|**$s*|Kz%MD;s$?Sco4_y9^P}Wr=r@3WQf=ioN`9vPTTpDm-v<N}mo_N2#-v||Cf^1woA5jEdmWf`N`mV5A}*y7-VghA<jasCey;<!gCF^~LrjX-K0!43wnv_>;3^=W_NxFP+y$6)Q*d2fHt7z)q?3@|9cf*FbsFhPz@)zlN_sb>bpY0Bqz?uKlWrT7^iJ@p1gz6Y*8?V<DJbcc;X^`Lr;*M8O!`JZ(k~*7<f1E$^!0#X(mw<weIk4^0AB}Bu`VfH5xO$ULS-VZC3Gi9H*lSyyFt2x>j>Q)(iL0_=&q0ya2cReaQxST56gQIHc5SOd7#}kol72YnW1w7>$Gp7<AH}bGwdHwSKk7Y{tEhY7mmXwO?eNw?7h&3fGIsad`JlI1D_jdq_Y602hIqb2><lp5+Q_t4Tw$$On#L188mT(Nt4et=$iq-I&Eh_xF3~#hqRl(zrx-LP25VCy%NWzSf41_4f_+E?>=yQVedv7`LBZB3A_q;B{1nl)ZbV4L>VQ`p}!9bZVucI`WxW3O1@S2J0;CvYfQSV($6G_O}K!1R~Dvr6nZ@HXyDhO7Xpt$+EifD)1co0o(8-azT{T`IzMm$;KI;_fC~eU10ILtS5|eAtfX{6FzF)DC4q|o7gdr|<;jCQ=`FD}PDYGeun8AYy0elcO6dQfDB{ATb1I+gunCt}y04N=N}jO9)|hkw<&zgS;p$4NDk%d@ItjWQa1wBNDx1oe7kTnnVryI#G4jJE{END_A1ZlXNgzRNjY(%!l8_)a;ae)t?@I0k1e5+7`Y!O_!2c-upUU$@Q1aXjimmbQi1Bz(Y{GYx{H5eyVA83AqOG7{62d_x50vBxN}m5<Yy1~t<O+&S_)n#`DtVRO2?=6rOgbkW3pU{=Et+PNzD7ax9mYT=qW>`w{fhbMdyGLpWi0e`=(mBV122Lv`8^4p5BN#og3ux0g1{4iC*b(h@1TAQ^&zN_@G~&=BYp-){Q$BFQ`<q9xC#jm`xg~lZA%5T{VgC((GE358{ZL<gmx<l?Rsa}gj+(l1tw{WHnT0-=89-1Goc+OO!^Y+AAm^+zXn}D_z-^un}qP^uu12J-V01ZI1BV{U=qR^gAd=i8PRSKP6xdTn1t|6aEpL%0#n;iTS-?Xb(PctChndkHsKq<#3fl`6MhUh37B*OFzHm#0pL`?X`n6OG{7UFgTNz!Z$hUAz6o3~Ao}URL)-*5={kXjct32?_kl?WcY^K~c!-}2h)ueO3x{Bn?(V{cV3Y3S!i8az9_7L{VUv!yunn8qhnbeN5rk*Jo(a4idK>UIm1nz>9ZI$W6BmW8@iN%+fQfq*HsJwE`YGuPOuE04=V5D1dI~V<xk_GvO_<uCw3f6(gqK=klMpTj-4(c!@+qaHN<eTi*rk9=Ko<ulA8NO90#|`eLO2I>Zr~b9msL_NAh;szvcOM4R{$m-YUc_7SA$JLI5%`YU~03nSki70{>T!Wgz!_)eSm+X`%K9n0l}$*V&4b;A9NaE@<~7&_Z#w&O+xryP;|DSU~0313DRy6o(!9W@O5zS15+E6K0(?c!t-F05dI6?HsIUpSPzu^84#Qh6#D`2f6xJ7^7$9-*KOqc7i}5g`_S2gf~nnj32g`A7h%5yycPOm;5O*@QD3qR`hsQAAAAN}Gw9~P&C!n}t^1g5fvMlw7Ml8<Z&}jMd(9F&4)!SELcpY{-?tsl*;43bz)OMW0h4|U`Xv{h3!C(FE<6SH6g-2^LHgrarRSX90q^2@-sZyZ;#nuX5cpN#7lB{Ib4+?N@GHR2Ll1D_ez5zibKat)G;~H6&Iy|^^<BvhD=DSqJ?IR;?*ZokCQZ+9Po>K!Sqq&Rcr9>lVAAwV4p4fHl8VroTsRkO!qgWfdjmaJN+v<4P7pi^_#QB6dd4;@d5QXj(5Vt0;{U;Z34Kelw<wuOeM;!Z5+33QuxFyLNcKAFHz=6_ohCu>4B-2~r0JQV`623`(LB=|cxJ{z2#0`4Q-3X+icwR^6VOk)a21zLItRF_unA{`O*%7hRp7^gNmoans=(F3=K)W4ZQ$BCR&}J;16Lh52kbh~^?-9g=Yq};Tn}-YK!<>v06z&#x-s%no`%p(fExm9pN2R_LvRg%8-ULboG(G@IV<XwbPeE|z*WF!hfR_Uz6x+g=u9r01$H&yWaO;|OgcBxh_3}MJFxbx3%^>x+Q$ZGgRccXCpgl1UFnSwCpT~b=qFvcF>K0HANlGdP2<L}ZN#q+X@Io6!1aOi!5*!i<B3WpDVY!uoA6-Z2@vAOLkPd1WC;8wfG2Jogz$7=($kcTfd3HSL9pAvCVn7zvPZ(!m~>0X2;^&rw3fg_VG|w>y9v_Czai3Ef^P_1AO7vY)dwb@2H+ZiZwS7Ti>rtH4S+Q_3_RiXup0nt?pg5dalX&OrxmzX;M;?51dgON(i#D4Zjh@kTce)Ir!nkCI0tP%1E0pgIuGF#@F^}o!lMzRDbkyuj<wwkeocWJ1Cvi%=pn#ufm^_*EpQ9)6Tmk|tfok74o&I3A^Lvo4LuG%WOo7Xg1o(v-V<DJ7w!n3F5t9Hx&zA59JnKV!oXpd59!X34oFKuT4!L=y`aOuDbS-4do0qzz`ekagH3uG@L1rf$WOjwAia=223q@&JrQ~;@Np%Zm26RR44AkJu#ZC@MjGi4fj<By?i~Cs03U{Z2{!R(kVpHU0p19n?6c74z-x};oCkj%9O19wcNX|8(mw)E+y>Z$Pa^#i@Yk?6xYAD|{fLtHVQahr_GaMsQFohxNj?U*3HW{F-vms0HPSu?UJoI>0(v<x<vogg?}1+p{5EV#I|cqIFma#4Z#D30q^(2V_rR|MCcOk{ml5j-@G01rU>^a#0DCR+t^<Atb`0F7z-wWD0qzuV4E9ynrx5ol@Im-|0q!6$={-o>gZMG{96<U3q#Z=eD@ebBH0}E({H_2Kw+k`%fZGL3aW2C50`O(v<F2&R$afJ~bGyKk?+K(|1U?OZ3vALK1D^ms4I#W9cs=5hUIV-fcrEx9u-D)ktp&H(#V<x0@pON^0ZjT$2;rGZUPIcO$hQLAJFs6v8u`uuPu%Okq?fq-W<k#YejRDEz)_ru(35~?K+l2@rgz*l*o0>TPeaUE;AVrH4ov!G_{;`=8T<?27og0qBTd_+-v&p%bD$>y&jFqZU-Fv|JqLIJ^xM#L;IHlF&@*uj=0g+TTJ`y^sd3NWO6~;3Cj3)Sc(U)nZUs!5_@9tYc5x-eloSCbT@+kl*d&F(7Xe=oxFFI>C@HC=G%)E>;L5=!c?x`K@a2KaBW)JuL1-Rj7RGje0ux7bDKo$mHyfJx+0ZoSvL55ZS-{$N9r*RI$#)KfFwNQg2*33hd#(ew+LiA|VB+2bHwX4?aC5;Wz@7tcE;yP8nhTv1JZW0z*b1BQ$G}^Gb?iT36MxlJmaEVoyUKkP{(pe~0~}#mOZfxoX%i&RRp6`eO$#6LCHw<o6DICo;50}}3+_JfeT>`JS+X`pYh8p%(;Nh?kCg$p4)YQ;Ke54*G~&v`Zv%WNeW3Nw9ta_x=083_9!jS*IKm&mhtexS24HSv1JZ^;1|t0fqz#8`Kzb75ZG?P)bXvEgw2i=|^Fx2+!hK*9?hSh*V)TYQ1%5b=nGAk7a5DHx;L9OTZ={ujWC5QH-^alxyYS=idmKI$U3MPmikLfk9P>z;&jg#+T%(rEd6QlW%xkgWNV+18xaHso7j@a);77U`F!7W=1b7J2iKDzLfmb4pxRT(>uQ+0nP7B-(zEyy$Ae|%|{ECCuHtF=xIbAp-Y{I2s6D|q63b5w-gQw#ULV6Y8lHgam>>kK72v~Dlz?1K4qz?k_0lfv7e5g)VgQq#kE#OMKcv?@-1DklVX{~|Q9Nx7=2-7-xC2+-{iR%oXW#CB&7l#j}cY!VfO#EQvc^90vS0L{)aM~tKYa(3`rzmtfVB#wyPZx079*Q`F!D)LHVy*zEZPKNnX?;awnxm}({2pw=-C+*})?C=dmjG7+e0P+kge$!i(uhw4mk7QD&M6V;MRD$lkPPr6F1w4*fwV;MdYy>Yd^TGmgg1dFyCO7kec|&VcoM=D;6v&CpvwajKLU9+gVXl=$onBUZIh-oseXu40s0AG;;SN0KXBT97I8*^)AoAAd>@>)NtcDD^(~EQPQ4oNTG)hp!G0E4b3I*rS#V{+_d;39y3)%ajrgqKvVt#*bIOYJ3OM(ykj(HSF0YHvjkK)b$)>e4T0@%xAx!&7h$lNWc;Y?;o(euSa2oKGz7hHtVB%N8ZwfeVPe<OV;IvJe*7!Ce&JAeV({ckbt{~4wq-%RE@~;G^?H3VqIyh~Uz7I|7g&JprO?VP)!kb{P1=idK7ym1`U%_ueS$=h;|AsW;{{i<8_+N2O{~-Ma&ix;7wEprNxC9q}4{3ynC!6-@JQtKTPtuctiT@jEB<~}QxCl7H|G4ZA;79s8F!7YW0(b?|iKD#JfTtmixVzxV?`Om!O>42&!IST0;LAuSp$!z|_cM5HlfDa^)|WI+1)DIfN2P-A&7jy6<7V(7w;4Pge-+X%1K$Kc&1HXtJga~;_Y!#WeF5pKfIotM37CASPF?{21k#AR=i+Jq)f2$PlTCZ1<_Besn)Ezi;!}Ym*@iUYUI9lq=(4xNkMv)_^O3#=cn#8DLEe{vUq%{n7HsmnjaZ~<?fftB<QoT$Bb_8&g81DAPj;(jfnc_ThaXX%N>^mVfYz#?-dfr#{YU#mENg7vk)sFVt4cGc_w!44&ebZG^D$<tW~q4(PEh@$hT=MXIcEJI94FqH'

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
