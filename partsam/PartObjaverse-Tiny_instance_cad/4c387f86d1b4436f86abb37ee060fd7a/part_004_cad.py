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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4c387f86d1b4436f86abb37ee060fd7a/part_004.stl', 'relative_path': '4c387f86d1b4436f86abb37ee060fd7a/part_004.stl', 'source_sha256': '66da074da4682e198084912ac89bd287bfd448887572d7ac6f6698f225858d6c', 'input_faces': 938, 'input_vertices': 584, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08105485886335373, 0.21238458156585693, -0.0789225697517395], [0.0805150642991066, 0.4999997615814209, 0.06171098351478577]]}
GEOMETRY_BASE85 = 'c$}r32Xs|c_w7$;(u5!=-5hLyQbH%RoKO@j5Je<NJD~=p1QJLHgj`T0ASLurb3?BZ1O-IR3E&6*5eU6}L@t7Wf)bQo|5<C!EB88hW4!U6W2`ZMcd}V$pS8=`w=fKUD}RA92L7vJEbXypw$;cmB#Iklj1hf@#SZA*H>TF$=#c?Np!)KkS7)~G^iFt}0AqwPs%oFUF};UXZDLk!)~|8Z8fMjgLx#l;iyYi@$gn<r#eY3=U`*dUKPD<Nx^Ld=Y7H9KuVL1!Uc*c@{~!M=n%4zSK4){L^yTjNKZoXt(?5HIzRv%x`p%v2)Hj-4-zcx`e9P!>Rp0(Fex1BF^SR*P{3}O%w;lL}z7B|||EKy^<Kmjf6%d8%-nxqR9rvu!`~mN)@4B-T`8!!_)i)|J&(GT4)84&WURw{-Hlh7YZSVQOy%zog^^FG;&**)H*_)o^yF%XA{umFZsqg&#lIAzMU0R3spWyF37>D+K+iHD050Y@*zbm1A!+{z8{wwO+9Wu0^_JiKI?yWoOoA23rzn=T8aNYYKA-`Q%>t;S^%Knr`ecnu2rT)DGUuyn)rnWbFu3E3J?=FC!+xfKCx${=7gL!wZ`c7_l^_@3UHIIGwbM=ku_0j+K5!z4BoeA)B-$eU<sd~TGovzIDzWT1$T`RTy%?(;V=Z{(ceUfin8?5c!?ZWlCuA6Hy{(nr=_U`vmv<}A2X~=VBr20-|gx0}xV-(v@Ro`wIzd~NSZw!Gy?7&ajKEz(8_jRK;uKVZ_>eHtF<|p}1vzJh>8=aBo(Ji!Z7^~yxT(1rP;TiSK{uvne>#reCbXUEu5n|%He;?PsXZ*Pub!gLerLXULFx_wdSby(U-}-&;DIKqtQF>pVzqZr=R(-R5l#Yw*uLa2e`%3ja-O8=^^{wB3M4lE=%XQqZy@B>4zS^hl-#W1h<M$%^6BDw}cRm=NTUhs(&uJbz%+mh2&Ky_YH8fN2*VWF#JUp`n{>6OgPxElSuJiL;<hgkDr1qy>W6ZalINbNe0@~ha5}|doa^66mAstZ9ww{%~zH{NI=J9ksq4U`|`3Clti<NP|%^Tyo$1iF<jPs38VqG`Z{O)60P^WWM)OT73uJrY-^P$M!AbhFT|JX{jAHGuSV|LBZeZW52nRyBz&wHslZ=EA=;JPu@wY}ZN!hU#ox2iF8Bj#u4?6tnW^I#q3VbARKzP|Nv7v@Qy!l>8b%ypQDd)2qXT5o!iZ-ms>d1)S+hCJsZQ2&r%t%K)ae_Z!|B=Yo#M!yeMMV=vTw4d%y;n;7p%cB2hhn&#%4NTPMz%A^rXA{)7>sU+l?;kj>zT<gceZ%tTxVZQA$GCaw!sk9?{Zw)-=GSv4{OY#%%o^mMf%Xlm>2;kSC#dg=ox2ZyF!tL$Z(tm9Rvg#51smEQ>&HgO^Yd5mYX+xlfA$1nzlkY}@#?=v>um0M3VF_yLw|bj(RpU?zJ>nge1<$tw`x7j|IEd@9Gb3mv->v2eElI#edlzfw)eCxr}N+1RTX)D-lx7%$JBm0yGkO@=`i)p_jA$joma6gqZ?rU^h(8ZVP_`R@!h-nymNJGi}Bi#1piddG0k7Y<JP=carATHS2xx7IJMEQQ`^;d8YXL<ZKouzd%8LL-`&PK$=rZ-d2%M&w>q)H*LU43tMkg!@dTdZ->-z9XXyNCI2rrY_i^z5TM+qcl+$sszZ;^ybFT*Ge?(!-*YA4LuY-BpbeGO^&v%{a*Twwr7p3*Lziq^RMr%L4=LBQ>8SSrgdl1eQ;Rfc@_T9LT<7KqHt9^Kyw)<ua+8=*aeRn%!v9|jr4gRsek7^z2wAFF+Y)e9(BTdyeYF5+xGPgB?e{3Jxw@Agh*czn1ak8)GHzRT}j$3bGKRaAe+q;@1<N2~BQ+?}12<l%g5aavx7WIvsfm%;@zhunkujeAq(Ur)<ecSz2lKQSA@1mbAf*1Ju#?94w9&p|c#JOd25c1sat#z~B30B|Sd`tUf9KLl#>)a+B&;2hCU|+v8T-$rkIp(I!Wylkab7rF}m=Bw_&>w;PJ-6z7bG}T2e{?qL*2Y|<uQ&Eb{<9OYKZG>H^LS%t^<772XnX6uXsqXq+VGD#@WUM)Uo#^J{$J-$`>oRrXLKF7PJV`Qv2(RQ?hOav-*Dp`%jcT2ej4_t8;el422ptKevz~k^<0nhUV9ts|BJY#zIC>`ZpHIu{Sf3il%w@@w@<;ouy!~0iL0je(`aMjT(M>@_T8KX*iRZp<J_`33GM$njdNNX3+rulXY7lA{iyyw``+qC$a6GZ>+{b(Oy8Tw?3}UI-@kzVylG><SkYhSyK|+Ro`1}+YFH=BLg61ejd{|^#`9o#ZS`GO%cDO$Z&=HM)VHqQ)I3&iNB2Er*)2ExlITyz4D6H3uBvaGTC3w__qDJOEWL>JarJrh^K~2h!qP49&yLmk<20^>bDsMt_`jv{ToJ7E-V=HT`@!WG(Vw0U&H*hl;a~Xx=hfzIv3^<%QQvhXOnsxnDx9mEg|dBT_$_U$|7MS{uN>Qkb=t#)`PO8J`c6(N#~1G}>;^-y4lZ>#<vV|jh8@&*T{!G_{;}(aqWz(ZT7OqpN85Yq2ci9MGc}JpBplDR`eznuzTaYTPJ3$=#<$*vg=n7wzlDwat(B(xhjnT_o-h5Pwf^o}N$NYEL0V^5gZHs6YCf8;?SCD8(sy1NuT4|mb*?1(-=Hm?N7a+yUpRnsSAz(gL#p>w-}!YV&Tp@~u`a5XME(nV(4OxLTrbz2r~cU_?T_0ohv(@_CDnHw%fkL(-(K(M=S<c5JN;5{PJLlos$Tc(YV1E9S7DzCIx|=Q{FhVeo2}d{e0}R&aqW*$H$vBsX&!)|cQDuf)CpJLT{%g8<6HpRH?(oTm4~4H;anX@@B2Qh($zV7-RS;$POwItSgG}>a9|GR56(sIZh_cW%csFV`31(SR}{|E<!i(L`6!;td~Uj*?KxZXpDB*@!snM&CKSG>9qLfa)^+PC6QsT|qzcaSamK1pUqAX2_#>0mH=ix3zLhgxuWQwcz<yEs>MYbJ1m}mkHujxTN$R^!{e<-%VPO833PpQ9XI<Uf>iya!GiR#*-$!_E^8JphM3Va6bFVWpL;GVt-2wj4)p)-%DtNWluXsuIjlt*kYX9TIwY^j9zzp?Ix4=4Wnu7NoMbl>BzHn}|UbS_9F^hIU`%~W>d!nB+)UOUkks$cTuj+ky&xc;$Io<$yst4m-S15Bj=EHFGf3&Urx1UObKlo|Xf7ET%zhJ2P-sia8y)ouLedqYgI2ZAKy({0e6x3lm>X2{(;~NkP|K!IwFExzUd28i+IL)uliL10f&cmE($X^NlZ|lK6Mc;L52gdj94D5psnomRBR>7}sp>FrTn~MJYwiovskNo!+sc#*5Q|smlFNeC_$eFD9kA8yn-f9)r=^r_t`_0>=a%;3cSGvO=v`F(?i7A@j^?S}F&2uap=aagrc#hIHj^DvNZ0+d2>Hf9*ME&zYd(qD%Q}erWaz4Yj<VStRW~lFECw_|SjzoJ`l=}8hIpdILIr=m1658*oJQj60gZ7`=YqkG_M<u8~u%n;v?l~$R`Nv`$Kii|e^<mQyzT@kfV6Ia?;$E!!!x!NF*UZ2Tdfkpq)px}XP~V!7{e|kln*+4{$F((&lN_aaoW3{vqd(o@Ps~u?)A42><WEBW*{Pb}9dWa_`myh-@0t~b>$WS}C-e!v-FXuHf93IfP&6v^3D>m-75ymm3H>zMwTaQZF)!o3QtU4<AKS!+KH+|y@PflbpHLs;{emMxpHNTJ9v>h2g!()E#wUb6X}pHENyPm&$LBUvob~$W2|tWMf5xLf)2g9Ai9aNvKimBJZ~XAW*w81;6ZcQQj0=6zyxKSJ6I{15@_cUUb=?PheH!|N`RVmt!_!cQDK2eq9C~5A`Xi2GyryKR@0|SQGkyK9`EUNbWCE`HG4f1I!94NoNY>Z<T+5ntNqyIamJ`u`|MlgZUosKxud@H;^t$$yUZ11?{_EQP=MMP)+6TP8D|RgUGoi3v*S<M!3hrwk{N!-VpF2yYqR#&NlIPwp@Z+A|uYPhg=EI|3rs?Z{?URNpECu5@599u6G{$S(^c3HD_0K*$e)@FO(|?~gCS<|?*K@)B*}>`P&mYX6toe;ekuxxkYcXEqJX#0i^MIMSuK#n;o?JzJS6qYrzIi;Khr$2%^K|OinSS@n=dU^KApGGQ(H~bl>OXz@EWO^aqr9&`JlCeD&qDnR?#H~%#=bh^;4I(%TS?W>|JhY$`;9NpC;#~WI-j`bq{EN7hyEwz`uW~@ZjCvC=R#_!ImjD;@pVPuy7MC851)qn8l8;(&mRka*f!*kkJ9|Ec^l!!1R;MyHu|~X;2huiY$O?|&-}A<FuwlhKyzWhTwFI1?MGXBU29>a`mUHz^k?KAoM#q|h40<pMipM|=X=+0Vut!=S~~M|+UGkD|MBAo?e`r=XYoe#XV^vbGrldZ>#mZDdTz&cM@OKa=|kc3b2iuT481QWJuB6BU3llYYw1C>A66Ro6&LL18}XgcpE0*l|K(xx)Q^qBbw{S6|I6Q<=R2QWiK$q>%csNV=jT>jHOz<Q>CDq*pYOVGRvet?J8!Mw$t(T*xYGN5$HiXt?tIkwGU}Y*!TMTzZ9eW7`?+_Xc-EC#fc`uMKi1a##`>WPFdhf7F2;B;j_byvJ)alOh+J)NZ8(VbBiG`7xnCI@&cctahtI=fBecEyi)-||;(mvxV7_e(TZlY~`+et+y)hkrd<Wzo>BfC+Dzyl8F2CQmp3dev@Q2;dx|u^=E42OB8y8{zANIShwYAD()S)Ws5FM@UjjeSS`>s19=C=CImN59EsvhvYUvpa|eDCvaXsWh%Z`+9c33t$c?gO6frP5I6%>BOOVtzjq{>bt0M_fWbzdr~+zSVx;dRm@xZuGA_t~)4sx#sr-!{`2N4_$@+cpAIW?~f0l&gIbmvk~xPJ8FCPpjFIc)5quMp23ARkM&D3@{ew$d7Suo^#7a#f7A_(3-=TI+$Hw2B<90M*~|R=giV;wv28I=&IP8U4*jw2hGyt>&GW(V6IUMaU3boT3w~?|%+HT5E%Wo^^6y9gbM?OLUnA82XCEFIuD*F8HQl#9-ufFC+{hDC5cTOFtohB0*=Rqi$^qa0yDsLUeZon<{@WLCqkYUfm{(EZ$aAUi65nw*hm^y7yI5`s`ibwAjE|gUzP=Gx7V~7Ft^GHCv(SD_4#s7K2k+}IwMBbAkIcR)OZC2gccXpGTNsyqd(<~BXP|xJBF*E83C6hm?!X_u9`m8Ug>k%`&Hhx~?_2+W{Lyb6@U4S&`2?;TpN9SqN?q>fC)`7xA=OZaE7g|zu4}v39&Km+5x>;0|Gf+AYtJ9JKUe0{+3F9=#{B;?75B$;psO!ln^(7@eO#mczW3$%(?Ok_SF?Tl|JZMyjrEnHzU%4<<RAH!UmdKgmymx{S=3=*^m1R{81n<_JjBBOlbeh7qX%K04?cnM{VP@T8N(i69J{ArKK+gBc%LKg9v;lU>&9}-pC3@4NSD^leZ3rfr#0#`(89X7Zo-dy1LM*gbvLgE<N8h=ZEp;0i~Zp`{+^Mrd%y4e@%paJXSKcOWBh&B4XiU`bj<_4b^gas9FO}Qkm~1q=d=5xT-5V+W7K<C5!`QQ?1RqjaQMzU=x2We<9G+p0m}(NfBK=m&Yfh`o9`FQE-vhMcd>ta&n@n*ChB<)<L_iv!hGn9dEmLb7474@XdUbx*caS)_rM=>75hV9%vbv!=A(CiaNAK!e0^8qyaT@Vx9*)l`_ZBBdtsf}58`nya6Z5|_TqYb<Y3>5c^3QO5>ualo`-wz+;GA$ZzES>J{U!CPULydS`oO|&v#zZ_Lgm9eLf1r`N(_TSm)B`lNC?}KF@DPmuT$oMs?&F^9bYHGf?w*j5=taxE}MN`&O-+^QbY}kGhO?^r7MJkM4-}-J;a@<V(kM!0Cy8cISSbKLF=zr=9w)ZnpY%!Rk1t#8g3j<^=0G$u7_ZzEcD9<ip$Af3wg4<cXbv`ph>M`1vCqV1IVI^}OOKI1+hAjza&J=W6}kg~p<NW?}TFiyQN;;6$`fxP^7MCNRy<Py7ybi)gFu?LyO$XLKa?ll7i7<llz#niG}nJD<%WVR(PzyodU94#af}N5YS(iT+Pc(Q~#{bT!_8c+bfx(KrVe+lcmj-{j14^gQY*vTY6KRfBBb{yRmpkca0wXP%*Tvx}Wv<9ol(;y|sNS^O;g(fzSrmU#SpS7s^nf2D=<R<YmUC+@|%SeAl$UhEqBlQj(OSGlykr^Ix8Ub3s>L9G|R_jI0~hxf0sO);Ox=IZ-EcZqbgcY0vGFA3NDcFD77zv~sv<Nf}^EO`z7@a3r6r!IZJ=aejh_xEwd`2O9k@4L)W)z|sWlgaM6e*Vr|n1_9B^fNGIo$vZ}7J0Ou?owfBpKulHZn|5?%L?oQe{^5ebCzo!@<-zHkHn*xS97iTzP^=}g!~KLn%`4u0P;8$vVF(VU1}uS@7RI;guiESm)eN@yWZ0JxF!W+UX{*b{_$wv$H4D?N*BTBQal&AhG*mR1^SlL3gg&&E53IqT?*}YmO%c=F3s;L6Nb-?vOY#XXXonuy34$a&y6w*;JLu>FU)5LAWzmjw4Y(({nc|r;Sb-0af~zda}DR&vB<MyKl(E@7x(qtJhUI3h<WJ!Jzm*#^oQ@)tdSngW0(CA?c;~@eN)Cv<T;4;-g9G*RD54U-`dqg@7Eb;>bx?`o<ttL-!!_L_#UwAHRkyh*L9`L!gT}m^E{W+0qb<CnTkB6zVMqToVV_>)!~mhhka&(jn50p)q%hBeztFWyL<>fN6dUB+i%><55;w}K11CmnHaC~6Oo7S2VDo8$-cg`t25T=2g&%|Px*QHoOs8#7_afU_&lZJLFC!>s<t;jh|>0+3fJI|$izN>(A3Y}j7n8DVE)|GJl@|gITh>R^H=Y=`k1AkyLo+USKWiY^TAUo675G0Mg32^@p)XOp~$~uH|o>L#P{HpC&Ew2LHnU@{XEX=TRX3#KJhNiZ#}<lgWtHsx^!KbL0R}bJ1ZIc1Ajl`dj2f(kGY2NinH-~9DOTmAjT!pqw~!U`VIb$P3UJruC_OV?%=wyk(mFRJ^DGUkz!=1I(3mJAyD%;(+X!`oxTD8Jr{n@lVWCI9qmN@zq0jnTPNiu`2YGnp*y8U2Ifx@><{lY#_wHI8lyem?>pPw`Z=#Ty*2z@Ep=S1Y(vM_ozfQl{MYXoy}m1c2<pGXn&{U)aSG}jehI(3m>$9FhT?s}+vWWIgo~Ib?Opi&*7R-}zU$Z8<C&y?Z+bN9vok;D&k>LI)0{Cn!*_h0eU{FDXZkGO*N3>THjVK;+Kh#0pL7rV_F*?ZN2YJ>$U^;(dvxBKGdClTV_|$xI8)JnE826Pcb&9!-WoH%Mg4cyLO=Pt5%-LraNXG6m=7;!>Guux%+nlSyuWbO7&}_?&OFcieT4PZ+CZL}m(YGhMbtkeD+&F)!f}a1-IloZ`vzy`eZM*zYwS;aeeeF@tZ}RFnpJ!w>aZ94L#u54p3a<ANqyJo;i%hs8{b3BdI|o{@_3GHaMX8Z)!&HqH3ju)nT+4H&T5VPnT1f#jh3zpYxdh{zvD!<-+Gzd4egz`v97}!YaV;Hjq7qBb~c-zAx{+itl7Bk*KYOQvy+iOvjlwWHhvE_XBpai-~Tps<97>l)@{Umo{jqr&CvGtoXyCys~hgOo`dhl=WN~Rw@#a8FZ1*He$Z)Fc)71{B>aJKX%RvH2-@%JiTQISV2ECS?g{wuv(f(e*a3Q9b5A4BsM1(>w~c6D-`Z6NdFrjwej0N<$P?Qi^Dw+n`%qs$?q%e6#`e<JbI<d>cB6g!{1IBGxz|~rG+Z|zY?z<VbDisvGgQ~_+yY<vt>1bnsN3A)Ut(O!Vcd&m>Gyx`)H3QDJAcP`6&)LkJSN&Zz0kg7n127~q*jBUwFd1=2k7^IW@-)iI}YGHUpETB8%&L0`x%&5b*iC0^OL{Cyuvx(2)=~hug*_J`(0hp|5nip{e2tvdv%O{|7y+8!2Ry3iS}p4;Ct2uTY0~waoyUh@cWJV4%_qj*wWJc&ip;B!)^3u-h-YxKNp;UKl&Zi|MJ6r$a5O~=eg84J*Ky>?|tqY;~#X<`Mkgb->Hqd9e8N#br+mRo{`%z9|DpF`ug6_wcNGh(|vs_D-QW5Kj^CUS#Sk;b{4`u6BdZyGcC9dpXV-XQs_`WKjClqH5=o1X$$Y;y8Im5s$uZD#wPVg9K`%g4b|_(&4mRvVV?KIx_-^=Mt=&^AA)t7_Gq}T@6F@9mW|)HEi4ZIhaMQ0dqMiU0ndUmn|$Yk6_ldCQ*jnng1_Sk_9e@szsIr{)<B+J!DxRgbiCg0LTi)nI<=n<*F2tuZ=;_(15mf?N&344Yf(7z>`2A@2~EN8z!nW;`+}H<l>;@8dr>s<d-wBeXFk#Pi<8mbiNJXA_o&9=6!=+_kpJ&T+TLEgkoR>M^Q4jozmG{<2j6)ed9H_QKRt^#!_O>__RT!_-Pq!9(VxtMIG^0;sqI~9KjFR-Kf%1Zk%{|FJAyn}bCJK2qt`XlPP08e$2OX!XnuE^2R_g3#_c4nvy*lm{-{UzoUKVXe&3dMf0N(5dXS{!Yr6|<#(m*)A$LW$Ue}XWcr)g0cjRwk;=a-X;g2|r`4(VL(ERRl@MA~fbB}yRvewOAiS5r}-iGAP!*xydjo~qvhm9Qke$HJD{mCqgdRC0a@0`+GBTwRTt%F%1Tzz+XpUuAa>#1PVcfpU3#Qj!u;rC4Gv)CVe9_77X_mYL|4}RBSSIU@?8SeM5@19>1IU&AAUdFsAVw5rZMf&{HJ2CZg)F=Pby8-q8um0&>NWI4YzyI`ZeqJAz$h6Ii)zr1rCFFI~rPL*4(fQ=1<V6hOIn)_s(aGdF<f#nd3DnQXqDkZl<gpCl1Zq54bO<?t9L*5!PVGh(ZAR`+Zq5)6qCQU+EkX_=7iART@QVhJMGF{@{}ay75H3c2nk@Ppxfr=LL%0I9B3ZO5xdQnWhHx!v9kOU6axHRwhHxutYx3LF_SDv7(Kh7v<Zy=Y2h_L7qFu-zkfRvFiPT|a(MjY)@^pr9I&~gdG>z<?$HHr<Us6|-Mc0zQByVO2Z#5pzd*SWWjns8y(WT^#<P{9z#neS)(K+PB<hcytY1FA?(Fx>f<cSR7an!M7(FF21@<@j8U}`j3v^#k)xhq4sDYZFSG>F`kY%+w4Q;U*C4RUdEK8E~PkeZ(?T8vzfT!JB7hFY2|T7g`KT#h09GW8X*Xf5)~<eCiOder)4(N^So<S>SCTjTLM5$;IsM17kq+Me8r+?gTVgBng2{eawq+?OFdf*M5@O(c&XCo_aosnf}#>16LZ5q48IQP+?~za(!Wf6EZgqHZROZY5`tcQS-`8;{qO@PDY=sN2b+8_C<q>lwn!s4K{#i^<E#3mL+*sdLGq)5x>QQy9YIsT0Yf<H+O5V;I75)RAP-!Q?pdK!$JxwJTY)DLI1NgdtpoYLZ2ZldF&e8N!9A`N*OL$%V*IF@#G|OOQp&kV}!vGK4Ep%aKK2CRZX?V+hx#)+CG8BiAN3U<kLQhLJ_vl3SA7F@)bY9<M{;NUBZkNEYoxw#mI1!hNWn$)Y{TeaHhC!ZFmoWYH1i7_y5YoI*_|i>8vj>ri+WbtTnJ7TrW%Np={*KT^LXi)N93B>xXXcpr5qS#&pfA9+7R_y^<hx)uJ8`VI9zWYKNpZ^#)8;pNozWYJ~h<>Unn;hEHhWYO8=ndHwI!k<v5kVVInKOv812oI-@A&bV5hm${M2=}B8B#TCndy?N{2!~RekVUJIL&+~OgrA`Xl0^%VpCK1!2$!TjMHVeZE=hitAzYqXmMmI{T%P<QL-;jnHL_@J@@wR}4B-~k24vBe<QC-D8NwZ??Z~3<lRJ<<WC-^+9<OuZSn5z}Bw5rZ4<&!Z5bjOwMHcNt?oIB;5FSJwKo*T54<e6Z2!Bd-kwsI;-gPegZeCb<@eVbFEZUg-4*5-n@EZ)_h795A4B=N9!ZoNN<Pcu31~r&mnfd}Xn0!1hPUOXZsi(<@^5Q^V9ApUp#1P&=-9r}5B<~<^VF-Ug{ffMbx`Fx?`D^O;)UU{2@$Y}n5Z=WQ-b>v>-oyUwWe8_8gbz~>k&jW2QV)?2@&1oekC0DMPg0MNZ{)pE{3|bt<%1T^2No?)E=I1%5UxjUKyF5DNo_!GMQuoJKyJXl-;g0(jv<_%T9{mz{makS!dDr>XQ}7Nq6f%l$@>_>-%`IPi>@SpOJ2bcPNmKxkI#!w^CE>hl{}Syo<f~Ro<?0jokyO>ybBn@s~EzW)bGjPv)`Ev;e!m}U#aKF=UA6tsW-?Mskf;&$Tv6_Zu7P9(+uI~sTIi;Io{7RgzGSb8~Mx+;hNN7YBO>(&W~V*aD9ewW1smX+=SYi+KSwY^QkpMID{cwiCT_aj`OJ!LpUEp_)pF`nP-1;zMUoiNzP#i@1^b|@8f*h%Mjkm5MD}ML0-Xmvy>q`mmxfvI+Z+?^KUXkcq~JB1T~&4`Z0L~c>qJW2Q`u`8bR(s{(vDIPHj&XZA}g*zrhf0Mr}f_OAV$rA=jpcP@9mO@b8B(gj+F$-=?-Fw`c#}W(ap-2=}5!k|TNly%@rS7{UqEcyc`Jn?M~;9!dR#I-V?=LiX+p!sDn@sME-z3&>N*^BKZxsH@1LndCL(EQat=>Or#TuVnAOaFii@iF%uSiF}74T!Q<B>=7lnS3FNHL9W0Mu1&2&uEV{cHbb~BL%6!n-XUC)8c3~4uF1V4kRe=(A^a@0KDj>kj%OLdl^McSeD)gQ7pTptO~_5S*EDAcw_yl3rG}70xYsmg2%8MyLezZZeB6f$@wM<D4B=DM9J1(M@+tC<4B;)*tz^-q<SpbS4B^?-xn$AF<k{rU8Nx2=ShDB{vWpzc5bjSMKo;#m?oaN{5bi|%fGiqL?nLgu5N=C-gDl#N+?E{55UwBacyAJZm0Fcrmn<4gu1bD|A^dW{<GoC{3bhusHd!=;T#MY8Asj|+MHYRV97cYNA>5hTg)G{O+?m{mAv~Bmh%A~w_U>iEL#T1okz~<N$lkq7csMnQI*u$lg`7m5$Pk`Golh2BL!Luk&Jg~Nnne~pO8$;~h<b^9h<unKe1Rc+lX{0NDtp;Yz7{Ud5H3rtK(4^OtSm#g21B?OwJy0X_p(|H;UI=^QJ=j}_(}lu8nq<3B=<gH3E}Gj2;p1QQsh$H`-CNg?*<@*?^7$2D|7D?mJs%SurB;4;PGB5{4fCe3SW!=3je%0`4zIo5PqH7hTMjG<?9UL77XDRsV3RvUil(J_$h|)<p8Mcp~9l4$d}2-8N$1%Kaxeakav?eGlbKrOUR<L$?4=-4B<)C&&i@L@+9&YhHwlumMq$z97FEM5bjFtP8RJ%?n>^+5PpZ+fh^jV{0{kbhHwjNC|R^Vxdpi)L%3$Z<Goe52K5Do@QVy#llm%Iv?|#oS7r!Tq`pEHeVJU5T$UmHOu*wkTDWjtl*o%9>NDhL*d~ZtiyTCLjUn8K+L$aFMs7s57{cwSZ;?eiliQKsX9)ME_92T7CVThm-VEV^)Ht$tj~4!jI*dA;ESf|fMowf1PoPdDi_RfWAkSb3r%{)aMZY7bkvB4gcTf+JMGupAkbhtZI}G9d4B=m>7s#SF$-j{QW(XJIUN8H55$^M4$wkOz7{aeoYmjSjAAgl0{2D{}Icg9&i2M3;4B-L{;okxt@B704q3)qxA&Xuk?;-!h5YDDvCyU-9XOoXHgiliMl11;6Pm+IT2z#jVJn&E-(U%ZD!w^0l@c20)e1dw9`j9Lt&xw0{E&LKgIE-qMEj}m07{YHbghQz<$SwGs2xSPr%n&X}eTw`PpCJYLTKIQ{@Db{9vgmH|5%Nxk@E6q0WYKi;7v#kZ;hEG~WYJ0FndD@K@M!87vS<u>G&!0f+?U#qEZUXam;50^_&sVzvgkYH_sDNDgj-TyCyTZqw<I@Z2-l-FB#YK0d!HY|b*R;-HOQhbkVT&-i&h|4BfrEDu0#zaixwkSB9~?e7o`>?i#{~KMalUB5W)`(=pC}?-{c468w}w;sF%rS4EcA5dGFn+7swa*=f6@flh0Fsr(PysX5QZ!!nq9Lo76kxJM8yOhVVUx@FS|+|08NKvV?E}hVWC=Kyo1K{uD#FI77G;^?CC19M@6|;b$4b<)|-`MNM)!@^cK~GStds(Te0U<dO{Gr>SMhqR)_@CKq7{7owIRixwsqA_p*p?;B8qEPC4jO9<a$2w$WAMHc;&e2sjCA$*Z~iF}s&3-uB?hx#)^_#8v{H|izwCFcE&A$*k~e4Y9i`7ieSIz#v_LpVS0TkbzU>rt4TpIn|AL@rORPJN9m+K618+<+n6oNAFp+mV}-+c1RRrM^!V?M;4{+>JVr+>P8b;PE+3*rrBNKO&0`BS(>kGK5D_6Um|z$fL-gF@&d6XOKnH$kWLS8N#cn8_A+O$g9bl7{Xsse;|uG<gdsX4B>SQ;cpni|3lqR7X5|%Kji;1gmbBXlSSp+mdn?|0Sw{N)H38UJhzo*2v=nYSEIg0evRk0Y7F6L7{U(%pasYUc&2;65I)Zk-WBlpoF}}9>ZbmOEV_s6CNE<MuciJ(7R@HFC9h`)Z=fC{i=HHJAb-ga{+jwTS=2-Rn!Jr6yge_%-wMcACjbBGe;M-lKY4#^`27z={{1)of9~x2H^=1V`sc^b;cpd`-zMapMf2&G@O9)HbmM;k)=*^%'

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
