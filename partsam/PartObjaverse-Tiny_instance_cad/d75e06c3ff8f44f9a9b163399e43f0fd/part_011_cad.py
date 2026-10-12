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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_011.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_011.stl', 'source_sha256': 'c2813620f7a3eb6c35e9c6cbdd82def438be362b5c7cf7814ef2d51443054ed4', 'input_faces': 1530, 'input_vertices': 825, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.278508722782135, -0.4999999403953552, -0.1951359659433365], [0.278508722782135, 0.4417187571525574, 0.19409297406673431]]}
GEOMETRY_BASE85 = 'c$}r3dH9UgANOzbMfj3^--cw#PS%P+l<d1u#ul<<-{rOw*|)5tv`DEaDrAr)yDV9vLDm#ngkS2JbI$9`@)>_T*Ymip&-H%I`+Mfx=X}n&&wXa*p3$^HQp#+O`B%u<)Um|ElZ_llMS3TjGo;&qK|Q;48(5}qzu_sIOxjoftj=xRs!`JyQ#eDMk;S@p8`xz)vFhGpPrp*NSSfF@S6&-1Xh5gF9bX&JwVU$mb?QB^Ti74iqf@_b;m5_RR;X0UTd_nb?`ZG;<G*y_Cirq3J+d{d?wMXElzI=G{9x-t{J^^nKB%eGxAd@j9L#p&sQx?Ut?%OdDDR#sd`Or7@4uh4R=U4uYm6VT{<*We9_ITtuX(5+Y%*qhtnb5jQ+L>2^C7-(L!Vs_^WD$qJ=71SJ-H{=4-A`jTB%bxzWuKCe~NFv^<B~aNcpDm?f2t{8m#*0VZOWH<T=t#eBXQVdA7d4P34bbeXlJq@?(8R<R?;I<j48}kso(Wl~WJPkKg(tKh~G|iIf-l@marNe15DS5c%=qdqsY%?-TiPtS|CoeVLy~d66IMC*)`JXXgBp^T+yf{@@2>er$P}AAG;e5599i<Oe?}&Qt4$T8sSH<I4Ql@?VJj*zz(z_^!xL(5^osKM`N#$NDlqk@6xxb{%s?eykr9{q@;;<a&ZH`x_}Q*AshO(ch3=Cq;iFzUZ&@gR;N2yy&m>L$bg4e$ij+JEFgSdtA|9>pP;q*7uA4I#V0%)Z-=k8}UVdt?%6;`a6a4vcLHL#-hLY&Y}4EZ~fpqV*SJqwG{Kg9ygVk|Ms|Y{@e2F=RMSSWPWl@SgVgK^J9IPAAG;akCT(~B0tvmH;K=Wlf(GV;rRSmKlpZhew^&o-$JYp_<ot6Y{vJ>{NVd#e(-~7On!VPlK1P!V*g-$xqpzp-9IFhXa8V*xqpzp-9IFhXZ}my?jIt@75fM4%l&}$<@H+n0a3ra{#svNf2Hq={K)HXq+jCtD}8(YjkHr-f2D7)zt)%6U+Fs{|ML1P{e=98>u;pIxE@93o46iD`YYCR>&x{#l25T7Mvg1i!-y}|hlnrMhXh}YuUsD@zE~fmZ`X&2FV+X?+w~#hi}gYJc72HWVttUlT_2=x*N4E&gZuPju|8N|t`E|;>qA0$)(7j$^+Eb}eMl(J{FJ_3A0o#U>x1>>`e1#zK1e?x>X++-_2v2?eOKg1t`CuZiS<GHc72GnQ>+itx9fxT<@z9fN913w57JM_k60ff<;D6CnQvl!i1b&i57w9KLnNPKeTW=atPc@itPc@itPcsk7+-mQN#CAdq3{3P^RV;F`ttmezCFJZ%5#1t_{*w%8SDG)`BL|fjj`>K=cDxP`Iu0i`5=9JK1SLj&PVIZ^HKV~<)Z!Kb-ncM>-q$LS*yUqe4l$~d8}_=?|ZXuSX%QTzVqv>6%X_6`v%gt?;9leBL8yzk$ynrQ?5Ueeu?!*`mUHia{Y<46W=fLFV`jM2SolOzR17zgChTSy$WQB&%gD9H{$az*FEX`ME)b|n8?3e52f#j`7hT)=_ibrSPvuR#d;W7AH;eX$(vXYtuNQZ$oPu&Fmhb69!7kz9!7kz9wzu=zRC4a`jOWoy(jI^kLBwT{Djvd!jHTjk>%~{5$UrYT3@b*)=zl-BK*kf7g^r!pM@XUpY%HZjc$+JpWw^)KcyepKgjZS{~&z3ep+9yKh{s!{|G;_ACTqken9vE(cgsq5`MydN%*qA3Hv46FR@-p->yH>x9d-&{bK!*zFmK;FV~X<U*t1ke<jO{d?xI#Y(C}w%9fY=EBu80mCb|PU*RY0uWbJ1{>mO#?ysyb_gB`J`zz^-`H--`624teyziIQ<Lr$5c87W#Ty%b_J|BCgGk%k`+qD1m$;om4p<TMXugTg;N<-UHY2R(O!_@P0wl}r^$hH;QKk%8ZCv<Do1f|ZG8;yVDLsS2h<Y`LXy-V=V>{O5a&6~ZU|K7OS3Nv1(wC|=apxfg(&&QWvK0zPX&0NZqzqi}8bJO+lx}E{KP5B2w)6SDSXX^5m{?zl@sZ(XE_RH+m?F`I6uYGsW2Gjly=f~>f{(aE+qdzeIsLlGg!JYwA&!yVBp3sE_rhMLo#{Z+Vsei-+-TvU&{-&N1KbZCpXs3@Ge5Ru*|Nd$1`@YLFOV`(_m?>ZK#%}%i(3mOu?^k|Yrv33(j6c5NMC~s;x-2#i{%X0$#rp1;-*ow4-t{{F!Mj0I{>P@eo&K}?M#uW@>Th&CftR=I_Bid<n(_@wnEv)%tH;aDJJpoWx5?z^bVk?YX~?qJyg405>iqjWrA$4Q^KR0|ZG2Og4|K_G{Ev>BalbW1x8E83V5zRB#YvO5>i1{G`p%S)$-_-k-ko&b_@zqd`a?CBjg0eG-!$bjcAcU7TjiwjFK0IGSzOqROY%Z<+;e|_r~Ql7be`SUdzkXaUe<YVPZb}b+Y@SK{1qilewy}~uKigJO+6QG>3ZCSsm-|5s$=|#|7brnyPY0i|Ltl^<Hj*%M?J6n**(VJ|CDZLAYYCly1v0TmuP?SH|G4BcKCIzMK2rwnGCwTJL9N6f1UrWGXBQXIuB0YjXM9n^i#F(w))lh!!zqV2eync<x?Kg`FFlKsM{0lGsO5;u6<|nHAx@WU#^+)KYgHm?<CIml$ne_ERESuyx(`YeqOf+i}i6|@$A>-zOAO~51c%xeP`&aW`2HhYM3rRWvB6X<TCZVP<o(lSM|-tFaF;K?bkd$M*G*-8Nb&3efsh3^rQ6Om#j8^&W0wREfx*X$7v8SKI@+QmKiVWyH(SecJ|}^{piibvGd36H%E_S@Ng^Rf4kMp{~`Bvd)z<rn|ijLH~C4rXy#9=WK;gqF*83;n)ArF;qF^;`RuV*&#OSr%f|0i((KoFEa(;MyOZ|m@$$A9qT3(b{iE^o{;u;7O0#B&8Rw&>9{0Y^TX60Y)898X8h?5^-QQr>WOH38)XdbgB;7$>kGF^($3TTjru=~Zap#5auZ+g;+`;6hME(A{{&!Owe~3rd<4oP6^B+w8=OXR*$z=TD-OM=lIB)#U_t)ui{ZIAN_1{=v{EySE*X>z<sjEKDvNw(Y&2OfBTHnw(->ISV=H1*>mk%_WVEkKWbe^44bBD+IcdnWFlPZm#Z=rujEQ+0Pf$V+E_3o4Y+IPDj(c|bnxXO%UrjEw%oL1-4SAVabC(ihCrk-N=4(RsP+W4w&Z{1|$|B_YbA(*L|SvN**T&Vqq`E`E-yXv&mI(>=pd)?6e_5QwcRIKmok@m2zXY`o9I{!_EnDU=?i<|#Je>?5F!IZkZ|G+<;bbSMAn0lI}H}&KlJ6N};-h&0Yo(7F|K7-xY>GFa1uWR2Oa8l>fw`a?USl{{I1v3v%f2rp~sO@=EKE-XFhrlPBy6ES9ebAKmo&8vs8=BwLzi-`w*!+a&na;mkV}kL^+|%V<Z>?Hde;Z-^`#ZJoD<0?*=jV2Gznr}p8teY1=xF@wWp$q2lNGAz=Y7`7_?aHn<=qL3bidpzb&Q|ow$8tM)||io)j!Txe(=}yNA&ZjnDO%MU!{GgcY(F~xP=ea*Zm*8#Q62n95LtJ`f}PYJ;(UXx9RqKpKdcq=VQhg<Dabjj#B@U8O^rF`0j~}x}MOKjIZe92D+H?odZVQdEK_g`b*lxofmGicE%t5lO8YM&I@{;gw{Q0{M6U=c=_9#aq(rVWR9Eu?jhZ;1`jgnemtJrlwY@6Yv_k^{dHcBXN>cM0n>hGa%$sm-ubR>NB4pyYsUIE|BZ6!>rQC(!Fk%R<kREjoOCklezf1Iec$pVod;*u8*TOD<jtnM=d7uJK;_oD-J91LKi_)o`x^e+LI1t?>Uptw4t+Cch|)m5fcAs)Gn@MRJge8G(18VU<=vfCD(Ln!Z)kj{rXF{{cVK%xZb@~F9}EuC^{0P9kBfhOHQKq}^xOGzNSx1n_NF?n*SBD{VsYhtpK{zG*-ReJW&B>Z^F;bqx?Pj+&W$~;Z+WsFmr&K4#=mt*`~I)*HC5_e{3HHdogXLNPiFqSa8&#5zGPj$x9Ff(w159QQ$AmdCAz<TSL)*i)&z~ef3>bBc&B#HnlZkwLsrwyRR;=bzx_s2|CGymzJ;pw*Xx6`WtFKX^KCufyiLsc;y*aW__HeMeNXVIPM!5QjTvM74#RYNoGZ(^$NKKH|Ma{Ho$__je%T?We7P#RygOxgS*^b}HGcUD=DhQ?AF(yYxAVcjX{f$l1Y6XIEAPv3t67|XxSejN+pElLI{!(PjNdks_Pynr){FBe)@PoZb;;e8F>buvZDxLkhNd=tkw<hsgKo2a+AsECj`n@YgLU~OW}f(~oi~19r#T;!Ouwuj%#&T$<Lm8dt?OHSFs{6l+4Rf%(K_SbYNzM9`*Rz=e*QNLjK6f5&S&t9SqHq{3C5pQ#N>I7`(n*l|6I2B^gPJ?cpu%~@;!_{WUZb*{$~rC^KMQn<M-=h#{H!Nx__bC4UM1c7qgGgvh~@TF@CU1)}y*#i%tHW?%A~O&iU1>W5d4qw}#T3$)=uW8Fl&K%^tdb|FFBWbv+sW(euY!#+(-szhMqt-hb@4o>$&qzSF)hbCS+yDD8&>_3;{RoE<w)0;N728Rz#ar;q2|TS<>g=;Kw!zcoVp!E_Uw>-t_=GCOv>oTJ_K`s|<koGCx!yjh1!oB9LK)-e9b?dCi!cyCaw@2in)`g_3~*Lknx?AY=0A2HW!r*&cNyUDpse}5d>QnxpCZjRf>%m>!JV6F$Vw4cV+;}z(%ZJ74={9*iIC(U@h)w-?D>xk>dFH%a+hfud2X1unI(7x|lj$^vq^}ulL_wR4YH@R=F7fq&_^SWX~?YqStvtHdhs{8AmU(NWvvg&%AEXBv@alBJh`@ti*wI57T)0}7T<u~<DEv?7PTiYEG=QA$8vL?@=N0LoFB_GlGaeB`fZH~KdW^CSqb;kH~xzp{n?~Hn&$ID;G)bD$yzVY{*Gv`bF=k@s>-2U$jt!*=!c3!wLR@ZxJ*NoUayZg*I2I_up{D1P8@=MM9_kFO^`1z{Gop*t|OW)Lg@A<D@-vady>3JI%*<Aa<zIl%8dU`C=$Mv17Y5dwLb-&!!U%syEO_4_XPT;!EkCV!*Gr=7frfZ#;Q`h5cd1`|0_oOY_ciZIGzPHG~I&bdf54G>qOV;goCyyPkANTf8kL{N`CQDD<p4-`tpY3YgJa^xkJI$P5X5H{Fy{zY<uR~ws56r5M>$^8<l72j<vi9Av1+?#eI#SQKVEQ(1XdUl~8{bgND^vCJUP@!;=a?M2UxA$4jX$-(34L78)rtDJFE!V`uTnnk`@R}DMc1>nruN;xGV0?7oRo3CbJlC>`K9l8llQ;$-`yJ~Z^0kUbs;$a)@1E(%%#f*zL=@o?X=#f{b2t>+IMd>*W(xpKBj%&^3=Nh{$le?o_ns;`EXZe(DnP<PSVE<G=A3j2Oj%D*I(~b-M-+0W4eFAgV{~}1yfFs_1)oxba|iG_`ZAFjQ@8L?K=nRn|6P-bYg5f1NATH^E6n0i_UAXS=AqPe_LPFkKNuAjsJK-T~9EdcZNAH{o40Ue_Z>aKE8>uesE4@Q_r!?<70jI-Rj!+J@vNkXK2tZlkW@3apU66Z^pr$@r*9-)-Iv_;F$I%e<QQ%_6M`QW%BUT^W$TW>y#U2&ZBPsj??9{lsKvL{7nv%pO0r~KlpS$)Bbv|&5ZS(tHpHr!2LG5zix(6ru=)R9(TfVJucqEt;faYIauemX-9UmemLoCnfCl%+RVR`+q54nR>kzo9q4M`YvzknqNuJv)S;MJmoJtY8++Vf=i6qU?Kz~M=i8k5ggM_$znl_Vj6bdN8SQ_bMjtnn$?uwRuBv_a=nXS(`!_P>J5|!YZ%z?Yf5qa)zn0tdYx(V&asDr5PU&|3aabQWG&j5U!waqMmp9!s)87gU#+dWNl=t7dVb<B-`^EWgo40j)+y`gOI`?XklO}Hm&GlgXY~wGluG{I&WyalCr}yiz;~S`I=9Tq*`=8Y11C556^I=aR?YoOBp4Ro(-EY>Tx!ujWSoTTduR3nl-?p{2AM95_`=Lv$JGt|Zj%~j)wTBt6bAON0^=vDx{lM|VX5KzFMf<@5b>rrPZ_s#see-S2W%7J^teJ<^Ue<o__S2^QyO)`D|Ld%#{EL-zdjeNY`H0UrI?D&@^UWFao4G!mDR0`JWX`YP)ECY5c1>Y3-|}ZN`<|97hR3$wJ(Sw)V@|i!zOR(=gIC`(>q)syL$&^9+7rCq%3P=ans5A1Ynb+o%V4gH8~Pc)o@tN&^BZQpJMx*i-j6M0+EeSK8TWj(jlZyzY0nz7uW|=`VD^3EE1To)dUIBsf4Zib=iNUwc`J}k@0Wd^QgQuq29$g)uAb^0bv^#PFMp*Ui_ej*FF!|?zWp3Ip*)`>TVH-IEPeaAa6)-L*OR{eTsU%E@wu?|<>$iEcSZZ<=fc*PpYuxJ5$%_s^GZJ;+AlxnwZ8nESNgL3@^fD6%g<G%FWWCaSCxK3`^D#~k@Dhm)yRAkpQ}d3SA4E&efha+q`%^G)yQ$h=c*B3e6AYt#pkLCzR17)Tvht^b5%Fn+3gQIzpS6|y))rQzIP_e+wYx8pZhedFYnW^e!}<Egdh2ynk;X>XCeH^_tb2A<oDF@6TWvQe0$$Tq<(SVh4mA@M<)D$XiviT!fbxz_riqliu@;hFU+=6+(#jOdmn}L?R^xH_KW){q;Kz|u)e&HBEc8=N%$U_EHB14;d^8@pYnTTw!Hjam7V|cdsQ|M@_R}63ExYy`Iq18vB#C)>#@H4o{RP6_gthe=0n2wM1&tX-!~=ie(3p*pK!hlKXSgy^7ed}zCGXZ6V7-1g!5hak@H=axAQ^x_I&r&E%VU+T3_~8`nJCb<>_yNPk*g1`)hsKU+LTaCX}bY(zpE$j%cvwVg0qf?634~e-p~n-vpojT3`0p`m(>$xBX2hPk*H!x$o|iN_(}+`|j`)?w7+)xL*!G;XXH8kG#(fKjA(%;YaRsljZGwZni!0J~!b<?sF4<<UTjsetDmp@FVxR;V0bZCVhLKoA4v|xykbOJ~!bf<Wt_~X3NX_-0&0bbF+Dn_qpLG+~;QVFYj}+$CdZFSzq4gW_@{|oAkweNVv~U_;!5`ZtC~Y`D}eTpRF(Fv-RbCj?^ROv-RbCmcE_O3FVp3k@krBEPXqlrElkRr2S$(OW)3C>&y9^;M?^__;x-gl(*}T@MS)Op*zQ8=Vzo}_^v4LE5Gca<%8vxJ+!=g<@xV*K1F#4-zUmDrT2cN%gOR3jUN*8&3>=V3B-?A<a=!^<HyVT?&SFKvVJHze!L>}To&WS_uT?@#CSb<@ohcMRYd!(ABvx!)(>o1^HAU0EPj4ERq<1a`G6n#T+9bse*L_M`mWtymG8d)Vdt;)6MhFn_>uj*EN}Po!jHTj!I$5Qk-q(2jP>RBVx(`s7bE@1>mB@r*E_<G?B`{9yMGgYWIu2FD_<Yke#zHI!k76>cztC1C0`#2KOpj%@cPKMU%oyPe&qELe!}Y`>5F_OygriUMLrW=AKCWX>#Xdr{T+<uqQAEMSkYhmyB3*6e{DUozxKK>`Wvv<anYX0@9l{8M1GIrm-zbqw!ElcuFna+m_ODJi1`yKFXxZ-#duji@;ex^ycjQey@>eYdXeCZ_FG@JKT=+_Kg4xMw%=ZlWc#fz+b^$Q5#Rnkh8W+-?<2|awZEGo#@G6xXXD3LULO;Dx!&T3<oaOCi~QK@Y$%mDAMpbsKauk5=RMT-$^5X-bXSP^Z}*=8kss?{73(v;SL8?T2NHadAM5+Ji0e@)%FF8!`wCa)2j3_2W6R6@i2X^#7yFZlFZL(WxBC<6+x<yGJ(tCLCH5x~U+hm3{E*0}*q<bnZzkrO*q=z>?oSfR%Y4fH$s5xS$Ic)BMDini=TVa%U-fB6V$W0mI8)yGk@J-GU;Q4M_U-QualMd!P?c{Q_p5L@zPNdy>hs|iha;_%&3UC$%um88Q+Ee__)o(1eDeS5C*jIhs#xy-?>FJnWlVCM|9QgO5wvQO;Y#7C5{^gF`yRup@0G%lgr<O#U=QlR9=HbjWDJ+!vC`sjeV+3?S_4*fKEd;z;5iO$D9PVT@;AjV(5CvR2X5e)KD>Y?!4>Iq9`sQ-Z#Yzro<u9dRVY`Ls1)-zr4?iHsJJ+PD~48t)pPH7OnplKf=h7h;^>pG8l%4%C#82_^&Iuw`_%C#T#RECMf1R8!hP-)j@Qvw;n(5OXiwOdchTOk3y($nz+>TYXkU07JRW@w9uH4I`@tu|eK;PDwdlw2N8vaejy32ZxNNv@PlV&B$LK+i;qSunc=+-6Xc<_A;v-=#nPloIg&u}gC@zg2fsgQ9#TCL)KFPFKh2rCAIar0_V`y2pEbTo;+f-YNqI+Q#dl^rq`(PD{i=+Et6^cus2VfNk$c@s2aNBUM+mQ1K@OZR!%ow$143)Nu8Pisbxzd&~bD$-2WDME@Z3#abK3Sg&w;?0?JgnODVoZA!Pej|n6X8jYd5)^<JavW~!zvW7K|h4oz?0EQ@MO3>+74E8>ow-xM{qxn>4WN9bM$q%Iou2#4L5_E5{gHmtKm`b2k1}m2k<#GLkh#^;Pfes*7F!n57+e=?FaXx{dGB))HyW(?GF!tpGWQ3sN8xOE2U5IH|wh$4<L8T(GTI}@G&$5D^<@`tQPNT;rddb)nOIYIi}L5V3oI?<Vop#cs2YJx)c5hR(VqTH>^Uj%9GN{<V;0na`riE!UFUocmdoF?FaYcxr!%|mx*Zqm^s{^Ij+>MdyB&HmSfh`-f$muG2934i!Oot!gd{1x)fakFNMD+6dy(x!-wHR=v(k1crUsL-V1*hj@{@&bP>D|?uGV-)wuuem@!vc-eXwJxo24uR47hHYr`rOr$v3R3dN70HDDErQ=w18DikN7Pr^$7at!|%=Ih}&i~a(ih0mck;B)X#=&$fkaEMU+8*6dCr080mkL$nEOmJQ}Bl?fWa7I||5tQDA{|En#{s#ZXasMV1-$8G{ci_L!U*NysKhf)OQT7;*6N+=AkHWd(45-?tWZ<#ldmf{I!uQ}m(ChFY@HO;DSm_z~NO;`-3&%n9U-%$=0DS--fcK;S!298S=>On-@E-I&Y>(C1V?uE!PxM%dRVem*qQ_FKLUBh=^jL~jD1O-!J(gk>ieEzS!Ad)L46D7zR*zZZ?V8;U?GJZ@SE3)oAM;$rYTZ-o;1To-_z3(xy1^6OUn%|$-3WgN??u0a_rm+oui$;~e)Ma2KYRe)1RsD8qMPA^@KJONd=x%LUsb-oL65=5D5JP*I0E5V5sro7XdjM6jP-KHR_QWNbgY*#wn~?JqGP?3u~oXn6CLX%jIGkep6FOFW=xg71-}G$Ko`M_Xj=!g3fuv%ir#e$SB2HwQMwD>!+hKAMCaIUbQi320lXVt$oj7IRdfOTD%_J$JRjW!&xd!Scj2Az->B-t-#k`anSQm0E5q&3g>XAqUBf>|zd#qlU%(sCMeqiABl;G+5&jZg41WoKg)V`=g1<(W!e7Ii&}Hx@cr&^jUe0{nOsrtOu3)ZiArz}QycJ!E2H=%&H?*rKx;`j=icqZfVs@X_1?>uV<=9=&<*?Guu)6Lab<F<G!#?jAkClInP`n&n=0x|CiU$yi?H)?$QgoRU-Sa5^9z6;xRqarG1n)mo`TwD+y^6cge#L4JUB?sMZ!1oR)`C?iPJ`BjRVYr4J_D;zoD!`Bt5AH$F<Kf{dc!fS&c~aa%Sy|63|qegeoK$xjbWZ0j!y{1)6j14G`M3p9zipr-C(<aQ@K&vhVgwV%v05MictJUIM$*cqf_CJ;g1N#Q_z>-DR75yq(oDpFTttc)ac7_YWNZ2W%}_l?dV9nLBDNVZ64N=r_15^G#r=EPvA@N&*)nCXZRxeF?<oefPMtu;uts4OYlwjH}q%tH~3fdBK#|S1HAx$NxN^Mm*LOCu`V3j9CI!xwXYErZ%5a`v%)bi92*G5-=YEdTlfU}Hhcm;iLQcA!l%RWBl;e?3VshBK`0)Ez6}q9hoAv?2s{X#2M>aKptIl}a9797xAcygYw7Vi5Q?Xuvz+K$oyEA$B1d*^Z(uwwz&Fru;T!NB^aOkdR_nnD@@3Zt#i`NLPINs{oF+vyr*{2OoQ}0C9q%Wk!?*7(DE<I_&xyVlp?DNJ!im0jq1e8^q4-&J82l_;9UTH!hs&XZ;Bs&gv<F-S&V_b`yD~P4)qBDP9rM1h(gN@ka0xU&TmmjmD9#s-OlW2_Kb#rPf);?Yz**6Pa8@`Qq1cO-guQSnv=Uqju8h`%E5kmt0qlbtI_CW}rESm#a2vQa`U2b<ZiUu|Tfr^S=i!!c3qtX8Xbt!|_!;y`_!+n&S{$wj7en*G#o)X#W0M!n2&=V8tx<E(>F^x*71R&E0%t?h!0LbQsTGdKgyPz06}UEB6)g={h0CCY;4*OGaO6O<qlI8~{Is+oEnYUXkQ1FhioIxQCpv!=mqM#J(fOmeGFr=t&L71-w2>2?KZ;}L&x>dy_(ixK+8AyJw<i=gL2JWJ;5ukkxDH$mEdy7B%c6zhvhZUuIem;!oRd(TOeju=W{0zrYsGcL@l-hK5sIHi%fnB@70}1w3UE<0H(V6XgJyv9z>hj+Pom~<YV=Vjx^GdO3eDg|_c@AF5{lEKx#9G1F7$CY7hD7_??l&C#pTeaoaj2NxH?+biLTp<)w<pkZHCr$qVIbvZjRP-qVJO{w(ExC=g_B}=(?f!8MJ~ET{je0M2kAnbwhD6G>;QqHx%bZAB7)vqU%QIaC8dC4D?NS2K+g?9{wD@PAI+>jw|7~>X`l1XYe}o8hnlN>j=fu(Kq4gupjLN`{6W%;<RXII4!K^b28cm?F@H;XQDIUneZ3r=kOQsFX(l6ML1T5V<4e;F!~NW7#@ng3lD{dhhrrAKKd^FK75u?d<K07J_DaZSHh>@AJ7%>5AgAD>_F$DE8w|scXS|}Ozv``-Qn((v1^Xv$I!t}bX`(h79HwD*D=M_(BV#W-BVmACP#LiRIJv~_UL4Eq!ax-OYs`?eJA?)m*Vs2Stt5=nPU5XyW(W@j1zsoU2$6UloNfwUGXF64^H&`cEzdC<4*MbcEw34qGO;~h2p;m#lH}Wzd+|Y(K)GjCfXhD&e$lv?U>i4R|v&d(Ldm;@HO;L_!?~I`gPiM9se)t{EXu$-3F`I*$u<d3T*_d*Ieo~n0?)?SiKhCjqX9egsuM_`W5^gychl2iGCKN_z=3)iGFsY_%IrDqM!9B{vO>97pL9!eS~tJ==+C?TcQnN^<Ko|;V6R^h0DNY(PD5}xExv>-b3H_p_`oO`|XPNqnn-R`}2wqpj({i`}v9wqTe{t_x}|iLGA0^7sAIL6pjXj;=$o?J?bYC9cK(W7#;(^jt+ufhes2N2cj>)1L6AQsy?}?k6)B{f!w@6n~D()$X9W=AvzcyOj{cgLzsV!;Gw7s4~55uV;cGf>cVfpQ_(T-RCo&dIy?oQjE;t9hhu&?J|PsZN8f?h!`skz;cf5^^nG{-yfYlT(beet@M^dZp|}_NF5C<5iM|8(guA2j;qLH@=xq2!xCLX{f-!G_Z|A^l@-mxT*g5kFxta|BfUbvsfG?rj;7jlWbO-zZPL*VIC#*to=A>xu6su62Kgrx1lb`!y^5Y*O6t6*7!)xHz&_3{Ma9u)i9kdr*2d;(ogloYy(e7|f_!;y?_!+no+5)ZwmyQ{m(w^vfs91e|sLp}Y=o|29_!K%7J_Vmdr@$xSAJECLx(2B8a1J^Yo&$f1j)gyk&v>Her{c!pXcCUrXdC!eI6UETy6rKcI4Q|!IyebVMsvW)aL#Z%h89M1z=h#LgyQUIIygI=7WKes;S{K9YYHAKzDX#)Kq$V5-i9y2KNE_7M^)c`=dt3H^fwt!38zPM!s+2$G5ya)C@zv@?)6ey9(@ch50^s=!{y+zXd$>P`~;ymADSJ`2WLXl!kJ+8Ie%Jmr}!Uoc^6fAyh|unpZSN-^XN_ZCb?GJg}GFXP+T5u0xK;6t9v9WhNBdrxFlKuE(t%u^Pb?jPv9%Q5|01Eag|W4ZqiixNRkt|*;H{FG%K72&X%Np&)H}}G%H*XE<h;Gf<6Lgfm5UE*r|D}_+Q#}1^ySl%=vzq_24qTT^|&mMz4CJ>&aEl<umX#RQ2;3j}`xcrb&w4|DgCDnk^}Mzl7opF}bk!S14BZUp$VMLA`JpxHMW2E)ADL3nWGFjZ|EcP@Esl0_TS_qp6dk*B8a9P?bk}JyQID++OxXuV0EU#pL=D`U5;Z923GZoKQR>9L>VfG#n$*5%5TOB02${2+t%G&p^k+GvGJFF&!O;j)%v=!_eXIFt{->obzco?P!8Fg`2=7h^Cx3P3hYcgkp7`l|q}N&EV$nD0Cz|3Z8^cgeSqX(3$Yt;aC-pR|v&D(D&dT@T=$t@T+j|aP&n#L_dH(g!d4NccJgWyWnrpRq(g)cJys{I~)whI&>cTHarh*i@pMvB6m-sZQ-_*d6H24G};4x8m@u93fF*rXm8jD*N(|iZ9=iS_s!lHHvsMHiQc!VcrE%NycRxz?(szLRaRVq>zd*s=q^}=;#}yrp6E4Eae8#SCwdK4oDvOsqSsu-zsHP$y+$jx*Kx(O2*s1od7kK;R6Gi83%6x#6sv2Tx{ggJ6u*gHfZv2?pcg&S^IEZ;>oaNBOnk*^k2Tj5J%1GsLqGFG&vC`$Xu~+#H4b0#Cn+3fNjTP^li)S*T=X?~E<6N%5gr0}LF>R>;KpcKxG`K6EdW=Ai=x@!qHsPm3!D$mjpl@N!(Q|;*bA3IE5T*p8faa(2HX^F4L5~5q21w5aDQ|t+#jBZ&Vwhy@1pDBci}DQZg>lP2>k&*1fNAOz-Qsh=neQXd<(q~--7=OM`n-FH0XU;h2qp66N>Nh_Z#qC_&Rz4z7C&9e}K=!$I#vIG5A|_J^U^F89ERC44#D!g=fKo(eChIxEtCU?gqC&>%uMIT4*J>7F+>+46XndMsvc2;T&idI0u{w%?4+JGouCI%y3?`ESwiEiPnKj!anpx*ax>oUxVAieb7m8A9x(P1Re*^565D3CAtJw`U$)eUPUPWl2E)2T?21}H=}dm&G5(Q5cp$w8rlV(1`j|R!vo;<XjQm9Tn{Y@*Mlpf`QVCh2{boc0xp7j;UaJ;v<zGdehRGtKLs~Ho5Bs?m(Wh|OK@+rKinH0gHD9Uz)R70;id2fbPK!z-iIE7_ra&ov+ybSB6=CV2>*iKf`5VUq5r}6;B=nonw5@FoF^Rl&>U!HI0u{&O#^3yA4OBckHVP<#c5Hs-lgTS;{T;EdL8~B{407M{uTZiJqG^_pG3cfPr`f9&)_}q7w9bb3wR+q7+wgEK)b;s;2vlTxCh(@tp&G%pGPae&%>3`!f<8yaWn_~IGhX31m}XYqM6~WaCS5=oE<KRmV^t!<xwA89)1>W3qK3DL;Jw(;C|>hxF0+joexijm!*iViOUGZZ--+JIvrgMPlsotD`BOp;Mwq-gyQ$nFX8v$O@!jT=r(vSd>GvfABGR2AHxUX9q2T82mB#A0R9l3fVPJxz&+7=a8I}uS`lsq*G5agwc%=L5x5#$1uX?vfuBL2f}epKq7C4Na0m1yxC7h^?G5*WUq{ElufuPlOX0WR&(RI==kP9cAG`}bj-G;#!y)t{9D=W*zrfevJLo<54xGwkRIR6}2*tV4JaBH<8?)wm3B`rNksr;D=7Y1t$!HEZ8BRho!bz|PeH8Y<DbY-DN;m_dI2W20&IM;d)q0(U$BG^FS6GGO+ju|2x8W=3N%#tU4&4KvgO8wJz(?S%=t6ia`~f-w{s5ke_JF6t1JO3{K)5sdJlq*>j#h@7!!^;z;hJzcG#6YBE`(-<3&DBN>~J19KUxsZ4;M$v!^Pq1=(BKjxEb0GZU%Qn`@vn|Vd!Ld7`y;o1}}g=Lf?izf<H|WUDH1$6u%dandn$_4m=hfiB5+{!Y(=+R{AFF!cz#v%hC7Y<?u#y6TA`rj!=96-3uRpPoRh46Y!7dLHI}b47vk81AmWx2!9U;(Ft%6eh2LdzXOj#Tfw8?SJ2w<D{xD+8r%|o0j&bR06&L513w2hK^wwN;EreqxFh^3+6#Ua9*w>ZkA@eaZ^4V;b?E2tI(R3#3*HGIMUTTr;h)eD{1bc?y#`-}|3vS=f5Is|M%DEo1)(?_nj6jr7eu{qLHIGW5d0WiB<7k?giu^K99hvv(ERWt@Piaav%@MB|Ai*QDir^LCc!Ec-$XsI3dO&pDPa|g|3)*wDir^l!i3_S{5=<(6E1*efeXNSQ3uWor$^QGCOwZ8|C7S#75E?cH}o9*8+-{p0$+kpqg&zA@P70Ict89#Iu-sJUV#pTSHR=Z&hU7+FWMaL3;WTUupe%OmV+C?Post4r{U6Q9=J4I49yQ0gP%Z)!%x6ZqSfIi;reJZxIX+c+7*5o9)u2q2f;JY1@H`bE&36>7XAkP6#fR@j=l$Phrdb@y(WD{C|(_o0Qv?x6Mh389*(9BQh2f@MSpZ?Q^yhuPc{ngZ5o;TeeFMWeR7;3-3AQm$*&N}XU6|rQS38wG<KptUevTfDs>NXc+PwDm+GdfZ)rOJ2T;f8ga'

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
