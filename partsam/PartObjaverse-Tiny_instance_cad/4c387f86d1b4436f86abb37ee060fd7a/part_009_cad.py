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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4c387f86d1b4436f86abb37ee060fd7a/part_009.stl', 'relative_path': '4c387f86d1b4436f86abb37ee060fd7a/part_009.stl', 'source_sha256': '5a43b1314532bbd694b983156af28fa997d1606b7720dfce1bba7a637ff50c0a', 'input_faces': 1236, 'input_vertices': 753, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11646176874637604, -0.06661361455917358, -0.07087747752666473], [0.11646176874637604, 0.1844421625137329, 0.05367153137922287]]}
GEOMETRY_BASE85 = 'c$}r2b$k>@+{QP-io4sPA-G#9Iozc!PJs&~xCGafB_X&(2nmqD0dd^5<nZDY3(nybEu}3EZ+`Q8cC$O&AMfXV+t2fPzV|TMyPKVvwVCVOE?xS33jbG1spcJ#sZc9LA!SqYDHD9hj2kk*cWl*>ev{plTq39cG!N_8wL|BgZps8@s)vv7*a2fa8d^LW4Xp1`+2S#9)R=K&yhrvMHO9x6@|NDi$NHw`V+VWt`KG?EP_Is{%9dK5l`a03|KopIQa^&#@BDAc^jY$T9r7ZdGk&I*F>e(qa&_mfRmp~2t)1hr$cLtkH<nk+<`=nRbLr*A^2*nVB3EvA>1HZl(_iG)mf_*1?H5kw@>$b+oAS#J-hScUA*Stnr*MAj!dzFmv-y-6u5z_a`|%>T@8f)GG}l8*CCJN=s~gvFJxs}9H<nj>6yeV~aK{8w`PQXGZm-sBxvBi^ATEF5We-#NZgaW(!vo=_&$Ht!f6m<HZKizmdCsp*2r=cKAMy8%dO6o+uGNE-E2r{_dT{&|$@%6=y#0G8CyKwD6wdj@ja)zJ<_8&bb<t+d8<rCFqnCeBowt83aJeb38^QVSb9$S$|92$s$C&Hk#`0?C+g#owxUXqD*_|S{?3o#2Dj)fusUE(`Q4ezNXn$)Qy|&lz=e*X!gCeiievPYK?GwCE{QI9i{CNh4id?x-cabqy%PiqMd79XcbF?>??|YQnRlp&xPc3iMl<U9W=t;(0U6{c2u)ld9;UD^N`89{db}Vg+i2B!Zb-I=N*Q@c%jk$6mj<=s-OSq|g_2*na?+1st%C-8}x3k~<h_T<vxjm@w4436m&yI#oIiJ6h>$Ar#t~carE4#=oedD;^hF0P7DL-O7Nf7m;yz%7n?=OjZupW*JGUfknMZJ~oD|~8s-p;XeTt5HjRmsM@avQEUzsAc=`JoNmPiIXIH|A=>E8hOp8X>0K=e4=swC&W+DC$93HGQtD+;*(#3|F~UZ_a&LIPbm9Tt8B-)u(zY9p^FadB5A-MZMX7Ryc2bk=x;sdO@bVZ4!U}Lj!*i?|<Xdevx-PEy_EtB#L^|bF^Dq?)S@#x!P+j*XQF-;ilaBkn8hCrV!J1FfM81o?ia+NA9P02F!JpTQhphaFuK0n=RXu{l<Qw_?8vpn{CMhe%~U;xjnQFnQ6+0MsfMmr+bReRqQV3j}CJA$Znz@^t@1A{`{c_mzi>H+-qGv+>~p_qmS={jk#L<n&~*G=je}iOY6C=a;^Qyxpus>HM+>}yX^>%OV?t#og6vG<^MY*a{J18Jnls&a{2EMa=Xge%am*79lgKuc-S?B^Njm>`*(VX+<9vu=k50Lc2rNX9qWWZ-u}mr2SoX{^Vhn{)qZ6|h3_0>E`Q>XC@<#@{~%G`vbYK7&)kzm`5tdXc{z8ic*Ny%W#PPZX^}fyec<v^Zv8%2nDCGb`$YanbCKI7J><_X<?7Ub#P%I`H*wye6L06w?V|iQ`46i_dE4>`b3W8xl$Ud*q*au6?w!kd$M<_h`Kt+Gru+wGpRwMofkQbjaGlF{ck=hr@{D&yuFknF$~*5{Isf&6$dya8mUtQSk<U0kUL!_qe_CD6cbC~E>UUXah^yRDXU$|+x#AV->t)PeHRZg0#TCh}@}C9<n93KA=6qX;xu!fQo<GmhqpM8Yx#6)}e4c)#7MjY}Y9Ml@?pM31{Npbow>CK(Vk*Bg?;cUU;|A_8%?olqBfWTETaS$)u5zs&<XmZRXP}ocNBvlHz78<u)jfDSNuySnw$pb8m#=nouBrU7`TTi?X0w~he=5x17w0p2{&OXft4o@%HkB{*bhoje>N)C1IrBi&gW{Xn)J_~>Yef6e^S*y``$?(D?I-rdUXgpg*(u7uO$l+8EA?tkc9~bnGQ`W6+wySzWIY#X%CF|<dj9j!3e$En`f>j3z&um=kyAvjzHekVmH++==aB~&naYRd<aW}<w%Sy_{>|OS{;ublUUU9S{<T~$mpT7ZRP<l#-;cT8wERVBkvn(R7xiW<zms#nto->S+(KRD*6+Jca#_BJZG@LGkFUt}cFZd(*+p*6P%Ow)zT+G&ALFsWl<x@T@`I<^P1|{9;ePj|da$W{vznZ*S-;v;9`)lWQX<S$J|%<bceam>*P6=vlo$2m$Tw_>sr)TZ9uIL`aGs6fyj)W*A6|>cH!aWCM&$O$6yAQx0L~+7@b~IgJk(XL9N0L~Wj?F6pO-N|*O|AY)|h3=TXx}gRW2yXw4DhXxt=jz>G{pwTs~8*-Bcdqm^x^1u&KOzN3PG%ZL3Y?F^)NwbqzC>pH)HR)@LpFIP#=F=gHm0``Rbu40V-j_3%xe^TQ}FWB%({u7`v9XPNT<CUE(IL!wOEDfb7Lzx(F`Q~3oqxP1L!yQzGefu?%U^EDGq?M=^L*4$%kZ+d>96_4}ni*Y>!|7iaFDGx(j<!a+c6J6y>z6~S2jJeidGL?-=c9Cn><9hz!Ip;pj7MSw(Z+X8&4z!!Lv(=Bs=Pvseo5}|Sao&8;YEyab`xf66YAV0*7m+*nKNI7;WpdplkzboG#$ij%+;O7)bg#krfIEEL$)6l6>f`>qM3Haq$K&3^V38~Kmz;aH-X=bOo6TZ7me|#tzpE_X*ZzBBQQq=tw#Ze_BtHLqG;gJNpX&i!{%q@wqP$nzc;UPKIiFluoJZMLI9ChL>BD*LVxqrWsx^)gpYu)~-hQsfeBWby=@p`U-C|t6t(*9K)?cE;_N`Zv6GYy6h$!dqU(N5kX9VZ(R*C&*c``ucwwgUTKh4+sjvx9)3O``synZ>+ZWOmS;(eTlFUE`4w}&qkUZt<d?b$*&uQ!L!FW>Cp`kDAM=U=a_6Z>^<ey-<YNpa$Pjry6dH*+cB!uNHE<Nf}_X0cyy7UA-*t8(7-I-f^njN|v6Uy}1y{$jt|nt$f{D4&b-Ij6+&Nm=VJwx_1g%6b1m-0wOL;QhPmW30%#O^Ou$V_Q+)(cn4fRli$LZjawBa@(bwoL}+SV{C8s;0v5Di|6+6$AML%-bS9`{CI9YKQFX+jquC|IFD>0+M9ZCUA!sZn2Fm%EjLjQc3TYR_3ra^agH)kqWtZqvBvi1DAqMW)Psk@dF2s&oi>f@RnOnV@by|s-(}+S7EXyVwkyZ9En+*i%cnUnAGAr-L+*52MEyKT5V<=0Z?PZM$#+7y{ZEfEwnNpikGJE-=L=dpR4V-{a_2C<?$O$twOMwNr(P#>zP!I^Z_W;5x!qP-%lVzo;(e``r!E!mlXWHM`2+d*dj1HH12gAx9+6#qZtJ3?SW}Mnsqe?W2l@Ol$Ks=6yBQM1c%>BG#d-TY;(A;0*(mDMz9XLVELB9ks_&n1J%91xTrJc~yx(8rMedC3%6Zw70iqte266kW)spicvy1kowkye>cUn4;tBqfCJ+H@g)5Sl<c&Rv>^7~coD$1+3I&rQ<dx_T*=ke#f=Pq(Jo#!#Jf8#3gbw|uPyRm<%LyvMj2gGr{s27jVmuHLI**MB>Z2z{L#mu?Z{x`3;oARRzMSUvGzle6C6p!FMARnJ+&V3te%F$menJ26jpX=HJ&UZ}_{oR_Qa)L2er$6BPB<<%#i@%#(o%6tWzQ2+G*mCi`^YZ;;t=~D$KH&DYsL3j0Ke8^4P88p7^sAL3pLg^a*Z<l1!n;IseycL)f9w#)cW16J&a>1K{Y720h5O6gUsoFYmr^Tzl9w^x-G#?PjKj*32hqlU<cQ2G%G=kEjW+fpN7)<Vb6SQBi8i($$ME&s9?JFO+<AVQC?9>2+e^W^(Z+tE^ti_3r<PmS^Zm8WRr%k8OGO*|siUZ`cwe=BLC$Y};&Eo)OCCRGyo=)cxg`3R;@ydlM<4D-8T+-P+$paAUDr78TH&~OJ?|Qy&yPJ9W$f2h-#k2SR6ELfczQ9eI}V46&uLHC%(*pD+)uP8pX2tQzAfj4{^fek(npLNj;#eaKXH}!<MM~1zdMqG#eG?|TQIlV<kRB(+|i>C->+5siO;F}hl%pez6#%mTU`4X_s>Y~rw1EFh&=Ko=dBNl^BE=d3*X-zoI%_NbiVq`<3pCGobQ;)^)PBO-;X+ehjZK0!N&6HCkN*k=at2tyuWI$;XL$?_*~Y(qj@}e8NvCXequbf=Rao7aon-nmvVd1^13<syk(gZW6HJue#2w6F;|a2<o=lAEzXOaNej6=#u>-akqM?8$7S_oDRYi-#!-G>JlB6O&M^)s^RM&qrELv<-+X*O*>OLfk3S`ME;06Z>xfA1*K0C~Tn*{L#}Us^J`VQ#945-IZ^p;dPTfSmbFLr3d4*4W9{Fa!$Ss*Og&F&)I^~ZfZqFCRb%~NOEAJ0&{H&H7YV5zt!!YjG2}vSXU%$ii4mU9lsHK*Mn);EFPJCbct@)wG{;1q6&Yvgmh)`pH(fXI3qu*H{1&Vrb{Is2)Cp-=n?c7o4s^}NW%nRZ^u`;B-Xt&Cs|HOHk+IZk%e!q8o9Jx_~&)+KSS|~n$ktL$tTHRCl`gdmMh1|}ci0douxMrE)!MQz7T#wmqmf~@8(3b@wpOcZtlc^ne9P4>`fwA3M!k(M+tABF;dl<p_+Uc`Q?G5#y=h|_tL!dctQI4-SXBRZ*I8HfN+>bNm=oi+VKgF1G^b1?)(ACCVJD+zPxFGt4n!V{PV|!Mg)fM~2`n3?}eb#Y%#`&K0Qgo2WziY<FuQUH}d(QW8rpQb8=Jp(C6~{aKg7Y(t?OEBpmD}fa>r7*NR=N~kC$?AjdZ4jAD>tfeZjTBywdXnyM0>UrnG<Mi&uWXm#P-$Du_9LkKJs&@ec43+a%AlnXl&1F<6a4-9PL?cG=;bGxlW+5JzHmaB${%xXSJo1^G5#Syh@!E&h2?;8_|#Kk7jXu+R}i>`Sg1uM7;$JQpI*geB|+2c`Mq#ZD7{vqWqf((ViXmV?^#e(aN8{?;XC+Tc9zwx4k7e_xo<F_`da<@wmF--)YA7sa)7+&L6B2@2`!|&gj$AjP2YpJ=a#T{V6Z~jQdMH{-fA0&OT9o#{H#s9Jr2ste<IrB^KlBf+lVKjQdO5zgn)I{KW0&pUq-_Ict>iGwv_tQbd9&*T$a<yLkL*^VcZj{&KwUmuSkh@n>%#-oIDkM~e4#EEW69dZG@G!?u1SMEMU5d7K%1P3%YO_A$dm`5m8le?70r=Sv<}hluh)%XxpzKP&dHS|#%B0Yg1ltJg>{<@jFK-s{b|R{t5xas6vKzLzp%T%xHw_OG?)`7NgM+V^czCCOC&(gfb`uY%0wwd<gsr_JRpr^ku!tDWa-IrgKqf75lQ@_s+^d1|)K=JMM4<mD;m@>;vn+K-lFoKb&oV*WhZc{q+EdcGxv?+cYGWX?Z#=i~d3%jSB<c&h~Xm~)J`>eA}*rX1s~ZA5sCDbM?bkDGH}E;Hs@yK+37ZOXNFrDn65^Dm$Ico!TJY0A&6;Pbs|b-2CVJtgk<f79N6&Ns}<Mf<dVRm6R6xjn1FE5v=cZ`yyl2jaLW_ai-*`jIn7QE`9wn|`Y0Qa{ylxxZUVH0SctxS{9LxS>`W!MQa4*t$RATpF)zGX{(nxpsb4<{6*=?9DXB%h2Am{$hU=z`1t5*Kd@l2j`o0oTI%tmZdZ27ks$At=ySl%F*5&A3B+HocCI5l!`ay+VTC78e__Fe77Hp6vubxv}5A>N*=fMTpIr^^ImZ-jsNPhLjEF`jw6n^CY(#h9i{HgU&Z&7j#JjBom5d?I<8qR2hI@X<>O$CuXw&EA2*ffH3N<9P&@wWxpe%sk8KrbY;W3e-1?z+ps{^w$9*NhPvr7>g8jRoKx2E;&MU0J%K}a96Xzk;aw&nvcBr?{6F<x}wnOba$1?TIOk+FL&WjxG_c)i%qa25p2N~O^cHZT9!Osok^EBmC<5|XbtDV;=q0=~*&P(-NIxp38>AY0WrSnofm(EM|Tskk+a{0VeX?<aVu{~?&+j=gYZ(F;4<Xk#$xBHY8_nGALeCL=BoJ-dQ>f%)*m#-s~Dg*dFoOIn`+jUIbcag7CEVB~$K9h7^V`=3bYHZJ1{oCdZ3pKW9?YL&^Ixp1Np0(>NN92-FV|&)F%bX<>`FdTtj#J`)3pKW9?Yhre^+KqrJ>xpjre+8;wrB0S(o%MKn6W);*P+%cAH$68S-Wo4a``&fv2;7vt8`s#KUj^g^Q7x&`+|<)#`dgTcUwv?2sgE7T-WQlbX~9K(sjL_OZOjC-=*QkcBtL2&~xd&gq}<HCA3_=FJVozb9w1LiCTRJ=hA%@=ZA}&OZQ<c0Z%xW?%P;1f971e&!g7=p3fJg`$D!WU--O0x{sus?=8k5`M#5*)MAm#_o=KE^Yb_)-PdwXZOyrKAIx5I6X()>Gh6&&&gJ`TPtQad`;m5EPOW;CbLl>wWAwc!WB<~}z4!k`nfej#6DmjYM{|ES-&eF|vP2vEqjn$C(yk)s(tS&HQEkqp`<#xbKAcPUMeWW(oJ;pnon^*E8~d+z-&M_eKib$&wfnS+n?H}E(*0gNm+tpk=7exA-8WWFui#v|&+Le~&$)D8+M2;Co;%6+vDHo%yRpA(_q`q4tBG8`Pj1b>z;5jC+WmGdm+!Yb>xOW7>3+VW$5OkoziZD6^jyBrKV^m8)PM0DLC>Y<2(~CY=hAZu#hJvp^jyPQ!kxzh`8i18PJBF+o|`yx{K>iWoJHB~&d>3r=Q5U2E!G&@k9J&hZ0*Fk^xVhUz=w0`Ig#~s9Ou$=B}ccNoJ-H4Y|9;-%g?PGbJiN$zxMn~&!y*ImR8Ygjs04Cj%FFMhI8q;o1^QowZ?v}Kc|a-zt-4KwdZ=yM)hKh{YZNbXelr~#@LUv=Z1FowLGp%&l#0h$GE)wT(ZlR7-PTFo?}{?eBfMq9;yuZ%DMDB)K;Wvtg#>I&sC$=axOiGwYB&y*4V$a=ec?=J<oN_IUZ|l|Jrk5d(!DxQ~TGRBj>ysYwSnb{&M{Mh;!*Vwe$K1&ZXzt7HbwBkEG||O8=bf(sOg`@e-U%&)F?mJ>!i1OM5P_zHQIB^c-L9p2+_$J@>bUbci>$Lv5abrFAgp(!2uo>jlo`c?cg$CK%hBHgCZ)vIpnVJO|sq!xN0{P@5N_<Vj92wnJ?mg)*jSqOo0R^DdO4b$EQ0=4n{l4dC+9ybjwx(-MvCN}C^|=hFNTYk>gXzBJFo;k0vkX<mwY;|1r^JQi!ocbrS}UYw!T`M4y_lW}aX!?`rC#u@x0&zqFy9m%;i??}$Ic}IFK%{!8FeI1aNOY@HOT$*>J=hD0*J(uPk>A5uTNYABtN46*ZIhW?4$+<osPtGw9P0yuyXnHQqL(_9<9-5v@^U(BMnun(6(mXUhm*%1Axik-r=IM#oF6Jc~bK|^3Q*M}-C|<jmmnd=<^AbhwVqT)iUCc`qxr=#;B6l$_QRLFRM77&$)W3P&rm|@(=h8e_IoIaFep4RvVD(&@2P@~=JXk%K=E3T@G!ItKrFpP=F3p40b7>x|;<1x+X}&AX6BaJbA6Bb8<y@LyE$7<&>Thz)uhw&Eezl%U^Q-k-nqRHw()?;Ym*!XNxir68&!zd*cAv~V-&dM{ZfQ}Fb7_9QoNM#*<y@PeujkVId_9-u=j*vNKVQ$K`T2S-&Cl0!X@0(*OY`&fT$-Ox>lcil-?(1Gm>bt?7<1!#4e{E=dJR)<Sg#>oyI8LwUb|SY!QcPe^%^2~v0lUYeU0liL@uq@P##!0m)5yB0)}!ft(VbrdA-cuxtzOLk0WwvJ&w9Of?vz)dhTvA<yw1ohFsuWT4!X<m1V!krS(eo#Z5Su);-yG4&q!|S0(4#x+=%`Ky!Jl+mdsA-PWyzBA3^NIieFem)4QlkDTM}NbA%r#qM%0t-sTAY5kp^OY86STv~sp<?{MFJ(t$s$+@=vPR_OUcgm6n{Jzq9Lp_()8#=Q-;qA!l7H@vy^3r-tJ(t#FYPq}~Q_rRKnEH04^_Y5jX+5T#YwI!PTw9N6?V|i9UQ6pw^;}wiYB`;bb7>u`(mWIA(z;h`x-y(g>wNWGTIZ|h(mG!)m)H5~<)!t!a;~)pIoH<nTBerg?aS+h-*|HFVqLRv7we!!d1<|~dZ;m%m)2QpxxCI={m_TYOY6$DTwYhMmzUO+>*b|&<#MilUwu2$x^g+!)|G!#9`&h?@#b7wU$5uV`g$#w*Vo&g`fzz^UB8yg>-y>U0YvWNcLR*M_PYVf<Z#};^t%dLF8{8AUS9fr20fR4Z$Zzc-&@dg>Gu}&_mzHcK`$@;-hy6U`n`p3a{S(coNN0_@!ZYZmwtak%jMtS&~xecH}qWk{S7^ret$#HrQhGsKaceL8+tDN{)V1QzrXQKuGNE->*Jx{dCpz@9*cPG;`dm@YZt%AB3`@rJr=PY7r)0M%DebI7LmL7Jr<F>_&pX;&c*Ms7<1$Au^4l4eC%xcRh>IyHy7}0n0h6as?170WuUj=Cv_;K|1@{~lR86c|F3>hr$)_Mb^m|Asgq@;o1z4!DjFh=f(L-fXMm%?D<I<Ka1~5G9lRX83?hz%{|YAe2a`vDcfhy7Bf#WK!P~%FAmYvNaBxzpHl!*TA`XLym%ulHH{tJ=z{A1h)4)r>Qz2p>_y92Zk6<70PY`i!h`1I+Toc|IOx_V(6I>l4t_p7tCT{_*3a$hZSBAF)leYp_23LWIJ>adu<ZZwn;0h42C%i3~ydBsRToEF!2JZkS?*y&}t^pC(gLeftg7<=V1(Oc~_W}=xh=brW!Q>&}An*c+I3B(pd=!2Xz8*}z6?_tW9wNQ~-wr0<5554t0TEw^?*m_h?}hIJldlAmM}x_uz<a@aAmZKd6=3q^;N9R|5b;j<GB9~0SnIdMm*5xSJHX`Iz!$-PK*Z<ZTfpR-!RNqdA>uReO<?j3;4|P;5b^KuB=B)~B0LF99t=(dFM^22L&Osy;>qwZF!>TN`BX5u4|p<oAVk~+{u7wIHn<D8E<~IIBF+vGXNA`Slh*`i1!sbYGs3Hb$*Y1hg4037pA_~=VDidf67gq+Mf?R`1x)S%CK0<q#P0A4U~*5eJNT=@B2JI2BAC1yI6XK6M4Sy?1592IoDEzQA};QhHtrCYg#Q3<1SanV{sG(@A|3%B4kix*j{whti08u>fXU;*^TBZt@e#MQaf<jJ`~mzZnEWL80r(L_{2%;0nEV3xKkz4r_zV07nEX2U3)tPAMeOFDHm(tWg{QzNPr<+M1(WXqlkWznfUiKrm*Km><U7III7OV^ojn8m5}5oVm_+;;BK`>f15ADn{1N;CBK{YC7EFEy{4e+)i1-cs6qx*X@Eh<;i1?XX+PFsiC;S-vIG8*Ud<>ib5if)<0+WviF9eT;h=)SN!yw`z@QGmZ$zbw<VDc{DA>i&1aRYc=FnJDe18`o5__@L&ex|U9pTe_)$+Ln<#E%sg@dJ1!FnLBWiTJL<BEAMs2PUU+@ESyX6(YU?{|x?&aqtF2d>bOZ2dDAz9^4&FB6cb);yZ8}AMaqCOpp8y_`bp-egw||CeH>Y5x-Pe#P8rm!Q{okBw__3&g_;pZW0%RTi_+Z<UfEd;KmT~FYw-A@)6))z#}2z+3;Cl^7-J|;CT>nEIbZOegqr~J`54xbxRv(i66q>!S8{|AAsM1)48*VGs7Q&$^QeBi1WI$h>O8LfyuvsNyH`GS;VE`H2#*xIP3;44K4){TinyeWeZ*tEASLB`4uqvWw183DiCpbcm{BJuqQ-Z0Z!v=1^7oWiMXUYi?}%a1DO0@Fp0Q`JBzp={2ws+8!(BufIEvgKl~+_{27=;oX?#_oX0(F{3Xuq&i)*)DSwWCKL&mdJ^>N0gC~H=7lPM;7emCO;bXz%L&2lLgCXK>5OEKPxF>uVn0yGBygQh@0k|jldx*FIJTI7>#^nO=7hn?ct5l_=>aSE?hQ9{C#=l>Nh%Z6J7vV3!FK`UF2oYa^h|j~HfuG?Ra2_H)2N9ozKL$U>G2kpjd=er)4!;Y&i(|lXi1-LZd=!2ad=<xlqY&{ii1>H-ZSZXz1Ad2yPea6~;7+g;$AD81@d=3d4E#R$K8^urAmTqD;w$i%VDfk1E8ssN;=kc^Z1@|V8B8MnsIZ8?b4xpB5Eq1(fENRkTfim2r6FQ3cw;d6FJLclABcDqd?c8BHh2_x4n#Z`J`YSD3!V#(frt;m4};0?f)9c3K*aam(vC62PvP(355eT`!0*8s-C4vr;dJcDiDOV^a87U`h`16wFE}rbF_j?V>JV{lcnNR`9Aj!j#PuQKdhk-<QaIk!gNW-u#0?<gGH?Z~;J8u-DsL!H{5?e62<{2?#4)B3MEnCp+z?(8ToT8ah7fUGh`1KK2)GE2F|{D#nh<dfcmZ$$9Aj!g#ML0;s_=Z^d^pxrg@~&_#FgFCj!DE7;kn?s!Q^yI%7xd&e?i2j;U~c4>%gbM8zJIQ_+l{mXmBXl4<h!34+fKW1N(x1hKTDx#PuQKhVUL>@}6Mw@4@5+zzxBL;B;ImgxAFR;jh8ue}Tz!yD{g+XUY$+53Y~*AkLIpw^>v5*p2;#8#DPW@MG|8h}Z#729vJ_JHTro;z{rcU~+HpByc~7xCy)|n7k~w3AhYITm+sE{6S&=51tSFPpaOeDvulce_(PdlLuwXg7bjOLB!4BO~Fm^S(`(|Hi&o}d;)j^>S7#3Y=?*sz>~qrsOtj|@lA;M75oMG1@`4Dcn&a$I6IUjRez^uZ{66x!)wZk3&YF8vw*YU@5@5O9uRRkcn)w5w6Ss!aZ!jk8$1&@6WU`oye57P5j)|x!MD-ooDlIrh<Gi04R{UO+**iu3Pju&-VfXlZLTjwY=wwR!OMWlpbeISh;u>2|0-#1l=uVM;lB{^Lx}h${0;aG+VM?@_&P*<3;q`T1pXfW7M#V6JtzDv_$~gPm_%F{PW_=UL|h(T4qOg>pgcs}3?l9iw}EZw1N|Z5F%a=8xE*XqA6Nwu{{|6Xh2I3<M7zHV5kG-b8+`)*8##@!G%nKk=&jInGesEy5qE=#>%c33$vwe!z;z+wdhm*1@=D-(;QA18LwFT1c~x*j@b?gLBX~71d1Y`Ta07_AHrxYDULIT<ToWR$1uq9CZw#&l?g|n6!25&AgTOxEP>6UvJQ_^C0=yoa1Q92|mx0M6!3p3vh&UF$6dVH&hc5-sfzO361uw<l&xMHRLBtE-%fQR<`4&LLiy-1)cr-W~-#-{49sv>C;Qhh<QNK2bxH?2!5MB;k4*RblL|gzOE&}%elUD{80T+XaE%0h!@~U79xFkee0$v47UI|<RTpS`U3a<zz_XHOO7lw!n!7G5te*hN(*MNxo!M(vF;j`f0VDbUrS>P~;*bWi<Ld4zS-N58^z}>-3A>wB6x?u8p;AY_F5OE85eK2`La0_rNh`2TUdoXz;aBFZIh`1%Z0hqitxFxs=MC=8x2_~-v_5xcW;vVp>U~(UD5AZ;UcojSpOuinx3cL#<-T_YnlP7?8fVV-!Ti|hE@>uW|@Meg3lae-$5O0L9g~x!&!@+C8OCaLeO4_(XJOw@#J_k%b7d#a_4I=i3&jXV$0Q-ZdL&P)Si@@Z;;2GdRh<F%$1en|g9tQ3U5to5i2a^{BmjP#mh_k~BfXR!1vx9R&#JS<cz~mNiZg75xI3K(un7jlyA2=^WoCjVUOkNb62b>Ec&H*nBCNBie0nP>ymxb2=llKFc1^0o7hbw906tSABfK)Anh!;b|A@G^tnfSX9_((AMEN}>TB}BXd9tI}2gUNS;H-LAhYJaM>rYae}9lRa?o(vHmgoqErcY}B1Jq|;}Yarr5a9=Qackm!^FNnAUyeXKx8Mp(uBShQ@-W*Kc0^AAQ86y4(-U>|K8vGOZXNb59ybYMVCAbUtM~JvRya|}x3)~*u79ws3w}Q!gfZKt4Ld1jN1Ht60z=Of7A>u>uU10JZ;6q>sM0^0g4NSfTd;t6#M7$5a8BD$jybrt=BHp8<jm5<K;alMw!Q^YfTfy-VaRht`n0z)k0z4lg{#8jEyNSoZN5Q9n$)|!xf&C!j(eP<ta)0n>@K}g=9DF*Md<J+NcmhN`2_6V09|oQT9s&{n0`ChZF9ZGsTpA));90@s*_E{ah}|LL^zfWu^4#F`;EWJ)7I=Ozc|LF!aAt`3J9u6&c^>e0;7ky426!$oc@A&}a5{+C4W125URKc`I}0ua5%-4o0h130_XZDzh$q8mg2@BGlfe@q;_+}5JO=(NTm_Ra1pf-w+B31%&WV>p#8L3YVDb<!`ARVP25=O39egKv9XJub9ZbFzOdb!8$7f1}F9$Ejdl09jHmoD5x(YuACO;0o3cdyrUx)t=CO-<k4!!~rUxJ?klb-}%0$+fL&%;lE$+v;egOefRaQG51`FL<RcmYH_4n7!6J`g+(JO(26gZqHV2Y~&+BO&4uaBuK%xDD<N?h5Y)_Xd08@4G?7-67(ha38P_K3`9WxHm-H2R;})7~j7SL_8EC4udZNFG2l=LBvrI@qYLT@Cod{{SfhQ5b*){DKPm_@B#2Xh<GpjcQE;J@Lup9h<G>r7?}JBcsF<#M7$FsJ`53GhNpm?@O$tSF!@#RJ@9>q_yPPHnEX2U0r(+Ad>4KNOnwP`7kmdIz6HMkCO;3p1-=0hpN1!c$-}{?!4VMgLihqO`8e=G@N|gSA3g?5?g#b<Plbpl!$*S2M}Q}TCqcv$-P8IN@dWrV_;4_}4Ll6o4<hd3p4JbE+rZnxyMoEPf!l)HLB#Fh-NEEN!R^5vA>z*P-eB@R;LhNmAmSnLp<wbb@DOk)M7#nX1t#AQUIE?=5pRY61|~lM-U{9V5wC~u1C#FsuLo~}h&RIbfXR1*H-a}n#OvU@z~no@>%d76aUw*#10p^IKMW?n3_b+D2oc|QPwVHz(^54$Rlh>SV<F-}a9=QaFYqAnFA(vM@J`^L;jJO!mJo4scqecZcn5eVa3^fH14P^dBJL0O1^eQ2_lJl_LBvzw)4(&~v*FXg(@-z7A>z3Z@qD-nCSL@e4-STiBjHQI<Y&N<;Ik0%WB5(*P3*VF5b>W7@iVv+Onwji4EzEjehI%1CVv2a34R3;{{?>tCcg{*3;Y}+ehR+>Ccg!K3Vs3+KZ4%?lb;4Z0-uA3m%$^z<O{*ez>6W`dGP6Aa)0nV@EnME7JMq0d@^_zI0zyRgiivKPXq^o10doV?rGyY@l5y>_yjQdFz^(x)}D#`!~22BySS&de`2k_5O;7-J01`>fj5S?0h6}{HwJq_#8!AaFnN2h72FgeZU*lNChrVx25tcnw}Sr!CLaQB1?~$GhrmO@<SW1-;N=i;EPOMVd@DE>91ju4!MA|P*MsB0t0CeT_$Dy<MsN&xEkwKqz5z_W4!j0zhlp3flfdMO;8oz25OFj_oB$DThwlKB9|CU&AB2eifL{cY-v*Q41e2cu{{eQ;K5ggbo-bY6V%2Ki5t$0LQWR1)CG9_2!<pLpeaDO&g4L_?Uz(S>8vn9e>bCSnubtavpnC?2d+Psm<HRk1Ui}Y_X+rJ'

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
