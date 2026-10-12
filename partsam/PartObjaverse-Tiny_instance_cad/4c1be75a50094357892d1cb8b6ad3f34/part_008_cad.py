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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4c1be75a50094357892d1cb8b6ad3f34/part_008.stl', 'relative_path': '4c1be75a50094357892d1cb8b6ad3f34/part_008.stl', 'source_sha256': '693382cc5af6a88576fcad978b1eb4021bd29f4c6c69fe4b2e59e8e003cba257', 'input_faces': 666, 'input_vertices': 506, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2068060040473938, 0.3560889959335327, -0.1618540734052658], [-0.07483699917793274, 0.5221379995346069, 0.006846945732831955]]}
GEOMETRY_BASE85 = 'c$}qt1$0$M*Y+g1yW2%dpjeQg1un%2K?8&!xlo`;u>heIyAZqtm*Tg0a47`mBE_Xx(3T6uTHK3&v-k7lEAO|yf31K0KV5r0`|LA!&z?Q|nKNe&v`KKH#F-8L<TvqsX0Cfu${3N<CbNm^9NE9yH=X;H?A2$GpGmKF`ICUt8?^{&(%R2NnZW^_I`{h~GN7^};Hxeb1ByEWy7Z3hAK9T-MDNH>oyA_K!*~5UTYJB*9r|>(*F}N?%NKW)En3_$)baoLC#4O+z3}^Edo4O*viquA^mdEgFW2s&{nhS`%dB>XH|0UKN3>PD*<J+pwgV4nyF_8|Q`5lDocY?`HK8Ti_fM&I_a9$rduOReYWH2OqIT!Vsr%GVyI{3DTPIb!FV8KtySvnfy&L*<@5`fcdXv^tyJx}K>uSIIQSF|GHPQazW3`(f`l;QK-HA9iRDz%Mf2-a3AP|1a$7p+B^d7aF@r99xqO0M*Nd>g8QwV;#1Y^9JI>J7p0NOWvt?fNmj$ph+^JBaV0<^seKJC@tkI92Lt2I=+r>?(_*A)!ABX0_|yB5c3K7EO^!_T4|$lHRh+TIzEQSI)Ob<pp?Xyn1`5BrNYn6JPq$ma^!&D5>h-nn9s#_1d3hdlH@0ei$&ZSU*+&r$8COBeVb`&R9qtS{B>E**$??k!b6?#j21qJKYa?`Tj5@uY{{)#wNKZ(R=k=JBcBd$B(9bF+}zJ+rUFzBCa1Hb?>g#V*57?I&vY9<79Umc_%K<_qL=YXju%s|$#KR7Kb;G}HWhU!GIDBS|~-8$A*8viJ<z$Mi(r-nUf$X324kYxa25)tw)ZpMyscXNlXWlXb<kUq>%5+86r!53Q?N$HA|9d)00(7u5Ey;a>R3yIbwPZ0(WH2g|j+Z}~>#ITSqdb>E|LI<GE4{B@FJT(@4K-fk^I9$wc&{S4T=SKCF*hMz*&Fs_g?>c^7_c4v;hXdhD)an72Cc*-o-_?>qrfftitcPHC`Jfu&7{Op^AexG$m{KK;$&nIIr-jx*)|B$m9r{nr~#9v?t;?H|s+nZaXkk2FyP$xHPqi(xL!@li?#^ZfI0eqPd348Yb$Y+iz@Sn2>?1u|uUW)ZVy*23$`_*W~Q*=H2x9*DZcKQ`{)%^<E=Ze5QZfk-3v_7;)fB$Ve<Y7uY+BcYuc{$hy?Wg3y`cQ`Pgtb7wjlaZr14rw;xY{*>pT|BOm)Z3N>bzbE+Rq{{*0hGbQVq;k!||}k_ClUdR70MR_Cq|wub`eQSB0NP{W0&aBeY-Ng!0ILjWk&Inr6Uy(m4q656AlKO*LG{>!}I5Z{2LHpM@);ZljAM{*`axr&R&%*VjG(_PWTYC;KTpF9zg<y;nHmZ+{JSbuKgP9hPVw+!HUW-8CmQ;yhgvbv3mZ^6)GP@{n%<>hMhu?br1k?2e@AFy0dlbiC#lf5iV_1oGc^ppMJE=+hCsKRyEX(T{g)ob%qR-IHV#>ZjH?^n3juwL4;`BmM(#k<aeW)b6`o0R6tJg}kMO-JJrw@Fi-C_0abO_CJ$hT(_1WKZhTw-8;Gp>N#a8wYv&EL_GcxnjhD!O?VFWxr_K~_rrXR%%|~ty53g1t8rzl!)w-}9-7=h`@hbCN8{qbyFFJC&%G%a*Mmv$vjuinU?}Xq3A?m?jSFah^=IU*-hSl&+Ii$52i8w__2WC$PvAM^&4;>jkN-yfJ7UhjUh)v?XY70AbLMG`H_IQG-%Z_+{}o4(pCeJoXOe5!Kb$#?INMKxee@8G(;apY?TbGEzf2<JGio2~Rh)=t|32<3wj!RYSg%~u5x=kWI^=EVT;yR;YQ))RE&Bb?8F{YkME&Pjj`#=SIpw&W5q!V35P9p2b=X}B&p~es+Gk*0a%7IcbM5II_^GfMJo>IW;!idc_V&4ufA>oruk(v(u)p{jJc`T)|G8l|j}6vU*FdcQ=_g~pK4E?HJt(W=^=^wnezwJ8ygwvCJr@|OcIVUx#1rul&#52A!2dBkr@VKPX?tJZQD|SL1?sj@QOx6sL9j<-zhrWLLjF$-M8Chyz&dtn75LjJ3hgsB2Vds8us*!&4|~dyuxHw%@jFc)#N%6pcv^&DUh;K7em)dK9zMK5{0mzn|7%NPzD}e;`w=bCzR)cADf<pQ>I=K?A@&<4pBMYUFPo!%wwjpV3$7h%pWGDo!>Ke6p8c8eeA(Rye(D?r-@Bg0x^yfAbvR=&>TuLQsOPb;d(TC}|KY3Z-(8|A@^I-f=Do+4*hg(B4?ivTfL|MK;`tsQ1bfdfIj#ztH%DwB@(|kv{>S)ZeU1rW9<rjn=cBfF?JSJ?k6)qvI!<>#@VVUtdr(*1CSxCR<O|sEfBaqZU=E=^zb%A#E_KAb&%wIw`Z_=CN3hRv<d}|m@9IFDrNdEINtVOUwp_^1s<Nnu+_f<;26o@N?=Y_NQFwk;&x-aRiXqQ=CvVs5$ys1;KNRzFb`|pQG6Uk->Eiw&x#r&_O%J<w2J*AyZ}6yP3go9J)(yw7{@~sB$uM8<$6wQU{_saVe4hm4%7Fd9_v<s5_sMS$Yd;&8VjkxW&^mE+d8Kww_)5f+ArkwOLoZ=}b{EgDUBBph>kN4Td)tYq+kitFzi;&|wY%Iyv7V$)g8U4+sdjI&uaJj=i%~y0Zm8W+59^q#@(|>q*Y9d~_lwhUneOkAx0ILR|IIV3!xeuA-vi<?t{EYSr%nmvzvFqe`)XZ8{ON|_J#OJ|h(E-Qes}Id`^-mSPhA&zUj7{WnVN@SzqbbYj0(kb?e0Frd7t~+)yYvmQF~zT+(YB{9*so(_-}*#9N$}amfWV-hvSeR2kOwbyfD_cbel2WP`t0XH`he`k5?g{y_jFel-^jcPAylvb6-x3tL1C;?_9eW{@<dmeCy_6UCOx#`CqyMd0SFM>%^69F536x^EdePHq7fB#B*XM*4s|)u<p&74ST>;K96pKcQ<Asp872r=Q!-Q(~QTwRDXkcd=Z2E<Qsu;75E4I4gVJVgpb3}ek0al*UVR_lbE5H_frQjzx68WytqI0N52oSKXesd7pLR#_QSX;;C#T5>8j4Vr*S0gXTHJwUQUMhk^6lyUnOyF;LCIl@jvc^ylr}h_21;fyj<;pI1?|^d3XAahdpCA<Y&V?_`kmf>+{4;XrG_Fo_GLt_@*Pq6(5UrzWqYvCrwlIyQn3`yD$Rwv5nCFJ^1K4yhP{A_qsg%C&l}bdtw>QgL_{P#v8r`{a##!eN?j|$eRcIaQE(GnrCnB{K&({!SMg(8tnH@<-oX>q7KdSo#0Dh+UMYWz;V7f*4wk$;s3j8SRXo1#QN}SHjL~3FvK~`V128S74gTdN8Wb#(|Yiw$cXmyvmpO>upf4=N{u)@*HAy{;=zleN#JKa-h*7F-s3&1;k!fXXY(@j`@RbHneT3?-8pR?;ynCX=fw=argnG1$?#MEcdVZ)e}%m-=GRm69(Y$_KkQfY!@uc=edca2`b{+$aYnSq`gVDf+Fd*O9uYSOJpH&4_DZMGK54xAaa4~zg#2Lt?8<x&^H^o2+P(Q>u+9uRqx0^3vIPB(>x}l<UMo+Xxo4q$qtdYZVSnN~I0f;i!~8m%w@1I>ZuGl)HRk=sF3iiE!SJ7>BKCE8dt!Y)5~X%CX94%^Zamj6^i#X%>{!g>k+a~}n%?O5@VravKWz@Qf8QPUc6%->9~;%ee&FXW@KdTP{9pb-<9D}dgLpE&!n!)8KAt;?!ZF?hsArFHU>|;}A^d#8I`3){ruFZ7Sr_^DMj@V87d0O9wG-_Z57c-(y_Vy-d7~QY=jJUuXYWPheBexF<e}|C#95_^)|Jas2Jw7926h+rz3wR3O-?)?eO(h{KOb8h@l<QA@%UN|(l|ZKilJX8&I8>W{4tM(3ZQ)~&O^LmH^IAixzPRv_NAU;Ikavao6=!^_v5|Td%gquz5e=FjdL67%JFm`_;v54+8qJ;c`h^-``c_!)$Z<%_01QaLF?0Z=O*ld9W{POd^qZ7%yqSU!c*e;vg-l*{pT9`ZQ2QSxH25`{`U#AzxfgC%(YTje})}IJZIVOI1l!>TlT8mcdVrL>%0<<_p(Df)$aUM3iJLt3Eo3PcEC>%pM#-a>AX01twX=(Iw8)NWA=S+_s-_|#<ejzzm9#eYB!}fWB=3B5A{%a3jBA)Ie_a@w{4i;k?`Xgh<v8~fIK%Fs&-e*Agwp=uvLhsS`^~HhW(6*3C8)u${z6J`gldhTj>(^+gH1x{m3-PXYviGlOMYx&i+54--69_-Ed6p0DDE8S39Z<ME(c0hJRlG_?sN(V6M<+Xg><)B)%qp;yE(A3F5zl^Cef`d{|E|hQMCbaaH}V#eUM8q9OcT%!2yt{}lU*Yjt2>d{)Qh&et9J=}{Yg662h~)jLG<W4cvDy#<{_owVGE`uwX1<}noKV2;1fgOAw@z|Y;~>ff8>J^0lv8~Qzd3H^>wqjtxXjF`u_6Y!k6uo*l$o*w>(;XKyStpMsgC^6z0h<bLE4a2^AfFI`NZaJ(QjvA={`cDpOK5|B*-oDt3^ST2MVXuI7+jpXa=EpPluG&pMynlJB<i&g0WS`pI_us+K$kS-Q@rv3VKg>b>?3$<Z?%Q!*?XGh8-r)<Yf_j^I4((q(z`U0jjQUxA68`-kVZ9yH3iCU5AL86R4ZKJnu~pkG+i?*5#ksL>e>Ti}(KTrQwi@DmeF}UWhwnnp?BByrx)<O}?YZbTM{VT4O%dz^Z_h#=Y97YCr*q@E-!lgG51HVn@fUlM$1xc1TRdl-<<H>xIB_KW_p1Z{r&eh`-E{_{eXr5VN4H;)){lE=f5iXmJG{^Ke}egX+!NzH175f@UB+{{S~%MO_%q^sItu%r5n<?e-*x0++Ij9bnj`<E_}w9Kd#rC|Lolu$-{AT9{#WE@Ex%)&!20amj&;ntryl&I!T!(}x<=>4bD}!pJc9O~l8Lcy|5ys+eL5HUS^Wfgi!K4Xe;n4OLp`zo$zBls_NamU+-<3LZ&-GWD<#e!ymP+AzPCeW#8VjOGoFG=F|Lal87IDfxf7qn^S2}Hu0rh*PueBOTe{@v_bkqZ97|H^cwN;$;JvEn3fS*`#QHGz0nQs1w!yylbt2Ts*MH&sBNFSduWnWBtLNT<J$$H+%iLS3^XS@m6@Hdx#dGr()*18mY{K_3<o~-g*r(k&4tuXwSg+d5$MfRxVc74N!TPXiAM)V874cWkj(Uho3tsH}1>bFE;5^fOn_1)WyjzX;(KOw#-VT0`Jd|62_{R;?_#JJYZqfd}or(B|h9RDeKcartPec0wcwV^sq``SYWqg;g^?Omr8~J{NUjH%~?bjbe9#Xf(xnJx^wVR?i$9B|Bq4j1i^ZQ|=4cJFjuZ(zJMIrt-=lH&#mFJE9&_1v!<|R)Q-fOnw`;2#b4cOCs(tJACbwu7Smee>Mo|YT+`dv$WS2^rPehOv4zAJHa`2Rg0=4*c_`2M~L;x8PEd0&@B<1}xA(f;;HwY%Eg{6*V;{2KX*cz}LOo<zSZsvtkbN+3T6Q)2)5cO}H1w3fE_RnM*Y^dv5i_Fvz@zWTr@)K7sRwC|Hh+q+M0Q2!qP0L<fJ<iUg{!*lIjUc}!W&kOU*BRt>NW<i|KKjD3I$U;14qcbI(6NA66tLwNt7c(Gl4@1ev8JNd5_`d4%D~|eUu@ZH=IVt=U_(S7#HHz19`Oe_H)|nFfOn1g0jBEI7yf<vazRu;GsP*Rk_CDUHt9*#pyk*{qdi&xo&LOzIx#Fkey*?4_&J0cQJdG=g`OSX|@1ukKbsy->eMa-<J%aD6&QyG#-H!dCDRUI>4RM>myI<SmoTU0ev`>cfOxNHEI43#29p7hu#`j_qn;Z3cdo%2l@b?^?t#jjfH){>v{~q50kG3>pesEss=;g({_Zf!g_|>Io|1=)wmQOxmKbCJ1;@r?1>tWkMcn;PY4g2)$*l*{)pyT!B9R)v)r(-|ddCF$>6Eqlc=1z?K*9b&C9305=j91#;l_EEu3%Bt17aWt0;r*!I?M-SA3P+yDUEtpnn1lBzZ)@ajV`<F$ChXHZyIR6e#Af)3I;wg0G=|-r$NPf&=f&#Z`8X8*%i{gfJN5>6y1g;l|F|FDr?U3My0<$B{#UNVd((iah;u_Zw9h>l_0T2)^>(iq{GVxs{3mISeOk|4%uhAsbJB0vS8vaTI;@ZVkNe1Qv|pGU{`ZVQ`{`A+U&jEPi+gjW!gyN^*Ln8_f5iJikD7=lsyEh+Q*ZE|QK~f7pY364H@9BleQr$|%vaEJjo;yTi1w9!!Fbb@*LaNY68zWehIqDq2i{fU`}Ze*_3wPv5%$Rk(SH9+v`-A)`POa5c}CzPtZ%1RuTpy)zlYZi#e9v-hjnQ{EY8)&y}&xKq~jX(Uv?Sd%vBfb%)4aT-m%Ps{bNK8)X9|-h`-z-#QEo2^xHDWI_-B1zUO=Q*T;A}qaK`t`Tm`43*y<j7=BI+f&XWPkpH_59hdof5bQPhe%fIQ>M+?r*e@4UyJz)g?Eh!?h5w~I&z$fGyqMe#aTZUFcv@sZ{TIjkv@>64@MzL$<nwkL%wr_}o{aa%Iqdg5P0&7BJIs5vIMhi<9gMeD2FzDkqjvYTqG*493-+HIZ)3c_e}Vj$IDHZPT8sVaC%lJwnm&hpan{vpPn`#T#^RjK)$SJdOYXGr(--Tf+qZJ9#_jhU`;ollb-p*)KR3UJ{Z!VgShwS=X?ySGJ7{01J>IjLe8PH_{}%Ske|*q*oaNr&`@%=O2RPd`R=ejw7LVqq#a@1wF0b#8o}=Nqj(M)`#(PPvk;qTV#+n~j3)nps8ezZDV)c6M_u?-2DV!6}@on3*uH0#Np#2Iz%;S|Kc%B}JL!7ZA5Kq-WjmI+%c6ZTZI$lTdAkC*E-B#=e&-1%^*fHdD<ZAdYu@>_iSsA=*xE%5O#bci~;)&W_S$~H8%typIoaatsJ@Ef*Gk7tpfyUzso=p1#&9kr0LtTH|Wn$28s-&2&8{08oTgG8r>HDI6^XjlKAA<QRe;e}{HdE)(*#PHlu9400{Azl7p8mdWZ}{;9V}5-&mvCO~j`opDFu#@V&BJ^JBc3K@(0+S!yl>{J3;Uk*$g_Xd1$te#0>(AEJ?7o94eRQ~(#TIp5ybyjM|}VFl|VdO8e)HSYsMV)Q#lXj>pAl29tOU6)5Go?eH3*P=8ydUksE&AoJSsVFVOk*=Ff%t+*3;9@je@Z=hU0@us3^*dU$^ye0lu=@89o?w)Y*Zf#=bc{mA#j+K97U_-ys>n~Qzo`^7pgNAp!<G@k2YVUN#>c@K?JKduL(;OF}k$lF&Bb-eBiU#Z<4m>PWVP+8YoXK-HZBc_F`f7kPCqtu=!5ArvEncB_Ev{Ur=*;2v23+){r9#7CX{(OzPz5~1G&<JhsnKc#ruZtP6{x5c8AMzp^^*bN?bMLwxsL!8X;XB*<#Ngecz^U4<)g8>kupDTA_7L`Ob&g}5+l}Xrr*XDvdR=Q7=5xYF<n#9U@%sC`W3f(eEP?iM@73=6rz`k(xh?iZ<9qA4Jmt>gdsN>k7;lv=SSMRV<L^xrsfD`j|5EL)7G1GV%#$1EMRRgQ>bPs>!t<or1FTEYCkLp#^eOB&C+<SMx!i;Fez_eu|L)fT`OGi~{RYOtzJDj`e90Dl{+f}Iuz#wIev7_{QvbEO!T+W0`hCiAZ%2Ri)5#CtJ#O~JcjTZPJ=K2FU_bTG8>~w|rW&I0_&>#SZ|^YF$-4L2uQ%HntkcUk!vBLEgVp}7BHjb~#^Sr!_w7dL?@J`(cjG*$|6AkwYX9l|u`f<LU%&6WA~S2<x-vb&cbEdb;lIPHDE<B3Q&^7!&m%v91AFQ3jxRv_@&nY5Bev^I9p}bTc+Vbl1oL&+gZJfU;dmZ)oeDpbPU?G&<9;aKCzj;K`DD9d9W@{2@9KWvbe^dGeM4r<)i|!;+{GJL4gHSW@ss|(;C9%fUm$Ol>f`;(y8(WZuSLIA7iz!G7fW%DnDGjD_vl?~#n{Do&zP4><1xt^7t;P;c;M$<IO6Hy)OFGulN9gqD==Q?hh8{;JGmO;%e4dF**E^6&kOU@QnkB!%*A|F`fa|(^Vb~2)n<^|J%3Nuc`;o^qkYBtYWHQ%t?QNRV@;eV`9;IeyAq3azDkuqza`+udn558^|SSozE68X%fbHm56!2E+k*G(=dIB1o%tH4``7Ylzo-J%?K2;Aex29S;{2fYL+r2a4bymhd%nSYd8?}6U6(X!cTVz$-S0Bmhpbu-K0nrdgxR<Z`|!|{OSQiuzp33d_yyL7MZGi+&TV*qa;B>ZzP!t=^X_Oc80|+r!G3aZt7YmZ*+BUJ@c{hqORE0eql&2A_sQTqZT<Eodz<{nzZTeD>-<;S@);wN!elmGI(+s|1;i+S67YZjrvlx|{a^i4f%4`5zyGN~cN;^f<i$#NVhdtvD_>9-EMp~;l^ndzM9gL-T5@J(33b77R_0n+Yh^q2?QA#N$`4k0Q}508JFJ|v5>H+5S1XUKT;ug4;$16&ewON1^7}y-%t6d*B`x)|v<n(5FAa1-f1>!iWS|TFCDU*3&9JiA54zw~D}AkWv(l5gV3d{SRzi5MIkB^qT2?CaUM*sC#$1;70*U3>*C;EKs83=Xv#hLS9J7dGkFe6mN*C&aVOH8(>1gFU>Vlp8<U6u4ZLBn<F4)XU2V!mNf-Ts#BYm_XwzRUz=4iR($v_wUiMGX7=24%=dpoVf3T>$i?&5v1FQ6_MW6-z6P=#>_er=_Il_I<@KrCk^8|?+C3udzN(Ew9X7yQTKD=Rmx+@mh|4{d)~IZ9pdIAfN0&rm-@dtWQxSc#%8IEFcqd@Q3bxQDpT$|359XrF3jhLsJ}H?Un4{fAN)6uwrmQpZYh>Vk!=bR(ylQE$d}!r9zxlZlvv{;C;pK9uMr7BJv=X`*mGwd9aKQWF!_fnf$*k0yGkk7G>HM2Sl{zRJoz>Vm?5;bQz}y5J?Yk@a9Lb-~#N+!21KBaZ|Ne#Uu!>i)bZ92b7SHqZs--e2tJH17-Eu+o+s7e2Qo3Wo=i_dTf#_P6pC?^mW?nLPiJ7)U*kadx5KderNYzY)a7)CF5pZ%rOX5Id2_ZOF~0#5&ZgkxNa9!gDw4Q@H6S4k8K<W2nc_zRiG}vD5{3(l*n|Q0hbZn=0(98aY~xJS|}*C;3@|SdO+-<ZMo&+!JmJFH=z$Oiul&0asrU6Zk6nMe2e_7_-ECoceLz7tXe^QjfZz@NJrv!L&^yj$y7w8gSQ5OyIfLr&1SON9<~)7j?lI>_hshMqMzJ+z`H2p)MF<z}<4Z&P`0<vhXn{^_;vf{z@2dxEfJ-oYjE0*{EmZJ+Y;*lAL;S`i*8B5!3|}crG}Ax}flJ2XP{G!33TQ&ZjQ8#ej1sX}d%e?j<8%g`3HU!c`IB=MCzDPYk%zpFHeBY)c6t7uynrV`Zq9rJlgiyu^ak1#?@eK@Nsd52K&fv{#@mSe?3Hed_he)jH&6ed>ah$W6JfNWCICBQ+-c>%n>x>_8NI40XYwtnKv%oZLnfUiRbtnbZX*8E~*1`zk@KNc{^d*{NqIFLP2)PCdEbzuXkvkGi1nQ{-<09zG=sKQCB0Xu!=2#EXpisQH((M>rngVkZNx4kijGYg(yjz@?hRHq4desVj9s;b*v&Mg}|#C(6AU)H_k{#D2uL@TeN~YV4yaxlo0=pzu?;CmbwGy)5m*r!2geoGAPf4i;b^S&4b5CpF+?R-*7SF@K+ex}aeU!ogwGhcUj{wD+VgIFT~kfQJ)_!p|+#$5IzuYQ<~7%YD@M@%{$`e!iwID15v{yg^;?yaCs0e8$0g<YAf5_*aHlh$#HaLR~N;eUv8OY7i56Sky`>>ZQoT>eMSyuSD)uB=0Iw7cA)qPPMku%0O>r{^gzUs2}xyY$r9k(tuOziNdiVR@$@O5Ml!FDzdK<#00(x=A$l{fxJpin;$X3{>Fe~q6-Sogi{x3zd(FoWw!zEE>IWz&46bIIff%d8HaF6_|%EIV0|lJS_v@V#FxaH%#q|OoVuX!E7(d61MUSA!|6+W_M+a4_r$mGpak_2?4u#;yBu{v;h1o%{AaqLa7;LombS!1;ZH^ber2VemHmk=nZci=#00L%pOn-E{jGd!z@v%O1%+e6oB6yqme|LDOLF}^b;0pgelg(H7V2Ag|GojQo={KV);Z#N>VhW>xKoJSC_}74?g(%4P|w45iD}P5T~PXy-vy9MrHKjL%Eh`YN=)EYDPC71N=*wlr2d;5=*?Ll!Uf^MO6r1(sDEdrCH0p4y&vm6HETXK>t1SFYCAy}d}mPCa{VWDL8<fI>}Mr)!GqN0{xRx;aR#+5b)8W2f|aSuQBFGQf&m<xj4_zHpwxK{{;ocC!Gt=O-)5vPD0SG7_0*HPU{mT++vTYX)-tH^g1k;kOsILOQ$Ol{yr0CN&XZD4%DxTlX{ZZIt>?0moxXArQ!>W32DSYyF`?!~?@V1Vq1FXm)CD6AYJREtmkWXmsqZ(a?O%vq11>x_sM-6(540!n<38~!@dSOHBOW&3K>%w!4^eoLp4S<vXCyzQZDw*HfSACEG_1>9MB#wcu+-ah16?qoz6Co{7i?hgJMr_5x?n<Wi~fST;GdM=4eIqzVnUtAvA^9!iDNbG$EXV)FsNav&!W@?6Y5*gL0vFCW0rV>sS8ToSKx0eQx}wamm14RA4!PfM{2khYp5Yn>Zl3zTGR#0^S5&3nufZd)T`8FN?zw87Pj)075TrjWT&2;_xsR)6Y7EqH7Zz_x}eKSV}m+P&;@H7)aZELTSy#XP^)sihPt5CoYbV$;~naPQpf38UkSS4Co8ASzx8{HD0RD;xS#rd_K}|T8Nj*?U>zrAUFD*li|xK+ZHzL|1*I0NbAA(a!4QMGlR6Y%FNjI0KQ^ev7sQ0xJZn&6zY`N`Zxs7pO^l;1ZT3<ZTw$f8LG9(EE+}=D-=K~h)CB_>v(#TO^<a*tB!5?ddIjE3LO=Pb3ub0rNZl2oE?9~8iW$^cW}?)b)L1U_Z|xOkoz&&;N>MMx`<>~x67@>v-<qq-HZG$0X=hMhk<<knQ);un#>8T*iG}>l8sY?lT9SFWLtRkn>^b$v)CHvurIrMfvaXV{e&n|a^>~W7m$-&~Z6?k#s3V#8{?r9SI2YAF(*>&<)KXIR{erPPrrhBe9ut3O4ATDr>IZmlGy7jbeFfW<WIut_1szs`SObC71;3_VjB_4D%+Gm~+Q>^iFXvcn@?6e9Jp=Fg5i?L1OvE|u!hE$Oj$mKyIJZH>VjR;1{$>_&pp`I=D};Iob3KdqCsUuyT!e9afz$)}`ykr8Q18Mx!sw?9^)74|#(pMKpUie!t^90d3U$FbRyNte@3OL;DA%j03$C}a*2-L7&*k-U>Vh6CN30yQa+oOBN2v=Qva-s`&sJs=<$4Q6^f)UAtn9Y3lPK5wDWd=CC;x`j?&+*FBFc4L>Vi$IoVRjP_(7EG6BN<USeb5Rq@R4_1j_Yjis&<~?6BgsvWF<wd#MZVvvSMIB`a5na($g5`fV$%thBSzkSN#RP#65x$~Y^7tb9+D>k$;uW2{74>1|~oQLcMX7wl@~iItaDo)YEy6-D%CRu)>BY-I{jt`|@joNr~Kl{r?X5#@S<l|`S~<o7>V8BUbzXi9?bM^^r}a-S&Ie^Eq#Xl1CC0ap4E<$4T7^zm$WkH5Re>&MguA6PkOCEm(eqFi60E_l((Yb*a)c|(-z7ZlN-TM4$(z)C1lu4_^ktZJpZl_6Go5#@R;Mf71-uKCH|RWs%?QLb-L7rbNTw3TC4juYkj0(HUPtQ50S+)5Bpt_xE{cUakGWuBE4M7iEdU2ucMVLAWI%59=tU#BkkP}XtV?oTU!5as$VMf96imRkA6$`YbnFQYEF*~(8=)>&CYl<QdPf*Y+QvXa6|N}^o9H_!!>$h=v6YsF`!NwA-P=0yLe|3%=xe}vQKKmLb-|MQps`PT(L|7A(L`2P1_9%vGrM9(4o?SFFMnO}Ab=Dz@*!ejI'

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
