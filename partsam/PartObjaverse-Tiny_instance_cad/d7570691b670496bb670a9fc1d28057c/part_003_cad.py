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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d7570691b670496bb670a9fc1d28057c/part_003.stl', 'relative_path': 'd7570691b670496bb670a9fc1d28057c/part_003.stl', 'source_sha256': '6eabd0f98e0708ba4634178610e4b85c2b4e802c7a6fecceb5f91877b4f37d94', 'input_faces': 840, 'input_vertices': 472, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2315199226140976, -0.45125800371170044, -0.097379669547081], [-0.08749551326036453, -0.23657763004302979, 0.04695922136306763]]}
GEOMETRY_BASE85 = 'c$}r22UJu^x3*8~m@((vM$9M}FduVPR8-832quge5X3p=oO5nP6clp~BS*nNFz4Lr=$J>xH0Im2-<K=jzy5!%f8Fc1_IjV*Q@ziwU3Kczsb+m%ty2G%OT)inTES<lZ<-Y}O___9OB?M!V&nin|DZ}khK;po*~G8@CF`QLo!WSHwP>TYP}jcxL4G4#Ygt|E1bDhuu(}2e9Wio*?~vX@NA&eq{-(ZxLH<sEP=DWH{?5;3s@8C?VD%_l!5U`$AO6eeOu;dH!`T?6-ve$b)uKOaRcbHSUHrC)SJ%ZK+j)gjy{wP;%~ajtPoIB?eBZO8_;oMWo8qrrb))FxJmNQePT!Ev9g1$2?=N)`zcrzk_>I0(mP(w%nGol3SINhy8MH-o{@x_{Uhs_Dq8EdAN&A7jlW?7z$fs(Tf%1L#8R9oKt+^)tFIf!nj~*|6y=W=4pV4wbeHCxtK(xQh_UT7Uds`!4#J`<a`lXj^7B1IcS6BRw;r_@!@aGcox2-6Cd%qGA-*{@Sk?-%yjr_y^MSZOAqvZSVGm77uzdQOBJ9ek&CJk{`6-JylwIq)H)z?J%-kCPYb4J)~mA`%IeeqkPy1<{%X1em*`X`Ft81xtVJO9%N>DOQ3@Mm8K|MP@ds=c+<Jn`E?_aV;cm?_flBIDs-sY`ov#_pA>z2k%r{C)PL4&SRueH_c%h~F$%1b(k~GQPGnt&o4luM*#=K4+cuE2)_H^=%tu-1WB&qz(?B-0=6>ggRW#FZ0t8n-%%{EJB`^i-zRm_?aNr_3nHV<L@f-$M(@7e%tdEi1VVq_{~1|(7wZ7`2V#okvQ+~ir<LZg8JwOLZ!ZS?;y^eKwP)-x#iN{{j~VCOS{qjjctm|t3}b`*Cz%`d(-e=CUy1+L;T!5q`f{T(+1_&{}_b$b!sD@EW0F6`?ThWfASB+_u98y+U2f~{FCZQoz4AIrT(@T9%$cWALiA<-uvV_ah2dN5sUa^n#`B{V@e^<{g*L6E0vM@TU+NBzoSPy@(k;-TJjG_jrN6iVjS-@SSWFRe-$s^Z@T4*X#R-V7{{mLH$B=R|DNL~i9UUR_9a8$@3!Z6sYA;I@!Pf@Lman;>*YEN&xl`d9d{e?3+$D4&EgRMkK0&hGQP+77C9<@$C_CfuRPn<tN2FjQt?|yUdDVLb4$kEx_mnFF?Qm*(M5;I{q<uk^69=p;^?P3N*r@e5ZafUiu^;~Pm}xZ&qnc>pYE5%f6p;W;;d|l_Jh7*o)`YOTiUhuME)}eA<hA9mFUo_xb7znagK+`{b&uWg!sW3FwZN#*&*M*S_=KTbOYnn{Uh$jTDcJC{w&1lpJ|}vfATk6_umD$Zg@JG5BgILaqJ5&ivRV4@$z})$1@W5VG`zZd|sIkj-&sG-;61QIMKa^OC7%56Tfye0dek)3YGT#@1T9Qbi7}N&Jvw-Tl_|)eHa(t8hhk=jc$qGdeDaa{pwAZcC&6E&dbjjujLc5K3uqf>t-s0`SAI*tha{mS@GN7RYN|l(#pDI&9EKqE8_k&=kJ$saah(NzS~0hpVayfzaGcuNUf+asoTC~XrHST#<x#rX>Y!tbO!hJwoB6fV0Ky0ZFvn`_j(fYcYiul=4W6V^moKZX>W`wis#79mWaQg60ZC3^JJ-Wljg|hYX|iAuPos*pD%cd-w}!Dlve1)cF~EI(Ef8f)U#ZJc``0%%Hq1+o=JRLp~0JE-iDPz-O~7C-PjwnTD})s7~}N`>!%s|H|ATLEbw=0dO_M%jT<KZmg&*okit@b<7eTOa-HHDuG=CC`FuGhb#Q$CbXwx}^FsdLORr1mw`~qW{2XtBrT+Ebh+pq}5%;_GskdC`<aO~I)(m(aZEh;_!RB%qeit9PkIWrsu&)Tdfa}gG&i=MoApNhHBz}7<KgrX$eqbx^i+K1KJw?Cvy2!plFB>a<>#6(VH`AP#b<9kC9C>;aME-jtXF~TN&O|rNPk$e&kDh;n_#Lq~(XWG-d}N-~S|xsMLT1bpK7Wm*mGDohi~cry5iQsKEf{esK9l)o)+s5^BYpTNT(@z0JV$<WSs~-Te=zF2?Gp0uxdHj_^hMn~8X*5_ljli4eZA4X#6#q13zv1k9^Mr3)8#_Hj<%aBab7e=``JImuV1T-{IfJb{kKM;o=Zl^{z?n2hd5_A|DRmgDEVjfM4c_eBp>5k+WFFMbTz~e48}MfvdMj9edLb%+^T?evS1I1V^~U~UsaAE{?EzS?;R+K@$y-ZdhUBC&qsZKG5EE<=cWCo1G3I*Hwz=qg#x(WKjt1Qaf;?g{Vxob`D6A;k~$kZb0g1mov%v!fSj^!=u<Ny{(C#>JlRj~Q}ds6h*LE!@@&1~cg*Y5sN3jVcs`yRx?jE@{^gYX_kVVt6TjB<V?Fh`>u2%X7K9+rgdTGxuE!_wJFb*~-yXhJzTf#B;>>A<dPW2+PU*M1-^KV^M|YMyGrSbP`Ro+#m)T)5-)t+N!XI)G`~3DLWq)Eme1bSxcVYdkTH>I@Tk#nAjEO`Y9IL$~@4c7MJ|P_IPkZ-8a@~H3h+m~O?u*qQ?ee{y@$k2_VLh2@k@Zlo9}9n;n&?+THhI45=Z>PkJ+q+Blh==w_KEw&uhpM}`lRhF`wd6@o>Ry>t@!l`o~vX&oZf~!mvcY7CAF+SW@r@R)Vqc}AJtnX{*rSrF0*Q&4#Qu`b5Pr5AiixE#&K$Fu(ZEC4*Ay@k2o#*NqntPDB7p{hCHX+Wj!(Tj=*&@IFQe?9x_kNsNwLp%Y*)oYv3o}&*lezgMr+iT$cHupYTDyj-YN@%{j7;8NpqU&*4|xKZJ~vIy`KPd`j9;=K>?}yg1wf@e8fNee^OWMA|KB2LH?W8@Lbd$UHHM)kb`yKH6^|7lwJ~iSe4*1o<qRB=yujyTcz*0Pk_#9df^GNyRX){&Eq&eN&W-yS-X|T-X00=541<yD+YKkpIlm$fwf-*?;OjxslJwiP(?j`V;%Qak&tu(_yK<+4y>dw2#dS|ErG3Gi~k}lFyS&;<x_Ufc1YqS@Ig49@lk$hH-xoChvFp(jO-!?!QsEFCNCq`-s`%llZl**xwo<LGs>hyZ#FPpue$i-xMSFg<0r{`0ew2ur3{$AnUx<^RoDjDG6B5yXrE3jExs?-O6~+HNQm4`@Xq0PW<{7yuWCpKge@aUvnJSEqqMsX7BS|_7yfa_><oswcCZ(Nd6gO5Z|RG;*6gs`%l}-Bk+&?fq7LvTIyymy#xM)3y9P7qKuceC>rsNA*fH=GqV3Qt>Ng`fzGJUhoO;@SL7VzS+P0lydrUu)H%l#@jDiG#J)GsXM=q2<wUffI2G63H3j?d%;Rv~c72e4!{#I8y6Zwwp9;rh-s+2<ELMIa?O^0ni1RjQ$Q+4tbP(EG%459hHIe6+*%p4Q_e}VEcHSi48`c;3WbcN2tovnuqL=82_}ydBzUx-3+q*l%pSuj6I|WVI&)cJ0BL7o(e=#4ImFJy3sxj(3A|7#SKah1skEo3}fq7+LVSMf>&ud!^_^qRx<9>Otd#ThR+!Osu_=x@9u^iZ6`BX)mKU}dNuInrJuTjMf{c^LQUwO*oz5Y>2#2Hl_aXwX*`rFzTh5x}V__e-Rm-gpGzZ@+Pzf4DY&(gnV!T6dZ&_197-fR3c+!uj&u&*d~T;7k&+#lnlUxA5OANKgkeWxY87rz-a4db}#4bHE6yoJAVA>2n?m&_b*#BY>Kgn!po*|(T4o}+#DE?BpF9l<$|`xEi&p&c+kcN((a&|@FMf4(vDKk)(A9s5B1j<{5a)9K4v$<uKO*Bw_K>u2z!K=B_s3%~6q-wTY1^8Ifo#IJe$DgAO(?t%A<B1hq0{I~e6|D@ZP(r>Q2Eb~ftUm@$H=6?YGk++e5^PTb@YSh_*dPZ-MI_qPG%5&44ybbN$+>mGZYI#rBCvCxX{obQ)nv3jj9TPUA4*Q;>{&{!Eeo6n(5B`L5X#Zo(Lh0w$0QfDR(BHNz<#}p9?~m(V|3}tyn_C4rpE0|4MSVJM!g;CB8F?PrvvorI=lR8Nx3-9o_L<wEee7Y>XU$K$)H$vV@}F51`=7mIq(0WiP0>DABJ$rfM9xFZyERasJt3I?J(IAXZ|;uvahI@9*wOQV{P){c(EeXMr;OKWWgReflt6!{F2!@u9*FmA-~61PVesc(BI|InUyI+2>vpOr>ws-tD#Xe80rz!B&)q5gX74Dht9(DwgTKd0T^^LieRr#r?4xWM;Ws>nVE_Mho9y3gqdvjkel*sTiP>?^<9LfWo6llCHw}^ZMD5N~@!KwC#X8UTS<QM6aaPvExF_Afdsg8avAC}q$-FZC<K+Cx_US6(EFOySE%Q?LpJwiO#F>y8{jxrh`s>+E_}8As{9KrT`Br`l{N3OE$GWF)n=XEH>s_oHCmTrJv<s7Q-TvKBpC_SmPHQBF#$r6KVt!^iE&Ek-LWuaS-_K#cvEn1<TTc3aBuINb;|6&S+H#CRobdTlAM^KTa(=6g?t}JKRwK`!b@9G%uQT$jS_|iafqP|M={H)U{m2o>)90MzX*O<-{-!OB_I<me{j^%BbFom&pVqacKE`=Z_&fKL_Y~{u4YHo-XUf7~<385gqUoe=wwGlv?l1Nt|08$hJ;J`h75%Ey5b>Mc!ajUxM))IYqHeQC$$6}nivG)QaKH2nmHW{)Bpv+b65KC$Hp=)KgDmJ**#?MTw1S*7>$|_5kk7$aW!~C~G?h4JkuTym`pv?*Yqd<W&(UXnI)Tq|e7>*6ebM(H@!LNY#rwj`Pcjenk8jaFv=XkX4XY`2oA?;<FNDgvYSyfP_59g2v=3g7aXEK>l++>UH1hmcLmV&HG01m2uAAi)`s@8co}2ooNW`zZ0MGrwmr>{Xn-Tvr&O<cUf3W^s+=TYE{88s&OD9S`y;h1}_s02>888s@?bRaj+pKkQe|_Euf1fUB?^zQ2khF!c&x!1S{4F=ouR*>>O26aVA)HG*8G-k#gjR^ZJ1g#sE+4ROf6*BEXKjIXAo?EOBRm?3-+CwxahmLq=eX`x3)h`8h39)~WdCWVt^ohKaLn^+rDgpzZ(31@9o3~@=6jq=>(esBe+~Dw9@rE6sQ919#eZPu&6MMA#=aB3xoRWk=l0fkFQ)&$&kry4!#Qo`x8irSNrSq5-8)VC)8>Kr^%e6m?w;%9+)QtF74bX$1%Lf^^1F}m{W9W=3%VoUyYd$M@I9B%zHSqqAEuZ3JFZ_uK09mTx-(iV!aP2W_N{lIz3w%(ehR;%M}O2IT^P<c3dAAKtq86^t8gE^KQ4alO)13x`<<Li*v}qC-JT7=x)FE^=ab3)!Cw*oYJ1e}?GgB&gyOs_n=8i4z7_GcNaVS=N`KL3QOI*&63@x+%f8+IryX$$<9%Gqm?={E9cfk~&esaazi2P1n`78w@mu|GW4s#wm?QIZ&~)@S{3gct`FpIld#2*LnU6~S9i=AXcZva15Wm9~tS5%6oEMq@j)(tjU*z9#z$V;3gWx}g-xIA@hDd#k(|r+t`dq9tLyKd-TBQfZE8AGSpPt`_{nglR$g@`x=6{UO1krTu(SBi5%<~dao2C7adhlO7gnTl`$or;N&<*o&!fV8Nkc2!p7D7H_60!e@C@b$ldRSigttRsE+K=@=EBxk|;fVj^8h$SrogVQw6qo)wJg><<&A$9Mw9m5@^`GBd;%f&!nbO{+H|igGSe`rf#;@Uzc#rtEssu@$FaITeV^j@^Z%=rH{p~b|iTQOE?T6%(eTAOqmWlgn9O`rbmFypkS~taSTj+{$%)VQ$t0i8=b)O<1qlrVF<NC8RXz$Ti{5H?!xbE6G_!~5qd1CJ{Qu=H2jzt{H6s+grH}QLPrQ_nahQ7giHL}-SnGdeJk$=5!7?+|Kq@G5rU5G!wJ@z?;7GoSs?-0Lz#sl=%zFFq2Q8F5FdL6(%?RYs^-?S1@r~}`NjhHq#KfJsO^_*KB`E;l)@7LO;<?w%hh4#f7;W@r#5#pyWDE-w=jFJ9oz6;Uc6B!XF{fln$IesdxTdOIa7s-DQuzD2Y#CYMk(DaAwPmDi<aNSSrm$k9{9%Kd$M&0Ii!a9&}P@Zd!Wr2uOajT4@p6|oDlzwBdAJ+3J9vJsUerSKn1^pU17U$SsypiXmM|eL<dMNj!5zqnt<a4>r_vQC-EpHRVZ<Yml7JDwwN4-Z~@jD9dlzeQ3Zpiv+gjL6Q6}pW3;`9dmUg=U9bxZ#j*2y%La85O>AoASdhI$6M$$T^CW<mP{-!Q(b&*As1&*@R0#6oEQy3I7)@2PNIw=Xz<uKrf`UA8Y*V&rr5G1MnVR-CU!C&0fdC)&>+Z>02F1HAG6_0V1NaU6>fzs>I|=0n~Bvj5l1hogNhJAR*iQ&i@sc4!6syWBDE-Fs~l|Gc@lZka*IKX{tA#IHME{O0OvSm*byl=a`*drS=GQ7rO*@m%uP{_GC_p3R7p>YL0@qpUZs`(2muHG1Zg^Cf+6WBAJ!NBd6~Fy9JP$90$BKGIrFm?2uf8vJEOAx=wQJlEn&;ksv!A<w0^<-EdNS3vysp>;5Co6VAQ16zh1xNcGtjAQG3cprJ_0{>!;<KEJ8?q{3z=9qlG7LU4(=^^_=$LLe=dvwP8i!Hb8L+sn^;x{w*!8&%pSJnZ;eTw+?0S_=<S={7zF=M6={O2~{J{mMx_L=7PF5<TjoP>P3bd>YYWWPS+0s7^r;URer%!BLxyBzmR<a?aY?9PQe`{zd8YK)XR8#%xHA$n{xt~<NFJWp*W{}#XbstM}3cqyKDAurJWM<c{3{#EWrGu=b+>qX9^zkha=eWrEmA;bxY!F^g=$M1mg(P;l59`iip8-8EQ5+Q#3*&5h){Wvdm&?+uR`@Ak_|07QR{>1*rV(~jtWkq|g8)iT-+Mk|+y7Ao1k--c3ze>XXWcVG~XKH&q&_4Yr%;!rB<vi2gs506oYUpo0o4lu(C$pgajMey^l)n!e!~Z=h?ZOTsPb1f8%+EyeYmYrp&-B+MAHCcz@#{O+BhS*OW&f`~8X$gKa5l8xybHg(wd;rW@&33k=4$f0zjm}Q{Ekc*$8smJpPbQ5{C49m#-(W5<thD+RXESryvO3)$-O-CY(5S7bRLa!C$A##FXZ1@Ej}UV?Z(wqh_k4iT-S(yCG$;t`}Yyaf0GO5d99!z$v@N~er<LX_5;7q!QaJ=y@mGQ@EkM>w~_1W$8VthjqJ#0@=2+)qy1I!>%V<R{%0!4x@64SCw{YI4eXQSs>}I+(Q6~(9C1T^LL+3{t?zoGy~7K2epL<kqi1LMqkCc;T}DdXOv4-gW|y&U_%*}d9X)S__@gr7`Sqlv%pWbZx%iFV?J$45bIH14pI;X3zb0ZFGjGN7bV4TaTL-egfA$_A*Q=fm*Dclz`TLE+ydC%Ru(Z3_3FDjjt@!PaKZ@VsUKHb!c7y!RVlHrqU(Zkh^LD^4JiiXD7Qb1+#C79-lYN3QsypIDp+08!uM*!V*$VBok*Lo%hwP*5Md~B|l>7X<$Bn(^^YrS7^YA40nE`|4ebCJ3fjH(^)S*-W{=V*RYVjMFrXYUn2>c#2@ADyvbH{|=RxVK5U3n{h{XNd{jJ%2RUgP-t9@@vRKzsh(rg`El{2ozg|LCK%H@<BXzpdW|jN{P8cwe5g1?@*HL7u^_WgRwpE`q;RE7ZSFU(El3eZ-%99&3K^!Ts2;hxm<{UdU%`N&F7w>xK3qH8Bs{d&_gmjB1Pcx0~U7<I8FMJ~*}p;xzq;eBShvei<37qW#X@xKCGhlJi^RRw1-s+XemY_Zahe@&VbG>6!bWzY&e_yH$qOIOp4*4fj#iDEz%^qjA{BdA5XqLuvV)-Pv*YXFSEY_q>O{(?}|e->dIiP@hWU;dlLXAmx14a{omBtv+HOx}Xo@yswY?bQ}i%iEsFw<y{(yV~@i7qWMQw#HkvAeMQyB;<viqLY&#b_&savUF_2vMB;wr-`hBf9)Z8eYt$!Uo3z)~EkgY1_&YA6pC<WO3kG06mHsuxWqQ6%F<$@i*Uvxysa??F>J06)3|cNNz&FL8J}amCm#qKyKYboh_5bTnpFOKq{@?!Ta~)?6?bNiRDeh10OIA9J9B6Tt+Gzu6iruJRG_V`_hXy@P{y{!NokKoDUPSFr?$7HkqA8x?wE0e3?6e8g8RQA%K<Y5^F!mvk+Kn7Y4xkPu2atoPYsf+5RW!v{skg{i$?vHDlHZZjTA=AHU}cJ})WT#dS*O+~D{Vo};51jK<)bOCN!7_Z+t;Ki9`CdSr=4<IBK0&mk$jwbn0%bPnYxa=nLLp?o;;D<l-h#af_-R8%};Jh&f~PR8Z?obpL|7wX69$*&&>Z`pIo2y%1l%IQ-h`>|786?P}O*R;P~7ke;{9?DPBljLtexAv5=<NpW2P=Pi{%=OYX~itR=M$xh1)Q)BK#)*l9JX4ag1HrY5x+xh7dXKdMtJQJaw~k*iSKlbcifP}`H0_9rWyLsoj6+=slL`h~on{FbWLh`0Q#*n_5c95s+Uj%?BtZ>J6<Zzo4OZ7J1<I*{x`E=hGGD^=@JNq$!RO@p2xe<NR}E+SthZ=}v3ZzOM}E+!{XPf-_>PmyD(^T{Wv26aAJ=>)Pt9!?D;D-9qICl93tk(I6@4<%2dDc(!HN>=)gyqBCrQ~ZXi*0MKLD_NQ1Z1m}5o$FLKn&N*nXa@4%8uTkw`M*;0k(DV<<+PmC>ePH>r8UXb$-dO_WMA?$>N@f?@@nc~@@jH4^)y-ODRMM<8|@V5=~8keHGv#S-p)C%^g1<xtTd5)oqUC+IEi|koJ8J1-Avv={+&9Jth6avX&$maH3u~hIeER#!Ox0Kr+GPTpwlK(O|sIn<jLd^Y9cv#tq-BjB`ftKhmbo_Ym$}LCwC%u*M6;u-Kkz=FXqvm8bXe8_GOpTb~|k)bw70%c|Z9CP4NMm;(634@;vfPr}d#up+=FXkT+0wlQ)pJq{wLtP4P0P4W*8ut|X5k+o}7>c5(#u1bGwnB=rROB>4#S0Qm@cK27mL>OAs7@&M{g@&I!G6m{uOZBFh_ZbxlNZbxoU9ZDX`KDVbS4yM}4!Q|o82y$}&htm`fa$05TV(KRHCe~#!P4PjR;-l0f<Rh%nQJUh(G{v=@mWA4ZI-fkBb?iV>+=DuR+=JYj+MnE?^=eI1>_u%)ZqK@S(G)kN4kr(1{~OX2*GN&L8r1I^SZNmeYp`$b)DGkh%-fx&xE{4NxixdDM{P)M$heBt`mfgaLeyU5LgX^kP;wb^73vIf6>>%DY;r|%L7HOcOP#FeO1DvGTYjziileDB$TN7o<Y$E9)zn^=U(XlC)2P+SN`1*{o~wDkj2cGXLft?OBTu3Bp@xye`29ZA=Hv@byXLfb>P52BGvs*kPU?E{PV#h`Vo#@aahm3|Ae!Q$G{rYH=mrg}OmQf+H93@A+G(?#)=<qiYDIDla!H!voYcZ(rFqCX$(g7H$eGC5sin!;$wg_3TTxq+TQl!gG{vi_s-LU*S#fHb;@;FQ<lf{zXo~mJ6vtA7$g$+){j=h6)S{MOdu+wY`*6i-Z(fw+@Rs!t)qd^U6|bi$PTv13ZcZ&tF3oy1rzx&NQ(TFfNBi||l84XdJRF<qw8DH=7v}hRQ5%xI$OEaf$OFkH^-r=%PTsdD_NS_O>d*PQp6pNlou)W>AEh{ndWL+4_et^|OmXr)P4RW=HOsHP+_e<rb&X?qjrU>lm|jRR?iW(b2gR4E@#M?ovoyu~s5{B~$aAUF$<x{YxirOPX^OA2PO4tlX^KZtXOU;|K2$u(X)Bzzo2EGVokH<6>Ll&g`-tM9)Uo8@RD(K}e3BYZ9ZQZUU!zVUPhuX|s29oC$PNwfAWHwCUL>n`7Nu|a`6BruV<o@)C{Cj8CGU6I?@kM*Deg(_O72N+OjF!I!})+xe`;59SAIYF%t3MTxrE|N)cs_oceG#U8;X<9Jrw_>-X^QF6s1@A`8N3qc`i+HB=rtCl6;uDpM03SnHo$EX8$+S6py1eCM)$L`|;Z2sFCDIUPJK!r?qgJH%)O}nqm){;xaVF^=OKHXo`DN2atP{XHvb%Gs$CUifz=oWE;6HO>ude;v!TJvIp}kLQ|ZN>PpT>&QDWZjOs=%My^b4L{{oaE<r6v^(2=gSEDJ`X^K106t|%^BDW#;qPmfLk(*Fm$xX<$sb$DzI5xFuin~yK$X&=IX^KbF6wjmfCimu;&7&zkMpJx{I);3ZyoaVZoN6P7lNV6ilBZB>QQMN0mM7OD7o;i9N-aXpN_L^<BP-2Mb|Gh`79(dS=b~07Cy#wDn&R{{#kpyUt<-X4rPat*as`^=jx@zRs5)8cAaW0~ow}23CqJORAS*3k0Y4yTv_PAXGm`7j6c3>eBQK{epbjG|9Zg<9o<$u+o<*KYQ#{ydZKyq|qsXnO-Ke9;qZqdvO|dt17<m};_NEpfdy`Ai6n|ztRE<8<6vt6_l6SJ!aWuu#sXAF{2l90C5NaFp5OP0iFLFO}7_|vGjO<ITO;*~4>`R_V9Z8-@UQ1KFj5?aUjJ%SjIEp%t97R4&Jw|>;{fl~xtn?uHFY-(39`Z}_E1Kfx)Nt~1@?+`(@?-Kt?bmwokf!*l(>_wiQ>T!X)*_E5yVDeBqZTA9%}UNjPD@jqn(9JUnwgxMoQ9f<tTa724cS6doQj&8oQj;0rZ_LvO3q6zMXf+CMea=PNbXGDK~ubr+JmgrPF_cTM14S3s@9H2{H!<)O>uc@9daG69p!0?N6-|9r&wzgpQj$9E+-!&Z>26EZzZp#&LXcRub@sPuOKg?DGs3yCWnx1Db_5-9jVQzZO9d<)u?UAZMc?IqbaVGV!f+GQ(TVPjogjvS2=1aaw)E1<@j0gZx)#1dm1#3e2*MKolaIdgd9O$O6^BpN}f#(BhMx;r}~nWP9!fUZ>O#$Zzspl6h~8+k)z35Xo|N{SCW-Rk++feQBRZik<ZZ-zt(=OWv^+9vsz$^(_3JQGg1E{D}6~;rZ_kC6<L|$A{Ln9;?(D4Wr|BsACr|SE=_$%R;IWX^(i@d?Nh8waa#*av7ZH|*kXYxUP4nml{%h0m0XtUPF9+YT$Y@UnwFf7ocvGmZ`9OerD@1YE#yMfEL00Q3poQd6*&Vr2Q?!(2e~*kFIj0Ra&dB1YG-m)@(Ah<@(A(`4d=Q_zw`4BveI>ArH{x;)%y6IpA~1JDXvW|Pp(a#OdUa18gBV@POkW<<=48Ie3q^_`RrZsIhx|DG{u)_isPuq$V#`8<H&ocYsq`a8>uVE8_BDvi^!|UOK6G>Y6#gN2T*O~<n=dzrnoCjaX*^kzSL&qzT{3c#SJXK*6s#0#l>ifbI}xMr&c3pC%aH9k(HJsEB%e^LVlt_)w=wIruYywf~<5Y`4D**bvAhyc@uRxS?PB2Ch`$#4EYH8g45np?^9#Q_sQpJijPvG$w$cts9VTNw~-H!|DY*8LET4IdX9X8e3$x~e3$%*s@CgI{H!=HO>t+M;>I+^b*bseb;*sWnaGXE-Kn|BN{f)YlSk4NPoNejPasdCmLN|e&!Ltk&mpg&)*>ryOI|}hL{l6?^&|g5?M?Nw{5n5ZoSJH}{5o$}tj^$-s%Jy;nY`jw)TY|6GknEGsfEZ&vuMA53s9_nAMk2rNtG-0|Lgx6_18aj|7-v8f0X)ve)B*7tT5#_e>h|P_a7O0wMrw;p;XTQse{t|>Q`{>zW^?dP(T'

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
