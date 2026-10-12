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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ab9804f981184f8db6f1f814c2b8c169/part_004.stl', 'relative_path': 'ab9804f981184f8db6f1f814c2b8c169/part_004.stl', 'source_sha256': '30218d61421e3e0186fa77cc2d2e7b408e3cfb681a0ee6db15f73620cc14ecf6', 'input_faces': 956, 'input_vertices': 544, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.1081305742263794, -1.2983298301696777, -1.090911865234375], [-0.5407363176345825, -0.6614789962768555, -0.5761970281600952]]}
GEOMETRY_BASE85 = 'c$}r32T&AQ`0aZzV?e}!Vi*-g5EFtqj9|o^0|pQ=D=3)Lm{2ii#e_Lxju;qSvtq!UQGzHS#?^Jz{qyxX4KuIat9td`R(*ATeYn$o``+)~z8$RX&^lZ8!V3N?t2oX+HP={EQ6%yyg_W@ZqeF)H2Lx9g88kts6jXirPt)b?y0-1mQ>TnoCOHiV2=*WCR8Q~JU|=05SH07~z|kS2{YLf+96caF{N{ecg99@B;K6=D0U6tsJlx$~^);Pc^;7i!kN;U`R6+kX>Ql5-Y0P?6P0iZ87xmq}Q{7fRpHS7{J2yo%?q(Ru_x6KduFpHsi2ak`cesfCOuU$?{{CS@>?i0d%HPlZLET>M0Y9f5es}m@vbx>)^G9{N;1%qrO51eRFZURJ%so{V#a}IN7`hz3?HRRv+{K3KwxR6=l<T$t+Y5faRkyzy;1}7LrvC2F2z5WE!u8+}y{DeP@vo-X|M4pD@9)C?LoTY@rd7^3?k3+a>fcAbM)^9WP~O^F^$pf}ab7)(qI_vj=;IZr&$ApT-)k}U)BZoTJ$)Ur!C$pTt*6Pqz3Q93|3-UMzM<Ar*;QHfjg2nCf3)$lx?OC8x_{G*2-P>9*n#?_xTyVT%Dx2UyD!21=hjsBXP6y^@-xceJo753f6mz`pLzl1+7waM6gmxlon~mqRa?~K8gfm<e!kB~Kjv(J{%>bM`Go3fJxyhsspXA#9Z~+lF}0rhT)ox&F~t@~`Nv_XXJj$8{>ILQ;ro~VXx{$H{Q~eKqtK5Z|Dc{lbns6$M!EV6P~Xx=)qFHoeTe!E`<A5o5nGX`YiFp(jfnkMJ+AUP0_D9*Ag>-?P}^VGvIga=9#fAOw;~z!+`90C`FX|ptyK4C7%&^<C)7rLHjT%A5~soc(*@(hHw5b19R7yB7%!hsCZXQd;TNBx?pJ@}joNO811>o3%wni#{cXsXpmHd`|A4x!uN#YY9-R;V&l+eKs{r)#$rown`D2=L8T<Y5RP~h^6)?`5l}y6#Z^PeF80Q(?7XIXD`2H?v=k3nu_g|;rhmS-5uDb?pa033}zUYryD^)d2ISPM(oqApo5wp?GXAi;mt&Dyu5Syr$Z?q5fzif@;#`pMS?km<hocH6&YI)<--SE@*p}jVoLw%-UzEJedu^r)t^5-#rlzP?Fb~9G&g7KwW1iw`t?Ekkf&ZFrV`blazgTrLZ1G)Oc|GEbK@%Bf8`uE)3;Sc#6{knDm%6qqh?^q7w%R4vbpD@%<DKQ#qID-DV?uB;9UI_Egr6Jf~>qaQ|?lJnid_9cce6`?z_CdX$%tL>*sR=)DC(1Y3rS9JlQw4s51{iO}1J(91wXFpI**rCWe4oEm$D!$VG5DvQ)q4Ae8F1c9Y~VNYL%TT^Q}?6X%?JNl3i@~dMYVm5u{!wPf6~nBX<G3Cd3o@@x*t<$fg}sxkPZD+@C@?gVO%Q4({;2@vMcgr^<$J@xfT0Av{gN>Vt)_ivzNyBJoqlz+*f=8F>g4Ar(5^~tdXxHuAqN=+`)dD+Nj6%ecv|C+*fWzBcG03MgJDR3V-fH%oo)jVO%_ohQIFx_Q&g~vBX)n1IE8GacR1RUvM1q>EkVoQ=cgKM>=D_zsKXaFE_&fw<6ASe>LP&#C-VgKSIX`s^?{jo11E$C(6VXm{-aN!M~Y?^E`GI`x`I<{()D>r~aPk$Am%fjlGdS(}rU{3+NBO`cvfhs2w=&_I~gai(_2ek3l;n;d)|p&Hh#O&(}^e_m$cC(Ec`VA1wTJ!*QMoO^_E(?Xe%9S(p#Q(h|*m#b=J%z6QG;@ROUvpI#mMry=skxhb|kZpL_VY>eyJ`}**2ugCSC^FXHW-VXDA+)(xJ2A8_<@A+fgt~iNy8&(<qW<T|OmDF_nE|v3j14p&pBkq>Q_;4)`zvDLK+k!$E-y`(!t6jkOyio#q6j=&>IeW}w|GA<4(@Mavob8MG_|kmiv4v>I0zc7@Rqatee_WdRevH-f!(X@u=b3}oNw@D9|39az>j%UA4QS`lU*SI+qVC7H=t;Eamk;pc@^hWUysnvwad@c+^5maG=!f8UC|@Bj>gQe*{rNQ>{-;&%E%ra=CH$aAXvfJ@F<y>6gP&xJ{0aR#Ufr(s5dP?;XvadYaeia(!N2tg^GpFNjGL2};P3f`>wfncINv%Z)c^ESwSNt5Kfg8im7^^&-~H7a`<ZYSezQl&6Xz7nKc}MLhcCvwP~{EAMZIJ2yLLuCjo*axns}J)<A(B6>!81)4#1yWRxKBIv>@jB$?H*1?_5}ajy;8SWy2LH?^y|XmFJn-K1Rb-_#Izi|1X;*TKISTkWZ_p;ks~sJoX<@SZ$w((yLM|{7ZS%<LP_;OgHxxw|&URZ39qFHx_=EMXKtPx?y`p5Oh}(#zVeKsON<d_}w|)PjtBf^%@M{?HH~LbF-m6v-@H{kFkzdPK-nQ=jaOmk|X9F@5k{Le!qXwkG6+!zM<{m+k|63rRG6fw1DsU9`pYFV{a{d4=;5;`kn1CUgtE0zh*!3C-T2!3xCv2<nzi)$j_Dy;Qw~O{vZE`agoOzeupc_Tc=hy|5i2NcWa4!>l2Fk%)27|F_X}q+Wko0(j31FkT<!IN5%!1Uz9B#7)Kp8tL<Z2m>+&(ezbezK;%`s9PoG8V!U`wL_gpD596TyAhctHA!t{d-x!ChHsii&+<weYOTMFgnIXtSFB{BncfO+hmwo8p$hVkR3%y18z{RL{`-?cv^4IVe;=avPF9gT6dk+6XIm~kpCdOO%(OAzJH%!7jwBjNBZ_Ut;-d-3t_i?|fts5iG?uEaS_lHF%aem%_<E%EpA9M=!4%vnI@X=ZLV@=41`K8c5Yj8iKtq+Y412K<1<#qkYIppnud?^-w_lC$n&k>kc!#BZiI2?J^aTUgqLpb(ZQ9(cMNyNBVzXIi(7eqe}?we-e+b%{vxj)12pJP5%Vvl1zXheG$`YeDy@Hws@DTR>FrDwq}*bnndzaE%B`%Z@+g6AKGLf0()b+eEUoBQMV{l>E0f^a`Idw8maKkF6pe|kC0lW{1g__$--UQI@O`VC|GYPhaFTZDcu-vj>fhH5`WjBrCc3~X%CZl(u&-kST$=V0WIV>R@{+q&?355PF>*#+%C$eqs-_F|rTv<c;hIKzK<{;T=8&h)>}z_?oV4fWYw5q?quTu);fV;wiNG<<sxb-&uYYTV;s(Vm9ZG4U4unxU8%dc48@Q}g3|yKKd{s~w5;<nY`mzqBXT@iSXs9*fMu@p4eDN8IJUsBhqBtOE{SLOuVCLi-&^=lwV46T`e87{4D=;dA}3fBZJh!k^L+<7#7d^y8rf_&Yyg{A{X#^ZJDAyiyX+OSJVyrr&V^v>oPyO#k(JjL#3}6D<6{>meTsI$`|PybpiJlVtO8X9&IvKX@eCMPCQ)<bDl);2ZSQy5^XFLN3D}hx>ouetXgW$4{c&Li6J}m|Iy~Pk&&2rVQDNdPXfp-qqaz-(wT{tM}4(7QS|U{~m&QbpozuT0R@9rK5lAEkpUW$Ybq3(J*N-`(-ec^QZAN+p)(XHE%QLf6Zq*XwQE#{kz>T4-Bk}aXn=M{CY#x-}?qO#`#Vg3BPYQ^}O`)ZE(Ga9tOWw9rVi)2b`bLAAX5mT=zL+Kf1nbXFN}eczF<cHM8wI^KqnIXHD5!!ndD`a))YQKTVs#Uxw!>#%=$+QQK#hC;SZ)Fuv~Q#JqH|G1_@sLCm)U%VNCeXo&KI_gkztjLoZA<fmzuPnw0#=S9XYMyy+|I9vAn^fAc8xn=45pu9&!l7+vA+gv9Yua<_-dE58tDO|@|6^HNrFWN_`gmE#iDEviu?qED?Kwe$5gWstm){U(yqdqrs!#~*{^Y*0YA1wU3<#3&ykM*OebvF1-f1-YUY9ilm{zg94Hllq8CcUxnpSYrZ1D!CA+WvqaR{`@|@&lA#_zk|cPT=!crNBqDm&0=0$8Fw#{=fYee(VvnL)B=sgH0m#v*<JWJ$wk-;||)<SUeQZU1#RQePzc-D1T%a<_BBOYlUvZuXGI>cm~(yPB*dL@(He^FRNhQ>v|mff3N}b!}gx&ua!qo-oF{f!{Xg2|7bh>pR>^J$8(^*#kMA!=YzIBF?NrDzuOM?mAs$I^j~&PGaoORe#|)ZJD=AX9*4tU)(-P~l~TAK*{^}WaU|ORtv}ki=gMUB@nX>RKs&8nW>HVW`O%oqeWt;`gZWN>qbttu`2_4|`CeRimPeppN{-|Efp9$kZ~jlbg@3#&j(5Wfzkk8`tKuu%XB|sRweSmf!#W^$656@%5cp98)N=akw#es~cz>ewa8t|2EzgVV$mR|>P7_}>-y%$r7QPb0`zZbV6brw20Jc-C(N0^MS>%I~7tb$D1Ki+y+hKk_Uj})&9nVjd+v#Zkle5sSiLUSm-DN*uelu2Zfq!@`t`o@y9Dkq_^Pls;#j@DX4m|HrnwP=(yr_fraVi7fu9aFoqC-Bk=g#76e_luXN2Xi&se6*m_pc-uh0ptX)6h$(=U`j-?>AViuZ+%l;B%d+ov&#~PWbnhWBjB<zp?Onoz?DJO)h^hzuY{G_i!~_QP1HY;qy7UY3(-5-}}<wKk9|;Q+}8?swBfN+Zp5Vz$y3#@Vr1-+Yj||xr+Lv-+yb~zlNZa7%$ahQU30EY)6<-pP<|D`5eg@uZy?vwd+EE*6ZL+_&c%A(4I3ZpRgWR#`i+M_?E(Tr^Xfdo%>>)$@yG4d>-{&_!INSyCCfE^Es3+?gDjvfa`_Z8Egk&evPv&iTwnh!hZCFkhgq(tGFLRdEQr=cG_Y5dF+7CdDvJhIn~1N+*~amSMv|nkK@*0|3|lBK7TP7`>8t{<!#b1E|&d;aua5}wa6<zUp4&X`-Grb*q*)+?Oksoe)l36?Vvpermr~fK>p3?hH+Xy5dLt?(<Yw@sL$l#@IUWIy-VN4ex~?g|9p>ZeDE9nAC2cnidPQ4k6W(hk78^M-x2RcmCs+$pVJNS)6&)Jl-`N=2cC7{^ZAc5KL^IcUzoqN>!T@l7v}kF)lvS9H`<NQX)}E*FZ64)M}mdld2Nb$-e&r1I^nv1_Xzsgs|x&o8X#}E9?0~Ud#UC0#Xh1PW--qu<323&`m6c8-`9`(jqAllC-@<lr;VqMzPIpuQTd+Bn7snFS4Lny@$^RfG%H7cu*LkKT(O1UAO!0HXI%G;E%Ko~!%{Ji$HrqlFgFj%bN)09@0xDm2Z!Rl=hjVVH}AiZm)d=Swyq2Nl4PDInd`2+A5dOff4a2Bed_#V_|K=~cpdSa%+w|h{(>|<hv|g+$2?6kA1{W~TsZEcSop5H(9RBgPiYeaKP3@)-!dNkxcCbEG(PvNd5hQei|~8k`Jc%>2<z>F7vQflB7gGU!G1bK!|%`={j~op_IDT0UzCR~s_%RH3EE-Vp(Klb98?wStj@dP^Ld?V492~o@Mg3p-}7qY*Vttv+aK=@eTVs?{kkoOug!aW?_*p&8~#>LjF$mew`Tf1y^#k)75wh;4EXQUaQ`zl2Ki}kgwN}8gl%@zr^gideBY-%4>7Ho2!BRH^ef*R8o~qNzr*@3<Ax0T_ZfukNlmdne(r<uxV|TRfAoLEqT0O9cY{9y^)+26jN|s{2)`|#uQPv?e$C<Yeo)JQ(<=jf?Y<_)hS#6^@Y~@2*t9za*T)Fl2P(75qaS|^NwDyz48i%<!~3pG|6u^ujScYLQhDtGpX(xH)9#o*%2k5T_j(aQ?#TD8xNlJ+w_x7p`x?cu6!*{PIo-q2k2~_gADV*vFINtES}_;=6<FsP{L5h89h4nD?`yQ@V<x9x_`BUrwI162tikyc{9G5Y&deT$_jN8w@cG_6^SGK{3F9EH|7eV}q4DrPOh&#YWkdh$jf20o1;&Z?{73VXZ(!WI8gPG*@&bMW?&mYV|4GF>s=UGTHDlfPsON|n)Jt2(@;YUTypHl-9_YU>kx3T5Z5QO_w^+3Qhb!<e>T!K6h5HZF$P0-U`TT85l7(Le_qF;fW04Ov4)A=r9@}>U*VB+y@Hy}Kt~-SLnz2Usd-1$1F2T>z=W{tzhzad<VhYap+a){)*5*C>N?m-<l35?kpYspin?xmG9{WBKe%naQzr61=oE#0m-4<Mr`25QF1LIx^9Ebd}{(}Ck*B^e!I?OZG6Ot`_eg_qiZ6*343iGVug7^G}(<3oY{)^{>nd_6)u_@-h_TEQ(FJP?S9e$KM@*{g0^vfjlt8rUNtb46EKF{F!f>Ht34SjRmZ)N)0^M{^zpRY7(0{=-<i}yIj#<k#c9yUHYfxmm|;h%1TJXxH8e!Eb@A`g}P-!N}CwT55#Jm!TO_#P+I-`EY~v)LT<SLiRSNBsEwqsbD?+n4`=zZ&0#WY#Cwclha}aQ-7-p?$7=fUn&T7M_W9e#>_W=Htlp>j>tXxk>QH9mDgDMY-Oa`<eN}_xpyhXDHugHLiDjzi+aBi1M+maUZ9>2e}agzZBLf+PXr?cLRRidg$LI2Y%mj75<40Xcs$M<masu@HtOrzGp9REWtc~wCC`q+xy`2{ieRvK=e<+J@6w6qTa>v9hITOPJUOy=YQX?pr7w<hTj6ul?{m#urBJj9zNgaYWp!2S^=NWTMX%WQY`$We{kL6cbLX|^WpP;!BnCR#%Y&O_`e!q-M(9o;}@CA^20Gsmfpg3;NckfT(=muEK9TSi*mjH?+)y*XfXQmybH#4>=GPz^@s%Xd^S{Ufc}3p6#kPz$Sb}-H9hVJpZCAocNeC$-Le1hHMrjGu9IT!D-S#p&Fg7=)(ZZ3Pt14M^P@c+TEKrAg70~j6~#OgSBmG0b#+`J%zp+ydmK0H2j&_3MD)w%A}C)Z6!qu#LYaPz$v7_WN0c{(pj?+~?`M^**6<7bz&h=!y`|6h^4k1kET04ZLC$O6qWHay73!(0g!boictgN<JQv}8v|-Z{e#h`B-Xb5k4lz_r$M}9aMZJ&k4Zn}`-SH0PzlS5w`2No5ln`&;kD1?z4SEf~kF&*dX2Y(R@ayBd9$%lE*iSOQ7vTMP=DL@@62R}v)`lcn_<2ubd}-I&Jy+rD?D$?+Nwe_BwMBc4u)^<B@cv)PRtI@-ZZ5{@zO(Re=+yh`h*JEnQS&#|#P`$NCgZ%SZGo>nzvBAGRDCskhdKCO;&nLoGin8Vem`c~{sHUEPmADtR>1vQNnFn|{dq^Q?&A9|#ccuWnIG+z;+baQ^F4y*8%EEA&-eS<bDK=R#sK71&z%^jheP3W9ip{crmx-4YR^MzPKTfR6!UdXtb;OrJ~z;=U&_%*@U{D_uu5qETEpOT9c3tszZ;JSz~}o!!{mWj57hRB@BJ70b<Jwb|Ks|=uZZsuGs~Z95C2;q)PKn*<mt~Q@S|`YHQ6u2ekL`5&+j^nMezNQsi8CXGsg0LvF2;<r>^8he*V$JuV97xhdsc3Wwbrp6W`@&?U^yr!nfu3w%YsU^ZA)?{GRsr5?p7S<c5Fu3HobU66VnhR`5q&M?Y~MF#h!&>&<oe&Q)o62*=I-4L-j&h$}yo-?gN^v1tD?KDZ8qCcvL}1IL>*5AB-s75rU%E*8-h*SF@+;oIT8oc?O(R15zTzq=a4?^v&!;MX6A>j=MNH03=4|Lb71bLAgskDGho^ZKa0?=UUg0-w*HO(jn7JFQLd`MrU0-)+pFw^zXDce92!<8a>hf-T$OLVFy)%SiZF?_r#j2}XN#^@p$Bmu16s$z<OQKEIFEo|h^m>cKyU_gmU`KAFDzK(x>8*J#g;cJM>-zDN5`%+xP0e7>*Dy#D&Xe~t0{0Qu%r1HVhU1)ultN^U;i+Iji4#dr_KeVEDlIQ(ASQNO)akXOTY!SCJ1Vq6;n=fLOlMw4}U%+obO;A`JkYu}$7>j8hva+K%47cd-e``Uc`Dm^mR3mq)}^-k34@<lsT$(ZRfB9Bs78R%#BPj|$W|1|yI|I?iz?*CW+bf>OIt^ePDx|2tzC|@$_u}Oi>A#Wl#q1GUa+LN1*%P@osQS*`uk!`8gWYMBzTXHFea6^W0HHNSg)rKsZhwMbwQ*)8^<Pr>FJ8BNHs1@0cT!5;O3y||O<iCPc9a%IRxgfbPH9NU5*?}SKNX<zW%}sVByHfL!UCB+U#mP;{y&1x@s1?bg?&MkI2x@C`1o<>W_&PO^EV__<o&1Knf&7M?#1MW&ok#wQI+i+*JeJ&!>PPNE4WRmwMT5zr<H({r$N}Wl4B>d{-{g35I~_DY2Nu0f7Cl04N8ZK|{*PL~3M^WNEFqjmElw6KOqLM7PqijX2w%`4gd?f{>cFCjWYKlxNOGNwIHo{LGlb_**OBLt?@$xTqIs>rcgVkV2;o1}{A3B?2h?O8Sab{d0eLY)xB|64xdQpPf)Kt!?M#*sexe|RKTrpfMaPjPgtO6GK+Z-k&JeCb-9#2WK(0deqW(qpBKKkl_o3b*i#{gzA$O(5le?0eGlUyclgOg)$&JbG)E8uTa#89va#8Xx1tI*BdXOx-iYy^~o;r;zA-q>X2(P3LB8#>pO9)S))+S2`4^a@p{ir3#q6Ntk!u_ea$P&UM6@>6;>VFDY^fP%hc{24kc`|tsLwF0-Mh8AluL8Gi%<|TTc`Z7@EYF1>P%n{1Q*~M6LRcF|!oR3*by?$1_zu-X77fv5jZ<N5Tnm?`=Fw%%1Hv*lh{`%ZShNZG7`YomxB|5dxdOQuwGdg<mRyWngdtpxT8dnb+?Lvqe4M(4+K?<-jl6}ti0Wk4cTQ$~>cl=5)ssa_nB_wW=8mYHl9fw#N>+~9F$YBpkVW$=S^1ftxhz^x$;xeEE$4+-QVWws9h9u`BD|OCsAP>bVQmZwzofd7MVl&F<5&0>wYQQr_Jw6W5S^uD%@68Yfpds(V`>Ch^t6&S{|GmyURSc_E@5p>6YfKOLl#X^vgSkKUerfQ)?6yA&9TB&bXn^OVbMcM*8D77oVroTn%jl7IbZk#|2~&2I!4L5UI;&-_Eoa3HNtZJIZka$?Mp7LAn!|3i;zo_ovG!><@h^iYF~0+9^08A>_(kSb|W{YZX`D*cVGznQV)?2u?>BxW67fJ$iC!83}H_tYklU)5S~d5Ad9Xh&m_lE<H@43u8QTha6KJ#8@V2N5%oW^Xc}4cK6w#&EJJtz^#WNml01Oif?9{%f*hwHgs&=D>#C~^;X%}H<U!=h)C%MZ%!$g>(&WnI@(kg!)RN?q%!9I2H?kZ1yDUSv614-l61h6nm+Z@at<DgxMfD`tA`hj`B+q1@4P^+QVF>HluhM^d_TwV5o@`AWOSUF|RiFdN1K1zJE!Zbt8NySkSIJk|2UDq)$y3R7sO8CZ$S%~f<g#o#7ix8Kb+(HOL%2J2D7ia%C-n^Z4BKWW)tYS0^V`V~UO}BoUO{d~twXNEdNiYUCwJ$*ghyxWzkNnbm-$cTah*KVhfXK^QvIpZ$<z5;e}=FdL)e8nn(RVu!w??M5MDx^PM*$sEMW+rq;4dOo*;|fC7&eUW(a>~2!CV<zhMYprk)^QChuYhFQjfHZ)CeHWC#Z_guTt$(VHP$h9O*y>QAmlcBQ(JUCBQcgs>Go7xD`Qs^hi`*@f+{qn0D<$oDgTcP=BgW<)ymK3P=Cq;p%?mLc4P+J@YQ{n~^fJeMK7le&bwgnhP?A$*>Cn|z-9i29lQh@8y|A*`c*B!6Td3rh(9!w|m55I)Bc-a)-g-a!td?jnbghfx=j7cviqF@#$&gez0M$==L~$_(M`4B-a~LO5AL2>+l~BUfXt2)i<0elUb@Q6)caDOq_VypI}1eL)tLT#2IIr+=Th62%Z+oDl=5A=Itpt<19!hVXKR@KJ{FD{4AfRC4YWw}lmkaCL^TAGHa&3G>g7Av~2Kyq&s}ypuV%ogsXh`iOj*{Dms{_l4WSKXnLUE9R$;Y(@U9LkOo(B`;GL!cVC8$j7O>srShDn7g|f!pj-Llc_t%lgWLlVdOC8YhQ+N1BS2zwH4Wc{6~RSCRb+e3QGt-RS?3LsFKr{7{Uh_!qL=Zax(KcnjsuRy+w{8Z#T>7?F``s)F^Tkb98}O?k->mk6;M5X9#;yL&#p_P7L8u)aB$+<Ym;O<ipf^)T891%=LRz$@P2O7B0mQ?ntdpuFhQVNS#XVNM1qRPTtO(UcnHKp?)EMVNS;|gyR^(2~^4N1nO`43C#894B?y96mkl4`leZ~-((1{W(d!u?k4YMuFqr$4`v8AqfRDIW_~wg2s<-`^HCd+^O4^xPzSPv@C~Zu`VHp%Q}PY+LFy&)LGotm0rF<@5{B@4YBV{TxxSvdojid$o4TF6ojE<5Av}OOf;@uxJ%AzHf+1X!>P7ZquGeG;8yLbpsiVlFnBP4a!V?+7;b!9@oFROYA$*5=k9>#xi7Mma6Ssv6F@zgYJCYlbM^aaiN0R3;g!fWo$a~3WsBz>o<Y;OFIe~c}%@97t5Z*(*NxsQk-@_1|&k&wSok^ZZ?#&RcOC3xe%v`U_5H7|L{#SuIlO=?oQS*@{gwIlC44mayxIsQk-o_9Pr5+@Ql4npilQ%Q(XE22OFoc7s>&aT)2Qh?uP-l~8GpBnngzHmVkn5AHP-~KFGN-FBgzGVcJ5qa+JCcV{Cz6Me=TpPU;mq&(4B_1j;mZu+hYaCV>K*bO=6xzv@?N+AwH8(US`6WS)JEh+90UER^T_?k;ncn4z0CV?YBV{Vyn%X(yn(!ix`(`n`MriAJcK%tJcQhx+MC>+T!UJdT!WmKA^c8(79&dt-=<35-)0D(pgto%V}74t2(M!Z8>!pKMzTLOlpM<Z_NVqC`;(h9gxgSq$U)5GHq`p$HsspWD&*Sastn-<)OzFw<j&NN<j&;b)M4ad%-7)z;V_2qF6wUbF7gHHW%6rk0`)TaGIKqFA^eS+O4joG8@Gik>7cd9mB?MF{m5O&lc?e3N#rTi4df~0G1N8WHO$K~4B^%cVNZr|Rcd!~RdNn$4RQ{0q5{oJmJq&1mE66?5RRnYCf{a`Mlys~F@(oc*OAAQeW*sVk$LIE5N<_nPHsi^ptd2mVg7kgtCBs)b*T-=b;&Im!o8@S$(@;Vy%@ri7{Y6)VdORBBh+2wUCg;74B?v$;kRZv`j#P_TZa%XtV0OfQxnJu%u8W==4n}~<Yifga1Ux1au?=e59$>16y{kEYHM;?sy($exi#}otAnR5tInQ04^QS|ZfXu));S8xdFNmbYVD9{)>esZzeMKZ5o)Aa+eVu8MI`$wlDVk$-75CyD&}G@s*hP;`<Ug15A(%``B#_fLEfBE=VKW$lp#EWdV@TJypkcjk0Jb;A)LbsA^eRY{EB*vEV`NeihPwJJexX{EZT`2NcEt0BBv<OoZRk2?!@2cWC%Mlgd0+4kZ15b8#07@QumR2l1DLwLo?!NMr_T9htyE=L-IxHKJrEKcj{~McXB~1sI;lDZAKK!2peiqa#8->hMI#cDt%zXZQ<-z2;r~nqgUit?1Qfi;inAYL)6*iL*%t)eIwj7BgSV$Tk2Z!T9#=`^&qz;+cAXiDp~z{mm$2AA-snw{kn(S!X^bF{Fv%Uc4WT_O9+2d5W@NS_nzdQ?Bo0lVJB)R*@<jm2>VdClD9HHd>F#P4B=S};j;|kbcXOd>O=B7a&9Z=Me;@FknnfrQErBC5r(h>wJ6zvT#{OhT#{UfYD+Fe&XW<{GLAJOBi2(7lSMy}*OOzZ^1E1W3;&?nk|l(5(z7AkFpqOmC0}!LTljB=@Js4b@=Nj+>LKzW=I9lM@P3ByGU|Bpc;@;thH(Fks7NhOZA$*GKudDFDY+@fKuLyhngX>WO9-E$%6K@%aj}$qiad=W?9CAF$`Bq*-9z5PF*BGUJe~TOJe|CjA-tdZkt{0XWIwlsFDeM(=Ts-M6UU6Ogz!I9AF_mS5r%M0YA`vN<EJJ=xC29YDfKLQDLINE{EV7T{zT1X1x+WXbL<IA2<M~97|X{Hwxbpy+mTC99mozGV<i~Er5VDd7{d0{LS%cgLd`?&&{}6zINSf}f2EN1pS*`tEdIv||LZR;KjSw4<++S~Wq#D%p>+=VRyX6=R_X(-R(`VeKi0@w0R'

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
