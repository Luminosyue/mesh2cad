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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2830f5fdb88942d5a3285a7433b4efea/part_002.stl', 'relative_path': '2830f5fdb88942d5a3285a7433b4efea/part_002.stl', 'source_sha256': 'e1ad97a7936a1f66c4d8485bb5f6268d0e050428b5c7ec4400a6b13422409fb7', 'input_faces': 882, 'input_vertices': 551, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37730294466018677, -0.37661680579185486, -0.4350385367870331], [0.16648273169994354, 0.07605420053005219, 0.05043374374508858]]}
GEOMETRY_BASE85 = 'c$}r22UHbF6s8}TBWBD#6~Ta6#w^b)=73p;Hs_oJ^2}LO%!yXa8Ak*o4T2a5M!?+WF{e>cM_KFsKRYvfcF)<f%ba`u?_G-O>f04=RX?YFt90q}S@2WRQsBq*>1AtJEXuN5@>wPh7(0GQzX9VajT}A2!IDe->L*PD+IDW!zPp2EqGg&}{{iFrjdiPIb*ne9mYciPZQ!V}<Hz<H=`(6<{{hP1tk3Xq1Ah6(4em2~z^~6`Jv^$qTdS9IxB6QDAAhp`YJ%-#ndI<aYTbYDgi^!zb)0BL`g8h=Uw>5ol2UDdVe#vq_aBvVL&BuIrA&VKceN6~X}q{7e_tV&_>GXshJ1FJiF#UR7r$l28u8m#)r^;NL0M5x-O?weT#L?^rJR`w{<vDw9&1Yf^YVFII{1S!g($U!d7`}iYm(Ggw3F1Y`<|Eb)?pvTZ(H{252^oLA=LBewfOae`=z|meS*}ZpMNEOyS3Q?@kecv`!%mWg#XLn{Zen^bGY9J$?%7`9hCa_)R20N@z=#~{dn}OXo2Sv2g4^G{;uY6skhPAX!#r(i}r-aNO}9DRT3ZD=@{IXb2(|JRyOZBx!>VY;y0bwN_qW-=LIQ0`2^~zyL_M2yZCjC{QZd|h{HaAiG%f-mt5CYaKHF1&EupVv+)*bzcp+#uDdN@tF&j?28n}qb3MxUAC2o)*eLDMpZK$#0lIuXX-IsuLrdWww{@G;6Xk*D^~X50Gt1SzQtnNDwCC+;l%M&R)N8c<JyzP)aR9D+?Th$rbABK`d;8(OLLQ(UGtWvKtp0uRT&A@Ml=`PXL>!Vj!=Ixu;@mX#EXF}2)W7GY)MLLKhjyOuM4W>n#BX-1EcKWTs-XSP8Z4B*ZySpE%rA}lo!yqn?>(DJJ@%!=QNHq_IigK(OMJ|u`BA?9+0D}KZW+)YR-}i2@M>JQ!OkeT&c#=WqUjFUrQFN!(jLpH2Z@N2yVPrOy(Mw8olg?K?obZb8`2WLUwH%NbCkG<_K!@E_BRO=za=#<`uC}5-0zZo;<uOEy-9vQw0tDS$u6{KSHetBb-fH95r-3-aotd_$;z)S?JIGx1#W`B`Om4M6N<?FT8giPf8)=2QodRtjF)Y*#IJ37C(l)1*dFDx_C|Tn?u%7<GpV+WYg=D;`29ytl=gLKAni0ixryIavYoWgcA=A~KE4?0pV=FqpTx?2>)nf@o}2FCx3_yB@v$z=f;dz@wM^RCw>zHK<aF?7@ZKzONY_F7r<pDFhWx%t56mMKI!Zf@cR$3hySZ*q<&E>p&`$!tiQn%3NuHlQrREj6-?&%eH%b-KRe62jluH<AvEtYAG?DtPrJqZC%vm8Q-?`;hX=m@va$Pg;CR{hB=Xj~NQQ{f-`!TCgJ~Uvtw7<Kr#LYPRJN%VvZ&QA2Z3Fjv#0&MbYPwtb?K>~Z{o3C&6Tj_KY0QHGQMhjne%))zPAQ*wUVg6yH9-0HnQ{MqWubd&BMyr(pK4D%<$i6AtDv6vq&;$9`@f3ca-anKoucG9Swcoi+{`}C@Sm)UdfcNC|0@o-uZAU8sCq1Cx`oT%-TQJ~%71a&Cvk4-g83xj75t&uC&=fmt!4h!-u)?l<M0!SkA2gh5;x6wAbv~UI+rnidt)5`6)1jtjK_ZIxA)p&KJPVE{I;wc4oiD%{p3FEO?*)Q-{XU&{@R<QU+9H9!Qa*+NS@cn!dS=Zwu8UoD|wFAVhPetON*xP&zL1~vCnmv=cUbQg!|g#gML=>cZ^e)8ffR$4dT~5wqhOs<_7=Lx6*zib%xBJw)?KQU&qQ)-Wan3+5vu}QuQMe&wU9JPs@~IxNh@mQ{?aaJ;nMwItS`^-YtJ`T~JiYYt64-lX}|h6~C5#JK|=<ir=>Kg4Ay=%!K*y&K8ufQbOXR7Y~s<!tSzC{Pw%;4@lhd9Y;QL$QS;AXn!d`a}@HLn%<~?PSro8za4KR^RV?qWz=7HpdI6WAo7Ja6~u4xT76agyH+BeMtS(FpAo<1-7<;4wN(MspYx9Rtt(P6u21KOe@t)j8~SbZ=khP*v-$mnsMe+*;?wOet~a{1+?PFfx>Hh5jadAB*C6Si`U*|*CaZ5a{G&(7eHjt+BIJ4v4xoL`uW+5^*U)d>m&#}T(o>ml?ephKzGJ2@4Zq)zc~W1(k|3!+HXG{qnk@BOiXT2L<yU86J8w$=u?~+sCjOQVxc|Jn@f<im=wE-J9|b1C-{U>{?Tk0*$F4&W*NpiPkG9WHzCjAgUui4jMayyv{_Xo@KD5nkdRVUe<v9BHmW=3+dG;cn4QIeV|Iu8Do8y`7(!Lv0aNWV_QNC7s>2KDxwNU@CrgFb}?EEl17gzMx)32pH`k_APKX(hD{?iX+o-uq+2TM8subBVdZbSayVXTsNI$p$ldaXR>|39DZl;6k3pnsKKk8xJl0sZ7^B;vO$7UOAFPpn_}!;s${>J0y>c6iSH_Mm)=H>f9JKk_cWX_z-V{KWmPPC<N1cS8AuD$}GrNp084=gMAa&(`ZQ9*u4*Wn9~j*2X+|Aw}x3mT82%!YwQ6nK*5))Kl#79{GFkOVVE3+B;I-T)!v^;{kb!9v38Wu_wG9C7&<U$9%c9<tC}e|K3Jvr(Z_oHB$y-Jt^xc@v(WO7r&WnH}2ObQTo4DB1QU_<+nhrOUEyx-dwM-p8H~*u|+MDxY^!CU>v)i#d?ybAlAF`(~zH9%Ss&V6)(&DVExb!{deot8;D0Y<Ymo^i(mI?)?M1~^HB05TTc`9{k(*A{@zODv6aG+uhg0?>#q@35P5oqn%JLB+mHG`#7f-kXTq^=^vS#t<MqAtYxBu5_<bs_mFvcQlX0xQ7$JV^h_Q%Usm#cu`VPi;%3lEa&L*rUdTdwpm&5ImH-(f(zuE6Dej})wtY7*X_Z@Oyt&5}nQxlMvm0E-RrFyu`e`eHN)MJT9zWRK=`0cri+`#7m$y?0E!;vTYCyqsbNcEHPy{RtNt5SZ*@9L#W+|vB|9S6xnjFV+oqJOWzbNGb3(%PsJ@~FQvAU|H=Bzb}!SY@!pZR|@K2ZnoHiMxLCqQuW~D;oYaR^-wBevia>ICuf^`gBO@nR0f6l>500d2N^b$fLOrwXYwAyyK5d*x%GBhyK(uC)Upog~YGz?8Wus9`d{A(Rg07+$Eo}-CcwIZupz|qM<uh$@NS4BM<V+A?u^PohIYR>bn5@=DT^Z@9BZh_BQv?@0ztnJ{xcp`A@Zb;<vAUkGS0omblqttD$^}zh+DQ^IuE8Y|(RL-0%Ja{b%eQ#3v>*>gnYy>z7{Pvh1sDv%X_r=P*+Gjgih(=5I@K2=;;5rXW6k*KnS&z+3#<#%1uo&xn0cH8=P>b;WfbJ7L|Q8;j?hcOmv?qpILJ^+cX)KVCIZ`bqdSyR_@oPVwuX+%W%4$}Yb*7nec#SGSOFS^|-8q_>J+do~F5hjvBY(zT<EOEZ53>^nQm!v6bnV~kgyo<4HDQM=d6^^Jz&*OS5|?=?yc?I7hJ=EQn39(lBNd`p~*m|w9!FXJftYkjl(4yn&&mG~_`OvI<!WsJl4f#TPUc=X%dM{(XzGCSIJ?jHKX)9>i7LC>)NdodGvYjjyzPqiFL;@8LZmGNK%R$VF2zw&mJcW{w?uJL0w`dwll_`7#R|0(}g&Vg)mF>dsi2CnPnBK<=jeGGX@p&+cME!WCAXrH%K{8o>-h;t3Z*V?L&`1La{<^Bzy2C`4pzO+F32iPa+Spp>wu`F(a@=i^sNjsYxvfkQTzCnMP_CWF;J)I-w-5*;KryxGZlm+tlX8-BP$A|AkezY`2#=Dl>8s}463g8^e`zhv~O;*(3^()q+z(tY|*q(&QIJOV-Un<Y<+9l}^w(NDpZ{7Ac&XaoN$9N9(fd9#1^z&`H<XyHOmBeq<?kV}1UZOSTznjx!9<@AKjCs6OqMT3IswT_dX{U-}-CsBX>+-e$<Z<<I{$!19A^qEE@I&%VdlhFq$C%!d|Jd@}5x?PkRK~6S?PtlaZ7;^a-@&$AwAEPY4@Qp@^8Aet-{k)FhV!Mr+unqrUpyF&emi&p_NSA2i{H|$6!LNJS#thl^WMvI!`@hzle<YCVib+Uyyc5?O>0~^oSS(Z6u<8FZi2Lv<J#712hQmnJ|mtrf)U5a>?r?x-`%3K&+n4<A54<_wuWU#{_7jW`)dgQ!8ypgerq84fUTLc`0aC^qTf~<gn24@XsFzmyM}lkm?!t6?Rp^nR1dbvxq+T3(`uz=$1d<cuP6OXANF9o_}^9&zjf+LoG0B4#(3@-CG&())gR+1Wr*arX5<#^4}w-5#W=o-efG$_;x~QvVZ7X4i_h<iNjdu}E6(k_osdWE-;8)WuNwpXQ^t|mtDg9675p$Rf)B5g@)h16k$TRombmC%PBOmC0eg?&`QF4lbNMauc9#d}A7TEOuL|Zxf6eejes5HqBKu#x=PsFtwB8NjAKXUHA@%6eG9Q=^s)}E~_Z)G^Qg08QSD8cdxk62O4tmA=81I#w#IHF#z<gW3u{=McS~odwwY<KM=bpQ#<ORkeH}TtV&tHoEo=?Vsv9O`c%hpBt(LdjZB3=vPG0wJ(!u^%Yi++`uDE-WKay$BAprgzeX7+osF6y31a?YkVe<Js5R__ac$BO80nuE04tTtVqv)*arF44H+=qIb(vA?OobEzKQGOkS5Mwl;VB%#0G4wiYt>@--$nNiyvahu**>N7&mZIO2R)IxmfzL5TB6q+P{ef{9|^7(aE=?_MS{&JpZU5xWWTb4c2e~c-AB2T?g5dAP98SQ+MYqiAR(jEQb-4*E{=7^@U9vhyHk_YMu2FAs%f&u@&FUybf$Qv__ULkSmnJVY`M(^8rE`BFu-(^o3iTUYyTbY;4@RgDmn}hpeU+G&F``?7hvoT&9B5o7s;Ju2U=_lpNPDNh#*ca!_nG&aqW-O0>*vfaK)L%1ToP0hLj(B;DL3>i2UN%tm_ZW_OIBEs<%i*26c>b#&+9$Qcx>I@I0OhyG6!({U78h87IBb@A&E{Pz80F(+pJc=oovzgK<+H@a-fxDSUz(ZPN#15H=ZAUq(|5%A(Hhw|SiV+5JV(w!Jii3Xxve#z4(6-xGq5gnIwpCa?sWqFt@2{YKg~g%q+QnAz0t2)1<Sf-c5RIObY?%?@1o-pPt)%J{;tVhjF$=h5zmOn>!f_rYs`E1Tg;LB3hpCuwRL-eaWyR<K>UGo<-V;Q{=oXo{KN=Mfq(BqJjd}t$Y0;aN<6fwv(V4Iy+YB?Ds2(}@KmhV9Y-Mko#*2m@M~MlW1-6>E@tCe(vPf<x?&%vZ$RFup?~SqU&(m0rv@yM@^R7P*CsZ=_+3#`)*bUnZH&Jv6EMDpB+2?^=5WS5(Wst`SG(Vkwo=aNhxpCTA!uh_ypJ-DRh0Qmf4dg_EwzT^x5o7G;@92{!u_6pf%Vwi7v&$^#rRA(F;>dQ=acgbYa-4K%)jm+ZX-|Qd~^Iao@0H+-!(r6KhFUyi5ajzOi99dqHQAjXX+_;@y{NB^Q_+nNk7w5_cfDptzXJM%5ZBh^=LmcV%==JUd~VTP-mG(^+R7JpV5XN5`Wr!WxVN!yzSMW;<xV@k8_F0LU?aAHz)S1lk1>=-p?lQ6SR}L#Bc2Qg#5JKskw6By`9BxI-?$Y8SLk^Mm=QzZ;js|*R_7=E_ta|)C=cC@r^LQRo=8%>gm|(5A;v0NA_G!*hlZ|Cw^PSWbvELI$^(8avaXr*7ZgHI4YCOUuM?{sDIxN%oqETZc9B24U}*7262dNjQxCY`J)ntVGWU=R$VXU&Go_Xr(VXn9rtTyM3E3_=Y(!Je;b<)=UfN7i{C!Rg7x!ks+<dHk9&$=uhL7#v+dm&v?p?z_-&~lrGMDZxc<j){ajn(W6AFgf68){AC!XkcY}J!`eC{pLHYKVq`&IVnqZyia83M1mNMwiA=o!+vx^^-dUp6A4x>8bd9CdverwYXD8Fkl`a`b`;x}?f;@oEh&L7RV^WryqZO8s8<E~rcf0sE_;_P({c}ct@;<>C_=zse8y96n(<vS&Qz4t7cU(Br!P)~Fm>d9UP=d$On^87bJ{MHkhrM$iJeA!oN*OTEN(gFL?9>q|P?JllcV>ZU&+#bl2BMO8`{k<>Z{ItIt&KdJn7Ju6Lvo*Lm-p}@5E`B5be7xVUuu$qZ0#Bj53-;?;i$yo3{J|Lb-_OK({`A9$cl&tM^VvYZTE7?j^!b-j{$e27WBZ1Ejn7T-+Xr;QyxP6BT-Ww>%yEf-y)8Jm2ziC?AMBkie%s<ioOe3TN4{`=z4)!KBJe$jpMy|O(IfD8t%&?>Z(*G0o(Y5BY5h^u(-!6Xgp1$e`V{-}u)kz|v#pH~zfo(Nte3{42$_#<1D~UOrs|kCGG;(M`#z)nYir}2%c~jMKRZ?Y_JSQ`-b*`IH+p40A@$F4!MxC|3)aK)*~PCvU4wOYR}A9s)lB?0k2pCevOZsp{ZmwD)Uzs)?<q?l|9Ut~{N~rLc#k`t=Tg_MiQnSpis$8U2<I)^zN4Pfagy(9;Wk{?$#PPzTXG@J%L`^eT#ek~w?^K<KBVacl+RaQ{Ca^T%p+;%oY8f~Z|{^9dB*0aC_kx<_${-tVm!RH;vDeiXk53MF5}B`<M_@0_<uaZ{OwyG?eVsw{?$z-57hH6NB%!J1nv16F7uZ?Zz!J2yi4#0zL))%)f|oZd`N(QOepqkg%N*a`U~-!DI4(IM>LhZ-&W~w#39c$tS=2Wq5q7_a!T&2`5fd2weRA(`E$YF|31zK&p$)^Z@7zJFX1ldd&Y>eQr>pj27fwT-q+|}j(G0Pdy3!gxu}iAVd5I>+rk!#Uvry-_ka=YaE?E8BkJ*)ioC$PC-R8-!Ki2QUaX^DJ#oLcFTh{kO~$F^o*SN5i+K2b-0)mu>Y|-XZ^J*a67H*FB=UteDdIPduEF_vpVK)1?3M1cw5Lrv*{|5@=9K-L%~KP<ne80b#px^feUu^MH?rV;uqCP--v7@TA%1%t&h?G!tGJ&S1AoX<$wzFbIo~f_EB^oae)gF&-XnysM|-MAVt#xxIr!gx>&fRhhZtEO@!5Gm{91fN%!g4YabE0q4COh`=v_*od`KAD^Q{-wq3-uEPP>KUeg}`ixp`|1^T4-g)Z;r__UHEWcInr)Yw>93*C%pbW?ovA{BOU}aDnVM%;eXI!^4{>U*Q$b(I=P2b$dTY`O(9WZ<L;n_nsGCqx_d!c+cZkAMx4t8F72q9{qpWIb640hci;XcNf|J8xwaUPj5O}{Kn@b<Yi-Q$Pe?agMZ*mS+}gWf8hB>??FAy-DSULUpgOgsOK0i&#AyCtjpgyF7js+zj>qr`de~IJm2Mo#cyPKA^Sz`T_22>A*IEy*SLc7Lsz~JzTpP{X1sqhrWTd=L`Jsq;<w**LB9HYZ}NZq34hCeOABzpym6@+>RFpn-uGw;XW@7762GmqCjH5<&OkjSe9%t+{^)1Rvj_jj?^#gxqxz$z*r#M1hwC~y9hBeO64B1;tKeUEO!8|je>nQ#jSXl|`-6C||Lq9YvBx{aZ~eRr`H6iA+B1JY%1_8F@9)fAyRdG?9!LF?cgsH7cIpJqUz%UQeNEbmb=mhU=IzL2l&`c7^Ip-}c)ppQqWtt17^mZYA}<(Nz>xbHrHzqx6~MWnHpgB3`pQ~zZe@MziT4fJs)^tJzPRk??C$T8N4r*szgj8G|BrFbtzD>%dcr+$?ri7xrP_NM{~mY7S$r?SoYzqNmLkEJ50^Mee9YCY;rB0$`SfqTPYv&e_IK_g`(VQ(FV1uN_~5#2@8jJ5_sTLKXwUn@-?WaLgXmi?;Qc}8A!z^Oc;r8Bc<-b|jzIl=-r&92`7PKdRT_)(p#u<y3<L0el}yucUo-pSeV0=|>{G}2;kwa7<oVjS<G#%*^Tltw6o&UR6{DqJXazT-{G+aN{$zPl5Ak%{iR=33m2+%c-_>YO@7?0JR!zXUNq2l-)4Z@B^|acFbL6{D_<l%{!|><9djM;*#)!{v!SM6@s8+WmTzCFa#G&$j*_YeuHbuVBDTdGG9lkF#@gVY@&vB^d!V!E=$#)*+v%XhxzcKA3Ue;8cLz}zqBW`mq;k|KZ4f}#f6Zd=bIQA#KSL3-1c!v5@Yv+@=mGDHI{Xe3ev0d=}iA!5C&I)`*J*nB`{7@VE9OYLPi;#NGdrCXCt64EmuWv4Xt=ntNdq*R2-K8B+ez!N?58tSZIOOXZf#-2q#;0|K3+~I_6XoYNSR>cJ`x@h}bYJmXwx!6v#@eF;%6IRN^7+nU{c3O$=fly1;paSWt&a10^ZGbk_jNqp({#;`bN2JT;<q2%A?F=>*TUGp7Mdx3Yrn<#p4sp@cz?fYx%kt**I_NPL&kx2cm>Lr>Vi1VsE&4ySdZ)eu>kuc?>rdSH#ei6Vad`@EYBmcAFQwy{-kU8o>^8W8Sh#|FxnYZ0OvsGs~~R;If?uAn=R)8mcM$)eP~hV;CG!M<Jxiy@4dAum(b4SlK37;$DVj^fAtFDoYzanqiyCbT-W6Wu6w_gtRuGi_@0yInTYx)RFZQveQ7IvZ^!vQ+P^Opc~KqA17@#R@TbnyL_IFz{L14K>i4fG=TMqv!FfgUca--G!2DKzH`?#x5GnpF4mhvgcu2;pc`FzEW<i`s9g9T2T~|>2wj70#haKK_`QLtHv9}%f>CO479Q@;p;d|5>y6`;EUHtmj*7)9uYc|whzlQj&&)-QuOFN%8uQd_B-7|;Gdq(19oO{HyMSGfr$oyjN8HxVT)*JOt7=rh>5ewlz*cbKOcaV9^QtBz5yEY#6q_`o^d6I(m7_(5%rZ~*!jw$H>eHX$%CX0+Ob44M{GwT+k{;?a;-|kPvd=e9ZICNhv=a}aG%6M;h@)F8NT$l3}OTt0)pTt=4n@`UmZjnvVp0bz4uMHlJ_neJxqdgZB(VpvV@SZB-B;wrR4(d6d8{Y@^Xo-0s=sw!xH>;DBI~RocM0*DRjN9_uEoWz;|JTcKR@!-^GtPy>m!Tit%O-xkj~)B`xZLQ^uM3FZXufimwD-$<e($=l_^nZ|@czHUwQK+O>vzk_dlLIVoJVTaTu{%2Y&h>9Fc9UpltuY6L*(4pc5Ns6e~sEGpYC_$nI+0!|F>VC<i1GmV`Dn(n{zaRzn!bRf3XDJ#&ay&8220gXD?~TDC`fk!!1z$>^wQ|vt-zVeQ>%yxUYK#-ly%KiTA7(M~L4tZVKK5yPw2)QmqJHH{CFKK7PrV|3{vMf7oC-_cWI5ME{JxB7R#!bL5Nty)ce9e?@t}u0zG&Hwg1;*f+F4e;&!-EZ@H1{JCwmC@Ftvw#3cyb0Ye~@RCuu-+J<XL$7xX=hCNLP=3`_ydUfG331-oRs6=FhVuOz-G4it@3C$upS7Lj5B5^wh|i#*sDG)8yhpMg+JQWA;so(qT`=$1t2ILXL;X-c^Lb;$Ud%I%7odJ8|3&iL`Mo3U?_|_-qob@_mZ$r1&ROU!%6q)RIcDH;d_QSt@o0(X$gFrTQnfzvv9VRfpZ4!2wCU^deYqY@#cywMSoTZW_*du;ZQF@ozhIaBzqMCrOnCeM{41l<DcYIjau$oSES7whfqnk<PmGjP{iNyt{+}2PsqugHPmF5Ss`mf;PmJpQYJ=A=YerMth1#90bP%}<xj#+u80t9k81f9Novd^zS?MD34Du4{I<nIB<R#>d)SYCdyT}{KyQzPWl^!MUCLg03WTlbhW8@g>WwO$1<QQ@?)g&u@N>=)UoJ_t;eM7!Wen?aNjQWxMnwmoWNKPR;I6!}pl_}0j&FBDD>O{^;&Py#s&Py&vElDm$E<-I#E<>(FtwOFu{*79j{2SRuQ{0MLkF2yYxfQt!wGFuoxerb8C~8Nt(jMedWM8Te*_S+zrg$-RFj?s^@?vrTP4QalaI(^&<hA6L)Pdxc<b^cFbE&_Rm3Al3B~Pb%lc$qM(-aS&wk0cVMjk-!Mr}w|+KxPys!`jKl{O`7<PKC%veM>crR~Wb$bD&w$5VTg$CKw!hme(yB+ntQrcNTSCU2%G-b$T8-b&s{wUd?lk#~}JP$!d>ZXxd=M^o33qsbxES!AW#$Vt?T)NN#?OUM_=2dNXtN|%zA?j;{2$I=u(pec@|&L=C~L{_?w97(=LQ+$tll&thL`5yT>)gV77zoIFANj*tc`Um+X`7w15`7!wxP4N}#M)DQ%De409De`XWMDlL(Dr$f7D)Ka%;!ZThb*W9rb;(t!HON)TF4S^l7jj{0adKgDE^0n<E^-EH7IFsiHw*Nq1+4Th@;CBZ>YwDd<OkGS<Ok%dG{sTWi{vPBDD^a1X)rmIypN_>r|uvt-9XmK0aSl-0C^rw@igijveGH!Y2?w=QRLC&AvDDrbr@M`U$RE-M*W@KjohB5xHYv0S!qXdYjO)}2eQ(}<oeXw)W&3`P032@l53MIQ7e;`x{xc8OVboPQwx)w$=Rtn$x1Vmvy&ZZiY?TPmVbT}XP{;yD=k3IK+a85T#Q<hth55TD77550=XR7gIbfUv>Dlh+=QmMGqnr3GkE~DKUwJ*@&NK!nqoid46@QC<eAiE)Fou48_CP5o2VPfN_Ue3sr#wB$x4rr4^mH1kCBzekWW%CP-DnSlgUc&k}r_sX^O8?ACi?mBVQ-qwEUBs-lQqMPgDGaruYLjh5Uj1ovL!y@BFMdJxy^=YF2ViazScdazS!wYB6$Ya(QYQa(QxfY9(@Ya((J=<oe{+R2x}oD{^acPihx(Px1(w;+fPwWTm6XGs)|zzU1{}ou>E*bskyiV)7Ak7&U+#Mh>Sbj-ak3D_u#BAfKTr4y7(6E1gRYB?nWdlY_~DG{qaJqsdAKkT;NLQ@fGV@>Ip!ss7ZlWThI}pFD-yfvmJIS?PH46!Hq1;$74^<Xz-r)Yar;<S6Q9veK>OC~^W#@m1<hveF&otK`enX!3jNpVVlw(hzc5-l;g9BQ%AdlgLUhl2gc!s0YbPW64S%kROr1(-eQAMv|3YBP+c}{zU#keNO&C&g2MF>_mM<R{D~xOmQyiW3n>E*&Jbt(^GGem0lq$Q~Zs-Q{->tH`LwaH{_etRpguG80s`~4EfM6TSpy4okku+_M&zoE3HfRBG;r=CD$ZZpt_JNkV{YtlS`2EQ*)8?le1AXkh763G{v7RP?dLnqA7k(eM^2$zD<2VzD<s$UL`AyBFB<X(G(w|hLR7Fw^8?zmFnbe<Tca)@*46&nqpt-JhIYhWMA?G>S*!=@=%&$AL<aYQjP3G?nLcI?nG`&Q{0H!o~*Prxe?iu+Jc;xYbvfztxBy=R$7~^v=X^0xeT>5S*bI*47m_ZaSm#Bat?Ajsv}vcg`AF@*0t16dTIu8da@HWH(6;ha#|kgL{nUxT8><tT%M-*H>wBuH*#}o6SC6I<mTkAG{pm{1IPo(<EdlGO8v-bdE|JS;#t&X<g`3;7ESR=>Lzkp9=VdHcq?^3IW3ReN>hB8dV-vmM;@jrj-Xy3D~%^By-toGpQGL+pCezQDZWCzPgeSbe1)9!%kEKMQlF4tl0Q>FkUx`Cso%+|<jf9Gm0v1Wnv<NFoQGPFoQGVLTAEyx>_#n5b|Y7&Rwq{`*P+%Y*CDs0wkEeE_oDVB_acv@DPBY!K~_4Gyoek`T~7`opP(s@r|M*-N67Ky8`LoJ4e~>p;%C%wveF3hGx7`S8S)GAQ<`Fv8cJ3gOg72aX^P{hfn=o{$Z_Q3)Y;^;Jn}eA@j0qL`5gHGbqZPO3bN8&<OAdj)MMle<V2d{C)6nN6Y^VX0$J%*@>}vp>Sc0TUiguwIIAP{PjXr=n3bkDA64al`S@9JPU<7F((mK~j?f%b<<CL=L{|EPtW0rUN0{P5RF&ryV!r1@E<`Ru%|$LkE=E&al$wp4jrm+rn&QG#mCqICXT|v)VTyB8-;k9lcA(xQD^vUzeKF*}$akoR$al!+9sbGx6z``_rLH3@9Ymf=?o3nMfa*nVK(0ouNv=kArB)!jl8aDFkc*IWQ}dH^lQU7Xku#D1wm>apr79Qvo2K|Z^*Q-H`4ROt`4RaBO>s0emK;qEqn;uwJwy&8@1-f;LfuAIx`w=kyn?29HgzFcsV{jpc@lL3c@lX9O>rOUP_j}Vav!ocwG-K!+=`~SA+;@8X(Mt&axJPSIW7NFT!mVeTAi%4Dp_e6a#?Z-Y9X@H9OM$@d^E*bsp-gB$(g7QWTolJnaEjait|#P$V!Wo3sOr_i<3){-KpitN`E7}lk3nFx1=^Fw<PzXb|otvNbW@*OjA6OI-aa_7I`vtE_D`J=}Pi^>MH6=veK>Owbbp@tz@N#$$O|F)Wc+@5oD$3$RXt8G{tAAm&i)5kk63MQj^GM$>(W`6D<GabBYtGkE!>_N?(#6liyK4li!iQQd7xa$>|(migQp^ZkL0m*qNG#>`X32ElMs$cBi_L-N_!*%4836BWfLTBXU=2OLAB87-}!_81i!JII_}3<mKeU)FAR<@+F$$yVMh8rSasu<ag8?<agx1X^I^kp%2MQpOKX*&PaVhR;D<!BTR7y>Qk~(ldMc}Dt*_<spPLT#jmMxWTnT+ugS^ObL217`_yw}r3c7LFOct(KT{LQN}rHFlYi0_XK{qSB`Z^$o%)fiROMmWX^IO{^N|aZOHgx?)AFzqG{shG4ss6WTUKfzvXxwlT7+DR>_SuQN-ah%#=Odvrnn5XFu4r5G)-|yYJPHl=2#_Zii=Yn$i>OdRFz{n^RwbS)H`HliY?UhWMzs!IQ)})eV{46O;dc9rg#}maX;!*azAnlYG<<22ILmxTGVRfTI7mUS8_$Nm0E;sB^RLPCKn)Qr)DB&Cp*#<f3ZMSPWFYS_!ad%`4#yN^%40FIgWaRtTdV&M-HbcK0*y6A0Y=(_mY)vAqSCH(-beDt{^L&O<q8rPMt)aP98~9+>bhfth5igAGs&ho7|J!hNjp?ZADhvkZdE@pw=R%<zb2|QeCN4$V$tSm6jm8l8aFDk(Fj87a`}TDb7XBM9xLdL(M`~nwOlGW96YKwo*%xtz<Wv;%ZcPay4=TY8|rDmgENHb~MGkslCX($-}9G$x0`Z({ilgG{sY?bIEBr)>N9}#ne^gv>a<OP4Q;xc5+&dwV9^)z%Ogx%E2*Ty8qMvdj6ju_1z=OfBr}G|Lb4=_v@tp{>y>C>iVBwE^Xf`gS?w}{PmxDSv^I4JHhfl0BK0YN&'

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
