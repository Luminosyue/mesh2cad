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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ff841231d7d4c54ac917e63c678c9fc/part_003.stl', 'relative_path': '4ff841231d7d4c54ac917e63c678c9fc/part_003.stl', 'source_sha256': '90c7c831e55447b4faac874ba2cf42500d77dc12bd92b39c84b28385074dedc4', 'input_faces': 980, 'input_vertices': 559, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.28676503896713257, -0.426430881023407, -0.1953539103269577], [0.05186363309621811, 0.23179882764816284, 0.22433197498321533]]}
GEOMETRY_BASE85 = 'c$}r32UHZ<8|4cyrxC@7p%n#2QBlmXRK}bWW*ZfAM9is7qa#Mliqb0Phyk;dm@wxYrp;+gnDh4g?qzBB?4Gk{*Z=v>{q^nFuU@@+sa_TTX;R-Ug@=ZJ1+<0P-6lURt!XMUXdc>-kkGK6T|x#G?>At$i<Vh@^)E^1G-}zfNgEe!h&IxvYsjE3p*|HYK9#$b_wlp%bn71)78=~IQ~%JeA<C~6+-FdT!ynWmctD8bvu~L)75pp#fBIQQTmB#arE?U)Y}fW;oI@=Y5^pHgPaa%QO_gnFeew0g#OtCTdo5PJ-K&`RMjJm#Z(a%&-?}J^_|`>-#Mg42S)$Z-(+%mH#Y;X`xBCm_cdegX5I^r@`2Jmg^R-@ySHwRXuw3PDrn?P4_{LT7yVV!pl0Hs+t7o~JlHV6|o0Pv!jQI95Wu!dD!g|{!AJ=H{&8nv)f34s@GvxD*h2mT8*OUCU8!x8I=VNol*CWGFKUqphK1TQEDF4tRNN?S?L&}q_F7huGaLw5_N_ZoE-8q+}Uc9HRminCPj`BaOEcIl2WQAY;`FZhIuE%lDjodE3Km7=P_%%tdJ<QZrzJGm3d}GUcsZU##o!jL5rI*AvD|#V)WRBMId+QPSpG`@x)f^$|&6H8dXMCcR(~R#GE9Ji#4!`|gsW;=o^DVd@Q^nU0cSCy_ULEPD8OT5H2h{V*eUjc*yA{$Ooha8!5599yrMG>lC%!HGAGE93DskdJEh)Y|`~a@w@-*TbTRxqWbeX41{p*9iim&~AB);Bapwz!PFHwAR_7U+dv7J%R-wv*k@6)e?Z}Al0EImwoz4sjCv;984pVDuG<P#Qz<G!hMR{S>A;1ACOKmTL#wOZxE#qat=KAZpMfp1+UzV31azc1)@S;}K;V~XE;tN6y00MuXZVY}pfS1*H~_9U*OS7k|W1c!;QHys2`SyR%RU5=fR{N1;q-p*BuLp$ChzU}Z<T=!+24vOD(n)q6)JK`JZGm39kX$RlC0nX$2=f(1QMIihOhjD%9m)j@5b15Odc`+x>cTgcoucs>pe_U<3US`hRlHNQv<FvHL)o2%5y#P5cGcZ(q<G+5#<@*)+HlyG55?{}DLE4Yy#)Tu|N4FQ>e&IhkUt6o!@MGGDuXX;4`uUy?^;S?vK98=W-9G9TE64k*y!hs$@^V~D=Xaary0i-r-*z^o9M`IyID+f$hkWYz;JVx|Ci&Ri(;=UE7Rkq~T7HqFU-k5qq`OfP?KAT)$wzx~Lwqw~v-q}vPssoKWuy=Ck$iODp^}dtx)<rSb;r?Pt#aM%p@#T+lQ!aOA;rYEM7toL_~z2y?BgEcxJ4hFl=I=ZWG`_L$DJ7=zUKb<nB-sN-Z(j4Pzd}OU*!KO$dK<xbbwzcQR>;Y?4$H|GfO4-CrXHK?a@+vz2?Ug^8J5Tab9=6$~d6Se;~f$KL3=I`)F(FkM@gK#MfT@c}CK8S-w$z|MWc4TUYLtbdg6k%J)U$PoQ1TLH+n|M*d6IBA=S!lE3Xq6UpBa9|iwI!ZE4eb>C$CH&f4oKj}O2&%RFbH$A4~xZVemzQIzY?>!vp*G-c2`uihGq`id=g+G3x99N6IEaR<yIT-oeDJ<t@xo_;0bfp`JZ#^;`<KO$dxGr^TBYoU%Ij%h_-zv#xa24c#vLeR815f72aferi|Ln1p#~kb#`I|o~7WI(TeU{`iz9Re-5vc!mTQHA=mxo`e#u=P{W$D*8TLAn)`=mT(!%xxjd0Pqii_Y#v{YUSV??2^7`JcMVd08GlIV|OEo*wB->KLytt(EdygVG^=uLY>LAC0A)+WJokqFM9eeCs6+lXMAh;HN9h@o2CdSAX#o{_ML_PNOl#VI%(?@r_0&;lF){@p<fVq~B5s`Df2A`P)`Zf}iOW=H)SAN1T0g&vC4mW`92{pZAYN`ZFytpCwFQBl*1@1b_Y)nLjM~madfJR_iRj?v@4f;LrrgN1xva>9;kMeC%b)NIvF{+VJBG&X@L5`0QHAe@`v(t+{W?_-yH2HeT|1SrO@Hj+X194U4TV-)9aG-&X3BjL)_MUh&SpcI=Xr)9@OC`YBfgzV#W(zi^zC-`cSN>S16B>36oKmsd*tPRfaTJ~SHFv1!UZQl9H6kx$u&D9_gUW#s%`YVbc7LwoDJQ?93;_zUAspJ<%#sJ(K&|I=^fD!%?&mvyZE>pT4VTX22fOx!A;(|p6YT&*JXb44kqt>Fu#Pk4p%ZP{#^l(*S)j3Y*z<fHZKDfyUT_u)sZl=IRD9N8_$|8xZTM0&`0p)YQ;Rn8;LA^3+=U>)<S?^3B}pS|$A_LK6P4`ZeLW}o%&U%1HmYhms8|K=ZSE$NM&X|cW?z6SH<vzaoUYhJH0zi(TN>%n!V9<mzq`{DV>r&wW>=R`sz&VL@x>sJ?yxBL5s%6Z(M3IE+qIbUP+IH@0t-&o``_pa2N7UnDGtMwcR|6?<h|M(wLe#?a3@Pjv_J<OShcC|DF{@t&rhtaoXJ#Q&g8}r0-_gnIP%B&}(om8lS^h*O}UbY`DAimb3GRisDjs5Rbywp$6a!7ygBgW4)Syst;j4g%qcW#MqY3eP$X?o$f^J_@{wz-K3QqHXINM8c&#kPF`^3RbO`M2GUb>X3Y<K^?9Z!(YC{LaYyZV!Ji`DiQOh_9WvkNXAlsrbfIJN&7i=AoaCZz%PV=L-DZz2$o8``V&@ieEVPTf5a-V_vqeg+Hz}#?=d+lHT@p1^k~4rJgmdVSf4DqrRB$Z@t3$cS6@)qThNTeeF@QelS;zMETn_7hkX50`q%WSETRMOnkFn3rTP3-w^5JDkGm|i_mW0Hr}Ir>)}f9d*#RceKkt%Bed*)qC7)q$@pO1<iAMLUHExaG++A#a-2Xn<a6Z*eCt`X!%|HpAM?g{_`BX>US4}uerNbShwnKS?J&>z19F@pH^eupY(Rf+?I-iHW$ZQh$I7E$SgM)w`z@!DPw9B92OeZV`ih(2-+U|U553EM+;^Oq2LD)oT$h<$;U8)NKfDyy$BlCxlIuIeTYP)@3Aq0o`Uc}!L}8>KITGVz*+;Uz)ed^XKe!a*^Z8YBKW=aORpu+LHO5IZO?qixdaEzu8|@7_FKg58HYwM**YKNslKQdNd>t*vUGN<F_`gT~aUQrYh<zZwd1V~N)lomO4otj)^g&0lt{A;m@-a&!z%O1?%47R9e2yHi{4w}to1*{4RYyK|Y$(rwG{>bJ_da5rxgP~T>wl=1O|CKGmu!K2Y$H+6gX`^<^SfFcexw!s=)otfpIf`b&-4cUBJ!MEH}k*Ohn?G}@n?XHV_K!V@Y^4d_N4dhj&<g_{qW;=V;uN+a-ZnKUGOVb#ymNw;8F4Qp72L*Ks&FQd$r_uz7Bj_3c0?vSAWTR&$2w1_=fKUsZTR@mb63r`AmnM+pVGX+Wnhf5$iW2;mIL6&g<0hpBzEE4X-EZ4eKkJ|FyVhaz4h2;LVcHz8mnl?$Z01o5WuoExr+J$NFb`K8%kiBE`45KgPb$_@$Vi{#}6d2j0s1L@!=i+N=3v7V`HkC+RJR?qOVTrSFnX#z|v-9!YO2_BZ@D5mL|gse@(xY40~Q-npIYBfl?~{0@Y`=ekS3G#cxZLtRmx3b$q6v<wTt=bx>x4!YbF`&-@_@cYy)<DJ{Bc{qjSZ#MV~zgx6Su9vmEkF0O4<*!P8YyFC1|05yme#y7d1@ZMfm1JHsYwVNjX>E31e6#XknRhhHVXQA^#>40RzOi}@=GBEJe2<<;pA+{t`s2+w?jKojU5r7Pw==F5-)Odg{oM!a6#r%LUuHNh?YL}N>0h=Ao#8L^kbbAPsEhHren<F6SI9W8^__K6^7~N+$32}@_VsK&?J<rG%?-av7qp-7lUUE}Plxh1T#fb-Wy*e+J?kfF*Tyic3-qpS#kZAxjd6FzT8uxo{MbLabV__ng<ZIBdUqT1^|r!D|6{lGFUz&-8{~7!tjK>#4qUJAPuGjz*j0Qp#)@@u6Ri96;_GD}MY}x-_f1E`aQ*5;i*GEiE%m8iJ0<PFHfS;Y1sgGsH1o!N*z~!`XUTE+r_-U|7a0gY{S)bT7VU$qGws7V#X0vo%dExX>ssnK=XP!@)<(t+i`TD%&i%rcqu5$WKljl==XPtn#&}|nd~oo$evyz@<|8d{F7b_Lv1n&;OR=vqqnET_?P6VA-?+1~{;>}{jQg(Qt1&-%)x>&Z?mqnfgr~GCqd)`M7qx{<gWq}~)-Bi9NINn14}-rw58B(N40|R2kq!4bw;${A>~h`hnbPC_e5eQZkw(9hdE8e2humjqb*5tfs@-JqjSWx4H$3;CzxN5^{n`Wgk8N1T4e*wE-1zqv?pMBsVqPm6ze9fa_8QV}v0`7*y%h5KxfuS%Z`iL+>@4G$J?A{+^TiGOVEqm8EhSosZ>|f({?*Y+3C_Od%X{q0EyDezt!)G3pW_hjn|fg!HoDZq`34oldSK>x*(cFv>d1f7H_6}H&PDF4?XP1o-rtYJ{rI^ESw9<}cZi>~J~XfPLAy#9gZmqO#AVcDPt51^liH!?Hc{G-)pOHs=YC=D_W<{yRafnH?nl<(aOp>u+AGDkp8kRTvF=uBFSedbc02bM^H~)+Z(Hah_-{9%e+~=6`flU`9C!UFjEB!+C7&eUT5~9#7bK1l-#Tx$_-1rH++Sqag7I(JOyr-mP8)v>{ciU^yPf-~@hl)l>eHOedi#lfwDzLZgYCgs_^sH^FF%w1XtwBv<GyKw`}NI1(%!XQJ!BoN?K*_^Uc8j76RhnD#-e<KrQg}#4v_gppYcK3qc(Lq*1gL*<9?(@{vFQ!#mMwZ`irI7V?0mrFM#v>(H`sM+7IE++kkb#))48ZS{pn3Zuzn9s`g&iGrA>0_J<7ax7ad1!uVNpD)x;MaDS>Nc8Eql>W1`Vj-kI+J0#<<)wL7SduK#@>lz~Ck~MW9_#Bsv7Y4?wQn~TGV$)#E3vJI!`OIUVW1Q<*Z!k^Tt?}%Q_=XMlqt=VQQZL4*?J>Vy-#J<EoTBJj_^$#no^SJ(c55F#KgRjGYZDJkdSm=t<j-}KS>P(#S$IT@b33;$IWO~yzG@oMb6&7-eU0|9EH~0W_rm%x)p@MrQn`t*Z<&dCKVpuIzj{r~5Blc6FfQE8iuTj(<yPnRWB+(k#%=piv|lrAu-xAnuCF8?Yx#QO8^udu9GLt;=1r@X7x^6A0KZ3B++U~qwZ*v|YDJ4kJGA_qhIM*&JP)!|+$r^DdNhJx+)Kt=W7kE@k7FBcMtxt${&UP;SwGls{gUy_(sU8VnP2zC*OpwydNX3NjGq?2`&b9skBG1DO^5xfnJIDKm?eYwTEQvO9;`!4qF>a~kdIjs>&$!Dm$7y@gni|#Kk!^~V`|iEzXReMDW+rnc_I?mbL<|BuTN59d@hUqUA=e&(kHlK-=ODIjOTqaBmYBKrx`0&;l8uVJ?RJb>#f8$=iW#D&-Y-R;#Eb)CH>45tlt{dK|kaDi+y_no@=a}yiWXuUC{3u3|}V4&-PWu8>5XU+Q)z`(tj;|AB(R=6qEFp2w$6&<I^$toJZ_?o1)*nm<gZrxL!6p)`2aCA%D*M#<P4fZrDebL3-XNT0hp8{LPC6ke>U)wiekjzqs4hIQL)eLM2&O8~uCA_etv?YhIkEp;uh(+^=nE#!7p&x~E6_@i8d>$>GvI?E!A^d0%5|?kn|Z41Xu*XB4Z7efTj;v5w4s9{x=e{V?wnSr6F9>|W*Ef3=O8jLVi;JK*!aOpl$5{kPC@*r#t;70;EHT#$0wCX7b<;$yIG+Ob>8X%=}X<E6Rj4#u}Sei;9E9>M;)tp&#aQmLgq8$CLUub1WiYoUIU-d59hg?wHfj&Y-ATg;2En=g0n7p9k&th=nW^ySX!wb}bIj^%L2b(q=@`$Fl@VZQyjLawLQbqMw)w&cb9kU@(Qzw~gd2ZCaziFOHE>fAoH;g@EjKSf~Q@l7772g~Gej4Q_<Vc%kZS3F-^UI6R$_D#f3+Sf8}_QO8?3LQT8rR_nR@w}kGbL>xe-p2Z%_6O`ERWBpHeb9Kkr|_vZ?h~#?;d`#1jcMf~<a6a)Snt~E;(q6CPwZ>0I?Vf=0vO+Vdte{0LUEkO)^P0S)N6tDZJK7XU!Xm5M}J%qEc;hl>(i(g-ZvS0bD>}Nn-0Hd7p&_BPC`CzpRs?F5#yfO%nSPkK5ynZ_ZKadKdyJ~J>na4(xd-YScLZ(D#wU#zgq(DGwe%`e42+Mebij6=W{N^zRIG`$ltFA_o1h(!g+eZ=YELoc72pT{gt`md%u=`XN}#7_VjBh{1)rcUuwi+U0c)wKWka+{|7CXdCG{@;Gfx#_BUfZ=F1;%uy52c9^*6jX|*?d<~a9LGfyPaKO7G~%)ouzD_1<HN;Oh^Jx5MFH?MpE`%1IhiLV{>Lw~H&65~$54`~<1yJ+$4A^oL4YTH+fZ}0Y9<^_9k?7JDR1;n><Ua)(HVxKPO{n_$;zSFqB$iD~qgtrjiS}P^?hj(wqdF{H2cKuIP%p+bIFfXTGBJZ<kiD<X_;b~Z>49^Ik_kG%wVGYIiSQ{?Ki^(nXi_JeR^4V2aeC=}r+W*f)u6O!Q6~DJ9j=SqQ%F}(-6!BZ1!8#^x*ig~N<>1$_q8&wIpI^(?Vv_jxUGTi>dc`L4IjS^#?<sPf&2J6o%J-2sCy1Z9H`<q_|3Bh?yo>$y_Y1MEJk({1`0=jef6M1bp@rf{c*}Ea!=nJ&+0BMHuj@T!zg(-`7x&3$>fk-7ylvs%_s2f-_Q}}ytK~UXKL1k|&$~xvLA%;vA1ylIc9^ucXOHJe`T;e?H-aW$J^NRczs1k|Xq0?zR$Izx@BK@jqiOau;_C}<;=PjFgYlg7WB(D7zIzkwpWK@#^SG8Tak%&g?xOs$G4fuP*0l`$eAiI_tv6zvsgqltXKER?OFHAq1=QP&4!CZCF<4)>Z6o*HT4;?S;`{5v<-9uhFGBer4#xFpCgrz&Ehz6xXx^*fKka~W_I{3XZk+^wS}6K){T8wxtCijsiux-FKVILCat?yu+ynEQZy}sl&IJR-Umt|~sAZ{l|K=CVEdA5=yox->(fnEubZ!sYyIQi}tNq=6fPB{Cx=Q|h?xscN9pGGVTKh++w_zvypnNM)KOG}bKeh(q>jk!8zcQ_fc1&M86CnEz+T@^Fl77^+o^n0L_~1Q&cdwR-e>!(h)aQPy`fNMk9gX&ItB3RT)t>x;^0(hC<<=hk!1-PbLH%#s)<yhJzp(E3_66_76&luA{9FEV|6{(x`w3bKH>;HAp+(ARw)%zoOvuzx(wl|HNIRLe1?xT2vz_>@G|cz@{_>n%d%9HKM>Aghi*->#ZTMSP%X??q#+rB!CPy!M4?)v51c`qyCF*DN@fqU#7875;H5Sj8irvRJvfFGX>bDI0-YIaus`(#nD%#;0?yK5nLOI_=H9|RCW1Lz18Q06cvA+1xIiwtVa5kK;Wp5qvGmjdmKHFC{!t<yBrvk+v|4R0Y^-eu@{pRP|i}hjL9IRh$*X6moW5Lv0{Hj$@|8H*V$p5e*{(y6+A0xh+_<Y{2_dJ06e9NgSqEmLDU0rO9@yhb3oO~WO{(yXr^B5QB<QxC&#k|(w6WW9MvJCngo`YLn$D^Ej8h_Emytp53GoIJCfS>qzI?8h({n|S8J1uoa(bTbWA7kl1emT;A_m=bFd}_Wbh<ykBd68;P*VhOug?^;fD<^vACGK;k6_oe8wDVJ|i_RE~{h}(**2(A0?HY(~S&seReVNd&7p`c6{8sy-T<uW)G=H=dot09?HT~R2^snpF#5b&e;`v;*wa8~{x>h(&dAuLfyxH#G{LY!Si2v$8^xq~MrGILFjl;e}iC4J39zBEQcy8<QJf`mz8;)DJv*@AEsON#JkiJ1w7t!~{aUW?ZjrOoHC`5Fo4g1h_NAF-i?Ik+2mgHmWUt`m6e)&;LrT$O9!1&p9pR_-7S#_*$ja_J0TetO<?}sgnl6w9Yjd>^Xt@wufJ>2Ic<)5mA^amsHv)s2>a=YR^mQjtw*H=%Ma@yua;CwG{6klr_xI)^YJs-xgZcpSr0&UZ1yk9!+3+6T7=s{A>h5ulG<oMzp&c2p20q+6-Y7W1(A@i%A&W`&uFFX2a*pk7bQAe?#@n1I7bE}*1BQN6mEuMh-SzlD<GwnfDdCsAqHc<aZYK@TdZF5$}6I-Q5o1A@3OE2XyO0>axc#7Ldw4XxrrGEvz!1=Zs2mdhUGh5UN)X(=(qeKhs!FxY7?%_FR$6N64M&kYE+ih_l?AK<roPVmLzn^bbZv)r8ogB}4&<E+KB*HJ(8}B_ne}ns<ny%x}A3X6s&de!TpX@0x4(+7@-cz~03-u74alGi$et7S2;zE?OR(tp}{N=o?`3B*<;(RAaz3@KNNVysLl>Q*T{Z~rdUo={bee3le6XpBByNiD-|2%DyXtoD<j`(yM)`54I!vFaJ>*Ud?(BES`v7UPM4&&jsK#b3Qio&nB4cGhaO<b>s(UV07-obTgbY?x;>k;wIbUs*b*D&y&WGy!tM@+xmc#iNax9qEEYcgRSy38NX-Omlf{57MY`1&Uw>>s%_$9a{GgdeaQ`M9RXc>ZF8_(q307(cWAz&_6K3RA`B`+lb03-=-O)`)Lw{0E+^etC`OF^8@qz3Un5EA9x}f`0l~d@c0>IbVI~N7O^QFuVsh+gHY0TLByP^*(gMdruEuVqax_H<Z8kSolf%1A)u;|K=aOiT1E+59+g@-*n0UUmM2xHBT{LeCsClWO(8}NRN7f`G0linc{o3#C_k;&zN_XenY=K8HDG2LxZIq8rOnni}r7Y=RmhpVLZQ;DMCI!!rwJmMr^`$42%}v$lem~8NV=)Psc2HUvhI}@ojrJzvLN(c9%52=Sh%utTo&qzVUH7o?oOaj^}Abw!`Oskv$<{1=`2O-+V2XC-U(~ME-{_iEj;Ah4g8ApkMMmOl@DbvGV&(vEmznMX}FzZ>sFS80oUfxTBq}hkc$m;b`|-IQ$WnaQ|L9ELgtp^bF&a?`G_y)+&T?xU7fVC+RNl@P7Bb(bCV2G!f$e&-d5^{m`$Q-^REQ&;;$dRv`Y~!D`~~MS8!$^Osv*sQ;aFWxZ+tnHl>zskmP@s43QiHy-2t^idhHUh@ma`s_hDye~iCD(0P@$Hg}rRl~mPn<rQYrl^2<{;x31cWaL9NBce|zHRG$+}FPvDCcXm&M5PrR_zzwW4|4Sed-xcWjwQ8eu;8k$%%c-Q{T{j3%H=)ov9%6gL%BHTsO1O9PGnv^F%xS7$Ux2FCG4V#XnU$`J8AI-w6MX<0kz*!mWSBx0ib*=Vh7|WS__ETT12$^PLy|9_8Rjyzf`Ih>ZKX*IDGBd0k2Qyg3nm!JqiMiZn;?zRixV(ysO6c`^S!iI#Pac_mQ(?!?;qF7nyfQRYoE(;U=y^#l0(nC{b2j%q2Sf9ut{%lR5Ry5aqnyVK!!*n;}0kuR=Vli&VID%7vdm;uEdD`!Wf)jYIr!A^f7rA+lNN&okMBGt3>|J9#JRVeTO|NAFW{ahSNJx6qR#7Js$Y7??jU$Rm^a&vNPYDscya%XCJa%b`&YDMxO@@TTsj||0WT@i|Nxgr!B{JtXDAXlcQBUdJ;r(V*)>B;9c=rr<q@?=MpqL!mhBP*RnE=R6JT|ib^ja<?ZbsSNFp|}yX2e}b>5H*B6h}?(ToZN@pfuXn|L$Q^ixGOb;+?70>+JiitJepdEJeu5wT9Vv`T!mVIT!rjS{e$dH&hCgz)YQ~J$f?Qc8H%$|3y`yry{IM0C0V~-48?v7#nq{e$koZcsDsG8$g`<^$g{~as2#{N$RikvTT>g7TT$y#8<Ojh+f%LN_T)(n#o^Sh<ZyBXbvQYKyo5TMyo9`%+J?NCJc?R{Jc|4m)tmem*`J!7>`yN2bd3u$6z6k99%=?^CUOR{D>XIQm7J2Ao}7}LjiERfH48ZxIX~5ltkjR3pInBaxF)qaxhA<EwHLV`Ig&b?97$eJok3ntUPm24UPq30#7gQ=>IkyZ*5su2G?bxu7(?+uhT<mFdgLbL+SK;s+T<YWBytdWoFg_+w@@dMm4=hIkhfDK$lJ*~s7uH@$h)YE$-Bt0)KTPE@@nc|<kjSVsQ%=C$W5t*$xX@CsQJj%$d$C@_F9RdIBCpRT#BJMH#Gw}H#rT}m7IpGQB!Kk{}j7Xvyt7%?vD7AT9lfNtTY$7D7geRKUrxRaz4l0=jn()sBYvx$j>x{;-}Of8d!zme;sj)`jPsB{E?jB1)(@MRpphN$MGcRCjZ4ytW)!mb#g67)T0)p<|7v*XQci?&PaZ&LDjiEW+*<yP@F)0N=_i3p#DofLEh(77yB5BH#?%6BYHdHm?OSXk5hY-m5w1FC!eCuC!Zppqi!Z|=CRH(6u+Z>B)=mUae=Dqq1Z}oMa@rcMQ%*ZP0r10)0m-nC_`~4s!r}iZcD92Zc7e!x|YEV#r+)-N^L-`M{Yp&q8223kyBGMl2el(X;5{&A2Af0)I(&Gypo|fnwmh4Ca<HO(2~b+#p|j2wB#{gaU^xKmOMu&?nj-kCC@2}Yf{H($#an6GSuE$@|>l(1hpHv1UYF;Q2ZxDacAl=a%b`pr}lb;q4<|0MmXxQf+L176qli@@5@lXkyR-ELhm^FINS6WhT;#@bL4YuyB`>eOSnK)doAJAj!RH`lS`0GQHPL+uuP?>>e!{IAIN7ManTX$9I?j{OB}I~p?EEI9eEwouVpA+#!!5mq4){)4EYK97DKVgP`rk^j=Y8(MO{LUBJZW{A@3#MW+=X|`T;eTx`(`n=NZdTyqckS7IiIoEzffnL-9Wh#dD~~$#cl-8H%q{pOCMUU0k8J$eymy9FF+v0!^g4kd><Ri44U@s3!Rcc?ES1c?EenHHsX?dR)#>e2RLTe2V;ndY}A){L87{e^K3B!N17q9Fd8dfuT4()s38<{MiMe_$5{4`;wvf3N@A-%WHXsq4*F(@dD~B@+@A<1q{WLsdLDa$up_z$ur4Ysn^L{$#1FZn!R<p#&7wZ;_QwnME#TMN&b`UL(M_<A?I^yEBW|Y@lA%}*$l<|sfpx7ww3)1#Z##($WzJFsLRRA*(Rnj6z`zEAnzc*qy8c*RoDBSOLCid$L|#XbZ82yJ5~Aa48<9#8ORyQ-&_!izf;qb)3Z%|XDHsyP<(*;l6-)CntFwNh3)AyL-9Q70`da3n|TbyW2rOAW62Y!Tgem1G1RwYrK)|z@U!AiF3D|3u?oex9r44#uN{%s6`|O|@04EVXXRgJD7G>b_on_J_a-OJkBUby6sP2I)$vj?6c?mg$OXxTU6adHn4!1;wGg=g*_Zk!*_Z4`^&$I_i&FEEi;{~_y~st##i-uoV&vkk*q2k9mg-IR=5Lbr@f54QJue<Zu~OA1llJ`-C+!U??o6HSlDwCwSnV}7r;en~CM(@fRyvhDlH8p-joh8wkGg~0k35e0jy#UMi29Sfh`iY)xvy^KXT=9y5Q>kvAQY!^g}Redkv*sx$sXh^RMnre@UvodQ@M}2jjDXbO23np?j~;|4`3(`r5+%MlGS=Vm^z7ifUNX1S?N5o(y`=8<fJvf;<nTYF3I-@iaSwbT$1l86c43-a!I}iQ9PZh`o?tXW%@&@N%t>`TTw5Qm0HPRj%ehFhSWmjhUCK3l;pzXG}QYVI1Txs20cK2NIvL@Fh?wRM1O{28}%UhAk*6zidQfc$5HQ-<H!%Fs!R{~S#b)Mvk*B2xd62hxd6GoBL-3jQyY;RvAzaV<H$-6lgm4fJJu0_j)-x@U`H&Z29g7rMsab+Z`wP;huVUiN?j+_tR0%!5$=xolcBg6H4C{IximE^xiq;7)q`AxT#cbPha=u<&_t>SS%u;^)U0F`ieFN*kX0!DkLpfVq4*v(Gg*b=yHt&=Lh*H~E7_IxbDg1hCPVQQhT;oURi_vDS#erNRHBxnrXrUk`%_)X{^X)mja-!MP0dWs%xmV&P+XUxxEZw=xf!`7wKTaUxdXKdxdS<bT8$h+?!{1CgPMa}gPhIj+Gpcu#jhQ4m3oc(mVAwTlbT4rNxnmUL%u`4L48TSK|V|Uk9?NAmwJ!9m%N60m%N6&h<crToo!+fLvclh;sELtasWAL&r|Va>IL#-@_DLiH%ZUb6sLD;TS?F06su=+YW<*|;pKPeC{@=E9Z$_q&d)T84gPLCwGw$ec@(uAc@((|)t}sj97HWj4k9<DdXv4`MimdEcBR%OcO`eDHY0Z<kD<0Ck0D1;JCGyDo2Vh=P2{80UgV?Xq;-YjKGYiIKIEFzY~-5c>{QjJv-7j!S5EEz6+`hA4bKIXZlqo%ZzOM{UL$WK@1))&?<DV`-XZTH@21`$?<TLMo+Ym(Pp9rBPbasft|7N2>(oW$MeGlX)&HMpW=EuQL`G^(YG!gyvM;qD*_T|ET9#au+>zRV+>!h@HI)1}c>=XBc>=jRwH>)Txf4TieTL#-hT<XAzT_d~k<?J~NOB8m19A&;WolV+WpW{EL2@Co2Q@P}Gwa%ep*ROaaaM-n6x3AY6l52t>*T^voYoPZ)V$P;<h*1bYEH5bxir<6T$)^$T9sUvJdxUwJdwPV`Zswgc^P#Ac^P>wwL5t(c`CINc`A84Lvc%LeR4~3Ek`t_Hlx-jD-9+$BO46GbEreebI9|kBgyl~1E?*?1IRU~mB}^8#i@nJ#mN?`2U%$jvV~lXp|}V&E4c_cX%AenJ2eH_o$N++(UPCRDb}cIwd8+_(`d<UE9n`ZV)YEL6g7bAsU^>+iYrp{YRU7jVx8(k*2!(DrM2X-OYwAST`hU6Q@oZsQA-{h74N1l)sn|j#e1mBwB)f@@lNVoEqSa~yp1|lOCH-5Z={ablIH@&8yJemQCpJ7k%OqUwB%>dife1hZ8zzewPN*5Tipk#XWll3;{Mbo<R(m?bf2X-jM|K>)X<Xe$&{|58st^vP1HH$P2{cAdE~9+DCz)m6nQYU26-?!kXoD^NG?yckd+oA=W#U9Olm#FQ0zi|p@Ee?C#z8WlcCt|h}+ct48>=t&&g-VC#f&UC&}>)#ZRcJ98dUJaR!zx4><$b;)vSRKx!UxAh{|v7r83AIzw?zstZ}EI?tT^tT?X=Lh&cogPojI7oQl4-#em<BMv*FCqwa3>UZ){@>gnE7w~6#0sO4|0EXh>48=+Nhl(puRbCbNS@AFCf0+D>e1zIXOMaH8xU+^aP-zir7cF_5?85fch3A$uuJ&XbD^DIvJxac);oki;bu4)-)10P$B`4LzX~t*f@tJjek$T%HZ>2HR+vMA9qe=S;N~5UzwdB60cq{dcmfSZLZ=#;mlKZmaRn&Mbx$i4p&QN@i`h<Lt{E({Jbkd%W;xugM7MJ8bBE^NB+I`ZVl47;z6h`eytxfJp?nn(JcO<u=RwcI~x1&}kw<GsuD6T`zNzTcBQiq|q1w*k9RrM1e>U**Z#l@+g$)DK|lJ<L)_Mirk1K1xFuX4m$N1UYIA)h2)Whg%9i0#x1)H~!0<S*2-<S*ps48_sZRpe;$6i3W(#6(B@%}^XpokE_%^ok>?@zho1c=9#sN%A%FJ?d5RJ@Q@ZIr3fdd8hL~&rrOJp?Iky5*)G75&u#zk^d$CM}0*8kNk%El>CPLfOTSX#1`ra@)q(9>I3ov{`Lk#@k55<501#}xcC3V5vi$Z$V%1ssrgy)d;aDr`6<i#o}t)Iy+pQ?cTzW!carB)7n2vW{^l|i&!=uD&nIu7ULbEEzoLF2yShSiQooQ@D9%HDPFA5ft3#hrS5lR~l4+yKP3pV2dbs_c{*xZb|J2@!_S=8p<A43-@2|N#|I)jRmi*Ftllm#ueVFFz_@7#cT~ITM_CElQXmkA'

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
