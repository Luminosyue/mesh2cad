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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_006.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_006.stl', 'source_sha256': '6ae65b58a3f62f9437e79e7cdd21c97a1c83d11744bc463a38902b52d50915ee', 'input_faces': 892, 'input_vertices': 644, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21372637152671814, -0.18154895305633545, -0.4665030837059021], [-0.10294311493635178, -0.03778664767742157, 0.2347654551267624]]}
GEOMETRY_BASE85 = 'c$}qO2b2^=wCx#kl)NZu0Le&@oSO`ibA};Di6W945fD*9FaZifkSJlvEMc3p?2>Z^2M_@RphyygU$5S+rn?x=`R9MmdFS4__3G8D(A70HpiLVjN}S2yKe>%V-*)~YT-h+lQX83!_j?X~uW$FB!-@?YJkn>RlREuTIID51MoruKjQ5Sv1$y)x)_rJ!ih%-^dzCLxG*F<|prP*#?K-f_prJi_l3u6lfMGp_KCDmI!9B(2f@MpWE*dCRsAynp;Q#n1rAWc<*5P2RK(p@gjfD2YhL;G9No}MaDph!sTMvBQO6mdl8~xT?Bn)n8CUpz`N)JD)FZFO8_BT_uIVa20*7N9rR=v+k%vFc;K^*08mZ;^?mA}$e9Bb@WsRygqkh%@sI39mSmNz#&ag@K+y(;%h>G28D-=0*F$3eyKv*wiaTUJ);hVqAQZY|B@0Dt>pdZ}9%OK_fVV?3eTX^TibsK#eyt>ZFow!*CMpUrUwcI9~~S%CY6ILbdzBOmt*aY8wl9+RJ2<mLSH&*eBb8p}Ar9=TaZ9OWOHoP+a+ztwfEoJaecY&<^OT5j^hDV2rC0eKoNzu<X1n3;9>8||Wbo&1rW^F(~}Nn1I;*7Mi6U$v3{+4$XVUHOL^_L1>Jfz+Ij${+qpSN_KE80l}9Ov&+MI3Lxn(nDz1-1*rqw;oV&>;rN=gli=C#0k{u%l&Pcl>4jZ1#!%ti9P-*pWyp`Zdd7uuXIC=Pn&4DPD0C{9gywkV?B5>1FxT$f23}yekuP}tOw(;ex6K_^J}$#D0REvl+Ci8`qm}4uCKSioxfQ}{Lq1nr`)=QaWlT&5hL4w@fXKOp5~l7a(xEV{mJ>4<nalA#r{_AyPi0KNj10dy8J`xA;bx#SuXRpYyKv6Q}q||m9F9ky4T&}@mJ69^q`Dm^tyS#z5bOR7;!`D0o7l$t8^8|PBQtZ{QU8C9v|dy-_N``l5Xspzd`0V^cwefACGhJ%3SFmoPE`kkBV=t_=(38{ZjFDUBy?rfjon;DfoHbcA5L7=B09`J+i$+7dcO~YphPi>-F+^PaI>(kpzi%&mM3;r-4gf?{(`cekksMd>#YF8E<^V3FbL*!2SHHI7(OX?cE*rxOGG2ziPUCzN}Kmc-*#PzBV4>eWTV9Pka@}?sb62AO0#%V9s9lSNlM!`HLdyMvr~7-Fmnd^r@r2sOHi`(CtZA*SmEKy7_g7O>R91JzT7%O}e>qH?KF<?vQEAVqLn*$BsI>z^yy^JpN>yJC2HPH7d4~bbI#hi2FcryUqElb@kS)Wp3SquEs~#RX)0|#!cy_(vjyYI>uA!hKi5zRC>4s^1*m2-G;8l(>lD<qpNXHx{2`#jejitLszzQ{5P@xzqd>7SAhkr2TuCs{-WM@_T3mBH^f(Q!p2t5K4$J7A@>udtN4NH4Yowmjn-S_`~>oD<axxp4G-gd%+l*U@vU*)c%N^*#^bNzD_!+BFuT-lIS##7dE(gDr^@{&^ubEceyHLrUG-PRQM!%%?KL?z$41bN`HSR!Wz1d5d7@q8`!xLC{qYA+yDA@Z$0E)j{ZjFD-59%6#t$A@;E8WdJR$cV>!<lV&dML{DqZbk_SQLaUkdrY^XTF6g?K;7Fvk-|#aFts-$r+m{^7jediE<7KYaX4&L8gu>(tDJGVfC}dHq8-)@_(2pX)X=J#oxX7tZI*3?Apbc#rQaAfFej&kXPW@cF*4+`6sw<E!Sob+wOKwdbyhq?@N}u9Nwk|D4Ae?S=}k;pga+Prc7I+Esc$>1bE!>Ume~>bh!I=^?eQZqAYWmC`Nf)`ZoIBI)+@D+?m&M$4aPyLD6PwO$)nEs~yjz!#o8Rs5xw*Sqy_Ug#HEY;x;1bYpPgosslFv!-%9jh&OZztF=o9!foM^dlZmwVp8!N;lN{#5m}>8V6lh<DhhV3v`UbD>}wO=@xV~4oVLy9pj*MQ^mnJ=(-vQ%Rip`3q8ExZ(eV2j%Ho$Z~g1X$#JVYg7Z=Pm8Prl46Z22`{A@fp7=@+`QK&#dhf~S%~;RRqrI~)kDGdr<Q%qN#=qK=`>Wmy#fL~en7%8o2NehBKr2(wyRM$+{Zh7@ud{bug;UG%47Y9T_0O{DE4Lm{`qj_pyLA=EIx=ldB;9^gO+H`2@0)t(7x9%IQaa)*UCq0Suj|Gem3iODT$6P*{-4#B^Ac)TiStq858bL&j@zxz<7PFV$=~0h2cbLPcc9xCXZs}Yt4<tk9+hq>Jr?_?iVr=E{ms!cJc*U@=O&zY$2Xztd4|%%U(3@-$NDSnzQ%gs(=GemdI0;a(v8o`aDVS0f1LA`9)ccf#pep88#SJCeBHk~>o)uY^Gb0(YX30@@p^7toc;S=*(voJy${Iew?&bN>)gIyi1p2Qei6sqm4V}{{9o|;51vTJ<Eiwky#CF}zKH8V>H2z5y1pKiuFty@N1Jy?*XCX6YTniP(8*Jqccts|?!?#TJ=nn)aekGq&#%(;`E~sD`JM43!99<`ZjE>zPu|D(KaQ`?u}W9@*f<x3qJC$8#8>keD)=k=o6s?j*7Pe0k>))Vx|9%U-mRniI1a|m#JUQM-^1rS^w-G~x*7+SXK+Dm#C|DV@0amtW5j+bUGJCe|Bmxf^NVwx(oLmf{|Tp^8L?kx`WXql4j%Hk_Je*2ay>Mf9<jel*ZXVK=o2v?rR({G9-fMq@n+?c?FRCujhF4FkCnPrchfdmJ~ebm>gDHq^l<zDsfT)vjOXVf%R2XZR=QQ8<yyIJ)VWdVXRoi4h;yu?SI)Ik<{6DVmA<06Jonh>m(q>vEtbl1jHjdLYPCfA|8wV}Teots9>#MTy7K}1n?G|tc>gNhx|E&s`4{U}=`$P4c1?VbbM#(KWPEiG6Q11@?N(dro=2q{*;zL%eDC-@70-))KU{bBep&DQCSE6r1{{?0GWm0<8>c(+`}Eje`CMDI?#D^JL^b)mTc2dR9P85UV3gGDzGXeS@q6<1^7FyWd~eYBw>X|(@4lyWecw~MzRsOE+B#IazE3)FuurP>V{QC3F4A+Mbp5%|b+u0_UEe1ie{CO7y1owtwtpdYeLoN7s3CRzJ|S3V>pot$vD;<5;ukNw_3$;;&5W5mx?M7foOiorjY}Rq=7F3qdvPM^Z~Lc6J@Bk`w2XK7f!t3*TPAV4FDlFRV%L9%?*X8Po<pzp!+N(Kgl<eoIl~<%p!|ns-|W^yW)aqxEk5mz6Bv|9>Q?Ul+uZ))+neJe<zp#b%g2QNN<PY8&!@-|UN6n(dGfIe%;Go|3VHIehcx1K+Hi2JXWZT`!2a##opHyp&zxgSe0QhE|I#&E>d|jq^7z*X@;W(IZ@*_87VP8m)zOP_p8RKy+#&PLHqsL(P(7#IhXd{M#k>83NpACf*5QSo_{Oi-`JO0q3r`&LNMhc<#<cSI2Q&Z3=eLI^Ji7H&H$Laj?Q_u`$H+O2_p2#0Ji7hmYF@YX243*AyDlH!Yma~byeCfU)ciiW8N1JuPgFFo^HUQ&ag2|%N!_?R$`i-xnqKPRDSvq4*j1A8dfFPl$E}-xb&>C{a1{Su;EeO1tlR!`KSb289QNqecQ52~7pi^56W@q$6&)#lIF5BAkvG1h|HSd_d=pvEc2~~3d2#<`w{AnXcN$)O7T=edr<z{!=-Izz{ml&0Ka_er=c(=gN;iv?lKGf7-;(odmFmLdFm;VwZ^73OAEy2qWjlHF(BYIv+`4*yg;SQ3=Lf5N2OhUZTjh9KYm4yjR?zKE%XwbPh7#QV#+J`zKI+_}^jGp!@i)e<jpT0}U%57-f0pKJWd7>CqxAF}Rz=c{Nt1q*<?3Ee`CB(v$a0)#9DnGq_%}19ZXQqP83&^&>+0O%=#5!d=bxA3$+|i(Ir`6emPN|PYTjC|Gvl<^-<Z~BvFxuF-`L+)-Z!c9l@n(l>nhLSXYJYlosW5ZaK3W%?Z5E&;C!WYYa8pjztyQ0kB>SJt2iB5SLY~QSLZP&P6y~Xzd8PGb1jRQPeR+pk^HUs?G{DMXCCXX<O5yhV^(Ry&qbEje81G~E}!dGJ>45|edZ}7e+M%vOjs`C=J{8Cwg)`q-_3IE_q<P)9#A^or%Dg!-0yjxD&2;z-ls}8yKZFtZ+@RT@jESK{bY%4ZvQ~%G93R}=!_@Ni8uIpjefe*?H?Q$yDw7yhSIhC?Xj%u`CHKS{H?@m*uUOPPyTl6g{&u9730Y#aSe_$Y>+4a@EZo_zw+r0&-fUn<$RdG)w}44pSK5>AAWSfGY(NJ<vGEMdE)U8<S)T`u1Ox<3ZCWf?_+ModFIR5DbERkkx%!z_3(`WQa6fLz2u3LsF~Ewe`7rH&8Rzke%QHozo%bO6L_B=w#M7;p*s9~)x;Iv{C{n_Rq8o&dD=B++~a$q;W@qjDVOqd<?ru_Z{>c>=a6^1d-AcSPUPPUI@a-wXP|O@zJE^nt|xxb$i(NCDTB^?=5f~*zVCY4&ogf3sC)7~6)GIs<7v0h3_iCUAM9y2n9!8pYk0pqapGB5=Z9BxoFANZUN;%*xkq^Nw1?f3>pt*guP0CI#4Y)L4AnU3$<vrpeO;t{!jr16i<FO}BcI^#8=U8yV{#tDS&qv0dw9fkj~+aj`iNT(7Z}0kw_jSy_q$Q&sa(hUxkc&vxy8}7bBm*E=N2>HKB?>9r<AULpHjO1eag|b?^9v_0*+sf_giDg_LZ_<b?5Ur{#++s=M~;O73<Os=z&M4PP+B*um|!S9_UptA(C#~pAzrZgV1e%q3w}$GsmqMPrJ~q!Y$`V)RPD2xOHnN^b8-ZsTM)E)4y2j(MR&%zp;)t^z=6f-Dtha(_iEMHNNLsHp1KAzo18#_w?6-ZcN#~J)%ClzNfzdrC+!cilkeQZ+zp{Lw~}*NwwA0BIwqz1<{`VJ}$jE()<RY>+@@Vd5HHVZGM%m&#yg;b$x!7uFr1}x>3YCzmA^5JHO$Xtn2fubTz+b?ExGoP@4DoOK%-^>n8L7bYn<8)?4S{-zoOam**C1YH4qr`CX)caM*D9-ZGX><a@CAT^l0lcGu1Fcf;`Q#(Zye_!&Q!CrioqwbG4h(Q@AiU7meH;;u5R&ox%K<LkOHIew!@ueWenM1Sc2<*)K|^rStPM2rJn`CGR#^Y?sw4+<>a%ICdGC-{9F(@E~b!Gn(y+`7L11Zp4P_x<<7J>QR%9(>f^^Zh6=WC`CRtjxXKou{s={_48QU+HSTtftL9ag2pGeuxxb>CU(rA4)wu>>GZMbxOwfGtkWf-Q>Int9SM2p=rPHe%|}t6CVF6zwvuyRxz($J3+3)u&)0#TIzO-IFBAml9!*i!2_gjFBr%9Yv*vKTNN=cCl?&^_(QjD96T)JE*Zt`Zmi4qEyh4O@46m_9(?{b&#!imr*!-8X`b)1cH7*n=l+y`r`h(5{~jsyK)VP0Jz<4?(ydz^=JDUFt61<fucy~}UUK&4bI0vuTdTSB&>?;vjcy;!cI$yE{5%?e#;<kj#_?2q53neP@Baf)J0d=(n(jPzO4pxLP5&={XT2$1e@->s@gI10yL+8G{+jOWS2^~wuHCOHUB6#dx_-Z^bp3wSiKE@GI{w=Is?zoQRi*3qt4i1JSDpCU{i>6XcE750d*LG7>u)~eX;-^<b^Nt^S7$u6dsoL_yLWZ`wR=~`U%Pj8#z(t%b^4{<yE@~b-Mc#TsNK6d`Dpj9&NyrLu1*~7-qnet-LE?R((YHC_}cxd6GyvWb=uYLR~>)te$|;r?S9qCN4sBj^3m>Bo$=J}S6|WbeZ*;3yI*zk)b3ZE`PJ@MU(wb5YLbpT?^Sm4@1D4a(RFn{6JFnt+l~8~zi(wp7UR+JUNiPL_|C1{AK&Ef^>b5iaqDJ&e%~3!j<4N%cq+f|jAi4Z-MUqY-*@K2k?TBhawX$DD^%R&@vq76K|}Ko-sAV6ku_?qr`<&S9yBL?=xz7JasFPDf0ieHcyVf}hn`io-Fo2b&HVTN#|-fLA8ar6V56)2_bz7Ll6hOVasP~SPO$0E{Cl%@PEfjjPEfjjPH_CSbAqF5=LARB&IwL@?VJ!=a&B9s^`q;~{ocky{JzwFpH+IeIP0dS>%ZG7Jp|p-^x&i#y#JJ)e#xzy|DlI79OdsvITm|#`#<zoelLcu-{(8Jc3!ehY~cNL{TaS*+1{1!=XL$;AAG(o-IMh+3wiylewX**DxJ7r%dhY~49>$!4?quTx|L`z?_+t=#z)fC`O0ivpX1~2ON4H%mA|ux&tK+$?^3eWR!@BB;b|4OxZ~Sb&c}G#g}>5+V}qV{m2N_J^2~UE-!}zwalG=?<#|u(2K3<FEhpW&y&y*BX$=o1xb=|IuQ!Qz>!#B4%-$YJH=mD)aqHm_>qd)DLJ{@P=6~zfgGxWWXmzy+x>aIOv|CsA59Za6JpEPo4}m7{dHU<zKkUEh>94wfFlNT@ckAk&A+&Glj!3%Mq3>3=?%Xr9TC*^sKDE`Co^e+93@66@SS^BXM^9Mi*6jm>Hbt7>5OjThgSAre-$&Kv*MzRmZ@4D>wfR+gP@7*1x~a{t(k*R%4e0v(DqYQQC=vf&sJ~AgU3;G@U4Ne{U4Ne{U4Ne{U4NfCakTfT<FCC>m9D=}op!bNsS`(gpE~~9`&8-r`_%E*-lySF?RlMGUvl<C=&$To(DnUF*X6#{)bp>S5Bt-MX<FDY$Wj=Yj9y(`|1_FJ`lB%NKaK8N`hWFLqsv!#`~Uk-qfht@qpn|kJ%kaj4}2T^9pO_`SPfxS#plYxd_Fef2G9ie`xtA$h}S|H`4GP@cx{1w1UB?B)&-JY7gz(FtOnX8tP0*&*dk#!fG5F!2G$XN7X=;@_6WEi{1NyQ;1TdA;16KL&j~v$?4Yo-Fyep1i2o(*zOX-qoq-WQ1S5U`an2&{S;SWDokP5HDEk{R|3>}4(axWUa|mr8LhOU^e+=ITz$d`R;D=B@4tNCo2*x4~cnmxa{3!4u_)+i+z(?R0z#jsifImSF4`JtB{^wmW&%4?^?;6ANuCYCjzTO9a415Uwn^<x;glz;a1aD1aNY5Z}3^*C_q&_y{zoGmF_z%J^3)>6)1-z~BZ%Jcpuo15aOae|w{uNR0GI(3mYXiIwPIe#p68;5FdA9N~Zw*eqZGkO;t-yal+rJuYNia6QfhR?dEx}u&E^!*K1IA1L1Bh_|{r(mB3;1YZKV!_sfZu@qj5$~cz5#p#=4B)J0oVq_-V6Q%Yy-w_1L9l;jt0LBUJ-Lq5o1~r`hD1FjOl3Ps@6nO^#8W7=3@V71Un6ljCcbW@%qA=32Q>nrol#h955L;;W2|b8S!nxz7_gxVYPs@!MBUD&BBfY54rdzd?q~T;@j|f8{!kEI6H(*gwJM_Z${ZR;6(6k;N#F2!h67p;1dz^9`G*sK9TovVRMAt6rZ09%j{#U<6~Y2<(V;_gtvfmz~>;&Ens6mbHZlew^804pGj{HBR&yE+yXWRx4<g_sf|j&ec*Xfz8jxO-wh-FEo>j=Z6ETU4Xgt`8@x7<#zM_8;T?mG_#Z&>`2*v36P$1l_#NOG;2!WZ;KyNmFt>Y9e>?0Z=4}V~T_DW?@n%@dje+;T$%r=q-UYvlx(!_OO1z%1-ojoWw-?6C{t~Z+vfdaE!oA?Nz|}bK#n=<x1iy*T@A%n>pMusKyf^YV1wTUdT%W=-d<s6NVfFA_*9ZUIV5D4sH(vJVci0(>_wPWeNBA0I9K`c@2zCs9$FMIbU&7=-(vzb;l{Eq;2d@uQdr>3IPcvW>U?cEGsM`dX47|OthoZd}z(U}JG2nzp!O4gxre_bI)4_-*f)P)QI9Y{l1*QkzB5WOa3~)Vg9r$|i1YkV)QPfEQt_M$qHjfB?*kDw3;!!Ui`cYtF^oRORWAOmk4!k*d3t)Tjc;s{#xCOiwurP27_!ji7FfcuM491+a2N<J=z(U}O(5H03ZpO<oC;l&tcoA0~M}S4Zi@-<4`WOAnindiw=~1s0coE<O@PC0+w}|m_oCw>gbs?Uw4}~>^5pOE2iLeR6@&GG>e~8ab;7`5{Ty===5pjR<u|FB{CMYLPK2?NO6ILBYyr!^U={Xkmo3LKOg2MhW*oapHrUEBCWiTfrZVT%!^d|zl0(*fI?gA$~4NgWpHIT|q0%O5<BK8U3Dezv%u{-bycz49@1?!6b5T*tXf~SI|Mt@Es_G#cL@KdfFPq^|ri9C10Vv%Dk`d|Zlf!pBKfKR}mV62Jv6zx0{*abKOoQ!x%9~<%8DE|rkHuzQGIq<W>t_TYQZ-Ms^aXJfoYOoRS0Zai-Nd7%g?+SR>75ggMItx1ozjMgr3UCDY74ROg5on+Anej58XUOp?+Pe+B<?8P(jL9wJni9Ep_Prdd&KN)0Ki|voB;FJF3}fF-SVv)x4L0ISfN8)9uNlnAh@ThMN$8IRb^tB~C%gbocpaRKcv^vRh;b2k4g5OlUIOk1?}i*Z0Uv>1M0p%=KX@GYdEf=`3&`_4Y$^J*6fu_oAA?_V<#iExUWZ*nU#?+{(qhayf~N)V0PF@%*a^Ig*pK=OTjOKg>SMme$Gi_TDkJ`b;ERQ|^0N_diL%aqu17|EHLxXkOZcxw{Vs^t1?>}$5w=ZOKR;uCKl3)ix(ZwBV<R37><``_b)w<3#K-l>h_^<ppr6|zBfb{c8oV|9iC+;`MtuGWSQh+}uu^_5CoBUVkFo^d6>zFUb;H1N;MaVN74Vt#3W)WSt8N&)v?#kQu)Lq^lJ8YudGPY^A$}P-T?Hn9Uj@GgRJqJB=&yT-xdL_pp8@;=*c7}A{5k`_18<44rohhNO~Jnaeh1!N*!RNT1ug(5>xXi}Ab5B1?_tDe!ia}}{lNPnRtUHNe7vxagjq1+lZ34T{s{aC{3F!)5k`C&jQDb(1#Y4Ka#vj9jfHg-)&xepldw6!*}#tA9Z_dCjQHm;;?sdmz?-1{bXQ#BQ-pmeY%+}a1Q_v^z$xG>!PmfuuLe#ApN#seVZ>JeSAu^c>?>i-fo;Lt32TVYZNZzvpKuzmA$UX7nFb^NHLM+Cw?i!A9}Al$tQoL1cmrW=giVDJ{}R>)zO%qv0~>(123K*Wf=@+z#NQHDTv!QUDe%7Fy@AESi=$3&81b$!;yr;Sz)PThPhekg`mdc16;=f}47@zbDgdj14@B7@U<L3B@EHUg23{F{LxBUqYYM9;EE_NfcsB3=Ft3Z(!)L;Gz-yvTU0?t_fbzP)cfiXC8z8I_a0qy5l$8Tk0`G&e{=jnJeNewNu#Bs`5_~ElKJnVZMhUAA91C6pWp#k{UAzW-M}fZ&BR&#X2fPmIjs%VcpD!$0*ka&5@Oi=(3EK^AH}u`m7sD1I#v;_251WU0(co)=yTS7dD`?PvYL_t$cz$33U|R4r@Ouqd6g)M`(gI%tPYYfESQI>iu(yR}29^a+hq8>o%;3dPRuY&IJR^Kc0?UGDfZyA|V&F-HB{S&9GsaZl*-@4om;yWnd~(Bx=YtW?155^<4E6H>vxC1OEU~bhz~tabh2;{K68I+g8~B_Um=ruQcyeG$@Z{h*fp3C~SHBS@ED`W^a06w2U?LYc;2Q;=2}Xai0R7;8)Xf5X9el8`s>0p_RtNt8SPNJk+!Qt(d^r4SA<l5b7!JRxFcbBwgOh&`kx+YK8+?o_e9U(WixoD|&p61>oP0XKk8q{WTZiK9M7<uUyAk!ti1!4p1Ye0*#BITM2^;KZ9O7qA)(ho?n|#by3Hwo4CqEnUj_~aWzmCv1A@*j(B_rM&xC(p~;t|g$Y?!cu!1uumf)@gg03R-_fUr@(qTr*zM+4siCoBR^I1;=NVip081gCcI`Z%wA;CFo77GY7~UGSptc?)e3FM?Ra3jqtF&G&@m7dBQ{NnzuK6$g$59}A!2z(0J<3Gaay7WRR#V!$!rZwecV@}VdzjJi~I4_Fwy80wY)jsq_V91k1^UKs7DJP1p|pLhvZT;kgW-yv*(pYdHk^X`7;>!DE@@#Vsn32WzPBi<Ic4xEg5H{f>g?P#Z)|79#{XF1{#Zy}z^_QD#$h<6b7E$|y)dvL-Q;NO6M3M2j*un~A8)c?#Cmv|<TLwaEuff>N739Bm11Xc&1Cv2{;?}6WeS4Ew<!0*6A!sZKG09*)eBIftNdEgn4M+lZ4_2vSr0@H&NW&+QISXI%+Li8mgxGK+t_A)_NeVT{Z^Pm$SK<hx*dobd|VZ;Xs`$E_^!e#)!2LDXhmni=dWyFUG>yLQ-(FXCM!up}SAIgZoFKi&n2cnGlXknv-eE=K`K3&*X!lnUdg3my1(}7=sQ=Xq9N5WYyJ_Vm=fqx8~2>vnnhrsdRgyX=+;qwsSNN~at;6uO%0f&RXk3J0q4hE;bk43*nfsX-B03QQx0Y3t_z$XDGgHHng1UMD^6Y$T0)4-=;Y>7vSXSkHWtiaOXB?OlAu~rf~@qn<zqC77!Irwv7N&KuOflmAlp=Uuo!tCJx;PZ3f8{p3o_aC4EPW6ZffQi9#2}>k+PN3h#|Ml@_!e`)wS%p0XMuDp`AMh!7PL$;U`oJlN?C>GX0sarlo&tT~S<vSw;8XDID9Zti0?!G|3XB5Jg|gRyS;7AWJ_BY2r*TM%F(7>5^38^Lgt=Wj4?YvV37*W)pI^Az%LaS_{sMJ~=Lb)PdQ_iy3Sp`J{5dtWWXLfE@=F2j1=^?2xzU$g=tnN(l@w(u5F<6>6o5wc3m}*Lh?gH4@uI@g(|g#*bxD5>SQxx8e2Bj;tc>`a!Ow9h|3bjD;AF(#0%icufV#xX(wY~a-v(v@&xtnP0A}&O^dnvrm>!(sP+3J_8E}e2_&Tr*cy3`;P+rC5n~lbl)-o^vPS1X3f#rbNz^Safk3SQZb8#xG0L<ay0elW158^q|zudqa;8cfrS>PMsly4REo3H|SdGN}>D&W)>VQyd*aOz_vlvi^3mIp5ftOQ;XSQ=Q#_j0c!%mu6jPGgl7<CPWd5s$*>Ou)?GwBKgJcxQsH_TS<@E+;Gop3%>rqkyHr(+Mkr@*=21Jf*OFf~SE_eg%PPz?(Mk`7<T@um4rg%RlrUGCcp|9=)dbud%vo=B#48{7bD(8zf1}UpD>nf@V40pc(%IRrs_a'

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
