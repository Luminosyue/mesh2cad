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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_003.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_003.stl', 'source_sha256': '1b3329c09b5c4fd8aed9dfe520ab23ebdfc9b436b739d884ad85da8d6d2c1046', 'input_faces': 1081, 'input_vertices': 739, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27017462253570557, -0.4991077780723572, -0.27237820625305176], [0.2701725661754608, 0.3800107538700104, 0.2917025685310364]]}
GEOMETRY_BASE85 = 'c$}r32Y6IP`}R))(xe%BU!;WILNDPEs)R0`s7nV0LhofM8oKl%Z3#8hL?CqbKteB}cVqz-74fy8s33mx%-nO{o!Rq!*LVH@T-SZwzrFLEXXc!<8zzU0wu?@eKDQzM6gPg@*E#-7Q^O!-HF6uH`wkyDuy@}Pm4*x*7h>e(IsK8oxJ{?l?Ye~+qm2pSefo~*Jv_XwE4+Tc+Tj&k;r(KVj~w1}$Vaim`}C!}S<gWu`m%h)fSyD9ve#v5MbxR_iYQybHOciq{F8-E!85z%6(4igfj-yBJ;lDi>~qMi!=<h^49Ly?FRzjtn}%HRIpk)e?Ml6Ms1ncJC(~W>Ipp4E4KFMGAD!avo>(Ex=a8FsuPXIMyd~-{XIJWFZl+IF>fL9$it%3+RL)oChP&$(W&Yz=@;blg<MTd;+;#BDMP)vP7x3I0`k_)UbEDoZwf;^OQUBh|3qFV3ni`U(%%^Mxp1WU<Q0iswt^WLy(*OLsV*c3%s{N6>nmtzP-8tj<b@X>!e9`BSdzxiXuV?d@yv|!G<&4iEH~QB<ugrh{?>zUX9aQRNZf1&5>Rs_Qcy8_e?X1r!|8dX-rGK76BCm5vsh7ENFV!)3=ZbXf;~L&v$xWjNzm9(2n{z&g-1X-e<^H;Boj)huZ$(e}9CClk$}@rW-YsWEUbmD|Z|9+2rQY4Pu*j#jJ?(SIjYDV72G)C){>;zcpP`&mFLSfu2BqE@{rs$WpHxxmW$vDwpwwGMOr9I_x~umWx%=d`b4ve{yLewC)6^87L+-l#>ZEf0!`F#<{4qzVm$|>vTc?!sUGL}D(ex#x`W$l4%Xd#J{YzXI^||IM^)mNFzopiHn#yzku%&7}a-(ierQR5tp6A}WdrtZsa!+U_<^FoEf0`=ZCr>S(LvFlwrzrEuH$u##={==h=EmfXO1)>{UVa_jbKg4QbI84^lT(%XZ%9ZH?~`AS`y6st#z9KGIckOI)9zcPUgpNEkCb}Pf9~*kc$eo??yt<Pv{}mg!7AO7_q85-j`$pMPo2Y-GXLc*L|$r$QZIAsZjw^(nL3kSN9(6Y$9xXC*Z1tW(*O6tJU9PZrqs*asyD+iH#;A8>|^XpRdZhtA0Ib#qH=#_Zq)nzgi>FzK0i-ub-n#Qhuo8`(h=o+v(@3bS*V3lFLUplx=Ot<>CqwX;Ry$Q4!N~_)iI_1`_FjpS=>ggNA6DFNU8U1^N9XoJ(PNxd#1Hk>+4hybq#!neGa*CtE>8cn3*}5pI1cIFMSTVYvY?_r9Ru&`}lbc4^!)rd!D4<uhbX+crW+(5BB;Tax<*mL1q3W+w<Jj@?E7~=EmXNO1*KmlBgS4O6`x_`m3PY|7a4Qx3ywuvd<wmGWR~L^v^MHH}`xy6MPQ2yU>LsrM^H>o?9_f)q3QvVtdqjv)m3|KepU1pF{51k#Vn5ANOWE&l}&_>2t`<u!nn;`h|N$-g1jtFY_8_)%x)VxAHuqOp?zbcc&Cl-w$2J$BXl;u-504|Md4(r9R(Ck(YS1#^;oexS`fhd&>J-C2w!=IpppPM|Udqu3Tasb)wXInI9|coUaRU?o%*a%}0i<;Mb>p`mH{P+`aNeqEg?rQ5^TT@=WtN<thHvN_|WYo_qcrtJcf>aM&89e(dYvJip&-q0b?AwOtmk)O%L&+_<qstw-*T-mTWx&+Vbt#@F61KBxTAchj8eJ@MOSIOW!*#!LBe3)5|(-2Ywwo4l@JC%%qy{q@^sKJO;odG7zU7+){BGEEVA-3QnC>+o;+I>8(o%X9y#OFVbqP2_#dT?KgVj@x>R=hj}4KYmB#kH6r#YwH-^-#A!$BY&SI{lnM0#@J_9lzdSczOFUREh4WH&)-MZx)c0(bHQ;n_dMsh)pe4Rn+q@UpEs<<*{&*ijz>H<2cA~y-T&z)u1~l2V*V=@@!Z?88_&&bg~d2~hx6R%b9WU#uNuYp`qR#@_7?B60X0u4d8=7G_uj6q=12bGxqnsbR3$$k-hXD+R%%{uy2#V|oKW(Tt9fqi?y2TWO0DJR`DCo+l)Gods`<2do_k`m9aZu>qrJS(ANkeu{roV`&9YV0^O|$rIZw^Ho}X__bM?HU3j9BFYf4o$uNN)qi@DYF{qqB!yNwUj{KaUImuRl$v8zS@h>@04?rJ(v%`5H}eZKuj&BGswJ~`8?*R7W!KIbo<9#OAnB+soi=?*ISckvte`@}4-p6_a7BftJ5qty9dug!C_Ru6SPnP>CdTKbhbuIG%%i@iJ`J`dUPJ`caa$4z>9Mtm;c@V_VAJM#0~=zD^HE{vo!o_ptQ;h$?ycJXtWS-|4C>-&{FH`9GAe*UVrd%e@=-OjboyXV_?d2U{<$bUXJW6mnMwW&MLy(K?Y>$jg(KJVUwg+yNVf%19xp6&hxpMUm@xB2@g?<GEet7<gQ-M#<j^Y=E4I~SOH^LOC&?zkts-oLUQ&&@kM_;V9~bpES>x%J*K@jRvY)hkN=_GzA5`CLl9Iq^Qv&F6Q-_odJZVm^bL@^M{>tHt#U+qBT}`XCRwKC)iBK6ZVfhsyQwWNEX2=f_^D_e<vb_vgt^=ks}f@-Ba$SXqA%@1NocB0rUz=k7hp;^+5GyXW!zu$NzFW6VmCHyg%tf8NDBw?64E&bMaDY(D=Tmh$~y=0V^8Gj0_5+Vkr7f8;^m|8LFUxhrQc{(auq*I3MFOf#PQhrQ2p_kir;@2`@1W;$ITJJ;XOu94GupZ+)b-<xK_RdIce*WkJL>}j6+W7ddqyLqSb`RrTIuY*5oz4+Yy-BaW_mx#Y-%k>fSslIs<?~}Kun15PBQ9r6I&)s7?i1|;;BI^4-=Ia9Uz#{(hxqm~yw7}fzH-rD2?7jU9o)5HL#`BhEdA$`oBrPyEe>@`UH~uB+6OV}eKvnVn9Ms}+U~cs*!LOTHu%NiV*<Xpg>R;kM&TV{I$*=t=`m_lX^#zKH@0&A6i1|OtnHHGK^YZqJyrkq`R^aorlFEuc-;@#gqiFG5pjsF4ee69`<PYbH{@26O0&}a-Ht}4eMbsrF&)7`#-&p>flGo}h`seQ<`Zt^}^6b(4ysWEXmzBK1$KreobV>`%%_gDZ`QWI?^GZIVxVWBwd?N1etu^t1*Wd8xysYFe+VI>R(LOCOx1N6|o`-&3_q<YHB$Mcm@8{O)VdC$PhF!(=d6hLy$tR2w*MDN&OM$sLEgQcM{@W##KJvbJTD>pc|HdrQ=XPmvJ&%Qp`tu7!9v>^l{V97|U~XQWuiSUL9{0t*zw^HpIlfPt7jj(=%*`9)M4q)vno@r$m$?1|%=1eAPc?CU?#GJvRjEHjpSF#}^}O@WWhI~D7T3S@`)Nu(_HR)?4bQQWTU!b!_t!HjVH1CSeVX`t=V9TLz})rhpg5m=Yqs$FIPCH!@%in`pYIrvFD)hSCZ5yzi)9n*#M=Lg{LDMz{5!p!5}5lx@$mkx=bd?fvwzXe+&kYC&yUVzI<DkhPmB99dZp+;`$huKdpzRLkF3_M(*koV^R*Q5ez`5aPZr6#O}szzr38L1WNxm`%<r$Oji1+BQR77ZV6Au`*KT(?Ft_F`xDfa`wT7(_d6$0TzIJGJIWRXfbmjH_Z;Ff0*T9G``Pbi^;q&m0Z+0RucW+HEu214hOUdW27kSw!iAsLd;<>v_G#}4++KlIBgZ}(FT02@>O1^rNxX!7Kjw<<phkPFXHn|c4bL&(QaesgAAFtGRSSCI{yCP30dE#|(-)}8e#&t!;iTBmQ*u=oxJ9snCy?>S$^Pk*V^!Z_>nE%*LR$y+mxXp8SO#7oseV#D!KABuCL8<T8LFBGDv5p?NoIj_ruKq4QKkv6X5t#e)7Zl&`Ca$-X{7tgR@6ApO%)Q~a#C@6DOWf~}Euw#^6y^TP+<n4O?ysG1T_dhf;|YmMe(Q+1zcGzP|EJqT|F)6h`dn*n1?J|ii9Gj))jX=yk4xtBaR2yftCHV-A@1M2cH;U>J|z0Q9xD2;YikAOR_i43{@K>_s8V0>nRx#cER>++W6O%a_m9MizbC%0dWg?syZBuBFE&jH%v}*J_`1hTGx<D?h}Jwei@L@8pypLe$t$)M-v^rC;6DdjUw0LKD&!N_vu4c{CEuAt^xyP1|Ni5tG?M35*(>5aFFvxAy!;7qeOC7r&vV9B6@MQLxg?&CC-oEmjv@19zwqa|uFB)p{N*?N=OtIhS!V)s<6#s2{MtY5!D*$w(h~lh)>!@UxRR%S&7YTg?{u-0J`11m=a&8nkCbtZw~L79lZW&3++D7L$SYOZ!(W$~dOk4sRG!11C%TfZom1+2^cK%=a@ISe<eBI3pW8ei3>E)Amex|_{cH2*s;<oA&nda*vgnhqmiTw)`{PeK)!VsN?@pU|(sBOCgXS;m_4&(Oo4@PC<daVK*Uq*3Yv<bimAQU@?RxG0+PQXr?LON5wR7$M`WHp<f5+3GFWI^Fe96wW=Sz03JzuhO?fH_OYtNVLTzkG`=i2inJ(tgy>|A@kWarxRB|F!iFWI^Fe96wW=Sz03Jzvsu`FzRFwdYHAu03C}bM5((oommR^jtn)vUBbElAUYMm+V}7zVzSgsXkw_bM5((oommR>|A@kWarxRB|F!jFTJTNejZNu_$Gg!U%b2DDL1Wc$xgX7C~k{mpU;YI3d}vV?utH779=_4uAgHP19NM4;&tA~wROK!Zsr=B?37!*ZftSv(_)l5pC7hdcbpG$eLiMPe*Sw<#;g_lopNhwpJd1U_qVq?<>tNZ%6yFFIj%X)N9L}ZZe>26Uf+m+uWQnIzf*43DxK_DKQn5pV?Ow?G9Poz{VPuMk-0seU+VMR8~a4`X*g-WQ*LgLOLoewDdUnH>qGlF=B{Vc9mn;?4RXwlPg6HLj@#qT#=zV>l5|D6k6Lc-UXkRKd%LzybgX|8x<$!ruM^j2Y@7W~xw~GiB**#-yAqvpt4QTdO8(spalSugNp{Lz4gN@S$}RWP-Hv_!J*v##bH^>t>+qFir`)w?{644LSTyZRr`#P|Imxkp@}Weh-1F?zF2_9K=2pjf_Nk)WcTcSN_cwp9(|etA>vWwxPPrNF-szMZd75rhuG_XoVm?cay-vBc`|5TjFJ0OBej#^t`8CNY54vA6k4RSTm-R;uG5>CP_BrLAE6=`k%8fxUb~^SclaLUYyPBqVJYSjH=lgY}xNc>0i{A^4zq?7vSELiaM>>Dl{=nRb`BwB_mp9ol@7Qu{U~cZ-Bj*3;;RdDu&k17whejVz>gDHa^=qZS6}eW_7vH&A>GQ0XIIkamPIk(TR=+9rrdeL}Nn3fqDL1CCSLW$IaN)Ak`P%v8E$aDx<rTU7eyipBb+-N(E%N2Qy-vCHYbWJ?8GTHVUkKadn8)qjrHt#VCgzipy3aBHB051iuZI=I@2_@>NK)og^A`X8Qg6Lgdz^A(+uEH<pNX5(0{d7K+KBp|zdYpi_m_@n=#YEzo|zt)`-kSZ!|Ok8Fvcl2AFTS6=Pzceeg53E&gYODhay%v<?iHq8w2}zkN@(3_X+K)^pUxd`pp+kx%FtOV;@(@;myiC@4UXp`=461Jg|@He<kvmn;Qb_T~W_@?r#0_roh~&J@hWGZ_#p=&mlJlMXd>}_e?CnbJwkm-oV@(cadLD&z5^0rM_7&as4wEoXYd{hn?@EmfQCcdC+~-a(N#;aX!a&ub#_wub#_wZ%`ksdu6V#d-YtdGi9!?d-Ytdd-YtddxQF5-D{7lt$X!cpO3!o)pNOC3d*tW)pNP-mASs|)pNPdwCAa<d-YtddxPq+?hVSZ?v=T|j@5Iyj@5Iyjt#2EI#$o+I#$o+I#$o+IyPurtYhu#tgYMiT)&?Bx>wKTx>wKTx;LmE>s~w8*1dWz*S$gYSoi9=T=&|!w(iw)x$f0-xsD3zgLSX{KGD{_dM?+!dM?+!dM?+!LG@Vo>bYF^2IW}y2F(-eUOU&;y?QR!y?QR!y?QR!z4mp}*1dWz*MWAft$X!cu6y-7=zeMIUi<r=w(iw)x$f0-x$X_>gLSXW^>weF+w0!($DP-`GS}C=$b;6gvR+@u%6fgBspa-MQ|9`*QOost2CeJ#T(0Yo2d&?<++M#S*Vk|6;1u!wUtj<0xm^Dv4_eP74_eP74_eP_xxJo89<)B!bGbg3<Lc{eEw|U(^1Sr*ww}xNwj5VmKl`V)<p1uX@8i>RxsOlg`aV8Am;3l+uJ7a1bGeVt?xXGF({s6xPv-hQK0TNF_++l{<I{7wkI$Z`wvSKG<vu=pTx}npp38lFcCPK?({s6x&mLFX$EW9VAD`Vv+sCKpavz_49khLXdM@|z*}1llPtWB(K6{?pK0ZB{`}pklp|+1ND91iNyN|YyPtWB(K0TNF`1D-v<Fns~+CDx#m;3na>!9u9({s6xPv-hQzMvfY`0PH~K0ZB{`}kz8@8i>RxsT6&pJ@B|^jz-av#*=Bk5A9#K0dpTwvSKG<vu?9I&1s*^jz-av(HQ0$EW9VAD`Vv+sCKpavz_aYy0^0T<+tu&r93Kr{{7XpFK})AD^DfeSG$~+CDx#m;3naKH5G$J(v6V?0IVY`1D-v<Fm)r_VMYt+{b5+tL@{{bGeVteqU+(`1D-v<Fn_f?c>vPxsT5tSKG&@=W-vP-ACKUr{{7XUr;^v@#(qT$7ko-K0ZB{`}pi!+sCKpavz_4UfMoBJ(v6V>^|B)K0TNF`0QNU$EW9VAD=z0wvSKG<vu<;*Y@%0x!lKRkE`wD({s6x&(5`de0nbT@!7eyk5A9#K0bS%+CDx#m;3naKH5G$J(v6V>^|B)K0TNF`0PH~K0ZB{`}pi!+sCKpavz_aYy0^0T<+tub8R1=p38lFcCPK?3(B#N&(5`de0nbT@!7eyk1r_4K0Z6w_VESf*vDt*+CDx#m;3naT-(PNlw%)XP>y|kK{@vE*}1llPtWB(K0DX;@df4B$7ko-KE9wF`}pi!+sCKpavz_aYy0^0T<+tub8R1AP>y|kdM@|z={euW*G~Db!1Rb2{&s~3!ysigavS}62K*;rD5O8qo&OUs1FQdk{U>0mR;gX}fA`;j$+DBpVL#J4cmkMwE0}yOxL1f_3}WidGz>lgA|4DM1g07qqc?mVm?ZnHLw{lt@gVqCFo~FY(mZLr1o&X^VAK!~!<_cxymlf>WPX4t9=-!iz70(71@~dc3}NcWG!i}$A|47K0v?Gm`oZJDB-t+>{bg@*FESc?2y$ZTN%N%fcEE>%hoXjfB<6Gg=aq<T5A%ae8{oUZ<lDjI>%o25F|kbjna02;LBzx1vEVTnqd$BDm?ZmcK!4erd_6K6I~F-H^`v>yc)Q@k!NXBQJO*<*i1XTmY#;MOOq<|IVDjBy@{QmD?3fWu1DVFbCqu-e;3L4}FvdXmCNN3%+l2naB;pb9-Cz<i^`v>ycuDY4;8Ca{9)~#{!g=jOmdyMx(-!z%F!`5Y^3C9n*)gM;K4BUUp8^q&g^vc0#~7c$w}45q-xl;ICJ~Q@e+ecLQ%{;Fjkgy*7CaU;#N#oi!#J;GWbcO>Mkl5&@E&0DzF_i?z**UGVNB@_@rOJVBF+R41JfTGBR#wem?ZmkL4RTraTvTWm_$rHX`VD*4|pbUCe+BB>J0e%VESvNKjSR$55V2PJ>mVq<io(^pMdkTV~R3mXUYK20%gZI*-?`lH8e(ccuz1%_UnoM#3bUP@L^yQac+2jFpW#|&H(QQ?#+B4(_r{;F!>}f`516Xc1$^@f=oH#c_HFr@N(ds7^5J3FqkC!4Mu-r5^*{BBru7XdeS^;yy5U-;9{teIo0Ka_Xfu@AH_5dJ_SrZ2TcAcxEedAHdAS)!ti$?;tKHE;KCTAG<+PGB>Rm+e_|4GZTK88iI{rQJZZcs@Cx7xsF69<6^6%xCorGNG#x$*OuiIM{yDflJ0^;$3R4+)C5X5tJPKR}V^o1p2a{yK>F7^PB94MD1(S%WC(V<_n+2~4u8A6%Q(YPO1aK3k<&5jX=YiwE3*pPb<m<uYtH3STF>RP4nX1F<LXj9J5;aXwLt{k37lKK$-$L{!CK0!RuLqNeo4}WYX<V9jb$A?jG4qv7YvA!<@||GvE#QvqnC?t14SMD(yctB?7Tz6fVvLsXHDHqLw+8)*NyOdZJHaGk>PhpY@#5ia!EI3^bE-4pi^1!dZ(>S-?*@|}29xgt_hQEkVCu}&3f=)Cj)4yVx55~m;R#@p?3aN4#3bSY@WWsdG4-T*(s;Y!G2j@~$eik0!PkMeGf!gL13w5RKM5xHfd{c;h8y(z`0PhS_=ga2KlpHPSB&9??*Wr!zdh(rOd=i*KM5ugQ%{;Fjdu{<58MwmGN-z(@a^D{Os5%t3_l9q4?Ye*4JN+=CO;1z%Z{1MG=!-S{9|Yc#u<W|k*J|DhQN=5NwVK@^d}|}PljIslZZ#cPlIV(ns*=gesBu&vrHG^SHa}>z~r~UGuSaRnZ`2>g^z}ar@&`|hhmKJ@QYxQ>~|6UiAlsW;rGBKV(Llrr17r8r+}xRM&?vE6rKW3V}66_4*UU_{2`e95qLg3W-ilbOcUYLAmZ8Zx!{Qy<1_djFiG~igZ{)M;<@mLU=lI)q<PYK58$)Gvr!{+s+$N;15aX_&J+iq11A3*Og<0nXU9Eey32GKeiI`83jP>OH8jRucpR7{`^BL@F^Tvw{Btmgn0nGYX}me`ufSiSM&?v^89oU-jQJR*32+aXd={AeQ}Ate%zdUyOsVj55b-tmeQ+wqxCEa7Cdqyi(4Uw@d>=jwOd_V9G*24O1HT5oh8meuT`GJS_zcr1#>e2Ffct`D;iJIhQ^Dlpz!%st*O^W*9e^K$PGFo9s5yfg8sh{!7EF@;V$q+NM0_1S6-**N10MyZacSNM;C;c}n19676W$+8J_1ZW7;Ld)PBHCe+5!I(B0dB^1>S)%_QHFDNwQy0^d}|}pMsA7lZdG&&6CFK4?hGxgc_Ms-41v+aBJr8Gj)M~045&@ChrYSX2%?1+7?Rx#w2_*M4Sje0`_8zZSXE&lI+(7{fSA$N8kg&Bx34G^Q7@UfG2_zQ6qDz^TJz$8!>Or6b)|&Chq|z?*!h;j@iYumT3w63y63Fd>42L##jrF29spJX!Iv05$}Tc0F#KRC(V<_YX{!|-hdjJQ{57HBk&3)`mck}ht~tw05^m;1(UZ2lfMUE&5qf~w1{aYd_J@Y<19kW3e?aTi{K5xB-yVa`V*6gH^SS4NyIDQO~EuS&3h)i2DmKq%1l+^wZP<!!Q>6V3)nHsm}W3dginKrXTz6)Ct{2l@Ty>v>{k{2iAluE;Ell~V(Llrr15IOXM<;>M&?vE5ndKtgn0?3aCk*9c^xo$1o$&{%v`4NOhe(LAz}}FE_f)$7!MBzlVrbe^d}|}&xO|klZdG&&6CEf2={<JsF69<4TTp0zr#EqQz5tuOkN&LUJ5*x9W$9}2vZ;U#}M%d_+)S&j4=dW2uzaw3ZXwSiFh)+JeWjGJ!zgao(nz#JOVW`r@B7ycfbRf@-Y4o{x&!xI0rlrn7lZcya0F*J7y$PFQ)GB520Qdrx$7lpoYfi1<wH{$$mM|pO{2E5?&lkA|3$G1Ez6l-reCD!6D4kF}(%P3?|P7CeH?Tvt#-(b!F-Z?+g*g!25waVvMfvx4<OX?=AEvCK308=K_<6sVB{o#>)(k0mq<5=2X`a9s;h<paN5Ecu8<YrUp!<;B~;IP*V|J0bCK>0A3&509*%N8(f#E98*pByWsLn^_WV)Yk^CkraZhHxIDNXye_yNxE8!7ID#phsWQA6xHMBWrlRml;G(E04G#yG23LbefUAKk!7GDnFqLJh3NH>W!&E(l_Bjc!0(POM47_YWZ5g~Si@w#N8aTcNdJ|`3`iI^F@V~%+GJnmKHAE;=K=u!E@@xTL&x(Ge%*Zk_z0LH>5PE5d>~H2-nEwIK0R9_wS#S&;E5Duvz1~J&%HGiDkom8M&`*ZQeq&0{^8dj9H3a{Ly7V}Pj!h4xLtQ%bB@Si$!Vn(_@}I%KF#DZ8pCLja0oe=WFL1p4I(aB$AiKrz3Dar#Mer%6n}+!Mt$^$z>dwF)gO}oKOW<d~bes>zk{<(~Mx7776ugFMA=6R#V(?M$4frGQ1E%|6^6TJl@U=(q8{i}8bsc^K{0M#h@I~MS;DzwT;59gYHT($p8}#}b?g!t*{BFS?fFIzPTkt2~HR$Jq9|M1beox?!!9HBWHE=n{1>hy{rQj7zCzvc~8M5PeodQ1rP64OEFM;Wpl}vY_+sJOCW(E8N_!^G83cmz?$n+JCyNzBC!C#@~D(Wd)j&WB&%aEmF-Y4P5!OQSE75W0%DjfF(d>Qx}#=8Q)9Kc`UHTm5Deu&rP_rPcI^}En{WLJ=%gP#STN8JVZJ@6{b>pUd0vpAn~@RI?2HlY3sWX;)Uz6aBL@DIQ-Ox>AUz?*?vGetA?gntD7kf|k;8{P`+26u(G1HXr{+QPd8a136PcLvkknq!>i7~@0Ct2^e>9rKAspC0HD1MZHweiSgbkI?5MeEmas4{!|5yED8En9iXadUQiyH?9wHdw4f+7aZ3S-U-|mU+Vzx2=0Ws_u*~8-SD;c@b|$TF{cjjcHoYv>k97%F2eMj-Ty-HXW$>17iRtgydapo5SX0miK+fMYRRc@VW<d>FM?x<^D}+N>hi+B1%J=H0Q0Btd|>jtU~;M_ruy$tOHO?YK>2ZeejH2Ogef<Z3C{`6!_<`N9e5*fBYgcGcusI09N!e)1l$zd2yTKKGv#7x2+siyV~S$R4vz#!;_KPrIly5!J__C#90iVqHw6FA<Y9UR{|x*J91<#gE|`1~m^@>s;NNk~9}w|tIDP#!UK5Ann2ccZOyH?FJ`VmG90#5Ur`mb&OkncGsQHxXZ>BkL`o#_6znEq){R^KB{ulgKsPF|~@?~K1T%m&h!ZCkC|6+`PQ7eCWg*XE|7nnRZcn*$R2+sh{fEr@*<spJ|(9g+Ct3!l{H^WPUNyNM1Rlp?T!|>{060r|n3rr$D0gnKah>yW5gGt1P;Kjit;vMh;U=s00<|{&kzm3<F6K7+}8!FB_2e=TtD7X-~B)kN;B)AH^9JmU&I=mvdI=B|REVvdp0{$*I0$dqh1Y8+h9G(YU94ya`JS#j8_zQOK>qEqOlZf-e6Tl?mqVQc{5^)LmJ}`;69Q**7L|hTR7fd293*QMQ5x)!H3MLU3fqTIuVtH=lEAg6g;xNXAnbw5}5pRK)0h5ULz^j2t#7E&Z!6f42@Y-M!aSFT!m_%&BtAa_yN8qKvB;rJPK`@DU6Z2Ie!n5Nw<;3qW<qs9-9R@B8cYzCo%fQ3IWx&<o6~NWNHQ|-OHNmyv<-xVVHQ=SeHNaKj#lTg;rQrF%rNHvs$aBK;f!DHg-w-0sn?#%+z8y>=cEP^{lZeCN`@tmQ3h;wq5^*JXGMGeM9-agy5toK<1Cxl0!Q;UsVtH=lYw((K;yR4$F{OqG5uXVWB2I%xg2_!ViTD~k3QQut18)K*5#NV51(S#$z#D@}#P{Hhz$D_^@P=R#@l|*OFp2mQygryje3tpi5aD(4nsVZ1@D@zXncfQ(*Q^e>9y}Uc4;%?^4UPnx@U~zR90hL=jsiD<cK|m5H-)zYHw8C_w*fZ>H-fhUHv%_=w*)r?H-NVQHvrd%*9D(u*Xn$TxHcr>_uv=7B;siJ6)=goHT(vcMBEmB3rr$z55Eg05qE&!1e1u{!LNf!#BJc0!6f2V@C#rPaZC6)Fp0PY-Y4Xz@S1YsmrT=`{(;W~{{v1JDttbed<mF5bEx2#IOb1?_zj%C{sym!)8m-TVDc>B={SBC{0(>(_;Wbbeh$w9CSQu0UzuJoJ%m33|HkwSlOO&S_&3!30{<2Kgy~zRui;O@KQjG?={eK)Oh4djPf_<hnDX!7&%ocJ?>F$r;OFT16Z~gzyXcV6-0A*r|GVY?{-K{Y4CQ~mtRJav(Fr^<Lo?&Q8+O`7zeT^3%+}AL{1+?+({Cym{|9|SBxe'

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
