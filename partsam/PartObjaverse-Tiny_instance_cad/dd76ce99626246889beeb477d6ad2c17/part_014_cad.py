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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_014.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_014.stl', 'source_sha256': 'd3b46b6d86e4d9b7e5deebd51d84bd31ab8974b7abfdef90ed58c0967be02f98', 'input_faces': 620, 'input_vertices': 402, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.004059857223182917, -0.1140596941113472, -0.27302148938179016], [0.06465071439743042, 0.04544523358345032, -0.12704354524612427]]}
GEOMETRY_BASE85 = 'c$}r22XqzHx5g)hD$<LTzy%}}Lrdrgxl$#e29VGvKtc-%gx+t6QbO0z+YP-VUHT=Vt8`F7<Vq8y{6U&h<jp?cH*v=G-db<Hhik9>?cX_b=FDkx=G-h>hx_^G*YK~TRxzzbnJR&rCYD3XuMLY%7}B?A^x#Ty14sI3xfPdxrvIvC`xdP``e?(n(Peu@5AK;zwvMCh$1%0a206;c#3u|%h>GhTpU^8>c$28u!O;dE+$U;av=Nu9RwX#d5mG+LG1l>a{FmLRf;&&@z(a=jlv=+}yq5jiS@F*6<>JM=;?67X^viNi`3ZLhh<AT_P;po0KU9AGL{xtje^hh7cyEdGHm(&3K>3Gn+VgM7g>njh4?h0WzTzF(8z`>N&Z+LJ=e*WOm3zL2D&JN34f2=DthlTGCyIMc-L-K~L|s*m_rRavN7G|$^@-gD{>y`C<=cd#oRb69eO)gLDDKI72IZXfRos2GWt56@3<7_;LY3q0cT-pKnGn>o!D}0LZXIB2PxrVSihFimRr#ISqHSDzxL4(OBo0UWSMJ|U)wBN!wA<ljXKj3Qebi^fYCPAPTAi%zrsv*n<675m_NsCovi;8_N2>hIuPN>+{Edw}^B+=Nn|}-Z;r0$HU)m&9zT?&j#a&G!+o^I2qn+KY*4Vhy|CTDpoAMWU=ft+EoJ+G+Iqn(PZQQZ)FrF)VG1_zF`UrLZl6&`C$Dzs1^7THsFn&T(nyK{370~`y(EfVoJ5AMnZ^xqkQ=j3vx`)@Y*57+-CHT9#_YO)v|BwT!obNlIvvSwej_9w-Bhin!zAP0g?KQ6e>N($i*2+C|E~B2mp<i78=^PTO(%mTMn}s&+cv%zmk55H8Me{Wft{3g1%Ga`NwsCj+ei$eDmfE;y)z-b%{?b1h5f*A04`%!8eu2$Z`ITZYFCrh?xK^<&`gfc^#^<ucR>EDyr(!&RapkO)yVrVg-yYBLTpgaa4YiCnt$TLNyN0LQspsvt9sLsc0QLWAQj~CKRG_`z$@Qf@(LTrDqWq23d#ZX?`Al(7%fTqWR4RCjAk~lF2kp_1F?*v`ecl~G``3Pf=l!`%jN+WvT9>Ofo>8BzM{L|2Z)W{7%4wAY?G|wv{ON<fs+?Z!@w^uw+PF8gD#l^BhI$@b*k3*GxJ_6m^W8xHnwewOeIpkjf1hvB{w=?cSLJganeFcwl`=@RbJNqP|H2OEtlWGrxa;;syRG?ri0WT+oo~}kaV@s2TeWAe^$DuJIetB+(r4EN_Y5De?msTzxGKN=H1OQvk?KAx*B!(CPk<NO{e|)kB2|9<WZzU3KlZj)*FPJf^1BNi1`m6Yto-_!D!=#HRq#3a7ARjgHeJ>8{0s1up((09LwptYZgnnK{ABt()qeLEEADo*1b?e9QT*)KG<E-(ox#r}eWl9zxwgvhdfNy5UD|xruG#ae{La{6;16Cdu;%w%NdkYedyZ<i?=GwSTKp>TPYbH|u*1KddR{$nBe=WxVpUG!W|iNQvIqSBHPwEun3;!F{r7$kUhABCE@whG%1^imeknjbmuFcSm0vG^6?|JQ@U|CG&v|#j+c#cnEytPp1$dWC3)Ovd|BiBQ=3b%r+~F$SdD82_cqtBE?CA_uekady8?RVymTI?RtJ7@!;HpI`|EqWDHlC@5dR}KCkGii`xi)xuw5=aAc<vz8Zr+{UP|qbzz>l6(<>>crqknU>1Alo;^{*$asVc{r-U+;5>r`tw?om<T!MbW6*Xq~md9~m^;0fO?vDN2Z9Qg2Qw(*d``&?G#yD#NOJ>5gW-@HFl<!3!T9maqcd9B8ed-@H<-D78gm)tj7)o0vzJNHjg<KNqT&tV%6)6fp}^QrpiD^`NH`&sp)cmGE9T%JxFz=O6gvW`RN$#1|%KE}AH_!r8rc?|qaNi{Fr-bj^SUwwh~51VhDr>?G7z*pr<wU+PA|0{T_-<H_M;dj4*|MprvmuE#$^jFd&@XNnqo{oQc*v6l>SL4=s?m6mN=Q;S4)rxC%o}pjX`L0xPa@M&jf7+LaZT#nJs{Wqmr#v?PE>N|DJFqnRt59z6JsXsFAFYl4?O6*v<>oL|k1F-C9u^4&PnxI3t-1bW@Os~4JXe^F=bh3V{KyD3kF*1?(`>wBofX#k;&iqJKlqs%hkEUbX*S-ah<%*D><AuOSv{|_cb0$g8>)P7k=|&ZEjsv!WnZfLznhz8<6TxPwU*<E=?(tJQ^mb!GGROf#DPbzvCRwb#UU%L{pjtmQnkPP)nxEybud0Z+=p@;OTgP~vW@2qzVNy7-mboApC((uD~`0Ss~NoAbj7`SQ_;UW4uW?&soLKicKf)EH~U-7M@NZE_WTu(VccrDu>Qmz1)sYW<NQp0bzj$&^Wd#ssd4C;vli_Z{|tQFq-Cl;y-#Dlq-0&Cc&Qw=b=b4F82F*Rin~7BfpW@M06%?tiprnb3**gO1$<k$y02sBox?UB-b$6Df6^e`##i-F<H519BgT2=#^8IJs(#Ub+K2iKi2&a)2=o1VAH07T#(<~gRrN973mJU+?<&9N?RAW|hyma+x$*uw9(qLaY(v1~Doj_t`zKg`Jfpzh4OQ*uSn>knr`=-kGu2dod20+iY~#sTA3R}y+Vis<=MQZ$&U35)H{XM${MB<g?i~Q{J|FXC$fz_MKfOwEy-_KQH}?_ndc{=#da_@|x^(PE@LIRjc=K>Q*T-H5zq?tDPfyo2c#l`R1D^Y_nvdG^h{HBMvn}3JYkgF^IafRd&wF>O;=aew{+(Wd&rck!@_k!ftyfxJpVf+c-l_MLcV7228@~{tyvt`2>gmb}zGkL+e|bht!FZ@y06cst=Hu=H7|)N2f`<%M_jfGYgns|72Kdx{YCPyIAEAGf>VbdRP1VQ4dFp)<2A*0K_vO0n)FZ)v3sd_CPjW9i5Bb6NesmY=4*qLPtZ(ywz&x553%;k5n%C}%gD_v}4F)eU8h%z7##NCSh&Qyt`taQwwQjgxt_3fZ9qYr|ZHH}~>#bhnZ>)!#w}6-1gZE3oT=eh7bnv@x@m`(~h<4ce3+u5H@8$FfSP$Q3UZZ&aL#mx!dR3Hjr6hQA2bEuca1{MDyBzrbD=V$@-O;Qvc&$kF-QYf3R6Un_Z-4ON6|l}%9*%h$v=)3;VXP+`*J3?cxD%ZFPi<%QBR2lodst`oC!t@4p9O!GK1RiSpJwp5dJ|Q9?rns5cjp@T+6HR;xCSTVzDsU_@5-X`J7-Txv+<4h)VkyvQ4;fF)I0E;dC@QCdg#u#R`KSIZR<}4f71l(cZ0on{~jv~o{~%DcU7Ng=iGm0>`P7lUNGiG#2h@=gSy~l>Z<niWc?8P=RB>!Cofm~a7Woi=--;X!1KRT>xnDL?}RF6^&s$3p{jgyee>oY4<6lEjU!L1UpODX0RPuIqbE%RA5ulNllT37xbKq%;K7$ve%H72?0mvl)t=_Q(WS2e|0znfo4&L<+P~0d@ISF{ciriY{n(iu;75C-{@nlQ_0qtLZB+R)_P5VYu$`Bv^}+R`0oH+@m%$e_LO<Ugj(Wa)3I4Bj!@K!!@cX0Hef7oTxX;P7PVvR1@Ld+Q4)2kRdBI=BthUZ0XW#<xKHgF4dVUYOuPp=j{-oAzz2H1GFLb{h;M^yBLn9RTw0Up6;@nr8^UGT)5WL(LwN9GrPX;&lftPyXyI@Jkdh2-hPWl}CnRa!+`Cit(I)U=5wg<1EtNi-bP=3Gk1>f;E_I0=GW4??X3x4}F#%=3WnAg=l=Y1nFA48|&{qi6ge6oMCbw28y=7TT3g!k_#J>AAnG*#ou)qg1F%gI%&=irHG&rj`q{9BAquB#dRuR>UF%UwZz{<8<1`v(ulx!(0S_`~dKylG9_@O$Jcc!?mCGrBd(S@$1s?o0JMyX-t?lp0s=kTWP>e*x~m_qBJzQjE_+Z^1X={i5d#!TaL0-v-6A`l)ifxf0TBob$z-eHz|V_40sUDW}GX#_{QXR%nBD{JXcW@!0t0`f5CTk3Yuyt4I)d?FpD)ZBAppoC^j&g70_7wH}yvQ)+{M-hZfSck}$`WfSmX%~3wTJ6r*s!CMx?JpJ)oelJ9U_r8ev-fuI?Zy3+=*Q@$CS2p5z#8B`|rBykOEtApjeUrfXUFm4hAMec{W`XCzIfMIQTg<y18~9v)i>>q25xWiif$ubxpWh3*pWjBs_kXPR8}6iN>>JA$0_Qo2-gzPS=K+el=9E+U9i7%=oM#S3{@6IR4rp(8VSVuQ2G7<I>pa(0Po<&YH8R`gV+JqR58n%ghx0u+0i5Rv`jZXZCr<(Q{S5n!$NMlJ)8~SFZuV2<^4!l;btSm&qxQF2_gP15oab8F?PJ{c9tBUmfqmESm$;9;0DfZ$_FX6XV1BLef-etQVVz$YJZ0WWYyY}C{RZBv1lE%a8}WY0^9X#zU)VqJ{7O6d4E)v{+xnKl2b{(E#-sykoanCC;M}jeig!)7@wg<c17CcP@m$k)li~;Po$e@7AN%vwxxjZlQ{zYPxh37k`Ms<?PqlOIm(2Cb`=loL$a-qt>6PwbUaYGR{w7|vgFCW6+D&f^9(Et+06E5ZY<%~hihEPWV_$bB0-WoWGfxlhlRJVZ_rt!I?`7|^81PeNuugLS;N36){KZ}D_j(LOeR>W7FS`=oeOp>#+@4DWuZn$zwk9pj#?M{EdC%1CcFuj2>)?IVbIRmR*8cTANx*x`ITPHmSpAM<o_p&7>%lL5sh-REXbj4kwi~=;6TFvsZsXnhE%=`yiOQSj*e3sj=ffM%VL#LNJUGu2w6tF_ejGo6hYYsuLo)b=T-aBHxiDX5+yNi|4&RB5qwv0K@(`T+6RqAwjKjB2!M}Ko_m1Nz=F5&(;3v^v=6*nn_1TR2<2=XQe|lyY01x%5=W+zk^4NIJYdDWG*U4tZ!0%@2q1uzbBRI9v;A76>e8#gJ^K^H4@brRcH|~G5_$uHj3x_Ii{=RUn9{9<;>bu_2t1Rl7(g=Jj&OJPto@2cEMS!0@kMGBa{&rq15cBJ50@`O#ckn@DaUS)o{1F>Z0C%6ijs7hk1D@?mjN7am(``I(x2lgf;5Pc*8@t)s@8)-32H)()evkWP=YdJ!{Qffcfm+ZUwllsH9sav`p1%lu(IC|?=04D~a5?yuAXR@ye1CkGwOI%59-zv1ysCx!dUk>He9}C}&fq*((HCV#KMp?tzNVt$?xcd4M@!DJ9|KkUIF64<v+-s>;ysdF7xT2;k8J1b=*J}o(rkRDzpB4$`wKhIej5G7{kiwO>)=IBW8Jv%DZY1tpMvxI(fp3{=FGVT_r>|YxzBVS%Madg6wY(Djl=$SY*Fw#3sgJ1{OYIK_{Y6aKF<xb>ZQP+Vt(mWKft`cUk-fH1^mv%bMFj(zaxGx(7IuMt*8us;xf*WhOa~Y^V9<$kce}?uE~dOoZso*5-oWC-w-?u=dR|y)a?ob@7-NJuih*x`fGJJaKCD{ah}0j;+)g{%VYj75DlJxAlje%I=zky{80|PPkFxNc`^~)JSSW@1NU7w9sJNUd^as<h4oEO0Z-q7^{3Gwtj~oOfoCd-@t>9*&viN#Jmf>HGu-EE6W4-|c!b|s1_WWA*4qMp=`_x(|5)U)@y1S^ck#U4^K2)0sX40MGR|*J&fkf&>xD5dHtq-KdZo3lh<!qlQ{Z}8+xx<O?ksq0qHSJe@WA#M|K{(c(SLw9$b<b!6*r!@iQm_X2l?WB=E?+=lbRWPG1d*&itkYW$oIj$b#3F^)4vcne}6IepN`VS!E51r!CZ%3<4S&QZBKK&W$>BHRlAwL!+JV@3_hU}zGvf8&~Et}f`?79kB7w8;M|uw%ST|GUuz4Vi|;9}SKeA3z&Dk*^;ZVxcdn;JS<Iul6T!Jpa~|r6_Ix@Gd_;wR=5=e^Uz?3Sc+x#9z?gxCWz+I&F;SL3H4`ZRO#k2isafA@|EoVWs}Wq~|NEzA9~gD;Gpwj#mFOMxSq;lc?Z?<m%SjWKgO*L2-7sJ398CA6_GJ@gV|f}`R>r=(UeZg@7oiqknYsjZMVjak`r6bX)HUeqQP-fZX;?7hnq>8<Yf{%Dug&-)!|E`u%(ynK4)YWuFG4SI1xs9+c|RhTbbrGNSmFX?h1dq!sEb(AGEs|{zZWdSxFE|ZKvs}CJKNiz<ppWzZwK3<5?M{^VD^cO4;k7Y(w8$VuVKXulfRaHpRwqCjLXyBCoju1VI>VKOjej&^v8x(VZT*j{0X)AYL>K$^u?)*GnPE18H>(LEi4aX(eF_U%WaqsnGd;{E^#iJ=p6J}sIxGZGIBC@Skg=uKpw!j6fFy{t<E%IPQ$8_RVA;^>#MSl0;nB~Mc1WOWf{Rt6IO!HlgrXxCFnC#*I=7V8;4TYU^$`Gb*Y1Sk5IA()J|R(O7;n3(MJs1XV?sSi7y-0iCXxl)WVuj3u{CztRc0q#?-=^QVVNCEo?Nkuuas$PErf|japb1A827ksD;&{7S@znSQxdiy41o-Q47mWE$lw;CG0Y_upCBw#qc)_%SJ6sV$oY@qPNliXwh=bk7T0#eUK*cL7M36^pbv^c^fdlKXnai@o#yJzeS7pVI1i5kCyyqEZ#x?nMEfsu0b8hdrn|ngK+{anfWDsmW9t^n)un&$<$M+#SiB7$<%|%hmuR&l3rMEOWd0#ybrC5VXeu!SlGvgePq~h>MqPPoVp9sTQfa7W3fzzeMp_1acjmOGJj*HiFq~T5&b^n#?;xF_jAMQ(>G>4hEspcyp5UXJ;tUMpV@N#C~EN)Eor6}??)fSI#*==C`;Ohv?xBG*ci596t&65TH1Up`$2pUOTYABUx}|w-ICft%j$#iSeaUwIj^#k=U`e^@;giue~V*X;#-V`r_&A_wwmm)h3z$LD*0YAF*ozO8Be8+GOQ!@UdFMEJ2L-NvW`rTp(PnMi7bh16xWL++5+ZD;+nC5>Dw&n2U-7Z)C*{<dF^V(=CdDUdmQAtV7AY7wwdHl;kA>f%{r&>IXY4&Tb?bM<|a#_PPVjN3fpN5pY;Y~v%POHEtLIRnd2msTGo>Wj7Kvzb*Lq8HeTO=TG&kHA5A@)V{<HZ502rPWV4uG;u-W~sAn;rO+AD2X0}Do;QWZ9mTPZon0qp}(hPl51G`Bs+QT@F`d7x{WuD(;{2u4=E~ZId(O)wb`-S<wrZ$<xJ87aP(2t-V!C1;`&$uUjd*(6Y$+Qv7-;?nd^uiWeVpEHsO)qs{PQ8n<nYNtfVVg|j^^%@QEo=#6(Q~MU9bzo{0QDj2@r=dypq@jWNZ+2%)Rwvj^S7n$!SqC?3-3-7-PN!-YV*1{ax-nDVOyys&kAajtze#!)T<1;K)sc*=(F?}sLxXWN&klW4dWkZ7g&yLj3s_e{l=0<(yuY?2a6W}oF@8b`U4id)e;|I`xo-T^>SSaYGF<v#G>0#3+u>ObUd}N&WuIJQ49NovFNtc!aiUux;XU*)Uk}kPo{259Y;USuqlR3r=HCG)2SyjJ&t~eVFQ?V2-y^}cuT%`GRYH69n9x6)7mk;x+N``Z6sc^=<1BCvmed=l(+&-bWi#r)D`Fp(?owtpF}-`&(o7OjcL=^4oNi8Ur>wh#p{!(dy&VG_hSF{BI{_0JJMp<r(!MGk1^CHt72GyVSTAvFi&6V7EJ$y{x1z<K=j`lVl(XnmLWWVx;A4mUqfHgz<e$I63Y=j!mz6JwONn8)Kz$0ZRUB$GEFW1mG;l|u}l+R+>$2xCk^pc4f>rW7XOl7^1ftToX@zQ*GS$y)WYU57X2l)Fc)LdL#c(0VJtd<TG&^NMNg*|wwtl&?bN%e2Qe1kfqFW10)0!vA`NR!-GTX=Q+Hr`0{w8-NpwHPX4+7e(a(}D@et;dcs+e8bt+@YvzGoF>QqZCeinT@i*CudCF^XaiI1m`u;}KD#p~1&)cvW&58yQs7CnIdB7P$KVgU0`w4{xpO=Q1_tz*ATq&C^N<h!ZQ)BjF=p85fOJ|E}@)Ol!i3=8oAt7Boq4C`Q6d+IvO)1JBx)8*P?<oT$}GZr6BEq)?(d+K5Il9uQrzjq)OJ&D?6lbC-P^+?0IQcIrx)F$iCJR_+)8CIHF@&r+vEQonJQI|CAg$7-kvFJa@B<&BH=<n!HQJ-S`lqOor`JV9^4f>QNkEH*HX%dUx%zS64#qXe(^mCT@98LH`S^*#Vvt=;R4|yMHg97BGsSA)dq;AM-yRwZN(nNP>n#9%UyHktT4Qo!F$k<G4&N31$v80F7H=+)w4xukd9YSr6;l~`;1*!8e{h5YX{Ap^ji_HI+{387c!&Vyhg!(kEeL{Vj=@*$kpRt&%ecP#Z#upiHXI|ZsKA-cyKlLJ-=wtLJs29<%qZj^&`Vr^7nf5KypIFi!aSaeJ^V8H%7*FIq*0DaKCo;XfWlld~dpzK?ou}Wf{j=tXmNlsi+h6*j46m0snp#*l&V5stVLvybF32$w&GbZioz{(cXL4@HJoubi*kHz@`%nuT$XIkVwXi9SMUSNxwt=zeHPjoZdodQ@ih3+{G<}$1tqp5N-HQ2}QMY1xG<{#z$&CBZcV=1`waFyz%`}OZ(a)ux%UJR(rr$_C*Aj~#N8iGt!x)FL&SskUDEe@VZpK*rXVl@;U8u!(<2B(H-HrVsei-|r8}kpdqz$AEW50+kWxougHrY|~4b;c!?@}M9zDJ+S2l^g$PFf|y%KCs+vao)JH8ZRUbtUF$LS2dJa&3O{T+~Gwi;tuhKaRQybw7GZ8$>;xd_3cUv~kQM*2=I5!`d*8ppRtQK*nuol3vfSa*RdSq%KE2ka6p9AK(0b|I`0E<ez`C)@!!^k;uQVwEqljy)w=yE8|Du*5R4tHyF*=_)iwt+VabW_Fsde_jC'

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
