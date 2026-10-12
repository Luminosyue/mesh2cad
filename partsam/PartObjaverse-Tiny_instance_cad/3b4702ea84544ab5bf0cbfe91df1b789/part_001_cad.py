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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b4702ea84544ab5bf0cbfe91df1b789/part_001.stl', 'relative_path': '3b4702ea84544ab5bf0cbfe91df1b789/part_001.stl', 'source_sha256': '157760d08b5ae8905b038d986d6c758a46c21a01017f0f15b8d9a1a993fade1d', 'input_faces': 1059, 'input_vertices': 625, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26481810212135315, -0.16266709566116333, -0.49999967217445374], [0.2557986080646515, 0.23831720650196075, 0.4999999403953552]]}
GEOMETRY_BASE85 = 'c$}r32Xqz1+yD0l=_Q1sH04qxgoI9zDwkeD0O_5J6s2RN{J_EmL}`i$2+9w+fb^nt0wgRYgiu6@NK3*+#Tco9gd**oXP)oe?45i6=lsw6;(5;Zlkd)*ot>SX*`1v|c8SXMQVE0qRWL?YcxhUx#)d&r$S7e<8WuBQ#E@a{*BCo~ip?l0efp<#QKuf!UHaIJNyZ1ELx;UTBqp?xJ+#U22B8u5(Bb1^Cd3RLJ7`?Y&|&1a89e&^VZwj^-NECBiNCAXuM-(zuNxL&|H%Ho{8vB}!JT;T=R-nWZO$Dd_0)b4-^}9MzZ`zV$2SJ~q<7RmzbTOKzTf<W)mQoG>6Ne2yC(NLW6j5?H}<nb7GI@TzWcYZB&jn7?WEruV^=0yeP`w11LQl+@1$=ZQ8|grF*i<@W1}H`^MjJocU|fr)4Q4-kiL;nO#1d2F`WPMgPi|}5a}CrpUQkZUk7vk4f>w2mdD(ZdAOOycZMvH=^fYqIwbv5&82S?$t&yE`Ce&LmTR1Y^SLuw=40Pn?TGwc!+M<0s@HeP{bp4E^^nDPG|C-k_02r&oBKGudDhprr*L}ZyYtjyKRt=dcji+*-cvQ$Uj*Owne;umpC`(Ci+xMx?|gpqY9QZpw!yDf-<}#B7bv~*ReCe>QKGdyxT-z=(dw)A;PrE}?@rH_<#e2xC(G%~H89b7T&|WoWj&j}3`n#dm+Qn1={tt@mcEhEPnO^Q`aQ1yT)lBzeWdT|m??c%P*tD(dRiVe*{>*l$NpI|y}M(sqcXoI(FwA=y9eyF)`R^?`vl+e&ri1c&RkcHT93<oIPsV@A6Il^xn22sd6cj6@k|{l+np!-$x&-QMn=cWR$t}gzBcHh)%WI;Qtbl!52bIUw)Q>0n(u87+1b)}1#LWPO>bu3_wiMFXZ8i@J94E;-$-pN_v^?$&*e|gl;t#jkGaTxGVgcKM0s59jDhmF+*w=MFWoJP+xcv6Cz+|TJ=rUlJ#DRjXXYjDr^+0V>CKTH_RIRdGnm_7*=*@MfBWLR)H}VnpDNus$$DIlJ8!{%E6I9X#+|0pcb2`*`Tw?B=3~E|pZ8m3w=9qQ?K=D9?`}OgEYt69kK-D4IgoGM`y$21Pd_i~$GkS_Vj$mn<9DBY%v|?T&yg1b`S!oQx+LrA<^uLZ3!jncljDAs+iy;nzEQa(m;c}FG<n`{Oo9K(X|9Kc-2dDd$K?sV&-I^tPUhqIr|@BGd-Gl|{}enN@H*0b&+VX;fIjM9`Kq1k`FO9R+qRT|zLt;oy3o>leWZ8Kyl2YxqsF^!hYnbM?|28_%(!J*+q36Rbc)q?rl%eX<a>e+AGP|%#^sz(=8*}qey=a$em-Ua`|a{aOMgI<1gU?|VZT&}Y@f!3UFQS&_G_)UT^$_Ge!p4c<$2%p1NT?g`mtZ@Ms0cAd*;aeJty}blGn$Ji?TnpXD?2b=}+#Iz7ZSA{c!dYAK(6G{zF#ZGhl=CO?LzCZ=b)oYW1BHavcifo0F;?4(MMwdQ7$lcX&YGeQBNCuj}M`E>CPjpZ)5-Gut=4=MUSVK<SmQr*}Q_EvNF0yeQ9;@PK|!KFhhDE3Q8!>peMBUSGQJOj|Cmcjw6koDcdj_w!qPU7VZ=AN`nW=bCT-C;4(9-<@7BpzldNa3P?N{=qmo&F8r6*(>C6**8q{Jui8`lfE;l8`oQ@P%h8ij(lC5sLA<+{&L#7Uq4^<ODD>6`$0eH%IwMgYT}J}xjks7yuMsF!>-8vB%YGKz5Jz<)_O3G&y>DtR^KD*_u;uzS>A+qr0)rvbH-X8KOg0>Cqzl#C_194{QcQ#(s#A&z`oI-iQI49aK1lGXvx0b4<CC2KKH}wyy(6vkDsr~^Lah?>&L$*%Q58aak>3iUH0QLq;K?R-}%%)Ia_7EN$F>C`Hf>Q;@F@2;7#js9ZhHd*v9we@$|nS^KoCi&VI*4=^L}zcOFfazB6o`tT+4HHRQPII<m$mf6u+#d|l{1`e(<H1?(Tskomj%Kjh;&JWcwZkk1pj9ddu=JlswC?vQbb*7oTzi*x#Fi5MRb^7v>5OWzR@_LH@o&O=uY%6znO-;5h4eY4mBnZGCf5s$xdQJlW|beWGM`GCydeXuO2*T!Y@z#novQRA#LIhp-^;nMe%N#y&M>jP!}&K;k{25O&vKH7tGdzAF`en$7rv{ka7F}BUz7pNXwTl-00^`ELfm9P3q-S_Js#`l%JJ}&tA=r@$Fj~9NvmR=u6yuLP$=)TIw*!l*SKQrTFd3;%svVZXUT08XmT6^~M)&299;#|*FLw(Pq?yKv1OD@jmTE<kV*==NbJe%+DwYE3ap52?)NM9cpbYJy{y07{lzkF1GsQaqDZCW6G)z5qGM9KZSHoPKzy&raL2$sHCEy1UM@T|YTN2b5tp6`=0N6UWRT%Rs|N6=D!zPcGH`+3j0y?X*(@5;~VA8_BYZoTyN{#N(B<B{&G<6XCa%ZcZA&#h^)Jj!?eS<+{ma>UN$a(0j5=hg7`@;=|bj(zhP`$mT5+a~k<_RR`1e`DP=u7`+Meb4*aeq7GOP35@ec=(fSC+7FzoIbX>&-JVO?%UZ{tiIDzGCojx<?HDkPm3N2m_K}#-uV8>ZrLvOmE`-e`)RU%l<zhx$nv`%?3U$stT`op<J`+Jvfi>@3+OwaR=Fzozvh7S_5RbndJX5V_2;gQUrOIBW-gaL`VHsm1)P7#aUb8kY7nO{635qnMr(P#T<+rRqn~#q$8&$aJHPbpp)=%tw*5ONj~DK|T+aN{rSHD3`Gsd8|AsPubLEX)vRt8=KI4V!yQR{%m+T?u?;Po;IiD46rEe4smhIp5$3GXXzP&_<OmCzgmFZpI4B9EvYyF<r*ZMuLuaD!pf7?h2=%YV$ebbBm5Bv6z^@ICE<D0tddp1tx^0emjzO111UAv>^Td!;78~biZU)_i6zPb;09xTB5^vz-)<AUz1=L=)m!yPg|Z9LU|SK2x`p4yillD_BFJS*k-d+|cHPuJS{+hzW0p4QnyK9?%rJ0A<*vvAz@K<(epe_BE2Z*Dm8W1#kIeDQ(wjgoK4^X^PP!{`0;&Oh??lHhZ_*gtQ~=}QzwyGr2ukfJZP20AXI=pE@h!z!(le?Onb<q1xgzH#uz=X}1ne{i?^OZtwQe@I`AzpmiKt%1&$u{U9Bp!22s>U=qZ4{Z(DPKr$9{NuvEu$D*p_A=d8%kuyGNm?_D@2oaT9+&f3e|cP<Lglww+pTxJD-^sn;B};Y{W?;<_j<AU=A&INX2G*tq<?jU&vjwser2;PXV#L%*5lHB)eqZkp_>A=E8TZIEhmrH@g#nO{9Vat*&giaKgsssc|1`1p5pn@pB(4@=h1`p(hrN0_2z!|A=lf3ucdE<&y&9ESzo>`?tQ#Yo`=_7_Gwp6&x2Lg`Zu3V;eP(=HtD;<H%s6CtQVK_`2N|leWg_3dG%W#T(SC&KMV8yYG%t6tMAD_ErHwr;7dOF6duRt>F@B%R^JSMCVlgdI~T3KtN1Ox-$>uj*Vpsy(s#yu%=yn7?Bg4`pL0Jy^X^5f?=FITK0-bT-*WorbLDvI`MddLt8dyq;(5ZG1?BOY$ENb}mb-%XJT=Ygt9mn@wY=(+e#i73@_4e!rCNP6b_CxiJiIP_=Z;D2??~bNpK<=mcW+rQ^LG?z#rY3z`Ke4l-p2h;wNu=F_BUex&q$tc&+MLJ^*x1WVjOI8*(ZH*8`|4R9^Vg?VL##t+C%rNR^PRMA<CbfYV{pK3vqu{mhazQ&L@2%@-es1y_}D6tM;q%xQaiM=f#npbjj+QC7Pq3JSTng_w>8*hULB9?GdtHSHAbX9(-5NNq^CG?$>W9KP}AXdiVNzf1-T7Khb?P{wiPZ$CR)254vxETI8zL*ZW&<dab`zzTRKyzUr@(ulfhWc;T~OBO)37OpLEzz4&@=pPhYt{eD&V_5JG4v&z?>JCv_KcX;bZe?C(AYtL(bKAt<2Z<aYKeb@Ctmwb*(pI6j;<LcfEKJ}wL*LaT$_sQnljrRGR-_TpW_n)df-uVra=T$P|XUX4d*SndOz`l0<I<v2{uk{1USJ$cQX1Oa?U+*7W_5PK<e*M}X<o;CVuk{bg*ZT+KS?k&IZ*3e=zCMm9Umr)j`Do*a^7U~<`T96wR*Pc4Nkx9%yujsAzCOMvUmstTua7V0vtfK(djAh!@Bfu=JfDr{))tq2(re?9<Ck~2oVjOk{t2AF*B`~>n(GJ7$N78~mq#1Fl&_Cp_DP@eezoyP`TBU|-nxC2H6QQ&!w-*FaeMW>-|(2z`S;rWiJ9;X_b=N0jOTc!^!586`-%1&q_5pCxso<Y-|znFY?xfH;dlS9`Oc?y9;cE^Z<c@S_ko(P`ZxFGU$$_+;CnymxDv8e`r3Hp^|f)w>uckVpReA#U8%snHtu**rbu7E4_Cf^AMUnK<Mi!%$@GpIv-rL}b&m912MhX)J7(%(_Pyg2&l@`)9c5p8zR-R3eBnt=;__?HDekn4fctd~y~F<XM?TLxW?Cj6m-gIbziQhik6U}rvS-!$QKr+L%gn5f($}Bk9N7~%z4qK^PfC=&-@M1;(c1&HH{DnBEynu!($}A7m9Ia~I-Z+50v^|kN8B%H<CpHc(pK~M^&;O+YyErQyJ@~UFP@bAI|H3x-B;(={i4uL-*&>|xZQ~4{Iz)rkI`eNwLN?1F>F}Rq0c8PU!PA_zCNF<`<Pep^VNHkmv~;!Z~h0qKL2CpUc$aMkL1ad!Rv>#c`C2(9e;VA%H8cBUgy-&<ue``d2jK2pEiHx$y;)_Os~zGx$-q<zsLcZzdfT3-~T5q*d3_dy7DiSzCK@P6j&>Lzj?m`al83?(cZHZNZK8+{cFDYv^w|ysgKzIm*+Fh@2<-G0eiv6(%0uXm2aA_%Xv=o!5;2c3x)B#tu{}q`>NkozCKT@`+9o)zE}6X>C@ie@~s@p&zrfUcwV|tL!O^~#=bqHgO6|8CgMJ=BG1nk>LYzMFKs+L%k^1!I`3DX$1Xfa`ue=O^7VOj*KqdTU%$lb3FoWyD>(n4MZE6fW_>PC;f-7l{e7$Ed*8R}KJJqpMPhls`g=zB`u)E>_!b|R_Flsk9I{vbt-S|v2bY$<{@%nD^11Z&=LmbTwbJ)n51{$p^#GdhT@Rq=qt*lHzIs1ZJX`wudnjjdn>-G`_g2MAN?(8f<>#yXOGI)$TL0<wwf@uVYyGF6ukJ%i^pU>)epC7S`%UHR&x4LH+1KB1`uQ05m9M|w^z*g!`uk0<uf5;YeU*>9<Sedd{XK7~_Oa5}pC2_}txIv0o+EwzeYBsC^XMsGU9RiZ`&&=N>%2Z#e-B=%^g*fGdvjOiX!eW6%InMc`|%~K@Av+_N-FzW|L+bh92ck_oS`Ay?`Z1;TvdC-1-#zFCdLJ9hhfv>eER{u&orv7jSJL1{e1PlxLOkX+PVwpdHCA83wO2iyzWz5cVU(@;yHic^&XCJTfB9@YQ2XUUYdPv-H69gmi;vuKI=^E5e?bb`c>Wc_9wcp-m6BmhVQ#h#ud??eQmvsIRw78-o_I#B0f<2^z+qzt54_gGH5H_FNe$V!c~11r#EYJ|NStT$FCY^c-+<cXS3$3ylzZer(~~Ho7cr^>z(|3wce>#5B|NjZpvQ!BTldNKkgGB9}0B6J8IA3^xC+f``-8Rny=2IUp^?mpRdYadm((^b!(p5D|miK>t}S|k+z7}6@R>*k4x`Y;rsQUD!txMDqrs>HDBHTo3%G`zpt$))P41Qp?rNkq3-MH_4S0x*Vhy3zW2RYo!#tf>ob+Fug_F|&N@%{G5zHFbhR$j>^qy^S4R(LUt34&Sw5G2Z9S@=f32B(?ywL1l6`Gmt8sS)`=?4zl<86y%KRNGZnBScw)VT7Qmnqd&Q|&QI$P%__xL*iZGEru{nq!cC?L;=zMfh4)p}+>U%jV;udip;eRVzh`C2~udS*Xgt><4+#K%|rb*>!CzP7I0wQ{QT{nml6biw!Shs~8=^6~29@~WqtzqTG;_Z|0^rug{UdU)Me>*1BJuZP!twI1GFRe+yo^l^Xno6^_U`FmD(<#|l~yMQ&l;ro6^U|-|p`AY4(17q!F-mmtZg0VJ*uQ&a>h7DWzc(m^zJR5%H<JmLC=er5dhTnL6(!R4$zW!Z?b7K}ikLllWY<z%pzTb)HzMfwHPQ<nG=}~L@w`WB2`GT*1x1xOgyA|i=Nyn`Dn9)s-T7CUH8s+QX(U{xXC0Ns|dRD&v{f=i_r-VS)yM51V{GLzyZpg8xN@Ae$xUzcj{iyc6lCifp&%bEjD|z+|#QeVR_fU>F_}ceSuKJHSAMHCV<?G*Jxndvrlv5qAEA}bM<NLjs?t9-4!q>kS(|zx})BYMKtjDFkUvurPdBS>J>iae4{yNgvzmIb!)#dcPtNMIrr+oc8JLmp-oL>8$&TcsPJ4k%T=g11>>%SkruT|gunWxKeJ)h{q>GA!b>)Tt0t-k*KpyzQ>zRokAvwyEBe=pXf7+=rYcZ>EyC8h89GMb-zZt-`HX7|@Q{jK?YU!OaOzXur}mSioD_xnoto`oe2Sbf)j`kk@16Yuw%@b&LE?Y2QbThq($L%aBVRommiOi$%HVk8ie-zZ@WA8h%gmQ4DmH1H?2BkKKseNtPyR%FBf+c&iZa#7Wx=%h9y=O1wp^d)c*I1e;0I1jiS^i^;<a2M!X;4a{Qpf|w(fWvI8)ojcZ#IvDuz_Y=XgIHe=Vx}PO1?>&)1s)3>2PPd4epl@G9T6j-!@w_#ZLf$Z2`vu(TkQ9Yh?@xFyU?@XyWkrl=8L>O6R{rpDVTH~cs+Qdh)p66h*%1p4qgiW06{!a#1Ro&MI<AL7eg0;7lRjwcp=J^CE_uHI2A#B5<z@G#9t!*5OEE90!+Fad=2atF<HbU5yKF~4H3kJMHGNOHCQKsDTtpy2ZJeyON+Q9xR}t(&>rAWq4`9Ngk~DdBf&GEm%%geyKkYC&$kHTZ$$JL=X-#NzR-T))*{*j@%A>@MqEWiRS{v(aBy1@t?;{6_)TkUqck<3)xkBu`Jws1wMEnt(FFNWzKx+xz)g^b_<=ZvY#aZMv=;Knk34C6K5QfY2W|Ez=vi=I96N0%y@9kpA<fs&W#F&DR3D^OQ8#5oJ(m?x16mVYN<?Xcx0l8?;#MMBi<kzT0d6Rw5w<tNwpQ3iX+}fe1J@E!8^5cK-!#NFO4AnF8C(Nps|BqMZi_Tg&}eWJxE-_ucrLE%Qqa=i4Y=0lLg#_o;kT*Kt6-Oi{UWA7cPSQidtbz1=rgbj{lk9f0SnW%@d)B^BE~|eKwaSR_<K8o_(u^xK*vH=9^3Kv0mP4%^6tm)_FMAUk3Qx;Gz&Z)=VLl_2AJ~SfpYD@w(;24L2N&WZN${q(IA!u&9?M?|Jr!_zu5KyWjKib?_Z=#gQkMhz^9-m!6)%s;$tEba4rsm_d}0^_k#~W6Tykdhd8$=SDqlwkAgS>niot#d>on&Oqz(ipP^nUKZ^Uv<38#m5B8IVJhISl<VBt3!~TYdaH79+qE8_1D59%~P6*;Y2;zaz9$>nCDv9fXv@G~#5#>d^CZY;73_)B8S{|&f`G(NZ;9AhOM$UCk+z0y~038A@i*mdMeHl#s3iTEB5yX+u+TciVD6}THCXON0ay(_BHNnk-=p7vQ%eBCbp`F2v!L6X3z@0FTw8Am8L4CKuHsZ%(9}h(Q3(W$5EY9giBBns6f~n7GZ*aeJ6`Y13_CULWN&AC6;NKC%e~S16`iqDm(4o*j!G9t>aYqrIM0A682M-r9Ktw-iH*hzk>4zZx96>w*K|BW93H%<kGqe-9GdLRB5gZNffar+&Xb<iR?FR0KvUWubz;X5m4}}f~4}lJY4hIhdkAU_A_rr0<K)(QIh;vy+od0xa5I96=F%fG7e{N&_0!scD_?vhk#_**WzbS}AgE)vQKo@~Y7lJDwk5W*|lQ=>|H4&Ad6~UFjrKx{_mV#CUmjbK&E21nFkyj|nNg58V1`Y>Them*_gYzMXUqTSupq0Q>x1?q8cO`Hol(h_k_!Z0Xyn-Mujvx*}l)$+uf#W3pQS9pn5!;|!!P~%Fpqs&4z~i7}!AYV`oDk6%`B1)%ppC(#l%^4WL%*#LjRe;RzXZ(%ehHj_{m}l7LleQr!N;HpU{d-mF_rBcj*0Xa@K*3<=+EFcMKlu;k03sRAU=v9c2K<;tUIC2z|D{sF$Hm~!9l#w;2>^_wDDllIB-*N6Vz!F)b|hIbI>?2U6-Wk_&W}q4$gqagX3{*8Hgijixk8!L63s-p&cjUZ}Jln#Lb}&aC7huBd5N0Ahw~ud=ESZu?_v}Hq_k&Xso60jkWa2vFN8_QKw%Z_Mz{J0e=UjI{gmX1bhP98{uzN-_*udVEYOqCoQ$D|Dp~47u$%{GYmc7kah`TeoI7D5I^ga(z87=-MhbT@Vz?e1~5J2(=&W!XjL%XBR#b7eG=&na1{2@5kcG)LEHn{-NLm0?$Au|M+V<Z&4ZQ(&&U2hfmQ^U2h+V%7_=&)64F*e8sh6>KXh+Q_rk=t@i)yoOfqujB8WeP&H;Z2{t~(XOu7h6dH#WXN&f;<`o%~)-QfHGiHI54&m{01=tA%uF#Y}-^7{+rCeB6>{|UVYE+itqh=S021~Wa|(DTp_&|To&A~uUy4qXQR68a%@8TbR}Qs^=xXKsgh6Ld3p6IeY@5g&x^1|I~UMG&jGAmSqk;;qo-;H}_AmU0v4rRzfI9fPlnuPxUGX@3MU&12A<0?j+n90CP#et2!c`N1`yt%GvrI@DZ9YvdV*Ag%(XG7x9uT&a6zV!DrR25u;{P7v!g{QW1+G0p9KV&l0V;^pdZgYWehLhFM`n}A7Mf?J|}5vzHD8qg?k86#(IqZIgcXcU;VosrX*kfuW0f!`428!n=Ojn8izTh4hWZf)b|Mbht~ZNP45J7^nlJ8&}cIE(f&T5xR<;}OIW(A?k%a1ivS!5jp>h9KSoJq_Lht_N)jt_Q9QZ3eCjt^;ijChY~T18$5UZUY?&CjAE72D}8C4qgJj0Bvbwz5s4(W1R<X3tkDm0$vIBAc$)Qu@(qoCVdrL6Wj<v+!Fc*xFxs+G!onb+#FgL+#H-_V_j!sCjAtg1pW#-8ax{3o|wjnY6d^ERsn}X-vEb#BXPY%;#!G>udW-?2GBRa4Zzi*)xg!k5zsJj1UMX872IANW3-44&^N&yz)jI7G)2GA6n;bW8>9~Cn_vgHGc+398LZ|yqA`Y(wg;281CvI9!%^mS(Dh(Sa~k&=q-Vf2h1L);0YUsef_NgGUuZ384e&FA)xh61z@#<72G}Ozg~3`Kf7b+82gg7sfJv8tW5Dkrh!@-VSQg`W7Q<KXNl2GLmw=Zb-(}GE!OOr)5yXq26Tvi(LC>yJp$owav3)9ZB3RYkR0Q!91aUnZKWETf$!6#j@MiE>1aTy^9yk(A&o*?=N%x>xQ1Y_yH}SvFdSD9T$I!aqx;U4Qjhu5#O!Fr+zw<lvF_`q3kuxVl>_HHxL8%?2L2b62IUnMyMo#-6CQUJN=B7zEAc!|YQ@|U+s;!e=fu?{{kna@)@pCA(zvuXyI2>&<1{{MnM@;vSbWeE#dKr8Iyc=qQcZ1ys;_nf}2NA@l5X5QF%izn{pPC;grh8@@YnGt@YYAQqy<p_Ln<J+2w+`-E)VM%QW5_j>PmL+WE1~UdIpYp-TPWq%7J30(6JtyrL?iTtjWEVEMYKfU*%D)n>PuUoZ)<@uraiQsg=t)A2R#jLiN0Qqzr>B9)s397o45`%!pIrliR(hc!KC%T>(Fl0JqGbL=yN0Io`jh0Q>biTp?s&oi=pGei^1<fBWyYSTLju0X%ILF?UXniWvU0=0xoXjca|a0qF~Zjz#-sL2;yL95pXcLoQ>a!mJv}FS`J(eX^7vp@%z*M(0<_l;I1Niis)|Rcb`4L-4MhBpaa1Jz;8jjg1aJ5;z}Yqi>M6k0<I{cf`|?X;%EeMN9gNdQaiXKI0{-BTp9Tj7e_r-M1&x}5Y%Y}L@DH53U&HAA{coGqaN*ua@bELXc=fZa0eViPee58EE?tRj_8Ow>xl9WL`0$fqHru-5nXVu-iCIDb^+5nae9Y+-r#rW^uGKQ^d$HcI35}Yjt3uxnqU+89YzrU2E7cXcl7kWf1{1xm;cw6^A4SO1%h}dbO(4RcrSDhcrSPpbR&2p_C-w3>GWLG09+7%(=+SW20ypn0bfKApELNGo}TS9p!W@C3gW5Iqu{CF$<RIE$>9G$_k#CgKmS1xe+B&-JWA}hg@~%qykIIn@m**OFe&|JCiD|9>00n~5pzY1KoGkS#JiA|esdMN989_jd=>mVg7^tE7W@SK9C`@+9Q+iz3%m<uARdmgj=(v42i|ZnZF`FLdLMBLb$<%&^(Z19bsvv5x(9I>=ixBg>0ZQdI1j&}4WENvv~Z@S&19k-k<ywH)vog4oRNlt^Mb2FM}n(@M?q(RXW$%+!u7HO=V3W`6?7+f6*v~U7aR*d1l<Ha1l|Rm44#ZOq4-@(J9!u9g>;yuEe*r@A#G?mU&M3`-p941*6<M18XwX^-~!;n&<5ZJ$cK28!O!Zwp}oMQ&B49FEfB;GXfv<_{3f(1xE`L1>x(ET;x#;r7XZJCcn#0lqz%AtfFq&x!S#_R@tfG!8R%*7dK*7`*Tb_or6)dvG`FBP!K5^|atnVG=drQY2Im3SfsO{(0gtiqem}#$*MUEUjscHBdg2rj^KINutOd`6wgS%tw}AeQ{;36+`YY0J!FR!`ZzdfD{T4h5JQ6|t4fJpDH{f(A?K>TR6SqWp=7U>;=Rs4z^T1aS#HtMt7ew12zKZQ@Z8?48@0K*guR))HDTo_DpMxog>qDP{DW0Njkj@3q#rae1gxY}`r-<)CsU6(I-^2xx$8`LDJ@_-|JK)d2W1w$<$AIfV3xW%x&DFtm+8gKdYw%al7T~YI|A9J;oH3DjGW1O&XFMgI3OxfpgJUM9_g3_dN<Ehm%lS`(bqBOLnAXhD`WssFLi!A>-ksCCCVD4J@8Rg3Exn(i_cXMAlist?`c8V+Lhn>)y(YbHp?53vE``=|zAs{}h_|8NgWm=Z7LiNjTU5j)8*4C_g7~7)p+dWfC=0!3W1eZy5@W;Y3k?B}5!*(Ict=D}{AL(*D0nEg4}*>Z55jNWg$@G`Lz;J?W5A>%!GoZ0Lq~!KLq|YIf=7TyL&t!}piH9?#KWOO!9!6W!x45%dOPxdWaE98Lm5VZM<7i(q#?ay;~>6e<2t^DdcFm}EP}W^)DE_z9Oa>9!F_RFdLnw@9L<Ez7V)u&St9yCXM<-WO&@3va54O*5VQ}t5I7&S2RI+N2(%}-C(1@#(4YnCqMt($2V+|>@(6~n^30EY=Ev_<8499|#lXc8#IGQT3quQl3t%6_cBCr`EetM<G(|1tD~k4S$MM+Vg+PmdABuP+;yUy%@B(puzZCHS^h5ANY`+ct89W%*uM@fkd=b~|1!xiQ0_3+EItxs{U5nqZ0k49t2Co9IMEP%{?2o|N2x2#MC3q!%OZ)+jYZi1GnDkfhEO0V{_`Hpe>jL_u3-DAQMf@A|SMW-dV<7Zr@E{z|K<G+~?}X<>T@atg{tBZWsXmF%!%K!10+X&r*;nIuh^tT^Dx#B!*T7Z4uj22a;2|Q~i|8w&Jc9UTXdm#);F2PGi*Sng4ne#fLA(#z3%n1!0Xhi00sJ565b&>}F6jG`5`w!#*@8;s`hWdz+j9QV{kq}vKXKE4>HBGl^_M+GUfvH?x<uus?>USh@gFVj*iEZCjQ;@~C7*K'

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
