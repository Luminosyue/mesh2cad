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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/29e480b958df44a2ac3a4ed12b7ee1a0/part_005.stl', 'relative_path': '29e480b958df44a2ac3a4ed12b7ee1a0/part_005.stl', 'source_sha256': 'dd1e754fcd5b529e757bfb6de5e730693a468dec080038806191ce058be3a859', 'input_faces': 831, 'input_vertices': 600, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06397861242294312, -0.1997821033000946, -0.11872343719005585], [0.13496799767017365, 0.31029370427131653, 0.25417762994766235]]}
GEOMETRY_BASE85 = 'c$}r31#}fx`0XbUAb4<x3zQHXf)oibxC9Bo{e}X?gF9g;?iQSoOK=O4AVDt_hZdI>>4g?2Sn(n+-?w+#T;Bh!_11f=^{xH8`<|RRbLQBbnY#!KNa~r{z`y*)8Q*Q!ofQp3B8`#R7}{;%;GREp8&tAi{}CRBxBBugLFYGV**LJRhcVO`Rk&-nK|c&ET-jFGzk9{P#chSVhYTD%Ft}gmkbzyhiC;Ik&!BGc{-7Sg{kz3~_N`F5ba7kRBE@ZEZ2yn{Qb`#e*tZ>u7c)uhQBmiI&(7-cYVXxieXDDj`sS0nhr~CBHAVVVvyO`z;i)yfBSkg!oqc+$@BA*!LGg{XH@52MhOadrd#)#kHJ{ky@NXW}^rrDn^Kl;EqrO>sil#U6PCuae_*YTiXjEU*+kZK@PxI;E6{Y@&fMZ(TEC-Khdiv%v&lCE6sjGTiW6ZrRdfbR5D9@ez$jA1*`esx?oLAhaSn;j%y*6q3B9}D1W9sESn*MPU^{wjNk-u|}9@qR*Nqytw&srW=Xs4ewpYEqOYWgc5)VFV2x?9WRSx|j*P+lDOQ|?82oZhR}>v1oa(Dcq*cXmm7*YCyEH-kRI&zo6&TSWVH`gz<_Esy2pt;aPtH&)+x(M|KWdhb@>c`W~0%_rj`P48NLBU1Ilqcxh(LkIGY8o5*3L;Z#D-*&?Fih32J{+tHt8-87J-F-?sL~T<_uhP%Y^CSJabDG|@^Q#`mS@9my7wrc>sEzv8s8J_1zfM(AZ*7~YZ=A}e<#epwufD5U{gpV+PCsk@fjbuHao5G^@ttg+=FLl5KC5(l_01O>P|q1M;=HOhR^K?^Li2atIIQJyR^1SecJtzh`aOrv*S{b8gZk$8<Fq~4VvlS2%rUi=X}Utk(H=b4YyQq@<<+-#7RPnj|5|+`-NvPwe)<Y6zct5&^SO3-vHIp0tp~HUq33J7TBE+Xbsy^CpI}_yyYm;SKQF!JW6RkD`Bd{$-}3iC{ghZUPs>H$@M(g2esW3MkJTnC($89o{1=qe_Gt?}i}Oyu4Efwnx&iIvd*s*bmik8Su3hx+L-x+qboN@vC(~*4mwW!|Tm62~<JvRTRNs*%llsngZ;`&-I`!>8EtsSEync-OuNS86-f_N$`qpAEJ+8C8m!7W?xM+rc4&99UG%d~7Xk|@DyX<sIkK5}9^wVke)i-zfYk8~!+c0kYSY?X(?R_-8%Xp4)z{;n-GXwgI<Mo8Sn*Q<D$?6xchwHT_P<`j#^OMwX9jWca+P!{yV&B}cUeC)I-2wf%W5$V^{zM4Iy(8bZ(7!u0bgZh=4}O*VdY;zoMWLFW?caVN0`2%%XZWjvwfxQ^_jG(SzIcz(?}z-P<#b)HzF+;m(?;p>&)-D*oHQSPsy|2S=h4$qZ%some%?r`zVqco&Bu{B3gdaoMguhe@e?$?&9jt_|JL(qA!yetQ9oO!!tWl}NAnpnPt%)S8tV9Or6|=~(+~cLajCkY^Nvx=)l>6dxC;4f4@LTnIVWnpa^5kz=G~Xrw~{u4f4j#aH-Bbb^=-kocO~|Xa|Y61UcV!;Z{B^P<DnUM?XX+=pjeFaW$JHnOaFEr(&xLs#?AL02LEc~aJTXg3_?D4CeLuoKTje0$&R}Dck`)lc-JiF=6Ab}_Eu_)wx@s3*EtmJC#F)En?L*=`caZG;fa0cgh%K{p7oBql`~yy^<BS3uX4+0!UDACkdYhQ@|iPPeV0$|lWz5pf8$|2?$rTX6Q?&rTB&d5k2vLa+#YkC>IYgo-16U56~6!c({A-pasENgf9$)M#OaOat<`t=cRu6R9$KE<r}><)optjEY*yc%{p&8be9lDf(eq8dd5@dFEI>coMtpM1$MD?0Q`7B9zt^qaQsmL{*{s9AxE;5^OFd7cV8wlI>2m~PT^3zozuR#y-O=@q{amGA-H!Wu7S<^vKD(!%wNB@MBh}yo?&nowwdQkVx_drxUv!*x25oguzjukwZ$_hC?*6n|I&WAr`@8#HD(Lv__<Y$t|Lf}}X#Pb{xtG)UqmJhPriWWS81MUy*6Uxa_&K+H9IeKSy2>SubxUviFhO-ynQd<Ad+di6jEi<}Kjo%rd#v<$ots~}i}p_=d$HYae&n-x`gzRa<!*jZ&H4H{L%*GF<@vNqeb?7#v2N+tH(8?EV$~=&f5LF}t#|9(&v(kWrJ9ec%zih&SGfAN@}sx89e2(~9e12Xmd|zb_fK7+e)Cpq+}rc^m7?}Gmk+q*UoZD6t)GFl&%60W#%g^zCPg1~^Fua7>F1y)ZoXA?t=7A1{u+0GY8qV!IG^p)<2nycn5626a~p?^)eiN|8$MY77xdI|(pklOvgX6_-_foQ?q8DESKsuAa~t1my`RJH{2b#d?-v~93r|r$YjLcH*BVFN{Asgve6xDg)bY)DI1+x;k2vn{zB(T{$39ly>C;)qH~Z>k7~e`&o2u#SG}ZL3=7TWb-JPqx<^Kxny1I2R4sSj+^?xd-J?x(P#{5$5<s9KL4eh+Kj+6F7vvr(w-B_=_<y{N&-L;3fkEj+nJ@I)NT^i_lIj<bT`sKze&EL`g^5Mk3HKPLVYaV{V`aJR-{F4EwhsGl@|Mo3~{<C+sj>E>pRyqzlg96ld#@JDwhLuro=dNNt9MTl?Lem{uZ}uPS&eU@9e#&SVt@E{`Q5W^CWCQhljgI{>FO&;a-`VCZ>gVtCXg^<fBA?pT(XO_9z`FWuoce~xW2~q1KEOD(J>@L)izOI8&+TycT_MX7r#FK;!e5jM<68RcIxqa|CydYgs%v^%gAwW{jPuUnL-2Pc7r^Jd;Czko(D-l``JAhb`<>Hc(0&s9R6BLtF&F#kyki{qoUMM72+UiroO|5-#pQL}Ho7m>@)$$gsBaBhqsMb(NWNSBT65rge?@(cIgWLp?`HTfhHJj|!+-1fI?|p*{x_r0e!gp^>m}E#KjCw}wk3V7^P%BNJ4f^3y2#r51np|~_wdIQ)^zrhdoXXVXs*69PkFST1D?2lnH#LWX|+KAiVZ-!8Xuy*u`l9~)=$Ux+D@Fq#=t-NkG3CI+V`gt`_{cM^_{Io;5sCvU;l^BUq-5@dc7P?*TD~~?si@N^<9^+Khd_7&V#lJKcoB;2VnhHWWQbqr|$*$wa23#vd8Iq(nuGFe4hV;bzQeQSnr+no2$O%jpNSUj`eDSf3J|v@6Mo+IBs+k_00}ju^#(e5Bn_BhpTTnx?%l!vc1k5jsaonJ4<_`-}N|FTCYp1ZOCW-Ae3{-Y3wsJJc#2at%2+QskioLdzQEG_rAgX<Fj$g4<+`UDVu3Nt*2mJmeNz_S7TZl-2a8`*Ydmm$pAl_KgOB!Ls8H3$Ek06EWtQ-F$3;fhlj&|<cs}>lJm5FY@K2;e{(!Ei*&?&Q_+{|JGcCS@ge%mj>NukVS}~@D@84gGu~-+UQbvjo4s;kALNa%`o^5wx^A(ZN^=hVHVEs3q7fKBPb@*b4U9oP0od;{TJ<=b*f$<DLI3P@^o*NdWfRtE>$_t8o8bGW({ah%-&B38+Y#g+lN;yjlLz}zjc&tlQyIq%?uPoT_7wTtO!1RmzeNRfePx#U2>(<M9S@yH>f^Y7HV#8O9fbX`LN1i|R8RP83u9j)!yAl~Q4`^ZH_~y>=$r%NVdQ-H#d@PWXG`LG(YHRGL;I}N7W+k$w<3MuHeD~-ZjD7fk30ZB;x+p1on+ciU3K25Z+=%2`(wF#>vd1?E$fhupGJXgShp9?ut4*<a{%knTUB?v`F{I!+;h%&fb~Cp>*xmc9pSmO-i&wkkv{t_%!7~8<2X-Rsc#-xi1Tgw0Qb4Ky23x10@rI^GK_~uEaZQ962{@rW4E~Ztvg{nsk}({Ype~+aa@i|_Ahm?E*f_n{_SO$H+ywKdv5mv`S5<(9N@tIN#if@`<KW4%gt3f4%=#^S*Y!2=C2rUZF8`%TQ;ZqR+BB7zm4~C3BFO_2lS`GGcjMi>a4z5XFkg5DuUzEH~N&s{tD+!YxFIo=QwZMkR9s{`bN4{7;h`4({aNLc>=%hOQg@W4*e_m1Ik|~7xn|c7ImUu6<nl#?r@B^ug~c5jZBTzH)4FpX}wQrtoIkL<n583^Oy6p*IF&lhaT`hWkP$KH)NlipRhie;=enwZ!}u0`CI>F)%{7^)1mOkb=7j3O^advJ?2o~I(7o%d7-@6Pp5CZ8mjAdV^S$yw;Ow+;Maey>u4))^7Wce_-W+x-9Xg;k5_elZqB_9e|;#9TXx~0#J*8Kxvq09dv}z7=xg=OFVC@W_Vk1^v2PUrO~*&uk$QSv98L2sR=-sw?t^kI#`A`n#o<r))$8r>x`A;oZCCi*7qW3*$Y~5z-+bnQ_MbNu_EqT{o<lK@?XH4-y!$hep8HOQ$$h5;pX+M-zMeV{8ow_?KHP7KZ}>i1uCp5!CvLaq{!ys6L%Wgw?Rd<qEsre6`8<aoSx433HAnB`oMS%2ACUs{W~1zwH~Xi?eIWPK?A%Xt7U+!nay96x$4z+?`xaUH!rwB(f%a(Pxs2B+_@DC3*79E+s`c;uI7NN4?Gf}}KF2ZdtVa4>7S6wfh5N+gPWZ=jp}f3rbw)gfU$2q2dwW<3txx;B_bC6z2%VSB;NiOeY4t9!6!kC>_2PLP`@(_M;Ag*v_2hh)j;po`?ck4}fPJ?{xW91b9;$xAeTv=7!t<T<6PDt<lA~X*vkoNoEx!V~4s<U4LB}6^%su!HU)-N2t&VnX<yofM@-fEA&1-cWa}6w}zBTC>`tM&|wEf%541n*q2m6_0QXNU`C-h%y-Fv<6j;u40{@zB+$5%Sz`g$!x`d8R@wf^0ArElvNs(*hoTCbyV%7t=r|JLIEtr_(R{x|!*3BK{V494?)Kk0aG1a;Eu;T(*8W8(_;jh&BvQQ!P#|Jhuh3Hu9NFBxN}q5kQctv=#DE_-pTGY1EtJ*}UO{f@H(b$)bJ9}mA{QysUhG8eQw=BO6BPhsVGiTvM$VV%~mi~7deZhGAuM>6TWZ+jYteGQJc_Th6iz3phW2+ilybgWnTJTAdER<+l0$u<84>S0b(_00~wF|Ky}sMp=rbA<W{_Z_zMBalCR)0PqU-C?iLuKJ|ZerT1!^D>9CHtMHh4fVf$E?{Nriu6&NuwI?;kB(RN&tu{9xr3e09n42z=;z-&r%3RP38Q9ezDbi{yuBHT^yj?MFB<H?czAUK{E|J;PtOn6>*d;a4EfX#(fc-MvEQ+;)wZPW6Im&mXnOmd&}co6;+@t1_Bo3^Z(sF|!gwxY^0|!hWj6enK=j|+FZH^Z?-s)M9oS!w6Fdz2cvoZL+jsTTbX$7i`Q51#@N1M^t?4Q~#yW7rWBC5zmR_foJ{b3wy@&6bI7UCeD}{M*O4>;MJlYfcHufF559}D1S$*SKdF&%CPlJ87#*N_jxG+NVZ}&#a@5ne^eJivF`pd(wT0hR0Ti}25Jj?oPAM){AfOXSvw={qI>1*o$Z_mY6d0<|T8H;(mzc>0txEK7)Kk9yrqrgY(PtMM|3g?OEZszul*l+7s3F*g{!}|c0hhYA#(F^;1e6Hu>b3My86X{(MxNjS=9s7i7BH=qm>$qaiHU#UggKyxkMnARIJFrd*&#u?W@EMPF_oIy1-(8qbedi*7JzvN909|h<_{P-|81K*D!Sm@kK1kntCgx>FBkU*iZ-De=%iz3Qw8480Jp<uyE~C!_tu{ZPzt<cI|C{HYW|eX9A9`Vai^-wuYG>hvIBx6vSZ}N<t@UHeACC0TGhm!)nI_iF&vA64{+-WMtc!B4Mm{MkYkFJDJ7`y#H^EPW`)FIq3Yw3RA{PFVJ{S*I)KlO7@woa4`(xIbtZu&5Z8g&SRz*H>m*ICFhH<Ql1Lfb53D2*hlj3>UkP)ai-?i9>cs>>NTrL*%Q(z1HZ=Nq3S@yy2I$!S}tzY|UJv%(kBmd5uP|i;CaJ~My3cpD-{{BKXC))ij<nzt*ZkOv7(q{?7^(xz2+lf6kH`d*}-?3fnvt9iP>(w`Yu<75qx|hMedX_UtAAAGPH!~E#^TB`a!%sR9^;UD=MzpW`cs}swZj9$C<1l}Y7^uGaqrdhS+lt~kU)b9$P~TYkm)4u>RM2iW-!CcV$txRCKLvk*zyGN|XLh7_VEyBLSN(6_AFyAs>9}PypNRG6@0B;}aV8B`-?_Dxo>#(q9nQCDH)wj#v?%}8+FBmR%_8s}6YyMa$pY+Ko~ow4(>@vF#`8M3ucH6$dlANl0ouNeRH3N187XxC$@+0O{AP8uUR{%FV%=i%+@#v>1LpbChjH8-so@XsL%nkU*1m0|`rp3q;reOQCS1?ym?ySh#Qoj9pv{`k<yE@>ZQI;m?<4FNe^lR`vJ&%Pn2B+<{zvt#jP3B=#@{n=+@sOD?lht*<GwB6Z|xt>&~v!|9@h1eer~;4$3s_xRQmkGsPhT)=e!wuT%&zf^=-f3(Dbfk?eP9Ut}00X&sIE7IZ;~MgDb!e|7I}OzadRA-}!HZpJb$t!;YE{wyU4A%2xGvc<VlmIj$YnvtD-im$ztoTgfZfS3kTNexd3*PP#5l$9`0bE%47L#dDRJQChFYxfIZozUn*27TJ;5x6fRo=jCv9(SGC{R|V-iMrl2nUW+w<+l?N~XX;SZHuLbj=zIwLH0?2O<o{F4X}%rH^o{}g`QjN|=X|T-7g~#Un(i{{IZZ75nk#U<>fSn`<$8G;{^DqDZ)UcQ$Mkch^jd$md0#K8zbC8KoAYT_^$q8=&f1O_F4J;4JaWP}QWV$pqlTfq+KQ`h<&DAf#ZvwBd>!vwB7LbI+Wt-RuM=+ml@A+Ge=)~!U4Gi0_<Ws>$7wyAFRs9!Gf3a>uxd9zf7tjE{^BqCUWO|s4&&6lSMbLVM!O!L1pD5TzrqiE(M$VL|CDGyZwlyfY@z8;4`)JA&s{<>AKbl&^Sc|4dh=U>>+jobyyRn_d=J-g$rkvI@Q#{))fPJLI?8Q@-}Z{OFW0!cS`W@FPWT-HFz%fRMZbUY3Vx5JmgZmKs<sPTwXg6iP8f{#xlilcvAQ1G`-Hc;-(mYX0QZZRgVi@i*V6T{GgA+(H}g?f_~z+;TF&83@LVawYUKA%Gi}fI2On|&xO+d+Pnk7D%TqoH*1_Jl;M;d-{zjZ1)*Vgm!w-Cg_kHS}-iGU$Py4Ykqp$8O*;kL$_UO1>PJKtc!x$fuB*XsXhXAB6S{v_Sy_taPTY4nMgZq(K?{-guaj@Tbr1u-G`{(w(Eimp_WiYNiPKoEir5(CHwB@S+zr$pGU&PFFLC0&`wg9|0w=7J{V>S!LeQIO}qz~Pp>5Z*L&|mw<sBh*B!MdtOcC2>_yg_>368gTQQT3hn14pg4cn*0W74jc9UCV8GPQ^Ol*)RH@pFK%_+^3}uhd;2B=3~WRf6IB`7RH-BEwumJ#^%@Knk`J+mv{9={_T5Xe`7*B^<6Rk+Rlyp715rqT*v)Kqn3DHdlKt4t4|WFj}}kE_?G_$o+~|Q4F6co3+hi?s@K=HKNj!7m1=VW*ZC>Nhg*4c{pFh0Me{K>pTqlaiz=z_2rIAc))8G%`-g30nEIw)E%dixGqgQB^5nz3(V_$1t4I~B*Vlf*M}0@tXL?@t!LRY0y?-(I!{gMqE>*@lC!{O#$(<kL{^uKdTyxGz^=)^nUqU~+hW8B~Jw*Bf9q^ow$2B|Iv_9-7Dr^3Z6{XQGC;OnDZoS8Q!wsim+;NTNK0#j{j~r1?FrRrZMLvJd)_iOyxG%SLh5C+1IdL6dw$gIALVm@5YQ%E(&nep9%pQNE-?VI_*Tt3T7{;}IUs0Y@Bk+FG*^ij#HaEce<!_|*?F_ns_8QOx{*4znpBUUXIbL*E-?nlm$~o(IytgpBx0`RQEU)Q}G@;mcDcwt->pQ&;V;m^4L48-T&Umk)2Ig_sva>kuwpffqn+M{2D__9-deK$z9JzA?++Xbe6ZzDcqsMiAd5HVL2cL1=v5oPbgwJ`+-w~Gq?^*jq=(@)qI3M}6%#ZuI^9@jr;7zFC(834MuCw8Mf18Z<lfEkQd3px#S(hq>_WE;e_|4;V{bzGD#6Cvjx~Qj>=e6D1%TGdk=-E+yN0y4ne@Jb#*D-eFvpu)2cWr$#?{o7DEynnM@i_L=J`99E*ttaO=hj=ar$%GZKJJ#qzJq^Ntyf#jETngA(tS~D{Rh<htuXl4N@HIj|8D(kPrDVqSCG!Lwl??hxxfx+_EC7A726Z_@bwUmoAnW%5Al5MD~=+42T$xb-0!3P)E0dL>&M{@wcR?0w%2y(>V6LC=N#4N0_Mso2NV0YN82>L8T(G#o2%9>q|Y0z`w6ZrPNcv53cm4=-p{xu9me}ekKUl1sdM4JD_;`aFL<WKco~!i>*j~Yu}-L&730b!1NS)@en!8UTvmO@pwAe`QsTWHSJxUyf4woD10|o2@ufr~>~~fvi1GI4x|n}=H%30YyJ<eo<&l`r?lea}(Vx)1*Ja1}zAOa$+_wDs{=2nkz2<NAnuUB)meYLfnTFsw#rj1!uM|0Se72gUz&t%568Ue)js1~k`Egzo@xD?*J2!SVM)`{!MEU(ab^bNmHp2Y9^AOT6DT((cFDyX2op2k+O@0;Q_IMxcLq3f|KEHbEIB(@nh4IFCiSo>Tk9_?PqhG|lNB+hveUH=rneXxD_QL*3#q4_D>o6Xn|NfN``{iNPa9>fXF6P++xiP+GDyi+(@iq&_&42=K>FsM#&sI<cq+gpwpXa)M-FP6eZ}s-WIyE3C%G0(X^4UH@+mD%ZG=4|0s5$o6D}6<O+!}~>-mpE7yA1DZMq~aqr*_40r_a-U2YWs21KWIi!vEzC)}6sk&`+C%!1wx2-*<MkUyXK967OZ0L6O?t9Ffn_uHw7DYU?DpkJuH2dXHabX!>G*XnNP7mAGDoBayy-8r_Gt&8dygIijJjx@*6-x6R6Y_amP%_`QwG>juWpI|uOn#!+|<88{fv->oC4heK<zKEAaI>#z*hk^aOTz0Wrr;Js_dvwO%t`XkbZ*221E!~>+y$oKp@p2Ya(dJ8|z0{q@(_#c=*mgDz5W<&(qVev4O^J!Y_SH(WX_0F;u{i8&Fq@U=i^P1~;KJ=Fqh4378>T3Kx<Pq1;=_(<g;n^^sT^Ww`M8_&fKmWA$U$c)l@_p!!=X(p+;J$IT6aD=d-XAv>-PiXJ?1hGEJ=l}BfFF}Vf8Sug>5qDx*%J9#nUA6z<uN|g=!o)sK8W?BGdrGl90<X2OKih)lw?IPo=+Ny^z}FDcwzsF-z!-Gqj20d-LVhi`5b?LWi<SX!^deoXDEXGv>&FxpMC|uXNY`-{^N^%L1!`_?H4w$>6pJ(&c$&buEg`^($_GKybeb`W>4KewQ^cmXN5)}eR=c`v*blQ7nmQ3^s&F`y4E%0IlkYt75;#Y*ax`Mg@3;t{==QPk1oFm<-5ESe&t|1XRUu2`z=d$;rl0k_`Zb?=9}w>@cH&$tlLM%;B(efI8HqW)`OR3qJ6f$3BTJ`j3fK5qd$f`f}h>Qy6RvFjGG@GBfqDQe$x6(-529Zrx)=3-@^9}#C}fjN8~fLJ+5mtv`c$LQoKLaFf+!Z-=a`IXEVWXR}TGQG=9Hktj&h^3j1FOML$P-vEJl>zc>Q#3CzBFB(ZOedWiez*a;}dW<1X~+NaR<jNOiO&I%=v{+faL>C|fY-er(}<6%6%{r)8Ut>xh_YmR->sF`TLzg2->G6U}S8oomPL|2C&ofPZ-kCoMTtgH)v$y@B3K8QY2J<#pfkD={u{x!I8{7Nf6QW}|!?!k$E`Y5LSOVI!Mr;k0${a^j`v0~XW|Gz(d+!<enUGZ^|`U_d~30X9S2Us*WSwi?v10ftoEk+hCLzWPJZ6Jh`@%sv7(dy)6<SYzfUxsi)hHwbgP8J<a79B?(MV&+)M;4t%o<yF_5MEAQKo*T4FDI{I2(P6&$f66$YspI)!c(b}$)erJQ^|c8!uc7(c^JYusGZ58?Z`REnHj>~)HY<%=45YjDu!@UY7??(eR5LrCj%k;o?4GA8bFp1HW<R`sV&H&?aArM*%`vQs9ngS9m%=K*%-pfsm;iuHOa}zFARk6HEL<HXeP3R@NoknyodVA0E_-k-b3ER5MD*SOcuRFUPWHX5RRl?CyV|@jwG*P2(P8yAdCJ%UQ1rb5Z*w&Ll*suyn(!tA-tJ-mn?dZyqUa>A-tO*{G1_NzyoUY0E<>47a)Jn5UxdSL>BEpu0?Lj5bi`BL>3)M?nLg-5FSpo$kXFvN__mp5DsMs52H>Xi;gD`Bll$p2UEw8MF*0D$w3U^D%3!-XbEx^a!!WuDFY$=tAP+cMomc;ePn<og!eIo4^ZEcMbmnK50H--2;rmD3}n$XWC`KJ210m0^@9NxeMsI<-pUXTr=BH?Mw7$I3mC$)7{bdK!ZFk<WYK@fG2}B0VHdTa2UxT`Swi@ufe_Bi@9UC9e<0^2mt+Y0QM-~we<b^n%Q1v2QhSg^dyy-WD>H=ssXfV}y~+M$lObG<+L|odl3a~kH9j)NhgW>0rh1Y^KO5lG<Rl&l;kO3#4O#Rh`7QYwL-;=RDOvOZ`9Aq3L-+#q7FqN>`2zVgL--)|XR_#a@<H+zhHwPcK^9$1jvy~$2+yO=CyUM?&m&J~2v24RPhkj8qs}FZE+kJQ&twSCrY<Lot{~4QhcSegQg@O?FOrv%S2Kj8sDF}0<H%9u9Sq^U)YoKDS?BHLXJNS?IYd4|%|aISB})jOGZ4bJ4TNx6hHzVIL$YWHIbmHWJcK%tI*Kehi9C@!mm$1@I-4xIoV<d(ks-W|x`r&emb{I;g(19}x|A$BmAslfgCRVC+J`KfpFDu<!w{ZiAcQ9x2;m9TJY>-vWC`K%210loH8WY%n=Bzb#y|*<q^2T^CM8P<4>J(LL#VR86c&9?9zq_>5FSdE_2p1%da{J@a04Mcikh7)nu{zUJk~%6Thwf1(d1+a;ZOr1Jc26gOJUJ#<PqdS4B-LP<7Cl2<N@UV4B>v%O=Qtk<bLG74B<Z1m1NOKavyRphHy{n8nWnGa!>M)4B_t7b!5>E<nH9I4B;-+jbzcy<Syi3hHxk9HnQk$awl>JhHyKEu#+MDh5DQ<D(lWK{489GAzXv{Jz2CCxdyp0L%0>SDOt1=xfQuPLwGQ?KUs7*c`$hd<0pEep=8lviP8^Cl>aauQ?xHxG&oUtf)kZLnCB!KL>8@*=zOars-G&XH_@DA(No5M^?52${hvy7U4+{(gj-X8C5s*-w<fn_2)Cf_Ba0p&w;(rX2nSJ*kVTJ@gUEpl;ilBXWYPWPrsO6J;l|XhWYKVPV{!mPxFK}`S#%b;A-O(7xB)|WDnob<bs1SShCGM7gdx11dWJ0OBCjXMGK5c3KaxddU3-$Bg|8Y2;m6dHWKln|gz(=6LfC`fmm`Z-Bzut4F@&>HE0ab2$yv$y7{Z09CRwx^xe&Q1L%2A#Dp}UOsmaC33F%Wa578uKQCZg}<S(319^tIiXJpa)#((7(PB>p-59&>_=mq1y`nh2ISDzPH$D*gnq6dxt>i?ke-}O4kYbd&fEE-|_cYPxgwTB3{5z$3t(Rqp5&%8wKZ64d8=ybB^<V5Xra-#M;IZ-<oZp097Mx8<yokng(Zp9F8OPxs;olR~_ZqE?zNDU*4E+uy)cV-CNsjJDNQDi&$2ZnGr>JGB#UUD~b4~B4W>LIe|336|82t#-v^&DCBHhCa<G(-3&hVWO0a03shtfz%V+maL3&BFcSV{Cj3jgLC<Q9C}0FoX*;guf$;%DtmkeEyz>Y??!pk(2Rr5{9t+^WyjE;v*@)^Pn2!%=|tRH7z+QzfVC;P8Ll?PC-u15Khk!PQ&~qzuXMrT=9{S=`v8$kP9=N4>cD#Bfrl^%}N%{LC!|b$q=?Ng!3_f$*(*^xLkY`WV-LD`N%byt_HOnxgftU$`CF_7A+kgb>pL6eAJGQiuAsxmL!`@SDjj$T#?^bXC$Pp6dxtxqY6XVpCMe9AzUOrvd4#ad}N7_s`UIA!oJk}WYIiiUveRaZ~^8i`Q>FklCCmCxC}$MIJFSD9_z18e3W8+mF9WNceSW>$ffvw1x9JsO>KUkP(Q-e7!~MMU|L~m+tL@(@|xD*aURDv?hNrA;te$yS+o#YLfC^L>_sg>7A;NoBBx;pXQWmji&i9OB<ElV=cQI9i<;!T<opcb@2EA%qBY6ik$o7#1*z4@qLs-7$@v(<*{S8oqNT{$$(b0!>8VA@qIt;a$tf9m5(X}ET83~|hHx>4a9L_ma#0?yEJL^oL%0sL9Jw6Nrw&87Aw#$cwHmn^>#GSvxH&_(1+@mb2Cqj8hHx{6a3HlRxhk)BAVatjL%2S*0$H>)xjwlrL%2G%1X;8YxjOlKhOi$s7g;m|*^gYDAzYZ6nk<@}T$pTQ2<N0GA&Y+W0OurUNrDhgM}0vSy-$`9PLTv5{E6THK^Fau{D~aL5dMpLg)DlW{1^EaL--m)_!oxoeunT7hVXIf74j7x?>IyF3`6)=>L27kcs{=}gfB3JFHv8RML&`+k*_m^Z&0P)Z%~tyC4^lb2;qCw)a2B>-uF08%D8!tA$*nkhJ2O$J45(3RmRZUR4=lG@Es3?@Lg&evS>!Kgzy6ogz!^p4zg%ovV`#89th!g)cj=8@5mCu|9BvTzfyh3q6Ntk!k;}5!tbg1$fDWF62fmi5W=sinaHB)$r8e^JP^XqsVT{#23bP*i3dXXp$9_vnFm7n12rvKG%Hy`I4MIo8ACWTL)e#Ej4WD~>`N}g5Uxb6LKdw<u0*cI5N<$iNEU5EZa{9z5N=6rP8MxJZb@#<5N<_nMivbuw;~5Igd0;Ekwxp18<PVV!u6<i$)eTC^~kju!v56n$)bK_e{y+-a7k)$vS?v)NpcZ}Z~>}~ESi&CfSj8loQ;}=ESip-jqJ@3PDM>Y7L~C$6+a7mCP4^)@qosWMgJmyA-`k@Kce0ui(Vr?BLB${zR3{2%n&|J{e>*LpM09Un;|@lAv}j6yo7p$EP9;0guId=yqS82Ecz>XGdYGKe2{v9EP9E2kbIOOe2RLVEP8`{ihPzKe2(fOi{2xjBVVLmC2x<9o$;}r8bub}L>7%CZ=kNCMv~{n$ISQ$qs}LbE+U7K7c+#zsmsXAm|r+Gk{ro$gfoQKF@&QT!n+v4d#O?6D4yqDhVUVV@L}o!@`?C386Q7WkCBh@`=6-?$WCf3^#J(*^Npo$C-0-~pl&B`XZ`L-RPVxjs9UKU$QxK+!hr!ENirw>KmB(F|NWD9KMc43yx`lvbbr+^@n3$4&+Fe8{{jP&$-YAT9F#;K+HA4Qr~d^9&C;v'

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
