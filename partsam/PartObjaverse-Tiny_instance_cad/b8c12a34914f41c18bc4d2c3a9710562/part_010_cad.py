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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_010.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_010.stl', 'source_sha256': '3948cf3c8dc1bb9941f130f5560a5552313a360cc2de9bf7e85f789578672fe6', 'input_faces': 1150, 'input_vertices': 706, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.21046091616153717, -0.07618919759988785, -0.4999997913837433], [0.21093252301216125, 0.12341444939374924, 0.5001144409179688]]}
GEOMETRY_BASE85 = 'c$}r32b2|67Ov}FF(aZP5)3U!6vaRgP-z2V4hSkif<#FI2BOfQfC7pHNfH{#D2OODf<liv<`Dy!#TG@Baa6?YDDUj5Z=b$*pF3;4^&V^O_5bysQ>RYeyXsao*IscznF>+z@8qa#jSj!8xiE^v%0?BUySfj$<JPX-Z$G{NfT5|Ve5}hq#c5Z!x$4@sspzg~c&%>TZ|^#&R@1y%=k_?KR=vDhJ#HIx$Dl6#JKZ*@TX)ef>C*T1?oPkGSC;|Z-Er;4XEdspcXpk6d3WdiKmI$+RUz+|A70zyu=C#qPYFho?|-Iwh8}g<v{0~kM$6~7Wa@|PFOYmuyF@P-v-_1e-@<+O#CoUi-VrS9o9LYn`6<>5DkXa77fWKjU}!Wt)}LSg!Ilg?dTQ$fq8Cs2@uMvL+imkjFZpuAr*fR%J<*Fle>c{PcW3L-W&4u+-zIu=*$XcV7Ooq(Hm>K;KJjtM_n*BK>pMHFh})l9@@Df4z2K~)9*@hP*=loqy<PwQXI!u6lKzQmkB$4SWPZ&T;&Q5uPWrRj_$<BPphPbomh_wI#l7kO#m{ca(%U6^!G9ks%G9IQnt%JfndNsr3w^>}i!=3T_ozfae`#S>{%y}D_3!vx)^!V?MlX6i>$=5D(cjvdb={J#=oRkFx^CXT=$|(hXI(d1ir#%(R{xarOZ0*dv->9+@_Rhr3J%<o-9NvfcU+xS&w}}XB=fW2KUwuGSovq7j~S6w&-{n~O7xKnv+7w;_;;dLosd<}&c`J4zxeS>v+7yUB5$tf`G;JSr59En9P0%;Hf7a6zb$&>?C~wWBhjO`KF+Ft;UDM~hGf^j_RvIsZCO_R3-3hVW#(bcL*jhV*_*S+ec<T}<92ntI<9}`rnJ}W4_-I(Uv;~0c-`z9CD-RA<%~G_(YRj6RsAqiFCKo{yf{5w=HnP=9F>&w-S9bazfGO7y?KUSQsdsFy)$|hZONriAGs!%URb@(qFj2x-L1#w)L;7Rp<LH3*xhPr&id?pt|*sY{OR$}=hAim@$D`7cRXIY|EQin|Iqk)x{s-@``G`|Z8<)_={K*NepB7{o9edTyl(o<>!#oQbxptd`kQ{U`?l}5Hx64B&-*2-w#M_Rq<o^kcypXT|H8p*a_M<RjThz8qb9Y-=FC6l!?;~R{@(49@fkKQ@f)pYjnAC7s@wUjx}QIcqt$gBgZzwRpfiqE*KxGEj$@!Rj)BfN2G?aAgZeX$R@ZU#{j+b(!pw10UB|s-f29v{=>^~X`fkqr|Dzn+&vstr|1l!g3*H?Tk5}Q3v$kjIeqPo8J-)8hJNF;-axT4i<Yk+4=>^C2FUqCsytTT{TdV854e~Q@gZ#`}tCzgKJQ<gZ4vGCn!N$Zd6o0YnlURRj{l;AFwYs*~>e^nbYkRG(?X|kLH^@(WgZ#QquUfS+Yd+|DF}hzbM%VRHP=E9@@q8|WA1q1YTh*gUo#)2KuTS|XQ@8Q3&u`*kubX(dcw9lO+xSy;8-J>vw<j6L{EJq6kg40a)axcLRo%v=s@u5K=QnYw&u`*V-!2oE`udo-RCODd`u3W*)Yr$vrM?^!m->1(O!UG*rr&<(8jo-E?9`7k_57cc_^03#lmDPMlJU*|F)M$`x+I>=J8V^UesjO$>u>INeEz22$L-I1`0-?3wfu5@jAkEG-LJb-D`(}m`<vAZd#v4>OV@qC>behDUDu=4b^j^cw<FfAKULlPBldr*>;7+b-T$qwem2ODpAB^O4Xf+E5!91?Bhc})fsUUIu8W@y>W`nby81QM^PenE{4D;|>x*kIipO#MKR(OUb>Hi}x80|?bX$(~%RzoKF4iww-HwZmCksd4yE^AQK@aAM(S3c4?(1W9?SG^D{x`bsfApaLRk!_*9`wJ_Z8<^z+x(`zLH}Fbw6}Q5$klPXuGq9DZg(^)*6lu{dfxC_ak~mHeLilN>VBW8+4j?%I{Q+fvoBd)_YKucrv77NT>npJWR+i7vFx*P{rB&W>r=9=&x*MICeBg4_)q-%+q>g-<!$L5>(>9OZvC(7*8h5a3)h{KTvv7Lm%VQMvg+0^t8V?WumAUnU(UZeyIs~_`*MuG_T?CV?dxg$wd&Si`*L>Re^1J;kM-lep2m;+@{J$&^*4Up>zkA3LIq{NPWFw#HJ0QWU)AmSs&2<ubvuq;H{+<f9Y@veIQn{;arEVwaa7&*zc0u1zc0u1voFW=v#+O(m#+DuFjs%79>lBYLA;6{#H*^?cojW}SJ8ubRqJW`)0bo8So9$N)N)LJ`f_aispZ)CQ|oE^v*4TF^W*bho}27{KSU+XGj!_*Rkwc7>gpG)u6`lV@e5X0KWKIJgQ{CU=yl@<Rkwc7>b4x~2ZQ{kz19x~x@oU{PUXj?b?xLiNUtN7$NDbxTaxiA8TQv_nR*bPqg%h}%Q1d4&^4Yny81`et$$SA`bS^S*SkI!>jS37zl-FTKX-Pnb*;Kx*Q(oft-4*;UN`Gnb-S)rx9i&1)2wS>j#<~L+jZ^BG3(lwW7f4V$E<5#PrFYR7d@1#KUEL*N%UZ!L=W~!)$Kls9_*9o!9J<=wELu%WA{n)V4u`->^`aG*nLvVvHPUf)AVQI1?9)(>QB`JKaL*warD5Ct8V=`df>;=13#|yw0>O6v3?vq@V{EV>4)gxTkg!&531XKP~G-}>b4)eZu&uW+YhSSe(?1){ou<n{h+$-2VcJRn?oB!G1~nWJ=j;RuKTLd{l1D`QgPN6IrjVHp7Hz7m-?(PSsS1C*`zqmSKaz?)$<=LJ3T(X)ic{Nb?e_%xBlJg>hG+s{w~n*cUD(_XLbMlT<dTAyVs3>SKaz|tJ`v{e-HAT_FDfQ=%&5azgyk5H}L!GUTzrAGqdhgx9d)IyY9Sh?h{qF>(T3GJ*sZkqw01&`udyo=*uzd(dRe&x$1VE`s><ts=B!^^X)RvMSXqjdm!BpYaE|v?&}MGtuiFnxTqfZ1@yo#pa*_Ib?X<<1HXVC_yw(}^$S{#^$X~MU(oWcU)b1pe6D^_J@5<YfnPum{DSJ%FQ5m00X^^wT2Jd2v>fXf&;!4q<=gr8SNAD7*C~3iPSJyPiXN;-)$Mvj57r}kupYIZc0Fo2c0HooxXYJg*Qu6c;x1o~UB6mS8^=!iVRo+mR6U4e(StY^J&0pfw{a|b5XYhiaje$U#<5zCjbqV+I9AKCajceO<5(@n#<5yY`<!a^uy|jyaf0eL9#GxJ16Ei6Xm$0EfsTK)y81_}tAAA8#sgkA@qp?!9<aJC$HoIee$!qX4+OetuZ;)%xLCiRo*3&voQWRX*P{pVr`0w7wE9ygJ>NWs?&DJQ;C>%HxZl_MoBRFZ2hLlVb6ukc>l!^+*XY5zR^6^^^k7}12kTnvY1g%uW7jo$u&%WnyRNkyyRNkyyRNmK_WpF;s3p1jQ}rMYK@Z{(^dJsV-Nqs4K^%e}#35Qw8;58)HV#1#o-=DX_BpebW1ll?IX0frdYb+$ng3$4{_XEL=)vzee<gbGI}UpAI}UpAJC5r1cO3NKcO2F2?>Oke?>Oke?>Jh2`#X-7V}Hlda_sLoT8{l4N9$>S$3YK%$I)`^?>O2&_IDhur~MsA%eTMdX#K5!RNdY$be$CcP8mE8M-QHd8{I!2HoAX4Y;}D;Y;^y8*y#RwIC}6rTy^_A96fj*Zgg8t@I2h+H|-6chg;pW*ZwY?f8^x&ICzf^-TFb*tse|@{9vH#`*=oIKd8F(gQ^F9uxZKqT=iEy@XJ=$_h*dm-=8tMe}Bg4{{0!F`}b#T{;Sp(<<hkuO1|8=KG(WX-L4C(>pZc#|IWhb`u;|cpZ974o%d?2uJ6?Z_2j*pK<B-hK<B-Y;JVD`p#H31tNZUq(Czy5x>>)f+x2U8TaI17L4GqXcKur2j!W=f&Gc2t_XOtsM%C^6jjG%C8-0HBexujz`;AKyJ%}^WgE$jCh%?cHI8${SXQBsjCVCKOYJM9}YJU5EqqfVw->CJm?>C|cajCY~zTc?zv2m%EW8+e-r@epI`q=jy(S!FJHNSnoQLk&?Z`Azu{YI_7eZNujoA(=|^Pk+9HP7`uUZeZ>c#ZDgd!N5H@dx&OW~2M}nT_t>XEwTjpV{dCeP*Nk_nB>eeV^Ip*Y}w_-LNUHhlzU&W{%n%*W1QF==OUA)q^<4=(=wN`Pt6{opG_cj*Hd(`_)!wKM!>FtKhmCpV<0qJZ5wsk7@sy?-5iF;wz*3_{!%0ALaOdPK}NAAl^U^;tHet_`&EtelWVu+n{{rt<`njT3zRDke_)Q<kz^x)>Gpaqx<g>CLi-cu6e6^@Li16b$>9r-ye+b_Xn%%cQIDi?_%tA^}86O`|o0m?!SxC_L}d)RJY%SsUCdiVsu-M{VpufO}_>Es?lw~+3&&v-SnHizX<AY`py0x=ljik7uNa93NPfE=T_HwZgrjKL4M|Wke_*8Sn2enp5MM2``MDSlkXo@FJ3n!_Opd2@%>|ubCdig{!!h=KdRd}$Ll7}QQgKls@pin=QnYV&u`)!Uw;$l`1+VQM|B(LsBYsNUmp|a_;O5~<MW&Ei+z2}_r<=S&G*G#H{TblZoe<~`OWvmzTeFE#Xi6JzS#Gt`M%g+*L+{>+hx8l_T`xGi+wrf`(mHpd|&MAX}&M^`OWvm#eHe7`M%ie=KEsR?f1oAH{TcMtv>XnT;&vg{duh0{Xup6y??<Q(JOJf`MUuH>wbv!@OS4#xAAJ{@_S=F_`3(_!QVYl-TvK!?~i&l9+w}IzpGGO|D1PYyzJ;i@BM4?_ZH4<66^Wz?SCy-KdWy0)9ac2d2QBTyBOJM<jh`;qDbt}s6y1EOU9qN5K;aq=KfO`w>J2{`coHYp4sq>|G&R=aahZA6y1@EqD#SPQNqQ9Pj_~a;}<(?feF9F*>NtdlC#QD!YgttSOs2%<7(is@M`d?&X%~c7CD;_E`|#}3Kv`m7c7L&hcAWCbv6~82N!$<E;t7+I2%3{zQEZru1-hGQU~SuD6l-d9Cbeit4dmV_>u8cNZNlACOi)lej+CP1WfqxSQYwdF7=*AyXJ5_mp0D<m%``3XJbog*DPl<oXrFuh6_%IPX!l%)8Px?)6z-3$}zr`;FYm*%!T9N6|r)R_pup$H`&<~XAfb*r((jVfz#nFnU|M<E#Q)VDtQH~!<V_VC&>3i#yQhTmt(;eq>Xg*f4H;z!Ex~Z&ibU1^gg5scMCci?Cf4}4E$DSJxK3C+E8q)vtiD9lW!O}6h4Bo$AkC7?;>q9I3C{JSzprol6DvM>`h(A(w1T1aQJZY2%qI_wzCP~MEGUSE_Zf5*c?8<*+9|<k|w;Nvu4in!Asy5I%`b6%i+zzI&i@Ta5?up&KJBCewwrTq}L}+_&LrlcGd)b5yz)GtBYQjv?iQekMjka!q0<W3bue>3hxj0flGOfxSrqz@QdKLf<53Dlhzx&6@CfV=*zf|p!^YN{lQD&L!9+Y$$ej9JsF3d^z}gSa(GL|p<gPQA9tscxpOyKcQ79=V=r@H6j%Ts1s?zogy++S?qFYd3)<WV><w?p+7+K8czY`0V!~y;3r=P2KjZRjNGIoQ;M|t@D9LjucnJI=*7{`D_Z0RUu?I*Oyda(M&mI57*`QQ{x1|y;Cj2Mxdw6yB<|&}=Wi2Rg8MqXFJo!#xkE+W)RTr%~SPfnqKT#9EPy=641MNgG53c!ZfhWOh!Rvr0!+)YJ;(G<fe=MQS7f|mD*!P83%h<E4(ub3yQXls@_z8TcEAtCyXQvZvkWTpLj(_d!taO6sq!X^byE%AX2A{{V;Q4SlcMs<aHc2OZm*Wi`Hp=kt&A_G^d;!OT`EWURC+F{^?!tFF{*|-F=>(<h#_7^n;#{y9{6p9N51fq$$H65w7!xJ&gYeND9|<oHAH}hp`x)m8PJ(|FCD*tQ91lO5vhM-Mz%`B;3*H0&l(Hs(_rWK?D}%?u-*>jn*&c8={5NMm%Unn$cw#EyW4YG*;5N9%W9NhC!q12QkV^1BsZ!pIW5I7z34hPo_Ea)H+ZiL__t5rj;Jfg~%!?V|!|?m)!{fk;aB0U0sl-2A%wE<6Yzl7zKNYM8ugAH<#pj9-o&r7u-$vbbgI~dS!+!>Ug8vMcdI?JT!e4jxin9;F_ux~w)&g)od;$Cw@MZWb@b|#&@Hx&3oxK3Q3V+erKb^e;z6*cA*@Mm=L6>}U!AIbakVp7yl=lJnHhdx1ehqv9KF!%A(kGF&kn79!c7ShX@VOkn1z!d}2p60Uf0aIcAN&w5ZGV*XM@f5?bm^x(;BNRHcoX&znSV_%;j_RQ@ac@%qm0GtjMeLC3&1JxkDYzu>|fxUaM{oIlD?NT;ah3{Qg9jkQ~GHu_!j&}XZuLsN7|=c=M85|z(sJm)^}X*4f1^ieggl5Ji<?LR?XR;QG&lm3IDINznpyseh;tV^3+Tv>4JZe_v};>H`V}a!vCPWZ^8e-t8;BhKZWc6!Tu%dsXkZ_{tJ8DNvQ-SpYX5Q|9;8X2ZdLazN3ym(gx*Ua{MLjQvMdlf+g@@BYACAp1~woIhF8l9N$U$PVxwU&)J(%lKv)X!uLkWwX0AEsh{vKxb|M~NBCCi@dfxL{0G`snLd#|5H8o+&h>sF-`C(y_)hW&m-`mEf0@LZlJz?koCKdlo~c|zu2n0Q#QJiNaT-_)UW+`Z(Kcyg?NqX^Wk0$H90R`xJ_H;L9|G?Q_JH?<UkF|RzYyLSYy@u%uLIVG*QRcDSTnMAX0i@sE}j9N1wRA+FgO!FlXHd3{g~V{oeegC%i5MTJ`0=;pTYTOa;@r=T^;Q#a3);#6j{TI!6op;@EPDtxZG37J;r_DX!w2bY2YMy9%FoZD!Gqn$=C{>3vURo1)dH+opXiD{m8_Oah%9FKM2kSC&KG677f6faG7^<-z{@b_FI{w)4{3mspJtZ^G^1J)4=-hJ^1q9z@OoAuP@ID#$v)B0w=>I9(V`;FSrZ-75pb~AN(h{!~}xJrxGqE{8X?mT&^{S>j^#pe~0zI3;Y7U3%(EB3*QHqviGvb9FJAudNTjzKDjnn7hab<!X>Vi`1V+^DqLdl>BQl}r*S-rei<Dld@IM3Y0EtD5%@g#OW=#}m*CsLci`LLyTG0Brra<5JC&gLNa4-6hxnE}qJ7I)N}c9|^WgL0FM}_^Uxsf7x52l=_5R~4>hl%4aOn$~H)H6RcQ|fHtlNlwoX)Yty3+3z!DHbvug5XB1*gD2j*@$Z`@sqD`{9+q%J6fDb!LLI;PSjw?n&+i$HMQ0i=WtouXrEa4&P25;S!Tc?DaLc2Yw#+5)x;e&;5jOxet{XaUZw?KA(Hwso*zoi9z4ySnzXrIsB{mTZtzmuJ{Dp0hcl*9+L7Tb`gIr_izs|ze~W+;GdC4cs}>uGPeY!j>08Q`JL+s{u}-u_zv)6cysQR_tGcQ2YZ>%?=q*~rC)?geElkI6?`B5HvDt&Yq<1-jO9r1Uie7(o8b10{*t~a2kLX=2DEoty7ZaDG@c8{9GVL1^XVP5aUys>d?LIGsJ}nx^NJ(E0=Pb}m<aBG%Qa-2&jLS(>vI@=J}>+fOt?JDk!L8Y(#h`_f{(!$!54#%!xzIJ1y{l!g)anGz!$;`!R7Em_)<)`KK~Y64K9Z-=ls?5xy*qJ)1}XK<axY43zFY^-lFdwbk-}CJmZmPWAYqHj`g|O=cMcNB~7~x{t4-~Wuy!5myzc^^1RKQ5iApxuFWr<ZB8fnO{#QWNj}wjf&Jk9GRo~oJ>>Ws>d_C(tc&F7$F(%yd(=hJq>Vb>(r$UKb~0;N`|B;{oA3qnXFmP8l{CRo@KMZ7J*O)B#J*JNI0-gLmp)gUhHu>BY>l&Ga4r04XHPo&2ly2HbZ5g{*{6X+;b%HK!`a<Yf+M1YKkN7=(l?RkO!7&dgTaH~XHe#u;4t_UuKf^r8vG#6KM))a-{{inbItl(SFc~6`Uwu_ytEuUI|4in?z$^FJxcxw)`RzRc7U@toIU4G{>)`;?eI>AC8^|C_`k>_$C9rEP0t<cw0oVc2k(Ikj)AX-kCu7h&bc6x{}Lg=3*mwn!OOxgj*|06IqQ*5@^^OD91||z)91OgE1aF^Y>4bf&IW^v;Z2-f;_Mu-1zhTLHrEnt02gcs7i<I<Yz%Kq85e^s;H_LAUGMB#@H+UVF0CbXX-PeVH;a<AreG6z7iaC!+Gpe&;o5n>j6FCE{;Z6pv&X?zaMcfXb?D%%y|Y8WgW-abNBEP@);jwO{2Trkyhb{~n(2gV{`R0=V=(=H7q|#6xDdXKaguR6fib)syaFzESvpBS0e(Ctyb5-zv&vvyxL_JC_**LBQqMKi^&tA79oPZhfjp`oL>~!mqEE#((bs~H!3F0#yBX{Vf5F+2?)>M$a_|FOoi;dL27CtI&EYK^3u>C2+l})zPdUz!vLugSQAYkFQpxp?;F`h(H#mC=Tn3jpHPqR7O!zp~u&ntzFyVJ%!tcU_55|NK0ms3|QRWcpT0}bpyTH4_j|7i^%X<IaVLedVDSQL%Ie_*_{sTC#3;Y21jhOINU=h5CGFO4Wqs#tquCwdGR`9ki&rS4);N5UtoA-g^;ZM7BHago69+*n_JZCGTBz+}m!q+jkBIcdUKjHJ4XY0UCaM^R(I$PoFPiH?ndjebmUqK$>t(oI1o&DF@FU<R2(AI$M;AgpO9PaEIuo=8fI@z0U2iL*7IXli-SMU_LtiwvqZUk?E|3W<^uiz=17qJFggYDqgxug!x3c&^NYuGpEfh*zr>2v9)1L=qB=^yE@is=NarxPwFybag|E<Q;7Pg(FVxcIvwX9eIW_}{c^Ew~0=lRo*Iwo01tzp3kWjMsANDR^C~)VJ(s%w>-{lzmI=Day}deaL<)dqh{((FVBgE!{X4A0uOYZIsO68yH7j_tHM~mu1;2?q|G5Wbh`;5AkL49@%DRPq1fh#@9$YYo(JukbQGC=`ufRpx=xiTSYli#v1y(le5d5O>p_T)7Q)JC$f*7%D!Khy}t_cZUS?#i1IIE{5rx#leCfK?SL-nH97Yb`eG#I=zjVX`*|7qUHd`$wVmu2&Q>^k23!udg$v#UUk+ae-Uwd?Ukcs;UkYCWwt+8!F9ut~7sJIT7s=dpmQE#@N+n!O_zhqi_zm#K!N=f_!+!&Rh5rVx%oqr-#M-XJy03)(3-&8}&##oV5_^ob{}|V9jkRHKY(rfmO!zw5w4Qx(9qpZut!M98PhTv+ir7yC7s3nS*I~k2fsevl!LJ7w!57iz*JG_&OJ~CyfNkIn;0?hW;0@u8z#HL>;ElnX;EmzufNkODz?*>W;7#DNew%^q!FKTW@Ri^S_)7T3sC2Gx#DvSfD_Dj-SgZ_tvEWVcw(uvw)$k|ae}aF&|Agy4-I+aU1bjHy2|gS?4D1LW1|JIE3?B*~0(O88fe!}Tr%U4>;dg=U(xowy@H^R41>1t{;NlB!N|&w|;Z?x4>C(7YcvY|+yej;7uzk8TW)^+|*dbjSR|`K8ycvEX{3Ng={3LiD*a@BoKN;){KN(&P>;f084i}WMt429;j>KLklm0ttlIM3!_$qKUd=>mg@TOF0yeIqsuuQ5nCKSGb`6%;p1M_q_TyPm&{FeByL-Du5<M*Va#2?B!ZVu0nO8un7jN&gO7LYhv;>7igzxZ2;SH$Ow-#rU1zFuOD+cELQqKQdN@H18sUE;<4oGY=;({S-yvd4)Zy9GaAj`P}Z?(<Qi9f1k&0^S1e0xwFH-j5W4dcScE*Ou#w&pVv<Nc|-)kocfeRO)MG|2!`$^|8Xm7fU=SzCq$g@v(9&zF2&G5&TAUNmpMY$LCR&l-ZRsCV<`H3rL^O*p%hk@w@L*hg5=xrxGqEydx&O6I}3VO!zwSGhk=16TCCLEO<D)Ec_o_Q?4z1E%+o@41W^72HX;r#zmc@q>m+Ll2~Rn*fA=Nu>?0`!k+*;!aGvN6Idt8??m~+WnUf6xHgMQ<2{{YGA|^37<pv9k6_NpJdtzSGuAprcQc;r+3QB4-NbmyaVy43=8nX;`%}csaEU1eYo|-&OTn&KEv_e68$OD;(E}4+2kZv#M*ccjDxJiZb>V4D_<H7m@O8`q;W9^LtYqHY%=~#8elt8GpX84yuMWHpb%?<I<d5J_(FbecH%Fz<B+9b3&cj+U_s@??W8gl{dO5qo+0`6hg$chB>qDLa?z)ql^~Z$wb2i!8gXtt)@B#P$xa7Ojo&SjJ4bF~o$G18w@2sM$_c6|n1CNFmJ9}2v2)GGe)}3>Zv%|rI;jg)JUvl<3_)qwuF6}DW^HK?31Hazs*Eu`J+0o9fmVB7--k9({v|%Fc73>R_Hr|#_%DW!k3hWPW1-}mL2fq$}E!Y=+E&Lj=54;ccxduEM{)%g7CE8bsHVQw&r5)?+K=3elH<y35vsuo1y5m9VB<~>d3EwDl*Vz@|)$oViIdf$lgMHzB>6bp(MEY+cW3BypD}5|@Wk#Q0NqYp3g3qCzw}JiPVgsTieGYtJl+3X^n6G`{y}{ezz2UclgW$Kqdw~PtmoxW!g1z9q$kP)X0PhL!0p14h0q+j>hxa7ya<Du6a(FkeKU~IQGvm>VxnC}wtd}Dl9>VeAtPRmclQkr3q^q+TQL^r4I(#`w^ck!h(M3CkIV9`nxm03TqRD&{tibV=@Q0ZT<sE-9N{-7jZ=}9Qfyct<lIK<MMYy1(zX~1;m$h0UV{Z{YP}a*8sdR+{{?~uWT>4Mmp^38ogJyeX_UCPxXMX3(@*lfhd&PnBdyd<O)A8U>kzatK{{t!Y<{<'

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
