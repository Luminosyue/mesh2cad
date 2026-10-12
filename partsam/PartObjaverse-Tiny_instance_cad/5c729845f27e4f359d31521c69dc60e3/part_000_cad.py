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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c729845f27e4f359d31521c69dc60e3/part_000.stl', 'relative_path': '5c729845f27e4f359d31521c69dc60e3/part_000.stl', 'source_sha256': '680f0a9291d6366db7e66e68a1b9b366076ff73eb1d695498aa9a161c35336de', 'input_faces': 560, 'input_vertices': 434, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.008111964911222458, -0.33816832304000854, -0.28961479663848877], [0.07850930094718933, 0.28011059761047363, 0.01791311800479889]]}
GEOMETRY_BASE85 = 'c$}r233v_H|NkeEsI`JvQq)*tFG{p%$+Z-XE!Nm`k%&DJYAvRSC3c~;yVk@m)DlaKBtj^)wf4HSqHS!Yw3h1coX_Vyw=>iJpXdMle)&G{=l#mtxo6IN=G-}FhJHg^=koDa_@|t5=iP}}wW}(MQ~||b866orYEb{kku`_MjPp|bD3?EmC$#I*Hnh8!GFq8XIU;go|Jce6)yf|as9(8;T6sWp?5Nnj!^5LvBO+zqqVLd=ks=>Cuy0JH_`OO{-Jlw3-KsUziR%CIC!ZLC=Cw)-7Oozg_1#f9rVE|5qo!PW_R(3&{j(<on{ut;g-pu*E{`zh%7nq`^!Y75>*&u5Wqd(-=|$XsuQjpe+|lg|&QFb+Vb1mXgZQ}9)20QR+b6f={J>{}&AC=5_X)}?Hqk8Y-`v4CBRZLLJ?}yqr{3%0ddqm?KjQHR^>LBc2$@3t|9X8pwNKh~klHsKF_rS|U+tiL*62f)d`d5Bul31FAzzd$j`~kr#^-ykXP7xx&Wz*y^_98iT>pI(pKofV*}>-a33WMFR+Kj9+WL}Qhw1UtE$y3L<~lh2`k4FIZfvFVbrf2+(VVNndASZl{Z^BI;^h9iHQYnz@#7ct=St2J%9TGy?WEtARzGacwJIvtZQ_dq)Q>iF2DKk^V>g}O#b46Rxx2u4?!R$S&a(sK>G!xbsN22{!KU2(a3tr!F$>M@wapW_KC>z=Ft^vgEzfzC2K_DlM^)vz<z6(~+}<(w9M^4Z?-7>vuETu(d)`Yl=lZMbX_VJdSCWU1rd+u&jLz5Hqj`oo*KaMR^L4p4r*XYk@$rY2-z9%{7212)lIJbJ^J-E%uIG{>^QoUQ&ywlS565MgbG7<B>R-<crT+EN9jP9!TkE)P+SSNlQ?8^&b3V9Cg1Nn(Yckg@Bx9kuy;igY=POIanA>X=>Tx~e&(AZr*W*reJ+EvUV{Wf_ALn`4pl*`oxMz=WJuAFeP9F7?^IAixKFXauN6fiVA7%25{p4N8E~4v|F`4S4H%rVg=W4@no^M48({UWJcM_=GoDE!un0$1fF>?ET($n5=IOj9gCzx|3S>yVg4_jpJM@cElxnEGMrJsrQxo#OZ=bPK>SF*TnZH|sJx7T`|<hqqwm}JgfNB3~uuFd7TEf~0%+I!ESx~YXKA2H`j7hkHIbJc#Tn|^iw63Q=?pt>o)C1sd%N7~y|H+TG_W7N;^*suO;UKzQ4UKzQ4UKzQ4UU_ocyz=y8n^&IWVqWPF8YEecYs{;IIaD7<`5bN^A8naeo*ebjuHNE#)%%a7G@hO(cF}ncnvr47-RC#$HrGe{EqOWB&3+$4{;&HO@_*gOkpJsGX7q2rj~TiBK89R*dXVq4Q9+63+?8~b>yuT4?_(DWt)Sy(22y>Tdy@~FbItW;8-3omFAdD5Tp6;I>Z9aokzvWlzEAaW9xcN6y;99q(KzkvBl3T(kI4VEJ{s-q>m%}it&c`~`}%0KH`d2-J2zU!c|RZ5%_|qJkFJCS?q~Z1%Q|S}T51u?I;c+#T215cIgje2)_jm|&ee<q{JksJnd;-bd53cQKFY}L`zRx~@1s2JZTl!Ax9_7o?QQ!gPyg6QISOA}Zy68vQTpUC+DEDP1J}^_`>nR@mpu8IE|&e0BVsh=|GM8Ix9>}h+`cdMw72a`wY=LX*Jp0y?{A~HbaSp{w4nOCUv8uNyJJ&0x9tP9q5&>CPNVzOkG8Zp?+fCNZKUH~$$OCM<!-l|KG)zR<<88fX>@)A-y~D}_1{tMPC1-HfBrDn9-2R4Hz?N=Hg2Z=!k=ZDbFEj|bUJ?NUDUsF>=({=71~PeAC{u)sWxc1iO#cIe(J|HEjQhl)UbAxJMs_QLgRUOO*iMR@Dv)4l9~To8h`#Sl<Rf+QSMmw^;vW7j6Y51<(~B;<(l4;+s~SmMdM2FJ7&%uB{x#84F8+2+h_eK*8-kUKgzE7vzFYuBDHt<{HmLCJ*O?@PM_*@zIxR`l)ERMp>evRHdB4HAELQ^+hSBVWl0y#Ur(i6UDt!_FsCT><EVO_a^<~Nsnp+~c61+e-@MJ|yE}#I>D-b{<8icn#Qh(+ypKLt{K7JG?$|nx#-r78pEc*oz*0x4|MYn7|J5@--~GQ(9ULw8owek5zRaM{-MIY~&4*pD`M68lbDak~(apIsWgOS%nM&v7I_sB6?ed26ID@Oxeatzv1m#Mu5PFVr1S~jd&K<v9<>O+1>sVWz+lRiU`>&dLirVW{+H(JK$8|a{|B`flov)%OcSa>suJ3MT$(5CtIM2F!ocf9QjB>qN8uwE#h3_}{wsQNlJd^3q&t<04ysdJSkGuFwZoeWn)113PuXA2~FZJ)fah&@p=rxo6ykPTGbMDyLlj@@tn00~rX>pOqv+%pU^tsBPSaRihH>!`GXE5dZ%d0$|c6-iJ|GRTi&ABV-5#`EF7u8MM>84z*w}kp}jIK!iI3n(G-Ktih_Rcr4spee28O8nQ{7C({OFrcB-x$Z&_t_sSXq;1C@i^B#KSuuIqYQKIcrS~Nt95!w^H$5rlSK7e-;Cy`*1q=%bFQW}rFtr}Ch>i*OL5ATgkAicm+vTz$MLc?=V=r8`j(oXY0jO`FY|SIG>5K>tABUOT|ZqvM0uw()W0)!CHGS^;t1s%N7MM73wCkdX75z~UPq>yb7zOz)W5nuiM|*5iz7V#fIsLuYC8s8Fy~78Hu}ChW?bTZZ;1<>`}|FH)64TZ>B+yDL3MNe#q+_))%ru|x~S*prkZo@{uaLORW9=P>zgZ_Ki|st|Kv!%Z?AdE{WJ}y@jGv=$u#H6y)#_TwBb}YN4;)zKho9HR5!I+F5aJ4nnAgH{7YVU7O$o{XxHXau2l=7^K!pfKy`K%-^c4jR!hrqjodN%5ao_-;e6bf2)b`7E&TYtTB!%`_pXkh+)?His;6sToh)<i_Wh9OPu7A=bMERkoO0LkpmcMtzFBWMuCwWHlslVjq`J8)?WFc<U6s~9_ovmZ_W|T;^;w)p$MAh7d<^AU^-vzq*iE$m*FrZ@uCJ`h?ZZPd&AGO9D7RlV@3=X4c$cO+=#4k?_c3J;ug42p()Ur1ZA^7=O#ExBd44Ks0h#999oLETtNZwS;Zt@Seg0r0&d1!NT*>~Nay2@h*O$@hJl}plO1aj24S%m6PowkF+hpvZetxO4md4v`EbZUbOLuqh_3J>ne&QnS*IYC2b3T09ddhdE(|Y9Er0k@ApWfnqiYtZl)=88*g1$ISpW8n99G#c4lX5-KmvSv`8t;p~-pl<2j^X^{AZqU#beM8?^WmrHbL*E<d&j%!-2V=R$A3lV=hq%Nl&iz8ZJ_q4XL#K_RG;=|`t4#g51r|+d45j*l=pv8bLsx32Kw@R4hrS=$>qK_e=j_F%julwu4ZZPcyNgGWiO6d@-EqQpK;Aun`y~&LU=w@Tc}(5UlnkG`f2y=2}}E!O_Uq!h><(Le?a?8<?NRy&ADsB61opKHqJg`&Xtb?s1EwlyO#FufiaY;3l3Y(SABenbG$b&a;;k;e@|V>*5g)tMY$Go%zE7S%kaK#xtFEA(lV0s^_`Ad&i82ueUDtv?pf-l<xHa7op9MwH)mOYUN^5!v|JbUNlng&woS7fw^3idZ&&)+a=wmcvrqH&>`e1eo7aht+bQ`Je@{o!Jaqj$pZi%-mER*hnVoLV9g9~`?)<3jadWONzQpfOdY?aL&h@haydJg6&b0J@b~fee!B2E^?mj$aKefME^Q5KypQUM@C^gEaTE^qEoaTu(K3|q)JVn~mJkfu19X99A8AbTIzYMpu*EgJ}Tx(Ou(q6xHlGlrul`QQQ|3F?hTi>*_cir#H``epQmhrpx@1k6*zR)s$rPeln-WgE$gk_vH@A7=OyvR}?*SpjCzL%D0slVQO1Lf|Ys;61%u=+aZS`J^wVmtV_*tfVI-_9`Sj?$AYxe}Ai^W?7^JpX4E;C<1ytK3i1RdeWbanJd_7yT>eTYULFUx8bkA1ux9bGzK8I=Eim<@W&575F`7!Cbr!;yt;MyFS0k>-eneyq}!=A-8uQr2T?EwgS)Rl}-5l!tF8i9!6O@Gu@oK8$RH??||dx-1(>mzptK}e9W91_d_j#->-P`wXZmjdRsT=S_yxexBAo3CoSXYcYt!^er4q9mfn1SYuhKwoV&`YG;f_xo*lA`|3ZG6pUR~JmiCVBS9o97c%r4f!}ku?v+^WMd!<RUW9E78$?GrX>w^29r=Q;0Ja4=Eq*~f9eZu>J1A{H~G44zH9H*r|#yoUAI&P`IHue?ep7&<PbqW07I354`L%NRc=gqnPk7n~e`bhG(=G+}wg7%-<PuppIR6DfddQQ{M(C6A7;&s!vJ&%9ZetxcO|BUtns<R{a|0IK--v=l0d*$d}xQ-Y2z5b(9JfAD{=iGQ7@^?jk{tBPX=iA*Ull*9FzCRzFXUW|Wt@wQFY~p@uf5+Dy&q1yxyLkNPF48*g`lB1)|DW&U^Bp*t_t)c|e{0V5$M4X6-hIiJzwe<3xz15z`TN_<ong+6_O9{XT<0xEc%0D_E%yN<*EhQPdD%B5)6!nQdV;Q3i%n_&m8;7(a2<S)@p(Cp^K~)yUEvvAhoAfpQypg9I7RLKPxEm*pW*A(hW{SPQRf!V&!H#ix;ySf@_Eg<!~F+j@pDSO2+p5Xq3^%z##^*Majfff%#s&)O?7s5*~Nda<WqOI`FrQ=c`eJFtN!<SUGQ2>xih5!_fvAzw=~}EAvAtvVhH7qXNUOtbn`HJ&!*1l%(*N3Jo%m<PE$YGVcbv7Ey|T8xxO*yN|y(eyUwRjd)?8K$CKu!T$}sGk~=2dr(C_7O1b7Ul=InNoHN(i$khwMJf6QJslA%LfZKmIfbYXqKj!yr&zAGwce-`1&j&5j&AB#zDX%*d`|vzDv6tVE2YpY+Rk9bHq3c*ah0m+cca-b(=UZ~ehb|hA-am-%W1k=9_VKGNxugAMZvVuao}<-sXZgA2z)yVK%KPcMD0lImwdl{BPwGnFN6-5@<l6YXd>!NK^LwpfIefl97o+1k^=MwNPdwzh72#YPHiGlt3-EsE?lGF@ns*u>x4j?ls}j;FcO<3qd&OKOIR9ZX*XNH@$IZF>YmIXEr&;`b)aM<}7ij!G<n>8@E*@5qa{D@H<o0#Y$nEQ(k=xfnPi|WWjoiKtdd6d02aVjm4jQ?A9rTRfwhkJ(eI4}Vwsp`m9@{$T$!+VPrytuo=xJ|T2R-LyTL(S4Z5{N~&9)ADu8VCQR6eiC^?w=0>(qf_yw9v%kH;Ap&Fx2Ka6hx_^EmMyL%%lglsR`kEzHj&??qAW3J&Hvzft&mQ6wbozj9;!(tCH}@l4E1^Vzv?2;V1@;&?p$_V9WU6nfg6y9({)I$UkT_od!*c$_JhEbEAoyCc7+T)DrFa<$wluIGc_zvlj1@p}*NG|utfz_Tyff0FwtAH(a>oKke3aTor^lI!o6q+H9qz~lU-n00+rzvpq<o{x;&{(NNQ_U9ubw?7|w`nNqF8M*!W$kX2TeB>FA?fJ+v9^3Pgk=vh-Jma)IA9-@y^O0vfw&x=ww?7|wa@+Hfrytw%k!PH?=Oa%)w&x?yIBm~Io;ui`k39Y0y6csF_&Ivn1Ma6|1%971A&T$YPakugl|ahXauK{<B>lnHt8fPGL)<g^@%tI?SA1TPX_ozoRx5z!vHkswC%3(yF>?F+8BcC|KjX=5?`J&y+uqN3+S}gG7`grZjFH>l&ltJ={fv>@-_IDi{r!xQ+uzT4j%#~A<2kPF{fsBKy`S-%ukHPe=eV}_GoCuw-p_c(Z+k!EIj;HrOsM5wTgIio)k1$qlt?JA;;#(oYx<{_GL%1t|Mx$&92E5b^-nG9eNg-V`cEx`y%eRMkOPwZA-o~@L-0rN+Tf4C@52j%-v<{ES}HVNXeIm;@JeuRcpGqUa1Wu*@V4+a;I`n7kmPRgPr%*4z2M`)y}-+broczR$AiaX+@m1L6NSdXC&8D3CxNHJSAwU4SHOFNSAhG#dw~0ZyPM9xJ0!W2(5LX$@Xp}Y;Fj>V;FjPJct>yuxD_P11H2o!1Gp=^7q~09Cww`$CwQ5uzRMuVUkFWre-57l{u~?z9|azTT8BZB$C|FkSojCvvEcgf(ct>vG4KiC2{`r`NOCAV3>=1jL*ezoON0`HMnICIg+>a+3Vj7h{t_Mo{t~<xJ{-Ilya+xNya>DiJ{Y_JJP$q)JP$kvJ^(xi91o8G$Af3W`+;YIr^B7#>ELPbzTj!#ICy_>9C!vi5<CMu3myfY1)dEb1fC6^3m*cW3!V=j2A&UI2#*Fw<9aQGByWWzZ-*}dZwK#$e+AwNPKJL8P6qFSF9z=d?|?4??*MOuF92@?Z-LJPZviL4=YW&I8{zTbjo|h0nc(%{weacSwcs`IY2Y>BRq#0QD)4If4Df2O3qA|%0<VM52CoBefX@YQ0B?fN2X6vzhA#v!#I@WENlt`s2XDvqON1wblX0CA;XA-Pa6J;?TfkdT_eA(c@J7@(5xy3@7IjR7uL7?^y%OOrunTobgl_<E!1+t|63Qj?E+kon`+`+)dH7r4^5BZ_yx@x9O7Q&PO5iH+eBdhJ%J4kk%HTkFZg3#D0^A2&0bCC54K4>R3s=Bp!DZlY6y`GEQt;PcDairCOL(!r#P2ef{HM?hp<-Sv$;E}27J5hMZ-piKFL+6?l;l_N;^5-w=M_FH+x-kl&W67NXM=x&zX1OPz61Xgd<T3R{t|o}{3HA|_($+v_#5zD@IAP!={@`|`4_l1SW5DJxDQxL@<VuTu$1J-@H}8C$xq<<z*3Tbhvx@NNqz>;3zm}n6#f=iO7d@TU$B(qNAO%=DajAuUSKK7zry9U{1w;qXYjA!9C$W38`m!feg}L9*C_}7Blt&Lj~w_t@IBN$2Yw%XAN9?FKL$TW9dqEngMUZ8a^O$FPf?c~_#^NmoPQ3^F$cfPd#t<<$@`JqN6Gz>+$Vi3R9&c=&}5-5LQRE&gsKYp3u!{(LhXfW3i$~Y68cQ2olsq&#zOB2)ezb*j<-c<j?fID1fgj{i-l$i#R;VfB@3+-nj|z^=yRdDLYmNIp+iF3gcb-*7g{JZRcOA@6rnGK<TKybLfeHV2+a~2CloI<QE0r-S)p{H-9m{%DMA~B4hkg+Z4|mFbW%tcS}L?d=u4qJLN1|ILf;By2<;QvBy>P%z0h8vbwX=}E(x6$$`o26>n=1;XsggyLW_hNh#D0Zx+VCA&>uqAgqnz~meAWmSH$l>2wfIxBz`X{<Q9Bg=(*5Up%x;mBUD7_d-3~Cq3?v6d$F3y>nDCMrpU)$_VVCz;95d`g`7fN;GMx;z@Nfffj<Q|f`1Hd1g;IQ1+Il-N%qIFi$Idg!fS!0zXvV@uMU3?Tpe5=-Vj_L+#KEl+#DPVN$x1r2kwMA;#@nTO=qYD&b0;lZ3Q*Nxi-W&K8Du<#|VuQ8Y2`99|j)<mOc_Z3_KK)JQ$K3D>Mi`1U?cx5`7JUBoBwjfQN%4AjzYJ&ciQ2lE=bhz%dy2ShSIT4wC#Cd<@t)=g-ha`Zti|NO&|@dVlaY@GMAjcX)qrcW@Xa*_gMI`@*Ba(Wq}<_)u_PuoIHp2R;}q=Zu^ay_A3EO)p6DK=@$rK=257EO-Ps%5*KGAjv(2ItaBF>J9G+?uj<NA<5zJA>bjn#^I3Ue((rzS9mvg1h@x$06YRLeKhzC{5;&4J2izq5^5~eMv?Dn6(t1T7~B|bLLkX4A<3UWk{iHlf*XKqK$2BR^84_{;P=6G;STT-p?X4TkmRQDy5PEK-xO`6pMWH{gFC<uoO3(0k$wtlhq|^yn;uXb)VLeCD?9`og1U5tcLH|>_k$!G*IKeMHzap}w*<FDeU14gy&3!ya5L}+@CM)yz}4V2z}3K|A<6H;Rd8W=QMd{&4zB=L!78p_1xRvbcwKN^T(ioMWcgpm?}8tJ*8>+6%B9Hvyk4xY@ci&xVCmlA{NOy0<lK;C`6%-iJTKfE?2W$iLXz{r3xe~3OG1+6E9d3#Wsu|&@Pgoi7<UP@k-h?wTnb(QY@Bl`w2{6Bk{k$s8!SBlyav7t3PfE4(WWXCV7e9orfU~~>l}c7i^KDS^P|4SA<0D{$%Wy$!E%ntIaEmbXKodOB>TW~gMGjX+)MfAN3yT!TKYng{gi+9A4TAPU_Z1m_ArwD;d#N*^MU=r#o#5CfA(V1E5S>GtH3M5OM<1p16~bZ4makG{A?Y3t`fLBB)K*`7+f3N2;N%xXD=sN?)AFB!{DvKa$S~d@Nr0TTX+~a4DH*Zjr3!X<R<Xe;MN#N6SR?j7?K<W4+aP0e1hOrz=z>G;Z?x$I(~?2=m$2gyJX`>vN3-o8*@yuaj%nX+yf;W_esgdy;O30NODg|va#+<HueURjs1gUV~-)(*t<$L_Oz0XeXr!|@G{`g)?VKJx&B}OS0n%YX!OM}{~wRoKWY7IGxH~hi@rR6i5A-0m%eY_;(zjl2FXz>{{!^*>!t'

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
