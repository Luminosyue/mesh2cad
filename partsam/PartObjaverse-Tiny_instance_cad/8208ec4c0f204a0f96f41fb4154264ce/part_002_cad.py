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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_002.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_002.stl', 'source_sha256': 'c60a64179b7724d546b1c0ade7390ec323904953dcef00c9fe98e2df95f60cbd', 'input_faces': 742, 'input_vertices': 470, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11599037796258926, -0.3353613018989563, -0.11711475998163223], [0.32155129313468933, 0.2768213152885437, 0.12205272912979126]]}
GEOMETRY_BASE85 = 'c$}r22XxlP()VRkLocD1h!z8(<IsX_8BA}c211Dp*nlaf_aaOWHS~@sp&76-y%<FA!KQ>3;2{aQgisUW1W3ZGnfWVMD17I9=Y6?n?)>MsqkUGZ)oQi!NqCbqY2R1mUopkpIknxKa*9HhMR{Kt8aZ%quWpfpD)j3=!cWP;oc=j}Uh}ri!aMjWLzPhh-6IEe8yHYa4X7PeBcPlb5EV0U@W6<EpT`XB9!b1@M4v&CHXqb8qJN|vmkz96shnE1OgVLo`oH{_$!>x<eS6Yj+v^Y4pChl7jF=K)J72zS%*_{5Q<xjy4I^%zt1S7?!w)iFpL+pu<<Anr_xvXLX|vBH@9UJ2x%K0-OU(Z`AH($z_G7NjseGJy-jFYetLd+Ez1FQDsi)`eWyGy&XN9ksxtICqu=$*S>o9YDP{?KGVfFcU^>MqHYeU|gWq#oGYOW`KgVeKpxW&Bd{&~zlSts?}xOkp<?D$FKjfc&c8<(pdX8x!z|E|MzFZXY7P|nMe^Bt`&;`1%2NqY*Nly>f2(!<Tooc=qd{gtI3)PnN6C;mFdy#JW5i0k25gdfVck9pJ;Zm0FakGb#7-_oBm4v%18>cs)}YeS`-zS_gN-P@lDU#7}+w5Dz3>p1y3b0akE73S^Zzu<OHPh@U6?W}fpI_Fi~$Xr)VIj=fdr5_HglX_l$c!c?tA_F*Xu$sB~-B9WOi9f98{{MNQ<mdfTuJ5hfn|Qn})ujIJnWX&zUvA)j3$7;ZIaovL@ePeW?Bb?}s}IsK*9wf~>tfUmG1)6`_H+Htc{%;CD4w}Bc9ERdpJ!KbJ^l?PKW*Kwg`Z!>epD&u%ADLXZr@l^&kKL4$G9u~so(5MT<h!O>t}A&gl{UpoZC0)26KJy3--p=daL=oLQe}1yd~qg%&e{4&wuY`?sM9&6<W*3eX)bNws(n)!>hl@_!%~zx!Ujwu5b8E?*G{{<@a)pILUl!>|#FtL<gy-<FAt6KWGBSw_8bj%x*H?ay&}l^Gd8G_4tpHerukxmao_3;&Q&9jyTGEP@zS9e38p?z3b%SabmRGxt*{3jU&v}bmL_FT)4e}%Xds*uHk%*PCa&T{#U`mqcX~M54^YC%~cQg1zy<A?aBRy+i473@zr4$SI%d`c#dOkq%M&B<-M*lf6$w+qm^wobNyO&;T?DId0DSxgjYE&{gysu1-IuxICEq1Wah?;ihRAy!OfVfKkd25yn6@cN`bmk&)I%be^`8fH#eI^3ST&LJdcORWu>0NIb<A$q;BEsQnbi!++Q*tdY<C@%WD18E^e<rP|i1D2j5@%@+-`JlPb$|Vd7K1zGnG2=B9uB(_G(>N^96>=*wKalgjgz(KLd`tue2c@IR`b;CgDO;p=6U)Px`ZOs;R=k?XnMNhO(U`}}0yySbk4Q*%WT=K6t2a-UtRvxl!^ns0d=Xv1pqxH5v8>?E#kOku89koiNYlP`{cZ$Tn+-(O8+K1uDeo6ooAMycnILDHX9(oQ+-;+FQg@H*M&@O>RKSn992fyb2*uyhyqbM9!Vr)RjF*X^jCZmxRyN8RMU&4uxN;MXmjSGRK_^RtC9t`b%-zu1AfHhU=ABhNdBD^ofPZ(NC=YsR1!%#9nHWgH%fTgT^<uO4&ri%{Wr0yl6y2Wv_FO`>Exq?TuHrTsARt?_&^UY@7PYqoRwsgcQYU(0=Dby~$-t7J$$Yx>H3zPUSdrTSVKhvN^&aXY6el0T%pjN88Lw()ftdM|;m*Vybl?-|L@*2%bxVXl=sz~jp3QjNL3whnWnTe8ec&2+wx^uj80wP{6uz8kUYc^*(AGbg<3x;xx^-Ho!Z<C!NGkmqp3Z~J&0wm!Fw^9CG{dF<|18K1q6GgmkGWM2J!BaeS$`EKU=gUxckG_19m<1XWvTRq}rJooC#<5Q~<D)l$6%I9U|d?@3*?4MhiAMGReOWzl7ao>@*xi8Z_9$()1#Npog#5Z%GjK`06$#oxoMDF)*Ix|-u7n1zKqh;P}@rl&qnJ3NARKEXw6>mvBg=_MBsAnC-Tv@eA#z~8dJpY)J!-dyrC;3y-@whV2ZRUPbFHMzsyK0n-x8}7s%lNq|<0?<-&D;;evuxu0&wi8fSw4)%i4uKkBOlkwknuKm0nd}>?DR6;53c5U&$t}R<HvfnlIJI5a%MTN!FnwBW5)^1wM<W?oq=old1@Z)!QA?C>ILTEeR%$~0u;&5kRbU<3wZsYPyK<<LqG9U)`^djc>L++Z8>khHK+LZM@avhm3K1NZXT9#l_7&%ms=B<E9z^hzx1kTZqLwc%+(W#GH*YfoXFSr>Ce(1&iqqhGT(>34EJT8D79GX-xVeI*Q-_R)kn3M8v)DY`8$0mbK}xYxsGjKtYN-3M(TMyLGIJ+Yj(J~>ET9X4XOWmOKE@FCo4Jrb&NbGvxZ6juDddx553~^R&`Z=H?9P)bJXw@=87^)`0^il{bmF<V6NqxBlXWX!S}nl=ej(vJ}fG{aYcTwakzG|hn(-z%zXWnU&b<52mCJM$G<g?TPxFW;m&&O__ZXi=ZBiitumdZ{-)1|aQ^;ie!l6gDo8z_q~Y^by4PZ^PWbQ;|8AT31AM+&Gs*MN_kq;2cOI|Lm8=)}{LCvu<a{fvT}=7PmY?~#q0K%c{M*%|iEDj#GS|QSUe>YSJmq;<i!IFDy0b~%gSu?z@oD{3g4d^(@fVLnWkisy53{7m_#HMx?z@TFa=wl$HZV7bJw7etanzE-F0Ou`Eb|hccgBS!%cOrhN;~o1p**WE^_L2k{70Mia{U3FmU4S0&Xo0V*_rV&9@_Hnn8%(=duBz)a{l<D%#}lPr2UJsZFh5D(%W3W=P$fU4QapcCEvfwx^sNq`q&)8e~RRG_&N{d`A-eVE7x&Li>cg>cHs-zug@#<Pp)!uUnJz>^{m!;i`>`ITlsgj_pZ)kUNlbfr`Da$`L#|lS2vZB`!V(&&r`<IIOck@%eY?OjOX7QS4{G)>(b8m2lIQMuWhTj%sU=B!+dbN(cF)d!kFuOPRV-j;7h)bH2<A*xW0_XrJh#0yw~I{%v}3mu+($qxxAP4pF5lDDUd4peX0-Pb`IY)i+y-z;TLYo_3r!;b1QX?w7<VHm+R>@U<S8yM|G+H$Hsg=>bsxtxX@ewE_|%)1Nb&a59YXdgz(8xobT&B<hNiq-`oBzZhZC2+x_F@=ei=-rOB6x?tH6Q2I>FEsk`0WOut9glg(!weCv0edEiFyVd84+Dc)aE%U+Q2)-Rarx28Y%BIF(CrQe-ABjg?Z;Hy$<R>(X0%~T5TI>mckl*b9oz1Pti5X#4Sue%!3g1L8`XwgM^UFjWH+N6!lz2i{(Erq#vJnK0-F68!j?h9X|7~U`O-bea{H;d)G-@YGxwaP4E@40_{n_DsW&I3MQ)KWfg&%B|0TbK8l{x#3+TgcoyFB#L;G55}IzSIj+k9R)2qO$kSpGw~Xybkitw@T^5vOe<6&&uKl%)Rru`tsZ=ZjWdF*Cu2%nR}lXM?;u<pD#wmUd+AEBdtRXS?_zEUrNt0%)QUSf4KKKSpFJw?{n7LRFAK}_qnW|yvW@99QOsjWbS?L`)*cS$K11iFbni!?p<%_4@NQfu3OZYl~Rv)o%1M*+#lX`RCp}&f33SVB+5MMS*PiFzh&-S*QqQ1mVEE}uyT~_lX=#Y`o5{mz3Wf4{|e^+TCYCJEbA1{`c^r8UgiVOdf0fJiQn72>u2kDEnZ)H*V{_yCRulT*5}F(ZDss=*7H{MaN(Zyzq02AbMO0tu|<=0y664EXxfRn_kBc5Gl2QO-e1PuW$t|sa=7<BNHt&aew+7w%G?^l@2TGRGT)gq%)Re@4*%DC;;NTC4|(4!6*H6Ut9jo~!M*RN=Go%R|Mi}GCzQGOz1ZQ-eQHz~AnVM)f%3ba_iJUlPv%|E`?zuZjpTdZ-|u&m-}k=nFIp+<9nb!Nk$DYs?|y>1qcq=V-u(w7I*7S<zrtu0#@xHVVQg#8+`Av*d#{7k<JnhnxOZR0_xy9=p8XlKSuc72_U!XmgEs7Z*L8Hb_c~e^x63&4>{A)Rx1=7=ewS~_ec{f0`yf9*zs&1}d0)!AZ>Cr!WWUO@&!*Pt!`!=H_Ye2%?`hv|W$xV%RIXiS?%hAsXFXu<-ETD77nbw$>`$7d%QE-wXDV&#?0(n%>u~S=tHn2!dOZ89T8VJ^UC(~3QY~ipTjLG;w??B`!ae)FM&$+ayWV||nDfFt`^*ma?lbGYAii$i{c7V$>|Xcv{b%3%{Ueg^*(X=pUt;dvSJx*zWNwuUm3{h%P<ih@QjF&t@BX|mZB^!4sVnlGX#akB-aV?x+`G@O<!{B@`(40%(_ZTFd`HmF&X9UM-yN({i<o=AQ>Zm}OFf?N8pgA;^1GhzBfbrH<-9!KS<DLl`?()H-(~bNrI~xb<5;yDF!z4<F;lilJ>Ks`CDQRc>iyoNjrf?k_xqIAs4jEwcP=&7lzh+kGBtXG<a@rmIo$i*O*wK+xaYf`Rnbr0S3KVh_0I}0_kMr$wGCnJ{f?;y)o1Sg?x~e(#@zdz)Ec^0xaWJT^>96N@Ap}?!e04Z&-YwC&ta*@^ZnPSU6Xn|-;vFDB}v-(_IGD<Q3mGT@6<~563o5dwar#rWj*WtK7KMm@;%?vwX8oL;re^0p5S`7q{w``t<q60PhQDhncj=JQa?iCs+rHS?>9`wPs(M<A9{f6Q?AyR@0dg8A7kD;?Mc3F8$x$*fA;)_xms(J95*PM_wm)Pzcbgb@43MB{G3t7?V>-K8}0M)?^<PM%J+j)osaYNuXT-o*Dy-UcY@b}d_GoucWKYP%<?^;MjPf@ougd86+4mlGtK>DxqW72+hoq~`9}7GI?Q6OEG;ZPYd(Hn83*@qY?Vym_8S#%@%KEvX)<%YTsdi{mR-JsJ}P*M+j%L2obT{4oNwG1!(6-5UVeAjA=yWMxShGxU;(#Z^ZQ1=|Ft>DTwifn+8>_<-~WQnaDP7U!u1$xlzh+VHlMjRuUQJ$U#_$46QwK2?K9qJ?6s!ycN12sD!fGt&NtSS=jV=EssVE|siL&MaUPj>^G}oGcmBxjF+#4$_s-x2a{f;aN&lx*;eIpY@|@##o^B=W(dP2{$D9(zT>mao`k_T{9w%CpD(AUgt)1kLJIDLxTJw=|{{8m|&v=CQm8>Vnr5z9M%6O>%6F(Q!xRcC%)7ndWy8kKb#hCAyo2@&^`L5f<{jXH|>}x)*>;UP{Zh83mW@bIkT=_UHd!u`ze79~}<0ALNXKAH>&g=4b0RExO&2PpqH(y2a-<N2oIx)Adw%~DXe)5{RFGQF8sS$Esk^T95fR-sVS;j%6@K$wY-#f=N>96^t*jq0@lJ8+pgzL+CNPfRIvR~bP{@eVI3DcOL{!z~JWp25@4=j@YiB2PV_ZxCMmB&?OeSANZx%%n@>4z@G_i+0c&lUc#AlGAke^kDsM_*;`%e_MS=Yz>S9@Ly~r2gVPWuCb9y^NDy!I!um%nyc=e}|jv;L7nh-ZwEvhcQ=H`pfTD*(v$p8o07K8?Tqtpw`UIgt-=%tMxeF;XZIBOy~JoNk3ZhhxV2E{>I;Oe}P+1`!iQcH{ksvD|UvoXWUg8Z`WgZ9imQOFYOsvQ`SLeKa}r(;HJZKB=Wk#xO-jBck^6n|B{B>PKTQgFWFC?BguEA{i(Hi-EHKI<nL7u*M1kS<WL8*Kl&qcBikcs=eZxaeurBQ&m`+i-+z9&<i5Vjf=e<F>#1_S4W>%JHEt^VOW^w9>CBDXQ{=h?|1SAUyGT8iOUZg^OSa4GgHFi$a_%qkeGA+ISN0C?$2^0|T=`U!=W6SqL^n6Ul?qk)x$khba)gZMC6{^K;w!F6JtNb}`)E&}{Cx|!3a%{n=lx%EM3}TE^8^`hYtJRRxspY=(ytHi_o)HRm}^N%@}6DvCeOnT_iZgA*F9iRf}3mGz(;4|_b)xQjhxpEQ|cd>P3EP<cJjO9Z%F-peqQe8s>8Q`GoP>T#%QU($bGrK6@z!Ux#95T)nr`NA1UqB8_4)sl}o;-f@=}rgJ+E3ygaeY^(Euvy7&AK_m9I(aHacC+&|hMvxQs3<T*d6k-Sg*xm@_jA7nf{4c_49K5%;i;q|I@Zk=40Z)N>xot(Yh&DGn&l~<!>AA61^yjVrK?uki!-5suhE1PBC-&gjS^v}wYa$Pc*@ow&O__}<&pKN`8TI#=8F5Z3JeL-iW{`n1spFFbM&2@)&Q24#coPR;CZ^o=LAMQ=&e$cAk7TzsZ`hQpcI5*cFUOH(2$2spvJM*TO@l)woJHGBczmxNtI9ck?yML>jo8Zd(-6ya=_N&x?t&;3Fq^l?2AHfZWH}&!N4}EWjD}26zE2W=fJFRwe9bBoDi@&?*=dv>QEvX`Wc)#WE<R|KJ|M((vFgGiePH^|L5|)#>a_%wK1BJG^xeBgae=w2j?NvnTc@-n$GjNOiy#l!9@Kz1EA1tew)Uzs$yq~@Kjn@wj*BzerZhy`{UP1byRdbo2KR$(hOW``W(zA!b<2<N}w5P>*>3<dD=V2}Bhu%NS_@7dLrJLLLzwpJQWL*>*BJJ$BXS=(9jJQTpf7E=bznnj>udI4aB|qZ;Y0n4f&&C~?8$)JFzJ9*}AAhy0)Z;ua&`zy+l+<(n$v$^Iz8f*ZJL%S2=hbAs@Z2#n4?HWf>2Ua4f6d%x(dIb~ODGE2d&>JtRD|nKnF-QA$G`henR^BPfBh+Q^}s6s*FR-e?KTv$t%_~AY|CI<4%_k}CjB8avC@c1huhW&tPwcrQHZJBKukK)wt9${A|3_S2zrBUGf+MQIZiIc<6)%Nz(~i#W}uF3C?mGhwjH+ZQs~di?J2^xBDVS4mIvpY0h;=vxoypCt7=<M+oHgtz#ZKU@f7GN=qMaF5i#knpoy(QJQ2q=Mm-InyTTfyob;Er&4TX=z8o>>z0k{DdHdk^LX%y!?FQIYFw*A`Uxj`J{TlhN5x;_d-_QO(Kk*dj^b>oH9OoFyDTh2NFAME3igUZ_$_*nPVB2oHXuoZHZ2Q}`!Zs^lTN*#n#0o%Hg^{iXU&y7?AT9)*7G)Gyv8^C<I>d!sEG>9i9Q(5(`mrMXF=FCm|FJCvn(`^Wj+ppk=<A57{H!ZJ0Z+_w#f~PQ1b@i31JGv?J7ou8#16tpABLT>?KIda7yHh(d#LX_utSJX!S3N$Du0Ri9`qm3<nJQy9`s%C-(k7z{>kPijI_hbfM<jL5JvhFSZ&+Fz-oh$4n<5>A33$bDXsur2D&QZQ0NBGjgj9NaRZcBgKiAp9G-Y1=tkhxFrFI0NY{lX-wb(;pvjup*3`Coh?~OKMOkyi^<Y$9-L^`INo&Zf2d+VX1Wha-Vn>tD537WF^22{%n?GXGe$f8V`4Hb%B=(2?0r49}a!3<<1AY-XlzTyunDkNT3mCUYF_y_6fj)xxf-9!6pA1d>7_`HVAtwp?IQ&WIlZcaD@frB@(B~0<13QWQZxKI&KJUs&27iLGM=;_KZOiB<ae6<|Ph2?<!Jpdx4(fOh@e|k`)cYQer8+VphnR}k(d0|Q-otO!KwJts5OE-maq=@Fhb%qD16fV5nmFFc$%s4}rwvhF9kHWpy6R|%<C|i<H-xVP-4HqiIt2N|K1NJd5pDk%+Tnr7CtlgMqByoPSPA%|IL={35R=YsTXC@B;Ev9U{>q9tGpsm{s|XzkD~|kM6*-1-|5PL<{iE$)ApS{_*wN&FgMWeJotWzQ1$o52hbDH-wp(Dgz`sY`w=kY=A^yn~UxD319d{7Z*t-OM4P*a`i=9V~bN^gITdB>NFg8g)g}p%CFVKcN$j^knDvIls1HKq^4(KfK8KB8OS43xl{!0=60QxWJRP<3Q`Xm+nd)Nb<BiT)y%L8bK`E0w4`h8#z5Z{Dd#<AqTM&FRWjo2wWgF0>_ex}G8;x_m*XtL`#_BL`TrZo!XP#-w!m1i&?+LQq~&+&Uy$8q=*(8r;Zz^@}Nh<Y=i&kI7Ahb9(;xEQWi5Ofvry710g%!z}bgD?jK;rKePn6y9U51MCazVwHt`IVjn58>}aKZK?{dKTsJljl=uKY1qRfqevC%eG*Y2ZNKYkGPiKf7c35Ie87fF?1O6Y9S_0&*{8=vKGk&UDXwnr?m>Lt*DIFN~8<;{Ws2w+yXe3Vp^O1ja+A~O!_~Fsr)SB@8D^@N@d+```os1wuM3y>j)hTPw@!o5y<}>#{?rLz5>Tn91BluwJUZsc@uuCZCjvMAa=^Oz=&;!kxqog*_Hqn=VA+NTZj4<fNez_2U~|@seC5lb<m5U$*)J=I_UM_D`E3&n-4b6#ioPLhn@{T9C|kNSQzQvw)I2Y8%8_=J_b4hx;5&YfOt6K7_k1(WS=5G2Atxlwhcl&0dapA@ea@(kWcJ0#N<Pu$u#720N3DY`~)MvBUlJn30GbjSO|C-`1H1ALrl5?bT()Wv4*%NjC6ij1>~1SS$=5p+2N@?tt%#75^-MWvWT;zJR{1oLuUj}15R-<80in-(?F9i4qXhs8vG|NT^up_I?&`hLAOWlC$LUn<VV{!)V9vhop5Yt=uRkakMbpm$p(XyUWj-Jw8PfgHpjM&&<l~X8G0eg2ZL<{Bb|Vl{Cen(&}-pWLa&8h20tH~Jl#ukUGZG7FI=4bH2BFb{RQG-&|~2#9tk}XIZheX-48j$qM?cPg(jvWCfy3!VHCH7k*)#X1e$zp=o--F;HyKIgDwdl1l?4Tu^I#`3r_ccO_bLJZ;JY<u2S%no7WYSu7&tx=o*Mip}ZK%N<p_p9<g@t)u7uV{usH$2ZFbQ9)Os98|b#swcz`p{{}#}fwe@=Nbt$<BhmML;9I)N20#zM?@vSQX!3($1JTaG@a<vka4s#;KTaEl;rHl1ScdxMz*8M-!HLl`jP3`zKei*@1WN?p1W)(bBE+OeBPKltnphXaond3Z>!OTUeQ0785!Z#MxH7DOZAHNfxL79eqR?4k1#K$~R?x+A+ExiXCs;wS!eHeQSAuQ`O}+*4C=P^G0&jtwUhqAjdqGcvkA<EDZ6ZGm<z(Ga76#n|IuvmLbQszg;L>5JFBmxiFgmyQ6nVY{K<9)mkNg0Xmq2-XS6(`3@`|g>(e%#`KDTX|q0=FD$}&TfPXqsvBF~x3$o<GwRva;ni#pI15$A^f$dyMqY4ICrptB*)hPL{lT?J4_Zs>~ObiSFu(m~Vjbw>TP=AgN(HME9!h$8C^T6YXWOnL<P5NPrX;3;pWE1n4>J{6k$Vt86J&2z=`V8m%1wgSIF^_{j)bgyk^;VDjpCcnW|mINcc1-2JC8<1~;Q@jwK*eq8}dKvPFB|sBfi<tB-#5<r95R<J0C%*=IscrFy$##OT0jD?)+R3H(AT;?y$cu+2w#T+J$lU{W5bV4w?>yLL+mdZN1$_pVjGR3vI|F|Oc_*NWZADCaJK|F~cDpNw^eT8NTknb;O@1akox=j?J&2vM1+X~u&omrQ<&$k&1hxpA^gP6qp*JGli1salZN)JsP<9Od1j?Lv9c&}&JBD~a{A}Bn!>>b*Q?}eyHXTMf);0riER6U>_<7J1q3K-C;kT*o1GXIpBYz3{5^_kN#I?JGoRiR3aE_N?CvXgvpGNs6#B|&?@RQ)%ptm7j3?n@kM*1t*Ce$+rWnV#)Ujcs{=j6nsXCRN*1ZZO85tE(-J^^*l0h@w&652Kw><h%C>7F;iOmIhUL!5|n-v+%6<yXKj!)QKAhLOGiP5x^?xyO=Sn!E*n)TNIgz5x9-^kKwDpm#x&-+^O}Kqn!`Iga84=mZ>d2<@<NjD<Q#??k*4c^1wo33Xn^xt~RS#A&V^U|SE{`omM)9h!V++oBOixbmVA_dw2Q982ZH5IdTD416^75R}Ehi1!AkxDR}9X!5<F$wxx>f$nD82-}8(ksk^@6!rE&9_4=q|2gz$&~0HIY-<VD0gQB4#ANM|(*b?a4&@PG(TID)JALNFy<lBYcT3dK0=~6NcSalmO{}ABoxnRIZVe;e2D%OEX#@VLD-MT|ZUz4-H2E&J>Cl}JJ7w)*pCU&`c~4lBZ3DrgTx<|H*;w1gfQ<zkY}+`*gAk8}5nm0x8pjgb?25^M34hV0HzU3XeHEH~if#K4r{EaUyI~hmJ{5jGd<yhPl+A}Nv27G|3gVH7iTAawA6R%3KmYgB{J;K_g8%(T&mQHi|G=R4$hZG|$9?42c3uDcF;94tbi9uCxBo{kge~bWT$KL-1vEU9'

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
