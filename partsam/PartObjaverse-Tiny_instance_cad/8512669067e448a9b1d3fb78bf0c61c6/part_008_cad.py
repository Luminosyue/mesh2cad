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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_008.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_008.stl', 'source_sha256': '00bc71bf594a69c6851cc5aee236fffb04cd48ef88db9e851af3273b1b394ca7', 'input_faces': 54, 'input_vertices': 53, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.032520413398742676, 0.2910354435443878, -0.13230469822883606], [0.05846841633319855, 0.37111303210258484, -0.04301730543375015]]}
GEOMETRY_BASE85 = 'c$}qHZ%ma{96t8~@+T0{%bz6c1(J($L4n(}X5AOJpd#A^R!gf1yIjf{pciGDnJ?w?Ps{SQS&7<38A*fzHaEK_Z`oR3@&iQZ>ce&Qp=Asgtrb~z&vTwzudTLLXFGeI^Xzw?^E<!ych9c3CNAC~)W{PfZC59@BnTmAs&I%7e_+!(pTE7db;DMhm;+so7{2nrgR8u&ZK6YLb2j<geF5hknsY_-a;HmkHn#;f1sYq|wgsB}Qm<-!vfUrm+n;FM;E%40ZmV!<6^mTjcJ0586q&=$-q1)C%vG%uo+ujq`%lVssA?Z{F_;KlRF1uixNoZ8kQjOBAared0P)7XWzhB7?VrP^?-F$VSjG{F+C905j|8Wc&y_^zdQXq?&*>V1&pW>yf?i(&pN87{VXTL$pd06wAwE=abpU$b_g(N$-i&zRaKqmy{|<V@YpQ!ayBq$ddl__NWl)`)wL|6qQw4N$reFD_Wy0TB8$5_}PFEn_-1G9=sLN<8bTO2P_|TV)!|L3Jp-0}#QTO%rARn=N_UrK9+KqU9p4pG}csz8mW_ldwK3;zUJ_A3z27IIw@mlp)$Wt7?A9^Hvu{w8eCC(MK-LESD3HX>7yO5`u@Z$mG?@Aei&&PMF`uHvcB{mFQ9EJXoU)86_3*89a^%?SC{=D)((X<bBE}Vgnek^kkzMC(1V&AneeDv^HRkxxn=vp|8cq5P>hR?OqXRvQ<De?@}j-E#RjM5`r=MXQR{uT8R=6W0Qyby<cjH!nAq3@hrgL}T`gOC2=dH5T3M_aMqeO%qk*V2dh%Lg`MT^EFZ!?(MRBafHHI}!iMLilT6>^h71D|OF7-?Ih&+Ti&!xMy)k5P5t(sqXvel!<s3_2Ijf&yxHRRd=N~Ouhgg!%?mBFIBo$A5uP#&FZ!4`iCvZ(=5n=u3uW&Wz9!tKKg#!A#476EdP_0A?tn3*nQXU4O#1B#OhOUxZ7G!gZ0#RJ$2M$slUnko2e^$J(lk%>eP4C)07_jjt0M@c`6J&)(<B8!DyL+9_t@*M)i+ao&J``(r+R5TV%(PevhR;_1jf{hCYZukM*;`el~(r10GBNhh+bIuY0vWz3;beNpV8RnH+t!n;R`pwiM-v;om>m>)ikD$#(zmCwo>j2boF|r{wWO8+kmrohZoVNFcY9CleFNlgU$wH;|{2rxWLpr<2d)lzc8RjeIV71~G{|iMeKQN<N!Y@)V+-+|K+Y&zHR++cr9HCFT(|@;ved#GA+$kk2RHNIsuDi|8Pim`R>Ro=wal&nC|$-b|iLeha7Mg~WyA5*L#fk}u+vyp*_<yp+6*SV3M!UQTqAOI$);PF_NEk(ZDcvz|`YvVgpZSWND%vDqDQ|Mb`A&taeet$&36y7T&<pLOS{sMjAqMsH1m?EPpH*u};u{w%vk{0;=G2zL'

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
