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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_012.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_012.stl', 'source_sha256': '1226ea1217956823c35a36ae3fcb2fc6f631a86038a417d7372e168cd5e20cfb', 'input_faces': 116, 'input_vertices': 84, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03678681701421738, -0.29357320070266724, -0.09793612360954285], [0.49999991059303284, 0.20530791580677032, 0.08334442973136902]]}
GEOMETRY_BASE85 = 'c$}q|YfM{Z9L8S?Y`AfAupzs!!?j!r<5Hl70^K?{27|RsG5Wz3p@c=VL1BxRm{lcNrrDP*OcO6TG5cVq$^0_o60<fLQ!&9zjdAft!??`E4`%U$(JH=|=k3mUTN9%v`R94~z0dnU@A=b|gSR&|EuV<1n3SJ-w%?yY2&+tzPfiAcQ%8pblXb_&pGhIPoU=>n`TmFdypN`kljJ$;NMLd}Xl>K1u2F~8rddai2d9EV$BrBijszIrH}uqGfbz+)q45Cyxzb^`X-!o&?Ro9LUK{8UA|HPJc9?2(=EhtXRlTM9&NTzqE(q?<8N9+YdUsxD-0wN_DbHW5<ax<;a6j_yyCa-O_VkGSLn1FZ@${JT`gfP#;OFVe`GoJEt>AgdHMih0@Bj9P*BN(r-Tav6r$k=z5O_TQ*jJqUPw)Rs+)q5O<T|)~UbpY_S9#twbA$a%mdeEW!FBME?C-lO^3$1oZvNgX(H~rw9C_l6UEuR+ALM<a=S6?XiEGf*Kh(F%dGw`uF}FX&JSEqr=S}nU?_E5{^LGko`TZ=V;ymEmPlCt$&wj%>dEp$Nv-YG_^apo?%l_K+bk6<t1A-TdyyUv%a-LH^zruenwFUh5qMa!h^8}B8%kxAgx?kq!x7`x+cZ$5^TJ0^<d?H8kU*zYhev>~}<Q?(6lI!3yuj}uM&&}%Gmwf%b)823r9)0a;pD|BXKN9?R&saDK*C$+K#(ZSuqR3~J1j9)<IZzZd=0hvfoNIYcoCqi3r2p{~rt_~1bM9C2l1KW?d9vaW`E2ufBoB3)&l6d$5&4+;c_r7z&CjbZ7m0JeZ=R>*p&2nx^4q2Flg(e{a{iL5^H;f?zvSxtRW9c*xjKK9%lXI8smx#Ha{lpiD)U#loPYeB%KTL>=P$WBf0fJm>#<8e@;<lSU-15qY`Pjw#(kq77`b*kc9Zu}@^OxQBsR;rf9aH|e*#zX`r<WH{{)V__UEtSzKdr~`2>!9^sg%m{JEAco6eKKkq@mcFC;sE0$1|t`4hOD=i1sr()p`g$tTQT<t*<ty`5a|bZ-A8oe);{(YKS)A;YT)gY1%;{MF>B{a?MBG&HpQ&v%mzJLwrV(_+WpL2Em$`=Pn;o1yv8T=*j7c0zZ+Z>6=3uvasoS@4Cl9w2NeLNnmApqbDN_^rrogBHSXp;bU@9dtc>9<5EZ(xGYa>!ItQY4BT+D}d&~XVc1|Wr3!`Z=}WE<x-#oJ{4+#68LQ7a-bXG8)?<kDuHV79kkeIs}{NoUW1lEcfmIzR}bxgXVrjxOpD=JrW5;_*1;D;HE11tJ#r1uE_hZ=*vGUKo@HFv&(sEA3N41(;2V%@f_B1JBhv<T!Lzky^kZ5MUkYChwZXS3{hQ${vF<SB99VBf52jZ5a`;MUHM|3Ro1v}n6<BXE<XW)qL=UD_@K*Q=XeE3L_O?Qu@MT!H8*+B6x1$Hs8u%*sGH3<79ebV7cK8ykHyUz{Snog&rnT@j#QgazBlkX^cI>lb5A%CzxoHhR`{57MIz;P1=x+D{WDY|Q!Lz-4XnCOn@II{XhI-(=$oLHR^I`8kS_h$C_&%(Ap!?wuBGYHMAM-s*pKe2+1GIWszBk2^pZZV#%HF#|{ENi+kFC1X{Ab3v^DWvd{zu2#o6f%L=ogZOOi-O;-%8|fJR?r<'

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
