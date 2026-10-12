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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_005.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_005.stl', 'source_sha256': '49b264406664fd67ecd53da28066a9efb76c605a3cc1a5a6445c53a2fe512782', 'input_faces': 223, 'input_vertices': 213, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.32958054542541504, -0.14518216252326965, -0.4279639720916748], [0.36573630571365356, -0.13062943518161774, 0.4664824604988098]]}
GEOMETRY_BASE85 = 'c$}q~3s4o;8OIk15ye-08%5U#K@>?u^H3AHCM8tSghYJMYK167MZtnGF+{Ubqlk$jK9UHLYXTH7NsU&66=j3G3PQYq4-n~XGkr{*W|%2;Z0gvav-f{C=bU?-$+XOT^Z(!9_wBc5&z?PZy~afQJ}_AG{EgN6cO?&agM6gXM;okdN=)0hW@Tb}SjvXYKH30_(?6yMURbmsCeBCOq-6xJN=#pw7CciAemd!?;7~m{DK%|lT0+W-)U;KJls})aE<KU(^wkL)63OR@;ZvuD>eE6(^)34U_}80`p>5ce3L=i!LzPtH4+hmmD7Zd8u8DG^eW=B?xO$VXm$^G+kyUSgp|$dT9FZqmc^?1A;;(t``0C#+e7(8tBhNS_?wst`s^aFZ9G9w(;Wwa#=j^<4f5zqhc0KD~en;f~{jC0GQiDsluG_;s{IyD#Fc09y>{FL{u6-9MaMp)$bI6`r>+>C7Pyd!gm%t;hnmpIXZx`y#e+_LBIO-X9N39p?ja&I0D(+}&zbSC^@v3LzLA`N1D<?uR9-B+!aoji}aCTje({m3*D8^%R>AYrcoKSBxoa_)d8$Y<#yY6G5|D9niJl9_@GkI=wT@&gJSCWh8te$bRdBxcX)jD)dJV&|n%|CnY`ye0dc*gY;HJ<(tEiSH5aJk-nrcznYxaOChspRNmuB$q)8V}>z2hRxoWzPD0ajB1^WrVU1<8mLHqmS`f(*=vO=jh_f8&-WlSOq`NjK@!itg`0q^kmO@lm6qGx3N(cch;6!TpyTTr{eLu0-Jcw`pET++x5P2LLYWsJ!Nh+KTbzmq4oSb@4i>9x-Q1$>ykNJS2Ab&n|ZXVTDXrX`^tIl_)A}bJLcRK>)E=JxV^5x+5K{c-4yCg|L;w{UYmWdTD9I7m)8&Db{}xv{df&u@4R@bq=M(OI!vCMTl{N<{sCi}lzivu8iC_^m$|<Fg30%ZpA#zf2|8EKb2iV6JKTx2s(E1CYyKr}&%ey2K3?|)T)r<}oXzvw`9go^V*#ZVJZJL^?#_M0^S)40?^)+Z3$I6TTz)QOt|uRE<hlI(%KU!y?7Zfvv^wQ|mpQw?jLY{OT)yu{|Mq(8x!cp>c^;eewg`^1@i6ZG_8;~9{Ae>v+Ii0E88@_y2BFV)S3LZ-;o<mRVBDRY+o+spiL-soi?jKZxHh&-=<ju3Brf;&x?d7!{q?oet$kG9C-sHT3Y_h4dao3Lv;ENM*m_xYT{1VXKisC|!_T+#Tpqv7<vun?AM>9*UBYu6-N&;JgU2UTngV}!o>1@DcB6#nj+=u-{@`JCe{i|KaW~iE^8UlPd|sK$^<LxY`a~QL``(v0+kcF|7kI|g?I-sCwp8G(kIe1&hd&$_`aA#HS<Z9k-vR_~Y`W!Atv8vQw<md?_mnPi`~{!Z@SOE$+#C|rthz2o-$~7?>yo*>Kl@K<R^2bgz4rfm;R3h&OWgimE?d^Dx-OZsd1G9@UYWCc$EdT-!t-0=TWHm17qlqnd2gZT-!VN8i1(#_M5}V$f_tsczF8J$`?I}%ByO)maCzQjZm+kt;#PkA_v6OeDf!m%*GmNMUXoW(q2R{LojI0XEfqMMAG7ny6@L7B@H<5+uBBwX&vW~^zILKW#qIiUIxTMhK5(z!r3j9*@i1<D*(KDwD@&@C{OIqM^?E{Hql!D1&S+BBkM0(@*ZPsTc5zvOk_S!QujB(;cd5AXeV$WwUSs<4V=6AsgUz#UT~hM-#f>U1&x1Yxm<MfZ|Et1tf%g+H&Yn|=v+o6)?{EwIxy;#f!MOZ><;A7*%HLBmm(T09k4>K?jK|(5!L`gzaX(~Set(uZ+c%zcT~)3hnPdH!-FKApEOYyN8C;$pnX`JwjMdjv>r>{|`iv2Nwd~CC%kS>3X*7CigSDgt?kCIc-kvh1>YpsvO#g8|S%&}LKUw~ojN!K=K8Jn*|2g~#=s9?*<?tuqzeG@f5_%r~B>XAp1^56GbP9SxAB6WI;ftxH+5_H?L|+mQAgJ$!pxz(a2mT=v{Yeaf?}yLRNK7a3H1rwxAtdN690`3Geh|I&$PYx0`f=8+*0c%G@$e&Y>^SIH_z@(Akr)jPgda{~DDp#*qh2R52Kh0_4aYHo$Oj^)W1Mtcqo5<<CqTzRM{?sC&GppbSCL30@iXWO_#_gqBL6CK)c=CSGSn?YE%h@=JVD}d1ocmmm;rqf`UL!15<e%Af}nmmj$Mv^%fV-240KGZp=;n*!~YVx9{x?}>(KS^uaQ_s;tl8q_zn1+im}l#B|}r;Q&E$Q{<Pm_^rSsDK{vy1Mh*3oNlYXW4t*5<F%nZqgg}Gg!%;I88U`PRW0;?U&nrp9lXw9d4gU&>1mqKtqkaL2`N+>l?iCypjeIn6)W?u`k;ELR13r$#QskE+NBuk!bCI8mTpW&ZAn!nq`b8vOCh-&Kv+#>aEJS`Ga?~#&5sQ2*a@7BnL=^H-$SpxH+A|XR9Q<=QhWRLb{)of}B=$k~!XF{=A@Uz0NBtfWS;%K0cLc}mMSd@G)Egw;Ch-<D1AYgIZOCs!j{2=6wjjR+xg9tr1NjW(sNY3mJBe)QLHPY74w1-&z6+m?njGk1_#F8C&_nQ<ICeMs)AQ|w?uOrunw{J+IjG4-J{xQ|G!x$7=Ho3~(+<ovyAS&?m(<fW&DJ~B1@Lq&vUN&z9z0z`Y<*FUgkPflu#OgkQ(r>DN#Z#46Zp?ad`hAedJO&>5+(^3v>LvdL=B0{(68Z-;rQP{8{kWDo>K07)L$e~hq2UQJk;0YxJ%Fmc)DNEJ&5f&AsnMR2^s=V-*u`m_9~3u#C5qaW_CT7aUJw}DlxW7jH?d57Fq*O_rOOq&)!Bg6#h~8DCqO>QSh<Qm*8XJw?p57-wuBedI0_)d_MFjd_MdoXgz!(i2@S2&|kq*ErNd^ng=a{&x0=}@f+xAXc2rPv<X4|8E6rF5zco8LH$?I0{9kaD}wqmXaRfyuBQxo7M{Kn(RZWS&>(oK5%3$K>Cg!HboeyrEclN}yoWi6iT3F+*!O<_&HuxnL0<-i|MZuS6koOZBhQc``^7sZ+K;|pl9$OI)|daE=v$NaUo>kJO8'

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
