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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_012.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_012.stl', 'source_sha256': 'e3a4fb8f93941b24158b418a8101ceff280803bf27f12971cbcb376eaae2431a', 'input_faces': 1034, 'input_vertices': 567, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.16877830028533936, -0.24717570841312408, -0.16684706509113312], [0.17735664546489716, -0.08428722620010376, 0.17538639903068542]]}
GEOMETRY_BASE85 = 'c$}r33A7YNnuW6p5D^fN9c(NW0TB_9#hp@AL|m}l+O2)4xB)IKDk55l;);j}?($Sn(RM+)1(Bsdzy<eKTWy!8w%R(~ZMU{#JB~W>SAI7q>#v-1=FD(ToO|QGKO$~MM!t$avfg3T$VQFZMe)CFqlHVpf8fDEQDmh>)GoSU%!Em2ojPV>-*e8Jl8ahbbo(cqd)U#3jyf(ET@X#}dD@tXr%vd(N1^9lr|;IYPod}O=T4Y3Ve~mCpF82SF{U3ldfdb@L7#Z$=<~*edapr)hx94zx?`Whw8H=K-xlWKs@pdVHQc7vD{BIj-+Vl-J3U&^Vq;n_FPpk4D_**fuYdlVXHBnn@zNXau8yzke%IPcKQI4t{hAED-1xRCy?9ldRax=UeSGPo6;E2d;Nqn>xcG8ItVdVgHzi9itvqU6mR`7c^iApODxud6-hEz{UOsT~{aJc6uG52Qy@+1?bL%Iv^zy~eW$LB%g{QLg!m)2x>5<~wU$-VpFJ4|KXT~@FU|p8p@WXD;RO(ON8(&xHh|0RETk*k$v|jAIdQ+yp)8OYS<2t?c;H&Gi^l0XXm3310#m4wPD*oX4t1|V4Lzh+jJH32gtQWrdY+{yPTJY-JDnICT@6<g|<zM=eaZhCF<yn_JRplSOxaX&9vh?VS=9T#@4PPAhv;W$c)AJ@hdVl9lnfh0Yo=wl2^!gEpSIt`z|N7*WS$cV=ZJtceTN006$Gp|(%v;h=?^rJ~Z_-QXnm4a&-jaDxKg^rgHE-p@%8Fi?{ZeJ#${*giAxkgJ>$5Sf7mwL}Q&zlmA0M5$B>uhU;-yC}zG2<*@$bF$?KZ5*&`VoRS)bO+XWXzdD_(j{{MsS$^X}u(>s@?=UOMRBX<2$<@Uf?5>BZ+q&q-fbxlI3)hR)B_&)M<*EWNn@tq-R45_;i3UtN-=M`vulG)phO-LO2fpJAO=RNY7QGjqh6EWLP9v7DvXZMk|~mR^45xcE73zBYcozCW?@d$0aqH*d(&3zziTnAYoVdVW(@y!4v*h5J^1PnLW<dgS8E+rGCxD_**fFZ}#vWgQkCZe3YFUa#*tZGBoV@Ab&4ta#})@$-*~fA9Ht^s<YO&<nk`nU<xO8tphHGrrL!bE>X)9`TQKo1di@t{Z%RmR{Fz)q`ohr1-w?EXmTNLDAAIy|~2}%QN*htyiS=B6@k*5o@yaLjS$XS$h4^Yu9D=^U%?i_1UoLm3V&G?-kmeu_3KDbc^+dx??t`b?x_jymTM0{a)narI%g2_IvfS_o=K0uSdfUU!T^s-}CXw{?Ns1zgKqg$^OvAYhPFY!T9M}dhwR$j?B`_@3*)yeO=nuHM}<KmMpzcynIoX9!(s&I7=^|Hf>2-PxgmDov<`ZZz#@Mo~75lJ9b6YdeFY^Z{M!Y(xd&)E@$cG{cc{D+0X15@$bWX-ihbu$XQkUK<TBwe7`A6ulwozs(oP6&(szhvh>1nUDs9m(f&m7e{Z=uOOHk_tJ()jFCHB04PUdLak}<_Nk8b?2PWf=SXQ+U^m?+N(LA6h`x&QeKhrS!&+)h`=fwLN@+_|_FH7_pKfaI|kM83eZk}9~$9Y|Oob>vyy2Z~ad6w6emq{<J?XWT{UV2S@*YfWw&x?;oZ*cMDF0o!DkMnwARh-Aw=;U!p|LDr&yk1Wp=k<oMaULhVC_m(JURNIHb>(qhS00z#N5zxJd0ly2O+0y=*OkZBUH(&iUF31)E9*97>4mRO+?dvt-}!jyHSy$q^*$awa`DOseY|uZuRJm8c0lF#hu2HLJ!pMeSN`bZrPsuhR~CFcdcBKJ^2!IEpPr?c$4(!Wseip{cGdMNe_ZzTEm?ZqW@j$Sj30B%;w-&z(0NO$<{!PG%UMga^kVnY@+>|2?xGb{^RMfj{N?H_z3%n%%9;9aXRXW9qeHHVe;@7;RqnI$;$(l~^kjd6u6)_YORtG1kB)pidfCM*zfSfiPEYnH>W94B$4mF|%E!wtUV6dzuXyceoL;<@{fv*-en$P1Unlz+r$^e)`1lFzXPlnwXV8`JC;J(vC;J(vC;J)Qcl2aG<Md=d<Md=d<NIMhQ}@}Hv48e6%GbQEd`-IcIX+&xkJtXE<l?1AE?)a0A1~d<Yrmv?&Fjk7l784n`FQC*Ui+(}i<e$@@!DTS<ab^#lHYk<`CZb#_G#pIURQqSb>(--b+PYKe&==NcV1V1SEG~PCHGzXK=M1UE5Gx)^1GUT$nWYN>Ji_^N%vLlx1}fN{6j`o>B{@cttM_v>!mxUzMR=l%hoSu>B)Nm*MIUJ!S{d4=PzXS)6nhes{Oz8<UPXRk(qkE>%VT&$<Jo>Q@nG#4Ox0L{D$>e{nStCUzJ}Z{ga=T_BmlgmLA<apenxb%I0gc`iTbYu{ujvKI{8W@?6({sr2R3S^bo+`=l!0NybH2zT<V}J4rv+eo~e1B;!ga-|@Qgoy0%7@*S@$-%0u*Pp^0LkmT=f9+Eu$@ttO5>Cvt02W9EyFHX3jYFz0n#@(8wm#%2FC{zFZ(ZyMM)O7zPRo5&1#Cc1z^ui}cF3;3=TePBT-RgP=u3nv`H+(&_oT<;fa9x&OKW;(w{J%T*cUkMF{7$Ube^b4Fq!-=#DM@$hr-<&?k95C&BK70ekMv~y6o<w-d2#aj>-6OFS2}rdO+31fS6*Cl@zNs~ue><<Jau~Vd5W&Q*vCt+i6<{E`gruRi&y?zug_nnmm2f=>-0#Uzv^H4vOa&E9_jPf=|z41q9=K-K7XB_eEvE;`TX^|K7Vx|m3Qm&*XhaUuhWyyU*8X(zoqD~_&(~KpM1gV$}glR=lm{SdQH5}`F%Wk*~KU4{4QR)k5A6|$uGRFd?e{d=lm{SdQH5}`F*_3?Ol9w&QJbQqtB1?7q2&vza;(ZeE#(~fAPA`V{76$kM+9p7wO4)KKYB+mA`mh`HOU&+be(Zy7CvVD}Sl!hy10m@bLIP>U}8ZCtlb2jP&GvsEbeDhr0OWeW;61-iNyQ<b5dTCtlZii}d7usEbeDhx&NE$Mo@fAL`=uezVN^jMt;_@%fC`OPtRn{p<ZB=QCa}az0ZN&-qM^&iRaVz2DUNjMsHO<8__SB=-?r=QCc{`Am(@`Ha_fK2u&lCiYKWtn+8D>-<@|@?sw^-N!30u6Oa$bzYr}OJ3~brTcj0#X7I{y3VVUe#nb`ymTM0ytv@vr8l^E<-he;#OK>yZ+JRB-}ZWu^X;U6<;$FJdtKjC^18mKlw6ncT+X+>uJdiL>wMemI^Rz2yW%<D_PWluYvMWI_ImO?r7I^@?E{nVBS~k!=XLGticZ)5E&1LNy7p-`I{UGb)02IdzK`T|eXl0zNBbOo9|>LipXB>UPEWp%r0Z2b`aY7=lkX!Pe`&0{_sG)ydt~YUJ+jw*ynm1E^|Fgs{_b`Ee%b5E{si5>U-r6>_wSdzUU2dL{j%5fe%b3fk4^e_@0Y!v>}Q;w>}Q;w>}Pbn?)|dYll_d-ll_eDi+jK9^<+Qe^khHd`(Zy5b)6ND%Q?UDHLojQldf}qAD_Gz@bR4Umwde53%Gcl^DAHTy7IN8AI|xGeDYqv#p|5E=;D+20=|EJe~<jm>qYWAuPeVx`qz0o`JLC5-+5j6ophbsE5Gx)@;k39zpK&7?~?nj^L+9<uPeXvy7If4e)RpBCO5_7>U}8R_w%~GA1FO}AL`<h_n|&s??ZjO-iNyQ<bA03qxYdMK6xL?_XEAI?-M5d=zXY*Pu_?6c)btx@p>QX;*;;+^8G`vmj=b(KlFMX-#<+H*LzaFe^{gQ{X?(U@%_VOp5=${A9`KiKlHl3e^}EG-#<*|S^e<+L$B-mhhEqB552DM9~M4b82_H(oI(2*={irS(K$CLI$h@jUe`H*_A^O5`F@SAJl*Na(<AmdUf20^(vR|G_Bqm%Jeqxu*R{`)uDn?L9Iq$mhvOfPua~?yc~60^{MYNsbBjKH*&*w*bmh6pxjnk_*&1E>rqh*&>igI=y3S+OkMcyF$D%7wOwMDSo}9<(y3~)(W1XJN=YpkG`$pw=URQo6-Txhm*L}SII~1=gze~o|dmrxy-N*aCTk*Q`JL&%KR=n=x{ok#4y}`x%zgzLT{%*zV`o2@rzx%rtuPYz)y7Ix~y4>HbcwPCR*Od=?UHM>gU)<lVcwPBmO+5La*DLwpsH(s6D$ied=)d|!k(FjqyXf@MsXy^D(f$du|HSL8f&Z&N@#^1i*Ma}Pzwz4Q{NQ1;Q1%Sv*jyC-F5s4ixwtNFcz!6|^HJ0$lve|PlDfFzgiu<6uZF%RL~&i*aIa9Bf;%yO(-hwcKj(w5;OYDnH#{G2hOdOOeLk*>8_KKU!hn0>Q{1q%{Gr`0pYXki*$L04-G)zb!`ArP6KzlG;<qUV&wDcdD=EGwW3|EmLR}wy?8&&d;pJ7vp1^gP*MDPPD)YfS+MIP`o^6hw<i6NF`3v{)N!lJuduw|v?XB&vXm4$Q#eKH6jq-8(mexM}Y*sGj*F<sM_+O&9Zt*wJrX}2dc4NT5g>t+hb#cSxXl+879ZKVTTo*U|EAbY4d??pOw1*pR12;S_l)q9JH(UlcJdQE`n&QVXmW^w;L%<&SxGrwERi0}w|Dm+yn#2t!<zipvc~WG*Fygwn;Xe2>&zpxbk-E6y-uN@mTN&b0+;Czp_GZ3bXZ#*1{yKizg0C}v+Z2BtKh3~CjNdH9``~9H_!^!jrnuomycxd6JT6OdLwPk^6mTDWiW|0*KeRjL6TS~Ieei7B9rzSCY=^JC(e|b;eurZ4yf@>&mg0Le)>immr0b)Py&3loyu8lXlen&ZSX;|9AIzi8**47c=B$^>eTw4sW%qG8ZI7e<GS<mN*3R*?U(PetmbKZKHQR=DKAY$4TAqV8JXhB;){V4j1Gk^u6!7n%oM=d0+;9b2`%vbD(j*_(#SOnA-eOM-<+_OWaKi%J@PtslqAqUu6x{Fx#`r45Phcz?*RW^6Uir8#ZrC=@HJJZUx^Ye7h8N^wU*`FOP@3aY+^~o*^K5@pJ(;?=;ZXdU=U*7&Q`~TJF7{@=-eCM*DgFk2x`A&nezz2V13%5dof*G*itmh{$>8ttG&#i$C*#fV_sru{DQ+mQhW7_7;#1skXZb_BTR!1MVs^%}X?NjM+;C@n4MiJDUHmS^;CU$H|31ZsGFDss->>VVkD-iv7hc|A><hTAB5Ug@%?I;nb5>xUw_v?g?o$-6FT0N`XnO+fpJJU%X6>9v`xQJ>-B_DVShMX}=W}?@uH!jq&vSJhW8FlX_Hg^z%>lm-<=2MP#SK@YbqHl{D4XTuy13y#h_~2ZhjM*Hd${4YaKn>A`3H4z!>8efCo#r9Qv4*wvT+S}4A?s#*ToIn<+%p)Z}ZPJi5p&&i+!2ri$ZCMPjSQj@MWG`gmNKual?J_XP&n)#HYC7g}K<9`Fe}-d#CtY_$h#IF@7P%-@;EzurK4cO!2<>xe$C4PZy@R;e~iJe3N;6I>im;)$oCU`{7gEu&?}~)ypS*KVtgg*|Y`t6gTXPuYJ+>r7pfeF?imW@!w4GeHp7A{vXiw(Z{}wy8th5G4@4V*M6+6r!^nUqs`g2%ySFYOXWUA@%pm+xRSOf(f(=H$%U+)U(<di&s2f6xfyG=1M7S)&)M}n2OW5>u4k;9Y1092Kbs%$pP|$lQWrN|jn*-gd7(7T$8~YTZ-}?px=?0Cw1*pR2RA%9ly9hu8?J&Ip3E5Er1;5<W#by|6tGV|u8SMC&vOmtKa}mbCUL`ybFnY;d~qnP@F{M%KfcWKmZ40cE^assf982xLwt%Gh6KLi&3wJh_<d6RZTxHpzRmdCrTE+UX$9`W_^ncW7yL{C|A40{DQ-9gZ-#$h9#^Hfp}ZPC7;t}liW}}Ce`xp0CwzZmcEPi0_uy09a2I?HLmNh2{2s;Nc^KpWA;pI=R(t$EsOzJTVT^kZUfyQxi@C1-SzD_#AIzi8*>=qHmaLb`eTw4sW%qG4ZBM5CD%Qyq)=nMmSMyA5$J%Vln(fFspT~1Hi|3#t&($o(nopaKaQoS<0slReQw*t#8<x>Jg>p+Mo9E-YxZ$_NTkI*J+z`<oZn!<%aC9i&QWrN|12-Ja7~iJ&XvVT}4R;RMHy_u<4Ljty2J;_Ecdkj?@RD5Y%RFBaN*jEN8y<)+^V~X=sno>{55S*!-rf+O;)YXmu{ZPeF5~x2@ptjl9ekJZyQlcO_-O<7WBfKL-VZ-h!FTX9HN_35;?3|K=5bAm8_KKU;(!O@Q{1qh{GlzBPxyhv^ux1h_u*6Auphn-Ks$iC_<f4O^8t+iPKqDESRL@cSl34%2Qcn^czKtxFX6flWNod{d@zqTXWKK+tywRX`xM3N%kE>DwxemkhIKNPwQ~yX%RE!vS(}@)W;?OYZ{az+f#;wT&(#f#bt`Q;!R=?a2mDtkrx{WgH(ZC-Ih5N%X_k-c;)dT5Z?UI^GCQI@+^{>`@YGPgqb_c^7H)VdV|<t5r!tm}Yq(3me)+gAZrCx;HJJZUdT>qRhL`4IU*`GJP}<^C-0&cLndhxSnMPgQa5(<V^A3ji6gQlfi@lkz_ZYuliob`S9^iY7-y_A}!%thVKjXJe@&5Rk2L2IG(^A}U8r}^5$ULr1aYK1Ed??^S_!KwnFMnwF%P0IGV*2CRv_<$7H|&qE;b_CDi!V|Po`*C3A5(ldV|B#;L%Kft7|yth@bVsGU&?hI#M)Y``CuMx&bl+tTd`g$_bH0km)*y8v^|yfYgs4LSUacDejU$L57uTg)@*0i`E5LBvw03W^IXkltlMeR8E!wjGvI%Oa=IaPal`d!T|&7dlr8dcUEJ_{;w|>{P;QK94>#NaZa5~C@2QI$J_9!#!x-PE_!!2raSi(i9FULe;)b2_T!Z-!r5D#EZdl62zRYtel=k=(H#`_$=Gk6zT}EBpa0LF$b5BEjiW^>*i@lkz4;X(yihqEgUf>6e-z&vGz)yQ{0OPk$@d5a`416C?m!-JjWq31upLu*H#SP`v@Zo?5<5S#lfc&97D4+0yi5Y-r(;mR5xZwbNjX)bgUHk#X;CTe&zn|hG7^@ThAJ+BJ#|XxK052afc8Tjcn6>qc=7V{(IopAGZpV75+@~mBUv?kY({>E)pJAO`#@acZ_Un13da*XQV9j=6o!`N8b|cS07oMvd8S75kbb;H??hg2$p`2+*UEFXZTGvqS3Z;2Iu8SM~K)l7C8Oof9_He@<aKke~`GLB);Rd+j8I18mil4z)Hm>2W0SD&ey0~HIJlA0UL+Q;mi5p&?i+!2r%R}jiPjSOT@MWGmgfgAFxZz0rndco1@hNUNJr{d3Uk!{uFvT12(;IAH{N5?vfS-=wu8iL?#dpQebnrtwO;2&d>3B2zka^sY;)e2S_?v)-;8WaiSNTJGNIv0*5VI?uO<Rmlal>8lH4<$kb@9cD!ShJQ|1iZzGFE5&|3=qGA0rueF<u%N`*N=95Z2ZP%?I;nbJl}-?!bDf+@~mBUv?ii()JA6Z(yBFXYHIx`;9zPy;+;hS+iYP=Xdd(&EYxd%5yb`vF@f#SGfJGKHyKGoNY*5-0(THtwUK5N{f747dQNoc#Azdl$#>j!wq}F4bKYYN9y8+&%zDQVvHYC{4B<@aSaCr9Gs8q;)Y%FT!Z-!r4QF6Zg@p5_GO;02&FSV#SIU`mwE0K$_(n_hKJ(MJnv+PPjSN;x!9Ze`k3(tr})SC=>vYu_<d6RWBham2Qq%=6d#D68Q@2Fnvvp$Gw^2k5%c(LiW|zS;UfVL!>736K>0)ajeNonBW56;O?w!h;)Vn9btu}Q)WsiG44w~V{Et%nP{!(l|3`Fv^l>QTK8%--8T$&Z>oC^Vvzia)(dMit^W2H`Qn^o2yuR!{K1bWLX#XthWCm;JY}!A^Gu4N+*@88@HS2r<&)H2p2V3)8-Nab+wAmVNKbslwPoa!5q%LmwDB8~fuQbfXb#cQ_h_~2L78lVTZrBBGcz7tEP!~6R1a5e^`cCn~8S7`Tt6fVzu8SMC%ySK)JQhlhYZ5mcmy3Ow=W(Ir@F{LM7+>bu{*9$BZvO`1&pcbhNAW3cI5ro1GhZ(-{?;k}0)BGf3-XcTFW@H!_G0{8iuc0LSnzoQ#-_O8SiBiN&)hwl;)e2Sc#o}9e2N?9<qz#<`GgN9rWc+~n~P6z!#utQp$(!gK36e#9>n<1r}!YoYKi}Qbba(Oh;irQ<pstb$8`;6O+CsSJfeG?i|>DqIewJ;V)x`v+{edgdpPYMVV#U+?Tn)RqdZeN*5=Q&|5?w2o-^t{^Bi5tSTkv3`b?g=s{?)($}bJ6iyJ<U)+m&#%tSt}iyMAQyv6>~`i^K1H|z>GJR+1&sf!yv1~)u{F+NT4BN)rZHT*@uZuz(_Zn$NhYY1gYC{4H~al><Ru`ly{PAHA=DQ>tMzPiRkMB}N88xFyrd2Vd;g->zA@wwQW`FfG@yQTPx_-O*Z$oNfC{6+jU0(WHmMk&4{e#V2F@H9Tf4aeina1-<Rc#0d!tKq!?cf+T+;b!uOHeWvByAiV^o=uyFPjSP|@HGT&2zBv!iox>`#^03ULl|pI{NJnVqmLnsI}a}}GWI!K*KVw>$C-o2m`9tluFP|u^-{S{QM|tFJ}#l{5ww4dbuyl{^Gn)4&NJ17wHdKy8?nx>;yIhibI^$AY9?b{O`Aq=``NVt{~XFuhSbFkpFnFG$~E@8BOlkr4L>K|VvjN(5$)lITf+^H4CQm`;)YA$hDS2S=P7<9W7)Wd+XO7+<GQ$Et31~b%F<ApaZTce=jCEw=J`CkC-@XM+yh_cxp64xQWrPe9e?I|bDJ-GiW{Dri@lkzml?m1;xFT;8Tc~eH%sxC@zVtC&G=1Hyf=Q%1z*C`xhZaVF5V1ZVjiDJaYK1Eyf5G$_!KwXLjKThl~4E{#Pr6qX}920+;9tg?T)rPb@5vigXi5D|D_b)ov~Ws|2|zGeeBM-x8UVv#y*eh+Jm+A1aq*2d9*p(nt5)_da2x}C|+N7AD7bhNZK!9ot(?sIg0jA@JuyhZRS|BO<CvH@SI)6bI_FM>MF*%mNre{_Ot5)ei_O!hSbFke~Z>Ul<Pvt=i|D#;TObP>@lHS9nl_c_zSq<(V=`nUEFXf-0*0|_#(xRW-J@maNB^}<>R`zVe35CVE#jC!8I8lH8PiP*XV!xuW|nSpPfraRsT_rZ(0547U`Csg}#zMz8E#KiGA-q{NBu0zR=#;PBx<d0*{7Y@B'

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
