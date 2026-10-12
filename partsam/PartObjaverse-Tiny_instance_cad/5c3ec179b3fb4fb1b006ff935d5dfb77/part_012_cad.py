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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_012.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_012.stl', 'source_sha256': 'fdb0608bac656b1e8cff716b7f59add3eeb6dc3497b75fe6c98cff9ab03bd942', 'input_faces': 486, 'input_vertices': 611, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.52489471435547, 74.46100616455078, -0.3037281036376953], [5.65997314453125, 99.41752624511719, 25.526073455810547]]}
GEOMETRY_BASE85 = 'c$}qtcXZZ9^X|UJfC(K;2O~NTV0y6$SagRLx*;^tOQ@z}45AkUaSSmXzjO#C6o(K>5H<APOcgbB(|ftI^9<+XyXXFK&+q4Ro}<;H(d_K(?Cff#*Ny5W^YvHw%coxUeU^A2SSgJ(%3lrc5;3qxr!E76`t%#-Q5l%me_xI>8a8jxsFg<zR*^+IcNx$rqDY8Q<h!nwiWE1BbnP24Frq`B_I)EdchP+94!s6+A$~yj4*j~&dC>}`OBXlF1{OD>jQ`=^H)Mj{enMG?j^>oL%}s4n#M&Z!Yzf|t2Jh_O^Q}G_FGeu0tPCymxjhx~)(!AZ2k_1b$U8?mGH)-h#(M0-DU0c&I}W^=syg##o8GARWOL|=Ys-4frt6ru{|2v`gSS&czv^ETdM0It{(*Ii@_mm>quw*qAs+!fs$Eg&zxt>d^L3=&AHZ98z?++4r`mqMjOL9uXQAg0wAWsCk9q4JcxMXiF~gUEuRR|6bD&-`8+f;g@b7m+KCA`vDk3DD>l?U+<(&*^nfKN$345-hUgu02$hQ-|rTF3Tq0-#m^8Hzl9VdP}58hir_-NE?Pm5#T%Kf=1>rDXfzWkMWHwe6120iX~b)aX_Qr2S@lzzWl8~j4>&PTDQOHwJ;Uuy^JvCVymha!)eS5v?{wWPg+M=<YHx(+>kq2C<<-Yf;)-Xw9=Is|(5M?-%p@ODk%&j_Dh>>uB_B)6+y=9X;#6x6E*y$WLarY&Jl<KN)7x-Xdbjs<W3x*zrCc1o~((Gb?-<l76sZQsefHwe6$QpQn+0?b<hC82+e^yBXQ&=V~Dm-xAOq!{;OLPzL-1be)H|HizNGack-gEvFLo1x%UA=v45C>qG}<0r5l)g5*kw>K2!dXwL1!g`XgW<ACz@RqOe571w>H@*n#_s)hr{iMHMEo9!>ApAAxx9iR?%<`>{upZL|uS$Y<gjdbQ{|{#uVm@Il{MH=yxb?xSX~Lfqd$ML?-uQhd>#_5LH*aQyo|VF9hkh$yY<~9V=>4#B$!f8G4D)IbcohRZ?!adT>mR)U_UB3w$j7^V^D@763dZTf;18i%e_$Wxy_1j!lv)0a=AEaFn0I`WL;u~371*wE!O-(o_z8zoalLi&Fz?P=3HzsXEzWj^J_ukw-EWYex;zhGFLsA{Yd3ha_R-QTpLmgZXUj#%-&zGfp9SyTd{O-T5B#?80`%M+%lSkVz3H<3eZiZzkguG436;3sp68iYd7=<+c6GMj7=IRedLLx{cFVYeeC!HdwF7T%xmbdEU+~V`Es$?EE+1bXcm{TE18<ZVT#D;yeTsP_z<|8};PNd0`6TSjHj3@>zE016wo-$)w&#T(d;`)kzy1X3?OFx==E9j+PaW{)-bD7lTk#+Er?)zIyF@hVO_*DTuU8R0A<*Lltt-dZ1HgMLA#bQ9KWE@$O7O<t4*0R}lkri3cRO`wJ#PD{Wm(V1<EZyWG4#vUKVRv7F^+&Y&%jQ#{BMp2Yqs!Pq2K867yH4D1#dj+hW6&!oR!<v7reUpj^*8M4J-1or^w#|uWl{=6w3AqUs>|xc7OK2(Gt9qzBuNi-AACOI(TnItRKt_6N34^!om;x2km-N|E$(;rWXA_f;Y?GM7+H@2L4=G*fYMPKObL#x6XriKjdZqdvAj`+h&EG4O_E6&70tz_TW{ILD^XU0q|<YKIFYeejIORg4DbA4eTuS%|W*FXOT~Wym`N4em+KsJ%Pu;Ur02#Upj$z<DkcCmYn_IttEN}io9`@>$QEw{yg=t9#d(&JN5awqlgDtU#Wik|IxfV{iyWs5X{TLW8wc1;H|uySl$@)i2Z2|0k5jA!hCulIm<f@M9=XJ(C;Rk((SeDiJo#1%v-5)vHdDQ<kvut%G$@n^`r*xJ$f7UMxEq(mH+D8?1yB_;pgq=Ilmc)j^*I?7V{#WtNu}#+i`kjcILZQLc6Y)LOdJ>?;Q^Pw$CZ%-8JByB-mr@Ny+U}QQ(c}m9VqkM7Gl%CVIY)koJz;!ExROyqkO@czX}~!E7yhn!*2WY&Z6URbTWJgC2KvPWY#U*s}+Ej3W<WXMXV36ZDt2ko4E770j!G=y$85$$H%1z<YB@JlId-b-z3Pz}sKqC-gkWo82C~)l1@}(Ub!mCuP7pg&?n{AL4j3f<*sB#HU*{1;(i%dUi_u$Moj-cT$2kt|9*I%qdupm9!lCSA$oJ+UMuv8Sr*Tj61su#-niryd~pQHN<%I?gZ~m#JF}|U|hRfg_rSe#~}~cTfnQP$QyPp$s5DL8{;I;#MI(EquPj`n(|z;26@R07yC0HkEw(moNwI*q9;Vwfj08FT@Sn|`P1ry{Ha1kkMJsJ3FlAC5IZFgJK3Yz4=S7Rf62UX{4LK5c3SXmIe9J%>vvlBqt{u6dJjte-?x|Zzp)d%eN*O(JV)6cYZG`!<`?_(dd~mmdeO5J^_qd0FU+~%y^`nM^~m$qAn>ltcWOr<&zs(UqQAJzkDG?%WIh>qOXgYUk<5?#m!iG9VZT}Z0ME1T3h>64`TEj8)H?vYopUPmFI~X%uf1^z>dlUMUv00+>k!onyqyQ@1l8O>9r|Sv?3Z<geH-fyXPp=FvJP<uVZGth2mfW=;!MDL#?1}h90*=L#(KtVz7Y23!@9`ZI0NS2@CA@h#QMrMHy{sho)7;#!}>~vMPuD{bS~QUW&IY8b(*_&4(z`^0eP(I&i5=o@n`WT)`9kbwHyylpDCy}y{r!(A7ejTZGxe{E7qT8$IqC@>jpvpQ(x4(rUd)bJhU>K=Dm005pOk0VEw%DXcqQc$Wr8i*)~6S+r4}Fvme3_qJPJ4%+K}KJeHa5yy1s<zPsZD=he;!n72R9gP+gOVmsCFy^t@l0QRgJ8^G5G?16l$2>9W}9A1Yzt$t_Th=G3Zkk{;IZ{Q^6U7vA?lPZbaE@$<#Ox&)qouOxW`FC26ciJ)LjaRq8f8Q?!`=^S{ygeuw^UH={)^Fw-$-KI?UgnGM4|BVoj)4Ao<<T!`p73~a62Uu(IbqMKH^_U3!Mo!sA<s;>gLTdZ@TznI`fJo&jze!Gc=IvlcRRNq@^*LOt3ckka1QZVN%%~@h_{K~D8B9w-tqx&Ew0FU!=4cdJBtrMyXc9F{gVy6m8?AUEcbuIeDPth^Y=U0x0!XB{bRfu0zZ7tivB%Q6Y(|=yb~?+lzDA8&udvk{s81vk@)m{+%gFIbF_m$m&9P5yr-}9i#*5uF3)!p!8^l+pDFtforM3#f}Z%Fkq@i%27hfg;&#PUjQ0<{pnudotV3osz_^|P-nqO6@qA+P32ndKwHy31;3US&<+;c+O}fDUX{W$%EAQRr`DkWG#9IMZ=FI?(bMN2H5D%Udh(mY&zZ_R7P3TFG=lbCpbF==N`C!k-7Ladw@->f(3>o3Kr}2oNzU^SoyA1I2Gw{xw$yk5Jr3N2z7j|CQm&o(iOh2?MeGRnNh}y#X3nv5bPGLRPnarG@&D?J?vOTZ=Mc!L}2IFP=OXgKi?EBgI@?*V}?mBpLGvYscPxiBuA(46WU;@TV_bNOd&FH<5_tZgq_a?pI_3DUC%v%rr!FL|@fb9&Q20d>Ii9e4fvH#0<1MgcAd{DY)tf%st46NtcKJb_J@Vx9STgtqfW*63P>#yLs{>^;mohR~K+;~J9eRLD%K|bFk=&_D+zOt(|W8MxvhV}5;5e4}Ad_U&BMQ>tUtY3AB`~CT(^sK+tH1t>6P&{9_;H{S6%^!1c{xo{@0)HY8`pYtT{o{Nn$-HqWH}gi7Tih?s;*aUrp8mhU{-|=PxqTT;=DoRtFkWiLW#)Fx{xdDND`Yk7td#aN=Yf*3%qzcjSoc;*g8pb9=Dk5OFZ7sPi0^y2H4Xd!%nZbHv3mJgzB+j83V5SgW;~b0XJy{*)C=;hr{!S2h=+OiO<T10Al9)e%iYv$&$D*mW1<hRKZ_h>-ufu(|Mj=`v41k}XWn@T-r1U-^%zA{Lq2Ok_~)RTo&B-)@;BVBvNbVY0_O2NVmJN+ym<lr-Y7NCJKm9nn769QKKTO!>(47sQgOTLNIo<IxAFS3;c4cTkE~Z8mWMsV6PP!5*T8e!#&59h-L?jL0%YB2_lRSAo=jriF#Rx2Gd<<?m{sVIAL~zb7I9c58uQDlZOog$oyL5(Eg8n+kTuLZnZ_gDc38+K-G5`=TSxd`CSe_QbS3k~-8qP#gAVljgSTs*LVKO`y#BG`mxEt74}Sj8mdBBKVj1+8o{M<cw1MX}$6dm_`|1efbC_7ird<sAX}7UHX*!<mG;%FOd)rBVi)nI)`#p39>|A^pdi-anWIIbwfxPTP+C5}`Ntg&f$iAhL{Zg~oc-Yf@Amsa>Lw+6;1wLB@^jFWC(PX*q(0_6;^lVMR`O_Oy4fd2%;LG*o=MK|11bmr6h^s?IunsIy7JAkruUa<`V4c}8JL*j<d3$}ni=6iwTuaG*4uk(4?`F)`dlrG8WFij_JIM2+)nftp;<51CI{OL7r#F^)(=Ncgx0yfI4?mA%UbO(Pe#wmI?w`g&&zukFm)L{6UNx^5W8PU1i*^mo!|M~(^<@gSf2aw*ocAS<-zs6u8<DfXhvq=N^*$!&dP^0A|Etg7b(E_nfWIf>I_?C<OTbX(?P{{lnSJm)`zK+NFY~i8ui2ANbAEQxPXxaeyjw3mi0ywE$-LPP``dOq>_2;J<N}{o#`PG?gNEPLWXxy%@|<pSy>91S%o|}ce&^oDI(ET4=GBkF8{wR9t^2{yGqof9;0)*IO=s#|ANJ=8ykD>%yyQITI=h&+hPFVzG`s$h^}LT~-do|2=qbVZ-zXW$yt!2P(6iWg4gcg}`E@by&&g|?&yD2onK$NvSL<VWpT}I@SFs*>U!W{`kC3c4czM5|j?4Rk+GUxy1M^_r6)_FZ*H3@@%<HWD`C(6)ZErch6&%UD(LPxAz1L)iz5O8HM)>Dx@ZA0U(kI?mTjOFpwjILx*}idsd26!p@u@Mt&nm{e;f@C1D}vYav;h9d^20a6&I9>aURBQef!DM1X2Q=4SMqwyE`8x0%cpW7AC-pvsX7f|-rPD8`7K}*=QmZj5A&+=C|N)6;QXn|zj?#^IuYUUe~n8#@7wcMGH=G=eWKa_8SDv|!@TX^6Z!f6AguSA#X`OXcvTY5#VTnu^WFl_Fkc^;g?g8dM7<AhV&2I+hx3@7tS|G<!n%mh3mYGEdmD8H|GonJb~<M+J{D;PzOTf;z2qK`yBYPESGl&Le{<aB{IAZ}W#00``zf<A@~~QFGH(=;@q0M~=Ow#!8MOB!p0n&sMFL=d9`LI?*!QR#$?dgQ-F?mNDlOyd?hiaKsJ2&_H~y*$dy4(SdCd0iX5L(o1%CTD9nT||9q8E$-X6M`^QT(*8}s&Pd4Cj{mFE|AZ6@T0;Qf*L=?voBGY$M{d9P%JzQX#p6Z6*MJa{kj;U~nWZ&TRQ0KDqbgxASxMUB_!mj<vidkoJ<_WS#<*w1ge!#`nFVQ1c#FS*~BU4@?Q4>{l3NBT1FF8CetbCct}M$ZP|f7pw4!ub&#&vvqzFWAm;cup}dV7%KS$G$-P$n#5rjQ1<y&)NR=@_f{}F6Sjxqj(bQIsO89+rK9KQ!Nei_8sslZpmksFF)`x^D_&>|KV{wpQ;<Z!6ynIKbiNbl;J$$djEYd`+M6l9;=LIUKIkbemTJTP<^iVkmX0ugnYM*cuo)OeUIC<VGHaJItu&qw*Qy;6~!UneQRF6UMx5BRzPozBVQNwUYK`>^?%<7aZ-8tH+&r9-e&o}c-~h92lI1;>UaMJ^W9J4z4_pwyslHr4l-{fzJ)!`6kaE&iu;+Tc^~@MX3LEB?sPd$X32W^!0~s`f94v?e>PzM=~2iJ2O2T2URFduUYL*Z)ph$7uJ^d)+ta^dKPRltMdp`RhCMgm`oT|261m=LvcH`_k@LB#U|wK;#z^@8yPU}9=~|y-dt&gs=DY|*e*19#Ec0G@jyux~`fD!deN(rk<e8~aykDXA=fd;)^Bic`B<!oG+(Ac}ul5(7?-I7apGOi8^SJ0C`C)hv=X3R><RR9d1M+HmM$8L$yX|5<CBhJIlZL==x9&LHzwhfX?=2XK_nS_SCEVUQH{?5w+`KQOynpihAE$=A_s=PLFJ>Y0Mi%5@bHV`3Yv#3|xnE*s{3g7{I!Xog=Xw5WYqa-DQf}xEjN$QpHxulPSqI+rS-|pF@V$gJCOyVczt4;KId3DrPf(5Vy@9fxFXnYw@=lni4&wU+b)wR0)^j@m`Rd0A#CfT2*0BF#Pr;spH!^~s%KJ=CrK5O{Ie7{Ezdm#W*ZWlRTiW+&`S>JiGuIn`75)43b-Y(S;m7+EX1Aq?pBgoh-;5A`&*PlAg?uvqcf^l9gL%8;Xy{M6m7I_M%lWy`UQ{3Jy-GQGy{Eo2_OqV1;MJlQh@XHSysxRw$vB$UkLL^ZW&^)RGW@Edy@N*}9-74Qy3eXE@qhXp`pf-`*Xho1#Ix-e3%}LR#`^*GPZH;U)qo$aUbxJ9hGO2dr#H^Re2Vf{SWhj9|0`{vf3w59*=8H`oV<(piSp&=Fn2xnA=R1rXxH>g*V+GLB>vk)Bi}wOc9Zqr?*PA@&5il`z#-<XIYr^0^FtBmPi}+n9f*11o%msP#arC2J8`IY&2Z%B>QOuoyCL$OOoDt@GolmkhuPu2k|%2;Ki?REeX_L05w|mHlw>|+6!T67@aC)_?6+7mnD<_V9y8BL_}Q<;eb)c&G4MZKLi|_m$-L79yj?kx*VQWPTIS90N9f;XU65Cw`0@UeHRJ)>HKzsQIr(tr)uz(0XJH8TL&}W-?|`>gRKz;)L1$i1Sv!ZK-fl0DXJVtU&iWO+lOq!P)nwk^a^e@GUzSb6`;lpdczvW_XtAE0;?I{wnYT&_Us~qn%_W%k))<3!1y4qvKR@g#>;GmS;;QyR&bRj4^t^v&RK#<i9TfsQZ+y$V6(-+tC7s1OWI_ez-O}KVuw?M_{7cNM==13JO}`*MS5|n={QdmUzjZF&D>=28H!_`rosGuvc()(zW8S=neMmL$D6hNh{r!2r(CLl$%c|6T<e$h*%)5ud8+*?{|D*TJn~}24+|d+z!q)Km$a>Nnb{-src+S%a>$OB#4>w<n_1GUBdERgr%XnNE2)^NP=B;?-VJAg)<e3^1Am3;<;_yaa_@T=*$o~a-^`<4p>9lH?-!@N&pL=bBAHwD{Z?~24+cuK(n_cTL&$rGbyzetteEI$@E6@K%>o55*4DUV11Y=!rdmG|8dMM_LwMUpY7rj8ehh)BcdK-L}m*4|O<GEvS3SN&GD|*R(uZ!=6y0pW7MhxEXt0jAR|KF}XlzB4%?-#5S)i6#+?&funy9@J_vrFQ3-ah7yh2ZUO^1WHsGWecl+<MqE<vQ$7(UN&Ja0C2Y!h<+`Hi`3`wJR6<!5Fs`{?D43^Qh(T5C7y{4L|oZn76k}ybX;(evWCxyqg+vWuH#My0LRK-ou1ST&;hN{JC`r^UhCr-()sSfpOj8JoDy@g^0I_!}0u*`XlsrlzHU9FzAVE!Sj!kyff^nSQqtXYKeJi*ly&F=ugPcoh|0g<>2k)QM}Kr5{EKx6_vRC_8s!=)5*{iCGWc@&P3im6wAD~oxC5vFaz&x8?OXkK=S;|jELK@$$j7_iO=_aq5n({=G}hDFiy{&L|)yTpLy>+@P=Ir<1{>sdGl5b;<;r2e@|i`bD6gzvEFt+UqSy?x()g7WgUJm0{J|9RbEH9Q?af#zn`3+ub*y(_W<*-ezsG;#QZXH6!S)gW$<&0_ni0aPm`g?{|@ZgF%9eCS3g7k!fnKV@0G}_htm17{{6CVTov!{?6UcpH&Z3To<HZnZ)-xCcVF&Cza&jWzAZMx7ycUwJ-2Qn&a140{%fPq@1}wud|xte`N{XU@|~*6^A7TlDxqE7iecY-CwRLR<jp<u-EWB@SU0Vc@0oos<2$R+Va$6M$ortbZX(~ln1wu)t}^7KYh!%XdceH1`2@a0=sX;GBfE$5rCSNS(-rZr3Y2Hweu{Bq8xhbya}e{^l0V`9Ig)2Cu4CSN82Q<*XJ8-0-VZ%l#-Y8V+GAV?Cqcf@BG|b{_6^*0c#c1T{NUus2!GDX#Jo97zLVd57thOC^D%F2SPZ|#+ZcBv>M`$Z%!ztGO-FxiT!49|55|R^+>1QiV<OMD)&zV<tzOIbw=bq)9uAZ5uHVV?LXig8-%51>apE@~>*2^YSQlglZ?>O}eT<8l@cyUO4A@zFmgMI;%)8^|d+%xzC#jlXzi=yfJG<Bu3*Ov56XR~Vi+JAC9pigs1<3DwfcCzf4E{cNXZ~l5m(YB8pH}J?{PXPr*uOdq?*}f)K6A=8h=;hA$bUnHUo;i*Q>Zud#zTpd7Tb88Y&Y7(yzP<v`H!rheUreKmb~{UJNQDyIIlaU{jl#HbRO%phC$5R+nU1uNqFy|LdrnC66Dovj9)u46!KY`K|Ys!?>eq7^X9M8?+Lf?y;J9*m``rpgZ;62v7c6XD)g)rzH<cPaNrim=Z!+W^E<%L=k_sg6_oG%=i~c-Rqr3>y@A3{mERGR%7pJ|F7C$o4R44%pT0Esmp>x@1MA>Bw9Ji}clURa=hIlMx8s^H?_37&F1pR@9J}W>e4jgQ1?>NO1M+aU%glQ>{{%h%;=4h$;$O&L1#cT(UO(H<tMPil4NnjGh260)I=l|n5kG*pFIC4r%<3NazMv?6AK@g(??fi{X5OeJ{7Ui9m08e#EE)Rcepa^A&OMKLvu7Rnp<$!^%ui4}UadwFZ^!RpA7gbH@F^wUW^_khJzbl5?^x__I|mUz&bY?RyRX2T!{s}rajo!PsKQ+IZ{ceAPUcb@<cTU0w{b<GKVJ{%e|!x5i?{3_GY0RM++4?D=hF8aCuZ$I;HM)0n|<ZG?ms3$&zJc+?{m)c=Ckdvrzd`&qW(pGFrU7GJ-so0?NI}<{x>|FcdcgC(B3^aksto{LH=$9-VFN%^PQa%c{=k*__@W8_-?!n_7Ch1n0K7bvfgWQ3-8$mg13*#`tZ_I=szy~Qqn<tKlkDJ(-<rBLdYTTsz39t_Z;%%s$qB^ZQ?zEwd$PgPe#F>^lPA}llVXI7~1>o@6c0K<`-usx64U9jP=3{@#n}>cyE{|FRyo;ALMsK)g(Umw8)J1$U1Wb_T}urjm%rYVo%yjcu$&jANW}Cb|KVjw@hN*%mqI<oo(c+>!tDD?2-KLX}|Pit3k{=3Gk0uQ|g`NW!@Vt_PD=FoNQ#?Xd!<11bOGyN9N5j>(Sor$Kki^ft+96r2eocb~^MtF2=mqmEUdk#qYMv){Vdq#_znGOEON!H(}nm2;S@^zrz~Qjd?30zJIV+R>k+m+q<LQ(Ye5<3`U;G*B|pk3A|TT@tqKdDTkrnGV&fjk1wwS&91|lH%rO9zo#eO8}1kd{WH*Brz!RyoO?F(*932NuL(UR<}>e%#qZjj5%^u3S_0l04c;tV0`Hwy#$#R@_XGSKb_MU<_AP>*ci`=?Sk9Bqp2M)`cpK<Z#qph3pQG^GkNA$lj1OaZ^S%o`)#UegpT*D5u0wuKTiFK?Ki7N@d%pDV$*$<fZQ$*)!k<o!{2!orK6jc+oGge$9w_L+_gPJa@ADkvrHVh^OQ%4;I2|P(rU<`Yes4G*zvDAEL^1Em_w)8)S+9N=iFHIr@a8~S&qOSN9{F9Q*<bh*;GHl05z^D>zkUTe_(|Htux!)=gjC93b?xxgPe3)v-6O~U_fJ53l>7hs323=W75=wB0c}Dyv?q)w1QJRRiWABaN)bvEs>*qJ;fjk~UP3NHZbEiB>hr>c0)+g60wSxMoSC3qrG2-I5H07L&p=44^iOBC<7jC?NKMecQ_V=oO2|UUB-hdrJmU7`gp`C71Rvp(N!eGf`w@x~iV(gfG?x0O6MiI27Msct$`UFNiivDV;e(`{hY&z8L}wvFLGFHV1w|$YAtzxGp@#T!CE+_lEke8;^|e`qg@o^=T$j*{Fp#i<P?4}&&U=fjJ`WLnTJLN^3u#jfVKCt*LM1{6!f0vdFN6_<u7p8^k%Vp{J6O1G!v7+2BjkQv$4s&90pYUlCvx~U-A8nMtx(>o5LYQYxL%$xmChFs5(Jk;hnByo`_+SUeUC0z7kPc(MA4_?^#^I6zSf4&P-Hq1#uEAwbZo~Gq6nSjsIN68{7RTch#>SK^dPh*Od{CA>1+K7KNIE?>I-yv6=5-<CZRTAIU!Wey~0%?{6?5Zs6!Ya=fR@05ut%xpCjerBG*&u*5};`)d)+)zUE^43_?pe>T8jNDTG#pA%vlXUIJYnCfBCO_0G~(eP265J;GdqMW{^ZOXxxv^%Xxx&cg|Dge7wCIKl+s+e$f1u4`X+puU_)7*E(lI7+x6+&aP%!Md-my(iozJR|tgKu+(2^Y>q!XC-{1bN$XM$5(OI)Pp*6NV&YoT$Z>QK<ASPZ3&MF$w^NpACx~6E_)yoOISeogRuXr@^O(VO!t%~gc9-+iisXw*4HY@H7!%tM}LPzc~aL$C_`xcRk^;{bB$z960Q<n5Izx#5dVmdTL^au?+GsnhVWX4F5eNE!E&FLD@6P~I-VDOdi?8g{JTK&`uY!KUn@cjLNh`eLPIInCVVgFZA7jvp}xrLa$7=UIoH=a$h|Fn^!Mes&l3Kq*r)9|DmILeHffvpDdeDCQhp@YcFFZma^Du=28o>JzT~#^(!NM)e?vlh!V^08q2s>_WnU`iBa|R~_f@$hfu?1(fn-i8<UCzIqj0ZF*Zw9PA}l8S{#9AmXL}%XPh#sC-E&BEmG$5}od@M+Vw=7`Q|jtU=RXi?6M7PcO1Z1VWqskROWURqXn~<jLT}OerEH7-u_E`K*s1NGA$lUE+*Rs|75g7ctgjG$hLryhnH8c(%UmbyA?%RyYr;7x|4Z=r;P`;x;{%`V5gC1)ONf_tOp~%6L+J=Pe4x)G<$L1qbD~?<dC-G#mt5|-CpPGE9v|H6BjwVfN0$v5o4<>%=8E5jNqL#rGgitw#5P_2P3nD1eYTmfU!j~!w_C~?sa#C@s<xE1tiC=_?$PIZF4ujYOJwvh6XBM^QRfYvKOPePl6ZP3`n8TSB2!dir@oXkiLRnzgO(4F*lQ?dtw+aXfYi59Z2N<7g>YKxoFy?jOV0PpIMU-{yFi!qx+aYW<4bcTq^vnTj#i4y0l8<9LcHp+smGum8>eKfnG(;M8$#$us6i-1eO7`{nec(mUlL9eb`ma0Szp(3seN!=%VnhUERp+5bn5dM?H{^U%LlozvXnKa^KU(=w;-LDCj=96`Cz`tB;{gqEl{p&9eOU)bJ|0~D?&=*vI%rKzd+kr!RJ46{#5>njspp`2;DrGFWO33Ukj7#L&QEk=jr*bFQF4*Bq3VLEeJiN4gI9tTCQvP6NKkFmI+%4e+u`F58ABT^jyx<_~5#hn<+MEd!`fCdN8*xkn(=fqh-%a-`o}cvXq~T%z3F__fsyZSJ$UyK7Unrp!B_#)#tiT*NV;4#XpmzyjA*omiTF)*nEtTM7T*<MMx0trtrFNMhd@5V&$~R%oe|`65mA&_fqcFGG_?8MBf?dQ{A_zrLT3LC&@jUi;+4Kq;L93OwJZP>jb+*pDFWlLy0vVcc$RWx<kirO_3=t@mWdYGFYx@xoR@MS0U6Ogh+grBoq~t{OWog!gq3BUDg45J*L-X1q5Y8PX&?Dve|tQ*F~jVMr7Yhyk{5vT3=n!S)33g#}KJEOvXeZ858>4kn>tH7QP{5BOF&K>-Y~Aw2(2O*FxtMWb_)yU+&Xu#odHAa!u>e<r;FYmibon2TNIxrKTd6O}J>$qxCHlUHZHxU29J0Pnf6e@L*lsU&@+0q3{g#TA-h;0tH#+e*JtiUgSE`dAJ8_?2e*G>#IhnOX%f6y`u=7h5KI0bwqBE+^2Qu_4q}?DG%1*KNI3arnBhz!p$d)kh12s2u^*aW48zEcZaZ#a8<6okn&Y2e-a&9{~GbdZYi&k@+qlnpXk&6(9eq%J$QBumvTiZYk%l<zh3|A=T7~ssGm3WbLVZsF+wWwZB6k@D)Eu_i+*lgM>s6UV{)JFqnskUR<0+>HN6RuB-g(eT?IVgtI0JboPIWq6@5{nU)Qrn;aOJeoj`Kq2o@ocaD=dda7)LWaA|35q#`_}@<&1zpZ{=gM0P1*qv$#!WzG2!vTJ`T)X{`cLC{35>1Vl13Nmfzd<r3gkeT$SAUvURRXUc^b0(pjlr^Viz9j?@D#~?TzM_31_j(Dxh)!Mphp^cLnUhl9L*iL<`{dY&P}&1~s!CZuyKA{W35DtW10A0e9?L!YT3$N7qT@R$YhGX9A@^z>1wFW~@4rvT?13Kr9G*znB>Y7wH>Y;|NN7Z8Kxj>9DhStkORl$;>-7ljd~jbADQm8y$Z5X4+}l+6_Hus|*)p2Yj&PUiPDaP4bj(l3lwXxA6M_go5=u!~?_pdZtXH`Atdy_Owfls_g7t(&g7s3L?q@BdWixo7=O02jDpwJ%os>2AkJP2>oGSK&62^#4`n(TexbW?y9?f+j3?{S`=yG>~Zhr&m^9Yf>LAXQMMmVecPB>p5@VcCg%8x`&%j}i5?Unl$3Z{xpMI?rE3bd|wa=+GdKz#O2^yQ}O`Fv1MPPsR?jD>ts4v_fIAb2M_mJ?QsZx)I@%cYLhQvPD=9Kmq$)vtu@(pSHVf4a+f8Z7?NW9W(W-Aa-FRb(~`cT)J35<@zc{#L+Zh5fCx#2pkaNaE@Xw_N1bOI&IBQ0eFV5+BJVW~)e_>vIp`GjV$fHwbxz)BPSoDDDAQNy-C6?g*h#J&%unvj1$t|M$OQ{Li0$zEl78j~V~(JO6w8{_8tagsA^)<~ORBT<<kg-tys%y2*MsS^Xb5dvIz'

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
