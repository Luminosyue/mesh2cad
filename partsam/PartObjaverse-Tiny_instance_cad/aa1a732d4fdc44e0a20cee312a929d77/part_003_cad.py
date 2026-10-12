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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_003.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_003.stl', 'source_sha256': 'f96a56accf0005102846c872768aad46b0067d37b06d8c25a5ed2c8ff74a0e68', 'input_faces': 1304, 'input_vertices': 721, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09929057955741882, -0.18636180460453033, 0.23970353603363037], [0.19180625677108765, 0.022927481681108475, 0.4680766761302948]]}
GEOMETRY_BASE85 = 'c$}r2dE8ag9{=|_l_4raD8f@xDJq)G9c0WDLdGYmYphg;OdXOUxe`(-k10`xRGM{E8YqnviN_@uS27lt%kO;ldavEy-?RVty?(#E_UrRrpYPi1th4ubuf5ND_Hu5=DphL-?qB_2-t=ZS)#(rf+I9_U2e)+Z)9>1=yZ3G0vv>bYuv_TspVtv*cRuUfE}7t#;Eu-Ky7#@hPvfJ@8Xw!^$i|13HSW=?Prp80dtTYAPq*&!Pw9F?-|j`f?=@X}cQ2Nkv^(PPL(5tna%kCIW&e-=su#PE-|zaF?WOOZ(@k2r<(mzm)>{zzxd$)qGq0$HEng=5vSt?yY#;M0%I3`q%Qv4nNcD4D)+YT+`~9<h%+J^VY*ylPxBap))CMQbmIkBO-yDAKw#^B@tX1tn?PGqSQM);zK7PY6)epAJ-4OTl$G<zGeasIUUmE(sz=wvYe#N#=HpcyY>q~~WkNFji2hU0N^GEl&P2O|<7cH-e_tX282ei(|`&rp+=-jaW-1T>>e)+b~6Mmt?V-K{C`Q?Xgm>d6G-=Ffses=ZGZS+Xk|L>pK5cl&Pj()s-%r6{P<*m>^|HH6;Zrj@%6aFdRhV{K)dDxDjAKX6wOx4eC`zYa8?*H|z?PGqvdAqj~$7kyl*UuIgxppS(bWnJFwoXp?x!u3+*FNSKS`2XY|JSmoJ3gzEextSbw2%4aEnjo~t&?27ZCjD>%PwE*@(sVD<#bnnRm-cx<F<8T!q2z<`mXkI|A<!eLVs+XTf@BCwkY8jT2Br0(ECBFlU)73TK00^_t}JBaqutqw2%1}tzVlL&)c%^2W^P^K5xCBZ}aca&pojIrttV|eR5;muV`93ydJ$@X!Eo4yYzT8-XHJh&bobMyg#|GsusfjwphC;JU(X(SsV8Y`;HI&!uWA(()`MO`g{=g^DFlc{rr}>tJD14it|29`1j=A2|xGW->*vZ%huIjm-yWMe_xo^&-{UFL%*!%@-=CG#p@>}`k7nUBlL5>)>)J0=a+6vey_26hkoV7N3BZryRS?1v+|^A3qt?*KC4sxg<})PA?USee%SxspRY>uE6#3_Xg|nL4E@R;&#z4NFS=oUqMw&O_jcG$wd+=;`N7QbiS~27YlMFJyf!OS{l7m>v|rinqC$AwPTqZ0nxE_cce4E|Pren_Z~euJRKMYYA0@t5k5A`@-)rQ@D^vYOZIk_3{==;BbIYc!Nb?JImaI(kgYl=Owo}o(ZK6Mw8>-Am>rdpH{uGWsV|v>6jePTcbGNmcmUcY7Z;xlb>*6VC=PUBf`3i=Pc_S?!f=#2}NXv)d#G$XJ=9~9Tz6ISnzn+@U_%@&O{kBXB`?)fCy?EbVFJ(2ao0xVzM!vZogT9BnoOZo?-(K&P)%r~c`)|e*@7wXDtVZRFp>M{e;O_b3L*I;V-Y*&7PB`nius>$}^u8TGgSv-46XvrSpS^F#=U_?Sig-UOM^|Iq_-=4`-nY%%829rpJ=s6a&mCQRaQhTLXjOf9+z*~Q)wRR@v25$GgzxW<-Y-1Wi*eQ6e=D|5O8EZ%>;2r=VeWIezvs5zm+<}l-TT4V5w0DcS1UL7+>r2jUiE(N>T$09jm>6<=Vi#CwP}8??a-vZxPkMl=2QLrtVa@l`LI1gzw*~R()}fmCH*`949BJN*ZZgYHAg1={5zXc>qow+UomyXthD}Aj9cW!$zVjnFPuKh)qm>Vbie+?3BU5KX|v*a7#ud<)j#@FcOUGR^vfPPCiL@PpPB0CK3tIS^Ns3;e&M}6Q~luQKa=eYI;D{IxfPFg2>oD}0jYjr%J5|SUE90*zuuhc7nY7r__<yS=7h(;_K~Yo{g>B&nE2d3KXv)@d85^7es1G8iTb&Bk9PU9wc(mnfAN1lNcesBcI{lzU`?8zFaJJKKj`<PyU$jyzdFq?blH-qAKhoW*I$$7=cjH-e%}@E%}VQ!_icYFZhdi9+V_oo`+ZNYGAr$Pdfy(;iq!|qOgmqZZ_Zcc-B(Xb%Lnh<e5k0`Wm;;!;oE$xXxDjK>UH$XYm?LR-}^TID-OASa@zIf{gUfz+4+;>pPL^$*`0TOmld`?=f>@^vz^cH!LqFb62AXE=>5vEOI>|_4_0igNc#L9^nNgIx$6(VLxZh%x%!W6cGvaPj~B=L>HW&LUkv@Ss)N>~`4zK<eh~L_?RE?O%4I`Wr}{tM_hH;G4Bt2Wy%W?NzbefyynfxfxL<Mf%7x)^e(;l(X@0(S>-CAxZFOAuJECw!yOn8vQ2tS(e)+VU+;e`N{wvb_!VwpI6!(LN{|cYO%ZGjbewrWr_H?3tbX|{m_5CzIchk&d`%}MoGqrtu+kUX_uQ$^A?|s|<$~RZMns$7=Uvhj#4V;j6{Jn3Ff8p3mo=ZKy`1bq;XYcrQTK+`7$)EghXN*qEPw(6O%=eh`WIWF+#{KAgKmW6J;KqdS=YQ}E<Ep(K_Q%ivY#o*Gqxm2FvZrf>zMm(|Z@ywf-1qZ@-mhr9SLo+w&s~`4r}y6+75e3yR<B9*KRWJ%xF2k85&DI58?H(7gPz|d>(^?Q`niSEs=Mp!(9hST`MF11B-?pvLU?_ZUzJ;v=I1V3nXLcgKzBV}K5%uKU+6mQ!-RiA_0Z4nJ!y5CpPSGvQNQr$Q||faimj{C{CxSo>k@v=Hm-hI)75Eye%x1y_H&Ql8;%cUuid*U&9A8SaH9RP28X-)gXgVE^DEkQO7`cKoO|w?eCVn)zoN#MiTdRa?&SO~y;r6AW!)<h^(%K;9L^7vFWa^<)&Hr^`o#D8ZdmB&2DV?7=I4)Dm1sYhQ8V=Yb7R#1&Q(Ldkm;G~2XmiI_`wI8!soq;As3|jWo_pq{K^eeLO<W^xKuwkVolP&thalfe56Ub-~8)@U-85Ku0OBulj@h%{5{#vI}73SVfhier27w5OI#P_BQFX4vPY||P4n}I)<|AQJWrOrQ!CZ4829<QG{5qfrit_G??;tOH?2(b%gS1;O7kmz50b~><-xPk`tSXc{x7OOEA{wz-yEM@r-d`qj=%Ryj{l~cW~QCr$T#P=tVi>iY5C)Qn?J#gf6hqFPkfu7x$id4NXvikm*oG0Yh3$weC~X~jI`^~`z6=oQTxqEyWS(;Uhjvka?j6ZJn_CAPjX+CJKu~~-nZjb;eP|d`8PWrdf$$R`F%Eq&og$s^}Zc%^9^rv&*x@5_r4v^^YvZ|=ilu8!u$4qQ8{4DYoTxMN8Y#hqg-L?E8+Py_dD;~`(0tr2BB~7r{1^s)3UB(Cc5h@dB664$^H7YIuld#YDLx1x6cpWx6coiFJ1mp*iZ9(68Yx&r1J6Q6XKs+{`7wCIP*KDeCreL_e;fb3BO|V#qRHSPoLy`{%)AtI^6x8>zNmv&)*+&TL-yzo_)uCU;e&X`Rla_-~WBn`}u9V%@5<|dB*zw_(#5ZKC!;f2k+bG4eR^-^uB$5u)e=uyl<ZeqW+lssrCJM<$ZfUwZ0z@Bj4OlOMJ##@7w#S_5FAr_0!x>OMLDZk#FuVCBCU|?=RLb>5sX;l=$ZR+WU+3?eVnt7wg;eWyfvn`*AzUH!}`f-{zGaSFLaJ){c|bFS#zvxMzKT-IYDx$sGsYizxr~qK$FizZc>C!t(=NKN(MQzjkut#=6rMhV{*Si1+P$i1q#NP4C<JkP@HYv);G!A=dZ5m%VT2L#*$Ak9*&aW7hY_GwP?AKe4`_ABfs9<DT{X`HjAp8TYL3^T+#ke#ZKKej_@MW}LLX&*!KeGfrCHUoX-3GV?#y_wzH6Z^m2e`|CH#D>L3&-;WQGZ^qjapYbQk6Eogg-;ZxmKh1bs;xm3mpKIp3tncT$qIS&qT;iMd?f7i{lKz|Vxx_ce$Bxg|x5wX(&(^o+*Us-*-{y}U&#iCs(~jrXxA|}953O&nFFXEQ-(J6V{I|XxAME_3_3ij$?-$m$<C~q&w7wlb?R=*7?f7ixGfR9k{@eLX>)ZQ_ozKiwzh_a{z8UAO?~g;|n{nIv{=9hKj@#Dv=iU2u9JapCL+{&h*!n)tqkfuk)%yOr^S&Kdt?#ev$T#C^iO;y<eLJpN-;YaCKh3yW;xq0=z8NP=d{f_!lh!Zkj~ORReDi(nIB9)*JncAXeS5y_xMzKv4|d$MzRfo~j#=O4vmM8*Uvj;eamo7rdJG2Nxj6h>Gyfm?X8ym#=l8Yu?fk#>{qOh4H}n7AxAXtj_wxx+J7)Z`zWu&-{@?n3J|yzZcx8Qm{G)!F`G4#C`JBi%<D2z;K6u~G|6AYBM|t0lht~J`8GWvq|F^!MPxHPVKdtYt7w_Bo{}P}1!03CK`G4#C`NrtHnEC&x|7QN*`hNa1YR8Q8*7xH^)PFP1Ti=gMk#ENN5}$F;`*xhSz8_bkewuN<#An=&&X<}0x4xf0kJ>Tw|JL{O|JL{O|Izm~^Z(ZO^Z(ZO^Z(ItF!TS`FX_Lzua)@b_}KfJ^-GSwxv!P@=KR|Gn)Pk|*!!CGZGPJMf9sdzznTBve!V2;|E*tgJ(~Id65n3$=KgDaJD%A2f9u=v%HFT7Z^uJB|8IRe-rD=S_3e0W=l`v5?-%xY!20%nWas~_Z|`^Z`N8`3ero6ctzUA#HuL{c`)2;%`u6$3&i|MA=J~|V|5x^Y-u2VIkAz?HK9cdH_dW1S-bb>&f1d=u<b5RLNAIiPm%NW;{OElc|GD;kB;!Z#+u)bHk7WGleIERh_mPYry)WdCn|&Y2_|f}Fz8(8MlJRZ(CGR5{-}b-ceI(<T93T5WlJV{FFL@uy`1bskypLpklRqWzBN^Z3r~Un2So<H>AM<{%_wD<=*7xrpdf&d^YkmKIW7Lj$zt{Wr{a)+)_bsFL&HKI9_wRFh-@e~l;`6>}^ttB!UhDh!QKNRu`@JPT@4H66dB4~C{(V~S+xL5|@89qBzJ0&f`u_di=zE#>d#!K#W8d#B@$L6D@Aq2Y9#8vzZ;5Ztmwmt2`Zgcz`@Pn;`DWkmjjki}ey{ay{@eF^tzU9|nfH6kJO1p>yIBWeeZLMO^36I3>-%*O-nZ)@N_^HqM7~)EQR1_%!TWX{M2T<e+jS6;Z`MJ0->!ow@mUAqeY*}Kzu&MW;qfu+F}-isV_M&@_wl}6k7<3so+$FodQ9v4^-9s_n)R4beX}0Z`hNYC_w9O2>-+UtQ9EWmW{J=GFYnv+m?b{z%cA3N)?-@VuV0INvmUd=XMJ4MPqQA=`hNXgbR5ij%o3mVebM(a>oKkG*AGVRnDv+?KI;>s?`76wmiVlHj6T<_$F#m*k7<3s9@F}MJ!a&a^_V5T>5pBHS>l`TYu961-yTo99<#(Z=gY3gjC`{mGxE)P%o5+^n_Z7-eVfmAJ*M^T^<vj!miXp+wCgdgZ?AW|9@F}EJhAIBqxQ{uOzW47Z)QEF_3ij+*JE1Wj?anpnCB+`uOc=6oH?lCIK3ej1Um<{gC1RD|4R{>`sX$Me<^Zp>;J3&rO4r}TDJcG`+tg5uayac-HY4#XlFQ6+^Q6}bI?xkpT$0ZQQXeRI6WcbSo`kD{?d!!!;4#;;?@Jb3_grlH?#+=efMI2X&1O^amyCB^U!nQLul(Nv>U8__hEnOrLgu5*k5`!yi0N0TC|=FoIVQwUfljDZV#ak!|Kn^MSVPQIvj4v=e-m-eLiq}M8?G?Qb(S6*CN*_ZleRIPX&&5D{{@^_H^KMY~Z+c#<ledZK{n|*tZt@OUDI{weODXFC7&)Zk2IuO`=V;F^O}lbNnFsPxy0UL(m6dwYdZBN=F8cbx!peFY{SyTdZ8FR@@#7oIVja{*2GK9~}bkz_}mEG1oB`*CB6S;Iq{B3$(c_?e5BP6<6{ZgVFope-V2C9SrN-)#dz2#|Mu8V4sK42jI~h?<diU7>}bYeHK<*<H?Qj<bvl3lqYa*J-<l#Mb4Gy7bw5LF`h)O=sZ7%J`>|nl%->0Jd(0>M2sJ&EFBIjFNTo^55hyxq3{s+e)J*uA&#@>hbceI@f=J}=)66GJ{sfElt*)n#md#cira1I?eM<EbGKh{yDxA$C~&+t<I%l=Q+Z-t@4pqdThZI#|8eg7qqoAkPWLEo`M{~#5Z53N2Lw*<3LMwsdcTJ{^28c%|1Rnsfz$r*j*J6$2Ts+tSb1KBcBQH--itAGVBl13i?duucLq+?hB#nMyq!9Ca_s6dj_G*qLwjP4b=$~;ZREmmj@9p+=ifQ6Lpjd1i`ymW#jyJPQ{e6^($g}In-sT(#jPuPC9HF#wk|_2fi+hDL=OB!j(FB*Jc2$(Onu%d<N7Tf!*}>E-(eU!6jnRm(?97c8OQ2d8U2%99^+b+rRT%i_gnUtcE~uc#XcGvq#7T_k+=HJFOr|SwqK;r`_pf!uH7-@zrMpi(P6Oivwm^A0KEeKi+#?_IMqG;O#1c}{ga-Uajbn0W`AiptUlMH-_nY}v92|JhY5Ta^?d?;u1~+E8k0QlMp>%y>pAjMeLWjhAJ3+5|Du1=TxL7}L0Niw#<BW*2>q5`1*^}y&~K^6lM3=*-(fu8MST}<rQR=Sb@(S@KcK(B-xK=|{Q>@#*w^THu(mIWe+&EXD&2^F30D%^fNq4feN4O({tW#D{tW&+aQAfSr|2i}zlm)^KZXB8>>G3wyoK0i^c(nRVn3pr;cdizMSp~q=Zfu&{t7F96gv>z8Lm(4AoM`^U}BBYgWyAmHA5T2hY@RmHiHi*))s96w<2~V+7@n2>?rg|_y}U{(4*j%#M+?k;6sTuN87+nh&4r<!wrcwLYu;6#2TQD;CjRkKpVij5UY+J09S|42%Mf3Z081)rJaK9+=#NYbFiJ8QkHfJwsUjJ(o2Kw+=jCB%3wRUqb%(jZ0DmWORo;L^O2OLR|VU-EoEtWu$@~_mR=TY=Vp|pmjv6nF=gq6!FE1~vh=)QJ0D0{dUmj#ccv`u7;I-<3mv&8PK)u6l%*YFyqU5z7vpazOOK85Cd$&IWBe&)Y1<foLRs26#vfCb9ueaWl%=g=ypgiBO^m;!EIlg5UsIMI6XWkFOWViz2g=fuV*Cqb>8UYRuAhpYK}@Q=J{>(L#+@ij&yR6u%F>Hs+=a6A@)%!AS=ueeS5lVth;diS(raRTHD&2_F}{kj^x7DgQ<nZC#+Ol+c8~ETl%-e1_(ICki(`BqW$6VmKAW=i+!%MHEIl*Er%{%k65|e(r6<NXM_GD&jE|)(Ju=2eQ<fec<F=HgEn?i7vh=VRA3<5#EXJ)UOAn248_Lq=F+Pg2v}KHsp)73|<Mx!L$Hn+0%F+{Jd@5z>$uT~Ivh;LVIsFc0=>k|ey_oo7Vq)d=QsPUAiIvmu5r2=ESUJ6%_;O-m<@5^TD~O4e)2oQDA|_T&uOYsMm{>Wzn)qsBV&(Ko;wy=XmDBGNf1j9GIlYYdGGb!o^t;60B_>u*FCo5!m{>Wzi1;F6V&(Kg;tPq1mDBTy&nG5UP8Wz5h>4ZcZxMfsm{>VIhxi;~V&(KK;<Jc}mD4kb&mbmNPQOX~O=4o@^i<+giHVid(}+(aCRR>QCqA8+SUEkD_)KDA<@9Xgvx$k7({qW>B_>u*&m%sMm{>XeHu1NKiIvj}h%X=})^9fb9=Z$d4@=*Kr88jZEcg`kG&b=7bQau+*idu;Jb*ew(S@-3a3Y^Cy%m;Dg{RUdUnfUg+836-0l&dMzRu~yr2}E<9C!}<_&OblO9#Qyx8S$f$JaTFxO6ZqEx-l#@paB2E`0!&&WGo-kFV2-cqfk81L#6{A^V7@6}KtH?Y81}5_$rgxF0$NzA)o{Pd|!20!tUe(xtIFR}hyz1xr`KtJufaDJL!+2TRw$YuLxvxr(^-Sy=i3`~my;I^Bp%pNFOE;C1Zd>+~Qlod8Qef<Iy(U*|I7(kEf*3U~$k_&S#mmp%bYm&421$Je=-xb!ht`X2lq`}jH+62Fjh@))`lUdldV{mnpsJ9r!&2}|FHrORS<x)Yba2us()>)FTGxth52IavB3{2}}JI$eoNpMj-o;kE4J>s(1(Iu@3$hF7zXuX8zZ=@?kL5?;wZzRvl?rT>Jbi{M4<<Lh)LE*%a_m%vNd$Je=txO4<8eHVV0eSDoR#Jg}#Mxe{!W$Yuqr??F(Zl`9Qo}P7l2eFg0PUVSj&bZh~)R8B?DdS=%P)DA)SH{KKQ%9ay_bbJwb59fB$R<9HeN|U{J+Wi5PUVTO%edIl)R8CFeO0kHx%Y~1U=tt9zN#zkN$mKnQ+eXv85he@N1nJ(#>Gygjy&-#85iq79eLtAGcI-tb>xZf&A8ZU)R8BCIOAexP)DA4bjHQbq>enXo{tn;!ZVb(f=zrj`>L*3brgG-XEE`3Hu1Sxr>ZM{nb>(*r}D&;GA?!jb>xX(&A8Zw)R8BCJ>y~*Q%9b7a>m8FP)D9v&!>v%`E?ci8k_hc_ElZ6>L{k?;1%#IY~s#Yr>ZNSNbLNqQ+eW-GA`DMI`YIXWL)eV>c|s6opG_Vs3T82D&t}usUxo=*V-tqw^78!y62vparap1?eH{oI(j>-I;T>W-W`icXQFq*GvV229-a-qgFXbm11~@yg!MP$vnfl5#A4F7(IK$voJm=Fe=H`Qhu#mX&KZ=Y_r+q;x#)ec>YPAX+AkK9PC@&@8t<EA-F-rOD6H>WHS3Ot^yk>|`I+M<-2&@gxkuLBFQv6%wWT)Kqb*@Q$Newkp8uqOz%yxcI{F`2&q2Fo-RDU6fYp}Td>`Eh)^p$Ae9qr|##^+dHm9NghV|T+$-4cdf78Y^>P$hufOVhQJ?rjI(ps>dA**Cvd(sR%g?;Cuf5N)|?3s1#Nq2|!TvI3Oo`<A|!`j5_(8FNe%l68;_N05l%EN5dolj|1So>(-570wk9XlPvW$0e8@-xV~_M}<3M^U#H^#*j8tmCV)?wppRzr)?hrE5|3M|>OS?k=<?d>1?bJp%4s+-elJp6IUdO~tKdaqElj1`lB0d(hT!AI@EGv<7@*aodshcBHMF*hl;3(N^%)S$9saK)-;si7!Jxhp#VgJMcL>@EJGKmfE}<JsiHSxK%4|*PvBkwWT&MK|h19<y>En?f~CSoBh!`a8Himb!atMZK=&m(MnjG_;U1L@a@H|F6Xl@=TfYg>Rg5X0S{oGyU^QU9p^iV-$`r$$L9{>cM!XW@714pe`4aBId8Y3ec|pLqkrJv%<-4@f^UScNB;r;gMF{(_;=+zcO?(5;J95${7Pb%aooy@mlL~$<8u}9tB8qva2~p$*TA=AUGDZnd&B+U8_=Hc4R8<iI(SfV`>S{^2BLq$j}*84irYWYePM0NnPKSOu=e?_xbMB_@31zV>-*6E!P-Y-_)v5=cu3ae--Bok_(Av~v=*$kG*;h_YP`Llwsg%tfbIw@R)x=zR)f`+#>|J&y<qL5>t`^Ug$Kif&;Zsx`*8fEbz$Yqwv5ZWZQMJ%bDnjqu0(%>b??+YbUC^=tT~^bxX=8=Jw~kGVGXnHelBeSYai{q0<8lphkj!GmTrZw;ka}|f1<APe<!}jPJ9RPm7MRc=zn3&cYRNPzo)Na{r)S<y8cQV!n$|roUTO6V9i&3n{n-ZOIzYwsM80n1^4GW-hu85>$={b@3BAML9D*2&sU>=!kR~^pLNe2^~ul0+_P0@9{Lxod9ttQ?^pCytofCLX-`@o)^%Dh>%K=lzQZl_Rein_-4DK%eQ!qhhx^jEThaRPJo@%Fs{9nc!B{;N{R*DLnEVF%FIdk6dNx>t9t>+d(Y?MOS`WUHKHrYkg{xEV7oHK6Z@;jKe?WhNe}KP3zlXnrzec}>zlOg=zk<JnH=_T7H^LjxN_YeOG5Q(&G5iVoIs6IyDf$KcDZB~&H@pe{2K^8G4ZIoM0&j+YM1O{Vgnvc1!N0;gbB!v`cV-hGi0%&`2p@#jhYx}qqX)x{;b!O|a5K0CdKlaSZi^lcw}p>HTfs-dN1?6Zqu_Sv5pX-W4cZcJ12;zxg`2}o(I#+HxDnbAZUi?#%isp^0cbt=0Ju833p|C`>u7a&I&Dos4}fR$+0)Sm@I3lD8*K!?&3BuJHih5eSiFrkhZl3~-a*^IOF7ny(RT0>&dpNvD0mU)atV4QJfCyF2yF`&vMyKVqb=Y$S(jS{v>7}j>vC}p+8Caib-6nOJqVthb-6wjJrI61>#mK-=+4xAIqR;aSJ7YL@mY86y^Q_{Kbv*e>UeZBT#<Fx_Os|W@Kaeg7F3{{;L%w(c07fC3O|{3W6fyv6L?hCjZIIYAH!p^ZY&#xZh)W8y0LEzx)FXR>&D8b(J$c_vTkgB2K^d-DeK1K7trtESF&#GehK{nR!&zZUY(eDE_pf=oenP`Pv@eu;djZ?1?W6@8F~6H`ZoMNdAbaJ2VO~@zK<@3SCFSG(WUTm@^l5d1b&Y^U5+k-7m}y%q4VLl$kT;r0iHn4O~O~b8R#r{20Rsg6P^lBM&E!Z!>^)~;7NRz`1!2M(+TLy@VKnY)92Cg@W`yo({bpt@Z(vRrz6n{ctqCa>Eq~A@bIk5(-G)s_|dG()8Xio@MBq*r;nne;3u*!Pai|az+<y6PoF@ahM&v2JROTZ11sm0d(+S<@HF@}^mX_(cp~kn-Ivf8;g{f7(24Lw_7!VRvm@<w<nuhAMfoiH=lLAU(z!A2L|M8Z#^+O(z8mAtl%>mJd=X{o`!Vi9S-LXD7gLt5i1CG#rORV{0cGiXF+Pv7bYYCor7V3b#%EKO&WiDwl%;RR_zcR@H)4DmW$C0CpF&wWA;ujjOP`PNiIk<|Vw|Ha9U0@}DN7%Z@v)SpBVv3sW$Ex3A46ICXpE1eEPX7-?I}y2i17)OrDJ1!5@qRgF+Q2H^u-vTN?AHF#-~%3z6R^va;>4zJL!54T<a|KKKp<1^{&0%=f5{_>jSiQKx-@hpe$eODzyGWYa+BZLhpy?1GgSR@6X>8xb<gRL!osLdf#8`CbY&u>xXuyj@Co$fUh+WT0@~V6I!34brV|SptTNq=Ui(b^uD>?1J}9-y#ub_efq7aIS>6t)9*~pi^%&8U%$2WyIu1f`dzQzRQKZTfv>p`%~@y;L%-cLPoa4W{g%}{u;wH*pP}F3nzzs#hUW1eAigJc<W<Gje1_&tG^e3C49!7kPC~!`^gB><6#7l3-)5SZcwK)RDsEE($NeZv`^LC8WofS%H=*1MZj3gB8^Z^oWw7+X81GA2S{JTMxlVCArr7uOMg1sndNceHd<%Lod<)zN-2-j}?}_dN?+NdWR)KehtFl#bhceU*oP`70S6d&TP2pRJwa+;H0RD*BH5sS!#K#c37L|7`zVsg%_kDFNj_26O6Ccd6Sc}SA%lB365OgiP6S3OpA#fF9)zR8;hS&~hbvPha4c!6G65A2223IAv3%Vn`GqJtUUEn>5HAVM=l`H!NE|;YBVdd=`fy+~AANU~ZG)8ZLZwy?HHh~*Z?#;eU&>Ms8xvqVCp*O(|*|!X>2lt{*Uvx5DMxA}pePG33qmKAP%KK8M4!S$6_!R1hkIuMq9qQCY_lBoX=XG>l;J7Yz4n+5Z58(UsL~n$5qu&Rh4d9yeZ#T3ayes{viS7f};PZAxcZX}yhZ^YK@cx{?TIhc8^_-9W(faVK9QW(d8{lIz?)bjSalQ#YF5`});^%hEWNTO1zPNkd^kz5J=}<hj9b6y%zkE0l+|s>IziV0TZTCzr3y<%4VX>`fk@&eCtA*E8w)meqbhz$-!T$lE)IOv'

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
