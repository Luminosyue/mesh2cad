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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_000.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_000.stl', 'source_sha256': '813ff8eb9f58447853a957187eb42f747b443cc76c96a96e3a25abf805bc36a1', 'input_faces': 1420, 'input_vertices': 805, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2936045527458191, -0.29368218779563904, -0.20253430306911469], [0.29061582684516907, 0.33265966176986694, 0.1892269253730774]]}
GEOMETRY_BASE85 = 'c$}r22ecDK*uQfxMSAZ7hK^DMr3oStq$q-j0wN%xcceE3LX{%D7a??|NC%OU2q-9s6boXzHl$e)l%mL&cjuYC_r9C|Isfy0ob#UN$&WCZ?9NUmWOti2PLno|&-^Lodu-vT`ZpW<d{S9_d3-~<3>eg-Q<s4i`}P~2;LG9U^2c&c(-uvdwNCI2@x4-}bC-dg29&AkFY{>E8fD7+%XEEtz@Pyg`nG?0K<6%!H|WrNV3$}vuzQDoU1E>R)~Hmqy#L|*%lk+A|CfI<#kvsf`O)c!^rcn3({+TwJeMDfAyDI>lLu<mH~A-{`$gj9fr$h93H>=EP98m<<BaqC=W{vj1dF}n<e~Z|4;^dXD-tiiGpUy_Y5WG$pR`Xp?FSbPA03I4hnw{tEsR!MV_r8gyVFk6=prK`@$y<ZMmW#!xYV@s*W^=9KWpT3`k6F+j>!v8bMnyg8v`S8@<97b107bKWZK`-)NG#;YbQkF<k2z9Cphop&xz*!7R_qj?*~`MMB?PW=kAVio_}nd+0I4In7n%qr=OvsqfGlXPMLiB-(4bca{u?`yE^Z?#R$_*(|M-<d2f!5#L1(p(v5ST|HjKEfBl%#PS~Goa3o%SF706F^^0^c{lAgX$)mX{INL$zp+2RZ?GVk`*0i(tkCV>7-<RKvlYVVX{~vE@#?^+tlOu6*U#9Mpop#o>GVT0x$Z0=t`P!?IIC*H<`B$C4|L!@H|8UKD-O#?GLnCqW=*XNyo$bH0x#@p}Rc5;t$T1}nCl9SEGR5iF#abp`{GZcKpu@uxBXRQ3f$|fb?VPrz$?NVh+ilI=P$W+7tC-ap4@uutGkO1e%=_wS+ShqtziHq1+k+-=Fy3tElLegZ9RA?}vptVZH2rB)Zg?b49vIYMxU(G|H@R=nOJ=`}+iJFh%A+|V&UOg)DQ33k&R(B7ulrLrGj1R7o4m>nGv4O!njVRh`>t)C?zGdOsA<1a57SQ9Kify*<&E~Yciu;uBIf-Tnr7bD5346d;^fhK%O*M7vt~i_x)(Q@?Z4z3=Xlh)ujFNC`}=q1Gws~XX7+p0Yfk@l?i+o@>3`_KJf@xRJ39T0UK!pu5-)GpzOU1tI$6#3A79bwXD})A+(?`}I>u~&o%=2w7!fz$SkTOGDi3VhIwIcd`f{25=;_al40BWFp{LTOI^K0|kN5D^^d>*Oz_h>n;H*fTJUr^dS<c`0PHVPL@7B)t@gKf8C=w@6diCo;PQP;9I_30pZP(QEhRW@{;p>0X$wM<%raJC)?jCpF{o&++{!N_M4gWcLSR_s!-0<o!hnp^(O0_-9WnC1Bm!HeHDCP45BR_D)Pg1T@Gb8cxXt9~jcJ29#Y3Fc)Io|mk(YgH`3Hg3B?VKp#wBs+)d3GdD9yk-6?fknF=S(}p7MgaLS9Km`UbVSzb{(@{K0ZD?5+@IYBF=mgzIfJb=NxOyc9`(iyhxlpSat0@=ifCsZeF)~-_)P8Dz~4r{?Z?sc9QNoxm^!<a@GUkcJG^fTV<!8A@;8)XaD-n9yHsn!A!IL`Fzy5?<@297^=0)wDa#BGd@}W=se2$C(vq#d0#cBI_(6vna_8fNBMjY<k@bvbA!*#eDdYO=Ogj*rJbI4-tVcc=5=?MGW+Y0Ilgr6A8C#+e<hRqx__B!-uC2wnt40$>t>U0IcMhQ<5`{gC)#*(s`u-gWY&kF^>3TJ<z(jDoaS@t&YR}_{xs06_gDw&JjgoG&5NEfuiM<;DH11-M$>h2-dEK%ChvOGY=`b!dq(2rU(E06w3ltA*}ruQoA#N{bsl=j%;(|WE6n>EQ`3AdG-x>|5+{#lZa2r-ZZ{T~?RGt{X{WRKywiF3N%MJ^lxx0u-Or+?KW~2I^v9Fu-{SPge{!zL`{p+J;p}GJ_0(+B{-&X3e6r5hxsP>zbj)<q&i1WloSZh#*Lh%^d45v<Ddzpo8gAM-o7;T9C_Bz<=b77`<K5rx%KS*2JX-SFe248v)Bj86^OyCQ&I7E+0tZH!{*QUf?DutM`{+Et_6g@4o@#!Mp5L)J5+@HX*t*#1Z@*#YbyqAg^S>QGIzMa1PxwqPlUHA0@@E;JDi6G8#%JL79wt9H&E#h}u2t?|#&KP@v&q-aF#C6sS$74ev^M?Umgh6)eeF5kC=xHP*|Cwsw5`ncX?oLaXTC3Za=tG_-)mv^Z<S}w=hVFU&gYBHgHOzHK3@X2o;Cffo!NQaq~D$lM&jh5whsoK=l@sV<Y#Z2@jozE=SZA9^!<%ash*$3@3iA9Z04W97j;d(@?IzRf5rAxd0>gzp3!5qO&;<&<JKQG-v@Obeu?jcX=<8$U3T-jZ!I?OOXb0gA?JNXJ3L~xf1b;x|7-`HC$SxpZd9S2H0C%;o7cRr0S}q|@?Vl^XSdnEI*&fe{(Y;WX}@%W+5T^ue(F4A`}tWZlb8F;jN5Z&yXoA==Sv`Kag)FIhso!f?eE)^&g3}{n&Yd}NauLhc_`NibG&CZc_>X+Gv0bPan?niyzo=bx+tm7S0|mnZ~T<m{#&w`b#Ik}P9Ew$#LTxj_c-4RbRO!z&G}vsKEL;5+<8Fdb{+_Q7<Tf&=#ZIzYV>v18#)g*o$RbPd<zyjxv$Z9^SSVZ`TvK|@=oUYZ=Z15PpV(oSr_R%@OJ@cU6gcu>nG0Ncm2|=pZ7oKtgCe%?A^>+SBEpV{Uq-DQn`I!N#8Uy?d<r@JpWjuagjKApnP5P{{|WBn7rl>W?h$LzSsMzFa22Z;Fe=%{l5CjhmjO{fZYG&)<f~~Xu_p;Q|5m1r1|GJ#><1-H;hi1`^ZCo-&kEIUOx5uu9SJwX4(($d@o+^yLk0T$~;v3*HdxdSJ7-v9@Ke(6({25zU!rqIqj)Dv~R<axcS0Lhn@YW^5~2K2jk_wK|7;y^Y9>N`$l!%YSeb;eg8l5sM=qlmOMW(_5QNCe^KiF<+J(wYJZUjuBYB#p%x|&PD#DLY#vbi%V(c|!R)W#)+ryS9Ou3l+AN5~$pb|@E)e=lRX2HKv;F;Bwm9$C=3(;i4fB3&9wHBp{dr@`JZST6Z;nox2W<O$&HJ^vpFAnIdA~OIk^4&RdM{<3)YgoLfa+(IJgWK`CJ(EAhRB0EQui}Rp7d_&eg<s&s-J%Q{F15r8T#3bPu<S|x$dW%tA6^(!#h*=)8<jt&*)F&s-HI3{fzc8$BXV~h&)N}cXHpj)cp*Qhj*#{P99SI^x5a@{cc~EekRS#X8O5y@o}f!+Y67x%R}>P98H<~hNRo?v~w%<^KBmB`Qc{29Zz{&*#CFZx&8koPtN}%MRRUC>Wm*X|Jz*8|2ntxzs>dhuX8*9+g#88o}BsL=6e3uxt;%QuIGQZ|7!ksb2b0F{ZaG3+rFCr-CWK8HrMmN+rFCr-CWK8Zm#Bkok!LF((}L0?fmbyqvn5|+xg#ZN6r5_52*d6=l`TD`wzt%hc?&aQ0I0W+FXxAo!fC}b3G0{IpfggdK~K9jzgR4ap?A6jYBtA<IwGo8i#KCY8<+`8izL5<IrtijYBtA<Iv63IMjJm?JqqZ+~=$D5Z$?Cf4uQvbI-h_a(7-L_smNwcjqN?&%C5_J1>!Y<|UQ8^AfpdUb6ky^ODW=ykz^M=Ox>|o|kN{=OuE_yky(g^ODW=ykv7dFR47L_LpZ~vbml&Y&&Y41QM^m<NQ1IIjeK~IcszMIjeK`bGFz1?eWH;&Gk6cxgCc#*W*y<b{yJVk3&z+IJCJQhdQ_8(B^s^y8Tz<(9P92bo-;mq1(P1hi<OMq0RL;blX?s(9P92baOQhbskmwOOHc0SL4uaN6%N=7H^6-PHgU(uT<{NSLB}gO6Bf+MedoebZ+M>a?gCFa(BKW_smze|9ZZ%xt_0VfAoB1+t>4z&Gmdm?wPM_`+B~zxt_0VuIDS2N7erF%vUzo^ObE!uXE}iSQT%a*xa+uQMtR$A@{6vRPL^G$UW;Eo!fN|xo4fDa(A6W?pf#9{_Ay)&GkCR_D8RCZ2NkhV{^UEA@{6vZ2NkhV{^UEvAJI7s649nmmVi>uGc@d9W_oudoEl$5NDj&T#pl-+i_xZJx+9P$BE7LIPv6+6PxRCVskwn+<vO@;O1&PxUZ|mgWJ9u4{ol;gU$7LaNAeo!OhipaC0>tbRJdvMUMwJSL4BLNB{rWq64ey#2F7Z*W*Fwc0AZzj|ZLG@nCa39y~eY!RC5A=-kd5HrM0C?Y|l)Zm!0O+aEPf-1gNtadS0JY_7+N+rAnnZm!0Oo2zl6^QhWidYrhq8YgZ$dL5E+$)<SY#O9uLh|1k{2)Sn+qH=c~Lhf0I=-jSD$UW;2mAmT@a?d)%_Fu0<Y_8WKwm*6uV%yj25S#0D2)Sn+V%yj25S#0Dh|TpnMCDPnzdY*@o9lImZAY&|=I`GgZ=BfNvkp<YyAC1utV2}pu0zN@>kysWbqKj<9inn~9YXF|huHq>b%@RNI>h!zuS0D6dL3eOy$&JwtV3-3dL3eOy$-RtUWceWs`i&>9b$964zca%&z(_cc02u7->-FUzhB#2f4|nb{eJEHe#!oL<Iv`w-yc=({{Ber`TbGl?(dJ}p5GsJZhwCy_x%2-a`*Q~a?kINw*UI~N1N;4A8mj1?~k^9{rjWM_3w}5p5GsB`}+4so9o{nZLWWRRC!eGFVF9fHrKxo+IIAMIPd;L@y3bGJ?mkWyX#?c&w5zp?s}NqvmVyDT@RCc*25~d<HY8kb+YZhUMJgJuaj+m^g7wLuh+>o*Xv|*&pO$*uh+>o*Xv}P>vgiqqiTP7*2y;4>tx%G9w%is9gRCq$UWmk<?c8k_ly&jyW@o1Gfs4F#|gP-oT%I#C*+=SV*9VhiOuymvHj8G#I~=;iOuymA@__E+rAzrHrM0C=6al{JgWAWXPl_q{+{KwqkhlQx&1xMZAbl{rSpK=UwRydn~pl}Y#;TxsdM|eX><L#sdM|e8CX5dw4;9i)w%us*OT-6Z}4E*k5lFLybG1v^DaV9Fa0>~@kQ=AzEtiWU*w+SOXcqIMeaGibZ(C?a?kOla`*Tm_Z(lg|N8i{xjw#ZfAsNX+t<gJ&Gqp`?m50}`}+8@xjw#Zu8%L3N7erF9A7GTk1yMfKE71$9$&T{eSE1rp!S#N`%9s3PB?$B&S#5O{>9|#yf~fP^Wp-9Z=XnY9C6;A&h2@3(Qlsl#A!#J*QaxPUSHC>hs^7#^9FTp&l?Ob?`GbQI{z>@u%CIJI*(E3_B_VW%&8~iy)T`+@9W!H=KM}|9;VLid6<DA>rFfAd`^F!PtEhyd7+-1^Fn>CJ~Qp;^G;Q6&pQq0y=roG{;L1m>n2y{!Rp+e2kYN<$K>ifTb<kUY{MfG%>Gd4@#@^3#~bjaHTy}O4;;>%(QIFJUa`*YdBrx@=Pm2pp0^zMG>ggAdC@wz=S7FV%V~0T-nGu%^RCn9HMu(9Tj%zCZ#P%xdq)$BnOvP`u5<T1^N&iJaih*-*SS59-Ji9z*)Qrmc~5T7lb>DIY=3ngz9;8A{Lqz$O+VH7{DDP}m|R~MpmKX%fbVN_or%8gK<D<lgV3;sCRf)rcyg|5@D*xwD&9Pxb9Wy2po!T&>beY_+v_p{-J6=%Ro8v!++Oz)t<>DSuDY&7=k~gipue?gS6!bHoYKy;tFCj=xqF>U^A4u}>N*;o+v{jTXFJh<bv@3#T}-a7>+$6Fx}Fu?O#AA(A)VXnhJ1tjnfI%%OVYW$E-9F=zj<AC-ILDU>z-;4GXGv(SLMmMuF9W&n90?3UOKnedAYf|&P(U^I<KT{BhC9#*OvvKA7yfNJzDfHlk4l(!Zpn2pS}*xlXD%M@0`i?b#^+p*V!c%9?SkneI1`Cx7YEtA7@@qT_>n>d!1lXy$Pw_ue}aY=k_|pq%pJ2{#DmG>fB!E=<hn$w4<)0^yFMe8Lqg{<mx(2Pj2tq&|-;sU+Owgo!jd`!*kv=?da=FRc@~{4SoKWX-8f6s&jkYYtqp5X1}QGUUhD-dkwDNX11HU4p-;)I^3iIyUgpV>wI-?uk(%W+?{H^wbvbca;`hJxxVh$lXKm1;6lXY>N;qhyVpSvKVr7Cy3ShX_B!imp`)gs>N;+n+v~W4gU*=ORo98@++HUhTJpJhU3DG0&h2&Rfkt1OTwUj`bN9X$7r##ZdB^qpI=A1Wb#AZU_vC!P*15fY-}8KX-nH%z*YEpk{Ajk1x-Wqz=e`8t{Xd)ctL}TCb9>)|K)nm59d%y?o!k2=BxSy0+EMpy(7C;DL$v9y=JnKlAv`(vh44N6yLnx8-wB=D`%Xj$|6y`<|BC37x6Jd@eK2%x?}OpLY;t{{4V~NjY=r;*&%9rCzmCB9bWXeaz8^Zb_x%WF&1iCUUlE<#<IXoHv&r>+OH}UOw`6rOldJop=-l2HCHzZqv%S=PS9EUgyW-zc+T`lKE;_gOb@3M}XSTb#Z;a0Eyb<1Oa((}qaH&eB|LQ(AI=9DrVC`e39d(}^PtJXEf-jl-7U}!&=-l3iCwR1p>A$+qkIwCVexhfZn|9Rwf|72xF#T8e9n!h`Ia0foX<yyfNayZ-jTUq?&r|nJ(z$!zq+Y#DuI|4Ss58j4tM23E$ypDCrj6ixZ|eI*>D=BYD(U{$%==aMq4MOce?kSPo7YwMvkC`hneD9Zi=}h-zE}enndhavzgDwUcMZ$=X7Oio)bshIGWzoPx^_r$%P<M$k7fK@hV`iO|8>i-%2gh!^nbf&Sf)k^KHrnE>I6IE!dLK4_y|gT7MzXG!q>q!@pbqC7{P^~;|K81DDf-sSNsZoPoiOlMB`H8Md5vTQM@XwhQ9z?!)kbI{6$zDe-Up3Yv670w(t?WE#3~+#M|L7!CLrBc>7od;iIq?{wQ7y`tf3TCYTY=g#Vsk_*;T;De<%L3tSk*&*JY<;_KmC_<DRUoP*EBN5WTeVHbQP-jxz>44=Xq<5l3pcon=TEP@xszxA0C{{|MurNqC6_u^9GU%^7Sl=wMV5SJ4F5*EOv#LvR~xRm%8F@Ekd%*SKN^HJiJ;X`<3ydi9aH^e)_PPlLc-Vq;8iO+<y@R|5pxDH>7?}rC);b-`M{8LK&GQ5Ic#?vPn%CVZB5-$Ra;zjT(uqtkkTk&6F?VOL*N%#pad<Q>?@1ew3!WH;R{B<}Le;pqT2jMTlc5o2h4sT0|52VDWz^V8YJPcRhVSG1y2Y-k6wwn?^L5cqi&*MMizC=^v3Gf#@f$f+WW12+63p|$m0wsP5p2SbGO;1tc?^5Ec;7WWIJ`KK(Ps4}6!MNSlLn!g~l=u^rcs<w-uZP!#ZSlJJ<FN|BHn1(;mVMTS5+6W`Pli+Q$@p>@#+T!};BI_3`)n5_{xK!~6Z{$f3BL<vU*6@hcs@!zKTN>$;{{+MUH~tcn7r=`QsRYTbuUZ{)8J|GiwTA@J}y$?r{O956l3BvCBByuUkz8`tMTb@8a^E#3WwlB7!yM&@gOB$A3lNC#~-A`E5dqsMZ5y6i&wzQ!^iRRc)1i~s~jc%K&<YEbzlImgTDyd;B6RlFH++DDe*~gGCm1k2AAW@@SSiMzKb!plM+8piT?<H!hgj7gLm=&@Vtym8H;%-@$!^-1(+YNfLDYC@QV0@ups^*UI`Y$E8&$>jNQtV_(QRJ7#4>2;)U^aFfE=Azm#Ao<NFdNeg>Y#Pcx>^P~!V2@ilNYz6PHGr{gp5VQ?rulrcSw67N8XH-Po=26!d-AYKX2ONr-!74bZHZdd`&jpu^p@mzRLSPsvL=YS93Iq>WW$;U=^N<3Svvcj_Pe!MLH7_5UohPQ?<;==xTYrG#N{u-QwzlOg7m*H>VJK#=ScpTq>AEU&7fIs3t;CJAE_#He?qM;l=c_{I6usmK4e})oo1}osr@MmE~{8_v?d=PJrKL;z}&*9I*%J}nm3-}P;0&kh(*lS6Nw@NhYIAIm|FkS^O0t+W5uL;G|!*q$sYe;cfW2WPHwQElCPvIF{xGy1jy((_kvEpmtnuO#vu=q?kBO!UsEIu3#!-X9ZlGoefb{#I>5H?6iUc-x5hLsYM*Zku7VBUn}?+D_b^F2cRGnfaL68{wD#-+s1z+AYL_-U9Eml8h(bKp|qCt-G6O8gU;4VMx>;Y&WY#ihhQj`6V1FfETIPfLm42g~C3;Z@;dcvZX^Y>hX=yTN{VH+&R)4IhQigKyyT@C|SWz5zc7kKqULFX0dPm-uyf2fvPIPBfI`KQkp>9G1h2;|<_5_>I`Vy&0>o;Wzl#`1`Ty8LQ`G^&BN$gA#uvRyAP@_&nYM?*)6}z3{Pc3_ccL1Q+6q@XhdT{B8QUnG*j1euIC2e@ltqf;aJ7c#cF<;@RO1JUiPfTZ~x~4gcn`<bPA*U%{{Oukge0ef)ji!(mE%6D7U?F2on$AvgvP;XPnayeIpt2PNK|60Z(x;MMVBlz4IY2wog7kz(JMpu|hYsuZjRYvQ%=maqlh67LOr;l1&3a4bF!Ukn%Fi}5XRGrpN|u!Ryo0>8zN;NMZ=x8W`PHl8!lP{vA5O1vy3UIu2z%iyJ9HoP=mDlvI%m7>H;#;OF&0<+>-@V^oaW&Hg`iJyaC;pgx}@GyRuF?Wa(-$;qihYRre_-GiyN8{aL54;Cst~(|EEG1qIR>!O1epn3m<LM~z^sqRd9=`{c!0*8`z>;_dJYz!g*v&|ZXNpy3SQ?hXOXH8iTKJ=QE7%h63;V#9xUe_g2Okf|;p6coa526F-wL<j!Xx-r{3!em{}3j@@9-r2A9x%82hWvgDC0gCC4N6Fi#LT$U|GBg{xmFuKaDqrrSZo2Q?L~N6#gVEi9d-qN^$%&qQo2W`PY!o#)jnfv$6!Ar6oAV>}RXEeD-GHn6sb7;$OmZ3CW+`;s@a&T(~hI`Ey^~t_{TJ!TAZvYYFjDaCAcQ+C#h>?2ZecO-Nq1h}*S|cvV;}A$ct%ejoHFB(I&s)53HK$!jg~!>q@|--qdODe({BJ-C$k5tsp&5<dzv;!@%t!c4f7_(#6v<5OHp{8)^~eTG?hEO{16ybLUjm%(epNAcSD3$PV#kLMRC@s}y_iIn&R*asJm$0y)R;Szi)z71~0g-3CF3~!^vw^QODQR3gjB>a2)U-%FHFP=NmP>$`~l=uVie%v1C;>%<8QLIi<;=jTq{8v07jp0>XN<1CBjZ2AVg8$%B;%VV6TuR&r|G=fhuaJF*U%@}2#6OJH8Tcdo4*wDV3I2iqg#Qe0;XmW&;Xn9!{1<o|{{_DQui_W*i!celh<^${!av0q!R7cOyl<?!z`<}iJ{aEsPvRT!zbNrEX$*hGrNnbU*{?Y$@q#cNUJx$?GvS5s0x&IJ0M8D6cy>Gy%6?7cvG{fN^(Xjs{4+{?J^T<~k1tCxCYHg4_%eJD?1K-&yTi_Scf2cn0`H1<gpcDL@eZ&q-U06f>*1a7Zm>Sy4etTF;9c0?Jt*<l;RgJ5{B!sh{yCm8jVbZ`P{u)iO1vn{ffvO~z=C)Qyd*4ym&A+10(fz}2+WQb!SlgHJRhC`$~eftWAPh|jnD8K_*azpZnz%bjZcNk@MVmHsg(Et*c~5$zYM$LFXO#nN4yu_6L!FR;=N%fyf@wtcEkJO17Q!m2m5;<CH@Zl9DfJD31#2k<gs`bN<1&jkLSe;!=iX$+z(6Oe!Lhgi5J7~gT?Xt@Oxnq{9Zf{%!lW}Gs6scX8d2qhm3=NDe>>&SNQk%DN6hZ+>IZ>m%^#|RK~$lN_-l88J~uag}v~x_(<3jABm5Hz43AQbl4A{j=up1;se>=Z&2c2!<+cm_#G(w{tl1D?<SfOzlX7r7rzJ31`Ffa@LbT3=fZQtVt8&mC%g~OiD!lP;#u+ZFb|#{|1Z%nGcG0m8<cVI8zufF{2u=jKL$_X$ME+k@%P~o{C#{2T#7Gc9BiS)SHZFPDm)BF;$eI>9EY#Qx5DZ8R{SV@1Al}4eUuXa0p7uXz<-B#@!#>Yl=!z$#=*Bd7QYO$;Zow)U@lxr{BM{WmlFRI=ESAMFTt$1l=wF=JuW5w1(b2{1ttD5{0;vYKLo$T58->@F?<ic5x$3S#NVXE_rv$`{dfd!!M89DB9!<}7{+(vQMek9;vc}R_y_oDcoaX%{yt5KpM$^S=kOEoEPeuCM~QES-{PC`?eH?b9p4A9;rsAi@Naw<z8C(9@5Q&lOZYbYZTJoTHog{qfv?3^z>o12_+oenUyRR(d+_=AT(}XRi_eB{;<NEtl=vFBA76v-fDv4{6W@U!fKmJaeh_|uAH<Kt)A(uj_i;-6Fg$@D##h31_)7dWN_-3@J_T;Zh1>Bd_ykIPCftV$ci}VfNtE~uxEB|0!)M^*De=khZCtn(pNxkn@riH+E?kUH#D`Pjqu_j8I2Rv<52eIkfwOVpEc_LG2qpe1B|ZnP!RO#_!5z5p0R9%f2_D2Z;qSuZ_;L3AyOj76xDsE<zF$I#kD$c+!!h_6_I-ai0iVD=?hhy7lh~L2;dp#J`>a0<;UV@-e>fZ;&OYc5hvGxo*8SlSd<fgRKP5hl5}ya>;B(l%^WY|Y9=-s+i@(eET0n`9h9mG1y!L1~3?D|j;uB(DpI?+y-YN0w@Cm#+UIIRhm%#6X58(IVh2Z^oA>0qk;eNa%tb&)sYry(=4ZH;<-X>Phz{g>I{Bb-0tKb2=4lIY)!5@S7<B#FB;RASW{89KY{wQ7xK7rT5o5C0IrubAi0iTNRid6(|h7<73_;C0<J{*6L5-$d;<Hhhiumqk5&kXOwGvk?HAv_bF1^V$UcwSf%&x;p_HSpqiCD;P5gg;A(kAQ9P5%@%3@|c(iU&klnTi|Yd3%(CV@qPFKn1mm|55hDF#t-6$U?MIh{vJ%grNsBc?|jCk#P`Ao9$|m)rNkG);rK$l8GI0LhTltxXNAS^tay5u2TzYDz|438?t__p$$!KXVHTfz>apYZz`Xc9cs5uZ&xRL<mGHuN1^6sp0e_Mb?*m8ReegwaA}-v5FT%IMefTzfCp>`f#P`61_#XUScnE(Ne+RyYzk~09`|%z4R=5`zF2uLuy<s!FH(nmzi<id>P~zEPRy;eN0j9?@;Avq3o)%97eLnZU<efk1U?QFl&j|0qGvYa5HarJj5EjM@;$>k4yewW1K8e@EpQFUv!9I99d=gxQ3%B8u@C9%uz5rhd_uwn>b?{w$9lip-gRj8n!yWj1{57~07xu<q!yCc!cq6<FEP$86OHtxQV0OF+o)2cg^WnK*T09q?6Q;p);<;fuJU5;nX2kR3MPUxSC|(*C#7pDVU|GBx-Wb-y8{@6ub9gJf6D8grw!_=w1K=cFxBwr3kAW-kG5C164j+$);0ip1_lNWG{&-vX8vYvlyDcSN7nZ^6;#FZOyej@QCEfrQ!5iR@z<l^4cx9LiuZ&lOIq{14Lohe~5MC4J$7|vZVNtvx-UOD$o8YZsHM}+60XD`v;Jsigyca$UcEX3@uTtXOV0*k9-USZ8g=6q8_{(rS{xaSfhVah#ORzuw65brP#oMyKn^WRX!K(OE_zUo9`~`d@B|aE7zz5?4;UoA!ygRIncgOp}ig;hV2Yd+cfe(T;@j>_y*bpCrkAh9`QTRC68Xt#GfgSKE_;lC{pN`Lj!|<8-Z1^fZ8=pgokA~gw(Re@D1sA@I_rtrw&Ujb6BYX+(h_{5z@#gIBmXvr9zJLeuv2Y|l7GFw<ucE{k!@;<4Aifx1PKnQj-Em=Gd@jC>5}yZq;KD)pJUmQ^FM&gF;V66wzM2w$1CGOmQ}8$N4V3s=I2{+x#Mk1RDDk)8Y+N`8e+z$`5`U8tp9M$bv+!47KU~-qe+3^3JK{s}p0Fh@4B|cU$#5(#T#8S|*Hhx#;VN9X7#A+bm$Q$z!)5p~_T_dM#>4Eh?Qk`|ntih!ZooIN54OWi_$IdXcK9~_HrskTCBBgop8;p#v)H~f;81)9J`MK7d$PTzQQ~XhdVD>vy#{W?H`4AJ{_PqbFW~=m<o|ar#vWga)gP4jRd^Y{ivJ0(;D6%R;IH^K{CceZg1^CE@!#-YDDm^~3Vt5{8D7SJ#(#pB@SpG>;YIvM{D)Y54==!r_yzoT_y_(w{x>Cl175{%;5Xr)_)Yv4yoTSxZ^P^OZTz1U+wLFuFaAvI%TkkAHHA;(cVmBdCsy)hO86iCG|!Vv_@6J?pW*Q{d_lL~l*hJR>reCeY1$JH#KzELv8n@W<A27U^GB?%!K-*}o+p{`YC^IHcr3h@knDAMY}>V7o5!_jPrO;<gv2~)l5eK**uqiuZ^jm8QdxY-e?rce&LLd}4C=w%HT1tseH)IH|FT+aA>-bZqgms0^1U|pr8Lo5K#h?j%=bTsglj_'

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
