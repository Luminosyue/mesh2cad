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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/649dd4c47d6d4dd099e518d6393e7c5b/part_005.stl', 'relative_path': '649dd4c47d6d4dd099e518d6393e7c5b/part_005.stl', 'source_sha256': '92604bb1710953b8c5034ea1c03028a9c7689f739dbe9a967be7277ca3f85330', 'input_faces': 907, 'input_vertices': 539, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44182175397872925, 0.05841332674026489, -0.4999999403953552], [-0.15890654921531677, 0.14344054460525513, 0.4668556749820709]]}
GEOMETRY_BASE85 = 'c$}r23z$vS|Nr+vg~+7|Ntu#R^p)#i<hT=xN*Rfx5H%Qg$~UL$SEY-hyNq1Z7c-2@xE^zH8N-aZF;Py6ZYsB=GULBL`}5jo&N}t~KmX_V^E{vD{W|Zn&f06Qz4m9Vz0Mi^`;@N`W$C}0tqa{NZLiqUvLvclQP$Lv6DN;(eB`7%$0f}0Sk)b0{<-?jy#xF8kMmelt!EmI7&+<jiH+JvH;Nq<)2L~5qfz50PM$b?+_3QzM~oD|$ME<`BW-`u=-~+??bnT4w`|umx@D85(f^MAAO5RsHz9DK$I%_qmL9jR?_`U&WXQ1{;eK2&ReXQRBlz9bkN<eP`hy+ce;}56Vw`#cm+mlq>iL@=KU?d$bi3mxW~U!<{Go}f#kWd2;ioyizjI8Q`my+1D1X{1@4a-b)}NiKe&<`$)UW3FzU=?1-^aJX@z3--YWQ)7^?c9tHT@_0ZwvPWSr4f1?X}LSr?_{KybfmFkMDK-#O&+x4L>fBs(zH|58mVWzT#eHJ?(D^sNWNRfcl+cocb;QcR7Y1x5=r;>px-m{&sZ(>VFgA-xSdHT$``w)kEv)w@Lfw<hWwPAC#N=kN&7{w>s@PIo9zLv$~k=oHakk@Z(Za)qe-Sv)RsBa~<EG)lSRDPG772aBq?NG3s}WU#sn}m2dbR<~a5Ei~Bm|eOYa_{tmN^^Yv%7(emvMCp+yqJL#z5$BuC756s#^ds<V^i?nmS>BpXO{J@z69Y0wujd2nv9$94gT=!t{2>cetbq^Ll?)X;L4P2Kw&UNt}$uNED@g7Mx{ZSRRh5Lzn%c<Y(!Ibd!MEcg@?+XooaE9K$hrWyO&Gskm^{AgPXor?RS!nu0c7&gockfSMIDXfP&T)geO$rR3`z4s$*z^;o?+Ev!_a0Z@J5T%h#PDMEzgE9pg@BIFVLCqd?BuxBQ^NZ*<WKPL2=6yv=7nOdXQnewd_}Jm8h%H=j?bdmj_=R>jq>qYerLN}!;hKl_<?<2=NW!%!rFf<&-i!Cdoxd}Ke(ck_W~u8octD@`K{yoyA07hSvvlhmj6b}x4oET)`Q>1a@yl9npUXw9LGPMr0waGtA0@Zp+53+4~~0G{VqK;-<EXI{G5@d?eYGyQ``9j{&p?jqDqq1bGPR0jBV<Bi*~Bt-tmL!bLr23(@y`{_m8UomewD8LGQ=2^Yy+<pP=O*8??r0|GwRMhTm#t(m(n!ef4_n+hzK(d)Df47gB$M9=H8O%`;~g=zNwwl>YJSe6(+mQ%`jI5TiZb15f80KJEFNPkUTHn09}0_&B#tYCD2y1B%1Pc_=@p-D9*T`oI*;^J%@+AJN}wkAF|CJi~7_-Dyu^q)&TXKQXNb?P>0`$3OPweTE<RU(NGl>l?nmT`j#I$KHtFk?|9&`RC+BEteLn{&?Sx@bmShwdK5~uh#b8sMjm4srubUa9?K@8UFaj#(nKgYr^#%;#^<v*e3hbZ>)X?zxL<Y2KcwBPrkAa-mZBmt)co6dC5w<!R(*--?P-OYxIvl{x`#S`^O)D&hY~~s~Y1ckXygN@LT)!zRtbL^ke!bhx>^;OAd#R2Vd@W+Wwv29}XW6)~=@y8b0G8I?|8nl^pI{JHI#_eqEw>z2x|T9j~eXm`~fEx1_-E-S$WNZu{{Qcg#}XH(RfJ-h0~q9pms596y+GhqiOaQyjOKbKJy?>ZadnvK}|m=e%4$u)V8MPjtq`T*IdxFMi_oE=E1B@7><WXlHbWrN`a&&7tuA@fMU87(V^;H=q7-{pf8+4~6%SRq%_J-@4*Zc>AsNjk$(T`=cZMm~P3YzxYsi`+ezqbza!=xcc5aCvSU8=jpt##ixGDR!;r?k}>$h9N*t5ZKwL9^!Z|QKlMA`;>;ud(#4wpH}~PVF*<%qrc?eN^*dK#zMHJ`-R6cyKllr378<@g4htHXzB>*heRmw<M{kZ+zkNL?Z&>HH996%*w!gzJ&2Q&Y@o&`f-Detk!`fU={c)C&H~guWbsg7jvXRF^{`jaJ>g&42oBE^r-nWc-!I%1jelDh*F)w&izb^{Ej#l~xy}qg66&d$S+7i=u@0UoQapL;Xsb8tzdBwW$^9}hEbB*&2Y&xKR*VF65&o{Vfzxos2H}bZ%X`X7^OL|`vO)oV3nCZqkE#!Bcxi;JnZhS}mHm7vH+u1kQ@Y|ku{NTRhd4?Y|TJO7^?alH$kGQ^X<CE&U^KZdry&pG@q@OjPCl*vMG<?S4-+acQ>-#n|=Q@toai0E#UY89`sNcIL{5}o&Tt|PT&vgv>>vjDenlJMA==Dm;DhzMGFF)7xS<m?Mb4;K0gX>49d}`EV<!>~7>iL^bJ+5!1d}6dSF>it62iLt`7(UK}8FxAPHgVl^g~m9~XkhxGc_G4g$2q=#ZA*@;^PTr#S8eCoTh(Vi^&Py|^xghB*w6Ic{=p9>S2Nmg?OvztN!D@Xwm-P*Gt;O2*6s+O_Pf3>`Hbcp?~j^?OF!0qlH^~te2a?O4<!kjSCe%<ao6YmlCh3&B^PNu9ee1yz4Up_+ew85;r$al@Oi%Bx8;0G22oD|^|a7=q-3Dx`J@cai*-m&vQtlDQhGsn|M>RapJ({)dM2{GyKV{j+tu%&>%hR-<+=}$v`yR7;ZuFCKf6@d|4D1<hxgZomk;^vu8b(3WLz)r-h1;5-@PCA_A`C=ehm3*jPvzoTTc6}q>s(|vpuFyzxg74`k~DKK>f}I%p*_fb9B=C>QC6pI(&>icdU6`{q9?xc`EeWv1X3?V+)-9y}*fhop;uZQNLR+=Cxf#hTl{74}C{=<BwK9zSnm3GfjVdj4=-;uI`|I*9y$Dcj)z7-Cq5K1m+#xXYj3VsearN-9Paa?^a(wXASPA`yO9^df0h?wSLZeq?PXDT{!lo<FEQo`>$Vyvp*vz;IwnqN%im3{j@-Q-e#viSDjG*-W6JY)TZ~e{5O>USp7-oS2^Q!)p2~?|MB<ub*K7YtKZ+R`*jJ!v(*n$ezMlHe@wpm$0$EyL-=_`ulh>;QPEq~UyT1H<p*sDKi`o5MD?xe2OZzHvX%O69@P1<bgt$T*N@Tt6K~1mrr$T9?Yz9z^hci7_LOeX{ehJ&)%PapzU#TwM-4w>9ESV}r*%K-?0?Pj9qW?Eh8y+!J2qt<`zC%1EzkZ*bkU4L!)HIoSM;jsvmWpl_b)PhcRw?-Jp0Dh7f+bwyY)@^fBC^fKbrMK+(#jQY_4%X`c~e>_4?je|CITsS^s>KXZSHASpRe|%kv!VpS3N=^mQNApItlO@I&jRh<bV)Htye$AGcNa6Au4SX!sHNA>@yJf4gzNyM97{&139yhWzml>Ns)tY4P2C^1u1)C%gO7zLm{6-$8o5WAE5!_?;T-d=dXgmf^>(U?1Rj)9>)C9(Pu1PPp&xKfB*A_*VW)%lDq=Tz5DBxW2z#P4*Lh%QE~9Guhv0L_6=Kp4scQyymNr|Kt*9KiL|40Kb{~_e|I0j?_HnTiFypUcXnGbjrzN-j#RY57GL2{H*uc%G=fN(_hOc40H0BZ)IbAuhzeRbiS5vL_Mwa`zAL(yZ%%9eN8Bjt-OtT8tZW{eD$T_Kjn4GyLl{e`7CF=TlWTyeC}U9P5t{)jC>yQNBEt56`DtuPgQ@^<gMZT=3hRA`px|BUp|@o-`^14Z~o<z@ZJ2c{pMRfQT<T<r{9)OpnQVk2eY-`e9IFkZ{~mB^6~hZ=iUAZ`Js71%lns)Q$Ljdbzbl-YomT#VyZC?m))-Z;CZRx{pMZPSp6=Rald<)HBz7XI`sUwtbzIw^KY5&HRfyo(!X?HDq_76@_V*2^W@S$)eq&9U8WyeZ)l#emL68W`zB-Fv6dcEpM2|nFBVvmt$ycRV|^9!6E+#^tH6>B^?8m9WG%@veAbP@ti`6!y3zIhOSV!E&pZ1E<r}{Hyc6lW&pZ1c#$T_#`#p=hPF|9tKKsw1b?=g7^?5!`%vz@3J1qGOU)Qnz{SW3FeuqJ<!&e+te+7Ob`zp(H|9|m(_5132DNwrXnBkAAqTkz=F2$dxe%oH=bH|dm^?9yibJhb7QGTwLZxhXW=4Jf1jO!BIec_<tw@%RKuRRfdTW|6|`TmaGSZ}<b-;XSwW%OJ0o)UeITg*P|T@`pPn{dqV`)VGrtl#iw&<{;DA6`DE>zT#Vjqwnj>nSjNo)^5img&3unUTJ?fbVz4QU6rx-=yC!lqTX&(ew3w&-pIU=gP&SjqzaRUexjMX+v}TXZj8rKK&ew^y%kd<}l}V^ry9{U%$5sWX5a%FRG@#`<$3Jv%v7(=gmmpeSQr2*BI>&92~CejYU7@hS%@U`_S~=?^z;!>UaHMVot7czp(EeT==^BkLkXsm2o=P@LR`g`y>6fvD*HOUv(dQ;fuN9{S%#WS@-c44mH{z%s*RT__W_DIAi*>-}Qr^JfuGR0Eziu>vL55<ec#K2h)<ZJ?+-ygty;HkMQ00rzdH>?LW&2Z@(`+jq-~qf8JQPhy0iX%>zZRnSSi#wc)<iexdqpzGa=<FW2->8SCVbALC=49BY>EINDhE`eS<Mg!gk|!7aL;kLj5c-p_$Z-~FBf-y734#~3H<6IwCN)bH{=`>VT)3_sy5V_x&Oy;}XwiR|At)%(3|CG{ulG3I4&+usj3ey7=d|IYWOZGTgL!X;f-pBS&tWo`DU-z`2RygmLld(|Ib#cWUOH`Q++rTunpoBj@`_3PA=kP_a`kRO|->)Ugib)IVd8uee?9^U>ys{xMh_kK(M*LlI;st^93<g1tQyK6mthUmO=`LgLh(O1{WmipdS9n|+V=KG7M@ms4uG*|OR=?a~XTHS>|Nbkq=E!=O-)PJnG)|2*`>2tpXBYo}{*AKL8#P#}+eYW1Z&(^ZOo^Pj>?Bh+tudU_#&fz&d-SkJ*(chU|PSbv9SwsC6jrrc^DLvnomGE_6(O>$3mT$3tfB3ld7F5#l+#*wbcimD@*Yrd8MT8%^FVy$nxjQ?&KZEH%>i+hf8?(dv)1O{!`t)aFq)&gkzSV4Oc6j@J`Pq8EG>ywP+Mj>K^xbt=r0=e~@B_CW+85q_E3=h;FWF?lzVP<D``aPk&7YYOKJB+Mo2%bAPJQxcF!M?LhmHDunfIAK_4^}z>UVvA<L>*y`^SH9nCAb+P4<QNPw?PVrtj`!=SBGLKDO)Mwlpie{l4A#dfbMuso&{Vp1Vu344>zeK>T0$uc)@GuIpHy)4dH}(DKYv-rZRT4WEASMf&tZng5LXT`rMVn`!$S&QL#LG<lWhpoY^pFI@-vat`RasNn?l`Ms9+$R5q-4ach=+n@c1X8R0(Ts`vYF3OKpzr%F)0knVpw?4r6^8HaxVZPzB?(#?ath>tm0qS>c%Jb2bV#6P&`z_v+lXSkgwY71*+<gh_)|STg@{Vn2`0n*`f2U#H+C<BHUtDL_-$?z?e5CVKpux??_=(Qa=XrmF8b<#oW;fLSZ&0!~d^}iL`g|Vp-E|kf)!?ta;p3sq|5^Qxn|R(?q|ZAIelqG0W;e<=eE0cce}wNoUqtx+_VN5qNq@g&-Lgu{$E4``<m`v|pQ|7H3(s-y>AZRK>srs<({-Ky*SW8p`fq+g%XfN9{Y&+AUWgv3ehW+6S<+eaeDnkA_r9q6Fr}~I4^V&13Y|AgU%~IEzW2D!N0%;qrG9VvCsFe@-$Qw$yQ<&$qR!)&8fZQBYp6fOtMd!<oxgrn+H;EbEH(YnDf--0x&;3!^#^~yO4~VAk6XXI`s|lR7d@@>PJIu)yKcNU*Yv+<-T19Ozu)xb9>?c*gZ`p9g@(`X14HZ8n~ta-vCb^>b)UAZeth<0|5l#;Shu{dPETk5#@(NB^Ng=fclFtyar23<_Eo#X@4LW>k;R5T@uE}Sf8sIyUa9t(U5?-NqLB~1wSQHAaFXsLv91gG5qZ*AD^vY$-E=>^cudhh`iD;Gb*YuEKEFc_9{MT5*WXcFUyLp?{DfY5Tz4Nn!Vm4kUpH6%els_O_gl!P{?NMD^+%oG8s4A5sK?ch*~5K0^{C<V`)c=mL%#d_YT9pIH{9{v-&ecs4@3>q^0CMH{p4g_S4YL|3Lhu_;`{acwWx>jA7r0@XO8Lf{b}~~`n_t@Ks|1Ur#1iZy@2bx``hmK0%hf2<oDb9y@@ZX6X(mkFl#}M;rC@9mER3|qdL+L`n_J@*$;9Ie`JB~XOjP2-`yv-X1%AslfSls(a*l(eno~)KfAv(4_tdQ<#nIm>;E;!@cA8}+dm<n-vI`)>lnU!z5K;}sK35(UVi`2IpKb2pWpvegkQ_(=U|P6nU3EnMf2)kTb;ZbU1N&lTle(U=bAGEjvD@`SpE*8zvCxXe^mXUdvslQskY|Bs?TIN{+NpToOS84Q-7e!!|L<*CV@-;I<}*~@mDl&e3-hv!X1_+QOSz3Mhy@96B;q)pR51;Cp2SP{eS%lO}pl8|F?faQ`=)NDeP!K2;YhR3%(P+8NCI*8NQYfu7x&)Yr%EU+u%Cz^=Kpbdblpy7_JN7fHr||fa{^R!}Z`B?Wm95f!+?^0k=R~!Y$xtXj8Zu9F5)tN5el`sy|uE62iyPui@kHDfCD96kMM+3*U(T080qhL%+Am&R6&b^gFApe}wCzC#|yn6uurkVU_j2a2@nptL%CS*Wy}>e#2|=zoBdpzG%mvc1*S3pCZSW<G@pSeKG9)lXyQ#`{mr^yon$1f1sT3({@~8M>)z%xf#5k!TU4tg*({CYG=n{Likfl%S%1NqKon6efdm#LO9lrwrC98p4Xr7ItCV9NIxv3FD~+)y#B9!tPyrR;ZYX-92I{&8V`?$pGBX6pM^g{KZZYo7o$ty#qb(530?zlMR&qm;cWCEoDJ_o_rv?(b)1)+(?)b1ypA%$%k5ZU$3i=Nc06v!K=cuKAlwP<4tIiM(Qa@o+z%Z9_k)L^!{8zCX!I#~G@O7=f)n7k(Yf&3a3Z=8UdTBna*iuFZyze>y2_4`T=P|^^xts&&xnz{Kb+S-;xp=f*p7$n=!|;d&hXu6NBC~|KJ;GrK6ohlC_EH?5*-6S2~R{Pz!Twl=sWN{_)~Nd{3*QBj@5Q-vLlrc&aq>Z9pmg6O9;<I{|(QC7oeZO3*e>bGI%MRjIM=~;WRWIPJ{E%d^it2fabtCwEqAhype0Xk!!jUe-*kKUIl-Ku7p?8SMIeJO+**LiSXO#JD#$!Dx82$@RW^h;nC<APuaa7JOq8zQ+DqN_e1aXl-+B>v1mt6*}W;;3H5r)?q%VD=tG{edtcZc=fcC$hhfpj;NkE{bQCN))>C$miN>R2;duBNbSC@^{4u%!{uo|@E`^uCNoX>h1n)%C;GOV6G!H%q??(^7q8nk!9g;&9!lIHRC7(;~UW{hLlAmSH_=wlpa5nD=OMV_txpk<#C%IJeo#aBvlLO!ZyeHh9GTms0v}Z0}cep$6&E+_9jL%_r4xDVyk&|Sew3J0x!B6qtBzPP;5FQ6V%IB8w*;VjT^c8q1{3`k^{3`qmIuU*b9*;f=kB6T?AB3NP??dl}?}K}zkHU}Ae&HlLQtenr2ya67!kgd>G#}1@^UxeP58i`rgZIE&(e?0FI0gL-PJvgT@4_qK`RFWoKKwj74SpVensa=b^G<@Naoy$mO(BF=+cBNjE{i7fndxEmOvj&Lhu@Cp(D&fy;P=s$@cZ!R=mz+6cq6(U-U#nNbKxEEL9_rq2p6Ke;X*hI-3({JTkKe4$1*#Xqp!is;W_9`cn<t;Gy(oMJOLdIPk_gu{oyh20Q4Ss0NlrpsdkLDBOZMij)xyY`@ntp>_dd`Kti}T+8^!>--nL2%I+!QC(s0|>>d;zkIuBp?pfhy(ATW8dtCTcbeUC_6NDvatU_0#%iv{Po7L!Acr~1iZh^OOO_K>>cial6qPyW#crRK2?}hWxTsR-jLAS#>@HTV<ybWHDu7uaapP}!;pTX~<e)wJ3z1KyjqkdR)1}r)io(@kz<KfBZQ)oOa`VcHS5SDx*`SE#JRC0>sTgk-}VNuEPkMi1OQJE9Q@!DlknL{L(O5RL?MJ4}b@Y-e3`Lrb?jOWuPsY~XnN$@0&BhS3@eEY2(-+1)-_XMv+e?U*d-%@@WIs={tTb{D#WQ!0^wDg&`v!&0!qKUAmlo38jJEjoAlRf%uI|cSy`YgP_($~LR`o4tlC+Grr0p*3;!(Q4TZR*79PQ2d<zdiNHF{X3w)98=Mv~4<i0zN^R>8J<x&`#k+9B%=-h+{6IFFFy4wDEV|lk(H(Qx7U-Jm?~L5uXtrZtGw>M%gjQ4xb$(?5JtUR-$EHZ^tcm$oAq5cGR<@svWo5ag!al*-^uefL+%HJNDSI%Z?N~w%c({Im^1rj&gQXu;XewuC>EsM~VG@6<e>gqlO)q?bm-%_w9smGqfSx4E`5-8!URYNBMV;aurnG6TaZl_b#JVU^&($OOO8-EbS9L=TVjrE=4cE7pS9@W8WFpPT{6@+`;)YMVrA=zOqNlNqa8RUeU^MW$L|}_S{Z=m(UVB&eNt6+ItCK>imuRE>Pw?e4h7y=e4kmg*e8;D0n0h#~2xj$~YO$_!vyw!Z?xfaxHuVTo<hg*M+a=+BIY>)qty`x5Cxos(kJm#^}xPjc8T)Mz|i=v>u-y#4&xu^==&=JtrUMQJ?dOg0Dkwg0F*XaPBwIM{%%wj@NU{x@a8z5Jer;&>HxzSB>+$7QTkp)j6+g_)K-)uZ~xZbMbLr(huc5%A(i6Q69a<ay@r*@5(*A8(mMNa8IvC<^8L<pZD-NVaWkCxxeN8nrJ0*z%_6sSl+Kf9;nLwFL|I8tqNDAjIf8#lqaW@r><+@YG@U>gwMFwU-S=DeBpAmZ#y|lco&@FDH|7})p(r(N6}XS`Z9`~Ivl=^G6A>-`7VlnilQGYz*nGG!dKESRXsY^s*=lYgRAh~W!Swodr)~@3Ekx>>;GMxXU(v-RHx5tz%_WUCa<ID)0*^mRbE%Yt46tMyeBL<<tp;eMYu9?6?soW*v*roCFoV;w5!NZCA{|=`Ky9Quc2Ja3S8^*TvvHrkLxb%<^<vLd{)Yq_k@inkLop^vU{Z*V?)M(T=VKgHO4`8bUkI{wVN}mbN!<zw;o;}Hg4qF*Fdj;<+{sty#lQXO9<ECvo#o3*TL@C6TStl2}=mqN2|j1t+Mg;A6s9rqX*g^7L9>>z+DL8vzF>POIbqrupODU|B4+iqCMdk;SPjwJG3h-|I=SBJE95U%4lu4GJG{5Tm`KISAiR#t>6Z5FZ2OebO_uF?nel}fzE^9fV0s<uxK%y4Idzc&!d-NQ91APXjfQ5_%};KxDW65g!{mQ&{yC=@N0zdd_uSY&4df!B0@OJj-SyTXeOM=wcJ4nzf1`G(GIX5Zc7NaLEFKi(id%bEnLx~A$*j+Du#>c>!XD5mxS=g=sfsi_-#UX7&-(V!Z;X42)997!EN9sXdSo-+!(D5*JkWCCWITIE#XFRYxI7&H9Qo31QvY<9tzJTgg-)y;E&)h2;n2>VOaDWd;~5fgj;j3%RS$k9MB$a4YwkMXQ3~^v*4Eq;ca%DLiZBF8R!eJ=zri0IF}IqfDnEY?E$|D-;Z{I?}zU}C4b$+YvErB;r-}gct5-kErN^a_kD!$>*yo!>u_H}xF>o)d_Uu$CmId+gu4*J717FYMYud6Tmiir7OetTfUiIsz*oSP&|YvQxGUNZ?h5xHgkM76fM0@VquKCmI1N1jr@_0>^RVb|@GkfQDmn22uZ8;)!h_L4@F4QzU_y8fIv<_`ziY=~^bk59o=*-vgciYv;G=}FRZc_rSG+9P&AGo4!hhLu20e@Z42$l7&%#^Km*Fk&tEeA-6@DIV3qKFvg|>l3E5didl?dTuma61pVbL$)WAKOQ$MA>nTj<;HTkzxPF!*t}1=<D{Z34G|??M~HqK)9Y;O1y+Sac}d9DWR)3qJ<GiGBpX34efo0e=90g&u)LOX08JD?J**%~8p%!lJF<=J0dqEciKiHu@4g8{Uj=gEzycJ!QH0G~-S55A+oL2mA}V7rulRqI+S{3|KT5E`*N}!o}zZ@R#U^=m+qJ@LTAc@LO;kdOs|B4;%;gC4_&mR3+E{LI`J~`(e?2a3;JHeI4Ej|A!EM5$y}V2zN(&!lGT^?r=x6BHR(a5-ks330r6dtL&e!hY&7@USWk&k;7M^mEf!3yV0(&Xb<>qxEmq-0{RmC0{k*M8-5uMplPt^E;s<EqZi<G_zWuf{S2>#dlSMBqJv@4Iq-w<8|b_68}R#{vb_I3A$)`o{+bZ}3Oxji9)-VxuPdi29WQ)6S{t?C+Hhr5=7Y-UU$BJmpPsUL;!pGs_)oZEIn`fa_r4XD5Uy2DL%41^4dFUyAza9PD=Z;=9IqI5@8RQwaF7uGf)IWW{SbZ+ejR-aejR=Qjf3O3pC2HEdlAB?EmgU<h5PsMl#43=fBSFf%l^r{Xc_-0edH(2pWcRlvWHz)=!dxd`&=RSsC^yFIbU+VBr}Tje*iM1KT-'

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
