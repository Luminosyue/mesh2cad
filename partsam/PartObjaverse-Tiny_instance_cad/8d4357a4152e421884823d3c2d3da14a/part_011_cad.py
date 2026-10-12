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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_011.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_011.stl', 'source_sha256': 'ab04e1f7c68508b0efed51e1626ae42fa81ac8544da5b2021ed7ec716297814e', 'input_faces': 686, 'input_vertices': 419, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05783037096261978, 0.25100457668304443, -0.02928721345961094], [0.06628362834453583, 0.3456554412841797, 0.060159455984830856]]}
GEOMETRY_BASE85 = 'c$}qN2Xs_bx4xk_sR1G_BZBl^q-QA7Arxa&+5idC2_;m4ORpv&ApwNI(0f&?B7+4ff+$@D21L5j6a;_Z&EDTP&&h$e)?4pot-bcQzq9W?drrIOo_nEPtMnOyE&RP^WxO%zr-P*|OC*OCYz>bdGOSO}=%Ez{#*7NGaw{)?ex1}dqD{N^f~?`zm{L*ELwgP>RmV}PUawlE$~#K+8Z>0sknRJ!4H^;^Eqv4N{f9>T_@TYK$3*+=($%ZfF7K#Tro3aU<Nx@V&6k4n-olOhB$wZQ{UOY!++9;wi}p@PQQmWTpYo2r&gIIdL@RH%Jq`a27gq-I&aeMa-u23bHG18-aKw3kyYik~wHK@Zf`2w>oXi;z=Wxu5K;DzRHTckiYxTPRUijC02k|%dSSQ*UvKRcWI?8)DH`e^!wYPz9{>yRYd*yU%oP>Uee|go9nqQSqHGgZHOL?pO4)B?uuF^PN>VqFMUU}E$%*!<1r96l~AP)YsifI1!kQ~Z8hmTX<`mAEA=9y#5diC#nSo5@U&YPq0CR|#le6dHGr}JS*lGeL(CHO<}8podTrTROEG*I3X^HBXA4fn5C9hO^pYtnV)U8}>jeLNQqtkpP$M=S5{)Ioo*d+U1TJrPI2w{E5V<#~_{er1;v`a2u_uKuoZW0kiq*Fv5X&uDvEC7L1rrZ(#Dx;IkW!E-kRd>M!G&h`<DG|%_5BYufc<sHAgvQ+&Yhu3JkeO4ZP+!1YO*UH6f0>`IyEMbJ^n=uIdj&ka6A1jln<%1rq)_Qxrt$Esuw#-HRUzK-GTZw)-{l<q{{`;r!uO5o{Z$^$)zUcT>%D)w?@vUKhPFB8rUFAI?sT$v^88J=yN;g-i|Lvd9o{2R!YQ2evl(+WIL;LjoMaPxn;Tq+gYbGH7JcSl2pD`MI;r-~}GO^mfcIRT?r;bKGyB2EuyT|5J-t%z+;-9dzznqoQ!~dO$@Q-e%<HtS1g8zf7_`P>4*VjCc?Ov|@@g*2P_y5uHV86E%{DEy~x2nCntG+T_dFwp#aTPm&dGU87{HGQ}{FM1UFn&9L|0f*nGjuV=Rgae7BQbug*%!vCP8X!S9h)2dc>J3FUVGT0W$NGG0shbt?O!{2j`H@1G3b}$aTBy1#{IQe+o9$XjKf1UKGu4tEe78?8TICFnxO5FeW>!D<amt#>;1GHtVVAtZ--n#{+-|5gnnC+s&QgEAWo^CW3-->p~_pmwxHdvpYN#sxwAL?CtpJQgj}jCw!2b6@ZD21jwfZ6{$9tl<BOD!DhU6}(OtFP=i`*Od+)>g=Iy#c%eM}Me}^RW%i#tXZ)f8ds{bLZ16D*&Z69m>u!WcxvoY_!9*%WBe*MRR<J|q%NL_~=Ij1gAenfS&|H}8Y{oV2B=PSRmJH}7z6pX`;p~_nYtD@e%v+%ptWlK>$`vdsbI*RtZ??_g@%m-+PU(0I0xOQKhtNE`kjdou6o3^v{<#h0chr|E%{@TCZ>CKdPJ{yGJRjxkr-<KW!f6Yg~<R75p(-U<nN$YL@9oqBDtJ<EP<&Bck^p|}vQsZPU4*vt?z;`$?Q1zWti5Q0?Q14}ju5aG$bHPtqigw$2Ws=6fSXFsv*-;p8d0*H2m*@J=bF@8UHY1-pUd`WoJYIRbKrH(Ai<Y|HIyxmJsQ>tWSf58W(0*}*_f_5+Ss3?I`>?jNv&iOn<v*W+{@om_{pASl8mDne-o$<9pAnj;yL4vdt!e|{Un~#i<M{itG@lAj(2w0R>$>Od6EPFx@B)7C#Xd6vd3$9B^y8$1+Q07ix6RP_GmE1ghQ6lvFS}JP@V1Tq3bS;5cI7=bUHRx3{I2+^n=n6WDDNC~6?s0(g8Sg0Pp0YbO3aIK;@GR}t#|$Msmj-FqH*l?Hz#VGM>Umq&bW;J{b{hSOLotFQ<U$9`;Mz=EnOeHlRs779$XapM>=#pbQb=3vgUcWB*sJN7;R^}-f`vaTHm6-7F5GJ)@z{h&ci3ro^`sYzh_!c#M$>d_BkatYCGErIp81B3H+JuI&K{`Pft?bk)ZA7&Tv!jBhFJRCu+S{QLpFL+$CDx<h-r^KeosI>YHzMyt!9@4*rWVKVm*V)BA|^b9&{iRNO~gTMlS^Z{sQBwLL2)q28vMwEbO2cYYX{kIUHr`?NDI<*m0{p#AUO*8Pv8debq=^S<x6eI56s44X!4{K*qAJ}Xz${iOSFf90($Es>8i2J6p>{NN*IAfKl@b$zoIo*bp^aN3LhO{%T+S|8jSu6ZtPhW6yX(LP-|HqhTSrvT>5kLQOdKl&o##1(*l#WIJ#kUWQHJgI)qURxW;+j*8L@BQ<uRTxKShJ?K&j-z$)*szz?`?00_ATv*Q?qj3EUh=!#-~9?cBkp&u;$twsn&lcD_LBB-IeURO+S4(5wen{B`&K8c$3}lS+q|#)tQY#X@mA$u7!SM0jSqXt_;Dm#cGyeCo3r89%A4cU^XwdWV?28kmg)R9$G`LLkCOuP@y{1`%dEQZGv}ALp-XvlKDu7(2Y+M!x*vXr{i8A89iLuC9AkZO7yW#S`Wx$spMPQf*;;L?^2U1Q?&VhAT;JSTKGS{c3+v&cs?#-&v3}a$9ai34Z|zxL<vk~!V?0k7is!iB3g~)ouG@D0&ESo7-czE(Os&_rU-)_Reqj|^tGwsxI?S)ALzqW(?#xnu<9=k9N}a9oLtCrAD{3B|cP^)o(|G26ZFjWt=6%pPCM8~VgNoR<KYoy`e%p5_Z{AO>k_EA^yzv<Qn|a&XH2m!qr_}y(iN<kn=#AfJ+^_9jaqu_p@9qg>G2RcceRdv7QC%@kd2^p&Z@&nCV_)H{Uqzpv%zcP+;(X=JeT(DsbKs4Aj_bys;5&5J-{sk{RiFFpDfzL!wp<SXY?bi*9_0XU?4!IfO_ewIUEVJaC~uE<Vcd3Yqw9}r`x)@j*oS-a)<t_(IfwYhzRsGR3-?=NALxo`rM$UsbXV(z=g3YC@Eox!U1A!(Ni_K8qvxxRpN;s&zSL9T0(fH|>pu7x^&UQp@z(OMxIo@>s50Uo4AI|fy^>XbpVgxT`15aQzk9<&!5jN$_vOjT+Xp${YrUNm$UARWM?MRlY5v~fIWdlm{kfw?3FSSRDr*0_cTUuPw;Qhn{|UyM6&Zr{WZQ@H)SjLZ^QCHrIf1+#*%<jxZ=wF~#Oca=jz)ri=gY)E-Yzj1{PibVpR?Z%@Wr=a9vyq6zsptO3hK>^c5q((LEF)Cysp2`d>-+ZYplFosto*pewq}>TkXP-|E^7_?`k6aC)I?1<0IORuFjW~H=l#7vpE*1fBL_%PVRhD=cB8qt-Q0t7_?i~YKYr!vhwD0mTTMw#MxuRKQ^bHFL`f11^)@ggZ2DmVj%DA*c|++eaNrg>pC9oolh{{8m*2C<eg7jW1L*JG`@9dlJZuq(9@{5mhR8ooi}4#8_$W(Cx0V;u1Rd4hxk2J^DIPt8_*76k$66B_ZIl!ufl(P_c?*Q6%>y44{n7#vJ6%Jh3D24Nr+=S=X$s7Mx2!v@-O^}KL2>y{In4B<R7e8bK>T`l)tlLg7A({YwCJtRn37o?IKEOeK`j#LO-T`?zXy&#rkJHr<3>W>xBDP#oM~x+8s|Kj`6(jZIDs>!PCZtaelXi=I8n-Kh778a|3%%W%zfx2mdz*^^^Rq{2##IIDhc-R^(mG>k&`&Ji;}D{%a3loji3_@ArP*`u=b5k>7q4$a|V$-(r<tI42FC>;%6tB{@x;TaA!^P=Y&+|8n%ZwdV1HK;F*X4&x+O-_$hz?jhi(rOXZFoz1W=*#j@7iEkgp__Wu4oF=|AVlwjiZK~St2ZNEPah~Jn?bBaryV>U^=z8neIt_fu5cF@I$JnRECnC=?r_|rM<GDV+xh^b2y~a6`)piZ|TjvnJXI(tc@7)M~%4v+xqvLR%vZRLIAIx(qN1wrq(f(=AwcKw^Q{K7#7{*Dh4I?$5jET6<JU@u}#d+=NxD5WrxtX`<1@Jw;*Eo)0+w@$?_45Pp#`&9-d-{@>&38X<&UbH<qwvq-MV@_IVISP<BzR+;aV3>?ry2jliwxE{*V-uWJbVTGfBL*7dAjpNVBQ$(p`SO`L(j^dh+k(r;<$owzL3-#ag24?&ztM8HztAe)mYEZ&H>+cH{x$=h4Y<+xv00rF7$i;WIZo)jl;aRc4GWE^9;hgBX8bctV|mb|Hx*<|E9Y>w>xefM*KexV!WMc9Ha4Fzk;_4!~fA8#Qpkj#F=pf^P>24?AKcb<6J*w2l5=BP0tgp`bDu{Fz%a<LT`aL?!SKCy#IQJ#DX{O?~dB@!EeKJoV6k^o^yIFLq5j7!q1!g3QwiAh-2(q{QL|1mTSSw;8zL$sh`CK@-OU*Miv17`3AIS^kY4Du%Eq(IOW4J4m16(&xf9w;o!N>SQno}>9{QwgE*llz;F4wjMlq(H2f!LMLRf4BhHv4@Wwg0wR|Ds80YF%*b4X?`$j)+?i*eA)+=v~U_K{n>p6ut=MKboeTnDLW~VeC@235Te{DJZ?-$qc?D*ya;wQ|)eaaiJ^W9zMGUA*2-Xk~QZ|tA_{0sZ%QBT3|J%i`L+VME|xSme6`QE{~Dg@_7F`JNQ*LWT0u9RxZo6iOR%^S}J-h>w5jrSdnUG2de??<edw^46wZ_J~L4^uEtBH?eoXE`+*`5Vtc-gc9ecZU22<DpEAS%JLyJZ0ydj(UyvJMOUMsMmZSw0RBU6y<vIeB=Nf&rf&3-*~U&TJ;>f@gB<CCEW_l&$REYyhU>3z2cgs=-(1s@jSmFFL>kqmo=*>;u!DCJmV_iIXK(zh|}{d-Wz_{9lU?Nb;O5A{@!X)h-1EwyR#bg8qeLXU)I6jc(3Q$e^B`s-UC)S0Y3d+<nv^i?ytPL&LN-8AL;mX=f8!x<1e7zCOeVmn&(5+KmTp`8}A>zYabzgjeN+n^e~(YJYzdqJ<*R(X5ic;&jg&C8s{6X3!A|A{|x7Bg_q$ufB$BjXJ<L0{_f=&(7&U$fnSh>`^ed1x(+*!@qK$@DC(^;N$Yi-yNYw}A+czO?cwV0esULl`z+Wm?HsS;(-9u5?dR#z4D<KsNz`}qb?m#pKgaXW<vLERPIcgKzPDZ5Qh9rIF6`5)hv3{}`vCagUyeA{H|YM>YCR7A#(QCBxlPJDyZ?mzqiSH>_TC2nv1P%(Ul;Wr-46fI1jH}j75nFzH{jm^=c~?|$FQEf{}1wM^b!28_R-(v`mliJYwdp<?Nh%J&T&eW!F!}o?(;wIgmXPlL-<daiFJ5MEY^W;(cmYpf&by{dj95IF)WS0b#9BUd+r~`tq#oJj%|zcxDz|@9Amss_bxkuI4v5Y-_v!%`A+8F5XX2g?@hgrIL3Q?S9J^TV~zLz&ilbQ&nt@a9J_gMwEvW7@GG7o&m9f1Pskk$KI#)Zhh9m={$Q3H@r~~doHxFOf6hbTdj;V<CHxT1xsC4@+|#pRzifQx;0z7HdjR9R2zyTvoC`i_hj#eW;<?-F;1}&c{`>Reye3-<#4*0Ru=|Zgy`lKt#<}1G&IzN&BaZR?hFv@v{>JwnPVYMK#`huadpp7J;l858UF7-70pw$RXJVH>i+Wdlg71G~=3rlO0_XakW<TP0bv}mkmI1kxH@{=CA__sz{}ge)ibOwND}^}i_n==oRY3fu^}!q8$+)hrz<IXuU5(ZISMbJnINrEhIH#Q8!a6*&E%qPX>frqY?^E7;6);}!Z^iw=_|C_<G`l|co8JZ52lFX!en;e-T@U93#&<^^Z#VG9cS^2(eeu59_^!$O!B)gKzJs!#eF5J1Zpu0A4C1uhj`jSHL+Hna7vXPwf8{>-1ibMbm!E&(JFd*(_%6oy9?bqG3g`63cV&Lw{I1O2l8iXU_i3IpsT%|5?|*;KR^UGPj<+#i(qBP8){WBVW6uvb-*6A@h<RSA!xpXg)_L$74q*L#_(*v>>Nm9W_=n5G+NJpluwTjcL2DeoJF`!+TESMY?g5_w3Mqen{qj!$`&9p5eF9jsR?YwKCx8chIqdYwA&THnsFx9o-bMTg@geGOi62lOr~a1sTlyWR2>yzC8?opgiN7K~PJNE}0rg+h=ZMeI?=Onrhtz)(i_RSc{E+xB>MX<$czrN!;e%P8n>d)b1htb`bZz1i#KF`K;s=afl(vJ|LBFCD!40V2Ar@VWxB+od>QG{dFFGIXP~uSf<)a9Gogz4l`fXy-J&D7J+ff8}q8>^tdJJ(V;wXyXKGYM5MNc8_L)?!dcmVZuV$sux2N3tC2<}TgnOO8V;=aTmPy|O)e@HBP1aUNRcZ%Sy)We8H4<hbL{60l+1a&WB(UHUv#LXyzt5LTk7G0jW8u4os!8xf56W_6*3(+o2T$p}^D1xg}w;>i?fw(GhA?hN;5?^#K+C_+q&@UH7aB=GD#G-Q$7bng|orzfDi@ryli8vGe1d9m1Pkq+{7JZudKJh*3Ux@EepQQeU_!s(}qzL|o`g3B@9^!9^Pf~wJe24ld^>@VI(eEfl@LuXQ#G>~R?<GD;eT4W9^$F@D#7F3Nf+F~9>d%NppCbO6_yqOO#CNFwp#GWoXZrm?5&S##ZDP^cgMfc0{)0Lr@f}{DlXgaqQ_<Opa}xW<d3KI{(ILd5iv`S!Vgd8080VJgH;6@-37B_f0_JHM&Rx-!h(%W+7Tuk=hcD+SpA4cFy92T4o&jZohtc+9(L<=)`lLB=2io0eHxKX=ZUnCvZX|6#79C41zV8Rv{V7Api!}8~GuF|RTz~4$jL|&6{~hx0&~8RsbW8Gnt~+&W;#k_9>D!uIe{wGR3EzgcAB(O>T_*t7rrnabHS4cMyCv<~<SG-_CN57bx-4VWCKd_xNfDNZ2Kba^4rN*H2(T+s%91bclWN2w#mH5pEoHfUlACrB+75EX0&rH^B2{^<;3~9>)2>F}g0u_LN3d*1E72}Uy9&9+#8rr!5Q}caI;s#y`lKUq6WWc)g%dX-4&$|rm|G)q)u_YSeqq$YNBiVGmUW~ZPR>OfPTYpL4X=NX{x0em;z-&OuP?E1!|4-EemHS2;=aUv>EF*ML&<fe-HY6C;t1+U;`X%L^BVuP@ACTg#KOJhlecNNqV31;(pSp6(0-S=H*s&q>`i_E@c{CDd@_*s2eb#!_XA>)!SokAi1t9@0lcmUxq-xfKhYzIM=(w&`p9)Hh=prM+=5ti1L~T@qDv4rATCW2970`ySaf#c5aMhU!4`FTV$qqcfByt$q6p4MotIej>%{qp-=GMtPyHtGo9xH>l(*QQ^{J&#%h7JgIQ7XjByJyIH>Pe+oS$XE#QA9FV=RA}=t`7wyfzE32`0`*+v4vRE*)(@79B(poRN}+aWXNE-%rZ2QU?>i!dOzCgSOzD)EUV8xeUZ|Z6W&SAkIOb!sLZ3>622#uhRD8LiCsN3bZTm`a;wpj8%bHI2n7T$vJ6PAQwU`G3yf7rJvuw1Fxw|EL>aSy2PU8zFVERBz1N2ep~9PLB3?bHNrKeZbsakwn!NZ_rEf<OVUqpElQ05A1N;yU<-bYwjYZQrGAxdTa?$n8c>#pQj|WSv~yACB(BW3q1L~BpNl#xvGk4n$r#E;{0jRa8?m%&JGQyt9<*iL%iM_|7VTf#WxX0o5$wM|h>j%|?IJgl_6TC(nlNr8^OZ4Qka>$O_wyqBeZt9oOZEhE?<>#WAIdr;w(N~$O&!L15`B{3leN@hPazgPC!kF5M%sQXdN;N0lZnJrXeZO27~q#oEP9c&dk}2-Zao9Ba9_|*e6F*;-SoLme4Tb%ieS061?^G9;^+5i>XRYVZRtOXcr>LgeMVEqQ}^&m47J#G0?KAmhS0}fhu=ra;;3VY=lbMh;#sug$i)-K(SJC7#2!dJoLKZ*#G>mHi!Mvtjk+xHVA_KjSMYe|AY4t_gDG?ASB`dB;+g^WV8%Y?Ywx-&J8Z!gEZijWHHpX5N9-RgNKMARK)WpQ2J2s+a;#Ih)#OCGiA5hKp6Qb~a`Cj?<dzdJXP$1#F<!r#*9bS)CzEL}r0vJ?%umY4(vByd$+CFH6YfKwOz_DVV&TTo9?Ll6h{w`5j<LoP3pXPGe@I&-g}mU!w55C!InmRIMb9RlO@G1je6ou6Y}$*-?I&JL{3)^Mb*yi30A9y@r2Go)b;M_h&$8X)XfLO%BY&3uO@e@%aI6W}ItaGN1dc7iQ)wTge_cuw`n0Bx*d2W`gLZ4$Q_0OEo=UucSadS$m`W_%V&Y`th4e{gy~*TK1MK;fWb#s;K%7cEhd!yCld0t51MH6}spO@6Q~*w(y^y&jP)3p$JeIbUCy`4cFF4UBHti(ZW66aRk0owSEV?1%jt#&KS+A7;YQYwLo>-&>eFV#TF1D0k5Aa{hYt9o(nbiN>LV0uMBY1~T){}ou`&V*nt$%$I$*m`rvX6<Sd={~AQ)y2lPNXgJ5&4fej|5MlpC2dEUd;BCc3nignB#5{@g$Cexg2lv$je;l$npD(_zLIfGtQMyX<uR8^EkgJF^_3nE2fZ>`?su1vK~#R?Z=`QP|KP%H^5G!j0@n!-by`}csunY;svxtw)o^K@m$)EXy2r4rO!=jxd(~}mV01*;<D5i0`LafTZpeR{!PZ&!<>YZd-*@aje=nN@gw?6`5yYn9%d13|DI+KxuwKQ`Fr<J7O=j5c#Yp@5zC~`bgU<aIY|96)RMy%w$%n+H=Wl`Bwob+9YfBh?Z;DSON@n#GoE8k#@le#Cw28;4q`WDZgn_UM{~`QIV1ZwnUBe=M{>yPD|^)^Pl+qj&JzS%_{zk2Xs7q-TR!czVBeya>(bLl$}alkKP>ZOe+<!LKcW1GKKXt8D?#AoAu)dd7Jb7)d7hwuuf0V65^af-EeKrJAm9SDMJ|)SO#4j0^@7FMqJLwbF3Ial1;O@X(WP0QpLPLai)95^e`8)FTr1jsEV=`=_+|~TD^f}a@M6D7ot5}Kmie*h-Ym~d`%U7%Enw00=qGkPN@sG{EZ}<dy+;3omi#jd*uozq7H$)<=r4&y7i7F^#1dDul+_@vLB73DX4C%3f?b0md@Qf~-ujo1<+Z~7ME*CQ?!p*LEZ9F$y0D)4KAcKUuANVu%4-CVlDS8FH0>qiRuHGMYzeu?#7l^!?#(hRf?%(p{g~Xl<V6I#Xp8Q`-}0DwyXc=noI;;2#7n4`1>mK$-NY%3@ey&mRzc~4)BjKZ)zQCyvbV6({KrS;m1#eZ2)r^=Y3tvQCEB&hC}&H)hyHYWxOhWOHmv^wr3Q3c'

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
