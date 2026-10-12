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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8915325eadc4f86af543daaf10702de/part_000.stl', 'relative_path': 'b8915325eadc4f86af543daaf10702de/part_000.stl', 'source_sha256': '0205b702411d4342df7837f7882c6b13c40918868fe20004ee0b0afa8001faed', 'input_faces': 760, 'input_vertices': 483, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.263088583946228, -0.4999999701976776, -0.26308855414390564], [0.2630887031555176, 0.4999997913837433, 0.2630886435508728]]}
GEOMETRY_BASE85 = 'c$}r22b2`Wy2pE1GAbEFK}QUT0!l{WC@P?WD9QpN3=%}a1r`Lwz$gYlUGO3TqB4k*b56@PNnpuw$qafi+<VoFmk0Vpef?GaYUrtL&w1xPJm2~M`oA^Z)m@>hs_WSP!L)+q9R2SGXKrF|-EB1;N8$>noHMj{=8$K4_8wd-W8jM+r<C&LpV9H{9&g*ebI2L$yi~1M@4-DYt2GW+Yucw#wHo1SeFkI>$?TEQeL!Zf-s0ciqyOOEo<F#6kAc0t<6G-Bs#_ymw|b56E8+j+zv5mNVuKFv&5^vk_uV$p@c5noUhipq^Bm>7eaCI}`{B<^D?fZgo4qOilA=2O_rHGW_niT0Dd&&%+Pf?#zz_G?yR3z$iPcN@_^%tEGg+m#eP`ZemEJ8|SoyJib@%zN>((2$+n>*9lM_pG0(`gWiKTKLr`w3#{`^Om?^Ee*KeA$<PQUK8UH<FF->#|CTfQ^8=2D%{OFNaHF)k&a&L87;_<i@O?-%C;_)f3y7t48~-!|Xje{PXextnqVeCKrTCiOf!Ud&A?$1ampdfRtBU!}iLCO4=Y-Q6X%zw>&PJ{CLk@8+U~oZOW9(DCbyIRU=w`EvePn{(S!p6AJ<I=$tGPaW0i$5h(xf1XjNsZMYC;ZReR-rcu*oBuq{sOuJ~`|Y<=Kd(PN()ZDC=Xa8SH*5Pg|9yp@tE|%7ek`N%q894;ElxSVJF$fJ>zv=}Kfg0}{_LCpKb|#zwkpRr2XFP4Z!D+ShMWN3af@wG_tkv(7XNu-MR%^s`3qmw&&SGdNy-1b>FaX>e0Toz^{U)UmD-Z>{O_Kk(uYr6+??_}hYwTfW1Ds<KVI<Tlm2=VnVY5j=#2RX)qQrVn;{zSe_YqoD>IevzVzty9G@R)^u6*U=@n+G-%+oV^_==``w7q2`PsI~pP$J7<?8v{e&XPA_535WgJk`uJ=lIE{bFtlU%gJ&b5p-9-}QWzf9iFzo>RYV-+AENc6I)h3zVPup~LBv=eh0y<vY`lr99`DX$PiVnD$`#&O4RV`J-odsrnVmYOJ2K(_pmfuZ$mF89t=y!HxZvtLJ%Y^9FytiZ0(iNtIh+?VEhYU%Gl`PJkbI^=eg)@!F$P&J*J}$XEG#xc3JC{YGnlG$SX#cj|pKL*;XEm(+Z&EvDWJrahT<lx$a)AAW1_R`q<=|K!^DtNvd0pzE(c&fy`eg8X>i5Y_JDy{=6;PvYRDCF<|(^Kz8mW0P(dv&M{Q;qwy<?>(Z9e{9jm@5lbwa$Mcd;0aIp&l7Ij>a;4aXP3XC@@t*n;rvni{6FaPoBqJ`1Bnj0U$Fg{*I%gLJv?f?zuvk7(scSO2c-D%$v<ya*X`O`_aB2V>Gr;Ew5ku0*4mG?8KeBfZI4dP@%a(bhc~CD4^Jwg@*nHh;4^>v#D-Ut?_^y1+@Ie4=3VvN;u|)7?oS^p^{4U^6$gCgPamy+m3p3T#YbkQ<fnT~`O%S^rmB2d`FF{G*vfxmlg_{K9V`D~EC23uI{&eZ#_Lns(Z%!2a{~PMFXvS|jrN_Nt^7a#OzAhAu9LF;?Im3IHFchRe!bV!dBR(tSAMv6u73VinyU7mI9x{gvD3x%eWe##m*expecJ1O<GydR)$?AzMg2WIt+?{zWnNL^mc;qS>-_nQe4VbIgY75IrmJ#^Jy%ZovBWra-FWY1<5anJUA9Ko%XHn2(hkj2zq_<?wYsl89hD#Zea<4kAFpyGPn~Dhxy61z+H|pc{)yR-sd1X|BmFz;`qQD&(v<VRQ|E+A_s5k>{OJ>Gj-68F_{XcuQm%V+sjgQYwyJT0YvnUaK8^4GaEE@Lk4;(TPjB)cBmb_If7j%{CFeQEc?x~3&J$<6kQ|3FZV2*Kd!nC9zTfHZY(L@o>iRX(R;83<-$6Q`mLGd|kRHcAe&b62brY@UtySmwt=$U0AO5N78h<-5_20Ay+jj>vR^yXoeK+q5>b>npo}8rWZTPd{%Tum<&yHC+0lpbG2BlZ!W9Bzze3GH(Ikq46=0B=jnBOGlJIr%zKfGq?9+l6|S=w*&%>i|MuBCo|8~?W<y4=65r^dq(<~?S75@Y^j`{DZIcB}Nvdy@V9lY0JR`!R1`r0%zME!{p!)>7AXs_s~+eC9)D9OABJUS#=EZ@#3`Pg<$olWuM&-EZ7CRn>?1nHBo|`9n?J56oSt>W%RuO&6+m;dZ>R%I~{Xj_LP8r_O8q=ShsYQ?+Y1)NGAEeYF1*s$Dzt%dGaNj~!jC+I3>y$hH3T&e{|D{Tte;@7JU!pE2@j{O}%qUrt(ltv|iVf1Lcsto$d^b^g5pl|KKey1E}evRajQocW>|&m?}=^G4f`dGkqi-wk(b|C%AXpPw>O^~1)u$L+=s-~O#0R}6bXjk{dhw`td=o!fr6R+^rVn0XcBia7Ht+mDRhzD-@fa)m|y`WC-)qi#>PrKR}Jyy+@^VxJ!Gn|>+ExZn1}o42WXZkYL5vi&kovwg?&RlA@+NRAH~FFIqZ&P?%3H&Xp!gmH25ea-mT_9I0$>v69c=h81F+A-d>{J1v`R`uohi(mM!n;d6az8S{``G0jDmH)PFlpk-qNA)xDArI?$8ou+(JE}fM`bE@uFTU(OHO_Jel+yFK?~1I|^<sgV=eb1(>wf8>QtJ7{t7|_|V1jPHr-rKj+4$k~^Sb>ej;{Bok3CXBx8Kp(>;387FP_)!xBmESfBJBIqH4dfYYMpj^wIMdbo(9s&^q;Z{K&Ghy8YI@Q;$E)b;*D9KAr!VmH#;Tk6HOooYwhIOs}bYr{=x-ISgN;`hmn(jDyU3(~O5KKX#$9%4cN!u4(Gn8vi7HYrJH9dt8_F&!y@9cECewe3D4ts>YAWahe%lTD}=)+J5Yr`PnJwG4ok7zqNeV^Zn_Q?`7t_wr^iI*<QT#{_|Y!2lP6H?I%3npWgJ7an|W<KV0t8&Xn}LzhbOE+J3lP;XVHJ<~{4Mero$s&rf*{j1!`)&)UB0`Tq1~oDgH(*7jY`Pf2h3Vb=9*-`P_#HzmF4Z&~NH{rI5s+k<?kO`*W^M7{GU-y2V<b&kv9E8Wjqexy^e%|X6d2eW-MehWCi8ox#6X8m2|XXw@gx*Ziz=TG{x|D*g!yRxp|x7SaSzV$vezWqLpJ#_XBm7i{Uo}L)@`iK<2?8~Y>#x5RK{fyH-@3dNHovr6zk%`%Q{)TVQ_me*7iCX6g|MHINucG%9%<-Sc?eV+rucp;i>BH9f&3Z-HI!~PQ7(ekB=W*}9QqQ}G-t79*#}>V+=TnoyIsWv~30b<|-nlI$y}j;{^u7K^eD{Z=s{fJauY7CVlJu?hF5^2byC^^W?yMZYpV&QKzwiEAuWuwwJ+j9Cwr|#BZQp4$d1H_-_22Z*>iz@zdF2Q6^D5r~{k%H1`g!*oJ<qn^JGO7$J8|#*rJkep{)$#zpnP|!es9KG>Gx*Rx8D2mepLAic+aZifcLEWeZYHG-Iw*Aja%vc;|hOz|F}Y3CtzHmjswOO>O2AC3YBkbTp{BkbslS6<apyK^>=H0W&C{OD{q|E!dFlH<2}FcAMe@zU!6zapI%SRH~zGIGyV*Z(CfSQ_}2E#_%@zZb!JL_%s82LV~?v{zLVJFbK5uL^TZ*&uAguGZ~12YA8%Diw*xcJJu_3ayZCpdQ~YpZt)8b0(BFUZ&0j3v%wL>-dY!|bAKAW{AIUsR*QfmRGIhUGd5`ogp5ae#_ir)26Wa4Z+c)#UM2lBd`P=hKnTIMrU_Ps^8!(?$`3#uPs{C5>*|?S7KY#b9_s`$e?*r!V>bV5W-&MW>=I<(<HGhwcU#YKqj{E)30=+(Ed~01I#&_L(>l>DzT;FJ2ORvva>m&)jC)?{Swr|#3BF*&o>U`@tmT%T`WL-#|Ct$ru`PO<-%zRh3)}w6StVg+gx3|~3Y~QSR$+}reyY{WK`F)phTTps+UDmDb^*!59uJ8S-*URnoL)$m&hq2$<tw^~p>yWZ;>G#dLWt?_wuYcOUS^tb2;d_y_z8Yt|5VTHf`zoK!H?G$8Q?Dn-m(Eq|BT3&{2bOhX^?U->pVi+3)}PgR1J<9_@9p(xE4_cc-Jd>Tr4L$fSNRNBZ&w<y-mZRct+&UzE>r!7J&uy^3(B{~QQ?bvykmc-uzmBLLcVvX`elFbI9x{6yP)qTD!ujHM83Z$wZ?BwH(h`8eaEqV^Bw0|=HJ#lJvLC+>wMppEZ=-rlJ8S0{{i2*RCxt_=Ti9z_|B!$S>L%L_(9+G{OSGQ_0;bJzU!&q2YlC4<sI-{PyOBct`|usJ@*@_&38$B`#WZIbT6GB(?8exhyL#QSyrn5MG^g-bb;Pyk?(t}<(u!V^4(VDBj9_kx=-tSZrt{NO!b4lBdhze=2HoCU2A?S-?f!*jXxvh^!Fe8`?!qb{OQfOG|GM!`@6jDoA2`SeLv+qeBXE4>v3qleFBzm_6fw<Ul6np!S+>p#;x`~2irIM9Av+QeZQ)_&hFCp6|nC@J%4-O1^bxt?d!07v#%qPt=GNm^|A0O*43>2Br*0?+51v#Ke;a@UGLk<x9`RBUG}|1p3wWq^6jg!e6z16X2#>zzMUxh*YfTEvHaxzpZ>>{Z|^TMzP-Ol_9-c~#?|pczim!wzYAW{-`#f?-{SY(!++EL-Q&8w=G$jw`DUM$d2ie6S3$l?Z`y&iPt5ksKC!U*UJ<Yl&F`CiXl~m@+fwfL!xCyd5IM6p#Sfc#5%ZgT`{gX(?3YWJ^$crV7o+~>+t+9LW?x^F`e^SPw0*O0Fj838M|)qQ?VEjxiH?PHQ_f@B3+tfvzDJk(YwxSHeY3AJ`kk()`SxvEzS+0w{Hf<>`SyiczS$QVXMNh<Uz#xU4{M*Q?VEk7PIo=e$hQyH^36V2*UU5QeYTcw_Swc+7q|E8#?5@f+V^YwX5Vj=`Gmc%*!Io7;yCNgcKOCxch9$<d5c~zxA#9gnTJ!)FMj)!UEqfgHmDK4$@`NR#hh|ZpB}y~;9|-@qrqFipQ-o1+5+CN!JYr#E#UP+UX}CmQ7fcF_?V-08GH<0gT4;0fk&Zj;Zg9@Xg&C8xFuQ>ZV5L*>%vXod(emAd*D9kYj7X<ZFDL8HoO`=1+RvWqIE->kHR%WT6@Da;qK@pxH~)oT?CJSr+LxBi!<JNXA{C75yD@ilJ0Ach1+?N@VL3Bv(S%V3E?*AI#@#ZW=DtcJ}-`;2hnx#L3j)L5xfPSfi{O{z->{<Ut5lazjCzBg1>?%qix{Ha5MB~xEWlT5H5vEzDsc|e86{a2hc<C0eC<9CA=TbMrXp=@D#Ki+>Y{_LI^)V`AAtlKnOQSKZ2XXjR@fh=-2QB_$(^dJIk?f2l6lz?f}n6zl7(*x#%G{7e0y}gO9=q^dOvokDy!NBk*=~2D}}fhqi_1!H=R+4<6-M`0vz>$?)Id571`t2XI5QGTacp+L4Y{>y>C_xH5I+N<z3KD)plzx*wJhE{$fx62iBjQ{XAog<A;WDrj@K3S0?o1XqH~62f)R32+^FEP56m3xA7Bo%ohx;m*{P`EX}=37QKpf%l?E;l1!FGy$K2ze10|U%@BQ?eIx>4>}Lt120A&g%`t}P^lB0I2Qhfdh!AM4V;BGgtOq<=+$s-xQwsflp%x*q6OfBu>3287Do%f#o?<6;i70UxES@XC|VLON!=<+l;#|zsZUp-Rea~K!ZoW<hfE$Sk;h8Zr$U5q5kj~;S_du<H$cb24dD0DZ{hdh?@_5+-*YUSPJLSfr^5@;z3@VKH+l-*4WB^2f=|F_(39{P_&B-;J`V3f7sI>Y1!yOD0o)Oly48_m;qRz#S@3u8IJ7oA4z7=uf$PKN(1LI|xG?I#h2fB|{)NyYa0AMtF(Et={T`kO|Ab0;{KT>FBb3oX_z`$6x*MJgZ$nSO+u%I(44em_Mvud%;lt=I_%OT`T>x)|=b#<oIdFSa%A-BU!vCU-#=-xBKSb-pAHsK`<>0&EYtX{*HE;<u1ebu*&?0aed<9w_z5>1$Z2&i*EUzVmYY@Vn(1~y-cnSIwyafIcm2&-&W8wOg^<20<{2saueh*%W=D{oB4d`ij1H1!04DWzlbSvz_E6_Rc3OEaG4`;y*P$}0291H(IS$_!s053-Gf)~T-=rwRUd^=hKz8$^}O@pt4E1*}v72vAqweYo+rSK<So@aTnkr3XAehTk|H=(b<o8Z-GH+VHX4y^%?gBzhI9nFp4e>z&%!T*F8p=01ha7Xl6xFdWU+6ul6z5#6t-vC!c?}sbGVe}a|3|B`-!`0!((Y5g7@Iv%Byb%5edV5IoKj4NTtxv)Y;j!q;@K|^i`U(6AWhp${i_g4xl@K0=#^7OaFEk4Gf*Yf?;KpzTROaUuI2JzQXk7yzf%l=K;C=7{^l5kj{07<*eghteHh~AiebIa1zVHCF4?F-KiM|bwgy*BH;rZ}h^eDU+K8(uz{4mGD<wIJ#!{y<-&=K%ma8Gm^+!G#(&W2}GmO}~QJV)y=co^j;+>0_3ZcI7lQD#y$d6dyUcpqhuhrR*7!L!ao`@(&Brg`W{cqGp*58Vsz<r(Fn<;hQZo`vvT+`q8Y?Gui!*Pp<%=%a)`rC$<$g}z9*8~u-P4f-76lZ5a(LU;@z{462diV$u}2;WZ#KSKzQCWO}#!p8~W+iBy%Pogi=zK3$(a{q67G0=;*y%>#Vq66VfxDDD0ZUa|E!*Er&Fj^2U3~zU|Zgn(E2v0+&!qeav(4p`Pa1`wZN8v}&N8m@{9%y&C2mB&B41N**42{E|!MW%*I2SG&(po5_Swi?m^al7w_yM#v`~W-{9Rv@C$DpI&G4KTR19$>Fn)rb7d=njyegKb$-$F;hZ@~l5LGS?hezY}wKYTrU1AIN4h8BX;;4gV*^6b7Ogg-^&@Tc(e=rH(s_(`-o{3P5SeFSa~cSXCwUEv|<P<ROZ2|5-21m1#fg}1;3sN+)C3lPHBp<(zs_&&51d>@>F4ul6%mKl_95ns6%@zsqYzWP(dSI3I@>R}OIT@^O<S=iKhVbd;zP1_MR?Mv9SL1EKQg{RS$g-v@GHhqGy={JN;-y)oej)tG`e*3T&p^(-tu;^e|^kaCW7q5BIAC=?x(Z9j(!>^-nz^}vo(C6TO@IC0g@ICOgXchQc_zy>`14{_+M0Y!yC4@gmXTYDsFQKo%FTp+0-f&O21Ns=;0e%YY1wRE3M_-1A!_(0(;OX!VbQin>zJ&e>UxKd*X{{X6EFpY1+7iASeirQyo3a$1&h>srFTt0%j&L(in|e_WEejV%i=k!VUmdMwI4%p9<@aUKCh#wg*3uj|fiHOeCNFLZX}t)G%HMAygd>FT5VQ&0gzF6<gr6sbUqYL~FQ5;j&ERI-=fi|>MMAiQ@3{zPc=?><ML$A#9wB@P-2;ot?+&5G;o>~UL!=Wv=;#nW;9P$0!oTu74>*^f?*T%1KPt~?KY9`WBF}t3Av}{1?oSB+jS${|UV#4#y*Z@y0(^loyqOSwj1YbijldDg>_tNOb3%A2`aJwRWww+MUQP%v^Odpi7wB;G1^5NZcsL>aI3ausS`n^DncqSPUqJ|Oq)erZH&WJ<;EnKjLijl}1CF3~q8V@ob?Z(-xE3LN2O&I&5T1+9gXdAV=AsATgVdY3gzy}6KRgG{L}$V?sVkXi3%CV&%0vgjgSbW}=gj2zYVWx{=*53KTKmGC9j&ht!cz$0&4lo8gm9&h4&jGFI)tAI=@5Q5q(k__kPhK@P|1UES1+FM;x@E8d=+{nS{**`XuXx=>Tq>_e=FJr{*R-z8pmDWbDqCa$~>g?XINDJekUQ^gAksGc7eNay@`bIWI}j4+7<p7eG2UgcjZ2xB82ZCgiHFKi*Rc%pKp3`HzE8UA?%{7U{U#<i(Um^#dCB?CoKCea^UsO<>xMZp69vVx%_<B6T;c3Jfm#%XZ)Xe=GlbsTZHhvgzyMLcsY6w{x@1Xr1czpjxwxG2=^g`r=mUJ9+cTsLU;`!ydIqlPo~V)6T+Jb;T&HX3$I1v=*RHKlyRI8ewq-jgWdt(L7CSfgi8^^D=1Sb;}w+koA3%aMhM@BwuWy-Z$ewct*Ki#5yICK!Z#Aa4-&%fqVK`)QMcYjbKo56&AWu~J7_li4%`lX3x12b(hjW#S0hjD&<EiMxkfwA*^cA(4~7bqOZ%(;#pLCGvTo?4{0}GXU#4zL^8d21_cBRtQfmKTA@$v<fcKwt*ga(S;`|STJ+h<'

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
