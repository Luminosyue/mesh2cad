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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_008.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_008.stl', 'source_sha256': '937aeaf8bb425a87aee94dcd26abcd5793a47d56c8b081a8b18f448ee3fb9485', 'input_faces': 944, 'input_vertices': 538, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.33507847785949707, -0.37187233567237854, -0.1454961895942688], [0.33507847785949707, 0.2524293065071106, 0.08941926062107086]]}
GEOMETRY_BASE85 = 'c$}r32UHbF7^VBEpdyM1G257PWQ-`!G>n4*vySPhU>3|dw4!1h1LlBF%mGjY0~p#I(J{wyo;fEJv*TL-y)4Y0-E;QrI;YP4-leFn`YUu*zvhg;U-}HWHT?6`!dHd#d{b4^RC3jFYa;@O4C~u7aA?J#L8C2NcJbA}6b)<MwwZrNi#9?VTPh%MXwM;~YU`!Ed(|veUN6-vc*w9J-GjOX4+#iV{;%B!3=RD05AD-^P~gwcrGKebv%FrdOnH60{{Q&TMb+Wu;424ziv6bTno@IS@;s$Bt-kn<Aq&K}4{yChJ{QO%zAbP%{O5xfDK$20;v1n`E{pGyaj{Y@_XYW^KTQ%fI#yaKT4{rP)+XLZ{->VH<@&Z+@c(FWQT#SRE9A4^Sn;i0Cd+lLzF*c#J&JZg{vmeBZ=PCjm*4wbPkeL3XtZnMrU>yLRYv}93nahssnBXEZ-6_>pXzsBboy{9$C{8G{+Zio$C{7p<@atpz9gR;UYGo4hbB@Vz4t}&t$i<{T`i4u^7B;*;@iz#$looe)W=$JllbQEk*7uHz7yXVvj+Zy5mHZEcBf79`}IfSx`94t<nxAoQXl)-Zpc4*AmY}1)CSRh?Qq@aAC8L7elGQKIQgL*pJGyuUeYGMy-IoUZOzw6J@u_sw@5ut7e>3n<B!SjuZ`U(`tq|}PfMC^O8&ZK;Lm!4dJkMI`Sl$Qq(1ufr{X&vg-Q9gO~cWycL&6`nx2Q`=O15emi&)mQU3iq5+7@2|80o(EcD-7XUVU>?kDBgew!%1zVLIbl-qTb)ZZ~<5XvcXR?4x@?IOOu$rsnnvq<V`9ac9=ejd>f<y?QXOZ?wGBjxwoWJY`|Z5H1?ec@L5`Rnf&<mU}W9K-l<lX`0XZi;UoTu|C$jT<QC>wB+=Z~b^i;%2>3b-Vmtu?@)oW|)*~%pN7aEjdJdGvhMJZ(PkN<(Ov!kw3Z-@=tFPEt;jR`1;|isAur%9TJCq`I-M*fBD>|sra_}U;dK(WqV0}!>yBC*KzT=_~!X-ljP@b$Hz$iSEl&(9luE&?NLp3ik8}j`~~_OlJENrDPMQ*CcaUl>}nqsml?059LN4HDCd3^iI1c2P06oKtp<PigXNNcfO{<FS0R*N?4{Jl%$qw-;@A7td5ohF$!~0Smiib&c4I#0aoeeU+o_ePXZry0jUxWz<a(_diEn+=4)e3M79-cK9VOSb_I!0t@^?D9O8NSS;fSmAQ}L~ZuJ2I3qeO(1V-8Ia-~Rqiyj<65ruepo9pJYwC%(3S9?Gxhj`A&r#K*|pT6|;c<3!27aQR;4TeB}fJ+GZiM7{i^o{r16q&|+Rv&A=$b~r44*awNT^>A(Y(V4|J{JtYTiRn?!trBSOzouN*kvZn9Tz7YHg7_0w>`LpKJr^93I5@kay>;>-f3vt_QqOk&GJdq9Kd?@%3YYde8tp<qdf$X!aK7Z%)3=a*xB9LX-}D|L_0-pYLH`zPgmvn84#}@o9*TMK+as)-R~|`y?1^2Zd~Mfg@%4YgPD?pmTx5N-E$WW>U%kh1$^Wdn)L;Kz3HhIOmi+&7UEQ(glxWC>Q{qn!#Cm>jmH4{rQK^qH@fqgV{-Y-)f7!EAj^pnFSjSurh;Mj&JS*jtI6G7P`hCRLEF}|_Z=Nk9_g~|mA}HrsA(V4Em#nMSDuqzaunAI*kx+BCTz5v%6XH+Ha9;em3%ba4JhH+M@s;xJ|2&fWwe|R4$Hl+sE&1)MlYOOK6IY6_naNVV`E>UJ$zN;<@}EC|a^_ZUgZc3c>s@5TIq@^ro*}<Cb|w7UXW=Innj+(($P)OC=Ht4)Z$`@J%%SkBpGEo6pQlT|MT{0-3pobA{)1&QpH8+z{#EUHU9-2uGk+WSSq38i;A65Lm@&V?Uzl5btI;<?%JHiOKfW^jcFopE{KgfAKgSj2AD*>DG%`Kv6CaHH1H0SBKX+U1uiCMi=*QbZQogbCr1(bI0`c`$_1B4iY8mq9*p7PM^;|0T8L|}l^KM6cf?JG~^4!Cazju(-#|#OcB)W43@^|Tn>t2tP`fHw@;g=YX`oGz^NUr-l?uhuY{Zaq&kJifgD!&o_!@2*7gBd*o{^i3c-+#LJ_PFNaYv;eC{`H0|l%GGU20z1n)N^pBFwxzY<vy*A*Wj-|D)F(#`~|;vCGm}|cV+#v*WP^yal7!JI6J0oNB+c-80VKPb0u!pamXLB9OWO(w?N{M>G46yUwpLWH@mfODW84ji*Gz=iufG*K1=eCr~`leA+)PvDQTCH`2B$RM|U9(!4dN$f3G+2UCN@IYb64tzGHm%iLcidU+;cK)(vam-h{O6GI|XO7eDbg@wKimWZtFh$E^P4kUwM^>XW>6nfQKB;>Dkk0p&DXk9~EnjC(}y&Xsbk+m6V3Xv;lgx0GMg4dXEW67Ij1x{7ZvlKu?FZAn>gZSRw0z1RA_M}6$+B)@%AJp4=*#dm~kMLDs@<@b!-We>`ATRfG0iml!o+~1D0IU?oTYKrgJV8MN0=~G#UwLBvvj<(6AaeoeKi1l`HA&H}-PMlmv-(OSe>8QGVulOS);Cp7oy8Uf1{OQ5s8->QBo@JLyJ8d~U#Mg>VLVRM6NPBEwozcGHQ>A>ZK#Sd|XH&V)nDgFl7r%n*VfkF9f$X#FzFl!&d$d%>pV>Q3_KD`q%D5kWe=hAc*YuYCnSI`tqY}??S>X?!hJ9$j{*w})R+Xh+&8FqxKe=~8u4{R+U;OMQ?kCm)Qcru^n$q89`9<OzTT4s3Y;MP-{^t3)$iM9=^7lKA{0AGsZ&eQWm&htI&K&7a$~ngV`mU_M_B>;xy^c-CaV{x5c$<{(XbFGR!!?q>Wu@Ix&-IV6e?Qwt&QInb-IVtB^G1Artd;R@KOHLlYl|I)_J*}zCH0y7C+c%{9_qRJu8eED&oZgM?S4`C-Qwh2XrI<Xe7%jA^t;*LM|}O%IT=^xTAPe3)BT5>FYV1gN&L;f+amr`J1rIeQ6Y@C>*o=NO1-8?dn@d~yb529_GWPlk<ZT;%#rp^2!%g1LiVFZs3!5z7IuK&!cX?W_QvZaK91;Dh=WhA36lShRhTc2JHijmF8fh^ad8<B+Ue<t&&PnVGLNF1WFBd=JD~or?~O+M<Nn*;B6Gyo>vu&w=dDHDqIZoFzt$=#-+s|$ANu7N@$D<SNj$9^f06u-8V<QX+g}wD->6p{abD3M_vaU$5;rs3CyAT6_NCnat)CO5p4LhJsOQeNvnBuO9GLF|ykwm<TRUX^*7Mgx`3-wx{`Tx7>#M$^x75>dd0sr?yg__>=mKe%ZASv?S@#?AuMEdJcCjt|5>MvK=fL(d4y`MAzWn={+?VW6J*8iaDd*sK^TT?7-%0w>TFMvwSmTBGDf7a5+JGMtf&1#fzh(St4VJ^NJw)!S`Z*_z&wq!bKJUiCe{famZwxt(c8!gI|9Capd%hX`m%GI`niRplF)=5~srUr>7vI2obuAC#_C1~KFYIG4$hu*MxgS8>Ziuh@1j+c<j-<mnoPYiXX-_6MS+9)3$KZFHyiv-To*n0uUBfUw-&WWp`QIhTdT2lPFZ?%UHp^#A9@)oOXZT~C+;80?e&E}M@;S>8_~VX6N_}2+MtqhIz<PDxKT7KHq66By_Jgd?X12jmsLvIw8_k0;4(~OMmi(oEMgEiLQO=8t;-{>WHjiV7&pdCbx86EP%CT;%fcwkDmuQcRDdW?s^+Mc2qU2m>b;>B?*=SrG@hMP5&P#^h<pc6_uPg9>-jAf59S35iAD7!CKDL!(ccNch*Nd*c2fz3l@%3!)us&beg!^fm4D$Qh)#KRbH~fzCMX@5{+Yfll__6NGhWqu@-tZs4m-(u1DT8tN?V$KZ{9D||KbR>0Yuz~Uxlc$r=Q`RS65l?*J^CfPFYcQy$Ltb6$9Tjo$O+>!eLa~!dh#HwKlZhV=j}V<TNirCInMU$4cy;byvKao@(}H+`j@P)X0;-F<a5_Z)N|=@?0<^2g1<R}`{dQKUYm0x#J5M>mGNnR(go{Gvp3?W>@$tNW2Ag*vmiM?Yt?_pKCN5{lwbdW_{I${885ar<)vS&P9NdFc1QmDtMQyCGDfav1bxDID_k7UH}1lBge^w>uiTgMZ5?n)eCupislPVt6UMinr<|*GCqMYp{*ig*$WmT>W7AcvV_O4c{Fztli*FXizSL3tJ?2}}rZ}G;Z;JiQ*H@BX8#_~c+syQcTNa00*HLb{_||OR;@f5gNW0C)D^QN_b?hg77IhOpX)Wr>{guA^jEoaA_z>#3HwydV7Ot}XT1UM>{>)oYenB6Z|F(`_#J4YMg}7N`(5^c_kbllS#9`$T$?rIrd7tFVHw)v$c#r%Q+{D+C^Pyjs4aNFv9U#7=H_Fkc)|U0o+I5Kd#*zy-7qm&7htG!iW{JYM-|e1>`FUox_%>Sy$#0$8T;{9wx?Oy0;f1(QIlIfevbjbg|E!9L!z&-eGshm(|7cUpi@0%EuN)UqpWBCVzVmtitCah}X}{>_gNT1eudULa$ZYU0gmE2MhUZN4JmGKr1@(NHEcG;<%ZvYWe~oj~fXmYFX8kJ2Uk>L-$AB>#Fdn_c*Zeo3U5g?m4rcL2DCd#`@wxI^d}Dt*@$DV+qn_`xqP@vB@r{+~|B}z067k$%_5_p@J{{xXTrO#sJzyI07aW51r?QW<%b2oJd_6WC`CoUF{92c2_`ByI4qaMdoX2LD^;b`ibCzTDaJg?;ALPKg{4zoA`^J?MvVYbZd5W*O{y=-Twvl#OOEiFA`*-OVtNsZ4SFfSs8_${{&ZGL+QSTAB?%U6(XP)J_U)G!|zAfo7=I@%Dc&-*OSA5fLBIc2$VjRYK7_NK&2+oNf<K=v9E501%|Cv>MTb)l*zV=}g>eIrR=evhezV&r9+M6jE=OF(*QoeQ4G30mYi}ByNg`A7cT<>t*E}JoKeVwIUwq2U+M;&*UqP><ua!xl3W``e$d8AExkMsL)`Ng+|x#Rv7URkcIeJ%svqdD%scZP^>_NykoQKBBo?{*&LPn`z8fd}SqnTv8hF{{mh-zyUJZ#f(F?7LHZ{op+G`>^gZ-?dYxP|w2?a8A6xLFTF1@G{C79*5@ur6Xk>u(kLizWq1c7xX~~uzy;WQO1ouc@X+>aBkdR1G1R-+!=A$QBLNaHqTvr$NKrWu17w}uh*!BeP?1RnHToZy#1tIZzrLgx06x-$gmYspBf90|Jf(pzn<@t=gs!c@b#ojxbK%NDfeTC`)btl?IYPY+7=|?d1gce{AUx8zub1oZ|c$TV@@Idkxmj%{qrvP)ze9Q^rbVzH@y#_T`M=?9O36K<>>Cm;p=zBH)pjM-?sK7=9_0dtUs4upue0h!Y^s!e#CX#cHp-7T5DIV8+s2}H;hL25TD@*h(rHIGEVd%_mSTci1KgslYOu?;x)=2Rs{Q&#31Z%E+-+LNrTb9&reD@_OD;zdxv0tjq;Il?3sRuZ?oscc)pZ~es{@)=iP2~Fdkyg!Ecuh`{v6QjL(xj@O*4sS@E?wez;GCZ5SoLU#AxGCw@l$-@oA;GGZP49TES1e%tm8{HTX~?$ia}V`jUG^1t1~bJ{iO(JuPN=AM{Gu~{&l%~#0Za2(<g>?6-n^-&+;AM?aI?6gJBJ-YJ`Jio9dVSH}uBjZyy;Tub_UfGsCl<{e}XtK}Kd{4;!&~c|D#>4OF@O?w5FZ!`sb2<0gwxt)}v<$>JJn|Il-q4Kr-eS-Mls_vlBCT%}{D%C&FT*9@2Kvb>68{s2k(tD|yYE7K`?itt^?%`OGiG8O#vhjRisM>VeBW^5DAv_WrR2V;FLp!u83*9JS+_C9zkha=A5a(btKtLkjpgvIQy;@W@*evH@7&l2e{#XN%9@Pzp<f>O3!Y)!UbhtEHpm0lowW|v9UqE#?rR4>|8R_}h~&jm|9Yd~_k4r;Kd6EB?wA8VeRu3PzV4iUP_DZaanMI|ALTVw%0ILW`D--C{F?I-&$sigK>in3G2UM6MZc7Og!~QKA)eX3%JX)6!!PhpcwsyTYvbhi*XP3Xi$9v9AGhtmyiTD1PiEBTW(SPVdhX)eAJxJ5iKrp@wb&xaU%?sk@oXs0IZHh8oN?hj#J|#1oWpLFL;j4<vHuM3FV9i!K9z8;t2PPaB=07~ZIrk8w)PJZ|FydGi{89G%2|i~iM{O`X|L_QKk}Cj#k}seJ{<Mx0Ds#-wCk5he7_ge8RhK9zC|1BhPeG=Lw#NbVxN$hfcxf?-Y92qIQ*>tqCT+$kUwra%HLCSrR2K--?rbB`Do-jhW$q2@!~t;s$)Ix(*oma#x|7W^cd}$bYZ6Wj!4wA<tntRg==?-TbDEN`Td14=Yl-{u-|+F|6Dxk<2PcOl=H>uDCWaQoL}x1#QuD<tN6zJ`xtM%w&1yjUv}~B1uNiw`ei=O$wfTGx7EWuG6!Jau6q{3bB*qsaoxagQh&XC3HYCuVEn&+HA2<X_PrMB<5Cps%(EJ}k5p)k=d;<eW1beyiFq0}82-b2h=0O(yjS2lS$s#8{3yqzAl9*mGvLRyf}gw^<Lc|5sQ>-Nh<}G^7`K-e!|#0_>%h{JxNg3U@K+zj`u6aZthZ+6I6TKZnvCZm6Nck{)OGjKwByRm;fnk3h-0Y#{{Fab;t%BaI)V7-3&H)O`4l-97^}{qoLghD|L<Q;_L=7S3+R`H1F-LPE-d-YE;mqq!XN0DWd&m}FYvt8@cRS(5*^xBuJ4l#-}@d~gK|3EmVJ~XH^1Lq-3jfD$r>hc4$ULJV_h%Qr{HucUtdsBe0y~d>_ZmclJ_ojOCywj?JMqU?YH2(9P=y6zvG1QFtOk-G9F&~;(P0x&rtsSk$4_dt0l^xi~FqoX&WiWQKBu%e{u%x-QP{}JNySBzgIAx1H{zFbAW=wQU35y#Cf_Wz6U%%4nEI)X2uP;U-y|HzWM1h`m4v0n6$p;z&YCZ`(NCzGlbxK=xsXox52ti^3|V)a>i9fJtLfCzBpzsK|H_WxrD7;YiXDHXa({|;oN6z+k`lHZAAG^Z)1IUT}9sS((i9Zdkf{l@2#zm?{C&cA^(gLXxEB*vTi%J>_K~dyW{!i;n{e9;phR>XA<t?_S&tnAM11y<=4kK(Kymr;%R#W-}JeL_~h`w`Mpd|Id2=4{>Jwp$Mec_6+OR)`1(G4zhgZUj{dUbNB*7eh{KMRlHW)wjQrLE$e-md;_$8s-WzZ)kNfP#l@fo)nU*-`9|*vBE9HrLKI;JAc_8W^GgIb^twdKm2jB7u^ZjEjDc^MIi|3C&Fy3q}SIfE2(Ju(~j0nQ>Uf-j5j=5np>eCbb{6F8X*fkaPALxVis^KfVf0Z>9<<}b_`?!?%XY}BCD8Kc3)bp3W=14#Ou}FMdfk>>wUW4R3uG`n+y19yBUR;_Yaj>s`hjs<kK)>fIBJVTUKU6z`@jem#yCPzi_#NtsuTM_IefH^kybsp1vH12Eckn##@FlcsVPEmB^OCWD*S^W~VZ8>vC(|waFuwM6#B;gWA9xP_$0@{X#0tDu^G^{uFX_wf;(H&LS@Jy4aPr3YB0Gl4b*)Z5^8C}VZiHXG9pYJg0Nw-ii-w<E1#vCf6W=?|{s;c5i2uBQV%&GYpPxzgZT8>C;(e9(FT}St+>3rGP*CQP=3fQ(@9SeFzQ&KysE@Hwd_5o&+S@WK-XHrEiRZHuieo=pwkO&<{0!Pzr8(Y5>T?y}gRXfFf9_g&AH}wE6yH0lih94rdS*`BiSpBVVcsTe{!_~NH5lJ3C-uTO{_`Q%n}hQGsFpVbe*S&9?)5;Fe|0|A>(V{sIgYK=2E@%Z9{aYBhQz_K{si6!tBU6f#vl9T`&B(=I?8eO!hQN-I{AJt<vl24R1>UsmXkQQ#mz(cZ+gJr9*XO-y;=_3=ZvpT*gxGGi1=KYgZworVPAiC-42YC7+kl4n>;5@dC$#gSqAgr)?D!&6Z)W>D12XT_sE6s;Z7_?{r6PIe%i83;%m?0hws;a^h5q@QFxy%<$bVTqp<Gm%Yo;i#d;$?NANwjz0PGkpRO2;`ecrwA2U_r6I2LsuqENTc5ggSjBks27H@?6)BFwceBavhw_Ry{Go&Z(yL?|uo8K1uwm;+XUdFUXi08JxnCCNm@ZJoclN;aH!@p*ibBI}a3*JKuNP@rl3i5x;i27X1h<(G9;`036+<qR{J&yg2@%g*#hip&2Vtl^EK0^!h#`jF^51{^6ry~E6Hu4^mz9?GOJ+0`0b7|{iTVmk7HIHQEADCVC6ZY_bQJ)F*@qA>(NX)}A8_}+3t+1a6^_(I3?^Q=VJ;%Zylw01zvX5JW`J(Zh&-V}Q<0_#3H;#($ICC2B$Mral@4wpR!1E*XBEH|sa|8A1T}XW6dS{sz*51)F@2oRx!1pMI?=vnumim}mTEK7kK*~2>Zo+sR-S0o;Xaj7B!-8?}&sV_vn3*-nuXSI7`h2P@`(VvADhlJ!j{F~*;JsX5Z@eG4?2!0+X$RtV@EzV?U3Ut8({FgMILifTmpSMj$~n|SuAB1xo!KhOg|zc1W!*DlbBk|HxQh3{hc!k1^QFbtqnz;m+UyGW{^FT8%89UId?ejQ`~o|Ouk~Dx?=`=4m3W#3x{Ghi)c|qJkO|{FBuIRt?+v_1-1I5tO}`bW&y{Grm&EsJwG(#K=T<4aNADeu{IzzWoE<f#eA}4L7@wIgpgzYR;l1BStq|t||Dc@e<)mG<`+E?F%CE(D<Y^=2TPtP9dq}Iai{cOchWB2Rs^h&%_x$1;Kk6esTsN!}%ZP9GJ|*wZ>-)dR_xslE&BV8MeS!D4*NsB_Tw219orU+kS2dRUSS$1w-+t(<l;a5U#&h_}1L0R&hW9!H+_5f=ScCf1TZ8f6<s8O&(Fo*ESc3P*Lu`02yZ?36)9W_g>#P=o`B?rb>a!~h<6-bz%)89lE=f6BF1$y~{i@a1TYSg!_wwGp?c73))9||Do0;-q{9BVTo|le-9~UKY(2m{0xP3hu<u81Pzcctf3h!h68ZW+eQ9RyTPg&0sF2El&PvT=6eh%~T>O+*j9Ph=OZ7k@o?U^p8&2KH5DC69yP*QyT*%-X%UhX0G4<)*ZZ|jr^<6&xmlw(FuLw+|mj6;v?=*Rd(@wJ4%@b?<`p5y(kRzHwGBpm(dI~40u#o|{a|KDp+|MB?{=a+-UPx<=`?ZxZ3gZ}^dYngG~54<zW|IG3;W!7?Qy}GCQQyFEde<}LE|5KU1UjJ8rDpSkL>;LypWq!A4TCJa{EtBE_)JEh1<Z0AyWThj?)5x2tOUawbJE>d9JIM*u9pnV^L24}dAo&<Io_vgahH8?}kS|kDkS~*OQ_quclkZWllkbtAQvV@8CBLCQBEKPjq`n}3B>$kkBmW?0Ob7i!R!MOdswEv*CB@m96z8O7Am=1!qyB3FXCr5(ej=-+I34vZStZ3^={+NVCBLUWAipQSqTV6DB0r{HB|j$LrT#^}OTI}xNxn(GKs`*pKt4^~M?OtHO5H_1N<Ki1As-;`p>87YA#bNnCvPV&p$;T3ArGUrArB+}obFofpQ+W)REOG;+>v?eFe$D~^(I#)7oe6V7a)Jupqa@kDgK-4(7-AwK2N<wR(h0to_vJ5hkS&*o4SU)n;b!1OpYKgq0S~RA<v<Pkd;m$&msRwol5?bJeN9+JeNG5NpUE30(k~?B6R|JB6$pTG<ghpICU6#IC&6t2zd~B05ym_fZT`Lm)wWkgGq6BYA<qka!2YP<c{RF)HdX{WPfUNvOn36`a9W=+?e_+xiQ&?TA%Dgu1&2=u1&5^twF9%u0pL!u0k$Ptw1hME=eszE=l&JmLPkQ3s7}(0kQ|RAlZYQlbVN|lbn^BgPfI|iRwzuM9x6XNX|gEFey$)%}h>5cA{n@JCR+exyUYLH)?*e8`+&&gzQevM=eIqM=nGyMJ_}xN-ak&N-j;UOfF5XNd1Lekz9>hhg^+ZlWHZ`BzsdEk-f<csK1dLkbSAm$iC#J)RyF?<W|&nWTjomt;p@Ey~*v#otPANr3R9_l5I?idr}9Idy@N8hm!k~2UACp2a`uq$C5{q$5RdRc=BZGbn;~KEb2V+Eb;>Ca`FQ53hD;(3i4(q#WB<!<QVc^Y65vL`55&C`55^x>P7Nj<eSu6<eTJ|)aT@vWOoZRw*{<{;)>Kt<cj3F)ZfW<$*q|bcc8W<cOds?Qapt^fINk~l{$^AbTfG?IgYxM97o<yO(5?lAEzE9A15bLkC79}7pZ5+7s)rMm&rHC4(e^PgZzYgkNkxEn);Odn*4$KhWvs2o%)gdo$Qnj`h%>JVi&5~6T2`ecB5t?yODEKvy*d^J(v{drRF5(CA(9zk=@BTsF}$*$gb3MWLL5?Rqd6X`B||>eNR?N@n?Fk$e+nc)W_r`@^k84@^kWi>P_-}@-6BG@-6Ze>S^*7@;T~J@;UM;>H+d8@*(OT@*(nW>UQ#Oaujt5If^`!I*dG%97OF%4kCA=wjy^Tw_{TL8?`q1H*(FNsUWoowKlm3xj3~BS!rc*adH-F0df}d3k|CF-!GUH-=O|YzCk`mJx^A8gnW*Cn7W&Mn7oS`LEc4POI<=<OI}KyLst4Hc`11rbuM`sc{P*baO!+=IC&8@l$^5XUPN6;UPNB?GwuADw*5?7nG~<2t|G4_hfx=j!^ktKGsrW^lc*EPlgQ(!W60ykBdEj4BgnzjLF8a^Kk5K-KXL%I4>^F`joO3Ujog{qo!pt+f!dL*v@N*<xi!_F+?w2iNpTaZAGry+A+<5NA-Nvahg^?bi&~ppi|j?MPWB>KqE;bSBA2C>CzmA`r<NoaCl{uAk_(gbQVWptl5<l%$hpbcsX58n$yumb$yvzG)J$Y&a(Ze8a(c2xwUCvj(^CJXV_v0BX@1v<Wh-?_b1fIvMX6hwy1B9LO5M}6#hq<cnlDY;^D#C`3#ExwA;wZ^(KN9w%GfI{ou)5Jv#*p^Ow)IYD^aUyseP^3i&|4l9UF>kQN6X)v81>jwSks8_7pdy`f90TRdEw)Q!RCDD{et;MONBgOPv>rTT?q}sdGnh%KTE?nc9`C)TX7*Q^hHBS#bchr<OYR75Ag|*HYIC#lh6UTI$-Ocm#E%mbw-x9!DLorLJ9yCs8MBscW6$nbcWY>e{F{jJiNeT}u_Oq^{6X*Ivb2shi14W3<$DTk%fnUh+=zKI$>@KJszuU*zND3)GwB3*_6>m*m^zB&yo?C-Jl5{1#|Ma(;4EYF%<way@Emay@c;Y6o(Aat~^Mau4!QCdFaYDdaG6G<7RkX&gD4yqCJ4yqA20dYpWOe3qI>K1;qty-2=9zDB)4zDE9=>LCA3en@>nen@^veNBEzPNse!CzHQXzmva_)2D-~GeCMK#hIus<V@tOR5x-~axQ9aaxQWnss}j_IUhAIIWNxu`Iy|9*PUm8l;6$4vUBhZka8_o*2R@)fRws9v+mA31EjP?V_TJewxqWGGh?GPDNU@B7)zzk)5P{UW3Tjnn!dQtzEXNCP2b&O-zvS5rmwGXEGRvfW^A0}*im{a%~(3cv8MD;nz46?V^itwG-Gu)$FkC>G-Ep|&G=UwMxAL%ojZz$QiI4!J6Tfao#GzUc9zt+sklA$H%sbVR$Px-(~>&(6<4*So*7cs3dL$IQR|G-_tb)9l@x!W79p#oI6b}MWTjci>B;vrs5(E~V^VybdV_qOoJc)KR(hD6NIpc}MLtB1qpl^#k=Id|l9etauOqK#QoND6nyfUOypg<#N%0mY#dhi<veH##J9!Ir8#$7?ow|*@jrX4I)P3ab<o(p+<o)E6)C=U3<jd6C<jdqc)Fg5e`~D7-;(w@L$p4V<QdNK7rQV}|m;HT>dYycYe3qI>PGn!6Wm0TX<H#mCmb#9-j{O%)-AIllM=>dmrfwo{V%($C^hY$4;&|$I@^;2Lo_dlTPd-JxOg=@vLcK%2!#G}HQhb$qmwcD;y2_;Z4D~GeEaP&9N%28yEIF3#KS+%xA0!{3#*^b&?*mMVPgAduudq(1sb|P%Sng^5?rDC0r>VbP{JCapNQ&=kNQxh6NQ#p+B*kt_ic2vmZpfs#FO%Z&Op2E?DPGT{cpH=AbxewvF)1F$q&SdCu@95t5=@F+sj8idbNozxKT}aA#lJ8q{*_7bA54manG_pLif1q>{*y`ZEGEU1m=q6YQrv|}aSJBJHJB6^V^W-xNpVId#p#$7J5zIzoyl356zkNYWS#6q{e|pBZcP1^+?d>%`Ukl)c@Q<2JcvA*YLF+BXH#d8XOkCD|0FLU&!NsD&mo6UCy_(QL#TtvL&#mJUC3R@&8aQO&B@iNHOSS;p44JwPjWVDPI5M~6E!2*iTtkyO-EKqaRz$MWM}qe1}4Rsm=qVH>f}P?DpW6W6><}5V{#L+joO)PBM+wzA`d4|rA{VKB`>1RCNCndq%I(@Brm4UAulF}QbWk0<Pp>%<PqfV)UM?2WPfUNvOl>RwK};PxiHm}T$t=a%|>=1f775&WR(<uqN;xV#H9EuRrTdpY9_KuihpQGiaq%ALSzqeIcgPhIkGRc3E7t%K(&zr$fK#l$)m~hs8h-F$ad-?vYot^x{|z>yoS1%yoS7x8cJSB9!niT9!u^`?N07ZZb|hgw<K4fRwGv+=c5)T=ObIFE@TV&tp-*7`j$!YGwLVuGx8hiSMpc(<r^l&-<cHWVSlTB&BLU)EVUfDEV%*Im)wBdlNvzoNghQVO&&#_OPxoaOAe>n$>HP(>RNIHc{Oznc{O=Hbs>2^c?@+dc?`K1wKusJxhb_Jxhc6kwF0?3IWILIIWJkGTF4stwFXuF`kG1cQ|dGFQ}Qe78}b|W<trw|AD9$pw?I|DW@l1dl3JErl3btKfLx#4huV|ehdhBgiade5f;yMHg1mtmPToL{q(+b<$s4Jw$s5V5sPoCI$P=k!$P>x^sJ+Pj$jzut$<4@RsO8CJ$hoL_$+^fMHK;~bN%0e^>enYsiXTv)k{^&CQ(uu^u`eGpec(R&9a-%&Kd_%&nG~0xmb9eqQ5E}8>swOyv5Et!eJrVaUB%<56D+CwVa3a+D=evdX2t8M8!V~&YQ@{Ak(SiGx8n8Gjh58?x#H#2RhHB}yyEfHiI&uTzT&>rewNg;fZ~SKW|q|Rf?{=s@b|N%%bouJ^uG#7{ipVe+JFAX0srf7{`a-%w7*%gnwI(!wZET}`aVQU_wzsXP`r#yefl5GVkbW'

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
