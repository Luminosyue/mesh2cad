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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_004.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_004.stl', 'source_sha256': '1d5eed432053f63a5368e498f35cf63e80422fdfaea42cb0bf9ca9fb48bb9969', 'input_faces': 291, 'input_vertices': 238, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09990477561950684, -0.14399614930152893, -0.48760101199150085], [0.09996625781059265, 0.24103480577468872, 0.43417394161224365]]}
GEOMETRY_BASE85 = 'c$}qL33N@@8a^>pd8QCkOI$5NO*O}SO3e~U%|q)diNw?dA!0g84K*Z!XeqrCL4t_Vh8S`TRWSsqzDPpdwq{!8^?BM?&pZ43zr2^6dTYJ)Ue@~7_nq(l```QSz3)DI@0EbQ#Y=c;@>fS&7{8$Eg{qpSP*(HOrUy-#7CI(qYSYPKGd;A5@YP=dul6707ck62o373B85=Zp%oLyY4xf&}zCMi|KEdxznKotg<WcWU85^Yh9-}8t4YK^HA)~{Btmg(TTKYD2v~1YeF~{*g{*_T}7`ggDhT>!H4-`9t+g?y?yfIGv$G?4|*fGWLEBK{n?}zWcwWf=TZ&>9F{E?CH_10ed@I1CU;>}{=@QpF;wu4VTIgPlN%82hjJO%k*n{@*5%@fk_dCk8cfuH;OvBJJqeORQb*UZ{=3FYgqfN#1cBF@mV6A<V9zWCXb&>ro;s>AraT<#ahfBgG&_@yr<<GDu?e64Qr^@yu+^CX@(M@ji--tZj<J6uHGKUEapjNGf*qxptrp<GXMFZ@Z3k15|M`L}HK?0$IaGx*>2+XKIM*g510ohJU1&ExSL`wx6CS5m7z$k%aR2J)BvS=tlwQ!4xh4NfXw9}pq^P%Z<$=Igf}{S*0hF6!M=P2xTKpgrb-uHWD}`_69R7xyFo$bs?5SF;y<ZGD!B_|nIv-j;_kPDV(jOvJ_9yo`QZ`zd^F#vS;s$S>g=gP!h!|8A<xlgw|?9=+Es_(pu|Bg%J#G{d;*3!6#&!!-wx=RgwbHEUH8e^J|gXy@%2v(bM6AMZrDCM%93zWI0P2lHA__(oub(`e_x-O|pnJ9mI@6_fTq$dPvT@P@Db8jXH77k80)bnPVOg%(#5d5n}av|rm8D}HPpjH5PmKE_eII7H@AYWfM~yFF)pjXa}XfN#Fo6}~g?7<~Qgi6oSp|B8IC#Ah4voRK1awKv7D*-U;HeP)T@ea&ZRf907nF6$=3H*OqDhhHHsy@-Fnjd^0s7$x(z%1Fuc^pUj3a~axWE*&iXnLA&g-k7<wP=2-!U*A>>dCZF~k;ka=s^qWYaS-tn^A;iQ<R<*iHQj$R{D7PJ@CSDgKe`L*b)CC{dbPl+@J(mUb7*IyM&H6;xpy1NRk|YMTO$<fl9rqTU-R%ki~J59@kU}l@ylj^4!_M$n~*o`m#z4`{*Xh+-#7;SV~n^4U(dUQJmzu#t0?d82H*TV8trklI11nF<RSjO0cekQw?u9czsU^5yYpU>JlXdW!S&zWhWJKdn3tOC2l(ctOvG#NBuW03Y4G(L&!iv5xx{xafN%6Q#GkMazOibW#GmLY^=|zYzTUto@jK$ukbg<oa@4z^q{Ih1@qLY9SFa#{zXx0J`H-gKKlMU?>hms%|L3DJzHbd&g}nJ2;Ty?`h<5~>L>^;WoWzF@L3>P(T<M1)vEpaeN<yC8kRrYj_bcX`k?;uf#B{wY@wMh5j~=$+YGGe5byV_SUMAl+$VcLjE|GD(8!qw7v+y1;n+Aw~_NIK_2dVJ&L1nTqzGV|6zKt&Ljlayo`lF@oz<bJ^*<SpXyO2lMGLc8`{45?E6)*E-@ktq%;wRvnizZ3EH{6KVJ~;$md$d&A-^?NPo{bhir^7DP+ikk6*BLY68(weV{bDpcgn6sa{dP0r>-EC=pr7~7FXC4$C;d5hWnN+5_@*9wbKn|@ua+b6Uk#OYW_=cX?aBu6JszU{&f|lnpGRx(&B4RJM0~x*nEytl<}Sonh?jNg*1`P3zR^1wzUHnZ^TadjQ^a3SK>xeLm&xzFYX*G1;Yjh9uNA+Z6YHX3E|&3%87cmdK=DiJ;_nEie_;c7QpYW5kI#3x=#PUtV<rBCtlOC_q&*$(V_s_wA}~LVD=*~Z^G$v+&+F#`-^h^ubdOstev3NdKkkX|>*(}U{2$LmgL{p^I-pOwEc0P+41A-{3dFk>)sXfyT(lCO&rCtQ8B<c`mDkT7!uRbPgL;$V#g7bJ3ct@AThZ=SGOvs=hnK+L-g7m^adEo*?gAT%f9xZ~>m?sadpfV0k8<s@Fz)WWR@VyqX1NWr&IHvLzht%nzB?WLZ?s=1{ePtieDhv}tS4b-#4nXR5B^{G%l!Z43-QCeI)N9BPepqk)|d7e153-etlEh0Wu)bGDeOP-+>Ynf1M-Xb<C9ZR@BB>qwKZ_9su*{(cci?p=^N&pz0yBzv468VrZ(c!1F;`+ob4|Cc410;_=i76JB{9NN;^NAI}m>LbiD8Mx$`Cd$#0?Xf17~uay?2e>X#3}xadC|E$V;P5%n6rQ;Ygu5vbQ})l2I24I7WRQ=QQN&J{JU754uyE>prK-fuE|^ZdRdzP2F-zP9G)BEJ4(n#6C|Q8Z8cJovivmiW<CBc9t2C88sr+i&URR&;sJd@y2z#kb8LqfVKX&--4+(4FxAFh76Egm0hE#-kkg`eEreJ^p3*&YRh*kl(frxI5pEg>U;EIeN9hv;BAHJoQ+7+watLU04g>{=2?0C=T`6)&adyzWBCv#^}}lWB9gp%v~&P1D<W`o*DjNv&0u&C*Ar##J8=h?s4@K;P)Rc{TwUnu+gS9eEYg>UY;TGwsqd^(-ZB`<_yLA!gx*I7kZhyY~KUfzh%n%#kg845zqGbQTKX@&+7-xH$;5<`?336$zyw;nwe!VPWJb5fv;Czg8AcYE#s)~ZYtwy+Ye|H{UqM@-gj<WBKdt}pI}rzCF^;uXA*DQZ@30jk$GU-pSV^>$bQkbpK%8#$@`<*9GT}48;bba@22c0?|&%sGw`(dw*8y4M6UR@{n)>JL-u3N{SRfI5Px0jT{lSjr<CmL%+mMa+xLNv%5AVNn|-;TtjPUj?|$&@`%kyaAHIFR>iTA@tnXfOj&P5?f%Z6u9+W%>WZ$c$Kau&f@}lIi?UUWT^CXXLAMX0?spKgy`)xDoQ}*X;=okC`+*P8N__lq%F`>WswsV1d>xbgo&k?u3mwq2R0Ot`sZn@0crA?CYY(I}gc7?Bv%93+UG|x3V*NbmEhq@1>N*>#}$;|m(;%(<9ceS^7pg!CA%dygPC!THRJ7aq%`1bRlvsicde>gu@7$JFlGjKjN>dE=keJoVsZRgnnUr&*9t7G{)$nR*oQQ~dqV*Sm%;@i&A#*wnv2iWf)+==DHx1H;a>R#g8?g8ApFYiWsZ1)WAJ{sO<_InBEj!NR&?lBxICd>QJcJE;<OBMf>L#M#b>p6(8a$NE(?2P*yeXiW+xPJH8Bfq25xW~|Z4oUpqyk#EP?rmH%HcEU<+*in-v`fz2RSwEMl<i)~efuZbC-qo^{&#h~E%z0lJd*s!et@q<-jF<lUY2#g+dIgwC2xf9%xNP2ws>jh(+g;)@yJ)kd(Jt0U-R#e;5)-3CEj)qrk_~_-+tfairp=~?S9Po^{n`(<(^HSIvKwUqq3KblkL9F@q3i`Lu=!H&ph8A^UeKu6n<~!Xx`&he=PTSe!FCT&yjmVz1wxEHzZfiUAeqhOwE*gpUC&It{H2?abIY@vJ&@@diGNI`i#k#2U-)kw=|X~h;O_9G}>*G^)bL3`zhxox&PE6%HaOaevhh`iI97}7`b=Ve|{|Yu4$3*?f0~rry=pSdtI&f1bP42?}5jx6Tk4iaX^vV@QG3T^Xrz^G=<Wdmliy_&{eoH)n5TW|0+DR)qi&t-mdxodlf#$YD18P(S*|PS{QF(x`hyOB=rCb11-Eo9z^{X^-%IK>Y>zQ$-&fPsmBpYhgw)*A<DumB8qhnWV;5DgQy2l4<nDF9!4EZ4xtXF4kbrYN3yO^wny<yauoGS@^W$%brjpJ^d}ZJSXf0U9Yg+zI)*xy98Dcdy@I@)dO7neJ;TCmwl|Wxps!{#PVqwOIu?dls6?(sU5UCpp|lry2({w2)Tb?6vG6gW^jY$E)QZ2MK1*E?uk?NklP$cbsrw{>(w!{4W}%q{Z*pzw+KlriccND1Ch}SF>(s9@S9P*CwKqSnPJW&GRdQWI>1yQHsTH><q$l!O@dWC+{Ja@ajcu<@t&>|&w_sVFJehitg%k@P5K4b$;gW@H3x6h*zCdI%E`?gfU$&6Ta+j#HiCo4gHmN@#FCm-Ms;)c>In0^Eayj&Ki9D83oI!0;FCmm(%A6M%dx7oFBT^WbLA{i`h`O5vKMTFcgQ*q!Q+Fe`A(U=SDBXonx;NRMx{rna%<V@#nCQ<q#r>%Lse2Rsm|JmIYL&A?p>qBCSyyUbatG=TY_~7DHFay|^Ch}4$4(0eENmqoq*lC}T5%%vPI5e<^m;<+PsxeYTNvjeucuzm&t2q%LOPMpiL5(;P<j{jF2*ZPquxUPoSa6zi)9O*)A(HvP#+}krVi6&t(;Ddr0&4+D3}{ccO&~zZ?mx7!Ws)bEWB-@C!zF6Lh1SBdDQb*Za$&(TJm;k#a~b>UPs-NdD|084=0p<pFE#>KFhsNUPs-L<wuZ*QxE6oBM7ApLg_g2I_h<7UmSTabr06@HhBc~2<Cd5FxVgSsMnC=sN<M(4S5^&=N#89<ek)t<Eh`V5N^Rqo<i-Uo=Paaj2uqAjC!?&CKleX(1_fbT5(J2M%4Alt*Gl!Hz1ULiR_?OT$TDIYEN=Q>c-@TY>%q13ZZmOLg{wodeo}i%go)5egL6#Ah`i`1I7lDU#1SEu1_fKLnz&sP`WwUle*wLD1FqzaSKW0RO(bdA0nTkK17{PK0&ScJaszt8A9o=$ycerrannNMy={PXJH@pKGt)@LY9TigwkIUN`FNty^-ZMvFs*#r-+Sg?+NPj<Sgp*)K|$zsE@FnN;kDo!$M_3=~Cp1)TO93a#?D{CA5G4DeXZnPVGTml2E!d`336I)MdyoQmgns70RP@F>(d!V$|ixuTU$VMqQ3Nf>8Pz`7pKOZ>g_Q-y?rdeUJJ+`8M?)3l}Y9l5bIGQs<L@q|T>y6H4D9->1GqeV2TjTJd%2yVN(yKTs>aLH(wM?iP~CJE%XjFvr4TLg~2{CXv;1KwpnyUd8{@zgzwL&rpL?<e#tXC5s+S3zsZ!ZBGAnPz~r?QjNbgsKu~QPEsp~_D>Hy1(5'

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
