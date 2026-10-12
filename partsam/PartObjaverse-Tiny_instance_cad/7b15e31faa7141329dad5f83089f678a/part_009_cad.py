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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_009.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_009.stl', 'source_sha256': 'fe6075cce63ff8b6ce4dbb4b0e8b9da537bfae7021ede9176d1b7ce2cb9fb465', 'input_faces': 654, 'input_vertices': 423, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18207795917987823, -0.09321722388267517, -0.4321448802947998], [0.014341899193823338, -0.0034890174865722656, 0.21208886802196503]]}
GEOMETRY_BASE85 = 'c$}r22XGX}wuVO{W3my5yhMQ{vJ4m#mYfX8B$HX9$Vud22Cz-W1d~Ksz<>xQ$RI=zECNN0F*%zB+Zba^y7-dCozv%^+3CK#s#ovfI`x10)qDC(PfvI6uFB!9GGxrJ@xPMV#i)DJ%a_+QiX2*gZCwA+V+Qr@A6aSm$ccVh9^unJQ<t{s*gCw6pEgdL9MrFWWZ%(2wH-lq2Gj})bp#C<F?!7C-oty17~QWw`AvHdjqGpukpp{=>~H*BKCD{xP)GF&p^mAJ|Kq>xMhWf?ZIX`}>P&YY5L#%_d7))nv45ns@U?<tFG~LWmcsWmh&^lf^<lST?Rnh)G-E&HVXQrm>3d$^kG1E~^H$;f4d+VrIPQe9udU#Ee&sx-um8MMs>f<?);aCs8KH&C%l*Q4w=d1@o9+<4JLdtut}HpF{Lb)mqP;UZGv|pI%=Jv|d|CWFA%m31%<pQUah?r}xc%>ZU7kX3lSKPoYo+TleZ6wj0jZw*FS-4<1-bqFTBpVJmi|ZhTE;lhuU@*g@SXGi#d$95ldj8K@1~UB6Zf;I)3NnB=P%Mhs?(MG8v9pVQoo+@SA_3@@7Xo(qTScG^^oe<yqDPjcO<uO-bIX?JMbLmnL1h2>Ahc1<k$MebHC0o(Oz%z;Z^bbHE~jYuj7oU-&;3EYH#M(ZtdXl!ToX_{zT;0!#8rC8`F8-7H-J?lhvGO$UOF2c1;tnPgu!$vRCGD-sTd%cl84H&(!64QXr40(^F>_=h+*~^~`XJ{O++cxL?O9sbA-=soZ||g;<`)-9&!<z*ruinNRnN{%Q^uzWe1sZeJ)Jb><fRI&*a4_IR#6)y@mwakn-5b${XKu|XfsAKQ}aY4A?u_e@`(BD8o5_Pra0uSIVczUxsF_V2vl_RB|dJ=cSI9C|k6aTxN`RlBbr*ueAf%n-SKrzTwg{k0;$b7v6OS*{_EbEVN-XZ~`0y>kX}J?U|xz5C<L+<t2oo}VMr_<DD|NfiEXZTNa`Zx-zxpZ;6;`n?e%k8^$kUsvT{x&7yPgs-oClVtau<qqr<{guiko@cN7Dz{${z}Hn{ALq|@Mfh69gFHUZJi^yIoZ$9DJ8{34o{RkMBgffK*F}E4eo0<0{yD;RPU_0@|MG-uqTkZXIREQjT<05q(cUqCDc2dlK;-fC=XKE2eG&WF`tf}U7%B32*3IPnITL>nKPR3OKYKIJ;CgNq<a%x&;@9tu<bE$y5dFFe6-c)G`q}f`@46uN+YRIP?aT0ei5(>Rb$9E}?E{vGe%%coaJ$ex+)rXx&T~J8{g9fh88(Xcu6Hl^^{=b5w(lp}d!vtupB=f%aGuj^Vnm*xGbhFGo0i}_ckT$^IVDE;uDAfc-niQ$zc%U-|Ln-m`R9dkJ!Npe`()uf{USvk-Tx8ix$st~b6^Rs^XO*rvzB&EsHg0B9{=I*#5g#sUFF}G(nTJvGr!)miR;xnR_1#0@8foDj<en`vse6n%P%Ly^*%bp{f_L-e#S$>_Xfpsp3BGhdZQk5oiF&hwXddfJ%LZI*?s*%CY}!u&vX0QTeyAhOd`K$k01ZsdO6pd6vh4S+9CRN?*Ep3tUub(yL{g_OyvA;@{9J)b$Pk&eS@Ieg|DqSe1gZz#r;fuwM+c`X&K>bl{>S4YQS#c=SxozuV2xL^R#cn^)%1G{khw)UY*PN>v?&6wl&2#B#ZpcuUm5d1=YFzp&vzlXW54$zbCo~w|D))^+a~%@qd<?{bdiNdbAP$h~MjNTkp2#cTV`5`&oBzw{%_Y?r{5+L$`}@|8tbc;|;mYzfVgPz82V0_>M~{?DuLad{4X8-0#ypoac4%9YUAX6280dRvuTJuk_`v>mtv^wNk%M=MK&jKA-c)*VrojX~lS)<L2^poaJ+oKC!jP<LvS!x3AGe^lRJz9=8h9*{?cN<nabPJ1*+UFpldn&l{cVUAOz@^?DAi;ygpfuz#n3$fMtD%HuG0sC>Pjjby)b7xw$y5bd>>UeT{-a0|{exsmYQ!#a!hu4AF>uknu-`o&Yx-nptI=V`s1+lM#d@rf+J{_#6pPus#=XLu-&)93}f|Aw#O>pI21x5h2w*TVPY%#|RGL#wfTU;Y^HvFFhmMGIelJi;U830}<OUtx&Ho=3m>h48)KWQn)u(L1gbzRQ&{-k!%fO6T@f{Nn9-oQ~mKr(Wuy`1wIN=Sl0u{eD(L_}WH3-|B5gNxoh%n)mk(!#ID*q6h8s&{KVm<m+*KPS9(8#p8B?*LOW>w-{$fk>{!PZN4@?@;h-oX<?GDAHVDtdAs*Yk=idQwp#c%RwYaRo8Om;{w^mZ$@!nn6@GDl;d`U%A%6y*&p(t-ll)o9n?#+j`=r`^t!On-kNcl_DU#pf+$vFj&Xi=ykBM3$@??D?^{Y*2JX`o}s|ermdphqEZ}y3K>mI&4Rq{(t+brrV_IHZi*E{{XLG-()pyX@uVQWSHl=jJzU-s=Xktbn_-0y&F-v~e3kwo%6@hR+oAHPNTKi5dJ`}*kVJU)TrQl<9oPOTU9=Ubm5`Mp0D<Kqavo-Fxua`E_-%_#fjLuUyc+DO!?FJJQB@v(emd`w>*AFI7GK9;YHkL4@lqfea1`7_QC^*Fj8OO^bzCZZnq2X9j(|J^pOCv!Q;*K#GS5$*T)O_ux#b45Mwz<EiMpSjFJk*`-8*E7BX`(K_D>#e)*gEYyX&_(!;OF2(T{<2QI9!BJp+bj3o@~6Gx`(C$Gs@+%TgXQn<DV`UHduoc5N0}#<U$a(}@Y^0vmV9OYSpG&$JnxQ{za>e&GOsMZ`M5cx9{<8}dv(5<{>U3+L_H^)$>SV&d!+E!M+n~;{x3fN_2PZXJ$FT_<Yx^O<LOwDCr$FV<rTjBe5l;MU29$sy_;qK@KbTU-aoo0Nq*|MMZ)iXLH2VF7QSoMW4X?w31S?)n+J*Zt|fQb52z;gU)QZnr|iBSag5J1hssL6_W0H)QUBJkM9J5d4He@&qXVxe#iL^0_gt91I?r952FJYbc`<$Ud2#pK#plHhUAKvG?(j6#?rT*mi|5q4uu+=i2S$s1!5gt6QSv*#`by;Ac#rEZUybt@YR}Kt_K-BYuRSQt{Z9Qt_G4~+Ei`XWDUX((K3(LS9K+)lRi4k&*x#KaJM#W+`Z4_ZgMOtw@5`T*;(A`Ba{J>ElJ8mj8^2#p>MOUe8_nzI{S=;8@U^D*d44``kS6)xjanf5vz|oBKRHocm$ykR-q$`TvG;xR$Mn_tW3^Z2kL4@#$GbC-ud5z^?%~-sna5{p0OwzIg2!R=G~sJ)@^Sl<h1svXfZG?(&Ewf|5}#X=7V>%QSXS=0Xgtri)4{whnf}GqJl{I?;Qci6=^o)HEadT=myjy?%P)&@bFEC|aa(y#`1+8JJP%LrPnG=06=M8d4J)Qe{^tJTd2#t?lG^{*`e6DAEqVVcIWtM})%C&jA0H9>h~wdTsZK3lqF4_-eOmGTeXyVX+WGkY>hIDdf5CcwE>09XCHZlABSrglbrL0i&ywNdK1}S+>*~z;e7(wf&-B&vp5-g&J<C_ld-{Nha-ExRrAdBC2k(!8ey1c~d9E#AUoGyVtMtiK$;W(fmDnV;*UMk#{j_pjIZxYAaep0+U!+L>^9bHg4~~%YpBu&FlRi^!KktdyPrX++$-Xm_*iRj^W0NI6=tJI5`(Bd$5%FUFxW+G*$4zg*`{|e2<@SL`#XNUwCle*Vc9K{h969UCd6ad}^7ovXCj4TTWk0KPyvP&tx$MU^7W2weW+JcKEe5c!oX;&^IiFj;az3|w<$SK6sKED8Jx{{_uk)notLI76SI(2ptKQxGT+8Po%U8}nmam+1EMGa#xYi%q{l58W`s)0&+AH(W@|F2!`O3Vqd}aPvzA{fNUzrcyxnp*}Z~RSP9e>ML#^3Ul@%M(e;rz;Z!}QhjhUF{g7Ry)8=dL<gIe)$Cy#8dXmL~b;`-s9nrb_;~e7yc|N>7n|_a;%N<773-*KQ6Jb-G&jPnLYM&PywjBtN(_?^DlDNp+h0yC=&4KDRW!xQp}r#C1k3PP6;^FZ_9qbuKdf4|a+9<E`E^Rr0UZ<8`dVk`yU_+x24pcyFFemiz}Eo<9-KlO!Mely_E$?C-g&i|fMv>)sK~zViOa@|E{Nrmwz#vDz!ospTv0Uo2mFel1^l|6=*db8Y#``xnbso_EVv-oIGB^8Uq}ZwmWIhl%~pTV-IH<d==*@!6)yzIhJ8=QgHq?&I$E5h+spn>WSynESZpo9}Dho=%ed;D&rY|5}s%lYM8BI#)!A`W-#$u&=zIvV7&dWckYbDa%*ROO~&^pR#=A{gghVDErEJ*z%QgujMP}UdO9B-%HQ0`8h!LGQ$6_&lBLQ>y;yDCx4!+ybrQ`<$aLlEAN9GyMN%%ua$F=<ty)ZEMM98oz<h*SKnWlzViM;AG=`td&krC)$ufaWjys8F80-PzUeFHe0QTT_LcLzw(yy_e)W8A`s#eMeC2#@`O18=eC2#@`O5j+wfs2y%K6;#m2<e|E9Y>}oaXE+=VZ%Q-{+dXavnB)^;}`KSI)7Pube9^UpdEGzH;8MeB~VLt5ZIQSiW+OwS47#V)@E^wtVH>V)@EB*7B8etn+QQ==WWh<tz1DzEY><EA?nEd+_%h%6Y@|)$@bpE9VExSI!TXubdxTej)5D`@7{U`@7{U`@7|<`}@dKTeyCCf3bXJf3bXJf3bXJe{m-?6z3T8`wr*5wfwyXe0_aw{(k3GAIUdAx3RuIGTV21!rzY+87=#7@OMq``1=%3-#WtA?q0>;agCFF{qvut&oNBjSp|O=w74ICzHy+%EW7VK(@pZt`kghq%I)Vp<9f;rX5Uj_mc1VHdnL;c#ovi#o57#MG<nPW!L0Mr_hqJUeUJHMndF<}rY&5`-=p2#IbS?C_&!=c?BsFloy0!={>s_DA-BJIOZd)1&$*s$;oQFSOX2GQH@W?H9k|~M`4-f--52MAfqY$UL)nkL#O-Gf<#9gUMEIWD71{q~68GDpm+;N+(L7_PTt5~r{gvUdLRrR?FJYY6jL4?t*9P>q|A}D<Zf5HH|HN=m*#GKJ3~PK8_W%78Ln`|NBXU8rgNr~vgk}eqgyw^02j>H4LlFBzGlBiV8Z-l#G$WYQ4@{a_^Zm<=9Hd!oIkTcq(j2xLa-c5Kf?(2ewwlY~no5F0pjE&j;2O}{;2Pit(5B!9;FbvDHb!(dqPGz}5X2Eij4@(_5rd!+;0UxK9*1_rp@YD~!F{2<!M)L6Uj%VCXd7@h@Mj3(=Fq0#=HR-}+Tgn2FlZHU7&sVO4jc?F0WAnF0S<uX00)5cLbHOi;@;;)5a)(w0p|wif#w9~0T+fA1s4XFhE@QV23LaC0apUohqeXR2X}-H26qGxgH8kw15biZ0Z#%?g-!!c1?$kSz&dy)g7_lT3%&^c){k|WA2S7U6m$(Z3cL|P{2hXL3xaqpbQzfR8}JtBW(4s%=r`bX;Kk588Z+r_FzHgXAzck#3|@!)q?@3t!JEJv5X7sXOTnwaOQ5$j<|W`u8td0!(l5cJ7r>;8{FpC+%{+_H59vx<zbkFE5wC}?0IvtTaWCAsKW_Nu{aS(hNxIy2e~Ib-lb*NDhx3>(q%**z(`|EUI_4MY7q<EK1?D5^WZV3ljQLAC(l(z*V!o4hvCaQ3cs@uQ+n$%kc%DeB+n%rLc>YMsYrf}^xHPo5=6imL3qu1n-}6qK2U<Y$tq;Vxp@lTxdO~cjIm7|bVw!KgA}#?fqxsf1;$UcHFljB#w>A=oK^tnmwUoFn^i$2Z_7XRTcG7%nHSuTAUYc)hC+-IAuld%0;=a&G&9`3=oBIp#I0W$o1o3zT@hE72@F;LUXfJR-a8GC_a8Gat=%?Tg;8xIv;8x&9&|2U|;E$n|!5@RGLd$|l9bnRmVA7AkRly%a>)CSFL!YG0Y&A4PjilkWn!|BTq+M;-*cD?y+Q&8~eK2OELu_L>1Y<lNIu<$vJQh3}K|B!J2TbY$kA@CK5D!2QcZa&b-NEgkpM%?hTR>ZbTY#O=CSWJHCiD|<O>ii*8aNbO3K|3^EdnO}5Nw`VOCd@k2Wf~cX9)TvtzoO725Ka2V5_+Su8Fjz?HXHR3`SraBcKDo5#S!s?wapRNZcOU4%`ko+e6!c%`;_tXb*4}W1T-|Xf{KiKyPXs#EBXQ@j)oHCno&~OnLyE$!Js2h|EUpGk*TTh&4tmH)5_vA8~UKM?)8Z7olx5^an6$8u%|G=)Kefs0W-G{T4IgBWMd~MeuQ>T>@Tr3~avsA#(o({u@Dj7kUkR7km{#d>onprfZKy?WFs`RA)v%9w*Wa;CIIF{QNZWMuyZMyuy%8M$Ch51J465Mi8$>Uu)6dTKM~+Dd05Jk^<ciZf^7!YD5@<xG3r@idu`pC#HKIhx<-?2>cta<yR<O8*z1mix|-iK^)@8?L%<gA@Kd6{@^&wv2{kQG-AFH-yw*%LzjS;pzU_(0q}P4Y3NVj)8MnvbKrxxu0&{(=6f!PZ$f_olRnja&k^wxXm&hjPr&p%k!A&xW&yV}qLL9c5X8mNra0Oahi^W|q-UX(z$c8@VZ?O=@goHBb0c0te}?V=lYS2-{Smy(hz&-}fo=uQ0e^!aUTs7SbT4!(m^2l9)QET^?nD0szcS*D5#{|@1O1pOh#NzzfDhyKN1#W+_mT4+^bauU@8EmjE6~ee(!=1x$ae+TMYZpN?gqa>-RaP`;5}#)WyH5e%+}~LW)9*l(1qZIXuAcv8%&yP<GuKKFUFI&i7^&cji>-E1g-$4nn=@8-$^5OV!oUJoA;k|7j!4Mn(^AEMihnygEc5U^M&CPQv_p8SZc(2BW6K2gJ*#kAc$9?zg4JZ75wj^r@-HXe}tX^ll}~*dH!1CIZpZl{2crU*M1%2aT0t3LHro{2>b}IeT<ycM?vE{8yQjAh#+V|Fe$YO!p|>J<4e>@OzSzVU-O{z!L)DEGegf@G?+Zv7ib;a2Hg%0!CKu6+8kUF>q84@OYjQxvl2QVOnWr#-*ceLz%)N+<6h0i{Udf`Zmx%J1_xuVRDd=CSH|;O5E=+B2!4%waRc-32F80Q^ac0@?!ivPYs?+eD`3(iVA7-Dg{VCWx(XZx-ea4Kd!R?br1!zJ?$H{z2tm9CLA+1%t%<~R_V8%DZ_|BWi+jEVyiW7&>+2B2aZnGKGyzO{4NUtE?MbxHkS2ji4}mF&vqIy*ambSu^MmHeN6;GJ8rX+ELJ$|T?N!AP#F?R#Gc)ud_@U-I$59Yx#C)ZBTOAq(t`05&EebZzD@72*{!q&44~+%K;y(DJ9kB+D0mtCp67Rvi)-Z>wVIDUDSA`Y^R|OYB6vmosu9fM?MLE+E#BZSY!1pkB-#}l3N$D9e_sGUrR~lmtA}$Z5y@-_77-D+%XzdTiI!#RLGp!Z0c4YALozF5r{{oZ#4W=N@1ih>I-UnpD8dC{;7Qdr5XVLa5_$>G|^tk3bn-On^9@BhhIpS>y;uPp#VA9{fDd05duV7k7X+2Garh(JYCKW-Pj3E9K`WE~r_z&nS@E_pcp=ZFqgD*o*fiHs(LpOsDgX5uFz*|sLJoHa+Wz2yp(8gd|yJ?-83ta@JeVNwqZ=tinlZ@ANH)4trL!mANaXSQY188?JX%{eQeeeV$zA|E>5p|6C#EASx<T2uz(Wk?YgSZSdhaYnev@HYu1Weiq9AQLjBL+g-fG46~oyGyW0QwcUtr6jPU2CxU`oYK@0Um@P?g#A&?g#FH=!x7tk+UtXy&h^OtqZ0)$77sG$AL#1F~*2U=vZ)GBT5?akH%USOhKFzK^%a-0?=Oo{JPK%;7+Ke1GFx9z7by<F&jZV4RuaKt<&I-!##K6zLPct_r*2zfsO{xGU5v(<{^k@qWw&?oe6&obS&73{t6h8&xn5;*I&wygSZ?tmmhO3v@Hj%4=xAp4DAB$4DJT)4sL+!Y6ora=X)-QUC`cO(qVqS=ZJVHbSii#cnWkfm~;|&p%GsjF&9BR9c`wg-E{cob36$(Pl8YUnGrRO=!GC2f*>Al#0Y3tXiYF_Eimcl;M_)(FydbtYiTeA@dpUv4~?h|{TNyrOxh9rsS&M=7y#`L9%;lVBW4&8-pbEEe}@0*f92!*N6)+_{f~XrSIS?{+g~}r$Yp(5AKogH`0m-?_>VqVO{GtAwf_JQT|8('

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
