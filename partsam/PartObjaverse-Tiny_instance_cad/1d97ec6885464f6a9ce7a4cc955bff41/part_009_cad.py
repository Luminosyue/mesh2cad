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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_009.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_009.stl', 'source_sha256': 'c98b665b25a393f2f4e1c080cd95cb72f5349168e8e6b8180e56d7dd2c0fb28c', 'input_faces': 135, 'input_vertices': 149, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5922054052352905, 3.583683967590332, -0.6255683302879333], [1.295830488204956, 4.75767183303833, 0.27157264947891235]]}
GEOMETRY_BASE85 = 'c$}q}2UHeU7RLv$3)rwljkB>J5gXuIqB2ngVnr9b;)e=~QBXt?jWQYwmIZs(68wzO*rUV}7t5%zq9VH(3yK3`$r?4ro;_;bz5nYj*|U4jo?Sfm-2eRM&VBdYdGlsI!@9ba@Y3-2J8f*=!t}|WnnvcXd1;fP;uB(qM@?uNJ1)sZtH_-G-uk6I`g9K);G#{^rh1QvnlL=xyRGisF1oe1ukIZk7oQLx89OvCenb@U;K(r(q7<JnDso(uI&Rb=ppCEY@8hda)Bnf6a;gNY|Kq~LRLi``3Wjn<d}L0b@@CH8m^&vN^CWI(4`%N8IFGsMm&fsDuSsW#Yo58x9S!e$aJ);C3&gEzyO6(4Kt+zfr61+^`%dIZ4&iw1YU)Yi&MJw>lUnG`^$d7+nDhKO9`O+&oX1M6vYzW)7sA}?a+BljUuJINJfWSK+XoPDckcTo*AZA3`Omq7dmO~|aW&Z+K~<SM6MOIH`5&qZerGy!E&R1j$9lRa@-%qKT;F;8D#w@eK%K2JDly+RbPwmRSRQ>yh+(cR+kb)c2A4&i6=l%}zx&&m_qbia*A>j-KI_p5$NBn4`OM9WD-geX(Gi~K{A}j-vK@TCjB>drIgi^(=0<Ww=8i7cnQJW~^Ev;_@|f2T`%qurK<17GEzk$89_BMUoVmTUAL47IqK;-gn44>+A-?HL?vEDt5#k4J1m8RV2FL9PVy@T9MjnrP*SU`SfvD%|bF7o7Ozx-Ev1T6UX$0=f-^1Ko`ST^7SK>3~M)*$V+JmfIK7afv?(exR$P=_7htGR~8^Ie8@Biv7&v)1p<Uh0)`3HM(pLF*Te80@(RK8!@@UtiQKF22^{<FJ0U!&kCbItDy<WGsge24C5Zag}J`QC8h`5O6OGq-j=#(Z0?LOr$mX7ckfy%pjgOh*65$1%6&3}NmlS%m)QPDK3JiJ0%A%c$pc3UedvQ{<`BljF7g9nAHu55eD`!s8kjj)0$gh4mabG7sx5;Q&8pKMmzR*vH0lAFNw*nOl`((Vx75Iq378gS=1Ntd2Yx=drG$6Ay7cD+i;_;0Qcdd(xPj)n}j&Be9OnlAD-Y%Qv9Txdzs;mCsza-{EnM!eyv4W()5V=FOSR9kGR6k25aR;&FpJ;Jz&0iG3}v3v)fMbQR*3PyLHLZd4+3?Z{H(X&-u%d6$LEoxbatJ1_TU?i^Xb-2N-#^?m`&9o?QWHv<uG{M>=Lq30ao{Khi$^SeFF?L)V~CnMf!XJK6T8oXZ`afsLMu15S;U+}LGuQ@hi+~C2??a)#@FY{s}UJp*UNap&(is=90@*J;q8_wLZ?M`Kme^2h$1?w2+UxjsOHoS+v{e9MPtcS(ukLxcOckT-2cBdt%fB6;k=kZGB*64MZ?^h*?xc=m=%=JUU+ZG}I%X<7Cut%Xzb8}hrt!nR6oTn!0u^Rk<I<xAZ;rbV(p%0$lbG$XT0dw6)c!lT4^Q0|v?e<#K*}VXL*!2P8XMx*2T)9rObk%H*FS`);z3NHivB2%M3$Xqx-9`NoZ7wmt<bib?_lE1#5B6iOt;c)N+2;o8_w9C>=N0!k@=v>j`<nvpECudJdVz5xl5Fn3e+qc^KCF|4!q3dbe6ubizE!6JtXn_q8?!HBKS>zJTnoYeZwEXDFWSf4kv<=N7<&}`tnw{*J8&!ZCV1>Y=Eloa;M>okpXtIs6TagC>Z!A?kmqZa!}IvAe1CMm#@sm!`OP(0|5oh+=DHiW_Rt1D4Q?z)e$&bVUwIq(TY}q_e?)(Ro-?-}zu|T6SXF_a3)A~G;zM1q4`e;$_lNa-*-eh$kdFIRSReam_G;$FPgU?-uO5Q^=k+P(`X;Og?Zp)IVa$2v=GUuH=j++1=gwus`^BOUM>DZ+Z@h;19<r{kEXKUb*vz$Ycd@T7H1MACDny-qkl((s27Mk0?pT8NqxMA;uG8x90{M4fJzJ?YP*3VB#1C16dG)V{JYCBdas0Wd*x#OS=6%(uTaCG6DDoH?4Kd%iTFiA%<guo<!2YnO5#o<)*q6S!$9>ildNVgt`y>B7KfGW55{_|qM&r3~(=l$De$2H2xQ|*34;$;DKk^)~!KY{7yDsyWA9-Bg(b!Kix8nPx_ABPjdrQ#&oQM4VVSMt2xxFP*_L-Dx9Dm*AKIa)-g!PcDbN_9hjo|U&xbMv><2xbU?=jbtbBDj*9QgzAeEA1}KdOmwpM8gQb-E>U`(+^Vdo*Y6h-k&!;Tnzl>#xRsp4ytZbtDzf_4@N%zw=NV=Gu&Xc&?vEbN$W-ZJC>f4IcL93eVSd$P?~E%1r(~w6;&mVm>{Rxs|aS-}6_hpW-}4!<p+rJ@Nft>oUHRqDL_|Tl#Ul<4M9Xj_);wxzYIo`f%T!xv5V?o~T>=-L9WKznAkoNMf!9VgEF8v-$hkSU(T>hi&C}#~HUdoVP|AbBECg{aIHjjrqBB<QY_e-v!g+`Fq8=YCU*hdHEeNp1)VjN1MUh-Qqg6{o#1u#cV_V&l}@=J1F7==h?Lb{n<AH&*PirSXX^^qMzGOBTu&z9Pj9uf%vESsI$~l^xyp(j9cbU*w5YTWZ-$<&D;*^iFK8mlg)km9^6ddhWirllg0CGzYp=vLU>%eX$*7g+f39yFp2N4R_fIGz_8!^YMmK7$1S&%8bMiE^{X{Hve-{nf;_zVfB%y;Cg8vO$?D(o|NY78u4<^Nteki{t}aHphHyHrrp!aw+jDeWQ;hUGVx(&+tEa4yviHQ(aedL`8;B<VzOs?Z5|l-Wr{hUtq!WeH@kC`)lr2z}B%Y3^iYEVwX!3tlHcfo-<LRQwCyOSZrp%LXsruXzPshGuq{oSoo-9Usu^8z^a(%60eWBypVx;Sck$zW<bX_shx>yD2SA$}8l~h(nSt;>!Tv3d4WiirjqRD%Sk#-SHzKR&>N@Aon(e&pkntXXN(j`QbFDpj6w6fXC<|&&io{krak^WRP`6XhcXNV@hOpLTCn*35R(lbSqPZc9QOEmfUVx;GYCZD40_sZHTYbTm~Yw^T8iYDJlS$kz4C~GB}d>ds!!rO}`-&wAqYd;cAK2%v(iR&zyd>1)KG2KOz@21R9)<T(|X!0GzH&)g}G<ko?N%_J=lkX))y1!`h1B&JH7frsUvcAfCEBk|J^8J(zlH<3U{9wsNIfsZQAE9ix#0?frK3dLE%m~rsM@bBwA1j*tXl1c-euQZ9A1fQCEK=D7(d6TmjaL>UY`pj}a&D+HhiLL~a&DNgw{gVjUC>lnfN1g`3TvpWndoM6E?D9|6iq%vV!f3$7u{U0=^=3;qRID^SRW1d-dlWg$w%X~6HUI8Fv{0j^xL&edoS&~jYT(>ygs7+MEl7YeWZ?_qREFV8z{%5!@9b-db$0l|Hl32pUE3a@&DBQ*DHVfDlLBHUX|+~FV?WGCHZygs{YZ<JWg*c?N?eU9Fq'

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
