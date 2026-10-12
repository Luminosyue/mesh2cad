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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_010.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_010.stl', 'source_sha256': '63e474034e019ba6cc65ca8fa50a39be7776900ad6d7f4ed961ec40726c78054', 'input_faces': 1068, 'input_vertices': 709, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.23800155520439148, -0.26051390171051025, -0.27256301045417786], [0.411755234003067, -0.10541797429323196, -0.13855628669261932]]}
GEOMETRY_BASE85 = 'c$}r31(Xz5@a}sCf(8qa;0(IB+oFR83GP0Nvy1I6E@6;BaCaLB&Z5C}SXbOafD8eGgkT{dAtd>Cb$#7?YhK<v@4T0D?)iT8?Vak|cWzh9%#e1i(xlC$@qb0M&^JvZ|7fIX)IQd7X=4Y5jUL*6V0eWQqbAt2?1oSOnYye^=hp4I+qALTq<{ef!~2H?)OG~a9aJlzoFib+$gt62K_mK(3>z?z{ANMJ!UyVp_>iDc1NFF6%}Rmg992t~b4+pkKmM0VAA<M#*b5Cvm%3ul>FR#j>msSs9c}pT@!O**_Q2OduNc0zVoZ$DzryWH#@|O=<2<v2MIK+lLKn$*_Bku^xZXB4d~I+_6vYmA`V?ckm-}Dj?JhF%d+H?{`L%i97{0H~>^P&}-nN&G{Ihl#z8AiGX1-)Yhn+Kgm;J98wZ9|yJdX#y2mQVM<Je!5J3;NQ^-VH-2YfTXt9J^Iv&!Gb_&q_zjPX0Z`uLKu-TkAZMV^^i3}4$jHd@`Tb8;@j_q<w_DEd$Q)bQQ#&FyN{x^Vtxc4NCP^!HZj%K4k5jZ*V_O7v&HPr76^zqj}R_FZX{)%?z=)4bi&d(W%+9g$~vyYS8Y?gJ^D=UKNDk$?XM_Mdk#d>8sVYSz7M<j*q6tLAsssAu@j%u~D~f01_Ff74eN)cj6Id-gZaxS;0OmR>P@t@o3&YJT71tA_9D_T2Ej=<gf<l>ON=FN*Pxd&c?aOuwk+_uZUy#TaL)W@khm_`Y(D&WQKr^m4=3u9h;^u>-#Q)C$9QTrYV^&F^iopY!}a&REZmh)|yYP3*f|<HY(meJ6bDeJpXn@V&_6osj=OeczoMNydD)j^piCDI2S9*E<t_N|{)(K1;`Q9`yGizrU~D<^0-A_{d|vzb<zY=YJCwujV&>FMMmiR>4ohzBx|Q_rSOI*UvZi*Y#zJm{0fW371sgoKNrGSY!QqOJCsaHW<tE)+(OY`<WZUx5fkCWA?{(odX~8`+l-+th!yT!y{fNJ=oX2;QZQvN20&a9FOY>Z#Tn%cr}l|Z;oH{vhOazzBzs^(=R*^QyYr+-SY^3jmF}AbdG<;^P}w%^Y82Un#bQ_mzZZ?l~1l3{qy`I>Y+21eXZ@^(PG}<``WN?Zr58mr^sW~&$4+9-?RILsN3Ex?7JuYk|5SId>4FkoLZTDhVPAdF6zAVv$BTo__c71I?txB!8hL*_cr#Oor=V$@1tvbW$r&ZAwivgZ?-Dj|5|*4cpu?A;9KwGboRAPWn<L+GJW4h_RV?oWv$A2re{9Q$1~~`eDAFEhHus@ZALAgx6<dtym|Tr@;JlJh<S77Y0cYB_t049o@1AV@46hu{(F9%)qkCh>sY<raiagA#aw6HD`Q0eN`(#I6*WCd^*!q{@%p?tJX!Uf1=sOBe9|LP^}UZv^Lf8hvv}2a96HYHYE_k3k$>{%?B6cL>-RPL+Vn6{&n<sOsHo@K^)Svq<}ufSK7EAmy1mcvwVrL0RNt!4n_DKTzHe(i_BYf?P<`k5bnHK@5ijzOOy;`b3y2f>=dIxS6HqKx<PYr0ez9CJV*K$94BuP!mE5l`#krmbXNwlwEuWsZ8*pFjmox1%p8r8wl<IqyUNC&`h&ytB->u-|D>y~&Z?3+E?>ZPS_cyXQAE$dy$o;+di!nae+rx5y=YMPX?pNEy{yKL}=KZO;S?rgyYa^~#RhJs$_a2<h^H3y<sBiA3U$b8}i>Pm=ufaEuQ_lhT$YWi<ZC}F2<IeBI^`YhOzA3H`y@%O%jK7trZrAiR_*Q-1u!i$Iugmjbo{u)H<^6qD-|)@)<{Q3=^Kbb=jNkHqZYlQHac2wXnV5^;kN4{@{g>~$gzYZ-hV%TeBT<Y8zVrSz!#C@p>lpjq6We*e%=6mao&5f4Ys5U5zNf`1F%R1E-R$q|EXL{Yo8xq(In4eK-^Ysm^7GC9&eG?2{zn|+>xx}Nl2zY%^-K1*bx%@#cdcezKc9C>RDJJ;EZqM|(*%(}&2_F{6&uE@zGKLG9#7dSaU%b$P}GM<Vm$7d136Dv`B>HWRI4ek2TUK=d+rg1V#IjbYn;E>6)}FT?OQ(Hj^vFN{=YHoJEFvXIsQJu=evWMqEz3NpYIcWgU*WmbtiP<JpK2J{q;R6$n{~@Zn0n5@&|m}ZCfYC?>Z2{$HnuNVw~<iVch@8Y_0>R<2cX031a>D`__6`dyVrPPZaCN-#7caGTvjq-6gJr$&D|lzLvi)Unf*=nI!r@`o)+R&-fY%s_)xB+3;PbipHtFYhq@e$A7ZMi2NVc@jN#CD^m46vlnq)&G0T+^&K7fe5tj1kSNAeU@zDGg%{&R{>OC;-*@R$tjIqk+1Q>t=T6S|(?ibFa5~R(>z|TTU;8)*`-`t6i2e&U^LgsZ**MjA1Px<9uzRw|)2$Mp?{e>nQGHKYes18M+%!?-FM5v8Yu#2wi9Em0;dwk)IbQVl=3(DnC|2~Jw}a=iX(nE8ou2UfHEW1iSN^`aPP~s_aeYYli&$6wzO}AuzvcJ6Tk}&!Kl8o}zSg^m;hWcouFAi0y|VA)_15<01=V*Q2<Pj@G>Ivy?@g}D*S9C`CaJz}qMffNhh0h(`Bx?J`uH{}LFE6il<#-;pN?03Pf!nzf9LvY<&Q1G{om}2ReeXfr#zp5TVq82B?tIEuKJ2-kssG%+T_JiB7e^Y+<*MENU^^G&-wkkJW9-i@A^UZQ-YGkc-~Cp^JcEzVt$++C-=|ZM$C`rbVkGXc4;Bz#~XZ+kE0H?#r!yDujV?nrn;CP*Ym#Ie?>_#Kc4mh-2YAyF+aYeFO2>4-TH*bHR(@YC)F#+_37tZ=l25HuNmWPw@F+-o4&8Z266rD$x@K}Cxy!ATJW_CBl&z_UKhF1KPUIMu0whk=lnS<8uR5j|K@_~J0|?j_seG<q^Q2@-WjfkW&cc4eNW@Bczy$(C91x6=NH_6#G?e&*Rtl~{=qlmRo@x@JzuvUxE!bY?ps@UKKDk(it)b<;r_p#i4pm~sm%Rf?TZ%UKlh%`%QbdKiTuO8T=%N1ixl(lX$ZgHeLIVJa7I^Rzh|>#k;nHZA17NHiuv&_JjedVDq?=LJzw*>c~oA^kF$Fl?tj0Km>>6;&-nT?AfK2YZ?U^vXNzYR^P@Sp^Lh?WC+5fTB82-7e#h(jWl7FIa1Z;qPxsmbcs%pjx1P7acQ4#!_~vz~$5x8xIqk?Kbsc)Qv#)(SJV{-Lrtdw(zV$pxE6sV*v2Q(Rp3c5!{%Ia3uDdM%`bn|QJv%D!cHg#6P>)A{-#i{Y?<(<l8dpzJ_sdzkGWQRv%HuSjcfogO%`Ec!`_}p8clLcvIgfeW?n|!9@5}3AVt(8^t8xFpqGEm=U)AAphF{_1^pEiuRNwVmKVCQerpo^3Uh}%y7LuU)&be;(pLC5A{X1pj>*_L1VnqMK8~Jz{UMWg!cfbNZ?-%zbtG=&70rm$+B#Qoj?&kHsdv(0nZd4%qzs!sk+g%vX>#$-d|NU(f&NFnHoPR&xoPT%Tmb^~J+>2NH`}<b^ORe~Qzqyj@%&DJ*@4K;5)N@zEAl`21tys0czi-w5!Gn0aH)o3R`}@{)^864U&$<U<{HE_)`#_HW;3)22Xb#uI=mK2-n}oCf^{f~*kH2s2*N2JxzI1OY`uqE4e_zw7?EltX?3cg)zw}QGj92H)-?xs_B5qy}nLZNx<-0Wv^)t8JuAgsRA2$1n^W%Eex<2&tt@&KKg8lP<i|x8wtm6FUb53(z`T5rScyAl$!E+w#ef0CKb+YPPt|#XGDdxxDx8~D#Oq{2zdGPbC{;N*#`fSek8|Hp_TqkipO)IX4P2Umm;iQqr{9LKcDem8~E}uvHKVdy{mh%VSGGZ+`j;{~PMzX(Pw_I0#zV)0TeH4%1HCtZKz<0nm&kLrn1&$TxHOsG5`@j27s3r1iUD<cVjS=TT)AuBVi}RrAYZ+^c>on7MX09c!)4Xe9`1oyf$@o0cks*xdDMJG1pVOV67ffrEqWb!IkNq;=3*TMoB|k4HnVhWpj?B;44||)a`o1rYv!8!KlIS0@fc^7-iTv7MQ`rCPOOeNOeLUa49QMVlzB6w}zCRlMLX5}t+2`E9_k;wIzh@CXP6vG@_p5pV-tM8jVw~=nkJ;}LEVk?Lr04wa__?p?dmr5Ada`e$oQM0@x&C+t#))y_b0SyQnqs>eKKF6{wnmPB@jA}4zKhtdCwL{_f7Lz_EylTT6z6|ESI%3+06xDzXdffS`LaIuUt3IU*KO9%nzO|C-8ss!|3f3OU9EZv9?z6*a=nfJmtS9PoSe6@zw-I6Wc?^HKPOYzzne{LS6dO!=go;>V*J{jll(bj(TZZbj>Zf5_2c@>an|j_zT<=N-F^9b#eJra7>_r)5cfaXR^)e?&jC=EtnE&z&vm9^2C?3JXFq2DmPh!G;@9~4{Mr(+o;{zZu<v(#x#p~6-|zTx?-<3;(?*^b`8_ZCaeu$#%kfDs-v1-=`0{qH!FfUsiShV4mf`+=<niThlaB8ra<!7jb=bdrKks*ZIZnK0-|zTx-+9LK{)arioHt{+9{L?$&O#@+|7Ll7X?a(0f4}3)U3VdG*YEgp&v0{|4f6QXc1+-U>vw#4H+Saze#e*QX~Ff}@Az^*D8~K$jxQ~JLEdgHd3<SYva#=z$Cq>1Lq7lc9Y@-}L;M`i?|5-v-oxv1l005KHNrWM-*Mp{-;jMA7tVI@hlhyI@%?@CzQgkX<LNt8oPYg&>$+uZGUo}+!25f<lCgbf`3v0tV352&GX1&j#C?tFd#|(+_cdB8_FXypi~BFrcjpX}_e~it@;rxb68TMEJGnvR_qJf)dvT+@KZWmsZ{BY@#$Dm{Z?p6DO3EGM{OtAK;PK?y$bOB}hOafe$$p~<zFsk(=fL+g-ow{7=KbvYn^>O(cwL&;vE%P?|NevI^{}6BU7t_+z}qc#TU@`nUgWq=zVC-CasTDJ@HvQepW^3R`TG<xd@XltdA<FnqT!p@!`3+ceCztHK{La5=4>eX`}@{)sk4LOdp^1-?srVz4d2SYzcc3v!1K`9QYotMech7J*BNssslE%(owP4(38H_!U>@f}K5tn0GyKW(cKN$#(f`V9e!i3|Hd6I{2fpFw<WtIs@wg^c;p5BusThy9>3OdIY0`-CIJ39o<G<NUF&^*jdwe|3`JT@MgSvA6Ui>`J(IbM_>EPb%A2=ePpA_oL^VxKXm}h_Ax*vJZz6aM`)_tp=Z}s2pGJMC1Z{&3{d=0+!x$42eJU_kji{sb5U<l{WRZu=Bfv<IK#rvD4DeKUoyxp3?Vt+Lc`|fK)#dWy9Z(g@MHU+c)MR`$w9F7q7XO<InPumzG`di;)IW(O2D=rT||6jBvMfKfy{@|InELrt^OLp+{kt++6R9|xr=k<JHYNE*Bi@*2a$UP}R<j3*o%rPup^}Quy__<HF!Eqx0{Q2C!Q@2>vcfRh({nmDj5&661=i_B%lV~yiu!sEmyA7g5{v!OjqwhODkC?uv-!%SQ^7uJ1Ki=%0vw!%2m>);^?Ck%wN6e4&`|Er>yjw5k$Ng?2AGh^ai}~?x8^C_;Ibwda$nxw@n<?hUG3r-dXH&+A`Eld<q&I4mm>=)!8SI}6;?GOJ4d-#5{)F=!t;y%pMWZ>-jY0Cf>F2uw+X>%Uc%VF=E@xlMGFY7NOy7}hpg7;T|Cz$`e|3y}KIZ3J&riPllGmHNq^JY_zI7fsGL`26pQl@O#?QCv#;j?)eumZ(&mT-*3$G+TkMkCr!SjH1WsS$rx5iU)1&=dZ6*(S1-x`m7CC|V4Ic)pETqo|W=kXs|#h<4XoSmZjzW%*=on4xctolxKeq7;6s_&}soY!B@L5U)N%OiZe_XtW5{TD70@0Y)CJvTGQ^T$N?yL5;b<H_BG^Kanuyp<;^BlllZKUVcUxUO*e0%Jt}CTrQh!}lMi@7Nv0^`U4<F>kJHrP(j^S)}NX?{E0;m+AZOmvgk8&!>1EV);em`Fx7!A=Z4>U&8+II5Gd;=UvzzdR)xEBcp@QzX!gR^FQJ-pI;)jiuv?h-N)y(H=D$KdTZf%)XT+UJ{=qD@%gd(d@-M{G#~MNRi47v`GYs`esx(Zt}`va>l$&L={v!`|K}9`zI7c{YBP^BWf`yYv^}^!pW4O!+oXu~=I>j_OPRfVoZgG&>#J@hQdHk<e!pm4jwI1PoX;29y}#py|9&;k*U#l;o_gWzJD$Y~KRST@3i(8SUwS*&>;5;QMgB!cdEP_QC8)mZ%3@wu+an`Y--Gj!^Y9z7T@B|Q=ev6%zZ>TlUtki~`L>5R&(u(!=e=)O(;enKX;1R=t2MtStG@d}bH0AK^FyNOzvd=C&ncW7FZ$zt!QJn8tm^y9|Ax<lwnnSI>yH`uJZP~T&$VrQ9t;Xf5&1V(V}EPwB+-9p6ra}~2PUY#=UGQS50)+&C;A`xk=NO<Px$kuHAmThR!)Ae%+I&hTl=$|zvKnc-`}^+UmY*;JS26M=L<jIsxv=b;r-3@fv*D&??_R7&++s4{Cah=>TB2Ma{qVBl2qR@qa8lKo|!1}Z_3N}LABipB7f^2@cDIUyvQGn?{iEU7N`0yd`{<Bc2bPfd2uA?nb12{Y&WGpe-CWY9x;A5zUSufc8gJc-&3A{-}UWczdURH;p5_Ti)b;<)o=JY!<AKHe|`V(_uS0uc5D2HPx1HJ@+=ec;K1jMj(@91itXl|!Tod16!YWzvL*XHr;7Q}9_C=b>nJe~t`>Y>=iV41_Se17!~WV{V!ymOhp>OYs~EpFp(6Wtn{(ZWyvp-`aIIXQe!g}8TjeSHPwR{Cm%6jQ;QjrxlK4KVE6YpX-@ht|@2|RJU$g)DJn=nG$Cfud&gS#P_d;E9?|8rPeNpTC`Dy;(d3do#d>_^HUGUBOBlpyQIX|8&n!k(j_pSS~zu0$I`d8kU!FR&9K2J%^c*9r^=Mv@jTK#<UI@$C!_||iwm+X6wC5i79TmFdz`Ma|^h1th*buD;9it79DIlDG!q3G|#b8lb7oFvtE;q!NG*Th7Te|rn=|8h)%$e$VC>wC_1-Si#!eA!*4U!2H)V-wDU9b?6K@{C~rZnPM`r_Nx`Gp0?9$P-(Y&zs*J5&PxyRA4`}L9`hEk01E{$8k{XuOr>>Tpy0(^EWfk;z;gaV2hXsR|tQ<$91@Dq!|C+d3=2K-yr74)svs+diyRE^Wz<tkGH#hj+h^B2_L?<Gf~WsqtPxtk3StF=K;^{U5^Hd{q=lYi;u^${p5ayVx5=j$o1+#V_t{bewN=e+~0)#eGkNajprTvuIDBBz92Gtit7809^v!LM}H@Z{?nT9d8GN%c+uaE>*sl_R)5rg*9Ct5WcuEpYq5{dAFVvAxSl(5?2A-==g~NxujmR%s_$`kVLyHT1l4!6dc@mnkv>lJ&&|IZ_00cOj7Q%Au5TBA;OANgyYV>jJyNR<EbGJm++g`U7QS!(5OJOCJk$r{i4ec*@h#}f`vu>6&b)+uZ@R4VcTYoIJkGIM#q)E|VwdP|{mw3U5RYfYQSo~y=Un)YkBZ+z`TN%MsNv%||EOp3cL(r2@Xb2x?_0mW7|Xu1!ZYzZ4%64*TfaMNF_rtTyDjF&-?yGuz}Ft$67%dG!M@vjTmF6xz9;gQ_&u6;)n?9v>p<&!WzJpvK3*v)ekbTGyPNaizQDR}bh7V6f9rjzyO-zLu{Qp{d@p=+{+-35`8XOMBtL)g^R50xVtM>O<r2RqHGS`+T;lhk-tp|a(cfC<j}timv55HplW)$yw?HEAZ<Yx0J5$qlz_*?Y*?;8iPV6gxS8IE~^9kSj9s0u$oG0iL`MY5FzJXcA?}9xExo;Zd`7xh39^LVuvVT9nIDUPlcNo5FV}$tqvZvHe?!RNJ_`S0?`&q;H>~o3VFT1myV?Uyw_`S1pn)8<NzSQh2et+$9H#B@_U`O$LZBIxi!*`|h6u-ZA2Y2TFNxjAIwYAq#hVOnpP5ge``!d?_eJ`ep-<!LBxXSqpl@`Arciy|k`3sa4zc+VGDgT|ZekNXtRP*~LRWN*Q%B4s#KO<^$|CLwd^T6SC*k684JU?`moXmNiIOXrNN=z|)7k(#Y)s2EP4c}9?pSX_l<e$a);alT>v&Zn=4Wi_~OYm|p=YenizU=t{-tLXN^7qj{ALKmnt^W7U7`|hETd|%Ucg`8U6TbC+ZT^k(2khbg`1cKb1Iykv=ApuA@$Wo1+Sg~l82{cz!@uX?snWynJ=Kn;_HQTt)r{#uqnj<RqG{AJYPqyQLCQawK_>lY>VN-}8AGf6U;UFAl`GY#_5b&8W@O5uk0GtzK7!i7=k59}jozZ5(cpCY-_q#K4%NWt^cRlOp`D#|E4Uqar{3=B{W|NdiH-F<m>O|SU6<=^wch^FSZ{00)QJ1(?Vj#`Y3IJA>A}>9>2*!?exK@XJTxD8Jh+hF%IPhu#(haY0XG5D>jLza9(_qOg3E#Fb<OpbM{kv&xxkgc+3Ee($8|_=ouT`{ox!{HwncAVy={V?1#beM)Z1~roz~l0w9|Oq7O)p{PV+qv8UdaMKA^YH^)^SJr|EWX#LMj5h}YP;5wEgyBc5&NM%>!Yjrcqo@e(xRv}nd_HEzW1HEzW9HEzT;G;YLoHEzbXG;YMxG;YMdYutz%q7k2j(tZ+uruX?=Z~38<z@&x2v<_(vo`XIHp97D=93H^jlO9&yi^F(-HsQTm3_S{73^vyRz2~%+Nw<Tk5!1S!OmztBi?jf^IXDlFhvLdHLOdC*I9^u?YcK$s85{skkK>`3a*Pn)MJtBmww~U;*2mXQ<3>D7<3_BZ5idp~jzS~;!p_Zjt(_b3N;@~=)pl;gE9~5eXWF?DH@9;mK7mHu2#xri#*NsmaWlrCaU-s+aU-q{rTrwHqPJEWm2_^z1<{D}LMwywf^(x0=g?bYJ*St}HX89yXv8D+{iuj_nGKCNCmJ!W-@h=X{%FJ{phdt-^jux^b`XttFLW1pg^hEqv2i2*9{Kx&X<Y5?JT_{?-#~YO?_l3LY21wc)VMXqzOK{zZPwc{G~!dxb70CjA9;6x_n;B)xASp&2ghn*a8YO{u*c5(e*%s82-*^5K7O$AT<ijGvvVV!im`bxzH{I+XddLIajnDH_JhAgTZet6d@GQ1D&{?do!bh`J*|;aSSLBaAEOaxfK~)&0B1t0i1kuk&$U5s0np9h0B|AbMsOi;IW*$6dfTDrYNl(X#*O%M8*6?$^XK4SprK&Wt_qJuOxjoBB8W-<wx#lD8^@$072d0HOnO1#-iS$uDclV)=>UayA|{PixP^^l(v}JruyaiM(w53$h)KIEJRUJ=e}#)8CjHlz$`frIla5h%pT;riC58JSCLN`4cf_QF6yAlHG*;o(HjYW#DqPUcG3jetDu*K`?Wynt#H522E{2%Yrm)+_G3g|Q_iG%JUQxI&V$v{$dmttqqVR6Sr11)Ov~f(@S>Zx<j!A#BrSfRRq`eiMh?sP!!o?AjrcrpNjbqYj3LnroCcUPx3o+?vg?l0<4OVy$V$wu~_1g&}Che(kVLQj9?`)|&1~I8i;Yo-|LliE7nDirsXWKX?{Yv438potJ6b?d6I#%Ich)IVl9D$fLS>e7mj!A<QcGx*4{nM7p;}DY$P<S$8(%}l{LrnVImdZ_S9Fx`pQ_ZCM_=CocxD{&VFW^?-XeiaiXvD<jP%Ha_%YmyxsV-JUOneEoawPZ?I0Q;{F$6L3&#0Bdz(0dmKnH+VfEPid!HdB6p;Q;|BPMQ-TKN*(9vlm$x)_U?xB_Zre{cnGO(@mHnuv+7pjM6nUjdJRQe7N@nD`ge%2D87z-yp`z-z!upt0a3;0I8uiw_VJcSWsy4ekn#hf-aPM@(D^wQ?}H61Wc32Cf6XhFVE=@fsR&IF#yQIAY?LsFh*hm*5T1A>a+*Wzcx=GVmiP)x}4MiF>0~{s!(1PBc9`b0WA3YUNOH6>xoM8gPB^4b)1ii#O1SCqSt#PC!ij8ntpX_%(PFG#I=Iyb_uSUI~5-rMmbSF>!y?%6H)Y;AAM(#bm_9HBc)<z%{^5=tp2D_!ep<)x}$A#8aVE7pEd7{uQ-yEcjROX6SJ6X7E~QGI%ZcDU|BsQ^drBZLEKS2ZJv_sV-hXOk5kaayYm)xDk}<Vk5-FXKbvsz@&j-s+m+D)7x0vDIATMbf>~pA9q5tDqIyYX%2;{KIVY#Q#b@MX|TdnAA_M;Y^l5gG3gP77a=A+r0{*jq#10fO!bjs(k=?eA|~CXFxAIh&}<6VL`<4fVXBWgq5BmcftYl-!c-rJL$lgac@1LHV+t=pO!}?D4-k`Pw52lDM~X>%DIAZObhpA(A9q8uD_jRLX>Nt7KIVoVP&gbhX{f?fA48$pY^l5fG3g0~mmwxStneemq?v4~O!bjs(tZjjA|~CVFxAIB&`%VukC^l`g{eM%20f_o1jMA{6sGz(4w~JT%9{|Ao>X`xV$!1uKSoTN*_O&wA1Njsq;N7~(g=mAK1M)uDeOc{nnz)(k9nYn6rPHhbc(`MAE!Wb*iv~jV$xFzuSHCHT;ZpPNk6uwGSx?lNrx(Y0Ws-bg{eO7g?_4VBgCY66{fnF7asAqHr7Be>3lHNN~()KjT><rcss#uz%fv&i!sph3g<vfT3unPi`Ai*6%IyBI!xg#h)JJosZ4e8IqKsog%2SnU92$G#l_GcwN&ncn6#6^yAYGcDNJ=S4q8#+oQO#S6{flv2)(NCaKxme6wZp6^o5qnR2N^MKCV;vTg0SG6{fnl6#7t0<z9$MdnmjcF=>LrR2LJVl@-p7n6#e4R2S<(uPYpim~^bd*$|Vy(o&h~;w#k0jS3$|OuAfQs*B5^KWVAl4>74r;XQ~+lN6@9m;|k+@Mnlg8z@Y5u>tg^!s8H=PF6TOV$wHSDpOs2gZk)E_$Xr1)e2KxTn&AqrSc%eqyrU>KunsVFxABrXf1{FASP|7FxAC|(C-wUf|zu=!Z{F=zSUBh>f&3}$1MsUM@+h2VXBMkq0h8b9*UTBh{AgjlU`Jq>f%LcU4`=^CT*-R)y2lp+X~M|Ou7n8HIwRNl*Wy?xs5dj+#LJ@N_FuCV&ZP7mDR!Bz(G)|i$REq|FN+S1OEdKgHl}#Lri=TwQ?2sB6tLJF?a-cAoNG@KyVC{>S7FH;xBBhao{h&ub@;HUm+&$fm#^|?g1VMrMfr}F|h_61*S$k9v;=j@ra2pqgJj1Uj~Olmx4pVgP{+>gTZl7s*7=mi96U>6Tlt7Z=qBd-y$aNg<4q;+zUJeN_BAvVq!aVESMVcm++`Aeu<d)Dr)6M@Kta)bU8R2JQVs9cqljlN_8;-F>yB=YZAB{_;)DP#orMV_d%^}0PX`0hEiP&MogR*IvGrjcm_PGi!%@tUq`L<fUkqcKv#pufJ2~9z#-ryDAmOz#Ke7UtSR6=;6I>L7ym#^+z+*~A-ErS7?kSbFvP^^pwq$Bh-bm0x;P6l@lDjqE#RBranSYPao~~AXW)_G6e!ij6vV^>P%AHj2Y}y0sV=@pOgsp+vN3oNcm$N{;t0gVnW3w|q$|NxGpRoAfHqV31!7YA+{k3AkNHt2Llq7}OgdI!s*hu#MeL~@hM07;!c-qeL-#5?0x@ZCg$E)g?WS-HV$z)oQ+?bCZK3ch#H94Ok;zma3!qMhDLfD{>3D@T#H2+PrutYEI#FS&j}xK$6b?m9+DGBRh)KIE9EX^6m%>yZcR^b#{1!1OeQsnj)yIOUli>;vK}<S9VLM{dVhU4zECzKeO!d(X-LG&sV$!|}4@FGcL*WF(q`MWS`nVg~QQ_YalhWr#CR2SZggQA|;b6q16BSO2n6$XUR3D2&XDUqfaVGSD!ebDVx)csUOxjc7B*dh96sG#P2ijfXKM<4B=SC(|eJqSRIY!}Oh)E|YoDMN*35BUXmVnMynCjzf=s|_YAtnt{cqC%dUJ9omCXG;->SF}7ufp#UlhWr#CR2TMpiYiccm!h7$qHviJQ<u1N;NYdv?;ih-u}}0p^fzk_?g~H>VIouXDtIZ|3<GPZGs%6r4??9xCvg{6k1l{l88wI6sEiZ(4Q54h?w+|!cP#BK2`WH#H1e-rZIkimIfcw+jhPAphv)O^!Bmd=SOHpu=%%R&>z9az{jBv6sFfcfM!zoW5lFc6sEjcpuZ~YLri*K;UkDik1D(!G3gG4k0CyWF%sMLmW$>FS^!*(){EZ$(O5qLn}4%I$+IISP6Pc{VS4Sq(3}eALrj`q;bMqMiz{3TF==Uq3m_&fsBkXCq`4KgBPLA)-lmV~tlmyTZ-Kwj+dRE3fX)P)f7=FK0Nw`P4qd45OvI#LDLfA`>3oI1K}@<;;nRpo&nSEgG3j^Uv*26cbBNDktmmNH!E^PwsI9j$(2C%~dMl#0s?hRa^KWyZRl#$?^PtrfE{~YBg2F`*lNJRR1{VQ45EsU_9ni80S42!&N#WXvN$V&)7x7$-k(j>kRN2Pgbt2sartdP9u<`esNIwPB_n`9Nb$Rd_V*1Y0I=pTjUPDaZmD+0K??sVr0dK&zHbb}CQompIDYo+|wh@5WY{7Q6U>j@kI(q#!s7K+-h)Js`oCh&!UWGqJO!}F^B@mOARCpa?()9{&K}`CM!dnq<#Tbd}>FtBQ9_vGY1JBiK;vBuTg|-22(A!46Er2crchq0kP;YIZb->H%T1Rh7p;N#e=rwx#-o|>z#vG`>rm@~?LK`UD6)|aBa0R`U*IOBAX)yJfi+-eEgUg^#HE2~Z^+{*rexx?=B3)1EZ2>e=;TCp|Nn3$iV&6{NSZSY5qY*EJE(O!J-eWtY%WTXa>FrNFo};mT37!M)0&M|qskf=v@2S|IuJ{}EX#}kTZUn9cEeS4z`3QtI2Gh9iVr+M@|HQTMS|_wD_^kf726{UTtq1O)|E;OsW<V!^X<dAcwL!Wb>_pBE(5B#O*yqO3uHc23+mE0$cf=L2Zw;Y=;AU7u9ia`u^qzLI)9<ZV7lEhif18Lt6Y+XtdjIJ)UqRjAQ<yLENIT*0f9tQgr?<K`R;P`58jh!y&<@~cIR0o3NzY<F>AilB_xnB8E^)h7HhZo#|GWPMZ0dh>kEMzKA*}x^<<DT$SJu!c-1<>WyH+33Z%Xw0S-WvFYNKy3X#WH7nw$I'

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
