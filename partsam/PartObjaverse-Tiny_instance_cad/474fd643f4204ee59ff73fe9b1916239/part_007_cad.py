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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_007.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_007.stl', 'source_sha256': '1b2c85c1875764d9d1aa067e762ced56a2210f6d23c64a8be4b2b105418519ed', 'input_faces': 854, 'input_vertices': 728, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11168919503688812, -0.2114081233739853, -0.45741355419158936], [0.11693021655082703, 0.22506868839263916, 0.42838287353515625]]}
GEOMETRY_BASE85 = 'c$}qu1#}fh{PiZdv=F@L!&^!z?y>}mOK^vWLvZ)7c<>;><w21IcZV#l!QC24aksWm<UjMf_wj$(_B-c0-^V%k+`D&wZ+3Qec6N4VHUw3V6E~HCe_4&xA3Kb+D;kDIQX`eozkTn%o!hqWldpTvL4HPZ@%2A1&#2X)W>6D9qrWjEcf0m|+V;*}(v`b(hvK>Ox^j2u(YtT&*4<n6=-sZp_A9mS+NZtp`*dpEv%T8>zF5KHd0mBm$m<&B`hWbFSZ5`2_MRxk*1?jS%IWRb`HyP0PSzFQxV>tzZ0EUfO0%)Q^=|Rgt(Ys@(NoR{r*8^BciMFlpXp+>aG#~S#BX<fm2B@Ae^%l>i{Q_xx*f;+cv?6-9{fGY7fQa;hMW*T*TkKA+kVx5o9v(5d7Gs3qNe!9`p}iKzfJ*(H$D`Fzbn&R;fKYSOFG+=!(UKpi{3U9_c|y3nln4(cuk|%$o|lGvt<9ZlkjtoUar}!lvvWYJ4fz7{{NBm&1>tA$MT09og?|FF$ej7u@L^%h>gMpBGya%ngK}v#^YZlojZjk-YnP^@jK5glXQOcNcu*rPVjF`SSma=P|DlL7zn@c<-U^M#=>%5_J@2(KdAV6;p9zG-d1+Rd+yE_&bUFYqdn{0c8S{(E%~vUS492~z7pREtTRqHBIz{AXZ<tc+dE5dlK27(cKiB<QKP%$Z`}Z?NA|UY@H;#TllXRjNIkJ9Zb3T1e{K+e#2l%Q=F4!zU!4~sanEv`7tS~xe)91+--3B?zOCFyr)lf0vj4=$^}fE5G|Yqg8#*JFf3oscInRg;yX3fKYr;3z2T9zQcT#VyrTI`k3DQXYF>;+dBL3`WQZKFhIZ>|brZ4yPjfdriNje?VO8(97Pl|7TUkk_SerJ#DuYVNj?4FAI;AHEKzP^!e)@nI!{A5wWJ0sw)OF9+#Ex0t6Z(nLEzi)mE_uWU_KW6Pr*nfQTA=y8o3$~4!8DzWK1Bth<w?%$V^pN9Ox%XX=bP~7`pYz#1@!w6pD1NzL=$D%zeBei^S5}wuIBwR<(oR^lI!ifQhf0WV7k+_q`+N2{Id1<vNayBbDIc@Z18JAcUvt5qb8M!hvos~@?U`)w7g}=u=7w&PPxE7D<UdcN1G1fIC-QkC3F0e0pD6kGeh=zTrt4B~%y#+r%I~69Zbg31qdqlGA1c3Z$9S)w$nuE4{@w*&-)h%e?l)sC+rtJ?h_Cxj@?$-!DfzM2wSxc4g6YC9f9fmw&7246ESkPV{Luw*9Y3W(e1=O)ByQFU9Cz~DEfQa4>t;zmK|kd4{!{q33hkBOH>fJdwKAWFA38*QJA4z$t>Jd@jbZ&HKbF1VTrB@oE7Z4;De%{?haXU7h46+JQ*d3EA^n&WDE}F!aopA(@$D89H%t8Yk)gs5W{Phn?0it-TD3*_93Fx6OH5cR`9E6YlJKZz@ZThm``SF10p-)J0Q|g{k<Y6Gq@6GZriUN%TUUt>9EtmJR2=xry7!ZOWu658$T`WMwY-7US9?|9u_zzk2rel1g}EgP<zM{>{6j^@OF9GUNcnh*EPx+>(IiRlUEA3H=M8v17P92LtSr6Z-!45<&gbTzxGs$v!GC-O&#y+m$$jA&RS&+=BS`Ysv##XdwV}57_Vh=G<+$-aNc(Kxtd96Tx24@NN;E_{7pVw;a@r%pjSOiY+-*#x^I<8{>9iKVdsrCpT?e4uxpqg=@pStE{`2_qoG`M_k@Jfg^^ZI!jBkR`j^z)N`fF|Y3(t?8bL4(AlC;?=eCrM3tu4)j!>XQ-<xkHg_14<BOUlR7<{^AncPTfs#Q77F@7*!*pWdDzzpp=D`Y-M`hjH8&rO+M?&yVw4zD;~jw>F1RuJv0>`Lqc`eBL-xK4#U8hvmF>ha&!FS&6q&{3GRTq#gl(OLwI6@UzrwyG94(r+YW)XV}+oN&aIR)rS9M(|$>3Y)yH-xJOrqA5mQ5je1#5%64K?e0%&fTh9O7NjYE7!@P*^T}b*x)~dMDU$D#PME)b1MG3dLw>C<OD=XqRFaK52AGutvquZ4Ne)2iePMRZ%O8Q^@u;BSpZt*%ue%yl+!=IOOw)o@6ARVut{M7>Sr&pJBj1}?Wr*FSs%AsI{_||!U@!h*GOS##5Hb^;pM!!M-=}<$dSFU@d<hW+yhvK_B`rER<VYhj{zWrhxj`Pz{Y)`!@Y)-g^>oqt`>T^u_Xry1|qqN(eb#Kqf{-gWh|6Odd<a1Yh$*0+PG5pNi(SBZUkLOF+X!zUugp0o|{J30~Jr?rmA9O&{tx-z)n`U4?#J4YX5cOiI^!v>D-Qc?mpge20lJw2D?cuLE4F9h#DCe3j;n&zWK)6%R339$|^TWSh81*XMaH)spqa5(-*TZvd<6fMX*Eg<6`krA&PR8=5&qX`z-%r{rcVMQCsQ2;FANX+oLM(sZT=XAWZ$dk>@qzU7%uPq+x_i1eLVehKR(xYjING<C`OiySkNxmJewO>zEHzm2W53-hzNh*z+>b3bNj-6A-GulO)1-Z|H;k2h+BMgSZ^!dHD*Io4L4S4dD)HTEeiGkq6i3=U&+Unb|F)I13#vmP?SLyuDAF%hL!SF)#4?myI}7L4E3Mp*Mw>@c4z3ER;YZb#d|JoD(cjDJkMvUoBR`>+P><fdU61RRV}x+mds8I6&8Ok-IgNH8aY{S~+eg7q*&qF%+a<&|({2#ozUq<sW;dI8!Phr7beDd<5fFmsc+Uv<HGao^QEkiNSpKAnQh&^iGmy@4kND>4Xrw>&=@nl;W>FU0k41{hdxn*5F7i`-2<l<jONsaT#{G|Y@A~Tz>dE6~h`$zr_te1JSABi!VjSrwTNUcX@{M&pM+qlvh4!psefZn|k^ZNB-jMS(7S@0tF=DuI{=;MCd?JeAyqavqbI=~vvYd}^mkyQpNNbTl%FQny{0}oxPtrZP;Okqvdx~$@OC2lT%oru*V?G;oDOUXC%+fv^FG`_5&@>m)uVd^JKWIJPN0O!$-!p%Yl)vGz8cE!~1URqM*`)vMK9}aK_-PHK6aF0ebls5pY+SmwPW;5b;W;&_o%CP4zL6&g_2Ho(p8NUEBmNr;e(AV!zZm0Ai0=wnjCwxjvD9ZX<^a+eSzY>L=C!rb9)I<Z1xWoi-*?CJI%16Y=9yY(AC6>0`_QaE{LjCmfALEK88@(#b`;-g7KHqr&MfuT=+Fx3e~giK*!ayO?XVHm2=UEp%5&fI-~`(Fp#>11|03#PU|zH{C6XY%ZJHy<AMOidMjVtwf$m5*INn}gUsagqa-ACO#Cy}zf8==^lW38|+bKs&xtac_#W(((v{25cOH(`tzu7Lnz5FJg*XKfU{d&zo{PW%DcSVjt`{woix=6h@`vky05e7eS?lOsATnm1)G~!#UlcAqmw=bTP-zI?HJ7|?0Z-4d+vVHkD#z$^t$9-WoY9Z%$XA}J3!E+?t@YHCRD$T_6ZCqT`hi?<&`YfJ=`2Gdq_lk%2(7#3_{&PCi=TA5AKC!AF;wwa;+-ek-ev!GgCHx$B<+xVHlXyOU+X(*bDM)AXZJbZX+VG2phDkpD?v8e*cX9ZRe$H3l(a*7S{D6GET8ZcN!R=^AuY4!I{Wdkm!{Q`4Dd~qMMmifq<+@no3S5@sm-=V5_)P=kJk7)7@SJ$|1pbLVa=pw{EzmwJzA3&d#}b^EQ8uTfS0`G0D`=ivFSl_=o||^_ZAd51&^2<r^4W3RWGmsP_+6em*8b(VPt%8qZ<kzr4A(cLf^eTu#Q#xT`d#*!a_E1avfw-V4_|#p|G^sH6zMPSgy)^-Y8^?hQeou(@{<jckK}k?H9UEdPDlXiVciC(hv{Qv+vu<s&%rFSB4YVgD?FDw-<0;!I&~K1(hv8Y)!_#`XG8XjZ&gi&{>Hu%C^!1{jj_0XA=9qO_LZGTfAx=%;?F*b>r#5Y_-2XM5^qKpyDo9zGjQC$Y_$K=AEO<h?>RkBeDh+ebH2Xwx#0EfKAX}0Pb(eEx6&n$_kHusu*1H`H5S^)|A|MEf3xyv_;2T6eB-Zmc#hQVhV*;gLA&!Y{$5|-XmSMO!K**Vj(@=S=`DHiUcb6M^6yTD>-`Yz+gJZY9=tzS8x_m9623=0d>&`7uOE|g1L}z#Sw6})eqb=#sbcQ4zVXJb<mi_!K8Suni-z#iY{v6!^cA`9?QON-4=yS9wK4P=+JR)1;nxY0d|KH$?v3SFuY~(O`;#lN{Ewf}&q?$eey4Ic-`3wrynPq_C9iMiKZfgDWM(Yidj5lqv&UqdjQVq+7}9yQR>sH7#D1tJxxT}3OAe9iXvD20{U7V@>qv>~yAJJ_UF3+b@5!_j=XC(>r~Ukf_*Ux#=+Er0FX<TZ)`@R?J7=E6Ro#K{yUtVLo7cKYefw=B`~%~}x2q;W{adqL`d?PxfrvjaX94nkNXD(~;jQ7{94_Mm=H^})2fW$@e!?=+o>=3Lqkb*P2>*|W-g3M>pD<2T?;H448g@s0M}4$f{uzOM)@?7x?Nbo%z1yF|&)*<eexI}#-k*~{5Z~<8AN{Tk9c298xE6`{4^bH3tNu6MXR7ptA5lTZvCTmPF)y&BEBt*Or%AeHCShLSLp!uj70;kuwXzhI?c9kFKPzytY=4&;<L#Co{5KbO$ad0u(m$~azLxiS<IGfyV>h-WeXIUj`00b?{m7bf0re?h9Q-_M<T+wRHI(+>J~%*pb2`Sc?8P<k+${Se;)}nPaVjHZjqEpPXNMn&ax^_vI3Au9zST|IL!-+aj5m1wu7fb2F<>s*&-$P6JU1iVvVHjnjB_V=F1}@l;ytQZV)U<4ToK=X?Jw<E%$RTFzAz6RMf~vNcn&__bWHMdeJ;}P*9iTbmmg6t?~TOsb-_&BF99PkPB^Cz;zzI@eseFDZ-u9q`_Y}Xm*n4g)dl$(-b#FP?g9AK+KK<KcAoyf`uV>$NBZ5eqyM}w3Fdzq)P#TP9Pan4mE?L^3Cbd$jrz&Bx_Qn-d)p-o{B(<?zFNKdq8-bW9RAY*Qf}_hEoe_}Jd$}VD|ih0tCcgLze?Yj94_M?=EP4J2QU0P{E>~&e~AAJo~x6ui|<NW70>%JMUVLU=7M-gzi#1JzA-xh?PuX?=#TxnMtu9w7|bsYN-6oY*M%cKLmE6!dlp6hcZDGTZF=B2wa*{VksBq%_e>g&{M5gT@%6$5kxtYS>33Q^cA%emKO54ixgW>9(+Tw|;cd*fMF*fA4r+quX3C@D8|RXt|CTk2+<(^L?eOd6St03M+9UU|ebytsb$SHy(|9b7OW)IR2ioC7cn;b>%oX2tu^!?R;`!_K&8eYiH%`UH^%^w|$Gv1>{B-Ux%m)@3iQ`6uNIPccErj~>x*5(ZUN_X++J|vJw$6q4<r7fPOZ#0%y=;a4>^En`w_EmvpXfA>^RgiB-$X-E56d@O`d{_X>i$LME!<C^VO%xc28`zodWiXquDzuFw8JAY4)EhO@vV2&&>x$U`9_qFZ?sD)^S++yQ&3Ne9zgt!bm%`MjgRqd`bL(Ja4Cn~g)p8!CM*1)v+c#deE`SJig`ijeP>^=#CP?WjQV_a%2bKZ)<CYaXG~?(=g!q+yxMw_R(vDVum!@)2B5!P`~4!x?{A|q-}khH9M@=8a1qYy#7N;Q6|PA-Q7Pe<jBiQ43igrwTZ^kmx>nO~QBO*Tqko(066U#svS5Dq{$kw!OF}U}eL64V`+kS|5}g<EtB=Y2qB*1m=9ykznT2#X&e`z=#xqB@n1%Y%6!rFfA}MDpbH;Go&$q@%+{7Qz4_TH_=I7ksKE-|dFcj+w-fW-#U)RxC5rKK8i3cS=G06+vl<nPv;a{65zE$q6)CVIF&sSqXE=!L4?f~WmvVN5MWW>bC_@`NE*>&+B?}NWGy^K$KrVYL-=^m>W_Mi3bS{d{gL(1X4j>&RMwp-=FJXPR4@!jiQNj?o%l5)6jgXR6j-j*A_(WIpOe)+r&sAm=7AGpy`d}~cZ$!BN`o`Z?2cNYKYKFn8nf^U@b^@n~tN%+oM^wWkO7T>!52=DK6mPh;ghNnm!N&kKO3$gr<C#K8!W-S!kAADs7uItcCv3&pPn4hXXIhJqr{tNTdZL(uN)f=B+I-Vm<GDXMEC!Q~MJBQz~0_L-OuR0maFIgGm#=~O!Mym0cck6iz?f27i!R7v|{OMc!`{KPaUzJ$CsxRWl)QKP4A5cin%N0~Ub~=uF^3|V?`fL;lyB^EmoLuUg-8w+(oAGXOZ}F3+!gF#(agOiL8~C5~q~EDQ;_s^=<2+V{N~nkJ-wgS$^R-5&9wBktg3%6K{sr~fRT%!d#ByGqgSn9Y{K_M7UY}$<*0@v!{nYh?MoIcrha;W%4UkShjEgzTA?A--@}BR!zhVlugzvZ?UG<N{cig`*+Y_Vz>bT!yJjLNV+J~6um9Y-V*`B;N<-N|?{uuc~@V@70uZ%b)W!%l#?zx7nm31r5cG3>aj`smaduu){iSal`yX`Jo4ZgFT->_DE=X1gHc@N?p&k<Li{pf!<o>MWC>!QEwc&^#y-oST02S<J<>r;$f7TU!yJb&FkWL^GW*VpSi%h{?n3BKdGZ>IPH-_cKSH^_<hv}gsqFStBX-mWey#kc&>-*5%@z;(=2Wu?S9`fpaN?&3T9Ev}cpitp^_n6p=lZ_clR=U4b_d0u<UY({((`b)N}FrNDbPl*4o{uq5{f6VJU`(yUCbI7N&A4uQX4>U9Wjda##Lpc@PEBy)g!7uPXCcu2gs<hHCiHVmhLeg{eSFJK_#rLczj($s!Kjx1n_7?wN{oZ(&5%1_fn`>@G;Qq}g*U^f?``TCE(LXoq-HX6=u7dH0>tQm_=w9+xeDlUA^e02u&wm~V^}zAI855pFe9yaTcpof)_Y1G@e7}gfn_m2Xz1I}XgY+HmHCErC$p5OhR))q%KL+nj){M=lhsk>&-tqqBY8evwU-zSH&1CVN?}J`HCO6&(?K`98dFpw;0O>p4L+$6AdA_mVTfM&XJ=6~0jr=&?Tg?gQk-p=-*eq}z{^-Bau5StCICvI$-aFsBt-8O6?|k3)c<N&u$L9DzcvZ=#*LRKs7|+|HKjC<P_vD`d-!TqgpNc^G&hd)$JCOdz)fgw=(g^Q6zvsdF66ZL{mGbcK*1>z)HyCd*LaM@dj<>|YdOPR1ja_Fs;+^9>Uf(e;6!Y_A_|9>pZ-2&nb=Vn<M`g!&l(n@ee8>2e5vLM-$9R|P=XvlQ<7Qud$2gmLatD0JxSadDV?1u`@jW~0jQG~b!+2jzh57iHE%%vDD8>oh7$<ZG#glPZdmzUZw>7|f!PD&G|7(1bzH@xi2n|Gh9gcIp$2h0wL?`%;@l~(y9AEt!?-)n*q#KCwV#j#zSKl$-`_*@j_eKqe?;KC=Fiw2uxURWnmiRGUFivis$8*8!JIBet#yiHt&1Q=b-|Q~>Irs3K^7_tkb+7Ln&-ePy@%*oT_3pT@3t+t6^k0E=)?vKeIvIuMLeN(Dj`;<9;UV#z?crB{#{!HGoW?we*LSv)Uf-;|UEX`miI@k8d2#{y_$7|agT!3NJV?y+8_17i9wes3U8EBkDc9FZ9=_Dqw|~Msj=crXHS3a}th08`A9;P}{E?MCKz!%?k#!=S_-2Q(s8@%Fuk-bdYmKCRuq@158NFQa9rIkC+U?;x=ArC`eUTr>JepZz2J*j}^KS0wx)OhJBhq;|Y`kXI&=0sThwOxZHX7@!Hgdg<*Z<gD=3CABaZX9O9Y2QjD{<b?o+<S+Chb*z55RfGnUPX%?)DFmj$>ZZo%99bo%7LuW|Vc@#sbWT+6i0A`MRc;f<FrLs^-vw=)Vo=3_syAd0)00^^x;(W$Ok1>KELnXP4ssOB)K`F)wWHn+iYg9n1^VO^o#iUf(hAY;Rg2zNZ%EsjZ^ux7fxutV4Iq3&*V7i*y|G;4!rhi|?E_x28Qoyknl-Gq^0?8}rr2x}s}X|KL7WQ+(&T3(q4re8+kK*WPyU^R-2Jwn>3{71jy9W4(dVWEA|DDHch5;A}j%2hT!&QuBWKGzR_Nns~o;u9xuo&h-*z)<sCivF^eXxDoOGRk2RA*zdC5%9Um-{DGb2{nGtSXRJ#sb`1XgepuIG-;m?SBtC`o9qT~cx6i=0GNONSKLFpCeEA*uKZtcHF*jXkci+B8`t?i8_@MjHYV@OzeG=cf9>$vQhjA0f`WY)Qk@(K_HeTPk?!^pChjbk4c|03`gzs37<n^8Fk-YxD`la4@$9kl%={wdVc^YHf#7;H|-|Ni5`Y2c4V(<gEW8H``P}WnqR|MjG9qY2ZzWs#jyNY98GG<UE#J}Qtuwp@2_tm`x%4cR8w5v&<Nk7g`-5$PUeVW&Iu0!+s#ssWGGoC)id%>Qr@Ez;oyuNdN-Pd@>dO4%mK=_VzddBVH@ZDI~XMe`JKC>~#L5zm|F+Y?9>-4Nai*Q`Wx<Sv;wK!kLIzxBry-3HgZpYO&hkR#a+?a)Voj#cVH@*al|F89s%d5c;;QGmfarXH7&h?h&pj!BjrxDg?T9vq-(A5zBnv}R+E0bfs;b;q_^XF*kPZ}w<a~(lX_|A2qx5kNY9XllVqd6GsNZoHXBK`Hr@q90ISLT~M-S#3K$Mf#1?|80#^&RV7&E+59+ncb?_H2BtvmN*uzH^;z4gbx!zT2c-vR`4nt}!nF-)X4VYf0yB2YLVUq{@W&4ezmjc+z>aR}WlFC-!<^&&^^;r|WREF9XJ-zSU@o_=gqb{og%pDca|5-QX9%I%j+58@%s47zn>F*8#T0x@aTOB>47CtpC|PP_9c%!};Pn*J;OmT8en*I`DHV;3pj*<87|ac+ZPjwhF%EdF}Ph{B7m>y31mHxO?C_#5<njp4U6!JJzwA-43IC`ZhrOc4imezs%!^cdU~)c3*^F^)b$WKwY#0Q?4SN1r0IJl&lY)Q$=Es&k(G`w;vowIp2JMbY4cIJ;~f0{iyX%#P^h0gZGs6BR2Z_X2rzFXT>TQA3paP=^Sc-bWYqxJG0DR?g!_06Yja+;XbkP-GO}$-*Lor&4l<r`F%mp+894cnR5&3QS9#*To1lSyyJTZ*OdJD{%y;4$)`2+j=T?geY;ypydM?d`svn%k-p=53gcWuq`xu&=96B=!}VI$6zMqDU7OY0;JA+OU+l~skdEU!4&#A^_{4GKKJujh2K~L(li)kPE3vvp!*_hoV&A`t{5ZaUF?ZcWyyJTryYNHgZxO${x%vs;gCu;4c*l1-_OFR?{lb32cPp3iy^pc0Fnq^%Ltp(Skr=1>3EvGFtxLo2`vuRxYZcKho^1&~q?pWWSzYTQox}a$@2(@|=886@|L(f67{23sD0hR^@G}mOc;jeO)WeUP;1_SvP0p*pD2y{Fc#H2U=O)Aa>Rx=G<!%rM^Ch41;d{$kIA1$cX84ZpyzJ|>;XA)aTUQT$rx5gS2jY7)PucPC-;Bild!iNcIbuEhe$g1G4a0YHX8$Abqw$@cJ+RPOU*GvXojK_x{H)3G9p3G_lAfo263hqmEsOWzi~iED@%r|u_~P5AcI@)?&BC|PUkd&ucKpQU;+t*$i4||<3&!`7#;+JRfB6Iai;=kRR<B0;M&C|c2klI=r)Xya%HX@iZkypxNf67ouE&Fab`aX1NmaymCohisy~##=r`xIq@?SIH0LnEE?iZ^Sj+?WO)ITGV?^FL^Ug}@pQJ(G&zs*35k45r3%HYZHQ=US7TU{65l>}fs*P7b`<vH)Eu-7+U<%B<NX)NE&wGZWdw$W~1-wqjzajN6r;QQ1a3y@B{i|B7xTZeJRNgf=x+DiE4G2dggT84PX_oQF_!92f-m!o6(9Y^E4!eD$SV&{&6@A!_@sCpj$-h~)P%!KcM?OAu=JHEHI%RGYbpA_@T<z47s)3=*k#Q7G#jQu;_BHr;`t!Luj@Ezaby00aW_Qm<Vu-i%|zVrKH>vU#}s}4?v`nfqi##PIdM>?wm@m>D1G%I5Hj_;SPKdQig`jGwT+(^G(7o@+L-*FGgg7)lmf8=NOLbQWlo}vC!8OihqV|?MkYRQlL#d!FR@3rl|myu47FZiyfP!seA4%|b$<2!L<)+6yft;gay8+1(C4|{l8ysxe=gXc$*e7G;_Wq{wn#`}BembmUq^1$D56yLdL{So!5Z$9{r@8XS?&EaqU8}oWi@O^zu-9GSBO~&^n@yg&iRAqwrX5%dwcm6m6?Qw=Fh#!9me+QssC5+!+je=k84gPMx`;Dk?bx*=CG8^sEh^H8j^IV62F_k<=EKd=<-<5uk^)e$fV&3y!IgFcZi;Mfb)itbpa^deDm<5vKx$gWs30Ko1zC|9iOM`w!{-2kJ@BI4=`+wnc>$1%InC0>J89dvX<9AELa9_mzfa}wu9pW3}?>`v%lVZN0bR>Mo-;pqrt;PNP@;98<!Xa2E(&s+noqwm|`70cEMQ7Ci)#%R|EmEPs&}=KlW5;p6H2os@=>p{MW0-yx){EvShUeS}{5=h0>t`7sF#awHzX<;RhPieE?$brD;g3v)@wNbbpKg5j8NTE1dsx|DU_Q;l-vcpHT{=}RDAr#;>HB?-o}u5XH&KN|Mk=F2Yo9-TqD}qJ%m4kSPdXR=zxvZB#fudF|NYY^A9T^^>P!BMTJs!g%`>TIa(f=N=Go-GsWpF~p2M`}k^iR7;b$0G6jGDZQoFdFot%T(Q23<iBcb(ELhHrk1=NeFmy#D!FQxuS*6DiFe9HY#`FpLGDg3IilDwQ+^9pJg^LUT(_Za&t^&ey%^9O&c_uVJ|LH!3~?sGdk&wnM4^_cvCdO71(5cj$7KFjw3IW@J0*3YP)F`dWMuem=hV>GmWP0m8Cq4i^)?@FHEN~U#>oP}kQh1c~Suf->p{U?^c*0&YkQuv+F`VOIWVShmD;?$apkV{Y(q4uVu^=<xM@6+iO;eM@mDI8VULuh?aVYk9gAAcufuPOYdaFhI)T62DX=$q69{lWRD3sM&#>)#h3U-Qv=-(#kkk7?vl_(|ahLhB#Nd8zYo-%CI63qR=H<elUf)cQBC{Qfu1SKO!ZiZMH>^||X~J@>=$@>0KMI(hkf&9C{JSKPmgc+K+F{KQ8;=eFjjKKq{VS{$U-`||Moe&V^m<nIo0{~q#l>gPP?Jw9cjbwOT-n=JQhyl&f--l8y<(0UG0&&SugHKBD+LhCjP3lzpH>?X!Dtu55vG{^Hd^{CqrT8|_zpw_?L&h#|zqSn0J=UB`6n+4P($z!O;Fs~zto;+q@bsy@#$W@YDiMkTEr;tZeYaU2Fg?f~NsZdj)1yPg!C~9wfO{QImx+I}>Ub0C&is`ptjP?o>TK`07U5;#0oBUllLhA<Pfz(-a8>di}thW~_yj7S+y@)z3F^%!l7^n4QRgR|>rW0BpR5(mNO|AJHc`~);rPP|2P%q(cwBD+4R$&97^?E|<orKoM2(3>NTHA!yQRJ=EnbkQYP{=@Nor=&p9ieqjLhGLit&0*`=OSmOuB7fUw?bt?>!yU(1IYuZHIJkoNF7ROJ)6*amO@*FJ_`K^t%osv{rgsg)`JMGM-c;=_6UU#h2aV{6e4w-p|Fmuw-c%J`A(sgLS=;@g^`5T7YVIX`GL<+hb!)^+gAh7`ga4+x+|geCqnBC{(#n{73cN`cjC78J26%tqZ7Ba-lQ;A#Y8LAAhe#Ou#9|x98Eo5{q~5$VREoP^kM2`{@^v#$*6U{>MHC|SfOx{e3`t1`ZD!CLhIH1{c4`uYWk(gb*W2Jd&@-YB)ZP~ffI7OF17YG$MZ)y=<^>&jz=AjvBSu9sfSUIC9j|!OC9ZVp3%fbmf;2JOXSPcm#D9h_fcP=K0{tj?Jbux<Tcc1sMnE$sn=20BJ1l{i`!bSR%oK@lpn71cxvxH&4tJrs0$kU6-T{(5nB6`3sL)1$5n_&PE0ODotU~Z?+1NfoG?&N_5CoEe1iG}@13FKAnG8dF_c`0x)Ad;l*r1oH5a4~r`|*qP&jR%OfvDDGf;Ohz<PfN#ucD0#JJ%GSbM_>t@DrzQ0JjeNZv%fiTO!LPEVbX+K=o{?MEGl9GBW#?r{jM4VKSHmc8b(KG&iw<209`jz?{fvr+51r`wcdY#$D@9yOuPMArK=aa(I$X36+ltu=3AS#DH%nZk8K>wDxS)S4esr&sBG=Z|d-t?zN4*4}iq{?;GykGQS*zRy0*H@K~Rtv8XElkZb&enh>TdZ|K1_1laJ<;lsZH3v{@4x}EWFp%4U)a41SD-v3FWqcQIYwql`Pjh2(XX;|)oaD~bo%#Emgx0xOJ`Z_5k65NliH9uvLCk9xB9Olg<hkYY|KGCvmSww%*Fp0}YH$9!62*9~#aMP)dsN(Xg&pKM)S9<ad&psg*3-yasWoq>4kzpFvI@BrsuNmQAhiCTF}1m^xfXRU>hB4ybCZ9euBOjZp&_Al7jj2x%@e4*P){V!pq@xQm-(K{^O#FNoX~nIc>?uR>e1wm)T6085L&k+H>Pe$9Yn519YpOtPtAekYSh(u&RSPxTpe;Cbsg#!<c8EOsDsH}sJpN%f(fn1kmpj5p`PMXUQ@_3sn4mlMvoWnC6A{*M}9|WeULn!TJv=3916u1iV<3uA++wIuuowIj}t{bp3u56xeIj{{<blXqvN`h8&fxCOm{--I^-PGnyXR2V}6ejTF)m>r=HHV<`Y^EBiErGM%|uVjaqX(>LLmm6`B)TSEv62w>78q(Y3j)xxCN5l>BW<`qhc@OuIaPqjfEXK!qyg($rO`(-2xGRmi09qe5zOK5EV1Qm3YlPiXy(m;InMe@m@71-0e?#%lyHjZ928kVwrum8MQgj!zw*zfH>gYferMpbp^il6#r@C&ix?mmoi<*3i0?AE5OUg`*0)48(q>eopLSjOHCa@n3vA%`XY9Uy#30=TpZj>4$9%tzU4T)-TDWsY4YeDr_gTK1^tRh|qe1LK}sK{9P#ZM4};MG}rfu@8#oZZcAw0j@*lSmcm+Y_o8k`tmW@Cuc6+-vUoz)=k<hKin=~yCy>`rui?2(U|Ahy`5oo8(K;WmtG>>?cs{epq13aeb@^RZc%_g`#a~yvL}8UeYlQ;}lN9o(eSa$cO(9I-lEONLsS5oJy`;l19;lc&>iK+1@z09CDE?k?IfWhyy%b`Uw^`vYg}7?Fj6x2Dh6-gB1}GF#sHyfZ_5)X;UQFFcA%TiXtB{&pfm-`_{orX%!TlO37*~P1ltLQ*t|YkvwdVfRC8=AI=To<&o<L|lkI;G>kI}^ExJ{Twf9m<<A=LA!w-H*8;<<dod}}UBor1a)QIzRvu1(#9dI-5A^$_Y&gw}%<epTqFu$Rz!1bw}|k<j`OwdSFO*5kN;1h)@Sk0bY^?#JI~JzQb5LMWm2MDl*>iPWdaN2xU*q29yaA0SVpp2+<N2(8bPk5HedKF)M>+*(5G2tw-<<nz?$`MVQ@)~Eddt)u+_t&fwBP#@trXs!8#A9Q=AXDD<dv<|1%+?_m|TJtRG?$jL^GlTnQQ_mu_p2;}9-HJSux)pVMVkUo6SLLswLVZH(NYxH(P}rg{fINtL0Ch)l59*H8<H(b#$5C%1@21{B-a>5SzU(Sb^%b%ZTGt`Bqpm~Ulw66rDYZ$?Ol?x9^GEtwxSfTb))myTlPHuTwEmvZIt8J1GD7R@gx2{9t$!g`p!Qeg8eieI(hm*r8$xS8?$a@Tgw}EW5U=BE5L&wlt#6Ry`9YUaTudP|xj41vbkyk>o0%MszJ}IG$#JRUGCxTPtrL;`sWm60PDGv95Bb!`_|Xs0x*l2QqaKltc|50ZLE((TuL@BLD+#Sv5LzD~wEnE{M!{0o^BK7hwPwBl8KLz>aujtGk9m>M`V#p9^(E@7JeE%DAM#b|tBm=F(E2j@9Q9@D^W?MCI-gsZFU^ywKT{tdub_@mWf-7%tO01<pS;z8?xe6$p(l9^_1`L{vO3;Lasz4?S#P&hXs(crT!mU+*95%I33#0o`fO|cPT_;XFaF@9imMV@2N7DwSLm%`dMTu&*1W(E&^nVpID|SAbtm#>>Q2=2{J<ampf$9%6*iDl`GY@Fr((R@AJDocS*KN#(0U~~gnA|QCUQ#ZP1L=~`W$<cdr<51-K?*RAE0%2KS1lc3QZJ36g=e4)M-@Adc`UIkWOL#MsqU*T0?6Wp><PoUO(uj)VIhfsZ%n2t=IFox0olLZf>%RIyZF_a#QLi)FI?s)VG+X)_o2A4VhsCllM>uQx7H|r|zRLL}4zWbu{-K=k^flX!6f~(3*2nYiPZi9EVy%>j?6B16t#}&vCU*qV|WWYdJ+>8lm-6@<QsV)QiZG)QhNBkrz|1qV|x(sKa;+t(z$%Qm95Ys5KgKe>3X7gw`zxt*i5Qem=kT<Gx1J)d{Wrsr{LT=ET%pRZ^D1NkZ$ZWWBF9xh1vcZq%AbP<wxKh1{FEH)F04T3;h~qt<+i`liBug$oACd<x5NAvux=V;SrE-+=dk=JeDlsnZZzpEbbksWlI#K4O3^Zfjrbtp4CD+#XClnCV<0v|htJbmQ^TQ@1BiqHa&UhV9!LwsC9d+vIuFLlpYz=LMm4JB3FopV<^=B(yH4P?VgNoQ*mgf0LDbhq@^De@E87*5ws`P$)wF$AB(R&m^?YPu4N{$#<zu?k_;rzSeIQ_ABfqFQSf6*vIWf)O(42{M}pX_l!Tp?L+jmp0BV<VH=_KAM_V;Tl0GARn&hFTK~zIwcK7yZ#}Ppp66~xZcg2r+=kqoT3^R;ewYUzMm?5#DE9|d_w!E`=l}Fyxc%=xT^Eg5|Dl`nm$8>W`u_5>O6%)l$e`-+^!S!)PyA&7W52!|jsF4iOlck'

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
