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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_010.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_010.stl', 'source_sha256': 'bfb887c9c3ebe266c78d9db898b56cf03d1f0d03cdae327617e8321d5c5f1144', 'input_faces': 760, 'input_vertices': 459, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3010040819644928, -0.4140051305294037, -0.16856695711612701], [0.2587894797325134, 0.2529202103614807, 0.0008641330059617758]]}
GEOMETRY_BASE85 = 'c$}r22Xqcu{P!m!dT*;6HF}F4Wb_Ro(Od8!hzKEx=sbz2(OXDX3<*gDQKKXnL1OjA>g8cqTXl7I@z4Ce-z?tqzURE>eVud9_cPzz=gytm@0~e3I@xC}qTpY7C4PUEvU6)FiW%}KMU<dn{(&Qh4hyI~X6z(8rGWV6zf4`;rDtc4zIIBGGR4trSin$!$7ZTy^WjY#YpRaJ{rm&{2ag%#=kGPl^xF^i4H%Z;2Y3%2J1pb6YJ-MNYpPDwYO2%J|Hps1GP0m=YIE_hnU`Xxub8TJzP-&<Thx~erWy{0_{#dhTg6Ym1wUVx-%VB3s@qMq4qYz39@A2MrF*obqc#Z;-`eZc1^oUGiLalkfNL!oe=qqqQT(U>{3gHe=6+uM$+0^`T~o!k6wiBAes}uDZizoR7V#G~m-t4iF6pbQriyQL*?LNTcVqNU(d&NVTW8&o=dyPCyi4MbwTQ2Gm?-(TI*r&P>8{HPzjZ_LZBs0AU)%kUazB04Z)u``HIj5}4c;Ojj*e2Umc@TbI{M~C;#&$`MftfOLjE62LHw@xyY=@0Ns><e@$jcTJ0kh3tV(<}I+yrLrCRuV4?9WUSes3*ZQ-M&e3XA*>=!NY?40O|sMAuvyN^oxdfXlH_2D@VNV+*X;CW*Ph;Q_AmUOhXkM~KwntQ;nTJEx3-ya~q)4gAvmEXULMLB<NiTtd&BEE4mI$iu}CH9K0xG280>r1I`t??$wk2Q3z_*%+YDQDfOwB+A7AB=R|k4kykJd@<Umf9!J$n}QiQvO=r`Fp<i^{wl|<?r^+$bZFD@vVD%9F^x(mq~tXuIrFa2~SDi*xpp`YrVHreC2i^+E>&Axvvp)RLapBACMxy3$sZ2>b~9L8*|PqbusV%?>LnIS{?q&P^m}VPQmluUW#-ce?h(7EsN)^9)@}<*Ba&F_E_$#9cm`NzSr)W#EZ5ZlJxIim2%h8y`=qVW#&sdTKpFA)hCV;-?q8hLGkae5ns=90`+)km!zZDTaNfoUrD(r*^Wp)m4Hz3t+n=THJ?ixctFy(3<wn8Hs{u_lJ2pi$Y-_yw1eJt&Y(TKmhw?T3yE*Ud9Ii1JH?Vk2fjNg>6E@C`7!p?lYA;|?!mW9yCnYB2a-=~;9T*oz5d-I{<y`c$B1F@5BE4O&yjn-<i|R{ulV}>BKxIYnhcWs+b(w#UztDjgk0aefqdp@f^_^Gea-mRP2N(^mRFAATY4Rr{Ma58lYHuv^C6wLAsENL{vr7^Qi7#i^z_d2<?kQsOZt|cfxqH8uN!i`u!NL@<xCfpqpls1`#y`4__ndGh<|h~#tp9|w7Yy7{ICFN&w9c;wDWe=aNmwM<IHp{Ew3T|?2?Gz(kksubBLFGs_hfx`PGpH(2fs&N=E;mD84>pPq>+mGCLCKhx9#xe4fBKl-felH;Vo&zB0lE?QEqN`cbQDNGB%gIQm73^iy?WA*3^@6Z*mECMdUG^Pl*>eyw@@(H;(GM>?g#(Ee{0lK!Oa{wm{(zI<qsw9lriBtO>19Cr@cUzg`!Ws&kW23W;c@5jpcZ)B+>=~xq|iLbp*-fpI2>yaeStGD(|N4|0`k@VVMLpyxpgY@ea#(1;zI_j~$1@Z4SmHwDH4qHa%5?`5CT*g&niktDhZ+n1pQtO|Q=T%oek#Wt^ARhBk-o{71_qFw@hM7-wTxv4f|MoPLYmSpr4uvPke66P~#r#wu`~Dx=RiQBW_U9s`UY0ICEcx3JEWXmZhO`&uO$^$@`yla+5@R-q-+7euFPoDW@>8m)^k2*K3i4d)hsH=J@uZBaYFkzEZwae{bQ<`h-FDu9`Ym!+`mGVDO8d8+UV{Fz_k{Sm;U?`zO`VH=>X9tI?cWgTkIKPB$-njW9{BaQ9uxht1@%&7G13noJx=<?{$$L1S!cpOUUa9FTlEm6^M?=a>vB-We_O(Hc`jwnF!7a2^Du4}`+)pA*Mfh1!Wk*&-F4SWy2JCq&wB~u!<?LwzQy^u<WGH;cubyaj0eWsMt_N~%u15`Y0vLS{&nAri0|aI`-gNIC5W%zys%NqP5l+)aPLs~&i$l4==}=HI!gaEU3{xk7n#qsj+@X9=Z=JbH|Ieq2e&ABK5cYQl%r!UDF<!ZO!)Dwk^Z<58|8QHDj~n#h2U>VOG1CDApKFD_eAR3y1w^0$<I&o=8Av(s`zTN;k(7(whQ%Qmj*vD$FGu~)hn<*oE{^-kv>D_N1K}}`LT>yjr3>K@RRayuuAfyA6P2BE&Zg7)5fiy;#+U{z~A_{j3?Hpb*b|AJRag}?cN-fcGAmF%3s~y5$O-vD)no8?jZfZ+N2)Z@y0`&<@Zba$nz>rwXn`e-zm>)z2o5~&r!89(%HT#Mf`fJ@Vt2oB0ukZWxUc`T*LULf0cY$B1d3;es@ROn`PyD<hSn^tYejUxmG_P7uA<v+a&4t+ll&pbr9)%OvX4dHLv)#w6)?ZK8;UH{?rG${Jq}-r1SR}tS9y8BY3{?xX-JG(%;oJk#cRDH5&PuJ1SM`@t%(PWb6R=4}*gxpPWyvDZRwEruV?OI4Sku_rCHm$9XB|0zWO2e7LtmezLzmA?@5HK>C69B?sb1wMBZvo=LwjTs~pF)i74_sVwP({7-o(YTMos>x$g|@;hzkdBpeFy4Or!sqSuk?^`_`&q{eNEU-v^_xcFx=V~3vr}agdF>;@;^O4S>IcZW3QD0==VT+vy|KUd&Z!_D8?lBknYW4y7a6B&MU@RDq^s{Ei`0w)><IlA*m<O5;;kf34d>$PrzEUf@v`;<n=Xm+un>NUQmW49@XhR#I97A59AJmMO@i}uGu$_H`d9w6V?CaQmlp$B(&w3{Fj&Z3S)}K+w;19~PL)y=lTJl_4y<M0GZr#Rs^yG>>mn~#F{LwBlF4=m%i~HWUri_yQVmK#DJGAy*g7j|&VgJ<qF`hGE7@m8|W310TMj`*DywL9x`$VAKS3o)18YBH|h0(6&JVU$sClB)TcC6HwaXcOCmYCc~r;8)jjT3T8d28=-pgjEcOMkH*30NobAD)$VrzMt<an=%Z5A|4lH|7(!PS`J|w!-gIwu!IbDJts+b!8;#DRLFs?_&4ma^Lwq&_4D)!?^3}g86Z87U^F`ofBBcMOBjWR8lWWzfel<!#c&k%^9?>(s=$io~XAQx3ONU?T+%9;DY(Aj<Wju`ZCViAsx*~G}BkDd6CcPyIB7kd1YR<7U_=rPCSBs9HU|$9ES3+Mnz#=)5wPPY1t1bm(CTDjt%qSfA!V<5ypv6Wu)I(3LHp~{KVWxzuCA=#sN!%29myUV=>mDxAHENdd#*J`4~AF@!L3J9k}!Y#^t=@;qR=OEalvB1lp6I3)cH~*|9FTa2WMkJ3q$tpZ>wTo752Pu)!tt!~8QaZjX42@u*yTteYkdlJQU(@i*4DuPcjhO}e{9`b&f-%DGZ*%=57`u|MqVhkB2FhJ9yn1jgak5lFwNf&EQev`6bN;mGGFU+l|E*zc43M&3rgr@6y#v|ie|;=T!f^K$SPf7~SZ$+HLbTi`3!tr0she(tG<@zw1q_NikB$v9xOyhXoQF;sl@pKP+e&s<0S=Q}QxdE8nW=M74CC-k#<)v@2daqh_XzIw|`)<t@hH^z_9;^OQ1BLgK~n_GxKD+2ROP{=7se?kx04;o$ku}-{-@l6k$iFP$C>%JeJH#HFTdF!_PPWKCub(Gae#(H(>CZrc>C*!B3Wq-^cx9?%S=F$rLpz&=HztKk2-`5&4-|IPj4u9|K2_I#hW6`~kP9sP0jX(Qf9N1J1{(#w1j<)B4GGAK*G|aOxQ*geryizp!oxh}SE8Pp{OfM3!j~wrS{5*YybEBZ{a^K8$Vw<r+eB;hLl#5*rtPgyaVSRaJrmRma;XM#Pp)JxmUIOdcTNg3j`V>Jr(TAj+YcESmJGX5~ll_l=@jB{rb2X$tLB+l(qxp*eItJ;?c_#CuwYd%JJntrW-rWVo*TXzk$bHJUK|0y;i?1H@#JN?_9HeuqGS<1>SIWLsJKh5EAAZ8Q<ERa?UR8=r$Gp;XA@28L;wZWQg$3|$hiyaoT$gfIu5unac0l%3Mpk2&>8qn=!2kO;_N#sWlycKPR)@c1r;J<LlZH}0R_EU^4tyPp^<vefI4@CMu&#aLCG)nCUKH!1dU@dIXeslgw!s18SBG0DpYWQolK)eSF@Egd1;4Aav~Q)wRkXjGUD2+3D`@uzEj!VU!V&+$^BBp0q{A<g&cvDUYyBy{T75X$yL(lnGp=;B#5)m-_5Z_?@c(s{^Bp}jVvmdRZQo=|E+M{A<g_mS`znZUDK7K8?&8-|^2u@47MmCIzh97)r@mz@$}_zG0?9|d*EmO9a2Dm`+%HVhu@*sjc8Y>Or?{NI==pNvoS@eT_(PA#{zL0JALH6Ctk-QWK6B(c=03`8V=VG>uE!j-t34=Zj`OyJ&$HzE&0%SWR;TWW-}sUETJsRhe^sz9x7~OUD)AjoOMO~bdLsVb#WN*ePQ90+97n=`GBHH_QXSFXGvfzr2u684lXhsGRS<qyl2y`e+Y9@PDPczDbGgWK|0e4P?d%uMN51pK&-rq>T$jOm(Qq%fSbm?p4dp+(2g?7>N%4(|?$JNgV`4!$_td79mi#C#w{YLXo;VM!7?1Y&tSsVZ&%HwW&$#~BCsynLe__p)a^H9Nus$j@8UDwKt0etheWcwg-bpCW&rPMDt9w3U9$tPK`;BCW)soM43hG;>PWnxJ#nJ)&Yd`jH#>ES3B!1c)oNH#q{?K@M8|Ndg<z&BX*&2&>GX9o4zj3k*#=W^=821)$i;?_SNRe_g3ctkoIkS??E84QnD4zv=P(E&x#W$ihBfa!c_^n=I9`gHbwDiBFk??!|EBiXV!3XJgne&Sg-ymN6R+G^VQ<70%ziiqp={&iP`Plt2{FLSi;@@8<<6q`J$k<p_)+KsQd#o@183w;r7x8V)op8RI!wKyqx{{m=ThIN4>v(U(kGn6v(tAJFdz^obB8|35`u%5PUMnAh_(?ToeQEpZi*x!4#}VJhUwmyr6wX;s9!9;Fb(C{D<z+j}zo)Xmzt>cJ!#_gm#ddfv_8rBC;9SpsG~QSIRZQy9(sc6n@7uYy@GR=lD?)r#tFasPRuJ|0J{{@5&5H9_&PTQ;AK*J)+929655^C#;<7JNvJ}MotI8p0Kj*#0H?Ak(J<<IYn5PoYim!j2S6S|R+ZFd6@SFH*+HJY7GVUYNamy;_R%&P!Sx0HpFh5w_Lg1@waXwZe2<JGJH;S)^Z^wCi!$nAE>q+>9`pJBv#FfW=7u1#ZYO6H_=X*&wpR%2?z(2ka?}@%t!211{DVP@rxMTfNzzOFwsh7pK<Z3PPEq7g|9a+*#NckE&C&~I*O-V#Lu9LA&aw-KsVmZ$Be*S>?Wqh!2yIl<D8{HL|Z**Ir<lh!xhkD695B{noj5FI4u`cpn1mCL4Ix}-!YU%Jsd?Q~kS>I-!|CsAEiMOK!_Jx__(x27Dw@p;>Jk9!}pT4LkzOD_ydBT_K*jFsujC4{*p+BvRgdhG)e08&fq@#IFKt6-}%kR~}E;zs1lz`_=KP$e~rO-lYCtWJxT<F4O@hvfLah_a;=M;Hc%YNX$b!N&Z?05eDOMKgl^5SQ%mke7O+4mYD0q9>>IwPHTwXh#<lV^=wuUm)xOT9Jl`|go_nfBTq`!e6G2PB`@UrPH|`))%z3roXqG#T$Bn*Wabe)K(ne$f=a?{**Q=bt9N>eT`75wy3mjx;PE5MMcgbBuN6agNfiqU`I8@Zz!`v^`kOd98-{T9OC$(SzH{`d*ve9s9tzdD6esqCpt{KPSLnQVILH-c>PgI$aXqx-%!<cW2v*{AYQA_zfpVN;`QvfaU)lzI(isw`J&Oyr+Bbg?S>bt@KlUc1~&kT7_9D-<N~!;SJQ+n1kZ08xNrWR&IlQ*32#Ew$>HD<6OeWNzNs-#)ZW<!nR?2dQ%1awTykY#Pi63{=YU7=L-cJiLXA5#X2W*-SyTYzU^)`+_&~@<a5XloEJa!!Fze`ueCo59+LFc;aFdtaYg<sw-(>F_HVp@>3bjPeDxAvcet_|?R^5u`^*gS)%NS<d_$eEMAl8l?D_E5Pr&<=oz*Z8_S`7GmL21X{tV~WMr85B;xD-?=e=s)8ra{DcNSkgaT)I`xX#yltQTLeQy1$skIg8zyj$Q8cR{~?To&;wrod0Y`%fh}74z+@%Sc~6FZ*t7pa;G~=+F-PXJ3DuE7s~F>snp$5MNt*SNgjaSsvrSIUn(DZP((x@WB=shgw<1*K69a&&YgV5Iqm+Wb26Y*f-;_zx9tne5b;)j!>FKU_6P-jrWchan5h-!1<kRcuDw~>+tur@&0sN1@SE{d&#=U`rr!AC7qj!uVjhCd2)eBS;t!*JBzPZEQj~Yd~awAZz;avQfjEgPqpH{mKE^Z?U8eM?XVT&bMO}N)qM^!4=970<6NLlBJS&l?^7(rT`)dB+K>C%7skHlY9XW__8Re5q+njooPRrJk@7NHDENKfZ5W^P6%}9I9ER^do)^RXzN#7gkuEsjaGZ(nUhLg)?(=Fg=3kyySo(EFeVm>n>pM%DEB43kq1YcT!TUu`8IE(kO|#%no{shW`B04Wv$i0g{4PQp(E$DU?hf%SW3HiJ%`b@fzx|2zP??{k|JsgC#rzoh1o>G#NcxwxNR;f8E$@}1X#Xd?<oR@8)cg60;wz&fFz&=fV}8HvD86bREc0pRcOaI5oy9k*tiw3zn}qer4Ik8N@s+Z!v2OFm`QyCN;@dvqJ$dH*qQ9Gtbds}UoVk_@?}zNt;LkcF?_&(RJ!lWbF2i?viGDD*Jib2(xPj-YvPQ-q+p3~?U)B5-@}G?N*qQG`ZTs`f^B9A_$hcvd6Nda3D~j`}GKG(S-@k01ToC_Ib9_H?&Wd{M)(Y{X^I)Ix=Mt<lRZsD44pSt3-F*<&SM4Vv{s(WFFEr&}d>3?drTE(ESbT4EI1ApxUbJBy^TdMhO@>Xu_@KQ)em-xJeWmq&A(V4g2g$b)7JzXjw=>QGgDZ%yy=fuyg{9tIxvyHcGUA_lgzuCrn{j?~d${<@Ctu9d-RdHpKYVa5T=;~Xmnapp;{5l_Rq-vYLXeK1hH<0LJ(Oe26gi*M9+kxT?7c_uE1chhdc2JHWsjc1pErBO5BapW!#G<b0pFvIor!f~N=Nv&647o;%|<#E!*TBaE*H)dgB*CiybtkTS@GWFU%WTce>y9^^`AI-52PK-hjDe%6}<0JjaX6V(s*w;;|BZ_*JT{Y+&Ad~UDL(4n}&1v8txdkyG<0|5|8)N+UGdDKOGt>zHMC!zCRfffcJ2=_2L^rSMWY=#z~ZCwnIpNM#Vnz_qgYHUhj1AtplfHoGQ>k@^9_h5a;RL4`QAF_72XO?+g@QiEV)P-?~5M^Y*^*-+G~)=L^Dla`ZUy4f}!kPN0Q~^Ip%XSQqa4Ed4t3J*GA50r6G4VAT6UFU${huZwT({0jSvUt8eZ>$xM|2N$<V`?t*Z#5wZVx#BA?vS9w|aO>drzNJ|&?E4;f#di)R(!@6|J;!->r=7U3PZqpKiT@kpKF4Qkg)n?qv0wt;g9m%yJ<j~q;#;ozT>K&ZjZd&%89X2R-1TGe{mgNDoKxE`#5$?M8GI*pV3PPs=Og&e&GkOgpT0nR%Z@aRpBFphyx+Nm%&*G$-|;=mxl<@-x60yMPUXaRWc(h?daaB2nd5)v`Lp6V7U?*&L^<zxh5I%uiuZ`OE%;t##dX9V)f9d)1LI737S#LFp5ohFU8P^E%kkdNdbf+LZ<HYsSmzgNjPE4^r;4vW{e<=Ql%J8#nx69hPpee}-=%gNiuYABL&aA%x5hp<bKfztoV?G={BBd3Is@y#@K)lhZ(rfN*39!RyCv}VJIHg%y42%`uXwdzpEOb{WkkscIh7*H@WJ1G!fTr5zfAq#f5JPm!T;4Kyp0>x{r~-hcXvh}_GN@A3?>ItQ^>*OdDJ81dE}+k<K(5}mDFF!E6HoAr^#!{G1N2U7;-%IJUO16NWDl-Bqvd?kdw#<sn^K|$w#TT$VbU1Gs0Qw9qKLe9r9D^W3s95$WO^17)*AsgJ!b>n_8IcKrWOKs!(fC3zKV*Yg3DmYm@6!e<If>H=&jwHz7BtmLfMNyHLxJUC6Dd709i~ZK;*XZOK1VtCD{vccxY+cP4kE)*^Q!_o3D$_aP5tFnJKQ9(fSCAGHp-AGtTRCb>7+gIbO3LGDC#BzGdWqgEofBWu)hWR2XC!Q|4^Jmk{k+|*YJI5+vV0=-XuO@2WAjr@T8J9RJlcXDz@h@!5d?j^4xFQaZJFC)*TZYIwq&!BE3&mad<e<25weW)wQKIFmF`Q*XmzSIzMUvgLKG;&vRN9uTTM{)-SlU=D($gX5}YB1TI+=n`k+=o1Xx|BSC>_uHk_9FXI*OGn7{?r(<KY1!Oo;;O2i<(HDMP5QpA}=AYp&lf!AxBe>lB3B9)RW`{@-F4u__&L~<O2*QU&sh|sW$3avZ;5-Hu5v-Q?jWa$j`{17);J;2Q|k{lT9r|&Ppz5_ia2ixd62ywF<c+xfz4WEvPlfEy%5@waKl??Wy(2?a6M`CS*5qPik{=Px1h&3wZ!}D76)ND0u|6EqMfa6!mBFC~^R`GdX}fiQ0`ki9CbahdhHkhdPivhrEEn<R#QW<R#?!)PCgo<WOpFawvHk)q^~ZJf7N#Jf1w7+KxP$Je;bLhm$STmShV#V`--JqB>Jsl1(j5b|#mk<|daU=c1b9buM0;{6>L3Aip6$r2bBRNWMl*CSM~P%C|AyU@&=8MhK%$r$&*dlLM%$$N}Wh)Mez+<Pp@l<Pqc{)EVR<<bKpZazC;M)ragsZbuzVZbx>Z_9eTJn^3!wn~>{KJCf^>t5Z9WtCJlWOs+<CC08TYrMi>rk{eU|kQ<YmQwNZnlUq~0$gRnpslMdS<X%*Naxd~g>QwST@^I=b@^JDP>Jsu8@<i$y@<ehdHJThsUQA6OFD9?1?jo-yucsa$uP4Vcn0$zOfqaO3N%=OHTw*Z!9)rm*s5bHo@=NM7@=NkR)K6qn%{k*AUYo4gK?{-<au&O9b4eBklk+o}T%KByT%O#N+Kk+k+>ya#cWMi=JGlq7HMs}5Keau%KY1|KjXap_P3=kcCi_tbkp0L()S=`c@^tD5@^tcS>L~JT@*-*gc@a6BI*A-kj-t*WN0DQwbI38|IO+m&9C-_a$vdb^$UDdh)cNEDax68J97|qLokm_yj-ZYwN066ON0XP6!>Gf_VdN01g&abjLhVbQLY`pvZLXTYU~*ta7)$L+?M3cNZcKG1n_80Gm|UEii(H(XlWNXeIeBgJTLt=%{FeNPdX4;ue1mF`Z;;ceo5<<pEy}mKZ3~0R;Td5LHHaEU4kC}DPA88dTc`nK3%MtCG`T0)jXHwtMs80XLT*pisQt(qxf#`i+>Go*ZAW$@*P^<RYmuu^n~<xJ%Tw!-%acn}tCLHUf1)~)e<BxVFu54D8o3y`6tyn76j`M<CadJi)aK;M<l5BM<l5wh)XwCF<QCLk<QC*M)PdwS<Sx|V<Syji)G_4V<U!Pl<UwR_YAD&8JeIncJeE9}x|%$hJd?VfJd?bL8cSY8j$kl(EA<e0D>;>ViJVHlOua|GO#Xwx<mc2EWK;hoKPP`?FxlP?YR-iwo0^|&PtM0+vPvyaR>_U1P05YO9jG129mt*xCVNrc$zJ4<)E?xKWM683vM<@6I+*NFo=o*7PbLRb{m8-Oxzr%?T=FvNbn-ItYU*tAYVtbjBJw)&Mrt^DBY7(|ioBJ)iyA}TMczk^Bkv=pP`8j%$OePSN2oi<N63e%3FO1%WNIuqnY@>}p1ha5n;JphO-`gPCnu6OQNzfa$T~HItdk?DQ^=9zHPi{@HRKi4K=KOmV!Lm1?P3O#XJv$`R3GYCvJbfnwJW&`xdF8?+0^3X2IOMYoaAEU98`1O&B1Gv-z(5Z<oD#is5i)ek#ADd$v4TTs9VUV$a|>a<UM3v`8GG})a7KI9G4NcQ6s6#$&uvQ3?@&Y&LK}AkE8~XN0L3MqsX4*Zd41o8~JByPx8;?mQ*)#OL8M>dvYUk9jZpIL#|3~My^V(Ky@NlAeW=oB9|kVpjIK5AQz#QCl?_Xpq3^VAm^k0M9xRfO)X5$P0r3>axQ8yaxQWnYAJFaa(=2x&QC5xtxPUNE>5jYE>12(ZAdOdu0(A?u0*auZ9}d>u21bku1{`C?M-e<ZbcnLZbj}y^(J>B_n?j?_aOJDPA2y!52MZ`4<nDGE+UU3Td5J`1=J1H2=WH<PU=?jPI4MGm7GStO1(_JO8%4j2l-F(-_+-1Q$LgcCVyct+0G7Xt`$r+H6Qsa|DKoE`N*cK<h<mv)JEj8<c8D^<c8!nR8Mjna`%idj5>zuNjBAsJcc}xI+8q*Jd^56o=KiZ^(W6GFQrZ<FD0*{29sBj*HY(_*OE6-mytJ+H&a)WH<Pzh*O9lA_fR*I_mKBfx03gh4^elK50Q^j_mPj1k5f~~$I0nbgPczOmBHkb)Fb4R<P+4x<P+pHYBD*Ee2lu6e2kn*-Azs<AEYLd50Vd1H<1sJlc+j5iM*2<N#04`MqNYRMvkYhAjgxVsf)?c<X@<>$iI+R+I?G>tYk2GVMef0$5E$}$B~CneaJ(|uGB7MSF#he0ol}IWG8Y_Y7TNya(1e@M#;`=lRqlZzsMiSPpCJ^Psq2ar^vU-=cs$g=g9l1I@#1X@_zDR<=cAYFoVg*GQtV!4(c}Y4)Qu`BzYZqA$2x+A$bym$$r!cWIysy>PYfXa(AjHxjVTnwHvuD*_rw?*_qsc+LGLWT$9>}T$5apT8CVbT$WmuT$WstT7g`WT$EalT$EgpT7q1VoR?aJoR^%FT7aCBoQ;}~oQ<57nwy-JoQ0a5oQ0hE&tyAlF6F;tV_|!09<n{zftsJ}K+cg7JUZEBDPsSB`Y!^%{WJTm^22`^_`m-0$Ip_!|7BW6TK|2d<k88&EQ5>(%OZ=5^5zMY@;}a!fmZ'

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
