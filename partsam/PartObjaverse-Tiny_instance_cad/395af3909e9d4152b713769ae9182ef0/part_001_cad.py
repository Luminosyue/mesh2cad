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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_001.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_001.stl', 'source_sha256': '611a40126710076010240e62dc6ff0101e78ea7ee8fda4c605cf734ef434d1c7', 'input_faces': 960, 'input_vertices': 542, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19870829582214355, -0.2037566602230072, -0.28937605023384094], [0.08868489414453506, 0.30424684286117554, -0.009268596768379211]]}
GEOMETRY_BASE85 = 'c$}r31#lEu^zJ(Z776ao;4CD;9g+bSSZoRI%is<nBsj|~!3pj@ctWrQ*9;H{S)9dna9?!M1zyhizWFo5%d2|z9#yBl-<+I2ef##czTI0J(7-ckW&{878&_t86$~hA7-Ff7%*NnuLBYMcbQ|Q`KX90bkzW1s&#AM2Ytbm6jfXMV7*Vuqw?SQkidHcdt=7F#QEyYx?gN5?gF5x^I3TENH}Ti$)OS#~1plC(odUZh{4Q3$Tp4du*`K{lqfGyg|58aA>I{gFNf3MN(Ve1>bzM$~TD$d8zvEP+gQDhD1=Vjk*hBrsp<PGyxGQ&$t3OFo^;=slj8lJG_{}?-z&{{vm;SDD;xCQQT}%CzXJMM(K69}8?Th@~@|*6iJE_N8{NTTz8}WtzR=-iCI`XGWqUE>r{HlJ-m~tq;X@}-9KQ`gK^@_Wd)8VrU`4{DP_nQi7ypi$#G4=m(QPm!V>oV25qrZ)_Pj;*S<F6>+mst26=d_%T*EjUH<7Uh;x9fV^?zA4~8RMQmW-7`PeL#QPs(!ZXael!XZyvv2{g&P%c4*!iVeo(4;g-jERT=d;Z6o5%^P}~5iK==Z9UCK$xn8evsHx_$2CqXoT5ZvC+O`Ct9NQNnZ}s^aZ`(5jzc<ZQHK#tjRj;dLEb6)B7##Osbd<)`*`wEGA6LiydIuNN^E&ocMmZN0*{=RqowPnppDVb<+gh$beR>pCHI2!<SM~B!Eth#_F652QtmSarzNh!gS|=mQY0j$UG36<*=e4x?80Q*qz10Kl>f?L$TifP1q{sR7L0oG1?HzvB`ZpJ}p3%7auMxlNf!;62&JpUjrGD*}-?F$f&U5&AoNIe9`wr1~bK_@-A9{Md#%;=oez)pcoa_CvEeh0lhvN!<HyO22|Nd~V<~P4QhWx?dn%}be3Hod0IOKUAAFgqW2cx}t$DscHoCR(D634}dBfkA|t!GEQHpp9o<p^Ajc9^#i?#Ip<>bErQv_<2d4oAOwJH@>oE?+;T$G5e{x!zy%t0t(=m80C^&9N`gKH3dH{JY9}U+mdWYB{Z&d%5Lt?EV?Qk9S8N@6PM=eD`nYc`eI-$92xxxdqqv8|wdgdGvq3)u^wBX4J!UANX%gM_yAM^y32F$R9F5#~*vmWvG{V#SwQR|30mUjPV+8<nThCCS|ohnpU<)KPveK*O4Ke)~6+1k+Yhw(nIvaudUGz+myn2AKr%ExuxyRmZ_-5TQA=_>RJz`m~n_JcKN7VeTL>l`@DMQsB1g4e?%Um%u)OvK54D$+}s*(bUf^q$Chd_uHSm_sB8PQ$K=yI<`sM4_cdYs@0nZwZrZUK*Y&3##*J@x;LnPBx6H7iTwUiM(c}6q!S7vRXn&WMsNZ^ZklXc|cYi?piRg*z{xA>i@X>RWzhp=Bw}!)K>hJrfFg_${3ID(g$W!f(=C?;SM4r$*+cfR~+Mg*&UBsKV%+u>IZ`1lP9j@bE&kvHJyxwI{ey`M%)gS&u`?XQv1Fp|A*?!IQ@)>@|K36p=4_l(`rR{o*hn?;nam{bN5ruYJ_~sGxD}TLTmjAY+9+v)vJiT*=YMlME_IJ~>c(**JuYo9E=e_WAd~>vl!hM{%8ueYcs?K+oVI6S&6PF=A&ophHwo8>z{^z)F&hgMRa=YenYzsc(+TM%<yV2ej^*rL*evBMj(4Nihaa{u&uh9Gfc8mi@0@UxQJ5c8ftKTV<C;AuU-?I?EL&wJI--q}gaqaI$R1osN^h11xe3Sj9oR(&258?3JLMGsT$4%5c#)h(p_nk6I<Hmo+cw#CEfArlklE=QNEAD@v5=Y$HXO1!G*PpV(zdy?iJ@2j>+8*pxQy|ZobBMomNzZHF`c2ig=j%%S`^%0PH=^#LToqn~NFLka5m@)EiN$qa9WqPv7b%KyKK^j5TfZ(^4)<mHo><rRU?1v>`yRUjdHz_nT6LfY%C%%U;>Sm6yEV)mwcMuQ#cp{lL8Ea0(gdTNE7uO!Jdt-W?@#HgezRYxJ?bz0824#d55(`<8zAL(<Xnq&fOmWKJJ&x(eC~6qf7C^MwhOZ*-jd-9+WDKx>USjBqVe|p953QapqyEEXuGxgOhf(V%@5_e%d$NGIke}zsE7DdYb3w1{1VoOaamFR$MLJRp5L)Qt%u*RSzGDvDh;rHiT`$3{RbDU)$58|fc946mHM6Q6XVMTw37@E4!iajYg7>}kG06n!>;|sd_9-?ZA-7I-`;E2D#>s5ZiIFAmgC5u|Ao$jM#v!avwpG2-?dht9ybl^68oY9$YWg@uH|fc3*%3jU5I}*8{^!~efryWYU^Rwc5cKx((;?GL?ch(KQS-<8-wGAhC}zYo1^`u`F`z3){t578%wl*nT9skam@5^Ch~;-zE10TgE!XO8K<h>6n+}#^~;R=@nRhOb-U{Ini@~n@>re+p&oqNt<?S!J_W}`cSrt=9vigY-Us3SF79^NwLRN*O~HNn<9Fm4_I$n8&-TMw9&<oD#E%@0axVF*{n~c4A^f+lX@1M_f_QF9S<5ZIy>~p?W#-DL&qMFf-t1QNJO6Ts&s^YumhVAfjDwTQqC6uaBJ{lPb7S3Q^Ff~D6IbYUjm3J}(Y&zwEpOhU-*t;Y|Mks^dOH`V>ltHxYs`O*Gvd5HV>fF4V9cAAC&_TXGWlVCdDIs7dB%IJSMK|2`7QpX(0{|=x6cmLdaz~diFs_o3&cMj5UJ(#IDzt)e0IpSUpsDF@VwLLA@VHu*Y;_uH4f|kEcCCLWz%}wfc3HQ<^lS7M5RbQ{!JdN!^Yf&pU;oxIbF3MIo>*uXKgjTUh}GCc%J>^7|NNxmfm;!vx+EZk6rMuxvBB?nf)-ouiVCUYIBSa?QWtxyEo&ye5~3|%=K%a9p2o4_$n7s&+*GJKBQWK_$hy5o=si><I$`6@ca2_{oD7h!n~hpD&qM3W%bE`@u5H%;`tnHn$ZK-n}00);qSCQ&6}dIe!LtEfB79cUYVzS!gynAkLw-jy-CX%<fGSXKHnVmS*Sk7jZJ(`462Ph(UbLhZRfLN-h5gM*BhD?d3t=t^G+c%;y*23B7SSTnmF&R3OMiIar*pX3*V1^U8p?b`xKh4`F6g;{C}t%{Lb}8SZ`c!%F-yObG=ceqx$V73L?JmLM^A|VpWXWfw>Uxd~Ur~Oyf-!JRe%mbk=#+8iRSw)FwU3$#KS9AOOz;=hGnGYaZ6WQMJ)OjTESdmm@L$cCL&5cHpbtC+n#uoAf$|f7Rn0#ol5c#6MsY+W7|5f73VWw|zX0b&}_D^yhD{5$_zwP9MQIRt$b?$4OY9M~+9iCf-DR!%y079rH({TrY1R{$^i&9<(NVfb~kFQ`jf+=DN2A=4tDwc;xBbM8_-BlG<4JG~RX4wZB-V1nGQji(jdJ!>h2iH)HB~JWtMAgm{y$-WThMQQCe?o2DSXeqpSut6jr7e`YAknY+n+?T`MaasPiFg7VDsMZML_hJ6WJXZYW&&~d<2a2(bZPut<VeHYEueEsaG|D`RFe@{*wXB_2j^Es^o{9M;ryXM9E{7FfavqDClmmPO7{#aiY!+A#zibi`cr02C9&x1VSGjzRbDw_fAbW={0=fh~NH^;tHsJEZfA^#POXXc=CSbwxmi9ESx>V32n#5`;<ztHuK*=w@yGdRw~V!fB@iTa)6kF8v9tQ$W)#=gdlUvQp`V^Pj_H?U4B8GwDTh(}l#G~2Cy>yiF5wVaE`z<)Rrd4}CY``I4AeWvNy=PKKNvG$h(3*gT>7I|vdU##_D--GAFp2Jbjv;DMPS^nFF=McXT#MjTE^PMf71MyFTkiS#tEVP%m*gyGapxw1!8;|^P-_OwR+z;$G1lQXfe&=}NFhVg7WQO0I*`f2AkuMF#w^4z1*M4W(auxMFy$j;6zti!-h;4xJEn^GBhb%+>(1Pf{51SzVni=zv&kEd^vyD*B#=}w0+XXP5M8a>{dI9UnYt7MqzBNSo7j&JVdCLBReSm-l$g?IB_RXwSunu`rANRL)JjT5PBQW1LE{gbU@3dW+gRzfiet$kjwR8s^PaJoKV!e78e#5uDp4Zf<E7!9d)NgeR({+gbw=TGjvEk}>H0^@@fizi=r&TEO<PMsr?P}C8<nbPZ^L9>-_1o{owf>DIBaq+o!Unz07JQyPG6?>#0oqQC?3FOSZR!R8&-IpRe>uc`kmc~3j|JoY?#F(nxhedPOxbO!Med_Ka|@~8o+?cDe=JAuVLsZPUHz7!FEI~{#dD>#f*14D*Xy+w+>d%FwNcx*^;TIOH|!~gVxP8GB-VdvM-J2Scs0W~vob>c<{c3WRWm%ndSKWR_-ii5IPBLQ?W^(v<go=|TnQY6=bfV!;s0=Dgy!EAg7U8~t$ur+U|pwK`fo=&%v%ik{R?9}T=pxTn{O9{|L(t7Cs!|g3hn-1JU4o!(Ee^~eFf{x|K99JI~=6*sXcBQ{DZIUckM@xka*n3$V138$XB0>?M+HyTrIjp{pQQHFwVS8hWRknY~;_75$n!A-SE6uYdZYSap1N$)=TfZz|V2O+M)~E;mCIIufzKV`<H$gH+nWfdB(TJeo=T8ta}GEhX3*T&3Zi(#^L#B$ge2p&Z8*b=18pL(^p4)iuJhuGp*3CdsaX_Y+0oF?Ou0~=U8#%sW}YordbQ*xtd4)j%W3Cd^R@up`2kU5YKh2`P~f6BTGDSU5}FB@8g%CU(CaABlVwnZfa2t?=K#`!~W*@7202H3$RWwI-FO(+1RGfBj!zb9yc$JL;U5Cj^el8DW&bx{&}hTt+)SOpz-!>7!RjUMV>hmw0~I_9!7h9GXi<~E}5?FWXCz&hXupozw_5X@tgLpf<Hqa^*cTsMElQO7VUFD9rfG&4Xn5P3Sd2xHU;9dwpyj<yM%pCBmGBhPtJ9+(YZ0+7u36pc6R96QY}yAizxrSgYa{`WUp`??Q3cj-dmiyqW94jg7-w$46D>{PW3CEYXY{R-cE+$_<oU?e=C>AI`&3?<gd9J>--wkv7a`rAL8rn)$z?<{hanYd&|x!zqdozMV2l@Q4duMAdl}`+y`Sk%5yFo;!}il*7Nm!jr+bFetYsy*ne9PhVy!)Mfq1O#riqsHJ*RHypZQigK1iC!?4e89s6pJYrnQ0o~3zgHJ+&7s5(dM)3U85%40i-=hf56bwA47cM{r9C%gI`CmO3-UR*<Yd}5I2WraYkhZ<k74y?Xe{pO?@FfTW_ig7q*68!$hb^U2e-v;Abhl$7^KULd<F&FQv%yY(|{8L7vUDd>MuF<g#%IVyPx4%Sr3bsak?+D!Y-y*QDaxwtr99<L7S(QfP`7vc3_)Cw#I(9zaGhHYN|F|Zo?<W_q|KO1i=gpE&`=ev^5tOHAZj?U)zfE_s|K%w26XFl!y`E`fL9A!&pRvz-6Yl}du_Z7sTziReq+1l`k0jWKvQ2x0^<TLV%-5%{V?J7bL;a?USf5xIT*Z2({wd^H*mJ73hh_&b&iEdM|H~U)R~U2O>+`R%$PWLko;tr+>UBkXo)M*fbDM^`&tT1e9?wDlM8ZEPEym5UZ}HsGc@pxB>a$$)=V*)P_krW#zq~>Bo$T5AXgfD@kH&SixvTxc<{gIpw5OfaZ`*6Zd-Kw{@I3X^g7Z$9rSr9Id221dZFNWFH`{~tz6_a*`c6lG^Kv@wS>K`Gna(soo;w$G|H^WqlGdlC3C3~j)*{*tEtfxHT^3sj<s4la?P}#r%#+tD!rwYx>&?{uEB4LSc;md50$6|M-hlnClSy&j^L8!2<z*Sv=jNBXo--9rgZF@aUShwh^;JAKmT!RZY;GI$-*JDd-x~M`<5jX#sGp}N)o;lkjCFftO_XQVU+Oo?=GF1sR=Nx7A@vc&m#d3$Ca?#d@2V_E{!w)nY59xz;5&wyW7KaCOo!+0hC@;RPk%@L-lj>KFK`v!KgP7ebv50l?bh64G4^>r)j<BR54!(gu{^?kk1`{_bG-Uo3GWeB!f$<4N9)<VJ_`Hae(;+%N9(?mY5!`xcYaq5<q0k^RQq+|`sk;JD`4H+;HtjwFz%d2{TwWf^G-Z~@%hzuj9V+c;a`Vw%eJ^UzTfDd2laMiud40JEX<pif5LhH{igfjw(f_qZa2ekAC(@@?@j0My@*5Gx3%wiU5{BZWk-1i#bdwh)JC)y|6cg+BGZ2O`&`oJS#y^y7{~5yQNQi#A1IISGOW*MtV8^+KDsV4e0E`dIBfymr_M;D&ufmH2QUwYO+tBc?9%&gPZ5jvCfmlKA6h%;I>DCw2=32ZE4~Z)(n;q>bKp+A7ib-VJmX94L%TkJ@#^kC_&)|>JRdp&_c6R1${7`i_*0&GUenjki03$O37d*_X%hGykzcXSziMFp@H7DXs=lvLZvmW7PgF#nJ0bJc|2z)Yb+#<x%SP#YC0l{CXy=W~pgaXRzK49!@!V9h6!JXVtnUrYh2ybLJM=TYSJ=mO%I<cU*ZzHv_b6%KV?H?@f%>oU67Nfr&&If%cMq<s=`-Z%!uPsS+wndo;sN46;d=vHPCNR=u?xum74P$n@GY2k>aT)7RT8wThqp2QR9c4o8(ZS}qxuc>$H9x$Zw<bWad=O9%=^BR@Sd_Y_U-KXYU8}w{19Jb0N$$xZpVJnTOX8jXHGm<y>End@2_{ayY_1%dkp%^;%N0d*9ngFQ!yW&AE16?>}Tw^bm4a@HR5&rb-qWozxoODe&{~+8>!oByd~O({OecaIiVER|F&f*kpI0I{sl3p&x&U;e+Bqs-S0OQ>&yKma9_eI!oPF{*1KV);J;TKd9vd>3&*SDc(3X4O2<3<Z`hBw+UB8MU3<CJwH_=bi{t&v*yHLqrm!9+?nS%!JQ~ldbtj-6{7+%ttd<OUI{btE)VjGbk8j4f;3&LN{f=a{Fb>=eSHGnm-+OlGjQYv32K!<oujBsah{pFzqo!hf;d7I5u^HAEO-Dw%mEY$Z)(IawtKa$DXESHQdZ}zi_yhN0J#!P^jhGBC<o}QFe}5W{@<e*V-wxj+I6Ol!A1(Y(#}~&;JpWkE7sCB{FbCrf_eCu;!nD0Pd?v!b0OheCoPcrnM9nDlH|)dMe@%t){P)aQ-{;4BF5A_H*k_*Y0e@^9-s@~Sfp!=%K=%!u-@loXMWdb~dtg5?E)@0U6N2$4u$%gA=NF^>r5J(x*s{YG*ZylQgYU`AuX7@v`^>hY*at8#NvD42evvJGH;lv2$76iI1-~&m4d#WZcXVIdRvOP~=EZ05Jk{@t`km`cYvy*y)Aal%*Ya3u9Y=iG{ce8S(3Xf_Rss17Y~Z>-E6$rIulk+)?WUp`Fy7`_Hb-@~&)@#y-xh@N!oRkg-&Skc&cyttv5hcZe7ZN=&Hv{3uEhN2=EX2xd^k7D)$geJW_MzKQ^Cwwr@XVzboJY3<=mT?-}?F++J`Oa47c*%#k}{U-(*Ry@wT}$!rbzdtGhojzx`xd-0$0t32y$i)ej`*cLW7$y_<YWhq|4&a)p@0{N~AVx^HK1=QYCBZxl^pPt0%bFhJK?*5L93)!*c|b6S31?2A}O`3!K2uhH9{sJ~=3-4{13DQdf&_vB8Tch<eG{x12AkN7_CfBeqtZJq33Vt!*v9({l1C_iJUtKVFt{K3Th_Ss|c9(!9CtNw1k@T_WIzL(6<D%3UJ>e>BZVt(_Ir}*w8|B6tz^1uIr`8oTR$*%FX*C7WJ^IMng(mal-NwL4*<K7wl`{rt=T>Z{+TL1Dn?&jxtE%);tbMrgv?e@5XiTSOa{&YL9J#Hxc%|>C}kRfVLV&(tQ?<~J1tkQzS>cLW?<$}cO^GCn4KFzf*ElljbSU-d;cC8=toz(cwVeO5@iQV@f{m%Pt&EIW#V(smJ{6Dm}AN|huX8GKFg=;yDZ`b~E^Z(G!&CzdGx|ZKacKxKQ|HppxzxmmZOw~)QaxK5JKmO=9dVe0H?X!00)o$f+_V*wB&i?LrFmsJt{om(zwpY%qagBG5Ge7#B<BX%6ZLMp0>|L_PCFVCu7RR`j@#9*z`^9nZN56C2vwtfT?$)k2uKwtEj;r?Ko)K>CndA14e&@Jtj6WCQS`Vh{PvYJD&iYS11n<RC-gnF6oJW52JLeHgs{ZTUu8Z^3kACMoW$}9N?&m!Cqu)6XI))XDbh}>8vp@Qs^Q^J7nY*9!wWXlPM%U{#ueo?6F~6~Mq|UFV5vMo1`b{4A-tI@g@us0ZpIOs2igNRJC>oonzjPjb4zu?k6z!JZ3-9TE^qc$T*5`iH+xc7F?pJ)CLy7s#HH+&$sHsoTHaGv3|LlqSPoKa%a;M>TSHI)c?wG{<*4%xxf7w%<ck>&wf8U>|zu;6|=Q&!m+2MA*&6Dj-%<l-s`$_w<32uIS<_)_N^Bd)}V1FykHuv}oO?Siuxc%2S4U_H&w))5t*Dz8VnT_t9T>euWamqiZCjOt|^eXp%^`GKYu2Aa#_dmsX>5(w?B-mq`@ITa4Nx=V*UsF?)#f1N*rX`CBf25`-iwS?GW+aOVf1ze3iwS$smzC^6_M~Pfdy<n;bCQ#hlT&k(lao_W^N>@Jf1>6h|3pqo%|T8|PD0H_PC_=QS;z+YKM!aovY7BEY6h~H@CRx-vY7B&Y8tYb@GGhpSxopjH6>Y0_$l?92Utw_5%nGU5&1q%_yzSVS@aG01^Ef}8Cmom`3d<h^)gxX3i&SiD)k&$^aA-R`5I05BK0KsBKdD>JX!P%`5N^G^$c0`6j}5HS@bWmXdGGe2wC(nS@a-TG=?m?pDenUEV`R4x|1xrgDkp>EV_p*x{oY+fGlb!iyk72#*#&kl0}b^MURt3Pm@K@l10yxMK6&>uaiY@kwx#2MIVqwACpD@A&b5yi~dU%{YV!5Ocwn@7L{@22Gx`7$?-xs8OI3W<Qx}-Q?SnqCuKhuPQtz|Y_LxYi+&=Dejtm!C5yfyi#{idJ|&AjBHtk2rrsxuz98QwKcqe(i{2$aBs-{A$)eZD4)RUv4e|}1<0kbX*+G@xVF}hJ!RAxTljoC{Q&W+blh;t68sIhLwba98G2zwJ8DufxWz_y;G2waC7GyEuDb(M{qBY54!kww5$zsB#sD;R4!pW(5$zsCy=rfV;kz=SO$uZ<Gsy{i5+=tqfTs$Fv!34`i6V6T+O-2*;B#XW?V8Z{BMQ_rC?~_GO(}d5HMGw-1kCH_<(1dr8Mb}U_k=Kxy(u5<)qO)njE6Ji$X~K)iqEl$Xi^!tWX~HYWqVs9OYssRkXu=!GqFZRf`xER4fB!|@Pu|ZM;d6|;Nd1fa7h^6`*OKq@n1|Gh<co}XNL@jG!(-l4ACez3<~?;0IjIMZNkV;3e$N=;MXW>N93D6(3pEK@RARDFSCWhHm;%%+WKoGJK#e3v^1cgK;PJlH0%TE%@ult{|H@;kQhmvy5>u6Wl-!cX)S*@-i%Lu#>Ur|-JmxoQ9kQsz{6@V`?!seQP=6zfN=ystzvNClra83*xdr=WbE+r(9e7NAYIAaP_Uro8?BoC*<43JeuFn`hYC&=}9#fj?NA_b(X~u{arxqk9O(<us1j|nKC5sj#XD4T-79nRQ=b#oR=OE{!m6vux6Rt|FM;7f!u1ao69YJnM4x&bogUB|T@EPg_vglj#8S<+H^GUe=MhRAyCfu6Zi`<$VLLE*HAy1$QTN7+>g7rwShO|NnR)U(6T!NgHCj8NWzBIsM!dI!6$ydpTsCM!!>RhUwJeNE#!S+$lQtjlk<j2&@<j3UC)R*MX<g_fWlshd=xG=R4xiGmpwIR77>#90UxD|B>xfQu5bu_srxgXU^?nfR#9ZnuV?oI7Q?oDn_ZA5NQu0{1B*CH3AW+WFQr=v>yN=JQ578B0x0Tcepzh5AKCEub6M^hun5$preG~r3qj^s(?-qd>J-sEO9;TqKP<Qn91)O=*o;^cDV#x&vj)FR~i<VMtD<VNHsR9|uva(kL^6>2VW6|!v4<e{da<|2zGC8r@LqX~P^gbiwTvZ!;b$RMYn<{+maXQbvMixwbfBp0L!SEp7bi?$?JC%2&nk=u|5Q*GqI<n=V+<J2=`(O2Z-<bSBrM*rb&;mmBeK4c$`iJ57_MQOrqsIAFu$P=j{<cZ|z)CuJ2<OMY0NmMJ@%Dz2`COnxsgglu%p4x*fI+#43ypSe5mnPhn+K?<-g4~u|iJFyMiJXrn{LO&M*!_(re1m$Ge1jZIJw$en<FPd1bu{4+ns7hrTyj5hAax!&kQ{7$p96wv!pjqEEA<3*ANd6NI`u61I{5?jG5G^Ig$MLASxh)TRpyEOG~tTW!sLqND%9#^(N^Rt<Yv^K<Yr_GwIA6+?oS;+?oSS;_9h3D1F7xFf#j~#TI8<eCe&i&Cgd{IbY#)o<T7M$ns834%m+F7Tlk9sy+!^)enJyIMvW$mP9h&8hf{l#!^z{R&B#lr1E|f&1IV4JHOQUG&8g+cqK(PT$=zte7HWO6h1`YOi2Mh&C$$k-v<bN<c_6htc_4WhO}GcO3b_ZlHr0n*n_S8GKKE3j34144g#;@j?VRdO_GV0ens8cb8nS3Ia$0g$ns7?02RS9#xn(W<6HPcd)ga5i6y)UO4AhKd(Sqa*<igbI<icb#wGG)!Zc80ZZc83XT~8iK-j-l@sF$eg$)d-}qW_RDk>vtKWquMCElM`XHE6=2)HdW$@@(ovvgma3Z1PI#0`f|7Bu#h`brM;0GI<es33WVKbRl^Oc^geQiaM7ZMUJ2ePo=gci&i2}B@d(KBhRFcp$XTc<|Ef5o2W9MnfP1ylL5U!{zU$p8cP;kNB*0<hbBCR8bbb^+L{_d7VSrFO%9+2k^{)CsKMk`<POy3<PPM~#`n2!G);Ixf<;l|sawhM<SWz@<SXPC)a&FIWDgJM2eO!OUaHKOd1=DssQJm|$c?EL$&JZPsa43L&B#s3-KiFGck&==fAS#mAJky-IO+&$Fj+K^Jc2xs+Latc?MUrP7HvZANNzwaLl*TWHz3!g3I9yZN&cCfjVkkHHvSg=&wxH5|3`jK6Fx;fMivbxpCa#~jwd_k&RsO&IGXTgn(#R40P-~IAnE|JXlL>uaxZFgvS>GQFY<7j@DQqnJcK-y+J)?#YlUT>_D|#czOL{D>QM4f#!q03sB?c<cqa7^@=Wq%YEQE0K=M+?Irp4}7g8sa7n0{t2a-jHk=HQJxxX#EnmUKPn!JoUjJ%9&rS>3O$$hD{$$iNUsg=kL$-hv&$-j^*Q_GMmldI8$>rg9@>yYajcn>1)Mf|7@$bRIC)Vk!lJXW|Sk1tF0BbOzYpjIT8ApcCQKo-qU7EMbQ%}V~6EICT^+_|Y`$+^kds3piHcx*OmN^)r)Q-~&<i6-nt%|_0~W4)+J$a#5uYHB8OYO*KQi|oZ?J*hvDP0W>^nwp%RoQmp6_T;g`C3$>KYI<@`au#YTaw;C1g(jSinw%_}fh<~>oQ|A@=aqB#(}YXWgo{$MkhAdEqEs`vDUbh^T8jKDxfZo3xhRhn?!)7|Qhz0PCAXv2BG=-v?Wk?Zq9e&+%o|GWO76<Phth;cQAd(Rw~=F*YbQ079Lm4%qzP}QZX-L_xWf0C%R${qc93sVx0AQ?*xNi-;+*d&g}ppr!l|jZ$+vl|u$XWf>Ls$Mtd)gDYmiIv9F?hFWH08bOcOR!(~#3JkC}NS&iNizcqr9O9!ma`T7xVaO76@!=X+k^Y1BW-)5x=^p=8n7<SC4EzEc)nOr1quOkP2qO%`2Ap2s-nJ8R)})D`4)<n`2*WYI|SGR8UIi3@L}t|xCKM^huo(c~@EMP$(>WYKNp)y(C5FE6~A8cp6z-cH>@-oiZFsZr#$JjVGAfbb^jcJe0jR%#SkG=jW_an5fHgu|&@$>HP;)Clr&{>}N_g78x62J%w!Dw?p38bKDFN){bPc0MoJXfv5(KJ$jrglAA!k!O(SP-l|E__sbZ;Zf8%<Wc0Y)R|<_G34?*-k&;(>`(rMI+i?^$NoYSu1T#&7B!Jm@f_)?{^a!JOw?b<zwo$BG~o<X6IoQA6@}$n5jn>*YI?Gm@FQv_vY7A#Y6fx!<`fqFn=HDA{D3Su<XaRu_W|lN@&WQ*>Lc<a9=n%1hCGA0CQ=WOCz8if_mcPW*s;d<XI<g`%+;Mbk=&i!i8_`%md6UW;PDNp-N_Beb*Y`mb;)(8zZ>7zlfu=gt;wPR#`m?TaAj&M<NJD5_!nvi<NNwnxFL14@qIlk+?Tq*_`ZG?wi@4`y{$B1S&z#aUe@aeX~Mgy%gD<Zznd|l&hKG_Pg0}EqVeR@ROfd!!q=$rWYH_+n^fobIl`~0SID9-$nU7m?|g)RqP`%D%D%u)j1hHyFC?6Y>OmIGOU^|tP7^Lk%}W+7M;2{NE>5jR6Ru5dOb+1R+EHth+mX9b8<Rzwl100dJ1|#YYCCdY@<{PF@JN!`^Z)d}QuzK)-W3^c|6_$8k97a++x5t43Az5~Bk+I*$z<)Eu%J((50UkxhZz407(r-<'

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
