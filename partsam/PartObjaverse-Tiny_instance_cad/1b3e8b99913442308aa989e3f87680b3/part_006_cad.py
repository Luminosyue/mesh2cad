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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_006.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_006.stl', 'source_sha256': 'e220bece3a65b3c696ffb8cdc5336e62966d6a0435cba5f81af3c727adc3597f', 'input_faces': 1016, 'input_vertices': 631, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.18338394165039062, -0.3777007460594177, 0.10988375544548035], [0.4002443850040436, 0.029216676950454712, 0.3979114890098572]]}
GEOMETRY_BASE85 = 'c%0R}XH*nh_wHMbIb+V+Vpa@b&ZU5&7%-!vGztnTCKThw#;llgwh;rU7`8c}ZNx0*tZmL|o5R*qYd()h_J5o+#vS*5x_gW{o?lH?&oyhVRjZ=!>+6#$buJD671P${NRExGqiM=AYq_+D;6Z~!djyA9>^ESzNplvz`tP^SY1zJoZzq!$p^YpZ6dc}TQ0dy{(sg^*EbVG8-LwCo!Gi+(1@s>j6s-J>1N(*t8~*T+zyZO=cA4r`++597%DS5WGXKB)FQdxAJUr=uA-3Wb&nvYC-MY{~`PW5=-<~cmS*aFH|FNFp*Qbp``$Ie7U(j9r*1%uK<abr?!S4jWzPz=>(GzyTU(J$)xc?j#|2nqc+DiP6dFv7H#Xk6NHbeVeUeew=F%f=8S>(U=JK|6Jd|v!s@auDfB~N`Z<F74=IO7LOd%Meh_^tWS@94)@B>u2(h?AH@{N`0*s7LR|Xg?+^@*6*1^3ndKzt>OMe_MvR==a2a_|tqvU9x#dzt+S9@ZWg?|MZi{Yw=<DN8J~{rB+$gXZjKNdz^*ekNbP_NV51V>_fkmnZF<XcRu6yHAf$k_^C=GPNx;(H~$Jkp3Ysczh`HQ-?k_c?Z@3hoV~-v@3_8P;_E^FXkXd?KXEKxzs`z(UiJU9x4bf)6aQbOQLl8bk^i*R7sda<S^SpCk+L7wt{LF3vG|C@$(T*l?j3}Fojd-=Z`+X_@ymJ~miU_%N<NzJFV3ra@NaK|`hTR~$yNN;>lZO!$}yiCWyNo+)f@F$Q40R)rNpm~bC-PW=h!}`B-#&;Kzz5-@Ndt7_|t}Bz6>u9f4*$uxA&WYdN{elAK{R?TgN2tkbb(yBG2+S#BVWA!Et9vi}rP{iQk;ID*QU*9J?%j$KnLkxflKI;J3PUM4mqwC-yMLyUR|@L$^%u=RSxy6EnhJ&<*~22hgwYPvl>d{)+pN=N(@hr&kzfTma&Gos<2trpk?R%((lY_@mnH6m1;||NSBG`?L|iImrv-JG72n_Gjc9nOEAutcdSaOZ-}FYN><$3H=}Z4@my`-{QC^)*Ajs9mQ{Jm<IEtejE5VHW0u4)@!tXT_5>8t_y!##($v0zawnFv`aq$`{!2?aT>SZpE6H-)+XGqR{K-tX+7=@zb!TVFHT@xx;`KNx3?2h9!J(m3*i6IO8oX6OVID6KHT3b;@5hQ$2d1{hxY%Z5x>of<HPQ^1pZ;3`=tHNMbh5x$>aL<$GsTWy9weC4MF^tv3oFI9UCNm|9S8yFNHtx7TTM_5XZj){9T4^60IHw|F~(pWjo7FiDUPOfPYQW7V#hZf^}v}mP_JySt@?}t1LJk`#ZyL>n46j(-`dU`CRaSsEjy8lj7xfJ@diueQC3_3;K%r)2aac5o^S+PtA(?FuySTk+a2bDUE!zor%cP9xQ%yE97HeZHK=Q{S#LrpJT-kXInY(J2KnEuYWj#_CbZjujM)|d0H!%Li?wmQLl1`#IN5!j`qopO)2Mt{@0cN__b5BlmAbC+f?+c{m=HL9>xF1f34M~l=ZhxI?DZhxA8yqzs`KT2a8{87Q^{-27Zep;Xn1?bsqjQsTYgChzI70-Vpnnd}e;id7>Xljdjm&={(e-KH48C&h!4ex#D+kE&c1=CLxX^Y?k;BH$`60UD3X>eWujy<zCc3J^M9(og{HL?ScPiHMAe_O#J3g@u*w17HB_n)kK*O2TfO{K5>krU7a9tczju7vNMipylmIZi+NSai~UZFlI`7bm?tmmp}m&ZD*hW7Uu{rs`0WcLW!vH;{c8K`B96Vj`0Xytr*>V&IsBL8|9d?#=izlusp0bbtIVfPJ;wPpOzN{J5Bv!_+n4X3a(}hVp7eJMlK9Wi-agBl{+T0{Ix-}llzQI!2EQ%y1f{xt`U&v|yocX1AX@bLEb&|Ooo9WfOjT;-c|nh_i1xnSW{UE>V6W2_*C*x)vqk6DM0@wgSeNXN=1M;Kb0Pju2jUD{Hecd*sDbu>kAZ*Tf(1(L?s?IE=YHhl7rk7mIq>}{>38ZGv^W1Pep}nQXkX?m<1DvHzr#PFz1Mog`LRX(dfx@o-hPk%nw?@KpS(w<Zr1$A5U1|imC|n}UjJ-iowscgzh3#cwAW6=a{h0PP1#=a3`2eLwOTFvRpb!ndC$?j9w@n{L5lfio$rhINA`+e|9yS<yfyr9-PWdTZ!a?h@%^L4Z%IUa>&@*P-{Wgj#<7ozK>OxZ<HTPiBj#;HC*<>^QoQ)*6-E1?j_}(e*GYZC(B2-y>uT>&>&5>N?X~T=PIi=zv5SA>MeLW?0jZBA{EYbRt>0dh_OaD2%eGV7gVKI6+G|dGu8M!nLh;+~FTEgf1}~KMHt);uFKBQ{+Skf@P3k^&?IFoO=3i;AJ<0_CLZ`zL&*~w5edl9|<LGi${CeDc#Gk%f`qjIC6~FcUBFWP_%~{%;uV_bPzkB;jd&i3OS0s<>L&fh{zY^{3GsSO-JtTg8-9~9|Kj$y;&H0ublfVDoU)RjnCC;yS@!Kk8ye#blhl=0oksy9;b8wjW2Sm!aSRZVL|HF1!=Pjp?ir?{kKjM2-l=|qsmtenE91_3d-3QcvP#?r!cTxP-qB;MT{5w35IJUxX;g4^N{Th8!>gjm!N&NPS8*m=XHVpL{kt0d^JysF%ANfjqYoUhl_eXo}6RroWhr`6LfBA^(rco|9j@qtF!n|HQMe=Bw5&Ii(2>zKvWWBc>vC4e2{&N%lk1^{c&wYF0zy2NmLj`5O^fg!DA64eK`0dlWDZhDsOZ4ke1OAfd<0O8W`N-4V6Mn5<MagGmeZ<+;N&MCUF><|QiQ0<xzG33G_nIfycMeMq97n~MAkLH`yzagO|A6!Gzirb)@?73g;+UshLY(kcGLDXwysjJg2<>mgNuJi%%h0dwDg37KiHP$L*SGX1MCVMEJgvj_!e8E5{MLKfWxQ-Lg|T0Ka-jXHF4JW@+YQveXm0V_V}{E0xHbH(w72ajBYyKL%x9bLajY|y+!3eqlZ7(=4RC(6Cbxt?Zt8Fu|HXS{zpO{Qz(3^_u8S^@Lw!00AkSMxB~Lx>mdrQ(Rw&vZu7>$pu$3Hl+RB0A*UwcEzq#{$tQ#L9#BUqGd7Edy_^lg8B2LbAxX#_b0>{x0_^kyRqdv8p;dr-AK^<Z>#1DEVakPLLXrHB?)ZY^F72{HNF7k;*o%I4OuHg8!q2D7-Wu9C5yvA|2d@JIQPLg%QeDbK&&Axmm+UItcIF5FaSjXzy5&u+E9Ct;dv0t+<q5Y4$>!sflM=*|AZozMlm+Kct(0lCfR`~68b0U6`>DaGJx6yvvP`Pfh{91!JnI59w8@17|-`}YJD)_C*0l41(`vS(X%`^C&k-sI=U5w)w`1PjEQ6HC8s87Zh=r_F&>fg1d_;shB$g^NRw0Da|`w`kn@n;K?<Hh_b6a0mo#IJQLhjr4g62@h1D)^TMh~JUnKKAQzCdAqM9QV7cHcER(d^YjxHwQ_4+iEAwhsk*mCx;v6;ma?WZ?p5E{dW)4r?R`WH($yxep{Vjtj}9f2Q8+U_^qD;a9`E88IIFQ#Sy>dNX*Y-|4N>^wJh478H_kT9!eaG?k;}I(qZr)E`mG<S4BSk%UwjAZI~yY;kW&qj{ErJ(Kt>=SBKwm9Oq59cgV9-O~lWejPvHhIvDqSwNbbJVK^@@sD$(2bzihE+64U`8ZUl(vo?r-koojIfqdq`?{MSwe+zfnUrU1y*xwxQaa_EtkMTO|hx+J?g5`H>g5Zzrg!Y^3BmVv%^jon9;_nQ=xYX&2<7ff=_T1i>SNU7Oe=Znt{u(9wWf}4Sc^2=De$D5HNL`=cxX_RE!TxsNhU<io8kmO(ebMip{ur06S213T`XNpWE9&N67<o<`fPP=Bk~o%?Ce-tJB=T%o26@JJ!+dKLh4u-1as3l}7{^!OB-FXy7{rhMg>ejpU)zA^4Yq|faa=s4-!B!OPdFyP?=>0yZXAT;_sUtx$5AgD^Q!O-^cy!Ed48XY{rxf&`}?L8=E?fm$aB~{nQzv*`y{@7{~Ym~Z+63YopB(Jz5?;*%|-nFRd5`ojX|DcX5jiN!Wnh*ScN<bVx6&eU5e|>BCFA_Ru}PaCL{l5YmjGw;mC8-H`K>J4*7T@jy`fF{FxKbZ-=<Wl3!qEtZ%R2*L!V2o<lL;ELk?fzlw44t;hUny$$}Zxc+oxz<JH`<pA<Ihx3m8)LhJ;Q+BQ!4KZ&6MxqWQjw8;b1?cw|&V%}|yYTZm%|0wdj%z*q5$dqR&hcVCjecU@4!?vv8{&FiADHWu^z#biZXeMG?a#n(8|Q^O-<t;i$h_j$E_7dj-&Mu&+dLoq@r^Kl)~&_yRj#P`^=VzX4m3iYEoITZ;#GM*XIqj7>tU}7;<rZQd|@p=40SkL8SVWszP5?&G45U65x+xA_;*?{4{uaM{<~VCp64dO->(tk*Jy+5oPhz-uWgSf{IO$EpY8`SF4ug-Z*jSVd6+K-bqMZ^e!C7p{4p0XE)N66Zy$&J9fgmgU$5TCzw(hNX?Gd#P4p^*5y!g=>eDh2bt^jr?QaAk{`4i--~AKNzE~&tS9C(Zt!?l>LVIg;KjhzcHR7c9n=HCN8|HK2HSm88NBfZ1SZDgJ!+c2ki1R|y7F_?A*@=2S4ne=g%A()tN73(<KG@%B&#^9*K8bq1=KRTq>ls_pDfIiuiaIYDgnAA*gZ4WH;Q4odC)`)QxQX`GCFpnC9PHPYTd4EX2*mMfg!N(FZRF$AANBmy6Z0+MGyLa*Fi(!nL;Kxd5yvzI?E_X~zj_onE&JUM$CqXIB-HJ5dGT9+y_M^H%LOy8=ZAZX-?4BG^4xbGb;!_E{PqmE-_)0RVqHq#3jTRDv2Oc~!TfjjMI3VjSwHRRaNg0pI-p-a97kFaFXZppQT*D^j;Qm1E7;%MA>!AYjD|n#9Oh5A-stzq80>FTUayXtkNu5afqp05#(8#oo-;CTU$SET9Es~RE!s`|n%}z7^1FIw+!s_?0e}4xOQrv)?&7yT+64c7Z@FG|>>UPwr)`LDMV%eZ$KrgE_JsKLOZ9PHZk&jIE1ea;HEjjC@6+1NM!(04$onz#oTrk%dDwIDTdcLkZ&|w#b>3P4>vpL?@mup>5x=#v8P6ql1S8G{-oLkhh<>lkM4XWuasU3U%vJ2qdc2o2_ZcJmaqAiKIdNM2`kMxLKX$DL?(h0MMSJIjNcsDnN5~^j0lbIt8zT3)mJ<ze-&DOM{NJ80lX-F79sZ0p#c!>-U#=VV%6!jQy#w0c>MM1&hs;Miy%YSC?u?T>r!+>K;)C(`R1NTaVD<^wwk;bW>KMiQsmDbTKf_;$Q||5((WO54{kTZ@OZ3EfvlHJZ?imOF(}_|aecBg{`-lbNx7>=we0%>l+Amy<_FoRkb4o`%?~CIuqo2RtVtmWhL!7X8XrF5+-kYTAAnom58vb5z67Ey}?GFE=LYNn`rsFu8Iv#a!E-rrazY8S3<&ZP3lS9jj-<CHW-tRb7<@2#h80Wd(7<YRNwntWmT3^aKZ;q^s?eR4bCt-@jcZ|h*4STm%=y&{2^qZv-;;*2;JKh)T3p?XJu}yo#ndL3{I6keBZTrXo^wVaM%pa}VT=<Iw!hdqI)W_EF7yLIv;E$Mv_b2r;qYm5pqHgVmqduQ5q5Y74XkRTE_bE#f&~9fG{7+ZQ{51dIb4%w*(3b%+-z;?(A@3@aMIDzDu^u){js5J5`kBY^dS)@d9~iI-zgvm>7ky_a@@&HWcG-aI%z0^0&xP^g*CY5mYW6zJp9&k9S23BN<~3{4E{uL(PnmCKH#_D>$y11b?FH^PFZ9B3y74Fe{sil!btsN&%XRdxy>P<woE8&seoxGWyttm&`@Y1wJU*ZJ&3o{^+EHRCet)4H;`L99^UJKcvaN?y5OrkfhV`mrqO8yM$#{=yPdyRm%}2}7z8c;)TF(!_y1lOs{51xmAM31e`TOF%xV{MvN54D0@EmyEdmf*Y#c#Xw2<yQ08o2(Rvjg#dwv_eI`t2Ex&wux$U!M%(*S_%n?IPZH*@N@r{yOwu{NDT!`*n3c=6|dQ&J)#57=IU6xz4m4-iY(}nlyY*^`W!GuYUvilq-be_4RAiXW>ZHe`qP__$jEvbv_UIQXBr9KQRyU`bqwJv=^Rx`Hx5Y`q9X*1>O(ng_3c7ySO9v>vlWj^K#@A8OK5MaeaR(4A0A5bD%!g{=s;?fZzK5om_wFW9#F*emD|wYEJu0ewQKrS<IX9@Ry#4^*kyIu7^Tq!Cw#GHQ4Sf#(8n(Z1_jc#`)311J`Z&SBl^4G8^OKp8@kA9lnFm`#r()OgCKTS+j58dx@6ve#us=Df0QXTl|(aB_xjHN_IJ4>lgUm;Kv(z9;jt)CHYtu;eC!Zf%D&UJdWq6Yv^}ApDVUJf%@d&d!*W%=SjZ94@n$*1Ab>@-8x=$37!|&r@z2>?fO^pv5hg|es;q<wExx*&pmR^l<_t9{fKdS6OQYFG>`EdIRxLE*pe2&-=(><xA*4tvVE+#<Qr8A*DJ?d@H}AGE<7jfSQYETq7sNxC>i~pdx$va_}$9FfvCf~{#bvy<2i@6{GhDc_MR&+A9j1-`fEfX8AnU_C0rLCX@T~er(&I%nt*;&w?h32<GrU|whsEe4!>>LM68FEUdsCwEs5W2BoFK(bt&V8<8DM(?AOFTvi|5_f8w}X&>iiaBjvrT<LP}|FM5Zfy^Ytm75E&-w>R={QyTerEXMlajqfS+(e7AJ4jjkz>+*2KubD^QqgsQ{;`!jn!SGwJ%K1wxQ55r`X9VKA+`xAM5w&r>IA$o~C;7_prP-&TK9!<ypZa|q#`o$GyqB7|h;?Wq^|ux3jN>SL3H-+g%YBoz_a_`jLCX+-G3sw!@CEz3X)W5<T`BX^(JUJK^*Rpz${+CEM6H<;-%)-G)}g`|@t&?1-UI5HwxWId8Dk}%S)XvdK7J?qJupO$Q(Km_*sq3r(f-*pTsN+6j(lG7{Lt(IzOSjf1J|P-NoXGxkM-g61hoHhhTrK#%Kf<cHSYiQGcV!KRTlMG+8=e^{2lSLRmXiq&wTQJ&Yt*#&x7ycy~*j-(%$Tf=bE-ov*b9{i~hj*AR+_SkM_}6e<l{jI<qe~?#qLtFkZFe@qV!~-Y;3o*1~(1xxC-#&ik-;cX1wRR2ub}T9NNbriV+N+h)i4x3(L<k4QU6;%x4R{r%b;`E1LH`;M=*aQ+MQNBlDTaQu3$#rnB<IO5zohwm|>ry+jhNcf}EO5ODDFR`xXjK=zu(~SDtF#jF7r(wVLVP07VG{ySR0e)+zoATble6JnqZ=Qkped<UY^N-S4H;T-HKdCIfpW3|x^RNcqBkA>%FkTzq;QStQ8tq3MmG2qMtB1(@QSHt-JQt7fL;Z`mA)g?8N8s40<2~}K-7+qEbqC^f{71&uGH;K(N7Pe4N8Q?OmH3Vy2c*3t{X4W@RR{epY=if*4?kjm?Im#jZ9PH!mdEg$XE^X&qD2q!I}ZFpK5<|1yxI|p{6}TQ{r3XY)81-5-tQ)tg8%eO<YS(K_s7d!@!Tb<gY1_rs<NyP=Hv=^K9MI2zV~RCp6^qA@Lc3topa(pboi+FU0UNg$0c`M=j5IzeoME`@LTpEpLOS@U$fPMeA36_dw~1_$Y)$H+^?q_i2A$E!28IAUTpsj&-d~b$NOM?0NVFiA^BM1T~VJ;5%A~p!Tx4EDEVj?M&LO?a5j9e*sLnf3vrWBho@b!zI{(E$F;RT-aDDo9>jU)=w-bB9=r_gJ#ZhbmClL!=frbIb0fY#D$*GBtdoHDfu6Fz<_=zovi)o$+Q&Q2N*zvDMLo~pJ%(-me#z4|VxhFxek39P)f=U~-90n<EpQV1TdWYqCA1&<4Y`QAJz9b9X$w!5__kDdPOtl2lJ;hYi_}?f4!?C+dVHsy7W2ebgYUH>JyAEG>{$1@JVpMQ{UpAl-^Km%`;vIBrpG=&JzEyQd>D-PNS4MY&d7dse2+TU{R)3;4f&rxA=f9?EUECEW)aUjnZM#bJs13zt{Uo)I1A^shV*y8gzKxtS+HK6OvUGs?l|tsL`!_TISrnB^|^y_`J9CBFcR?{gd@6~#5emV;5Z88^Z2J<FdwpZz`S+MgFLU##P=Z`i|v!R3-iLCZ7uRYxCQG*@%+fA%M$GGlYjBO#Vhz7wF_X}JJ=3L`*a1-?+7Q<ZE0$Z%b`MePMone=6QA<^I@qg-jC(P^M9+W3%--^bVHn$QzVW#Zy)K`{;4|r3w~i8KIo7A9gF8)X6HwzCH{I`N7-xDN1Ye#mHKE^Z{m0?*%a;V-7rsFzT>-@Exw5Vq?yDq_co($g<7KyV~ZkBKR2nHy;>X8p_eZ8(NFr>aU8Wrzc&}-d1e}1U)lXTpw4+?5&ug=>{obS`29PI-+sI==55)5$j5yZ_Sb7B=AjMm9~=*cVLb`WgYQwoMxp&pcZp+3euZ@=_h`f)SWD_)`@T=|v^>D`cs(7)(b8<E<YOrsh5AhHiRZ>Yui?9sSoke{N=qC^-CuINI12Om{p)6^=ic^`r{l<E#2*@q_l7sG%KBidj_14DgBQ5oNM3_HKdwOgin}m>2F6N!vttYPtAXn^>G$zu+*gd+iaKoM_4dW`=r>?D+Lt_o^I(V<zVC56fI3{>f_m<V!Tf21_X(P9z0}P*b28>n?URU8cr?yy&Y2Eke=j4?pM#{mt!XaQ;p;85|B2_}HtRPWrzh?re)rLsKQ~t5e#hk==Kr%O97nT;$@*sAcOQ9%mxTYJ2j08qc#Cl<871G>InwpU{A}|M?U#(iIG($K>#?&Rkx#n2xc(o5`%3G&&xqqv9OJbD-!0kVzF@!NCSqM3b`;kGslFqQHecqOX1_0aI-dMMoc4`yzB6}~`rA7H#C|pUBJHhu4CbekhVP+P-jV#Rg)pBTIn&_#tb=y!m&pg?QX;MREv+ZuzIX?oOISw3Z{5{L;yY~DWu3H5%#8TUU6B9uFc}xULr%1}M&df5WnNs*{K|#+6PjV3)XO911<jHl{?AviuEw90{LRjV@Ekg4HGIcjL6>#FHo7qSJ-!9~{=F3b_>y=Iowfx0e`S|-(lHj#r}h3g9<8-7KOJ2wiQl%%AN%#H4%Xp1bx@xlgK+%r*eZUlMPu<h7Hz<DkJe|gKHGiKZ_s$`@2!DYXTG#UoIO6c9-FjO{I*Q^KF$`g3hPhv!8rd;?uNQ;KPP@|RE*4L{cRuAXNwi*uZDPkscjvM{rb8H^J>-s94{G$B96lq>;HvdTz|G0i9BO){AvmKp2n(=#(uTiC-cG5$cFqISP^IN4a}1a%P`+AOh&&O$BAECy9&oehgBG_WRCmwbolP@=SIYz6p8T-D2ekzk<EzTn8)3sK~e{Mu0+&rXkC0~UbPA8R>O|?-?9Fizpuf5#a=-BM4SgL0Z~{V(qBY;w|h7r1;k2yENSk*pSL>JpT%=Aj=pyh-}M}hyTe^j|Gw~R>#t%Q%ap?XxZ@t$Pj|+A4y%Um(!w8LeBTA2&Zbx#zb78Tzrlj>ef3!CX_@f^_1WMf`8x)@!8jg$hWNEIU>qIeaeWf?8vb8g-zKiWx)+%W-+}HJjq^pG8o0h~nOgj|0a>xXwxd}8N2d|L)}a@!e*!MxyzH7;{Fd6&aQ#*>3hUc2e1B^DnF;HR$90?^>l6^bJxeXrZP0jJuU;&KI2k76x?=Mqsk8MB{MwQ;=(p-KT+cfS<Gafi=`f!!U%-0hV@CV7&9UCLAAvgeD+d4Ov=U#t5rugY>Vi6a+Jo!o^64?3)0ak`Ln`CGHG5giw@YP^=hjEa^L3K+YhG9m`+KyW`1MIx$289>h|@G4*C8+5Fn>zbM*iz~UFukfb#F&q<hivr@+_H*<Km(x+J|n#b$G;a?C(!6d{3Igf%#DJHjb|aKH}H?@1brNzR3D!>CgiCRKhx-CvV2MRA`I+%2Wj3Egy-+dFN9{<nzE8$7woT&)8zSAfJRVv|qAC;@ghFuRjXK^>Fs{IA8dNAWy%p7?(7C;a@)$`2>!_cLL9MBA?K?Xm8Gq_1rQHe&-nEGmH0q*~Vg>DYhE*4-CNkKgsWgqc<X-*yqSUBr~2{Zr_49dyZlKUl)sfM(jbq)!HKdB+NtYLT>pk*!~*dD{39?%Dl1^Dj|M-{yKRc<(M0bb<)Kj-!G5KEq>j73C`DF;nz$naNW`n_mBFR5%}&n%NgANT3qm5=Hg}IH+S>K`;^Qv_6ENH`B%P2I`xY+S2q4+SOzVZ)-y20Kk-#g_1|y(KmQZo(5nBB{)w+!Ww+}8-~Nqn#(qW)0}Sg=jUe|Y52lVF4<-+z{zV=}9!VWeRyveC(XdH|ji*i^hZ)w_u-?>ODR?5cC$eoX{&p;XuXHpyn6Uz>y~(Q05Vlhqo`Sn^TWQx69L()t#!&2GSS7<6QcI=aJls~Ai(H?-sYz`}R&8>yoznE=8vIQaYE5!Zw#h-x#BIgZxvkWlT!UPlT!q{Jf3JTn!<rjbmD)H3x8SzYCS=vVnqjrcRk_`YZCa4MxvkpOGfXE}<F=P!O$}>JZp3XbwrxbMM{doSt;kKe-N7&)!#a|iaa(Z+x0QA$_aTRngSf4J-_kHYvJbZ{Y}1Dvz-@oSIvLiP>Pz+`cOtjswuQe5pmrv!`Kab_E@~-qO==ZtdU6%AJ2ewo%^@|HdQ&Hmdy@mHqsf8fuGDaHHI8W$YGZPD?sqe)54j$H<4tWs4&wg#P+O9{Id=7^jmQD4NlU6Pxu9Wb3`=ELcEi#cmPJ$lQxC>%jbYAg<7!w1!(0q2X;?+WN*HD~th`|b3^Qr?FPmYh4O9PH3>h?aTc~MS*`|zPWeqE8SaHM3Y3lT&X+;bxZCI#bZ4K*5Z9^VqSfpVCse{N-hK=Lj$MJ89t%i-^-^cK8igO#5&#=7I{NzH073SXy^KXjPDbJ06cjMm*G1e&NtF#B%%D?rbhLUr$pE}gK<U;&g18N;|W&X{R*3Pi@+~+Rra}>D;wLQ5#+xMWgV;-U8w(P$R`)fmA9a>xF(3b5RP(8_>%uR7`V{iiu^QP7zdy`XBUz@;650RBAK4#cl>LThP@_g!k>LIey*W~@=w^Y^NTW%|^$s7X6HOXCQik)eSb5eVgmF6X9Gc3X|C&NCPpyAw(AcvC&QHPKRk#o=#mo}^@bs%*Jc_4W(HG&+$JQS}nau{ORHk#r{n&MH^!DOX7$fL-KCgh;BG<63#2XorMZROv<zYivFAP=G`4yO(whm)63*N~TxKhoB)rcT_qY}9RJH4f)Y7z?GzWM_`gNp36uNt)sqYCL&9brCh5JeRtH8c&Yr?^jUIk(H{Pe%C)Q$L4pggQ>mAgUJJ_-YLe~n{&aN$3{`=F^*4Ba$<^OCXqHb#hA|J_|IjIktuSGq;4a(Hms{*_ciE24Xktq`966zP4QgnOtOm8o3Xl*BWQ|8Qu~pWRw0ih*Q6<4szH});N|RRDRm}!DS0tX@pS48@^tc4>Ot~U@@A^ado#Bc2XbE`$bsa)s3XaLktb7Yk|&evQdO>Xsf)>d4BKjO2z3Kl^%cT=ly1=e<hCJ2{)(qix00ujC)1|UH<db_I*qJ!eu`SnPf^eL%u{K7?u*hH<htbF`#Xd6P&$DeNDZM*Aorn0Qzww4$y2E_$WzJnsP)P9$n%(^%5@%1aWr)rc^d1Ycm?P5GQ;*zm(!MUt}SC5#ojz-Qd8Bjp?C##HuXM#)17lYnA)4{O>Ir>P2R)4Ynbrc8vI>9auw=w9v>^1pXyU-8Rq6q4W^bM2a~(g$}nCH@*c+cU61XCtu?Hw3A&Q3G?uJPadkrn8rIOT;WWjgsb1vK<gtd0H>`<a6KRU0Xo`o@6t^^NmC;YUVYN)qzsX8(l9eg0ZRj||78}-ys<wAimyvgqk5d08A0;25ZXq8b+o_w#cJe;zO7cE(9CbQ5jy#1rj68)LKy6A6AbU`&kv+)&YS3*OSefE2)EM#>@@nb=@@n!L>O%4wavXIDIgY%MY9ntXpQo-PpC`MRp!dki6t|`7Ca^NaeW{(uzsIsK=f+IVm!X^^Gii!LskO<W<Tf<L6{u>?RN%Ja%+$ZhnK{qi(icxwx{Cake3cqYzDiD}DNdrUBqxy{P}h<lkn@<J+sWH`{N<r3ZcJ@RZcMh&6px_}B#$A_p$;d{Aup$nCMz9FUQS+X`g1(5r72!dQ@oKnk-U+-ni@rp;`k|6$EG?C_s|p{rXC?5CLg5Q$p^^?sQbtV$a|@A<h|r|)G6e3<Z09Z@-%W!st36zxfxX*ht0UHI0JPHS(#!xeXGfK@_OnT@_KRtHIAG>-bCF<-bCI{Jx|_G{zz5F;YV&OE^C6eC6^`pQTvkp$o;8{$^FST>TdFGj-`#Jcr#7$PU>OuPV#o@LGpI;R_X!rR&oM$FFAp{l)8?*lst(#jXa6mi`tXii`;_RjNF1;keY#9ko=V6t;Y2!P4Q9cdh${7Icfs=9Qg`$6Zs1H9d$qX9XY!R`jMQS<LpjV<LXXR+>z=>?nn-!_9ust=TU8B8^>}UP4VwFS@CM>PV#E<M(TFcpY=iUdg@lwpY=rXT55vn&zhrnId!S&&l;t84t0|0&-$i#47Hc(&w8lXLTzFCvwkXWOf6{ov&JgULw&0KS(Be~{eH@E{k@(a<$8aV<NAC3KgaXKIgab^^TidOL#}XKf1gtnzon{i{e2EnoS9?oZu)cnQe1)B(e&qhr??F@%=G8{s5q25k35fKsaRcWd75ypQ>J*Y22*^3>PuFp_z1NXS()M;8qSGI)%9d``WjJH8^!8+u$u|z_Lk%zn&KW*f3iBiH#hycK5WjsJ;}b*4&)B}oiEj&>`QJ%?Lw~3ynbH~D{eqj>_cru_93^Ub|JSTw>RM&t<;OAxHGj2S)ET8vK~#y-DnG$qtaDmrLkmxau-@GV|r1?(iAVC#*$|ncHFR8)NABj)KAoF<WJ<5PB6vIoM4IzP>+*m8Dl-iu(T$qs|h@SI)ds-9znL!6xX3CUc?wGmg3q*A7;Z!7^WUj7c;B~O>r&5f(>hESO~QdS!n}u2sx0ZxDB-yxed8IwHUb=`z}vY{M-ane1ZDR1XlW#e1UwPruZiHGx;X@9W}iZ_#L^R6SM@m1Zz@|TAN&u+?3jo+>kYDN>ki{rnnz9gxrrjfEq|1K<-OzL+(rNMJ-S6MXo?q^{T*a#rIgl3*>v`6V&tM6XYc7O>z?XBJ~~lBKZkb)#VAd6&GTynv$Ec7K$q}zX!}!<@A8LoghCTpQ0v_Pmxa>c7u9}nnX@wewS#9Us0csUy)syx5~?f`E?+>ko~Cr$bRH7>Hu;Wxj#*DA8KE6A94?BFLE!|qzAPkxd*utP4O2KRMqGUP4O-2De@`S<yMM%-J&UeL{t2bruaVf68RGAb)TmA7gg2h7q=CcVcq=5WymdPihEMS$UVuS)c)j9auBr-If&ev+JoGKHEK;$+=QmsjjHP9#%;x^sJF<sSQo|06lZjTDSpGhKP0~)zoaStK~wymdY^os^?FZJoP~8%^~yq1>`HAxb|rgIdy+lK?Wm#TcI0l<AaXZyM`~+wYu2kHO>tYAVlS#2*^BH>O+`+{db!gS=b@^4<>9vCpRD0aveK{QpX9VoFvTV(nBojhFvV%8FUc=C28xv_&gTSEoSpif{GQ{Gou;@l)s<YCtW!P6I=L0K9l0HA-HN8TGqoeRBkS9lrr4jRxH;8}?8TZkrzx&M%|ot1E=g5&EJ;mEe@WJ~Fx5mhv8IJ-ic3+`kkhb^rD%$)Q?rw^vtHGyI=MR8liG^xNp4T=Om0u^PW2~uCwHYO_MtW>H)kz;Xo~AmOOi`+KkLyH*QY72OD#n%#eJwtQ{0&9N%mykjcJNIQM;2nkuB7&WDD7s>O=Nne!kTD<oe9Rm)e-zn0+X|YK;3?!yZ$wla*$60zW3_GOQ}K8Z|Sy8o7#LxvAex(9GoTjB}Z)`nXI}e1>|Ke1?3Rrr1HfN_LR{F)XVS^c%OYlE0BNaep6^GjadQQq}&HO|hSfYf~FitCAa%8_^X1zMfTDj#`yml{G3yQ(T-{g<PDRKSdq$(-fyO?1KsVFEuw=nc^2zRqGct#doNe$#=+CsAtGm$akr?$#=;gXt&w_ZH_@Y=BGG6^&iup{1q2>`ZG?y_ctr+QHxrHn$_vgy@q0qruZ3SsBwKpQ~Z>s_%l_F@n>!;PES)@f?AgRd%R2VSo7s^a^2|qj$s$5XUP}H*Ql4tN}rRjk)O~MzoC97zahWS(ANw0bBFwa`knm4u&;)tH}<KRI(Mo1Q`3{vksq<0YX6A8yFq?LK1@AHK1|+CJx$(C-bYh>ih7rPiu?~vvB~J)*|2PCKF}0rp*oYZke#R|vQibtiQ9@FGWKcmL-Hk>;)~Ri<cnkn^#=I{>*Am({zd&k{=qu_;<n<9tZ_baMsi-miWpYNu%gtw<h*QClv<2jlw6LcxH3&~NoqQBNpdEt8p}-FR{WTz_z?9l`4D+0bvJn@c^7pbc^}7h7ftbT>ObV;<WDrkxlAy{IjCwZbC~|ji5xV=1*rMS1;{0+MaV^1uM#xH<*DV!<ygD&R5x;Ya&c;Da%tvToSK82gLxFEmLRMBJ;Qn^JwR5Pn4(sRtgF&vDe8PI#aJBUSXJh@nrVu&QZtd2s<v6Vt@ssxe~kQ!{F<it7B!Ka$XsvH6yK&Peos9^eoy{JJx)H(@%~0roZAFdb<E9rmL}&Wm!i6nOOY#5E0ZgdD^bnlO60=StmMMvoK#hdoZMENhWeVUOtD72MOLQxC4INaN}rKmlE2Utf2Ju;Wr8XGN#AX<uaC(oSE~Qp|Ap9}|I~9j?LYsAV*m4(|NUnPDS!Fci1ok!k%F&J8uhKJaSnBo4<s9^ufVnc1uh}ty8'

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
