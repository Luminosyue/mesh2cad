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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_003.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_003.stl', 'source_sha256': '90a6ae627090b2201c0971594c82e00217bd0d5ffc7adfae94d1c599e160433c', 'input_faces': 832, 'input_vertices': 582, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05016223341226578, 0.2827063500881195, 0.07994677126407623], [0.048736587166786194, 0.42491963505744934, 0.11211702227592468]]}
GEOMETRY_BASE85 = 'c$}r21#}fx+x;h4AUFiKiw1WI5W+wqcyPBHNRW^K4H|Ti6ekcukOXpzTS+0f4(=4EXm61srC3|EE#Ez7?+cmJ{@41i@8ez1+CTRD@XVPrXJ*dKoZB`nQm66O@TaKudzZG3Y_&8^L?+E!8yONYd|=;@VHF1tjr7p6NniYN>w>_Jt=e?;&_-%weS$-V^^NeUWApLr=j&76=F@LT#PEoq!M%q>1cwMeASi5Dh|3=~AZTca>+hv&_*N}%t5&AGZM^M&`NzxE1pUtD^#@&QzkTaceU}>VqIU>&{<<1|i(jO#dG(UMmSw*5oxWG3ukYR=eZACV={tUWh5QGlr0<yAO!~Ge%aOlx9_plRiu{J>rEgBTj_oGaLjCnCkgo+x->Bn*_M~2b`UjGwZ||20^((DM`>$4lKj)8ivi_Cf$Uihw`nKjjNZ(mI3fnz@0qs0{4*45T!awsKbuOMp{**ze|7IZC`QU)`Z4d2eXVK-TUt%%xbA+MJabL9m#X#gc0??lOBj88%z;^q!M1I}v@T=*lQ*ku%mp@1Sfkoi=KLr11$(^#D%SWz}{S(mQvh?RfZIk+4xb$tF4Ww`09xHuwM}Oq+X(xT7$4coNExRGVM|J7z!K0+FC;A{irWE|%V^F7PDd{`=bVmIOkECzwvSYQ}uYmk$Ps7>LcTS0yzWtxB@P7)~F7uZ^UnRHOF+1uUN=E(eW2EmK-v-;g@@5<R4}Mff<c~=w>*zxUOW(dc0QvS8+c<tv|440YH}nbGlh{W3j%MxA4<|~>I!66^s9&d?Wxq`C49Jf|e;U30Wxna~fWNgMwj1&c{kbM-rQB|}ESC10aT8a_`ZLl0TC-u;ZkNu|w>|g6c0Gq<zkUypzCFx_{B(inw;8ojr)D;^=X_JNr{8ghY|rf6*ls`q{I`3hZ#&Tebw-|ppKq=7opt?DXX;V-jc21y9~^h>{uYaGOXP9f{Tl7`3`U*xHQ?_&D}86K?(m<tMt$!L80RJ0q0Y*$u)pJ8%6!MZ;)yBu*SL5eb^Lsn%k~uQg8eFq>x|aB_;Sl}d7B^S%ed^)x0kS^epGGb=iI(b`lBkKPD5{;@2%!b-*&nO+8;SU`ex6k39`Ok7k)%zTsLw@O5gUZ3H*I?kbf+*^qpaC(Vpb=@;udU^^KR?eTZ?ZO*$%l<4HI8`@6w^9D(-y-a-1#phl?U*AMM4Qb+oZd3~^7KTN`P*snD5Z#Kn#mA{DX1{9ON?T-Se-|e>aoz06_^4-@HZ9rzUXK6W0z83C<{4I6hJARbDzUlr_nZK|%d?&AmTb$CjT`UCu^{!pAy?buL&yM~ywpT<y9K9laM_RN~A5s<Dy?jRc&QP?+_`V9Z`{xeimnn~aC~-*EciIxro_1)bzT&X-jq3BT-Gc0&YP&4HV>^zE(Pj<&(fyFm<7E^-isQ1X1^n(sQOAhiE%(>k6LsD-gP-mij#s`kXnzxqx5<ZOzSigZ5?RNAelRE8#P}I>5q>bPSNgN_GT$-uy!4%`d0jPcpgm(wBA>_0tal6Boq8DgA2AL!+jMMq#zFW=jp1L~DSdO>D(Tw~m*VxO`ySb!Q6*6S&x-KdpOU^gv#9hPyzl7!no8gC;r3$bkMKqPJ5Q~CD9<n6$Bj=n;CE~Yztn*}DSca3T+g)*YjFR~a|V8vVE9${qTlSxQ70MayAgZ@^^*rl-+8$c+Mn+<&X)(Rq;HSqc)N$=YrbxT`dyl%ey6jj<Kc%oT`=CXgp(NO8EYcH60Y0&qBA%yQ?|y*_7pCH?Q))@PfvpXH}6w>Z(DqOnVzWs;3@X^r^vXJ=a+u-C64dk{iScK$>Z|+XZU4Wp?-f{=gl53;J5HaesA7i);`AmwyuHtUKqEA?Kialc<Y6-&gGKWZs0rA*?1&Y)|rFrp0PP2&eQKr>D#-a{d&g&xXxVM2%pExm~E53E%)SDoEN>2-=Zk;i;P45ipt0zkX8C--*(b>96<ZE31zU|Z|Wi6Jx+KXGox!Ee_j>r@2kqVZkYM7U7n{#Knc`2ofH0C*7q)m{Ad3xu+;Y|hWr|rr0;P0pich!*srl(@Y5HEzq5nIcV5JP>4ySQ$M9TW>Cey_(s#`8Sdg+m%^w=0J&WJP$b3KCuXWEBsI%g=^c~?mFOI`EPu_%I8spiR(G2y^U6;P|kKUGi?bl=Q-(dV0O`Bu8#XRBvSPc1D2IF`|UYwt@pY_(^xSn5(m%ejGebkv3hW1qGD}8&7mX>^5i?;JE{Sek2`CXgNw~Q-yez+g%$6)?x%o<|x?aMgc8V^IAvDM(`3_^c?6M_A`^LC!}-PgU~X_!|}j*-5jJm$kj;aR9ttg`f-*L7Y`=As`4rG|eE*LkyH0_snTkCt`Pw&e9>9_q~bFjwwxV_cW?whNGd@|yG=70?g*;7Qo8hexIFe9!A=wpbjORLRKiz<JK}#W=pX)*^pLE#yC6hdO_an<KaT2J<CtWfI!+NuQl^oaoE9q967xm?`@wM<D7K*oHcF1ElZdb<AB~?^0d*j-_m8=KZKMq8Rcw_eK4~M^I;CLFA|7I6PsZJqgvOryM87)twkuL;a&<{!h4n>FJSg-{viSn@6r&vd*9lXiuB%Q)ND%3(WPGkRQHM`cB@DjDW}Jx3v?Ie;4gE_PoG$KQ)_b>F1BnQ9s@KDRR4gIS#dF@Pleimi{mw*&Z|Xa2((1MWk<EpAYS{Z9#raKIC5v<n`@0v@^+5`i_+uWWK)f9oqTi{v?_IT|Knt#d)-|#@&f>zj%K)hX0QI*Oezoe@uB<#~3vh?WvGi`t~h_(ar_C(4PKJ#>@P%S+LzAnw%Hef|AEc{|4vzr+z^@<D=pGv!6rXW4l)eN#9-<{j49)iaO0pNZ;nq>s5{X(swkOF;?bR!TeUQTnO{J&}(C4ea^#;`+sA98?=|ctrzFdFOaWaDK=XA6Y%_~tuKoCXO)(tq<^mp`l0+})ag=P`p(D2(GQ*&S6XZ~={u(6gx@wj>g1X>Li!QBPqoSje_1u@+YFA+L?6s2Q$PG#<}cuLXwFLT-+PD4{dM18#^&CIaq)Lp%6>BzR)D{7yYy{&IiEb@3qRk9K{9_L&#$Uqp?*+MsHM)mmdH<Ea)4}40_KN$rw;HBGzgLTZ8$$X-5tK~qafKojWMq?{^|?=uiZUld+K8TsaFbvuPr}xK;&PVi1!trvhPXh+aG;{_a|p!cc=6ng=Ztbc}7dVqttx7C-Eq0$+u-&2tTf$wa(JTsB<l~rH<_--bWdCk6PO4SiBPL>Eds#(|9%NKlotX?(xm2vn0||$9`xFw)^h6HUAZS{d5tlU+)0?Tz4$KJpsNkxUsc<xr6XaXSUYqdK&)d6Bge&9lrJ^jnxl13%_eQOMP2yyx%j1rL*Q=xrTnYR^EDi^WKG@)X3@=EQ@gxx5Dc4InE4QYpw6TZzd#Ij+gUpRn+kxw%5|mX}GWHtCv{YKbg;cFIHRYyPw}57usj(&rFy{ndvrIx4R9`BWBG+>vmt^d0hK5+In2v=kHUSwLN^^)W%G=Y}c^_^G_{#rS-VG@3UjJSjX)wzOPF?ZP$PKddzl9JMF75uP~C6E!%Z|kM}3q`$X$@d413(*S6Nr%lWx~lC^)_^Tr$#to^V8^DFJ%Mr(WA&uh6l?)p!E`4USzZRg<Y&jPIZC;KD6euDKpJrIul&A4{YfBLoSSdV+Rp{R3h7TWpjR-jN@jp;ZqHW{eDJX1HJj=49j=S#13J!HOm-P`e?mr!Te9OV1^pw4x>UFM&=i1U4ES>*S>8zl49>*~G-eT3R8o<N<GHQ;}mA1vEbd=Kg*w1NM^H$>*E*X<6ArSJH#5$9=v(eRBO{bYN1Jv3*pgP-vq>Dv>~emz@3w7+)20kV#Izj!ripsd5|uzvh9{Ek0M-+kTCjGXWnbP27m{m1>N#I-@vSMFch@l9c}zIwlF_eYqej{E+YrbM{()%$6}^&zr7Z{}ft!|vn$7?X9V%<pgx*F9$`<~zTZ`>WiqwXH)UWPYc^sPmy7>Wr;8O!|vZU$1c&eunJBWu2Sb(GNd#fnT%I2)SRq@%=(yJ`(kd*M+anA2v^xzB=E~hOd#nGYa=dt-uN7FDo-r)(PVGmzOc{Z#krIPdpC4WgO-?ouWrce}5eM!D|ERhZi0#>nQUmt<T3unO_axW%S5x@NWi=k@?De%t(Dn`s(~mJ2!8vtfS2LwEIQI$vVpX&=}l*T*~9_o=<AkXGve3e`+5#!&m03#=%R{cksKC*&qq^r@p~<jjfj~=h6102{ON#iT#bgg*sy{OW$^64g3cY$R9s=qTFuLSkxb|2=&k3fUnHY%}v=1={H=4{%<w~b;7Q~FSrPGcFlqBopBQK@f}Tj6oviW@w4>*^;{733H~IsN3X*1(4o*|=_}72=IZIvca%)Bj9Wb>7XDUTe~eT)P^awIQ)GL-M}1@eOyr;3Bz^Vy$Xs+9`EN1r(w^h`sUL1NRn}LYv&{K};Kv+A`$wIIA36oT`n=XTTKcwQ@#r_(2-L6ht@PFBKD|&f>L|~N#`$~Fw^zh@p+6ad{@?o?^?PoE&+C%u=NBdGD9@*QrfyLw&oB3N*lZZ_jjY3Ymp&TLWk&iq={ub0Pp#)D^z*N4rSIId0sXwFJ?gymn<nez*bDzgYWU^$NZ;|71HMNP$7jjuvOS3lE&Xo}tO8$o?$-VoEq%wXC8)#ul<sIYL;6E_{WnqHh-)o<XAtJS?(4G=86<ss##6{|zZ=K#)LHl~G0u%Ut<jzawwbcN`hI}E`aZ!ZQ5E^h`v>#yX2@6HSIn3%eS2G;r%ih9viQn-4|Bva)Ni-eGC$W7ZL?&)&oJy)->>nWyzBt@{0{EE-x*Qor0)pa&+F$))X$f7cFKOx)-*>yT=ku8>1X$S|ExcJ<-LtLe7N+TJJ24pxq<iUTYsI6^KpS?-fkW+=15<CFZ6AU^quqh{4z2h_V-EZxiWtok5}s|s57rN{M`8dZVsC(x2unDEPdzY80?oH?we+%5y)S?+WLHPZx!;D_gBXG@1_5F-gs;&+Ie(`^wsxZ#+JjVqrNwby@Gt@J)73;9onP5m#gO$Ew{T6*Au-%Mf5|nMCq&V_q6g`r0>4o8bvX$&=0*vzDGFxNIx8xo$sPkjzf2StzD{lvi-_?MLk0$_{w`o$El9ex1GQ|<nw)Vz<lYe?=v;uB-F8^J^I=vXwSvpr2lz7&@>C$bL0(t<$bBXDEoX_r$6UE?)&mYoAez%t1NY#K~<%%zK_-0*M+aVzcm8=QD1rAtJQ6eeC7SHUZsun)%VHvtRcu(-ai{&1CW0j?+wiSxPIDqF2#10_t>_?^{CT&F!n2ZM?81fFJOO__u+b{Yw-CV!+pMMMc=}2#PcHP6UKAu3^8)M%KLV6ZX5V@`lFpoJaC<9J_f!Y=Iv(QJE(v0D17C8zL|UtzWV+@>4x;x?*&HuL-@Rpd~W~rSEy5;*QJg>S$y?-gc12c`v3ZVF(~zdl*jS&_l}?p(pSHyxPA3|irZJerx<A(qE0CLt$kWtm!7pjer7)JM4Uta>>Z4JUT?K3m`9npufSKn`{?JiSd1_0cOrdbF6pb^m5eoc;Va*v%!I<RDUYMU_t@IVnz1Rz)#vY7{p(w|>;8`4IuL$jH0ng}MSk<PsH1#GGt-VmzVh8oe>(+!nE{sfa&BM!ey1mYhkWIGpBBFl+l|2d*4+F9{J4YCw^i%I`_#VODSh>OqA~ketmXK+zdzRa2>%Z}zw38!eKR%%E|l9<zGIqe+rsDk-|$$*>-+-g+aJ!iJ|9g@6DRAh3PL*<Zr^S3xn1oD-t(I^s!Lz}uBw%<gM8&Xtmf5P`s#OE{eC~>tKWH#k4AmvyRf-+D*W~{(9S+VXwR$!={xK3xD;Ui;LX^s@;%z^tKXxwkZs6UzH1wu_M`r_rPyx2@37tNMHV3+?{)Quy>VQ+c9Fg_UoZ6AoG{s+`jZ6Y-<*p4GBtS}+lc(j?0@HG^#8W~tb=iG77XF{ta6K`&->Bm>&dI?(pSIN8;|NBU-`bTT?s(Gx*p(IYw7=M{lJn?)KS(Om;uYAudYwf{yByE%6bOl=~dKuhxLkjT7K7l_#^5l>m^L*Ewsmr`SE#nru5bI7;ax(U!mQ;i+p9BhI!;S<n#Xcd7iWV4Yr%m1N|J{1;_Dg+Y(tvSs!BbFC~3-J&6{-Qu^xp6Me`5>8tBiw2-6lmGvz~_tU7atcNi=okRUQ9EYu%>`dva>uSul7f?r8hod#U247vbQ}!|Z3ElZzmIwXtDb-S0Us?ZS{Fz?*|5`8fD7*A+Z6=|gm%KvzFBd|7EUz<%KViF3t&p#*M>4t&fUm4yGV({mSJpw9xnfXXSqG(g#!LTS>#45oLcX&8%GiAx`>U+iGLtT#&a)|Ke@##L8!n@cy6)@S8)&DxPHfRn@RfCCM$A3bSJt6v?K8y7_9*Mtw7^W#cih48GGlcduVz`L|F89LRSKhyvR+R2DItAzeVtLv$CCefJ)T!h<n#Ti`?_jqerS)fuFv@BkM{8WgI0AS>fdOO`s(_?Gd+;6tS8hD^?|RfKhzUPVY^8fZ>IM-Y`5X}@S|s0uAk=n+h~7|u6*wM6XRr4rUcm@W!<AbvV!y-f#_#_*)in%wUxfDC&q)>HwXIX-5B`Fx=JnRI{YQLzG>sP!LR=e^_BIRW_0IevOQaIAJkrSMg2*3={qWL94@Pe{;aq_`u|%0Std^U_Engln{^|xU+<IQE9*#&jrUO}lJ_-!AJM0NgkKr`sV!ZB<I*$da#=@Rr`o&-{GTRSx2u<wzPjF3D_#q}vOd;$-9h@!;LbQ+?arb-H~XS~`z~nDhBzFT&~>O&asvD=JFs2<Bd9YC-))WEW6*DTZlO-a5bOI8Gg~6g-%-4OJ;C@{R#N)v`d%%%qVyd_@I3YTy?x9n)N#+x`F>0f{2g@;8R(ySi90d=3OQ1aH=_c+A2}AamA<;(SewyJ`s(^*?OiZ@Wj(X;Bph`dqxhcoAlg%N4z{bTmv;N=dTG-qPWtvo9j))3Rxg5o81rHGdwz%4I<!Ywr)`_Q9^2*n1oM&;&!=ybQHSrr%#}aNeEZ{lXpgcE+}`;F>Zt3+cix20`IuG#>m{_*i@%lsZhWL=zU?rUz`w_F)gu+2qtAM-klS4m#`lLjUi-7b&xLuN`?_TN%UAm9`gXlvz>1XP$GsljY}Zcuj)r`GdD{uc>r5xqSJu@#5A{I)2li)BFvdgqP;B=q=Pefo!}pp9Us<>B_HCUyTJr60W}=-=oR3EK!CY^jv{L4)zYECeu}Zc_`5l3t)@zmJeCO{D^veFySAVBqpVt=o%I_Mq@ja!l{tm)^FI@WS?<Q=WMxeg(I}7LeNcigSGO|BMedTu?+S{e8Wqsv$AI_#brLX=@#EdPuM*jcG?@II>KGOf!?@$hQmA?AB6-Sx=$X9;nqS?Zculz2?o_!?pmEY0W!fwI;vjE0z&@-(29WrvQ^l#_ExE(nk*NtI^;cI31-XH+K7kGI@`pz}JIA8eOp+|p`zAdr>@-t1v`rG%J*2#Z&wG;9$<GQ2=l$XA}@mFZidmY#LcioY%{GP}j)))Ei^)s1&!T528N?-k5lCymT>f{}V{Eq3dzl#=0U;TZP+4%tKD8GlYH#&`c<@ZyD_6O>x{C!p%%dhGF?shb{;p0kmMF!1V>lc*br*y&;f86@tKcyR3{r~HybiUR8&p)NB;A%s4SJb4|BiAH<MeRuz+Kc=Zxh1tXS!fWsB{`7Vmn^gmIgqSV8<TaiKeZv*pWK|<jNF{uks-LPD_T>VQk#*Rk{eJPk{ghlP#cq*klRz+klT~{Q2UbmkOwdXhf;&cq2xi--sC~#fz<xwf#jjoA!MNw$V15nbp~1JOtL|qM4e6+8bzK&o=BZao=6_=iZRqF)T!ht<k<|tbEr||Ipk>SbaFI#9(4hE9yy-6lq~dHay)qj^?S0=E#wvCmDFUi&~4<E<TcdY<Td2=uGmW5L)}f@Lq5z9e2BV@e28pPlgTFeAoT$GAo&IL6<KIH5AX|eS`TPGa$0gKY96xCe>89^@;z5Pbj2^Oc*+p`%oWe6kEy?qACrG(2zF8*lAYwc)O+N+<U7=V$alyeso6ciAIX_qk)K+Unw?ydT#lNDT#j6cnvX2B0J##m3bi0vXf<*bauZkdb;Sr*44{r84<Ls!1iNkk+H`6Zbrd;@Jc&AjJc&G!Avl8Cmn<}h96|0yZ9?uvZc4327FvVcl-$e}&8ao1HOMu|g{g(eg~=JH>B$+$_ciFR8d&H)@_q7NY7%)bc{9~P-b_xUE+Hq97gJ-%i^=n;)5!D5-%!VqzafvM4knK!hg18J!^t7kZsZVh4{BX<53(P%D%p=*jarsmja-gel3b2lifSX5A{TQ-erjH-jhvU9i&}`Bi=2~Mkerk3O)X3oT7>LP&P^>!&P~okEl$ou&gY5()DqO<<Pzl4R3CC_av5rQav5?JhTt01isTyPTGYzqT4Y~pC9*HMHnk>M=vQQ+Ey+Ry$wGB<ZE_u|Ke-OM1+_W31-S#YBe?^)3qx>sYFl!5a#!uk9H=WpaA#L^qPC*8CbuFtqBbQrBG;!jAlD}cP@9kg$nB`@$?eE?Y9F$l984WR4km{&1b<BpC4WsGNgYHUNghQVNFGHVK^;mKYLJCaA`6{J9zh;P9Zw!cj?li$jUpI=hr41lHIh1p97&!`okE^Wo<*Hao<*L^5FAULLyjdcq(+k$lH;iJ$Z_OF)OfPc6=b0+$wJqV7m*XF>&Xe^W!jfH(=vwOb*}i1x{JD%yo<b_x`(`<e1v+Ke1v?1A@~mUkoIL>A^0BEB;O-Hq8=naBL7BxK^7|JRlo7?f*(;+k%iu44fnk25%p<``cJhlbp*erJ|n*-|E_(RhyBhF{HH7apuVI&C%+^=p*|)*AwQu0OnyNAi6Qtl)k(fhzD2!DzD2%Cy+gi9zCrz%;ur~jM-_9pcl^6xPmeG2JWqz;9IhxrEkn&uE<>(OElI9TZa^(ZZa{8Htwa`Dg<OSmrk2zoa!Yc1YF~1DawqBlawl>RYACq}xj#d2I5m<SP9Ep+Wga<>A$XcA=1^m()5$U9h14kWLh=IYB=Q3CJnBSp(Nvn2)fL5EQG)7C%}Vwre{|*Vb;TZ6Y+wjpN8L?cM_$7ayo$P$yo$V<x}Ch5yp|z&2lX6z2l*8BHu)6!2K6WM4f4;_>*SxwKf2-v>RIY_@>%i;hTyBzpU79q52&}v56JhZ=g9ZS7pU9G+u0Wv7=o`*cawLsudgr!-=*#)3;l(Bm;8qMkt|dk(>MIP;EX)ZMadb-UQ`>|i=2sCn4F26g(0|*D@svIQwx(zlgm<V<g(;))S~2~9GB%7f-9sLyA>FM%e$fswHUPoxfnSY)tj7){Er7z^wB>I!B42ake`qbQTLJ$kvCB{kT;PN7=o8j*O8Zy7gN`e7nA2P1ka_eBF`m9Q&*Ft$#K-R<T!F7L-2Rh9pvxGyQrtgyU1s#H^^tmx2QjpZ;|g)e<a^0-|_fz9^PRHzU+$Q)ML~i$j8VBsb|Rt$@{4%$ot7h8G=tzuaZxauTdY6uaTcp?~$L9pHnZ8g<c^Gy-ODQhAdQ^W6$|_!LO)ZWD$aYr)DCH5d4msg)BmFT87}<)I#Lk<bo;A&w>oWC0$XGTA5mkT$x;zTAEyyT#Z_mT#a0VT8><f=V}dx;F{F(<eKE_DbDBW48c`gQHkn9EkpJp7oip-7a`}M<|5}H|Lp-4=ltIc!H=m=$dAb;^$^)4Z=`M_ZzM0HCXknrXSiZG^&4seS?Ch-H{_|*#pJ1EgF25abRyXx52Z$sh4vy3CHJH@B@1mv?n&<L@#VczZ>pW#n>>s<oIITSFpN5tJdFG`)gT*e)7R9V<euDy;O(xt<px*mpl&4ZAn#-d-sFnqu2}1e)znSoP0U%%5WI@Ifn3iuHgs3ibwwSjKUF9DlfQCBV`?L+PHseQNUcY1NN(VY`cyw^J+dFUHnlFfHrY2t`+OOKYq=t`CO%+^|0JZQrK6^yW+0~_dr~u#J;~y~)tH@{jhdO9jhvO5iJX<3CB?S0Fa)P}MQW-CH67W5tWncwU;YSAMfD`7BB!N#k<*ehrr3v!48b{E@yQk5+-PcQZmKsqH`&J(b*QDN-sDo`Y*bM<8~-l&Z&zHUUZj2^UnHNSify0c-vyu6zO+xU2*D>bgkUd*;Jnn_<h<mvR3CC#vR{gQ^J55ZLH&x{g4~VTk=%_um^zR=m^_O*fjo=6k|B7xE9O(jP$!W4P=l!x$P-vMm?5|=wIjJLxgqr{azk=;Y8`SN9?R+s!NsZB$i>N7sp42><=+MWmEw5+#Sr{~A^5s0u23&guad8FOk83J{(*Xq`~&$6^)&em`6TrO`6T%mL-2d57&q_vcfna0f^F2iWE;66wJf<JS*QAub#gmu3vxShKWaB}Kk``WVDeaUEOiz+mYhUgNlqePVhBD!T~0ng-jZVcZD9yr?}~4!v#ImRv&kc=W619DI+7u{yDJ(|TT%OvTajB+gUP`hyR8|5>r)$&>ys-}tCOp9j8<j{E=tWxE=tZ!6=O6r|1LNq^#fUi;4~fx!EgEhUnjpM|CnNY|Hu%0%@voa7pPar7s%(Sm&lhm*3UBppQWB5pCzB7o+O_lAEzE8A15DW2!2C-Pkux8@PLZ*!Gj?<Cqr-vs*PNNT#H(fT#Fn))yV<mF4T79F61z3KXMp(3Uw@b3fV!8B|FI5s7d5)<cHKt<cH)B48gCd2gt9<zf!l5e<fd}t|wn4@ALR_UhShMllPHtQcsg_l3!AvkzbPkr2awvll&JoRVwgbWRFzP^kffm8fs>88ge>nPI5YOYHD_JYVvyzXa=$f!7r#9S%l#8)ZaY7A_RX=JwpDT98X<Ajwg?&&Loc~hfoKRL&$*)!5v)Dl{%U_h&-CSh&q$Jh`g1$g1nXNq#hwV$)Bjdkw1~Mu@6LFWMc@<N6kRaM=n6kPA)*sPt8frPtHrtOwLQrLrqW4L-wSmB72hGavX`V^_C&{5%n4Q5&1CnH2E-jGc}pKnY@(xEqN(<GIch2GI<DfBw1*8@(^-ok1zM3&J4kAsQ%<O<i^yh<i_N>48f&ck&9Z4T9sUkT!HFOu0ZysHX;jcMfN4vqqZgstxv8;E-%{L!XuS;>i^e&3jfO=@ocGC{=@j{zqBs<OZhJYU9~<h0&LSFt$aR7<@%raXqiE*?$Z7TcDU~K'

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
