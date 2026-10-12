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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_010.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_010.stl', 'source_sha256': 'fcd8e4d3197b4730d970f019856cfb6cd2b961b855264bbf5b2a982208d51f29', 'input_faces': 620, 'input_vertices': 389, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05683531612157822, -0.12630560994148254, -0.17536123096942902], [0.10461659729480743, 0.07444623112678528, 0.15871253609657288]]}
GEOMETRY_BASE85 = 'c$}qN2Y65S*T1n!YL8k8H%5aZRuGh1n~269F>VNn9f>_}DrSukwZ~6M5j#{Q)<q~vOO2X!Teauks8QATo^w98@6G@Dzt8hN@0;g2&-t9s_uO;8_q)fB(BQ1u3M=yGr@T$c9{jqTqLAcP3M-@f#f%uxw_j}4q0wW#l>E%opQ97ob_xmY=B12M#`{O~i|rfZUr+UK(7&#KW!1m`u$U1s;X`{5i;3t*eDm<ZvHfg5HYz;2pKVvDSvRP%TC-whb)x!z{PVW6V8$2Ua?sY=y+%7oD+jl&Yh)|q(ece>8$b5lMB3bI2%mqe@V;|*vH$lzYu&uLaMpI_|7f&^cx%;g@n7)sMt;x9(;oJ(63D!kcyA|Zee}`Q#Cs~`5dU8auH|?O9&;S!+E&hok}+rvY0rZN%h`WU7v}ZtdH3*h_or}tEB<6M`w#1z%G$dG`)l303P0hqg&cqFapv_7Z#jR;yORl=ufWL*_`NHhGp{FJOlSS7?F#k}{hoR2{Bw@4<qyhWy);9<v;S@8^`kS6aDGEp2*2-3=GB%r*k8FZmw6*v@@d_@by(~;dGF1^``CYe=rVe*daXC}>c=^m_oO8<ukQ|K-kh~}H>a;1c$D?!YVuuu#xSqcES2$}c*_&P@3s6Y3IF*}<~;{eIREOqB9i~0K<3Sr@f^pPlT+TC>dU;g?Q`}wBVTOb=K`8@xfypBE#i9l%wpbryXRZh4X;R?b3ZX}^j|FehT})wys|BUdF7ZQ`DwI6{42F)-jl1a<Uf27^V&CAnKwEXk~q(22*36`w_82(2liLKXe0Sq)`EGn`4jf{oNOlX&(xN7ez6ks*1GDFpO|dSTdz%y<9Sp`{MSF{_N>l$cZlCp^W}Q>U)`U1Po%HJ&+{wu+KM{N8>cRE9KG`u=FPwEaQ?0R^)lSNGVcoW>Vp+h4r33Bf6;%XNPGKP>V3sJ=8eQ;=9OFzGTgj!Z7uWK7(Z!mRThi?+NsQYe#^)4^-&3u&qWoaJm2l+IOYda#J{Jvlz)MW>~H-#RPr;+SMpPOh2%drT=*?nn767$9&z)^8M80Hr{`hrcScBv#D9K@$0fZ_9f`B3x$xFu8Lw8HKH}!h_=DnaOyzPg{evX`gMZq~-`}~@LXIC@L;O=Gv%fZJvXnz&QQ_17;(9R?F7bP<a^CV@Pm?r`f29@ko*`M8*Duy!-l#YDh?_T0Ug9{`gTl;fyWf4o`Tn@1wDV)vwsU?G?h60Y&pdvrb+bu(^SjEtHf<a8)+KL=Kkz*Bo@7(TJ+v!h=V^&^=1E72Yu@h_$NjFU$-Mq_7W;c5R!e^YZ)E$K%fS;Gw}bq(izyQ4TF33uzxvAf2HqUff_W3;gHn1k^Xide5`WIXZT#NIB+382N7Al(B}jkYzDnZX_(|HsFHzEdB1Vb-<q_iF=DpPKA5r3eFg;cBdy2nT>C-~;?>{ir-S0ffntbo=<vdPmt(PWpIY0Fl|NTp3{?U8z_v*DTB(dGQm5h5qO^&f&{zJ?g<xa>r_I&wfDc8-yqo1n2i}=0jgw;t>@1wXJlmuPs@%OgO>(=Z8tT%N?ra0=sdP!3688ZIoIV<%TT1EWNW#x8dm3*1u=9Ok&^Z4Uw5X1SjvSpX|eo~KlZNXU1j}d)y9s74F#`)Iow%JEo$#Ri--E(%Iv<qL(k9K(h^Pcl(_OrefzR}GqO@3o-EE~w}R^K^^Z8P?T)MM6;oF6l?v+xBHWgPfw1LsF;@Vm_G>qc^Wvz9!Pe!BiJ^ID$r%o{$X4of+%XI}BS`z7c5Onf}+q{Ow-&!%wsc;ZIN_|R<-^M=t*+U>s9Ql2%tNc>|Zw@ZJK@!!g5C48$Gey=+1rubK@Any(Au#Nq0Pn7s${e)jroq45&NBU#vFJH6W_WgV=uSxSiV>|n9=FQf9GUdm!GeG=TWh~+NyLxTmb~WoEuWyvUgQR~|{ae-vN8ftnyXNrsDwBSY@h5hK@Oyhozy15}25#pUepoGWM#{K^@j+`iiFspU85w6Pu91En-%|WLF5&f%k-gdw?!T2IRx#h8P8@%K?j&vxo_XJ{WIlB|uiLDBCnj^e$Qb6W$nuiUhJEC{@o!e}d%Y@1K4)A_XPxb*<?Oeus;sXtu9{zEFmGsn((f>?DnsIyyW6w%rs!TSw|V`U*U~m+`d&{;u=o$j!S7Z6b(!10+O(m>?><)A55_~|brI(Ek5<dLig8Arl~dx(KE-j2ES=N%{hJ>xV}5?66z&gUS9kMwt)Iudc{(Xm9EVp5Hr?)SS4Q10n73ZMmU27WG!t(ey(0Z>Y4P>^9VbUHum1SEeDCTJGJZbnCVcHq{9b1~R5CtdUf(@I=C3E-oF9G6<E5O>F0Ccbtew*DViK4){?$h6YwDj;ZvIiipQyv*l`~FStwNaBgW_fUAG__Sn>SMj%Xs*4jMVSo8q90Rr>AgNnIGSmV_wO9PS&x`xa#LE@&BqVaS9ce{yQ^``;XFO2+ucWdXB@~KI_(8BK2EI*5R*8b3Pqjd*~zMZEQO!hp=K2C#)XtXRNTtuMd#@$eVd{oF)0WIbGI`;5DpEopIRA_jED8x8o`H*L$bQI&jTz%qy>tMN5Bq{|)E2Q@Ze2U;Q&~@A;5<EjCH^Q#tlYf4};45%Y(avA^CXgx{<A?PcD){+p~@oN+j1i}>q7vVQwwm6T`XRPk@ENSs@9WImlWQ26n297n^rZEpTt;v7qpb?>u2vhJ<>`&azj9p5DWu5%GH*l*HS;jvCO4po!<)R@M+wo{k+0^`4Wrzi8qcN=9rT=C=~H?Iw-AnP<weQ8&@nlNvc%+GP0`NH9qS#!9*c+#qW%{t~8@AtIL1tmV(zr!o}hi>I|z9Te)>*cGTWq+9M4#zk1zLk0(vQYfzHIVg^Grzo_CVcsovfj=s^SJIen0cd`x6Espcgzb-BtQ2)m-%shy-d7Px{<7ZcI1$Gr(|B?voFasZdjWY$!ERk(oQfRIlOT<?@sz2eS@qwwDn&nvj54MGXE~BE#-f5I`i7#F7jQ~Z^(F<QBnL~J&^eb^Q_s)hk2vQRp#~3BpILY<Yiu2-jv5FYv!{+ey^YJ0_HvW=CJ*2tF)Jr2j_E~ERj5Znm&HqFO2Y+%qy+ma=-Q*P?mD~Lto+NzDkzwYP^TEQe_tJ+m-t>xE`%W4-=UG>+C${C*@{;V_5G9)}>R0kGjL-o3%Wd+lev!@f_y=c**mN)-ErvpOq#d!Y|#qiEMTG^Wp5@uZHk3p*%0@Q+}Dw<@5B|Z06ULS<L*jGyJ{km9}5<_vZSR-)ridR`L61jOBi#gf(MZStjGWzNwe+Gg|Y!t|g7+`t&TkJ&ogRw`BcV<QA8YReC)0N)~_q9<4&<jhXnNYh~OyyoLLRx+$OV*^~Hu$66Q5-)+peI)&r!pDpvIPiI~~Tf_T)A>XCR{9At%`{}nQ8|=SgvGhCtK9f1!zted3_dmw#8>7bUiR|BH{aEJXb8`JEo!bp&KIrry>0e`b-gnMb^!9%YWUUTj-ZNmT><jW<k7B=3`DLB(_bu_?u`H6~IP>ET>#&>uXB~z4NUt9t{#Y+L^O5n@Io_9Aai`?H#T#b0c{6pd<TGWG_?L@f-ZLkN<ES}fWt?f39?pK|8=k+cIo)OayxLay&fPhVv(EQS%B{1#73(658(P4iUYyTwKb1Jn{5A4+7^gS!l6fEVl>TUE7xquV`PhK-;_r36GyCCt^*Xa<9Ba|FBkK|eWPWU!Q^tX?xDKqx1xUH=Xe9CPd{dwEi+NcMeR0&yD*=0W9yGeW5q@4;dA7Z8%KBl~?L(RPLVhxDVm{J(XDh{V8bk>H-Ba=ZyZ$|%pK%`I%t!h>pBCKi-yD~7s^vb%+`RdsyUeqfewFyE<34A9oMY&zMWkN#E)He?wsH=pPCYI2a=@BS%#Wxk=Sa>v>aVt4xP71gK=x&rFZ8K#VeFq=M$VBE=gE5;<><x!n6H)Mqosa7xi0*t9c8{AoK@B>6PoE9=T2`qN5Z_|xja3b{V|W5lU_+a%dF|kyjCmId}rhu!{eXw@<ZW&%r5=t$h-c`KiMMlPHKeoi=e1T_jhU0$wxEshKK#t0y`wm#JB+*Cn-bX-|H#gWt1N3ey?*5rd<yo#{9EuG7n~dDdivhoYzT4!g!f~hYrec^V+e2!hf(?){RGA%Xs;`3-4PE^i#8X4jwnn_}0v;=%@O`s<KZidyn_OCi<QFus-v;nl9%C&N<<!smyz#y@W@9Q8#*oZ*hRnm#pp5FAU$@GVY!{n(pow=8h_|fBJcNy1V^*uCJE)<5-t8ce}NQA7Wnd`D>569cmSi%f1}rq0>+Gl{I;uGts}C_G4A=B<Bsc^Q5`^k;5BB=cT&akMbl<;w)RV+g<PKsq^ChQRwbW^*iON@E`0-b@wA>b19xLopW7hUuK=H!Mt*Ckn~5?yWtxq{?54~>fJgYE_~t}>0hXK^T0KkNAKL{a~121?3?rwGA|mwSLD0}`y)+zA^Vw)Lz&mmFO&}NnODDQB>vb38Rv`ex<sqp_#pdZf2vk1&b&IfI`caAr`p?!;$L}`v_tHJJUgnTNPj#i@tyrCcr8aC_P5GoKFU)o#ocZV%ty+AI?O9=DvN(X*$3$v^&~&jW^#N3`&n~Pf7zG5`Ih~4XFpqZ2=ks0A8F6n9~oC-CC-h!(l0Q-Sb?J@KjHm2j)Hxq)iO@<bK(NGe+Bc7!)t2~F|T1CWCd?$-g?o3;~UsN>goH1-!)t2JM3%B;TaMq@wUWw_Jh`0;X8aH^FH=9TJmr5U7tRacJAzJia!<q=oC3m!+fDF`+(O|<`s|hN9^OYEd`i2Fkd_S7ki)(|3h_U-p77TA6-WL)0c}s_AlnG0Or*m1BCC=Sn9o0+ntjCYcdaFzA&qImH00<N<Rv`Ank2Vn5^S-J?A*i{?6e|^k3)v(E2k<_&UwxehT{wD`lAEbNzgd<LvJoUc<iL!2I%$Klah;>%~|n%ol$Dc$sIhkI=d=XI{ZMs)2okHY7>%<J=SNKP=~3CpL)xjc6Hvob$k|DUzS&zsfk^>^mHO!WkJiu<uY4(<DDFR4F%SKbUkx-rMEROyihd@0R#G;~4gFYRD6b-=l=AH=K2s{zmw24<tXA&&quCLylb>r`iUYf3YvqDtQZ!anEXweOc5r=C$2bq+TwhNV%zVn0M~oocx%<e@h&+6LZrmDgWVxzGeQTzvOfJIcX<DUNCR2D<t(2JWcXbCp(`@d8}<*@6LIMTK2<Kj+3>y+z*b4mN-`m2%jTE{1+6J@u7Y!^V;!BCdb8is4X7FyxO;nDdj8Up;>G$^PXit$vBB|&-`Qw^GX8`^Uipso;xD(x1Ex4(m6L<d0z5UbOQ6v_+wQ6L*lewDdn(utF+s@@5H}su;l;K`!Wvf%)|RdGr5<Hs~CUGOMc87kKXXO<cu>`Qn>6d19$QGV>stL-;WgDr;Utn7zeBk347fAMZXas`Omgc_|Pp<@3@~bUhH9BJ(w%q-LLf$r<u3BlG5D$RH>Fj&K(y{-{bBt>f4W)ch1M0_V0-*C;k|>P249syt7_XaG$8pt(zw8Fq!K`#r{jZUtj#K6*3RvUfWpHn0e>^+G)2|*H+@+d86Df;NH;K)rNUzK2>lJ?(pWJ=`t_iKGETog4I(q^~dkz{MEQ$oa30dH#Y+#B>wFKyWRa!pC2i4e75d(_eUdajN}vR0R{Kw+R3Tnf2}I>Cho@_UN=6G^+pZ3Pj`6jL^+v%aWD2yoYLdDojCW2dfaT`13JsP5%+^;-9(AA^MTyI;GSJyxJdkKoR@Vh?%B2UWbrRPSp0FHuAJVLCjC7`c-*Huym7jTtRIfbeYzgMSH27DNdxzEigiHVySjt4Pu$a)^$$z@b&B*O+`p^IKT3S8pLOT{J^Z5NbLmUjkK<lX+kaX7eZS1K-Zo#pl6G78J(rIM_wq)&KjpoxA4$1gkb8L}B0JwFC=b)6oN+I29n8tR>6a|)2aFr)%CgL>#eJn;V_Z_VSCM;(j~>f91o!gVxQ61tV7<)yxMx@9v}E4M6E5rUoN~`@-VGLi?CVwBv#Xx=k{_%e4BWF@NBc8xWjinZ9rxzS#3ADEpC<bP+?y*2qnUT^zck#B|HI>6!&)x)<K}~Lk{|5%o$*KQK11SHuPx^lxCb{MZxsJFbLG4p_t9q3cJW`=N5&uLKKlENbm{LO$~wonFZMq!{&)V8bq@85&`iIY8Xb4@Rf4abb6avLg_Zu{uAfX1$)5%NpMNqnpw|EDCsVa+RQvz_Wa@7_4{vSx%a(V*#3^24XY~?!2mUVAfi2gd$-V_l`noHP@I~0?fUm$N{VVXVh;t2c9sWP!8N%PgCVT?;d*Gj8{|HRaoCS8$uYms!X~drfChin$!pC3}J_AhL53rBhasl`U*k@cmWd8(B+)0;x5^@arziP{Qq@Tz0gnzN+61dB-9em#P+$B7733(!X1OAtRFT?+L*uMckgiZQ3@NGQn_}##>4{W&y?hfqV!2J&V2t1|VgiZK9@J-;Sut`4yegymg`d`2gfbT&+0lo+PJM=@~$B0YsxeNOi<T3bL(3GF+uy3MHzC*o`J^}1wxBoJ>_<9K@UEG$Uun8B0E(Tl_Hc4sl#qliJ1>i^ghrq<;f=xI-Y{I#1$pbqlYzOCZ`R2j%qzeIm2wV`lD6lu4&kvj%c41rcfy)cq!QSxC2Y<4Qz=zU5g3b@#;Z$2nfGY{x!K6zey|BwJf@dq(;s>rA>{8%L0uxsa9BF@Gf4s{NqT-oa@T2DfVONIK0$&Abm4Pec{gshUH~?v%00+8k(jP;rz`r{DD7^-3!sTHTt_oZpI0$wPV0xxDu#;XFe0AUe=sLi4kT=3L@jN|S7IsBjDgl>;UDM@5c4_FU$eUvmE`#UE*B81pa2eQbZRu*u=MciJpxXnJ4h3!n{23$^_1OrvKkBd%us?iM=r+JAa0y6jFKK6OfE}(m_`<;Xpqm2c1I`WI7?^Yu;M~A@AcPA+Hv=vNTok$mFzI06qQE|oV3Z^25a2Svl^}%Mq29>u0I3AN2kN~8bWPwO*pyxuwgw^G8xjPcmPjM67wq1s$ClvQ0u$E|ap{>)y`(KRgsux52%FOD!zN69u>tD20qUA?J=nG2Uk}d&0u#T<9=liCl4Q#|V24`{p70{rq!V0eq!&Xkbm0Wpq^AKd1fB~#7yfg>PX{JF+m$vOLi|+7L|fu*F@UEc-EiTNunl1Hn*{8n4+lRHcsz78@I>f%=*hs89t&<f@MH+#DexnE7W5QgN*@cGWG472;AcXA0Ze)h@J!$Z5W-8L6M;!D16~Te7D6}~`fK21;LXtMfj0whf!+YT1$YzmI^fMn`v#i0H7=WQ66$pg(vyH!<N0rppUvRb!Y2F`?A7@8rQl}4{tDb$;F;hleH!YX>Rq>`yDbsWy?{xF14jV&hY%hJAv_LcG7e=h|KGT9@O^CQ4IB=81Ee>~ZXNJS=rG`wz>A=}0WShhfDrD0Z%hCVflat2Fma7g4lSXl0gr@D>2+Zf9u7=gG;G4Lum?a0M?whqgb=O+iN>>^B8|9ETiSwa0sB*M?SR|CpYTw;o8CDJn7FaP#H~PmP+fctn{cc>-u1I(lr7P~4mS=w;lZ%OV3Y4a=y2dL*wKhF!j>VhN5C%{TsSn%T|HqFjzp|*@R7iMfr;w^+rgxpKnOR3^hC_Y@T2t3z{E9$O}INSam`^9)`5v@4V&<ATLyq@1G_ai9XJ#`rH=+Cu03qRlYxor3cEe@NTiJcCN2)TEASZDgKUX_Js!4$$GChW5NjlG421Ad=x)G6fuo>10!IP&hY;=q-3ho4a9>C#)L$g<K<F^wKJe>|n0<hwVC#_nsE_WzosrKdq{qM>02vB?B+{IEh(Y>jVB#jCyyAcd!5#)o+$7izCLM3f6yP}66Ty7}zj$EMJzUT9a@o#$DIR<;#On&*IB*>hi=H!piE9U&@K|8tLSPdf0UQEMn%0IxU=wZuoA4<3JI{?mT+-u!4d5@JCjd{tw>$h`a1&65lfVrFM|DYUfcj@F-a+pTvd5`1wv>k^yEHKAvaYnU5MPY*W#L11CD<L{Ulv>?aL%0Ji+LdoX~YKthhaVn1a1IKTp!rIp#zZC7`Op&1Nc_Ar3SdqU^fOA;NnS#LmK1RUPvRZJ}`0JVH2)kOHFWHVRr{tAGkeuN-t@P3N9FSdvFziTYwM7+*1f#A@GDt*is5yKG=mIrQnwjHpM6kAL8;r*8wgJyD<Emw0wA$_>YlBx-xK4;1ZC^cy}paKj_-Pe!%4*geyWf1+EBO719)SM!Gq0b>JG%&46nF2S5ma0v!Y#038Tj-i3o;SH(L%Lp@eST~-8k>b5F;$|0>LzOfwYQw6R7DF>fY@S}8plqr>Q71+ffgg=7#!>1VRywHVFhmK7+Km76nldcP$2e=W^>O%6M&Rc?~^di8-g}`nJ?Sr(^z{L4NhX9v$`Bp)mN(1{qiXl!AcuFscGEz}DR3|hp&{^?oMb3*!zXc}!4)_Z2uMom?UVaxg;ViHTXZMn`$1Koyf$5x*Y)bzCHeovdBupHgc|HTq0h=(Lc@id$&OXV`<|Xn3ycg1ld#?y4?oUO|c;7?c2EGj+!k3Unz87G>fm{Or3Tec>ROAf&74!w*Q?M!hIc&nGfr&c{`ws}=7m(BNc@4imP)BFM6||+5Ew!M@E}+mqR~JltaoDxM5$+5j+{u=lz>aTD@J?DAsvF>3RDZzPVduoNIg!=|Lb!=7S%Jx40d_bAK23n@QJn#kj~B4RdBLY1ux85#z~qwy*x_=(M+0tc%ZI?^;|=U^-tcJ++{KoLz~oa6*x{<drwedDTlxZ%PY+;+>j9sBz=NR&0S|&b1kwY~E<qY`Ujh@i2ey+=cpilCHt4OuTVd~U*=f+bfOo+@4A~0*45Sg43QXK?*o2S5CcG1vxFfKgbixNAg!e)30Nw%n2=FRfQe0_-_X8h7`VMf1fRDhB(qf<|08fCO4q1g~zeO5x+ii&g7X_YhM_}SMLT`7)rF0YDN#Az><zqtc2HuM@JOG^v?9>6JJ8gpM^K(V|F!kL6z{Jh4WrQsrXtIX^lOF9#i-U{+KN>z`YzYna%2GJ%|MXvA{P&;1oznduV*LA)nXiG}Pu8|4n}05aLxZzZpR)&oEPMdr#iPJ~0jlEHt^'

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
