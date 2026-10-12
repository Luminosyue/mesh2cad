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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_009.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_009.stl', 'source_sha256': '9519048008388e7bda10b85f58f68ba52df58794f9e8b677059ef7f5bd057a7e', 'input_faces': 26, 'input_vertices': 27, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02509807050228119, -0.12718640267848969, -0.32021719217300415], [0.17448125779628754, 0.031702280044555664, 0.1594545841217041]]}
GEOMETRY_BASE85 = 'c$}q_UuaTM9LJA3Yc7}0*=EJy_T&nQs8y~aSBMLwC4oitFlAnuZEU7X`a^M{s1yc;W3^FZw5T2y6g?yqXk+*iNP|&94_&CI>Y*^9dZ_O2cYe2Bqaf<QkMH+>IOlhM=id7}0l%Tf&iGix#(jq`*BTguFf%(#iHV_DkC<FL5I?SCR^%{L&2|NM2M*|1ik);u#AHvxxkYepi@KdI!5JM)3?;$?-GhmU2;3L$Pl^gp_J-r4^4z+9vrE{p+9jM4{&mzr4SVj7c|b?9sG+{%t-PWgFQ0P0rezd#^7+nLP-*xL=k06)w4*$Q^Ciz`&P(ZW<Y^zym-lx+K+as>w}afdFqhZzZ<Q+^4Hr7kA}_>zg}ipY(VgRY#+;ZxetI5xuP3L?FTA@qSH&s6%Gs+OoF95Pq2*H0i(J0ZiTkSgg;KPNtMd!jDm+i75zj4@A5A0AeC2%C)=A{@W90HxGrkWd^<BjJPn^4r`Cim>zS4_aemy^h^>kS|KlUt*?>`{&_pkC#?hNXgk2C!IcFylsMsVNOgP31RHF4g5^b)E*#`CD$U&8rvOA+@iymxRueG}&w+A5e|daExY-`8+nyKgA6k@L~ea8>;u_HurGT^94yJwYx<gPa>ocwXsCdBzi{>Y`b%PR{8VgD@#w6b)-y2p|kqf8Ro}w!dqkP5<3O(8*8=l&@E!ku41H7Sd(pE#$2f;2osP$%C#S?;zhy+C;vYyo~~U1F4<7ooWMLqeQI|Mp6@b;ERZXn#nIFT|#Om4|m2=S`S)J-a$24Np0jUq>R)?KH%5s?S?;HoeM+4@2tH@e_dJqyJ%PXlw3c5o`By7=TknCo*hxN9Zt`F0Al|iF8'

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
