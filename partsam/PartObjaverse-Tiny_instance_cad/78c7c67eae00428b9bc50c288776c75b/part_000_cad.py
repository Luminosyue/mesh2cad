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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_000.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_000.stl', 'source_sha256': 'ce7075046322dd97fe006d43f1b03207a19492bb5ce17a00403c81419044ac11', 'input_faces': 880, 'input_vertices': 491, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2770555913448334, -0.46473070979118347, -0.07185250520706177], [-0.1621924787759781, 0.37799298763275146, 0.19161733984947205]]}
GEOMETRY_BASE85 = 'c$}r21&|fj+OC`65G=S46Wld8Y$Rxa!5MUL1`qBu5G(}C1h+wh1P!hmGBXVBZj(T8J;4cZS^Yknv-{S6t8U#()vEWI_k8)**UP$h?_DRTcI-H*Ed9%7^=;DpKNAXCmT6yFsjLAV`}7NK-?4AOp1lXhvXVQ#`RCKHx{d1u1;?@mSVMDl=-9V?pIl`Ea+T{;Dp&r1T%CIL>DQ-i&o;gKbm(aOYHhps?fA*>+of&qj-UR{UA%OW`~k)C<PR7g@c;NP(WeqZs_#0r?~{67N1v-`YTDZ-%BZ*0R>$`axO~?6d(g>9qXBKVIKG{4kK!k;i1PP6sn0mRT_vsKhveO;Ji#ZOJf45jIlkRsgW{{)c6@v7L??ettL5^?Z*cN>Z{Kp_t#Qlbzq_b@$DecJL+XV)z7-LzI@dQ>{fidLFZE3QhSzlB!^=-np2SO4XS!4eoqSU!Dt^sn<)5|4iT5-etNO1UP@bn#oc!S<e^7kmcaCrEOQ-lYT@_zpmh$&1dQf$Ban<h~HN=Ux26xbS7Tm8qO*UzK4z*MM2Vbb3E^i~8{5M<5&l7XT$&<aD#_eoV<qx~)_?|^SXujSzQT*~p@)N#t^2GFSq<%AOKJVmj^vLPg)487NU%0~YJz0x8^@mTbt2`5SJHCBsndW6wP35_HUirHo(Y&mxA-|C2Tvtr<old`2U^V$~CTkoDly>sleX6?GPm^v=9&cHX;{TZ8^y|&s%ZU%@P|-Cn-c$Rc{C!Wdedqnxv%R^z{5SEP{GPYZoO-<bit4%!U)6YaiKpwjTSW1dQakxWN={S!lH7_fJx1dbK410xlT&qW*rk4Z<<vU7l}&!i3F`NYyiUBQM1b;~Jf!PQ)ko{0UIz91@SxUPhi$6oX&U93c~^CoEvo!oQYlZvyc*{^LsVz&L>ixUy)|xkx2Vqf36#IvCe``wz0<E9FP7rlkJEa46i54_>Bo~!zp?kK&Ti9G=bYD$Z;d{oI+M)Ne!urp@!!AEddN}3<@?6pdnHhL%DixV?@txn_0PB~|6Oa1^XzRJx7)W*`j4me{&<wjPrFRlwf~;h&o_UoU(OSI!9Ml7_?qfpbV>CO>!dt~uF6lTeP?HCs`#7dm48i=v##qZcJ8GAdbT~2UB2h0&Kci02h=&C>q;|QepFSh+s8-bhuzY8&XU{ZdxpQ&`EY5r&aoR&iXT~D<I{SnGd?l#<$FS&>RfI3r_QCqk@CxhX?y}6X`hzesq3Bb^;!RQ74UL{{JS}vd9-F6*ZDJRt@@1>p!wz8v-kbRyp(YKfIO3&`0xoU<(H|UI`0qBJYHI%{Fg_no*i*C{zH~3|B6x?=X41)o=cX<5BXZ_zjRxT!{NosbFQ}fy<9)S-}h!{t8v)=TI;IrFRCZFmaaGbF`b_S!jz{<h{pMBdCk|NpEYg;3aQ^}i`DOwY09&#v*U-P&Zl!VE&i3Nx~_SZbiJOb%Coka>Zv;}(%-l1_0YM>_=h~SRe!tc8n;3pwBJ+7xBInJ{JoxvpFCXoJ6BPi+^=J<4OO16$EwaU8Js!;;>ovP*HxWyH|v}{F+h1X{dB>}GpvtOe@O4X8lUmQFZl1r@Y#Kor+1j*8|2nGldr4#jqIfOJ5Loqw2R_PPnCc1hU$ObQU3T=T34*kn5rFA&(bB1A5$Z%=J#WB`B`eI-!*BYoqmIYm1oZ=$G3+pR{j=sRe$`U%76VI&2Rr2oEv$SXIyS4Pt2ol6@Rvy<6Coj>%L#JwES_iHO}m>koLvo-%F%C(b-hb)xxSXPLS$()=+tR=GOQ$-mH42?$q@T&a8SW9+vMJ<?=o0pJ+W~i>v%gGO1sl2Ry6)amFX)a7N`nS6KZPtD}8gCB6Kvm(KXF^N=Tr)NlOD%Kzk?&XbA>*^enS4%|;Y7hjxk>X~#@@qf+Gb58E(@;^S;`W!t@>#EL8$G00r%kNxA`(ojrj_-YT;<Qs=`$ZA{zNgbQ<qzDeek)#geCy_6#ZSH$;qQB&-*9}pdUN?Pmla?3xbB1HW2@g$7hL_?@r!Cd2A)-&9bY@XwK7oW#^xi+lUez#h`zeNG>%sM?lc<Du=jsB{-vGDKlzmt?`gb3@k6#LzE)}N$Ig!x|6!HlZ>82e{uZHgb<qlqgVjRo?d(e@-s(3?@pDVc=Nz+ZOpqTGtUQnRsNbVQ<c}OApZkc_rjPPJo#r}MJytK(`A@j6D@!KDfBT=~+Sd=Yf7^dJ=<j<D{VV^~PCeJnc<T7}g;*Dz{5-!|;~yx`^3#fMSln69_Jw<jPybH)=%4J$lm4dsgBum!C0Ox0Z#cfy`JUEi$(wp!s&hg9kCPRDtCJINJwBs;tDR8(m+Q1X?IWtce;36cY^nU&qSf!TwaU-)za3|<^6#srJl=AOU%pfELnkQy%nz!k)F$OWm{0lb1ghuKI>lG$pnduwOz|04Dn3;P<^Ll}<Irt|{E#Zj&-0=E<x=^Z*Jyoix)|Z_dk<{Tewi@E<y!?)DgT^dnwM6K6+d^Q@?7OP4d06L%Fk3g!sUDNC{OGss%PyY<yo*_`)hWGNPpi>dRhLklo77@a_Kb=d~UKnEYNlBz2d}s^UR8L`KjNY_TNX=qPfZ+@lN}$@U}>Q-#a9;v!3k-F^c!hQvG?eYW@434}E@&N9#ZMp5p%uQ=X}n6`yUBuB*t;)Y(@4my?xe^fcw+zGL-hto?Xs!7(S#z22_<Xt$i<_;%tT)mdS;_G86Kj_*01Px*HqQl35|<?o2+s^6P(nB)7Ni|nXpPW_%0eU(4<-x?p^=iKVO74OZd_*HilKQUDK6YIS7^0~~Dx0C8$9ZUCR&LwZgw#wgZyYkP?qxkM^<R6XEyz?C5Nz(F||9T7PeM9GMtLCcbhlBEYuCv!QlfP=K)?u|7iog2osN-MqXdOPCd(hvv?|dsiDoE#lfv1k|ompLehQHnZ{l@Z}Cy{^rq4Fp0t$nxaoSw(BJW&3c!LH{A@4h>Z@3}Wkeq(*E_awiq{FVB-&Kb|fzZCyri`GA%uf4JURQ^{p)bH_OivQ<|;!|F6onziAm*wBuCI9|7)pP5-`VD`tJigCOCC<su7Nhu{gO&gMDP8ZJbUL@WZ+df{R6U&Mo`g-5|KL&Od6iM|p;_F1?YxSATUFzk?uhDqmrwEUFS~p@VG;Rfrpf<yk@EQNU%dbE{ySE64sIsD-EFP6#-Ym7r<ChC&3f5U{Z1LKb$c|0*3a7Sl;=oB#s7Oi`RmqHo;Ix&pER-Jw-ix5f5z3m&iJ$9n-rAatb+Xe8MV%jW>g-YD?CXXXuoI5Apep+Plc?jtaCLesqz$ju6-AlFw)<*Jqexo@b^PiPo;#qF3v+cbf5hD_m4R7JATr2C5)}}dHXK;0sZB#{;2$`x61!%yXtvbR{Jj3M925u4pDrHyQ)8Wtm1i2i1CzB{R;*tKGSdd9LMvFWp`Kn$Hiy;>+$*4kDFbekE}Rt6rVMj>%L$&YNhyH^<C$rwY-JndrBvC-Pi0F!HOR<LD!WxD8k?O)Xw6*e_gC6f9Gt~zp9Mt%u`o+il5VZJD$ho+pl&jetlilbGVkqp?XsHeLO==<xhB8@!wvJ^!L5HzH!~(t+gKceGe=Cd{USH`8~$wRqFRiY1LDwrt5QrU9pt%aNh}8I7stVq?qF8Wm26d<LUY2bRormrSs6L_p|y<l}Ens{adqg8n+I)lxOS>eU2Wj_ndaz?27MS!}Z?MY7(e;KKI#=Hfmm01StN&F2(ac#OK@Dr>oz5T~yDjEE<P+)RRA(^3TqwJjLoMfA9-k@8wj=Q@psYw{2-%@6Z&=b7+9Bx8Eq`{}@|&vTA<4J=)3-x8(cY+wi`~^Yp`EXMUI5(|YdxK;tm|o#Wfx{#N|Kgv#^R8^`x<c&u^bJ*wUBnd4iRS7;o@CXe#>?MV$(|MsSO{!IN?{U*Du^QUiUgv<YRmiEz~6V-30hsxh7M(c<7miE^B@{|8Zb$-7=^)$Vsek)8;JkPiG>zm3yIYRZ1jl<`Tv&!?~s(YPeKBM@1+mxs2K$q|B`NH+S%j$Vb@xJd1##B^2drv4nw6E@`IYTrKZH_A5cRww)QrElTuzcR9*^^)JdFPPwoS&(2-gL|DAA7BOeDA67?Ktn{bKkKSM=JjD5v@1QXHVq=im&!k{oYEcdcwRKpUofSe{(^3a%?~BzpuS#YwG^qf2-=B^<43>vbcO-eyi0a<%!y?dfHohKgs7rYx{cT572Xk_id2YfADYQKc;azbXoIK>sRIHKH@uPKKpmHPV9ZzUGbi>vGktPcmB^?E`P-DI)A=j7UAz(+a~CGd5>z9TjE+*9=-?hUR|j8c3Tu5F;ej(=DF61H+4zX*=wfid~!i~Zq|+R_kHW!_MJ1nc;9&Peah!}-+VoM?ecxsYxDf@Iey^p8t1?B@qGA;{0Dk|v&Lo8b58Ow<w-P2>xa)xR@>={uewP4I>l9u+tMEuA3a^`_E=`cR~_%ZF6PDO+jov=zf^m!et#M3S|`5w^7)=OJRe#e^&B|XmhXH1%)4IqwRD5r>w)#@^FNOp>(JX}fNNfS>)f-WpL?D2{h;+-cXxi@KJxkON8dj3KJ4OJC%$vWQ@*qO-8WtDd#x!Q-Sf_V_xaY#SFUrzzTRGS-Wad?zaA6i@_pwF=ZUvqJLU1+r_OyL|3quW=Rc(Pv1<}*Jog8?&jHR)Z;EEF`SqQXKHt;xfZm&(YpnTg*F^K%^rGIsO^s5X3sn?<EK={s>Mc~ixhpH)_x&&X!aK;LelI=Jbsbn2>F;|gJyw3-{@qntehSWc-}}SFr8LgI=LFy9;(v>}??=4<_tYukzMt~>*Ymi5>g4|G;d>u@YF_t!%J=<F;arO6K5h-qs(!NtD*u6#8n?AqwayP@k<as_<;(N(E7jS1r+Z$irI3H{qWsf?RA;Mqhn#x8n<oEFDUHv%H;(Vw^t<W|svYU?e_kg!lepsTBBvD3dqvNOSIU$9mg>KeSfAq-J$HO>Ob*xkXOHKZ{CS6zf5v6yiFZx;|C*)z&131hnp{zQ)iv@t551*N$<M{}yzg_<(8H>~$9t_S-{;~?2UX{U${J5ASov$tlh6Au&x`_!zduX)Pqt9~zxG%COGc>9Gi{W=&N1aFK0xv1n`s>mOsn-jwx9Cn>Z$Q5Izf4Iey{kjk~+r{Wz@JG?4kOL^>Tk6FV{l-rVduWm0K(S<Y4&|M`{0Zf3bSkQ=ZNBUFWUWTSxtV9O8O!=^a;Eb^6{z@*dUa`@Vm%H|CQcT~z*<wyMYX-oxkf9P7Q(Uw&vI)fqTP<HLQyGvPzDQ_uNc8lS$=iXZ&O@qOPH+dO}IR~%FP?kBGAJ-rkEP<*f4`abT&UlIPkmFuqVFTVFD`1ai&RR69&HJ+FED}Sl?%HO}5;`4fyC(dEj!})J_-=RDiGw8l~KUbu`?}=Mj_s!+ARZr37@(145_tEDw=zZgurScyn)jSSNtbY3~RKKAK^!#(Lo%U(ueARhX`R$1fbzhz|LG_H9ukq}5Q~C3cRh|mhRsZmOJeLkszw7SncLKh1yM90AuM?<xmfg_zkBj@rZ}N}cC+wagzj812`!cUSkN=oX-<Q>Dr2PNU?>#(4PU!o%2SJJteRSS`KL%W@t@u`*G+(~Yzuro!KV2)$i|>Ay+@pH(^pVf~F??e=<?nIL^*xBsw~jp5_`e>h@%f^x{Hz=FJkzO!;v1Bf&wE<m`(B@Kw<)Rm6Gv-a{w^%P!7}A3GED2CL?K;QhaDQ92M_gqXs*2Secxy8S)uPSqjSpV`z&kS42@5s0Oe2EOxMf(G`x8h`NM6E8}Fa(>&e+)GhN^J1r$mqzt%ooSD`ifyf!k4`i+dyI@#Oppv%ATLUj(l>hv3PBC+~id)<8>Y!_Sc+?TDTIrV*RY)k#Nh<443&$p+Yb^RW|=UYSW>%RGNiN^WG+k@IiNwmL4T>Qh|w~xnheLrZ;e5Lp&^_AcEJ|Ew@U(+>@F@qk-FWOZ5g73lYLl2byZ8hb2el619_ug#jdJp6CJ*%c_zI@M<?{6s2>0^q2-B<Hi=eqJVpLoW9JgtRS<)7NG`Ks7I!r%8jH+pz(4@r4g{cb6*I(Z(pIz;Qb@^sR8E=j8VEA}hDy-n}^e80D;zE^q5zd7wc&UUFC$`hQ{HO}^>Evkq6l+E~9-PbCAmloQ0e7_d5dyRaa2RwIIsm>&;)o+dk8n-PywI5rpRKLF8$*@mjo-9(Hjw3W~Jil4f=POU3*Y*A_=JX8Jne`j>Te*Sa`~9r^`+8`6e4ls9j8Oir`E|eG+^~Nfru>OI=z4jt67w<CeO<iwwib6%e6z$_SIN>w`uo=T_VP!R)c4?(+AGhqmD<<8hH71%ZLa!xkNWw&TvTJ_FSk?Y%m<I^@7zH7QxtKnw~%c?%73(?t}90)?Uw}gl>b;CJ@+Qst?&0kiYngs`=4Ct6~D2t;zK)Y9C*(Y6P8o){GQ5cd0PFB&E{JF-rUy}e=e*1CB0m~W3+Q-(RDrkO5;;MIlrIDr0Z(4(e?Yrkc6p}r%W%`d*+bU$rb-f=X}iW>RJ!w5-7fHA=l^nm}_wqKfIsDf%k;o=o?W^Juio=PM-H-5?ylq&*xaz3(B+Roa0+{(x}d1dj9wPdq#PF@2+{|eXRGZy;1+;e8t%j<v%ah&OMr!32PJ|sNaKGFYf92A;VI~54pDNnllg6mu)Z_^M1Dcx9jA;OXK*Sy0aWV{O%n2<4SDw_kHKQH{}l1b9$ou{`1st^|iX*xFb|g<zMCV`6Xt>5XDz7p*(yph^ao%@nbq~bNaR8=34Lcf48sW2V|P!_%W3>IrVsxv{!!a3%=)S@7Aiyf32MIhh$U!rj>NP19m%kJm1z^x6jZ2{C>>$9$;lf_4{#*6CV&a)h6e^oA)u&`R{V<Rh>Pe*E;`uxqlr$By^bKe-Bdp_gf<U`}OXf<iv;X|2@)woULtP8vn00DSz{U@*j0@@&r`x7U@4eR{yo?_ikt9U(;Xy%xa3ilFRV}POsPXPA%YEuQe>YD}T)4kIr}oJa`u2=$7S*PyNh^x63|_@V_pr)+{I9DseKxzkYkteP_PH#~ye5nDaj<|H+ifzvF=Xf0)NBqc`jea{Y=u|Ay&lym`#6*|HK^sjN<I{eHr3O!LpD|MO4SLyP}k{e-<#slxxiKVjb+%d&p@)PANJ?ufR9JHlx`HFM2I6Y_UkI3e5;wc(cV5cGF=2)qjY16~DhLl48--~;F}_yBwmjf4-vJJ4TYqqE^1@OpGSydGYHj)0fI)6hZiH26ofAN(Uc4($n#gD0YW;fe56bRawxUW^Wh7sKn&AK-QHc60{39gaX(z($Y25%4+m5_}H6h+cs&!e`L4@ELdyx)0t1|APJu{{nYLJHnme9B3Li2fW|<@4DPiGyLPH)&czq-3R{!??KJl-NWC8KcX#R(+oGq8v-|n`=G1fKJYwr8$1vG4Ltz=25&(R!du|o=nmNEdU!Xy5nTdrgqNe!;N|c_^hbChJQp1Y&xIGD6X6B$GIT1u4Bmh)hBv@F(RJ`nI11ekN5MzY2-xU3_$YiDy$GL%kE3Vc<M1wY54;PWj{X8qheOfMa44J~%>n0!BP{8DOB}(voPhoaPk`I{t=G0_F}N+97tILgg_EIK;bd?Mv@o0k&W*N&bHk0$VQ?dO2)Y;^0xv>W!HeKE=wWybd=xzoAB8WXA7G<NV~H=qH_!~QX@>8kxnR=_KSguHrWt;Y=7dc%`~*!4n`ZbPniw|C@HO;bOKh6q3+OZW0(=hr3pRQdJ_kpm2jOUV1-cww0WU?D!AoHq9R=HPSF{V<6|Rleglog!poQRX;QVL~I6qtwEe0Fy09S-V(VyT@cnZ1)o&xVeKf=4<m#8^^U-Gx%MzN%Q;6`wFbROIto`C)aPk<MpTi`|TT68yTbR)bLUWzV<m%_8qh43sm44n&y!86eX@Ju)yT?U84YtRkw8hA6h6W$Da(J0spA3~49Mo+_s;Ar$X91U+mcfp(BN$7NV65I(5g*(9o(EM-#ILeZm^E8TPcpN$b9tXEZ+rmck!mZ)2(PZ$~aAGtCoET1m=7y8N+0aICHn<Kt1g--QLKne<;05R!cmcc?JqoXdkE0i1qc`B=@JaMOd=fs5K7~)iXVB;H8Tb_X1U?0yK<~jP;A7}D_!xWyy#OD9525E^qtWmo_*ZlV{42Z!T?#LON1`@767Ga{g*(CZ(Asc4xE%ToTn;Xd=7)>J-=Y;^qoMG(aCdYH+#Q~V?t-VmJJ6T#4)`Hz&bx>FZTLIR!0zyOa94B!+!Y>%E`o=_Q_!{WTF$j8G{a-iS@0Nm6dDGPf=8n>;nDD9G#s7`&qvq5^WoL#W_UHc74^bf;r-|#_z>sUewyKx=q7k2JQAG*kAyp*o!|~|UbFz57ml=~=KPAJ8U6ts2mb&!M_a>2zlNK`S<u9A7C1hd1db0UM6<yO;q+)7I6Yhg9R$~a2cQe!0q|UOEj$-qj~<7Oo`l!K8`0D7MtBo?2Hpg3Ku^IN;C1K;cpdy3dJO&zUX31sSHmmOL$J|b;gxVWx&#h~N1!9&5pYMe6WkH5h1P>>!4=SQa0R$DS{yD72ch4>M!Um7a8Gm^+!Ov8-2wj$Z$lr#+u+-%IbUw`x8W+BIbGo@aC>wZ+#Vi)PJyRzjtrm~{vI6#e-HOSN5ehfUg%`F7u+A65BG<MqO0Md@K|&!JQkjV?uYktUd*8x9*mBJ2g4y~2RH=Ij^>54!+%&(b6)&GGdu?U0UiT4Lz}}!v%t;Zv}k-dEgTz72*-xwqUqtda4NJ0oC>aj4uGq`ebKpaUw9U}9yYoWo(2DcZi0V-!_W<I7(5eQ2hW7(pufR$;Q8okcs{%kT?rcvhZn-b(Gl=)xE<ONZU<LGYr)mvvS<akEL;XH4VQr%ph2+Fo^S*Bd-P}cdw4dw4W12eMQ_7f;TY8H=NSGrT#-HA9<B(tK?lGC*tczHhFhUM;8t*Jv=`hOZin`V+reGXp>P+t8#)&52KPqiz;oE2y=jJ9pdoMzI5nCbP7NQhq-K8}pcx*Gj)6zRP0(hr(X?<AI5ip@P7PaVT<gF8497xK!Li`4&?@j(a3!=aTnX-t&Vr5p0{4ddpkZ(yxIa1*?hg+{=fDHu!RUN=Fgz4p2pb&^4~5&H?cg@B2dxHs;1XzAxCC4ZEd!T=8>0<iqu;}g;eP0BxF0+Z-3rfxH={A|X80;<_Rm%RHe8lH)dp_EJ}FBxTmfwjSAaceJJ<u)M!UeZ;f828xFH;j_J(`2AA)Iy6QHT#1hChVn*HFV86Jy{hR4E9(I&9b)NoTc4Qjz@;4jcv@E33#^eZ?HoD!`Br-Un`y<ww$;L31yv_D)O{tg`oe+M^22g42F7U)peXdAc%ToU!bCE)^S3Ag}U6fFf8h3lh@VWa)v`fx9F9^4C_fo_Ipz`vtc;osrws9B@e(F(9>hHs%B*fhfr(AuzRhF_o!Vbcu1M}y&D)}LY14DUs~me@4I<I%D3csLks3L8xW2g8}rFW^jYJTwj*4^DulgcHE&(8{pU>To(Z0R0XQfODY@;aqS*v;}OmBwP^Ai57r!!uimma6Y&$S|6^@`lw4Y+yk8f_kgFPzr)kvE$DUlI_qEy&G2^g0lXdFiN1h$!n@J;u+hEnZg?U(9-audLWAL8=Cu{ga3C5F4ulh-3E)KVmuNaT9rO1k&2Vxw7n~f<j246oGEbRlhO?vj;OuZ!v@Tqi`KU@W+zp)$cY~**Ti`8>`&63Y$>>gaGCT?04ew@rC(#UtpsnCmjAIDRa2_-foCi*dehGiccqOG7&VXiyGczt3Xokz9RpF{!e|ehW&gfKlD%aVWX1F~%37*6?v`6#6?cpM5QaC9!6+z3x<>|w4(5JJj)~EI@&2R~{3|s=vf@XrV!12-8aD4c+CH=<|n`ZbidJ}#O-$k#$cj3R$OYq<D9rQAM2Y!V92|t2gq5pwj!Es|rzlbF^&2VNkBb*s7j+TOp!&T9ma8<YtS`V%R*GHSc_2I^7Gq^F_0Bs64fa{_`a1e7@mu9#;&2SO41Y88phGv1Y!70)Ba7s8HYUVW_e;ba4K88&*{0{Ff{0@GD{tdr@-=cTmx3GEWy2HHsK9CrWgT8`IGn@i7^O}NYI4hbN&I%Vsi^GNCa%fe!99#*l16P8pq4nWva1FFETm!C-Hh`<cmC?FzUFNbf&2S-_;e2QjI3N5qnhpLMPLHO9)5EFIcyKB>IT{O24ktm)ye8pq!->#0uxW<BMBl=u8BT_pc}+$${1qAp{t8ZqrhwDI0cch@0M3IJhV#G$(Q<G>xF}i)E((8xR)fEROQJR4l5lCXI$RnqhE|3vGnd6^h6B-ja6aZQ5KRxKXPyGl<ZyE4BM?mlCt}<K(PVHk#y1d62d85k1JOKi9>yyWEeaQ9TmsROa7nJ;@V!s%{-+j$-i3|chK=5Wjs682y#X7&1{=K$8$AyjJqa5<0UJF98@&J<y$Tz>4jcUwHhL2_`ZsL!4t$5}jA2d#x&HRtht2&ssCKL`QpNs1{a+aW_n-OgqviTPH2&ZJOZU%4{r}6TPq{w-h%~5nT=QJ{=|jaA&dY}V=53MnzW^}8d=v'

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
