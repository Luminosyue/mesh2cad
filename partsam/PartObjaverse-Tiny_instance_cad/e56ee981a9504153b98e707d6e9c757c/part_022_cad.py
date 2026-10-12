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

PART_NAME = 'part_022'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_022.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_022.stl', 'source_sha256': 'e045cbee0dda91df8b55bf840897b467c9c77395e622be95c3e42fe829b7f457', 'input_faces': 1208, 'input_vertices': 806, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41933315992355347, -0.2699945569038391, -0.1902661919593811], [0.49167919158935547, 0.27010631561279297, 0.2705245316028595]]}
GEOMETRY_BASE85 = 'c$}rY2ecH$7PdWS$T??_ksv5RkRV`SM3Q7oh@?RzsEA5N1%@afsF(<%4gvxaRFHgtCg&(o34<U?Pz)fbs9)`_r}}o+IsaP!`abX4>wWsI?%mZ@yW<>go8}oZ77XeCZVfq$tDec*A{3Iy87deW*u8K6XS#LoSGCWJLsCL{U0?n)`cA9ITDEDQ5*iqKrNYzQ`*rJEp<blIy*=tws2r)#<AuKc`*!Wq<%PaacNf2L*WUfQE5Bc_t}k|1%N6TXt6e!#<Mzstp^^W~|FWwtI8Pq=X1&r#DA&gNN|XPT-nKp+KX$qCR=*!RS=seN{XYz>pBOw&ub=17V4nUH)6b7@=TAH}L+4-JDVYDR?b@F(KIs3PX_NSoi^aF6=f?(53#^~~ZqGjP<3(F;PS1B{@7d({og$0&yLqhq#!p!Jjc?~SzMVgGeW&Y3t>ZF&GIOV3o|9+v`quauKXi0lVExeH3$7peH#q*r552QBxc;Gw`narl^!yP&1^OSKS@eM0AFCdWpDg)MF#nskA4s=9_@+OhDIe>4Yr1QLzkY1r)Q{&Ey{^}9vo^T?2ff_-i5#r9J>XZ}y)oVV_-XQ&Kcw@Vyf3(Zo*%Wpt!=<Jbr_xf<o5LZ*t+(C^-Ucn4o=*hp6^_KeUsn!>dngU)u)x;^R4_|eOmeBS=Z?Lw~ovB&W?8jdEz&>==H7fF@AFCyukXQKeq?!)AsFph;H~>=eOq3_|Cdzf&Pa^)ztObHdqhFk3??|_NVtldVRY;_!0UO`SLYAF9kl{;_mnF?Az1xlRf5d^ZSWqSGVXoskc2n-}!J*aQ*g8x4L<({KgOU4CaqK|ILo{);E5d_48EQnO=X4Z}%s*bkxrD@*CgIAKP4Huj}8m*2j-n>nD0W=lW55eDIU@_~cxlZhqr?`49C>_kL&l=6pB4eZMoleZTYaSob^IxAWWgJI}Z7cb;$E?`+@P?~HHX?`+@PkBo2M?`%I|<+ty5wr}UR?{~Iu?sr}u>wahZ=6>hpvF>-aZ>}evZ{6?G_}uS|Z{P21-`wxKJl6fr_Py)d#cjvjdK**Hap&{#UpM;wD1L1G(3O7Q8LfRMI&5WqpP#@_Ectb#-;ek1w%+Z>?L&k4@e}8|uL}6jX+Jun$0~oG5WX{dXdr*=^ENvF(>*u&^F;7teI~C6_=~k4y6x>1{yfP=+E1?UxykQG_D)*o_NV=Kf&M4=Xg@ysgTVMCcWXa%?~LI1;3vQOF3|tzggk50%OAqG^M}T3-_Gxh)4rWQG`~e^dgJ5F(|+6<A7`%iljVcs6F0s!KFLdUQ`4K@1ioX<Z{i~BTk{*kx92y}^653MZ`EfEKW^1$tcCUyR((eB<J4y)WqP{xX?(jrJ>RNN<J<LVe7k;(Z`Y6KTlHgnyMDa>SoP!e$EqLCx9Z3EcKvw$vF6w7k2SxZZ_Tgq?fH#N>8Ja@^x-Y8zSQ=s^*%qjMEjB3AO1?#j}GaP?)A#}_Vvp6_Vvp6_VvokZ(UD}Z(mP5-@2X{-@cw0-##C`ep=_F=UeBa@$K``J1*;d@s7(nUp(JBU%cb8&X-Vl=TSHB@2vv!W&Ak4H(%RVxW4`TWBca$#Q65}kMZs2A1{yf{A2ree*5{y^R4F}&$pg`Y~MWp7~g*Wv3>J=Vto7g$MzFee*5{y_U-)k^N;PD=N~VR_55S|=K06VV?F=azIop8eCzoqjnDIs@$Kgy+c(cYULNcD$M(JcT$-Zi#d@Ezee*tLeEWUM_Raf?=UeYnwr}2FjBmeB*?yY!t@kP0xBFwiPuaem-+rI6{fM=`{XS*;Nqc;(_bJ;q`JIKMwcmTd4tM__Jh;^FNAaCU8ZLFur;H<XKdtXMwr{Qvo^O56@qFuhj^|t7b8J6Ne(QUV=Ud-%jBkI>v3>JB$N2X59NRbFTa0gi&$0c4mEZoJWBYb~`+JV<o9{WEZ+*|Pee*rX`1bc4+c)RC@$K(9wr{@YczLYvIks=U=Xk#LJ;(OV_Z;Vehtj=2+P?R_8b8hVaQrmi!%ZIhd${G>`O|z4H@^Kn-1zqQaLf0;hvTRD9&Y*G_iFq!-@`3GVdYQrJ>2r`{As?2TfX-_+~l#phg-h)J>2B6zlU3X$f}1l-@|R+d=JM@^F7@1z3<^BkNrK|@=bpd6RPNWS$sfWug4V$_zC<t*J0yF@e^E!jUO_8#=@K3{WQyR(DlQ!-RI0mq1;>3^OKdD2K;E>2Un!GzVXfa$#re_r<dRM?e*>aw(s?4b){YDjgRpi{Lr229lswj>%YF<@#jf1J|EZL>H5X?>gV|VP4w>q_{pN$4-LAq(eFp_lLxPC4CFEESJwTHr%c!1+d4OQ{P~R^!Z-PiAMK=lli&7D{$$o~H>Q{0_;!Bd+xczZ%irwo4e5=K@$K<3zCAu(9&3Ce)#!&czs9%c*ZB7Q8b8ha4k?~Uw|*=?R&UNGzi;x#-k-C{pXdK8f13KS{gH>a1bj0Nrw(tapPtY77(e>Wq%Yn2u=5+=${#<bedlB_f7JM#U-6Nj%t&v1Y~PHJ@$K<3zCAvkZ;ekHpZ<HkH9l$l%EA8I<KwMwjgRr|@$vFl;}dE#`6buiSa`L2+=I{P@wfb#nHT)Xp<FA|Ti^I*edpeOlk2Cme*DwE+v}${FP87k3x1k;!MEqdDR?&B{I+lM8{f`v{51JT{I1_~ta(r4GcV4*?z_@m-}cS=kLKO&_Q$&JrSYxx?K&~OT_=eQLtWpgokQ2#qy}z1c>bo9`g%5F$Tq(p%W_12?;8B%cE2C_;sO1gYGN=?2tTrGabW#Wv385x{@Lr}hs^qChiU)VjKFaj-#I!Xczu{PGTm`Y<D2v4RG+>2cr)tz*sY!2=f~LBgY|pk7Y+6H_@SAfx_)d%ef`|CH1nSH{OI=M`Z?>Pc{=~M&JKV6=x9g3udcba-Ji$!$<^1k`|~7+?9_SQ;rDOy#0Txx{oEc3^gl9Sug)`cyq<6J8{fe<`J=s$==be8tpdjzZE#_4dUfLYR-G8%t`p<ibz*$GPCVbL6Wcd+5~`O`&)b#7fpLzPh-f`GbEkitjUU7J#<_4gz5bBdfpL!Iy+hA`h8K1P>Lh1XJ>Dtj^mT1^rQLo%gr98HR6k#*)Y0QQ{Q-U7f3M6QzaPO*9Nne+^KV_<pIT$L`|}$=hHvsm{<%l*x6PSNfqA!lbG-3$ZMFaP>Fxgh*uLpc^l%s5pRTjq`boY^|M6q^_WDk@^BV(ob)cKp?Ty^^V;q<9BlzaH;$Mu=>sM?U82`{`uj%}KBRl=$WBfS2$&(yASNHR;3%br5x6$J^a)Dmo_{&S^>&x&(`a4L$fjj-<WBfS2Io{ZirMf>22XFW1cLptU{iN|te*8$ioSXdP6M1%nUcYR;-Tt~YzJqV((do90de67nKQG3Q;hTQOTYjtaEa<Yu-%sO5<9xqhJdGd1H{<CvKdJjkp5!upT#0)x>HLi|>~Z_aaT!09z4b<aecFD6;|f*!TW|MXXs5rQ(cAvh`HjzbM#p8-^RVHwUH*D7eiYxUs{zIJehPKm5U9_WZqe(%^7U?i|3kgY>h*iy*yXPW<0qffzBkU#l-GW1ecpNF+_S=d|M_UfE!wWOzHh95dt>1I!jI#}$scMF)p}#_u0XvtdqDU9)TF?1g_<?c{$B%k`Nu8Ru!+tSxo4w)-i_~+*1p5ICF-`-dB!er=QnBQ5kG?OT~|v!r~R2H9RIu<KZI}QJz4yDz2B<E+&l?$-NR4dn|Tc7AE3AUvfti7z2$gC=RYx6k7pz5C)-fnALBFr&h?4f|E{x}KVr^z{1Co3zZa+Kdi%9*V85ZWAM5@PJi6OIFUjOgoqxz-*N>R%!0AtPzPeZR{V~G*>%<&=T+x~v{Pkdb2jA2~bW^I%GyOZqKaaL=<}tQPe-CvYzuO7af8vDBmp{`!|NI(1g6}=&ym49Q-_&idf4+<##W(Zi`Aw>B@Xw1g=_l<ss<y#DFR`IF^*9%-=#EdE{un=kZ|Wz}E03P%mMi!9=Ox-BpWe@ikN5iL*Y>^n?Nm(9Tk(Q>1Ltpt5;}jW{CflQ*tn|BGp%o6zwt(QYQNfb{rkR|NBlUxna6mQMtZ-e$E@|&L$Z7eJ#Tw^>c1Z_=LLQQ-^_13*Hb#reZ|)K^Efy9>-N#P9RK)-ZVb@=$UKgJ{1cbrdcPM6><^sp_)+|rd7k`XwC>N?(fj=MVEhoi_gu7Tj^6LkKT`ekYy2p_H@|B?(|N9x+vlGbCv}1D=dWe<`R66EW}$9>WXV4NyxYE+cV~{H>-4Rs_Xq0dy?uJWgT7zupGV_61GVp+kK@15$CY|-AW!Ip-*o<epIPglN8`uv%{+#>{i8MSxHbNHjBL++(4AlV`x1Vd?@Rb;zAxdY`To<qfa^y~*IE}iPai6%*Dq1m^&NBl#7}grl<Mzi^p5I!{f&3;57YyGa)b6mt*M7dJ-y#v;{)|({0P3Ow^+8;I?vx>*N>Rzgsg4!e*a0?@2`jCpB-I4_IcC&{(3Ne6yISU6IZ+H<LX&wjlVvPAHz5G8QnipkALI(sewAdkK=py@jYX7{u29wbuwnW?!W#04L{BITl_TNZ%rQS`%-k}RK4G3vjh8$&zZ0Nl}Fe3>(lr#eD6LoVWS?m^{Z0@^)Pyy9*32gR{QHA*7un1=Z&udeze0+dVIP}4%P{N4BxAh2Qz%_9#_^g!8*ZDW;qkQF5x>LJ`t#sP=ky*&&Tb8byBf}>&GAcAXq1sZ|Wpcu&V1vc3xZMuM^`ZcWB?#N#y2(dcRY1uJPB2@trB!H+ABC^|;P&e;2~HzlR&&{vK}o-uLQr?e%f(D0U!Fhex~X{{MX`Sf6|P=>A-CR{QJ3_{odf_v&QLFxO9<`+SYRPK@vTxIkauxX#3<eW>&7&%DZCCy6)a>V9Tf7x1IQmg_vF_5|z4@=g6jUfTGzzphL@7(dbV%|Jaw+8@*X*<JX6zut`R;G23&Hb3{Z|Gf6<2S1K)>c^>=@sQi!8MOoTWBd@lsUN3g9_@E(zuI3v#&<eu-_%d+w_4i&@PWYmI+yFYeq?`vfS<T@kL$-K-yWD><45q#{6@cj!1WUoiU#H}bgqH!=g3H4-s7`h)&8SzuJq4i{F7mN9L6>a%x`@98109C49u_XoB54R8K?6<xF9gU#*a3dADG|RGfP}QxvWxPevR+ooB56OTB`j_X9M$V`(}P)bx&#kz4C$iGJYK2dw!^MTCacn-<AG)Fn%20yPjmre%Q@7BWqxsjUP{B49rV1Q!dwc7UT=eukqvf-t**t`CUJ;vuL1Bl7AO+{pge?!MaLqt@AuICoulTH}@Sg{-NcMxqdS9cY*mezJqV(H@UQ(-f!=xf_3tF2iFhPn;WRB#Hdl)FL)#{U&c=sI1)S`2T#)Zx0DLhgYhHyrXCWHEz;}XKOiu_#t-3p&-qPP>HQ9UIB>ojKY?%NH(qU@9?v^o44y~$ks7@M^BXC1La$$IXkdPgAH_HGo6LVv*U!bj1K0UT)~mYzD{l|XZ{&RbBd+!v9-PPT3%Gvr#Sy{t?(4FyAFsY9Fu%5M=GWO#S^FFQ310tG>$tvseF!D%>HgT?|MBhnqw($gqwSmfV`6qI?KhqmtRKra^%I}e&Gnr>e+oRG7(an;>c<&8P>);ZXyAFk_z8UPdfxdBz291`1J7N?kJW9S>aPdmhbC27?XNfEI}^2U>MhoIw$4LcnffulsW($UPRX4*|GyW4?@dMa>3*)cFZg_pZ{Cl*`nmao&OdBG@H&7W!uOs7FWjIWN(SDKlK*8r>aK79zK@^g_kH{{zweto_V2TYa=3oH!ApVX*vS4o+MnJbcwex5Qzy|yce;M;;SYn)vG`GZQz!9HYq@^n_X&ab3**P|y*iopfIi;TIcxoO5}(>YAJ>MNYXfyMqMaTG-Z#BE!B6HH7kJ-E4D71=Ie%}ezfO!F!uPH-?S^W<`Rd?%`s2g&_%vP@c&|_F9;x?h{~Zy&{hn)l`#snA_IqyP{&#i%d9U=|gQ_QVe=g+<K5tmQSBFJc=>75@<UN<>+^F|k>RjOagYBDoNdCQF_oq*ZK%UU~b9%qo9$M$0cjHI#&Admx|6bRF`7Xq~C(oYOc@FA-Z{poAPF~jIyt_)E4sG9i{#ljln43Q_Z=HYMjUU1HzGE!UtJlx+)LMUC89##WegFTggzJYM-xmDNHm{`XJCE!Le3uKo+DPZ&yO4L?z&GEEyzfr^TDpGpYPR70uH#cWPxRZscS7Tb@V(#Zp6sUc4Ba01&K7MnNc*d{2EM078V=U}n$3alZ?Svgt{;E2uJ+CIq2+t?TW6H^3*Q&mZ>;S5y8pWy2EN}KKZNi7epFz#o|kt%-QyqUP=Pr*PoaK+@5#mw;d|Hre4lE6^1MC%d5NVgbN$4`S;6nO_%VF%`^l+8I?w%A1K<CRpS<sC;QN1M%Ozb8Q$7iNw>N$Q-^^FSxuVy<=XBt^eRBOTx<6e~0>29+*8QsI%lPKKX2lKN&+k79d_Pal&v@Kj|Bpd|@AHu<g<L;=vy=W^!2E9Yeqq;-{M9A!dqM1tQhNQ{x&`t(W6Qa|Gk@&{|Ge0~H!q`a)BUM+Gw^$j@gw-A9wI#-(Ca^3&duZfj%@kfdD^kL>nB!z;P&799Tq>1?|uJo*IMT})g|!zSK_g@t{+Qw3jAK?H0$8{$)XMQ_?X{i@Ev^bci4K*>iv$p7WjQIRHwJz@7U{s-xHmhFX;7qp9=oIR(X*2H@zJA9Wz>N+;Lt1RRh118s90Xeeb;~_uJZUaAdRpcw;%=4fx*uF2fAn&)wq#zyI34_xlUJGx_Vl?|shSpJ>1GpdJ2kNd7fTkMkWvb_DkO=WLz-@v?#6PmLeJ_kRDqvPjR%>TSW_$MGF}@As6;U+D2%@=@UTU)%TIXU{L!dEV(9{9XR+O1-}E&F?bFHM&2WVu9bgW2aN~e4V<y&7UWJYOP-XB)+MKU3<0Pefj3V`GxP`d%r)fI<3bo@8lhU`p1vpd+V<_qx;|Yx8UD1;D-j)*b(Ue=RfN8GhGk-eMM~6?}0iubz=M&zIR@Ka#iP_)n=>zxNP6+=ge#RxbA;1@OLS(5B}2oJ^I@=|M40>hVR{Hr~aeYKio6$cMi@wDc`vJ`K|V5e?1sK`D^XX{{Dx0-r@R*CtL3DAFu6u>vylL{f5nU`o}rerMm0KN}LV+eU$N|_}<?~J$#?*J2wk$@%KO4roQfH-D!cp2eW<ecksI()BCOXcHr-|5_dhR^A|k0HBb-xtDbVVv;V#q-~Rh~<J*5fZ~QdB?^JH$`f2_>CcgdeF(ctI+TZoMzRoo1vTVK24;jCH$7TNYljc3zT0d@l)=$PK>f^HheU|a<f1eetyEfha8$V6|@7}HZ`PE2$Ugw<S<~M$PsrDnA=eYUfV~*(j=6$fS?!WP)_!0VVe0zM1Z;y}jc8k;L<u|^a-}v@;8s8qz_~KqVkM-}Pjc@<^=+MGJuAg{kbYOgpAH{dar%mAhO|0Fl)t^P`swNfLLIp!Ty88aF#Ke^UjHds8CH73s|6l)CV%6`eR_Fii|4S@;tCUcvjf#g=2)AZgv@QIujFXDD(82Iz6+=|KhmL?JsTe@}0NN(Ajchv+?GI0c$DzI9@hYAt-}B^}L|bp#d($?a_Ltb7=ulYp^(whVUxbIS&Io*2Z!{W*N5f;#5%37M9m6rp^1Empenv$v6(69};aMu?vi)3g45iPq&By2m@T>IW6ZBK~BXYio_JTh`KS5uG`?K5|?FILSpQjH4*#7{$XV6~oT>3Bu9Sy%ke}|&8;I~x_Q}G5m5Pnm|AQkVR!{OIe^rO8WZEv!TY&!w%3r~Q@qR+ywsd$cj&ynkO+McETS=wHs{RQ?X`U))jdYRm!ec(Z?GaO&m8;K5sN5Z4f;qY*_9mO#ZXPkz!o^VeUJyc9Xr@}K;%whXE<amWX%QhdP)8LosM*^J<&md<Xv<Ex`O`tEseOZ1M?EyavKSv+>vHyN}J<%TU9QrT{9SOfce_ugo!X?!;sFaGLXfe3BiV`Why##H-g;f-xy$Ef^@r(PmEeRJTXJNDmd|gEi6_271!ZlUgP|*;541SE|_UNB*RK)`-?p0A&MI9CQq4&b~vX1c^;)yo(aV_@Wko9D_1^Z}<-V4h*jbPD-;HGd3v?ct!iry+Zqn+SKIPM1MgYXk7{=oZ#@e+Pc#k1slmR!OeRdh&^Zyj2@z#ZAoqv#Vp?&#Y#20sr!hdu>2SJ6yG6Z$9pY>YO6o3M`XJuKgiJ_yI?+f!&)xHDt&1lkUkZEBP6eiijq)I;xq?_r&K9NQxt(<6*UNBVFN$8ita3+K!b3guEUC9HL7SaU_ycDsslXnD9Mbx{qi4wqw{2zo1Aj`oUZWjI1ElhfoVqxM}^MNTvqTu8MQByT~s7apzJ#;E9nz5w@u%b;ap$u$}t&3cA&a_pjVjtNVDtI+2vjD<Ot>KspX+A6cnRPs%wPbPOR@`}p&D}1Mlsww&!AbJ;ETE#6Y%A#f93My_>Q3<^Rt_0tSR)z0myGp+8EBW?uCtB9GZW-1q!#;$wtJ=t+;=Qoe_rscR4a<9mI&aY4u$-@Q-sT8v%^ub~O2x>q-hL!G-p9|uwmHcAJkgu>-fT09ZDb##&>X%T+1WljeG)FL`dmy!(F~f4uv|_>8T>M|6{StqDUX(g%h6umx1O+EpC3=r*G17ra9Or5gyw_`GM;77!tfMzPnxgdeRLjtOvQ0nbP8;8l|{?I$Js{OMGI#59~Vf`%c42h?m=qeZuBm=EXQ1)yk%I<t)jS!JZK46v@~3rV;0V*qLhlfXh}F9S^&)t=VnZbqqo4tVY7Wnw#g4i&|BdAXaV$AxHNse6)oj!yOn<3il2}1l<UqEbUt%Xf<Bc(OTzCncgIi}YcuxwIp^|oZkOgdEO`r|$C<l4jA3rHFkF-C;0;u^7ap!6u3{)U41O7Xg%Exf9R_z(@wAE_Xm?n&C)@+>MF>B`xi0rBxo^pHiCo{FOwsoUd6uY4AE$)>*Jn8fxsJcjHAT+j>(pcov;g&3fN>J8r^e=972DCBKE97-(Oo{ihh@<nKCa8M=r$kMVOeymkL$5qk9`U^R?$?&A@qokA7WYbsE?blEPB|-jaU}_+Q$u97Cq?W#w<5xpTeK3Sgc|J`WgHMEZ%h$f2jDI5dI6j0sjTxME`_u!vCQE!lM7d>r`x1k;*=0-wV+%;f3%bbSb<DUV^TGm%z)>)$nrIK~v#W`ry#FaEk8Ve{hBrtvTTgaAq_&oEgrF=7qDu+0lG(b~p!`2hIU!Lvz8RS>SW3Z(phSQN?K$r<l*r;l*eYUJQSMo`JuBzeLZ%U&2e#AK<0%3iKkp0$z<?hF8O>=+AH}ybiqruY=d4Kf&wawdf^yExZQ(5ncnYM8ASXm%$s^-)3|@ycyntu7$V2o6t4zCU^t765ar>LYKj!-@|ggN!@=-2!Devguj7Lpo`!W@JVzDd=mZ+T@HT-pGO_|Jp2o~5&i}K4c!d?246+Dz*pgG=qC6Y{5!e<{vG}mT?PLNUqHWyMN?8Vf6KUBCxrh%Pr!e`H_(&t4fs#=JNQrdU-UfuFD%!9^NdTFYl3i2^fy>SI5&C~mJrU1UV|ls^P#`P62f`VUttO1T<8Tj7h{tNm9Y{Q4Z*q4EQD}IGz5pZz6i@TU#{<`3E@-dP52a?ME`-4@EP<!_zZj&mFwwQmW6*nGs6<X7tyS+gz#lFJ1immGnxaI5Wa$DgC&H2LbJdU!k5sD@Fm9PM^wg2IFl^v;d4Vcgl2|C!*CW@yyhyJsc20Iw?bRMt>89jOSlc(7JV3Q3qOKB4vV&fWANkflPnigQ9?xlLbwq9m40VHv%wkQtY|JcE1VO}3+IFjqxs>&a8a}%Tof*j7J>`WH{pErTl#yO%)N>`Lh^HndVXYnGQk<qGH^yXGg=nT3}->h!&%^L=<RSeI2T$O&IRX1tHOEV{Ae{eKU@&44i|(Ap?AWC-~wnB-`rJUY^pFG`3T|MXm(gM2V9KxilDjSB5)ow2P|3vmim|fN)hs3Ni+<Xgl|DJz_-Aq(X4Q3xEz`jE(cdc3&R!RyU?QWU2sjbI9wC1jh29G!*`>_;Je{kXc4#;Tm#Jm*MKXb6=2cF;8KiBb3(WodJEhPZh@ADTfi;Ra&SxdVYDLrF#I@r7yLLJLu<k@_$jnD{1p5&dN=$u+#Rh2cZa*7HQ;V=SF{q`6>g6{28%ul$LPnCgm6dnX}BZY8SM^thP$BM;4W|{v@6^R?tr$3JHSt%kHVt2!E$Yv>-epNa0G1wN8mDOTeu8d7JURR3ztXR!R6uG(I?^C;mT-7xH4Q7?F?6itD#-sYH)S56I>m>6YT)s30Fa%fUCfFptr$M6%ADEMfdyoL6$`i`1k>qMfdr*KFgwee0)F4qPu+@WjV?|g<n(`wQ(xOqSN5FR18w_Df$jPj<#v&r|@(YZ>U&+e(2+VEQ?NnpHdgcfhuBQ%`dZjpNe`aTA;1qrYbtZ9of!sXO=sYOZdEs!zzxV+u==W->Xy{LU+UcRom<IL39#)QNG!z_zC?Rmho81@e9vp`49Ge4m}FzQBhGvKKM44rC$eBtU}krvj52{K0!Z)SE_w1WNby>hd*R&r=ervN7Octs(28M!k?*FD93?LhvnGcWdConZ{cRlK`XQcTwFy46~)jnEMtC}<2%i<2@ekIv3?mH2p1+-L9`hBwTf?5oJ6m{=hU$!<yjv69p0eYK4%O+=QxGGRc!}UY)99_!&KXF6+O^iupG;ODf)Os|ABvHPQQcCu{=*jf_X|XSHicbsLfo9-Usgq>%Oi>SHZFm+1F+E`2#H5)?|Cpdhikzt5s}9cfsGw^FG`EL=NG~jP0Fa%>`LrqT1%Dn1#LzJ1V|Wu?;@R@?;g`Sx0m#JQ*E~z6%#s`zWNMDq00@siL)td(nH~spNePeF;9L+I~@S2t5J6soFkJF$4V!{!7JG6=%^iaQ_s&&Fkn4c$UgFSH&CX+whmFZHtQK=r%Z!qT3ds%i&`(2P)2@zrll4yrQBj+6|UIkD}kAQ()OwD*H=i4umhM_)$elSnI!V0~HUbco=;Q{#mu3XS?%kD_lag6$$J4DZ<<ce?}jcql@6(s%@!?En&@TSZ<=C5&Lh%zJ>RzZH`kn$Eh8|KePNZeG%THVxx+$;ngh5!*s^5K2FgT_+1%06${Ws@G{l*3EPS;fu~YOGtk%Jo@$$CR18Jqu<WY@`zyiN2v=88gF3E3Eeofra8&F-55hmIxT)e2`X^k2v8#$UfL~J4FRc63k3I>@xqOWCS@c`@Bh@x1tjA*xV<9|7we?l;F**`XP-kP%zVIUEJAsaZH>jAaVjsE&-cMa_K<B~-snz{xDttx7(G-1675yHT`8`kjdD^Z}*FVz!BW=RvRAf_84J`~;r;f{^+2AVFc6GD}+*U;$6;GlK;SSVsTeJ@R7`5F2Z3MrnqPvRmXkT~&^Y<#+9gZ`n6VQI}VinU=tUzbOE1B2D=rni{bG;Is1An7pQ&``7Mfbo-6?<vlOWQZpsYAO%n{ZgYtp2Vvg#H1i$ZuA(i~bJFbxy8#(k^-(&ZZ)(iVSFGIHQUzv}d7B_)pFgX&24Hy8kH7r1VGh->~KjD*g-W_Wx)TmixmmwEsez@J<zHRIEk!!Ru7)r+q(d!g8J4P5W-zgg;iXJglFUMCZY8shCgueA<NNelnN#xwHvCr($eaKf{U+hP$X3Li-Tfgyp{R3hl4ZCVan&c47UDAleMBrJ_0Q&1n;s`)zC5Thk_-U&S3Vj%Z0Zvx-u*m!eHLuZjw^SD;P!v^rm}sW^;YfRCuSn4;S+(k3kT=c}||rA>ITiXAHEp=;s!D%R1yj<&_zH}=rJhc@8>D&9`f?=+$lVR=TGMEfM#gys2V4()Sj6Yitpg%tfxBl;pN&lNAx{t|6{xX-*s`)joIXB*je0y-8RMBm;)XT$S2_EqR^_%LIeM1O}fF?V^;+u)kiMm@9@+?m>Y3Vj)VliHq)ehRPU+*yt8g5{i)bMssD3Y>v+U*4re<$X$6t|@YDk!NbrbFf^q<l1!rT@TAOQLc>((dn>UbLHAQ9PI_mHC?XlkD^gn?iq6LsEihb|Kr~D5BdWv_dL1x9YEK^a!-|e>q7K>_!!%KiynYChV?Zz6?I_Que^I)L4V^uD9^w{sGA|wm9RWV$$fPzx&fBHZKi*s+kN~6%c3h`x!<1PSVez=N2lm#`T^)*Se{EiPto^v(Yf$jY%>TQ0DsQD=b~$1IhJu8&p6J37Z|s#jM-L>OIV)eK1$K&q3GMNJbTM?%6sS-_zUJ{CAtunIhxKqi7tRwr08eI#prx^I@^pu`@+(Pne;<+BD_n*-V}Y^5#0gHId}`_p=d?;EA~APT?~Jx;#7*hHi{mBe^HSotlxP>^TF-I`q}Yev?nZm*hxP`*TTQ5xS67_v!d7FEL`vNp?TnOVg0N*6nz&yNna16r{MysEi3nktlSfXFK`UMqkqF6Fs`G}zVJ=fyM|tXORHR!xZhObeq{I-mT%$OCoIoz9T*eQ_OKjp0gkl*eH5;*;_k4%SBlnxYtvQ}y&qmp&1^)M!7}DDMu*UI@Iz{w$HV%*E85P-O<5Lg1~1_pn1fD&Pcq);&?Nk<+NM)jKQoASf!ETf-RL2B9P>E=jl)vgQlm@JP4EEKHX^K_KSamEUs1oC&{eQJn|=}2&#j^hVEK+GeeH}s2hUJ3F|41RMBg&Z`8FF}3QNw7<lV?Mbpd_rPya**!!uQU8P?BXqRV}pU|Dn?d_=_$Vf{`gdJKM@zP^cm3~yDjEUcd)Mc2WS^Q*A_P9(YnPO^`K=nhz(6XaWJA9Nrr??dwbd=xza_hFs>=$o*-59JQ)d!1-;SdQg7$0PbZEZ@-NUi%rk5SDwA+?(WGOjO>Jh3`^PKCJJnqUGQZRlF9~-xx)Q!SWs^@73AR-0*C+nU1~#{}tBn0zaejZXkR)te@>qp})ZL?r}A&-%CW#`uH!F|00L5yklGo>-P`QOFq8L@?~-hA6Kz0tiM5tZh<e*b^<*F%R2j6PjolDj`~=GF7@$DmPKdzcs|Rbb746j<@_6jz5>gbk7wLPhr@DTmiy%9l>gl?h2{P(_tekP_uz@_;|+8WEOT9h`4+7XKcS*cSU-P>wuPlm<-YzCdJL8tK29AUr%hPSd)fEf=o_$H&*Zw+4ebioRna)C-`hnS!cAyvgw}zj?xc>3qw?$}EH#;t_KdXUW?v7nKhc)((<)vJ>-T)ozOby*ob^Oo!!I&MJ<vzsx{PUK^e(sw<69Rk56gW}?t8bR6<`_j_Kdq|2e?i1lyJce|NF<4&f=<P^0rX#aV_-k&E`M(J6d%G>E5^hGyH2yd&}TI%k*#AO6BtYk!G9bncTk@39J9fKWLjT|FSLge*j-}arX'

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
