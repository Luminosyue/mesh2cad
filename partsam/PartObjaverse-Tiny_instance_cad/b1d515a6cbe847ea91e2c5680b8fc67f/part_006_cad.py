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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_006.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_006.stl', 'source_sha256': 'a8bd027d2a0afb912d6872928c35762d7e6af599bd8403f9f98014d644a7ab5c', 'input_faces': 545, 'input_vertices': 340, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-3.013502836227417, -0.003064662218093872, -3.3409128189086914], [2.667782783508301, 13.745270729064941, 2.9487366676330566]]}
GEOMETRY_BASE85 = 'c$}qM2UJx@x1NilC^jr8u^mtW8yLHQ=2#I?qgWH8xfYBi#ug1GQI9dvSfa6E%dgjpCH4X_mSe}RDE4ygz1N84&HnbjPyV;wTkEa&_}BjT%y;JO*|TStIde^m*eqEKD*g*p@9+5^avDkz<x&OJ;P?UG_UsxzFzlOtLmVm}aQgG`Db3q7Yw?*w4OTydbc-L@bwEgj5fatCW=I7iq<h~1-wx>f&6j-#bc-jvQRlA*#%p|FkIwz#bw9L9)k+nNDrGAeLyiCAUrtgbsi=>wx#6E!+9aLEeZKt@!ZU_uCtNl5Dg*q~+q>H|bC2u_+&$oRDZ;Jh34ebAelQ#GI$a^hYO)IBjfCOA)p0+Tf7SOfjW-9M_hx(q<e2@dKZ2a<eY4u&tuU{v)uOi~$BsLdg>ZY)2FP*Ox$uT?_0|`-t2oPX-}>V%$#JFp?gjZHynq|gYu;eq#-)H8rNhfYpTu9U67FtVoX01vWxValr5OKnh9cY<k`fBM;`AqktM8WqS3g9Q!@RRvT!fx`CIh!#=f`;K(8_bL=icVP-HC%)&X97OX}qgL6mWZQFx&a4@f++gGl<70CkDd~N4IZ-p8lubW1ht3(9`+(qsx&0<2=S|Z)g1{C#-`VuGIi;q$GtvpDOboV0@4QZg%X2dF}Xh*Pu`DC-1<|rSU#S7QTjg%bf>qMZbhT?!-P=uk-UX;AY8S;AV9A4b1C5jpd9==JCrq>?7QG+MRJ@46nCR1Nec<FAH#I-5YGTfl2TOSO0O?f1~Fi;CAi+=;<8(18~*tKJ+vi&4=GO-+c$%S=I;Zb$T^DiT<-*z};2bK#tLQ^J~~4M;DgAU^VNLHh(78`+G?qKm0T3uObTE#CZDz{LZ$jW8a;rJ5NFW^iP2sE$*_Mkm$?kJDTwLstSIn>`__pUOjgP<WKH~@kZP@-p6dq81M9Z5bQR*7{<Fx{RrGjO2NFAJMA9kEqw1a>@X<`>va`8_yYQWe-5}cw>EIQ^|nW_`=C9*jeavQuQN308Qwp(na6ic;P~3=gr6I|=KwdSt>N*d^F4+C&l$*aE{%shoyn(PV!v8F`Um>^<>h!U6T29C7P<gjm5F9Q9G8mx;H+^RxS0{j;}2YS<NdQyEGO&*&%5Lz^l?QczXCqa5Bp+WuKO5r78e0-`RBuUbJ@O!u)`WJ;O3bEhzomQaf~;N<1b;4T4y+qRcLq?_P^c_xLWOko$YykHzEJ4yDz|db%vhKz*4ZMd($7lRZc&)L*p$9`<dW|U0u_g0e8JUkG$kg8Opf%HQS-pbm-@*(4X;@mpI=0Z9~3t*RKTJYFL`*{p9j1=sEZ!;AW>LY@efX{~&MFEXZ;?By;|}7zO`xw^hLH=5sjTe!uKC_IK8kr_g`gAoi2ci#%WNfxwNLt4?FSf}d@~`cHic+^SQuJmg=x{{-^?)d0Br@7e7CE$6YGOE%-VIixJ-fj)^?uk&H-6SkX;b(x)idk+041ORs)zn6;sncZ%Vw^-h{=>_h={}w&ofOS6iXT0ig$Z?gnd7lP9!u~jGEoD2r=$^x-`LiBjyzvjWu>P$ZkjIRQPT=OO82E`XF(=FE*#WqbEicRIHyicR`A=KMy;cNaA73S8!#ZYEXZhEja-62VzmIi(`{W^yZ@}a0m%w=Y*Do1Qt&F%;efy1p9_b|+4{ib6ZjyW&_}ybH?|cv5$03VRPgR?a$OqQ=oj#Bo-FOG^*=IP;j=kXh4Seo}{n>X6xa+|0?_h^gY9r?9c!cYAiy`l+Z${+Vhk3KvT>l$PgM7<x0pi8{F#x#zwmRq4KhoI$qi){Dd%xdyV7|uv_hOzMM}WIteZzXpx;PW#CLRQC)yV0Mbw$iQiFjX_0^G<l2)HY)rj2<Axfu7}iTr5$<V=J7n=M)X-UeAAr^EX-SXcSHJig9Yt_vg9@wwuQ9IR(pBHO2KlYdyht+%jV*A8CqiL&c4F0lu2XP;&8XQM<c)@yHz0d8j`puQRxjpLa2h97Wq-CfQz6|*4^=mZJe$ms*Waxdrz+<7?}`NndHKOEW2azf_<H(GV(dXfGGpJy`K0e6i%z;%4=I-DEKZ=c@)J|!Ibndw8%a=fhqZZCX|`HV(8Azw9*25v;x;&nZWhJDP#5sY6-f&JB!gA1YGk_s$;rpf-6e&`CXs~C^JIELf8sfoPge0}^n#s_xcdKMLN9^+kW8Bbh~{W1#wb_sDmZwhd${}cF$6&AZ6{r%&Bt6eKFUioH0UNY7X;qe<Mz~8LumEb?l{kw2pa0kuH4f(ZZv7TPXu0qbJF34lfwF@|(o^%0sou15faQtqruWd?P!Sfak`J8!T^)uK%I6vp7=unn3z7XQydT{sx-t+Cpbth+T<UJ!a?L7Qvtc&gWX7vobzxA(kn0El%$E>>x=SH)A{5j6sOR-)nJ?CnSdszgyb=C#kRlK?z`<a}IeKx<@#Pg1rf%V!2yPV~HoC^CGgX<%&y92i%uQ=ak!@QPz#9qvIbQN&>L1p9zS8%Iz$UiWF^U#6w*&%<;T*x=NZb`@Z9c|!mu85N?cXB9j=j&)b_XhmL`C$Iw6WEvF82GufUit~}BYl8dt&(#=&wNE8-~968G02}g;y(IbKSCdO_-5edyp@PwW8_*suOy})h5Yb5oR@xG#C~_m2JQ^q&30ZM&-3P;3fwq&9`>{+#hk*r*YyLgR)4|!6>t=J(tNb_2=p8`hv$um=kxTgsfRIsK@axN=fnSm{Zr>1f<D$49KVH*A^yxUbq-?u!Yp2}|5@t@#s>~QfPJp~9)4(7y~=s|StQ~>t=I<pt5fH&k7k%R=jp{8`25i9HphLZ%c-pYFg`zgvl{1K*Wn=GcEnE1t3umNz<PS$!Ty^AF7SD^^-Rob?Oh7ocswHra<fe5`G=PP?!3?d^E!V`<?n&`x_dCMBOK%H!Y0O>Gtce9JU*v5@8uosunE7u0Jv*m1m?Bl&*MDc>h#49*sb3?=%I`|J7J%scEDZc9IpFMeffLvOxEof-+43STa`BDB>C3)lG`x8eJT0gxrFn8ePSK*y34mD>}5svW_v~D`UUHqI+Wu&au}bJx?h_Fdw&)M-0Gi>dTdp$vkCsVXcXeknzS9~2iN+<EzmcnL|)kI%sA93yP_ZJm@#v59_VvoHvCYv58eeiQ;z|+B0BPZTwV^`-kO{7hu5}1pU?_>Ajdz$7x>(hT$hvI?P0(EfzPEgy%2Y1#;yIZYxXG^uM##5hn}$o4?#|1WIl{r5smL+`@m)3t}HhE+)R1N=kNBn;HR!;<FGF4FNN<!m74u1^gq~?^W^xq$dj%j=YU(ACiD6H&3)7_yH{n{!@2G-{KHwRGS7RtD%+{w&seuvu?FY2*EvzItk4Dg-FI_4>WlHD8P~}UA9H-|`-jil<5~eXPA=m(^&Q6FhiNY0=9IQL2bzCZM%_`4hP)3I^Kf1|dhjCp@r^l8OnQ&JWaYby??H2C0&w%zN{)x_a}Q$NgrUHVIR4&rCoc5Ddwz+?TUL+xtpBrLxW06`30(D`3%^%p;eoK*_qTyN2gGt*UwI2ZcaDrheN)A}`8>0V{a3xZiM-{m6U_UO)^91~udTv);@w;9i|f>IK5v}p09>8kjrejld<Hw41^NJYUFeB(pw(;DZgBfI9-r}&>ydAn>pV~GGqC^06&Ct&LlB3~4b6e8MJ13w4gbQdcdt{7f6aN%xv>}D!&EH8-(kB>aK3KT2kUTEYR`T>l+TT3#(V6adr4p5uKZ`%ujY)$`Nt@B3Anl+2tD0NLolyBx)<Na%<9PT*l!f_uRHb}aC_iL#Fv@mME-IG_~V>nUy8*!$LwO>g&sa9E@1xLk?;q#<}$uVjNq~GBlAW%<Og%cAwF+C%Lcouv1buqR$wBp>tG7|^@#jjUvB2Q%X;|XKEPG}8;-|@Ght^}+E~6PsGg7YdEE;4b#~ZB;CA6YoR@}1;`_n6zX`a}K9%d8S>z7J9eT#{6Y}!9AKXM;RYQyOd7;`%^j)>P@%R@t7$0?!&kwJB@crogv<`50xhaSj>)}6$Cp+ypkKaD!9m_8ST&>TKeRf{%iuJk+`5nW1?vWh#PsbvEx}!VscVoF7jJG+)ag^GK&m$in2Ciy%VL$YKiu_{l^y2%fVhQZ$F{N;CU`;It+)OOR`|DQ$`r8S;86W)@{7PjXg#2jUzRB_9)jkMvO7-OLyXh~1+uc%utD^gX8+S%vf1LfFB3{(B%`;&4*ww(zgc^R(^T93nhy5e~_hk0cJ)D;wHstT_90|bPxkh2%)#bDl_|L~XfGhhSuAApqa^9<dpT{Tc!g$w<bMPnYaTxNGUC@{1cvoEsdp3;*ZhdutzqjYt;X1u{9&q=^kNG^mvpauh*I3K<UW*Lq?`--C_juNfC%|2&9&#Rg{VnIq%L_Q4#(jnTwQpBtIV+a}cNY)i`-;<T@g1!S+y?ISUk*KO@3W{k=KL(YKl^9%`R7`3)Khm%A>b-cCElO2wQxSOngsy2?(N~aU$!*ryK8V~zUQd@70&<ar(5$O_veAY-TUPpEMp|jMRw;gjJM-@;fyKD_eygTdEPVI;fLnoVtl>|oeSK2n!)jPdphD*-I~Yx6dB2N^I<NocRNorKC}s+mm*7YJ$(?2I8*tG_QXErDS~@T)iH_j^<G}s-y6g6zUxdfa96!a@Ml&17UIFI^a8k9V-4(YZGOyk?#Bq$>+LG+uS)oY{XF7x&Nuc0zR$do1M?a^b^|vK{lVYS5uLcc&hCo+G*Y85uj}Ly)H%E3Lg20z4fwln<tF&2eX2b2h~4Z6*O&Z1v;ITt19v`2;yf_GOY*}Q;8v5`{QYt>9`{J*+28owA6GR8<To+7{(e6XxO?Ii*hl%N90s0iIm_8`nD=+|R@|SOZ!$Qqy;;NeCxs)iPD>w1Fn`!?w%e$goUi{C#NYGrP1p`ovT^(*E&*=-Rsi}~>qAfvjJkVy{EjhPciK20$JOT?aQE9gT<3=xu$y%=iSH@bWxU|`T0$RZt}DQe4Q;V5>$*4ci1EOIdvRyZaO8Ov|0TXl?bbew5BrYomR^JJ1*&`n+?{nf+vm;({_ZZh7P#uO8uM5?`(gjA*85n_+Twhk2v1&%_lF<n`}n<^`JN=X>mB$>TZQ{4S9}8e+5W61&U@~bS@>Sce+u8DKC8DG{bwV9J9o81{jtV;#Oo|GntvBs&%eL8me)ex9=-$IxZf6e)tJ(c^Zvqvz}>Sx<#_M>hV>rwg5?|=#d#y+{R7zH7lk_DjLOS(#MsK`tPWwo?U;Hz?|}gJ+njayzWG2f^fv=@a~)be0l2&TMd;&Nvg8E&-*%QiqYmGntmXT5wfHgLqqlv+_do5j@p-c66CS^N8tkdg7w7xLS`oNkcN>BHyF=CiY|pxFfZG#Iz8A6|Z$e&r<;~~oe2t;M`DrzLH@btm19$G(5B=5CJh(S7mX2n5wP$kO322%IJ<m;MIpv=6K9)%5{9AYq%USk-e^;1!fb0FYk9hpZ^?d&8)&}2WYV>0s|C+zc?BJo$+no3exH0i}z6ZGTnEgEB4RE^?->bXkjN<#)BH_G07sB{=fz{(DpntD9e-}2`&)->X_wc^=?aKA+=mxHjVI%RqX1`y|awfdy@1Wg75Pz=lKN<gW0o!xdkONrP!PUUsN0#w-;=>_)F8wnVxY?#H|IRXb6wWR7y^E|*FLMdx-0{M9xHB<;?`?fru>G_0y_V6w4xf|mtPg_xxFr5PXo8dD-wfh=@++yZgM0Z{9zQ9Z&olKt;(N02hpcyaJoIsg$MXG7^*s0;#@rjpd9Kd_-mjLGfjcKI=HE?zI?HwUyBPl6ChalD(Y9L~FrVWEa8>g;=jG}CT=#ExK|Z!l7vwz9dp2<An=*(S^A`V(Y0L`5?{RjnrhHCuXRtps55jrHh#UaiZRW!{-C8;u_1q}@2aoSGmhHb~IP#m3yn^LN+kDQSz8CV{A*+C^!&_LtiC4kh_pYIyyMJoRa-1{x_s}*c5x4F_mHD1wUkINkx76f%zAuG;FD_J+$BiGs=iNr{_?+|gaMTfJ>np%rfpUHr+?0RkJKF&J>ALtA-=B24#`(*!j=yJqZo>7k`C85|UE6V8Q7hO!(+A^TST#7v_2YR%{ynAIX}(`>#P?I~h5UP&x%emetu?0|pSL3TcU$xOEr&m8@o)b+p<tsTC31bF6j2UUP<8K|>7OPLNPiyw-~ZEuo>l)>|1_am)oTCWf0_`Zb?BjKmL?xf<uzp$qPD-LLYf?!@(EYcP9%5LbVb_4$#&f|mDbcuIQ646<<KujYf4qjpDJ#Ds@ttJH4q*n?QHs4IZbth$Yg{C>SvWT)e=tqqMDBDXA3mV6Hfhen(Ap9qA6B5^#^Int*NS}V#28(qA9N?`ZpWC!l|D}Q%Oy<&7s1npG#9~O*J(|N}G5WO=C1|(e#&a>QB-1Qqw>5zJuGu4NX;LJ>kNu${L$!YOX2P!M2K({wDqILrwLiP5iOujWuQ0R9raqYiJ_>^(Ge=PW>F3W^0;B`ylk4U~yVrX-yvskCS<GicS|5^9X4-)$}h-gN0LnE^+<5g{Bh1D@mKyPV3GlZQ|#}mhCmw5?)j6T0r(Bf2O^mc95p(vUee}k3q6Gv_}=CO}wb4rJ8=0{TL(rvs7$A>%J^R?UkCEi@$jMhWZJbvS_NL$xBn1aOxM<>j>3UPB`@oXxglwy;d9tIV27UYp6Izz7bA+ikBDie7*1&@_s4B@n;C9KE-HnO*7Poc<v#6ieZZ7D$*uihV<7u6xVcLF{gf*gJXHErm4cIPjTHqaXeNQPJN0?iZhD2`O+qSSQ90S08M3u@;extBfb$Me2(}D*_?cd@<^0$>Qj!PTtdD%T{!I(`4ah7OHIv$Hx)l^A-SZbaOzWjqr67G?;|{i_-B2Q5iJ~j#rZ2(<`0&+N#BQ}^F!%VE~DH;IjXp{J@GeP)^<hsbkSc-1V2*3y#&i9?>dBMkvT{&Ps~%F^vx>od&&B|WNk5`gGVQiy(1)kqlB7d$}MqXuQ=&byyp-*_z2G-wpf?RN2W@DlH&XrsOe+jo_tBU_)o>T`A_LzSDf!^NWQBf`LDc#bLA?<xsy2cCo0aJH#HS;aGN;gP|CTKd+RH16aPwaZVy+S=fkCMDy{`i#dX0c{a+R5`vAo`KS25=6vu$aH@69=nCT||ktozm_LyuHC3YiTUfT3WahOlqS*2f2_S;i$%c&1OMRC?c+C5}1Y5&RhW=Wek<&<WUU#bZA_%+2sBL~;lmcm=fK8J}9gh{`F<aNq_l-pN|-;n=)C;J~Kocf<ipM1kpS3J)>^~Ouuo_t9@O}<@2+Qcb;QoSO7r8?47IQ6Nfcw+8f!l~{xmAdDte@&&n#7V93)SNh}Wu6*VT6lAb0je8RV}gWJ-&gjY{HCxFwaY55Ayl7QOPe^=6UzCu93Sd;sN}zi;*ar)+r%keDEEG%DOfo5t2;QSQoW&CGfz0>R#UORMris{IQ6McP`>|7xTkJVjivKMQ6Z|cgwa|kmzNS=Sk_ffKdbHF`c+P1lCbBB<8YmD>Qfw2{iM3RRN614PwzyEtVoezIyhh47dg*`Q=jUCr*0gUKGhRLQxQ#m!l_U7i)u@t*f>Bq*_qA&bRMWDyt%YJ_G%!!x3t%b&3=_Oamr6IqPHnLM&f6i=<8Vr^(ha~S%c0hwS?%rK^WEZ3X1D)1?ktOH8{AQd+Iv%OF5WRUMwt}`Y$rAKR|e(v@3|b`a&NI=JBT@LZ3)prE?RVhv+PnQ+R&y$Eo6zQ>9O5lB$jmXPI)D@-(e2Qhhl4Qa@DohW03*w2Ax6ep1f&oXe?C=c0n5PafeprS0*{Lh8ergW8niDA&!9Hu24}m$avz?*(d8uB14o-0v$yZOZ8st5heZs1N7$*0TRp3l^vkwTiGRvR|cyd-5y!Jk=rcd(T;)`cbmyp0ih!?0uNzS5KT5mp<7#QEZ>6KAZ>1pQ%Pw6;6HfXG7{<xWu#PyJ4Q_KS=mISx2b&hNnhGO24q|O99~?zw^|;f<gh}bF{vjvPMsBz9}}Gs6Nzb>VGBnE}=fuQBNJFwV3KdJ@(Y$lH#Y~vc4kHubnAAN@dC`MI{dmQ=E6QN!#=NKyAwB`K3)cAxPTf`xT{4Iee+KDc3faHszxE(xyD4M82m^43l|&miBykf0*b}RK_nA{iyB9anuf!{54GGtS)#(S;H{Vy{NSF>9MCZFC_e=w39VIsOhfaHt|cEE@*OV+9yQqy_!yF+O6r7aO&@ozOCtuaL@Bx6swx@2&cZErXWo|g84|_UsG0j{zfsUelZ8j+$}l~ZI^lI-K(PCRq2zQSMt7RKI*@bcdyF(SEWzyX4hl9HTgQYO+2@z_lo&D;l9$|BX-#<?Y*L(!@=@A_H)SkcIoz6!FLI#_v`3q4K>x()L1z6X&<~DAM~RB15HO|zg7$F5UiRWQ^CRVstG4q4`h#C3HQjLwRmZItC+IOdP!!A=(t)q&5@?q7Vo6}PS)ck?>$pY9-CE@`9p-LT~XHaR($M|_*-`I$&KQd#5YLWCzJ2w5nGZ?@91Y+HT^A|`cGt?r(~~BWm@+}8M`6VJJcrKo@9DIMD)BXc77oIsI)1L3W=>NNSka;vesxy7rE)8|535u3E_LB?Jeu^749v*T1RAlB-AhyM)E!qo-XZYvM+~(-pl^bT6W4hcS=7)blWPrdY)06)|`=P9QA8v^2>@sjRp6_a6#dI5~pONT$$GMK=$B}=(S8JP5dlP{3u1}toYm#8J8mM6!FL9nvQ8YqG^S+3EQvfwx$Epz9D^jeoMw5k@huB3+4Ug!l}PV_+m{-(oPbb<lWQsNZOA?{yy1PPn_(NJ*N1$pgzPr^~rC^C(np~zL9oT$tfOR$Rj@fPITEX>sl;4N!Ia5)^bnyBaxR+@+NWWpBAiGrhJ-D{I{6oiy+~}1o!m)g@;JnUt*7PCvksywq5#v3-{z#iaT5S+vWL2(aBRQ>`WNNTC(i<64~>EvPX;L*&=!7X(x%VEE2v%>~u(;B}sdk;Iwbgr2R~uk)KdLdMoX>nQTls?zX(=B{BC%o>TvpjHmVr(d&}vd`aX{oKalml{ljq$}92IP}&sJYh+AKd6rk6e<bZSA}g<8>C*15c~?!p2vK{qraqcRY5G<;^?%YdL6fEFN8!|;rs)SwziS#RochCs{t)aB>5tIVQPby|J`+y;PMZ2_YAaY<>Gzazy)+FJPW?8S<W3Xrl6HU5Z=_I9!TQR(1BLgMxu?lE&pXpZRx3?kXlf@!?GBncYx-KAx03c3qR%w3!&qsPjRs`0nI*aqHeT@Wg^!o<O*A#qR9D)>qeX`fvLAh<-A~g{O_ODhCQE;urk3(v3*jwAUW-_VSHUd*(|_jr;m>l=|7ZS>UjOTx|NawH<~QePS^xQiREt<|x?fUW`hT?e>-2@J{sV|(r_%'

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
