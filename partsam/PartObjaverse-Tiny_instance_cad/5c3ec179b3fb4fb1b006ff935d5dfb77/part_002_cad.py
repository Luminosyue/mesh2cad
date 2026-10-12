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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_002.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_002.stl', 'source_sha256': 'f1a3f490aa95b855a229bbb62548c798dda6f6024bf5a755295521f993b12239', 'input_faces': 926, 'input_vertices': 492, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-10.462234497070312, 74.87784576416016, -19.63945770263672], [-1.4648876190185547, 100.03697967529297, -5.0608062744140625]]}
GEOMETRY_BASE85 = 'c$}qtb$FE5_U<<c?vkJ>43=O)gWF(1gS!rd0L4l}kfMVHD-OkBa0o5X6c2=f;I5?*0)rJV#d|37+iSfq7tVd|ANRSJ^Q`Ax^RAt>*Irw`@7sI#G;8FW%+JEVeAe+kHHNrLSe8gS%g-7T5gGMuc*LL*0|x$Jvoa|!|32f~CauGowYOPAtPw#yA_j#=2358PRqa_ZsJK0-=Xa4&k=+J#{VuXcgz%x=`VERO{Gi_521c0Qg+nTpDQ+)Yq_};Q{r~Y_8i^t1NkNYR=i5zf90pxQU+8ad>>t2gamrgi&I^>^p14COKl~)hKP_Kaep|QJf}dLq<wI&0(((%zfG=GU<(oc+pJr2(cb%;RzRz6s<4Ej|db4k7t$gFF`rEOotD=3yBKRNFyMXewI>67IU0U8MFiHJ8Ha183^atVRpAf{Ex~lT-+o5fhkKPae%}XkJZgvA-sEzt@F3PXGl{6B3!jm8^x9J=F-9qMJQ>P-zcg_tzEdvl|`dGwy@2R5OQ5*clT_}I?n)2SiS0T<_4*cGELD6$PHQNQh&Y!`1Lnoo$JvZ`cI}?wgo(|dJ=danCfBWqN%Dc|T!%w;nTCeM4JmR@h5PV!JZI?A-GyF#u)%IGI5sxEb0sOQ-3;yG@{2JfbIk0>E+aaG-?8;x8rM%rQJ=%NUuH{`1CZhbD*T`qZ<7nq@@SYse@Lwl~#_3)%M0slm^W1w}QT;t|F!-hewO;GoDb0f?eH7|FnHzjm3eAH%umjrF_FXIG^Y7Al9H&}<KmHT)R$v4C`~cqbYfaQ!^@i5#SY8F?#}`80CT7ra<q9ba{!D-M?^@Fb<0f|*_?aIE|9QqBe!s$qv*{Sb(<?^fw4U0*`({8M{_<!%?w0|`|JhmaU*u7s`puFJ`Mj_J`TWpB%R9zoKz=$rgrB-8^J;uoAE4h_%>;j_w#MU{e@l7m;v@La*INB}|4anGaSHO;bUgn4?H}L^l>ndKSL1Q!JfXb(Ne8s6Vl~83o%t>mh&(j))Bbg=*#bY;F1FP2ldozX9Piemp78nbv*{e>-QYFKdyhWS@~(p?v|e|;MJT`BhWJ0mX?aKYd5EXcIJEaeH65ScInyy7^SIEz{*N$jM^1&Gi+fRi)Pirc+()PK&eZi0&&iDVdrv#~pPdqZmIfjJ-sXt2!(POh^cL&R!ulwm>L|(|>Re2J&kF^=uRQYEutqK|-?<ie-_@93XDVqvowusN|7ZvJwVyN(o}%DAbGsm)+jr~uv?rBAyl<;uKAzd3^}7EmjedDH9C7x>I_9-XqF?@5gnSm?iS;wAIPx$*E%I<D3giFRAolwl^lwNE@_9E9<<D-ze7WCB>vhC}_cUC9I0HUuz0QDFn16|Dz?aR2c@+N$c^y^@{OJOCUOc#maoWm4e~sO*^*W-!TkcB8=bA=-${)E5Ka1|7U0I{Fygd}Wt7%%44||Xk@f}y*={E=dodq?1m){Z8dp$qe)!{PM)g1|#uY=bipAl0rzgp}^JcIp_w-doy-fF%O<vRtUUH7KzxOHv+0eQ%q74fVZuJPMPM4|kk8i;>IBeW-}AL7Y20CBFmoJW7J$9mvOTn#=fB0zut6Au5kZh~($Tifg1<3xG)cErEMAN_R~>wzo#V$?e#9PRy~KAt~shGATJA7P!@Sq|+DKaTjV&RVa1V=&^Z_8a(wlUUcnIB$M#i1A!L0eM(who1~Sm@h3#Xn#2)z`O1&M4TmuV_s~|jq<5CV;pWST3qurKNsTca1e3kt)#rmkrVY+D-XWwOy%wUK4SdF1fXBs1C{su^d9wRn2CO$)(-8>{SM=<Y%b*I-5&IBm$&fKuN?dgNr0cGe`6gg(FA;>Y{42&&m@dTpX_K?s$7}}`{RqKcS>HgE8-_SkKP_v-qrO6##OpNjmJ}YkMh>wWbiYo5Zc>k3(9|p2Y-0H_OIs-=Bs<%3*@2jNcH22+Xz3G=HdDBZ!-89v=Z^G>I6S^dTaddx0BG`r1FR-3ctNaN1|O7IDU?2MEt3TAa6CEv{1hPHOw#f0K}R12*zi|WI8^r1ufvuzc1>ovPbK6zHWke{F5-QN<G6k-`p7d;~$adVmGi3wyTRcZ?}j4MkRHfw=PykoOh;z|E6qiZP&dJ#Pd84+7(<M&+(D@k+=0J5l^vof$H~F4)DVg5YMj8SpRotLOfSnfj=IN^*Q9d=G)!j7~;J49P4v~6Utka>Ho03l;&&7A(Zcq@#(0UAN=un<(<<?EAQD`0Q_L^R=*p_^Tzq=-+6s9`gvs({QG`DK09|o`A09byu*!pt)>l7zFrN)nW>cWu92b2I}#!>e#YL#`ZKc-#^cb9m@g-%V*FnZ0DtN|_`e(T@89X)x#OpTch%6}_K7bQT}8`a9eDmi{Wxd6fW7n2=&xf#a%j2l$uCBGtr3XdGx`qv7rcsod{|t6TQ>0an*pe|`V;M6&!vl~*EbCL>|Pal=y^_g&(XipkKM=W_;Fju!5@xCoPln{Is6yoV`nMUdnFgf@s(NN7oJ1E+-s)&V#SUHKM2oXt4l|X$C-RE;%q(<{dF!H&(W#<ly?M=27jtX3H1}-h5kPx4}LuYwfy9gX!im;{I?#j{=MajBK~d<(U0Xiz;Dy^z+Cf@=MLfM$F$^|Tu}d>HU1cH(?4lGyuD8$o}U7=yyL<L@cY_e{N$^T^4F#!f78O?ze+94-;U#z_k`m6%L;bsdy)NIkn)aUPV~#omg>j84!qOn2-<r#4f^XzHuxWP0?(KBb1)y*r^fr;(qqWKHwg1$#V0(k-nHZN=!(u$?~F^}yNpBpMcQbdUB7Ks-nk?<;_+@Rt-t@+q`c#O5a#JWTa<Tw*r2@CIRyF12;Q174E)sBi055C?JwuW0r0agBm4}Cg`WmJQ18&Hs5jGg<vqVNQ{KH}6#Pfwea@b|5&X|7ihhsmgn4+Qvhv<J|Ka=RD$R>MV_EPIFQWXhvdGuV63D|%U-(bHP3v{f&#Sy=b{)i-IS%m@%L6|lx$ykTRttGf$ci}sTm%08BRpR&r3SxsA)Xg6)?xhr>4W%(o<qGY>S0`s`K0T#E609}!^=Jx5AEM8Z+#byc|9x;@uvXqn$-{Eyx<M+{r&+z?JdeztA_ay`Wk%I{D^0CyvAc6^GbQ|$sTBLQY)^{+rVcp0srIM=(=k6*?{NCn)m46<(n~1a;<{@)(z3F6bF>I4;`nx!|lO%PW*^<>2fEOFU|d#k}2VTZdJ5*W;DiUbUz)Ro)rb*CucLn`Thv}XU?a*y${Blr@}^z!!;juo_PYi@L#(k^3(1LzDr8%LOgq3msCFJsPYac*N5E)u<n&Opu98hw`f;lYvjjw8vKORMERnv5qIV(C?C@weAUzX+;^lK1ir&_Jdb?VBF_2)mG`c1f$^XDD8}LRyvkd3P~I987O20U{j2_5<IZE8zdwTgqnKOZuVTHj7S+Ie;K?Ms7w78C?}#9Lr=&cL@(rKD|7kb!`F9-n@~sh15aO}B_n;jW`M&3<R#xNriTn!o`*er$_8-AJQ`Cc>Yqgd4EZd6rpvgl}{#_f)>s{-Vw=b@Z{w-Kf%e!O2d$*$Bt!Gu0cePy$zOzqz<;x^sUGBUb{#V6gd`8;wJi0pv-$TI;_!-a;ehz_m6={ihmchS$?=1L9`UdmGFBacH4Wm)-U*qAYaW6clt`1h-J+c@4jKMr|p6?I-O)Hc?0soF(eZVKHj`j{gJf48wh-Vnar)yUVJogjB!4K#2ZsBUYZ~WU0`JXu#abBB`=U`HOv^N3IDc2j+>wZ)deiEyIAB}pgz4?%Trytg_p2hK9Z{<NACgA<S)uuPfzxf8`A2&e%uI`I=jmZlC)7zrG1yQe+Dg)wKTN!+M)a%Tj2K?wy_<uS8dB_6Z{k|#klN|NBI{ruBkL;nyr>i5@0jt$><vnwcB0ulH$Mdz_Q{~-1Vw`)Xuh;U9y!TN4cyq*G8vfmDZ=rl^tpC;<#$&&syrXS9uG>}6u0q!k&%jFXv!ns|eFss#%W~v%#W~E!f4AZNZVTpx<47dh<=Fy$F4h58*IwWouTkEa6ZJa$QLocyG58qP>u7{}o6SYLHZsoNRx{2~i1QxDLl5+q>yIduf5>^-Hwx_?)(8F**^hrzM*pUBqFvX9;`y?>Bl3K+J@R&!@!V^SIIlK9c^m5Wq(Qyz$VzB$WsD!I-(Zvvt^ocm%a2CA-XrCe_qN77^~^ZT^{O1=EFXk*KC~vj<Hi?N-nte6{{`@VW&Knb@kBpB{8`80eKa&5%2(&O>cBXE$b<6bFkc*hh9Pfjvm?&ojljnuZ>|mg$io?oH&+;*kKXlZkmm@DH><&S$n&(6=$95;R~rsO9&Y)<PgeF<LFB>Z{U^J|a}eu;XKofekJf>A=jx0+%qWBR=B#&=x1#ZW<+$Gj{n#W?d1o`WH;Vo1b540rld<6ay6gJp{pkq&eB^iTqhWzsU+4kl?MJYVS;6q{8Q@XgTje<X+^m52qB?uvXU$&tNsad?@19urnU3-AIK+P6xE1B!{)Tpae1rF;A6B4zikhf*5c<U#uoUrc!@A*$t&VuQ&IF&t=Sy0QPxtJp@Y58}7gzK_tS6%<D(|}982(q*g8%O0(5_=#_g01?Z=qw*FWb3}t>W_~R~X74e9rG9zTcL2Aph|*@SbpG1M*Y4IO-jh6YJQ|Yw_MVxB%jRa1nVJvlQPI(=(yo_TTZjGaBDhJ(7dpith`ne;A%4oo-}PfA#r2IC?+k(d;DU9rHfoJz?(-d~eiCRNgzZH{x6phWC=AS5dxJMSkyG!uwDDJt*IQ2A)R;Cg6EgWS#Q%;-~OEGB^(3FGW@>Z*{<Xuj?SbbG_3hfZxgYx{>>^ZYLXudNa3$pN%+Yam9{=|L|<c+kWihS<l)i?`g{QHefI2V@zY@A>Rn(?S35{=g!83;AdI}tlK-X;r*dxX60RZJ|Lc7@qX)R`^I1G-UEpLTNj?2p<d<P(H&9mj(V7<H*YBKNpleOzD%Y4?j3tpc}H80=RLd7FN?OoPqjF-tMpd%%Y|jidnYF2yvBOyh?=Lo^TywZr}5Q5jXQZXct-{Fd#ZT6XYTkOel9OSd)w{6e&gf_v@2}}#M$&X-t!~F5dZVTcyD}O0^@2*Rpnhpf)Rha1bpA!4MF)%`QazkG1OZ<82)ErpU|=E6z1Kr^x(5(MSGw2#P`C-|LFd)w;k8dRSt}kmdBO1UUB~?E(ra&KS6m{-EXnZ|2qr&V{Lb$d}}-AQJUhx_`OVd&rbv3r|ol{NABp!@Z-Y%faPBi{dl7b;yF4Qah58NdAh$Hc-K|b```%nDf*T{y#Ytz=XgB!2~YUL|A}{)cXeX$9=kIu_REW5+*&g#A<v_dq5R&T5&x+_(O*qJWL3Pn2jx>^AJSX*wesFIVJQD58v8-v$CUSc$i#JKIQ9n@Cn)d8coXBNQccubcenD+fXSHeudvVTnY37Wt0caUtV1s~pPtSO5YJ`o8@sBZzg&w)DQ|C)n&;Ya*oU--BhH%7@O>270MF|d-4SQ}E97lUCEZVUMl_@UBgos|TX1e2S|9v2oKIQ%Ep4xJbg=TSy5Wfb-D&K@bS#E?+gw6>FC<4krxr%Lnw3QPhApvwQ7sVhq->7$XLD+tgZt)2yIch^o}Y%|`~7kT<n3K%<e_n6jN7$7h$re3){{-mF|N8i%cA_cbXY%26vp^p8wdW@J+$}1N*xEzBO8?Wwv9zUI?rQ2>(fM(AN33Bt&MfbS}+QH>bc1OfTr4BYj0oW?R`3<A5ZVseslyB1%IhO`~>&Fd2pkG%DZRZLcd&ZjOSOLobbQa2YyCu$2rJiU&NVjJleJFzUIw-^>k)!hnM5L_$-W{>u%+(!7tG-_T~5<-v-`s;TiG}*BkRCeyQ@F6S=T&x#KwA6Ta;O|2I2fJ|-N)en`uD@Uw&Gtu24XbL34)<=t({Af9PXtPin)%Db*$f6V$P2>gI=;HO=3@Db1Op6}-eej&~oU2i^NKYeos_{rx+`O$%xrw=Y?Qp}MI{ZhFb&KDk^Ro?kyCgi_vX`CB|ol@R0^EBGkFFDQw`X?ywidu*9pLq)MkZiB=o})wf9i0ZxU)KWoc{m2+d{!Xhe>6&Y_kR+R=ToDx9>sP>oX$9m|1tw{zFE5|;ta>WjqCbu%<Em{;3udS;z@S}->vydfPWYYKY6!nyF8bRBK~E=k++{4;2dgl5%{-bez`g&pnQdq8P#8@zKDMv-a}lozg6B-sx<g#i?RPRK3sX{pFBsa<HY{q{o2agBR66m&3u7#vDwv?w~o9)y+cc3zHiP8KWqDeuN;Q<zR#k(w>aKotv2T|uKogVuQmhyHQ@pF4;!R_pKW+9Tam5N-jY7byBB8U`g|Vee19y-p#I{<p!}9!(T`QzDsNr8i~cH&ePq`UGt=werSl@r+hZ_(-i=n?UHt>{ydVbqLUDtXw+}xCKa=pB^K1@=pSRQDXTeC^&uNkjejNVDXOCVOZ~51xQ+v)x_>bG9^|}M|EARNB8S+rq!o29_O{?{{;P*n<S=@gpe_eTN5#9$}-B;t@z>BlWdk)4T4?WZ3{!jgb%DeZoAB#M|ycoY<c}Ll$d{3?ysO9z~Q{GkFjdi0{F|3C}AE(jsJBH%iu;@O_)AyIbKiPtD8&wL=onwcTcZGLBy=8YIo}FWqcP~4D_J*&=b9TWf<((bQBF_aAupgbKAIhJs3jZ^m80Sa(C~u{og7u+zPMmvgXso<vWB}^@W<AcMS3gdz_--5DE2^U(^R-ak(c=yB`TQmBMYMX7O3TOK9N9H%F3$PByQjRhxgpBO9Mrry>zr5Kk+LG{_3Xg?pIrNtcRLG#|2+oziChLhxd&lBHcv!*GmJyMnahHocN@>^TXmH8W(`B$TBO7I_eKZ&q>q9Bv{!HsV0d}u?K$FkU#lzn{ahjVS(yRty1f+d=Mzh%)cEi59>q5pZ{8QHQ)v9xb|Y`uyW+WDcMACTn^CWy51xZ3x`02tAN{g)8}BbwR^I#lV)#iJhx=6vE#<9EeK4+8|Alq_{<GwYc^4x74H4+y6Td6(yxk0b4mHGk{Ol7bf3PUV$#;A3oLzZPdC&Fn$lK)x`2Om<TzS{4VEEbW#{2rF@ydH^CL;fVUVPs@$e_HvC(lh9!~|-&9)Bm(dN(E@Z?S#R@3+r`fASmnfM7fq1};_J-I(Xm+jHajdtj3CmXr4u-mJtul`})Y|6UvAE40FVS<*{+=jH}zmoo>}f#`IoxAhV9@4x}LUvfFgS9$vf_{lK<-=_z<C~uz^h5p+13iGRFJ@CG%5RdZ$-sihd_EG!BhA6+Y5AXAJ1D}NFm*tD|A;*ns;Ggb8`O61zKj~uy<y{~1p#10a8`}z-*7J4(`f*WR-XkocytO+A@2&Y^J&E&I-o2tT+7)2OzO?t9rF^3Z)H`<t#zWRb<*h8Uke~M}cn*6(dFQZpDBq$)AmTW$yzBOB@S`T;c~o?x^7gfjz-QWr{_Vd6enziEJh^Zl=bGLZ@honIabBPT=Ecaeh{q4>p=)IptPdp%pk9BjKOMK?o<pI-pZ3e&%{c@9pOLuN6*lan@YcCb$lJe1z~5f^LCbe}g?fF;YP(!FL%{!V0C8UJje8;c3n=e>?LhfzPjMft`oZ_=e=*N-Y`FL4D!*HK&w)FLe@R7@kJ_NTJ?99FpSB(G+}}PCem-8rxJ`Zr@r1Nc-ck7w{PYjUJPJ+xSN-?oJ+~#FFy1C?Qr^8M34B)GJ6aI?ALTcMV4QSDoK}3K^3Dvn59YFV;9k+aGRoVdZgKr7fO|-Dp8uoeeb1r2JDO`eu3=}DcQx6>dnT>X@7;a@zX<nTUEX$xGgW}{_QnOlcj3D9>i4%=enBeuIr1&?aCouuPJ2)E?{C@gJo3&~-h2BA+8dk``T1d@^7ei$QT}MG`mst3MERW#luv9@$kXh<ZnyjUzOVS8m|5A3q_+I5p54B>+AgI0`;7nRtL@*0{9j#duT-Y||L@iIt~S$DBh!p@CH65g!^lb_o2d&fGt%6|+`vc`3%Xz<BioE^r;(#J=z@ohEHJhNBl|4qf-{UPH8RA=VCsTPjO;akv);%C8+5^VBbSYMjohIw_`6NkH8TZ_w5KjO*2r)pi;XO&E;!1_uSSj;IZj=0yOAQM?i@z4ThIjy8@Xj{w~gGhK^MGhq@a-_#(vm>E?CH5af4NjRI{K91{+yn<b;t^)CE@>xnln2oRRZ3=z>>`v@*8xMnWv;f-Q{%8Cz>39c<7Aiweq+H8R|SF4)n?&&HNuWQPs9;0hx*ja)Kvk-FdwBlXSS1RBX=K^H7%<QrpaYNVkJx}cwt#>UpqNLLHGU}Ym|E%{G7EX#+wpeb(sWTdZ=cGLyO8}S(9CL^nD&;|Dy`NPPcMjlWXOf)jiNE@l2y5LA7!;CC4vXHvq5F@chP8c~wUGO&}*-YJOICZlTQyRH%Y!8h*wm}zsWF)VV1IE7Hf-acWU~Yp&jRaWG1=AbJYQ$gqjk;hVBN>eN8c9K2Fq4t%##fS&vo`30r;YeX-^o0)pbNe;l2Ml&GX|*(%2G7R$ZjKBsS8dpazVzek^MI4f`^P$G`5_UoWnvFtZkvwYKh$jUGTY4YZ!4F=|Wwwj*(<Wl3TLyK^IJAWTKHyM!HiMjFz~Jzokaz*q{q;G;+qsH6tgf3m!Bw*hr|6n$!jR8R=_emXS%+1-l!WZ|c}-B-Vm1xX8#<BfX6bpe{I5#-#b1@kYM4K^L52<QF5mjjW+AxWtIlNQjYQ)CI$gv@kNrNH6Mwb&X6nvdYM8>Vl(XT$#Ev8!2Ex7nJ|{X^*kR8Chq8F1S|4qs(n1F&1>en?~{*DQTo8b-~g`rWx5{<X7r~vxPIhVvNkQK^JrzX=rTnh^k;g7i?kVj>Ki`fi~!ZUV~vqdKvkSx?o!)-x}#=WF&RLv65@^cT<f-*`N!KG1A%CLX9-DpbPdia@9y4W6x}ZE_l*lxRIeoMo<^*W2B6cvX*@ILl<-ynPVi%$S~@H^Tdbo*TYCF8+5^*Mt(Fh*T_Wbf+LL7HexrDk-A`cBh`&`G17>-U>PI*jZ82SNnNm;kxHiSQbwv<&;{$sST(i<Mkd>!3r5SFHMWgL)>+U6j~l6Fq^XfM)CHRuIcmgX<TiD|`_ezg*Fed)4Z2__BflHlULyxB=z=$l^fwY|<VWg)<BY5_5^v-Xb-`WI*Tz?bktR0if-R+wjcuTjDHe3Wg+{I!$zbd@8+5@$OWr3<{*5f7F1Xl84<ivqMpG9YWy!r#vkn+pPF?UfBkhd8dPXYSpbOS9(%Z-YBOR#=HaAkrNERb$s0$W05^R$@24+rC7tCj*nUQcK4X6v&Fmm10eapz7lxId>QT}7(BPF#do1T)@NH$7NBe^KKjbx|z8_7gTXCxWrU*qdF<!|=&efE12<%*Gul=DW;QO+8<MES!)?AICh=a?nd&v9n^Dz@xj#UpWij^X}S^<Mm{u1jC}fAy8mTwnQl{ng)|`>K5UugWBmD{1s1%tc9}*ee*R!aP<WO56cPQZQcuM2S0xk^DCFM-HO2xwyfy?3?05iDSL7t!5tA6Q!M1jjbB{tSV93_Qcpuvu~adrJWm$Y-Zj!5G6;)jGW=PIYyNJsAPPV<2a~9ls?#FY`?IN_YfsVkBofcn0rK&yvJE`bcHb*N0fZ7F|w9pVhvIHK-!UtZIN82WIo>*+j}Fv%-MU66{+Vf>yp@CGJdJ&DeIE9K4g2Pp1Z6|a(R#W6#su2c|iRIe~bPPfB#E88RJQA@B_<8%*iRA=TCCBB|Gu+{F1-<Jg+{`PbQZCJnxdx_Id6}y&qWr8|p8tFZ1vPZLf)+=jmV8m-+b@%iSk_p1%*QFZ1>R%Ow#%&+Ch{eV*I*`1>B?dBB|Bv%bvvyZn8ZW$v*L?pj~gf`|P5kY(<&&mLM|)`+M4{gh=MvX7ryU)H{t{QZ(;o^njQw7#r~Z~6Nz%e>?mdTV`IE8p|?dzKO1_p5c&mt!wI@$<TxjkeEgYfAo3$+6<gF`e?OH8&N1r(zk=Wv;Jb{#JiAPUXF36m27ktI5f;X)X1&w8>nLWBxW<U*>^4R~OUvBXKi1dG_t6zMnQ(8y+!#XRI&tOrFDuv>hUzAt%q)Pt-rr=CQC|BvBWXu_e#Xg|savddSJM`xolJ&{mD>QFg9>**UM|{h}ppor%@RHQ`#;k|;K5-!YDz{nnQ?LvpZ-wq?Zq<PNcoyNJh_Z&^<-QUAQgNS}<OZ8UK$xgVMHaYV7D;M)C~x}eNqc`uOnqbJm#&@P<3JIPvqgDAEtd>-WDbLsOsD(@YgXzNI<LasA&)rlxJ$+tXjE;9FmSJ)?GX`4d)h1^Jv$+1MS<>&KE=16{`%o%yFsX<$5Vt#V+Zc~<eS=wYA$@B6f$JFPwU&fleABoLI6nj4U%};xN+T<A?z%{i9QPx;_Un@*oWnvL>lJ^wUQ_v=HRp4ANOU%mHo72{SSe9Hz=Dazv0>`7gPh_Gl=+7}*hqflfa^xyAwmL+y$va~+=FCBq_RIG{H`*Ez9pvO2A)I<RZSsyB%$#K)N?zrAs0?kHi5bW>qR%o!vB|q|DdwymQR0^Gp7OM{BGw}(-#A&QXQ55v>dl;m6B{u05wt}T!^z1v)Bx%OXp?V+cFb7>QSvI^g*|DDB1VvF#n^fh#U|e_ZVT`Hdx<g+<vVE}ZR?18$;mh1Eb6mp>t^A*VifgJoImn?=Af-Qu^T!0#*CmIL7RLtxh$;NkwjTv<om1-ZEc8=<m4N6F7>&z$v2jK7bQ{`l=V*bGfvVLON=L%nPWh7!E0=ve0MFRF1VaI=t<i!;w*CV4L*?iK-%QnQNHVB%^paUbxOWd$Iv#JIFMWv`)&+TY|=jYZrsJT3NB*~7ST3>IG0>3+qj6hiusoB(s9%UN3&0w&{mfiL9PvR-h?PN8Q1dNdxN@Q8jgMW&K6rnmdQeH9mmpfqS$0y%Xf7rj&Z?`9Q)C<O(YH=H<`JLCW=j-8}i*Q?}4X@@?I!o`ZwAR5>Jzp{`64y&?b8!wb<6OM9GKjN0z27h**|fO$&PprHNvbJ&y})tDWtae8|3+>_3UE7|Ynn$=;OgS==OwP4-mgv#oQ9k`LKeTT9y-;#_jF_qBlf0@`G+NcK%+&m@#6<5l*nO3+q;7)nm|)=E(?MVsu|$i9rMwOxp^ZpyyhXxe%ayO5K;y9v}M&?b9SvhP!dx}eNM*(a+@TOctHxnA^Hmnb&bi;{h%^3=<7y_5aOFxtK+_8=#Dw^O&%CUMEW)d=c>k&Jx_ZL^6J$gN?{mk`A!dv&re)|0xR%xBpzoI=|?;#6|qGqx#2u}S~SzS}&Gg?XGmGDc?77DL=fPWEP_s7KKz{U-Z*4(fu{*|&vgD?ltoE{J2h5U~u$wd@=Aq27n<f{gvPwACawB`15EL#Yp?P4<{&U-Be%L0P9{pVdp-uf(0?0yzdm7re^$$-ZY#>Vm_VgBG+6AV!g^z_HzeC^nfNvadRZb4746=a8GWb;Jea=CSYGM6t<wFZ;G*E$D(%ILGSI){Hoiob*FC>fLCQJ?Sv!tRzwLD(4k-Xe&r8NlwlbdQtC1o9toVVg9xdC9iV6@tn4;#4Y6H%tH38MHdvC?EN=n&UzCiuW~L?o3`%6-sJ2S_QY!w#U^|6TbQ#rqU2T1Z4S|PmKaA)&Rk-s$IvG2lYRNwZ0l@}Gs(dO+PV;Xk=x2PP9Ta+&YEQ3zch708TWDy<40R+qCdHU%()*?Y;vX{=L$Ee3(EQ;=Ph#XB(|C?6GBeTq~uKE9Z_s@W+LYnvS#ll%K9SbIj3nmN!(5DEOT|5C^pHroQsrT?gcBbPcqSFCl(_oXKI<LXQoZgWaQjM*6cw<S%2lcXa#MPh=a(<ndvI(t7wyPB<DJHsSC<{ma*2Iwu;0O<R;N)ccR$jtVzy|!l;LF-IQ~%ezeUYjwdI151}4Ho5UsOQcI`{&SvZfY1=_uMeZbXevtSJ$D^EkO`$G0k7ITtZTpEa<mNE8jYP3Y|I4}BOpXP?7><!>+O`pYCfA*FEt)7cSzqPcZV`3C5u6*dY5R^il$@*wJE`xaP0ld;GWWHJ(m!&JJ%qM~#9HL!?06RSS+vPn<zVK1DN))l=hY)=TTNU_PR^!7sfW@gXYyy5`vju&kDN;<(sqiNKu*rSuTj57o1EotW$up<rGMl+e;;iZiATt-W^DV2Vw1DwiOl^DqV$iPZ;z*KJ8=g&IlJ#fy%TM6rY+~bsi>#oJd}Sn+AN|kIk_8<oO*KF@>w`nu0y>J*C{zyuS{D2F&{a(d*Gz*q-{4VeokFb)=jyGBKH@>wvT0YlWWK^;71gjv`@~(YqPDjIbJ0P<!Eb1>_krPPUNJXlQucqmveVn`;&;W-pT!f8?-$pCXu_yzPmvbo3u~P^(U~cf?b${8MJjJI?3&04rUN1G2e1;z>m6MYW7Kb+I)z~$ptXy>4{>KaV_@}-cc8<$+4f7w#LLza@#qU(sKOya9qp1htt#rPjc)(qU{0k8o9^J)gz+VB;RtcA`^2jXlI|Kq%8|ECpn8_G9^)L^4ySn8-=I~%6p}Z=~T3(AZ8{f`SYjlPn+C@$<3UlBT8QLShydQn|f~Ag_FBOMX491P42wpW&YX_C9iVtsSs`LiEYTq-J}B+bV0Gnotpd1*`GwotK6%)OWPgdpXB83(?jYHX_LD`*_g9HqU2TXD;1_KgcwLp?pCFto`yELvm^I%<W9~aqO8AiZ)-bk%ZZD~$=$6J)KAbRca-Gb&k*WEIG^R7)F|3I5Sx-)PM@QQVw1Z_a<6D4bwOD-<v!Y2+BOh3k!#PKk0p*{Tyk$Ik-Fe1#{N5P$B8G%-C@puCyGt(YRSE*ebfbIU6A`?@wA;MULv=FvBeWT?0>m;HJ)QaQ0AeGktMVpCLSOsck}vE?@OEXo80TNQMYmaNZ;n7Ejuv{xjY=(xrk{wuI1iXW$J<f9Qz$<t41tJPVTn#qu!4;xnn5z(qzpRT~O9Lxo0Q$<HUA~WfI7B;20=M6q~e9?!A>`TLs%O2Q6tEOzcZ8gk!rUQEW0l<X+tk&K1GOoI_V>yGMLT?mYYMDp73m-XZt)R!|q5#JTYsZ3~IB$jSIhpq@aR+)3=foK+=CUfUZPL|c1eRdUlU+$kJH6r0>(3}VhsFprYg%SH;=V7tsRC&<;e;m%?KqS)l_XDjAx2vPDn*~s^_O(qT@*V@9J$nS|_le?K$n6ukN$*bHyJwV%0;%#!fY`AlIfG9R;pWMq_$+oWKIFlS~qHQ|y2XdF0k4;3eePiL?XE60(j{9bfY(9RzUoHv%_x}a<mwzsuNMHXSV*l@d`QO)zzy8Y`#@GM4Y}~9-a((aeG5?c<*`&v<{{giK{cr'

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
