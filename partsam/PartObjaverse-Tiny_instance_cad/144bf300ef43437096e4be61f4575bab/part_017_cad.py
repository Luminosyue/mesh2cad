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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_017.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_017.stl', 'source_sha256': '219911c05ee4e81e21de52a2ff064ce9027fd963873d861c9d322ff2e9d2e78a', 'input_faces': 786, 'input_vertices': 484, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10114290565252304, -0.15805934369564056, 0.0658053606748581], [0.07527858018875122, 0.15754735469818115, 0.3666609525680542]]}
GEOMETRY_BASE85 = 'c$}qt2XGZf)9s3k5GERvxnz^U<h<l4g2@Qb1r!JZ3n4Ow1(6XsNg&{oqewzX0s)sGau7)b6Rs>wHaXZNznMNqWxlW8t9teSs_N=9=l1sW^n{(A-BO1(Y18F4@K@A0mM!>!tAb%@@i1~5BYlH{2ln?JUU6vP7&jxk@cJ)RFKXAtvqKLzW27;zw2$xb{z0Yd*h<&)t5v$Zt+d}SLBT<NhkE}K<m0RP=6wT(`zn6;fWCpgs{CWMTGh(is+K8l`_=Y8{Bu_!*sc3<hn04EeZQumE<3ke)Y{qNl<>yGXM1$ns`BxI)~--ztnlex_K|Yihr&CzcL)D8aGfrju6p9fELBH%bNSV^x@=p}GEwZ;{3N{XYCZTbFkJjt^TJ{zo{sN?H;(-#ejLsg!ke$guNS}b3yUA?O)256Jxe!AJYN<kh<$uE@Vgwl#s2AV#1sEvpXOa_jx3jYVl$tUdXkfcH;Sy-ByqMadrACwtpUHLc9ig2yPXw3d)t8@wtB0?Q8ilZjSo$QcSJ^ty_qjk;&e=}0Q(h-Crh4R-WA?f|46j(v##zH`<D~NkLyD`_z^KHrQEfK*xMVf1@HBFk<{0;xbQ}v9^kh<o-Os&@&bRjg78-LlGCKUwR0brdJ_NKEBTz@E%6&!??}DQLVJXF&fm0D>doOmz2#>LZ*+F^5&wCQioJc7pYYbSU$=>$b|Wr}&QJmN&(265tVhKp|Mqo7gm>k#OaD5(>xsSN@|P$X4>_j9NWJDB=@*;FYvHZL6p7QUS^bLe^PUUuyzh{4WgTxMe$2;Dgg1*{lX@MlX^3-bl<;<+n=&38ZQsE@dJ_D{y^2QrXCcnGvGBj_#y+w0v|;@F2MTX|PU<Xv*0z&)jDdr}Uz{%U$oA6$@$cN%Q+QX>;Vtre|2L;4Ubh~Iv(^Y1&#qG|#NG;PgLnonL3`I775|Rnbr8?pWzt@=PZhDZ-K_#Yo!85}vuBS%y>69YAMrQlo!@ogUBiAroZF5$B<?y%@G~w4>iuJy%p-HrQuxVEeuiJH*d1IXd2p0=2S3?Q^66~5RN}O<rUU<Ss^r1gJPmnX>;}GL38~jwSOo3O{LdbVf5%OU(;3$k_G_OC?>v55+GX1j0Q>J;u&;DJLhJ_2mi{&UuLy5gx5bac<15+~at?k@L||PiyAA$}9TwioaB#KcWoS+0IXWKp4W3B+W|L@)=NeJ)->A`28K*<Ho)G&fJHZz|DD84&I0OHlE5R@L1O1i1jQBV2E<pUj{Up!!XMSRDKQtfw=$~ag*v^C_{@|I2b3|3li!%o?J|9km{f{qXy|PxEMZImt!M@D>IJrLH+<D2X&oIQ(>;lHa;a9NV9mxFD#`qa}673D@2K(To4N_hohVk&h6ZIw!!?-;Yhkp4`5BwR|CdtpCe6kKZXXF;%Rrus)`Mt=YQ)2It1O6K>mHZq2MKOMwWCvgUs^s4>J1^$@{0xY5V0rZ8t~AJJzjwQZuNENl#kuX|Rq>Plt?-6_4T;luZWnuJp4YH{;=sDsxQ5u<=RSwMt7doc`{YmIjmb}ix6a;?{&IXcg!VRm06!foZ<hFiHX@&wHVbd&YAN>4$lhqzhA`o6`IgIiVo#bW>#FHohI&&*V!q@mCH302&qKZa%1Zo>CuI@;ue0DMWy3DvJCsCwv-U*2eRfEH*)EpGx|FU7;>`9|#)B)Nri>pWv?2UAn<V)(a`wUa_pXL`zOKZ)E9(V60foRH@3~Xr=zQlY=Igs%QtzE1=&$4~$lFmD_;>jw54Mgy#E;AKitxs;Kc(MI_aS2MI<OP=<q@ytm?7iDOtVRN*VgU0KQ^t7JeOG|ycK;8>qc7(e*Or9|Er6zE*0=Zf8ClWyuIZW_}TMO^6%;~9`;{Gp}jrtA<tLFz<*Mw8De+167rBd0`{>FC4TGoKIkuFIO4B66Ze^XjhxcY^9I2_{VmClv*=Qcx53`<f3^$aZ{HSqyV?WxHqU0_x7>Nm$F1FAKj}O8iP?pEBfG+W^#>V;)&;L?;(uyq;hnb<WdC4}+64cLS|ZM<n=-Df2;|Lqs|oxRZX)BvQKA|0v%CW84Ouo)uItqo`-kR*VDBh~{ZGX!7>Codqu!KX_RH^aOAd+u(^<fmy0HfHb2|EKd}j1-LNA#Y&Jcg>yT*XGR+Yqk>g7zdH~8~T_-TaxTo54kR+l%z8^sSvdz}&CXjlA8*cZ4j?X~x513v2&;mz9z#J@T5BK#M<EW9gpg2ZE#c!T{zwv(_gTVL*jR@)<(ze8h$w@*zc^U*Z3Vw{{<k9uq3er<Iajr`<Yhd8(9Tp{&6d5?HHM}QwSRs1^wEbPa;7s5|ixs{TS`SURT3rvQ+SL9sD<BbPWuRZ@b#FP6S#`!;9xR2y(C%iQ{Kl=SlD~yLct>GtsGRB47@2J$fuqF7sRU;*y?IUGe8J8P^|J(}uoGUBfC$ui&%&`>xHS{(5H=zXT4atLbI01QZZpsh-YpmGYcR6AIH5d3#F;cJbmrHoZvuyDH<sH_yrx^eCYX<B$tV6y1;v`Np^wSQp?|TsU*@c&dx0WUdZ{72sCcI~N^jEuq!n-yd#eOyB58Urg^%vggolE-5)&Cya+olEhz{0g9-+7;4p5AH%ep(q>A8Z$X6MOS$MeyC<V!RbU5B^zE#96$O^q2J$?rYA1xe%xE9M3ye1oAM!U3jx;XFTt0#k{a)zKs<AWez+)jURkW{Jc6ZytDTntj{5ZBo8jzY4As{&zE}k-bMVu`-Qg_T?iHX^Y@XTnlbSIdXdEM@>nZ=oRznMzf)qB<nzia<T-SM@J3R>IbyeE8S?g|m+&_4>)4<BgkjuPFcD9mFgy<~>3}>OZ3sW{DH6XcAZ?QP8B_%P_Bh<Xh7?9T$FhSTc?|ovInOcP8fOyTHGDDdhvOfgl<Oj1ZI}2fj+5sXt72C1Z`=PEe3n-jSG#fxZ$Fa^-rqyoYphI>dL3;p32)sfg8l8=a$;|8N)X<ta7V_E)3dnnR<-TIJ1+&`zTe>*`lZ?e_&;}B;&CMSVVoSB5BnpHrM*tK7vN9Mg}wVz?BBkmL!4I!g1^J@c03pIbD|UC%$5;;2F9ab{;mLi;v?*1$7X<^_r+1~vtOjWw(%K-SL-?2<sXLocw#f*UFY0kKm5A1*C_Qp`s>=~ZQ_4f3wb`Zr(KD9$3Foda|!E1-N)#!sNccIB~6!nbu5E%l?A->Q<-qFix`MJH%k)U73p<Qe)p|`bu9c6{1p2v?R8~HLLSy0f}d-7u}`RY2IH{F9@saC#C-YXBi6k-^Mp4lPQm_jTyCs0|4asdtu69!)d%t1pCr6(<^??G+8Se?KAa%DnfFns){YY%m|x@iq2A6tF@DnJ6+e!Y*5KRC6#ov-nixO%>!aRK?60lkHSxUfRuO!KqS(&_enQ^H7lWUTX=MGhj#hx5ZeO+vADV#u``Od-Tx0CL3qJ9coCBHtYV4Q#la~u`EOD3oTaJ!s?~G;Od+(HW)fHR-^*##$-^Lry0e{~Y|4#Qw!aHv?!2YCQ2gK9EPk7VKz_>lz2zj{P34XT6j*|HHqaTgPlJK+nBgS*LeDqTS_Ay7qk8}AP%<Jpv!8hoIJjA(UeC~dW=kvD*4vT%m2J)P1i#{j3mAN+dy|o_6xH8ur6W&>6h49vXFO1t>>xDNT=8%1qeMQbQ;=iK>KiwC|KEXQp7skVw0N7_~Bl|b=b${e-_(1rNZHD<6TjRR;FFyc$=LFeT7$I{pAA9wMAKQ7X&-cBNw^FUqt{Xp(l=7S-;@@`pxjc{A`-aQ-cTI4|`cwRo@W%6ZvTrlnl#%C0Td!pB0d29L>0w7c4;~QS+Wkhxr}OM&#M7>W@XmBg4x=B7%X5ddE)$*ub5}+_+h@akTysO78;!A3(5{Oi=*KL_z~{pGfPG*i%)7sqfqz+Ql+@FpJ?<AL=Lzp@nr1)ZoPqn=!pXv$#uMz5y+<LRGl#=ZeA{?w&)7aV@2cKdc&q9Z#9442_SIF2!cYECX@~1Y6YTTdv%$|>&#t0-#p3xi;O~uMU-^OT>+CDBpLg_oBD^u-7nxtSvpI2|uqp}s^IdWtWj4Q$eMtY4@Z<Jg{5W%6z`pmLQ+TWOxq}k_Ogz^ZU-p9EUsujqo%<4S&RJm={9mYzbz^r=T(`+CysP3g?0e@AL;SbBVP9Yu@>9PD>OD{b@hpy(`;_bFX}AxT`g?=aS8+Y|`Db^af6HtU-YU0mi}3ljVw|@c3;T}^rM*_x6Ic(+j@*EHR}K(eHsy%$KMw(K-mEIu1vsz|eBK`Xt}L=IGCn^+e^vdmUih^KrCvwiXT;h2jqujEQ*u6P*8V}xbsgg`fxng)>;L<)80V4eg?ApkC+oR+;33A_vtaP<wPn9*g=WFLTjzm#+YUS|`lCaho1CBTtdsf*oD)BetE~}#wv)nJ<6q1D(=}<Ej0acr<F#Uc@61f`(*o;&wR8md3^{RLccTXG*U$Wgx5qBVKCrtX>yPQ@E4-0AMDl6wSc7>K{&bDh>s~ud{NCJ#d3SZU@aFM_cwWfvA@v%&b_(x0`W*Mo$5Ggq*53mAzLC-nV|%jfKg}w+gtuoJit~!c*w0&?vOB~+HsfyepD)Hk#Vo?xr*3kJpT{p`+*wgiR!f}6dtqL$?u`Az*uBC#TW1zKBlDlQkH^1XCD-q0E92XAgyMW7ZItlVtWgr5Bh41Pzu3|je7cW#z6<M*bEhwb;AeYvS<j6v`%v%m%;2X4%DA-LR^d4@>n(XsGtT`Z>!;Nx1IBYiOFX|#UB6xGGgsk0(mE6PlYz31IGUHid1m)?!rRAMh;#ZYocm>47$Nq-<>2R^-I!lPM+<LjR$uaL_{U>Ce`pHtir6gvZO?0BJ#1b~c<1~2k~dd>oS(bC#;lO|CwIoWU2+-Llc?dsJ0tE%{%yYm;(2-WK-jPR;fVBS;z4P*y>1WT?VcAfuX}aDel@nb@K*gD@fep`k<X18!9Vww_0|?u7Wd_q2I@_3NS@94<?-I9$~L^e$&_J-@E&b2?@II&-slu6{ce3(gL9{G<%PHWI>>p2>v}KvpHL9|+cC2w-o<_K9P0fbT-r0o!ns+)=@?hODZ<<02TMG*wYhMA9JxYx>%anxley<GFWOE4@AF8`Z=L;GVBS6S72Y}9E_t?E6vjB&ok4gb?!Z*J?nOrQ@2OW|65n~7%nz#q_N%r#t}u+-nK*};9)*2)nm5Zd?^y5x_oqBQ=wIIi;jNG~k{?HrfjCbXzE^l#$RW(v8a1%K{nZin&6BWh8@O*;buY>}xN$fb??<W!p?@ze6W*2QB>L+`EY5S5TwfyXU0}z3(62k%6*@$C+rlG=b5wPV|H-b!Qg04J_Q_^gHmt+t=L+wvGZ)Y4#XXVFeRW}9_aXLg7q(!WbosPM{BJmh^QRdOoU3F$Exd8;q{M4h7$WU*Rah##z5G8Ix6i*|9=%@#KZC2G-?OyF`OnHp!kZ~YWqo&K{t@#fF{AKSnW_8H|5tF|IA3p})EiRvIL5aJ=5<s)@B@qEebL!dct5!C#R4gpDk=FfQXb-5boy#}Zg*84DeI(pc%h6hN2U_O+sZA+`A^3I*pKBbF1(}4N#rfw8|&?Z?BIJmk#;$YRKxp%Ils@7c&6-?^KjScbyB}GdMWtx@3EejD~bC>_kO}#4~JquTz?Pd*LNv%CC;~1WSqF_Wdi@XkMPzBPdt~TKaJ<4hcR=+f9uwW^F<8&zh5J~8Q2i(TR?v7-@?Peck-9_Acj3ac=J~~{B%sh`@XyP;pcQZ8Bf;cbu!<r7Sj&MbsM_Omb|U2B=<?HEY@AKOzaFPPftNU-v+@?*u3d7PJFxJJ~*fr_>MJ&w`yY@vk&pZz9nUzynnS_S|fQhgPeE|lKaFI8J9(RN_(Aek0L(-JHcmoB7TfVk$BFk(kevS+wF_gYn^|9{{8!(Ny3|}@jj?(5a#K?e!?543yQt%SvB0ppL>jx_}7NW{?MMexb(a6V9!{o*PbZ*5XZh%cpePfI70k9ZXn~?Iii@{H;v_+1EpO*b~`G+fAPXNo$n*Oxw~jA#&b2<Um5S$4idjx-^n^=+y7bagGSp<{*t$}-qOGJFB6fsAWz|K!)(ZN<_q9kMt2kcd2-8r$9RSJw?@kht)+Y_^I&Pey$0gR^sbGRm%YKh-Vr4JjN4b`eYRNu@5jwsyXF37-0J5i{LItwlAmSo5dYqp@*L$_-a~jR+biiuBjdO!lHVPNu<u%R1LL&Xl9@98djBQ!)SjoeoI9D@OD~Z2bo7vM=<GNT_rv@F!W)a~9+P&Ibjdnl#iR&t`sToMSne_yFXfvo6#MYyM=+j8VgKGOd9lRVs_t>&yA;HICf^TBFiu~|{=sM*B;(vFw?W?boAJ?jzH`jMJ}vj)Wx|*J4$tEY-(lV8yhwN}e_r8j8F3D2L@pKH*)tgLJvR;lzaR(pm*>yQbGIX;82HTPgm)$-<2g6QAAC$d;myt$mJ9Fs9QFDHf{$yB^P+L(VP9i<7{*Ho&Plw^<NosE9r&nfa$aH1!*jazCL7K#P7TC+<nE_&AL&pM=SoNOpuHLKzQ8!r3HCQS;Jji`SMXJWgg3h2T*$UGC;T6Y0zYa$o?9D?Li~wWz*}8#KDl8E>aCxIdS~N%0O#xXcyIXOI^sSS4?lZD;s5tn;Fmh&I}q3VXq<;6zk#2*Gmy`5rExA1oJI2JOnim+M`N=i{?C<!xBSAPeKx_*k@_eXIx79?ijP7*^NfX`ie)8lwgY%yX=R@P`_fzSKDUqw|93YEZ`@pqbC~oTCylnl&*dx_KWks}oGlXk>O`Ec-pddF&;AhJoP8eODb0C{{ZffPQSa9v`2V3F{5<#`=Z^);%6PN8@SfNBqd52zx$u12{|E5HOM`#63-$hOpx%2wg3nYL=eI-0!GHEXQnp@|!TIgs%jmBjcGy?^6S~Kru#XLZeU<xoAMx0M_$N*R|JI3d)rI%vg7d)t`2qc$KOFq>Fz`LAp&vihhyTpGg*U&HmwD{WG6MFlH{d%*$vkkx4S@X|j|hyH&(dCJkT=@f=sV$^b?=G2E5R3hbR*%dPlNE@vr;qUEvPB%H{QehEPu|&XF=ct^WptPSIi6J`gqj4>Ie91>xVcmPC>a|Jf7d@%tSr|roz5zWqjAMb1v)~Ob0)#65jWns0se~M$BiA?pRmCn}83GhW(`4i03l$Z!JH9dV6h@JljHWK4#^43j5Q;@LnTJ2DbM(>?d@Pd1pIA`|ht$Zxx)k+m084ea~`;&&-bX#HS+okUGK}gNI7q>}}JbU(PiHAB%BoWSfmRkG256Fu~`rwyz$Gei@DR$S8VL;&)wJjd*7DSc&=g4&!`IHrS^bf^k;uo!kdp2gak`PAg&G_@nIeU5{~|W+mJPUw^usn;GH!9^ktSm?!aH@qVOOU--G275tnP!=#>na86>RDJ8r$|1I959UKDtd+lI<zB%Uo#t`raI|^?)%3$1nX$?La?;)(4uQA_C-+}-0AsENA@8bOYdpz%3%|l_|$p`m~c4J}RWi$BZpYR@S-#YNCVh~UJmsoE<Pl2D?PVj3_A|FA$kmqhavEBu2mVK9*p*8G(+m3ni`8wV^*QfuN_}<9OaRT3U`1ZwfR<R6-dwns)xiT31O017ov!aNzfhYX;$NkCbS`h2ZknC8Wlkon@yfy~s$>l1;zC>y82c}5>8dLq@f1?RMPd)J+!X-b%S<V;z8jSCzjK^O5j%7ah<!x~vFV_`(wN3D|>mu%h0dwG|LOkp*?}DC#@5IclClJrn>*B}kfagtX^>6SqGz;#7#(3D5c#QtGh9RCoEx^yqiu*zTd-y)3W>f6Pt`)@n)u%qrlUELf{azdRcU>@^L-75cdB6@ns2SR|9pA%PE_~NwRrW)_WEsNe;%TsNith>>?ed_#gJ)x14yz#hJ?F38Wj|&u+kpFodp&#)v-M~AsS^jj#~{3)dV+aptiOb~-*{qQ=NX3Qh87RdPf@>PT)n_|KIW|fSl7}nlKrPKVFI3?67l}nSX0ZAa`Ypd|4gidbHl{r@?ENV=br5IE&qx5ZYg4z?2{d5cH?|&M^}6o>$oKE*Nl+HI44_KR>qTkG~Xw8%8GsF?TYxms&_V=lb=2*=aAOO>EM$)4wH68w!`y9IS)BUHofv65I=9K$@gQ%g0I5cbLKoG{Dy7t|HVu8ul5~z@Ld10A-+rbX%o(2%ZK3m(?ZwqoW1Un@J_Ep?Av#|!}(CN&Df_$G?nq=iuo+<b+u`O?}ii8<NMaDYvei6`D7EG8zNuf`{G02%l_FI(G2@>j}c;TALr?8*x^6E4mbOKwRbOR7+NwLxedR*-+UUbN&T0q|L>oM53Kh8^=Wv`S~dQ+pN98#GmQR91}M?EHp|_W__^ur5%55k>(iz;@eu>%3`(LD9%=yRWjQZ>q~h)@XW+H<d9A)qmj}}K0NVCu-Q8JVZ~CrJE-$aw<wffH<GQa5;6GUIujF?nPlzp+E&l#H?f>RAix}_Uv_Haj^`{SA4p7qC4cBU%%?;%z<eL%yZv4yFW}7u`#ysl!RrecB8B0Gml(j!QeQMl`<v(b1oU!`2q1=qWdlR>2`ET0%!S?7r^r20E#?Xw{^{3we#;tKvmKQN!{h5nJ-{7d!vbz2P`%dF4EbIQe#POr`Z^Zid>$K50ndN&ruS#wcr?7m9+;7ys6DQN|I&lii1HP&M0<TZS*IB+!UzfhATbEBMxvS(3@imrRN|MNHe1qjA+TEeuZ;bCQul<d2CG)yuUaPUMl3Vnl@gSCOu$)Bf&+-+PlZpLV?!g#t68B@-PM^NSy;$zY*iI4qu<TDeUt({Teb|m`#C|OIr`;7|Z<bH79XE-SSayArrxfbniCruQDH*L~CPm|LCF7M$Q8JXGaUk^);y~h&)a!{y5>KGsLOg+ZB6T=%IP2B;7bW8uR}k@N#-QsPOwo7<^+@6&#G|Mu5RW3BMm>>u8u4`M(Zr)!ug0^L%u=$3dL40ylF3SzQHK#P<L~RptsysyzCx%c6Yo&6R7tRsJuJ_mq;kQu*+aeK8-5PU*VVdkTFGT4r<CY><{<<875;XbIF|YZaV+sV>I1~<h$E=?5l0YjranZxnON8T8|%>Z4`$ztrwrjZ8p6JrLK($zG>Uz*gffleXd3%uJ!Lw_(RB9L7Roq|shQNjP>&-%!yN5poHrQj72*@r3B)Ie4^VF>K0v&WdIRx3;zQJXi4PH<Vn5wr{W@P~n7_;HryG>htn)PcDS;BpI%C;S+bQc<=Q{S&21*3$j$l1|DVte$n38Qu)+$*;thq=fJCwvLSx+2Eo7CUK_**3H*7Eut#F}fP<fxK8N@gfoMs69)N2&MxmtE?0skZ%;{Gy~MwGZ)BCBv1BpdLs(g1`F^5B%oZe!Q+9uhDpulEsF8O{%uaN~SBBLVgv0TTC26J&!nq*q?ebu|IKd>M_K<i3d?nAs$4m>yBX^y8eZXDVY2g{<eyE9`#(}dBl^chY?RE9z*R*Jcf7*bujT1;swmh7S=zVF%2TWn7?fyo=Y7<JePPFwLkGNVqfas#J<GA)PsnFiFMt@l!Pi7tE7XH?&P|&97;X*zwA=4OSLVlq?VGZN;)ZNrKFvbwo2+NX+*vwe``fto4N&YZQ?T2CUF_!lGJsHOA?o(ZbV#;Sl8Wyb#x-`!g5FA7Szp&TM(PnHHb~(y3|#O>k>Dju0!02xGi(hh4t&0JQ-s<=AsLw73*xpTr{WDW}UT}iyD+Ntg{SrQH4^Hb(ds4btvUncX1`vlvGsmBXM!|pYF$o<Wsrg?BlBZts<|fMXb3Wlr&RPT}dG&rOB0Mxfyl!|FTQHF4gv=y2l(<l1P1)_<$0pk`vUYiBItNv*Z%Vc{2C9-P+Gd`Z&q!HNL9kxRNL(msvhfN#&wwbD8?;H~e{)w=0QNa+sp=870w5;*_kQXuOg781Y8pz0~K3_Y&`?zDT^EIG*|p@fp^u@irxg7}s{<SjM31n@7=jHT7QN)x`U#_Y?0UK0+N&e1tfGI+i$=^(HVUXBgKu;zNvKHS-ir97ny6IF9%j^%3G@#OJ6Jh|dvUq&`G^i1limtj5GvCD)YXRFYOn4(g2G;LI#*oSx;(#QCU;5*MYfeAGFJ1C>-((w_P!;`YQgCFQAeQ8dm&{S)y;B@>mzDcMDQk@zCpvX$j)<fai{BksoEwcQZvmc%Xj`w;4B#I2S5tfUlm1>#b~1*wY=7bMP0(KtUv<6abv=Tlc8o=?1-`e)+h#Bpp_9OH{4KaILI@igKgZ0``}E44inDH_|UOA*_NyHXb<?n>O4Ixlf!;z|^avr^|L&Ptq}x)*VF;&HrIkB>mcW@r22h?i4${U#?}nX|5pBQ=MO>9;Zcrslj7>q@OJkUA^tu1x$rMdQNM*@+7i2U4=rpZ?S1UXS0j#HoL7<kAwSr)XT1x;$}F;+)jEh|?*_q9g<Lcf=WpZ4`~$Gq(1Ow>|mP_`hTOzN4?y_GbAe4;ueO(KruvI^sOUsdF~nH|<TwHl<^HZqznn8{4L_UL*7xqt}%j#G2FdQP0l-)VGNT5YME3POSAMV(s`6Iel$1ZMFW3_%`u#YJH8y<=ucacTb6felHQvq&OIh){}@^Qg@@CMBI%ybuF62SSIoMWQv2aI9T^z#=mjsxK=4yu4Fg$PT~bh7Ae_Gy_I+;^=|5|-(0(j*RA3;8gEjvR>`kQ4zj#~lFI!`n}gJwzTr2pJXXmJB@q;jBb7{5GFQoPipC?T9mFGuE$Usw7I7$b3~?y&eCkNzNY<<I7$plC*I42ij6v5IK+$*@wM9IPcoKCe@g(BK)boiK6R)J6K|F)?u4GOk8P^!%g^Xbs^E8!sF7+hhxx^0Y#l#NcUDPXycM-=>FC<>bdNppP<Yy(#sXGuSs&V&1NlrKD0&c)sG;T~=PuhEuYffE&xUG@~{N0ndF?BBD#>6?P|75*dClYT|`j%c-6mF`dp^_TZKM~g;PEVbVSZjT)#>JIXP~t(Ik67!E25=vxXDfN2B)=*bRg#H13vnjmrv|jPeadTQ6MHKespKK`UE+tt->d6NDk-bvJL>O=wbnKo*He115*PI&Vy&~g0lSFvP&BSe(YUgbiqu)DvlDBrePv}18!*QW*nb)~QNPzzl2+j*N|#f*w3~h}Y#5)Ed{xrd4Z17!C*oI1H&VKd8_HVuq;5pqlemu(FY0#GjfmS3pQAtR_Z&szOcafCQ(iIdn#5^&ovu6WH!-E9{zRL!#7)=^C$ZM6iM4<CZ|c?9gSr6mTO~!5uR;`!n<!~P{Udb|;vb2>7!Zx$P-|Zr|EgrEl5pys#NoudDH<PB@(=ZE>Yc<pdHrjO#wkknE4ia&4n^Zx)G5R%w4X)&EAcGizDiyyS)t^El4$DD)GLTfD0!^pppqaZ<CUbLXq=6{wDzNDyo7o@@e*P^F2~cC##%J4MtzW2i^g@`AR2e0eoU-I<1W<ii1j${!ZEJ3=D%`meC7D~O8eCmjlHNJ6F+AAy=ddbapgt62}R?Y9B(x_zG{+pr#?uWnn!o)G{o-21*o$TUr>^yq@Ei@<6_ijiM43#u5>{qIh5QqpxuexX>*gJac7Fg4XBfd8xR+uzCfHBlLtlP)cK`x>U`H&uLl<xd+Pd7kL!mQaeIo!CUr65VvOIUXk3Rn2XP(ZS`>|IQWqqyNu0XgYMi<bYwR+hbzWS|PiN!bbz9?l)D4ImFc<Zxvk|AxhkBGz2JQ)ii62ovBYs4z*LJOQy8&y_xFSX4G8B!=QZ)XaT3`P?%NjqV?@`9T_ce{Zsp}EfW6T;)P;%eE{ct4lUFytkz;}uDy{{y7Vd~7pg^7z&G|ob;ePv-;;|KIVf%pM&AL^0BBN<~K>b}HUk0$OzJezt2vDPn%XA?iA&gcgGlvwW_@>Bmnosswl;tCXv^HFPG`KUh-Yti_l@$WkOk@`Hb)@j^;KN9PGj@BiJJ&21_G_FL^xFJR3pQzIi|3sXQTGyA3WsNs7hG^nw=58Z(Ut+C)CDwZny%)(vot`)svECbMt@m|*QZ!Da-blQWJ`<_KiM8HMto0k>MB*3JZ;4+J>wT@(`d*&8$JM$Obs=J{o4EbEzt*}Vbra&$eLzQw#+@k|ccN(AlKMyDmc(w<davNdvc~TX=r_b~*v|J9jZacEzDj+JICbA}m7?)yCDq-at5E+#tVQEe)US!PXl$cSA@0z|EluvU|F3`9`R|{8?lS)4A9()vmH+uU*SA*|u4w%GaaV^n>Ge5;y7{G%7e~AGTM^^`03`(4i~'

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
