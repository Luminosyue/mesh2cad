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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_009.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_009.stl', 'source_sha256': '29513713cc9bca92876d0c87ff803ad04bc6cabd31b5fb46bce0a6ec15b0af72', 'input_faces': 644, 'input_vertices': 606, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30318817496299744, -0.4675174355506897, -0.34941691160202026], [-0.0008292238344438374, -0.15138688683509827, -0.033238887786865234]]}
GEOMETRY_BASE85 = 'c$}r22UHYS`1S`xMPuw5yQ?Btz~1X9Hf$h*J-RB^Xh1a9XeO~6TkPGnV6b=WI-;O-q}k0HyU}RuV*BRa_u2jS-Q#!8cm99QdC&9n*~>e3X6}3E&g@`7ryOoY75b^5bX>8ZSwLe&5s^<Rs*E2JK5oR|A!BR&7&gg8DJXsMW7DNwgS!Ouc2UMFQ@lckj2#^A)x_l0Y-l4dZ<E*1(C~5L1AiP48Xhu4`0WOc8au@B#||GDHpKXMl?JsMc$?~0^)^j4{SSZg8eK4l4og2{s5S2RO`)c4kK@lc_?pWu>8n9KFF5+@wvp1;cPE{5^p%Ky<Zl|8?C4wG`AJ_Zp2hN;-!_%LvgikvUpe;ahU`zP+~*yA{m3)vD_TvK-|Bvr+UNUOXL%M4lfLe9G?n?meW?ArYplI?^5J!<HzJR-_MY>lulnsd!H&aZP5P$C)zes>Q%A1J&yNHjX6=uRk-mB5jC7WN%`j?Tb!n8NZ}J&*Rerv4;XdZCt{{EAnA-v7=PfCHbDyOdtUr}gF3bGI2JT?zr9y=CO`(%BSwA0ckiIr~@ov^W$TLg!=lQo0?7W<Fm%g@aN+k3Da+AKk(lv|q^SC*K#zT%RY`fKaNngLxkF{4qdXjIMyN&JFgU#}|YnQw7{Jl3xUs+L-wbz@jr1oj^H?!?-eI>_-7IKgEU(=sUUs+v{<+ohBOzpF$vg2TFcvy~0rT%DkJWVl?(%0{Jv*W2=^`rJ}-fn09D?LH_F?HDa)k5}@pKBvKziMJj>03wYY@BErmEz>~Cr@VMO<!F=`pTh^Y`m$PU&hMc8=l0*x!&=H^wmlA_&D$1B1ZZb_p|!aCsrnZW-_nG)kV%zy%u0~tyF$5=MlYqLsr*H<j>MK&B<W%h8kg(z8XGU&KuSb-Ko9BL(V7G8!7RQzP_P2%|92%u=bkQRhl2Bls@n1o1Z2~UrjHQ%<^|{OY=r}WU8ZYvNn>w`MYeLZ8z6wIX@`fTu(asYQ;g)H$N<%#(dwNG!Il7na=W5?jn69`(qT_Zt6EQKa8JxfaP&_lfLTuQwHn*lI2wIb$ey9<Irmn)w^lk9_DZREZgb#S8r$infrmpchW7E$DBV{Zcot~X0iUX52AYa-t#B(-L}#GPpit>>pyL!`mNN0wYOw{qIx`<V+U)0Gn?u$_Y>A1wP%Jre<r;X-`~3zs2=AwV*9JVeJtz9RCyOap2M$Geck_s9Z&saFIh*{oMv{u)Zf}jU!Re|&X*ckOO8J!tO6SkdUgrvoA#As<3Z{0tE?kSqs?r*se^_~U)%bWk2jybavZCNE3omb9aH7M^?a51cut6sb!6$9%<4tExSi^8=a1Ci5&^W`<bUXTUGhb|qi@Z5lhzNPyRi1!oi$W<jSrr4^p(={X<adUda|Q$8uXOv$URVJ?duehzLwVLILrV3s;morN8BOSpEuK}E|y;1%krD=$Z@V0d>6^`T&N?*pQ<j|!uEH_5E{=fCvS4}^`1*<eC~5&zQqzx<FljdR+cBTJdHPXA=|EcAvcYyW##0&tpvBC>r;dW?eEFW@yxGNLi(0I>n}L^))Tkod}7fzo_F*Wzf9@t3s)sEe_ucHXEaT9^vwy~$RC_`mgNu3C4KAjFy5c~ALa2kd8V-bsP7UmkJXQ1+r564{Nrw{Kh~FP=seEsdYa|WT1@Mu%`+}B|57iS5B+AOIQphTU8QebelD8z=fhq(9xPsCbk;s%oAgZ+tn4@_*_+6}b|{VYbIU4Pce$h-bM*BGSy$xe7ap;GDy9_aYlU8)WO<?|O5c1o<}mAL^cd+|qPC>7{Y_1$ajTDG+f`O3(R@Dh80)9LwTkqW#i1FFzU6%->6-^XKEU#~*(=AtW&aOsyXMt9XkDkjiDKKGaZ=8wrqjFGxK)Q8BfsiHwq1R7IQjcr*#4TPhDu*Kk-@gBPHQ25-!ijdCfn|j=F(ReZraQGxvDbF%XLb!?W&hNXx(_(_Yli-FoTXqu>!oG|D=<)Ey3EWNhhd%;p(hErd;G}Z<@3ID7oj+IB4y|_E+0KTl(fJx7hwFWmV~`qi^uzsWg|qb?qzGPwV5Za=fa`2C_VQ%Z@aThhJjn%d%yctP}Ij5T57sCh{+xX5&G<)|2MtPb=7X(}s1DzIr{HkGJUsWIdZ2{>%1P|IJ1E*7V(cJYNh-l>b)#X7!?8XeWI=|5a8mx_*|fPt$ku?QY&j^HJ<B)=%|x1g#g>Ol9@1T9!#)+jpPWyCqm&uhn0FX7h>uvNc`DTOQ~0N#9EsrOp}2=PT1G=_^})XZxjF!=!IcZp`LG{ky&wX*+q@e5hCdDCbjcP$-*k^+ETgudhsE^Q|_<U;f*2wE^2NEwVAKD}K4a=5uX)2f3bCvLo2_LN8aF{EHh{f7C6}vfri}oA~^HYCEm-6W3CIOE<-N96<N!n|8-DKd3uh-`$q+_Wq^G-=v*)^vyT&Q=UCXk{o@D=Tf>()ecT|^sSR;lb>hfS(YEyBYk<yDMw!~g6q+(ZI_t;DM8Nj)|<D|*mnPnrgg<j&tt6p=QT9{C%PSG+x@(h{FmwJtbMoEG@s|%mcjP-uVyqqM-(~0wp%2T=AGLM_d5E@+l$iIPFBct^tI={bbt6~IP=x2<g41n-7HVVBeeZ`Ls@%$>0!$EFod<&f@;%z)$$4Jj~3=be$5&@kKZI&SJpmj*#25xhSK~~<l%nS&ozlOKVbf}=gE6Y`nLJg-u~EVInFGzGuipl^Yx|iy2gc{FVv%Q_%0g{>b8E;x8B;##)DS)uB;358Gkn3G{0o&TMjN~<4yO^q<R@KhmB|D-6>kPKRCt4vp%3Rt@8`-V)dd-u1o%d#dP1g)s6Z&;vB7u@(qo5^z|7>X+5_3I%{uQKaa-wfSxg|{Vy8%)Ba9m`TLY6zfI>9M_+L(OzW#PAEH_NHxp=m_4>5V{9&PVAKLSHs-v&%*hcG|dB-j}`qu3mrLX3SI>p*Q+C}%LN4p(o`6v8I&$ZhBmd5(odMT~vo76~W{>p{4&RPHDh@)>gWTyMvGP$Ez`vLvwzHz`(mdE62qWbd7V!pnz9IZp9`X6Tfe{zjJ4@qF{)ym{s+`U+P^~qYgek`fU`lF?+qWYS;p5-w=9Vw5m>8=O!wLHV<xlEPwY=70r2)d5H8q1ESR)015S@Zbu^gT@VIPU;EU)sS4@*k{V=Syi)RNmKEh9~gxP$q};wYW2UJS<G5=TZN*=Ho5sBt5@Mf62z1?*2m7sb$soY&@&UH>IyteZa=E{`psG|7;Me7v=nDy8h<9M)i_s0@eNB1LU}}zK)D{^wqFF<PV<8d~I8Enzu7{B{=%JzYnd$e@kM%aw?m~;qPbSnE&c7JufYBkogw#P8!d1iX^iBq%Nc9lErc}Uw0c!&uPoQ=lS;p(smO|^8LD7U;3uze!TxXYLdUREbsr_H#E+1pJngoj_2fiJ!8IdJDuv~$eFXupLdSd=eS<mkLT$>q;FDopJV>(DYSkadyM(Y+E#R3$<dqT(Jxh}?T#P9d^J}#-N%m_%k%GjM9&G%1TtU0mq^!}u9et+nRms~eZRFU-`^{B@ci;w3d=vlhw`ugHkGwsSCIM>_fInGXIq7y6O>6{zWG2BjrV}jERXpSUB|WPaGt-%G^&GQGg%%zW*D`f^9S=y+4X5&niatFZ>dc4LQR$V`c-$zZ}w;VYqGdfKe4X1ABU@PG+&LX$m&k9oTKY&r`NIUIAm?3d90)7MV9B66_n>)JLX#thEV&l4Ot%BeUqkC=lK^GrFC=I?<|jb;U`+3{H`(I^meuM^;~0E9@{#{eCQ9JKdL3|zsFfV&-m6Qf5~!MzfUq#p78NBpA^~<@91mF7@B|Z9LDCGKXsw@1yd4Od(2DLQ_r~nMxo~hKP-u3zRy22&%B$-e3MrM%}bGLqN8uSp6d1MaUb)H=}s2U)3Y_rKa1ZoUkNHt?e_)qewHdp&mR_5VZJ)<TYCOHIXRjgw<fvidX4po&9{EOOY^{#^=DasA~R?`+;1B5m3J#?J~3T8$MO&RmHegmxnHFj%}aNxvplxv5=xIo%vT>iq<JH9Im@H{afRlG597EW97XM~7iasWl-Wn~!$)7{n}++*d{XLT3Of$3eQ6%cDw4|j|H8!P8GC-rOWKb+m~VSdVzEx=c`BZ!`5|yF^R+S)X`XrAljTw852X2FcnI@t^Ne=W%=2_E#^xn^d%qXdU#uVO{V({0wv#`M`T7WY-e-DWjMbf5>l)>~@-UY9ua2;J#@?Uxe@b7E7{+|tddwP_m*p{iA4Kzv^-~P%XSo72UoAe$^OydQo=5E3&GVm_AbquW0L!ne>&50J`~EI3Og^3)*vCV~T;%86OwScg@1p&5!}qVFEOCy$YU)MxyJO=;M_(V?HtTD7l*O&cf3+r_wZDzJ_Fa^~{7=PbyU!2CGQZ1Jx}Q9g8pHC}&Z7I`aw8HQeJx`a`6KEkIr`Qk)5-5$h~?4TJm~qP&(QNM|6aPURw|~kJo?!~v~HQ+JK51U*F8w}p7i7#YmfQCYF)s5bxjj$Z;fPmlpd$>J<Lt+FFHx{K=F}0&+BGX?@AVHZ>mAQSvRxx%44ci+x%niC+b&;+{g2jXiwMo6Wy3^iEcx6iuusqpUlfN9$$}U$5a0$lg4%5E9`h`i9gXet?9#jWx`k*r@Qm<^Hs`&@{G*neghNLYuso)9%kL4?R(DW;|=qG+IBA+Z?<|@mTh6<*<A1tDXz=*_SNb8Ipx*{Rxic`L7$h|K+g*;%cws+n$r5b?wUA9-x5yWo0{%M@b(KTQyo=0c!BxbD^NXV&5d{TZQsu-t;Qxe`pW2cR7WB7+`{IY3!j$0W!u{r)}PnMseO!ZqN8tnZg2Y@$DYSLiteLxt1OS&s}Nn6x2!wQ`srGL^6Xs8^XT+k%=Z1ez5jJ0s9vU4WqGvKb*UclK9YUA-_)TzMMkhZ=ElcqeLi~KSABiVPL@Y0tm3_cWvsp4u_fJaZ{Nb(Pr5*L@lz)A_5HC_U)RG}9#dct`D=>v{O1Dc`iSpy?dRp!$287wZf3sv@*&mH-A(Lx>XjCduYG3cQB9`rDfE6#`FUU1g7TlsX1;YyQ>weL4lIv$%Z1u|gt75v`@UXppTNeO?fn_kfkSLO>u=KOJiMIG#<TTGbn4gYMSpdgJ`dhX_x*bl>3XL5({rc&9`TO8^}lxXTz5!m*539$l_{u1tfOzfMDJ5+b1Nh|`r7@A^u3<BU^3foxwG`V_gVe(EPt(b^jz!C$Y_?QW=qQBAD`mr+upyjy;oz;zh@QJ?GJS3zsREbA+^LAN8i#ujjpo=0xz-r0k5gvW3O|6)PGd(#eGgOzllP=_s$b+yLUg)dU(Hg8r!dlU#Kq3gP3pL|C#D8z8K4+q-WE*@lx-!uld@JH^*82jUVXx(m9^z>G+<;A>LE6`z73IoPSQ|`}@I-{33<e{%Xy<s6Nu`vE!-zQIW=N!QL#7vhyrm7Z>hi=Sz)^qVX~720LHc_HnX4&5g&g@t{TyrRTyC>3lpSgwgeEl{+7Aaf4`FM%85FO&NNI>hMb$HlCHNy>uT{&y$U3-D3zn->F!M)r-2E?#FEPVvU(g;~DQ6Dt$}GGk;1!djHUNpAKJ{_*9N_<zD?*M_=7{kNnv=6IuJxE2XdRzn#R|ms(8zhLH1)zMfT*^6c9Y&H9s7nEXQXQ<(2Ek?QOAyi`Zux-gu+m)TMGtfQ}`AEEjROgiJ}o2wk8>vdG+ORPWdZqoJl!*=E?H?EOi<-b$RZ~TI;Ysu42vhCh^M)$3Y-?2RABzk^jd+*eKeDGXL+xqMT^KH+O`c`7?m1$q-`Z6<>wYOUG(Dmr)dfuPH^qj}kOJRA;q2=kmBzrUKr}leks*}o@Y=8B>?Wj%~-Dk(sI-xb4k0@`J$MX1F>Tl@GRKCACP-j)x`BM8O(K>R%0X81gM>>74Iczx_4|;kUUC$<7XX8yvJ5SHIFZW~PO>Iz>>d~b!8_)W-lF~QT$;-yGS~!jB&i35ZmjAbCdY|*8hpZRV=n&dZyr*Zo4%&RZ{9<~ZoIZg0mIWd7oTt{u1lGPm5PffQt4yM!ug%Ou<J>za&e2z2zo2n`tUdEhtJcwTp$F4g9wlWKU0=q9^ZZ!fYSG(S9&2oM$`cmPe7&AR>*3^~tpDZ@@98?VyD{^%rQY=XXVqWPte<^6Y5jRL-#O+l`at(zeZtPN{Ehyh_2F)R<}0%;RF4BnoM-)fGnf1{59Zs}pSJh$?0%lIRKIvH)Skar8r5T5H1DTNG``o|%zU-MO1kemm6PqS{&6wQ1Gnlh-#mLb-aE^g%JLT*OnHWsVZJiGAzKgIx9jaie%GnYw@$u6_5Wov%cDJxq4@#t$J+e`p>+QkRg&c~pU3sSsweZ6&iSeR=m{*3dh#>P3&n?VzZzZF)&BH6)qZ@QC(``$yg&1mxnJn|e%<W?>!<&FT4(xQjb;9fWSXx^jAM0b@uBsnDRvq2%|DN&b!^eZ7`ELf{V30-Gu&U4i{`cDH$2a$zeped!+d>BN7{a)O01uzr&a0v^lZ(1+k3Fq!?*bU;yqY(`F{HQi+6N?Z26Q$<M~zJI7eR%&7^u+_V-2RTNCO2D_|7!^?C7BFOAYz9_`i<YTv(YyrZuKL{YsQ&1U^E&st6IgW-E{dwV>mwS8}H@6X0?@;~QIaP+MO$B@6R0n1~1UqU%~FP7!O`x3V2(sn<E-W#+2yqx(aclc4eSso?FWqJ;?LSw$QDSdxz$vn>Ulv+#ePo#g<*CvMY{3H8Qo(-u9U-Q+Zk$k^8RHF9UnS`(Tri0UY{+}PyI>EezAJ0RNXdd`xJ8$1Nik>gwIjVg;;C&KnVlTekv2$p>@po?C|9i8@pI4WiFWYltW&9F89zG8sAMYL6&+i9cnrBjdnQx82`(M@G^YQS$M%vfLv*`yP`o29jo!7+;kF>AVi#Drbnq$3K+`T(}t-fr&bA8!;r~0z_&h=&Uo$JfyJJ*-Zcdjpcd#C!c_s6NeY`$}S+56*EU-mps^=0>+>dWRk*O$GYPW5H)k5hfw^ElO)vu~>}dw!?-a`tWYW$(XJeL4HK`m*P7sxN#0o$AZp-l@Lq<H4!E?Avv!FMA%R`m(oosxNzcr~0y=U#I%A_ur|$?CqWE%YOWw>dW3Ar~0zzajdTZ_ScxdAA0d(UpeEB(1<)rQDx{rhd;#>ruebx*Z&lAM7{sNKgFz9?|=KJm@{0AC72Ndj0iDejuC^Qv%w>bSYX63=<ndsM*LyKNa#ZF7$cS&@gsBz_$MP)8xam&0X7bdvfhaC&^6!*MyxerB6J;itPv}X7zbSi4mDz_5n<3};2(@wWW*@wV(?HS<{2>@Iv+g9h*?GqfzAc@H{v%V20~|o`xr6Ji0`4lf_oY<#fToz$>6?5{9;5e=+EE*I2Zk(8h9|yg&8^nJPhX|1Ud&i66azBbOHEBoQu)WKfvKQ7h|By!Q*i*euAzBPsF*H1YHjvhjTFjx)vOUb1@dW5<Cj$A{4q5JRIlZ2k0X35S)vl(0Sm2I2VJUv%ufuT=a+j1~$q~nTqo^73WNFfU9x4VT3nAa5ZRWa5ZohXh(1ruqV_H><O+6Z3nIlt_W=lt_ZFGZ4IsfE(dJ|E(b0PZ2>L|E`@!m=}P+-0PYU01?~<Gg4P8GfqO#hfqQ~`K^ua5f%`%mf%}5{K^uenfxm|~0Dlke1FaA41MUs21MUs(0j&-00S<=N00)Bup+4Y1a5rdma5u0&v?|yi+y&|d?gH)v^#FGQcYsy`cL2ACn!xSBZJ_1BZNR?JGGJe@3M~y*!7ZUBz%9Yepx=R;ftx~$gPVezKudy~fSW^0frYjJ`xrImZNw*qLhwguRj>%b@1a$|A_TvKdV)m=egpLaixB)4S`92ha5l6$ScKpY&>CP7f<HrRf<*}a0<8@eA=m|8EwBq%f%<@ba6AM*HR1_8AFwy{5!f4C75Wfd6<h^+A6y0O34H+e1baargT27jp#OlYfvZFR1y={xfIb7)0M~^62d)XO4Sf!-4Xy=!3Vw=XA-Jv)b&SY?5bO%A2X+O!LF<Fvz&W9fz&XM0(8geQa2{wga2{|zXmfBr@VC&W;BUd-K%0QS0q2D_1m^|khBg4_2Iqp-1=q!~5d6}J7x3zW>p)+D>wxP)UxVv`>qFmx>w_CX--8>08$&;W8-trcKY^Qpn?pZ<n}eG|v%yWlO`vbVO~4JIZ@>+~4WKW<FL5jccQwM_h;j(Q<)MM#^5BZl?%;~xO3+|%C2(bE5V$hf1KJJj0j>ZI09OE;pk2Twa9L<)a9MB}Xh(1va4Bdfa4B$UXjgDo91FqujXAo2D|sRW`$G$ZMF<Xr76FS8+#OmBEJAQFv?y4F;2>xrun583pasDq1P4IB1&a{e1)2{mLU3njUa$zk9iiWVMF{Q$%@59x;~}_%5q?ILKnN}gZ4WL9{tns>{2jPB)E8VFTm;%0Tm)Pg+7etCTmaevTmYOOs)F-_3qo6g3xW$l+kgv!i$dFii-L<mJAgajSO|7Ej#VC4@<a&sgXRW{5ZoS`3oJr#J7^BD2*JKkSFi}dt)X9VoJ4%Vu@U+i+!EXZs<;xj0IN_Jun57epl)Chg4;lIf<*{!3v~y(<9G<(Y{VubVxSwqG2m!~;B(N8V4)W9Iq-Re;0w?#V4+*V7r+-0f)k*Bf`vwc6TpcG!70$4V4=IfDd1Fu;B@F-u+aVBbZ{m@a2E6cSm<GJ7WgVc@HJ=@Sm-hEHSkS@;9Jn+V4<hLx4^d%g8zn|1`9n4{u_J`A^0v-2Mav|z6-vC5Nw5>1PeU@wu1jc2)+S53Kn_<d;@$PA@~aP5LoCz@D=c7gy0P5KCsX|;0$mYLhvQ%Zm`fD;7j0Sgy1CTcCgTG;3RN7LU0^30xWbhI1U^OjRA)nB^+u*CUg`y6P$(+oDLlg7WyMN9h`v>d>J|xEOZ?BGWZHY@O9`Uu+X2u*TFXsg8zd43Klv8{1@1Y5PSzZ7cBI5@E!0ygy8$og<zpe!S}(B5P}~=SAd1C1wRHqMF{>Ex&bV76Zl{7e+a=Zpj*L0{{+7PzeWgt1>FV~8UcO<eu)tL9BKgz-3WdTeufbI1iA(+bS3x+_#cGehtMTpp^Lx|!4D9E??UH+h0X!r1^<l@d>c9wEK~#E2H!#mz6qTQ7CI4p6MPLJ_$u@#u+VVuRd5zG6MVpk{YH#{?g5Vg4@C$b2Hgu5x(_@IJRBkT2k1et&_m!Kz+ni%6QD=HLXUzcfF~ma{{lS$7J3r=3-~vL;MveKV4-Khv%w1xf)_)h!9ruei^0ngf>%Lf!9wG}tHA3Kf;U6s!9tV3o59-=f_FfZ!9p*AcYt>z1n+{Tf`z7lcY${z1V=&>!9o+jk>D)|!Rw$G!9p*9*MV0f1TTZ02Maw1UIzXHA$UGi2Maw7o)4ad5Ih}v3M}+Ecsh6*LhuymF|g1m@D%WPgy1pI!(gEYz+=E8p(DU~jL2<71E?Fg0k|$ga6M>Fu+UuKdf@s9!HuAK!9w$a8-W`m1UG{g1Pd(;ZU%0S5UfIrgN2p=tKe1$!EK;rz(UJ`+ko341h<Epz(PI1?ZF)pf;&My!9uHnJAu0*1p7m)gN4=r`-1}!g1bX&f`!%rcL(=C2o8qU1`DkP4h9Dy1b2h_fQ5R4yMY4`g1bPgf`xj4yMQ|*1p7fNfrVB8`+++k1h<8j1q&?=ZVUEB2yP862^Lxm+#1{xA-Dy!2v}$Va0_r#gy1I7Z^1(IfSZ6DLK}d4De^I^($k1O&>RTC3e*MM*9dnbdgFI{<1-hqE7TqQy%G71=!f6!htJ%>-$3(&2N)r~Htvt#?T^p$g9|~6f(IH=$_O)l*No4Kg1>{70uMH#q7j4eyMypqDR6mcMeq<Ksu&T1-wnZM6~UE_2<YVES~SQ1>%SiUzdxEhh>rgevGZ^8ugM*MbD@#T{-t?9r<`KmG7hk-oH!?mGokz+tWdSh'

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
