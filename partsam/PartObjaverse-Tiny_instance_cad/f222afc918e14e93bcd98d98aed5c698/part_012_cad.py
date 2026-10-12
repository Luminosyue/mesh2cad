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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_012.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_012.stl', 'source_sha256': 'a56faf83f0dfcdd55325a34c02b4ff18f9d14cd9608cb2a058692a25d9591bd2', 'input_faces': 132, 'input_vertices': 57, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.36363598704338074, 0.18181799352169037, 0.4545449912548065], [0.2727103531360626, 0.45454496145248413, 0.49999117851257324]]}
GEOMETRY_BASE85 = 'c$}q|O-~b17=<q_1^a<e+JdD;S_+iXf<pO<F~LM(Lp0sEaAgRTNMZn6LSl@O|KKlh@4_8BWXDojVPcH#T)S|sGxEIk^3IqTo#f`6_i*mqb4VsPt*r*zlji)%o7#)cqYoit+!ZrPvtMuQZLQavQ`@^w+f2_d-F*aK-n)Od_Mpw|n`gz1dUL%|ypb#3+*~YHa>dP^#$ID>`{7PwqweY}Ymb|CM{hn_+pRnE_}oGzS1na?&vXC!M4Sj;-YuWKJ;#$J7jO4}TJq7&#~+_<J=eE)>gN|-`;SvAXMTRsJ$`(mAHUi=^~<Ss?bkWAuKhZv);)gdqx~xXtvkyne)+Yo{W`zawO{Agy2r2bYhC>2{qmt-eywZ2&aZXt*ZH;X@vHn=Z~4vcw<Ev&O4oi*ex+-_C%@7?ew|<G;y?Jha=7G^U+dbh^J`uEb$+dT{3^fJTi=W1*59wvwcqpoDqZ_M->=d=e*OI_UHo#Met%21-&4DAE4*%&zQ5@(#$93OR@hv#t^`+fA3^^sVQcoUu7v68%zxeqkp(A1)me++9DLSU^Jw$vF2C-q8E1`y6YvS<5;zUN=By%f5pCMqQv^%!8P1*nEAR?)8LYzPoGMs`%bpTghD)ysI0cvY&4H8f3Z61J377mia2P(!oVR-A={CeXgjTZl41syL<R1n{;3Lcht5?A~rwkV0vL_D~;L>XZ9D|QBk6L|4t-lq(QMly40uI0jnA29TG~N1{`_b~&o_;V5m;3`@7M^9!SiLgVIR!8Smpy4P1D9S|@G4y1Hwq5Ivv@M#AYAhIfW7cu=D5`>PPcC6ZnU(uryGpJC4VoNgeRF3R<DG0P6kZCWltPTz@=9b?1T3)r>wpy>zqL_1(!VuFa?)hm%s=-!W_2xhUwhN+=&*q_H=?_xb%vEF?ftQYW0m;=On-=T=s;)C|r8Qz{_xXUkdDk$M8hKF1X}x1B37&bHM5qpqpVfXklxQ0RwQ!9|S}25OcfLtKB*$3bw-~e+cY=*H+sC$>5)U0{wmt+<+H;5b2#4uSt7npQE%c&Dv_H<GgslJaLP=|4H)`Ess4l'

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
