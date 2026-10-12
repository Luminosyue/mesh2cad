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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9f43d0ac857541e8a3a92e20ba284c44/part_003.stl', 'relative_path': '9f43d0ac857541e8a3a92e20ba284c44/part_003.stl', 'source_sha256': 'a123f413f8d9e895db8585c6e25350d37f5115c6739ca4a621a7ceb91fde2eb9', 'input_faces': 648, 'input_vertices': 423, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24460949003696442, -0.5, -0.025235531851649284], [0.004536827094852924, -0.08541011810302734, 0.039285313338041306]]}
GEOMETRY_BASE85 = 'c$}r22UHc;x5fvt8zc5E*H}<djEKDr_7)WdOHjEWC<=-c6-DES1uJ&!av?S}#@LPZT4IScMnz-08cQtsTM|u-?cKA#@4o-=)_ZHc^`2{;wZHv4`<yv*+MJn7(xZ!e?h+dQRn`tqpPf~shNh|XiB>`z9TAr>bWlXR&xny@-82v3>YvLl>=yJzkA802Xf4SrJR*KjoL5teSM$M*y=q&$2FJuD#D$IsiHQr3P`rI;bbN%9$47>ajBxrj{Cw-zw$!g#+cLrOfBaX_*#ygg?&l9Vt>Il}pR%@|3n#U5TF0cS;1wtCRn}g;wxPIXxJ9@Y{cyk7=^3MhM|y%6yCd;NP~DkQ&%XEPz@rZ+Ybl&PR&ndrx5ACk`%;f(@T}Rwm%Ik=+FR<eJghohaqaaQ)N}b0;f_Mb$IEq>E<pU`V6?x=mifYm&Hz6cjO(TZrkc6-**2+1Yx-oK)Zbtt;(eZeFZGNmH%)Q-gBb8q=~9m^;_*<aCp#MTJYIqJKg+*Bas5an_;-z@e*M&6a$Rki54i8AQjeB#LfUCf@XB#reNx&ixo*~qvl8dI8||4kFHx==HCMQy4LT_C+x%s`jNsXbpIAfs!LcV`vDDvu8u*7qX^*YQ#f4^W^qnX58_WKjqPXqX1n|rrQop@fY@C^EVXr0LzAjDLukDRS{ONVVEpDIAk#@GKaYp#~+ft9U-uKB8-_%RE=HVyY2;L$6X7~II-198>;vR81_`p%%H7j<`!G9Ws_OHH~Anhzy8Q1l@EB#=vRB@S^Yv=Nye-`FjD(&>}MEtiiWn3Jus-@-ND-L3OLqa89D^v;mo<GJnd!O{PBTq%}Gp*4-8$+c(9nZ_)y05-P|L}f|2c_7~KH!gkl74f{O88OYhqO8*{Z@X$WQm^^4_=^-aIHfT=^yK)xF2)$TgMHJq@K|ug&SL^VxA1$D&ua89s&Nq8$4~n5V?L>H0pVH0_){NuO(7XhargXdI#%$=LP9c%_j`;ogSc{U#wX!<5GM8_{cvn-=YUfyyHzD)KjA(*6+PN($D(iK=9{D(hrXK?$S=jy<XtETVh=_<vhII6Z~yi;o9x`sX6$ne3%bm&!pe1#g?CxxQdIV-;5%+g=>YE2{+Qm3)lZS8!O}f_aelnl|nz;J{FMs`hCGkb3Z#KbzLOwyqXGLD+>Leus%xsV>7|sK4M-SC?fMm-!ct+?iAsA!qY^_pKG8!@7=M_B+Qon)RM*{zD*MP|4i0b(%-?O!Kc5(zL(N>h4h1eEb7UQ5^lKL$BXrf25<HV`|1`qsoz#C68um!#--T&c&YF2Fz_@D`?=9f=7aVq1boR#^z)*3UFANm^+$V324Fsy%)op*)ernYVT@zh4I^b-j`c-7ZjbiJJfDXBSwGYVJoTb*+weIuUbck?j|)Hfn~aMsx4*0}Yw7{vn*TZBj!m;Mjx+XyPtC$Q`trtHsXt*4c$qMa@1M<lBtK*a>Yr2$^JMu$8DG8K7VzO4WqdXFq!_u5WdrKrKBfg8mGL#)G7+D!72`W$Y?6#u_A<n;tt#B=*HOkx-@X9xJLk*z+KcWtB!9+C#Q&s$SNvq9^nb+U<L2?T_fMTD*J+l7cs_q!>rtyP3h|*|V%(3l94+<#H5@$mJ&ad{gEGF>n~~tx$6$S3uG<&=9*+9k)xfy#dWrGfZUsMjL&i&cabURISJpt(^KPebd+kwp4z3vhK5><By;^y!$8z_MVVzg9OZ(O>!1JicUGNu0gj+(o$oT4c9Kwz2Z!un@tay$;`9-)kZxeXgqyFf}%i#C=2)A!f#`E!;bEs$CLp<-EpNJKkeEgVsUE7OK#J<<>Ab5`(GLFWb`x9h7dTs~r-2v;J<7I!Ih5CIr$~YP=swB((>|PCCq_A+u_Cpe{PhSjvXSj^7b#u!}5+67V_20UJ=Z<UsR7*zun|2uY@`cAr{_8~WxD$9D?bc;}+JA}#_w0rBxc#|R+P^y*eCT_OSDofE|E)_0gP+`l@!H}&O!^@;9PP<9Rk-8l#WKFe<S_7&k%<2s&wZ<{z)|r%I?6cOmgBr(Ny{f(JJMLV-J_t4uQ4q*czAWhFZ@x)*D~b85ou4pR~TQ9m!0MM9sULnNXPzgrlLGw9A%yf*B)2LxbNO7`<wmVJ;XP$VL#9EmGz=;x(42$fN;y`CbAxF(Pw$xVc4H<o{;gf_#6gbYsWcZ*v!dd?{C9(yOkAgi%(i5{l97b5%c(JzpRz{;25$TJnIb3rDL98KlhmnKCd3e_sm||Pb{w{qkhLmoDX|p|FIk&2OjQ&aZfxIAvPl(^>AO+&d<U4CJ#saxpCZYmkpM7#tlRK`vC0E<95mTS|cM7A6j3y<+t`SzIy4}hb4YNsEn86=t<e<Ex%S4Zf|Q5u2)>xQ{uiaD_q-g5Bu|do(HBDK|P;^V|=UaA0^g57vg(m<2gI@Uou{fT(6~Gt$ahAGuOw+da><zAl!AXv#pve{cl8FMSPWOSa*wGOp*I2a}x2ht6{$_P<OS|e`*i-(-@3bzlsuXOUgn$#xbnNU(>MO8?8h<&pGz0Gvs-#{h12hEfwqTSv#Cd_f7`qxkYQ4IZWC$FA4P@%tHT<yp8A4ka)!Z+zI1YJKrF=uRbFY?_L?>SUFq9%h6#t;sZYHmU`1K$@_xddo=pdqZG!4=RJFSfAFwRu#P@v$UM~E;2dLwY{vdJt%LNB(cvce;%Df$!+oboJ7({}d(P>4;OTb}|I6Y7=KgeCT{KnlE5#zd>t6I*wWcy&mgJs@|FIy}#i32I9_{z*BYuA@&W$rqVt*c37X0pA=?5b(p4YmT5B%4!u)h_phy6eEPn@f+l|lTaM+2puiBG{l{EmJ*iT60Y-vjX0r@%MHNq<^eKE*l7XB)=Bt3A#+CGLS=NXPT5Y*9J?TfR9Des~z-*SGC2{oQ6C?vwkWrSvly7hM~V_*j3emqP<E-=_N_zUT$qUkCSex$Z*;=2O9z=>L$_!u85~@%(-ri*sY{cNnksbHPi0C-qq)Z(_at+6lZ?5N!1>vhIvqrBHvd-q;8DJhew@h`aSr`bQ7=p^w~e>%Y;z?gzkQ%E)=lTIM-;i!|Z3Fb(gsdIQ9L`~}a2Atz&GK9{NkzVZZkqa^81+p-ei6Xv2ni;j@znxp!MT~dEyfAG&|VxK&=N4PdC5&aod6!%*u0({SN>>GIxNxxaz6hJ*4JEK4UsbQ1$jM=hN;{UZC=jV-v%yY|~5b&jqr9Z4k&f+|FpgMRXZ>;OUOL%{5^(pwhU2-4xv$h^`UxjiDHww%aZj@>w{ifZ0y94tr6nw;L`95PEGkv@Gt;=EGEpkr2V_3_M7H*Gzj{Q04KKgBbuyDQQPV{H_w_!4#1^p3Ub0Ye!Q#Dy%mg%pyiNAa^`mN+ytkcau3jfb@RODEhSJn+n5I?jyo~Mca=(o*-!QC54KigkUm?`B~*8@-Kjs5wDWQjM@&u$gIcNNyb?^R@69JfY+=dFNw$M+!1d_UpF;9S@zc^<G9D2MpRQ_*jsfB4I~xLgGBx%**V@9!u5Y{|%jc+c9HU;GYcB(L~R=Et4n%aVWKjC{Yc)SV^VI=j~u$saKe?;Uw23%8{76z<rD?-kmr5yFidlcXM_d6s-%a=s96k$$OHC0oi}jGrhx>Zx#J2l<8b@*PIczaG3yTN!tU`{yYV-}o!=7I@wo33$KO-^2>nR`$Mv`Sr(exnA*h;Qw61xL;|H^TV@3;MX%Se?slpZwDRxR?64yhWKE<k5t_T?q6NnX}l{KfO#-SxFdcV`Yo}voM(*5R^hJmfW8Uq$mrKsxFzJzY?Lz=nz?b~58+x^fSf1oF^e{f&+~xRH(lnBJ)o9wW7HQ|*Ol(ilI!$&^NrY)V^>iQ@2xIw%T4}yL0Lz}pWB5SKZId^&bxv7Gp}!wxYHrhpVkn}fBT$l;l|X3*dOYika?@=X~ONb7hMyZT}$fMycgu)wyW>)UGe+Us6XK&&ec_}<9v8)`bOcivN1o0$H+Xl?d>kycow)D<JhyJ%>NdR5MQu{a7#Gmr{!^V#5bQH^F;5ODf7p$R{}5c7xurfMKTYKP32He`BaSKpptXt{-Qq>Za)@*dhSdbA?<ngDogy<U9m6iKP>&M9sgapb~fx6vGvf;)|K~jaO<-s=!d{~@U5rup15WZ_SGZ3h1<Fhl6Yg~V40uBiE6m6HU{%EZzVY&+QS_i%<=lB-12<Uv-SzMKPZg%j)PsX{|Ao)e|Zt-(7Em8yR;+UFyY4BL&9x7N9BI?9sPuBD>~sEJ0x<3*w0#^o*j!AkM}ICcz*E3{jp99)ryw;yYzOw_;J41F+Lln%6!}SM-FZY36g!lQ6^iswzM10aia@lNPkvZCtSB{hcWJ+cz?VQo}(Vesata1ux$Hhotf*$@Lk2>c?*1gUzz{bE$yX#z0fZ?;*Ek<S-<+7pM+~)d1JixSCI9hmr6u@v4vRgT#uG~ZG<}l!)09T?v3PmWbg6&T8Za(Dvi$(<L67@X(O<&{?u!}<R7{K{!LHp177pc55_U!`o=sr#IDDCsNH{04sH+VEAN}uox_A{?MGwZ_`A+Li5pT=xXp|8^k^vSPAgFs@fG&tT=QE5&S`Nc*5rs^vrWEdTKx72cfEILT~47t6VrriYjfYg{Z_#DpK8<AnETltRI-=kzny^i%ad?^aD87rq9eY^N1SW?dp5zkwIIIaap4Y+VX_a{w-o{}zgW0+@`$g5U)=n)@LhS)|Ce{;IbNZ!aN|T8o?jR0Es^^>)j_y5<f^paTG|8Ob7nTn!S%UQ@tzX!AyfQ{?!s-~Zo$4<=Lg}2e;u6L19?tcu|c@y%WTwh1@E(3#+V%SXr<aW691pxIpZG&#Y;Vh%VuJ}T@mishwt0QHzjf1P8Xyf?D=0}d{;R#gu4yIepo(l53!kBz#HZUPk4y?8uYbr$DP60m+ttElk0a+7p{%GiF4onDe`-k%|Fv7@h5(k_858Q%R18B(}e5E>u(BA@s{sq_AOI$aLd_Y_#N#{U7LBHXm<h=q~3epIqP3Hv!2v*=~cRn%Rg(S9<BaO*>5$EDB+GV;P%N^rQhtG9IIuV;?|%&AE)3w<?U+WmU$Z1(XGvy(x1nct&+G&lW{IOFnXc*$*)(6EsS{m{5W}EGnV=a*9K+qx_f26GOF)cAv`wvmelhXzdvN93%5r_3AYsLA-_Kw*G3DsI&7%to^Lnd&$ca>xc-q6ul?G5zM0!MpF?}jmX-BrtkZ=X*M>;EF=8doZw-$xlm0msF5I5hNzU`e%g==C-l#|0{ImSdqPfpoD!f{jtQSY0Y>6|56c+9nF%-|i?zJbv#>sjz8ih*z4)3S<&Kz<(P41su8+G|h8JCBPg<Ge1-j?{ict6z_PZh3>t0-J=I~c#KmKl!tmdi1Js=md1`zM!hy+=vZa|Y*Od%)er;y<g0{l^X88*TLyg<G-;BmR;Pz7Mx7C0uW^4D)LIm5@Uw?s)%B>amqi{#xokxEk|fSwXZj0Q;(CMTBrYiSbSRWIo#uv|1qXsVA{-oW6tc%7y2E!*89`V~f2d=L*Yrt%cj#W(n6WeruSyV|g&f*ZR7PTyJVq;g%OmQBR>(_?^zTmT-OZEaCPI_&wKV-y+WkZAO%E>kRx(WNotq&y5);(9U4bk&^#xnsEDv6|ye$?2mKArnE|x{ANYbpUwN>_oJpCB;T@NKKipo13U+-{w&W=`}H$2uk5Mm=*Ol-aLz3_PvZ4~_`S~vekA7+?Ol}2H(UFQ@?F%}ep0w4JPr5t>Mv=({nHJ??HqTjU&S@T7ko?+KH;py8{YW+-QMn?a9dIk*6GgYcz(SZ58mx2;*a9JN$>5QVxCt<@w)OpVib5R=V-(8cg%<6E;5dK=qcg0s5dyD%vyzgX8#7fcly0R{Kd<1Ue$jMz;~uUdSSh+Ivgyve<Asvr#<=`*Y)T3QqM;69akH6IOjfK+?VgQHoX|?Kifi{7kb1K`7UK?=z)2qSE(iTWF)><h1;>;KIkR$-#GD5z6<J0ZK!7-zMmLvGUWFJ%b@8P-_zyg{Ao-L!gt@c*HQmj4f}JME?9p{o?w3N_L2Fioh%^Sy5RX`te2N^?$v%?FTXe1|Fu=-n^xnBJdZS=6yetE(=boITY&Gh8}%`A-6wA`pRWYt?;^_gm*0`pkV$-lUU)w}HYXnQe*~U)J!;6h);5L3n#Wgn+?W2ee_2_$&9?)_#fpA2#te}4p<jKE^;kF=zrTOGGbTs<KV-@8-P-e^GGA=BUgJDG@@rWa+Rp5u!ab&;pP$!QZ07oKw#VP6m-KUqprPoecW6)b#@&Ti$vs%w-+e#EF*ytS<d!#sq<pOd7?<h}{9QzaF~Y6aUSXe%#Qv=P&_K9t)pX4NTD>BKZ*D$7{KPX@?*qGI9ABjO5&zX`v_Iklo;#<P_m=xSxmVg_Nq!b0d{^N>sVCA6@AaK|-BI~_ndgt4`=QqD;TO{Gez(zn?^M|jwayniN%=xCIENRjgZ}Kjr>)fUuDirr+|qFF>iM;9?oX><B>G3+P)*ABMn70q24NrAu&}bk`%RSjW-E6*OnB9Uavsr&2BIG_@ZC?lRJgUW4v*oO=kb*>|Iak<qO5InGmO{3zViEpme5t6^VZ*g6Rywtc9@y#skkp~;x74nB<=N)z*gq==XpO)c%zd+GEdJWqCG3B;CIaSccowT&fwOqKJxcD+O_atnJ)o<qMp30C;Fjqt=S%&GY{eKbF_q3R<XhN@qDj<?+@BQ_fWa+^eLDp-E-r4-SLEQ<56R*3*R%SCq2LPpRs2*o-arHjl(+aF24^rN~WNleO}=_(4-9JU1k!_Z@jKPuU~|@{l?@}?B~~(N1*>l;(dAe*%=c5*PtPi|JP%*=VOO?X71`w%f-$TZ%o=4DfKj9JJ&|yciYoXgj+q)9=#_1PE7l(4!(z-{{!dP6?pH~K6!z^!-{T#@g4gd>n=TB#@TrJ2<Nf6fl`mLzj?H@XZtSf=fjG~_YM8Mzx-aU4MBhE4Ms`4K5n|a$6Lyc!~EoXivH6n;f|uuan3w?Q|`+ey-B|J+m^i$ZoSbAe}58M7{6yO8H@APf<5y7ZprHtYi_?|Vof{;8!V2?abJbwrnKsj<F5=$roCS6sN^i-Oa-(O+Tc*rpBO5r{<-Xb|0jk+{r*>fV%X5H@&ETv4D+~Y+MmvLywPB<IMY>=uk<I*7!{}3-_G<eXL{>QPpB39i@ws&s1^H%zS1wL75hkE>DSbX<#vOw^atiCR=^Fu(z&P=^PpdV_Abla)1Vd0$2<?}d*mmb_5@=eYVhwdonZNg^i{c2j8W`24Zce&`>7k!L&g`UUxE5JQ;f<l&Ad;kOOva1R%RKMUy@p}D)f~uMXgvh`bw9eR_rtSN<Y%TmH(qtKh?mVk}G|N{*Tm;P5H`}q<u_%n%Wh6n*H&Zwm94Pn0h~B4rtJ)=%1$kjd`b8=XZ=dK&|Yzv?_m}$=}CxhV8epjLKi&Oqpbv<Vt5a(-yKt^fQ^ZFm4fjRmVccD3(lXP%kw3i%jw9EHj^4u}QSa)br^pyNYphsTG?@JBfNOePvfLZVt6#6KE$=&!L}0J%M@_eU+B6{48o0Q~nYrrDxENr5;N^$>firji8R8KZI#4<9pE$qK+{6$_}MXq7I_%!=!W+?F5rfqTh$CAFb+-;nWl8yYhxpEBhs_>hBTM6Y0D1Mo=r;msX8uH1#C<uDoa_#SCX^%knC}J+)%>=qp{HTCs}smG*U}cJ!;zug}zuWvb9u<;plyHL{ZQtC0DccooKbFh;RLv_+{sOnymId})^Xl-h&ZgXKz)D^`#;FLeo%|EVedGnOe%U4mNK{7fZShbLo-Q~Q|8D_fPeu1WjQSGI*Ssb_l~Y9DGJQ+=%%ukr)vtEA?xKXm~8y7c|YBD8<capezUQo1{B3+h3%p|oF6tNdnU-KoEzZ9=V57iS8gZbCnleh673a&PJ;)XLVTZAM+2eNl<J8U4!iD^YvXugN-<Z=vtf-i!@pTjFU4I8!Wj7y7QeSo*=v6hqyKzAG<=<vN*S`#aM}>JIc{=#OM<2a~Vz;~1m-$+U`1G5J#%JCJ#C)CttePGejgwPK^4X*#u)zAJA!>#)-A>`Yzh52SBpQap@0jP)qijeZz)ICUap66uFiD?5%!>A|!;Ou8F=m6|(KPwJ-h2h;D#*rq05<+o&v@*`;#3pDwGOp5E|${$9nSZ|ZB^mxX7MLpQ$M=~~*dGn~pnf&pL9mlfDU&*-D)U!=~D$C7gnN;dT`ZK8&TTb7lXR|)n7|f(rb~>$!TWa!`a!ebuU%OE^rETa;HE0_%)|FR_sWD?}(N>`Ka;Ea8@?NIA^3=+fqAhFEUi6i1;7rw7M*}i1va)0<PtDzq^gGk~G0u;^%I`qipW2UpN0uANypGzx*F;0!yIT8d&rxey?N4g2RD0AY4SP*I^&t9Vs1-}0@6yUnWg5k@GZ>@t)9AajvWuBgSZ)bpRQ`JUF0Jf3rZkpYN4v(Ew$WF52lY1U_4IdA@1R!pFq6`Un0B!2VfvS76+3A1e`Y#Fp3O3ssFi(2tKy!Re5H>tUd3Lg@6yV?WXfi_V~kPxw`gBeA2a#aS#Gy8?PA_>`p1}dv99CvRULa6qu2@hF0JfcrsJmgO)T>bwPN4Xcj-N>;~V;$nUvnkr1VLq?-{?Dd0S}J`;O}!XfI=3d5WjAOa}EgCVw+ySCOYvZ=%0~+QpQgMV-ZaRBRc2l{T;+v&c6vE{k0GY7Vbw{t~hcWIIi9F1?fEa+iJlf$0{<_6TFtym7rJs5Pn1PU_tBIg`?DXoF0;7yZx4d}-CWza4cDeOI31RavGQbzPJHIb+qCM(rQ!>{ps`Wtgfm)?LGy)s4C!eU;Q1HXrlyQfrKJqpxDrIXXYfy0d-iJ)}K#ACs@FdQVVeujYt)KUHf_tw;4OMt#4rYxr)n)tSC_rtM@~sTEsGt)4OJxwFxkesHGS&U946^Hq1I*3OhmQ~$ZFrsdY~3{d-eF-?8k(zL?Pl!v+qeRbBeI8!-iigDiPWM`V>1|3g-0R28>F=TzHM=-^(>}1AGVN!YwlhUC~@vLVI{lT<~bu{@snL^2X(&|h~H>7Q6(gW!0Wc6qj^PyI@x+%}4m9@~8cc!A$KJ;CAMX8l7OzZB3NmG=u?xsAANwGgPaOJ<(U=@3z{o7Z%5X&o8&S@*UfmI||x(?f+m^b~3Ocus@(^qvgW{hGDXlqb6Hu>I+Z|_Xanb(GXW2WY;s||fsM>obO_64m!bvKjW#uOjGGQFw0QFmjxFmlBrX!}x!nf%_2k0no_?ngh2I)Hg$tRtCzB6TeN1m+K6UV=$08%e9K{Uvn-eOI31{b@Uqn^{-#FImpzE8B|J-=x2w-<R4Ir&xX32GsSb)p$np+UmLn{o&3uk=n%ul1DRkAY&p;tTTBhYQ<VocVc^5Qu|W3Vtah4y{PN6eO}aMsTC_nU+E&w<Vn9EeU~n4iuGjqO3qY^ei8bfOp4d0uFZHaYG2w$ChbSR7PX5tai+H9O~_Pg!T1*R+cI@`ra<Z@^t;dxWPDpPl^0GPNFBvI<%iHlQLFq3^rNV!QY$->aZ%JG$){5*JHweq)1Sfkkz|8t$5Drvd}XK6&Y&JgJKmY*&`x7oO*VsCF`F~3qd$ZGY9__Mrv92`m0e`g^XaSDOtMUJm!3^urHPDJI*I;lYQ<9Au+EdnQ>c^3BdH@<b{=DvQYX_-p-yC83hP_NIK|e|W>T-Bzm&0xFLtH{%*&v^ifIAs%Al|6Sk4&5(rMRFFE{xaj8Ai>xy)Nhe>u}!*0qwps$&^r6q`j~=~UWu>RG0kC5)R%t=K5~E<KCo;>Z;XrnOSXnS5o(GL2$cEB$a<#TJ_U2~1<jC(y2-O=sUMWZ866p5jyK+o&hdU%~u!%v(X-fo<we9c=QgY}e<`)SCHC=(}_W#<phJ4%9*Pn^Cu>R<<TnYt~hjc{Qn(Ek>*IE17(y^U`;tu1dcc^NTRA81*X+ac<PgzN1z71x>!v&o#s;_MG-T(>tDhlvS~Xn3Pug{0o**vG=JJdq7|5JJgCf=qr7bTCp4SmA*)=*iY1ooujYxd1}SZ(mzLgjd_=;&r>UVf$2QU{lYxOex+9Iclt`_cY{`}j2nEV>ryM$)D6DUy{HxIL9N(O`bvN0OvA{AkxPCTw_GLM|EK>2&%ghvGlG`mf5`J+OXmDp-CT08v#$UAk-bNkJnCJ``O=b0J`7J%Uy-!`0OQV{IR'

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
