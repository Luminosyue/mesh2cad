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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_005.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_005.stl', 'source_sha256': '6c530d2b93aee98ff3c0f4f9f3e27b53c4d9fbc6c806ea83e0f78b3ae0fb8ef5', 'input_faces': 900, 'input_vertices': 580, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40584415197372437, -0.29368218779563904, -0.39995166659355164], [0.3987024426460266, 0.2528783679008484, 0.3999682068824768]]}
GEOMETRY_BASE85 = 'c$}r33D}L*`v0HzMH$Lm$+!(g=FCH}Q<4)x6e?aslGA{cI%+q_iAY2mu!)i~MW*E4GGt1xF%D%LA`Q~0@$_56XD!dZ_x@kk|N8x$>%P99_1*Wr_w%ghS?d|!Q|BA=<u4uBf0ct$oeK0yHVFb97X+n)5d($}zq|i{VRi4le`Hor-1z#R)5)E>ckJ9VD;N<xTK&!e!}<@c-Xc={s)5a_*N#*lc;C?BL;K#_=f0tL4$%JfeTNJip!{Kj`rbc4wQDqPR=;+n;T5$bqay#ye}&Z|BzpdKAXhI-e8BM5TDLa*eyx(|@H5uGzwmIQ|7~FWNV9Lr@BFyVPnKP{B{%FRtRI`Za7*j3zx5xJjQ`MH<0o@ZSpUTbj2|7o!`7+$uJz|Nns4&{e(6Apzu5Xg+i3^1#z)Sxeu1AC8vn)KrtSR;tsgni+vG=s!TXIr``wSV#ya1hm&uRTKA7SsiVoeLDc|`%zxl1U&W4+xH_J1-k?l|CkA3AevplC;ZO#q*ldK<mxb^0gI=izM82|9kpQhv=w0^w%&!3ulYd$ug2g6&8H`;>j<^1TDURraWZ1GWU*iURWe&oL9AEng!bIMG!{Phlgnv#FPRO9CiKWKh8T4{>)yEJ<%yuG~N)B0|EB?phQezPAIgtwRXqt<uZEBJH!UgNLaXP4)z#%8^|zxI|lw4YeKY-4WN|Iqr;=}R}J)cM!9b~y)4*qf67r1gWt<M*0=jo)Pbg%7+P?tkwux4!HDVAP2{#^2TRwQ#?A|ETp{za{E!HGXWv&L!sa)pg8zIX|f0Y=P;=V@o#VhW)D6kKFt2hH#x=Nn(!KzB88WNy&fP`pIKU_L%k9u!a1ptBrPC!g5$Yw%Gc~)Ao10zli*54Zdg<_7{@>_u>sH_3;z4#P6QSv+H}Pc1oS#vxa89g6~p)H#lJZgsfk8omsDlSpJ}f_2c|*v|vl?&ujgr+3q{0+5OY`i>)6m{j%BL5;tFI{qet<?HkGJYx2E6#ro0f`<ndN+BUn5U+<!MX1h0OYPO^I3y(4LPjpz#^|@icsPz+lu2>(g6U+X2vH9KQRd<K;V+E`q{iEt`vmaf1v8|KrZhv>*M6+Ld|Ah4;9VVLnIo7P*F5?#%`Br#;_Wp&|cl&enXv1BZ_7msJ{lxoXKk>fUPkeo`pLoCR%Ws6YulHM9-)-OcC-_;`cl*Eh|Cshhc>hmqztApEi7Km1JNKTQxnaMw_2a>)ohkV}>zesJ*7NdLax?hRn_qi2lOI_hy(VLwK^w+p@{`@#y=t~+tG~^11&<AyX4-B(asCAB`+4}ur14{2K77yAE%H)cZrJaJ-(g-}I6v5*_pw>dJiDCUzw5B^6Gt|T&duOQfBj}mO8(+&cbMfr-f3!X20wB1zL(5;B&u0o9Dk+nj;GF-$6x8Y{Metz&3eb4TfNe(*WBTD{hj~3_1*UMzUY7FCu-EQzqfeVE4dl`SiV(bGx@<!?d&`t{OBv|#+v0iamfDe`1W>Oce~7tTklV_e$LivcDz?zY5d@!mc|bT-SR`LkRK~Ka;eFy98cti{ZiJC&YGD>sk5@D*&lMoPR$GF2k%=y=rJ=dCI9OwX1fO)Zb<pv;QcvvfB5s{Gr1Z3;D^J{gzLnr6|(!ovvxm`e$e~iRMS82uCR6bHMi?KwwXPj!H;cz*sNF3#ICRRw^%<~#jdaSxAjUH7vA4t{pekGef{rFpK6!C{`D!p8`Pd_{Mdve&*WzCqcy*JCZ*1Ug;K_a^y6cXOtsp_`de3+^OpFXGtGSN{XFXj2WOc1JUOte^=}_x=8xoz;(3|;;PVzc!+y@0(Vv+8QRF*6`B`ed9H-KE<IeeVoJ!x1>q5nC|KC1rt@+(G*P740-^=<r@pfCo`9ZDjD>LN>S6JWW=X9Q8)+cB2Hq#G@zKu=3^y3|lZ4Ud%Mfl&2+SEFOpUBSJ682-yJigR?zh7#7=SMrH){i}H{Xo=reuVmozgrq#9)F!LkH6j*$6xP@<FBtTj=$btwfrr!JmPnQrPg=H-<%^YtiNlS@!j#)``fMW&p%r=++pgqzTEDI^uPC8SwD8{kImuyoJqU3nK~jr=LPHMkRM-kgV`^G_M?}XarpgAvwwKMgZ15b_x{%v?RY=l){J-WKT^kzYsS0uV~lt2uYbY%tv;KYo54@G@!ll=$C>)U`=TG5FZ;p!q8}owzO&=wntF@O@~^9Ik1x(|XZ_fDHO%oPTJE$Rw|DJWVSbO}qxa)Gjqi@9-WSJB=gZ@!^xbhYEuZ72^xbhYSToc3$^5f7nf2YcZfkBPf9sQ5!hZDDPWJp;<a?j|oa;tx5BGm?PX%*boaPU_eRJ4%{hu71n(zGqHb3_65bKM1N&0SHa=x6Gr0?b>=gWCX`fgtGzL=M!@8+fGV`pu@j{oI#v!6_wVy~y1KgIgN{wel;%e5a^zwmT(JrZBl)8;$Br1g{k?P;&~?}!*bws-c@@c8xqe(SsO>;0#vZ#V5pcKkX&cyRvq@c5O!8^7May|@{tIgDTFCmFv%(fdvR1#j;($K@QZr@X(^`U$S5VvqN={?UVz&G$K<_x=yocjxo*yf5tij7Ixxe=eS4&j*~}!uqkFr<n7BXuf0SI1mi3@s8<V=3(#OY5m~1orja39ksqVzBpeVU%W4lFWwi&7hhi-U%dZq^>;G;ZgA52{=UKF+syb3W`1Mu!%VDUuZNvK7k{sv$8tK(UuU;h>Uoj$-FcDo<$00x-FcC(BhHJY@6L0aFVBml@A4BXJ~8LB!QCU4g!g~%53#=6|Gi)G>1}2|`TRP29|=E}{etlm<L&-0{h*fJ|9zdWeldQO{a^aQIJ^HxdhWN|oB1cgJelS*PdeYtC$Yh)`QB%qj8uHm?q~D6&obM$*Aw<Wu=C%weh`1c-Ur@yVwLePEo8=B^11f*KCtsETR*a^y`7f|JZt@CjmDerpWJQluR6bn^@BQl%y>+et#5pJTuAd-U+2r?LYnW^_tLmIe+^zcWyW=K^SAcCtMlhrKd0zvd;jp@Ma%7e+%<0c=Z>*ve(?Tr>nC?VYvzaG;ZpBq8t=}R<K6pWynA1acVAzOcke%P*`iFp8w|I;AMZu+k5o0jo5#F=(E4s3i&h-7EYp6N=CfU#FZaVV-))zf<Lq&9<79K6FfzKDJ&$t!HtXkbUoPG^%iiCNtXLEtzuv#x`u_YAKX(3m_ByAR9lt(*>U!hH7{AhwGJbuX!`00=jkxnq=`()ge@$Ny?w{z`??1}qC$ITvbJ$Nb_;zQeeCNyj*r^MR9})S^Pl)`S&u8t(l<$0*AMbLx8ApN0cYa*vZ<zm4#(aF4AIYn4kAKgm<~u(o`{(MRA7;vTzROR{&wV}I&+(=0Hf8c%KTAI;>bU-wb>#MvzO3W6OH9;}+fn)nQO9jBSx0VP>B~B9JLZTwa=S}EF6*#;)9Q%*LHe?e+wM_ONA4%mm)l+LC(?KM$xVBDnD)T)7MtH?KJ<Qn>-+OM{2(azwAueSu6aLVeSchY{)w~Gbvvi*^9NG$f3bd|&+`XT@*nFuL$_mR#_UbWA8Y-@z%hGM@^=@WZQ2~yynoR8?zratev8cUE;_Vp>hcV>etbpO)a7Zo&E6j?Q)PEbesk+bCsf{@lApaZWq$U4!JR4dv-e}~+xfY-ou7UG7u}jNKTF@u&)&baZp!?e=DYd%;*QquJ~`!h?fd}W9k0FLjr<|@c<ue0C#M{*ef_SJQ;yd@e|^El8GkonegC{>d4Y`E*ZZR1oG<%L`mW!+FZwObr{9vttN&{5*NSl}eK+o;@5dd!9H-KE`9XHVp0|nlT>5SvmVQ#yk@LCqWgR)6J73P{(vOHbaz1yyoX@2%>&W@s`Eov&ejw_|`P}<rK9_!49WkFfU+yQ;ciUb1a=Xj@MEZXI?>=Keru{+sNs*s+92dUKPdi=<KOyqdj?2QA`Dw>r;m2jZJkAPV=BFJ`g)jRv?RYADm!EU?YWqA%oS!>io`?H<aUL#xH(&WW;ygUfXTHiQ*2Ub9me*y@m)B+97uRLp7uRLJzPK*)zPK*)zPv7LKW15Y|8&<`X+GCk&X?C&X+GCk@kNKs{bhOm8y!;BJdc;x^^xoA+voS<dOXc{_aE@(^>~`k^5i_de|4tyP4fq)=F9a>^WFMp-)o*v%KJRt7x#0VFYo6_-`&sgb;SJ~>AU+mLI3&djEeha(s%dGoG<U2N#ET!^L6BNf8qP*gZOFB{e|!HBPC)RGL0kW%W>p=F^;@1#*wct#*z2M{Y>wR`<cleMeT7z+&7NQTWiOSxbN+Kaev$S^8U8;-TiIvi~HNs_xHCa+-C0g%lq~@n}?XXY0p)K@1LvUr#)8{zJIQYpY~i;`2M-7^W}3@;k)M-kzON=pEhqu-_0BNY4e8k8P|!OGwphb=Tm7u&zqbtpHHRvF8}uvc0Ul$H@z>OV|rga$CSR?PrNUlV@lsW$IR)F-?qhbOz(^5n9i5aF}*LIW9D>gxFchI=ga!|Y4x2ipOZE`VBb5D^9Fv}yy1K~Z#ZAh8?L^bH=Hk?vwL4WXHO28@=2y~Cw({WoG-_n^xe2~z8rVbcjM0cV%$mJzt2$09v|fU9^M!4dpKXd@8Ny%zDN9lvep;JFX_AEm-FTEOZx8k<?D#!m-OB7$oca4C4GOq`}i5F;{7h?%lEsyFW&F+b$GukGL7e_&KK`@d0)KWbuK^k{VwUd_q+V^@E%vJ|KX{*8GQGCSNv0a-plgm;YHrDzIZP#xwYEPOxsub{(UF>wD+Ba@85TFb>#a_!uRhx;itXtBz%8<aznmdrjDFv@YCiQ=gWD<`Es6d_2oR{eDOZ5_r?3Pk=_?uU%V$AAM}Ow#rwv=@e<~~ntcD+`SN|{=*Yl67ZUGR$7;U3CsY48KkdDA=garfoiE=@clG6a>CTt$r8{4~m+pM|Ub^$;d+E*>@1-X<R<zIM#NQX>RDR9+;_n^2FaF-a`{M5!q7!@Bze^B*XA$px`F_(De^(MI)64h~#!>9`<>oxw`F`BJ5XlSsamG=O$oJ!p{GiC-)H?2ZLHPdq0zd8gLiqmr!qt)27sB`REq>bdh4B4&pR(HcQR=w$b-t_b*4O*Rs3Y=SeU~4fTkSxm`p%d2y)WuJU)B$1K4kO7-$_MpefmJA?e2WJ-JLJDyYo}Fd*_tDj(fXO)n6Ca3<4d6g3`gjzM(&j)29CCH1nUv-QDQ_>rdmF*Z)8NX<U!2Ab3^9Yv^kDHFzC*akk}kaM^6Dm%(M>D^#>bYoeFIS}%cX!ZpzI;2Q9yDhi;xvaFs5Ykfb<vJTDr2+g_ZTsRkg3mpr;1y4Y4hsUXSL&bB1<~LP*fUZH`fY+k)&^O?D@OX3_d<S|PIu5=K?ukAJ_k??~jJ;USUicHxH{l8JTcPE4>-z!yu@BvYegN-*ccW`yx1PHR&3jdRiYCytZ~~r>&V%Q}&!gjE*DspSQ{zHy;-DZ}AjDa;vlwoU^U>CtKg8$L)>;VGwaNzecg};$piSU1a3gdB+z9><{Sp2U{vN$P%d*xete4?ZmZK0{4s8sVgPWr3;im9L^apq&{1bXjmSwH&-~}q~)N>ZRgmwiL#Z(kkQBp<m(6SY$uZr_|exfLSTa@p*f5k%ENoxtT7+eCbgjRqn!7b6|a7%bNp?Ro^2UQGHag~Y)+5#O0YkdH20XIX3!b7RqjL=*jtpHbGJ<FrT;qq`rv?N@TWvYm_fLrhzny*lCiHhpzMR0ZaG8GrAsG*`XdO2JgE`?qOU&ePeU#+%zYZd3CzXX=ghxY_l^WZ)3%V<~lWw<?B4Q>x#K~!TsYOvflpjF`;;Av<VcpAJL{RG|(pO<CzXIO{ktFmlpZpGMY#rSH4|2?7kL-dp2+&I<T2<;M_8`ql4pjCr&^MK~_(2Ij}^M>YZv^1OzXQ8FwEI1!}5u6V`AH4)VAHEc=244y{M!Uj|;q_=9ydM4m{RRF3zJ~om?<<=Bp}4n-o6+HL2Nit-`*~kJ`v;%toF3>%_(m0dRCGpj;BJ8(!#ARR;GQZT;qyoMtQ+6a-@OUF6TS)Vg!YHKs~Dl;R%+f#y+`1O(GhSbzS|M)2X}-!pnc&Utm7^G)-BW;0Y8L}gk2wXKzqRNsF*=N&Y<r!FI4e5pTEv$@6b=WPu@mn!kt-9*N5HUx5-(6&VgMY-Nbiq;(I;eThZ?D0=~NhoeeL67o%}_F}w(!1uudZqOZfQPdl<~9r^9<@GWQ$xG&#xef199hjq?D7X;__mnCf5B`jZmbP?Pi?uRaf7xH_WcdB?)#Ub=9_z--8(7cJzJb=)AHTo!gHC&m{+#1~pw}wAf@dx@Bx)c5jz97r$Ay|jzqUZ_uCOytoltPQbT6In-+M2)Sdz;{|;caX~tuxR~@Fv#T?bljcq66RotiL<fYp#S=4$hq$Xx8Tr1<|r-Ww<hZRF=@(1pOFp0&fWQ;|4<WkA!A@zNSO-b?9HP4$W;)-M?)J%{QP$;iB}f=J_iBUn)LBcfp^*7iQVe{9hG+qC3!C@D4bN{tJ%6RS3<k(D`sHcp#zqBSP~@^fUM*TrA6~UOvs8(HqeV;Tz%hs9x^&v^8Iwb#C1>>(JbmbJez-ueQbiiQFCVPw+-G8k{=^*4z}W5}Z3{)~wH|3!x>^DsUD0r6ghQJ)#5Q2&~UBA4F%O1L1-6<4i*H976MU^d!6;{sz_k_zi8%r9*wKxwwii^)hDJ(EOE(t>|X-OLz-<3jGp31(%?Pu3LgRL2E~}INTBLfR=<iz@1pePAq39{L-jirqZ;(V*T85yY<~lf6PH=qg&zGa2(wXyY-9{n%%KQ>o#-?ybb;uJr$gr(=_Wj?-YGgD%3BU^*O&jf7j>nm#dS!>MF{p$fqJp#ecJGX#NuoU>%zOK(k>Tn*T!c!&?8&vV6b#%DpP?AvE8O4uS86??V3x-vtjs?}N1thAXMxs-~h8dJ$Y9TR+oM>x@=`E5en~YH&FfRaKNnE5qgC3TOl_rlK_8E6sPx@!NVCj%Qgtk!3ll;)^W%J*}mwp+D0(E6`Q&QWY!t-b%ik<TIV~B03d*5$=xO3U^U)i;9WV(RHVw6XA*EXr8QMl8WW%d+>7j7<v>w2A9mXp}9o14b8=~ZD>A1?tAbNco{kgUIxEFXzogAz8Rei-wbzSox9N=-SA&TmxualIeodDbyz_hV|yKAosQEk$+oS8Rzyp}C0S>;kCk9QsQ{Npi^Jv6VrX%=7@VZ<j<DU6^w&~!8N3vph`s<%gu9?!;k|0i{71##X#OnA`IHt=aUigIFtDs|^EOa%4SGFXTSYw;wb1%-Ex0Dy0IsW|p^7@_m2e%nHd+sEtD+s>YsYu$^4oeDUO=b9Q&haf_g>;VZTU>+>_z_r>vcQG_YU%%DfCNz`YJ!;q6_<#9#i?y0<gX?&Qh^2u=;6WS%>CH=wx^j+=kG6Eur~3Li3C0r|^sLepLV7e%hL|i7fX0Zt%@$5E?H*XrJiHKF}3kbHF<NP3)uJ_OT9oiAnVFB-ZBzq7B=sCRz(^1GizF-9B?I+r2hi2fYrii?&6tgWJMW&==t;@Bwr`d;rcz-(|BM^U-(RQ8$-dtl}aS)zQo00V?iP@hJKT{3tvM{TDn6ejI%aejI)RjloaAPoYo3Pr;+nr{U4?7#06k@vMqx&@u2Ba-6U8MxqbHBjJ8%U$`IK5^VvugsY)d;c9Rdv@%=;j?kaFe=kAHz?Z<6qGjPr;c{qsxEx#otq50uE1?lM!ZK)Xs-l^SMrdQW5qu@u0KO8gi`Ikd!nFv^wPCF_&@12?@MVN%w{K~!iCzKMgzKQS;W}`Av>sd^ZiqI38^TS{#&8q3Iob?<NW};h!_i^zaQFfAe)s|SUi6>vz3@HgVE7(*5PBCp2p&La*5j-{IuN}J9thu!4u<cBhoJw2hrsut_rv$WL(yUIQ20S~1pFY}8|?%4hMN+7LVc<=2kisrzz?A#U_FlXn9<`*k6ArF$IvH_(ob4Ph5Bt2{i^lxP(MG;cF_7nXuCYYcGLP)XgfZ|cGfx?9?kE&eP9gBIfi9>h#1K_Y3&zU$A0udKh~)^S_Rhozuwm`CN!5p>%e8;vS@v{EL<LK2$zQ|qD|n6a0G1*H)nY?Z&NWt#a47Wyj{gi6(6H<cshAA(Rhfr(cVU`<E^w^UB}aDPp5|FA}R{0D2x__zf;GuZ&jQ@Ps0Vt)1KDT!8tBMTkDzN92chT>N+k+yCC&6pH}>pZlkB*%_=si*n)0^Pm#9)-5BE2v`>@k_*>epuH#d*Pf<hjH!8kV@ilr9-lXC~6(6DN;gjTjh^`OuH?+SY*YVf1U0uf~X`iHqX8n%E`zqF=tKsn~o>egc9Sg4}?^$$gh;wP@lIwUaZCBUvYTB!*p?RH(4^$-3HSqH)#;KTyJ_oNMZyfquh}Y3xN3P=pZCBUv8ro~9q4|5&M?dKO3OxglR-ZkiVhs9k_zZd4)B5k=9Dh$+>zLpie@ENZb$o{Q8R}_1r1&!x`_TjNe^eY)@i}@JK0w|<^l*p|(LO}3<NdT<UB?G#AE1WjxoVl-Q1J@-D*T#?=_=kt=fSU%Hyxc9;<>cvlI!>t+ODqSS82aW4b8u*SfS!9x*YyZ#Yz>wqpRTM<gG+kh4@$6zmn_tENxfU@p9VBsiAp}>Z92zUPouaFROS-#VhDEcoumtq0>S<hxQzD9luW7)pb0J_AF{>{zS!6wOl*Uci}u0%M|ZK--Gq%I&T^JUWj$A_t2do-a*^db*yXUq08VSN)M|@qMyT$s~DvshCT*=PTnZ=u@E1jeS}=cN!qTi<Iib-P7Td>sJKnV?PxFf0u}oI=lnvn2;7Uj!f25Y-$DBhavk4J+tqd4i*_$+X#PUQF%`$rqwrHIo>1{L`XqdmyeH5nL;MBpFUWO#oVKg$_$ck8)X@Bk+Gang_!<2XUZCP_6${aK;2+6*8+|9lztH}LT*p7tc6A;9Nc%@>X#QQruPS~+&%#SoEYkZLx)?r7-Xe5yh<~U3JGqX3qwVTCK1=&7H8eNKR_Asqu0-p>g;bocqA*$zu1DVaXu%LSpxuC6$5+yJbsg8EU5^@?o2Y1{qA}VKzEDLG6-Cht;D+QCK`#h#6WUG4b=;V?tLwNS?S|CQ+(t!IMIE#jTvtVH71yHIz_rM$jb0PtHniK2>$nbWSJ!bZ+O?>m`Dzs{RWwJN!Yx!ZQ_%{&3T{eXGxVwuUrqaJave9P?dm#iO1mjFG<Uu+E4y^Q|JQ#C;@m%d&m~Ct4@1arroJW{{$|Cd!MT@aJKtD9ziSg@tN-a2xC-^tt^WaXPjI9'

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
