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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_005.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_005.stl', 'source_sha256': '91def03d1e714dbfd79a7ae01c4e8e565ca76790f09e24960c983cb59b26ed3f', 'input_faces': 1344, 'input_vertices': 838, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17371760308742523, -0.05904656648635864, -0.36900466680526733], [0.14451076090335846, 0.0445343554019928, 0.13932453095912933]]}
GEOMETRY_BASE85 = 'c$}r22bdH^)UIcDLCHx_1cU*}IVS}c1rd-8N)T8w5+zG?lpvCkAekjg5D<_I4w6BVih>9%7(hXiAVI;us?J;Obg}n;?sKm`-*disr~1^X>gt}^o^I;bj!BX+AphkITr6F1OuBl3fL5wN#z6lLz5Bk^u0x-qJ>DJ|6-Z~e{?EoKb(_?w-z+N7KQK67`wo5D_0Cr@nD51o<?|H|=IhwAci-M^dbIA@yL|`EUun~=PY1>ObZ+x@2lYCC`BLQz2TK(w92^?_fBY|nDj^~6#eH9>7`ph<r#i;n+qF!`;K7Q*bC(s~xa11+x<m!T0|UyhH1SHdb&2ut{wF`vF(Im~<eB)n<oV`;<nK~i+6VtNd1HGuGkM}GmJr@&p=lp}HkI_-r?BKXxL4Y5dv;x7-1Zy0DxdI_$4s7tA)hSs@e?0O-faEXMe;z#QIdap1<9W=ukgBGN}gl2&HI60a!H=C$qf&bx@_`?KF=ZTd;Yb`jCWuLX+J8P@F6`-``AVEd^|K*crf{!Qs=~s(!SQyhKGJ!E&1<e5I#=&4Hau>@&xz)yw~vNFRV84i`mlt;|qp|{w^*2k5;CALi}lIf9Q<NbN0<X9y$oW@~YI+>pN*beD)`XC;YNJl84@hFD-3iT!!P)e#ZO0`HvrTRQM15WIfdGVET>EdO-5@&*jT+dBAe=hwf~b_E`^n5;+f+2jGFG2V@?~trecOp1(ajl%}4qeQ^0w;eVZ2V(Mf)#HC*%dCKoKJf8IvzOX=e-EylUj|-RE^%<xYFZp9XS`xXQU7kSu_$+gU-+j0;@^}eenJM{yZz^@dL))eckKeP>cf2^<))O2zMfj~eOC+z<?{ZsD_{~XD&nJ^tMjl5V|9!;D$m1w}Zd2jGzRM%$-|_(5&VOK8ec?^&EH>>q|5zTn^NMiJSMld-OZ$v}`}VKpp{M@#uZPSvq<wT)@^D@XhpJ0^cp!_Me*%Td2|s&Y`0?6)KJ>Kkp|Z|Hf0vT{kDf9-$oV0mT}f#V4{?5opHoEIrx<UzJwJq#6c+x+K*_(diLB2wxmoA=43D?x0eEOzP`EvBG)pV|$nm9-`^EA=k3&l%*K_DWGLFZOm-^O^!|i&AEtN#_<Y=`tavjEf`*4qGe<1hL$aUp%n<rTB>Ym8;9LxF2<6{~M=lm89Uljh#6NY=|vHTY#|NUDsZ&x{wl{_tc)KZy$&Oeq1^2INfJPT!><7V$Nynbj*6&)uI+^%En&+oyfk2n0_e8U4f`wPF?Yo>l3ziW~l?+%asZ1Wl)za~61_=5#i65-*xHx}y{40I8m{qFq8JT4EMtGCL>gYc=v=Tu3Ad;M1EApGqS^L_O@+^gU6-Xjvv1Gn{iyi$+&MDxQR%U@aeWBK9U{48iEJa6h5ru}!{$+~iQ+y{l%_;`NWH~c%kN+LY=+5Ss(OgP<2c%bW4)9?JJ%zh8P)KYlq1-|-S?(G-L%fRh^akw3Ce1_)2$1R^`^56bzn;A##Cc^s`o?`0R^QYnA^^Js2nDUXyf4GaEr}=tbWSuUzb$UD<oH||Z?U!r~h0iHs`VCFHA^qNYMR?PX=0)yzmwWYC-uxq9ewW+*?(tfe;uFmee=L9POYw>3hkNU)Rdwe1rRipzX*bBY%2gEpXw_U_zYh2MwLI|YTwlKq_xg=5FTCRe|GILxx2`Pj^uWKa9PX{Fx6Am}N$kn-vaXgF7ryV9S#O~S-3<?3EF^qYL$lsuXLpkJwF+`R>E_#yF1K}hJXbg0x^lU#Gj@0$;rHg6<1Un=uFU`KtcmY;hkNsHxx3#T?yak`X@ws-;?Lu7?|8BN=n>!iyWI90>Y2i~{u8?8TKh#J-1h5o+po)m8+NbsagLY3qujHrB*v-J<&V{A`75axnsI%fO!(9Dg>$}jxwl^&?#-v0hx4<?Gt-{)v&+5x=x}d8Iy}JnJpQwXVZ)uzJD1x!J??zox!m^aap&{S<&WieKJQ#^^T+*uPxz(MzC14XjyuaQm-eksmwU(E6BmU4dfYb;F1PtTe)+iX`-aQCaoyT0e0!z|rrq9QJIwf=St@)($+713{CS24LW_lOTp^#ovv0}wuAK9Pzx10qUxjm=Hay&HCjGu+&R3xuC*}KF!Rf-&4U*5P$;ae#Jjqz$1>ZO4`EbSQ!k3H?KIFb>A3ihD@VL~&h3~6o>WN(!V|c=_fx-g`(mwFE)U&BCdD2S$JoUFrT|I@j{YcKMf4%1Cx#k-l*k4oXFVI!^>a(WbK<(l(4{bXNAJIVOXM0|0f2h6i^4X-{N6#7_|IM4icV3nAf66JsGu0RVK~ewubhzE`9v@xQx2|07eNSlfg79u*<$LdQ_qLk4W|kGcc9?KJcM{GN5dK#evwrM((&hHN=ka^O?Rn4T_B<A!?Zg*`=f5laasRhwy#*)i7rwEKeC}u4Y<TSPt-|MRmi={ggYd=+;73jSP}zQlCv==F{6=;8p7wnY!$aHp3cuDu^5-fh{TAseJoDGGZf_Nm<07H4@QRb=b8vG~KVRKh`h9Ru*29>r!ui|`?9MO!zI$({tgFK_BiCVk)Q7_7{Vac{6n#$C?Xkt%4Zqt=&I<>g+hC6O_yxkhn<eL^UO%tbuj8uD7XHdU(>{2%ooOG+JzDsoRdT*wvr+hy{e(ZtYk1r{zY71Phwu#pWPc@@<>!A7GW{lOIc<2{?n1)bU;5DGpVEB0k6-?2oSBC#ANzUZcJg;zpV`}de8`}Qrk+!a{Ovo|oMh(V{`da&6HXc)NO;@desr?QrvB8~&FkRB<Yv1-s!VcRgzKC7<8R;JYWUuO%yaD6^*+vghNtflKJ8E8@j*GRPH*z_GKFP*uS{X`C%ls&y#G|`cfqCgKA!nm(>``sOKIQYi16#<q~BM@3;$=I@cjAZ@1^K!vL24?7S8vsxX~fmFFke$@7rX!$#eMg9X{^tuRxWp!ufnm=r>9BdxI6iXFZVbwKJD|ZpPbefbiQ5M#=h~zr)9!{2t%%ulc(^^yD%>&%Dlj?gUCb+UDcV`ti84emow&Xm~i~0Y7)vmB*cR<#A_SdE8l79=G2QC%$jyC-g>6;eo%*=VM%%xnZ*|W@Z%rTGfwDo&l2#52j2hyyPDF963M1@NnyETVy{TG3^tQ^fWxK_c`Hw?!=z#>gUJj$meo6kKuv+yJ+7@`h8H_@KE{9!uebax2+}pW?kaXQ@xzjd3AyCm-?DK@xw|Auh~%e)RJaB2d4Ef>pb*qJ>eU_n`QdDTICC~-PTuyPZ}lPcbB!2<H+(6GfbY~pwA2sjIA#G!9kNJaDTJO6FgFWOXTqzoIlyL_js~*O`e3oPnz`{T$@LDrTcQ;t5(kNa447X^2N;eqQJ{lcbV;SW)ohaj(mR_RZxzvDH((p{x&``PpH||&4$leXx2|c>&7Neu-lKqxh|2A;hc<j*jK{&JPoxhVAfCY#+REDJH9;b97i5^jw6pd$C1aK<Hh67@#1mkc=5P%ym;I>UgG*L7tY`H!P;re{KRdXBRu*&v#w&tM+tvpI`zlMadhWjS?BjA3Qw0*K4<s+<LCBzQNkACXNJ(Pb3U}(Js++bDEwLmb6m$=DJjSGkp9Adf7V>53TH`><9g>?!ug&Myz-;)1+V+-dH9v#u}{^Z{W2MEx*c-djd)pju7cAd>yK>`n<x+OD=WN5Klz@S>r)wT`69ykex9&<sh{6lFXw@O7RdQw-HlC=?Y(}#KQ6r6)ADyL=Z*L!1B5rcDC_*}ZnM8)o3#;sxtM7m_jGCLH(Xlyj0@)YN@#m>myh%PKlb2I!$Z;eg>ML(I)f>D86N1HU3l~Qa-F14PdUCaWfso)FyZBHhKCPC37^x<?63G4^`y?7=QbMNdy{D&KlnvyU+kpt)qhIA6ADY63l0mP+F$0URRQ5Y?G&D{OXfd5o8j@DmI&v3o)D-j_0Q~M)=}V(uJXA*wyF7k7`L*W@Uq3s?<T=CPoDT95gyJr^SF84x(=T+*W~w?{m-08l=m2I+J}2pk~}Nlk?RQQgXa7hUSC{zsg#S%e5Ri!^(4zk`xyCqe%ceJec*ID;o+KwhmtokJZ^bvU!K@pTX*_+`}T$hw*4ynN<jGARhIb1>u@_>%R}#^GCY*O?}^0tV|m_6C-tvdD0Pl|V9wKl&Ld_1hd*t2sK{;M2gb_hSB2O8JXbGMe|Y0w!xJ9f5Z-Od;>dnoZtD*n{X_VVC#2sWm&oT}x(mX0uJnz|<u<>^OLkwJXnVNV{?8-AXC7Yizj0e<xXdo$ORLH6P}S?4jO3vu!fhUxd;9CR6~c!U@zvvUuYLE)(r@1@{{8E4FOTKV<y)L+d$?^Md#SPX`_0WIk>hfCVBCv79)R29%jIr<%k8)x%fs>L@i*!uTBqeUPyD6^zIg~=7;z#o?yU!hd;8tt38U{wJ%_3$x~^RA?e`x`2p>6e$^XW^^?yC*hQy9vm)ks+2STS8|8LxzpV#lm_sv?Z{qx{(Z~YwKEZ-}$?={C`Xm4^kuB)yQzNd?v$7*(vzu%{SBz*Q;a^5@g-A*6B-_!8e!e<Q+cA6-B%^ErXyq#B$_j2QW`9mL$-|6Fx4#|1u)<!>Hf82Lo^>~BjQqQr%a=se)uJG<97WwM5{DpQ>PwyfA_S7H9*k9_*GEjKaD>6U7|7P;UUg;;?p2s@INc(NQeeGl83;6k+-E#iVKGV-LeDCAoH@gW>Q)p3SJsxLVu`dsl@Bc;K5?<p4xej*dxv-CKx+&-Lq}k-U&BG4D7p;_W{oGsTp-frfneIvbZzh=WCL}E-d}M05K2S27$)8aD_`1Z_o6Ei9B5wS;#ExH=+v72irr&3g>m)qvyj&OhwX*OFLxrDQWa<p(FDX2E3Rw>)Gt1}r&`iP;l9}u8;bvoY`gm+w!vk9;3D2HZxc%JBRMpQ}|ABYA_&Mt*w7R>W|5aD=KRlf%xAPo|i~cNfo!dG+PMvmL1xoz8Hga5ne~StK`kwIlV<b=ixsqq$9pUc{@Eu<sZ`xn#U-6o(t3J1cKb*A4cU)U;&jYj%y?lLb<ne3k^f>F>9;boNe-Zv_1F47eL)?ya!oT8r-Hj`L&bVURe=7B4X(zlhzdx2bFXyrDZPxgX_ZP3q^~q=Q3-8t0%v)%3b2+Y?WnJUjk9E@fdBKBne*3kOpO0EC>#Fn$na{IP!i)8j{c`HQ@bERcAFk-{i+t;(&1K=gos@NTF`LX=^hMzlZb<tnYvsJR=#21%Wu?w1AIkc#cG8#M-XD^1r?c?a9!j2iolN_{6MxA4ME&Hr3%t<b`!6DRXwx}4PWR6B^P;Z_FVWq{1HI(?YHZ9jKhGlf$%L}JXLzW_A-UhG=UG!vFuJJRx7lrl@Z}TCyv3bbVD@Wx^<3dgF3Rs)S*H2<%-gabcl<2;o1x1R8<*woxIFHR%gf`8%j3?t68a7he&$X29sQ?0YkfT18M&Y1i;8kQztBK<!zQwRKIkI%H4UvMyq<in1rD_|JT9t`@OatpwtZaQl)~3mm%nR%cwg>|E4##e9}P@OZ{|7vcx$=uG*b(?KWRW2ndkax*ZTO~2U6$KSLJu%H|h$%E$6G?Z!Z`gf3Jq{OL0q0zuP9r{O`;u{Lq(D|7TtOylV~9K5oJV;Xg$QU$9HgZ?C79`N?}{k%@y}_s{3PYr^MblKnm-iL9UHXM|6jBmIubDD%^zr|_9_z6$5wEd7S+2|q8NBf<Gk$bDjGmM=8?2l;#tJW3_^CGJeQ!0?W<<#*gl-PZUx^AN1{3-|fli#NQ?5yNB0l#zMs^tJG<>kSW#8!Pn`StWc@KEp$ew@Le+^W!7uGn~-F&&Lmz^)r37<XJj%gyGKh9FIHK!94C<PxiQT9n9m-buf=R*TFpQUI&Y++uLyWdX(i({h<!0yUIHBUk~*7|EaxmozUaXbwZCj^W$-6emw46KlHdWZytB%&Ew9zdEA+|(D}`o4R_9Omb>RSk2~i#FOPG6^SE<<i`%=tOO-_C-{a0ad)%34kGsE%S?<iI$KBt>EO&nwv)uh%%yRd4u`;83RY_zWdfZu8v73GxR3(x5x7?k7k2~}4<#FcU<IemC>wLQ+v3@Og`}Mffub0Q^*W>Pf4^~>8SihFL{d(N#*URJd>v4CyUyfgA^4P!Y54Ad(7!NEx`fVh4|Gsd!_xJv?<HBpV_FoTic%V?iw~^fad&lMW@14NrJL?n6?{b^payP%ry}zgG=h|TM3{2(A?{b^pa`*a!%ia7Td!3>6){}|x$NF`ySGe4}E>yXs<gwRD$nSD*zrfw=EiU)2;}v>I@^Ib8tJC4${J`DoKQ8zBeYW9-#MY<Fz4{&Qtt*$ao-KFRv&+48=y11Acm0Q7Z6f{J>wdo+KA9Nz_PfKq`E>Je{m^pv`k~9cb>eVuKe~DB^?ci}y-w)X33uysuQ$5f`+ecq<V5$Q%e~_l?(P?td*=t6hwHSD<%d6(-?`rFa&KI<Rtg_l#6Ld{_vQ!gUaxk!cl>_5OY(4?+&g|9?yY~gd;Q$yHh)6nqr&a=dGfp5=C|Cv&hK(Bf3FLYhu;^xJPx<>Z@K$Bh0DEuZ64?R<MPMyJLeyld)IGU-;_M|cNXTy<+fkT-QR0m?p?2b?vdoNzeADV<u<?N?(bPH_vZh#sLu^|KEGV<%@5rD{BpTBu5ca6(^P&3wCA_SIOi+N-QN=*<D7qjsoM*;ze_SdF1O>d-2Hvi<=*_S?z7o&=X<Hg-M{aqY!vQ%Klixv{oLcu_j8ZCe<xb*d_VWN`*)({D_->fooKoHccSI)_w%-ww;0ZS1>us7<@#Ijj&OT_{=_75J?&i7RyiJ{<-SC&@5OgZDV+OYW3Q!<>tIu>3ZEWje($!|b;Awn3U8Q3?oU|tjPSxewkA5ymb?4Ka(DhMcjw=7cm6GR|4z5u-7l8A`^9qi?{~}H{bISZUji9E+nU(=^tdw*!2w&$eYJsZt>ymJ8nfj3ZJB+-^LLZ`jThGvK0Vj=MDtkg-p^yXGd~`8@8_}Hy`RT&_kJGBoq34ua9-BYscGhZkJwga<@)yXS6N>R<-U=zKgsVY@7)r9w2^u4Ca|#6T2oi2GO``_jRdm2EWZ;qt}cA(i;}<Q4OxflYYT7NTAn*7Us>|}(M$LfN##D|r{7y;`u*WO;h7)FeYS&Z%60M?6NH~iA@`MWy*jYyGvU|fN}f{{J~iV=RZ#Aiaqf$Dx%WJX<<5Q4F1PnZ$GuWtxN{%4%f06dEO+h$ce%X}JmK4B!rRxB`Q$$8aH%*yx6cJknJoOxA;Oa%ko&7|eeC0bi<9L(>UkT4A3b1rc=8dmU*eB!5<azvJfGF&W5a`Q?h-y^t(pJuU*DTN@niQ0Pj+4M&zdFs_xXLk_OZtnNWb&X3%AcV{rHR7Ux9KLgn!#{Ol18Ycb>Cwxt(W^JI`6T+?(fVmxS*dCC{Brf5p@j+w!XLh85>V))_zUy71z!$@#GA4Ef#p${pdgy32EFse7Bhx8sK26}~EmtpC1SWj?ds7v6ZU%)^|)>wMgKZpG!^b8VJ8&#k!Jdv4|8L*dSIJudg2XR+LQuE*u}xf_o=&-J+cvHZ?+JubKTL&=iM{aMa)RW7&vy4-tS%+14dRUUVqt8%&b{FlQYtJ8U|Dj1(axbs|_%l~_x(a-;Tp3%?kdCcR^b8U}t@A*eRx8r(@bKVPeN-NxX?$71k^LLgz&;7aF+wZNO5x#nbti$G`&2bSPpT)ml+8&bgOdh$9FR*iq9Cs!6`?>S{qszVXw&l+Ak1qF~Ki%=1@N@6T{FKUJt`8<O&LMnXdO0pQuLcGe6z)6+>T>TqX1VhmsLQ?Q`+AiWo_~)Vr#HSa{U#hQFTA7wIa!z6em&mF|D3GLz4hO@qHyOqUzdC9#B%33UzdB&Cl;&1{P0}=yJzKdYJV*I@t(}jn(}7;V_Ux@yyRq={~9yox@X=R!dFe56FEN~cb>m?xmUmC?sK3H_s#>BJL}NpkL7pPq07DeBkKqs^n$F9EfdUm<6mniJZ`7?9%VmY;(l%<+<DI3<=*!e%bn-kUG6=%xU#A6jkV?bTb0A>e7s&VSyzP`n*9|#(?U4kH|+lM`1L56ht!v3J@;-Y-1+weT<)!B%bkBuz~$aNr)VvF-bfkO(s`zygcI$AJO6%y%k96P;Bn{QPjI>Y_Y>mZ>LA>G-qzvX^M;nY&)YiOd*0S^_jy}~KbGHp-qzvXzh5!4v+%`d<$G79-`D!M^Y3!F+&k}C?)<wPF89vQaozpL_38xqes!-0=gAAQ{a3ZkdJ9i{TX@@Vg`fLL*44HC!n?`+`Jr#Ze(wCcB`){Yq2<oMTjFx>Iptr53Ey5#=4Z|g({Jq1knkaSW=0;@flTiUw|_@G(Obr~YPj$xcANX&13!*m>*IXCjqUb_ocF4Y<n#C3yvTkN`iy4%+@BlC<J!#d9jAe1UFG+%O-ud#?mE8K$N9S~lxw8a`RQumm#fc<<bhjvg`c`2ze64@D1V2pN%E!PlQs@9^+f$G&yx;FF8m*^Z&a@)*HtQ~5&lkB!(+3jk-rnaODlXts*u!Ik-zJoCQqJ_tdAu8J)BMW5Uv~ats&QQTI3XdyN7V@zY3n}AUrgtzlnEi$$TE|E_`#-ex^>o&m@c+Bs~5(Gp=yT$+B)6zbpJe_Q9sVe%04isqg#O^xm2E@vFL4t>l4>fsSn={wX~fT)>No|5JKzmHxl_r}RpcDqZ^j@88l(kyO<Xt@NZ)GGYud8n2a`_jN3YPlkVzSOEVdJ|(dzJ|#XUu?jvXJ`b@fJ`X-G@g;m-d|_gBd|`YcVl{jre177~`26@>#8`YTd<tR_d<uM0Vm^FQd^GWSd^A3Wm>Zv2DXY>mO4;z56;mp%^c*oe{uyFsVs?CKr66sK<Fga9;j__J`%+3d*se4_NX&}Q$~Hmjd5-N$;d4aPl!KTRpG7HyQbweGDy01r#58yvQ{#0^f=|Nh<izy&<oKtE&*GoPrz57vr^D<2GAX5{#w_>@#3+0Qd>Rx*|54;fO-zr^#5mIuQ{mI%qli!7qws-<aR!LV1ONS(oZ6E!zH|}e)V`KdC8bx8_T`ZFWr-E>I#$5zSO#B)*X4<o@#XO~h_&%G@h=i9<6p#=RC-nE1!}B?uS6_?uY|9NO3;4^a#SEz#=puqUm%vlzkn}6EQ>FJFBvh;lEm`(lK2;iHSl(v+NW0s@Y71^h?(%|@M)0tPtitilaZJfpMjW~m=^z!S`evJ{F|5(uciI{D3SKbqos}BCI#^UK3TNHd%V_M`!AFZDD5Qf$M3{%N80bDjoxM-aR+`6aT{?5K3es4Tg4>Azwj|iNtNzIiL}2<OoG=@x7R+K9*dgq?8JZY&ne~5^AQkf|B#p+ucL0SeR4gIN|yp6?SCVt#p`$_ApU(-!w99}Nc)k*QTUPg50LiriSzI}F2K*nFC;F(>$o(+>-VNbOAXWLa|C`Annvzvw4X<g>Ev06xBX6!sB=2CPiJh}uT@&7^cm8AJ#iy`J$^INzEX_D7h}Y0X<wBXi`TI-zAC;7(*6ZvMSMkGZ>6@a)Upo05pAXK7ik+ytW2MuQTHz5X8dMq-$ks7uS!k3Xjg@LCMiEbX*|+?tkPioP+m`fO;j4DG?^H}PsV>ld=LK--u5$zoI~;N65qp5RT`u8q0%_w82TQh^p4U1;y~gc{Ai^q_$jm-$o5lte=6^drq2-lzKgfDh3GTHIBowr4j~T14`W`25Xa#Mvdw5Th*}2m{utso{4BPgL!6ACgP%+M2>%gtHy3F?TWKb7JaH0!B7KY_&cKhue@OfoKNCNjI0HX}?PsG|5jD)B-fxxeDSe}KSLuY(*Gh%dntM7%n2slSU$@m?6u)5`?GF*N;<dCtO3Z=(Em~p{UTdy>VWnqcq|ayQS9@KXetnNv7_U{B+6vS5F7@f!|0N#8|BKHOBho%Q@d!R9M&e~&YkryckK*kZE+g$@*!H)GaUEd}j?k~2lY`O!&D%k0jA0J46La9R<FgR6#{5^m_Wv@s0sLLYd5;)iu1+g$Q~E(^yV8$JXOuowS`J$d-%dN-{u*&F{u(}cjKm9gE$yFIF@220KY6YBpVaUP`E*=`&!F1eRxx*sNc$8qBJHn7OT38RPVM`M*YVeBvyYtV**-nB+(v)W?jrsI{UxXW<kWBL(LMvR<4aC`*Vy)Y#Qa=m{(iupp|1<nc7ZwE$DDu4e0+jmMcj^Gh2KWphu=pY?Gu#FN9$Wb)OR1Hb4q8GR`YrV@hm>CsyU-lD&k+!;#1*oMoat|zmxn2h&S;!X`}rbrIoZ@Nln^6rE=y`x)UuiC0^IFpIXo1ZxDaN>v#vRqu%xgeg4J!KjH5XGm>A&ry_h_UO$D;LrjHFMQz%jqtEl`24lTJ4L6CY@IO)a&uBk$asa=RxC3wZ(;D{2O7_)C*lOYq{7I$nl<q4%Q2Ji!lv2?cdHpQ$6h5g^Q0ez*k@m-;McN-GX2a{;hsl2*AH{pRO%(Z~W2Eoz@n5O<go;;G%t<_s*V6tu;#c^u*j9U8YvvdkhmJ+?MR=`i(eWg8+4poUMPmM&kED!M*YX7Z3S&QpKSpg=sQ)X*{T===@i_iC+Z-luPUbZ!K8SKMk2x7rHexhB8$Jp}Q+G7u(0+r`CZ*4nwkU;_zQF6ajJO!D+bv={9pmw3RL){b1&HbJ1@MoeCEkh_|2h5cCO*RN#{WvZg)gtRt)NtbSQfAAyh`0+eEt}T|KN2@6C*wi+vO*g#owa7G}K!n!WZLp34D2C8GIRPvc3SX3y@#?Ftu!Ay!n}v{It=&EZaPy-hUYXEynUI`iFV?hw<8ZyUM)Avu_roMeMspyuU1BUv42@#TQroCR0kS^s-WQypF~31(nJvl_XZf>-ZA>N!sT_#c5ldT;+(>BK*s|ewjSlXHrV5R2petikzkBrxaZKhiVMJM9X$M?!jwmpOzY)WSq(HUq(wzi%&~??f+KFrC$F*EREOF{!+Azp&)e?gxRrcUy4|odUec2UAd?`6Wb=EZ8B=PgubNDFBzAuN7wfd{muCQ=KWuYd+;;V-}sA_<|uup^tsYjr8T_XLfnd9s<cpP1#v!p1%4TE7Jd%-=MtCUm(fQ1ne_KDaSMJXaSm|?ekO5EMBUnNP}-=pp12vW-(SbrKF4n&uEnpV?Iz-8{4B<^7R~4V`HX)(T1fv3nWGKFjS+qYuUC+NBlT=zZWiO05jW#Ev&}MUSVvv6@N>~R=3^aW*8WqaB}yxmCMk_p8m#mYuO|=(NBD8H8;u{KG+b$z(n#X_`1g5#B+`BiaU6bjl>RqI1A%$OMfiF61;kJAE2()oaRGh-ZI)B(YQ~}CD*P&5uOxnox9?3N+WA;SO}74c#u`uE!_jQUJ)63Rp?S=~XvVw*jiBBUyuW}r4?mK*S%k(gwlU1xCukhwU5;N#oP@8gR9~s4Qb_3orO8S|cs-Fg8Q)N;o>CLytN14P2E-cpn&huVY=Cb-n_A?JrB5AS!N0=mn#AgO`(B7>YagXFR_R^hc)Wh^J;wF{{zKwW{7~9{NF0xE$k@gb$KyZX{rc!b#`Ga=8W5Y{$5LNIG>Z8fMSu0syUgFa)buJE%6tu_?i%Pl=CBsNCNYH1sT5QyM=Xoat@ON7L8S^xRg_*(Dy38gRt8>ywz+6u5MM;8kWx{l{HQ2>7Ulh%s0jTRVO#BARH~>{nOF{A8DEK57GHrH%M&Z%E73;#j7sSlM|#Fkit(mr9O-HIJjzJ!jI^ylZH1_-5M!%|@>5qid`@aE%63KB#`?;PyE3&Fq23@h2bq)d^j)61%EPrUp;TO{m{KyOBuY;zrB+G-O94+7k<-q9E^5`W0A9z!5&Nz%br-@HM}_IPq*7`6EKPr@sjW0^OVh46F&REJ-ZEW#QsNW%r1)s1fAx=ZDn=pgV~ElCXxhinCKub;^`*U5knI9+J0DTZK@>R(pcuv+L;k{So0C3sGGEasKegv)?vgUbq>Mc&T>H%`)lMaSf6O;ZUn_m9bduNK5x>QMLHn)5ZTPMDjY=Do)+ucwuE($E{Y}Jec%64Ied@RmzmL~n5I5uPd*2Xk?T3|)D1AjdhW`qGlz0Mv6n~uUk2C(`@UMx-sC65D6Y&Us6Mh5nFn$Am9q}vtI{bR#QT%%RM&fb&M!cQp<BZwXt$kQ&i_+&xJ(NO9Zz<K`^=rhp@SoFu195vq&D$gD+)iCO?ue*!M?`Hqs7vSlj6QW-i(kv@&xv8YeXj@6*8ZN-2TB8w_MLdIGh++k-zT=kx25g-#1HUx9kwNQitrnG-3dQ{xHY1Nt<<%Z@xF(4MD+0i^Yj6HJAHJHn9t4;^W2#+cV=wbf2_1dX}Z#CrKw8Oly)l}gdK!y-$bdqQb(lyyX06&p6U2e#EJNcv>iq4j@LCDB8QH9@Ew$fDK$pgcSG8bBu>DuruG%Yk@%6cSwYT@Y}b)GhM{+9HvvD9zPi(YcgAn)X+pjZcsn267*{v?9)(6m%+E+_oIpP-h%502*$0QvZsuh-<J^N*GgqtGZVhoIevZ;0rMXIjmF6qWQ)-~p2G$0yeLtl!N^cUE;@`wKMcVfwF2oNa&Lu9y_g8AEG!|*UjMxmn48Mpvbd9}<i|~tRqkVm)IK~mj7#c9%IBJQb-5^w--1TWYn0}X1*HXr8>l{Pv{qg;1vy8DVqo##u5#ybUpU1ZS7;8V~u_du7z9qgHYRVX!GLOBfwKwDF9Wmefo`+jXe-dxt|0U|zQPKY~eZRyV*d5wve^te6QTi6^K;S0v8rwXnuN_8-w0}r^0)Hh+qJI5H)PGFp(66r&ui*8)8M+R8|3(yE=hru~{Y#9-NAte+NocSAZQi>{4B&6F{dM9aYPrrB{y>kY^^($W<hzaki}*YKFZ^Ak{T<@vsQ>Oixy*jh@mKt9YPy89|3&F%;x*z;{BN}To%jp>cl_mu?JpC5#h+06TIo2_{#&Ill@9XyAWZx3lnyJMBp$+_#D7EFjsFI3`#C}GFY&vGyYW9LomTo@=@juaH5^e2D;*^sBObw@QTh@8Bkhi{{SUnV1Mi)o&qMUP3vX*XM4yKkr|n<IuZV~7hnbhJh^O$!*yap6LM=yl|1|Lw{;bluh<$O6xzX`F{si96?Rn;2$ApM|kw7gvUci5cKSlfre+vIS@gn{#{v7cqd;<MlAfCgYqmA~H)S)z4X_eBaN*^grQTmeC2Z&Sf4VBs{bs-MHcfk)Qj>E4a|0l%Z_~EqCewWgI+Uht7-(IPa(okYoysl?CwSI&jK^%`CPumg1uK01(Hy#b){UMBJD6xHnZ^-NR_(sGo_%7scL_H%I>ty_JVpn`uwi!+h%c*M|{u8vEd05VvS4HfnUF?tj?5q8-FNvSxXDiK88mRP+(oCfpN_BbNiZ}z`SE+^4he}I`3y3Z71IhU|aRL5q{2Rm;c%8R3ed<^bUys)ViL>$cy?2PVcCDU_VJ1GF_&UCi(rBgT#Kri<yx*MoI=(Ms>w`XIJ3Ic-#KriTY(ERdGuC+8EFdny_lfAIFTMrwb$ko_8^oUYH}H0DdomY2nG5apJ&M07T_*mH*D+0$cpX#X_5F={o0P=M_+M1~L+Pf{HR2y^n@Q;@r2W&xe0Uvi1;p$42!9j*3-K0S-%F|MNJ~tK*ZDI<NuN5V!>8l@G{ls6eGjI7eU+FFuciGpVg|fc2I|T{e>WMc_K&FZDaQ4K@}~pR&lUV{=rnV$<M)C8?ic-@{h;G1{1s~Y0cn4RcnyCBe^%*7;vd9o_*3Nl5q;15XYpr<rz3KnrcZtE>pi9W#J}**MoHAKvqt^L^nJ5`!~UkN_BT|#t#n7}F7Y<o<W<Uyw10+}2e0GxfOsAM#NWZ+AYRAkpbmQ<Z&tj{pCwBA)G-@A8}C0$%!=3d1MBzh60_j7ve17P^4?)g+W$#CnW_JR@;?P6-vj(V#Gmp1;2)x&nR^{C2L8Jb`6By4#{~QXYPx{5Kd*F-c$;_^{}b(gCZ5OtjK3JM{Y7E|zOwrM+*qlSQX{1olwMToqtp}D6Rv$VrTj|uk@oG$(Ud%u@P&z;@ttW~n3x~mSLto~e4GBXugvSl#J>2(_(sG&_<Bn1lwL;K=R?{TB6h+zVytfv3*igV<_&VzXS@2;-43;<T_=2J`pQrL`I#?UPc`z@!`u1G$2{bt@4~21#C#T_#!mF}2C*r=5wS6`DZZ3a4yDpcL8Y=vWt1}WIvXqq>#Ed3sWsBRHrwkwHHgpSbu5N2M%x<17Wk}6&(PO1^kaPvYRrn)EKcb)rEW<3H<9+Q5{u)5j43zqRs5^8$xY7IY}cClUPHBMR~%oAzFN?K3+Bbv)0KR2csoyTGTt}oy9Rod`74btLtn+Htr+u|n|TQ`A6fA^h`I5(X|H`nr3y;9lyWMSS1PCU9Iu}xmc#c@YOB<WSQp<4UyE20pNsr?iM8;xXp@(`S?E*8?D*`w&PA+<Z==**sSdFvUe}q2F_g#GB$mLJplwZJOMFS{E`jRueqF{{hu9{<_uzFKe0O3ie0O|H>Z!>bRKV9Fw#2ujeJyIpLtQ2Dc~KtbArE8D6|w)aqnylP6{T3ECQ7d>RaJUPsXwoK6JNqtS8AYCfY<?F0AGao7QPAjn-PoPi_oSSd3({Pj{Wfcc-@3p1#jPbooH)ssPu|bM`A&|ey=%WtBNm5?1Jw?+oHsR__r8O7u13GJ23u^#D)>RI<FhzUm+I27a;#D)KiqXiNzNo7Q`21n<CWEoVwn^H$%;ti{^}3`%dcnL`$X4O0AT-D7~fhl2SETHMsU&l?EuaM%p(bM|1LY#`huC#@D88AL0OfRi&5d^JV(ez7wxo6071{;#(14!pA8!R_cbde+Oybm-rgK6=Q8d?2GS9n-=73&33J+yD@4+yVvlw>1zP}4`9A*JzdEchqv?h4)gF1efL3qBj&R&HNHkaEr`wWt%xm&&GBz54N~f<G*GF#QV*pmO4DG|;M&(!dPAuh(!M=8`je+8zAdpgzBg^#65qg2jne;=p!7MN{;VHFjZ^WOHC1Y-R0nDQI?}!ku@`<IW9mn2gKtBde&lS%cFm}-9coXzUijX$Y07*wrH;C&4r8lBO>dyr8Sm@#-4?Zpn7206*o%Jp5&Pq(FrKMsAoDVi_XiRC<2x#KP<m6Te(k8}j4}T`ynnHD!7=ITslPqz$+NrmKYj0t%Fv;A-?w<0-`&#x*ni}fbyY6!9|5ReJE?gFI9mO$e=ta{e_;yz58yu%i~'

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
