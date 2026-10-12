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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/36793e98c89f41c186617d4581598ec4/part_006.stl', 'relative_path': '36793e98c89f41c186617d4581598ec4/part_006.stl', 'source_sha256': 'd0b6e9998662cbd3a0a319a1866c51b0cd9f0055033ba40b9ffd42e0d1995819', 'input_faces': 728, 'input_vertices': 431, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.138555109500885, 0.0497402548789978, -0.03143147751688957], [0.15654760599136353, 0.2611251473426819, 0.24220749735832214]]}
GEOMETRY_BASE85 = 'c$}qN2XGa~mK|X-!eDX~k7Qw!lL3()HaX{vkpv=Vfj|h%kP%VjAi@(lXA49eFg7NG3E##x7AAwq854HyJ?Hs9&EKus+Evx9d+wRjclz~o_w@8kscD0cl4mjSm*1G&>DLFhix`HOzmdg=2pcrGXP2<>68#25`WYFOmp`wc-MCewrtSQU2qP-6Ygl-fL4iT8z$)D;1{QM#cI!WA@Su=>o%;{!8YX=0kUrsIHXq(2WI&i57b#b^bTL=i&x*N5y8e%UY3(YQ#r7RKDBk+~hw9>62gXQjWsO(fNPYLP@J4*iiORp<0)9*T@07P5MJV5T75G0QG>`GukntKftb+U<V=d)_=a$m*)XfQf`%K{ddqt|Q_dZMcZM{&R--plF*qRQ0R}jwIY~vg~@AKi{FYel>e4)t^>KBD7Z|>}K1oas+RATqoj?g!(c2xP^5o0x8UjY1}l*g5SbbNy9M`S~u*}ol9-gx!qfbjcMKwo?GUg%2)OYFI_<e>6VQ74uE@!B|v6OYbU-dxoSzc*i;wzDfmSLjppJE(laA0ovES11mC{*VOa*G?TR-gEE50p$zS#P1E5KS{i+N8EnppPbpReDNv^HP87-@Z%fl?{!zNvQ+EYs;%;7mtRrO2cx63KJ{BcziJ)YA^$s5;^4APpr2L!N9DK1DxYYTf`0dByOsB(4N`vH=g{{&^F8<-+Wwx#nZPeCgm(Dk<#hdB75tH>L>>IDZy!YKdF!0qr}`%2aosa6uc`TCmnv_Jo{j7BTf*?_KD@cEr(Sof=+h;dXTr(7Xoq;!n}ZrH*YiGJ3I6x$r!<cn`CW%HfX~qQgz`liwbwZRjXj$G-Z{-<jSY#_{NJBc-UwTa@iI7mzPA6xso?8YIi`Hm$?a5MDIfT0#nBIgJ!Q3CV;&?Z-)l2|@5^@4`nxim1%I_B+A|<ATz$J`;N7{<PcDttejA)+8u%$=wH?gCmDXuL$@R@{t^YKC<T)}gPTS!?nDR!SXzhpYuw^>#T+`3)Qa(>tT=z9!j8lD?-O8KoGUzxBK9=31*X8~y=skOp|8(R$J^tk|@WxHd4|g(5)AKah60dn`y~23k^<s_cdkq4gsu9{P>$5q^zs;z;@l9X!=cUQD{;tcZpubm6>uDZcr~TiY`}|wwXIw^mmOrfh-^@5&c_TKT>a9xacW68B90L7?J2>yKv`h5&{#qIOb8pZ;bDWzkv9<cnPUSo1gZ`_(Jep_5HRa9eW6*BNwr^HnwHEa6uA!doqgU(iTALU8otwd5si*TwaQKNGs;}_5_AB$w(?zOVH3xk3Og*plytB50m9a1Qz3ow-PtL__J7tR7uH`~cfZv|5U48Tj<&6Rn$8bHuR%)K`_1jd>`Or++U+eFBQ%iYc%YNj!UFm=x&tz`Jc>e_R#*DXXeR<>B5aj86Ui+!_KF1c-mwBwbHRsy5>OalAS^20=n77{_(EErLmU)xrd0t4zqx(ZG)PKvL8&#kCINI$=y7}lw9hEn36vlY}Zj#QoUf%R%#JKx1&rogWz7;np|2DbiH$UIFNw0guF6%W<NCd89Xq5JAbAV@^>TCDI@7?pYUdO~Nlax2+-NEmQh_}!mT+j#g!|y89T<62!Zs*o2U+-J(|5lGbwO*d%U6eO2yV1@=zm3)NW-bf9rbp{(ow>3P{UkN=#5Be4>f9aU^uwIhsvnq1=Xo<>p3c+Oy%#H$?^#B9cl%L0wVn-5DsR4v(|Woax%GDhryB}BZ!G59g<Gd<{c~(yp?u$mm?uNWZdHAo&C8YFQ6BA?;%Ds-i8aHNH_ALiI}E-RCb2u}UYzO^|3W|fJ-Ln}_mMr|58c4;>Jc_o^PQ@-O!?$D(EhInV7^~gNqM9DB#etKhcVx5D~@sB`i|DeGyM}CPws#qy+0TS4r_ih+XubQ?wemPR{ev8XrJ6|aew|b2;=YSTkwTq_9%aJ@dC}$C0hH3mA@c<ce~09P|uWle=!d~)P8QxID~ag`Wm=j6kRz(+w=6Hd8*&N3HRmj1>5vI+t<xi{hq7Ho8VcmzQ}m++2&)uHIFos*mLowu8+)W)6oyR9MbtAvEgCxi^gNTYzm#Jeo6c+&C{bW=E>u?_54<i1icTNU9W0CcBe^uTK&~H9hc^3Ls6e&r7$jv4#c`|eqN0C<`I~u=a1BNka;&k^9G+jiQk=KGS*+$T4EmVv`DX;d2;g@<sTQ&c5}UJrsuaF-y4nV^%Lfu-Ln>I-cGM{J!1SiS9$kQ6ZL#FPkHn32+d<Xnx*rqIcMiL$dd~F<KANQ-`Sl<CeaUAt@Ee3bMXk}OKe5G19R(q;{JKuaLrRM2d?kbK%JM&9ZQC(-en-ax#W{1d>%Kh@66R3l<yg-^MRTBp0=C2@=;x%7~AWDA9DlOYgp;o%1`nito)$qxL(<6;QZ6OhiZM!e~I-;@<yjI&O+)af2^UlkCFKo<%5^?8H4)u*Lm4}wxo`qfB0Cp>a7pYlj?8h*YRNamtN$nH-|UEe0#Y|QhmK&aR1s?Jtj&1mTR^C=D>EReD&tKLTESF#xIiOsZ$Jm&jTlt@b5>WebW4REJ>c>DbSyepP8LRzrP;ZIqUkPN%+*MF|S7DS&<}9lNC7M{O;c;(WmKzd3De84N3SZaTq@_#&=2hy<h0>bmwofJxTuY^_5R7@Qsy3|HCrq^IV8e!k=4?_3G81v_B_q2t>bdTwinIUGVLP=sabuG0y0Cnwg;MDQ7=%AMTI)r=wq4C#o%|{@?UN>vetbj(+R*p99{}|6M^I@Q(f;d@;SQ*NpG7B^gJ-r)Fav=N)%^K6Q;d0^T`JkK|mWI>)#U&c1t55<TYu*Xi5PJLU~fiX(cz{g3%4uJmH%9rKmZdxP@M`OQ_nu&y7S^I>94Rpp)Yr>kG9Wg0u?+u)@$F&{YQXCq?1_EYD4ZtPtL-ZB3NUw^d%*EQ+=!YYzZ*L}|Wi@U;n<(>DV;OyB~Y3#gzWp1y$^M2>qF%Eji{n2%yovxdl_fzX|m_7$M@4x1dU)JFII_}p+8ezTZxW8NZ&MWU+4|u-#1$xK&!N~F$_f^Mw!}Vt%=4r?J#F`VU{C})x)?A0)vHmf7T;Hg%W4&Yy+M(-B=laTwO{VK^=X%W3yeyt49P78>CMUKi?^y2{eV6Nboa;kt+fJO{v7R(@oCWV#e|m1F)a&nDuO{{{3f{54b(iU^ymLKl_U;G0WBu&j^#k<9|IqWgI%GkAKYbFsV;yev3c~&NLx1SbH9wYwcdX~FvB&V-;CL=DW}JlH@myfuy$=1cyt~w&@zeE_dz8OEFFKz)f^P;Y?|e>4yxI$VXlATCGbEtj?p=vIj^`a?*DdJNmWCfYX{PY5M=zkyn}B|pr;d(i_nJVx{?6wq_t$NAV%*il?;4i!Yt=Pg06m{Kjj-FZwEjW4wVd~P&1iX6*9D2S0<dm%Jl`4jr-Q$L74^S<0rSA8OTj0kKz<kYRov4Oz?W}_>lDx)>-?1mao*#(z;8?+qrSjZ@XqJW;@6QU66+0Xd3{|62Vc*E`@pOESdSWmu&)qX3%uib*4p0~e8nT^4=WF<-u1GR@<y|Gt-tHkP(7a5DH8g0O|Y(gaSQ90v-6=(Ui>@$9_))u{1N&WPf-7@<#axApS%oy<aDf0(yqh(<6plcPp(qXx4rVU{4R4}F7!XgbGj?2it_*QT;J?V=ttzheX!ccx?kbRwGa9kRdF2)9M=12V*X^9Cw|I}c`3Gr?mM|^rUUQTPw@O)2E2Fw;YzzW^vhb{hb}?>LOFFkYOU@G-m#D2I=g$fZ$I?zd$?{L0RO5E#&7agSeIlufjq~)*Y>xH<<jx!>6!@Mv9IEZx(WV$Mbu}?+NJ7SxwK!K;|F5ic>5a9k6SB(k4?aM>GBl&VI8|+e~tHd<4oQOTF>x4;LrT6<%3%lgrAFjTl0K4?l<9$@w<0@1KzPO<i0!+c^vylp2d5i|Enh2;eL$H!`8*);5(H>eG;GP{&V8TmyyT0PgUh6^wu=!lWoxTU*goip-&xve&<@P`~1f58TCHw+y^tBWyACCoet<{`xfcGz2~c9;2ryEp4l~!r{@OrbM`~me%$As`*KFI72qBFc&<Vlk^fciB>R5Bo%ZhW{axmW@w&dW*EQhlj)vZi{_0wO3VF6>I^o;@-D&PXfAR*_)w?h1e!I0KBc2x>`;duMD}(QOANn5)>$=NTuNwG_tM$6OoA1}_;2K&V{PUFhd#&pg;m0%r@7VuL+}jcF71|#~{^Vu!`nu=N1Mgi&HJyxg>EY$b^A+yn=F>TN&N{sce1!(s2X0mi{V-rJ^868w{?PN5?$dhO9EX127R;0JrS-nx`s*?HhYwJn$O+hw9g+>}h2hte?CTm^3WIMp7wu5Iw5}&SS!<wQI`)Un_AQ`y>?eChbcFtJ1$}NYUNneO-JyQq9sAOWc_xA{T^9PVj8oL#!*wuH1mX9_)Q>^GI+axa=%)_a4=bNXeX_noJCB%z`(=+mpl@*t?NBll&z1A;K_4Fpe*K%tI_@5Sg!eIyef7i|Il;flih1clN>j@>%A>q<f8K~HvfsBI%mb}s&<{I8|1>+EH;Uta_z$1GH1e#!gn97F1m)dn1I}t3baaU73M_=aRCe%VUt|BU=5p}w@O*8hj>kS)^iI_0w=$SFvpmK=<Sq;RC71SZ*WlvlpP7CEfA0j^ryJMR{T?HKYyq4%v06iIx0pB3=e>+^+AG;e^*cVo{l7qZT(4ElbYIEK8>fT7UmP$)e`l2<;2rNlyu5WNH_qE^klydyQ>#Mne4p~PE%;*Xq3^p*ua{M!H~0=;C3!Dn&K?VX@fpmMb@SqV&H8BYts{`9{TAh|Z>NHHy!Y{3TL3=8ZS<2`{`$Vj9kK_!<Nc9)+nEDNuHzHF*GqpJ{OvPXpF~FMc>ISiTng>BzP!Fq^b~vm{>ez>F_^#PW1M%zJY2`^BcgnHclyE5U+%8^6z<wDq2Kcc&lBlaMEmkqa~Je~X2g50w}IGab-XW2oY@4=e;YDlKjhVIUGKRsg+RYF66-`GTQfa=zdLxx`?$ncy^!apcbEq!O~G^1r$eDnh(moIywq`F)H9)Xyzg`O#&|aCheQ8kodG&7o^3)N$9qFhwq4MNL_%Nhn6^)Ffj!Xo&4zmJ!SkA@_<roKz0U=GzpXkR%?`(q=kx{a?<6+B^Goza@HMmHI!?N)??XL@uOm;vO~_MsNIUhekMJBeFeUhbF74;WADJ;;Yc~ZS&{OwAEq@o@*LJCq<UOf7M?vgU<X8{=822#!UCqjXAJHHD(PJ1d9m^w+<2|gGx9%>1e&uki8^bF@U*;0}Pr8=6{&A10hWh9H1p2M$hsL|k&_|@fbJG)l>{E>iLH?7?pr3&D@$&B4@!%`A>8d_UH{{8D3;U-oR}*c|w!?7Vb_=05@9Fmj?kkbVpQk(c(+_oD*xeudc}AX%DCd1{+8G0W`cR#Z%oZ8&-t*Ez)aPX?*2k~A9`C*s<^P_U<bC%)yyJbh^=dizBP)@o)a#adeUq=oc^7oYbD^<W-@pIEM>j-2%2pKZJ$X&i-_^GLAU(co2l6}K%UgAKLm#yq`i;A_J>4z$LO<~t`e&nxlSJ?8eF*0rvKjY*`~xr^%U=ZV_#VJ=|BO72?*|fZ{|WxusU+VU1V6h0o#Xoi_wZZbCkEiY9`Hn;zk(M(O8R>zJ#3@-*F1&3>pb*_XLs~@+${ba=XHD+;pL6?-H_)vzLPO3y#nv}zQQ{28hISwW0*DnhJOD{<OwcYPxBmq3;n^(sL$PBF#lZq06xcSv~%L;%~by?HTsRG0`^fpeusUxkNm+qz7MhDbArE~i01<T*ZRC;)C~atdNKB$=4{aQjCCp>`1e2IzWt#j_GkYt3chS%>`R0c()Vgs-typo$*1c|t1I>=-RH0$Z7gVs=hO!y*7)+~>b7Wy9=I=<p>?2d^8xjobz0Z|*0`paudlU%{>bA&s*i0AeTl7jFMc;1`%uS1k$>CoXt(1PF&}p81^v-?7!L<x)w|<Ifp5GT>x2ZXlmFop%i+8k`wZ0IduR;!te24g@M7i7842JW-}4w>9R=Sf0@v5wbd>hn#>c_8{vLV$I)V3O{65J{*w6WYh`z6K7rF{QE|mQi&jnV=>&WByzQ~=&kMHG@evf1g&58S^_xq)Wn{eMr69B#Adncn=3-FHbql{6Vk*8x*)aN0-6El;CP+uQ>l?PK)KQ9b=$M;wN@NqTp+_w_@KUUQN$m95q%UH4jyz{#+zE^O5CuT<f2)*OGGOP4?t{brL;l5z#`(3NWZ_qoxPdoRH>yPqipGph$xxoC820DJ{W^L|=aTN10_(CrHuG4LFo^glv0Ppx-&I+4?{U^uwb=Hd+Tt`mDIx68SZBMf~-nSWTLc!-4q3?aIyHCJ7zTdNEy#w#~-p?$V0`2AaKG3w%V4dy#o>1PCHcj%CWSaN+-JSyWOk`UcBa6{3#OD)9A?45O|NBoQdzSlOeIi+*OvV5ACz5`Kk<7Mpc3n<Ng^26gez0w${eZ<+vMt88X^iJG9!+i%@o3^+%rV!8@5MZE<h{q^m}`w~YZ)(O?8R}^%kjmG#pbc>Vqz~Rad+bG)b#a}B?scgjJwkYQ6sn>W6@S7SDC!vT(*76xH4mJ8S!K3+xuYAmm^n?xE%S6w&i3jI6tv))rq~F#9f)E9PwDjg2yxVV(}B`>)Y0wIqH+^N^Syes%@ien@l``*K<7a5XN3Cz9ao8V#zmv+yLhC9+#Y9#9`D=Vy>@gL&*2yv9F26SE8>;T$8c)y!Cm`;>4fX)|A-GHKpb=#`)>16Bp;PkLmLhi>0yckpY~a@oUB}Y@dlb;a-q`M7}tWWg*T)oQe7p<b^BZhgfh1`sW645uaH6D+88=d7d-ALjRihNBVulXBdn9Y1>ia*NpcuK1{npjg-5__!`f5g?u8pYsAl)>nh70CH{dqCEjk^PU3GFANApWApZl)9w9zLUc6=7HsVW+y~lRYj!+{xeq;O_^@9Jh?Ka~_j4#oIKTrK5A6~cvJl`cBe1PZLM!c1Nzipd+;?4A@dF(v#0iN>@#^)KICigGm)5OP!#qVLR)5OAkPrQdXfto$6!ya-QY}?3qgU_*z#NuP=HxMu3F~Kt#$I?Wz$hK*W7tw@YKz<RiaO;T0uO(hUJm0ox#$GIbA^lq7arBGnHxbM6_2kx*_u}1**AjcVz2pTSXB^L1w6ZSvj&VHW-Q<oF?;;;h9M7_H9S)I8V7!amK_7k>+hzmtI@&IuJf~Rh5b;6!3$~rG?IN*oKhb|re3|hnY7dgTNKX8(EPt6;xEsWmiSIHNf1OzD7nT)#lks(8;qKY?fbn(4H_0XU1HMW8gyki^L;r+WEQPIkNSxab@dd^|v+Nz#=V#)F%prP-i`m}vLoDYkM*M_z$W0SX4`T5RdA{7lJ*Zhhyn?)Ns~C&lOuT}46R~(%1I=f=hUHg~Ye+wkehqOU9`j=H?+tiaOARKshOzh97qo%YNV^o`als9lZxidek$59>3Acf<_+`W!i9LQ;ze&89Wj6Y79`YXQ!->Pmi?8a3by;oVaB7DU596_LT3^3^ul2%x$`-aQuWhA?g&S^LW8z_qYm+PObI#g6W%JpV&9;)n!nLvOOX9|iOOq?<bI#H%TbMpCb7W;Kmew{u;;fAGGWMrsqo#mu*{LhZI4g6OB+g1rYGUzk4dl)0gT?#t_y+^A*kg`w!5<j=QU8qgmKr%vdX`Vk^9mL&9kH0;m(2Bn<6rzs;+NFCBYsC-xKGH7FGwsVII|z-karxn_lUim98XT2=&KM{Aun7V#^T2iS0NrpEZ$@piHp&ykeB1jeef8@OKe+BJcjXdn(*t1#cyVLiC58<lV4B$I^uQYg<Hv3`~u>2#7l|A%NW|gcp1yDBe#_L;l#tKS!CNx9$U$H0lAUHVo@x!fV{*rZ2N}sOvWS0bt4{09KtdZx1kRq4xy$6aSQUobz&^O8F33@H?epb8(%Um$?`48xv4KpT$UQ~fqv-I<%!EuTZ_0BkCmkr@cZ|;EbCLYsBHnZRUj6wiEUpI*J50rTm_$VmiH+eWZUPqH6X4)eFLA|6{smnA3$vl#$u&xa}n2I9Kbja?Q?2^n7;<CgKdp$Yf0?og{#I~HHaHfCvh;bmkVb34#Yiaf=AE<_oE38r3r3J3uewx#!cuO5clJ;2%6wNG{K!|g4@wTS++CdX7o*n`|wydn&3{f&eTLuC&wo;o<TgqCl>z=ErR+HthdC|S!M?D2*%OG(}~5;q6wZ&o6fSc=@(Hmn>do?g`2|Ii^b2O367=BV%b>w)zrii_h)(GhBEeI@ndL$m(b?0Y;)?y5cg*+{izkXGK`y(>+i#h_s;9hnWrGJa4zZ!5?Axd*P8iS5%;H;KH9|(eY^v?M)cltU8wIuO(bz7`ToRHc)Ta$p1h8cv=O`>rI=gln1|kbKXkGF>4=33piVgHr_%prZV2Qt@4Y&Jn(V~FHDj4tyq?leWX_g3S?0>&yf$)7?gO$OkafU)t_SWC|4sjtSakQv-QaV?ed=#eC-E)XeQKUE{uljaV%a-O<%i>M7z-9IC9(Lwjel#z-=+!vgZ7j;Kk`GKH^gtK%}HLkH1x7BAUMBIEME2z{vwvLay%zBQny^JpRDWriE}Vc$>TYQQ?h;KH~15K^`fiDayf`Il9%&5=DJDRcQ~(|tWT@5jOdr~ddm7&o@Hds|B%m0;?L3q|4tM9o>=^GYJMm7K5Gegg0UBi_dY|PrT!rCcdV<_`8uzMT<f2R#mh6S>^Uqmu<sy#Gx1hp;o=PJ#R!gJyo}sd;uVbJs98b0%D`Td#8VlsAh&~f2g`ajE2&#aonY@imvGA&uO#;^@gyD-yp)>d<d+h!v26?Ed5i^*XDoOk<E7MYC!R}<S38&GJ+`f8Je%=c+G=V>^O$gB8GG?u=A1)~S38HfMpO3<Z7lWSwv8g!hw(S$M*HyMd)qdWcs%_`A6~d2KJgH86McB`UC2#hJcM`vvG`!>h7f;kTSMZ0jDyKFB^KY>r))6e0W2eNU)wq{p31l%trPP~T_%$oz_=f|sl?N5>(6*9abNln+dA7ekhnjw_!u8uC;HCBF^nbmEZYW?8_e>8yV@2?E`qTai=WBkA&dtT59G1I%ss=lVdRFfyx`%CrxAB&EWR6YH=cJGtt-n<V=TF+*cL@Din#>$vaKh%5sbZ9d^C@DXB<U5oX4V=JCbFDo4`1lz88=6AQmo+vEZSMy;%G>S|sz0v275!LDUI08INJU_B=-zv2bmO!-(rK7VAj8;1-PKcoT9>$P2D-TV2Mr8MmMb-;Da&KD=-pn70M7aE*vN5VxbI1MAa)Tz8+iC#?hdb}ZYLxGj0%8ZZ`Lhqx_qD`N3oSw`Y+w6^5scuOB#hp|{K+iDWmVceB*C{1t(O>lEsOO_R@W?N<A>Wsf+EPP|)FIl!GxmwiMB(B3)d<|l;O170J4q{x5ad~Qk7=LA(n{f@sLFB3ui<Pmh6meO`l^B<zwj$$-)Cm5<w$h9%GA>K57;#zRlFTb{3Hp-6;sc4re@ZOAAaM!e&zYwL>sEqXDf-WRa6!g-ZOg^@Q^p0!WhNHOM}0x^`KZlAZ7yOtmWRgziT!=zygW}v>htn=MxT6wQ`7qsC$}vHu|MO~G~v_R_6f_UCKjKAK0UGc+&(x3W3i&PRUj_FI0xe*wA|E4xeSamP%k*Zw&ILaF)lz8z8v+be0bri@O%Y`Q`(k=I)ia4S{CN@<FQo4saUTR#2I*8jwPe{@%TrK(-Ip#n&duhoQ(Rk#A#^Bs7cE>C%r#$A=|PO7iOH3Tw3Cs)aRi_;z0U5#Kl;)FmYk>!ewK=?8K5ct8E`Mb}`OI6F!|GpQ<1(MC|g>q+_0@4g8X2`RIT87hwPXGxZ|){zEWl$)umf_?G<C9#H>$B-6A(ij=qr$#lWsC#x&tzW~hi?;H'

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
