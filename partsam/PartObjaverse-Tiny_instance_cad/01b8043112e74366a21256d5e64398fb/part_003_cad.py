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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01b8043112e74366a21256d5e64398fb/part_003.stl', 'relative_path': '01b8043112e74366a21256d5e64398fb/part_003.stl', 'source_sha256': 'ce92464513f1fdc893e926b8d94b89156026da7580ed5893b2200437961ff8bd', 'input_faces': 658, 'input_vertices': 526, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39357757568359375, -0.132377028465271, 0.2990855574607849], [0.37323588132858276, 0.13240888714790344, 0.4559813141822815]]}
GEOMETRY_BASE85 = 'c$~GI1#nbZ)U9s<BuJ3pPUD&oAh_frgG+FSMgjyId~j}Xch^RO1x@fEjay)_Ai)~f;4sKA^ZM+yn(0gNs$RXnex`P<FN>Xh_C5Dp?Ph}OBuJQ6!=Id5NH)**7m8_`3Lh=4HYlXufY44M{r!9Q8RDU(5?}ps>74pa>jk&;&<1J4@^=pD->F~za+drRx|GRZ#FD?u@BIe!>(IOX@BKQ5D8G7#p8Z3de*bPA`h+-tE>N;~sUnsV1&dflSpGl%Bvn0F18y90isf5{y+P{dM>Q`8x%sxjy7>C`S|;DRwWavhtkr($8&BcePx_<&$5G;2nwJ;f_~s|R<JA$=nO+KhQTo&Nqn|>7;_C|vqkh}H;@f8xNBu4Z&}W0w=(9sn<d@2e{B}k6NnYo|Cf_l=_&)c1?NTn(`Cb5iU;*?Kn;rhrT;gj>^I_cUnXz5TGX2tbWEutkdlC3P@U72=iEn5H(a-t}sMDe!@-O5?KdI7V-2A_z|I&F-=Wc4$59w&~^<k;tCu}3WBLVAVNCE%N7Hro%f7Gd++~m9F$9S9+{*3j=@0K6+M<+)A|13B4Y0u_`J}b;N`Np_}@Ruz#&5yA+0qRG**&#o->y7&Hp1&Mdo1|gf0jIEC0hmvt#rNytmx@LI$BUt#8K1?sEVzkzo=^$(=X`+w`5ye}il~3`{jdFR@5FZ$c!d6|H$eTw53alSuRR-ueyYa7w`PeJ|F(Wb{IGN4+lnULDgK(d=qKA*Qyrt^a*R9fG<<s+$=6fPfZyT>ws%;(<lDpcqo4PO(Eq<)JKcT#=ziqSOa*^uH2OTT$5j7^e{P#;dmTgSqkh6osDFNmX+G^`B24}08T(^<Z5zzno1+K(J4?;^#m>PWG2hgWwaQ-cwI)-Lzizk8r+v!stKz>OYpSom$rvktKYcX(MJFX+@3LO<jU!>Eaka;JkRLM;{{A@ZujO};9~WZk$5Ap!^0l#zP2<`dwnCj34Ndip$L*0nBoF2-N#K6@xo)Lv($|=b=KXu^plq+bWpZ<$)^V}!zAIn5ACGyP=40CLwr`^)-#DDiwBPjwhWL8Hq~`s;csTm(>|ydP^X8&{_?v4|C-W1mw-1wJ-F?@({o&tu4d3T4@ofdnzOC1H%+Jh;=qK%yYo>XapA`MPx(5Hm1+0^n(@^KY74da1->tv$t@F>B^7Xfuf0^&{9U*6ang3&cu8z6#E8qC)gZ;Aju*uiTkH@;Lv(DsOD*TQ4e7r_{%kXbFzlDY2xXTRR@%%0PCPQ)j)?bb7;`vR_-=F8<Rj89Q636M0K0Hq@HqYnlRT#JMOmm-KFJik+PBZzA>%U_j${N^TJf9m=2I6?HFx))u>p#%{nxUw(<}A*`!6VV<^&zJI?c2w~kLZVdUZ=GEgVBGDKBoO*cn-t<z26J|j&(Q>ShB)TPk+x~sbiTq1ob1kqfeh1=zq^})XyA>e(VvL&-)XQ|5sD<{3N-A{KD`pQMoancTd1?-vs%wrEuJ(KVtGNlN%#H@(}8G3^wnVURRL+Pd)Rvo^d=6*T(!m$cJ@U^)!4B`um!}zkh`1=jy1FGc)Rxx`F&FRm^oNTtq*KtC;6`eNP;BeRTByq9y9AKZ`!s1ffnfKdh6`>!`D?Jmxb?Thw264gCZcME>;vIq&JkO2~QD?w8&)uH``|97i3}Vcd#e(NE^~Cg0IMIqHvV34dN%^YJ*fA^gA;rt^k%SP0g0nWU!qG4{5=_V!GIae4mKw{}LI%ii#xKfrl-a47PFJmIG;w9~!5k>cO0?(4*e?T<P`zKCxtF;wQk2%CuO*Y*!r-PezO(#%+Q-}bo{>b#wf{-3@^eyNJcf3O^W@GJ4HUghAYTFdKHyvf%qZ-Bq&rO7wKBY6FKVXjkg^DliZ=@ygk>gVS=Kl<#u>DT^G^<Dmt`Uf9k9_IHvAoW9&UYEZ=z7qcBXELAmE)Q_M-dYuXR&6Hv`r#sSoi(!k8!Pq8=N4a!j+Hw0CSS$3%-o9lZO@{9`&Z)I0&*ObpZi5!$8mH^d~3I+;@fA=fZr}keEnH?xcG<9p^pDH@r`z6=7~Qz0^@dD2Y+<SCGz{-jq6ySYs9zzTX&QA86BvTcqQsj@3dZiez6RG>UroVWuqwh{h&fOu-@i~uk{--NPdoQhy0i0;CD<JCYpQ@#?2juc_`j)n~d9gx5;-TsIgt@^!S82?FM6hu4Tcv$qLK3dWQk1e>C?5={GhA^P}}f{Y-svTz@ZzeD5x(-`G>?80m6|Z}hXG{^i;@?))pk_icsk&HZnr{M;%jws%`&jC(0`spx{bnCC3@QKxNAT;D^=V%*8qP>1I$y-7Xz2dl#G;fws9#ZdoaCHUSAupTO$l69qhDTn@Vcw@V&<U^f+QYPPCH?#QKiX!mGzl}oQ_t0mx?C5{r&NZUfHTcg{B0uG48CQ>cY4WZ5H?zMo{)%j`<LoZ!$D<$SE!9KuErZr#d%to%>t7S!`nALs*<XD;v42bLL7kZFyCpx*IBb``Nql>g#M?zPy}^C#`i-d5`4PrFIui9Gm!r<8<M2!N#XK~fi#j(JNF6=(0o1uT6n*Y{94W`gdk6g14N)iMvnct!#+xwz9cy9S+za+d{W-fZZpd%&{g+7p+SD-^cc>rg4=#2{=4(zc*JonXuiO{@mifpZ^y#wry_4>e{qjB>=ab*wi|@EvReU4lGWtpPMtu9iV3Thj^H_Xqp5%Csk^C0s^W81fpK?L^*Bn={-sWC{pKcxeMkldd<JXCAnR@4-sm`hS;%oUP?G}Bx8S_?WApF{?_eeka9VXwpF*WYT9wdtsE#3@1-`nWRAEBSx<;2%BWV6f9XSSPsV{3MkuTL$A{IsWJTzeHe=531y>X&Sf`@MXnWLzWc>m}K)o;lD@5r6UZ{cpv$9e;=SJeP8y&()X2x4*aTmF@Gv@nT%ND8AKWmiYRjOBnaXNcdM;;C^p%8H}5tllVsW64Jl%IwiJiRU6cIgzl3%JL6HOWjWNz+5^vtkHS#LD-ZfV6odTCg>n9Lq(%PP%93xSn1<~dl>+&<J@9;5Yb^Xm-pF^|=f55(zV<4i`1-55nCH@MF%O~JF1puo^`jLYExz^n#Ax}wad~lm$l6?d{oVr9Nze{;(muQ3z8?*b>)5Wtm&CUo2*&+e<Y&~6ttP%b>1xT>-@HJbFn`p^6R}_Ri|=NPYbju=qfIJsQ+_W`9`S8Qlfyrj<0g*RT*&`=4%=1ZAN12YhxnFk_i+Co>Wlo89vC-fE4C}vf&Dma?Rly5#P5Lg8y<;uGIKioDh_Pd_^wjNwqf)+$unXw56#MAdoN`W-*HAa<?CA$im&;<wVSppLjv)Qr)Mxfc{_-2z1A*9`VYQ<`<5*0Z(?1v65rZv8tOM&fqv3865k#dCH?EEbKh|HZCkC#511+W_7~N~*Ee*)Jba!jzT>ZPXQhAM|L7|Y!~bW5`1*-==yO41_`%u5H)>tPJQ$;}KC>4+BmHcDApIDti%36~dSR!fe@7?m$H0^5C;AWZ_18x*KjjaJZ+Yk=zAg20)af`F=eKItPf7jq_e}k}eC^78lW!l|_LTd6wEHE!CG&H?HT<6Wu)VW=#JARNCBCiZGTetR)sP?76#1+Az_0QS^RU_v<9@7$c_{xC`!R`rQtEs^fpv8b*IAdZC5*s)hF-<G%@ue;@)uV`{dtLHTzk=H$7OzUOhJAzFY&dm55>2Z{Eqo4^#tqr{C)9_oWTd>_s+gF`S#%3=x60U^t1e~_>Li)QD@jC>@Tl7;#-C<k~-RwXINLUai~9GndED4?Kq#GD2x2nkFkH}SCu}EjB&?gyO!FqK3jgpb@S;}_!HAeePg^woV)KxFc$T@K1ZKLCWx;+oq=@{d>{Kaz6Jc4dZ@p63+m@>a?Er*cC3c^oZ1NE=1Ge_E0i?(mg8fvPTtqUdRSRbe0^0Y=3n>1@mo9z>Kk#m9|+MU-%{2C`5VfiA6_3VpC2EQamyUW`KnJK=BGs@{9~Ch|6TLOx%+yXdvc!C2c{F>_E&`X7Na}%qty@op@HICYi-25eZlq7a;O~YyUqg<T`=yvqT<_av!uT3`fkgZLVRuHNSvQ}|6ogHJ1lwezFfBzunrH@7vEO5H?Ch38=HK~`^7j9Z|Nw${-KumKi;G2J<-p_Qm8*Q8IIpK`EVZ4{lwQCU(wIzIylc{U1OL0x6yL_a-IM%Z;e-oZ!7o?*R_64Fb_xOiLZ|>FLjI_ZIFL^p!klx<4~tnNz{K4Vt4OHZ<ieXr@nkh`cHiPplLpXPl#`6^$~SG^+NsEhr~Bd{EO>;%@nBrcUjcob==60^=4nUS&j!wzy6YMU)3D>9$`41eS3+o6+(T-g%QZV^9Sa0@lf;=GywTemm)uSIO<GkF23X5UGa^3<8a)4UoZ1wnID4tt{R=OAD6BY-}Qb^FFOG95I0YJN1{vU|DWL)clT)I5BHG!D`R&M`t0~g=Ed458uyu}SDJji;zIa?rl6md&oGarZ;G$AjzIp)81WsweR2P0*@1a}v`BnQnT8m5?5<z>_Tb&9|H6TJIlLYBpLdR7okVRE-x_)r&+jjr%62(k=f`|iD2RS%uf_4wc0KwC8X@=duKO|D%i~hlcDD^a-wbPw^TYll;yYG`;y!;s56oxl{m9Qd2KmbdVcgS^@Rw{t{x<`Dw@u<(t{=vIewYPy9?eGmxOCW$1twxYdIz8m@1yJ;N8!45wFvTeW;6NL<ni*HVCfQy_aUA`uz%|~#MhgR+adE;_yOiEJc{`pcFH{UNrLNRmD0$sz9GteKN@*^$b7lppXggl<GSf_Uw+@x$qUaZD}8W%k4i1RebaYQy-iNs*F9Jvedy<AZ<YK}fw(VfIA45QzAoY$`(L8Z?fH;jy23WmmR97Sohkh}p3KL2@?;q1?MWZ;Z52K6oYiIm=J{A#@r~T`p{45Kd^KgeJeOL}ufn`l^+TNwJ;b*(td9GQKe}T6&%co8TZ?ziXw&{0+I~CwUKuXiRW}0l{k+7tdWOpLvVF#Q)Tz-&w#T|B3Eop>E{=K2R!Dru>ZVu^lcwW5)3~P0i{*LnMwtiS9hlFV4dglBmU;)?Z?qqSe$H1BUyEElSMt-nK>c=CH%p!J>Et=uo^3Aj_iPZ~^?97JcNWHN&}XyzaiKj&zA<~_CfUDZKFa$Id$TyKpZo11Fh3h2-Pfnld8+iS#n^gFpP6!@{>zser2hE?c;6Vg2<thzzxdWS>!eR3jScgbJgxXfs*bbd_b-&gae69#z4%SM7D+#?e6d~2*NJa$d_&&9*%S9gKRx}CKfA&T$!igeIww5D*TZ|Pm3&?Ytr=IXlRk@VmHnu%5C5fa3|I?4SHN1CheAj3ex_ms{KEysx3xNf_o96_V!M{77vJ^yvMc{*--zAB^_D@_nWa)<tV6GDzxFS|x9mwOzN5peX!rj0<_VGiAr<bg!mHwb>C<=FueRig`1$GfTkigk`t*&!x8hqbevfuvw|dNO)Zu-y{;VbXsrP8L)XDfQ%GBr2KI>a@oLnjOlZD~ET+wLEPyHtFpS+RxoVw=@`0@3A={ufxu*rUZyL+Dd@o2YafnQ?G0?D^e;`&J}zUy-_ZG!{(fp=C&eulus^7H;_m<PWI_~ADfivMOR@;A&9Umt&XqiH{;y1QJ~=WM?<?(5v}7$UyjFKvWr|N8mM`%pdmvz6}oj-JC8OP`^~uugb=cibxqKXDGckF9nG^V49P94C&U<8Yra_cQYU8M#3E`SKUm|C|Gu|F}`}#ou*co%kP)V!Ix9n<I5nor-d=W4&8ae7(}v4dRcA<$2@QY}qe-Uu0xSaa+`TrudE*U9mnZ56AgxcvbQBl(}Tyw3>0eFHJdF`iXpx`T6rTpI>Indur>way#7X>)(!#mvy*#0O~(jiaO&j50r8JieMgk6p(x^e}(=sZjJVvrOrNY^m)<fDRpWMK>dMP#kb8VKOo3$o!BRJy6NsamZ!kDt48Czy`;DJ_QBVszE;=ww!7~rKNjcnN;yrwC1xw$<8`lVs^fakrpNf3@@-@MG46{s=KRx5;3wfa%$$6_<afD_{o+|4^Z!0ld`q|bSXW)A;Qa7sz#`etfzR+Buc05#|M3y4MF&<wzCAbm&28m#lpoJibDN{SeTl56AKxR&{1@&w8dj8fv2A&dJ|i^r?_FDtXUF)NIA7H%2|r0G`8>liqA%*7xrO_>$=zjLT4Q!0|1s+8xys1-+A*~rpEvJ_Z*A3Ed`r;{2i)r$g<ngaWlA^Pzw!N*Rynog*`AF?KJTv_mGS<?a;*;X|GA0#ndL7JOaAJ3c@8z=3*osqTgjvHdwf1MW<0|Cx58HOEpw9MJwwo0^nZH5ajBcM8=iN3ys_RMoe|&Kd92jY-)}-4kH_#`??a|+K|j6|PRO{tkJ7%bfxls*_^$VpMyCDPFU@nGlsdB>%k!4DrYoNJ!~Dg!thkEjHh#WfPhCcQ$IJ*kpH*E7e`8trvGc_@uCK&%>tmnOGVZ(`c&<zqgZ+}ds`%P5FZc)hq0h?A#CQC?cfY&us5}dG7T&?QkD5t+N9ViZ+h0vEy$7?sek1;m_jmyz7&mpoGcs=UTWl9U7t<1k$4K72OXw%Z5aj!9gMVu}wu_%1*(MwmUvuQdxL$bgt@pfx{H`}qf5>BbpJ}yx6W>v8Gxk^V3|Mc8vYeBj(;i3uX$|iyS`>rty9E8rErR;*Tb`G{A7aBg=ldl~tp$Hdz42+#Py8|TdEWN|=J62fWWaj{V{kd~^?YOSK8Np-9NlY+|Kq)l5B8%`qJj9vq`~O()gpWj^{&16);6`VT@i~hpF4VrZ;2X%{AzviUbj#2i{iICDeGAq*#hgQ$N}-S>0#*q4L{FnYZu>UNr?IPDUbK|8Dqsaj#b8X&8vWMwYR9x^M*bm8|pVpaLL^_vSvVj;`ZV@I)=;p04>`~d``6Mp!l}p$#DD@j6weeULxOr70#=tj$<AIa>(~7thGnudcpVDT3dXN(vkKm-UmF|iO-wz;`^J{-W$ZXpN@rJ4&UQ*z311<zsLLeW}(QB+l+a87!KbT-`}wh=z=<5mhp49%i`OP4afPsMlbY#^E2uMPQd#sKjiBzGRyaj9ES_Y`OWB68U5cXA-<(eRn)my75<+ikzXxPp37XHU+A|tAisJ|yf-V|4E3*W$M@!Lr+}ZMAN<aTP^WAqyvLi`0(D+ofuB1Z&!@|hV0-g<%l8hf({|$i-0~FLyT69`mNe1$JT&MS>hEj-f5##`k6b&B&xtOEi|<&x9QQfj7h(P*Pa}W&QLO*Qec`9Mfcz5oWn68<aMY=IQ+(TyKHJ@W{Ye6RkLK=N+#d$CLw+4E@g2E};yRKE>p`!X6yJ}S_j#`T-rJ(sF5i?_F@INW^7l2Xpw6lMsMEI>&Tml_(C4%O`1uFn`n947>U%d6-&*VwzSof#^^Gd{o{O!cH?9{^9vHX(6!Bf(H?W5LqJH2))c+@3>f7g9Q9o=K`k#J$E{>lg==<g|jLY}`#-va9UQL>Bs6VGO?&sqVV7>}xmU@<(Sy6wO7wYdSjDE+@M*S^KP=7SOKVto@yy<(V_Oic;?>dj!GfhT+3mU+G-yPfar~&euVmpj6SC`AryOSe7dkFgB_mj1rg)nYftP9uooGn>XAwT&L^cy*Li_B|+x3MNa^FgzJ1HSFR_NZU^uJ7Bpd~MZ8?1!?a<$1y0@)W*b^yfI_^SW;=Ta7-Kj7R-z`(%Es_cEf-t`ki4tsjr0PQX;upHNBqG`u3w&)n&z{$1byarr-gFG&A57j^!Ai~DWY_oEKtIMcICm-|YsT6ffGup0Bs=T=9h+~{*5j#qtHUU`0TeQ#6$au(b5)A!c&r*}=`y1tKR&-eiThi!6yYIv-;929K&*C1o!Z)|RnL(^0w(b8&NI=KB)5M`=AF8%dC1qluOfBL5&rAn6hpZ-&j^&XnG$r%w0#XG3G$vemgsCKf_6XXNrV+_SH)N|w*@&)Qe@&)oWY8+YVJ@Pg3O@?9zL-Bp;Bl3On18O|^0r@fYHTg052}AL7XFQ|6rM@OBeNTQ%{>V`Lh5DJS^l$PPvgV0UoS2%>6RgymoS2-{8Of<WRB!Tk=kNaGj6|LY#a^BW#R;hYl4m+~fiq?}V-9r@bpcuFV)7#LQtC4DQt}F_jl6=qlDe9_lDvkYIGnnU98TUy-Avv{j-u`&N0Fnchse?7!_=eX!{k%cv*c6cKdG_gKgl<!cgZ)%52-K756LeWieFLRk(K^MentMoQ2f;y->9CR(7(tk6en?NGEb-nRrwzLS@8${-aGOK@*C<)@*DC~>Rs|v@*Qd{`40IC^(^@c`84$?`84?m^$__8c`tPrc`rGVx|tkF-auVP-auYUT}@s~UPZN$SCN-fmywr~mrxgzmyj1y7m$_CBrhb-b4DZQq216K%@~TCJEMU!S~??`+JfAIe;-V3NY1COsm>_mjB?HhP}e4EA+k=cL$#8XhLG!!>oF8JruHK@CO2Uyu1{@Bu1~H@4I<Yi|3)oE{*7FL8bA)<_Ecb>o!N`x4*XeZ7qZe&w>+iYsG;O;<etvxMeRWiC5N(B4~F8d&gew#NbN%I!ah23f3@enQreE(f~@viD-HX*EwwqhIdc>@;@=gaW+W@kL>}#ovCbI782i5zs`gN440FbC>KO8H@(70FkqpJ77>W&s;xM<K!x)Ok{UXNxg2%eCT6+VW(U&@q+?U+P8NXBeQwNg!lLt`;lLwK9G6r+IhmrrF4kQoc*nhAeHMVQ*E3L**T+<n~sjaC^$*sxVseQ?P*>`uh?NMCC8I_$;k)gOeLveL#6>@cQO={Jj`f)|opV-xZRc=!dxe~PsxeEJGT+kW*&M4rF{8T@xKiQ95lv<ozlpIJcO%5cN;Wn1xcxC9j=Akru2%?svmL`{G-BJw20aSmoKer)(p}3ISeAQqmuH~k+xV?F~txEHd3y@v4l;)%6A?G7!W+=`@%}dVi4E1=BjiK1$jKb8M3=99xTf?oS7c~Ldi=0SP4<gW{jGx(qnt+^uwLBP#HLADv-yg*Z8Hy7-BRSQF>P_}$Pd*IA$*76Qu3i<VaYkwl=f#ZV3{+oo26B38Dzeg)<n-ip)D&c;X~}Ayv-0P(<aE?5<aA_L%`6;WX(n<e_NutIGuk+#7(;PxY6G&;!sNo-uZrjMK4J=W0(lB~6hm<zYEQD#hGeBx$$iLm8H&qOGm*=ab1)Pqq9!FP{j7l#k>6_27v#6(=M2U7sSdKz+vNM?E7UXOE94{89poeAb<~yQb>ykkiR7u|@eIXfsT0UbhmgyXOHzB2OOi`4dUM|{a>i_DETJwSFCj0dE+#K0+Zc*hIb$_-DRnWqxpSWDIinUsaS%0-97MKI(~&LYWYn)3I2rkq27N{TM1D$rKvsH<{FEF^y-1EF@2Bo0Pohqy?j%npPvJgNx|X_=yq0{JdXapXe1&?=ZOtgYPko^Mx5gAdr@qquTc3*GP`{GjkP~s9(s}&1=F{=`NXNN$9WQ}Ah61^7T*p*Bx8ts!+wrLQcWQI8(yrv+$vvo{<OpX!o1L+jx{th<e2jXWe2jda`X~83`35zPe1rUu`iT6H{Eqs8{EnQ&1M2MoR-rf}H3K;#xiCX<A!ih%rl)2grza<-dXp2AKXObp_D6=|C)7veC*)hyIPxv>1?r#V3*-~j<Kz?MXzD(4G<gekGg%$i8#El#8|bZKD7H~IYyX`S6fdVnX#brz6sz;fBI*ii1bGE{JwtIMbuT%Re299Ce25%FJx`7yU!~q4UnSqAJ|y2IKcl`QKO?_qDE9Dxs<q<5P@I~Yk(`>Gk6M_Vk6eMFxE!?*xg5Ey+d3=DP+W$gxHLm?ZfbgRZgO&JVsdiw7Y(Y`-xr4Bc<K{!Joz5=7Wp3eCPVQh>IL#8@@eV`@@cZ28cnv7qo`ZRTeub#*Kqb+#TnHZiggdHTXp?eL!D1vL!L*SNuEcZMV&^TMV>*OPM$%YL!C>WLtaQ-MqWq`r*0&Nlebbgk(F*EZzXSMDBeZgO;);xyo-E*dXRj8e3W{Ue3X2OdX9XGe3p8he3pEfq4*B<G5HSpCG|B~sk$+L$)6Sfr6Cl1c|d*0UgWgYG~~48T-5AjrFqD?$VI6BWPh%aA`Hc)s8z@XoRQxd*{E5`*~qD=DafhF2^fk!osp25lA3~?lAMK_m7Il~mztmKPxYhbC;O3$G86|;3y=fI#TbfnQnQhBk~33Nku#HhsR_uw<bO4U;=eV7;%`(>vI@oDwg2Wtu?ofiaQ`dyp(f-$PssW5VWi|fPs#a8!^pz@pM`UjospOO-!+el8#$wyGg>edx23irw<ULCDDJ{g+}9b!ol(*mC8*WNCCHVjzmb*JAy+2Xq&6nkBsZY8BsU;8rM4$GCAX#yBDW^DV<_%G{e!G@2wCZHatCrp>M*j>0pyNkE444#N^V7MLvBTGLTyHFLJp=jA_tReQ|pr}P%BdFlPi)dQG>{8KX!ITH-_Tw48^^vA>`iV{?vYCHCID9PfACUhmeO;N05h;hf({Jhmi+T`;ohI>|V~8=!~(>7|l>@IAbt1j5?MaMjlU{Ode03N}W!gN}kJ5Je#3-7DMqg>SXdX@+9h5@>upgiJ^ELbu@V#c?@GT=WHZ-1l1sqAoq9M{{D=?oU7Z;xbBQw48>Qem&sSjml%rAQ_qmklTT8Qla(GMpCs>RDBeTeN!~);O5I7`O5Wy-?bLnLo#fy;9-e6v{NMf;jsN{obD^33hmAk~rupN1_uouWT>J0C{op!@)O#$=)A^rzp}SIjf}{N(3YPMh'

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
