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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_002.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_002.stl', 'source_sha256': 'b2cc73a0ab738d814b644df906309304d7c782a699257e4ea0a176e461f71f00', 'input_faces': 1280, 'input_vertices': 690, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.05561736226081848, -0.045531898736953735, -0.1708139032125473], [0.19592511653900146, 0.31739020347595215, -0.0470673143863678]]}
GEOMETRY_BASE85 = 'c$}rZ2b2}X+P2*@1PKOEB!im_f&>YY*#k%pLyp2G2bCNJp+OKqavbuI2P6(T2n~V)l0gNJVL+0Kh++=-?WgOirgyRbwf^;euJx?@s_X6PuCDIgUDf9t-}r{9QfIN$Kl!Z1c?L``9cNimk6T%+VLb*7>C>&p;FA3YjEu1|xnBO!Ij2dh#_{c9tYOxuBHeoo?l!1M<v@|DJu4O|5h&8L|DYj*y7cSZe^B=x;_GyIZE%mUAKbgkfF9v?(F&DHmk5+CRwD3b;Q#WU4AO_IBRAFvhchkv1xah&!NZ5bVK<$!N!r1pC0*~7X#PPopV;Gh$Mq*)-YjkVvxDa&_S3M%7Pmd<()oz}7~b1Yr#f5R?KZxu`cpFLXf&U4Jn4P$!4@U9xySu2bHw(hci28KbW*bG=Y8b*P_JpnqIv7|*Zak%^m%=|d%j=49<jaYz3nHL-s$eAb-9afKP!KEESe8)sjjvklXaKdzvZ8+e(LQF?`^;A%5Jy4H__dXt@~qm-JitV2lu$`RCOb^H@&xgnd`0(X3VDg|4#*X`_Rsu``qoUe_bD7oK0_?P~)69>b~pk8+~0LvU;iQ%l@afzq2xOKZe)WH*jb1ez!jpDqnIv_mAlv?w?SBf(P9FJQwf!0QX@aw#5Pe{(}uleh|%v>NRoqlaeyd^}zut7yZXIy*_Rr;~BM|<Xsp2#|^DW_rB{h{ub$jPabrAO0iz<et-RFSA<V2<oZy;ovm(uS5bNEvA*v8eeJ;RXg-ww;!bz`P5<WAZPC2b^T#dj@uxIW-pSm|f83M}cq@A|e?J4QhAVGhXzlNh>2-fXPmNGMc&W9&Kc-L7{RwSXK2xTF?(cu&)IHI>RU?(!|4HpLyFTU9t;x~6^PtIQx1Vv}bKD_a{pTAPsr_qRBd*KGKPev?-_742)9d~uX8D=@Ozh_G&m*4xgz9HF<odwa?(Tl>jo2N{r~I8&_2(kq8l`-trQ4$UQ0^+~yb`l1AABj^f4+&k@lNCTi0j+7g7WsLmj3;lUhh9;65biy(%*m6>;5NJX+l4D){7YDs(9O}7jgf8*p+d3&Ao5!C!X39&4<3S)%`H58-9rEQ+kz6j^^!I4b}bDy)XT=+;OnJnzk*PPi)>$o$p5c%u>VMak-auZ!~Y08L=b62Xndmaq{=s9nISh3aN3Z@hbf+tM>mxmF>~IJ*o00cR#6T(9gml|M-|*k59_8csp0fKR%{UWPB2{tyeyDxWE5=P4AuWWbIG%_xIoQy8nr__S4T}?cMhIpLR#}O_#d;4-D1*YI}8^vL;9M*WPmb9~gg&aa*jO4+{tFiRMF-a;yDc!p~gj`at%C<fy*Pc=z`k+?d{Reaf%B{o9*9sJBni{$6i?e@w6Y<6O&uAJD^XPaTvT%?Ik8cK2^Tol|*hwAy}n<2}*5y*^Iue`Y@AOZOb(_G9L2+oO5?do+DY@XAK_cQY3s?BV*row|D?d}-zN@7?sl@^#(&$JrTF{#>@<5&bc|K5p;?K9qI1|G1uySKizIA92cO`fQjx4n^kgiRPU@|8Tdr|HaR|==xxm{mIe1Q?aT${!Vfm<(+i{Bld52y?^HrKB&Cjzv;dG=kLOG{IQ=qj?c|bj^@4VW%>fs-Thc4@qyo6A9(upJ<+^(y$m0GD!;ma&QDXm_v!KOet15ZUOyk4yZEG2YI~j!rq|C0EAvd{?I%Y2e_xMy{rf77ACPu*#P7@S`u7#QxQ6@i>ad94uj$#p{T<%<W|)8fruX(=KZ$XxG{paVG`;tG?24aRVMxU9-S8H_cPH&8<?l5d6EXgV*W+(x!KXAB;~#(1>+ug3yTEysw_VTs#q|395_}Q=P6gNN_lxQE`!~4nI={P0Bc!dL|BrZ{|JEOPyMpWW^WXFi&wuBaTRb0{jPm!#^twNGz1uuz>W%WBuj#$>t@<tF_US}-zs&a@@yz#};rPqShnP>AKBc;vPddFGDF4USaqf9CzcRg^Uj=7rze#!KZ>HDtH)~V6!)hE#sox#_F}<GO+Gp@d%Io>9>Gk>AX`WC%{@xp|XZ~Y)J^yi@#yfXiujgZ?*Yh#^EPhXU)gPW$!5{E;1=oAe!xmYT4^|uFA0N|u<1<P78e{z9Z+dV1i{v`YbsyzFu2mgxr;PIV)45xK^Qt#C!sjli{MO*ui2ZCV%zmy<a*xM)%Jh1D=Op7teB=56>owB{S+7|!Rh2)t<Q>=RaeEB!EONc0$NBur%Gawl!QUU#>;71`@#(5g@b|~`x<7W|4$3F|I>Fx`s~SH3{se!2>@N9^xW4w|v)%oFmT<`ZyD9iA8C)M4F;Crx^YK0L`=+SpK({#M1M^&OO&RY*^Y)?=2i@aO#xI)f`ryTwz0rK2R#EjnosIuod8gKk+oJizLdott$2rhc`Ouo_{_}FK;s06bdRzBDW4!WnS55byuXU(D{og&qe_p27=N0@4e|`H5e?LvH`)OqypnT$v8UArFy&eZ=&=Td>=9ugDGgF?!(R|{x-w(L`T8%%D-Stl1UdhpX%1d=OxX1krpPWtYXLp5t(Y({?zMAh<`cV0bC1&}@E!Y{KglC+s?)aR=XZf#-_5DfZ`*xlcaa_ae<2uzpR{j#6^D@0YFQ)@OOK4WaxEbCXw_0B+Uv7r-^_J|3=AF~i)bD5_KL2!e+ybY!M)ScQqt!fZHh%R?*W1nFooGIoahCeM+`mab$4A`H_HXzUJK}zJp1Gy`fN>G`vy=OQ@>}c8@b}a7A^Pd$!FR7a!#@tD*W(b(hi_SXhX1@w@157;r#^6f{E=x9_s>W8bIR-U3ZBHDIy5cf{;B?)@+a4-=g+A_PBb6Ln(Tfrwc_#Zm3MM%+!oD;;@*GH{l9m|XIZD7GnYs0jq0myR_}!m3MwBQsmA|>+D<edsFdW6gZ(i+Fx>SiU3PAb<`cJVP}k)i{$7XquCI`0e>CrWU2sQ)KR#IPzxu>I(Y*cHYIQ&7D5U(xj_!V}mF2fb_zlVj%4|q-uS+~Wwel&oCLE6Dts=z^sQaac^7{_V^j|O2>+9v5$IstCGh+Nr&-e##;b*G-=<92G@A~#=q5RQRbNuJ)`6J5f^K}N|*DCLgzu~>{e-A%k<sAR`nBE(o_d?2FtK|06F4=5vG#@;2Ma_Fp;a{tw#%<`hZP9%2$TRMH$Nmn#wW`{_&ITu%xAK3felKr~Q@%n2^}cA7;cztXWXYqh*F^kH<*gE#_eJxe@3O1kOEUg;L$#lFammqq;-7Qe=XtRHO8VJ(wtsum>+PM+_@2sp{V}}mk24=%I5gXTzNXjbYp>g<{DZyfx!ojvax|ZqDYbjQ+1v25_pA5F=a=_J^NCfOsr&hBd}xpIMeaJ$e5i9Pb-hj;Q@;BX3tg}0Gur=?-t~cljrT|OZNE^z_uF{qan}d8CLNCEz4wvfQyQnZ`?v4lFJ)BQ2gYoV=Dqo(_7~W`d=B-ytN4rZcbm`m@5l3Z@N6HfjW5|^zQ6yb*ZmAOz$Z7G?;oE>JmV9*^DFmTMfH5ER`75%pP1ve`@0VQhd)zE?WfYq`=a^am)F(&>ha%{pI%w*=l!9{(R@mo;%ff(TGpek-`8xefB&ZU_CE@r*krE1|EAadw^rki$Itcm$Mm{CLA#*xxyQKAx6rC|`=WaN-Z#8GD4+U0uEif8t^9?G$<e&Ne;)DYR;lN}C46A4dTw7!b2ys!)(eJr&J<L?_Z2;rPrGNayC0tarq|DZ`w)Jr^4|MY`zgxn_lx~xFXglBb-jLHm|njxf*JcNzpH41>v_JJUO(T0Iq(&Wx!!wz8eTs?txov)#a-_`{|)aw54TQHzF&>`{{5R?@87<GUm2Y5@4xB2=kpKv332oN{V~1nPjKyY<x|(3=eBu1n_fSkg9q?ygRa-lXVdHFvvU$ZBu;sr&!*SUXD9zW<q!Us;J<%N@7+J`@N1R#?jP+}E3fY#t1o`M^7{TUy}p0!g{PE%=al=r)$^-Iyq@1K!lyp#dT+jMcs+j$p1^;2#`WHO%<y_XX1#b@`RRw%bCUUq>Gk}?X^C%n#P!~M$?$r<WR1hmb=3ZuFPYw(FBSVi`CqOt@Sm^g_4(Q%{Pb%J{O4<WeZKZ!{1CMtZ~RTq_}fK)RDSb+OI^=;+4SBzy&V4T1LgI10MqOBawq&3YCqn3+3<S39IW%?G1nKpvB=%8UiTSZulwxA_zSmO@2#&5uh*5%9Q=cuuJ_ihhS%$B$IhdC+B%E<=WBZXeZXFi|Et#Gi19SM9?#%Dd;_%~JwB%Qz9+ORsC?pKb=_GHnqIF5tvB&E54v8j*G#Y1Yu0%D07q@l`qA_@>ql!yA?0^8Q12bRj^2kKR!^OmexDx2cdx6w{vKGQl=3bANr<?PhWEY?6vvnQH^F}$P49gt>4wk#cY^=EGQGa9g3T)_e>X>h|Gb>;_)NJHBKrR}eo@W@|M}Xf>L|ZD6gj^wgOBeVF|Q6b!*A{sF^{$CHc-CP_~mXt^mj|c+xmN8KYZ5-uJ^t-8s7VkIuze=oa?>ssD{_y5AB+LmG7G-QQfb6R~evv>O}wf28ZJBEAM?rnmj`JEGL#k9M|yrxWPI25z2etMGddVA$S6R=HwFpIGEo1?m9U^`6bPkMqJ;I@ta#Ljkq7az~52Z>v6D?mMA~6X~a0#r}63IBgP?k0l&X##CSRz4k&+XPNKj6rq}(qPU9QRP4tha>Amm3+W)ThqsP<q-gu_|nEUNU#5mY_@iT8mjzbgt$y*WQ8BF`V@>TmSi?}X^_s%OPK5hSH5%<60z5BljK7PQmh;cBycVBJF_Mz*qv|b@?{oFRaer{X)@WqtZ&u!Ct@3j>CP4>fk<PopGpXZHJ{>3B9{o`yk#_u`2JmNkXjjyP-_wL(g>nMNZ=jHzX*d_2ce_8JD&m*4x1WV$3|GGS4d<^e>S8v!>`SqFA{loLt^!j;g4aP52UO&%GAJFgRxA8YJx!(JpY<TZ|alMQ3_9v0|=ePKMpGMrDPUWu3=e-<xpWh#${H{vN{KqxD_dP$uNXAEb?|Z)Cz4Pjguc^E@Zie^9ZRZr_-xwBgUe?$6qQfJfW0~Jo{=u-w=UC-M%1>UV##4V6H9hl2ry73eQZ>%ZOHCit^U{g<pVWT5d9UHU@3bE-=RQ2^_S5^$Y<N9y2|kvn{K|7`d*&^s59xVJ2K@AqE8Xq&y2kW{)w;&>4b*YH@9>8A=3V9Re~xhXW3w(ZeWG5MwZf+;pR$5=nf6~RZ|U#GS@tV`rp0pqc$(fDPwnS6TOM(JO|QRu7r?Jp-dkrGKInb-KBN56-0pMCTMw?lzlzuEP3`;Q^?GwB{*v-~J!^Wsp0$4bpYqqvs^1IiHPh?$S}@%g%8x#$es`?b9`UT#oHF=MYCn4YXnMVV3?BYR`E>)_e(LWDrcc!0w~ylovwd;CCmTNKeXqceW<PunF}<z7SI6i1$o0!cCHnhgdi{OFnurg*p}hWnZg{<aYZZQn^7?y=>Amms3(G5ipon^&@O{Jd`uj%k8~h~Yz3(lCxAph%U+`I!_r8Z4-uoW@c~JSm=T^CGJ&%1nPWgY&y57>?Zw(*R^BHq{{av?cT*Uq@zB7A%5T5VMR%!e$_Rn`_(_4BzV0cG=Cm+&Z`Tqv5^dHyr5Agc?_PhAIgH}fDXBz$r+cOT2c>SIKuK~)R@1>r5`a84X9sOOm>_FwOEAM^xHoUFBd)LI@Vtf7F+wcLtOFOe>DSv0s3V(l0@AYR3zNqrv{tfT#{|NpIwx|E5*Zp^<FIWC%I`#Y2-;E9Ly_XH|eK($qzoWeVj%|8xo@08xW7{9#pU9x*v3ys5#OwKk;q`ZQ`}kGmQwpt-w)dUc^t?}<>-bbfT(94crq}Ps;NSSOh1Gs|KYIQQzBK<ia`qd_=j-hLF1+Wk;q`OaZi4T~_B@A8ub;zKD||urqo0$8*Uw3NU7F*r&(U|Kzdxqe{R!^JFX^+=-yhTK{siyfYp@^v9p3O>e<q|?zRn$WAMzYFeNaD#XXBfHueR6Uu?=tYT(#!nrzjubxovv=+_nm4Qohm0tNi!RBcA)mu8Z$*a+Uvn@O*pay?I4X{MX8R^D)Eg`_0;2SNZSDtaiQr?{yg7o8NwcudTeTzq^`V&#$iHFPC<`p1(cf_57`0H{~yFP|rR6pUWFw&s%~c@p<vgTTGvlkN;dg0Y6mvke){wKEOQ6uHReviB(oboUiHicjhMev&!r7G`%;U9DqNkyf?o!z5Y&~y|41M>aTVC&wAYSwqF0fiqD7F-)Rk>sK3(=z*`NJ*XwuF>+jy<CM*BgLH9a3`a84XE!KVZG<-mLz3wx8K>zohX5!1gueR6gU&AM|4z-3PC_n1XYXA6{-W#8>_<!+wd<?J0$3B3c`on7f_&nnE_l*|Ixv!pA^A`PG+VCOPcTRu2!}hH2Ot05>P9nZAp7omPE!Jz!qD1AB@2cOm{tmDXe^mK^o*(YVZ&lu#kLB5*e6|y-{MXU+`Z`*@@CB9E_lfDf?*o1D&$EAh-3|Zny6;f_lQt3aTYDk?t+o;K$zT%xLhH!+ZH>b`C;yDtkJA93^k>9=oFUr(6|o<u$T8*L&bZFqUVqOtd`N$nZiwHad_aF6HoT?3XO743Q9e<B&oq2Ue<ytYhVs8QT^BJ94e>uK?~TKlNU!e)=hS`W-`%n%qMwG>{j|>FYb&q&X?opHJJT=9AKbjgKW?Vi<7S_H=7j6V++XAGr+o^4MtOZ+)-zd@e?fV79O5JXZ41S-ef6tdHN1;(rMI$JJ-hh+RSP2JADz+vRSSK}{r~z`EtGk&;{W5nYazpt7|S{ou8%3<<KzeMarhK@2|fjXPW}T+rjLEdC1X`vO1KQ!0G8|ucL~?TaMh=TN0OW1k#Hip4NipDlAGbR@CuIg2FL3PzfG=ySFpWs({NP?S1U@mI++EQ%<1D_V^ljQoQnJ!mJ+^$`wYGV-y&1sTksF$Z}1Or>R6S}#wwP~<>QxV=YngH@vvlTSk7@c=iL;3m7EK|3Xda~!Q<dL<UDu|Jf35{#_?LiBgpaac(xbbA3m@5!!?au2JeI4ho{mOo=;nHn2!h1mJIp08g0oqA7`g68SwFKOSL8cfj@!83E!oC0saL3hW4lM1^7qW-@>25|I*G8qxf4mA8q04v?Xi8gW>9M7uv!LXiE-<_rnX|X|&}Y4sdUG;Qk1b)#2)F6XYJt$GsQeH}Eu>3Vs^?m*0cj_y1DD_sCoDJ@^6n1N;DfCRU{!^BInv50-nZBlmVb`d5>z0oP!gnxy>A0CEI80G>(CgJ;5v8IunDRwVnw!{NE)40tZQj9d&aW}m_#?z^6paD6fWOFr*ox$mCG2|r2Rg{6dl$9)6;4&Nhxgzv$BkpIGez)x{6%6<0~_g`@z*Q8w>Za{W{C40egjyAu+5Il@r0}q3zk{jTu@G^2OybPYkv4(TJUhp__8a$2d$1#Sb8Qa(BUkkE6T%T=PaE@g-_tN}*Uh+veFC0tCxX02K{+nxY5B?iY6{GSGSW5UgQjYl?$1VfQIlj)=mZ5*G$Odo&wrNGm-;5&1!K2`X<XU(kypAz>jcX<O25iG?$OL!|yn$Q?uVbIW?ZZ_*Mm?to!PUseVae=1{-34V*<pDmOP+#n!=I2R;7{NS<Z1W<{3-bb{3-k``9zFj$s9g@iFOXSI@tl191P1j&gZ<_!&At8@Dz9p`98b_-a+n%cfeaY*1H^UFuZ`=3U6im1zg{jzI&i0_sHvTE2<^;R~h&@N?6~k!uoy|*7v-y{#^){ri5EiExD&&gWsT9a_=O->&S($%;jE)eK-#k)^kN+J)acTb57wBl<?m%s)R4bs1laB^AT9)%ZFf@BYyzPy!a9<bK!sBl9X@*O85;*So$v4qJr-_R`6Zx3cmZHg72OYE>8(RP6_{y--7Td?tkGE-1EYxxzB~a;NBK~f)aj-s=z(f0e+XNz<ng|$2i|RG>&&{N4O>x$NM=S{0t?m-}S<JJ`flCaLy3tn^(j!?+Cy_Dvoz@2e>~K$Gdk1yqKH`e-u9V4dFU!Dc(W*1Nb9&J?%~K2k=7L!t-cLPJ#!*^WfpM+rb0jF0_R!(Uz<amx3$7)o2%oOTp!73zw!XS>4B#X-hVM+ryRNuCxci?cou$h3C_jd<WhP&xaS$J_>J!H_)CKu2&hKdGJ888QhF<(Oi~xJGc^A46X#1A`8Q%;Ns--aB;XaSq?4@S0<ao%^45PuhVW14<g@&-)1}pagLif?}_j#@&kAk{66^+{62h`JPIF%4|1&49B)3nnLG#|WP9Om;p!ExQQ?{uu6M)rCOHZo#Wup-!__-nt#R`AuaK?aSKx+Z9NZADL)L)nz>Ub7a3i=A*&1$5AB3ldYj(Is<D`FM$<gp=wi!#x-z*~&;bm|#xeHE)_cA6jM$5^i@N#%3xeeY4A0YR_d)cS3JPU@i?|0!*WEZ##<Eyzo?QU=@vKrh9jw8#%ac~W?I$Q&;Nj89M!mY`!a974x^9b7A;nCzf@H>q4XwGpt=RFBtNbZCe!t2Qc@OpR$xeML_Z{S#qINnq^k=y`pV0+<);delhaP^>sUnKvFQ7rj*>_a|JTT1v#+)?;T_$=wbXW^6NG592Wj=TV$gTErJSjCc0__!GDC*ZPVBUrL0Eax~WR-Jc4coexF9tE!?x56vob>s$k9lVNTjpleg;djVY@G7<!&Ks_R;i?+0SHjgMTy@B*a8<SuelA>v!j%>$fBz(z27VI$Jx1m27{yY;Kaw}$AK^d9Z{a`Sr(#vgF`weth2XZ~>J+YOIO$(KvKm~CZR(NoH-pF_@E~|9xe%TTFJVk%j0Tef;lXeM`7WFQFDIA4OW3Dy$MAX83RibZxGtF=mMrRHi*`{s6ZxH`I1~J<rSdBLEBrJ0J^VBL8yOR$_%}FnjLHJAWHBGtrd<rKN4^3}_JHLaC&Z}p?g$SdSHMHy>EwIxbU2Y*2`9ocIMz^(*8`qN&VXmI{Y1vFBxBo`{xv4+!gblEG3Qu{b1%u?=Oi=1IpK7qjC(rT!hdoteun>q)5oa%4NlK>$VJLAb8+lau$<$ojBP3U*OaUW*JGQer2NgB<V5&Qcrm#WUJNHOCVjb9lB3}X@CtGfyaIlYOoEfxr*P|Vl?_)vO1K7@7M9HF<F75%&I(_*RGxva!&k_Y@D=zHc^19|e@>>rpTjrE$6^#qX7h15+S%YB*#?&E56d~u<-A+NZ<D*=x8ZH%0eBm{liUsOgp)beB#ze~o<}Cb$!tH5lzq)06X9L(0eCv?UG#N2ImE~PXiIkVaShs%wS1hFwq$-E%k|4oTKwOxz}LBs-_gDVU*S4lrTsa43I3k;4fu0do@>&UYZt>c6)r$K8`rG>SsU&T2jN#}_h(#RA&0`dVLj$EXm8+MK7pJCuZOq7Z_!@QT;VOUkB@uMmTU&U2={<1(iVQ4wq#Zx%ls)T`4fB=7AO1-?UV3X_zLZF@JaYO?XTc-@Xxe`W&ZRtnGG%rixaLyTev4}$>u(Ohqh#2A8(+&fidpOSXAWQ-UhBpW`!m5`dH38FHSfO`3)>3d>eNKz75|bufsRtZ^@tGZ{f6zg`9U<&i^?dSEBtKT#alFOSXmEFkfj#4dy->%zUK}mB4+Kz&zzGYB~4ea^^6zsD+GabH=qTB|L<j08e0hVOa~mW<6X-3+uJEuwIV~>ovRZtCVmvO1LZ~T#OPfObI_v374aUn^VHCQ^Idk!mBA^>AS2?$5;>7u)?z`;jxr(Z%VimC9K!l!g@U}tk>+qdR;HvixPg55}ri~FQtUHQNnx4WLVw>FUCB4j|l5`jj(<n3F~*3a9K(?EhQ}PVJTsG_nv{}eR~p?ckEd>#Zo2w7$sbe5^h5YPojjS@3NLD8vAe^B&^p;!g@U=tk+z^MJQoeQ%VWTI`TX$YsaIotQQ?v)`-VoSr=Y_ElRi;CESP-9!&{L-(`N)B<A59O!!qwxG5!EiW1I63G2C{u%1r}>p7>eo|g)jq=Xw&!hI>>(UkBaN;rvJ49ohcZtTM~lyE0XxE>{3h!TE^64q-yVZ9y{)@w##y{;54ND0@WgkPbA2U5cCQo>8fsc_?PJs+-alyE6B2A0g=<4<B#I|KZ`7?mHw|ASAHhvC!k3GyTO1bl}46g~rgLB_@^mdxnm;<PiurO76+WOrE3aWd!K7=Dv{4}KF~O>Ti#!%5^uI0;_EvBq$`?(h_H4ZMc!g>#21f4C}#t8=*8g{u}>8LrGW!g<0~AYAEi^7om@$KXuxpD`-Gi%~2ke3!fd--Z7ozlZ;VGsmiwV`k>q1>pAK3Wci*PWtyUSp}}bHZPO%H~q+Aa6foDxd5IHFJeq&jE0i0!$aZu<TQ9byp&u7FJhm<Ey7ifeYb-vliA_yjIZYVF{+&#evG^dOI>A*B`?F@!8gcj@D2ET@)!7fSjJm22V<Xu@zq?Ob{@D2*%EHaSXbd3hjQL6;9lf>xEDN@TndkcXOj!y*|5#AdUL$?@G#PbZMGNQ8$Pdt;hIG*hxfn-;hD6BXVaD(;o||cB|G`J3T?@keVm21WI-R_v{YO20sI*(PWTS(i|}XgHQJZqi|`M$Z^4)0|7brOqxcqFh_-N5+LCqPfpAs0Gi~8Hv?WKvd*M0oEZS|uRgrNT09PS1z!?}9&0kuooduRLkvs?Agg+xchChQZlIP)z@MZEV_%eKp%ow9s@>w5Oru{5jm23yMV_d3oj<Y%Mw(vXT9{3%26L}Ec1aBwz!rS4^9BVSi8wk%KH^ZCRUbt|$N`$LnxO#`HYq;XchHyi+5iSz07sB-nPX0bO`81pxPEFpo6sLy&vQ+*A{{^RsQTYojC7g$pW9H%5FTmZx)hAqyaMHi#WFxo{+cYQTZ^n{u!DHd2<Z5^+yq+<UF&a;ffycwE$R+S9cq6$UUe7*-<yr7D`|b)iBn!d?8DGuvyDy9reww@kOWk3N@9?|7PhDfIukpM8iTZ(Y|AA-1FVugGyJR88z7XT9xeo0ja3iua+?la%#5s=VygR`o$W`zNcqX|Ko(V4}SHsKUSsZI5$Lj{aMb3g}vAwX&gSPNa*uuL+_&s<FJeIcbWZIK?S847>yBqH|;ZkrnxEyWa474-wUe_%1*X-ndAD^Zzc@;hZpN22fJ_DbCuhISjJ_G+kTR0={`HZ~Rg-gTYO7mXN0e7d}o%gQhDYU2X-qpO3_D057Sbks4Vjlhmh5Jy#%_-p*DB(Pmuzpqu>*tBEe&z`4=aO&<N;sYp?oA1gp@f%E!t2SUuslmE#XNit3+rdKuzsEk>u0`jMM^jWCHy7tGU0Q)zl1;Loh5vp_muEgyqknGQo@xf;dYepWU3N<m-%h&*oSjq;SeSKG9_Gq63$Es>$$qHp3e*GIlr)87YOI4glkd4ohjkhDdB09@FH?LENhv<u@Bcl!g{SFtk+Y*dd(&LJS7}M3ClWCN?6v8AHuR;JPgYk@grE)g`dK)lyGrMxCtdZhAK?oCx@@y&~Qzogh!H{VaXmou1mWI+=8qEw}5Mr72sNMkgN&^;o4+9xHjC948f8;eLReIPxuXT3M@GtmUCQTsq>x;FCcfr3*dF+es~?co!kR&hm$x~0>_&UuOyS;B(`7481`XoXV5>J90`wP8=G_N%enXA?>mq!;0|z8vKHJFewhryFT?R<Z8#q8NVbGq(ua<m<4nf3FZ~-&z5&0%HseY8n<eB*cnQ3f+yifg_c10jxK@&j;T7<1atpj0-cRm>_pwjmx5CvgTyrSl!DM4tvW<_+&~5|2L>7Txf?psD!7soi$f9rwxFq=^ToSHGHi0GE`gj2Cw(t;g0xUTfmUDcM^L`6nLmq?Iz=z1=@FDmJ`5}A+b~x5rjyD(HNII~?_8Zwx5^dq_w2#5Z;dQj%gO9-rXurp~Eg&bugW);wP}*(a!Ek5VZMc4&$-3|h@JnzN+9lu@;0m-$aQ!NfRefBMwq!jYx1}u^f``Cu;bF9gFuudcDey*kE}TI7LwF;cL|cAe<E)3jLE)K{@OVnNFD2ZO64uWOVf{Q2*3TSa{ah06LkZiI@C-_LF(tf(65dB{g`IHqw;tYy!unnn*7vipzUPJeQNoQW;WCtP5lXlaC0vveevuMxLJ1F`geOqKYpMS9J%70Jgew=B9nJ+mOFjcX3uh*uf-}QUkQw18;Pm8UaC$fm84IU@Q;`;&3QkSNz^UPM^k2>=FIf=I3+E>D!MWjVWKK96{4|*bej0v~%mhCPXCNPkGr(!dbZ|QQEF1_|0s5OCE=WEH7liYXIpBP7PBJT;6P7;4H;jqRlIs8K|5g0Mf8>9|V@3QwjyL}@@_+X1|I2>ieR=;Q==g?d<h;TcFV_7pY!{RNw9ooKC9Ac%'

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
