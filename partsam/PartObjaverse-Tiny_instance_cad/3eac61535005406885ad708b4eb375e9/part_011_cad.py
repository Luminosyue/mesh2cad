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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_011.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_011.stl', 'source_sha256': 'cc277ce220042af840c6ffca7bc1b6c98f41fa27deee66b6a2a4af4161e5fc78', 'input_faces': 1024, 'input_vertices': 721, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15417790412902832, -0.21880373358726501, -0.12787887454032898], [0.1226494312286377, 0.4999999701976776, 0.1595909148454666]]}
GEOMETRY_BASE85 = 'c$}qu2XquS*zMT#PN=3Yy*XgIA(W+?W=!v}^cpZ=dRw~b24gy8=>}sk#S~*;0MiMWk^~aU(jlRR5CRE=C+S}8KO5dV=biU*&UfzJtB+6LY9x)MnRP;%rAV2>z<-5}nbopY@@rri(lQ!3jM05ZgbnQ7cVxMtq2qjvtV);vX^aeR*CM2ok1^VqP_j?ok-bNhtYIrzvtM9Ie_P3Z!$yRS=sC2<un~RwO1)9fAtU<=edK_ip?$^YQq?L}@V8Ye?Qff8`+xi|z04tR;>lwI98H>Et0T~v_0Ud<M(951d7`}a2i25ryVhRm#;qb76;=;`{$aVdKCX<?U3)q~Z<lth{A?U52K~k=Z~aL+rMu@eg5J2*!a5e+^>T&MUER*@R{F;@sJDD1^olRGD!pV%=zSL=P9w%?Wk63e5PIh^6OUQ-^uIta{A;wrNgq$Bb{KU<=??$Wdz8N9Z>77x-Q*o-;FA;9e9Vno;UD=x>8?d{q2IZ-LHQrM3;#kl5hq11_#e9o{VdwkoON@zRd>9GZktQp=Ops^;Vk^e9p9+p=Z%DaO2(=Fc_s2)0G;jW%(-IIF{@tY2J*>!VYR{;a}b}`(J}GyKC5n<cNuZMu84NqH52{?@xAQD_aL97>Ck!I?N{$0PQHm~pDD?R(<yDF@^3iSD}Q$ZzirC@^bpiLb|dl}RAh<re>32OwVxQ{YA#lKn*Pw=-hw`BMugJy_l4f{2k2=pbyv8y6XK7b58eK<i^AJ&kdLmnSo<Lg-?l=W9@iM>^tTGrh2Z;ctB>#7=Z9^o-U7k!zi<xv{Q|3$f0L&0ABTF)zDMEzXAQ4>>}KvY%KyWk$Cb|hV3eA(S^576-F*hSz05r5*B&a}5nb)N(tm#vtNz`U3(%iUQo8Z3PaMWk65>zo1l>1$7y8?DrMqe^fF2O=or+&~68tmtQMxnzur*4bHU|3bDCi@z;ySMC?xh>EZ=pYDtd4vZR#dv}@B`?L0`a}J4}m^2JNny*%Fx+=Y`?yYSNiXzkZ0R4)LXeRt~+(xIVaj-a9Xryf#T40JCvG%e!DJ@SG~rRmKdjdb04?%2iMb7`;~q!r&qm3#2>*5?_~F?*H$eW^Hq<uUiCVgzC{0zH;!BTvm<K&;#c|8RQko%@b`O!e%|wU)7sD72ZP~H-8Q5P@|jl?{cYY0rMsQDzRsb&Fb`C_1D)}W95s6@T=1h;9CxWPX#ay(q3d}j`uuhk=iw#j-RC0CikzY7w->$Z?H7Xa8+;1+54wte8+9iJaSnLJaW?;Lg^KfcJmSp7{9`s)5C6nX@aH^lyLa!P@_+1tzn-_N{S3VgbX)Jqh~GL3`u|sJk&m9YZ*ShA;xAbY|H8fSy`KN*P<TDeOSgZ00PTEyB<elHalNuYjMA4ihkh0JQ^%VHaVq}tAn5No&j-zdp3>j6j#KBsM|)MAUT=?i_4Cpu=GCl^j#;mxyIV!-2aZ|CwI|Ne{qXOFb}-s)TCeJTy$JfLS-39mrlNgT^h3Rz2kg~Dw<`ZerQv@T{oD+A0R40U=!4OJ%tq_CDBbq-sEWgR*co!|kcz+ImeM`*aO*_q!TX_ep7GRMV*XL<cywOOn4tW(I1!)ovpG5k^oqY7QTcGbbp#ICt>Sb~R=SP%LC5?F(C;L{pX(E6RD~ldj^hygx!$nnDgoUct8@qFc~`()#F;<)h;_U;X8i>HdB!8w>*#9q_JE3W`a+`8S+8r$?R{uxQ|azLsMl8VD)fR=60O(W6Q@McMC&**msddlPtKlb?YGY0sqi=MAGTgcd-}IKRs8gI4_mLJNAFb~dN;(kZ{52~>G!{eZbN)CXB+tUyPcrEmu{aQ+aAR@y`pq|-#2EIgC2ZP>E`;1$5o#Fe%Nl+?T4$MQ=he-G!Aii9i9J9Mw|vi6TJG>*0s=!T{)z5u5X<aVomg)Q_#7-b!^!NJ^8rO9qd=OL3iTS_xgAQ{`$V~>>2bS-znV{k`eXRdxQHRb-mtm*QGwlTX$)_%zV_#@!~kxWWS1kcAC=dx_w^!wA`wj31}bZOX~ik4q5xZEpxs7?EeRqo|^M#rW5M3;Z9QM;{56El>oihhJ)6AWt7gAsBrukr91e2ovrUh9kb|qePXnsKGs`zwx#~G72@mr^@tOQzqB57-jD2)3PaEP=76<7d-ADxQt6J^63D;*OtfdOM5UXXE2#Eyr_F`?nl1K#wLjY)@7$~M3EK>v_XYQzT*uMh<|BTNGSKgD#y;rXOvFD{RmC@_SKR=88vHrlZO%0qzoW+}UEkkb`!Yjs-yU&FHB)hH&%-y@vFP@_!_KRA*xd|zbVKB+@29`lL!P!W@W0mx{^KuiQTo3n&~AD?Kf4P2_vb{t?Te^-9nIgvKO~!1dm1~h%u;#&_;J5=ynEVh*0KH8aqY_69`PF-*>7!sV^{J#^xN3|)^Y6|whZf~&O6}Wss`HO;R-L^=Ew2%fO<XXdfd5_mO{TZ2maf+KDYmLLh0QnL)Y`e;A_x(g&=>fuUyxbs_|naRDiD6X%qKC|FsPCHWO~BdcP@$dTVAue9jNH;79P!_EF6fdLQICUr^0c#_PRGx3m473GJ6EeQsR5^?MnU4`F?q9=c~f{P_s<p}XR(?PmON+)MYg+fUS6M<LF#PO6_cYp#g2>NfUs=dMK<rv=ADk1Py5!%rArAtO=mk>bdIM}Lg3xcW+W*owh_)?XMeP3@?6o<I6q$?y$cI>(XoeEt=x-aeJ%t?g{g-M<L=e2w<e`_@-?6EVJuL+3u!7J40egMx_9@nuY?f_ZXmZm;iU1Q(m2bXzXyoR^#pO5?uJAQQgt9*jq4!cxQ;?^fg3&GnM)L^Jr8xT16i*E7a9PmU?9dJg{UTijIsW)#|C$ccT{_B6Wen5N>dJFIkjP*aTSY?IKQfm^-(A97y09*KH6|2Y0QtH!h88-aQ`zuD4HJgNNsM=9O2k0@Uj`JWF({6)c--|8&c;-%*qsq!&WwS(TVv)A{v*V&1AU|%NG%lXQvG8XlwO|5i2AA0iKe|N97Jso{tAx`GwO4s`-mstn*sfc*^bKl{*unuv?uiER?4}X1y{{M6t;{1qn6?gm)<kKJmI`7N&Hr1f-T!c8>k2?bbp+^r#y|Ineb#!N&$bD-=rJHln&yCcRFurP(*=uc2WBIB1N`F~&ul2eZ1s5ZJjXZn3+Bx@(1<L>5PkU58dpD?YVXyuDcdESCC8gVSf5_ed`!DKdWAq>AoTJc_hbdj3=eYKrQ|naYdKtv$yl2~4T&=T>orco&zR9)zHuSD1)jC(N+g(*_t979fx<%=ZV{0%^{(cenuU?atuFtg`g$%WSFoupt9PZZ~13sW1Ml@Ht-jCR(n}|<c_Y>!L4KbfDse(9q{_kHm$xG+_Z#z;QdV@7_UgLCbW5jtgKhE0U-2P`#@20!Eto_ZSJCCdNuZ`y$?&QwU{pKlMuYYV;x1rs#&V@hwmFwPC=*8N`Du13YIsK}dUOLxx_MzpVU(Xf$za1|(o~nJVt$wukxVwH^>3Y3wd)?)*RoC|y^A+`52|KLg#b~ksab_%4y6dlCwEy?n(Qd9t=-gL2GIqu|tyy}9wVgflLquWd*Y6^}BMk8aeo*^<eIK-Usgq#UJ>yjCrMz{U)}LO79yQea`Z_Kt-K<#v-#6<o*dIMT5@Q{Yo_X@U6FT?N?%(p`KJHf*@yF#y{^zP8PS^74yhN|xT$|&eo1fMBpI+~|GM|SY@=)ov!!>?UpJT!>t{e1Lx?a~Aap|$Y%UA+&xPGuVNdrAJA9THry4LuBRoCkQ=T+({^K7$TcX!4n^!M9lZGYoJ5cI%L(JKDXT)1B!tB-TJvoE5(^0&>bq|h*xuJ2!twgut;el7fYZs{u42lwkf(Di-a{#O#tyOQU?U+=F!Mqs=|K-c#{_pIEA|F)CT-M{6*`M?+#&PmML&_f#_PKI(ghjA8!&i$`@ZVQax8L!njgr0vKz89f4NK(3ecuDl1&%Yn!c!B?x;fNoVCCN(<+{W|X4AeI&U7vTk$L+=U3S0w!-Zwq-?Zd|K=l<Q+F$wt?h2cM>2;v+FMm}dVB2SKY_pBjUw^P^qN5^dHHUClPH=g-Cz6s*{zgN0h*bn|Wr=#6gELXbczF>QXJe$vh&ikYNr(-zJ@e75{b2FQxH`dAdgO#rLm5wJ(_gHm3e|q#B-nvWcW9`r<*2Z;@s)h4C|4!<>+^*L%?%p_8bhK8wzRx;tWI=yRDgvGU_PWKOzs-j@^fzM%A<pv;>YUYV&=daKo}gaaADgV>)UmTO;_O(ZbiFRMJz9nK9NP{4TxYtQt%DxjUg@^fh46j*9Y8<#YlS!*@AkeCIESI`&dvF=AN5-;H(A@+-f$`XgEv|GgL!o^^vd;6FYn_<_eVHCACd?4av$OP-N1QQat7%7`<|)+ebZm+-`O~>&A#F4zGYl=Dcv=9nD_jAy^GTIIghz+Cgx#h6{UYMKj(O<p1-+2;XKW~G7R<JdaCp<?o$EhmHy@ZXsOb_xNio|M0}p>x-)&kx<%_e*L5Fy0sUzJ^#87VUtd?}uV37+!?!Bk&ij#j<2mGi{gq4Q|DZ0~Vb6J7m$>OlclXbCTmAdpkC!Vn`@^663v=>SJa0-Ys&u_Rv{%lEI9bzq$GKW;s=`EHrR(|J_4p0W-x7V4uGf>Ms~+N%a;WD;X7_%Ge>x23gijkN-8C-<;wN5QpwKo|Jx6k_K6*>V*`Ixx(mRe<x_c~idvadr=18U6)(%v<5wv1D+Ow(B9mBIAe$%LNh*JyxTqiqIy~p!1_xaV<dW}ozXDS?UVzsqiV}T#^xE|0Gcwg(+0sG>!jiGZM_S_fzN<-&5%{5^S=0oSsRVp8S{;cm`H!3MzpR2g5XGNUo$1APh%b8*?o;w82Q@XxS+0u7{zr8&CdG2bvbOP~%e3bshdRXiKT@SCgulC>iKI_T<eSf9vb2InMC8*a7Q~O}sw%%yBY?E+Z4mMbB?N_c1qt+|koyN=Gd2U6N(j8w%dG&|A1J+@j`bSx>i?dF5>i;hF>bL&>J@I`LBfa`bnlL;Ed_5}C>$->kg6Ch+!y>(|dr*Zw3X@Yrc=g--Mla}53%v9ybFfZ(JzMGS&!6wA&lToGD6|h$x}#-;_k0zyTkZe8m<O`@DP2DoFjr;AI-k0JE?~aS06p$!b*^Ts>cIRq;5g!h)`kAxb$h_lIV!$>F4J^0=cT{HRi6Ky5ADUEPo9nSz@dMcXZhJGpa0Io_Aax$+W%>v(F!91W_Y#p;?=m0?$R@?*Toqb2|YCXRO|J%|G66dC+lIS*L4gE?+gC}POta@>!G_JPPX<pGc<<tWX5q`{U`0hZs^Z#MtSw;yN+=9M-8_2e_OyR?)zf;S;whin=(P6(F!`BBRE1_7)R!nzE*#8or!U6-0P$2)z24-Z-T$kN%d<z4?C(>!gEHWes>jz@A;Tlt0h@=SM?>hzNG@7J6ovl=Q)2)5zlpF$FA0PGe<;WzIA@?Vr^%8`=!v0v7MB^p05t(W1O2IUhRK1(=7O}3GupKnKDwp-9qKherWq}l;1a9Qx!+gpMP^-Y%Hmu{PlCRRyOPxjIo83&UxO*Q*STg_iV1>vLBj1_E?JRcwLQqJ)b+XT*SGny_FjGx<5EW7U6lcJ;z{GpC0c^>nuV0{4?0<Z}jglO`)stNTu`s>uAIMj(d{Q%>fV2s`lK`1nWR&t1-$ypD(Us40YFx$x46P7W4K97sqLsQ|Ww;<I3_F>kaDqIgTshXXvg-rGGJgBVIwT7ld`!<YUmCAC#{5Yi8x6$lqL})&+W>W&d{r^yG(1cgJ7wo@X2{;s5M6eBY{>@SN8%Qr#aMy*J}~tzE-;>4wr>T~nhSs?a~A><o1s|2w}WpPhmB<vIL@^xQ{3P`azmXv|~dQu18lhPt1BF%P?Qs{W|=%Z`l^2dui@FS|ETciEKgIfp;FkpAVA?m4fhLH~d=vsGNKpPheX!Fwj|xH-y?=L7EN9kE|?Z=S32(ffi~?VvmVQo4QhE!Cd3zny6RthMJWe|=84cnI{6drEi2|9e&C^@0AcE2{OEXJ1ohAp2*@h1UGt|3)NOb<cZiT7Uh2&_i>n`<_0paOe1hc5rr9y63#2;UnnL3!rm<>gc)WuvPc8v({JKSGwoi_3P&t@8R#2uIC5$KP53gtSGTq<+<J;*Cly8_GJMhmF{`&qvzYu$i-gcv_M_7f7<m**Uu@;PTyhwVk@iW1ASiViQ_k0>3Y6($0lN)>=?epYrN-Y{Hzb4^IXx<eE|Fi*dkT_yf3&f$8g=)Na<hfXM-jwUB8#&x^e*LsLmDeXFsuL{s#U}cOkw$ZyDr^?`8a@bkB3Eji*s>T!@-S_5H{>*5Oj|gCd~o^ZBxOk$<TzO4s{Jd%x7!FSw$W?%9X-PX+z;PNnPptT{Bbm#+7-<}m8^zv0h$$#f@SzY|hhtt)M512Ep}HNigmV3^W9`<K`Y@Q;|ObjQ$?Xt#0S;=W1U^Zvl)zR+zkO4s{evzr6^or4Dve|{~T?-ja%dd*tPtnFq*Z|<bfHBjk#zicjF%Q!>T{YSso=iXBu^H|m~>U~drPHuDvz<lUeWR<l&UG+a;|47|)PNH?2w{B}dJt#rFAL=+$7T2ZeO|;M1@@uTu(UvP0&Wp^-YpmnKe*F{P6C04EbbXHGNLi5m)>y0jIKSB^?Be-@L+Se5!;GHAeeNNp>-U=6g^Qvcf-0+ZqJ9o&=1Yt9u-5f^$X$J*4{)k=x@W$6I|lQA_)MjH&i8blcC735b04EL{f&i6*Y8c4M+;(ny}ttga^<0adW~_EHMbfc`u#3b=U=mg((O0D!F4~Bnb*C!(!aQW?Tc2re$Uoiy%+iHXrk7|U);wxB`W=k^~1h8>UpDn57Tfhga578>iMC5FVXy~CGX3<pzHVL+I8pih#xju$Gf}j8;tjf525S#pZ_V0IAcq1Qht2i<T>XID-WIL>W<92a2`0;4qd<h{GvMQH5({h-%pK75woGkz+XQH>^cSc<jAd_J9(aG>2+pwMfKcL@1tEC-lE?39k*Efo3SQ6uJ5KXTddd7k*f>zpf_8*`uUWZi1YRX;_LZ;S0O$}PPf(C-`s1f<2gd2L+PG%tSfsBr7sOrx;|&{<e9Vyad;neCcE&yXg~q=98$k;W<OPc`L~O<j(5kRQfP<gos{l*4)wY;&u`Bu-K>!j<NaeWp8MN^wpsh3eduQN&yKB>Zi~r@>#N_x3GD!Xj#GR6ZSeo-RJvYI+AiI|dlX5tmF`)8>i2dM3vNfh!F|o0)Ew*EjOC#7d6{cyTj<SqC|$3M%uSC}|1i=XRJ!MUqiAca6HF6vxNbLcrBwSvBm9ig?WukF{y+epW4677_<9|cYCqyfzd#(`H_f;pjIXvC)xJ%?$7sGO3w=dPrMnJfK|YWBA^yjXG1l?uPM0120o`J(`8Zdm#dGcVvy`r%Be*_g#rL{CKgOD;(P`5nFI}%2hwWOZ^fe1nFV{uR_!OwO<3{AK*9p_c<GM6Rf<MnWZClEt-mp7f-^&>jfjl2h-=TEQCyuE<VVv4lDc$oN%EjMnxS{LyxxI+DuGi-_{risBYY<<rD_%Z@e(Ns$^?SVfy|U|NW3Bz%*xpv17a0D{l&<%=uH(n>zTd53vDSWTOlve!>3t$%t?grsm^oMJJ66P6`?K-(^Khl-h>f+57h`-4b$%h{Rn)8B(;hPkdD@;s*XMq@E+Zf6dc2#tv*0~dTMG629?x^4454@r(3V~4_Sxyte;(h*dBWL1rR(?oJniE@4*q(d(x*4Zb)Tg>t?g{ID}whKOz58Xk<!_`bkF-pnW(#>c3Q8y@v02;fYpej*9oU8p<e3lzp`T-wa%litC;_x^L)m0z1*$U?;G^K!xnOg?<sXsy56UlbKg-<8;7_CpQj{YUfNVg>H0l$=aQwES3?>rUB8#^>c0ZIEkx<A+nLeNul$WT;rJbfo$-zC(Kvs2*B9~m9Kn^4660d@aOnEEgFYWFwOQ#7#y3I(a4!8WCeGS!Mk`*IuDjx_*U{+rHQvXo_Z0c_9N3W@hxcZU*NDUQt&!LX_t|=%@xAo<;rN5_ACz;qSAV!UF~+KU-h;hCeTcX2)OxPGO83n3&syXCfu+Uaug}lxR)#*b#BS^LHSRyh`-(X#DBUyP#&krUW+3w9xty~@6X-uS+ie{eM)sNN+|x*ygnISwl}<l6p!6DZ5TEDmj+dE`&-nSft^Lyoj8f;V#+o8(->>(%X3QA$Tk5+1+qM3-y3#%G*%rTu_jagz-m@)1{k^yDEJ;0NrPB4h=N_{Z`|jjTd#vN#INkvJ(6Kw9>-TTpJcR$)pAnz)p`#z4>%D)p$7|f}`W5=?x@uqUdB3aDZs?&cl<s-&SI2MPPU)WanfpXyTqIsry61g19mi2gJ<r$g=eu&$;`{lvm9F3CHzR|frydAhzgK_bG3LV=VM^EM?Y0hYpkIBbbp2kdb6stmZxkz_&P(+B?Ph_d&@X<Ybba3I%5)R^qYZVS>*tu8?(_E!jg_wV^^V?G;6J)^ymdT!em8M;dA!%Sc<O|Iqm78q@#uQ89Qv;X)H$L)&v#ZXg!dojPu*|5zOKUuaDEavN9lU~Y;V#P=L7DD{nqQ{itC6tl@IK<USIptKjFXc#D44bGRuC2eNe?qh_Bz*>X8p|{L858ulEt2dIMJ|UB5@<9Gwl%o!@?hKi}K8&3nf891Ml}{L?me3*H9^ORIFfe|J>jdm7aBIjW<`PWY#83xB=8UhRk9sU2Mpf4vW?upj5NHDi^o&yj4G3u3?j@B(ywE>yyR9&ruv_50Y5Dj`nb8^q^2%JVxf_lJYle&YH4MMj*Ddiv+`vpC1AT0-gi{R*SVDfN8O=voOn*QNHDnTYf9w$eSn51L&RzxylkO6hvuFf*LRbCcwEUb>NWWOL<Tq_P?Zo_$m6!hB!!8!z2)IyTNr*YBO0SBoFB>bl=PU50tUh4;Di`o}rs_A;xk{mmCY;`c{kofEwJf6sULy|aH0_;dejW~>SSw|x_={nKb!9(kS~m|z_j#`J3Fha-j~j{g1HkI(TOGiX$TwLcpthvWBmTG#Wf{{3KRIO200+1mYq^?#%JUb>Mm7wzx272ivrC%pIz?Yv@-m+l-}FV3p#@oV@^SI>uxa`8$xPxxGvpY2tO;+$vbe$>l#qw}r}>xx`QmG1d{=!mIk|0O2ozY>!!$j|1_RS@U-aW8+f%`-fIfBYE!1IsCYBe?knt8Sn3{=EF`9MuNx{PY##=>2Raf3(lhKfLuOdGI^v;J)gd*uK9M;^$7p^P26$ptpO7_;WAec~HV|r90ogSN`_H<#3)^W-{~+VM@2nY6!j84Con0oK^AjH^Tb{JLcnj`b~Z4+mET|D8|n}C|#dN*)NA-KJ0uCy51KTodLbn3#IG#;_M~oyKuceLf5}vSYI3CeMcI#PS?-(ZOs}%uQ^BQp7)khX23kZ3A$c)Id)KQx>D($-*^A=E8f>S`waekj%>E8iRTyVULZc_H+w`YzTZ_+-EZ|g=?p)G`7_55rF(wIx@Rn|<I`c#_3zeqT=&xTIg+Dk82WSKNTus_ojbVY7OSq;b@qb$@Vs*A7_a!Q+`q+Hb<gkO-6`6r{0B_%ito&KA8~3<Ibv;p=RdJ{KA3g7mu?t4J0G*?p5MFK!|LOE&4Rz4w|hh_SN;(T(Qf+OU`+zPSKu<_&-=T*4WCO!Y=+Kth+#ig$*Svf0AtEIjNgNo;jiCEDw_b^@e_3Y{`rSEysw_|u9t3pQxDfS+()gKJ?C;8YGM9N3Q@W~M{-swf$<yG3jTUsdY5{s?a+C@wx@WA@f979INVQp^p8pK*XN)0ZeqU>avi!p2iE%gUl2$C{fZ+WurC<<1iJov7g|q#2VMVtiF_&4b33ECuln7F=kHhKr@p2=bgsvoT^C@SzU>QL|9t?dhj{%}k;+Zp4sZs@pAv}Ov5~{**VFPRMWiVI)A+ytlOh8v|6lz{kqQA7EC2ufO_B6#eZ^N5wu-o%e6z6i!Zs0I7QT_6C2k<U=VKVVgzfMJHueSoUVO(t4U|iiWs-j-_(TKc6X_#)X<@Srl+R+B<d20F@<F-8S@iW0b^PRma*2h=PYb=BFUs4|$A>w|+)fkQk&hSUpM{O3N&Z&YNMGQ5;%D-v0`m#$Oq0Bvu-69g5iuWm8-bSvcJ+Zt{)?~<#0tdA<P(L@K4GJ2l5Y|AkocUqkK8G8iWc@s@P)$W3CrXQ{6sEM`beH%@HE1j3F|E^RG6LEjJz3rByTBlDkJQ=utwr@6Jd!4P-=-RD?@Gy{hF}3!ukkv2#X-jC7(;52)6lK<~@)66TjCdUWZSXYtotR9ZD<5eDf3Kb!cX}CbG?cVZKesWxg$m9f<mxjAr{fXj_=CNqk7u*F^S-&urgla@o!ciQ|b<AJ0CKkL{a={lv~|A+aejA9)4#jWV>$Z0AP24sD2+$)B@tT%+w{JNF?@B<>@h&%8$xo#ZmlG;G5(Y~R=Hqh;7uW!R3AKWBXpi6;3@VX?v*`2rjIg1;62<_`nq5@YE*LGbYg%E!}3@|nVB7$~2?GRX^ye^bB*<q~Jm_ea5h@Im<x^pU)+sJo3X$|cIOADN%btu3()xy)-b^Ok61xy&mCzgr6WNG|jGj(LAapFfy$H1m#T*?8vc&%7l@(^uwohIyZ%PXXp!o_R|=!|x|^vN3NPeI!37%5DiO<_m1<3tm|8lETgtuaaL8b?+Be*9REj1AbEQB{DDKR`Q~v?4v+=kCeEaJeR1$E-VePDtQ)Rm4vPI0q*tz-yy%du=K>w2KX+4yJbHi#*rTpmMrW5@d9~G5i^IdI>dbBfx<Ei`-Yf}ytr&Td0mOM$x{mZOT^1S{G0rcu%Bhy5O0tl6t+!{MPdwjeNo44fhCB?$uA2mCF~-x7<qYFhp4Lo@f!IKfswLb6O+iJg#9DzD6xnScr{T+U14d7xyj>1c{zbAh#AQLmDf~YY9HWs@`XZQBy28m9(k;=J;GKHSCf|%@rnowA+{h-B`k%o%0z$iDx!{B!ZH%`kmnSZMObNK3Gzq6o(Q`@OeS9<Y_YJl#MR`o&);Uhzs>6*c}ceWRpMoG+2;?j-%FI&L-HkT_pQVo<R97Y%ZX9scD8#}Vl{Hv=gYC*m*e%=%|5@C{eCO2$7lBWMeO$y7m_El-7gSh$#byX^ASsuXJ)%+Bc>v6$ab$ytU@mPylnTsi8;xCX1m`YJ|f@7c8?)0A>YaVvWqy6`~dsQ5#nm{I_xhsi7m*#VSfoE`jgw(Uy2j+kY`|jNl7e0zMuW&5HXoNk^SW$aW(la=DeG@i2Mk1PA2XlugRQq5Q~rpGUv?16y(L3b3<Y+@|4V3UWXDK1Ck$N&OZ~MkRN2u+lY(FM+loNY&tQCyqg>gEU(Wp$r}s%WT0GPefl;RmWt)6SSEQ-VZkg9W|`z+!sfGlKFcJZCF}~zudpnPIVG_?iDk2x*LTz;=J5rWd8K7}T9!>_UYnS=#I*F4dF?e&zL!3d%e*SEyaIhvF|QNM`vl8^nOAXNluJB8-z4UCg;<<i=5?K##Ie5MGOybP$|YW>ugt3%^Oks<T;|oDdAFyJ<T9@h{7xTOCb`V(4fB3Op9;)*8uOO;hTl)-G?safrB89@{D65&jA6OV>k{*p_<-M2=9P_kXQR(;=2eP$mtt8n=KO@^Pgo|o%*)po<r1IJSLSt!c}w&qmpR2S?-=?>URL~@tioCoE0MR8V^x?xF%5ZM`edah%W~85Qp;;8PeblcEKBZB-j1m2Y)4*`Sc$wQd2V7}@;1V13+qShLOxJfcVTUbf#gl;Q=6JBYeH*Et*NCvki0Fi4S8Ggfka*BK=SUyF67<Gn-H6l4-(cx*mPnj`5a-RgbgNkCGSn29@J!6FIsPEy)ETk$p;e$kq;)HL)3N7As<ByB_BoJi`bidwy-c^2Z_tbPY7EjESxx;d<=cUsL8U?v@z7iSjvZ!hZAR$hm)Tm>N-!5uOcoZUqwEeIEFky*ivD4i5JQ53%e@pFmVC-dipG-Cd*v3_0-l|$`_CyCMJ*{CcjVAb>1hxO1wyZmE1*KPhM469%0`Q^N}|cR#2Fon3FseeezI~WhrT?sHL)$=OniitCHKv8xnP$4ao}<^N|-MPf1KgURhWnVbzH?^18x`2&+XbK%R*{g{aB0^t4RWGFi$Ckk=wsCa*<am#FKkOJ0O%BQHXpo|uVT{srWs!Wt8clLrecDXaytFnK!q6s0E1Qq$5=OJ^xBOx}XnfV>5HFj3bTOkR>$oV+A?YGOL_D#CIJt3mW5uV=`g{)zP_F$Z}H`sAV}%Y11msHL!!=OC{`tU_LgydF{4S&uwF(T_Yoxi2vVd3j+Ogar^Yl2;R!Sy)A4T5=!yWS}O?^nX6od@SW@$tx1elUF3KM$~myBhO6CNS>M8Ao`F$5cZR>bHpv==Y?$)_K<jkJf1#3QIlo+Xz|qIE#)`J9}*vsKO{d-)ODUG-$>j-zL9(%F`nEMwn10~aT57rVdI3IA#Nt0MxPDTWZ6{OG-}f<<(tXR5KZzk<co>A&c)>8h?B_2kxwN~BcCs9tgxZPKIFrMIfShwI>`snXDl^Y)}J<j+5k(rlYAv{KKV-WVMJZ$Fmea654nT9KXCy05Me!qbs`3lcNSJ(*tf*K<gMt_lbS3Gp|zsc%2M8!{9ED>@^8sI6Lp=P$?Fq?$m^4b5L=OV6xK-C*Tn4P<%DGs){WSlyaat3QIloGXeFqXu#`6^??&uM-i^E*QP)|HJPR>9c^2|w#1iDM#6bRCuC<9L$&Uz25cVhW9l4u6zf+TCcWG{FZcF()@;`~M$p0iiLezC0Ax|KlBu^l}OLUXR3p*fe4ska5RAG~Z9VQ+nkD|{3YO-u8Es9!{rTi%QVPZV_Ve+X&UFTHtNyORYlgO76qsYezn;@(cu^oA9VIjh15W~p_(q{rSSvG(+klH{?c{uqD;yCgd<gJOi&er51#CGH%<O7HU$y*9*B`gOq8+j&S>4dc<b|kMspH|dlS#??sYBen79m(4gTavdW&qUO9W+G2V%toG$ygIQ4d1hhRh21fLw+!%~h20e9=L5{^1OCi_kMzyUvZu6X^m}G0&&&9J#LVP=<g%X3KL1na&#eC@@fP__@~6aS<Pl;K5i4v2aVq(@!X^k?NZdufg+8&=WZ72Q7HV58<-5oi5+leLl7CCob$&}efjE_X0{K?r7V=PG<Arr64kGU&tiP~f#L48N=rf+0EE_``MQxO&d@}hkVkr4A@-9SOXBYDR#6jf!$;S{!k#`o>S6CHdOY)+^f`oM<4kYhMpT5*&Sua{oYCSFG1IarPJCk=JFG|#P79|fNwj>WC??voMURGEWVgLF7bCUlhETiD1eSyK`wdm7?nk=hLt3|Drr97CtG_fpsX>wUlSxcSL{$<?~bFz+)ax4kFPyE9N{1;&_h5b#;?+c!eKGIievMjwXEFCq8x;!uI_?z~Tu|Hbs`Gx!?@elHs<mp*wI@S{<Y_G7T#3ST0h3yeGi@2Zs9DVjulV#^==ct{tl<y~>MT{b!MLv_L>zqlxhj@g15BYiGIr4SFb_@HCc$7R+*g;`Si2KOT&}TO_S$39ohT0iR`9AU`#C7CL$Rmlm&Peiu#G~W~$<GqckS`JzFKjXK82Jog3Bslm50QUQpLlAr>=NyJYTsMR50OtNE+U^!K7*+1oI##IJVu^Ceu?-!`7&V#gsmW&<a2!GpLr7N2;yP#3-mcaO_p7xU7&WsQhu0xHgOsGZ1OooUFRI~M50NaNPdxcfqbQ~<HA-GlgQ@^J1H!jc!K;geU4L;Wy!S5)Gk}fPmqTbSCWU5&n4<Q=aQc!CXt^cPbOX_e=NrGYhfRVS$)CZ%X_)tcZe^1z*G9dNBX{CS!!BJ`lYm#zhK-u#K+`!$lnuno$txBGY?r;c3M`}la+NzE)N*|gq0ySATK4XnXrF+fM1bUr;i^sSyqEqomzEE`B&uf-}<pW$)y>r$FS5{io6-I0eLg>8pP`4U;E0}_za^1u@8BBVFQE}Ce|bGL7(Q-WSN83gIW(uc|G#N#IMN<leZ`8I@^;EAod|2K<*&+Anz)ypRl3CiR43sO%c|S*qc0zKK-c4veC3KYGIc0-sByLUCBF=4<YJ0hmcPpP9&c~KAIRtK3v!&VGD>m$>#}+6E>JQj(i(^CQ*}R+iBaVZL^e*BOgp0PCl4?9#Pjhk35dJlRS=mJ8>JiOZ3Av!k!YJk^d^}H(|?(k>r=?vxb^1`<`}*+9gYQB>8fpi+nlxuS8wvujIcGpOODY{yp&$`A}g)ge@bkB3~zLy|6*Ve&kO24522=rqG<!oR;!_<b#Mq$p?|IBkDTWk*_DNB41BFh3F)&DeN0z{fUFgzZEu2ST$m0@(%R*hMFvEPwPOfgQdJOc{O59@@nMY5_O&5k`E&eCLc!Lp4fr>otVDf2&?D=tmFe;Ral^~R|fDm1N<u=_(<R1SeBLc75%=ll>f%~uZZu+Uy)a34!X{&tUr)gi9C=zEAcDxv*O>L7WOOgCHe2d-U~ZLJWhU(KBuY4GB@oWwR@KG<K(A^XUR{I|4!6({!ad$_>%lRxtn;8e5Cje3xxF**2M>(C9lKJlGo#B$$Rj#<YV|*@<sgIm+=;n%Xq`7Nt{M5V|QnHcb1K0JwYrFVp$i~*@ERQSXPJi_hNZ3mepe}qgXzQWj&bJOqS1N*%;<Djpfr=Cb`@f$^B7nVl8sLpOO2RjlwnvE946-=nL*6xWRIRK9a8!AJ-Zvmnh35j}dgcf%5J2k-V%ZE5mY$vP|-Gvj6#@{49MWuOR9U@I|>qS$2;3$=oUs1IP;qYb~rIQGVX*1Ki{TE=}?m2GEyWn&cyiYYcE{l20LSBcDQ^+Xwiy54beRZxT<F-z4wm3zRu_v*g;1x$g17XNj#?CUbjkpj_e}eh-=32<AS5J};QtWad7ZWh0quE+3RjoJ`-4W<I_-Qv9F(m#F{qpPZ`=um3^nfB&WT&mOG*vb~7q`4L1&vsChVoLKMqs)ycR$tUi{{{kbuTT='

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
