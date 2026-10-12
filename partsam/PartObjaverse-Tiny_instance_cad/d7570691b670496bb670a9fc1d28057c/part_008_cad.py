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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d7570691b670496bb670a9fc1d28057c/part_008.stl', 'relative_path': 'd7570691b670496bb670a9fc1d28057c/part_008.stl', 'source_sha256': '901bf3a3d62894b512e0dd2043db4b22e16807c8610fe6054dd7f0049c7bdbcd', 'input_faces': 840, 'input_vertices': 472, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.45858293771743774, -0.018758714199066162, -0.3971957564353943], [0.04050353914499283, 0.20489239692687988, -0.1717531532049179]]}
GEOMETRY_BASE85 = 'c$}r230O|+|L#|r$($jI43!X-N(gUKrVt@AROVTV%q(+d$Sh+SGi1t`sn<-(5GvD_d1u;eY-}6<_j&I7RqI^mT-UkI@w>ji`?GFO-{)E1XISffb8Wv41qzxg_)|l9e&XQ?eSJj{VWyZX5re|U4I3~hyus+uNhV4e>5D%`UEZmCN55VsN`x}SZs4Hs0bzDct?fJpyW7>bwi`SqY+P8#=%6uS0|yD;CuC&!AcG%1G$eG8;ku4XW9RzTjqK}NPqY4i{8QX81l`D94^s@PW?Sf63Oy2&DX(AqOJC_;=dAGcrrqJ+ZU_H#<CDVI4NsN6?uQ5bcMs0VJk4ySuix$pzkP>fnWy&`=_@B);Qu*Q_N%Pum?iVPaK?DtXUTq*NJaYkn0jbGvHdZbr)Xj6E2VAWr};=<{Rm%eQXBpsMNi2*QA^-&sgC^D>z$W*UMAzdj#WeZ!po1!_O7Kdo|0AJ_uB@)eJS+Yu`=>3yCU-_?q!f?VFmb`-ky=;se9~>9RHE>$n*E^6xna+WBAsk;a7K;<5vz9%hLG6Esx7O4?2y0<BP#Ro~{{>?r>4~)e0Pu`M=u1Pb~s}@NPLTI*(20_fsMGu~p@~=*p#|KJ855w=&0kd0d6x&jkLjeJ5o5Yv!28s9z7{-(M<rLEf)xG}gn$pVC+C2Fm-=*=OOt9)5>kXAI_X=xz8_-@#x0FWSF22jB56@`uEs&UTyS_;tNsqrJnDWBJGV+kcdTdcJCjbvQQ{{>wC3A0^;*md5{VCC9IOS|0P*`Z0X76x4ZjC-~>?!w)$jef>y3-0z!f@YO*wkJ5Vx`dxVm{-sB9J?pHZG0r>Z;ro=3dDMU|nHvAVWZZ94N7Vn-In*JwI>!0#2IleCS+w71CG+SU{4+KF(WCH3_r`qHJ%c<KQ|0>9d$mP9Tk7GPEtcy<$@Y}KI_xy^q(8<!J@W$NuX6<c(*9V_NdwWo`C<6m+Tp%t2Vy*34<Y}}4ycd!Ta0H~68xmO@_u!W-H<0?Kk^)$a9H~5$Dn<eo$z-(l>1um)-YR+XYdaApS-Yc_ufLDCEMX2+P7Q!zB@7R+qS`Xor&{mM@`h>`DTpgd<ypO@>-~K=}qvXrlCH=Y^1N)#3N6eAnc2nW$>HE!S6K<^JRAw^V@kN{J&12{{FVeKWV*Y-qo2+G5%|@=+|*P>J#7r-+cwzKW!`Pua0a6zvFWFZXe{iq5SNN`fQHTv{xKj+|l@LOJiQj#9};Yi#RW#I5#rgkiSMW+7En>b3;EOJHM}5oIIl$ztP_}2j|1CR#*>iQONVoW{>RGKQJ5nYCim%LvWt!Pu|h^iM>z<i}o0Q#60-@pUd$m6^7z|b7pGtC^J)#$8|dA%N6USVmQVhG*!EP)X`f1ohRlud<gDq+!Xkhg;BTkIjCFIWcbhgu`dF<YJ4?lhODQ)OnHnaZW7v;m<@k&DcskU3Gn-#N1dnj%+BxsUY{?_HSN_4KXGmxn~QP&5uq8szR_@v|2xm1(irE*@n|0zhIu!)NBg#6@O^tE=U-Pw-?%>Yxpk4J?^x|Rzg<t`tMjIw&%ge48%CpjKwr%|*FPA+I;_Pxwq`c!U^xu_v=LY*1#lj!PD9~GyUF_NRyNT3!!uEzXN!^FX9%Ac&MEotSGgDhzp*#`+1~K)2lKvsWj)o1X&8TCZ}@yJ8=w2X{c<^YUc5Sv@yzK3-~GrgIUc^}DEk6XpAvg;ZnQXqbE835w6`$B^KSJO<nihP|4EEy{TO}YdQjVs!~KrxjP@1op$;`?YJBxW5%e297WX^56WaHS(#}_GNA~*(=Ztd@{5`(#b8_LY57hX^b3kWnhv#YiHfaB%0@i0xIL71Y13&B<)~8<?_&vPg@12D6B)$Tkk4g*VPd<SAdJ}|t?s9`)a3=cw*9!gSHbS0{<)p8_G8%RJ>5TTK5t{ajIeevwAI{HT+!q=4X#c%B_w`vkAIsUnw{463*Q;Y5zgr^Dy>WOCsecZ6CRgHn(fYlz{i)}2o$I$&V82DM-p2MpJv)^`eusLpK04Rh+4+4Xp(E<^wH(gdiDvM#Cty4a&2V2^ifihlrWM0Dj}=4v#i!s8O+lWxPxoc}x%1#3{)O>>dM|yY(zw%dJR`>7Ja>7A_D{BAU+;3blixSySC*f`yoA3-`;bGZ|BjRJAHIO!!3KV@k*I^!Gx&X$BhMF0)Zh8({ru}q^*Dn2{csQco=U=VJfRZCU-d5hE%Q-lt2mr*1+T-uIZv)<^-&`3t92Uu>r<q!Z?^;UHTw$sb&N)xo9;%xdoQ7V=1A=K;7F~Xl7aeE9)|amx98zEKBCQ2`5gSqo$<M#_fpKe!&&%#TgFO%)MSmX7FmrvkFBya{(uzJ&2Ja#9H2*@12L$x8S1H?IRQWYAFQ__Rj?m3k0Z~n0camo68S40)6_xrd5U@OaTs|*?%_GxF9G!&aR`3Ubv$1_@5cDmgYZk{qJ7mB@L%oKj9*uC6~_N-58B`OHc|F#{|582JOO?+2b`Y^PoUpAo8Z?QhCFQxp#DQP!k_7b=O8~H{q}i&>fa8>IkRlNW**g6Lr{l=b((dnY?^{~dvY!OQhRY;)$NKp-&~`qzwz^+uIy^~{QRiCc10fBRmk%&7VYDTW1M~~&_4M1P&rPgQn=q*D%!^!M8D<RX65%4=arbRDu3Y|aG#;MFMXjNd~ci#e_;~p)~gTJr&)xy4zIdl{58hIj~}ajkLnQ4dGC(*gc^>Rui!9Eoec*+>JvW(<4+uoezPuO9j1;#``KNvuYX{^l$??9r#r%5d_e1)`obS_1%A*F_>qCLq;5Wr^)_xW{O!B<$#K4~a#!PzkHq&OVe4>iL=A$kdaJSyW<F?tDFFV8+o<O@H}q@S4gQ5(jHg!{)Y-`&{_`{Pd0~97P<^_h4*t$qpA!<YG(OMg-_M<Oosh>SO`gyCR#S0bh1#Qi=@@*^V{!reG|)#=AN{wZSsK6L4CJr13G;s5Q&WH4^<>QZT^-lqwJ52f6=WTh2F>BS^~ZVg#R=o_@_?V@gY|H!oYr5^5A8!7uuf(*;kueLNVc~*la=3BKYhgaNE=>ZotU_wePA}$Vf9_u7nK^pzhaJcRUsMmukQ?B*JqK;_hDtW#_ySqJW<==uX2FjWfR_K{))zWsB6ddFkrI0{(|+O46luG-foO}?_34*HKP{%`t9LYUy1wLSp$AyFVtsUG1Q^F73Zrl=8>N}lonOd{zo^=SGh*WKh%Qb`6SnaGNl&gaYse?b)MikUU@q1E5jUq>vp)`Dp6YBHcPfwXHC-j+}Fyds;I-u^2}38ejZmHhh=K~)V=7pJU(A2c4aYsmjKNBp=!wQQ3mbHB;%a%%)<N0;8O5oy)n+d>(TFt;_z2Dg<mvY<Nw}At-4}7HigmNDgyhuVmsvTT#)BOy_EdzbpyWMlYZqHsKc^=?EJpE-5uxHs?%79i~d1-U9H)2UJ^#g^`JNV0N-|x>{op_Av3?PZZgI96~^z`8vlj%Q(c$KYl~8M^ZRPiPN@Ir&p01K-lF}*MHuIu;n^DBV=$gCadXjc#2ffKZp!tq+ZlrUI+6>&N;J+BeqL7od4YZ#){x&98Q<r1pYFqtoR9h9_g(r%cadlAYuv9*BJQhS7W~VF=E-)?``*>~MK8<u0posDBk#apw-uke|2u~KMQ*^iv&a0p+h8BPzW{$kD8@g~3*)bP9)5h4;WB^vUewL|Ec_<6_}*#OBkY$@J^Zcr@wwpqORS%Lr{I^ahV_%N4fDPy33XVq0{isd1ME|WJ!tRQ7vEPKzh|be>XOm^^8~bSm5BBaEA5y0GylcB1nh=?!&a^beeOHlm%0&t;&^-xJ@^UpvTHrpTQ!{XQ#QgkkA)vu1M}XcGtQYEOEDgP?ojqm%+mPb?{MDo{Z_wpKKw%cagKSVqYmF^A-|vdT>1BlI^aCCoymD`J4cSEb1&(u$0x&|QylxQ$~`;>w}is4y;;^-i7?H~@2k1<@xA5d5?EJHM{&LN!9H>;g!Uyz!cS|LDEsAeO`R}=`72|8ZM%Vb9vuk(m@CfDW_rxmg5K~|Q~Ca&+p5F7RPPQy=W>|L&+olemu?tmMt#)ZzB$JEu>;zFdxhW2%(#MjI=6%0Wdh!Z3l&2C2cGbq{>468>4o*_)Pm#OBkQbltc*Gra)rNt#blYM!c#o2=QM=>wI`m}NwK)!p0=E?DLAjZ%<gLZTAlD-eRVPVJzE2Q!UxP(r#RH}O?94og{I58JuI88@$Z?)^{gK~7yWu#a-0(<$@~A7ruF^w*e`rfR(4l{|8XJq>CQ{2TemXs!=7Rv@p~%WPBZvr0%aW(-v-$l-}t?~&Kd2?7lj}DS-#gPHa^%F2`2Dgo8j|I%PtsC#xJbj9&ItdW4d77mi>YH?Y}0!|5PVApuOFHXg{MF+Vg!|o$?j!b=k6C<MT^r^8x;nKWE82#^-O$8~7XF$nmRFEs!Vq74o|+#C~k7Vn06p6aL?SV*lQ<*7}F0U_55Ckmt(-<Zt07--p%VkFqrWeM_9f$xG1QjDB`J_BB5*|MoL)V%^?3p=q!7^hdvyTH@UEy^Hn_?U4WZ8q7;bHvGia*w?YGG5+E=;rAPdJl&3H{Uh_x-uQdEj~C$&Sc&%hUPxE%0{omgc#gz{VmuE|!f$&J<Kg+NS{{dQ{Cr`2|8z=*-~Mz;{`xC@j>0b(fPSssqhIemr~`lRpuXIy@r~d6DW|rh-@Du4pX-V9kms!~b|d^7t*6NRu5sA!BUd7SgYM|JbvE*>T8{RP!RUAY9~l3PDEPsLv48nFOSfx2{GI<{zbAIYzWX^FzG8}V>}_{`pGN=NF}Y9GVl#0*EDd8l9cRisfhO2rF+(uU!)@?h@q_QN*9W3Kf6uEH3`U-31K_)LMEe#V{5@|V_YvQ_j=CU!oHzW)`*M9MGX}t~SCn-)F6*Wn5r}<S{v*yIecc(dU*{-12WvlouZ)o6*T<ZMKPel2PRumfKCwUi{?{~lem_q;oQMClFUFbm9)8pjp2v}>Psv2oztKMU?iJ_CJaN^rzt+WR^8DVXbMW4zgx16T^8HX(H#$T54&(4S=yAiFvVGa{@R#0#KRsCbdbh69SF1Z+l;a$?SNgg`p74#|KQHZuJV|cw9V+6vT;?|NI61-R_ehGvWaPPT4?o^b=2vGG&cOP&!FYOo!TGQJBirW`utIz1#xlRIfEn6ZSVE%{kpIz6^qW;4zVUkxhtD_U&(|-5JoA^L{ha@#ulFpC_POoRZxY6#o5_9#G{JjyQ3tI*wi3pl<}I)Fbqm3d9f;@DqbBHYxGA*QX4E<3u^eac?H^K=RiEIe+Thy!J2dw>KHrVE$9)a`0{{77)Okt}#<SxSe3O#!b6=x<#^0Eq#4@PcjQ6O2IjGWVKK6Bm&+<Cn;~o6i#rV9S|BCigkxy}n$9P^nM%_;QiTnX!sPhF2-2cs&@FUmbzIyyA+v~nRN1pKYc)wCr)Gg)_{O{+m-vbs&-}?AN_{}^pFYhZ!KmOZ2_%>Z-{gpG}xUPK{{ciTex?MFM*XcK*BV%!H{GEh;pWJ}&RY11aJt&2Fsd)|g?9bu6{p_BR-&gg2<G#YmqdviUw4e10pF6(XLi<O@;q!BZ8o3!i|0x-M2|Lu`dJe`@48A%x8T0i$7j<wsiuT)H;CXaq7p^xZp?ybh)ZtmG*54L@I$XPo>&yG`_sKep^X2CZjsIUitmhs5uzvpD%klf7K0F`d+w6wF?<eNV>@@1OJ^}thPdo=-m$)VK&)oq3^mMGx`H8aMoPF!y51R$w>Hx;`S1kO#uJ8{Y#=IAVuRiideJtkP)cE5ZH0O!lVl{l@xzR5f>$Bl1<o9ig_LWOuzIv^I-?A(A@9DQU^ZROaJFK6;#h7=81!%u!jBKyll!oyq&V@g1Ao5>5jB%cs13#!1=Do>-42{qAtmYiT_0BQS2zSh5H}2<Kqcrob-od$`rg=h#FT(vg@5gxDnj=rerFdS4A47dyoZ$zr8zb|_Wy<-|7sYv_#1ECfcTm$`Nna^ajr;2<@}FCdJiV*Hua%4Z1=qu$Wr{pY)=ZG?y<6Ot?XrH#^FXOw74Nt0uFL%K`cLrr-mCY0F8$z)hwvRw<GHr0vdk0z@&VhY%IB~C<Wl56aSOijIeurm^mWfJ!mo2+o*YjRU-;=K;m1y&FY^@dk37Cd;ahu!$~=i1F&^u^@XP!m>!VyaD1F`BNcc)=`FjezM-iDvdDS02KOgB11;Rhwi}~a6p73Ne{EqXF$^IiIToHbb$$uAQJzqIXU%8(Ne^Bp>vfYe?qf&>tqzd2K{u}(Vg^!~DCejaXz4MaXcimPTk$-=@3fgDeUB><PmA<lim7K?TrK<Gxah>3|S}XnF+4ZDv-L4Jt9Q2UBbwMZTE9>3S-lY}t%=47KuE+R8(hqcz-!lYvb4$fK9}NF~6Y0li`ba;gYtSK#>jClv_)1^D%@6JQ@0YCa^?~oNOOif6|62Rnr%8WHRrv2e$@jhBY5vl;ZanvZ^uLyq?_D_~|An9WZol;T9u?nvQ@Zr4q{8R>r1he!(pUUXMalIs;I`b4IbKEJpLC9v^V;GI{Di^quSUZklq#PiIj=v-eie_N3#4D}uJq%(1fjjvi^bBfXmMGNzu676pVvD^_It%2ez>h{uU0s{RJP~uVRI70(BA45{4r)2Pg(=`(F>NzJkQRf-ywJ5552Zr`Yw-<zrbYatFxxBka<?txsrc8>HxD?>DOu_^9MKCe^vT3Pr@Jh55`mB5BQ#)*U0?lwPc?7_SMku5zDo*{n;O~z4heg@WW<HU$qXslK;Nc>&4?_`}bvKzt#;$%lt~+I?`7UKa=B+&%G^u-Gi?2(%043^s9FZg<t9%>JYt3w%2d^4*x*%CE4%8`N-d=|0daQvoze-**9pPaz^^<rD}3K@x4ZBe5L;t)IWPL{A(7QrQfP1#<_44^0)Z`|DQh6w?6Y2e$NqGWd6Z-WWT}lRoqv|o-J5ck5K=j^U!{7)K=-6Kf^eOUPt@KC*kW%<$cAMyL>gpPxG&zFNQZboMUJB5knMH%$30*`Tps%FvTCE{_p?k^DvkHtAG0J?&A3W`%j;*nkdROLu62Ik~7G6s5i)W$hWDf<lE$Q>IHH-`65HGo_dBX^dwnNK1DrFK1Du3JxxAAPNAM7r;yK6FOkoauTZa&uaMKI8RRtbE$SWeEpit1HaUx&NlhnblCM)QlCP65GX$Td>dAWEzu;AdHM2q-W7N6idE^M{IC2EppW2b^PxhcTBYTh=Q(ei8$xW$l<fde?7rIfKQ{Bi8)VfqRa$Rygsw=r3*^%0e>`2y8JCb$eG1PJ7G31%lx#XGTNa_l5BzXx#@Mh{Nvd}H$&E$jB!{meH3)D;G3*=0O;B1EA`wYPs8G;W{50ekGze5bc+ZcjlsjJ9B=aFN{Q4GP8s1anL{^UvIAco*JR1dPy#^g3+PljMGYE!b%mSit-Cx+nuO5S=B+?U#p+Kt?f>`QG<Hm*5ehG2Jw;L;4irKokurO4*gdSr95CDoB^Nw%Zv$U?`E?Z~aEGs&&VgBgOusFCC_ayWGfIh;I^A$SvYGg;_C@+R_r>IL$Catbw*oI*av5S&WQCa03qsrSk0<ZBGUSq#BX8G<vY7s)~oku%7r7=m|Ew~>X$l6R5g8G;v6qsT%hkr$JvGXxK(29bx8dsEwxg?f^ElY1}(_o8}{g?1wMB8M;phf@2Kjq5&?A$SNwa05e>qn2R^wx{+b3vEZXC)Z>M_M!Tcg}Re{$c-3+D^W|6E0K+V1e;Jxkxj@2sOIDX<dRfNa!Il^)s8H*HQAb6i#nKGi`;}ExFI!++>mTb4JX@@Yf~qZYm@6U1W%)GA`9J5o<^QcO(D-FFQ6VH3r!_2ATOk*lNXW~F$6E8ULy<5A`4wl78*caM()B8T$O4?7Fv!hv<$f_xhU11EVL%MD7gmJhb*)axdyo!wGz1+*_5h~#h*fCQ*tqCeR46fGj$qy8td-N5Zr>gfV_b9ZNU)Sin@s0irkjEjJ%9>Y)h?5ZcDC6ElRFPE<&wAuEF~+!Vp}LYDzZceHLU0E=zSLJM$jOQd^PBk}FW#lG}1j6{tnXMc79L*1vGRdJC;hEv)425y7_9;!57065NnlS;^ajf{puBu-LoS)RNT7O5T|uxB#`dl6Qs(HlY?K7v{JHTN?h)+7J~DQHolcYE3RpE<v>+mmvRApq0rY1b?HJCyNmLj#`W?Lhvo>zY17{;1kqm<P+pX>Q!<gc`HM3k|9o0Z&R<5Z<GI`J|q7{E?@%vmt25jD@zq)Ez1yWMJ-RZBG;l;Cf6c6P;JN#WIL)gS*RuXoT1+XhB(d;yqmg%yqmm%x{|zsJd3K5XOYKKN07&pM^XdHBgsRle&nI#vDEJ5vE&I1!NG>;N9{`OPVP$XO!XsoCikQUl6#VeQAd!6k!Mg<@(l7)>Pqrb@^<PD@^<oG>H+dz@)_zm@)`17L%gCspq?W?Am5}OCx4<oq#h?fB%h`3CZ8qmp>7~=;Jof(2wp=SPhLZw&k#I^I+8qx98DccjwY|BjwP=qCr~Gl6Uh4vagsWfI)N-Sm^_s{TFF~0qZxunDR|!#8cOY_<h>IL4xx5c^4=!}_o8-I^4>WG_n`Jv^4?bk_ofb0^4@6$52wyh^4^C9Pp2+b^4^~XFQ#r+^4_rp$5ZzzdGF_fcTvwMdGGLoPf_nGdGG&%GnBkFXZ(yHSbUzyqW(dBMgD{QmimDFmYhqyNj9$0T!vs%o`I%3BZUgzcxDRzi)|k&d1tKP+tjm4-kB`;G<6SI=o<2AauRhuIf-mM{{<&f=O}s42*D?)(MsMkMer@^Y9;R(B={XQLCJe&3I0air{q231piX<*1GYTD7XZlr$X=XTKM-Ef+tg_l7)^YPbLqbjv@~r4^;B@#z1NV@<4JOCGRs*9fn{tsukIcT!k7yu0rlWT~F>nUQ5j)3;lz<mi&nNmi&nPnVL%$D%R6yUJEX1lDFncQmx1($>pfE$mPgYsSf0-<VsXKawW1k)sk$<cO!F#V6%MhPi73kCJe#<DA3a6(wzT)7=mM{lgTk;C+YyQ6WNA3kUWrcX~Pg)f@(%CLAIb)AzP5!Q#+8`lh;w#lGk$1)-eSCP5n$3D(2&FYB{n9!9S=~$sz<7rdNqvm|TczPBv$)3o!)$RG=ng5rW?+2*H=BqVAVj{}}RR@*t`cc@Vig)rM@tnwDn>u1>WeS10$OwkP)?$5Gdj*Re)%48cdKKgdVP&#9tDg0Iv2Ko$N6Y9X=+!GBUkjs9c^PNTjdr;&G3FOx5`E;|{5U8v>B<$3=u48h*iK4fq56lxqfj`ul*Avl@(oNT=3WQO4L)DPqjytnfV!AGcR<Rj$e)Scv=9QSgnH+eaEBXtUS3dgaLdY*iqeF&a!sCgShv@-$E<8^C8L>giN*^AdB4dHBv2INt^b~nTbLkuT3<+aGAWBztzPpSvmliZxznB1J~Mr}lPBRf&+k)6o)9D_Z_VNbs)@1+^<$BW#A>Pl`xcA?fKyO8TsYm@7fZK>7Cw&WVr2IK~;nP4A7)HFmLL$oqP6<%*JL{~#>G=#q)x*MVkwHvvkAvzhtkL~^VGk)~DQoE45@MpU+x-tJo@+N9`ve3=sCY&1`*@f4}zSkR~0>|Id5Wduo?6*Dd!=K!NA-Ex<J?l`1>_hED?!<h?n)$G1KJ;5rTasIHJgqps&Kz%Nj?a(Uku27sSaV|-f(KLG$b-p2R3~x}xwj#DQSGTtWbq|OK|@?o5Q1+|i<3nN&N1jq1zLvJ!Y{)R+>9aEm0FPOO0G*)$aTrJ8G@@b1plW%#rXc?IQ3+)p2a>Adroi-UVkzC-FriPWC(sueL;Rre!>v^m?5|V*N@;T)c0f&f@@O0kZZE<I$S?Ozw=u7-x-3xQa_Tvl3y}Dveq9t)*Qxb&dF<z+c-y0^3_J@9qJSE6W*I(u~)<y;lU8xm}*P5WnBe}eb?3mdrxQ#xii;s3+hC&XyeUxLYI>L`FGvP-n<q+<H&rD+yh1ye-}=jNFL5L?M^kGui`uxduBd$3|XA97Wvkv1=s9LuH~;(3zNLLu;AQ@adzNX7w}$MQ@zQp$<?SG$Q`&2s!>J0YE%pQdd`Vh&*J&jfcF?qc4P=HLak1&&izq@dWS4Ra8dqjQP$L#+>&css8|y%=|ASr+~Hag&r0!3(ovh_WAS&9)Olp_JQL565!6xnSo~cLYCZCFLxdP&3PW%(btpNQJcK%)JcK-sI)glptWu-NDtVzHR#8_{qsdW*7;T8f48ft)3FJ`nB<d{kB=T(P67p>FGU^KQGV*fjTC&hJWHHWzhB!oC$?GJxSxY{^>m;^4Ks`tn_qEp$d&rA<y^nJ+g}k5F``C6rbuW3HA+{PKmiIfGb25}Xp1O>@jB_CPh#|J{=LH|;bu7Kr)Gg!?)_N#)5_zg2!VEE)A$Tlx5P2+l07GzJhT#6}qd)uaPd}C#Mvf(~qfRBSBgYvco;s5{l{}T>n@OEZjxfY9L-b(??n&)O?nw?XL=S2pwI4Z<Y`m|2yw`rrWxV%ctj93+ZLCj3zHteiMvWj(BM+qZA&c<@b1XuKkcEyT2atPG)qMA*GMCVW<b}*FSgaSZZlbBn$)e5)hS*Nt&Uy>oMvfyJ=Sc8YhTtO%!AGgv$w$e@s0n1D$z-ul#U4&%2;Oai^I?Yx&I6%4$wGILCy-}RcawKBkKj3+%SDFp>tJGPUf}=qpGM95BkHJV{zIw%>rZO`Sz-R4{AtMb`yUzlbtoi%_hoAMpZIdxLi~0?`5y|)X;A'

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
