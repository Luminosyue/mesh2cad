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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_003.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_003.stl', 'source_sha256': '779080dd86cdee20484bc3ff404fd81140886d1c719f7fdd08898eef5edaf180', 'input_faces': 600, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26716697216033936, -0.4524882435798645, -0.1572890281677246], [0.38077160716056824, 0.26695430278778076, 0.11456559598445892]]}
GEOMETRY_BASE85 = 'c$}r12XswoxQ2HmdMCPYv_uI))M!U^(R+zFQKF3&(c2b+h~63H=%NIP7A20T(FsO(bcPT_nPFz`{@?FCH<`QcUF)uUt@W+<*>8T|{`>y-4(<G$U0gN!Q$p)gpsw@E5}KwWo93#G=^q?2sBiyKm4=NN@1*5|ul_i6Nt@2C+jV!+#%L2g`t={xH`v3+<WV=MmWQXwBWQSVNO0h=-ou0Y^;dq=z+Xo7H~dip14r~XuFHB?_x3b-m-94DHvJ#}WHG9sH!5`fgsMxw6-yhSZqEm)Yim_a{0D`W!`Ji|^_73*&uj4W-&_RWGxKP5Z7F?T{KMBJ&xl%`pe0U;|21MEuG?K7j{LtyieED0V)!=yX6oABG!uON)r5n}x82>bS6$nNce{%6yO$nTzV&n4Xq4;I_+P&LxpySWZ!Zbo{3JF``IddFrTo?W@b%Z7W0Ak%EBM;F4_Dy3R6Bw4gPP;M=8mu7+cuAeZ-0AdKg#(hO8KTwk;mS!-cDS1+adnxZby*6>Nohd8sp$=!BOxn`SWam-=&Y_uh-KCzrpO?`1?U!;hT#r6hF-UApF0ZO8%u^V$ctB<55p-v<rOG=+7u`OYAT0N_X-ywC4F^$kWn)GxAQ~2jBXl^GWpo`lh(AJ#q_teOCm0%YpQ`uf;xJ^7P1waWRh{g#4y)Q^ao)aa{R&#QZI|PMq+s@>+6`j7yhR;t#w5-*irkL49@?m-|+#5RZ0^eX&Qzw;+7m-+u7T^{1o%tzBPSLcMZ@!?%3(LVe8JqTp-A%gH<`(FFZ$ojX(f*~esF<vq3wdBY}&?>k~2^5=OV{W+wQ`0j3pP|x6^7)Nbl3;6o}tkMrHkIHxjf4hjEKljD>nmaE*KU>>8hp)R`l=6Y&cHlbTu9V*udjS3OxG?f)?azpxagL1d-=S!i{q=tFKczp4`Y%5z{akOG_$><~zop(p)YEb<RPLLv^?sCZRT%xO6?}04dTA5xYnl~;{?Wfii~s1>Zrpdp7xaVm4^QzI9Y;UtmUy(wwx}q4`<ObICwfZx1GsNUUih|%Pcm=!*bX88$sY;Gv)@JfdBz&F%hLTVe0{x+@iPBRM!W16UjD1R&60rmW3L%2<>Sx6x7_fScAXh5e(Mg=SdYhVpdYM<0^ytfN<w|CE-BKVwpNmV-364_IxWO}u)Z?Gx7MyI>uA`ZSmd2uM9PmZhH=psZ$rPC2lqV>KerG1(>&x0`o}b;GJLaVG33#^PnGp@p#*%r)en@{GnU?pa?1<Bw>`Rp{YroK=rGC;{N)^e-mwjQThGI?9+wS<uWddHUmMv7>%#J=9DKd;WSKvQvZ8<V#II+e1HOqrJXZGA*&oEe=Yx4-`qTpBXr4Pr{72(aPrKjXDEMmv#Q)_5d~3uC)W^IdD}1f>4w;7;Z=t=m!-vnnuQXid&(5;Qqd(py{;_-Ttw+ZokL{_u__jjWSIr*+Wj(Ge4qvzQl>K((C$v|a_wF?O>9@o$XT^Q33Bh=-=+3oJ&g4A=<EUK}U)y&>_MM&M(f@jk>qeBXb=HP{JkUet$+Zfb;AeA-L;d_?7b9PnLs7^RltI?>0}uQ?+rDJ+Plas5b;$*bkZ(XX8Sk!LQBI#b;0W>zD}(;hUtE>?ZQeN)*D=o6NAw(TPr+Zj68&S!))4DoJNs}s>VLF1{+_LCJMoA0T#9=49)|mC9~R5JS)1|z_gynk=3D3xnU~{g9z))pS7rXxkA|<gp2z&tz2~h#{#I`CocMY?9{s!Bb07RQ>9GImwNIYHeg3$90{5MgTlVF>XW(1UI7|MFt>N3AMWa6E@SU4*pO8-Q?dzjZ-hAq;jL+ePvhN=Wg>Px|9^+uye@)7Fxp@vh|FtmYfqmC!@uxn9uN@nVez2DMF83Xp4SDn$H|2Seub9*?DoUO^1v?){e~f+&-?X9-^5{1MkjFGN-D%|cu;w!IXDcc5Z)_R(<{sO`4-1p>RfFJbp`&F#@x3DZz?|{$t;u`N;^!yYV4TepPQbTE$o^yT=zL7(;V1E<Yo9^+iHk6f+D{+3o}2eN>bds|`rrDn1$_NnKKSNI9_W8tp0;PC9^H`7l({{|)BcwYzIo9XjEi;LROGk0`k{X2Hg)gA|7D-d!x9$wrhnouqFxy;puFYgMEJI5Z|<O9LaSi^w+F13@|%~UpS8Us&_CvBcP0O!0OYsy3Xpj<Hd*p?>yG?-L^<@2sYzKGSA8DNGp3|(a;_^m7QWT%v&_?m{wHzYX7N&fY*ASs$MYV=ea$aq-t_zkwRqQ(ec+V&Jo0$vl%F5+LH}r<n~PsP`3mxQyJCJ?#?64QwL1;p6julH(_G;-eDlo37)P@{9?vgJ(&Ge~9~JPt)23F8k$IKx0_yQ$HGXc%E9Wac$_>74T6-C{=rJ<xBkM?cuX+ixj$dP*=oS6pYfU%eJf`*Y#(txHybWJpv0wI~+10TB*lT>2@}+8`yzOvXd2Ys}h@WGx%xh;i^rzncmW;>Tm3aQ@1&+!-v;G@=>wuiHZW@-_j`Ce@T|zncJm^n*%sLt0>tEq(r>9`Q)Gc+<54P30W&L!Sx*2}apoOUCr_$ngULgBr#nLO$pZ1EEr5~<hzUV8<V0^WZMp8a}!(OOs7d)5kzc+)gKW>cYj(OyIjF<JnP$}Q4CFYMg<tEmVt^08J=J<~oM|+Y@&LQm=OL<o->S>$fCH1s6!939Y`r&!1by~Ip<2$>(%$pM3aK1A6CgVA1oiktjkiqM4pY&DnJTbRe0N)bWLiUgR!_jYA^}|xW@2Q=*PyMIsao>>N#NYk*9_aUxv!!3PtGKS`X+=GM+AuEm^X1{&O3#yhJ8FxZb0$`i@|Fsc=hv7p<mt6me0vo+zxj4Td(HYz@w*3ZhaL_<|LECI!`DxLkn`&N+t^pNf{&zpx@Q;{%ZMA;AFLhi;+Kt;^W@VOXs>xzu50iQ)sgi(a08xidZ-1y{ya{`(SI9!+rEKPzCc^lU!M>o>uBc?_~w0+Wj(%Yhv%EQ=qM@QYRr1*_MWp)AMfYl2MpaR<1=S4#;rt>_?ODa_*VTn2l;jSmQpKm-{Y0nA^%_R#ebE32ijZrGsfLswkGyv?eA(hUzqZ5m2=Dars8KVhk0cwISBn=`Z+}Q_pFoTeIfcN-luJahD!OQIpX^!%lUB11S!AdxYTpa$oXjZmnl*{Wn`G><q^p9dWMw0_YnK4HE|N2%jU83r2OkqW2L^~Gf>~SRpJlynu)*nrz^e(m_}H|?|nqxzbqH5Xm8)GlD~91IY0mWChZy&Bjv3x<a>end`Z-QK%)5l#-iSO`2(xbAJ3k%KCk4v#HORTuO(Zu_<Hy-l)qq`jrxaw6yGft{a|)2zY6oP^*`bd^Vuc$uRjj;FXeIr*9!~dT7Q!miT+uYNqqAm%qvUIrFdU6b;u@u)l$FW?+=QU_oD{+#6LJqz5|>rBI|cmLGiW9y)kc69!*0%CwPee>a@I{&hIDt@P-cJXKIe`EVdbY<osT&llUV_kAna07~W&7ZvDhJrA$HI_cdhvs}B_4mV$En<s`gkS@Vw-|8(bY)aP9ZtS5WnrQ+M4TTt&&u~_f6<y*vmc?#{-J7mJXrM1{4{*lV^oo7V~=DWTtLHuKnFdkY3FZlL=YvQlmjPtau*>cp&HtW9l5!+>4hCh|>OZlIRpVAoPXM5m<ezLZIDSqd*R+)D#@%_o#?yLBBl4Tro`r^E7+n6m8ejYc}TR)Tz>(x>-kN8h#;=FEqw*c=G+6`CnHNOrh|Mm~`zwJXl@hx|I$bB=y*PPtMkIo{`wfzI+J?niL@y-1^p&vR=!?@@}Jj9O-kbR(TORPIfcv<oFFO4vc8QLs^U%jgM<@=(Z+Oit*-ZHqR__K=3eTRi&zS&Rth=0D>c$q()<UOocYw<U1m+v#BwXvAbeqF@RQf@8E#nr-in&Nw~-<sfgrtf%w@v%PcDSm7PtP|})NBrFC-%I?Iak!sW|4)pgwlGxuK80nxoEA>Ux?HfB_3VjxqDR>=AIx#9#c$PQ3H<&Cu<lKV*NVSp;A;5p&9`A3lQxRK^1?*;qrzq1?YB+*bnh_V^pL)2xBX_6`0*XqK<Dn6i2Uxi*#8spp09o0gmrJ;_F4S6Zx|0P>>}!KkNYP6_xb2Az4vaZ?}P8~^$qfVZSNnA@inFVl=5evtb&%2{x>&szKQF5Ib|Mp*LTZ0%PxMR-$vwhi$S|gNjb%jOTs+XJS*V)t=*na{O`AM4$!=sOMPw@5&zR=dEak;K)weya2Mb7+eoyl@<Yr=yT6C{S#si>VS8H4`Y%7j5c%HQFKj0A1U42w`Yy&rE3+XO^I`BX@mHRmk32pxI4{_8O%y+WMJb<X!MQ;94i|sU6*-q59EkRs+s_fdP!$=MDVOEB^Kq5<UZv5GT03_<FU)H<iQha}-e*F*wqQOu{NRJ~U2pb7`5u-WDZWn#+N+fuH4o~Q!2a1R^$h)n^Ot?+J@H3;$GB+Py5i`EL(j#}G%yr?P2V|aujwE0)4jxanD4IKfO_7^a|?dKiE?h%b4dMX6cxXhpPUPaoxysy)+i<Z;1c*wYWD4j{m1^^UHo$=Fs|C!uXw&#CRY}J`5>7;gJ+`t+A?qPi@L};-aWgli&wS9zhsM${>jw^c|JFSukZgG`->hnNxpYBZ7Jn<d87VX!a+HwZ=oOVC;9vQBK!8VR^mr{N%_U@lW^b6-Ng6Zfqg`qzX$Wn=G;^K(0tg(^}n`bpRnESE&j}L@*VR|2+nKfBU8k0)LzEd%^CAVFR)(x6GhOU#tUdKte1o>;!oKt-|HX5%Q?koxA<|1GVaG_^hf<2espE|4pqdCbCdRYuk_E7Yx2A|KbG&8xuV6dI9A?sTw3FNWT_M*d0dCfcO-i#?rXXdFaDsHcuwmjpULwf{=E1Hmr1+ER>eBDK28vSR*cM({4bElJmHe~XDv8~X+4@@U$nbk6~D_g`To*;1@=E%M56eGo6Gliw>|RviZ#EBf3uGKUc}Z7=W*)~`m+{D`R+O7oZdUrZRm#@$gh1WI9>Wb+imHe(FbJx{zQIz*CJBBl3BhRmOg|1TyrTSe(QJg-Wyhb3GN#&zCNsweE*&L5ziy@OmFdf4wO6<I^n(6e7Cmv9oES2Z>A<;ylk#@C4b?I@_n;zaXfcS?v2F%%Ovk1p5riHrgTljzi?2#zuVjUAa9Ru;@7W%e$WaJlk-e0{WkmMy*J(i=L*xf?oyu`jl>VUC;5Z@#h+h%uZ;V4`JSCLRPr4CA?t2YE%bxA)fDkJ)|Yt|<%Ru3>$_O;)Qyt<$unHW<={&3lYZhoK}#7d`(CYWlBY_njN{`z*q`-Lk>Wpfm)|E%m=KKl@O-c2d9g?4!`PAXUTcXLKQ@b;d+t1yJO$56p6cP!F8A6vFIb0M5`Xej`OfQ+59b$qscYgV1<5*cUku-BPnP@zUrYU$_rZNNzaLWG)lcewJJT|h&-|0^$}8`CGsdAmEuL9^L!NB+r9OkNpx^Y)`QU3y!X;1oVaQ`&SU}46ttRDfhQYUtD<%Hmh4OtZXpj6J;7e)AvoE8JZ<kKkw@n{B#NRtZ{KYY{pJ(utJmH72F7zCIaL%##RubQyB=6_@Cdv8jS`EqLzggzn+@s@V-8GQ%KhH>g&i$0{_qQ5}|He<&UB~M3`?uUp#lIbo_i(LVEY_WMVmrzI<gw(RDd!@4*AC)G^p^3e)CK#t{;{9<`VYx}W*OcKErF9H|MVHMPd3RQ-^WdprF^wn(ypD=<vUIC4Dkm%!}lru!5{Mbt2eVG&-O^kpJl(Si`Ofp{FZ20*Y##fe&1iEys3(mpZfs5Y2+p;fBd2Rp5sY+?30#q+oZf_ANf7RGhf;NyX}$kxn9Wcu}Zd-b5_!Rj+eX4tN3IYmuW|&e8M1Ecb}fGK>hC>7eA;R+GU<5=Lgf0lafd80pI45A9-whZipXeK|O7`{A3+nPLw=zXG#9MLs1`V<Si*5`9=JINcgs}-=ut$t9;M*4Z-=;Ixb24KJ#S0eNB}7!O7wWW|8&f?Jeu{;%CW!VwdE1v4rD#i1Quj#aJ1~w_Eq5^|gm5&~LV5kr-d=>a0>eS5YZH;urZISs=Ukp%)~7_%fWA^rbn(UoXGM(fqt3u)bW}CI7QyGH;ieuwJZvYDjsnlJfiV^S|SKt%o(1@;UoRKSav=i+w?Wl)utm+WW?Jaf5dM`d1xg*2b*27Bx~Eky&%qf&$b0lMZF7KMwux|4GN7YX7T$(ow_9>;L;tI=UKlXm3PkYFly#YHMm+a%*x6svo%pxh1s~xh1&`wH;Y$7qZfh<X?;!X2b|1dKl5kh#^KSHDaC-GZ~7PP?wXJkhf7I$x3gLw~_BspOf#Bf2Up{|4vS%ZY3v@w=fhhq%I{dWnC5TH)5j^XBmnQFcfc~t{`t9Td9l5R`Mnz4pTQX6tAQ%Ca)xiGZfFKt{~4RucdAzZ)CmKG89J{ag=(3x}SW4e203Le24skq4*y40QnyIJVS9bbptt?yn|{b?;yueH<2BE6vI%Qz&bojQ#Zxes0ri*mcPa_*V436@geGA@?nm_A(lDBemY9tL)}c?LtaN+NnS@@Kn*9WxwMtMfb1y0mHCujNt6Ey@2~WEn)*EFxGB9wjv}w6Mv|2-*HY(z;`!8hTI&3n$GXmAUBjsh$it23XT*4h;$R~}s6o_z<REfyhT;L#;p742(G10tsN>0#$kQ2$=Q0%Q)L^nso{*+~6Bvr88Zn1Dg&IPhLLNm8A`hlos6pf)w#~v&+><(h+>;zg9Ze1-4>e*ebs}{%c{JNUk)e17bvk(lc@cFkc@g<nhT@$J#cLRfXHj+XEOIDy0y&f%Mx9CyBd<==zpELFS5c>sSCJzail<RWk*ATzq!|OnBdPtVgUS8L{!|Ou!ZGk?DDF-TBzGqVP=}HO$bHj{Q(uPSK}HOuj-!qxk0Vc}P9#qz&!)~G&)}HNW++}p{gu3oyq=*rmb#N1OLjc_6yK$;(Ndq4iXG2W#Y?EOwA5#@;+fP?E%n*0cp){6ypX(wx|*Cw-A-LiR=SG(JIlpVx2I{#cD8jp%de+Kr0ItU_KnhMY5Hnfn*N-|zE?Vi?3hoEaT&>R8%XU#9ZBv(?nUiS?nUlK^(QOsPOjmkX$_62$58BRL<b{!8qt-Z*q_>g>`(5<P~3*vmE4A0lj=+M<-KZBYmjS_y{Yxc-sGaxlH|8W8$KBEC-oayX(lJ(Kgs!wsANQKBdRkL`xw#Oh|Wf|XDIH%P~3vroZN!knA)D)m|U6aL-yglDpM<wE0ZfwtCK5`b5o0wi?SWLshP;7jPNp|B13T%BkCK`(uigZ#eNLM4XE|W4al{q&B(RL?$j#eD!i9FwG`Q%Y@${qS7d!n48{LwqM67_)%YoPF*vUgxfqJGG8E@AqM#9Fj3~iST$-V{0JR{w069Ok1UWz1nVN^3hxc-(x{#g88Z{R=7u%unT5&Sl^NpNLeo6g6eo1~reM`P%#8o3MQ}2`S^XHcticc{V$1@aPpuQzvAm28^PW?=MOMc7s^O>PIgOjM5e;F8x3sH-bm6jwIBD)&#RTKT2T9T|naTa>@$XUpqR9~_uxe>K1S*bs{5xEmXv4z@^+>07O?MMzFw_+%+Lv2G=T9aId>_PP=dyq3zi;|UACub&?rTUPSwkMY*o2gyMW^!AG;@;F2<ZjgN)E4CK<R%QoRjG~1N-LAAl8aC)kc*IiYNENxN-L68D0ZV)g{-t0*^OL{>PN0dZpu*HgW7=Hj@p{qfZUo~m!Y^kwH8^aJGneL2h~K*LH?+Ts`dPl>pB<xkL16oS;<QCkd>Aot5BSiUTJbpa$$zzaz+%V7NeFXD=k1SM$XPqoQ|5GtkjvDj{HRv)yQAChdrUHJ?jbgu9xH|<lm@|$iI<KQ}2^clg}7&j{2B-pL~&elX{<gpL?HT8#Ru4m3)<ZWgJ8CG3sUVG4gThDe`ghL5AXe)Ohkfvg5mf;`7uC<O|$G9p4-j-%GR4I=)LNc6_@~{F<To59(*KQnk<i!E43YoJ0$emAaC%kuy4_?ztJM*U2grzoC~vR{D(mhMYuwL4LuyCQ<(&Cy||4S5*%u)+Zxb=^K`LXXpbXJ~0$OHR2@o2=xK^2zf6<@h&5FQ*Tfokd?k8-ylC^D1OCIoWfB2gZhd5gPh(;Lh*NcPs!iO@6)v5J>w+%_&Pa(p*V(mgnWc;b9`S?yo0)n>}a#&JC$O`oK&plsha0%PCM3!O-o%{O3zVk<a6XR)Hre+^PFKQK21GHKFE8XrtT*1X1|}NKGah80mZ*jUumiPhGMm^6yyHo*z<~WFDy>qu{UPtewm$nSx&0jzZ`q1V#j`~_#^cR`3dj)k(xqo&1Z(=*`l;5wJy0XpBav4lj3UB98RgvFU5{$oMQDn%)#fzPu?$uoWeP$SUscFv)S<sSK5}^gsilxQ|cK&v6))LDfOJ7xGYuWcAP5|XQuuj|KNOAtj<E}4CFW~DeXjUMOIqJDfO(SxDnOEDfK+2*pr&sDfKL;I14qsQ|j4I@!zbAT4Rp0qT;XA_vH6nV~W*Y<ix$ExF&x}P}OxhYDscBvJ15g*@c{*T9%xi>`X09b|yPfOOPG+R@~Hx#zr(UqB*Y>H{-S9CcIYc%WK7EUMsH8YsC$Ct+*kt8}U93$$5+@WJD%L271+usAxoOBkED>QY(_{P-{>tl9g5>=QE;+5qXWs#cRb`d964zuN7zGwc^~oR-B*Lii`4Eu^X@R@;+{4cOxnrQGsEiSAc3_<e`_5nun2rUUq5*MkabWjc_Grr?0$H^m8(b(etDhW0a>?i&~yhlb$!VCZh_y3T&4*qY6FMrgBD9WmKl8>aPAjbzz31t&X<kU}T}E>RvF7pPinny9a+(Fpa0`=wpNz!_g*38>%yW=v8L@9KJWbc79IjT%G@?|FWL?M^}sGU;lyqzy8gC|5`Nd-@I+)`p;jIw)0D`#?x5j>F|+kpIRx}e*pix#jO'

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
