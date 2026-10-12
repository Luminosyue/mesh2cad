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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_002.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_002.stl', 'source_sha256': '970d042f76fc047c94bcaec97adcaef123648c90beac01285f47558fef74aeb9', 'input_faces': 1040, 'input_vertices': 625, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2861103415489197, -0.25643301010131836, -0.42565101385116577], [0.28611090779304504, 0.3643167018890381, 0.4917263686656952]]}
GEOMETRY_BASE85 = 'c$}r32b2^=+qQcbkRUk-Dq#c>SP&#BC}A+*l2;UvJcLC+2?CN7ZA3s&5QG<rIw+E(NKQ@KU6KL@f`R!AC<c5L5ykY)Q+3tQUAzA||M`DB&$+L?r>446S65f}9Mf9m%3adY|88-b{}8&X%sq}HQP3&rj7%RkVnCnt;WY;j9h2k~RlfW)I;(AmHff!coRQAcRr;n6?=!5*-JvRt`ZcIhBUGi|kYOW+^%~rB$gsZY;y3U0#PIaEKfHghq3Q9ztKM0sevMGwYBfURLjRBd3dD=xEpB&mPh6wv1CEP2TN`_#UazC-Zx7$yG5meM@0#@0`n&4;T^6gqqoE6#qTxx6R6f!3+usw7;m6kgcGT}j@SPs{7m9}3RXgTS?<SWz;`bBzPrTmq`z9ave8DBkZ<Vf&6CSu&``<Z-{l0^r$Ok_*K>LpS=yK(syH4j*tAtKp=;=d#-!Z<)2R~L5|MHNPs@*axsd_lK=yFE#>{0C%E?!9aVbczMS4?Uu^_;Zeus?llYE-u`ej@$+Y0pb~cY6!%PrqrE{2f`a<-Mk=yk(Rhp}w9o`~5vW-!t_cI(ex2`}tFc0`)z$?>)coQ7@<NeG^rE)30W!zxy#x3g7;*-;Xd(yj^>?NO@x4e4gd6mos;=8h_5CA1Oa%`tgeUmZT4D-jEq+hwiga?D6@DcKB<;TvgvQ^GQExy=s?RQjaQ~K1KUGufDAQrhS}o6O|t#e{VqSgFSxVl;^8TYgGP~M`ilkGxq)4x*zcq?YX((1XbUsy6E(#J^!k$(i=Z&+B4rzy;Z+uG|mj1kN<6;#+7qZvd*V|tqrQ&H*7hs@?Ts(BXFLc?0;~N&rjsDrO0M={CCf*&%<Rpy`#q2`daU+diDHR`ChF1I@Rt~J7|B%PMu%9i7I_;{h4E;UdN@{Pv4;YP~jU@c_KR&D&L(PQ~5-{o2t^s%G6PQ=)3Y8Rr_zeMWv6n|MGyU*N;0?e|e+&DnGR5tn%H1k@^09j68Z+`LWus>U=6+uksHyeq8zC&;L|@sLTP?zwUL9YJYks)o$U`r}TJO)I#}QiCRni^>r>b)5pCb&mw<2yMGi>zVqdpCH{Ja9?7fo={?|GRsK46>votD-LLXl`Kj`qTN~+io6%AEPT>|y{q=RWwO4*@&6sy|eJASU=6`U1PUFY;_V{s6J+R+D9>QDRQ|GPm&Ajb>GFi<_;UaZ(`m?t!R^?$lgu0~c&uN?+-yY|Yx;JQl_=ruaozK3l@`)VItNic}lT`lB20eZvuU*`i(|K)t`@D|){+;%pS)%ff98XjI8%;T{e3$&gjKk>tM|A$9pIPSb_t+De%8&Ifp~uh6Ey{O(oF6>yZy8bb`3K_z<@BmoQ}b15#5m=9&u)IxKc3x<rF1@p7peIx%J_707gm1c_n11a7yVU_x5$TkRX#mKYMg}nq^Np@k`C_G=dHKGKOVw!H!I(LY^WNCVa9oQU3;B=XsfqXJsF3gO$~Mazh7CY%0qo4-_+Cj94Nh6rN7eVL-qMr->dm1{BLbFK0}P#=wFAlZ(SFRZ(kRjVN*Q+_%YWV<J;Gr(7ofeUuo8ARUX<WGQAh+(^Wr47+2xhsmhNPE2pn3b>90x`L92yeD{}PdcLMT-G}eg^XOZ9RX#4`C$zkx7wF%a(^UUP&X?BLb2I<{dA~mIf6o(0pSUjL+t+0;rQjZa`smc&I{%H|?e?d4OB`3@$h*=<`R?*nYXbc;e%CJldF_tht=CcbiS<~YnTu5ZOXuwh9Czn2ece3r)UH4|S6*76+BIB%SD=4c=NR8!=NR8!=Qx{dC_mCSpBh(gxSiIAUfQYB-M4w2zrWnvBeid>(~NJg(~NJg(_%kO-l5V>Ewa&n+~{9FZdadM>q+C=>q+C=>q)ouh;1sJ87EtwKIQiv)1DcB?NsBg{6OV<SH9e)`n6HP)2iObr*HN5qgUfTz23Ear|1`1em^m9|MBCRoO~z$6Z2HL^Hx>9S&w;*pE>LI!=#Tie)fPG{}T!*KQ=qIRh4g3`yI;vW78J({fZxMSAQQlc1nG|XRTUCL}om&N44*^DQ_r$`D4nD{xeL?V=?OM>`GU@xBZ(<f&53$*rdw;``CS|y)I9ipOYUu`I?%~LMw_XKYUy9-75X|AN0E8)x+<q{5P&q<%~_%^HyxaM&-Mu()IO-@;gT>Z&c~eysPF7=S7`9>aBi9`Crx4_5Dqk$M(Y?=<*mpI^tZW8gIV_(;GiR`MsZ?-=NOF>Y=^Lr`;kQ$0$EivxKLPOTFC6ZItgGy{yKQ(=+m^((686ul#>^ZuYlBtilfEM`$;<U!Tc--)?7j>Rjb}|L#!z<!;yIajS;4zv87`s(iOKQ^$?%PFtti|Er1GZ&+5ZuM0ZLcYoTr&0kJ$;_GX2>POpmdZ(!CTcpJwtJQI5%v1IC9@FKweTRNAzFU4}hN@S3Fun1k^h@mSFO=^bYq8y5uV|gT$`2Qqw%uQ^$eFsUl<(Z2##`*k(dX3hUm2z5xmb($xBA=P9pdQq)YO40eQ0$*l|E8v`3hB@S<_Uzg&04^kK%_-JK%?_)KcYlPX^N)-|I#C2S;e1c`3ZA-03|&-^_dAU7@3X-=6o3Z|1#l!$ncQZ{|1m_etu!cbinx`8?2cr@wu|A6{Oj{P$<=475YqXG_)hH*DRa+f9$Rc!R#J&Wj~2R6Ba~ukA-^H{&}MP8?C`F9p*ZKSaB^3toFGr}M(g`_*EV-rTo-*7%b>K0k4tZG7u-zn_?Iogp>-`6TAmaY-3|Kh&wu(H!&XsC|=9q|z1D-m!)G)I1P2;~(E?c~Q;R9^*W=Y@7DIF=`(0`seJsw5Rc7MYkPN`S-Qb7t?--^Tqw8LNurIG<N@6YJK7KsHnz&gnqGo*G|9ht1OlNWH5aQ-(@^U>;AYv`K3pB{`124&RKokijh8ax&2(#{*Pa$$HNvqt`dHgWW7Gd5AVJ(N97Y<sn%6qA$`A)@XJ2=kvd+fEdk#vn5BF#r0+u$>93@z>q>M!`w5wYl^@PkPOWcZ@23TP_xbwD_s-~btnr-|FX;79CB5D@zSn(^_F2y-{9`p$`5kkAVf-%!C_l{oNFx6gTeZ*qd!n3GPw0HO?~AOOJxitkU~F(6#&^eU3(U8nuK%5(@+m$=xBoV-%lK~UB7OgWA3YONeysGLfqBpPp{{=%RQb@qv9ZN;K7VAMQ0Z7V8sE9p_N4O7I(fyxDdI=xozQ-7z5X|Tc=s>L4|9KEd~aYkm9NA7k@1}>tMz>a_g}_$bKk3u=RWvUAiej%Ozm@DpE&NIKb0T5p!W?D`Ij!M##N+>-hXh5?3k?ltB3TsVclZ<@Zo*B+-5zQ@%GcoFY)<dRZergHvaC>s$XI~^mRFWB1QS$yNgu%SOa~%GroK2WnI2WdR=6E=b8R`Ux4+S@xz~0SN-BPWu5<6*FmZuYc*2yiNpMF{Mh_i%J;Zlc;mnPbhqSl=Ez!={)(P|Y~N#^F}{08W3_Gx4`4pWkK#vv3+CfgtfI?j<zxIP<IwotoD@}0r++Yi_wn=UyogxoBRifCT$dB+7xYr=KqozzkJIr>JrAF>%7gFP`LsQ)`pfHMl?UJXHCSKo>b<HT-Ag(9jydj+xn?zSa=6}EzPTSUezxl%ezxnKNpD^6jBl?`jBl?`jBl?`yyZoQH_c(Z8Q&gn(avR`ZkogRH@-dojc<>C<J;pu);+hYeEWPfzI8sj^?OfI`C0Ro@$LD_`1X8de0#n!zCB+h^0DTt#Br_pDv`f6Uq!$FQ~TC@Wqf<S3N<b_L*;AD|HilH|M0FKly6^OjGyiL(lBMF@~!KI@$Kt{w{z|+<y+S~<J;Fer%>ZL>Tmn{j-T!Nj-T!Nj-T!NZhZUtZhZUtZt}OU@1~sg^?k}%o!(miBz$ZAV|;u4lSpr^f5Le?>E|%kdMx2v>oIrE1-1WVulI~^ulJ(M-q8E<*80=-&H6LpTkB8b+v`uaQhB}aYpr|T^*fYrueWXAthbGCueTHFt@U=O#veMpwf;B0z5e%Z`bzJo+xIW{+2(WnZ1XmLw)+?SDD$~z<)3YyH~HK1yh)EABLC=;d1`;$zAp>qpQ-nItouRRH}`|ax9<mS-`o#|#($#b^=$W{@4Tb-g`Gz_2JTzEvgem8|8P>^J~z^3gr1-5`)>Sf_ucr}?z{1`-FM^L_ua83OZ9lP_7jY6?<W}F-cPXo#Cp5+E}ehj+XMR;p}Aw!^8<U|BX;fw<-0GO-sNu}@1Fc>A3yZl^uWGKw9FgI4?k2eun*&ny`p@3|Ht;t{*UqP{U6&m`#;|F=o<fdo!F1Ed~?1#CAR7H=!lVleXVF_d$oUU?}J5GX${qE8`w8<UYVz#Yg+qk(FWVs=QRF}Z|~Q6<v-HCweJ_5U0prb^wPEl_6cKyM=RgnR}B9)LHYJRWcbV~eZE=ypSExIKaFqif7-s8ZzIQV)BExVHwX4zy<cYP=ce<j1omm8bB<`=+SiTlEvnO5`@pdouWZVx-E80Vd#w8XsvVsP^#l9Wk-h!&{J!);V87Zuy+--=zIUkqY*nAovN?f$^62F2^?tgwuO2H}RsC)6&l}&~pEtg1=3y&+VqPVE<m`0i+s_wl->m12Z$DqKee--FG%Zz~520t42A*p~JB(0&+s{XgpY8d`br*HNTF+&SZ_ks)x1Y;I@=ezFqa%w2p8G_+0s1(t?+H9_iWVBFed~FX@$KhL#<!n0x!Z5o=ehNqE7Y>So`3E4h48bzFNAMDM@yvt{jq&H<>Ot^e#FWritmw6_`|1kd93Gs?z(w8f9v_6H+9!8|2Q$v8I5m0XN-*vtMky=a7XZY<<9SR`;Tj$Z@Tpg?g<>1=b`T3c|5;wo~s()ey-|FF69N<=dX1AIlkRK#y9QbmhG*d$9!K}&yUt~UT<~9KzYn_;pmaObb02S+w31#?v{qicQ>34JYS9!Y^lrRR0}?j{-v)@9~~WhuDyPO_PZ<%JO}qiPEo%7Jl**A^Yn1iVJ|Qad0uaP`+2?bL$s%BrFUsJr@l@fZGTbcQ>aDYJprdnesx_5y>?W+Ul6%mSiOg2e8>2vU+`mdwC|=ARnP5W<!@EKmwI-Se_VxbY`j<3>w5K`TjG6&5*@YwZ12GP58=CB(fPFbR<F0pwb$=I*}j=)@T2(N*(v(D<6qm9?>;p-_})c&mi7;x3cRNg$~v^yKR(@*7xa6K_+}hBscCO2t#MTQCzJL0-0bfIe&5AUv>Sc|-<efcJ!cIaIHlY3eD%QlB+*vqbbZ&}t==#2E`Oo&H@=H+@;81M-<dv8=ik4WUavg&L*P9YxAcw5_sYH-c<;rVG)P~M>34V26Z$<ue2;#29$B%{@4F4k>-Q0wXB_bRVSH0g<2(4?i;Gn`ozt#PKkZoH{haXW@%sYjHShC8f1a<?TkrpP-Lmw$!HkD>&GkMQzH9ut&DC>I=aWM^fAgN3*-u{no=!h$R^WXkcjyng9b#Jp?=MBVT~vM~*ZRQwPTqoxf%2R8ri^dDH|01#@AHo<H}^jMIldV`?$Fihxo@=cKl}XSBvNZ`rr$T?!Mn-P&#fC2*ss!8oF90<EBxAx+Q0f-;C(Q!M~d?8_sWcKzgOn&tD)07mGpZkd87LMJp3@e84tz};fM2H)bA?{udmZzXdHOYE&S;N`ncBna>lpcmx~mBP?yJgAJ6#N-si**C9YG!^oe=Z(dnHk9hC3XpBQ)#(EGKsPG2?>cyG|1*nhwOeDRvzs;^`C=Dcv`e69K`dgV=>zV^3)_Yz}Aw(0bg)4T7GevcX7l+(=^HDBf9{ic1>FU6*2_<aZ8?NnC1ZxKG9>wq2?obOFW9rpWX9tdBZpq>+lw-(Ur-wPuG?^Q-0E3SO!=L3QFFx@FN4*1X0m{&``_lR%KQ|G6}>bZVwdD8>_^TOG^Fw5_o^CJ8w@7uijfX<)s9}5l6^7|otcgXU!s{N|9(B=HMfABrh>s#w~sMtL4-f3iDS6$9heFE>Ph87RjetKR#pL5-DJ|1--(C=TL)8h``^t-!es6MX`Y(L=duh@!Err$UH<yHPkjg#=sW4d0)76jh2buPtpK5GvI-ph42pV#d<A~WzFuQRT`+RqI?nG$&KH&P+0{oR)W?+LpLS8IPnR^Ywj@MpV~AKE!1@E&qx{~4YBrxC&TmS6q)U{3WlzFpr?neTM^jgi26(ay$d89BByeztaAT3_#{Snp#S-+muE`gPZgoW_;$?Qs=7*DE8Zacg{g+(wQK&&cV#Fur|WxI-6a<aC}IKihdaXGMm;oy|O8e0v^<O+BxDd!E6!=NYGCe!ag?D>d-myOXP7W}sh~_l$4Pd(M%@nSu7_y?Qsbv)-q$->=5c_I@?KJ)avt+kBoeLg#N?zl?8Rzl?8Rzr1RrbUyZV6W_jWM#oRo`B=YeNch(88bTkwqTB6`jnh;;_<cmI<eR#jH@^}1Jw>edTl%=xI>Gq%Iw96^U8aBBnstcrv#mq6Z_wqj);Y$v*Eyl9r!xKH+^o}#pKYCXyiS&XoSSv2@$GeKD7jvif4rG>sqyV~sqyV~X}IyeEPuP1b-3~Eb-3~Eb$GPfM_GY><o7bhx9=m2Z{J54-@cFVyi-~J^VHnG7~j5siTv<+mcPHu?|Nbbu4>=<eUS09{XWR}=J|q^KFofXN$*xDrl0Rx_jlQRvp&SP@9*52bM^BW>%P_a_I<1I?fcfq<Wu^2k9FT|eEYuJ`1XCb@$LKWSg|tdxw5?vVEk<R08W~IKVVgA;CEqe(#wba{cHA5jBoFs7~kGMiM+JnaNs;;-^Td%zD?|gLPr8Vzjt$wRyyL($NWAn_T_a)1MSH^nDOoXG~?U*X^HgKewy*^`WoNfPm8uo*X6PI5An0@AL85lhu*{0^t#*H|1^HK_aE@>{m=0C+u!r&V}4(0eEav6PWQ#f1Nrki%~0Q?`aZ+@y{GZ*-+LNA@f^@jZ=M5IC;gIk`nkLHJ5%GwOnULt0>7$#cG-~6!nNZ?jYoc`q|>jL?<cil%0Hty|D<+6z5lD9)YiVE-W~sczo{*-MXC^wX9(eO=yUKmxIcO$+#ha=Cc{nPYN!KOgKtBV;M?G;Xc@RF+ys3VZUR4sZh{|!$D*6zvGCKV9OP;K7EU6BpF^9#&%w{4jp1kEIp|n;4jhX|(<GUPWKUA-csL9{jlKpy4L^{q^?zUq;U~}{$(kjEhoBYUA@Jj9Vfb<QepJeMKROncvfWSFMel=~!pZTFF(bO&(IK3h&+dbzt?s35M4Q3e;^}iG>3-M@J47zNmy7S1_HIV`M4y4j!cu0@=G04~Idv5s<g5E2+D3G!udRmCmZF1wZ9AB@7kx1KT3-lDUx|+M_1!r7b{uVI+VUaVMKle*56(?Himq~W2<PRqG<Zea&qModgL4siXfM&WzV>cI8;MSUpMj-qM61zG64huM(f;rtcqlp$9tsae2f%}2X`6?r{|o3i_ystH_LH<Jd}jcBFLh~#wt?mIE~F7{40n%5BpyA`UT_b%9r_R~S_y6k-$Dp~nWXjWB+a6$;V<EpgzyY>7CZxf1$`BM1)h%1gr~zR&{eSLSMUn>3qm+VeWm_A(Qa^0I1OzJi-zDdxFRZf3eTcG+tIJ#?eGtT@XfT7wAanF-$U@t@V$g^C$tyb3GRqS;Er$yv?tsFZic48Y1E?`A$$`d{5^G(I(|?4t%ARYw-LgN(3$We_;vJE_;vUVbQU~|_7d(und+lA!S&%A2;rZSv`U$NqHNpXpWp+8@LF^cycS-Ez7DU0*Q0O1>*0gwc6d8|e2@_SFCknyS*!GMY5MwJxHNnxA>0P-1h;`(qaESaa4WO}+=2FLMF`hLZ-DE<B?;k6Nm`}tF42Yu;7jmPLik;DE&MLL30((of;Xe<;mz<d^dNkYwmU`$|4Im#O4cfESBf^g6D|eUBZOO`ZQz!03$!)d0!~F+!L4YoR6@8GS`w}W7bk=-Cux<oyG$D%g)hS&62d#sci|oIPIMEz6W)bxhIhdqp~v83wB1L9@Na~0iDa$Pb|q-TdT<H&4njDLwuHlQQ?v!#6mEj1!l|@Z6GHfQv^ab_T$B*LlB8AI?h0-AA$$e?m=NBB?tu5e9=a3u;JxTBcrSbk{RsYuwmU@#|4s-OOV%oFSBy5i11<*FB!nBGVYm@|584#I2fiC^0ym+(g#V5ow;*jMTF%#o<$P^hj`X5;!FR*=pbdP-Z9ut18~V!Gka~!gheZqd>R8BEcVTHK(SK+&(F?vdyx?ow3-p6%makv3=r_?!Uq5Ej&!QQ=e$QZBh<*!;{_Ptxe>09mi!$E+p{xZcdwIA3d?O)z8`==Q4X%tffGfkdqIbc!!e!8Ma5?(23?ZDK5dN1wmvaA0`M-t#g?}W3KSeX(PvOtdO!zbSb2JP79KMKNfG^Nq7YSj9ewOwU9u${H<1vg7?m`IPi#CQuE5rA~l?dTdXlYoqFkA}09xVi44;MfS!Uf>`=nZgwxFjK55xo@_Z3I_@n-RjD(N3`F<8WtqDEb6E6n+vN1P`L^o+N~yB7{exU0~5Z@JM(dA)HPK_acN_5yH*UE^rt6qd8g$ZVs0tgo~r4;8OHKaY8sBS^&-m=SB0wdEx8OlCWqo_&T^qJZ?hEqQ&51e5Wj05w1v|l_i89h{u3<^o>VvGy;pZhFg=iH`)wtMj!V^hr+$#5$Kcfll0{XLU<)Q5|;ZlxgUENy#;<4u1W}hlB8Ac$Am>!!k@s)3E`K~8So_ZC3FTX`U?CKJQbY|PlcDED`3$t;AQYxLbyt@R=L*_7Htbxf!h<pz0q!PZ@3TI9qt47MSH+KXuH0IaA&kC+!?Mz2!D{IRod|b+H*N9x)45sM$v_E6rM*2&nAQ?qs!st^uc6b-%KWi+Y!PO(U;(t=#Pnn@B(xhyo^2&{tr5z5MG=lKbg>a5?uf<;JYUY;o8YsrO#^9ckN-(N8$U>uIQt1S2!JQ54Wd}(+S~zXdk#A{21C7?n_?^4?w%1o#8HUW3&$37*0W@FH@4Q^>GTH3BQ0BO}e(9Bm59L4}J(vLubRY>DM&09V~hsoCfD5gk^6`ROX3Q%oii!k<9z6&~)e8ewy%Vv=_V@9*wqwN5i+E&Ee+E`?nCnH>1Vjo8h8pKDa2HhY-$%=7sYzzvm)^bE8FIGw<gnghOaqxGZyY2yG3wW=;<g!lMY`<!E16bO5{@UV-+8doz!(Kv%*m;5_t|^jRMIupOKSZi`NYCvv{E^_{D23E?*Ae0V<RY8yg$0wFAWndaOUKFm2Re3J9Hn(th#MhN#uyTV;LC;Jn^1JQnPKhC#-zVlGHW&Bv3;xP~%0KXD%pBeF3hrS8djDJ=(9$Ajo(~jm^N&2%xq!CZ}c}M5<A9Njji0_?2Ps8QNzZO~({tw@M6@3#PMR|vz1K?rsV`wM%496-*+2t6*ld0$P=qvCrzBdZ(3!AbYLTkZNrpeTCGI<Eg_geDZmXy`x*@=8R@tN?e)NwL81HK%Oy7A9%B82ZiABOLM??fZ;op5cm16&)v8LbcB4FB$E{nODbA^Zt?5dH+tM3=#t@LqI2ycf<u--a{bv*>>KEPMsM42w!z82*(u`jx-;q5I)|@DlWGcnLfYoe$50m!iwyrSJjtAbbG6iv9^-h3nCl(x&wY;YZL8@FQ?fGy?a8+oKP|?cq9TUD&jRaHDwK5|4(2@L!JBKOD^x!h6tD@E&*(x)WXm&qCjYXTb~59q<Bp7y2>03;qTD4gLkbD@ki8Nwb7-SM(mZE1Zr#0H?#<(ME71+Cuo}c>e#5$Ad{)n<r_O5PkxE9DV{Gfewd9z=P32@L;$FnhLjo|8=zf<7k!;-iW>fZ-l2)UMcr_bOXE|ehGaUehHq4PJ$=G)6nVgbdEKRzPLnRiSG9G-ER6;bfK@W7cv$^XZyy+Y{ri0>%Ot{I%7@L^Nl@^v3ZGdG)U4a<DdZ{+zsstcZ2((>2N=|2ihI(0pE=_gztv`cC<=a{-#VG{9no^W8@NLY)&*_j9en!Zgf4o8(xUM1TTbVqZ8rT@ayO__;uJr-+?{&Z}cDdZ}@J;U8=9XskBEb<JGj!Alh#b<J+|7aN2t~b?t^WfCn?y&AcZp^I{9ezL_V551<>JYxAn`Qgpg=Z5|e$hfZ>?&D+9D(3hQS^Stmrbc1v4x*+^3`ZN41T!;BV=7KteaC`KLq-*oAa8GnZ(zSV8_z`q4Jeal+cH{ZK5Rcc;C_FqKgX1w3eG!hLuc0sczB`=Hhx^jHeE$V>xbJu`^7)H=CcHKtZ^dH`x)@%IzJbn#-+-r}6W}TE5VRjGdM7*tPK`%xv;ul3T%ONLpcUZ7ly4?F2c8L!LC3>m;0|baSoC(d16&0y50~edRjB)7>bjWY%_U}1*O?q|0x^bqkKq{ohz``V19{(xmVir8-#e*$dD`YJ`eP3I20RBIk4}Nd!`;y#@DTFrPNY)rRE{NFBOW#5k%Cr-Q{Y<olCB<F2d)RVL>s~_;WYF?I1O%x-UqjX??D^D_rQ0cwcuKmP5AzJ+!c?uXbZS4+!1{Q?g;lpd%!*6ZfIAy8~iZ(5d1LQhT}>(>Z4(}K72RY25!T5g-6Ech%xc#jP{17#pA_zJc$m0d!wDvA-?ZU<MV00v?KZc7<8KNctiMn2%iaej7O_@Jc_o4JEDEi{%{|7H2OR|8h#Vq0E?DQ*8C=XT|8=_kDz7YWIn5oJ_5I<e7(>va4+~NbSV53JQtk;iynvP!hfK0>_5=z@T0Uzf3z3eAATNv3Vt5mfX;<Cz*5h-9J4IPs80Q>Q{S@GJ(;#?MSpZb`@mh`q3CFMC_Dvy6Bd>Hrtr7$aWok|9gkn)aSpu-pMwwKOS<>b{qXznJLnqt9e4@)7Q6&rioOjmg}0&`;jQpD=ppzJWfRUDuScGEB%yyMX-<N_OVaut{2hD(-3_0B&!GF@Gw{#odH82IH^-H7<U_BA^TD~$+_0#8SGZtYe~8Z$1<>!{ALCjmuHU2A!}9s}q!AV0eD_B_|IxXYR`M^z=Y`1E98bPm5G@2>jDMCdu0NsqVev)3MK8eL!spR%;PddO=x4C#5%^R1a6FEp$Iv5ijU@fq?dUOB$|dD1f)<90z&E00;2YrzXn9yP1+D;BM{B^Mx5H9*Iras#2rMD|4SFLiA^aIy0hSOxf>wvCbF3rO^B8S$l(slbzes-+M!$t6gv+4kVF}^#=%?_fv~_vfK{y4iK^s(!#|`nQhL(n_!By}jT}kvdxFlR0y%jDF7ey<=Md4y-CAb(|0<8>}fJ>oO;3||&_``TzzKX|5^b7bTd>oCz$Km(T&*Asr_tA6k`|t_$f8Z1F2OL+*@iqDp{5AX~`T_g_-xZd1OMB<q+D6!{e}wNRgu{ez8$#HuXN0?<Jz-go)phjxs{ve#5H@Q?;TnW+9YVMvA^aeEA1w3gUrE>IUSTso3+H9d6uzE$QaCsBq_CN9h0mZTV7XpwNz&Jcjqo8t*j&qmPZPrX31PWLrL{^*E}859^uIK__D|lwcLM)|Gy9vtpKbWR*)g71;zt~5t@6k-87DdZpFGe$A#X4^{|lDQ#K8'

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
