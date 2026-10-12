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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_009.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_009.stl', 'source_sha256': '82ceece13e9cd7b17d48cd63e51cd2b9720be44b6b12cf9db8f3b9bc7acb6dc7', 'input_faces': 911, 'input_vertices': 562, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12134068459272385, 0.3251705765724182, -0.0976407378911972], [0.08387990295886993, 0.49991488456726074, 0.1385241150856018]]}
GEOMETRY_BASE85 = 'c$}r31ymJl`}POKE>!FQF#wCOdyHcq6%#SR77+s*V^j=mY{USuP!tnv=Xj1?$8N#y?*8xRzAj!i|Mh-ree3(qyY6-U_Qk#Ld1{`SJ$t)e@8;?395nn_Tr0Tpl9xwiO;eFgbI?Zg9y+Xl&)&fmf(DPa(d@-n|E1`HmhD@3``TzDv=EnGy@PuWb*bUxQmaojmvT-neFhC3Hq<|;`=Ft{dMm$?e_(KLiyz$2e{gThYuCzEyvjLMbSvjH&guX0zbuv}Bv-IMbjYISpb9tYS~TiKwY^HsyKfID-+13weB(w#_^q#rZ_f1>-`u}j{3yq5$oDBNzBaTTeA_tqr5dCD$<N{&<6=;!sXOwA>=i#bbgKB;w-ETwbHsPL))#)AR`8>1Air@-@%4q>(4J1Y_DO!EJL*T)6F)ge9`TbOl}EmPDe?6ybES^{@AG})Z`*|aetiSK#2N98DNB)mzp>OYD*v?)?H?(=U&jE9k8iB_TE_(BuV0Mzzg>$uQB#q>U?J+bOhW#;Ht^f5M>~rQLH<e?j9ZO6sNcy0$JHyNzY`4cwRh!E=S3~l3HFyd=J*2e+YS-mX>OAEdg&f}rN3`apngAZ<Og|)Z_JECo&4i44o}_E_}a_!lCO=(E57#58};vG-7o6$bdUJ6|3>}Ft5N^o>*DJ+`7zFqe_(tHZbW{;WcV39Fg~^CBfs+l_@h=}T^$M(-+17Qap+TDj%%*&i#pTd;ZOU4I_Lf1AFYjfar}yL*w{>b^ZWcX<7p(9#&PEs#QJI89P6rcG1U1|1pV6h55|9wJ?gZZo~Auo#O>XZU+6Q&r{Z_aW4puR>s12LuRQ*euNU48zaiJ5vkUrFX|DL@L}!eD*WJ<{zc<0~oA@EW=^C6Dou(v8orE`-M~5fqZ^c34n;)uR9BzlAof8I%uf=D-DeY`qLGq(~eBgiSg*tWCO1`nHDeAw>ihdouhH+ln5cOk^BY#L+<d^b5{??LG-yAp#<6N~Q`~x%5ukJ_Tcf6Az^Lsi1<9s<9<5299_-4et>yo!FC*~z@Gx#4~iSN|%9oAc1Bk}bg&T`zSeV)kwm=F2WkES`lbk`%hB!A3jsiS-Jk>mQ+*s}}gdo`(}A3L!(jh_JDNLde46U8_3v_-#Me_)(<ZH1rt1lr##65|%KPJC@7e5a)OnBUpU;5(!J8h!oxQux}uwEJ7zd1%k-hggSpkvQ)0vgp^GW@+{Zr_sN6N<R00!#~3Tsk7#!_}aFfsK2&2{Aov!UosQMbLw!ZALW@Kz8;ny>uUCSjN8Fz_ziC1xb8`q$0MPr^C({W>(|-|`MD;i@sszIz<#nX8130r9P8(sJ@U8q5Z`FA7VGd?Eor9~*cg6A?6>;csaOwrtD*k>Kc$Wz_aDQ*3j9{|cc(*s#;-f1&h{~=)4Z$HcglH7d@cGc#%-&Y_{OpM;+uuA4$Ym9G5*;rBY#m9oL}*|;lFVgUtfM6^HpF4<}ttpb^7kZ_-vVp{h`g(?NZ0*4#sE7D~v;8ocLz_g&1egmslrLriibP?1A~p(k-q30KQ*`F7TVQ*q&y5E`G!M>{Ji=8Ovflyg!O@E?yP+`-Y+Y-M@&hKQ0IVej(J!Q3~VJKO^cqe2VjKMIy#?(S>c&FRw(@4|hB$^>UsRUk^EoaX9n^{q1}l`T5@Bd^s@*?eQ(X&3Yb<zc*vOeYmhy{FS3H{<-$<`)|HE`T)jZe=G5|YLl_9N+wHtjJAJ@uSb5x_}2>*KWbP8)Je>U`ctQg?=&hyysV$dW*C3_)6&i;yLVfpPX9uv@8x(%>et@}e?xza=ic_>Ctu$zzL|U<`$m)F7@w+9@LzAoxOM4yD2+e10``qv2J$~w7vDJh1?zTz8|wf35hwYLnxf9B!{Te6o5a_icE>zs%a3tb(G&iw`<TZk$57|T$ylkg!v^(pG&kja>+6eel<kaujp{9a^4<d*q`w`1VV|tqS$yMZg7{|4PPFIV1mut0x?cPvjnJ<<HN@8@xvmr6y&&c>{=E26HT$fUc1GG_{HGNCOUAp^-8Isl;mt8$i@%|rrE;&9_LTC*`f=SS`FgkUOT;e}aa;0y9k9N)>|QMX^Ht&-MaON%`YtTKd7%~j-xIO_4$X-Cz)j+7x1wczBu8uF8(mhUsjvTjw@B*T-hlkD^U_a!-7fJp_h9kOMcuG}9j+(7(QT*ry3aIek2(3~LeVRB$p8LJ?i-9#o5a^&1c@It=|1+^>GQ<b!nUG4Iac62Y+MHZuD?+yCU_Ih&ua_BZ#fso?Nm5g`~~p~@V*eVzkFxx%kQF*fAcW%UpmUX>US%NZ*)G3ar?SZ+OI7yh&nss#7|z68{^;c*L?BWPV-B)81a9a;+wO2!+-V&*CE>x@TZ(ad&bAh`0F1Jgv)V;j)b4MAM=#p1AlS%H0{?Oc#ChI!Z@2}+@-(TkXqs!ZtKyn9~)%cjHt@t*8MWmtwX;&uFMnPqdxqSZ!wQA_KL5ayNBbpIwte3Wo-=qQZdwzo{Rg5<Adgk=A4fCx>E$#i8|HA*T(x`JUechBd<H!Bma9P%zL{b=vSgG^2=XF{dcQmevQgi<bCFd{iyT2?@Gx#ug{jhUpazyCLfS~8CiU1$=@qRBY&yK5^FzY{Tscm#bexe&6K}S?}zr}I)(lH$$0VgUIyB;CKU70cnJJA4{+Q&zOsI_MW1Gfey$4t%;gDEw@wgz^Ag7SpK?+1`fLvI4VNbH?HkIt8JjAFNq@cA{_5W`Uk5Txm*bYHfc#&rFwUiVPZO;Xiu`^PFfMt%Oci~25&5nBWM4CO22PPWi{`;^Q#}s(-QhpSd}&=h<ho*nxr(oSyo+(@+F91Q)-XHr4<11N?d>@KZQq58Uu_`jH|r<+zIJu9_-2Wl$UoE{>-KG^_}Z{5X#eg#nBVzdCrSS5X~>T}A^p)Jdy20oH$wevv8cay%|yvhj72+he#5*>d~Zm*exyU4=Y4Tqy!B9g%?anJw)o31)X56J!MQuicM5B;O8#E)hs>wG@&b;VFGBWf&E6UF{Gv44KcOV%%f07#X-_)rpN8#Qtb<bn$BD+Bz;Oer%KFsmRTW>KFj9^ib!<!w#<kv9`FoeXN#Y-jT`c~ONg?7NOGKRw7ceiUYmSljti|{nXQs%!Ym=SeyE;kz<jcL*%ln4!7%hMARuXkQH;feR+X#MzUvgY6v;R!dw%12t9^f0JP57_wkF;)&d2$T)3+MUbn_TDG_V`|+lV6RHzdvn*Iz`V$pue|=Oa2%)<U2HpMf>*$OZ%T>!8qJGg?TAoNqp^S(k*%YclM3)+VR*>$@gD|I(4gHz81|BUwgMu>Nu6pyhQ$<rBfQ;tX~#>_~*gW9`0|N`+0e-<@ig~XdEizskLslR&>kzAn|8!#`xD>E&D}^uP;4_IuR$9ia%mZfYcA)A$9x$-Pg$9%lY<`Iy~Qv(L-@RL0@ZD7V|QyNR;R@XZVTm^`<4@=X=ptj@#z8)Yqe*uNFU3i(XP+8-x1$4`W{%l}~(gQahYSwOz5Uy430^b@mO$e5L!0`8t^%e!!pTmsTzW?K$W#^{aHpdTZ~wL431lr!?oqnUOfJ=UwS2`LSa$zp+kBCBK%lkN9z!kU!@;+A}tN8}UCimHgxj5eqOL=bMUu9{aXYCfzce=S7=HJHNW4enlIM&)^#kq&*>9W&IdQXXXA(J3d60I`bZ&{n4SAm%;9JCBNaKwEG7AlzemOOyqmd_LO{Hm$f3_WPjGQpb|2^3p-&RW2fP~HrAIHU3(krx#mQyTMyr=l3(gO)?3^U%%h&Yy7(@rlk9K`<F?zUfwUv2DUN$2exkLnWu1xf8D0|iLj@lFA^xM>;yeBO0ONVwwV7yOPt^JFb&%+rvEFiAS2wi3=yJ6GR&WP7F0b!~QF6J||B)<y%6iiVzw#1wn$=CTij&mw%i0U`a^Y`3seg3^`g`Rk)=#@{X?&;kcCq5muh&EBH@%Pf`p_HW-{??J$?w|-?YZiO>-e1>vJaWZr=mU6_D;b0n4!1iy}60;U!1f;{A<1eQpdYI>fC!gSN<LvFhJ_u$b)@jQ|L<Zt33&nyit>|u6Ee1k~(qsW&HF*i_rd>op2ucyABrp-2?3z<y=p6>7XI<{>Bw?+=EfLPkQ}X{FLjI8R8p>enbwHJjcs8?ugg8z8p^&igupD_|!g!{pxm!V5~z8$9-25_t~wc4ijI0D*48;{OH$Ezu}?-z0jWNWhP6$<B$=O&wa-9DuwY+bdc+bIS1=OtKud5k@nkN{FL)0>RL;z=Tj4rKYI<@KXa7a4{IHE!;i_q>#sZZfBM?&qNrcd2kYNs<S1!R0M<#=z;9STZCZ~OE#-^)m&Qa${oB*TH+)^N@0Ghc1@qxQMqYpMLBCe@-XgwpE!pRc8V*>W7xJJz>As7vuMa`}Z9(|F)V|1g@jHCQy3!i8!FpH&KVmWK_+tIPJS4v9Yoh(_`rv+G)F<(^Z$a44YmSeT*S6&+$m=dgP=83G+(#O>iciG+^~OBzb&Hn2znUYyz9B2dbI1N=I6o5M?;48sKYf7p)-eAhtZxt0pLA=1wXX*+!MZwATjtStQWE~Pk~r@AEjaG{%9Eu|mWAk7)P@b#zUCT%eidwq^)srQ_<D&2nBP}}QNMlBP^puYfc6Zo<&8RL#W$SWp*<74Fke+}iLZTai8@tpU_9$4$vm6SAM^fgqxi<AI#b23*NyiT_2s@Z#n<C<p<hLxZ4(Xe3%@4DGwMkroL>hviLX7IfI7Al2T7gA_mE#?J^W<@us?_WM1B<R|MiCRF%HWDrpa;Y4aT^&oq_wetA(eFK01l{D%5<1ysncgOte9H)PMc}_lsG2if??vagABuv2QPmfS=t9{W4C)iyv}We3Q=y%&SA!iN7wx3{m$=XwRc+@J}R*Z(Oc}I=(TRG5)&TC+brg;5@40u}S<Q{byQ_k5jT^xV%nZcDCd<e~a-Pd`iYyD?bQ6@1x9+;XB0NQge=I?0l)Ck8X+i9Wxt#!AZ!k^&Z!YMoHr9#d2aF-V=lKXyH%U*Ug<}Fm9WMV4q5InkV^%o$wsM;kC5i82!&YjN=_#H)pz`oy|@mzxH+<_pXlm1&W4ap71=!jD5TV=VclAd|sgko!cq-|NaTz?-Y(3G7jrGVK~O=*dXM$$h%8k`%Ff@yEEEfx8XvJONaTAmwy1({|!y@jfWZKI&Wl{gK@SA#Co2Z7uWyLLQ*IBMi-pFpNENW^7FD$q9fW_eh7}!2hW}K;@i-#UF+fZ#d8C{h`0o_+hLK^;eA4KyB0WZmvpio&AIrzW;mah`o=$Buue-}koK4zJMNa(TQkYNrB!T<=WkaQ%XQFj86aw|X^7`<^Twk;^=>Yg_T{UO=Xh0a;C$;Bfb)jW8>4cK!+IX>yfRJx)L*!+k1K`!K8nX((hB3=bfozD8|Kd|kIxHxuZVAipuW@Ft#V!)nX_QOuisw$<mGnqT6ZW6Keis82S$9C{al~sE`G}M!{jY7GQKIk=F%7KvAv1Ued*i7|K1k<kO%nOZQn=y|2&rtt1Rccu{{{|{dKhe+E0A0FEt(h<~s13__mkhZaIiL9r0XL-&_m((cj7F$8S8()WeeGx@=stm35?lt%W)>-{E->eM4vc1_k7PNPkrl>n?i}eh<||?xW1?9g%;rHpb`MRoo{u=^?%uPy_y#mtkrAP+yFLU#!fpF)<MBab$a1<;Lf|r-P86E(7ZD^S+)X2LAXzP^ax7`P^hS*o<}->3LP^)tQC;EpBVH^*n0l#^L^8Tq4@v$_{?>+p<sUr|+XZmt&<)a#nlH%lhv)F2C>7il3GHE~BtLu7~%q9{iGW;dt!}!T<h7>X<K@VqZF5VKvS>_p8V&A^V~3;RSz2Db&C40G|ifG{SvZ1w6;ro;rwc3~M32zS0BZV|0*tF>ZU~xaA96llEV!j(xzpH|h+lgmFviE9*+{GY!Y>URUz{+{$Ag%d}{<_4$>2K3>+3nR^}lL#y%JKI<KPj(!k_IyZk@k@NS`0hwRZ{{q@sf8$lG-_Xt0zM0QOj%#LKAp4RTcpv$m=$GH?)p8xz*S&<F)f4?~7>xU?9B)^rIWMZ#!S$)2tz3WfdmXVJ`plDYHlAg|b!ov|e7|serd$`yHra6B;S-8^+0;<hk3K7(_-3^{s2`Ic*L|aFQPin)mcL7>DC3ag8|9wkdqeM_SnGUafn%EU<v(@!{h;=G7Vfi;I3Yj0n2e9nVc>T8`w|zlr*1aPZ-!rqa-5s>;ir7>^DbVVN0^S?P~Yne)^m$cxqg|`{4qZKzDZklRG#x1Wd<Ri-?wU4N6P+SejkqfZJFh`PQCJM!}}Maoz<72&XZMm-W?hT|J^67|JuQO>RS2ckcw#k@o&;Ev)vBV?^O%_nY*|?em0Rm0^cW^CCcOc@;rt5UhSm5-@XZQA8TB=hWzd4WF2btZm+TSwbCy!zlUbTr}5ceeJAe2_13>oKccC$N2`29u7mnNx%s(@zhAoghdht_kDtc@<L2NsPTG;F0{q<f(9W2<_#Mb#Pxwb1q`vNUO|GZ<#+u^m=P?d`Ya1q5`{u}KtgBMtvJTCV`tVQW!ng&d-<QVk@CVu-Fj4jaeb=AxvzN!Z@;Z^2#!t!rSq$I*PHl_vo9c+~^)gk(c@f?V`5`$l4)vSibNI<1w7=_j_$3C*=U#33aP+sG4aV85kNecXv8b~j`>=jK-x92s$?$iq$N9Ts%SO?Wvr#`?5$qd>TFAOGw=O|`t<vxZJQQCm6bZli3(UL!@6Fb}*10~$Az>Tti)P2e59Pje@ak4MUbh6)N%?-?`@Y<l>-~;leE2&z&8P4foDXL?4&GS*)2d;<vRp>}Y=e<MCS2}kv|BfkA6)|b<dsuvt$ov`1=hn?pFP%o%J0Xt3-Q>O@;-uZe_PraHLC~i^Ts_z{c>M$UMxI_x{qF<{fC}me%D6fesub`G{-e6@4)_Z*beRL6(e<=#;3#iQ@Nn{M$&0~Po3wk+|TJNi@?u<-)k8hH)Bu<)X`pHUcU6e{kdKS`~8RZScm=B%KFrH)IlBo&QKrFHp1FZ`Tc<5y$$!1Me4)P<d1oL>5yRU8|iwXeuoKiUYiG6AwPN;&c}cwaz2`++rpoM-?>HE9l?F@+z#+R9l-Asy7kBS`gKM9E;t{}^MRYKeY4IK%;U*!Sht?N;JXgT?>8>-IjZdd_V+Z_PmXW6PZ$t{{L$Ue&X{-Dhc6C+&+pBhnlzSqH);-t&)-`nM{bq-U~|nV_+Q#!exI$Db#7)Gi{s9!$lrVTthM%2es7>%--Y|m{If9*4{{;@yDRqb)=N-lPBo14n{c`A=zEu;4u9vPM?S>$(Rn5OqGQnCcKCd4&WJ{xF%NNGjQfcBt!Co5=|iM`)T61gK8;MrkUudD<L@4}%i7n*%}Tqj5+1_0i@|ZL{F3A9Q(vIYYkTD9(-z|OYvemF!?^X!mVkMBkM?_fl=H$|bQ;$o^Ar4kKVTngmK&dc!+)Z_z8v$|JP6m9ZyG-LoT<y}LOSeM%X8p<x$;c-yF<37@i()MQ3m&WmkX@J_-;sZe`VAug8CuY|IMfoINy@pkiVcZ{O)&foqb*d^$XO&IOJR)pWn=n&EY>AgZ@qr!Tt0SU)=YFCL(|HSX|$=uBhJ+_tn~*)BQzn4THb*FvfFdjLeHMeiG{cwG#6(;uPAwdlt0HMf7({E?ghO7N8EV3sGgl(4M!8;U9R4`=9*lW2}9xoDGh9y``LY`j7QE?#27?4^G0o4BC%=IcLOibFRUCXY)&_<M0OiVb<5UuPt&DbyD^L+wAzfI^|B9_Gr)d;lB37SNK;m;r{9meE(&5{={+b9>0R~#1Z%3m$Kmb)2yZ#pY!9ekFUvv^QQek)UQ5Rz8^{Pjo)j<kNSKA^V`@F>%GTq<nPOZ=QV9S;3wN+9(_*Y`Q-cBsDH)8{fzG<d|t}z2Y=;QTwfj>#pl%<eNgA<eE8c6;J6M$(4Ja%FfTEF*iYORApcGq<cD6z=lN4n@LSG6JKxVj{_^$kJH$zTa@VS8&y{VcpB?*#Q?uOCeskm@j9Xwnj9c|5tF3)=aVLyVHhd3a^#2O~m4SS><*TfH<JwiUKj1Z<?_|v=_o1eH5ZXDtq_>QJY<E0oow5aWwngDQ%GEQizvwicOEw>fIumhReQyk|r#lD3Z+;)^p?a(6G=4^V?2`_-{%Re@qyE^QSfBrP!#b?JUVQyn0NUv~Nxo+?Tc1FF_#F73-pGBdKJ*9jGi<|g13F-Q67pmJ9^VG-Ptx!`$m#0vXLzAb*T(pMy>K7#%{38d=dhA^PFiXtu5V?XFz@ZQEVuT}8WY&gRX8s`jYGbpj(#2Li2iy^hhKgI_NCrC@x4jJOw{@2hdP~#%lB1ghx~G1srC23Jcc!r`uekOxZm860qdbnGr8{TU4z9p4^=@sD>zC!jUyvaXI($kw_kwgo7HEEZ`j>Kdq(MUUDnGSLB3~g<fmW2>%J?VTevoWKjO7~p4D2n6W<JI4FBG4e7~~C2lwL-UtSiSG+geB%y<5HJ{tU$pM!GZdBws(sPm#Y>LmYx?{Qznp-$dI`1~HwL7u0XH$CzBcuOJ7mq#5u-@iImeEs}$tcUs=X36U_c5<CJ>~USt^F_#Wb8S#=eD0jOAMLR_Ec=rAxe5H28`#bb@_Q6xco6&xd*N@-BHs_0QQJ}f@k037PfbMKoA8~3;NN$Y?=6g+x$zv`dnx>ZJ7pb4eaMdMXWg>!=Y1cm)X%dK{HHiyv}&W}drISCTlgOvz<0|m-_QBY?*reXH~g)3^1BVa*<##JHR^!znbJkRXV*t%!gE#!cjR~ME#Ld<Qyb$xZf<F|=S3IE|JoV(i!;M-c)yd(&&nmpZ<K@k?RNPbYW_}yKi-D>=if4($?<mEt=EZmf1HeiS+hT`&mT|1@3OYD9QV^v-0x4@0pGT>{9eS#<{Ijh*bM)~A6Qot*Wh~q|3LU-66JdqbMaB!j~G7iuf^hb20?DP@2*-Geja!E-HGlpTJG2MrROeT9KyX1d8hf;R-p&hU#?VE(^O>E9JD_ER{zvWnd-k3{qO(Os(+>btAA=$-P7~`_n%tjx7D;<mawPhAS=yC&Pq*3%}7@I%?7OW2U&&U&-A{LmA)arqrRlRAwQ(vqrM^Ep+2C#AuIhrR{Dbcfc%L1fvofkIhp#L`h~1Cy)9Vjcls(6+t5>gQ>-*MS!rIf(kx^fvPR8I*2oUjLSzSWVX7lpX$f*+a!INyxg^<*T86B&9NCRro}t)-T7m3Ib*EM!S74qyLvdNED_Lo2a#^wqwG>%tak2~9nOc<WOm<=@F2+z?kfFE$wFp^hesX@UUBx*qk<Sv@s0GLcn3K&mb=_y9rXyz~|KeI#YxfsJ@h7YG{fYXL{E7UGp*YEE-6v7+k(0=m8H%r1oex*256D-@SE-N4SIMWX*8OSfbMk5OF{)ax$EX@vh2k63uQuSPR6G9dEBPz)>{!ErtoG51>QY2KMpn9$tTc|il^jFeNmjanyqp?A-9T2limY@AIf6W!x{9ncoIIU6g&Iy)G076+)n$YlVu^87gQ0jLbv$_@c`9`hc@pbRrG}GdQ0G#^$&0BgsNv-G)Q!||aya|8k-CYzk-Uq#ioA+rw~M-ytn?sx7x@HrCwV95Qt@T#ZR#=dGwNgNF|yK&WTg+tkIC<-7s=^tptd#$#gF*6i{wY-ebhr_rCZ7S$SbKa<dx)wTIxDmNR1#bB+sPICeI{K)>7BgWa<?1Wb#<*c=A~CC@poJjiQE-N0CP|6pz+Y*WzfZK^{$>z)&2<P#nroJdHY$taK_lWnE6A&LvMH&tWKDs->>irPLMVrQ|gX#oM*ib-bOrk-VLJlDdnm^aS}NIY~=he@WEa<RtPNhT>0J>bm?yeN6sD&R_$5N6x_YW^a?a78R%CTC}GYBbTy7SsQhas%epy{8&pwQP+{9$eXFLWTkt^JE(tA_mGvICo4To{)>E-dY-KGDfuq-E%hl`>36cyujIF68yo0%veFzj;LOxq)Ewj@R7YwKvWfy6A187asw3Hv`HFvQ(4W*C<Q#0rPqynb`6u}`^*i}H`>FUL^*Z$_`6<WiI`v=jb@D&d^W^iK55>EwTc~@;dpNIKsB6hv$kEhTveHQMGU@_qBzYEf9yO92$+b0)x`;fFJf9jxo=;v)-ArChj@MGxVm$RPay<EO>Q(aJ<eOURn!8DTOTJ0|KvnDJ179mnZ?(44Q*)8ilXEi^m$X`QC8>_&l4MV+6WNnoom!S$mgjJFhT>Wb#TBR}$i=Ak)Dq+p%(J)J7cx+t$WC12Df^7#Pg?4_SNxl6I%SVi{D%5kOWofTCt0oUB<gi7bw5;mlKPL9x|b^6ZnciLQ@3cTd$Qs+)MzbrKUcieYP~L{F3?i<f5qxrp{_gX`VmH*L!QH&Fst<)MxCdnUcVGipw1`fvP2<GeI!RHcBbYcJCk!W6sMzRA#2q1)GXvI%u}41YR^!dhnkC=i|xq6Q0&N1?7~o7o}t)_>P*hAsjqu1Ys3<+R1ZruwS;;mQQH!gsUD2le6JU|CbcfPF5h31q4*Dm;<i+8vLCfQ)tl_iy!H&m&8W4>&B)cP+FFh3L9Rx2r#g|{$wjF7$oV)fMHq^6FcjNRGm<rGI%-C8M&_ksD9%lF(o)xn6Xzpk4xFhTWDkzD;#!udWC``irzAC{on@{1rMN1!61fuJUzMS_xh1+=qMaqWF%)-TC~ie<PHxWkwxTvB`%>#u8<QI|uRcSu8?`Lija=BOZ-uEv$a$$*Es=q0!^q0{$;zA@)FR~Sme4IxkLp8K+L5gEPjWqS6KY4Y(#~WREiBQHp|}&Z3AqXLJ284%qCZ1%0JRgj6Y~QY11&L_p|~G4fE>X5e$<X+rT*l8<UZ7n<c{pW;sMm&R3CB=YFDZcxec`?)raiE@oh<MKyFE{Le<Gt$YmIc%TcS7t8+feF%)}Jn~<Au4m=r(D^Tl@-Kh1cb;xy?m$E(;`%*iRJ8{kwtMfvw?`~S^y6;BqPgdHC+?^Uo?M3dzyg-KHq0|7f(!u1R<l)p{@(AiMYA`vNdBYfrhfw>GmG&VIArI10*Tf)dZ}K2=5JPcaEp@H*rFJFvC3j&cZmp%Rq1M!v<ksXy)GFjg<Qmk9WG`xYYDIEI=9Q<GA-hl=sb$D{sP@zXTI%&zaZ#!x*^%!pN-alLT8dnhT!LDTtkjdNv;tXaX>tj2F=_>J$~sn@pIVUWMpjywoU(5gq-G@-BxhqNw$)PiR$HnKIpsR1I1|;5s*%-y>B%YgF?LjYvK`rhT9jOreRiN0BRi0DTJ<?6wII15`;e1rOHOHPPO2Tbnx!-4Em4<RgItuat5B<vtMTtusP)O&Em6=Cc8qV9+OI5ek9xxr7pPYlil0+ok)M-)QNNLus=B}UT5(<;s~|Zq*^OG7T#;IiTAEy%dF9xT+U$$c%H+!Ydlg1Gj!ikfw<tq#Mrw9)cD64gL-7l?UG?n+L-8%E@w!F5LB2&k!%%$0YD|w%uaK4QCqJ=7vL(Jye~^{tu>mX1N>-sbC%rsmrLJTLYGJA?xj5B@>PmK}R-(F+RaCV^O@?9*Y9(?d<|{5kb*8$KUD-ZoYCf_vIU6+(S*hy3VvXK=zE=Kwj!!aK>3#BZ>J{pJ@_pu|tnFmZ!G7{J>J#!4j`cN$;*V4{rXTrQaVD#A&qOUu&P2}7P+Z7rJ_=D?$c4zo7>d2D=E;j%iR?wzsWr(uxgNC+xjwZvwGO!s^HR<&rR5lkD^hEcYjTb&G8DU6tphizGue%tmzvEcbx%<I%WA$AYn=06R`aU(lqJqt;;^QEy9PbVP<)o5_zv|P`5fPWhoSf-L-8f*aq?bj0`)lgIP(%1inmb@ledu*t=gJMJxW%3fc(nR-`|#a&3JE#$Bg@yIBSWG)OCzCmY8mdVbl=}#mgCrk5bo=*YN#E8H%4!&yt^zKT_|L@3T!G8H#^06x-TD-;>|7KZ;c-&P@GHR-rgMHIpqk4>bcd6FC#}GVrzHw+zMCsISPc*oJEi#ha;*$&cC3%?!n1R^uK<T}KWh2T`Y!gUG$D=B77w1X*b}@&rrFu*4)wjHOOtEVRTdOH8GPGZgP)D2}5pBroLq;~0vgsguaj<W<xe<QZ(!D#iq>wKRckS31b5A4>hHgUExJ=g&~wi#mzii`?I;|NW^`$o<I!sI$le$b+rMXfQRLtaKdtq$Lt8v7WKg5-S+<EV0N&{Tokc$~Z6L`^S+(sq@J5`2J9a;<*gP3#co}D|ze%48@BXiuY0z$O&xsUWVeE48^ypm&jW!vELGV82{L)e<xtsW2nb1aglnRq4)yTBwrw(r~X6!hjq_06rZE+C!ZtVqMjl@p&q54BA;Sj%3h>6WxXk0Mcqo?%HyT1PsPzx(<XIoD~_}3e;oC=P3n1}IORN2{IAs*{Y$-0R(h9wf_jE}mwcD=aE5w`e2MdPhM{;Hbv;?>3bN8g<Za}gHmPfLCpDZL&OYp<{!312>rUz!az{(Fw}h`HdQdwv+E}84CAw4FGMZSTg^l`WLeS=xXhv<sP~3ppg4}@IklKXYgmoJ-6#qf(K>mZ=nA(QihHY)kP~4R2OKwX3liHr#p8fxmp|~|eaVx41xh1tL)raiEysiwz0aRad0C}j@SP!LkCJ!Z#r*<HZCx=+gM+mhoIfNWcZ9xtu2U^WpAhkI;kld4@xRceqcA_>SEA=LivP54?^kMX~#28CVq^9(1jMX@d;W&+9ephNAt1;}u@oq`(LhVcL%VT$8C?3dAY)~hY4_acMCE^*16R8KuN)MB_Qx8!OlmDjvMLkU3K%GxLOdd@gNj*#+LY+oEOrA-Nq#h<8X8R(ko5+#mWz>V@W#k>yc=8VNT51e=HgzdAh8)AZr3}TZsfpy(<XEe*i=`eS$C9@&6z{eg)7{j+$h*l$7>buzjr9`heDV_VaE4+(t2ywajwJh$y%~x-S<Ou+>NIjEa>_ZPIM8a&0;!QUsppj9VCpiP)bmks2z3s5JT-zkhdhUQ5!4-I@8&kP4(a|+|Mv!||EaaFrTITQ_}}kL`%_)(cLrH%{pW|f-p$ji=W3d*<$vmd>uo>v>VE)=L;XY'

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
