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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_001.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_001.stl', 'source_sha256': 'aaaa9da92b442182728486516c510e9829173dda546495354032956109397d6c', 'input_faces': 1153, 'input_vertices': 799, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2152739018201828, -0.468140184879303, 0.09293854236602783], [0.30320489406585693, -0.14085471630096436, 0.41842082142829895]]}
GEOMETRY_BASE85 = 'c$}r2dAv>4ANTjUWF}?K&_PHc^DIZm6q(0xWS%pYO6^KfKZ$-3N*x)a5)Eb!m&={+J=Zm>(?F`9Od+A3^F8amud|o+$Mbp~uh;kWe*4^Y*V%XNwbtI}xLemwxpEh`)SrshoK4#<jOt`rQiZJI*7V_%r;Z*vd`hhe&&=>xMWea=aroaZy*hX8=dq?+FH{>ge9F+t)tY*%H6PKqS`BZt5fdj*ojhd1;E9um4VV1!A>*bDkK|KE4S8mG<nIqQYSN^Jw_f!c-kIM2$3F!khu|+gFS%uecD~K0c1IYTG%%xOOz!*8j^=^0by7{a@4<?p*gROjOf(NK+@5I4{oPJx#pdA}olZty_sly9raXLpa&~O)eY*RJXg>D6cvJ2_bN+B_ZvQg(xasE#r;Ui_c1njdQ|@cHFw=GX?e34};VP$-O}YQg1MYDcktdpaCso~J%7Z^uJ?hF2EI1~)HRzi}Q*PG}yT;9T<@C|$@ibq3z?k1Ub0{{q_AQC#z9;kVGUefS8Xt4@v($>_fqSp-H|4(myIkkR{wnv8Xx{kceWu*DpLd;?@C(-tM_>2%rrS-qJ>+-S@mMeXlpP)C8?)n0d9cD&SN~S`*3sPCujW=$?t6RUao2HX#2<>j?v0dmSNkR3s=RP$uPG0d=yoJF_h+q9c_qKQpBl5Hxwq&I*L<^1^pEDj)ob1Pnunsf@BSgK+@5kdD|$S?*LJsmU~4qD9xUw2{V%^5&BKQhx0rJ8(G7b|dEk5=V?X|DPaiSmz6o<&;~8A;GaiqxdmiKQhbyFqOh0e%w~s=m@d+=P95RikeW_c>H2&cltwW~s=;Zo&^j&EXGR=qJ&Ii?Trg~lbNpQ-ynWp*X<obLIb}X4`n$J$I&*yN5xD4ZZA=lSS;DO)LP3zIg_4R1=xs+;J?@oTlde0S1iRRjV;^g{%VlA(xa&5oL$@Tr}W_nU|{%HH5lk5ATwd+h`bo{mb*2(q#*1Gw1G}rfYC%<DqKUXE1>(>h>*RL1$j$;R-ud7{m>;qj6L|<3CemS{*{R-9@xIfyDc71em{rYHC+7lnmwd=2w>(^ha$ECf|^R8Xrom{`Z`<{P&Z|u(%*nU*yaaT{7@^IQNb)QhVT&gJ#7N`+&_0y?mH1`&opJ>W`B`;;g=H4Z*MDG)<s$COIxj+BA*{*!itLi>se(QKs?(JFnNNjE&s->>``4WPr-1@%H(b(L-a%=SZ=zpcgPE&5(oNz2Q56&nQy*>sOblGOg!_QVd?t0z&U82{oz`XifOnG?s=dSk7{%nPkHk)$qr~|I{z6I+uP5nE$-oLf@c)IEMom@Zu;A3`*X?&bqA0PY2g^9-TC)dZ{8vI9s>HIpmetxZf7xtOvkCW^3C-`T_c+>oJa(#XV&rREFn*UC&&wp!nUf24vA9yQz{Ry5gf6SEohgs^ru}fl_DYu*V&Wz2&pBzy0u<#El#(ZGMP;72_d#n4vCKZ!SdGO`xS+3*sK6%u1oPp;WM00PuyVFg%HKVTUIPICaRr|Lmq?&STSuWRcdON17`^=#;6HR$|%njFZ`b(^g=KkmZNH*r*?{)R>+fXZ-2iwn1GUe8D(_Q`h7M4`^!@H^+H0CYV9CH0!pDc*p_xeT*Ni^m5==|>XjXFnj|BCAgraaKGMYijFWt@)g4_3DSpfR8Emb?EFBh`KNgY^?kxs@;A>fi3=Rr^w(%?C`m{mgf+{(VQMtNZG?EB2dmZ|}3N{)5GPM05Y8rUy*9cSSi@duM+OzB7BjDffL``G6@87prdWr{`5y?%TLJWI7%v*N?|O_iD)W^E$cy^ZGtLnrRwOC%<DnzkD~-biSNiKVQKs#WGFvAt%@7gKyqv8K(K><obN`RUVaLn$J$I&u8zDgmlw-$;q|#V%1!fZd#8{uCK?ie|?&1z31fmdcW2;n(O<Clk5A5J^#1peexaq6}i4&`IgR6?X~^T$@Trv>ewrq>-(zRshzrS*Y;;8*Y{_;?J#wn)%O3KT-*PHdoLwNbM5-#<ofl+_u1xT*KvAM)$v#Eb<C6p^EXu2uTtNnney=b!I`nS@ABX3^M~!*Q%rgIu7RQ0-23+H>Uxp-Taqacf72$*b)1i1Q~UpzMv2C}*8PWE$C=bvU0-@;9WdsTGTiO!k5>D0;?e|D9^5=GJ2v<4nxXdLlIi<RxwmhYt9{_It@gvm8t*sd_TCDIUHv%shnw%)Z_2%UYPj0_LeGUv{X4ndzn$04G#$T_>&I^`n4e)9A1Bwx$9wgabkq3f<ofvkn>)>Pesgl|{Q4%HO)<?MC%<F<th$wKnx9Ut&rj>Q*~zB)@8oyP|F#|6>+78~HJ*3nJ8a6Wynn0tGxk`zDYr+Yy4nW^h1L6rWjE7Ixj(g8W^5iP^0~@q)J-$x!S4gE_STAts(p{?sir)<^<P(eyGeO<UvcPoiYfPPdLrb?AKM$9=hoXjQjB@|1+Mm1arOCI_^Ip3#(exvS9@RFAL@Rf@Rnp#ZkPDZ)!tc0_OkWKraaL3XZP{P7c}<o<a+<%jUR_h$DfmH$M1iwQOGntIk`4I{<$YJP2=z6`uK+{y_IP?zfP{7U*CmJnWp*U<af-Uk!3PX^V7-o`5E5zZ-#09JGnmpeZh+vvFpgU_Pr>B>slN(<-XIkqPZ2HkZ#PkA9l63&fcr;=Z_yvGv(IwE}5};;Oi6We*1%4sir*GWxK0=@W^7dF8bF_HRk8l=Q&Oup3qYDGiFYTDYt%^=4u~!?v(m`+jlkDlzZcMyV?hLj8pB8E=)G%-fQRG?R#HS_vhWZB%AW!<$JSY^PKBc4_~q=w=S1)wYMh58T)r~y?-nJ+ac5OJGp-RzRu-BrtxudeSEAw+cHh#@8tUUTYva7P3Jc!*Uqo+o(h?!`Qzkw%%4+dGEDQ+$@TeZhm$f)^FJro=YQE9uJvViU!wZ&m~h0Dhj(pI_fgNcOgH7$;QKOTbF0BDl^;t^HRa()4!PR<&el|)8+3g(#gzM}z7%pD=hpq|efQkP$)?=9tU{J6pVw5a>u&XujCr%=uJ+#H%hmO6XO~1%9-LL|P;72*xTvmEXEz@-<=zJex!MQ!G*kbs^lFELrraK|(A7TYeesTZ2aS1)fUCVX_pXqse<#=b_m#{SG9AB@-*No@zL}=+adLfpyp48en8rUR*T&x}R6oOXew|!DzuxWdr<>-Flk4**Q1SOP)BJRDeSTU+-b*vhe<#0V{$CxD7Q2poH`c59@Xh(draYK+N?ngC@cvE9eTS~N+WU@dQ|)sNN;Bob`~H*Z%2!QO?fX2DYRUr_iiKkHz!|T4-Gojlrrd8WbhQs&{8HUdo|utr%7a&Kx!T+JHB|4LGJ{E`Jor_=tk~Q?<Wsed=Cn&P<-Wd)T<xuAN~-+KABo2N)4lHgo%_S&Q;DWL&@kE6KG^H0kg5NiT<hN+)-_~0eka$D-?u(K(=<L#u8)s(sC}ks{GD7Mf8X~<Gfd~#$@TMVduL^s=8u!>^T+<<(G1i4baH)uT9?XZnC8Ee-!cD-7I5Dm?)^-$`=G<7JTUi3HP6G_(@nYW@<~^Fzo)M1XZD^nW8Sx4W^5jO?k_cOFP}^`<$=*D?)F<Ys`WA`PpUEhx>3lLkL#)WS=&3sl!xcN<7)3qITxMh{w+I_jd}2dyZy({M)TmRKFOv$Q1tGs*xWjJQ>}}*!pWxG`k<bxea?Mg?tha^xjm$rt9|&^&5)^oC)fM8tE$g$_2YMP{rK(c1w*Fs$;q|xvHGpbG>yNL>*H?~W<6@>Hz(K5Z}<sMrfL2-xjujFeFrj3^D`&c=BKa8x(w6&cXECH+fzPpt*>yU{?Y!dPH$$L^1!H<RQ`ONF%K-??8<{<Myq+du}8Wo_qQ&Z>3ZFUKJ`9m{FiB_JbZeHt9@`v5%sxBfzoNF++XSoSNrgyWHrxMevoR)t&ab5_uu|CwT@D1r5f{ZD}`Lg+3gY4PupKoOnK1P&eh)E;;33*BQ~X&^6-Ws?)J{Vr_5TDV$A!GaJ9GRR5bSQ<a+<XsYxNz@jJPG{MO9rA=CKe<oftLQY&N{e<#<+-|GH*rs@1T`5ou?ovoRs`QzmJ{P7N$pJ|$(POi^S-@q3#P4nN$@0kD3Ka&}|j{H+!R{a(69yjH_PB+!(@Z~3_nR5TzuV%*P{s~*v=lO|`q?qz>qfbJydEo1Ms-LyqBvbA^_-U3azqLU9yYM4*51R5|?&XJEue*GkdLMUsS%N7KR3Doin|s@(sq6BfX8Vo#_;QC`{ao0k?kB(KvCov-g%-Hl`!1|d>v6@}cw_$V8F&BA@7+1SC#L1W(^p;X1KGVorv7tst$#baX{PD;om@Zu;7bo@n8qh3*T%={@KTy-{GD7Mf8YG{6w~>2a{c`JD$Pwc%^xS%=a2n`on)GyPOi^SYvlDr)BJaGef|f>f0Y=!j=Y`K{$bZ^ddQUfyEats3zC`}bF0it?tb>&AI<HZ|D>Dp;H>Sg_JM;})cw!;CF!O-{P;OndvD&IDj(1{-IV+PD4gj!PUrsW{m0Uc`QkFJ_JLi^jr}{h-oNiwF5~e#xqke9&+(9He4Jb#AOE!Yka7IU_3`(;yF27MkHyca`4C@Iov-IA7;}5<hps#rml86ycXFq_Z)9$Dzt$tkwLd$#J!OT;^VUx@=B3r==Q;hn-%tJC+C$ruO}T&e$xv)=txiz;@Wan0n)2Wq|75xP`Ji|-51j9Pz?2797Rh$?^L#b+`*Mw!?l<PvIam8&N@ca5pDVV{ln1JOdDxZnKFI#9c)Th1O{jguHEu8LQR{JE-@V5Cm3glAIq%aa*V}8#t)T&T`;Lu6rv7tst$*h}Tt9v%*N@-2v_9Q5K2ENWkDY%-s%iXla((<04knw<uaoQN*KRo?$uxhQT%SMIKwqM1emc26Kkb#D9W>5=C)eh`b$XEN_j0|%%ec>19<MR?m0YUsiw;+C<vE{MXElxH-Yug}nsTdClW6X{zB1L62S5HL)74Me@6~fI)dNYU+@E($R&4Hn^<nk<t7T6dFy+B{DTiFIySRIFy$2Sx+HcBz-O3z}&F#gt)qUNsmEw*0#Og<4^WX=U)H*HQZjUkVQ|hSeb+5m!J`aDpNYIprKm5wo-cHP~?z;|m-DS$dpI1HR8VBe6uD-g{m``c$YVW&wKGW2{lk5ElQ>J8?j^D}k<F|SiNi&U4POgoQ-T&QW<M=zdHvaa2E{Ue|>*V_R4ZiW=0n_|(@;l~FuLcRG`RU~P{PbP1_nYRwlk4-}SGLmr*mV>v*h(G$@|q`&`Hg?n{NJ@L)s)+_PG!dCLGK#1zTQ8WWXb~>y|Q9+@3q1wOt0&!`<MFt@H!<AnsR@x4ToZLf7dhWxwEg!rI~W?-u15IwE8Yl`K-CgrrdY@a>$i$eL!8`d%v^al-rFjXS>GdilzGRQa{m@`*(O<$8T?Hudd@K{!K9DcCDta{=+X9Q2RrfneoPa{*A+~JXa6(`&x_Z?KkCisfw=lcF}D0?}l4G-($+dEq^-VIxo%Is^7ou@^QQ=_fGrG)xWiOlKR~B@{2)Z{>ckRUB{Vxx7x=>FWhU&y`v_&j>r1tA9Y_*yy<RJ?tlMxSN~R(RP}jLfvi2I-1mNltN)zOIm?~dWy<w&%lUUbZQOFMgHL&mxqhxdjgaYhoLoPi;CFv#ntom<zvJiq`_~N9csjX0p21vmGEC<yC)duGx5Vgl(|mApeLe)obVxIeo0IF~7JRL9s%btuxjvt*x!)z5)=N&VtrxrM)5*s5NUpC(J8&`4xZcU{Snp-lsrxZ)KXGz>Kk=OiM(?lm{mRMp{mTBWYBbmPLnpsuKV0I8=K6l?<obT=TXsZUzqEbZ>bOc>zqI||$@Tr;_uiH0^+><IIJtg(@wH#<x_;RoJgM$;wdbUqTz^hV&z<K)a{AGplhSkNITR<?pOeya=Q)?0TzgJR&z<LJoLqlSO3$6=bevp&PD;<6=YX7Ce@;rzo#%{lURQfgO3$6=m~viMdrnHvo#&)-##wt#O3(HF_2;DYTt9yOIVnBY$47roO3(H2*PoNpbN&44&q?XIK7aJ*r1V^$pZarBdaloZ{W+;%+n(yVtGcyLnR5S+f2(<3?&(xxo}E7wn|rG)j^^GUODCCfd;RBGv3W2dTis9ADs{k=dta}W9h=+ZepT<kDz@2Y%I$)S569-#+%MGUFlkr!m~#8Y-A7z`zh3Hd@?1aeHs$sQdydBD;p~IzeOBS-J59M29(&By&%Y0=_4QP{?WWw<_N=RY&N}+@%r;Z*A8Z|Wk6UV{sedQe`?oIC&M+Onlk3NCA8Vg#8XqUu$0s;tQIcu=om?M(dz1H|@%)nCaen`4mtdMdPOi@%U#s|irupgQch1jS@uvBolWX(es``F>>^ic)8L8%f-u<Ucd2s2xXl^}PGu4#)W>yZx=Dt}yjQ#jlRZ)4XO^L?*hI;PX$*uACtGs;AR8wvjF6w&SK*jB9U3;t~Q*QmV&DFnuSs&H@>?;YT+;@IPwrhOWTv6-&)Wrl-9<15Q)!uG1Fq-?iy%ulEt!CE`yT-G29@WnaCH9$e=kvXsarm={y8eDvbdM>w6Y3mw<$SJdx81qNlm};=IN~}l@d5RG=-eYaO}Vd0n`5zg*fUD~JKZZ!?>6P$)<3$Br|Qk<{u3yiXS*p6FaFEbzx{Z&dY@J9%N?fNe{!Cyy?0GpwT}(Dvc;J1d-1sI=W0|}eeP8En{B2%yr{6Nea`!)UGuh>ax1ClHe<fAim{*YxJ9nqo_8SAbUaS3A5XBt*O{iDHz(JAUjNGvWSGX&$@TH{x4e;VI$ut%pD$}p<y6yraB_V<1aognG0it8*XNt_IkP^Wb3T98=kto}MALe4a(%r7tN(JqxE{&%_2`Rha=^6Som^k<z83k^{;%yPPOk4K!LDu8`xI@za&mpY^0l9-t|Quh=;Zo-Xm9*lT^F?d*2(q#Ht1Wc+H3oHPOk6guRUSB?gV=sj^6LxaeX1b<N7jl^zHk@uCD*3Yh9Opo#!@;+&M)mzg65CF(l@{=#o(WI5htkU8C#&U;P(db?P*z_y6~QbQL%nXIbw?>ID1&UmU4lBef_}@4+7^@zd~E{KH6HjMP%TcPU@{6+Z_r;(<tAkJLwe??-&?B7Oy4$5%!wS1!x?gzx=?uU*Igh0;cRZKMiDd^O*@ny=*|%L}EA_-7F>7U4R+cO73VNOm`rHsW7Kyj+A|#HsK7g0B@LD+8sC_{NBrk8o3*`rb`^tsGeeC~d?)k9hG2H^iy$-N4t%lidfUjrgY#FBIYWIQ6~j`C4(ZqEOn1uZno?2-n1^?_I;!3X$c5(nfrF#BWAwMV$KH6?{!f+=4gp8=lB5K%}n1OZZj1Vw~ayT=)lm244555<lxvCH|X7mH7Xle6RTFNc|NlZ=B*UxbRo}?+C9%>M|vM5z5yu@^|s`9#!J!p!9Q&{(i^hbt^@__OnMF|IZxP&*b7)$*#dlxV-K)`o2bcFJC`R{v~6z30}g#hTp<V_$9_&d<)zL|HOqi@NM`GcopA)?}FFxUHER#?Vn*cCB75>jqk*_!^`+~d~2jO!*Aea{4(c5{42N-Uc@hQo;FhA8z}M5;W_*q=k9Y#d_5)pDf|`x6kkJ$uY$ketMC<+_;UCcz8wD;p2k1Mm%*R$W%!4l+jHwfO8g^u9sdXqz_WM&|AZ1>Nr|t9zu~L#wUqce_&<Cd{uw3y1^fdSUciN4;$Pr@TdKrw!cDl8_&?U|xh^gxZjpV9TX>x3_Pmdy#B;-Kcy2ro+=1u8^TAzsKD+?jjTgWR!ku_QJU`ry=g0HHt$1GiF3;`ta2F+>3x0#=!abhbYr{i{|7$63#HGY<!40^S_zn0uE+u{)uE(Xsufb1oDe)_C4K5{q8Lq;m#4o}XxRm&LxEz-fKL<a?rNn=S%Wx_2U*U(il=xZr5iTYE8w}u5;{Su6;8Nm$z?Ha^_yxEcmlD4O*Wyy*f5LURl=xNn87?LM7yJSj%32by5b<)J+v}?wZG`vXQuooPuyjoSr8x#+$(Z9Q$uSFy#~gogen#QFF+cCUjES&l%=i>#424Bv#<K`xE-Vx?{)IS4!oo4<t1#zOcz4YCy_-28yeDQp+{2s^7K@ob#h7El5;60w1aneYDrSC`Vh#(-#LVY1%z0tinE79pH6kn@vtG)xriAy$tgri7gTjh2>#-thR#-V^{Z?j;3#-JecX1C{HP7w+K|B|%?zz36h~EVt_T1io#Ph<Mp4<DCcz*bZ=l1?4UJ%yu+};nx3&0wl+xw?@KKPL5_I@j#2R`Vzy+4cRhE+Yc_jB<$_<-m3{x5F9O1Oo~^+f3P+`hhu--H!#p{ynGc@du<sd4aKd>lT35`PB1hYJ_s&)}0O@u_ezE?kOF#ivu^&%zII;S&5=d>SP_1-_397vfX!NtF0R_+MPO0H27Dr^Ls?cW~j`_*i^2B|Z}V2N%AHkHm*l;zQwVT=+UZ6dyu~4~DPd!dLLY_&`d00DKu2&cp}c{V4H1@C95r1Mh?PqQrZ`=WyZkcu%}HCEgdlhznoB`{Mm6@u#4T3tz>b!Us{}emDykzJdGkrz!Daa1Jhf3m=A$pu|VPxwvp1J_;WL$Khk}$0_mla01>Q?+Bm4JK|5k$@mj^7dRE~f_H_}@veAx_$=NX?*XUbJ@9UD3f>KW5>CRO#5==@cxSv59FKRxJHWAc2fQ5|jkm+w!jX7eyfqw-x5it+p?E92B^-jc#9P3@cniE49Edl=o4^5h6TA`Zhd06-z&>~bydLa@*Td_;o_HO+Htdbp#_PhqcwM|c?2p&S8^WjXhInH*2ycuxg?_v#-W)!SH^(1^!|+FO9~^=E@W<dN{4u-@9D@rV$J^j5ELGxbV0&Cjd_C-lONnoQPvBDGU%@W8l=wHWD=sCz6?Vs^#J9s9xRm$~*bSEw-v*z=rNp<u&bXBL*RT^VCB6xEz@@~$fbDQ8@pZ5*E+xJiw#KEzKY^`qDe;eCOI%9)L)ZeB5?>6P;Zox7!6vwr_<Yz1mlB@~8{ksnZ^3%Fl=vI44lX4=3)aS^#9xDTaVhcFVSQXmd^T)|ONsvnHpZpI--b<bDe(ocIW8r>5I%}ai7$aZTuOWyd<>To55P8f8`e{R5?@Y<uYzmvRrsfHJ^m^FIoyDMj&Fot;T!SI@Ed$Hz6)-}ci};}9S`Dr;SPK+9uK$S@%SFN1>b}3hF{~m@ttrJz7zizeu00Be+k#&U*ey^)%a)lTKEaR7GDWJ##iDW!4L6|@TG7uz7$^s-@_N-@51@`yZAgf7oUgEfp6h+@K@j)_$&C!a2EbDJ`=u%&%|GZuj4P`FTvUPOSldHgWLG4@NN86{7tw3e-nQPF2vu#{|lGk|Ha>j%kcN{4`2WnF2@f=*4ohs55wcQ@FXrJe$=B%{5bp$7lv^u@sl1^;@`m^apBLnlz7;qO8iH71{eN<ONsyFQ6>HZJdF!~!llH&_oxy-1%JSW-{Vr^Cp@aekHJ&8@B}U;e#E0nJR2Uvg-38H@hp!j@l2SF3$t)3@pO+W@l=?J3)68a@nnxG@kE%43zKmv@dF-J;`?DDE<AusiN||XiSL2?ap68(N<8RMCB7FX;KGBrl=wc6D)9uEgbPz}De;3IRpLo74HstMQsOBdRpMzdgbNShQsNmNRpKFd7#AMJkFu^plz5RiRpLeAVO&c5UU(Fj5-$#q<5J=!;YnOdyfpj{mlD4ZhH)wJa_~o7O1uL636~PTAO3(#iI<1p<5J>f;VE27ybL^nONp0)$8ag}67UEvC0-0><5J@Hz${!!{BD?uONkeT>9~}5L70k5iRXvOxRiKan21Y>-vtlgQsTMbeq2i21LJWi@qfwo;Q!*cU=Y8B--LVdoA^I)AN~(+#VID>QsQy&ATA}I8z$jW;(1^SE+w81rr}cJ1z-j)C0+=I@DS@sd|aePL~1N0J_<gKkHUw+LHID-5BuYO{3+NIe+uslyWoBC-mnwi8}AM~;N9`AupQnNe*(70pTM7l9q}jeZm=`n4etee;JxrZupizB9{>m91MtCc2tF7e3WwuE@sV&eJ`x`TC*ou9@o)-09-joC#V6s@;0yRPd<J|4pMlSWv+<eu%kVAyW&AZb7k>?Z9nQmF$KQl+<8R_`!2jTH;IrTyd=_rQS8*GE3BHKGgg+0T!=J~e!>Ramd@_6npNvm{<8a|ve1D|kBh`QsuLt+w_3%1yH(m#S1n$Hi!E3_pcuo9axD|gGuMRik)$wZZ8@w7`1%8EB!7IbB@yhrE@LT)=yeiy+SH&NM+wceRhu{wUA-o3Mh1bAq!604>uMPL&weh-eA6^%)4-@eEctdy)Z-_UBNqA$tDNMne;>}?i-W-1vX5f$FJ{ZD%_+#)8{utf{9>&|?kHc*Ial9?e!rS7lVJ6-hZw1rwR(MO8inqjDz+}7y-V7$<&G07h0Nw;|1oz{@2Dtp5*VRbfpv3=zm+-&vKj9zvpZEp%8-4-*A3THq4?hck#LwbC!;|>Wco-hT!}xdb2>u;@93I7w<EP*W{1pB@`~m+S{|TPPf5Lx(zv92(zr%C*@A!Fm5kHS#hF9>*_%(PPzlQ$}|Hc2tZ$bH;$Xonf+{5ol=EXhuU9cd27oH#9jpxS;!(w=0{2o{azXvY?%i$&PQm_JE3NH)G<7M&E@IJgWUJ@3^OXBy!qWHad5m*Q>f){}K@B(-qm>bW7$3Y8^!~cm>l(qB^Yw8AGGxDYTBQ=T=9|6naBk*Cc1U?LZ8s3dRjr(Cf+>Z}}dGJB_Q!qFF6y6`k;r;Qx(8BxT{h$Z$hYx_c@B#Qhco#kp9}M&2gYhA-2tEWK3X9`I@!{}3d^kQ5R=`K%qhWP?G(HwK#>e90VRL*uJ`p~KPsAs|_V^@x3Vafuf=`3p@M-w7lz0zHydx$4ID8U+9B%{L<85#sd<^&DkHY5oqj*!;7;lQ#ht=`=_(QM){t#Xf-iKGj%faG!IlMG1f|tfi!n}A%{9bq$elK1W=E95Og`fv7gcpDoUI5Pz<M8}=L6{pah!=)=@WS{#Fdu#oUJTxi7sE@z5_l=R3@nS6!OO$@@$z^jSQD>=*MLp%8h8WP0&jpfgRSvqcuUv;Z;7{pUGY|UTi6|Mi?@S4@pgD8*c<PJcaBsS*a!B;Ux3fU-uUzQbFe4=96lX($EV{{VOM-AJ{fkvC*#k+*7!5{1lR(ffRBSs@NxJUSQ8hH!pGq9d;L=4AHxy2l=w0@43`rB06vXNi7$bETuS_XI0%;#UkIPVrNsXW`{PpL3t(SdO8gzz50?_34+r2<;_t$NxRm&Na4;?<z6cJ%rNkG*p}3UzQaBu!68{j6#HGYPf}?RM@c<l)ONoC1$Kz7sE8#?3N_;h(giDF9g;Q`T@pW(-E+zgMd={4ym*-vN*%sjp{x10p+V;R_;JqmECtyeX3A_;{-Vi>HH^l3~Hh4X}F7)Ab@jCEPybfL)HpOe>kHGr)BX}+N5MB#^7*@m|#vg>`@CWf~uryu`uL?`zRq-nDUc3ta04$0>fLDfv@XELs7Qnl9^28O-b^AfKIh(d!7!}ztr3zWM|JczB-Spv;r;g^yHvK!@kHE!#=jupbIS<5j?R1x1(;^qbxab5N|Em1${{T3(l^*'

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
