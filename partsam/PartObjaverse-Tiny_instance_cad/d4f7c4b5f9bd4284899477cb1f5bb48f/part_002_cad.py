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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d4f7c4b5f9bd4284899477cb1f5bb48f/part_002.stl', 'relative_path': 'd4f7c4b5f9bd4284899477cb1f5bb48f/part_002.stl', 'source_sha256': '2eafc12a0769ba33371b001bbe144583afa90ebb854b82a808572f4e48d0f06e', 'input_faces': 1371, 'input_vertices': 973, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.1128796860575676, 0.0929650291800499, -0.4881383180618286], [0.11288180202245712, 0.433490514755249, 0.48559439182281494]]}
GEOMETRY_BASE85 = 'c$}r3cbF8#7p{AE4MYVLL{J<sp!^U)f&q|`q>_UmnE@n-B*{?*P>D)ZN#cMcm0%zTX(UHQavo4rz=%2DK3#A1cGb=w_qi9J^L+1od#1X&QulQCj16jMTy>+P{uOnK4!&G$O-sj-$mQJV^zYca?=u}b_9@k)*Pt{fkMGMrtyAkYsoS7=n$zDIQvB(TeLD0m{&1vtrA`kPFBvJ`sb}xLz1#I@+q3u69mTKNu3Mjup5LcSyIvi=*LOekK-rR!viFpX42%3f{>$N2A-U|rhE1X`-m<rfr}6J{p4t@l$L8A?_G3$j`Myhj^v91)pM32{mOf{cAH9_Qq~Ys){OG&?tT*cO_1F`Juj_;FzWu82N1m;^O?>Ba@snZSY5(0}zkK}I+arv8_nTKz`tggKPlSD4j`OXRkMEM7SlrO8&v!qZOy#>@wKejCdfNGVyI-sP=;DXW_W3fK>Ff5vPcACDKHOi<&x1}IKKa^@ElM-n;rrUBQu<$Bbt3HR`nz_%_Q`h_yt>ZM*X8^$^HkUm+U>&1<3_$N$IjR7rt{y*Yn1Q)c=A-(*X2jQ=ws&VcD`ce<HyO5%^kKjTz>RQuG3*Zs`u;jYG%GJ$I1`dhx|mM?%HsF#edCx#_)Cj;wR@EUt{d=l@h1JzOGO7^E;0l`FekUGV_D|B|kE|jPEDgw)r@`UG2Lu<-0>KZ3_FD^(l8c?Cbit=L?(Vcl&f(%JRD_-x+3>9~oS1SE_txi1O|H_)z7?{=DIAm2iI04rV=rdH1<l&q(J=NB#O++l_TmeuVO)*OpfGKd$QU9##3;Pn^IX__bfp*o<MTQ}w&;2lLeOgLN3+Ue9e`ueVw9Sy!|8tS7;Ct#N4kS?XyW7lQKb<BR2Isi(F6XYr}0b4|~c{@?#ysrr3OzcW?B{?k{E`2B?+o7~;^Bg0py@$-9XUyq-_@2tvkf3x!O^>~PkeB*t;|J$qi68mM_X~XZS#)I~wt(6}+g+Fw=?<Yr$HOkTT41CJbex&|jvmEv}F=CKeAL^-ndp-vFR{6GXm*aN-;#hdTXy56n{9wKeYyO^J&u-<8h1=8ib-q)osq#0JJr?fA<j;+k`{ggl^HI3|+IJT!U$0k*AIB~8^JC{X`}w*)-}YWAe!TNXTf+Nm`!Op&@!ZqfQ{`)4=f`I$-z~anOSoUOA300D-mkCnElD*_oG#b<ej?koTm9`7-ER2tM^wJ{Bh_;GezLU6*W*h2_IPtIjC)s&hXsB+$A4<z&+9Dy<!UFxe!R!+$5Z78zRo}P@M2%B<4EH0;6<tCOBP>`hc5^DeyqImgLbg|$S9ScJea;H)p&>>yt2^uo3%dZzrSZiwf^Bpnkzra_;g<S-uI)0l^@mp75Pr(A8qCP@!dJpx^eK5D*tW9C;R1ow$AsH+GoF#zmM_#*t>^53zwt)NX7-D{N#a=zMp8S@^$^S?>wb^U4QMnEiN2Pl^<z&!Pwtuf6CvX%F+9)eW&LIqaC83oL}I#>(XqS!uyr@ZKUrfe_ZCzyBPgt`%(JK*{}Rq+xLul>g=oK`-vwT8vCn#r%6L&e*?dDmqV%YWB5V-k5Bl1v{gf+{k0!yr1G^N&09_FZ=;50``|~uQ2E-A?VdN^uaC7}Y2O|v+PBAv_U(2K^6m4t-BaeL8t2K<6X&NIxAC3#t8$utZnU%Z-4;j8ay~8N`_ZbOo8uNg((Q;*zO$|BTYfo>jvX-i1wYbQ`9Z(nC)%7-{nf+FciNsa`Z0bv>if~DsvO<^+K;_;&ghrqbn<r`Jz&&d`(K?i`aQNapQ>k*9!C3UKi;agG2W72=T-URdYJ8lAHActQGR4&t+{?Vjnj?twI6A-+8oaZYASzfx;bv~qlH%+<vV#NBz*tl?gvu(-_$;AjE5QHmEW_6*`E0E9V$N<|Ley2exzX!qkpv@#}C#S{Af&-qx)C;3GM6iu93Co_~rbf&MV?C)H)IN6Zm@l*M2hhML#e8@4F|%zH^=Ob-vSi<r{u}!};d;#E-SjZ`3n6_dVZ_K0MzXKicn`-)K+wp@wf5^?&I6v9O=q*}^|=MmHYu>lN)-L-{>8zdCpBSSmk$@vxDf=%vchzVq3DnSOoB++_B<_J_?g>glxT=lf2Bo6L5=kKqUN6hF~!p3y!*Iql~e{h0W<ukR=K6fnk>_T$gZGscx$|M2U6euJh)eYEe!I+)wdx5xLRU7MQwtNrR7jQvf{U-+s&ZV$}z&;Q*mWzMAX6Mw8#<FJVGvy4OhEaMPA%Q(ch$6@rb1->79ezy9Y@|&uUTeh|;=Zm67J#AmtQ~R-v`FE$v*M6{HHEO8+;&Zg#uJ$AG0=o_W(el&$_8+`tXDUB3a-5Ox&b!C=6U&$GH0opdLH)IVW$f;h`S?0Ny1V?;RQ(lwvyAU2Z&2+S%ePLgW3OGD;+IpbjFGSX<nU{Z^4&D$M@Ap{)EJ-IUv=IeSNd~``{9?qA8$~`*lyq-QRQpjsdPbYx1K6Ln0NTm`pOUH9lqQCb94OTM>;59f6j77o>Arer^*TD1%70?s((zM=RDj|`GcZH|7zbI^{dgpiEc5qUpGH$^snvf_SC*J_SfC1^0goI%O77&_S>h<?wv+IYX8q?jrNSjzx4e`wcW;c1HWx|vwzFwSLM{d)m&%r<Lzdf?L051@5ipa)m&%rBa3F6>wmPxBtQRBH*=ihN7n2%>J#bG*!SIq-HiR!el)(v*xyKlKPUR_wv=%mAFk$O+D{Y1<3FBH`H9#i-%kuUzr*N9{OF5M?lI=??Pq=8J$7z~F&`~I*f0F}t|og@<!fK(Cr7qXe)bwh{k5NLeZ}0b60KD|FV`^kOZ#rcD~9h*JNmL;&WN9Ort;kd)pv*eNcUa7pQx<z^>(%I-lOsZ|F@nK{Qj+6$m}ot=%ritg#G0G&-#Aize2`%2>fwHjP{8<QGL8$|5Xc(`fEShYqC-QWbTT-pLk-CQGe~n@=P)6AA2IlI6uGtG-EtyKl;)<V?0D(&F=fof>(|4VEe(m!;k(mcTcK(?Fa2p;p}MNf1-o2zuI?CA2R!E(r3P(xUGZPU)q1{klA0O>nOkL5u=`g|3EvVK3+qp?S7*2gLNA}`BXcjf8!5yebKLfy=BIFuKfgl@c9Kl)*+{VT~V(y+IR8wdY)*}!S~}cml?++?K^MfFs^?lZ*Q#XQ)IcZ{%b!nN#zIYf8ph${O!J8(r8cZCqBus$7s(si&g$_CC%}PAG<H-p0FRiZ=CN(>;GZ2kM^DRuDRY;kE?Pr{xpwY_|AOSIDW-T)l&8B*TNXj+K-MtWsK)!si>;|Yb}iNZ2Q6Z#E<7Zy(d+^_JjOk%|`h3{A=EhRDOKXG&4V~q3_2k&o{=K_T7t9jqw&)adw#Rzn@`_fBg8$vPOS7tycSfY)gjGU)py&lr#D(HtEknemVAeFMgKuUi@UekNoppw|a$BVc)5*e4X#E{$qgOFLfR?k1v)V9AEIArvL3pm9PEG<Iy4CPxgJ#7!TTaM>~5B|C)UL{rurCnA^pV75mUAKR)Q6e!k!71*5;TAKm<+(O=HJUHka+ZrsHkM*HJC8|xVD?|j+W_v5ikJB)tBPhL~k=-*h|f$jYKUrQM6Y5T$XzxMwaoYHsR-moX7za-b*ROM?wSXZZX@crm(=Z*SnKXTy7J*oWo?+Igl(|)pgL34epQcL;ShM4mOKc4Hn(awQisOg?mzFTCYxt>p~pz0r=Ypg%okF@zVrSCM@YpzSWoKgji^)|MzxXSNW(mej+N5<sZo62|U%{A6f?Z@zg>nHfp`roF`Z@<@AZ?&K3Q1D19-+8*AaXgB@Uo2WB#rV{|JwBb@|M`BF@sFQn{Lkss$S=p5kJ`8AqkCzu@~!!({Vemb{nage-&%icKiDq5z5dvKaQ@T$ec!j&AMM-gPc*GmJAePJ^;Y}#daHeVz16<G-bO2)=;H6cwf<}0UjN-{zboH5zG&Y*z9hFk^_>6OK7Qe6Iety;=lk~YQTz7sF)^`ZKVPlmyY}tld*qkuzHcAjZ9mv9zI}YR{a`(uyhLr+I-k+LeLfTWZI|!c=QHtzf2#Ue=Uv*j&%4~A*YsEO&^+(bzJ1;mzq7+2U#;^-?c3*#@i)8qewOoC{4D3O_*u?l@$K_iXLV0izI9%zefzxBT^1SUZ`V3+4}AN)eZ=FwpXIzA-#%}5?(6%!UmxpphxYBy9r1I+ec%4v5%~7!j!tz)_~lujn`}QAhxqpACfg6%p?y=|w?D^e-~Jru-t*>2za6a4mD;yISH^oR_I>+vrS|R5mG05qqx{#_=VI;KpNr$q@AG~8b8+BXpNkXy?tjs*zxBCZ`}XI0cV7kHw?Efw-~L>m$g$=nzn<202JPF|8RDPs@qPO`hW7327|!4dqy6%%>oD54ufrsJJnH-Qbr{<ZK1bl&*I{fwI8Kdu-1qJ4NQrZGec!&06lwUo@7ve4v~OS6O1_si#;=EUT}%7+buDL9|FQnxt?P2yx39}Z{~F@^_I0_)!4l*BJnQ;l;9J)ZlXdR%ef#=h;M>;^Clr|A`_}bR?c3K&ojY&$efxT;?FZ`^zJ0ya_Je+$T;OHDzSi|*?c3LrwQpZf)_#`j$^R<fzJ9KK`}%pjVnmf=T|W<e>-u?gLs3;v`+D``cl*A5T|Mya>*}|C^m2II2G@s^`_y)=`vuPAl@tBf)_n@w&ysK5r?CAXf7UABx9^*1-@b3+H2Q0jzhBmU8SQ7eFVp;Q-?#4**?w@|f^Xj^vi)G3KU8<JUmxqdRQvXMsrK#rU)s0tf5mq{H96cbx<0la%*Vzpec!%c7Hc(Rs{eQEzM=N*`-X|`!+hVqZy5O2eM4tXq1SxhzOSl%>%OYnsj%<c_f@rT-&fVXeP1;w$GWc?%X5qG+xJzqpXI)4li#Ns{iyFp<J<S6lh6I7eCvL+?d$u_+PCjVyM0>D@c(YzXV<=cpWXeZz3<!i*#qCY&mNic<BU|}Q~UP#)V@7FwQrA4_uF-|{q0)MQ3SsA97Q6&-uLb2BD8Nm7omOoxd`ps&qYM)f28uQ=QOl$Kd0f0t~kf{t>;X%pXE7|f2%0pe$E8ne$K=lv)=b(uk2mz`|Yk%&$Z*b_|D)pZ-)J3vo5axcPrm%u6$>R%1;)!obc;oKUafqKUb63{jJKkp4-vB{oGDu(2aBba;)cwv~NF06x);E_wDDJv~NGxq<#CjChgnLH90$OR`s!-Qwn_RIi+NUjCsCqKbM7XKbMu<f3@%1&wXj%e(o#sN$z>6`d9mQ|3*LUsC@f5v^HH-eXQruoCCvr-+o?B`}Xs4+P9yV)4u(@T##=)FPCgu_$|NPtmgo=Z$AeZIe4q@+s`Fx-+nGJ@U7<(wQoO{7=5OQ?`L_=5I@UvhT~fLzWuzV?FY|W9%`+&Ydvq7IK1+$RP7c$a$5Nl?_Lw`ckL(fgL&Pi#eBbf>$z6#+t0Pe_P6$Z`?*u?+s~ak$H=#ygVnzM9IW>3=U}y;<vG~nug*_3u9C+$&QCQC6UVpBPc_c9Z$DR@thZx+s_`E^v)lLW=Z#}0POI{*=b0m?>Mro}?C%}ezOMhkM!s)9M{WDT`PivpzMq_0Zf&^VwI7|P{Gi{@<X-64&wAe5Ils^Mqce}K3zwt)1imgOa^a0de*U~~HiYxFpTO7o@h`vi{rJ1({Bf&~BieWI^>IY|_Hjr1_HoDgrsLawzV)1Z7N6(dwQoNspT#FX`rQTJx1axy&-zN0Z#~biefxR-$Y090zb~MD`}+ckpK848`_}g$Y(Mzk2fqD12-^?7M{`e2-?zU9q5Ul1gZQoW62Dyg`x<}UxzzWq<AV0HeDA|~X_;TX^?eiD55B*%Vzlz@@0(oJ;k}ge2;cr5O^|PWkH+@xa_sNXXy5)GjZ@(1_l$nm=O<SWFzOk6KS=vleWF*7H}^|_FG>5>IE-Z<Z*EtAUukc%75;1Mdsu;QeGe;sV@uz+zlUY}!S`siZ+#ET_Je-x+S>P{#ZId0U8DBw+?2w17Cf*cr9XSymarewe)Ef)!@kq>v^qcRbl=8Qe!N}zbw>F;&ieI?zF^e{KW^7Y`&NAd->%QlYy9sg#_jsxyVNK8dd&9|rD>mPsy?<Kzqi7URDSe=s*m<vo$r3VIqWBU(GFEreX{t6${O{Fd`|mRH|wK)r<7SA?YmZeg8a>9eG*4#2dh4TPkkcOzEt&Ga>QRh6Y+{iQ~B{H`yUDWu}W%Q*!kMG^W9B3cc#kMewO_6T(`0F@w3#YZI_h!+SmE+rLWa~%{i=&7Z)Esn#xa>H}f67-)iS;-_DN=R{Le=Yd=f*f2jS+Qa*l`^0ReKnXi4F?-Z=E()XWvU-i4&;?uAn#gBHMyGQ)kvp@TOa%Bzw`=^mHzwNIQ@}sMipM2=dv9O=KtCIRWXyr$WE8itQy7U*{cY3OF;<x<1KkUcw-6zfb$li(vQs(0)bpGhBt9<QztGb?|zo%^bht&6ZZ9lq2eV<qRF?{EPoGJb2n>kLV^4<L7PNeeV6S5n=b1cukRP_vetDf4o>lwkf>#2Rap4zwTseN6~#79e3g~ws!lMY8y`LQSJ9SQsKDoax4YhUNb-+FIVcpm9|+qd&$&t2Y`Dqs6L-yO5U_uWgEw}kU;U*|{m-|T;$k6hYr<lDZTZ<lZTS@Ny#(QDss2iv#HvA=g8<Xin^`*t~Yf7yPP?XGC1j;Dij?@H-^{mb@LzO(m+twuZGNB7R&9QI=+u2$o@@G^hC2l@E%CK<=We)6kU>bg@QGe7dR@?%!M+kdrMPtq4}+?2w1^RHiP)aS+j)cMci%4bvgPP5NW8RaZ`{9wxR|9DCH*8V0RAFi&G3^Cg?@GqL}sr{(cp7EdlRM%~+dTKvv)iYYOs9OK6?FPQJUG2xM?P}k(_RIaWr1I@{z;_C$c8=dxSnZc}ol5)m=WFdJI;!~?J;gd;`R>uWN5a0->6?`K+PCxV&pX<W@H-xMIoh|&v48g?$hUs?L;Ep&yL|0u*)QvNLbPxHPDoInp-WPhul+3bAH_Uvuf|Chzl9nnS^WBHoCNKu{Tj12hyCdItJHbLz~%eH^-SQ$&!-;``^g4sUb|L)q#^U&%6A$uulv2TaZ?IE+G(9J4kOLf{I&Cw&6vMd{oPh-KF00#(Z1b2+PB*$HqF0(k>ETnsAoInJDjHl_3Ru`^UK<9;9J`bd~3UbZ|zsCGxM~+*$&!|+wErko=j$bCFA@v7@zo2YrpK@pNUnV{CSV6c{E-9zK!-{+Fz}H-$wh<8T_7-ov(fJlg_QGotM6>?!TY<=}0O+QLwP#$L1VV{bl8A-z7i#dqq|MamCd*+<Ehvu%CEpbV}bj&`0(AF4K=ve&FxiVziH2OZ^U#_Jj7h>aOEqU$>7_+sfDNLw@4Jvi|k%DD{st%QzbLlQkEm_RlpwoXXej6U9&7Q9+e&owsX0%X#v3kF817U$(FNOZ#?z*}m?t$liLspXj_<eZJ^b<Y?HB?RxOA;m_)_#u%TC)$d|yU$?*em-<~S?FZx2&e#3&H~B?I810`pS@&qzcdnkC(ob%_k~+V0w!^7>_x7$S{h)pDlj|m|36JNvTj)&K*W=mt^>}tIUyo<)JO90-%1QfF-4~d=B(>kOgBrKJ|25lx(y3EnKdRe*S>NM^uiM|s588jZ%6HdZwKm-TvBch^VPChu?d$f>l27~FzHWcp*X<w2PfX9I?oTj2otb%0hy5tyGm7u#d|+*OJjZhWeKhRr@vQy$@quf@{p+qja4PI4*9}SOM{m6Lvs8ZKmY>vl>;}_!`agd-l^?8c__0?;tTp;KeU{+|{aZ)<ZeHN){<ZRh{;jL>qy1kn`Zrnss-t0FuWwm=);HVN{pB=JzWd6XX8U)!&G3Wv$4|6RsP?(z2V?wa@frVa@_;!$57s*x_Ji?h`N8<K^Y!?&{9t@qelR}qV}&jn^>H75=UCX+?O^-59h{1muiFzpQTjWx-#e?{X|#RkEA=~#fv@|$i<uuB@5qn#&h6iy%W}O4-@ZQM9Js^x?dv?+x38->Co8QB*E2pz{Z6LsM?Y$7=2K7C%GdRelOG$}WL>!ZBh&XC4f}dL*uEYQS@IbVwy(#7?FYwq{AkPO>OLs_9v^$d>9DWYD;Gcca(AO0+=}XVN^L)W!^bBKU-xe%GherlOMaqHU)3-A_%;5~Q(<4PZ?>=3H`~|in``-ceY5@Gc&Gix<K})9zx$-&>-yuzz8|$NJdcv;{~QhbdLC)tEig{`)^!Zq*Vi$$Z(mQa{os1Sgo#G~I%oen8TNzYk@jcrGTJ}-?!i-GU$?*Q>-M*O-TraQ*X?iny8X59O!>-~zxukU_U-GX@!sDU^UKNK$nbT)*uL(UsO{_dg72JuXnnZ+Xo)4q!oDuw_I3Gj+t>T6{cf$+hxb=sAJ)Eo-8fdbi>i-xom~4_u1i<gw%+L9QB@5;=wHhZ`q%P<{<Zv|f9-Pg{^C0|4;cHauaj%vzJBi3ORf)(XZOh8C&RuT&(2ZhCwu&$>bc=j^?VM;>nuLU>qz;^8^ZnT=4yN*><7n3%MXr^xh-EGAMs<KT~N=9oNZ^+CyOujX<+>7cbVyLRNoqP9Et4CjZUX_p`ZK~Q~qg9{gdC%l>5K>$?q~{A1L$x_nY529`NdLZHD9Aj}A&#EFs*~(=KU_Gt`SZ=s36zT!9cSh`tLKgwxTDa60^*qx4f)^eb3G_=KZE_!xQ-mJt37{TUYh8kP_~ihc=82p@M;2!D%y0*h{dC4|!m;hWHRV9~MgO>lX12wWbnO$c}P;y$nZd%P$`2;Ys~4&MzILvMqN!9~!*a1po=dJ|j-E`VMS7l5xrbHdlbISAowUX=HugclVE;s2p`!2g5qL?iH>a8dLYxF~!pS`fY!z8TE}-wfwPbHRDx+=Os;X$Nmy7xLmhv=kikqKy}A(bgeu#cR=)A#ToV(Pkm8&TG+XA-<2-_px2!_FlB};#Tw)IL7wdqwQd+b7ArdlPjFvo4+}{xEj3%&gR8c8ESruX299dT<D!}E;u)O7n~c;j@}B37J+Z{BA*v|y~u-RNAtm=H^AB9oP_Y*XnwdjdIy>x&d>JlAcSv1^TId51qk7S=*@6J_;$1yd^=nmEeaPwZzF^wXi+!<7e;S^3&Yo=dEh*>#r1^nb%bysv<O^;Z40mR`hIn~>Icyx^hpPAtUv8VJG4FA&CBWTMGv$mEaRdy$AQvL<}pFI46jAY!tx&3MrW<?v))=Z(Tg(ZPPh#Go1^p>SVDLwdQG}w3E|af0a!wK5gLIdgx^9-!V<!-qorX9;aAanVF}^sXi-=~cs_a)EFruYy%v@bUW5LcrdUFFmsZ#hkAIgw^7MW$CZXa@LU-X$;=MBo;iH7`Kj^QpsMO;hUJK_VgzrLcf^TBq?;?aNqW8iT;o5|7eY7-On!cz{2tPpxKZHi$hu}NV0`MJh9`qVmRK`snUJL(42p>jw!aEt4hY8{7gzz)yv+%Qw-De2lI|<>h9HlajzaoS`Mt8zH8M_}7!pqS`@N#$-`W8G39zzH}kG>8+5BEo3h5N&CbUGY|$D#A#aqt`HV)zaCeRK`{KD-s(1&jU;Z-p<SGNv!`TDUmlyc=8`?v74^Co$HAdw6j-+#N2CUUD+axx{uvw>g>H-A27cKM2+HgV26`z<!I)3AMu<+DUYLsNKfXuA(DC?L2~h5FHTemjU#f=<rZK4yT_*$A<cSEMq}*c4%zOX6%T*2a9fTGRKwh$LQBi<~S7o3cV{Wa}3|b7#Hmt8uMM52ck1V^I`^bNc2c(P90&MiT)j$cYiZSMf0X-&e^=_nR7WW^Ir7M&^mA@>xAgTp>^Y7))moOp>?JfYmaDy&|1`hbxX8PXdSD=+9p~lwANK(Efg&tS{sYAj*8v@i~gIIxyJs>x+{7tEpr_{#+ofUE3}5sVyw?%tj|Qd!}8foKBGN_4u(aCq^skzs6M{SIY2W<9jis3f=haFucMChrQtH<H1?tiA>0UU05^i`qh;VSlq1~EQRg0V-XSXI9Nj{78;Ev?2g0&VUFY^_6SxWG2&ZSL^IQkL2A1;~Ip6&!U1=ID`d_+YQ3v1Qz5nnx;eV;maOyh*j-w;sI6M;l7yg%WMpCA<wbZL5Z7nQqB{^l$9B_AOGiif#r5(~0cgO3Ab_#I^UW;}NvAn+{+9Sl>c`e!#mg^iJd2w~R(yP)Hm-F~RN1gkLKHy}Y2TK3FgpP(^g2$j^;o9DN>M-`|(8t2^e?e>IMP0NWTo<m5)`6Sx-g0OixE%Z-S`U5@ZsDkU4xwJ6^4ViFuZ72=cf%6G{n26RiY0`lzM?ItdkeNDJk;}>^Y`ZbO}HQLm;LTf87--23))w-IXs4X^h5i@RlVr#MR_k`Ufv5{j7F!zqv1!>l}hfTyr(zZ1RaR>4$Vj5x@c9nE?f>R50`_dupQan6he3i`T{%zZi2>~%r!^2H#!;~!rum?_2I#ATl8MIE!+kz3HM=6_C^1N`@;3m5pX@YE;<lyLz$D%Y49ZY{&b}k(iKYx_d)-GCwn>lyeONlv~jxPdT3v?G292eA8i~eUw9H_^b6IeAN$@0Zi`M1wbf+WatJyFogC^%;d0cuY^dMM(k8mz!Y#b$<>ft@u0r@Z`mQ&9)f=xq+6%4^-%IqOjZ4DQ&=$1uG+4K51^Tc8_4t=)K_9lDP9umX>DMQj55mR0GV^;;l@P9mX28|p>S!8V9j<|14cCBcqSwMT;m5pq9K8X(7Ov<;B`@wGgl|ME!#Bd|=p%4C?4VVg%zwgHp;7oM_!=+rp^u_bI3Icg`Z!#bcBx2IqmI>Rmr6u+>R6q2sZ7+Mjx}hPM~Ir#u_o<Og?KDfrzrJ^hT5_s?Nt>m4&OlA<|D3U|E{HPt|6|bJw($&?UP3PiDrb_GlTXP%^zz2{PfRVXmK<@EZ0=!`mbC=m21LsUG*OHfABr<?dYBG?eJ}AQTR5vFnTLo7`_R;8NLa=9?c7159dU4!#Uw>Xm&UooCD3}WL`rSz7EafWL{?$E`SzvGOtSu7ea4wGOuF`7eOOV=5=r3V(1-C=5=!6yU`MG3EEt^2-neyb8StorOEY9xxOXmxca)9K9APt)QyP_<jFaoTo2RdN8xkwI4n96mh-HPbak$^(NX7KaxQkix9zrGG(abZxFfGc--csy{^-RNv?1Kii<VxziM|X=tl;nM;GteD@Zvo$wh+QQ(V_5A@`a_I_2qmPZoumqUVP-mOn4)&J5kqn&?#^y_N62I4zKHYQQM1w=m5Bt7wx@x1x>(}yr}3!FSI8tIm5_Hz$?-B;g#?%bRjId6>iD4Uq)YnrOnIH?xKz08MNs}bPN2j7Y}*S1MLnkq|LUXAHnjs=Xl@4a5dVb8tqaIe*k^3h<+&pcVJsju)XeZKeRdA4<3&WfycuiqRZhA;T`Df@D6xA+5zrBeb&=Q)#<06aBs8@T!%jIO<xYCpDV%j&`EGTxDC1rZUaA$?uMU-KcMfr(0`5KCFpE;3GAXDz#mYKa8)lJ^`bO-A6&|dd%cLFRp3%+X|!sHtMIxCWof>b*Y{Gs=2E;aMH#}IGSoPd@iZYr&3_rU-RbWhgz$4{e^_(?+%wb<y<lm38PhVhH)N<eA#-dZk)R(Y!K=`f@G5vWx(nV#op%#kY1^&rk4tQ#Pa4u^Q_v+Dnd^(_yXX>l3GaQE*hKCo+UXs1Bm55hHX*zi-2lIh>h)T*KDrpL4=*Bw*P|QY4YcQabSJzX*7HmFLv#hag8uywosf|^Plfedo{*6_-zU(|{ow)V%kaze>i|M{AR#;mod{2)zXzd%VbR|3AXv(nm7&%<S^rvOsC8D3OS0C<y7mwu`~)FfD<g9q6qYr)b%t8+W$m4wq1N5j{H-n_T!(1I`&+Ty+Gq>7He8En5vqf5bF>}Y93FxWg+<?khrr9x1@LnCb#yu`$5vU#+oByZGS3A>pGG^t9eCf<=yZ5G?ea7+gEBh8ozR)^O!}r1A>0`j)#n|e<<QP>Ik*ct3+@8XMi;`O@58g<571%o2k`S~d$>J)tk-klHfY_9%=KSbjt`a4iiB`=v@R@K2Y%Q)Cu``%Lxk|DbfwS2r_+^wMhGuMC1)A>48G_ncp1DLJqs^~4-&#>y!g$F*<M^hUxTl}UwH9{7jwM$8J!OQ41ejxUtT1<_yL^>{{VmE#qVDH<i#6=@au%|1uy>e;zuvuB!p)W!e4puoEI;6(aBLE{Dh~iy{P5IfOHkYFM66kU8(*MC44GPh4AZXDummh@?K#H;Sy;oguft!cM!tM2;l@FJdqF{MF<Zhghvv>uMom-qEEnY!b=I^?WnZFc3umA?x+yHCryQL>ogU@ucfIFKAEOM_`ft2!Z#Aa#n2bwVsK?b_%TAb5h46IA^Zp-e0zFkKMA+;w)><Pz0fG!3w{AD1-}4KMI-Q3cmY}fUH~sguY;GvtI=%mYIr^RpQCs^{4siMnqmpzb!cvQ9lQ$753hokp|`=y;Q8pi@O*d*S_Pg0k3t*6qu`!|a7!=Fd2M}|b>J}Tg7Beqd3IT?J))=K_xRf~^fS1xx32Z^;z_hIyxog!UhGBpz}wL$(Y_(x!|OeirFk2#w^6?4?Y!Pj8N&0uc*~1l)0O^`uK0T|zVl*UhSIqiioeJE6`ddAxxAiBnVP?&Y|&pr{5`L~XPd&gy~ycBE;I-HU7F(W(VXy)X-aeRIwxiPkfz@ABdT+A@i(3GBb<wE{XqHh9^ntYvAV*GmFTJv%ilgh_rojDRp@~b@8`AXr|<!I6}l4MPr09>E8*pgz4y_>@Fg!k^5ScB1AGzPh;D%8_#wxu*U{HtIcCT)Y6dzT{x)45mu8_e;gw!|;>CyX0bU=*)BHZKrOrpw)qaRBh4*{0!ix{!PkDU^PtT|Qyw>yS2)YD5?!__6K87cJ-iyyE_jBs`DeqfK-coXpkaLc_bL@w(%=we-$4T-JvhOR%SwYzc=$Fg%iRdQyBK>d~-2}@yh8+86qi?`+ULnW(Ip~}4-(Jj3SLYO>3HV$3=Wlc_{4D1IUD1wk7w>Pq($)Eq=yUM%@RN>GdC!x)rz7tZmG=mzdy(eF21n_7M{#v;E>-j5d2|>Y_hPsgHPIUI^W?<Q;jp~7I(gN}twByT@~YttC+GQ4nQ{0LZw=bv)$av#CoCbn4&4Py2!D+3h9!j8pnG5m;brJvSVH(EbRX<`TG`Xh=qOl1_+xY}EFruF-3&_zZ$($b62jZirLctXcJxJ9>b0G^iHiRcZROHlF7?|<Y^J?7Q@>rr$GW|!-)>?H?X`va?IE_(UR$Z(USb>d+LoSKN9o7P)T=V>xPyAXNPEA?{_6H$O8+dSeRO}VraxEHp1OZG)Bl@ke?1=7GG5lwUwZrqKY~_<Wv!64N!ANlyJU?yO$eVLgk{~5^+um_$l4|ANfO-;i|X@_1zs%jVm`VMe#eV<y;zLC4KIclqT%;QS@Y1h;7MLg_F^159-iXGR4*o=FT>Nkc-4zn(1~ytSvx#^27MO(!HcWBd6}0GE{Ya{i^3Jr2jPlvUG#CdF8mbQ6n+ZsgARoIz@yO#@Mw4rx(J>Fe}Ha+KY+KQpTS$<edy=#KKM9#89ol5Lw|zL!6(pf;S=zF^a8ve-i986x4|Exo8b@PH_^A@H{mhpEASY&FFF|R3pYbsz|G)#Xf3!NTnT*`t^^lDZ-I-!`Os_NeDL3n(kqT)3E^MSGw`qQdGrW;9zKiigU`a}&_nP!_!smP{0saS`U5N~V_mofZPc6)9)!LE4}xDt--cg?7o(fu#juMWf?fC^dI3HNe}R4re*u4k{seymUqLU!SKv$N=kO)?Jo*`Y9zK9>f)BtSp^M;;;DzV}cp*F<9SDzy2cS*i0dN!aakvTm82TXm82kWQ2z~&*8NCX=8O}hZzcY9({5@mf6#PAW5<LW;gb$+o;Dhj9^a#8cK8&7$55uR?EAVOfM^xs_kGvMXI!);<@YQhPG&NSANK@mt1zZb#2(AS`j24CqQ;zUUj{Nq4cdSOMz<nI0O?fST)6m~uLi@r^dGAwb6n?`y22b;1Dmn(93XewP@Mw5A+7%uSKZ7=fpMjg8HQ^?34YUGW11^u2fXl=8crnL|SG{-*9Sgq(k3&bm<KU6#v+zi`8~PO74Q_@$1~-ErM<0M6haW`$2R{gxlzMu7`IZ;&6T&;trSJ}TFS-)m3!g>T!e`+mx&=<cXV5k98F&x60^S2}N0-3c;rGya@Oy9qodzf17ts;$i*P^mIk+F(7LCDe;reJpxISDNeH5+?-;Uk~-wt1o-U?q2|KljV0hSQ{3C#&h2wy<6!xF+t)PW_0zeIDu62d>DxnK$5f6*IZ3E@0=Mc_Q}9cXFz4)_tYD*OoC0Br;}fZL<(;P!BTv^U%zehD23zXZ=kUxh{Ahf6S@OA-~B9~GGYdcM?TKGkHs(DSP)^RFrEi=K~NnXg@0kM#VFGr!}kUwXceVLcebdZ*WiX{;ZjZ-my9H&|~(r^0jKSJBb%tMFKKI6M{}fj$F|fS*O1z|X=@p*7&A;K$JN@MG`;=soZ~tUto*ytRJ47i-Y9@Ecy=bn>DjAzThE373Qabd-MMD3%c3gKmcR!0XT@@H+S%bRPT;ybygEUI@=bhru)9*U&-mYw!$oC_DpRfKGrHz;B~-;kV(n=)3S*csJ_8yWv03%kUp?*)*m9OH(W%{50ADej1*P&W0z$yV29|ZumF!5BN7YTe{Ng(iKYx7ew!d3&KUv2jC)b3A6@W0xp9#gv-GHLu<nSgKtA0gl~gyM(=@dhO?vB!`b2A)0F<1rno`vwDcP@GJgP}=-|u6*0l7-cT4qbpZ+J;xV%-YWADDt@QVocJI$X?2*2}JudLvQ6dKgNTAs&r(!KxWVc}ooTTjma0Xae|^Z'

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
