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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_006.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_006.stl', 'source_sha256': '7cdf12c0801a0cda71bf802a82da8e34d01415e559671d82b57e4a8472582464', 'input_faces': 764, 'input_vertices': 400, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12327997386455536, -0.40542611479759216, -0.28014078736305237], [0.12348249554634094, 0.499999463558197, 0.19579218327999115]]}
GEOMETRY_BASE85 = 'c$}r22ecH$y0&{0CFdX_3^@nMnI>o0NDjh~gXB$)4M>g(0wUlb${}Y2L7)*3QArXd&M^QI6ybOTJjm^@zNg*0|MlOs?z$J(x87&oUGsHyRdrQO%`9V^Bu<jq(tmlZ6<rT^vkH3XMQSUvHL};R;r)8_iYqy2$e0)_z46UIbW!s*&0;&mSR<`*g?jdi>oKfQl~AE-y(<+e9xBv(@UY>-x((_&cv#O~;@9ssAg-6^$Mx+tq?h-)aJkZ@i-*b<DIS^-`d|J_=~cn4zu?dz(UQ-<t?6mB(BQSA_Vl^xXRC5qUOT1Lca}{Fly@3NW{ZZeObV8Nf1~m3c9Rc?Z?%d!FRvr-b~bseHu$A9kBc8ZFg#G+*|E>$vGxxSl(%-O@8&OKe7Dgvtxt&&|1f@D^_?vRj32>|7Ah6YKmO?vd2N>|9?0(u`|+rG|CMx_|8C@_$y@8FYwG#sOUAcf{q%;p&s=#An7^-l@tN_-9}Z2}uI-_|J5%%fezeIG<2z}eT{rKqAKhX8KH!#?A9LUMmX+)SQ@-4{T7Fd@b6u->qeb#MGVr)w_jXU?J4Ms}!`x5YQOz@;pq9^mWP|aS98tgP29w|EcyXh=jy^c7{%^OwGxwGM_GXj6;z7;dW|3)!@UOMDn|jpPuYS?*O~1Q6bM7?nzw)W^t;N@_n(MZHYW&E@>bq52YI{C-d6&EnrJ(%o`KG+HXPogZ-;XPLEursb-lKk!!J5C!&fTUyzMs0uwS<0j+b3Gjz3WXoxJMrv-wN#xUU$>oPfYpTyMx!o54GMExG!f&zdgpUx<>oupFe6l%uIIJT<^%z{ib~PHRigJ)xFF(v2IK^zDvJ5%f8os|7*DM9r``gAf4%V>v&kp`~9BWHvJwt)<Mhr&sX<Ud(1fbTzzX6&li5=MH}@QC)SJ<W}JkQw$eO|6KD8AGfqN<U)S<s9VgbFvpP;D#cFxRiQ{~)<K#>uEzfv}X3SywJvyMF@om~Il;{uR+wV6}pZ0fqjnVPo`?SCBNB&V?^WPb$^@)D<ktsj5KK1FS{ad4u>0ftkJ<Y>7v7_5`ocKQD#P=h=*HyoK25p}Y@2oX>9;t8j{OVdlKeVGxu>KwIm~mqHzF&WQ`&R8hJGi;}nDG<6Vr%|iTI+mrAju}<UsT`TI9;!cZyiwIt+-zEzjkP^ybin70`+$nF4$)7_dvBk{r~n;RSmSKJ9L$Ku0tKlY97XOr0Q(fyq@@cpV3sU%=7Eai819Pb)Kr9I;!nfevS6;yoZ7EZb6+tt>Jf#Z#C9=+xk39cca79k1}ujzFmEV@!k6!Z)(5C>3UH?eJ8uFJ648Cy1taa_vc}Jd**^bdFTF3vyMb3E(nyjeo@~UGe+xwSKG&q`_haz_lr?l|8lf*_S<GWM31O%H=v#Ioy~Dt|Cicm`@9ij`q5dhzV(gvuiIJu=)%E){Nak)U)KD=f&9K7xjryZ&uG4treCbP{R8b5x;8@R;Vk&qc^>opZhWUfKlLx_xV66-q0eJ|{2z6k`@ZvfA8of7=G!fs^*M@F-`Y3mYC=ESxmO^+weTnNTsWP21@ilTXim>SJ?+){yo7&l6zDIv@E>L!cUu(Db~ydk71Mv=VcX36YN>B+raXT5O8!9m*z58dKeB!2rzX#zV|3hp+~Kg%=n~_*hn{Hp{=JQFmF%tl)75%k%laHM?Yh0Y`g^--`O(9S?`-TE$Zy3hGW`|p*-^_cE~MApbJeu7y`in~t;Z{Me%M*Uw1eHErRJG%!<3JX*<|ut`D3;G#EaUG#j5LkQMiu!H#3`gJMzIgvrdK9*3#=ff1%^#X5}5Goo7|k{Ff`6Jdx#3wEkVIYWXMYbsli?==@fplIBmFPyL74&AjB6%x8S3Lo0LL(4wWEoAOJ4-mB&7>U{oH`Qzq3mZ<N1Y-u~3!2j@qmj7PYsqnp<#<zN$GrpZZM%$rmapT)v@pm@8p3rw5oZOqR-=j6gXn);N-<j~}T0%cE?=vm`Qy#8++2jc~*rEQY$67wcOJ8dH<43~U@5P^M`Tm;&`JE&CKQVr9^=&)<)r5ZN;HE%5o%+p;Z+F<Jc^K#RPa}4lc51A?%{Y(v{_VIx{q1k=n0ng13v0hU(EQ=jQ*@u-Nqu*u=6CVk=P3fdwP)@sQ;!dm>biH2bvfTYU6<P>(fqC1Z@;bO-Cq-H9_Baa%gZ`{-dEphsPmieI~QN*x}8GjPdD{rvk!5;Ro`X)bnv5}{<%A0emmVvoj>=e@8|dZNU~?U6V~7T^Ie@kGySnUVf$FS2I)MxR`-w24feMW9~eJ;`B(KXF~7Y(NcXXq@PA@{!w>)PK=UWk`O_W0R?GcUeV6&u_uU8g0{Pu8H%xnl@81jL_kAnpy<k0ugmvB+duDgSehDpntn=qeE8x3LTIuJV_wh@!pTxIsOxu;PecWCLcba}Ur@l2x$4S)p8~0bgiLU$hjvrT>>o!#1-C7{vhu{Cx%tQ7>eO^M_;<P?X)pu{_({%yg&iluXgx7VN<~?ZYl}UYv`-<XQg=TIw`G28*Kl=AR^S%t~JLIwP-A^y9Gvn*l+3(DC7Nk0DURVE3_la$2x5o>Pn0i)L-=0Ie;YXJzQNJmlTbni7VxE_!>Ra0j1blb<*^iBX<UMm;H__XtwA?lGoH>)UecZfVO@3>=`gU!dPki4#a!$*i<@s&;+^k>rTJ`O%j0gNk`jl(T^(H+s*Nv2)bH-eEb_LTv_OIG*kvXRinfo2CzB8J613%Ivr}3jZTy3|W8BLyO>tZWSe!u*)?K;mi$6t2-yMSNp%<@3_EHyTn`~~p+^7wAiO@Z=uOsdtUeEv;=@?m`Il@Au1`?|aLqA8cL+%Z$n-R~LS8bhAPW6eIn-HQL7=K0&tG}id;nc|mB{;7-1^A-8NT_8^+^OI$!pRctG<Z*rf%D8vT^)t`CV4jD;)z6x8<Hk=n^(2p#E4}&r=nldskMBE!&rC~L-bwb^JEp!p@F^d`cdoxX+0=hY6}|4s)7oF_KAvc<AKUJ{xu0_nOnvNn<p!93f2*(YtylXSKh)((1M~NGI<D-Gb{{qQtNo#VS$!^i-#t0Q_|{~e_c!|)Kl;@)<2!eG-tq1BP3xI@`u(yvxsLPf_39<Ou7e+HyuFt3A2MJ4am>sc&h3r066W#!aO{DC3H|W7)uuh|TKm+e-F!dP>|~*u3Cc(NtXgQwcRr)O-!FaDcVF$)z?5sI^FX+7Lp@hX+1dD!9R&h@<h_S&%=?BUH{;X#>vKJ)>Xx&exsP8yykPuPmA)|Lf15C|W`cgP|LUv#b>#dsQ?Id%homp-I5~~KT<huk?kQ(_!t#-iZklmoUB#!o>-*zBond^&iF5s)xvo2V)+}?sjH~E}C(XDDC+@h|T#x*rzH`iT<fOnSzwbvbz8@@qr}BH|`q$nMl(+G%X>*pC*ID#AvSTZ2I~+{8)RgBrjUJtCp3~@x4#u~b2cp%AnRy_xWy^AN9j<F<?x*w2E`0yG_>ryO2FklH%A0w{-TiH#d=%dvQDSAn^5L6N{hT`v-|rXv$l09{^S<BMAD+Bx=3D!=`qnu53*Wh$bdB+M>O36IlS=3FekDFKf1kp>G%{G%k)i6_^>iJH;Ja-rX!-Np*NHTr8;w)n-ofYSuhe&rzc7B-(RIWwI#sWGyr$0U?O8W-erWPLU#oA=XWhhiAFeg$xHjvcbzq`d2krFRH|TS$>#}|2-^O>F=ih3|KVp4PTx7p_-BW#QJmUvH`tLnD-lu9iSkK=!^FZ{O`t}2ze?s`ykk9nFAy4>L7qhQ$CaQ0B<i7BuY2Vys@;qkUEN7Y5k(br?^F)2$`Ao}`$G$XNuR9gL0`n)nd%5r@3G+wSr8n*6{Gh(;*K@u4?yGe^NtoZdIoPbbcC7}1^3E~!ofS=tZ~ex3$cAFNZ)l;POWZ1)hqP#{=VPy{Z#CyU1mEe~()dm~&O;XW)cyPb_1$kd4_TysXj+><{^+;1?&oK=3FP<v@Ts<%|3}^ThL5b({duK!f%=CJHP`ueh5F8Q&U*(HGW*f!O8k4A592#;chGiwiSxtQu4aE6UZlS3>b~9gt>PU6{Sp~f$kZn^qf_9zcA2Gm9x}62;JUsaZQnU?UrwEu&3-=eY-FGxqfbxkeq+Z|bMEW#xi7jW-3g<+tM4^FpIhxNrS$XQcj~(z=;zjmli&E!qK)<@%wxB-jPLFb8{hg_KaWR7CpUiN&+f*zv+3vY(BW44`S%6>KK(rI`=OzI^}4i={Y^yA8Aht_y!Gf>Lf>vWR?DZ+bA!mZH}rEozRkHo7~lTa%s?LNMoQBz_7nB(20Fj_z7v@hsE^fcg?>&?I!E(d^yl-V=JRzlllt~9_RrQa<J)B~X!~$}VqFe>Vaoq-Ps@+jbDPkW^LlQx?=QVB=S7j<muowWOZ2JvJLgOGD+|@18*6;`pq@vCTP@Iid%FJWKhyK2$i6AY4;}y5_%`P}(bRYJ+$qf_E&qp}=h$0L>$t7B)%Z>t&U11dH{;FCaxjoT+(^F<3U@xD_2m4@nLkUPml{X4e0x3ru{I1c=Ra1q<656bdah;7zN+U1D^KcmC+PW=mFS*1rwcE;qUCSs`BilGBy)Zh9-UP`pV2RN+b_&MAv#@shkkMJ-3OHS`*+ny_VX(OzWp?pnI|KksBeYz+&EOUsPQcqzZ3cK-Ja_M<(-yu=b85nS|2EHwNl?&yTSPWIeE0|uevXdJEZktzOp*Ls`G8Z!+Kv;IX`((Rp;9x>buN`zVFmLruoxzep08c&bM{ccg}Hsf*<O9B9PzRP+8~Ot|tQdeLtM;>p(s2r497_B=M<0dpa#bIuBn`-~NetZ1D$ruJZ9|^>1*#Q8T3T@LK%)oNwSe%g<_irqFrV$<tov;T7sThjkwI{m{a5f&5P5g*xB9eJ+sS_oLm;2kPl&&ZzTk;$MUP-u)Xh-#Vwt?+^5E)*fa)anGplEadxZ{7|Zn#&=U{zemb!Fzp$w*G2tQ`h801S`+<VHE&nV-%Y<ybe<j1?-O4dqWc=YPYnN7#hkZ9Zco<oe4iL@Q_1WL!)f2u`uwW><-C={j4Lbm63xT+jLw=HZ=3dX)px5g-s)G<^NS<uJ8v@H@IzOZtN*)xpXGLIt>fyZ`tA<K8-C>XRe}6gkBa*J)RR?#{D1o!B7yo_b?ck)X5YfUrQdJb7uxH&VswqR1K)4jpQkb3Z$=M%q(0w+TS@b1J$tWJ-~WE|)NAJZ&2W~@n!kvCziI6|Y|fQJW436!E#mu>^{ceM8gEs97vm~*9v#oVKa6qc``x#3UHu-@x^+s=*J^Ip@`?Grdxnl@2j5A>_b>R-vO5FUbz^iqTjh2JuIu~mi=Bb`yT{V%_mYJ_(faT`qxD^HbB-LHdqn#ys^1S<>AL9mgSSt7X8fP^_Y#)-NawMqXN>RU)Za@)a!fMgHag;;#<v)^cAe^G+}c_08{g(Rva4Lt-%(^!-{m>_+i&w&{n7kh;%PNA&ZBda>+|7{=gt?*c(z+-G``I^abIh#<D_{O^%*B_t`ugRxW%%n@Bdz+TTU}htn=CQcOMURoVZ0xm~mpyentJ(`g@7UqaV$<wWsFNJdB@E-$Qy{c{{i99oj$KZiUX1IYU~W-%CUvex~2w?N#6L$JM@EdVcEr{<y*qZPwqXIR5x4-&W^I-}lE4el&ePt^Xc=FL8X4`m6H?uIp}{r{n6w{DJHGeq>;Qz<s%KsdfJ_y@K`&-!D5UFPrgWjhU+D{eEwmLqG40!>>rc<3~5m50rQ2Z#V0yy>)(|ytP36aP9Mf@^0F%%)D(?x)dnyCfTj$D#_-V&&@9DcqC;Nt<Q}G>Qg?HS^e;i_X6deB$v!}ow+Ll<(;Qr&#M_5`1RO<v+q2Q&2L!}DXh#^?`{cxIwq$4^Y#D#)3JW#{zpF@t5~7j|MjP1r{!L}xQy<HFT*#`-S7?gCv-df6MP%p3Ezf)K=;Bwz}L`&@HO}%A$-z{=Ux=?qD74IQeJ2BUcW01iM|ET@MM~lCxn~9EiL`~40smW3Z4beL0^aGz_Za<cs4u}Z4S?br=v~b>F`vv8QhF|3NQ3xz8CEY;kM{JxGmfUT>!U%+o5m6?cfgRBDe$G30(|#f;&@(j?`-*{0`a~?o4^%#M%v3W3*ucmcLnOA~=~BO}t2nz5yraZ>i9fu>4C(KG7twXd}20*Y)esB*8TklRG(_3~d4z_M)p7Y2k^yPJ-76?F!HEE;1}e>mr(tdbNPX6P7V+{^oH_FA}5G;lywvd?{B8O%B(B>!2y&I&f|DCAc<hqsd?!u7M_jYrxgeL~tVNCY;8LhF+vX>%*zw6lgs-1)Lgf0H=o2qK)9Ra0avqoB_^=Hia|7>8X#@uQ8e)PEQ$O8AEeowEsnC!4~5qDViJ>okjm9g{9Bup$pJia78cXdQlmj4=;e{p>yG8UR3d7HaZiY4bMSm!7`|2u8TpZz;fM63G&XRUNhk7XeD?7Ip?D@;hEH9K3W-W?!{0q$`M1!HI#h9vZl!Taf%SWgx-KJ!Pn8B;Op>@=xz8%_!jyDd<*^_y#{{|U$wM8QV$nB1iSElbRWDQ-i_{pcf;G!ZSZz@C%OaP3GYSsz<c3?=mA*t8~7l6k`TU#UVtxfe;3hfu*_FWES<9^!XFUA8__lJM)(AJ6qf$YN1r!`|6{2>wUkAFf&T+PL{Gpc$SEw(j?8~a2;sD75jZVe7+ne%hL@lp!AsyZ=rMQ=e3Upw9YlYFAHx4ZpC`B%VYzS7775y+1>=1NV}2Mq6dp>MVZ8S@>bn&F2t5Xm^J1(QT`XNsL>m#pvWCg}E9-qLLilyG4g5MB%X?&R(HLzGH|Ot-(Kc{nxCz=07VQ8xf!{zo!J?gE(T?yNaBH+Z+@5=AjkbhETfnX1252+58TZowZ3s7j!)O<{3vC-FgvS%YBhZns=x|tc7%UnGr)3?Iy{D|3vZnfLoNy{MWla2<n3A<918Y?#LO30o9!^i$bZAOgG&wAq6ix^KWvM2HMH9iINnqK3${y1}r@^8#U<aOy&Vohfz_N#wJ@+C)criK`UJSoO2roqESn>Nw;rZxnSac>lAD+i`7g+K8ebFiC0(b#sr=T<8ncV*rLU=Ojz?0$k&}Hy@@M<&yuZFjvo8c|+*XUQU=pFcL_-FKA@Xzq?=rj0t_)qjN_)qu+Dt-Ne*TOOMe=;~3<28o8L=59GEt(pQfnz8yENi#CK7~p<`fI)LAwqZ`A-sza-iA(wC)2*$2;m**YIp~{2i*eife)Zx!w2AR2;mFp&+rBKD*8Ko75*Om(~93$2;V|qz%OVEe@`Op?^}egqtbT5^32wyjYXTm@?6L`_UAxh|Fe*2D)e1gRNj}0*TQqi)eN2k%U)9U{IdV9jn<Ee|BN792W<$;USIb770{Y+1-LF+3$Dfc>Y@!{(Z+CHxEb0M7HtBHHiDbMRnP`-1MZ;;AzT@?VbL0J4eqBhAzTry0E?D~W&b1l*|KOwxFThQLuhWaJS>_A7JUWI4d*0;a}dJW3E`K$SmpKU1}|0;!s`j)<LH;L=mYpTe4h~hgAjgVX`S=N#P8>Y^AW<bzY~?RPYK~)&<F4XuKf!ke1Z_(h;D#IS6T7<PvH;H30C}mRoLIh3U?)hyAZ<T&{gm%+G`vkJeCk%K?tuy*Td^+yLE){7liOV^geu_HoZp(|C<o@`&~GMK7pUmz9HJ%A5*y*AATNTKfmx7+>6}9NOT>%j=GLSrTj=<3lB$gz&RLm!V<#6(3fEeVc7%4!6VRDV41sQ&T`NOuxQwd-&Y7PL&w9SBj9Clgb?0L2!BNg-$A7gcX%x<Yv#Y;XJ{Tc56`Etgz#Tz1vnjA7p=g&)z=Hhi(cqNxEI_5U&>8I`@>V=x6n7?x8NygKX?i}3GD+<f+wIo;R*0Kv<KXSx(WZ&yO*dJ=g@EAQr_Q+dohg=o{ScQMaRR1y%^+0QT(F(Z9F^%9Ry3xv0e-$guA1o;qGuZbQIhT4x=OCFx(X#0e6MFpu^!Va9cDEZVR_Yhrq4jR$dhGqAK@Y7#@Va4iAC{qpjdp<Pk39#j9TACxo-0+2Aa2W;7R^8P19pgtNj0&?0aV>MC5`>*LqF$VCX}g!5SX_wsOMG%s8ku7ZZ(DsUzARk#vd4t)hK2bV@)hD*bx(425i>RF0$`YB^o^b@#;7eg#<R|(-)(NVC3a5i)(EFmmy*~`-sGS<){u!L|=v>;rNKIqB&C6DkGFV1^$7(D`i?!|Xre1_hHb9gb(i`-re_9CAbgV5Y?ZpsWo<vnkr*<jJsuxNMqkr#KpcuWZYN(gU4x5As?57B?XQlDC0WJgQF+2O2c2{<d91uYI|fit7U;LLC)v?!bj&WIL*Gr}3rf^Y^nJz4-x52v9|rG4t6so}bCel!i7hW82&uyoAHvnyJN=eRq0`|@`wHv}CG4}nLali*SCP;?AD6z+-kh5K?X;Q=wamh?vZ!lJ$4u4owT1&j88MSI4?&#S`S&^|Ho^RRGtv|mj8ye&KseG`6@It@ez#Kh14!et2I*9hU#Xm7YQT$1Nfp3ka;a4aF*5-kar<h?Buv_(s_3)~WpMccx!bB$JnaBDOcj-|Y?%<nSK4?^Q&;@1V?G3anu)@0c$Oh%`|qHn>I;c4iUnD{kXcq}>z9t)2~C%~iOQRp~$9Q7E5PKHOpBhm5jNO%M~1|GwGjiCKyJ}rs%hDH0p62hg?epY;63%`c;x8lc!uo*8rf1}YXu!Qg=G&3wAJO<4QO9=Nx3&5g<VF}^xXi-=~_)RN*4<sxhEc5h0co13~mJl9{mV)y$&(uW=CYYCmYomo=SsP`|E{j%%MXSTzcz-XnHY{2P?gjTo%fh|kK4^8g58RKaPCxaBYoV24(JHWLCAbz`5-kUpgiD~M;Sz9hv=m&5wkVF4g^R<*&^mB2xF}j1u1(tt%icrwB3aN^toZdyI4k<96~EpIXGcR;{Q4-I56uhbgL9*KV9{J~F6xmR%>s*NhI7L?&`fX+I2)P~mbFaQHh)bN&VXivvr%5SgEuzY#mLVfRolRw;5X3r@EdSvLb#(BRlQs_yr_WMa0R#wS`#h<S0se1!IHBK+9oExyl@4yT}*ubc3fYy16-ARtATccC4_DC4Ol|BCfXU65Uxgjq<$UIYH&5m2%q(Mtruqq;g1R7<>>qHa=0E^9~Mmk*Mnd3BDP6PqRff^yZ@C{{6AT5tib=+>i>Ob@Mla3-&w=U_4kjOVw)tD-%D7Dy#HjwazegIvi=J?y(%*'

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
