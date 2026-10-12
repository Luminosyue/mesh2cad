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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ff841231d7d4c54ac917e63c678c9fc/part_005.stl', 'relative_path': '4ff841231d7d4c54ac917e63c678c9fc/part_005.stl', 'source_sha256': 'bc11050c431583f0ef600af342ed000ffabd8c924f16a7b312038e9549d75978', 'input_faces': 116, 'input_vertices': 93, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21098758280277252, -0.41352924704551697, -0.14756570756435394], [0.005155190825462341, 0.22874850034713745, 0.22250205278396606]]}
GEOMETRY_BASE85 = 'c$}q|4^&p=9mg*sf+&OniW+fA<i&io5G4KyS5RT1jSN$#){BY*GeS^HP`uf!mRYL^%~D_g&S51A!s}lys3?IuuCs+%>%2$Zu&ufNZP{wM_xb+5Zm&DrIi2mE^E=<q^S#e~?sI?7?>_H+^YeUrhiP&|YuTHFW+eC3G!^}|Fl|Lq`LdD)MHOR8%U1emA@J34Q(w7n#<cv|KH3Vc%C@kmVnMkrRkx)tO19Z`+oH$Hmz5WmKKxku!Xo8QE?iPk<nb$t3(JZ;?YNW#yPh!8uCLbr*CWs~1$~!KXN#Ik+XKH=>VEQfr!rMLacYNZJ5H@U5C6+Z`0hVxXVL%q=yR%VJ#y$M+SC7VMyYAGwB!24CH1OpExRQC%R4)jZ<L*Kp?^WT_-lM+ymOsx7|$9G->A*HsMJ~W`B{v&^V4?p>$ubnwXVW9z9|+zXBFme?WlsUujxLG@!OLzPfgFX&~JYid@ZpJ^E58^KZNT(YL)(_2Qg3W<*MUoe>YkDU)CZIj#=?%)OmAu_eqTNl@0TE%qu*N{G1PlZ>DD9zUJAUR-FH{zxX|;<i6{tAP>5qulVW5abL$Xg_x(=_~SO{$$7}H5nFT;^V(!#JS(gO`OzZQ<2viBI{3zh-WPEG^aA*1_4Dve<ASt52&qSYf|rQDr51V9Uu=5^^BT86{Iu(`j(z4dq5rHo@U{B1jaZlP&8;~9b&~jxKHY-$1^aP~^HP}jZ-l)G|Al!Lblq?9d`9yxB%e(&9q|1^;akoL$fr5D5Atl}?rK4Mdk*qxbax^z#=2VZcedfV^ljOamkl-Wwb#$c{JR2=z<)gB1p1GumU?~eGV0mte&v|d?=yHV>$x!G+1S%8{kr<f{P%u>=XL+_=kU$qE0Xv2*hcsbmD2y)@8rJeu}7d+OT~}=De~j)o{BseJuX@Q5eJY5=Svrn2h*nkzIDQhbur$1P3mIUTQ2WBxJxff9%A;nyz}4~J6Gx;V>f)`PzdV5IGNX_&O1w9cX{W>`glC@V^nQ~@5p`}b!C2DiT+l>BIzHVhjlTQZ^gPe-d@}+^{^h#r+-q3`Zp%THNk)Wpw!8}Bgm)q$ln{`Z~A&4`Z?<GzB}VaG<w&MKF}t0HQU{Qc`Uyw`^K~5QHR?6kKk($YEmDKp~o<OK>Y#quRS4kUc3YK<Q%mZzIJV*)X%|Kd9T*i9PoZ0t?2h8U)g`bzGb{U3D4`i7>fI7f9tIGeqMKL2%guWMT&o7AJ$PXPQp6snXdit|N1WS;Qp)(d2oMl<1O^N|23?ydE=72cc~q3qW}Dlksm$d3FODU=CJrZepp8{=_gX}OG4mVt+Ef8J9f+ZM-8b%{|Bn2-i~UL&negTqF?T}QlB55KPq*;P5j`?QqQjIhoGH9_h6h=O|l=3<NLGni`~%C8OWzzy#;yJ2b~xHqJ{Cz$R6yg&Zk!I_I~foMi=tnNJ-e`ogXbCNA~~1b|>2Q_oYsP=F9v8R&9p=t1{VV2K`2KX{uab`I+1|YRzHzPYkZb{oa39>S6nn4bU4~YS6!+PU<SF=`i|@(!~!=lHawN+p#a0O`7=Uj>*3L!dj`PZHeokvCrbX_06;z-1kC>2|wpi<kdKryAgh)do}#B50}Y%_xo4jf7wwb?@PIiGij6f_3M^<`&wRs3w~}zxvXy(@@K@wY=$4PaVh+|nYgdD)nEEQJ+}<L*0K=&uQbVg&IUgO-x^Vky!>pxykEJm&V}C?FZ0>&E91DV>9Q_crA~TZk@v8yb0T!@wVfFM;o@fWH`_Ad^E<&PIWGIcrXBe>ukDG0`pfT&7O;38)X{+ZnlHNKzHdY>hZ?6VF-})_b7uZ6UtJp_zi9r{Pt#QN^?Y?LD)jo~Ql>g?>VN*^DoOlapIq_rN&n|JSKutQbeh_}MDHg*Nd6IZ23f^io>w}DT;PcxdLo}Xjhs)OPQ8yj(-TuXF`J<{k2-;zN6w-qkh92%)Hre?*+z{d+sL<5L&&$2gQ@+<!DRJS+>6?q+K=o@4W#xX2a<22hLCR~-$9Ke-$A~M8b`j1JdT<`9!JimP9SHKr&6bohk0VOC!(lh$WdgSdN)}oM^o=1N0VbbF`PP<dJlOlIg_C{gL*ePgPcYkLrx>7P)Czf$oDc7+o{9IBRvu8iBN{(aOwzhIC&`5PPTKLp$x_S8H$6bQRE=<0IE(NKpsquCJ!bLp~jGhkR!Zu8o^LJ$P;1IJE_CTcar0&W6AMkgPKV;$Uk5x&ZTCMbICc>G;$7kGBt%fnLLSlFL@GqB13T!)lRl^4U!m&lc}-fWO6EXBsrCw?uqf#QPh#-QRIQtQ1U=>ABJLoYB<@S96%jPR@$E&K)!h>_MrxmeaL>)0p$EVpI%|U|LrgOzYbFkaLXU|f4}n9pBe8fS9qHL{L#tJ^Hb02*~ofnOFg<>?L^u?0FydmK>'

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
