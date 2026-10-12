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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_006.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_006.stl', 'source_sha256': '566e434dd7f1eff1564c9744a7c889ebd72ef0e03a525e9eae0a30f0364f21f0', 'input_faces': 771, 'input_vertices': 452, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.43072235584259033, -0.33731770515441895, -0.31684011220932007], [0.14379267394542694, 0.08728590607643127, 0.4999997019767761]]}
GEOMETRY_BASE85 = 'c$}r22T&DB`|byG0K*#A>=9H9m|e^|=751UXAc5`Sy53`bVS6A5d)@!D<;f{ihzzeCroQTYe09!wCnmAR{hiO^YFpmy0_}qy<7Fx^E;1CPfz#TJw1I+t*1xUY=t%aS5A9cvgTxa6-`s&s1?=%eFMf1_4XZCebksB2d#kk>c4bd*11O~&pr-Xpf<(T$9J4}fNMjGYvUpHUEM6MLq-RT5AYf_Xmo&&ukzb?jTq;f=8yCD8snSxxl-MqYP(tLRCcojTmB#a%ahgw<Ne}$M^#&{+_ovzTjajdOzDx4^iM^L-}p|l@@;$S!~gJopXiq>mz8gJtO4KU(|*yEZc^UN;RN65hSYC)H06x)EwfYZia%h*Hl@~OH*ZS)=K{qynw~l!*G>6ReB=25_#qK{<?jlGo|AUgZGn2`%-*fkoOt23TzAp2JL20b_ZR(h;8m$-pAG)hlo?VkWxv#8<_m>?f7wE*=j0nx>VF>$-+VJq+T(HSy42I7kNC#*Pts1a*HF2x{-8I?=XktI)W4+o_S9Y||9j~@a=*PUoR;ej^+fsLDchxgayy=sdYaaSA6h3y{%-B;JE(uluk!iZOX+9puW!-+A>ra{sm+!(llyQz(M+xr0Ds`hC~1Gs>bS4%zNqKxco|3C?dEx@=TUi-KieGrpLdm9S8JRLeoQ%Oziswn8Atuhi`(Ms?fXi5hDOB8b&F4eKku;QkKs1%p49VwEd0^`k^416*USAHJqN%axFkaQt8l{vY0rdy@QVg6mipbS(jH4tWB5K3=gZ%J`steFPly}K&s`zcwNI1w=m*NdHzNi}`4(Sph?aJQ-{J6Dx$bG-3)0TBf83J4U)eQQ)bc?3+4A`;{8}R<5A6kw3uxzd@wHvoHp#y~i#sO$a6BA-v7wWt9kJv0i{ETE{r6J8wtlblkGW<T{8eLjNj@y{J1gaDHiExz(<Z5Be5&-DRwf_(EgjIGcal!YeWgCWDecJqtBj*|u<EZ;{#l~<+TwS!rF`uMv2x!<LgC*!x<STwL1dD&=VKT6Yg=!YcJy-=U(ZE<()M*SE~Q)^h`-7e{vQsTrGE+ymORu`oZ(;EjrpseN537;0be`WLfTvW@m*=>iAOh(Zwn>=ZENSsd@&sE!><yzO3KCElX2Itoq^was;mP>_<rd(BOxAs(|0I;*JZC<H#!D>?>>@0x?hf4QvUfI@eS{<lIQligXF$!;bAEMyz?*e`Jb?h@^{|DQ2vcyoXnRJPcdK4H9`5u39F@^S)PX^f36jU|0+@DqgLpp%tviYLHOslpq}M_NPEnf-0-!EjpaHmJ$A@-mtDFpzC#yTKlPdQW!&|MmGDO;Y?sfG`J~_U&Hp50y!_V6xEJ-2akOoF0N?+htS9ExX_6;K#ar+_-_Di#zk5EEcFv54U#R*nxu3vBN2UG}hu{akmVDMfbisT#*Tc_IDMI{|?2`Yw>s<KpbFn_0-+5fh@16sH`H*nA|34z69{p%T_!Yt=AFO3#r9HOs7Wk3#H_G4lpC`{9y=rOr*M@8n|Hhd;qC1`7FP?z@KQ~kQ--!8eO+Fv7u90#NZODfeYv9M+-70?Y@k>(wnq}}?2g?1LIS<OX8;6&`&(&m(e17LF^VOI&3x2?`m2$sb^usdm^mA9mf0rBUaDndk<-Q8U!MD%cEuWLJV7+~|3VxyBDCBubX}`@S0)Fy{Wuo<(%HQez%D^|<50gB+X?-NVB`f@p`?B8Z4)M6|-!HEq&!%9W6ul?oYmNF%e63VPX{YJ#EAvzjn+X3B_6g?xRZ_osavb~=-=#_|;Z+Yx`FVNa&-h)&OV8EoHu~TBviMKVNI&aMyUTOdoY()7_%(i)d2MZ&2kXq^w(u9Wm-(PoJ}mcZom2yUu7#54R<CJTuig}c|3H_#H8*6%KIf_RqWF&O<@sVPoQQmR=?s7W70E;GP|FQc{>A$X;*XiNK+4w~Dfw)Kz7*d`ekJ{8Og?%BdDju;Pj;4ZvH91KaW^aFfxk9*o%H*)TykI9?1SgUw><He&;6cYyh?9?Uud$d*V^#8$lE==;p?@f-MY&$^k*Ln{71uN-(`OLF7;@=d!G}3XZ4*@?oG7xv!&|zv*H*2VY!Ug`<wFoHOAD2zc}km(NnMGezoKI#5V?%MxKPPm;ThIHaa8aehHWPX6(!<|E~X282+j?hUoOa(9gz|)AD)vKDjUJ-ZpsN#TJ6!xy))Q*RoNRXt$TA#4i?#`Ces<<gM|28GKuq?9;3PGo=02wg&vtZZXmh$F<lW)(U`s^0&ECZqa<??U_E}8_t#DWPT=9!*hIhX_UX^Ao~hyYO<8Knjt6AKYfPE{IwrGAb%I@1HWxs^uvYS$Y;j`C&aI`T=LCw=ONb5JNd;orpN4)^3zhKKkeT`j!XHvOT^bx4oN>*>W_i1)y*g6J?)a$wii2&Nj+anNc;6RXQe;2MQy~_jK=+>-T5C%9$L2k1ix=T>0hJ3GkMP2x4tmNzjseQ8*b&LpDoFA;eY(JLh9*qM%H0V`*HBMbdz>y&fBpcKG6ie+X{J(7=PA89yW9p-$>{x{bgzVTKd@>Jo_l-W5j%=_Nl(|T(EoWJtBUN>5@-c-M#3~uicWwZ|o`idF|pJ%*VOziBkWoc<gWdugP`v;`!mnT|__DD=qH@_O62yq@J|Iko&569^>LTIUeKHeyV7@1li9RRVTr3A1(U<ZLL-A+g{d5e50Bj`O~x;-cufwI3(roSC#wH3yqWKvb}A}LGf$v!#d#nMAiW_YdC!SELpd0{p#ZRn>-l)h)LU|+>WpEe6-%3C;L3()(GTV{8r@ojq2F{S@$iL`WMW_bI0wH>@$pky`^8w*i`9fOTc{bwf)%*@l%4uw`~rQ{eiK$4DvAV3F&{$^DFkRjtiEE2DFj)2ulN3_-;cnufKZBb**7ecyC<fh<)&+ws<d#DuR7s{}J-M)H-dD{xi)&@U4;K<huW?m3@x&a5ng#t4P0T&9b21%8r+Po3>}dXleJ;7kIASbcCOJ0M9#@b+Ue%#~<z#-)pQ~Pb=I}+OKtdD*I`z_b6GX%%Z;7hlIS}D!zWBxs0QWJKi4;{|0~3QR#o(&tLjqyLxwv_)kknzu6K89g%;(H$$G6TE5H6#qU;8_VcEb6@J4W(en4PPI!L3cY(iuqvXG>`)TC=w%qWO_hMbn@lf*9bUFG9@+7~kZ~888?8o|E!M@?K1M+`qr1ZbOx)%0Bo(+e~zdO{FeU8?1r|eg>xZ>Ei4c><LqgDp|-$JpDH;ll(H(@CJ<F}SdJH0)y{`jWKK0wQRSk@D><UH*6+6+YAbd6sk<NA0T>UlF?)<>;QRcWU_sTH25|BRRCuC@!$FMW4+^s{ZzbZNI^bF2@QQ{=w1kDrG~`DNL#ugL3h=3o9bXY2>IUPV41iXSezY1m3>|E?(1-{#j4(cIr<Uu|smM*mdrh4<|-g(VNo9M$B!Li4yK<EnMtkN1V_-Q_(+tK^RNkXsd2W8PK7bzgf&iq4D0{&af{?E5zrkoQt^<YV}M?ZN(jhBMw*pU;P1qzcO4n1*$v_(k!}l5OGlNrE5u8s$$_Lp@=Y)=M5Vng@Si417mF@%8u^`0gyff0_8kW9;kopIf2+vR<-3viJOk^7Rix53Ug3uot|Jyt@YNmCq*Eb-;UrG4ddEj=T7_YI$+Jzq-P2(N}!qd~5N|`pKxj+Gg>!`;AfWlQz(s$>Lj|96-5{Zm1{tJL<XZhjNjA`1jTW@cc`}b<Hg)vR^k|%@tn{K>M^s*YS5Xx557_82zw~??rLX#Wy>TK>P3hhU>beM*XXuwR+><H@%I@+z)2=7kEz?op)pA_88*^qCFm^#kU0n;O}>5Mg8tWv7eqZ6YXf(1^@miLVT+}F*)=78sAQfZ@;(@^^Xrk{i#>5uliI0{ov()J+q&l4|=O1XlKMf@Z*-?dJn>I{Su8N?=9b}h_CN`CGQ(X|Gwhej}Axu-hZP#8-m2QRzdw{GR8;CJ{vyAUH|K6ytg=<M?FoWQBOhzT-Wcm_(rL*XlIu%xUbrOqMqLq;QPEsJ^8cY{j6sc>gk;Y_jTJ#e5((}*EAk--V77p-r^|yKr8O6!?sQT>IZWj?#neneA~jysQ-{3u3PjZuG@(B6_O8sx9}{kdu_0MwkB`G``DCgcrI=n27g;`d0#SIzKL%pJw*Mp*WrF=b(ZIcC8ZzQStJbi6+K;idrkDeb<tS77v)_TojK2qhFQ>_PZ8o9djrvLeHWu2V&n0AdOJnRS$@cKF|%)eIWOgGBi5q*QOD7q247LXj}!9Bxs^N*wD*6>XM5{+C_m@t&6&qn>)j52=j$!L%{@*&TYI!XKiv1jbH(;I>YZ5u{ou41^{*a`emLiVe(>CleeG7PoAyfEQBPbV>TieqGrMs8DCUHHfKxEq`6wUW-}<_3!T63r{}ic=@)g^PZ=6Cqjs09l3wy$UW6Edy{bADoM)L&m?fLT{AJW&8nkVsIH@+1<hlU`3zC46qzooR__F)(533!6%v0DSI%N4g@&FtIfug7>5ACC9HxGeHqG$wA6`YpTMFpei0i*G&|i}nob#dRhW&(TU#rGCrT9w@(diTL*F$V0u@W%P5ot6MYYq4DDZ_&#sM|L^*It}V2=gY0XyQR}20o9iIFXWn)f-#!ZMu#EW!dD6KN%1`cqbGYM`alg~Ou|Hmq{?rO~NBuW~P>=6U^nb$^cyG_P5%rV`K!2X^3%~av_;+xwW~mS_@1;g{PuU093nJh268(^G(cN+G_Iexo$Ji?UY{Z6(Z>zBi*G<@t{-2VH{Y1f4$ir$4uVnTud62hyXcN>w^l$jP7vR2%<2j}M;Eea%ighqA4*!XK?%rH{W6gHdbL|ewpPeJVb?gST=hjxd=SN41Z)?6)+G7olhX3@Rn9Ti|{(RJS|0w4#mUZ=!Z_!V#X7=rVt1yoKOZi?s2!73TxZj8O(VySP;2h`GB&-`rWpG|Faf0~P^!|)5i~Dkl!F4+{K>NpEMgIShD88+}4eh)Xgm!-XfO?*_L>~I{+^wUN>?3U#uwOAAjX^&LO%mUd)j`gu?eTYz=Ya|0Tf0`qxVr|Uyw6G0GkrPM)u2N1{%?HwB))xG8ML$5d8x<fQUK?tFWbv~nKeeBJ+1DDum7+I_p2W~mD$(0PqTM=hyKj}9`*d(6XQFuBkGypfb+jcpD~Vme`lU2iEp=GMEl2lyZSGGE7mVtowHcq-sF<^8Ow?!%%9R4?zc)_oTt{@i*c-7?__4*2w4gL!x`jr%d&VcYVLvld^B9nr;Nd#;#*hNM&5RxgL%E6pZI3IImn;H)Z>|b<Ax8)?_49-)j!Qb`O>X$Ux)HYJI%Ut#J6?Mhjk-sUtG6fB-(T9Pt2nx;nEN084c%Ic{@uxt&e-iJk^(##JS!e<e}9iN%BxH*hG9wmviVJ>s0jr$(Hbo7eqS`b&z_@U_aCoJqzQzyx@t<zQyW|btZc(&T-<0if?tRk8#Nz#QZn#9$4NB_j`CH#_{6?@$JV);<{aYrGEYXXZRz+(Er;aWquiPUF5yg{-u(%M;}!P?cdZJ@A-YOAGOA3!#Z4NtoWK2&etuc!!YksCgS}zW**khf=M`6vaQ*NdG{UuuREo@Ug0i$Ur&th;#D{&^12WIT_?1ERaK1p+xNKcmwm|pJvgV<{6C@nzC-1{ECmMR-0*yRoRiM4g!0E{V%}x%i1VPxH@L4$&rTy>x{7biZ;o*()l%x$BYbdvF$DWy^IbXVAN}ZP_{TmW&nq9p`ta=<-mAZjfj=!u?#oQQi|fW7LBDOUD)pQCJG3)<O^oA-UUL4WZ~g{<-3qxcTgeZYUp?C4++@Q^X}>*jE7pPjzT#WBzFBuTO8=W*@qMHIH`;Ie9E$mMBo5~V-a|0%OKafV?O}@e_L}&f#P+J4tONRWN1Vr`2BCkd*28&yQ8)3eE*+3pQPZ)`Olg4fO=@s`E|2rR=vLxe7WGH@fmd+u8PXHyWkd1aq2~;jb3J2_Km0};abJCF$aT#sGg1G?Gw6q2J<va;Qqi6-`O(j<+T$F2Zc#bsGVG(#{>?ok56#yu;%kFCqMsX#KA+h)UuMO)U)+fE!IllhPk&Fb4Q!8k{?<`Gmk0W@)(1If)CUj8bt?p6UVof{ep^2h=aG{pA#XoV!Flf4N#fg%Maq3yx;f*#xYQ!F(^4J#*!iR7JXA0H2KBsk$8)5|m&2m<vdZ@@)<)0KKZCPjzhSQ-zGd)RJTKank@CijW+?Aa1oiJYDDBry4uroS?YD)l#QZg*#5W6e!#F<q8SB-q?c&>iS&jBD$%p%z@mPE<=mws%72D!G^yWvj$He!~)~Aop{>u-3jrIpVll4l^Q4ZguPM;#aZT4%)D?PXZeBTJ<$@#ArGW%L+Uffrhi;Sc3zOwk%C@1t=iCCQ5?&>7I>9PfR!uJ~UmvQ3TcML$D)OSWcAAOGcUtpayM_0tT@ULIQH%5lSFL4?3x{D^iN3e9qzSnrM9>22)$_u}pKl0)DF5K@gMa8$xIDvj}--G?qrE=oi2foJpPRwID7uILDhQE0&@_$Ad=?62lE9##ZjptYEQs|%X!6=^>>!I1}qSRw-4iw+0y$1Ukx6bH?wqfF%9u=gWdgZc`hlbxlwDUI31@vN-#5eQ0%DJz0?=;5iR9Eb0miQh<-Y&<uZ|^SmW$kakZ%`EVe{#Zk{hk&0-fY%tv}es=X}{Hb9m;#3KtH@GhI8<{Q7HepJKEDbO6sw8aKraPWBXwooeN2OEMe8fw=J81e%tW``}Xnm5;EtreOyIZXY5Ji@cWdI`slZ-i87D$*wyg+-auZZE)-wexDnr{-9Clq;DIFU2eSSpz81C${gdqz=F1hQL}|}&I8U(;+9dPB8r2&9hH|*C9Q`HV%wiqjUkF5h`XplA$TvoO^Uw}Fk7iGodhD0?h;QLOQ(JLO=A$Jk9_8OI!+UOgX;}~LyYRaY?fuW_x1Xj-JMD4J#J476pKX1Z6VL0*-Nd&{@k0CKy|CZtwiLfR;6B;L`ED9t#Wy^A;XSVL511Dni^+Mp_2V$i>(CsMC-%J+#5cRl#5xn=AnT9SRvmuZotVFm8)F`A@etpl;kjd(<t61UKi(2wtLlsPw|0|xZ9Vi1<vWI8yypHTd1Aj^RK6FoS1XTx9-w3WIbBwKZB+-fbIEzh6H8D<e2=tpG1mXV;pm4^9Z~*4H;iM94fAN{F7a(8n&bJBFA)2;{TJ{(e3ww<|Dy(&F9|QiH%b=4eEDM#z9(CrTfX10p1|)`Z1K_39_uSd{NCi2JMxz6ycu2!ev|8Xek};Y^Q*BtelIr84fCSK9E^KZOY!Y9ENK7U>awm{y9_}2nY&TX-ucM?`GfF%%chZNPc0whXWTG+kKLmx>hC!e`<CS4C_ix!`Yq3QX}_6tP<%^pN94~HexLgOBHH8r1N!a35{%36YxsRcZg1qn)V|2is1(#+yC?GhY^<z%<_HJ*9?}-$hWhL6Liyx;;v4a~@Eq~+!+Jie2)`f3IlJ}8oOll2sfzLioKa7;aO{U2L*bXk`?L8v2;X0JUyScRSJXlObSRGf@b3}g>q|BC!^KEEcUr6#-+n6()|tY?kw1T&LOr=&;rU+KSK4Wxe-rI&o{I5$QwPs?`%C!CUt-_2XFSGTca-mEOxI)B|G2wi9E;Tw-za+x^*`Mp?YCa^L;26xpX&)R2}eEu_3PNa$FnTkR6gy^A}w-jg|#7GnSL6pO!Z&7{_lSpJGAcq)lXyV)vNXY`_tG}4w|+&Edm&dM^P7$N0En6L&-zP1E^EU1IS$&iaSupk~@%_Q-_k9lN(S6k{gigQhSn>wkOvmS7j(JPi;XiPcBVuOfF3>M6F3KM9xXAL{?gsoRj>IhEV*TT9B+l@$VW!aW?+Dg`ACCI4yppI#VrVXL22?8@Ud-3AH|1X<Kp=az|<xaz}D^hGHLTf3niSWFPVfhT<92apW1~+0<#|+2j?}`Q#PkNa_-DBzY5cHF*<x3w147=`Z9h<h|6*<h|s5)E(q~<O9?_<OAgRv`D1JQumN!$u{abvW+~G8blsW^`i!nl?IUg$bG1z$bHD&7>e6ahmhNln^Fgmm3AdJCD*2QAlD|lQk#=q$t9@`$R)`|sCCIj$oZ*N$@$577>YG&d9u>dWR3h;gBBvIQ2Zw~Cs~E!*HkqpUo#XxW+;9{eNTSR`T2;U_%=iFRfgh+R5foO^0VTP8bWb)2WVk(c5-fqjCr1$q1b_;_y>mKGE`@B8FCeB9dZ@&Pt+!4r5(vXk#&Y*4{CR^2e}v3hpco2xfgj5LvbK=23hHBav*s+L-8W&3i2ZIa%v=5=_c}W@_OnP@_KR<buT%Jyp6h#yp6n@dVsu}yq}@?5H+5hz7`x}C{9R=B<c}rBKZjUAT^eJkQ`05k(JIQN0a9|WUL)?8H&fJ#W1QDbvW6J+>h!<?nm~d_91(cTT{D{Taz16+mIWPYf+n$mDVQLBD+vs$u8vL)RN@lWJhWdvLiVMH9t8A`MU<qLsp^qKN>>uE2>6Ts@9QL48?yi6hEi_Nq$aFp}r=+=9-eiP<)^Ih<u-XhkBcQhkT8p_yYAR`2zVgL-9H4L-IND4Tj=W>PK=a`4d&GN1ymv@fT`tvI@l?s19Tmil1l*#qTtP;;bzD134?%iCTv2L@q|HLRR_{xfr<uLveMgPFCtcu1>DUP~3{zi>!1IxfQt+HIUqi+?zU`+?#BrE+SjWW2no?W5`n&if2*Rla)r1XOZVI6fdK0BP-oaUPfNYP`rV<pRDu{c>{SPHG#a5ywxFNE!)aa9K%q&i=o(LC_YX-LOxDDOg%_GOx{k7CT}M%q|PNP9Zz0Jp5&0R_Dy0a9-S7!)CtsK<OyVdsu$Ux>`m=QR_aOiCih?{?o4e>?o4h;ZA5NKZb+>~Zb+_1bs<+HSELpvD|IASB$uG(AeSH)Whl-^Rcm5C>VL>86z6q7D9%ECMSjIKQLzfeU+Fz3e<lCTQ2dsfLQdg2_?DsgDfJHdDcMfFMz)i0G889MFOZYT=c%X3XQ(Hrr^!dD#~6xFQBRXkb8S6Ey+J-jzQj=c8#R@DoqCU<_$4)!oXYk0CG`vWCHW2Y1Nja48TAQS>0R<O@-2qqD`|0-dYO8ce3|?!^$Gb`@&oESvQo9CKj3G@FQ`sr6^j3&79*=r{Eb?HtU_@vdezCf$OWkN$OXuysIADQ$mOV=$mPhD8H#IAdy|z~$u-FC)G=gtax>}_ax-!}>MU|Q^3M##eW~-veaXJmWn^FSNa{-RNb*GL2J%F52z4Vlgd9fQN)983Q)9^C<Ou36@)~L!br)HwNsc2QqaG(8BcGriCZ8Z5WhmZB-A-1zki3(;lsbvLlx#2*Po|D0PbSZC$aqf7VFdI3){rBp6UY(d^!}N^{!{9osXzVM-%7nR^}jdAM`;hT($1O2u5+gG?ac94+LElap+iP)C{E8G#XnQ4k(E|-$jCj#={c#m8MTB%Mh+`>rxta{$a%#zsQDZ+=7{3T)VvNE^Gk6#Y8J9m^_)nbkBZahtl|RHzsXA9Y8mrgar&C@mTQL6r{t%6PNc6VcCI%{Z)zFq&rPmRN|UvW^(tA*SkscZ{wY0APJfo9uZ?H8b{<KKlWCE_P@G7;LQY?Q6RDTUmsw9D^#nQn`IN|z^J(faveHvzrI*M`e<LfsPF8x4Y?3chUy_x+AuD}GR(gwki}!PpdXjvSeQ}X`oP3d-L_I=2!v0F4CXy4`z9jx_5<dr}#gw!dMjc5WM(#%)MD9m!$57lcEq<nYQwNc~$z!M^$z#aVs8h(($l(md^Qb}OmDJhPAo5J=cxn)NJlUT*jO<VDOYKMQOZK3)BYTj4N{h18+SGRBcD(=E48`>_^-(>B;-(D6JsFDqsNQ5hav*gKIgmVyI*mMw96=2yN04m{#gWu`<n;cHWGLRkQ2Yx+@iOXca{3r3UP_%ook^ZS4xo-F2atWK{$yWr4{Bd>4{{r-2e}QoCiN$BO>(JB<EJ<u)sb43>`2bdP+Xc?n_Qb?S(>5PLTyU6kX;#yTTpwF+fxTndy)r`M^XLAqsUXKf#j*=xzt(Yx#ZQ<2=XTCR%!%Usg1msx`S#X?;vldMv|3oA;(hVs9VT!<bBj%$ot4U8H%H*%gE`urFb26F?A_f=?wB>atK551Zn_z0(l74mpp{ro!W!ko!p$-hTNQ7jarjjja-~sikzN*#TkkVG8E@xD9+AM>_BzY{(GD+tWk4o8UHEH#!#GxTAHlXLe4`jM0F(>BD+yrkkfP5jiI=1T2!GnW+?7VZBOn@_M#3Tdy&UdN0G;p4eC^~L0(9mOI}D`LtRZy&-*nD#hV$5cT=~Lca!&P8S`O3bq9Gr`5<*WIeiWsq{fjClH=3jF!c~Mj(muGfVz)-fV_vgle~w#jT%MXMqaOF%$fBJ#Y?D*$x1`WOUR+r3FJ`nMCuUoMDkFE;@;HmWTnl?y~%B<)yQqh?hM5hsKv<@$VI6I$wkRd)LdjIat>;Cat?A<sslMIISW-IXCddLW+Ue$=VvG`z)-Ay&QOM$mzs^NG!I#6A#z@FNva!JX<c$ja(OLd?v-aKE=DawF2j0@QA?8hr-f%)^kOLPL~Tj#MAoVG$vU|aLviJ_=#Ul-(?b2eV?kQXPm2|45uFxm(_#a41$hH`IdwjHIe89sI(ZH`m^z6ZOdd@gK^{%EQU{Z*<ZjeH<Zk3v)Gp*Myr)(S#SIvWt5O@1tCC%))yXd864XlM667DL70Ex6i%^}(KTyk2oyq0MHK-NIHOO@sifd6Tk!z8gP^*)hkXut5k{fcoTQd}Qr8XlsW8Zb9_91sA4`e9zp$;bdkcU%8kcX4UQ74hdktb89lP8nIsPoB67m&lqi>NEeO4pJXkykMkZ=^<(mF^;MB*&zMr-wt9!dd@M|NFm;{|s4pGXKv2|JT3#_fMlT|7Dr9r2Fp=r93^dt934I@ya3((yyxbwf_OpE@^l'

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
