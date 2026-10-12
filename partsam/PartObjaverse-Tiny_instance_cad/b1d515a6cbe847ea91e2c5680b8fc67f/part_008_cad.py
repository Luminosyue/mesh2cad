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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_008.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_008.stl', 'source_sha256': '53e1f0487aac69d8fff93edde73256e68d26cb30f6fd5023647ac6a30c4c0b32', 'input_faces': 545, 'input_vertices': 322, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.9804900884628296, 7.083329200744629, -2.104233980178833], [1.246269941329956, 12.026373863220215, 1.7142397165298462]]}
GEOMETRY_BASE85 = 'c$}qM2UJy8u)TmNVgV~ELY|5!_J+M&d#|yV_$&|$QNc<Q^<j(}jlK70RAP?=6>Gexu@^+6Sb0`#5k-v+_1`mlzwi55|F8Ae|Ex8cnSJKWnLB6Bx#yl|I<)r4l3&ALG41J`l+oJ*HBC`YEx$G<ENax?0bwI63>y*cruho4{+xV%yDn`z^l;P0Xy26@7&dZ1RH@pQQgy>?mMUi{6+S#_R8+rVeTPR43{!Zsei0+XOnl^^ej~z6y>!(oRmxeahLp36xBMUfyv-1-1-E}XXmVr!>k_)j^~|NWm2R28Rd8!^F~M!2uLZaN@r&Tv7axi%T#Jd=B>2Jhu<u<|?5$DdFN*$iVfZgG5cZemEfPHG!$-v(qwd51{7r|&PusGB>wA_J6Z`93Vj3vBy)QpVT$8(tAA88IB!ydt-xXZDmreXQZe17L{@Yr?^`E?h#80(`Pi4G&#Ra$i9d8l*X2osdr%q<3j6ZCyjB5n-OO|o>JQv(@s|@n9xo*1nshA?Tc4q_pCr3KOZ|?De8$I`ly)k6H__2q#gCC=_#BaM7a!baoSq6UQP8UD6%$5g~ZhM~oUgDV(`-S+QT=bx_x9of@xDmTg;y1p_`j^BRw^nf5mucePx~r%7cWj6j+<GPh&voD9p6D5Yu<tQRaI4SoJIY?0<|er1-31xf@_fx@8MnpycZeswq~P8AUzWJvtOQ>EhTxhle@_|r&sl=oz8WLAec0415_kV;f?M4B!#*|aSBd9AOW+H)21p*3jybRV7|WW%&y_iWGQSP)T#<Yht&DLqkOy0l^%B1|$O63TEY#J^mAA$IaW=uN55pwS_PK2@D%=*h@vV&e)`2`nWs1EXzy2-kUlzlB1xWqaUoH{cKIv<T-<o#vf;{irv4Yz|7D=31lc|z_OO8gsGkOP$pW3721otZ|xDmZfaLb54FGyXrumB%g82+{G*CdXp0)lG;-I2G>O?OJ%%|5*m|NCwSq29iiIIWF82yT?khv%IZ{z}$^cc$Q$8Y{8BLT7Cgee0is>p@keevH|9C7<?7D}i_JQdH~{I^C4Ky;%W#3fEDR?*Pfm?#Y7NFLo0@wkgvR#D8cw?Df3zyhd=5Ym(>W&VoC3?3Q`AEF5-M{HHgCeaA|e$K~fGetW@2z#T_0Us)c+OFkpZz)yoH!5!s0Wk|kS<PuzSPZa-l|G{Ua&JSk1mb|_45qs-`>f+ycbX{<xPaN`)r-32)TzgV*NBl8)UVZLTSx5HQiGo{F_lX}p^1?%@!@2tex7Rr=e)O>6Qdf={O9j`aUzK^$i=;~(TF3qX`+eCZKl-EOzh&I&F^IELJF&NPnj`tK&KnOu&5y(X$G%4;4)<?i|3@+G5Bi-)5_j4N*jo=^z4RRQx6E(V?!f;*oQ~;XNzy;Ky5M@v%~EgrS8<5vLnY*=_E*?Xa;K%se0?a5{8acJb+zH=b27jAp8q5Me%^#Sso^Q>+J5gE@M~qnztOx@n)q3B5qRin%*%!cVy|~f7Tj@d683@7C1u~UM%rQDdNJnL=X=SIW7KlNt&VuCmuc-Dh@Xfhf*V6_AV0Iu$#Xd-*B4xy-5bxl<=_*^=ZGr6&rOkWEoEjqWZcw(i0AazQlFZ4dCYI~+^{c`iG8E(n3tk!X;NR73s&Uk>}{;C2G_7I&!0d&uNekEUWWyD42(sb(b(UNR=Wk)PPG)=@m0t(shgc^u|6Dc5NEd5$jkQ87&lKe_MgB|d4K6GJHyYr1v0L!%O|N@$HGRy9otZ!YrefN>#Lpz;+e6Q@11Q@Kek*N?8o&+Jw&vSda!i;Tb|o``3Tl~#nFc(Z%HQvcWike_V!h8<(!~z+atI=a;n&C)fc47d=33caJ_GStc!@5qFZkEL0;E>i}~tzSH{&hg`&N5DC~Vw@LX-H!GGdC;28_jB#y3CVSg@B@?h-#?uF<tOCrvr&td;#=t+5=wgqATu^86l^ffXsj$?17pY7d8oCoSAA`i)zUSR(|A#pkeG?)IiqB{k*+XEyImL|JWq%NN<5nRvv9_z(77Iryp!W|hNm@l7AQlEOc{up;9>cQx^`ljG*8VPPRwu!xcbSb>|$9Ta0atz`bR{;LKfm`oi!Fp`<;hE%918%$<fcMmp{&@a(k7R!}PWa>fUThWi&%xKR@8-RVb*lM`uAeys{KGJb)1EC4{4Aa=xTDM})Z31^Po++L!UVTA{TlDJ3iYwB%jFc@QguJ-s$;?D(*Nos;f7-n@O$GP%X%rC0=#xn%-8W7I0u9$2yV;x1NIBX$oty1c&gy`xJ<l%e>nVH*6G;6@KdR1DVdj5b#dNH7z8}5KJs?rn->k_IqM>>ZMAS7{ysy-HA<9&{gD!QUs$t9-fZ^bh-ZCC<fmr}<~y4o;+gYF;<O)bd=l}b%euE6C>V^o>WcUJ{*!`R*DQj4yBDbAh!fZ+hOWbN<$fh`TGt&F+>vk{`Cr^kaQlp(1vjEv!%xCI_^;O${=Xgu`&GWOuUexj!%z0>I3Et!iTA{M57;-`f;@k@QRdg!JRRrgPo=Rhby_Op>i+G3k646!UVMYP%9>4ZZBR+%KW*_rdHw<^IPY}KT3qY{d*S@Fv^CEAdtwn!hv%=v|IQXT$F;wV=h}|?G)6RrpU4&1e?B$FKE9+n>@z0d9Cc<xhRp8;FTu55k?<2f3+IgYS@515Q2}`l?(~m5Z|nwHueK)>C4QUsC|<^0<tw=LU>fJ;0^%R|>9LHPR73n*UmlYB(aKyF+|s!S*5lW4g6j>A3T}<~QtHRLw-mk;-1oxI`Y$l<KOPSy4%-O99XoSl-(GMK=g0#6V81yS@6Aew5YLjD@ZW9#)}y7~6UoEaH#lFMPQd!gw;g%z`$TZfXBD37MGDR(O`>4Gww%P{7@Cal0;99wMq+>DziuI{m)HjquU_msJlCgaIVbB+R|xKCS|9m&-3HGaJR0_q>3E+udo1T?J+Y(U_8Q2W<F9gJuXm~eKT{`T+<4TvR>T57u^q5Z+vU0|{&T;5AkXpine1;yn<0`H<L(*39UbS(b6J-KVLyMHAh<pc^J}@7N1n^^c&6a?sdvPWUb!9iyE455w|EuCK5rSt^V2DLU)hV``^9o$&r7MRoCe-wvm&s*9^gB~sQIhl*08;(lX+usKKQw!;M#<oJhvakdFaXc`+`^9AaU9p=TQ#_cL{DU)(~|*HXQY~v;KYT&wj{%#V>(J#^1v}oE7VIDfUn8@qEE;zjwsG(W)8V*MnvN-;H&oH<=^rMW5dVe%9i9)7o_%zJF>p2kwb|K+m~I=0&$(1K;=(^LPsTqY*MvaBEsgtlxScaWBxY1Lt!F#;rdO=iT9cf?HzNVZFq(gI&S>cLcxx7oMwojql~Tn)DLf7|;a!{E^afe__ikD7f|7JsH=Lkq7qzZ!hA0r9lhi^VMQ}&kSz`{C#1>a|G+ri1roSI^iAO*K=b~pX;&<u6gy7d9<XD6#urEPq)NA+e3-d{&8rs_=$fG{OVEct26L@<(TzO-eX$IOq?61oW=Woi-Gss?D2TNmpdo<*RymN+`ck*ae3Y=uVfu**XqE&-CE?op$+H1R%xj+PV5fkt@1lrSC)4J1=ruF1Akdp;&bGRkn@YtbhpG~TfYhGdim`eVm~Py=bRitvJY62#|UmqY>4@FpDp!cPwfhP1>RrAjlXdYUYvd%^~1VdH(%;sKfGOV`<5hpKkoCE{+5=DU|${eY*_lqK4pIpC;N)6X(;Y((#lGm8?Pq|uHE*+`8;47^8Bc(;P#IhsM{5FvEHIiUzPDkmBT($eWld5V@RUl4o|*M6A{1TWqaU_vf(?TQ&;RK&D{mJAKruY+v*JV+h;>%f3+RhkNv9ebbRkj>2?Y0Wi#@yWFpQP>0W|6e$i2fMV{h3{M)wk!mDgY{4w<&spoZE*($i+qdD?ZXtBJ<EfFz-+uqqR?xPBF4`}Hb4*R~SPs{VztKz3lRoE|Chx(apypef)npbd#zm9sCwE^+Oy94jxSz7Gl`fOG9wwBA}`_-PW7{={)8TUKiE)d*d%O&=X`F_xU=!Eax?bx5~Q@(jG<7Tl4uJz9@_D1jn2i9riIq}~?6I^do2=9aXTh2<o=lACK^&sqr)2j%s?+L(nidRqZuaA0i2K(7b>@y1|W52qY<Fv$eVk+LVr{}#D`@&mJ$vEe3<GeI?GTuA+M&i4qQxNL^`sCMAhg+HoZi`=vdF(t~{Oi8mPKf={;@F3Oy^p%hpYOQDvo|N+7meNVozT=z?iI8dTd)szY=pWRG~tNkHKa54rBxc<*H_0JlKhNMK|EWI<9;(WpMmvV9k{0^^<e8}+bePP>md85rD6x%FQ<9z5In)JxZr`S#gAi0LOk{>oCl10D`bDOZEF`N<DPque9m|!>quLZ@tffLen*`b8X$G9=Ze9-R|4<-Zq1W*t~ER<_t{4BMa*LkymyQ{En}s<w;#R}>)7z#^60Z#{58#obNjiaxNrURc)5(bI9lq^o~r`RwMlzsN_(MT+!K~KjPKZL!+wzV6vp5FhSZyJBx$s?5BJA8VRmiohkjKeu`Z9n|G2+2L)ncx8zt+ndmgOQLD_H)3+%X9;nqos*l%aelYLk_?-?uh<#4}b&6Ozor?#W=CRvvuZ}1+`#>slqt~}o<>&zz>_AxzVo!T0e-!1EAL>m0}+`B~l=$`wqA0Yp>&W-W?`?35VQr8)W5NGRUa?fmg&{OWYwI(<}+ZU`w{ihx`B>sCb@V_>ne0OMla>%`cR=^*4wgPfKH_|r=ZeNsud~V%=_jC!b!{YD$O{~Xn#)*IJhmwL@vrNJMljpYN!Iof??=8pF+K6-O1M#EnoO4?I)c3}|cWw#3$HHT9?{&hC=iOWz_hLZ-_#I&AR-AkPnkf6MR)2@w{}~Yzu`bd|$obhCKSb`gj9V9RUQNy+`@i+OxJ%OhXG{1wl_~e|jvF0uPk$BnCq`O!?0W+W$bGqW+iK*e;YHlHzyDKk+x<11m!k5XvhKemxc>7coLfGYl{`3n=VG63*Z}zq@x*y|UZ3k?f1o|~hu$f8|He-gTzfGF_D8(rp4|R+>J1rpH10zzZN|g@w0D9#!mA+9t3B?Cp7*}oH(P7AMVxKR%DLA*(^Kw;EX|PzEn(I!iRV&);MSK(u>X*Rb7sIXxwq5HuEoB3ytcfjjPNspYs=r`JT~|z><?RilKTLoWg`4c{0;YXMeE4@oYwO+>hr@woWtGv2yXb6Mm;R)BXyuX7=ZhsjltMgH$|X6PmC4Zvd9zrXPZok$5we9@FowjZ~uM@<DI$>KbPiXek)&)?=NFiI_$%np&pJU$+<;4Tukmu3}X<^0}~2KoLb;P!7Y;vJnxiNxL?b=TJHJu^<Mlg-h=nT@pXbbq7jdl(pTzS%YQ=dYpnriaQ^YlD)&WN^DDA0En~li{eo}g9!9r?$UU6BP7vmI=T-T=&$vBEa3ggA>b&PlymxNi5M1lB5Bqkn2+W7^N^slp%J@FDZk2IunVGof^W6q~Y$D?Mp{$%!^n8UeFD+i<`(e`v!EN8YMV!$EPl&!d9pANGTOrR+;}OsDNV)H{cE6AJrcq0t)8@Y&xK|wfXi;*$GGfNcJ%?WXDbCvmgD~EV6sbqYx^Uo?vm@?jxNo!ibV4331fq_QR>b$yxA<Pr%Ur>C`;Yeow?(f8zS2KY@?QQC?yK%z2R^Jk&MQZc<KE&a?(?;@!YLBpU)ykBH7f}5yASwX^1S;Q)<-|wKiKD7Pd?b;zx>)gDRM>AoJBNEQFblA7T(Y0r)~wRKPUh1f9f7w?SJ)CcWAZH|L;%T+szoZne-$1WXeBM9z#;{NRvvM6l79Al9GFv)W@WuCbcC0igHWJ70G*14kGVCs>rr6v~&6x!*P32A5Hp-cn`LHPwK_?scie6d@AGJWzrFoekVWeBHyE~cpBxk>^qxW>C5P6*}rt<=QjHvp{)2h(k)`QsQ=0Sf3m+*|AVB)Od$V*ZRcEUcTqn=yHwhxQoljFRF0WSUD-sK6lKx`%AKh%Fe%=o=_Dm@B>&wdU-7hEMtuQkEU~f7*D~_4%)jC#DVL<)*QCGb^EA2A51aImavJ$*%JFR9NK*1nlLna7)TFMI6(2!N)o4rdrfgTbs=eZri?gjabK=a6((5qh&Mvazej4go>4nJsC>N*yLfYrLSF)XP?<8#?Hl6qk(nc422Ip%!c@(KHu?3W!IbA?p`QO4Zwou<ouJU$*<iu2-FR|?s+njT8iS0^$OueB=15Fx2S@G5;6($dM(N%j9%B9GIDK}-lYE!Pw`I}|ZI8EIRgO<2peK?Qf$W{AHljfQfW70~>%c)Ob`vmF{%*#sJtaQoKa`v6c+}kPJ**255%ZW{(-AwxKP5-^AkEg%!|I+7~^aJze%%jq$XsEB=#OshZBsQLQy~$OZsx3d}*pK;j%5~V+kK8#2#c5NVdTq*uh_7Uf&RCVcnmJN6vz2_Gi>zwqB;}KATgg7ozFR3P+e@@l{5<8yloht0@<H<bw3)*^IrF9Tr6#Q-chxtue;oTe^X|;!Jle<6*4ZbH{Z6u<^EvmiZ6EPCKF?P6-AZg7@i{JItS0`2NuDO<CRe&IW%cJl?nb#QZR(PD<$O8USZPu&V(Qr!F*k~TLwO42A*9kS{fDq^Gy5#%^CuEZq<(?)#H7DTi7vQvt{&6oJoyF6Pfgn6(svL0CsJNSc@f7|f7vzlPYCgslX-FG&YiO2UK(mSnE4E5PJGEr(^oEXjd}ESnS<K&5lFvYloij%ImqqO?wpellSY|TnLL{EBI@6ehfpp}9zr>UF@^9MozEOXKRZlHH)%KdGs>gb7EQjJ@*dhb`|V-wcQ7Vru6NMKG?NaQw2(ZRax{HTBR@o09erDwRD)dU#mL<ldrlYZACvCTuj&)#(kGlg!l}387~zz|sV}6@b}n`~nV;Rv$szLRly%0FpVX7sA=)I9|3g`=H&sijww!h2Nv=^=b)f1Y8)e0Ph^f9=C}&}t`nRQdOv+1AazT><s5@oFE%c@O<scOxR)Bh5%6Zu@8^_8@IV<h5a%`s`Z<oG}Tzod5-hg@lsV1?S)GeeE#43@OAX)efii#2|$mcCe?oYWW<w}$*(Y_M#awgT+KG#=$@=m0x#H=QTQdjbq)Rp`#btP}2u6QivvnCy-ewJLdU!i`7{0i+9e`C@I%6F)%xP~*X;o9d~cIw~Jua)wA^5HJJYF|h!oO~hM4ls^QBqw%&HqNzrfNjYxv8z0`U|yYb*^Q*+E-rJ~g;a@soHfy%_T8!bu&peq5!=*W*w&=}<Vp`D)go4ldOrH8MY$Gr<*zG!M3Q%<uLmX_H|Y`i8OlGKwAiHIC@cOeZGNTQuf&x+iS{E%i`g%dy7T)XlD2AXRnV}W6fZ+LD`ju;@|3HXR82#@=b`LR*_(FdX_tp{<WIX6)T@!&5NkudIpt<1bs%p;yo-x%7xE5lt3umql$$f=#*9VrCY0N|%z1nAj<jh{yY|GI&|i7VO*l>!j@`t?&KYkv#@CV5g>7XyuJWz+Vcn#98uo9USOv~Ubq#xMb?P4f!aUel?fL3mqxOBZM|`be-%xxo<w4}GdJXb0%4)wDreQz%lCpE(38lYb<VwG2(sh&Gl9c?;q?;P{j!X^vNGA2`Y<uTor`pt>WSF#`F~oA5_2f!FN}E{vG1y<V|H7Dlap`9;zV+n4P`*xGwXZN~l}X1)N<KyTl}Q=o$A~Af?`zUUKDV>&6)B1Bim&0=N#qx4zlv?A$dfoXzqs@n%;#Fgc^XW4Fl|;4Uqv~Ly84b+-^o#wOHx<glIr_%B1y?VF&9T&=IthRb@ou_j%d;}VrtJ-`>@)B)tN%QAJkr~_Ia!J`TeD2RXb`=Qw4tCWbWij&uY?LVv0N4z1`HmBSgF6cPZzf?rc~3HT8TZFKE&i<i3;@m3KpXNy=4d<4!wY$|{~hjHw{GJLPK}E5+nq<Vw$G(q&?bJKH@?x~idF@ynDw+;Dg0Nq&`bag%~fDoQFsEX1U;l#5diV!Jov^=7Pv*sl6ir5|q>+oH^036t`hRG3`p0VV|#^Cu5xTPb3J<fYi=&*u*$_o7^w&+kv3jj{*z!jzrk=U{Bk{$A9BI94F#K;rdHs%TO@@=(g^nQJizWhqx6uS2;4<;v_6N<EZV9gbCjV^^SFmhHjBf?e7}nWxI+!IT5o=8Q3b?Kw^QWX^kba;1ONK<a+=6S>mWeW2>+!(92$PhL0l&r5$!-N)^7|J(GX_zRNrj#kloVycgl-N=3D%gtrX{M6OFy<p$$Zl9k)VX95t!>YPYrS9~3i&(15IAu&;&ZJ7@H7WbKssC5V{1ze4Lpc|p)sH+E^On~I^J6YblLt@^;5?LO{gnQfUd^PJ%(-){EX33tDE?6UtUK-U&`$B(l-2%H!=&2eN-s~nD)p+=YmqmgT#IrY=0fG9I(c2n^(i|sr8hK5r(BO*C*FW^9g<F)0*u)iyVCP9=f#K@Bd+8!)GefPZlCAS!W{ZBr`1RnVjWt$x##!zpZ>SW&wn;I^<UTjiSpk)|Ladsu05ZczW(zEsSd3@)w$I?D7ni4H&mUxwf_JdhM@u'

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
