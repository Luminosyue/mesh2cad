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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_006.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_006.stl', 'source_sha256': 'a1a8b610c2ffcc294f2c44dba0d77092574156e5702495a5d823feb52ce3fbd5', 'input_faces': 1280, 'input_vertices': 690, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.05561736226081848, -0.0455317497253418, 0.04706702008843422], [0.19592511653900146, 0.3173903226852417, 0.17057333886623383]]}
GEOMETRY_BASE85 = 'c$}r32b2`W-nV;KK(c`3paT*G$!UoLC^;+wMwB5(VOg@I0YQS~uq;Rz79=cDU{UfARI&sED$0T+0Wp9%ef{rxs=uCMzH`3wzMfO(_w>`X-Br~+-PLvP^~Se)C_`RL{ZrhEyYOe>%8e{bN_H!+HN0oy(7xS!4yiaWVN{Hj%klD$&iQRSwTXW*#u{#oF4LpuknV|P>iEjk>s7l<1z(w7gA#`(b{*JdP-2gs;+u9IFr=sLhxF;1(9_;7TQjb51z)vt6?|iT|HFT>N*gYZ+St$z|Ez-NB&`p29+V8Wo4!dhT(+X))88l&j^@KHTOM}&@n<$We}7^B*@)w`>afMh#81vf9LMnPab9h@)oIVB{;EA07w?PaeXT=Bob3)3-gWBzmRou1Kj5kF8#ZN|<C8v8KFgUs(R^_7<PV(o_I+);)4ofuMbtOFTYp;RH0L<aS3fTqxLt8iG#`H9Q&oRl{+&*HLtmbYsBidmU4Qu(?>T?JD|9}hJ%$g^o>0;K?>p^#s98jP)4TPnTy=anTLH%hdyn4h>`yDa+u64MaeR6PHO{8D80XOFdycoR_jA1e^P>Bm`qlnZ_3xyd_g>!zyuMy{-gep>o>b=(C%J!2AL9NAJW<kVZ}9PW$EP1r_n|Mg!(Q+4{k@uoqj_JS(#~<x(<eASoREIrdtTG)^ZK%#R>#@4^St-Gft8un{hRIA2=DXfbjHK7p6q=<_W$^ibG-xFhe|o#H~)@v-}`RWR^I<`Kk-(E^J&q1`o+D@eGt;#Qa;%Ehb_^(Z{%g?calE6wesQI?Y-v>rQ-bs+k4v?>NtY>=brPn$Mm{Afk#GioKGAdpgpG7?Fj_7D_=R+VDaI&hti^X-`W|@{Teuq&z0Np!TW7DNAsbxTb<vzuhDJJJG7g(zv(0KfdSpT{Y^jqlk&ld-M#HGy>3q^@6Q~6vf~4^$Mm{A>CLkqQ0E=r!>RwP`u&?ebZev<&+~X|wBvmR>TZqZL)Di#<LL_(P~KlF-rL{6d)l{+_x9KKLQUm^qdR(!Z+d<Fz!bbSw4=BErq}KF)osgh(waxy|Mj#FH;=e3A9SOg1JwQhMKCR@&-{qGALe#f-Z#|o{wb}tMDw9;)ztX+=%;+xa>gOhrq$MHK73)O)8EiW{MJe%oby%~xg(kn-pao#!Uu~u$MOGBYG*VbDAre9--i8ZXEk;Fv2`{@^XWJ0I`5%ChS`jBnLxz&<eROJ?|2{MV0t|cz5?s<2M2lkWqRGO^lA9Ou|eK;nqIfl*JKav{O~2Gzb%)gMfE3tQuoO)eE72R7v9(s&4;?=ciJDCaD)5dZRhuHO)Q!g&4(5wI`@h16a1XTs(zV?o1^*kJju@S{Ts75?*S|Qmp+a!t?EDEsc)s@t)KdM+Y`Q0i24aVo%^c(sm;-Ra7v<coM4{9%KOGR-oLt0S~MR_Y@^=abBZfpxz{+Szcs(u7|rY7m+7sy2B`VXe0+RQ<tsPa5zXu0uj~EFhp#tt?vrquU->fyMnts7@cO*|WB7#pBfRHzeL#7A{NV46X#eNKo%`he?>nM-e~BbD@A(Hm=e*-X73*z|=B-EeIO8AQ_B_{R?O^Zm!w2ww<@Iq)?;fW_SMG-&20G(kXx8SaUSAi(hYQV9$9W1L_|5U@SxTfu^X_#q>t}yWjl<cQ%8xuX(ffNhz5cz2@8Z{;oap_%n_mCkt=w~z59S!-{e79<{e4x&&&f2#`+G6H{{8yTzr*#tJluPH)4RvNg+KG{@QC9ZULW6Tv5w=!4fX!+Oz-~gy5Z;4bbPx0T^nBiuEUu&aeZ5l^Nzpi_4r$P@#!tcdB@-M?)aBGr~J_xL8m_Ng$F$EO@CGV)S8ah?@iO|_l33lD$k#|k<Rae=lKJk=ehMeK3LQ7L7wNP*U$6t{Ttl3ZAW|CV|v{lfAgD+L-Wzz{yyM!f9rjR|7^0;9_DGL4>L~-j=<kkKAm}>>HW+DgT4P%KJ&X1oN-`YWO_X>^3TQpzRB@=-er0{?+S0s?0ipH36-4Rot~GPUe8N|r}68Q*ZnoUo|pPF=1@NH<Lgepn75c-&s)NI@Zr14GmkR8o<{{g*1m>n56>(A_xNB<)qedv?2uP^fBkXZ@iDzSK5ya!4aa%M-}LVImnm|P>pnW-y!G*O(novS8NU03@@JZlkMKoHD!<h~-g_KtV`=(zb&6A;?;z9r`3?$i)Ban>`}oc>z4f*F&az_a(VnGKo#Sxc;KSN4aePRR^Vw&VZ(e_rw>_qJ+j9e-tKOuD_84BbCs_Jr<&%Gz<ZX{tAOFI=N#6DZyB0s>_&V9=IrYyaJM%FAbbPL?jt>l3sE(h6@1}fc>vZ*e=-x>A{0ki)Tv%a$R6k{+^ScU9!zayiyw#xW&S*YxIz~N*=ixt7K3rtm#;CqQRkaSaubuL(-<jp@SNID4ev0FRv_F_FUilfTW_kPTKQKu7?C;I?_Ui#pzx?0eFK(ahZRZ1Cw=-LU^2s}9d&j}_?l=rts{GPI3!LLj{cUeFpPr+bS`S=}f4`vePc=)8=EH@0tM|+2_{{}W{TJ`;h~@*^YO3|4xDS=DUSV#;xOKs=R$kvH{vP;T<>z{@i*@_B^1ZsujX1C2^?Ab$PAGqd`t-~6x?ka!@mT|Nz2jzjciftMt$gL#s{Kc2?u_c2ELG3>$@s@+seZjYW>Yk8J$_349_Qhg%yE1$)7<^hysurn`n}w{uDmrd;(iYPioXzyxSzw1-cY{Jgoyh&T=ZY%*EM(UD<ADNy>4f?7`}6}+1_z@!0T}+j`u%3+uJYGyZw6m5obNmYJO;D#QpOT{;2Zq@ANqS{R1<-<KS=bxbopO>ba47+rDT%bnF1%QTXSS57yeZA(~ImyHP!dd*E}eRnM8)o71BC;Q7(c@6>;|r1BL;sqwGAZhthN{^ZkYef|W#;0RTJZR)0IKD~3Ax-LKB@4TGkwCBr`JEHkem5h5Le0Yd+oY1+|JEQuz$?7^5Dy4jCXXiM<GO6n#{5s`*%W63D-e5fbPjy~jiE?|R`9Pyd&hIOHs-f~*_s;QNFVpMm6+Vlfw`Weo_#56G{~P!j>NxuPn%=#>Jv%6WXw`gge_bC|UiUXV7@wlNJN|~(<8N)m_ez=X9Us%X<Fg^4{5Nq<JN^5<NQ>qJ<=U(7#FO|wbya`ge{^FsA4r&>`g;q%rk*-}v9I?<^Wi3`>b>^*1n%3G>b>wtv3=2epk-Fo{>k_&_-h5zqIs)KZuOsAY{Oq|<@nGK^HZbw^p1_xJh?@R@*BI%^VT=Lt{?7#@20%l9>crsS%fbdnCI=U>2-gDYj<;>?^5rDOc^#r^MMvw)OXFh_*r|@^S@^Mv}iv3=>>H^U&254zB<lJo%TiZzEXG9^X=FN$_H{RcIxw7b^Y&I9PjIJaeGw1tBrbY+{Ew9u6&F1sNS7l89uyeof@Az_;cCRamp837vaw+ujdJ-_Z1nZes{I+^L%?Y$$K2v-@;Qr_%yy`ha_+NO|RSOZ;9XBKFK>i4|vAMf9Dr|FSQ+S<-55znh(`c-zWb6@W<mE@4s+$M>KC$e@4x(vj3|5^g613+48B;eCYjQYW_AL{}DC*?H72DZ+d<F@MwHe+XdeCn_joyT8%#vzrfob)9d#5gC&(OI8Hq$Un`y#&Aab?!-tk<R_$DaKQczu|8P}mH1B?o7(RHawi=&L@%hKA_8cp@FPeAfrKV5MsP5;Ly_AoA|83_uJpWCvpZ~!F`02{K?^ErkD(}8ua`sj}>n`PaUzlFMFZ|j1DZj03vg3KanO;BN{Dtt<%Q@bCej46=-oA>TQC@ld{5QP&Jlr~6`F;(PyvH}aK7Q~Tez`x%+kVr#&*!`NF^!VE?J>P>kAKZ9<*mjGo%Zm2Hobm6`}g8g{EpYpXVdHFvvmUBuaP<q&u7!?=X1EkLgjb=m+ZZNOz+-5FXC4#@7_P!rzo%QAAdjm>v--T)9d>uxcH><lTNDVHuEdfyYs6h_&-mp_lury8(z=f{KxQzly~Q2hS&2kf7P3u_n><2F+VZAo}Yv};^Pmg`g*=(cs*aTCgA6U)%=$ElIh*~Qn~Myzjbwyx4)*>{S5~2)2}S@_Sf{fzri8+1a%yD{0*<iKUnq$<x~G#<{XFbWz)Og>DBSK{&l=nk#zvWyWh*N;?Jq$xZlf$cfXgL=5+r1EY@S!mN@Oy-+hMH-+jS0_|rEW?|xsKp6|-=eEgr+9k0KyP49lU28$^l+thhZy6Xdm*ZmEy$N$>o?TGO-ygQz|@qUiO_?TXgPx!@>$|oIE_YdELrq|zt)>!<N{p!Brd+h<w_nI{kKOn5`6TTl!ufHGtLrW>2+R|yK`@Y+aPi(H<U;2G|1RrRo#zC(KmZ_wC{NKqD*U|J`M}K*I<$sdB*U|L)I{LfgbN-d=y{}B~-dE4YDSx$4vbSI19{B7<k|WyxCO)ZfazuY0YO4H_K*anuSOwp@OT@g|-yWa(YQ#L&YSvQumnN=o#$T^n8s1$G9Eg8mlH>Jy;{#r=qYl%4g5%wFRKx4_!(iin%J<0_a?Y#Q<r45cGlabT^$)}Uq`bS1G;O5vxsEN3IIrRLdHwV8LzUO#V0t|c!DIL%$CrA?;Q_DLU8f~0pWJ>~L_1I5S9e$zaX(zd-&FPWIE2?Nr9JH;#vynL|8RW7IQY-uceRTcPiw<oey8(85!cc5wBI^~Z@D1k9Z%Ei@eFJKi#m=TPt)u1^k+Dse8+1M;}CodKjV7DI0W0`KfDn!p21AFm9IK*dBk-wz3x|GeC(j*5%<60-TS{SzIDR#h;cBydtYrT@S)>Be{Q97e4g8;*UxSLZhT4Q^>f?w`nl~-$6r-mzc)><-y{CV8Yy4)&<gK3TW#<=4z7r}-^SpptNQMJo3E+z@Bh5Q+fLKF@81geEB9A;+i7~YofYvtepwMQZid(6X0?7n`PI4AeXG~24X>ZW))4$6<pVtDP4B+1-^72L%kl0yv+4DF<Z4&t$9x)j-+qVR`B}t$Yt`+heBKL@_y4_-%5RHX?mh1VUaxOw9mV)4ulr?sw_knmwUyW7W_owr(xxjve0W5^tV{TkBO;$~x!+R${_x1>Tb(7!Pg$;>1A4vG@OnNOu8-foOpP=1Rnxok)yeof>Nt8nY<hS7_QMt2haWrbbl0Cv&wR%Ja7g*(XOw3?V|sT!lNCR0REjeW`g_Ol?)S3xesx}Vectfye5^YDw~@|q()nI9eOQ05b;4g#KBT|bwEsqVzy99OyGQvs?N>xxFT?BWW#z*k>9E2({-$@ozn;K{)N%CnHNC#RR<F~_A1LZP-`w?T!@J*)EAjo5cl)b-Uyeh6tu*{O<@NWk>D~47AHHJTK6ZXD`uooG`uonG`J(b8&#2!o-*=|h-*;A3d`FJY_onIf_h#_m-^!;XsP{rHwf<mwcRl<lez5XEz5Z-?AL|?8@A0oIA7=f;^j0U<x8sX_<oG3{)$f$`5Yy}SSd;Ouz8>-(-}HKY##)8nro3LCF}=IKw77=y@0C&Y^?J48^?Hc^Tl{3@!+L$j@b3EgeS99}-Su<ByX)s)`jsDiW|iahyf=Fz<^THF@qWGDYxtm^@0s=WI&fKhqB_2xb!pdgUO(&7{>u1wIS%X6rVr?OxZ&M(^`V25|941=_q?wE2d~$|-@<>FnBqOJ>D}Yc#DC6l7@r3`;}HBaLHUn+tLLp=uQq&`_2FQ(!OCA!-pBg0>D~47#`tR-U$37V-lx~M=gw9BR^m!;drYs}<KKcWO?`cQ!|UT)hw-1|X}{^+_4C;)l)s!=oma0v8{VBanqIFzFTmeYKFE5w>D_seS)cXr;9-2Wtg1fi^QL#_|Au$h=Z{`i{;N{&IPKKy)rNQf^UbUHm@<yn?^Dz3_o@Fc{OQul^L}ytDdqM1)L-zL@<qEizZd;{Hod!E-4_3n^7{E~di{L1I^jzw?>;{b?>?W`W<2Wny!}$V?J>Q(UcCpuq;HD1J*L;~@!!GMSI5!qF}>TKNm-O{bVuC}JfBVPKA-2|<8Q0$uGhm2pRU)#7vQHVub=0p5Ar;>O6F3&*@;!&`^WU|e4`ourQ?ow=NsC;sJy-(tX}x9m3QZFhS&F-^<FdOzpJv^IllhyhZx?<$9(uAzOnM@di~b$A-#Tn8GpXA<AZwr-0<%Fd0=<t&!wv8q5jYJ4IgAa;~#}Dq<lcHpBrA!XRKuW5bEpsmEnWTuYxW5DE~&?RT2F)yzXzXE&dc<uZJ66kEb;le?oaZKBjlar(i$j8?;#Cv`2q0n_hn}_s2i3y!8_6y@n6!b%O-_zsmdcI)LHR_4@gQY078Zudc6NuQt3-e<#kw7g0W>zY`7b{`aQl;H&L(d{}=kn_hn}4^38n_?^|>@p-`O@fnZ*OL=#E46ny0xEDYD`_<m@F})ritHTQJt0&d(POop9p6|i%ApCyi_4lCZtyk3dptTZTT=^j1cc$0hci|-=<+t8d{nFppYw?GaPuK6$J@^gEyYsYSsmkX$w#s`QP49m1_r{k{-d!g#ynCPY!<SXwz3!&xx?4kc@H}}wV%{5Ej34(x<UDg7{>*cc^WKIBc~1TjaU81^e$^il#|aO`ulY0LI9AyYl%J4otusD)UDWXI`gSY)Cgpv4o!Rg~y)HTtzf*auDC?qzPuJ_BPhM00$98KY#-UZDcgJB|q}TUD_~bq1r)_yBqMe4<?X*6|H&$M^)AYKX;avBX-?jN2@3@&>k6ZBgqsJUS=H5FI_w7miN#)(^@@QV=%PQ}TLwv-)ZDH0|zc&lkv;V{{S**NPudbed)q+U*M`!eZ)k5Fu|6l*Ag(_8R|1bYt3t8jsHaugOrzygIvK{P)n~*QTP2dh>Z&<R2hsUzr10F%nfF-AUIGOF~@N#k^yd2(Pm$&S)!Y(r@!i&i?crm<*d>`HfzenzXcW`{+=k3zgE{S%TV3)ae8Av9=iPRB(&Ms~2QVS=4UzMy4SB1-x72&dQDY61w3NAxF1($)VkhS1iv_W`|+-r6jjFa{aAP2*PsWX6nNk7+<tKjwUVR9dQ82*4f0Dk}<BKN|F;B}l++LuDEgV#|fh2yNY%U1Xh+lO)Qz#p)^9=8xa%=Q%ewvb#8C$euSJeTd~ab4g<wwrU!x{%Mq71>u0uFZA@Turzl+jY5SHOUHaGp=7<@+tULu30m(7Ce}JL*VDwev>gBLJo%4v2Ou9hwVeS)$lsD<##a7Qon`wVEx+>*1s=d{Tmb>PZ91z5q_B>98VE`h9caKBK#6XxHm<3EJb(*ML3z<2+MsW_up&eK3H-UEI9#|90*Icg(a)Pl4W7ZQm|whSh5N%*#?#z080j8$rLz+b_?f^v8=3iscV-P?2=%Y>SSHGE_H<S*(Hlzu35^--+#ezu3L(w2p=cU!^hzd$&cX=;bY`E_!xYFyar238-xeh`Mh1~&@O3TRk99ThdNd1m-KT1ITc<2zfW$0--maT@4~y`_sEU#d+>bDDeap=&WGnyN4TF|p0!I4if}WsA}m?f!$sLH3uh-SI6M4{rSf-6u@vF&$^YQ*;rnEf7{&MDY%waIf+fp%IG*h?a8t4`EZN<|BiQZ^k0lqvW8oCWWE|tv4<1Rbf=9wh<XSihUQMRJDI9+_WB3?j`zq&aNH&9;QKun&EJoiS<M02pRAz^z2;U)P-0x6?)5-7Qboe%TAHEI$LCQJ*AdA5=hOaQT#b{pxvMJn@It}R8tBjxIP<R}?ikuFwg4dF7!)xIbavGchkL8@wz9HmTcr0~<=f~Q=AG=H-H^G}@)xL@FyKE1z%bWN&*(V%tmu~Fu#y;UH?5hQLV>_>1GUGF|Px!vwrVBA@zhq|Weq-~o7`6Wxb%Z~NQTslDkFk9e_ci<h+n?j^!AIGCI99nwV-<f+oyxJw)r?jAFxy>m?cmC6_qWSr{ABjEV@x-(e-r!q)Av7PRR3EtK2MQV;40L4iu3<L+y7*I&XO`FXDPyA@)#V3_mUsLd*K7*QTPCShWs3s`~#N$wV?lhFplMEXJxoDb;{GPmfRnbufuP`o5_{%X82ul4g4;=i44J;;K`g*+Bb@v3{R$xaA&(Tw##!A;fACSmMrYyJZu++GmwABD9!-ij!}6Rz71a^|AMc<x5(VFif_RW#j1Q9mMr99Kih@i2IR}IWG4>~V!IPOf}9PHfEO?(BN?a8a00myPJri-%i%fj+vEax0mpxvG0e-@#&f<}WJ9<ib!ySaN9lWB{$8E~g&FtzJQsw&A#d|c_=aon33(0v1pb=51%D0SBjud;$VXur!*-1AqqMIk*#K@potpG3p7E0$0FQ(hk`v*D@N#lKyc}LYPJkD{BRHqDuRl2g9zh*pd3WsQeIWTBEb}heHyz&1w!E7b;1{q@Sl(p`>`!2yu)MSDvcE3-gyr3xpZ)pSC;TUKR@r}@d9Cny-s^XmyIyDeV_Z6Xp6zqE+wjM1U&H+YpJQ9*tK#GxE_{tT^3Im|YcVn(Eb~d(_X=ExZReeepU=Km7}p_;?R)H#ZTTHE;<xZNtbaR=Jio6-p5LHwV~VhkBAkaJ{5Q`Z;k!I@g#Y3>Bb=Ke{5VC}PZ55ZB0Pwk4a;*>p1&2ym9XUNuw+YE@+nwS-eDEUv#?|smfQ<V9)J(<{t=e^1C}h$@g-ZplB3{Jv|Cu_q3vVTTy!<8=dQwfek-i!z{1Z`gey{ni&BIwitz8u`Gx;uo-bU4BK#CZIG!Thmm)lZTnNi|jC}u8BR9d4Q(?&$V9DyRWL8*Gz8kBN$Km6A9}0iSH=*z`z6FIZ@I5FjSrwLi9+sQ}Podq;dF^Xp*`<<Q+S;XuU7jQ>!Ih{ZoW(BxNgHF7lfOUDalVXEEJgSTc>+EH?<YTm_rr(D<M3hl9Qg$-`5)ZfK5rYlRHR+fzH+p)B3zL=<>;66b2>Q=o(^v$-+?#6TgY|r7I*`>8r}d;<DAmIvE(#(8g+yNc6r7wFHwZ+k|kitq8`r0c2PJJ`Fo7wOz?LxD(}GG!QYa<!Qa9+$wy)p--I*9sw@sm7V&Tswu``Z$S$ztiynTB?HA!;<V<)NoWz(6XPg4?Kynd05S~RYgJ;1@$Rs$4<1b+h3o^DHIbRL3E?k#7HRxjj`d*N~|2alwCirKrLpmwro=y?|l>8R{6uv~>gfGEAk#f$T$O5p8VF$*x0PU+z)`9C#r#k)W$oNV2frrD3$RNB3UPjJ?m%&NocsL0j#yO>Zy~$zlFzN^|wfnHgE;GqAcxQ~-Hw)gw_Het*!OvlzaA&&=WdA_+2{*Az9Q)(gCtSiVdDx$aeZqg+kF~3o+Ao=hx}REV-z`h=RkqLIF2SF&{R!?n_zc_M;{Jj^VLNw>a>Zj5e@mUlHrI|(zBc=WUyD)uUWRM4J<Kk%@w3_YGUGaou}x#&F#4XE{y)d~)FR{HIO^2m{14N<%>4aVjFXJXR}|sX<frgy_$YY>J_?^AKY>rdUy|R#lF|lY>0c-M|1j;VLDq(AQ>O;~dXD=;@=bUSyp!Aj?}Yb|Tj4!$8kq{G!LvE1v~Myw8=g%a;a+xWXO{p)xCQwnELqaSh1o6%=OSa_T<}kp%HJ%-QiSi4F)@no!atIQU@5|n;L5?0Pk6Wu+fTsF$)2!e7Y~nSy9+#?TnvwgLySp~aq0z+Ay>j<;3edGcnQ3Q48b9ezlJd^!Ps`@d`-v}a0}`*p^wGsdkOwto&zNr_rG~A2;U-q;+b%ZYjBCY3txi2BY%Xyga0DsoPUwUVHv}h8QbEtuQAyiZcd%X^s6)DCpjDr!Yj#H@Je_+xfEUxhsc?52p-QlrG3N5@$h)+2+O-;3-1HT4e&<ZD?xY*+wyLjj-SrHAn&ps?C-%o;Y#eQ0ry~A-rZU8S=m>E_qWVhWxr%r>dL!Y=Bz)HU&1n9m3^PWC)hrYy99s8_7}LH;Nxt|yE_Z-bjdHMQ<3+&yt^w>rvUHP?)dKPtIj)h8vCcQuLEPcf&ClUCoJ<&nZK4I-+?8^!IEuZ$tPh+3zn35e<|_^EV&<+JPb>ogC+liCChP4$u_X$Sa>Y$7M6M3)3ItUw*=O6KVdyT6xMS{;b$nqB`CtVD8e##mLe?k<vXy<k$;09p$HeJ2sfb!ccBQsM$UxgJs|Ion&bvp@=aLsIasn5ESVXWl=p5;@-%#!_p9(x-l@W;c$W%)$@^4TvIZ>K36`7;OQyo|9Bmt;o~3JG{p=Oi&u3x%3>R)k5q^>)T$mypOA-E!cb0GrMYs?}xEw{e4Mn&oMR+v17|w2AgMaO;W@l@=^s-A?vKm~CI>OoP@{f#hjB@h#ACnhj6iX34M4o~V!TZRM;C=8x@+5o^K23fFOa24*w9nhhE>&rlw68SntO{49PHFlj{hUgUfv3W$<SIB7-b${8x5Dem6nH&6g>y>#Mw3(EDbx{u)h^BL@&ZM;K3Ni$e9Xf+*?tU;C4Y@k91GuwQTaW51HMZB0$+u%lR07)Ux#C2RXzbr7V~gZwu`~_$X8&==RG`_?dRbk<Xi9%IGHgS$~e6WCz6ZdM0f_d0-gacC6nP~j=z*K%+J_9%lYES`fz>f#L>rm^gTa+|6`2GSolY-!xd7-{R&0+Gx93@8GM<%4qt|UAmyAtkojO4!}g4AKH68CtOwVlPHp=2EaNBH4;~6HCMUs*;T7aucm<qHz5yr0LpZ0juP-?S9zq@ABla_Gja}Zg6o=V9h+7LEVS58^5qyyC$#$8KpU*zw;dV)2e**i2Uu0ibIDze!cBzA}!#?54>}vqmVY@u823(o#`gW;=uf#s#7Iukae;oUSUtnJVj$?ZeZW#Om+mq}v4?mB6!l~>_g6FXv#;t)<*_Qr2OaI?seEO3KZ~}GubN=?U?^*u7I#~y<4nIj&hM$B>ljY&ka5=IPTn?^A#=&v4p&I?0NdMc@zP{ujco22^(l6=f268350X|6Xfe*q*$o=pUI85$_!*D9+l=g+lR5+D7!n5r%#xBz+!lTGuuw-`+zruERxD(kL?gTd`o5GFZhGZ+aA>4@U3^#&1l09L`ZXSM}?QZZ$auzH()x%5Jo(eA|H^WQeZH&n>#%VVEHn|;s8{R_hg15js$!+j9j=z&J?8?|q=6u7+QSd1045yC)`rehlZ%KB7Tfz;<#&83;2H6m<0oNxR!S&%5WJkCoZD_$5PGW2Wv~L(W5*|sNVf1S<<0rWYUIuR`*TUQ3UF5s)E_fTc2HplQ<($&KByuUdlsdxl?%2xvKyp2t%6nxJyp?TvH%-M)W#1&;Wxd$ni+#e?*cS))Vq4zb+40%g7svZs=B%>+BJ*0|Q@q!&Fn7Jk_D8tS;8Sd$#9f9zV*4xH5AaF0<=vf)ce><P)TzpQUEbYQsgsX)YfpSn_SNQ{I)(jH*w>yhUC;jY>=W)|pQE*1x>1CmAuGU=r9E7b?b2{gG83E=zGtcY)lw`)_y;m$jN%{QpUDES6yY4W@~~tn54U8y6#O*V8<y<q;ZbaNg(r}U;0f?@#$;lQ8mB(+>*NafbvT(^2Pebtkjvra9A7xET{76EzFj)nWq@6(koDpE)DeEvE)U5)V<{(p|Fxy^iltbJ@JaG>_$2%hc^3W%K0$s4pMWotmtje1gK&R4JJ_Wj?UMFYChNiVs8gAKNk8Y2li+#q4sr{;1Kve$gLlE($<6R~crNFZ_Ps&Qh38U7cp1lfi`)+HVBZXQ7u$)nbq2Wueu=&%lJnq3T)&sd0kDs2*NChS|I0P=aXs@=SFV@ryUDe?!uDC*H}L0de}=mOpJn?p?jQIww&i+>dz@=`nL2*1-{a(?u#Bhddl9b3_F%^MMY2D<oqcb?bJ;FU|DIu7x-kyjaE(YGT#EDOz?EjqBy+-2gm04f7?YbkgT5hufWLunkUzsW;D5**j8P8SAl#MyJ&h~HIF!Qq$rs^n^m8Ja2v3ApkTc*F@H%oCybfMYz6CFbCveWLjB{7qVDc?keh2dVsYGspB`3j>9bw5Tuw({UQl2}N$dm9%o-e{5@k|ju!Lvm8BF__H$;z-~2UzkA_zl`EEYHzaG3r_R4y>QO!ut6vte@e+ttrA4D8dCP!kH+-zw*u!&PWk1KoKra5pGEl?oAOMMJ|G69y;1mbJ3l!p1TU``K_>?0}GF#2=}50zd{jiO%ZNN5pG2h?o1KxNfCaXB0P&CyoB5g%Xf@?|MVmGz>+Ir$v0rh{;=e;uw->u@<~{-G%Q&TmaGO#wudGA!jcnV$q*c(-NLdC)GSu51ucd3+L5qcUlP`9P{PeA!X+ufIVr-j_9jJG*4w^^WsU6@I0r@e35sx2itsBG;lbovu&g7>`ePY#6)ZUhmTV16mW3r{4Yv&WF)VoqmfQzR9)u-N!;=5NlBGGmWGh&5G(4Ji3zx93K{2}&Aq&Dq;C$qxa6ULU`3RgF&Ov5_bHG{1hv6)6Mlu%82tPzx@I!D0G6v27XQutqpU23O@MCaMvN&86E<hHB3&45Eyl@^kCz%V*31=m<!&%`>WM()sZ5H;~<q6tb0xn5D4wr<BlZD{oaA7h(To{%%#<z-z&HK>*>;EeL|NbNY`KuN2e;jZAW#s?t+549R?PIzBBk1^68KqzL#fx?RM~UU+f30WzA8NQ=>H'

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
