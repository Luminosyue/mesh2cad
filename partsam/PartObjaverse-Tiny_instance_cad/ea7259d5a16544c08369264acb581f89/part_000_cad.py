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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_000.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_000.stl', 'source_sha256': '7f5b6271a6c6ffad38362c86e2c78df6f5c05339e5144106c36e10eeba5f73bc', 'input_faces': 147, 'input_vertices': 96, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2520557641983032, -0.3735971748828888, -0.24132277071475983], [0.23760072886943817, 0.46661704778671265, 0.26824575662612915]]}
GEOMETRY_BASE85 = 'c$}qJ4OEup8Gb>~iDWoG2#N4Rg--}X6cNmycbbSI2^v2N!iNEk9gY~7XGzAZE&mo)qP86BtDyK(h!|)t_07^;A+cu4a!$0|TCL@_YPK_L?{nSP*KlV$XJ`A)xzBao*K<Gjb3Z@t^S+Rg*2l-8$uC^HKc%(S=&xzY{56NRtfX>j*+V5&qZTiD%u5S^u6`b@dmt-4W4@QROsjSkmsCAe>6+klO)O1v#W-E16_raXixwAFR2G*gJ*B9;s>If-zF)MY#P&xfC&oC(M#VT+IRDq5pDLv}yz8Wm*2v7mQ&dd}8w`ccOTT<a>Bf$aE-KWTV}7i3t1jn^^4;#HcI6x9jP;0L5)Iv%De>;dj-uTx_lIt77Tv0fYJtD6=?&z~d(HxG3Pv7%kpbPh_8xR&O9*u1^GUBE@A*dL?YVaHkV5xV7j$#7)MEv2-=lo}Rw(-SY<UJ~y<Oje`Q7LTUvCrL7+2DWIIp<l$p6WC(cc`|jCm~|09|ioJzXU`QSSxsS1@0n-(z0pY2VYR|HJi1(Y}J~u<sJ;>!~kpgI?cp33Y_I*J6FDcfO3cFE3t%?z0HG9xu8c_=8_TUnjab!w<T4c(2TNf3Su4xR%41=ak*h_3TekpY`r<TT$QDXHmaX|Li!{ZFL=V-AmTrTGV_5^BYib2>zEcUu)O(W60-pK-Z6m-czto>Z@_Th`jHYp-!V?A?mai6+(B9efNFn@iJen@x6VhfAQDd$gBT(GxW|(*@u=@(2XNEpF;biuQs4AGx7-H_U3kB{|7!|VqRq-vOa$wvIh0sEQPL5ixT}Ea~JY$Z>`6C4(*ZiQ#$7y>R6NUJjT5m^)mMRZnG2pZk^nM{B7LF@du$BkI#ax=WIirn*LT4>f4wq`gGYBXVn;-2km-1bS+NSU&~naI`Rw`-TjT6x1RZV(6w@3$&<KW*5OLhR^$twzZr4<avrR}jwbBmgSpV%2j%?eaXGE%H&b*igXisx?|$Sxm;>D$+%4yAps^Qm2ShgtWWTiglCdt<JkhN?E?-9etFphwAF`#MTe9z3-z3DFS46i;nCGC>Y5YiZa}3Y(r!^SYyp|>7>QZOV3n6k3-6MKW72}7=ytJI^O~}7m&Y^a0j^NLhi5@BItdCeGdPR}wwQ@gbS0YbA54%x^xGLFSeN@BS(65YvZeFOBal^c&{sb3v>#v5a|In}N<arJheZi_%us%1Ue}R5~tX+raV*4q~$NJ4E<Tw5jv=Z^7eI@_QH28Ykc?0AAe4yk%v0^9M6B3~t6N8Z7x&MPsj2r#y3goHbIm~iA2|Qc&F!KELDVcBfurAr>u%%dEmyBz4U*7_~dSf+wZ$3xP?p)+Q8($;ORg9cxpVvE3M|i~3$~V{Wxppj&^RPV<dQT+xt0rHb_dVUup#AxkqUSuj2J7V8_yXcP<@}pJv~bT@E6?J*yEk5t`)5I?+;=l~?ZCJ>a$o5moxwe(S3GJ03we+2yNG*CJKZ18y;dvFyOHgUd(zl&Qgo-B2R%0A7~<U@H(=Z^c%D!3oTq#O-R$J^<uCWJ7G1R)xK+-rwU_ffcKiVR19Gm6*5AE>JlkG+5%V2E{nfAVUeKxv<y^PRI#{_|UcxvZJPF;}%6qu(Z}Q%GuDA{DYvr7~y=URQW*pc6U278Eded(=;(Z!%ZyKBAUNRF(@!r(yyP&(j;`-c`*@XB%%{zg(wX*)&t-Y%epVR=o=Q{7Putw<4%k5ZKZ5Qv!JRSMm<>#TB7pXsN;=S*_;`JKl)hzXBpD#xqBkhT|knbn_-gtUF?tgP`3v{bNo+GXNn^nla+}#2EELQS-_{28EpF0ZO{FwRMH$IMW50~No?zuS_&ylv{#JVXNw|%{R(LTPWxSyse>u-O(l@|5-bW@`GdGOzVx|JpTSD$Y23FH6IZ#VVnrrm8@h;0*W8*ke%;yvWawhguId&G(4$;4sA3BCA4`V*PU!-vuz%KRRlOh1`96j$qezipF<I(fcr1-30D7Lw-^ClROg;)V1Jnajfq=oc`*hv(DJXAZ>^ZM#n$Sz;u4s5)=9B@ri+hZ4hxiM{w_`jeT<!=3b<%<ti$^h23L@pRj!+7?B;m;6rKhS)ZmIEp-qF?SM&^ok8;oI)45iiu@=EZaQ!TpUy3H1g4GOD9exk7wK<Vla6c`^FPp<Z&D?jW~^b5c|dvW67s7=3Zhfd4O%vwv8mtCJ!JEBF6XPv+2*~m>wQYKbm8DcmVwX=7{UH2Qgfebn<kz#jt%ed8TdiZA&4}A<wogkL`JEQ+ysVm6$@F!#?wfp4cqnEMhA80`|!wdSdUgZJ?(9^c3_VA7k4%wvS_*;(<gzqCfdq_6a0<Vh0nyL-Zq0V4uN6PptYYcYtjUVi38nZGG9^mu;TdK8#a%2f2#zV!IdH6z|7=-z7T8y*WldVt?}Kwmo251~HdBLQ~hjw1=}z@tL;Gu<b$OT=L<zjbQr-ws~TwGj2L_&t*&m+auUEgL|3E^-Ja2C2$T7j^kke;aqD!&d-l?^KgIq{#-9#j;(6QA!d`Su~Il*3io&{=cf8BAm)&(m^qA7IF3AsdlW$oCs#H2unr&YSzpd2i1P_z><HGD%lZ`Nk!PfNc{}?2r+=^f^Jl05Zu@7;zxKTS)!w`33ETblMW2!8tLn5D)mwYS#)ax;(Eb6?Ns)R'

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
