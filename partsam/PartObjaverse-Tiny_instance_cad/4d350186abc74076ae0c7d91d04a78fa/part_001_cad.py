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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d350186abc74076ae0c7d91d04a78fa/part_001.stl', 'relative_path': '4d350186abc74076ae0c7d91d04a78fa/part_001.stl', 'source_sha256': '3d799370673ef56804399090447f722bb3a278682c7fb99830a39bf764b4e41b', 'input_faces': 12, 'input_vertices': 20, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.47031834721565247, -0.319623738527298, -0.022809138521552086], [-0.43317875266075134, -0.23842190206050873, 0.08514810353517532]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;2?`#jku2}}$OAk4!c!cdl4RFavTTCA5>P|3(302T)U7(Ll9)HfiKk)e#CT0JGTIJrpON<rNw%|cyAK|L+MsH7+{FFwC0B^4y@mY7qV3KTESNGwPN@->VMbQFv=brfn9$OT+LCn#)^ytf}nKbTN_1x!mzPXy5lcSXVC3sl<9f#`<)@)N*()9-h|@}VVQ^#?NFb%FIA`V1C-u%;cNKKFG8h)ys)2NqwDRRmU_;2u34OedUzm@}sZtp35P_-SCiZx2}fz!`{og;rm%c*3oYyAXY?VD$?$f~JD?@l~U`$5^ZvEN)p25ijfjt7oW|?*{8L$^wfse1`Zpp=R+Uu=?0Eh`lc${$)^D0S<=+tE2CL#i8NjP!+$$9;E(SI9NOZ8a@eu^T6T>xn5xL1yJ`lBt~uqi7)u&1{QxX8{*#u7Bj%&4_17?4R+^ti2E6Gd$)qcFMkG$KPZ5>U%}-JSUiDaFIb!b>R$zBR*1OqP89VHx16`y2cV?RrV}R~3NSJ-fG{U8b*3dEB~6eZ2*7CUNi)-gsHACVL~+uDI)i~3N;5&(>_E&0#H>)71<K|IVlJpW7gP?!<^*C6s5}Q$4#XA&`4xzTp|lW`%@4$UK+FrJd7$h7Z$>5&W?Wev0UE##N6z@@I#HtmS?4^US@1{+@MdL$c$|r$5J<lShXeploC(w'

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
