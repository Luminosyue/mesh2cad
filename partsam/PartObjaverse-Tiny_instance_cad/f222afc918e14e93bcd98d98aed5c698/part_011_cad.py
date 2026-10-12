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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_011.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_011.stl', 'source_sha256': 'b017d97cfadcc7374d57a19a867a9429f0562325fc6d7cc4c0776ae1c6e58364', 'input_faces': 186, 'input_vertices': 143, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36363598704338074, -0.36363598704338074, 0.1818237602710724], [0.36363685131073, 0.45454496145248413, 0.727267324924469]]}
GEOMETRY_BASE85 = 'c$}q}&2v;m6vbZ>P>~N2!neZkAp;nYK)@J*gpdy)B#e+q05ODQLZV1Q5+ewKprRt;#+5t$8(gqcbRkQnT(GbxvC1m-A8_MB`!c^fd2`;R%F?OoI;T(H?mq9mdwb?hrlo9Jd6fICj5b#;ZvTCD6j_@Ul}BUQ;n9Jf?8v6GLl;V-xes;wIDXpJ(V9705{*R{)4kb|p5b&&D!rqxI$e=U_YDq@4tJmJ8XWG;n%>lXW+WT*k^b(XZ0N76tlC<U+Pc0XHJ<v9pT~oR2j4f|`#Rw51x@#At-oi{{n{dW^wZxz7w8_R@$^0Z_7|gfi^Z#+U;mqiTk-YkqNY2=^anRa?-tW17I7V-M}I85Uraw)Gx|$hPc`IxX}s%G#n(kAel1vksPRrwKj;ZR=&A1-e~atUmkqay>fh#2?~m(xe_U5TuB#u{^?E1wExg{k^Nn|k`EgzSxUPO&S3j<+pUHi5ep0@l<d5p^M|Jn3y8BVx{kX3Aqxw|w3ICEmswezN{<!Y>qwBb?>uA2^_2`E`zbdv4dSV^PPu2DQYksOe)%torH9uX~{8U~2Xnv}$el$Om`^xie&h4juKL4@tUR=LToaVFY?q7BHue$qJ-Tk|+`K<a>@qWFkdtT-DC2te{CI3}V_(xYiuB#ud7uP-i)sNPZ>gvaJ_2atw(Ynj))K|if)T8PNKj;ZR=m|gQ2|rSgswdW$dURduQFXmutw+_>kJe-Uxl7%-u5~v-U+YeF_o=%3RNZ~5?mm<I=I)#8ll4{T$947Ny86+&R$cvQU90YSlJ}plJGpOC@2V&6o7B7NiTft?uDbf1tj9v1dJd?rKJ^?>U47~~pnAe*zD~uboDZree9HNtdcvoi52`18%J;tN37_)4uX@6#oHNON3w`Q2qq_Rhb4K+<9?E&*dck>;DR@g<IOnfD)ia{V+Klj)*w-C<MKsYqj>TUQ2de(vD`NHb|NDwq7CcN3trVOFFA1%TODaRNPhV)+(9VFb!|Ot;MKkP;@m=%{d*HqB*T4a|#q2~gJO%H84}kq}i`ju@*bP4g?*~uA-@xxEI0D}n+Mdw%gAMRAT;m8h4Bs1CJ@e|BW4t-E-Hh*MY%kYle$RnJG2Tz#a1d_T2sdns#hhl`@GSfw`)9!Y@HX~82=0To;<XLj3qQv`=fSsPyotWy0eB1k#=t@NAl}BnH{lmUdpopuz^m{Me7y{2;1+X%IKv5eJAOOBgYd&#TRYeWKabxl;N=)UK;Q5X{3Wh!92|p>aV_KECHPgmeF%O4?_~d@U<dpNUOT~d_!ahlAG`)XgeUhl4!;b)2EG^Lm*^Y53%?QCE1`W1o`8Q8+HuB@GiLmHXvY{o#+dOg`ZvMr@RN*v0^WpM9ju9Rbz=Aod{tyeX72njtc6?ctY+S7=F}6DBF=DEjIW??xHHC=(>L4!PqS__xEpSDvo6ZzpW(Cc4a{i;o8eXqYolE57_Nt}r@sMA!#9G5!B)7>IRsX~E9h?oeT_=+2zVI2nK_l9$8G^T!6Wca_^aRvxZ(3~!)mzY#dgNGGiKcKVjJVz7&C6UQN?%_W5#RfcY(*?FEVx#?1J0#pB3fu#&9;={^PW-(pBI}xINRE%$v!aHN-qdoM9@)AEj@&BE}z~Z@3)(1nZ{3)o^>(bKrA`Gj6#wH_GLc;gj%1p)Cw;E4T%2_xq{PUI3qlTg(FD7Q~*dJ%?q?TgIGfV#<j#+zhwpvy^#Dnd7{iemV1<&u6~jb8vf}OIU9S^PSJ9KcD%|=P}=K6WnrOG3za6zVmtX=P}=Srlq8`ylkq!<|jWB_Cu!Nk9wV1_;W2jb8UEl`5$kYmg)BV!w;d-hhLJP*^`U@0j<COmH'

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
