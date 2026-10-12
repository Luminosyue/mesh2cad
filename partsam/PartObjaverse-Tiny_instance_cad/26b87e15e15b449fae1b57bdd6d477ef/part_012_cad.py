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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/26b87e15e15b449fae1b57bdd6d477ef/part_012.stl', 'relative_path': '26b87e15e15b449fae1b57bdd6d477ef/part_012.stl', 'source_sha256': 'd212d5f0ed342a0a3bdaff0e8fcf1e17f4f5649b48e8faf314e30e551619f697', 'input_faces': 986, 'input_vertices': 586, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1450163722038269, -0.05687510594725609, 0.05154353380203247], [0.09403236210346222, 0.28427040576934814, 0.1610463261604309]]}
GEOMETRY_BASE85 = 'c$}rZ1#}fx`0hOkP$WPhcmrW@3l`iDF2P+2oInV!!KDoD?tbtf!QC>!wNSj2(!r&rxKp@!-{(1h!neM=)?N2@t#>`Y^JJerd$!M>!)pDIc=1yk_%DkQ*vuN)tAt@lBsEeS{X6vO+qr#*hyp!&4e~Kks4xF{bynRbb?Ue9G5Q-ra)ot>Xx}GSX){;Z@RGTL%v|9;`}FM-+M{jHK4BfiuNK-ZqC>17(J8c7huF`#i<K-MWERO2WDYa`FaJvtTLkO=w8PP{>e?L;Q9;VowEQ7a=TKYqt>DNh`uSKYThtnoUVZnZ_ebTkX+1ok{)IO&;v4m|ESAsi_wO~m+2)-3u6VvkU%Q3oZ;U>rzBT0RLCwEquEYBGDVvZ_<M3npdGccYyKC+&^_?OISL^31XJb^4^+o<u6CcrhXRV6X{IYdb-}CmG=Hsq%Q?G0HY>)JQb@r?8)Y0p@ZZ}ikUgd{!hQ31jfi>WNm=~q#ejTOht)njFU#h#_r?L03mdBl<6v|ns^l|koX3@X9D*U9rdE|_y^E}<4zPp$Y$}^<XHuXEE(EBitT(|YQ-KwHI%*T9uS$)U<vzEgX(gXR-I-<U7?>5cfG-p5)>_PgI`*-U7+--pTvn*2I9X4C@w{JvgKKAe#$mjjEJ(}*Tq3P|_Q`9%?=$iUD=)dT=zJ1((tkz5E>*y!9#v%Q}VOkGP?W^iL{RXOURZ59`{qmt5TZAHg#p2rDR`FS==d^WE{^P&x)B7Ab3GFq$60Z9u{d}#5n1z~;5mOfVB>JS~bJv`K^dEeY&yvG>zwX?XP(Mk1aKE<(>u2joaZT^8e==IzxAm8mTJBb@)OXS@RNu~+M$7N17K3&VuBpDU`ZVr0IvDpAnpb^mTkVZnzBcbPAA85LLz+*c_}cESOcwg@^6u(;UUt`U<$1jw*Zrr1`i9TFlluKW7ttTqH-x|WzV=sF$}`A6pgQ~~|KffZEk!xEmw;cQjn=2L>?-beu8Hd!BekCxfjhK3t~=?~H&>-czs)uW{qC5L`c9wDd(fY|pkIYwJE-{#@zc-NUm1{o#8~)l`&YeQ(=`}h6T7PKD)8vEejXHnez>@p`ev4-C$yXw3+eUk7yd}!GQ}t@=L8S#YeGEroxl9g#m(Qm^67xyZ)AsZ`u7zNF&>j0K7jF3Yp#9{s)qSzhK2N@KEJ5G`c?apRk$hq>)CZavCBrHzl<%SzTL8b_7m&Q<HK=%XI|Sgnttpv%&VO<s_*Vr@x1zjORMkRnHuR!`=8QuZ+=ES%>Qq{`o2HnKJ#xvecpSczUxpR+UapH+A+yX_3b>-xc`8A=nr34sc#iqxk2+k(F5&uaEAKsgac4-6_et7cc&oznts|3-Pup!y8H8>JR|RK)pSv>Fb?tu!p}bl<FrXN^yfiok$=-2S`W_k&zR36-|f@-yjoq`*OlZ5`t!Bx>f7V`Xg#=#4A%Ph?2FkKw|}~-rav0j_s&;VvpcwMt9k01>E~-bTL<gteR*0GRNo!YP216xxi#u_buL`D)}eE8+r?RUW3T3)?3|Xzb39mmE6on|Jqsq{{y%+2{|sD!^nTCvem!qeA$@cY_3iSL(4WII;eJ!sR^KVN8uQVd324X4`Qe|vq~&+5`~me)@Y9~S{olj&%Sd$({)ldx&h_RY^0{z9edA$1?dQgn>zGdhPQf=n<kS0jI2ZHP?>p6Z`@h$EFt~0yb62Qu_fMhY)DyW~+tFQOp!(+3gy{dJ+G~9{k=;<9{P8uNUF!qNdA<|UXS=EOU~rwaT&>l&dT+(}nz|F?baE4vr*Z0`di_$Xu-@JdM*2&6&g$or3z5$`1LYjCNc*|#)Kx8y`}6JHntt7y5n8T?8MK~^*%#IK>`18l0ndg>NWW$=(x-f({oK8&mG(E+<`M9dK191;3Pb<d6Ry7bC6&(4PW~IX?|zNcw+B?wdb94<#CT6uMSZ791)UF#5{b|sT9ifpmp*BKHtH4D>l&+zqMT1(YW-N(Q)1nJ9)$GGPUyIB$F#tH!M?jo{qY^Ne(XgPuwIuwsJ`n-LCg!A<73{tkr)2pCR%<o(Jd{%kuw{7pB%cbnaz`9KAe|MeNT{uc{_K0)Mw(P>O1ucpd3y2W8I&8dZ*?y)UxCDbK}@__07C1wVbZrUGVp8jgbCXZuGzKo0wONWm4aBcRtp^jeny)!@lg$>-x0Na(Y<Lc9y@@cXj)3w0{2k*TZpr&;DpFzxgIN_ATA-BK@GA^YpshFFAQHAbtIIdSBLo0+^p$Y*pW#VU+fN*ZsX%_g1e{-`GB&nU*J?|Kaca<BL#^XVta;IJ+a%w~A!Ie4At>=JkGVq;H*2_YdyipRk_)QWfcwx%=vUH_L|c8<lfM-1;<jWxzVM%Ma-*me&1-m3ImHvu}LVTd7-GpRVjl^u9dN&$ny8{aXGP^oxM+e2*Q4{=jkPdACb_qlUd#?<*=7%9&}q`sSiayEOfoKB&LSo7MO3KRxjmX#X+)Scdd>o}pijxqyCtqC0%<L#%Q)G48$=QQztKJN9{nqA@@8&JDlC4?54duk6NtF#L~gTF#pRI-k30uRuF4U9P@WZn@T*Ieb6n<DaJ@eT5e2_amAej_bRfE2zh$Y0>{*rd8jyq>f(KYSYb*>sxQ0>U|k``lG$Fyx*$zoH!lYdwm${Iqin6=$}90`RGjm=B2W0)pzGFj^~>CGjQF@^R}YhBd|~Nt%iD9*ctiw71sMT#+8KclTv-_LEr+t|KG+PiR(N671VXy_IrYI)k&<rt5e7-&7bS68U5cDt)I%a_D}m#HneAwx9ZzxCTY7n&1=Cg^iq9m-=6XM{eo$c|B46dJ7bz-{qBhM(KvYr>2J(Lzb&`uXk6dPK1S=o$zC4m|GkCl4&R~e=&`b4-0j$cavmJiQ_H!w5&FxGjYz*H9PKsqZ}d0+2&Ct8gyDVO9NiIq=G>v^*Im$0w%0&8dwoLtPPmNck*_ZJDWkgUb<7&*hqX$<pM9j4=98)~*1NfdQJ%nsJ@q;zqwzd+%pdpr=mh2q?*Hva4>xOn7`7Jex8w!p`7;;PcRhNi<JaANC!W)vhpBJgu(AK)dg|F#Tz%t9R=u9tXg%g9--1YQm&Cp_cpAoC;S@-pV%kLQUw>BA{9R+lY|`u2`-t^%T_NN@xFmebnW^a)9M|>M<)24=qoE)6D^12>y;zq)ecO73@mT#0>bcS7DE<Dgb@BXCc?;&}b5ZKMwhTu*7S4tCI^tH}DOn2jWrw3(*49+t4r;JK|33HazPP@-|0eX?Q%Nw7E&jYw^B<jG_jT^^c<yil8>w$4xvBlreYqLZcL`D7y|^Xjhp8j5zEpm=LH$yHWBk553jfA6_3f(D^_;<Z|2OI{=LPkhqpwlFp9^9BX|ff5!XfD2o)Gl^jHBR3^}v4hR0#H^gQ}`;j1SiH6Kg>X#@+RV@CTOA{hljnThv?6_v`h3%Zyv3<>B*!y=A5PR@2cKC&MzMJ_qze`jARfHQkh?Jjdv+zG-|xIlb$9{gmo^Mu%#Bde<pek&o-Neu84O9nF9LLVq~@M15m$Z?yZ4UMPRsyXsqGjt|lM<$l;|_Xqq0OR*1GJ{<K^W&rXTu%&^fE87?I<;9NhFE4ZH_l}=F_?;iLwV2+=m3r7;*Qp4<%jy=Ie#bDhW2#i@n-d-FKW^5uUFmhC)=yZmKAOJzUaa#s?y2wDkV@B6cfm>Mr#b#adY^F2hffEf9_Dmb-(7Db+V{lf?|gewXKhD|zI#$eq`&qY^>DBq%6Tm{(vMCsM*EAMSIc8I{CBPTjXPm~U-TW?rPwv~J<o!+>vao1z<ni)P~Y`#0>(wjUYN(a6;t1g{1wkTe4cgU<%GZL8pdsbX1L#lX>r{iucm9gj-9RZgERfq8m+Is@zBq1ros9Zy<UAgU(HSGN6bJyHCu%AZ4P7odRq_UXnr;IJ?VDO*ZjXM(Z8Gb%B%0bmkjlPCojrb(FggTOOO8a+ey^h?=M!z?N=7ldk)-C-#s%L`-+rFQ4fvJsP9_ee1+C?s;E72eQRk)Z7-*%FUG}}G4KbLT%+aZxr*^~4fQ=e3h&nItyqKoK!Z=K^nQ9DLOD}KqTO#TRo^~%VToSvLT0QFdFLU0lJR&RU)2NaTmNb5JI+bWpSKoc9eLgf`AiSTK5t@K%s<nwuGDsX7d%tb@to>^{EvgS$L;@~Tqo4GPIf&KcRYGRTB+~O`Bdja?>^8OTvmM}&q&?3Tjf*W{NYU+<dZ85&ucfjp&wRE4nM}D^>6aI)pPxe*1P#%YdqIayNu_FgbvyxT_@~IxK5cRV$^pvYoX`i=4s5I&enzM8yV+z(|q#qd1uZj^{vyd+i5!Q{B|@9>H8e(sJ{0cyFnuOZ9ZzhwYbmsEH>cpd)QFxyIm)&*B=ir*Yac<i}Qp|y>LF0xtaP-hOxu+dxdvnJ@s{|Z}wWC{lwkH!900CxBBj4Yp@@#6N7pfngRJIpN{plULV|V&dVOXub-P^pVYTB#$S?y@HzjxR`14spwn>mowa?YXnq&6qddneBK-+tt){CTigDjMSbcM6DYRebr|7qnQz4%Ri?QF}IgEAP5BWT4tL<o(%!TvL0gsnyebw8K&pfBH%I$}r@iLy5*IdQ<NxUiQyU&!t_~m?So@t}Laj)1s)ecp$AJ}ztsg^VT3GL5L-~2c)_vBUI?%opZ@Fu^GYr8}M(w|9;^V^~8aeockEzxv|G45O}zcHe+`mX<$F4OYN%Ykuyy6a*s$CD_umz@dw#yL+GYCfMY&eD8ZA3^(A_0=~wt-!fiu4AaT&4uB&eTaQ>qE?vS%3RTXkCozQ)MuM)c#e*@R(&Ja;?4Sb<qgam?#@WxcI7xtKRXMa-*cBy-!2lO_2Q&Xf&OzSAM&YH`!`MJZLg5?I{&)H6v4T%ode(VU#`A8>s$0g>lyl6rIAR#!Nk15_ZnW`ir@KymhXHzjEiMeFu!v@U<bEC`ibkcU7doXQU8Gs&Ii)fRo`xk@osTmGL!kJ?;2kW>rIvq$Y<4yxtf2C)dThWA4AYCW$&o(oj;AnneDi~HMH<W{hVqR+GW8i<Z~oZKdpyRyYZYiwVC>6)s#55Y&!|_SjJCtG<~L~7<XH{;T$jICj3<k>S+4m!?oWTNAAzo`<m0VpZ=ZmgE?Wh`o@*pXpc@+(BJmVSKs}|LLH}0ol_X6Q6cJk4yD9<jZAOsxW2nzB*y7T1NBy|toqj4+E~~8@LX(nxiCxf**9o{UcXWX%->Cl!>>_khn8o;ER4&4a;opTmRS3bQyKHQ5%O4{AB<MRaG&-I%x{BFt8aa*r~ScuUTQ{efPb-u)|0D8ULDsSbLR{#ztI!>&m&K<?mQT)zEyn~o-<!;M*H{83;)S&>`ODnVBb>uGxjTWBQQVpN{D%&ab@+L{tZ2vzVkq=<D;{~zv-jx>rVCy`p<Sp=S_2dR*W~khq5b-R^JY;g#F0T7g|qN-Y1jwe*Rgh^<%SsoLy7YcjE29{_yQ|^p}g5Cu#XU|Az7M0sYn!@Si@vxv!U>jd556<&5;GZ=b7y_X2$X>s%S3zO|x&_6NJ`1dR8v9LT5c6`aE_YK?hv<`3#S`vdV@bzwW+cfB~N{lH0Ge2bRjK^E*!H`P(!+;R@}-k~qn{T{=|X+4*#iT2&&!TS3ttNO0UKs`@z-5!B?sr5|V*P0*DUyc95zVqET`ry6H@gW$eYxa%S`#N9X7tN;}-tTyQ&+CtPPZ3%c^MGI8QJTL|0r^*SFb^NwG*Zh`-oLNj&q?gVt>o86U>xr0uYLoZ+c?d>TIvrfGC;4_`ziJb_g1Ly4o;>0#4|Yq_Dj90S;&7r=1smgH_j(g-%9re{a{Fcz6Y5*T=REjKtH)z6!n%q0RFx5t@V05AMg}vr{@Kp;V~H3N#3FVSS9rQ-SZ@0gnn;TDm*WgJ1|7cnYVqUe)f*XaWe*KIj2`0uiAMS#(Qv{0s48}W%gs7Lt4+G`fGm+=#6=0@;ban>bzU$FXzc~T(5ar-1ow&dhThyub}<VRsTjzT;JK+0nfACkGb-7z<J8Tt~ySQ==0czSIN*tuX{b6o_`vA9yAYS?X34(DhT^C?|aW@TRLj_7e{D6G`;)e)D6QlA7iEVE0gcDtkY>)>-AduE!X?`cPaJ*gIk7ZdzFsHbHm_Jyq^!QlwYrt?g7s0PNl>1SGKcNG{15YdcNv<*aYLNZo<au_dBWM$i?$v^Zm8vdc6Uc&|kNC4#)L9m+PO8JFe}hIc-%-EuW+Hn7A(H|Bf+k^!riY)w3sGk#^99IPc(jn!UMQ7cEa{0<=fgP+a#?*&h1+hKncZ_got>URo5vd0eluTK^uN&zM8}dh7RVPQ*HLrw#i5qkVn!doz}fP)&~WFt2YnsgHU;c9HMJp5b>bgE785oVQ)&vgx{Oea)lmxYIon=es}5>5uV!0Q&@EJ?6c-DfIi+xkZCiGp4{gUTK$pHVz~V)%*we9*pbTivzF@wQY<2%e=s$s>6o%)_#$E688Bq4Tov^nXk0nz2}gg>NRyfGB=kRtNr?!pQd*T_zu^<SKFrRoBL}5?6*AwEX}9!ymhJ($FRQNeW|`{=Y;Rx6InY`YCRg}b!}hEd#*LQ5d3GIuy0Lr62AxO_89ek{AZkx@SMu)oBNYtpIJQ*+V|yOBQ;+m82$d*V)T>3oA5p+Q7GP*`S_z9*Dsl%ex`kxpLwq9^_`w$@f?@#4B9Kf_KA9(>Yp%QdFS)rvQO6U<;{V4yGs__m#4D&W?-Qe`hC8y^gK9(^iyWzcSk(GHO~yt-#=M%Or4Ls@13n}h4h@u7?=?ALW+6VkBz9OzVpv8yr25o596y&%rx~MPuBN|cCK?6UvDC(s}|mj`I_sLWxQ42{=5PEjeja*f7Q3)3@yi^A{f_C!cm_wKjAq%Uu~Q}5ATEZ{ZkF~jjFfxcQW?e7Z{H}%tiW*rSZJ5yClxFdahRA{G&h0{bV7=k?W}Xu0ngTUn=ts`{%WnW}+Vjq5o9Lf%C?;8}#|aJ-Ub1gT?0&$FI2VGmL7t(0_Rz?)B}4ldvE1Btg5}Y&;wNYLecUi_a-`)iCT=?5$c)W;V<-?x+al^D>$CcO%I(JFah~jsEVO$Jk@TFYrRgpBWH|etkHZ&V$zCTR4A6HVgZK&t=rN<EL1p<F3lvJ#l^S`$1!3BJ_tPgVZ-xHVQ|7T!C}HJFk&X&Sf|^+foSo|53sEp5D${SJx$HMop~CjT_*1Dk%!<KGevVX@6Ybx!g<78*Pq9*U2d4W4ywC;@v3puLWoEJAm^ybf4k`KE=GTDO}%oS`*Uaz4`nWsQ+TE@%t)Qzr%6+n`d+meQ)IbJ&eWoO^)w*_{)#uJZDr<%(v0i@VmhI&$0iW7K#4v9<9DJb0qeATS}rGeGjW|ExU<!pFCU7#ohZB=y{gAc3#XUYcivrU!G9k6A*~{9QP3Cg2x`HZ%^#6`8ek)Xg+q(TlnkV>U&$8>xI{Ma!k^FsyU|Bk+{B5_Y&@hzqfI9JF3s^cJKDM?!h*?4!id!(tW>mHy6_PoPzwbrHB8?7rzI1vr@}rjb5+5D_H>6b*_V6-+Xlm{mS2ke!DTb?k7Blj^G?GDh$8JxnEX&BULpmuXU~->L;+P`mTPv@f_v<^?RSc2k<`UdVME&4(8SE@3owsXA{&nzn0ePT6K<Ve=%bsk<Wn{IG^;MTb_A?e1dl1cOwf9ZHVie(IfGDu+@EZKWG+BfO+{=i!r!A{BFluoLYU?kfB(YGnB-8l9rv-x1U$ja|!3~A5q^&2CDDw@)LglP;&~NJDh1qKRra}2Xk-Kf$#jOX)*5i?8H1ad!G8n5*Pa6$NG5B`Q)bhp66AtKU;he?X~|C()Y%>pW%CTe_Y@7tQP9=%h|(meY4qG{0`)wgIJ#@|D^rW(|H@_+nGi6JjSY+75(*D5Z0yWFSuX-is~Ep4Q(&GayRY&X6>H%T~3#qon*Xw_u)q8vFf`oU&MK7`Lp<aL6w*Iy<=3U)|)eQjh=fM!MXLluQ9)&meVQn%MOh9>hN<X#P2s&Y{v84uDW<noYoihdoT<7L;Bn5+pD+W_X&^2Xg;0<>GZvnV}8YYH173=xW4zghW|dTA8T)*`fm3UtW%r^yuPuo8Gb*II7IVtch9*R<Lck<-%DmKfcIg89ITs9+OOBo6{;eA@0S=S<GNw~e^pz3PnTABzOIo$+tX<EGs^#_9oGFze`)=@QiP$L1?!{V_ME8sn@78%oLO$+eG2CvXZA$o-@HER=jC5IuC0-_`sSK@XqP8V@H@Chf1&&vW?&u&ypQoXC7HfIFqRh4{gS7^Z%F?(qxz;#JG5ikj%df$LFzl7j$z-!_0IZtnfk7p&5$3@{oH=L^|SlkL0tFi^QgGKCuSDj+x~9o{h2qf;C;rbgLtmlbp^je-1r*#_FRGIQt$7p%?5f7W&dyt=V@o#ZT`+LnOn<mzFC3atF{=9^W`Qn`2A9^VNr2?Bi}WYC+Zo_ac4%U@0#%l`&vG~+nbNVf0k6!TLD?N#P!{OEYRy(o0?(1>XAX8d#wfuagG{xLVbH+xcV-q8lFSHj6?l<PQ$O-5c5*z7TUf>@5kyp`A*~9@4#c7uj~^AbRX~P*c|iv@Nw8D`?OZy^NSzO2WGf%e%860`tJH!wBGC=Z=v1-`y&1OV9XEC;%&rz&Q#ypm=o((*8EuK?XAcsJR6?NLLOtjjo6FlicNFS51nCn?;V^R{kq{tEsqhe7@qGRrcvM1*bn_}&Op?|l@R!IQsF%#f2VD}Y_~pcdl{YkYI|ALBh`23^TYFC*D9$0Vz<_#Uys%204x3V195$`LOHZckPqh7C-;$l+w_I#-*~_5TKZIdC-fQilkbOM-APdk<7wP*>~H<cYCT!`L*e)7ulYJ*F7(^Ez2MJYjD34V9i0c<wFY7ysx%G#^U+w$w-=UTJ-j_h_n~f{8$0$YtTR6+!F<Ab#{DP}){psVP@Wt8&_CC-Mt|q~ao4Mm!{7NWOXEE(*9DI=NqzIc8f{O9zhg8r>_a=-foR8NtuelqIoLO~TY_;hIvd{az0QGoF47mzaeG#4xvkd4;HUo`zr#881KR6OE9}cE$H#ec-O`xfa$dvxuu*%^UL&iay>8r6-~RLl*KILa^KqX_t^L}$R}tqDlS*Q|l<BR$J;>0{&Mz1*uJ%{(KBLSyoLeTYg>|jyYxP~1|3Z1(qfm}teY9T9gdZ^f<O$aM@?@`$aZ-7=u44}W9f#L9AO4B_Sx#qNcl4LYws;?RW;^P+_6DT)K2I(2#W<RJ2<JGP?joPP^Eb!!Ek4hB&aXkg>+>UipIZ1I?8l}gLc90`sPEa74)1dd?MJ?W!RovIPNVJRo_KU4`g<|>36JZ3(|(EHy?cH4Uv4}{&p4yc8P>3$F>j@Bg?=@2r+#+)Izd;aMtfCpFyG$qigrFxLZ2rLvkA^U?4H=S@^?E<`9oSyuD%0sUGMLZTiwC@wtFJ-v3&77@w5Qmk9=5y^4E=rc_SUxHFMKy_&q!*|KO{r=VTX<&-C%=*L-j8#9Tx9XBNf$nV9Du)xY3=kKIQ;tCAr91|j%e+7F}gd@-UCK4<L$O`aO-!L-NNw{Pu-f9J#VM)$RB7+(qZqyNq=iSfQXzt*#H`w-F}U8VWEn^Z#kZu=9@Co8jHACfaveb>78@EdKxewFjEv%M<*ezP9VmxlMpzH4+C_8+(RW51Ml0n#5Ifb{JDo^nmKU5rBG(4M;*;kw1^;@r}}KGFU-0_)+U5jam+6pnhD@Dcs57k}rF{0Of9$6Aad*D9QwtqIWl%ms<@91w9@_p5f2U$j14^AlhmY<v~JPtN*C%Vqu70Q1<vmUx~W;g9p(-%n#dQaEUDh5Fz9YrWY)U61c6U>FjKjnqbXXq<nlC#L-8)&Kv0s@J*b|It6yEA{{WPxW&88b;pOFsWI{qUp&dIW<E#IW;9&^ha`XvJXS}l@Ii*4_NdW`4#yNL--2y53=Yj@)hz~hVW6ULq1AAOua`IeMCM?KEV+Fjrx@Q8~Hl*Em`y<`8xRlL-=2+uP<2i2eO3lYafL0dmn^wLZ(eePDswc5H3K?O)fw#OU*$RElCzFM=ndQzz{A&Eln;?EkrF%E<_HZmLLa_b1{UoQHzpA^OLiYGc$xUQS*>9k$<A*B<Ezm{D~p#PfbnsCnu#QCnqI;@qzk~C4^u2AcXHyrH|faU%f-VOTI+CLcT<fp`InjkoQrKlJ}8!Fod^K50kf&w^L7$Pq2?}X9(|M2p^<gCm$rAqCOx$V81-Y5WdO~zCnFWe$D=RgCYEoA^eyj{DCU{_ya!+CuRs|q-G#zV4u#&5H7+Hb}@v@Q_GUelPggxkSnksS7HcPjMLYJFT|GZW^5c|2w$VVBwr&xVF<sY#`gukBmYMYAd40zi>4(@2!HZH2*-<!e`D8(hp};uA^a;t_yqM9`2_g@L-;B~_#cMwONQ_l>O=Aua#A1YzvQ$&(2x8q{zv}(8u=sn&)C>c-9x=b-b3C+{gwPH?_n21cpF1_1N8uT19>?^cn3rHF!d_=D)0X=^(J`>^&s^oS@bsfAo(am_&4e!@(t=U>Lc<qasnTOu#XQy*r47fO9=Z?Z<24a+`<yViF^>k$*C{NFWHvD62d=GrTu<l2p3`qSM~YU-onkP`KW2hY1tR@@w0Gz>YrrM2W0=)NFj5B0gX=<l{AkT!qL<}$=?1H%@CeX-9w&FUd#|)K;1=NK%Pt8M&8E$G?yVfgCRVbx|}?YI*YoTJd3=Rx`VufeQRx;KDU-3yoezjNj*qD$UYaz5Z=TP-b?+B?Cpzt8N#Px<1+OQ^#=I{`{*5p@EeA35+A7a-6Ra*^wf;xhOtpRHp)=blhZRz8HR8GH32yR$3p<sAP11MP<_c+$hjE8d8vuWiP-P+GK7PvKaqpUl^Mb<sfEae*za31ggY^We~B|rgeOwNsLjdEIZnbD!lkJ3$?-WxN>TmErN}OZa1DlVy4ZMOK%Y|m$^IN?!bhkv)W_t<99P0~sPm}N<Y<mD;ephl)cNG0<l)rC<i#9&!x_S(8N#EebIEf#_C_&;hcJYDQzw(XV^X*gwI_8PxhHurbryLrc|3J3c|3VKbrE?CbqaM6c@f9w6o&9jhVT;VCh{hZ&m|1u^$g*C)Klbr<O{~P@qB@LhkSwTFod5|-;hOR3_s^*;lvE#)YSCk)Z`#)adL5v`5=aHC5CWohH&@T7)=eOHYAIdA$O)$qn06;;apISnuT1AT$3SOhnkC=i{rlzL%0z&nB0i`Gefu|wKBOf$A3qL@NjA;@^JDrhVTaJFJ$i=v4J7HlOa5t8b+Q??n*61F2%W^E42o>E4e2_IE0#x96}Cc2){MH%_DCa!Y8Ru$=-S7Btv*1HHIuYhrE#7pE{51ok#jJgqu@`lADv;FoZ*?!^xtf$)V&<4B>F<D6;4fayZ$|5N<*3P4><yEf~TT8N%gbqb#*PwGmmgC%Hbk3w1EL9kmB_Fj;gwxd(XwbvoHQ9|?D(Mo`C)MW>J>$RioT6R0!EqD#mV$Wy87$y3Q5>OQiEyqzI@oO*$Locuf0A&WjI|4#m!A^epp^VC;rYO;iIN``PYY7jXaxdgQmS+q5|1i7}4oOeUJQCpKmyOX<-M=^w_`+S@4rZa@6P(#Vy`ECkBxCgZwS+piuv<|rkIfB}V96=t$5FSbWnJn6oJd!+_I-ES29LW&gMV&?#-9X+&K2P0AK2QE9Ha=4iQFoF>XOquRmr!SuMZ1zkdy<z^`%rt5MMKDasdcF#WYIvfs7bC%u1C#Eu1Bs<%|RB;O|DOF!Vqp28!e~>8Nzv}xyk<-&`;Fd<lMZ5u!QgjYF4s@@H?tWmJohV4J3=o{QjOHe42Wayn?!ndXg-<kUWUmm%5NF+MnEz+L+p(EZUr0j9QY~oGjXgT#{UYAzX<XN*3)zu0*cR5UxQDCyTntHOQ5zEy$u3$(6}D8N#`#<;l6pLB_YWK{zY507JMOwJce*KDivZ4z&x}yJiU2qPC*8Ba8MRw<33>4j_Bi4B?j4_S9}<(Fn3=S90ChXcik`)b`}|OcTZs?n8|ri;g6VP9XOoThys!i#(C)Ax|XFW(aSjZYPT#CvPMlqW(@kM83!nzDxa^Ec%svm;8z<>&+{E7XE=DoQj%_ELwt`ikzQXo1C9qo*~@S=i8dplp!1*8||q>Vq*-o7d4z5&h)()!WOj~S#%WHB2QunucS^VuOx4zP9blh&ZJHui}oOkMv!Nc=Q4yBQ3sJlN0Jwj*HI^v*O50fgpW`o$)dZ+N67c7=gIfUhA;FVvV?FNUxaX0-*0Q1u!L|D>LIdsZ4;IdzDREg*}I-yWC$;%_91)Mv!x8-e$={T(RyUj`s9A(0n{es0px)U;lb2qWbYa_m?1orAv}yB+=^O|+=^T@HvFjZs0GQQdC1<iQ1}n(6{`4G7{ceNpUCIQXQ&^@XUJ!%@5pD#=cw<=qNmB{$g7QS>*8vL@G$B!vUgn^#t?2o?MwEqi%l59!PLfN@46Vw5Khk!&cqPTLM=%atw7E~&dw0dL9Ij<txnEC&PT05&PUGA5Y9`jOcu>a&P&e75DuW`CI^rM8Nwzti0oZEg;P;~qGl!gQ&Td8(@?XL(~vVWg!51fkVVUp^N>qW>yW+cu5e*$RcbA=Xe)A6ay@ECvUlATu12j*ZAlhwPZn)P7OhLJO|HTab}@uQVxuXwHMK5TG>qJt+MOCk7VSe8waDGc{TRYysT0Yfv&m!0(-^`lsT;|nhsZ0*yBWgAs29nicge@d*Qu|_*U3*9!k?+KPJgDRB1;JWNH0J6M{;I{a4~9mvS?FsF>)<xIN7^q3s;DZ!m&}ET7)cGnp~aSfFaz5T9I6l`L&_8C-<iIr?w}H4k3@Fj;9VGk0(#{`L?&1$`GDF?L`)~$fA?T6Ug%!!co+f<o(ob)Rkn>jpS`)+vnRp!)6HYrp_db&LxX3BJU>erLH6IB}X%af2VFHiyk5WPJTnZPkuvA<_nd5Lo$YNAVatqH4Qlp_YlPx!j)sADm5Q9D>*Co6T-pN6x1YSQQ1!j`_Vhe&*BS<E+rqQE~G9ci}oXn4j?Zidl<s2r~}EOgUPGNYp6rXYsl*v!fUC+$SbHLsKdx3$Ze^u$W>yaLu`~~2$!U`CAVezlGLK)lH_DQ-}WxT_YCM?R6nw4JhFH1@)tvRCqsBM^$K}2If{Co97SG7JwskcUPC=gUPE3*Jx3N@O<qMFK^;bJOZ}NTj4axOT%1~z+Jr0`OcqT~E=o>k;6G6xYI?G0CgXozeJjUf2q&awA&X`wCnP6j2&bUtAdBWBry!?h2&bjyCyVAKi)JLJB`0ABC!hw96OfZp1IeN$Su_<n8Tm)*Ph{_&=0}EbB5F!<BC=m>#HVsPQT~A;oS2%DESiR#n4Fv;oPnB|ESiU$ft-z6g6!Q7Wn&2EqE;p6BA21oBYXEi!iA`%sMW}#waKDY$f7QCDRL2pa6yJ}X@+o3Y6!U|xq<O*&(we++=1Gf?A<eUU<mi3b|;JWBa4nD_agto5S~PxMiyO3o<v^C5Z+4NO%^>y-b%Kq*U2{d5<~bt^$A(@Gx<LGHC6UNulZRxAwxI~H8WYX7&#5O0JRobv?5uwG`RpdCqp<BwFp_XFgX)BLu_QHmZKIXmm@c(Rv?R3CpRXyV+ePlHXw_(A$#{&T^PdSsQt;_J=Qpe@I2~x^5WQ79UHT#^T_j<W)?$u4s|Md0d)p-Dp_;_S#&;m26-7ncoQ{>yor3k=iB~F_%G^h>VC55HnONqzD@p{A$*Ryn|zM^Cv`9RPx5nWG+Fd_@^f+mU+5dMgm5aV?7dPkgtIe*OHl*Kf!uqQVhC5ERwh>=S7!*<h_hD{u1T#%txB%S{aLj*`?hKf;eyl@WbeMMAVWA2RrY6ze827667g@sr|B&ui+aeStH`Ixzf#wbe<fe0t|!+I@$pR^?|=8dsQLDvJOdct{SRyYzu)}+=kjsCxhXcU|M~HJ{g4E*j>Rr)zWOqDxt!V?{|gY0u!H'

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
