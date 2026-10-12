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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5ae22f04776a4a06997eb427eafcb07c/part_004.stl', 'relative_path': '5ae22f04776a4a06997eb427eafcb07c/part_004.stl', 'source_sha256': 'b210c7bfcb2a2abbe7380047c3bd02a76dda48a0dce162b6a8880489f279cf0b', 'input_faces': 942, 'input_vertices': 528, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0370824858546257, 0.33207985758781433, 0.37678688764572144], [0.013953682035207748, 0.38621610403060913, 0.44171595573425293]]}
GEOMETRY_BASE85 = 'c$}r22b2^=yM|{75(Pm(Fu<Tl5RjbHB1u@1L_u+vu;jc1$wQ7xSdlD45+tf9hzL7^2$Cf&5@Zk+5fCv0@^j~_da7rtckey-+{-!Nd7pi){kpoUy1S~n*OsyAGvx8;e}z4}ins3KDIdmgWcTFp3`-b1q*vF3#OM1D9O3mmqI~raO={k@S<4Py&oIxZV%-uFyACc^-B+w;_o~H8`HFQPFnGw|&i&&C4DOa7e#6dv6BELIV$aS46T&|iuT;KjDPM&WrF>(2|Hpq>!&L~5_;+P;SVQy6ov9-~-z|Jr>5o4sKQN`d@;zDckL=g}@Cw>5;M0Ef4|JYwg{(X=&#z3oe4a^`A5*-L_Q&_rd3qPI%il||>glgiQ2W2M(|*ds_Hn;!r1S56-Y)-2jP`frw9YH0MLC`4aw)5P%vU9}KQp&opBJ9ie!&v@xDB7u<v)8|`MwtUtnx9HAJu;D$F1`<etgrSc0IRb)BfqF()Oo6ZTsbhu2AQ7q?yiNt>iaKeFp-{&-t9?`@cNAT-E2V-a60liszIj%~5{n$3EKssI2zeG*EsZrLR8Uy=AnY_wGBEf8u%VpV|CQbbilwrM3V5c;&}8YG@zV_!(X0XSC7z3pBRtWBg}&>hro?O8bK<>pU+d*nYQSx;{5z?fSo*U-_Z2UF`C)S#+M=&F%B5eRr8EKj)=1{lLaJJ5TxR%J+3`W1km(e5Lkj`k_o6)6R45Rokz$d#O5Z>8UzTx@zY|1HQy1(dXs(JMS)5c?x7oQT4xC<%04zUsry7_J4H#PpfNx<ps+RE~%;gX}gsl>U-jhl?UI+)4z`PM{m)`E&ptam486M&flW0?bj`mVjZ{3T<xbEvg_Gyg5^8qjZYq@K8+LYdX}qa`=_eg?Nh6puK$6<_Icqu^)&S_+t$wibbakV)6mM}l*bRWd?v-JPuAkPoj*BpCN1CO_dMD_`}gzPdCYOYzq`oF<MPdTaPpkJuFJ<gou(g{+`{h1Ll<=Ux0>7iwfl%J|K3r%o*(Yk{*aaS_;LCEuc}#o$d{649^dL_cK@!~qWt)TRl59!8rokNu*y5_KWnb`+pV_yciaTa_r%3me*D&^c7G)%YTsAcZny5;bp5NmtIsRu1?_ietNn&+>~V`9*b{5_W3z_ZFTU0u4;72sdCpd~eBb59c72S0y{A3SixtrIFR;!YC*B(iqw~i+RN40LzGwH#9~YD#xW3-@&+lGnwP(c&+JA4tLaX09m(~8#MD1@IYmbxJ-7Mc3hZEZ>KYr~voo7}p%lEBZuJa5mqy1qGwZG7>%a5sT`GIbo?RM*3#VYTN2mH{nrMf<|OKZPV@wCh1hx+^N>!@V`?T?sXkB9nME#DbG`0@7_*~c~I$?xQ;a&LjEPt(cvI5B?71$G|%(3o-d_4V8h<p+9Cw8x3@3r@4g34W+YlHL9VFY5A_XWHWdKeT$bJs$AmmyWTo-;BxDc{%-sAJ{P3zD}<PboqlL?d$8(Tz%Y{Q|vq^Cg|h-^twGB0u6P3GY>KSh#zV;&%VBrs^~m<dfELurMRvS^ChR9`(@R6n2$N<+vdjGD$jv__I&_9;9X#kt40@<AA00%dpy)Qs(j!20d_wc-#6dx_rmY%{4)pH?PL7fNp`<vo~P@XVXED3_@P(l+Wm4XQI{Vz+wPY$ZFPMf>tNpp@I#B<u=9_(F<+Hu-sQ9deyDX@yZyTzRlb>zIp^CxS^Gs_w%fn<3Z2Ky(@g#G1M%JL_9;J4=ehQZ-OkTW)c&6Jc7Np`qVw;3&CY`#2(7dGF?)h8e`~GXUk}>q{5jsW`{l<fI!~$9cKaVGpxZ57Rl7ZnAG^}-mta<%r&qu(KR)>_b=+!O?eSkJLHVH}_3VDZ4<yvL`=vxXorm>;b6!t2QogThBfDR6R@Hf)T4UEIeF>c>YZJS_{wkpJur4s?6})&aNtI{*Z}J3>-%x%a`BSUEf?r%ze(2~9t6zfKk1F5y`!`nojURt=yVYO8^~pMauCrGAIDWQmRzC*cd0*#$?jx%ogL7Bt`rNN>T`!Jb=8ScJcKr4qSp6HEG*2J5(@9;vUU}`mK2aZc*cPjugMEhR^O||wx^D+twbS{Te|r4SYrk4mo&U#!)^jIVs)Wv;=YZ||9@phr4?4$vG@H&}cb{GU?u~h>J_GjH$Gv$``Mzbz*7GQMDp~s-D%tIiA8K6L8lT3G-?>YdZ&gnF``_1o$*Ok0<NL0CYCZ3QJ6CA`;p*0SHhv(}4!gfL&(rxY)wIU5@dNojv7Yb26%%#+gSG8(j_<3q&6=M$<)7Vd&7Xtwhv?%b)wSEdOI4jG%a``}#}D24(!O5WmC*Gp_JuwE8$YhgH`rs3^P1W8ak~ZWabEV{x$3y{cG=_hnVWN?uT!U<S&!-RyAE3SrQo57X_xQt?;KVBc1e3Y;G6v-=X{&pRKD4Fa?T6ix2CM!zcJtH^6axY=T+g@9BUk!^TIdd%BiO}N!Q2hN15~bX^77M&SATq@qPZIc7GXv&@sEe&L_;V+RfDeXuCPl{qEEgKXCql-Cuhe>GDrjv+Iu^s=U`~e}D3zH`V#FKW6IVU(;IqwTfBoZ+z1Z=6s#<o|0Dk`)5{qGrAv5J&hm#Q5mcKjqmJ>ntGn^@`m#7W=@H|j#ByV^7*@`Sw24hzO>8#ygyCf^ovtZlV|o3<(u__Q=a~HA2-zbc-r-E^|j8!`pC&&?}YYQXE}L_oU+D`<L5nXU3bR!uga$OG0i@e@nd4@D&N`n!w=@JuYI$BX#Bxr^uDUu=QMuKtvWyZy~g*P+@|+W**EroUSHQUOJ?i3Fuv1Y+z*X!+Sw`pUQw%G%zfDS{#iBkam_v?ez55lT~GFn{j)RcJZ8Vn<iR)far?pb)pdTeKRNX0S<&UqbHwo(S8hLM<VL$boenGCSNtK}?|Ca-i1z(wtJudaImbG#dEOb{+&A35=kH4TxMp9}_}ka%{$>B%pKGwr-!Ox&Kl2m+->vQQ<+<#?R7sy#-img9{NVR%bYAw={reu%d3a7a>(C8%W~%xpq|@zh*0cCdzZgI1yz>1;D(L#Ne;XLFOZm?8&XmXZ{IS}qPoVR1E5Dh~1R9Ok{=5fg((*m^%Gt-w+rT=mv);$|=U!zW_g+!!xK4TeRQWGwR(^c&Uwc2{tDk46Jm20;)AxOF-}bj0R(|ME%xSAW`0+JHXn$3aZ!CYwhsqD;EP2k#ll8jxN0mDt?fXVPW3Mamo%dE|9btU4U*YmYvESSKJZ|5er{)j#ddJkK;8lBn#+3i{+L`F<&hfY2wC3l|afjWu_gjqr++X%MF?rnmV*F$G()3gHuPN^yC+57`ex9bEYW(1vacJJJIpzCovhGX95ANM=k6V{-?(=~Ko6|mD{8Z<KpK5%LnUi+;*fulLyuR>LoiBc>>+Zpw>8kz}%G>3CI6pl)ztg|?sqPzFmn+}gf6RR^uxPyUQ{CUjch$#r-46pj8tD8F+4tu_r7X&K-_MQjzHbN8ADO1=<9c2Mu5DJn`*~!1_wy*QeX#P~&spQUpR>kyKW78W+9==s91l#ctn1^NzZu^>Pcy#L4lduB51aiH{LrRD_CAcs!~ERY?=|IJ^E4+v^E79l#MIL@Pjm8DJZa5moczq+ocAxrcg^37@1DOI-#vdbzI*=W_^$bz<Gbc>#&^%(obvAbz{##tRsCJ_eB-<4`Nnt8^8-5@=<=@hh~vA~BgS{HN1XDm^+@1+mdUDLT<fDir^HFod7SpI*H-zSr|ao<;CUAu(QTrte`2z|o{ej$eCNJo)@zN5PmCVV&U&qMR$ZR;yR+`YcgC|>SLVGj!MYyJx)R?R=Vo2`)m-JLT6ZsKtNmYU*z3eGRdk-RJFMrs@y-5;b6#BwXrFboQ-AzG^(ywdJNDlA=ze$33qRGqLAi_Lt?^^d3*Y&!#;gnK92~3iyY{dAmx_#0`Ca>I{^1)(t30lKJjZwK*ZCU_RK9yZ(En&f<-7L}16TeYrRx7sGkbnzeAoVDV9QSByZ1Q*qsEPj?nmdkz&G=GXFe8NPv>{-uLiCh9I5K>+K&xveN*|V_HW0vQhuua-WK_E9{2w66X!;#JnsGEtIL$1YF`>Z)xPx3im$6Y?)~kVhlZ)+y7$kEwN`$r=jq-}LsWkE`+}rF+UGrvGyY57NmR$Zve3SM_xqI}_;`tZ{dUc)eBXj)_Vrul@L*N`qvQ5<gdZy3!@lnDebe5tulEPDbsqNro$LKjYvnuN;h1_FzvBw~KG5U*AeG<se#iKM0bO1DW6O2<H#^(c^|7MLk6#vVU%yL!9;nWX_bE<2@!jvIf_*kC-*>2!z3<eha6i?LZG6^v_Kz#uSLJuV@4MQ(x61E+Z#eZ#FIC?Cp0Utt|D&JkeP#Q8JyrX--*4XfqlY@~E0gT&X!dCByWgKC&+M-9nD@CR4}Plmzj2Rh-~E31@5KqqpEh2vQ_Q@@`0n@JW!867=jDDszQ3I1JIBR$zn2d_i0P_)z6Wsjs}~&T674(V%H^ARj(^L&*Oc%2Zo%K8#H*@4SzX^bBsc1)eE0Vi#&>^TajRVi)&B19E8>Q>SMB5eJ_JA2cOb`-+N$z=kKwc%eyZ<J9;|Gm>f`>71>gN0OR&y|t)t7EeLv#|#(r+!9|nBhO6B2u8#B)|zWaNd;PT@yMVEK(1D7tfRQX-s1sOl|M$o>W7~l0>kdtRr*_5<=_xD2n<^MK|F7G@~@!j7w`5!#qROR9Qk@K9zPxXCNT(u_3-*>?tKlrJ>zq-`^Mb$nVciYb|d|&-MX_gQ4Eoa{cmcLbB`9<&8`yu!yzjJ+=@~6(*<I|LPe{Y8G>FBZNpM|!*pz^$(Xw55(AF7zwetzM{cPej>lW||iD4+Lhk@mk-E82JN&-hOLoqnOb>w7%M=eSNgBtKc*s;4vG=ulbtSI*h}f}iSpLVREI3if@{ly`k+7##O@`RL<D+Clp!k8{4`-Yp$npU8XvLPewN<Gk;9P~j=7{!V-1oAWi-#e-(qmGAn_)A-JNZKwUU@BaSN_<?8hxvrxtIqO8%)8(7;k^KKD7+v1EzQ$!NRwwE@a_+Yej?@=*e+TQ2YtvNyocy}I-y4@dPW_(id)naNqvKWnpHfn+>*%q?-Bo><|2y-6OzZk7-~F9)nOp;ue%H=AZgBtYfhwQ*uEXSS?-`<w>-tVR(7N<cbzc2Gw&(3rdnw<1pX20tB6hgSlW&-ve?y0nsvSF*vFD}ra*R^y`ffas*hKs0{j$k}AL>=t%I{CPHCnX;`(w`iq1jV@^?R=G)r0#(<JIrgNN2atD|;rY{I2i(gNY&K`>tj`W7U6p$;qm`>+cZ)nf55(*$*-0C%-&Jm3RFeL}2+a%XiAh{W3%O=X=?CHoQ1f<>z}mXIv#G%~JjlZ=`%n>#s-Bk0_LVT`7-8B8w-Fr+eq9KOGTM{uxdCPe*!H{9pa)NVSUP|G$4a(m7m*x5F`s5PpXcK7@V`i~b19-<_lnN9J(k4#z{`$OS*b&!P{*qS@dqsQjEM%F76gmjTWQr;9p<Xih>n2O*rDx@D(++40k(>0nVW>_O${rs2pJj+W?Sa7(x~A>1C#54VRqq6OfN@GIyO@GEc}`V<@ocSQ@rUE!Xn4;Fm}?g{rni@|;10ccTp06YkN79Io-M2o<pPs0P@{%B#iKinHF1owu!qff%!;V$8LH5{G7QGyVD9DNNIjfdm;y~oif;XG(&^hr1~oE0quXN9w)h2iXQ4)keHWV{LIM2mPLV^TO5`Yik`?VF1b&W#p>bHk6I&%lqs52HR<v>^O2oDF>n&IV^epMbN#na~1oCO9LSAI=D8Kp%rM!0FI@a5~sa2%CSxj}pRp(WbCyEZiU*#lz8%5N?d-h4WHgcz!tE3ddx0B0L!$f)0j<z|GJma5K0DAzU>a710;bCh&`JUvx0s7aosJgvY~4=v#0SyoL~7i_VAF!t27Z0bPL3hZn$8(8=%=cqlpq9tyvNHiKV+Yoj&b+Hf^OxDr|wt^}8jYP+(8@blp)g_c7r!sXz4=!<YYxEI<N?gfuS$HU{`d1w+m4_<|?fmgwM3E_R{T6iD)CAtp&65b!xH~R_U1L61z-Gpv{H^B?h1@J<68af4@1`kJv!o%S<=u2=LxGq{7t_#;ftHHJ4`h;*Dv=Uqgu8Ed~Yr@sh=i%ybm8ib2LI_vz=)bBJEs2(bOTuN)a&Q^=1+*Ug0-S*Mf)n7e=s0*RJO`Zz&w*E>tKgOJ7wBI23-}Bnd>Y*cpN3DNU&5#06m&nF0)K-ZfWLvydLm=%EFpZJ5I%%%f)By(pbI^bxu5VPbQ&x=+!L8A3U@}^z@6ddXkEBD9D~+^W8g+;eYgYqGFl&g8E%Kxf!o2Y(3)^7xCL4rZi>dD)nU;puxJH17H;f`jM2t~uz5BKHz0&dqb1?e@N;Mx_&K;T`T|@TZi^<sZQ&8<SXgupJOW;Xu7nrC2hlHJ(KGNt_!c4j3wj#<1-^-%f^Wh%2;u8!3Va>@nGn8)egj{Fe?rf~Kfzbg^YB&pNAwU}B|Q14?A2<xDj{4t>c5vJJ_!Hb<6a%YCDE<0gz$6dN3eu&3G`!F^b=S@xH$SLEFoMB{S1~6E{g7kML&lngr7x&u!Qh4ULC?k!a591^ym=o=g}eD1C{bU2;pvoa2G<jJNmgNGM^XjjqdhD=KsR|(a+$|Xa}=)5FUtr;)$#^ga@G?dm`%;;Q{DJp2)gJxDUG36Illd_e4MNMAl8hUD5YFku{fa9J&P--Rz01*Mwg|H+mxLJK>J#dQW6MC~Ve@!mZJFJ&`r0a7%QxC$bI|Zb}HZAcW0*Pgw4YFQXmM)$sS|6?8Rx1^x?t7yb+W7hMnk3#apH-3UtvXGS-}62cFoTVM&{N746T3E?Nu58x-bCJUf)-4@{5Eai<{zonwCYvD?0N%;5h@BS8!KhfLppYR{(UHA|99{L~n9_;mMP4Cq#A)E<)2+jm&L$ku7IpJ(@E;J9E3(kk;hx5VZ(6X>-b+{Z{1FZ?yfNP_5;M#Cq^aZ#sTpw)!*M}RSjp0Uc6SM=|1b&qe?nDT`LI`&ZNBeNR9FBH`a9gw^+!k&_2)8DLTcI7`R&XrZ7><QsB!nBH4d8}wJ@f^*9vp+#fn(rWXic~lTn()bSA)x-W#O{)aT!85FPaC=3qOM9gdc&kqgmnXa7OeYSTsGH5%!=m*3BYc_zu^>UHA_C4|*H^2fmK}=84P=gw6ax*vu=0e?fnRMQ_0s8AF{ISHj|z_v-7@3yYd-FdJTZI2SBxuBmcSWrS<MqUIW@8&yWQJ}hd+f0L*(O{iN%>Q)~9gL}!J+-t<U9F8BuaS}ZbpM-<x7jO_>hpva$!AXShTj5xMZba9^8{vcK7w|zigr0{(@OAV@_&WRxA$$$J3}1t<gyRx=4!sPYgAbu6;Y09eXb}DkUW=}S*TVDABzPV?h7cZ$z6Fnk$3?Z>I6`=QI3}PA(FO2AcoVu2-UJ^;55kAx@6izaJ$wtj4&Q=*MSp>Rg?}c5e?qUpKf&LjSK#m9Z=?F=TSE9uIF6wy=p{G>K7pQtPrzTHhv2W^PteccPvF()T6i@)7o7*sg-4-d;8AcdLbx|N7VZuALC3*;;J)a1xG&r<s_**|!u`WB0G)_VfG5I>(S`70cni7--U1&*55q^{tLXReRroe~3%(8ihW-lw2H!+~hHt_b3E>OqPw)l!H2NKU8vYvn7XBJOf}Vko!27+Cv9+HN-a`l<KvUoY@Nx76d>r15eg%tu0`G=DL|4Nf!U1$H9Dt{xqu^=qK(rU!3~i3~f}6uF(B5zhxFy;LZVA7H_Jv!at<k=)Xg_ac{v+H5?eC4uk%ZfNBjeS~qlC>|OSnBDJRF?}4~O4C7sGGBtI#d*DtHHa6y5><fL?_~Z^J*pzoWmwzr#1so3Q9b_y+tXA-oU00PlnMqNm}#@aKeZGWs=~4DTX@ccMq&o$#mVe)v;(JGuwn4sSybz}>=;5RPv>S}%DtO9&rDkHJUb9q3MY2fUOJUKWn!=q_|8ybC^#9)pj=A@mX)g5#*8)HRL}9!dxgLA$|2;9=nyfp$f^!Cm2t9<6fz7YX4b=u!9xydB*EZ-<wlOW`H(3_^G&x(uEP&x&fhS%mN#;h2pE(B*IdPDXdZ$?(_carkTaG8%#}!|`6N(!TM8a3VSsPK2ir!c);9@Kks@It-o;&xq=q8R#r{2K){oygVE$(3$8gcqaThIs$$j?t*rOyTBJbTBW})5W<JiBk*B(8@e6d1}{dJz>DGO=nQx|{5l~#5}gT;gh!#X;8E~s^bL44JSJ+aj3I>m;h2EVMQ6iv;T32AUIFhxli@w^3G{3D1pFO(8U7CL?A0pcsWTxw2u*|s!IRM`@MQRHLU<866<!1{MW@3{;brIycm`u@86o@ux*Yxh-WoOjwi3c06T%-6!b{MZ@Dg}5`Z_!s?tylJd%!+a#-)#+g-<e855tEUizf-;_t3@gd+=0rIy{}RIF%57l@RWPj)XhGuc4#h*Wh?UxC=Vk6WRL}HhaRtJ<u_p$iA^~Kh*Du>@y1|MvZB+7cD%D5PlP#3(sXtzexyxi0*+ugwLTT;1i7FbA)hVuT~kyg$d#A=peW|JQAG@kA&x-Z^LWQchR@ucj5QYMeuv@26QRB0p5%*gO@R;H>2;vuZ5#$IA)`hV9}NEZ1_*~Ec_>Ymk^c@IYj@4C4?VB@4*tnS<wfugz&>?`gEElgma=9V9|7NPB;hpAFt-j;rJ)a_q|$A!S~^B(E0E;upb=^`{5@E;im}Uf`o7(uGvCd(}nPRp!2<v>s@#>ddeHQKL{^D|M5odC&F^S`2)R!{sW83Ip5)DVJ{(^i4e|$W{0!D*$Cl`Xbw0BZJUvwh5sdl|00CHM5RB>{8{)0nju|ejxGE<nm%1*elGk2Dr3UT=Y@Bm_uzYsJ+m$lUWK0ZM%EF+Z=fr^k#&dgaC8zZ+S40Zvk04gWl^)w+!Gdk4ekh=eQDuNXa!ibA}n+CH^b4?tJi>{1JO6(fv{OW3Y#^iuvv!+o3*O2S=$O9K)1ni&w1J#xkm|``<Sq~*9n{Zp|H7s3Y&YZu(>A-7a@e#pyr+@?`58k(#O1!_cg+gqPe}1_dCK5qd8#FEZ)ewA>qtu25;nDl5jfofhY3rNm$-ZiQb1r|Mo=QTM7S#{@{tc=MpyW!i3FtucGE%v#@y|Eqo3A!4r9ZEo|O#3!D9I;eXJ-J(2xz;XCMkPh|gGSoYWNb3Pu<PtMuwy$feVvv?zW^}^ZF9Nx%2zwjeyZg1qhfN);)F}P){H(j3e|K0y0Kk`rRrylEnnD72g`}64N->e<Z<$NsNGB%@ps~djSq*E_=3(Ff;&wl~*w^u;'

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
