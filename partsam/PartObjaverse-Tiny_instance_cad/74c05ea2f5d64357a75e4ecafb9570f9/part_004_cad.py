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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/74c05ea2f5d64357a75e4ecafb9570f9/part_004.stl', 'relative_path': '74c05ea2f5d64357a75e4ecafb9570f9/part_004.stl', 'source_sha256': 'c1126f9c1f0aeea418d695be2eb749a518fbe7947fe2ebc6750412f118c3fd11', 'input_faces': 26, 'input_vertices': 54, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.18919801712036133, 0.06763000786304474, -0.3190036714076996], [0.19358842074871063, 0.0682491734623909, -0.29617926478385925]]}
GEOMETRY_BASE85 = 'c$}q`Jxml)5Xa~400l))Jr(@o;Rg$PqH>24Vgi-TsaXmVZS*d%r-<QWj}VP9o~4Dx#6s+dTG&cuV!=^iVJwu+Xs)ue!&>L<%{*^spNY|z{PUmvB|CZh-^qJ!F42&J+Uf*vu=B;^MgXnNkb-&7pPLx-O1)Dvw_}hDxL)i}E{<MsFUMdW?l|LKY0P&9m2<W@;G~sPoc8DZ!qnAif85jjT;XQPLteUGnDOwryFZ&&nVz(|tNwMh=smnV^KJ-jIOD$7o_};>ZP~)rs}U=&tPEIr`E!T8&yOZ6uP%K5WbL!GX63{0-&#3*dv4{6KOcm6p1-$!*2*Ds$;vC|hwOcdT>&pITnqT(`jt>_l5=j7b8eA7l$+$7Tci)=COPLOIp-!h=f=E3oO6?$bCaBNi}az~;NjDNSHDb#=SpxhSAv_l65Py{?89><xS1=#&0Gm?=88Ccoea;F;AXA_H*+QXh<uo<a%;fz_g8Ct^;Rf1$vHR4IXB5Uw@4q#O>)jna?VY1&W*Vu&bdj>xk=8sMfy-~lFQtfSD&qaTy{gJ`MtKK<eM0PRx_UF#X{XtuAyG+_M?0v`&UPK-|7E8%KLE-S(JlnMePB71=YNr>Mk84>Iius)tgXls21|wR3Ap2LLDMMNp&-77iuH<PO1;0P6W}_yqD??C>?7P`3|ZT>Nu){JWaK}9k-(z$hT2_0CfztpZqA*2~-jlC*Ml-K2#5CFL^iB`j>5?-|XgM@l@hZSNQK$4*qlfg)ZL=k4ycVAF!7h9yiyhza2LihgtL$oeum01@{LL'

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
