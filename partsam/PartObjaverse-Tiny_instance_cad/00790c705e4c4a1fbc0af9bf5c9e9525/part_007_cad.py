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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_007.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_007.stl', 'source_sha256': 'cf5a5f30611b469522c3b61752919177dfb0849bb8cecb55ae0869274b15d9d3', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15661296248435974, -0.2036806046962738, 0.1567831039428711], [-0.15539297461509705, -0.2016303539276123, 0.1594037115573883]]}
GEOMETRY_BASE85 = 'c$}q`-Afcv7{<@;&aUoiwqLq_q>j7FmTe^{rBXOvWWk~?L8(x=o30-ay6%b;5iJBp-P#|pH<d!rO$60NL+(XMAfZSQ;gEKrh*?rWNi}nx*K(pD>cH?k^W&Z8yywhtCKNOYZiZ3DBG2;1?E+)kmCf92BpM&??}{e&4#dtIn4NQNZ0cCc@#av6fsL>W{_bd^EAFos{Rew${Q=S6GZ-I^M+Q0v<K0n>H$~1SqAE}HMPgC)erI)UK&;*s5HE`VI&5kS@?uu{k*dk5xu=>+K4-dtE4X;<1?OT}9_MV$%DFN$!#O+WK>aOn=0c8q81-^*Cg;+<S<X|E2lcJsis3nO?oduF1H2LS(zkqY6L@lTn)C2u^vNbHx_sqI5$7ofIJ2N$zTrkcW^lzx>zys(Jlt>A<%=EYQ|>eC_CZ?oa-Lihbp40t3X$^wJly*d>$>gdT)Zae_D%McBF7=<_MbJDV_nlG@TPh2iap>biDw~S^j3mjHDca{1@w8S8u=1&yMlS|R$+hA3^}`(kn_3@eO?D=GjEWi9Kil}eVyd>mbd6<Ny5B!;Hml*<cv08-u5q?vojy?UIIr^FMuoFb>t5o0U!Isxm2(Lez_Gn8y~?heMU|UoRzL4Uo=f|eRzU%#r>XhvBJo?+}wuu=y}I^xYEFRN&!z6u3=sK80X1EJJ#!31rORdmnKeuCsr`;hLv;W$!YA{{4(-yf+try(Pwapb2$Vqxg+Rjc>%n}3EtM5ZV2g4llc1ht12U7+GSNwlb*<yqeO$+*wo)2CH*yjca-e^@1vwb?V((~e54|IO-sr9$a_gk$a~3`(WUuf(jDZB$rq6pk}o1(K$=g!fV_t^kGzL`E~%S*E_oNJle~+(gVavmK|Y6cJNX>)*`(XZXOp*)W|6m%&m^^y&m?al%^+_fFOZta3*=3tM)D@|22w^o6f_v!ra%3<evYJ8toxDu`lS9d-TGvUn)TzO4F%0w?`ji9Hl*r(e)k=PQix*'

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
