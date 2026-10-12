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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0d829115bb4d472da5d05cdf529b6694/part_003.stl', 'relative_path': '0d829115bb4d472da5d05cdf529b6694/part_003.stl', 'source_sha256': '47af5a8f2c56e2148e3f777f1f484e2fa4773357359c3d20f9971b1948d3cc2d', 'input_faces': 1428, 'input_vertices': 929, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3513723313808441, -0.4817200303077698, -0.3802955746650696], [0.3802885115146637, 0.2868534326553345, 0.3803081512451172]]}
GEOMETRY_BASE85 = 'c$}r33D`{K8~^8hwF)KLNJc{0icmuD*eXP%$d*x2BnqiSCR-$=vSk}fNQ*2bl6UOMzSE*foA$k5rR9I_b3XUu%sslU|Mma(yYB1zIbZjCX6BsdJm)#ja(*qF6*#GQB>1mPBsy;Byvc1N5s5;P;*tJc`}FI6XV<<}d)@y?PUI}#m;Y3sZE<V!mhEyP{UeW7xT|a5JNs0)CR(9xx2r2uj#lW_yHCG9U3zuy-RG{Z;$PRLXWy=#-}jy__jmQSFRfj@cID`mmsO4qivB<TSJ3+k@goEG=X;vC^T#(uQ?Do2=81NX`+nq<S6>xPmmB5#i609G{??Y0M58?$1^#2h_WAx-$41L`G_iM$Xga_DzKs1>`)Q-^*Xy`1y#M&J{k|VrT6kZ0|H;Nfd_R8b#=ZW2j-CIaY$yBH4EA64$-Nn$``IrW{QT$Y?hSu#qDi4G`6uwxZx!6)|J~`A1p7JCc#Z$Nj(+uSe%R-G{+FL>|K+>>ak%%;9@&mHJ$0l1@9RhS`ReQM`cJ>g6aIeEL-y_o|K3!h`i8Kds+jk>|2r$)mlBOF@3bd;91?pz-kg5|KT_|=W?#2_yF0v}RFQh?{r$JuxjTG(qD7Bv&p&}58*pU1f85rt*d0D@sVyu0eCO-&`42x<^DTcr=_5;ahktM6yuaSbKY<@l{Pj*aKlRJtw|)PbW2=2F+;4aI_@|EE;D4_AdYu2uPu$!j_+6Lh><%Bd_&rZ;%Rhmi-u2Wr|KGnmxGQ`-laC(Slz$@s(?gpw^7;PBamCm9=i%Zzc7=a$wEh!Y^H1O>7Cy1n|GQsm?#ehXvx9BxM-J57<(HEV(Ou#56+5Ynzis_gy=Z2>o-doP=a>A{@Q-(fkALFIVB7k!dp_P7&UeS(<g2gw(M@}HhL2nH_ecHxSwGQbpkHq!Kbf>MqnvlI<JSXO{_Z+{J&=C*;oy5-yx6}!ljVbL>&H4gyfd7y<-z8wuldQ&TX*>7V)j+OrWSAW)%vkZw(bb$yL!OntFQT~oj2^rxGr|Q?AHU<PhI`W=5T&=-c-LHkA3omUk^m{)7vx3Ph^*0?yVoIy>qw!IrqP{JzRd$y@TuA`pLN~GV>`v&ad4e*#E$H{PLB4u6=NwTL16%+r#;K9&Nt!$xn=FvOQc5BX9K$>KEguzVEv`obT!l{7B(3+rs4`^+6=47mOb-nv;?5>J$8A-Sf7EkAHOYM}GZ~dT^$H-A5K34DKhpW(4(s@#ELb+#1f;^K0{u*OQs~@nx0$>m<=O8q`0Z1@(=V!}!iFK|N*s*vWV73g^4}+2p(ONq($I-7Vqs7#km4ht`j5oU}8XujkR`tFQU-{}tR4E}w~d_5Ay^^;7-p?)8uN#4q0sm(SE2W&M2XC%-P6nXlzm{WGQp<zU!Gzx@*LG%aW+7(cr6`FF$ldfsimD-R}L&sTiFzMwtu!0>m&<u-Of(4Me<s`;Tk;e1z~@e_}yH;2n@`mUheVExpTP8s=Hp4E@^du4ODd?qh$>X#Sm$DeAtBb@K<gC^gVTk?}{1?>VYhl!_yc7XL`8<y-2=ezr+$#><G{MeSZz8@(x?tuUA<%4bOr^dB?C!FuDBa^Sb%Rec-DWg10J~yZ@jGxRoZ(BIul?RirzUD`x?`_Jsj;00e4C^O%9^4hqch`~0ckLGPBlrEZG2{B0{?I=E-@o6#F?_wmOLofiwVjWjN(|YUQEn#`&hXuRU;SwVH-^hksvq}z<0oI-vooCU?sq2Nl{fO^(O)-&%Xu<q^xm-V?(g`i*Y^c}*Gh-{-^KOle9DPl*VfnTT77q2n|$?ce!An`{{34&H?pewhH&|hcHO%t?7Q|Pe&V8|>odw5*PZqCx>MhkH<Rz`G4i8L>#Yx$x5R?)c87f}SL#RZoVYH0JoP@PzW!c!e|#qD`-$hCf6rIFf8pzKcK1Q!yZa!%9%q~H&Wp*9ZfNLlyU%^M__}a8)a%IldL5~+<<RE4@~PM9kIA*+>n`?m@Z4_w^!kDO{rz<rwKjY`rq1pXJhvM^aebG}d~MI$e0<GM%x|<deEmje2K@rokL)d+k?;BqOul>m)%^9l*MzUfM1|o&KZ5ZiU54!o=ey@z{8**8*M!TnYd;v@wKwoxd)VZwulea$Ypw}jcZt`6ehTZyKHIoAobT>C_^}@<tO=KAZHKGx>KWSe*4OsD`mTO3`RdzzEzkP7@ox8}!q;!Q(!SunZG5dy)Yt1;{b;*uQsL`P+viz6?Q`|@y0iJtCqJ_I*y`~0rT2I1>-}AQ_nc_*UHh5*XxT!m!{^04ZyH~pH`UkUY4csZL4JI~g>Pq^N1ji!e4bC$cjwXMJD>bi!R@QU<=nN;jqlp?_^v)T`R=+PKR&6E@4NQEs-{8xYW&!bO%M2gmsiI3-E(5YszE(%{Meu>nfcleY4f#TLi4X${+7Q@{S!ZYz^`YlA1QWle>h+3ADi#$CGu1E77X^I?Svss{Cw-jmp94Cch7zJiKXpUhReS`*IQqo>(zJdNt5sHU*xAhED`uxFHwJ5U+YQrUH=<?>YYI=eE*I8@B6=3`>E8Y{A+(#mQR0|`da>NzVmJV>8t$fTt7E4;G3YFX}z>H=>N68w$s#i?O6Qul-bL}*O&IQSzr6v)OYO=ldrz(m#aTG*bnuOK2KR+pPSTo?N#-o2VM_fr`pe8eb=9W@2+3`c(J*!htH$-_o}bQS^dQDWy}2hy&rzy@1Oov=W~9wpVs=?PpiJ3Uz@MK%}-t2HE5S>zwS@RmWHnj?Ps&T_Oq$4*M-e@*9-ZHMSm^vznAuRRr|=VPa>s1^L?$CB5$wB^tJvOxyJu|>uY|p<80s8`X?Rlp5eRtr$Ue5_ZeUFQ==;f`_cA~)=T)V{ez!=<J-mI@~r*X*4KV)^<DeH<g2gw$^PROXOt7hBb=}0jqwZhU3oLUJMZi#I%>4<yZVauq57`A(spC({MUS6>w$PMo@9M}u2kRkFRB09q($NDRQpw|@A^;h-SvwfA9v59@O7c%GS=5|8TDN|!Q{K^i2QWx_OJM#tL<3&Gp(=vmg;N$;QBKgjd(eH9(8<8eLXMEFMD`l_`1`6d+Tezz51@7#N@l{QTzET%wHHTKRT|bzLp>L6S0yD!sS`VcdW1DJL<dklF4`VIr+&mXTA_VK03asz8)X-Q==|;A>;fq-k0Sw-lx7hzb4=L<VP<nHpkx&^;LZ2)d&6WJNejbf4}-1_fd(1`6uw>#Y_76(WA=(U;A6A$E>gQSn8+i0$;~9Xm_O-ADtCGUpj89zPpd(r*db{3SYnOxpM2iWcYg2{-XHo^)tiQm-f5HdJdi*F3&oSknUe}ddB%;oLYT%zVKt6k3FAJ4t1Q%_&UxNdF<-R8RduZP3yby%?-6CgwLanBU@j`k>lT={7m?`>G*j1r}bm~&uMz?VgL7SY31L~(nBkc3I8q~uTTFI9pe9vWzYKg@df+m`8ue?U_ZY_J>O4G-4xsxn-qM|_kS4S`_X30g6sM5-alR|`$_CQ99&;JeqSB-*?;ok8|R1fUHgAsn}a9vBfq!t%c1)2etJ{wjC@yaDd*1D`{rMV59FV~clUAiwcPSN;=T{%(Dk3-yM8MAIi0WdJmU!JyXPau#ngA@it$<N>-entuARyFyY+Sa-F>d!FPP_GeVymve7*lNAH)4F%8$+iamQzS2mklzc~7?bu3z2>%1OLe^&xpDDsSrNmJHgX>i=ACOx_8~ZRDpn#`-#WgMVDKoF`}280Y6-TO{bO&wKGjzr5_+F+OAe-wyNZ&G?W1_`bc4BJW&2Aup1BJzC$*>sWp6B!7F_`d}QZ>Zw7yGf{1FUgQMzfbq2+h~(WkCFA?QxzN8}61RRiCF8i2={zUH*WdLYeq>X8j<4sPG&L`hU5{B`>#=C%64U+PXX;7yZ9N$;Gt&37>f5Wz%?O{bRH-Y2_VnDhXXZt+>+Sd#k0!&vH??=5U+-H#F|&U%BcI=!m5;CaiRQa~&AN}=moqD)+%A7}ZhqM3y!@A+>bP>QzyBdKeBa)`($zl;e0v|nxA(zx--fgO<7V!skwz;5-`tn2@18G8t(l!sK5rfow6lNyH^?{b0qbjfAUX6rzZ|)Gn|j##t{$#&`<(FkieB;cl>8I;$qk36WaM+cvhwjYKRGvlZuop9+voc22J6QnC(X*p=X_=5>vczd{L@k|_`l1v)3SWpUFzF*T9&Wvw8*d*!p9-KaM$?!6Zp~J_KwfU=Qw2L>v1DL)?>~K8P_lEPxZ6frFlnQ$hb~7cMhI^jGvqqf6f2=2_MeOxE?R6<+mrSA9=m*kc@o29&NtXSLDY=H=7^ckKSLLuh%<%bnA=rGs?pSE&TFh{q$X}{PN>`Ee|#yU-J`d&RgJrKl>bEeD@rIpY<GJeD@sD@tR;B5ACjW^%cQ90`<9m|I3dZSox~|J#Jp`V)*yQzdV0j{t5i_;L_tV^7*}4`Fb44k1m+A(Er}{`3v7Zf2BGtU6}E?hjSmy@Y#Q4$*=wLPvE=!+3)$jeXg{=n?HtcpDV5J^7nlBlD{9?&(Sr9U&;^rl>h(o)1wdi+o^R!UJhS(`dqBOeO^v2y8RVj&2zf-^?6)<`<$L={N}6S@)K!V$8Y~QpK|hFeyVuQV4ludT^ITLv;7jrcl{FhS^W~m*ZkNO&-uRXKe4{{lc;a|Pok|mzm{>ns(cbW538@|>p%R|?oa)CEuC27`?g=m`r7}azU>!^Y#y~ZeEg$VtPGxq)#o_>m!I7C*6iTA8sqzJyk5scjqm!k@NIurdd~R8;c}?`X3jVLZ|d9rH}!4*Tk5y3ec$#UT3`DE)wlhJ)_3_UsxI-5ua28A{$hRC&xvpQIivHdFA0~E#Mu>Q<e$J#b*eZcBVV5{Y`&Hs@)OgN!S~T|CHiTtul=;@+kRc^YkvC1F9Ki3zi97SU)y`mH~r7ncl|aW{Nwws{l@dM_4Ro<x%`x+;c_1TwB)1=U(5NF^MiT%#@GDxEv=S@kAH0bO27ZY`pJ50#%APm{Il}4eL{X>$kL4cXgk6AdLH$;wcMtR-<4X`$nOWSe){ZUgY&|^)}J<C@7Ls~tN$5%t{JDWzMDUcZ^tRDuldo9OO|C^?~IQ)-;B#xU&mS0x8pL_xA}HlCf#~=&_80vmDIQ6O34<7g89~VJj?iQJPY5BXC-?-zTE%bc6`nFZX6BYj<3bvO9uI79MJkYuBW~o2eiKCN8kGDO@G^rS6W}kCDpg%m66{DuLvJ!9S?QB8HdgC8CO-`j>Bg8Hs6fHrq3v~(mx({eA)PJd>P-4FGqf9yE0s!lRa(=#=r6H__+0Tyjy)cK5l(CPku_FxBP88j&FQ7j*oB0@soG02=dK*1MBO3N_{)u!20ffcj~raKYzXaq3<^=H8KALer#-XqMtvw^eTTpW`2eBwV%QHW`2eBH9z|IHLJp(8$Z%uME(i<^utX?_~-pV1K+pvL#(g;vFW?pXY9w-+fBEw3YU{et6Bbdx%zf~i}iKBiu!hbi}hXp+Kb)}*8^_-i1nFoqrRP=ljV~iZB=A-_&Rm-g^cg!7vX2kFEYO7Cw}~6b@;eN>n;t(>5ZQ*vTRv6-_ED9zRr(Q-_ED9zMFsbNNvAesr6WVS?ypR7`~k+mgVcbFMK;sEX&t*B7=IRGLA!)vB9{q@zei~U7V3`=f4@>&40tU^WV~^T(%~B9(8`5`gUHQ^>v<}`gUHQ^=-bL*O%T<YfZ*+SUl7p-?e_K&G47Q`C0QDjqm0+>VC}p#zeDKYr^L}R=c!6Url{GKhyd;-%@=$KhyedJ;?ieg8ncwkJS2lKT_Y$BTcMsyf%D%BCQGq<BP_RO*?aXI6rHCtnuCR9e&pQSmV3rzK5R7_}t`z`u_M|mcQrHG2whWAK3b?A6tDhAK3buA1|8B_*|{Gop0tXTVKcB(q9!@7cM8Mo(X>*nDrBRkFN;l+j-a4*Ll?H+j-a4ck{HDlwKFUexu)&4(4YY-^~NZ&zgU3d^evQKWqNE@oj$A{PRa91^YMi=he6K=c7I9t`8s2<h!$jd0@s*O`G$2M!ucTk8kJmC$0_Z8`u79#{6ddtaS&*ck2%Dv(_CLU-MJDuiOy+{#wslU+a1G?Yaq<Z`Mu3x9;B%KF+%S!ue+1hxK(Ghx&HihxKi~UH1{a>Nj8Qx)t@a)~&31bYn(&-c%%*_iX&c%V(?(=Vz_EF}_=OgP*nT#`v0_PCmXdd|qPF&;9Wl>!&t+F)N&J*A1y}*9|4l+@G<Z#O8=UufqDN;wL>5&d*xMq`q0l6dUtn=6-biLVdeVDi%Cf>2cQj&H7ruIp3`3vcA?=>f7~P*4O;_CDapUJ(~4(eVO`pJ(~43Klyc=cf#dg*T-33*T<=E*V9?w<-dRIos9BK`_}r}zEwYK{h;yP`a#`~T|a1i*S>x3<>37a)DK$kIp3~}G`?FGiJ!GD()gMmoBZ+Sa6O>?A=cM^5B0OwZ;l%AZbte1?OeZK-TLuq=f4onx9d->ul@Pz+x4gEGSl7-mj}1L72mF_wZ7Jq>f3d-*0=d~U2Wu*uQGmba&|R;o|g5~-`1EA&bRA`t*`SRoNv|<$BGo%l5zaCK2hJSYqq}5M@m*@{fAi}9W7UHOSpV$J6wIcF5CKcKXzSq>g1r`OZTtO>FQ^#D>uGdhk~EAuH5)8f5MEd;qv3!X~uW$CH3w4dgHrx7k<|IdgI%CyS_fs>D+A@<yO}@;@kHCB+8E6mT~>kUuu2r7ggWBXCOMa>Gtq>Nxyo&KhM?riCao62<O}PBv@a^CEb3^dlF(TJ8sXou6f>9-@fM|%jfxBefyq=ET8=Jh*cTCD|*|N!Msf4$LG|VoRM$dUtxVW-${M*{)*`Sk2Ch~<}Ki7y-&mVI&U!fMUx%ja-z@g>bvquKY;bMAHeO$ybr|sHs8JvB+-A{j_`TZep>bI`%J9w)-mDR_nBDVtz$YZ8289}AB*wbcnW^j`&f+c-pA6Heg(>#>#wuE_V3|my-&va<j2|u?OZ)C+FxgV?XOeczTd|Bnx8(0`Sn`wJ^j8v57YXonjbC<=iB%5SYPK$xc!*-^H^W=lb<s`TKntj{N~S}wtjNhAJ1pxoA(h}U*{`2-@K2=`YwN1&5X}={mJ-Q?@cnk&dW_N>9Q+ap56K{<Gb}@`1U<c*4O;hBZqc{%Y$2Ihws|?x^B+;x^52NzK1HyxB2EhRFVA1?(p@c<M`IsaeVdd`?9R>-j_9<c`np%>8YLlbt%?Qc5C-aI6v#XUdGpXR_bTH@5}g_pYB8Z-QD*Y-^6$0S^8cw<Gc5g;b*<a%=k9nzQ-(f^NNh)5WjAK-`{Bc<oH3;!}<0-Y}VI#$j&$KXS2TMCywmQ_*^&6j&I)=XMLToo@hh=kk+fZ-Voouk1l>a&nw!0tMiVG@8&7t+xOsE-_27hvTslL`?&Y%;k)}9^JHAUc`u*(_Pu<mV+Z$ST-T*01nb0%A6qwZQ8?eeKQPPJbwj!z^IpL$pZwSqo<H=yGcey@S7ZIurnNIO^38h@t*`Usop0WkXnoC3m#&xjxs)sQ?fV<8uj?9Oi=NyYE)O~{QGNS<$n-P8xP+cx_dZGdtoKYdU|pd0fBtWcKX2Ch=?_-F7S7l6<>q_iXT9HYbH~j6*WMG%Z#RDQqrJ&+zU!xAU4!$@do`oY9?IB{YnQ5T-_Lpa@O>G_Q{U%_pY@*4fkpO*kEiy#T0e32=*8iDH$I~4v+(WvMWesQGxn42Ju_HWX8ia$vu1_!U3;E&CC<0+HSIGnV?VBb!?*88O{Na)4<DaM!%F^o2kWQKsqD|MikGi?And0*H}dBPT0e2}b^iRo^o*t%zH7If-s3>VaVs_}_*~;hKA+`(ZnDRk%zWl0T3_cSs_({w)_t)g{{((~;?ZFLhYx4$$9+$Hcm1~hH`tHyW91|MJg3;&5(hIrHy!cUxmZ8;(x1Wn$!fJTe0RR^UHk2U^Mmy=#!uBb+h1>xe4$OIFZ*ek@mAkkmyiGa{)Ul=#OaaZk#1c=uk;mD{!=~iD}B4y_`iCkZ?ziLum1mgr*FZLIgv<DFP`#Z75Wk(JP7RxOU_n2(UI^7FWP!B9i0MC<!@(tu@~J+%;fK9k~5N=!+3}J`<d)d_PZ2)0iH_U>*%Mj=x?y-eE8nnNMxcHaW8H~pFk(VPrxq`!f$!88J&qvghlU#Zz>Rpl=b2oFG`}Pp=III;NNqDSm(uVFBYNG(RJ{2csy~F7q@#+11*c*1eb-+^`e?r#u|HZqZd8UJJ81P9dKta3dr&Dbe9)1(GBQt@CNvEFaGrM>wBM5$BTjJ5VSr#1Rn0i`(FMqFFq!ON1=DXqu?%HT!&td-T_|^-#`f8i4KGBgomK-!$aU*gm7u^yWN=^Xn9op^61B~gz)9LK?r}rzmI~yfXAR+;4yGK^xNWuaAPzIH-<~0zeEBq1%K_uN^~9i3%m~ALI@v2WnahG7B0*FuY<4S_?9JvE21~R72zug;TzFA;Tz$u=n%LoJQ&>t4~91r!WZTSD(B-uLbzS-@pIOW5T5MCHgpzxCp-)8g_eiQb1r)k!u<*1t57+wSFtVp6X$vi{1f~%8i${TJEM)^&Ts>?6x;wVhRS&@#<uXMp>zK!A-oiQ4qggBg+2(6K<`5zgl|IIp%23C;7)|_<LGnn<M8w7N_Zt@@p(dc9=Zjd2QMdt51_~31Moknl*@n6im-%mLA)#Ag7A5Sa4qykxE9<3?FzSm??wm1cf*gMo8d>`6<&Og7R?QGGrXB{U6c@RhPH$IqNCAva68KMXhJwYRPKepM1MlJ!KDiX`VZUN;D6wK=qz|2{36;5?!~q7A|brgi%DLL^5PXjcq;k;JQW^C2zT_NI@$z%0B!=eMMuGH;XBYt@E!1dXcE2;eh^&%KL`&%m%szy1o{S?fQO?i;NkEPbb0Rad!O(?bSb=)<2Dez3LXg8L8VTq!?y6B)H6@Rf5Ok8o#AKT+tCK_?Qngx7+fDNib|bQlx^XUsb`kLAH%PqPr+KhyhaGWj1Gfeh8Lhi;05qPbSS(Keia=KzX~rwN5f0t73j0@3V1C#1zrnpM(4tt;eF`q@ILr+LRi{FGtr6Y>+nQ)Bsv!!2@gi6z=Pqw=(BKNxF<Rq?g@8Chr`|BF6dCW3)~qU0(XY*K!-(+w-1GTpd(<>`(V9)^dN+9L~Fx0!qw1=;c9Tyi?h(;=*4hx_(DRs0$Llc0M|orf<@cG_24FGC%6fG3nBaf`Z)Xm{3QB3EIJQ<5}u4MhbP0c2;oiW0eBO96#WMlm3!DxwuOI3&x0j|PbP#bptax%a9y+oTo-PM-VL{eyQ7c5-QoV|3b;Q!Cv^XtLkJ(t37$zr%c9@s9DimJu7S#ZQCPGYtoOwlgs?pKj7O)VeRGdLHwiC7N5i7|u--2h5yJB9^*buhYP<3E*-f}4`V*}8S7Fgca7kF6|87D%qmAIsaCbtuDOwtC3Rgkpo?V4);R5JBSVH(cycgjYx%a$B2!Dnyhd+alqATE|@Tce-@Tc%0bP0S2-it1P_rhDyB)kQF8=VA;z5?IDaqNe7hWo(-(C+X6_%TAbH`)~L4Yxt7z-{0w(E{+5aA8!AV`20&SVH(L^e8MLTnPOXmJrTG55W?`f8*_i|Av1+x4=KZ-=J^9-@rT3SKyuS8gweW2A+$KgXhA}62jfkj&L`)dG7JHU30Vy+#J3PEe>A>pHB#X>D32oasu6tioc(2;cwA0u!QiLc-7%E;gV<*xFmcL+7`YDE{EO$mxHUK_rX=+TIhptEx0y10Im(^p$Rw-Zj26xMeD<j;eT=hmA2qNv<aVq|A8l<x5E?Qj%a<jBb<j8h4bJdsI>ozur2&yB+%Dj(U;*5;X~*G_z?U)x)6RJ{s?^){s{gAT>^gse}%4qzk+{8*TO%;f1;b=KjFX8eemD#X*q#@4oe81gZ>6f2$w^pPpupwT#XREz>9w)fqsV;fJLR>?K?vF?a1-IIpL}3ICLgF4t^A!2tNw<Mn}TE;ST6vxC7i4?F+YsTcADR7H~7PJKPLzgm!@&!41&PuxMkr0bB*G28%}FDsYL&@pfbhLb$LOC!?pJXThhyr=i8+)8L}$g>X^$976aKv;uqyTobJai#CC4!g=T|a30)}5blOP0C$52p-;l1li@+|cyty#9-c-B=cAk8e0UFf6c+s*-UI)DO1tw1wuK{va0#>mTmr6+)`hFXjnI~GBe)gX9c~5pK>Ncz;C|>FxF0+YJqVA3*M{1uYuOh5O0HG35-Ps1=uL1X_#SjT{2V$D9S@7HgXh5?p})h&&~pj|`a3Kt;|S*v!g=UTu;?9d9^8Qt?oS90LHof&;1TEmcm(_;`WXBq{1hRaKzqXpxDVO}?gO_&uY}vdwa~(FVcJr)2;pjIA-Eb`3C)Eo!KF}XOO;|<_yY6?SVH&|^cz@0_&2<r@Ne*k=o<J#cmp~Y-T===pM__`V+i59&~ETua4WPqEP5H-3a)^j4_AQCCWMdX1S)N;qlECboa61VZG`XwFB0fjbPYTfo`vp*XTi(SZ{g+eCREyLo7fiKiI#*Vgx^Cif+d90XgOFy_;a)>EFt_OS__sC{vE9iO9=mk=D`xe5xmB*sI<c(=mc0ocoJSmcoN(m&4b&+_0S@4J@^b%+FNI!hhPceLg@Rjgz%Z@N3ewO+2|**gz$yvSFnU|Y4m4ULil3zPgp|uGW2g)Lbxg_ZLF$<a1HbvxCVR;S`NMjZirTc8^TQp;j7RK;H%(DImg>)mDm<O-_x9&K)+#I{BH>1ZRmHf=-aTi+qMzHZ+S5t9fMAV$G{Jv<KTzjyU<7ByWpGA-tf)v^=Jq9dbkeS7On$dg|>jNf-gs#!I#68&_-}2_%gHsELsH?EdgH!pNAHP&w~p_j<@Fu62d1%g8xKw(32ys8RBy;dP>Ayf<6~OPlF4<r=msSQ{l7GbKtY#QiO0h^b)und?i{F7R`gNgkxw+I0oNJ2;Yr%gYSkPK?lL2<Kai(XV7WzGw^IeIECiJDR>9E2NwMS-U0uJ%7OopZQ)Z0;gV<xxFlQ|tqxa)uSOfeSHn%wR&Z0eHQEDi4d09QgYSj!N5{eU!;hnD;m6?@(XZea;q5uc+l$-T7XI4P^U%tu_>~Fa)@UVI^d4B-k*x{g?p{2D&PShv=fj)Od9dh5u(mHZ5yELN{y@(y5a=;jLbw7d?am6cKl9)`+Lsjw;g}aK(L2!&a0l9;!kxTm?nM_uxIH0U&x<nX)o640YPbQ~32p%2fZh$?0N+9g-{-|3^bz!K_z}1-+6nH&ckN3EKS&72(e`j0Zbk^#LF>VF;BukgTn;S;mxGI<f93{U6#j(}em^&8XNrD^{+WBcT`K$=D*MuQY%$uo#rSM(_m-huT!!PW?PTFnXoCXB+ttFA&>IRIZ-)z4LvJZ?yxlIWZF}K%=zRr_KNkr137s>2ju4jTjHl31=pc9$JRE%l9u7Z__J#X$E`?<tnan3kp#^dSmU(D0zpN)ZA6|r}(D|_Z-KqSo=py{rq<!OUuah>0oIg)j=LGr!EZP<peFc_$(UZ|vV9|B($?W?KR6gqra@vyDmhZ8S?=RnP16mk<mEW`8i$b}9o}L?o@M8Y0C%hQmK<KfNzdeP&5q*`vE8-pN&%N!B3E^evoA5Gt5IPhd1UDdruk)fI`WQMCehhvceG`5iK7xJ@AAt+<9p$?gB!n+VYrvPoH=}Lgo8f!W`{8@xf#_g(AUqNs4UdGMM#sZX!xPZS@C0}oAw1oSspxa)WcWFF96BBz2S0(1hM#~RMF+!=!adOY;T~`+v@P5Uu8P)xtHP(FMPN}WE2pz9yq^$$4P6Gm20w%jf**qGq7C4>@JWPlLG(JfAbeV=%$-Iw<XSr!t%o**>%kABkHHVai_zEN#qa_22z&sRM(h#FsWxhbFGDYfFN3c`Z-%dfyQ25PUEzn(f$+odFmxn53?7R<4UdJNMJK?|!jsTx@Fe(oLU<-R9i9m%LuEQi2+#0h3OW&;3QvTeL7#)4fybcZ;4$z}^a*$<{1Eym{1AK>+5^4|Zj82q8^f2PRpCqFe{%yp9Tt_cE<BGqHs6cf+(1vEuFa?Z&L`(pa(=}Vod>_n{orkME_}p`pS@Uu&V}caw}c$g4+!DOXj^z5pSKMC1Qz`e7JVLG>3z=$UX1YK3NLzlaXmT$z8<~>odDkgclM$OIs=^m&w$@SSHkbW-=SZ@-@)e<2txQIPk%<YqvCHTgcqVK;gx*Xg=lYhAw0#4r_lCjZ@4$dLb$&7Syy>+J|TQE8ih}Wf6Wa-_-rpOLF=MXxGsDndKG*l+!3u0cZ9nU!q<CI5xo$t57+0r3QM_|M%kDQYxxo0O$fhB2oFcw!h5{f;>8T~33w%c^CUVP9?suBi9QOy<;6lTMxz7azFa#4ym%H}NDLrv067DRp8V}w=oVr$-)}TIPY^x%&U?@gi5XlEGst<K=*cy*44%h#8_IVX%J&|C%61?0Az1VQShP2Ms~2s&xS0^Xg=oVu6TJ=Yh2DqW2A?J8(z_L<y;y|4gnj_O1kd-Pt`{A>xXp`xXaemBC*V=U8(zHN#k=T!^bL4F{Dt(rcxCPkFV6Jhi`+mzLC=6Cgb#XJ&5IknxZjJH(UIs4@JP6g7vsI(`-d0L5yF3?*W?ELHyq0i^if#!aX1DyLWjYP;A_#r@U`&O=p*pea80xyTobN>_Jpgzm!MtXOW;yy8@Lo)0=)q)0T)55!A0P2a)J<!dT}G#0j&mC<5+hfgr5(c58)KL1AQ6Z0e_9Ig1?5pN8g3NhyOzNz<<Fx1p++?AEcb*5W-iWHR0CiZD>vSHuzSwI(#eK1g#7=fg7S1!42WsXbHGBd@&(>D*9t?z^B6B<_5YI7F`X03-3Z-g?GVg3E^qzlkhaS4|*Fc+7#{scS5g(JHago;fv9;;EUn!asquPCtwNTH_^x7H{plTyWof6ZfG;O8{8bd9BvNRL{Eon!snt=-<->~@c+Enjc!E0fWM%Q+DHgbLPx;^(fiR+@F?oT`w8J2(7JF9v^-iDE)SPMuZGLOrO_+k((nanW%vU4T=Y`-T=;xKxFT8~t_U|oZ-+(Wa6`B$dJo(bZjRmyH;3Dxec(25d-O55J=_a@0`3J5AcQBNbKnW^GV~o-bT7ONUXOkTuZMRM!oPY^JSWgo(a&HB;lJ?q!hgYkpzpwcz(1jD;Gf_x(Kq2Q;Unl`_y~L$eFZ)YzlXjEzXu;g=fk2Ozz5;Nv=OAOP?$DD3@!{`i*|yqg*%|*;qlyeI}pO{2;qt7-|$5EUsUe9|Dugx3E^YtwXlTn|In*p3E>~mny`fMXJ{2zLii)}5?Dg`5LybB5Z-~7fF*=CqD5c{;WtpZ@4i6@Ckf$wsN941u`OII_xOFf7$JPA7cJ4Q=#6k!cr4lh7JVMp`}bHvc#aqA(GSoR`~mzcx+C}abB(Y(>xh1xd;Hl)_<Z#H+~dzm!WW`{!4kq1(Hx#*a=3q24Bgi&60Lc@>4x@1Tf;r!2hiK#2jE`lt#B{+9<&L34}3e?5WXF5f!2mwz}KP|!`H&)3E|@Csc>=lf4PB5J3#nb?*0EGgb$-@;luDoLih!A8vFwMG};I5!@d7$Lild91$;MrGa+0Ny%??tpMy%9;2gGv5716{6FvaXMjwV}!w;g};0NJ*(B|+x@J(n<_$IgxdM;cCE{{r^pgh~cC*>S(Hwa4zfA7V1bTzsgUJWPFjj-q>SlbgxLilMf9!9&O1L3Z4YxI6t^afbl8LbIn`TvHkj+RAhz-8f*XnD9KTnsG(7lY44OT%Zvh0qJ&Lh$M6x$x=m8R+@&8E_Fo_#(6-d=Xp~Z3v4tg{#7~(B^P0_!_hgd<}dZ+8(|RZiV)OTfujt1K>O1{)F&YbOJmUo`EidMc2bK;8o~Ocon>r5dIeZ75)~^%{ktV$t8p@@uD_*C0ZQ560U-t3Ri(IMWwBCDcizj&_7@a;fp+N*(@iwc!A?D>xhmUI&X5@NJOGg<oJIwr_DQRUHkOw&f7ceUuM4MBm9^9y?wcteza_Mvdk-q<a+<}7m&#ep2+_Ji2R@C'

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
