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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_012.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_012.stl', 'source_sha256': '219c7cdbb4fe0718ef35d1e883153db6c40457bc35f9fc9a2bfc080c2e70cf8f', 'input_faces': 1680, 'input_vertices': 878, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07784871011972427, 0.3206292688846588, 0.24062040448188782], [0.10270021855831146, 0.3592959940433502, 0.2571251392364502]]}
GEOMETRY_BASE85 = 'c$}r2ca&5`w@15YNRmWyX2>~78u9>=(*Ob@Sr{Y@StN-AB7zbmC&7^{aY!NxG6V^d6&giF1QaoXV8DQ{t9#e!?sM-SZ@uSQXYD<|ujr|+KDVlReM)@m=rlP!!GDT+=9X*K>U>9!$5dudPS4ncQDX-6OBh{g*og67PqsjA{;^!pu5;V?ZeGt=&&1OG6GrzNRk}`0>3RcVOIL^~Jz)5#F{Anp>pgr_{{)ja>pOIGf<GTUu<wWj|IcM&YsFTGsaCc^%nLF9$A2>Vr;vQ}r(FmAjH~?RrG|c{-d=mIp-UdOBE$LcJoTgcKDY5Ux8prU#s~5~o#zBzC+6+V=iKt-x@jZE$5g)&oX?r+5&5+bYx&&rq_wkrZm(~1`})aQO9kK8mgT|sb)#ZLp4v9a7oNvGcWY;0K413?jQ1Sgb<Qo1sqBpyAD8%j@O}N>J|a(@RmJC;=RM$adwrYR*H6v&P9XQh4i3EjwGkyE^3>^@gY(SXG9r%|J>2J(dk&}g!e8gwrlG;txi%@d{)ZYw<Z%O5`NH#<wIze&kJOI%e06Tu-{$u7_4Mf<k=xH#=W#E6?Q?s5o6G0h;{J}n@2%4=^7AE^&wc+>k>l;>uJV|Jr-SR$?dfxFxxD_>lpW!pi(O~QS?9P6CC<6!^10OeJ|!^ErUfION1fZ}OLCr5&w()!xqTjWp1k{^&+YYXF3)e-k5j@wM|tkZ?el9tFPq!vPUrG@O>1+`Ew`_q`ox};@aM}uFE*FwrCRQDZn->Pvukg6dmWqW*U`BhpLF!UZEovebG;5W*Xv+&y$(9JuOGMa+%~s<(7FA*Bv<`lbKMU%*ZrV#>4&EqZw>Er+s`_;{Vciaf1S(tpAT#ae}3(Ar*r$<*<3%@GG0B`HrLO!&h6_boqcLc_~&l-AD!F%$L4x}v$@{iY_9h=oy+T&J+nFRd)c33?!}&S%kBPbbGvWr@p?b^+^DrV{Bulhka*55x95e;?YSeLugc}~CAa619<R?S`MvasV?OHqN~&;aQ~2|4&r_Y-^VH_{ytey*&Sf7Ux97MXug`bM)%mV-na_i+o5K6q_NUIJKgn&M>+$+N<7u?}ZIe6hV=9;X7`g3d*|$|L=K{Iyb3NX1e<OF?-&8LB-}c1Dz&fb=s?P0xWpjOB)w%3%6^psPzRvY{{rWnW`P8nt!EOC@F7KCIufNXaJR;ZYuX8<KufNWvAEwM-@7A9>mwqGH{i$;q-!9jBx93;q_Ia_netvaspGTYP=U3;B@#^{2xy)zD&UGet?4K%^{gd3Wf2v&eLvqLdsd7Euv45&u_Rsi2!QZRT7nRHTLhd+UR4(VsmU(LfucOXWolC!wOaH&~(^<D%?wRD$|7yHGe{HVMU!BYIIIBW%p6Y(0bJ?HC?Q@a3A<a3r+}=;*b$BlHczvI-xxUZnT%NC@8`p&Qq4bZ+rGIR$?{6xX@n7a&9e7{rzN&NCKW%RJ)%B;(y5;u1YIE6F)p&iswYk3E>Rk5cJ>S0-(T8^bRJrV*<g#zmZ#tLz9=YtRYP{q70=eV+g39GQ{V64o%l>KiH<io&My|gH>0HKN|8JG+>#JOkcf7vJWqkasRc`CAb9ukydi`}S&pWwZf1T^`j_<81m-$3hSmoOPDwqDZx$b|JOFxr4`d{UGyrchBF7uiA*owe&t@j6&%kyq?y+5d2#(x~WJTOoF{Z8ewUy<wmQ|I#i&c2S?KXtChJH8L9T;`L|U|Dz{%6Xx3Ilssq=a<T*-^d;3m&)~c$N8mlnNO=?O9S&%=ey43ye8M@yUu0&oPQRF_lev$R4(@)a>xBg<<dXoj{A?w^?1kqN98h~m|DTt(f3c4%YBdBasO1g>~G|b`=`ns<MsVh<uaf5>MaU?E~KATF8xgIxSy+B#*e?Vz~qkak1CgbBX@j%RJrV*<c{x;D%ay3-yc;j^XXS;eqbH+_dAu#en{^4ey4I7zpBE#K>pQdk*}|EJw9$?9iQ8Ho6GoYyXFMeA?<6C>#uTozvRg`zlvOcmCJgP_ZeH==QiHvdc3FeOrP6)Y%cSem48-X9eON@>`#?Tzmdm1oaA#GZ*v)cxa6yW_cib7$mdt(^1P6z7P=Mr{Hk1@NAkG(6@6~wZSEL<a-Yv_J~o&6e7Af?pl`n$5V?P<T=pySxLO+{_fM6}en_5Ne5lWDyv_Caq)}UauJa+6`3!46J@9+yjgLHER4(TQd1~$zKDY5Um+`TArUhPSOwGvtSGn{Xx%9t1PgO4GDY^8&8gFwwKDF9apWA$FF7xR%YieMgKeUSMf0au=liTM)?lUTv`;2`Zo(nx*o)<MfdH6}6+k9*;^T|9iDZCG*e^f60V{`h%F`it;|MUEq!29|wZ{+@|a@h}UZueDtA6B{ChskAMRpV{0$Hyf6?Q@%t&1F7mGLDYuL%V;fT=q|L*|%-Ksa*PvT=rEp-sXC|^r4!M&1F8Rbw>t1ce{Vu{Y~Yvzmd!SrpDV`#(S>hY3TO)D%ay3udi|$AD7suq1*baT;4CaWBpYw>q+idf0gU;j`df$%*XR(o50Vy|5YyiW^>*DDwlpHcl5u?^>|1Bt6b)jns$VtV}DS&JnuHw`-945e2;o#0^{`lsdCw`$Q}Eq%4I*aucP-*mFw}2{Zr+k`6N6a-iLBts9eqqa>x0la_Kj6$N8mlJ>GGCsa)nW?eN6FJoWjmayhTb9p}5sW&C>;lEV8$?i(tX`v$q={-bi~A9Bb2N9B6F<Nl*^na{$#Qv&1k{Zr*~-y?V2KUFUK8@c2DsdC47eg9Os%%|6um%^Wm(0w2>58Y3Kx#NDWav6X9iRpoH`umH@rQgUM-(OTN`zN{M`-{r;c*pk_mCJlm?#~STdHwxP<+2}=JHFqkJoN8Z9GDeYhr}(Budi}FzR&*5KDY5Um+?ocz8+xno{{UXa(TbxsU>$tuD{A<J;{^Or1!avx49l4v$(s@Z9X=a`J|mZFR%{Z4~pzhl}o>o_i5PP=QiHvGJf#5`GNTrsTleEs$8BI@@u{JMLxeOm*<hZ&#C`h$J<<wPs%vU=Qbak%X~hozaa4E$JUPAKUFUK6?xK!6C(FdmCJrep4z{G&uzTT_4wpnFZx{PLoV}K)Nf&69X@UydA_Jz&I|HuT@!t7<83bEQ(jyYc%3~NBKu$Eq31oAOaI&RROND>l1u-q@iy1vuZ>CZxy{GsGM_?C7YANve4)txSGn{vxqU9=KBIEE&yd^aLXVf{MU78QS>bb=kIiL1A9h?4-iOjZDwqDTIep?7PcGxzBrXrkqvj761Ha$yhbou-(B^huwfA9_%YB$!_Ek0B=8p0A&iLHsV{@6$iZjb2`q1v5Dwq9}T=s3-Zz`95BbR+ujkmcTFMX)yV{@5L#YQUvKimD&?r$oW{f%7qH#OeoGQQ-RH(g&}<$Ap1^;ItazE<~4$!_bfbNT;&$@Ti{T>k%Da=rdK*W>m2>s;nDwQjOo|La`-|8ASB{@1zfXPfK(*STZ7>VKU}{~tT?R^WZ={XymOyxUyw4=T6gla{w%9iZAjbuRz@2D#opbuRxt2D#opb*{(j{Zr?%e|FfpI=m0%yimEE7vzrfOXc#slRM5YmFw}2^GoG2pWo}R3CvTU?<$w`n%r@|t6ctlq<WvM3GWko-_W`I`%dKg{-bm0A98*F(YYS4?>{=1`_H`^YXh&N@1H7{`yRRD{;6`=56K<(PnGNOj{B#|<=<Z|wQFtob0Ph#a(TYU_5EDu(*Mo7tqW3pe^I&g8@c2Ai^}EvB6oa$QMn%P`2M1D`S-^zG+rNgpX&Ra&Sifl*Wd4SF8k*z{R4T@!zq#9A62f$dzN2!9dC1)&xH65fpI0OMXbNh<^7T;MbC&lPgO4G7kSL0FI>mlT#vstx~k7@J~o$rsCGY)C!c5-d4E>9^c%USP)VQLc$>@k0V6jCet$|-<nya?d46qPZ*JuCsB(E8$vr(TxsJEF9v|~vU!U82Y%cRDbTN>}rGGT?`=iQbzao$65+8Y9t6a`&@}$N&eQx7zuE)pC>+Ex#54p^z-=Mbxzc;05<oTj<IbX<=YBce=jkmd+FById<emjrFGlp6%BBCwrT^`HPvvsoBbWYH<87|TCwH9gbDNLNrT-6h-4qy?@!rLVepb2kGr4^(<olq?<@+GHeJ=EPd0y1`q&XvfZu7CZoEHnOZVK;1Ie%3y=daD_6UTUR>9@;6wglc+&O?#kA5|{<C%Npa_WPj9<@+GH?5k?L%^l;Xt?{|d$L2Dhhby*3^r1b!R4(Tix$N8azNd1z?~%*Cs>a(~kC#4F^Rc<i=lG@Iy4n5H?r$oW{f%7qH#OeoGX6-q?XIt{ay{Ph`YM<4v*Nb9uD{CV{gOM@U*)o%<c{@MxgPIWf0fI5x^u*KxBl0;+y}^Y|La`750dNt*STZ7>VKWfeEy!C68Kr~4=R`a!RC5@P`Mo+mvA_c>-|&b^52h>>-|&bc0aVa-amD&$Lsx5=XO4+srORC`_P^jI=APA&Gq@EbK7q=*XNhc^>}@L>0IV>yv~lmICZ}3+@9Aq*XO&=Wqi$PJHq?K-ZykE|J^;gzW?Z4{`+onegDz99<T2|I+yv(+Y@{pb^p}4{Cxs8SNBhy%YT1OuJ4~Z*W>m5Q|I#cCzQXxBmB9Lepb0WU*!6Ju5;=Cy3Kb6sJ_4GT>6b%e}B=r{CDf*`umH{^?3dLMdx-tao+vG->bgg>0JJMaB}_qPUrIX30z1GzE1vT5#x2P$9vvc?>gS*GM^<ib_M?TxIZHHADzqlB~L2SCSpBxF8{qedCZPv*YP&j<FC#A?ULJkY%cTJI3tiJFNu!qPnAo5l6z|3b{%hX8Q<u5@O_;=b}{^U(YZV?Hh-#9#Pg_g`Fjt@J>!<Sj<>lUACsn(&uu<7m;L08KLdGO@lS%EqusAmF8dXE%&44^`=`ofKO|4;^{MN4o9pp$Tl4u`=R+>@$<%mv;P;;XCb-V_yimEE7vxDD()--T+g!$HpBczK+gC@Pzbcpghg|yKo~J68^ORirUyZl99-lm{mCtQHHkbJ%z88F*QhOurKRTEFmfSuU_CBL?d!MnneJ=EPd0y1`q)jz^Zu7CZJYS#wyF0uOZU5+8?t3<;PaNaPrQgOM-4l3URbGy`KkHofPjcB;xex1H{{9wn*;mzgn>)rQKkIXwkIiL1v%lCA(TDc@Qn{R8<g#zuep9*h8@cSOYP`+$c<DnmADhd5KI%bm-R%Bp_cxWx{zfkQn;LI(8Gq-oy{@mXay{Ph`YM<47c1>`TYsI)`z6=wuXDSeHrMN~b3I<Kzs{u}ZZ+HM+W#t-ej|7EzsjYb$sPT#a>sbx|0<XH%*^s`;Agcz=v<z6o2&gn=Q93Yd?0u1pDLIAliaa?s$BL%a>xFuay{O$f2v&e&-PQ_4evv_FR5JaOXT|e(z)~-xjw&iuE*>1OXqTa6+IDr9euv5T+VB9$N8>u8GkhUzVJSg`-aNpzCrG||EOI0hum@hQMn%Pxc{i!&L=MBiQwz#`=`p~{%Lc4|5Ul`Z{&{qr^@ws$Nf{~a{t^nbzk^%A^og!dA`W?{aoiVe$mB1uD`$NT>6b%e}B=r?4RWN`-{%?c>VoF=Q5wUt=<d#Uj6+}<+2}=JHFqkJTN{!;%~$3dS~FIxc25z^mrce<n#>a8}?UWn$Y}X>Hb$?4yyjY`l~Rj){L$4|NFZzGcNJZVXnW{_-i{{0q5c?@K@kV_$&BC_yRr=e;&SwKaY=xFXQ9!DR2=!1)mMy#%JSi!2|eP_#Su$--BO*U*nhX+y43&{szCsf5U&GjDH5t;Gf|i!UOn+_#yZ<ehA+R7vWp+W$<Nu8NL9%h%dljgD>E(;WOb&_)L5roQoSS!RO(d;Tn81zSk4#mA#blbN;#x&%*8aS$rE@fp5c?!&mU-_;ffCpN>y}&*KyDv2Z*-79R(v;N$QlI2%vGXTi7dS$HzsgD2y=;U#=Gei7crFXG>MLOu5#W&9t1W$*_12>cf}W!wvY!%Z2#NA?qL_!)i={|bJHe}$idhwxMQ`*17%KE44i!wnbU8}K*bYxtY^N;nf=iLZn6aKp{`I{YBqiyy>~!*lp?{Dvpgmp9<=_znCI808K6A9%Dk$c%V2o(X2gGvQfa20R0wSr*E8dg#T|<A3v6n$PKPKCiFvzwuk}6n+c;1ip`dg71PG@C|$hyC~y3;7WW4z7MX$*Rj_7DC0-qar_AWIlO`2U`;=#jQ;}7n*PGi#{Ywva8t(9l4ZfOuy$!F;}1MRn)Q0Xy4}Jb;NQSc@Ne)7a2LLdwYWeTKMD8Y`*_bMDdU&n=lJKmx673AAK-uZ5BObZ-p^h5fcyb-y-OMY5?;VBFpn?cW&AR~!}zEE`q5v%`YW9`NDurGH)Z@j*{Aq@{2DxpU&BwsRQxo)A8x_-;~U{pd?UUP&c_$x)8MQ4G<-6gfltOK!PoIg_*A$UpNh}%*J`*4F2)!0XEssB*TNb2TKo<8D*gt(3eLw@;p^d2d@1X)o-+O(OvT^BKY~Z`kMOJTQ{3=Z{3`yJC)5Xj@w4$X?0ae0=M2-~8S%`}gJ;GwK+`K3_}REQ$L`ZB|4_!igQq>AbI|xjxZe{xH;wOx8$F?O)_5{p=n0+6#%IB4p3pgNJPA(rgwB2A<KQGu=$>GFES%~I-7AbwfO9;ddx-Jro=`v8dy8>%uh|CQfvfR%@DJc7+;A=a0sbz01AiA!fvfNod?#Fw8@`9{#6N}~;UDAQ!mGI9U--B9pV0KmpZsk6p(oT&#tqF``;apJGrW%fj9-Cg@hkW-xDDUN+8v{eABG>`AFxJ;DdQ(#3Vs4V4|n1_S&Q?O@tg2l{9E4hP0IKk_z-`{d%Hs!{~lh!zsG&>7=Da-```)OhkpUj<L8;j7w`^#hu>kmvj4Lv?XSB2Y7VQx(s(tz2rPgX!E?Y|cn<tgm<N9pe+(AFAH(y(ig-S}By5D2#B0OOcx}8bOu*aXiEuogh)?m?A~+k4$7ka&Q^rTa1bigk6L!XX;@w~)yc^yWR>Yg)Rbe5#DqbGu!OP>tVJ^HlUKAF<i{fQrY22_fUKVcx>*7uD_TEshw5N<e>#qrL0BnvAz?;Epcr*NQSOk9@FAQ_wh4Jk0Q9L`I6+VV%#k0YDcs4vQEQ#mEOTgNA2|O0I#bfa{FcEKq4~0|kp?H!v)N@Ic@rC|MhHt?|_*?igI2&JvzXo5%4M*ay;m^aK`15!_*bVQ8cY;mvPIyCD6*nx8H^ghf;&?5*1}uu#!0W@ZxM35#KHe3!$GhUa;j?&ee4;nhmlNR}d?G#<F30EME8uE;1-=HZ#n<5LU^1S}XSR+q{w7?8zlkq^ui>xp*({)pzX<!`FXBUBCwvIr8aBim@)@+IjJJd}@RoQ7SRb#?T6ds~cZa?4?)Ydp5ueDKj;4&i0$1R#;7i~dd<ni1uEW={b}K34^WXw}0c$jmGX4S_g1>+dg01n^ti>S8cwg87@4$QROBo*yN8_V;Z^J3$FTo}FOZZH<5?{%@XTlfonfP;X5I%@`JO_v4!}%S?NBC=+zh3p%D!3F*!<XW-;0SycJ`VQ4$Kn0qQ+R*;N%#c*BpwH=;Bj~bSPrj%7lg&|f_QEigXhL`!ZLVHJU^_2=f_L=s}5`oE8&&+GmR<Z^<WHM53df3;nne)upC|!Zvd;{Raln>l<|)6DZC^84D5kFgO7zH@DY5*V=3eFy`essPZ@v18{GE{SHo5KYJ4qRim%0!;Ve8EUkJzH3-Kh_-y1pyjSq!SdPC=?@is8d8#-r=$HEHU(79~91T5$co#V#y!rb1_xo<oh%;^o?6O3nt`Msfgh4JjLls9w_F<#gk>L+_|F>dZP&0srN2XBXWfsJv)dUzK+9#+TW@fNTq-U4q08{mc=@mBa?_zXT6pA5(1hV${s`0MZu{B?Y>H`Gsy;T(K1J{?ZLr{kmG0DKhQ3pT@>v39*E<4?mbco){_Y07vX*aGi^4}`7oR;<N9%J?KW8K2C1o<td+0T<(od2cf)<5S@%d@4Q+_QHEH?_sbHJ`5iN2jT;n#~3&RpTX}ie%xON{q>2zzJjOVLHrcH7w*FM;+x@Cd^5fQZpSy^Z^J$K+xQOnA-)4Y06)VI;1}Re_yznM_%Hqqo;E7T$D)F6%6LA1RfHwsV|Yot5M}%kXkP0Pem4Fazvn0XH~cRA48Mzi2|vWY#81LK_(}W-+>Rf?--lcA_wjvj7rqZa1P|f|>4QU*@z3EW_~-bouwJ=E8UN2;*`tDd$j@Kl5Amz;6n+)|2=2u{!ry_L@pte|a09*xUk~5L*W(-E4tyh?0uSIR_<nc+-;bY%-{9x*o6z*rO@20>h91j@r@`}v^;}-ccm;pO!rHJRUK_6pOX5}W;;;~2h`uaN8GjU-zI>FQjsH!r-o^jMe}G@&Kj4?)N&F<ec$qSO4!)0{!_UBd_!;~XJcJ*j=Ppske}T8~U+_QRfA}AGj;K&y8aFJ3=fF$D$MMp5HCP9)hS!Dl@Va<?7>md9nboI^*Me2?T6lR_952piQ=T%O2b#|&4?i1^hCkq@jNc%;j9=z6xIr2J8lJ(w#&5$*_$Ai*Hf8)C`~$y-XNn5atZydPxip>$F9NIKMexe7E?yb00qf)SS-TpP@v^WyUY<27OBv4vqw!q07n*hP!mn{t#vhQ~#&7eUA5g~AM+Ir#XL{am5j;I!09M8e;6-5#yaw|w3UlE_@hs4b8=84!f$7Q9^E-@Z@K-^974uh3SOpfutKcPI2D}8G4c_+#JsbXyH^@8qKlqRE3;aj?Q+NXZ6h8_N<45t`@I8Dtz74*MZ^O61RD27*6CT5N;ve|yV|WD~!;kT2u29A=!gukD_-Xhaei}au594QXA3TAdU|oEa@$cas{CoT_cpv`@&&p?FKBugFUd8aNc)74XC`TEu9u?g84C}y}cpbbRtb*6WV_^wA7Ow!a;T7<_(DaHu2aTtJKYBywrtzC(pL#>*tnu^ks5f*j8{ZFidqd~A@f5ht8#?!mZ-iUCp?iYy^>C**bgwYJ34Y)W-9wDO6V^}m-eTO`Yp%j?;m7#5_|NbPeudupnKJ$zJdJ;cUxR1yYxs5O!+rG7b;@{DRFHq+ri|x?rf+i7KjrY;co|q7FN0SK>!(Vv6kZ80471~f@r=;i9W(N?@!!2cUd6AncE3}`e}zBeKeI-^QpW#;*YH1aPgIcC@$0OIhcccM=EigLo^w*hV_+q`67MaBGM*o1#Pj3npm{&(;IH_v%rzb3jAw>sewmqPPCO^SFEh-K_x4v;e+}{1^ROT6iuc3Y!`66vya{ZIH^Cdi=6FNA5p0V$!dt?gcuTx99Eo?v2f>%|LHG-B5&i<c626VE#CQ1XLwEqbjUT}GP{!Yai}1Jb+3;n2Ha-)M#Ao8q!JhbYcwg8S?~8Yb&GGJdC)gD4gm-|g@eX)5*cCVIjd#OG!y))+{KcqHue?YZU*fM#a4~!yUyP51{qV8)Gq64W4Biel!Q0`DVMDwz-T*ej8{l!UB_4;jfSvIc_>*uD{v<vSzJL$JC&88YB>WAy1AhZgi3;^x3T6DLzs|!8@I(9pei9zQPvY;xJ-Fdp`1|+<I2+%9FMu=g1^7$wIs7GjIP8lXcE^X~&%#dlvv>mRfG6OIup4eT8c)PufiL2(;B(;;d@jB@D%6*o;RpC;{2=@YKZu`#ALFO+PvAxT6Z{f9kDuo=yF?j32T$VX@FVbj{Cz%~Bb4#&Z~?v@UjbjjSKt%jaC|tQ!9>dVc$k2X$EUzVJdw4YLK%Mz&c$ED*TBvAX4Z5KWqdC@h400W!%y(z_!)Q!zr@;|p^P7bNAM%8(ILwCR=5J+iZ6o`@rkU(GRpWoI0c`=d!9!be-p03*YMunq>S%^$MIeGK6nN{!@T#wt@u8C9bASlV;<|^oA{gj4&%xG+U>9R{B;(dfV=S%_<op-@5eX7S@=eLA)J9P#HYbA_%wV3?1PWMd%&mh9(Wtr5pRPxgYkGX{0aCJ{si6%_QG4?UHml|j)J}LUi_I+l<}c39v_PLhaK_$_yG7cJ^&vE``~?8mtmCgsc;596`v1h;q&qJFd0wgGhR;_KO7b6gTs{Z(^0{F&+ub-7XKK(2v6V_@$+y$ejYyxH{wU}6u2-dbPgJS15S$yotwrd!4XlRbJqAk*dr=*E*pOmwuuUz<HlRSW>KMY-*_B+A}VxGFx~*RiVEE;j5mf|qC)o&<L#nC{bcVg#?8HEESwAn<CF2}a1?Gh6rYYK!Txv>J`N7R$Key;Fx+q|J^^12=i|%qZE!tqco^S?r^3^CDt;^~)KACY2lz4k9k>a92VV^r<E!yGa4bHSwVOj3e-%#0r?W<{QpR70<M7w<rEmg1fwfpl8Q%i8;oEr6TPWl2!ejU`-rKvB@ttrrz7t;s=iqag_bT{0z6xIpm*PvA$6EL<{w}}6_#giI#b43U9?zrELH^CpCjXl<ehc2fZ{eTAFY(Xu%kV4wGX5F-2LBBI8vcfVjsFB6i4OWtxHme;Lbw;t1uNpY@EWiYUITCGub!|oY=n2l+fv4B!-{xqyd*4ym&A+0NARL}7HHmE7JfGVfcN_i{s6xRzryd~Kfo{XAMo4o27VjA3xC0Xp%3m-#xq3+Y5E`&Wjs%Gs8{k(#w+`)F{}h1#Vg@iq3Nfr{A~O$dh8bd7yd2$9RC)-0x#oNa3A~(_u-$yuklauYw#!h8vY|R{q!S08~4y-xo{7j6V||U;?-eGygJ?@tmj%##(Vf{ARGjH;)C$MuruBl?*!Z8ZRyKSl<|hJB;F7&4~ydE@d7XlUI0%IO<$&m_i$6j|0DYW{}2Bc-p2pM(?$n*7r#pnrlpJ*fqC#EcxhM}FO4?|>&qsv3*H3p3ZKEd;{D)YydORU4#kJyiEto3kk2fUGX5;=i$9BZhn?_Fd^X)F<IQ1tyg6PC7Qn0FIbeF+(0m3t_}Tbl@L$}N@qEy%dp_2`2%Zlw4ol<3@w%`H-h?%+OBrtu`{C{J-f#%s8&80Vcp__;KpF1_yW`ziqi&S(rmz~`6t4<%;5k@}s+94vFdv?e_gt1TUJKU6>+;@eQN~-t-gs-g15CgZn0E)*6z_o7hgI>a%%eW6h1cSD7?1T=8-I25*8tcDw!!=0Pr_LINjwggz~k@=Fb1!H7lfJdf_Mh_XH?KL;P<0~{1v~C--O@eH}R|RJNzpC1-yfQfnSHe<Ja+@{S_4*WJdTq{yTrhxGCdl;CHww<NuI-kN<-|gumhs@pREa{)ro!bxB7V&ktkp{CGK70xyR*fU$TipK$}q_|sv1@HAz-e{^u)GaL*D;Dhm@un#^I9|)hs2jV?o9Nq(O0V_m@&OzhVVZrFoxoJEn%n%(qXN`NH=@ok}-{;)EPp{Z>{3hr8O?t(i`&YRaT%}j+J>d)P5ns?N_FiH93j8@LbPqB9ZCF3qdy8>%ugMB?LzCyGj2DI(@r?9VVaj-3XnHFzKO4^mAL6ErXNRVrveQ@j@$C5HupIt4-V8Rt8_+AwDC1AT{`gaPudsgV1-szA@OH2<-VUz=E8%tUQZOr?m9;BH87~G4<AqtHVwCYRFdJS5uL85<*;$J!l<_BEGrSq^`3cH+JnV({;=RRF##_NUcq_anEQOb1-Zfzvye3``R>7+<k9sg3kLPz7&*Ohgiuo&-zaE2yU@^Q9ULID#%j1n;UAz(A0k+0F;0drNo`8>pgYc2~b8tBR96lN*;-m2)@L7Ba-Wztsd*f~WRUbBoUGe64C(3v?_$=NH?+X+0zIZ=49PfvBhlB9$cxTuX?~FHvt?{OKO;{JNiC2SF@M?HTSPVDJgO|i}!d!SxJd-EXE14+ckN7JC%myFBv*86{A-o`74wlEu;c>7L9*4)n4tPA?A12`a@eyz&J^~*DpTo!Cqu^+K6h0UZ!3X2LU~jw^-UhbC+u-#)p`NQp8879pys$K^kC(=4!RB}^yb0`t8+OB+;4NTZyanD4_QTuZ?O}JkJ>C*_#toa|E%Dm0CSDt_1gqhd@EBMUH_VC0;E%#g_@j7w_z0dJkM@N6G8%?m4Fb-;9ufG*OPPPt!ZdhVJPXW>XTkHqym($dvwW2C3a}Pl0k005;7#~!s#C^eVLLn)Zvfll4e*ArCEk+Hpdn?vEUbi=#S6d~JchL{KpD>p)8kq3bTAr^W=+#k#xugSct$)s%z|gf3&VVPKGv=<WxOh^j#p=ms#3-)!UlLnybNrJH)Ji!P{#Aa0(b%5bAHNr4ww#4$9u~`8P5%~<GJzTurOYjc^8Kj@#1(9SOzb{Jc_^^cn*Gt@u&RN(O-@I)eLrl9q}&s0QeL>03Qnb;6w3Y@ELp<J`g^Q55#-GC-EM5EBFN73a<le;C1lI@Nv8{UKEzV<6C>9az=;#^1Zp`TD3awe}kqndqV#t1vY@O38Tgg;&0>Ae=_o~?F;{tS^b-?{3U+zt<##%-@my;1rC{+tIbdU18g7w$^'

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
