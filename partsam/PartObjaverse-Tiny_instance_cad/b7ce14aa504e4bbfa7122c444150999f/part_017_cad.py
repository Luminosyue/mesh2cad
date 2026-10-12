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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_017.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_017.stl', 'source_sha256': '4180f94aa60807d9bfa0128c93da1dd68df36f4f0e4175cbb9fccdffc7549158', 'input_faces': 840, 'input_vertices': 802, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13339799642562866, -0.32224106788635254, -0.4999997317790985], [0.10053834319114685, 0.3131502866744995, 0.3131597936153412]]}
GEOMETRY_BASE85 = 'c$}qu1&|d-)b*_30Rk)pNPvfHaDuZh5F~gO3;vMBU4su6AOyFtgz$oFaF+#kVQ>iUy6})d@Zb>a>+XAcGTl3W)nDI7)va^p^zGYsdb(%k%}x*XYlVb{8T2o^k>U4$&#bLw7~DQF!i)itefo877umOPk6wd<j8BEm|4E!tw^5z?O@oX9#*n=2Bm1`Nlee5FZ-owJ@)q*s?a;GNzdmhxwC>rbeI(bbwdvM3lIeXrwdobfw)2%KTD*{_ME*jaVV?ixzvL_hvq-vKJ2^g!+QiXo+_@~UMG~PKGhZL%=r48iv{N@LHrwyi{XL#pLho^9BS%kxl_HMW<+kOF<4ZpClv9^+r0(r<p8S7bCGrVe7<WnNrH%;QyXcOH@BM9$(2XX4l0Ne54NAMQdr2=gdA)PL%yC;u-_(TmH(4!LJ@Bju^+Ugvq#qbaapDIG-MSb}c@EsWPVE1N^+GpZE>ZT^*jDm{Q<wWIb#M6Zr1z;W^7l>JEB4D;JkN3-7b9`5i^4zoY>Mw4A@T`ad`<rQW>TKH?}`5LS*t`oo<h)<dAEyrU$;5q)UDR{>3C&=|Euw&U-eV`1LG-vxv`|*Ype8+)V+mUEB)yW9jo+1VB(RZPF?nc)cq|+Q~c~TM4rZ#>0(@Yb`PWYE02qQwnBE$albW08E^g~cQ1(Tr`<@O`I5%T(0!Eua?-7+7eY5SlWtV#N_z7K8=U=ShLLU*X()7W($#c)2S<|sg9;)~>waw-&v9*(acdskcV5wlR1y8@%Utuan{I_tf11}?E91};GyH;^?qArB^yLjHpU7`SKHmN#PC9itUjoyEgunMlgfd^OtoMX&6|1An7vlwuH>n$2e-yg8eGnb@yzqZDj`r&Z(v8biNN?YIgR}pQ?4+9~TWxUme_(t$Wt{l8y*ucpn=e}Ichjx6^>?}I-P*=Eb^Cm!#h1DsU+Q{%TbJ>dlu`Q46Z5awFLOm{%4hu~(l<fBTT(fn7^gOg{`aLQL3+`$;yC)trK9sky&}py4Wzt(!Kushk8kNeG#=6wQO*PAO&s6p1(oxR91l|WKC7vWPhGdi=f?cXdB7fr(B*kRj$7Zkyh0B&J|+6mDl}lP$UAc`Wghv)Pdp~#jL52--~7kE5^+3xGAnWXZ7%K>^}3}|&R71}{bJr(&yvypE-D=(^rCIWdCyFrR5?F*dWT$a>T*6BhlaW8{tazuzg{O+&L{q<6vtOOv2wohCVNZyOh}}hXRIhXj^3uB%6Z0kPrAQikUIX$+@9&C8|LHB!X3Ijo;82_x&wbJ^yN;m?JF<($2dGgoNs;U?g-tC+(XCfd0jdmH@PWvf7xI5h<>{}NE}DsvJ;AbAaf=WFL3Xe(B=8T(_o9(ufT&NN*wRItGk`LJkNO7lE1ItK8jzUD8)Tgm+lkdw~>zXiQWI<q|5V<Jih*Ee~|ymonn6i@7teo>c*WCBEH$)6z5Oh(?vU-^EWW148=c7x}5KUm70$EBFB%e+vBI}B#Qs@SkVtgfo61lP6AyX-xn1ZhP&zYwybpO_VLyHZ5{r`nhBIo?gMna_+>WT*L^ig=vJmpG_Q}|rR#XmKqXIWhKJ_U_?|oIxNWEV!Kvq$ICbM?E;?Qr)6;!U+eV7NvF-eC0;9j9eE!)k^6@OKf6A#F>+?~29VUtMgLh8}<v3c!MxUg4ltt*CQbTE6jk+!J33N<F{s#`wd1=-}y6zMYQT)yMFGN1xZEttbe2AkwM;PNpe}4U3=+?lEG#_4N5c}n+{}=g(t)%m0>^;$Mff?7;IJ0m6BI4Azy2E)Ky*1x%ansE+<>H*WJdV1*J>TK)`TP>aDH%ik88k!mo3HzU9nRzH-JMrl-+g6b$-l{98iz4^$MHCUpO#Vl`B%kx%;>dQ?3eG@64igxL9t(fM!!+~=*@IKc^FCenenrQF3;QECByd8ah@o2@3NgVenO9}75VoyNpH7}=Hs|IbRT$QsM0@y_WkyRyXfZjwENw3Z@bHXy6MKYK}VgseP61@xBFR(Zyy&e{(txR6yMrRx~J3`vA@2U8{)j@9ovKY?RLpnv7M>K88_W}J@vGrcRaG))gQX_H}`c{`q_#~vN7DDTf26wcg_pXnO4g2HEaASj*Hp63HeWcD8@tJghlt&H|mjppB3VGd4G&J<<#Z8v!V`)>!8u4h7#YK!w~scKa{0B3$GDzEYBFakBu!wad3U{E^I^R$#Dggc_+uSaX63A<@Lqzjuzw1N|jTIV|+sA6*Ehi;veXDTO1c_@h57(Eq%6==V=s5MEy{~FY0^FW)$ZE^Hzv*y!?}EoO08R9>Y#5I*wNYf9TTRc=aZZ`lBBmmj{nUKEB~k<CJ-{VD>IC4tGC_bIxCX`{#5WOmv_8-z*aO`>xFt=LgTEn@W7o&FLbJFYJoY<@w+9d1uPE!y!fYeNER--|~HQUySp-|Nc9=F1%YG=NxZ=35UdZ@QhhOad4hAho@U0{HOmK=NxbTeIMvPDt>yLvp>!JsZY4+p0wkSDLVQyfj@NVZw%=hNAr}f3%>Xi(W3o^O@;1DH=M>*+hPlxx_zF1GG3fNz3am%{-&37ye`ca<51T<Em!V#>Slb5tH0E3|H9#Fzg?S0=V7yu(hu_dpzHGdVC&lXMAxOiaXM3+bN(7d>d^k?PNL}Mhhdb@hX=9F@##&slg=j>P6^#NZWrah?DYmQzk>J1y3He9x95e_wRxoL(%*AuPppz>)E1GCzwA0yFZx8}6ZmUntn+yJhR>n<M@=_J@806n<?+(}?c)o7Z@>OZ{}@|tiFs{}>JaOkk5;94((5!=`putbikPR~vkj=fq6W};waY|Bw>H<N-yQq@j2Go^Bb5G>^Fr6<ys&j`9_hO6@2^4q8QW;H*#7uLwCf4VOa7+|)9=tgpQ}PY@;Uj>E-(CjnWKbmX1KN8+0TJNoul1!Bk73wPF?o1?k{!eZ%x~-#F6t(*X6vEx;{^JUHbbLjv{^Z5IXOTutYzYTZgIn*EldX+)bZWI?Acr`D^~R4u9{lMij^2l75fO>m>TqdPmOzy(u4w{x@6K61um2IK}z?Aw38CgLGqQdGenyhVGwB_~>|5Cfz(ox-S>$=Ka#7cf3l!%bE_RIDL!a_eOv6|7$YEshLOZ|Bd76K2Xz*H7z$fb-VvHf4d*x@7wo&o7?==bvYlUuFqdxm;V0v)k+-e+!`@Yb=~N^dzVv}addw>fB5_2dkWon^ab_j_g_;#7waK(ZywUkHl$lI9Vkx8l%%KYCG@~&ZIyiFywG(yFQl%|BVCvN#`d>c-NthQ9ph8#`gl&D!{48Op%O<PcU_mqUF!Nc(RF)VZTAb^`}YNU&iQ$1(Qm%Wb4l-clIBsd2+~td7P@imA9~(vv?Kk(DDq$a7d<CWKb-W)l1hAE#Zq*<9u!jITM_kXzFaG$?3WxTx-Q3w)b(+t>-IR@lAZJ%59#+{jyBY8cxEMkv&In8bM>M7`&D7ec=J5#O?u-nWqkTpbRj)95$VCbX&iQ5D&~zjy&Lss&t2kt=zBR|=+?GtbX~|$oBT_XF3%_CY|^drzX;tJGk|_yT*i4Rb{55HI7rzqse1<;-{9OYv&v+OAKiiW_skUXj~GGmyG79Nqn|ocyMs@Q>yw$Z9Ob$3u*l!4dXV%~Rp|Ql=&8{C(b1co^VB%em-@5t0@DA^NA;4;BfZ|M6(XK?y*B;|2wlIP2BPPazji$}H%%sg{d#)0;c|i6^~l&3EOh;PVct2hOthz6FMQpP30=Qln9ui<zjnO{^xjAQ+V#R1x^tQH_{!^rFC>QIXx9s~UCE`Qo_;<wODuKvvmBphhAcwY&xcm#Y0+-;-ON8K+HJm@JG(}^&3DhS7SXQry=Tl4xA|@iU$(?`zK6|N;x-?x9AlQa%}4V=iN$X7(R-%&Vz>Edyv?=PZ9aN`@Go?mkN!(PEp(fYo>Zjk^U<6&YN6Y_Ga^SUbepF}mLUsW=VQTc3*F|U@on9OZu8L-_0sP)AN@=3_+95?m&Ja!`RF$$``zZFzx&2t#rCgR4~h16g)6#0Njjki_T*G_qh1Q3dvlgjbl>a{p&RRSE4o$mJpJA3VL3(jb~s7TwT2c{<NtJ&{Cm|<^%uM7?`U1Vq<+ixcAi`QQrGjBx}Lw(_57u-=Pz|Ve>=XGzpZQe`~TfLL+EoC(BE%f<xzC=mtpk$>*>iWPTf1Fl+dj~%Z`OR^uVmM;&-g|P2?`8?wz%c{{C^R_C+QB#7g3KW8lNbYfAiyh3WU?>sm@a-U%yCxW*Yjn4S~8?x^lp%E!mW_N`Wmzdz|&dTx6>`5B(4d33@gw|<bi-VajO`$6h@KiK|SKiKiLez5(uez0||AM7|<KiK=F^@G&)ez2yT7$fq&8b{BW2ktz((?z$&FH&@)?C-ArQa3lPQR9>=?H(Vx?(dzI+0|d_c0Mm_j&{vo({=v@`D?nJkBp<|uj#sfg8VgI=HqP{HA48UJGYx3595nc;(54n{{1kaw>qfk-ci+rZZ>|V>PFm95x2xkcm41ORUckrs9PNCyShVM+g)^RkXxQ+$A5c>IAxlg5_(@eM{1S2yVyVN{BOoB?J9Kr{%w6k7op#+qsCcNsFTp&cU5%rO23W*wd;{-?C2o;bM{dEp_{Y%sd|M}q-)nZbK$f0ZtWTij<$8pGhawc*M3-h@Ed{IZ=V+WKUHQ4G*@|qu3di(v+v7F{5Y(*r1~4HbBX@euj5nm6cWcryY3rPj~5fiQ@?+xKc~2er{6zZm{^LAr+Od4Zrsa=INE)S)Xlpe)jSthsw{Nv{>SJSQAOzcgU=}bQvV~ls+;#}xyOGU5$@JMyEnHCckAaGzHXv_wEHyU+=T8z*YE4@?k8Ql4>a25A0%}Bcij3bLf7vz&GHQg3xDmt)SQ@Ph|snBSTpv~2xokG-)rP5VT%3G?vt(2RY`BZZlY*6Q*&3{T9iW7^DP<a>JMG|dyo8VI`fzJ?cRR3O=te{KHq4YK|HtCe;1eszZ1It`@+f_LC?AM-xnp?PZGNRJ0<<7NzU<UKL>lWfc&-JN9Mzo<gfoe+IxxowclT6+-36DpVy_DGFgl_?RT89`o$FCuRn(z-g>&&U;TGt#Lq(4e^(muAv1)(_B+&AS5)W;ez%Uj^()u?VcqEO8TE1<chjvt4~{u?PlFb&{!%x}CsyO^&gUK<y6*1@%H$p&x}DE=f6RByU(<E}1o>;aosW#8=dbCye}eoq-OeZby9MHSb@R^^$MIv8t8TjS+p~B@uNyVf)gQX_w<51Cr}?E`H?89@mOJN*ecen|c7+&++I7(QSe<n3y5?QIfZkitt~=(`IC}p@yS{iw9T9qh-<3a}pg7uf#QgWP(Dmz%x9{bZ&iQLUcX~^@etj|HpOC+H9Wi|aR*QVJ^SSwMw9t)h<LLKpkCW7&-;E`I?R;*nnLxUB{x|nc7rJ>Uxp+=s%+BSmmpnu9^GB)ep2$w|$DLgx;_KIoLAQjS;5p&Vf5~6FURdMb30;3~sq6ANq}282mbxzeJ@-P_(s)y^NB&Gr);jZ-*CWsLRzgqk+~z>%wa)zI^}_J>R^r>&i*^0iI`fy$lXYD_PnNp={8`uS=g*#_Y8*TdPoU#@xYYIM=LvNA_oG#$d*9?(EBY%oH9dD7R$`qqzI@KF>+(6j)b+m$=(_#)wTh)l*Pp-jsVsE;dg|Rxx_<rjtgAx#{LyTkGk+s}?{&`o3Y_cXs#}2-;&*YNvZ?Hs9B;ZV$D7pk@u};!|M7iFo`KG-=sB&XTXigYUQyt<(ysh_ldju;Z-TD>eM;Buzh|v^rN+TH)OGvsWzh9;tLyf--59!F^s|2d(<`aa_4^<5+Z3eh_c>pFLUHuJGu};2{@Q(xCo~QD>-R;e3kW^I{ZF=f>)qy80$u)n3VMRSPwBdxk9ixAuH9b+M)p_Ydn<i)*i8>uwGKIT8DICe=N<fwS3fIp<lm!pUH&~<>iXZWbzS-ghHO&vlz#`*bo=jy&=dUKP}8NqH|0M<*Y7_AV_#8x?fx?`#@OJTN4_V+<K1-6{smW@x;zh<eSVF1(~YX5$Uj#mdJjeaJ4@4C6kof)_4}Y}?@{Qwd@sV*wf87=UHbcKHQ3<nXZ!Ebnr_c`=n4LQt?BmrCmm-gdCK=^bX~qbW9!=cHo7kT19jI6U4JjdcVMf~_4ioJcY7&M?Y)=4!_#!UwD)AZ3*RXHAm@v&%lRU8eSYb>^!Fsi`-$57RJtzTkFs^`eJWkI{Wqkh`vvX2BlEK~8{Ou$uFH8Ub$wpzy7c$^a;WX%Jt$8^v5n5-BHzoh%9h{goL};~rt9*$=83Jo(RsY&dtd$=ZPa%0o|vafd!;|+ywG(yFKk_#N4jp$yV^e}?b`3HJ)c5(YWEMiF7F?#Kju>$?Y%qiu`SeZ+WUc0Pw;-=_i;+U$@>}q^OJO4)!sj}x}I11LC!l}m-EinwRx)Rw*UKNo0R>+dzgWoxk%UE^OU;&o~O4(iA~Oallv8zR8EN_-y`+atR!^(Jx~9=@J(*>PS@o;vUP3V>ALi{5?2;_g7;lVe2e_m_hXF%^(cSseR5rw?|VyKe?MH;rGMa6{Y}pKBH!cnZEQ&SYwyiky}noSm+u2xOWKjY_I|Q2YgZ+{e4jZmyN}TI_n&>^M^b$4ed)kAV-<h-ezo~{qS6oY{drxN@6StJf8So$rGH@1RMNHgnT@YzDtXHH!=<jjPae1#P5Ef=pZi*@CS7}v-K-O*_}lNp@82tQPnU7jZ?nhH{aE-BwV(06z0?!Duio!G#nILU_#a$V=8Mrb`(dZ9ua7VzZ>!@+uBVuHM;*6VKcegQ`Vr{*dJ|oj{>IgZ%KVk<0?eo<bbip*efS%{pg7vP0Q2}eileO`F=~WvcJ{wqZz6Sl{eu5R2Gt+yS^P80kglzZF;jX;*VpMl*Vn&zeypze``!(w`-JTgl#jMP$SToHjgR$2fmAIwJNsX*+e)Bg-Imn#bzTW{`1@D3*-Ya~UEd^id)?N7&uLs;??(A+>w~OQLzFmjU6s`Jbx(eCGUcPK&+^|}yxDo&?c<egt&)#i7bbOmU6|AptP2Z1rtTNkqe)#~j}{npO6h00UQ*ZPdP%A4>nnBLUSB!*>}Kcuwb#w%`<wPlTYne0bzkw9>jAwf5^r(#r(Cxvb$#7pASUA$=W&$l_^e_cileQgv^o?NdV=+sIf{_Kwyx6`R!Q-f>p%lPS5^Gwx>2d?>m_YnTQ8~Wa=oPavicV1agpn?6X;l%Ep>ezcLH7WPq5x|ctg_lb+Xr6Q5=2!>4w&nzqbC=Q?k2~r(B1w>vA2s)b(}ix^Ayq_w^xNTkkA&eO;~RG3omHTr<_!EzWW1@eZNunlV%8`uc05)B?rdn<Aq)pO~wnX&h?nyS?RBlCG_T_T^cv#Fy*DrLM1!mb$*q+Ptxj`axgc4L!m7ZcUftE%2Q51naw}?xl9Mb^89=2gzSshi-g&NjbjqdlypIzk^})y+Quk`ggPa6J=i5-;vOCxlZ5jc|rMT>-43ruhTc;UsFE%_W|mBB!BID0{%uujEJv)mmqDZ(Dm;U_>v}yan3LMdkDvp2;Kf2v84YYr=H-u7SQ$YE%<**LAv%`1+z@n80UPnzXx)Hbp1OmQrExJV(Z%XEBw#1EBRZ!($e_vo<GJp{^fT<JhzL+IOn7Mo`&aY@fhcPl;6`Z&xb4fE5FO(sb8IR?K>XkC$&h|zWd>S-!#TK&gJ;gb$k2_XhU(d?~v%a99LHHNZMcR`z=z}zl-9{-;MmW@2>b)kgk7s#p>8A#yPL$arEBm9pjv*^0-(hf22IM@7`F6r<1OIPsTrDF2&crC*!~Jt1?dHcZ#I0f4|7{+8^Vbck(+qQrEweWA$1}{`&WJF6~g}m;64DRbgk0b3V#`^Um2#d1~JU^2J@DJhkr#*}C@KA@BU_%KqBleS)rk_sRR!EoHvT?;v@*K33+V{BDwOTC%Oq@gw^|*JZ!?-e%kC9RKn=PQIcAw>rna{O(iWLE){=@h`s<6=+;_t8*O6?@9$)58LWI?)LYiuE%b5_M2$8zVfxN6|I^)59DPbm?bm9j1FxapZek=|0mJ?Q(v7+{{MaIt7Ost>!-fX2eDHxv$Mdp;OCgFV|E_69{dcmH7H+$GS2@-**)Mn@O$8Y0ndZ~1%4NJ7Q8pJ4$L|OTY+<I4bHI(cyC}A=&ew%J+rpVB7yC|dot^e^6n_(yce?`DDQzX&V9^UGV2QL1m1>O3rFm>@b!VW1hxS0fqLD6oxr;RI|4g_w?y4ez>W^y2HR~=U-GutZtI9$hgofAjerfo>oKc~^13MFyfMm}fY-(Lcg*TDYYO}xyaBTalt-Y9^XAN&p}ZN&8lXG^aU;-fUHH_7)(m;dyc;5)Cg6=>4IO!Wk2afwHv={V|B=nLF3cJMKL_u_EFZIZKp*&MgX(+>Yy`fX*>GmPfmOkI%+`p@F$|o??}gYLbAT^ItRBGL;N=l>AaFSNK-4J@l)kNzYZ&lb@L#YWEr34oUMR}}Yym!oSrcZzfq#Q-KeOu0rhqrYc4KD0GW#C50G#70aE{#^K9S5;f;V<-N5VG}{;Sab7_>D8?N>*BGOs4chw~N8mNGjHJOzH3SroH<z?tBCm<?hU2R;hhW0~!R-(L7~zMGi|UlabEuVuD{Sx;bp@XgFtGwTcN4t@f;{SI6TeiCJW0DlKR2|Nv40lpWx{t287{wMfhU=(-^_H_Vo5cmM>TMW2~?bX<~?!cblo3S5Tfc?QkLikcK!#EO5I2}BW*%M|HfUCiez~?k@9{5FO3z)434ggQa;>QM4JF#ek^EV9FA@(}Ne}X!^?ndBn@C9gN5%321M)=$SE&@M|+<5yOW5MIFA3K2)!FPhc0j>j|%WOBZ%iyE1Z8AI0%mSZ^?UBsJGus8+1HP46H}G!olRn$w$9Yd|Zv}P(_5`1bJkA3zJMxfu?M9xQpJO(O*+0OA;IEl2XLbQN4g4H%5^$QM-g4Akj{2NeWj2J_H^BbjlbQX*tTC`Yc(Y*s&Kx_JfVagqFKdc=9A|)Yzu(}?u{HQIX6=}*1$G7Bz^ps7mB0?*Ly+qTV0G{j;KP8`!21Kg0agS58M!qAHU<9)W%YrL!2Q_A#lZI9i?J`ifw#x@TI|aPV0Z9k*pGI=4&bZUHF6oV4Zs!P9G5d&3BC;5+<zmp)!-Yjy_MN6W-&kud<V)lf$zfh9A?qXeg;N?Z$jA)@MvsLXXb~G9~$R7neBo99>nK7j@cHpwFR*_U&?Gg;?76A(TLCEO#w~>=RWh`$8jz=Z)-Q&+l~F*g?4#6+ki3PyAjU<P6VHa^0~km@SWHXKX4BCQslb@xCuN8F@FZ1i|x6HIT2`qmt$6e*;l|a;9M^cjq|eD=H;c}!+B|J=Vz9WSutQy2QP?ijwQjXG7D!`6IdO*BzQP@L2PsL!iQrGa2`Jo{5TeHv{M3Yar_dzGGbQ+uZZnhi1#h926#1QRp4I*b*f^2^P>H{Xj|?-Z>KQuOYmBVmmioHyco)>0jq#l$9{N$1;9%p-x9!z;MI^<EnrP>*+wm3HSqh)UNCzG{t(+7A253gejnT1?<KS6;4iS9iJd!&G0O-n3LeTVYcQ2(MH%N;Se;wUE&{KDhoUSi>hdzaeVN%!_}qlXc~0h28nH_wKIdOBON6!(Ar|MiS)J=>^E%qSh4?()CEx{c?h}9?$9Qnw)>mlnE9`GEw9DK19GDTD`|x;0ffvAeOkN%j%m|(n`*9O}aRvK*8~G+e--KfSt|I0|<QI=^9`6FSGa^sE{VB5y%sv680_S>qXq>0U_9yU30Za*gnceeUV)hvL2>dSiCGZc}&c??Ivs}RJ;JiFLv=6A09p#zf!!ZXqk9!7w9B+ZYM>`+D?>pN40`WP12A&)7asqRJdw9PGQN66FlMVZO5&Lx!ZOi@V?K}Y92hWXoydFnh=Q8|xId6w!R<z0Ym+wbr;4N^zKRn;}z|X)v$SXH67x-heE!*-y&&hZVX8D2P4qg}A9IJsBU{;P<L10A(uZHbvs3Un>)aBU95vM-tacmBr2JuEP%fhSzd@I0@bDr~DN8UVMO<*hVG>DNCI2SxW%Ci6~fLBBNZGp|fv!Km1z=Gg1RvKUyaQ>zKJj`kX^Ex;$s{(8XUK>8`ftA7U^SRFK128m%_-%eZ2&VFQlyUxu*)wMEfbYTMQRflx8Tb@t<KQz68t1*34Mn}7h|l>kW_!`rUc}=33_lkk?iIBA4Dorq6~M3%;@syU{5YlvA<o;1LVHoz-<xQcw{sQv0Xzz^LlKw9=lmhcdEBe;=R6+!*$eyg2-|0n?_S_-@OQ{D4EgaGoTtEX2m^*f4`vp`ED%h1EtvSeVB+_Hyo~d^!Bl5Iko$6;m>v5J%#r{<b?`5+%`q)_QiK235&VHNVM+&2i|w?ilM*%(J{*4lp9P-`;By@9ltEh@3p?7)j&?W}0yhw^EAR(!wu?r3)Ju;#ob&zdhj#m+ZMpxvovgsZ;0EF)2KEC_g7OexdhnFkkCDJR;AxR>8DJss5aeY5lYz@N3}6U2|35KuGs^{@0^7-<WdwS`bHnFr;Ai0JS-?-3Wd&vfPsc2I2$d&C8Rr?9Wn%UPFbjBc)X50U1ip%mt>1&mhhs+g&kv?LzXTKi6fvGN{xq1{;+PKY{>#TG;wDDBnGm1H+X2iD&VACrkD~{ix3vcCam<E&dyY1fpuMc%+-C>;IA%v5r9rs|m=*jN?APzWjNm-~OxUMP=%c5|ISca6f*9F>S;4cSP0l}OmN|q50>_WR#P0+XPYsQiah?iw{thNI!1*<DnL*bTj`P9!wQY?-*HMn^zzf1hUeneX|6Qwj{fgl0upP^;@!OeghH?G}jPu`Mod3$~8)lW5eGTN>#eqe@i-Q+pmWA&lKh7}D?*x%?ej|vC^K1N`me=9;o-oee8H5iF;@mjD$E+!{dd%9uIByB81l|(74zshYox{v70gr-T0)GJG{5rEQSsf3vvM|nz0MmgN0nf(lEvxgGS)vfaSK!<@Pa8tUc~X8&V0A*71p^a-4`u~JnDqhn1s}?6SP+#DLmB7&nDs|_f0S`PfZ0H1KL7`T4`((4<s(qWxyfuK%15GXIO+^S`5=^;C?ARTMj{`{2Vr{<@|XM57y0%B?+@#XJo=&z=SP?wWwsZ%5BwOj<0wClGS2riJAm>7DC7JDvy;pY0uO=z$?Pz*Q^3>Ur@&9ZPNUvQ@Z-Rv4t^Nhhmohudmr-J4}Ji)&ymL=<nkx@Vc<US3Cu<@8xI@}K8D#iW<P?D#r6_rvzaXh{sO*`*#c&ZfWL#!V)hfWnZQZl)0j<WHUl^nJS7{upD_Cjm;wARHh6C_dkK62eu~)%W+#Ei!T)4-kl7*N0q}8b4vc3u5%@FsU}i&@4FwJZ@4&1hvrfRy;NLNeVAcTG5WG0E63o5=mIg1%tQfPBz*69;m}O#?8kiY8hUL1M*%sg?@TJV6nf(D=0zQY?EM~KTGr@mkHip?);Arr{%zj`t2sjXY0&DvxW|M%E!PBy1lZIIsFdg`7R`!P3zreTPT<3mofN6vNE9dq81*QY%C#;YB90d#tB7TMOcxG3D*TA{{5!y%8m*u?PRbUYK3ue!my#l@jKf>%Nvtz*H;78zh6!^kX{t7;?5Qp>Y%mU1A0&jqCWwwpkc3>>{R`_iLUU!t=gwIXH;rtx4v&=34&x5aLwt?A3;3n|(@Y?`9=P17bp9_e?`2lA8nH>Ti1Yg8#F|#GWXz)ewTMRtlC_e<BLx{sUe>Y_Zvt2+7d@8eP%%%fpfKP?rG~iB0`7ZeELLAO32lIER*>79m*Wg{4bz;^T*b)3|_;mty1h0&GogMW#FUPD5v+}^Q;H{XoVAc}Y9K0<2S^%4amqWdlj{2O}WmcP6JzyR1e$4tX>kI4+UI%`CfW5)%qF!G|ea;Io%g3xBFh6)hW)aL90KWsz55EZDci;t3uYsdJ=XsdrVwM+}8@v{?Z<*Bu)&S29zi)vx!1JJ9O-Fss(=z*%Svp`E@Ni}onN<Q-08azIiogosX;H6|qdw=M>^u>|EHN+<_+M;n-DY+N_%}G$x!-MIXwZM<yxtvPBJiXPlQ2sTOa}fBD|^E1DexIM*SX&lVA7!f%6Yw~z+~XT!G^fO3jqd!7h(1#v%<ha;6d>F5?Ba481)J}>T~{{weyzQ2jDyK9IVX4EITk8_&fM<jbk>HzehdpBkObihVfVYS^#_v{uwJv&nyEl4E#0xxW+LI<!?}r`^fs7|HJqr-iN@);3-*I3TB@GlY>8oAJ;f0NBKXf$9-gd&U-M6Waa}l0dK?Xdz62VGR{jeD}nM7DC0aCv(zY0jWW(Z@^ORmBq-xNDYH~4PlYnhOEN5u^5XE}ynd~q;INSY*M9~2-#>m2ZYcjTs9sZjt<YKX5sPKNWLUpeBK{16jj>?yQc*Jg<iz+N*n^e%'

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
