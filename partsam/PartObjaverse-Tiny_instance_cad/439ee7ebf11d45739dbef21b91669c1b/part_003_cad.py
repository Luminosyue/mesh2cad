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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_003.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_003.stl', 'source_sha256': '044a6d2f4f7c7808c32aabbc5bef5928f11f0c3160e75bdefb189b69bd2890f4', 'input_faces': 1100, 'input_vertices': 665, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16746827960014343, -0.2909664511680603, -0.26579737663269043], [0.12477855384349823, 0.015641681849956512, -0.09099867194890976]]}
GEOMETRY_BASE85 = 'c$}r31(eoC`}VVVfl}O|fn{0TT>~wPyHi@SxGhjz76`6OahDWIf#NKSOK{f~DNqQ|;uN>i!aw(1SIV>W|DE%l@8do9xqi>J^UO>p$z(D!&)a%6<Hk#^;a@f_!-(UvE>_SqiKJR;t#7-Yy*ssO*Q-Fc9s`23<jR+SzD}#txOTnfL0VsJP-xqBz1s8)Eu)8)YhNlfpB~!2d(YlI!@ITW-m`5x@x#Kq_G;((y*h^XXy<*-RiZ@ke0tH``Sij1|Kq>JUKN}<-4E;*eYSUpsC}@`W>LL<xblr-$+xJ#)7SoPrhMz=v0X~(8y8C{-(0c53G}s%g^|AX!Dy9kLrvvd4GO{^J~fuF7s#c2ExcuHe@{x(v;2+?qAv5d-#y=tdN$ar%J=KvWP|dp)Nj_R^b1<3<FKEvRlYXri#37y=%<$>eWNKVy>lbiR`q$&GUR{x{c837@cL+vmEXhPlW=ulKGvAI$S2+YRjQm6RaAPtM{ngjT65IDPzlveW@I;{uTls3`R#eHGyJK^RC=vPLzUis*%s-t)L)Nw?zCI|J#H(c|9&_8>|d$$PLHqPuNtn7*S@%Or>al8YN*fV>B`qX8K=&tmfV2<c%-Vo88;k$?Xt+H_yKjD7?11hQ=gj`NBZ(@SE~F^B}V$!Mc@}sqUvMr`&-pV>zNz=v`sk9D>YR<nj3=Ss#QakYm7J5ak<yvYp-y<=?!Y2+}xQ^pUeeRxmtpE>hE@zM9Q~$9lFs~RC>MSO_Vb*2JN466F%R#q|`~#TlvnSWAIy^QEFZ;rLHTZUpeHH@Cg3C`iwd*x6BUp*<LmX>HGIOq|*7<|C1i@6WvESDf26JAH&zW&5V^^zw>5qU^}~0%i!;)A1GgIlvQ0%ZlcnM(0;d&zSK!|{KoNu%C{?=hR=3zI_U6o?o+-~@{YQ{+$Y(P{{aWbIcJmd^|&dN?-bdod^^{KgDU;iR;u1c<ObYtrGHeubppp@ZC#Ce9xkf#(b^?d`Do2n!VgW4{OWyz`V6-4IrsD<>hJ!2^mBLR>&BK?zEP<w()aI-^5#8M<!dcW_}hNM@f1&j^YZ#@)U(rGl=u5Pw9Asl@PB_AD}Osre&xIUs~%N)faj%mc6@Kk5p`aiV@D6G&sJvm$p)+QqCG#YeC=oo_}kB_^WtobR=)maBDC|-XmwtU(oxEH|9rnkeQp(oe)QBf99O=#%D4Y)hkUI^`2O2BNI#*uN^iR>aDL{zQogx63DV6l)%Wa#&y{b5o!qGM`F<VpyYN)`PM0OhH#RJSpY0UV&n|)M_eoLYvuwBWwav9vdTZ)A)IWMF(r+_VJ&bg`ULJ2m{*~+C^LGoBnocy1Yf9o{f$gl_8moN0ZYP|VXTPEypAJX<j}NN*+syt@olnyoiuzo>fc{{`C7k~x{gA$UzZms-)i{-(d#gLr|8-2AN4?O4SiZ6A2%Zy(|2l&DbwK^M#=&(lu&VNnLhX>x{f+88>dr*vn-M1Rsc-@3{qSMsTR9pi-+hkz)_pQtwS)7l9`ad|3hmr83DTdc4u8jl7~Ic?;BPL6`aI|ff8znvC!{pa`|wEge?5n*^I|?PiTdn|#&wnCJnrj#C6Ir~cQ_B(#-hEa6-T>8-B9gdhL%?MfmOID>OXOx%18g})}cV(Z%?~!#aQXJLeVN8>p*$jPv!H+YBw#zIULuOJgCPDT<=ct324s@IZ>aC3D93Yse*cL35GxPS3GZOq(lB8`kui1RI_U;-+Yl3?Qr^A)z4e@UbGwif9rXr5z_C^g7htW;<@za^233?Uw>oCd0ao!GV}Uz)O}&*zZlzpuuzq&U)qdvi)6&{7Ds<%WT*xIw-m9iA8SocRUbQNLLAqo0eGIWT>U^ir0<9Ef|+3-`lab{;agMHbz&vYj`j&Xhv&i4(dzosLxNO#qu42oFAAJRc@s9FKfUkZJUwft&b!<AIMT<9!T9CH612<0{>ZQAdieiTM!$69I?}IQ1%Jzs<EnhWU(GWf{+MmJKEM18`IQ)n_RY`(<HS5=)$uwVx}rW^w&Hn`KU~$<`Ju!An%=fdj03iPkL%}7CZw<13ggs!chOFt&cb!u5#uZ)ayiDKKZfHv+*KLnUR<l%Uw^;-D9$&0{m0w5f9D3H{h}(N+&LA|F88zGe5Ede^n*S@f3-I^(r+k;c6hS{<L=G%aQzG`fb-&yXVUzPdg}R5|Cy_CJ*?lSe7&@e{BPXFb9X~pTn|+;BA+SwRk?bq5~zPz5Uz&-r`7dlCQhpQV>^w8cIbBq{p8%@$~Q_~$9OaCV?6IRn##ALmnz>rvl#gn$bjd-{Gk}f^^H{L-THYn#vdm-AfJm{)b(j}ibVb)A<DNhJ;w7W@eJkbi!vdfvD<Jz&YF$$*z_{)|EwXn?{=?4`m<*+9*X!A_s!Qa$~W&Fz<pJ93&xds&ZFH9?m~ZE><H@DGz#hCZbSa#a9!&UuOk1<Yjy>;kCr&AIzIE~MaZAyG52a*_{rxXpGz+>eoI<J`38M^Y>AUfd0!Z=h5Gcyc+~v00oo@^B+9+p5baPrr}DLlt#JOj1mn7T_a*AtvI^2?*sj`H%T`>KtN&FQ<<1?9b{vgyt8p_k(oegA=lku7IB&}ysrLr$)5I7*tf_%~R^WZY8TL$Fhj!Dn%6FH;H%6?-_13;4p7ZYq?nJwcML#fX9q!k{ZIC`HzUn8<30=`XO-sS=_;#IAvjNIo9g6zQ_yXhbLw(?n)scU{OsYM#PId9z9`~m@PyV>tX&3i|(#1D+1fCcBQ9R|l&3}Q<_YSA;QykZWU3mZLxDNMYtIH_&`by;6VkgEM6JDVHvlrn0dCYN^zDxO9@0rN|)MZ@fLC=xC;|S#c#a|eovs}GYC*_;Ne#5x+!~*2AtQPWleg*wN%A2^}vZp|OR?k=MX3aURe0zREv_l^a*Z;!~IKN#VZdc`8+KBVwTvPY2ed{LtG#zjrdpAaX_FhrGTYm<|8^P64?)wYMHy;0q_sSxx;V0dSeDoJ+-`N%LJb6A<`R1birvk5k-*;=j#PwXV7W<D-qz~DQaR{$Zw^9<6+o>7G%}bNvcw4;RrqXqe!uYe@6ZBUP?<(KaTd8uLcj<7Q9KNA^`~5RjPd#H=jMGX@M?U}TQrDGp<Q0y4(g>uVUk&5tQf1I@bdFTMyQ%=j{d>#8A6WtEdt#ie*D8<uI=CF_b7HY7*W~+=@lz_~!~Vherxl(jr|+ow3Ab(vRe!hMA2>huN#&d8YM?*a*BR&W#ZIJuQ4{&hYa84D$HMdSL>$y-^;+fIW<Hg_zW)@?L(SF7*LOXMRZl0*BIJ{!s7i0Oa`wmajh8CDHvS#P|HZ~A-*}neH16LLxURDnM7c42@EkcGgYj72<jQwKgH?JfcM-f7+z7%v&6^PA8^4AipJDIueA>|u>HU6n-X7fN1rws*w1%ntwT&^Dr^%KF=l4b!#<#~;pufJiL>-s**+#VUo|zaQKVF67?X?en*{E3gXvxBH9+UJ!`d@3HA2izHxpTQ0{0`ypbJxc4p2ED59n}T(Tu>6}S60CMQ<KK(xSU3{Fn+vK8ueUzEmr#*tqUpNsNVcE&hIyPuda|A{@d@+KJ`|q`^RdM1@)PE72}dk_fenjDR5jFZeko+{|f3;GcoE@r#0F?>|3;doWJoNUw0PDU6ly^Abm4w542B6e~eSUe}nh$9d~fv`<=u%C-N!Y3ti-6g=9kic=kH_iIJ1={F;ODi8jPRJ_)Dc`?vGsdVa73<>s1>^Udd`xnu^ei>!lG{@Sd;XrH>hF+Sb!J;vqp&m#Z45jd`Vt5kY(?m;{+k90=4C6c55zc0q~cWE2tJHM^Qbv`8(#yx$iBmWC&(2w7EhH^TUz;RW`j{a-;JG}2CDu#R>Z$NvV-m3C3Z{~x~=b9aoSe<`kcL>@o^BbJcG4YjeejSW<&~&s<w;xc?zjdS!E2Hw)r$yoUkR}cMO-C^Qw&yQ(-puHf@R$CKcHsSG=Klo8l`R|EdB^-?fxdZS4#x59hxO&}H>uBjZW^~9pnuB#5`NUL7}xE(rF@;fU3D$Sr}WMF50tOPd99wCc9LsI|Lg5dXs4EVu7$-#y<%MDTW>DKs=smTu=0&#zu|nX!~C;0>LBXV6!SFB^FyfT`yI&VKpyq{HLk8hxtrD~-_2MX#~<%^+%L~oz`ud_Z96g%&i|>!D0hH^>%0@*FP+;nalCpHTz}7=<N6vn4CRKWz`WwYIk=y;)<8SNY{mW9FAw^MgL#p@%PKWrYV{g`dK%f0|CNonkA_Y|Kh!KO>bYVz-Us+x(2^%Y`U+c+e&$cgch<y5`z#-gerH)2>a*mjI<M}ybGR-!Po?#`i1WQY37+E}bE7^T4k+KLPzB?{bXkzk&W*^Y`cWKz@8hV~pYt&fa(5@*A6o~Z|IRyG`R2JwX!nB2(a!oPjDtIWb|&!r+HVIVeaR|F9~O%7Sp5jRKetR3E4`JiA?n$B=VFyU=W9IQ%2dVpuUQ!GuhkeQ`@VK(C&m-6j$nMTu{``T%W=Mf3*b3hHVyLGbqDW(S{IC?ro=;i#vEFrzSp!2+U?|f+$X~y;r@y{6#YlFml&@PU5|OOM^PAmmAi@Yed%0h0<V8}z*XhzOCBSiEpsvMN`D3UPsV(KouaGC$4+`g`SzUpI8SzI%;#)bhV%s&pkI5v8SRj4mh#=1E0BN7L%1(<PC)uHYjIzk`xWVvw?jP_51Xd^ZWT|&@>9&3s`Ryi@%*(KINlby)p6-nv*5jG_iEKII0N%2-!{kNy`R2Wv>e{gujj_Nrt}XOfB#(*^<P#@`BwB?q)+q>`eoL~at6V_GX?1jmq0$P24EfQ>uKm$wfneE`$u4YT)+2~`aH=(J3MKF{ww26<a0F*@(-?s`b^{eTI)w>pS{&_Tov2LI*-=r*XljWzVjC8pMHn@yS;=zXFJA?(=k76EE%{VuzjqWD>1*mJ~z^L>5T7}+=qVPm)&@;xHJjZZHW%JzEW&o7ufz<;Y>K*wOf?$?#hYlmCtwWVKm<Bg14&lj(>kuUZQ;G?h2eQYn*zov+~u1@2^88s*mS(=P;DZ=bg2+4*cKC!S|nEQ>vl9^9rE;^LOL^yJlcKRXSg+a-Dp|FdyA76!ql$niao1@~7|cdF1<610Cu4JhJkYM*5M7P@i6yr`N9JL;CCqP@k76@Eqxv1@&pL9qX6%UgG_vPC7pSYb)QncJwFp`PD<b$GphC7S~NByq^@h34aFO$Bd3!(Z38jgz><k^U8NZA1L3=gX==iigiJY>kE47ACS)%oz?`lk9IpH*2VH;J=IuQ1pQLYQOGABe7ocpd_T<|+&BFns&!K*^Oxuk&-BFe;nr#8Tkq3ie!pQUjJv}RA^p9U7%yt+@xEAo64qbSe}?y|?Pu{^?%r4Vet%^RIfCax(|TCP-E724uT{!}a?d23rF{KHY=2|f8A>y5L;hbJRO^&}|LNXoiRYRgrF^^aS<GX`{G`&mT}xs;`1ScF>T{L7=&!oKx0B6BKfm*9lsoX2dQR&d^I;tRTPX6$c>wF3wW{?{{<-_;568{GbG<pvi#w(~&hv!A$fwFn<P&ii{Zgsq$R~Bwx9am)yzd&v4y)_Q*&2m$(SrFnj&!}0Z(K}vHt;^xa_w57v>JT#PO!R9?Zq3F@1BUj`}x6lcpm-zX{_|dr`Iu#D{*w0%D2>V)PGea%)dU|u6%uAh&q1j@*_O=&&^mCtK8E)aesuRK|bk2asSS0jrXqxqn4_CUdEu`D{}zt5!O@r&gM^5K3e+5m?yS#sq5HUz6|*+Nr(64E5XV)=1j!>{AL)Qca<lraex(yd<;D!=HvewrhKP&6Xn}%H={rT<r_sCDc{QQ8{UrwuKQkn_Q&&^PhcE60KPH2fl9Aen2Y(RO)Hh}WJ15^bUcRig%-n)LBD4j2heZanTCA)e(%T*^fRr;E8m}wavp6#zeL~3xyA|f4SN*w;XIX-HU`&A#z^?=$IO&?Z*xvZDBq2G#C6LR$Um}{^7WnPF;1;L6ZyND(GIOo;d&e%f&6DCLq4BA$9Wow_j`N%TU(`H-2(0Yx(m|Bf2w?K>?n*&TXaBu-dt6_^TTcQd(&DXeThrRC%itchs4)V-y2($uP@(@eJBa4qTETdkWZ797zeUHx1-=&V{>90k~Sy$q4C`pseG5*k5c6oZh?MrEPVHDDfCMfcfs#i0_m?`9;5Vf2>Qvo$(3)eD~W!i5c1LV{R;!@Zw()ac1^ur`S$WR7<cVUhIxXg{gm&<!~OuH_b0fnPgPL9Gp!5eLG~rV`6`!vVc>PH@7a!do{V=FsPDBJg!vu+IY|HC_xgJC(0@+9rhIdG2<DIaq{4ZL+^T$+>r=*&qR3}?9^@bO?SP7su3Z}RlPg=#SNTlD_}JL)pkM77SNYbv5>b*~OJkv*taEf8?sMGNR-sMUzp&}-+`x7-x@nkqzt=?h=HMKtcbCQJ$0lT&t?Ick8tr(wJ;p^Bvd>gHD=G3hTNKaFums9C&eX$o^+k7#ucoY1&lM*T`V%*4GK|+M=2gBnEdu#ui@^GB?)XUGwg>#=SPyfC?wzjm+OSytj2#^Yzj}Z4llRwPUU=(}X@U7`oettUf0IV}#_JH(K1S$5tnZ&IJw<&l4$|vpDy+XnOqv{cTxRRNIIilAmG6xC5&dVLba-ypdO9&MA14y~w(Jy-$K$?YyTuH~I@o{>qhqBnHXQ3SlZuZDEY~XV0`I|-Hx7+e&)$nr&o36XROwp9n=IFZ`633_gF)ZjI!t_>?^9Y?_*!IXb>A8POvL?F0=`kGEBf_MzQX-dgg*N#w~h_JAbs|S){>*}^D%$+w_4c4Siaw{Y7uwg=cUhn+xYwm{M_*W?f*w;7?<UwUw9GP$A4baH=bj^pZ0Scqz_?w|9LU<4e}4B&;I}4dS++4^_igZcR!6ne%augWzJ$A&_7=KR;`D)&aPvA#e1+T-@bhp{rRPp@IPn!Oc;pz=jiSP`u6*N=+D>9i<REtK03#5|ExUTW<R5!Uo!=M7W$(`;r{Q^B$lr`)iIt+(k_<o6r7H6N%lzinR#5n-EjR!@7NpYyT8@o`gfvO>Gd`vaX&mR7|S=eB*FfW&0oUL#Cq~NcaOh8J7r{jc)!>~=A&L2Sf5u*asO^J4h8!9mwWKu)hiCJ=k&~{1MYY88TT*IxB5>&|C^@9(Li6Hz5(wKNmm?;<(JEje)8hO<AJ{a{%F@riE;Sr7lSHl|Gj_Bp)n&WYX9vA^q?N&l+XUeW`AN=y)iB@AHV-GbJUuk(z74X*k8HklSwK)`!}8ao9XWTPW=D$hn-ib{=)A+4fdZ}iI6GEXMgM8UryU^;eXUWTamM-1m>@^KX<C7nyS)&)c<S$betM^T>m~VCXG_Q|9sK;d@+uUnJ)gv&m${z-%RoS=a<gsml08XmiQk(@2q(FXRG}Ad^Gud)LI`<{>RT*Yir0{RqjX6Yo|tK<$wHq*Ur>b{(r^;O&Tlz<MD&`e5CUI@rK6nhL&Wd^8N9N$?=J?{1WQ(@p$HVs(Gqhj(==_{Bu6%yufzw$4gp*Uds2!R}RNlhH+N;{y0tJIL$gcWr50v<2}tE?`c<+|M9p{3r@E%uv~wfsjbkJ?~h9zj!P{kO!*&=V~yj@kq^hc2FJZxr*X>vc$}=QeXIPB$J^S~s*6;5j?Z;}eEvK_`Tq0B<~ZNbhAIE!_XUUkf8G~Hk4HXyez}M7-eII)hV*>y7<^B0R_ufS(R+>d6MX;u$m08vQSb!v=lhYy_akFmNn81R&oce@tj5vG_utF>``0xO+JV=b&i6RGRO9beK78+UU*o;c-t~?0{r5zh?}_gBOO~ko`CjR!!+WLEW4rSG_fUuLq1NKCr7At&TW!9#>d%iU|KImzzUSK29xC5|FE;sJY)pBJeE1&i@IBgWT5(xmJ{sS<E$5!{{r7Z-@9D;fN3qiDe6QDf{;*uN1Lpxuzu&w2PWk@4fx&qLXGMn<s-B#GusHvqEjy-sf4;)ue1&r^-A^h#=RGXWd+3KcD&L<caX3%n4%!8u^DPGFTkP<^mG95bIGmp`qlc|j={f(SasJ0Xx=i{0e38ldBE98)<@@tXetLb!Yvo&<k8<Cq!@NSJIIC3qaQ@2R{FVN5R^?lq@3J`GrH}2ce1Cq-=KPr6dXe(|c{cYJ=Gn{v2arGK<uuOA>3<|$jq4Wkcn;_B+~^$2*EsKIa^BBP)f_(O2`$bO>T4b--{yRy!}&(Nb>%fG{YUeYCVi(T<}=;PeE)s_E&L$Nf0~^CbgNqMPsW}{)vLj`IFIW0|N6;sYXaNBpO1AXPeOhC{^Tm=Z_Vs0kq`S5jq|<wlfCfSpBS7U*83e-zVXp~vhMa<8(6Nv`DgRh0_FSj)&BKw4_>Bxe|}rz{I+SVQocVQ?iS*F_`w+E`}5}-=g%$Y%k`@LIbO0j-|p0#rhI>X-sJqeo%yp3Dm~}(ZO-RwLsG!!{J+8Zf3tgQ<@@Ue?tZQp6zQORe|^E=`hp%b6!~yHLgRXboph@5{dEoZ{XL9Bx=mNUzYd~v9mEKahR<~qHv;P>`t2Pkm+LG#*IAsd2R8&Buf_Emm%hJVqj9~)o!BNiu$`SStos<hEK$C{u4MY_N?A52-(QEa{B@{y4$^boO5?hfx$Sy1+8OIy?xNEC-N19C_xla5i#cQ8DBoX4v$&3C*L<gZzhBb)eeW-mZB)lQ1nYF}pIE1J2BlZNzpiI-UC+IfU-|y}pw0C`JG_bV{q;o6Ur)T<3hB8nY541s)mx+7+gO*hxGrhG8>M`I-Sgk)<MNrP57$ZEDp)7gPb@&WTvz=!{l#@i&vjV00M=pMc`@+0ZmV<M*6w^l`8L;iHLmkIsjs3wTo*RDE^O*gP%hVz-40ksHtQvcQTcG)S@YMOTV_?h#dT_p>(us6UHK;0wJok|8wm;`AFhL&{yKQw@<`8hbIV^hKh#e7&c>}=AHw>(8#-6{2G{E?f4zRjTI9p^edj6G_qE9F%GbCbz~FuWyUiighx-b2?kljTUB_{8e}cvR3D#(BlREF*|6p<dgHb)c@-4rA=6(tHWHRL&+;^dKe}#4mzRCVsqi<}=i1ggQp>h9)9b5?cvmbUH>>IIGlvcjK&%~XIeJ0Kc1L@g6>)fy6Os<0b{qY|6w`ei7l<)6{(YYVSNn2O>Huuk%+&^PvZ>@ayJoei-*RkJ5ZxD%cxj)DB_vc(31)uwT+&S3iqt#!7`g6aKGZXuToVBSpt9ItTCMO5>H5sq7E8pKArE!0h{%uX=YuuM*a$lA`qk-~m?&C7JkIQV<6!~!9m&JWw&Yh*ocXjSt`xN`l%x-H@AMQ^x{QYSI_acApXLFKaKbyPvbgX<V?te2oW!$FxPS`(bbKj2fC|LO#_ggwYV85ktqq6dK?$2~@VSlC_ca8FG?&mbPpHn;Y3O@Idn%qa~O#2(<rpCTgrx*8~uFSq&T@T#9YCpjKRi|M)<y+6N4_4zoSnH2r%GbGXR^z@|GtGSEJC*TXV{xCYHGDnt;rK-3zFg<WEy{NvVIQx>eZ0n`{o4bte|J3g{W^0lC|~0~VVnDe?T(L-KYu@KvRq^RKk$FWK4g>okoA%Ycc^@L{hQpk>^3))Z%xPkXN&uv&8vfy?@Yu#YK{A--NxsU5BFm`?XVx)iAlUu<&zZqx^4ftFuAz$ovGLd?(eg85`6<dJ@%73I`)%Wa|bG4=l*k@`_HYT)0MArzq(rt`|gaWIVhL=+ckfG`_AZ{f$d;(pS*K@8}i}4dW-w&wIc^npT5|KZ-0V)_{O@k@W*1`zWV_C_KjW_kU#hNo80H`%(|+4gTD)~bK`db+R%F_m%k%0_&Wk;b%|Z-y5;W?+?o76!az&;)&=~o!R?6OHE4glfu9Dyn{cA>y9w=L`rU!`|92nbye!H$_`3{^zst}{)mFaA-*Gr8@jDJ}eINMzorulfi5TZ1mG2J3?@e_6-o(kh5dKp9ZbjqoR-9TFP%eKL<0j?rVm`Z~e4D?cv2XKtG?7nG|IYY5j-4<3=<a&4eieW1W!7!Ui)os~Ct7N)eR#l6;>DDIzW(n&iSJbG|LQ04g$oxd^#Avp_{5(`Q+ttwA)J)@DOofbSu{O4DLE}Q3t2Q1Su_n<G&MOj%M*U&#XT>sGlXw4gnwfQUu6hiV+jAr5dMq$h`g1$h5Cs6h~;fz2ybHuJJg%xo2-XJJxCrLq-le^*h<|-{>_UUUTmjsBM+kvqHZJGUX1Z#5p^6n#EZIKWbvZ07n!|iK+QtV!ZgCQyr}8Lrwrkg)Gx^2d$HJyfz<xw!QSz-^`alO6<M?cdA*lzp%+`cnC-=UFTP_4&t(X&XUyk!=JPwkJDA4;>O%5Drdh!6&SHL|6UY--o^S^*rhCzjA>5WBJdL`VJdM19A$)>*oP2`(f+75zA^ePS%8Ng!$H;$>T`$g2k5G@1kC4|>PX)A<@JZ@3@-voul5w1AkF(zEsnY}U5uQrzKo*@so=RR%oe}We83FArI)pldJcQhrI)yxiWeDf<BDWWfyr}0zeJ?_(jmV9dCX^wZjGB;~$&0jJWMl}ZVhAUpCL<@~cat!L<1mE())2x$^m3DPv)(}r;euW?^rC<lUonJhQ}dH+lbi56UwV;;+JxMMY4R|H<1vJDPz#WAkn>U-l0_?%^O8TOmLPvl&dLxj%n)wI5N<)OOm0E`n%a>3HQA(oMK;N8yckXmr+!8Lift6m5dMbRggk)Sn%acigzeaxA>4`~+>%<5T#)CkB}2G5wGp{Fc_g(yc_eu#LwGQ?9$B;wc`$hpLwFdq23fQkc^G*VL)c;nR}YeTC}=inHF7oPm5m{sogo}dtwXNEx&||Zb5cXeqRGgjX~{Xs!PHCv`D9|5q8S6~kTIZc8F?H!IRisD1vM2}GzmEc`4fh)MvX%jm3vs@XW=&t;XfF{w;00Dsd8^W=V#&cLC}I^(L7|)c;sWu_ayZe`4;m!$q>FomG51m#v>oskk<+7N%Bd4?*v2mXNK^7s^oK@nu9DMoSa@>vgqez30M1&-eumR7s;Z(1eE(rKz)8;-H(&cdU1pLJM|axFU;$AhVX5wOTJBh%MgA?mAby8eohw6N|q4zzbh>HB@RNJl2U&s|IYG+lQL}@s(d#MLpT>hxDd54S+p6s5V<Ks*dKcc`(qN}4%8Op4&=VnugQJML#SrZhi9(v1Zo@d1oC%5ANpT^JSHq-shvR>Z_T4FAn&B^VhGRiVmx&cbsl*hzdMOKn>?FkO=1jZ9-`r7(Qn9pUq7BPfaN%>$4u%R@*JiSjvvQ6_i~L>KZygD5DsAo$7Kk=4MGUNrpot)uTWo7-;rOE-%zFOH~cL8H#G%WLijy3Gg(47h#{PfAzYLpT$q}IT$mh6jZcoxV-95q=ck5{^OLJHgmY2jl0}n~bCH7?IlZVw%}o{!BiAC=V+hw|2v_!^m>0#pC`~O#F2}!@W(ZfLhLOWqUPXp*UM~_-6EKA1QFD`Xv)=I-!Wu*PpCD*3Ihe;TEFt_?5JLDBH7+?Wuc=oI;hVgMj|SXR!iT6g$%n}2sc*?|dHtOaxGv8#gwK-CGLM}s;~@1A`4H0_WSWD#?{|<7P|uPNkPlO@kPnm3P+yYIkk3)ykk64_>fdCS{0H@Y(1&*=;b&C2H~e=iVgH>=*nbxjj>8bnPR&Nn#(OC{LpTpZxQrKHcu~oVaE7qS5dNB4hFpf<{hA?MpCMd_T9_=+Iv`DJeowS*Kt63*rf55IIJE<{9k~O!Gefu&L%2P)Ex9erYtImF!4R%MtwXNE`d6Tal11~AE09}ItCKsk9$gs19T~!HsO`z^`MoyO>f|o`PAi7+Hw@uM)HdWs<dW3tWYJt?(O|M@Epkb6BWk^XJnIFNTQ8tK!VMV0wW&49qLs<D$zL*r%TvpdMT?WmlS?p!i!g)>F@y_Ji;)YG3s6gw3y||sE0RU?lKuWPA0r{ZCz^;Xnm8cO!~x|dX1zp{l8aE2P?M6Akgo<Igntb}2>(V+Ois+Qg(ZY#F6{>SIyE6#Gyz#c_*xJ`_!2c9SyUtM_hPpf7pRxWqLStU(}?b42>(KrG`~>)p)dLuc`v{7GxZnpFHG|@(}?b22%o0@MHYQU7QIOpJxV@J-a~cBqB8^X7oJQVKo)IH7Hvh|%kM-{CzB^LO%&5a1+<UwL~1LtXiKtabMk(EXDoFhc_Pz{rH&+z<aruP-B142I|b*wIK&V>zz~k{Vt^Mtyy(ji{+1!!l_A`e+L_#x{3S!Ut`{S{7~#cShVV*;@C=6V5NZTDf_V&~b|!ab*+ZxU$PRTIbpUw)kH??K7M8i~t<*u(zU00<=0ObMUevDSUgU1nrsQtqMhxLEs9%zcQj1Z)Bo`x>qt+#tBZpBV$PsL>Fotj!>PT`SmRFcsj9iTQ7G?++X9$;|hLOXVUkQeA6^3wk>PWKaLUMQVWNHj~GI<?C_z3kJ`3U(T^;hyk@(YIWONQ_j>LKzK@?kIbQTI>}kwp)X_mFo|W5_$nn;F7usSC*qdHidsbIGDB$-7yPUDQ3~JuG7vLwE;uGkFJj6Ll?lE%V>RSjn`a+sUGP1M=A$P}W}7Yd3j6L--6s_%wAp`84?yL-;6lC0XJ;|1NqVApM1ad@cl(C48A7?5}MJ`)gjpzfsSV&$B##jZF9;btPGJ23d3n+3!b$6L^uzi}=(OWYN#a@yYSLsO?29FUl~4D=>sBQR|T_k*hL<8#07jQfrZ0k{dIGTTpA0zoyoq)+X0xo$4@zOEZLXQFD_;vyw$KlXH>NF@*hp!W=p%j!Vr-4)G$`i~J1XeAMLReB>Mq;cV1I<V4Ib8#OCAKfhm|AzYRrT!fl~oP*yh!VoS<%}UP7wkSv~LoUPfT98_aT##IZS~Vd5s;o<SYBg$AvS>qcHF7w$B{`hjks;iUA^a7!F<G<)`73g3hH!iB!*wI9*8RPx&JeE85N_Z_8!tL}QJLC++<<8+GlUB;g!3|l^H3|2b9xc#MM;KmDQX^a9;Povtxm4N@6@E0B9~&Cn$-H_8q{VC;U?7j<oZ0GCJf=`)J|kkliZx_r#G3m=r`nV*v8GMUz0`a1k|Sv>sW(al3JQ9nk%5Ka<TnH(~)zMrTwz=9O%@%<h*QCogw@=LpUQflpM-DGg39O{0kzB#v^AWe@^|3ESe&qtQ0IiJ2iubzBi$UepfUlIVJy|imH=!<|EwAtHifn{6JkoUhBnuFV--G?|HF~pYKxdk#Bo(%Zm-vjbzb2<PGHBOfR4BFodHS!o8@y$#<D<9W|O9&A+c>2=^rS45+_w4<46%?oRDNZtiu&S-ogU)ybltlUtI%@}e0v3-xny7V;x6&*fe$^Wq8h5m{8yJfZ63<^20k4B@9#Nh5sMJ7-0u4Lp6IL5l?;go{umO%diPd3B_=C%5O{J5r01ms6K9ggaA<k~@=&Q>9MDsgKDL!cQ2&OBupT7{WI7F4-n8qTV6<$GnIk{5?Z>F+=z%Rodk#KMR-gVim80uGH@2?)-aKrV(Aq5bi`RMJ~m5??f#^F2eTh#Awev+VdQ&q&^MEU-&Uq&h=wzR`M#Q`;+>Zyo$P(A$*@9oGA|UF<Dgd%)}6GN^MSVN*=%v9>@@mq_!lt<UJ6{5FQk8pA2FM_h$(AWe7K+W+68rXQawKlaZf=AM!q0Mt(?M$`I~C?M&`ME=es;7L{wXBtHw64nhb&<2AgL{EYmg7Yn>t?!`RnkK}peSq$Ns)TQL5ya#47gr_rvzoXjZ@5oWqMdU@i2cj6llNiDisf)>?KaeMq$1#K_cro6Ksb0)s2(M=duVx6ZqD~{PBL764LY~6Be_{wPqy9i%Mt((IOkT`;_!UFA4DW5Z56kd=>`oT#K`uis#}KYS?Mbdcu1M`g7VS;0NH!S4m8gBlo4gp|#b$<ZKWZ3Rv<kTjzt@l2hun|6nYxiIdMhA*;on)Ve7;QmoqU;`EDl2Wvp5Lhl+;^f(c5GR;Z$)D!l|iu$f9@262fVy_s9~$Y2zS-(^K!0@3VhO&wi;XIX$@{bpTnkAGsm9w-*z<80y7HYIm||53=aD<dNhN)Sl!K<WUUa@zmbr-Yj=KLwF)XcpP;Ac>w#+aSY)x4B@fVNOC0m&9MyO(bWFr(d6L_;bGLi<iTDHi6j3P1_<FkREumeZ69i1avySIY7=r}at3NfaysgRAZSLisPxef7{WhNmy(yVkN%M%96>EfF3Em5f+1Yii^w4CKdr?Ou1W1ru1WraTAus`IVD5*y@n8eO)X0<%W_}yIU&!3*L*JgNdA$}1L04Z?-~suyn-ratYBHM$*=j{71Raf6=Xjj;rR^V+0=RD+2pa*S>#!K-i&1kk7fvuqE07^en%cf9?lRRMvWp5BU{u-<Vk$qSPbDvhHxM1IPy3?8~QMWdoqN3Q>T!7llxPrkwvGH`;!MUgojeclZTSWFoZWUgrli*$kF5t)b-?z{9C#pgm7x=2C{_kXF&+zMAY?U(bZ%L;RHbl;rP^5WC`K8)St)_!vD})MizZV7M17aKh$z$iE_+Cv_jB_JS(tF(TYJI>QIq&6g9}Am4ZIhzf#bL<Eq3q5UoNM4Ga3vK4EOLbkwTUFmhG$XzB>^XmSj76It{!Ifi_ZD$mP{{4D&b7p16WsmaJ?$p-Z^vS>=OL9W6Ou1ZZs7EMjAO0GstL#{@yK}}1pL9R<pPZn)RZpi0WU20EqU2+ZTw*h&6%Q8iK1k|BNKs|f#m_)miyRy9^sAb6!<Ze`hZ18*CsNKn;L&@F95!49*c}`%NUCB`l;i=S-<f-K84B;8n5oFO(<Qe2y)bZq5<k<}2nbe77(Q)LN<Y^4yDbz7!(Xr$y<jK_0<jLgk7{Zghs8=&6PU^V-r~ky}hkvqHSc~-^-2C{Pv44gX_|3ExwGTf^s#i0<%s**yy#L9fU%0IHY5xPj33Ms'

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
