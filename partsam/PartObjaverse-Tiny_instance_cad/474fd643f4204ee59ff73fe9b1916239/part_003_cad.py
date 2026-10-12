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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_003.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_003.stl', 'source_sha256': 'ae33d2c39656942a298ae7b0c4d4b8a305154e42ea255491ab3181ce333ed76d', 'input_faces': 666, 'input_vertices': 627, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20164945721626282, -0.16310259699821472, -0.48962315917015076], [0.20166310667991638, 0.26319020986557007, 0.2995404005050659]]}
GEOMETRY_BASE85 = 'c$}qt1#}h1AN3}<6?c0`2*n+WZg6*s!wV4HH53X<p}~W@JzR>rv$$)}0`0>og`h1C-^}mc(3ge(Ip6s{&bhsJZ+`E$v$M0av$M0UTO&ry6bAlfF&Z5C<M*ni3_~NKk;3R7(z|b`wjq7;b?-UQ&qyM^{ujklYB#D?x2d1e-xw6wE~HP}-hm}ufu-A*2+ZROY~Q1I-`>I9TleVQE=2p4gS++#QGTC}!97FNcFtmjisx|^{yvZEXV?GZzxb*M=CZTL_vx~%TzaUS=7y<{YBs}M;#+$Lif=EjcSQU$xesdJtp6DC&ss{nU8Cy(?b|JvAC|bZhmL9Xm|6Bqp45AG>1}J~2;{FBU`u@51N&vWUJZ%&cJmkC>`-jG@Tb5%61V^TKH<ENw@G;;+rZCw0RHn{@YBZLEx${-4}MrN@$K-s@TZK%@7{erAmzDN_naI@%edkjq20Pkc@MnVE5|i{pZv~vS9q9kU++%&UB;R4OO)Iwzh9Cc_254V{=+ewB`&hw3Hf{D`tawjT_DF>I^vXYHWPjh|GBc?HetyB_`)vnTb}U9@8gc$BJoq2!oQqqt@!UFP79BEzf=4+2Np@5^(Qt+e8^Mrtv98X$=~zVL4B9>BEIh*(}fq!Stow(?ub9~a-WoAbt);pHDdA(iCcB$SIwT=#m`B779SwKm8#Qf;c`vnxa|ZT5&zO}o@V#zT1O>*Z%z2!!j?;X_JXLNDP`bK`hJ~o!FxNTJOhisU+0=7Jfp-?DbM))*l(foQcm;QR%v&}AIGKL7-w4SNBfLCBk^~Z!auZnp2VjgbXLmKX9)bz$5X|xpW>u!{~8KES@O-AT^G|F#r4n&ezBq}gr~kfA$jt(hrgqp#M?z)p?#%jDZZ7kIF4g}D`{s@z7cj1?RMK#Ij`1`GuXCrb(ivI?=S7ey0#GQ_|coa64$GsTyNG#58};+p;G?1YcEQ9a?eEk>_gc9+*I;AJ41c==SNF<?BE}E`ugVV{@{WKCEiR?2l>a}mN>KHlU=^Pojci9*<SlW+Ob`yiul&$bohIPKwNiQ@*+>dlxQCr&mX~c6NvbpA5cH3n#z8oe6x-p{%%gi{v%@{@1W^Y&&IPLIWNZk2V2qJR-;|NZ7KV;CeMby^1al9eYzixcijM#`${_ez3h1OXM3~Cw)Gp@i`A|!%0=IP!t<Gb**+XsX5^_{RqDm=n0t?}Z;fBKMSj117tU|3_t?(%%VIfSHEzlIG8!&{A9xYRoA)`+bLQFNTUiUBUOGR-dB4yMeyM!e|KxY5e{T-)&1y%`{vra-N_{6zjrdy&a6F@mokDq@pdKRwmPmZglIUk{hr)l5dA79wMy1Y6{Hs1_-*;vr&-ijU-gV6ppEo(K%XdfNUr8*!H8^yW&g<>a@r?X_@yAW__pIg6&yOmG`kDM%e51^6w3jT$(B7WkLHvtw^iQAr%kg>#-4frPbxw}g2s$eF5wrhN@vXf#kw0)OewTO@{Cab69z#l^p0`-o@3ZaFF6{~{<hu4ut%mr;&v8E8RnVS07lj`?%|h%4{j8@^V&oZ|AN_xaLR&SvpT~#aC&5PHYsnT!z3zB}?P@X5e+?>){%7TV@$J+fZOQXn?g-&fFXEHj9wYHP!)8VEt6rTg$Dg65l;3#05&pnF6D3~`v=dK@R^nT|JaXT14azC)!Fbge@yX^$e`q9lfIP>m!guroQNFW3iSobdPwYyFclH}q%fPR+NXp}W)J*O#-r)tX-wqW$!t-10jOO>AEXQjdOpkteP+s^=@-4^p5(oFg;OwmDW^&zHbMCH@`VUA9f83!dk|$`FjC<S}62i}P3isctcO<{}^rsE7pENh+{$kyzgnG;J9)64-7%x4|d0O&Zc`3fNw3D<Ga~RsWapZ~khWD=AkL($L%6>hYABb;n8jboeen#HacZFT4V#xT&@b4<urPsQI{MG$Y?+x4RjpjT0u_)i!k45=L+xO__;^R6qLoZ<e&i;-5SN&V7<H&PA+c=5uISu2R1~%gVNh9aih|x{z)6TUG@q4bVlKM>1QR>Z1xdHn<x*hlNv_Bn`dP=eu@l8@o`?N+slRWOoh46<DSuOtk4{}~So-p|C8q!Ye<N?_4h+pAfT_V@JmA;U~n-eVYy%BZL&t5Je;~I0wPl(_2Y_jm&lDLoe8z8>>Rw)@5TSq)gB!5r{;va9pakc0!$7MzNV;1a@>vUzcYqH&|9qMPmLh)UT;JZ_|#QAFZmmI&*t()`@?#@jSU#YT;e>?|^NW7hiei!)0EBMB%YS?dZZ>b;q4eG~iSpo4+-%Go7?Q4p0-Jr~fuia#Zl(Sc3JP-8F0Dsw(g>s!HX^#Hk%DwgS_ippnOZ<_aE=is<cf_}U@}PekIY;*EZNFE1<KL=sUfjDPQ2u2L;m5Co=YcxIq&)W3_TrmnM#*Dec_jA{Z}ujL&oE5t&2#_oHMGx$@Z-*xdT_U1BEC0&J@`YXNxc2bpI7C&N>mBuZ)?lA-_`J}_@0(IQT`k2q@8$XjFNGq(KsW@b92mb$unn~<hR1!$oSR1)l7VAQ=ptLE6;QB&ALbMoKU6s37n@>@N*BA`<K0GnY0rl);i=F8Y$yrSNUeBpD~NY_twgce&A*C8NwCEAkT>IQg3#Qk{I7U?TYdAg>1W}{wMy5JU8H50RiIM$KYEZQ;YA}vgZJ<n+1&}zV7w4!ehOM#D5q(TH^Da72itTM($Jg!P>}^<D~e;mSFKsqYnIcyWvMRo`81u8~VB4^qY^8<8}8>bzS_+m68ALBOKS6R?-gb;|1U+e}7WyxyYU0<@bvsrC+xr>*Bn;9*6e);y3Y)<W=N&Ex)&Ne(fLoA%1HjDW@m$ck#{gDa1EB;C^nt?uT+-nJWE((PsN{i4VSp`utoU&p*Y&q@1qWL#6($Wi`aNn_R*3@PS2WpBwWcPkG#T+<SH$kLEk>JJ!NL@m&L!qn|0TeX(%PkH1O$^u%(1H)AK3^JCt*E55bWwNmz9b~O5*rz;U3dw|rN`LPVjlmA!o?KVkK|D7J;xK<B9yrUoZ;)j2b`<L<ajp)9!f5_Sc<!PG%&y&~K&vZGxO8)-jx|}ap%uG1%%l3<J&5ecU!<*aCe(ElU|8h6x6C#hHoOKt%&x3gedop}8!C2%E3z6}F>%j@!U;5RBpWqVC%Z7(2=a$^!+oi(sd_HC`+Ew%Hh##CA{YJk0;+yxg!T-137|B049j=dwu~43Ew$#7%s2A#gXoPH=(+f*`GfpLvJa)h-#C<r0@!mhfQT{u}#5d}kM*GY(0{wZ@neZETl>3pl%Tu(ADwE+~wWJ=*mER$cw;TM>?DI9d-4SSSNdvIo-374U@i)=_ZzhAk`~><3>n{9h3-H`~qk)`X>&`tnU&gSq@WYGG5iV?CJXSh~_}0qw(hu7g&PyKS!+DI)iUm!UdN8UNlQ=t6e0$$Mw3BXEq@Op7^+f#Oe`MTj{jv}Dqop-5kMQn$X+Pe6Vd(eD=0~1orNlR0PC`9&2t=MVZ!tbeu^Qv@u`c)vwxYci_!0M=Wr>mh&CfE9H{u4#yo!C|J?2yX4M6@DCyq&cswd)GO|pt_=3Rh#n6?=H-a@#K2Ngnj@`b^#8GHiQS1{Uhu9(QbrGdn|=ElT%KXhrS{BDj5<*XA6^`E}F_{M-Xa$VczZE06lqRC5e-g`@bWiN?;Gn)T0-Ac*-u46RcnjV1TjWhLnH2>mT@vRmw;Fqn2JhvLkbzx24dd=6j_WH~H)V$O>nr}Q>g88+e$mss0aneq_=R$G3J#r&YvY5zU|1s)kQbPE_*Q9;AlDiSVHg+`MdWHQOac@X}X<w*>`&7hE<eBoj_{I+S)=l~c4#JOl1oL16iy_Z%eUK;HJG8eMS<!FQ>x%xkV+ZL^j4XxFAHHq}f8+%88;y8>T-yfuH;>17Z$d5XcV0{Qy&j0~4Zcsm1@gSVE51>k{*4mwpD)Bb*p}1CUzGkX55|G3;M>^?A%E9TQvdE9=>M$)32|I=%Srojc{-ziZuJMAZ-1zc=h?UDpN)${#kc({%XrNDxGC}<!E=svx39EMdp^e@m0aQ*XIjgArTK3p+S{KW<+;x4-Bj|p{qi8slNI8dm&;&&v&}-pPtA|`%u8h6)he|c<q5hY^Ni-Q@p4|=VfW7Z`gYGWxV}0Ri;&+xIXM^Cg}?aTih+n9xfb)VPlrl9xL0P7daxoE%tgEVP0p`-)g!syE!QOE8L|ueecTD{;a)Q72kn{}B;MNF2mXP)GLLDsor64u?_mD@a^acc&*^|X3q#NN`gWWqxZbTY7sOw99pk><W2JvE=RCmm{y7i)m8-<J`mV$MYuco#^7m&ea9s@8e=VBda0lAwlpmt`#y=aRofr>ON6TaUlo;1hcV2h@hKX;#&nNdySO2*({<jjj#5XsdMES?AKZEv`7I|FB=8K<c!6exZ*fB-^UUCci|3&L0kI{Gt{J95kzE)O{^I~MpA-?%GANt{w2jsjMyW%3geQu1yd(T4s7g#O#OKa<4>Bo(1g>T6A(m{Bx%Q8-U%YKReZT40vm$|An`qlclA4U1blX`Nz-V0rEUV7J>_^s>3>h(YT2N}dS@>G-dYzBQqd)|Fj#>d9fHqvif^RM2({uW`}{5rPm*ZT47NnhV6`Br@U;=^;kzWLmcd2r9CT$pcsJOO#;hs%CltJ5OCt0VHHcp}%G=haQr|EBEW5?{O^o`WvkKzsNr&3NHlWig+-U<umc=0`FfGH%qID96=sv0T5#{A8nqd(2uU`!!#n{(o!~ChaGrAND)###vwAT+u<wZ}xqPdVXG9d?R?S%x@ZPD_)lP^jAhmo{VYbynDju;k<9&A-<9E2HMr3vbe5m&mDpKJdAPg&&zS$Js5)c2F=mWA3lZaz3d)&4`dxHBjs_A&+sSC?=Rw;^YTgg-5(l>Z^REle7v_9Z(GCv@bwLEQJlw3S&^r7F8Eh6qn})z5%IAuSi+C`<9$ZS5%7y-94h<WoI&cry?@s^U*8%ON8WF_{@xwo>l=;7;=NbO&r)y3=;njj9#NlL#-H}}jcLf^j(P07uW$E69y4Ejw3F+7LWRq2l{{9+N|Yzb5Ae-~67LOP72)gK>93-kJ07Dvaqo4O^5m$7>vUE@w9l>XPQo*WZj<tiYKZIQ;c~accS(TvUej_QzGpS@?eNrij&Ae`=eJ3`))F75tK{*Ps*F6LyIV<pzMqQwVC6V0|NR!ix98(IwB8H!Gw0ql7e2EV&zn<vp}mDJsx0~Q<wkiX6-9aMv}J|Ybe4G%Yg8co0!d2=?+=&qSiN{$M)9<A{NrjalJ@*}C0s`Z#*`BO-fZMaUJ-eWLY>9W)K{)M_w`jbqxq#HFmA6>IlAvGPn2KegZM_G*wK8eT_K#8RYB2x=lvzhcivy3@;mP@QNHv3Lf`y63iq|^)vo*ccCdx_)7{cW^UZ;8a2++jjq9aEPn2g%M~uT`jlAybo2~m{KCoNEX#Q8%FMa3r`^9%&zft*}{R4gbY-aS&6N*Rko&C(0{LX%$)xgkiwukJe2Y$2tq_{Ikd}n)`pM3B)+e4k$Kg+hWJtuoOMB<&-MU?NnE;h6rD!+GLUo|4ccV4Gf?st~#*KwU%@5&Do-*LTLd3z0){W|-H@)yK+_9s@cq@!fp(O-S>9sO05|5bnWT`YMY^Hu*z|EvD9Pge1r{ijuR_*mI?^yg8&vp<jWo&C9$C4Trf+sX5a;ooeZdxwU9t36u*^TNN?{;lyl!@t#@tru6|??JmY7o`{9dpAV-BRg>t+)t}6#ytE?^i#&iow)x_UwOvYx3Zqcxbb{BsRvKZ;TTU;s*iSMUBG?0PO3?=?HoVQca9&TeCPPVb7mUmBU(+7@rhj#;}h?M!c$OA6Mh_*Tu1iret1vj80VO&1Ez_e1>++7#$xH;JewAX?;J<DJFG>#W87t?-y^>H7~?(DI(^dDxAS4V=lSaauA?(2k>@_fdscFc_uTy(PM2-Rc+b8WD*jjF%#JJJJI1B17uVniVjOE0$2ivfAHJvTBFq~)#?Mi{bNuXnb9tu3JvxqY+KTd+he;L#?>Qagc~3xG@r|^jaa|wAxZQm?srb(40{8k7$m1CQn}avOZ?_5UZ3Uh?+_i?`y^-U&#x-D^_{QoY6XbWJxW1sn8oYlkc?8d!!#CnRMT$&wB+hYv{Ng+Ak5Rt!{`kdr+#lUTci=tZ0zCJb8`q+}4a_XhSLV(T%tu}BkA5|8KJo1jjqyA+wY1c~=Y2;!k2#(zT_I_)4#n}@YE~R7^VDYlba>7^j^|vnO<5UdIG>BH2|@6!R=uU21%=_g{H{vkfAxHwvKGcGj^}ancyq)rG;qG^;`!Z^wm0$@n~m{%rkV1dz&sTxzH@#c%6HBW7!69w{nF?X56^{dyJJ4_Vn128;hcZ){x3i8Q>^oF%wxFA{Ug3%u9f#I=A0{7H<7s_)?qm2L#!9=;XCG4teV}$ch0MLBF7;<%RtNvKFcZ3UFNVO;ydSUyz{az{pNLjr!>}Et!;_-C)S2wsfV<y#CLaY!1qM$o62!b^+*5cm`CztYa_nZ67yrO>IJ0zcrW)vykkDi-7Zvo=RB3&ZwT@@=Cxd7hQfEugPAuM!FSA?xoRwdf9MY86+6JUB3EF)j(It+e|+g5jSmN~-yxU}v>qpf|2OA{t5-n35|jnLb6&AZR?NdX<{`c3>!bg5%x8LX_ClUSu~5#(nE!NVz<lmk^P)p0Al@+_8|6FaW52|oT`0aa;z@LWDCT25-(f!1o$d(y1cj%`d3Qa)x_~1Q@bi`6e0~#|&$nw`h3}Yu{^C34pQC)|{PP$8<iFy(f-(Q>J~nZM#5v}@Ju{cVKZ*Xsc!>8Do;iN9Kj-|v`(!rpznWL?QXTQmdH80-#ka>4$Mtx90LE!WFN*)weE!4R@Ez|3Jmnw3cf1#{=03-M9q$*6(DGPM;CSERp4=V&y}~HZzD(#3|L!Ng^F4@raM#}?-tk_>jy+F&d*wmAUtTg<<{#Y|n_^vs<9(33UKjX|_ea*_h2k4!@SfCKa24%*<W<BU=KHA!iBO*r$<~PPc>iS=Nx25+Bl`O<Z=Q7GJKv+3RVpLi@m|l2+XcSk{hepmK=GaL`>g#Q#Md1<R>~Lj2J4Pu@4$ZN{(yeZzTQ>hzdwxl#Kkc`-MWvwFLr%;fa7w!m$WDTh4@=|k7?%N`^q<oWL>ZGy{9)`3h`Y7!sI=l@#_$|uep1t$2wr=`_o!ok;n1A)%tW0{=r&!AK3p_tOK}lQhew8Uvoet;s@eAxE0wO>!Rj8Lwx>zxbFPRBK|^EtRr@hz&gC9cn@wjm@K~YJ-EGotN6yF%QEk1XC9Ar6@Qk*yhF_F7$@9#&UI2X;IAr&dCi+xKj2+a4}QAsSSOsKGv2?RY>DUCLJ6@B;U(Yif9`>GD&Nn<@qBK8dHe_c#Q$pjK-z)GV_^M&S?&$mf5Z9k)BMGC7cDWLe`Oc)uO5K)QM)H%-oN8MKA$_*Ej&Mj@;lbUSWW(dAA;w4?+L7{F(&%qJ!BoMmoUesM1S=tF6U*q?jj}LH@UaP$Go;<ordRF62uR#Ec3W_qghz5mB7SvwPQVrJ)<e&9qUP4hv_HgdXk%bPn|g!exskTzGW}gx0plwAirZhjG1Quj?1xr#*Bn-l>dPDw3%|r`vcdtpAhd@C*!HS82)*z+p+eepY-%wgFK;kv7YeFs$b-H+t;By3$|fhU*SR0AA6b|f`5VQeAZ7z{<oLluRo0SM6O#y<b3VF1>dnw$;|r@^<NL`i_FPq(0-~sM|tc~STFf5JJwg#eFfjKPRVoTHGIc<r!T%^y^}p51HMmitf%s%;&%(Tx6Au<yGKv1)2oB=>x(paZ-1f$o@=@`5#Mt>Ir^WjcwcC4YbCyOeV41ldgS*{iggL+9$@@fc`x$c#d<U2ViR0nSFRvW=y-fba=F2-Xnvba@R#=5=j$75R?7D!=7u)ge0^(Ru-w1gW#aDl_03P`vEKJX=Pl9lhu6Tm*lq9ZX#P|S>&5^6E?R!O-f<bPyMwYti#JNH7T=ur9oBgoSFzub5AZw{iuHS*8uw7nf8XQ&wF2vVJ!L;2PgAVlvkP)vpAG-3^?uz9SyyfOEyjF84y<FekH!(-I5`jPXF1jrn!$15JJuhn`wo1^x@Fg(r0~zQ!n)Z3?XjMzR4MG&xt=psRrpq*#2aPu<Na&a9>~)_7oMj&1YrCZzrXm-b+ewW1K~T?*;)m+i~rR+;n63s-;PDFULzdqe$5v*;Ln-Q@0zgA*&Tcv<(YzY<96^dTpvx6<M<ux)ve%E;v4a1<ND0{2=Axs3_yHuKWYE2Fs|Po`7`1j>$JT+&ca{RSlY8WDXFxRDBt|}4BtyVzrWYlw>AtH-+0}Ao3C$luZMA3#A@5uw+mgtdh4(WTcYJ}{xjCESMo%QH-j#qoxe&OEx#3+9qWJ}t=SiCziSg<y>Y&acz&P%9=>D!ygfVs-xD~$N4VmL@qMzv@*M1~gYO{hxJTii!1oA7!7}oD&yXdUr@quf*vNPZ&$}a+V|!*+ng8}wUxV*owj|vy@h>vs`;HyqXkV{}iSPX0$J=ft{K5D>$Tedi?swKP@y(<7p2$l24D)I|<H+|(UwzNgr-1lYc6^s)z1xQ8?9QzbU$`IE1<Xh;^R=E49pO8_lN#Rzeu13$4yf`kGXLU=JsrOFOuoZ10{9(P5ktNkv-fwv_ZGSF{gH8|>rPyE&+*)P6!Yu$$n)^iV?BZ~qO3g6+Y5ik_h$?9V_cYt-(elPkNCyoFb}ez5XPrvl42cRDSZEBRBev-G&PI(#`eTm$9SlP)W7?e;utp!uZHuP@RQW1Vg3aF&qw$kZNfqs7rMKQ#(bIM`!)CA35aho3i~VA0OQuB^k>qK2j7}Llm0P$53uaC+%H{!pMk%3Cg!mk{ebal!L#r;&q4V^;ajs_!atk@<L(#u{?7BFE9Mt!9+G(LpE1&Iy`f{!|GvcchDQH-n5Qpv6Y-Ak{*0E7;TKpW=iA<T5zi%gisJb^0QYS(XF=)Dthp^PKNwyF@0kbR*@=2v3jgZ4ZfO7Sv93Ah1hj)zWAJ=z|0w0R=ViyZ&}(D8eb<^e-c4E1?vL)o`P}p?`rR&T5mzD$#yvM{o|kg%?TX_pwhZHeB8O3*;kod9o9l0B2WI@%=#L{J;a^|90@v4LX%F@r7sh|nLJ_~WKKhk3=kOdmYzeOCZtDJ1H`-UY=W;dMxIMFKc?$826h`}CpHFbLDb14n?N4w!75TsW1h-hR|KCq=1N{u6o<dfI?h4(wosC`{ay{yLjHyHJLan(LbvAM>YRv%(*~xl42e)gIYf;x?uA1bo)S7Ek*QC}t0?D-*)0sMuT%X*Tx;}L$g{`Xo=P9frw4OwsLp_OlJb69!c<LpD*2f90FHmbfM~<M@yp{SKwcdXq>pBNH8+A6;TMnOk)cOMV6+xauJ%`5-LEcJzocoI^^EsbmImcr?$FgYcRr`3N@Q%<ru0OQqkK}~Z8d^W}1GIkX2VC^~&)51S`3&_*>SKh~Ug8Y*-HGR}JJFeKup4z3a#!k;%oVlYV}AdY^B9lm829mx<$22eJ!SdNkmFKoe!`eCs*d!R^!do&Q|F^DLTFu>T5~mW6>81ZsjE@fWX>|&E<;c2vkFfXK9W=WL4TyKPH0`j4>7;-Z<?P{YiM1AT$k~hS5ViW{)zlIwdPgSHONu>)p|O46}9Gb)DzXdMkur)*QFk;&_kiELL;)??x)MButi}mS#RG~2v@j6o<MzCA+A10isO;>b_sRv(kK)p$D}TzkXNAqIXiW6{TqeX2KbEuJyKzcq32@2VbsSI)+vlrXinDKkqUn+EGEyVPNDYUr;v{P9d#jvztsNXkuOjeQCv*n9|Qca0ewUvrf%=#IMkUHyA*nnds1go$fD3gp*LA?&r(pgB4ZA@3H3;Y(F$i3&Xe_aELEo13hVs9>;0hLC{$3}e<;pL*4tr<!xc^|M3D9NT!m%|^T^Gq|5aG45J_H6-9{lqp(CMnKk^Xje$;~qt;Z2sk0rGB@V9xntvLnt5NZ$kl>uEqAs1scXQa+cor0W-T5}9)&9SLdQ0u(GirXo4AhhmF{+YTj^{<51)5r^`b$lLrnv+xiOuc~o(t!S;I1zuVk;o^1BJNXj2A?uyU>P-kPo1AS4><#M9_r-eMAV76@8sl{)NX~g3hfE4`;Z4y_n{s^Xg!rYgIe=UYW>^X{JZ94)Pt#Kklz{5?-eKHZ#5G7>?<MnuQ|O>dD64InsfS;KPQh#b3SS}bz5?7ADxriIhiXrk)CBt&wVE&>#`=}w$}O>G{2?(UR`_16#@yZKly=g`ax@GeVx#H2ch*QLhCIGd&qy1Z&LqBos7BlK9X^t-&1RjL9O{N<C9TG<+;oKj8@06Q(+XL^)`hY<oo2E)c2_$5?Xr+t#=Vx&mxbeo<;pLq4gm0DC$Af(+I6Mk+)Gtm2VTF^&jN>)PGRlRd}rMLg71gyuT?7S6HmjT-8Y<g?b8=$v-IksL(_qgxs1sgt{ZSIdw<sw&Z%$QF*nlMb_JG6gnt0BebqUbYN^P>bA_Uxf8hqbtmff<TlhAjeTOYZb4|>fY7>{LQz#W=@haNTBjhiPC#g#m|Alpax&`r3ON)^LhGc|n)4G$8J~zcD!<kV71AiAS4cvwIXRJpG0Dj($w{e`a=$6b8K|?U<1`hrDFi8GRVYu+MxBi@<r$;79HDg?LhDk5)+Gt8OOs7%&1HRb7H$VIZ&pHU7r6|zi#ijz6m=%*4CIp38K~2fOH-$(&PXmxosl{-ISX~Ls;^%ZmMN?y|3c`$g^(LiYj#s>9!9;Ezga^Lp$=ip8ba&UWH+_urPR07wR%8dDS0-v=JC{;=TqMzKO@hl*1VAV8TCs->p1@4mDHM7Q)_6Qh`fec^KI%|%zKCYlKK|e@CUR`=?`d~${*1B5o2FczvTWOaa-$u$cd=`;r`!}b$Q+rT3=QuuKauodB~}$(^5b11E;00@mP6Ds5R>xg~>^%HNRk-j@MfA3F?LFkY_8LP^hEON})Y@Hnrx3)EccBTZg&>p>=;El-^{8<q9*1>Gbj{{GiZ`(7KyKF@=H(xd^QTh=TlGUh1gdXzoHTNL`S*x)54-BIlyk+=RNZLLP+@)SA006jvyqkekptJ5hkY$wM9W8_gZb1*i)!S4TqY&g9(GnwwI`R*0iep3u4iIUaQd>dN$Eb6ay<>Uh+Z39TzBtW?;cu#bF{dLQ))@*Zl<1E@7Oq+ZG2Y$mimNNByCyn=c=b$4O~b9E=TAhfPU9zd<R9raL!J_>yaty_|NQn#f3k^WF_YaU45lln(O>)r~f74$S^PI5`=oYcQ693U?um!w`qJ)F?GA~`d4MQRs0HMNU6twLvY&34oMy+5?(mh|*?PkMU0jzV>X8Vbe8m8gqRfA9mezNYxNANW04`|r7}byfbZ26a{H`sC`=^{MMB*s9!z6mAh(KO(fgN8V3;kNPH|^<F~j1%%dP2(8DG4^fY$_K<DrSL#?UDJ1p>U!m5}I;lUP^=m@w-wCaE5n690U!vYhy@Akr8=>`8@+;~bYG0py%J7+g(|m*a74=o(2J>m&Nv(OK&%QSLlwl*wrFpYYIXCk-H1DR?e9z|?@A(}2J=TY2fB*mL$DehkITv+eat<OX|CZPfWBVk2KmvszLhF(WKPrs!@wFbN@C$hnc@*^`YKz>T+M*66H>3`wE=w*)orGmeKu*dsX=t5}oR&Hrb!l>0>axsPn#ZHrB$uNu$9<bbLmu~ewclq7pU7$apg&PpA+)aQhnNlgo95@#8d_H+S7W^9CDc`^2a@koYhFfOl^nHSt*4NeQENU${kz(ipW>?qp!H`1(7J*jxDvIkuvcLcc>?tW{(Ta;67_YJ$DjN8om%J9T$$RBx)M>DztudMdJ?rwXuY5LuQ9J?gSj;f=FnV`TJuEe%G6Q0H18u%q`u0!xJG>DJ`C1VMREn^uE4seNK9a^iPZbZd#N9&-~Q#(m;U9`-~PouSo5FMns@v3&%4=I+SDHMOllAHSn?2`{&ooaW6eKNYo6-US5IaCt$CwQf4<SDpWn#7zl=Jb_zLC8DXANf#}HZ%<=>NVTXPV#=3&&s7_0RFKlBSxd9>F3M`48@6p9jBmm(LWE=664T$s8rf1`Cvg%%2p39TDZYi><$Mcs<O(fW|W5rvBe__6_giF}28nffT>50ej3A7YNfe*gVGD&{EjYQDl;x+&^^{^S_cz14quDRd|IpsuI>mPsK#IR<qMZpR|DPNfi&+usqf=<7UX8K=1_btdXmgw`3!y{I!%*CwB$u1$TI&^nenz(7O4npXWWp>-j0R_fB^a)j1F<gC;I>iF9!)FgMO*4%}<CUrxFt_rQV-Gy5F2UVGJD}JuqIXORB`}qm2o04l&H>GwHwVAgSway>Fa#SR=E=q1l-H`D`39S>5b5kdv-p+FAa%)|;hM#|m82{^kz5U-mOB$E&|A^c9%jnAme193Ha(!7mP`5^`*l48wa>57dH%!L=0ci5Ccm'

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
