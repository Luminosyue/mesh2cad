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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_008.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_008.stl', 'source_sha256': 'a00c1e50d3274dba46826a4d622828ed4af424315aaa1b7a7a7f3edfd1319aea', 'input_faces': 729, 'input_vertices': 457, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3946787118911743, 0.7868410348892212, -0.6397410035133362], [0.9086401462554932, 5.196065425872803, 1.1367985010147095]]}
GEOMETRY_BASE85 = 'c$}qt1#}fjw{-^#41)%TfkuN%@F2MmbkM;)7q{REE{%r4-R0sC26u0QyABrQ;_j~V`kcM<58qq=zt+Fr<6CF#-TPFZsybC&Ro%JY)UFmgP6`A6G8@~119mjZV;Ew;8Yzt4ZF`1wY~8k3{;u8o`4~x6mwz!hwPyVqwHx~wy^R6>ZQAx~-P1qN^e^46gnwSszg@SUVLe-R4e8diO<U0`wG8dm*3o-)XxY83bDgtD(c*c{!nyLAgUtWozh9gtSe?pW-RGb?|B$3EX_N0MuUuRIe7GWLR|-+xbt3L<xi%KRRNX8%C54vXJxt3Rxt>Aqx=_no7g8e5tQD%e%7<!s*YoTspKpfh-qNd8_rA-i@vYJRs#||l&^T_tw}_K4IodOOhw7dzU2bWd)K@QS`{&d_{2AR<w?7_I-FtDW>Shx^jc<E*s&22`p}MvBI{NkO^(DnIWs!%S!O(-Qt8QN1tGYe&$W7HZE<^ddmC*h@<FsCD+$7aq4N$Lj)<D0ahat|DgV1}Ngud*-MJ@le6za{@68inK(1+T{|G1H;x8hvY-AT%89QU?qsJG5Ylt0gLiSq?{Uez1r4;@8*ZXQG)szsmI`<9eJy;)t*7aUUE^JWk9P+RM@lTTFL{jH+L@k|<tdY|<}oNlPs4E&CIONAoN>jUWTwWH|Q;AQ7jzf)f0dz(K;d7nwD8+o=P&)Zreexin|yYu{kJm+eQaeonvIBij{XGtQ&zf=No0=J|5vr8DqeaFsf`F_nYuNM5!dhKmTRChIu{Uk{4PZ#%;#(A_C`l9)0&+^1xl<N;YypzVa?Tm<XtB2}VnL(JJ)ed3aKJB2o-E9@}b2KyB6ThPBMwOl4f^_~Z+Jkvt7W&?LXiv8_7xezrnN&A}CSiPy0UF;M+~*AD&mF|snd6x1cblnhmEHPS<Fts5(malAcv{QvnyTfk`|}oS+;%}HwVwWqwO-?Ls6KCQ-@p?Z=W2rQTK-@i&99jv!*PxCBMkA^Y~Q5%*-)+DIDblYSE7JJ8fQx?)m`a(q27`qiv&II%BkOabr1bLQT4ixQ^kD;RX<$wy~c^!jrC<lY1M7NJlY=DjskzH{$;H8&(87~^-g$rMDwtyw(7>0imDrt)n;ltf~)P<^0S(1dps?tZxytC3fmg5v!(Ug`9JIWXszqCPcf)C@-Sr}p8p~RcHz1I99!pGZO>(`r$Z*yjd&eYH){<#s__yp->LOi-GDq?T(0#QJ?5+KKJ#l_jg#l~CG{^Iue!I&fH)c_Zl)s|e{Dk5&E#f0Eg!Eu%HRIFL)$ZUg2pj+*@sjwFi&-R$Pvtw0*f^7#?yY#>lOCZ@^_~Et^Q1%RCk?Tr18xjtqy9OoR79^{F#;FYxzBQFKYQ_S5)^V-GVs&aSo{7H3H>N&PTlit!-Lw+Xkwe*BU3#_RlPWICCng?x}lJ<9n|!+pqfKgL<DgLziDfw|b7efO)!Eb@z;DjpLb8+1By@SPS)>Ua8|~MV5@#b_6urs{QI5tm9~RKBoJD>+j)PG!MZy(awnhI=`*fQ97@!@d<T)x;p)#&x0#89Qx}CDF4*6M(>XrutEK&@?pNsc{4&W(VeyGA684t+w<e?Q@wnI-e)y_tGa9OBdkBSi$-esj8ifH|2nJfHv)rJD!#3X_9v-_{W8zZ6<R*;D70sCevg*RQE`#_w`J7%V}usGrT$;Os^467G?wVDZ^t&M{=2X0?nPBG4=WA5sd|(C3pM{!-s*fd&Zb+d`t>REwZCJ-be`Cm&)-np^JAWtADB_&xK}J%sd|>wbG6>^g*s2X-?E_mgJE-Y+}l;vIPM`im#E%p?kw#`$Z?$y_T^sJbv)lDhrTfmp2vRzux{q{Ro$u`hIzQQ#auiunPzDGD(`ikSQ`&Us~$FXy7o74p~iPL51pj?yCqY#e1Mry+cQ2T%I{2~x;xu(jpNSqC|vcdT_<Y&`wBeO_8k6%eX3w^gvQAihH>1}S=Tq?X2eLvCL{P<JjMOP3Jz8rP+R+DY`&@EYqUE!M(@9vAM@(uZ&MX}KA)gCJE@lU*58Uetm!jZuFdVe-ogKMqqfU`{B*sJR~z&2=1hHF48QRC8h^!~Xixtd+HUX7%d1s?kP>-ri+#>aRdtQlw__pV?@6xn$J`sVPRmbdfccz1uFiAsxCiTzmx7ufdr()+k9S=V=H0~Us5kv}&9AHKYi+On19`AIbDpQmvq|-|b@4oo&ZPU1D?#pUswYo@=i=7iy3g6`9&Oil^^ekaS~Uvmymf_L-=XDFHAfy6UfV6`nfe3zgXLJC{q8N%e5P-(OWQZNIL<{c`rgs@^ysF#J&Nawxc6`lxfqV}UBYqBnREr`hhw8vcTF6QIKS1xdEn++)y>r}q37;@P0OF%5B=14)y<&xSO;E*X?v|#A;~oUfi5^_+>h9eJakpvif)4ZEW59|H&G?50~79ewcK9cJ=*Uivtw!b$fpZcpE?5i$L{+4T3^SYe1%b}yYHq(dp4fFgZZ{xb?fs1T^~G+KTp$s4$Hb%_1kl?Pjx7)ajdx&q2GO>?QthdjCHbIAJtv6n;~zNT4;RN1q<a9C4n9*1p1bV&{Ge^dq?{-$ba0Gs@v0-A)gUA-<l!oQNCtE%&RK>bUnAbN2zX}IE;1auWeW-$J~Q{Dy_EPy4RtGmT%Eg=e4=zHP)qw_*&l8cR1GdZ51?*yTC4ej*O0x`_SKEIxg<6cXV9r9ELuB-US(SU-PtTtm~~+IGO6UryJI#M`y5pMgOk48SU$*_2$Z^=O1H1EyNjJS=TG8Or)->W}6V~hu?SM`FhY?_a{%J8}Y}?(RIxA+ihL<t+suz9_*irc9yAfSM}e=sqV?UM0L-VI;wlx-$uO`P~L1<M0I!d52{;1DDQex7I990M7>=$;(46dQP+7--*DaMUFAFCJXUgrKF==m9QJ?LG|cmZTM)nCZRla&u+CJ-jPu^!`_TKMUc0od<qh9>QCjb;G+3Vt)VZPMSLcnwx`*<Hd%2c(*)G+sf#EopKEI&vGp_HyBhI=7$+i65r&`|3-Vkx}AAlaaIoesNnd;su@pQbbzjNw3;ECN*b@OFX%;$Xx(a!3vRd@gOP~%ux@O*hDbw+&qJjQXQg>$6!3hnvu2zgi=sOMczn}mA)vL02ydYGYvo>#4Drt0>eU9djPXrS}ZyS<_6-e#88>&;j8p0?+#t-5Ot);%l7Q*Dnsbcmh@y&;&-M*W+Z&wlS!_cX-(^d>WPetH^xRNYw85Bt}%N4l<heEaM9)SYQI_K}@GbpQ2y9f5P}tI3#$vA!Um5i?Zx22a8GPQQwI_;$AHcBe&{CoAG;`@KU}t8VV49(Yg7d$)d5-RK&Qd|vFO`;C$Q>|u?+zMtm7jOwd#JWI3cx!c<T<7KT%fbl9Cp}Ls?^TC|?81uZ?chzkJd3M#sdy}h9S$z-iMnqwrgf_u^^DD2qXK`H3n-P=)`$ft+cyCCH{M*?dW8VpVue$N}fyQyWPN;4_$$U)p!;`Q-mdmg2|JIURs=Kcb#dBKbnzqMUH9>XHUK9De@+aC;Z6V@Z#JqKXPOszW>UU0c*Yw94-`;aY-;azF*^X=cu@f;L5?|6dc0_j7&0N%zd_??rfyc2PEkwOFZX=%?N}>D+=-!&KH2>D+ODNwyAKv>`@73qg2x)mj%NOK$?eC3wd;Fd1cADLIKdsyW??oNHs_t1ZU(4HzAEMr59ZqVT`<1c2Regbdxo1z+z2hrj9IXW?-+LJJ0!=YL$N#|hlh84$+qp1~-saixec<vq=vNxzxjVQPae7Wy-AaV{V2x;m`4c@)b$5U4<Hotf*k{YEfS$E8>W#k-&qdBJh`(Y6=5u^wwB~6*fm3=t5c9-pdkphrbVJqcti{ltjX1Zsp0rfmdolodcsvc`wQ!f}9v=(s8JZgVug_t`i5!UhY(Ij2wH$m}^J(Qk92er-QKMCN<;n`Z58_+PemR5n1oOnYnM&h(D<@aouD25Ntz=`Jhn8<j)r|z>5GUmkuG`SP3&$c(vPa0zg@kAI{=>gw{?r_--#d)hX;pV!On`O%ZNOoTAKYDaYkp?T!`0Dff3I-WJ(V(|zjw!C{ognjaYpSy{sX_R)An~*482rSw7+QuoX@)-QQb(2b<CWS1>@p5iSj!p;JG+@9?#Kt=w@x|2j8N<X|kU~eGjnyPpOCRJYSof*ZO{-o!&UNaW2a1R^7WIJ=$M-GUAM1s=BcP>#g<D#5%Kg74(>Tv!6qM(?_aqJ{*tuncrX?{#fQB`kMje`##WmJvoD+-%Eq?>t>+d)k9VHmO;I)8kw|S^ZF=!4`6)v@H3cKB_mLN5Oj0ME9h0K>30ivbda7Wtp_jkoN1h{tGan(N-T}vWS2+BHFhuPhdSXqNxhjk-~Ks3b?@OldXBYQkC>t5_RYa}k#*DYe!4#h=h%u%P=5U*oU3zWi_kdzqoB{Sah_~`7UxNy6RLaW_-Pzh=TE`f?qW}%4||I9WQojL-n09S>eh&|8plkxY=q9M`APMAk7sXc<YDhitXFT6sqP9*h4Z9ePrSdMNs039Qy|ap7b5?C)2Z(6+EMGZZdB0sVb7Y9&>NJ)dGbY+o+rJ9`JJiJG(9)kGt=w2(R;Lo>fVc!5I^!aoLfG(zV!2W+1^u_Ck@&_PeJ|q3+OFM>i0A6<wQ8Qcl!tPVNXMRS6fm9-&gD3!a3y3ebqfJJ7FE@S_bEt8_!VQCne@j;CrlZiQlO1icE%i-eVc+on>6nIE{v2eG52@IGszW?y4OJ>-h^`U4Og}pxd3%U$<`tJTIxsUHQ3R-ZCeV=P>B@YOYr$pJU$Utq#50eCUHN<9sq2x+flVcfU_q2l_{-ZiLKwq4z~!Q8ZiZN4?i#;hdQ}J-(|aK9BbI&iY(&+L~uNehaRn-no6SZZukWP2;q>g?e}N#(w%bRQFRe@ILA-F&F2JWH-5QK1KYk`&4%os)hCT;VadxBKL5ftZidH6!O2Sas2mu)q0Lq!F>Jag6h_jRG7~_p6PhG3tm;-p6Z7@tel5@`rf>XbvV{5jaR0xqBl-j?T058#>LYn9p*{VjMsk7zdh$T*0CwjJ>|#oJdE?aH+Nyxt&KQu*watry{y+(=yi|dJI0Ttx~{utCdBul8A-KY*8JkSK3Y5Royj{T9pc}(h4;{>$5gjV;raEXn1p&We}F!l=cTAL*az!;g&xz+Pe+mGb<jOmvEP~RaQ-y&Y}W5&?)-~2FP7nctynXGKF97kr|^C0T(R5QzKqMD55v0c&2Sm*tcCYTD^FVFt!@PB4Z48x1<_7VMxF<{UqN}c$F7fk**;0VJ9N(<*q1%!;%Z)PdoA|IByS#R+_p`S?~}v6XgjSXdd_ek8H9DT2KF_p&uQ#ypN6UKeUCgFYX>8Kv-P)dANQ|;DY4Iv-vXWOu{Rw;`6tjVU!EV<J-~e1Tvyk7Z)6tC!!H++pBfFI*Uf}}6&i{2%!c0BPu^|#sMxnY=F1`I))>S$X89s-E&4$(JR0%OY(t!J)Q?A?{D~{b=a;dnyCW<A(C6p&q&xcj_Fkd7nE>ZEyCK@?NgN4%V}6Y9gb^6W0XEwIU;x(b9BfaD1K2+&^+kJ{qdkWIOVm3l7;$`WApXAB&`Y|IhqB{&9(#{C(G3u%+H)=MZS)E48BrJIhs{U78h=yWlO5~1J>fg|wI9$=w?jJ*uR-}^MQ>w%Ji|G^$-al0kK)0qd-4Y0yWGgXG44&>nD47I>%4NUzM}6@R#<n$shkk+<3-*h56z|^&N-ZyjFP=EE>qVc&dQRy@4JG&Vw|$ASKS`|9^;;8JjVUfM#PC67fZ`OwDj*^t^!+8{vyuLrvFB~m)+Z@x_iMG<he@}`s=qHdTHo(*SpZW?or+Kc@Fe7*k_Fe)Mrv(i+$GBBMR-A(nile_Fqf1{jMelRku!c)_G-@d86~n+I$%Lv~BplHz>(0EkFAL^pigL9(DJvzHb_}E<qnS5$BwA)iK^vu0bDs2jBe~2kLii@6ZQmPgHyKcT7&~zj>diZnoQr?`cUM<N5FY0{!Zc2=N~_XsP%A@&n~--`Deu`$<Wx3pHZl`KVLE7v(1m)x0I}Row^<!~3AwTK7BqNPOtc4ZM$+Nrw0F7r!EoJq!C?>5Itcqhu%_m{iYQ?n7g6?mC}bbyt}^*asU_#CYXNrMkCNYi*}_aEE^Pwzs4~{GGS)eW1ryy!Rc>j`-P1>3PibL}NWokXv;-`vm-5Bh_CE^tm409`RQf!gtz{7cifHTZHoVFZf+S#<z%H<GSjeR+v}TJbX9v?)IWRe+=aN`&xYG$#5HbY?L=%digv;cTLB9v+NVlXFou_MWK6>KSTUFkD=Ep^hx`d>kPinRrrYZzx@a2jX6p19=+om+WBgt&QEJj-MfnZKM<!1=i!N$IuFfOhWgEV$ftE}Gy1zFvFfhVyD={Fg7Lh>|4nsw6^yUl0`Ff&By>+n%ul;=HvG<@X&%Ih>V@-?*%IHK-qu&$`)diDV_Q!~{_jpe{8ja#FDZ|6<MYXg@82Kac@AvC`{u`Kh_h?~&b@cC;T$`AHp;h4hByIh(XTUe(Vka0FS+J6*S{CI{TCrlEUa&4-fk%W<0$g8lKau8{^)P$Y2<a?T#Vxn>}&2D=Mmp%`BwWe`y~Dz_v+$ZJVyo5{*28KKm8TdTde`s;o?WIUq6Iy26V+djM|0qtr(5`)EfxBW&rxT{5slGll$^jytmr%y{NbQBlK&WOaE?SrMQE7>!bbNTRb<mhwh&80eM@TPxIr-@d)|c^5L`g@A4@94rrJCgnHNV+&Cc(*8d6L5vTb)<hfB+em6^a59=rPQ}g30eD}+gN_BS#;<z^EK%B#Ap=a%n`Swpne81|JUUf4u;@blXA^%%)qWmGOOV*~R_`VmnIP|8O^*ORPe9`B~U8)-NWizp!9|%F-!|JH+n$QUCe9FI{ZiVjMHxuhy&{^d9d_DAQJ@#KuY!ma}u8($>-OcBv9P$vqq3T9sJikVvL>S*=jZp7yFZ971alY-5<-X?M9If-poIP3Rm3Kuk)vZoHFfIeO>A1K8Lmnt5`33LYyKw$<U2m<rZETLE?JweozZXXJP~9B7LgRb#b=LSsnqJU97r}Rc85gi_@9d+x=gCd{e#6rMf4|H%Qgtg+Je*52J;FSBKT37uZV3L))jb=|wKK;e&cy`ydwS|3`u9}p!W`%)$KdbO)x&i?_k=H0-MzO6es}R|=Q8crhP5cabqjuX;eQzC`?{OZ{*@t!bF`d(-!LXdA&$qZ`+^ZGHOdz{f_6?Bqj5YzllAYxcIYMKb4)_rU+nAc^}WJO60N#-z!v;Y<64=KsCO04S)Vpxyq1M(`(1zTQQa(`Tk~U0?Sk*u??0$+e5#`FA)dMg->5$#GtT?1!?2$By^Qn5#XYKfqr94bw_j|$-=5m1x~p_8jLYTn`aRnI^{nc4+;=!vyr_%!{CMY8H;1&sJQ;sazstKS-cj9C#TVamjxD`}=lvey><`CymB%_@4SI)q$EMRfTT9>L`%#|{Xn&kPF<zhj@%M=>@gAeS`S4w3NF{v7Sr=b*v+_KA7g~Ev|GwgWkw$fQ(sKA+L6e#I&h;=I;{3S|--X)X??85rJSbnco}M?1qL1|VFs6y$op?@0;XIHok^Vi*&X}9O>w2i~gRajr@IJU6zcVv~{jfenEyejP@;ttW`UUDbV)(f6yQ<RPp@$#E{IAqhzqeW=&uKYtq9z*O9=ZpZ`kU&m{v+|ex#BL~uXdNw?-0hFe!$WA-Gr-V2fg+->!9z^_WJ7DFDuq#)$ODY@Es#ZWkqY6pQ0U>QNLq&pANVjRQo@Em1|b6l=-hLh9Q=~NMW>V`O{BwMU;Or_<#RNZpR}3Uq8t$9#Has`;**GK88`%v5t;ibJ}ysvA+#)!K;!oUdM33+bnz1u@mGcc+Wh?W;iyJTyTM7gPb}#v93WxCn?4($2XhhW)bE7C#>%_x!_~RHZbl2a=}e(%NfT`k)L9lUh@9O<bp38JIMPtkqaJXjPs72BR|Jj|M317<bvNF8_xbnUxpL=`yj>@c?1~mGGmQ)>`%v*lM60!>=z%z{Z1~Jz`+L&-f--u0WSEEu|<z2k7gYid~m<qn}L|#v1hzr?tMml?$`*nTiQH=IKT(7rTl%?bDwn#kg;@ZFuCAB$Fj3NsVh4%n`5t8pVal5_=d4Xe@gz8b!>Lb<Jf9)!L8I}o-8I`OkW(<@rGP5F8eF`E7tRhb>wCHq-}YLc^o^$`lPNy#G{UlVqPRCqlg0?OYDRC;*tv{VOvCxO)e;P7iN7@S7Bm+W0`n=5^_P4u|-cro`^B~@!9E2E@(Mcf^h@L1&cf8&$uSJU{1ysJtKKW))B<}i<1kM<-F*}y808xIhK^UlUxZGOyyvH)|Zo9umI~6JqLLX)*a0H%90C~_rd&%bZiahn&3poiZZUmEJ`fK*rMkn&&N6{GH!Wt!3vIzc5Ecab~JH}W2G3k7`b3+$13yw3gm*7Sf`XPLSBS*OWSuiwvYYT$3Bc<T?1L4;9$qfF>WPtK^J37I|9iASw|_BbCJ8~>*81)$Lf&_c5^I(*D+l1Psi$VEK`vSx_!|0_zor{7nD9s<o$B*MB-$}#&cdwB%erqBKy6T<0m-9K)>agn#CLl&T*_O+u<e`?CXOVQvZI&+s{}-Sx(9fB~Ef|I>&Vkx!_D6^r@+1waII<kK=j&ByzzS?6dfPB^Q*sB}N~|LK!cVvHGx{3FH&#OGtks@<xnVoBm$pz32<&y;I1i&?o)t&9?O=PNEjhJoYBepccm5h7-j%n>>tMum{IKwPUTwTX76TOXFA@@;3B|me#R$<n8EdNuHKm(2sp<`4jhJ9%TJEZXotiqSP<iSp%_;6U8UmMFVlq64NlAaPj#OPjlSlI)<O-9Fp~ZJL}#`JW6dR>)uX0PHhkC-bp;mIxf<8nz)N~oc@XL;=EnVxLe7$a$j4*xZBCM)4!ZCcara<e;4)T<bq3C$F86FQa*QXj$3bzYj4h@Rvfo*@^Jdva2&(P!|3Zl-j2K-$F&!)V|YuBb3do<VU9%*<+=||cwd_E{)W6;8-}lQ-)^E@Un3X1LoWD)T<|5i;6LPoayHt=x|b2<I-U=>U^Q~VPUM1v$OR+V2jN2;J7D0PcakXAS7^d-{Ny{seqA#DJ$KvmpCmuPw#xb3mnhd6$OW^L3+5#kEKDv~f?TjV`!JGi9?9$B<bor}1!aGdGqIdG4-)12Ax(HPA8<iA+dU_jbJ!d5xHREOh^EiKXC1k&M=qF?CcFSmcrlvr(lp_+&;8+peK2M}l<Ug0KiKymVu_!wgUJOel2_z?a_*ORnwWPRxjsiOc$r-ADouDax!`S@@cZO~k7>f6k_*0|34cW{_?;$P&Vk>F324F-kqf4$3C~C_n2jbp2f1J#n(%z&f&nz)MaTt<(}V|-3znq`caaO0rwOk>6E5eQjRv0Yzla<84A|uIEXcTY^!fLFwK~VOBT>%5@;)W+kfVrly@XtFHchy!rE*S@vq#K3k6h292_H``D0`^9_sAJ8=1eNrJ7~h?91)-8<SfvXT=xGy<Z>pMNiOG+gtF$yvu=P3CLxOMLoOKCv7{`Qgj_HMeNx6Cmw&N{u^o#;9*25b$5JvzTB5|s=vX@XG7{7BK8fQ?E*RgjOe~*~TreB`zdDwPJQ2%_mdvr_<jLvF%KNjC3;NS9<x`Ohrgls|p=4&+EJT0$q)d8p!3@OAESsK~fqjv7B_L10{KRLw5|byUFA>|}NA5>oT;7*}JORh;7xKj9i8*F|jFXyNFb#c)sl}8_L0@XNISuhQS_by#H=;l9OT)4ABgVw}jpLMtn3nm@NMAOh#EEijp<}Da1&>hc=2#E%9`x05><`DPk_-OsSaHXSIaY{VFu*bSf2ZegEGM~OUTUUe*~zohCt5DYa+Bw#PqciF6(BD_pJ+uKD@tCJKGAAAR*SqAeH|U^;#gO5!A_2aIX1_!x#WW3jvaH%>)2g#!3)&xIrfPB5q+XvckCAVE&8rAzemWA(07Y`47uQZYLf3><h|%y#jyw_52a7Ec8+x*??7Jw^IeTxur@WxcMy3HeL0!$K=MHPvNPWm$Scs7oB6ImUW2{@%y(V#y7U$0ShOW?OJ6OHLuc~N^lf3jr;!WxrY8AbLB4{%yUh1W@|E;GVt(h7&!?}jW7QpNPcB%KW3<=6+`mqg@ss&3^M4Mxpv)JU?=t_pkPCKX8PSWA3;s@jF=}0i5~nM#W4NHq!#1q94tX7p_Z;eN$OYFMn7?y=;_I0|d8QXR){|VYHT$}V+FqjcIY0AKlUz`qr(C>_;ezt~<)EI6T+lS|>=&jl4^jLDng7D%h3WUQ9oNYP?~xy4TfM}+?8hSddJ@+$AKlo;ZoF<sE-24RUe=w5n3rQ%h+Li<nHRN;f7g`u9N${RPONi1>s`<53*;A=e;Kz9#=p<1T>nlk*xbMzY5w1?1IPvC`IYBG=0$g+Tz92)W_!A`&fY}1o=c0lZ$0z1j<}w=YE9mT<J0k{K38X+Iua#M^&P9{SP62$l8!ZWY`7u683ecJ7wv;%@5tZLCt5@2pi|2ST<{&WMUE}-0bjr}qHUHlCizDCMBC)p2J#K`iRN)^KKXq5M62&u4e}cFiT2*9|E&QoScBS7$A%c-Ls&+%2F%4!;t*=3n3o2`dellYSEYz0s5NA+N)t=6j(5z<TcWgQ2=n)j^}RFxZEG#&qy}+5Z2@yKpD1~#&p1O^=Mc8Dm1EN#n@ld~rWQ*Mras_;lc{xZtgR1tTb2>+FUKOuBk2=uuVcH(che`@9>;c(@1jq%)sC$qUqzp2?Hy}P-kLtqd>s2>fD5*!Hr3&i3~)j5iPqAw5b_X~5v{Ug70D~oCt4N9Dv?*BuL|?!CU?{4W)3Hi3$~ypdHP2FjXr~U3Sk~YSf(xWw37an^hGjHJIQy_x0`v|LB4~&UCh%8@)h*0Vh&r7x1g^zbNH2c6l_6F@-&`#9M3Y7n5Sms&FBkZp30M#r>`RO6igmWUrg>=khh?(1@knHT(BuM$<r6|FZ78fd1}r)3Vxv`d0NgqE@zpQ%+q%A?ey(rp0<&1qi+ZEw2XWieJhy5X5`K2Yr!0TW*!BbQIkB4Wgf?}%y{Oh33(IxnlVo<au<E&nWu8(<>-saT~qR=^fhIkMv@CQrY3p%ME;4sFU(;R=27qyHObRb=5Z;@EN7m!l5eGNJM*-Kd<%Wsn5QM=OXyq195yCzOkXqR@FVjm*qEB+X$12)f@Q`sPmRbM(bt4|Dnnj|J{R*;mb@%|F}Z6@-k83|%+qjk!G_c%PanuX(D#WsY{)zcexN3KTEsjqVwt7P(`NF`^lfFHHj!_lZwvF}A@|U?ggLBFUZ1|k%;9_HQLsKW$<t8gaVX1-V4fO~H=wT(^Hhqw6n$lwr_$u5>5Iu-L-L079dYVD<k(>!aKWS0_B$3u9!1|;$JRKukX&%FWAhxF>)0@I!Lg22ajc+Yg~$ber<TRBtmIkg6D@^f>B!U3Ct7mHQj({nPqg10%S@h`KGAYHmYX~`eI*^M=~x4D!7`3@cWkO-)5ryTI=0TSeU91Wg6pXraO@!YLHcS}^NE!r_W$cYKlkrH`Ma?3AOA7B|9<Cx{zT^IJ7+kt{?89)YFCRZ-@lAl&i~{PK1fd1#(x1kOlmy'

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
