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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_001.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_001.stl', 'source_sha256': 'cdfbf0d2b36989f5471bb72ca9dbb19114561f57e7bc2e34e67a1864e039ad2a', 'input_faces': 686, 'input_vertices': 430, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.38076743483543396, -0.15482598543167114, -0.1794029176235199], [-0.08984004706144333, 0.30088338255882263, 0.11555789411067963]]}
GEOMETRY_BASE85 = 'c$}qt33N^8*Zv7H53PCT5*jl#E9#hQ2r;E3$PJN75o(@$Of{$GdALNyTp>shPRuh&QPgl-l+LK3TJ$^bexCEYC;#>T*80}>S?gK*xzE{mpZ9(Deur~zmf-f8{R?XNS5{l|DzV??ikha7TPvuI>OX8mbie+?tH%r->!-ady836^MIE~b1^4vRMrq>%Bl{2UH!Sc2S776)27y&wfl)(-jTjaY6Fy{EWPhc%ju<q&zoic!5HYmB^|@l5+BK`XYFDc2n&|pp{>y1K!9A(Z^&_e+f2>GU*1VcMrKx2-fAkdHsImT_=(U%K?z&SF{^tXB$n__C4l3Q-`PH|g4?LDCy6au>Hy%F~-H7&=INFFN;_ucTK@SPsr>tH$;ehyOy@)tPyP0zRa7)C$Xu>}+Y`6Hg`aW6wm+gW7{htrW_4F}^#Q*oLY|qDWVu#%of4$@u=x=k$ea#WSN_^MGIK;15{+QUUjSpqeU!9VE>6_l5ojYO?XHaWtr&-Dnf76@^|ES{$qAv=R_<G#u@DEMhF8aVDNz%?Ek)rF_!zGS(<sXT!w}-A7^N))E(T_9eM$iFikLlk~?rU7@2mkQxDPj*M!aq+C^wJ$=eDnw9M0Zd62yx1tk^XA0>th`1w}$_w)6!1Oodf;d+zk5r?NXibT?J|*PX87Ar9Fv@Wt_cH72tnminQM-y9nb@vNUx6ip#}+Ncw*9?^PK3ond>Wot1JTzl91y&wNJW=o9)O{!KsVGwN;;yDpQ&F`j7j--9}Q`Iq>+!(U#L&tWNh<a&##GXBQHC!%Zm!g#qp^R(#h?vLOfk|yJ0&dnzM)w<k+|DG*hi9ToIKIzw&*PzenE%j;Ecq{Gk9J<0d2hslT)?(boC&AzK@fz{J9Vl^JNA|*hM=bKbq?)wHyqXCA91Wzdv{GXwzByy_HD`bIMqcsP^-a+C<=H5@_UB${Pr`cWVfjQia>hv<_u}Qy&z6+-Xt}SVUnLho&;53-w5Qx*#ED-B{fBD1#NK)?{@TI0&`%GF75_|E;GZ@J`kGaeFLT@t(e?b((BEynP={rc(BEAX;XkGSV!1wL!d}d~G0>a+6z6QGD{2&UzsVTqX9G|_b%#T*{z%%dxA<86%}p`TS6*K#cHn)9Z(jZcdba8wvB8Hj>Sn{m=wB-IVNuY>25po08=}zPoFUN1tyw1R|D>Df+RZM|>kpD~FgAT9?Q#Fs0pno4!MrYU7VRwF9{!_dOMlIE(-Eh~hw$GwPwGMUX2&?(YXW~yB<AS{Q!u|y)PbH<R@$k>_Cfp^rJ&cHg>mZ@B>q~Cyog`$G1@aOi{wSymK*-7znv-mg{vh>9>?W?9#deG*uXUC?kv!Y+?4&ooL>NXhlf`s{-d*)FVEgZe#5`N>hw1XZH3<IHuTPQQ0M8bM0fW;1-;fite@XJ!}yrTpcfeRHO8ao9?|zDLO(tlacZWc4)bh>?)f(!^X7>7yCT+#Zf<-J<N5w%jPu=D@E?0p))RBr8}WD7n+$#0b-Az6bAj~N`*%C&+%L4`P8oC~^C_7}X4hv4(%=4#;a_wL>SW`f-Qr&?AN*aHG4Dn;mirouzPTcwH<f{Z`fs}s|A^>D*aGZFscl6!bMA#cxhVGiiG34LhuaXRe#&Oi8+H<Z*Uy`v&uT99V-)%GYpL@|3!uMxzEx~U^iCPih?&sCD~P{&V?Nrm-hl2uDgphNj{DB;4Smg@l6TEjOyZbLL!f^+SK=FKA0p1a`e=W^Tp533*(zy|aiJdkXEfd^dh(p@8T7zQJhv<pe|=MF=$EcwUHvCzhx98ZAL6I&MLQSX5Px^(*WZZW`E<m|>Op_+K7#IFd9l=4x7wrS`pyT?+y5r{GJ1QrN&J$xpeG#>T_3%5tBmtIr$slK+(13FEG+HOyR3)*j=AtZepvcte!dQR<UOnd<;qBWZ_F2nlXnZ+-(jA_H+IcU7yrd)zYzbwV^_<4f?Gf@7qv?KM!lLUpF`u)#GV_mLHc!h=yZu+Wis^D%ce^E7H^St)M!x*dgL;U!}9yl>a(Yo2K`pCrJ`%bgAbK{;P1<#7rwGU^r|^Vs?YB7r=cgMA<obS-NcqX2K~jH`SLk9ZHUBQwFP>)Yzr~}d$m!YU3;1_PWo!mOYD~GM&$s}jZ!bMu6_Gl)*<h-GVu3y3==&ye4ezYW)A4br^$KC{mR6;_2$?miF2(w&u95jr+Jb^*Ybqo99(c9>iSp$^m*6B-@A23lH{Sz4$;jA=fz+DGhWW8M#MJw58H|O+ppvNdusvioBRs<_p`Uq6GlMq*W$3$*~K`~jlL}rXUAfkJMY)tl0i?}fb(BmPn=KJ)kmC$S0#?oD+TN5g}Tts1>)SfA{6Jofi<A74mcup8Qn?FamJ;>&>wY|{n%{wP}-wSe+T#V)DT_!qP&conMH$se&`pXXDu{FY`ZrXMXz)N=lIk6l2A9#MK`AHLVI%TLtbtlgZ|(zv}brZS<keGJ1;u(qVLQ3wNrO@3pJ6)KP0}<V=Lku?;+!F)_RG3-n&tB-Mt6TOX26FzvhjVh+pmj&dskk%lPQpm!f-uf+fE9X*n5Zz1w8ODKTGkBkm5KOX`ie=*+vjaQ^kuj^|-$&wwnF7qfoo2KoN?O)ld8h0))OnGT8H&lM4W?3Tl*^OmwdoAvX-f3YF{M$3Pa<$gzhy&&I9{8V&z$sZ&ydgv|D_1<sczj(Ry%NTwL{w>F+ik^}#<KsTHQ*>AUgQA-=_esCp6XN0TkLOHd*dS@Y+Z!vo7Wxj(onxa>&(uB75+sfmlYn#jfLZX5D<b{Uf6XQRb&Z(>z11AVpA#$RbnTmQ8RBb?qon@5KaE8@f6IGR`pdd<-|7$l&Vw;-rDEjy$qeZLeLy<S0jD(V|6zI2uLWZzj`sc&*?+u&S>b=o1HIc%vfp|-{(WBj&-{+(me9I#UvvClqU#s(N`E~szQFjuc_g}LeGiPY-#{6Ece^yvwM*ex$EF-by%jzqx@+f8a$isF@-m+88OL$ogdoIUnkwU?$L~a(GL<Bbr)(>!H}940Xiw8*@z*ydOPzRcFGKt<r-<&Iyj%SBMe{}X{#yQ+#2M3A>fD<=4ef6pF1l+>e$@H&3Ak_bp>ht;^WT#F&3k67=w_Q-(thusJMkXkPEEw=TU&JVKq(n#GpY*w-<+2C-t5^>KiA(A-TmB+aYzio^W~GQ(6io<dFR&rWgLuQFV9JP?l;GJ+x<&CKXw289Ohp;>970Sic$|+|9hglZfC|g96B!J;M(Ga|K-FC<L~NxLUiwvxfsuUNq8?pUCTCG&U2o(Q?MUBN`(G2i>%Kk^JTP1$mrjFsnoOQ+&0{I<}tiyiK{2^T~F7corV9#xc!<5&jCTJ5$Ekg@i#WikbZf4EfC#Y*I35WJ#Yu+@2M$>Unoe<uV#nhQvdpqn$Sl@%X!-6?I`u^>0KG|kL{B<M!(Fc!`A`u-@8F{^Gq*UpFOGhMEA^pfjap)9qUY5R`^f2iRXcAw?x;9J~%7(d>rmOV+88<&ot4^Qfn~&&0=L9dHNg^-P7To=&ppP*k@ntMw~lWasFHO9OtZ0zZBg)c;RtrXM-Q*JmsD`M0CA)0LI6Eh_v7PQE%M$&gf&#b{Y>uL^lpZW~fhZL=*TYSCw^DkE$*C^|Y)5e=}OnyV~^jcyDp98uS{S#orToRh|nyud1T`3sSJ2xQ|NRdQX%W-PIwx)VbEXIo7cSB}Mm+YJ~OVS!J0Q?hyshuZ;oXZ$9|tfKxZ;JjHzZ+Qj<P^OrNyo^=M^JG_1@?f0JjQFJZQU*@&xK7;kP%lGiluH!vU#bBvV<H=3Y-3JRChyDcT)|7O_+13~5go^7?pY@Xw=jbUsKcv@|@p1o_0DatgtS9j)$ouYf&}+8Eb5xJavW~g-8i;@3x}4+P8@fpx&;AI}U2lGq{(AhMAzx+(_^&-HakOspWqtEJ)J69+tc7uliI(_!^Cs|r9fIe{dCyS~GfO}pTN=-A3*)iBM`jmY9}$}BY`?en+tcFTa)Z=^G2<INZ~gd}=&m>q_St&5aUN^<i|EGr_85mzxsx%!9w5%$vZ8xN*O&gfM&A+L<6VS(VbyndulCMG#F=rI?TL~2o|w6!>-oybJThWkGCrQ8lMw%}A~HViyT#?)>rNjI{gZgSSN$wX>cm}bDD+%w#NUieM*OakxbLlVc&|DnJKk5-3xmJCzyA=1`W)8-{tpIXpZ%-|*4qbdp+8T>d2e7AsW<O^=vwYEc#pFvi_9a}s2b3ZS3q9k3-592dezc6r}g|C>)3&+@Sivf?^7o9z&Ye>S=_h7KU}ZM%ehNmT1<5F&UKut@7<Ag(%UjS;`F#JaXdQ?NWWZdemW)kxC>b4pPs{eg{1qU8_{o253GNWei!<>iddiDRFU;f8?*#*Hjl%5hl@p|zefK#@ZX(|Iyo7P{dB`5_|IvD`Lebo>bBV!__v;o_a-YN(BA=rMAy4^#JMyq3H!y8PZ4M1Nt~lTYa!<!S43av$)ypeKvukWS>7J;uRIss`%WmvAx9hN-=*w!=0&^uq3Gt>BFM|`$C&T`)Pnz`z!P%cupC(DLu!cbebrn1U56@Q9V-_ox@Y8lS%36{8}M94-FS8v`^%nnINu&9jP|b?j=YDzMBP3tD7veDXRHI8^5S{$We&u-6NGhOMrYYyJfHg`&Yjg*XR6M``R%3#|AK3g_vS}sefA!Dc~au98hA?PSC&h7&Km!n=-T5KC#An#5959R-J_zLpWMazU+@DwANAY<|AP2EK%cMz^RdGc(T&-kNu3xKvg3Vi%6$0q9O7Ow9C`UA7JB1KJg?To^X7%=h?6=R&rP>`%Q@fGbTagg)sXk{eQ};VIbL+#dsW8YSbiD#jT?aYwP)dXp!NQ!w;mDDn-#<RzOS<5eN5+%F+P)A$m7*EXy^8>@V~Vj^Kn9FoF8u0LVL0;z;kh}kMMlgI{^N>%46TTaEAGPdqVWfdGQ=t?Q@yeuDTCJH-345=iDJh<-VS7Y4Gne4*Olvp)wBIhGfxQL02SS#y9(9zjIYig#V>E$jgyD(qHfQ^PpEBg8jYVA)Kr08n`c?BlJ2|Fi(q)7F`cIEcI{ni<RGn%vK{2r^QyRhbaL#2R0oDJ<Bcp&hhe&tOKr7{Y5uD^)RoSHAQ_kh`@a-<98$LAcy+w=!PD93%^g4S%!06vkuTdUy9#X)>lH_U$n$HgyzBdYGF9eljU3BzGaG@75^U>VI4cx7<$#13mL}eD0J6~1?Od)*R7NGc)qGFy0=kxId|!!4`N@=Q3CDp-od##Z5r0|tN9UUop}cH^p@-wI(0K|62^h^!n0C?emq>xW3J^D@f_Fb)p7aWgob!tUeOi%;~uZ*#_55mt9#e*{vrB?=-QxYykDAXVx3v~E&Qt-fPb}K(l1xaIq2Je<$I63sOOkf(EU1~e(o;EeBU@tbnoeWI9DHC3jffFxbKnnSg(F;wA-n>Dum#CKA{5gn-YomCw`Fn(Q5R?bJj0?5vR*>yw|!^0sDThJ{X7VN!YL5#W8LbLykM^#|)Su`Sq6VAiC-9i~Vu$``90!W<mQ)M@wF`Q=OTw*Z95GlM~~XI3DZIS^Tc47hfsk@4eO<<B%-{df$;UFZ2hu@t!p>UUXNMDOfj}Oq04Y+bn?p_+_W1Jr#-`k$%2%i|+0je@@zex^1dcH$I*t_2~^gE${oie^KA`@RI1<-%aXTL_3M&DwMLzshjz8iN6usLH14Wy+!gnjr&}7%$K4D-dCKQjo(=}^@6T_FZ0Md{{zuIU0pJdjFr1nox0vTzr@#O;rC|`bu%hW=8?|&G~X|T`%W(*<KVis4C~d<^@#U<TiK7yI(-g{zHt$LzmIq->zj9d8h&T^FcRb8T`9U=s3gYWWFOJp*JqzW-fyNlb(ely+M|VMLw~57*W;!AdQ5%Osk@gCx-9;BL;PI;b$whx83!$W>dp-M4^hb1=z3o}b=R8L65n*4!+zx71;5{{nSpb~kRMH_uJ3(U+OH4WaLlP2r<aKC9b4mQ27N%W3usTfjQXmX&<mZ&5XY0#5B)0JDZ_o;4_AwBY}1jC%=G`djnsoyzd^E7H$F>~_M1O-%Ak9HxgdElvu8J*x_)7~#CN4=2Qv7V>ysw&hho1o?fbrW7UL6qX_r%XdHql)k-K+i@Q?dR#>c&F><*`Hv=}Vo;EuYNLHC9{#rRAwvN=Qi`NgH3?j`yjr|#aLavAe<s?@EAy4iEQ+}C_HSI(d2#P%}3UB5rZI`cu><xbr@aEsj6Y*l52=#LtU?%9=y_mc$|?sMwyItl6G&-Zc$b#v$oJf|#oeeKkZ?N!8IZ?zh~7uBn9#5r#IoSoR$ZN2cjSg&e-f;x!|Kpf8~tQ%DxV}I%g-Ic$U<jd^zE!Ly={N-F=uMZxs54LWv4=%0`8g;GrU1^VZ@q*n>-Cj35TsMr6{iv7tA8}qS>VL$k+v}&7>!+>T>!%im_0w(ZTtD@lSU+{@dcmBit8>eeoVvY!np{6!w%#`i^YqD)1gCDV!)~s_o>HL_&vj`X>Y+^ASf_42&3RGcY-%`P+8GuE-CTs<5hh3ObL#Hx&AyTLEZmQC6m?I5ILW)#WF*dA)U_@7@Lsx88T>9YzCQND9v+#e?!{lrIn_hm)26KK*V?VWv2Sg`du7j&Qy7QsFK|Alu8rC+_28X17W;Rz3TXe)^62l;fybP>r}h}hi)-Or(Y-o!*VQD<_jM;sr><|Aj`>)o6xMUwpZlzFt5LF3H>T=n&)I^=x2-3?#5s0A;RL6y&HoDVqfg+y9Cc6X9L(!1crW)Kz1Cf6zo+$6=rI9kPsbIqujvQw9Czx*^Iyc@IGhdhj=GtxALd=!s#K?LT&^hXcYl-}>p6A3%mc}zp7?K42K_}|tPeMHpe_e9{-+5N-}U;*4yUeV3dZ<ckHh@3{r@e3{UzYpdZ(_(e=7B<-CTv|j-&tLIk>DF`(U<&6sK;Vt4;e{ol5_CQzgFVVe|b?-9B%-J=S?UIKy8<Hr%35-|W&fg&bNzEh@tCr;tii|7`pJ|5M25I{%|Tg{;@0-v9MaAvdb2W+9nKv|wv{EF3429okL{M~LIps{3hLpamCE&d;ZPV4(`(a%e3qG$N`vw2v$_CmK1l4=vOsnme?{7OD|-9a<|3O^9j^t%ijFqKQMRXrU|-;Lyrg$U~HMXvHmLCGt2lKMRjFAge>mXW^{|sB5;C&B6-}P}gkjjm3W^)HPevEc?3#sB5<Nj)m76@Vi4RWg$1AuGv~)3t5QV4y`)#SB}?|w%q#OmlkFbt2Jm#EzDN)gjh^%vV}<&MiXPH&9pGj!W3cxwW${7TbM(Pr?$*OyoK$=5^5`0r(Y8uYKg2>yKYmdsoITW?e1jFDs8ugO%}EiN2q<kI{Juc!TPMrTC(e^Ikm>DiyA~LYGqj)cAW%JE5qFT5yh#!Wv=bKKW0s2V=gt~4K<a|+>Si{&it!f1~Qk`nM0+i`B%lyH}A?(+sfQ6Bz9;%P33hAvCyHZ+>Ip0I5d^lal}Z6rgFE480XMbUK5B#4o&6mB$43IR9?>$Cmou~-3j8nL)*&!?BF$}HDd1C5-t6Fn#yZyqOC(yxqFXj?a)+SGZF7OG?lxbh)fPm<<(34r1><JyN86=p{cz7s{s!kn#x^y;$Mf>i2Z5FYf4LE|Ly#))S#{8XFI>ssZHl+JHHdDP2^`gzcZ-K;AcC(YpAW^XFI<Ks2$*EJHHpHUF2swzu!^&j-T!PUZ8e?pY8l6QG3quvd5>GAGA9hLwh`JEsbMtkH4+mWsdB8+1g*sshwY2E6EzL>%rC<ux9M~u{E7FX4jjo)o1?f`n0uT?2nyaTT?k(Yhf>8=T_xxF0ZY1XewvZcx|pjQ#p&}wP_Ab<!n8##X2;Vv;Dlb-l3_So#nOt4o&6k60e<gXewuCc<quyOJaY{5VofJT*$&J4S25ka;!f8K-_WUSbe@tq&ae|KHn$qI&!Q&|3m!c$g%od#1AOx$g%odm1y9|vHIMQ&>cBepDPpf9XYPdz7=9_mA04pJ49UOxGb>nxrKGaHfqzDr_IC$ho<sm5}O^G%F`9XbZ9D1kBBP{P37q~;*mpBdHRv~&7tjOyD#&a($X#Lv+xb^gxV?#Us*Ut9CT=hE!-rIIkamQo)I@4+OHPg^#h(cv_CBr^#jy3Tl>XAUOzxxv$b@#?+LFf?GFprHD4X7oGI<Jg%k@nhzAaBmxXi04QfX%oO0CRZHIQtQHS>(+EYgz{^QVcI_gkev$cYbI#kzeExV%*8#=T<G+!N7rdHEJI|~&ow4wc&wjFs-+OD+i$h(p^qpeA<(3IDe?c(t7!gxK&LoM{6ZBN^Uyghjx+NR_RrFmW1N)G=@jMsy_1EF|5Lh%BG;<;!`lPl!lb!GFD*Q0%(Hb43M<ZX!j9KQ<WC1`Vyf3Lw_rOiREp!m16xyTh1zeih|TtV@_Y3q<HD4v;GQ}WE@{<O`={mEZyur<jQYO=lGlb7K23gl{>r!jBJ&Lj^d?@2p_e5!>x7G}}zAfH7(gLWJF4D!i@;$K*pPP>(M8~Il9?X)|{x0BDNokKpGJe+nac{sV7P&|Tm7I_4DAKDq@eaL&$PA2b7-i!7Na=Smh2*nLzI>&W7`!<c(%5mMwzRe`IbF8<sZ&PT)$)}Lpb5QY*Y1@!@x6si-C)!%%oya@W)+X;v9zq*T9zt%9XRx1djwt><ZEZi_JW{+KZ7o0FoK-xCwj+5x+77hc{Cx9W@gB5ce!ev!%rS;xj&Tm-*oW~uy=a5TgLvOwwA~%~>h8#Icjmu4$IGq<#Up4t`}yieaW`!Uc?ic#@wpa8Sr|!dc4(t53?oK5w0Rb`5W}d=w=mwq2qNC0jkPeC7~#;qwD1)%m|CobF&3hUjSg*`g%~2*p)IhmiHM=L#KPwm1`u%$ZIXp3Vt_+iY+*eSMQx#l2^RVh9)~v3LSLevLtA8F1JRe-XBLJ!#(5aEK^BHP#%(aQAr?M$j6)2y;ryPRml4!H;rHxu9zd->tvwD=)P^#iJ)R?}se2A|^edWLe||TTwjX&v`rEuOKdYKh^)i>3M{O+gKcD!L+BoJjmRLY-1p8^%TRgP^?5ABnanvR;pG%0v)JC$OcAadd7R@%>`PxXWANy(7gNNEg=6NBph*~VayMWlp`^@FN<`J9OkNND&mqa}Kv4nkDOvLg23)zN6gvZfl#g`I_FQZ*gzKnbYZ5;Uu@>R57k*^|OLmN-NhI}3E7V>rEYiT!=uO(kiyNP@?`AXW2<SWUS({3Q&z`iN|sdY~1XJH^QSc4X0VJJTj<~3UzW?>XD*r5%#@C7l-p?zjy1o4GK8)9J)F~Xt6INCFaTBN4_R^D3gX}ghsOdCwwjl7(N3KlBSRwZv>p@xOVw3Wy!(Wfz?cs)Y#hP3aKHzaRPC|;emDtT4jyE>tGaoTd^%9bK8PM(AI9r7IHnP{_-XCl{VvuM75iu=*}lPjB5`_C&(;hAZ3lV>K+MVpU27kMGtlH`TR%Myy$q<xRPCb>@Ah+HRcN85(H9eF20@s9|_KcsC${vmlq+V{vSl9#3}NnVnDC`~9{gf=&M5%PCwvy#6{UVzr0ya0JYLh+)sS;&i$m!Qo?UV^*~?K|XU$OC9gkq3|m(v~9+B(FwWiCozl<jOW6SGFa2HS#93ZONOEw;~h|q75bwBJWPyjl4T~Z(28bZ}I`Ok>t^|{b?h~`;+&f4I}SE-b3@P1w9DGLkPvY5{h@G4JHp}e>xM2x2J7M-jd_ho>066ZDaB%3*i<b2*pDQ#k<h<B(GzkiiKK);*~9Qu+U8N%>~7E+S;0L?kHZ9w!G$>Yl_?RQSm~w#WdfXRXi7Me$6+>70*nYNAs--iu=)KCs#J7=37q`*J$%<zJH2mqAjfX)-J_!(7H6=TBmq%+REgWIX?C}sd#nTI^@dMC0Dk-=39Fex7TXL8`9R*eCxU5^=Rvm*I{n#y+HBCv>%Ww+f?)I9g4Rg6mL)4nq1kAny;1=?@Zf8^VOl^U1@ughtT$-?MdE?yf1Ayd0+BRXrstKA&({$A3!MHn>K=6*-*_le--ae+eP!ucg2HfJ8Hi5L2-KxQM?IlYt6ULC|-@WDS1<lZ#CLl<jPjod~28DfwV5ow;n1UKwDVzt)GgQq0OuL)?39((B{;9>$BoTX|rp-^;~g#%~!ktZ63|HFDU*lZGO$Sk0@S*wwUJIcN8y8Tb?|)y<et+ng6^0^2zs4JsWEo{sXB0_nR62Ji__Syw*nXpFfreZl6W%Z`MT3BnPu6YBkjU3q>#`q5'

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
