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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_007.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_007.stl', 'source_sha256': 'f694090b24baecd7250b299c1d58789a1ae539c47ac9f3e8a23f13f7a3729159', 'input_faces': 656, 'input_vertices': 466, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07004956156015396, -0.4206494092941284, -0.2922925353050232], [0.04476454108953476, -0.29851067066192627, 0.3810269832611084]]}
GEOMETRY_BASE85 = 'c$}r22~<^8|NajpW)77TzFEHBG&9X1Q!GvN;8-e(3eMnl0F%TCam>7_Sk5CVDtaBj5zQ25;2?sEk^=(DpcfDnh<fYIOiKNov!Cb4Iplw>|N8x0Yp>^Xp1aR?f6qSOz0bM8(zDOYmFh_N_l~q^!-~`oTS$`Ds!MgG8Gh5IPZ;YL)N0a{*-p|M!q@)kx~`wMhvzUSX@)en={UcjvD2D%v^4GH|4GvpmZtubr%j(WdeW%L)5iH}e$UYpgZxxK=!?-){M6(3+qG}s!qT=`3(Gvq|MFi|H3j?mpO3_;s$~6?uBoM<?wKwx@ErxN!nd8z6TU6`oeZG`4PNM53fzQmJ%2~|_N)h{_!WJ7K^v2A%eswmpJgjA@|9;l312>c197sOnDVLU>-p%uoc&q`;^ZkW@+IlNCSS^ajB%3#kG;ruB(E^}a#ortf6MtFO}?JLbUq35oZU){Yflb7_9EYUIaK(LgmcWZmMQ;ozosdF-B+?6n)0vc>-j4Q$2o2rQ$7`aJs)erHq1j-JmObxbKdMLxbHRGg>Ok%Nk7Ka-;%JD@!R4)TDKf{k?$CtC44F2Yt~N@^8dRIuJ_y=;XAV1o8naT^*GA8X}phri#T%ffMZ7AkyQr&eA*A9&d>RC-imo2ui-wP>&gCq3Ewtk!`2u1*5NMUBA@t<ysi&3jQ#)N536kI@5p*&ilfB0H~D%TCB7BnINID2{@;~Ep7!|WjNi^QZbe^@|J=_!hWK?}PZIMG{~qQox4Ve1Tyi~T_PYt+kq{&1%^F{y`Lq?j^_hZo9q%H1YgPv8r2dKvMqkcK$GG*wg>Q+k%6y{X*Sjq8k>V?Jf5<Y$(S2)HrYVjT|MYutoZZN@Z&dW9!Vbb$l%MJU+tk0JU$MWO{W|(TyQ93wcRc%9_%@~Rd(_o`kpH)b$HLEp&wap=Jp0&-eEa1vlP_miGmTr(FCUk2vVK85&uncK^RL_yzPhkPf4R=HMEIG)*Y{P&{MKXPr_*n4%18HY+3#Y0a(zb`ef{~OeARlK*)K8WBP%yd@%4GoeSLjd2EMmN)QOVB{_mT{t?29dJK|3BdY|HXQSVHW(bxAG+uyI@KE@sAxY!@0j_pI?AHqD}bGa=v)9<9w|HnQ<{~!BI+)mB|_8IH5WUQCCZH)hhh;RL4KpgxH^y>)U9vgf_)N|Yd#L52?>-5iG<BYz(ejWYOH;e0yog;k9y=sVmsmU?3Uls8aqC}ob>@@fVp62U~orLSkFB9?QXU7zyudh>ScGXSDH^AgO<}MY!E!LlTc14~Y3fFfr`1-zNsq+f<rPwjdvpVwWSv$h$OZQ$9zN1RR1o*zpzmM>35541zzP>N%dFsBtFO}!%%Y1&o`%Kf^WN}|&hogT%f75-@eI@e<;xzq5^tZ(J!@Ol4H^q@-d$WIZh5kKFzEm$k%!3m15w15sLCl*}=U1_QZ87h`FX$!mk$P3b{KPcExc53C&nk_@{Kzr2cpsnQIpX%ya-%QhC*r=iM2T@NF|V2G+&*xySdX^Z1&57wZvAvdDEu7Z+w+S>9E;0F<UcF=u(1v;1Clnwj}pFeuLFGfipWQr6>=E&_Z9e=qfv)5gXzC|+f+X@{e*A3_b%?cOL&sem+m=X9v=2UJ<Rl>?~FLHv&DUsXL_6S-!^@zh&Q7N^5pYZUw8718i-TiZp!nyU*UOL?wg;dO7N3IqOP*vz<xEWY-60kS2B-cKWTbh)QL3XA$&f6_4TOxdK_s^fT-u^{TavB^lmc7Ej?tc6U!eSaV9_i3F7x^9AWg8{Qu&)U!^YAU2p;8$fo(U1?L>XeQARIC;S-ZlfIl?-IQlV-#WW^qtRC~4`Y95dKK#^IL+i+o91ACf@3i5mA6xcpZ42PG0yZ5`t?(>?gOI5`9br9uRkA^+NENB>Asw~9`%2t>rwO%#<=%B5!a>kd<*kK-+r$p*WFtQMqkcchdfiqFis%G&A)(pXk0_&ZwvAhz9s7-?tAKB(cc#2WAd%3Gfcjmx!ROxxxWhYmg*~fImjD+{#EP)zQMai9zh<wzrSFg>DG6Jn9m?L&JUiac9(rgMqkdlV#>4Jzii4=o>oKn*8D8gkIT1+Gwop%)+6?F>$`O^4^s<-uVnp(x}Dl%pNKOxhyJgKKW!fUv?$DfbJVkY3z5I>>(4vcH)J>Zr$iaoslLBSQxh5gXY9jM-S)+q{8H1nwkc7<cier9_q6mz$3*-op~BbSA1p2_#P#aF{v6czPie}$DAW9G`F)8PZ*m~Uz5g5HJc`FUrSG`=2<s>(UDUH}vNz&CaLyEQF4e^Q<a580@NEfUV*imQyD|Rn*gv0c#q)hq6U=AcLDWfdBYYp2<ZQYw+vavljlS*nXgt?`x^qgz4SaGCz7_RZ`c(L~z=DIQ&rsB7=^qt*tUE`k%W0!;yX}K|E6o)B<-i>JBXM6!%jl;F-%%KYx~iQj*0mIvi2j*jrg5dfn1iT)yk9vUrQrRFzBO}`DIaBG#6i@R`TeTguke0F-<E$L^_Gn9b+(D&7&q?}o)?WDUFu@+Em@aL>sp=|itFP0nDlHne!f9p-yih#E=>&KJj9{?T~=Y;O`IouDPO@p@8f}efW9Rw5%r(inQ?;AKkK}CKl##!apF-YX-~1g1-N3~@;2jo+bm2G^AOO4^Ni<+z40?#Z$Jaa!F!HU`?k1WazNdK#(K67tc-OUPy^SM7mGMKPeuL90nVJCzwjLQ@!4(k_2+_=mX3XLLe2r>x{yD85AQR&&-Ws`ODN`TLL&S;8?LvY^2s=ZuRmX;tbx(+V}vi~ry-w@mSG;o2Ocoik34XOxGs6T#{pc|Y1CnXi-@oL*1T}suVj3Gmd3lmzdan^vlf1?2=#YGKDURVZWj)r-|~R5KBZ4L;QNk$6U52fU|PR6{{{z)>r`J~y05QCeO%eU?g8U^)W?<mof&7XY5hw6PxixKV~+2a20#B6_QPcS96=cyD11xaa@Lifm``b}EBxF(m}jT_SaJRsXW>gF=f(YX{1J-%bM!;(>wNy&+61N;eI<7)#w{p3A&y6v;yF{2A>v4voUq=X`{}5kgeCaiH#!aROA@gUKV6LXw9(P<^Fk2c=`ZAI4Z-syBR@@C*Xoc2(a*}~%<U1J=T8-rpOGi}J65j~{gqL{!q@k0YeCrwqyLXO85IcsRz0luHKB~-CwxosD$HB06L>G8Z@uM$`?zM8slP4bj>tz@y+-)9Q9c}Z2==js9TfQ9^ary}dZA86c_7ZMw@mp+qk7P<ZyHw~h3B*5ZW-QB(*D4@_HDxaSBw0Wx<U9};M)NAm(NrAQ8?b`eQO|o?r7|*_PN*KJL7&;c%GK~=I5#6^Kh>?E{=j<9Cp^|>(5#H)8&fEzxyZN|FidF-|#IJzP<Q+?0Y|sjuzwkBnsbAcn0sEX+L9s_K6X`wRk7$vr<vKs5hTz=5qk`Id;%NG49Byy~cXh-+$zhp@@^W75nh^`Iv{1A&67*0P|TKF0M-&IgfscDNo(kpTCycXHY*Qg7+HNi>;%7sL@vnPvO4g{EYYW5q^l{=!ANf5@L<M?0609edXPABHjoe&VwC!4mytO8sWilbKt*RiuoDQgZUSt&d2sS2;YtQ<GCrh%tZYRZ?YG4wH)<O>sx#uA6{4Z`g2f!zDUDM_h8&C+!yaiJiq8$idQ0^+#Lgr{iWQ`u+Oh75!a;*E7*g6GZEh@1N+9X6!d>k*?hgj65;2^;XY>HKwS-shF@|)^taSnf&7O??7{l_7uG5FA7yCx9;|os{vZ!svBy~d)=uf-KI*=Fs}A1VS1)A$5XPyE{fGO5?%UG0VBZT*NfL2~&Z8fO{VhC)elYXDgmJTWc!_vJ0x@pJRa1Z6x211n{LA$H*#Af2Teg*&d~13r_ObBW!nY0a!Tc8mqfS;;-3H$SadN%z9N9iztQXz4W~7?)AL7Pwubamm+yMQHx8u4>LdE*B4X(S#xUQeCuffi^uA(n--z`nVdz3u*NhIb6&pZ1c^YFa$E{HU)_vg>A=f3&*rThB+qpWEzuJ?KW;`Lld`C=W}ymRP>W8ASL#5$6_)8OZ=<otYz{lq(kdFs!{udp9_MKPaD)Bb7miik9>Uws~)`$dD${~LTSvU!CfzT+8wKD;7DtRvZLMI_=zB95h{m^aBQBoga!4dQsGW1V^h!!Nmt`~LEMalOi*K<0DHw6EF*`7q8Z?hg@oj~(PKd`HpO=wEBD$+z6Sgy+|mKB$vHu8f2IL0+%|-_r&*ppWO8t?pRtO9Sh2KCj@qyppyUeMgZE>;1tF&p4y+=!pGf<!$Vr19Bq7IK`(>C$+x8{xBdd0`pl3`^lDJ$a6r9@NEy?N1i!_*tb0+B8>B+=cD^d@fq|_-7&z_KjWHdAFz3bN4#iV%bqLfUoov~*)s(B6phFHugVNJ`f|o))4Epr2S%9c->neu|NVX7r}e|Q`x_^V<Nn?enEw^HuC%J+`@XHe2ge<YadXO|jlP`L7wi2%8xcq9?}qtIUqIj0<jZNjIc`JYEB##Qf5!f;>9-WVwa6FwTWX7X)_p16Ci+_sbQAq;{Td+u^bpgywtjWdzjzt0EBgn0pXyfw@wxxVYs$inz9oH;DZbRtS@@0zT~I%*6RwE)^hm+?%c36GH*6mGd4xv{zMmC`aXr3?{QE`-|M~mU<61Ey&%UAXi{>!?Wf5QQi=XQ_?wrBT54X6YKKtV5Tl)Kw{bmxrpY{n9zSZ$I>N&FG4KZ#Xd|%Ypi@u*oeO!faf6xm1z~km3AEkE_<iqzCNA@{9XL~!tzx$Bux?7Ubm+s8N``*6jOYk4=67!Hdg!yzrKA)Gue^4Lu#^<>FS%~nJJ120x`w}m~pSKJ5Wud8VrO$#9r^ws9PJ0FJGS?yMQ|aYHf4->>ZN0oPZsBpf7cFae&ge_&Uz_Sv>g9_54?e>EZM8?-FR5q2PH}wyKlu5{vJXTY-Is1YzA5z7i4+mPM-Kfzg)g5<q@N~y+x<esd0ci@eBL8P__CuW-lHPl7W1k5j?{-Dj^)(R6!cF-K1G4J@2w7_uIMW_TcXZST{87|r2fu)66nXUe+%qOr!s`EbdR9l#uUfaJ)C}PbN_BW!nZ!KWE$&V_bs`7d0qd;b#?QA&wc6n_kwP&h@UeVKi}RPF6zYAwZ=~4dUs^4MLoC|>=3^GKDn(mp4aXv!nYSp!TWjGkwnqYJsSR<efT-#z5|Fahr{RZmzCphVt(Wh;oA!LV!bSV9rs-h6u#quJLZ2|Tf9eg@n--1xW8d>VqB$j1Nb?k@O(f10p_!F4fyx-@x5bN13dRTJMX|ew@O1@MT`DY=O=dK{nhJAaVw?YJk3}qidzBwX1tH_@H;kvf4>a#v+XUBzcjsUyU6EWBjmrw9rH827=FPRtfR2)n9rd7!nbDE!|&^lKf5COO&z`+>!=;p@3w}RpD9(*zhETxw><+8e@dBnU$Yj5bKVXk{*+ANOIfjapU>-XP4u6<U-)v)0Q?;LcumaDL_9zBze|zwx{Lmj|M0D%KYvec+0zo^`gIh(lz$QLd(oGX|CoR+qCbCsYTe_8eQ!)};p;#Dw@2q(G5Sj8_xQe$+X8v|&e<&TDOB+NH{!{4F%Lc+g|Gj9U&{L!d5+i|Ci>t13-cT)iS;54A1-|P?lshBRE?X$ADS$FA7#z;!9JYZ1aXFJ7QX&-IVn0C*EJZwH?}yc!9P?TalA6c@2}*%4UE$U`48HU-|yxBj_<S4mk?(_bNGePsGo>jT$g9r2623=I=)YpMBWhEZ;tS#yNRfisQam+zejK3>-(xL;vVAkEe;iV-tK|<EIEcaeNGEsayVf>i7G^#&zlQh&h3x;m|GwD_h`Oe#K~L2>v~W4O82V5x8BV{K1FYc_)^#5>xABViuF~pS@^Phec{WF+K6A&5dAw3Un}PMR(oFWUi5Dtup0L(1^Y}<W#m8Z=1SyW8Tl90h2PujJCRqxRNVKd>$tA&#}<qEDLhF3hVZ4fUJI}u$79|OMxlR;V>WSIxRd^2^jDl43%xTR`5b>WT^wJG@2#oh&S}(DbY=MaKlIa7$q7dP=$tgf`947ScaC7*qBDhWvmRWasr6n1jC(8^zF&()n#u)3O};#%`gcOP9+jiZ;LlyYL{t6mI&|OBFKDM2mwyK+$F{m9^6@+>e0xqH{bs_q4ye6Le4d|#IzPKPL!3XLF?_CH<;+^)+Xs#izCF7c_LG>$!nY0D0zbzO@nass_kL@)$SW@f_wmdZ!gqLo0AK(6lQUM~TZi|FFvgeS#)v%S5z8Ws@ufH)_#;z=Z^=(a-JZRPJV)k7Apgp!hnUM4*Qafy$cujm`+R;z1;NkpG0l(7niYxpIfp#Y?!^39OCpi~Q_fphMi)=hUmIW8UvGrmP(4L$uS#_!|Ivm&HP%e+pRO<dQ{xHk{=fdzxV`KD`A?1aI7!lOwQZ$tCT}HgpspovATOhSOI}9)ni@?0nmmy@fjp5smO7F=mOPBwhdhkji|S79MV6_bkY#d5>WAcx<aX3%<aXq?)c474$sMSz$sNeusGZ2&$UanWvJZI{bt-ulc|CPCc|G|6buak<`4sge`4l;xs*vN!m#7!X*QwX27s=nN?FY5(qDGQ;k+)F8$y>;4sG;OF<VDma<VEDk)M@0&WMAqyvM;#@)sx(V>`LuSb|t?{ZAE^UT#MR}T#H<dT9aIj>_n|Wb|OEOpw48iY5W(p5?N~+OZ2LfCGzXkdgRy1&8Z)go0CUSN0CR67gE0?FC=fL?jUa`AE%xmA1B9B<H)h(^VCGLrYU4iuaLExiFQJbXnL3&Ne-v(A%~MgsawgR<R#P%<R#>3)Meyp<Z;xm$>YeL)QMzIa%bvTa%XZY>M(LEazkn_azk=Ws!Xm)u0iccu0eLDwj(=}D^c5$E0L>HJCLiB>ruOr>ybaE`j9^+kD|^Zk0O6ZT~Gdwyn}jxyn}p#dWw9497l~O$B`4Mm&l3a6sPk2NMmjPIp%~q(lnZ^)t9zEou{w$J4D?@K1AM4-9p|?-b`IX-b`LgT|{0>{+2qK{4F_{>PrqLPoVZ7Pauz^x{^nd`%vE{_aVDeYmwc_pHQojKOuiebs~RAZbsGire-|W_<ibMWUXo3nyT$ht=Tm0M17syiR?{nPWC2GrH&v^C9kF~B(Em#rEVwhC7+}oC!ZuM)L61YzDPY!*7O=#t1Yd@u28R$kE-p6+U(SAWIK5ibsc#VIfVKRIfU#_wUYhGU8(KKUCDK*uafJKOC)H%1lF3ycc?eXcgUBi=g61IhpBtXhsk#8CbFHpin@@ziX1|nNe&^;p$3uXkQY#AkQb0wQx}m}lOw5H$&us>)EM#wavt?AIgi}N3EIR7tTm12Q)iIplcT8n$x-AO>RECO`2sbGe3kkmHHo}WZ3or1ks3zcNM1}`N?uGJPYocCC%aL*likQwskO;f$qos6Ujl1Q<EzwE@>TL7>RIw3@<!?o@<#G3>SFRN@<i%1@<g&PHGu3(9z-2S9z^a(9ZK#;9!Ry42a-ooza)<$PoV~rr;yiD!^vyON!07)B=Vosmz}_WlE*kfzaWnx@1#bMcal$2&yY`(&ruV|nqDSrnoQPe=_qSQQ#(0~yp+0$yp$Y34Iu}RyHowi-O077UCFh{TJ30BhpaV?Q>i7aBdwLNb~L?1K1<#~y-eOgUQ9hqUQC`wwUeij1E{OW0pxMi5b`+kQ0g4=P_mV}fNUjyNnK6;k{nEpBnOkjsTauM<m=Qt@^!LSJDRp(9cir%Ye&=h<S)n()F^TU`3yCNe1@Dry+BSNUv?_rzckkNt0SzhBdo21th*msdq>!B8+9Xj8+jddF?k*N8|rxSH)Jc-jcg^ir&cAmC%;N{NZ?n=+VfD;tK@w0P3j@?P4YSFM)EoGUg|9JUh*dDMDix`LaHx$A$cZs5P2p!h}w@FM4mw%NS;AnL>)z5MBYlBLf%S_p{^yzknd8H$al%w^H9@2$y(ER236b3X0U0zpSqL0pL~{jntYa=L_J47$688a&0S@EU8S$_&+52;sO>m4-oRa)aIEQT2L6=CnpP%PW-RU8%KS_}*3O$i4K%QJULf^HshlhGSksFVSUcw;<6Y!u$LVY5xl{WX_(vXV8fM^&Jl1ptc?Dy+lP~gE|LhB@580jZT2MbCYuBt@`ybRU<Q6>Fow|bj5#zO>`WRw{@$)c#rg5&?3e~oc8fD;*oN%n^-%>e$z++7xNnq`qM~wG~pXKr#FMh7^Fdj$oykXQh13%)irYFf><bBjfWG|lAjN013aXi*^zJX8jSku|$W@InwN%DLi51{rXH)Fg8)JEi7UV9<+BXR?t+l)G!+=%fSQ2QEU&gbXz`I*KAYP+YlgVX~CZsCMuO&?3;+>*zdmPugkoHE8M<7Wl*weyBh2OIb?k2O7Q;4&U-dWJlNe2`j39>VilQCk}LG><i%Yv40H*7PfKEAkNP8S-2n_osT2TQS}{R13L)*M5)Mg8UB8ZAJZxY+<~2sGf$HbNTsPex~s&YP^@!mLfqfN#)#=$C}nPum_Jdtxwj@(fAd59%Rke&YMo1YGCcWsni=%IoId0rWq1gJ12v=W$?2U`r3ITson;@!DCH#8aRW;n(iTwBu}SikazNU5_K|pB;$EdKO?`wYk!H_Q)iw#lDdcd8RL0SCmUk!<mWs2nZ`raSpC&jh5Ae?XB&?-9c|zRJl52YT!lQ8x`14T=Os(fL<4K*B~sroupf^#bs=l#xG<gzKdVAtJ8wTV!ob>j5!8oLIlJ&!(<c&GJLd^=d&19>`I&Zng?f#=pYfJcmyw6^+WS*&<mEhfKlKTD8RIRdUNgje$j=}0GmTfNu~w>W1$8-jirOZrEs**pxv$!KtL<~@XXLll_Lkb-r2dQin>xm?YWs;=M9xuLw%Tq}Z;{WdEkSJxHI}?vZM)RAow|+ut=hiR>WDgz+)HiU)YggWM*diBpQz21+Me85ZQAcOJ5W24m#A&2+P<cKL;gy=wz+DX=LDY3<Kb!>qPD@*f#jxYdrxhRs21|?YOMdN?H6h(IZJJsYD=f4kx!}ZgxZc$e;{vB+h(<`r>-M^uD0H4>rU-TZmzZu)YgRh9{JyD(|$Gk7WHkii`wd`?G0*8aurGYC9k@NP+un3Qd@1cRi#!Vw^ds^wS7o!L-tqOc(skC`jMxra}=buIn<ft0cz`~HZSTR^1s#AKy8hw?~os;vHqjBVznJn+xKdVrXC}&QQJzjZJ>sdN2qPM+Qv{vlV!Dis<xig9^}Sqdsl7mQ=5{jtF4CG>QL*FwSQ`gQYET0xw6_`QQK?O*UA4<+nZ{uuQty<PA}DY`TzA_eU<;y_6^DOAAeOm)BJ0D<C&AxSkHfn@7c#$%S*k<FNud(k@jXR{SQ8>Oo#'

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
