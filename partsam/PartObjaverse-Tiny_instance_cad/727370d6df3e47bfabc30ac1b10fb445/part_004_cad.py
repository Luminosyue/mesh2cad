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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/727370d6df3e47bfabc30ac1b10fb445/part_004.stl', 'relative_path': '727370d6df3e47bfabc30ac1b10fb445/part_004.stl', 'source_sha256': '23127ab255e19c72f7bd3effcf47b10056747d9d6c10ff0fdd79242bdfe07abb', 'input_faces': 1070, 'input_vertices': 679, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1586005538702011, -0.2283795177936554, -0.41162630915641785], [0.1756604015827179, -0.1841677725315094, 0.3447117209434509]]}
GEOMETRY_BASE85 = 'c$}r32e=f))~<V#lLX0m$Qj8wG&yIG3_}(qN67;yiXb9L78n!}1rZS?3G^mO24U|_kT6INB2f`UZ&$Ck#wqT;&vT#u=RE6t?|i3NRkf<Rx_kE4)3QmzL>VmklgHXzYJd5{wq>bEWo58N_ZdF2f3H3xN)8@6Hp)ut`Rb3>dCl83YuPc%8f}d))Vt4!Uc(Dj@fE7pw^E_vzCwM63?DhX$KdWmhWGBH{Q5lxj_Bk1Bi`sSw2%9_aD|GMi~GtJDejx-`yc*E;SM2`xY^!at~zTr{G>EAYFcbfR|5-w*`q#Nt2cVSZ^lT^cV5i&eEaxZ&v&BJ#3|oinacB>0p$-V^=~K}>*?xbo*$^&CSKnfT3Y<4yG?&o3C|C#OcH108B<K!H*W0tp*2aQeS=n>@7rA<Hqv+cRF*u69>#dOHj&X@_pALt^Cm{W+IQMC5Wh<`&$remkoMU}81vG;;~OG=Y$n6E^9?e_seP+<J87TrQH<d?ZRYvG>nF_itr{712yU>%&o#`Lm-d~a{fv2OKTx8N=i7rz8ou*dFJr#p{M~Ab-~L-~oc4GB?DpFK{k}0T?OO@nmHaW84L@8r<{Qpa;7wz`+P4e$m-eSF8NQyE-Ka^N(Y{J&$y3+y@&~{FTl`d$J>Lo@jWhgo<IOtYTjjf(^WE}H`V9rmdEp11%`)eOuj}Bu_OsF6N;=J)m(HJhqEY{F`wU}^d4>DUG)DX~$2>o@?WyGXWtA}=?FSytHRh{*`^lVm^XR(iI%wY-S48HuI7Y719e+r_*FG`krG4wpBBTD=x9@*!%*%2fOZ%9wjPV3^KinO;|APx-;|!niShcg9_H^HU$^Uvi&kwzGMe2FzuCae~9_<Ip^oX~;&ZF~(^Gqlt^S#^2^Mglj8+n4mA4;C%H>G`tI@121re6Ed&)1E0ciz4l7wPLfx?g|HRb$`k{My(1Hkhu4(O#cpdYsnjU&T*9)~p-8?pKd9a5iM@AKkBY{-Tjb_Z#-9bGSYi&l`DkzuMPz(Ea)@pObl6Ef0J1-c(A?w<~AFf7H?QL;La?et4X^4%g!(|CK&od*9jgUVG<ejI@8z%JYLScFMlJb5iPj{!QsO>HU~U-@4b;^ZmDv8tt9?oju>_yxwRZ-X|?$r9SsgNdC+Hy!L^HJ7k~VKPLH4j*$En4jaC1Z=d-^?hB8ONdB8WB+u#uaglz2@%Tm;Hhkyb7M^eQu3)xLRbT4avYz4V{jbL#d~!(IcdjMpN%bqTUQZ9m_$L>T^Wo2|XT1KN?U(l4cXS^6#a?6I>O9WByN&!hk3T`Q_!YZKo}v#=NBYi`eA0eJH?Mst(Ju3xCx0O64(T^VL#f+}<8hI`K38@Auus2wJmEatAFYioJU^IftBmJa8(FVe7vmy*eV_8}t!1<i*E!hL^L=SH8|SkgkM{LA!*x#gy)jNb9y`N#;@>KK#Pcttjg9o3-()}g#@&rG+Uxv`)5-L$jOS``$+M+IY^3j8FY5XB;arBV#~&W2Zm-V==IhV;jrixwNdA<+#YFmgKL_h(I&HM)+|ct4W&heZ2lV&@xz>t*vWk~KP~|{Oe7@auo8eorm85<5wT7?98Az~QuE#uI8oqP?fZ^-&%9pn0=}142pt)S{oO|K+Y3fS*JDuga%lC!&=gLXH7fwr^3x8(R-@pEES>IwSrTv4vGM<Tfz4diUtdM^1<(E1SEG74mQp*hA=}^=3xxVaVF|u!~%$M~Y_`bBSwm&95Kh%7S;p_XL&f}{-&uH)K`DKjZ51TIeQ{OgxCsPf%zM99$xl!{Y8K=Lxtot9AW&hXyP}+}pTk>o#8XKP<I-0}q1EZ&Ue(+Li!?)hfBhLw&Up?z--4BfO#8>U==}6z!=U(ztvd<gL6rbxc^!cH<NZ-=u1LF@hnjzyH{GPOb@KbDjzLjX3;fM3jI}>O4-0#BYThn)CzU1+RVq+tHy|03S8*xVaY8~bI@apep44?Yz`UF}{GtOZ>FJId!;!|h6Z?*4a8D-?xzV27&54WG5TlQ7IR-W&?K3VFS<ecQMxi==#*ZbVxF#YLB-|1OZ)@xjCFOS`EqLIhf>W7&4e1GpR3_mb_lGJTNzPLzVpSQuMS!8`Xk2l%}29%DA^sSohrEaszdE@bS8*8)=U#HrC<dgl7#y)NMf6g}QsePOGvhaTPkCA@=$R+3Di)N=IeOur6sdJ#$DDe}XmpY`o858O2Jo+39`|NXFXRGfB<2lFKU-L|)ug`yHQ!~TY&ohCQUCj2(*V>xS%+GvvJ$-KukvzQrhWF2)LFT-67LJY2_npWVukXK-((v_obidly&(HSQI#U1P{iQxp7p4A5w!}vII=_86CSKqFXusiGlO~ww%&2~budnO>%b$Bzo&zWLF!wpvsrCc!j5e+#-_))$9xJo#&!(s4{`Gce@jn=9>`(1G2{MXb^_n~%zS~j!4+k6jFznMlRQQqX&l&9{f3h>ib*FtRWt@z&e;K(RXSFkYyS;7ry5I1={iv19H)&&eeopnXoJ)(F80Tu}=_R>8E^TC-!}@x+mp737ubz<ctU4SQ>Dw8P8TEI9^`w2~BXT}WzG?X3=lmPL$^KtmOY-F2FY{`UL7pqtR+sigb{h59zP+Tc^xNc&tjpI`r9I#8*@q6x^|GO|kw>pf*#D%rjI;7}!*`BXlX@PkF3*7*D;jxpox?tPoI;Nc-{v{ZzqyH#$G+Z6&WG)3<lO$gy!0C*&u_j}ouvKdveKUKC-uDi+e*uR2-ZF5^<Vv;Q{Ly@#iae&LGrvYr}WuKKhUU!T-RI9%6YiAi1hpZaH;bj+0Ga~?`yt^w$WanOL{zE|Ep@=cznladE@c@R7l48w4Ln3H=E0RkK~i_@O_#dPv}%m>G!RG)Pd*WupjkqyzQ+8>E(QWE9E&)<Fboi?gz=!_^j-ovsq=F6*kGbRJvjK;qzxhOR2*znPr@pOY&TIT&|;w8I3%_f=^CI`hmbW>6iDraQoq}$$f2X3U8cFD801jxh3%Yf~@<sG{*Jl+`1$8!JDs0d;L8yc|x~SN_|RhlYSrOl<Vt$Qt_`ol6h4;6cg#|=RKV#@G!B_KG^6-d5(RO(D3#52Ejk0WIXwIi@&43oEy*njrRJ{-)D|bF5~?Bh3DHh9+>Y<|2~)Yg&gU3ZQC=EzP^qEyHd%1OY}54@_Gy{?kV$4`iGHUKM!l)y8XNO+ls~O>*wllp1Z%vK8gC#Z2$WmIZu8+X!y=O@%`t|$a87($C8KpNccS>)kDdnzxS(B^<1RyjFs;RgM}I!z8y>{?K5`p{9x+)lIQUa8UMN$v5~$#ccAPCo@1T#cP0PF17ti`?i;?oFZhoCB<D<~+v0C;DtSIGY4}dL?#B4Fujl0}(n!`l%T4kBx?;S?z3l7vKJDwDr}#3rm;IUjy7c?}vhh5recNd$`KMNsed7C7+V8F}?FTn8eV%9h)v8FH^M#~ezE`x1HZ*;%J3XFYfr~Q!_eM&;Jij?b&&hc7a}M`S?d#_gec$w#IAi$wz8NSJBR=<iU(>X5UX?#7e%h1bXQ^!X`uucem+{6Etaw7&SKcW5B<if}!z#z5J@<DjNdvi`Ry!i?Ypj?2_phIc^lhH!^?kvvdC16PKW;1c!CD6-k3LuXw~+RA_e(wPb<*#}$8z2_+AVn!HI@70q$FOQt)`CjTXloX>${9{e{c1p<mW!<RF0B!sm(UYQ&!IZ(2NSQZ#!=?>fns2Yxw&9WgnU&_tReMjef1Zt)>0&PsPt*%k^Scl>I+uxy&nHIq^%@lkrbpB!2mV@;;lRjkKRJN5->1<xy`uC4ZKmU(B2>?f1Om`Bv@Sa!$^kW%y2;P4fOS?>(9Cf#lLY$pd+RT=cfIKlfbLh3{j1OQ%Y|XI{wu<ojV~SwQA>BB7Tj^g~I**X@0O?~?Bsf|I1*qlsla2Xn{o|B}w|1DF1k`mg;*&d)V(8Rxcd&}(t=`JqX9<huB3wB)}f=eE_kx;&R|9w_Y}+%m4a(AELQIjOHZ?Fat2W?pwczG3)w%U9(3+SS+a9bXx_@9*tto^L#_YTwC_ROVH$tel63yBOzK_<iA6C&`mJv5dcLEjjnjw3d10h?4Q=X(8v&h34YllIJw%cE=Om=W7im|Aw}br&a~&_eOp3&t8(}v>X%G)%4cCu5thJojxz?@>^{g&#5SH9fKuK#uz^J)aw}d-4_4CUq>SMq4xFjgZ^Gu`?{X~fG^JQziTb?eXXuHe*4cV%=eTxe*dWVzfj|M{;DMHw=|dhxm!v5zblB(ehA$>7Hjx?KkVD{mRC1_R9VR%`>*jmjP~_&g8trE`{8xu=ap8X(vqjyr!xK;mE=B>yo7Pi`=(x(eVe+7an3uhCzJCtZ6V`%!?(3~tl?9C>$zk4Era5hs4sO$U%<FuSjCFUduYad#&sQR{e4WNukT;_=e+(bdBo?v)j$8V>GOTB??GFyo`IY>#c#b_>XW^#)WMfs>QA1~h#yWw`ql;cUfNFB!1IH7vr3)${>|ApTK0K?%#xqFS<}}@`$8FwdfICa$T*9pH`?2a7oUjq^?Pe5dj+`<R!(ZHm)_^v*L4U?$t~+xEwNEIEAE1<OO1raJ_%e*WB396z44>gGM-vd(r?ZKGR~BB<omJuFC5Pw$@jpC>v`?1M$etdeWI^B?T6?4(<rG=%O~Rh`b5^N_$j$xw0j^v@AdlUy#B6tJU{SCj8O;e>wV=6DIxpcf6FoU^Nr)Nk-mQ4_jOGu-&gd!;Y8NWe<Y{Wx!)Dfcc`=dq}7Q?UqAl`%IB5qW#A=g&v_EQ58{XSNz%Gr9%tAu(w=$Q*~)u<X!L1m&wa<Pu`edl*XyExufR9uxD&a5bbYjMXFDX<SJ$dWd;PxS?;ds9$aCjs?|ie~ueGM8`aJEZQGfmZqJ90`75FP!zEAsLpXAr?zlBOjo#*V4@%(eis84YIE@_{4ulVcs$$nn8)!bJtH%lE>eJ6QJZxO%eztVow7t)^RMmuXIxo<`<6JMX7Z|;!meg9&~gCCf*Uh02zp3Il`FW;P?oF{k38}0qO#!H@*y$#>G-%ielw0^^Pq8iHelBJW8Ka{?T<mu^?_J@-mmCt)6Prn?7?;rKOjB{`%$)nr9`vvFNU%MiGXY&-fuDc%eeCwb*rv-0yk~{-<814Pfn~FdFTho7~rtI4Tqdec{K5LKrR>paukLNo)UxoTa%k}c0-LA;%J<#fBsY8<bMxM}@v!u>-G8w*gwx5iD^u3+l|E}}g>@4H?a=+(W*W~^l__KwK|GS+#BlnMg;E&>8U*P$+es6vKsMPK5T+es(^V^a|;%6Ho?e+6jt&1|>BE5|EfrBGtzGXX0zkkX(5L~cS@{G?X{@-#A`#)MCejvBZi~Rn${*wRv=^dWW_2RqIUE2RTbBDSvt<P%9`@*YLrTwPSJ0pE7ZFQ;h()Y#xx{Buq+s-)d<xQJsukr)w<ovXIJayD(Uy>r?KjXc4^^9osIrvXW&$m*@dFXT*vR{1;Jul_?&K1t{yV-VopC43`JW1vL6)JXYpO@!uHP5#b$oKY6?X+J0zztjSB$9L3c~;zOAG%sw+FzIT^+hM#WB7Nte%DX)^7t<_lss|r92Lm?m*EHQvma7_=;g7`G?hFrc#fLZ%9~d(wz=U4I%ku=f1<VIr#}9YN4#-52RexVQ1*k9udwvHzmw#7%6>RoU)t~KBKa=LJ`a31*=uh{cau7wm-i+snA00)aHn7VLvsE4>YVo4`+n?c)F+ho1F6psePukq$vI<B{>SqJo8B<$5L#W{o3FEOu+d)6%lG+6!*{;#>G}R;<HY}2-q(B+Dtq~zB@-n7*%!umocRG6=W%&23y!+!82)8BHv*rBWSleKll(Uy82imXeU{Y0Nhkd#Oz!PB|CBl6@00h_K-&beZzs()>zTNK?8C7OWSrYFN}l4kq9c7h9=#s|BbP|~-D%`JJp6pO;m62(iq$QP_t`&Wxv>xZmu;_KYfw<yf1g$Iv_2di>DyZ}%lq%{5vIQ*z31CybI3URtupJ(ItF{L5uf(X7n%1&`nvx1+s_O?JkGKQym1D)t~1s*u%nCT+if;U{-5M~1K*m9vfo<%V2*!US;G&nSEd=B@5>&N_U~7fy1jqKiS+e4>iWOz>-`YS@~ezzc`?~nJ$6M$`u2C(rG2X0`;7L~$EvX3@O6G&Pb<?^W1NA$j~&DRxU9_UWWVT0UysMC@r&W>@q}(x*%zO0?|WUYuk_cAe)T!2eVt#QZ=tj|W&G=NOZ%_R?}^V3O@A7%AM|JPKKqj2lYUnhka=Z)N3P!__hmoOukX|oZ~yxeJv4m#n{=|Tq8>}0l|>}~%o37kN_(02!qPIH1;@O4+LJpPzBBZ$;p=@EY&}NSeL`n5Pt#=4k-lDEUy3~YjP~q9=Sq!ueaq=&_<En~^HBTxI&wa#Zj48dGxSzR&$q{Q-50rD{?ompBYo@3eB$@sA@{*C-3?#wpO<}Kwm-!m-fLgvbr(KAU-Cm!{*Kqz_qEWFJ~GY?IgNGq59%lW+B~wpXCCa1&-ZV7Mb>vff5Z39F6Q~x^%LTMR!GJ(?y3`??`v;GNBVjnS}XS(?QQOZp>5sd^Ocjvdg*gs`?|e8hqbTQ%PDx$@Wc0uCKKg3Cln+9JM#)%>>3^E>-NFHJ!IW4#u<KKZaulr{&Gfqu6MoeFZ%)eY`lIb#}nD-ap#S7v@iU&J3imqoN`ZmzHeS3!w+9Ctb5q!e&<ZE_QvPiuji6;B<7-V9r=S-W!-n&mpb!Yr?2;yeQU(+czu0chc-W!epAVNbm(jkxsJa7L;O<PjQi}%et4hYJ5}U+c)Q36vwed#=DKfuYUI)TO8ZXTuf(5U$81lY@P63vOxkCX?>F?izwGOEf7#d9yKn73Qs*4<Ua!~vWnZtm_5->2-axPW8cUvQ^2vL*UUzGC0vT^H`F<n3jxYIoKfLVg{opJ}E%(p9bEFQl;^hARaa!rO*IeWIU;Da!=#7V7`@pPB(tZ%X_sD%V@NPEg_cOn-j$wbp>&Cjg?E8mxH~hfHw#K?UZ|4vl!|ylpT=BB6&u8ri77Q@<$;-appW3$<zai_+^Ob*UF76uvbKNKAm3}8rFxUMhKe#pdo=D%CI?i18arveFjFHB=2Syc^_8$*4*8OE)ulvisUiV<H3gUnLk^CHr`fES%<2&;60<H_~JBP<gd+KlXs3h(EN9E^MjZ;KN`qrR5@_QzO?>UD5*<$(qBF^(bw<?ln!e;qBkhv$l_My(zr2QK|$?wH+Uk>{VK9ly_<=oJI;PZu&|6*-fuZ}fjy*7Rz<Jar{x-Ih>5-sifZkOk`wzZA%*u2NtE$U0Zv)0OZsK54|nc`bHpBU}!r7I-QxCB!FrVS;}xUJHDX`VfizWw&MQvaOO4Bz=`p43^N=ZzbSKm8jS|IWmFB7I$-z^}LDeZOXFnb#M`<o5^k{SM#W|HGlkbr1W8H^$rEy0%<?KcwMg)Bk-z{O$4m1ACeI(@u;xPaxyic-uQwI~(nTRbCf=Ma-edePvhbApV{$^7H!qF@|s7_{8vo<vWR=a!R~@pmZ<8_m%A;`RAXP@oe!MeqgI(_<>U0r2V)1WnSm&8oqUGgVZfSA+!Ct)$z7>E`4g`50&tX-zkOsUT%vd(UHFW7r#ep6*1adQ8SGE{$f2P&*;bU`wZOo!+!ojMjoedZ}Gb)k$%s2kB;;MlkOdg9FO*`c^4(mLV4cs7wjv3p9FH94%{4V_*3p4ip;P5!1SAkBCkj7+soq2@$2@Vo;(zJJ%)X*i<k2_2R0dgFy9--e$(>```dRK^U}T*z3ous^&4(a{_y#r+uvRiZ+m?m>GpP>0pd@%FYSF(_82~ObLz!LNBXv|TmP+w@2omu)LHuht|MK~u&=LEJ<ePMjr!>EXy5wkh|%xMz8+^d&(-BdJ$*R_^L@`BG9JEv(|)+$+>fFo{c!ymPq;nx*Ygcz9V+c-|0@0NjoK6G>+?|O5Bn$9%ervC2>YBfx?k-F?k+O=wK5Nv_KVIL^9uW%OFEA~!$_lU_U$XX4S(})WBg(N@myp4PP)<J|G3lW*G}`6j5GEtBfs|T3#*L$c8UqcdE&KiY5ZFT{>hN_;F>a)r6ReN!Rp&1;$JbKO!Y@={Qru9{^kC^{uKkIOI0lOzx#I#q!<}xS)<+PhYo<1HieaTgq6Mt2i#cX#xytHMi--t;KgtdT>%H-FVNNS7w`u38+Ze}9{n0#53fbPgxA8Kxv>QO6#WwZ6kbCp{tEpX{t8})egm(AKSx)?pTo=174UL+A-V`&L>(6riWi`7!3*H|=wMjsKzKg<G1?ziIuHIBUWzV(mr#qPgyNOx8h8!0SV<^eg|36wG5=MB;$`S^cscW2hAx1Y!JnY>;rWdF6LcxOlyQ85u7cH{1nTm1<8}AHn!EA78<*YBuen+rzQO13+}P;Gw{CQD|6(^c0_aRw=|^w?p615e=tA@(cp>~5p?Enu6J8F_Clq%@yTM)IhJ@lqXeYQ4+}Mo@Zj^VU3ECKL0(U_>!Cl~~XaEi{pQ(i6_af%}9-;VsLh&c)LiiK-bM!O#b9g1X99{`8M(4weVL#dx_QMU(hHwM8457Fz+6XQSmqQ!Fjj3HZLUC?FabC0noEP@Fkq51aR)8zQP0=QBQ@A_Y1?~>Ni%x~7QulWW#WT?N;TiB8Lh%ap6L<x@8vPtz4X;91!mHpQx)=_^Jy1W~1FnxYfa}Ah(K2vpI0vCPCt4QH3Fkt~!R1&R#Xa2^=tgfh`l5r-f$$)B6rp$+q4-U-C;TSd%#G$~FSIAzlRkP8iu*;3qaUHTKcRRqItU&NzlDy1--1V?!{Cwda5r8@hoZyaVa#DDp|~~L3~miqkC<n5v<6%qE{>Lfi^Ew6#hKm6h!#alz(wJjXbrd~+yZS5w}AVgz2IKdv=5>94YWV}20VaJJOmvK4}r&_Z^7f>G3ZEm3_JoI4v&D_N32JCLUC<3(!24h8->tfa3Q!3S{ts-->pL^Zifzqhq8X{2*uUV>Tq?|sT!fU2$}^}ngK2X7e>>;>6k-dv=Cevu8Y=z>oBIeXf?PRebgoAKT-eHM(GPaEB^(d_@*0M+=zDL2Xq(w1AGFFg-^iO(QEK^_&J&&f$(!UBcV7m8U<&D^`4K4sFP9)je;%sc9duWSgGp!Hlg@D8VjF?52Cx^gYY3V8a@OcCKT^Mx4=rb!F%8{=qdONd=I?|-()TB5sLps)%^cOEm(!(Td11nE#`Y3z6D=G55fnT&m}@}2t5oRW)30r3><=gNAJP+7}M|QE%+9FD7M{kwsoTeIv(x-PeLcdli&~Bn2XLvC&RPhcL>E3(DCpDcr@A;9u2p2qcU0*Z3`>4;i_;+H(o<)p*CC#?ud4PJHoTjN$@1*GmB6>FJjK~2*pbY#f#9{@FMs_^d0y^cnUfJo&t|WN5f;`R%lDO6<j5vUR4Oi`3c1Z2*m}_s&G~6Rgh4eHKL|j3B}pm$c~mmUxQ1*_0U>yJ-9R45$+5xKxe_TsP6(o@e*_?yafJ~P`nIX1TTX>Mn8l<hNq)b;OX#0bSyj(ZiBXh+rX93DsUw@ADSP|2d5<zr$!6Fso^w);!J2kxFGAH_)qs5PUY$=3FO&OX)ZJsoC{XZl{wIqXeu}*{0I3|-aiP%ap(m&4&ILLgSW#w(VyU*u!A0e9r&~xkI{?h0r(<(oKSoe{Rut_A3^uQN8n%43-GV-Q}j<*sjA&mJ}XWUQQs73UN{Au6!pPL;baN^dtXY1CWn*3kD^4?{2x(=i|`}(GI|_7&YUk3im#wY;3LfQ3ZeK3`V>~G=I{hf3ae235KRUrW4sR;+hzDNeJH-;#xpnmb|Z<~K5+s$GqS_k&_r-HSf4YA*xO1I!kOSSsLGuNeHQiK^`ba6*O$`2_^kZD2*p>?JMdNb7<v*u25&;Q!kggl-Pnx&h;D^{gm)8)e?d>ezrgp=JMbOqcb`yv7gh7W%V)(m&_r+|>Z@3V;@{9Du+j%n!YUNUpg+Sg@D6k{yqUS}AQbOKcf-4x+g?KPIrKh!pE;Z(6rV+Jz&9A*Su_Sd3-3pFz&q$~KY9*6<UW!ebYr#pJ{q0kMgcc+xRD#p0Oy8%XhzrvXCf4*A{3`YGr%d~bZ8DZ9h@C40B48uqb1?|a5Fc?qOH-AaBKKAv;bUy`MgFbE{gi#qHsYp6I>9^Nhp35O$EOSCnXdoK~us>;KXP;I5C_8%?_u4)1&#}^l%fj8QcVZE22hk5sK%bbK!aLkA&i#ZtOr8pmX5`@I-VhJeImoBowznUxQzxzHJD_ZP9{oTeuyX6IS{<+zt+)Q(&d5;Q+h}JqRn^4X=WiqC4On%yTKBcoI4hp2!>~p>5$w@MN?d+>S9#MpwbB=tFTDH&VNij8L4`ja+CpG&P(J&Wfgiv%*>2nC`~gZhS^4{uG@Ce+sW46t73$h1bJd(OK{obS63rRyr7dA031ah6lk7(1vgW_!Tq@oP~M4LMTpzCW8~f2?@o?(X?=KICDgOGZTvQxKSJ}gyw<^!G+OmaA7zfnib9m=S8!?dEv%rL%1<K038eurltc3#lz5d;bHJ7bQ(O3^&Uki9*s_im5zZ&!!6O~a7(xpS{yD;T}ly(i=l<#!qlP|p|}W|7tYK4ix7&Nq66Ro%(E$>xD`4I9>pA5p)KK7aA~v@T#7N3MvK5j=tFU=8$Y>m#*JUlBj``?5%?Q7s<=_Zjf!YBxFTE*tqhlgE4Wb=t&UcPEAw}%6N+uL25iH12*tI~DsWx2CRzoq30EQ%mqjbWW#JNNIk*H|2CV>>fy+nCtvsRFkM@TB@Er7Gcn-V^jfQu@CkVwqqYnHte3DQc!<s7HgF5gYcp(}MN7MI0Lh+kuZ}?5PHd+;~%9_<iZMZgE53K{&gBuZw>!Y<`y_WR}#pBTl@OXF~`VFk~CwLva4~>Omsl`4*aS&YyFJ#U^Lh*34He8$e3?~$iLmR=3n8P@9JUkBm5?u$cV@zM7K{!YsiYu$<dpDB0(Z`K0Zq!0+!nNQ`XnHskeAtpm&$F}A46q8t2hmip3dOt8q_7IbJJ2Ms3dQO<OFe@rP0VNICngkEMJvNq;T~?xLOY<9;SO*mG%1{vF;^lK*FZDCHDDV}52vSIHlesJ+68V44<i&$K>NT---9Q><I#8F@$f`+7Cei&O(YbzKr6wOm_rLfaVyk@ZN}P)P&^bJ1`lI=L(%c@P<S{x5uQkY!_ii7c{iT9>-yA<gf1s?W3wfpcng{UR-sruTWy8cqyJd{J)0?Bfj)(mKC}LNu2Za@^*%$NqtD>ya0SMw##(_;+#Br#_lD=7@4$25*>224r=st`Q{l0M;+AM9xFuW;Ee|VIb1TPZ#TC(i;EL3zI;!ebow_E1tHagMgs{>oa5cCy>W4eSlhK**Oy)M3P&@`53y)=PV+h5q(Q<G(=Fpl@+y<=<S7&@}(9Uohcmz5bo=kru(AKcJKdSp;E|+sgiPm=GBR6KaF&F&+o(qpchrpxYMrZ@L5nKq(4;O;f^OOq3XV5&b3dOP9j}*r+UZp-hE8j;bu8-!2^V4^ILUAv22;2*vf_?x`fhVCe;7RZ}Lh*F;BUtH&@N~E@ItcCy*FkH;wONZggyP(&ntyK8ho77I*F)>W^_g2eLUDI=3Ot4RbSD&dL&w46m_s+TFWe2Ti`IebFs8a_J-8lyC_d+o|8qCKMTfxO!XpXA1JO6&fp8x}aZfk8qCL<z;2v;4bO=0zzWWi1=euzLJ&t}3D?JAvhi|*_J9+^<2Va0UqTj+B;SuOacqDThK`8Ez_JRAuy$Ho!(4KG?xI;u;IuMFGqdnlxaCfvH+#Q~c&WC5i`y=YLpHO_3P<)<Hd=)(oAE#bd3B`X$)bwvc@xN|FMTtJ-^Y8FO_!4>nz65`VZiK&shoU3k5!81mp|~&F3+@YdBNTT;yTBdc7H9{!1>7F(47Z0nq21w5@O$WN_&s<px*y&P$DwE8IQTb0@jdiBd=Gv=DE<?@3SVVC6qj(<qM#ck-6(|?Mhn7);Vf<}a{taUH$HLWD|9Wo3|9IDycYhRP`rUqypmA77+nT0hG(FQ;2H2o=qK<;@REq}Eg=*ibK^033jGQ`1#d#v!fP4#CPMKxLh*KV1H2vnfl&N4x)S~xUQQ_f09_1!08d3{z*FIO(2wAE;1AIy@Q3hG^cZ{;z8_JS`-I|TQKGLz39C??k5F8|jUs4j^c6TY{Dd4T*AsG|f}g+_(M|9s>U)t;{42U0{uRE4{s1ez315RVM~SNao0)xF5Y7zeMN7a+i@|x}9B2`^2=mNAD7H{FHw(Q8Uu4`C?G&d)uff+CZ(7Ed7tTu`inF@$m)kC#tI4B8|KPLo{~#1!Ar#*t6u&@Kt`~e(T-uE?Xf`w}oRz+^5sF`p`fnVs5{gq0iXT~`YD|v^#i!9L@M$=N-hxB$bvM#PiQeJ!E%+95xI-u|%G}f(iV}(&M$EGz+8AyKH$&UO&ET$t;+}52fwo86!R_HDXk)kuTox?@mxZ&V+2Cx{G&`X<Bboxv2&W_z-*xBRvPo2e3<>{V|5uv-{Zaqif@S<4Yrgz9&3`;5@^AKabA|t5nU+lwtDlcq3EcmvFLWEJJF)eD09^`-w*'

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
