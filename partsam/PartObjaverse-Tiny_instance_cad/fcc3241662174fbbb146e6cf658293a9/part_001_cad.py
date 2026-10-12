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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_001.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_001.stl', 'source_sha256': 'e2b3ec387c822dbb0bab9fc5c1c4a1842e1d490cad90c53af9019a79425d3c6f', 'input_faces': 1628, 'input_vertices': 865, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3556981682777405, 0.010205822065472603, 0.4345014691352844], [0.361838161945343, 0.06321262568235397, 0.4505802094936371]]}
GEOMETRY_BASE85 = 'c$}r33AjyV`1aS{$2^6IjE58=GDgBSWXPO(J_?1*lp^g0GH0Gb$9x>~P@1qsisq6b;z%hZga#SD{p|PmuK!ujUjOU*uJ6;eulK%x&vV{=uVJsf_S!?On<Zq(=a_#boRk~e_RMeNIC9J3<a3_wGi*e^C;JSqFlfm00Vj8i%Rf8LYT3R;>&^k^S!Z<V-hGBYIjr=<iKQRuTcdRO#L|5S4;wM8*Pxz*hxP6wyiu=bhWCl`;ZOG((kJT6)Tmyqd}5Wd<r7~_{D1tHEgB*8(VjzfWjy)BY8jK8T|XA{tM_?$TCOX;JTxJ2T*h$HCo!Jf;qz7L=ds+WeA_dB<k15$9!dOmRr>igxAVJv@s-uS{cyMc^cS9-k+PSL`SGNI8Djm;{;y*^-1O|K^!=La{=~XJt@i7;-1diSeQV|^-`Kl;;ECN{OY!ih4jMkWlV|;C?yi4$_~x(_zkbWz^^^F$@AlQ)oxk~E!-qMZe$91%(p{hV_FL}e$#}$fKMapLYIxq4J=;ZdcRgGF>|-f@JPEGnahBFtAM@&do!RYUJYw@J?k+Dpym8`szxgeX%Q<I{@BEhQ`JJ6V_~*>Od!ru@*FLh*Z+^@5{E<9aH~HnaT;~rLzh{&0{BS*g+SUr2(&vm+`oZ*P%Hcgez@1lidAKw2gy~<f#`Cz)+}^L{i5E+x`1M=v_TM;Z)_=u&%>H@u%VT~#+~f}5{-l<N41YV#%>U2(p2xf8$#-5{<(Xe`cYek7{E^2x`rdCET+eU0o<BT2x99j1N&Ct4x4pE|k4LH=^Yl9lPn(=$GJCg+;_iBe+x6q-RNT#}xVyaYaNo(R{pPV;&ttisCo#v~6u<nI>-<Ucs;9>I%zwT2yQ|5D^gPn`XS3dt9*XhAPp|m$(DGXz9v(BmJ5P>Z%=)}~bd4Xkc_I&A^X1ODn;sr|cvh<4JmDh0dyX@frxoq8A^qb$j^}rdd+zt0jh^F@v+ozram>!6xx1d>;iI|Cdf5KQF+ZNTEy2@okB4#d!|nW`m(G~&JHM9a`9*Vk+_OA<>5UY>e#>=#War5>>9>pKcDuOuJ7j9AU%%zLKm2*Q*m_8Ac)^$3?W=j($&BXsT;o^Ie&Rk~D<1B4+r!hY9E@$R#Bb00^3Z}zp7}#H5@Yw9^zzkXemw0g`{!lDozXXA^Ejt3`SNhRpxN$ge>3+xWTy9cqPTk;P~1HZz>_a*UG2vsa6P}}dj7<==hviPpPJkC>E7?Lms9=vE!X`?%T{^LH#B$8SK*<@&zSA9>g+LJJ~pd&Jv15`+b-eue;)JW_VMn{v+@<s{$_dj!D}1+a$4@@?0uH=gu&kD5yjo(gXIUirug>5b-#0Fg6H^Yd3fxJRA1h6e{B7v-Mrw-ZT?8nbB4b#+w*wW+&vD%<Br>k$MtVJ;@=O~{qA{b!Snt+dls{P4#SU+_nx=F6W29N@#9Iq{^eO-&21i+>*q~)=*1zae)Cwa=SeJA+Z<0O|L)7}@h3F>yy45&dLECO+sBvX;oTpk`t@6``y=Crd7jracb|7GfBp^AU*)%Be%w8tYkprw|9LKD^KfTSA@jUopGOq8$6L#jg7<l!FYNkRm2Z>Za#`-4=QsV`<k@_~^Z2sd+1fwVkB6!?^gfR$?mmy$d3tp9z7DdS=Y`Os%f8(C%JIyT^l+m0^+@o7>F4#GeY|V#KHlNUXD)lTqvqj<vU&QQV`IGMbsrd>_Sr|?<A&ny;~E~BzarJI-*Vj_9+$zaAI_sRx93qVFZ-3rKjh*uKOWc5`Ko(<sJVT<82N|UzDZwtkHhffFPEhHar-*meg4wiK7YaO{_LKA!oy#W^qiN5DqJ-CbCc1Y^9RlC^SkEuJi+o1*EckGuY0KZE!Xph547{FANPJ2=3VQ{Zyj3~8+m=9xqW@%<{VYRbAF|{J->4EaNcOo-!ylRC-#0h4!g%O#pCkB?Rly5+eOdwj=Mj=le2Y5Nx!_B+vT;~nK?Ek{r<1H`#J(1skhVgbNsP94Q`KDmWRe?HP0^v{ki)*`<r+B>UrGluI@L|Bgy+btGN68XzzE^v^9RqYkA!A26n9RTc4K4t<SlidLO@bd+|C&^Kga*sebcYuIG=m|0LBfzvXfHGiF}vw>~Y8TW@f^-Yk#X?k_c8>$iO^*V{L=cb;z^%k})B5r^0MZZEiA-lYF-uk~A>md9<cE_v4ZZI?*DuYGywgInv;Ki)OBk9T)HG?-(K!@JM;bG2NSyXXIkC#GiiK3*oa+~Bvomh0sW{npcaoLPFw%wPCb?|Go&?s=W%dC#T#_QT`)@4FIPKkji)@why2d)%|!Uf*z!&x*UpXLw|JKF{;7=I;3?Jh9^I8~yq%chBp(TsHIMO7<LoG`Ei<m-9G{>xb+9P?=ty^9{}I{%^TGzq028ah&r3%iZ%^_Cw9x`S1MGtOt92*q*P#!!4?K-)B+Wp66H|>i3l4><^mj`7L+SGJ58*@8h`FPZW38Cp`K6IVtJ)AI<Il<Ib~wONwWGYHru3&3S0Qng5nrF1Y)Cf#vpjkn`j?uGbITzTVM1jn_MtrwwSZ#xIZMI*)zc)XVE~wY=fipIhU%J}uYlGr8fyHGbR6a=pErqbt3yo9uqb>r=gcEZ6%<Xy9hwdF*v#z291{_gj0NO3xGbI?k?#JY!P*=C@qWpY}v*s^4;19=BW%Z1TTfUXRB;F5v%Lzh3|L`cK^Uh3oAbT750mZ~t+*+JEeMyWT%7*ZZe?UZEZ@F4yY~t{*S%d5eC$RGi|Q$8wz~xzqBse#`4}{dj2>S?jw#;c>^GET`A{Zb!I1-*ETC#ebOPRqMg>xcwIHUiY^1zgsf){2S5xt>tRJbqZ8n=Qn@avs-<6`1`&7^INXx=Y0@+{Xuj0`orhk@1e?`>mHih>mHVe2GsFhuTb1xuW-g+G57m(eskT)o<A$@o(IB1N0L4BYi_q!9B03co9B`@k9~j2J+D^Wz3x}{s@XqVWm}(qyEy+|^_+LP*AEqU&(GoR^>BMV0UnxizxR5=mTP977e{)p55S$VBfZxd6nC!!z?1&$>)9VPci(S<yX%eDDRG?FDVE#y=Dwe$xSrp>uc!Mhcl!tYWtOYgcb@l=Essn*7vt`Ewc_siDm-a$DewDqitGCgwePXYZ+^@5{C54v<?M2o=RD1w=e^SAdN}WoXl@_ZmfPzRdVc#ph20M|clT$zyj2FK_$`;^dbuK>jPlKIKX>H5&#1WjKBHYft(Ka3IL>Hpk2CIixO=tteNx5s_DVXv&h*>s;fmYilFO67@?5vEJPfz5Bi!|QE6sPkS+3Vxa_N73x0gNtw6AmHIIk}>kJ~@t_I0kiy_VKq<CouZy}b7PR&U=Vr<M18XT{^TZ`r<{^K;Gh`cJ$vV2$7YV7cBOl6DOBzV24seI0Gr57()5e#>=!{l1&#y5F9M>-DD3!`=Jkyjnj_-SchrICUoeVqU+f<Ade;_@Li6ar3w9oa&p0_r>ClKlXhzJwNXY==_%J{QCUa?N_hsHUHoG_4*H;`_^|J%XPoK-lF$6%k}=|{CF|dcYlWK{n?(k$30)b_5PXEyWm>C$EoFUk2|<tF3aN{*B_PjUgx)*^Lc&zak)DFSgwyhmd71``i%EoF3WY!NXa#x*D0FE9XGabTkE$SEsuL1;reIXegcnMpLKrpU2maE*Vp<!e&KrmPitNwb{-g3k1xyh<11-x-F1HVo0NT*?>v^rohRIG>bb5J$L;H^Qh%HEyl%bsbqCx%|F^Hd6t}OxB0m~#-&eKg)tcM&V|i#xAMg8pio2ihg@@06;W>Y{Jd#*_qu)H1yPw~f_m7!}_bc7k5sJI#`HH*mE5Rdo=QiiJ_WHKs?)zD-|26yPhQglf*qXbKi>%kZ&kJ^cfX5wI;r2Sbdp%Zj`~K-3!}aw^%k}k1&GkI``lRN1etmt?onKv_)ZBfa1+K48YVLl%%g&>&PsVZk{;$ocu1{+2zVBeUx;`1l_4-lQCpEX%TP)YtCpFi3^!3R&u9jC{pVVBhPknt-bG^Ov^?%KEzdnz0_gi&6Q**sv>Fbu7$2~68bxSvox^C&NA9dYQb3MPlZmGG>udiFW^Q-HYn#Zkwb>5}9?$_5dHP`!tzMdJ!)&8chXKJqZXMH_0j_dWQu4if<_xMuRGd0(F^!3a*t{-3OdZy-a$18O`Q}ejT3)d(0deGN1HIF+EtLvF@T<y>LdZy*}{6uqmeaw9yR&n=zSiAqI@40C1KEK<XoF~NPhsX7+@40C1zOEnhpUJ7;|5e;Q&$nE^|Esv}56}G7dp=g}hIw45&lhQKuls3kuOGTxeICYg{dpM8?RK$Te;!72_x(_KM1Af>bN6$4aQ%50&Fyta%k}4BG>@BKeZEEWxcut#Et<!zANBbbcm1o+x41dg=UX(_^Xt#IXdaheeZEC=y?*rPRW#S@Uw>Xj^SJe|KChy=&aXeOqIul<SD#mj{Gs*-#r5Z-G<QD_`G<GC#r3Pt1zD~?cjxw3-{Sqg3_P^xtoQpbDK`z*pL>MIeeMyS^yw+@ak$qlvmMpvMKyPyU*P)lqMFC`ce`Ld$D;e;?)yHLw{2&R+xBz*io4Ih@X$+*H~RHk?q08$>Ku-(fBpGw#ogmDJnniLT%QM89`|`~#r6F9{XVy!*P9VN58VA8O{0L}>ht!N>(AR;u0L<Dx%<Ah<?8eHmg~>kYp&-B&3JyD-#kve_dNTF=I;Bpc6sgdyZxT2;_myKx8eHx6pFi#)7#$V)%|hbr?6aqpF(lnZ`VVz>bKne9uwSNAJF}lyZ!G5&3>i6|Dw5jUBz<sy(i7>d4=Zoyu#(`do-Hs`_<p0v0Q(T#^v=(d#}$7OEBv}e@{wr_j^z9xbI0RuKV@-@0z=h$DcEJ_7nGWEQ;%Xce|^8%XPo~oO49=yPu1;pSy!QDLpp&^;_<q-!92$=F#70RNOtT!jts(7UBAPj^U1(%yCtHpHXx7xB=JSXVhHx+v{D)dVaWjJjtEeY<Km2Sj+WsKy&wg;rjcqE@wOHc`VoSI8_gM&s+ABbL-TFvHa^FIG&zI&RvV~<h=Pk+!?ZVNi1*Yd>$Tt;lZV`dCuhZ@X)zI%VK}Gb%%#1<+~c=;XCg4@Wk5Lm&g8YL>}+_<C0gz<}a|)!_)3w7vsrerg-mn!}b_=$_)4L<obJJJTj$=cb-FE#(4O0J#U_+2V*?cp{zGgwKOwNAh&n@@O^N-ypH;wxI4f4zPaY^aZ>Tf>C*o5)Trmn!{2rGpJ&i8|9SRI_MfN63h#PQ-*eYo=a0;-<h|Z*x7Q>6z2~K`W-;sS&hg9AZ+FWh=a0vDB(=VW$9>;larbpPJnsATitGNk?+L>7d5Gn4*9{bRkCTsNHOqUw*}T~OkGspm6EDwRk$%6jT>l<|<@)y!!q*H>uC;hs`p1jq&Yq9W<Frv%v%NNCGs}C=)3ZGLEj+v<XYBEw_)0ksk4)~q%(uVyHp5R1_i+8Y6PmmGkK%fM{ks#E>))Nw-2GhB)7eeVUR})btyXyt*T0+L_N(8iaJhP4DO@6l*-zB(cxdikZ&BR+-uLXBh95Zdnjeq*9TLUe{Tc4)-y4DJ-zN#R$Ytg^x%-XSdi=Y<@$@`#-(ItyJhRiolg8X@o<|NfG|QFg4znHWW}KfszvYo`6IXcnE_lY>b7OgUp0Yf7=gq~j{-S37$f(@reor?^_UsSv<O7#t-09uG%u_j!Sr6@6O^fv%t?1#&X_IE9e>_^AR<BEP`sIzBH#}Uv{`lD6-Mh=fllu>i^(TI_(%Y|pX9gbkJ2NZun(dxz?o`iqheu}Am>uJjR(W{hj4Jcf=d?WBeOfF}TD7Sju7B4^bNBVK<?8o~G<VP63gk2Qd-=+gSpNr&Jv_P4=2)KOg(JND@ONfC-|p(+algy-HS_l!|9Wh>Zmd4;;l=k%OTS$#PusM4L5#oK&BL8d>lXX*xZj&n+&xc*$Nk=v;_mC0iTTZToHl=QY+T&a!;{~7ZN6vwHn__y*ZxxzV)GZ8?%|PgwI{`V%~2knwzA&b^p8ik|5Ud{p2y1#_=A^XkN4yTt35pKce)gJm+S2UW__yP4bxor>)#F2+&x|mE@+mk<JFn5k>i8qk;~g-kBh{MQ$0MX{;BzXJo)*ivHc;f?MN?Q+I4Yy9x8LUx!)x(E%NMFrwmWt{LUQD{sRxc_THlO+tKpStZa+Z=W+Y>@3X=6@3T4W3Y&iYdvS`pk6(D)@5L$Ze%?N35wl!v9-8A>4>gN%o;+=OtUqO%hbMj2eP;Uo&2s%ac$&M{TMm~n+fn~6pW^QR15eh!zi0c^@AWw|N}8NoKA7RzULTe+^XT6Xgvb4U;K+OZ9~X+d`)$Sh%=~5Vjooiz&S%Z~=~^cK_}1F<tB#{nULEmubH|ZeRwtj+w^zEKbQCE6?CAfKj{U0sU;U(GrRtSy{Qv!?W45=0(Wivy?TzS7^e6ZQuvgG;<EO&Lpcmlh!(K*D#czX6L(j+WgRMYs!+#0eh~9_)0{;p6PyBnZx6xnVm%|pI-@{9;dGLAEL@%Q@A3YEME^Hfm8UAzFKJ>fzKVe^@KgWL>-PV}`j+5dTJs@EGX2-BOj?tgux5HMWH{&x#|E5U5a2dDL^J2i%h6Ic*g8v=%68c5_udt!$-|>=Z0DJ&7(Yf)GPxQ0+2$>~cgqrw6u<hswz8{$-pXfvMoFlX3J4a3YKd|4?=kQlyzoP%aKMNaxzKWMzePA;Ff<8!Q$tSuGy+N4d3(_ZkAeklKK>Ec0MP|wO7d7z>f`<Kr{)?U)u&ZdP{X?#+Wc!7h_$Tpw(7)jwnB;S)iN6CDL_2uNHG<qDsENKp=D*M*@GZ$K`9xo#M{?B*8eWf@=-;UQLPn|GAXjggj6b8lb4<-a_og=hy950l%l8ay1Ui7f2D^fO24A1dl27zCdj5k+zW?YG|1+6?BjbPgTzJVRdL(`qnI)g-T=abJ7#2Y9!aq%B$@et10GZFi&r%cpH#N!kH??cz`V;;qeWFKF`<aY?;y-bW&xP(!eG{1_pXg8U?~qyYy+dsm`3sY~FnyvW*BEk-p-1$2GXISpgFgfN6MY`vA2t$w1~0i*l3T_E>a)o#`DW82eiiH;^lZH3%0O-zSJ5+=%#v>~J>tj0&Z7t82f@yu$Kn%U{n3N)FOgaDiGCM9kj#>AAT{w*V5`sr@w;J?Z#T77<nK%FzSKkyBlB2vUwl#6AoMW2<QhbF(M9Qbn#__<^kRHB*g*8t_@S^V=x+F}u-)jP_&j8me4@9~Q=H6_uQ)aFM;*h8qKnhBn9T2z@hH9{Uh;{48Q%)l4c!qx7&a8$3cm)n6+IY#7$*4+Qxl(=%#trNwLE0rL+(BFiGG>Pi^;eLFS**lWPBCfl3FWt8+<?5V026TTG$$NKl~4{!|1j6tYnsaqJN<0eb^p!R+jHoGQUj5_wkae6HLZe(5<PpM0dguf%QYT#;3y8qKDv*z<xld;<J!h@`*k|&tBO3=qxPXD`b9^jC=9@@tx31@ZDjp(f#qmU_;Q|@!Mdj=wbN00mF`<x6zYGX2~ZyFa8*8FFKLsTSDen$aoAN#`j0RhaUv%jt=9e!iJ#-;Xi_HLr=v^uBXT?<45!iC$r=mPLKFvFv(Ypn)vs~yo8L!=#gA0Fc~w^JBQjJbP9eoY$|#VUUJEK@l?ju^b8@h<P)6{{}P!c-%He<BL7hMP->zxQG1V!L-8L(pPREJM9<}dMxVvM8695>8vYtJ(SHO?tub0^;-3o`b}?Y|ANUIa!y2KV!@n9dY+=yo3-nxx-rk45Pi-N&u8{34wJYR$l)8+g(30zAmQTh<>CH!G$tU_{{C>wU$tOA=%OJV#gx^U`beNjt3sVy>xf+tYA+=Y@^*-4~QG1`vD;&dQ+=3qKn407hy#g<}x;lo-I2J9rI*?n&uIMg~sojb0fR|h^!e#7&mR!rJ%lIN%ay2Bo=;e6HRg&B?CZZ)*DRP&hCi*^VUD2iRrC}Y=_u=n_bwQWLORjt1_fYFXt`gKsP<xSF%gL5VP5k=ktzz_60sS_<eDpRBK8~8`p49F~kHdF{l|lE!_kfi}cgB~C-d=;hMoshs(c3!e>!_6@*8^mGo0|BhLF3n>pU1x%Fl-!JYU1w-7}gX0DqeCOfFGbHI)A{_dY})`E4f|?7%pRebd#W|twT%gH8M-Kb&O5Wl4}RKWju!-A2c<|H=dgK%Vd^(m#K*#1(STEsNF@bOYlqdi5?d;HOVLX61^XiS@MY<hku@IO&C8!U&Zf0%kk+P`QL=UNo@zm&G9TpV`}3$ZeAweMQWEhCXQkm8qqh3%nQlAkYnj3@?RnM6?(>z>qD}NzQQuJjQ-8{(ObKK(FgE<Ifnh?7~PVd*08o{sfj-r)n5k;|C*ZU3PDq=6f|0D;-3y0)<0-;1$=o}W%Sed@5v@y#`5$?u13^kjG+G{v*Z)qh~;YzYmNSs<@=P(lJ8S$;_oN3<P-fVJ$=b6`T9~5e-ErYx-ULL<^yEBhn|Lb$tQXz{t}rbpXi44JO*oyzQpqFC9~w)ORYKi?<2R2d+F&-X35u^9`Pk$_n>>@BV-dUV+nfd!zG{S5AlDHS@MalPfugmW9UCvzTIS&e7mWMFGXg_CwezMPmo#iJwZ);aaalT6ZoBE6E0(MdK$nbpXeR<i)5C3q8rfD1lAaRk>&e{%#!aTYK_T%FS%v>h@L0OEcu?KM|>izIQmKahh!5jV<J6|!X=;RUHHpnmVBZgrKcIJ3Hmb2C%HZ$_b1evkhv_mW&DKY>qBPA*M}bQC1Hu^KKNZ^-a*Ea^t8ZBKGFN}SI8{+M7N-)6|5Qh3d{EenI+#B)WknPX2~b|3woX+v*de<n)q_ClIW-K`^mhEjOFNQgO_}wzs3JeX2~bI4Ly&;TA}}D`Mx8w<ok}A_y@@>`9yz5Pd_qCzJAoiSA>;A_rrfn=KW->NKZ$+<P&`a|1X&(pXiSCw1+*8{+H!DL}tl%h?@8+WR`rQ579G#%#v>aHSyJ8710Cm-;zzZjMeCoT-~Y3coO{|nI)g-?krztSbOw;EZ+}gmV7@@6aNsIC7<XY=ov_6$v2Ri_*$@P=z;i?WIjU1TJ%V+B$$k+(30yWxn)dZ`MOf;jK0b89VfHoJ5H@L`D>C}#^dx1CbQ%lOpo|Fuv+NB_)}y)Nya+#Jb{;dqEF**lUeeKeuADJu&(IaEawR_OTH7-#6Lo2$tU^*JwwSX`G!&xAA;3E55=D%n{XLJ^z?#DKG8qnZ;@H@iS9*DH&_q!Etc;`GE2T6sfmA>%#u&^kMs;7v*a5>O?+Kg2t5RUnry;ltV>T%xa1R^hQC2($tSueJzZek&^K5<$#sm}$Eb;}L1xJ(`WVYMh|H325H<0&VRg}i@IR4FxQw;w=>(U2qL1RQlUeeK?nF-qSQqqlmhUi`CEsCc;;WKb@`*l7&og9}e9ur5UmaE({S5vnnbXKvot}1h$tU`I{6A#A&iQdWdfLJ|p#Nd{B-cT5AEYL_5}75R=z}a@e=<wH{?x=*hE+%R$A3@eqhzd1&z|V*a`bip{V9GkY&&`neirO4^k)1-*lhGH{7l#q^hEq7*gNQ%_>W-w(VOs}!Y-pf!Y{_}L9fS8fNe%E#*c-~LQlZI0Go&&i+>R|6a51Ib=W5Ki}*#bkI=8<*TX(VFT#(&FGdf;H-k+;kH8m%jYT)Z{~Ivu1$04r3cy}OOHKS^u-DNA@WWw?(2wDV!PcXP<5L61k3gs3Hw6r9hEByxu5AIsW!!{*hs=^s^fvs~fMEsD@8CDWB%kQ5_%#8;hNCy)CD(AWi(Z5O%`sl`iT(yJxw6BvQxjc~+BS4{d>z<3=z{nHu&wAi_-wF^=mPj(9mCe3v(Y1&B-<LsU(s)nS@MaVginS^zGQ0RCD(`W59t&AF||7A5Ah#3h7~}6jDO29EF1a*{4_F4KGARCCz1IZGET$y!M}li9RC6=8QllJ0QMpJ1^fos$LIz4`LGYr8}QG=-a^mE_l8YFKaYPLHVNGu-wxjg-2(p%>;-f?{0!Iv^fUN{unp)L`023u=!N(Ju;<a!@oizf(F5=;V2`8Q;-A8|L$}9|fjxtM3cm<813d=65w;M$2>&K*I(j31G;9F+O?+QiTl8prdsqu}U;HfmQ|QU~Ww0^mS@@l>Md)SteXxz_o%kKFH_`j>OJSqYJMc4MebGztlVR=AGx68(v(Vq-a|R4shQ3Bmp@3mK(K+!=1BUHG7sB5iFl-09DPD5r2pBHo-RP^-W}>CGlw32(_ARxUWd15(n2g_`KPR)~6a5u_ADJcJK5F9kz?!1>;Xj7mjoyR*43-1^F<x?g3ICE>4su;3`#03YKN~b&@`-*9-y&$(=jdngWrBw7L$|<RhwVX2O?>H~VIQNf(<8Z>2Mw38G<syv)V@SF$4jm+Sq{-7@k_}p`9yEPPl2^SFU5ypWzbXbqhXS7G&S)r!Ahe?<0q3@@=c~DJ{dL=JsH0N_8dAH|1o|k`ZN4i*c9}~__?q!dMkbsY&3c<eh%y<^d$Ti*ktq^{9afxdJFzD*aq}o`~m#O=*#%+u&w9=__ttl(cAHoYc_l~HPK6`%|Xw`zXRKXUV`5b+lzh&e;M`}dOyBnLiBZc^wuN6=&tzo(OXM+OKPHPM{kv>SEeSqIJNTV%J@pKN6^Lb?V`69@D|iWcaPpWQ13vk9l5%btt&P0b@3h1&G7fZTB7UXC08zZE^4APQ7ewlh0h7AgwBMQT=&B7rB;btb*R^&)`DCe$kvRS_&<Wi*G2!0-xW0MKJ*{>)j`8@p?Be@2Mx=FUX7PrtAd8hI2|pyb_Pvd##QJGK~t-P-ieo7b;vII0$y^B4;UunYiP+eAz<n<jz>=lnA&Re1pMTHVbjr*@Dl@utwK-6zaB7bCwd}Ya*YcZF5~NH$t2k>Fpfh@u7-|bGS)-)a!hRkx*`5`$FNE0Uii6=VUy9X<HtLOO+?SdORglxa2dy=C07H-)MZRUORjOOU(pTldC4sKMBjlg3hRZ=i<ewg;8m!Ju1Re!x(dEBY&^OqUUC(I7ojFP548s9BKSLC_0W0nk}DHT#sswF%0WE`HPHpBRYB*#KM1RdE{HDxtBigSpB+{NT>vk+GQu-bD?+9O>Iu|D2l1KE4n7+!2RewCTzA3mqLzbPg{c>&COSX00_ehc$(0qJm0AIE1*iw8WhYlgvN_bmXTb;28SuGa+0a?=lB*EB5H-=2s1-&R!ru+ckFJE5Tsh%6spThEX6l)#WhGaDY#FGD&xg-~&W)E`#o)!LiLOSi5V{yX1gnIuhL>Db;Z>=LE>0~cx+?xoSY~u_d~R3<^qqLg)f^^cee{#milLk1C&H?spTtY9dGLAEL{Fer6+I9C1gtoE0=^mSPV^J_`mo&SW_Zb!9577ArRaqLQ+pDfjF()q0*1@D5dB8L)aIdQ;b#U6n}B`;FS!;343}{xT5`P=Fm)Lhpe0u`vWtETFS#xS4U_R7bR=kM3(=SGl51Via2X@$89`Hf1HBF}xz+{^mvIJKa_tV9x{PbllIvp7)Mea_mQ0fEEyj!JdI`o$KGDtbWfBaFpzGl!*BuFl%UA}TIl<IspzpxvPB3gOIy1g>f?>PSx$&U{!!Dvr<0aQc*01OgUUGFJw~XD;t;t*l-3c$bs=}*M6P-vcGrB6i3M@A|5ihw~!CO%i-I-bl-3s3g)*Rg#-vi$XorITM?cwdIiLOnpD!M(sJS-7i8~+Hb3c5UAa<zlEqgI7n-Klq{){0!6$(BS-eEH};v@&|D958wj{*+_b&yLaM>8Sv#gqE846;Zu7VEAHcqO%1}EoabZsfq6tG^|U|=xq2buw3X)_?2W6E@KvYB-ee^WSoIcBeUcaeILtrKdb^ejpdt9X3007n)pm)mVBb;)6;>>lCJ|b@j+M?bO-zlGA|-yke+++l27zByyQATZW-^Prwq0G(I;5Gxn!1nbE(}={tV=naV|aW$SnEV(Ifsg%N9hpqh|)$gv)pvT>>uoL{GsVC$r=eU4ou_VP(+AS<cyHmVC3Ri4Txj@`;{J&*Nm4e2-HTf0N9T?<Rfi$UKGIQ>ck9i7$bkivN+!l23F=dP>9YMgPe1%^|bon?vnh@+Xj6#yRw~C9~vfOON<lWR`rl=o3GMY&RKip-bUQqNn3el3DVJE=5mSSZVZ0mQQlcBlkRNrOBL;+%nE%`P!3N^0lW&yaSVb4mI)9$vl;e4n5`YrO<EUe<HKw6J3s;2ViB<Ke2pE$SnDmP!pe(%#u&^5_&q4S@LzHCO$LFL3hNzN#^Nf%uG*3yyO$T41b!;l23F+dLD#5fIiLgEhn?&TTV@U4l+wV(aY)SOlHZ~nVR_Qu*~Sr_+?~%lZ@HvsfL$)qSxYoA+zKYU5%b9um{n<uzah?EcsSZ6MqMpC7<Y3^mHY&<m*aJd>&YKbXWW`vI&<l4?U9W5o$7SN1r9L<P-e}%l8nh3i>R|x1P+BZ#^~fcamB1iC#}ncQQ-9?$pE=g5^PX$8RU|S~3=*r!HRdiGB|+xz3YY#=7*>r1lW{Jj=J4%#v?2wTH-`pWHHTrl%*FC0|c^#20}TLifaPC!25?i_lXKF8M@%fWJUy$tSuVJ+)vp(HB_Gx5+H|-liu0ZZb<g(Qnh!i_DU*7d7$4U`5cq@b8gLxQxZ<3Be_w==brzlUeeK4$<>4tQPurmTwE0CEpfmwa9-Lxn<l!PZF6WUlKjyi^7VblkgvqO}LCj>8TBue4^jQpChy66J4908nB1a=U6_;wSn9lsEN);X2~ad1IyQg%#yDMHSvXEMbSO*?~_fqjD_i`4wrnQ*Wu5QS@MalPES=>4fGk7Z#9`E-)d^&bCX%}iC#@lH!@4UZq&r*g%w73!>=RryJXBuPi4I16TK4uGnvnDeq5QJO0cTvpIJW1wSwF$sEN)=X2~ad1<Tik%#yDQHSxJ%dC^_)E6Kc$jJfE!C;A#7U-Xuj@xP$a)e}suBx7E5)99@+^~Th!ei;8SbBV4Hy_JaGiZbRv*P`|SV^MTT?yDAKg>+i7RbVVZts(c{fUzX{QEF`%8=xCSZ;w%bjGEO=@lBaa^yA$BLyQlgds3^x_z=1c_tlf}@pQT*z9e&ruE_m2VQhoGlUhy2Cg=ju+k?~}q-J#^d?V%(-G%$F##jU0mRecHYUrBWS6jv|>2w=>8|D&SpL!w2vgpFp@-P-cUz6hm^}DE9T@zoEx$3iQQu``sbWQx%LBp;w-o@PCL~j|XXXNj!E`Tq<yrOT&aW}!#@1{rex75C26ejxn=<Q(8)DKd#`gi>A%qjX<^!5YwAE=2wPVIZfgXpyA?G*Ln=wpmOp?_j7(dDA|b3fbvezyICEK50-ryNYQ-2Zj*UFYwuzJ-_Ze*W%gR3G7Qj?i<R`#;L^9EJT(w$s#4Q?vSK{LjoKx>WQ&iY1uGpNvh>a{r}Ro>H(zWc!zV|MK@%pU2BsjK4b^)ra_-L-hR1{U2s|4#RGd?HB4t(1#h%pwBRu=pxbkD41Z5e=<IdmisTl@)UtJCEIu8`;Nc2`X*k+g8bcIQJtT9ern%w|9`POf5Fa^?MLcAQnUI5{seQ09_7gYqRw%ibBz8P|15eG`b&J1=&dRJO{t514BZs{EWR#(QwQA?FS<6qHh&}fA$qH$>*8ymA41p0KP=~B^w**;`Vn+3bPaqX{^n71ExhQ)_{RK==;6`Z2>M6RCwe4$1iCT)bN=Qt^a%VH=+Dt3@uLH#_l1DbpYylRqlJn7g1>DQ-Da(Wre8*>i*AD!Ci;2iTN5;YlM*z#H9i%+2HggKl4DQ`<C=8(1pWknBU;{2lE1l)PGgP$TA1h)%#kg@^kz*k+QDZ>3(L;mh|iE<dK1vu@IiD2bawo&(YbyLntmBG@VBj-1%mk!{^!TgQf_S9Grx`F$SsHSKmX*r&e6TM&#)2w_;ob>m)@UIOaGULqI0=Fs@A$$MtQ%_2}b{uAL2MAzZ~HFAKddpYy'

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
