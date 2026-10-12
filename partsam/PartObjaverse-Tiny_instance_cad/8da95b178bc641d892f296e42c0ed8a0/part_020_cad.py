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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_020.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_020.stl', 'source_sha256': '10a6468e95926d4ed45159acfa952489271f7478b6097b22307525ff79466da7', 'input_faces': 123, 'input_vertices': 97, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44927018880844116, -0.10814821720123291, -0.2959285378456116], [0.2786605954170227, 0.4999999403953552, 0.2951596975326538]]}
GEOMETRY_BASE85 = 'c$}q}eN0tl9LFDCL_q;xu8MDYMR`$gq9FJR_dvcNs9X&S)bx^G#7sp%mPU45t4+6NWm7COV%m#;VEK-<-J`7)lnXIK&5X^Qo3@54Ta6h#zvuZrbk4n}t<`bAeLv^pbD#5^-+k`AXL$0%!W~Q=W7v|#Z6S4$j8XMt4p!r<tX{X;S2by4#nuqkUwArH?pa*4$Ws!+YS^<$YkXC!E0bnAlV+DqPjWev$~IM2SC(#EwW)HAkNmvSr>lJ2SCyAm`1pD9jA<@s+IW}qIp=>pqWBVwcH_FA*7C;Dk40|pZ1bDEbHDU@YmQ;|Mjgf<`0}vXYsyz_IP5n0j(zZNk2lPo!Rxnfwwb*#cj8IA^%yzQ2aeZ^9pZXgz<7NnJjUz4oD#m?w@uD}=!jUq@|yBB3+3xVj!B<gd_s(Sp;q)k`3|@A?DsX|zO=nZ<b9=H+T|AOuNCw6_zd_HL*@LP?@NDYQ=RZXZjs}azYCA?thhnmmutguasJYBF<yB?`N9W>M9w&f>;AD%oOd^i_4oK$@KwhQ^LS(Am=DeU?D3=FRsUZ*AlFlS`5n>U%r?1C;Mw!iYagAJ^Iv~e&huX1(_;Lv2XZ~|>;w4QH|6+SzkMh6;ak<>TwmRI!Ef@~LFrlh-V5UY-wkaN=e?^gioDp_<TrU^Y33z6uOIAv*>=40r_VK6=D(M9O=O#Oyr%pqIi6ivaaQ;}&6f2jucwq>vh@M$Q9f`z%Cn}IubS7>b6w@J9_{C&=f!#XQ|;#YmDiM4^A8#EshqdbGG2L2dDWkkn_q}*|LF(e^^_97oo6|DlpS}wt={R`=(qE1LAkj9-RaF1|H}0(emmcJrBa;7WJ{mkh4o|<`0YF^bBXy&Jyx&X_WJESGm0qdGYXsKe*64;k<TpLN#pC&)(dacH%M>%xx?&x=Ba;kt*zHzFBS7|uC?BmvwExF&g&I5qM!SB2h3Bk-f!o<>wJ{X^9^#H-QBpaQPXL>_s&V%d4fFVsUO&Ezs^99b$UN(mDg?DCHvEQX1jP_JlAadrhH)Eg1qY6qI<UQ3%eq{K4Jei*3XyphVt0Y-uU~r`yt3<KXhyfZxQG2h#Ml$tljN5`M`Y`<gpL+Ut?SB_IZ$3`}|&Fi>05;wT;F*uew_-{Y0O=b#txr;Byz`)#vVbiJWKc4NKpYXXQ66ed{QE(mD^m2ZB7l2lOtz#qxgT?tM|r@Ayo9uiu|+`JPnXP#)LSw6L#5o=&!o@A|4$_<-+WZO>(SZvMUSSf1*J>^#>sCxS7mNd8n;R%&{rBT0u!`$xKUQ~%W?-IUa{|M^T8wV1DAIlXJhLhu6cJmjNb%DG_58DPrk;B;Qos8`5YU`jWbG6zhV3#MEIru2X*3&4~M!IbmCl-Xd)EHLFvFl7c<15ZT}PeKt-M$QCJ2B#vkz^UNb$ZYUz@FOVVCCK^U`M8HADB>by0k{ZUf+Ajq^ng9+*D@6GV<_UK$XswP`o0uJJO@RbiFAYAc>gj{#AztvDadJH%5?A)a0+^xf_|sKPep2A+IzH*Xg|@%Du!1ainu>A7Tg~^fY&hOU}P+KFgO}T+!q-G?hB4WI>1rje!N1E>L89lI=~U&KFBz5AMg-fBay?Aao{-I&u|p+K;!`MK=2^bJr6<=k3bQRLJ<!|4h9beM<S!ak>K9EdLhG+(cozGD;z}}hKvG-fkTn~z^aeL`Me(HRm|%NoD)yrmB;IG6!A*r3NWP?JeJo)UgMGZ;IYUtDB>h!KG?}Ckykvf<-+wRfRmB&;CPHrM&^O@@EYP(yvFf*2t_;^*P={7jsuUwYZ5Rf!8CUw?llp91#%VGlOGc52>Yi$EBt-v)O5=q83JEv{pm8l@>_n|^F!vz?<Ib|LixYVJd0>|vcCY7^_40'

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
