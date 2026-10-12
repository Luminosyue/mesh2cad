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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_002.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_002.stl', 'source_sha256': '6ded89088e5dcf4dd546a95a301d8a350b716b457f099c50c1aed47eb0f83163', 'input_faces': 1032, 'input_vertices': 583, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39144158363342285, 0.08527001738548279, -0.49376043677330017], [-0.2976210117340088, 0.1720735728740692, 0.4940462112426758]]}
GEOMETRY_BASE85 = 'c$}r337C%M+y9?uEZM^h69!`)%aGlKGRP9yLLy`dB}<m1LSw6t5TT-!L@Kn{w;_>~Y!%6tC8eZAl%@AN=lWdNGuQRp|Ks={@9TG*$M<u8@AEnDYrXG#o}pj6R#~#fh4i0Np>O`V`bmYlp^!wLP+Vwa-(e#j?$dX8)xnQG5f0_g@a2!uS#3JCZr3Fo8X0;j>A}9k`wUB}mzdO`UrJJPVp6{$!$u72HTZ!c!yfD_ezRT!hxb+f@P~Rm+E*P{sGU+XIk9HN<is(F|I0tQqz%3D9^RrP^_7HA8!GMj>C4BrWb)JT)7$iL{rUL+_Bq}#bDag+4~=-u^^Xq<u8$v8|Ky<H`acYE>kr7O^Y8v@yHg)OwYBzbedD*qH}y>&d|UsC80~*I#BD!*>X9LC`;C8eh}(Ws2jA8o9oGI!CEWV>sdGxW^^HHTgj?U#!MF9t{dXwC|7Ef}KKQA>PIkw~_`gkd$H&ycxAiAo*M9STZhidJ7W>@##&5aLt#9h!+xl}a>HK{!x%KhW@ojzMA9%^FZ|WR;$*uq1FFOCRHg0|V)RAr6`o<sC#;tGa;M@9JPcaU?-TL_H__n_BTlRMAn>wv}2i8v?yj9m9efe;Pe`UA!k0rX-#ZNt+=w8?OCllT4nmYLQy4iN<{G};wef)HMTi^K0Qr!Bc&bujY{rJt=|Fq0jIZhim=(`}lXO>qTKfUUQ+k*0qZ}V$@sQrBHwI5qf`?syo^`{rf@KbYD)PCc4wO{E<x*RY3v{|4ZTDr~kX=hYEzMpT}>E|2Y=C@p`>-_w?u5+cD_Itdp^M9)Cw$t-%ou030zeF~79`RF4W^?D!_@%PB^Jwbe+j;CeU+14H;nv4b$G7#3f2M?6-_$u<!mU60MQ0w<8pP^;Jv+^r$Az^EYk%fs+J8-tPqxZ|e(0fNu5aei&o}ev<=c7m^6fmD{8`UA^VqXY3GFXV%ka~}xwkm;==pXY-x*7Ln!5e+e0$wrdg(f&nr(6NJ>TYE=&9RZ`|2moJmRO;(Y~EW<EP-8c{FwK?L3<Nf8(|X)lbLw>!)9f+a6Ru^?IDUPJVwt=U@0uk8{oV?;L+te8#+-Xr9mUQ)An1)7Q<d{Y%~T_%wQRQ^tBT_ZiQ(_Zj^3*cg2uODGlSC$>N5`1Zc%<s0A6xA#52KEBP*)k*tvyQDk$o^SKx+v<KD*tf}9hn{cOVbl8B-#v4SQ{VG#{kv0w*MFy4IzLy%&CdGte7in7*VJ`#Wq0?f=SSuH``YvU{HT5H`8L06jo|xF-zvfPtAUkt{(wR5{`GuY|FQDgKbPR{7yNX5yI+j|bAr2HOr7%y-hH)9@N)q_>bYQi|G8l5_|Jt|Mf5zbn7z^2N1ku@(cJjp=iS0sou6>jy^ndm9k)dVwI4fsv$H-u->%Qa1@v{px!mWt=iBvfeE+%c`F?)XbKmoA{?h!x?<dRi>h_o4yV0rR`L+&z)cenxoV=eu<-R|7zOA$O#<v-DuH|;$(>&kKBYxC-o#*@cQSWu0Z}Sga*ZzBT+;xke`hFdE-5P&I9e3TDI{0?o9=np^r=`^0<g7Q(x9jcH-@1OyN$F1eJ>Rzf%q4x@yYjf>@A-E8@l(Gm?e^E?<J<lk|NGKze@&gErM>6oMcuEsEbjjDeB0kVXLS9<5^jGz-}bk}QC;WC)=kcS^nAM?6TjDW{GWG9AJKm80q!{9r`8$Zj)U=22Dsy3>fqaPsQQg=Pse-R_c716^HTk5UH_quZhP?4@ojsIKcJ)A9#iL$j&6IJ@7Dg71#W%(bbMRi_*=D~c)hn<XWIg|e%sG<zozWi;LM}v+j(raQ~PHpZE^BF-{yDQrv0rg+~>RJ+jZ4rE9-ft+h6?DBQxFp8vp1_x4)(izU^=CE&95@<#g|#o^R(DKRxNV+aCPX3dh~{7{AhSw>_o~zHQIYb=rR{+5KJ!KXqiX`@N9yM`_>IH+ArB{o!l1KQ{Xgr#^n_)7rQ7jXzHNw!W!@Z|gt4TIW|k;*Jk~I=-!M{F+DH@iBF39dXAe?L+N9S;-wA{B(R<-}s{|x#MH%jH%>~&x8+x#|J-Ze2njpkE!F2&%~8_T^&u^=&XOwx9k7;_qBg;#b#%HdcIwsOWx3atMi+k{pk62KYp-4`$I~)_hHYs_u=oSXg}9__c`eKw*5DrVjtCV+wb|d{rN{|zr!fE{hn{zUwWYS(;K??E6=z2Rr_l{cIpPFJ)Updb4O3@pULaam*?C5cDh&l-Pdk(#?$ldcs_DB^WMW9PtUjY$KI*^#b?}~%RJw<|JhXShpV{b>G^hi3T4rLxj1(`JwNjOTa5M}f5072&$sO<7SevpA2vAs^?cjkGS|P!@Yl|8$J6uecqU!de))#(czV9ApZt&ZdEc<@_k7#_s#mn%GOs(Ho^Quz`S7nZ{JXNc<LUWP`SaVl<LUX4_j&xm``z*MeA{2+pB?Rvr{~-8G=BG_O@a0Cqw1GizA3Q%_)+a2^^g0#iswhhC#&{{{I%ZAcYT|`CZzq(>$~IW`L;c~t{lwpXKi!G)AMbAPh8M`?8EMOdcGac%cr$JHP#(Z&$sonAJcxfIqrCRzHNWO!`feQ(j8CFx8qZGpZ1Ht<Bq52+x)t_v_I~b^-g;{-?pdAdhPe^?~bSE+x|{kqWy4;JD#3z$Mc0n+AmkfZNKN+_P;Y%`}2po?e~1!{*Puc?+e}gzvtWb@1Mjt#Jlt5`L_Od<C&L3>z(?ZZ|k2Pqx~tbu5<e9`L@45j@JI!uI_s9e4GEr<JvFVc6G)$H%bfi(~>7^|I$e2v8J2v`BC{7`UU6X+x&k<Xn%3MoA3Ei`OC)#=i}S_&@k;E$l~UEepG(ioZx(Xn}5>~?I-MB=d1_Mx9cJIAlCWCRZe}+xAl#G&$88l`S><J{vqx2T(<km^X>jB(w}yocH86mw!ZP}u3jCOk8ksf^>f!%lcxjyP|CzWKef^n?U(4Q{gw^geB(E2;@0>4s5&|C56;Jrs*i8$l<C9$xvpEs^KBi^kE)Z>T<5nK6X-82_q^+yar5)>qw<S&2+qfk%D>z@xL^2D{ld5XO6tXWIOMJ?&$sKu_-1}hJ3ZgF)A(k-{CxbV{9@Zy2et>_wx?oG_x@(a!Sn4nc)lG6<NN*ceA`aroAuvvbfDj}%rw{c$HDWX>YMwp-!J^Ae&I*;tLmAx8FkEa$MfxTr%I3DaqxWGPUHLi@_d_Lt$Xl(^nBZX<NNE}^KE{OZo&K7`2PO&eA`ar`}^1Pqw@Xz>-kan{yweKHF!UIzFq&u_wTpH_wTo!Z^zB}{{7$cqw@Xxv*$;($G<-t-{0?^Z~J>&m*D47(~jEjP}+Te^L+dM)~>Dgzt7>m4|u+PAGoKD_H)I%`^fX{KI(io>*{CsecSUR->=>kJnx=w$HDmixOu+K@7aQRKe)<izvm~0=exeC<L8^}n*0Zwx$hMw-}CMG82|B{YXbA}ZT`R}PCHWv3=Z_8@@Z#OKEBN#Tc3HawANV<o*(%>r!M=hz59K&=iB@lHQn+5qDip7XuIn(ZnnPXN7Xm;<<~d9Uw?4kHG%c<ZT%N(a9^F4v5)Ngs^{DH)!EhAcXzIH*1zZ5^*^_oGY+;rp5JrXR@bLrQTb+mP5z?F+TZ%T`}=Osx9ee7QSHxfw$^FC=iBxlE#S_V$@l!I{BDKT1m@#MzTe32u9G|!0{z5ZCtcsnyPt3Nub<!VihKX`{K(J0`MiCX9O$PF{NDBLzDo}DZT`ia+Fv|<owMFN->$dfe;?5E;(cG|`F1@gU(|l1!E2rRo^R_n{89T=pLV}L^nAO18lS~qzuKwq`L@3C?<&3~FdyIMw>YK!E8n^M%k%Agwff<JGhgQK`FMV6(b9o_dZ)9&`7O`8e!(591MA~Q)yI#jZ}Lt3sXMfP_9b^edcN)NjP2SVTzI{+9y~wt_dqr{^J43JzO8Tlife-NE4ur4<!X2Q&HDFzyZ()D#?#NoxB06+cI%k^?)i4V8{gFN^YLx|nvb;af4}GXcKv_5So^Q8a-XN3Z^!?Sm)-F<`JNw@pHO{GU_QRhzcE|;yhlZT|K<Ajd0~9UAu8X@i^-3frTxc0b>9y?-;U2sGo9<&=e6&f=e6<8eEIptH~G1zYrjK%y}xQta((l2T!Zm}etOmCT)#@I4FAL(;{yH2_h9%1I|tXtkE+kl1-6~VpLOq_W;{LLj;HZsYp)5+$G7<v$2;R}-w!=MD&O3f{CvAl$*(b1`{w7SdJ_VD+h60GpA*fvd46j3XI-E1wDaQmcASmRINP5WJm1cv@%^8>ec#Xbzfbo3sQe>?gWHcE)&Bj%g2x9xYJ7H$3?6@cJN~uCxcknmAJ4Zx?-<|ShX)1vHvhIf!TZtp{(kg)I}XP8_oL@WeqPQKydOP3s($AE*v|P^cK6g9x$Q(Xb!injLvf*gy)yk1J2B;t(cph#_i(NMuYY1!y;{v0|F?f*m+M2-hF&Tvpe^7EaBV`k4tf_{2fm#UZin`S+rbYI!jGa)z>mVu62dQ{Pr@(4FQFg84~IjcF)I2K!ovvRrwHL^2;u33@JvE@79so`A^bEUJc1B@1brBO1nxx$-%kiXfcA$UfFDGM!4JZt(5K*0@D%hJcnbV7Ivt))-(Dt!UnPVWptImv^mzdx{5<+J{5(7k9RZJn2ceI^k1!U(167Pw@fabTMhH(Pgl7}NFA~Bt2;pZ5;n9Tfa6<SYLU;f=5FP;cA%usZkHJIW31}KT0iK3VhNr==qqE`J^x<_vcs?Qg3OWOxLEl~>gr}mT;i>SG=y3Q+xF7lu+z;-F4uE^Y-O)a<tWQ~sJ<z^zUuyLr`cXsLqi%Ge7YJdqK84L1ej*%M=TA_tFKpWR1pRn|y27$<-wf-uEIKb7S=;k6U29&ZHq6U3R`VFkd3^pAbUrL|_nL~A2w}74g%{9<1$=G+zNzshbNeR#>*zFC*3x(tg9+h5gs|C1<1<}%e5Uq{4@cIR@C0-S+*?JraAZAqV;;N1X0E$sn!9e{$h}C|+^>Xtp}oVAds^>IZSI|^FTH6;Z>}v|G)BE!s3@YMk&0p}8lpwuBIF2{P;sY<1hg@n02d`1^O=$=nyN@7Uq0UqO@tH4X~uP>9mUZmaB;XK(S*+w;WG);OrTx@ej-{NPJ~PH*#z3VUX8_e6?;%Q{!qnQ73nHgqH_F&iWB61N0`saxkKb0;`kW(f2+8Jp5SwG?hkTfV)VJ}s2pD+=Xdf%Lou4OqH-*sDHx+aBYX?T`D1jR<P?VUbG`yO!gp{i=gO1Y04>is$w@+QhwGD94lNJIbKd01aRJU1;&X*KzF9>!&YL_r4s$LGxmh^=PxblFus)xS<KM#iym)f%FLI7&;=>$E{zX0`dKCT^mE$kTJxqLpC+BvP`z^dh#X536K-ZDKhVv#*j#qI0L)O^`@H)<|VZE({&6?Z8TG+$-IhJW{{f=IOe}_Y?p%~Uch&7TQHESe4Tpq0eo4GHCCc#OW=Cd4pGiv7TX81qm>MzFrKj!2jdK|t8A4Sc0oB7y{u7h{OYlwA>)gH!cJ-QZNOOCMFpWBH;?8igwGqbOS{|-m?+us~#WuIkbk7Oqbv!4pFmg}Rp!}Vdaw;GUt3w#H9JG_PU^euWg)7m@CdX49L*)r{uY(y6JgXnMUgWve<pY;7h#v>hG$+fnyHn*@YKR{Q)E6EqWN5$PL+7rU9&=znjxH)<!+#GH~2sa{x8xzek`NB=nmT*(}F0>7N7u*`{2#a>e#9cY=0Czzjhr7Td(Kq0c@IrJsybyk0#k=Tx=yF)bsx#wv4}2f`D10A06rBSPh38UhF4vihZ}>iPTQH7hOj~9ezs8*JNFTZqZ_wBGX!Bh34fqW{W3Droe$2%;{Sr27;cl+k5^jTbgcmZ_BjFAlcVN6)GpCK1bK&OU$l4HYg5QecR(#Hk_Z-Hu6?v`k+jFix*PDYb%rvHRn8P{v!qe5Q^;H!!3E>6kEARq%KKcSYAD)3e2G4*WNBhB#!w(U{ZP2^nHgJ7H_%>LyCR!b?3D-hvz_s88gm67rv@O~iZVNxmIE)JEv6&8!L?4Dn!u`?KaCsGlRg_S1tBTTijX7?nVxfvvDmJK)?|hD^*rnoI6{l1jAcT)|ZUdkBiu^5j%c$2y#nUP#pbOy%@G|PG;<JruOBb{|d@JWF)An0o=~GeqRhT}>d3iJ!RFR7)NZtY3{uObYc6X<Ja;<#iXD13$uPE1$dJ|Q=p(0I16BY9HR<eqC6-g>es<=r-tcsiAEF6pGh9$2UpNog(Tp4O65%G9(&5bHnqjLN%IuSmt;-HEX=wA2){5>I@4vT(Htj=_e&p8)MyNc0{WZHL#Yn<j-#-cge6>bjqAi6ScU1@U~V}283l^quE6xTS7%CT9Gr<uRg^zArtf;l}w-;NN%yU@?!UGN5UBfJ4#hQ13ggD0R9Ly`3?+y(6lcYzzDP2k3GWi%PC43|dBz@_2BXgpjP&V}X<Mb^A<44NfmUsp5OtnDm}wT$Tj#`q9?5d8{12=7I=z<c3zbQPQquSOTbtKm1$r{Oo?G_*UM2KPXlg(7Q7xH)=jD6-y!tD)uLYH$)-A{5zQ!X?q7a7nlrS`aP<$D;Y*SXkC@SvAmQRK%gNa2%Wiy$Q|%p9|{{{xPgW_*7Vj@IPoQEFqi|uMC_M&Z{CfS_&-#mx4>9W#K$%KC~>H56*?g!MWgn!&-B|62hlZ>Dy^ScrziqS4Axqcc`dC2)9$QTE$Wos|evG=p=XvJdv1`>GPs*qm$sb;f?50cq6<6T@CMmw-Lf06T%;%tKg5|t%UHW=o0u-cmp~S-T*IF(H6ZOod{2)KewZ`;M?Jva7}86)`n#*ZDM_ieg&6RYgc}?lc1uCio}ri?o`oPMJiDR?==<URE$xvNyT9mJ5?N2@uiA=Do&zbXF5L0XFpQ04&4cVNu5m`FC}*j*XoSE#<`t*eiLoFpPVYRwIcnf0>{xO@$#$45z>Ezvxek96{$TrzJ>N2rA_zKj?U!f=d%gay@iOQ#t$m?t2jpNQSqIM&8Qq#RnbUAQ&f&CsVJnPoQmQqif}BPO+^6}dEqd}qB-GG)G0?4!h2oCdKDj|a{LZD9^OM+_h)MBXT-;uKK~i#3emotXaTqs{g8HiL%kp9<9+nEDcp?^9*d5L$HK4E=REW~4|9->x+l5LH}Kc^$2dL-A0>`4r^o2$VM2H(`Wd_vUWcxS*TGBCci^S)ICMNb4(^QJ2X}^3(MF-jUK6f}R)Q<SiD)S}5spI(!Eta7G$)(`4xwQ<%($9A*%<3@7}x!w$bR0BehKe~_n@2LJ@97qBX~3XG5Q+(G5mTcvj1NvgvX-yha&4lxEp$BD6+1Eo1#@hk+mmW6)g)_h0CD{p~yZGE{@&;7l(_W`QajP0YW%0AuQ{+x_Tzws-h+#T$d28ObA!Om*YBwa8*LM5+Pg>UyhT>m*X0Qa5a26u0?%0u15%`;LGuCv{R02$H;$gDHLj`q7qsWt^_Bb#bD9AZ~~kU{V$|BADpoW;XerB-&OpEUPu3fufw_doYc)t2p2(%!A0OCv?81Y--b4XZ-X}x4S9Boro!iVmhMHrg1;hXFClE+e}wCymEd}C1vCM!02f8`!A0RbXb8>&-(XB-9B&Z97gd}?e@6d+e};cTe}~N+{6q-<sNxwFvsLsVga@fu%QdzW=cp~8SwjucPvC(nW~t~+2v1UxtlD2fMP)*`IGP_W4&RK%z&FET^skWSF#Kmo>o)jLcq_4u{yhWFCWOC0|AN1O|3>9{e{(FHl{Vyuv%&?@5^zB{5lw~@;i_T%o-A4mO@?d1HPOo9$UC5D6|^#31ulsehfBf*(3{}`a27NSXMry<zA}!N2;tr6R(Ll&i`dFsZ)L0}p?%;!tO?;qR18runh>6hPK77K@1q~U@54I?;S1<5@CEo9`Y$Y+BdqxvoGYxgFq{j%1uYBT0+%O*Q_vc43cL)x7hVQ`kA4P={s4auUqH{o7vL*|@C`!v7Zu;2`_Z%TS!(Skgg-|=gFlDgLhps&f*TOR)zBJnHMlfd7B0)!l_rGa&>V0aoE??9$<DFx6+-wd`U`v(UW9%CFM@}mQ{kzstzm@lz33zGy>LfDxD_GX7aa}vg+~y=bJ5B0TzCokKD-28O9-DscfjZ1i|7UTB76hA28+ttHO~m)Jgnzi!jWf+a8a~;IPwe<HqR;HdT2^G@>~<%j4p$hv3AWfQTQ}^AsqSMK=@zuN;vX8gRuE7LO36KBOLkeLO2iKZwO!G{4ek|_~%Uf;b%hlU|9d`FS-N$CLH;GKzJj%AKuU2FyAc*zm2{Xj(is(+zxF3w}Z|1A;MMBYH(FJ5iJduW^b71g>XSMdpPoZ5zdOrJ~7WDVe`xq{sKK4iag_lXQPWkk!PatAaoc!jJ+|45WWZP2;T!YB!pAYR&WYjj}UH+_Jv!+{m~I{e^`D`G98_Uj(|t7--MT|cuU0!LU^%?m(h9XTkt&ic|v#&x*VPZza7%=JffeV%VBvplJ}tP=qK<e<ZMS*z-!SZ=!#I}{;-1nte~ytezKT8n*K~9UJgZm$0YnJA^ZwD4}JxH0ev3spkjcEPUv8`6Fd~10*kJMhr(~7=ixWuGw46?8Tc|GoGq;Nrm$uS;aIc~91E91%fO=5;ZpFeXeanqxIVfQt`9FFgm<AQ;a%`P^bGtpdLBIkpNFp#!j}o*U(u8BukaCcC%luk9wCI^L94^>z;)3wa9y|@Asmkug5%+w=uL1=_$qTEb90rsIuBoke??cqzrvpq!tbF|;P>F?(82I?@KfjjcsTkXIskqUZi#k)Tf%h-;X4T7_Gl-#Jv<N{3J+x+4<v+Vp=UyocVOY&=;cu4Jz3biOAE`p_GQ+)dG{7BfX0R+@9M%O(Nb_J*0Fid7p{WV4@Z735U!0bf@{NV3E{=)E_gA#0o@0iwQj!a7MAbAx1tBoui*pmPw090C-^FQ9li?Z=64^$dC|+Tgs}NtiSR$1|1})>-HPxj^hh}JyBOh3=sR$`R^gbqEdQ_n3!=y$`TNr$=l_t%|D^lRDl&hvpQ>g5kwv>!+2r?lp&0c)SzP1fZ!m=Z2ma2GH2'

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
