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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d4f7c4b5f9bd4284899477cb1f5bb48f/part_003.stl', 'relative_path': 'd4f7c4b5f9bd4284899477cb1f5bb48f/part_003.stl', 'source_sha256': '669def86002448cae715782c1354ea61a1f02977f6534a85a3c45e9c87d25066', 'input_faces': 256, 'input_vertices': 276, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09450698643922806, -0.3381099998950958, -0.4696022868156433], [0.09025761485099792, 0.3889424800872803, 0.48559436202049255]]}
GEOMETRY_BASE85 = 'c$}r033L=y7KUFSLBOyms4OzH3q;1aKu~t5QHF5<LqtG8ln#&(#w?hy7$ReVI*PIh0Rlp7_LzhihzJ2gN)Qkc!2}315-4yT6cq&(mBF|CudKRVo-=2r&$;LS^7rl6w_e}sSN$pp1L{ULXX<eSYqYHOnP4l%L`1XZY)Vq*qzPk_vTjeGm>t2IN?$y*E{q>~f5M0eHihNHj7!QIn;FwR5YsccYfNk)COIQ>Qf6ZM=#0#9Ny6`!n3|Qu{j8M4iAntLTRL^QJ2nv4AvQ2Q@IO8p@)82eJ8rGyYL9+&XCJQS_l-_ex_m3BeCx?Gm2TfoJ+#|5KTY{;x;H;C?Z$n6`7B5IG~awu`N5x>o$TWtXME2ZS&trP=8BC%jWMdu;Dz0_LhTu|JU;tz@(H1#8QI=^jIVuqTuy$5@@c-6_VF=yJx1;|C9<yd8xPCZ&o8NR`{t(Q(znN6TkYo?75zN<_L4EuH!r4F`}tPPS0A{2qfSHRUr|`?=LcJsdGZ5ytde==FFUIJ{Lsz$o_v<lt=eyV?bGp%J*TSt>eoK4-`cXS%5Q$OPv<AF>!m99Jcsr_vq3&Tc&nO+?d^}tyt$K=za~-5XK4@V8<Pe}KXAUu5t-j6PWmjbtMu)-Rx+OjGNf<r{<v7?#XT(Z&C{c$Zx!v3e(<?3WZf*aT#a+-LFt>T=gNHJv9+q6k8YEGsN)HBoShoi%D)$FFOtvatybgrx~TGN=SV-;>09-A{WwPE2XDVg`SFWX{XfJ@-zbZezP+fuI^G!t(zor>LgkNF`S&iBz8Sep`k^C_t3DijSo&;Ws`Sl{ZB_kc?@2$fVVv}XQ}?O)DLAF-KU=w0>Qh}`mFH34CLg$cd)~{+?>^Auv-!$5;;RmM#yP#AP@Z>%PkHh!_|};fo_ynSLa`kG{7O%L5WW%0@#dFyEs^64EAix;@PoZGy!G7KwA62W3qBp6eO+7XSAPILt>11jexu*~XrIncU}fG$_dFY$KU*Pn#{&8JTP>1zy8U2<^4Zjg0=LhmRj=~PH?oy)KK)&>+cz(?%k|4==ap~NG~ML!C-g}2%eNnae{Xu3+qdp6nbXH7-|VJ*gB|hYvqrHYzx)t<ljIu@d{H2L){@kt{l4CMLj8}F`sK3$$~VdJ8ZX?n*)QMH{<Gfs48|@h_pJxM`GoqsLf7Zamj2v0`Tb;`9ktEvTkzSTtSxRor2Wqe%G|!`_&FtR-_YY<yu8LU&K&sf9$ehV<p*Y}zA`Q(?evT@1O0ZHdFl_P=CAh~pJ|_rZw+~LonM{iZRpSI&KJA=;Dybr{EnAR*}GKMMdzn1M)hsXRhvBZkLvWSe19^}#*J~ZZ_NW~p7D+6N>$&!dDuJ8lW&!M$SS;kaNil(Zx$KH+={*;^@PUgzVaTgeI@#Y%zrQ%K2!Z;rDo6e>qG6+ezPwfe!7oOziFTLoAznHX`l9+_G!O4<B)#SKJ7PW9MW&jIHcdSPy5X|F4AvK{iNTtPy5XopY)qk59v3je$sD_Px{UANxwODl74gQB>m>(lYVpRB>m>}1L-$se9~`r*Q2UVvL0!lt~=VN>x+|5))DQ~^}@*~>w;4c`To~F{hoL7$@jVT!@jrIE?nw&yxI?2f8mF%zj_?H{=yGifAu(Y{nb8Qf8mF%zwpD>U;Vyx{ng{s^%s8F`m2wNuD`k-y8h~M==!VQm#)8he7gSX<D%=Y{#<_NbEMyg*7Mu*W&Ygvwn#s*ak<;K;InC4Uvc~P@DxivPx9Fa<+B`>A2`@(mEZW<r{jmryw!4k==C=Iu<LF3Vb|Mw9D2PCKkRxNe%SRk{IKh7olmc~;fGys>w4(*wyuX>Z|mct*W2*JuDA94(CcmD)A<Rz-acBZ>YsPZR`=(neH*^>c@-tEm34Hev}7MN9QTgfxBCyMkmq~kp7*65pRW9coy*<hYv0IKzB7LNx24Z!w%e)B>u==v?A(6ohbG1N`sTK4WIg7t-Uo%+bq}nQ$9phqkIdiOV86^it$btIv2E^pv>$@+^nbm?_44m7op;H<znLh1rw2Y+A$?=jmv4Id9DWGC9w#_+hx7xNPwtiTn`_E?%umls-z@4}={~=-Z^75+m-gxTsQs|>(dZ?=kLd4Q>qKAa)8ECRK_jJaj1Rpn^B*df#~WOdDSi6;+RB<G{jlHT>yN<q{(d*!`dQUOe(&2E$?|-r`vcaj+0v)`32aI|c|Ozq2Wwue^yz*@sP_`}y+HOi%;6R4dx7kS1ZFoVlJ%4QlVD0f`gFg=4#Z2J?$6kjLzPeVb6Ct*Y8<l9rhU54Mt!}Hq<y;2Mt!|crG2{3Mt!{x=F~~{*{HAg*|bmh*{Dy)r~7Qwr}fi)HtN&)q5Euh<XH9nOZHK<Pxn!seC(s@{aEVLap?Z4_F0DV1A2crYO1FmJ-!k3qPI@$4~MS(>~;A%>{kar>|Rsp<D17OA9ed|O7uH^`P!%XLF{|eeC_Le)}oKRE(uK7sP?z5k%!#A0pCblxnG?(ue~8(pZ%qLU*q`L8b9Bvx&Nr!*Y8X7wXgF-ZOYzo&x6jVzRow>wwBi=^ge?2>3swzpY)0L>HAWjzAwG+;N+A04%(;lKz%wsy-%TidY{4>XMAjp>WjjPN*~`$-d66Zlib(%Ex)IyADs7vulvEtPf@-+FA_X=r}os(D>kEfDvt)NIZIA--I@}ncxd&%H8r90e|Kx@uK)Yi)F58N-*`L#eGEL0$6OvSLFa>C0xyIv051eDg64u3ftNrRgO`ApLi4~&!7oFXfnNr%fG!8G0KWpw2fqSd2@Qe8u{?v?g+2?O4_*NM2Y3NE7y2AH7rYqyJa{oU4>}8+2VMq!0lW;n9Qq=7IXE9W8=MagLFa&b^N@WC{S(*#-vhlDd=I!U^v~eF;C|4*fct^(gZ>qKAGkks0JuMRAoPClKyW;C5I7#30DS;_8;@8Xw;}|0fc_EO0UQIp1snrz2W<~-2fhh<Gx#R(4bU6GH-Oth1K_scKk&GQM>8JRL9YT|2W|;%0&WRz4Q&i=4Q>N%3T^|w9(pzSdT=Xfb8stg3xwcndECV#jz<@0M{pN#H|QPUZr~o!+rd4+y`Xo3dx3jGJAr$GyF)vJyMwzT1mDf$Jst;n9DsfRJ^(%htp*<gS3!?}tH6h$HQ>YGqtJhXkAjauKLj5G{|h1bIFFBce9GfA^mFiOunj!}w!tT$UxH77YoT9&Yr!X>{|27~pMrh{J_Y^=A@~y>ukqN(V*|7dya8MU-3%@QzY5&~eid8*eFIzoE`+`gE(8}tH-U@6B?!T#JS-mDc~l|<??4FN#^Y@sZ}E5^x)(fw$9Nto&}6XCB(TtN;1uw1=vc7OF<_xVu+T@q!@(nXWbv5FBNI9eEc8jR(COez@J#66!9t$`3pK$)XMksdpXQOqBb!GmGza`RkBK}ULI@rP%>WMr4~3?Khk}Rjco3QfO$QIgbE(iYa3YV<cz!gV8;lwrMqNTDyI4Fo5;_b#40Vh|2p)woAH}#2f`>pyfkz>K2;O5dj$7y?@I-J1bP6~FoDO{goDNQdW`p15@eYqQ(A{96JHbNV1Pk2?7P=0+2E2;LejaOi>_Z6NgAlw6A-Dn|xE#6~Tn=8(qhSQU5RDMGYE%fm2#sWlMF{?h$Ccb?Jffk(i-tymqw(4(9#?R#&!Y}P@b^q<U8Y!s;0rwJaX*4b6jXRo(7NC#ytWRHt2j61@iS9;jwu!)_!k~mM<{IuJqK=v{BLnwjd=WrsSx}l^c$vFgy0{bUxS5y1s3yp3G;Uep5PylBUseaghyjBPdv_xV}pJN7J3#ev>{k%1F+EgU=f1#qrUohnD{ACPaGej9zLgYn6E}mh2Sfo4ZsNlBI-1+`+NUd_uIo1Z{+z$JNioR&mQ+H^Z8iLkD!DBQKCNn!Pb!{=m>F@#(o9SJA>u'

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
