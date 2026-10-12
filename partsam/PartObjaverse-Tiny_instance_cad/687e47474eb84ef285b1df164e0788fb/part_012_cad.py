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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/687e47474eb84ef285b1df164e0788fb/part_012.stl', 'relative_path': '687e47474eb84ef285b1df164e0788fb/part_012.stl', 'source_sha256': '5e0125de8a82eb0fc84f03c0b7ca4ada6ea207e76d8bc96742201fd1f4d9c167', 'input_faces': 576, 'input_vertices': 366, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0256351251155138, 0.1499379277229309, 0.12550154328346252], [0.06350282579660416, 0.28012073040008545, 0.27196061611175537]]}
GEOMETRY_BASE85 = 'c$}r12UJv7xP|XfG}b60b{HF25H$*lb!^xo!64Qsg9@miBG>|!Ye5ASHKKw_9D6TBqb9b&jv|7_Zgis2kQhshy@coa_x1(edT*__-eaxb{mtggxo7@U?;Q;2Ztvi%;itNGepYPJoEn;@qNL`mjSr0;JA6oJjMu2BuMJum@zu{qUF;v!BcPu_8?VKA3=NGL67A8#=+P>yxre9GBW!f^*yxZ^!K0&xhAQ7LBr+!SgC8?2Br5d7>pD$*d_0X!>UtU{8~=|##XmH`Skbin$OqLwId`V5YE$h-IZAEbS5uX*rCi8VudS<wh;K@4Aih50z*#9@?cI6tQ(mWtzx2Xs^;$16SIX-ZcQ2EAYTuK3^zYV)Z*8{@{-#@UUE_@y@y!N<_<GHIQjZpQ0)CluOQrnu?OAfY{mbRL#&sve*UMcyCGAc~NBN?^Es^p=E=fDhqd!OcOPxy=-|eZC*PA~^d;Z8+EcNtGIHz7)(!8a9ZSMs5)sM(^t<Nf={)bKBhd(+g_2gU^-x!#=Nc{75QopHWiClT#ts4u)_j`hTW@IBjZ4=?UeV#4X`{Jai<z0;U+MmBk9;`S1mh#&8&hWib&`ys_(oWmVa`3n1N<OWlx1s!!ZS$o5YgN$BR(82)@6Ea5TOLR|t&x?)*LLJ4N<E`?NZw2X=cAtd-Qw$2Ka+aQzj@{s^tCp>O1t$NebN3`rUWTJcrg6c!!S<vr_B*R*-5Ue4Qhb)#Gi~8-@HchY>DWH>uRNDNd0T$<^AS&chBMa{ilmRveya8yLVNzr$uY{)k~uMi}z?xh?n^K{s3veDXF8BH(p87#oswX>an(JFTUlhxA@xP+Zc!5@6hjw@sp+e#iP=X#`m`h`<*9C`>ba@Fpqp);-sEbNA%;O3R1sKUll8U_qEbrrmY7t9-1diRKDqg9mZ4XA^5yEt>dKr<8{$r%^M<bHM_xozEM7}rS2T$JH{zW{HHoT*VMkq&)ly@%5_J?Vg5#@;yQMRBE+At{kXh83jJ%VaA&yqU0X}Nw!FXOI=V|xxcKSK&`-Volz!85+k}cg@U+xp+82a;+9!mFe|cD;{F@t@&C0i4Dv$Y@RZ^~F&41HT+JDa<^SyQyuH)LNo#dyu8SO3>g?V}9LUZ}OZw1M-rGX3jcgOY?;vdWr-*{ESb(;rvllE4+FV{29TqvK*8g)BB%9q+8dDFalBM)_=ddur&U&?hYPZFhHOs<Ioq@Dy{%y-TU^QOJQQhxX^k_T;4DDv>Vi&@GwS%h(8xgq^vxf>fI^|VQpab=3ThwGGj9WL*WH6ov7+T<4Ur;e2Iqjxxs`l2#MARpuK`4gufllR@(5h3MQI$?Z<`yt=2&5`o{EzP8U>)`<yS8pDUlGhnCuzu|eli!<z>W-G*=g-2rS@9kEy{tuill_lq_YWp~t_;5@xo+nGjK84$M<t&_Q=;Yl-B7<}O;gFY$!V|n+M-$L5BKs|-{QK(h<|S^#*cR^w5w?b{M2}?=fM{+KC^xpC*@+XE?deU#5|jPMSLwT7VTN|9Q}ONX}svVvY0Pd&AEkqLuJh0*)vf8n`#q8&z{G+y08MqXSKQ$<#k#o%rDDYtONb-e=Yvf6Zo8idSILsb%>R6tM;Q@Xhc>)-`e8^>TS{DOhI3F@kRTBb2Fsep6aM41pRJ1d`;SAa~g>9YkOi|p9@FcUN@U0I&>4pN$-g=PRv8H#Mf(Myqa5Vm%JM5ubhl=Qw8-Wu9R_V@p&%3)@c{k$#yNUFSqxfBK7>1E#po99`oDy_PF?_`Dnkf)kDnJBCb>A{h0~)T<><uIMMdB6yMaeC)%^4|LKCh)!|39=UiX;e3oQqU9LB-D8_eYs?2Y5<{<ca9+DSren+(Di@ETvcd`CP=1RXA!&*<1axME{K5oj!I+2|_4dd*9<jXn>^U)UgkNDO`gV28CBk32DXQ}B@-t`Fl(ygTb^+VslpXH0!p@H~)<^%W(E@0liz`AW+^#=aUB#fW$24nv1-8KXB?{Dna{?jmyob%wD<IwNB2TMJsqmDD>eH#y>-DX$Jr!h6f*CR?}KF0gt+~mJLUi`^6lw0eA`E<M9EO{N%6!oSr$GIb^i}+g3bnH`Y(C>O^AMy3N`?0>9%*VWO9*6Ru{*C=KZUpwP`W~~zKmQzgI2nR=UGF%%;5;>bItA;Vd5rja`55$5ku&ED`qn+&kgsOW*k4L5Kt0PkNjofl19A%b)*F}?T6iwjmBj~8{$>>!f2Jo_a6Vk+JO_C$&-G-5Ro-8#o%q(+{`kC)-($Y?n=8In;cI-JxB&5Of0RiO|LPL-i|1;&j`^T(qP+j&b7`mbRv7Xb(MNnOZzJ+hc>>zM^$q-5eWkqdkEtl%*kdln2lg|qzpIQ-?RH1;Kc2_T{;P8e`das;IH%pm`B_UEjPkJ-j4KoNcRlq0%J15Tb@IS`ocG-F;2+(KdK}_W&wA&1qVpn=|H}K&kI9$dd*c4VGGwBxAGUUXi*IVR5996lcd|YhE8ESN>nC~2b!|L%Sx&jZAD@i<iT$hXvx%=&JR*6sRZqiphyH`|#oe)AkL;IQ$nQ5A_ebSiFg}m^CW#uj9!-zHymK7~f80nJx3+SPa|`;`&N-ORe=U{YYm;}OeB)Z!hsxnx@X^<P&W7I|_X}3LpWzRjgLZzIjCHQG&jQiNB#f&`zhhrG5GcOBe+K4J$1cd<scqtG?@D2x-Pa%eb;D;N+TR)Tajp->dB_m>M~>nCu7?46dzuHoRcowcH+C2Dwd5mcU*50M55|e*7fHFNCX|o7mQ%<Ndy9N-?27lj%@$v4zZUK1zNv5iQ+$*AJ@nI=^~lGxw<zz5*Lut<)E~6$8+kp=59ge?PPqkr>$8XGzjZion(e<AUz^wq``4@b_<iZpi^Y!*M1JNRLw*j|hhO(F&PhDaTRZfHf2Zm3g5%9NXtMZvMjG;7<}Sun=1i35eX$mET&}OJUX1b^k7J*6!1>Tzas|p?o{sazFs={pvr&HPL-cnL&K=sNpW(+}MEh6gVShB;gMaEg#-+^<dEWLXKks7fgQGpsFJVKHMQhi__^!T0u5UA5hkr8<{=ltR=U?WDuRSrLAE#F2`66F@ec_kLPtZoxKf3D@DR1nH_5@;|(W`}vum6R0)p{xm=OXiD@lCyNqTW3^o(Du+M)_Afzvke4YIg6jRO(H6h5El~hWZxu65sS%$2_Xo5YH#x4?y{q5g1pqaNlR0F-LrT$Rm8Ntt$)prl{4(|2|#vr#)UEzIEjZ_>GdWZiPNUJ>R^>c>DS#_OI6Y@Vnhbf4!WH`@9ELmx=#bS&XO1LD<)pw-8@z-3RBGg<s*kpFI=)S=<lkp-qra`}6QM58OwD7r{6mbs7HQ0P$@blTd$huM{bFy)^Q`{o<pqMOVjq8{Y=&nEQ43&vqj}N4;_j`g)a;IA?hBT=A%Cs`&RjFdnAhTx@zX4*t&L=$G;K_#A!G#n)EUM|&1s!F3y2;YasEz4m7$4@ToN`1x7r_XbNbUs_aJF0bd^hF``N`584te7#;{_+#^tpMw|R>wZ}0Cpe)$ue^l6aS+B$A5W|g18c1if6qRg(++Cb*DlV4zhD-gQ;b=Jeos5K0-x&vuFLy$J?Sm{-B&Qq$Ckl*_P}SQ_+56Pzba<pKILd9_}fPy|DomZKF6=b*AFg4zUI}%xEnJB<$th8J~MXY6!Ozf;Bz%-DeX1YzYgE2B--Ks3+C7Lm++Gvu`X9Qj_afsNt62cJWV_8jQ)w3oQC<Hf_DB^66<sP8kFC^1^1KI(im?g&ci>rSIS#lW}+Vdd*YkA-$j3P^~Cd`t;TPq{IheIFRf$oT*2!){QbwI9%Jfz)bIGa_*!sFw1>}mY%i*=lJa@i;Sa-ou&rJ={L~A`|D!8dSMA2bpA?9Gbbo^D&sihB7VC`lf21q=>+j9*i~f!Kizz8N1${l;LE3Fg+l1#H!Rg{#r`xdJmgtIeU+iW0D;zOjrXRz4;N@n)ym*89?`QGzdcilp#pi0i6a6*DTYUZVNhm+zDdywL5b;e{FJU|_AAt3CTPXaExG%D9FvxZF0W(m4mqvI!cRW6K+1Z7Bt?4fqhvPQkx}#3vx)(<xZ=;T)yk|Q64tYE$`~<&b5A2uGx#tV|);pun&Y3>gSJSV;&pL>_MUTL_wW<y6zr6zUzi}_DyFKfzmiN87k98+u4Dyp~5?_Dff&R$O!gXJTz<+xU`ON$&r=YL3d=H=ZFUF?dpnRQwFrNK0(C@2KQGRsM!t;^7esLw9kK9PX^W%(l@aG1j{xA2Se9G=Z^%y67gX<2viSpUwP~LJ3<N4xU@vSS@qaQzOAm?p;rTZGG=lD&OZySX1Q`c8~J+SLpyvB1#Q;k5BPftVM>K@~LM1S}h12OJjKgNAi?=;kN%Ybu^XK%Fs=sNhd&Z6H_4x#;Hj>0cCAJ_f(T&_zl{I`|x+-&|(<iFw@_y=F0Ju7#iJu?k!<@Ynop<e$Y*zbHD#n<)i*r!gq<N3ybGU97qS25m3L}1;{s{#LF9ju3^$D;mk-Nm=wK7jG|suey*F)!55{qE!UCdP5zYYVpD{OPw`KSNRf<i%J|ew>5+Y@Ukp&5ENQzn197Qmf%_--7a;R}}KK%Bfie=cBgcDa!Y3h`b#_Js*9oTWj1e_+FIz3uC-tUBPj#eZuu>l{<W%w@r<Bo)4<G4)X^4g5Gus*6s1$DBs{L*6joRFiulUDF1PPXMQXT`=k72j6d_50qFN(!{JBtLjHSl|4$eT|6vc*vvzzTUwhZD&^XcW?}VSf8{=w6Q#@B#at{8jcBsEeRi5)7pnmQP+8@F22bNin{<(#Hzj!0Gb7~d%%Y(5`RC$N_;_W8B*7GsO=jh0sLVgLHW3`lO=oiN>sHf#*w5NR?o^J!ixBiU&wmevdedB!y%I9ks$3-(`UYmvwNBw>-$UE<6|I@Ej3G3UE^H^uH6H$-733<y3&nf6@H<D1#&?d-3|1^|8y#V9crDGxA<c{;O`Qa`+&zQ6c<#}$m#t%aIz<nrx8_%h&Q2`m4{|8Wh^lYpfPCd~cyG!u9C7?ZK4f)vh6z#0wj&tGT3Rt&;%WM$8!&-c<RraXoY=sSl#v$jI{$~yGt<hNDZNt#dwo+awpYuK1Gpz*bxz`GQ%hsqTwo_r>KMLpjp3Siyju^fH?axHsJY8^I<4BahG64Cx#pn6+#uh5C+t)_@ui{Yt{chwf3ExjzwolzqC_mq|M?LXL@TZ@|Io#@n>poe6diXt&bs@h0F`izBJUlCf^TzQ?IIms5i}KY<;=Hx?2ENbodw}{oq~V<R$_3BW5)2!~&zg?<^KpNpJ^w^}Yt|&Rzn>$%N8M6Ve3RB0>qgZYvcFp%)<8W|7Gu5~s)Bw$)Lne7@^^*iuW4^6{H^<t=k#Y-=jM-v-(wf{gE;IPmYhWR{GQ7?&jESJT!-uS8;v~7nU3e!-rG?Ar@X@Dj~+((*x7hKvU4ofnVWavJ7_q+p1p?k+3gMLi7JZw`Fn@a&P2l|DW9Cr&yy<S$2_Bo_}Zqe80Wh;W*7AJ<&M1HE@Q<!sDbhwYvOy5&Dq$W>jlCe+!D`id{(19VKd-=+{b5pf#-^KY^c9je|&FPwjtiv#CNmQI}_jcn}#-%>*~Eaif?kj_cFE|?DMwd-^AB%=V71vt2ox5-W|7~-3FY~{<(we4xb^u7UY8UZN)Unzr}Sn%KtGI<1M-xp8su4-BK_QmI_@^Ps6~iQa*hG&mYm)@ABi|ujKb5KZfDCY{S59Qm*Ao)D!E2?^E_p6<_<E-yiJ8eX!N(0LoAJ1$n%+4C7?!*zKa@v7Q<)9)^GBF#IdevA!RfhxvW<D*O!-k>@k_u-=5H?GXR|it`2YX=-GHUmMSltXr;Qe06Z!DfI<oKear?KA`IkyU=glQO{gEDR0@|ZWrbS?%Rz&gq>&`Q0T8=nsxbOxn4!x;%izl%~=ZzDe$K-%2Yoe^}qj9nBh(TSAPoQ-R%GUr!c2KwBhQ9xJLbhe2x5op*WxVj+{>}Z9ph4Lw!qDp}4F8p}08pHCct?q6UQGr~JK*{FHoyq4+rUEcrNjEA@M_(pBWG<hj)8<hkVG48`54q2%slAL<umrJcz><c8Gd<c4GqhT>Y(CgfV=>eQxWr7g+T$u+30$u-Ee8H(#s{mJ#njj6-P{XT>m%c~iR6R3^Jjafc{q4*ee6ItmA@-gyF>P7NR@?(bLy9~wI48;ejR`Nme8tOK((iP-2<Ym<P<YnYJ48_x^Gs)A)lc+jbX*_unc?xwAc?vm^p*V%QoSZ^lOWjCTx{th;yoY+4yoY>}q4+ZO8u>E$KJ@`vX+HTr`3+Ug+c$izxEMomC5B>GhGHYN4B1F_qn0I?<=l2-D6UE^O0G(-%urmBq1b_;_)iV0)`CA7ihrWsAS*pi{)v2qx|Mu{ypo}K40SGf47nF|I9X|Taxbzk)rag$uFFvDMr}xTBUh$+kd@XVS0<OIRwtJymt`palv;!QDY+cAHd$#sayhaKwK3U+T!o>yCbccOCfSqPkL*p2q4pyyT}_T5ANUY|Q?FB3la(frl^!E2y-B`Kenovuenl>6Kq$7S-X*J0{Dh(S3N@R2g`B}qyoGv@yoJ1!x`wQD8F?vr26Ya326+NQ@hIvv@+fj7brM<W6mlea95s<Vjy##6cp)`~ypa4YbuC%x9`d*3UDT80UF4$-#kthW<XrL{>V2}(H{?6ymsGU|z2s}fMHq@*sFlbrWDkboI#gG39kLfgaYL$++>qRa>PB|sI@N@sxG}XdxiPr`Lvej-MRI+zJ43NE)q(6x))<O^)u3v<`<0>i9Q7x%(j(+^<aFvvaymJgp*V~>h8#vVQG1b<`jSm#FKS(~7um>AT!HFFu0SqLtxQ&0o?Mz-oLZJ#oLq#V*n#>f*@5gxEk{=BLUtq<qgEjoBbQ_-cB0lKJCQ3<J;@)}zDf+mu2es=E4dCsaU<#=awBpx>R7VUS>$Hq_S95zdvX9nv6*Tio5>N>?PR6jkt4_>se8#I$zL-R$5MYF$CBfyKa!R1CdZM-Q+JTZlSeZYkDzWQk01|aC{Cl^BBzlrFcg1kfL1YpRVenS4j?NXLiQ&Qq=u0Pl0z7Z&D2n`ncSD5c+iI!N*zuOB@ZV@P{YV!ymkabaX57VIh-8KP~3=Gh1`go#~i3!<S{p!$(xz$JnC+89{C~lNAg4RbB5v<)E~$%$j_*I$$L4ro-q_ZqHZTYBLB`%e4A<^-zHz8rjnJ;B3~kBQpb`r$%hz<*HZ_P*OQk}{m4qa$x36$N)M2ikaM(u&pJ5_#ia}g#oh*l;_}q%WTmgjDinKC)%ixTQhTx|xjI#yZ>saP;!g|+#pfA{4>J^Rpk5(wAkU*_kd<yB&m%`smy)B%Aq>TRsWZrZ$)8gvkd=-ie@^Z~jU;y=_h2Xvrj8>Alf$W#$x0WJ!^zRqZ^_Z*Zy1W#QFoEok@r)Nl9lF?_mj_1?~u=se`YBDi~5rM7un7LRp%kaN?piy<Z@IGayfDhhT^6S#XbzhzSKHoUvev|7g=dTaw~EhY7=rBayy3N_SDAY_GA;a0a<B%vWeW9>P}YLg4~+ijoOv0v<JBx`3q`K@)zXZ48?sIioawi?oRDN?oRfjb|rUZJNy`mn^E1#&B!$wik+y=WGC`J8dM`IRcFC}7>a+Po+JN4&SEIuNlhp3Bqvdm$x6e>N#wy)6L~PX6+>}-su#IFxf<0-R$75vjqFS<O?D=iVkrKETAcg|*`8X2tki*QPc~2;wf{U~3xE7kY)36dwj&p%mLw~6A{Ql>pjIN6AeUh%u1IwyS0q=Z)*&lxM6OD9r#2(IlN&G;e@1Oj{*2s$8bDTRCbuAWphl28kh?Mz_oR*__ayhBeoa;yOYTGNPmLq@Cx69I+?zU{+?yOo9Zgm`f*eThMjcA-M()H=+>Sbs+>YFa8bnq)fZT@MkvfFjk^Ch?@kEB=sSL%7sRPK1$+M|J<RG?VHbe0O>QJ)MH1Y!SDe48XQgy~X#n*}r2B<&TK>m!OIFLG!97yg@4IwKvllzl{sC~&n<dzJ@jts>W7>esr2a)TMKR5h)ZdTlnI*dA$taLbe7&(#}L5?JkWGEg%4JVHv52gl_l{O*|Cby-k^Ko11L$V6Rov6>rN?(vwDDF&sMpmJ?ivgjy1N9MEh2rMa-^ogElT|3LOT9!^p}3j>p|}J!ldMAVdwPe+O4pO$lkZWNkd@|;?~!X8pz6G<SgAL;Ho4b__=*}p^(HGVPgd$lR$84LK<-HWgxrx_i=p_p4{ZtPZm@H<|DXOV`@cWBLH%3sKeqqZcNYHIui!gN*VO*~5-^~<quQ4~Y$|s0a3xc%EZTnn^FU5+'

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
