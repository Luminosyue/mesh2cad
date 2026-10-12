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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_013.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_013.stl', 'source_sha256': '77bbc3d48524a743fe3ab90ddaf135b4ce2aa2d528df023b3ce4073e7e020fdd', 'input_faces': 504, 'input_vertices': 379, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3328556716442108, -0.1822034865617752, 0.31406736373901367], [-0.24531963467597961, 0.011258929967880249, 0.47181159257888794]]}
GEOMETRY_BASE85 = 'c$}qs2UOJ8)Anz%p+*Hn(AZW~P-8(+Br387OT>n;f`!G14GW4uESN=&HL*sGEv_{dR1y_2wv8<sV{F*l+Dp_BW3TVdJdbbqzvunV`Of!w&OP(Yvv=ptotZoL_ggixRi3=w2L4nq=8O!g>0Ze&WPD(F8_99QhWGzGF0tm|gb^mgLwWi0Ue0dYsZC^*$w)Rv1@w+f{CrqI19L#5J|O|s%>jLe3>!Wyc5uv)VZGyoZyq}^G0w#&_KQu3bLmxr>VI6_98|TsIo16C_@|J|1!r2DQ@h2NdaL$`v{bEgIm{&;n;&G0Zu{JQw@9<~pNqm<$6Qn1;a@=K8><p832$DXsl0Vbn$EWkP0{(zk{RId-Q1<~(@SA~`z6X7`G@b+b-(>k=UeJ6fc*{L4*gzo2j$K2lQ933`!6a>M8luXW0iN#j@hp3{{G7awUhCs^5$74ta~~~dB@=-*dH}5OTU*iR(WU6XYjL3bM@bd+oJXzBf(qV?ZW&)Z81Lxyt!TDo!IXz<*j`pVgK~et@^!{jg&X1wuS#m!{L7^Z|rMTE6hKTqy9UmCF*?p$mUo#bLBRbvsx%`>(&@~dDrtN{oafi*v|?EU-%*7KXE4fUr<kZ`_6glr#Ye@;`639{Mj&li}Jm_VSh{@=Fd2%e%hNxBF^Q&TPkkcq3fP&kNw`Q1^+#KH|yt}%ESNB)ez4C_cf2UmEXe76o2@+AOi91Y9O9%z#G5RR6m{maq!=*GUnfUs&Q~6`@;XR<-m7sfH>c|c3$~!%fg>#%QmT<kXPVmmWKZ!Ia&|4pbpq?swe7a!#ItD&3;+uJAW<+f69$mtM&%&fSru|u;ac>{j_E^#J&Q++ska$_}G3eihY#>Z_CQ3aj<ktLmf^wV5e_!&AX#<akXRL^yVb$?1jeDX!EtMYi{sTdB^o^jho@|i}JR<&y_ci>4tp$))H~cc>+EyTjS%XwGRG&^;mhs_*>&+|1%u%bo)nn>(nM$sOOX5w?8}y|D#cF!6}GOfqUTh^~g~Ez778P-G!Z(X+P`!_Uu;P$h?MqHSDH+!?xub;&AOM_!yh|<LJ)%nFHQ%^wPXI2E`!`foGMsEW3($Hd=}LZ+8a!4Zp2^8e^h$zT@pF_!-^}`R$DJYrP8Iak01hZ`l{C^R2%eQ{L|P2zjh{UFRDcz&lS2)A(4NOORjBqgZ$CIMku<H>j(Zhp=v^r8w6f`w`Eaz1Y{YuBhjA-@*QnJ>Wl1--CS3$G%oL;Lp8oI^Uc+2ziXz0sk#m(4XBhU_X8<>@>3=FDZ89%h&=t16v^u1xv!u0-M3NKB?>4gML7Kj{k%>ABotB^Rx|lX}^K~_tN;7TQ6t-Oh?{r5n6}Nk%Qp>n04Uyl|tW}Ukvl}uYsN84)AHi!F#X5z9uhMf6Rl|!q1&65a+>fHO}V4=s(VJ%Ms^kEwJB#X~_GIWte|uHTq{tU(7$h2>aSP#IE0)n{`g-XDtNZ??I;ee?1869-WW8KVF7=WZeqHA!io+pBsR4(d0+e`P1pJ)9Mpl*E+f^{JAw5^Ur5sU;Qg1KK;jGeu+LBPy0dk^LsY%Asy4z&r><-r{O*tb_#9Mb?x8G#<}}p6yo5qUi*e)=_S;&&j`$q>4?7l+Yf5Tnf?Xx-g_tFpX!hJY)pZjN|VqBs(PV5S0=%qlsvkw?YpyT$Gil*?eSck(>dUsHxiM@ijy>7w(+mkAA4#7`1F?=2dhUI>b4YkBYA@QV~gC0Ixjc~eqL*!{lwboG1gt&7kRPNR^ArxfqZ%Pg8lP%QO{|o5&y_o_&MX$k1AugAf9`y*jGdzta~UFeW`v7?5yzAeHn`~5zi$(P*;B%IH#A~F#j{~wmY$SE}F9o{i=Q!_&IGU_WN-&%=hmAe$po^)z0%z)gMb>JH+8(39Uo3?{d`Vqt=+;dB$>;CF;ZfvfynQZ4u|Fb!XMjM~&g<H^sCLZJzXJH+XBEc;tQe5bSGWDB?V=ApEb3b7b!i-ZJN!#?3PEwXSO~)d=>N*Hr&)+q)v~gFc3xR%`cye~EKZJ_P$3a36M(65wZ-`iS$~RO~CG8TLD}7WnTEs2#%r|Bbda;7^+;t5wGP!k;SDvF_ZiTIbHJQLs~_3gTnhf_1Y|pGGr(_;X|>`pN!b@W)XZ^P44Td@Kv@<9x+efIkJNqki%>*ZH<BWnkypOx)wvDu_c`Y1lcKjd&)TQ0J?CkjICu@x0yl9`bUi2<&W&LcQ5aA^!2?zkZU1^EDX$EGmdNB&YqLvhaEJ$376eeakJ4kE3vH^~Yw(hxwt~G@jO;=aBdBAD_^9ucj++|J{o7(&JC%ZA1S={hVor^LY0T=J!m*x?ldS>zbo)D{uMftom;;-9TOvFDq|eFn68W540oB3oj{eZymf}?JpaHb(>vK-WXk6{kN5vr1LFJz+3VyTBDzLI-$JbpRK&rI}hq@))Vaa{xPiUH(q(mUOcy0OCJP(s20}s#PgNo)Hc|k{}y(R6h)k;XTqO~kM?QaQX^q!$0n>h<|Up7`VCQkoGpHY{Wk^R|M#om|BQ`@=fM=U<CqtWc+S{>crK37_*g#ef;`5hW8LOy%G(0>BW{1Jh5Zk%>blmNHL&i})v&+ll=cm)ZT%Vb-|t)4kA94O?W~Nt%ASS&PTY;Y6t@z6bvJlNe6v+Lzqlv-sXPt#&pyEYmB$bM@1FvGNHv_J`D1lm=X~(akbAnW<MKV&Up5*1g(&pr%+WZfUrvCXR(o-djy8t<USDDUCg$aj12|vZ$6@~S&rnxie1Z5(9fQ17d8~Hq;df9ErIWB<Q`!=>zxNl!CpiK8Eo{;KIubuZJTDAJeZGoYru>Edm>)6_>!!vZP(CLw{9GB2d<|@h^Bx+4`u84y`RAVE+}Y27zuOP~{P+|4K;zxYTif;mU-&DX@5~vF{Z;{Q?tBn&NJ74xcYDJB#ILchSK08hOceO%r5CC{#ioK^*Acw4ukOoM{Q~%19l(c0;9g5vjQc1Ayk$ooeXcNPdEwlB8HqUOU5h^X`UUtkEigZ`8rI#kK<(R4Hb)+Jy<4jMunEdr#)CI}JdyY68<4NN;qa$P(00VtA9c7o4D(Co*Y^eE;xe^kPH2oc$BaTBJ24e;4hV%muODqt|2yo)y58W8L$%ParoKfSW;VpS_nYJ1DT;f|a=0Gsw@&&I@jeVYb7~<kmD~_dAMDq8peE`k_NK<undF0eXJA#>S@J;pfW>z(_FL8;eg@V;J*@v6>mDz|dVYre&TOD@aI`HAepg<+@AO@*>sqgWh&WfMp!UsMLUF!&l!8Cr;p)H9p(55T3f}NKg6G4jFVv1>r7!#(ZPWZZO!ILrR(ZqEq+1$K`?kx7+XOGzZyAN>ndnx?`*9EW`S>F0%BL#Uo&EvhHra~zpwtJab=^GRZSSV({o<(A2L4zJgLlXKk>T?kacEu${JI*5^GH1ZSh5SkpF(r+Ui?R8#Pgs#)(swv=YfY0;D5t>*w->YJjYHAfSo07@c-~FyeD45y7o$MkE<V9fj#x}G0Wlqo!7^a-$|MH9M2)P*DsZ~cb$oTSnVaw%PH{Y68p5y%}bKukA-}v?s&c$*AsC#@>qFG_qupKZ*fJ}HP$|YKOs+I^z*mt;ZGg#wk{KNzB%F!@_6iT%-^~m_j~xSI^VfHM|tb+=^B6IPA{yR{y=%B_ZvL_eEOU6#;jZL=T*oG<pbQnm$;7ot_jfnn%}O#e(#(C-@Cm&?>X#ubY1JF)7bCSD~Mb3aKvo@c#Gp4`uX8doVy~Y;OCLDxR1{Nj_0wzPQcE|bBNECO={m(AG|F+RQ+^}E{?uY61?++8n|b>7KHs*$CP)B#dESbdmro{KZ>}O`5pChqb}_9IRHOL#p=H7e?7yx9l<*a?9uaOw62MGhVF+yjmo3X_uPtl3*8Gl<M-=(jWg?O<S}3m=D)p(_nqr0n15vl><4Vad+3>eP(R(aWB#!Y=qKw2;k<m3g}7a9tMRdiU|;t7;2p=R;CuyoWB$*X*zfG3=!YSxSa&`7&>)SQ@!X01zS)BO{*HKBkDJjCJu+bb==b=&!YdVgKsxd@XfpC!VYu3{oLGZ69NjciWl%TR@3$KM#~(l)UhjZD^Vd@Nv-~3bj2RC9TY|Uj{2BY2Zs0lLFFWGndmQ$E?TvFZdI{{@%QITzf4?H?v;Ftr2QNb(=zSS^*}V|;^BQq*{`CZYj-QA5&wf=qj=VLLH#eIL|0~$=`_jY+JU^G7g1G%tL-T9CUI}rSFd6gf`s;JAwa-lW88H_AKVOdLfgV2C@9Q+Id!{VzWos1bxoRrr2OM3b{`3gNzRcjw?d{lCkLTFe+!Vy^hBtm!_x8d3y~DvT4pM*20qA?yhTt8)<*0r8{pRqqRU-VUdsCl>t@Q@Oe)3T8553X1pM~Lk^&WtDnoek6vRCVj`R@I|hx%xLaNJHp-R|p!b(<{2bAF#{uoG<szu*DhgI<k6UY>TxexDUao#bDH^Z2G4;_T+7@wfMlM*N$DH!A&r`)gx$^s#Nxh-amLzEgh9yHi@v9lK)wqI+6bw#V0%x18w${(jMk8n0bLmA8G>8Fo7R&r<*I-cjD@0p2pM>U_07Js<orb;A4`nfU$celf&nR!7*Mw|Ij3(I^G$o^B65B@WL;f8RuZI24KfeiVl1kd|-Iw-17M)+)SFzjq1e&iJSe>|8vk>l)srz@KS}ID5ovUhGCIzOS`_{lHnc?*gab`Q%Ph#6NQ;=9eD<|NjogzDg9)b*+OEa9)anH_Y3ItKFuZbzkODb=jBlC~qGSjrfnNgSf44jr+7P`k`ZXE$l1f$9?$TN}P*HHQ`UU_S%>1@kcP<yBh2~T95a{+V{}sANpgzUxnkn<FPyHe{eb2saqa@pAym(^;V!1&UIuNJI>ut>ZhZI5BB@!DSi(xc@XPPDFOQ#t#Kc1@kN};Tguc?JLdE(<ad(??0h|3pA+o<`%pi%i(%bAdubdj$F^a=gYzRVd#31oOPfDXha>aB|2b7r5Buw&KcC2p`Khb${(I4ZI$4+p{&YkhZPDq-<5C0sy3u&wanFRETHqayXZpLn{lr?>dGY3$et%e?_8+6@ZR{)YwerpnBJf;VJ{@+9SIS%J;QhjOJPGsLyind;=Pll^>r6zx@;(Ru@-ChShK$BJN`40W&)({DyLI(+*s1*(_P3SUg7d<A!R;T+pOlLGwBSwf!yhSc4DrPC%;)nE|HK^St-Twf-h%MFVd?h}`yI6ae=qY6@5|OQ_mp=;_1E`G>nglQSgdz3|I|u-|FT_sj(mmP!M@rBY2571Ucmo@H^BShcQ$j`Q{Weax7OaZUj0vF9sc3O{C!`jpSJS`>ah1Eth**1af?_7z8!dnt+4i0`>aXW@2eAt!@H9BU9RnH_&Mk}>;xasb)8lBf}i^b?7V%5=crETdp5Tti2tK7{Jt@-GvYA&ci5S_LgQdB;DPvO?Z^CpCU{Rbhr^$~d%&-Hf#;k@<6&pyZtzjwsONey;C;c{+`8#`w|r9$e4&lX+voN}|Mx5g{<pQ*Z$?L*Z)~lG_&i*LeI2NbI;`Fp^BaRVZcWGE>owhs{q|ddb+3)rzUR1&K4xCO0QFWaPVHD5)<EC>{yWSc^FrfnHu)oux8~B$b^MOxUI%==Ip7y;!@m69;G8DS27lK_?+f#TuxveF!QdU9o_Y^D21ekV&YlVXZ-1?RnvV^D{~6OUKe7;hmzz-w@lTir`xjoJpIGo5YuG2l&ea_Fna~)1elZ$$!p`FPc7GuD+j0bW-}CzWjPp>A`e{4aA9;yshkO4(Rh;Vs;2q!P-;eXr0e!f7Z>;P0KzT>0Y4FDp4Ld_W`&I2cISM{G3U-cP!h7_wAn?b#;=E*!z<bleYgl(<3(S9h8|U3Ui}xmY`=nUxYh1SS_V7<|9_wCLf9z+M!A?p;)aRAA$XCf^@XJ0%J&eWgkk-y_cwft|f%#)1^c)$bk7;}??ZDdxHpczCwjJ)N+kS{cChVBIe2Mrt%VNH#2l{aLZ(%2~H1-=;TF<Yo+n37Qy^3Rg>x1YU0Wq-C&J%ume5CUoGbihO<C|jOZ+WYITi{aVt<T;b)p_^V>VB;U3*p{x0^Zi3DB`etjn;|X{U+v5yo~c@sfl>by8*u39{es>xg_em$YJG;+7l3md&xLo&FspXM`oy>#)eYZ@1Z5iTU#UVmO&FxpP`fBPvJy756oPNzS=tt{QQx44iBHEytQ<q@|GztV5b`U@UlM2+qY!H|3lxM3XA-Ye?>IyUfb*DlJaV57zGV)qfczEe?lar{CO|`_kTjvzwZClKOw3YSoi<;pAhwM`4H(E3tc14HF^-wqnzv-D|2z{h=pq{apLzwiG>R%7OoC;!Qb<{Vq-gX!H0;2%ODo+Ds{mxiG{mOES%W{DSSQ?^sD4WuSNL*ab-%;Tj%0r)FdY|f>>l*Vv+5MMSe~!asaW&LB#zjMK5Ri*WcRI1y>~&?k@Kr{<ooBS*Ig$8`>I1+agC0e?ckwNa}*K87qm|Jp;Pn70jXJ^ao<$E*bDceE621PbMdy-KV@sT%9qJm<16F*U9x+GV7ohv2b70-j}X1g}UH4#!mLxhgi4^^k4k`gIKuFT%&_)#7eA)h5MAc;Kszlm3EC_*Qo3oe#E6Y3X>CAoY<Q+A$8K3d6FD;qh6a*^j?&`iRUwJ62B(QuYA9y3A*5MuFppE%#9)zZXk8R!>Nzsxsr3%gz^*OCd9#%9}@=?SLP7hfU+fVCeNIl!A;Z!mtq_w9(kz?_8}Io3bAl?T_eObTDe9Tb-}$|V}xsrbd6|Y;hIwyY#|n|8ow(x0;vmb&bUeZ8W0Ot(uA6pdM-dLoE!ZTKYuk)%hE&kQ5WoPLXIWByIEUOSHBz31t;(f$vI2mxe~nt_ZQ0{IEp#!&zz<a_uvrRnKFtvir?+bA-Dx)2yqMI`jj6LPd89sa+XSPFS4hj+@tLE9|LDp&T0joPdS_N$Bpq>X5b9US=_}MkXmTSz9T)S8S^bMt;L*4zJ4~)JEU(UGBy&k3I@)eoI5Y(QSxc!*_LyChdGmcO=Qd^_U#SSywtwUHHNxIPuCbsDf;L9O!RnS;RX;3*O6GbZqx-gB^ItCv2Znsh3if%+$7o&eGYZO3#bb&&+mzyO4J31Qx{x^Shz%fU%tDXSh)4n1%E+Z@Gr!|Ij9T%k-Ff&$cz3b@n0No$%%YST*w40TzwPtx8y}H#Uc134#6LD2)1wtj^Ys9lQNdL2eEL+=#%()gIKtW)CJ$A|KevWt`Wt0Y(*SPyL~B#5)UU9E}2-kZx}C$)huG+7BQ!i%O9u<K1d(Lm#M6QN!0K2bCKtW%QIdd@tl<>?!^2{y~#b;iCE6uP}=>9ShyJOuP4t+3~>_u761Dg&;<v%Ms3&dca7@Q1=k}Mt_F3%`CP-@HHsMWa0<N$rRaGm^AmfsPNXhwF-MZC9O7FXugHlsnSkdrb`rP!{GR0Z6tQr944k*NuF;jc;4Z|%#SjZ8{YlP?oRd|=!WE#u;<t%dI3MbQi%}O`!ZpgeMp22EYeJZ7G&SKaYG<IgG$a<zLOq(_lkb};OA?o(6#X*yDSJFYUGR4XYENo#Hg&;n^i%wk{w?QS>TesdaBmFcLUJ;MH6XQ+LM&VY&%sdMSwnda+A_|KC~Fdn3?ObqT-87g)#hGnlPgOZKrHe@;<Cg=DL)_<S%_HfEE{V=?yNW5%TexA_9%CjoGCe56?l$<cxRayC%Loa%*c7!#X680kiILgVHG(9`%)Gm_9gb9bSExD=}GBM+>AMq+Ns4FkXn$tPkM#)j6~jhLwWbfS(7v8#hQ?Mu<|U+nf{4+m;6s;{v>yD_erfwo$qjsEv|8xI6apx@(krp;xojLD6bKVtYP{We`ta(LvS!<MdD!M7L<*MMYbar*;t+nI0T1M1`><(&xQS{*L97;u92U*U#_z!vI}J-aTnr#9Pv{7lu5)Q2fD^!jt+8;i3d`b(UrX5&!~&+PAu{h*9fPqmJ3&*E;1w+u18(ur^F&FxkdnomuvVESIVWobLArsu@`k2o+j{ui<qE`tV1lasB3tb@SG-hVn^zKyT0?p04_>h#tZU-pHdfD*7PqfV}jm^QuJc3QJkE}Bd&QT4d7zA^fj)rf%r%+UF3Dj^TY*Bka;Q36ASO-8l{QzQkUUIUhr!Jx*PEo1M)2Kamu}vXNjNlvj>!WiG_dW8q#2%lY7STki1|g^@qf#DGv~f%*ur~QqLk@O}T`4E#*?mCB$}qHkWcK@icxmfpRXf@TsmbmUsen842VC_obdd9KjLi8iP27xyBgcxLo>p*O*B>ESD~FG35;6#l(9kHxo-A`^`Wv6S<XG>g8|Nfyj5n(oY&O=OQZ-S7bik;}5BeyvDrAy)Ewqa*tQx8J1oncGqxCKk{Mh6Y=Z~@$5MrD8q=uIKKnsXT;A~Gw*9v@M{jiXDRm*%l^FR%Xwm{^~U^uAcqfq_TlG#lwQPs#8o)F*oVB>X9SOD?k6xu!>A8qep4y?5=;Dxu=iAAFRMr2+A$9jpMH$ZX6A7Z$5!T6^01S+Si-trN_l{IDe+wTHi7jrf!qwr1H?0kH&Z%^om^)#$20ozj6Q7T*vWbmxrJEvTa^8^D0^!W=C?a@EVYrueaG?4^yPP@j-FCVKYU8PSg!uriCFrt^jhh8q3mbPC|l&h!PKSi)Sxa{?r_oN?vcAQoU$pg+;?)n4dD>{{tk`iyr#tAlwFB~xwgR}SbCvIH)4^}PX)j4vx24PNH17SJeIo1F}d&{>Vgxfzki;Py}!RZ1L$)<?qeEl+l_zw=KH=X_%x-R*v|Q<DfbYcCVt<;1<PLdux8)KSmYT>;m`2%9mFCJ6N|6D^gV=F@)OG3l;#jzkg^(aHO?<cnTNO_vD8UqE0dddp8wN-QU3RjP4f01|6%!me)B*7S|ay1o4aiN_g_*(w#p~(P_74UH+?BxDsKhGe*t%uMoj'

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
