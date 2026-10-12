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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f70f112151514494ac859a50fa5273ff/part_002.stl', 'relative_path': 'f70f112151514494ac859a50fa5273ff/part_002.stl', 'source_sha256': '3c1d9df0585a4cd46d5955386e6a62d450ae8a0f1c6bc5f7fabb9e372d971eb8', 'input_faces': 864, 'input_vertices': 599, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4977419972419739, -0.458616703748703, -0.4062139391899109], [0.36192816495895386, 0.2170272022485733, 0.4062139391899109]]}
GEOMETRY_BASE85 = 'c$}r32UHc;yY>g{y?4c97c}+`!Vv{~!yZjMii(<8QL%gM1~Jye7WLS>Vs9v;AYc~+6|o$Ri800~mPC!^+xvZ=!I`<owZ3(4?t0hrI}h*d*|XbJ@4r*qOqmNS{9if6?dvB&+Zri~jND3LW!%8gV}=9|46QMI<ODY*Kl$=MO_z4)*1l6OH)WhMsmg$Xp~0i8G_h3i8PupsbxV~&BSw!I-EVl`5u*nTlzw2p??VR)KXh=vkpso=s`VQ;u5PL8S=}<l^1u8qr>KI}E$v>ktjn)nu~Hr0UEcW$wLhIozU}-1gKxe1>aIRt-TLTwv<u(1?a^^R`S%Cs$yYZui8Pcy>Nxq1+P@k1oAsBw`u$q+m8J5{zC-x3eCxu$@94`{etmZ=+J$cyzRb5jzkA29--V$^qh0vcMWIJ2|I>K#ZOWOmhIXj2?Y7>xRJ?qM_V3^8wxJz9eLVLipX$G+2l;kq+8#ssRdaFvytD*E`^?O7+t3d0e5ic0ul(mj<=baC(&TUFvCW6&Z`-uu+o@l|e=+z<aoct}?pLeGw`5yMzIr8iCDqf@=qqk7SJHkaFHY0f-<dD;h%4WgKlBLIN105%8v7=S%I$q`8|^3ic!TeJS()ooet4R`A8nV5pL69qg-_-E^*#B@iq}+*y>msbe>tPC&Nx8zw^y~L>HFQbVQsuCUll%;vnw!7-!Hbu!3QXRVqUIKyGgM!&k@*!k84IwgKxbzeH+!^Gc&h;(k${VzSCAvyDoJ%`or^bJI_zPrLVs=d~#jd@3^z<=juWAbG*t;<yf6D2H#ofmlafxsi)aL(~5jskIP%Bo^wtbeC2r&s;7EnGx^Rv3r|yixtm;mxlIP&5fsAh={cNy`=`0F`g&T&wZ5gFFRFKbQtRplTu$oKqxyVhes1!u0gF!?%K0`2*K=<*^3}GvHc~$i%3|=HO?z#m{F|3j$&VhlkIET(U=L}V1f&1YBO0e_`@`(--ej1M>Y(-HTVAB`I<jOKmveKq!B@&|pzZ9H7LxBAP&-avfAvU*RQ<fL_TCcrC7-s-(~#?PAeiduC|i6T?I*0h!B-niUq{;&C{4a?!UJl5+n^1*shpWb4Zicm_1%<j$(^bn&(?k?&XD%aYG?=R<6{S1`A*?ed#pQoliK0dsst)Oe;L}Z{q|9Vul(DC_G>S)hJ4$MSe5eM9^OLvWmXz|#hJc^_E)(!`PSceQ#sbS>1*ikmuix)t*c6(eo0i$LiTNORS(hcPXS)hI$tZtcJI$M^!u*YO|I9$z50Gv24~{@*e<vAzCHZy4LbgZ-(R8Q8+-aRZGY=;@-x<F-y4av|15XNw^rV|i~8|t!$>-gup37IR$D%g)!9S7<IiKfZl)BVd}Y%%gKs@kiO+A3=aH|xTX?`wPx#t#DQO-DqFwk7;Zym;Mv$+qtClk-6Qf=DR^ijQ3;LdqH|chqzMZWn2XH;L^X!uSSE;_mgKy~D)3SQ){%9AzL->^M(T)A>i=qtu@~Sh}=kNbcl7D?;IvsB^`_@A5PwMlnZ|m~$M)#(1WwFnrb<gfr%iueDMQ)|zZC{hicTc=VzX!xo|5~3~*zXie^GK~2w3phgZz+Rs-5kp8eIwfq{d}=E&K&E?cM6}j`}N6nLqApw<MuK6mP%pVJ`FCgpLaTqAIpZ34yupioWXZYTH&Dj%{;~a<tIFk#>LS(rY<~wUEj{Ox&E|Yv+oo>ZTI@9u^esv3^;OK-~RTde*0bd7GFOqNAY4`>qlEjU&=T84&hUO<qap_`L@>`!#GcGO1^#nOU}#wv;u8k=${mQzWq$MeXe{<OgCCb?dhrHE4CCmf7?oW^E?esHu#q50X$C=kFdWc6J38eX4R(k+1})^!OvKq%N-&=W1SzD>FSq!YM(6oQuOoG_R9oXpUu8Q_*CD=JJ~Px6<@#AD9-ioy~XGcF3a`rv@k_K?`&J%pLXRtgiqz?p329ioiA2RInU!FjC@O`vvG#@4{MKlE{LXfODMUM+UZ~`gYWS1+)2OvE2S95dCK+Eu6(QTsl3E;yx+B5c>YZ7N%PU^U)tcSZHG}iS#!Nf){kfV?Tx2h`O2M*e0{O=b+UdO+T9(LZ}y$Sr~IYtXRJR<kZ<xWOOYRWiOXrZm&TQ&>lB*5){++uzCB?+&)+&K`L=&H^Lh5lMVi0%O~(zsb<KSmN6Lt`<ZI_CTWCqTes+{@m28+7ouXA&zAAjKXG5+}hjc!#Uw)LE%I|QK*GH^lmcaHGUHMkwQ-3u-MZS9WB-K;>vklD`byt+ZcO-?-e6jd#Wk0MGuWu`S>HbBTyusi*ds^v!!E$m2`OcbM_<koe3*}qSPBr+}G==ij`#rdx$EU{Yk4yFF!oH*9DXNeEG47w<9Spvb`2<}jD-DaVAM>8)VP6~NTm1?cd~1Af%C|=(C6ONekLH8YVI$qA*iI)Je8-h7bX{%rP9WdfVl&UL5wH0C6&^=^#{Kxvnb)bD=COu++l^;*UbCH3xqPe}P9Kl+u6#>VkMq>t+ctAKSO=^fhST^_?JLOFu5)Y;Zl%!i)$Gjm$@+}yZ>^l?_9>||J0$7nuQReS-^ZDJ%f806UMdBB$<Mgn2#ezR@4}~cNUcwP#`VUiG09X;53eNsytegBr*+GfPvh`$l_dSVR;K<%`DWiDeA@3l_O*F!8^ZZ!-#LWy)x00*dP@EM81;*@VlTR%vW@@G;5)YVq5C!4_*IF9`8a%c{Fi(xKj#ecEmk#7-~RTSnaR(1&X9WzjZ3qy<XLl#>Q(P9otLzAUOn2Fe~0^#W?c7vd-^gR=faRHhIOEN_e58|P59I=FK%Dbk2mGuN6s_(HsSMpKXl134m(z%eATPTCH?rZ)_io?m9Gk)#&ex)m-PLvsu7fL_ARF)DBt!+rb~u?Oq@&kX5W%Dm-3aK>}%shb(=@|W?yliNBPc<-WT=#=$NWdp6v%7M;Y__cF9y4Z?~cn^z+W~UEiCu-*{VseqLA}`tW^`$+rui%K5Qpf_}c(^IV~I!+xi9ynZ}b67TVO+J#T;bLM57ew^68Eym;izfN)baiZ+3#P<;$Z}9y;uB)x_o;*(4sAmo1=U~@su6(=jX`E*Z=jU$gmh*kan5kU;+CVP<({z4*Fl-<DF)w2E<H|1X%Ut=|{hFHXUaVofHSEjt^U>N^{kXC<YU0wj3!moS%2~1capioNosZXrPx-HA#2Uuisw|vu@|D$D_`b3~`x)!fG|o5s)@ht?`L<N7e!MwPRipWA@0f5{Kd$VHeNy#)#yA}OiT&94!-oB~c5poxoi+GY;miFxvaql1*Y@ZX?N{?Nt~2xT`l$I@KROl$CFy;w-<20-48At5)OTkM<z!s{+&yjZwQ*}de<JBizP|n$&w-Qjr9`{%RpIONGoB|mUV9_jg>M(Wp?qy#i}u(1`u5lR8TVP94#RP2zUpag|BUlp=tg6{c7H8=!+y2#jQL{rwfU0K{#a+!h9y#?UHDGn>+`jFXRSNI(Eb_gzwizD+WPZi^Yv&KzE${!`fK;s8!{(Hf5E4D<Xe7;%Xwt-wRxoMFSEqeJT?0n^E5pF67zhI{(?{WMSK_Q+gV#@%)YkHDC2z>=-Vx0eKYx5e<@i8+4b$9t+!@hTW^&==6Cng%?oXvH~V(s)9<K=fqwe_!g<7%Px;3KrugaRk@IGE>MyfzN$t+pbyklbsGl*9EaLnX?ZVg2Ys$Ix<o}QJqsiCKkBVFHLfWsk9*Xm9v<pAu{QGZ>#iZJMG;zL;cHwL1aplMhem`KoPB8h}b%OHd72i*ou0zaz#&t+pcfRj2UFVp6?K;P<T;}^K({+^D*RG=!k6yd{bmJ=H`px8P*KhW7&FJ}x`TEf8YuAVBlqZMu<4U{!bmdd|x#t|#kE@L9Ta&L{->QiTNA=^%QL`yu-<y1=@M(L`f+zItoN=9R^0n)Hdl38P`v|k2aUYSj^a*{xX!j|ueEMCW%?ZOe7xz2SE`04i$o_KZ3H><N?x$S&)V@b|ozVBYcE4u!wfi-7cXE_|Uda2w=r8!R{nfE2_2Wdl4>kMReW*Pp;-q07iTm8>FZk3x>5o;zc*AoEv!C%?VoJpreLrf?ZOp#*+{Ut-ee-i6v#&iDvV89uqwh!Uxs%z?c<yv-W{jbo@f^(TXFLZRUO!epFSO@!X5S%v>W{vwV-52Z&lSzS_FU1id}FMB9%;`lUHO#X$2(3xk1V6(>AuG7TZJ!wJGXC*)3=-U9N6q@&w(xX**8CDHv8IhX2+O4afW$>=i6pqd%kTcT_9fH&f0T$v#&jecV=oGuOC<1bAGe0J?D3Pyd7^CZ+MRFXnH4Jf4ml-b?Nf{-L~Y{czr#!eA^ZG1pR!sE!j`~V)nK7FOHhU6ZG?4d%t7$wf8%gs%;Yt?STDizWKe9+1K7HIdc{}r(XxO>l3rDU7t7$EIel@M?2nUE6(ZXyR&ycehy{wwfBI|LV*_y^BwOo&A#>?)ADoY3x;`w_n~IrE_}*Ad;Nl8{NsJDE1&A~eDg*9ezoIrHoJI9KQFZR<7Qv+$$ys0*&TO9Umxu|1hcRF8BFc(*z)#@VVvMQ2eYqz=b&85c~w6iwC^s=zV_XPTDitm{qbtwftY>mI}oMDmaB$-$9F7dU;B<lxwiGH{<t#U`?x<P-_mUgt&7gF=iAYCtzH@SoADn1uh&=g<3#&D$CXdNQ(GkJ+dtzwACvD8KD9&JzC3Tz{-pZY`mLKl<);qd{OVPBJudgLKjn8E$Nv6W{9gXhQ5)qKoW$4Zxkqq0(T({%_+9oLd&-h;?~(8m`DK4(|K%<||J2Ds@6(kvtGS#DUVPr@{s%o*v`^m2*I8$(a((X3?5Fo_PXf6<Z|YDztu>FLoFBP9_rsS_J$s*EKmSoKKmN@$8t)^|b2$}%BHt1iyPWE|`(JLKZ}Rbe>l|KB`;ExP_YJ+g_<hZi8>{$u3mANB>O4N)9YvB1?XSJ(Jz0+Py9Mxh>2btTs?X$R<g4xO@p1j$Z$0I0?n}Pq*-Q5QD^U5?StH1|p1MZ!O<9q$l*(&4hOY-ZMUd|(+-((=o5J_0&ds~Yx7^u6*ZtPjlaloFOZ(o;>}%hfDNW`l>F1aBJ)7CrzGt&e-puuX<VpLrZ7)stllEm7xc*am@VfKnIkl&~V>0Lagz<ZXT_=}u``qCA51vTAB|T-m!T)<EpC|1L7twZiQn{T^ed2PKeB|+Y=qVr9ntc3ykw-CVH}(E=uK(X{`8`XQlRQ2@{%6>)y>cJE->zJeuG8&h>+yQDWjghj`q+bf$NHY+TP{4{@4MQTBi}N(0nghDDUGTAS-trF)jE&MDOY6yl@n5(^B+{FeCIErLnwb=Bl6APADVsb`$K!l#$3Mk9=zzk9jP5Ad-HR2_jLX)>;6!>Z@1=b#{2Dgi{Ibv2n*5sw(&KnK9=%VCz5|DfXm7Gi1VK|8>{y%)x7yUxvX~xw`)hPPpguA9$vPb=cz|0zV9hHg0H8w?=(vHxMmoi+BzBXE$_E?N6NRB$ux$xuhW<7xyGBX7t-4<A@vI8{u-(9`QUx|IW*qNhj2M9A8>u}Uf8~X{r~Y@sACNKc`tJQBV{t>uNcqAb^Q=ukDT=#%Hw1z@ApL?ZvWbTtMtB_c$Iw1)_HW_u1s3Y<(R%-HTxOguWsAG<uw0*>!Y4ac$`LZ{-1NGeUv;^W>I@~IdF~V$-ML2Z|i6B@56?ERD<r)`&?_@D2!V^-`Jde7E*n@qq+Q%Jum3{OO3p0=y&bALCv=(zUS{COO0E^^Wrh*R~W_LCu9q!_seRNbUv=$2e_UuYzuh4yx{(|t6YBXtUpn?ecy2XyPV|lmU#?+@Avcr*K@l+kE>asyxy)Tm28+V+PK<PhJ5S0sl4CXQM^8cd64fcnTy{$MxR+r?T}cJ?_WFm@HkvO?q{CAmC3gRKd1XYNA7Qes6KtY$X8eF;rhgTZ>Dzhs>b;d@zkES)(w6j|7b1FzZlNtygNIM+qqt{e*CMYd(b*#ztfO?$89d(JKJW`ZH>5`<cIWLSRMRR80lMo_InIPJGWa)$I-(^zQbYV`W(FXGwt`g5!^lz!R)&&;^W;JmaHG28S^D1obyvgQNH!JIu7oarQB|F0_c9%TC~VA{`+#yKfR30-}j!sC(L`8{re%@4hL)<sGN`}uIEx8e&2m~Fs%btM-m?wzSp(P9XyHpy=YOozgL|#xg9oa97*b5g5M8^&f@YT*R-bcBWrMee>;B%QuH;ATQ#Z~KPSjpp7N~^{KirK;}+~+3FZ6dC^!B-HfIRG2fi?zzb9OHjgD7IoyyPSm(Qm9SiU+<>!gx6gYzd9CEr@8UR$ou67nr?%TRr6mkP|MJl_?(-y1{tyWE4Hc>Jet;`+BaPxZ9rZ8J*mE9Gxe`L>D622eRsoB6$&@3d3;c2?(Z;rbLg%l_UflW6;hliY4k{mFL@2^qoTR^|K>dHK7Vb6<_8{DSdZpTbl4yN&J>d0uZz;QBnx$;XwxY7T85dXDqI{+s*j>Eg~*zVCT1KfV%=ADs8q92dC$X{YG^NBO5FUyr3+z;mOf+>h}g{ditoF|@PY`H|Lh%~v9K^6`GNiP!TYcj1RpIZE@3V`;lEC)YEmA|J2!Q(jk79~j!xn(RHE+W+-aF6ZE@Q-*$l?;JRto}1VwH>dSho&Sv6IVL-QZ@lOLUBB6nzTon&2Gf4+8>jc8awh$2sE@6E*bFKs@C_eto)~Ti&vAWt{JiIK>gV8o2@a!irKEh|{Om)?w{>bXkJ@ulR(g(Q`7nr&H_!PgRDPR$<g0_uk?)+heT?3>jn2&F9K0}>$}gIqeCM!2{Qb#q+qfV73-SBj%;mU$13c*ZU(HgSpO@o0-!Zo^uS-|ix4rL9`F8&kU1&S6vRwYEIsE<PH<Rf7f#%zPyur`gaNT8BE$rvF@pG>2mw6rTUY?Klz%H&&TGKEpr+fvjPjpBAu4d(%MdUkbvF~|`^IJyFBMq)^D916Z@hqNq-dxXT*SOz5d^4ZtZ8JWu4Y~RL@j$L0$-ml$>v>~0e@|ZF5zQARq#ZwBoDso(%aJq4_v*~~-<0C#W#@`U&^U1$$oaiK@_Z?Dgx}u;hj4xN`>^kGejIK8b}%1T_A_Vn$E6k-!|$~!4q^Y**LKofW7!|FgnVbFb#%Pe$OyFC0rsPo(mJ5#Sjz3wD~|8WV)I2%Uiw<D=g&V;zItyp_e+s2Jl=AB;_u0`wHi&w<-eWlKOvl-gRBalt@o{~w($Mn;9cBbb@p-o@ypyk59-pqw!S{Z^=v(q+y7|^8n<fqquib?_VImUn}2A2StCzz{v0>H&pq?kRLU!Gn)|V0Z7#<;oY#lY7;c|45qy7#_0xXw9G4T`CPv?1)*2VNeFiq=b^g-w`Q%3>a(x;#;dbyy`HtEr=$fH_ZQ+5_^}g+1Hg1QjJ!b2D?f%`_?#MiYf2uh@A6(kX&h3Ab%Ng|-*Ymq=gQ-4Yw>ZDiX!ae$Y28!v+~(uD7RC4JU$3G22=ylX&hPoT!I%NGo+z8{aQVM>;`+oa<N4d<9@>-d-<?M%4Wx2b-{<j=Er{>ao7d#`X9*9ve4LjZQ(~yU6t739=XLfg44X^-(<hu?cn$Ys;}>-OY!7_F<)81)<@bBth_t{<?w3_LxqZ^F`P25>UU4~i{@^?o(}wcbz2W*ls?XO6xPP(M_=s^;gzlHEKdcF*{IA{UJ-j;oA@|qiM4CrxnXLSNe(W$VC*}EM(rMYrw@-=ZaZ-3AtpoNpImovS+sOITPfh1}nv2VyeU95<PLCnvHz`2Aw%$4$<QPT%haz0g4tFm9-N9izUrKQPz2&j`eC25wuIKbtoc~wk2=ad`$K^bW=YFr1z}KY(Dsee!9XP+j>}ljDd$NBc3(vd!>LkBThJWQ)B7S5C#Z#b&97<tjP(R&2ail*eN`|`rCyqnv{eS%v$3_k6{a^oy<4IA6=^}oH_6Gk99t&*;9t$1~{Te(PJO*k9j{*M#-39&$90iRBM}e<G?}M*`{}k~I`W$*6{2ZJPy$enUzkuEWzW~34-U7b_zk;TMUx8mEB;SOd0pA3lhAso22G0;-g|>$-1551(p5&$|(?mo-H-RI-YoIE44R`@`Gk5`bGSm*94E`D+d5DOS&^b^$cn<gobTjw}I2EdbQ^AL!o4|*`v!T<#v%w<}k_SU4fd_-dbWz@lHYz3bU-X64V)!lnVhG8#q4mMF!Cj!ez+J%Opp(Gkz*C?R;3?p_&^6$>;Hl6B;Hls+=wxshxGVH)a9400gyaU$A>amJUtRzCA|$sE(Fz(09SIHv&xg(d&j(+C9syqfKZ2%$AA!$94};Hx!=bam;o#BG5#Z6_mLe)Zn?px{M_?Q@M@Vi8?FH_Ier<}7Tn1VSELD!7GSDYr8IsFE{{l;ubt;FtH3v7xJ|w>rIpu}^r!Y%RfhK`dzy}bLcY~$&f_4D+0+&NbE(DgE3z`j_3!DWZ*$pf;Cp0TqMjl<h<lG_(K+8k(fXjoe2+1{}Il(o-7HC$m1zb=>UZ^`XE7%>ZK;4wj|4GgS%?8c{&Ic_7&IfJ<?Er2C-Ui(b-Ud#DCV>;d@1g&J--9cnzh%EyM3l#zYXxqB`B)nBwGOm6v^2Ol_#cHs@*9Q6l2i};mc9paeZjuij|a3oxID(C<llr|5OEG6ITCsZ90{Haoe!Q14uO6T4gq(8_5pVR4}yLN9t55P4F}Hw?}Z)&?*%77&w~@d51<dh55R72te?O#Bo~0@b7Phvxf;|HTn*d|>J4rN?hNe+?hNh+?F;S){vIJYM8rVoH_*P|Z@_J#9l>qE4WZuPhTtktPjD4*9%w#r9`FaWfozKp2+6-gAA)}eUxc0qUj!e89t0l+{|F5S{|Fuq{SG`F{4KN(_*?J@==b0e;Dyln;Dz90&_m#3;7ia8;7i~~(BHt1z#m2Abz@bazkwCZrC;Hl1OEz+LrC5UjRfxmPl3(_PXTv>hJd?)+d{j5+k(472Z6hSCqw6eCxdrD_kwqT&q5QxXTkTN55V`pS=?CVyvl-*TnJhKTnPLXv>Ny;Z~(L!H~`!Y+8NvpJPg_oJPbSv`aO6QcsN3Ge`pA}KiH<5lQ!tLU>mp-v>mt;*azAO>;v|KRt0;3^F#B3^I|;ZM@V*u%JJlm-;$jeV{u?7I2Iv!C3GivC3qlo3V0ycAKDG<4{iW$3vK{z2JH%N1|9&N3?2Yp0o?&!0gi#51;>EXp!dLO;2dtOa-8KrNG<{`1TF%u3H=IO6Wkga0B#KqhIRu7gU3LJfyaO+LPvoog2zIKgU5mgAS8E(_6K(d2SIIM8^&1>Lb5;92kZ~74)p?82N#6q2j|ClDu|Gr6)MM5R{WNH8)GaMd;_XNW5FtT5_Bba64)C$5bO;u0rdx$0OyA`0Oto6hc*Kj2RDHZ05<_ogsuQj1V=+-z|r9A&@}LMa5gtqIp(q<B$t2|0ha*Rh1LYu1^0lq2KNAuhX#YkgJ(j=fM<e#fKCMe0G<UM3!Vj@0386H0Pcy9+y>em+y)#74FU&Y%mpGO*ML?B*8mrW76cc>*eZ;WoD(X?Q%<+f<18osCONy%%x<j7_$~cpgyj8D6}%tZ13C%Z16&5`4K4%D0WAT}0nQA~56%qE4lNGO4lWIC0xk{i4xI?@4&Dci2JZu3gI)(;17~t$m18jzLULJX32<4kAG9vm4?Gmw13VNw9XcL79lQlP6TAg{7WxDDEO;w)7I-Uo26O^=2KYN@Pw;nOs|X9U9<(R8C&p_%gydS#KyV<&Wi5o{qR_(N!WeT!q1nMj!6n^3kHwNu3)q5vmxR^=7lq2-^4WrXP9UEb%ocsOLBurZI`A}b7<3JIo`{VimO!_Hmy6gVVv&enM2r)$8M+9(2sxWkmMn8IJh}ZA=wk3<<VcqPpZJ1A)Q5Hgw-ym9!UsAS>;tX`?Fg<1ZV2rRZU_#5_5}xkeWCrqfr|X5k?Uncof@GHWt(miu~fu%5kEjTfj1#Xaxl~eoel1Yw(AU?3Lb)X356~Pw-7N*gdbuU${vP#1VgobhGN^n&_&?E;EvF7x^|k1Hjp|CY(t&3zLEXX6y>)@eOtpD0_~(b4yj?#PT(-`G-wbw2>X&;3}w}VwgwkLJ&Hk_f-8&oN<<B4ZEy{6C4}VaB0Qi~ptZqOz-6Idfy;tRAtcv@RtEb)D?%%St3f@XmBF6i#?Ttz#^9>ZO5mzsFNEX@(CXj{;5xeFtb>qT5?T~o5-eXU)r0y#iz=VzT2b^tYj7>72iOB`R|`=E{Za*OR}4`WeOMOlsP(7RM$l5=M&LkbU9i^H+8mV{4D|!I5ivpGdD8-{%@wJup%cKX!447QMXVAr6Y2mvkTVn720RnoQ^Zga%@tlp`h$IS?OPJsP}lwq(LYiHbo~{8{tQ4FTK`J+f;Lw^j|a(Bp)HlqV@7ggXiw$y7?bP?ZKHf1lai}JTY#&9D<WE;t>yY5&j(YXYr#{&v!Lsh&uhvoUE2&ry=I~w<Do6VEs>-3iPR;~q2MLpdC>mg{@B+%=z8!xuy&r?in6612d@G<pr^nN@M`D@<@5NFyc8i>o)i8Skz1UHA1fS^uRtq<Wk@~(Z331dc>%NoScc?L&^}-plD~lt0?Uv*651OqLvjSPJy?e1!_dZH8ImtUD}iN5{sWo|EJN~Bp$CMX6me9<acDe3axC;DSmqppC-s1CTe(dXG!A?Mc~Q{gVEOkLa18P!CyGcBaStK+H-zMy2+3Cwk}p9M!O`H;(97VxBKC=RfRLOF-4B+U1YRm)9k$yG-Ur<P-hgc+UlDOvL>lxD@O=@#i+BkA6P%2FJ%ru||B3oNgeHUkKwG3iZ-AvHfYZQNpxePxcY?2g??QKjWzK4Ni{Y<=?gZ~dj^u?R=80GY{So|=h@ZhfBX1G@z5=`gd5ch<+_wX|1H4wmauL5kSAth!n_rM4b(@G|A|gecLOBU2D*@gPXe2li+wDMX!+y7+Ob2u|cqQtw47vn-PQ*147opd|XG9zXA4J|o{5=VrggnW&+<1K4hTaEXN4dA5x4`$Y{cY%VupE<n+&+)x{n*ET_-7D%P_KjFT_QF@*F*P!_n=(KuSL8Q@e2ADT-sfn3q|CFmIUV#Q9?vvXj!n-av~~2tAb@t8T`F0xE$02EVVqihKTwiDndQMO++*nQ4RVPI6y>m{JjadG1Ll{+6dfGgtv%#BC11cL%qSZ!40qvPn7M6I%)f=kNpRLTR>}oYoLr4P;YPm)DP+n_D20A7Zj0QL;(?bpqZiB!I{Bt+&Cn^7n%i{11kL-$SnxYi9Y@4#+n~oTxcomrxfxfThO0g&{|+Gus=d_TWDRd)DGav7#p>qb-{H+)D+PU+8Qi#svxf&%Bcgb3$BZtI?zhsN+_!i>L&N!9@-7u9^3{R1nz+Sb%%D<aclf;i@a{o?%;0VAcW*D(5~Pv;Lc#FfzX!VKyX8ZWFN3pKd3L*53G$z$=W=S+7#*wZVGM&^#L~nw}Q3=w*q&Bb_RC@cY<~WcST!CeucH=KZN8D&`j>kQnP~p5%Eccn>%Yh_s^Wo{qt|Bxe$`I^+swTXg;viY+!d0FGN{Iq5p#AJbI6H@iq9J+vj=p4)v7vR-o^|?~o%|Y7Vf}+&V6(`z<vSLULXa#h^u?xxu-yt>nMOzWx&N4EhB844e*q3YIy)!gIpE1APL1f*i@RJzt{z|A9V-O8+@R@?#O5+Pb+H&h(}KiHOht$#2dS!~bA}c}wGGm-;P#7iDF9gxRTW7W%%#UHqTCFfZ3%{`!AR-i90'

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
