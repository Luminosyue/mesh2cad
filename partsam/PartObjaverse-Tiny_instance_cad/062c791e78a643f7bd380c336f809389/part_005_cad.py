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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_005.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_005.stl', 'source_sha256': '80b20f12a94b04185873430b7888de0c6156f5dbf0944c55e2871ef732eeb18c', 'input_faces': 1241, 'input_vertices': 744, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.34715840220451355, -0.3353263735771179, -0.3421453833580017], [0.49857237935066223, 0.30191904306411743, 0.34216803312301636]]}
GEOMETRY_BASE85 = 'c$}r23D`~5`}fcDXre+wrg9`6Q;JlEcn%^nk)jNTNXkq}!cHVI%RF?<ndf;p$2`wNrZ`BcpNf!vrTq6=`?I&R?q|RM>%HDr*L{6IzGv;V*IsMwwbtHysb0-=_hbz?fAR%-rqum6R5cJ#@lYUZ;KSBky0v|~b=Tq@I`v2jWY)g=<Lan74QtnHoD}%bKC)Hou5WiqDH}|A>7CLk#eymCbnMctON$Q8J9cT+TKQF5wCmd1_Pf5@qEl=8?}c70RjOF<xx&SQy@LObe=^ubh=2Ry@l;!_^7}_dZH?sXc`WMV2OkV-KbWnI;fJQgj{5n*Zf_h`8dz0T`{6<jCne@DeK&vCk942b*Dt;6yXiwWUUBlNP;*jZd8F@_$MxNOWO^@uH~ni}wIArdep+IAr0<mn-@3E5pkI2|chg%Vx;gpuT{SJSJkoc|<NDz{i;DWCcYQZ~yy*m^U1BRP9rN?u@<`un-xjl-{14`vX!Hl+%k)-C`u>UMmA=f!^}T$aU+2_A(W|qJ^!Slg1FY19dX~Od&t29#`9J@kSw_7H->YZ*$i=QYADQ0uy?(xTpZ0@UhfX#6v+&(~T;DqPYOBQhk-p5w^}T)@c=%ggKUd4mH2R_NWqNCD`>v@8=as(9$MxNO;=S@{Km7N!xrzN;`d+`n59LoCmg<w<^}Y7W^SG1GeN*Nd?InD#z3@YIiw;ZmN$>h@`tbKHv>)Hm{hP#cO5e@L^{qEXex6uw(wF(TzL!s#kxqGPeX}63-lXs4gKs^)d~~W$de`^*$qDj#WBLN4zX{*#xA<1|$mmp`^seuwkHvO6_5afo^AgJ`eK#N1kF*~<Jh9%SFY|GIuN~{;JfV-Tc4bjwy-DBeKd#^G!lI~OKKNe$!4EfnVuIg!T|Z6wr%O&q^(l|*d-u^N6&!!`qelBm-@8xot!>s<#(gS$nUCvx_vxT{+K)dmYq4>k3g5d=UBB?u#ZkX}@V)s3Km7FNNq*;b{WR&5Zcj?}DUa)W{Xe!*`=JXp7e@aV-@Cu?t>)Lp82730Wj?O&_1i;7oa-%;r2DhiZ-pOzd8SkTH!Gjiezxz;dKSJ{&#oUlXV$auy?Vos{k?3VUp}rc^9grqXp~?2vi#PlO=DAi(!0Jquj|Y6hVmYt{J;6~x<c1~nr!q3;d}G`S36Jo^#|#D>j!+<AEYnyk^Lc1^z=!;`$GEOxQZ|D3+cP*BfH2)+^5oa%jx>^K9atdzD%`K+85)G^xbm0z8rs~FY}S(Pq<Bc?aOgk`rf>ZFUMi&d-Z%@2PYpfFG$~;AMxe5Eq$*)+}z;!V!o5U*Wd8vd?$UGkDTw~-(A<foX4f_-ADLx9+$p1e|>Vp$w#b1r0>nA_;MX0eeb$D6*#T?tyo`4->Wx#xxSLV%qPwIYJ6Mm%XOplz5a$T*NxKm?$hJ%Ir)fnuk^k90$;9srSGL*(L?)kJuiLlKE;>odFji1(yZryTCIKg{33msUOuNt-)r9syB%LVe@Wl1XV;g{U()y5#oFW456_8SJqzEf2YmVbD1C38aQ&RqzT){;`d<IRm(RJ<_uBD~D~>Oo$EEMp|K==b^mU2%2GaM&2YmV7K>A+&2eLZ(i1!}S_wGl0`QAhN-gvU9f^%N+-bVV~c!e+D+eqJgPWd<0$w$0*lD_xcfiK@XN#ARiNbNIz?IQiV<8vLu_trVW_wvuST>G)xA2{{Z=X|MDKi~R&cA_85kmC3U7fp-$`Mp}MFw*x~;gtJ8?GaHQKbXGR;>7gv4pW@;w|?vF=UY|I&NTcoEu3{vi(|{9K7R1;j<Lk_p|w?<e0Ka{l;8CO|Lt#-KmO0QBf9?AO&%Kc^OtT}l$hS?JI(PA|GqTp=idlK6VrzeeWZQsorxQwK7MHH(XB>#9&4`sc!yf6qdtDP+S8kj>peQjnTM7gT_5%FLo+%W`G-4Oj{pAYl}34n_Ho9+?cFvdrjJy)eMpz*%=Il%KmV7%b{YNZKuhfh&d=E#_3<M`7wt5zxACrny8KOZZHxN(9rEol@^3as`_^BpcSL>s(1Wpk#`Q+iYd<jkrcr*^k1xAzls`Va{{fx;%%$y7A3uKO%3dS?)93c;bZ36q6ZP{){r8}e|N4itA6VRMchtuZ$4eUNLlr9Obn(OQ?~VHTLrWhr^8YN)F6GB2UorE?4}aUk$Un9rm-a(*5ABco_>rdV4jcJzI;iX2+Bjuj)W?tic-SaU@T(hJocs6E!KjaK{dD<=aetK^q5as~>5cTRAGq?6kv^QG_9mUr>^(+$*N@fOZ{|PdtC;r7oj4Hn@k6tIGp;xGWd5kmf7iZ4Q6E20|IktMdPDj?4`#`9DC*-|6S5fT1LL<X)Ad$;sgd6GL%%II)6bo${n+?Xhoe4zAa%?!qkig_)9dh9#wU&Rt{)g%z)b&prTIEtr{|3FxPBn}3r2aYSmznKoP#eI`MZ8B>kmf$k$z3}xNQBK!AS4=fdLtf^j6+ttx|o`yS_{x{&CgEsXpa#eOVr>XeIrep60rm*3-T<q@-C7k5?R*>Q|rmvOcZug=eMuw3qA4_Od#3(!T5ut}pw8RdU(#RG<Fl`m(=SrADqy_36*9FZ*-6!noC1lTI1;i|fn#C0r@}+El;$5kK(k0pos*eLiBNR&l?(zP#UK+uzdjs~k^UUydiS8eeSDz8J4uUyfIShn@LYj)$%<$4}Rn<7D8-G40E7*c$TJHho?(o_oF+&jSx_-=S5^7p^boi*S+g&ipFpBiEPn(YXqGeoZsq;mi3hzHhISUd*SiFV_R%s(bbEa=vzbIbX+Ls-gd$W<B8gay{^C@BO+wa=n2s*BhZzOAhG##Cpc_Mfu~;H_`Pa*GsOSX1&zY=^t`E=K5*YV`s|h_Ll3qNVJ^x<vK9fqoMZYdeZgfdNNp~kK>E=s^^RKYGmd##~15i&mX_uSP#d0=hOY(TKJo>-gbSt-j19v@AzUp@A`5*AIaX+xv#|Yg6qrYg-F4XPWs8I#`B2l%jXemf3hAg<nxZ_i|3utjQWl*o~JzDeV)p9#5r%_CC<8K$V8|A;0N~9aQf@u*ViQap?2Tvbx3^0pX-eDCC=&fM(mY|3yt($ET<pj7`r6VkIegPtv>IpAN9H*7_9i6_PZa^<9@hLuSuy1er&}q?OQL7@0RFWH8wcu8~;4V@GDGl=8t7hj!euyRP%EupVwkb6Vr#+HE{f=`^`v9A8YcAlYh>Rs}s`)s{iDy=ku>xWaQsxwf18z|Jsn4KC-*H<KI(fMPmB+NBOlM9K2wYalKVL>G>?Ubimrg^nu0~^td0}kh;}KU-Gh^KLQ#1M~(7qs;d1^*~Qz9^p}e0@jY}s_vXa(!K)wWaXG&5zdMcc7bvU8_t2giTaEPdJ3H(4VLA2~^*L+iPF<f#T}S)*;r`nuB>KTxJ+vR`Gq9qcZ{2%fwo(68a%(@7sqS{8|LnTutpCql9_8mp8b7eaC{M>d+7BPdJU;5<M;g{Q`bqF;CFeP!Zu)&j{cOFV%V8aBKP&3zKU8H^V){^qgL?i5#q;ho`a`e1j{o_QMSgy`(T#P+c^h_j=Ap`&mqdO1_=#LbKa98eX{*yeckVatmu<<~5BFXhGx8VXgXa%vuKnOg>vkFa;o8g2bJL14V^V$m@YJj0jeb}zzvG`f@R6Tyy^=iBX!krDb$_+)l=v*_<A>*+pKsLj^{*X&QH?=SA3yZl!i7fuYu|Iymn(G8@Wps2{lJLDn~n3{{7XOIg<G_m6!r0~vMI}q^eKm(=fP5iw;2Ap$DH()+susm`CB%vG}4Rl+3U|kPHW#fojlvuA2!VBpMfU(oafNY!9B+HigDg+uSv_D=g@}hHu(BCFBs#MwSA)YBX{;2^&I-Pr}o1Oe^_hyVjl7ObH3wx9TO^X#q8%p%RB3v$7}30uJ=$;C;iQl8xzxq?`@{*E7q-EEb8N1(T2wO8E*TK<F^Tn_4C8O6gK+#|7pI9S39fy@Yoh#r26=gt+%Hde%Cjg^r`C``T170y2dye{_{EKypv~|*M%R677h9N;ZqI2@y%!9e6t=J6xM#cSEEBlc{;qN?-Q%%wEj^aKeXh-1x7w~3Oebt6*uNb*N^0$VvI}i^?CKW)4J2|tEi73JXX{g=dJo@R_T1ML<~Rn)o$%uIZuvB%*U#-)L9RmcyXWMzdq9O1DzwreKDf(N~iuW8uzvJ%mIBpfyQlDMScA6hIPigZ_V$g{n*8Qo1#9xRs6^fBYo!Q9Dif^=|=julbn2RpI_zY2dn>Kp7+Esz1|I+yRyR14_@7Dw6FExv)Z@j*D}VRz&~Ae|F#;}Fy_Hv%~ZX<x61u(j6acX1+^b;mEBlh1y8->tQQM?V~n@1A83Bk7;l3&?&$pk;T4yR_KMsbp?z!UjLm+2@Z=n0of9gtQ_s8Me2>qI`uOnz<JTDJ)1B4hU_9eIGd+HI_!%?(^<mEX`0_!cJgy&p?zmZ=@8&z-uV2r2*tlPwDXz~KdFpp#edzk3{FX6~gfsjzNBeI+Y>eBkAFlL>v91WGd)M(lEN;#t_<>qejQp*oopgH#mN(dM^tX~{ocC|-_b&4D!+Wn9=e4TTaniqEe@oQI4}Q{kmyv$zF{j@zO}{wm<A-0#x;`;|q{#!$bJWkJjrxoX_*8%YmGh?S$KFq8%wOSh_f6L61`IdO>-zCL6OHp)B?gVw<;iH7^>go5y-u~Z_1@y=hmZF+ulLn|obPMFm)1vp{6M|}MmZy2zu=^wz0oMA>xawlGV5ncF8y2@ek9{K!_WEfaNm6JWj>)jgNOQ+)AeOJ!|5&#_Nxcim-P_N)ODcFe^_Os9j#k8yZN<?>&tct-&tHe)u-KEU$%QF@3N*kzd`NHc1)S_L8@Or#FzaroM}>zRG)tC`m&#g`aIY>)#pBP{WSN{8|C_IzfUo<pVu9%_u<I<+V$mq9T~E9gg%cLH(Xzi8`if4_5LV1F1dc1aVcGPy-o^D%4XDOxcSe{{v|O^y1pDI!?iz}sM}GD!>*rZ9RBXj$=a9WJiZ*~BPr=4`a0x1f-mQhNP$a^Z{0NJ&B(Q-dOauSHP@H(n)Pte>AE~CpZF%~<I8!|DqBIX|E#KC8t*YYU(DCxU+&TCyvS(Fm^WSD8nt!0pD))5;dGa^FV`EcFV`F4(ZA~VHFBNf`f{BUp7_~ZeO|GSa(%gu3O5@!Pq*iumS0DGe7Q~wFRG-U8zUp880{6>IYvJpT0`0x>qFO<>&ei{r}X<rxh{2mxh{=d8K>X($#t*m%XM$W+Tx@a>uT4R>*~n0iO%_!%rl;YA{nM@U#|aMU#|ZnV`gbzK1X=IcrJ+a-|plio>N?3KBolVs;%F%$mbx}m(M|wo;|fMpTAsRK7R!s+oyf`eCPV|`OfM%#pxg6FP27qeEIwsm^y!%Q~pBcI{CRO`a4%7(^=!W)%E3btM$RJ`u+^%T(ThQ<ICq_>qG|q+#X&&&U{WUm!kd9u2mcSeEB>ce*IxR-o=NHGM>lds|#yizBllE@!lYOaEjxL_Z6Nm-dBXfk2>?m(O1lMEWUgn629F^`|`bt>&y2l@!9w2c~`!-aeevTCY+_3_T#Oq?>5r+TdIBe9?A9Pd!+F3U$rmaQ@Or;PZi6yM)!j>@4@ipd$5po+wsMFHrG${o^4GD-CsikHy<$47yiikUU~W*WBhS_`93gyHKP9>e|3}b-ZFBwxbvM!zK6t@?;(Tx`fFdl=X8Dfo-^Edpp(960rS0O?fJU><a<}o7w=sIP5;t<{GNMu7}xt}U)|5-dtld>?}4rQi=6Ma;yttL%lFKI{fC|Jxs6}jYt;Y5lKMWh`qZuL>x=i^*3D*)FW#%WzI?B4{ar+Vw~f90=r*IA3$JNEeCE~NMmc*t?aaHaZW!yFK*tN(kC)G9uDfddtN$J@JjWPU<DX8|>(|(!9ovlb-%Q-?)K6#QxgdTZ#rbaga}DEukB0)zci2B_ne+Y=-JN=@J>Tq~wTn3K<@fz&^ut)LLC*KtWj`7HDpV=E?oZ+ScNy!e(4A)5w@TMD->>G~>ZISbbApk6?@i}>ZlzI+jr;ELlKOrN|5m@fk^V*v?OS;Un)h{uu;U+_KT2Ou&23ITVxMFhpYM9EFZW5N@%e7(`C^}>^xf~0t}pjJO5goX>iTk@q4eGF!d^aNpP}^K@6oO=_W`Ey`EKszBlh*B@%fJL)w9^wCw+IHfOlPD-(4D?eGaZK_tB;C*>~ZcSL}<EzPsPUYe%uqP5SP>6tA3O-<tH@eQVx%#XdCYyZd%rU+xo=zPs<pJFnO$CVh8blk3ZUU($E?S$X-0eOb~^lV0qzl75=<h<#Slm)9%zK}lcMr`*>heRp4z*Dhk8lJsSNko%6LFZ-L^N0i1F{aNk{O5=<BMef^?zPumhzMV9_xZmYIoHV`|PvkxsZ~PJaWW4)M?30nc91rEb6zR+HR_-&Az8ufxK9e-Qm@ni$lQcf_QE<}bbGlx#9COC`KF9U@zcl{$hZZHKk53!w>;qqMb!B4uSagW9Px1Xen-bGoMY22lE5i40HS&KYo3jtEbH?3?=_3`3JKwFl-Mc61<A<B~KWL;+n(BNfopR$q)W?r~`_EzHdh@^P>_?qe@le#q4;86$)F}U^cFsOek>2%X`f#=-`n``VkL%0w#D@Q<`%_?HI^%j>UtVwgyNmjMkoD>MvOdFY-gEYkiS}}R*<SHAOPqc#`h(}I{!q{Ozt0p;In``_*+4)=`asseJ1r9a*E7mge_ZwdU(d8H^?&uho+(kXREht;|MyIWv3428*)h|OdjjfzmlFuwi#`mmuw#ZDE76&7fMb%-d*Lk{vlU$l-^Vfcqe<`{j@gTDg)?$YCiH&z0LL6e_ri~J%oAuPco)a)Mi0WzaLlvl6YwUE*^KUnU*eeZ=(F%Lj#-XwhHG<79ke|BnjLT3(GYC~Pb07C=yLc?@_Gxc1HVFE)zF6UX!06^PKP^@S7-DsxGZ^<L#x4Gkk>$T4BU&ndZV4;r^%~0S`O|>UZ0=?;X&l}CE6QSeN6S6iRd@*SbiIdPJ{>X+o$MIxEH^5LqCN(@!R`oH~39{YlglL*XFlZ(Pr>V{Pr^XD*Oz;y@<XHKhAGO&==v1{8j)h0_O}k{XQe%daA#xdt?ovcmcW+UI5QQXTo#fN$5Cu5<Cq35*`NkMSH`2;SbQx@CR@^^ewm@+#Ia~H;3z^<>C5p74%uS3S1g}0xk^~MKi%g;ezP>a6vd1ngr*9v!VCG+2F^}hvCQI{AeCHKU@ec4i|!-N6W#_!<Eo#a3#1d+7PY_H$hv$P2e`@CvY3M3px<)0{213z<uDs=yZ56JRV&RkB4WWo8ejTJajia4_<{Hgjd1q(7mwIHE>Hi-m{|x+7@0%n)T>fxG3#i3{8Poam;FTJzSb&%Am#Ic^oqzT@6>^n5t+QcoxUZM(4xzIi>+x6>dU1HAUZr$CK9tbT-_ayuxS$xGs6sLz}{b$!iEY0d7ZL?a?q?iM%SK_253_WuZgh56J67v_1ShdA)#EhP#kgSJZ<0lGkVGhj1bCDvZ7Ww;`{0(XQ|?@*0kQ2InWQr_jRiB#xPk4u>D(m>lR+@Eneri%y2KaZGkJ2fTn|7NT?ETpW`d%?_{On6>CaSp8A+LRK^<+}e)Ux%PMArf7AzDO?Y&0M~;nqb1<V@C#^O_yxEyni(z(KZQO3KLzJNli?h2b~FQ=9nOtrfpfztXg)XvE`~k_7lX^7A-D`&6|D(Zg&Uxa;0ACQ?Er`2_Gk~dJ^Ug1Is75~89EC73?7a~;NkFObO}5eo{L7|x$r`C2fPqoi|&Kh!t2p(@OpSPx&dAd&qo)*^WoX(6nHi~0UZHPfQO*{;32Suc84vvE7}@X`Yv3<jyLQ`B@~w=6bA{#j}VH}6N=LjiXS8tKT0Tml2BZVP+XBvT#HcLm{8o2Q2a5WcmSdJD?;&9Lh({Uag0#BlTf^$P`sT`ypd46m{9yRp?D;rxIdxzBlI1(HT*jI2K+i)9jyVYIaiHwDQIrEI%z7Psc;3j1X>a<0p~@7a9%hw`UspEegI7mKL97A>EL8I1NtDG0nUOx3TJ`yp-;m3;OEd%@N;kotq6zUnrJP!Cfo>Z3^#&1pdH~3a1ZojxCi_>IspD09)*4dkAfrUR5$`JL6^cy;3yh{qwo%NC%gmRhwg{>!Q0U7@HTh@x)I(0FG3f?i{L5f*YFg01UeEP0rx}u!~Njy=tpq(z}@>m={s;$y8~6WBR?91)7uXc_uBCwq4<6@3BDgrhyD|AI30W^;OKwhJMiD=P55v47Wx}}3%-v20$+!(p+CXb;QyfK;s3yw(2MXT_($|4{3Co0Jp!MDPou}+)9`obA^1D^Tl6seEqnq!4xfO}qDSGg@EP<Jd<KrA-@|eEGI{~N4F7=s4F3RML4Sp>z`vtc;ospK=pXP6_)qjN_)qvY`Y(JNRu8R8lam})q4*y3KKLH^0W<^r0Q?Y|8GZ=Ph-QH^!dcPma8@`6ng`AS=R$*UF8FcuN%(R2DYOv$6kHH31{Z{jpwGfZ;Ns}>aB;XKS{g11mqK5HOTlH)N^n`Y0{Svs0S=+n;1FCDtp`_yYoWE_T5t`t5nKbVk2Ztr!>^-F;Md{T&@lWO{3hBQeiLqtz6Cdi8=y_$25>|44Y(ovDq07A6|Rofg{#9g(O2M_a22#NTm?==E5fO8d9)l{9xj8v2$z9hK%awOfJ>myz$M_P(W3CvaA7nBE({ky^T7q+{AgY{Kl}um8-4=LiDrXy!jGYkz>mR?qM6`F;fK-mu+j(N7Iw6<V+cAOe#eft?O2R{4Ue;<CC9ZOt@2uP%s1%b1a3_pZ^Q2KEjedPe8soy_|}e-@G3i&+cDLSDR#urC>$kS3_WDWemgGOan6pP(I4O+NcS_EpSfId1zS_$r)_-(e$v(=aNcC+?~1e9nmyUMu9nnMOX}lmuBSD1+M4=MoYOw$Q9Ck|PkLMLB@{n|W`;A9Uh#c)WU(WOWAE5;PqGt=A4Jvf50WkmJk<85*)gB`RrS0Z-3IT5SD^FZ`5deG^CTy)8PwrH^7t0shOURV!Sm4>@C@=%+|7;;?HEX&o9x&^?83VRA0T$o&lbbqpj+T?;OXclSZM^F4i7;G!UHMK5YBsmYdQ$8M;F8E;Th=H@C^8KLUC_&9NZiJ2ps|sp$v+<P)7qO&ql6e6C6P&!x4BOIshI(K8pWi$9H!8j$Vd;hi`DMKkWF8Q2Yye1HM7}Ur4Xg{Y)sni2ed!gwLRt;dA_U96bXsuw$kj+tCg1cKC!Ht4X&9-45@8PoXDZmG4f@smiRzh4X~sBj`E!9O;jstKrq0;|Q^bJoa!NH_ua?=M-gd`?KOh=!T@b<CoHT=mvNmJPDl%53*yn9fR!{kIq47!*k%h95bH$#`Bw-{~XRghqU{Ny$NMjycL}d-$G-A;;HCtcs6Bq$8x1#po8F%b_};;DWP}~It*R}FGNSc3*jZ`D0m6H3>^(GgIC(I7M*~Oh9|)N2*sbGqu@{BKIjOz5Bv!_4E_ZE7#$9O4EIDw!ad<$=vQzr*h0s^7Tgz|2=|5iQ`h}zhyM6e2*vKas&pMX5uQlC>qw(?6*>kULzz|)ikG7!;gPiQa$+g@Ev1cbp$p-KwB;>y8N7@(yOq$EZeLZrkx)Dtod8dU2cZ4n0dN;WaVPXsxD(s~?E`m!+o7Mp?cn#&kKy;=chR2kyKoz{7u*JJi&}77_<gi5{65?s?GLwyJ0{)j6CDY~ozX#XXSgdm814#xkaTwp`hZZ}9i0SshkKwi;U4g3=mPjN_)By({3SdV-3gC{XQ9X8S@0V447>*3hhB!2eh2@X<jj}<Bsu-+ze&y<_y>Fg{Tsdk|Bn6x|3f~CYuRhEm+dHnrod(30<7_}*_x41oChrc7a)Be(r0A-n4V)Yqj})Wa85KO`R<zZe%6^vli`Qpd(l9`dNq)I_g+){U+O{e-)J(dLh(Q7{jdtf|5DG2Gw}PPa0WORniI|i7eiCv6zWuQIN7P|ij?&+>QBXE)SuGAZ~?dsS`n^DK8l~Wqq-eA(1LIdI1}f3z}ANe#ktW;a3<2{CcR3Rl~DW?nj3x!E{zt1vvW)#^eMOy970ROui8<<jvD;E25D>HyT_IwZ&fy>kMs8uu=17WB@|aeOTZ;KUnR65{3ORzK`X(PNK*xE0jqPV=dh;<#kC2=ub@xDPjcKVXbZSD+6rv}zhp-fJDS;1-j1eryk*C0b~Lu*JwkDN^ewnO+!1XGcZ9p3&EYO^H?$et4ep9IfxE(;?PzC513TJM?svGRXQ-FDXl=MQY3ibF;kM*cmuQfD_nBAebNsyltbC;}5Q-b24d4cpuMye-R>!Ji$`Xp-L>s}4NdG3<8Sc!rzezM9k0!L4o99c(cgG^d74VwD&8X`NgyK}RDcqE{PbJDH<f*tE-dpfn^n-GwQ~Dx*ZwxDa4OVHCmg4WP!NvLQSyXw?5{m1gufg@;Ht2hBagM2j)`RQ7t<g5{>vmMLqa}ZDN!ph9?y=R#TWL|aIPBJs;{1f-s%SO18t1Eu)`zRYmC>58(vomxIEX$02Vu7iiXS5s7e-6Mh2e^5O}HW)CKSJm)`#DPJE5<`o!}4Amhgx0M+x=&5ux~Fv<>_*{0aIV{0ZC}Z4dW`Ewm$S!F|y#a9_9|+70dpe~xyAKZggPo#6p+f3ySKAN~w&2Y&{CinfJ6h5MlIz<uCeXe+oE+!Jj9_k??(4dEVecl1@bJNyA!1O5PhKl$#w_&%ZdZL~D}Hv9%!5LQ|p&X?@071TR8)j!pHx(5iwna~H}OmGe~3!H^~6sNP}5j$?v=l@J{-uc~u)jL0>f59pg--q6Ym8yK)cZ&B>-uuX3@zo^feAhVFP0sNr{1<v1{tLd1UW2cZkK)aC?66~QlJibc=?ZiQyaL{h9!|RZep2yCG!CDHRT+=jaoUcv=mq#Jd<p#t{)yu*p>g;Ud=@>Nkk4VxbC~iSLpLX!|3}Vqi*x)+D87PTfG?2#3h95PUT?zJ(JSzE_!{~nd=0)zDE=Nj4Sx?GMUTP9D8J%Kc3Vxc<G3AT>=<Xq(PYP0-UK^F+A-XY!*&d|V~`yO@s&5!j!||Dv*QS?bc7v~?U-oCw|0!R<Cq=e?O0^T0z1C5V}%{d>^Nt~Iy=_bao&zic0}#CXvZEq_Sx~H9WgsD*s;-$g?22q<BT2C>^NaZglkdP@s%Az>=<arAz0~`ltG<;31v{{Uqu<z`8QAob^a}OY_(&D9hdA_ZpT?WmQqhsIQJCJe}eOm<M(mY<#Fn4IKL04j7O={LHs_5dOb|Neo38vN%<9zrjC!HN8n@B_e5em-f27L*fHCVnRc9nPx9MrRMp8mbOC&hHu?@-0<WRY&ZFnxi?rQ&bOU^eHr$2ogTLVV4-o_LRN1E6G1ZQ*xvr_`N%#`&auMAE$L(03?DP{A7x2!~ek<)*jkhx4H^r(yE#~iwX=lZ!?D)oxxpvGa-CXn(tlD1n#Tj<Y!k>YjfWNn6n;knTm+I4-?byz5o6!sKUORpu{SW-+@@_l!Cp+H+RoOD3vtacNaW22lrTmK3H%E01+0ePL`bMeltK8^(Sbft}b&(fc2&-?Ps($jJi(&Q6RMm3|x)fI5SXCVtMVG_so2+V&XV8_f`i8qU+4+4fZKha#^HuHpBDxk<--uOvmqXXX>YK8v=Zfe?Sbc+5bzB*Z!Rni}YL8dY&9M5$t=g_Gx*b;E#8sQrLASx`8@g)0H_)B1`sS|Mt|__~R^RAVd%lJ4hSfLy1If<s2WWG}Y7c-KAH(PYSnU~5_g52i53KeWsC%v%x(`-+64V&i2;Bv%Jq+r;s*P@i)t(1+uhm0$z-o_#8aJz<TVS=PLX8D4qnlv02SbeymCz`x_H3xJ_$71$toC@Qai=u84pw_Y)EM+Ux&~HzNYwcLEV>F-drs6?Rt#MMt34`ed@F=5gVmlEHD^4DE`ik^7&T4?(M7P@Go!}NJm>;g?XgkgaCUSatoG!nF*pl42UdG{)Oej4oeir!KWc2ufX;-~9w9X@-iJ<y)t(|XhN|C{PKDJTBsEX}i+&BOJxgl-_zRs3t36I?PWc0!2&+9&YL35(j)&DADm7RAijIXZ1e|&6XLK~I_Gqa!#07K&toC%Nx$t{*6s-1usd@1fIt*5O#?*X&6#Wubd(71QavU83t37FI&N++@gw-B4weC5DegUgJZ)%=Ch7N|+9yv94A3+DfYEPY7Go3_-!si3dI^ZHY5>|Wm)Y{-YIviGe{M7p9C-f^=?Fm%tj9<_(u-ZeY)*kBjdNq@hv!=WI4_$kv)crS9)qdWo>im0A_mBFnU_aTm?$WI-|MFEHY5o)0#3Os#d3pa}wqDJ9^}iWSw*OQAn5^}u>Tmx8v?;GF'

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
