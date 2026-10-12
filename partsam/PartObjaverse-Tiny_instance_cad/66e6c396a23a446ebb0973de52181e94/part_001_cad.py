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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_001.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_001.stl', 'source_sha256': 'b702371aa4eb165c70bc86b7979b6c5b8eb855c8599806cdc6c462d09eda3e58', 'input_faces': 599, 'input_vertices': 340, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21256446838378906, 0.06886473298072815, 0.17867007851600647], [-0.17124469578266144, 0.14207527041435242, 0.2211458384990692]]}
GEOMETRY_BASE85 = 'c$}r12UJu^l!hOO0Yp?pOdyS@AZ8R16nH9TRE(qOV5{JOBPPtT2eXJdjE<pAC}Rf045&0_!JM;g&S@0msM}Tl-%IzN-E;Qra!#H9>+AK_ty{OMU$+?1wt$_Bf*()CXJiv^twvGAa8z8Bkuk%D$MuUzs5NNF7#pR8w2L3JE^ObmT|^HXWu!9BJ31zz-!ShWjd$bz4ZUk<y!#IxHhfs0LA?hLi;fZY7JUXL#F*>}v3-Wbm|pwTt6!&vre3ugnhBc!<Bx;LA;Ld5%Otvq%d$gFsvkZ$N9w(r(ymkvk#=LvP%FDS>{n@5&VM^0RNY$z_6~PoPxq4kx~YYvUEiiO>@95(r<0Ae8y?Pt{n&2AdH6X;+T&gu#B0s^YSLd#doS%u_k+^k5S}LON`rUOt}FEsar)nsag3w>f&Jx6#0i{^dB47aeTN6)%-JdJ#%V94T_0ZRpp3Izi+NYxmv&<lKlr!VCF5(2$B}2waT#CVs5AU4!LEs23;)qG;J<G_@=vWK?V7MN(%*0>1NkI$ly+_Tamat(Zp5EjTjryW^G5zIyI^;|Bj+`w<e_fYcOrg;_o&079n!Az+l2fh^H7JT=cHY;Ck6J*(}?3-2KkIzk9>ZaCGG0?fv8XE<yhCURB6{`uEze}Sc-XrZ7^@y?TEi-G2&DU#=IBCW54b%g8#H7(qFwB1^+?w5I>+J>bdY9);l5@_PbfI8v-!z-r3TwUI@dy!+(--lpd3$U0c>i*3A(80rgxy5%zgUk$-_bGLEL|SlEjhWgOkV)8L;v8u5Sef_>*@<nv`H@(EjteY|}b`)(MF^&VI*<169yP`9b^IhN-_?Xn&7o{7Ug7AlMSZ+eINl!RTK_6>FOnTvcn#iBop{K%62-=`p-%l+Yhdp6E*QhoGWWDM%uI1%w%md}-OJo;hY;Q`kE-dfm`zo0(D9MBI#dRd)EHN?ZpuDAVx_z7>YkE46Q|Jy0pA7<xR+SPV<rQH}=6LoX$fH>2lrCs|k;v27oqd&J?L_Q_!V%~DFE1^G7&&0`y<JlVa_zT#tfsryFy-y3w>s(UygZj%stT!_R`*r&r=506_=jdB7;*5#FK0c``>!#*3#Ja9Hp|3vUyek#_tj|TM+Ng7{y6CINmr)1%Q^<c+9oWOZ!$0X1_V?H7n0MI%xxdE#@1?)CZZ)fV8YebHJ$HL!T_fYAzg|T@XjLz)%ij*?qVh=iANE9@S9@b0Yga-37b+m1ta7-2g5nX!tt{eP^u;~q6oWcPl|h_64dB1yC#=h>H1e4~9{#J39+&IeSPJp4-o(5gaSv<aOJZF+rlI~V>gQV8l~%2hf3pbWxxEDDwflzs)hxh1esaXT^(&$uem`*>`P#wX_!jS9E1hv~L==GiZ6T}u)h)0^zj?nwovWtG_=X$bPssS^k6^!EdtrY^yq9)eN;ljC<y}y>32$Mqa1i&^8T75L$V+M0PR_x()4h;+8aqCPf8ZXg_y+BLX;*Y-<o@bzS4aJ0jnZzsa}D>ymiJii;9KxNhxY|z&n@uxzk&GmULTNtyl3<iuSmPW=B%`9eqMn5&zwd4yH`-RJ(uu45_c4J;QPM1w2hos-yj?7y4Dl>{{1=pn`cV9W?j!L^s8sCrQLkLnd4~d{0X~)`_t&{gL@!gBl6$(2>r0OI_~*HYccQ7**ITm`_P9i)=0bF5%0^2drO=z;}X<oK&Z?|sfFhm^<y&Xuq+#Wb$No!N4=1UIvg)A>!bDjGsn`dCi_Xd-swB)={5=R?I&PgG<aXoMNLHf4qIU#Jw(P=>WxJH>7B6eJzC;ioca~<E1;gnv}?!YpS#8)pItMMPhIqh?tWja_gMzc;|JVh%3qPFzwQz05OPVz(NE}(_^oTBZ}Vp2-fPwkapu*8f9Dg(|BrC^Z%sm<@VUrrH|mRFACvl{{_mP%zhW*UAHOX0ry&^rPuC*8dI9|(Sr2uyNkd=VcZS`&7V=+SYrl-M;t1w_SsnS@3zK%^-Quzi+M*ix-yDVg9XAdA<Lr+39mnH+llQQ)sx0zZumJhnzLfPbc$Pu_9a<oN*GbZD%ydM3yywb!HQxeI|MmspABy`~(<~nQ<@@EhjQ?DZI%gL|owt3Gb{*sV=Y6>UA8A)_6+<2D-LQ{09!b05h5`3R-cP7!)I(`EKZmHhvgEwlx3}PbKMCh(eU$XqjJSz;+qK^(|Nbgp<bU9*v};}bq}}}7rRjJM`80Qv`>v|)xR+edz#boj`V<X7eb(e)y(1f;Pd04Iv9zm;Mx)M!R!e_n@Db#{Ed%E_#~t>@2IQj+lW~kqpJLye?Z>)y_e+y`Hps+2w#~r2J7&xLweP#&e)dm=zxngU&GFdZQJbV)-zHne(LQxV9loX@pUV?u9JOC6^0!?t?MmMy+z%a>q5fg(;QzQnx_tc}`Izm7iYd4crxe8fcI6Mm@r#l3Dy2(f-t|k6KcCOlh;-aPK8sO@Ab;%pZb$Uh(D}%}b8p-m{yn5!&6|sSX2)ep|8gx*hm2&*yMGt_54=7q|2$+i;+(FEe6~BlfBFpcNn{(u`B4DpYwlFoZFGoJqd3m#l0?MmH$}$L)CoqPY#0ywv=Z2_&o6LKJ|2hqRI-zG)6J-d_x;zSvEDAD(9d7HVZ9$lAkHlf_AA;4@qZhNzVcs*{jGKw{oish;`H&5{<_UsIhJ-cD+=?zyJTh8B&5jo8tV_j^WMxsh!gS>=OQl%^UnJfan^rCzcIe<`~cMXMi;Di#&Yz-&;8-Qcpd7~>Noh`jYb`M4o6?TR`I;FtvA*i@@1#Y=Oo@=%y#YRa=3qj3SnQ~L?M2=WXyY6i@w_51N(I{5$pPL9{CjNhJK56Lw(M+mj3!yU9I|AKc@}i%<6(X)21NL`ODF7H`>8Jyf6B8b!lnWxWlgY{RhuK0l2S}-r?})=P6@CG29#aw(u`!FY_^)pOf#kLH?mLGo-ylzg$bZzHTS%`=jPK*V~)JKXH)sH@`osdz-?4OT6`cK3+vVtDHq0_&Gwagd)!oZKT~WMvwY84T1gOeB^m*0_r~{82kR+DECWOtgN&vMH*w?F|nxI+Ry0Ejt#NiJ_)GL*;A<J!T`kQ=OcBT1MFHq<oVS_&Z`>YurJSRV&2s~a6jBRhWIsM*Egsw_fZ?!8~MERMI7IKm^ZW%>QEnc^K-tMdRyKPhLP1^cONL@Xl$P4SlShj6SB_Apjo+A{!4q|-n&)?&l`XFVBXP*s6%WN?s-EM)ZyW6*`J!z4{+bwz^*A`hx3))0r8tvwq9@a7OdC465rR}%la!GxAC0j?F#=rInu7?_@NGQrBR=ZMYvCztgy1H&x*@=HHmJR_eCkhDgV1%ue#;~`eBGO=H=%{{bzgh`RL+S{jW=UChKYZ+X;10THwCzh39j_*J3zd27Hdzd14=x<_@Ss;8)xm=a<0$coF3Dcrg0E)hg840d~#G!tm$5sAmgey&g;dmi`l_;J$T+UA;L6&n<70agG)jz`AC;;GC99hy98z>?;D%SC_`-TG`tlL;gF4<K8X@yRq+hIj_dE8S+`FARm67Rs5WgfBMH`GM};caE@yHgF5GZIA+<020m}AU7x}K*>35tpA><7dOenQP5M%t(_I-@Z}bCcH$*(a{jjGn&e2vQ;*YzEJg;xYxqf{I_M|4(&l|gMNxO1LBl}io-yicfyeaMG&$-Iw80=%>RrqhQ!TEi<0saNAAkS8LxPSQhLYsRL^CpL)&Jjz{pYzX4yS{5V%xmY5{JWh+{E6#j{zex(S13`Zu-+P;ICm+Vab7l_K>Tf|WZevY_Sly_hmil80hrg#8F|ji#Jm%S{Uz(LZ5`%y%0T?2P1vu-zgpRK&AUl|9p8@({dd5BhadX?IPQ7<l=aeXoO}!WmCf(vdaOX4L$A=cA2ryQ2TPIXjZB>PK-i6`i{bxtE9RYh0`q>EgZiwiCHGy|G!g4H%(m()4ZjC49Gi)K;XSW+cnJS9(~!S*BI5IV9<yD^u7vw=dOPG9nTWda9@d>Zj(ySS;Qzi1>QDmro+e`i`kC*8`t*yaXZA4In;ph|#qS%94ucW@Ly5i8zc}8H%ywORb!pdC%fh@HqA_n$g3L$xV>I&r7HPGQ%Ed*fgE1WTRk>Ji0G@xeDQ!@n&)cQHW=TuL_ic?lEB+$qRl^^^UMK|l*cX=js19F)_`f$moH;?#U(=-(;=B1H&ysfVpEv;P^76CV7v({*lQK?BUCevJ8|yOIO1pkz9n^=<QQGQw&Nu$3iZ}-j?w0nGOHt>^Rbc;kTiT7aFQYz%D<i&70n~rpd)QqoVqGWZ;QThi^Q~H?Eb_lFQ|4p*YarqeazQ<_eQ}S)IN`bLb8+OUY{mOjay05zqA>E=nzKv3u5;PSu8k|RN4{?R9dRz%S@p9v?G^kzY+$dr2Iu|mCgdOc?Wl~S&PSeno-y0??f37pvXA;G?VA0`a=(l(enR}?Z;ql4nbNLAXQR&cuxnkeVqPB=c_zP-cJ;{vS!dnDNZikTA4$7$?t0Xxe=_EMc^7fq3!)C5H?8dEdDR+8=&Sd)k$=+<ICq<7!~fqK(ryUPg8jyP<gdFf?aJY~n0Nhk?AP=wSnoO;nWtgAyX-6D%G2;)7=k|J{iEx5(kj0B{Axq9;h$1p=5M%AQ^wIb?!$U7?Zb2CSP%HO&pc|mU&epWBG2=Gqi%e^Q+kYne}z4$Pd|6eYkpry*@-y!I^tga*zlyKU6W^&`DmNBhyRlu$fv?3%==Ga>8}~M9r<rQiM|@4k#_CJKVct|hWvkPFYRg|?B?^Rnb{U`#-+l4{21i<))V<0-hlnO)D`<;e%`yj0`{>ZWuL2)o}#ZdE=B$e>~~q77hU{f#OM8HnEDI)?bAH?hgFqv45`E5-+C7IYt<^uyKo%(Bx&YR%kyrmg+AAIp924cmbf>TRmZw+CLXmszq*#`=;zc4sOPpmn0MZG%=<?i;@FHt{$5ScR}W%fPl?0x8}C)KUHMW{&a1KI^MB{gh<_!+s?U|45%BNv68B;6YPb(?w@06Nok#yfe#*79tIIFqesgYZWjB-$lzHlF4#m12wT1o1DBK%2M`2zc*j3{T^v}IHum?0pAM&|TpVk$1)-^#K&sf~Iw?1H9MT4#CtogJWb#M+sonsO)Z@d@!XM-Q+O}>hLbHnqSGP5$`xCW<L?w4+!C+aY2JD$f}TEhObo0Y$Q%5UhyCuLx-Y>WG+!AsP~7k2g2SgdRRO5{J#74=UZit}aue9^=S`IlY;`xiSouX3XR>XSPgeR~|w8-^%b*i&q=t{4^PYsBXxa$bI)V15qQcYiMJ+RgQl&xq-{p%GTUo#1-3;*LdbiXw)+;-d8LWAUpA!YF>s`rrR*LR|g-)vqS_2L}Fse>GvaDTm)oV;Xf0c^Y{m^(c8GIhT5moJ)R8eNTQ&{zSF20e>PFvVoQ*7b3e;>yq8cfz;;YKynMyXix1xZBFh$4x$E-gUFSsp5)48Hx9uism|n*<f7C9<f7#73iO=<7DMn0s*(JHe35#Pe3879sweLxFQm>OFC<T*jv`MY52OA<9!Bm<?LqEK?m}%t?m})vZ9r~BuEHU>8i(M9)aK-d<Zx;PIh@>?`ZKvRxjl#Ap45Kip5z$nujCkVJasrZo}56PMou74rfwupCa<ODlGl=tP#=?zknd1Gk?)Y-Qbn)7<!iw<?0<K%4Y>?8kX(jbpW1?4pWN8uJT&GI+{8xw`UtcYwLQ5NIh@*o98M0Q29ZO^HK>)zHOO96H?kMmgF|pdYDscMvMaSH*_G@-6=%tTuLXZopfAYZ$giju$*;)Qs5{Bm$m!ID<aF{9>Ll_KvW_~8tRoMl_9YJ`_n~$n_aS$sHX?T=2UDw%gUQ~eQI1-HT7@jM8o2`5gF|pFYD01@av(LF97qnMb|#0B8&lhp8<V{_1lOVVB-bH_Qe()W<c`#Maz}D+Y67`8c_4K%c_4W#buD=;If;6NoJ3Bg-XW)wPg38KPm-Td#rb@~*MdJ%%aFwoT#&Z<<bve#)W+oUWM66%vM<@s;tcz72=+IPdeo-WU~*G(J8CO(J8}dyoE$-JNev;lB-f_aAlD{qs9t0ZxdPRLT!CDV!-M&H@cjF8ROI?9^8B0E>&kk#^8B0Y<G}g}73bevPr(JLuax}yzvBJ~y{6>v*EQ~^&~zn#f77}DLYG+d!xHw3P@P5p=-6LEhg$U8Q1+wHJ{JAihy5$Gt3^L|Wxopzw&?$0o)4kk7U#vA=gE9Wn9o-^o<A?DE43Wim0X5efh^R6Jliw|nZ_7uFY*|2EVU&$mfVe6pWKbynp%<EnjAnaNe&?UnMP%5QEEwYQE~we!9}PQ$wkPesP)OE$Qo)(vW8rb+KXI|+<`iX+<~m+5Imkbn>?Pp!8A@$w^3)4w~^;j$B^fd$5CU+<H!T3-N*yT-Knj~-O25!0pxb%7F0iS3vyG7J!r}yxQQZup9orsTA5s#dsB%+aA9fza$&OhN3actU|VVtvMsqFwG_D^*@>zlJCVy%>ygWoeW)GCKICRpEx8%_C)4Op9YWQTg^ni=A<v<1AkQKHt>pK?-yDL^n#N`7RSv<IsHe!6$Qjga<P7ps>OAsN@<i%5@<j4r>HzX!aul^YIf~qt+K$|o97JtF4kFj2HYL|2SEn{1S0~p{@_VZWhv3?#QI{G*RmmY_PiiHyC%HJaFu6F{fvS)l$o5nlvOT#Nhu}g~TXG??9kn3Yj_gQvB0G{xP|K4`klm?1WOuSJwHeu$+=}`WxfMB5$?x4r4#9DzF`7D(+Mhg<Jb^ldEOZWe0(m9%Z}Lj=e(G7Wxxe>w2tH;S=c!Mrm&s4b_o-LO_sQ2e1ZPn%k+aBKsTt(0<OS5F<OSp@)QRLN<Pp@t<Pqd(Y7{w|+=<$j+==W@4I=xKt5R!{tCGu7tCP!;U8pt4E@WqFZL%}Dw32^*N^=MnUq^XS8&m5l`Oo%(!>A!j{$~NffmBZ=|FeVOTGZl7{$~xr9#jV<|FenUGE{qV8L}(2n3DgjQcTJJtWk{l3N1u-BbTPyS*+KN^$_Z4Q6ERvPiP5?dX`|lg}PhR-<|s-)YoFae7T=OTUqRHEAGG0NF~1?1V>Zjl>Gh?JVMDopXPoOJcT+{$?s3W3#f~f{C*a^m71yK_rG9qKCV+wQ!~k@$p#L=+o_Al+sX5(Q_1tmiPX_#p(DwO<eAh7WT7j`Gs#=1`^iF&k++a{Df#!vF6v?OE^-?65cv?-mPXx9-p)0oaR~l{nn+G$et%H6khgF?!JAFvfN5lN2);?ZLcU3U&LQ}bX?&)B;1GP9dWC$OoI^c8&LQumZYJ*~Z!(SFsmrOG$;-*BsoCV!<lP*C&rxrZ&ygQepOYVw-<Za~)I92Q@^h{&&tm;~)F0$La&gleu8(O{F%2hbak5b1<HXm3i%>t4KeMKSg%-8}iy^oshu~_aQJv~YEle)VzwgM`g1<8MZSq(018NTW0r>)TFZlv_A9WLXANfy<{ri(c@CwsdOr1;pojjL3i@KaVi=0edO-?4Sr|u@NC$HlWyoY*@yoY>-`jC8ve3$x$e3$&%qCZ}92>!w$*xm+1a4~8gIgfo&j6-lGY87%Nasv**ji^3kp(?o%xh;p_PNvbB8b(#gVdOegA95XXX{r;sG`SSD2)Puw7PTh17P%vb;5O81<Tm8i7QNe=LvSdE;Hn&gU8s&^p`v$P_*$^}gPGu$?Cl5S2khOK9D;9A_mOXrPf-6PpCJE5T|xefoMO@6DI9{AaR{DHolBm}{+>=vCMUCxr&HIFr;}Gv_mEeScTmrecaV=$?~;#`Z%|*8Z;+o+zmT7i|KSj9YXcR%F1Q4>9Mzs|&t5M_twb(I_NF!<H>5VBHXt`(uM3W7Yh&wD;D7q>*7-j=(F<1p`TD>9P3wOOwfvi_OtJp+A4VhE78K8DrVmTD@{6%}@vWBf9}%CE{Q'

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
