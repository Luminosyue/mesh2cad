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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b5aa31a84cc746a982228827c5185ac3/part_004.stl', 'relative_path': 'b5aa31a84cc746a982228827c5185ac3/part_004.stl', 'source_sha256': 'f746b65cf61c619d43b2ca9bd758561ef14616c14611cab46552629a20c3cd29', 'input_faces': 828, 'input_vertices': 529, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.45114636421203613, 0.22403736412525177, -0.1344861388206482], [-0.39169228076934814, 0.27372226119041443, -0.10146275162696838]]}
GEOMETRY_BASE85 = 'c$}r22ar@nxVF!bGbkBE2b83sfaEwz5LmJVQIG)^lptZrK^X-VkR(Ae3`vokmAHch5m|x)k{JX^DguH833tBvo<3}^{8fM5yVhIpvu`zh`gA%yXLoHBlRQN>N5AqrWvV|pE>|hX5oK_)Iek0C_3qTZL$4RR^%&rBvP5(FGCrX}v-*u%dYrz_pu({odbN)$T+v&&a>w$8i+Kxo>>k%Uu5GtA-Q!|ANM5UL*IpeWd9Qcd_UI7#zDSu;6^eOZE?Ug{zW0Cml}_3)>GX+s@r}**RTD3hKR*6(dGR`1<on>%Q&#S){`n^PJ~a14G!LwNBbtY5o!nsM#TRQmdFw~(@qcyP&R@$Hy{>o3G0o>+*(-UVK*7i6rag|y7rv?O+5glAE2n<9ohy!NKK<(6#Cd?+d2XrIe*fAdn)mD&%>yrujkd>U^6}UATIIJK);#ZWt3AGLhph6>&vW&@Og`eq-o)ii9!RrV`=>>tX!-E>2eo{Q@mBvN%}xIV_WZ2%)cC@>U+2J2TE5a0tNqUDeOf+q7ptD|De@vSwEVBRHYCn{Yf|n{JdXd#8TY{1y?Wi;ovikoJdo-=dt6LT`vajbqvieNq2;OeTlaM_LF>QK!@95V1@gtI_gmw2?MG|=goacIMf>06U#8igcwE9acWZv8x7`mWr@S+`cC?+ryFci4?{~A>@8+@hw4X<m)9XImrS$}+>bQ?srRAUbPV?mRt?~hKXZcud|C_HwbKi4Y?d#IdNpp96i-a`)J<jTXHy;?Q^^cktt>0ffUfXk|uhq}NvYWO1zW!GKnA|t8wlz;o9_UlYnkW8Bo2>S@<8Jbu1Fe2=^JmlPx|=;)`+?loHAct1#3bDZs%_Nr?d$9KmOisV=h+5pA8=wf=ygp_`Os#suG2c}?e;V7q59uy`3aMB-*|hej#ra!wEUf9R{#6Sokao7WACrm^}J5YC-Ye2=;jC0X+Jj`y~)bo?yT(}c`SO}aC6O_^;xw3mPd75-dd~Wo6OVl)n3zi=wHKp&Ss6HL+)$VD0;tv#vYyjv8%QIZ7a2%3uo%MbXukPKkKv~8gJ2kuiHwkf74)l{*ya5v+8_Xa4?#O;#O#WA(gd%22DP4vew_^e6)NpuvGJphg<ClnB4c3&XW?~Sh;y#1d7Gz{P}o^mY<o!UPmUMn9CYRH}C(nwT?m~7Hj>jp0n1A$$b+BXn&5Wq5I*OMOuFJ*@VRPyLrz`35mzuZ}NKA5)zNE$(_1ItZ_8C&p*sskKPGiYdv3_NwDS{d8qzyYn=usFVy-g-b}F8yUBNjtZ_GapvFjRJ^E*SrTNG__Ifw@XPfsXo)12gcPOCc``(GJ7cY4zE?~`1lRLi8?Db3Tt2D~m2g1QGwf?eS>pXnoMksM^p6`Kdo3%ZQ=4(Few}iy=)6J92Loa#Y;Tm0cc^Yc{%jRjm{7GwFgvgzOC9M6yzk05=zs?A2|M7l1N9*Y{#y&?S$<4fS^ZFC5ehzI4TIUKgpMxf+A3}fptNpNbw)MPr&lNjoX?g!RYkb2yW?APD_c?2F_Knc(?{uB+o@t#!Oh0({&Cq^07PRJb=;!Iyx-<P5B=>Dwpz|b6W8H_3Ow)YrLTi5dlIF}GlRHZmS@Xv^Io0Yn)1ToJQ>}3ieV=@5v^{60Sp9F>={rB!Uf1N#jfqx!-21&fL9g50Yt6SHxo_4|>wbOr$7}gX%dPwMCe6)yA@_Z{%D&%Z<L&cd*+2BUsXn)IcON!+!(;5XJ9R!}9&62W_c@YnjFum_N7u{E<~l#~jnaI}Tx*|n^SKMHeKKhB_gC2aWP#80x(8-y&gURE&k?luA9B+k-?#g9d<%`#^6l1H`=PJIaLqG3Oh|lRCJ&S=X4h}>y9=}*&feF3!_+fxm-btioYDCcF8!%h-tk@5@>M^!`^S9lAa`z6u-E&m!!$o$%|2hfHdO1m_LZ*Fhqvtf&{F$+Qtu->XT7`mp5<D<`CQQGL%r^X)z&`aYZkETanI)_|LPn2dD?P_U4CjtU0>wRto7DD<FtR@YLB~K-WhD4ujn6>J3qZ*&vR2gzUJfWG4(T!N%Q~I&pFE1E_by3zOI9;^1e@>cx-Ok<2Ct5@zy>W?lI7=hx!A32IzG^U1sew-hut?_8fbt<36;n)-x~0YQM>yi(gyqbo0}TIe+H0bH?4Y-x=P=8b{}VXRDR3SZiI^&6y9T|C8os{sc$$w&sKTxy<B~Hd^!9<mMb==B@AZUXSg6H>dyI&r_4)tbQ}|!Q{^84XyR-mQONI-114z+aZ(p*k-MZz_gxrKhqB;H~ne)!Ocy7(hq)<cidsWubAD#DsTG7F?s9nt$7%l*WK!8(?9-&-83KG*xqNz11;aO+hg)Zt?kcKCNJIo@%5Yiym$7kkIi{5yLraBdfnnzLXXSc`Jc4Bd48Gp@cG^Jzt7~%6Ej{WcLr>=_p7DvY2Lo2y|0?ww5MUdt%-B@Ig+Hj+0Wg5+tkDQHRBjwLe6^|_q__a``*T!-%NStp&9q!%C6SBcK7*pU9^0yP4@HA<lL{jFPWVAZ`$ML<~c%pLK`|;^W3y25Z_7jKFzG>g`1oCX3i}pH|J{RL(<&LhyRpMQja+gyX(=E=N#y+$E3MA&u@R%zAp3D<mOy$#?dX$dCYxpX3F#4%w4Cu-m&K!`<2N}|G3XDQ{Jp2^Ipj0%un~dXhKKL)3>tDZ*G3Ry>)(bbK2uRAIaVE8khO8xw}7`oP8r{J?^-$KX^^PwTpFbG`ag;&b+tzse|VE-q7-#&)xim4%TxpX>OjICU@VbF}`ljdoVK(ljiR8F==`8d^EZFTvqEDJx?B>JqvnT=h(pESS|lr8|ysa<^|rdp4V<p`<)N6+PP^b`<2N9t3R;Ug(=VbF?U@g&CUB{Q_tjK*8KOAyYHp*?AFie$J=W?gGXBH!b|S1FSE~>eAU1Dd1U|Fx-L$)(|W45wdR|foBh+A8%=ILU$ZWf=I;JU9@u+R&;R{S>GS1WTkCn}K95Y!ymFsM<Yv4~KfAekKX2Z{n0olRz<=r|cc059=edydx+ZtW#ax&7(*J1>`;uvo&*Yc?($8PHit4(!<kvjc&ID`zo7}ulHqW~xxw{{doA=x9dB)_tw{*{S7yb4+HRrBB+t}q9Uz3}8`=9d6Tlai*{cUSqxbHnoZsxhkomSTV<Nn+#XA65>)6Y)bdfJ|D@9Tc`#T?DM*U<8(U$pjTH(yyk!Rm)@<fD8EiSH}etGebFi)njW=8m`WvLm#f2}g9jlRE=z*q@^x6x8y&J865&`}x$*Me}gRqWXR#^<Ev{49`Y$f6aWF^M2UP%Xu~5+)meHmI9i$%BAl&{w|@<g=e4E_B5-f?SH0~K7UK*)qFx9&3Vu1tDQsh5>2i0&Y<+#{@ZQrJeXX|KQ~(MtJ-(^KIf;~$D`#_6xQ7Q9PrZLnvdwGc}Bms=kIIBt?{C~@7`b0+?%PwfoT3uQ$5!?<WA*i9!ft`&&esTMDy@JRie2s^Cf*xlK<lI#N%%25596n%eT{?k2p6EXglkkj^@EpHMF1C#Ok_kcuLF9^4a6k^rW_DT_vsOaw&Z-bUdo{lq+Gi-{j$<FI(+*x*XB+-ZEDE!`*+0=H{Gf_J99JKkI$PG_db$#SdD3?R>kRkA*Z(eRWUb@(y{pL!sz(-OrDw;-k6$_2;ej`_69B`>k8dYJcd$X06BfqTT+R8?>Fj-?Xk9&a+zco%gLgSa#|0#PieS-bzcf{u7<-@v8l`_FJm9)_8fFe5HB5R=O_gT-4`U^Di|o-NG6#f2X<Hp1~RIc^mvf+hg8?u}*`_CTRcUET{c;_6_Zy)#I)4b$|XsZsxP;H?PT=&+fe4JzDcCTeN?8PwqQ1QrpSTSps+4YdcSj(EB?6omD<~d#KhE+GW>s|D(sQJO2v<wEeL|wLgD7r0cqLKP^A}pjD4kwU71>?_mNpnreHhXdWIh$QqZxtG%_IuPlw$<L;|5aaumu*BY;I(;nK-tK;;&Zn!k>$GYo%y|hx>!+A9@Dpu>iwaLoEv;10qdu?mH0`uCieq*%%?*w%{E__?_rS)~Z?)|~%#MbsYq96Q+n`-}f-nRN7c)E$^yk|4>HuO(@yFY2CFKu0|pPzr3@eS3ftoL<jjy*0dDrosOe_Gdd+LqJ$TV&U~Q$1Zroy%xFcc*GUFYc(%k-;UkpVLg%b;0`_lbe2U=lO>vG@sqb>bKCxFX=c=YGU=9cWiO3KgUFC90OBcu=fYk4?lYKzS2yv?#p{LpO!c03i{LgAiI|5obOzGNArqlwfvOS*5{f~)ij#(^Eju}8#-R~Qfhv<guVYXPNDaEyt>s7Cif@Qvic#|EV(t`+<xeL?^x8Ue5d`q|EShK{YEtRx87)tOJM%>XdbxnxAqV3`AzQR-=2`T{h@VNqIt06dTSg*+ke-3%=-khe<obg^1avTy!xfAo*#a>p!F|KZqJ|J&S^d7=RWjvAmu47-#BcIV<^)J&Hrj^jiWE?alPM~#r64;rKrx^T*tKjELW`c6?p1sG&j!|=Rhkxhm(5?me&6Nq?n$&@*mObc5Pveua`Vrs-(T%O>UmcjF;0iLF@76xA(XHJGA|)PFw3S`2KcnKhHJOZ@!PVX+0%xS>xrKx<#-1(-CXj!)w0PaS0!?#?iZFonCiMcAba!i|KX0TdVyr@hPhx{NJz9d~r^z-<&<Gwf-wVS?kf{{+W5SAI{H@_D^8{D!cy6SGE2_E46%soC%4?%jDr%m96>X99yAz*SmWY_nYtRGR>bIZLPb|g{9igrypuRaGnX>Tx4IDb>Ze&f6@96b<zHLVu9v8YFXujMS_}}-`C=N>nlE6uX`tz-OnXwY5AiWwSRh*(0(X8Q}e57qPf@fbEO$t&#&pDd6@nTSDazh<EKAE)uwAdyr-XQg62F%9;|*V+7DiS&ni%VijK>BSFGo3Fm{60KkSlqUJbwZxt7o4Xghb7*Lvc{>2<Rti{`;Ce%;^tjn(U>PND7Jx<uCtc{o{0Enm5^J|72-(L7DrXn%UmzDjQTGra1amLESt+cW;W&VTc{c*dt%PvQG|zwB2gciTV5r{f;{#BP7@9{QYG@Uhi??~8l1{fmZa`Kq_A&r{*AhgtXKJ@mrHXg@9+s@KhsT=RO}Ij6m^<rkiej+fWW+r5MJx^G^O)*rkcqx=7nfjTaYZ|HSr9M;bf=lfax6J($9|J6s!H{4*&2cOB!d>b}TKOg<wTk{9B-#lOL$7%a7q|-b{)y>iJ9?kvUSN0_??@QIwD(~NLFxn4J`W{yQ`;NBK=S$}9+7CPPMe7N&?!4K$Y5AL}^}a3?j@A>--$l!3+N0x}vbN6uLY=ie#qMeUR9LI;KPz<9^3L(-yb7Anq2y*=_;=jada88L^7U@&{<bBho;O;y(e`}zr1rzM?%L0NT59<n1MT{UHrMw2c2Mi*eD0gpSj*4Jt@V7KQOA8&BWr*5E<U6Eu&{yVoHxw)1~$~S=B<-#tM2phbu@2(Rol;d{_wWinrFLj&4&<qa7te7=bsDe{*zEk^MjeRetr)jc%Y`{U*^*CanDERgZJDkR{!|T@3p3=r0q{XSjX4w+i5Fm&hJs1ad*hgdI^uMtDkprmSf+`t@F+7=cP*OeNEhG_kYde+Ro7zwExQ%*8Q_iF)g2~lhvQ07DY8*`<m`QoGbiO@@k$z-{+fk8eWuB^L3Z)aao>2+sV%zOg$zK=cumjXMc0nWY_%m5bM6YKW4Gc8^ONow4M7hYhF!%ug~n~-lG{A_j}fLgTJTMd|OlPXP!s?JE=5ZHrC36$x>?jf6Suml;0b4vU@b=bE}!Rfx`EXM(b%&RLehGU*}=5d(qtgVks?OWw7q6)o)qlgQFfq=a28*zqCB(hhUlc(cHN<UCZ})Q}ZdmX*+LDi{`<1T50{W`e}QTPl@K<;mtHRKaWT=S?gceK<9I8H9aTinV|Kotf%FRe52>XBI7jwS3h4nnTG3rHLkkmXZmaTPcFqL&b=oGXghfi8Jy+Q{6=rh`MpQqylQ%1nY(NK=I4DYD{G#wtClZ!S%3d<TY1e}w$XD%=id6<*;7{A)2OYsXYT}Uzwc?i-$lbT&o_Z}kx%PcHq>gruR&fdzjerg#PdARBDZy4q4_1XAN)DB{P}*`&Oh(y`1Z<bwLdhav-b1gC$yc}x@rAw7H^4fWc^jioQaESH!AEnqO?vnr(@ehe^Mf$d>McIpOkbe{r~kRCFM(%|G)l8$!8wNnHkYgd@}qYJ`SG@kAs)s%ityO0sIhr06vd|FXBgG@k{Vk{0e>vz5@S=gnviEC-I}O_$K%yyb}q3jn9O|KZC``!(YQ+A>nBejm3xI<KbcO5d1UvGx~7|67HL*ulpk5-Vs%bs9r>MaX(xaeiI4D;l1HFIDmf$f5`X+knm`H2|OBJh=ljz2jIQ%Z}@rmZ~Pj59zM@lUQ0B_!vEkm@vHDn_y&FjzQWkwK*E3Fzr%mQf8ZzKKj1JD-i_~scQW3)k?<NMycGWmUJ5Tp!e8Rk;4k4BNO+>>(Hs)~93P2~g~f-#BjJyb@CQh^A3g-`2lvGL!ad=RcyCzT4~y4>JHkzoa231~EM6Y20$0RK!QvI*if~oD94uZLt_nB7>%&dpws;#@{9U*$+z#&oi+6?F!5#2ka0j>t{sH^}ecA)>3HN~8;~n9S^jCW%9D`SZW8hcuif~2l|5YUXI^G0s!hODuw}abp53eKPmUs`i2W@JJ$G|aMPxx%)+4LZyU-A3!Mf@IqAHD}C_o#$3;}2kwa88d(I5++f&g)T6g-f1_?}g7%_5mz@78Xx{&%t{m+Kg|)6X0+0J$M3~KwW$AU*SFQkBR!?M<l!(3IBuNga3h3c+{njQXt`f9hLCkj!HNg63&EYhBMQTnUHW+JU5&b&W41udmi<5b|jnwe+m|V2F?NJLc)3Q{IGZdI1lVa!q4Ib;pgx|ctLo7<lYZNbP_)Wi~j|mgs<RPJjz$#3?B7Da3Si?fP~ZI1>p2>T0B3TpZiRUgwx<p!D-;scwRU!b2l{-{*5^;bM!YPybs?C?}OtL&12zpavqInEglcAh1VeA)%a$3HM|Pn1h0ZuBw8CQknj>Dyb|97?_mwBM8eDP-S9GaITHRE{|EjVc04NKl(?*ult}n4nXH++NcblHH+&Pmj)cRwtSjLW5e<*12@-CMgquh7K}3Ti8jFOFBjLq(dw4NC5ea{WH;0>3|7S?}DiXeikAQFCBk>XN2--ao3BMjuHM|Pm1a88;RYAfP@#b(vxH8@zt_;71ggfGc;lcD*M<o0S5}t&F$06Z4_*i%>{W}K<KkZQom++{BU%(f`BH`yfD&eB|M0g_oE-VthLv|Iu1Ha@^2^Yh!!6M<}9+mKmo=0OQT+*ZN!6o<LBVm#77_!&lG4LCS#`O&({7OXcMASN>ruZvxQ@9~s4Q>cGz^lMj82biDxIPlDhgXIxGY{$^;kS@*Z@eSik$E8e1wIe|1pb8iF%JnZMZz2Lxv=;Kcq6<M55qg*KX6(5fAGEV4LlPpo)s1e|A}XVMZ#wsmGB8XJ1i3Z3C{tGgulmg!MS*L3X6nyIV#~Fa4+oT*(od%{>6Fpd=(Z6A8}N|zdI`7!jvrp7lw-<;V1Ac@DuQDM_r!5w~_E^{1hyH06q;LMZ(*W@OMaf3%(y-kMF?u!{R659q=*y3VaN{jLSLTGM*kz&ollq<%BQcX<(7?1xF=(9#0LY<~e^J2_MAw!Q%07^j#Eu5Z;QfgT=prx5C@-_3(P`e;a-b-Uc7WFT<C)pTkJ_5Pku^z&#wo55fm&$02+hd`|jC<~e>C{t4cJgujpIXZ#p`7(UFuKZb-aM>HX#xe-l5!c*}1u=oOa3Op4Fe}RPOM6?25jW2*#!>jQ5@O-Yf3JI@_XgMCl=fZPoxA5_Zew6iygnx)Agm1-vgulZR@E_p>_zZp=J_Fy5=zc^GBD#*>hHq2mI(`Jc4xhk(fW`N~C*WU^@cxJn;@j{&@H#vm-vjTV-uOiKACH8;#ka!W!t0UnhD3d|0SRwL!rSo#csslgKLhWB&*Hb?v+!Lc{1ATtKZH{zQwgWQ@53VD<PlGmOx?jHckt`5Ncaxf3HSv4eg_Gk!uP{wJWe6uUHCTGjLj}2{0$PG9Z`o!Ge$@BDH6`;QGe2-EM6MU2$w;^HSn6Scni1&+#CtNgLi_(2f**Z{qa$7e|Q8w8y*4A!q>sG;I()>EdDLL7G8vemm}eo_<C4;1H2Mmg>Uve+AD<3-XgpL32#KgJMitW_&(30{ZrWNtHS5-v+zBS?wSAM=iqac`4_(ni$8?_g+0ks!l`kY-@;iUN*hroJT;t}HINAjXTVdy8Q^qyayT8F9tmem_GrxrXU5auso*qlGTed1Wt}ABd*NFi^;7UI_%ss!1>Xh#0&l^;fxlsHZ9&5Gknk9M6g-N#I|d2AkAyqponY}6aA)`pBwP!x35%D8Yr$oaa6bG=SX|a~KE4+okAw#z;huO0SUd*q3Ac-=F7Cr);IeoPJO+-Tt{O<VCH^Vg68;#Mz2;-S7fy$SU&hP8;x*ux;p#}Z8QvUj2FK#>z_D;2ygw{H0`3D3N5a$bS+Mw8xJ#t{bs`!N(d39GL^K}>FGRu%knkupfqy#y9*R$fhr*vD;aT{6So|w^7W^d=UWA0rI~-y2Zb#U>{}En-&vzcZI}%=jFN7CzKjvMNuz4RPyc!R}(<15|(R92kJRP1HQICjbN7N0U3D2ZVHzZsf3BQ1ZpT|4H&%;HLa3>@@1)l~_#m##;;dS^lcpdx=5?+r_ho{r-^+<RNJ{#Two6k+c=JS;B*GM=H?*Yfbm5}g@csIBkeI#4}e;O|i7pL!@M#6dV=i$6?4kVlhFAC>@pF_eWk#Kjs6WobD?VhOLyCdNl_*z(e4J^JI77xNR;9>XzSbP*LJ^&sD$KrM1Shyx$3NFRH)x=A}C24m}Bs>V80ngxigYZ~b{@;+P9X&RRdtmVtj(ePpa#}n$oEFZ9mw@xZrIGNPNVo+OZia+k!gIqf!MTudN<0Oe5_WJ8?BRYKJeBk4OE@zs=*ZuYI8G6~0unBUgkQ!B!qxG@ctN-z^%h3LPa)wa@l<ds+V><9&WePy;pyP)ct$)OoQ`qIh=h|P;q-V~I6eFfo(~o;4L<{yLBf9gO}Iba7k?A(3-`fWz~ar|_ahn-Q7^m?+=nv4@8XT{W^g08JpK|~9)1?j1&gPIpM{^m9ry`21D+Wc_re+ALe8UkQwRx{MZ!M30_=n3j3Z|rIp3HwlJI*-xUKW(Jk%Di0Jnu}BjKueF<AU%xGG%Bc{F!xA>mezo+ZTV;MHOA!f+k96cT<8e+m|V(s{HG3!D8}I0v2;7SHB9+S`TmI*;bM+5d&*`A`7QiD!q!Gr~FHEO>G_3!DZCXTsCN;?KaD;QUCq99{+%_rq^T^lC(H@N#fD%CvDFt(i7RxE~V!5D9;TgadeASiBD`J_K$Z+4veo)DQ{3hS!E)gR3E7Uqr9qb@1A7ZT@{7B-|JYzm2zs--f&6-C*%SaCdkx68;nke<Ejed>}pu9tgjOcZ1)9-@;qNt?3KlR(J!vA>1g&lPp{E|JVQG`O#M(`hZFNKYUL5FYRCBOZ+dJN9uBasjpE?%IGsGS>!+249>`>6z6{ceF-Zw'

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
