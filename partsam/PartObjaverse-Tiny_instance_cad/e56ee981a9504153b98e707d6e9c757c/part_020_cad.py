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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_020.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_020.stl', 'source_sha256': '8e6cbe0d217d73f889e5849b961ecae92dc8093b101a704d06870af8720e8c47', 'input_faces': 26, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2782948613166809, -0.23030894994735718, 0.21959565579891205], [0.40895962715148926, -0.0987934023141861, 0.2632923722267151]]}
GEOMETRY_BASE85 = 'c$}q`T}TvB6vywntEO36u4!pCTDE>HJ?Iu$kqeoWV(mjFmg#P~mLO`o=Jr7`^bjS{OKtTKF=Q4!NDn6FNA0Lk`Gp^qA3ZD^)I(22Qb-ha@407mCJdr3{5fZS_soCp+&i4H<?9Vb!bc(*PaSHO41_R65F=@Dy6UUSo$ie_b*FSB3OE}|yt=orz*ejy4djfe!s#w|nYIe1?Uh?hX2Dch>#BD-YRYO|6;8%;9o23p<?dsSIw!qOu~^JPW~x~@EBxySr%SMUN5-<*T0HNc_-K%?B@Jh*xZJ?GI5{{9*L#fPEJ`Km-HZo>(h;a1Jr7*Y&F<FtAQzD<K6cj>aAEdQr`kvOzVjul=VnBg+DGB?4bBxG>B@cJV(8NjwU3+-`3igv7k8?C6fT!=uK0*|&H=Yx$kX`Pv;4f?o2>CsxQJZw3A7fy2A}F98Xu{!h4URJG(HL^$mjOC-#h{SJwLSXb+Q3?pwz0_AB9WE6(8$|*$Mt$30-O*@!qCMsGn)noR`Aw$me|G+JOtcPVKqx@=QVOcqRjHiywmfw~4^T{aKu&KZ$MzF2uNj+wZ3HdR-fE>2i|~p4%D%^#R`};Px_Iui8KGz%UK|Up+l)f2n96aI3$pPhBq`umKmo?H*>_nuz<EcL=x~movn;r0l<?mit%xdo}AfdpPeqt?`lcxA=31E`g8r#WeT%*aAGz`FwzJ;^jVpckR6X_P`+H0{W2lx7^?Lc|k6CGW*p&_NEzLfAI_W%eZgC^`F2=S;m0I=V;m+Snt7tesw)@nmNzOo3FQNy4%A%Z{uSfAxvSkyHz?=t&Kr8l(=wftFru6Ys=XD->r=;JC<rW#u&__sa8-KF~(w^OtqeB1I850S5n1O#bI29`BJK7gtd7dBQak>6@~LrILGp}Y)`3@Fs{RV5!GU<5R74%hf;;(d^par+(ea1m4-1L^VM)fgd|{GgLx2DFdiX`dd%4|8F1c!b1b*z>w=8>KmF3?hY07a{=xlzr}lGE-|44bb03c_KbXBQeRvQ#PU9F{{Q^C;#Gn'

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
