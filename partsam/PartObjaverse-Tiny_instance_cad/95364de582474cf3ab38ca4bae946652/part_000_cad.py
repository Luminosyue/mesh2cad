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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/95364de582474cf3ab38ca4bae946652/part_000.stl', 'relative_path': '95364de582474cf3ab38ca4bae946652/part_000.stl', 'source_sha256': '2f783f230ea5f6b68ddadf6a1c9e1bb738a9eb704fe027687607b0bba6d63291', 'input_faces': 788, 'input_vertices': 458, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1205688863992691, 0.035457465797662735, -0.12197060883045197], [0.06488056480884552, 0.40626436471939087, 0.18748989701271057]]}
GEOMETRY_BASE85 = 'c$}r22XGWe_~mC2Ib$#w5HOe^au$fFAqo&CgUDJTBy!G(Fl3Pt!ida}gh1pVG8%HuU@&n3lQS4>j4^-p``()M)m_!q9j>q5Z=ZU<>FMt2>FL>W(?GA}*);i=U;D6cZmxdCHBCi&Et@tZY`~!Ip<x3{_31a<p=E}z{<$@}ajT!2wsmMjv<ROrVFN=4_*Bt-s)hUcl+b;``wkd1Af!)l-vM31lwU8T*TAqOe_*$eeql+Ui&XISE1{P!T0$SC|3Cgqn^Xm3;q3#7Nop?$IqILJR<0AXmFgYW!q<KJ9a5joj63Hk)tW4UZ>DYy-zXnFMtyd@X#`)3etul}&cQjR;(N!6h@UVV`JG`2Q&E1*i~UNCtwZ3OSEJTIJDh`Wm2YwqpPOu*h~qZ0;oIw*+sG4Ct!JW#uhqOL{@POua2{D_!*|)=oxt}~6km;ew?pK(!>^*AR)>tUQSLy1<e7f~=jD3iw+`pmKLvcfc?!v&@$ZGuP9OH6e5un1kk|iW%R~>~I(i!Q*U}7M2`zbA{AZcrTccf3IG-;o#P8Ma6#UvX#-aT`ErqXV{kjkJ=yZMwj&oxId{@0`(*76DuRuLc4S{dxk2;9@C)`8*ExV88uhe}n>fN_n2c>pw8~Dbhk*L43XQ9QY=U6`}UpD7{_+zS7h2J*2)Mtbb+QEpLzYO&#^=>cx0v}O--FUwon&uLGm;VK6w`UpRQLn{=;hRrZq2IM`DOaQ2rgw#JuW2Lo8S!B;>M=YBzVrP%X}4Qt=HPh!n!q<IT}FA=p<~EzwW$i<>Yh`Mo41PiWpYYAgE#MyeoVU%c{6<8gZk9{UB+R~qg#<L?I-xoCetx~T%7{9;P1bl6My^!^ouk71LU##4uY@u_B{=M^1BGMLvT2JZP*ozH)GIqIo}o?;9E0>pxs=_3vR~uvJ`}G_ndeb<-J#IL!QT9ccXlnTgb0}Np9i1W^9A+v|pf}#`~aHv`dAq@XhMu<@!xF9eM0x!SMCMmyySgDZ3H<u;$e+_{na_IMip$_>8&*UyFQ~h<g5(Zv*_PzexG;(-?2&@wUkCbZ(XMtzzUlI$LP7jE~XqotFlnU(B-GQQnm@9KQW>w~V(NA@PYGzBTs;$-gx~+Tn)39Cy<$j0fX>AGD`^p_2G#%cFl?w>Patp5703LLYvS@!#f$btw02fcQbz&%n=F5#vOUs{-HnH3s9sHS-keZ-gg<?`+gXu50c01e9;{F#+wIfAcZq`LJvk>Xm61eEoAI@|%wXhd`gkh#%*D7Uic+!+c_#9RuHr?}2_X)7IaCzlRo*{C*XVpgwE-cB6cSFFVlA4b~s`tf%e$6u$G^2K1wGE^Z}0zdHh7uW<<Vv1cXUj((mu1iqye!+3MGdWZU3g|bWes3S72`fWyjSI+d3e?vWKw{)MTqkWS7xgCD(Na^<!8>JoMH^8^|SCx6G!Y|@ajS_#f3%>K_6!@<2f$+_Jsn4Mux|GFz!Br_x%DX~k9ImW~&wBEF;<wv@_H@l|itAVV_?^^eNg1@4^V8QYsOQ^^;@`c5>(>m(vkm9J_!!g~F<tIEFB3K)@00}iu08+Ayiu#hR^(}D!q-a;!TIXb9!b00u8+U#otvTkou|^uxZ9}1cTO*ccC(KAS?Is@c_m-6esbS@_zUV~cl{0Z)h~ymylY!6oQKu+x}3+7E^@y<oE_ss%e6wvub(aR$)xk^abB-S!Pi!tk@g()BnE%K)f>JU7$@!4Huo-1-@f`M${S-ZZ$f>}g~)N!2EuoqZie|yI~>Gzy@>H?3~z<&*sk_auA753(7*PsY4BY?o|kdD_aw%f)A1VTtAC7xuf6Y#b}$1sqdkr7{op&_dQ15s!=!x{cYtqoKPTgAW1QsaSXlDUiaC!w=kl+Dw)s)&({ieuSNXbf{kGP{FVbJeZTh^(W7Yjm@~r!W_AxW<ABXzw8;EhCH=ZW<h3%zLPcx)H=0)Sq)}8qN`rGIiyF+jIR__>$1MA@v%p+RSn((!3JLG;>Ho45#=YL1PxpFL!aqB3I@}_kLz8)Bg@oCrni1BA;Yzp5wCLhL$(e>vwD7WA_=24@|ewk-l&Yq8QW3P$7JQnR^J*{fuJh~r-Zx_=q;Cy%Y!Fo@x7$fD+pGEn9??*+Z!MD!UKzY~v6_`Jro$q6QwQ|0~IJAeCk^A$pjxz6l{YkEuUCrb^dZ;aY=gzd!o{cozA6!$4!Z-6&#BrT{&kRT2h&+-%Dvg}i?3r>OcFo6pZ+MSIee`j~SK$1H8RF;dfPQxs2tq&T=QqWnomWmlJ<XlRF^*k>L*Z+SL*@FK>1WGz7YJXsmm$A(wK&>MpS2Y2ZOwZs?KZsQ&+y02fv*K_$N01s)t2>0mDcdhy8gIc^u`YHb5?<Gl&*{Ob)9G_*Zac^lIK%r$zQz45Y+S17u@IVE7LBbUtTASL7tNz;G1XP%Jtr`_FS~@-ltOj?Xk<q`*{2S<e7aGzMgr(CFB{?8hNbA`{6r>%#?LVmg$&x_0c;dPp8soAEWUfvi|6~TKv}r`qwV780D=NQR07^i2Tmrw8L;*V{EKk7l%<Fv(Q(pdtLw3m-=kDFYDViWfMJpmv;x8uX#8Q?Vz9bmOMF1UxmMHO<k0?{*-k=xoC_N?ZI8Fll6$}@b&b2B~L?N>94fIR(tlNGuN6p=m~%LuEy(SoEOQ1b)a>)s`!Jl;JC)_y)#gLZdUPE$K!m>bE}cxH7gT*?R5nl*GltD)^GPltU~$j!=(I#h0$ow%YEP*$EsmI)H@ZEb=#?M_*#IUjE5D!Vm)lxoy326NZPZmjd|WK{|NVg<84JbU#%GO+r6v9*E=*s9&O$N%!hWnlCoatnNjXjdp=`+F?=&fp38qo{o@y){>HO2Xjf<cFkHX-;83i?j06k58T98Bv`hDY@O)v^HRO3EG6CaLf7u52LBlIGd?O$T^>AiiA?x5zUza1#0UPaOdH*HH9Wo2Pb3-WZTh87uP~K?TSNw8Qalf{U&XDJdjFsRU7b8)B?d1Ac<oPA#a?f#S6}gM&7d!S2>ZQ+ZjrEu{sjNKr%snUf?d8X=;kfx8E`sk|A?Fb`Nb32dB|h7&7fPN2HD%uJAD{3a|C;|VXooDPaa^PMJjv6yh|HVy$H{YA=1%Y}?`-HVBcvamzl?jn@Lj<R(f-bnUUI*^R#J|iV<g7EQT-b78Cx^JH)Dci-gr9->wnYtJ@VO?yrq9*y`|i+=J545i*dfzwDOo&&G1_C{8#rW`qwPA0MEJR^Iw-D&$gR#pFOz%_kDB56!@;370^D~>C5swJ~3_y{3k6?Pb+g_%(LcC!<NW-&%^a)4L&RNxts~U9+XS!leas@zu9vqo)^tW_vJb|e@*h!*Zc~howfbP#rFypzxF%KWBS^n@|<zH6nwqy6y(<)KSy~h^p{1*ACOhXPyc7Q4_aqi!FP7*b{(ICc7;IK_`=uw%Y18Q$&B%4^-UppE+%09cXoRx_m}1`@f>M9eIWCH+ljJXD0vpX>uRw>a@`e|`^ohQ^87lchumlLT#<F``H}E7Ex9}|6xk>F1Jg_Sp6igunI%sAn#tkYrJG}(x1LWHztD>X$XETo^zZu%QvdzY@LgNJ$az)2k9o)1K26G>I)ZjEYp%t3u!3vD*Xj&Kd%9ka!@O!$DIj_7`^tG$Zz20We?G%H#X9%|?d-g9L!RFg_rSMfQvM3x`4RJpHENvrrSqbHUC%~K{x@mh8zs779BSDY$^71SN(}t%TToB!^%*&@xE%A~zaA;$#}y#=6}R8A3XW?&>Kh~NmiROJaesd~ufD5gza{rF@gEF89#_5)@h^0Ouid;R>(Y(2q&|6$;r?tNNGJ32xIe_tc0lgi8Iq%&os}1_MV?nnq<rLb)Ze*mB=*6q9lhb3UoN1$YejA;Pv7t|WWE}|OWHT2kmOH%fc|yeZ6f9CWRUXh{N;R048Z!?s+t16wrjrJ2P<C3yldayj{AwW(OcTT#SEOUUCbN4-sXbTbMYJGw?Ds^`_+PDIA7PB<G7#NhYriWj($$|Hy%{tbHaV>LpW20p*~i%g>z7T=_&ZeAsh39J+%SGp&h;uzS+8n>^Ej^F8gA++ex15)saW5{tVBRcIt*w{_p|R)8$hO<IVn18NRlskM!?@`{Gad75jx|=}2jx45MV;i%y&g|B@ek*TKwa2Qy8d8OT$5gS12c_UmyT2P3ATK06Dd-JI!)#e4eJlU>N8_suQq*wEteU0w-tKjMDpzy8L_a$cXe;JmCRxh4PQ-=%+#yp(a6;wJWA_1@3q{vP>J*70vo!Pi#im3`5bxnv*h`O_&V-=eadSM*Y;XN&IeUAdmgcq`LT{F-g0eC;5NfBm;q*w?ax=SQMG#n(wYWX&`Z`LnixZ-yO^`JelX*2_xpZ7V{KJLidv&*M4Z8$M&<8*iV_kox{H8Tl)-zmk8I`pkMP{udqhUp@V3nLoQ9hp*o+EbUX>2hR!ChQjc*mxE+HR7}1>+HKw>)U#R%xgJM^N<RjCn27RmVHnT0BX@$QZx`7p>+0H1B~R|(C*U}lTFd=9G>z;7-a8E6=(QO8KCb!4WFL0_O7Xkzmj2y6T>3X=Jbc?r$9!VX%7b;Xz2ne$^vl+6a=jn#fcu%fd@FqCkrL9Lxn7|D_QNdj?N>IQTV3~(%Ral?&vHwyyBi0w?y|j_;W^kmmF=92*BG>$eb|32jvM(2&n@<%mB?d$jllZ>^TjyqkGay0lKX7!o1^i)lu<HH`lP@(G^_qK3iZ4hCgY^!->9dV;|6^DYMj)+br1Bf*`f``k)Ejx`qx#ofb1Iv4vj#+Op8YQ=!=I+|JI&20_{1ah0G6I%E)-Q><eGZ|5UE)l=tMm5dXcD_a7+Zs&+dWSCc>Bc~sw#59RH@*GvCa-2vZRJ6G<%9iPg0&hayRS6Cyt-aGy**W=0x@SUr3%X3HS53>JI{tBLx%qw?fUoKm`?diLArNnsCZ$--U@ZGILQNGAHxj%M)g7+_0*Z%UHl(wAQ-zyxGJeS`L#`#`ZiS?Pbd>r1>SnW3rg8BtwUUmI^ROa)cuLdIjg8MQrrOP7YA=OOy_TX)@uK2aNtUrST`=g$`zdILv6o2KqeyC5)7-_d1{m^c9`G(?ud57a_dwt|NHt13xv_J3HM)9qqWn7)_1ubvMc$$zX``lfdz_)IN%k?`iLax)HXS$=F@j2wU6>dv^eVy73e!j}GE)Bi2&C_=VjJo1E-mJ+Dx}rYI9?LkKeNg)GZptv!r|cgxenMJe{MeO_bVhv|R+oK-?^erxWk5|Q&evzJ?1%sM9Q|W|)!=Ju*^gZpPDg(KFYVEu+o#LCcOeApc5Bw3K`6iEq4Z0}SLhcr@kS%~&Bn>NJ?}03n0U4(jywIf%wzi&N&EQEsrsMxDST1dXUvRB$m7~0_x;>M<hknW%5wPpZn#{hXU<9cd|l^<cC7G8>i@Wm+y}pIse#Y&6Quq%5260He>(%^w|ta#%jYfa7Tmrj^5+;T>k8)sS=Zg|R0rktCz8iCSLzvDtrhYw=_LE-Uy5Kq$I4f;E!rh`rp$-&b>zL$ri1X!>DMIBgZ}ayw5$%^k6H5vNjntXD1Pbs!O+SHa=rzo<GQss6?A&m-|2N-=2idI@U2NbFMEzRx9_Y{@W10fl}~5nuk^R%X|!JMce9Fx;qU#6$$Q3k>t$c+S`YZn&nKk*<NuQJ(DylfbJJ$Ies2wsc6;2vC(1oakmK$xhJ9T#cv~;jf0rEBz0NT=y@ziuX^Zi%YvW{o4j9xMpEt|;$1b&1+Go~w`1ZC8xDK_GtK>Z~eXZg)xgLER%Q`AuhknSzb%nEPYH5e#f5X>&{}Mmug{&KM=N*9axX=ab7VXe2c@IV3nJbg5L%2U<Z(0i9h`K55bFZQ7V}HIQ<@2AHb<|S*pr@~oSS{n^(^RyZ9guGzbj35t)9;y#+u|<x|ITBN2TS{>TRsS%KOT|tb}1a!Dt{2ZQTl_F|7)U@54tzV^L&l>t7JTnzdu;|y@j;H##wTmUh^6Xzr=gVvmvkKk6s1e$o-q-DLd;wzU}u#`Zuz#<k@)yz811o%3lqW`ZTFKOvbG)<EQyG89zhA;A{7;Nk0}0lX-8^L@6KNP1f`E(#iXy$4BAYX@8M=o~t7DN%si8d!BS%(bswU#<oADK6)(Mr|@um-@OiW*Z*}aeD^%_Z~pjz5m2t5jbMl5`C~GCW4E+}QRAVsv;PVBW~Lke>0hhs6Zr1+fbpoY<S#HK;y-yfk6C?BM##9BA^XxFXUn{Px9CXJ+i$kipX*Y$Z&&_D@+9jj*JJS>@U10lv7T}IE<fn$>z|Iv`KH~C`kO=7NuC_{Bu}Aray>3O1>Y$0TFS@elKkZZN8xkAXBk(V|IIPe;2YJn8_*`_B+u*T@XZYzZ*6`NKWqBYIG^H?n4itYbz(hz_k7}hzid`5A^x?sa@?u&q#c4A!8g-fmGUP{Ij{KXQhwEQ@m~y=JllH9{`C5HxDT0;spNgpwHffu*q74I{QZXcbpw3&{A};~N%91|5<k}isn6`DGXGRcCGSJtB#O`957-TIn9{%RB!7=GQhx7H_(sDu@*b__DS3~QVi$bpG#US{#HVuq9rI}{%9q$8>y6s|WFDJ*1N-0Boc*%i$U0KyJ^HS|=dvHQ*OGPV-hC5r9yOZFe$n`M@*GEBKU_-s<>Ei`{C@TfeAgZy`0n2!SWov)l=>u>_uXlHWFMw?sY!CawdDDtbgb;>M>U48*UcjPGiTGu`>lvKlaVKKi_D*y%gTPxHa!ylpC|Bqq4ho`&zD*Ii@!9Ny!XsKP1fOu?@z(;YLAe8<4S{Nez^7yzE;GL=c(l<@SJ3=UMcI`>z8H!e{U9f-xv4@>n5YjeYsz*E-cqk|CD%MG|DH+^T_1e@_Ur=+2OkaGRVGST1)mhqp#0|azDXU>k_VOJD~1t8GpmD&Uf#dxqV|xA*`3|hg;-*=$)hDr<pD5+pCSRZ(vu;9)&#NN6`*iwL`M+9n}fGox6>+Lpe>x+rn@uKl&ox-y5L=<#}yoA1UvCulm50`Xr2oZ+$$Dez%^Sm38~WSom5O7uLH*{8t>`emNQYD_X(&$fJ*N$o<iKv+TS4@lxIs@cGUzZHpgRS=Kq{g5`H6*PBKok8_TU=eL99y7;Fbe7#lF2|1tf^81g1QBt12zjBsdEaPEInz>N#2pP9Ex-Y}$zZ<}JEh{I_n-hA-^UKv_^1kI`J$cWVxr6L4UcM>*?t}7v|71AU;nw%r<aceYyU6%i_(Aq953GW3Hd-goWj&&0Ken4M_W$$`=j8qVYj0U+e%K)ITY?OEzMGX7zt^%lrks!CzV9yW*lnCVhm9*N{_u_{Z=YO+_bb+yne*lRZ(@C7TzDeaSLS6>zH0!+lQFb%BK%^r@q0Jt*q)fjwLur;`r4@BcO{nVw(MtC?k0KYyVrHjmziXLX3}o>dbP$fK1cVGdFI4h@h{Yn{h3su^1FilhZf1_hH~GJDTaP9D<;QzYr3C2cN@_tZ|)fc-wrJ<`<#u2p+074ilr#OJd5;iipuC;^YP%NQZHGDI9qMUd}w;jTq@V&3Cu@Yt?cr<t(Dp3dr#8H{IGQk#;IY&$@`*++tU84C&}*}uV06+|MOAGulWJjlii@Qyod2QFYDfEGx0vc=+O$k7IsJ4r``sP6Qjv{%oF<IJ@R{!^?{gIjLu&8yVF@n@-*nQS^Bv>d_8wLSzmFV*8VbC^4+#EpJ+idW&da6C(LI?bVcN~U5#a5?)>+7FJZ^#ly&cqM`a)2c7AzZF+2?8Q!D%!zgMubG#3BZSXuWDekAvcrN`jwHQLDjNf9r3kC1p@^6w}mzb^{>AiqB=?vHVy#eSA~yIBwXKEdie6u$HO82Notn>(nlWlk1<@LSn$Oz0-{wCBq{R<>3$ewLS&`s95I->BY9?rW~;^1A{5xpF^W_7eT1b$NpP=Hh{v7xf4qnXiZDmG<{qjP`cL%evXz*6f&n)BpThH$&qB?fMncG!<#IY+87T=TCJDNinzn?|-V>y~6+1PjxH#{eS;dcY9JDRwu;<>H_ixax`@YIhs6?8c9|<hCGoxfjXN!fjpU^crJA%c`iAgdYT+hzK|5(IYd)XPm`4%BCAmRfuZ;|bqiVPR`PA~6^7zV)LrCD<XhA;<VV!|)H7tI$H_{6A>Sw8r5+~VC7+_MAS+!@R+>OQMgEnc*hM`;c9DN$C_c+je1f{2yq$f2f}!|eQtYN$)D2{%(d5O{nbc_VOtMLxNLD(5Y?4P&CzD5!M=})8q0S}GA+Mpvlh=^XQ!kLulhZi9ji)pW#iJOC$1xO-pr#-zRby)eKP#^3kWiePdYi05@jvvgkd<B{|3iMwQ2dU1i~Nr4aC{qoihoRsbV>2ICh8z7Rb~EW+56<b$xo<v$xp~{8HyiJPmz`WN>=J3KOn!L{zlH_5dF%}zmdO^KT^+<Ka%e;6kn&FAS*pcR(h5Ek>5$_5PeTpp*Sx!y+c@q;*t!-MH!0AG8AW`s_!d)N_|LG{zD$~9{C>Y^^kg%{E+;Vq4*_3@nz~kvimx`%uu|IYLS&LCU2s~P#2Sx&Lqc>r&3L_(oy88<e}7&<ef<|Jt=->DDFk=P3}c*P3=T(O|HjKT!q?_Tq7x(Bt;8qH}d|Z7@QRIs4d7XSY{qW@n(kNDbyz9Ddg_dTIBBJ5Nc&|2swyag<OSo4q_<oN$o`LNghb;O&&;|Mx9QcMqbBIe1p1^tUE;i<ma8_o$QZ48H%ql6z^pyj-d7;N05W5t;xaU`V7Us)OzH4Yztq8VjpT{vJbfcLve9xEpjdPM{#NmvNyFHwFbEc`@S4QaUer+SL$H0(*5MF<W&sCsU4yP9l{H#%cup(E2!nE1<3{Z{qp>*_$G7DBi|%Hqi!ZAbBLbg=gs7k<b~8J<b~wX)b8Zb<o?tUa({9UY7kjzPqNaXWThj?J;?p3b3Ag+;W3r2@u<TZ)=}wsk2;^{IVn~5UH3UEPR4ujC~`9Lu%uW|-AElp9>x3gMuy@|48?1yBgkvX3#c{8HF=+2z)(Dfp|}E7-KQ(?vtn=RYqHXJWEG0DIwTb5psIUw4u;|a)O6%@yssBvC@#fNY*78kEvZeZe&qJlCJe>psD9*f<W$rj$x78)Ar<urS?OD{(g$RvFUanDe=6oz>PyW<_9go;6lb8S^+5*eN3sgV`Kao?u2^Yaaz1i#YDu!vD&&gPTGT4!TI8RSq7}6+wF<c|xem1?S!q#n9daN;ac^o_a&PizhT<9w#o4Ku$nG^qc79fzpZbzq%pv**KP&$ahT@CV%Vee7$nJH+MTX*Y48_M7ikDGi$jivH7>b8cr;?{~P8mk+Nme?LJdEtlGmyEJP9rN_=W*P19(7avih6_WzF)rLXT|lCB0edil41)(@j8a$`PBMkr8;>&c`{YqYbW!w;x-Nm#U-fM$V&H;RVdD!q+h5TsmkBTvJvEs<U!P6@*r|6hGKteeX>$tvOl>P)rVY+`~yRAW@-Vl(&A+Iy;*Ukr0`3M#?+?dKGc5HrsN^iHq@r%ru=>zhT>{TaVIH`CdD{vU-CF|bLvmz=H!ahQsj!{T-5K#N|TXuk&{y$<m6=cKgB7i>Bve8lT(m&YBh2-o|n#0oS#~WT!>ngT8UhV?O2texS2;=H)ALsz)-xFp?En%aU8WDIgY%;qn{M-p^l&qArE0cjbJElN3BL~M>eR1$p*P7LvdDWI&wO;Z&rrl)YN3;)Z|nQ#W|?ok(HJr=OCA${zNW84xsiW2av<4N6BI2*rf1sh<@*oP+XgOl&tg)S%qTLA)$DxLqhR$mK{faPL85BCr6RnQ!A3&ldDs6k*kvnQj?PllG8F2dr>vA`j>+2MNUK2$x8E+(~vW2-^R4!%vAS0qqrEg5Lsze?c2Ph*q_==`!<g$cF%i?2T=!*m9Evk&6A4VbE)Dl48?C4iXT&#lOL0Rr^b<$?jZk8PVSIUoYwK}`ca(GA$owHm4ASLA3;7q9!qUU9!u^(HOL*vwHb;_Qj3z6W+j&-=cJ}4=Om|RD9%7lMOK=FoPnI1T7sOLT!x{zAvJ*9klckDM(#phN{uDEud${4tau4kBQMfKKU0<enV%KUVJMDa;JZ{WvKO!6B@D%D7>c)3Ym;m98s5%OyqBSPA9X7EAayo%DtR{fFHKZk^M5fE&!<L_=aV~A+mkz!Yf`I|Ym$pl3zCbFGf~r$m3omgkyBFBkd<a6yRYq(jLiI=Qg5=-avnL$dDNjC>!>u4thB2~{kwXcV^_9;(p6-o>RH|0KB*nw+AuZS*!^rjn|-155OpD0=`!*mvdvI@!0~M_-~dB$B13U3wLCeN96(ij0Rhx!WcOZxVx_~#0pwW6x94GZ&h;M0ReXe@_!xB~`55^qbrV_XTJllyeum-%>H=~Cc{OzmS!o6GYVvr7;!0F+awT$MYF4t+9OS~}A`Hc4s0GMMOOeZvt1=YVqZ;IT<aUm4&(DenQhQKal9e_k_aFy5zCB|r?nCWNZBGtMik?Z)k=mKunPoaM6gOumZbWTDR$7j%)R)|x+Jd3D0o9k>fLxvGLvF#pwPh%7%uwu4txm4a@A@+om!@VQE6qn%TAb{D_AX7WMJ`Qt=d8u!EB%S=ekOO<trhF5v=dpWliY$DLUodrb|Z(7yHop<mG&ZsQF~H*k$bURPln<_48?<~{m4V9!x@T)Q2UXGkoz(eccFGAcjb9@VJPlEZAI=tZbq$3ZblBG)*%OxM^XdHN_&$>lBY2g&!vtg&m}LWMv_-jXHg@`5!BYyNOB~<-<n#3tTa1WX?}8Ra)jgCK8WJYJhnxhMRp(CVkn-(P+XZ>jI31cp;YE)#h*0Mi)5we$V!iqmA)c>BC8xq>pQ;Xtk2^sjUp?J_o!Pu>${n{lNwLnN!~-<Lf%8(O<hM;I-k6oyn~^58+9^y8+ik@4OwXk@&@v9YG(3s@=V9K{f?RZtaz+LLUAbd4O!`9vI@lwslSs|C=Pc>D4s}FYjMR&(~>8Wr!W*xcYIr;E1p5kLd{6dLbf$gwO+RwiYHOWk|&X!)DC1Pxh}OfS!qdfU2<7!PI6gtUWVfDsp-i|GmyV0XQ$>SXD9#2P+WmphOD$9xdOQnwF|isIh?wbtaJ(4y+#kGhLXd{ji?RCO3QoXFVEvE&F4{{d>-}B$8%DejjS|_$N6SqdnnE0(LQ-R+A|N^SZQgp(mEdPUx)ppw4+CVb!6Yp;8=-fD9%Q;HQ{Vz{Dw@Ev69G8Jf7+#JDGnxwJllcaPoL^B6Xif&V4+t(jOe(>hOa{Jr&PmC|*R(NmiPNyokJ%p?DRw5Lsz8@+$IHhT>h+0c52U$h*jg8H$fne<mx9BOfQ9q@Ex*4Rj>S=JkL2Un_q5r=HWa|NM^@|JQH+_h(+7-`tp#>)#)JH4RLmo`JMvN&l%AWo^~2g!VrXdRry'

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
