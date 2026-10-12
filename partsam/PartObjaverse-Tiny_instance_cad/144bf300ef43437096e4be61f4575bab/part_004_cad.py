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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_004.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_004.stl', 'source_sha256': '801a47880cce52284b32e129a5d37194e2fcb59a323042112b7924c0c6546fdb', 'input_faces': 853, 'input_vertices': 539, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2145954817533493, -0.2000209093093872, 0.12988325953483582], [0.0504806712269783, 0.09057950973510742, 0.41913795471191406]]}
GEOMETRY_BASE85 = 'c$}qt2XsyA_w7zmqW69|dT&=Rmn~O`9=*#U2?-Gd2@-5IO4Mjk4}xe{@2+e_?*!4q)jQF-{P(x!%#+`5yf?-h@3~`*Irlv4tZ#kmE4!Us&*m<!IW+t$tnF-nCoXLjO;eUZ%b^AP1`YN1_8n3oaL@=REsN;tUou9v>d?}&i<1_tg_iX39pW8SvbL>c-99x-ma~=YGcagqP_IC*fk8gLN^jgNV2H1!5Ao|Y$k#e9Rjo>`a<(d^%h^WR{vZFPvr@3%4mllbq0#EqVZp6lr|MhiDE|4BI!=7`{HUO3h2u)s?++H;ex{h{`q&w#m7X}Ij_9_I+u|h7@baSDBFc%bttoq4p?S6QNznt}pA^6N{m10<FCR~c{(Yn9iAPRL9LGCP@i(UWoJ5=?$<wxDlj!!&RYlh?%n;qo)KPTDy5B^%Z~Z25G|v#p-*Nc)35i>Bp6KQ%o9Kxp9*VA2YJNo8uRBWeH^&|o-CknMA<4Jy^s^G@#cI(Fw}KK!?;k6=K6jw#dgKO)qxbG9y1i8(^eeH_UwzCz)N|}Nsf*sm75(VlU+SP2j~CrBA_nb0IB-<y+V(in6V17z+lr(Ue@D|rh_m38<f)y$jr^VcMK>}|7TsJmQFQyOmy(CMG+xjcG4+`E*L{NH*>~}Ig{k7NfBIXFZ5;xkzy4kPjY{*O-_63hrIY>|A>}ZxHnW4o^9dJ!y=#)p8+)S<$m^dSQU|lx7153HJEWfWiqYppzZ)aEcGMlZy&1+mU^(VrM(Bwb8;HN&tpVcXTNNqw3k#R}n0ZSfPSZu0ch6fPPH+<D!KBinJ2Jl%e{H}C(QQ4(V_jrCd`9Nyw%wTD?OI8EBe(*_tJNmVGw=4|uT}ge`6Sj}2><YcqU(PBB#y3i!~FKmxLov|LoxpyZIMq><|xtKVvv9B`pBp8x^)tNe!SFEn^+Nb*_L~&d|oiM%oAhwZ<v=Z9{An}XBn5otpyO@8}lNu&j8f_TyEsA4O}YUbAE^US@ETetL?li=GTtg@L&8ubhGKfWr6|2rJjlIr!f!G?B6c^UY8Ij`D{Kex>lx%L*mRWA^zrvorv=-2<!E6A&IYjT!ZzK|4od1zI~|l*LDfI**)D3i9dXu^fz&DH1rD7F(3QvM1RvRhCVV@^4GlFv7ht`6y4a9PyFpY+GG6|@JF7Lej@&<tdhTZxjXVX9x3b2JU$ltUjJIqotH{~^}d@9N&I=G5NCKX>=U5{v5wm2M?SY!OZ>zxYbAf%dnfpxsepE!Bhaq*4VgFgId!maoD9Ui+U*MFlk3-=66gDy!%BA)IgR;xY~O0E{|=~st`qQgD!)RGjkDr!JUxJY^YGEX#Q)75%>O|#h?DEWHu=0jb@A8QMnP}d9rNhkW$ZKWCqTb7X0F5?T3`GVM~uLFNE#*e(He|Ag7|)D_xDejFHJ|Ho)_APp4i?;`kQ!Z8P;iP55yUkv_-z>;xMJ%>xI#;3_q|RG;M<Ye?e-*-&1b0d_V0j%v--yh;wrFVDUS97voiF2KLAET{a44FNXQKVuI+lp{cQN4H|>}t#|?Kvjw9A#eZBk#EEr-o~j<!X_sYkKDFE27$>XDhr}|SMc2bVno>8%@(qIXVzHlBJqf*sx8$!+ekS=F?_ESUJ#MT;y?RPL&8mZ9rM>&-ddue>GD|*s)VhOmytv6Ksk@6a=1J^$(Ty9u7s~PHK=C)v`9sfXju-#$-%#gK=l_;CHS<SH9*@RL9kjChMb~T9iIIK=WJH~pY!}^_xLx$bqLpMnG!Aw<AaQ&i!hg&cng3?erTwBGjlsM<^gwib@Nm(MyzO?%_r0q~ySCA8qU+}muEBWB#XNuZX`j*^gQB-fzs6=pyGI|0uDx8gRr1+%3+Ib*2Shg-o{~6vbsg6O0psAGZpKQ{<9A~oj_R^k@?7*q){z#_P3mvo+e~!rT63vq;>3OuU%T*rxA@msy+h)pb2=~n)0T^_)vUBz`g=EroEOYeF1sY3sqc1)-_sYEZ-vgvI@h&l%Miy8*8@+^h^}2PHB9_!zr}gy$tdh2PEO0^*l!NbzngqS*Y~^6mt*Ha(l2ei$7b=b^xHbgWBa}Y(Q9AdB)XX-<D$LoF1kLryXa=|aG8h3hgk`z>m^w~dZ*%|n`h@kPt{j+<KJ!)$5E&a^tWlCzkMb1$`;r&0rT+`*24=^;@Hk?N4phWMK>o#V%+;gh;ByYm-S}2RFV2<`M+M1&yVC4-At<Iknc|^F8($xJJx5>gQDB~-9$I`XO#1e_T`Giu}55xIC{~QYbAb?-%8BS<;Z8)K+*NlJ26ihhamo%f7eKyPmQEsj(LHo=d6~{<0EBUv~_jhpT<da{YgXd*IUm-J}pzP7XMc6QKAp5g8KZvB3k@!Z<TdzR%?Vh90*$_{e9G6k;Gl`N%A*W*Am^BS9z%%Pws{I<(sXPIA5=dZtSRwJjXiZJgxN_BlR)Tx4$m+m^&Hzq&BEqo<^eEnuIwJzZ?1$+D&w=R6o(p(~HI5@zq;&<GC;Vqw<Kqo~F6zdPpniUmuEYO!7yZVIH_{h$)GDO4SxU@pB#I6MbHE`>asJc~u#4&J;pE)$60($WqWx=AJHfc(q&lYwuqSaUP7GD*kP6q7D_I>qo1|dbhuBjeN%DK))isIIw;Z-<CcN^gN~Ef5;2@4ErS4d0Lcbg!rF&i25IV4BcZR;+(85{$|2M=p$Uw-)U8l|DqeB8-12wKF=8hJ@mTh=4jVh$onML*S({NQ>`Q7lo*11CLDl1w7b;D^hCQxohaxZdtjd#&-}~Gh2CN$>UnVj^6WPa*RMHiiN9Hv_31VR{*x1=-NbK!h;w!_^y;}WzFq^MUm1&jd3eCTZ)MRPB?94JWH92-Y=Atsd!xTI24USju6#r4U)B?G(v?AdMh-<jOFR%KEHn1Qtu@%Mve0Men<;VEFT}V^%?>^CFy?2;-_hU6>7Z|PpDg;44_J40C+ObaCZWFfFn`wml<Q+{+&{?YCF)?Tz9YKcpaaI;7yY$QJr4cn99*Ye3&y+(IVQT{S`FjaAN{f|i^KKzUJvm%2iwuFTl=8bjzc~7a9%Z8iG0cw#QCec4*w%d(Qf5$GJlL3>(Q^Gi{T$oR_b8yjk;;07ecppmpFQLj(f})=$-apJthr=elP&}$A_Q}^MbH`m-dAJxn;8MjA0+KA6{(_|6Cl$eVG5|-G<QPc4K}n;(YLH06oK2j8{Z8^lNB+=uIYtOCDtpVc(9ah<1l{#XLM00RKg9@NY8?^G##FRwv1Qkx^lj=tgd?3y+(ko0Y<mXTliF+j=Ja9|mB2_trw3T}z?6KE=5Fjr~x6JXv&WAHe(^Q4jt7)DQk;{3eQDgLl}k2KvK)a&3vD&GSPYj&wjid)8r|6mJN<s}6ttK6D-XdE%35h@UZVI*uQpKJ)X!Kd~0-w(mRE#j4!!?|BLPMlS5zW}zJLUo~Kg<QK6Lady2~BJ=8NdgS?6SM+yzCegJV9kK3)A4U9rF^eUB&C?SkAKPu{v6V#E1{^>>y<YJ=zJ8JD?ja+wPE(`KGsi=}bWzr$dH8Sc=U?Q$+Sqe^3fA*^?32~rEkHdVH4-dZ4sk}sL2rL(xa9FQ55~9H;#s1XS|;}qhJ7jOd8ZR}(|w@i6B>^Cm#qTbHP$Y9H(7(aJxv8Y=vI)l*L*wH^(zf}&EDN5Zqu2_XJgPz(c=>ONZj*#q5rG_{YgxJiMu!i`qYOrL@#!3s2mT7M?QJhLeEmDhvb<a^VanBgC5s+g!o;ak2qzDK+p6!Sp2e&g`WNLbhKMi{PiM#LI2PRdg^|DqJPG|r){QQ)P0EPu{<ButO0%3KT-!rL>%&*nGJeap<Z&lKZxhM)X+Chmpa=o9_M<W6(Rb<tW7YFH^Tq%6zJ>YB#z!R5&lDbq0gCv>*t1tk*BK{^x?O4>90ALdMoH>a>}?E2M!{>?hbu!+dvt=QP@wk)P<ny!Og`l$9S}xkX3Y}$N}7EmAWkFFFo_lX&A3(7)Q5Li1U6D^zWy;h~Go(|3=WGsiHft@s;C`XxG?(7JBn+7_S)i%WEw3kAtOdW@GvvE(3jP!vS&}e-e3S%Lo17@li4^v(I9l6wCrWWTVV0TQ7{G(K{pbO%bvl?c+8<A9Z<(=+UOs&7Kqan?7fuABvFmWq*fxsNFjX{bqwuIWB>DXg-?(eP%qaqZi_S#Mn0lx)vz;7)|1My`e*2Sr+TGGUrLpFOx;@7b$htM)Ue4>t5*g3GL)K3&$&JH}u1+d}KYg!aOvaZGb)@v&^f+{;}|{?-1Q+Fi!GxgyTL%yO0U~=3lKOACGyc&%2l5qBnfoR^mR{fI0*og#P)a<ZlkR4*i-J^pKl_q;CC(L*J1f`q7*i_uku(XU|)cP_KM)-(X}rf&JNkFZ8g#rC-{+QHawy40_NSnGf0$>@()Lme74R$@(?+OoE>7?nKd@zREhXS6c$T${gswzmoZxXyZPX!3O<QdVlfjwi<exT@#dU|G87{OA_Cfgx=}mIMKBpQct5=L*&1pGW1foztLA8g1`A=jKp6&4f+w*xzF;^G9L3Hai263^Fiz1P;{+uLEIm#s4eSJ3m-8`{N8@V_1&}9q8l6j36tZYxX#k{b%yRWNp!Oj?n?~)55#%tFS_Glg2YMu)&l-9qehC~^|B-6dwWhJpH%*$+k%$Nk<XjdLY$lpMAr%&mT@+toDnBSYUuT9;5@luD*XN9B(9bxGy1z@I_`@L>=He3W$Zk`pgxGxIb3vmuWWMuG!IQjoMC~;FTg|Aw|=-d`{fONPz%Y^%-s%gX4OahN->d$V~4*}X5<t0(~$nPO#}T}ixBa@vH<s~gLvM&axPf>zrX1#<2~RJ>eDMybo1~-_>b6x_4U24=tlo&xo_5Y;(lDK5<W!YkDY}1aFyq&u3<sa-|ZDJj<bp)pZ$FXOPr*9lE3a*9{RqGgG4WwQ}z}6hS!{L^+it%ZYc9s^U4B!Sb5RSRXb$=*8MXgPT-4y^8L##q|T1qU7(-ZBD!(<tJF!KZ6Z#-1<-puT_ANy{0jY9X3;gz(UNE4CeGXVIe0F4?bKNLJj+X7f5rz$-AAm%d~W&~`u*_!(%$21a|O#bL7d^I`bnHM-6c=GC+4kI;IqHv{Wc5gRy`;5UDZW57o?KwCYwuB=+1BaFuvUv%I6yzL62zJSB@Vw#&bWvOUP&84IhbX50U*rE6w|e#*;;NBxo{kjW?W!W{|h|zrPzG$FURP|M9Fm4|T-OT_O3jUN7@sd$S07XgIE0NBw}m&vem^64-x?68)eT>k8d-j<jorv(DLO_ma3pQb~R6PpUz8j1yfuHeL2T`@QZwkAJs|uD6r@-_e}+r&*ec?&y97@2#?BMVz_~;Xg7&&Qtbh+^?z*_Y%F-UO7)CrkV!b)1{~Ajv!B2FWY-Tca-WO<JTsY)L&0mmG%GBO^(-gmFrEjDd&k<w6nyibq{rzHV1md@=l_^d?5S37K-~9Eg(Pij?d-#$B175{lU48qCczGTk`+H`>6+Q<h`Kw!(Yx{`i=I?vt@hHcckqo`iZvCzi(+Py34>|)O`f6$ELIqeS*VF>e(CT9nIrSE75z7lj~3Ibu-?dy5ag>Z!r|>0M8#Z?T9XV=lad$*vpf3XjWfzZO!L;Dt>)0j#qK$g%8R3&J3CkJuzP$(W9qHK3b3m^h$SYik>*8s?>AYV741jL-Zr{<ovEz*vWPiZ1Ddk`8zT+p?}3}q8qb|$b5SpPW@Ct!Gz9Ie|^CU*7H#r^k<61*Xp-qJ{KwpmW#)}IyM@*J*pbkU)|OUZOvM6UOlfXSaT_^V<$#I-%_uE;HjO6zh)_~A5Q-%=>7+;OMUU2P<vu)Bv>Y^)XjFb3-mnhsC!%_u3HKWVZYiy_Z!$v;#_AP^2D|feEv|*vx!j|u+JxcZz=f0U-mcKtw`oyuoXUkD(l6%V1$06DfE$cT>s2i$+{Jl^`rg1Dn#<h#r-GkE$D-cDl(s=J3$|MwY}iG8_0hi_n$YvbwK<^xW6m6i2ijtp<j`>PFTn|0qeV<o}2p#9^||=vUC;vxlG<KXw7k5r%jjw{ZWwY(^|1s%zqbj?T(YI>(_mt-}(Xl!9W=oz1MQi=j?J_uCJ?u=RhseQs3JHdA-E_-3ZPTePd755AB#UxvoEF$GqPjD(l)9$$8@GB=^0>ozaN@&j9ShTLy@(9m_5KHPbGJ|L+}pq2KR|OP#lc@&0!R^!GXCI@xG78+tZpZ^5bm%6*MCq9ga)EWW5ygOTXZRF3;dxqsF|d&;<&sc@aIy&Dbv#A)28eB^WNcf(|zXm`G1o&Ml?VSXE&pX#>7eZ=W?tlL27x3*&bFQ3Ho$Xw{h?&CRA;0ny!N7<$SHd|IXzc_-jp*}%_5Vvy=-2bK;#C2C(`e`&Ri1YXyJRj4Vt&_TIS0>}Uot698m$_J<XCq|)cRV=EcE`y5lKuNnc^+fF$MZm~#0Jsz(s<5fn>7>p6dWw`+vxDX5HzE49yzfO`igGy-a%i@eWrU_nKwqZ*K%E&IO8nhc&EX5jPa4{1mg^zS8KQOjl{e;jo&|{Z_oD;QKFlEm*xIRkKyx~YR92BDLh}|A9jOY|I%nd-<q<|IQ+T)oOK%`@#DPl9`gzJxAJ|V@7yl+F>1wMmE#6EaescbF7ChcZovKK<>jIqjWUgs{@(44Jg=;PzfVSaUguai4E}eE%JVGk^(VQ$GA9nlb$Iry;%8i3H(T=Wm>zNb=E-v_tygEsOKTSfedIRLjWIi<U31M0=s)Mnb1`#iL%gS(5{!2LcqzJ3T9fv5=Re@zHp67h-!$^vRnN@)=az?Fx1WrQ*)==HD{dq7dY9!s#t0jZ_^Y?#eaT7>$<wi9GU60Gi08Qz=Z_VvF&Fx%IML0zedRvSk$(o_r~U;0sZHeiRtt8=xVU{o{NpPnj+Vb8+MV;;G}Lvy^v{+*6nc)15tw&hC1109Y1VTX^n@SsJ^d8kyJ<5!$a7Dv@C}*I`olrcgNH+pcHlW=ZuYC)U(o9u#(i+sX&A>UelrA{f0aD-$O*`2SCr^_OCPyDG@AS&^GaLV4$nO^zn1Z|FN=o%MBkZMuS-OC%yx&~s~`O5Ipn#eu6KZ*>AUFqrFdBv_QLP*zOrn3JjajxN9Lm*>Wlm3583g4Xy{cuPcA+f{n}VdbUo|C@v^=~&cS=b#Q~z54Zq0!j?p3?#%tyV#994H`e$w`iu?V~g=ULh<OSwqE$%ay28(Wv?kaV&z0vS~L63sJ^E0g1hj=e+wB8SW#19!q+nj;WtKS!0pA;f_8m^Pj-=GR}#Q*VqT-TM!0{`CiL^qbySRxp96}n$1(e*d8MYo4NLVdRPgI;!n>|@4}8(c@>i1X<7V)?u>_p1yuL^pl^5r4D6bNKsgMx5S%iSAf%7J6p4Nco<}I<)Ki9(vVWq8nwVB7O}M@#~j{f2(Gq8+AUTZY!v#dyMzIZm6^AQb~0E<xqK_t3{oIexe@y{o|!w{oE164{HED_M+@Rw)F$C?`d73e|d`c!g=o?&w?S)`=^#Tnirp|dn^&%TzWSO>-`M;OUIyJ5t~KVmnFcz_<HDz15xMt%>Uy-#2KE1`gFy9t{*uLecV30zpnZc@xPyke)><TkA3ET#D9GcdA2+t?P~f{=x=^NFFjS}uOk@qMDxvv-!1*fA?+r1K^!xGQRrTCP`6Bc58_%ubnSa8(QWPjh5xzgqMIdyaUOhx_k((FPv{lKVxD|H2)(^G;#7WwIDXV4LZScZg#Hfu0^Nu}oB~HBj`mkZ)MqYq?d3YmA7}i2Lw8w&{F_8${`^4xnh$hs%Up@C``~$?)?z*UPp1`sEgW?)QpG}#`!4mg-93i>W_*h{U0vn9nC&&zmwxpF^qv>wdMEMgZ}5Nm4f$8gEA84wedO;V^30R(t-TAq)nn*gZK7*$k4U>_w@c9TmKWW)vqkbWmw!e4G)>`u#)k1qhk9zu{h?3XiSZqZc8#9H5U1Zu#IJN8alD3$Za%^KG6M15&{!M_|EzYrAKdx_dYe&*-!e-46I;ANyAA{T;X+t1_D}HlnmUi`SoX8TlKB0GX1@vlZPUcxF&cH&$GFMwb+r3Q823G=5GQLs(amFT(BDGX$F#IHp#OL)y4m3h^eGKRH_k?4d}FvS(l>_Qr3BjbbjI_yrR~w~;Yd7h*tG-ufA0Xq-(3!Ix?D%yHqJzx;<>T!UEGiTdD}I_Df3azkB-iF5och2JkRQD$M2CQ4aWJjaWh;8w9ks)i4FP-`tpm=KkdQ$$9FsVeEyT@`sa7D@7iCThyU?V+%HY+h<W#s`~0=lqMP;0;l25K>O0~Wq7IcX&s$za{@sgX-FC)%c|F%tUJv7UHrkr0@_a}y_6X<qqF&HTy$_RkkL>WTxfXFs&BlH>9=|Wrf^Wco-vh~0k6wcOXIz*1+76j`{&vRwis&=@VO-y}#qUf;Z$zB!_#KAP%pvjYKj$M(cptnkuhMj*)PMeB<auZ~elN8=5cSOd1^%^L;ddUN>f-wO@C^9-MMIBRF8MpA6odceDtOP`x;yGzVyWb*@2!gWzDw5N_Xg7*;<_T6JM>8{<voCXdN}-dT|}JCTjhC_BWpSI_h0CmYdGq^^C05%&yL?o_(fve%DE$-&bguAyo-KC#GyWG^J2WSZ<l>0ak)FrcZ2gIzoGeYzkYfo+MU=R?e#p1c^>bH`7k09{-^6meA~Xq(BCaVyM>QoA6U>2`b-!3or-bsiQGpx8f29CT7zi(F0<V&d0uNTR~mZQBhihD>wvAxOP>0Rf_P3^tqgwmHF6jFWe!`7^${%XJFbpLefEUmejtBic^~3fx+)&y9xJ;3B_8?C8G^dGc;R<-SxU(Lkv&5^;#~d){dN%At+)mK+VdxV|7TXj?{HQIA)jZ4=z4w=`S(}@|3wM%`$A*!H~h|R%z<n5J^$mcXin$!UKdu%s(@u~S`MvGuM~emqeLkW@qhm(H2zipul|IlX0<B+zkfpW-pM)zTlSE+n*1U8DdJXgg<HrKz9v6Ko<vjp3-LO+!tLY=Uyy$xcX9@PCRe8TMw;T=Xo_zpz94_WxSNR!$Q4GAZzi8e3@2AOnS3JoD562GuqXK_@&?3e<O<7>Hy|%$Svq1S%Q6#f#6skS=x-yICs$aL+(urGrg%kSee#Or6^J#+E0C8Z{!U(&ycA9G!o)h{3U%_r<i&_Z$a5335sQ#3EKQz`JReQ*EW{GzS;z|z>yj5BFG=i6UXr{LP4TIgMH0so`;zzN_s7!|??!A!uF#LX8~IS;XmW*9$cK_ICT=2E_?~<*`3IWfnltbrxiZDSQaeSiFp2!9Wp6FZ>J0ou{)wL}u1xWC#3XWsU&xgy?m|@S&4s3TdZJo;>4~YRD^olRP4OHw#WT|sPfawPz*CcdrzsvyoKGH2K8-k*d>Z*cVpZ}`Vh&<ea)kxSbC9R8?41VuLM%wG@HcX0ivP4QHL)mB=|yRZk0kaWA4xumIDvc;`7Gj0@>%37i5tlkZX;hr+(6t$u5dH?2J#r<MDiH&F*L>d6GxHvC-)^bAonG&PE$NTu@HHFayO@6`<)w2@w7C>(-Sk1rzg+g^lN|2KvO&;(MGPYIC)0$>@>x5(G<@~tU#`?EO}1yyu?!EdCBw86wgX5Os=pPdGg+;c&IfuhFLa3T_adF#<J1GF!Isl!Neit!Q`Weq2yzTp^P~yMZA&pRXCKqzhwcI1=18BL>xjsg#LqQiVr7_Bp=B(h7&``L)gY}Vjy`a;|^n6>azjF!Q=zTgNUKzp{!XDP4R)mVdTRYe;_e{Jb-ZrGS4w7atvWRgULgQW5_dDdy%VUX)JqVjo(MhURm~yTxrhEI95C@xzhgSu`^?&rS^*7{g>!UU10|L<+3cFWqFBt$n%otB&H=#%kSnSrXkNso{i{A?#ec@5%ZGg<8el!E4k{E!jD8(@|jkRR$8`&ruZS6;s<Douc9eFjX0BhDlw8clRT2#ByJ(!!Zu8r;>T%<A0r+hKSsWTxQcug+uM;M55*ni8;FtQ8_16mP4c7Ur-;YNPm!M_9wR@-c23e1KSG>JK9zYWp4+Oon`PN)if5uJ{=*68#<BWFo{{Fpu~nFxJRf-;Vs`R8<Y|eS$TP8>w8U@Z4hvUVwveWH6ix9JG{x7`6kkVlkgp*wAv(w%jJt%U_-tYn`E2qzG{u(^SCFq@+e>MRuO+S{PtHT}xt1;CvBKr#Ysl9U=aH`^UrL;jqOBRsOX2hsc}`D}|8(|mI@?}CTtl9dYgDb(Ans>sUsL<D+F#W^d&aU8mYufD$NElyWr4)u<bmXaXo~l<%ue(o4kuUN^|Wjp(Tm)RKI4c1<f`4yJPsiDB(@{B^ZOl$p5&hNQT&C~hj_~#67P~L{7$a$1$ne(QI@TtDL$Dvhg{)Y^2y{2h|9>IT9(MTFUaGGH^~*=CXXk-OMFEBl;2MxekV^Ne@|2VIluRu-+fM9@mrQ%w(PoP{}68wFO%OOzeYSqevSMp@htgO@&uaV7c9F(JWo7JexCdy@f`U@@+-v4<d>QE6`JCYX^KA~UMElP+Y_4N&uEIjB;Fu@N&bd-jr<MyTjEvnx8$#g3FNQHpVAUI&I#;)BJBdlJh?_UX_r!rxx)LzOXT;-?-0+E-yy$8yhwhJ`~mR_`4!eq@z<7pvg{*Ka{~WJ{*~xTu1xW7#8l+U6#uNj6nC=hhX!=vaVl~ba%Z9|xik5{jIWXZ%RD|1RjwaspE%B+*q`Kaf1P5UyiU>IkK_-??-9SIsM}Z8^(*_9T<32bhi~j>^0<8FxIH3&PE>t<&SS;jYrpD}yk-?o;+#q1JW8UTJg*dgOH{Q>o`;IRAv!z#nzxF-B&yma&vV6}5kHWBV7(Mq`<~kG{vz%n|BHMxP4TrF_Bn+Mh<nKASr%^DY|9oCXA#56XOT}Qjw7E=9zh&S9zi~XruYQQCK1OI$C8gHpGX`>K9PJ1F`PV{c~7A!zMQ7`3gT??<i4$-DZZMf_&VY&@^$3viPOo~lW!tMkZ&T7A<iI=A&;gh9z~o$9z{MUMUCdr6i+@!DO^OHM81f8K5;zxeDa0FiR25(mk_6rPhss8-)Px(%eE2slW!y6MLbNti+ndRj(j)yPMYF>TegoFON=9rB|k_!On#7jFL6KlUh=KP?c`g@R}eR*8263ZuX(aDMSr)EFCkw@+?AqkyI9v<>|1i3cXJ$ev!BW1vXkSsjC?KeZ}PR|n^V*!dCe-W)^Rj3hPY4rHLn!kM2yvb%|pf46Ax;?=B?uEh<mkP^IY-O#I598Sue%a-lDFVmJ%0`E8IiAhkl9&Tl?4m%lgn1??O|&yJa1Ty@><Jdz1SUgUS8L2NT1{2a^ZU6dz&PFk%QXj68&V2r-yEn7Iz2Dc+u@cpG9D@;2nHh~3GP`__u4cypTKEr`9zTadRV`jfXNZ%Z6Z-j=)*F^Ieqxt*qXKjH}Te&mBv)F}C0Kyh_{;6wB#4kPy_??ntD??v8~ID~u%Yo~Z4%bHr&kacLx+BBxtir6$o-I}JTb5q7@%2>(c(unc@u*}0r{iFnWwq!qi$U77NB=1b#j_5(&j=TeF*nxHJKs~w69vlY`ww*jKe{kGd5Ni|vAg@hch4?4=pUkfcP4Ol~Z*p(ex(Q8jcVbua<XXGa6t6{WNZycjuSHY59<e!jbM~Pgu{L=<^2)?2<W-ncWuiN|JKIqFzGcTOdq=!PuJAeebNVU%w`IF6+i%%nVk~htc`W%s;tukI<cEkm$q$hqrzyVAvIE3D#GT}O$afKUknbYjOWaMqn|bf0DSniu_zB{E^5njqpecTuruYS7EcpfUE5w83SI85HhsYDiZxWA_-z2|5Q~V-vANfV{Gbw6xhNk#g%i@XWhzH2ek)I^)AwNkTN8CjoM}CC3mwYd4cZ7MWobJ;UKSn%5eujA*qbYtVMXr|^M}7Y;@j3Zj@&`1<Z}WS%`Q6*p6~AoRJ<G0IcAj{Rc#r%V`7PpO@>}GI#FylW<p0nVe`eVe;#1;F@~7mFh>yu1k>4TSBfrPI@6Z%ao^OhuAYLU;?pyNwJn!^tKA-2foM%6e(5`Vjud$!W<9mzae~bN0o)3zjBmU#`YySMh+Q*aMCO#v-P5vN7jgrUi3CHsW@h0(!)35ojcmnaM)35cS_!Z(Kr(f$!@e9N|<aby*#ns-Z_BplR6|$~@vS{l6;h<^xh}no)$TJgD(G+(jW+AU?SuK9gMqY?mgIxKPv8*w%9JxXd^14KKq6fLcM&zZ5g^7*G6&54UL(EPrMy@aid3s_RVh(bJX~|O)-H2()6{aK4Ow374N1l(E+*gIUi8;x0(myxr=*$|YCb|%v$<q@vv5yLWV@(uRV-2gZ_O-}s&=jvi{EfT{d46Ih^8Dl(i7w<W%qJuB)L0wUm#nOZ!sNN*LZ8&ENmlx*@olYPUbJSeRr$TF^sUR!8gm?rvadx`^t%>)>ar$9>6?b_rY9!X?>G7=U#I`7w-a-&r2XfbsKne_{8x=zFoz8PH6|I@RxZ{`jjft91vHGe!rbKQvn=$@MP7(L<>;4-S`F$R{HzAYFBdU?ia7Z>Mjrf5BbwsHh&jk}(bt)JT7Krnnxtl3oT!yyP4clWm8iM1CUset7Sz(SCTg8^v8<D2UPK>qU&}gM*445;<i7k)2G+K$WhE>tXjw(enp@^cO?_6Jrg%wWW%82brHIwZ>sVHS#}#<|JFzx-UdxKG-GbyQww<~5BKnXk^d?vR=*E6^CGSB~ytid7Eo)|3JDTDhX^M9s{z=|}yuD@WZ(`e8R-f3OyghvsZ)%xtSsUio-LjsRHL<LLWi@Gv|3Pd>-iQ6{OtYuRTVY?KoxCr(zh!=w^<yo($$Js~$^GfCcq_}wb4)$SE2bEmQpDfMJ)1i@=WzKy{qMhj{Zqet)BfXs2L9jQ{Lh~}ru=4OE7t$|0i<X1RI=weTmPvS^8c!yYyShq@M?k'

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
