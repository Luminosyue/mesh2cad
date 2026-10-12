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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_020.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_020.stl', 'source_sha256': '97138a60924fa03884e59dd9981158a12a2bded5e79639a4c2680c12b8759df2', 'input_faces': 1180, 'input_vertices': 712, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.12221763283014297, -0.24206319451332092, -0.49835169315338135], [0.08519243448972702, -0.048115551471710205, -0.16965746879577637]]}
GEOMETRY_BASE85 = 'c$}r32Y3|K*TyHINEJ{(5RnCqbd)Aa(M3h1N)aTXZGeOxG=wf;DS~teHPof|7JAbKq$KnbikR$LP_TmpNV19FE$^Mop1tAup6~PjoacS#H|L%?b9ZKTW_QECU8_8KOB(XOipH@q)tlSjHw+#{jFQIii0GL9y(5O!iu!C+kWpN4{-4r$Z9BDT7aC*?H^x-%6EU=RbmfM&%8eu6s$9cXIdVvJOmuiu&mqx$A~^pre9+Jc#)tL`|15$nS7}hYP7Pb#sx@q5ZU4vr3b7Vk8(Mtx4ew=q#6hn1&*z@w>RcZrxPAQRg4+g9JS%kly{|?7*zN~p{%n!&UOQ88=h$I_I|j8E`HnU91^0U5z7@-ZXZvwgUvb--ntu82sQZ50>3sX3l{;5w9Tojd+jLmei<p`y>aE%<`S|{R`(<0T>8O7{^Uhj%PCt?xt5*5td!y3)xavo7musqDzR|B~l9fBB1Rb_=yKAuIlTRKJ+9y=>?_SydsQ*0Uby?Zeuf98CSE7|0)3zP9a@UHYe)+C`U6ZU_^`p44BISsjhhbvBoP(E({c<l)JYucmj7(0na<yH`?PEuY{@sK6$~sFs3GR+d7Tb6CEPqCfTiQg{Sv_sD*v`#f*LB=+Baa_<u1MIV%U4|GyO$L8>(kaZOU}=de17}o4qtP|%8j}5^-<g#pDg!tc0R#fJyK2!jZc*GJ~>gmjz;7``MSg(JnUEB(esRzyW?&hwQ_s>Cck`VuVg>2`cd4rINU!!e1RWV^%Zw5I41j>_XFzOkbGV<!QHb<Ab-&rxxILC92ghF+(Nq#7W?a+Gxwn1dC_g4;LbT?<@s|dLF7BbZk>{K+xz9ayKg#e<+h96+*a<GU0)u5#z}G9J2JefTAsdA%UzG_>iMGwDLQVXIraSEyMlXX6_xzb9yt%)YRmp-74+Y)uCL4fXQheb-kGp^yV&l{_SbdXeWR4%wpl6iJh{+P&O_)HF>l_Pmk(I$8{LPTwsO~{eQqmv&O9i%(QD=|vAvs3uj{z?Mu;DGy6SA!<twi8Z8O3pzjQ!s*U{so>}PtY?B~BZa-K8(PSx`C?OJX;X{zUs4K25&%}CMaKWrtqYkD*7JW#IoOL006l&gHl>N@guY1#FHI6qrwr0Te<-IDLc>p88U_IRLN9S`<CfA1IiXQrs*ERdb5<L>gyMSa_}dxE?2car%TcT%-HeVvwjA2-tTN0}))ZcCf4=MP&8?w)#nzdWAX;=GQR=gZ`xf_w8-ykI>}0(klkEjOMt({k^l{90~LTbQEd4?D~AeRA49v7Fsd9zU4{JX)S{O4K(d-xAz8PM-Jfn9tAaxcBqj=d9d_U4B59uei#$Pm0)QJ>OlS@!~pQn-nhlxwih8l^c^f`Q^LAJbv7MZS65D_f9A)`^+jJx0hMQqvaXN^1Pc+RB-o{^78&Frp<XBcSI-4>+yuNy`tabAH{Z^pO%o@9e-YM`y6?n;vQP_ypDUL)6QABb6olXUB2Qf-!=Z|Uh6y<p~J*>o#XfVaeLTdKd$;TLWlZsd$RYKHQzpdliY6Jv$Btj|5CL)-7UD&Im)lTyK8xI{M(%2f;+B$ChLEiby95K*<Cw7l&k$!oX!vBD&ID){9fJbNV$3)ZLvS>5p}Lc%Rak4b6Os+$&!=n80G3Z<{o=qaCe?XvcJqi9xcyElGo3%dj+@q66F1KW^Ip-J2U>0=i}G~g463f<?6bvIK9qOuJY|;Dr)OfPV;Gf%FXxR(P_K=j?XU5Px<j1amTIPKKjmX-TYH-zK@Ll!LPnEbml2Pj{1rlqi+fB$cz>9?9FWI(eezRJpM=am)i|~U%Za?%oja6?#Q?;&x;YY{rWMw)IDY8wp-sHw{l}dDgXHi9p%SWzT)oTL4vz(Wee`;d|IAg!xki1xhw3d%#WEVxHG7j=+l{5*`wpGjJtAwW5N@x^JaA3FYCvICdlKsihREHb@k}DJ+rjn&gisV);hMZW1=6|XX6F8r$3a>X}*CT9d~Ai$UdWrN^TsK*UilL^gJU-Ugx6<?y{cm=JlL#bsg{yPTVQ-=yjWL^STWlaNQ={ye<t2)z+t+=F|F=t9<9^y0XsC<zyd&<m*DYZC?8KR_<;(M!ugl9^}z+mG2l>TW<HiNs{|Ic(gpTIC#~ay7QNE^SNMP*`2!Ai*ogPxvyQ>A&xh4y`o%Qe-x+JE6UCL|H~PoKl_se`T0fGJdchWzBckYaQVS@T|bnY*H7?(>nGu6{>A9+y7{DB&8PG1gl%FuJ51g;`0)Bto>@)qS5h^}AI}&2<;Ys5<#u0Zxxe2gY!P|c@5tA~H%!kn>&olHktO1D3gfXup6^-PwcP28l;`!qLYs8Q1Lf*?Fb>3R)SX|HoA(vq0rwSzo9E-cN|NKg(a4(O(Q@Ahvj08DHwgadJ+WWzto>T<@(q#mwrBGOUH_D;eiWzuQ*K@#66$Qw%_rsN`L*-Pdfo9xxjNpA9bxNr$3Nxf{Rw!${R!bJ-@Cn~tdsSJ{2ViDjz`DU`RLdZy-wE;<>qrPIPHgW^L}R2gSEQ(q1?PbSzk?XS6Y5~-N;V#=(yK6UY@6}gw<j{eLLm*Y}RT$_w|(L(aH{j+tYp%pU2s<uWGrGHBItmajV33|NSaaZubj$JTIvvxcA|A^7BpK2-#=Fzg=Q|=MZ`PE!&n0ubpD$?%k8*=b;0?_UO2oAOD@?nQ`*IH*2d$%YA+2>%RDkOLsg|ZeAZ2b#Up<FUrm919-sofpC@Ye(lZ*U46=FKCMr=+0QF?mh1MHa<#v%(#cCioy-}S&-ET1cldhwaqq*MIDW2Zxsf$h^5@gyb;m#D>iBmQ%NMUb9|<?lNAQ62k#O_<x<LI!y84vUd|ID!^LkaF)FS`+l*eZP_x1DRYToSGH?`cBHCvw7d7CZN%_rsN^<+q7ob^2New!@o|MBV^?Quf5d7NBoF-v#cQf_|!08Wov%FX-a#7#5&=WVk`%kjRic+PQnUC*;-%Io~`#A&+zDOdd{PWz|a?Eg^WSGxJ6T+OF*Yr!x5&abSs9xcapTk)Lzy{P3z)?|7AP`u+v-El&>d7K2#i_x7Il$-aN-~soggq!b!N$Upa>Qheh13rf*+&u42hV&QvW4<qJ^ys+5*GJCV?U=q|9`Sx;T->bXUQf*wD_7@{YsF!Yj+^;ALi)(p<vX0$DIOhn`G(3qw}tf9y<U`?_ffC43KMyFUv_5y?9p+zZ<OSY&Xq(Tcz?HNU(#}QziJ#A(DYp+=l;Q-wNlF+zHXBL7uNS(&GApU`953Z_CU_f`<bj$9vyf4VkIx%bqMDH@5_Xn?}Ok0@5_Xn_q|*G9ImTRInAf_DL3=C4<5mJ!1uX?o8RYx2YjDPxXL#UZ5yqff5Oe{Pg2csV!P&jvb;_Pa9>M#J@F0yQf$|JPT8a7=JR8g<Zfph`90yOQ<wet*r^9}+;CMB^WeHs^12^ivU;PH8$k^w3qChO{!Zca{mVM;I(5O1+h^35-?yLn<cf~l&eZnf&MEoi_uEOwwcMNN^5gCa$@2T*b2YB&xbtj5Kkke@c0kv^;sO1~Zj#5_`Gr??+<rdBf4igR?$_<F;&gxQqejW^(=KLT)p7TQ+kV^_CclTF^P_mc{KT}7-}77^cumKhmp=02_RnhX)y=2kbUxif$_nnfa`Bpu8&|ga^MOHobn~e=olpC~d*bs{`?V&?I_|#uq8~T<CMW3TQ*k<<&d8(k^VH;3$vSRNj`iog*6q^Gr{Z)z)%&dTM&au^Zrr%*U%&gXox1r{oX)3_Fm1bTeiRRwpN-YF>h@Rhfc;%@Ws|Od#Z~|I;2V<T^A@jfl1Iz&dA_s6qG@8g<a$E6Iv*9M*AvRs`K36$o=~pN7scuIgmQKKn{~+bgz|v?$@PSCb^M##CD#+m>HgB|3FYeeH|LpLPbd$VA96jRTpj=BcFFaGayp;%dP2E6{!LD<CzR9qq}LP5)%jx11G%11PUn+ePbgRCm&wWXgmOBc^m;<MIv>qC<a$Cmolkl_p*&!I$n}Ksfc+)c6Uxo&VW|<*#p_7!XG~7+XB4ORGbX3^GcWF+A-MW{J8O$a#~r@jlCPK^$9c}@>d{*6%zQ)gO=A{_KGo;*S@Bw~zOOO1mRl$|y`Lo9{2X{ob;<F4fz#LDqviNM(Y~|XB5|D4&#?(NKgR|S_#B&X^L~5(?ZvwKl+*lx`+351^2^1GI_mqKtXUo{_cfRMd-!&|ZayhDpN~%bzEo@%-<KJ_)*da-EG*}_aL_WbU3`D%xY9|>T~Ge~-pbYYcivTz9vwIHPd8dF_>-I1-!DBn?#!$p_xEhM71rZQeI7`;GxHT$=Tg^|qEGXC+a`LB@7Z0yFK`L2zW?<_c(fe-c<-mJ(w)C1C+Dx?^!znBIe%>rLRJe-?jI;u@4t%E`v=O^`>Epe{(*A!{-`*;f1q5w-<fsD{R8Cz{ge9#%GLXwxm|MqKsnuCdjCMVdcQO0ncP269xy-T{(*A!erIl%+&@rG=ab$)P_EwZOiu0}D5vvD?;j{v?~mp@koyP9>3q`r2g=p^smaOx1Lbr+>HP!c>iyTOL+&3ar}IhgA1Du)A9DXddBFaX`v=O+`-gwq$U5qGFZh0(a$9Bz`Tg3%ZL$u2Z{x_Uq~*?xALZ|e9@SqX>d@yG!p-}C@POwR!p-}6@POwR!p-}0@POwR!p-|_Rfj&m5FXG!eSRU_yx&&arOz*f)BO#2ej(hv-&XTXpI-<Mm>>H5Lb!Rqt+q>_UkIo38Swl<xOu;=IDLL0oX%&!^9$kT{kfV4`usvTozH;h7sAc^dBy4T3*mG=1D;<9H=kcr9s2x2IGxXc=NG~Q=7&DN5FW6<^!bHwv;W7#<m*U3k5!z09t$4ud932({>S@xrsU-FZOYZ>)r!;4w<$M2-_Go`R`f}qM+i6XpEDx_SHHKkWtQ^jxcXhUE$h7C0l&K=-29ync);)O2sfV>vYV~rJm+_$jXXN;&Uh@Z=f=Kux_&4(>w^b8zYuPIKO0<Yy>31!SMzDlyHD_d-<1(=exH~xTX6ID$(c1gI&S`sG=HrPV!QbLvo|BJN5_qflYaRD-&YcDeqRY5@O>rWW`3d48@2Tbr}+W(2{(UdSa{Y(-F#ARe&1L07s>IvdUuBW`x?r<>4)U;Q~cB>!SOk#E%P~#mS<d&^Z7#T7V)~6fA^8cqvaXLWPX|Lf~&tDac11pa##9hE%!dQYq|RSCd%z;b5eBN_OQL+Muo_2oU6aPab$Q>b=;Zm(sK9XH}(9{BW-<K+GH&^9)2jl|E&<UO?Q4#Zhn3eI#O`;cT7gqlT;mdOk5<M$L$sW65KG>$nhEJsXA^?U#jKCgR}DYz2E`Y8N$u$40ynGhH&%uOUc=StH1wp?|PW3<F<YC<$hIayIssD{(jAw@ms2vr*G79^><qV{82`VjvHxH^c=6F@k$TDz1a?Y{viMEjB@pNmqy5i?YjA--29#zJm7n3!gGEP)^>;PxT4&=Zdc6~T>br~J>$Dn9e1S1Yq{%jEj@qqXNrz{ACA#-_rDG0-zSzVyi**9L3iZ!Cw*$FjvEiYmd9tQ>VgOS-idH^ophCIF1YtUm#mXMBUQ(}_m9Zqt#n_xU3#4-+`P_%2VCa~H-A4?=C-yz<upIw_hy8f`DM%P(#;R$=KNG_v|D%lP;MSSm3j(J@9QX6_i2jL`#Q>1zN6BJ-MaIIa`Sgt-~qqOBHYY>^>=-J!fAd$eZtMpr9-Ok(ak62=HHK0zqnV{@&9{C%GKXLDo+1il5&yX&hKB}m{n%;%1aFlgGWK5q!Afz`KLEH<o_wv|I-`&>;13(>5ba8-+JT!_it|$n#p@$F%>!y{wwGN=tTIhpfjLx@H60NLg&FxL*8`gM0lPv3wc~;!%x7NIOr@(z1bK)8#TCZ$)X*LccBg8-+{gjZ3zDkv<38I_!jUjq3z)9$ZHC12+wm`A&+Zo__s0UV`wW&z1A4t8a23Y7tGePXbWuv-wt{Zx*z@ki+#x5hy0JRzAac=@O`Lr5IJf*_f6Qg`61XC`WF0f7Q<M?K!?IFU@@P?T<9G5NEUrr^n><?FT>(_7B4`bgU`o;|9dZm;qzj-CW{&@UWdK`Uy;RYENt+VvHU8Fsw_g_t6;epi&89}g_eXb$|66DXW)xqIR^a>hxUgb4nGXq7rrm%MEOW8H%7lrpl`r8fo}k<0p9@rEoe>nD%iiO(8};t;X|Mm;X~kGh1%es!QAG9&yVFInEOKTMX_8MJ|FZM_~$XF&q1HHyp|>LI+w&;mqC=mxKbFy{c=MdLrbA^;g>^~L6^Yun2+`IF-GOiMIP5V@Uw#q<4YEEpp)UhX0eCGQRr^?$;jIS-EHx+u{;~OyHRU0>P<#2_cK|HXE6&p0saV!oh%MRcfe0T-cINai=T<*naJINS`$!j0&=;Z&SET!8PHhxLoBwkI0)SWAB()L&@C1}9m~^^y9KpkQ7;y`+)rV_-pGuvprhgUvDnCBFLVR^Xyk2#Zm{?%Se}C14X8C5^+qF?`-v=uv6uuM4xhkcEsI^yHSoicw-&m_;wNHxB68QD)^OAtj$H1?vG|;Y6B-S_orR0VHt0(DXymz|D=mH;md7D?C2B>ZUNmyKAH!lWi!Y#2@S9mIW3dUk6g~=h%b-gwehik!Aa^NhMWJ34a=9PDVjzo=&_VF)SuA0(4jK<X2zg7O@fJS<%Oj8*k6MFJZxC|1AIhRXix}tt_|+^HvseXP1U~?Ii=m4wekhiQB6ksL4M4pC$mM<ri@q#AgZ6`8!D1nc<<JH2{gAg1y1?RxV0j2~7ob)@)a!>_?$cQO$>I_8FZkEkd-KaILZId0|3V&TT+0XN_%tkY4Z)a4sQDVk@?7rIng5$b2J|2JYHXd2MOA18_<xYc8P^KIIX)fBT&rSC25MHrSf0y$HRfxvs06jaSA<r8+Tbfft3qqSSB0+ztp)!I@?M47;CW7U<Z-P5UjbukLaSTq)xh`~sKI?c76n-ZLH{$PH^8#7%sKZ4SYBv>AnAD&K)nK}#eFdH@<9KC=Q;V2$MqR_o)e7q!C0s2J%c{D=7CRP@dJxw=vDY@&@0fZ@YkT<L%s0d!>2%hfWMBs8_=upJSP=-Ts`ntFvbf_wbb)qyazS7-^Jo6i*3*?@LQpqp<Cd$LU%%s!0&|L1w9JC9eF#TTi|(40`j=-hTn`aN1zFodb=@xH)?SIg~30QVb=rbVE7@>LD0eQL!e`z<KV}@e*tyEe~!Fp=wNuBGZuMVW8nv3%sA*+OTAc(k3|jcOYv(AixSXc@Wr9eLW{u{hn9rC1YZ)q6tq12bI5xhS`41&ltv!c7vP`8n3tfXE%jc&_!m%v`!E*lG27?{?F#=g+qaht>A8l1cST-#Luxrg`Y_~$Ld(Iwj2h*QoblW@WcneCH=*_5>qF~8>%rHDz71^#|2BL>=!ftPkoOj}9z4%!ggmZ|;p<{dGiW1Ay~Y^d7&W*b#ID_+vFHcw1>YAM4($cs7dj9+1b!g=An0fC{gF2S+6$iN3`QQ;DEM%U83G+_sTYOuQK-TF4i>vvY=Lfo-wa(3-2lHCx*eJTza4%DbT|A~<ZXj)faf_ok;iox{CbQ@fbO)^+lBGFP=ov5*)jAti#yPt;D3hx2>l8EXXtOxzu<p^{~h`_{4dD+75WoA&-nv+T>pgs5o7*>{$Z*2C&vGY8r+{`k;vj3=wbM;p@*P{;lGA{3q1q>E&NGnBD@=U$DoJddCn>1aXk%x2xHDbPg&}n#`x2yA$n!6!3h?Jp?l#ELH9uS!XJWu4LuJ3HT*Zw6YxincNDr8p69rc$MqQe9*j8-bzABk!}w#U!F>eVhu(ajf~B4emi`orZ&~y)r1mnTKZ(3=p}j0V0?QG|RsJ;UsJh(8GhNPNI&>2JH0VU=B=~92#n5H&i{ay;%i(7rZzgmSJkMEzJg!UOCt}Pp=n_l4r5L{yHMsA_!oi|5v;%x6XnSY}_)gHS(4O#J;k!W{@Sh^D3$z0~&*_dlu07z}V@ywIcT2q<7~camxWC4(-QTge1U(0T5qcJS4*nwaD)bioRrqVr@8B;Z?+WxBJkLo+9@p#eXEEj$G}%(`I>ui|4emR$=)s}`v@LvlXd7r-`1a6F(C+Y^;5$Qmz;{I6C(yR=Jm*v7aqR-%24lKIKeg2Bg7IBYgZnHN_gQ2^AHdgQuT3QuHK7&ZA0Ur2t`&oGd={3u*2I`>)U1WEJeT_*7XPy4VCX~mIxJpgQ5*USJYUcAUPb;Z!8tw%c|pkKJ{V)_Kwm}ed@LTb<^0em@NcrH!lFL3GCW_;^Qs`fa&V5%hrE2q<vu^gya}y>+67r;vgJZhAACa=HCVh2tq#xE^Sm0!uO6J^3nH%|a=9;rF%6+LP`fCL|Jd@gP$O9ScUZi^q6zeMcmsKFKwl5e@kNnW6uGaXmVtT(a=9<TA`gq_pn2inV^NPqQ)pfIyvVBut!wcmuv`MUbx|uX>g7c)_s_F<hDAwe0r(GCyv5>uXao2H$a@Rgz~Z0B^7F`TfLaAmuK;qnFU6uTi_*{{@E@{h%%T~z5quHkHHJ2__)=Idh1^D{RRr~lAeZ}hSrlW@9Qp$M3s^1#Ee`(?3p;Y`7~dT0i-8pbw_{9kj4KYteIz>`B3Sf+_J%*s;uwo>p(o&bBkvgWgvCc<ITE?b_rbENt9)-P_eKrw|6uVui{GI4;9Ig@Td-&iZ3TZ1d7N==6`bS$z%tj?!8!gnEUUW8-^21f)Z>07I~`WA7zK@j9|iv&v=;n(@YSF%!dHW@04)Gt0lqXe2);CYL8t*=LY|&RS!f>kvhc4!i^IPHUmaQrzB+s;v=MwL{CMbS`0?=TpsV3aps!%4Vd<|l)|V!|8|cx%zU9Go-$P&TVZKz4FQS(hF{h2NUlp*O3fP94gCOi{5av|ve>IG&hB0bx3Sc`0u#HOC-%;pm6nau~QwwvzHOewCD=}^*#*D{2t-$&fSf}PN3hSe=j{E(r>8UKffzE}Wi{&`zG<Y|Q1IXdJAATD04nX(A$6=itdI0`C7ESqkl_7)s3_}L@FJt|?@LZo5(!UJPbG^)aP|t%g+|On&{H$QPo-1GH#rF8P{m^~z`{CO{+raa2DX5!*KANKDm#E7%1>1ju@w_(od$7C@z74d!#qY&3*ADP}Y&zDbV;%Q=`*v)HYdUiI_EXVcDstXMZ<Em<*Hr9B8*Ha7v;+KX<j;bB37^H*`B<buAHx4@$aVLjY4HEBcmV$ZdH10Ykoy3&vQW>5aXzg32XP<k@1y?1r_@*5u=bW_<levP;a^KH%0ED!>c!f_KctryY)+f->pAot_?GbPpsnG#wu0ySF?<s&zXNS;@lBA&wFP`jjB5e?7(Tc9s)v@AURnm_-v2vTZf)tUHR`p(IMrJVL`%{e_xIQw-DPnb`W^f&L$13Fy$yef#ZCB|$h!=^iQJp0br1FKV%%M<yM(xm^_NlqyQkDw+pzX_+sM6t)x#}IFUsFUp6bQg!zI#7IGdxMEP6p5@LW$>{Cq5Pod?hLBz#XSJD~F|z9;gyhQs&5xNzu6_}uEN9(q}N=@s<!{(B-<^)?^%=3$)bEgaE{^v3-vHb*WNi=YeP;|;lP3Um?tWEP9z7b9;9bTM)lqt+_ab77nd>n0<nVEq)-U-*>zY8%$x78$wsuX>2L^rHM?<f&e)JxnIOgtBXNITm5im*B(T`#?W|=h_jTYj5~+SbhomiN%*g9@kL#FpLX@_J+@`zUm>&(o0xy?)|@n<xecVeS&%&F;4XsiU=dUao>~8Q4ba$L7T(ZXYnbEH=$kNyI{E|v<G~1`1;UK;p<~ubLdC#xz*3DAGNJ6mTh*iY^%9to7QdBC)=FQ_IV781<)_xC$JdLVhwaP{1_~M0i9s+W01#nKKufVn-5(LpIiOh`uPIO6D&PUz_{@kH{P=C`50&If%}7OpAWFu09_Bi$&l;TLN~y#VX+Z@Bl6ZlHzIc<YN^_5Q1<}VtwF2>UyJ(dpHg3K!`j;hBlrGQ51TB#D8CVTsuybyYe+A@vTNvV7I&fF!*hKxILH5jWv+MNxt0x<{x<mc&|lzhBj*nMuUNi|8oxrz!sk|B^>EkH%iW--_kSC?w=F&0vGic==~s-i_Qw51Hb)m&oQIx+KWoT!C!puykF!XEPeR@aXcBUhQ0pS<UBI{tSa%$80_#tp{<){rSKF}mcHYRnf7QcTOE1bNAy4&U?cq4-C6Ue5X%<P)Gw@09H=!5cxt@pTdISD6md`*hSo~?^aZQ9z!nj1}4fx#Zs~(apy(9(Y-v1daU$FFc0rk#foa!wRkwkjq{!2DTlUNLd4uBtN$aUe+f$$C%Bj86MFC01oxg${POVpc$ag(slfe6R?aMU00l=^BL*4_phx%aPn7-{K6`4Pxdy;ys2kY0web1Z^I3^Wox27Wj+8lLOt@LY$%M_@S;8g20r$m2Q`J_h54LWjZUR$uiHW9cO(IQRY|u^esbEgJPc$2is7P(%#rjr;Cwj=Hh<5ZVmBvmw{jgMJ8KmqjP|PROeV?S$M;sMQ_yx?x;5tgDNthxPSPzu8mjt8G|&`_Ra}f7L^0OE1cILZ0fy+CyE^OB|b{Q7q;`N5jv9Uj=o-a~%iI)dfEa%cG%AiywtNu5s}5FfI=2g3qnK>S3OxmwCat_dgoTPD^i2)EkF!s<$}AJklHYZ?J37>n!R(Ys0@5B-d4e)`73gA_P7Jc~zhx$PGcQH&E|&jC&pHDkG|3eHGN_zATF}EXqM&gfEPBMWN;3i?ApJUkG_cp@ooJ2(`+hUKxxlgLOp^MX|mp>T}<f9YbL(K7hUt|A`^j)q#EhUz<fo_>Rb{1MP_1j;PfY^};YN4C`tm>R^2x)PMge_0=}4y?tQh-oNVM6H713cSN4*#o9w{(#srn42@th7djGtF8oSpEIik-@LX5GkHGRsXspGLKpxjQ@N+S44s->4ZuM0Ub1l8h4bHv)kywtk^cIVHV=+$kHU}}6^v3-ogZ~LRd&UZq`azKNKePA=o@;Z9{{hQf-?#W5vCQ=Yi~kwRKcfcsi`cdo21~~Er=T1^1<PE22+HwaVVUcXK{<XAmKUKO_iLHo$YLFI6Fkr7>!w22!MAG_6kIY-ZvR)@IsftB{TqJ&$J}(J|DO?BN5-;R<{uTdYn6}xZI2Pm{>OjFIhFrH)c7AH>^PP'

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
