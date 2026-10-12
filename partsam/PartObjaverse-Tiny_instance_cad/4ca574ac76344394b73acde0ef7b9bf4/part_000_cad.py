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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_000.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_000.stl', 'source_sha256': '3e3810b0879d4ad534ab110dcaa4b5b0b6fc4b9349d18af555cdccc44f96bf54', 'input_faces': 1268, 'input_vertices': 935, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17172202467918396, 0.0229101050645113, -0.44015926122665405], [0.17169244587421417, 0.1838839203119278, 0.10623815655708313]]}
GEOMETRY_BASE85 = 'c$}qu2ecGL*KN-X87@JB2qJ^zs07Jj5G98zIWy#_<eUaYBuP#Z2QE2XE;%z~Bng5UWkiVr0^&!|PhOomyV{;J^WJ*v|L<C7?cKYpPFJ4ps_MS+^*qV4Sp1jAdirwfwS`(*7Fjwgi#4R{fI&SwcO6*bgMPzZRz|JUpTXG;n>C1U<+6rYBMWxvI<WJAf)%|5D|ahju$Z@Cx4r`g4e0nmhrR>4bS1rJ$36qQDt%y&j{Ul-<3bfmzg5gzx^OY?Xz%~<FO5n<=<nyp4=MC+-MzCKrD;&F{?(lN$ol)7da%+nt%vqM*+IwN0nINQilJLGRz!q1{$+UMU+Tg8srUcCbmKpewz}4RM=x{ww`}Ni$f@5gz0au!6RT-G5WdLa$3FWare50@5kB;=B>Nfr*B3E$gb&oM7Lgv`6ZUWGNRNLv`w894pmi(TjqTb`fx{o`c=;?&PqDWTX#L262|B;69~{&AhO#<*XvTZ&U+C7~FNV{xzXI#N!YjAw>)!w4U@YDHpBX!}zIUJ2y-&BZpF@{*`TI5{Xx(};iOWAee!TWql=Z-YDXiCRs&#Mi1*{kRO#2U2KDhNz4BdKsewjXQ8qj*U!N%>*bV}W%)0>TT>+vSmhwMKeOSd+>H$lh$Yb@t$A?x9^9A4_y)T%mspngA2r~md=try%hS6}DLzFck@pbyy?p?j}Bj?AynO@4htYq6hRnOML0>eiV0jfp|sPVy9CKi~hv*PVX&qOPwEg|+U#@UzwfC!oKYoBiZ@Kf-^M4*%YT=~<sRE=lVd+MJ82Kgs;LQx7dIps(wzKI2?0-8%l$saSgOLDI>X;e(eB$I?xEkh<L-gdS>8Zd)upu=UOoou7Lzj%qC4O6SX0e#zEYx>e-YrMjIQ`c3PhrbD+n>sRWgoTGG<bCizu;H`E;>w!Dr$nuxEDgVqrYCU}GE7qqqJ{e07`dXZbr3bFMW9$2qACIMn-`sXArvJE|M`P)}4?D-ytq$Fe=<>aJiOYHB(a7=_x+#Av<4LXiPe0qD%fDi+Ep!~Lc%1cgmm=y#>ZV?zbks|fj(Q2E-_PZL@)v#Gz~LP0biU$}IDFrWTDLamPKu?6KK*fXEIkmnX1Vs8b~U$$mk+U@wP)7H)PLx?MwiQurJSClCAK;HozzXgle+15QQ^_=q;C41)J?yWy6JaPH~lVnbuqV#kNio_dh}0VJ&?${Z_K+|x6&-qdhpOjE{8u`B*fGk-sSq*Hk<u4|8T3bUr62b3#pra5v8MFNZs^{DF5geQaAk~DxK&T*1TC<K9$CE`01Q}sRxfYKM^y0U3Y9fkm7hO-Mfj?FLkRDr(f#f?ww=m-lg4j`os5TaDP8vpZjl8Hr-$RsaW>~>Lxk+QJ~q!tluxs<4gf>QY<}G_sZs2x-aEA-H)u4tcMD*Zu*ze{g)~wIs2*9O+O868O{E`d^2MFl)7mTQQ=YVQaAM*NIrtkU&x;n(ch(x{%#!@&g~_Rb)Wm}`k1=aLx&HJAH@33Ub<iSUOAi;OSg6{+@$Nt)0eM1EOU~xe?{r0f93mt%Xw55F1KAAUh09~H+6XHqn_-ieM=q>$EM#HOSe1)S8IJ^TW&uoYI6893s=U{1Ho?mJHD+Bx5J8GYTaA>P*N;CP<5%!Z(vMqE{7anMU;=!P5Fd!RONKGI>_lspJrn$-FjS@(?7Zj_m3CpS?_vxo>MpDxm^xIH|5~{uoU~b{&SMEzf0ZpYpI+5D|ORP{Ub|7jGv~QrEbdE=;l7e^b4t*ei0QO{X*)dUwFTNlk0cbdajpab63XFttP#7dIF6Kv!8>@wH`dPIuuK{pCg2Be!rw{Wf(t4U-wxaF2BVG6Los>JWYzFhvM_=b`pG&jnnztXIc+T8?`Z(ZY@n(rQ7H741C?r!z0>B(3^(GjT`T?pC3}KiltkZM=sXs_~Xwb&VFI1Q|Kn0p>nJTv()12e(^jhmL7OsfcwkCJ6aEIF1^K>FR7b+`Ip`1-?1_X-(=jzSh|(CmBZ)wiR-^bo-NM&O5Nl)oPu><liaMQj$0K||9ljOf9FbsAK#_o2V?1>Of7cm{Jj4Kr}Olh%{n~B2dSI!Avo^{_orhcH#_^a)J?w*_S(bcd~IElv)xMFv|Fj0b}Mz$ZmqeyIA2*?Y<Bi*shfTsIJAR*m-YlA%17#^e1hE*__~z`CpybV>UQ~bS;5!6I#lase3rTypS@@2al3jop8FTZTdAAzHZX&A|5SuW`AglDe|Ya4zHWyUTrYUeiqi3%<-0zM%c14>o3xJm2dSI;2W$EiPUnPti4o;5bW{GJ(yRyC6yoy4xF>Zp?)lPBU_XsFb9!+95T)b(A((C?`&luGb^N|Z>E`zxy7g=Z=L`4e-n9L=fBn%#>*oF~+@TMTGkK3kmZ#KBd0y=n*^f+l3f+EgI>LH*$a<}t`$MUl`@>-BuI#6VkJD+Mv)XrLegC%`bU9<3lzL!F?}gfL;Wk`8+dt%S0QX%{I_|ryRIR!Eb9}VfSuasK>cx8{p8fP{zu8&N{+W$X&aK%$o`a-r?z^OJ?z@618b$PXyWXXadbg6l!{ynf)MjV>8r`?A0;dPhn^HH=o8hN5*iXsQtmFPa;Hkjl!}hq%&U*3t%d_4uE&Ip)e7JZyE}!D7H#+M}>ZZQ@|4qmBSasWaXLzZb@V+Nu{k$7Y3`DdCsoUYbm$e?)RA`H{9Hef_A#`FV>)Gb6bNZLM@o(i=%ky4SUtX*0_vf1DV(C_+0=gfCLX)*_P3#nrU#T1af!m|C?oYjx^J~U=q1(TMT|2R#1%1~>_!qi)t`F>O&*_XWx4~IHQa9xzb^AU|==Ocuv}SzW^KCaqq+jSJ{ejo(aXBZ?vRmu9#_p}=(8C2E?s4kD4rSR-nko_XC3TZu@A<-9Zu8ph(&5vT;&lw@*8DYloqBj{LB8(fVe6gsD|J)9;lxZ@4^6zs^CwTH@O7%O9{lGn&)a-CRqMg8?(_ZcXSFst%U|lI{H1Q+ZwTF#zg0NQ`nA`%Jz&00>gGN+H2MnP*X$pv%gxNgNZmX~NZriCMCo|Gkh+<NiSm!<4yl`Yn5cB(c_jSZCC*pBI9}HnIf&a!iwmr`EvDCZLh0vdJ-p;3`?;P=w>Mw=^}C#U;O^}`PTfC?_0W{pba<=V#t1#I{Kg)q?p<|E>)v)HbUM8=>g+!hL${h$+O7S*zMcK7|0ANlq;BfVS9h`2!)LBX_?NozAAT}Z>;8UMc>KXUmDJ61YgBm5Q$^``o|U?pr;@sP&Xu~Er;74}=igv$)<gHcS?_G0Qn%*`g>KIiO5My83f-P3l>W^;q0sGlLYYo8PuOob*UPlxJPyCRaDOb_T6SkwEZxl0Muo?7gnz{_zOJi<9>09`3+nb5Ts&0k)}v;ucPXHC|D1YS_f;8@p#5Wfle!t-d{a`h{%w`@&h$&&q+jaxJhKdM(%*XCA>Ga^|F9||Jwi9>@viHpb?e?zolb9+CwpS)fgfMv^_qHxv>rN_SNpNozl3hDe+k`Q|B^bM2cz`GzP+(@dp&ExJw1L~Sr4pqreErI`b+-6&%w7`y8Z%v_;<=bt~Rf;y<BFEGhb3S`I5THSCo!?Md`?w)J?uZ!!z-Eb*(nbwchTRgqS+=6+STMfYy%(Rye~)=?L%J*-q=hbUCyh>eKmbEZtsD5xTveB6NG*MEcpVHX)X7^6Oun!2O{2IbPqH^4qssFT}e4GV9haceL)SK7#vw^CBxF(l2y7{X)0XFLXQo(vL~M(Czh|Uu$YTkTzklvmHv^mpE^&uE)FYXg&1wAN@NQ`sD6+5qg%Dd!4#BoL}qVF%yD1J)bYp>+k+ntozPDe{Gr8gZa~PIvXC<df>zny*?hOotn$@;c=~d<Bw|Hd*q*eI=z!>^Ziz*?B6?e@5GM#oVr!`wAKTu?k{!bSL!Ce-aNCl9-ix6>g-=qx5o{k+vA4N&G;D=-i#YU5B=RnrziYkrq=xzdh<B^^=!Ux89ZI<)?58~Ty4m@m2ZmHeb?jozU9}~b-md7?=$y0^}t_~S$84)IiXLUwb!YKs^sVN6#iE4BMN=Ji0ggzKb()aiJX4ydy%@?_u?Izr1emtJbHYv_lF4G><<aGWZgR<pVrO(5UHE}A>NINTKCQIE{~{3q1*K+bh{pfZr7s>Z|YI#rXB<Jd-FItx5qMl-N4s+-;Q_f8yvpdq!U`lJ|b&=X4Y3<U80XuP15_00@IRfJ$x%4uLGvOrN^0YE)VPH^0WTSO|1uW4%O{FoTE7V$G)KO&cRv_l_<eF_67Mjcjw=wQH73Z-P~8NYNd65uO9r|J$EVJZ~Sss-*0*k4W6&-(d-8ky1n1b=pRlx88bX|6W*UaQR{)!XAbLnH1{(HHnIK@baVgHJh|5W%U|RBG(6uK-FJV)5vLxm^MLPPFrEjRF3{~c*s`qFgPtj$>G0=v>2!uFCf9oC)6$&IEz5O%`7$Q(b9u5QA?*jh*WrT|cwY9}1-|ZohjMxDEv0qqlS2GEg7M1e{tY>fIdyOPyc|ARy9ocmxRiX|dNuSo89JJt$I0BuIegHkb>9lst+Z|Ud3{3KM5munjTXFLAYU%MpDi@A=#@h;bZa8gDZ?L6d0Dr!@Y(J9{7;#=UG3aBQ<p=kGg=SifL?Pq>tAfqdibpb-XC&vmo9%_$~Ic}r>uV1nNEL-qFVQ*`<UBjn-lsuFZg#szV0B_1FcVKJ&^2>z7GvvEXn2kYYFY&zyBcbKbrCe|6Z42J>co2=ed2a<=gEn2dSHKhzgH#2$s*r^NWj9pK$t-y73bg9)7Ib>*HgkN9x8;RCwV>rbp`1k4#VCuN=3lTG9Po>h}Im=&~OfUA9l7%l>P0*-mUfq957mk@X8*jsr%IYCk6ZqW{|I6#dlpBig^Mi*dtFrx*{VZjYZ&mp|5iM1MEB?AJz@?ceCKe;GZhe;NOx|9TI$imw)<eM;T5tElj3S4NlZQ|i)>Y@hzb%<E(Mk-G5{72fpU3*9!w%9qsb{wu?qe%CO>`>{kj3@td!`@Lknd|H_I4U2XdT*$ht7i&=~-j6Hl(bsV+@1vFD>VwnlU$jqa$vLgd`t_}ErSJ3P?}F4#IYfmw^}DQ{)@Az)FHg?%bfP``x1`|w$?;)D9@fS0VEFSlSr_Ag(Pcli;wy2vihdnjxt!A@f5+>1`1wclU+Ydep5GPYo3GV<em)WR6~0?3bo-Fwo6+UC6xz5+>+=35)G(2CasLx~bVuuQe3rTyPi$R`KT<d0y*pa){g=283>@gn^QYpz(VsY&=U>JBr&SyGLE`>1yu_oQH{|`TwKX~G;{MiOC@at7i~D5%uHvkV`)Yrio?4gp;eiQ>{2VKuN2Kn29?{`qJdZea^E?uKX)C8kJda4-p8prRc^;9vc^-)hkLMAoo97W<Ig8gr#Pgce&GTBgeqO%+63>0%G?TdfiswgLm(P#8po`~ITNlr#q4YEOy5jlQe`O~3OYxj8b$cF6==MCA&`o(pg*WqHLO11Uboo3Un0}V;FU0(V)Xn^Z@8aM5J1pimj4tOl{Cn}fjhsLEE{)dZ{E2^2KCR37nb4gAT9@-P-Z3?`F6V!2UC#g1tD|)}za({gere4pPQRERle)cbD|AzjQaAHsQGPH#CUtwAbjNZo2Qk0r+t0e3-wX6_tAFR@{G`<FbycC8^h@1dZ<T(KeyQ8*p84i$UCysY>1KX4ocW;E#r$oQZsu<**V4M2f0nwv-$3Xlzfn5opQCj2JE@!ehL3%xbvaKSXmVHUa=u;aCSSo61rO=^6YB+1x5sCp+vBs;&Hgc|oAFub_B?Hdo?4gd9a6XJCF@+R%k>ng+w0f2QtA5}xxOQHv%VvBv%V7*-t5nORF`$J-XwK<eP{hptw*hAog1cgxsE1vlTN9dbVh|oI>R?uk6JHVJ%iID)*q#A@3R%US$~Yu&Hh`VoAt*i|7KsV(9QZ|R65Q2_}{EYt^W$$UjLQh&HAs@&HAs<?e$-w+v~qVx7UBAAFTg|M)Uo*T<?~;S?>-6w(<SCSWlO_z5l^|OzU#JUh2lb@74*e%l!jJm-`32ZBB8$i2Vabm-`0--ixe@eG9=AmsuD490EW5!08eDH>7UAA0c$pKBIK=-h|Li`;78$-lq_{X`fN)MEmr&{h9M6_Nz$U)R({Xeb&YP8L8X%dqTJ0s};K0KNGH*Q9nn?eLI1;Oj?)we1aJZYF+LZlDZk+tocQ>F83oDUG7Kn9e9g%vENDR_V0d?y8Qev_EQ;M?xzaeZOVS+el4M!{aU{4?X@oVk4fEL#}vA~UMX~Y|Jc!vd|k1hP3rbKY^~8;o?^e8)J^)mkEgI7u^&(BW<OqN=o(I^*zYHGyMCYV;_?^!38ilDCmeH$b+KPj>ZUxcW?^ohVn3wR?fsB#((!Y+*l#IyJHJ!P@_dun&nb0#KWE4CT9^ApLva;Ym-|IK)!=yzu}@X%c79jCqjkAY)nEQy*2O+pUzdhjm-}g>bhD3o9_w<yuGGzb-Ef6?E(ft6I8-%0BD~oT94^tC!^{22Qpf(}K&3WXm-~~WbnH(K&FsYWDE3QB-L9|hU04_Uu7fALa(RmV+fq0Cx2-DO*pJvBE_Jg%JanKp`w{!kqjc;)w|e$Pc}DJI5A@=BF}Y7ZN;mtZeWN%%VxN4V`X^kTVt;;=Zp!)YWY)#|0#di%7YI+`^vL%Ggl^s!@Ya~cx_Ey<>UMc%pTq50ydM#zqdWt{=W{y6`x;U=?`wpPvM%4(kh*za!+(4Q_jmEWiPY`)^)e-JI>q}YQaA6L_;T&wauDyoNZpL{;YT|o`n#zwsoU?@oZ8Ll6z}^;-F_Yyy8Zhlbo+gu(?_}7#QR55x8FZHb3URU+3)WN-IS*_>_^U*cz;Uj_V4)ipSXXC_p_pO^L|!?s}X+8`(IKw?|%jA-{EwM_sgVi-Y*L@Vm<2pHKCjL*Fy1s^0*=1r<1yQpU!ukb@@J>)Xn>J-ll1fYQN(BKB=4h`d*~hx_9=d$oBy+XVkiUf6&(~o7Uxfh*CHC4Ols}9$K(AB7C@c9=@)4|556u9Q>OKaeBo2m{PazlZ9@7e@5u0od-WD$>|sGhf3XkPwG3?<@>Etx8HAlqqNrL`?gXy&!<v1&!JK`&zn{v>+=0sshj7csPK3WlDhpo{(WV>u6Xa*=<>Z|soU?z<*vg1#rw`uH{-c?cWrJD;{9u>oAEZBRENu7yniiqGyeFmwmTZp@63D3LO1p3{kaFHQ@n33b$dMQ_yOzU{r4yxzx$z!tjqV`rEc!)yt@Z;zQp_ZQn&Nlc{pEJd><f6H{S>7HG=)f?*mBP+y|x~&Et&xzJbu~=X4p~JdX?Aw8LQQ@vMvQGX%P@F2BzZc29^1Z|)DJZtf5L6<L?xbCA0I{$RK1>_>ceBK(N;sP9x{n$6`bz8@lWdtOfH_Pm_b&Agn@?Rh!r-^|Mi-JX||=``QfslmGZeu&h~_!bo&^Kwx-#yzQ<c{!<@@lfh!UM|Xy`F=?Eg%RVk{XGh)o9C=4i?|%bcVm227PEixof&WDr5s*-KS%2JzD=Rq`!;2G^W7?;+uyAcy8YcMq1)fB61u&9)N@tjxNV*<q;8%sdTrr;A-+2l^lgpMO+S*l=|}!P`#3$~J4n6-$2h$B{*u(~@0&>--(QN-@%<%#jZ>_P?>_nZUgY1q8;2slfA#Jq?(gEeQc^eHl?opJmdowt>4@=A>h^nQHGkr9Lwt8j>h^nWLbu;*lluR~zx`gD^l#p46T1Cgn@lIhhtT5dk@pYg`A+J1z6<60jmtrN_e|=hexr2r{W__e?`wHoyl+N)hfV6HzCuspSQp=^i_%T{q08^oN!?!m6}r9tE5oC|OWj@<7P{&0QaAlw>h}6$BQNJme8(?JH{UV)vyj&1_W*;13u|3|KQMf`Ci@ZJA&k<^_v_y1%ewgfp|2_H@_UJ)<o)@&;=71aH|-&uYwR&Tj{L5p)XhE_?^f33cO#{4&%^)4daUn2I(4(JCOmmQ=SzIYQtI}1ET634bjt5!K2G59;yaoCkM{F*#rHP7oqp%=;ya&GH~VLN^I4bQ`INfd4vW5EKl1ycJ2M{F$KrdW!Dm&qF2957&+OB>{NAb5&G%PrU3>>s>L$GRIqUL!tx-C@ziM>(UDjZ-=d8=`)(YL;2MaywyR|~Mzl&>h`8`{q%kWX(xfQxjPkh8zhAT`xv+hA9%OXo{WwE+-bbMl%MEWxr`xC=G%lv<RVz^|fvgQAG-xyBwm)o)?EBggT{49+4QQ#Q|zlP&}9?Nnmo8)G^<7Q5H8GI7>WZ*e)!mq#ye*^zp*>hztfY-oZfZqmA2EPsd1&sJ<81eJK-@wm<-vYWl%x{7J1GK<XdpJ$6dYC_Vq>+vvDD14zudE!f2zWX04A3cD7iGnj^;9+#*aMufJ2+uCaKet@gk8bA!rxF}XK=z!;6uTOz=*d4mIZGIKF-ZXysMl2)AcF<i-K1G&#0`WvR2B*14n_62mcs28vJAMHZbC?mA$X5kFo%8DtKRIA1M12I1YRq&VLG=3SL^JyOgqbl)VdV4lD)U9K4ybh02B~`x!VGobWU7pTWa!ZWq)(UIXR_e+|4busL{R@D^xCFVL0<b9<PR5wEF?`eQDInPJ5H18ad3HU)2rc>RI7!3mpyH^KG$1Dk^rwgvAG-VfLeoG>4FKXB^npSZb=_5d&D;o~7_Pw%-IsXe_1Bi<PJA-KoGXxb`q>L10yC&GxE>kv-Babxfa;2*oWt#(5jEebx~%}D3RBV1$f@!%f;KLq~>ocb0a_2n)w;?$>qReA%3b%6E3$%xlhI8E6NWvyYvTLG_ww*voESp{YFl$8h81uqYt9Y*|RWjCpOsosF`;AF(xDBR+*tbNLofcwG2$_^^~8F&bs!u*JEgg=2(m@Npm1wIZTJRR=^CW0TtH4Xr;g8zs(SAcuLw;)a;@BnxiajpWdICvQ83nT5szo1(+Wl6v_;FFb&QMMMi9Q+q$Un=_z_zn0BWgjaW349N{0elStAA{o`l$}#{6u1j~ow60mrU1u+uSFV;0C$2PMcj4372rn@=6m2-@ZXjFr0fpxEAYO`>MI)oj0bP4Y%blOflt6OrE4(KM!X@8uPgf+`TH7qBYs=iWnBL<u1&nPvRWvgS}3DI@YN9K8{!=C&z0>_wh6crd?d=eFR(uNCB*p^d=HK(-(Mi_U!m^l_!DL0l+6QghvO~ERx3LXJP1AxVFm&lfm0h=13zovYaZepM0p%US=>e*C@(XBAA=8s&j7G3IJLQNkgso$H{z$1?Y6j`5`GCzb$=H1a~5@T9rZjNbxnLcjyEbxfWHLzB3@Woer0ul<-rRmE269dur7FKWp69%1gs9;K^eU#)*e^|yc5Dya53g`F)ynuhqCz=;}DBEoue=nfv<s=Q<hU%dEl$y|EM_W6#f^O7W|R2|0sJ1{1f~SWsj9z1%|<0DxO=}GmG)L#r!SBUqO0bL7K}VO_a9JEXH9L^M%TWE9(k;2fU+2bN%YK16U2bvWn|<aXiA|@KGLlTwpN{wV2a2hM^vYp$<C37x|=eBFu?0tE4Qqi?5R#*CO5(Y3l;40p10i;t}SCk2+`@wSncpAEIop0{;M~dZBuF4txfl4t3@RJ_mmUUt!=?@IO(1e*hml_#+%YLfFT+R$9~}q07P3;W!=Yns_~RuA;^5o3H}-E7UHP<pt&guZ_It1-=4KaqA&$J%lGteTVu|VPJmn*Od)W*U#i)90%T1SrcXTf%U-KE9;=FEwG(~H^p&Nge5*4ary$=f)9h=F~Il0hvVE>;27}sIM)R@7Q6$_bp>_-Z;Eq`fnC9y;M{w_#^808WmNVK@NbKG25NK4{<0WrfM>)x3YP(zi9=We_!oE`gl_=!fY-&jhQJ2k8F4NdupxK`obv#afqzGRSlJn1F>rd!|5jO1;A!y6I9Ci<)Dfo`!WDyl8gVJyU0`wW?{MxO@Gf{|oGSsm2VM#1iUUi47gBk!lobP}0)L?n3o1<MVk`>2L+RU<9R`NLEu2dQJPb~83n6|X_$E$qDcn-vGVmAhn;c=5f)_-ZssKr=0-toQDzFN;g>xx@Rl#>4t;>KZz*i}&scagsEcm<BUsag5fG>j=adDjNz-iz$5vMHhEpQ4?@qNH*4o=~!0ZTi0O&k-Jaqv|*CJZ__T_XtefoD^=-{O4kM>!LJqVOr&%~P}!;yu*4PnG$BBfwiLn~6S4I0l^JHbML*XjjC0y4Y7opdXy#&O&^`vEUT9G2%By+ax~C#lA)YJAzZ(K8R1)1-zMx(^T1;z&F4tFVm2pY49-uao<OL!mi*Hx222Y6E*_xrEt2kPQX#%6t@lH6E+5?xUCSMFdn?Oi+yzlb^>pMvTh7~51iuewKzWE67U)DH5%9%yq2=sXlJ$29;zX3GsJI(vLQYlzD5B@gVTRRBVVO~)xfDO?L&Lohki;tvpV10#bYC31MpTB`zix04Nh^hx;Q>za&U^<0`UnOf*-KhR}feRJSW9bmIYW6oP53uzl2r5$!8Y$B}@ih8`tmwgW%+|1^g100w<p};g_%~IQh&BznM`6#3}Bph)<XmoZ@Cfe8Lpq)EAzhKRiJnEsnT35kIHND|}@|+Ok3?J_2pt59|m&3U%EH*cqID6Y2M_2Jjtl`mLegmD9j8;51g#xEun~Zv}Ds-KYDBdcY6BY22f6>SbVd@SMn7b6^W_>ig7hdjLNL?~V4_3pgD-GwPr@umyNyj8jj5Pr+}hb2pSd0zL%)RoO4fjsuT@A5nJL#qka!&P~L5h<FbXhxh{=UkBa*KMJ4MfWLrWN0<=sF!(iuc>sI}9zvL-z+>RY!H)nBgVTH?&HFzDUIcexuJ1o?#vI@@uTFF5JAsG5n_$kdATTR<GsMjYUJA!F_fGTvKLSsJ)7&Y|tL6kgaWlVzG+hBwT8O*hi^BZ|AH->`f#RG1UIC|d4O++84NL-WjJeSQz%t-8r%LnuuY!AVOzA9*In?|}FC9}}&LKa9`@rd1XK+2jUEs|y-&zV-$HAN9xH)_ir+H&q^Y|0^130C*3DVsJWl#JIgrTs+LpVN*y8Z=xH;!qZIgf|un2D#sF|E1Kn#Tp;1MsE@`vx!%IK`#5l?M0_obrAR`M(Aq#B(EWS%H6oQ<*nKxi^JxFY<L7`8ka?7($!8g?35!J@`4aiG9Em;8gEfJUoBj7<Ep^6!#y*CwvS}>lC!!&<Z#ToYpXCE#m{=IB=SCrg`y-z)Ik>{zB_CWr5|uX<nM*^aNG}r}<`@gU$f#22S(d6sH%kCpgV%)BJT0V0ZAj%H}Cc0ImezplqYEMBo<iBg!@_I}F?ezE)XK*&5(7a7x=aq>r#Gcrm0k6R;OJt$)#6e-+?M;55fh>rdr@6~HMBtp~gW>;q2o{FLX6z#iaK=EYF%gqgspOz0Zjf#t!;=O^$>*c-eD(pni<1^g47>kX_7PHR}yR$2mEfp0=t9|k6ZuR%Sm1+D~N3myc{13&DjpG4G`sjH2sr;WJACY;-X^ILFkGwN+Fu0I#oHg!4==jY)Zaca|j(cTH$fYZ7jt-p;2P6a3I1KtN^FdpICAZ#1>GHZF`(67d!FA*=Ou3bXe4B&?z=Cp>_z|CuVgbl%I?XQNL*Zm0JcK^E;*bwI%;+$D0q%fs{g~6M^Z+>7Q@ciHffQ7*efct=NgZsd%18aa+2X6{&2;LOD39te9YGt#OwFkBYZ>Ow<vQ@yD;H$t_180G+0=5GhABzyK5wHb#Bk*`&OYnH`#lTtMi@_HGXMzu;{-Nv}H{<7S=3gs2rEGwQv6qKA8S#O@-rxg(U&E*IF$m$d!3X);1|z;5_&NA?@WDt6`5z1;J_y(goYsq1xOuIZaD@Bcb>rb~UMD78?*4bp_^zARkO}X(|6Nliz7V*={qI`z2>2TTU&NDpI9xK|U2rnuOQ0<WUjpt24hQ#xcLa_A?+CsWxB`4BI9-1Q(n_4xi#vFDjhgVkZsxS#W2l?giV53$m}f>9+KWLr44lrjhrjmlMZ6RIbOsIsAAxY4;G517ABnglfbGFk;JPD$bdGpu_@wj0kS5}kw;RYe;WTh+C+pFU2-kt<p?oW=3@igq;{&bDHUZWJr*>7(!~O`@!*^xGtpa=toW_&v@RuFFh*Mjvi*{NUK8aUB+}D9wz-jy`4}az1i#V;<(>nD~U<2^i5jPJoGdPV`72vM|d=aPh{o3$HNWO^YRXnS*s=%_~G``h?zk2XRoYvp#z+WBsd=GIbZZ%*z@FpnRroejOw6EY-`1=*U8Y2$H%?Hc|PVJ#B+7e+K@S!LZ5Aav`&WE^pfmy*jAuhE&!g#bp>Zi26pB#7toW|9fZXO#6r+`zOc(hf*_rR%N(;flxM|d5a#^G9S_E!tOh>t|v6hPW5pxeB%hRS9GCxX-XKzk9E06zt%@qDVAuQL_bh=;G6D8HL1JL1DBZ@5k)T!T1`GqeZ74{Qa#2zg%&oC-dN#uN|xn*?9PsZUbh><DZPPJNR4CiM@(x)`@-Bad@{lfY*KhXIF!Q$M0UP#Ks9yc*g|RbXCl`u(KezjnYD;Pkshzbjt@Pl3~K1C7gJ;9YRqmqhmy&43NSX{@AiY7%fLcq8PcA#fr%^;hb*Wq@yiXGME03oHj-3uRstI0c->r+O&MdKhbn(;Uul%;OOD1*dza!pKKq<bn8i>fATVb^ten?*QKbBfbVkyqU7+%IYg0{{jBtVopZ<F7O-hyWn)qLCOkQmNg&P-NihO;^~xq=wkfH#XL^&w94|i81uUR<rFRr&d1?+0nJy@{2=gc7xUZ79xMA+*>2!Q81b)xkHIUce2r0Mn-*Bi%{;fV`Re#J;9~HR)Grku1zhUj^KrZc;pw;w^%I2_FqND6Z|d5=EBjvAPT)2e@gIP{gP&ElPT55m@%6wV;OoJMDm$+%LD^{-@f9%QaWLZPl@(EGdZMtXn~nHW7vov*r{Hw`IV#Kxg|ppk#Q$+Io(KO2oUXr0*>+`{fO{N#74kv27<{&}Y^taR0}Fz$#JPFE!Qc~ct{ZS3_yois0(67VM!3bmbq+oO#}iPV>kyaXxPgno6<EnF+HlO60X#Leb!GX11;G0&>!<8v;COI~OXo5GKL)qpD-|$5cz?th3QPf>%woT8;1CDzkK_JmBg85Fl)jX}^bVdH$End)h|?ck!vl1KCr4SN0Hy>_jW}^Y5BNfAL&}x|KLgK$bJc;%!82KWE<3QggVVY6z?9%~5Pumk!NK$3I1loafVgvz_c;hle6_;0%C-V`IrwVCU5)Sws8cGJ@xb)pR2EB7?u6^Xsa;V!D+ufc{<^}93SR=|0bk_ea{=H>;1p)Ai^CBP1gG$HyaKoc{B`(>1Fis{3tvls9tWp59$*~!M1`3ZP6oaP{)vmvO#)5^r!X%e9APf-iHNfVxY)rd++v^`JTu~$G%Nw9Fqsi9Gt%!yd!{B>0GJwl4(k3hV0Q4iD3^i20C+O=$@IWf;B;L|YcAj<aB4%#Q2)zN_rz)3JLBSUa1Z!781Y-cd*HXg{{;RG?shYO0_`676L9mpLAV`u7QW9S3~?HJPodlwgP(w%!gWsJ8pOw{f}NqPxSKJ(n>iWrG{FD5n5O}+2+Zkbz6^efzz^x>x9GpP79sg^<6KUh&xvzS5H3CZrH3!#3za1(TLfGQK1PLEplmd7KKQH3-c*(gSQ0!JIQb(?fbY?W`<aJvg@^enT(2m?mc;LB5%{IF5iUnMi^6{q;G5uckiOL(MoK^N*|_c;-~w>+MLvVT72vCp_f^0I@F2p>M%w4&_dK<-IAtziN^lo=2Vela1Nd|g<6IAOx-RiK&;ss%?;R+9a`=e@p94R1K7ez?lOqiIi-RxXchtFO%I*XI0;lo$f{VxNUEp89h~EJ|11J9!_XT`B1AhT-?x)Vf_ge4^z-Qp}TX4z6eSI1DSFlUC&Lv!f_yW|^t7r>vq7Bl$Rx-31!c}M^71933qOVXpC;lh;=I1WHulgK)dKLI7;NRdMsW|hfj@*o6-OR~|dx0sy-%ys$&GFJ94sj23y4OpG@aEnx1=>;y_#z&}bv^JwaXdIT7U##}9Pv+-%~F=p&6vZ@oQ!w|;49!0RG68FHxqG*yAj3%%mKa(;pjXeopa+{4x}dst{sHULZ6+5xXUo6ti-so5`A?H`UADq)M&GD=v!Wt%NxLS;P=rszI5?@#+PVQtHCb;{{sIE{dWOyId}%-a{}^2=_H;E{fydEa`Y$SOVM601HS_Q3hneVFc~=g-kx;*`%FRHJZqdp{S$i79+twNc}^j2o@IzX1tvq=UyR?LC9o6lcM_cZo^btJR~yuC>Lg{yf&IacgZ~I@1O6lU4PZa;8{k)f6Tz>5AA=EJuPjm7r^-$OM}waPzXtpO{2KUu;3)9>;6DSWg8vMD0!DnZvTbx9r0gQ_Bk+shw}1n{Z-GAmehB^m{3dV__)YK&FydR4byrqGmHSK}9T#`85$~p~r?NNI@hl)6zu{sd-a}b$Wu?^dY#<$%bg>cdrR;rWWz_K;ARU)>u@Ud1?3t?jtJKy#Y{W|fkAssDuMOM}PDcDq;4yGA;@N>efs+w`s_YMC-zj_9!$!O?@E|xD@wb3Gz{!Xg0v-S-Bc2WTEjStRN6LPu-w$P}JZ!}C0{4QG5ibGU3Qk7+b>JRwGU6$LUxJenzpv~AW!2PiS`YL0aZE<Ms=|H>tJ9bc-WSJY#C-|}D6B!_Ab5WqlM#Pg;UI<YDohVP5XWT1-%;pQb)TF1gNt#Bi+Lt>ezH3M5^xH5d_9*ti|5~$g`d9MdTpVWs?1yRe3JR2`+W6e+;za9o_Kp$#*BQ;*cr2%@@2nt9A7Uv-RG-^54Rq8W>PD*{tv`ig(d'

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
