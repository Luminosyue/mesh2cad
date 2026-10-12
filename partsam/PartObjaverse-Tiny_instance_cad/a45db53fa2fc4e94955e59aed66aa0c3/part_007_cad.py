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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_007.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_007.stl', 'source_sha256': '36efffd88eddf33e6acd4614eca327d36f9e7fb9494b35919b0847ade9d6c473', 'input_faces': 616, 'input_vertices': 400, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31441715359687805, -0.43227875232696533, -0.1433708369731903], [0.31439125537872314, -0.16649305820465088, 0.22755542397499084]]}
GEOMETRY_BASE85 = 'c$}r22UHfvyT%t4G4_HTWo=-=7Ez3K?HC&>_9&ksDhd{`V#$g`6JwXZu_mjD(b&5*Ww9Gnuy_4pOEGq1Vq)~}yzlere&fC8+;gwzyyy9SPlnmq*>`7WXZ9qdL(W{@3jeF1BphkqR`IjYiu{VVGCm?^Y-D&uY^{-_CwVA^$)|tN#hrU}3hCpaj8`W64~~cpkMVD$`ZpQU&_6)+A2KRtY|OxsVWVOOM+m>|z^K>=%a0v4aCC(AyJ}#aIst0EY60q0_5b)Uuhj%K()V1trP>euNfqVv6#Bin2>sUo>~dbHIluXLLe&xX&yt3D(tme4`mJm(ewR5$zJ53D0@ZV?>UPreBiYaUG1vcFm2IND)}SBx%JVYp-^)9VRO`d_uN-!X{;sP3UizKTfy;NzOYPCBtJEGnq#~DJdyv%mWYh{#zf$V&GgN-yXljp<`EnbTuknI>eOkUNRL{?O)9Ck@U0nWRMXF!#m$X;Zqc7e}z8Rf^&v#5-ZhxL7T)ubltMuQ;{FzQVpd9<_qS$}g=K!f*g8k5I7pea5n(v`@J$`eV+L7xP|M#XP;^}vV7v!6xPSJUpExK_3*LY68(d`2FTW}h+(|DRmzB3N(+E{og^+WDsT#wH*>Id_W{QIf>l@9Q67Y?TLb+#%_*URWTgM5ARrOWi+eU_zCeK&^jaWj*-{&tyLsGjgL<SUbd-0R<z?=)XWFYbqhIZgVVot;hP4}HOTaW9M7ua?gs-zeObuDe#QYX+T{*CO)ueJiLQO{v2D`6_^Xvu<l@zp*)<j%%*T&Z6=wJn8y661@&kKU^F@z8P?b`rqu;hU(W78=Ru@jpMnU8yZk~WAaBQsbBtl%KhN?8<lrFnR$YKZ>`Mz5KwU@{avmZ<U4Yd;5@DOXf4${X#|%a_BG#6#UD^Vn@b{2@bxQ9?a}VPp?pyO>dL;~Wxj5mLcgMRuByZSj6B?)5P!NZj^+PmlHX+tov&GLHRYjk;}QA#*bUroF;_CE{~O#O-|Ui$?}K7qbREqt1IRZX^{4X6u{zWbjxj-8{{B5Gui?H>mJIxn{=V0FzAwTSQU5zHes-M7??1wMexfG#v)|QYbo}BEsQu3Fo5@#JRwZAHnn=gh-#p=dp5Oa0_lwGTm1AiV{au0P<U3x?qw<EYFSS!|R-b&m${wm;e>9it?^c(5W${98|GewF>3sXu=K7c9pnOxNCsBX8e51xSzK(k$ciMgZ?lis+9<A9($Bn4T^#rZw`|;l<`zW7B)ga$YT}=I;?94Q&J(H@j->M<se>02I^)<h#!2X=IbY5!Jc)DIL-&l2;&dbc%oUiW>zI@zv(R^M5_pGz~dj1J~UoL1t`RO>f^$_{1UQu4F#g4D1<91s@zVgix$}jzC|DDv%mzNJxy$25S{d6{KE!`I($H+Ig94FscXHa<~F@^o<C#W8?{><-$uk~8Y^?ZAf@<{zXmikA(Ie~mVcO2!Bsm|O%^~?+9@@1#deQEdvts?(rGcJE}F8SuzYgAsFScQ)}*)z-TJCg6vIH4T%r}D}=AI{GL2Kn0MvV7cx3f!LOO?g~d*q!_P{4uWopFHI2u}68_I{Ye@)YFU0mzYk+Rq6($P(3pq&~?+CmC4t<JjgeW-psJKUoE_xeAV|<hQ0mz(rN6^PU7+%v-r4CEf-S#_rD`wiSgp{$@Qq6YOBRu&+A|4`kEWBAESOa)|%Vnxr?uRsYOTW`VOv=VLxB<!l-1*hs3hv8@nIyaZ^sMvHMz^ygZ(*%r>Z=7hde|dCAx1+M7gb=LfmC{^VKwJQ>=S^Th8pJqOGw0W?lHSAM;n+W+hv`Pxqpsh#?pddKOwug<V<)Ta8K;oZqsHf<$ezfy^h+xvGqFD)>U>o0qo>QSm3<nxVBfPb0JOP$np1J%DHj_aA<m!Ci0=P6J0%Q5V)=*sug<LA^)$L-Ok{rVbHcP3FiFQV9Y<>wB*-*sh#X}?~M%x{z2{FLt04@!aDl!s=y2tKYWuO2_8depiD*+-rz-bv&;#&zd<&>kiJJo(zPQtaQY!1@2zno-o=8&_!ja10*G&##gRG4wkwm3$rfpp`F6^*HD5WxwG>t|#!fMRXmvv?pIl>%rsCl|u`te1E@md%vlthwq_w&Y!-Yj{ou|KhGCk*+unu*CXE?gZ{~tKb@{u$LIU(=VfM1P3QYDd!JkWj}4`9SQ(v6zUDgax~Zwu&mS)0@(+FazIz?{BeiE;9Q(-?d49M2_7Bw0e+*~;`~UED%vwYDk?IppzV6|}^>qG%d~-nuKJLn|*pCdQ`i&M(`FVot=t%RV=Z-RIC;9rCXFOl??!*1?bA9$N-sAomHYbgaTY6!NJ+GWq(+*Ml<EEzA^FcecoP1^8q!fGpXhUw3Z{`@3V((AA&kpj9PQK)u(KYEgtd!nM^ILt)on-p^(=%z@)@mm%r~bcpf_x?T47Wc;|C){)xG&kBKW4(ZgH%tuWcGI_a(*5!IGfs^wwio3<_-7%qQ*3i>8)pS{oz0IyuiBw^@HXW#^qE0=Jq!mNWOVIh|AA8#Pg+3Oup`O3Um9tf8gif(K~!!Zy1$i&o?v3huW!~3QV&1kMXP;`O3lqN%p+bKIlR73hnpB^j>0~{DsHK*l{!u(dyo(d7QcHb3X38)jXdWag*nFbsF*Y#r#Kav5S1Y!&tt*eh;GYO&_+2e63a-`C6xgnRI`B6V3Hsd&2ovtPYiTRPp8d1D#xcWDhE@?oQl6^&gzi`MkIdjfdvdIXm3$yZiNcoUA@|hrJ)PbuD;YZPb>_w+iR+Fe~Q~^5e5<KC1;@<N2w#Bb@Roc_GhpXMM=yaF4(EJ@KLMcKdOaZt;i7U-fF6{kY1$DDsVl*SER#f6ZjNF3wNZaQWe9d7hr<A?Iz|SbopDP@d;+_XZE5{#jUud}p6r<ZH`(s6CEHE4Na)ZHxImpl2$L&uZGGEmUsje#%c{=sK!j-SGWp@-cpzt0(gK|FjPI)(LUH1-GT~(`=Tsk$x91%;g_c=5h64B>DQOPW&EIDfOV6-+Jg#s&7%Z&D0O)K4d>7iSN_bx%s}>pOfp)RQWyNbUk|hYIpzHK))aV#QA1i<Z(d1#(wD6)E;M}KbO&Q*PUa(X*B0;&|Yef`o|&i9ZBW6o<gclc@jE}eEsuU+|ON(^Lt;%t?TK0n%?04>~`pco8R>c=jWj-oaa;XvVXWg-`ArP$k%pf(tK8%){yVh(}k!Wv&PMD>3F@ucwV2GoAT4~a4-3;@lcKFe9Z2<#!t2K0QMU-Ut`Zhv(+rhXUEdNR@?JU@!ikk<e=||((gj;_<YN+jI;ai^6lViyRUXS%hx@m<W9HpB_@!s-fWg?_syGS_<5>r&u}a6HId&tPS!u{=Hq#)g@zn)^P2^+|GI`-d2>QE=V$+o?)AH#BX>_8`R{z=#qwir_2m4G$E(uy+}f{P{E~dfj`eQkl?6k%{NQ44{a{Ar=6ty8-f!lOR310F_IK-Nb5;+2zU%Fey4An73y(`?E;?UF^~(46i*f~T(RDFO=1I5v+O76HZa*|8*?lE_5syEP)Z=dDv-+{`Gwg)jH_trd_J5(CbSr=F5kIeY7WvW5Pxy!4JG46s7P|ShSM&3(V0NnA*Z(d^<AAgH3YzDrOTFlME9a-9`e)?J`K$(~(mY+hFI>KSUl^a=;(5Jvf0<RY*HL-tel$ETk^kPf(fkej()gp4^5XYS>3%oLN0Tp)hi3XtE-#HIZ+&?@S(Zw^Jl^UZ18Kf5kI%-#IP&Fj%$aKg`SLh#%+DZS9uLjl3SA$099DvZc%48Rw;cn9urH1C&Jx$S9_hKGR9e4@RC-S7QwH<jNzXMS{R#Q<b5Ji9OzS=JbJO|V;Vt&Oay@62LLIi+^UC$S)`t|MzmuQuM%kXcJ}S)zlo{*!`Fs`Y&4&#hXMR4)^+@vyV_ebg_T#>tpA0HNzC52X=C-H#wZmDS>UV5g$@4MK2%dLK^Dgy96t4qG^EC6b()7L}&+F8%3go{xzj`o&%S-byt=arNZvE++H?G;jzBI2h=j|Y0o(HPKQuw&iywuU_$sV`+9rIXqLNc$<N%LWKmy_37rTMdxCy4UM`Ha`$ouk|Gc=A&-&M#>`ude(#$=)8<dxW#mKU`jZ@9=-azVx1ATrNoK4f6b4JyMi?>3v68lt8}xUf@jJOTPTx^wyW&JIwvJxPIxqMp;pg)?MWHAl0uvuj@$fYv#jPE-$^`sW&!odE}vMJkdj6(RFz5eY0HSG<%-7-doMYo_u|z_gv>+<I?Q??|LuRGj^r9-7k2L)|=#{bp`poTmP{W`SN?K7CDgD!=(3Iqh;hi`+4b)hH)O$jwWAzUp78nz`pd}t>s(K^+@XjT5uMZm)8>-eZ>7Itv_h~P50aL^X+=Ym!FU?uW#r%C+@fBxwdj8kN-D!kpJE~$yZg=?fvXpS1}8<PPgZ?YaPb;r9-+s|6S`g%9dW~_Uq_c|8dL;OSk8_YrV*f4QF3kU(y^y)9wA{T8}b2j!1XQxANV2-E#YE^50wUYBYq8Bdz;6%0+Q|rS&KyYcfASrS&mq-^E;yyv}xf8<&^Y<;EN^?dN5-?m+D{OP^z3THkx?OY4D3;S1bO>>E1g-{o=Pz+Kbre!;q^((4~Q|J~P7jaF~C{n9$5!_SkS1M<41j~9>M(mJQ}eqk;zt>5a~eRzH?t)sepc^y?xtjOyD()zH{w^oL|-(2g-+FjnilGk<htL?Zw(z>+sbbGE}TE|v1r)Ajl!L{z~3`=BRT2FQ^d7NSIe>1Kn^^duz_W`%-d$kt%&dx&)*!#z|K5yQhe8ApL<JgB(Ud#UUfW05ymJj@f>zCH;Rp)Kq-;>t)9lN{px{kb$@M<EjOG*0<+So)cFYi;N@;pf1*H9-MWnbP0@x9FTNc$${sIT}rChfCmPqvXS@5|^%RGMeW`#UaQ-rq6ODv~enAGv&a|43O<oy$x6P}-aT_N9F*J-!yVN80Cd`SO05%a`}d%!zfl9(mslzPwMTMg(#_(!QP}uo=JSN&A3~O?|k2Y2VO1;7|Gc-acciYy3VW?Ms@^XYx2C?PD5g4tkEs`<~johCGjx_DPM*F!JSnRjvC?E-&rFDxQzXe{bJ5;}!YxKCkm&ZF(P)_l2F_-PxD+k&T^0*q8R5Rbx1>(@6W&T8(&q-<9^Y&5|>@yu1&-v=O}r%lqc)_MlUAUeZ3h^I2FH^@Fr8uO81LU*5-87X)Ned1>EYS+a<H`8xq^yGj0g-xY*slP`aVpf}HVnvNrVw_rXgL%#f-gB}%mny<6_cM;03Gsu^}qcHYlkS~9Cp)ET~zWkkrGW`Vk@^>9Z@^e0}^c{$E>kF<&`ffz~R5?S(mA*4ky-ScUf0v>>^<iK7j>WlT3H#D_FHXPB<jdd5IN$8z^3r!TX7UU2-}?^d`@gxo^xckmyTVzzF4A{Cj*=b7m%j@#PW9pP(sxAW@xEMM`tC>@Hj;e#J0)ZDQTC<pn)H|Vxqj(8C}-oM=cv5&-IV^SJo#?lS%tWLJ@)JMS#geXVk)L6A1L0+kb$;O$Al^Vx%9vPbSyIPfA#5DgSrj=zn_lvvD)yN74gsw;CS#R=#St{;4J7Za2EJB^aBs(+u*z&tU+L*jlg-q`JnZ|`M_S#8sL8v))M$#16%@J6Ct=Av_7~U_+w}z@W<ee2*K^4LE!e_&d`s*LK}cPgF8V3z@5Os2*I@wf=fX?!KJ`|DI9{YK%EM+2*H`q<6xni!I|J~&@aH-z>5%q$3q?9@!<Xl!R--(TSEJQTY_6adxG0SdqaDIdxI08@!)vmSpq`vdT17SJ@_>AHuyC7E>z^!U1&bA2*G!tUSL;l-9ZSxZp9WWPFZmhA@~~fI`|s+Z|FbZzrm$Zx5&}b2*GusHNkbkEf9j6A_RAUwgb0A?sh;3?gH%y?g9>hwg<OIzJ@?MfkVJupux6!f^EkNM!SNM$F6qPvbA4u9cU?V9dL1|$nWC#E%;C5{1xz@;ET{q@I~+mgy8MaZQ$+T#n46I#o&q1@!*NzPoVw5pMbj~1cyS~gG0fs5rQ>nORxrR4s8K;-6zeVt-#H};_v$5*aM)U;7}ZI07CG`2*GWj8dyV}Z4iQcLED0b_6GL?PlqOeg{}ur2Y(Me4gMaS4ZRB%dIv1@I#}o_a5i`=bPHJMLhx4b0_a%q0`LTAKX5<v(FBCx2<XS)2ykC$8*m%+MPGzq9XcI69p|hg1h0c;gR{}@b<hRib>NxM3E&B6(@bbza9<ol@PDkBYQ=Jd;Mvfj;Mw5ORt$!QK!<`uz+Di6!=Y2b;ovFI|A41}6A^-ULYISgf_Gc-)QTro<o00A<-sgMa215$ieRCQ5rP|9Q5jkcS`l0f{I9~A3;ZvR^*dA?Tku)vIp`Dc6SValLhyMjjzTX$pMo!dA4A3YJjQRq9yrG;U=MIPXk&0WaCIv*Xj^Dwa9eO|XhX28Us@vs*R#SOS_WDfTn1biS`1tm{8C{RefJU}_&)S^@O|(ZTc4gm2tEci!6tIy7((zK=yLEL@Ji@x@JjF;=xFd9aI7uYV-bQ!S}_pX4LTUy4IB&&0f*pz2u28QXGI5S4`>%~5AX<RICunj26PH|2KXyzBKRxt4&<BAUC>0Z(4F92;0)+)@NV>V2J|dg=sB>^^WY5dLFHYpAB64#e`iIC6{!fpHxPn<f+mB10^hUZ7ibbR8T<`&H8dH#8oUOY0!~3Y)*u9bju1Q#A$TJ+6}%Cgh7f!SdINk3{0BntYv@nl*WmmftoOho1Q+sncg})E2rg@Bc@NfK@mu)6A_VV+CV^djv=<@xYb%CBqoLn`qru~#tHI;IanLp3HRwCRF;+~nViiKL0i6Xlz~4gWgTDo@wc@fB;v0y42*E!<*Mffl&xOth&jnA0&H~RuJ0>FpkAlX4M}fnv=n9R3#(<;1%b=^k%fN@N2(+$?j}_Grf{Q>OD9lB`zbUMT!M}kIL05rSq3;eM1RsEY3qAl&hpq*$Mc<_(1Yd<-244lgP&jXeUV>g$-sQI7H0VC?K3osieIa-wbguI5-Vr<xI$3#luL*YDgM#Crqrh?CanLa3T}}#)wp}w<4htTR5Zn<VI1(BKjs!1-E(0$GAAueQAI3F1f)M-=Dz5QE{1&X@x(9+)aC1Z;?&<R2ve0Vavfx4(AB1{CtAVQ_pS%%*3qVCa6~J%7KO@Hufe#^Xentqs2~7v5BR_5;1V4wq06z!k@pzX*f`z^Y3l-;(2j}7q_D1{iAOycbyG5Jcplvt7H*q|{!>uxLR*Zm71CIblK|cjYfuo^Qz|r7H=tOWNI08Bj903l8#(=}YgRF2^G0=*U2*IPFgTRAOel$Yx1cczJ&~f0Y;2F?~;2Gdq&?(?4IL}!K!Ly;$z_Y=hL*u}ogJ&WH>(Jp~p~JvBcoK9dcoKNL71N=y(4pX1@DPOH?g+u5&|%<Ea9`+fa9{8M=m_utaBpZ7xHq^fG#cC$+zlED?gs9G5ZnhE0qz6t2Mq`J1NVXs0`~&<gboDv1b+f`fcrzkpbl^tcrbJ%crbVrLhu;qXz&>DSm*@sSny=%RPbbQ0(1sA0sJL&7Whl>T<C1@T=0D8=ivF^dC-~QdEhxv9Xtp81#}Yl3-D(M!ST@XU{_uWE@F)-#jU7}5M0HI(pFTpq6E|*TmoDOS_NDMe_IG4_ydGsFK7|47uXY880-no11$y?S`wTGoF7^SoF7~iS`J(kTnZuB*NWPT*p5(?T2NnbEpSa}IdDyI0JID^09+kf5?meZ2Q3En16PC=23G`Ef))W6!L_M`5ZnMExGuB`xGuOp)E`_Q+yq(`+yvYhA-Ebsun)8}*aut?A-Djv1h@b=FG6r`Xd!TJa8Bq4;GAF&s2A7+tUx`LcmD+EfaU?`0Ox|{2j>FkgBAtn1A9YDfxW?Hp}yd<;PTK4;PPM<A-D##Hn;}3jujt5>p^RSh1LSs1Ahdq3H}J&5E=k(2o8i+2M2<Kpnl*Wa3h4^X3&b@X5gmKN?@T4z<$<6Dr!X&Xa#T+a5IG9N>=2A=73fJ=K#M_Sc`(6DXazYTlfVLf=fdEz$L*|5rS(Y1h;}V0k;CTfi?rT0k=d5{tzM97g`DI3s!9B=}Kb3k1U*K#iv#bfer%?0e3<O?rg;%=osiQ@EGuy&`-f%f>$5}FM&=2hjj4B;hpn;`d@pz`zM|;irfF_L;g$mZC(3cHnZw_yU82U!BgD#*3FrN8h%-<sw@8mVi)Fl'

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
