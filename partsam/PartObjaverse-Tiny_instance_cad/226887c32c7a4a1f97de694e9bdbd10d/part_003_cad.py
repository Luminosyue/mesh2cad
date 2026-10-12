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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/226887c32c7a4a1f97de694e9bdbd10d/part_003.stl', 'relative_path': '226887c32c7a4a1f97de694e9bdbd10d/part_003.stl', 'source_sha256': '18056d5c93091b8dec8687a9891689e8733bf80917c9b414676819c4a2ff28be', 'input_faces': 1372, 'input_vertices': 1067, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06650669872760773, -0.051333025097846985, 0.06001192331314087], [-0.034371085464954376, -0.00519581139087677, 0.10590603947639465]]}
GEOMETRY_BASE85 = 'c$}r3b+}Yj-@k_r>69L%rKFJ@X=xFV=FlPCl0$b%NgvLELmawG7(!aQb0|qcKnYR#xo6#Ly|cdKAHVB;d9Hokx1Vc2n|=1Inf-B{wa2<OV#QA7Qh&0#-rmYNZCqQI%h?jSQn~uI>(!@In|8embnEe53|F#1?)=f5QM*B{x{YJF`nd+>YTK@Nn_js}xpS3iUouxdcdqu`d-dtns$0wMz1p^O@+z&m^ltZW-n(O~9_{}9=iG%pD_$a>yGWjV?ji2~-JgX2o`Ppq+zor3bGe&+dVsZ?>@5E;{KZ@<uN*ZiK;M->9)9uN`oKRA9XQXScSXisP9Apah02R{TpXNxyiZhKB6CFWaa`l?26AuO)=Pu`USFOYYJY#rr~n@?-eKi2N~-hBRVT22*s+W1I7{NKaOm5$WqWY$ioHpl|J;*-{XOSSsyu1Mm4W?tL~gV48{WXr<$IJgaQ^<@N7V5<#aR_#M8B=Ux&C?0{)2sL|9aH|`}<Cm*<$6F(nbWIkL&&(b)233)z6ipXdw4y+G+j0t~W6^TX~}fOM|b2|JSYRIOVSdeqPVh4eICJv&sH>Z(Z0JoO@r?QP=s^oE_HwFHWoT>6TQz?o-yQe8FV(x-WYX$lZsdt?Tc)d0>N;kNkakfCtxX56)e4Q_K#Wk9VAU9p|i2dD;exgOBg)uuL6iU%tTkdtNTu7M$yG;$3%Ty_N3_51gkf;*dJek`d}SJ7Px!UmstOg(}bZTwR}peYaY<9-lR{tPjpzjjAmUKED6*e3cI_wlw&43`;&o<#7sI<H6*-FT5kmth4emPnHB<AK&d6Dj$<G@bmf-djqeRd*d|w{HMg;Y~{D(FAaVjb*{&)>&}j~fxmaeWR;KKr(Ume3j(i~f9E*+`Y*q_F*tYS`*m3$FBG=J%K3cI$M;Met&Y>-RbZTWi+mq=9mAWBu*Qj}?6D2OxvS?OmG2v|-OBk~($~$OcbLj&Y*gnN-7WAshP552j_->M{Jowv-fdRS`1eNLULTyB&qMvXpBSL_ukmta@ayP_(?{(;so6^PI<(swoSXOQwcP8i{U27I5Ik<fFZ8g_|5?Jo>*!zBm7jNk_4n#rf1Y^H)LUome=}-i@cYrzud{XiUF{zPUPs^BcGmfOhNRkT<@)oy;OVtiUcc9n!1?fb;vUx88b6+<Hv)feSe=&k^?&+yV{ooNZ}ss_KDcH70QubWWoc%Of7hgU>UuW%#vUh^UvIE-KL7RgF?rEyeS@#3*Vn*$|9Zz(4jkY8uC6uCy&cnSuyTDr;`KE-=dbS<VMl9OpFggqQv>JYn_Jy_pZfB4ULTyh7LA?|JU&gXuRr%Mcjv0s=cnsY(!lY<BPv**C*DGL?7ZQtk=FZ8=ZqhHKlS%2Z+-sj<9jNWu|5yI&)eBK<6PgzO};z((7@lz=Sg_V&#n8HzCP}nMXk?seSDLP-eU5n$p-|^pU*?j=EBx}R=>W!r}?e>k-k1A7yZZN?o|DP$B*a7PgPzs@5JEo89q7JfA%GlbD!0(yUF$Wb3gJo&#v+cdq-LCui07tvv-+%bFxXn<JRQ*`s@2?`;2@JJRcSypAYU5>Hf37nSAM`(ZTOKlQXXLeLpN-8kMh4Ixw(5pKmTt^8f6CI@jZ0_Y;%1Ej~PO96nFnE0U_b%iI3JuS>W;;eYl?lZ!rS@{Uo11IOp{(6u3+eg69XGCcNw_fK-!KTRIKVqoxj`o4-`U4MOl^rm{ZE|819YI4z6P0sn7`_Yz{>w?FRzQ6k#JPqWs-|AfUTa)YS&;8W<`u@7$@vr-dx5IUHe9?zZF8Z*}&A8&e?<#p^UGV!?_bb=RQ`Y(G`-RCxPu979U+CWA{qm^FMSu40+-qNd?sqzu{n_j<`m<-^Zk3Dv?D=csy5R9+?$<gO{aNR-Kl>J}R=McU-m+2ZIHEu6T=r*^i~j7nxmX=X^k+|<*(w+P+2o=>>s<C{Z<ZM<7ya2gZM@1we>S=3&n6fB*;8nw%0++nM0{tTzrJ7ST=Zw1%l_=`)lcQ3Kl|=>v9CY(JDtn^Y;w_`y`$Qz<B0z3$q{Ca6MY}ox$Ms-7ya3FsIkgLe|D9qtBx=Fv&lt&*17D@o_Mv?{<1$0sHpar{h2(ZKkNNPe|DuSYoEWqzf35?&ujN*oy-1g_Lu#+$!FH}*Y`*7@toHA>-&YtMSnKA=+B-mZfpGL`@1V~di(lwztg$w&n6fB*}EpCHU4!!@n%kFj}z|WCKvtL<f1>jp2xM`zq((!!v0<xJkE6wF}di^CKvtL>v|K&Wq<be{B>>c`&9QRoy-1ga?zh%6&|Zx^k>&5zsf~_Ho54}CKvtLRsX8WMSu4Geop10Kbu_iXOoNm?3wkm%0++n#675T(VtB&`m@PJfA(JVaU8opd#i3!x#-U(7ya4fvOhmuuX53!J&l*ET=Zv?i~ekK(Vx9}ma1IzXYaguYpwSw$2WPOOjdt3x#-WH(lb>q`m^WyWR;8lY;w_`O)mPgYsgrY%l`aqh#LR0Ka+>_XPt}w?48nI<)S}(3iedF=+7n>{n_NQKcDVwpTEApe9=mszv$08m;Kq~qCb0*x3I3ixj&AmuW~uxt8>wxO)mPgD_d=A{FwXufvW2KWq&3Q>CZZs{kiQI*7!I5`9cYGeA%CMF8edN?9ZNlg{=3l>Cb8NTIX;2v(9CICJ*V)+p=4qKc+wD&R}1E-Ji)r`m^3&^k>(*wASaR?zgVaNv!ds@7E?5{aNR-Kl>BLw?6;%@x!8HsN;zKtaI6)O)lr3YrbC-*iZCl_m3}BF8Z^{MSs?L$ozBjCn}fo&;Q(0xtxF2xtxF2x$Mu2Z>n7O=VTY`^Vj`Z=dwSO%l_>1pHaE&&tDx`V_kpUpUFe|v(DxG^UHneIHEthXY5)NJWlj|T<5Ysn_SL67ulk6(VzWGqt)?6e>S=3&pMa=Ijr(BwZG`k?q3$E{Y8J)x$Mtof7zeM{$QWKzQ4Sk!p|%EGkHjV*89u;d}N|^{muRH^AXnh>-&YtMSnKA=+CaJgRJqR@9(~WeeLVd{Z8kyKbu_i=dcXjt?{q>N!X-z_Bi1_ZgSC|O)mPgJAX^-{j2+x|K~>5IM+SI<f1>DT+Tmtt7m=wnEB^h)vWianSUk^nSa)~?9b~ft6cWytYxgv6Vsn{F8j02MSu3~E2eTe|J=Hu^?7Let<L5Av(80-cE!r0aykFpCyUDE{IkyG{IkwQfA*(J$8qfb9JVEe%0+)Rx#-U(7ya4YFp<hde|8^^X?-5*ers~kpG_|Mvv1Ca)qz~}XJ7o+tF8Ab$2Yl{e>S=7&nus+T=ZvG^+zg~>j!i$`m@PJfA&4TqjJ%o{Y|d~a@n7CF8i~|MSl+a>#WK}e|9fCp>olmO)mPg$whzmmpx>kzrMe$-L1}F^k<#R{%ms5pWVZDSl8e5=ik<;T=r+3%l@o$*`KGcw8oFQzZZ&B=P&y+c}RcOx#-WHvkO)SkAKroD$Y>H7ya4fqCe|g_GkCKNvnh3zq()fM~$)0U*9iGF4t+0%l;gm!>e-9pTlSOv#&q*JDtn^Z1xxZ+26jm%0++nU+QFyAAP?zx#-V251D@+&_?B=KYP+OSH}_kS?97pn_To~*UpCOIHEth^43zh=+7n>{aNR-Kl_eXQMu^P;axl`7ya4fqCcBl^k;YCQYx40H->&@pTAzep>w%@gIxCK@Y?xRF8Xu$-fZ^u*S~Kim;Kq~qCdOCGO6Rp`R6k!t#M-JpUFe!pLH(!vu{Z<m5cuDOA${UU-V~_i~g*0*`K|eTxx&OpI!C;j1KH4`m@eue>VGz{_Ow#RkU^f`u@`HvC8H84f2rn8+w1ypWVeDL<e7g^ZVK5H>~s5_Y0GY{%ms5pZ!%YMF)=`GylBf=V<Ht>-lH$kojkwi~j5xe=It9{G0jbKYh{GIMMUZI+yd$I+yd$^LIuEzkki|_e*b%4j$*Ghv;1NXOqkM=j&_KbrAhIyw=j_;P<KdJwCbY&n6fB*`H~N%0++nPnn}~(VtB&`m@PJe-1A=UFD)bhlh_<x#-U(7ya4fqCfk4j8eJi&#pTIRWACo$whxQx#-Wn5q&t0n19aJP33a_S?6;8S?8iZyAF0xx#-WXVl7lI`m@PJe>S=3&*5>Js$BHv@P1#}?^C@#MCYPEn_To~ciI|!4v6&|<GxV2T)&}nxqd_EqCbZ>DyMSMpM6J*s_`$^@si8_Y;rmO+_`|tMSpgElw0MZKbu_iXOoNm?2FE7pTEApWc*m2zv$08m;Kq~qCdNSO=VqwGr!d0BbAH(Y;w_`O)mPg|DV{__%Z7<yT4bxS*}ke4_TkAbJ3r}Ja1P8kAK}y!Ztip#})nA<f1?8JY@Ywy@#uU-@m$F`Ci_(&fl!})4Ax+I@iCKG4szeuBlwkKgT}1%DVn~{+T>v{#oxY=bx7ySGnlVzREwX3LZcDer<BmpLH(#bNDZNRNk+t)t|$^*`kgk`m@eue>S=3&;DE+)p10B_W!U#<)S~ET=Zw1%l;hxd4$U4`i-meRW8?W=v=Pf(7EW(u0gX@F8Z_U=|ubdxnG!E^k<!i%s)>Wt#Z+yz4?dP*Pr{H&Sif#x#-WXlLORoM1Kw|-`yG~`aZ66*`G}=`g3^FE-DxOIo#V?9bfcklZ*bW^N{)Htj*N^qCflhHBkGD{;YG^pUwWFKl@tOvCm)MU(QwL=e7H@&Sif#`-}eU?Ni>m{$_qD_2<_4o8MRJT=Zv?i~j7}QrH?l`u^_Ena95V-0yTQ`?JaA{PUX}*7!H`&mA+`<3!It>s-!1>s<6_fBZDo`&aj?@Rdoeac+8u&P9JVxtxElp1}J2G3z&WeOMX%J~it%$V1j|=v>Y}H+!dY(Vu;PsqrfNv&lt&Hu<7WR)6*`e5!J}ej~|UmCN-TI+yD=bT0a{@8&I)i~j7db5Z4@Kbu@Wx21E@pTmDU#c{;^^Yo)Cm-Ej$m-Ej$7ya2^=zz*afA&Z0P`T*OCKvtL<Z}MG;wF{L^&9tAue9E$di{pZMSnKAoPQo2rE<A`<F)$S30c3PbGd#)=b}G*56xA%=+EILrm68S`m@eue>S<Cf4)3k<)T0P2aHs?=+7n>{n_NAKZmCqVxPahzf9<@&R_Iroy-1ga?zi?dAnNI-^?$aXs>cP|EzO4|EzP-pM71ztnp*!pKml&=P&1<$wTI!buQ<h*M4n{e>4A_rMf!4oPXB2oPQ>l{n@{_qV@hY^OIp^t@GFS3zLiftaI6)!(x=MK7VvS4C|HOzW&_rbT0d|*<bW$cgkGW=cnnno7~p;(f4bUi~g*0*`K}j)2m$cXYWtR)N$ncXY!Es&pH?V**7b(I*xpPFm7ymk9dAi=kobM@{sk<%l}qCzg)jj?TyOi`VF1S^&2`D{n`KUH<ioz=OzzUSm&?jpLH(hpUFe!pa1l$T=eI#`Bzt1*Pr{H&Sif#xm>?d=Da$NoPS<(Y(?-mG4s#lA@k2V7ya2g<gm&`fA&86Q5|3OXOoNmtn-ld&r`Rl{Y8KF72Kfq7yVi1vOkBp)~fyG^Mj{X+2^nCFJCO-=e7H@&Sif#`-}b@c4wY-{muN+$eGspoB3y*%lT)Wi~by*ZHhI1%<q?Hj<T=6UcW&evVKG7a{js9aBKXV^`#g4+v7yv$8|2BAJn<%&%S;=t@p2)e}2%x8s}#IS?6;8S?8iZd$zY#*Fp5>usltz_o?ntI+y*~<nsB!WA#-opC9a8+xk2)&kyQcK0l~)G5;L)Q8kr|{v0;AoXSOiHo54}CYR3-)-0`Z(Vu-k7E-zB&n6fB+2nHlbBnwjN6bH;%BpfX|EzO4|EzO4{~VrK<#PQ-^3>Mnp;^D7bGd#)=W_meLlTwC=LhS>x8JAw`9Yn_=LdBz=bvB2;B!FCKev4wcwdFgKkHo1KkHmRKUnk+m5cuDUG_xXZ$y9Ax$Ms-7ya2&<-W@0`sZ!eR4&&)>s+pX*171<-m#bM^Vj#6w<p#4i~g*0*`G}=`g7RaBg=!YznOn7wO{3O{#oa8{#oauKZjr4wLEzInBOng*r?85^k<#R{%ms5pWPYPEe{_5rk_k+rj9TAv&lt&*17D@zWj@q2fu&K`sc;7tn)YPpLH(RKa<P#8=mgpt6YBnhJT!W{q^%c<RRa`q4$^b&%;NkT=wUzgRSvn`m@eue<lz4{*C>8RW8>*7wMw@|8o5^dC2-_oy+yl=i8~{i2fYjr=`k8e>S=3&pMa=IV^Q!mCO0(F?Ccf=bv>h=bv>h=byi+sd730e58VX{(Amd=W_m;JmmSoj%8FX`m-lNar^q~=Y7a!e>S;Xzp<*II*wfboFS(*PR#me@{sk<I+yd$yRxWUe*Z?Zbn5u>`!{qhzkh>V_GkCsDb)V*`N3`p_}mlE50ZyGKdAQ?{n=YCu6_Rc{<7{b_5Kw7S?97poBieb=en<>g0H`se}3^iD){`({IkyG{IkwQfA&s)6cs#v%<q?D`lGDt&;3s4vOk+#&Ob+9i3%S7rk_+g7iEnTeIM7k=+7pX^UwEAL<PTp&HCpC2UITCIqO{XWOq)V`gui9_RQI;_7{EF<Z?c_<a(8hKJ2}`Qstuenq2f=&v%h3m+O`v&y5Nmho)EPT=ZM_#2G4=^TT;3M_KO|JrAsN(PP6-j8VCq2QE7#D)@bE=6iK6=X(<mRJmL)F|3Em<$4L7%jfd4bXK|Or5;}!d;II?{&X(-r>j+S#-&(4eD-UV%k{%L7d_M8tCq?|&kRdhRgEjrGj%R|rhBtT<#Ii6juI-D>w$GHzu)YSBKG;{&(-#ys`HWGJ3$`uy=U>VTh~W_{<~IWQn~1dCYRqYQ7x_YdYO6D9f{TX$az$9*#kXI;#uRz+)v-T)Nw@LGr8z{{`r3{3m(sAU2dWm%Yx6xtjpE8=ymQJ>OLy_o4fYCW!Cl4-*-eV`<wsSjb*{_cQX$;_0qE7*US7~Qs?q}9zHvxjw9F8E;+3Bm+NWCWgl}@*r)cF^OkpZs$9-n>Rf(r!^q9*_;P;o_f;yF^OHIk{mOrExynV4@)uiVpO1cSf;{B=$}Y}Px#&yo{?qO2qdz~%Lw+y+@kF)1=tZva!>!lFJfA`yvVJwsAeD>$<2lyH8YkwyLoR!c>)UQ>fBBr(^|to7)z5R0%RUpfx|MxC`g1H(qh-PGBlCM<a{YTxv+i`ySJw5>pR4{BHLTag{Qg?!a(?eaCF}Jv^Lsr?t6a|G>0Hj^B`;=;A9LT?SU}~XZ<t)p*VW5yjb}4ocObLM<-DBEMc;7E%wWC0%yUC=QgA)(zF~5?{&U$!D(CkXX8mWHm@1d+JasPmhWo)kYJ7;k;coQD(%^Ao?mIe{&qKX?rgAx-HuvFDYuxI2Go8!t-70lQ<)UwRqAxEEejl0NtLj|z4d0*(d>)D4FF!rLH28gOe!r}9(Ko^-|D<xc4)dQ~ORe#&*J0{h^bP;X?J5_2!(V=#%0=HWxqL3kze44rZ+M1BsBtO!hR#Et>;Ghd%H{gW8Q-g1uAkJooWE)_)jA(<%C72j?EGkTKB8~vT=orj-(lAEG5@~#OJ9}C`6!)>z7f8)m-Tv?d8b^R)cMGHCvw+?R#x9|A8BokAJaEFHB-lteM9G>Z}<{4w8pbp$2hR2bv|Ytqt4|#QjIUI_m_E|Wp{b|`sn9d$z|X0HT&FpznkZJelBReUgo(Toy+fKU6fB9NAwMM(rjvf(KmE1`-XpAMzz13=c$`U<#L`!=khuC7fIDWi@xD$9asIc=o=;%eZyBcmdZun@I}6hw9ZGbGbaz3pQ-dp<?{KOEsr9t>!W`kK`#4-fAlYEf6+Jmudhc2zb@u;o;+l}WzI#Fi@xD5c{(z9oS6F#x$GPM%SYAz^0}DmzDR4_>gQj`L)Py--eI4Qo<EtmDKhwdWadf8W#4e+TVq`x^Y3vBBdyoP%!lY)&WCgjw_Y#vIe&Au%H_O=&PCsF51SSlJbui5C(8tti@srU(Ko_<BO`;yvsqtPXrRjFIy#-p=TOe}jtqW(nddBecjbE8eZ%CUZ}?JnP`T(EzERCpF4x8BTz;=ngC;7MedADFYn+(Ap>z5CNc-w47kwi<UL||n>h)1N7k$IMqO8j0{6@N>*89lJZ|GdkZ|umga?v+@O>$Z9YxBIb&gJ~Zd$-Evy0tE8?eVPFt?68TKWCX#Di?jjw<e*=Mc**Fe2$}bY?X_?;eP(NdVfA>Vf782hdc*8^^MBqdNbEEmCN;JI+x$Kx#WS$i@yFY@b}X<ycKS%^O3(7BM<prpu1Nig0GMH_qh6JR4(T?bS~#NvY(6ye!a{(@L31d`G~%ubJ;gs#rH%6k00~zxfi#o<H+xa*SY8$;r%y61dnI4?(5-l>wL_*FP)3N5jK8FMDY8|tpCq5-@ZQjc|h`z=ZlZcj0k?eo97@(Pqbby^BjcE<@fL;8mEpU`i5)BP_@748#)j9zV}Q6)c&Gxc=z;Fx#$}v7kwkF<+tkia(?4<E0xRn4V}yRjUG)^F8W4z@&@+#=ykc|A@ds>YpYy7kC3gheSP%v2;{PF_+EXX_7{D_*S4hfy0|VJ-w>RKtdELQSmknlBPy>oPR#rUdC2#uSIMFFm(LMw%V3XNeIIO;+Wvd>JjS~u*89cWf9J-xeqQtMWeGnl3BJze`xvjiUlM$s&F6E?mns)M!Sk#7y`by^zRCAhE}vH|aBE5MxH9WT7GF@gxbKH~PAv%@&*nZje81XX&JXP0vLyKZXzt_Zmn{i?znkBKq?xPo;QM1;>%U^sbwaH~r#&v0vn6n)a<y+2^q(+sLg$a>fBz>;Iu-r@`%jn@DN*?U_@6N89>e8o@$c3fw!(Yk{b4)2KRyU{!Uy5QU{`z?J`(oCN8)2)UwkY+5q^hH#HYd`_*8rb9FEVx=fF|;9DF_;htJ0s!%6sJJQ7aBBk|>MCcYexhCkrZ_&T@{Ux#mkOYlwjHn<GmhVOza@m=^{xCY;gAAlS11NdRM1wV`*hdc1&_$l}!ehNPa_v7dAOYjhW3BLx9;n(n6@Fac<zYEXecku`CBK`n>0<Yjt@aOOb{v3Y=Z{x4<H}F3G27eD9;qUPe@K^i;9xJBe3*6Zpj|cz2oz3x&;5*#e98U`W!kx|Wl+YDZxwAQ*7RJWY;u&CkJOiEuCc?Ae*<dm}8=ecM#&h9$VLCi7UJz!&3*tp!R=fya0_MO=;H6<6yfj`O=Euw96=5N~B3>01!>i&oU@5!?UI&)L>)>C*3i#LfH?Ru+4c-)1$D86UVQsu6-Ufb!x4}EW26zYjTi6)?7Vi$5<K6Mzuod1L?+@GI{qaGt6FvwZ2D{?J@R6`5J`x`b``}~oiEscu5uXYN<5Te&(2LK&=fF|;9DF_;htJ0s!^!w!JQ7aFBk|>M7QP&hhI8>~d>vefufsRNCHN+M8(fBO!*{`z_%3`eT!Zh$55SH10sJuBiXX<0!=3nX{1n`SpTf_<{rEZj5<G-o!mq)j_%-|%{29N6--T!JyZ8fm0e^r$fmiS+_;Yvze~!O`xA9l_8+adogTIH5@b~x!_!R$u$BL!+8}4k5$AiD)&gS?>@Gb6ajwgkG;m+oGO6ZEE+}RvY3*+Ev@eD8lo&nDc6XTijtS~vA70(V+<Js|CFdd!?{}g7#KgILIEO>tWGx!Pq8D0eD#Eam?VII6V{yEHte~y=d1@SU?c~}@Pk5_=j@CtZkSQ4*{SA(VTYIqG;4zGdNhF{>d@vmSd{42aZtcusizk${9Z}29t7TyGJ4(sC0@i15q55wEQ26!91J#2)x$2-BMcqhCIY=L*dyTev^cf1#Di}%9&!VY*}d;si>55Nb(uJ|B)DC~g`#fQV*_;7p_?1zuS$HMRMvG@cy7@vSohF*L!J`Ik<r{Oc;7<>jk8;-|k<8$F8d@jBKPQ@4Ci{bb9Vmt!Q!Xxly@CSSuz5>q2SK!fb5gv`Ng-h_Y_y)KX-+*t1%kj<lHn<AkhVO){@tydOa2@_5?t>d~AASIC!4Kev;CB2FeiZJ)kK!lb9{dD;3hu*C;b-AN{49O}9>y==m*Fw|GJXyIj9<fV!qfOo{5Cv?-^TC3i}*eK0lbPoz#qdK_+$K6=*NG>e}i}N-|$!P7yK3e8a~2b<L}^8{2l%me2)Kxe}FIX4|vSjihtnF=6D?V7I!ws<HPs3vpN0|{0Db7$CJPqv6VZU<H=!cJUN~U#>G?NX<-69EuJ1G!qej!VNyIJo*AaVGvjWU8h7KLz>o1y@a!-Ho*mB#GvPV$Trdls3(pO+;<@oWFdLo+|CG(~9RF_VU>cYWPlKm~S@D#3GMEKVh9`!Z@WgmRm;q0S$Acf^@$gtMH69Ch!4$X)|2vjqQry`b{}U#{oz3w#Fahptj{gqh;?Cyy3m6-BHpidA82B^B>J#XU-6w30KZNh`hxmQ?7Qc_*fq&q4@LTXDeha@2pX1l@EAT0P1-}Fz;g|69@E80%eg@vf&)_GaA3up7hd1!!_z`#&KZ5@RFXBJp`{6l!KfV{9#`og8;m`PPd<Q&+@4&ah!}wNw6Fi7-!q>xn_<DQ|+=H*dSHfNRN<0c~$D{B_xCM{I!{J6e9A606;S2G3a5X*;p95FnbMTpPIX)Ag4wvH7@hNZ#J_Vl$7vU4}ad1994j&DFz(?aF;4FLuJ`8@355tGRsrV3lAe@8`#QVeXcz?VP9E114d%}@;PrMuS;@$9X;b8n*yd(S$?})d9{qS~pYuFoajkkn7@RoQp*cESvH-??@#&|>60dI(Z4cp>h<8@#wybfLyw!mxRU&5yNmv|M}2(N-ygbnbDxChq5J$PAI7cYyKg0=8ccnMe?FM$_@Rq>*DAy^47gcpEc;05r!upFKj&kalCx$zvZB%TA$28-d@a5pTByYWo0Af5?N5A)&a@iZ_Go(4|=bK)uRB=8eF37!yU!4u+fVMaVI9uua+W8(kBR7{OKo8y1N<hZjr{s&BqJDcM#U;^CP9RC%@!JW<VhtP#TWbWu5bmo%ou{rLCZ*f0<9sZ7A$1lU*@XPpl_!K{npN5a{)A$K^A3uQ~fw%D^_(6CBKZyI_72JpKh8OVN_zrjm-+^y|KjT~Q4e%(w0bdIb;cM|#a6i5ZkAi#fC_Do0#3S%Ua4WtDp9eSM^YGbl4L%$H9<Ic{$EUz$_!N8sT!K%)$H0a77<>eri;uvEz*+bZ{5v=u{|@g9C*ytb9&jAq1MdPy;a%{K(2IA(+rq(kTRaR7z{Bunun*o0Zv=bdjqv)gD_$S33p?R;@tUw5UK6hdTjAC4O0YRz3I75%#=pSJ!UlL*{B!sf{yAP8*2atDg<*BPFkS#w!3*G@!V37OcurUj&xwBmOW~j3nPD+JGoBt6!qekvV17Ieo&x5<Q{YKp4m=5-5N5>_;&EUmJPsZMro&_4f5%WvjXRs;Z(%ar*&P2JCc>S~@!w#4+}Rv|3S;BW=J-SC!XNUx<9pEgUGhCP$Nlgf?#HjgKk)1LW%vTWjGu?U;^*<x@DY9*KLPLKC-9^2HhvWU3Esee!uP=|_&$6Oyom3?cfzyyPJAmoiEqU>!ejVGd@VeLuf<ov{rD<83jT;k;Sq2L9)T}{Tku8rJh%a$htGy<@Y(qHa3%gdJ{c~<C*$Mc5_~*98ZN{~<6ig!?!^bgnfPFQ0Gx&o!27^Scptn69EbP7yTDO+7rY}Jj(5b{!XbEDJPdw^hvCg&U%VOK2=>Gq;q_rxygvRF?1X=X*MjZvTKJc+75*h&1-8Je;1ysKyaHYhHpI)}rC>e06kZ(G#*5>HVRgJPUI13c3*eu^FYr(CoUkmO6aNH$j(>t@hQ;vAczRd}PmiaD`SH|va+n8CjwgmW@Wgn0=*HvYv0+9$HtvES<1YL!mtrd1*&Kfhli|+h`0p?g?re_#1{2`U=J-<>2X{8dAHo>8vpIeb{_RrkY>xZkJKT?7hkxML@hk8Jeg(e(f5k80XW%3J41N;+f}g~X!8`ad{1Ci}AHw&;tN4C=54?!)!FR&5_)dH){2AYhZ-htjjrdyl6TTK-1^3~r@F@5r9)(B19e4!35N^R2;&b5!d@eo<uEA&F)8Gnx8a@dw#V6t8U^qSw9|afSqi`?$0r%pA;Y@rmJ^)U~2jG3+WV{dF1CGag;9cNoybInD4#zv<ZQ&5SE#3-#hquC;!@hWPyfN&FH^v*nZg@ky9_)<Q!)wF#cx}8oY>ijPtH2g`6}$p$f>*%H!3KCaycGNjFNGI}weaG2VfZCp7%u=T;|1_f;TQO)cn(+=&w*!!pW|8aOt2W93I7;=hJTEwg8A@NcygE<PmU*n+3_TJBIw2w;R#_zJRu$*ro-doabapaE*=M_z~kVtVN#d*bx^=#!NhnhJSO}IkBP^C30&rO6mb2=@pv#L9uH6U@0JFphbi&&cxIRu&y0TpGvJ@#Ibjw&C!Pmp!}H+zVJ<vBUI^yJ3*kj!LA)ql5*EQr;$>h7ybSJvrEw2l36{qz;niS8yc%8;R>f=Lbzu#>E?ytj!RzCV;MaH~yczrkZ-$4#rg#|M4z|SG;hkU`yc6CPcEG#hz2LWaFT5Y@j`za{!ru5md?@UX55-5oLHG!K3>=1!!6(3x_yl|k9E(rEzlRg?@A27iDn1*Z2WQ~(@I`PAz6f6e=i^K8WpFXR3||Q&@s;>$xEx=NuZPk2dVDinhi}HW!%g^hd^g;N@5X&_7w*Fk!oB!G{0KaNAHh$+!}tmOG(3)<#?Ql3_<8&?JcnP#Z@^3V4g5B|hTq2T!&~@${4u<XKgOTI2lzAmC47Rv#9zbb_-p)6_zM3M{|COo|G{I%P<)R&o8xie2i(~lPY7ehQ0{DwCxP+sBzOw=5uO511C!!u@N_UGo(|6h)8d)%tS|$f70(W{;MwuqFdLp5&j)ki`S8zRUi>q>C@hE<#Y@5>cuBkrEP<E7J+L(H!7IV?cqP0VtcX{`Yr?8{O}s9wf!D<wz&dyXyfOS5Z;UsG-{8&h*03qw8gCC<;_dOyunpcB?*=>I-SA%UTf7(E4|d1<;R9iBd>}p)_Q!|fBj6x>1U?21!^hwg;7EJ|J_U}&r{L4!M0`3v3r@vn;d9{(d@jBK&cPSp;cz}4jxU9a@um0*7>TdISHtD_YJ5G6#@FMU;W~UXz8!ADx8u9vHheekgS&7aeh}`(58_AQ0sIL5Gdzs{jGuwW@iX`ZcnZIOUxnxJtN2ZL3BQTof!FXm_%HAl{tNyX-o+o|&)@_68U7MJ!C&I9;dA^o{wI8e|B3$t-{Ak?F=Hye$DPgbxbOq+Y>p>@&huso*c?v`<Kc<%<nSXrIi3n8#Z%!Q!<6{Pct)5O&xpHW2HcHjhgtCKcy5>t&yDAUx$u1WXD~1R8D10?#Ear3VG+C}UIv!H%itbZ8u#FpVR^hV{w1u4e~H(ERq<MQJy-*;hc|?E@P>F3_%+@HZvnr-Ti~r>Q@l0a9=62W<DFp}yffYncEG#gz2LWaFT5Y@j`za{!ru5md?@UX55<SWLHKZdG#rMH#>c~v_;`F09E(rFr@@K%G<+tUiqFJ<fHUwP@C9%Vz5ox0^YL(eDO`*%#aF;cd<DK5F2`5n>tQs$9^VYt;hXX8a1*{A{}FD(f5i8}UHCryC%6~?2|or8;K%Tj@GyQ7KMRlJXYq^h6n+uE3eVwJ@tg1xeiOd~ui<y_U*IkL7yL22i$BJn!3X#={3U#Xzr<g|=lE;<9ejnq!~ceF@W1gGu@v9q&gOV*_yKn|$Kylid9(Ozjwgcg@I-hr_z|8APX&|Wsql|sO1y537%@}D`kyaDczY}7v~g`+E@w;R`kz0}@BjY&6lmA0Pba<|LH<AOuTcp8e;)exSmsL=>eh(k%$d1j{`)^?V)cykZ_cj&2l9|7t^'

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
