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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_015.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_015.stl', 'source_sha256': '1c02d62a62e3d06dacd1724ec4dda32bf945fb7856f05c0fc09363c629b0e649', 'input_faces': 761, 'input_vertices': 449, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0787871778011322, -0.31161853671073914, 0.12213753163814545], [0.07401140034198761, 0.15754735469818115, 0.36634528636932373]]}
GEOMETRY_BASE85 = 'c$}qt2UJzp7VSZ!221SS=(RU2L_~w_+Pf(BenGLKAlMs6L<A8lsEFlSu_6}i(PQCRv7xA_@y1xNBx*Fq?mv6Y$q(<3|Ht^_f8SVR%{A}7Yp=cb+U1<fOV^Iszbm5QUwQ3xT(Q&@H8f30Uag2W(Km4X$RWN#wZ{fbancG1ul{A~rCoY<?%LN$o2X5zI@C94NMKbDOV!518di0&R2}9YI6lyO>|p=Ep}vZ5<LwvZYw|%OyaRkqyPBKZ&n}jF)m<zzEdP)Ha+@LOzBTt9H?`5T=K5x)wm&|7R%v5x#l4Ext~J;wwtnJ2qAxfJZ%p%Cr))=|UoQynTYQh=_2j$p%C;`~=d{w6o!@o~-=RJHyk40ipBH?RDE{vc6yCP?g7j<i8Uemv@y*h{*AD5|o;+B1y+HmA^8Jsmq+k2;;=)^#Zf{by{=Ls7;cFKa-guR^Rs8<cSmM$8`|ObR%UbLZKR1d=dt1{++lBwN-8Ql7&KLjsu{YbK-@J3SOZyXP$@2M}KZG~JnxlQh9K_$^!B%Pi-IAU1{m6t<^1a;&@rt)^@!unPDcBwTwp_4D+W#_Sx3qUIa8h(gz((PVUD_|>`SclitD0AM<IK>#G9JHI=f%&OXX_Pj>0L>9{j^Im@^M3Wy+Nw*j&D!TNdHUvtrPw)*L~vWUdI#i`K}LZCI6nW2gUAI3G?eWca`F89#sxVf6wp9xU{`NaT3p}`-jD^f53H#^I(19^(F~N#U7SVczY$EmEynq{9h!#FY8jp&&)Ey>u;yblYXMTrM+YD<5-!ODE*Mw&E`sb%fvY0^&^Xg*A`rq_C~}~;kBE!mdf`sav+{3zQP-kw&T)o+p_R;*Bk!3_)7fN*R3Q!)}a;9J~$5Jn0E(p?#>DShmOn<{$;Kk((l>VD<tj|i(U9y=cT<hXy0;~m)XZ8-!^x5;q^wBmx-U_<7IxW^#d{9-<pAsC@6We+|ZD>J9UKDy?i82N7dorV{XPsoQrKTU$$X=Bp!SEB=DnqN}jcHcEt0+5iR`lZ_?gyo&-Jwyk1b7FZo!JKTY~swM=-;ExY8+k-Ze!M^8d~XLrnt`)TBPe<SdXo=AJ+($*_7-kzUiJ}jF~VO@sXucH5R!fU6_$oQ<a#@v+lPCL;4a^4i-V{)NB-z^0{+D&Xro(|&Qx_TDo`}gv)&h5_CgtvY67GBT!=Ax{>_qz>gpVD}V^gFu-_J!4XFH8HqCBcux{^z)G7V($QCcLHAhZEv2;y3JX`~F!h_UTLDN6Z&qFStv1%cavv(x1mb%-7N&;jN>GCyTacgP)0`gtuih6JC3>9qa3BXZY{sc0u&^1;|79#%Mpi)p=?E<hk%#YBAxpdsV>Ki4opf>Id{&GF{fM{jc^?C)P<{7Kz`XWyQb4<tJ%x6sjn^-SrIilcR&Bz5ciW_`c83uAH0fOZIv>z>lbWM*3Oa8~a}B)rG>((}XuhI)NXMBTC|Hy7j8)$#1bPW9v%&X*<fC6h9tIB|k>K5~$1lZ;<CNO)zh7og>BXh6M3r3~wcVw5!8pA2D8(LH&HZBlE5&*AU*ms<-6XGUy`WasN?xOGa(sjlxre*ZqtL$;;UsDOd-gsGlqKgx9WPKe727K%GRnhl~G)<0WsFfY!)c|BSif=he<D(oa$q_?en0ynSp=)U)16{Ade*6kco9<~-*Auzar1yc;I%pT>(Hed{`mx9>sWZI)7!XZw}%sGoZKh1c8Hgr9RhsFU9p3U9f(4siq;IQLIX5Z>D2@Bhf>?=Rv!s@(zpvt>v<8|~i7xHP|Ap^~qh&vuEOu~YU9t84q&;-~i)oNFnMh1cBkgMS-_{0^@m<262fn<cz;t=u2<dV$ynM*0Y^ohu`LEHB)IH-f4OZ@D`|&M(`+f#P5P&@foy>0e#y$39>&>f~N7;k99!@R|kp0X_ZBbZO^51oPhQJmO0B6W(a(fpvOu0`fV`8|^!}qptMll0WUwywfB<>t`Pn?OajTh1Thxsgn187HMzaz8LLy&z~Z3tQaiwXgx3l_1W1|c>7|U<3{7H7?;n3$>OJe5b7Ys7yftqPLjIX)>r1&NIi-9_3{wjezG6x?XWZYt=&*~Yr85~kLeXKu54!}3O~vT>vt#SUHh<2cuQha>?ePXg#Q(rCy4#D>0$9Rp@Q6Jv>iExxBfg^{5tv-l6_TcHEz7L3oj;hV$E2EddOW{ct>1y#8>afbD|UTqJ58OIUg;L58(WLs|U%rvhS37u)eqkKOakvllJ-RN`2aAzeW4IRRSc=fINNVdpFj|KCJaQ>My*<>7K&(`+)X=*~iHI4gMif;?Kw?^`>bL{KUU&4yjMa-5%g8>=0g$%Z_`9UIl(8w;LsXz0OEHwptCrU%WO#+Al9Eb*O*1i~8JAMtH;aLiRUHxw+swbssM6vJaMcY+r(r|MMZkgrATo`LOn#i1k>litv{7P}FVsXUuPb0AH~;^vC&<uo?WSl%e7$GC}U8+WOCkb5!3Ul7}3gs9Psj^n2}*kHqP|3HL+SopL|aJUZB<-}_Caz2#UM=Cj@V!P1{s6zZbkR`?(BzOVG_H3@ZlFgxmPQ3ddG+M*7d_d%SFfxRW3_zI}o!r8!|{nAU?<*6+9BE3q+HQ~F~6yEUZhkegy3*w*eF7vI|8!GF<cI61;EZ<$)7mvn%wQ?2eq+Mz^@&8YV<i{4$5xnJMN8wup;NJMh!84fu+pWdVNN@3Pe_(@uvqF!lb`Rc2{afxFh97;eRlcA9zSOzCaX;44E!|6W=f0OEf8np;r_Vy+Z7+ICo^55DV_coecW);BMv8yCJp%Qxs%Kx}LtA6NYVsI<67vlZ-qB0^+qcJnzx5crYtSiaU#B7JuuS(s!hdWpyw>vp@}KT%lktoSM}2zMN56drcuO4F7N8C%d_wz-7~yTbgR!4<&4YOlE#xEhbYUp!Gj0>wyNwgx>eX4E;~aS_V!da?4iW#Iec|WiF65!^0AJCC1|~?nzyHN}$_$hCH@c#(%CoN0eT270oI5J{T>dxe`R&VL$Xg9*ujgmI)%bh3%u|i;<oV9wRRHn0=_5pEi;_64-zJ0q$$h-o%eu=w$Wi_|_!l21il47jaBdz?K>QOHO_6-+({b;rdmQoXTms%FQ0CFG={(wx$}?5sNQspC)B{>#zs-40c&m39?niy1u<qJD6yEsf#1^rg8(<&vC^Jp+^U)jkoYG_9zveFCZ5O6VJsV!!|DO$<E_za+Jg4ZruHfEs#A~MLs|lEw6>~7ZB_f2koPi&EpM3B$qCv3uk6DU!TEYeGKhB&b@l;qK`PYI^<6N$rEWAGb63*-5Hk{+Xo)z9$G#vZG<uPb~_#XU(Z9-k$$&Gr>moG%}^Qio3>G$&}@UeA-*I&MuI@gO72Y=^<@V2oYc>cW@0X}$GsQ7>Pr_7f<;kewRbS*)6J;Yz$Z)h)X;~v<d#2nG{XGxxowRth#ie<r%`z>1heBTjuVmuSxSdMwux+LQKPpUju@;NOTdH#A7enyQE-ull;Jg?ozk9+BXMDXLbqkXau+P``yytexXxxd?z$K&~QO@VM3XZRG<)rbw?TP6!{)Y&iV-O~9t@D<aA*RC9Nlh40RMZMLJj*vLMPs4qtk}vp=Ny1yAw_<*Gyutb!nj*Y5xvpr#@(%5z(!uW!#r$4hiT1~<&J(@1v8;E!k~{X*yKRKmbKjBoT9!4Nkk9HJ(0<=S<h#;-_^&YsyzxTnL~j;}`AysdKH?PW$G1NCNluZHpX*I=|J)J`KWDv!w`yaguB^Ruv=8Ycyte+7)P=RJkHo2O2#dt}X@NR?Q4{UM)8Hr1HoWI4_YiqLco%+F)|T~TR6Yeid&|s6UL#N^qq&Ye+`w-vD|Kk~)KP~E!ohc{)kpk{?S*}^?MmVG9n;s!xHh&z`<fqwx96CK^L^}9tlt#pDET~B3hwPAo1?wwIpK{P)-{rU%^CT>eNA|W`*o>9>xvtQ^QO}RiLd?z+^=peL_AiD@W$UMvai~MeguEFyYLQ|!{W!5dn)`)A0)iqV1(??hSw3)gJ-DlnsW_2zgWJ?Jwe~|RCvq8_EP7LJ}uEc{ypNkmwrw8cP!}(|Kmd!%J)CtvdiZW(vbh)qKoA7uU72aVP)jKrT$wv;f+~`aE>g@j`>Y(CA|J}3F_am1N+qm9e$3lkoS}JzkADmZXFl~{;osfv0c?99;3!a@ISYe_mlRt)p)K?*#iIbrb_)9XZ}WgUOI~QcV6JRvDqN;Z|uDZ-t`*lJfbDy{39LlKl&)VV|uLc)}J1teaBL=f9r9{$lJ?D;M<k%gLUJBdgz#EvDk-lgh`ym`k=iXygsTb_A5(s+<*4B1b^TH&d2J0c<&V0MtCFHD(@q;_PAH;KJA6K<b5jZ(f;xQ?t#<5>je(tJ!;%)%=`HM!rK~!VVz#Zey$(#LHpJNu^yY%13x4j@!zf9TlCXF<g?x)v=2Ha`=K=w@4@sfOVECg1N&|R?w=*L32#5y9{0T}jU*mxM)4)6OGEC}x_1rm1qXp&^ce3+;=7{`f1D@0e!DB~dquaQU!NPoYYT#<{<S)luwH`7E|qreU!=;oDx48N)=w3LH};j5_t=)lRWL6TI-q^{M0tO2sr44`*;)+~UQ2t9c$_}rJUSZ+KL-pvr>}p5_){Z<xBj|P{Oj+pT$JyxTO+(}`6Ap)Z`8wkhPO$=>)V{={lDenQ@q#pz63wp@8F)W>k{feJ)4}Dj`cWC?X}YokFPV%(FZ5czQ_dRZF3d0U+@}vm_8Q$PT4NJQTwQ@N5{jrcrTQE27K4$c&~C`4bGi)pM}?QjlsR>Ebp=Jz6!59b-{b}cFo~G+wd5Pr`s2-uSh)K=?^CguYEix`-#n^8|LvpGlVxvUB`Kp=!*7#?GxU5l>P4Ey|-h*W%B(_(^1d!XW+fr<LcnUdkC*Bs|tS5AmNQ0L2^DC-vuGh-<Ak(SzS9x^03HR=1afsv0VCTo*nORw^qbDdOBZty+&u5FFp2G*-!MYdxSR{7m@u|OFn@2y{Fr(kk5PO!nvII73*l@DB*1%Sr6-rV}8S;g}0PU$9b`D8_%^Q;jLfO<##A!;%WFvy8ymK<bKJU=Q;U(M9+0icx|bU^U?1J-izLHz<<V3_%GTO{$D!9ir?NFBu*_)xcE2nHv*qyoz%14?>^pFyc{jO7T8|i1K2D*<lb(rJy&>ZmD-rET3^uby{p3OHIr~IY&eIyTKWilU)ur6f0yI(o<~o44L+9l;kDzWy)m`UN{QpLi}-hZzaI6lIYfB9>KEB(Y$XR>#XJ^?llq_a2K#whKkW0%tHhy>&I@mg=Q&k5MR?26C|TFq&6YT)##LV>`qj_4SG;P9{I7@<-gdJr_D{F`sM{^z9bem_4i652|H0RUH~OBIc&(SCa8GFP75>Mymvhb7jNeDJAvso~pX%5j8l|Fr=zj41=gIGbMsg(HkCi?w_YeK*G`UyU+xEu#iaaj7HSQ(+Z)$S}^HFCl>Ni^URU@MS`W<5xUVC3e{M)BEVZ7ln!dr*T#rpl>InJFwp2Cky6L~+NJ@Ci#QG%<qGs*<u`RlO_zaQOeExcCrhUC-o=RiEi?VcvQLyN(^H`p8d(ziLn>+8PZcSdVD`MuAY7J>E^0`Q#cl?Uw)uSLIU?<G%`;bX8rm)whfpFNcG%dp?XIkhbb{2!-f-W~52;QVzz2!6#Ste2af*xx3ehW}s}?DOYtA#XFWuNi|^;CEZ!iWu*>i|`X^lRVf*^L?G|D)RVrH}>taf8%$C8xO%dQlviZ3tyrR-#-)H{%j-a*=r@A`-Wm)sF;NJ6|Y=SZ^ecSZ#x$!_dVmpkLb5d0NTHZ#B*QKoA7gKhVa&u?fAX;(P-4qtSInh&dcx4#>3qhZ^#DW?H?B4Io<0z)_c91Xuo78&Z#n!!PkE+yj~*|zsoF7#{2Lyd1c?xE8Ug+So<AEoJ9*^-|YMa_sq^Z_Tl6r!dv}6%01b5jNeJMX5FyAXGBV!I}++*AFI|6{PVTgPa61Oyh)?^cL0-6KO0a#+Mfpy&+%J$Uze*7?hj8cqTfLQ@u;Kb$WPg8!aJhVaDGMniT$eQP3)&GJHU^KMZYI+Bc2w&VBVi$pVXcdmAY{(+JyID{eB1UC@H*N>>-}7-!7GXUaRAUI{T*$_C5c@xVNkuhIJdTPW%|3!f;RMw^w*ut#SChY0f#+Nz;93Ke-)#FL*qjzv~^w{^H#Lzr)_zf^`~}x&d)L-G;a?V;}hI0phu|4C}X4bL1g=2HFRu%6Kg|JaFFmf!B{={Tkh#VSSx{A-rW%4Bq=WJw+b0Y}kJby2#&OSlcy~_Yc<F&fwo2!1Mk=2gdt5czw+gxo2v6Q@kIToELwe(epQ~k4;yxf5ulqd;c(;n}z11ZoNAS@7V4p_e0GHk#kVL)fw%RHsL<tH4*Pa_HROaPp;p}7clQDH)Fqx!}`_3CZgW*#lz31U$74+j>U6F#vS<ieF@_6ynu1FDlF^JmM|OdRdVzF)r1~cpL4K(YSUcMuWw)B?U!p|-G${vos1;!jQY1fK>n?f0r1}<4f$+Q3-jU>DZDl4IQZWmA)ct6_<NLiSKNQDEJi(?y@vK~iBea_<S>kDbQ;<>oh!WMNgdSNs)CY7t#?V>o5pU#IUZF6{4Ts_HndWR$EP&%zTF#jI6Oa|LpxT)d07bOyW{YFoD0@!@Uv_?@?QbJbLoX!qy3B8vR<ry85q}jf8p)h(665J82HhPgtxgwqdxZ-$iGLd@Q$V~;>Xb@itBD2{5TvqM^?4Qy(|9);jKn>xj$Q9u0(wnIfOWy&&B+<n*#rDj$*uZaZj+WPDY;VoWkD^4dMH-VE#USD;fRX+=zR=r3KdG(3{||O-G$XJx4tK`rz-GKA*wwH9ro;yi6a2_Z>OcVjdkoVBa_vi}x2luaY?RUH35FIlIt)Qij~0EfsumFKu-aynP<(IRd}$=;QB!fB&o0r={fuc`nvRI1taSbi7ypf_tNN?IYZ8+9cw4?YrYKuBsaD8CFf+TUb2<rGB*9U2(2#=^%MFjz0kJm4x<wN%DToe*YWlt?{qI>w(R1-<j6~?JGPG-tjULb=bBl>TvW6_#ZG#w6Vtv^HSw4{2ZPm&oP!m&Edzz73WrgDEuBegZumnci}B-K1==R)A5|84{V9|>?Mxj{ycU#_KjC<!S9}lexkp}?=ro*gAc=VoOM)w-eX4#ua`cCc^naf=cDLxh^KN4&IOlRnBUyG@LH|=a$ec4eZaYs8VWxhZ)4v*^9aAEHwlNIS0506HaxExCpO^sjBoF7p6(7py)82^-r0E0HJ%m2{?oTEo;N)I!a8mB6!Y8I73)0i9O_|HH0ojTkGR(+ecdAMGfLyRyA<9NX}1!wj-uh;$mp~kb$t@gUyq9-&x0r7z0#L8sOQRuP@jG?;Kv(&taXwwUqfc2ed<Ew?cpipEi3}}k9)(gj^eqWFMo}Gt9Qr#_h&EETe*+I+rByD@8$eo;a(IsSMFiP^dWNpv9+p!_8G5)*Ikat-yc~k+`>8NJ`wK$f7*k4gwsN_Kl=~v&Ev|+-{n~&+T!oNy2Ri;@|(?gpI<Rm&OxJXemRHq+ud<qRr&+xMf>XDrzh?~e{*rq{}6%Sxr^t<dy>X}n6G#T&a?d4@poslm&v-e2IrFdw^poxw6{(zjCxKi3BFYPSkaTtV?W$^1^h~9)M2^@#x)`p@1cJ1!+YbR4-ilFin#B#nj510TM{<QxnLdn7vAruhRXh7%jk2qS=ayitJc)rH|#Ez%oS>ivsOeK=AGqFS{14OW$OR^pR|s2`@i~=)&}mb|G$6ITE$7zwwmH(N^w(;n(~(hQFxgtKb!K*wAJsiU8(y~6dp_cjCd^Za8oLp-wiPJD-C)$@o=_zMN!y?{iyzYC<=F_D7=%OtNwOoiD@TA;m#C=Yf}{diMk*0PsH^o3fHF|OI)A01@&;^;T%s3io!i93Qwmfyop-nViRqJ$59kEC<^bVD7=_j<!CXr4|yNvWij<K;$@u2#T11PQx_*L&N)9!y_NVl^<L_&#CwU8Oc_JHka{bz(p89+E=IhNSbc8<by@0S#C8pO2z4>yV)Ui35{1WT5QW{TorskvTu1x2rWIDAa3yM0-<2o|8`LUy25p7^(I5(cpzcbnbV=eMwI`Tzf}-$i>XXEWOj%{h22&<d`%|wX_9tFXQTPr;;p^0gh_{+@%9K#*^TeUV6R7_~Jb`#T^=0B2)Yqsl6JI0#gQD<D>i-bGBz{VLp7<&82g-To@;qbB%<U=W`xM8MnSX^VQWP#v9ZFoDxGY8C($o`(CvZHaDGFD}GUf^tg=?BpmwF@h4C0N%H>j@>Ut?ZwP!#@?qVR3%>%`YNceg1DpQGMDe2#dM_HV6BqA1*-qVNEU!hNXyiThFqQu`Aty`Fd&^&0B+#7f^GUPF9~`a1C~;+#&<e-JDEl33}d!~;#e)Rf*7g;!ADC0;@NE4BLGue24`oS>CYjrs$z(yxh?K1r<fSz;v$FC-U9ypXsHbu;2F#LX!RSEDHWBSqm_)RDxsi04zEB|gj8=2Pp$^ND|^4kA{%D)G<6l_?6BFr_4Q73!+QRfxw?2N91WK23ds_ylu!nxb%a=JNxw(rVw!PPuQ|Q#9zw#8ZfCP**3eL0pESa4A#DQM*uACw3tYr=Cn4PW+boKJk6V_?EgP@h4Lnn)nTMEn+1Kr>K6N)O%xdKB=z~D^a*Sbqa9`zpHQoQ@)z^ds7lke880D)GLX1)6V={*$1h^h?Sl|yqw<+qn<#l;{2i^#-hZEQ+<CSSAcfr=L)-$>*NHiL}54TKEy?-3sCnVZf#08b<R>0wo-Q|wh}j|?m^s~xPvKEsKcpy5Qh^tr1aoC^`Ng>l<v%VclKSL(v5S~jj?9VU2Ep7D771PYhpKIS88|SFU*;P+MQU5J8Qw6W4_9Iv9d0#9CHfmr8(=ZImfJUW-b&~`jhr=eSS1`19Bh9ePX+h<P`Q|t{O0ZN)I6(!q3C0rx5?bdQvqQP5cW*amT0+5-UA{Sm{w&@JiY%>1z~4;X#bGI^$BJa5L&b#LbAOQ%4iWm=bHs9_oF>dx(!w_GO8GAHN?>Je@k0csg-rzp+_ji)GGY+4m4i4D+YP;>Fm#$XBPtF!mV6H;DQe@iFE_VYU9%I#%m`IkDo@I_vC&wN`-mfd<`*Sc$@E)OCrKKB55^VB4=0g)^wrh?PD<yp8$@@lQ^$)puJuVb6F^oVibQVth)sB(BRiJ*YbqcV-(8YUS61I)gZa{VMzueJPyF<a3ykhoW#k>YT*+i1V8A1GO`CPGV=`>=cEasB>ul^J*YC^Pj@msB;l#BmRz}@b}bth`%S!O;I>Mbs^&X#04n|7o#phT#VR4U6|NHT-=nR)CH&u6Bi)<fl`?HC`?~@DMgsSBJ4XKbspk+W>N;4GMb|BdWymusK*j-AYMaJc%~^$sOwXYC9Y3gfqEcu1>*0h>k%v2tl@K|4{HCmSGYd)@7llq6>h>96m~K74^GerXe<5zMd2vwgTzt9A=I0RLx>kq6y8FuV%<Vp;l~<8;SwB6J>n9?ji^Tx$D6WN`5|6SyOHUql_?(7Es53Vo7qO;O|+Y^T~iIXC2jTj4z^Kv8*Nujy#hDSMh&<z?Z)(xiJQ>g!SC**-cGFaku3NS?Tyr{s1Fe<euXJ<#H(n}G9|>6P~sW1Lx=}c4<N2&N+DCK5$B_w+mvjkeAA#mYrs#`7);rvp-m>I^l!vZh*i57Qx==DfO;OWuPI)pj3oA?o%z{F;(4@Ja7=Mo#u>_SRO46%a16@c#r|R#>kitgpLXm^;nuWUa}G1HEA4#DLm}qoGxM>|N&SCUOyATA#Jh;MP{$KTnKGZ>o6qkkJk1nuQ>Ieeh&!6no?LtK3fDHJh$(fb3lm>4<GN(ZJL<oQ_nVTW;qxSZrtmaVrkb*xdKqyWQwE#TmUs~D!Nk+3rxHhT4D+d{5_e>*?WyY!FK1u-sgsCRe+}8E(haiUMzkAo?JBIsuEtlG`fuWST+d6W<B1g?Y|41zCA5c{($|!p#Qs_Awx%>D?n^t5DV0shPhEpJ+3f#?DHk;0hqQN-+e4g8JIs_=Q)UvcrQO{Wn<*WLN6{X|wwXALc4Nk+;#kXmV(D);?UwZCLEN3T8p{jDnup_1w#v^O=1=KO#FLo2@x*gz_h#;T68q9_L9Q`zZ`!$-yFA2YXs0tjzi7Y@v)F1Z3B<{?=Wv{1#4BlcV~)BLkDxt*Z8Py4+QFRn@zg_!hjJ|AsV5QFV7!f~%Mh30I2B&W7}qkc1lmm)S4-k<w9`2U4~cUzKMR=uImFv&&n7pCcmeI<jI}p$Anh*XS`ZJXor7`bA}&okmAO8w0jFoN)mY+*f1$mE`J6?(lC}@W*q(R<Z6CHBK|O~!kYn;??6YZ?X6$8%yU>njUrQKM0`11^rwMU;+6ueUPGz3ciE}Uy+nMK8)C-7}9OCDz7~2Zs1+-@|w=;+XX%C?8LOg?ZCFVUJacSD0nO}9Ter9~i-a#Et{2T4x*jC}i%;`MhCA57xZckz#+VhBgiDzZb562Y9v8<pyfN@qL?m~Mp<66RgchL4^&RY|=r=5>=_L(>bZMA2s^HJ^53MXW-)!7nEY^SZx9JN3D6WeGjQD;tDVjFF>e$`o#pSTWfb%v<DS?z%eU!tw_o-8<twmQGm9vn+NRr`03R%c`f>NdnPY1@dW(w@)QgR_jspK;e=jBOdavXj{79>%haw(7@&eJR|4c7BfS1##wBBTc>333p(nw-D>J)#v?88D>f^;sDz1$TcPIM?0@61x=|+U6c5X+23<h9%;ZAY40UIL%fgnTvOsqSw|d9yO$~6ri>=;n8gle+tK8dt>T@?m;*SriHxfq<6p;q_p-k@+O6on7jYxnDsDB-N5lm=ZuM*s!5l^~e+o|~j$r?hj3JVrDcqkijwJ3yyA5%F;-<8nnO6&O-Yj{(XUcKr^bzg7<PwR`(2n4kR};^r-Gh1bBkq;Op3Am=<di*<<Cx4b45Mvf%x#$Sri`;GKT~)$V@hNk>u5J+zdeXs(Z0w0t8w4s7?rJ_trl?}7BSxn&m~?&Jejs1V+|tiPur8&kGKu(?-_GBVrSYak2g&@%ADS#ok(sw@p0NJchRQICSFZjjdQ3eorwKt4<(*W9YGw#vCQQdM$#_Fm_3Otv{y5hX!e;%yD9s#Qg<R&+KpI^$C=~4$uTN>BlEtKcu^KR^Z9iybsX^`+A6>587_o4i1uLGA;g}vRp08_t`KoK+A62&nJhQ)P1@U;?_JbSvS8Kr3G=9)5f>0g(^g|w&!Aq!Lun6X+e|#0b|}Xd$1w!aF2^xcBle^n!`$y;f6=tv*k?Q9PPEmS)VQ-T|KBqYYR^{Bk-LbO(pEZ(SnbW~*(`wAo3_FoX)D~0wpyp^`KmT?LE36xR?k{$&r|pc?R~@-iTBf1`>%T5izA*!+grmvI+(gGaWM5XVsF}NEIP-da~x6B(}>$KUKM}Wj!xN%WdA??=kxykr+jJu^&ivwU%&a^f1;H2n`t$)fB#^qYsVbw{iv4B{Ga;4u!*|mX#WF`(^%R'

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
