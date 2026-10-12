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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_012.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_012.stl', 'source_sha256': 'fc6c7b8e75d9faddac799ed6a7f39bc3b14644dff853e40ce8b868172cdd23c6', 'input_faces': 1420, 'input_vertices': 794, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1094195768237114, -0.4827260375022888, -0.1668308973312378], [-0.09983645379543304, -0.46227800846099854, -0.14577245712280273]]}
GEOMETRY_BASE85 = 'c$}r22Y3|K8uw?HB29`S&9)-a1wlkW#HFf$lnAJR5KvGe1_VS!y>~^gVs8-@P$Mc90to?@D#oy2S48ZBp%)bu6%%aVzRvHRv*%=ap6~fS@AE#t-~O4qnVmUv=A4<?9n`Nv#k!vV-)UaG1#4RU)YtQ*YIt?M>EotMn{d^*sco_+-xBg_|C`Hy%Et!`y=2f8A#b{OYqP7zO}%PLvo4WlUB`E7);iK`{G=(<ri{rRJ!#6-<0S7hX5!Rw$$aXyV<wMFzHWYQ=MJqSXSZk_xjpj#_+Pc;DwKQ|Ui(IpMZfRbD$HGSaQ(mh;m8_cr1Y1xxh`L{q-G**Ua-kpKKA<->wQWN9Jby+wxmWPU9Rt=xxSCPyyn63-yN{lCsx=pkuEPPD72Q({C%Ufp5B2S_ImO@Ztg8vW-TAAr?b4~?(+I~GYhLF(&Z)jn_17z{`&v1Yn#6v4qCY`A1Q2_NS8+oR{pzu(f1!(@8d10l1QI#v6pANMVIzTq|Ni6vX+nhzS7z68}02@*ej8md%B(T=UB@J+s#=%*v`)K`gbFIE;o-Be8%$Ytk0Xfq;Vo$UX;I<?Y!FAU)>U^d6c}U;8|;V{kyTkNFrSxy#Ij(_TOF7DUmMEEO^mgK4|Bo66x}i#W8Dn@Ao{XozJ)SOXkv%iPT*8OC*1$wY+YBcX`d-<%9N6*fEhVkL540me=(xT2e8QE{_#_@$d4H{j;t85-S{%NX>)&l0VB@-n@T<M7lgyknr2{cQfsFQrJI{E|29uVl8hzZ(nP9PxJi8*4sJzrLc7(U9SCAWdC&Mc$}O_mwWjW?d1>8clP@fYrjX9W+zf}v){9=<%9j}EN}L^y}bV2%q3nTUG6Q}_V4o1eOY#YwRC(UHP`*<<xjVk58kJ+b|PIKEBKJ@Fy7jp(Za5Y)V$=dpL+$ltp9Lp|3-s$Zs&S@X&&@HONU#_>wY)K#c*pqqf1Unq|3d6bu8b*X(xRXskyFy5$#IzV87F@+}yOQZua?Z>1~PBT-!s@;!JD#pr2V9OQg$l7mu=*5BhEA{e$zk`~HXLa-1GXn`?V^^H{+S`n`_!`Mq#jA~n}`70bWYT3+ABE3BMImz(~ljnhA5CDP?Z`O|2(E$#DB(9T<0?ZmY6md<|cm`Iz`f0}%*b6m7^*55xaqI*xV`#t(k%}u+SWi4;^OM^tZT>H<=J=N@ffb*uCmvG)R`CRL~>E?RgjP9*$x3{IU66x}y#lx)SV~3x#+t0qRa~`}qk(z7!_wp~dmN(}?d--78;w&GWr?mZ(2j?km|N1_xXVCtgJi6r9w7IurU)o%ci^#qst5e%&M9(8m9-K$WP5+i{EpPg_Y-@S_yW0P|x%U5&{fAel?q40px_Kt!*vvhLR;RXG9fxSH?KVn(tGU^p6%*-lJ+8e22Ue%HPaS`{xsE?I*Z0x!r<?2eGrD)1^|^Gu;O07C&^*|l%op6;E7;8E-E4m@=1p#{^QO!_@BW)d%X<0a%ta-|sd=olhTo4ZZ?wVxyBn=`5~E*r^P<IB>r?Y+*+u^OG;dpRY91-Oz<-~-9abJIt?RGP@_HNWypEs8BTin+?}y_xoxG<1{>xiid1h%<zn#acIC&L+{o_rXyt2Rk@w!$XEv?`mNAXjvJeWrZ{gR)X^XV{a`vl{+We+6M<+1z>Yx!V)?YzG^pW5#q%quxx2kWorN6y#5`UmH!$@cmO=c$S7?Oe|zqpanF@l}4z{=7Q=VP07-XI^P?_js{$9nS>YAvoS^Cer4#f0IAqoEM7y?N-*`ZzqesDNfBJW#^IavGUx~hP11bHl*gU(t6}go&0#(PkSrREUoUh+jvJOujG$Em!D<j(b9^v^RSbLtmDGu9>-BjC;!{u4$B+-o5yyq<8z&89Y>n$aaR)WV&!^Vl+XX%ntI%s{Ew}v$6fIL<@&MJ?3Y3Qahms4acUkZJJ;Wyi}qQ0QRyjGzoB_<X#;CJ2k&2c499ynE031`;~z)M{!G}pzuhw99jxUerDcA5rr*%Kd^?O={a!2{-C*Z6*q*(tJX(6hf1l-TtUOZsyMI2SU&`E5=x>Lz(SCbizF_i^j8}84JXUr&<AK>uK7@Yzi()$;>~A;bSth^4Uw^J|nEYavZ*S#Z+1Y-+=z#V9MWv0c<H+O@>$ouaNgQ8Ytvps*oBex{mFsa7S<%PIJ&vOuPX6asyPXtT?K!r*)cRbJ($cM|$EnE=Z%sWOP5#@~)Z;h!Tuy)J<~n`|KCd%=aC03$ME5SHJ&d)kZ)hGX8_Ikqnn;&xJJCF|tT+3;jkUZUccwirw$8t?6@9H-w_8!Xlaq5kWqcCZ_ZsUz&fmWU53NtlbG1D)uG2hLmf<hYc}MeTS&wb0+c{XCemghb-}<}SZ<oXeSh?;;?H@GvN)K&KZO^gY3s|4a7>|8coSJ)OXIaOE=0&AVt^VBPr*BLByC#oV{fy@3e9_;@|K6H<yqMf?=X$(ouKO#p{MUq?|4P5~x0QRPKlA?8?DcfU;cl+u@L;<+<8U|Ead_sQ`LvU3{Ps}rfRm5#w_D*wiPT)rJNkDuk1~$c`HSXy-ZcHpd}~}9jb~W7_CMZ=K~}EY)AT>{t@fki2b2Hgx3^&Y{H#3=;r%r?=erCm*LJJ@o915WkBk!<+qp9@)7+hx1?%I?%iLV&Wtn^CuwN!P`%Cjt^h<pcsd=pI3hOx1JhN<ovmfWMAG^|DHL>2uD{JE~zvz4GeTqt(TjL^=H)S5t$;lf#=MmO3nAZ%ka-FB-#)nzCjzdg4(flued_w<Y@*`VQk890!|CTH}l(2KI0|)2LIaYf!<DWTJd(&}<$$zxQd%<>a=KF50^Zn@F*?#U^uW)lSADL~9_w@5>uKk;7=d<nea&X?6&HDdfjo*Uho$DdN^3L@T&E4xEZm!ouV!IxrJzwXy!~FZ4JkxJi+>g*)=P9}Q^Q`5gWnH+h)Yw{H&%e4IG}rT5N&IpvH|I4w*ZxY|r^zc=?OAgjmj>sNApgxikC5wmA(%%5`N6HJ$DPT4;5-}QJo1pg{?7F`&E4y7n!DHE++44xW$w9;{W6^M@|NP%yrlF@r{B1b{-otL`*`7fN}E~pCX+X@#!DtY)f#VT9xFYTetx)>>vas>kD8nL%Md63YinvdG5McI$^UTrCC!g)O}Cyp9&kUG=0(eXO4zx5oi^B>&UIRo|749D-8^^s5$ApU_EWOFva|g6{`)UK&ffmc^=CKN>oCE7ajqM?xx4=E^<FpE>lJRU*MVcZ@1}iDwEL4FAH#TfKq58IEbC|YC*)pPXU4-3Yx&&LM)vVeuJhTT-_ZAGyrJz=b2HBx=H&luP51sfzt(nTavd-Ack*AXaa8cR*ze~0#@*I_*LifX-JJUxZm#z=Om5%TaC5z{k-2B4H9j=Q@65E@O>;f3nd5q9+U=>i_QPg8Fw;7}oAHU}KU&98?#}<D{kxj$eAc}GjI{00<aRqW`3R?9osqVEYVNjA&CB=0x_m3AAD&^2>r6kax!VtG9&!5N8EKCT&E4a|<nDf-ag_Z&<0$)G^FN&ad4{!Lbev;y?*A@7Xl=Lh?O}%19!&qKIp^izdYa}xuzW=)|K7Roq4{^t^(#BqemJ^!I{UE$*8>ZRQ*(E_Y3^<}&E4a|<cHJd?)Hi8n!@_{^YqxlmBp#KyMHw=*YA<L>l3`cb36vQb3a#e_kOPC?)_Xh*ZaA#-PuPuk7(|mN3xG{9?520>R%V~@?I%U&C8!(veWKgll${BZ_zp@Z_WF^ZRI7U9PfFXtlS+(X<q)kmVK1-TJ}-SYuQIRuW9a{*EIk8D7ih3(!Bh6P;>V@sJVL{%s$F_P;>V@Xy;~Jly#Kxa2D;szup_kd(F!A{-d@B%_C*!So>XbudJQ_{&{gLFW=8+Is1LrQSz^x_jkwVSw|V4Ywn&GvW_wi&pOIDJnJaqZOz^Bw&w15JL@RpYCAXM>a3%TlkME}^I29q(Q$HY_jvZZGj9!YXWmM#_XT2ki;Gk9a`Rd8XjxCE-_YEd=aNUtIy(Kvc=m5wr{7?G-1)D*zdO&>_jl*5`u^_xRF`+2{|T0Np8pB9oAdlnxt!;JOm08_<L3JOPv)Mne(pTK<mUSPlID7U$IDw*oSJ8Hf8QL}W7#h~(&mw}PS$?c+$(GE9M_tk$$s2u<?eNiV11nH6~X#A*Cm4Wajr`Qf7iMGU~>C9Lv-&bwvT<i(d5JUyv0sFgwM6w%A;jbYrC1e8`~$($|GgxA0<EUD0ydV`)lrA=hR&LRqa2`@~y4&saan0udLj?UTSjtda23n>!l`lukVer#&zcUp62%TQj^=)OHFQHFAcU^x$A_Q+t*Qp?c-c8HMxCV)a3T{#@Mdm^q=;1Z<E{Cy)}2QZ)+Z-Uk&<O@@QEftDTtKz8<c*j>q&kHThX~zp8)NxxO8&r*nN<bNBjl@czzq=HPvt=RAY;cb@YMwwv>ur<?12huH36Y`1|{zo)s5TY~LIuIC+hc|GrFKNh^db6-Yt_r6T<{?2`w;QgKZGMRfaXeaJ{F3sKhTp4^`|9)sm-rC~Sy!`zy&HFmzv<$2NH~qZk?)|b1>%3sjFB#T(!CfEiueATsy!?GPK3BQ>ZW-43-Hf9$obhuHC%2!M4%WwcUfSgDeYy;*J?nkCV81xeSG&1BuN8bQ=lN<kch|>#zS_;rbwxYZ>)x^51867ieQM49^IC3R!pil$X2xR!tn*j-+&_PnEG)G0^7p|tZ%cdI;pCjxcwR;G^7qX(cki2P?%p>aV2vBiJZpe64jEwO<?pj=?%rqD+`Z2}z-pi7KD*}j^9Ck&@4pYQ+NXIAL38)MJh}6I1kK&=BLv&c`96Z1>+^e=d-~EZ+0Soi?moYvx%>Qv$uDunlYQy0F0|T}=I-+zn(I8&^gn%RSM98Jp1ZRT>u*0lqq+P1jGOE8GbSHsoliA)pR3Va&qw;XG}nGr$C;X&_5aXbf9E+XliSZzY3@GH6Rf}UoK>*?&T~G&`a92GncRNP%H;NQR>9|Wo)<E?{hXD_?dPmaZa-fX+tq{pYd=S4a{D<t&E4ndOm06%XL9>FIyVo-4?%7}U#GdAm(6uZUEY4~PV;D4cYE9t<lU^}NOSF<-S^k=VbK2vx&2(9$=h=tDRJ_4_W4D(v-7-Pu%6Cydck_S&)x0rW{rpS_|ja*!+N}EuFse1JWg}{ys^CZt=xT{)8zK^oWb99p63kyuJb%+Y*!a+Jf`z3lMi4&zHQ}t{Y3jQlV9MB+q+o%H@c|E$?fNCHTUQz^*Mi&cX0M&7xtt5T(0Kjo;MD1`+42q^E%J#2A|7)4mrr}=XgzSKgVlw=ecFw4({{4yF2=y%lZDGo9p)nHP`DWx}7!Gemk1?u9dsbU2E<>M;*M6^Zi84-R~y`>*;(y(arVyiA6iwv;OvT@+R+Vt-t1ap3?ro<T^gwXyp;+q1v8JZa;^wx!y-`*C&`?EZS`4?sNN^yU*>L+<tC9_`J?@`zE)a+Ydgk^W474?dSGQZa=qga{Iac+?{RMp7!@{Oy0-puS{-#56I-*opC}Nwx|959h2*Lev_5E-|I2C{k<NO+u!Rkx&6H!&E4<ynB4wekIC)t^#q^S`Cd<KS4*qkHsgVo)_B;QuUlH<Vf}t_?#`zE-*vw4thxJrXU*O3JG*&sU3d2>*0@EVPt)A}ez)fC_q)sG&hqZ}yWL!$XDiy#$j_bct-HBCzZc}r_ttZF*0lOh{XV{%oAGu{tKZXkistV3@l9@jAK%S&o>H{q$g0%+sP|hncYl9CbNBZL++6Rs=I%VWDs?~V^R$|~zt5n#`}+)T?k?~CK7*U<?=u8{*ZF-0HxI6x?K-e3b-xq^<5D}<-?a#G=XWjKT+f@DyT5CZyYn+^zv%Nhn!CT(p}G5e9d54A=frkxw$?v4c&^gUb@`$l?^^p&=dGH%zki~+`}-$u?k?~C{)wCGbMHkvimmkweg~#pzQtbN{T&!L*WZC5cYg;acjr3m{bNq<{*H~C2ft&peX+GYb)N3#`u!Kp-QVYNb9Z_7_j%l0f1f9J=K`nQwoIhUwcpU({oSFGk~#M0(%(CB^5FN5$jkjcl9TK5McZdv@1uWLbNBb1%H_`cxWDgIwEZD#`G504)~{uKK7G-JwR?J=R8_C8H-1dYPi09c|0&b|RMvzJ|5rbi)viPPv;O~nE34Y#kmuc<toy0=lO@?#@O`RM*w2oK@>;52*w0$Qe$+&=E8#?HF4;IZmx`0!2IJHQvj4yh)LUdR_!jjJ*|qQ;Y7N;KxQ5ClI}7GgQ_1SXsnn%p+d@7srD~Eb3Hhu^_9@xD@Kb6w+4XQXHInQCIFf2bb{cF&RV1qkD^j~WKl>fZYpD-BKl>4WK&>PD8m^;q$-aWQ)U#w?!e^;@WIw=p)GD&y;411}vKk?u?^0XIP6_$kO7^$sXXo>8f0La~b{#yO8bo$C97Nquc4KlMJ({c`l=w9GJU$Jd0-wXD;P=93@q6(b;3N1A_+&T<pNtQL1Mq?PImv1So5BHjQ@jHuo((7A+4#fo5&U8N75FUv3cd<Hhp)m{!{_nU`0Mad{B`_Qcq9HQ{#deZg2UjA_%OT+9D;YjPol(|!)bVP{9HH%KNrt{_u?7&V0Z&Q7#{>D<Ad;ya3J0hZwAl7o8c#>?8_4=@n4he@S~8=?NIXVycYijHpQjHtB`fTtKi2_;+Mc|{1W_n_%MDw{tSEte+FL(SK%x1x8Z91ZTwyMI{q&HK718_A72L_!`I<2giTv{ffApdtjpke@Fx5`yagPFx4=(^UGS6f-$Oo6!llHwg!~fU37g|m;)mh6xRm&@WEuFecnvrhuYp&GgYfEjHP{iahF68n@T&N4A)hDWQsO(Hw6h(Q_@<C)i<>C%Rmpk|z63wQU&2?y?f6Q31^fkHfybe=*Ep}mKZM8NQsN(k{1UIszh8n^#{0wT@&5QM_zXS^p9fds^Y9h$ZF~j35x$FW#6N)V;~(Jf!FBk1_*(b^z80Skr{nYS`@*KJ-$#iLO;#;f8(xOj#_PcI@H%*D$Y%>&N_-bQ8J80O49fBF86{o>x8Ozi^U2DAFT*YP7LJ*hSw{E<+==hx_<4h6gzMm8TqwuVI+hW>4kdpb*1&W4_fMeYpTO#P4*$LxO1>FZ!*lrekD=rr!>V`=|GpMVz83yQo&(pw-|*i!CfBfxa5db4@8I}c%`(CTa1*|XV|4+`2y@{oT#xNsmdQ;iH-DTGe=KF0$0+ef;Y;|V_#<#7{s{gsT!BA~KLq3WL->R6L;OMf0r&y_0Iu^I@%N$h7do#IuS6fxKWyeT;{D*Pu$kA0PlWTrW?myc7p@4Kd5w4+ZVa1wjra!mLD<Y|#NUGNh0VN1{2jP9Z00rMYvBB_nb(Nt!u!HzUL!sg4h@@mjrgT0eTvR&#C0Ac{2bQ8rNqC0wQ(u&^{@^uC0-1r-zlcV--NsHH}O~CXZS1l3$O@(0iO?_$F)BaFG<c9HYcl$68{;#kN=EshY5T;z5{-U@4$D$Pw<`iA-D%Wgdc%_;79P|Lp~dXe3ue$ldOy2#jpW>F@7#3UKh%H)#bJLFZ`W7_%HYt_zAuR-v~d%H{wMwffwPg!}sym@wIR>z7}5(OYrsh$I1E$mckOe6tB%bEyJb6n}z%muLpm|rNryN?YNY92=2h8#KUkWE+t+89>S%>kAp{WDe?MH_G^7gyftitx5h6_+4mPx;-ix_6HbR0;nVS(;Kle&_*i%@J{BKCiMNGy@wRwnDD9>)uf_M$mbTz~@sHp}{3HBLScJcczW`syU%;P-Yw_pt=iqw$IeZQL7+-_Gm(sT0qr|`UWQY5#1%JY&#7}^wxRiKPDDAH)CEf!z!+YREDe<1L9^Mo01?%9w@N-}YKL>9P!+3MN1+0L#z+1xO@RoQ-SRe0*_lB+U-gqB)A>Icc0Y~E_@EcRw?v0fA9m#qUJ`HE$PvdjpbbKy858i~&!=Hg;@n`Tka11^Ne~J>%gl+Lm{7hIGKNGJ6rQKKJwfJt1g^%#v_y+hUz5#y&zJR}h&xg<B^YJI)bNG|^GjI+5489t^hp)zq;kS4(zAfe0*v4z|f0Aed&w!GjL5X*OweSvj6rO-b@$RrG-W?wTd*DOx$#5t>8UIhnKj#bo3y0#uo_G$t0rtd&z3?131@^*)=ioVT7(53THpg?|Ww1FeY=P&%%V7&#*b>iySHPCIup^!Whr^Dzus5Cqr^4R2un(RCr@=nBa0H$MV{im6yb;fVS~sTf4riIW;2pU33wN=M@Co=No&)Do;xE7_LuPy^{tA3LWX6-?Z^F4DGyW7WhVw#ZyehsPJ`*zITk$X8oRAq0i+>KE3Yqb<xZW2KpA9oZ=DvXVNO)$*+!qjU1uKQjeF5=`Q2H9ZFCe~){%3<{?hA;20N?P;eF5=xaK2~m3y9~!Cp~jtK>S(wjA!l(h|hzoJ#$|`d=)JA%zXjzci}eA+!qkv3jguUeF5>mJ<}iQeF1U34<H;2o8W`-40r~ffnN$c;FsdrFp6j6lVEpz5`G&Tg5QSU4kzQc<9EXU;M$jo-_PfH01ghBIj{JGFe7B<$l?#dOG9Q(E&edf4w*T)_#<#q$jsTrABDGt%p70*F?f5(ToVv~9NvlF$!8I7FKs=!pI)S{B>N6tNp%YQ*^5wKOKl1J*;crP+DrB$+)EuHD}_g>Di!?9gYsIcP6a=!1nW>IkcHq0)Ny2GVV}oQRmpw|`>aa#2iZ3G2epsvCAg3Jl<fPE&rhk&WM_wbb|xD|_O$176!ntlXLrDtsGG>HhBr}{kzE2Wqq>uIg59asWX)h}>O`{B;EB|+WcA>&RAsW`U}Y*qb^;7hmB=En5><n&DXc*?B0Cp0qFRylhpnh6*;Oz~4I_)eVbpZ8r{HwzMY0mvZ^`<I65j!T$9Ld+;6L~t{2;7Y!S{psFYxcM?^5DFz{B_t_-^<ez8l{Tzs0xXA13Q^_!|5ce+}P6iSLBp;XCnP;bHt&ymAGff8&+;EH$8fwi=XpZ7AEKHm}8xg}>uc;>W=6aVhcN$V%|v@LkFJ7%qe*_(J>&_z`{uzAxmL_z1Ec_y~Lv+=DN|KY<7FPw+3{FZh@EH}D7i8~h8n8~*~|47cN(@jUn;o`(-l+4sXK@x95<cXP<+t5EV+c`d#hzJ^PQpF*|?KLzhbiGK!n;-BIB;jj39{7)$D=1*RWSEDV}z^mcM!`k@qcmsGW-T<!)kHPEW)uFVT>bw^Ji?*~2{|i5m(zXsz;-4q$0(dI?7(W%?6Y{wbmlA&sUV%%A-vXsA-a?7Dqr`88(k^f1wRj#}giDDZfS=$};-`^)iJyk|fZyOf@b2&nygMF+oAD?ffq8fY-yiZh9G4Pb2&G*vq{L^0OxvA7iJv9g!Si_xuW!bW!5hL?@rHOOxEt?;_l45F`|?_R9PEZmiC-1+OS~)p{u$mC{|fHMzrufpf8symVU7oB_hCxBCOjUmiPwV-@OpSdSQl@I*N4^d`gkoU?Y<VT#Vf!AxRm%Ivd{5D_}3}N#@Cei`N_IE<a0c{0GAT)2T#SN#5+SdemYa)jo@o|BfJW{1+Rkd_k6a)rNlQS8TWjC2POXw-ipWh_iDVByc++WhsXK%lX#tn=W*<v#4^J3czpmD%5iue%Lp&w-z2{T_P}Ks;RKeGd;;u_%QC`iSx)k6VHB5Tgx9c~<k!FmF3Sk}vz+Ap;eK*iM%abd`|<r8&s|tXcp|SC;tM&pPh=TkRbJ1)XK<WXWf|cCcowex!U6V|@GZCxkHck@cp=<}7vcp_`ji4*i!X)^aVhaU*a?>se+~A<rNm!><8UeQ1@J0dN?hk+;#czT(%0x*OuQ5Q&sSkH7ZcwCe-4|unD|~OeT~k=#E-z570g_$CUdWv^ffvctH<1{9(|3@#TqjAYDizBbFuo&z3S7~=v=H8bFW(TH98loz<f+7eT~k=#P`9k!)7if{wX{^Z02I(om2WFor{U<+)MZ}yc(Ahe-)0$rNkG)ez=tQBG?(163>T?a4GR6unI0Ez7$HIwUiQH4maW2mx*^yR$FObl=ykD34R`a4m<@v2X6-(;_dL3@Kn4d-X5NTx5qoev+$01SJ(ybiuX&_rEnnZf)B(mq{KVGv+xf1>F^Bvbi6J+6|aleferCGcy)LRULCIuo8Yza<6&F;c)T&}j5o&5PF5c{0CvU);2E$lo`GLOi4TG2;Y092@Em*)ei3YkUxfF9E%9FX1+YDS0p1&S#Czix!>;(n_+Z!%AB+!8+4n;!@oSSc8BT<k;uG=la3DS&&x9A^nfM4wyeI5{_r%-4)A2U=$*?YdGF}VT!E51FV0F9-UJ=&DE8@q%<MCtgny@im6F&)_jh}>{>6x~5CMDh@S;OII*ashtkAnm7arkvG1HTTR1h2s-;dfKwH^3qI4fyqN5Pm&A0bYbpz{kK|_!xX7yZ|4GUkQ8TSK_1K#rP<EEF6rF#k1g0JPXf;*W%gu6wkEXDU|p<$$At%2q)tY;`hRd_`Ud@a6En|ek;txZ^dtcBk)`BX_WXCuqS>6-VL_FyWuV1$#@IA0jz~Lz^lP3cs0BNtcX{@J$Q^~{u2+wns^wm3QxkT;`QN~czwJ%?14AO&-cu+aXuw}d9tR$o8fT$W_$)5jnBYm!g2Uad=|V8pM^gFC*cp^kHEX}NAMiaKj#Y{gLmV?8}K-M2;P7TugBx?K6pJYoPfvSU2p;}9D~Q<ZEy@O9Er!_?QkS6yb_PY8{w6>a1<Vg|AC`$;aEHl{|m?B!Yn)v{|B>hVKyFz_rq*lI0cWxhv5`lcn=<jkHdR#?H3+r8Q~M~Q9KTpQ{qeEqn;TbiZ6i=dS*N+o)7Q!%=lA$5xmng<5ls6@K(=^Z^d7Qw|HheEdDZ_=9%%cxZcYUzX@L9nR^-Hm%(nHxtAf{9k%eyy$tczuz_dpWr&{$t9j;LhWN3tf@kh!h*yT5XYOUle<2w5%)JcpO0cSD?q!JAfb~6dFGIW$Z0?zR8RD(r`JTC#As&U7d*)t-_%P4(M|v+qT<={77r?2WnLmoZ0&n)rd{g{2IKwmZQ}H}F(=+o~@x^eKXXd}+1@HmS%$LOr;Uk`zUyCn;Ik@&^;`zx9Ju6xFQSXHO>>KzF6$<-VT_~@mE(-hEneZa&e`KTJ|EQ<P#>1zmrDQYUQffWfEpR>cCfUvKP3jG@tKl2eVzQBNG4(iEOZYf-E7@`IR;nl2mm!}$sj`rtErMlKg6w}VLES@^1@EB-kadLvs8h*KhNn`0dVW@&f0NfzUwD4@EBu1&ZO_lXhi_9W$UcQDs5xYx!8z1yvd`gcYA)G9IG0*Ub{MXt-XS|S<ntZs8?s2q=Qm`3d4AT7fBTE9G1)}em>Nhn3l602BO9IEcmGXR8%jJAK7eQ96W|m01pE#-8@~ge37^Dg;&;La@jLM>co&|9kA+v^WAXOMY6#DOSK(*iXH(+W!MpJ5@Q2`o_(S;1@Jak-yb#XD3-KlJ3494&03W~$@CER{_yYWXI2yknzb09&VPiNNZ;YP++u$eQ2Sa{|*CWfs>*1%v3Ha%FTX+ZF7Viyb;=S=c@J_rBej&`lFT~ryv3NVY32cuy!5gIP`v#Qw&&kjCcF1Q5l)Qx3;)mcFxRiJWva|6DctuLQFT4)#i{Aqu!tcT7z?bnk_;Of?FUJ#b37)`<VF6x@7r_O15uOk4$Mf+VcnzL|-ySw?>vl@KSF(<TeEtDj<5J>3z{a?g_}B0RTuOWcl(x8m5-*^{H$rKb8+k3h6`qbuiT?=O;!@&&!rr))_+PLOE+zgqybzZX{|C0irNlk5Cb)<H6!O^smlFRLO1u1)5`QaX+U{GFcww@hg)hRl@fY!>umoR<FN25hW%zO^?Rz<|#ovP!aVhb4Lw<>e`S-qf7{3_agI|o_4d>u@<4?oo_|y2ZWDV*U3fHY*eoUj@f;Fvv>YLn#ef=@6{wL3dCP$y+rc9f_uWPvfPy1&$QvaWA`g!I@IR^Es^zRrvocy0mQg4wNsrP>XEejJA'

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
