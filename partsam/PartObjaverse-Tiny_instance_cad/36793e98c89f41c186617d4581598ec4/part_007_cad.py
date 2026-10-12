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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/36793e98c89f41c186617d4581598ec4/part_007.stl', 'relative_path': '36793e98c89f41c186617d4581598ec4/part_007.stl', 'source_sha256': 'b225c0b637569141f32c0e43c5a5191f86a89a74591bd3859753f8fba3b3012b', 'input_faces': 752, 'input_vertices': 475, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12178369611501694, -0.0644075870513916, -0.03208186849951744], [0.1361059844493866, 0.1930638551712036, 0.2436012625694275]]}
GEOMETRY_BASE85 = 'c$}r22XGWe*RDrolSB}~CM{qP7$kBKCJZ)FB!S3rC4$Kai41}v36Vt<AOR~f0z?)96NU^X=V(}Lf%(7&Y?3kX@o%5^UA&t5Z`G}PMV&hDdFD({Z%<E8PtO!V&C+M^(ePJX3#=F3Jd2;EDa)?;Xd`-u59`;ncZC1ou+d&xF5&9W?H9Cc*CMEsmo`Eh>)We$M9*;FS~lO>eQNraxB2!N5<V<EWN?om;k|k*-Y8^XL~j?5=o=E&+ZC6oTBBNdTa~iqZIQPB$G@zuD%flI9Xh1y5<7fvJ>@sdny9?v>D7b6OElOoyl8B+^0o%Oz+0|E{@zOSC4b(F1HwCeN)|r<{1WAzW1fI7X}d?oM#jnOmA7X(3x2EEk195M9Zrz)`zC<@b>V=N<5zpBl+$ntc&ZcSXMYzZ{NxC5M~&^mbADVW+^h&bt>`W}ZqdKu)9{qCDU$EVT1(<<TlS-#KS;i&CC#bl$)`6zB<18Uw@vD=M}f~7xlwqqxBM>0rtaW{H=Dxee%K(t??iF%5nt?-a{tP{K(-&c^P}*}*QH!7z#b>%N1X+qntWLD!dtA8@(0!d&;CH#%V=~H?Ros{KE;j8ACCx+o+-aWUwu@#wqo>d{I2}1r9OE&f$#eV$IY>Ny7-69!JB+clsI_w5>IYCzHn5^9X(z4GX^}~EBWykc1T{6A`w!4u^8}e9TrPo4BEl&GaG#7<YU5z1xWkZ=avG$Zj<tD!~D>GAzy;utt|Pb&!5sCjl{<(!uvd0Bk>oBQcpAAVd2Kh0@4mPzZTMd_N)hyzr6Bssb}JKod3Kvk)Q9QaC2O=w42TU{T}oyGemfAKRIv4*lEIz){9O^JNQ*XJNOJleiQp-iSO7F({QcS3W>kFy-dn`)C1gD8K%6xs;gX2wz$kFzeY2(PwR&AJDeeZCrf_M>8NMW3~3*|)mGug>rB#aW@=6Gj^eAqbFD)?+Z@1k{BsP-Ih!*{;`mFUa-8O+k>6zENr{_PL;KV(34Ze#`e8o@&i~royHWo#lcoN>edYSF)m;X@xuc8=Mu&6D#pjv>9#`y?)H5Ja+S7SvEck!Ap#SV&Hd>C?sT+8fqPX5|>!zvLR--L=uEJB~xQX>}JypyJu2t?P-n-r=Iqy&3?~=G<C+UCM*VTtgJwtB@H?BlT`#2(6N;~V#E+PNIdue}ryOQX4(aVt^w^!On>-kcCuhwNA^4nyeC)=aXrJ!F-MgG*G(q7t!cPMW|5%66}(hkPGrZWB+V{)UMtVMCYJ6DtQY>zmzQ~0Y2tEHSJPsYghZL#1+!EtiD46zQ`-u>MU;bqz`mg8K1A>*hc?l}0}+Y7`$Z!PU+4%!PIA13W<d<@(y<z?#vzQ2@=N7~zrQ>5LNzuPW6gCF|AnnTil&Yn-egB~tZ-rN}^?O>~ZPq>k-m9(4w<~Lm57mgsmb+WXB?c7M|U)tiG$gg<}{f*_@3eHEqGkt&Yjp}1O+&>!me+No?8Cp2b=a(n8;k>V#E9Ex5GE>TNgn*CB<&gb`pOEXqjO+-$tK=f_2LrcAIY0Y>KU*I!{VjJF^tXMPwhAv1i19Od$t>BvS_40}d4`m~;!inmM&<=cIKP#!|Kw=tFXpB(;5}C*$o|U?%Y9N03I$&hC;eEf`drSB_PQx}*jK}Zr}vWUOk1^Si|}3#WLz){wU>6)yDbF|&5Qo+y;rzaqyhN3iWo<}$btU&^3`VHGtS9<R15Z-jDEZT{B#kipLW4(q11oE#7)9a6kj8G$D*V^+oseNZhRVo{(q^>Y2m4Pkw0a00@@MRyJP6<MBx_;jKp~fk^6@I@kQ{lA6Loo&Ne~&-Fm)3c$VX_5}PY}s@R!zFL-F`T4_&bW~r|;I2!z?U2?wlX_ck^j)ouB3%{0bos{o9bWrl`hrov?$@OD2Yc2J6+*k(QagXGg%gzcnQZLE=hEW&o{~_il;eH9iwOszVzlP1~fqwo%>Zc9Lf_jzAyia~_wvlUao|{Sk*PDf(5kH_gxc*7*-&%Y<x$Yeamsbm4+yL!bxwVX!4t>Ka^q<WerCx&#`Q5gMbHP`SlKYKbtDDr*S?r4RKdoD3sfRw|wQ&2EUEo)y%lt|&QfjHh-!29p7=ZgomT9rl-t9YqukDX{)adyb56Wi+e>`_1+9y=5Gv}=Vavf?trb)li*1eG5t7WeSKDe`tBSw)iQjW2$F!+vex$kR_hs>Awe!vRx?Vd}2(WkD*`3bwZTzG?5av#zbbeS#Xq_l}g`F-X5>ftZXim%`go>)V!GqY5Tw1;^mANag~FfZ-BQhu+YmxvQyF%s8dd~3NcX<ac6YE6sEyvy9ZO@5cLD|m_Uph_~1Yah&Tsc&(+l&1|1kn?9$J1q4v`d0w&QwH<QVTYw0GiL$tq`@-&=)c`ZyIq@y@jZTwoG+uxANXC(27y27FXM@R`IK<`KrKdik^PvT?=Ns(wqM2gr5TguzHENXB-{v22kxIL<D=H^{yFh~FO0@{acq^iVKUl1ejNBD9pxN&g!6PI9eA`i>QnTBw4>QG0pnbMU(8p39ko*0dHA9z^yds1m!1`reyBf4n2PgQ8vS`^0V!XPjl_9qxkB!XddIQS-^@RsPQ>}yyGY8Jk#1fZe(<vN8zW`DlyCGOHCA{+Ul}j$=2Xl}f4SdRxbG|ZT}F>HXrGp`ebC<~NjsPiHm2o$56St}fBs##HsxLi;hl%0pRLy}$az^gaFT4#5GnT`GtcycX?Tge(m#!am1Y{=@+TRmjr*mKq~TdAOclT5`<aJ4xt0gd5t(uQe&&Irq@9iW+2hjioFnCYnGJA$KXc#A(hp7VsVmd)s#(GFe>k6}K0za;-5h<tbEL^1iRU9DvOwB)==_892WOT+Y4hJWaJ`%>pElnZg8p!^LfZOV4BCf&?4LHj=`B1rZLcTSgE8&Nf_neUd9h8ehkj!@zn{6~{5s;I!L9vd%xgSXz3B9Vod2T15z0IF1<LcTwZGZVEf8+_Z<Bgz?R`<tV_(Yig!Z_xJa=gE@8vqNEeXZE&C<_pCkBIC`nfh>Q#|@l+Uvy`QwQVb?4RWRVxF>LetMuOxaGRjI`09uT&LQErt<t_y{^qHgTXE1fc=j|aLc%%7uo}E8D|__vagiiQ!72@Yw3nzoIX8BxOKcTk`loyuEMyQ<D_tVjSJwGaZk&c3G?gZ!t%VWEjWd7uT*yMqDN$&r&p*h`Oa_ifFG>CR?08@hvb{_wK4Cpj<?xg%6!&3KHF-20=JCk+JxMA9$1`B<}q5uDv=V8hy_1a4D+?a#W26ikNRoPR>^rW&#%RO!S59KfEqGyH3R%*p5Pc%1ozjlY@?(cZDLo6ZyW|cvJvyz&GD$uvy<SK`;oKIRdDP5%Z}%E>;2ANpn$ZOmZLuUdAT)n<@`Fn1y7xa@rvzZJZu5};gg&<v+UQ>&Q84#xaB@;6n_Nn-$I@Tjf3Avee5-V2haXN`jx)0KIUEPTA&|S%!c~5T7>(!&sK2j{k`07@XJ+E{)U5?Uky3Qa?;Kd^j{u=*FBEo{%`^F#-PUNXO{VfeS9#ub$)Vd0C@kFa$d~L|42DnlXKudtdRMbc_|0#+5HN5gJ7&rRj-Bl-oB^c)u-b8W?6{(3@wc3=UjVH&nxv&{>n1omid*fJ)gHN^D$$>2Jm&5AL>h&p!~&2;P$KNj~9yyw~c)YKI#VM$yZBa{K?-*`jd4Y=m;MQZkadg`UddAjW93Gom0yH%&qg!ohQH-7L<Oa#}`Mx?e`YEObqJPXN=7M&EB=JUN-55w2yH*9M22mba3muH)C(`jPG%sme_&k<#ltx_y3M|xHkNB8g7|a+biq>FJD>i1IGKVsOOBc;FkHh<H9}g6pnw3hvPhcd;)Hn=R50j9dOAY+!yv1M7u>{ytY0s*v=FOcjlD)j`8J2^tZqLz++xYIp)O_JU4k)1)p*m^SI<0@|@&sH68p}0DkY1?<HTWb^_e;{G!L)1GhZyn5%qcJwy9D7UOQUW;kCLtAOXtDdm_O{}OIrwgr66<`mEKt7q}X{loH{<=i(3-11yzYp@>tk8bk3s8>HJ<FFRKa|`-q9M(IQZkr?LG4&GizrKQTBcX#lk2?mv0T0ZDb%sXu@SHy71Nh@fxbOCim;0jg%~v?zzB927)%Fb5S6Yq$?==tC^~k~C2|l=w4(x*Q!6%n+=fl$AmgiHwem(HPC*--)NS=@N#`q54A(tdyuUUL&8osL{?uT9raNLDIgIk`99XFqYr)V;sm?N%Y9pkGESZB37Uu#>j9<L2+k9m!EF<dV-gTPzd!*ll9yYl-T-v@*DZI5;24a=o`d*@Ez<HjyUf9i>TGA<N6E*Rs(gqB#pT+kPMQbCzlY5!!6OT%BK$GXAPf70e#)(y;GBf%}}48}i`!Lx_SI*8tV8OD>qrQnwJ3VrS-@SEQA#5dc6e!Ffvc*L*h&!_juI-K*#QSgfk!*RWDI-QpHkmm(6<N$c<`{0)K6ElVH4=n2~x=&ubkFl)JnAaPDZ~Q{~k1Ze8rJS=zg6C*}^8VZ|>v+bRNbvbpF@8?H1%4UhlvV=I>$ZUMvi|4Hb00iv73z6z7}m4(r{Ml`F`l%ZCgo_&pMfv#jQi%1Y?5z=z5+j$U!K?XQb{sD&<DQ-@AV&fjxyhNlYCozdaPet)~U?X-r$Z(L#3Q{z0se4F9>d3?<!RW+_FBVzw8cfS!c7CA57j5&&jRp;yRCx0uPIlaY4`D;A9$}5GDOaTRjuMck*fQho!LYdNdl(7f({bE$e=tdA&$k2R93zL-{$Lf!FRP<Ek+y81Ekz=fS$&uJ&@D(%&06ZbCkA%X*{pXi@MU4`toRxwb2wgR0j7=engaIUCw@S9kE}i?eY(mczRAgZ|)_^-n#+FmTIysZnP#_{F(ckI2(d#y5N0>ENSE%X6FFc|Yp!cNE;Z9vgHP+_HY_jJyeMS?~SKHG5+@?x2-u&pp3^Th@(@BTo>g{w()dGvgDiuj|>-zt@k%y4K<<(hl~~g}^QA()O6*;MR5Q^}gV_p2~P)27bV}@s#)Dl>9P2=>2{X?l3~YznF&iqvLPN`wm-qUT;44as6)1EZ3=RK_d8{M=%d8Z~*T|GM)yvthd_>UjTQm$9tE7fmr8X`x4x;Zm*sC0B%|5cQ!1__n@EfytWDN4Q$oB3pdIQ#Pd?gu_(WO2=XoO5%j1C@R|<HLx${-`a2%X1W$b|{m}7Cf4s;0dmebNTQaY5<Zmq3nfd7kc-Q%uj~!fq_mkP~fY;58_jWDP$^6#vOGQ2XU!(sYU5jx{_rrTK%li@YKubJdS>LC;?S}k(xA1(i{Gim+Iddww<vorb8x3BtuH5JJq$_yeQuiIW<vo#OPEL#$&b(4j=cZJYzce?vqo`fVPwj;FnfFS9PvN@A(~PKRLI-f``>CULaLfBF`#0mj|G<6BoQn71_Ia`3miJ<xdGkAX?|b>V<U8V*fiGN$`|q%C&>wa>zynjz{vGn*e0lE$FPen;^7+a#Za7OF0yiGXI+On2$N0SyZ-AdFgz=)EFRs&?S#X~&cpTU1v`To7-5?uy)`jSAKY3$ZO6GSAS}Qrf?)Qd{o0Y*W?+48?O~B_=llz&OZYtgzuj>bHdC#aBt69!=v=_%ieHG`&*7udqGT^(AZ$j{#e&8nBVN!YUzh2-yajTJd4>+d+xaIw+J#Q?y<-M)Zb2GT*J+C=<EABTpmZHD?x<bk~b{<Cl-QRE@T$K;~Fz0RXOaI{dDtHO~sK;|~%ll>LtoPv7_t8uK%la6(<htJZ1>SeP$}jU}>w9gzPc?AM`*AlnW>>^}pL%=H&gZaRX?@S`tTGV1{9UZu)u@B_)T73OKRkr_{LmhF&X_V0e9}|7E*vWdq~&AE;`@WpmEh@CgSW?Xn3-=2>Xl<1_=&ezCo23B`TY)}{+90q%wo@xuRWCShqO>LE&n=2<^%Tm?J)kA`wM&)<^#^jIi-J@QCTtnZt@oM=lw;nUi+>LczjN|P91A&9>e*o0B-rt!LAJfzrGdYf4jaIAI8VvJ$(60=s&N^<GM@#H}YR5iFZsahU+ZndvMG58+vVy*Do5U`3^*Dk`>(Y9f)n>m*CB-%Xn=YyAbtRT>{T173Si86jl!7Qtl}%|B_q}=A8DZZ{ca+{+F<h@NOZVH`^};w|vK9hAagy^b_ujzrRKPQ+_8>tQx+XnThkMzcInXc4OQ~nuqNbE`lddmFwNy;6Oc7UV%?oBmK~s5P<RW0<X7OCGb7ao@^-p&PVVJx{U9}3|z-{pB%V9J<cTaZrhzE_`Qc}ftOk;-s$%nc%80zj<S6Jqm3MZ{KRA#2kpz3qn$5L26ul)R3jPlyZ=lFf8{IJsXa1O%CY&!gAWUrc5p`b#(jL@9`H4L<a#uJX^L?%^(^@9|6*KgR9x!m&>w==8h~}NA5Wou8kfVo-2L6u`gAgH(r48H*T2GebA6($^XvPXf_IF^x<R28C?{Vic-10!ZfOvV>vF+laO?M4EBHLnIZoQ&zPm8`Ln7WgX-AVWo>cCR`PbpO;F$*FySVBhm`4}h06r1#U$pv9kY8^*cu)zfFRdMi`#_Gz;Fj;r^a_81FS#k}1I8YItUolu^>6)d%@L6v$NA7aM(R=Vj{H97<~-oFW99ssm#RuTII@%j=Q^H|eH4Cgi#qr{U-ZQ9+42U@*VjXkZ~2byGq3ju_n&(+v44*!@Ft_>y0$k>G}G|potVe`c@_C1W`V!jgzv+qV7=5ndp>x_dzjA}Pr$S7!hY`iMVA^Fj~g6C{-UaQPW>$-?iVZXfLp#BG*kZo&)*o=<G>cE=XcrB9z({W-BZV*9V(Os4@<y0+2jb6->?Gs^-t(0&nIA<j`$Yb{e5G$wwNa_ZUD}4UeDM@%F%tBf={o6_Z{uyaNO!cz+-|iPXC+_<Hi0kaQAxVFYjbOM@OE|_yQQ`gQ{XZAZiNuVyqV$BMRYrj}o)MeU4(i*LU@vG<?K2n0MFJaoz5U0k?erX?Sl0FOeVhZ`Vlj%_f*HYBPFZT)(>#<Me>T;O_OG;$hN$_E!)2yV8EAs*m}N?T>Y6{rkJP?>2Z39vLR})b(KSP5CkYh4qm0s}J=?`_wK3?tKpHYC(B%p8NZPcgDQS_^KJ6A4YQ=ZS(~1JFe9Pk82O^zYXs_pG2VF_300O@*~ds!8pvvpK{(YAL~`d+SR-31*Q3ldc~S$tIU$FRF{3B`DlGYJU*dTQ2n|6|NaSezpDRNpHSDRR{8(;6Y2<cu3XknbrF|EQ1>J6P2P{XFMW6VAZnG{k*p)Rd%J3<<}Ul5I*2)e)Ir?dm1PA{2Xdbv`kLH7kXkYIC3-2wbs5(rD^6XLx-xTWdX!O_WmaZR73wPFij`!nygzjn>N?cQH&*?JabxaZg-mU4O5T{d4Y#Sd8BOVyG^M-Hx1nyseS1;&B3G;%<6hLms7JYM41F*1F4RBJdND`s*O@uPsKdFhif7Q2o=#JG8htpmvLP;;N;ZUSI{hMgwLR7&UQC-tuC`C6j-_5gQ+gRK%4P9nQ^=-}yY)cE$`7ViekirFXqT;^9?CeLvEm(E)`QzxF&;`&d?d?k<-rx3$+Cu0f8(->%xl586<H<fR@5Ds(~5N;NUe_3n)|k(Zo%zU$rY>3Sn2lkL#S(e#L5q%wPrbAyQ~QF{2AA#6=Avcxve&}@||h5c^rRkYf7un?Ri|5gJpfmxCl-0{5<BD9>*)f-&Ta%zoA$8xu|oIEAQ>He3}}Jp>r`e3$^kYs53Ax7cC#lQNEyu_GYYnHtLG>m6+$re8^R9X0n3RKIG{cD^q`2xh*qwI+uAdPS4n#@5O!6v;OYik)Cx-N1chLbVgcw=6h3TV~*OElRg7=Zf<jH<-ejSU4TBj%kp}}dFeB7+gIFXqt8oSg4=8~#fy=vxB|UmWj*3@G#k0vUYNQpwJ&p2T#H_@Y94V7T3PZM^bMI?nz6F#E^9(vnsGzM4QSPvqmEyQdA^KGlNF^dO<jg%sW^bX40U;zeM?=2aR6B(>HzBRSWW=z5J1+1zO9FD#8_ERm-V3zW!!{uCt6$PsQrQ&2Qy#kb}kEH9LzYBtUq-q^#C42#bNXVsFfKm8}72P)M3mIV;#b{y$|;rO*WeQxb=9(W2seH<6Jg@aU^569?$*M_DPJDP2|4g$tTiglTRd9@f?>erJlriHd!3Cvbo$>>E(>$sAp5JVXSPm%Mz&9FrLdehNkpN+H&Tr++8k9cG)WGHPmZZucg#+ELZ7$^vTr8+;>0qesaZrWUTx#YUPhoD?847#m;%~bKIu*8OF+ArB?ngYGr@8%t`$h<Kv7Kf9<lIUf6b<@n1B>b9tf6+a6poZ!eUkVsFOPTvpX(nHg8*{*}G{&8f^hC-=+Da=gh@eop2oYvZ!E+@~_N+V1C((~Nn3)QWxMvc`=47&jy9MBR)!lv??|EUTG^?#tu0r5;2-)@74D;>q+8+!jjRm&X~xIFxY&*))%Rl%GdG(?d^VJd=7k^>XGUxh#e88pg|Mim&B<i^vu+&z-ZD<tV?!L#HrS{xG$&WS6a=KFN3<<HfWs%sI>)ckWr2T_Hb9c9QG{%Tn<Hn$j0&Cz*4B{vu83n>3|w(ckva*BD=+b~9Cn^W<mAF4O<yvg;Ohp8PiB>)fW;X>LEkSotH=%8oNfX_N60YQ^@sY&YX0j7_qQ)F$;VYUTH`EYm~p<*}4s?Xm>wm5klnex&VX&MxNc<#CoU-o<z&P4P(TsV<AAUrD~2I+{9~<xipR#W>o7^(ODlIK-n|rMtMS26ZIk5Srq3xUY)qbH7NBoI2#nXY<fC7%QKJTG<oVnDjt{{#`>{pWAZNlvX)en4{uME_<#a&caw}#qN;*PJNwP`71oe?;iRJ>!AEkyjLiFp7B}6Zhn^e*O_yL$GOJ%I^*+XH>j0e<o)D4`9&V%Jozs!`<2_SF}^|eC-n{L``rHq?;khFZquurH`H&)75gt^<+FQ1zoE{`Sb23HxXo>^X>WMnQro}r`d4RXtjhFZtgI-x(msqeYE>7di!t`0_NP|9F7td?c2RDt%d+aSe3jdRv9fkvxChiFZ^t|pH>TBPjyh&T=J_*jL1w3JLHz@@@&j3J3u?s-4?d9P4<w&Nt^72PZ9`}S$tN*?7WFLhS>y|-m0#nrZ4qr2`2yxIrCv&|*m%auPoP#lo?7{>)Jv&1Q*UNDo5}Z6?<e0+evn%E6CT@=XiBHhAEiFZ_yqM?^0SOju)KX9dMjh)<6O3h^^YUlO16()@eR})$dzB_vRH0kMy70)7slmPjAK3a*-hKvk)yW9(9iJDQH+;SyID_{^>^7s>L}*KQO9vx6iww0W?4}ldN7Zre2~jJPzN%0ZyQD%%$)wrQE>y86=vL%aUgSgQU@}}My-5V9wU%iu}>OwS?UbTDa+$3uUICJxB{&#c?J3!%&9<~fn~m8xyomvSNsvTJ>ppG-u9gKiu@7BShxPf*v8-ZiR?YO(u%()`#}Dl`~!U<>JJ>_{-jo8i;90?{44DP$7Z!(G48AM_lyfuyIBK|^YcBo7o%=SQ`$~bx;yQA?%SPy0&}`k4`W+L(v<E(>%jJpVO}K5n8<x6vcD?rz8+NW62@*F!+j?(UtO=`Sr5ewYQ=t_R_qSj`x@_kw|U=G_vAyoFCSuj%p*SHvfb3`8F3HwZf-k7_9OK%<{ct?z`T?6d#F!R?{(Q@#?Po9c*M$|qF1>o9<kDSy|B+S>IW?2J1@+K6#Lc-vC{eJRepYM%gfx{)VW!X(!IE^%InP7t(9*{|Fz3X(5pBf?OPtxomYkSE%RG4E<#^|x(~Otq8`P#I(-ptbF)#bQ%mYzjHgg5HlKbRb%IAcipO!!gH=46+rp@~d&J83pp9c)#<7f6%$-lRlkr08Q;fIsc=Ne!JCCEbpJA;0X=>$vr2dinZfE{==ANNexmUUE9QAdNSouRVrPt9;v5xELRlOXH=Q4jC*<9)|G^OXz)^Xo4jKk>{QU}v_by+_T)|I*&{Rj`eka0hjt5|dDe$@R~PDjS2smFN4%6~~yIwMW#nzZIDCnMuh^ug4BYw#~L=#1pb>ba~qbui->%+En9#hi~CVx_;JFGJsix*m0L>R^v;%9r$LyC$?o<W1Oqjkvv=$36vJ_SSX$TGS<3hceV^pIX%E=~ceU^`cg$^h5Gm+@{ReWqDlok~w+EReV{)J}SP<I{13**Od898P}q&<iT4pZqHcdsB5za<Mxc3lC`4lM&6#fJ@-{*eZ}%CG2b04|4xHX=d!!nzwurABHX6-tImC@le^1N``qHbcd1o-sBO2{E-%SV#!By`KS+O<`XKc><{YG+M?ar_0kz8AOtzWaov*gfqF+GWh;3Ahef0(V>uL6T6(80RD}8{m(rd{Nldq-TK(6A2jFsL<zJYur^#yVjZ*tj9>P3t<l3k#_!0YiexzdWMYhPXSiv7%3X~i;naOIO|H+hV0E=whgWt_x1BrzwI`zKMW@>N{X3tF-NaN7>*0Iz@JRF<n)MRMf_aQ^^m#fDM`P&*jA$K?U^W2lvNWH|%KRXm;h2T(g0?{L{MvP8y8k7n%F%GYM@Hpbgnj(eN(I&C_SRh#is4L*SSHw}I(b#3yeY_A>EDqqFh8SmgePsx@scI)lTxyN$Vwk?d6UcuO{6B#EmN9jw{imi9q32F!9M6yfN$`|m$J}0OZ`-l1jbvZA@%E~ie>5+`p_SW3qnq2AOE?dvIHRF+Fm#CHBLp_pOoxh-FUg><&|DXN~#ee_Q+*wQWA1Ye+O#9i8=bnvRWqtmLD5zOR_5M{$=lZ8UCaAC8)NB6(^c*0r'

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
