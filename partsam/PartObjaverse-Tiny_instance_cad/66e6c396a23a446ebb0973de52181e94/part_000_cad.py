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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_000.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_000.stl', 'source_sha256': 'b0ff90e02c86e9e8ff7a49139eb0bc0d7b5f838d49fcea9e3a6dda3e01b86e40', 'input_faces': 897, 'input_vertices': 493, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19327586889266968, -0.3663799464702606, -0.1302691251039505], [0.2535002827644348, 0.14896567165851593, 0.22105516493320465]]}
GEOMETRY_BASE85 = 'c$}r22UJv7^zQFOu@^K(><%_;5u;*D)T_o8)L_Jdbwm-n#@=)7y<o$hQPkMGfFgQr*a3Uju|%=P8e7!=oc(>{3~#-+)?4qHwb%FK^SJLh`<#2uoja@q1*S=xOT!;uZQYO?zOm&rO+^+hmo_-8|G@5@!v>V=({GqX^A=zIap~NqEt&*{ShT^~2){0213LHjt8VrCscTigvR1#YeftmW->FZ>zWuv|DZhTFUIW6M{(x?s`h_`vE?KEs#j@6lrOH}IS^ppZWO8=Fs2hK5zf;X!owwI=s=adD38m)hk>cAYdc%MJM11Q%L&diR4>_QI)<3p9s?^q?FZ@o0rM<CXzqB_tcSN3=AGWEV9j88v@304oujkDu?Hw6U<GOc#LHi$mll<EKdXis{sRMswZ}Dxp|G;&}*AQR(?2!CM);uTW-`y*Z{Aqj+%FlTNrM;t4Y4MHorP2R&HxuN#gG<4WY$v{X#pkG}uO)6oe{OA&_V(D481K-r;v3yMpg$RlAWxIm(jTqxP1J3M6?Ja+3i+=tz_{`hKz^S((ogI6HzdFAmm7Zc3CW|Ms37Aq`sKv9?6oA1b?;PZuMN!(KlG(3?WR4#xQ=B&o(Fx=|AxzP-DMi;`RTN@*D7Qa-zfRtQRO?5Z;5ZO8HN6A`~d%LIO=({r?j{4cq_g>{0{10_N9#1R^?yu&D)nS-o=6F=ZR<VL!%^*9-mS2Xj$NExerNu$ANR`XNyP3|7e%wxBn3&b+AT06yNq!Mag5!5{>yPbw_+-awz6Euqx_M^*Y*LzK-!;3`74LTtxobUC^Jk9nsH-vl#Egm8j>)=kPn6M*qwDV&2zmz`Xx;9M|1^TKZ{L$cXvMwg>H}twnu)>M6cHCl>8zMWFxod03yVqEUyGXUIPz1^El^M1RtSN_%7ICA6=&A=P}Dr-KqaeJwCS+B?e6!aVvc6W^XY0(B_YPV!homZoa2y{U!k-it)tuEk+JSF@u3=JcbU_oH#)GwPXf3jD_3B9FJ_n6zIy26-0GlIz;?Zcp&^?ZG#(-X>HR-`0I3{H8e$$+$*cMEjwG(a%m<aNR0dF~5HdK>laFu+BT&J0kgJ_C}te4<)~~vLEV`w>#?J`7-L@wHxcFZ8zjueaZA(KgP0ftdpx(v96Asm;AP8HneYlK-xQ|HA6o?wMjMa+WC1>H}lMI=uhB0tn)hQq&~LDAdG9rWArCDKkBgN7xAs{w@4oAf(DYuF}x1^pbl6MQ=UkF%)Pad-}egE!;{kJ&)8b<mkfgMTMpx$@)NF`>j<v<sy6DmurlfskQU=@VL_e_l~4z5G1?axExxr;QS>LgDC&RX<55rFmSGG0@EkH;$F=-ufAIj;Ntz<KzXs<({>*o<9`feJe)~Q<`mb%memJ8G_5n*)_$ldRo!GUO=zl^c<lnpp^SH7h@?1!ZaTV;fL+ZQz8P1Es7Wjo$;Qqb6HkEIy7L7cm*JGc&_c=lQv4N@9gWl~Ed_6+)J5G<nd}VwNKi6gCFR5dHNO~&1)+;#GePj*2FTP{eD#>GZoq_xAziaS+8HxHIh(q0stH^VB7TT}6iuE?^kod-}{;Ahn)3^lB@jCuXM*i7*#5W7A!F*ZbWn9|X-Qv6UVJ&1B>XQq;Yn|9<rNKIBzYFbo9%=s9P`6zh;P;BdzFMaR+E-f-|G1y@-#R7ml<0_c7}v;Q;@e;Nif<fVEx!Fi3-OHuzoMSK=cE0!0jR@-aExo;O!2ML%HceEeHnGWJ~qK~T^S8_pndpg)S+BqS)b;$lh{u}dSD(q#baM>-5C4Hy)d+2(|voY`;@-xxk8)&H}=VZj_?~Tz`8n{5A_++0sZeX1@|@gH~Y<|xNgz2sDGPxSpW9}aosONu->i@!Mv1&uRES#e(%ggef%3@{S0r4=Z8oQ>!(UR^k-=`)OmXg^gm~H)F*5#^7k$(_1E^6O7Of-ZO;c`pFC6o?f<=tdY(Ck{!A%`e&((r^|37~gL$0oi*XIvBEFuh0sQs_Qnj~_A0v6}rG0SScf--o_+`j{Ee-mAaysVy*xy+H9ln9T<{PZ5FkSN7w|qPz`A2J5w>KN&d1KIf@%8yp=;wvusB_Fa@$Fd~;69z+9nUQZFU5E5!`AwCtcUdQ&F$k;J+E4uJrmy%QUv*XT*kOsKNjD%p(4gLXp;E0*qg{RC>q!OqbTl|4>yo!es-+S@513nofhBtloR*Gybs9#<T%><EyZ=Y@7eOkBL7K@>+88(ay$CN^Ui3W8{-|e0qrx+$NI6|!TL!TG!yqp%S*C;D~+8mY7T&3svG>qujYw1+%-%7UGui^i+!1czfV6~^2XPIUvR=)XvsNJ*SWvIe_LdMs8<Yp|K9NLmc(`cJvdkT{UiYX1|8QucV2wWzXkjS^^xDF#saC+BprUW$&sQJw=GDOKTE+>z8+WtzLyWK>wQRk(<>DI_al)%_wj|2KYKCwrM%F7iuWR^`-sZ$qZ=<29h!Ghsyq+=M4r-z7NzRX)#_+JZ0%C4gHrJK{JKbVT=8X6PkS)@5<}LC=4&gyy=+$aP5(uIERV!DdiI6ieZg8!-+sLh{2u?}x`TdLE_L{^Bm5PIIA0yaH<B8|U%U@_Zhscv8e)U5mv1N9qW+)K|1a&tH~N3O4&xgyzU_Dev^Q%v7ft_Md^_7~vA+)#eW}@Hejh!(i2B}^`7$b5;pgmy_CYJ!ieIFZ__ndlaotUKSBXxpEWS}91Lw=SMEqxU;kPOe|9nV)@v{zsU$6sw<5{ryM;GF{b1T3P4*o+lQ>;DJeX+2-_{N2^;yW7SJ~G}_j`H-aTl2&Bd%Rly-QjES(=z|W?BnI{?N5<^AJ<9X6=`pb`htE2eGC7^UgUqBW`$gLaX9?yJ{a%aEaGdUy25{cWt^vPEa!UOw;@9OHaW!Cqpj$twWS^NR!Dq%6Rw}2JimMTU)O(y#L4pSHv6scTo0Pp<Or<avf^8>^1h4xFi1340P=Kb0{_IE>7Kq(o$F_4>E5D_U*R9~hu^N*Owlg}{5akhOEXT8{tTXgalP&V|IWb4p1!?h9{4*~j28dt6!;(SVI3xxll{kN9*H_1?vM7Ds$f64d;#MfmX7^TGez3}dKLYd+#3G8*frw6O}8@DeLDDKl&5cx<+?J{4Hth~Y4NoenYiBku^vkLi*Nm{F8u4yhKQbNn>zpX?`BE+{awV@=lz9ob)2_c{L{<D|GNJiTY`07aU*=!x~jR#5H0i$`9DuV9$z2qC*!=Lq`glxeC~V3rTkH;>dbYhy=^SM(V#p0txwUPKF!3pS<}FulOOYSFkE~+2lvBapK-re>lKx1UiN06D*lYI;#+qgk^UHI`mB_{A306@ulvcjkvNa;EJU8co#5B0i2JdH1O3ce4de3eDEEa?;U)Srr61a77$bGoj{B{W_Ghl3{p*QXp9O1*ue~V-|8e|c$&<N(`1(_>|K#D5L<8Q4Z&uiOL4IBrxkB0({VcvMjO+QQemH+0w_PpmGo**#tKJMx-#(!Q>JT3xbub<*U!7{a%l+iOGgcfF-?+I9*G;^zRP^j4<i9@y{m(mAu4^QIzef7Ms0#LtTBoI-T6|^kjV`|-f7ES^cS9}lwV0|rzY?d3|D}caj{M1TU1RSh+!w2kAkW>T^U}V=O89*p@N0MBb4Yg?uW{k2`1bOC=;wfYI3I_%|I2e;T>Uia4He(|QylX5$nhtxKT>?x`QqB&w5%85`-H%MSpd%`ot}tqmU)BgrVN*LsLgD(R@%Gv$-&ddh&CJ{zBOYyjQ5q7><?P;8RBd0{zCn|qHqrWybtYTU!22yOhX-P71oI#&<6QiU&Z~tvYGhiywKG9VMH78^)0-=a_?G(`(>H<wuo=IKff3&`f5G=^#f41AHA`D0#4w%uKg#aL8$1}YU`!`uKnK{+za<b9q~1ugW9o_Fv(LcNPOe=J&db<(Lb>+#=tMA;kwr|$o;OZj70tc^<=&bZQ@^|y|=@!av$?}sy?2h+Qq?tup09+GzsUO<2~{x{0#rbW?3gj{q!58Zk?;Mp1V6qyTt{?|N49~@F3QkRtCNopKrI7nJxYhfAJk}{owa2jXa?v;O8&L`*-gI)MGNP>)MAehoC;u5#rkm)aO1qE3}q}|MeVSeogjaqr*Pr-&!$Md+p*u<e!*L>TH--v41*hZ503Kt{B(w45<IJVdC3X-^Dtd*8%(dfLQSzpMU1_tvAMdD90x0XZwKE&!w}<imx|mfjsS#`8*RKzBVcY=J)q4*jHaygTLSs`m<>#=4)@{Cfr}uFu!#pu%FbvD87+-Bif%eQHLxq#CKdRhIN(iI-X~C72GWAw(vmIq0VD@zBNjQiLWjG75!hd2jdEvf%f)=SZ~%Cthbvd#n-2O!gb3%NBbD-7U^fLN<61Jpbq}U#W%(sL;F10;Ag3V_F>(z4?K9k!qeAYRYTphSb46~rhXLP_Rm%1d6rksSv@jftK@&*3fJAdUd|nJLQV0l^?do<n^*d&ckhk%HCLlP83VA-UyKyr>}N-v|2>X#`Pl~XZD(KLx>FM{FDtgAeIm!3X{PkYtaA{4%3jp1W{9jeefnqdbw?Srzd2p*Bi)e;??-&@U|x>hMV(vah41>@*E&$nDLqdc@ol^KoIkQY#?@%-wp91;hfLB>efauqsjl1ZAf6NE?8EmHmx`dDo3hC|F}?A<lvb+%+OJ)O^YKdx-jC$24PSdA&wKjzf8ZDPPd(m8mGFLK&<|+;?h~GGPc*`NjS~;f$j_ZG%6QF?Q1Na5-8n0HUT)khT5ZTq%vS^WQ@i5)8hS;1y+9J`Ha%pM<jeeKmyD}N4b1PM)|lVf6{F?8XzIuFE=aDcg=UKpfAV{@AGZeg<H!23(jWhYa$UV&x9y^xg2i_n%O(9c>OGUsedg~GyQQBQW?@{Gp6F+WqvC5L_Dg;}z`9M^|92ry`rqe+<kzkx$bD@_zZYMd7>s&O_1>V=_GLu8T=#l*^uNMf$*+4AJuLG+Cr<L4lbgke?_W-QJ$A0-H=j1xE&p!rX7TN1n;}oS+B=jw+TOzZ!q=H`-93k;p7u%k`29?FjO+QJU6SwnJ$QfC{TQy>-hVglmk)TKz2_RPyJp)S>3_IC-p9OsgL(X=y5u)oRK<J5Z>A!D%nH=!MH{p)<176!Z}>)ww*FDx2OE<esQ>p}Vr9Ig>WZ&je2F?=50G)0v7hn&zIQFmW98q_|0ZdVOP-i3X#YCB^i%uiTk#zwE5rX%RPtDtw-;YCOQ3FN%gc4GNfX33SM)#~{4U0cuWd%2BD2tcy@B}lO-FIvo;#3dRc5K1J$Hb752-)Qi}r6W%Xl3zKZ~y=2g-hE{^E=LmAm5m>dV#9es0uWsmG(G@KZXXeaoE4pKGo7_TgzUu91x-kMUwR+ILxi{-hru>qiT-;C)+#C20RLe=6Th%!m7BOhL?h^GtZ}c<Y1Y(Sz?ve{AV;AkWx0=+DKGa$S98MZ5>S^9lQWx^~F3s}0`c-uD+@FR@ClYu(x#@408*M}K0TNgl_fImmBxll|E|R{;5M&qqJ=wT1s@Q>_2rH{-hR@O)w>jFI^@Hg3iH=KFY0Vm#@;Q`#@tjrWnW%c0Jt(qg^k+=uoDOG|sb%urcZ`d^3m-uE!-5WiXKpr1)Ze=6ie`}Q$dSN|koT<bpLd0<c<xvnG28T7OBVbrb8Q{>s~;P>h)a2|!OiAm*iJ)2%%WW0{iDVUdp2WUUCob=On`7!F237=oIP6MSs`ZsTJ-Sap%_50h!*J{2;|5xET&Fr^W)~9vXCtNorUh?ZnQ*ob8@RIk|W}ZaU|H^f&|EP50>%qzJlO9Na>{YYiJ$<Pl$!`x{V2Ym3amuqlU+eR8ZoC&Cm>2zdQ8`{T)Cbqq@g7f~KWo2?*T{oB^Z2~lvWDa_rx(Hdd%mwTmv-GJ?T;0MKjJd#-#oj_yX~dF_>OnA(9efUq@T7)0m#2TH}b!#Amh>wRl#^CyhDA)S!JJbII5zbry9X8eMRQinp7M4`T50Rvzwm2-nT5qRl2gYx0kGkI{c0I49?GQSf5?+y@b6Y)~A^c_qA~i-%}ZU?_~PrK|ce2J>|I$^+G992fJ6RRQ0j1-H85lY=i!fzKV4|{;FKp?jMRg<F>&6IjzjQ?M^p*KbC^`sQS2tGB3K;1NpCHgI|2D_>LcY!OvJ2eq090V}|rb{^u{z&ww{r&!q>UZo}4M-$+`G{qW>?%*z)(w_ChreQK9yrmC|(XS$5n`s-Ze|9v;|KN}|NN{jpxd3v3~eY$ux@|0bTI=kMJtSv5eFiXUueG|MFHG8$#>*<>t@VQ36Ga2i1`VsaY@6*iM7tx>Ymr%Fc_`GR8E|2}cz)iG2Uk&5RJVW|pZ{>hrxh(o$;7`<H&~5Z5Y6<FdB1HBF>$baSzaRqZ{8$~F3z;6E4uc!vx}T$^KiZwlr=|bp7NZW0=3sx$;v>GD@00bp^`&k`9$)dTjccNxtBat0jauUCD{rHp*`DIO8y_gXjqinYOC7mi%ofeXcckRQb%#Ys|7`<;aou?I$DDi|b$-+uzUzJdi?ldjGPFVdLV0lAlmS?uaW?UdTX@fG7FsF&*AI?L)gNtcqV(V1c?QPCeMu{mANyX%Wcc1=(4RZKasG}vgZ?iZiR%^{jQ#M)4P194>Smt$BIDH;{EhnX{f7R2tBlL>@g?%NNI{-fr*L0ad2`xxy&0p=V|`}$g!!7;9{J-AqCa)Nz~A#G)xK?X(h|k*!Ov5z`pSAX{`C@HJMaPHy89pYtL*s_Q?2L3WXx~1;^G_0cu!>xOv1YID<{5<pGWi!6R=;s3lLx5z83k*ZNfg;zOMMzsQ2jSw71xYW9p+lzb7(#CWx<HXn_9koYL>zj`sAmM0~C>KWxPQpVUTt`<q)lr~be>+q^sS6zz<9hHu3E@_P^D;Xa^!93#FtvnPChem7q>!E;DTAMqVAIM=jsfq4F`-5=v}?T7z)<9?Yk8uj6RXf`V<?Ttd?F<#&NtXmuGOOKYL&V0{i-u@Bi>Ah`e&+i?K^Kp3IsJRRM9D?_s`lZTJXZx@ijF;ahn)|Qg`S#o%w6BkS#@Kcm&(+W4kUult8|V?AaGz$2M|+-wdWEdmuezCN-!TmN{lihWsDr3O)h}F!*tZ?|j>30+e{|;!p3@#DB7XtCM{1Zx=F#}>YNF?QHV4(k^Uw5~iJteDZf=vhIehOSPb}s|zgQUO>G?<S`FyC?JQwfjyY6@M(|FWv+kcoZzMnVepTT+_n>I=E^uTk1{x)3NTTgh4?|L3E58lGQR5Ta-P<-FvTIbe6e&V~nS28>QgXh?;6_Y&sX*MV%`HkS8#Q(YvH_p1x)7SaEn>i{#e7%1S_|v~b`}k%U@3&2oJm*E*wHo{F4^73lt>JrMp8ICuR^l6cZ)`3|BYA9XLy|n#t#<bW+W*&0e8*8AwEwsR?N9eZ|M@=0h={>;LkFV{{61P=e^Pw?{0v<872da-jeAHQ>&uzA?zxO;-?s$r-%0b}A8wOs-_SoVM1H=<GpjF$-*0QG@tRqNVZI*hOw}K=@_5Wk(HQtI@g7D$v{UNrc(pId^L{j|=f-oU{{gh;{;W^yi|4N7Wcd94NZ<T7)<fy@sN0Ns$TR05&Z%#oBmW6}uWg)&M*nMk#60qQ2g7?V_Va^jk|jU)Z8N->Jcnon(kFYabA3)O+(+x->m!@O=lcYsRYv6De3`cNc%E70o$Ps^>i1Wo4)5~7FB*vU#(X^IEG~)s+)uuqJFm(ld)CJoY{$4ls==?{EY*JH^1qJPz9DvhP^#a0Z?nBlzv-nlO+`j6m)5nD$FICAQ~h!2|Nd9ryI1<Z`jz*p)vEme{>po2XCHodMt6qdJ`Bafse{SG$$wBskpCc$cE$i|f9eQwe{wf!PjWYM2WoqA2XZrNQ*twMbLubT=HzzNw&Zr?Uetl)0o2jdfn=rq$fL=BQ2Tm}w=e6VG~A;;;jCYGs*M^>R@#EBG>~i~w_+&%m7%x+wHmnr`6q_rveaT^r3J`k$wjF-$VJI{s2Rw4$l0iA$=S$WR14XQoQA5AOE@FHGpbX+Cs!v2QR|X}$Q`L6<c{Pa)IsDS<grwPtaK!KEO`_|aaU?5a#wOaP2ISf=Hm=+YCf{kQe<zkm7%x>wH~=1bJk!eZpl#GgF2GjgWQ{Hkb9HEsDsF1<i^wxatLeJn4vg;p|}Y3dvXzSE^2;qE^=0e;_TEC<m}{v48?v7#pM`^f2LL^|4a_129cF^BnOkbFcc4?4j~UCkD-nwk0B4Gjv@~whf=$eL&*)P^~ep$KTu1Ne;}8k<|CIO7pMA=i<4dT@nOxBX7s3GMvvNN^r*k$%v5i((k$dm)ST2T<ecQZRBy6UD>*N@3bh7VX-jeyauaF~auafEYHxCDavN$GxefU@hT>Y(#^hS$($oO5(jsJ~g~>|4BbO%oQokkpl5<ltku$MIxfzNJQS*`ukt<TGkgIU~6&Z?aQ(Kd3lj~F4kn58hQGX*hBG+Lk_NUe&*Wx(+slH@?a!G1#a&C^HBtvlpYDIEI_O${-@sHH{<R8g3sg1}r$vU+TStnPe`jh?HkE#sC<r#`AQ7e!u@Y<EAHOZC8m8m*eXWq)x^5jZX^>aFBeB+Gt&UoaESL$aALU9(S=CMFCQI(&GKP&#1q4+LC@h$2j@-1=-L-8A`y51Z9tT?MPN>NKvzaf9aew1V=E^Tr5wKPL<S%%_r48=tmit|!4k@J#sQPtRT@n^+pEeORAIrh8chvX~NTjVR`^9;o|sVU@}<kt+v=`GMV<n*jlcB-mNc820Y48>(U>R5)MxB^45KSObOYDscQ*0DT8@ed5e6{%&(70ChAa^y<X@2Ta;-;+yFi;_!_3sCct^KuRfFcg1FO-ufkoWU7ssP8mrTJk&2;ccp#v)c^CXQ@}nXUR#_^W^iKvm}P%OAN*TP+yb(A*W&AUbA1XIky=Y={b({oLASlvUA+oImfO#6k^Q^agJRzEaOq<GMtApoO{LUA@#9S{&vPmXT&%onR<Y%{?6fy>kP#gsLA9D<kQpx<kRFm48_~1G30IJ9Sp_07>c(t6tAUjBr9D_UQ1rZP`r}5jI4Aqc_n$NGoq+}QWul|ByXWEBX1$^qpl|JBOj)2Bp)UxQe()8<a5-M<a6Z9)MRop>#q0)^&Zthc5u$_Q6H1<ksnZ>kROnrQ(usulixEGe_<%LSP+Uo(|bbxO#VcDO#VdvNLB0aBY#%x#Wk6ZtTYGNi=2(2I5#yvIXAg5)t6kH>PPh@7o%FKzGN#oA2mNYKd+aMq4+y$I`VhqoK%gRlbo5MaSu>?g3>!0Lh)0oMpmlk@+s%^I{BJ2;+=7Vx{iE;yqBSP33UN^5p^DQ0eK$TPF+W~lh;t=$!o~RsMpBX*vDhk>tv-D$VyL>mF^)QBX3|Rj-+lQD_uyQ;EeIkm`a^YRyv(Ll{}L=hdh%UL5(CwGQZ-t&baD~4-Cck8Hz756rZ6UA)C%P<c#eM#jy;<(bS{lXmT9&I601-Ks`e~!)ql_my?z5CMS?LQJ0f9k>@*OqBEvAV;n>AB<c+EB=R(d;@Q+$<k{r8)cNGO<Q3HA<mK%53hF_!(o^IW<ju}lPu)*FMcz-o#!&o}q1bhQDR!O3iZ4+QYVNaJaT4{2=04vQpQT>a+|LGzUC$4S-%;Oc?&l4~u5(|pYadXYlbX?EugJ)~M5#AfsgK7#<HLPOX+e*DsUY_-rA0jUv?3mRUNP>A#poBO79<xZ7pD4<3zKtGy*>6`Z;$=in|ro5$KXX(<Mg6_(A;~wV%J%q_!IR$S?M#f(wCb1Oi}DQcND90N$G!@`<znjI=>XZr@qwOXPn~a)MuLe98~N&D;3|P-X|-)sJYKs#Wxs=FEbRMqn;rvJ+8UWeZ`5?qni6ULGfYgA<g|<p?DwFBrDyixt~cCyPjJVyPj<nyPkcNuB7fH?_{o()a_)Yv6}liO7SXcwB~*WQ@oZMr@5cg6mO*_Xzph`#k;7RH1~6$V%PJb;%(IVn)?}2@j`~;2<j}d(i!9k@=WR!&3zUqcAXcBCr~GnCy>We$C1aACsQYpCzGdBr;(?V=TK*p=a3_*bID3qkR!>i^HK3J>SoP-hAMWQ(TeSwdk?i!_mh?WMV?1pME#4rh`fZM*!7H|_yl!7S?M)$f9E~e(;0s_Bf=T;oH2<yl{}SyKZ&7u5Va>c&>1b9(Tt(E9kmm=9eE@}@d$?EHqQ8!8bs|x4k9<9wjj6QwVN;$*LTK`)Vd7C4XA<S2IOC;&B(uye`6@_NNq>%NFKvbJd-+-Jd-?wI)Xfd+?Sy^nA(OMOm6B?m!=HGjTnk+GZg>KP+W%^M6N^DsZGdDSQnk4_$QA#{=`sRnW4BULvbyJ;(FA&<a*?W)CS~+<i^xr$c@R(slSn%lUp$qx1@F?w<Hf>D4tFoLmtDqna)tWkUE3BkUXE-mpq?5k$srReodtB>Ste$qc7*uHLhTeJD79XklM(jCXHCLMx0ky4QsQ;RjJjewaK+P_thARYf$TuYmjR)6j!I}WS#R}ouRl2wK6%y84hRMXDGhOP<)Ddk$j4Lka~uEki5egi=8pp8IcUN2d$#6B(EZGp)M!KQ%^7y$5NM*W66K<dP@IfD2|{mCoktUBB=AoD#kfu7IhSP7I`vtAbB!*xHI}uyHf{}2lC%^XDIH)P~3+)j@*ablNv$pN$ziP@8|ugk>p6$S+Tlb!Yx?K;q+Qj2V30tnqnJ6aaZaPa#wOUY8bg2Ih5L#tTcoiO77r{_SDwY5OQZ~Z)ylRgt>Y%6c43_k%yAUG89jv4j~WWc&0HF&!H|R&mk|Nt{^WVZ=!A|Zz9Jq6z^duHW`YesVm6Q<c-wD<c;Jt)JU?@RphnQ4b)X+rCZ3Zdu9Ve@owq~@@{eh^*lL&oJ_q+P9|Tb{!PA2zD<2hzD<7QjEB@G)W_r}<a^Y=$$#@2_ZW(=F%(~*o+qE@7%ngrpJXUL!ccsap*W5jOIG?9*|m?vF%%!7o*_?h#xQ3ra>fH^+;zqc>UHuB@;T~hveLukbL2$oE^;DyA9XcZ>1Ogi@?PpT@?P>f>Spp4XWVkeS?VRS(j@X(@^R`h@^SJ3>N@fP@>XZecE((1ET!7XO4pOuv+Yub;$_rz<aO-xGU{sbGV%h3;_=i)<VBp9@eIYT{Znxt>S&95zg6tolNG!6YQ?U7UFl@%X!2<0noONSp2B{(&IrY>b3}0jb+yHP?kIMhS&Da1cafDIChs60q@K38&s@c)sMjs-Gg|RY>RpTbOjmrL`oQ8o_Z6p5Z;(^S4u;~3)N|yE<TKPnveJFzGvq@I#c|ZV7WaLp*mch;K0;k*ao^X9Pg0Lr-1olX3)Ccwdw)=Tje5!A-dhykquwGby+T%chx~;4ka~ywko<_D*tH)jzD&JBR(jUr-b)oHQ;%ERd#~aI>H&*;uU5R9x|OVSy~VxHD|Vd)iq|p}uc6w>N~6eY$gZ<VaWr+O#eJ43HmUn9?z2y^>r7M}L)~d{pPPzZ=c(c))F^Tk`?Q2Q*Wx~x6}!%E#nY&>$x0`Xl^PcJGk{{(GlSxx)ZZ=c=L*HWsXZ+2=Mcr6sa-7Y=NF~zsa?qJ$sMRY$Q{U`)ZZ=c=OxA6s0P{K7+lX?in~&0TinlSie1lgie1lmiYHQ+k|&Z~pM4ZBq%O0#KPxGoPF-Mef3{LQfI8md{#>Tm^?6NkIJGA^oUEQhg90tz<Vy2@`rkLZ|ETe6ss3lq|Lea@{VTAZ|MFjFuCKok8x-iJe*Z%I#`&N6CDVBITWi|?0HD*^BL'

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
