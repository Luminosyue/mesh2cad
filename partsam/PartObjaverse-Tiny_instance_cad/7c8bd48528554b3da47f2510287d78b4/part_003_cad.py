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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_003.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_003.stl', 'source_sha256': '3a414a72dc31f299aba719af29209e2dfc035b02f3e813d2a2d6b77eb3217d59', 'input_faces': 476, 'input_vertices': 292, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08079324662685394, 0.1943415105342865, 0.10947713255882263], [0.10992258787155151, 0.3529123365879059, 0.2584940791130066]]}
GEOMETRY_BASE85 = 'c$}qM33yFcyWSz8i6jz&5@MSYGcjv|gBn^5(He_7NK#`c;g{0<$Iw#z=EM}qj!+sT#>9}Y5p!t_siEjW4W;I);-~kl?|sj8+~?lsxzD}F^F81Dz3W@w{?@nGT6^uCM`V|x?g1KpRkX;y`+M30HBE`P7NAXt9ve4oNc6b+v18)hG(X|h&#4!6?HLi-*G-$CO$v#M9yerc$a{K7cub3sx_U^==&^BQ2gME?JvJ&@@f`<^92f22#|<4cCfZ@wY}B$*UA=Lwy82i8|MBPLNWr|ExoxjXsqBPPZ5-NYl6gXDd&PFb8|!)sZ>{wDq|&yX-td2V@U-|9c~5wImEX21-fR$3AbuyRN*wK8y6~22sp7A9nE9i$cbf`6)<^tx+XRWDJ^oO5``X2FT{BtxLHPCCwg`Xtgv7BtnJT=^XA$_K{Uwe)KH<3Nm0rTze6+LTXXZ+LeaPX>GOj=E80W+^#L3(!y!EHkXT&elUE*o6BZapV?i7D>-(RAQx@R{jUiW(<{+8me5XYV*yuDQ%>T=RU^0Ai8&Jx~h%_-y)a!mL;xtYRG{Z7VZ{e7YE_Bme*Z~Cs5JS<0Yj|yMU*eLnWEm<h`fqGI;%VQ7W&6$^Eyw(?C($Dzx+6Kvg`45tZxuFsAEd7!2M$jhVwR&@8T$TsluNU5H3F=VdndD<Dwn}(?^8>_h5W{)W9{i0Fl81GDU*zfcFhj<*d750$J|P8hW_hoZIv?ADc~ySY5z#qa*D78+J6`Hw>%2#JTb&T$&G3gZ9<x$K;kC)zzLPjLK9_uqj0hQrUaP9`X7pLizf10tk1epu8i}7~m%7=GO-H`-p0Aet^XtlZt+8I>Z}!LrZ~0#Qjl>wt>wjbjuZ5$&mO}-Hh0hHW-cqE6j8mU@1@(SfkS_HMua5hDq^0C#4ciI6*;a|KFU-Nb>i_pDiT~^<=1Chr#NYXg@b<=D80XDy5>N9Q1^*GzSdWjoiN6sOA-pZSKI**k<RNKa*dk5*eUHg_?KiuiKISPy@~`V7am-TL`O<#wDEO^yrC$29`4V3%l?}ddJFZ*vq4--XZ4q7{8za}%=SB%{>zxAs?SEqZ4x24;Ea%1wuO0qX{Ixt!$y4(mD7;ZR75BYh0rDT!MtJLz&m@1t%m1LX&u=Wetygi}uRim!4+Og7x);XDb+z{GB#yqpo+|wDUfB0m9G5so)Q7^`SHDF4+jbOQZ&nokn^($wHbV1{V7(kj5&nn865n``ApZ6y8-%wFjzXN4n(#KOWhK`83(WJjaTxD+HHA0Zm&SgzG7xb(KT4K*R;VfCwUt;4e!^AZ&10uAFPG01Ui-V}3W@I%hxMDZSL$qkwRXAGEx0=Bx#ly}v*wMZQs*lM>RICm>JTzlcw5o;B_Df60@n447~!p5Mu@)|oFZ{-!S*GR&yy(Z=Y{={XZRH1tqHwOV!aKNeDq->ljOcPiTO$Fs9emi%vXsL=WZS0&BIf$&Mw|wEcq;HAiTZzUF=s8!-d!ShD&}%xeU4QmW3}D$#sX<L*B!R!T<hr;q|L$uy4oT!g_HJ7Tzq?Nycj~?~nWk6%*e6XJxFnU}(#rtcBt~a-QUE)M+7gFwb0AAoV<T9rY>qJLb=wFNL>F*oEur`%wQ~jfJ;793}JC^x2L4cU_t<<LX`x_xIaY634pTGEe+VU&g*2m@M<qe!t`_x$f8nlD~d41?&2B_6+gwl`rGhtGC7a-JUgF>d?^-`)8_~#4)yfGEK%ivIpXfn2hzc%w2fXmWqAzkL3p>&)~wT5~oNdJcmB3BI7c`CkSsJ<c2uk76U&#MtJM3+nCQ&E(mWOwquHncmHeDb3#AtKQUgyTV@yHx+NN7ezx8cDdVk_gn81l0PUHLg}03B2fp@f%%AY#-6a2I{V{(^zs7#MYSIVdzhfcx;Q`06Z@lxb_Hw_bZ<PEki5XH)t2MNZ<nI#<ev_Bf&HTD^bIHHmbKLijuVTEx$7@S{#(UwpInWR5rFa={sn0LH!9V&2^X=wRf6SL8oRiwFk~*6;Q)&wT?mg7!`~azsS*%erv0LrJ_y^X(Jh@t-wZsd3j&skQ@~HDsxAu~^JrU!d*c|hJ+Px2i_e+!U8!P8wT>rk(Rp!g+LK(l7UJ}po#Umr7y}lj$V2`J=FPhcw3a>xDhv)jCWtgX5`%jVflXvml$-anuwr2@%D=dP2rdn~-ZRV({((lusWn6YkD8|+IE8&euH=Ot0?=N-G+FughS|b4SExai5&nYoY^li*%BL(x>s2e7{(LDjri^2yI$9Vmr@U}5&sDHl|Qh)2XFNN29E@OXwj5=#>Yo|-QSzY|i7gdq}!@L=yKS;v3elt)%pK`NAyPw2)GNe8B!_%GSiQjv1n1>tka34C`=SzK$?!|iPeE|E0wZQ`6jXS9Cy%ZU*9-kn*S-DaH)@hrAuDrJMCY}os_fUriTNX;(YCmJ%Cfvbu`Jv|`Y4_@k{M`l|bmh%c&1D_g^6z6DlS75K_n3t9Rpe=`-}MuP*9*?0{?|(&&SD$lKU#@>KQv6nWvTKv;-odfI$bgi>-S0YV$rd&;0yL*9Sr?lc-y!JICl-K3f<#*qU3d@752fOJhA`%H9AS+9E`woA!j4j`|;^Z#II=t@=TbDe%r4LZ+MQwyd9W^`nMgtRO-29B=Ykeh<!49f$)}#!(`o=NkgQb=FBwVjh1Ur=ch-p-qX{U3%@l1&tLa^%!f7IS4jLH>LY%@5S&{UY){5|8ZUL$MyBF?6`u!wR6WFR_dVi!+z{Su=#Kn5PsDTT%Yc<~y)dj7!@VN%|ERj~`n3Yw_cDbNUoRdmygBg_)?L~{oM(Psn<94E6?ng!I|bKG+$+2#bU4nRtBcV8weaTM(wHZSiJ0eJ9aF`A;D&RWy)*o~UlLyXX9CVwn>(To*F6lm&X_?G-{Mt({D*{s|2Z4)Ik88v4}8>8c)f%b&)+pTH`>lyg|{9miuzx``PNK{6W(_F0nV`leX(!XPDcE7>+yc&vjpe28(W1p^K(##XE+b*7jlF*E)T`|c78O@$*ISM*H)aveVNrA?;SJFAWmRO)Zr@5;d)H7H0gJuKh{e~66Q($ZmXpK1DtR5S3U8*a4J@KYgj9sKi8c_{&OyaZ@wSrje<O$3*6Gho^&4P;Sb9qj<=`qma`>semj=6&y}}ViIq5(Eq$@x-|a8Ft=A8DuEov3{@iLU{GV3E`RYa*>foD$`1NYZJh1iYh4<gw)504qc4D5~9)@#k=NE|c&3NpGgE{~6YONOiC>HnY{=);Vyz$Lpyw~)%;kmiIsqp%l@_6rV)Ddy!wM3jUkFdU0&&IyqdIRFLXodCF$shYi;11!<dhg?07;8a22R}ocO<gcgQqN&tU8}lA+VA$kbF}*nd>?pN?K`o3;!&TVo~TFrY~i(L`0k)bdSjk=R#_|8d(;un@xO9R@qb-ic&)`u%!h{u@gAKJDZFVE!F)Ja4eKH)Rd{`72Yi329<$GtH?yKphld*KGr((|*voq3x!lZizbkLaIEeZ4N8Axt-sXNt#--h>iTV85AmR0|T4R5!ymG%QZ)lh&c3T+yHzk9wa}nQV<^~;jiysv)_eFcw6!S1FA9)&+F&`GrI^fD%@0`SY=-_gQU%mkOEU%9DS>p=gm%5T6en;`0$Z~V+Ug>}Sk?_`u9;lCHG`@#Cu&kH5MQp_Pgl-z{Z|OP0>#b+wezp5t?w5HYU3jY{3-6UP)?!}lUn{&ZZi&=c%N>m8QB2SV%-?V1ei<9R_qp=MmOeN?JX(x%<HZR0cY1>JYPJRI==D<gPg#U>`?Bx$x$;`eJ*fZEY>A`Qw+nAO8jSTmx;f5AmtMlZUSFIy$~NBr7M~S_=gW(H<g>H*M$yT5f3dH|In*rCUU=Ire&;F7-0#ZkpH9NLB{2_iX2-(6*IeA+-DTe5EiVhP-YcenACMrtH8d3WJv|!xgO&n+zn6IL>Ju*aK@V?{Dg8<Z;#?aQmnZ#u%n;t#z6bN<buzx|<n79Y&P5%34`YAG^Uo6hicb({|B*d%-D_Kgw>8~^=hu6Uuz!4gMtD8@BIe1q;xbRPAHz3^4mgc<+9drg-d42>?t7)OcrSZB4gRMt;Jx6l#`|1(ORw!XC#Q#Eo*zpT-rC3q{O#hnFa37IztKdj)Ac#~TzUJ?6|m3yhT*z?h4BCKd&$#s-4FNq)-~iA_Z9X}|AshMcc`#g@;oyU&+9&ibA|6cLU`-Q`*=Q%@WOlW^@YNlbs~{pQxB=9wseE=y4xdsUu)%#@2?$?AkK=4nE&ZVkXOblT=#JkeAk}bOxCq+hUXTn`wHOuZA4znJ{8`!qbAOs*J_)tyfG{c^>6XD%v<ZDMZ#Mn?qVNqH4pPDZ;kNg;Q*YY^v$L#Z?$Kj{^yrr9WCC9>wX)Lb#Y)8=Bej(#Cazfynmg2uDm{@EbdD#_El}gJ6na{dKKf@Tr3xHeTCQ3|B3xGYA*a+*A(9Lyp88$;wa&b!Y;yFYHY>#`3N73tMN49Z56RDj9Q5}r&OFRymj6Vxi7Y$y0VUpg4OW<ye^)PQPWUwk2}KKZ{9$huAQ*Y9e)M?-<IS4g}jgZo?c>`<e_)Mcc=0VaUHF_@J1Q_T_d>!_N(u$!rS_Pi+%Oqo%g!(_TOsZeQ?xu)bsF0#Q!@9&&^xAG4FP7Mx4*uVqTUCGT-9QrQmtj;=w*#=P}~%IDq}(+8pyOev?1mE8XvjzkN*A?b2R<DxM=*7qRXtw-#RS^BCU`OYT5?kBDr^cND%4XdeXbapld`<?)<)*$~eQkJZB4){jR1m7nf$<xMRS`S)%j{)Xk2@LJ1zm~a2uwbzw5GklT1y*A=!y_+L^&<vcnj|G75(@c1a_up6-eIKH3H%jb4-O6L1$;!k&@Z)gd&HM$p?pNdU-r^@E<Gl36Fs!3{Il>zQ%OjuGeNpGy+AgtAnHX1MkmRpb?kBvyBn)x-|G5YKlZCfD*@ktIzXSC=es;I`jUItG4J%1L+VyIZuO<C5#=G)dZkx!r{yJFs-lDbzWi?HSrxu{a408F?pd!`JssH;w4GwGazxvZ)ljhC-zkeDm>!xWz4yi<~6IXFaHQG9HRbr(p(@!V%b%=^pg7{q*Tj>DmO2jWU`2D2;`?<Zbec8{Cag_a<KFU{Nf3_<rPd|TR#g%eM1#%i~e@X@VX|z>5H~J{fjrxHGQTUz)(dhqx_63T<KT#CEL;afg4E1gLxN<Ma-=Y6Y##Da!6ovOueq!H4^i%DZh!uB)w!&A46?crb!p9x*3%PBykCD4Vyq&yiPp7T$cf^WYO5544@K%b#tEpEIub{2^rO{5NR`xO%zhy3M%HMFvI&zC?CzDGfo=;x2&!MfbjaYG$X)8RASaI_l@=xM9v?r4rO+1=?6dvS|c-n($kE6sh?qJ%g-zW4@Tu<5x525YEgX!Os_NNYsA|68>Mc!#E|85TXkbGa-pOWiI?2M(_dr?PIM-fL8$5Enqovw`O?Aw*N3$fxX#EJ`}?QB=L9Yx{ysKbfFX@|MkO(+VtpeWpk5>EemY-_|EyYf1<9nzLHXifV=N?X>YHEq>Tr;p+qP`4x2UF_EM4<z4!*pIf-Wr=lS6}PxUd}#a8E=y5-CE`l-SGqBCRk$2&XIoqLE9cT)${{s0_3!~MN2$TSK5SE55n>-=ciKvqAoe6KMO~V>6mezhD#VqEJ5YBd?m#?%`ZMAI#51VBA)Y~;O}&{ooA?~{S>kiVe^5UnR=TKT-!A6%#x6#?h(n&!_NM&@?dR<0O<#pQX?qjDL#*__HT3s(!Af7(pzk~66tVKZ@6vXPSm~YAxei%Ne4n<nZ7s3V3#e85Tw<lac4>2Br4y(pI^+xDxwM^aUr;`G$XJIACH{hbLy3pd9!9KmfBGuBA7v<c)!v7=KXG^J2;%O<?Wx-kw<m5z9ZKAaxG8llVx=1rE8UE^DRE0`)z-qru0v6{9;KP~X8%$C&V8w-hP^77xCz^Xi7Ps!0_|F~gDDl*ry<*d+3wFarArbk38a4o^2&b4A;oC>(=JI-ydSY2{flb&6{Bxa;$q~B6BlP6)$YMIrQNhQKZT1B7hxa8xzqM$9~GkvZ7+&9`2gC!#ARH3iZVxE+6tGa{Vs6;ZC|$gv(1+{h<@)9D_xb^pY?Xy3fH9_N*qMHD%)$Ztt#>R^lL-hoOW~eb+*-IzmFUe!uF48J8^TD7$NMh+B?%$x*Bl^#}!0ejkfanfVR@riK`I@5C_n|I%}@%QS75)d`ml)GK%~x+9Qd-b@A!Ud`Hq&cqaWu5-UA|`Xi3pX)F8{?cu~TX^&ug54MdU?!lTx5PwX&5A6v0_aOHr;|?cQdKhImeNyP7+UL@CVx=cizGS~#`phLRpsn;K;uK;P*Y1#Av<ql&qU_?BH&HwNFS1SP9mKncXA#e0pB=m}%6`H=Du#y}>^~__$g5|OvhNdnxV`bQGspY1751c$^BGpaaYwNBYQC#|N}Y+`qbS^td?4-m8unbZ*Y?)%%uvsY7-GeZC05)7+6w<m!}Cl%ua-Du6}eU975<*~65_qImEK9bidglzq2U><+7Hln;=L|0uCvcIw(TLl;bJSjo^pVF_t0KPt+<sgb{b_p`IYoh`7dLe;&K>E^*hOH?;(GZcsH@)*3fohr433B<1D9-YM)KpiItvDS;Kyl=%d=>X*;pfHp*=Fv(hJ?cpz=1rxH&hUQVsfe;FFihcn0xq&=0AL4VbrO*@151n~)uZ8`1TY(K}g6U29k@3MBgX`f{KA8flz{G9kX@4-ph3U^|zR^kq{J1~ERYp^YnxH9d^^mDd#Vw}dbKOwF`JCf~#*cM4Vh<rSAyusWQR%g>2<P=tOx)iUi;;Lu4dWNg_g0{TgC&Wst_a^nusosspP!yh`;hk{|@f7lj4%y<6EaFt!iInN|O(IUDZxZo5_DN*CdBmzc(;*9~lh|(>@j}K+A~&A4!v7#1&udR77f1UaE^#+%`1Yc7K6R${=KGAohbZd$N62Nla9hY9AwEV?cpG&p@iyXg$|4QlKvIbnx0rYi+ZMTSsjSf=YUPtmKjm{&!}l8Xo#r^P;(m6>W#YrMkCHo1e4e~&KS=v9_3v!^jaYGow4L}o`~61y7DeIH6ovOw3h8gMZ9lcLf27{vkUSS#;hXgPkyz<psa5+AF1EstX+I>sN&8o}UuD~`#DCLIaqe!wihIhwkI6qJE>5gCg`d&)8OQ&Wa*O@F=%aiUenH=7tex_EL9Dn}thwTR++aKL3++ve-`S@meN=lHH`q?BbZLqYuV0Qns=Xp@CssPpA(36&iUbt>pZ=@No1aZyBwYXF%zy3q_Gfh0o<WX-_<w#>kL=<h?=D3g|I`a<Ewxi={{ipaUB3'

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
