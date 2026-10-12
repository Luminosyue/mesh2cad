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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_016.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_016.stl', 'source_sha256': 'dcc594fa58ccc1ccb1ee98c397eff76b67a4dedffb407057cd077a9e74d65571', 'input_faces': 86, 'input_vertices': 66, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18291211128234863, 0.018879011273384094, 0.24913012981414795], [0.17703409492969513, 0.07698801159858704, 0.4616674482822418]]}
GEOMETRY_BASE85 = 'c$}q{Z%kWN7{)J!ZjOK3Xqj`cc{|uTSYZ<wqaE0)(ZrCME`|^LK%^NZ5+`M4BM37#@r%*;#krWMkutWiqDHobL^07qU}9VZ`BPwwWEp00$uuTzW=k}B-}gNCuJ;TRqj!1o{O-fK=e#>T=iKYBO--{a;&Lc={&4jUtWp$GreasxgW;pihk|XTEv>JlDC;<<OZOAc)$R8mOi|jEE@xw~?NHe1QJvLIRZf@cYzl>sh661xgu;zM%AW}wZVPI8+lztLpmx8bveKoN7rE3|)&F{>Qw{yi-+WCzS@x+{GvCCGY4UiiUgV=W{dBL+zBEf7jXlq~FLZ2x^YQ#CawWD?wD0)h0^h&3JVD-Y?ypOfM?UxTalcna68v0WOympwpYi>~9FKeLY`4fScYZ?mk=f%s?zPheBLC|8Ij-|+@f?rSduEKs?FwAv@kUNfa-BW<Mc&cF^{8V9f8g;yw2g9pG5sv}e|>bG|NhRAVa`7qit>0jyRV2mDDt5Zu3ufgF>lHzJ!0M#4kt``=zy4?sh*kSJkl}D^+d+qJa6jTjySis*S*L6{JQHZ|Gz9x4RLO*JHhR4mo1s{)9I(UpIiGDP5JQqF;VAF^T~N+E{Es2VIh<-<>8w1qR!r#<lNWk=J||#caQ6g|Ga&W`_DdklIy%(zGTY#EWO<St?I?(JTmqsuOHv?&H3cq_p)_B%v)>1lpnjt^)yVKnKAX>RnPUrFF(ucMD1Ma;oN5Bd5hk8Ysr-NU+5Ljzq^>6N5(xLbN@d+xsaU4Tj~eI`usLwYTtf9{9e<4&Y1G!gItgD{Rdo6!|TnzKfXdeMlRK(=W;!IF4tqUm+CQcsUFq7*yCMke)L?PALI|r5Ap}*M{h6BkDg2QC|_<H^scaej9gkjdM>XYJ(t&ykxT2x=wDht4HHifaW3sIBbWA<kxTna&*lAP<kJ4qb9sM7e^cY!zjO{n?=}u|E}cI{E}cI{E}cKoyR9OZ&bLTb_a%1eyp3kXM4o&;`%Q1VjMlvAH_{Y^v_^Z|H3gDhbrjO2`^vAn=8Avys;m0{ue!Zj4UcK6got-T#KrKP;9_tgd>fejQE(x63;YrA7Vt)hI0quO!8d`)?O+=?6C%!{WvYq38nWS8;B0U%+z!qK=fO9D$yIP3*a6=Tc7UA_aS7Z7E&-Rr%fRGS;Bv5A(-WHLobo}$HE=iBjrKJVaW#A|xEkz*SAxCZeGu^;_-^nX@GgkB2wn^>0vEsw!G-u;3n1dn@QvWj;D;gN_3#|<dhj}kI0J42lV^f6!08b2YIqiyd=+>#I1M6Bf$-JIZdLAI#1>5tX-ZXSGYhwXEoid_B3=v62CoHgfaiiYfb-#bU~&gIAG{Ur1aAfJfQU=sCE!wU1-u+g?gm$YJ(~QrDHeO`KYg;_zalhYrVn`eN%QfS{NyiMU&dkRueI{LTeN>iG(S(jsPZ>xEo}A'

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
