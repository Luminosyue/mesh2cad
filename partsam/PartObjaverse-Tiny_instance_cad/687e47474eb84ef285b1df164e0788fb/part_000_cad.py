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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_000.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_000.stl', 'source_sha256': 'c17731d6af04e9a10657c5e586be5d49de83c968723a73bddcc32dbe04c3fba9', 'input_faces': 880, 'input_vertices': 570, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08705919981002808, -0.2596261501312256, -0.4999998211860657], [-0.0012009931961074471, 0.05411675572395325, -0.0721973180770874]]}
GEOMETRY_BASE85 = 'c$}r32T)X57^NSm17=hV1CF$cV$PV69(7DO=zwCDHsF{=!K~OS=7bR=wplUftSyRJ%$TtaV;pmK3_JgSj<c|}TeY=2ReznY54Uf>ck{jPS<^HiU3zx|{}nWx)461Q>1!AgSqyh$Kv=)XZk@s+%JdE&>}0s9FaQ0}nSsrJZ`#Vq7+?(b=^Pf(sh>}ElTXbqReegCe7f}M7ul~v@6bN|I){m0uS3s>uz&rCt{uX|{{39cw@SHEri#T&nTDJGAOFiF*D$)_j)S7lUmg%Ozuk6K)NZK@zw(#;`uSr9_~9n??b);2MXi3Vu8EpzzTU2%dzVD|X(3lsLw3NQeOA-k>pnyJLgUppj_%s0zdJKNS$*Hk>YJJ#IHdk@%XR%;+w{oiA2ZTBzFgLHnG?6EzpJ?ZuDRQLy-xG;?dlt43Tb*{S`%FVsSQZKubbYlefkW&9{bZSNS`-!uYUGkrq^$7*B<F#ZP|-_y6f*6UF*TOy*jAr?OuAF*3+))n@7$~P(R=j{EZ*B>i3)<@6pczpY(ohC9lBWQw6`fI^~jn_MW4@^-GGDo6&8C=3{Hq1HR8}&BrJah;kcH7WsHJQ{TR7s^(+b`f-b<5Bs3`TPu0${W>D<!e9NnmYd<e1La^l3;#>_VO5VhH&XjQuHSGQpylZpeE{iQs^Gq+*tLADYj+~O-_N^M*HzH#v2R+7^ncz!{U&`t{SKIb^zjc+FI|31<6EN&Y5wL_N3~uoPkoU7{9fe0s*?V$?WHHud-d6=emUb3e$NGd_jO4B##8e#HtyQ2db}Ol=g}SdyOwS1)VC*hKcc_8EMCjO{4E~oof6R=S3JL{pO=nS-;qBV^=@m2avKq)zO`eI-RLioT3_~#z2FbIyGuW}cc6S4q=Vnug8E$W6Rtn}%O=&>K3Z-@P(IDyap#TtMwg?w-;*;ny(8Nlq|ea<?e>02tzV1vD*VS4a6M&TXt~+D?uGwsv-THjg(K*v-kagqPLJ!l=Ys1gz5@P-)@W}fCu(~zMNPu>3=hV5;_*A$?RE>&?~c>oHQOCp{wAN6>RYl_OH|)f`eth1xNuI}q4}r7dcQ{B5cpwZ*QL3h>@|@88()l1TO-srKl6p(Ydy-j(4V;9*LOE+KFLv9U)EcLQJyYaH>NHhBghZq*n*Afn=^T$on+ms_hqU+3+Z<a(SC2A(-Hl*SP$f%eZorBTX|3~C33=F@@Oa8le=Dz<@BNrn$MkAdY#5!bF`f}e($Tk@j7m?<{$k)+ncpU1Ehc9rtRAPc_8wC?}zl>CDFg`d7vFubU}KzXDFXDw=h18{<L0y|BuI7{>Gw>H_@IRsc-CCiT0mlR^PH99R8+3S}%szE!4||`tXlb)BCe8i$%R`GQ(egSntbxH5=Oh-GcC=yk?<XH|u@bc1%URhK)o2>UJF0*}abX#&!QSs`u8ToLhRpkB%Ox>4yhtK8~k()VHjurS)rsvwk<fU8|q(2I%!zD^Jn#cf?Lq-<tdv#@87KG=E#yrtsH>qkN3xS`O9#fAt;vW*lX^yQQCtK8x3MSz9dA`wG~Dd_HVZ-?A@Q%hUd-1<JYp3iYjz=Ar*C^ShkdH|)Rk^cTIBd_nW`?+pLQaEwF#mr?JH-=JKscb})}s$=}OJ6@=7YW17em%a9FEeBJ_!$|*V)FjP6y|?CXUlR$x#uT)Zh;-;L{XVT$f6Fi0j?DYg!|!iX-%`H3mV-HSu$F^0<0AE~{{$XWKjyId=Ib4ikL|Y!`Z>!VsNYI{t8v{$wVdtaZfp6NN0&wVZ|CR8b=rGQJg@#|5BPs&)pla{eS&f*=nj8z+-dbYcGLdrc=&3S*2BDb_018BG5;=D3ID(vq;If8@5_96@hbGY!>Z;Er7^!m&4zzuk)}7E6vepr%MkVLFDI&R&3hB=|7sugO|QzJ-pjT{KkC^N`53Fy$$eS<?rOU=_sNBP9yGyqZuP_Xc_0JQHy$@e|2`^PVj91Fx;V+l9C!Sj{ypnQ9e3<Y=Hk8<UefEdE_tiI<Ie%`i%!P8|MCIGsT>_K?+kyAcDsB5{9|>IzQ9AQXU0v0-ymQn>N{EQ&(?h~d~>Ddnm*evxX$0Z!jC+&M16N(^t*+v)wdnbbzJW^u0e{HPn!=b^mEY{+OCYy+h|wukJYyhX^e92H3H+?ryJ@UbuWz5_I$51#>pvH)wdsNit?OQ0PSk79e%`fw6`5Sk$=nx<P-mTiR5EhWIwCd8PFg8+$We%zUM%D2x$ku-1*U(Z~af0ucAWWyG|Od^)e#{<44Y5_`QASXg<5LV!hNVJ+3Ed4DRb$+|AU!@smm0zq#B_?WeYyZ<g!di=@+htu^m!db{)a<!Dz&{8cZyXuTLghv84|I78cG^&?o{wOtE8U#ms>{mS8*-ZU-%{>a~!X*s;#a0cz(9sb$7I=-5p{EGha{+*6@w$K~s7dwB}^0dvmuD)ged97dTpNF-6?E_D!Z@6XA_H1hU9P{wv1o*awR{gy7DEf8lUFw_swqQKz)mig#q#J|uuK5>h`Q-kJ@!{YQ_|0mK6yH(4IPNQWp!(JkGtr(i9>F|bxeL<Q-7{amzhfEd@#p672Sv@2d~8J=THdDhe_(w7eGBR<drquZ&4KDWqQ@cs%$;wf_6?hFkbW-mkKV8CQX}>4V|`G*w_fRZW$juY*V(L|`u5|+upjwS2kHB!SKs_;wf1Wx#*A`)9)sVlkdE_IW%#TYdu|KXb+;?P@7n_T*9+D0(6Yh}^*C`e`rX6#=ofFDas3TmYx^;W9l*Rg^WjoWf2%dF=feQ3XIAfAiu6SXO1W8EG{$<Y<~H~{Hefv9e#%~NA^Zc`w7pp$<kxyM4IZw(<75*0>DO>vPo)U;t$#Jp-?ehT^TW6NlZblxG#dT=cpv1$^ycJ&nvcCpGyHC!uFJLk47+toe>X!l_{*D()z49Pbv@-6>J2~O818$Mv$iX16%Sm`J8zWdpba|ySUfT!z0q0cWm{|P4{VK}=s0M!bQ&bTYs!|QzS-3Q|K+La`u!|V^><BAlhk)~Tyz3|FL7HxN1a0YZSMHph0f@AO{T*)M)cNvdT+(PA@ewlzsK*RpY}e7@#N?*q|e`Px?GPDS4!{8;@1^^_;s6p?_C$|7Zy_s<P%}Vxb1sa`=fbVu=+O6gXVo+SXbO=tiJi`Zj^tgWR!nURpkGAkp8Z<;W6x|vXy~<Ct82k%64VTmj`~**%g}pwy(~2md7_VopIA0zgs#I<G}E%_<m>(9XA}IVP{hNMuFmU^*VN@*YY>zxU9bAN;<UvgzK80t!fhPzr_H}$9OkX@7H?zB=WBjqwU6O`dhEZY&nMft6#+Uy9@Kxf4*sewl{n5N3BoO+r#jU4!SNf#$Ca_|H>BiO;;XiIh*RvPfFuQ<yPP3;iSH!`$ptbX12B;YlifP()hg>FVx@t_!{$3U>x$P(DtO>pNF$vzvIq)-0zS@Sm#$iqxWaYI1A-dY%AJNn-Hug7sVj|m7nAE`$@+zK9rw=@;NsM{d7+!^xu|a)i<}^sQ2%<R9oj+%ip8mPfNgfwesza)V}fT1FmyfH>`7<f|38`V@Ut^7OYPO)k1pn<?eF7Hrp)pqe_+FXS=XK%b~9a`ss_}xZjW<y>3U}CVIcNTKSQ_!OLO#dCdf^7sr%r@Moo)sQtI-YW<#Ny9>(mb}ZUY>2G?!7VB-@zZp9NR_XP;v}k=<&Yp)KcVEX<t4lEE(<}?rH)r?NboOa^ur3-s7W=?QFEGBH`$xxfTl@&5U-$w3j7Y3AFAP%OmI>pY-Df7&fpbHU&#(+=AE%PFT+Q|-xSr&nF(1`!bPd;0TYb|%V^5+UM(g-vj4h4ypOa%XzexqK?>zio+ktVimDaEQPJpI2=X@N8-+6)d(DM+==ju`Q?VRtdQEzb$VAzq5>(I&SZ=J2@ZH~l6>f2rqNBW`3*r#ueMEcgASeNF1jq^F@KjC*?uIn62@h^Iv))aU6ou=r#W8dh|{%w16U(*?rhU)h%{hR82TRc<XXZ&-ire9YF<7e$F$afdkN#=SPa8A|zocgv4iSUoqNKWk=#`qli_eNc{U77Ceg<pO0JjvhO*B|3>uYvGyF4ldneZxO`zT(K-7VEZ2jj+Bd@mbr6QLvQyj`-6kpLszzFMXI1`Rv=K^=0*|sK0CZa&4hrUxrnvcY6!17sLCa`bKzse@!2o0qfO>MEJ#~MQeMW8H(~u*a`o|H$6wP?b(L<4~&5C<+NJTJGKX*ohG(d-?aXqwsY&<Ahh$XzDQsFqK@<STEFXfZvVpre%qTdNFSr;m)60#)VH*st^L-%Wt+A)>+uZmyCk3-N`&IvAm7IY`n&nN<9B~@M!Eg@M1AwRwpeGb9*uGS)H?NzC{NU<mnYi!n-%a+#p`~-wi){gbM3kC-^b3@>*@7cuhW(kjQq!4!u@x8i1p#D@<{*Upq{5WY#&gct+T6d+rJd`;uLW)wQqRWnyu}mz#hzBqg>&~c=yzF&4+3`vBX~0b*(Y}mab>)x8CENFWV8Uce@|Pc;2b5UXQii4)rbhe#3ZsdkNMX>sG68s#!?O%^bKD>y1lGkpInHm`_WO!tVx5fnPOIugj6OG1}Yw5%3#yvdZ;a+v42PlrRYSr*lDl&FO)0EU*%;$1fS<{LeP5+Y`Nz&&%;cwfs9)!1!Dvv--A%?UB#;S?H%*-p@mSn6KwQrUu@}Q~O5zJ{_N}Co5w-y#7Lc%j}Zcj;(b&YdM(m?pEK_2>BbipJM-2Y69}vbWQhn#<oma&i0{0)weJA)_Kl+IXoq`Z*e%`I=kIFpV~KCM(Q|b<e0n{>HOfk_0xW2jP9WGpy65t`S*K?`C^Gb@{cNn{7ZjEd;9tb^Tpn$T2ID+sah{q*JQ0P>zV}kA16lX_b+zE^A^(v^&OpuA)i_0&ZqVb*L8YcWU&UL-}JG;pYs{l>l&;1IHJSRK9>Kj{nXg7{9J0^;f?*QY4AP$ySZ?4<P%&O^Xac0&`tva;m7z)L%+mx2}{)?>f5$9!gXZ4t?5l0-H<+C3Dnn}^4C)PraH&5AHLWf^Zqwy<YQZ>?Z8%Yz}eKkqfaTU+p1?tN|XNQV6>+e1J9)PjrnV1q`oZAs$twH`bEcI!<x$`z9~aZoU`_SuD<P90LHPwg|W^#;())&&V6_w)=@Q1t8c0P0qZFDtx2hUYvW3KJ$4@h?Y2{*`lh)H(SIMkxs}>CtT$T8_1N#<+MmXs9H{$WdzNoFU!8aW^ZmGyXb-KgX#VzN<J31VYmDo!d>Qk8m!8OHZi1eZTlz+6ecICh0l&}=^rs0W@qDRNBlR8ML(wmeMdEo=*IY>N7Kp!>U5n=!F<Ibm9gO|eymwk}rj<9fAKHq<Y5m!Q7iqsRy-Py>j7q?KlHnzu6W&_^|9OUZt*^E_QBIi_<Gf~C8LdD2^YK^*RhWzPdCsiV^fL;fyjx92dcUsvyT;U>m`BbHQ{NO9i}ir#E<6XR-xcXcWYP0C^T5;E4;;NaApd43FptgLjdq^39(?PxajGTS;W<p(s_?rs(Q|cMatV}Abb0vZ!hQ7f`(t<>c(L#tl#4&cjrnVFj@{Rl<5vwmPqTk_U>y~DTjw)VYyr#*n|Gq#H=I}BNcyDbkoHx-VV)|oUwv!*HGIE;n|{v`xlw(`&nMBI4?Wa%k=dyS(&s9Ka?4X5<yNdS{4ODS?rk3KfqAxRJIt?NKVV#)l!$qJPzbIk@|mvl9sg{@{8+0J^10-y{mQ!JFYH@`)5HJd0{?3kwA-ccXQBK`qrPk@SofZM0srA6p2OrxMtfSWzENxx)`KUT;5kE&q43ux=<^ZB!D#L8jy=7Q&kzgx+vkDWkIi?xApO!{tgo-T?M>r9H(?!d>w-Qvu(S$-zpg*lMR^wJ@7k;Z>N{Fy$GO4eu6q5J)pe1+u$!*0%(KdAe>8cOWBz#FWa@fd^KtBVhks{)_6x_uvDg<^GI0Ho_fTJp=VIRZd`sso^T$ls4`-`}^+UsR>RTc{px(p0vEP}OpuW9ddyFS{pJV-I-;4RLW!PZ7POsK@&i`l|(qGzzcKhTR)*)3^A^oEodVXk1cR<^}ee68=6RzU<(ybRb$M_lz|7}@})6qd%o{q)?k^jZbXVG7J-%jlt5j(J7m>Z6D#lXDq%N53R{5kt@F7n(N`RuSEpIPm&zV&;j`#ocDg6<b>Z))sL<IlRG>pI8GESN8b98ll3=n2|eEj&-Ryjp|wfdloqkZolo?#sMTeMjxK_}vAu=%>@B!hi0Cd1cB$)K`iX`Q$8%@$UIWwEy8@IPd#f6z3a3kI{bW)IoY<(C>1cMxq(_J;N9N@hsX-Or?S_4(}<0bLZLbP+wf1|L~1<%dn3>kfiGfvo#C+0uOY5X7y~UzU}NcJ=ZWk)<XaOb|25F3cP|JS^&>&&py@p-_-jae3!m@Ze-2b2K77pCj0^A@!To)bwV2d+?T1^-lE&+xMd!_6}~-I&u6UFKI3`a+I8wX-eMdxuWX>>p1t5)oWD%(h<3j3HSV|XL|#uVU1!?EN9sDtmc0-B^>c7e_QVDKw|xiX)2|N3w{ykOel9mg`oiaRAL@u{gmcIRCEz!Hj{QxRBs?GUd7$Hh@i-IatvY*dr}0w)@x17LFTB4n;Hvs&r-oQxCO*V@`?JGHU&$ZOulMKIa<<%<ufDC?D3rsHj(A>qqA&89kQL+ViU}#HeWUB$e)@e+U#&OOPc_uHbZd_G>6H`Z*1R;*$1T?954OrF=og-u;kyk)`>NOr>(I-eu`aX}#rijJl9q!x=MnYIoeQB}+}CUQTL+g$`kpOyKWns3#(MR*m-^Ont?*vb$KQ0Ev}brcRr5U<g7K>1H}se0H>RSze$jQE<$f&IBel1{f4y#v=D&Zm-k)v6Q2532<9xbC$L(qSe66F^|8+Ln+u2_5Z|28yfY+t5@7`BeeY5XuoHKU#j&*hBDoEd?7V6PwQ%Y*zF{K0gW5PXLf1Bd!TkD3P{2z1NUgL>;x?Ww1cJW|)S|87|EIk&gZ~2r}eOvAXj6Z=P7-t^bpQ7pGU9}wS<Emr5TzG@}j>O`aFFN<Ro!U39RYt$?`CHeIjvQm)m&lHCFeYogTP*{TkFO8bdwxeTUvKKBzPag7D4)RtaBjTFjC_{3;GF(jAKgEiuV;jxv>eYv3(v&!hvHxK9LjigL&sTLWJ5eJ82ns)$A{c_9#?le#>?Z5$tbTzcs~B5H1;n$b|RlGmvL@aVkYkEwN-sfaBG~mPJD7UwQnEW4(HF;mt$Wuq9)Rp+KYY4AW!U5lFA_eL7)3+J8ZaD*N3*Axsd+A9n9DB=ig54+bVa~`Y<w9IFlxQ&8Zj{mfXYmu`dJecd{S$9c>R_oxbMgB=pDh823-1eHovU;O{7eeZjq_Xjd19!S{Kf>pDx(hj>nx5DdTA0quX58m_3{9QEKQ1>*UGPbD3nZ5vCd?-)A-<Inf+sQ2&r)whl_<D4_!Fsxe#ZJdbqQyk|xg@UyFO~;qO59@^Yk|u><U)E(T{F-&wN_m<JJ;Hru=%KzfS3mTZmDjMpSk?sTZ8bXR--pNVO5?{DpRe`O;w8>Q&b+|6{{T-s-)J=q=S6cOG2bl4dxn-hE;xtuZH4qFP3SLYMx~_j_e|4uhb^KC`e}3k{QJ*zU1X2TqvMJFkURWL{y2Bp+#2sOg?<{Zez#UQuij7}`?ZA$@Xubx`#aGI+7C<<=fOW$3C|Cm=VPCjr#bw(>9Bu{^TPRUSbg|ap5QsB%^Txh`cmrKgT`aLiorVEcKaIkIg2cK&Q?1U-q$R98vfWtD7X7@c;D^JCiSfiMqs_@g>|(f;}E33ehber*4edxn?5#$-^Clxw>fWG3%%0wGGlH>?59`u!+jmP41ac{z6WI9-3ZS~+>XPq=z;fW@|?zVfzUnhtLMl28WF!^KT@Ns`sVgSu<rWfZ`^M&f1J||9EW*xcxANbLFJLpL%bhizws68<S<vHpVS)dA!2n(YTw8|Ma#|9=g{sn{;u)p_u(;EC%ihW&*P2q+qIqB&+fx`d3!$mN2~OChdEya_RCQt)VIXq`Hgwi+1sgoBkT{<M~WTKukv?>Z*{`HCdX(kf6Hnw_!~k|?;CpEPUCk8*Y_YCb?n%Gf5-tpaFaeqvo)-T_fN7<(E0Mmd7#mv5zZ4rhr;hL5zoDg7r?$|L0$E&9&YHrfr~K@9=)&ca~Rv4u?`JAgz+Kl1pIXwac+GqTCd-c(gyzU)tJXKw8uPBCJ?^m9^MzI?|vwa&vRq@E1X-{J&VBaTOaG8G0*TkqUG~Z>i15-`AWGvn3w7$!gubd?bd#8$c{9AhLc$LvfusZ8=IaV5dT9>l*6d0>YMHCcX=;izCPFj=>ykm{*IOr=%-&yNMAcV&3J3~Ii$}gjPZE}>+j}Uvm=c^YoN9(bLA<RM_&B~|Hxdt&(bzh%h~2%75<m;nD<xr#(T=sO2EIB9sM-hO_cwsH+WxUOAj5_Om{u8{;$|hedFdr)NkYODQW!N{#ZYBZ-;hxFdzI2kMws<UvM5{-S>Hf`u87WJa(ys_t!Uh!RPwZJg_Rp&#<9UXosJ0{S~L<{I+&+`1hk1;(D{;ccWepSO0NOJU<M1sPA=}_U(ng++&fp6OT)HE*#qp{^>bs)}@ZVdDS<UpMrD1g%43LZeR5I<&X87C2~8)fxtxg%>s1)Yu)%K?swu;_&XP&+(zMj1KXSuL)A}CLVM;u#k_IJ5cMb3!TG?w4%q)b?XJG%1kO+GNyjlh6t4t-R3EgrDPd`RYqz^;)?Gh*<I*{OUSM{6gMEF<G;L=_t+#kTaQ8hu$2R$%8>D}aDuVIz&`k8}3)|E;OfPhQXAkwp`TPVo_ybmIyE0epfc>U_&w=W@d_jA=9E5t``)z>gpdwmNKh`b(`IbH*n*W6-*eCgy#`CkD%XM90-qid^YX3+6)+YXF|L?~~s&CyNq4oME1pTN&5d5=NO>bE|X=@t)^q=}%z!KUV>&@&2{8CMHUN!A~gmG-cea+YC?1uAz1CLSOiEZGQX@vKPIluqsKaInCK-XO~y=_TG_{mrBUTwODhtv4sW{i_v4r@8tZe7s*p0Q;w-s6keh5gI0o$!|r!uy#0>to*ZTnNAaaGg(oyjNh`WrZJ*3-!_{8=mjaE(3qsdAy%fx&_u(6>`DvR15Q9!!77v=RfpSKLziZSccBTzbgp83E$N~zZg>x<@~re{3$6|e~!$C^MPA4!_hvbp}+qciu1hLbM*ZiW9<w0mMF}JPh)$af1N~sd}`D7Yzt}9UHt+Hc)x}1#I(C)SM?k3!TV+LuW;_y@O@|XM^44QxO;7FC#K#RJE6a%==p%H;zX=Bng{E8)JS-R@qAE8taF~cYN!6LLRwDNlBIAC6B-TQ{LP}*GvF}Rjo0(Q&v_s1Fw}Ef8lUIVrc+1YAF{MTIWNU|N%S$SyS)8cslTp|z9(rioy9qrd&ib2hX~Yfe8ko?e$-Puf7t2Fe^;|EM3v*JBX~aATdz*~9;z|dW3FERiGw;m7?0mIQw>>)^=FyqThjQM4(mC#<zo`w_ir~Ie%E<;?_=yxO>e&D(JXblvX-BX-)*)&Sp6r9^tq35Gu^&}P1F2qvCB?5-q?%Fmh#`-mf>!6>5%H5iis)z{m}pYKNag%>Hq4VidC)p|NT$JI!Rgl8;cmibE%=^x#Zal;px=&<mu!XYDcnYH*ySl2DLkR26+}kcnY-(c?x+VwI^A$A9*5qDm9Wkl{}Ln97i2Wjw7$8jwXvPCa)$Rp>8A}Azx<*zoVWfza!^zg1#h+W_JQh2v?(4B3C1~WC(YsHXwH=kEAvtiw2NKlE+e8k;jtfFoYLSJCGNU<Eh=qqJ7Bm<Tz>%avXU!LwGQ?F?le#4Yf2`^o;>-LoP$TLY5GAazY4S<KI`2uaVbNqsgM-<n`on)K=ti<h~5ymek+LEy<0kX0m8Ga%1wZ)Pm$+$>kZsg{gVSg~=Y&Y-G`&$R6Yz)b!*W<g5(gOjKubCbBElAj^MFWLI)VYC3X8a%P5bc4`K4c5+Ut3t2P^IVU+E)s38w{0l?42sIbE2)P*bXR>Gkaxrp6Y9Vq(a#e<~AGIjik6edZiY!`zT!&nrT8&(v9LNw3rq(0}lUq}NBa1d5w<d>C{~(8vBN)QNsLjd4$m6MP$)a7!<H-xC1IP==TNuJ;sUyi}$uFojvgjW23vy;BsDmsaT-6C7+?@K6EFnDH2_amBdXOw3{D2|6mO7cdmOOzvm@L|xJb@fV{gWI;9>fqHLG48zL7qgll0}!2Mc0u<50fX6ms4+(my@?Mgs)ORkgt-TP}4hsMRSuSgwxUUC8s0*%n+_g{exVS96}8viw-4+kRz#!$dTk&hHxVF6giRnlKMCK^S|+rT$eLK*yM~5_M*NgO9<zsz9WmiCQAtCq`o9e2)j8WgtJipCQArsramHz-X=>3J5w)_C4|2-gg;S_lRuGPQTLKXw~$|vA5(4Q$K-nq;rrAX<oo2C)Ny1{EBPk*EVV!REIElGe1_VUe1@Dr4JC^<At#V`Q0tR-kT)@emr!evmyjn@%aTR&ktdT!Q8ST8ks}zwov8m9;7;VG)aPW;J7fvry41^L3E?VE2;qv<Q)CHY6ZH^TbT?T-*ps@0EFqlV2_am7x{WL$T$s9_EV_>@AzX->NR|*T=7bO~NVStCgo{#-kwtfrC4@bwTgei_d7Ti#ZqyBA3E_;?c(Uj+vV`y#dW*<k$Zr|KkEwIXkIDC`v&o{<$@j_ks4?Vw<Xa5kOVk<UOXOtgEVAenax(b>bt3r!`8Y#3fjX6(Kt4*HNfwPGA0=O;t|nh3-(Uzor5+(aB|AGouaiaJktKvnP-Wjzf+1XwA>5f-jog_WO>IdQ?M{v+&!Ubb&m!+)2p^@6B_Ac9r_LdZE+C&L-=M~mZ;%}f;j7d*@>TLV>TI&;VDdTgR%#paR`L{va8GI(a!+z?suNjM_As^iSvU)IJy}Bd5kq(<bsTvoc@DKNS+pg24!J+IF}Xjv4MVsI^;dEea&2mPvS?v)ZL%-bgX~N8VF;V3ImjlmCp9ZsG!xmAoSW)O&P{e_2<N3{B<CgPr)DOLW+&$-dr@<ey~y4S;S$t*<Pzjc)L+P=MaY%N)v3kE)ye)0;d<1H<a*=)YE`nRA31;=M6E*(BDY`&cc9iMcOdtn29iaC$$iK}sIAFE$YUA8^Qd9udE`yh2(suf@+R_0>Ui==@?D1TE9wIBD{@XJ=oYf*S+az1W$FvEgm4Qdgm7=F>|uH{gy&PMl0}=7=aUanhm#MHZ!v`bVhB%V2sfk_AvYv{HK4Np5f)ub{z^VWoj^WAUcnHaMvWp*BafjDB8!e7k0HlWCy_;$lViy%soTk-SIH~M2dGcT2goT5;ZIcA!+hdr;cQOOpUI*%$=S%|s3GKX<UodSI5m<SPL83*l0_5AG33M4mt@h`<iq4+)OTdj_vB;blhl96C&||t!gr~k$#=;Q8Nzz7;|wlHl|5BKhHwRja7C(#T#;ObAzYQ}MXpNrrRF8)<^IZ-AzYs7MlMe-%@8g@%|b3gE=J8v&dmK)F@~@YRrXpw{489=86oUV{X~`!E=+wz7JW>X5H3W$N0tyS;EWLdg?gVXA?!iDNftdzmJs%&CXpqC^E)Gi^HI-`C4}=(6Ud@F$P&WYshh|W!daaW!aq@$kR^n_(wj^c9Yy|1enX8Qzac+h2w$UiB3~n)pf)9o)+L`H@1s^B?;~$x2(P17B(EbcrJBg1p5&$EWz_uSW#r`y;Z@WE<W=Og)WT%ZLgcmN_0(eI_2dl<;nmcF<kjSr)S_fj5AsU#VrpLUV)9Ie@I<N`c_Mi<H6vM6_E)3%S$GijEm=bNPbY+MYwBaNgz)dw`()93WC`KlsJF-x!quG+!sV%#$P&U{)MT>g1+s*&JM}nOLfFL#A#6|+$P&Vz=^Z7DUL=1e|KtR{L6#8C>Vy#Xp*|%`2%D+0*Af;jK{k`yQR|W0k%uva=TSS8=aKhQqsgMP$ot6`sk_J*$xj)=Z>dMgZ^=&1(DP)`8)OOL3{(eMLO7!{LO4D3Dp^AK8@+R6(XHff<Y&|=<Y(jy4B?H`p5%?>5!Bjb(JbT<<YrXaYc=C%;o?pR;r9k~C;2@&i8_ZY+Mk?6UPx_2UPvC!5bjKELhej%My*X2^(8kWH>CQI8<J}=gsV_Z<SOJcR8O*KZgLrNNvb=!B)K?4xHL5{xiq;fH9uL@i(Hmmnd(ihOs>HYu1hUJu1ju2twa{BPHseQO7$l<C5JGC+fnP0+mU-v1IVI5<R0XK)E4A{<WUUa`P2^N`Q**iK4j4$<jv%B)Uo7q<i8oh8JwW=$P&V(sGG>5C&?1Rb*OjA62cvw5W+*KugDU@)2Oo75*DpYo<`nDZ9(2iPG;yHjM|(0f}GA7I-e|hh%6zTi+YPJAzaiMAzYmL7g<8MvNJ;X3;#Zq{Dr)SA>4)9klcmrO_jZwH}wozLiicI7362+6Aa-s)M?~3<R#QGWYJi%=t{Ea0rC>^UTO+?FZm`z_%-zt`87F*6IAwE!lLEKImi{Lf#eG0Ack;XYB;$sc_B51EP9wMdW<Z3lDv?-f_k02g1ns}Y^UBO+sUV?56P#=cNoGSsj}DlNG(W~5YA1n0$H>yIXBszT81oIlI%{-K`lkjLC(eycA=IdyO1+ctC2-3ku#B9sg=p1(!O2!S@;Os{2uZiw(lbh;Q>@{@&NL$3}IKQv~O2_7XFKE{sj31+xK4#;nUP5<Rxscry0TzsW-_t*<K$qguhdzjeh56;a?cSwWt-ywa6A~5IKnL)xr>tqAnyaWc!O^2v4AHCvRu_o4^pBOFd1VOFlroL*7iiOua+CO#VRqNEVg$_krq8c4yoAz;wdTsoBU9!cUwK!YNc2vV`yzY9?|fwx=s>TheZ>u>A}mUm;JT{z{%iZp#oZNp&TcB!6Sul6Lcr?dLT4G~2;9>UZ)tavrt`X$N^2!hQ_lU}`OLFu5PqLbkBJ`%x#5C$KL2F@(oc50HP<>v)Fnbn0dDbn-#!2l5Bj(?N#tZt4^A6V}sihVUBd74j99`x=IDFKSzITb6q-hOj?X%G95lhrU0{v^~|2?8kC!&k!C+?MLp%vKUC6P98`eLp?}7$a@<@T|-{OYaK)NC;Ria$1u+^{M<Ca$=N;K|LK1f@IU{P=jcY7|8c<o`pvYjji&x)nSU3y|Gh-oG$4b#+x739;;avCid*E<{{U}^vp)'

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
