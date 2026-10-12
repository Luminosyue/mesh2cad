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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9d6b66aba431493097f289a6e42f3614/part_004.stl', 'relative_path': '9d6b66aba431493097f289a6e42f3614/part_004.stl', 'source_sha256': '6cd0ad0392811d6f6d8c4f4d15ee7329b83c53688e6ab5ef4fde5468ad7be832', 'input_faces': 816, 'input_vertices': 545, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27505970001220703, 0.0077256858348846436, -0.2750728130340576], [0.27507293224334717, 0.4999997913837433, 0.27505970001220703]]}
GEOMETRY_BASE85 = 'c$}r21$5O|)V9;&6t|)!1qO<{OE1g}?(U?xQz%ljDMd?xB7;kCiWhCMgh7f!acjv8E(6101qS$X_I_{Y-pl>h`q%fd)}Hst+w|n*cuvx3*(62E91{QYl{y~}JhG&sB#Fo%<&Z}A88LD|uRcL#h6axHkg||3{@Haw^LEWzcJh!$OXG|6?i18&M6nujv08nr6)Pnd>pN`3$PocUdkh=VyN~ee2MiACWBEb-0|NV4$9|P7RW2o0EM7{UDE}}2r5AZvxGY{5I{3u~f6COjyGO168ab=7zcK$B_Q#N~UiyBS{D#3h*bgCJsXLVYJDJy#pHT9!?%=CkN9_{6>{0SC{k%$6KELOVW#ZU~oq0%i^nc5-P58Fi5r^pa>KwX6{(#3@#If3_Je_a%)x>IhD4qP3=zOizK=ze?_i;XF@O`CdeS!QJE%ypv=};(Ecl5m@_6y$}=Nn7c-LmmKU8mWGyPVD^N=KR#$$r3k_Ah=NuDkJ-_}9ZJUmd2CuT|J^htqjW>DaOdk+1k{B;WX$mD2gaPf9`Q$j@4F`lnV?`nK%jRo#uRWE-i{buQFoKW5E6zV0_JhXU2eH!nnSegZp%=x%&9ut^AAH~J^`)2`xl=Jg2D-T215RzY<AbGgY^-xWB>*PYGxoA;k{^n2I$+-CnZ`x%~)uk>3&`8Q4`P0`)>THKo{^z*I{$Tu_1=lpciLv=U4a`k#B>Gu2NYfJX?b<?j1)ZO?>wmE@x->a{2I{kNW`HXxWrn~dUJPo7vQfCX_*CB(_Q5O!Gq`UE@l|3fW&o7VU>z<uR`LreNo~FC;<xg9uk$!B!>9mZebZnWsQhr>0BTGBVk6N+{r&D`g0++MrJyFhDW|{M!IFo(9?W1%zzFBnjC@SxaU(eFd_y2i|(|Jzyr3JrazxGq|ZN5dRJY9XIXl^P`Y0Y!;mB-VZ>h}j9^{c&k%;_{g<W&AY_$YrV?<4j%Kjd<bKSJp%hZ5LdHj3}}-}o?hzVhWPr!(Lv`R3;je7}0=MBR<AoC%sp_Z<|*>0CFQ`jM+|??>A5Q1+*XIQ3swUq%15^$F(k@kny2cUNCSy=$q5b2@i2b2)52Jz013m$at)HKx{_>CU%Jtu&L;2^qxcdo^`xpFj9$pT@+7<jYHsb2%jOIOghW_HnFWT~6oaIH&Q`)z|Ff=hLd>tEZx3$k&4R>yG~1#Wc>SLE~xsR;pLx`kHbA<Lx_cw|7eM{Ytp5l*In8`8l7H)A9MgasPGowH4fdr6)PqZ&#Z8`+yQWUcLSI3|;qBRUQvJ^0?&cYZ#a0?l0LdT%5{ZEuVcB-Ita?zShQ@+YiPoSKrLa<CS#iGWk+;*-dm@Jf4s3{>Y6x>3Y^N<!eeDr*kJi%I6K0gS`46`SOL5lutDh<GhQn%;$0578k?m)cXbF!xJvg{?X(sA<doIp)Gbh`}-Qx`Rb(SL*4mC#KocXdtvK2{Q`cNzrIlV=KUFbexYuh&flFU=x%)F-=-5tqe3|UhXy2aI%#M;l=}=~e`yc)wXMOr8{de$6->IXALnQ1cP=0FqaS_lM^dA9?8gt`axgHSxcKI29#6DvO}RbH7|-Q!%A5PIi?5!~GMRp_lt0(+iK(>iGMDjjvcLT%t(T<I{#5Vg;xb%573$J`sh_xCyZTZR=AHGqIK98ZIRAxsoOkuLpD@nPkT{)c5t!d!@%nJrx6^cf^|hS;OgxTB9$(1Uw%_A&`x5WgH!wci^1UKonv!cf)$2??PWJPy+HF6N(#vy>d}Vn?zOTgR5tQz>81@I8=5|#K^Pr1w6yteNwrwO|H3l8!`&z*L1->%v0=NG-t}i2UE$2V|G3Rwx`!?ju7ccX8tA3qB$04oQ&y0EJ4Yy}kU;D!CS?X1j%k%TIo1Fe*?sugs@O6j$O}=_I+YsH2Z+rM*F#TTjyqr#SO0JjsVdHdnew$I_==TD0bAEPb<#A6%|8?<=aP;2-DY<;E<wJXT$^BP)6-VjE73K9q=vA5rU47N#Ij>_E-X&l5Sjh8N0@tIfFC{#PpmyQ4htv7q+NmEIIfKbp+6VCYX#cLhiuNxZ2xR}sWX_L0pQ#$N|JnCG-&cAXPi%5+^0n9XIGt5Ip1At9`8=Lz4Qp~f{c><Rcf4qPaP_roU#Z@WyMBD#3)Qf$^Wb$|wT$eae#ZT};mUB`jc@+CD4hFEI`Y+JHK@O6A8}m5leKD<BXqqBF?*c+$aB>G&A$)O^Om&Z*eSZsuJzo%{9i}v?);-KBI&x@R<S?m0^02(exCZejQzx`>^EpJP<P|20Tl;QI^J{0mkU2-e^+HHXII}AQ;f>lY%-G5DdNTTIBPSn&s}_5#C2Yu*Y_e{N&S`ETOGbHS6{|`Nr&~5l-{cYe0~Eie^+0t&*iU9-A}%)W3gjg4oi4^2wOnDJZ=ux?=5Z*uD*5y?cvpA^0mVuPV0PI+jQhBO&&XybFzQs1^Xvv_0!$>YQnI7be#!l_`3ez_<UcClP<nln#W1yLJIaL`fxet8#Z2d<I8>l<0=0)PoJRjIk5}<C?n<HXnCA`rQ<5{)xbvleCOiZhScNdy9_%yov-~kot``9>hAp8C+1Rq<Cc*x4ZKL}MO&5SbgZV2;Pex{xZiE_Tj<WWJ*~KqwCpeB+cIr2=-5w*)*XDQLQ|?=wMma?y8fpcoKAGvMD7oqzN@bxedA&t^0j$axqbuqzJBoU@O>%asW_dgD|wt5#^vVft3$cmjFR7uQ#xnEo!XDQ^9cFM@(w&7MRWgh^^F7EzvMN$$u}R=;(A~8Y=rK{S61bsb)zvbiv1d;IsK-md+YA}&f9v^?;YB}`CRSiw9YhAS0`Ue%5|LmmAp??;PLNtezm1e`z`X5d*sWb7O}r<eLdZsf4)*Zx-aD>rxU$^{h{G4ba#Gm-WHV4!8-Yh*DfxH8da&kxcaiKIQ17>%P79?o)vt4T3+Y7`dXSZye~0u1^H%7B%gmKWl!CWFP-k*lYahS5$7}AY?RwGF1OA@`Fy`Yod4)W-E?>Uh3?%*M+I;?(h&CV74D$B^FO|5Px`70=l|AF_WP!2th@6^ENJ9-zPU3H_4N<W3-<H7wsV^Aj5-~;JbMr3cK)~lJ%73ST959$pHQwDrxUr0{lKXCx*K15y<t9$565e8e(w8Hf3$@kT&%nE(;iq%?KxWx^3}2{Y5!3Q<zu;KHrDFiyk0sGG{UXFPa8qMw>Ja(<16yGhwHlf60WOU{C<q`GpsZ}Cw6a5{m9jqhE$<`qzy|VU-9?i_1Fch4_$oQAG|)a`|`Q<Jnjugxw-nUxZI?yZ^*Ze-Sa!;=ZU^Ucl4K6;C@>A=nlv8wFYH5pLt6wx*K2h%c@X*0{-Ir`tX#lYdqn4clD+2T<^Bs&p4mozhi#M%<H8)PdNSaDY+cF5AC75@zs*JE_|h8InL*`6|Ho4{+r&d=(;5za(;ZuJ3U`(ZT{r+-+5v^{DRlRXJgr~qw;lI-5933^Lrf}M)jU=KVLVa$$nE_FS+_sS6(kkH`j1EtQ*hg&-|;u?#^Ex-{0~4<n&we`22(44&(Eih0fPaU#-3F&i{n*q24^culvF57r)wBcjx;|@8WoVayruAT%Pl1b2+~q1OG1`Hxgy?r4H3jvcHynTYy37EKR_3*>|2VCbuTvY?;K*eLd<=*WLJ1H~;DM^ASbJ*TNg{_%o)(Z@L>_`q<<*Dxa_~I{p0J^AqHM@4r=d@TC)tDWAqK{kD=u-C+OVC!NZ9+D-m_yT3g5G5dLxp6?Fw<%;Kd{aIFCuDkJVJMu3l{e1E$-QU#MI4+0H{G7hFHu+}i^xUt@aXPNPv7OVA64xG~^moqT{uRvS;OZ+MP!31ylW#sv;PEYh%h}bpb>VW>elAYFq9r-^-@Zrb{gS!G*Lhzk%>nX_xs&+5d{%AN9eiofsW|ROD>hU5m%_={s@LKDhxZG3U)04{K19%dj;%)pPUm=G8sDT^73tXStFuxbx1UGlB=LJNsp+A0<OlQnuw?(cN%bw>lhOHIUebFl<;p_N&y7GD|6P5f{SX@e<=3~#Hx8aU%jK|(%ON6y-=~FtSSfsSFuzwz_CLtHPgo@@U02CpiT$1nqUgHY_`RB${=q@g8AZ5Vy}P!O%4NYfes9)k1zlJ6YqZhPx8=FW{*VS6={h6Vk}n^O=X6?sSWW46h~RXJ7rw~(kL7mQvlaQu`~29a{lNWwoG<xO7k-~;4(IoFcHj2LXzE|eW}jF`U&>yD`j?9LdTMts^37p2cprZMdwO1T_0<X)X3>2_^ogPTyqLt#v+ubaTzz9iJe9ZdzC8KbyLtRx<IeFVx*Olt*;qpN@xVMl*Y!MeneX=)Kd)6vAm6q#6_t<qsP=l@!8dLdCEu9w^Lk3JW>-#Uc4qEJH@W?|`er+BKU&pX?En1CX<U`o{7L)kn%V)+j}LhLT<<RV%DjG8*gwndZOVB*e{x~&kNs7yUl-r@WWs7HpX;Z|m&=sA!RaLM{l*>P^o#c8@!=!)M^|5Y$Nf>teUN<fN-COXZDTs{zL1Nr1h=GpA@j>R&d=!8PU~T1?mY6<21RImupODh*Mo1XyMcV!I`(()wb3cAb2>M<eU=O7-`h7C<5dP4uhc>ze16~4SJ{u}`wbdTzVy_a-cy_HtMPk<MxD8QVhm~z+Jp{k9ewT2SspL+cC_!SJa5hCM-S%uipelfcjK!`-t*`>S;}zvw2R?=k6Z(3AJWy=^7WcSzgIOK-`DY)R9|Kko{L?4`2|0>D*dDO(RB}Z<n>$6PfK+-zVz_@Qtk(<$k&!+r1CWO`ci*M_NQcGzq$|g7wx`EzImZHwL_y_Pfd69+YY?K?Wdnc>8I|>zQ+YBe_Oer6}p43+`h>5vVYhL`guSB_Qzc1@m9Of>36%imwYn?_m}hcm%H<oX7_lW?Z1Nky4$$?%e19_;p&^wEva7^>R|G1WjgYB-hBui+kK<iUh);|n95<SxrfXDA(f|GZaU}F#Ww<{QaLDx<Jn&{nCi>e7e?*M)t5hpQoAz#K0v-SR-*T7<`UiqG;0qfUsfmceggWtboSD2%Kw<#7bt(8^LIP?#?QHUyecw}_8slM`Fk0vU)!7f8y(L#ca$aHteB7H5hH8~`ErR+eol!!yheB9E1wV2cPp|_D)O~VIe1_6E|0@M_?>thR$ITI{Tpp^BDaUHIk)HzzFGcHZa@Ax=)H>Ocb0s4(SGWW=7`I?bVuL&H2LbnOEh1pd38>|LN4A9x&CsU?#7qAU#xRHUkRN>^M%}HAKkCoZxs9XaX4+}9ge<vcNqC*<Bas2r8Mb5zEpE2?cW+Ju|L(jET2Dr5I@hx@I2`1tK~2cMn9taQ!>tUdXHw?>qEX7qVsqjID3=s#+P@`qIHK{^Ttj}$3Hi>&+ihIgXvv~eAB-I&lhOVW~rlee@64Eyq^|==fhI#w^2FU7V&uXzTF1$zttk&H2YEeQEk549DVJ4e{OG+3(|K+($Xkik9Rr3*X_mQ)ersy9<RhYoqk^ZA6oAjyOL;~tz{lb?Zy6mh=TSh-&Lb1opM=u9X^)lDOX<|&GVG<`4X*LwX3DD?;-KJ*IKtyJr9gMMb~}E>slpqXI|$T->7|>rIzk;^p!x*Ym`p&CDaaW1v*mwm|qL=xb(0Z<wLdBYgEo})6zJj27c#tRF@B2uDeU}dd5EPx%y3c+>?r&Wj`P%KPRG{+p>*iKQ55R=UCr8PX4oT+-~p4^nSs-V(@zB{stOP<RPnRy&|OyAm0qy#{KS1zkQCr9QixXkJ<atylT8}NY|HZkKy%XZl3R4eKQZwceY8rX<Rh(M>>5cVC(*c+N1JtJI_Z&e&TldI2X6m)*(DEl;v^W)wf}sH`hL*`A3;Bjmlp}e=$$A;d%1GQGTzAdEC`EKJq-SmPt+PJ1zS)r|+p$|Jw8%rZp-?^)9DA$NSQ0DpI>M``qSr!hRnAU48QdkN>uhkNN%ZlebR&$cQU7mHa6oTwiBH_Hui8HIfwXQ<N>dPH^?r=e$l()2F2GK9pOVc$|!Q#p|JWPXp-u*nCd=y;9{qwC`fHpGfUN@o&xRduhkrIzleDrTWvF;`>Fr|M0{rO6S}%XaDDQJkRB<8t?Dum)GfgNG&hEceMMjy6|(;!e!3qs|oZz+E~Wl9VYu;8n@#B@AFPRzGIPh@cZLrKcEA>chlbT`=Mlik|&LO@+j<g!&kS3(fFe@^*!e38-;q%_+axpe$>g2J3-$8sORtS^WGTWv6SwXR@WTI4e4-w`W`_^C`046YM+-~d=2xmZTm9X|C8^xBHy+T>o*r)#rjQJv!C|^66QON1M2aPi|G8@-SAwH$n}1{0zFr0VWYV{V_yEjx6jLxOzRza##X2CK}(G0=kTRNoyU_4<EXyPJ+mks73)J+-`L0NL&bXDrF5EYqViPi<7DsC)IOAK3wXShuJeBTptiK%pfuj#G+*0&xynYT`C9c^MZU4Liqkl+e(z8F1!~TgPV<iXROkKF=#%sw%053z&D+p-Kj!CXr}c^5m$&S5UY~p`PpWj><+QGL_3i6w!%yM&T1^ew@6hb)ihv06wKRM2oOq6(6I(Rg&G$9bX?>XNhm0rR#QIRZ7(@L>&2#?%`B;Cdan))4YhQQSpO0L96VFGowT`Cx@?OQ?!F1zwb+YfZpZf*Y)pAdRpT|NEI6aT6Yl7+dPu)6;@@Icu)2!!3N@s6zsxKMOk9OZkY|Q-;&yQwoy918pVBonv*&iOr<$&jUBOzt1qc2GZxI8!ekZ<c)m-n5p?~&}s4kBN}zK7DW5UF(7kJ^!a|HQD`FQxClg37_ZpOfsrT1~zU`#D<U^8B7-aC+`f*e{X}&1B!N61`uv?>i;?<zi@kW8Zf&t#Qclx{|b==h;MjC;sp`zvsaISh8R09gQRQ{WPssMc!{498K-tzAtC@ZL^;9`&sPE*&ZEWEnS4_#lBBy_oaxE<ZIX`RIPE8(ob2G&zIJ7KBwR0{n_?YIX&#tCi^8y(s*uSpVk(g#QU{TwYmR(<9*;{KkcvNoA!NRYg{Kk)Zgj-rfKzWZZ})GzvDeivVSgy?-%b`)X*IKKBjTV0ZtF^tL*;D88jc6*>G&lGo-)m<nojj@&3=MUwHre`G~{ZPWXMd-B-(RA>aPK+o-af{c(wOY=6&g_a$vMe@Ak986Df+?dSda&7oWmQY7!sEcN95T;J}Le+}QIB>UYj^L@SH?^0|@>DYf;gZDG>eM_=m^ajn>>P$X1ta+IHzs7JnQaH~$;rtz$G`TK4Pb&DXEZI-$&OW|F)0Xphc2d%M{%#)M-6i{#4)OQ0_)gC#9?$;KW3-;L*}u=U`;WWQd}#lkQ|VBR_XVb{qw-Yo9c;3{TIKI~@Exq$)B8N>`8zyLOJTfEHKH|-Bk@b9ecSMN5XrvcOYKh{k8xx9z)R#Wt{BDXOyKsg{Sf<K7t?%@{C634-+L~N4<`OD!#0Hby>!cqzUQ<5-AA&&EsDPr!ry%u!QAhqz-U@8n)i6$JlS8Elb$ye{9TDH-*@(Fw{-fu6{#84cZXN<cU@8-kLTyGjvMUH<tzo=J=)UguX=9n%&r<mtxH;wPRb$m4RH9A9$|`qc6I+JJp(HJfBi{MwenT|uYb~$WaS~Hha`QHI0UD$;=RSGEd4BT2u|z4ngW~x=cYvnP7O^7P7Rh2f<2+)+MYNT{01TT4npu<=qK=9@NI<Pk5F;#kI)og5rY4gI0Sp(=c&LR;P1FsasS^Df}bM<UqJ}I2K@}a2EK|A`~fP;=mRu0ScKpgPziiVVtoV^{v#X<{uk;A{ugEW4Jyj<8$$3iD{eq<LEnJipsWR7fS!Zi0iOe(f!+n50iT852A>6=M+m+N{RsYu`nZV@d>tY9DOA+WQydHa3Kezp6(RTw^f~wo_@NaSp_if0!Ou~bf{#N_La%^Ng5#jqz;WPH(5v86;1dYJ@z4+852)98>A(6GyxodbR&0f?0B;3HL6?D}z+0fp!CS!F5Q0})p+YA?mxCvPCqkEjCxSzuE5IS(Q0OXfKj<{*D)2P02Hg(Uz&ow@9eM(~-JuM(qg=P6EbQgH74@(cWnr(EDAZdN%EDfcTTstiP%g(2f{!5t?|`lZ?*OlMD96<Z!Beg13+)C~!QH@}p_9O!!5yI!!5zU}pdsKc;O@{+u)W*`XZDn&tXAZO<_G5m7lg{-g5Z460^oe$OwcUgOyJiZtZzJ+MF`#pJpkSZE&=@sTmn2mVr?riix8X|ni8BE>;aXe<SB*zrGlmarvmqfwgLAC7x&=u5#{xd2kR>jW)Xt-Lid38f{Q?lgN2GT1#h%etP?gv4e)00CWK%edJn9F6A^;bTWPkiqL~#v5Q4ive+72|cYxLfcL2AsqP!Iit*}Acfo<T%&^F*U_}#_`!R--(+d_W@w*_~EHUoDAcZIe9cLgiZdSC_I9U-`;6{oH8NGIw<;t-tKgEc2OGuQ{}2lfG%hL!`D2G@et1lIz$g4P4K0(XP90JlKhbVCT9h!8v)+66os90=_I4g?Q`wgC?W_lC9u_XhWbHU#$scR~oR3@r~9S^!)bEJM?SWv~}iv`H@<3r;{gHNXbieF8%8eT3k{(2d~3;C0YB;C0||gy2zDw6o%8D;il*--^aobj8nvwud$bw+H_UZ3J$Fbbdt$u7MC-4I#J{v>kXbbSShPcqn)XLU3znBXDc*FVM!|#<-tf5Q3{C1lL3e?f~ry?f@R^P!?mMbHHQ4^PwBTLN|lwgXcmwf#-r}Aq207>frU@BhW<f5wM96oWX-tw5JScR|UWsz`oG(U|(<*s0~~N+z8qjEVMni5x6r#a4%?Ea4&ElXh(1#@E~Yc@F4JTr~)1i9s}(T9s{0)5ZoGC6D+hGxHY&o)DK)6Tn3sGTn1banhsnLoCPYz&@4C>{2C#6gB8{^Xg#!A&rcH1X+lR>@f$QfGz~Zn&QA}`15OWa038Ev0A2*$0A2)+fu05neFcsIXZ7F^TnH-0{Xz)A6`?-hir^;D(%>fGzR+6WzTlzIR^XxFU}!h6(23w+@JfW>Wzf;!W#9$SK=1<aOz1%HOmG;qH#iJD4%!nu4m<+d2|NPa--@51)uElhLMwxX%HZnYqEIhzQE*16822+m?}J4M&hEh>_z(R2F!&GfLFhX0LGT)AICu?sx)nX4fzWVpIL5(1XnSxVxH<G!u+SRd=HR*r!DXS<z-7VZt*8ZU0<8uX+6ru+Kbjx}_qJj@bTV`>crthjbSQWVI1D-j90s0%5Znja8r%om6#5HTXmxN?aBYO(3ecM13gB{9)PuHw)&vXf03Hq<4ebCHIu<N+K3M2n@M!RG=q&JXa4&@58PN6M8Q`_hBjB~*Lr@cZ2>hoNIXqZ1K~1nwF;@u|>I=>UE(WavE(WdvZ3GtD8C(PW3qtS!XfN;pa1gW)I0!r*ItV--JOw%&JOvyM9Rm&rFN974F9a{QVij~ObP`x-Yp~GT;IZIg&@$j*;C|48;C|qy&@AAl;7U+2Z&kvv;KG(>^I(m|vG4^8-2fIk1{@1s49x>x3~mTb2W|-Vf_j3zz-c9ZZVi(7IW-7gN`znu>M8yAPjCuo8nAs17M$0LtX5=(W&&phXF!N;=!^)#-Uz|Pt(a}aZYy>{--366-y!l_W%rN7AviBWaC0lXt&HZdA{Rn%cBmIPJ2)*gH8?Fe1=Ita0{qQ`^<NKW5rV%!KZ3u2KS2Kme*nLPJ^{Z3KZgDRehf~8-UcUvZ$dAEZ-UQ5Pl3;aPe7x=C%`+Qo54H5o1kmJo4^`$9#{iMLMMYG!J*LR;81V_Xnt@5a6YK0?|jg=U=f1zcyI{*3qRit{tLVpA$T5iHdts6@H}t;v^Y2bToRfCToRlcngN^vZ9X?bun$6Tc4$^`c5p6)U>TYhTn1VSnipIOTpA&`AT%?$AUF#&12_ZvVHSkooCv|$px)qY-~tH2C7{K@#Zh)85P}uxY_I~3gzf@If}^4Dz(W54M}zku1iyre{{Irkf^#DT*M~L-H%D8nj}WXv=Ydu5T<99`T<~h>X7Fn8Mrbs6BX|e&6nF>tIP@a;IQSg&HuxO)2J{c`4R8YV2{-}#2>Lhp5%>l4BlrdQJ@jAjd+=wd82disSnyY9YOn~wp76ZDp5Qdl9N;wIY*24-HgHZWazlNf-e4ba9%wFb7H9@&E^r2LdT4fVdT=UeT5u|`1Wf^!z@I!=#T@VnA^08i3-}%Q8T14A8TcXeCHNuOggyqF;JeU7@LlkA=uPl-@MY+E@MZ96=n3#?@bA!_;NQVpp_{;4!Rw(Kcs+OtG!nc7903glM}S8`8-PcF{h|55Li2$A!PO9gy`f?b@W!#=Clc#k@DuO>E0#hRLid7&&I1b#051d&f|dji0#}CS1`G88R|eY<f{Q}4gNuUmLvw-ig9};V2Q3241r{oUg_Z#q0aumyeT>j9&@$40?{NfogqD*2d+#H-Gqkky-+Lm#_IF8wt3V5atAGnbvw(%>1Q!MuLkRYTW&`_z^Fa%M^MQY|!XH`*S^zAx1X!p7t^^(kjRX$_FMvjah3)|_053rZ-Vc2V-Vc5Z6?4*K91G56MOA1WXl}63`e30dxDI$EbS`)#couXucoujubR&2%cpY>HcpZ2P^f-76_!#sY_!u}2dIKB>z64DGUjko)J_26@-+{gW-vQr;z6ak2KY)G)KL9_4eg!`TzlDl9=`D^0CqdJIMF{>5%?1`BI3>KC;FREW4)azzgy4*x{9aFJerRrRey|Mn0n6Y5&^%!KJSRBD%1=uxVy)P1g>J<Pgy2Qcqu@p0`OqWa`QX{m!{FKA>Ci*q>EICPL2w9oFf<k%i+m172!0@O2;L`g2(Eyi$AC*h_d{dA`@w%91V4wyf}ex`gdPO{3BCtC1ilBp1w9PD1-=SB0=^2q0zC@80*;63;CS!_=x*=@@LA|C@LBK~=yvcK@JVPC_$1hXt_2(5ZP4Gq+rS&3Gr$|bOQBQ2OTlxX6Tox8)1U$1Y2YCU!DXSPz$2}CA1CVG3h{rG?qo$XXfU`AbQm-kEHnZ<3_Me$)x^UyM~eT~|I+%ue_{-koc;&buD|L0*_`8V-mub2{)nz+lT_kc0Be2dNt=K1Vs@1N2gDRpi2'

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
