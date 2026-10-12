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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4f9391e9db8b453ea08c7c0109077d17/part_004.stl', 'relative_path': '4f9391e9db8b453ea08c7c0109077d17/part_004.stl', 'source_sha256': 'a6bcc553a8cb076144c6fb41e178fa282be8b4717cf9f5d50d2fafa69d0a3752', 'input_faces': 1248, 'input_vertices': 706, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34399449825286865, -0.49999988079071045, -0.2928825616836548], [0.018237441778182983, 0.4999997913837433, 0.3015563488006592]]}
GEOMETRY_BASE85 = 'c$}rZ2b2^=8@AmuiUCnTksvBVkgP;e2{IrkIV@Sy5|*5kl82m8$(beREJ@TEGAJUFLBf~-^%Y+gF!AcQPxV#3UB&+A{O9{P=Q;P)HxJd-mAa>=d#G3QzWcK{?w{PwkV>;hY_9A$5*eH<&VZyo{W`Zx>ia^EUIPP8CgsZ?t<&o?s$H*Hz!~5SF3>)yZ@WGP%7zM*@9=VgqM-sEdiLqpr%jL6J^Qpz694r!-TEe__<cLI>6MhSUGSyiWr~JM6)GAU8v4KdlRl*ik-+_DqoV)*dsQ@?b==8l8h+yKCr?$B?cD+8hld|geq`3iZocI^+iIzNCs+N`YWwZ`w}~eI^2z7XH2m<)z9&@qH(qf42IIGghSqgc`L-V`T~+0W3$0W8ceZp{>z2FjSTqek@$!++BtQA`NY~GCWTmQ4%Q`Cm9)DIBGk@Z5b1SBmuYEgzQ0~RD9UF4v(`XugeEa=o{?l34tM>YA#ldJ={sa3C`ST;0yY5i_f(!eiY58Yv?>EY?-7~8E$4~E#rsdcC?>>KitbKTYTKS%D=l7|l>KA#c?Yd|hzVq+NP5%6F`BR5g{>@X%qG|ZylT}vx^Fzm0ss45{MKh=6hchRSP~{zO{+aSuzkXV6uNmIo@CVIL(@)%x=S*6Dyk2X=PuzItn7{n+>J>AiY51{^OC}rn?Dw90d^=y)$IjQjov-U@=WAc*hkrR?)Kedq=UeTgeY<_MZ?{kUd{3kN#3RWwqG|Y%g^7!eeD-@!zOIjzuj^yyd-b&Pbv^BTum0pmT7Lei(T~NRSQSmf4=?Mz-pJSeXy@yGxAMJywDP@vxAMJywDP@vCqK5Ukx|b`n@7}oX8W<zo!1%px}EKOeOy+)*UnbHcU)G!*UnbHcU<Jhvkdt}m2*4ed6oZIufBdi`BqQEk7cZ2=9j5G&F_2p_=%sDH1jh)IwI=xy?p#|r+<zb{hqn+=Cu5HjXc{b`hDH+c0RtH@AbQtuYEh;>vt<(`#L|C>9V`u%Nx(B<66JAui+={JMZ@+tydWN;cTbgHGJ~5pV)bk(GIcOO*ci;@WZ`YY&G)rxU%zgyIJ|(xU%xScC+%mab@Lu?WXf*EHIAOY5(EisNd&!wI6Cc<fwoA#GW0nsG`r;<460kYMsse*Cwm=NBdqreq_x*M~wNh_paMtOa3}y)U)B-`G&9Si61)ry_uhF=6g}Uuk-QamrfY_4d)m!MUA8JM-AUOcA<~jo?YvR|F{yHW?Np-=j-FrzEh>Dd0azg%oa^<@{;L4cX6U>hcYG2@?T89$nSgQ<0sB4;QD=TT~zx!U8kQa@AdR%J4|^~`QeTC8TsL2!zZZxFaCGfC@1IO_Nx4GKPx|R%dv}YxgAtF+7HbQeVLXY@7O#|Ke>2M!w+S;dDy6DLXM?|ulox>`OI}AKQi>!@yc)fwOLNr9BtM1!n1}Sn|61u;Zwf$W5tde$Loygt;*NFK3?0`$7}ogc(tGW*ikpXd{ws{{_Wk*@O3%Q-)*hxv-yZwAItaZWBJ~G@trp7+<exh(A*W<((>ac8@kug+Gkz5Ctt7UR=!@B?0j!MxAOJ)xAVRAT<1?-W3*fB$ewZP@4GBFd}q<#W@>xiOk+I9zTPxl{r$m-<~VO~cBI<xuS3o8^JpQJA3EC4XrIK<Yqmzy@M8m;Z8!4ub)B8B*MBSDyRNhHz4hP9_pa-#d~f|H-%03e&X=1Xs`Gnt#?EGb!NqFb4&Ui$jJNPF8>abvJ>G0zk6YW<<52st%&pAz;X*8;wzsu3_8Y(Zf#K`@+P*Gd`=MZC<G7sV_0{<$@r!EaILY_-drDuaY_2oO>(zXW|L0XBKk<>p!(=-=y`YgF{;A9ubsUrOndOA17FYG_cjJ(MyoINiRiB%~EiWlQG(N{wl|QV7`#Ed;#Y6sbVsoE-NBw=z3r0D~Z?2f4^2(n(Wc2S}!{(^JKYP+BC$eBtKiQ5gJ8{V0&XG?)ch~3mr>@U=C)BmVD!;GKJK7J=IAZKKR_KMvY92jv*epN&Np-%{zIVQ`d_5jwf1Eaa?|eaiDA$KZ`LWqKM=347+bAd8?YKIhYClwN?-hSLd-*GS8}09$+GUil%dveY{!dMRzBezdd~f{g`aHP#kTDMTUYVu(YtMS4{hh!=OQSwtx4-s7=aw4fL~>mkFWZq{=NSDGAN#Gk4)J`(gXf<aY94QeyAxIWyfxG)Cmcyw9QFHp{Np?G-!j`L>vNsdcDL5%c+NH0U55)da*u1s0Ha^DujfT<XotShH2g^X;dlJ`iAf(C{TM#h(5&aw-_^Pozg*vKH@$wIn7c%kx3Ii9PRdm86-~p}*N58o#*dY+eVw0}znrmOr|ZT!sy&b8bL)S!guCD8vby7QSx&QGUR$C*cO*B-ZsbRHeKuVABeR<2<oT$*+HaXB%=xmf>D#Ive`he(6X*An3)K8Nn%?!F$?cYNC3k<npV+^$>G!|S94DdQ)pdAc_kRx><%~Et%<p^UXn)TC%=`i8JNSJsA3r(i?}PsO#~!Ra&7EJapL+f(<bGbjPd$H`zPE0~iyD6F`OD2uzIOYdF>c!)Z5d6&53hZ4f<NCIpH{y1b$(>tuLu3@87k4i{hV^;mxD&XPdq$Yl|SvKTYr6BwD-Yz>ffFF$;fve%1}_v`-wl8?Gv2)Zq(;{?PK{~`&ho$KKP+xSB?5aj$EIr@)lh(`ZrwcoLaZFulv{YZ=E;CL$w1{{k}II@FR`)AN0?6=kP;nU5%`dy7hUxim}dUKe^LQW8Fw@y305&r`{{3uj_-K_|*<$zv1%d$I5mj!*;X%^Q~9c|M8WZjq)SE9vp1=l&}5pkDJVLwsvf;%Ac~ytmo-o-7ETiT~GY@>J?`Bp{C>fzHU$LCx4f0ma}<Iy{OOk+F$#b78~Qrxo@3&y;o|kIZm=%ju^fk5BN@Cws~B&cD6BmT_5ciooVj(?@aD>;C++LejoH_<BDnckv?yY^!wg;u=2I9^TQ?knf-X}<xz&O+ZjJ}t(SRR$A7A4`1-i;BkQ`D?acU$Kh?<?53zrXPg1(9gPC9Ro3~Z@H<HZ$-EyY48n^K_=D2z=p`)tDhSp|%S}b+fF?_Fl?Z5D*dAviiwTb$CZ@>8Q6V1$W(q$i_>a(+{>Hknkjoa9Rubbs8Sgp<%p;}dq_Ka=VJKFH6kM?6FtC;1lt=mcU*V0O6zZCzXwBhS^z>h_Xn(I}w0&3jGCl@x$|M96LrSIf&eXi@m6WXr!`}(@h^FMgTSpSoMzP`fnS!c8#DU{P4&-!!Rm)+ETlK7nL#`)2CHn)4fu3UDb{P5IQ7An1*&74Oo6Bqb>?>>X&d*_82?F`>*Px2$fvzh0G<HgkZH2hFj<G5m_?x=M;^j;S8JT;-Sx^4`&dfZ$$I`yCE_r3Guu$+?(U-uXJ@hX|k@sn6*jN$9?gC8l9$t>rczHYzw%;?r%-v?N=@BL_6e!`Y*Y59qh6L+LlPWY?dI}KmoH?YgszFoe)|6rG|?=xHFd-oZv@;%=w-@9L7mG9k`w#xU$r&Ye^TjhJ#=T`aNeOjyh<jkeabyDZ+^}qPV{L!@hhqsO~%HjG=f9|k-{kg+yPd*pK8eJbAO~Vi8Uop+d*Pr+M<sTVM%b)b|bff-!j<C!3K3`bn>+4Co{@S<e@15_g_VIkHeM0~KYg{iy8b4;Pdv~*|&mEx(kDBYii5*WGzFt@HV|g=}=aEh~+eLl8cb=->vy0*D^8)$KFAtmRSmy@nb6@1#L+172ygusla&quNV_kCo?5VC}W6K{f%ZV;~&+mKdq2+t`Z!O<z2Yly^2aI(%wrimJ{1W;;ow07mtF@V~wwvB(&X*HU&r{_bag1`DbmNl^UmvgbfBWZvIxhV^;G*C%zwdnyh#$KB+X17UA1|fWy-?^^!*|Y9SLeI<)k_Eb#~Z71YP8|&brnBc_o7)2p9kYFUNFjWhD2X7d_8{f!-LM7<pgG_^Lz3q2TgxPg1X)aZ#iK4MRuy|jl>2A%<|VqC-{9YU;C#&HuK9bO^o_{FCRa7$%hAw@m#Ntx_*n#-DS4(@<IbuJ+JIE{koa@sP^x;!z`!S!47JipWSBWpIhqQS6Q&ZXwUEyEk+r>KA+;p>aI20KYN)3!`H`)A0IYN`S$g;?d$7j?c3Mewy*P@#uE<s=VQ42!D;Sz8D}2X-;azie0^N_;W}f?<7zyyt>NqA!jJSGZtOSSbC+6&!+#Am@*~k{>T{F!z4pfsU3l9pKmT{NqdwmoC-}*?dYJVrRZfjt&)4PP$7b~~#zW-5HT8Kj^ksLmoO;cB7{2#;*7cM7cQ(h>nRe>?l;q@&%J)9!rYoeb(-I4HFw3v;L4U*7<>N=rv@*wuK9AtrpT{Fbnj8CdVzb@P*HfyR{hO3mttZ;|uG6&tO(nBFtH;&w`(FFw#}g{L_0;EuPm8<vRempJjEBhgjpqA(@BX&sd-u1`H8p(i^CS7ry5eU0FU+CNzllE=GwKuHK2zOS2`?*Z<~OWXM)l+MB5r;3c_DjVbse5Kzo5Hc>;9GP>-$mKx9?xszRnL1%4@Vwa{BJ-e5!r#e%+<OLVvz)H#^@upK@OI%AwtKe)9Jrb3V2n=iV2^_vWMav*fbo(aW9uzBeB5;~8=q?HPWhta~2c{e-#S{+HeL7T?=1erRlFvmG*KRp<T0HIJC<8_$`9TRvp=@7NmZ{2M9!fa&kAsqTx0uLO;9V!hsbOSRkfKldB?CBAp>Yc>By`QCMPXy+28mA_WLeLvjx_5E$_+xNq5-^*Wq%-C=2)4u9{czpZO{r>qL+px?1zM!e=-}8L|{ypCpSibjt0lxixLF~z>vEOi?A?mu(xxRA0G2b5_rOwyk^h@>|<6+x_D-2(kgCAL+Y?R~F_%%tkBkznc%5e&0SZw%u-NSd*4R+g&bs&7Fu=-vs@lbEKeEr-=zYeSXzW3Y+et1w1qn!BJ3hH_|v?<A`XE?swy?<r-&NKPu_<iqs*z&#e0)Du@>wEVN9w}h>_V;vNzV$s_ylq>vK0AI<*C9?)6SKcwFYJCFhoAbqis^gnbKc^HpZdItn;-kBk=b8&Pr2W>E=e%jKl%47OQJqsx4-toS8AK}|2*#iwV!o0jed{JkE(H-yzC8QzwrX2C#mfxs=DQ~o<v4YQ{OMg{(Q}xN3&m2^CFh7vN12b@0}klW0Vta`nUQ%H~G$=`;2mO-al69&D)0W{IN5n{@u*0`~2f7vZlRzomTylnZF}J9dGjHGe*91>yII7zn71=zW%;!(qrm5)zI<SKBL_lJ~Q3#d*jgZy>W=2*vs|3^9z1#(hj41eZ8lB?>Pj^_sS`B!0^526UdMB*=`(Ha;2};=etnxb^HAN8>zL(y$`T!jq6*_pV+>B-ox{)=TB_k&bOaGv3)z=e*VPvz5I8Qt>Zec?$0|PP2XpX+e`&#sQjlV7=G;c@7(86vkfxFN%-<kb$#pH>1U3gs~Hni`MLWV?c+UPWcl9nMcTKYcd~pt|DNZaEZ@$*=Xoc~*ZJWu8X4m-k}z<B-}lxr%lFnR{KUSE%=TG0Vu0c6=Wuj63H8kRwezDUQJ?S4FU$AFzvX-L4&V9i4P!hwrCX`{)t;}{2mHh$<<0Sv?g4fGHnP5qS<c{t>U*)+=fzF`qyBRZUze}_zg{rgx$zX$KHB%%+48-1vwW}p@gti<=6Iey$G!i2>M6t5&*??VWigL8<6O6#>c8(b=F5@gu3z&%%J-hznc8l--}j!|!A~rFeXoDKIX8-`^Oy7L1=FvyW`e564__GNCw|#uq2KqeE42S-L$jRsuT53^Us2oeW0!;K`Y`@M>AgmO{imV&oZ|VqzwpEHyheVg`z7~tf%eJQe&l>Evp!$mQSBCfWqZtjT#>@n7yEthJ{W$y$WkLe{PJ$KZfoEB9tS`6(}<YSkN>Vy&zpI^KEG=}d&Kpv=gDnfKfmqy*7M}HZ|B?3liR+XZ$D3N`#L|8XP|k!57$=DnRvcFUi@(HN=CkOv)Wq~{l4yZ{8)~V*$zDaZ~NZ!|Jt|SN3eZ6-+mv#_U(N8eFWS0-e2f^F6tjYPS4k-`+e{EF8tWH`;7eXm>1RahuZhX8-9FdRkQr5qg1<T-zy(KHtoHS{O#twpJMsm`z+eG-<Pp`JO7^dWh~#$zvq1!%h&m#>We-!>dE^-wy)n0@_g%kCEK_2?e~>z-_Ez+SF(NY{icMLd;Im(?`PS*_kNc4t@p)j-_Ez+7qfjk-+o`r_H}+N_xulxdh#Be=Uea7Y2SXIPW$(~Z@8+iQNH(npXGb+18U!X-_Y{y{CnOvw0t}Np7#wcU*|g=$Lvn4eLUZ4AMM-iqkX%5!pWVMi*LWrdymiixt?#m&wGz==Uead+P;3D*YmCSdGGOgpI7_#`@Hw~ywB^EW4+INkI(zL+PB~5y~nrnt@n9tU%$_*efxc0+t=^&YTtgJ*Y>^ld0z;*-^*F=ciX;xzuTFxa;d-Ho%5Gff7yO$*5AjB{7kpp>pwdm|DOD;-Q4T5E_2O%d}sM~Gr!B8wQBx^-RFC3Kk`riLq`6YjH=(0H}~2XP0Rm&@_v7Q<d4Rx-@}vJ?Tx14CmtNW&z~Qw@Z-L;^0j|Y{(ILBs&=R|eQh)i-zj<jCVzgo;zV~m6zsb+nuZ_G@a;-}erQ5ZcRYmGv`Nz+y>*b%qV1RX`#n6jtQrsZ_$M2?;~{@;_j!El_XKQT|DJ%;^x`<>+rL*}`TF+?oKT4|M)}Eq9gn8rN4h=Y=Kt|U#9vOl>zi)*mLEwd=jJEWSDzc~-&?SK@Anq|7@>UqyAAP@?(a4@wdNVV{+$Qs?D}c`a$=8+PSXz;eEd|!dd9C^EXx;I<djRnlz7<5;&f=^`>6}{7mnj;+CO#Cx%B_9pSmbfvh>UUZ@+bszHdq$2BgF|LU<)Q6J81LMYqCx;oIm9_%_@v;A-!H%M!x7(Sz`A_<QsY{5>29x|%uYvS@C&Mv7lOC8jv8&U0Lr5Uz_hhwH+xpq1cP;OEd1@N;l3v<RFF&W9F<^T98pVfbaZ4*Dis2cC@1g(t&r1YE5aa9Kh)YtYq)gDy)5H$<z!4dE_mTeu56Ea<kIv}1bOGh5JQ3E}E!Be*);4($rJgZrYx;lA)dbPPNY?t>14hfz1-*Hh|KH6@-5y82MiWeMR1=o@eYxHH-Y?hFq_d&5KF(dgUoXm|+P3myV@qCQf;IgYE79G4}8o1wMgW^hIHCAcD749yD{gA1e2!iC`%&^+)9@T+JU_*J+mS_^Ip&qgQ0v*9WMS6>UbEFt`0(A6wKmnDQ>M-$-J;Y73(+=(_6u9H$u?Ucw7bTvcJWeMRXXic~Y+#OAVyTc>U{_qHREIJ4t3rEm?a0Ko~eWZR199Q3QT$T`SiPnc(!mpv_;Md?%XaTqsToet#Md6ZYez+uD87&J}hFhTZ;1=+FbSgX_t`%^#X24|$;YWh5W)He7AzTA(4A+3$qut<cw4rbf=14Z?vdr6Tgm5FY0o(}gigt#(!o$&_@NjqxIvO4W4?~B*!{9E|rv~%32Ir7T#1!VJXkEBA{1W;K{1TiOeGbkGKa1vqpM~?F`QSWo8T4hi3|tGX1J{BlqLbl?u*^}>H<-7tasH4w`UdBaEJRl3sAxkt0q%r$fxFO#otPulnYYzBhh!kqGe<?M!!_X~v>luT_ecA}{oz6AKzI<`5A6f@gWFS|+FTRVW**NYgqx!+;pT89^fkB=Tmmfxmw=0)Md2cFakL~{91f$E;V}Fr+5&zPo{P?h=fZOSpU*t5M%3b(pceD^VM4eXS_7^Iw?*5-?P){dZ7Jm(Nr@OCydV7p-Vc9_9)>@LSEF0t)$km25j+PTK?sjYiIM1BbP+rkUW0Cd*T7NqFdT&spr618;JxS(crUyT-3G6N=c7yD`S56TJUkligm#2G!THb-oDY5!eGq;W{-5LOEyraE;p^xX_&WSG`X&4|{2h83{to^d{T2Qjek9=P{Q;LHg!2%>&!j|dG(CDhoF4v*GNi1(2;pzh%ka1GSLm1USMW9T3VaQ|i{66o!Wn2YX}b)Ba9%V7=Y>0<9pMh}D0DnL3Z929f#<<%(QUA33|<Q-6T-{U{qS;lA^I`A5T1dqhG)Q&&^hoVcn~@Q9t2k+ge#z9;0o}ofz&zqDj{4kB`TwDp(Ek9;KArzcrZL1T>}q?$D&bqEIa`{08fC&p?l$Ra0FckN8n-Te0UiAHaZ%98*Ybog4@9_p!whz;KJymaA7z<D)Tl!+rqif>#&6I)9BZ*gz&TIcd&%;bLii&gm3{==4}B&_<1xB{5)Kl$U}dMJ_A>TUk#+rc|9I-GhQm8h0xq^Avgz`9?k)0LS<dZ#J2DQ=(n(ha1i|pmJogzy#`ANKaSpoC4_ULvM%H#go~ni;i7O7+5t|2hoYn4q3{%R9y|q}g|3A~lVNGYaKN3Tq5}h|b5?i~Ix&zs$AxF0(*vn%g789gK_GPv5nhfi3#6_&%czIw;y~&ewV1kvsb4{~5L^(>j^==~!x_;`a7H*C`T(2`4xm9e06&C23_k>CMjwYW!%v|(;iuptXi>Nb+#XGW+rvZ9q3{rRGCBpG49`So!Lw*X;r}>pI~Igrp<O>>e?#!)?>|Jd!xF;F(TuQ!@Mtt0EFnAy4Zsq@6VQiX3E|afW>`Y_0QwXxA^Zng1eOr)iPs)(&v6RhA9UMmCZ0NObTT}dy#LTf(pCe}&G0~YBKj>n5uT3z3r~j^pw9+fUH~scUw|cq7o+)L3E`RO{qPSd$NpPNe1IN=KY*8_YvHBvNOT%J5`G&U1HTQAN2kN%;Z^8*con=KJp%8C@1TFeci`>;SGxvWmJr^9ZiV;2KcI2=2RImX^>0{0I8TbMPtlDjaT)yvz6}3~{saFBKOS`TnV`!O!nx3*a4z@>G!LAIIy}L)@O?oygny*Iarj60Lv$<rA>0G)3ip72r~RZIe<y@LMvuTB!z<AB@CtY=IvpMh4@Aen1L0BVG<X!e3|$K^gZH2Z;XUw==x^|k@XG-=gv+8oz-5^OFQsVdfU9w~#g7xho6ry7P4EnKDLe!2kB)@<!+p`W;lA(ybUZu&o{6r4XTn?2{qR=!26_j+0n2w9cbF@^3E_k29{3=92mJxQ1IzatKQKQs6T-#OJaBQiBw7?M2^T}3fs4VJP?<BC*cSec`ScC^8~g#f5&i%!O>CrJMc2bG!DSg6qMOk5@Fw^>^fLS%>;zr?6P6GTp)$`ygz)odF8FykFZu-h1an)sOiDTBQ(^-;4c-8MjUIx(hX042gZ~FV9dz|8SVFi6`d?T=I5&C&mJpWjwxm8%zsJz;9hV=2FFCI6hA+XNqD$aU;g8S}@JH}=^euQhybm1*?}Lw{E8*ktRdg?W6@DV%>TOs;xHBr>3w9=iXQR8}+3->Hd-y1P5tTN(h~B`LHY`UUiY|qx!H3W<;6v~^^cVOX{1y5;{1yCP^e_0o@D212_y&BD`bho$aa?^2{)c}49F>0koDklEehP1aH=rNE8{l>5c6c4U5#0xGgx^Px!|%hV(W~%j_`ZOv(y#Xs!d=kLa2I$LIvZXEpGA+tXW?7uMff6Zc#AeHNgs+{fS1Bwp!tI?e*yo3mWL&Te@Cmr62gC>^<fF&KhV0cgzzouBlY{laaH>D6GC_h`Z+uV?u2fEJHbuR4R8~<5xNd;1h+vq!foI#==*RNID(#rBk*Ua^y_DA3-_b1yTJY6OXw>25?naw>RDJq_*L{4e2X>|-jTAeohi{B?E!a(+oJ8@ws1AHI$RBY9eo3S9j<}agloX<(ImJ%+#Br!_l6Ilhv7qT|A4Cl0xnAk-$Z|gZ^ADHU41#|vV?GD^fkCL+#)5ersQ8qiPAw=O9fq)5UzxV;Yx6G^i8-q+!}2Kw}xAyE#MZ^p(XJeefKI{7=1aI+V8@bIKH2K<K$<?(a*Gt9#;bxdjn`kJq`~uP7l-WdffJ5T=$`$^f*sq9wgDPdS29I-qd6q=y~)8^Xv`Ajh=VanU~cWXL_Cr4?%l4sq<R+6LhDOx(*1JWUUY`j_!aZgo~wUiGZs|*%tpOAv_rE4iAPqqHW=haAUL@+!$_%z798p6VV!QBHS5m4|j%#qrKtb@G<ldd<^aza8>3;Uqbjx^d|fzTqx+O%#A{Xa0Rq7Tmi0wwt(xv_0U#uJ-7<`CR_zBhlb&D@N;M>_&NAIb5Z8xdEyHFSpqJGUWJRn#TgsLIgb^`zd&5&Ja(0NpPwkrxvezwygX5fb6X|mc~wHVKH3_t57$Lo!Y!HG!czYiIVREfea9#)Z6NwnAhk_|%b^eW+VBC|ShRqz%?r>cq9uHNRDwPfE$Hjhg7o=|wC^{Lt1?f%A%wS~gW+xPEVLs$3m%F#hKIua(1vh7co>=p4}%w@o#DmsE_67&3;qQ?2LA&03b-osq!%H)5B(C}2mgx7Jo%Mv;f&0k3UCG5Fe7bPioO*66n-E63B3#d1WO-^zDR#cyhtC4z5*A3OQ03u5^zDZEL;$lx|L$gopD^1emz47C!^coWVk0f3+@SbMTf#&;SOj&xC7h`9R_!Ud!dWrUho=p7rX|(i2ed!g!=?sm459*2%kXr!6)E!L05l;)6vgmP-(L=v|U+vKuUCg%fRW-TEWzEgk?XXj|NlsE8GXI=c}i%9Ea#a-*GMExJ6s}+MyNgBwEGSZdGVk(bB$lE=@m(KJV+7=jk`m7k&NsBK<5{)z|M;85g3hedDAx<4AOoZ(IqNVlD{RPtk;ctM9Qb{(FRQ1GF{V0Iq;mg)6{?&==uCaBlQ@I5%7nEe#ih%cE7`@^Av$3QmCEMHj;F!gc9G>C3u=@Kf};^!-zWa8tAv+!XGCc7S`pBhdlyNO&AN7#;_YLf?W%!9CHAa8I}yS{rT#=R_ZabHWMqsc?Pzx<2b%ef&?^evEbQG0M8j`d6EEt~UFAk?6=e*O9uuLcGN~_ZG)ikr>Qe9ZXx4Ma#faPkA;`>MokYcPu$LR?#NDV{by+h<5k2Rd?D_bcC;MN6_}7V|{%wmc9~=`1&qF-`1fW<r&EY=EpmPnk#4nxISDCtpJyU3!sJI0&ob;4Ts?TXhAqXTox@4mxb%032;4lD*7%w6_#ft-(`N(B!uM|$-2ys?1XS*v?<&e?uPb&d(ei;Pbue3InNWqr&8iL+5&wOZULWn+z|c(Z3;^WpH0!999J8&Eq-G{csqIw-VUE6gs-8e;A`-0UtMn#!q?@TjqXH`!#m+tXbZR%{Ilb#9NW)?@F_w#hJFFZ;LYe+crzSzQrjX*2%kuaf6*)fSAT*fgd3vLUJVK1spxiiD!c+c39o?PA%u6J*WexSXXtJCGx#)m9X<_z?rZDM3E^Eb7txjI8F(f9F1izb7fwW5!HIBIRQe+;+rkcd3YHMg7H~uOzx;g+{x5t1-3(uVPoh!yBzz7%0iT0!`ug%FA^c>(4dDi;^lJn9w;|k+{%e4)fLG9G4G7^z=nl9M+ywm$ZUQ$$Ps7dN=IG~ebGRkC3vLOw_VsIPLbwef+!kF4ucTkwqKR-K{nr+CV23_yOJt*LQRy?iFX7hc1t+yW!Y$F0PHO#yo1^EP)Z-OyhTe2i+ef$w`lPQtpQOE?q(6kCK}Y@h5Dmhj_rnsxJA!TqzmGlui#`NP2rme_Av_*U4~u4iC4?si-4LFPJ_d_sf+d8fqL0H8!tbJ4U<u)AXjWK4cm|psmJps5bVGO!`V=hsG%O)J4}Auf5T1|bge8RM2Hg;zjpl$wv%wO=Gtnnu3E}DJ6R?EvduV1@LiimtBP=02CFq9mB=k{O^buG>ctX$(;f3hKu;_!Zgz)yD8^Sx$bg<}su!QhOK{tdyMg#Dcl-QIKn+f5Kgz$QF11!1@UJtKD*T8Gx)#xgCHM|mC0k4FYqs!ps@KQoJ8C?R4E{2ogMTGEHbQ>(X8{P`<B7{Fc_rNi9FS-Zb3+uMsLwoPx-|P0@O<(P1-@5O%(VyF>pYGqqjD^J<n;siW7%xjWem#DKr=Tl>sbf$09duPNb$klHhpq{xj%VTN=(=F)_!pjuZV0B%7vb6HreNy)5}u2038v0X;rZz1VCwu8o`-G>rp|ZaIq3Re>iQr&3tbybU0Z}_psRza>yNOkPxWdBf?4kS|N5`uQ~$^_yN>Z6$J_tXeC^i%FK?!l<-LSkuV%Uj+!H}i-GnYAcWRvf12}h*x&'

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
