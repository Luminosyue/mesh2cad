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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_002.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_002.stl', 'source_sha256': '1fb41486f8dedf0f2a507ca8c35267df13d30209886a483e0c623a4348520223', 'input_faces': 953, 'input_vertices': 552, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.005866240710020065, -0.13797356188297272, -0.27157318592071533], [0.12069343030452728, -0.07150401920080185, 0.2426631897687912]]}
GEOMETRY_BASE85 = 'c$}r333N@@+y74xLZgD1ha8kpDk|pj7)nt?jYV;TC^f|pR7tOyikTpW9D*Q7B8fzT9EmAn9$I5vQ`;zQqZF;`d-s06``SCrf35#|U%&ON@8^DP`|SPfXYX_FNxFVLy5uk5t<j$<T8;a2IvEW#jfJP?txXA>IC<2tz)5w-1%2hFd2yfp5xS~dpRPUnyJ=IjuYHFHP8v4Rx0&wSVnh?)I=b(O@e?Oc3>Y_L{KVmb%<m8|W>TQjpENQcDA4)2X2XW{>*)Tq>gY4||K*<|Yz+Q|rnP26x>Y7A&8hb9Zy)0t^mw-HYg?;jaJ^i0A@i+yT0Hw~#HLgG8*R96E8T6s;(su05%V1*3h?$;nx*)9XvBWm*FJf+NV)EW(I<HO;AP)(KPiQ-d;SRZW9?YXuRF%$5O4o$isBmwD;(hcm-D>9{Q?o8^7yrk2%4AYkx+U3w)idFw|{bAi9CL-V~pa9@w@zm%a+RHw7*KG{`bGXjQ9WIQ{LXJm`LM1wP2Y%e*4B_8H(SsHXpye?E*f2tMaDh%J}D>I?n%o>z?KE_=T^f7G5Eb-zc7>_+tFRx6*5_kjH7ClFi3sb?>)Ao|iRq7jJKjOjx0e|J8cM*Bg5B@f$Upp67obpS4o%-xxcZuG_E48hPFI<E_&9I9C=Aljp0CE|MYpV!qZuPa5a?dSUW>?QvBopOuU-dHh-pf9@Mwx`)Z**B5tC{eSDz_`96o`8Vo@gvogm{Tut2gvs-=QtULIZa3E{`ApqH>oug@dL?f+Z!5mm+k@)1(Tj83zh85`l7AzI^87`U^~(M_rk#*|*ZzWU59+sG&ZnbDS;ZIm6uz;mUbwO!<L+}`dp%+U^X)ZblKJOrqvH5=mM4(^Xl)AbH>)<)WB6t68{6#MH+!D3c>B6lHuCoK2J+8_`{Xn}|L&VMDtQz8XvLaM{O?!WX<h!F8_WNGUBV_gpVo|p8M1Fw_M?5&b35&${lzyc`}E~BTE|w#W@R1!Z9?_=(U8q@p0&WyI1iU>mgi+;-9F0uyRm1poPSq)+ad1T-}g%8?JK&)$-eox(Lw&Xb;VfOch$LLAl23Vtj+Q|8o&3a@sIzD`d?fvh4w?wc*U>b$JfhtHk$UIy-5Tge;dz(l>hH6*|&;cN|t?l#qAMF-CiGbT=w<SUbHSB2lM@|ZB0=6x1N7*$-dU~NphZkn8xePv2@Ko{`b2sN671<bso>pPb2PWgq(jZWMi7_Ym*A_@z};B@jM$5UZ%3{Ge+_8>j7oCueCgvs*I<a&V8#-Z9ZSyoYhq44}H0>AHB`n+aE_!osMcu{ruC1`?g}+;$`2J&mXVz{%ub>m~vg&eS(k6zU!QUuTAW0%KJs{Tkk0EH)*Wm+gmR_#OL{Dt|`}#5kH&eYlWIh{Rn^dYExb>^X1y3vM<Ije5>F#>i_(V!!)m{eE-_s%~1L=IxOYwg)i1!_{N3Prd(Ir!Y_`=z7g)j*U@pNA>Y4_-Z!Y9t?9~jt<v|X{bnCtKZb8UUO#4dj<UYys<||;yB=HQd1>h(s^29$k$=|Rc>eTAuPsVFC-_*h?^@sORTSS<Z)*ejyv%H0?mK>c#``yt>&5W=jBTv;-><eM`>y>We81MzUYyVFN&LR)2=2Q@sjCA4$7J7CSMaUIgQ=f8K}VH*!WVfnerZD24GHGHdA-6BW!>Ss@_D!wZ*LaawneT(?Zgmz{y7u9MXp2P8znMmJlD$5eK6uOodciU;J&@QAJ3chr~{q<Pkgt^b*L3evH0g0Kkn=9ebxG$&{%12H@`W|^Oe+Xt6W#+uzkEAv-x1f*M17)?e+FEssE|fXgp5?`FLy>qPNQVv{zco`_cQPD!wu4_+i->`7~Rs;_V&RPAk4v`XX<y`MO2Q>n`r^T9ek1@_hAPLDbKy4%A-Ur}hQ#I<Zo_DeblF(nok+@{Nd;>(E~OIqhHgVtsS_#%I2ihsP&)9*kpSm40kX9v+o_QP0BH=Lbj1^`;m8PVrs)tK&J<Ul72rt4$52>pslpzU}Y&<WKLnmuqdeZG1dUYjfYMSB2{8iN`j%e{-A%oue^c+vM@s_h^dm%1@7bX-a#{%jHiftG53*L-ECRZM9Bv-)i1^o4j6*-=5I=Z;0O}ue-6V1MQblH@5SAA<lo>d46BeYTw%~*PHp#Q%m+mUFnk_E557F{YokQxX$_b_sD;ey<M&!+ly4*k2T?ya$W6V>BF)wu4^r*s`#$+{EsV#WM5p@dX%X6u6;dg4)4eA@3uqEgAwz2Dj!FZ7xx_-+S2`H!go|B@O3kQ*0*MB#W&i8((~BaCHrLGRfpN@X?`vA9deymDG}tq@umLfJf!n;<T^Tc+qEXY%@e-9wt9Mk>}%n7`E~V-C-I8kJDbk=mV@cOU9jU0xvs21(MM(9b-#dbogb@=-=QVZ`Lr@v=_j}En(u@Dl-Fya%6!cdy~+2@Q2NnqofTh<NBGw7*-HQRy$029e2&@=?j!c#SKK%A_oQ>?@+exbA|0dT{ce9+lh*4@w<x)P&3Z%qTp1fBk6-vk`FY$I=ec?IH1&TgG)mr&#ur8C{Cp4{rR?ii?WpX#&H>^3-&4o4B_HMadA8Dz%TLN7|5hU!&&mXTjv3!J-YJjAx{^cZ#@5w4<$a+ym`wYz#x}*bGRyOG-kMi-m%Javeah;nbKg-khw>b7ljqZ3xaKZ-U)$e=^Y+4b-KSn$;rr28+E{6?H9SkcZRRd{znks%({*>OR(xyc=EJft=Bp1YLUsNmn)~8>aQt+b_al5Gu>w6`<=;l@7!$us&V%;t9QwXFAyw(eXt$W|v(HZ}*ENRrIKwq9hvw^kiS935L-_NX;TXGH$%E)WaOQ5guEh6NtH!+DN`BDZDqJ{P&V#F;D}LO!A8$tAkNz3K>%r>RI$9pTXm8jCb6-5iI%Yhl@0$<DQa?B+ZDpI#c^(xUE!UyLdjOxWHF9ROT(`ovKMqy;F*3sW`K%?y=h=_&#l8@}G3!ROlIOuaviNluy^5Cism=X!y6$<eJ@R;jZ>%g!{>w)EoOetQrumkx$$fozHudvhAw7p)^CKVUzpc<bI&VL3&3*fdxl~t~ZahE6*1pufsVAMoA^qt2;peg3HwT9DeW-8CI?cziJ6IW~-J{~!G|AUrl%(&c_+DvbT-qbg*V<q3tnAzO`EcJ+|A$!Fw}Lv*_pIorREP6!aNqIASxXsD;YZ4N%!~PGJXtw3{$l=go}8~8FZ-_Nw_}l6vhT`&F5leUDp}665mt7u($5z$S+ehX4uo&r^y9wO%#WTcMwdLp=fAn}UU^-ttZ;sg*=?=&%6YRFN#*_6t9GRJCwm>0^I+`gyH_5+e#@fq_|N0MUUoTs->f&7-ot#gk=j@Ar}4ZKlF9p>l}i3tx<6T4f28xrJ!`MLFSOAMX#ZaG+Nab>l?s`8`DUZ(G~ca__sQ2a%eBbN%h&4;<n6WSzWd~LH;Y%w%+nYB?+@m_y?ZpBtN5O41ka@Q{X0{=y=l$!ro9T?C(qY-@Pg-GOI=OlFFKm%*|DihW}g18E;P=W8>ycezI0C7hw$(9!Z(+sQ$2KPPVZZ~-{ZcPHi*6#{Lv<hkGpEk7`|Tf0{MP7`zK`5`Zgwi=qMWhop!YD?{|!m*WIY{6|aBoNw*leezbA}XkYB>OZ~V9)A`V^6u++UwQJXD-+i5B$-e8H?Aw$22^!3O`$%7UPWv{K>Le+c`;HkM=)BsonD?(WpGW=gY@4R!Cv7$P_xe-&&5LQiC*zgz*bZh`vakO$S@G?q9;tZ<38nhKmZRiBKQveIZJj(R57*MDf6*TMS8ozb?ZaOw<FS7DjP6J9UH66fK&8DaZ}7E!TC9>c(N9V5SUGRH_Ys~q{eTbm#r;%#AF)mIjg`k^Z#O1Q_C<b#Z;xmjE6>+B`8Bn-ccAg${4q-PPv_$f=uG{5*_p4GEhvEAQ!NZs#$(l4#`|%M8b$rjo}uiQ+`c%k{?i`&NceB}b@Hjae7*P`rM)<39CP-a%G1yIS!plM8Asn|r}FY`Ia_I8pPvyc?`zwIQWw+m@U<a5`TJp`!E(xHr`oi>vv*Tn4UDGtIA`=2cb;eS%>l|Y-n*L3l6l^&VW*XTw6BlTb5#3tvC2N0<i^L7+qV^&$;V?B{EqUl--q^>yARL5@a<ha={<1qH{7@Xbe+bt^)8(=1@7?i=*6DL%Jr<hs>II$N1PTX?=RcwYIJ|^<H>#FqbIcQir%5~?PZxbxo-8TdydM!*cayf-Sm7i!<YK0kwg8*?9P&XF&@jSIbC;9ZSL!JdeZlYsWIne-*tb_e~a%&vz4DR9!K%@{JO#y`$+h9AOARcUs!b>(a&ME#@rY0d(8&rD4+0M?;ERL<JYyNw~CYZqdjCXz4wl6tMsE6@!|6|eS5~q`_55#I&bedJ&5MjH6PuVajsgSft1fiIca(MuIHsQ>2xj?52p4w2kbYd();!`bGe`UKKLIW`&VzWJWj4#V`E1?PTOB=)%7|*o1SksMJoAm`5{qp@_rZh{r~v5?+f4c-12^1dVi8HDNf$kuIG(hzIfg+zc@|v%Jn>x+ZWe$oVl&kkG=Bmhh<;Xv;E&c=zHJZyGkB(Yc8L!9+a*0BfifHU(})SwfZ^Ax|>PKbU)4I+l@ks?>hf4H9bOke5urle)0gF^SOMhi3k0>`08t=4y}~WX`ItM_RIMc&y%*-W%kSUpfx?q+Z(qlQ2SiZ!^ROG?wduT`S=|z*Yfk(-qw%$$@Sc;uL#^P*MsYM_|As?$~wZg&yFJh<49`1_nou+-+yvWxvqYE-bvoi%a`2O7oVVWb@38D9z!b|&*!)5A>CiX7c0KLJ6-Y3bRX_pPwF0(uWO&{8!uni{B#ZFt%F~@oHy&<U^*W>8gpO!{?ns!|BlcO+;<F%rg83GM1Hq!@$z~(>a95{`+Cv7RL^Cb^K;Vj>KiZDkG}rag}i***<(t3*EzH0=7qd`+rCpudvTw#K5u_9PanT0;JPmEv-ZgW7xVJ1(y2;&QRjNtPCj4#X@8n8&TadoD!d>4@}PKm-`UD1Q+xQX=S=vH;899@E$FP`yY~AxS#<v@7aT9wkGVFB*OhHZs8T<+&Q}#*)Q|A($0BIHINuzj>hk9Y`}Rn+9$x=I{mhS|bx&(R{-MIW-mH&flsYlbJ>c!FTJg#_9XH$2xmP4fsYCJo$g%W<GJdm3lT6tc;}^d5;U($^_ZMyDB0he-<ahDPe)NpU%FB0jopz4T^XhGNzT4iX>xMm4>;Lk5^xRV6xl;euqcHk;kliCet`oc4WcuD+plpJ&zBfKod{Ga=w?@@YkoUDMDKjfCUtiUokKgR<r}S?xR{x0XyXptN?aqt@Isc9e4tk!Py^#8kX+(LbUWxi|znuJY^=Ul4{-o!wpEe}O^&@^hXnqi%An#Lg{^$0^`EP$WiTcTP-^uNZ`;PF%_;t^6^z*ylQpo>lnQ|Ulap~N5G?=gWdY^L%RF8B{+U~j0`J8e$L0(_S&;MAm?>e7L%uw2kI@iA$r~2aD7VS4YOpxnMU$8{+UG>&!4f*L>qEhEquF-Q;WPwDv-mKm3be>07OO)$DA6r!MMZF2%4E0S^=DVOU{hX_wf1<K4?hnnBeKAhG>Ok5rUX2sw{OBVmD!%J}_js1-BR`_O72h^dt`paD=IRcKay@Ha<>*|U(m7FHM|0idOxe%<94ma+endZ7zix?2{fPHPxqMs2BWGn_<lnKwo$}VCXQEthX5~R=^73uXQ|NweOi;%Y{coD=yUqvrwkpBo<36kJ*hSw*?$02<OE>!co)$k--hSDj^lub;M&JA3i+l>-czvDP=lVXF+ZW#l^%L3w-k<m$x}+1`zk2$SpX+;WZeM)Qb@=-qQ0giwlkOwWn;nqr(7c+#eMj@22jqIQ)lXJ@*ZmH@erFK*;(OeJ!So!vCGdb;pXRbXbibQDN|~2-@Nk;!yY}gx!t_0&dayE1$IN2%+%-B>8K+sVoZ`FgYw+!Hk;-`V`&DVbOp4~dVK$-uS1mgy`{I1Cm77NS?;UeMu3N|S;%D;m%{%VrWZzY{152IB%h!L)ue5jFj~=wk%FB0*xT>^w-ItFQ%F4^Pg%vx`|9$Bs>Ie57{lo(Lp5E$`l7I8UaQ<AXrQcQS1imfu;Q^(daSj+Aa_G9^{IAuYo{LUvN%DH>j-jVy-*sLI|B_FVQa``h=s9_{Z<4$&;{CQ`X6Gd3x;wt4^D5tfBxPS<oOaJwYWolR)ARoX&tzr2aL(lRUFVFyce1?h;(W{Pi}TI87NPVb?we+Kl-dt`TZc=@N_`fr!q?sAafAEfxx#$!HLbhe_@G=T;yEX`FP?MkVG9o`^@HcS+`f3OGpZ#Wl*gklEk@^d)Cum}+O;Qt(XVvhY3`lEuRk$F@wHQJQ<U+D?^$tyN_%nNvBDRo$o<>0-1GMPUZtNG_$F~*ue?jWF8tizD>aW)^}0{>%)ESu&msDL+W0wLcbJ{7TV@maWnZcN;5~-%g<q;N9^Bt^`?lX_Q9nI;a^L(UQqAXs2*tMrt;o|iw{)R?diOjek5kY3k^F{z56RaR?`?AXHm@T}dsiMdWSz>(w@oRYCHt;=NZ)ZPFW=Uq5uHD!2OLu7h5eh`*T+meE&HzV;Qg@G(HqapQRIKKEHf|PT-o)s;^)q1F5i{UTLFqM*2R7}Q0ZUzhJO;hXX-VZ`uB*S@q4EpR@S9RE4uE`oWpt5VQyd4p%LeMB(Ht(A0PX|2=9DEzOMPz?^Ner8;|6*PpyoHN<ZB1q5RiJ?sInM)cHWuSQOU0wGjc*e|p4B_D5*m|LM`F2LE6G=~2^${{Pqi^yoL|7|Ob7+V9ZvU>1xYLo0w;Fn;3H=Nf4#d}e+r1miZ)Prz-!pF%$ee+q62Z4GV;eivE<{4V&BM*2V_X2JM2^n37a@N>lX7&p`Jz)!%Bp*OU*^Syz5Fukt5%@5<>pl86pfp0qF59lrE88Fiy!Ka<$KkJO2p}&ED24_LffwRCfq2GXKf*V5pzzxC05sclPQ4MN9{lErzD)bxhRPYJtIq(VaW$16<%ixpHv*459SqR1<(9_@$@C*dwZ3xDPp+AEUgSSJoz*)%4b_C<E5R7fmhF}}GGqgCkGk6GsaRaD3xB<AXl;64t#_bV|hawnvfg0d0;9=0I;9=me5sV|DC%`9=_ecce6zEBC3V17Y7I-UoI>t5~<DCw_Jv2m`O9<u{f^`z}oq>D|flh<Y0MEc$GH&YJ1C5>WC3F<{OYo-%#yy<T89E#~3OpR#5ZV~r5bT3sTp8LFTp3)|85N-|p-sUp!9mb3!9n0Y&`-gA!0#g%*Mjx{*8<m+=2jEI*cZWgCW7%w=y32#@JMJw@JMh4s1LXT*bTw>U1(+SyI@afRj?<xsFbgw2*&KcWqk))30e_c3ETqO65Ikj9vTE55AF@^1MUs34SgS68(b2>xCFEoxCFQqv?jO|*c<8#_6C=6MnPyDs4v(TYf}foxGi)gxGi`fg0VkzB-kIULo0xFuou(~>;?8fFxH^&YH$BAE(G-i7XlZ676lgoyF-hB-NE^^w`-ga!8pG&ia|?5-vO5fSA$jpR|9_tZ2|re+z~n++!5Re+8f*m{2sJ6_&soWXi0E+a4|$ljF)K%aDH$;XenvFrH~J%-co+Nkw2zoq<oe^zC{g*{1?RfctFcS3xdmnt3&I6nYIPbb;dkr?1b(D?*u194}z1y`w)y{oDm02g&qW_f}^3kz|r7Y(0Sll;JygP1E6!k1Hk<ejGG`Be}iD01l<Wv0-uB?gHM7FL-&CXgI6FJFM-B@mw=Z_xmb!|yv!NPp|Q|7a4a|lnhH(<?}kQ$cY|j`XMtyf`$7AH`+?ga7#q+5U<3RSv_JSGaC>MIaC@*Hg7FXp<N45U!1KY8&?ImY@*as`oQPn&7kU`H7aR&*0S*O^K`{Opx&-_&cm#AQcm((h=rZsZ;Gxp`4Mi{>=8SRB#n9#8#o#^ASnwWj0yG7j0Nx7S4c-b~0G$n90JcH<fo<UK&^F-i;BkmH7%x);JPbS(`jIr>kB|?h?WO#*NB)@lN%{0czQ;hjK>ff>hk(PJvBnw4p%(Z!_#*Ti_#*fOGy{AByaB;D9KrY+g7GWpIq)m+Rj38N3SI?W16~F0iD3LSGz|PTc#1P7LDxdVz-z&$pvS?dz?Y#H!I!~V&=cS+@J8qc@J4Vjg7H*nICv^}hBJCWH$%h0;mF-)1mj}}#uuQkz!$*j(5v99$Xz;u@oEI)ub@4_Ux7y>7}tY-4Xy_s3!MTU3mzn`!5{?V&zvzC8UmdJ4gs%&t_80HAAz0%9|50+UIw2Ar$Mv8Y2Z!Jjo?jSJ2V(<2Tw)>W4yswzt0d;F~6x;KQZ4K$cI>Ck)K}3-)QJ`XfN<|@OtQGFw<k;D$WO*YR;$u^##`eSB1U@t_m&*Ed?$KE(FaFE(HG9je_wTr@BEspv?C`FfIly1uh2mfxZX!0au6mf~$jdXf?17E{kC74Xpz92A4oEE{9-T8CnBe8C)J(6<ig0DUV=W9KrY<Xd&=B-~v#VuLAhYxJW(<#s#5ozy*=Vd{Tb%As81%FfNK<><RS%dxGDE76ZQvE`wlP5$Xf>LEbAO7*~So;7Z^M(6ZnP;L;ddX^git{K8OgX)fNFpEuS?%(n#cQ3UD*EdefpwPgItnXA9q7p8oq?)fy=gFfTG;JtPuX2JL#^a1!Dcms45cmsF>g7Fw<EQUrvSAiqIH=z%}H^DEUufZ?C|3KMT|G{U*FQII1FA<C%A{gI?z5?F|-$gL~1Ht%DD9h2G_{{hjl;!9da&-^<4EzIvu?5`#w!l%)3E(Jj8iH{+bPPBgyi&^VN(5sQ!8jekcqcRhyc3)Oy$Q|$I}nVYLSKMiAn#8RjGseaf}ewPpbx=0;5!)G9gO!5d=q+Kn#+C6?>^Q^%=a$xkp{gDy$imJwPbwV8P}Zg3-l5A7w{$MMerr?UT8FUFL)t>@d5<nu?WVy5R9{-7s1)!-=UAdzk`2;UIYIMK7?SL1icPU0v~inGV})YI`{_oG4vPkWAGK|CGZvS9_U{19`JnVLhyX>I0WM$=mKyMcsz70cszI{g7LQq#`~bV!27@#pxNMT<naQ6@lOcG-$Q=|e-BQC9s(zVS0fltgeHL}f|o%Lf|r4pOY5;5!FY)?)<6$HlfehT-$8GHzXSgWeGL8)d>(oQd>$MF-2;vRheGFrL&3q&ao}L^8pJq^cO2Go2_gvd3&L88`Hn|E#$#PYenujHtD%#jBf%rF_KfY$nC*;?2*z!l(GEHXIvYF(9FJhUA8H5h2ge~8uRt)a3hfB43cjmRFfIeHEw~K0q%^*g2*%#dC<<)>Z3k`vo(r7=o(nz#jRzkApF%J`4&4tv4n78r10Mq)b;c9uEodA#4!O96V0;F_coDQJcoFzRD9h1@_{{hvyKTCWKE>y|V5Tg0Pw|;?738xdxC+<@>J9b*>r#Go1mkkfs0b|vEeb9MZV7DxZV8?ToeQ1^PK6!;r-Cz~r@)!uO$f#tp~t}+!Rw*N!0W;5phv;$z-y)TTZ>>Ei(tG3!T2il7Wfv{@+yMyZUo~g&_&=W;7-sF!5?BxJK;0q%5D^l-*bDr_U|DW4@WTWgJ9eh%Icsiv<m#LsDl8g4>$lk2&#hzfd@m&fd_*JxV^290SLweoiPIH53LCH2iJoZ1J?uhfVKqp08fI>15W~PhNglygLgnP!8^c9p_{-<!6OixFkYq`!2`hqpzEdiu17wYu9Nb!4*6rcR?6pE<eO=%l>b<1jbgE$Ot*lCL&Kn3z+vD7=v6S&-QaG{8ffK=?a&=y2lN-{4)CwgDCiFG4*Yw@SD*n1#;u{Pz^%b`q20iB!Cj%-!Ck@I5RC6gW4(i5%zl97!1x%8af=^VGA`&w!T3)E<A=~Fu$a$71mpA2Ofb`U@Okhd=(pfQ;6>1B;6>nx&;am6a3^SMa3^qm1mh2&b-~S@(aafJpeA@Q^b&&c&j`jpK~3-v&<LmrHqmbcg7GJaW*A2^j6<wxbBs-lPmG^&2j~{C7;6Uv<3Q*HFw=$LK=2&se()Ud0q9Zi0q|MqCGc7BJ?PKidtgx~j79x0)}TLuMeansF}?#YLVH`Qj72>&?h5?`{0VZ$xQa81JEH-#FqmmMFw+{~&!O$0HNZWc<LTgxX3)}LrtJ5Pnn7=Y-@)Jih|kPt%zh7q{mw@ubUOHJsQ8@|#^U!<7!QSt-xFcKOT&I|W;?VqnCTEO(`n$t&~4CZU|pl1XZu4vz)Z`6nN|l6gtmoN2eY3&v7a+VLPNn!$AFo30ndjHfp!72ciQazbvkr3nCWyd)AisB&|}c`;7WM6RS{YmTm~xMtyPrXzg5ILu!_?Au;O?>SRPscTmbL6%0s=tm7(RJUf^!dT=#OuDCn2q?$F-QFTwqxqoH4dzr??1`~@@+!T2+1FYssJn$T|Gn&9ftQQ+#}8VJU|(pY^FjB7!AgT=UOAsE+2F#Z6+xF2*hSj?v%f^l<bD=<?}aC2}WXkl<6up6`q*bQ7C8VIfr?hE}4+!tI2!T5b>P4HjNI(y@c`_OFg3uq34@!tr>|3b6D1>8uV;d3@P8~r{*FwXBr!MG;$FYWD`GJangpBO*m*JyhmEXMj8!MKDQsfQae(?;MD;E$k<!5@J?hI)ZN23LZzTvWnm#{VEce}n%4i#lN}>W6VH=)Yi*J5g^1P@7CyzC^7u7WK@yIy67(JwI~Cn7t=t?*yMh?|>ap@lKMlcyGx#9V*@<vUjcQz3MY)6qsomnCWfspU^*`x54Zk5qlqW0h$PAx*E)MGI$^KTj*pk`|iWO=X8P&2Qv)=Gfe<bfwJe_9$nn>dFTIs{og#i{lnf(Xv+WTL+*d6{))EzFGHMtxqe~0M;CYgJ39HC|6>m<4+Gez{{gqLXIl'

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
