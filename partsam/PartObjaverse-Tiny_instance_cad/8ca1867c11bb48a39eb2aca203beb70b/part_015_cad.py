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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_015.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_015.stl', 'source_sha256': '87b9ac8a31262081ddc08e2a28ef0639dd23939d3a8858ed0e159df644d6e373', 'input_faces': 48, 'input_vertices': 45, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07077665627002716, 0.17078113555908203, -0.05088382214307785], [0.020387820899486542, 0.2343299686908722, 0.0617833137512207]]}
GEOMETRY_BASE85 = 'c$}q{OK1~87{@1@he@?<tnt;_c9UAS)gX#hst8>WdnvX75%C~tY*Sm*K9W-KQ5p{wAvY^U#L^lCt71h@-Zqz3FNz1ji$awm2wnsgyr?s?|Jm-2D~K-q`G51vH(%zplO)=_z6dd&D49QcVCjjE5T;cmLPpY=;l8ePc6<NeSq}+w&K}_t?MDtJj(NxkIj?o6vt1c&pQ`QeY1ZPZ)-#Y9&ZPR21DWnL<E^RF*)-+Z-qc{4wi}vu$JJepadlMv*QbOIK|fXV*q~lKG5EZN`N=D@h6`5%+FXl`>z97G<_j+Ji?hZf#!17QdES2i>W<;Yr^YAUxPIpKj9VT3V&4M?pM18!+T>t+-f-c1^5r#qzBONIJc5h*`iD+u{!r;X!-bP@;h{a>S|2H2aFJiEQ=IGYspGEU!byH<&Yo|LN6NRxgZ$j>y|>)z%UsTv>&x64&(G0<+xp1dnlHG#J~FrR&lPXFo*$Wu^CNNV{K#CKAHn7GBXR5efd6)WBrfVNepMV?ycdGY?~%+!e&?6y1kc+M;^XP;n4aS8g)z=^$?u%cyt`cBpR3-hX5BG!UVBn}9Y~?X<gJABV)FhCKAxS&O&$t7<?WAUyiP8^$hm$!Z+`EE7t<{X$E|nxZSQzdp<Ss$^w#T1*{(bW*(2Qj%Ij<TyDP8xzpp%Y^Rjy{46i`Eo@y;s9lRDXo8~&IP4F1v%~V^cHo~hAt9(fa3Bp6RxCU+J0mRkl<A(<k*Pu@=6vcR=$g6`?+n8dg7Xz=x7I~-?xEJvT!hWI%sf3pyF2y{`;Z=wg^ew}D>+xAV`c*-d$gf0hIoylbk2(6FAod}M^(cW@ypn1KJOB?NuE2hT;St1s)UAemSepnu4EK@ceP2V&J!ifeaRb#hsz$1<R2o&BD$(XqBHlm!<S#!tw%Cq80CG>~Yh&;Ejn=YWqC}gY&6jR~LWZb+W-CH|0op{+eg'

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
