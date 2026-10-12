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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_000.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_000.stl', 'source_sha256': '821ed7be4ad00c7440ac353a3b6a3db5532ae459772c729fd736477cc3522c9f', 'input_faces': 1014, 'input_vertices': 604, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1314249038696289, -0.22570884227752686, -0.027844706550240517], [0.1587013304233551, 0.4192394018173218, 0.28335732221603394]]}
GEOMETRY_BASE85 = 'c$}r32b5G*wuW!D1SLo|AfW&yi7h!u=t3k3N)`}-LIlG&h=3rdSRw)@5D^2(0!2ZP93)ARL=jL#KvA#_GXoe0M+`Xn&c5f{HMdUP_tsnQvDRMyzyIFnoPAHew^uK^b~>j(S<n8f;++`qb?s;~&l4-=mGwps88Pbi!9zyo4jVo;;+6Du`KLJJ`d-&{?Hln%d-v72Wyr|EBWhd~t<hp=(;9W6HHO|bV$_I1!v@|p;+7$zw;Ocl$RS1_dE21jLyTXuaovV>q77=*i9QhhKmIEsIZXK=wbel4`GrUFB(*`+x8;TC@xLw3&|}qVeC+#9yy`LHqjNg?daB}PTYuG@&7nH=s2-bF($??9r*-0El`GhKrrz<9A6KwoDojsQn7&;w|BJI*{dzXOZQC7laAT-WyQ(K51#G)cd|D?yerlVo=kf8j-_~~W^GtRb;_KePgzX=6@5i{U=Y~Umy!UYRjX^y&<Yzzs{0UZ%&0P4VU(c&w`SHn3H*Lt!%bl>#iynWcuhpNv!M0l~_GXx#Uu^Uazue*qz8?Ev*x}%~xVp{<)l(<?9}SL+tLuD-)h%K5n|s;*$sPS>n4T!o&(9}+-zQsq{n)?k^FB85jiBxwKk`vfPb8AQo*3Hbknh*Ob#s^=YkJPMpdOplCp2DlH$IVj(Ds8{KYEn-RF{!fAGr8%a9(BU^qcCjo2vQ!mR}_^UUlu~)Usw<g7Z8U|9VrHp4vEnr(bS<Ia|-ZcMb>Vf0j<3Y5mYSHlNW>yz1nczkS>0u>N;-?N8O+{&#gZ-tB)^*Zz;5UhnIvt4<vbt}oTShraOVe~R@L9ly@jv&@c*uHSf();6D=r8CxDT0g$guP3hSaoU%g{C0<3ZpTaaB}b35FGZ)k<?D&^E&cja%xBeO^QZasC(x6d7H{-*_L=0V8Jj}&d-nO`9zXV&uj~F3WuCZtl6jK+ZvBRgeqf!tx~@}i@Bm+r^=-G?_a9GY=!sgXcl~jC%<9pdL*DT9Q$HUH&VN_eeI~7c9`oCc>AB$OZauNNw`R=qEZwcA`cs+n1U<EK+u`82r{j;DIh-+GTK`vvGR7;d7b$u)I8V~`%xrNqV;*XJr6C#XE=#YHnZLK~iT_de+<rdr;s2<o_wDxvS-n}mjCG-U`uv^Pdt;cM7<k97pdOnt&el&oiAL1#?%R%@-iOh%_H9Sk_-Lw!?T20c{rMUH>YhD8J+)<#KR;utS3GZhaGge(|E?Zq{>R66UFYlXmfjJZ|EhcIe|*o*6RXE^8{2q22U(A<uKRZ4i;HbNoYx7~dzP;2z2nfee!q?CwIlevs(a_J^z(`8^Lhnsyu1IPyZcZ6`T1-7c=iFkce%RWyS(v_`MSG*rgeA!e720QyZg54?!KLPvdEg?xTNn_i@Y^q^UBqAo~Z85D_3{p-Sf!R^*oCGW9@3c9_Rec(%F~Nx^w<!>8y9J|K!!db*J|MS5MEYrhR<fy`N<1dapxw?<cOV`$_UtmDOSW@9Ns0s=NK~>TbN-|E{k6AOHT$D!(7b9?sYYRQJxSo3Rh%UuyNl?jwGD;+IT4^<}OfA4iXG{NC!$eN}b$z8W32#_D=5>ptV?y3gbvU*_xX{oK{{+*IAYpSybceeKZgwjO<d;eEl?z2f$LA^PKGHc#h$B&|E|BgqL<R{DDKXWO5Xs(ujEQ$<U>8`R@7@9=f^{YZ89{U~+)09%jltLy{$t0T5ueGk%eXW@G*{Cb@C!7N?Z1-kn_n5FBzqRQ*O?%lk4XK?<c^^QIEXUw0uOME?bX4TG&`HAj5VdHgvdV8kYb`M{>)vs6YUFfODR~+#Bg>xsdZ;I8O_hna4zb|)bYIW!RJxkYlh3>w;XX&~>EZMQ#f36C}Y#uz9>ahk7`1$KO6+d}!ncwcTlDjhI33}p^Gy5{;)uy&qcfN19x~>=1-R~Q&uIt6C`ot33&z;{6wyU}q-MA+spP3C8`|Zve>c^*EEx9+SdnaDp6V#)5b$vZH-p0pgmCDc)b&`96daA>=MSecH)wT!cPg-Am_xr*Aj1}1G>xma^yv|S6Q&VhwO!vL|jjg`6z+1uRQa$lgB%}Wm4}bBB|6JWx`Sqt9J$6Oy_k;1#iM6d>zpJfZpBLR5yKZmrdGkA2J=L?DAD>UZsqW>j-5c!BSo!t~e7*2jd;NS1AKD$%Qv+_@6V$z@&d&Ga8`azy%wP4y=;Qk{=3%J?Rxfy9V{kpHp89jYod>MP`0BqW{rW$Ce^YS&r}d)KY<oJ6zm4?u)Gu>(2Kz_##H!o(2m2>66ur;fox%P|>$PpX_K!ET&n&<HM~(5<W0G-KJu$oef#7_IKh)Lg4e!lZziGXAhm7@`fBeSh{pTvc_Y0jr=!qUbWXy-epOt3#@j0h6=MQ?SXOWEf)WHX*`}Mq$*pbmcs-J$uzxT$_ldH#CeWi`p{!!gKVB?eM@h<;9^QP#fTW`o1U)4``-<Z)4s`uHoHB_HnF{9nIe&R%EyRomQXYPj@Kl!_id7^si_xcBe^DVVy(!bseng6Q0^FOh++UKnVm)ZPvKB%6mKR1;zE~<}zWP6w%TUaq;TvYc8oy-`QwEk=?b3SN3n;RYo(^Ds>XUxyky!)r;g^aK2?)auEOtkUt{88PRKk*LLX5@v;Pt~*LXN`f+=Y`CF)!q3YjrEx2x96-!)!p@&xD(x3k7?amkBM9FPWtUT`-$rAeiHq3l+~U6B&|F9Nq(&pzV7aCY2Df1@+ZAC-;Z<lPu1Q1Gxhr~zV7bNs=NDhvSRxMc_H&(b$9-!eyH(^-@ndzq`G?^CAMAuiXHdN^GJ2~JW9U$mDQc|QFZrxO!aQM$Vcb=Roy**qqVkK-8tV?chC3Oo7=7K+#k}qbALz<uD{s-xpO~J-Mybgi#E2pbN^A@z5m3fKDxyBo%@yQ?)@si_~B)KymLQP-Mt^is_a_s*W=tjRd?^7sfp88_;JpCTXpxoojkI{*WLSnT6gaMUZ1759_RkAx_kf6Z#sFUuRHHks%O1VHTij!?>q0as=M#A(bv$O_hr@H_vLtjTi5#ay5F79-S1BEX5H5L^}FBA(B1E5`Qv)}@6GOaJk{Orc*%+b?e`?-yR_==cj?64jqUfjyIX$f*EhS{3tL0<c#F}`hUs2~$8Qd;r~mFzVR~ZI-WS94c=4X|!}R>K16~i)V@vif3yt6Vm$hMf^5v@Qf_efyI_tvCVY)YBf4E-1+qN)0f9_KIy=zq~yFMyZu=>|uKDRYQ_gYmM78ajqG&dQlA1t>lOiwl4y*8+O6{)|_$jzbpiShQk$FjCI|I2T&`ZqRDS5LIGdAfR>JhS4-)73Rk)l=Fod1mS48NaZP)kh7m^-S&J-?Lpk*=Xd<Fx@NHq*quyvFcmz4bu~A-kBGs#|s^tAEtZv9$OlkXYTdO!}Ms^I%`Ao89I1fQ1|Yk-HIP=3e%GfN^A+$N7maGrsw~$*N*%C{#GA)fz`{_^ZV1)qsyny4AZ@rEA<Ym$7|E}-Y`9J#ff>L@q2d656x%IH%mj~Pq$hgTK{(q)`rHv-EUn`kD;eFeYPn~kIyW;B}~u1y3w{UJ$dCjR=@4e%zba?yxChr^u(Xlo(a>v__sf_3XA{a>;s|oj~_QTOwXS`Zb6vt9c#2SRNwQ{@-RI);iEO7^*30*E~uyX!>$uIh3V1A;4NW#{8XWBVS4g!XY9V(=^nc-+Wz6c$Lap*>IwGGES-HROJ`qlb={X#_u5%q_oXbIeJM6&qRqe4{Tb(`tLwSx>WNG2x#{XL&dn^Hb2Cfl+|0^{b2BTRbJNxJ+;nw4H&sue>$&ObdTwUvoSUw$=VmfBEAw2Ndca>tt{!Xj&lzF5cU$`!q470#j}NOqv8MgpFg;o5nFV2bET{6)Fg@PA(26iU`u@9XLfifOj&(s@&*jA2F`L5l<m$V&gz60<+rsqNoZoFfFPf8i{<1H*dXjy~)xDVAms~x@zU1l&_NA<L*_T{B|5Lj!Wwpz`l$9s@QdT|eORA^u59~{>uKSX!>%Qdbx-Z4AUXr;lac;W0o|~?o;M{ce80ThIJm;pX>$#bg59el9Jm+Rs{hXUw@tm8g>%OPwrmO3@>FRoJy1Jg5v72{T{k|VF_IX#=eLhRqd$OzRJ=xLI_hj@KditL1>blRXuIE(uhv#e!(PNXYnGvQZx)tdhrhAv{PK4E;C@_0Ym>xgz&4N%p`qq*#J+`C%ico#vi)%vl(%-KO>gjX2PNz*_dg8NLTf+3%*;A=7J@sMf?HT&5lQZ5svh<dj<F0z#8F$s)aaY|P_mtM}jC)#V+!GT%$v6kSa(2DDdW`j+6~Dl)cUMnbZP$BNJ*;<E&wt0RcUMob-m}_ey=S${de4eyy{oS0vaWYm*Y)n|y53z~*L$MEsf_!1lJm&b^`7kNUecaNS@E1luCDiFSJ!)TR{h+Qvvkg*to%8Tvg+qNQeEE{^gMEPJ&#;n&m&jY^T;dkjqPXNAM?2{xq6)YlB;{8?0qRq=f33XG44yQp5VUZ>QU}XS^02Z%8KW{lvO|XCDrwPR_{x$uJ@%Zo%@oj>wPKFBFBDD=NwGxcQ8kf>31+kPw96sNB0Ks9n8_w-@zO`{T<BF)8E0|eDph*8?WEN+~?BoVCZ@-r@w<adipz<tLt|#M^AqT8(YeL|J8j)_jy;>ecsX2`@Ey4_jyN8@AK&C_YU3XU7dYCc~f~`ci-P#UH2td*Z23Vc=n~N`q`IUUH7G|`q`JVboM1z*L^9ge)c8R-S>A_*L}&=bzgFI-ItPQ?C+)0_j%4uSJ!jX)f1eXuAbuD%&LcT)7ACd%&LcTGb>Nd&8&PlH?!h7H&xg71wA)iUC&Kd*K^a=_1uiVo@;e|Kh^J_j-Jr(pRRrZ-#=YlzkfP<O22=)@%sJK(WCnP)2&Cpf4cGd{nOFY-#^jyeK!65)6vu4KV4nFe>%E;|4d%c+Uj~<^WNd=`hDKj^}QoYXJ2x4-Ir8P-v`*2vUK*P{JYxQ{?T)p{nOR;`@E~`{+Sg|p02KWs;=jw=9#7I`%#asnfsf52XplFcQ8lS-ydbwqu;?CUC+&|`t>`QqwBfp>gn%bZoGa6bM*9gFm(6#N3Nd!4(96m9n8`FbF*v4Usn!oQnB{Abv;k)Jg=-bbWq?=D@Bxlis64+d3(eE)t^?@t6T5?`L~rtjzm1~VPo$byEMo1el#dri5%-IKSE4<^b*9rNPKr=ov5pav81ty#{OmOG86le!TJU-Fm}DM>Bb*sY`d{*j5RUV*x1v?b{M<MSOXK+#n^>8w(Q>`w!D;$Q(nprqP&#-JLRQpjPjd||GKdV{C<4l%kU*WhccoIm!B0d*vQxk!&l%d7kmb7v%zx=w$8D>a>0f<HeO-}8+(BA$_3lP1#dRC9ACNM47lJwXm5Fd3pS)(!LG)-;VT#Hz%$5mU2JR@&!SxL40%b;cN=SluUxPfc}dPqjSa_FF4&X&B<G#RE+S9mf<HxUZjx6Ga_Sb~HONPD6I?+1y8?Ux`7{GN(|)r6?@T_!!TIDdJizCZkK`s;ojwy^dG$c9f+dX|jaXl~-~sZIoJE_2uUzl|dG$hj1Yh|iV&;>xXdmM%e}tIo<oq%1i?94+VmhFgBz8XWJ!$t5a#=vzXLzoo%&m*)gBkSOPR73(ef$jLayRp<8)MjzaleSNH&ebX^QswTPf)%Q^R^pnYdLdV_yhRDSKv2d-L)pB0Bf$0!6wE|8NLc%x!|*CTMQO7cy*5Tl?yh`vGEc+#MpSsD;I1B7re#TN_^#lGvR_KX>VnK3pS=*!S2R-;42sG$TP@uU1DrE&!SxL7xI#vM;dF6uUxP<c}dP!85@DGT<`|+lbqi&R-QbS3;rCjxk+BN$f-ww*CHRuP4H#f-yPsDlTUN-I@)g@;MbAQ2=FEH7!lwvk&omiSd%^zUwO?yu7ahEeHyX8a={PCOL7)%3chl|56G)G+GKp?Q;2zqoJIQtU-@KWYLfFOv@gE$Pl)M=UW(Y4h`)h$CzH#|wEYXu^(k|!Jbf^eetV1YZ%!XS%eahWe)V7s8#C_ZDSHd$+cB@2Q}z_)n=o&Cu(nn*$Ayo_7rqL=3G41^VhXY5&NbM~*f)l+!B;N$JldNE3ma^cV}0d<O>=C##NKM`LCPx^Y!4S4YHT&Wa>3`|f?w0#>HrsPO1pwRjrGD;E_f}^AkS6N*gHIna>3uoOLD%)SWA56f_=$La&BR46uxr7KIA7kziq4nc`6tDHDYs<ye=oFUIBhN`ABYpuh9NG0sad4v;?oG{gwfKJ^73R7m~-Q0AENxlAB;{`b>P~wF9{dmNs@gVtwU;2gyrv7VR;7<$?#vt1sH4_{tw6W+6F?b_`$nqr}uE=VP=lzVc(lT#H_s*oDORq1{Kx<rUigjpsVf+^RqyJV(F1&G@&ZkDq5;?qPoQVho!y?iDCIl=AJFS1l>~4dt6LZ+o$}Rx`(iKZq}U4SqA$T^nM~Wz7{a*xcB6hOfg{E;tKqtHJXOUXx>e<$_n`*m#M(-B^P1$^|>X1#dI97GJsG3vj`2X>V<S3tmOLf;SlJjjvp=6VD*eRoU3PJd1L{-^ojI9%C#IU%6mE@{*ie85@nST<}KnlbrV$t3;m41<yuoZj#p(<kUOBuOJ`EO>hzIzZ>9-$R`i%Li>3E-i3TdgRhdu=m39}d?Yu)I`o<N%IgGj6)a;cKVp65f*+EX<Sg0~_{s%8B(HvGkK-$Uf|ysyS+vjal|N2Q9diDR_QhBJ88MyE%Mkl2@i)@$<K(i4wtwfj@|jze=z|yNw>^x19(_EEaT&w>>dhEl#kg0Z>}{0qz`V+%?01xJ&b;l-+FHvT7oNZuz7D@R>+Tw2im>L28Ek3n2gBdMS1vdQEoHE%!L~WpS1#Bh$Hq(SUyMCOdF6r~;evM<TaT|?a5h}<d)iwc;DRk^SFn$<zWB-oJM#?kTvd$i<5`po{y|=n^H^i8@s$hqCojo4X6#;k<$^bnpX9tZBEMg=zH-5TM{I7A*OlbdH^8qXAIVMdHQL`7;IENSYp^Trw+`^G<Z~~$m^|(c@WtdKxe4adXW}c*4dg0V*4P&j>nj&LL|&4!XjAc(3mzh`{%B9)E1yctVsaMkbA07b5|c~LpVPkh%0DNjGkRHK7ZZOI?LJ8^uhI4&Jl7Y@ttfpkn||BN__wBy=P)i~nO}Vw!xoHtl(KhFz9aLhHD!OGd`sqSU)I)o=D6^O@P)sD-;#CLmY8C!x$_O?89QzGMttRh^U$^#EN-w}j`fubw#u>b68l$U6DY4-@LIUwoyIocD;Jy#7yKvfZ3u9|R<tX4qp^PY$_20E8RWUD8GDasQ7-7^*t{g?`;4_APvwFG$xCv++SoXJ<$?pqPjcQLkv|i+zH-4oBQ`h5s~$P^3-Eg6Be@AKrG4?0FD0KgU^m)t6X4y*XB@bMJjMn167rGU1nbgg;w!Hk$W^eMv9BW5S1x#%ygan0@RbW5Ca-~L)9{r)Ma&X%7VS%X<<p3%OU_@?zWB<&B<4Ewa>OnnegN%GBbTML?eUynF}JGH2XpDS{fvJb`gk7Wav$@nA7j{xaj#0*J1KuH^QsMHPg6dRdE1Y*wShS<d;-4kjre)2yLQB!&zgJJJi;DhUxTOMf<+>h3l@bBGxnVP8q3(#_{s%aq4hTQS7Y<=l?y&gyu@B&tTDcF!SmsQ<&Cw*S1#BRE;xj`TL<_M+L{NxW^4(*a={nLU7qVfV}0?J3*JUvl5;Ije(_>`<$~qNOL9KfSWSH8f@R4|a_(bnJic<lTggrGnoj#m0(?68^aW$I-#5Tx<Z~Wag7(h~@Dk)x6U?LingO0iKI6fs=(F(w{!}1W!I8#p##b(QBYEA1b``$zn~5nw&Z0HLSAG>SdE_kGAbjP`h<S>f2hsjh0X~SB7tu!&o5#<}(rz<yiP83LJeTD9EdB5r<5`nFJD+}*K5oUh$e29GI6g?(A(WT0<tZ;^FQL4Y9ZGpAJCE|Rwq&0F72X(M_|^ClKa4WH;qtQq#%?m!AM6LOZ>*}Z24FRKWlw(PXx<Aj;Zb6u#6{7yOg-uotP8J;-ya+R7aRi@91VZe*c4-9!F%D7LoRt$hF^*0@=Uormp<Pp_)YM8FyW7Y6XDf(mIhcA@~uL9^}s9P_22`*n*x1&4}1W84EP9Ka58)hd@T4V{1I}S3{HYihCd2Ufooq^#p*IXmB3uEE<6|B5A5&#XHJZU_k(LcjiSv_=##L~<T0A@Qa%QM49_I|dSiDQYXMG!w}4j!r@|}3D}aB2SAaLigkNXu24fc+n+cu+p9x<NM&Rq=YrzZQYvD66;q7R*G<gY@fp_6~u7?lDmz<v`Kf${Kc{icHCe$UoDRs1fcfprFd4c*~psuMrb7$)7OkK^%s|C50p)T$7;nX*rx`cPd?*bozFYU}BZ^66a(oRG27Ay&GL>*1xUGb%zxzsn8x`cP4uFmj=_@$_$47?Hk2<jRRpNoGtb=(E-g#Q<`>%h+NByn@#<M3<qEDhmB@aym_jo{tzrTqoevw*sUcchL^@Y?wDEXAm&7<Dz`S?;I4`>AU#d37SUan#j`oQhCi5$Y<%7?h;nN}`pa{mY3JEDD$Qui$wEyThgZmv|n*`EY6fTI#!&x@yyYaq25hU3GYt2dM7>>RQ0F+(&))QCCNDDoTAtsjC<{b*H}W)O9~&(2f4<hBks+=hM!7+7RB}SO;U5f|tPy87pk8I#>ff!PvvbmVwLR31bgY-$T?TynwNS)K`$Yg!eGkllpp6m++;=UZ=j-sVhNFmr>tk)K!3-YEWMd>gqvXT~4`6;qAd|;qBoG@IH6~z7(7fUkYCaz64(ep8!4pp8)Rxc8B+XR|l_vSBDn@i^B`S3xGx8MR~RY<glC^m(zDk>2K*P{U`ha@G|%X@U~zFcw6|>;6w1I;cLLx;cMXQz~%6D@Mpk>;m^Q(fj!~9;1_{4;1|Jjz{2ptJX;QBCGH0B;sDRV7d$7xJ$(5W3GfT>1uqQnw)leW0{m%w!5IO*248S(fUm<BTp!@i;0w+S@Lu@6cqZW&nWQQhyBMqpf6M%AyRi?zz3_{PDGru_e?ZJ}@Kg8?#{OySGw>L^IAtT?dGO<u{T}=d{uyNtg8SeR%Kq$G{MEDkd&-^xe}NyQ>~3%eT*~}PzQ2;|50v?ZffYPAV)<^$ZUHyI<!2I83@i=bLd<6H4R|qPE&?mSHxu&~xE)^E{OmGgrNDCVqvmIajeQG#1OLR>5o5c+ZSYc*J?mNgw`cjcl>H6-9lndQtHFhEDI;Z1gFnK5qio5D#j+90S5tO2_#|9@CNY)3OX0JLnFT%puS85uur_=aF{{9r;Wde=1zrwcMa)hx1+PU+W$-fiPGXLNhv9n}qgB{;^4!k&&BET`dEa0j%*Hm*pBtD@tFayQ{SM~qE^HrTD|ih43H&tpPxxv0S@2i*S$HYd&3VkFQmm=UU>SI2crCCZycWDBSOH!WUI{D>uLLg%o(nGtm$`E;>+Lt}7v`qmckplFN5N0wN8vlcz3{z^%})B{NBT_g2>kEHJ~#FgcnJOz{G5ozci>{eOMsi;V!|&0H^Rk)mj~a5iwQp;{17fCJO|8&iwXZ1Cj4*4P8xg9*a`4JfG@@uTnYcv*oCI9Dwyyq!5Z)@;SInm;0@sQ!8-8z@LaGuJQp4XFMvnk1;9T%%L~B2^elb_{}TQ__!0bl_zLh%_zL*#;4ARk;RC_P-~-`t@Nsw?eh2s}{0{g^a4UQz`~dhd`~ds}_z(CAc)^IpKjDHhHo|4>ZlUg5Xj}O;_}7rD@;3NwcsAvO@dwiv$`|1;qVJUN$KOw1EB^xj3&uuyp@{VhF_y}!;#XztmDk0u%Un_35WgXFOL-&wM$AR!_3-O4ca>Meuf|+gUKqbHeXRT>{eP0N5#F^^B&X~-|J{Gl^q+t7yLvC<KWuVKX8!p>u;c(!SNe|;x^^lk_jhyA%<*4Z=gVk#{{?%Sj|T'

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
