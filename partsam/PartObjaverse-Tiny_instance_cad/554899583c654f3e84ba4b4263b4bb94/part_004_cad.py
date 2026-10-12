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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/554899583c654f3e84ba4b4263b4bb94/part_004.stl', 'relative_path': '554899583c654f3e84ba4b4263b4bb94/part_004.stl', 'source_sha256': '0a83d255a8a2e3eafff187579b996886ec18bad0dd03af53fd89fe8c0b6f6b36', 'input_faces': 704, 'input_vertices': 432, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.003639297327026725, -0.4134344458580017, -0.08917780965566635], [0.07439141720533371, 0.09853511303663254, -0.00017467660654801875]]}
GEOMETRY_BASE85 = 'c$}r233N@@zsJv|=9r_#a;dp7r=}veq(MwE&m1HKnTTi*af~q&iI|gPiU<)w%;g$dHC7EZlsZ-OP}ERLdG`1B%}esuduzS*p8wkG`?=rl{LVi6?ETyO?0eVWr(MoZTs8SuQR`kg??tV~NBme^G*@k`-{>*Jhxmoo4hk7((~7{yKWa?J?j3x3+qALTglfKip+iPjYih67Y-r<ZZuV+JgGY}UJt$~k@MvE@<$DbZ2=)8uhx!i+@%#9>x_g8AZuSN>-0TzW|Hps%KQ_Utem2nKqdGdKr5r@l_HI&Y#eNs8d~;*@t?=I*hHp5wg(%;svtt83A4(VB{nRMbAA2x+{ik1!hCk#;8vN)3;#a=|-`=9I)L+{eY9zXaqCH8oQsi?h@dw9=f9h}e<`2gc;hTHlYZKaSSD&5lib(zP+8A7S?I!u0P)qdkaPj-4NPGP4;>VtcZ@7NIec5LwO8j%L;M;w?P|y7GmiWcWgdtAXJSIN(PLunZGJY)LbeV)Wj+WjMKO)b!i1XQ9iPP*K#L>5Sh9gd+E{J2l87cm~7x0a1d(&}Wu@BH*z01w<@NanHejOw8ZG%61(FDYKk%W4V#ERK{_JgBDGx5FNO~~5+#=arqzxyi!^>=wkqdf(5Y0tL%6P0fT-oAo<a~xa%|EWu)@}2H|;X9JrPR;6T4egf^XHlg&@E<Ib`kmw9YvHRG!Z#OA!gZ&cQh(;>v!I(=8K^(_t<)ddW)b{c2gN_S3cemOX)^puB_|_}e}A;c>iQ%Gez|q<9S4H8$T+#M8h(1qDd-2knbJQk3$1}4^DTV+c$Xy9pEO_U|M?euV@ijsh+q769DKJ=ry@@M8t8v#g;o+Lf4iwNU(TbQPP6eidCo4=P(Qq*wEw1Mz_-_hZ{A*j@!(wEO0N6f7ry5DBgTU{B^uA)?&>`qaa{Z)ezPgd;dc#$Z+zNC>b=}48vH$cz5ihJk8{_QWm$c@+fKCKJb6*-KPoT-e&K!SA8Y*w@lQD5n`xIYP8@fh$oQR}4BzRt{Sy3@L#Dw$dRppVm-%Lo^4I}gxgZMdIj2cK<gb8!&;oy(iRYD?fcb9!HyHJ`2bE``en}nmE#E&z!@qoTHu}ds1kc5pzG5Z((Ie)d{e_;RJ<eNa!r>Q<fNw30KZN_;n7#^rtqbt=c~_nAZ~Dc<5BOW+Jn3^7ai*`6_%l1rML#!<NW}Gzti*WHj*W(If8&pSHUlrmXY~!O#(MO}wN7i{=Zb^xyqt6p_0Rku^{@Awhx#F%j^Mgwb}i59>m`!*qyDO&q<+~6QvX`Xb%;Ogu*83pD*o+ITvv1R+z7w%dH7l%fApv0c{rY<cIlSXZ~v*x$4b)zv-!DQ<@p|{JuRCb9`Xx(hb;<ziM;dSzaM!KeyJnbd_7mMJ!rpkxwJpMwA8=%?;7;qv@+}9cl!dq<5JV}h;unX;yiB#Upw!40scQD#ILW<m;P^dF57hrFP8XIJkURe?+fXN$H&Dls_#U5KB*_|Ir$#G`O9tGua@>`6m*9F0*s$K&3?{y-Kyi^Yo)(Cit+hV$0b>P<L<whKjziVGTvIAgYW27Fcr`DqJ0JY-~WJbcK8kR#d-aT_;pGwgzrBJ`Pyk!kT~&m#J>|E`NwNA#;4KzYw`P3JBxN|zs-Q(E)c%M=fY|Dl{bq2AQHYF=QxSy{^zur@b^ZE|Hvu%a6ku)L!<XH_}Y@iKj41Ldc??hOBVmtB$;;?!p5WikK5r}r%wHddWELUm+_D@8uh2%M1He+KE!-C26ch2JIg1b|0+M&48LAq_=f9`c#h8SfyiUV*??%d-)~mKU)D<IX-K5hKlwn$?bSB^sP7Ra^=lrNeA~t!akR)}sh>P?E#maLD)+npwD{8l@Er9MMbKVt?l0os-Ge+}U9n_8_4cW>|J^<rKckMz__<PL5yt0F=kUC&W(_4ycq916*?O3#)&L9Zm3Fr?eDn4d$-|MpQol!l)K9*Jd6%({7)NJF{eP=sy>vbwxD<Zu0{B*kQOJ{KSabsX2CJn#<vb;RofO134it|;{n%hx-<jvN0af5T{`QpXx|W{;-+Kmpb7hF+ldoQ5{W3}~5dYH75X4{j1?GjZ+mtv*f0upTl^b$je;<+hal?=|^s`ZjZ&Yj(i}sB3x{&R<hkC;|=DtUJ%&kWzqJGd4_>R<{W&d*E+G6-+FT%H1X@PvA@2Dej`n;AnInUvF={er|qJEx+i}Cm0EtTi^atfZK@jMQ`*4lwQqmOlwb}mYSZ%plj`qsPUWAS(O_rf>dKESxJwv32{U%qS{#z~Kb$%x1Ou;$iU{NGE;JSycP^Jv5f@uN@3ycn=X_Hp?l;F}#2v93AO3d^_+kArX2dXDkwOfQCUXS7LxZ@<`E*0p|lWFFn!DshTE#5(Bo-XiPHu08OrLk{FU-B|+rF5~;#(w;rNR^q?Mzs9&TTDmR4{d8@G^~<VQbV*j<+3^b2J7@JjB)-dG_|~htSl2SvJLA_A@XacbSQj*-5B43}glpp4Y9POvrP3y${{2_*jXpM6@8<r9JY!WWvlO3?u9f^eY(Dape(VeQ#-tfCetKO%9KE5}Qt7WSnJ;NUSQo4@!{O^YO{`zegI}SYR`Cf-v(6XioH3X$`u4dJCt|3K=Xh`Qo8Bc}+H>*<^04WaKT`T>gVcW+B>Ot<KlOyi@XZ#ZkZ-m2>*c<JUP=33C1d?^&X|MeXcf%64DD%N4*6XFVJ7l}b-f6DExHiuTR9G4-svf&rT&ou7;k2XiFu@#a~HqCahVqnY7fimn}4lAK6iMH!8&5S@rQ4mYJ)uPOg)bLqc@%l-+8R9%-?4H&<|Fg#S&*zl*|`BBozOBL!!hP+)BoOzctuD>*?pD{r3;cI(R9M#IIj^ImUCNOOjXXG{<<;S2qwpUmNl7>)5wjA<f`xu}dYNhux8WC_f&)W7svU%T|LC$Q#y(;}WN+4c9e06+!>$P0vXjt)=9XUOVLZmddjN_f;*gyuZC^DfO#1fNx(kM&1WoM#*z<9|&LntS|N@mWL1WgLUv{_>RIMDY%a7GP#f1k0efdE_p63f5P+CSLMb$bhK@O^~0Q&F4qk#3}3I^Ws^Mr8xrT&8sgusvk}i{qZ{te+A~1r^A^u@+3xH0Wca3|z-k$1#bq9a{V3P<dMNwAjQ2tMM&B0VKOH$8zUx)-M{$2h->O@G725N;myE+}^JG3woD5&vJ5u)5_b#u>>YM#bAn$0+jv_zkk5)(=@3V4Um!lFt?+dBlcxJZ!iM1hDJnsL+Ny+m~N+ZwfcdElTTX{*|^Ib0UXnIrl_AWi-y(4!i?9=q_t>7DNJITKE!E3p0{c!mDlb=T*{>dTo{%fVf*Y3(b+<fhgb=fL4Gy&I*8Hx8!ZOk9@;D2%qzB6eU?#uqez`5{4e}}KXswMf*cQ5jZ-s%B->-<hx7kr(PA8x*t_<#9H{x7^6^T=7ffQk5%Tg!g?@LtSohh7T4S=uIXYWG0ibNp0a>Q`znc|O;kxU9ahX@{)0-9F4#zLDDj-%%|T&s}@H68B{UdBV3!ypa3)a}~}Fw3K1+?Y{YCJz5ol>pEQnBz~d~#<zXVIoUt#i;?)rYb4J<XpQmd=(8Taw&W1<t#e01<Tvf`MrpsTyX+75x0d~U%`I}jb;`^2-OFM>?2O(fpZh1vykj2I%-^K_9&X>Ep1r2@kH=Gqv%T(CwD;d=$y<fqNPD^ulYD-50P?x<n+^L{N0(u;j%2LATk^v<_C3MA*Ae#=?_bV|#if3)?iZxpSLbK-_1uLe|KICsWc9VM%kn;7Dku6+OSi)}>w3$3({IJl56)>dBu-R}<oVp4<$d8%ExB%pZ42&u>}lMWqg#DxXa0LKzltow{L;SYEOExKM*gwSEsX0Mg9pI3&ODa&l<QZ9uh*M|ykvdZQqH}84wrTwXd!v(Wg}^SY6^V&#c$*sBTulbhtp4q@3BqxxA(TdHy)prcK-TO>V+g?{A=@W%6&b0D(mmd^=Oat#U1Il^cQkpJZ~{h=EA<j%=bvnogOA)-ElO?58vu$$+)^u9C^Swsup}BX9vtLt>b6N1ICqlvcE}-!MbVfOI?!HcLZ!kKG*wRkoLD}FaC}8@*e8%f#>4<GgRK6=TDG4wmbmw9S0&LexB>_?fUImS$)G+1pRA`Igj~koJx}W%2h-5^VS>WbLYst68~XM>Hk`PV|{ddbwvEu6Q$qkPep$^(w>WdC{fm%*7;ChoBU4NpKw{)`Dmw%Tff$L?=l~@m*>TEJjc2b@O2L#j883T>B6kOy-7oP&+XC&{p={SLh2`<mwiRwB-w9INs#xt;AwKcQQv(|R^RGARnC`QddYoNOp`dSb>tj!#%Xz8b*_tVU6peL&xx}B<bEe{3jHMKOI)Y4AWhC4p2W&ILr7ye-@W*W%;)lcGJb5e&`!ttg7EbTle3*WIXx@L`A*=)G~BndD4v@Z;U>Plq+GYNf&Hqnx0A#v`dHfk{nLe6edBxoBiY7trEc);yD!W60M}*5>|PSzd#1#xUPbo#bq(?F)W?26dwCb}oj*m3zhVaRo;6&~t&N1`5`TI{IcHn27VUHtN{6p~*e7}WS!s-a=QoGNpU@TKT+0`=Fq?m%9OjF8$6wxCQ+|;9t?>iikIbe|rGIXpmwrAOfqbQxoFe|C`%*ub>t?iT-Zp9H=YLE6uo}ppjvjZA4~?1y@m^tX86oE$&GW}(_062i<^6=`8xETre8=HUa_+GsxA-AmQvbXm=kKo*Wc|AA4c~cx0M-$+SbuqrpG}iEH&zbBxIOm`#;q|oUfS~@O6FI-ONiqbabDtgdm;PGva;WII{t!hlstj+S9>uZtZQ1Eym&t}^Lk(&X-y+#oRlmo=NeY!y@<o}Qpd}0;5!C>j(xH@ySn71cYWdOA1>m(BxC#-#%}n=?{{V17uqE6%N0(@`DyohyU@PwDRO=_|CU_0#BGdc$H8tmS2q^_1K%Ff9OK_~yImFjzwhO`&Hd!LbKj_)&a(ma16CiF=a?er5&@;*JCj~xoNMRH$#c8#nbc3LCi7_g0bEyGR~5eY<r$g3VR?6C_4VpEu&!mir)2o{hs`nm_0fHY;<}-A;5#0-mUT1Z9J{lxv?pPa%*T2w&8)sr^Cx+qs=E^VOrzI$Y0szw+Yx_%ZW+%FQ{kKYYh!-dE8dZQyY`FJ4||09Wkx+%mCeui9_{`?*>8CMD)+UkC&s@u@FM2BRj~;A*RBoNhX4L|d3k?&R!Ytz8ugO(%e9Q?!kXg8q+#6Y?W^sO@m?Fgm1`^Jk+ax)th2h_K;j4dhWTQh&KsB2H+_e0%Ua(mI7;e2e}#TFn{<%&d=m*@4+xX}#-SbJ-&(-Da8u4pn>Lf{wvUDHa8AU$vzIxGezUeO6+fU}D%yKvjI5J2j>Fd`A3%HT`@WX@x|AFH6?5?<IluL)gmuuG<|+P??{VFX?=>uQrR;CIcw>G!P8(~o`sSDJvY+{i`+~x|;OjGTB;#}GUeZ738shxO(PcU2qkY2~sXu89{QrDk<N9LFGv&PLZ7-R3`E7FD{CD9SZ5QD0Grl*p#@W!1hRfP?T*s%I<SidNd~?nZ$QN3fH<(9OKsbE8Ln_XVtvu1vo(mE3{+a8IjOXxhY1hpp@#{9&f%xURNPO=Ux$cKu?uc)l#rKca<h|nm^9J>d9UY{;^SZRB#wOXP=lnySS72G>cjIx0>?2>4mFr%t0N=5_pnPwT@jgZ0Xp)BcWuN^%81b7|hOh13kMXY^43g`vuMS^-Rzk-0DlZvt+q=oS@=Z?JAI}Mp`el2Izs>`B%sFU|_*45!dyWo8ey|rlE`Ft8@sFQaCGGUW{>{=C!8e1WB>uM-&8)t0w4LPXjPsdcNzzVzfy8s%llSyId!;=+I!L}M6D{X6Eslx5WT)iYBp-RNOgt&^SLQ+gIIX^NK2zwd)c<3Yd>=i4>sz^Za=n5fc)zv3>Mi5p;U_rPuwQ>K^#{kuxmn~q_-0UUIp3@qDdVt1ocQk1^1W@IQc{2UZ8;xFY9#&s@FnJf{!&LjYR@Lf_b*qzUynFPhs!=-;4{3J+FQJpapD#vey5k%*O`75<lJw?OnDwvTcI6Vt-P{7{d%j!KUi-U`XTg|_!Vx8U*2Ex^0qseulke666caUZ?i%C`mDbGa{*k}h#DmK`@IYDj(Idq^3{)pBz|&F@iV@^I5b(#A8z`>H*W02JT)$yllp0asagBk>^DiSdw;ydiK>g=cbF5TpRC<erT*D4nO`@rOTNi<UVMIEkkQZ9x?AwIoUM0c?FaqZGieXc0j%41<-VWg#5l9Bxg)>FD1K4;=a7r!aczNoU%a}+`fPrWFnM1w+DZQ$EeYR|nt;6EEPo66)_h$WzBcEq%+uDdr9H8B8Q*`-k$ib~v*csn8q%JzTjf2yR~^|;HEkntI=JBZI(A;bKF|#Emg^qBg7KX3y9+Z+mpDA%)8gjizU(Q168FaG?&yb^qmj4GhYQ6YJ_FCo?siCiFVS_ev~%kp7!USxpRUX58{PAvpX~$QBVXxJOQe5-!sUK>o?!nxUgCTgfH->fv8h@8jQxog>5BYq{*}mew2*vX6d8*3!d`QS#Nqq6mev`0-mG;{>hpUy%XtL*1oP~#vhOe7cQ^hnc7uG+Q!GF7h@Nl1yf;<Yw=tW~`Kawmm;T>fPx8)=rSdxi?_*e}OnXE4TJWWvxX$zmh_4R~mio~(B@Y^#@ZN0M#=<uShonn?%#`;090}iw-;8!TuXMnEz;sz6^{bu1@0FaDYsonATqoDvn*;r?AB{&G>)S+$Q`L13{_c4U);)W>z3?3s?&6%wVMWNg6S-gFeEI?H&p3ZG%N&vRU%Vpy(dMnRbILLCTlmYqkiR$3cOI8^zHN)|VVs9o$T%;5M*M+4<9*ceea>vYerO`{amM$I)}9Me|HK&dPsTjT@U5jya9<hwBE8Bjso(m#<o^{lxqo{n?R+|4);0Iz*?euxbj%}TYzNsF#8<$0HG-pup?(QZGpnzqu9Cd!7a`XTsxJG^zLA(G*4s_;JCR@9#P95sefW}p<$IYcjU@h%;^=21(NnH#brAnUY50!X!Lt8x^$|ZX8u=>YcOYg&H}QRP$oavYMR-rK?hX-u>QamcqflGKH+Ka{dkTkPewuYg;df#B!yvgYW1i&6#i4RveP+SW*jF2K7Dzk$$BN(oYtdF|(oWxGsW<Ey#;0b^!}sInsV#C{|28Rd-<@UNuRSgGXLXnN=H0!Mv-<i&o2<j0-SE2+d+0AxzsebmD{XTqe&=S6{T;sPu^j7#{S$BbomlDjQs1Spy!ZEMf_!E96u|f}`ZkvD8^hh#AN0xg>&Yeu?o~G`s;_uIzTIoC+R#B+embd4bQkr%|LNp#_y5&TCmYpu|Ns7Ua)V9NmVGRnSQN*9EK{fkbs5<pM^cxPBgqq46vt85ljF!Hi{b?8T5<w;Hgz6(HaX~H=|CMrokt!+j;1D(qsbeoo5&l<Td48mE#x&>`eF@rDtQfgHFYw1HF*VfJXvWdc?Ed^)t|h897P>Ojv_};`;#Ncqo{q!qsSwuUCATJepGL=(t%_@asbtrtaJc5fIOH*aU1H_<Tm8m)Jo*q<h;~>G-0Jbl2uWBk=|nRMY74Fcrdjuc`&&KwHmnwxfr!5S!rH!F>-$DC*=I(oYcbPoMad3=j6|k_k>-@6<8GeP&<=-$g5ctCs4bR6Ugz@F64OfDrzV4D)KUFJMuDe4D}mw40#^4Ie8v=2K6iQ4DxhpL-KU;Wa^jX$>d0CBXT6!pf)2L<Z0B7<Z0yDEQ%LVdyyBBms0zXmy%<tJ;<@-h1Blkh2)vkZseKdDbx<+Ddcc!Te8yD<ZyBrwGBCpJeo!ED5@uU6giOEiX2Gxr?w>flS8S!$r03X)ZXNA<ZoFN`?4r*&!X6!TAS=nu1hUVu1l`+v3y1?OD#=ST83PfT#j0uT%KB!TAf^z+=S{ND-9wyAqTK1o==S?&nIuA?j!$9{hhjxtn^Rv@8nn1n`EUg$T@7HfAjMTveKvIzsV1%_sL36l5bH@Q%{mllhaugr+q9*)GgGLWTiilw~%*Gza#G;r&7Nsr;@i)&y%;3_fT(>_mB@!{~{kE|3b}U6aIyKkNPQD6~)h~cCsppZS>s8HnIz~9@&Llm|B-ym|T!Wac*i&a&EFltxDF&?=;a0WK|Tup_U`7qWC?vB3Wq-vMP#m(Q8P~MJ`JHid>Xjl0|V@s)JmXT#fn-xf=NksyF!ya(!x7a((ib)V|~|$xW#J$xX=3se{PP$sSaHvIn^pHI&?n+?qO`+?w2uI+@&#+=V)o+=bkYI)&Vg+?{HWyOVoRBgs9;J*gAPJ;}XT6i=YWktdKBQcdzg@=6xP%c%+E<>Z;v+2onz;nX1VaI%*za}VvsqPW(_@(Hy8wF9{U*@rrY>_Z+)jV6yJFQ#rJFD55bw~&*`snj)OrK`zGSCCW5Dbxkz6!JQ16nPza5jBFmh&-J-iaeb>jyi%ojvPYuBP$IcD;-P@ArE6w+=<$T+=<+nTASRMT!fmJT!egG6IFX+#Y#=`b@CeOVDcKWAGHSAkNgFT;^Nd|WTpAZ#mV`oIm!9RHmXZzY6Rz@Rv;IkR-{%SS0wkO`jC5)6RE4oiR9NTil0#v$j``6SQI~|#*>w<B0nZSq%I>rB;TRNknfN!>O8VV{*^j|{44nkbvpSB`51LF`55^yHIjUoe2{9850ahKX=Eq)2z5632>Cd55&1azEQ{hx)TQK0<O|eT@&)n<>O%4f@&W2h@&WQL>J;)W@@8r{c{6z}HH^HLyqr3kyqvs%I*P0`ki39Ahw4vO8cLo+j?*&t({U_{S5n83SCUsyza_6AFJVzUmg-9$OCCsVPaa7An(9venp~e+m#nl3Ib$zgpG9$HYFTn+aw%##a>ib~6pP}L)SBdy<Vw^g<VxfQ)Bth=@(32ibE)&mbIH4@+sM1ge`uNe^*>k?zoq_8R{Dzkmi$4>+@pWsXT>k6YG1Bc=>zgh@*^#CU;c<i@fGT6@)hz<YC3rdbp<t@tTau_94CrbYMFcbjB%wnj=Dw59EXbMP<N1(rfQjESn&etR<hDPTIO6(oH2J4ucaQ+GUuA&&D3AC%(<y}7xkW&IhPe5pgt!nRr~dfJfQdl)y0;XHxyr>7Pe*P8O4{V1#OvmN%2`~Zd+y^Q+%AN*)nsT;v-bGchAU;ik;LqT4pX)e31HH%gnusGxD?IV^p<w&&cPB&rplnGV{OUU#TT+nd^mOi(1x}xxOgAL#<}ZT#pn#q<&$`T)z}Qrq;J*u6K%`P`|Wgu9b?PQJdH@*Hgu>sm*Pf>#yRR^gPHp$%Uw`$c4zosIAGx$R()l$R)_7sa?pW$z`bB$Ysdosolxt$)8hukUu9^q4p$KAy=mMB3CAV#-g}Abpp9P`CIBj^0(wU)Rp8p<R#SQ<R#?!EQ+U5XOgFphfs%;hmc!Ry~r)e)v2|})ye;AnePUQRZ;xYN8O-_UZyJlGCwQM&%bLx&QESc^&vMRcczXdcP58X7n8%tvD9R8EO|3Em8>*{yqTOtT}MtLuc9s@uOiQ)PAAVIPoj<^Pa+3WL&!>pkps!Ssh!BZ$xW$^$xX?{sYS@e$-il$YTvI|=^FBH<aJa(@;dS`>KEi;WH%PYuGHdWrTNIN<Xlu6ITx9!6#IKk%iQ;8{8OBRMR5@p#Z{>l$yLcZwI^98r%)5giOfeSRF#8L_*wCGY9X>JiuY2BkyTN=pIU;fisGZx(qvT>pQ4r_D?O(PtD-oHI*S}d9z^X=9z<?IZAxxI_MkQ<EA2=2AP-?tJdrwqJdvDC-9T1)nVd|%N>%guDnBbOz&YNCT!8FO?M!wjccg}qJCa9JW67h*G1SfE&78L}EQ;q+SCQwEXHaL6XOP3GlgQ!Zp)88~Q3J_=oU8p<6gQ(bB{w6xQj3#a$u~4nH9r+AT}Qq_UeBU<By|{hB)JaNja-LZg6c|Enu}b5oSUkV)xR9%+~h(miVISUkPDJOWl>y<T9vF+C)Xkmr>2mVZYK{X2UGWwgUMs4`^jU-<Ecl<<H=L0r^rg9$WzG!sDsD@$X?VIWG}Ke)q|{b2-%xFltu9*>O}G+@+N9BS?N{sCh|3^noHOCS#dtjFL!c2avf?%avgG8>S%IXaxgW99K$&i%%XTCbq0APS*M1Rb#fmT#h%omWKVJnYCm#6&Y2c0ic3*l$)(75HBmKB?y@M}NL^3fNDiTnB!`geeJnohY&l$W{!jncSDF9RnXi`Z{|M{9{$=)`ePsR179V5%=Z`>q+U3Gr%klAl>fqsx8Zp{`0B#36wE'

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
