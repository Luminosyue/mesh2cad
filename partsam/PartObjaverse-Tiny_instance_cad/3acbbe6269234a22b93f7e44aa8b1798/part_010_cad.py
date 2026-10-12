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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_010.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_010.stl', 'source_sha256': 'cca95f7d9b8060e28cf799cc7d44204d3f6ece8cff18cd8c831481ab6226e27a', 'input_faces': 918, 'input_vertices': 560, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08589021116495132, -0.008550107479095459, -0.46212267875671387], [0.08589430153369904, 0.2213876098394394, 0.3340993821620941]]}
GEOMETRY_BASE85 = 'c$}r32apv-xVGnzL2{HlEIEoIC;~Ddq7r0H1WAXSL~>Rfl1L7_utYfob0P^yJSeijg5)5G9zX$!f&>APd%FASvoo!K)nE5g_0{|AyWjTobePyv#5YcxF0ZBjm9U<g+`g+-J&MuDYUQ;Ccj-T{N2e|Ws=V2ESis6DefbYfc=5HS@vQ>ZU~5F#&Rqs{>R<LLyKL>QPnNA@m+ji8|G@qo-fZ8ef9Ed3Z`k3D0bQd0fbJdoc8UI6u6m8CmF#NeE7@<`|I2?_qE!f;{rl@JQ4LlvyQ^+g-3)0?$e$xuq;JnSvQzj@h8LtCYI#!nq4V=(zBTjUaq)9xUyAf2H_J&s99K`~ho4`s@<)Cy%W+>^s>)AZqsqVfvCMZ$-j(IJwcl6uSyCiLmY?#S^qrbXs+=RIWjR*$m9m^jr4g!}Mfp^I(MvKvIJ2%QXa0f|Z#~^CRa7}mMo2$g|BkBv-7Lz_x?9zA!OK61pRECRR?BkY?yGjV*G&5MZ$C;u^n9A#(k~N`^>I5Lk-q&%LDimTRl9{xY*Xc&o~+s@b7tw=dp}nBFCSCo4_vPN-HVl9_i~E2J%bIVD?j^HRnD1vYJb=CRppm{M%E`>`gzq~OB<?s-fk?*aoKJ#x2^nxg;f6Isy*!-1*ISP=?__-@GEuY{)VRHQ-1H}YJcfR7vIj&LDi>M`jfK1#%EOZ`L3br-=QU>AMCYbl`L=B3RxeA_6eQcr2MrfRDaRV;dY-(-`=uEmH$r;={qMsR{2>UQuU#~B1h(}@{TL(<<@e$R+G`n@0O(e`tO`n<8y@cgX@~6`0AfLM3w(firVgzJykhdd#L>Q8*0C1w32>geQTA!xpj(nf1R2wl|O8&+HS7|wcWL^D*x7xYJcf>t6C#f&%J-B?WP%}+HFNcwcYJa)pj?ZRqZhC&PuuclZ#Wl{bdJ^uk?;LH&RWO6S}cU`JIZTc*_Z1TcgVP>QhyIa(%VkD_^bjw!bdNtzK!FtnVLBd@B9XJ>)pFDix5v^XdyLyuO`n|59K6kt#pR?WNtg)SGXueMI_Bx3){X`Qh!2RQq&jw#1vS$B&(qxJdqf-RM#B_rJV;xbA=WZi%4Z?|!(;f9B)s{7^r~Urw=B|LHrYJNSKFj+w8wOTODOlfN9dt>4%A_|9K1y)XN7)+=GzKC_bc%l5ojUHbO)TU)(;sAFKEEayaqPyfpgy%Xmv$8ASG?QbR2QS<So-xm1#>p(4aoQyxZz*`?{RX~-~%<sEHD<6<QKeJ(hx1KuRHhg<dC7JJ5nX$k(9)4+jRMw}&Ab)+rO{DJ}**#xsz2a(|geJ>z6$~fN_qD^}jQhQQtR3(zBR@E(%mJ^j^J9L)iSxYMwW{t_=a+ebxpF&;3Vti|=eAJ&)p5)mU%RaxzE758`0l{fsvVklo8xVtVA2SgA9~I2+li}GJ7=7g^k4JB^kd^(`^LO5eVy-K8k*#7ANTKfWqq`-+eiDMi~fB3k&h2}eVwm;_q5}$C-cbkWAjM+#=J9qop0~V<S&Q$74waGXRTMhQ~IZGWV@Vbqxx~w#M$2d4S&>3)<0}@o+b0+4$FM&gM^(j@5Xb|58v3c(d$RP*_r4q-`?t|a%K-o^tPMM*M2ztY+w1-4CU)_7=GGS=j(~B620{a@7T6OjvK>wMs?gJ>p8Y@qPLzp-!gnB9F+OtGQ$#l^_;S2hu4qQ6F+F?Z)&y6>&No(Bl+4Ye@kJtU+K=N`QG>R3~&3}w}#5`X7@Za!#BUqWmog7hu^n57e6TfzTG<MhqF9T{nF&3Y)`wb^7Z_Re3Vm_)5h<I#}t$0glcx4;cMsWnN_=){wqaN<aVnypW$oITUk`QJ?8hVghDbuoIB?XZ@Y!xwD)=a*l`R$l*`E9nEjyFkLBY#rx#84<~y4T?eO}#U$h@O<<GaKWKHq<sr{~e`_P!_-f`}Pr^$Lcdk3j<G8g|^*5~<OW&1k|(@*#H%fMM`-2U2enj9Bz-%FPH1p?|i@K{5i?^GBrkHevB6{h*-yFR`den=k=wQn8|4PWQGyYM+r#jdZGU!N-fUSGG||5cqgKO8;PyIp;}GW{UOtC(*b-%MZUy90Ck%hA^r+SmEouXlWkul?_RsOD*P<p+nh_qB7(ACt7h>)RDJOW&^9!PoxU4}Lpqhu4qXY^w5?ZB_ZXo|5Ib7ayJC>&KlTc^<caH~h+Bb$v3d`ef<vEvd@?`F&MRpMui2KiVPl-L^lda$fj;lFZ-K%U{0s>rC3=^}`K~e7#-mmwH9zXI$m?bvfh*t4{IdyH9LY<;V3?{?UA@o?o<5_m3s;hmDr`)}oNwuk1A^dB<C%RPeCOziCbKj<?Wn9i(sV`Fx_>zdns*`PTH?>Uw*?`3bUKAN;E7xw5vp?`xGf!8`BVyv5}FbzdAR{n&Z!#-L<bzb1a)X}&_{N9rj*QuE+;-#o<+Z7sReH-753QQPIX=dK<i%Xb~apY@eG&eTwT<nE#EzWI)C2jX`6{M&oqliKjA%D+-ejl&D8q#voVTl(&td1~DLlBE1L`_(xAXP@e?lOv=bJ5Fw%ob2^u$4PwqCnG;)PKwu$<!gWD!SUYtXk|*Hj{kk;OW#g+VY_d9;s@7d-|6*(y^VZ54tpE<_>T4;enRbU!ILV#{Gabi<vi=IvDA6wSR?7%7gwnMt=L>$Z>+jCPX2y&H8pPk9xdw=TA}>db@EHsWWLkwMd=4CESKe2*Z)-IbX9)nkEY4q`b0WBrpnRRV>{1qe{pxLEGNqoYFw?nukJUupBf|US>yF&Z+(K_<DcrG+F@UN^?a$p7o%l)TqiiWX6^O*vGe}SInuZ4`|~49Iv@1<I^Q|nQMFs#AeFzPvu|E#Kl0d2-@FJGXr=NeboGsM?c4pQ`^LF_<@_k$cw4ezuh-Y-eeJs!{rT4L_=8?w=W9P4PL#fVZisp=x3Yn%&(u=NpFP?)KD8h0GSD|Zt;t3{<52ste0+PrC0FX;%sai~!5X+v`my6x@?v$|=&t<W>RIafUYn(|p5f|2*E`;vxsBCv^;n;GR6E`Fja%#R6Yu!u<I!zuUT;>u9{*PScy*llpv6d;Z(eU0e(ZWf`{wnA;m58wvS)nTTTbk}uYKcsAZX<4>xZC`uYKpUGH?0H*UulcZ(ct%Tr)z}Tb~yi6_D){s&DvK&fT)Tsw-b#&s*)+ACW&-9;tkN-;t%DI=__n`)=LrvYgPag~Pq$HazRmWUsG}tJ;rjH}e1dGsWx2^6^7`69!4``q6gpcymtGA1M8*o45PM$?%Q?r2k1V-#pcR?0K&~9}OY@d=dX~06&uZxbHX+KAWq*Z1=zF`j7wGPrKGPzapoMeCAQi*ZKIN<%|1y=S6t`Xtmv}1^deV;CjPux%!aIyS25CRL%>bv>Da?$T{W5o(JApBl9D>?cUPoxb4m;qwd%0FY4i&zsEPo_IKX;xtn+1h2Kk1{`8_<z4Oj(dR^|XoBVh?Ss#uYvHn_>&{}T)c<Y_M{+c<*`LA&v^Nn#HuK9T#?|2U1y}4bs8-8ruZn!P|;FHRaJtxVSJK5{&@uq#dAb!6Kt7Sd(ef{0feC32k<=O4^W8)S-^w(#;`nY>4OW(zh&Btbss&aNzsOD=2ecz#d<9OmE`}1SRjbwkm_U)A~mXm&~OtWR)?cewN{2RZ{_xh2Ks@~n~DPJG=V!m-a3@`HM>*Ht4H;$`Lql(Jc^=Wlwzt7k8!4K6o@@M_#_jNwLb?(+3;m58YHg=KcS?5>f>+1oxP7mpal9eAj|7M@+^JC{<eCx)a(holv&+(1tx+Sjp%5fTWJLvUe=Y8#`z2>ja<l)kfSl4{@4>f&DJs)U#Rh6%g0~ZqHymnqtzMk*)q}gh|KYdBnljFQoexf?g4?HLR*!}x+3)THdALZLs%KMIQ+7Is8<2%0D`N-Gj-=)XZb!L&Xs{X|?`0oqw^?R<Ezu}B3r(HV#aTq_c@Vf6f>`YO9>^bvq#nko552sZ<^>yrmxvHG`r+xeDW?8SUTV|g2@2|f8!H?~)zW%v#%Gb_ToAT;?&Bar`esPObRPU|kT)h9Z&>cmG%lY$d$%A#hev>CBc>TzR?d9rv^24Rd`F--W?{4zvTOEq~ee$&*3U{q0e`X%Jb1v=o`OG8j+gttlR`YXypM34RJ=QqB`gAUH(C6#=;75%7U_IOKldpaE$7QYM_Djt7o%e%r4cked>sWo>3H2QilzE)L9BZb!F0Ju+N13OeYxU`+j{jxKbggUs$9b(v`QGyH_5IE_8P)wo%UykB{q*_wxw2~hwo$%${<WVg+PAJ}oW#!KX+P{&*ZTK)KUg(?f9V_78!_Lw-f*fL`TD-Hx{<HP^UkgVWW9~+CGDHnOKuAJ#`Ti+&FiI5h35uJf7g?~^S-++X^^bXtY*IJgotx~u*@^AC$(>0Plg&8`TDxCfswEMjn+`PKjw8ZzIom2hK+o#pS5pZ4~M(0AK@Ku*2<uIZZJss=JmGS@#5Rwap;a7r=Ig<tNo659LDZzN)42LFxvy)_z$=1=z7PGzMrzE9Z<e;|K%*aBK^>~%f9&%SzTt7cOJ#AWAV-VM`x{(ugBY3BVS+lo}I1ojr-O}+KZ#S{iyGYwg0dC<qZD(*!^+_e}3$KxlZfR(l_qkwQt_PJB^2^eB=3m_RZ%5k=9?SeDiq)zWKZ&+|Hk`pI2!AU(YKpo*5(azhB_HFSai$-+X@J^!R(MY=7f9OmO()<7A$`{vXvyUjIj?#gFrjAN~9%G+p`jL!bDbN7;M-8s{D7&Zv^=eZ-H-k97Xd_ngN)q5OY6ce0wk>mBF%`IS>}@w>k9z;it9o6q+mg^YZj<7wY~z89%?Q~I&@R)eaj_ev8Nj`z)Lo_~fW89vWHBZ<m4p9gB+d>-f|8Top?BpLboIidE?Z1FvR3(o#V`sQ<BYmVR7&w;I_hgJRcab{pf*<WtDdGE>oGM=wSa<5Uo@jNzC?11#m=eJhdcIrCDcn++6^Et5Hj(p>}wD!&C(!m86)OCRQoc#Ki6J`0vb9Fm!+DS6ccn%+_R7?8ibNk5CEu?Qg=XV+nP`>eAAo$ue<s0u2+&;<5H{NT+eB-@Fq@R(mkCWOr-fP5s<Gn_B<bz4x`RGm=sovWr7M?8I$9Vq|T>6Cc&G$8tT#rwYzVY72$!qv}+}iQdH{Txx<HO1~-a~2Md=F){`$_r6d#;#oyyprJsXEm=o}D8z)c&5hG1c4evG;xFD^2sZkK@#n_w}J0_{Muf`@!?meEX~KQ?hpP`LXMqtfN#p#(P`so9}JI+5GwX{jB!Q_qNXd?$f1jyr+&BzJ5>b9vv)w^F6qI%<y>+?nK5aU%wabwMahCkNmxBy04x8sioFS6wNimTYvq&Tl?mFaI3hH&--reoA1FR-M^9kzux=z^!xg~zcc8tD#uuF5FG6HW9tpxIwSqqx}fT7<o?<zb7%VdMXi_6zPXOVHS<|7;hOpQVLLuS`o=m6H?CcRw;%O-kBH&x^&X*eZzTBoQLhgv@AqTtNovhb@YPeVhru`3u|(!{PxOr|e0$O0L~r@A{AKv&x|i*{620Tfo_JaH<J3vBz3m?v^NSik+cPJ5^W8rC)jFTs!;-x9*Xx?JZ?1O=|K-ou>zcIxuk}tHyU+2CE4{ue*vaqf^<9xS$IkJMH`b4Z`}lpme$4(T&0O#PS}Tvp{c>7On&)jdy>89jJ!`&izOXJ%`{sJNh>@??#YK#K?T60qneW}MUZ>|)>b^k!Y^>|E>dutDxem~7wsC>Cee`<5km1MH6Sh9Kz}If%TW$QlUauJLde&bbz3#D3nuWgh;rW~P&2^Rb0P>A>m66*u-uKp1=R4_MdEZ-~n18X^5^sI<I@sW~wo82N!@5~}%EqO>`m@e9ID7w6Z+>iD?$-sDdGqx;US~_CWxjm;P_^YNW&MqH!l4>#rEjh)4%gf)eRCbM+wi#ZjdjcRp*yM^W1Vy8R>M^?-&hwN9NI|w<~r)|->*vFTz4HB*;4t&I_>CyP`<IQ+s)8ZZP!=_9?CjY<(uoqr;bqh#yWF*#%NVfV_mvkWWMr^b?i>uC#rmN-TTtdS9#lCual2d+^q7Ab@k5j9m+S?;qT5U-#3`+_QMDAN#9)mAHg@*|J$z?RQbkt1a1pk`sQ~B&iRJQH@;J_@AXynF}`bXCQMh`<vR$6?;s*Mmnfg_CLF$-u=0MQe4ZnP2hi{K_p80*&0)LF$468?-*H&9k5%EgswdxlgiEXMKJ0aOR5^Sn628m#3w0m*TJ@LuuEe6hg3YQZpYKo{zC#Hftt)-~-HJPd?`!&vkiP!T#Vx{jE+dmvIeZu6(w?CQ^He!}N8|2N-_ZoKuKn6OuEKHZyPL?A^{O1c)3NB^P`=&L*WdN%_H-AXRQY@dr0Z#yzN*USyP<G;)oxD3`>H;CXJm=*jN*M?PrbQyT;KO9T9$~+R$i-X2hXQd!W93s{`aR-Js$u6`gE%1qfh={Kb?9xU|Fw3V~3^mTT8JB!Cmo1-ad3Yybr#Bo`NsH5%d>00#8TB!PDWiXnHs;Jit;q&QdHwa5J<c+zjr7c7?mLFP+$zitMM*y;drV-;E*!??Ly$d*E|~;2Y=#_y&9rjllQdKMBES3BkM3>F{p&9YSzvG%Z{j-eai{JOmYOG=vcRG9ma`v>E&?{4^oBA=(LUsN0VaJQV#F7P=P}<EI?sMMOEq$aeS?QI4_j3p|b}N8hK{K7B2?BmFD5E4qVzj!rVmjYbN(7fykHLw|>VgRi2u;H&T*^l$hMd>Oq7Uxv@1=ixK(PV@(OCp-il2@iqGqNU)n@L@~oZcDKU!6VUu@JP578V|RE8>7#_jbVonT!(nZGd7-Kygb9->+uuM_=;zHdb|x}3=X7zdQ9$S%<g7?^cXJ1xGu&1>v2Akc`%ap((~d6=E@JWubw;SnOo=S4?WjzGXHMUe|kO&zK7llq|RBvH_+b$sdHTLIdpFz^_U=d59$U|j~jx;ait<!33Xwi!{ADAg=myVhoZyaq3|v=1>Ob!iv9-w3SU95!dDs7R|vs>5rQwFm*GqBY4i+y8s35Kgm=J$(IN0)xC~krE(0I3l#20vh!FfXIud>xZi%*nTf&Xd#&9FJF6zK_;U>}eAsR=cF^CZCM&ljy2znGg0+*-11Xn<RfJF$_{VTX4<KYL6n?JC<y~H4nrLUkbp@ZN-)Z-;WaBELpTcfYTt>LC<6SxWc-W06^H-#IZPs2hR!VRfk1N0^MCAKFxLv$ZAMxz(n1MUT{L%)RA!O7@)I2oRYz6Z~P<I!etJp8kz^t7c|gy8Y$Y<N687=0HW41bPpgg=MH{s|TPCOB_2uH$E5Kl2iTyAy(EqU+$9@OOmZqi8aG6#j`2d<2~bAA!Fm1kXU@;TdpOLU49ev{80`7JQ8myaF8$uYgAog5N*~!*9S{2*JJ4&*9$iTZG`1sA$KP=ym+gQSKIvY3N*d8oU+#9^MKcLVtu0!6(p@@Co<;dJH}QZ$Y=gTi_|^9C!-c5$ytZgma?V;GFOcOX(F$u?WH6pkKh>z@yP&@MyRX+7s>rcP9jQre8YKSDo>7-}R(#ds3F}>tXc&Ft)A7!xxN~FQ}^?KUWx6SJ*c_#<DR6v(XlMOm<<McA@R`xShkeo<m#falVbQzm2}pbKw|s<rsab=gvvy(@FYX&o9B>q2I&bGoJL^6s+g0;O=O*K<XS9tmnSqd}wDlADkx|xzSE&XSg$Cx)ULIDj_(GZiU0}LG%!O5I&BcfRDrb(F5>)cr&^M-V9Ghr@)ip4roWX1DpfR3Fm<Sw3LeR{U;%K9r_Kt4jzS$hDX6~qJ7{u;cjSmxEtIz8dsxnD;i%Cf;U8CJ$e(p1>b~o(_ez~pjTlLg7eYuLa+0)@UIhBIgVXr+bfALIsWxVhofJ@Us9*xgy6BBdXGiNz+>TlXkWN5?a&YH4EKY3d5#Oc(B5!ww%rRI3yX7Lu7En9_kh171g|FqzefmeMhF(?WD$bJd3ZJ~&b{x#8_|q#KejLGA+B4*b%(hAC=rdgXp|xZmw}7(`x0<5v>;pzei(fSei+V*rh~J>8PNco5l)L*u=tk-P79|;Gr;NLOoZSpXl7VwHaH8M3(W%yEdb|&^PxrId~jj3BwQG_(K2uu+S4Y=kt?*c=Wk0>w$MVJZ55&}Li2j+mY4kyn%lEqxoHETIXrEWgLV>{-P3N_X;+~+J?)&6J`tMV(?|K~L!o6oeJc22w7iu%1_T#FD_W^zMz9`N6=|b5xDp|_2wEO4&o+vn`QiN3wFsIW&dxp;L36{oX}cn5A-E8IPy{Up7lA9FHf&Sx3TP#Gsio%6M`#%ji{BMT--nCC1=0C%LHHr`L--*$9l8ci2M5rv;Q(x*pIWK^1gAk4!D-+O=m&5HI5WBy&J1Tmcf#4=Jm@hv4_pBK1ug&=MN{CSa7pwt_%qtIBw7Z}9^HY5qLB^F3}=IL;ETMRXf8M>oF9D{&JUMDOTwk#ifB2wB3uQn1XqC{Ap}=OE5McE@@QFDXlb}ST!s)FhZck5;39<J0%#$)0Gu1m3+INjqB-Ckw4rA4yNrb3ENCG(3!D!v2Iqqdqov`(a8a}@Toks^3a|~AKr6u|;NoaGxHw!8EeRKdGocT|ncxg)E;s|64$Te=%?77~(-MNyqdDLlv|V~aa2_-ZoQ3wvgBFGh(=K^X8@Ad1JZN#aIQy9g%>-v+fAXN|;B?em@aNHk$cF(nZ$t>r%vcbd6+b7rA_Ol-^TQ$puR=?~A_RYgR)j?eUVv7CMF?JqJ_3snycDerixB)3S{@c5_+zvTEJE;nG!7Oacr02379n^LS^yRyxDT2e79n^HniU>HTP{IG+X`+UjjGWYO$eSq2<}Y?Zb}IL%TghDm!(4RHcN%zQ<e(BS@^s5@MCC8v_0Gs?oS9#L`TDk@TY{}73c(b1^fviI05YqC&2v(!7b3Ha0~cRLhyY{so4Mfgy0_u!JE)s@FqA!2ws40gBQSy3BjAuQ}AZ^I4auiI6n*i$4YHq!6&2fRFt<`Dg-B6Dg@uQR0w{N5Zsp#oJ0s7PY4bYf-|FHdztxJu)a_b{1YKKjBbU)@G?U1LPGEoG#Oq3Zy^MqKySk*;0J`@TI{pf&sv1wR)pXIXkT~$Jc|(g8JYxt2CpOpe}RsNzkp{Gf(N2Ocp&^bA-Fc08O}_b3Z4+fdC`~?jYZL)zmCS*Xxxkbd?y<F&;#&3_$zc3{1u#p&V`fU_t=Ke3Fut7b#!}eqcI$P3my)?kA~p);nnCGcs0Bc-2`uhza}=Zk0KTa)P665N1$)RBj7e@JGc#89eo0>4&Swu{%t81A^0HeAliI6x*A>%??(^92l?Cm#NVEIA-FdB1bteYI=qgy^NfdfjFEQij~+8`Gp62V|MeJK%(z=jd+BkwmT|h4_SEBc6JvQ3eW1s-;8|!WkUAFx4?y1vq|O(?t<biC)cGY?&pW|2(AIDb`0;=`-U@Ajwhp8olLhxfhX+!R;er#;_XDZNdBLBcs{^U$1;H!Oje*p2hu}}quLG&)8o`O^qCo2TNN|62L?HG2CAcNpCXjlL6Z{xj9exZJ$8Div%>6^$<rsgL@uZLW2RSDkWX$Pvgy6;KJS+8_B6tBh!Ad>v2o9lht<>|B;7#Z%EA?C^_($}Bm3r<Id>_4IrJf%J>vO2!$I*MR2*EWN8$uuO^F7ZoT<{5WpOt!?7rX`i%1S*i2ws9FS*hm^!3)v%tkiRj;ANiUojxB44x`Jh)N_{LpV0mAe&)B}Dp5@rjmm`JG=$)fEv27WibV*14t*Ye4t@l!3O@o@MytS;;YZQO;78$lXnnXIJQbY=PlcZjD6JDvEJE-G^c#2sd>6e9--Z7{@5BGVY0@YSq){wFu!TMdSh0r)g0BaZUW2d0AE3+NDzy8n=xgw6{QgyR89a^s7yDG7HWK_8?I^ekZ7sMe{UP{y`m7H9nU1zeM?LDGufngg-8$$s_!|3G2NnBY2fdGfpLVQ6+@`%BiAJ?({9!501d9;dA3b9!79scr^gH+k_(gO({36@~jlezN@6kX&@%QkP0i`wJC*g@`b9f^BGx{d{Gkg(!7rqGpflh*jz5)LMA0`C%q@6^2y@d9Jdy*qKJ@={NepNiL6VKtq^SFZ1-#r|StO3Qv`T1eE7+MrA1{XmKz(wHvXjV8s{1Eyu+#niFqVWtNxG~xYZVbPG)`wq!>!A)@53Y+gfE%z4!6l;+7mdR3^ZXnKKZiDipM#%8OTf><Hd+|A;X-H}d@<VA7ou?%{S`h7pF@9x&%wW==i%Ss%jhNe66Ib-FTyjUF+CcS(TVV6cnUfRo&qPJGvEYx7MchrQtm8tCfqI>ZKBZ}eHCsFw?JQmTfptnws3p60~&;bl-mJq2iJ_o6PEg)1%y_EtHU+W$Ke|AQ|OcMQ*dpx7F>&RYoj&c_{M=WdDH&C{tJZEe`1}M<@*m2%)j(6|MmXm)6ueGi-F@Crx(wgqvw${^5s=P?7j6rx06wK'

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
