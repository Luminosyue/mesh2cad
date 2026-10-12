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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_004.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_004.stl', 'source_sha256': '8683b1b8a4d1ce1ff969101134182585ce75338de57de0917ee5408deb4bff66', 'input_faces': 668, 'input_vertices': 460, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09207606315612793, -0.39597639441490173, 0.047250840812921524], [0.053179264068603516, -0.10349321365356445, 0.15760037302970886]]}
GEOMETRY_BASE85 = 'c$}qN2UHbTw;t?KR4h^KR}n!)#EzA*W5*UzQLi<2P!v0kV!=+tg4nJd5fl*+h-E}nEKy?D7`+-3F=`~1M2+R0+4~#b%)j#1dh0#c+UxuH?w(y{&YU?@62ETw3zU`kUv;Ta;+!B`T}jf+Q7S8ijGj7e+{n?vo|A)SIY>^VYyWhN?AgDE-#`Z`M4IC^YIN|(sctPSZmq_6yLnjL#sp5CHg)*qVS!Uejn?!|!zTuh7JBg5;X$Lt-|mf@dU;qH)%LK=v-}_b71e6!zV_%z0d|jXZ)>Oq%t-Rl^cwR?mnRJ;-E#dc>)HOKE0+1B%lR@{R|;^P{7JVow664I-T%)N^6PMrbX)#-))RJ<uDC|Cf041QFQ3i+K9LmP{_V{pq$h=tZYj2abZaL+)_>1Q*8Y|r{XlV~kixA0u`=0MkMv4rJ>|g>ioYO);z&0;A0<8gFzM>UN!;)BT-HlRvi~pN@cxlQQ%PUDl=ZS3S>L^n{ZC9J-L_#G>yx{)f2JGhQlI%$k6Pr%6w=Q+v48wv?)Ue_?BA&%$4}oy{&G+g)}ucql7C_d>GplIIIk_0bbCa^EmQrMwvw(~4`Ba+C0L)mnsn*SCa!aPSTgCmm$QHDGTzVEhqC{Ng`9U$48>6@w&r?z&fz#eC-Qz9>%)D;dXg?*3M5_ei{dzg?j9!pGduaXUv=cXb{pyPu47z(|Gr0!x+O4{$IsC79Djr#>DJB)>n>e6&YS586#xB!>-2k-l3ZuisU}?=+Axjlubsf-ID>RckF%V2rmIPpzG}h#m#dI&eP4{@Ov8SDSHTotE-*jMsO$dnit?<-g&m^0|8OMT<~54-e$z--e*NnjAD8DGKW?H)x1^L|e<dT1;;y{J_4oPRq}w-K<h&DR^M3H!Lb|%~%?*mT_kEgCS9ZQ8T|K#s{U29g|B%bPKYP?qH|olyRNg=HeoHgz^30>$*O-$WC+FD#@?YV2lkms4X+~Y%P>gg{AOE_(@Gq`sM;p$&MPa>W5sI%^9`gRlok_Yh)5_!dK$T-gUH7-%>&JQDbme-S?N@0(b;oh{ZO{HL4@g%VHD&+ZHCay%=XtNtkKdF2@m4JTUA(%v9=~jpE*I|2abmJaw-n&<V7s*mdNljLyhM3r-(tKUq)7J9|A=%+A6L+If15s@1Dr`$w+-j>baOQCw*)8Bm1bk8ew#<>V@BQXJC6PD@8!OVyxLEBBb(E4u}odcaU3&ASAF{OJhr7G*LiF!=~Cmm<Zlfw%=*~Xq|3`j^7%gg1IIbGg#BY?aGZ`iSyux|x6NxwaqRLFldgLI%>8z%!SN?rInHtyuCw!sbfa#oe~$NO*mB-Ksz2%0={>pMh?d-M+1?zdg3SI`cJXnX*oE_!ti$7^m?OstYPjFH-=xl{$JvGZ?cbZ{?HU(2j<X}{!FzaoZkw2H)TO##^Le4qS6Lrp$iJUE?}v9O9B0}|))&5@dMq14*#FW|)_eX$x;5VhuG5l0x)gMZ_5BxFpB6*9QY4V;9JZPFL$;0MxVrQB&tA!SYi=UlKFEc~VZ$D2MqR30nslZ3Tg)@>_R;=-yO6K5x%)A1blzti4^o*5oOfMy*27!yet24t^_&W%E0@ml{1&-8_1|>m`Z=zrRcX@Ibv1auWyYtQ^c(lc-#)9XNw>zG=ks*O4eobcQIl>N(uLzkz1~atqLO$%@n6mQ^JlF8UXk)jpYNJ<>%#)1%a>g^ul(5LFPEQyb;2*CORihfY5$!rmq>c<anfx~%5wa(_1OPSI>#BfkNnlgXLudeA%%1~X9^$RK{L3X+`SwJ>j!1hC9WrT4aYgVg0H7F8nOOnILA@%^L{vCOZ_)JZ~t%U!}0r$<?~u!|GevJ+HZOLxqEx=*XqaD{jP6Jy6$fY@0e!P)u^(392W(%Zfi-p{bC^=Kcy2=|4p~M-@<jd5$lV-(DhV$^AGZRm~?AV7sRi**LXgv`aCb)-b3|OZ_4%TJn^r(ZJ8(HT-(FPW7K)_PnHr$@0U%w<ZR*VseZitcXAxe|H_3NtOugmfA!bA4$<caT`&JPpYKZo(u{iEb>v}5{W@Zbqa@W~z408@oA=A2dN&8`Cq2oHboK8Vd|bBW=lxv7V$zidwK$IBtKAgm`3J85?c<~WrsvJ8S!GC9?zx<!-}UwCrK7uyy6UkO^YDqC)Tc+UJLJFc#%ZIjekw+~+V?Z-Th@~<edtfRrP5WCZt*I}aVF=_<Z;rTbY;Y6p0|$-IAzr3pE6jlI*;`?)w!N;3Q!z-_kJc_I(3}a!;2NO9@>g^>0zo-SHtpi{35QHPbzTUxHvj4%8^qkMqPcl?F{AD^*3L3P#sg+@%=@^yQxN9UGs^r%Qx#H{?DY#BQNs&e5GiTNuR!w&+B3XSwEIRx^gU>=bxM>@ISu8Sf@1r^Cxt@PFdG;z9(I3aFy$ED3D~-<poPvzcY;W$1~VJJe222&sIE7Iu>L9IiF~p*fV!wd_J{Non=4pxZ3W7^>!NR>a2}Fl7DmTpM+@ArT05Yx42K{ahMRs`m5>`$D+?a*7_!0(c@U1Nw<$)NO5fGmswA8B3)jyo^)A1Uq(4_ogY?^Zk=_2^I9HnC%^C0d3{n3<3D>Z>H0cHtyGKSE5%7ySKr|Cy<>A+mp^YKy;mm3(bvPb{~+BqC6;yly5^nD{<TW+x@&$f+?T1___#Wn=M(5km4A4@JvqX8?Q1!Hb}HBT3D-w?8tHOoHpgGE1LL77=f!%@9*Fzj2sifcSmZ3>Qd}3jojLFMW_(^W!1^RNZY%jkoG`B&qqdT635etPiEY!2x;)*T;;6qJG5Je}zNWlNt2kU=0$HD9F|QkatsJLSNuKvwo<^K4TS&j^$LEFXG_3Qxk*)*=k}frV#`?_c&7^m0&*$%d=yLlne0}$kvHvqj*XJ?of}y93x-I$yugB7tvmUgPbZdh)e7`>q>o@3@W(9fvnbI8NB$WN*2T*)luY0GBy7EgQ(v_XXGmX0aYl;0gk3416ZL2f+eyZ<M*0WoXu0HVN`E%UE(?;ELxH!+}EsJt|-+G+4Kv&+Mzdt&_<KbyE>9bwwe3V^AV*KwRT`g0C=YjKQu-=|bx->hJuXka450jqCx~=Fn+`l*{8FjUBIImmw<GEQ(9oEb7^C)#&4U=wjU(M^TpMqHTd$WoBUWM~```nl3v7n`-E5&?ho>ULq;&CO{Xa5Sxw0@9s8l@O@xyj;8+HX&wXZ;yP{;j?Fy0A8u`}La<Ws0MZPw07ZT0nOWAYGX>l+Q1<UL5I4PmWWk4WEyxcrJAN<3@^`*@Dj(J+JCTx^iL@&D)mjx!iBg=?&!ndKc-^i?8^3j<d}A@t1sDR!V6`T@GzRec495z__i>{w<f7=UZLBev|7jH^HQ<bGuU<`||<lw=~BewaGj`&wRa};$B%}o}W_#Nmu4J<#AQTi{qr$C0+fx5wBY^*0S!sa~<{HVGG5PO5Vr(7Dl?d=NQkESMOtfn?}0*_8#(A^z~luDAKK)uAAr2C^z;m{?I&srjC!KxN}a@@l|i&{w|>m>B{1h=Icw$uWLy!d4cEo=aX?gy+OMAA%)`D228^Jei-R;wh!%ROZx^fMqSFNP2<7R4bKPE2CNURMS9+RsEk@eae^zde^MpZojggGRA<s{`u<b`SCfDHNUBG6jKOuYIqAy1HJPU4VmY>w^nA^EJan7Rb>{9}Mt->evb?Ow<Iu~Sbh+;%_V1uyPgz&%mgMvFY&q1E6Mm9^=lMtP*YAgL<2bRM2tr?p?7w^sucMY^@%$4poc$-gqWYCmxUb1=N4i|<3(tFNuCkuJU@`e^yhZ1=t=*Gkqb{{BO>wNc?)5s%=r8Hd{h;gq>Ivu(Zx&MCd!DrarG)p`&nHM%-RtrBuJ`2^#{R*P{JbKw1J*@uq+25+c--Edfa|sE0@}WC6+W+9MIe5fLb|O2>6Vo<aQ+@8-P${z$9dKl_V=nvx;%G3pGSuR@jPTrD8(7Oj>q$XBwRNK%;n?0kmup6t9V|LC(kB-Tu1Ejxc`zJNSDs>{fJz>55{xmEUK^3dtU$O&+$}8(iPvo`TW(N*U3GC>2LQBy#Dl@gZsorq^nCu@_2K?b0m97(xsz2dHwtv_pP?8Q|a$FPdLt2+?VM()-x7;eW;!#UD`d1*Be1`iAG(yKAh*<YHi_Pk#zN|-^}x&oI9De-?fU5OPNg=|I<lVwzcHEPUo=B@eiOl7wvrhR>t!#$+rW=eR!XBeVi-1duyni{+-9+OO?m16x4_Ga>cm*y9aUK9ZkAg`wHpy4S%t};?hq;dE{55+j3lyx57|kd|AIPC?$p&<5-X5xre%PH2Gt_A^HEr^M;x-hWs<0n4g15WhW5gyq5kd$@^LPhje8{etyocU)P|^@lW}Dx%4CVr9PQVh<Qo!ug`s{*?}6`C%!a4ms4|td<@6YX4x9g<EP>j!jOXe++)r<jOVQ(RDbn5eEv@Qh2vY(XBl<7J`dRMlWuL-kk(`J@(P(oU5bCk>r8(O>(a~Fgig)P{?O$IkInu{;ymi>Z6jVc7Fu@7s9V1Oi`T=J)vVhVg%bWf(7gZEj8HzlEzEJC+kP$2`o>EpfB9UlIX-mj(0lxz>(Wi^hpY1`{+%l3IJ!Rmrun{G{zjqrzVEr;zYiWU>ekmOybfP`jCETi>9&W1&Ep~BJ;!PF#T*B^@+H9>$7}oo^4~GsJWhhjhtd9=)QjiI;RRSvNFZHbKUnqWHd5C`gr4_#op9Jc&8RCQ{8;byGu9QB#XN4a__*lrJF;spCA@OQ?C*4%bp5?XUY*LR<%D-Vxt_sR%-f$?-&@)Id@N|z3hL`@1@rSIHJWt&d8raSiPzyl(^e8<{i#HHVm`b;y1b~V`TkBCwTkpZ4Y^MJeVlX62;+Fjd!D1~7!T^^Kk%HPL4<L9N-ZN#8FhUe%Kf8QcOM&J9JkhQAEz31eSGG{SErM%KE-)A)iu+oD_0tu^Fr6pue`j__48Eq@!&XFX`C1Hfa2<A(rrtgoBi#JzauQi_k-%$vqy}&K5nHE*ICaw|DExC$@7P9`Qa#^kN;$|ZjFs3Y;}moiT9tpA7Y-6uG(Ajb9?={Zp@T*gqcA+A1bM=`<@`(GHwVz&(z;z`aUP!7CnTY5BoXrbMhST^%Q?sFzfnrZ?CJYce~2Zfu~e8=~CYfJg$x%g)VKN{qXcpt}}EDkGJfqr0ef<?fQF3_W;tR7GpTC{v6)2oa5kqu3cYmWZxuR^?O17cK!WMkjqB$uQ`@<+Y8(WWm!qr-_I%|ai29do^+{KJijl{_owwI_Q(5QMc4hCMe%Xm&*Lfr>s9~JtjAoYyvm}YSkHKDqH$Gu(Jhldbp1KJG#l@6-i;$&f3G3?yW+Ywi*>w@uz2iGGwS+#2US0gQ7NorUQ%2OvK}EvQ(nBEvJ}oqG3xsJCR<&Z^XBv-U4LJr)KQUlShR6`+UMfEdHCdL<2X^{wqkyp$2#r@^Twz5Dy|3b(el10(RF+ekoUeRd`q-({M&mvvwr&y`@7BN@p&c_>!o+>kM9KJ_toHEcr%?BrOxnqR|@MoukxfTlW+5Q*2iIZEz<SpZ)%(MxKC+9x;kV%?+1O|n>~`_=-(Aw!~L&&@Mh!rXwld0(Dm^wIqL5bPHr}yM|tm$ELT{^cL;g!gR)+bE)BfP_ahmDai92!<5x=L`6L(XPqoVy((zq{y4#8OkJD1prBX+@uNw&*KXni3dEYa9D8l|@GdWJO4<DC(k8u6HM!IG9H6DlEhj89hhpndbMZaGwQi^n`?KM8{^!s<{c3&&&T~=@$|GA{+y?;FXlE;sKEa|p^aXhY`-{LxBp0GdOw@Ui?<yUAMVW&UL>sZN^^}aEDzU$u)MEyXz{@zdxuyfwrd!*~{{pBUEO}hSm-yYkI^LjsL9q-L;`g`q&e>gtohrIFcU2(hde38QM;ry*ldfq&v*9l$!K0%3VeAKAx?-SL;+Z-pyn{|8-VAaPbbp3k(`xQryZ_n6nJdYH;PPMR&bbNP_*YCuVr0d^TsG(Ol{@7Zi>)(6W7I<SF<;gm})3ECE#<3<GCwedYm%om28%(;qZHM`ICB@i`<6j!Ni2HR+wHe2QO@AL6aE^3)gIRpu6-~#udTTR|H$`9X6)3yIIL<96E$lDV-C-Ojvg;PS-)u;_{vKa>RXWwE>*L&VtS86$=)c2wykz};2fBLaGWVs|8Dk|~e_yZY_wOGANmoJ#^Z3{2|A|L-Q=GA%xXxen=f<=5n8x{rnyeT2jdaEBE}y?oyRshemi6=x{C(G7Yx%wKy88R*ytw7b<8Tz-i?xc}XUuDPu^8+8Ds(@pe|Km7^&RUTjbluCYhK{>?d_H^#yYKQud@H5LF}LWfRC>&KkL^wl5Vwi<@3eqE$eerIL?{(JP-Vd?=3IgBVFCpiSL8P$Cz}zU;CFSi5SnZ6#r2@9-p1kc)m)SO}cbzGRN83AM@Bb)^Qz|o)^UU`4nrc)AmDe_V4FN?+2^{yYqKYQ<7QtYjMC>r`5e+vX7tX>)!n#Py1$96IUo<UrA-9F~bd?_G+T`Pse}%w0B(N|JA3xO`CfEe?RRl;UGyRg_Qx82X7~=t*}nOj^Mt+x(MqI>;e82wkZni0ItO>D9j016ub*^bp|?tcS6h#z|P<$;Zq*DiXvVY`1HWG9SpT=SOoYLcmZrz0$38f3}X8NyMT8`?2d*U9g))s`J7OX#_I@k6;=!A0^UkkBVp}<GPqUPNMU1v6TlY<n=5PuFbv!k+qeTqfHy)eAD}z<T;vJ?`hbr`%n`s4@J8^Fk;@(N=E5fo+m0~QZbjc#Y*Pn4yP$6u#BGJ1W%MT_?jrOShW_;&6Ohvf`Fv21#&>Avq_Dlf-QbUe-52%*_$&B6ZORsw06Yx-T-Y;VPk}k$Hf*y8cnJJHay<m@0e^;EzX2bDCm`k_;BVmf;qxnU?LoX}@X5iphYYoAxC3Yd-;3=Y0q=u9LG0(iXW&l}`>-L$VdQ*>d=F8N#^Zz?6qX8115Xl`ENnk87TjOhH^RCDyMgx+)>l|(U>ER%*d`u006ZDF4gll9`yy9A-~sUNh&ce*4?Gz@vB(vVczxm11=|iV)b5YI{jp6PdQL;%X^5MIo@3EpEaLV-Z(Y#8o}(Lb9zebWs7K?+#F#!SECYBRJX6?3VJCp+z-_{&2-^Uh1inz%9$|sNP2gv-O%^Z~{33E)0A_*jL9PS93*Z|NGZuIN{33kLAy*dSZNTq(y&4_^o(0c<Zzk{}_zA>Y2;2i6h}@Ha8^8~shFD-0_*7xrgv|nO1)nKwi?A8M&EUI*O&7KcI1PNBu<gQvfjhvrVVixx{oq@WYcFsg_;%!q0qzCgg_!$+G2mO^vl+SeA>MZQ?7+7B4Ylt^-@CERRP?+ReQ!nFndo^l`rC}S^U&K4^sncbhMaqmZ!hZ6__xABg-r%70pBPrURX5nF!%yt<Af~-P6Xd6EJ@gU;34o(Y_kfu20R|Q5`nA0laMO~m<YZcG1mZ7z~kX_7`av<UJ`r`VcRu^+83bj1=!|W^t=RpFG1Xm==m`EJB+wH(c2;PujiPEoQcSnh<Y?WM%Xe3?GrG@IpE`kg$oM;t_45tpgj(dq*K5&@N{7(g?$e^1HKH~L;_XtaO8>tMuMM2uG7FM@KcDX0#Ad7!)GmWMIzow_?*GEs-gDd==(Uf8H1kZpzk?|J03l+MSp7%Hyyp5LH~M=G~|pzz9`hA@u9+I3mXkw48BrWoUreJ3E=aE4HLE$I2?SPup`10;6d=&*k&~_0z3}6l7Xwik094kU^4hp#EbwQ1&@PI0&=ZJyd&^Ah;1Vbwa-W2^RdlP^t>2-FGk#z=s5xXB_QrP^mY*a>p6xaXEO37qaKYn5!b(_!de1bgU=N<U)UnxV(`Yo8VYL;^afujEKJx;;4JW_*rpY*1^9gA3I(<T4@0gwz)<k!h}i--2Yfz!79&?H#0!JZENt7tP`idrfK9<$V!OG(`QVEXdm%6kd?sRh8*+FfXDIT8q8^P~B<=Q8lBxo$f!7dLQ&=sa8~AWxR$)_sf#B1Hg$SDmRKTla8yDaR@S4cw3UmPvL9VGlSMVu_IRZEpye53ykjn+}Lg1rd+YyG^hokS|*v5jMtD)~|h+6|ayP-cf#GQ`b6!fp>2t-a-<a0$m8m}$PU6?1Z9(aJTA;KmCCxO=yru~<`^?_dC!NR5q8x0%@?v8CdfDOQhAlERU2lzDP8U-8%ULP?V07rojfzKr5@<6<4@EM718yIS@gTCuvo7(8P9{R3_xB=*S68f8jxWVXcB>LBLcp>L7<Qs;1G(JOEZ(-j8{lJF`^A$E2*a^I+upnVQfRn)o3F{ziJg_5pZ*0>Z*bdwmx!MBTgLgo#Ho&&vJrJ`Uuno8`d^#ald&KJipN`nJouT%g=({JjnSq}D(6=Ar4n@zM&|fFS9faOGqJKTdWaMm%d~H#W#>WZkDr^F<Klngl+Ox1;z-Hjuqp&K%N&+i_I}0l=>}z0A@UGZK29^f*L9RwX8N4`h6$3T`FNv6?fyKam;L{AbWW*~DpQ6~dw4wI0=({Yo8Hb+xqwoHRI}klLLx0T>*BQMPMgMw^ipbdr`5K`fjaL>{Mpz|adGHFtoFwg4IAaO$f|B-tQIhfli+~prmQPq=pafn9+mr$p0Cz$zM_?)Ne8}YhbOg_jm<50i;7;%<fn22!FCTm)Y+JxkdqMPF5ZhEn&*jl~dBm-No=c#=5{O#}y-Da_&rt+99g)uw^=Q1T_@Sb(za_@f;2OS@m}~gJ!0q^3!xZqH!gdKu1Re!X1pgUm2mcxTBk&#gM{sB4*XnSFX}l7!B6ub63c#}96~I5CN3HfxFpb{>J^;T5egv2Tegu3ca2NPeU^FlhJR1Ba@MrLw;0_LqAHg-#xCN;7X@P0n16T>%1H3x00(f<B38?ic;ct!KK=1d!Z-8$C9s%D3z7(kUYRB<Q0qz1{g5M*7(cqEb*MK*{uYrF7YW;t~-x{xsePRKx3|<%L0bUopDzG|uRq)ReqXhmL`{OE5>;EcD<7<JNz}JE=0WJmqL)bsUia9X;1+L*w;2LHd_+9+1;VtkQ;<s+XY6H81Yv=~9;nxOU6Mt*?R$`tdaI3J3z$kDH$AW7(+rY=*Zw(iK7ZR}w3(E)051tR)5m+4D5xfep8u%L#>$R{~z(2uXfqwwL2mb(G&VjL%1M|X&l^^&DTr-Uq2Yvw8Oykvn<xtZd!LJLu4g3-Og2ca_2i^wXj^DNc&x5}d_PelL;0y3y@Y`cxE_gbA`yTihJQv&E0bU1xjNdK*?|^@g-?jrUfcF!<4G>lz=mkCyfBOUbfwvIWQdnzYgM|$e)&|%byfu8<0Gokp*c@ET(^QxzupzjX_Z#HYus67ttCz4Lz`o!C!ulY;hCRWxdi_wdhW)|o32T5JHEay7)$EP_G;9Li0=y-#8Mr5Et_N%Y?vGppf!}}+LCpccKHvk;qZhC#cpL1i!N6YN^-*&_pda`k^xhii4c-*nHv~2V?}dDQf!~1pVf+5TKH%QS*96!A+zb1nKCm8mL;T(Vyczx;jD0c4aQp@#cYoyTi+cK_=BB8(DQfM7+Wb(LA8OKgh8WYQg)IlJ06&Mn&jK^RHw)V$>=N(?@D0K?;`fdCP3Pa?Zw=RjYkAfPTLxSOuH`+0oEn}4*YX?}b_I9}{IW0=HE4JYT&wp4YSu6lJY3jH^r+!#aIMyL=tIK@@D1P_f!~2IL(Sp9mEdQQ>m2Y5_!ZQA8K{DvMvp6iYrwZ)U;O|)4!#^UX8=!tUqbI%AAa2&@|Dg1KmD)1{`;Tyj7&29kH7wNOY>(0#x3uQSa}~6_;o9&t%1d2I3GQjc&fc+lKu-j>uf^'

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
