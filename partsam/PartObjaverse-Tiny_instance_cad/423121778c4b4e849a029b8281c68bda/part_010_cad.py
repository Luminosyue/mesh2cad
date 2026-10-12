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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_010.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_010.stl', 'source_sha256': '27f2a670674457f5c6f5cc4d5b3d4e7597d0688843d9bb6c469e66bf40f15b3c', 'input_faces': 912, 'input_vertices': 577, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-24.1455078125, -9.306112929152732e-07, -35.24448013305664], [21.985023498535156, 109.55386352539062, 24.62339210510254]]}
GEOMETRY_BASE85 = 'c$}qu2Xq!i)b=LyK&T0!vjhl`K!A_{p)MVy*8n0c9i)XS2+GnCqzTd#*&r=~N)<%Pf+C<Gy-8aVdXp-mAm845pN;Rk`k(Wk?~7;7eeN@N@6OK5&fJ}uS6Veqmp(+1zhX+x`R{dDTv<^lWm7_wQN4$a=-;#V@aVybV*-?%%+sGM=eKCzyj7<FWt1|uRIlE{dk!mAO)XWUPt{Uo)lz+i3>z`5``~UvhV|-Ae8cVohxc~);r+TN_IC8raaF36RV$S#tG=iHFaLt53|h&m7Rh5tZ8b;OOHRMq<49xWqbkJf2fDQ*UT@MNfMw($;qMk>do%p4ynOxAzRX+u=C>x^8nN*?`O&7`sLb{gm#`mW=*gS4$^Ora%$w($wI^QdTQP+5N1b5aSbc~6>&2U8BwY(TB=&KQ+OYrk?`PrrUz^0dIx7p`SFKx<%VT~~M*J*DWdBx!7C|f{U&e7cXAa3nx^f}46km7l7W4Xdo5NYxt}<_qxyigzc{rCxiw)1m*EddO-iX}8<<a8XgmXE29cA8*?9AoSTPU}v9#nM!^V+*ti?My1n|yyW0DS)~VXT`f^Y;32Ql38VcHnwxeW)Pk#|&Uz-CUW=W0kp5nC%ndnKygyRQb8SO?W`{Y)*?4KkuI4=Q8tGsmSG8UR=swc}-^KuUz5hH41<qKAG=pJ`Cb^u_oo0=enIq$~R>K`_XQM316;4Ugq_;?{WL~4wZUN&cXF#&bETNT)(Fm`{)y`m|xH;H`|Rn9m~(vWG$CRP1wlwVSTZPdHqh4qI|zoO>^?~<%cnE?8+zoq<2TIe`{es=9S3(TyFJ{BK9>JGq2rB&;G6E&u>#X)v6W6eoc+nq+2U5aXnb8iwNH{Jc7%a_xwYCu5$UAx27kS=K5;WqyXRNQW*30g7mj)k=?7K>__`PtCauj<z{UEcw8Cw3tqYOK~uh8xd!pRyawK`5?$@Tc-`Yig@4oI$GxxDk5ZyfXXcG4KVAi|-)t2BU%dI$Q~so!Z}Rg`@c420TOL2)t!LuL2zpS7d96CvzdGYQx4Ry5n|Z6-;u~C_7u)6M`kZ--d1ZSJ=_hBqb3e4cxyrouGD+%l)3<zImsev`r5?bm2hTEZCXb9{`}Cu@y_D&v#lBw;sfR6MpT=){DfQs;sYm6$Z?8&V|4{+_9$1ToR}K#FYez5dw!6#g_g*&pFZ(ne_9l1@e%$`x@+RyJ4{zj8@N4%pdzVMMdwKJj$IrT=e(j!S58m|p0dJxISP4g@eYLqI*w3JzIk;Zl+bjO-earP}rvHV<H#JML@T;cywXe(DGhX|(uTn2b?%QsUlt1Wu<_%4FyKZr@&n&#2XSwh{wexFtm)F|`$#c2we*QD@e>o$MKgQ_SMMx?q7fU(kXXWy%E4J0Ne0VLiV<)x;Z){j7eqe9d8{&L<*WLziUY_OuT)*|K{-1n3w2PNN-dXDHB6!q;d0+gvyaisZD}G!)t=^8p&!02oy~tTT6Y<)e&$F|>Zk+hvHjw9iZTeYmXMN{LvBz^MC+~7SXyDy?GfxPwzCYZ*ezwZI=<;dx1Kw^}M9TSOS`_itHyg|I{da~6U;ixkCw=|{mHn*FCH~*)`ZtX~db1}yf7zQe3x9n+&r`P9y#(vmUdM1bQ}?~(@oIVy&$CL>W9HS?m9EoxrTw~v{itnjFs~KQDDzQ)`Fvk<@=@_K>3BFlSB1bhmV3U9@qJ#kRYVQThj;7E0Iv?;?q{!jTDOWX@79kF-rT+|#;=}NG_K{#r?t!H!rP6v`ulIH#`*GT{=u8~HZZTOt;*xMKJ({bwx733`0$!C&PU&?z}F33%)FIyDwXQZ9`=>khtCoJQ%CT8s^7T8_D;nK-)kL@18%={c>}zGe)})}nDkqh*Dvl9KUriPu$P0+@EgA`YF2+<jZtJAz<cNN8hEw7-1lGn3EVgPDCX^UCwZPz_e5~JTXT9!J={+!&d=Fq1osndY*(qb$~wnUM*mrne0|JY!VjI>k?p6?&Bgw{kC*m}vNN*Z8RLuc^B=4r{FJ;r&)KuOa6KERZ&l>`%-_p?%o+<hzBArfEqroU?*HnVvK(I-KPNG7d{mF$YrBzBlBCvMcx&LXGJM}+iI2IRx6fl<=~ji?UD-XT2$#Rl`^=k3xl(w3-&~h@YmLsl{-7?;@5;PIv3&pQEu}p9mh*e9X75yq?|&wadGEOG^4@V<-yALFAN_*MtzO#6_tmBgZ`sv&eAC`oUdNX=%p1}lnu1>%A-rcka(VB3q^>F{<@e0j3V3gv;N{ceL-5`>;a|MR-Ww0Nyf+^3^6tE!=EoB!q}hAofi!zhJmBTsc))Io`Z>0n`?;DD!2MiZR6_hW>C5AcHK7FeBm4IvVqfb4f8QyKx^q0P^>|%@uk*xjX}l+XGw<DJ-WxZ%yf<#N-@VPeH*R-%Z`|(X-FA0*Z`|(k-niWYZ-Q5zAdYg&<B8{8-W$(*c{iR<^W%x<)9gL*yq8al=L-yw=S|!y^T^<l{M~IgZNR)$^Qg3A$=3JjyI3z=iFtdke1DmnmdbnGDO}3)<vEW3)mKxPS3a9tp6xR~mU+KO<{+-G_D7?cf3qS#moYFkiPs<c%@Mx+>uA1yjm6*JM%&TCzdFeM$G%;h`;StlHuL8CS2C}S$y9)!>s&SAKThWFL2dSsLVRE4Q8_N>h^2X$fAzXF+dsd}ym@>(#~VgybFLq?tHr$Csh4~&%v>Ss4>`6oucdb3@@r~%Mz(93#JrX8H-D#?6L#I<arI<wu^*C>f$b|!EX8(h0_DC*i9BB#n-rNh`@b&B{u008=Q3wU6zB5%{k8Dpn)5hst?kRY^>{T)t=2A{kBrRe___3fW0^PeJPPM>w?0~huglz-dA(ko%=`HhBBb6MF|Q7NaEaQ{$PvxFb+4ZIsra@$@0!c`+5TvV_!$<)<ACzxb?F}yvProjU&=bksr`IkJ5PKR+utb7^Md_rmdae7sg;=5j_l+1vQ8^}U$tx~^Gfzs^8Gk?t=LyMC-dsZ1*QM=Ez0qpv0wr7`uRLkZ@YfudN8A7nb&U0cdOQ_HqYbw(30Y3#v+abl^!y`8*hdQf1*0KyPokDmrH-1MaH=%g(S{Al3DETWn^hiewXV(?>AB2hs((_ekAYZ>y58+m5}Gz&gD|Al{}BzBj<AaXnzcocDrkG9IWKN#P5;5qp0-LLAu0~EiTD(p1aQVr1kiP*RSlQ*X4WQ;ZEk2sr|V8+Jxc!J}8ruOL94<-<0^U<R*SUm3nQNx7H7m_$2dee(%&8Ihi-gmEq^ru71elxccgd#Mg@t$hgt3GJi)KCB`yuoqWyDV=i1?mCL`mpYS#FO1rm8;dWHp_GMnL(puKFDzxN&qIBve{DgF}?zZ?t_G2BcCA?it)_>ZhN_#!4%)C133CE>c=L5{!x20d`%PRAGW%ar#<;s~y?4y5>_+<LT`#ev*bC2IMyZSa+Ppnvl#}hl>E#~!is<9vS+CUlKiXCL$Jeq;mHS7|lxZTvJJH<YKM~UBxeZ}v)X>DWPdZo&`Rs9N5zrDX^-gv(6Ece5Wmh_LD$x@z1mE?J=K4RW}+hkq|8qed2@l`wNmuHtrc}}n6@y%`-&+nm8dnxnUl=D13*yeb)H`aVC<tceV)+IN!mG`-MKPgX_A`-{$NRairxkbd!udVpKQ+EF)^S}Uu<4wEE3W>Y^s-B0-lk%z<m-Dx|V*lljk7%5?a;{@uuWE4r(XuS(?=7=jQ|9e}v21UBKT*E>o)u(X`}}@O_TMu~;-@l2INz?Li2rthuehEHHR3p0$<R{f*)xZ7@%32>a{Oq_tSR<;=5l%LrYVJ)|8OR^pY`Y#x39Xc9`jbMSn)Huh3F*<i0tsAl>fQH?P4i4c%D&*y!wX6nJ*3LpT9&huPuw0@pjuM(mzWUl6mReThdQ*E|-4O?k65!t+5~QdtrCK#qW!maFBWPhl0{?3l?WyoBN#Cxz+ns*^hp)sl4Y6hspZ4^@+@ndy6n{FX$G=`O~xU`=wvI&hMS^Rb}Rl-yVeX{l0t1yq>?c>>G5M$j@cl-6Pm;Pi|Si|Ft4NmoaH3^VZKRL%BRfJMws9JUhVioL;&!^Tzys{2pof>&ka!Y)$6vB~|&kv;sFC%6ji_A?zpgY;kFqb24wfF`IeCc#qr5yuE|RE4xBt=C$Sz_`OgUtP%TKTV>sP<aAj#|7at>*UE#+%xiV#As+Z!#^3y<g%A0P-wRE9lgDwbdvji&wq~Z2aWZf*&rj;mjU3k)zuR0tR^yEP9i;87#k_S?zNfVIg_+m$j?TdMX(`WZbnL_Z%?N&;j_u24mUf(9pZkZsXFBux)^Z$I80Q-N&fjM@5}DTym*V^C0bg^!RK~6kWd3o4^tVpun74!TGOrKoDe+<0q$<9=0p7T@Ovd@(F##<1EaLY{pNRF7kwux;axIenFyU<;KQ;BN!uKyP<CXS~*sJ|dF>n8QoBOj~<7@d&OnAZjSJwRBB(AD{A`97>7goL`Uip327QXM(sH|L$V{w1+`#Peb>}%xA$#I}vteo%#pYXbnT`vdQYs>4uU_YZShVyf+4P|>hYY*P<vN}ZYceh<5jK>SR-P&iwo5hNWeY4lH?{xa=Q|1dE;dsW*vP$^thj{!jC*_d&^84}p9c@MTV%|_t&NAuveK#K^Ft4uaE9+hLTFZMd@y<hze{bEB^@Pu3xjb6+Q_Sn_W7v;cp#je`#>LN=SE919y&ig%>(dG?E4)%s-j}O2#eU8Zj^C9DKT3O@v-rMt=#hKOpXws(;Gxa9{QBOR%-c<x9OrgivWnO9jbGXcAC$uNY<?m8a>kUdce(trWo5r+V~VWL-&}cz{cn-}U|L6I9$vQU2G?7S4`rX|hnu_(X>}RIygl%_%wH)zWnJaZ_^WK6`ku5`3q{tQg4<u=c1)DGT`xXP=7T$DF0*~N^Ri!{T$J(k!=wvb|8MQ!`9}XJ9j{}nzZX8ieCsZ<j`4i3wA*FtFxP*jY`jjQ4Bp23N6M)Ihxoo3yY1lqJ$8%C=W~J&@bf-v&+Dsdj(J?4X5n=EnNNsi|Jsx6vJcXK?zh}e9_5qzN&QaBnLTkU`+s}9#GSjMp7QvbbNNE9pEdV+eO9^mA{&+8Ouu{~mt(E)26!ttacgZKKgJ&MV`ZKDEx*T){qL*Y4&2Z8=^*9QQBI|I@B!xWTt=`wm-WejL)<^I`PYM;VjZsSQ*YKFsW;<F;S=nqmDIC_dbZwAy1@RrNV{0`&@K<pT(0fYj;7m=8QWjsevEcE(C+HP_^bR}*QB55Ev28R9R}TC|L9jrs`M*$=_=+G^h5J|>4)m2mHgdiZ}#uE>X@!~x%`!+pWALf-`7sokF)x}7uKek%o}gWd!)MWQT8Lun<wSH)5GMwGbRn;aa14c|DNi3%JO_@zpmi-UaOZrlYLH%1181+qw*=SZzto1=8hZ29p>F}M#nf~KS_AR<@1h9<$5u%V;oZ=WgOE|4+)QPPya#2J@xoi?q4d#Ni_)LWZSjR*dF7mg>lu)*yB0#2{I0=HDw%Dm(_p4?KM)yZ4=|RR;b)x{9G94&H6IVD~IEl*D)_BxiBxBTKQ7?t;{1f<`LVOcldhDJ0|8Gz3(Z7ug5%PV4l(opJm>PMjSpu<~4n2Q9fs(1<O2WjF)*(4I0C|y<6r@+BjuCd)`3y=b3+9-aG&5qt`QUKazRez&viHB&Os0?w5Jr#JsOt)0t0;6V6DSpgM5{KPTb}3vq=NHk#ukZyciRsKx6*nm2A4yixeu{&9}t#7pcyk0)NbUzvFY@s*DF%68&0wnsc>A|A8KH<o>uW)i<?h~KoPv*r6>yu^D3;yuNQ5BYgQBtEp=_|S<b*$(lfnIG|Fna<2>h(C42pW5!+{2prOB#t%RI5w;`^Gcj2?sej1E~ht6cH(L-&ouwIT6N-cw!0_sxq<jx>v&N1$vyGB-u5Tv%`yJ*zZy}f5SPdMy>KLwd1JABUl{nl&|X((UackHBRalE>}Dz4PKxJyM|Zvl*}jDT_aJ>ga(O2Ee?MAhmWll-`QB7o$@ix2e4nyiCjakKBS*4~Uv>SzXRTge3;!@7+4uX`a=w@OIXvIX^nJ~GKL77)-T5Bp^5A>i!uPnA|CW?zl;`_>w2XrqzV|Kndp~C$nMcdX`hYP_)(6x(MP=Ugt|vULEPRW+r+n8R)Wfxyw=VdvSC}2UF>jCeU*9m=^p*YfSpW49b8|o8v3_D<{X{P@R_^OrZ!!NE#^axPN7j+-T(XX&UQXuu*k0?u9%Uq!<ncmVzx$}~I+$H9R_0yXf8ET83YGUNNY>>vtjpO`D>1Jh_Fu<SLgJ+!ugkihg>^q;LbkH(r?me%q0+t)^U5FXm+V&lS%*|JcV^zG?!RuS4IC?ea(mV}AFnPe_2$1Ws<sU*$Gm6V)i{xxd2@jOI<3+yN%#)3u4`dkSATw+dF`nGy0M}>68oY4>&)i4YP_y(Es%9-73<PQzd6j??floh^-kf^&+e!G!2JsA>UN<@GHz{?b$A2o@apgz@*FFB$$G`cJ@J+guRY8l^UfyWX<vYK>~|=;o7eH>-F*<XR$D)N-Q6E4SD~7py}RGx@#F4~c>NgQy?*TC*dOuuN!vFW=I<wM-y|f)&yQ)!euwGtW4pY^K5ai`xcJv*JP`XjtNiy3!CNh`ALO26=~h(Yto|MR>fhzHs1U#Uw^x=Fd+hhQ_2BaEKA>A~v>(TQ4-D{YFPC@sAHDXfyN?O~F0aAA*N^J%Cwh1tyj#yMpSCYK%>TYR_6=>1pS1nQ;r{k%`;V^w1K>aZz_0#YUb+9mul{NOm+d_J!nBXf<$1?{ADQ;4*-x14Q!Ch~*4OCb=a&Dzw%+G`ssGgYuW4Lz_rdLL^TbbkiI?nMvTsiN?EJg~WS?EZKD(jakoxzWi*R|}b1vdvJkCX=`SF~Kuv~l3xd@l{o{MmK@41M7@i-Sj=M&ifWI3Op%$D;B_P%)LjR>3Lc@yUu=)45;_mce1OPIl<Vnmno6&lW0XyJ31x2g?Z?|YuaPF&2qc5+}c)xU-FC;Gfq%-eb8yo%<YSGl)A?3c;;77gcH^vOq=S0~DO9v$a-?AABLUiCl!W0;SnJkz>;%=3|ZUg+9ud9HJEzDURUB5PGH?nh=DIj5vHmvc&Vu8IBDm2*uR&NUg)`6V9d__3T5{y9QpzP|8g?jo{pKB^@1c8>yLZyl5U_cF13{zv^#cs(vf>`z1s|D=$tFLn`o#rQ`0Ls((qHQ}wKE7HD&gjY{oWj}i9jq={r72ez`yxrti@zbz~_<1bnxJ;bmQfh`vd3qd`eX-$BcwfxuE4*^fmh<EVAILuXl;X^5Q|8M#y)9qK{^(NSRjrVer%STz%f6T)_YIQsY>IoH?cyvc=YO1w^X2st;Z=Qk%X40i&f~HDf1K0v<B$8>Tj13Q@vqs7#NIQGxx9BAqjQgb<-xf}Iw$FOU!0S)XRVZa@XR|d@11w(JSRVYZ8^_r50vwqYT=_2UwGy_m-o(hbY7Ip@0oX8-aGHOym!8HdGCCe=EpN1xx9BiO7riTkJ9Wt^HG|;XFf_Rk7quzz<cLkm-o)6bZ(jXwQ_FR#JOc_jKt&KIL+n%6{pR>e$*!abJTXl+wxqq>#m@2NyWKqJIe#{6N|VV=d|fuH(&3G_gvl^@437;-b=Ih#CvJ>o_NpYz44yQd*eNq_r`l^<@dyUF7J)^()@eky)^%xc+a>PCj6eHNj$&fcL8?U{PJAW<aY!*en&vRJK*Q)F26fa!{m1dMwN<k-=+S)Q!r~Z7C$NSy9TX={I0=R*iY;u<aZDXeg|QGfw<$Q{GLL^?<w?gr=^_r{C|I;FA9<G%e&iT9@$W@HrZ=yg|{31CFcOg)nVRT5GvoP!FlEPMA09}`QB~9Tl+tidF0S!IsZH^jCo~qsQ8a*F7e57;q3upZy#<f^?XBkD^h-MqV&M;O~UgDpDcc~)P_?3^@X>4h#&R6y3Fg7@(X`Me$Qgz_bhs3A&D36hRE+qmJN|}oXv&TSAHVDC#o_)&XrazEcfmIjg<fPCON0^hVbf-FSvfpZ#Kv|md}a{UqOC%W4OP&nHDF0M*IIx$4ZD7`(E<99(9NOu1618AbcPB-H_$}Zm6j6=IE<_zcW(K-4g%b%I}*L{JzPEd@0X0-RJjEt^9t~mMc$}7%hs1d_~EkgeZNw`~0MhNOlML-#=;VAN&9HleYMZG5^<}v|R~Mlv06;a@CRRoJ6{dzkp7733S3sp_BXwcnR=4$ca990`!T%Lx4#pLbe1>1a1de54at0L&!EhxHWW=eSL6m=o3-Cd3c5;;J$!N1Wv?#zJR;}*%0^&aEU;XZGb5e&I{QWm=fU|NY|Zo6ZzM{5$*%MFUsudByGqZz&7wP$N|8|fR{tQ3%nfo16+F(zEgm0T$=)X9QYWnJq~OFFNZG^cslS0xX*OpF~IMlJY#_01}092?&1M>rasVJ+#7mWpp?0^BclREcQMJBK<Ue2;G)3QgscHv3VGEaYXaAVO)ba>U^h>LtOZ;Od7*fJN&#0xew>dU2OH9l1_&m(4jkoQ2EL3uN}s@H9q>}fkATVMGjN12`{)Z`_X#*xCpiI$@OWU7Ltr}}dGo=$cD-OT1h^$^#vy+^Fy$>op6hQc@)iQS*L8;dIPjz=!R|9WQxY(7AHyyQcp+?3!4anVboFJhOM=ZZ<X4AH9NNp(e}N5Q;z+0b+OW~k2VDITuBi_05w0h05%40EfjG+l9QbqO(RI0TEhWN~NB1cSzqNsL<NguQNuCH0Oeq=Hmjv(X$+#bJtH37%&jBVm7k0@$nB<2j>*qe0<SgJ>c*YN5KN4~dFv)j-Ne%>_g=;1OPxA3Y`J;hHBd-zofxskdBcJ#;kVYcE5%NnQ5srWj<%J_PLjGvvb%G2B9t}Ad<rodz2{vVY^s=xa{e3*oBp*z2EF{@<@X<RU4Thi2$a8t(BEfe6jszbLp7fdl@?LfJ!6aKEpKMidk-#eW60oDZijXRBOUQcQ$hIUn6}Tk$2w;-Yu!+aD6_FPY8SRrtvNa^}4S*YfZw=fViLegY3|I$#8+=vh4dBz&yTYa_uzL;R5x^wJz^1uR-Zb!IfTtsG81lQq-qlG?1)hp)D1RvOh5=8-y_zDwIq*=Fy%O@P0yhO80i9Au@Wj>e;p-re_}b8$f*S=q3iqPCLCEU}JPOzKM1CFMLEr~MC;1LArQxvY34S<y5%(VCaA3-(@nSacY@a-m2IOquQOKJDN!(1}nc#_=0o}m0u1<0><ZR%Xke}lEnZS!-v(`sn3y#XX3V0RxDX?1so%jn#giipIq_O-{*d0Myi~JSva|AlsrVIQ>PX|2$@yii#mvAlVm%veeB<v$$Qv-1l>8o)K@nyipAkHcSd<*%J;BE!{b1m_t|BmbFI>Mz9!=)gP@HN<$fz37Gi?AWvi{ME=4m}0j8eD%7n7Gy8NMDJ(<G^d6uLMW&>vZUZrvXm~c6|_@3VkZ>;o`~AC!^j74~6dLPeC5>qri;<Pq-p|o;#_4gDU{LobIHaitxIRT@RNJ5WSF-$^%ybt_WL71z|&&u5<Nb)c&}p5O6{8g@B7fF9w_!m}D3*$vEIR_#v)1bi&!76V3=dFR;tqRfMOM9roG4-$NcrH;-g265$+>WRnB(0Wc-PL9i#iG7@3pn?P>?9P49K27G1Mx;jY>GQ<Z5`RF8zfD3>g0vrq+3>!*WoD}M$y3j)*gOR5}r~EgeyO`u#xTYHPYTyWW1Fi<#9eNkY?(pMsZJ`rx1xYrIk>~P_f$Kvjn;2l1s|C9lVB*RF6PF9Ri%I5oQeoiw&||>8RKzYfFv(YnB*L#1Nv@B}(61<hUn&3Cqze$9FxjR<D&?f~!0BOA7<@YTtq;8vZ~|;ekAh49u8+D&K>a5`Z|}oJ0TY)8x{FDcMrsdx1vZrbLJ^r6dTC(ACtrcQq)0hQcX1T-gO1n-8<H1+FT##6`M3`LAmk~eOUSzc`2xJlQKE8Xby5m+!Z%<`dAo59ab&X_cpCWKz$CjmX$vsf#sP0Z-fnOq(6a(hgWeVSS&;~b1Cz`_V+V8>hd>Vkm(xk1&<TgZCI~nP`7zL4Oj3oU>k9hlgonURMWV62IB*5%Lt&=^t3EabVYdM`uI*I#9fCa4Hv*H*FHSlFeIs<&j^s~}M}S|#hHUA*Bv}sc@=Nd=;hXrWxb6VtWgl!qKLY#{eB0m%UxjYt-mk#D^x<E@&r9U}f_u<=d=Yt9z#Ra$56?*YyGRGXzYEzLbvG4U3}hH&Z{RTC5Xfmh_#pJ&@Ocn*L+w^QKoa5dkQITc?uNpq9PDaAmItObr@oXA?N72Oa8dM!3c$LPIzko&CRqfjD6a2?JmR`RcWo%Y5cnd%+o6ApM0hM@A>i%sLmbWXyTILrya(=mAALLgZ3o{AvLo<hCk+O-3;O#=gJCztNr})01M9$UeN2WOaTNOyrkEuWJaIn&yS6{T<~H#6NI$?PFRsY|c^jB`k{OW*-$5SP+(Ehxe;JW~7yK?C{5|wtz;xe&D0flFp2|P*Wg_y&qFoxGeo5bpM0f^d17Nbv<D-)t4_V9y=Ybv$nFCx7A3KthU^B^wC%hB<7U+|JiQfi07n8h({8Z>Wfr+R1=^FG~PC5bpZ|H<6&idO2yVq?4cLMh!c?gN{O{5d>bsu>*fk{%#N9iW+`8Rm7r}*#zYzg0o{R6bYeWbncyBGC-2yz>6Fz!LVX)dIBH5GM|f@e<!PtP?2b+`>}nh))h6EYvL+inlgKj{AVfQgI4J*cf{T%+;q6z)UuW+?8L6`1DuD$uh6SA*;ZTpG9v>`MdFI8EbrdW?58?o|LL*%*nwMcP6(0j5N;`<viefNP9vYk<>yZ0LI<7I|^t;=mK0?UbdlljcL#@WHXrNtX7(m7tR>>4O_VCs_@6mXqdzn+Kk->7*6NUx7TrNlsdY{8h*!{JE1>1Fwc1;kn401!)4uBd-zUEZ}&^2*^sn5x`|2V}Z*6SBGp2Tpjo$$l1VDN3~FgBo_defL<E11~Ao8Dd1ADBU}@DHOP{{R8Mn&=fIBeO6V&f=K)h4t^r;HJHnX*o!FAzwE&Sn0~ZdIybO@U5iSrYdFdfD02hGF1o<jJa3<h=0V00_-Uqw^atH7R;LVWV0aLm5pll?wpiF-QQ#nW$0?q)O9x}gAxkzS&o*(!ply5I2aeGk)%KI8}FEFJ|$lru=5~jM!g*qkqJ?fR}svzpJAZ!TdgI)l#Ffi3yPT-udBWwkTz7H}JFxA^vs8^B}@J8sHAvXYTchWab`Vw+I@FC>wg8ULVN1)^dLhb?%50tzR$Uxw5NEI><unL?NG5|O$@csaiI|Bq$xwfJlB)<jz5_lKnLEv4$R1T8aQ6@^+Q5KTLeac0$C}eTq0OVzZEDB8NN0gD|PGG95ZKz9<TY#yq4xla%Adhfxpy)Xu4*^rX6+>N;3<fR&U4;w>rg{qk4uT!w9|A<*51AGCGv}RO?xbYM^}tJjKY&~gOsN_2N!A0d;-qMB(clTw|MfTu`BBIt+|)@L@-^fUp6;YY$X|rKrYOUgC>zNyfR{pF0=XWzKJw~8E&(o&ylBXJz-5sa1sM%o2YDJ~6!1diErQg5*P*V~LVgCk7<IP}ayf8a)YD?f4}hycF9%r{m{KJ2BT;8=eG;w>83|13W8{B~`XxNvNyD6UDnR7P0Kuo7G{Vu(K#l~aG!phBaXsPlPCDnL(Td1-6v1a5Jj#*3LXH7GAMj5;$x*<so%GyEN}$L;f&X&kODDa6`~&y}uK5enwQcLbHcsjQ*&eu^lbSdw0rCwW+!lIU*b)w;@zhC~=pN8rO!BlMiSRi^(pe`R27k^6licH^pP{?>FX%sm`^HK8p%Z=zo1eiy1%8V1{000c^heOi_7V7}z|W!Yhwty4v<cGHA0gk(``SsHp%Z=#oA1Cs27V0xkAVMxz8Tkj>ZGrr6MhK0&EOvbKg6|<fq#ciHW$EM0Po@_&`&}q+w<TrfIkmxKqs3Wzy|bBf!~Al)f+mgDx|CLK)#!o%Sm}5NnZw=hTxX@V6w}g(7`&9q<4Z%E^wWEFxgQTPY+3YZrEf1m)i%E9sOm5Bs~*s0>EYR!DQ#WK1w!7_quej3j|ht?1G(C7?SkNun7bXM4oFm&Pks@lAayD(*fs)o(VWNWOLx$z?~o`0(Syl2Due@8SoCsqrfDoKb-W@2^T;)(xLnXfV)Ev2A3J!1nAw7g7IwKAuV7Fwj_@MQ~r<O+<N&DiSTh?l4l@)1GbR&E94nq3-TD`GvK>UBj0vXbfCzxfr85g3cdr5@(5RO@B`SBybFBKk>z1u9@i7D7%2Kf@MK5$0en4#tO#7ikxv{M5BUt365*<lPl02d^c$`t`2?8qAH#-Z<v_ue0tMd(M|p(l+F0<hup`{rsiT%o8UWcBxQ~-sIO%Q3H-X=B(jX_bhU^dA#YwH4G!U{MaDV3>{hX8^G9U0vC+|Zi9d>Z5rU8K=>Hc5;q{Kge2EVYr|G<RzO8;ZKzE_@ce5D=YZPhdbzvF?<f3)!0x(8|h0~Dy7RR'

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
