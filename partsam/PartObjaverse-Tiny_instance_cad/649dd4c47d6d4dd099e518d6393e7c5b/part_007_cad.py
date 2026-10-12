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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/649dd4c47d6d4dd099e518d6393e7c5b/part_007.stl', 'relative_path': '649dd4c47d6d4dd099e518d6393e7c5b/part_007.stl', 'source_sha256': 'fd6e453a6ca167be620b1888ec7587159adb7f2068d28b5addc7c5fd4d3fb3d9', 'input_faces': 950, 'input_vertices': 506, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08092279732227325, -0.18441301584243774, -0.07614491879940033], [0.1983792632818222, 0.14556223154067993, 0.16235968470573425]]}
GEOMETRY_BASE85 = 'c$}r22T&AQ`0X2Wj)<tJW6o>NY0Lq0&W;FXQNf6*4VZNem=#CGhzTPKYAb@QBA8Y&tz%qsUeg->bH8)?fm`oYy?W28ug-4{mrM8U8^502cAhCyxoY@VNb4U{`sSPRnx-O?=BkbL@f$t3zmNZKz9T2NXxYS9|4d!hrgQ6d-CeY?+QbsxKK}jvO4PEHs578OiL#aw14j6b_Uq@{cZ8p}kMf)L8|Lrh^!*3*8|mZxT(W9~YGo~zOO>@uw){W-%iz2OYtJJGPb&RXK1QjrxZB41O6OG*U(5If{(;;F#1GxMUq0VI93@(7+h*lkOT7w{&v%zb%kR~?GE(_k`)K%ke9wq}7$f!QzCQb;+?V%;_|f~eNd4~n_R954X({z<(|*p7@*$1(sLy&p#3`lrE-4R6{hIG?Dc82zS^2$nF_BWw(G{WM-&rX2Yd>22F4x)K6aJ@!V^Th>_jd7LUD+x1=Xol=_O(C!Yt_Wpc5adDx90GY`n8w_JEZ(!w@A^&N9B5qJZHA!b1CudhqvN7d$->v^|UFD`d5t(lKQW_*ed0N8j7#)e<Z%K?~3?FyRUM;T0$QAyViLBE%MnCaX{+#YY{5#(>Sa6db^Qm|5;1c%jejyo8|NJ?1$uY?*WIT{xALEhrE;Pbkr^)_3I_RY?5-_QydrFrNJM#e<Rwtmi%4q=!CUW&%aAI;_uYL^UAzrxqSZnSg`13kHgY#W<8-5#5W@9%kwg}6g?&Flc%WoTE9Hf@AOXNgT+tXQ|?16Y~VS1O<E{FA6Rakd>*q4&!_p1JyL#3v9(g~yHI&v`u3El-@0~<lzZbN{l&66&0+CfyjF>ywy^Y5>-Z}B#lM#dez|bzkCt6G!sPm`?^a5^GtWvpSaVI4exhx>E56q0Y#7>m!!{}ZBp&4>vz(TC++P^tzuSU#^6iZNuwus;(Mt=&*CH}Y|I)sB$oSHWWQG4@9Ll?U_>1O#wM=yFL0sqWTOy?V&!g~Xwvu|RK`C)xK^5Vb*o)`;@vK~r)@|ET`MfM#d}D7Yu5&}?rMRDHsmCa5$bD(iJ>)rP=SQJmta`pr{FC?Q<GC2pzii7Zp`Ck`gkKB&&XQ^fu4nM$dE%F9jea#Rew6rIH_VmKO$r>5e*VK7*O@PHw)lI7%l&F=`iG0}b3RZ$S05_RNn3Vl6UxWH?;VMLa_x7NUo#Q@^W!oPS%Q1P512bs+F|1}882Gk=GEf&SUE#JcMOs7VZHDT&plmN`0t8gzPxv7y7=~t@Vlh8OS}19LAwntHC;YWyCMBkE9Q>*>tyIO(H0kF92@KZIfm=8i?3gp6)xKN@>=+HrbzkD(+;5jEnhBLsTBN1J1|cSIDz{b<UbkXtE{w-J>tVI@!i`7VBGphJ+@gTWPZ?^hffgS*G<Y9c_(lG#dq(D=i1F<k?5X{<1s!5$+)z}UdHpa6o>!dhx}bf%Q*OJPK^`4>`tr)$KI_I|MRl3;vYV>TmEkSjJTc(SJB_2D#-Y<Jb!i)_f;2uru*`|^=)ep{NmS}Cf9FW{U`coOjbYfL#N0%(W>{GC%V7sDDf*Lpq>@ikBIL&c!c=>)Rp@+N|eHVr?dNtzdpOvYt3b_o&AQ({m+e&@vi&yl=VQfI)-9AYPh~Ozu`H$w;3Y-qj;37*lnr!SN9E;&zH+%e5FW4{fX}eO1+EoVmvJR7v-x&55VsalKQQaqIZg)sj?6Letj9o#*8}{A9Lcp#lJaT<`=DDptQF(DK-28J!IXo_(mKR-&Uu;__nVy4;gn0qaF68=qvt_jM9&F*UK0$nS%S^xqHd{s~10l`MmLhuHsuh21tJ>^BvE(?AOlXw;7A;h+uy({fAwp9_!z}7)PsiwG{u$Y`H$8t%mE-bJP^SP$g*}<JoXL_r+_fiXRfPTCV>>J6Sh1YnE!zRLA9h*A>KiJ+gEQ+(-UtqVX5dZjLss<bF!}%X*}*EgT~C?h5ZAKiB+Zow0pQkMUb!L|^><xg+pgJ>c(m>nHWRK8$_Pzwzjg9maWy_VLF2bq4z)t<rq>D-tnZ-2I92vE>Ge?mD_y#>K!3xG%R3LqxYWmVRabQVZkda`R!L%R5W|c097;`5vC&E7w!Kzl<+Oh6AYoNf`EVO9o)v>U(4#rR6V#dD``{)bGgB0Q(}xO+V4s-dHbF<T#G|s5M%ipOFsxwELr@#IN;sJjT5{#$8}e)MIp>AX<1R`tkaG@H5VVAGCUdwEx+M8|3qtRue_je>f`bQ|cA=2aar$rQTI;ST}POgMVh^6trKisY-3>5-=aycEAt0F6)#ry|i6EZ-|FKF~2--hg)S_Pu1qqKa9SIWIng$czRm?UdC>+Z`Gcsk^b!{zYXPkOqwO-hm6JikZ<B?{M~<Mi*_6?{loe?w>%$xT9!HDw;Cw-tMw>yLOvI)Ggma_dhBm@hi?_#VTZ5Ru*rR$)1<tf{RRAa1F^2xNh9Mzj~tBo?@cUxW7%TSl<VMM&L+>#ejpO#qSzt$2Or??K0JVN+GFK>^q=)|KF|&Z%6hM7T(nU9SL;tm|7=<j?bG>#_}aUMGG2_R3)ts;uZ#60WVe*J4$q19*%1N%S)(OVf10dvzt$(kalMOIVgImxmM*_nY&zz}qI+<j={i=Pqc!w2{DfCB?u_~k&_1=_imx9|6(RLB8ZUp(y0zXiDc|xt_Sx6Rtq|?mMtpt4Fu7kn?F4BjJ+v#zPfpw={iIO>>hJjgzSR}`#sl}TpTA=X!t;uier>P20_Tpx9mUrtxXHS2OTP~7UG}4_^ZKaovM<uCB?IO2qTF&_+N~}ar@aH@IavpEf&XI-&L7_fkNU;GSWw2PCBj3VzqQp9`1$fkdE>!7xqfSbe^!cLd@}lR_r|*T{Y$Kp&uQ{wy>#m-<4G&yChLH{EKKGTy=FGKej}nV)`y7sxS!6?&@O}R@IBti{TroIWB#5rc#YJP+m7{a(?Imw%wxsZ8vl#+C3ujm3&yFn@cpM@T^Vr=?LT)O*4tx?q(3+YyUTp2$4A1?-AJCF<F`xld)6!(`t`_nG9E3*k7E6;nht*Rx8mz@@Qv^J;K%HdbE<Z#v5W^}LM`$2=>h2XJ|owQ|Lr5n$L+*9X;B=W_rjF&bFDz2?6)lo*2{g{Pu#`&8Mz17!TH&m{~rAEd&RdG+#i8<IE;DGI<txNx4^k_zt&APF`vEdBl`-Y`(NT435V<$|M_uFoL>U-_Q+WHQC+3q8t2DKdm1Ir!N1~#=W;QZ^f!w=y|l0Px)9d2py60|-sFH^r!dZ`(~qH_=?&n236OK5rC>3f6WzALkK2rW%ew^mY^j)A)(In5G|uCBc49wBUw?ZF`|5wT;ym~HH>{(bGU7btu~V+c(ykZE_j`?bID535C-m@Ol)pY-&c#}jf%2Se?M}iE+9B(QKKh%qyZ-G4>hWEJ{Xlp}$uC$IJx2L#x5mizZd{3V{9SL%bBSxP4rbqbM*3Z^$>JO1n#uXys2nT4UO5u`vmXZ9qw8CFu7>deeuuAE@5+^zb;<f5a|p(x1^I*?XK>CRomYJQ!%ewgYxQ+fzokt%l>Zrv@p$nE@(<a%qkKRL<TpZgVf^=OgZt<+5A*z_&T_srp7(%X^%&;u?~i1Cw`3W;1^00g^Z(Kq@f{m<l%JOp`>L?z=trv)QT}is=JU^!WxluM$$<53V`b^z_DhEBTO4=jFHMQ{yM7esujTO9c9Zd}&+<n<bbSf`$1a&?90liM-K&-c=k@h@aL(GKMJ4yOy)Q6-CVuf!>R8`?8=t$Bw+=0J8rKzu@_p{gbJ2IEk$J+%^9RbeNR;xHgjsSQw(lQMe$Q|jPxeuT&<<ZUoVUg=mT_%M(^kfX<#!kOXK;?SREKY!(;fcDvzY$_)62SO%m{?v=LqsE*DJ{W&GL1*_<Hl#GTx1ei89`;TZ7@>yddMp-XgW!mo-Dk4ymVFE}Xj`9F%&DAxGgymc{&UOO*YMzUd77w{v7%>t2>6av$$5h_8RzCjCKsd>Mc5&qS0j+f4EkdZ@qjb4UKW@Z+z^__g=_j`?u!bND-Xj`MCW`y^{%Y3vt$UC@pVJ7WKlqM7)54sVQ$%~8_NZ96?te)Lqyw`m<Wqn}rs1mEI=bIhbqm?!7WKt1J~qCdwY4`3_30)De*$ah}(j&(EYAnJM2Mb=%t>kEwk6u04r96^4o$r8-_Yu=-tRI{<J&FU!YqoZ^g>_3|JM!xRSFzgR+w#R<I(>3Jb?xjcj<mim@eiLOsW83qm^cRO$AC%AW8Tq6}XRsb-_zXXAEb=6rw~YtE7*||3wY&r6xmcF{0iW$)giMltXYE-A=eH}7l1FlQ43YDw#k1M&<l|RwodfIVgMs4f5fjlL#=6LJwT#$~d|ugb+(*CLGOjIg<M!gY#LGUw@Q#rCwRPVI|EUMo?`@l~-UaQ4|D>PXzxDDC<cBvNh98Ukk)_j4jHA)d;O8ER>p40D*Y8pe=g2(wFuwBrF8$eZx+46_I_62&y0VY4`c{K~x-j-L3zlM@S>yx1N(*U6{YZ21E${rWues75^Jkk;=pXZ!puA%S`ooz!(jTlI!SMIF;e1~`TJG0=X*c}Ur7#}tyJTIq#fPE(!%=dbHs5{Nx70g=@}3_tKlWIT^WDyC@MrsAeC0hQ`x(cpbeOLfS05_B->8W6XWO$}@MAjSoYkm3=C|yH;Ri$^k5O|kuCr<}_*XrVU-XKV{;$s~iF4!KI?@jM&j9HM_QEYtzI{g7_u4{VW1leA6aI%4IM;m`E$weB(2n&tL>|l~Smr~UUkCVp?a=>&UST~QKOBC;rkE#J^ul?j&lp_K-Uy6q?tiRnXQ6z)FyvRgZsYm>m<@k-w2UKTVhZdtw=RJHyu9QOje*7BzuF8x;T-1Gfa!8xHA?S*U#b_@oi4pb%I_6;1V3vh<Y}J=V;|=G3VvEI@hwlgBY(5>1N`uVxc=MNFWU;1LqB#Ii*>eZA?&k)%ftUI82gGT4P-xW-&a$7y?uSGU;CS2Kl`OV{OtkQ5B$h3d2{1&Q`FPE2FCk@9#{wGwPGG25!XFsknFFF%Y#u*j@EMh)<25l-28qT{2Jl%+#QwNWnH#UJBE5ry~K5H_=xlRmg6X2@jTYwV*_zs&+;Dr)SZ~GT=pXWFzFloX+aq8!{fy_#@0igu2&(<KR34GoR-cL`L$I&@jl{Af;?x3ALco2YHy6IshzQ2*B=JIK74D6E|_PQV_vZq*oOU>TRzz@>qlqdJ)6gV__jf^PqQyu4c~hT-lNr?BF{~~y#e{t63elFdvsRLht|*=_`46rVjuhP`~s<G|6lO+W0I#dv<KMFU%Q9v=~6`YpALPc{9PlTE6)AgSLhw>i_yO=;#)`f$UfFFZ2|VNZ##&u7s-zC@M(<9lh$oss3&U%?8o-BMF0Oe68`<VGA`_AC(HHNI{L$}bwK75Tc0@WgQksvzx|=?zb)=M)~RZN@a_9#p0VG)i*edL7=Ef2m=80Ll6J6F4ud~zJJu1)6wJe&9IQVG^WONX$OAlj0pE3t?AL7Jb#Z^8DRIuMG92#@-&c^oYv14wpYx$LOBDLW-X*yIf2+xOwEepf=d3S>P~P~f58AD{%&Qi!=kPD@#QPV|D%jV&@sxb0ZtR!+o25i<oXf}0K_1lHH?|po^=<-v?i;ODeNaAlKKuc*C4Z<D&WiQj*Z|*1jr~}MDKcIyAs68ndx`fl(_0~*S^6gYrjM{rSu?LeJyp=|VY#tycS(VHplMb3h4PAT2}_B3ns{Pg^PjwdzOX&YJ7TbI*7lM5t*JV~_i~jyl78SJ*5Ac*P|wC4a-F){UF3;#A4d6*iPG-29@XWub>>O<nY^(dYaJ)gU7uvdd3$D7nMd?Xy^wEu+$tR7p%nK2e9vf2I|=36X;{C@BcHF|IR-yAP~LCY%U;1eaO)!K=@W_k%ZnT`&MZqD@INg1CC_hM|Au<pHsHSeV^00z=lBcnq1Q~qxc2@D|NeFv7nTjkb6Xc?Lf*IYTkLzY)v`%{yx0l;?bgUEgdwkG&C^qSJ$56`1MU6geCvqwNBOPok@u((EO}Vl^u_S?w~}Aio5Y4B_w@m;Qjan2E!ydiT`2!44X*QHoV1T)`+oSDKH&Yxh$yW4&!gctzc1%G3&*=L=`#G4gJoPhs@yvHi|<zm>qh;XSl=J!$38UbIo7Z7O%{pvu8#iLF&*+4DKT$r4F<svzb@q+^|~Ps6Ep(;x2Nc@hqojD748RL@Bh0zFVFMHUmTtTzv)Z7FJ5ppNbdX63S3X7)$%^kc0UBy{YMD=bQ#6B->)g39SyI;_pT}Hm#uL#tjiwHQ2)Fr^y_?E<y>a@=LO2gH^DybRE*@Etu0=|ztIeNMLnD3_w>2%QBOk)*2gdXq<-7Wukcg2;JtApcX__XjH;M7?`^@)Uth-ldb%h4&)?CG+)wH+hrr)i6Zz91ye~GYj)L!78F`!BxA5~O^Wj&TBkxu1TdSk}A11;-7>D!woeVe+jd=t=?z{A7!_8ghF=O=;_}Vrpuk9Oy@~P6{`gYAn{;|PS**_UeD!?z?L*5_hek0{PWc%3yzBS$|*YmN8^k=)vO87HB%lNWidw{(D$0O*!H!ey)u@C$v=N+To3HbHuVqDy)gmYQKIn*<!^k})xC0EfOK3rh_xUTFIjNb7Wmw`7?{={5-|0BUJ`C04s_o)9tU(Bm(IX|4sg!O01H0dX{tjF=(dgXy1l3nsIy3t|BFMbhs%ro1{qTblTcs|!7PRezLE|l?VRBi}=l^^ye*}|9M{zjpmCR-#=u6xbI-;Iofe{o?y<y(st4g1Bn)RA+iKI8ztKeIKC*V9YJsjYM*=9lFO@E2HQKX1LeN_=Ze<T<pZ-DO>~KZ?M)H~1#}{-MYx7TAXQ*Yhr}KVdz-Pg3LB>EyoVk%&BC+p%~qYwoe#cH?_A%fhfuy?TIpmUTt_@7`lv#OK5NoTbbwP97r9!Dvzle(U}+k6E71!#cjdH2hh^un$?AQTnl?U={ck!sLCm)vYDY!GmhyIUD!!J)+JXFi(5fP~Lp6SK@%IcNS}Zl%Mbd-}`#E2mQ)z6Y}We%F1{#W{2Z`w(UVZTYCm!yj{kAYReh;-v(gZ9lIgdYYoVQb7uKeIM<}{o+<TQt_OeFd)de9sdJzm#x{XJwvL=Dbnh(q{*qsN_(87HZk91+WZc<uc*E~q0(p!B+t5#r4T9g{HolLOZXx#55#!)b_QyK;AWGh+SW-=aUuzTA*&%pepdDL?eQSpe@_i@0b4ytVY`3@K=LZkTbF$qXDC5Ji<S_g?Z_y6+$@_lsyLrie#(wQj?3)uW!~a$j`_X{KQr=eR2K=JSFuu!;ka^qwO~d{mz!&@X?T2w6g;HUEn&Uq7^#$z1Lo=fM?fv+k+NJ9<-#Qj%hF{<Z-mAJ-mOQL=e>V6#x8wT4TxI;)8s|X0kvjGtb4DVc`qd5PyGP^uYxCWX{o;oW#rRy|f&Jn_chvLOYOI^5*5JKJL4Lm>5A(tuaPBbbx4`G-2`E4GskE#0dPn%K)v=B@d@1*<yL5*CEVaz<wp2fHj``jbe(^gp|5(?jLp#*%%kM+Qp`LDi@V$q+L*T!dgLyE=G34=D48!%;Xoc_pRF1`aLI2?>|8HHKOXDsh|2twd%8wX^?;X7zBmLR_ZUXPKrR2jb@1J9T-yi_~m;`*kYjP;Y_0;3=+fKpxU|Sc|v*|qiVf`_#tEI*K^xz8ooP#7EV(m6eer{~M2LBfFy;{jq6GdZg&>tZ4n6|Kj<i+$X4*0QFoQvDd!{5o|!te2|!1p1(pT>D9I0c?llMl!Tn&-8AX;FT81+4FN+DU)2ccOpdy|lA!L|$nR$D^F^i`+tfWBMVCLn9yjacgj{{Wrg;y;M#3uGugTRG5Qxq+LDu4~`+<lD`PfBd<Hck4Y5Y@ozZhvA_Gl|Ite3O-Dj%<by^IhhL&1+A;dEw2v`$I{f<UP=A#T=qE?!!tZz+`-vfCkQZFPitC~)+W%@8%KwXfy*B43=E+^ihg%!GLVF&ahkc9xQsmF({)C^}2flYhoZIr`#(tu0YP{#-_oj@qQ}ABBa(#S1a~sar`i5;Nf4!EhclIgwP`<)Jtb3CZ@V+|?-&3_djzT>{D#&{;d*QWMPk;Lpe!w~TzKU(q8$6%U-}rrpt9Z|tr!Cg~d#Ulh<>_7QGy7b`{^d{)<Y{v0SdV!9)@HrnH@}W{`|D3RA35eCucOD+!1tQNQ=^^xCBh%t4&UpW&`+M5t@d;H<*#9V^c*ey*9aai`3x<51oC5%Sig);e(>iHMPB7gLAie0qq*=Kw}pSHIrh`{cOs9nDhA(=%~u@#aW&ri>E&W@oi|cp{w^JfdX}xna~!Zx@^415_wdVhfZuEFB=G}RM2mj<fqYbGPyF4j(c<eVt6`u2Dh~OCm-nLa9CH5RTh~{Pk@A^`%liVmo*w!9^v%WBbmYynNg3t)YI-?O_`UcZC)G%NkL_Vw)Kkev?$_#FAJ5nHr?iy%jqGliH^RP&ZykCM?>(>KeVN6(+*$Gcb4tI}4n2_XeHw0k#5erA;eM?;@)ghbqx_)T{JwW9jQ6Np@CWwBd*RhZan1_w8!PqH{)BPyGCRJ1&~%mf`k4WEUcoz%H-A&+57BWQ@crrnHks!wy{n3^eJ(2f(>^N`*7wQYDBt3E^#AhP{qkQ6WL}bUZn|=srXs!OstxFu>^~Jyrut{<|NcJ}7+mH5>OU2zS+&Cd?|&+g-^F?KafUy22HBr{nR<(Snf#dgg8Z2Ll=_bRl>D6fp8TAApZbJ+pL~XTm3)Rgh@p70GZs*<QLmD(kzY}tkYABMQs0w5lK-K;BmYBwOMO9pOLkCiksah9>I`xaxfr!D`G5vJL@i8Kp*WnHpR7Xh38%(r&|Lhi{9FvhHmX0_Mm|ivOg>D$PJK+iPX3Gfl>8U@F7-M2F8NRDee$2=mDDrjmE_jcLFCrt+ziD9sgubC$;FfPgW?RuWt>rtx`MiZyn=k2dX0RW{D%69{D%C6`jPyF{E7Mx`4jmA^)2}W`61Ooen{R#4I*zMm!K9SoBc+yho&YOO><``PD4#iPD4&XO-oKePDRa5PDRc{ElSQrE<g<+7a)&!Mg;XFHGq7Qe1@TT7PTmO7P$;HJGl(mjhdG1M$SS_P0m8jNKH@9NX|y}AZH_&aK>n=7uAF8MQ%fNCm*2JqPml7k#kbhkaLn#Qd5vqk~L~7E$N?P7iuQ53ppLN0685wFLgXQFL^|==QM($_?U+AqO=S(f~-Puaq3AeX{;$ONIjz^jZMYo_*Hy?Kc7XuKwd&ELta9zNOdDuB<G=KA?G2xQZtfW$vLRm$T`UQs3pkx$TgDngBlFQb2QAiN>5NnlTVPtsa{&rT&?&JwGG+qH;O}@?Q_Z*m#B&4OXNEY#rK@?h<byXNWMXiqMjm0k=HR4ucC&MSCOYV!<#yV8cLo*UPHY^UPCshcgP0$3PbVV)O+N=$<LDA+cSpZ*UorAy-9sUzDYhuy+J-l-b0Nd?;+2nt|L#PE~Bm^FC)*Qt|HGOkEc!}k0*Ce){cssQEOAZ$+gK=hGI|Z6tX9|Gj$EQGuek~kbTHws8`5i$TJv<Z&Cjy-y*-HJ|n**zoWh;zazg-_MF}`6q|cDrDv%R$Y;qLsW-_R$y2H4$WzIqsC&qx$UUiZ$vw$!lRe|M48>iX(Z?CRow0<Wcqv2iLTVRs7yj--hT<*MW#ld75b7*)2zfPiJb5*FG_^a~>^GwsirYA&EVU4|8MzQSFSRx~FF6I(N=`ve%}|_?>PgN>&Q9%2&Q5lx`jFkp1*l`l1;~Y|=HAylYZP-y+7p|5WOM&)?xD>+^-GteJ+|VvRC9lB?$OOXySbk?_w?o--`xM3X8`j|V4fGuGlSX#n)^fZjA5QT%(KQY>RIwIatG>0atCr#>Qr)5avka@avgGIYEN=ya%pN?a%plUY8P@Pa&>BNveG`}>g1}<C{OK3?L+QJo=#mto=(;oinlWqM^KlNl`bSlkWW*$kWZ6is3GJS@)7E4@)7cE>S(gkHss~hzSK5kb6oXhC>~6$LRMOhJeWL!`Wsnkd$Q90<PqeV&gkKciO%Rsok^a_GF=&p8&TVn8<9&=e<PP9f71|(HG0)tk~WKqU8q&aF618?Lh&bRS+deXWEG0vQuC5kD1M<K6hEY<AgfS(i<+9OLh)5<MzRXUan$T&6^c(&-N`BxAEy=|t56(HHP6)Mx!OEun`dzI9KK&eBtLVRXEF0UW}eT?vzvK-GtYD8S<gK0ndd+AY-pYj&GVvpmNd_kpQ*3NpIws9q)N@Rs(D^D&#&g$);!;;^KLnpq;s%&{x$dZ=GocIrI>qr#TM!?vW4tH?LhV*yHcByUCEiLb;y~?si>97smR|oXlb$v#b2qF$SM?np;jj=tx8s*_??zC$0=5!_`QZu{EvoET!dvil8cb*Q>T-a>SU$9<oe_$48<*}Bgrkv?WkkPJ*WZHvE%^qZieEm48@zNBgvb|d#S!;Uta58>UQ#8@^NYe`8YY2dYT+dzCev3Umzz?kB}3{C#bW@C&;^8lIH7O48?Y8U$WA{WThj>cJemrO!7AJ4(dem4)T7s=YF>Fe)<8_9^|fSj&(+VhT_`Pg5=udl02W5<ax9tee--;Fxi<@aenG=<ox7v)UM=m<WA1$N9{rFO721SruHX$lcz8gPomZ)Pa+SdmLv}*H%oSJ%@~T+8ND<$7c~z#7dbQ4m7JNJftrJyft;10I5#yvIXAgDwH&!PxhAy}xh8o~vbGz<P&~#N1E`&;{m7lk&8a=e&B>lrZ?Y$OBy|dTxifs7v6ecDyq3IyI+8q+zq^5<cn5V7c?WqXL-AJXVDeV-YHBm`YVs0lMJ*{0qj+Yr=c+h>T9jIvT$G%hnv0yBoR*rIoR*xLnt_~}oSvFhOUl(LEk?~sE=I0E%}uUAZbvOnZb$Z`)+GCpXHy4}XOkCG$B-A3=W0p)W-deV0%xpp#xiFNV<_%PT|i#I@;w=f8&Erw8<1O2o0D6Rn^HZ=P06jPBgslfk(K(ATa&vm6c1r2p1@EXOkGY6CjY@u9L-RCj=Gk7j(m~2fvj`~`6Brqbtm~A`3XbuZR%F?ZSpnhYVtMmdFm4Kd2$qWCfV%kQ4BMWZRS7C9JiVGHgnx(F5JwMo4Il`cW&m@&D^?~Yd7=oW-i{$&6|09Gk0(1@{{NJJ+!1efAZY4QZMR%^Vt5>Vq|~v3~B}P3~~^)9XW`+h3ZG%LJp(OCWn!aQWuktk|U{e$&ut(>H=~s`3iLz`3gCax{91gzC&F}{)@Vsx{|z`yoRAzcgA{WOn1g)XY`_Wr%oq#CwHLg<PPMP)Rp9x<c8E$WTnH%4as$>J;`;+m8lKLmC5y~Ey(rBjj2t^jmcJOYqFKxirR(TirkwzgsgNTxi{HHokq5i`%tHn`;dDvrm|hvQ`b?alGl;#)M;cpc@uRac@ud%bqHDM1hUd#@^<oN>L29GWb=%m_&qgROFBm=HqRG|zfjL<N#_y8U#S<#O7Ce&=NiS|sZX?|bC6>5tfV+I^|qFDwo>d$y{09d#T0u`&ud9%H^mlel$LbXQ(T<--}gRcT$1L*<nLR}cSz=YCG%a9`L4-)4`sfKGT%*^@2$*tSLVAc^F5dOuFHjLz87=RlHQjoHQ%FYTGIP9rODsBxob)9-IBkjYojH-r!(K{?WZ2nlHT)~xdO%E)c?NsIZpN0l5!D>Pg7@TNx2Kfanv9!Dc7O+Ds_vNlp9feiyEdS<x&(sq#o6haxaQsP$RXZT#e$l)L1PkpQHE_^@^61|55ydny4k^jufkWlF~b5bDlMGO^VgS`bK?BRsLg!VuQMyY>-2!YsgA<veM~frR&N2ob`wCJlEFwxrsA6I^%;giaNd58bWa%7ic|l9&%%6Y;=~{=8UuaUG+PcsAtJ%Sw?X;=kK&~Mlf{|S?N)7Fgcofk{nI`gSwOa2l)^~@f>O(S!qA=9I_Wfab1SuS`5WC7>au_6i=WAk|&VYQg@Qqk`Gc(l27v94l)$4XDA*=T|^#7Zcc4QZca|eP@JBjI2*MaIUCuHp?D}m@d0Wu`2abd8cmL7yT>yW$59WF<H(WJIpj$4?^G}H@8p3D#SN)-$vK@-(HTEAXhX6J#VHwz(^Bh_(~>h$YmqaNvruc0vyihg6jz}3B3B@HqD~-pBKt8EFQ%>~FD7rG9wZ-RKiI%fJdZk#JdZq_p|}CHIk^Ej12rA_nFf7CO-ELt*g;KCR+^2hLh*H~8(D?o8yZ6KUFv5ItU~b{hT?ynk;Vm@gZi2LnZKWdp|})7@et}z@(^-3^#ECEJUN_vks3$7NIp-EB%dcAqyA1lMxM`5Jb*foth6C{0J#OVBDn>*CPQ&PYEE)KavDZXw$mH7-$$zQKT?0v@8*oM&KS#3T%Dn~Jhc?LJh>jV3b`J6ICUUd={)jq@*;-fJq*RWoDoW0NS#MsNcN!)B>RvnQLB(Ekqc2vkxTJ@3NaKHp>`t|Ay;E4Udm9snL3udnY@>w_y|LBAhkL<kldGAp4^w*h@rSWwH~=1+p#@E@i^)t@;LGe>K^h6@<E2;=M2RU7>fU-?jrw5PDu8g6sta_`q6#rEAoBvO@`u^)TiW^<i8n;<EaVcc=A4KC|T)3@;>tK48=pKKIEa~s?<v4s$>hb5ZOX5Of5oIT8&(oT!*@pT!%cLq4+TM6!|9gKJ`?xb~~jd&4G&VQkQB;^Q2-mkGAu4N#UCE|Mb6HPx`0cRcOEb57__vo4<bjI{9z@RzXYpGIl%9)ao4IJQ$>qWY{QmYSsP+i|VJ6'

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
