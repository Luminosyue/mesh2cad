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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0d1d771d8014c919d307d63ffd24907/part_007.stl', 'relative_path': 'f0d1d771d8014c919d307d63ffd24907/part_007.stl', 'source_sha256': 'b3a97ae87016b0a5f285f32bf37106bc741057cfaeda3335a1ba8cbc43fed1a0', 'input_faces': 616, 'input_vertices': 430, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08114098012447357, -0.32272228598594666, 0.003783121705055237], [0.12513402104377747, -0.12414900958538055, 0.11929285526275635]]}
GEOMETRY_BASE85 = 'c$}r2349LM_x~p(wN_(k1@-laC1Q=G_GRpQQA?@q2@-;Yh6J&VSb|t8cCkE3NFw&wQ(>g2wn`S&RxN31by4a|tCaf9x#u%6^SJ-l>;L-w(${(2&w0<8Gxwf*=RWgHqJ4W7_AICHPgNx}bc&K)OA%I5DW^mRg-;C`9W<qW*yI@=inrkOW45c`9oW0?5Dz6%ndvtsXv*ktzm^Wa*1^sF>N@;_CxuT94-6YQDSS*2@h*WArvw>%%DBMEL55$eN#lUJj>i6V9kU((%b(&#7xa{~hfW!-tJuI?YL$CGrL>dr6Q>RmS9hHe+&T0~4z=2|A5vsoIglmdwe&2(wa`a`>$4svNx8oLu(<AVUGV&keZ_UP*!xK`u4L{I@yh9wf;*08a-NX0DKf4_<%s_1XEFs>=4WvHh3iQ&uCCoL@~bzFaGqyr96zvYf|NJ<{)otPH=XOYCx`Pa+vAdPrFo5`BF}5Pd0fMXF`qOiMaK2JkGcQFcG=@sj!u&D{r5!wwc3eX=i-gHZi6FTQhue~Q7d=kjO6~0sppb$rSn*hpSP6rq|M|yXI0!H<9bYuV}h?=z`XE7ab11sIG2oTC%SNbK9A&i=|1AJb$!0Vu|BnX69w1n-^dp27gbVZTnVUiNaXqN1RhtNo6OIBmMG)u(zZOme~!0ZSC9KWNyfF~$z1=pM)9~-|H%1YAGKA+^=Y@oc=gIozV5AzJP{uk?2_{1T{*t<KwekF@9?~Q`)|CAt4qd<`s<-R_`36>ML*Rt*HffC`K+j?5~uRI^7Z8WvGq2|xPI-1$ggf}%XvC+9(~`BNiwdc?Be@9r6uR_s&m;kUU!c1Dt<opc}M&!+>BrH{Gjkt&ha`gzB^vV)i!f^eI9xsxO#3L&tvx}mz00omh*pmM{vigXkPyx4A>y!YC!+vVqCXw3!a}G&-L-%kRs*BR_v2;_3V`cGOktmmG|f8*AMc2w~6C(*Ck1Li7Q<H=_dr&|5?k|y>i1P<68Ked_P{;!Fej|7VA)Z#}zN*YNKdgZ|lRjZoT|@Ui`MlOL^0I9DgX7>vsNaURPCWWr+H}@$Ny}{36dQ9C;M~uH2smOL;%po4#Jg)ooE?UbK<TnP2tb`!ww?=Lu_a(7JBT`|A}RJ(1VXhmCn$_a9yo{XbZk>lV?7`?;)^$gla-&aiTI`U4TKcHYnXQbrZqd@0ovw#vAcc7^xh)0KI?lw^*d_$XP%)wH;M(s<v(=~8~Jz37i}_HFLxqV0U$=yi!QuKNuU`=nCxOuC3W@;UEsdvh|lZaW2cRNKJ&*yFA1rF{8ZF)zyB^99ep)tl$5`zVn|A3l!rPY)J#(~ei-&+BP{g6qG9aQ(+8a{bo~5#0GzP455CiR)$Dysmz&Gha7;F6Vii!u@&LCf&N;%slSAAWz)@!PWEMaX-KRg!|vD9`_&nt<tab1{qg>3p#G)`imD|h~wS*iaM*Kt8zchec(0Uco|p1kMR18c$>#NGlk<fmQR-QqSw-7T#sM3Pa3bP=`yZV%{XM`1?zB3#{?Nywie^{+~Upw>v)yhV?`a*KHm$j%{X?E*U#F+Hhy!_m!ch8h}Yru4CX1D_`dd0KNj)#4-4)bn<?^W$A<I%^ZWo`w|r%OKKZiL$6WtJ&hz_xu|D+%A-ta3xdhMuE=F8ek9xv+j<w+YBdTAv#e4f6u&xu6>j4!GSm#~a7`aBq^|ifuKkQQWfNkDe=B}4<eaLcNKfOyIu+_QJF}^SQc^|ON*M>=HGOjM)v`@-M&q|kZEu<lTzIep%7yiyEd|wagvP#DF{crKS_{IsY%v1RDde(TswQd~*&%gK+&wGu>T(^sr1$Wi-<?Ht7u}aDhy~%mX7vFEYe-Zx*H{*Sa?6=L!_zSCKT&?;y_s8FBzwN&3Gjy$ttEKDmJl6BvZ>xXSf6`=JpR;wJH2%cSbQ#xtmmaqAf_YEBzeUE?b}huZbuN0g&wAgf!T*Rl<iGim;A)>(Ugwn;2<~`)4)Z!&d4JonU2tcyPxkWt6T<WU#l@8}u7!qi{I3fIS7$8X`!w%5=l}7@9^vnHT(;(Ug?|_-;$4v|_t@qu<in3-T)EN57Oxb?zP<O#N-0PF{MpO**yi_6r8P3H-kBxlH@|YP-C`a7^?;veR^8`uE$~be^Hp;+*XMj@tc<HG{@``k#B-;JJ6id&HQt?@`CTV(q>BEG#r|-#L!6B34IX7!xf;XIx5|NUm&v&9m2Jzf_8rFYyUxbSc)@s2r6-HHIm!jmpCU&xMSUs_5M2Fcu~=8ign@$VfBFb+?$7G+rzgZZIe&A9h<hHxpUb!J39c-02=4Hi#m`rV{}J5Lq+gP#|K(r!`8-Jx`JENQ6GZ-wL-VX$tCZjp@ypBexKdv5br;WP{tKSRYGf?4a&5(2=AVySVCDLV!Psxx%$IWHS4(wSBm8GvALZ$ilVV&G?yMI62dK}NeFay01PShVbeuoGlHL+rYws(#>bXeNN4Z-_aMxx3I5FNTQG9=udK@9;SBr3-+@O_$|9XqR_nr7OLdNynVjMqt@KSNzr1$b{@owCVS2jBqi+WCY1JBQ2N65H(r6`a0R8EZWf8WUQf7V-Q<<4(rF@F|1-OBa<zGutt&dvP#!k{VbEcI8NVLYxa+XdI(Tgv-h>?pw<F9uB$@jsjt_19BB;P{`z#q}LC7xVM{>|pNyjtNmB{`PdPbAIbdGOmvf<@&7IFjwTuyutN9|2#~rpQQ28;&|a6c~<V~zfP<#SN9@3-T{?Gel06ga3uhBThKS!%ALMZ%pEnttz2K!+m=U9s=Qd-ua4!Pi1jx7eg0gV6C&<=^<l^v5x=vG*k|&+y~Vz(CA4I|%vbozs$ax$t$KOpB^}~?rCRrOqU~IYx&D{9kF>Q<nU7p}R$O;x3Em&>PvqzKC=cFGs#g<SJu_W!N3B@yXUc5xy-7KBil5WFEf@2so@>qb`|2<Fxv7pzTvzKiOmNqX;ru+_x-s|X>UB-VRqrs4-*<nbtq!&8Zx(e}yGOLnYFr1c^<we<#1ZAq?}2Wu;LpvI19<(Et1GyxCf3QsVUuKB8#__N=hvAaxZ~k9-X}LN=Q=D~$K$?mHOIEz+<3uyYx{utHq7sobK8aQ>9I{*_uGzn);#Xq%#;6__cq(SoLeY9Uz`I21b2?~xNObi&dof|=FJ7y!#8mJ*ul{@?mwOR?oQ!WuCDEF&+o>~{QBXc%<;LSk8$z$@pw;upH%BDp0A&#i1~H|mUCIhrS#gpPsY`}DF>zTV=D0by1R`9FZjODY41K6*V1PllyTL!j>zNK_?6&}603Q>4*K$Q`y2mo|D)G3pXL(zm1AWRtm{*+Q9{hGn)h9T_5M;u4&(1B!B6=6+2<vBJ)b)(?ssMFH2&W2*MfPa`QrVOb8AMTE&s9ab_yPTPH-(@5AT!Zj$l1pOtjv2dSpCbH}kPAkJ*36uL1mfgLhIdTI==--yD5V%KvK0^-t}<@54GZ<o>6IuaR-JTDs_u<7bcU*70fyo5i@)>dkCiot((?Sabo`wHMb-YjvON^>67NqQ(BEHHz3N<LZDCqW}4yRJCy>WIN}No4Ug`U*9|t-*X)vo0%8-PRzR=n9T8~_SpF>h2N7Ww-ev{^?QXl|Aj%k&Z2rUpMRCt&ld^edxY!t5Pnb4yuB^Ix-XjJk1$tbpNa1y&V_l&)_&@*kKuXwx)8tbY_yf<J-|=Qi|hPrDYkLp{!%?#b9}u{+@E?e{Jmyv?Nrg8^USjL$2qj6;QBlVk1Kd_f{bgQcI5l0Str5sv%Iow{eQekaHYXEo|hvt`F(he%QkMVL*>a$!PRm-xemF9#k{ySJrUfISSriff3;EyucL??B3{W1;P{!j%me+opVOD|K5+Sk;Q4=@)UD&yzVzVli^FT%`lFsJEO`E=M1Bq|(w_JEQ(nAJywA_cx)#LGCp$}Uo-WsNtXx@LT5!k64tZ9tEqGIKy<)e^GVTg~VT)HHD{y~8PwUn?tIjHdD~~$y^U}xd_;a~IIP<W4UT?>v`2BXRsobBQ_4sqs=P-Yd{%Ij!cUC`+Z{p4G$8N@OKfm_BWUG%GSK<~PlyU8LD_$pAE4glWxj$N){UT5PmW_PfA--AGc~`%`!12c~>DGC7K6rhX7}ww4ws}-m`w8y&y)4JaJr(s)TDKEi|8M}WlM4}iA6*~JdHxt+?@z@%!JYf6bDnvV`S+wPy?2W|Ezh44{DV}!UtUxZT&;SEdCYTh-TaNM1kd+wnq{r0@^Bo-xBo-8j#vL}yx>aW1CdAdDa7~b^FKKLkG5IX{;S)H?-6yo+b+x6e>GyL;Q49Yxc>v=M1CzWS#Za^Qp_K&<NQ7uf@|}hitFk*^*Mj(6U<lt$^Ge{#`W>^+AFTxwe)H0xLlKt?d5r>a@yKYmru6f`qM@{-gCqG{w<x$Jhtj-YyXw(Tg)9{9KYiM@1KVPxZeLZ<ar;{i}#a>o$TCv9w@Sl_aXB=+nKNg8Q1e$AGLB<^bUUh`C-%=DS!J=hLsmQUya%pE#=pmW?H$nYZ~)$KZHwpnYJgbT=|Cg2c>rF$x^;}v@O2i`Ou9QeBW{7`Ooj?$haD~Ia|iHx%V&0`l;{Vd`UK5{m&)5Z&W#GuiKm$+kWEC&Hdz+c+8jbD3#y0MXu-ZK8c+#<7&&wnO3e|ua<4)`qH!fd#a-R`xhlPYK@Gm_4j4i_#Hey`-DWuxVE9fNh^28^vag;{Hc|*t@*X!OZ@)(^bXs)b?0UsOs=fxX<JvXaLkv<wc<sjJb%uxJQ-KM;`jOP+&KWhmv`f?zuwNa&aXQ+=l7L(b6kfP@q44<aoo?xw_;>mE8;p~<EtiSTe<2xm%m>&#{HOde2t73e18FV1kJFmD|c?LACs$twq?t>YYV>@GV^Oe>6~ZMM*IA_@q)U!@q)U!$D4HnSG?Y}?Mtt4+@~hjB1=lS{xmF4#vQwR=1Sui)z6V}SO3}BvT>Q*eOv|c=KlO+#3{jDQTF>3T+7R{-ADShOu_Y=QTF}cjTh`cZoFXsagR6q1Mc+bWB<Hx;|2Sk$$u{;<@)u=JQ>##N9M}7tKYjh()_1C&6bVJ<nH4th{w3pF`l~MY9CwO+<C!spc^lE4s?%q%WuA)bk9@pKGQ8vLA+ZYM}_HmvOFet&r=ZZ-k<fOa;5zNf2BWWynEf0{yEb6fWJ~7GoJGFwf!}uXV{<y&dNrJVa1ekN^qd%Paz4?kJ-xq6f&gA|JR>FHf`AS|N5tpvyDE?G;D=oYYdwWy^7YbVIL{<D@oSGCO{LL2%mI)!x|aZ6fOC_hP8zzuEHnX5}f?n&@FLJeXzITlip%jvSFLhlAmhW5@_NJ;ggO9CqDr?7UygM+Y6ucR>O80mWY=8U8uz}@MYknmqHVBK`+HQTfz3gCtcCQSQ>`aL`!}dXlg51j@5#Z_JvhNOeOfFs~``ZSHdtaFfVZPIQa^U^fiTzbiTsog&aS?FM)nl#Cg>{=v|93CuqrU08OnQv=3r@;8%t@5aWmVmatZawF7GfM!E(3R?uysRm7|C+rlWO1338|(Gu%o@kw`uPx@W>q<cY|tQ+FGAus9f@cV*w1M3Uj2i6Tadcp5%>34VZi~8K$u=Z#h!$?;{TOGOuw0W#L>fF$<);O;Q{KjDIp=*NIz?!HDT??H2X3({8ZbPs(@JV-qCe|5#8(gO~{Oaf{&0%>DUI#S)<)Dd`g-_ZWnpkQ0q~Ah(Iggj?iCAyLdgA(>p*z8Ppf5e4JHhXPdYiTG0PBHy?}0fdJ>OXF(X=n4B|j886nkDA{CSqRIQY?sS&MV&_*`gWE8&x#15Io>eDgTz$uQC(XlFssg1_A22g685!DeCKi-o56(TJntVYuF8^l>g&D16cb;hUP;L58)4Pr40!(yhSB9{}A7IR=7Fgim^vrG9T1b5PQ-*9|KLO{@^K$;dAZP3>zqrzG@i;LnYm|0?X0CL{iv!uG<j8(=RijPl<GFN9-cw-A2|{%zP_hFyiGc=Er6e--h!!LB0yJD7(N|2-IKlaWv3^}x8_L>&3WVIJWBflvAyT#v5xHS{-@et(T?6++(9s4>;Atih`oRvIn&RneA*t_ocPZ3XBW(Dh)X{S9jY-ycT&O&IAnV3g~1u<{mG7M!dEcv)zZd0Fy!S@M%E0wY~m;g7;1(1pQ^!AfB4UeG2h3;qtqV~&gb9)?wd_Q!QALHmJ|-w~QvL-^+Lj>yvkdMMh?(4FBowD?XK>25I6jbWV;KN@j#yf^%AXvwF&pc!;GoZAe#JvjOAK@)2S-#q@F@^b$n9fEc+^kDeyEWWwFksbsi-3B%o@nMLg<L?_b-mv~?$)BX~bL9KrE#Z?^!O8CjO{^(=^LRhxnFKu!Z7=9v@S9rvAQ<VcFw%`+y%0YNadf<aVf5%<2QB&4FwO?xZQ$2IeH*}U2HhU#GyrQ1pEUj3rneOOXIP5j37>Qs=%Q%LAkOp)q4k6=1a1D1eho&t6wDL(%i$O?Z{(-k|1rz~<^U&M9om6@lmV*?pR^A&vF7m2<36~q502Hc_-5aHz{|lWy;<Ssau-_iQw&=SO?)YQ(hI=J-v~`?2hQ7wb~E&NV{<XS&MA}8lK;M8bD)VYf=_w|IQg>-3jzxQpMmqq9|#s?VdKEZ!JlRE`@=|w!AM8L#v#5R;^=sYVec6>2`%{p44Vy2d?9?&QQ+hULlc_|pY#N1VlnVZe+W%%Ff_3b;FBH%J{UPBfDM2@2-ge-TWQ!<!&adse=Wwj5<D9ID%5u+{5jAwaL!7wMes>)Q}}yh0$TESEBsuw4LlY;>6PH*CqWZS!+A+)w?TJOc)#e1mi&>11wa#T1fO(GaPlh})&Z;ocuky7{s&+kEUXE56ZjP^es@?C+&i_P%fXr;zB%IP_<6&=GVD{d<X?fN_Mzq2Wf<xI!oEVxL&V>Q<r#JtEYHGn!S6!<0?RS%C$Jo_pP(<nNS`+B6#UaL;-8?+h5iKkEUx<*bS`|8U%@f5V}>0^4UU0bf&Uqf5vO+qd*JVa5#I?TeH86^=%dh7%Lk|<)o+?%!xVl-7zRHQn%W_jWAv=i1$qelVPGvR$EO-L1~HNFhro#UK}&oCbRc*j{2166#B4x(JlaLj@zC4R()AXiU4&Tk*e2K_#E{KU_?^!*X!G1@%FFjd#Ob?FEPV6367kV6(oWbk)NBScv1Igvt{;JM()gyskHHwzp{YFpy&iEfVCyZM{Qc0>u0t&OAHvpyuS3i}v?rjc{n(-}!2cNf3)oG=u7lmQus^}CL*GN|Y3zT+Jh=T6vCnXfxEV+69mF>EU|ke`G3aN?%Ul#Q8gWfwjSL%u<Bh<^AkNf*hE2!uK(GL4Voqq2ksk^jigW#O{6~eg6Mg`4{H*Y?0O*^j*UzZOO=z+&5qkleSR;(VJbn=|KSJLD&xC&w`Xn^9*@(Lcoei#|O^2rTAhZshg*F}Qk@O+(L-5V}?jT~e;~25S(8QAAo5x9?fssCk_6YP5_{kRka~SCi80l2l5ybDsu~bW6&tSY%p92`vN$5<}@r1?S56cAq5_59`_4LQQ*Ty;^HWHfH2oLs2PlP5G0iU!6O)M5Z>6zdf>?5$T;H2llpNZr1phKZopbbTw>2E>%5%d=5JuuRnU?1W7vG6sl`%vVYh}<L5I-x_M&0|i~<sICEqhO>X(N2S&27ipjUxs!$^m6#qVbc)50>`FfT${l*gPX_6kB5=og?2aeZupdAC;UBV$xpS!rCN?{L7mdT(hyI2Bm7O!De%dX5tjmOGV+sPq_@LJZ-AvB-v+cx4O;@A^m^ze(A(i}ho1l=y$(itF>F1~jlnTuYYbbB^IXW40Oo>@gFhc^HQ0RU1+dk~w-7$*Z8(SG6EXg6XkE}dP@_b&NzkdN<qovT&@RMmM_s5^v9OJp7jtdVx@h9T>y_4N5fA>{X@d40=%>a#|Bu4QsV!=W{Rf|A&k*wjM*43UY0B{!{!_%<!+B#B{`{uT?J3a2BA|(d!zVogn%Hpoq~C=m))zkMp5WvMLK8Eez0Bi*$Xm}CSAD}C8G0x*v0>0ABfl;*wSOplPJL)H;=e0wbqxJ0SRId-jQrtX)Q&(L`L$tnz(*h^0_{}j2xxPzr(*u8odUfSdI>BX>%4DIk3!`N|G)lMH7|c?UsP=W;~Muf?Z4Kwo>|IYdHGA;zCFF@J&01s_>U%iCp|$c{{y!5cpv'

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
