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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_006.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_006.stl', 'source_sha256': '637bb1103ec82dea40230835a40e356092c88bec11b8eec8c1119ad53ab5bffe', 'input_faces': 592, 'input_vertices': 421, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4990159869194031, -0.4550439715385437, -7.77156344611285e-07], [-0.18570572137832642, 0.07169562578201294, 0.12054625898599625]]}
GEOMETRY_BASE85 = 'c$}r22UHZ-_s0jj#2Q;-U5&j(1#3`8BsN5`2W)ErMViuVD5C-fD^;4vDwe3&yNSA1Kn*d*SQ3q^(P)gZB^pb9@%P@`@2vAC`#<M@{(p1sx!?EU?VbDXE3-ShC*GbVOI4TXUqfm7)41T5%_NCi1*y6e<rfwaFv%~xZOHW5PEr+>^M9I888pJn+s8?YlIAv>>=!;MtXVfxGdKS(&03q9`G<x@giQz;9~w5<kMlkgg2Me651%?=x*uydckR%=waKMLYtuZ_|M8zQOTlV;eDfIh(;M92-ZDDtP)`Tk)b4^qZmEC$sGgg~KR?gCt**$W3!PMMJ&?CY&u!ljmz?AG>ACq;U6q^st_b~QaAnNUeU7-*N6cU2a$7Nf+4Sg?n!oRfTp>?z*}qzzFy4%_DpxKKv^e6H_wv^X{7M?}l;Z-ITTWEDZB7{>zI;}u{x437{9Ff>TfYw$xKy_e<rCF^y})mmr~IG25%YiX_er(?{5wK_dEtGPTNdUET<LpP<>s-O8wB3(ipot<<2MR?YcciD4ioz~_~nFp9b?^kxF1*Z{eH$GM_lQ6dxgNCHKhJoQE|d}m8Vwq?<2ab6nOoIDwluDS}w$KJ*je~QH4ZDTpH3$SPydSA&T#nv%(=ie@E=!I78*;Pc91a<t9rgpI1#Ba-~*HA&xaNjN<29N)pE9Hi7bVaTj^_VRT*3YAKGm(%iIKn3uvHD!1&<N*3~2>qh;{%}aH}ZDo&T331l7rF?RvRYL#LO;v8X-!#<`w=S)aE%2K)sQ<mOnVc(MouoSWt)+ckuGpgIQou}=o1MN~rsuY)#N`@Ih5n}VA=JOxqD6YHjO<yUzOIU6ZfRF%iJr^gk|7`Kd>55l|2e$O5m%~<`N$Wao>B98yIzPdfm>3yit&#=QMr=hvfLqmTvm+lwVUFfnG)}ao7(kV;fPzS#ODh6oZ3S14fWBusq&9Yg?xGhQvT^}6CH6|mAPw#IHi46E*bJs{%lM6+=@(c#BFC>a)daa)>64_$WwN%PI*2{OLWAQebt0~6qnbh)xY}{Cp+S1_aC!`>sqg<+!DKZwGco44En!XD8vanP4QhOr8?r~h(1|DoKv|fR}Orc=7?LL{GK7?Gcil$CbvIQ9P*(3LVPKA0mX0RlP>V?(Uec%r3Jz~4hdDc6dWVuBh_t6d|r(hA<ti~(|zq#;%p&K#2UJ<)!7g()M05P-PfG6ql7ru$I^YXd18RT*SDklUH<FQLj3X-sQ<xgTaNN}g*^_>4UHSm4UHT3wUKN4+RhF8^j{qNRO80|Xyn>{w8t^*FC*9Xm&T3z$jG&QWaozUZ{*tgw{ydKHgat}+s9>C&ql7TXZw5^)~D2Ohr{z+<Hqw`<HmE$&JE{=#*O>e-ruk<?A);a?Qsn2U*pF0Z|`qd=XP#b=k_>;b*^m9Rk_8d2fYv9m#e-n(zpUHUAVSJ&rKoi>HT&l&TRuXzdu*#Z;ff9*4eyAjIVKPu^3+tYE1KzF2>imsj3)XNq<E5g)e*(9dTLm7WzxEztg^0Tr$xSmm6*r<5xXG`y#g}(Gge5*>VJa`4IK56P@UYE6du5`ILyI{GVBp9P<6;g!uBZdBj78B{}5XMvDDc4x@8pL|(EZZXQ-<wUFnt0hGV<lw?O-&T$v|OB-9#`S5gqiX(2>|13-3w;NENx0a?j;<hvOvW0b$_Llbhn&+vGxUJmYOkrGGp3(iQ@W)h#-1fE5UzvW3&W%sXuX4n#L6!`G&-jk^^%`lFBQBTUEcV}4NcVm1zNzJ(bx7b+eul6g<(WQ;p3B%@^2^RKdaj*g=06;BTZ9-#>6S<9(7>f;>uBDeiE*s;%hJ3X`dj}hh4)Khe`)+F8kbwZd?A0&lT^<RcZB|O^8}igU*n^NI6uTvor7=A6L>EV>VN3YEFqr*Zgj2|)t)27ukTFr`)zoH5XbkedLEkIOpX-#$6isnxomW(&_5HO-#w;H7x<MtisKYMS*Y`=RFzA)@qR*{gB9w3uF^<>*9fI^yJP++A)g+Th(9f-p4;~RPrNBl*Y{K|S5BmS@}21%{;jlnJ{Y-tEH6jTt@TXmI*}iU{WWenD)zU39(mm^$q~10n<e(&ewxmK5gAF2xcuZpv48VaT34=K$&R=!e9US+S84^&d1CFD;)vVsg=Y)niuRy<ex=WwMs7R0FiVJ2T%UNO-f51w6z88Q#KFF>db+N1#BHM^GlV#ykA-u<dMS?Xr<gBkc=%jB*Y>qMSmf5XxiqdpB9}Kyl&67PGYe>6I2X(j`aeveeb=h&Y(1COjiUWk_$X3{^XEqtr~BO*LY^1?qIEvuK%fvu+ef#`Ocde_+(P{e#|{(XBqY%~?^2T9w>Y^wtdGWx>)*(=^{;VbJvDCJ7e=n_3ymB1g^_Ff!p;r*!pOCKVZW|ne(n7Y`^Ct${bC=lVZRu;wqNYmHS8B7*Y=A&j$ywTxwc>IaSZ##$hG}qAD3Z0+v6Mdkv)!Ko!jFW*13J17}mKxj$xhKuWMN6_Be)hZjWPF=k_?pb^dfPt?!Ka>gQW|^dj{+t(}`^?BH#)FL5bx0P*r}JJo(i=1~6;U5U4=rN%KgoVQ-!h@+Um-MbKfcu<XF&KN`SJ?i55d#hb)zpibF*Q-tZt33Lg6O^}3;D|2=5?6|A5P#34#y1sb5&xzv@h6JPr9N>K$K~xgmH+J*tF}G8M6Sgj0N&sq@S*fMtzv|MqkjeB%7s_NP1R7hP~r=p6ZcP6$7_20gyOh9B_4l+@{Aov{MGNorv_5pI{H$a*lWbAeM$XKbf*55za!qEjT+x_xh3(=1;o4Dq3ddO+jfk2!xB{gT@{FjZzp~(SmpAvM{8B?wT8Hd8^zyuN#)YSB;uPJ?N;-A(~qt@GnV*}T(!TnVKepLGn@E`Daa>-c+XM91N*CSEZrZ_bz6-j9(6?RZw@sRFEyO_jcCfhN_*l(-o#ripzFpCqxf}N3G*(ud}tB)oH&Z#g1B<N={fy6wB%G;D{!obfAPWuHI8+)fmb^taOrvNbNc;g>9APjqeiNAP}+lcC~;1|?<}KdQJw2M33V{JZ=(Fa`TMNC4wijIG~STE&g$!F``|eB-}2L0ef^co4JiM9*NB&yM0MWmPjOyfI;)>Ysa^u{?R$y8=uFqGLeHtBn*PLl1*q%Ra<sqtd`a4CKC55n%7zv69Jq(?S^Yk;4WREwq$eYYzr_BnR#W8KIaU?CXqXVkoHmK#&lya749%nMm9NOPef^TSbfXV(?L3L=Lj8a0LLBFh98r<_N4pR|Nb5&&`+JSR5#QPkJgF)1<*8KXLC!SqhiVhYIVtZyMAt2TTcmQIkA?YFHvNY<&Rdg~f5=1P+IhacKJk}#i6_!Jl%gt%T&n}dr5w3U9OsX1WENd_(YHc;lcEr>c&<plZf$AdB1e2l<MS&N>FZ|Oh3C&2M}N~!;?gMRB7ObMZkfc}l`9g~NsTX31+J}=YQ&YgWsCId#F86F{CO$j_wTCtoB9mM5V#h{1N>IWBK<m1JX%mb#U+T}>Pp<D0rfxZRHWY*rrY$sNZKS7>DQ<E#E&A^){hlj`KM5yzvOj@^7nW{{PcdhZsD?Yfou02{|M^e{&k^#Kblwi60i5FP`|Fs*YLb0^=YAgJ;)F6+$Q)j@t>R1`EV_t-jDe_BL3ZfXuON}CJP+*FRA+?HI8)Q7vkD|%Jn|=54lAg=Zw;LxB9+U>U)zo?q8DsxMYFXT0#B&@IAt}SBc}kW_7(mamHLEj&slAwVa;6RVXHo`<gkX620Gkb)NWxn{*C`l%jb#Rzw`<q<P#yHI9^CK)gBa3wd0XOo40fqs9<d#+)h?_ScT<w0;^MC$63Uz3BU5>E01xUM#kuYJVyJFmas!Qh)mXT8TYKT)SU1r|-d)vHOXSuCLw~Y<{R`<=w<_{#b`kqjhy}N1=Y-S$0-hCUD$mZTZ9{&rOB;{Vt7j7dh7dzc}u*vaf;TK5GJ3?yn_|bJgU5&js7p2z9gk6p|qD7w&W)e1Pxos;(01V_LpW?Jqq@5$dS~4kZ5h3UU3!K8+Xn;`>y$fwWJh-{OdC=S;^b%LRUGFx9^uapg*^u&!+Fn=Dp&f+DO>>*HDUJ#1u*uwSIBo7DMH9?rykHC5xAzHp}fdn!`c7qaJB>c1pR*uU1QdGtNS;80=TSsGoV??amf3-z>}-b3{{Gey|frufqoXScs_&X|J#RG$+nZf5a(aGOu-rNwySI6sxc(J=x)>_zV<S9Ya+U1F@TFO*v~DNccpaDJLjIH}JYl|7#c>)G`8%y|OGKD9gtpEW`_KW%MuV+4+UB&AiQc^NWHIEPJ_@cgr;w~&w0sWCnOeC#Fc3ppffp1`$yrVv;54j_*Ek$Kc)dM@hUM?8OGwyzNQ24Bi^E_hE5;<(S+9-g7kzqQ<j{cGD@TjbjNhkWqsJ%n@87KeGyYa`5;b@f&HeZt&U!nrM5j#GUC>I(N4tNB-of3v!<o~58pv@epX2=_rbFJPw1%azCeqWiKm&7D4{+sX+0QTmFW_u4teW!nor>TQ93Un^Mu($5cw<NUF?{7mcls~?Et{FItLQs+gvTU?-DpXR9{^gJQ7kT}kN`AB2R-}Q8XFpmpnMG0Jczchz&Z{b&iVNrK(%XQgHn3b2ROa2pdKN;kZ|I@tVp9}`L{;z&A*s*Je|L;!*Kj2$}F9T*Zm{mu+Dzo=_xuC0{T^X9QCVc$N8ZrBrS!-r3n6-oEtPQia%v!;>gyz0EbTjCd&`r_izA>|p;2T2MXI76{17;PORbuubGhWi#%<4$|=bCIw;qP2Kqg{qsX=Y`iOQBs3(^sBZN%#^luASf|=;O>zGP@0b2l{Jf#mpYVKZQPrzx@vX7~0B=KS#O+e-ru$GrrDlz}ukDBW5x5BeaWfjo;vZhdzc}ZSc3DPctiEb`Snn=o854XZTytUm>UK@He0fnVn(w0RFyCpF*4aU!YIo+IQgZK^I^Qzrz0peHLRp5B(7Bv$*y{_y^FZFos{?e}+DaG2Dc|4!sJovY-pmUV>OFpiiJ3%S=H$1+lnZiux{wK8f}^iRL>Ox>(od^OOz!HQMpGh86xO^a5sasC^vfmFqQ#xeod~+S#aMI`lcT7vr^Y(8tkE!F;TQE<igTV_yPoMSB6pu0S6_o7XTIb>#kxPOm_F1!{Q)wOWaKt;97?BJTp^l8)R9Fi+<()-22wZzmzva_E(4XX5odP6qPhuUm#Z5}}u%y^z^_)P6q37mK*OUJ1}k(O!tUd=4Fpb_TAq8h#D*YG@0yJot6+YoNL1;_rFTYvHq@*FxuDj5!!*4mj5_%obsO7C^_rCqO4)99*ZNZb^ul0+t57660KgnthJ3F2S`F)GP+qQ&5Lg)O{6nGJGO*B5Kcd2(#%J$8?O7>q*Qe;F=RqYp$naKK!AR&^9xhh+HOO%v^^u3r4+zF&|t9VVu*TGtmyk9L#{$<}Cz$f}pi|n1&ptLZ_iU897XZPCz>lIRryzplwDi$3w@UJ%yPcYUYP|NW}OP5ZfO$NI<Q|qh8|?V<GCf3^695mb@K+90H+J(Vl_1m=2wX_7wC9fKEi)6Jr_-9f)=xX1&qBH(tYacZvT7i1L>)2ClmxKR4(JXnQd0i#qp3t-0>N%mrh0LG8Hii5PzHlc0H@uISel^TV|_=5`=-2-+i1gQ3tf&>n~!`a%bx?SZk#&{NU&L@fg01E9O278BtoLk~eML*av=yI{-{;KxIIBgYW<>CnAViz)Da&_ghm5zwJ%dtpoipa-J;De~^mtOv7B%(}t5K@UfN{<>j^I|_O*+I<kKH@rKvJM!cD6V#<Mv-X%XKGyG;U1IhO{txIMn7w3n4f++@SHb>*e+m7B*<EHAVO)O;{}c4L&=;6}1OFrZPtaFzjTi8LL0?3!PvD<Hf6wePvp?aVLw}F4T!Q`+?aR2vbNCm~+YvV(`V!iQG0ua~KcKxI>?-^<=!+QVRv6ct;V(dMhTh0*1N=AeT5a|tzrD~`(ay&;wnBf0_HK-GC-h}q`x3^q6YLWD>_xx5h|Tpb^xXly6YYKI$6xm)#(W6+u&#X&`5uBlfY%<t>kokMMcjN`YX|f;X6q&XD4A-r0eU0+7tkA_H^Xny)piT&vjy?C!skQp!MJuIx7}cSp!whCGK)sO(HIZcGnvgozOxWx2d>5Qh=g$+0lx`40y>;o82ozpP0+KM%|R}6ke{aKqCHnv*I9VYF8DprQOGG0dK=nN7{fOB9ngG?^DxeNm{+bx;x&VyXQKTXGap>v2iKm3>+x~+gK^ypJ{-CibVp{c@L}*;ZG4%H!MMj@%v_IUHV*lYL$1;2KO4FDqVH_vITN{mh8$-iw?W8v5XKaVYmLSA#v(S?qY;<K&to56*E3rUp98%bI)&Ni%oa0S0lyr21#~KW3Umry%k=~&{#$&OBYa=ze$ejBJeYmTY#_WB^g!rd@b1v=crDja%mSf%K@Wrv(!~kFbv&R0FqQ!19ss@^7KCvGAyx`35VZ-!wY6Gtod@GO5#vonu8H7%;d?=6Gs|L@%q)S~GG;5`lcAH*XC;j53}(6T7Wgb^3-ns}Z0NPn>oC{rFi-2ib70w+yKG!L6_$)SPey*)8sPeK7}xRe3DEJ-i<pHm3t<)v?*|<W?GHZ|+8=s6ybttv=+W>ap+`fHg7=0V1w9PDKlCu@A<PEB_lEBe-5YuUjO)Sh-q3@ghr^GA9uDmb?*r`%Jq~^>^f>4#@P5!!pl85`K+k}l$t(sw96kg(1a%LGaXpLK9QX+MFz5*A>F~kO)1jxq`$JEIo&-N0dJ^;)_|ec~pg)5j1^pTH2>4;pBcO-E4}l&E?WvnTPZ-yIoaj8^-V1&Zv=_8Hd~axX=zj16oZg*RTu*>;JrRB|^hD^%@WY`eLr;bGg`Nr>3O^1y6gm=q3Unm&T=*H#bD?A5XF|t9Cpo=aA4xE-S24?kUjiQky##tTd^j}sv!G`~M?1Y+Ptox6prfG`_yy1kbR7I5XzmlB<Di$quY~4419~ZRy3@NeF&%ylbUJhzd?s`z#+e4=dOrMY=-C*<e0T+VKJ-HPIOsU!v=BZWIvv;Gx+gQ4*(dOB(4RoNGHc7M4YT&}?V#I3cZ7F^cExMC{)gSy|HJGJ{A=hp&?Q)((#*;*D+^x^x-7I4d<kgo`D?j0F{=yi1YH)so-R&3T&Fa2ZH%Qha<2{E4ptB2sE1gtu)3&CU0hqMl?k=%3Ejwv#@h(FHUj6`gj~7q#(Y<1F3egn`<Ph=co%3F^yvWOx-+v*@Lk}$LU)1g4&M#BJ9H1sbq~x_4{$eFH_Tl(T)QL81#|9#{IoUjG1f?1=+^M9pj$(?WY(Bj11J6yHuANg>qCDCUmf~G=o;`<p=&_D4_^uTedsFi??G3At_WWWx*~K1X64~a!k2<B3H`T3#`RnH_n^6PErC^nmY|*Ct3o?NSB9?+T^YI>d@bl|&^6&3K-YwB$gC-R6Zi(u4N&(cFs_?3YXRR3zA<z&=#Sv*Lw^Ka2mV9oI?x}$*MRo+bShE3<p1=)EP3~jpIMUdKQJ-AQvBLd|H@9yrFUOqdV7}U-<wG#*nj*1(JuZ}OZqSGky8E'

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
