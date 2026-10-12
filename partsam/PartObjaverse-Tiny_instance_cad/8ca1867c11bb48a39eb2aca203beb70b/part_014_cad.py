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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_014.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_014.stl', 'source_sha256': '58b473a61acb11826084da88ecce7cc34695b363b7b097ebc6e77b0148ac6458', 'input_faces': 759, 'input_vertices': 611, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04493622109293938, 0.1375536024570465, -0.05506409704685211], [0.05705117806792259, 0.27737829089164734, 0.08411631733179092]]}
GEOMETRY_BASE85 = 'c$}r22bdI9x`wNVBnXI-bECj0Ip@$wQpuo##0DIal7^tDK$B6C3@Q?aEJ1=GpdizLA`8qQilVS;>jhENU0qoWYq)hzy{D-9yS&eR?q#3<`QCp0r^2bwRW&u+wL^}aMJ(rE1?y=0YQs-7wk%cots>UMwDj@A2d9mzF>1`DkX1-~_0Qyz&JT3z`cTN4Xg!(waN4-R>8VY^sm+EoO05=79Wpw7eEPsq14gGmoThxcfsc+$v;DYX1IMJ<pYLo?yLPp3-MgxVCx`!!|MJ<35dA!~In&NqmHkIss?3}=BQwB<%UoUB(&OVh#~%yoH{SHeS{2)<e5B7yN7QF4el3<6;4@aPU*hdI^OgO^yZtlEuJkScj$CUq1AL<6icQ{rclkxX@uuIJweUsna>mNmTb&u;tygwz@b<gQBl_L-GX2x1X&+yF|7rdC%g!S*1AMH`m-Br6#c#_B?8lq_#KxDO*ULG2z~7wl9k4XeZ*8~H>*JB;Swa1-H~r(bEZ6?bYyN)e=?^dbVVU-M8f%|eSZ7_3kM%3KU1dDIkK>=J;_H{*^k?LmvQ)2E+NF2A%ai2I@?5>LMEj=;WPAIQJpEQyH^)y*bGFykH5-C_d~EA2ULUU)$_nZ?-t;G${khn?T@ud}Sr_CZGgj&T$P29<|J=L2@sZw)PbB62MS8wp9rX7L@AmI~c2UssNN<)W{KtfadVl<_#tCn~^s+xTV!_Fve&c0-yzP}!-tm;)jHmID@1|r0^&4;c<26zpf2F!_e@OD|50NG-7HFUM9cQ~&zIjWaziw^y`3fbo0{e}pKRRW|d_4|h+WE#)dNV%8N3K71GN|8p({HVNZl3nnX84vr$+JAJKinrPu-|z4WBC_8t$aq;!SCwNjVEu*4Di<85?j^hXpcwc>gh!CWqbEe>COI`IMG1+c#nVi_Gjr$f3*6`bM$o9oH_2@zDb_#>-tCc`}Q~K&Hi&^IwO4JndHs(HU8NNS%Lk=i~jiW9a%xkW4v6R#Ht*6oa0}d)8Es^M=K8U`FPP<PXEIAS?#~7ye-h@9IdyPRUn7<;h{yecfXH}f4!XJH+LBq=<_%3>-CAU4IO{yr3ryP=ap_=pK-WL;PhQDrk_!$w{JNUvp$*a9UrTI@y%Xu#>e>B2bX7QAI0B(d_tfP59sdm*`3b@_8TwzKkw`KY4g$peMZ{>UZ2rmuy4IGO1?VNw_bziZ}NI~y@Yp<)4sL02l@EIhqw5qZ}x`^)3*hAt8iiGxSrir`}mf5`uMd@w;I$kz{hhPo#yqCYgYsNjhFq2o%g*P)Nj1(H{%f7(CI0a;eJzQ1a03W&-QY?*uF_#_KWSC<k`N)%k3L|>yPPr`)733*E8;UUU>I=0UtR&@>Ed2@uoj<;Hcxp_d=5AyySZEy^!S1_rmI?(|!97=b0qWc_y6e&@}J<Y|dBGTd()o<n{9WCcWv8{x)Cx*w2sq$5VKBJn@k)+nx&QH{Si8J=7-V+YgKO^80g>oaL#vTHog+`P#kadVRRT7RNWdwAeeHXr=3c{jL}N857da2F=%avz*Z;&11gf@!Z^@Uhf`vf8k?o#>BkdJ?@6w_N4Y*_D|LG71s&Uo9l!~>nF8Oy6%$RTz45Sue+o-`}5@$la-H89r2d-t7hr@8R;V<&u4i1W7qcu_8Twz;}_1K@s7XrvDUx7?Cp2QQ+l!gBzg7+<K_Niyxf11JpIwk^H1sJ6xZR>yVoIjc^xjj>5ru4ep2s`zm)Thr}Sn#jgL%Dc{`}zc+(%tS$vXSPV;><chs=V03RzoYM!^>-Ty_u@uolebjCzI&NIK)<CYPAes_>hRD0r8ogLEj_eOl*7tVcUlU<{NeC)mElYRc4e%XQjc+($kR!aMfpY!PBI=Ug_)gYfStoI)Mb7dxs*M9k}+Q(-9uKObet7vbnzH-br&ceIf1t0mS@!LWD#=FPGkL&bxTw-3?v)*x&-d&z$N5^U}&i}^C^L%{9Fzx02yY%k;AYR_TOK<vPg9nW8ZN~#kx(4}JN@S+bo9!t3&32?eW6y;ldjBcAUawcQ>c!1LK4atD*StPDxP@;#rFX}3WO|w&hxGUT+gEsZ`{J#fo!<`XH{RX8^L~%&`4-A>&SP7az7pua9lY1;6Qf)C_Xpuke@2sjy|jOFm7Y%c@`dd|K7RO!uRofzjq`n%a&32zkLAnb^dByJxP|3;9@zPZb(sM^nt$fY-hTJFU*{<sGXuPwj`4proyfPhZS#8b+)_^8c-b$vuk>bn885f5^s+zl{&3&@b&}`)+FefTPwmZhl=S90%JpNbzZ2MxPwKz6@Kj(wKB+$~Gq@k0)NhV=>-tTZ0Y3iS;Mu-@bG*xbd{V#pp8E9B@tFZWx+k*GH_qmJO7t5q`{i}D^yd6&yu7ZKUiN2HeqQ@XgRgwYk@4>N%J_%wbH1lWlzuhHoAZ_Q@x=-K{S|3etC!w>;&?Y+9`Dkd<2_#BN>qDsUNT;um!x<5uT4s88F1W5Z;m75<#8vy=?_;LF+_j<S7*JyMW5TXA;@P`Jip!NbLGqm?8m$PO~24ye!mzmzh9&`+spc9$cUES<Av`#>0^A~xn6ufO7Hg18aGn=i#?s`uN=HB$eZ;tK2rKWf&Iq2<Iwx~*p>muh4D$(8wWOx)BWOlMtXOD&Mr4z|Gc=qlHNVv;^p;~^zQd{;&JWebzRshH$i)GeJH)TK8zL|KEbygx&D;iz5X;_T(3%R`oo<zOw=i^pQSg~&++X`9@pzv_RuNs{w%%Oj;_D3JS(stZ~7xAN=?%LUED87Z?6B1m-h?OyZyy>J)x(Q_uMJ(eki@WJb3qhO7t6V`V*=7^nJFxpOW6aPQ%OlDe2w)YSRL}-Q@kU^s-;xFH4^^eR01my}2(oUfwUeUfeGydG3FWm-oxY%lqXdPk*@Z!Kr$Ci02#9o97#eGA(1i{fFl&(wpZh#>?k0(#wALd^K<J*dTA7&%{=@^G(M*7jnHA&m_<I7%#`ucsZU)Ui8c7SJIp1jC{IKKlhc-_oR1!uZow?_oR29?_GIQdwCrtz4=}+US3B@@7~Y;S%12oj(A?0<au5i*<{Vo>m{BKOYg2PUOpd|-o5T^yIT9`mhR4d*465}^!$f)*WbhPIluJgIlS@mIluI>Uq0uTUiQ2DbLXC80zJ?F6Tj}6>DylXe#ChBdlTd3?@gpPzc+EGFMe+#z4^UKc;_3l^n8m}@r|?b;pR{J$A9Q&vwh3Y@2!ka`hC`z{B!g;zc<78y(zu<9&vqit?zqE`lSBncV`9m<CFR;oyiJZ9=z$#_^I}spyMLRb6g~D+3HM3{Qft|oA+Dr^0+o$9>0;1&phqhA2`oTZ_e|vYFW?d?N_IyZ#x>Fap_r~PfQ-GuNUI$X6fTM<MX-Baa#74=d>5U2bbP`PiAv#?d9*;rFY*0i4L3ZYzO~)2-3Uf6TEy6L3-04Td{P3{(Nw^Ua$DbDQkng)nM6rJ-scTEeJX;jF-nnqJKqwzboJCNb=@ApGTtF%j+@e-TMf<ydIO@-Op=`(_X$OBfUF5c=?`;^f%7W-#GIX*Td4g$C2^kdRTh*`Z@0(+RO8Q?EVIebUskRw|_=g4$$5@_lbYM-8fJCr1y)2ch~E&tB&9Ifp0&T-rdhL3p>|qch~aGH<7QS<KMgLe{V#1cRK4&Ilng>)yB7fN}u?;;JP3m`#5ENkT?6YRl`~mG!D|czkj?|LHl^Ey!w0<?XqT-{v03Zcya$Ly}KRp^8QzPxBvK5=e^4Tza00DXU3cv+FL7n`NlbX@hfLK^8GsL&HFat9M1bzL#G~h#%G|u{<qfUb9_5X`}lxuD}#KZ#gf%JtG3i$J`a)Jy+1NuJP(oH?XTU>nQz|QzU?l(+3v2NJ;paa8G9af{HWRf{aJYTeaN4uILjm6Z%p!xXYAR8<5xWE>?coUuL<(;>KC1H&i-bp_jotUBfVK3tILntTbHlD?cEQ<tC}p+eboy4);G5Qi1zU|FZi}^IBn~4?ZtbfN#3m2@-5GMj|<bE<VC-HuQkb=^Z(k4FKTa|-*SH{y}3U%K2mOjvp-ijvN$uqNBUn~<(vMf@0|Nt-gA~desRqbZ-4mDI?i>)r0)7TNFsf@(=Xm1mfn3I*m&{&u=J)sGI5c!{Nnv*>COAh#>@AgrFZ+g^m$3=y3h3Ymo;oe{~#aVI(fR!bN^*6IIrKIkv<+dyujNZ@AkX)v4xAKX9jpHSNc+4zj=OD@4~Fi0B`jyw%oTo>)*)=n!fRJ`jI(PvjdkOFPA^k<8pT3_~6a>B=(ll=f!ybV$S#bp<OG2e0*qht<Qhe{&ZkJ-t@;Olw0ZBzPvv#y?KA$c=^7)^rk;?c-g9;<4$__ITc<WchZ~V&Yg}p?xZ)zo$>Oxi=;lRzh|tykDm1U@cw<;$BK1z_UD7s(}R4h;qCf4T_R5b=Y0HlUEg#P&xO`{x0iKx)2blvZb#$UUP=98JBADG(rNv<!9U*;pJ*TXc&=~xr8mnTuaIwD&^Sc9B%Jr$M?LQI8B2e4{BO&A)0f^%KlX7EeLjwd_WGt{y;010|62TAiS*|0M2wezS0cUXkLH-K_eXhNlHMG5t{3Me>CJI%ygV;SZ_XR87w0AE&3Vb4uQ)GBFQ+fhOVZ2bm**wv-Sg5zDVx3HZ2oRYdh>Tf#>>AmlHUEhq`4imk9<4W8Mj^Mh6MRYr&Tepk6+#C^#3~EdH+E8*#6Pa`1(gSa>kkWlckT(TD{QMZ?;SEJx^o?_(;l!i+ufa=4Ay=AD=Y+d_}VZmme>eKazJ~cHsEn&G>{<zjpkd#s1^2Pzn7U-I_nqcl=6kj^D^H?VRWC!+QJA4-?L7A1_n%RG^=`$>$S44BZmcpIAK7@zqcG&of_t&ij>_{_~9RW;u;F)3;vv?2$k(rsFQpUrndXYg2rl^-7w)@uolA%Xx3{zWx4j`@GNApmDHT{NsQ2ay-w}e<kR6k>2bN#>?YHdb7W|UK}sdoBi4K;&_qX951dH$BXny(-+5!^m6&-@glt*pRT^Y0_|~d(Dfn}ElX8itB5sZpyy9Ol~n&s2LB1@@OuBNKLKr6zw!U~Pe9)cS=Mp8&XHO0$984gb%Fc<z5stjo`8?p^*TTIIzOX$uU!Z1I!b1F_!ys$(VInm%rdCyzQa7<!Cmky-v#Eim-)TP@*F2WfRDpR$!s{ApH;lrt~cyj3Gd+ZOLpzFYd?9$!z=l`lHN1?>`VOoOZ4ub_A|e|@B#7+d;mU1z5ySDUnh6KJD8T@dr~axUb|Y^RnV>ib`>Lw!o}cHWEr>=d^gz&ZpAbe-<RUdqczjKg=wfP4i|;Xkfq@=a4WJk+?r`B?#4XYkgef1a7pG>h-s@V0T+i$lO^Gj{H)@Rc6Dccx-&n+o%q~|c`I(u&)h@an{s1}yD=t(80!*bF}MU=k}L(6gxipJ!*?^yHY`JXmZLrMRNU3Bc6N0p+rnM!y5Fu2WDgH_<#Shhd+@Ve`1vmMwxv2S&-QRfvIpD|?oM`wyThHxws2dfrFgo%kIt}bEx8U}3m+yk;lps8JOanz_2dS4Jv@_~1<!<=GhekF&B&&3Gq^li4lWN@Aj5D4xCPl9ZqB?~Ft2H>lgh2|IyjR&31`Ab$kXr<cmuf|-T==c=fJbz7R*;IM?JC`Tn{cnmWPYL#mEY9F}MNQ0&c;)8Za+4-58~~E?ESw3l}Df!G+<XWCOS;T%Vi+*N0~_uPw}f8oZVK8@v@hNuGjF!l%h?@M(BEIUAnMd=)pbzq{|Yt2L##8`%}^2G1mCz%$_tat)jTuO?T)tKsS7G<Z7Ph3pJ>fm@LgxE0)(Yy>xko03i7Cahai)<rG%E=qA0nE_|Pr^watDR>7t9o_+VBD=ty;JRchxGsDL*%-b9u0%G4E5Y^2)^L5e2iXno#=7-j8PxnbQi|)4cffVv+sR7s?Qli1K3oy5NA`g0!QGkHE1q$9g>h1O(lc%+8CR93J>z_u?Vxg}XS?iV-F7mcU1Sfqs9nYFDncnPMwWz&!6nEFa0xg}HiW})12QAza07Tv$jP_iHSk;H-{H65i(~@62!9rGmR~J*d9oZ_9_~Qi2X}z~N&W-=C;V*4$!9_it5W<v`5yc}{3-bf{0YnTDVcyL*frj+2gwIKoX%&JJ>c$kjkW83avVIyu5R>pqd%ShK7pPIOk442dtJuZHI`DGPVR%#;REFF@B#QwN^z5rlZ`?St7^nDsvHfEg~yPi;4yGxvLW0U{=;(eH_Ks_ufc!7`^nMpXx2^ft@bs?ZFc<;a`Mm64KBiGl_3uo=Cex6!?*JJR;FjTF!LzPG!^HuE3aK&gq%`*iM$zBrT9xbbKCj3oi~yH1*=k=kGu@4Qk<W>0;~KI{*vh{E@X46U6m=tEy)Pn5^hblfmODHTf=QB#jVJ@;a2dS<X!Nc@U7%+@U8H-mXqIE4y*ha{ucg-d>j4<ev8}-zXk6hH^6(~^_1eZ<T_a8tMFQQH+c-+4Id@X!$;u{$#38f;j5J5TS88%ZKJpl+vXOIQ?*aOODX=9{0;t%W8+soD=x!vGYT#P*Ca>7HQ`!hBe)h^mQ=@fSw1WN52g4lxeq=IA124Zhv7HL(eP;2P4PGO^sm}g*mCkV%i)7|9irz=_%M0KGyOBnU*#{J<@v?4%)hWMDoclMtXFB)TV)N;IMiUAR95$lTXn`&Whu`%mttF}{F!Z{GTXYbjj~ziY}V~v@=dtBeXNG<DoZIYNB%S9a5?z9kdt3p4u1##7p1rWc?(<s&PC>dbHO>u+;C1fKUomY4}U>khE@I}<nR~pw;?Chx_wKQg;&@;6YP4C91rJE=Q7J#KUG&)4^>xKc9nVITi`ro2+jlNCM`HOT#&p8E(l*HFTpBPQXIYvt94RY6IP|TJgyd89uAW^;2dm6#V^>?eBQ2c<XAYD{olT3JaWKSsIOU9l{dqA;SiYv4#5_gV%_+c!n&%=2j2u=BEN!F=1g(;60F8RWo<YGu1VH`Yr?h2TyQSdP4U<2`#{ZyECj2(4OXen5sJUzobfezD?HGiR!h4Ekr8+h93@-8QMf<Z4DJv2C7Zx~;of8;xHsI3YykIyA0+F+55f<Sb>Ro#o-DswpXTHMxH;UE><2f68<TzD#&AROA-Ex2pX>?uWEtwS4AmJkl{Mf9+=8qIw}6|GRp4fD6Y@^D3EYUR3^#%skQLzua6R&NxE@@WtN_=A>yvlD_2GtOCC`{tV$4*gdd4u7F;;n(XUy+nn^b4Ks*=s&=JZshN9AuJrxgE6-UX{t{4<#ft5STOpZz`LOiz{K8svXqRf?;Tzrd;#S0R6bRVluc{5Pyhab@yHSe4?6<PWea#kZ5+!>SZlApZrcQhWz_4OXSN5_uiI&NwI@q`ph+dYMvuh};byf;W*bz?<L^WE36&|6n=!qvfzF#Z$<6@D#Wv*&MD3r;^p-RJb<T60Qx$$oX&#{)zlI{1g0W$VoL8iU%<kir=;CL%YtB=i#z;e`&kQkfq?W^z0$`!F%AP<Z^f^e6QtXd&^-}imQ@$!Bye1WNCPy{j)E!-B!T6$zAYn_yzKL_yssh4uGSu+Eyz6#dcHqEc_!pk8B3dgPW7p;O203vISfnZb?1|w}j`D*Wmf^zo~0%ziW(z;(?5XVzq6mFji&Zs%)=4Z0C33SIMRDtMC#^@jaH4YCGM-_Noe3W%~E9Z>fE0Go|<-c?doTZzMOt8{y&P2zWUBz2&4juD<8^ngV|hPbO=^li?a<DqI7uOxA`g!?nm5TnnB`{sd2juTzR22|208;t`Ik&9FMAUgKCf5AP$F!TaFl)H03}mF+k_N^?Avq7>grwue==gJ;_{(ymc<&4Oq1S#eKF@q>2FwQIOtbL_gGjFQ9QXY6`fZ4*lIK=J|jCA(ItF(Ds?+mLO^N8wfWI=*7pLUJ|y6giSoJeg9wh+GX1v+GH_p0H~upP#@z4Xd0BKV;9lk6pdUez3{`aBs3NrMN#i0G`Vjogmc(^$9*J4pEA4CkMkSABNS~{*AFznIq)z({Ku<IE}mmRyhQoXV(<Zv{g<dr@*TBG5S?bg;hQW&$nxVU5}HK;4WlWa*|<tIiIj=BBl5-@+ny5ld#H3@F2Se+x0M|cnGC<7^Qe9r8v#5MRqN*Yayk08KrnRxfEUwFQ61Jw(B8#9eUZ-hwKOUf%}sEVU<1MzHo1T_C9+1!D?AlzRYsH%(5!(Z2OLOb)pn^;OA7frxf2qc7#>l3vaWhwZ*ROl;W*+Z6-HSiZ_y5;4LhZ;!o|mVAp$gU9{^nyWS^rh8%t$&P6FMPUeMG=7($BRne|Gl;Wy(RkN##U6shHa8-ILktN_ta7nTNtTG?0GB>O;4_uJEnNoZcnFs#FUa!yX`hZmK12PYshv_O-nV?_g-(i*K;1A$;$m4LFJVGhXB#*<H@Eerk*X`=sA(T=i$6x*5%HQ~>e)nnl{!ixRPx@a)^8RG*Cf1D?le%`urJswW*#A=xARbU>KI^{$X2XQ4'

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
