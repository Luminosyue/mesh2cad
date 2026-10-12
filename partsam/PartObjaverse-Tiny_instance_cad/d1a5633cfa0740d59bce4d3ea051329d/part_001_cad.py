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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_001.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_001.stl', 'source_sha256': 'd2a7875d9a9389a907cf229d23bb9a24419c9f83d4255e47a2676b863254f6f4', 'input_faces': 706, 'input_vertices': 424, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.23538678884506226, -0.4580686092376709, -0.3745158314704895], [0.44773054122924805, 0.13910993933677673, 0.4454312324523926]]}
GEOMETRY_BASE85 = 'c$}r22Xsx@zsJwjjWW^eaP=N77&XTbElTt<$c+fW=%a)TXLQ2oB_VNjh8ShEF*q_I870yM!PWjVMjPE9Gv3+z`#o~*|IJ(Lt@o_;Ti?(9X5W2wJNxXt&t3d{v*#$P;9mtL*NYs-)ar^NBEM2pnH)6X>k)xL6FtX_3$ZC4(ii_sUD>sF7r*{CWwJ88+R&hhffK4VvsY^|?DJ~1?bU{jo$&R9fHD4KCkzb|e!GCLCI%V)#NdE&LB{9mUJblz+Z)!XZU4spfBg4}Q3S18g#>S*jR))(s$Y#xmzv!l{-*hdrEcw$e9BOl`aS%PJ_m#<^Xj_$Q-A%*>f397c}ad=IW$^))^4o3EIvDH2f|;sXRq+}8&T4CeXha3(mh&gCq3zu#n;k<PFj73=S}#H8p!f%nPp`@O4ZL2h1!1}lPc1w`}4~5>hPM<*Z1#96Q7li#oc^$L%kHMuk~?AU&%9br_4XGl$)<^9Im_h;Zu>`D}A5TOq(o^BRo|4n%52KtC>0Bcl#_!rYmuAyDZm~-ifCyzFH<#xBB)Cm5_efk9*|x?s{C2_1sVg{-V&`@Jn7neVW1lqO2^xno&^puU2B3^!2y?Xoq1-WWDu%^QG^&-BbGd?c1{boKee>e!uT^nSajxGQF$B8sxwEiA=9md@9r1gVrN`#iR1G=JN{u&~yX*I+N1nb^Z4upWE;qk)4n}&krb1*&pEF?2U51%_r5~>Jai-j{enh$0f*e<~^EZ9k+VbF*3d5$Ky!v{RZVMToU<wc@phBpY>YS6XndVyS0Pbd?)-Gx?BEAop{u@AADEJLHSt^D~tSl$0S+Dn={OnVD-)MX8KyxMWjEoQTDg;AnvNS#n(nQJ7V=6F$r$%uS`FT_86In^j9a!c2=j>!1X^(b?X-;>Nv{pm4WgUXo`B4sE>B*a5c#~{?%3$FIjza{F}bL)(xbuwDz(rM_gfCr`Jul@@SuymifEd--Vwv7x!;<)!l!(;JBL~cMm@2AI)=9s+-UG$Mn^6@Ev}G(GIncj~e%zTmNb))6s7a9!TH$TX&TEjSte_{nP!v7#A%6?%4QD`u5m{=&y%=qhILj0jJOYldp~c<EYhFZ!w?HzE@@bgR`SN`(DAH{3ov4auM#wly_+7EdlU5XCzyFXV)XBf8(X--!~snp0dwT-<(rWzY4Zwng6YkS7bhR57etecIhi)M#=H1J}(5{Cnx-!KVqC!4@Evt;5&OS%aG}Pio!3JH`&_ndg5bz&m(^_?hD>`vmeUxYd1WSt>aJ`hk3)k!4ALWeDvePcga>?&(k8+>bnZm#C5;@67?N78+x@a{P04Ue_AfYxT;eh`S;_zbTS6*yt{$)9lvcy{>Q>_U%dVt?GV%i<s5Vl{ne=%(w~b!J_A-@{B&%N>n4T3pR*77wQGrXyWUB*gA#TZ`Ng(EK6B%7ztmoZ@;`>J=CR}ZDQn<6TcbR4+kP)U-z|apzhxVwKivT7E8)I(6lyDd*Q;l;f3<GmsF%|R`ONc@`RI4c$b6hmU-*k3?#BJ_sq~eME^g&i!{?wqfAK?lKF9TE^;50B`5ZTWy;3iZt3Go4Yx~Y4eSBY}FBgINq+NYHpCbmq-;Vo5dDIZ&w9*jd^J2;O^6#Thq*{F~KJJv&w>KPy@pCL#j(@GbH=aA$MxtJQ$4g&Xn~C&w;M)V|%W<yQ+F<^!I3Des@xAo*f_QFfW2U&Zk21GE`s<6SX#WF$p<bT%QO;S@+}cg+ly=eTo9*_||5vD6KPo#1BmYeck<aMNEx4~%W4#fw82+PfXs^mcrP`k^hyTG3<8a?p)GL=0<Fn2=+`nZ!F-~S|L%k|LMSHbsh<Qlaj&kz(sQ%qUe$V-0H+;WK$jAS)G&jH98+qTVe_>v6e6=6f-SYtTimr%p)#w=7c~M7MPPM_;$Y=9el)u-Q{WATNQ`cm^ui&dM52O8ul$PqU$D!XV7eGHPhOhd<cl7=ppFK*Vyp!N-k1|o7Ao>%2MLBC!LjDUrlWLEIuQ(%-{{i^=*z*`a-MQ|XTOQ@vd<pr-<x4{Of0gA|$|rN)!1GbDSHX2mpU+3r*S*r+%CGInlaBtnhxB}Ix{_aAaP#@xG=0}!f1><+?kgc-DOTTn?tk=OesH_49(*1B(n(3NwwrbWzN>7$6ze!q*6hS}Q;SL8nTm0!jVOunu&Ipn)x#YyK9}9Z`YN=X^p#q-x61xp_3sp`ucvoCZS}R5RgnIdwsPK3H?7D0(xe8i``3N+`>q2R=ZoPhWv-#$|Aw!0X@c_GpP-$KZpHZD1Yhl%hU<-hue5E6^daeToa?U(V%|I2R{E|5r7&+?*^B2zSUc(4ix0*8)AJzed$kkFx$6<`U%#~&KYcr+z8Ck)e6)WbLOwIQBK^=Z7>DB{QNNwtP@bL_(O=KkW1PH&Z_b~J&*n6%Z_b~luW#*+`kwt+u79+rgEGA>zBVHHu$#Z72g><43hg#(6YiH&1EudMz7_Leu00s%h5V8KgCZzroxSjL4oCa+#q(W#eF){>HVOHg>#k?t%In%=;VYA_$o5xiPsRA0Guy2_^_>H8ogNF^+DGdgfOdYc68Ui5rIc@g{pqoFNZ$bK8FlwXw2!9~{kz^5_1gXb`6O;b`QrnTe}|{2*XErlzqu~TY>j<oL^Q5@8S|mOq5;bJiaz&`suGuM_09dG>1)9UP~Ue6xNhSn7!TVIA)hr~azCy;UMuGx*HQRtDLkjuAOA)>|9BKW*JIkr-bq&9T#uQ)n*9XwPn?E&rskB-J=Y%is{g+*p5JkPn;wJqESHMU8*8GzPku#v=KKNqpC~Hxakff8KA*lvzuYb<eS5a6XlDoZk6P8r(su+tcB_}3KNjt<_zB9n`vCk!jgil-CoB)vA$rL$Sugv6XYjcW(M~OqzCPy#+y4c|LBHn6C*!4CJLt8~V?3;U55MKz%`(3eg;T7)-aX;8)pz**4WH{4J$tyku5*Wyiu<$&%JJl(>_>IHP5Smg>|d0#?a>ZC+2~_Eqo!;?fA!2SeREz_7vD&=`sTd)(f2PPef4J#tjEgCLj4AKApe<%@q90J4ePq<#Zb<*&t*B(UQ;oS-ju|3$JfO=crw<}>S#Nz+a(m^VGZUD=km%(Z?0!5oW%XuxO%F!AC)`rFwY#UiE>`7iE<BIit${xPO7!P)cp#^XSD{%Cr-n4L)RdmNllQxjfQsX5{~+|Z;JF>N9nOK=!Y`R+}d9&R{;4xY$1Ku>6)@1)%%;#4lBLkZ+MOSwqA2we{oy11J7;rQQymX*X5$mc|)&U9e=m?L_6=<k9L@njB-BiD}Bck)K~Gj3_oX(TRHX2J6yNIH}5;OKGw6Yo$$4wKMqO%=|DN(x}t}nJUr*ohn~mtq3>{9m*+fc!3)w?(}LZ~uWi(k{+p3#&o!^nFCQ*&9-z<liM}ISveh@&C#J9L8pVEmhU-1;Ez9XxHN~yI>gg*OSGyLWJpb_=an3l2^xUUw&C6pRn06ZJ6Q|04Rj!o7y8iSz_<3%ie-}2ve6{*K^5MQ)d0!jjq~%4FljkS;HJn>ISJ3BvT=};r#(BX+>3`gJPpXgmcVHU&h3gIVTrkGb`KxaCwQ{zWn{VFNrth3~9r>H<v3jlHkH6!Vzv8h2?br4m^65An<@COW@e}q3uFLsNS^YZ2>YMYM>8mgPf`98R+M!l|XpMYnGM%}vtTQml>VMo<n*R0t(l^id)VsgooW{EX((hP}@ib*R=EGr?r2p~UFC6E(j%f{~Z=Rnhp4HLL7rc<aZ4cT%a|y~B*97I{If?F92mQ793+dZ)x5W5g+z8`jPY0x*Q0|!g{NRo}7jo|D0zbAM?uQ3Aq_0E=qC5eIc)s+3elY4ap|s3LeV9$o|IUz6$R{}$%9rmK%s&-IqrP!Ln3r15#`ukfZ;!3-cCO`m3Ew=&(Dnpi{6|k@`9HyRAN9rh;r=AF56>TT-x27SDwC0q`5xif!$ddVe2-xIt>|-~sANy(b*Cc#*haXoAN7#ebwtm0Yai`ldHAmuvR`=4upk8GiC)U|N09!}1eE{5GF(@|K3_l474@#X7WtUx3<ZLdtp3My2Ks8l2)A*i6x}1s>zub9zIo1Y@;juDh5zyWOUfCX|M%R4`tqDXJGdI<e-Ga^kn<<|#o2W$%GqKh##s!WxAuuU(Z75yYY)7zUx|eO@myjC*8|Vso9E1W&!13!@4aX@o+qoFPocjeV^J@j+iP=@k$!VL^5OiWo$yGp`sVy&`dXtT_&m2)B5xr7{VB-*e17!D(bE{$d(%*Up2Mrf?_gYPx`FoO`GdM30rz9uJMhhO>0Nj}D5dVE;r`=#J1qtMTkrwepXZZ$hquW8hli*a-?M0E2I8DI+jEq^PadpS_eNtrto9l{pLgoZVYtqwx2PA-t2O`J80Wtz^1Y3DF0J(`fOCS>Lhz4_LA?sSK|6dXiuXJ`H&A=rOLX&jZeaS_#75FL=Sh7_2Cmz#3El_lIR8?e*zc+ZRq31iDJ}PEJQqHPZ=Sm<)jA@dR;|;m<5}r-1mmG@JNP`0)t-07e4E}u`sTT-KDImBe^WR3JYUuB_JbeQ9X`+5^g)AgU7ud47tc#S`o;T7-#j<dwIR5VG99QF&j++wZSefOGy>)1eqU+X8|TlJM<Rc7zdszlv&bam&wagCV+hWr7l%mS+}Eq`1K}^6j{NyN)ov>|_gD~$_UFD{jT(W!zng<{a{keCbaC^|`N#B?&%%(;l}YHA?JDl?{qW8Azv{Fg`5spfTa)fKK5HLBeJ^ft_lq?_`E#bA9egq{KRld;aaiRl`o%m?Ykdpz(lq$yxsbXBzP(E(^5J=%_RxiKz8SuGUZ<2mdM)xM#y`*B)K+)Uj|bqJ?_sr=2>Jfi6-S@va(eI`?yqm5UwAI3Hou4K9=wBc^1ZDd6NUG<{r^Ncxo_1gT}HoGdx`Yiw`y_M&@Tty!smNxr(Oo-NzZoKdY|ew&S73Mecq?0uV2rL_vG9csEzw!{=8Bh>G_;emhpXMvAUP7_nqd8`COmv1E2dZJ)su%o8`Mn-`vOPb1R{K{)6Ci-=xn`aor!`o98Fmw+^hsXAMFAJU>yY1YsPe2O>Ssqs;NIr4Ge=d+xKet?iNjw&A!g_gPw8XOyRMu=LGyB=yyBwEvp%XdmvU^rAgbulo~l{%xKwtr(B-d}t!B%X4!59L}Tl=96$;o;#^`C!)O%O-6eDp20O^qx}7W<4`Dk{+_`xbBFZR0pCd9Jg3s5r=xvJhoSs@F6dfroJZBi?<358mfk-E=b1Glkw5oAdbJto=hojNe{;Wfe-ZlOyC0B0*Wr5GH^?W~A>_~VC_TqPSsusEpO6pFqx8_D@K?s89e7Tn-QzjZ;7iD#&jls2Bj%Mni72Oe&T}mR^TW8CZuL?-;J$F4x`X_AZlis56Y2XsL3wy?qwN0!<0tJYuFHLv+A|sT8<s6YUe`RgIsO6t>z`Zt=DuF@&w+Nk`ib<-eVKOlD$Z4G1*C7T&y^KD@E*{&Xoj_&mDe7;FDfDb9Fx)hn<FrPbn`_1+`njv`BCrK?$S5+9qKbrw5!)Z>6`0tRhx$N$wQGp_ZNCvYoxCjjPgWqzHRD4{ZiK>|My(y@0*PDRilvJUI5oEaue^f79>dDwT$b->(NNRJssuAKNk1n=Vegu<B!nJd=IFc8;$oF#~;Htf0uH`2k*;|zkqMPm;5yl?+=c@f^Ys_<xDsHp5XW!_~!e^Uxy?Am~C?Zp`VGu`YirQlGXqCy9oMP%n9k6@8$KhF<9rt#9*H^q3|*IBd`vO$#hR2Uo_e3o96)k-N$}GNuTGIkNJMzOz(=h&iuWwUQA!Y^tV`^g4j2uFEsaiIJe`zMoZ`ZA+{0T3vr*NrLRUlv3}Rw%5!-?*7s*7AwAD^)k_&T|2-24-+W(o;diw2*&TRq#`jSA`KNflb@m*5o-1mJ6|tX>Zz#`2KAx*2FTwdsd{gOvJQqryk8_{+X3{s`7bpo6c@Ewj>G{6E^!0fEOl$jV32Xn+*OQ}Bo~Rwj=RBUL_BTUzx%rX&UC@)~J5T+C?`jpW+bw<Wg;*!=db$17KluMG|0Jxt?A1GMI`vQflp|ZL>GgP?x6}w<e(In6xQT1r(huM{$)mtPZ$GzR9~SQ2<+pVej3<y0d6lBdumH<X4}~fInflK^JsjcnzxwH6lX{K+zdt=}Ym}j`5ksl{$V17qsWZqzH<4$Pzh?-Jqy9vWBd1Z%lherQ)Jx=aaw_##aw_>O^$__ic?Z==-a%eWokLzs9!(7<k0y7awj*~Tx1!c0w<0&9Rv<Sbx1d%hw;=mc+me0BUr~pWzaocGXOm~Mt-~0C_cH`vpvI9ekTa=i<V>=Qnof3+FH=*=m&xa-XUXTt`=~p}`^eu>7n8pukEf0%k0<w{b|Lp7e?e_U{({_u+KAkQ>`iS!_9l0u`jWem$5Ou{k0mdmhLOYA)`FKAvC@bjhTuTza&jO!z=$uYi>S-Vi^#t)1Se8gk`u`nsmsVh&yX*YpHlCTpOQZ?1iw@;283Rq-cho~%pKPA4)Zd{*csOS46nV!(iUT>L6$ZQVjFu?J*h$DAhwYwLvR~v0J#lWwX~zk5Zv5|5>z|&OR}BpM_okrBTu0ILY_dL&k%f<nn=D&enY)TzR0$I!w_852K_)5A-K8?A^0=uOR@;TiY=?31PgVMMF@UN?=tx<`7!kz`7t?(x{sVh-bnq9ypcSPI-Wd^+?v{p+?rg5`USZRxfrzxxfr=L)tfBTlRU$y<1`~es1wM2j2LW0V<SGHHlq$EHzN<EhLA&;&p?LY-bQq#eo37`{*pYLI*mM>9Bf2+BeEIsF9jj^3iY)D79lv9`ih)PzDoT!`6~H0Y7QItH*#(pv;sLdxeoPnavgFHY8P@3@(5~Q@(A)|>M-(T@^or2IhgG*ojQX&ojlWsZ>bt}23aGAQbWig?6Xj6A95&pk`Z4}Yf<}<Ymtjk8<UHWUnp7QMz9FM*A#@{+lJm#pdS1zd=GxF8QFu}f;x~qkYlI?LvT~eIBQC6LT*YfPAyL^&oNb;`a4;K;KI~<<a;b{VV120xdpEwIG-XGrHWF8A^0=uCuE_O$w!SiVZ<PYU<XwvJIF(fXm7+oBcd6Ck5Gq@hcNvShOT7YJ38yB^BTW1POzRQSf+c7qwJ?^)a}%x<n3f1>L9WYxdcOSbE<>foUBrZC|S=P!ELAmm8|EKU{7j$CF{8+xHPpTxiq;LwS$s1HwqSWXKU(6Y6tR2ay)e}Ii76J6@sr)H!E3li{NBxw30O!3BE!-LO#O25j@X`henKI2u@%K7WY|e-k(*dwaB%2A6B7?^i}v-a0>I7N8Um;pT&aBXS85H>O3XunJ(B)9i?Qg0Y+K+dKCMA6w7Un2f<>zT%*3ACXf?YKf$969cRQKBdQru&Im7t;QG{3<oaY!YFV-;xgNDDS!e@tJ#q(XJ8}nd0Cf;~5X%<85Io+9Db%m2<H%o=$52O+$B_F|2a)@e+fv(++mahn8;~24?bNDdJGlh4EV%^vQ)(&lr{t2<a^#ZaiqvZ4isVLAFLEQYj}iT-?Wta5FZNk`hTu+APjV-+FSQ=I9{a|ZA$TY?fE>U+7|IYl*3wU7sT0X#$s?&>kw=mTQ2UYlvD^cwoyY^o{#0MGFU#Ri9ZMd|YY6r>qP7uJ8G=VsE0af)gQ)q*LFAqc!Oe|WYTQfrjfkZdvw>sDkEqSb&G}uyA_PCCR<>oWbp^kr*0yD>jRh<8yvYh#th=jI+fcp9ZOGqHr;@)Rf6EX&lRBC_lRTXoWXoD337$;tY0Fw`2{zYbf_qS#+p^Ygg6mL=*|OGqf^$<vo0{vx`<CazeLgFMF10*6mh#!snmUfURLNTZ3*JbLRkHRAf|IC^$dA|`g0~uRz=%~wco|XNh^`F5ov3BWoyZ-jmB<~*ovDq<LVJ)qlS8PJ$RXtQ)K%nFEZcg9;2(`RMLkSCKt4>~L)}W=Lta5$MP5OkLY+jOLheoNLGDeiMQu#3MJ`3HL@q@xPAy9=PA*9;PcBKWLG>cnAa|#BC3h!JHexmPYid_=SN7T048c>W9m!M4)2N-vo!K|j7=k0I>&ffc2aycH2QB?{ka~=Kki3oh19=-cg1VZ#n&pn5P9;Z>H&CaMr?DIxs0Yahd5sPH?goAyz<E^6r(z8+*5hJbKHd0RRU=L^1h2Ir1h26n1kX2A95sJx#0Y91awX$$o%wg6;%|Z-2G6tM@AH^O@Cbfa{9UN{n}gps^Bcjx3w~$t-$wjJ&1(byMSf4Ukrx@djNcO>_;2b8ve4{g5rXs5%SX;jwo&s~t|4?GL-0~+9<tEo<bp=}o~&~o1)s$~)duZmLx_JJsRhZR%{sD8J2Ef9bNDyWc5`f5Y5VY6!tcp+^VpA~4<n3NV8m)8zN4-ue@9+S-9TPU4x>hpBbcY)iN>|684*rxMh+)OQJa#Z$m^(|lh=`_Q>&8mu+554bC8RW3-h|79670l$%UCl@M_k7HZ_o}vJZw(=aS!XoQW~Dh~sVv^*vdr7zct^8L?Z`n`23gvv7vsNa{**BzYZmIe8uVrUK1F79sc+H6K}o;0$VZa&}%jgJlwB%V0ihc^$zg`MEF0j2JtDXK{S3Vm_-G;T$93tiyUnB*#c3^WH#>u<%-bUdwSA!SN%;%5FwD%NfqGlEH{#U86WwZc%TN^KeWQWEA23P=w>4C$%rRBkO10gLByTt2r)2y$f?Z^`-76_a)C_yNa~4_?_A0KMlW(p)u4}WD$bbQoEBy2>yoJi!4I$7^)vxgy2wWOR@;TYpA8kA_SjS5Q3i=TF8h3M$};l9!||o7Mh(roUAbf&!yVPLbH+Ql4mjm52NNH3(Zd+My|~e?7{MjaxY*AK2Ci?K2H9FD(d(LKMO9v_Gn2iK(0acBiA6;rS>A%CD){OC)Xqwq_!d#BtKwZmmxpknE070#>&qO!3(J|<b`B^>RPftxjyw9a(!|+>KJl4ay@D&xgL2ibq#q9+j=lV@V5-XJE_OXJIU9ne~_<}pHW4-KjUY?IoTIA$T`V{sCCJO$hoLB$+^hS6=*@S2*Ed~qTO#W1n;8$Ox{JFMO{dqMIJ!)Cl4Suq}C@lBv+)CBUdChpw=TdAor&ZCJ$y?_owD3=jUe+>Q1r;xi<B>l64;m9!7npWZi3mXHrGGoA;^Uxzs|otb19oM$Ki*ng;|Ar;2tr=L*4fs5g|Xc}8#{>Mn92aslcrashH~>Hu<Xa&~G%a(1$fT2cA9?UtO4+JKymoQv9@Y__%F9mbcp8?lYLmAs9-g}Rx%g}jOCByS>bq(+hbd~Ml^X8)i5OR21X;vI(K_8(0B=QrJd4r2Z03?r|PKMwKp%_-_-R6d)0vDRJenw0+n0h-Z('

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
