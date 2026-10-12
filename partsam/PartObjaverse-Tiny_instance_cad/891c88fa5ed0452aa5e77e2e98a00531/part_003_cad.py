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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_003.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_003.stl', 'source_sha256': '0e31d2595159ec446866395a0512ce6c36a33d710feb38a365d986fa6b345576', 'input_faces': 736, 'input_vertices': 558, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.17530708014965057, -0.4810865521430969, -0.358883261680603], [0.3458224833011627, -0.11396554112434387, 0.2790190279483795]]}
GEOMETRY_BASE85 = 'c$}qt3ABx6^#1!DGZ&d<$U!nBDIzH@g=9{WsV*U8$`lzoDUr++DmodO<%$fM4w+{{#$3smgop<E-Tm(8ZfEb+f35%e{q9<OJ<t2J_jBHFIN$r-?Y%W^kS={*$3Mkg?d?M^@2cz^MS{!g26XDvuj})j`c~-Kdr;tR^E&;c;pE0G8Z~VdxB+f(>5iTHKHsPGL*dd7cYd&R`EcpZz54X))4u0(z4~<QM0(x!-TQV*)%$j7-@8-lxXc3&JXk(lsciZ1(D48ACu`~yk_PnNP%{-1i*5OFbt*<zu3uU+PLI`F@AYtz-HZN9cc)jch}T`aRjfx^#^UwJh-F?+9CJE3UJoaK!Jj)Z;dABlVbtrfdy-};{iCUzzkbv^O20go^=qpKD*w47*r#S}`06-4S|q~x8y}w@uP3$c$NE17=Em#cv(I`xlB4`r@p@!I6F#m-t8I<f-JvH~|N7WMmEZhfKA)3{E{oR_$5&(jRa-Wx&%O6vuctJBe7n-ag*pGLo2%mWl$E#h@#g=1eY_rPn4Yi8skLj>JU`xl)F1EpEIZZtc{a)G;d>t4rF<4N@_H<LXh-~cj_%lb#Lx5TpH;p)Jl*Sw*|P79&ri8}r`IF7Uf8XUYvRGf-v8wjDnEL<z1Jfrcj^3TIlUgPS8G>%e$wE#5Bbl1ywo0bTpJU;9zD=s<)<``9`yN1U37lY0bWlkK0)VCpMSvnRC!D3k#!$=J@M|@$|v^guRr+l#%?O#9U1R+SL~q5kBqDA_2}BNDnFJnvfuk(7_H7vtW^)z8|M37-OpEc?DP8Q3F>-<LyvepGOCl#?^crY6WVT9=X2|@z5e?Cb9t+}E;%x=UShNI32!>i<H;Sj#OEh|P~Yn*;ZHUx|H9k-@h29ox>w!LCl~Q~skwE7nt!3vUQd~EXr1zJILqH3ZvCOPN}n-}@0$*bmA}hW((94Z2lVsmM%3TO?(EW)>Uu4I(d#Ko6Zfg}*0qG!qk~T_Q$F3=`tMbAcizQH&pC02_y1>;@`)sk^m^=k-LKXBpZ?l^|09QYeW|Yd-k-L4|JuoOls=~|>zQirSN>fRSZ_XPnmYf_R`t)X=*Z;3>O5ag+T!(+<KEQYyXsy~x;?7=!|%Vo+0QfGl^N>%Buw?swP+~ar|SC7tLXKVRzGT=$+I{5`(e@x$?E%<dF}@PeXl%!k@DYF+v|}_*R;<)$^JPQZggp>(zkx)^+=&%E0uqv?d$yc|9eSH<>z1J^+<~{DnC4bFz0`KN_}qhsdQcspG(%y+ais>^Z9Rov`*=N{_OLjqrXu;?!+|KC%?8KUQcXyc#Xe*^0Za!MdHb^tdH)Xult>Mc|E1j!&{X9nqmGp!`I7hQ+je=)(c%y_or)gVzu}Aywncm-{29iCsuE-@8|wU{QBh9=GN;%hJw6qE%-)%A6x(9&u`+J1=Mpsa=EkD-M)hQIa#5j*JDF2sOL}QKzXl6a_8jd%`cla`s;=Ff#_#Fm(=_ZJ-oZfxAD50^g8Dcskr#R^zhBr%j5O5_X^i1*Q$6u^6fBQmv0}jFkVl}!n!-$aJBNE@(SlC*Z*40vtA!w_wTGdKVFZ8d$Nw_gXkqX@%--^@rnA}dF@&6bo*SDzqU2|j9BoY%D>r?^Yfj2Pvx&`#`8SdbAmcv$L~eaV~>rD*Hbn;&i=37Y@+f*by@!{Z?E|4<?gP9;~F?NUQa1dlRvjoY_ht(KR(F$Lr>3)*JE8C;QY2lX2t8#mgRV!d2)QJKDS3n)?YpIdAuH(nvdV>{`@Ri&8J;X*2k9nTIpY9;P<x?-M1*8b0NNe&VKlf(yKv_9NDUlYu!zLPkZ^Z&Htr`tJPZ)uO}V6=Jll4hHq1PxeJ`1J?rv#J+Z)fey`hpWTVR8a>DDb+=&(HbC(=vea!U@YW}b8@p{UD1>2Q>_g!93-1Kft>C1PrUg7vUbzNTD?DfcpGu9~oU7Ogy*75ID{@%r$Ke5IRb=~ji&-q>I>{QoxKvO<H->p=7QvVzLzFMR4F6EE++sKND(i1Cp_qxk^MCq|hRoG{AhTY01VJ*L}{?=6KNfkzTJzAoV&QEe)cVEv}dSvPf{~jCrVvEwllgfBKW#ix4fBcUJ`98_DN6r6YHLpjyRabh-!n6K8HmP$Xr6-N6;`K<0ep=t0;@?-pE8fulMT>bovFw*hkL~=9-&aSjR(iPc6@LG`{G0YUG{x&~bQbkIPg$|juOE>u^^_icqm9>N=Q=ArY4PiRocQ*9y)FzZj`z|%N{`L2&+nzZ@7$~W51!%mX<S3C-<OZyKgWKm^jOcu{{D!B_bNTH^nU)m>%{&0ls={y-<Rv#DLuCPJ^o&uU!?TN>a+YkzjjFJDKq=?@1>_p>{rK|ZwtQ%%uQ5!(vw~J`7)xP&R@8W-_uTvRC-G8SNM5xagNfXC64*$LUhcRTF-gdzjwKrbyw^Aa{=qk=Ii+kpW^kzbhXrTBPqE!|9-paGo3#>z1LF~y{n!ZQMaDox3)g8Rvp*1+Fp+?9i^TpDI0ToJu&k;`aB%X%<p?yOR48oEIi)VM~jV6`H5}E@cUk+{_EBCn$z6tNjI{o=V#(`d-;8@dJFX&jt%*Y-y?%|%0KP>Fg*L5%8$JB2>UFpt@2|tZuh!dey>_b+^H0QzM^kz(0ZTOydL>AllE!yBA?&2In_FqxT*@je=hu7>9IFUbN<y6`o6ufgRkr1ztlPvTRO|@k*D5Q>qw*y){kRTwa<_zy`FfkoBkeUsq6LVxIgr|FscZ@-)EYt*M;A9`uj4ebb|76``+REb@(glIq#0Xw3@H)e)YYMoNUBC#kcAFhmQI8-dJ)6o!@b{*Auf3QqOJo^Cw;puP&+c+stC0zc%aqitYG)dtPt#{B+%0^ZWMr8S42KdAA|^ms+Ls_ta;fP)mNV&U%T@=O2UkJ>-tM+?RmvZie{1qS$n$htJLP>tM9~4yC8eslfW6T)X4-SmFJCy-S%|P3hs}C%v9jwx`mg9j<Xdr~X*2-~W==!^h?;J*i#+ULOa>bbh(X2YH^m^nCKyV7<>_?bB-|ua93H&^{}>dObX9uhLUyUf}id@EYy2U<UVvCM4_QU3M4uf2NJmKI0GY_b}Q;=lAN&`t*w0e|cfAhiixQJfHp2-`~-TOZ9bZ+ky3wubS)lr@#NA9g6Ae*mj}U6Duv*sXjNUF|WVh?AsBqM?O#B{12;Wz2q0XF8^C&yPD6G9$t@~AG=NE*UioM@!$bl<MqTY`}jWYv2cr;=a9ktd*jSeo0Wgw+MHix*(RmCUwM5W7}==K!_<ZReLFdKgF2tr+q1qsX}y}y<_fIm9llQK&5m<_soF!|DgOtO`8}a%>$U25@9)g{UGlF{`ROWg{`49#m49fvf3CT_H&?3rdGHIY=X!31(jVIIpO4bNN}FesAzlv;th-eCpSbRy%i$qMzfnGS%x3+OT8orE<1Vi!UfH=oo#*O%{Bu86xMZ@*zxpKisSe!tg*x7=|8k$I)yJQx^Z(0GugB)Jo~5q)sIp#<Wa%?Q<sbjlzyHL3e{qu1i!|qc*S(`hsL#!_+pmk!e<wY*IzE4Wf3L?D7Je;WPib|T`(1Tjni8*vPfhZA<b}sRQ2BELug4}InXUY@&h+bgG)VqL=|j?cJ(5sqp3+;r@82h4g?c0_eQUt_(1Ht<UU#a0FNwZ&YLS{xp?|r5)p5)cHUAaUSpTx+GUbDQSG3wy|9fS$O^1E{`kHkiO}Fbpnr_#HG~KQX;$zl@G~KQXqMLOgO}FcU<ePOt=3~|c@iFUy_?UG;j@PUU;$zkYIbO3ah>uwpB;TwH;&0XknWtG7<T{#l;nsE3>w?V3tPAqFW?e|r?YbbkSr=qJW?hhcvo56Rc3qHpnsq_^&AK4ESr_Cym~}zUr&$+dK4x7I-K-1ZZ`K7lUb8MpzF8L}->eIAKbv(ybh9qVJk7cw{$^beAG0oqZq@}k&t_eae6udd@tSo(&c9g~<hq-6LGsPIAi7x><a5osAo*rpkk2*ig7}zq;nwp|uM6UD)&<ecx*)n)7eqJfg6L*lkolN(LFRAP1@W=#!m|FHZ~E|7PwT^{>9!AV^|U^Gnr{2>X}ayhi;wBI%Y00~Jx#a$cF|40Jx#a$cF8yWcF8yWcF8yWb~!H7Z%@;0zg_Z8zg^CQ>9>oI>9@=IG5vO#r|GxLbus;R`CQX)mwB3gyUfS*+eJ71cJVR&cF|40U5?B2+pV6~Z<p(3`t72detVj3`|Xl%`t9<$rr$2}H~n_;H~n_eO}|~Pi|MzEzv;J2zUjBibvONXxxS{~F2`&7?c#6x?J|GUZ<o(C{dVy&{dW0W({Go2({I0ZAL@R)To==C7k|@lm-(B1yWF>?-!49;-!8i8w~N2&x6Ao4{dSqZ>9>oI>9@-~O}|~vo9Va9JWan{KG*cyWuB(rF8-$9F1qQri;wBI%W;{0yXdChE<UE;F871!x6Ao4{dPHC({GpaWBToqZ~E=xZ~E<W9!$SobklFYb${x9yXdChF1qQri*EYu^0}tpF2`m1?Q&eE-!A#4-+pWT)%|w4j;7x(*UR+VCExVh#ozSX<vC{h?c#6x?c!tl?c!tl?V_80yZD%XyUgG8+a=%h+hv}n-!A#4-!A#4-!8i8x66D?zg_%Izg>>k^xH)@{dUn!zg^~I`t6c$`t6c$`t6c$`t6c$`t6c$`t72de!KXXe!JwGetYyv@%{dMnti!xy4{y+^|XDtX}aBio2J|Sw`scFe=EA#e=EA#e=GiG|81IX_ur=JcK@yTnEkhMTxS2R%*X7%m3*`RR?f58e=DDB_TP$b_TQ%IcK@wh7qkCX=4tld%K0(-Z$&rzY{kdyvz7UneYP@xv(Hxi%|2VnH~VbmdYOH;;$!yN%6!Z|Tgf;3Y$f09vz6;;_SwpLHv4Sl{Fr^V;$!yNijUc6E4tZdE9b%Nvz7B^_Ss6l*=H-d*=H-~$LzBef3we4?q{>lR{YIATRG2WpRM?teYWCn_SuSV_Swq$H~Vbm{F{BYl5h6e%KXhfTk$dbY(+QwY(+QwY-RptpRHVXv(Hv^v(Hxi%|2V1zu9Li=h^JDz4g7*`)oxw`)tME?6Z~YYxdcSkJ)D{_nX;gEB<Dmt@xOIwxXMTw&HL0*-F0IXDhndXDdEtpRL?KW}mI-W}mI-W}mIx4`!dO=w_d-Tz9k2R{YIAThYxvThYxvTk$vhY(+QwY{kdyvlZR!vlSn+&sKD^&sOyKeYQ>2Uqk&kVfr(!WGYRKEH1C>+&=D4q5OYvPVm3~6sl|G|F1uVs#>Ya|MgFyo(-J)J~f_qj3LLo6EK8G2dx9f?T||~#M=PBN9=~y20Y0z(oYh6lH9GI5VYqoZjD^3X^kM>7PtqzEqHs!NM-F20sLU)dB-#zxm5EUf_M^eFL)AoXUCY{F{elmzx41V-aeJQ04+Ug+9QZ}0PX|t0N%whW^l|Yh`#_#58f5y=aEY_&m)L;1nvj#2;R*xW^~LcGQuw-Jc+-EaVO+bO(z8L&cGkQJA-$3jF}vBicIj!1W)2UFn$5KR71QA@CU>JXkEa2I>yY7c@JP_L?&pxFz$+6s_BX#-VJyVyc>9L$C$-2r^o`oEbt`$62>ngmug-_5bq8=1l}FIk7K02J?w+X3csxIB;FU}9>}Gd9th$+frr6+g7<Tb*&K6<Z1BqlPvZSC?uA^c>4hNP8+Zh~H~0X@nBbUGB)~5Lp2T0q_$B004e>s}BZwcN^#LE~7;`x0F9UNR5}>_;aX;izO+N(jmx0H?Uj`rQ7;`%26glCS6Q0Ch#dr{Msb&y@_+a2q;Df<mbBwtibBf&X%MDNBZ(uwOxl}U@K|BKd89W01remaK=1uqz=0)U&HWK64kV`ehUj_b*I05Zd@DYwNk7GU(m<N#;+Hj1AAeU-}Ac(&LOaXrdJmMHrS3u7xZiC-#@FYG2;{nK}8sdF{DTt%c`hpK~jM*J?itO;q4o~8PG479Csv$lQcocCQ+CcDOjxm>GJ{Xt_ksaFW7!O4*)eJ=t9}YYTJ{)|MW6bB6zYffY$OY{!j9*7C)x3@%{s!<A_#5D(9b<mS{4HR9L_TP5V>|-6R5JoW{7v9#@HfH7IL3mGIYmME6@(}8u^5j;F4c@g5FZ6R3qA^boMSBHm{SyjUm<uBACK`{$fX+Mqk(4;zd#!eKEW{-am>d9iy#U?n~3q-$fX+MV}QRPeuXv$e3E0l!!e%-yaQ1L+GLE!BA05$B8ZOz{suk{e2QZXJLVK&_=Vv~{2h$PBbRE%BZyA`UIw24{;p%B*VcCtCE-^Rp2VkOJQ2B6GZ8_267UN6B=BjDv6N#z6<7*U654c(CnJ|?CL@SX0bT>20{)(3EaR9{l!0FvcoKgf<9CotHN@WqUPJr|?OpH>9Ai1h{C!|KL>XvPQ*&m-=~OcnL3|qUAMk15GachSjyVPK8NhPjA7VTmxl}V9LHs@7zu@nIM;&8D$DE=f{3^ne_(vGOk6fyGA3^*BV7d_V55Q+RM*2TM%tBO#UuAd_pN;X1fRSp5&w$TNU`B8X;&U8hRmYs7D*UR#llWYWKMWYDhIlk!%n0u+A=W5}f9x0^a?IxfA3{`x_6f!x1&mZf{3H0x0%ixNApWUitl^kb)PP?NcoLtTn*SNJ8mJ*{Hhks)bAeM3|J*UwcFZY=e+H}p{sqQ!14gPL{&B#V3*LD{tWgmE(lOR?%qi-?uMRwkf0CL%4_Y16koF0DJ_Qy4ry%~7V|?5(ryxELSO+{A<Ie*|sv-Vmz*qp@MMA7m5dYdSHge1<8o{p-Jc%c#<}ZfU2sNZ7r}+Sjfm0A)>KL0k=8J(%5sjd&z<6=MNHxS4r}+R&fKw1(<rteg<`m80*BqY2*I>LnV5A!2s{+On@Gcc%je__($N02kz6SU-qB*pU7_SK!sfPI4fUy+3ONUsaAil{lKI52g1U`d!8roKj*9VMLLwr4aHUi6nQxM<o7+X8$6s_Uc8lJ>=V!SzEq#ELz;j<N39-M;sZpYZpF{fw;zjp8>z8B*i0VCBA-xV;Hhxa`p)+mVYcZ|<E=6iw9BHBUQhw;vUk!px<4;b%(_uV1ZD2RXW7~4AL6m8+x7M{fSV7x70q#EMe;Ijo-4xEDcF2~r$F{fw)zc%nBz60Y;0VCBA-vplxz%t+z#J4%dR*v}&U@Jr$Xj?E|7cf!{@$Ul0GVs1D#2N+h&5p69V@}Z$el6iid;`X@fRSp5$KbOXcqcdo@%4_eg=0?90)8#vN&GvER|bq!LwqHCRsc(aQxIS47@u;?DV~DgQ}84n!}!~Pk!px93m8knyLgB-3gXlYC4AB`j{%=VJOynf#!CW5sv-VOz*rpK;Sg&S#Fsn9W{x>UGx#-wC-HAFUKB7=4e^BmV;J6dgjk~>zRWQ;am>F3HbFFlwglq^0VCBAUjU!^z@p$3#J_QjjU97}#_($lPvVO({wiRk8shT;#-i{p6k?5n_(I3nz%gG0Y=CGCZ2`t#1dLQe{Ih_u5WH^>u|`3BzGHmCF<$_D0?`0ktJM6$sd)u~4IOg|;st>9!6}G811uO~PC>jCurPQ_jPnDjhIoF|=L6OQry%|`Fn@?S1@V@^g5WJM&I_a(;(1Y@2Ur)Jg7{Owd?Dr(#9ILKgEz-GH;`(G=SF=l;A7wv#GeG_2{ET2-W-?@ycx!~0jY-gZK%%)d=#95cvE2R5OWIR&478pn_!#+NHxTBpgudW7B~g*#=zS`%qfUB0p<p8gmD6pYKSMGJ{vF*oPu~mV9pS83gV4`w}CgnI4h89h-XE87GO<q3gS-ybA*^v5N`m?30@!L%s{Fko*DI-fRBJv5Puw)5MoY2ygo1ocs-0W0;z_0M$~5jJ`7Glye=?Xh&cuEdcXwmIvA%1QVsF+s80v14o*S*F<{mZa|+^hfZ4zw#W)0{8sZ_;2f%9J6vS%-Gl!T{5PuYy6}%S44oEfrA7@biFT5WF{}((lV9XR^PC>jDFf({fjBg^BYHlKk-vCwtzX4t&V9XF=PC>jTFcbJA82^J@s`&>&{BPg`;D3WZ95AL2F{dE@2rvV9b&UT)F4g>nApR$?68N9s4+V^&5OWIR)q&~3t6_W{xm0r<LHru<e(-DH4+e}uh&cuEYQPY9RgC{YF4g>jAbu5iANW=9Dgh(?LnCnt;#GkG_yZVUK`zx?K@k5PcrW<x;FSZ$n*no*oAA2{PvVs@zKmR|xr`uw30MLA68QZA<Bfnh#SQq~fG6?$FusUfs=0_D{u{77_;2791IE7t<`jR!?{9b#zZc^R$fcSK2;#p2?*{)Byh6bESHPU&FZlfhPvZArd>*+}a~?tb7hqZNU%<-;jMoF^6xZQ*9iGJR#`qj^spcGl_*r0S@U!6M0>(cA<`jRx?+<tqFN^UR<WkKU1o6|ryTDI_mkAiJ2Fxk0!tW|PiI>Ls6mqHN6oU9k;GN(n!S4zfe-D^b{0_h0;Yqv{#y=yMYJNr#KLIQOeggc?fbmkmoZ=GvF2R#{NsNC&F4g>mAbuQJ9Q-(ViGcB9z?|YD{4T<icyWwVkV`cw2;#?p#lVk&hXck70dtBA@Vfv{;>9rj5xG=D{3x&(qA0YZ;CBR!=L6=&faehxpcTdV2y&_B2!i-wU}5mX;6(z)a{+UTbMQL{PvV6!K7?GVIfNj75O_QILGVHW<C%at#TodWfhX|;ln?C;Y7QWX{{Soi-n2mw%A4;0^}iCn^+W#->eT;O*jDOoH}RD@QWrGYgwwP^2HJ~|`aBN#e{io)ogeo<SsC3u'

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
