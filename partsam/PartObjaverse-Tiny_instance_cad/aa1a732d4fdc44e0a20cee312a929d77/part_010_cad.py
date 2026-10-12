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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_010.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_010.stl', 'source_sha256': '04553ca9e80f0d2feed83820b066a9bf9c79d7fabd2b9c7eb3de223600ba845a', 'input_faces': 1304, 'input_vertices': 751, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18999764323234558, -0.18636180460453033, 0.23970353603363037], [-0.09926886856555939, 0.022927481681108475, 0.46996888518333435]]}
GEOMETRY_BASE85 = 'c$}r2cbF8#8n34ZP((pgRLp|`6Gkv`#2r-3D5!{_=pusRQ6w3_z>p*(Nf8hkP?4NLSU`s$NfeePBe*DG$)d80=NN8(U2pa2{-*!9&%Mjj&+o0@S6x$GU0ofEdJmQ=T`6Y%s>BNFZ#`UePb?<ODX~hi*PFL(-?CZrcGtFQ-NA`f^nCfVI{4uRb?Y^9Vz0;Ey8QX(?V7c{yk_F^+gsdvd9}plEnaQgzHQT1&%WCB`R3x^)AZ$b&0W9Ui%nZMchgtga?=gf64kG)mUt)e|M*wVtwLr~{S{wJU9MZdOf>yK&-FP0KXdL_&(Dngq#(*KJiG0Npr2ZMf#;`=EL<1mC)Yf>G30kne&hY_-oyD(eqvLVO`+et;E$zI^-Nu~-t!X`zAK3G)6?z>)ib%Yh36-aRW69~Q!7it+cokm&o6xPw){xH`KC}k3-6k}#M3|8u8Z`SjtsR!?A2w9z52J_nIGk+AHFVBek?W7^9x&iwl>ml`10mZJ)in?kylQcm-3_h*u1f!@{_I0dw%ZMH?58I|JfQUzwr5n8LzxLr{zca$qxU7%P;lOS6==aKd*`OFTH3>XuDeMSm>2EbnDtkzv|85`h53Go>yLC_L?X^Q+dVOC_gs#zQ}UY*WMhePvN#wbEE3x`>H;fJ0AElYI}WOZEy0;>a(NT)B3tSQ%#r8jM`tmul850&xjdO{UNq{_>8Fj5WBO_w8;KuebwJ$&o`JB*`M)se@?YOGRdpw+VJsWeSN$nD!eo?>Ui{hbv(w}T{$7@c(=Yj-V4jLA7{!7k0;jG<4K}?;TN8-#--T1i^qDt8sDs+HNMrZ`>9tSHGW!OkDsw~s*U#IYJ9f79-m_?+NDGFY&>_l=WoAyzW2L5yGQ!ToBM?Q<rf>jbSlzM<qZh=x&2P}{K8{zMf)p;g#EYw^p3mSX&s{d3PVGF>YLq>`F&sIPtRJD7geA1C(Fz@5E~rwGxz72{2zCT_N(*{`GsH2&I`74Y~VDLzvjJWoNpiY6Mg^X`Kh9ZBK_pXB_Tgm^&HR7e0xTuAN%dka5>%Y$wd8bdeGgTA3M2Iq@S5NFkF7q9FzapYmt6t<?xW7e09kJul+0Cx-Qb6uz6$XcmLdB`p?d)>!SSR_I;uJ$yGH?|0%w-AktrcU_;1ndzLBZnTrde{8aAYQ2to^qvkwPuFAS7Khx+)D8GLmX<nru%1_NY65if5-{wWt$NIWH={LT}i`rh_*V|jCR9;kjT3@$kdfkQdqV|{XtNm5@ZnN1@{lWUWKcvrZG&{1t;p_gEzNNwJ$m8husnetSzx8$hPha`(=~2g*^|Owz)sIaN{%+!$mgYE`wRL%vU%2QC6EEGpAj(hY_1O^glebhf@zs6SMfyj(Z4COEf#-VH&#?+)^P~LCw3jvo{dCQ>=K8kx4{M|RRE-*&L%&<SmUms6dFGb2QGP6UODKQt>^A1Qv2uqsQGVve$F~IiSpUDh>$=>2JHL<eW5-8@^83fph$-Jk`N=l(!sXBUc}`^c_`3YqroU%I)!+KM{)KbaOo?hA>u0sku&(2x+TZ%R{WG^W{xov`;_Lkzd-%jrQT@mFRsTsHe_(i2|FpjDpQ#ozKMMBq+z)FTfBwRyk^Y=vo}asWT|uP3rPhX^A3JoN=V$6&S`g*OS{)4MKlSR!-_6`t&h+PMI}4)x<e=-q<$OHO>(9B*B@3eb<kM@z`Hyxr{l7`qby0q%X}^sjzjis#Pn|VsU6h|3_k1XSX3)px{QgXFew3feJ$F;cuW*yepSWsWl%M)!PpJIl2VK15F)_7Eew3d+wSTDm#Kkw5{5`(TkMh&E)DPEZa?)H^Os|$7<)_Q<3gyr3UDo)GTIWakiRS50{=%}$z5Bb|)g@~q{a-6@4sF-Lex9G~nv);pr~Z{6DnB;2g6G@oBES9(N_&3BX%*?m7LEz|u?@Su>zQ=V$0Pm3%?m<);kKEcpSrqMq@NsI5cZ#LZLXIFToLVGTNLuszg%GIGwtk1KT+Y2a6RA7c-KF<H=Z2r_bn4TE^>!9_WZ=4QtPAqRJHQq<B02}#5bo#`sq)0Zi?~?f4?fUf9?2RxN`T}C_j<7E<ego{}Btf!-O7rQT4ZeR{fV%$%||s>#O!j)?Yd=s{O5>)&9HN%!}H;zOVLgqQ$lIqWX{Zb^nRI^5@*h{)w;qXY%0oxl#S!`dR(IcY!HikIxMrpBr^NT0iS}yzRWXQOCRQ>*M{Jd~<!M#uMx7@g%t?*Z69@vc4X#GJkdQo}cLP(E55jOr5>myMEB)t@ZVIo4WK(bN#8tbL;EzJaztf@A-*7UszwCFA6)2nCkiJd}MunK1yb0P4?Pbo$su#&v%(KF7|wVKDE9+pC+1)m}ri#@cG*MS?BBfDo>2;S8GapzP^62zP^4a9N%QTS5I|);`{3Qr0|39#sz;jwXBZ0{#Mry+PB;5`|5f?`?me9ug~w=xBbET`h2Z@+dr+Z&%b_s)cH&Mc6_kDK7VQ7jz7My&R<zR<D2#M`AhqD{PgRo&R<zR<FoIp@jS~{`Sp0N{jB<^@jS~{+pEWO?d$f`<GJ?r{?g;5_U$<7_ct}}X<zp%J&tK#_gg(KX+P_@P~(jD?QxghQ{KD>QupcB*Z1k#xA#HT*Z1jJKKEJH*Z1k#xA$?@*Z1k#xA%$G*W-`&bvx+$dhOf$R=*rIUTNR%7k|6dc%^;2->t8o8))C&cl-NMjc?kw{m?H*jc?kw{oLO!^;|;x_PK%Yt8r5M_PF!=l^Q3tZ;xx=SL0-s&$!|D6E#k1-;PUuJ=Hjw<umU2zpI|ZXx~1E@yk);YL>6c*W;@8v+A$L)hu7Nj~-XGuiIabtJ>H5S3h^szV1JI9M-<>pL!hDzV83}xt8|z@ukOY?d#)LkK5YU<AZ)~rhPsB=y6{AdVJH**|e|6PyL)t`+9uV&)KqkHU8`8Y}(i77yX<qcKA{A{$}{**SzgG)^K~!PgJkeJtySXGvn;{k328wL~&=&Pae9|<iGmyu3oyhhvyd_tQg9lEFSFnxd-=~arv+7TY0}*{87kHUN)<9PQcI1++gyn^O5%L{_=fwe$l?|Ki1dh7wy~rX?=aZ(7ruhtgp`(+PBA}Ur#muYu}C!*4N{|_U-uN`)d5p@)_T(ug8Dw+ws${ryBpWe8y+rSL1n>uk!2hT>Dw|QR8`*ueMi@=i1lpsmF8e>;0w2XYK3$pvPzJ>;9(4TkY%qtjAmJXB{tU{M5dGJRVqPepihfnFC8r`*iKw)BBxcEkk~)M&p4w0YCS^SX2IM4|Vr`xA?=b|5W?;b3*=SrktOzf6=Q?arcm4cwvoHPQXv^?`X<tS*?qw#bZN$s$ToPIRQVj?@r?{-2AR7e_+VZ+&!dMPRPGK)DG!GPj2(tW8b+U-_}32ucGM>y`OCB#ScBRE$G|v*7}7-Cz$r^xcDJ2fAO&GLBH^VqBn8^e!A#a^BvV=8wZ&BcMbdZ?EfGq;O7?YH}Bm)c)6cxpDCuEw`?`})%zOXSMO`Ge4d9`U%#)>zJ1=}`|5p-_4WH2?c3)+emUy=qJ7(+eP6w=(Y}3t<@@S<q<wpQ`Sn!qYqW2lzxlp8e`((y@7CAvYqW2lA6j3Z@3e2nAOCmN`x@=r=bzTs=SS_^@zDDEeNC3n^ILzr)cYFk+vmgneo^mh{Q9f+HQKk&tNn7+d0hMUyx`YgoyWCr&pW=a&f{4==QZo=^SJiydDE|_I*(`hoR|ImrQX+Q-@fng%Te!Zv~S<nXy3lC@wZpKuhG7JU!#5dzQ%6{^}a^?S@l=fEm^*5AAQ}T{jBy^*DYDT+Q0g`Mf<w{=<62k>;9?V*JwYh|Eu>k|2tm7?`yQ5bv&x~HCets-qrP$_Vsw8-`8kgk5~G7O#6B~)bDGwug6<`{ic0Ap6mBD+Slg`eZ8lBeLm9fYqYP=cl!EJ`}%yU-`8kA>wK-=*ZAeD_chwr*AM!AO_r~&PxSkmMA3TF4)49(%PYSmZ+p;B+`P)Wj<tTQXtmidT<^t--!a!|dsmq4;=VXtoDTa{*L(NH*3ax+VEl1qFY$h-xKqeao>tU8C*UXQ&M@`S-<9EKeOIP@|GORhtnbRSZ@&w|&-$)R`TloD_*vhTDc}FD$^NeXu1xv<cT@OT-<2uf|1JwZ>$@`L``>-pcGKULDc}FD%$B3SD^tEMKkK_P<?H%qeOIRZtoG60l__7hf7W+p%Gdih>$@`TtNxSqU77NA|J2XBQhTSF^52-`-9KiEKiwYm6HV58_m9?(?Hy$5&;4fMp;p^MKKGl}FWl4Dl%IcnGq2r>yKN8psTxJ^<OKZGo>s;mS@{ifyiW@GnHsaY=LG!ZzL$)zzU#KW{;pg5_PbN->+ia?Z@+8x%TeETTVH?It$q8QtzW+Su3P)|J6`MS@4B;mz7zI;SAEy5efu4<Uyk~&JIm)gXWv)fb!*>#M{RxmUAOk_ciq<4-*s!>e%I}9m-?<-`?@~*yY4JsZ?F2UTl=~_^>^J_zS>{<yKe34{-D3>*1qm<`nzubI8xtrYhU+&{av^AvyLzIU3a=|Gqc~-{1@%p`7ge&=D%p)&VRAKp8t~NGylc+)%=$%pZP4-*YjVpe3f6%fAM`a|Hb-x{!5n6{1@x%`7edL%{Z0%`}$W!6UF_u2mSPAzkAnF){pJ3Xv!aOu#Z>&l7g^bv)tgEkbjEt>s9rhn<YwCh5XdrHNEF%)-T*u+U&2?!5*HL%nSLc@gH@F@{=_y^~j0vW7W$I4Enh%kACfKSECk#ym}Rn3Hiyo9f#%w{KU$A#_zScjkmqLXR&_zs!HB-Mc-dB+4Jplzr^A0+k$@Tj#Xa!SU*;0u;=S}zSh_Ce6?@qky&5Q^VPncr{?==p0D=pJUIV%)jVH6znbT(eLFAD`g)$P_U*hszZ^BsH_K;Uq4o7V-z=Ybi+=m7dA{1W^CEp;&GXIjnRn^eQ_b_$zMa?Uw}YDJo8>ca)ZZ>O&sY0)UaDV?n&+G4Gw;>kE;Y|L%V%D#|GR3QulDUcU+vp@zS_6*e0^Wd^Ud;Aee^uvEMIM}p69E5-JW`$Z<eq2m!9YA`)Z!A@2h#fS-$FTdY-TLb${0Le6_ES7d_86%U8#vp69E5eZ1>=zS`I0iJs@{m#^meYCmgyQ}cYaug6b4&sY0;eAe@P)5~g`cINzR&pXz)=U?k5m)*p;XYPYyCCfs-y$`Z}?$X)jew+KObn(QHZ|}3LpIkcK<mbLGS+XYN+xtH2$Ci%teEU2nU2-7g+vhpfPcP|g%D3M$l&lN;Jh!oaY)KQ(x98JT$?lME&!^TeT-?Bv!*iZY@$`^ypYvEhckxZ89G))~7SA;GSyaZ9W8V*!Yzg`P`$7EFBFB_t-w&273j6l`AbxVuQS)Ae>!S4G(c6N)y)LqTY|-|G!Fr}kelYd<n)flhSIsTi8S?FWRqJQIs%w1S+ZL9@b_9L<-q!kwh337By{}Ik|7&~5=f2+hnFTA&`xxFMXG#u*eES~R`sw-I7lhis<fz#%^V=*4_LJoC3Oj<n{qDv3g?Wuke%_DU_OZTwKW_cpyqgvT`&I17!fip{_ABcr@-7S2Gxzuz-tQ*o?KAfqymw9>FK_De<-qyj{HJ?<YEEs>x8D)jc1X=ym=|p4<dOB;LO$(m{q(d&^Mb#dIkGF{+xOkpPfl$)FVxOQ_HE0l7y4gv{(I}}?de)>5$<wQtWvB+)4+d`Bc}XWjs7okTGsf#`Y&>BsD6Eo|G)nur`&3{4&S>=ImhTJj^VFlo89FE$7or{@I0xzyEu-~<FKr|mi0v|IED|qyun>AaEzYe7~UT<vGd3y-g&IMj`c+=I))dyEbV@hWAsGF@Sd0{>m16IGR|S$^{g*?x?@<@UC8>PWgNpRT%PGJP0^>|IqovoT^gVbVX4nFcX<YF3?Jfm+oG?)M~JmY+rlf|WtF=$Lz~0jxy!fi@*>&-K1x}yqwQf?cQxyaz5vU*OIcs^IrtaKdJTOYmVGMw_%ZZJ_!DCF(Z^sZa|z{&=E8^hjdtj3u=J(H?$QK(7XFyucm%BvFQKh-(P!Wd{6;IZ9lV$}eHLv7kK{M%p^w0$h&_tdgJs`sWdDi23eRPohUlYkGupc;+A_c|kQV(n{0e2ZMcW6s4e2)Q7t5_lx28QUw<6t&b`X}nBK!Ge^rZklM_Tmx0OyhxeLBF;kQQwWOTTy`X8OTnaDDV~xIX*{+5m1qJ6mo@x*_c;+=Tts2z@HR%}6(+jfJJJ&UcsE=w0w8ciHSNb<v06f|%(;52AHpIo@ZxOA@UO=f%vvzY|Tua-6Plm;2ENVL2Y9|J{e)1Ft6b0D2!R<Lv@>xf{I`mg7r~;d{~hVd>`?%FU2hSjIgWLmxsPfMwj1<EIXKFT9Z0U1%Lx`uuv@YdvKM%UCxnX8M8X)9`HC?s2pMEbW}{E~hz0Pjw7Sou|gkc}4Uec(<!N-KDZ)^eo5l2FjB2M*-yt&!n8E&_)5ykQQwMOP#-=-lEULU$PBPppU~+&P3`b`WGy9+fMyND>?t;)uct`Tq-Q<e!=>p|Akjm&I{<jVd=NB&8^W^u+(`g^%i{zp2s#ki9P{K|J>m&Cp$*ZbPUgDol>0B<s2?7b^Db1iT(l0x<9eL=-G~8sq+@<E!q;^%r>+^Tf<u^>m~H%0DnhX^hH?ur_{9!b(T5`OWj6MKhcr^&m}Dya|}zJ_fT(9xkeC{I<KJKqD|qAY{RQ)8+a!9rlZT@sl+Cu)8UE4#-o$rFNl4Pj)!F#P5cYkZmZ~UbTmAY*hlDaSeBv0N5UVY!{Co$du|sUfewQ|BQ^#d0god#799gmA~pdX3r{091)TuTA~pk^0)Inn89D>rO6&)88N7p7A^HRS6R}-rA-soJ5xNWBPwXIC1Ro~$8+s7_h1fClH~1*AV)Ph%gxK$BF?@*FujudaK4J&ZU*X-v_M!*ioy2}d_rlwW{fPbyZy~k~{SjV4Y&p6OUJhS`UL4>bNsCqu@Xw@0uL|&9(xTS}_yB3q>jV5NY0(-1{++bw%>gbZEqZH!kC7I=CBVOt7QHFJ2T6<G5a1%xqSpm@7irO}16)X2^zs1zKw9*Y052mgnh5X=(xMjxcnWFJa{@epwCI@u9!pyEv;dDGEqZEzN01ghIl#k6i=GtVp`=Am4Dd&!Mau?wIBC&x0Uk|Sv_gPCCoNhrz~f1aRtoTB(xR0EJe{=Y`2k)|TJ$1VRQmOW=%oR!N?P=a0AEE~v|50#B`tbmfUhSldRu^NkQV({fNv%(S}VY}k`~Pg@GYc8?+EZsq(yHJ@C~FzYX<l_(xTM^d^Ks&YXW>ZY0)bKd<kjM%L1GrEm|eO7myY`FTm%J7Ck$_XOb2@BfzJT7A+s(Q%Q@S5a5$Zi<S=XNu)*N0X~tmXe_{GNsBrGE=O9lRDdgx7A+ItiljwP32-ISqNfMAGHKDX0(?Gc(Q^ZQ5oys2Vd>L7NsGP*OP}sdyf-mn>C=6Q_a!DQeY!vK{=|f(PY)nIfS9oK=|RK?5fhd^J%soWV#3m=KP3JkF=6S`9}xe5n6UKe!Ndm>6P7+bkoZ7i!qTVTC;mP$Vd>NTi1#BVEPc8U@jk?arBC-F-iw&9^ywbNdk_<rKHZ&ocVfcQr@IpGN=#V#bZ6q7i3v-e?nJy3F=6S`?+|~7n6UKew}`(*Oj!DK2jU%w3CrIb#NQw$EPeV-;%^d@Kk3sQiFYI>EPeWI;%^fZmOlM1@pp*{OP@{=PZ1NAKHY_Q7h=NFr@ImFMod`x^n1kLBPJ~OY;r$zgJbj>$FOJ{ShO81`WpNf>&gA&KX7$oufb)B=b+-{5PJ<4?F365{-7SBS5p_!SK(Kwlg(2?KGDm`EBXrj3hUTBG2)`Pz@l%!Z?KNd6DKZu8!XxZ?!Y=WPif+!|AIx|g5P2to96`LqP1Yrci?we$L1+Zyew^23+)7VVjbbu?$XL#s=3R5Vn*c|_i^|NVy)ovj=7({2fZ5>?E;H-3*<SIxM)3Cv@hJ3b!?uqiHkl8i}r{6vyRPk4sp>ZV9^2a0M@a2&Lb}RBrG}z9>h8}&jrLqpN2(;z(ZKa<~f77=tHn*Z@4$>*gU5Z7kvO0?Fsi}9h>J=;-dG#qVK`)v5w7Co_Klo$$e-yxEt#T%R2*kcW^)YAS~Jo7VQzpb3Sp=r(n^+@L<-ldCny++7K2U2oGc(o2N2y(FU;S`|$g$WAmIvT(mwc+7Ir>IyO%w;-ZhhqJ7{#tYh<(BQAOuEZQ0F%sMvDDa1wVz@lB@uB>D8R3I*TFD%*}?#?<kPetMt*(dj+J>VX!BYcy))OME(;zlou8@`U%d2yrS318`$*g518Pxvy&#Lgy<c*2)BCUz!y#1oeDmBc!7P7|)eB76qxN?zfMh@BQUDxUC#j)_$yk9fjzUX@q}&b`737U9!bSMmy9OsrDesCdGcIwp1&dBhX0>X=w%@`xvVm1AP(l1Dt@>m3t2pFH9T-|U#!h2#-W_)f>f666t2_+iJyE+&t7!g75iF}Z%~13%6pd@1WnUSY{2F}V)w2RCLBt{OKgd4-=Lc17H%c*41kiCsk=@r0jqOspDt#1nqrF|ljOBc5<`$HcB9k9fjzeJU}zejNfgV-dcFbtSK`<dK+M2M>aqvIt)tH!69BpCxu>+^BfMO&k-uoIK(QH*!quGV+Kg{Fq~6mykz1;ku5ARUwafRXEn_a=g_gE-dHVKRMTmUh5ccjkZOvg(c75<P*Iy5EE^W-UzpcUq@@eufr)c38&z9(K}#yXIzG~=<R`+=-cS+u;eL4TC`>$CfX6L2}>S_wCJsYnCP46t+3>gYm{5jD*`dmR_GP5jQ1suIZufG7nbcUpglwv2ij*b?I-#bEa%FdjyYe7{tOSK%)#hCuw2KjcFgsk=qk89Wwu50V7U(Zk>B}|-{?kJQf4o74=mSx-}5`)^BWx~OUi7G&Vl8+Z!PPsWu3Q(&7rMCXTWlvDRj*FNpuG+*O2QdZyja5!#XqA52D|~a{l>=@_wQ$VY#l^>zL~yQMqXvLRxqb`ln-9&SkqOZx>|=OFztKf9A6<Q>-KF4nU8?y=cQ8=q_0L=NigeLs`OiyLI@+)d$e6a58T8=^f|__^!C=H}|3i@Dp+KdrzVNz_JK8L7lkahu!4|H~kR04SvL3w!2&({SlURWZh@cQgFSv*>?}4Kfn*V%SOkPC%PSemUW*&<8bY`*{8RoGhkVSYogQO``u-OV}3_;Bm4|yK8?oU``l%{o97;M9V}%@nYW@-U};ln+xyWC@Y9sp5S6|qENv%kcpthRma?SG+t8`7EW-anr^8RWOOa#tXAyl!SYnbViLQd1u+CHH6R@;%W8#g8HKBbP5pP87S+=Vo@rJ~NAEQq+K<mSI(MEOfA7h`3)`cI0??>yvby)X)+CPW=oI^jjop!55ycV&VwA&rT?;v(7?UN*)Bqn?}`~FV!9{BON>AR1j55teb51<dh55RY$_rcBF<vVv@G)2FKTe-`AmtR5m!LQI~{*CU2Wu4_N=b|fMS!7>7hpvWY9T~%0qCdhd=zlMwKftmGzl839r7Rh%pGViiQkEREFQ6M?iOI3k0$mSFSu$q6jP8PE9XWoQqxrBb!p+b%u&g6}z7<*oOP^Whn0_a^7?%AkZB+|h4$HYy&Y?Zg-LO3KS>%}W%p%4CVYv_c%`xY5(Gs{P>-I+X!qSIi{kzd`;CpD7JJCh3^#4tc*$&ZVa4q(C4!RPS=Uoe_??TEEmixaW)b|K=74FPF?SmeH<$2XS$CNjZvV^7oOP+e@4!9xxvJtuumgD-MW41$d6D)O=I@d<Oh2=TQFOIqH_=Wx{{3dxiqTj*toNPArolRYZ<@w6*jw$bV$`Y32^Z?s&fbA8Qx=NiJqx)eQvt-@J(1WmyXHvHY=r3?b>h?Ce2A1b@)2Z)t>MAVPUaN?&A|@=?1jpHq<7|Vlj3-;!4$%W}W5$ao(IR+@WAZIQzk!#)U!#lQui^RVLU=y>B{~oO5}t|9hG)W)(CP3bcmg^Vo&b+Wr@-UkiRd(VB0L$L0Z)c!p>yC_@LV(xo(nHPzk(OQ8FVq6ftRAo;HB_pbQ8Q8K8zlO55vErzrer3#pv&FG5jC&IQ$>@Z}d<2Z@5g{s9bZDVG%wNjl(CxWzkY_S@;Chflq)-qjHT{nzZm=j?w?Zf5CsCCGa2cG4wb17<?2x0w0ABp$FhY@D_9{JUVV-pP*ad&*P@7(dZ#~eBAu@=jc&*a@^E)JbDbC8aLZE8T|vENn1=sB_=$ZwwsBThQFk(XQL;;bJ#auqGjP(?8`amiSV?z+4r;1GUS~SH+^Lq`ZqiwZu-^~^gr;}xao@%&|-K@-1ObC=&$goxasR-(8KV@adT{pLN~)7#m%wwF}f5U5;w=*M`#8f5I4u_5Oe|DKW>ig0q9(~cifBx{n1%)&$t;odZUx!_u^)(>4{E+d&JGy^d34M?iDv<Sr2pq+%Im%zFz1g`2DyUEBm1{;lXh;w!V*k2@j2%v3M{#A081mWA{+>YgqcU^z9Mo5_lqg`U~`PcshN0B03(POP`&NPKNX7r*qM%@B;d29y$~LihjBPoeeLfpMHgY3D2jWE=1?R^XSv_(OK{e`t&?>8a#<UJp-Kre@LGjjz5V$E;<e#3y(oRgU7(5&@?;>{umt&59hap2gOZ4{Sf^K?i)A#bPzfO?jAS&v@bdU?ix4!v^&}#?i@G$v@6;h?i4ruv@_ZhPQ^_>?S#GucZr*RnnHWP-QuR7c0qf=ed4B{c0>EY1LLNj_Ceo=rO!#<`xG4we+rL8KY>TW!zf3}9g2Pc4~0jd!{A}8D=g16t59AQe$VnHq%Wa<mM<eMIx)bPlNOyG;44Xs&JFO@q($=rd<|*Q1p&T}wCGm>zLvD;!T?tzEjmBISCJN-7vL*Mi_QpeRnnr90(>cH(QyI3n6&6;0Zxz>O$Ycw(xSryd_HN>4+DHIY0*Ieu1s3AZ-CDtE!sW6l}L+r4e;rtMLP$$B5Bc10X~hiXez*GkQVI{;4?{!b_?*?q(%D#_#D!r0|R^>Y0(b?d;w|EVFA8~wCG4!zAdjEGvB1kci=M5VgqUM<y(9Co?qro$ov4AJCKZ-Z@2UDWnP8Mzqm7I=0?c(;W7_G=0nK$^D@Ul=AX$N3YiCyiJ5s5GRI*FG0C%*wD^l+W)6kSnUMJzGH*iWILKTF`Q}{aK*;yz@*TL$dysFy<-Sku73G<S+@r~TraTuBZ#ll)Ys-DRJm--6dby{PXCdP4#Fu9w^2|b>VaUCkJg1Q77IH5u&w=HcggnoX`*3+~A<r=6Ii5U|koZsJ5w8GWo@dB&6M3c~&oJZ}ggldw`#-r4lxGxjPbT+f@?7GuyBu_vL+F0^5PSgL1s{NSqwC?_@CNi9cmw<{dL#TUTpb<b7_JU~$|9V0mo={cy}NveE`>#x1UN%_3H&wsHvBdG7TOvXeKo*0kru51*C1U1Jr%A1pX@H{XqTVR{cuOx;tR*<yKoD(@k3PFLU<_c@d7GsAw1SG?bw0#Tn~4E*P*-M0`^TubOZb|`?3Jt4Sz@-#-i`Que-X4_E|(bzQs1kwhTq9!#}a@`_O~%8|;t8@Y|$6kYmDKhC7B|B7MCZ`^43g(2wEQ+-14Dd;_;3y~$k)-DNwxh4c=0`O#f=qI=+F?y}ikR-jwqTd3a+=$r88?(dg(bp$%fG5ndkjHdph*#_a8-8`qn&32r^He62|zE1sLXB&jqy30!Hzmjbb&UcrMY{y2nVF&HFitSj%HY}r_QV;2uq9@ZwSMnQ6(C^?qv{Mnf7nc3-vb(&9wuB35+r8*E_y*dl9NHF^bw{$k=rDLW>uzEHeM@>2zb9=wigjKle;e|Nwu9TU-`b<A;giVI1|H{_^j7k$fPWw@d8Chxqpy7g*L%>3S1R?t$=wC@w;nEXPa3kE68qnuyjyekX!Ex1TQb{QuNj^e9$d4kdqVOjiPw9ujC@xai@X11(vc%ya>o7-K1@cY'

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
