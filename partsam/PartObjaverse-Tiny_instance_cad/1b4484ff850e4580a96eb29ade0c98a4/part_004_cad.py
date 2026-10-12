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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b4484ff850e4580a96eb29ade0c98a4/part_004.stl', 'relative_path': '1b4484ff850e4580a96eb29ade0c98a4/part_004.stl', 'source_sha256': 'b389274921d605b30e8123ea6d86c13c960024c7d2c394f4c4e7efcfdf95df49', 'input_faces': 802, 'input_vertices': 663, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.005324899218976498, -0.016565941274166107, -0.08822640776634216], [0.04930834099650383, 0.21158389747142792, 0.24412496387958527]]}
GEOMETRY_BASE85 = 'c$}r32Xq$2yT<oRRFI++DN=Ol9ShP+7D0MbT4=JA&<VYV@KL2oZ=o$MfE0lM7D^WBC@3nTg8tWrq9EAdf~a@inP=ABH@WBBb1&z-=lSiE`DSNlW@p>Xp-uDH2OcxjzhcI`t*y^(t!Ee%IgH1Q(Fwyx_V1N2qH^NUaS<bz^y#10#jV=6Y||-Xj5a2e>76j5*YGm6%rbTQ)F@NYEYoMm@R7rNBz7M%ymtcmjd~0kks$mL{dx>d5Zh&|RjX3btWvI`Inn$-{>vtc;Ld-4RJu^ps*)Bb)UI7UH9g>4@S{UFIYB>KAoqUhv-A#p2kGtj%fn<oLz|tJ{ueK*{lNF`Y?i)xK4mYd)ndg^`MbWCkI=SJW>UZOO#JAynj?ehEvxZ6GXL`7^u9kurH_tpJxG@Kw;iWsIp*fu8}#k>v&iy9FLvJ(^o^B2NZ+gc>b{`wm<`X!e4e}{kIO7Nc3`la)`C(a(lhfP-7-MtcQRieSq~Lb<^J63HD!Hj->9g3UH{rQW2dEMmfnKT)ARbt;OqL?HNRJ|oOW8z#Pm#j>qz5a!Sp&G<Bf27?c0Y`dZ$9qp7QT`-BAD0z5`$PAG358Tk7e1uH0{(X1k>J+0{knpKq^h7wh^|)qjc(YoYQlDShKw-#tO!%Wui{ir!o&>&bhiU~}oufBckczgxS5zEfb7^xd2_L%w%^g3QOgy>EXg{j^Kcx4!>N_7nTp^ro^rhi@DWmfya5qpb9QDlgMnL+b5G5BOG0>-|CBT`;GF><@#EO5fgbW4BCK`d0p+Z@#xc`tBbcvIg^UdeoP`@&3V>xIleIYY&#?F`bmBWIB|`*%!YfJ>c8O$Axb%`mwg$PQI?nvuDY+pl|$~`;DM)=G)&$rf;=h9oPEZn?pYG(Y|L6Y%aI^-cjR2le?-N5B6yz>l^tP-xgY*9`H@<SNqXA<KyLa@;cd$#*vq0J8IuFj;sDqXq!B4V`ow)sn3m-`*pv%w>#*YKaW!9`>s2xzukGSr~Es{Nvp{xd(#8H9#@?nZ*L3wdR#TS9$lHK|7HBFpl@Sb<@xJz*k$?aaoA+}Yu`rx?(QA~;{yHAo6=}c(AWJ(`_{3!(l;JnbyDv4iL0;21$=kGZRtDzjM)|Ry{Y$Py*Ur;JrMMx**lz-<^1EGI*yBPsQl5N-Sj_XzqS9&IVk8GHByvs_8t^0r!lIj^rM&aB+C7{5!sG*+ecNqYrn^Jb^g}*Mzve%^u%EQk6!M#BR$~j{_ntdZ&e!_?6=WRH*E|0y8mn6__5WnVE;ExyPHEk^3lHi=;mR;^VI#j=vKLXd*Se4|M#+0ko{cyy8mn6-ebveU0+|U5%D`S^W8j$w*`HD-SN7p{=<DYW%i<=udhcufB!ng^4HfX-T%4oA%Am4rBO1U{EcNjc)A|o8{>B!4c1Te@Kou$ZY6oXM`zsL74)6MRb_v3>daB+Q`V<P%fI8g<DW<H_4UX?IgR1X#%9(o*1(?QWctMTP<rm`^Uh43Cw=dJYgr!mc30VM+K*1#E`9s^&GLM)vusp;?{=YaK>H4SU4A2B{CN4h3uoo|Xl{9Sf6#YxeW(1p8}~{7V$uXzpLIKi>e=_(t_{_*eSS%j^tZN_`FLYKmHGI7?f%j?&NdDC=9Wh4I{V4o{Xsu^)mHaoW&c*`2V6`F_D?VQ$gZI8-xp<_I6vs?{>Ib${feb`%++$gPU)HIx(wfqyd>-2OWLKb<B!*$DEGJJK&XA~8!^f9@9=f~+c}0!lKGx$njWlA?b|!rsQWJ6ZyUFcN`3z9-eCJ`--WNQ3(=)Rq;Dqvpz68ULe-A-`%aeIJ;$kb>1Ks|r*yo!4u1QUs^_yw%Kz^23Avxx=^@`NbzAyg``c+j-|GLiYR8RV?GO6y){j+vu6|MZ`@WEVv{Jn6$5E8uo0E5nEXR|zWI3awd&>IPzLUCC`5k}XA@|d(sr23X-DEz_-A`rxXy0p;S6%mKEK3gh_PK>>9PYLvl-{2I!CTUQr0RxH{&y1ImiZ)h+Z0T1)_CTiO#k!74WWGC+sMaT(^93cwsW>j*J|Ohpzl>xzV%|4<3ZnrZ?wyDBIrlqn;kENd<(wUY2wMCZ@_oEHa-=~|2gGHyZ;vQqww9H>8C^a!?zRqp9$p;-|45uQUAEA;J5~U74jYUcH;JTgT4*l9M<u@P`&AVMix64%KurEbM(28@4z?4FFhYRF8EGT-1{NF%#9hDwTlIxw~Gm%w~JRA`LK3z;PZB|;q!Je;q!L!N+CUK7Y9CX7aKlr7Yjab7enX6+Qlu2<6`X+h0oi?g3sH<fX~~-D}i#NU93I*RX%%P35}E5H{N(AG)|f=UsL7zva`A_Vw`jysXtYwe`%>q?{$52Q_zpPU&!`0x+&khI$EV)cVD)XHN2D@_q^l=)1-emx4J(5^?O>-civ4`?bNW69N)~Wouu!^u2lEK?_5a>`rf?mGQD+Xkjy_i;eD0=%}><0ZLQiF7x1IC=gD@8)~KcKlgrnh9y~6i)pYs1%zb;{%Jo5CAFs*MYd?zgc1qnDvYe;ze4RX0-angv&Xm4;d#t)H?5Mjh=$q9ROW#i2nHKb|_@e50?Oxdfp?sECSAL5WS#Q>N*Q6gUQAgH;J!)lI&^Hqgsq55`J*r(6w|_<Eb6{4eoZ5FP4wUyNHhd@EmcDVYmAX#-r?sqS?ML%E>ORnErta&XKPr9i^(IGx{ZRW>jSHcE=zbZQDf55)KcRl5efP(z$Ai9cpt|(+bx_|wM8}+0{?#{SeOf*Cr3HO!LqYXEs^$<?Z@E^@3hvjOn>#f#->95(L(tdd;pzQyB7Jn_Zs|KoYeMzl`=wGt^<bnwG+UPQZg=&(e5$i-ckM@Oj92exj-FNbpNDfQf7|T^vVUM4*1ip2kHgxx;OlW%`=-tZ<FNJ(_<9`HzPDBRdK~7y9*4E>>hu_gweP^!<FJ2R@bx(C9~XQ*4*SQY^T9am9~XQ*4*SQY^T9ammwyY&iE-F3KYTq7`{jqP$6@#2B9%UW$<X=b`|o`aI=|e9)6{V#4hr}4#ivy{F)q0et=XEHZ}o{?7xeYG<gxVHw~^l4{F}<>t?O$1S<*c%=)0e0SN*NcPwKw6cmBCDA9lUaz60NXZi4S0*R2mWXXZO+TB`HwMuoYVo!8!q67yuf*D9*>y5xiVg1%X<u`2)Q(dv9}JYV|$ee9k0h6Vj7?pN(f8#l%UecXRq@V%_1UzNYdIACo%u_Zkd-_F&^3Ho{*;OVum)7xhcDc>3?%O71lB`xSXtGcT5B+GhvzPsyxmA<*EaH#&ZZ^75~@7~NaU#9c!t9nZsEXQr_oBiU|^}5?X+hw}zYo%{&Nlg#-TkX5^i@g)-w=ExB5Nt<pT8k~2`Bv2r)$!Iel|TM<HNKRqk{0x>0!`I-je`Z$^Uf=l^o{g&s+`dy^7%#kX8JL89~QSo)yIlG3o`3J=7-l+KIX>5QvbpI4}7m}3E7VReGz<jWl{CMy3?E;LEor)LA_`DW`}xj)TzlrsavP1<88E9-4|s`l)jrcYiRt}zBS{Q(D?7Xy?9~pyf*U0zLuVu-@5whpzq(Gu=Ku<^yc$77iQLfw9osG^Xp@aLdSJ_u{=+`3FVca`j&dH((LIs;{v{2IiDJTYmZaUi+x{Mlv%qt`xB&Z6#Gk!0~5bV3;MQQK=u=JOk3$2aT6AW&bz)pY|YG%ZW^>U==<j#ORs$g>FwSZR6doPs{O9*l@|1)yIxWK^M1Oz{*JjXeKRI5biVk0&-S77CHh%paqzr|HfXUmGvB_xNsiCvi6YW>`n3$V7kn4KZZGZY@hw_*)F%1&-PKk4qO;WV)wlWOacSQhF+`2?c(3J+n7KIE?sl)n>bqph3h5jBe^cep5ik3BwEISt9^<W-y`B6n7A^j}N`F*+SBgfK9SHhS;~d^6XOX_Q{oy5{{CC&dD35E)<&bZ;ZziuJ?%6R*gXJ`{4O8!L>;1emnBFPBQubTt(~--9^<#XNBJ0OmGih1y{Bplfmgf=o%}sHug1&#9W$CqVvGo4^<i1whGV{$G&YGa_-%qmi{`G~W_s82po401>d-Z;k{oMIy+OlAKnf1r_3Hs6H1484Z_RXaqW$woo3H5*9f3<I@|7+iRJbP%o)xO=(%G5XRU03aHUrGz+W7ov}Yv;xx-^*TGT~9xY5BXNRB=!6?HfK1W*dJ6rSqtq9?RQQC_1t=G`}UykU7f3*Pd^y7BUJvAIn?{Q98E&LQ#VQV^SpKThsv3>EObBb`|Y-=^o`~p2$gfmG4))q!U*}%Sv%EzaIS)HhRU=26Lp=s_1=MypY?0?o_yB%{h{Mc$STKe+vp+th5K^;<-zmF{Bnx=&iLWn<-zmLd3~oEAO0x2BADLWdqJLe#xM6mz7_wKdY^D5-%9DT@j?51e6Z{GSQ+fMdYmz02CWR0^Zqe8Zn!5$uMC#c>TpRtr?>i0`g}apJ|7R=OW&*VuyNI_bwm0Y#%K6^e729pqy*1LJ^piFkN;k&tkUP#7vE>s7dNGb^!fEm`~3P9{d1~H&#tH3*Vj|+^Xn=1_4PE`bd$=5UEj6OukX(C<EoteKH<A>rO)p-w9oH1tk-U)1lv9O%WT<iqn-1ulKW%#KicQ_Ki1bnrO)rjGWfW^(muZ*%itruyJ(s8`Te2x`Te2M;LxhzaoO+8RM*E!MOVwe^ZQ%){QlOSUtIe9{#N@L?r;0Vug<Jptk2J@^z8mz`~3dgJ8@0={Qh72{Qlo;{m<&)d7+;#xUZitoYGa-$b8xJi}v~Ri*s$d^!f9V_WARX(PGY;%=(Y^dH*p}wyXWJ=R585=R2d?^)<osPCq|#Uq3%;pFeMMU#B<k)>$j-kv$h{pFbD-K7THLcC7R>JdeZY&*N6=&ucU5Ki+`5YlH2m-w$x#e?M^UZ<P;w|Db*T{=qvld!5Xezu$nL;r+%hDeHpgwg0|_`TqMB_!-`}FkioKam#K|K6_uMeg3{q`}}>K_WAod?eq6_+UM`<xUb*WX`jEZ(>{M+=N}h)U*{hedtc`t7kgjl9~XOH=N}h)U+0&fy|44j&)(Ph<!A5fjDp+Oh5Dg>{}y*p<-^|N`96D(=e3S?WIFc#R{I&=-<HiUeg1yf_u2bl>$8GR@VxflKQmvyf3{~AmOg*K&3*rU_3l=xoc#SceE$C2vqw6ao!3sON#XM7_xYbp4(}Jfw`+;?`S$|t^X~=GYdci_?E8iGGkm{Dd0p+7f4_jwzhBrh&MKdMPtiXAp5nS+tMah#JKE>pceKyH@A&z!?>olIKUDp&?@Hd(D(huA*!L{%>+f0G=ijrqufJz`7uu?P*!MN<^Y3fX!->-8-|w`~zu&ou!&Lt4`=Ivu_d##TCY7FjXLPge4IQukUa9>I-z!%iTd&$BJg-3ed|rX}`Md({^LYi@=kp4*&*v5R`LlTie*SD;fuBE{SK#N*<`wwI#pV@gpU*4MKA%_M*BhHx;OEcg75MqHc?JG)v3Ui)&*l~Q$IIpw_~l{q3jFf0c?EuX*t`P&c-g!HKYuo_z|Wt}EAaDY^9ua@*}MY(xY)b`za81U0>7WIc?EvGv3Ui4{%l@>pFf*d;2#&CS1{;vl|Q@hGQa*_<<I6DXrIqFa8rL(<!AGbw9n@qX`jzK@_jb%$j_h6JJLR%cjV{8<{i1`Vx;o<RNCkBsiKQ=N}tcmGR~D!>DhcR?eqCy+UN7Zw9n^*naO2UIobR)?eqC*M*lu)zighHQ)!qgKbtS7eLi2#tGGnv&*tN4pU=m0Zyi-Wo7We;az*Wz%>y*oe=mJLUs3yfzM}T|d`0bNn6DUnLzSP;SA@^!D?0mbs{OM0nZD2FXKJ6%&(uDjpXv3^C!eeMd{N(L^F_VARi)48qiUbeM|IY=QQtY)d{^yfnC}|tpnNv}miv1Ct@io+TkU6<f4gUbdcI`ye(jcrRC+dlSo;~~57)e;j+f0();^z~Y_Gba_RHo!Yd^#M=WF*j2K%9&kIj8OA6xr;zBl*vd~faZ`QF^;`SbbS+}HEHokyRR?<x8GcI{`F-@c>erp(&KD&9qXM`H8seV@&@j}}V~`Fh^I_A|`q@48I-e7%77`Fa6kYN|@l)+6{nTaRGpIHbPwuyqYi;!#x|whqFYawg>Kbra6F=cUircW9rl@6bM9-=TfJzC-(beTTnaw!XtlZogUP&(_OmpRbqEK3^}B!PnzFe7;^r`+U8O_W61l?(1>GdiS6zKU*K9eZD@(`|_Ad&(<GlpRYf13jVV>*#Gr9Chha}P1Xa2Qsw^nI;jffQ-l3qudDKXw%#gQzGcYQ>$bGd*K-*O38}&Uuh)xdpRX6Q^36#N_BXvA%^9;GHP~<U`ZeS8r6J#6?^b73YOp`+^>Nzg>*l;Xze_*E`abv>*7xc3e0`rz&(`-@qwcEm@b!l9`FcZlc+V~J?|j{2@$FkwKH+td+UM&cqxTL=Kf^jr=KJe3;b&N<$$Y&|(|he3>1SA%3O~cTRQMUzrNZayQjM-xL*>-#e7Wzh^POC0Yp|T=BDJoT`%ZSXt~R>0g}RU9>wMv7Smz5r!#ZF18P@qeykcu+<>$UGzxMe$+zh^6hdaPkK3g}feZFqm{-xeFxy{ybYoD*<);?dyt^LqC?lz%S?&ixQ&J-+d7!(g1j~RV>1eUmyN&mEFzQn!%bN{O)?lqo%_W!%YJ!gzzJSt*!MCqD{VhZBk(Ei}w;KtB8VA7|-jlor+_YK8W!GDUF37rkS51tL42mK37x;CQt6%n&U<cLv0{78%n;#|-<VA8o@3gX-`Dv0wy=Yi*8U&L#1{CQ9}R7b>RsY{C}2Q3XIEd?g604@ivh#;;Etpu(Nt^$1;O!^eKk%-13>O-4=>w_(53$O)ljv#IcZ3S)#ZUb!#ZUb(OAbts21^g2DS?E*X5h8|(h=;ZV$AddT+k-oS^FVWf^MLb0bA$7OJBt`DVx)+U&@SMP;11Bv;Li9hv1m%8kU{e!45J6MFtiZ3FgO+(112@Vv0%|fj9So|Py=k>H#HH&b)h!6F1R0pcr1c=OrWe|5X8L@#Py(s!G%%2de8`1mzB7!C`5Y^FCmCugth~}2yO*!2_|h0ZUt@uZ3b=uZVYV-CT#?64DJi<119Yc9x7sph+zog5eVYp2;#xeL@?<f@L=#jXkYL^@BnCka48YbiztC0t_N)Zt_O~TP6fw-Cqt)!CxfSmC@G@8h|&n+7oZmS1#m;?6z~+}L;SLc&LW<H76m^8ewdC?H2hN{#v+J|L5qTmfpbA01m^<(m*_L^8%qCxl280Qya%vN{sRc&BG97XBH+r<r@)oL1E2%J1HcoZW5E-_vm)v^&kD^4T@PN5zZ1_wdg8G-X5t<qo)ggxLHq<XANUDyk~luP52!7oH#7;{8$1n4>8C+yU&O^wr^LBXuhWcw>vtN0crWx1u&(R9P^w?zIwJatsDU7!0No4Ti}VwqMZgrYJ<wl>lkoS-;L2!&B<MtN5_l<e7I+rwe<^}^GxRL@EZS@{wuv`IR1hzL76p^i{+3|BOTkO=d*Wpx%>+s(q9(KkbON{rcqw!lcqw=>f_Mpn*oG#7^*(F_aTNq{acB*2ad0sN@v{ix?$D*+?%*!a#o)y#Qx^nrSEvoHE~2uCN(ka?(CpxB;CCWQk3|$y5Kn<l1y2Dtg|+}U1?Ptr0OtpPBKp^EL+K?b`NZ$R%Y$w5^B{;@LR)}af@eUdf@grwLyv*agH0SC9jA#Pt_!UUt_yAgtqyJit^=(Et^<A&nhpFU_*_IO)#*6|@pR}E@N{q!Xj5<#aBgURaBlFshEl52cM-(njDPEW9D=y3h;AZY6wwnwJP_Iy+!g5uB8c}uFM)OY?SYO5?*R{jb^~|A{sut@f<F`Ge_zB02;y|;5pX(qA#?$FA$SNh5j+Ik9NG-r99#if9$W$ZFf=RpVeoZB=}(4Y3gXiUVi$S}TvMcfPQ=Ry;vNX%1Q9m0HiEbY^f@rywEZpQV?*hO;E%!Qq36Ko!55()fiHq15vBitDTvEJOGOk@5I2NA4{it^1swq%1zrVR30?(00X+pi0e%<y9{64GaS<y-q=+~PJq|vOG$#?nR}sWtKu>|c0B?t`1aAjVhK>MF23yeQ!4|kMv=q27_!rb4)#EP+;&kXo;B@dl=sEB{@Db>T;3ME$(7(aAz=a|zh)Y7L-;_iUmljbGnhk1zvw?5pcht9TBZzN6&x3D(??5kt?|`#Mlv3Zyjv%fCEd#CuZUk)zZUi0-9R(f?o)29Go)6v#JptYbJ`8;qd>Fg|dK|m~{3<jB{3>`5f_Nl!1$ZQQc!cJ_D}4>R0{j~I3iKrSB>L_Z1o7tx;_skefWHG@hHeL625*B-25$pTf?D87;Cj%);CkT4q12Bb$2Rdz^zC%;P4HppKJa018uSP_4SWcC3w#LtGnD%D&)6m|D55Sj4q6CIS`r)wt`98@t`BYy`S*NifFOQBM0aQvXhkq-HgFYiJ}8|h`Jgwz6vR(J?||>%{CEOETnkzWOxg%s3)}}f7)&}J+y^`jx)Drz7(5L;0lEQ9`YLz=xI1(ZxI6d-=t%Gj;0Dm)f%+Vd`qt-zuK#GDjiPAJy5MB!Yv5$?R_GNl>F3}vA{-Gz5yZ=&pMaNvPeTjDC_WAT8d@GqL0kyl)8InjBG8K9BH+T%$H9fc-$ayt8c|F^d`84D5uHSIL=cw~aY6Kx<09UGP6fXKo&+5Vo&=r<9RQvPPKG9elfeg|lfehTA3)y$e*lh&D7^=!ATA3n5mEf2h-XB!ftCf6mH@W_w-(U~S{zyeTpWBCdDA}bB8ZPd-vJ*5N1>C!QSe}BB6u*kKXd@NKX?dqD0m2X3Un%X3iufGIQSU&Qv~s6&<kMF*ofj-wEt)L8*z1boxs(g@z74-p3q*<PT)@HXT1=_N1@BX%h4Z?LO%r`1-l61OHk_5m#|G-5dFO(xFEO!^l5Mf@Kez8;HSXlpasC?!1<wc4(G=<@kN~14)`K?9drzM9e6bQ+i3K)(ePU%#-MMK4h6pm?F$_W?hBp^T?U>DPKBNZr-DC%ehvNz>_KU)@vu$&Ewl)jg7_<FVK4>p$50w;K1L94ft~?x0ndXj2hRidgAN1t19yOS1e2BncK|;NjRijo&IzS{pA*}}zu{bX1N<BKBy<w^B={}pMDSbS{m^9ae(;;n1K>BoC!imIPk?`g(irzEwuy5@l$HgPJ_DXB>U^AtG0+6?7;q;9acvQE#BaKY=!PJER77{Nuc{(mKoFOJJ_#-X&Iv6F&Ix`H`ULnvaCYc(;OyXH(3io*zzv{pgByTnKp%-Ho&nAhQQ8ii1>6=vyja9oas0DI^oEWC_XgL3b_CY~e;HBw7?^^1Hk9(7jeWEO&j!DOAa0K!&I^46oELls$3(|@20=Uu`Z9PFxGD5Ga8qzK=o8>-;Afyk!OwuJL!Sg!2RDOO1vdkahIR*!2A_o<1fK;z7Ewxl?J)##S7;Y7=^SuZ@J#4`z%#)gLaASWh;8Ds=<5mKvfwt*ao{%KULyKI$3w?~N#}ycgBOWd2%Q6+3!VcW4IKj>4UUI)0>^`^B8aO&YlBJYIIBVDfUDtr9uKb@cpS7dv>W(Is0r-`?uIrn5yXAaR@7#F(1zW?-7!Y=K@cY(h#NvnfE$8~Lvw<QgL6P11m^%h0L>150Gth444e&YLK}ch@bl0a;OD{9p)_7h$2Rdp7(?2E9|FIGAYKGr3|<7zi}8TQg}eyj4$zL^4&af{QQ(o_S<u<wS>T0;+30tqW5J8Sy04B!zwQU_3GEH;32qIo1#S&41Euk<47Q0cU<{lMo{ce%nBK?IdsceiO5axKI|+R+DI&JZizq2#rpPBMVu6TPL`)JfU&IU%$s%4AF<rz&5%Wak6Tf-fpvf+x4n-6ck(K(Vhyv7RA|4TuU&KQq4vGEU5%Hs;f_Saa*A1mvW0aCld{F2$v3(o5228pOOqwM|@!KN)5b=Ydf_SyiorcnfVw93k{Fcz~#rE&eRbbK`VA2O;6u&9rHxXA26~rk*w;M_yh*3&D@f$+F6WhN+SAt1j1Cz$aC_W(K7ZKkYDu`DI-DW6_iBU>E@qVG-i0xa@<zUjSVA4p8;(a1+iul@4LA*@p7DFjbNLU7+I8EqR0)K`s1(T+NN&kr`-YepU2+vSKyhP|`L+RhxCZBi@T_?o$b?9O+=_WAgUlGN-Mf^m4+)zQhNa#jG>3wXIPyD)wFQ~6U7lKJQfJy(1DBeZ=OvDvK1@Qu*>kXy%uuVSkP7#->uR-U7NgXih-H75H)XzkGZm1xBRp>fH>3@msHq9e3kH!8^|8>g0|LFaQ5&Dl*_%FlL(SpCcD)RCtr?qMR;6tkIW8{RLnsl`={u|HjvmX'

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
