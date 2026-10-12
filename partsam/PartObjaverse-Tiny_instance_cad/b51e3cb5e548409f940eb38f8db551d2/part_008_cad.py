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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_008.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_008.stl', 'source_sha256': '7c4228c063b953b3f1c3672ecd2092ea97a0bb8ac9802ed715960a1cf02d498e', 'input_faces': 768, 'input_vertices': 468, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10556364804506302, -0.23311197757720947, -0.2628136873245239], [0.09898477792739868, 0.42762336134910583, 0.297135591506958]]}
GEOMETRY_BASE85 = 'c$}qN2Y3`^yPbq0U4&4BFdz_00D({ySfuyRiGVC6p@o*vi>!p2fFL!Ygr$WNdO~jtp(j9CkRpmJRRjTrA5>89_r33#y)z$spXWaJ#^*fe%-J*V`|UTgv$HdUp>48c4bb?nw6^)JJJlYnX%cy~0Bvk|)ab$e!=tMXA34EK%TK=iGk8(^uI)m@{Is#!q@V%e(fy->>gz$DM$`=o)`KEOM2(K>JG{?`r~%>9Z{9aDI$ZeCgZhpP7t0kwYS#_cYgP=_r|AF3zg%Jndfn`YjtO?9hGaC7W2#@n-N@wI27P`}E<1icdP=gZ?Z|_a-}*9LE<0nZxGnzkK+YH2M|o%PoCD;?=oiQz*u-t|&$PHi{*^nFw>5sTpZwf+cs!0qZnJL-%}IIJ=$n*xth>wk%J(gKuRkJ>C9m&q$9`%O<z1Qe-4=gP28~}UoJo0)?S1ZBGbj1_k}htu?};vwNy}BUou>Dd?A%BBB?V4Pb`)83((JqD{(6eI=ejf+XV(dwKYX6%$92Dh+w8kWKBw{PnQv%3+Vx2GZ(ZR0wotdlpZ~&|kB?wK)@{whw_W<vl6O76wwL??^C@rtr;Xd}yNd3iynWQ~ynVN3a=zeVOWy0BJ-~UtmpuQAS8$!XztMcUPK3M7z9&77=F{<4Ihs$`rfgg%GKKQ?f_>d)UtbVOd3)uOly{^*+e7(J4sre#=MCREZlon|+xo<3-tgbad&0<frA_AjB)GTR?0Y`xNO@;Q0FU3*&1c^5)x2|dNghv@oBX+WKGtpa^<Mw-{B&)}<5@L3mGW=nDX%q-a+`f!_fTGY-H`J7zvIbw{j!eoo*dC`v+ulgkMgdWHXi?vW4M0LwU)f$t9d=(ZVJ_p4(HEZ*l@Sm_bfWa<Ec=G^7fZMa{g|AOWyF+yz|x;^7Ynz$hUQy<+k``qb^gOokMtjo(GU`&u8Ot4v%qL{GU5fUhCAC@>)%Q_S-e*d9FR(ZT3AuVVu9ykH_=k&2E~9BTX%NuivMKC9f4cN4{2e;0daCu$jeo1%5`pEl-zIX5SI>+ff>qXSXHq=#fmmv-)xVJhq4=-_xo*&(Ex>Zj1l89*xHq6UOtCBZ7Q=S~*MJ>zB3WwQg<6x7`b;<Cm>!Vy4A^5=*|;o$GmqHQ>H$uJHWF#JkPDeewgUujiRZ^*s;LcG3H~JZ?9QdtJyyi~n#r`L^B1E?E4fUG|fI<BLlcf9p8%Jue<o9b1P~^3~(B;lFcyp0<&EJtCF2@6|<av+uN>q4C?d#qju>&t|{fexA>ji`{15Q|N$iKPcUIooDbH%;5Q7SciNqe&=Bt|L=#+Sp1lI<m+Ad`_%9qSFX_UQp;WWtR;VRC;86usZ__&^Y@+n`HJW5`s;kR+4tN`@agMMl4+dI_7hKA{M4=N-=4(df3}x=$DxY+{+7KtYw?q^^Y%%aY4NqE2}!iSOuT>2;-_^cUt2nyeCNrX+_y#x>g(9G*=_bcS3c+C*Y$0@|KBW5zVlTOe@^{3xGnyMVD`^jeLKz@v<d4ib#$D6ICCWNJWTw6>-<pJQpfN;`x;vEu3I^GP@T1T_&8R4joack)p@_!ypsEte7)UQ-tg^{OIh;T*!G-{J;dYr@u1t{54ecqT_zvjinZKE<E-W6`mgu8&A#(`3g-u$<?*a8L%!aACFiSg-te6jcJT7m)4ZSeDdDre*MHwyUu#lgE7kwY!N;YRyWJKapHEx1V?6$|uabS`y}pvyN(^NGQElE%S2NreKdsdjS}ysL-*2-|w$S_9R)p)6JL@+4_F0uEZ#(u2?+@8)aeiKaC2#oppdd?LZ=2I+-tg7Dt6I*@ynSEt_8pt%Hv9JA9F%w1f5QIo!zN#O!&me67stp~kN;j@IsQ9NOeNnlehZJ^|F+xg>w!n9zI{SrI{vsGciu>S8^rOrJKc1feNT}@$~%karM&a^((FIs<B_ZQcW#S+dM(e-mVA`=qy)16;cR}NaW~v%-}!pErM@Td)dt=lM)0_Ye(SdQaWOnUZL(2b|KS<=_B(?(f9s0d?CXaoQQmVX3m>-!$CK}TRGjy#K~LQlKds7D8c)+Yl(#L6Tu<Y_{};dC{g2#cU!R?i@}B!uIG<3TeCOmWJP$1&yUo7dy)f6$R-NZREW~Ht@bywfEP2O?eCx<>e2>SS@W5^H17Gv|O$y@rF*$tZy}p`n)Oiif=daN`p6zekX5V>cCcodzj{JVLcI11mj<e*w{`OeT+dE_agPc77ohk47=at*+d*TLC-VxQ3_qU3r$=5G;x8%Kk^iay{{;hfZd6E*z-?NRkZ?mjd%)WEJ>nhjj$K%OfZ3VyIt(>32+rjWXXO3C&j=X;__mww%wZ3D<!eu`5@YVXZW+#`BUz+DftMkfj@!y17=0|Ilyu{c1cztz#mPIb2@$`=3?ezfrHGEH<8J6wqSkZZrukGvgmF;V*5&VtxwSeU1w4JI}yd;+$f3H|Ty!Y`Q>DvQB*$+N2-{<~p_{#pNRdf2xdwn&Zc<yWJb0l&v^?k1+_r07m&e!M8@YT<qcJ+Czue{-_pKHhcX!1QDT8|rsZ~r5Y<+$N!7BGwE?PLVao9*VX%wuN1-!t+(TgF}>|9ShF#OuDJ`P4Q|%(VFD-;(dSv4!)oCuh)j!irgrdtU!du;sYtsFa_4ZS<+l<aek?^QIkII-Tmx@4eSNPOpD?3i+P)XQ;1s&Yyhs_-y#<ao+2z$8Ez`j{lC7U#C%@$xFA=ejeC>$C>o_E8+wFchLA>G~(?Z<|JSJKK1&__o;UM#+SSut>0gUuYP}N-zRZi`F`~J%J-vIu*ejeALaYk@YU~MEo0~;dS5%Y({`~<sl@Yd`1QW$?X|1KMOt=`9#6b?D$S2=mY!+x$809w6H=G+LBEV8J{C&zX8Wu}rp2E!k>|5(OV0P+A5G&_&NmESJ>SqypC3uSdj13do%5v!H;4Po!+$4l+u578i*o*E`0DwamZM$|pLzK2<V%d|PI=}0)9}^vPt6q?K>YFHCA5EfI$pH+PwOtF?f&Mw3l{&{{3Lo`f4Ho9?Hc)dKx_8L7i>$*>iM(bE9cKz-GBR#ub$5vzIuKhT+mKDs3jeLT#hrmKN!9%?+V%<dZuMq{GuCaKXh~mx8_$oB;THQ;{}VakEi|6QM#Koe<PJY*V+YZKByJ%pHn(m^M$7I{`tgX$vbjiq2r<B`DIJqG1;GvS9;60mhn4ocPHO5@|ZP0EryS8dReaDwtGLH^J)0%eCqv%5kH^3Sg!9FQvHI(56MHmKJ#FP#kXILpgJ*5YhJ4}l*W@-k^QfON71tK`_AjDzwf4hLB9I?(eTyZk6N$TD4+G=tG`dR`bQ>Gef9UR;VZv?wZ?u9@|EA$hX2m*>pE?H=M7)^{jU9-K8-l;Z5n-E6Aqp;`ws0f`OX`^oi+Qe3i*yp-?gjad9!azeCwj^^_!jR+?W?btR6oNUp;<S={%i$_4sV~>hXEyPV&|38-}l5-_RDm;k<HP#qibZC))gg8MLfipD}#(I*gWlk^FbQj|^Y^K3X<oHu<Zr(dWn6;S>H|fbW@=LcV8F8?Jw5J^79Wp?v?Ow_k?EpHzi>&(OK)W?##Q=Ie`NMq2YLyO3}H=1<N)*)oUbLAicq`0Dj5t-*iDSI;Z7@!8|ZSI<M%?;~HmzGwLA^*wK1xxVN1)$4mxcg&@6tLI~eubz)Rt1yq&Q_t(>oFM<5>&%9)o)^vP@io;~&Og1ra{j61t}>r;%K5F=SI=*!)?7g2Q?Bb8zIt8P>nqoFy>-;<y2E#puU=<1eDylBBQVDzs;^vEH+=QFx>kJ@`S1Mh$g+=o_4>cpSFitnmBxLQ`wL!Qxxb)|vMr`MtIFJ@z5|jo%)aMs@GV-d)nXFyIVbt*?=o$1T{>TR=XYEUe>z`L@4t9`<^GGKY9RUQ{T;(s@9#LuMsQxaf8_Pm`$r=lEhGP8XL`T7|Dg<vU-b)qzklSILhL>g&!0!@{VcDq+|P2<T9`n~%Kb9KSMQf;DT$m{?#CIvns@y4h|ZtX`+bJ5-tTkRUy-lgPc-~@^4CLFQhnuqrQxghD;+gISw(fWMc$z0He)l)zMgN~ca*ObHJZ4}FrRtD*RLV3ujl-XxrsC$<$kN-tM^;Ah+(Vg{V4Zy4PU*V>$o?;XWsDDyscQ2llm4}MdNpdP0uj<_C}j{{P)7gQr&CQ$@kp0<_+Ke-eybQG3O5X@7y1Uuio$0&i(8&Z}@87H7#Hb<<<N3@ZY&#U-B>V)$d=!SHFK9VYaor|689QFnsm-0WEF|`ReltUSD}W!IpC$`^xhVhOa*V;Fu7!j+Wc+zfN^)HqJ2np0R0k9MB5;M-m^X!v4{{mb~HX507(RPo(o`SKn*otIuy3zWV%z=DEXp_4yFPSDp{CegB5*D9@i5zWV%$?aw#sY5Y?k(fB=?p&4dh-}I8lpEzR#%|l)P4dg$6$a!0b472a)@Vh0ir38_$K5t|A>hm^^$9>4R@A`@A>$}=zn0@``6RyAe$Z+Dd>&aK2|MB|D^FOZfne_WseZI)+E6*3XQl7D|Jilc4>hnw5(2$Mvets%IpI_Uto*8D}o~tB(e&ajQ?;qQZBjh`Sve5gr70;7l_Vw9$`TgD)*PHq*$>jR`vhw_I&YNNOokiZa<Q=hro9K1rc`dK6Jg?;_I+xDdJUv3FzP&>6472at-;nDMX+*z2wQGs|d;8~Fy#MbH%rN_UE1M;6Yxe`!KVF&g&iJAkX5aoxZO+dg*Oxfs5&7!#X<lD>KFzVFP%`fi*5}_0Uw!_~F)x{X{Y5Vtk0YskhQ;qZkjIn%%>b%fs|%ff+t0SYM(lSz-RyfRgx%oJd#@m>lWOPl^#vU)dBgWSx8}9I6}Hp+{BtVh9jhOtTl}zC&TIFZ(Cam8`OF)>UM9|xw^bR)e&zAk_;Y_Z-Qveh<NWwjHd?;+;ZDl++)R1x>)+DNzWs0t=hs&crCg;b_SYnQOUpm6Nw@fZ>v=!9=j7{Lb0(4RycuuF8@`&i59zgwa=Fe^UVFWR@`mrM@h#`CCWOkoelFZ+-te76u3GZ0tTQ;j=p^R{Zs+Z5_%AMU-qp9G%-fod*iCibzU1*|J<9V5UoWTe{Mh$2m3b{8jq|(j@_m!cNZ!8i?FF9lJkOjsn8x!ugZ=a$DQ~w8<?$GP<zFm$$Bk_%G>*FgG#=aSiM&4;ev?u>{(wc{H2ymKQh5CNEqSlsE0FWKUQ^!n@*Mg0_4z38Xg`6+17FWpjPtKPkD&S?sj1XAZ=-Ly-Yl*U-&w0Q=ch&Yqw$w7O1~5I?<?~Cf}q+we)#sRwfOz^w$t@rM+9GAv*+!}_ql2{<ve_6tq9I1B#xr-_X}iyPY+Ap>lf<J`Nf%>Uz=?ojsL+MzMs;h6Xy-T`C`s*IWU68b2*ZpPjddq*VS$F^744#+uz&5`_<|Ve0}_b?guEJKa;OxuL$J*!SL(e;{5$xV~>Seo=#pK(=pLeR{nI+w47Ri7SY%AXtFfrpTWK#O&%Qbzj`#e&j0_><a1&Se+wKGcq?#LpsF83>PCJHsjGnxLLbDsQr8kFDbNCt`eSfm=#QZ*f&-u{LRSE!ZVs*q{k!P%QsX`nQkMk3f|iiFF!&E>38@26Q|g-Fzo3r`zM*lS-=SZEzk_}W{R;d&^egB;fbUUPavF51z!{DE9EZLEz6gB-`aAF?=<lGv2QHzm<UP<Q1a6{FD)brfE$B1Q7r{S3UxYU5Nj?ew0s4i&f6(Uy^iA+<=$p{Dz<)yDg8l*c6E!8jfvzpKK`B4(BO&#FP+#iT;3CixQvV4q1T7);8*m783+#WjfsfJeW9)yWfQsl*5&L2hpaOanf(`*UhnAm_YFMrYuQ@(Pjj$g#f+zJ`e9ry?*MydzueaEyZ?W%4eGsqh0jEKq!)qtOd!YZuYj40Oq2<`*Ya!q_(D?=G3;hB36X;I`7ZBV4To79F2hfsbz5yWhr{Ma~pF$Tvec7)7kRNsPqo&kl1UiY_N8rxTT?CgE+!b67TJlHGl4ZUtAaxgTC+IHFWl>-DD+`oC-7=^twI=YnBydmYUV{Av_XcNymh1;DS>}5KQuhLX4&4jdAN6HFe?UWB4K=0K1u}(I8hjbLy1+<*8sJgTl1oENmiZdU%k@Wsb*z_9=+6Y+2RDJ9CeT_S2HXa^4PK7{H-Vmp^;?7UK|dDwMW8v*0$xjjCjza&ze4|t*IR*GK(~T!32qME68Z`F7w9L@zk(k_XW{A9a)Wb1OD+g4xd?P&xi1UIf7{~^HvXi}0WJXTj~=<exuJ8J>g7iL!axzMUj)4i00mLg5B+k2b3o@n#_;{n-w(Z|eor8qKrwJ3Xvw9ZC4U56MxdlXQGx8>tbo)3;F8eU(W5B17<5rny<(_e2KWf;e}vv8fl{cM4gCs%1E2$tG5l=kpAEgG{y-qFKsj(}XvtNeC0B?3SU~>kF?pJnADjn}S_cP1=SPpS;BwGqP4&v5{>MOdtY00ygMlijnHT*^gLP;f8N<(u{&~?`>JJ411*(B7Lrbm$Ex8eNLxI`?RRv0bivv<u0@sEvfgV-C)u5}I>QzJihCm~%-w3^H19ea{5dA8HD?wL6rZV~#M>Y_>rB_iPNT4ye9<=0+(2~QTy9;#C<nxN+dmLOIkh(6o19S!Suz?#x+f4NuqrOqQJC?)Hy93Y>HG|Nv9=I-aU1SVD2>pZ5Tk2W@H3fQrL!l*yLrWeEJxE}HKsSL9a1B7}_TT}~A?VQ!+ylCssa_A%H);>U@?i8H0EDAvP4o)|w})<zjN#Wr|C;D6bvuD(0t3PQp(PK4mK+ToB@ihPA<!1w6p*?vI1;)odPIN+LPwbD4MhDYAR6mOqjw}Q3^kjfUw?34=)TApelzrMhTc;56X+u_20RK{@+4@<Q=z{Um?$t>zz+Tbka{F|BD5VnMuW#dk2cjCgZf_rQ?dS3^qvSzLd`ztHwruwdL%N2-v|BsptsZ`1cnNH1)c&eISyL#eCV$QVm0~PhNcY%4*{f}4332!jvfy1SI`bqy{}OJYhXUspO4<LKpbigMZYQF$<ULLG5n$EKNP*Co**zzU><l5wB%*bl2<@47g#DVS71DNEFkr4@KWgU=rI>O4|=Yt-aOP_4y?fXE6{r>unaZFq2C<vZ0Om@82&i)ABWyjFB14hU=4T`wB!xYk~cyp39J`z3M>RK0Hj_CUJtzxJ)Gb*&`wjmHK?BiY{dE-(R)3x0X4rtzg6Is&?}KK{BO|z8}ycXmcR^w1n?4Q$*Z9yuY+DIkSGu@FcUl-ka{sV5qc(i#Df!{<4yGvP~WJ%7R&3<I}uoonlsRE33xH|Vq}(}?{s8mpttnoHM3I!TfsY_C2xV2ya{@<K(fF#0T=i*AoVVAGPDalwt=@oZ!^`~iu#*@O;~>udM5*0Q1cY}?F8?F-i3_epF;mr=q>d%f!hN6!AGDa?}nDV9eRgAiogMZ>);;&sgHtFps%CH0q}n41EzZWQQxS&1IyddI|bN{nzzyK2>2-UQDlyw?~lmdMsMl;Ebvqy9efp9@*!x+d!hFU92U4B@Cf`2kosHjVdzKbaRHnTeZf>O9rgDCd$Imr^gaw6Ld~b>cNP3C^tZ?u{!{dSir!LZ7eAJA33xQ-dm3xWZfMEpp)&-o2>c}Qo*#2=KZexz@!Az=naPgVvZK#WfKktb`bO;xET2d3D}Wm{bD`fo^uCYr-bcppW$rz2cIXlU<prK=%vqr&KhRi9z5{(%;Gw{80w4M@2l+9i&IW!6{ULftuLNrU1{n38qyAms4%WYe-VcEXs97HUvVyZgXTz8czdZVv#~7skM4*AZ&H*kCEjb6Y<bO2Q{|e42_<ey-!3_ba1Hn0=KShuC!TF%y_xta9`B48~;2-pmoCCFTVjO`OXG4s!A-v+?945a3`ZqvtsoM&K3RD8uftFkpT5=xfyaL4pf(6=vI|5SI0~dpChaSP;O3=ZkdX-Q=FOUc8=RxmcKvC2TMZY@WdeHTdse`^9kqt#}>3!}e?@@~1XW*95lIucCt_)p8puV4c+*s3kg8Kqew*uFP?uj0a!8Yi|rg}EiH)>bGa%J?c57b3XJNmT*w}NhkOiT3bi>w{Jr8it4N}vn42ejnY(2_rcZX(b|psT<La5Nxw7`P4e2=wR*?gHJ_RIdx_HvvAw`k$e98=y66MxkF1a2RwLGKL?8{!!>HwL@U0KtJ#hXvy86C3k}EEYMw`zra`ES%B0-!QG+1LXZC7e$f3*_4=WHXP^_-?}Xmnfo`Zd6a9vOhe8iU#_(sN|4j6j`fGuu0;9o`p(RH`OCA6nE-*}BjKF;GGC=An;9=17(PIpFH1rr#z0s&|)DFk;0Q4RPM55+W^qUNx0zCy8!(WR2OVL~EL;<HjEO;)o<S(HmkA)s5FjXK<U^RFRAoV=(ROr>{5eJTijx*JZMg4KWSgb!5y{7_SqNWr5=7Q%z&qK!Wo#^jGZ>ci{+yZC8=b<H^fR=m|`j|kPz&U}-;46UC>EJZz%jj_qd=~ngsoq)CKL#Ad`bW__4LE_CZuC13PKQoM<~;gdLDr4l(#sIIC~z3;f|k4&TJmn_6oGvLM+7c_F9A{?2k(QvfF4J{hoO&{>K#UXqjn0Gccb?{U@vN3L_Zh!IP`I3T<CiV*^B5cy^{i`1$Kf{p(SsEmb@N%gTQ8iT>_`TX8@`9fHy;*LXTbGozS~X^>(7ZQF{ZH*Q57lU=wPdM!!_>9_T&Dq@wQ`WKW~F^!5uJ6i5PZftI`+TJmD(B?2o1HVPa79|ELK2CslVfF2vcNzfZj^^#EEsJ#Tsi_v=pupBiHqTd#9GITOBThR9qvIo&ydRqmy3oHc3Lrb0pEqOfj1c4ZVMFQKvI{>K@z%kI<&|?vJA@m|sy@jYh0T_?<$D?-)Fby@gqhCBY0XhMhc=X+Y>~{2)-b#VB0u#a0p(RH^OYQ~TTVSBTB!N}nb%4|}zyqOIp~ocfMCeJTdJ|FKsNEaOz0i9g5P_O&(Qi6<2J{SMrlapVWY?m%^kxez5cmQ-2wHM`Xvs~Xn+bFf=p!%({0$)WU~mWMIq1;``~`F$Q@t-xzZuXJ>o-O34nTX<T!4Oqz=NR&BO`Ta8$bVmEdSI0TJgXC<avl@`5!H+Yg!+BGOw8^YIz@m3T=~3-jCD##eedGaG1Q)q5T(a=?ka'

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
