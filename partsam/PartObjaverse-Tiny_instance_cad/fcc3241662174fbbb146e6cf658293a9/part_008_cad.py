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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_008.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_008.stl', 'source_sha256': '6b2283c0a4785639994213eddc482c9eb6b26e66bf289deacf2712d136aca695', 'input_faces': 994, 'input_vertices': 538, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3601148724555969, 0.043865278363227844, 0.43595901131629944], [-0.35530003905296326, 0.06489130854606628, 0.468779057264328]]}
GEOMETRY_BASE85 = 'c$}r33%C~J-p1!$opdBZ%HCeb9Fjvx6c(b0<g|rND-<cBgY8t7^O@}|hb)w&!-|OH@Y>F2Z7HnOQd<X75fREa|24mR-kJY9-*<i2_vM=F|GV#=dEWb(nRn)yd8bRCUiIp?3Zg&T1`}SXp0j%IAh4xb&?>lSz_1a6&Kxkj!}%9nk_$Ge^X-r7UA<2{y3fhE;G*ENc4rM3e&(=t`{&zr8`z~?`+U2BLx+tR*8lu|Lx-I;!2HAe4;eln^oO6*|AGOb-g%#nUE1e6?$SO#D*u1{(<F>gzD=`vuZFd@<MtB{vf6CyR|jSJFMXBrgHDlOIC}2<x;mg~onOB4!>Oi&Ucc2?t(x2<@>{QZBH7;i`rHzq&y`<s%t;fn{7QV^zkKyysNAT|&p*`psXBefx|*b4d(S14vwV%Kyv3SKzi@r7?sF^OZdB)2{qbTdzx)Eea(Z7m<p+aro{-f~9^dyP-}h7g;9jZyBEPo$-0GxX-XiiV)_pNCxgF$dyHzY-pYnq>TTjkvukD%N|L08K_fzOHH`P!6#D>v+e0|}>WPADLFK?IX-}}CO<@ujvwwJH=m5b`9#;g7A{n}IiO!*p@Z!cf%EAR_@9FRJ$yszU*e&yuTtFzk6SNp=ydQm?oeK#?6+&W)*V!v&t$(il(ef#n+-^gq)U+t@Altnp5-kClRI6poQcwgUl{PG{CPsnN?`>uTje*AsGFHD_1DS5ofFYnQAO46@bpNo!j_PdTB@9X%9{X@T+l-VBNxA)%{@B8+JXWCB5YA-)N{<}whe#P2}spH@IzJ1`%ld(VTpvhVN$oKvD^Q!#9VKX!Pk?;G7&%?W{&h!gI>PN@_O+mEZXZ(>mkI63#{%KO`xOIMfoa2{Ydf4QweyT2;p6Qq0RDViV|MJy;&~L-sy5s!rrm5}VeQgK%75%@@Y%jm0ecuyO+s*shZt@FP_o&WlFJJAe#;>pQYj@r<wH@T=Km0o7SFHG>&JXT-cv6;M*=}O``{Mlg_?Q3DF;g<z<NNl7Gfth7`MF)6sq=LmjN4Z&PhTH9;vaQc>OAKCcpl|_&7<&Z+q^#^%MaSVKOw7s`6d02xHa`Xm7i}srp~W?drhWa_1K1#UwO*gkw0T)re8U|UMf#zlSXy>rE>OnHCcYu{S8y?tFAdJ`rfrpx0j!9x>2fq?K}5n_AlS}UwiSqNm=>j`~3MJn4GzN@cs5FoZd2ZJO`Kl9(|A6yp=kict8HW<CovJG`pXcyHCmN2S1)~6n=~HJb!L#zsoP*;_~#o#rgTogZW9n>g=Z?zx($!S$@UB2C4S7driy!+_z>$^P<Y1GW~ddCI9LL(Q&nCb*3L2T$cLWVDit==Z;@qlj)CYoN8YfyJ>XZSf3u3e4WSQ@#^^OxU442FWEl$!A=db`&r#2<yUsPB{PqFpQqxq$0uctH}>6l^L+}FvbLvuzdg&FFP@aSzwrJ3s+_khb$<4~Z(sH3%Ixii?~fn({&>qXpZCYJe1AM^zUuoAHhDGEuiR}->OA0mod;t7ubZT<JKp!(A$Z{RDOvgD$M=ug{_cL$`z7rU`Mf%_J$`&2(TMHCJSV;m;>Y(#Y|nD%tAF{L&&2b(-s__NnSbg$?0ubwYw!Lw)sK!7@2h|B>o}3G?XTn6`|*CM`6V?U(DlXpy1vK{o*$6jFV2tm3%-9IBEMqC&ed7{$X7q*+eLom(^Jy-*Ya!jo|62&dtcx8V9?s=`*QNhsq?n{+AA-J&bKH2nCa_ykYD-mxad58(~6obU)xQ-&j0>%HLr;0vCfa@vGTY4HtOfWA2R*QkJ32{U$2U;gPhO3AMD#C)jk;1IyxT?T~(9i>$sJ#^L$ldNlm8D@$db3zU}<ViA_^}#ktpI=8^C7#McqOf0-}&?JU1!J2T(*+fBaTZiQLTPRiOZ^8J1Zu6r>(UvhptUs6uyZzcKheSUx6?R~#}{QY=5Uao5;?K}TADeL%`?~nhgV>?XF`hLmx-!I)qmwYbQFW-;+lJ6<!J>QRiZs2{t9STDaOwUW5@Ap@E{Uf8#W!_TaGjECaWBdM@dF1;%<*yA%Ul*!>j>db{$khE;iO+qO{3?9iXUVUqo;x9{pV)W(RN}|a!|{V(21far?|DCdUV&dbzbe|!+#h*g_eb*c+pdV(bD!>g-+wTxx;m@9e6_Dw`%`NEqvPEBI?m;n_qs53y^|l@v1{r+I)4D|PiT@pKCf95?U!Ynr;i8c$HxPHyxnxZa=zvj-q*anq#x$(^0hrRPw;*`Pk8Ug)b&^AL+|T+C_nyw>Au7HI^UMJ#CP|7^8J0E_v3jTzQ6DDzUEi*{e55Dzq{}Ae*BzYzPs=9zUD3R{e54F&-o<YKJLEH`#R3!@w)py@0V;Jci&gi&+7F4^7nn-_j&w%Uy1L=>+k!#@3*JF@AJOjU;aMM`~G<F_i^#|clRA}PIrIjeSh5g`@8sa-SgOZT<&)Y@B9A!eMkJc|N1g@KKH)%W4`YXsrf_veB1f)^KJR=zS8@?y{?a%A9`Q&L;2<3{gApYm-rl4@`FY@)t%4d`#9&v_i<xaN5`jo4(5H$6XfeU65sbZKfb;@Kfdo%|L(b&_x<OVFK96}`F-)ezAy3TKG|w&R{!#Kzb3!X@%rkl_VVNV@o!c|zI%Qv-#@?gzMf0S_s?&=ul*JK?)k0v<Lf)Ve}3zI%}?a}=eOSX{g*udcYgdlU;Vh}z25iZ&AaEl-uK(nKktq6@I1u(wXbf7=1ZJcz3=mv{C?s5lJ-6CiRK&JZ<hFezvIXAI_K+tQ-1kvy{BevANeKQXGOoM$?Z_y9^d~y;{5pc3-9Z95d4zgNAOF2A923#-~Zkee{R|Q^z(n`$It)O&!}zF&s&@yUuV^i`@Kni`Rv`MCXW;E$Jbx=!}|d7_1F0&<HFZ@G8n!x+Me!rI{E&0I{Ah1UDEe)-q(E`zOD<J=gTkuY-DQwUzquQbR4?hJ-x5(Am9J)>3!c`*KvI>ysz^^?05J$bv^aIZ=b(%aQeL<=WAY35iqX%PfX1pydQs0@pWC+ywv-;FOXlg@bc90kngb~YVUr(mhb0F@`L@mr|x&Wuk*Hi9p~}=o%}1-r|yHiulu0b@0OpI?5FnD?^5%|_<HL6`1+3Te}DJBZ(n)yu*~-I<Lf(q#pv5p`^Ee5e8%~@UnuE^`-OO1!`e(u9_QZIaV}rqyLi5&{7<%;mN_o`_<f-{-$wno_d2{Ef4}fc-j~Do?{#?J_oMTbo-=qq{++iidEE0o@5krQw&|R{eaU-h`2P8r_kH{Pvp1%m+jw8|qTr0>Q9tgzBl-TlBl*Eu@21Wh-q(4f_Q_?@{&nwJc|U%x<$XQZ!uRi4mH4i`f6q$3f3M8@@%K^vyZbfo`}V<vCsNPByzjS9aMF_0b*;qbx)y(~o@?>k)%!Zn%deeyRr>pgpWo-_>a3jd<M(P-Elr;%nQwSs^NoDxrK#gt+s*shZt^RCos&M#J3l_ptDkQ9)V#&}@pHLROQLbP_cOik+xz!3z3<y=z7#*-bAJ3ia=zw8h1b7{wkP-R@pat!@p%$o_lfbm!ujz$0l#Xi*Q&GnmmmLb*d+4(`?T`?dCdFq@0<8l?tNPMdTts2E{R{c-6`qcH=Q5<&aRw1H;%9S$Nnd3KVaX~eT4Tlua>X*Qv7|nZ*i30y%$~L>->Z7->;VM-=miA-=p@v|6G5)i~E10XFC5gwbAk5-h20c+`spg6TiZ}$6n&Q_9gGbuUi=9@3{T{=*REVdSCrNS`+oJd1K@0DL>%%?uuDMGyQzuwJE=R&k@s-{R9_%5$#9rFXH<Me9e>N-=UnZ?~(lYx~%sYoge=Wi|^ml@V@U~=Lert-)ryt_cXlk`wv<*o|ctgzRzFScKc~r{mb|Lm(S>snr~NhdpYX=yfae!H}=_&RbvKZ`n8t?3zB~2^A8pGZ=ck^mZ@#JZs*o}1c5D$gI2-7{)vAoW2XI4&Hkq{gF5}M{;AA<`*r&N{!^KsazU^*T>eFUEx|vdt-cPg50^i}<tOUe1aClZU>)OJSvbhDXg#Zc<cj<!>;1_(#=nQlZ>;wl?ZoTQ>sZJ5$FTmudOxtPcnx|D>lzor<<(rY-mA0|zk+^+b&M|vm!YgTly>6t(dV;{@lRo_H9@qV)uFi}|BSYJK7E`O@|i)j-kGc`J_CIQ>l*JBE_(*idVA7Nya##@)-i4oE}O94CbSc8jNX`aj2nha1J-LmJ8^w<ebzC~ao9JcHb`(8x{P&<8wK{Ih}LUNJMl*7jabM2v<#QcSZ_1hi8n=W$~wj!!)0&Q+naXcPUudoV>}>S&St%{X(t|t9>_Yzzl6(L)>}(E;|s$<49`V>Z*^@@<Y8#5zp|b!zq0<Xe1>uBaNzaBWeaK<yk)r53zw~^4dAWd*3|m&7OcA^wO)ejqwBMdaqIB2{~9h$scjP69&L4p1RsjF+AYCHp{;gL@F8fcT@$<;+UoWR{tMdbRtav6ZcRqxeZpmby#2{7?uG6}Zt=0`W63S<i|$KqaUXOaa*K~dA4zWUe(3$kE#3#c4;hV5375a){hi$6OVF2)TYNwIesYVSLO(@r@qOs~$ZdQvd>?!y`c(L0ct7;1WZjRt5BzDke1`WKxy3c;8gh$k(Y53je~tc{+~Ni31>_ZfiT;wj;yLI!<Q9L5{*;WyBf{_I-*b^?^|PSJ-O*NSf+Fvawptq$c@MPJuY)4*hqk&PDDt6bt6v61J{4_sPEh0#=n>>Kelg_f{M~fMV*D^X9qx|44t^NkA8mXE`U=J(z7~BgV=;aRz7{?dZTt-S8O9=h5&a?=jhEP1@xCOl_)YYi<P}dwPbRncZuH&c7EeM?BCq%j^c&<Be}Vpj+~OtZC1f=IC0v%_EhD#h4tfr`#m}LiBe!@8dJ4J4&!V3txA;@^r{oqdMK2|{_!smqWHeqLF7xr`lUw{Y`fYNHtI^fu7T<%uhuq?+=&9ruzlDB_+~OK^4Y|e3(aXtbJS$wD$9taK;z!VrkXw8M`UY}~E76tY7GICPp4{TG=&|G$&p^*0w|EwM78#Ahn}c8=-avATk3b(mZsTt75%3LY<Id>L<Q8{DcO|!RPq-^Q7Civ&3C}<eAnOe3EcnOp9P~pFc~%GJiu^s=>Jhmje}}f(Em!2_XsexbMgA6TwQH`(E6`SZ=8C);ZFNAd$UmZgB(HJ5kWc6DPG>CQ%h8uJ7V+cg#~F)w3VI4-5kH20jIoF>Ltn;N#HXQ8V=Ur+=ze50?i?-$;vGnC@iFLQ$Spn|eLT6vC!<d$xA-{papV^FM)xMS_yF_)<Q8{EcP688+o0}Ug*q=!ZgB^62Xc!KM;}gZ@zLm`$t^w%eHgjLyQ6m}w|E=$Hslt!MYkoRvCTu<;I$#Qcn9<j<Q8{BcO$pBJGwi$#a+=|$t~U<y*;_bTcNiix40>~DH)AhhTnm!!sT4*_ypgFwmLJx|3q6Im*4}@RtF{cw;<A1o8*c-18wz>1g}C{ZJH~xWi{QBjK)3CW$;yK<D1Yokz0H*`eJg6H%4zvZsS*ih&P6RLmOA4s~L;<8T2#c7F)(u)Ryo*WM2mNKpS6#zKGo7v(RUeTigiUh`i!wgGgI_1%4DZ?@@BU0#8CuBDZ)MdKqIdekoi!lD{Ll#b=<;Ah-B%^x@<dH$XQaxAD_K#0}tQ(Z-jeFD1A55%eSE7Qcjki7^;=%0+r9+!1X&5<QaK;xo}_l3Uym-H^P-(}Rc`!cU`(tI$>C7EeY`CbxJgdMRTtJ}ejMTrT2HXyY5vH<H`<AMlOvnP}q{=oaKPemRJ^1w0*XJQY2a+~R5IY2+4L#>v#B{N0tgNN<vh_%O8bz36+%E503lJGsRNpbsFg@wy=51K^j@#?PUjBe!@ZdL_BVmT?+22cI3*$H@N}xy3J_Um&;marEQl7N3JYhrHs(=*Hw0{~kp8cXEq2%0=4h%Am++qt7Oz@f~4(kH345+~UvBpOIVq68a@_i*H8XOm6YM=zYm8Zia5gSi}dRt!@P00h@OR8BI?Mm#^@?BDZ)EdJ(zBv(dB3Z9E2^4d0A5J`#N-xy1*g4<@(xa`ffo6;DG?Bct&L;qo2ccjOkYM6V>bcpiEld5xcd=fPvp#+RZmCAWAmdN8@gx1w()xA+6}2V^w<C|p+KttPklSM;ys7B4_AAg}S0@B;V=wDBnPC~}L>L!U=(@m=V<$SwW|{Sg_BKMa=@cq_;)UWHyoZt>^n&&eyEfSy2Z@nz`C$Sod%9zt&MZRp#`eI7aQ!uybnrk@U%g?J0eEnbXXOm5?U!;9h1(Z&y;A0W557rGa@#fP8|A-8xmdNg^5kn=XYr^#sg&Tx4j?|pKM=c4D5SNt;iWpayeLEl1daTjzKa*Lazo0D5yjxHzfA><s5cPAN5+dOnU-gt70XQF44TRaXuj@-tB;BoLRXyYd6Cgc{|ytoUsd9KJ!8Ans{iqA!#OGab+`EsXlsYh*|;1khSdnWh=wABd-u9u6n)tNz&pARB!^@#+ZfVSEr!8@X@HcN0TbSp9%SA@%Wyz%4~Z$NJ#xA^E>q^-UX6!~hj)p`j&3Vjq~5wB+)>&Y!1haN|6aRs`9jK=qe{XCkBJgeh_BEO5ax*;g?*J!IpC-__Rw~R$xi>@WN_#N~+j7409wmL2-^8M)h$!pxOEW8evMV{41b46}~w)$?a$j#7Jzs?o8Ioj&Cxgs}3TdmC%xiQ-6JGmk^LR+oM6}ch0A$g4-440?EW%IJAwkj*~CupmimKFIMwAD?@iu^s=YKyWW{|9Y#<FX=ujJDdctjH75RyQjv@`LCH$!pv{+y@hb$g}zs?E=PSUcgvP9|H&QH)!K)(AO{)ac^{Q#v=YRh_uy@b47j<ZFOR<$o<j%mDk1*^3MF-&WuHT68a>@AfAP`dQ7g!^%+Nfa*JOKB5k#IuE>8wTm3V^?a=KQi+FSN=45=5^H6iV=HwRlME4}OcmjF?V-e3p&txp(C(u@3OmGi$55^*HhHge~aXoZBG8(@ZE`PCOfVzEx|Aw~OH^JMWt!|g#4}wTr{W!rlp{?GU;PcT|FG%nWXsfp+_&v1MPvF<XWs6+oS^Z0bPe7kQZgE?5TXKuv2_kLvg9KlPzK-1DA?P9G7GH_JlHB6g(XTTG<JZEaRW9<ZZjs>Q(8rP6cq{lgxGmcFtsv4?-%0Q_=xfMrd@g(qJOpig1^Nndi(f;(#u$w4ov2N7k!Q74g8QKRkXO7VdP{PP-v}aY^{oV7g}#cs;&agFkXt+oJ&N4oSJAIB2IE4wY?g~WtD7eHSoE>v7Pm&XCb#&_AktRfNbuF@tH~`MgdRk0@o4mDa*GS-0%I`#SGa7Ri#)5F!N<eq9Z&Af;5O(s<QBgjMB3_`3BDG6ExE;m(SyltTnP_`N24prI+|L5-wl_obCI_-dBrE9Pb9baujs#$Tl{_yX{&E1_(t@N<QAWYK99WO>(SSfTl_BiUB+PiVYuXTk!N-51fPUHiQM9C(c6++{812TtM4cH7W6IT77s-aCAauy^v&cJe~A8&F&NJcmz{EvXEmSTlhG%WTf75$2Xc#N2a&e=QG#zr-%f7vh3E^(ExrSN2f4*_(Q_Gt@uF~PpNl-JJ0<uu^l9W4?~LA=+~UuJNL!tq;JeUwky|_*J)GR)G3YVm7B50CVhqOr370){k!Q7ig8QNSkz2egdRKCb=LeCt`gwxyLEl4e@ksPYavMJckA%mdA0q1*>LPeaxa^&aJga*qxIel-xy8GqcPF=aVGwDn^Ar34`T=r_|AGDodBtPVW63REf?mQHjK2w&y>gLfb?*dMpex8N-VMDQxy4@vk+!-p!S|x?CAat@^hM+rKa75u+~RN0-!KN_#o^K+7kO6qO7Q9E)5&eT3w%1f8`}7bAktR9O7Pw2yU8scfgV9_@q_3G$t_-tUd$Mb=Y>nVT;y5pkl<6$r;t~?BYH=2i~k)&+Ugex{wMmM<Q5M@4<onuPV}AR7SBV^V+_VN54CymJZifH_eJ+5w|G1BcH|b@ym&|IzY}~b`c`s_FF;>FZt-pC+sG~c1pNtPFy10uwhosj)GZUdE86OI2`)!l?ULXl&{hvl@Ih#+`zCl7wAF3lKD}~ft?K=E{|k!ZAA5%-Nc|5f{F>?4@sn$I=ol1V&hOK!LEU@HW#NBzqQ27Jpbq{EdQ;4P'

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
