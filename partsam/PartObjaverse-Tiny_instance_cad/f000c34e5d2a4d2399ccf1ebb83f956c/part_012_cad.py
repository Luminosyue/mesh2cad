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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_012.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_012.stl', 'source_sha256': '93e438a67b86d3f6f4e1d33e01924947fea417841aa49ed51ee6324eb4e4a068', 'input_faces': 868, 'input_vertices': 510, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06472259759902954, -0.28968411684036255, 0.41213732957839966], [0.0913206934928894, -0.12189450860023499, 0.4444984197616577]]}
GEOMETRY_BASE85 = 'c$}r23AjyV`~TNA79v84*rL~*c`mj&!^sdurY-XjI!GyO-V6~DB2?QvWJqMlw9hfmAtguJN>Qo2DUmn*_OtHKy{zZ_{IBbO{r~5^?(6&6-*=s7J<t7&Ywe>}%`;}o>&Q=0=gdbdCbg>II3{v9d7T$~CJ*h~z2}fe2M&HY;N0u_=0|nLlkJjPbqF{wI<J)I(Q`=m<Px=lB_8WlqeR(YiC%+}hbDI$*mY2HkDkVF+-<;+o(X?QpKgPDCO(&}TCqaeVC7O}gCm3gk3ZQ=9ac>Lu&&Y0PsVl{-F5to`5Z4F6+g@NoyL#FcesA!pCzsz8&TW6KGyh>>xaf~kn3~5yVGAzu+mqq9~{<P$}hgx^~1+6xqhVef86UM-)@w0+W#r#*LzQ{Uw&4uFY&kQM_X33?i)Fmd7Z1LQl*|fPRV`OWOw~wld10Yp-I2W^@SdC{dkX8#P5B?_TQ>u<sq0UDCG}oEA_nffz)Sf$#wqvYr7)PRuO+h6)SJC+>eVtdW~Jqjk<E*xjo(cMlSs%<;-a=*FV!G=5JTL@UyNT%NUXJ_Z)D2Cu?Ur58O9;_~b`&{|BX<n&a>6bA3GJs_VxqHk3S!oN{Ns?pE>t$+q5~Pc6sUbf4>oODzz;-g?V-PXDvhU!VWwYyHO;aQ$eLOj1s#<&w{KMZ_=A#2OFkYrn)!PnSGD@`&q)>UOjGSA89yu}^zQeeNk~Uw`988K0{vOS`&Gw#spu*OmJJve(W7zSl3BhsyOOZ#O%{{NrE!=;k(7-a<b%llpvKH|B3wdf%Hz_)fc`G5>gr9Z!<$_b=J$@89r(r^N5Q*=kp0a0jV>(V<rUqwPCM{Y%|%jg$Z7Gfsk`u2P@h%Ub>A`CBJSeYP%^dgkhB<v-FjYWdzeK!3&0^|SNFxJvKqJXJrGqqLMiVwRNO^X2vadFNeUXsk6(LSs{<{+~^9{aA8NEC0c5Q>6UrRjho*7EQB###N;B`_{Pf`s@5MDgW<air)|R*=Wr>uRi$RxYc|X*(rHglay+WldP#yKI?$yA+qD3l{c?lOOHq%@)u6A=IOAL(vOp~TjL~n;ewREx0!oiU9X~tE=u{eYe+fU=gau7bwl!hp?a#noXFAQ8{GU{uVCMITshZwp1CCLE%c7Gw{2zDkDh6e;x8xuST)y=Ppq8k@84)zJ=YHo&y(VxU%_1sT|csMM5>j4eCNj!sn)!1_LS>~27PDsW9Wx2QchBbRDXNJ(cT;U{j1}_nb=SKqr+4E?Trk2UdpdmGQ~eH)DL%fB*hwUIbW9cR?eQ{uV--NB&q+3&Z$=3dQ1^NZ{uC=xXSXS)U(AjDgR2w6#x7RSD7K@-x!nXuaElCT=lKIsjv0a`Kx~Dbe0r<zeIkTC;gJGjhzSeN7qfU#^=fRtbW&ZDZTIYBfdATbRSu`Sn}|G``zyKR~|_7`|%QWt??P}uv+@7Vr4gP-acMxz4ZGh1*~zE-q-r1_nqiksn7MzQlC7dt??FLn<Dl3Ph06n-Iwvbd8g~4Ua#Yy^5e62%k?eC?Q#8zCDZ(VbX%j{em~gqh}5UXrQ>e>$G1A`_d~OK?6SsTwNI^iq~lzDt*4&H)DLBNMC#x670Y+VWU=xPDtyu&=Zq`$ooiRE^)~+VX{k@^>-K(kD$Q=!isZ9?KjM6}*S&sowKTsU?$*Y=udc(9?dPQaPLi9qP|hrAeqYy_$hA>24yRm@JU1#U?P?mgd~aRS@j3LO_(O(B-iC!OKf1VsHBZy~-n!K3M=9s`h}-Xx4z=8Rh8zBDtux-Zz4?c|Zs`2__PUfa<BdK3@gJHS_}IPg-GfiK*Z1mw*6+s_uXghpn%gwZ?|bu$buvCClU!e5o?CwCtwL#jKRT$HHSg5-^33|6zPDe@87u8-oz3+lGcLRR?(FM&*6+u=<g?b3^uFfPsd<mo=lNu}p0R_sBtJ#(mHTcuZqFBd-50!k;s^UTw&rQ{uKVP^R|~rB)%7rR`T^GupQ+@Iw^-$1n&0>4BhORn>;9s7P+!**9nbNd1?~DXFVv5u&UO1ScB)vK-w(zsr`)L=ou}S@v8=F^Um>>7t<T9aZaL2I;#U89=W2Z2cXWJu{*H&Nb;c{_@qes+(DT#p7hOw8es(8IKJ~d0-x=9k#vA7)^&`b<Tk|fxuj3@zxU`f%b)u}Rt8=IM{b04~vhTFM$MR#J){%Xg=UMf=^9J<^Jz7rcS!s@p!zc4ezx-WE{91eV_{&#6+I`e+YaZe2c+mQ*uj{kk*DHr}o#sFMT~#Tk%~#g^Qa}9ecl+IPt~W}v{7V~TT(KUiAG$Semw#TU?-Uv$`C%VXKXSUieV)<s$7QqjDX)CmrSm0nq=w|b`~Yjcjn1zl?d{jYUEg9CTDa|szE)5C%bVTt9QwFUn%@t9KEqmXLjxL0e!kf)?LBhsjNf-&d2^3H59;gqj10(Nm!tbT^EzI;nbc?Dm|gzyslJ{o^m!p%EXi(H)<I|eetdZgYg~EPGf#ED^RCzRT+fa8dVbb^bh5XS>$8rKcCntQ@2qca^_O$Cjr7;(8GHTXNBv;uh1Pi{nA%>-dG?$;-ePCkTYlvJK{B478FI$&YyEXxg;sX7#-X<_Pwyh-|8+{%u`03-s~>7NY>$7ws~=gp#v0F_AD<)Tv;L?b{-unyo`<{jkn#(^FXxjF?@sgk@!D@leukE}{9x(+);^_vtYd3Ax0Jdmd2ZTU?t9nQvR{)=^_^Qo<-Uh*S=VcS={g^+&`-+WcyynCJgXlcA>&-@slIcUj0df!R}Sax^yTQjqt7*=OUaU-5}n=g9C@VES-&6LdcqwKq5PH8tm~7Wko=q|WBHL)!=yeu&wAI-E@Q2qp3na4ombVr)_&KW%8AZxYpr9kW5cALx<8h^YWa}{ZKXbI>Gw@9N#5pdvGS>YNY8t$|LTWdpJVMi&V*4?ewl63@0`2Tj}_f7<*@#!?{E%`ZK`JbJWr)BN6)?9I2kxbe9qeu*6rxiuStD!jFNMp?t}QcpQiUUKe{fdug{_0e6KS>%2{<r?#ucdyJw1w&#sjZS@RlS+v~OKtGC3@-|Db?eM?y<qpRjfIY$rK`-1wp2U`6VoH<YWtNbJxw|Z_=|6hmq`sb<oQOyJO@viSWLe>rT1@C%&PS@v=SKpKTY_4ao=gk+}^~u)ztly9Q{@uPiUGMyNwTy?S>sx-X??4&1?04bH%cT4dhPdU28Z<rY_np@#?DOYS{osU{?3+BNs~`TRtM&Zu6kI9wT$$m3|Gw%63+;2)0jFj=>-yljbN0CuKg9l`?NvX_`1JNKd}rA>=@-VcS0CR0=>8bVu-ZERc+Zdc@lQrs`%du0N79eYzu)U0pX$dmFSOQe_4VBDjW_&o{$%SM;`y}8Nmov&_cB@M^}Pyy@ZIUwe(m|^I@;%F{PgcnVp~48#)F<i)YtQguIK7I3v%xF&kOZ~(>KWY)cqGfa<rF>&)P}0zxWC3c`CMGvy^{quX~Qw^PcCIZtAWNx{utxUgo>EkK>2vU+=m5g&oYt&yV}trG9Wqz5{o<K6ZMiw3qcn{Rq#4p`X4zW0hYsY@dhm^_-*q;&e!{);-Oe`XT0>)8vwUJ>yNE2fgcc{n7ItzCKTR-^Yb^%XoXU-eLc^RX=ntX3a14b>H-!vr6u>`-}0Tet5;Yeg1K-eymZ%n(whc56ktBCLQ+A$Jp1$q(00Suix=?oa^(iGyAmk%lGvppSoY*$3|b@@4v75&Xx04`H@j+lINNm<Q&U>t$vhsSo5!br1=<m-sJq?l{3Dhb#4jvIwyYBd<WffSU=T|HO=XcL+7z1+i$SNdOxPVlQ!Glr|^T5yIRjd>PH{xz57mn@Olw@K32UT?fPY)l~46UL-yI{aD07_l)fCzgPt=(4_&n9uRdqt>%ODU9qMcS_4!DBJ-2)BjW1u8`_4IUjW_l6eWUkY1wUN(W9xhs+4h^%bIV@`{drSArq7|Q1L}veEp>fe|Gn!!d|CFjS361m7yn`Jn~am_<m+-@-ZSXF5bAhK%Kx&soR^-dZ~2klH~0JJwfey=+4uYV%PWWHCa+)g`eC)K^K-aCV53`~PBX1_L;aAJ&-hnA!g~+zy?5zM;twBg&EH6#tgf%`F?4-aKQw#bVgLA7U!OPA`=OGHt>>)ZH#x*V-};b$Ja~Sl@`wEGQr{_C^nkw~)z|m2`n;*WzCYCWqR|7nr2P7g5BcZ2`qB7h=`Y^XsvkMH&tCV|<q`i%)x-XAtG>=hZ=T}EbiT8WsUKzk^`3X|_59<#kBU6t`r%t&T6tDq-z(}oRo~mccwUb8DJa(;2+Min-|f%({n)ZP(k^{(hOg&&9k=R7KY4zyzaJy53QPHG`djB)^<%>_S<j)~_3xaw_9^v)+gD2YoLANN_Fwu@{ir_IlZRlixRk%5g*CsTSxZPcy1%gQsUNJ<L)JHaAN6agJLXM&J<n)+)sJ+(cF;eb)sH=1UwqCp-u2T9h|hTTt}i#!8b99kwM*FR@E2vR{CnR=;Kwc%kbO<pD|~&w<gH73J^9r66<%6N^2T$VL;WLDt4cZ3Mp^F(J>Qvj*y=BQ=eg`sAAPU#Vht;wT7UIJi)tP6kAL;U`+v3Gud1*0)cF`~RL8DopYCV<ek^JAKL7YsU%x-naTqFBPwKDFzl?wNV?3wmJW^kur}RBWJa0qk$IY{>^KJaUjip^V`pEfzL8G&NKhim?tOGnJde`$lNBhg!&{FEdxy5_0g&&Gf*y}Gx{kWbV^!ZV**Y`a7cMkK~SoPHYQr~&FkhPwxAJKJ;bt%-pz2sS+L#dDYp*$z|S^3xNdEU|Sqkfe4#@>EctBcg9ZEtHFI@x+i`S;#D;2$UIhjl&IeB!4+2db~<KyN(b>pHLNkMmnEYd_U}M}0jH>wHu{92;nzucBY}l{`G?SmzD(qwUUE`;q#QZcC+n&bR7&e-EJV?NbKG^_*ukZ?S2~l85h;to1Pb(lC2{V;-sRofDWZ;qXgR{-!xHk64$~k6)N<^>4KNC@EjRx6<|bpMOjFNyDx6$MaK4xZ^Owc`x?;cq{*r*{v-<{r5`Yjc-`xd*AQi>+`0bH^T3|Y0YaLC+a)DEw}o`8UL2F>xH(5{rOkl+ZV{E`k|3qW!)>-$MW@i8NF|`-5h(L)phCddDi*LTmSK+#on~ui^ht-XVp{JEA=A_UbE&)`1eIJZYQ?3)-m<tx9S}7k3;n%u~cc7zSqT%@?Kr%i+6qXiL&nLxffsearK?EOYQwa^Ng?e_2wOZh;_;PzF_wX$wS_Mq+be$CC?wMvfIo1L-oCLyUvSdn<WnmPg&2o>PK~+>U#3v4r@QvaqIaF3m@>89|@#LIcxhL_UAKre6QS>zlZUj_oIiUo^PI&^Y&}6%lbL!gyd&jlJwX1{!)J3)8ZHJAikc{@b$dvovTZviLdV&G;jEkkwNQuN_{5_@AveapX;1;UiF^S@%1?|z3<HzT?ekkt$jh~i~73nc<%>#{wDQ&V2U;VgGql#o`)Z@*0)%d>ry_?*WUQdbW5%u*TEep-Z}YX#!Y_T`#X)TSzO=gapHhK|FPs;t{>t1W$!&n?t+{A{pi#iEB=j#Tt7B>x73IIH+Vki`g*>KI74I|m{V$#KR>$8cs}m~bsR=oR+92hJR#TXd8~R>xn9?QeU7-Vy|lMUHR<<Qce(yh*!9ELpOgLCe2>}6`qv06Di#@9p;Y3@ClPl$d7WO}eE$@|nC3_I&i@plZ<YV6e~M6}T8;nTe~R#0q7E4XiEYS{FkC1RFDBxlL`*^p!IR*((G2k0@SEs=9buzc@J$#VLHQ#ndj$SNgyFCGz0HoW3B!}o=V7C7!js{(=)(cwweY_P!_T3w!Oy{4&`;riqwk`h!tcU6(f`0Z;a%u&u+cN{E_gBJFQ)9p_*>Ao;4ScTXcb?btN7Ygh4vbq?c8qrY;t4tMfgSfTl1Dej*S)~|Apue!{rlEFcA+ChV!8h!ujC5XeBr=97Kn}LHJq1@F>FYqC~ub4n>E+L*ZIzCAbpzu0<FwhZcm(!H*J#Yog`hn(#2f@T-L3F!~T2hMyt~7eVvEMd14h!}-y?aDKQb8ia%7s3>8$6*>ww+68U}KSLPqk%*pXSF{V<6&{U_f=9!P(M7QK&0@mv6w04M*;DX)5N}YIH|RgDo8ii6Ew~o_RGBbb0(}%N0hc5US3zsSRp5^3Ft```Iyww~9exLW6@CYP2@S(x`uioqaA(TzOxd0BJEBG4j&K$9eqWvM_qFSO+G;evukHECjnSg8(N=IP@@u$$BA!gdV}#)+2*Z=m<?tl<5A@!Eu+cKG3BwLy_+3ZBa4ey#9MLPN@vorw!dEEw9BS@&jxanIeG;Avw<QcWLF>a!;AVv3hJ@j|=wonQxG`b45&8t&2yRXo9)V7RN5E^)KVYLKM{D?Ocn50owSzD`HWBU6_UOCtyX3JwVYs(*JJ-Dl!+jF*96BCd1&@bUqgUY7a1=cUpCj*4!tfZhEj$KpLl|y~Hi4VMNoX^;1KJ5~26uv6qYdHKa0|39T$lc9K^SgH`7J5CC4Lgx2u^~VqRoAEZtiPWbJ}Wjgs<%*$c@o8@EZD6^R|N=8y)M*`B?fy`+hw79K10R?<e9F!f-PB9-IunKo}m0Zh}X`JJEmOo$#lG;Rh09vwT4GLDcvU^4ahquH6K0;(mt+!@JS<;oa~a!th~qBYYSx7?3a=Kwp7P7~Vw~UPc%mj3&c_;eLeSzUT{ZUw9BY5*|s81`&oAqMyPG;g1rr9zBkJ3Ll3H1Vl|v3j}WGx&UFgLL$C%L@%J_VH1YGL?48|q<?0irVnP(7rWtE@HBJ}JPn>s7=9Z)48IM3g_^!G{5@W2J{!L@VK@&OfQ_0y%fn~GN9f08@DX?e<!|5~8}PqE2g6^%Z=?Nub?)bDS3la?kN(!S_a!%d>El`GLSNn%lH-N+tLFS8`b7Kw0{R`?JrN%#;%UP0TWG(4@LO<8!ti=@H@qI+fu4eUq7%_m@L=>q^b~xG-~W&>ya??FFM>Oxrmmg&Z1@CWcp};zo(Rt%3=cq`h6lji2*WQEh6kc=!2{v>gyG8M&g82yVK^CG53eUL$%NstzTAx^4A)J>?};*-C-f{@7dBz|C$uNrll&SsVfdDFyAKSTFnl-V8*R?#!Ekf<1@uGs1-Ki!2wp^gbR!JcL`~n+<g?*@gyEU!M0h5=6rBNILVrbPz`w$K(E;#YcnR7K?nb{ZAq;P){Oy#z9e*i05MBz;MCbeJJm1%@`LuUF<3ihBncP&S@4KO6eR&&8j>pp1FQCog(TUiUh$iUka1;1jN3;}d!tet08%NmaHh2O2??kLbe@3^#_XI?L<MTH7H#k>7^c(ma?w5-&9711*L+}*B@Je(Oyb_*D7@k8Iei|JOKMe;7!;R4<aAUYAVfb@L)a2`P!te*^0(b#=`G7Dy)t9@egy9v5NJD=>SHeHQl>(wa!<y?#gyCk1$cg^wh~5ML$n~dC(;ue@!&gz$2UpP$Y{GD6yeV*I_({TW7+nd6;YR3G_<poKIu&jYw?XH?ZQxAk)9};uUnauvFOHONv=JKQK0*4m5z&}BHl~lY&P9FgDoR_6(*N4_&&kc_^zl`6s&hMUQ_1mE`c-qjf<Do{{}IhefAx3FyJN>mMbE>ja3mo5en8mhc{l=phF*d{gTEpS&m|0hl!z#L1ib_wfm6}*@Okc?N*JD{^>Kt}!8ZxRpJ+SaPvHH8;c<lF;b?z&I6Q|iJONFGC&0%D!<_=;G$7oGd@V#jgFhoj3kkz((Yf$icvvDHO~j}~+=UK<?}G0`=fd~FkD(vI+6Rvjh8s|R1IliIKZ-EC06hXPfajs9a4P*Vk1*U9HGR{U&xWrPh7X{hzz5*Z(EV`UfaoLWe%OTJYk1?}arEUi!tfX99QX_PGUZ?9UYGGdLnpwW!3WS|zB(WCwd)w|J;u1uws#^oo#^{{=vrUi){^73^y>n26udDJFDGIoVYmjGAFctPc0~W<2%9jxjxc<NFkC!wZQFooIn?;&(ERx2D8C{4GTab;gD|`X-3YIN4-$q?5{8$fBjM%nP{ME$S_4jk^AUzmI-;h{Ckew_(RJ`T+P{@Bd@&Ij1EPh|Gq4H6T~U*xu7TUR>x#Y#cZJ_03@=N>AhZSgD%=9DinfK@lJ}~F;lJsdhOi04x$)kBbHl9(!_T8@;OF7l=t1};^keiO{4u-%Jqd4sUqP3{%jv&Y2*a%?zZGS-!k>*M!L#A#(R{u-=kv8IA8pM?|7+V%lADwC@!#l0=XTx<Yi<p<2;3eAE$A<!b<m8kiH`jL9qHpisP=QML_Cp*-T`?<Y<@DJSzx1g!&%XL(YxV$;fD#sWeCH?&@6B<xBy`|8|uK>;7o-1$&3cz%y2G~BQp;i^Y;xBhD)Ql;L>moGyvy-a}tI#q8Z?f@Lj%K7`_j^2h9rK17{};=SJ^^bHfjy55te3)zF9GYVhM|8Mq8NeVi~{8!Z6WhRafZS;{Vp{{Wf|egMvmX7bfJldoNwXlo|=L))I2++-%#_o0R1``|)oRk#przJC7~S`n=ZSA^@JA-E1)kKe7%?-fF8pw;2(Tw8-M+yD*1MoYsD;0kCC*l13;0-OiU2phc%)^U>uEd=L*i=#E*8r-`$S^>V1h(Ap`0uqMHqE7{cO&A`BehH6*e@w)G(Ld2I;XmPT3BxhMa0m1$xC2}aHT5Wl-hfRQu9(p70nsj~@w@QZ@HEu4&F}~4aI`u+9PW>nh0D^;{)FKr=#TIc_#$EWhA%HS2*ZC7hW{oEUq}ChufyM?-@@O+KM;m5pfUIYe4H>m1ML9MfP10E;9}&l7h!l{;C8MD5{BPN#6EN#+8tg8Z$rDl+u$^G8mxVjMi`D$ew?!7`0o%OP?rzrKdswv>OP!4>xC}ywQC7ESVEs^PA>ZLc9C3Or2jOxH^}`B`qJ=G^fLMvd>Q@){Tu$9KK_L;d=C8{J_o0uKfroF!&?$#yIMl$ITD7m21Jj+S>f%3;VbAh*yv683jBK_4x?YAH{s9GU(uWJukg?4HTW9$`<XDj7p(^Gh1(H^|DsK%oqrLAvj-#$AH<snAA~<7495w>M^TfPqkJ}8gfP4U-43sSPor1hE9B)gVfd^scV`L1n-ei45nB`SEV>zf7Vd){hWo&i(XV0cgUN*9nUp`1vS;FNB@BOo{tABqA3}eIf2KbU5r$Wz?cmjLQ^If#)bvvhJ{vBHnm#k!108^7hX=s*QPY?8(GOu0hD)Gv*o5KQlwX^&YvY$hkHRJC{~TzM!0kF0@wKZ6Z7sq$(6+B2H!J9S&DCl0dYZof0^JO6raufHNW@Qxn2+v(=fjVqV_>7tz>mY(&<SuhxLzX0qo1G?;Qi<-bOJnqvQ`m>r=w%w>F`o?54;pUK^XoH{R#dKzDgMWgE0I}B3d;MWXPNG|MZ`JzWrm~Jvr8Y2s-_5+JC0$|IMk1vb;aqY}Guo``nNr@jvs0@D1~q1kV2e`d_;R'

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
