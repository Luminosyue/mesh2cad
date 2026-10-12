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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_001.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_001.stl', 'source_sha256': 'b60df9b529d92bfe256c2e4bccd032ff005568ce89946fa0ccee042b34912df4', 'input_faces': 1058, 'input_vertices': 579, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-32.5596809387207, -18.018705368041992, -23.44627571105957], [35.401893615722656, 2.808863878250122, 39.49702835083008]]}
GEOMETRY_BASE85 = 'c$}r32UHbT^zH`~3n&UU1ktM?f?`3ipdce^G!c96SB>4+z#erh(P*sESYpYwgxGs;j4d|oy<fW+OYB|$*?WKZ$K$-U-g?iqzV-d?$6@ZwnKOIN6qa>src0kwlYa%Zi)|Cn94M=4q%2xatzU;e30>NEh%eEj*FYC7JLmK-)u+~ORI6??7p<Q*xXAY%;@kHrQo&Xvs$=;gp|&C&d-h4_)3!&Oo_)UWK>0UqyT^C<FOToswpWM$J_na67a3{`4+*smvHd^(bN_D@91E-KCaud)O$w14w`Te4|GB<CfOGSFDCf3$As$w_x$Q&{<&L89G4$C!>S#f7r|&P<lPq%m%=!}4UhDFp5`V6`)t2^q&3k`wuFagpx$WxTS*&uiTUY*GXL3$i&c=4K{L{U>OpDz7rf4{~zkM~DK08K)^KzUmM(s|r$jyj5#d$rmR^!~*^0L4e>*?;sxz=_*=e7dhds^kXUpih-bJ(v@{JF~{&K+0%JWY#SpD?8~e{aAyl9x@%&+F;(-SHTUTtAgp*7Hay&dqXXWc?lYd3j&uTMm@v{Wx}IMgBax=okI(+}De9Bd@FUfA>4ttaAP51%)ZM{pQZO=98P($KlaAvuTkV&)$Ub_eSimz`x%;fpc^6v3#ag{=$XV(|EIub0bq6Z;!Kcxmz(7xw*V)C@()}H0Sm=EefXHE`60N=eAm5oNFBxWVg!AH8ps<^aII}ygnzrczd;HtAb3c+#{$0@82p@B)>mE`oVTTy=jpfjk-xcd~CwG=J$@b-~6~auW6NsRV>5(f3-2^X1{YXZW|VT9AlB2LzWcd<(GO;p1-f}gn+dDU~Ig~xjDUc828ip8voLA%#aP7>j&F$d(F41mu`{kx!(p-t~p1^^79=im3H}#;lrhUfv3FwhWC*`(;_#2kBH>uY>ngG{`Xp5jyAcumsPG`dc@yr-(7)o$Kr0hy$;v&nrV@1-YKPcead)o?tGew*WZ45^79yr+|20C{iemfEXUv1t(`x6%fEA*7P+~2SOmBKeYfP3i*SEBYL(^n(c5g|Tzj`O=!^cpy@YeyoRPd;cBAo&7>itQ@T4d&|LH`|odY|R{Gy*{jNsg?Jx!M1=)9LzuD@Qz{pNIU#<}B2g_3F8tGT&lh3wxQVX~Z>L;QF<O5f*tujWS4D&={<tW76*;9PEJ?^*9{l0|L=$Mb%%HGNf<^K<V)zu2zwFFDt8g-JauaF~DoRX#sFn%bLho^kF-3@(~>InH5sIJZZZ=YFu8wl^^rx$ZH5``I|Qmvf`o3I0B<REW1#uKzMd`lt6US<c%JA>2N+w6|5RXC2AyZO^uIt`EFif`7ibG_Q}E>&bn2eaze&<a_JxlkJ`9m(#S!%~z-Syr#FCBmMAOoQx|s&o@aHx%s3u_rDpZOMjklO5Si*4*s6pp`6>!_2KQckKghx#v(VL1j>4D3YO(0{=wU8@AH`3tGOAGpWEx<56f^q=a!7C{r+;^R&xDC%W~ZR<!*6q@0MJceZsV7Nfx=@JR@(HbJr2hjY*$m`32|kxKMMwkbe}f|I)3T+m`i`{jw^Km#^l=WmjIl@o|#mx4n2g>zh{bd_&ERPm#P|9OFt!o;f4;n{#K}<0Ok*e>}M)_fNNyoIB5jbH6!1Zhw?yk?YUKaC<XLsPw~GH|*aqULQ5rCi?RFXnqGG`1glbm-)lgXY60)FURru*Op}==i2shzU&>l2AdYSQ8isfUjM-(I5&$`=KbOrdY|VxYHqY$#`7F~SsTft4O#yLo17;fHRaq9db2qD>}8%-x%SgSUXGb^KAiJ$1B<b*t(V2L$h8_x<$DjE<J{gXk+;XOKakt2xv{jqwBNLib0eye%oF;&mvN-#p2>W^Hk)pi9LK41O%6UksJXG{dJHdr%1F-jaWADm+tdj%Eplzab3SjH&bG3iqrc<2t;bd5^-*)<)*N0R+rfRMdB0U15h&{&!}E==@=yNU-d<-j=jNfQe7@G)Hu3V*+(=kliPwLtLzc6@0Ph#Q@p~WBBG-y!mF3?b!nx72nVe@ww&(BvDnIp!&o9p7MP)gKH}dgp4w{w6w8-^d>-oHFUlYQ)v-IsE+<wFuZm;J0(^cHwIVD)OYgQFGUNRryd4aRqX5MectNgORmqr)2%FR37`Fy0ko-Ff#@T)QpIgu#mO(oX{6_oATT1}So>8RA1+J(5inw#aXaXr+Y9GCjuVvU?<v&^o{{a=2U96!}ZOWjL<MfyX@jj2&w_v{}w$ULK>hwOJxPaeNt<!>5D9bPs=zE@u)^{U8uxo%MN!WFo^^L;4iwkuJxzp7-Hd8?9ZInQvN(exnBogqDVzi4AJOaH0)nUm7qB~ZS%&_J2@-f76=Ud?SkdP)E6+$Zy!&=i@!ja<*ix0)Lbg1L?vTdHyHSln60gYR4Zek1)N*&mg+%W_723bV>>hdb)D9CLU9Ij?vJNqy+PBgnMKwF9Ai9br7$$>YoBpI46GO@7>7&Gm<uWd58{ljE&Nbv_=Qi~f}LRdQovJl7es{4|;0_%`7EYwms|uH;&LHD12HXNa7)=KL!^Z?{awg_0Y)1Eek$TE%tN`F6DIUmQnY<<r;m_}9DsA@w@bM%llI4#{<fnm1X??KPJkoEtk=%61J|%l-IOUbhI>C2jK!K3^IOy<{HMsIhE^nn%6i<3h{6O6DuK*GWIVHh8)E^!d_0#9yu>CjK1D+goqCoG1RhCD$XT^6`21tGv$(8HaO+aBg~Tmi>OFxE!ZSuD`#<<4{{$SC(^jjqLZ7{xaWG^9<u;+}^D(_3p}4xeoPPE9V;}caDzX_0hsBaBgpOSN8j`2wv`2dA)l)KDFoNq;BRJBjc;>ec3;19=nIz>!U{p@#nt&vVTszlFv%6U8*7De_{gX+Q>NRj|R{9vzi;*s!RLW^z!rZzI@y{5_LI$D7mfW7(N~i=Smsxt%q>#Jak2_UzOaryo`?*t;Z0#9<J(?aiW#u{#J8yN*5V#Yx>FfSaDD4Xy?XK7nc1Xb$xC@xo<Z4eyCNhHLoJ)k!P)>-P)`&4wn>@ajWKcZpyg*eVEkm#DBT}jYozYXG*S(^_2Ek2H^fkU70_RJ0|Uw+&o)`+v^`oN&VU`+wE)}QHA@n`EwrM_9|oLIO+7G94BgCZ9I=pbG{r8Ht&s6e}f0f@uuWv;a_Atdk>cSKC+q|7rve4`bWu~xn{@mc6q;)`D6M<GQaBjkIYk*+_v+wjQ@8ZWqz~nl8lF_u5unxa{CNFZf~3_Ci8%wD#>y5^Gm7!N^Yywj>nreVlB_Jv{ydd&e^n#?6+LwWd60GuJqI1M9W+|n;_#bvIx(o?C+zc-KRjQdrGcPaq{>vlJd&@>*+8VFW=vj`Gt~eRbzSF8a1BqeGbQf2C`hwj#Af^-0*Rc@!9MM=Vt#kGM`_vUdE@IcMO*HK}BRaXH$4Qm^B;Aaj)b?xq&?1jP)5gxBr=2>fO<L@^dx6&{xKD*plqLob<1Fd^(QK;qj@}sh^EMAKoeB_d`j!FQep+jGtm<yK-dZ{d6!u>UQZRa$TzAwgnZXeUr!TyxhG9rQW9a%Xm}s4}E34MY-_(QEf)3To**n=X#~)jz2fa_*rDj#M`^IahU9vbF%-_)z8SjbHB{P2G$6(${p1_WH||KGVpR7gJeFqx~bGLCD*zRk~+5byc=(4g*S5l-@{XWuH<IE%hKNWHQ(<v%w(x|)y7M`QF0?<nv93I@tix1;2_SgUzGMru8-Iz?MHiZZqMId>gJeu8E;B%oXIHd7adE-zyENO)R)XXrM;3H)7_-K@!|sAx3FjKFZV0wCCT{7p5+SXbAOZmjmRdh<a*F$IZjvKl>B%l>9?3ZGTxNj9&D54AHR5w??*1!D*Gj7x9k@sH^Np)KWqD(e1B!qeA&Ob?#cL6^BgT=xxLx&I^Vz97bnYY@<jSs&3F7Q{m?nn4Za_V>r-2gW-^|Y+?h00#&h`u&TRoVrGJ~B6<2bjQlu<Dlaq7ZE2q@GVHaimt9gynGH%b;yvff!o@T>5>6k2E&7EbU)3$e3ts=*@eQ20zk=r7JWcjP7a&G@7F^K#BX^hlACD%M2MW=1=G!wYa*w$4pWm@Fs-fS`+7SzZ}ZtK~A``vUKAnUK>MoxEG{;%CR*DA^R`}4R}^3UToVHxMT*ABUk*)v)8uaX<_)1`gUTKt^K{%dZzp0Qn#_DXKf-!AR*cjnx7@0pCl60KysD7m)eM;V`s+w=1x^TttmzR>-m{9MVkp^K$|rcIXTOIdD9f2P(MCI4J!-u2<<HqOcGWS){*_mteZ!Cm(6;vl}yt>+&h<H}d=N2s|o7wYZNyPVse*O&RlQa>60N^ZNFAmhLPBEIkI@XaabmuHD`JSw?kM1@#xA6zE~_jA5gGVj}2T<U|8+wOgk_K%V!$2{Cw3Fozly}sO^-!77Ib+EadPnF#0H(1V(D^GClxNua)RhEX*Udc6|0n&cJH-6loFEU77N*#wvuJunZ<D|BOb6bfHGOq4zl=e!ljSi9a6N}|zFYAZ>S6q%eHP3ci+E={BxuZ*%%+oQSQS;RKjONlxo+p%&`I-K*f~>ESYnd|3IP{CmPi{Q?B;zObI$Ft7ucNhIOA2s5Y&kCDs>=&mo{~F?x0UOTi}P%}Ur?XzS3AmenUXvE`^vZ){6j(V)aTc>Ecav_D!J41lFUmBgcsu9+x$Vs)wb_to~-1Kj<aI9eV(J7J4=@5d7AB5xXkARqXNk7(MeJl0!PYuQpwGQlVpD0z7prQBPmjcQ|JF`j`_dw^e@gGJ#$Juxj$CwnUb3sa>zLJKPP!XL#{6mo{({><}b_2ywTo_pSS48Lgaqy&9ZX-QF3EsinM>cTb}34sV(CQ*JWy+dR=BbkLBmX&V%Wtj@)Q3^BN^LTs4_jZ#6mBuKUXKf)S;q9xJ(7zmv4zc9P#0u&?+>#tG`Dnt!gJk6nU!yGCx8@fI8<>!sv2|DR+WdL>J~bFpk^o%cbeMXveQtdO?7t@bIINB#QZi}tDc=j-?U6++0(B|~J~4qYzeT*;l)qh*{QYr(nQ?k)E*@;{L}q2#9HZ@K@_e-h`$f-bxs+Rn0aze3G%zrrXGC(oUF&6Vq;+lGu!H6Jxm?zc?oCeH)!`^tT&zImmdE4h8oGdb>p_sDbFt7YVV0Pg3g`RDsNb~`_3HUb*R^Q>#5V>z!gigRbz0a8bv%XPDw8y-_-+}6p;?>lJi(#v&m?uOW(U*=}M*V2ATg1jfvYN_0>__RXCt&$sFg{6LmzTw=NW32S&F9&4%)I9aR+|m!6+eWpP@qqhyYHsvfC+&S!@q0kFpaZg<0ZZgKQ*wP_A-T_4=`QE?&IM#Xfcuteo_gQX2y^A<W1rs}>97#<=r41le{VjHjEUzs|9t->G7oRxSNX~da$hthl%EG`e_xXR#C=^g|9oF}R&9CiTC|hY`D!0ze=50SSqC{zk1mt<7iK5Qanb6ToLAM{+%Lz)gBS9>M+eCBh~07@Ma{MN5E+N>eEB^TBh*#u&tLU%-{Z^NnVgNsxtXse=g!Lka^K(=P3A{RZk9VD?-vbj!?{-Ljnvhd@8$lPnxnn;cqixfMNu-(c`!@9H{=lKw#V&cUfL%~zE{b$!^QczgL&sT=jOd!a^Gddb(!xdxpA_RJpcW0Q`V<_g539;oEi5CzRb-F^=0{a`}6Zad(U5FoX^u_yOrFuAC>1dEw;$>$tGU>{7I{`O!`mB^(_H%Tr}A&&l|nB^L-kvQ&l++E4f*?C!de>UmMGF=E5;@U*%$=)Egz&hRx^Yo5KgmbKsLbWt_~e$KS8!TC@4`eoN~Sk~f<m&#i(g%62HZc4>~ZU+v)BxU$xp^AEk`I92n>8RWR$vt9D*k^Fqq+$Gm5YHmDTF3%bFz31Ha?xpm*_aM2SrR4hb2fRMU<!tQcYX`qSp(hoW{jcQ4@Vxw7(ik*Pe(!ai?6REpL8e7+Uj8KOUviUdH^zxQdmgFZO0E^UE$8cErYz@!uiRht`Aweds(F)md5(PaJ?D;dqvZK?S5J9=O3BUf$GN?Bu(o*ILw=vb;oIB8w8*tGQ8J!xHI?mNIhFgxQ89$utGN~#&h3qQ!#UTxK9zdaxR=zcH|ym&bB&vPU(J{~M()!qxp~D)=7Afx$@V2AbN}kK+sN^!=C=z=J=y0(-cIhPwQ=M7acXYt=ppY<#ysNOaiuojhf95bK+RL%AJEUgm-W24U+xbL3XyuH=DlXhdx>o~i{rV!{vepgg_;|2=jAvbaF}z4M>Ma8vq$1TNfx<2uCbh-)}58*JlMwL(^>XaN|HrxPOm8KpPrX~dJ-@1qnt>>y!y-BycjC;>X3(=+lQ8UC-1u);-9OzzFp_z%G{8f>zO?`_eajxekXNO$<40u^1OI*C-Jp%KihdVJ-_#&=6dOI@*Yb_KhAB{lI4BA{ki2m93|J^f0Xv^4#{)og!EGHZgk?hqUOf^j#5WfKau5JDk}F=ua^E0W09NtU+_FqU;eh7jEg1QFZMz1A7d<X{q#kd*B*W+=ZEJ@WWUtAC-*6p+^7&M@2&mpD$oCYX5ZxP{I{3<o|5Y&Qsn)v#5j4+?);qh+`d6E*={8_wzZc!zps`&UyVE}b*X0H^CXL0Z=9Xy2YT`-`QFaSPJVB%*mZt?PtEnfALTu$pegb_3wp}^c%KdLV=QvraFh4Mq8G_}`pkU6%b(Yo-+xncJzGy{U)SW^_Rj`B?zB8@ysdI`Mt8nWGqdiOeBT*)PbkAkZ>!w=qdB)XuB32o+{!QKgQ+$-zq||Qy6!CSej4`|&W~zt3|PSRS07lObKBk<F1#GPf2h5Rl6<af)-Up(Tgh|s<)wIkYqOerTjl229&){UwU2yn!|8H87`;RGi<0ZN2g*F};$X?^E|Pjt@4A;&ZVp-|%kMv2=Cglo;`5Nb`)S@UYHt44R<3{Q{3_e!{vB_x)-$g>=TUO~U~@S?R#_q6J1E@^xu2aVzo+Ed9aniTde&~q2d_QM_g{k_KZ~)*^-B5WI;!_6`JTMhbENHOJ?X8qU)|(JQkvXsTwk6`uNcnr219rAw#v;Bv!s8njpE!nqwhNY-i1TCKh)gV`h%Q@CM8NfvEe<=7Zvxi%FViNeEo0K*eLV&>ArmavfJm$`@l-BH@PSMKku-t=ZradzSv%$3!K}$HuCcyGv|{a(<0aAd?W9xdpu{i*PHN^_si(A8BB{@zcEer%e{A!S5M~mr=5FqJczN#^}844{quUo`8@BeG=$$%|NQ=Qz+`z2JmaCvGe3;*vdYax7v(seeMjaCgKEmW%gsfuU$)(q<*(UvlE-uKYME!LxnBjjzKDFlxxKQ%bzjpuXSd4rfX?#%e@a%lKKPWyFKs^?iyO-OQ&*bs`M^26!POXxT(9w$T!;VEQu3)q<-POpiZUNla&15vnYWx9#JQv9I89Icy=UV1ykU1uc*5hkP*ZvCr{r3|TbUm;sK>eE#*B2l|M!Muv&!}OV=@l&9+P}Xe*RwPvDig17P;;m!`Ji1i?f_NyS|ih(8o{aKWhHyv}{+_`?8$O-Q3b{m-eVP*InD~-?=WBl_tpiV2<4HcXXMPo_{{GO;)R1kFLu1#k745d4BC|(tA69@153iouTB~;SO@$va1#6_6cj=@_xMi_I#2>ZoX|Vf3H-3DCdp|12UvtfAdik&wm|D?z!-KcAn>9mFr{I%ijUbs?ND{)C!&t>9bDA{G>sD$+yOGzd0{Xx|d{;>jewTd&1R!mE|8ik}mD~=%3vAy4mjE;1xfA%U#&rDmSlq7vc4(F7GusPu)Ds$4kMLviyzhrF{$kcWIAbz4tn4pY_aHsl$zn=ykvNE4V+8G|%Q!TGL3GwVYbVwrTzZjzapE>ehb(*Cpcr>QCUpN|h=9|Mxd=?nVDwhw}fa0lX2o0k|_nJOthgO#Taa2zW9?oCu!}Cf^871aF6kPr#3Y$!~#AfbT-YpWyGo<XK#VKY_DD#G&vKVDfLlq2Ou|acg)xF!^9`Yj6TY{0n>vn0zt#7w`gzcq@D#nEVQOEBFXRoC1FjCeQ9FoC4M$Vt2SNn7km^9qbJed%*p`<X&J8unR<d-$nd`i!k|B@O|)6h<F?PZ!q~1@HX&5h<H5wS1|dH;PK$T5OEuLdocNT;5OiIAmZZil3?<zU~(^T2s{_u3rwzobAi)C#1Ay_dzvu$N$>;kX^40ad<U5PFYq4l3W#_nd<vL+D0n7#6hzzy-UUqF5Znjc79y?-uLvd&1J?!X5OEZ|IGDT?I0_sC5!ZoN0FyTW*8$rh;@<GiVDcg0-r$iC@eKH6FnJ<)26#C{yc@n9Onw5q8+-~P{s(>+O#TV{4>+BRh&U&l>Jf2v)Sa9VaWF(&8D0%s4Rxn7MBE%A?gdW(C!p^1f{1^Di08l;fES?d%z=p4Ld5&wN5JGM;QinW5b;Ae)uV@ScQA?gt&4~_6MpUu_D0>w1QEY;5fMLvyMSF#lO93D7a`&U@S|YzZQujobrA7f_(CxGc<@~CXo$Esyf2u%4Y)VB1w<SR{{~E69GqHrh%3Ph!$ZL2xxj_Nc_HFV@bqAEsymtRnfPCb_yYVi_%!Oy1&DYbM7#>V0=xosXB9;JJ4F05d=z*T>dwy)aRNl#0p1qe7ImisMBD@-j)Uu99d#!TBCZAz*M!G_V^DW$Ld1<B;_u;hupM>hdx$t5A|3-D2_A{MGX^4_1re`=F9$D2-B}3{?}doZ!%u-vq3)cAh#y158C}Gw9ubr01ZM>MK*WLYU@&=Qa3DAuB5n+C4kqsfZVc`U5s!rb1SX#Y9toZW5if_Y1(WXwF9(|t@d@|^F!@993Gj7@_!;~yn4Id)Gkhj~<02w{4ySrVO#TS`9DD;JJ_)}FCO-f^3El+}uYj)ulg|aO0RIjVkAjZ|llKOX0(XOmo4{Lu$z#E(b%(eaT!&WzlNSc-;35#QKRhp(JQLU-><$q>)x@bD5&w(2^AsY!1QG9t?*s2c-PsQjuYri?z<&q-j=D1kA|3}3_k$;Z6Hs^hLByRP;%4wB;3lX$%^>315OEE7HE=c5of;5vEr_@&yfL^j>P}OLxFbZ|7ak9eN8RZQ5s!t4XTxWKXQA%QhKN@~#DBy0g7>2C{0$LbgovNOAA=vGCOyGt;>-|nKDZB<JP@1@90U=^z@x$BjlnVCrVw#=cvmp_NN{)XaEN#Yd={8|Id}$mDMY*zZi2~AfOmqALB!YK*TLk^z}LV}AmZ2XH(>JT;Md@%5U~?}15ADr>;xZ&h?C&Ez~n2yN#JD=@l5#dVDeGmncxu+@elBBVDcv5)Vf0)4{rr;1}4|Rt-w_w;$rY3U~+$OF>pbMI0M`rOipzt13nW!f{4$;FM%(i?wo~)cR|F<;A_BZP<NI=#M2>S13nHs4t2+Xh<ifBt>B%&oltjLLB!ud#FgN+!L?C$DnZ1N5OFlT7PuDbPBcXPEkxWB-Vxjpb*Cjn+yf#W1|JI^i@GxmBK{2`UJ73gUX8l56e2bu;xq7z;ESj`XCUH-5V4z!IMpL!@_b-7uni(E3J(I4$AF81t3bpp;Z4Eh-N7xveIVj7@Zn(c8Q?Ks2SmIcz7$Np6TBXL5F)+=KL#eh2EGJ-3=w~XKLL}!27d%+b`=qSLiQ9)?gW1V{|gach93u$CxI`64?)Bm;LE_|Gr=3c^C9A&;UmE0KY&x~4)H|zKzKZuycKvLxGh9n16~zOUJP6V90m~wzzc%OGk^oYt`PBkO`Pfx@gvlo`w;PQh<F=(7kC%y&NhhnPl$LDd^&hK>dqvHcmPD)9^Mn&6LqIOL|hdjE(8A#{2l5}8HhL(A`XE^f+JCPLLlN|5OD<jTkyB2I}s3Z6^OVUya%`k>P|a|xIaWZ5&j$aH`JYp5b+|2cq`llo2WZmA>v~YaSHq)n4IcP3O*CNK*WXMHZXZna3OFhh`2hu3YfelxH{Ml5f6a(0h5mb4**Yqh!?>fVDk0gMd0la@fr9*F!?3$8Sp<4aRyiM$6)f0U=p#XtB5!+oa#|t)TK|z^MbRviik79{{@p@29t;%K*VR^hrr|;z-PfbAmTsa^TFglgH!7c@hbQ<_(U-IK=3s1P>8q#ye*i#2Dk$_4k8YRhk?lhz~SHm5b;M%+!ahtb>|~Qd<P;v0zVEuj=FOMBHjQIJK%qU$tQsw;L#9qH~0YX0Mwms5OIBoI2>LTTorXE93l>eh;8stFnI{r2F?!=7l0Q7lShCHfQvxHrQub;<n6$v!Sx{GuJHa~@`>QC;GZDkKj4eN<XgdifY(FB$?#)f@)U3~_%=lR0Z#Sk1H2HJM4TTYE)6dQCa(@I4Xz0he-F2V$p?VH2M>XWr@|+I$rpjAf>%PshvD17<Y&N#!M7pe^seInfXS)uq=$&}K*R;$o?uVZodOVX5JYT)X9H(L-LXN$J`k}Roa&Jq{4AJ6d<P;<hVKCHKz&J0Q+J5Z!#BZKfmfmKY=VgYfQSwFQ1DRH9Rnin1QFMU$ARNecWOh#WgucdcmZ$$)FD57CVmGI--O=*lOF-!1RsWo*TFY{$sOQz;As%?kMPl8@^0WC!7U)-a`5_K@^ElDa3DnN4-W>D+ra+dJP>g%cz!T>0dOvGZiqM^ya<@QG&mnP03t36uLmaY3N8z74iOKA{{$xg13VZ!6(U{>Uk@fv2CoGlf{1UxZ-dD{fNy}`Ld3qPO;nG3QI|@CeZdhBaV>aFa81;mS`cwZh<F%$2zUtU&M=609z?tmz7o6=b!Q_)d=4Uh3BL`#jXLxapNVrp#D(B_z<E%23PHpn5OGO(5I6{RrzAvN6e13Q`+$8=cLE^d+z|0A)F!G&uTYng!KrnJI4j!T!{_th^Qb%bAmY6c@n7&iz<;3b`~?w@gNVDpJApf)?sS2O>q5lk;AOyNP<P5f#Cag%H<~!rBVzKK;5Xpw5b;6yVKDhR@Imkrh<E~g8kqb?@C5J=5OFNL1(>`XI2IfP5$A;mg30~CdBNTgu_rtam^>HQ6PyJi&I->BCeH`X3ig7Cec%CL^0HtbaAAnJGQ2sMd@#5&xI08V9zGRJz7{+lyci-r06zpKzX3h~c0$Cj;cvm@RCiwEGjVQ+xGX#Z9D%x179y?#5qE}n1b0N;=?oE%g@_a3^T6{^cM>7uJrMC-_&M-7)SbH!aTZq*aUh)PQ6TD4A#fnL7(^Tf4*`du?u0?a<sjnH@S@<Ns5_-0;!udVFg!OnH|k7b*Z-|M#3kVQ;aS1tRCn^@GjTds5%Fo%rM=+2s5_@2;x!QQWcWDnIMkiV5OGh4xIVltxGw5WeTX;`BF+KN1I~k*lmnlMUqQsz;Mc+A2f^3CNf7Zu_!2Pr1n@%e2#B~1{0A_3EVvE0Bt+~74+4|t1^a=sL&P3%Z!ozh*aMsqB6fpk0h4D1yMZ%6#O`n}Fu4!d9h?m!_JtP)lUD}&f=fWet>N9l<m17u!NVcq1@OgS@&n)n;GGchRk#yO{u+E0{1PJeMs1>c<c+#i7VHf!4-wac*8$f--Khr=_kf5e!N-EfqV7zBh*v|zr{H_Qdr)^yLBy`EB4U3y)gyn@r9iMhxHv>y23`zY40WdrL|h&sj)s>5mqXo&hKM5};<E5ia470a*)(;BI0_yCF99xrx)T8r2Sda;;pxESRCjXXGx05mcnf?Dcn#{#7KnH{MBE?V6WkMZr$0p85F)M!j|4}e?o@<`vq8i!G;yj&#N^k&FThtI;w|tbF!@687VtcXco2L9n7j>m5V$%-TnJtgOzsCR1kMQ&XNG47lY4+OgVRIAuJDXtayRYsE4|FA|A<}S8NlT3U>9&Yh&U5G8<^Y|oC%x*A}$Co0VZz^E(rbxA|41I4klj!9tfTb5pRa?1e0F{Zw6n6h@Zn>g2}1wJjZ8ZPl&hzygax(>P`iSxB*1m58eaZ19hh#MEn~>ycxb4yc%_9Gemq7BF^C|PW31U>XJV=2e=4C91brIE{?hr4iQ&`h%3R%gUh4tRDy^rL&P!gNN^<TOH7)&LmUg&;Zfiy)Eylnt^g62f(L_xQFlr~#Q7lN7pP5Ck6xfIZ2`Xk?}mtH!>5C%qwdUxhzCK$jo=Nz4N-R*LBvrIu?IXGI2&q`2R;)&gNV<;uYk$7fX{(9LBzkp=Yh!wf$P?Eam|_T|MXug{qH}zUe&(%kCxQm{PNFH(*9<K|1Rb}|8Yv)nr>7-{wp-D{L*4GdOKYEALe)6p8'

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
