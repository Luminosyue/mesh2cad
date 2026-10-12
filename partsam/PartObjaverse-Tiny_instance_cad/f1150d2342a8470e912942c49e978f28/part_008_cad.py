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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_008.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_008.stl', 'source_sha256': '0c6a5239f006e3a25f62b0ee6738b286cc31f9148f26ea625a6375dd0a85eaf4', 'input_faces': 40, 'input_vertices': 32, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09574461728334427, 0.051501065492630005, 0.2858567237854004], [0.04818906635046005, 0.07532849907875061, 0.34958744049072266]]}
GEOMETRY_BASE85 = 'c$}q`O=uHA6vrnYHA$1UG1+{m)vS0}EwKb!P)j8hq$p9z#X~MOq1|YqwslhqD#GH?iwE(b7kls^QnVkJDxyU^d(hOg;7yO-Jo(<{pD{B;5FL2@|MS~7Z{NZjwp<DX4bfT$#k<pAzqtV+IAX#O%eJ#LJ8d_H=NE7IMBL-N+Is)ur3>YXPb`aD){NblcC0be8n2(Q@}^Z^aF(3f{M3RoV>6$u%{6S|jjOdqoA!rCj^)jfBYE?-`LC;&S}?cnY`x`PDwm%XNxr;~d@gqKL)BH@uY7;Fqww`B&v`$Q7*hGYzzg1sCsRrt_wn&HZ|}ZrD*VTp4X@7Yf|@^e*W)4^SL(a3&TjI)I<)O^H*7ufcp~rB7dJ~E6`lllel``}Jh$F8e+OL8pUZjuteh--QuwtNH#bsh{?SvLUGs-qyq!PcTYJ#0f62A}CD;0wT<c$Qt$)e2{w3G?mt5<Adwlh2vCI5OuFa3++Wbha%}<-_^CP)7Kay+nBYEfil$G0i{zGuG>ZeB(5xTwgTF2F8$g8d0ukP&VUtQhN!hc`gDD^Nv(T89kgZ9I-hT#(waf)7O7(Pj{n<4|wc?L8MZ@{OZ8Tbs&vgdvxs22fG;vM~{mw-=02jJ828E6zfiW=?rMDVUKdW}I1_!xX2GzFi+S@t~?K8gTT!0)06QiQ-c&kqg3hmgbm0L38A4T7`ZPqBw02hMqWp*i>*a@g;q$l_cUoPD|E^BaLb{aSu6*ZYXhAB}!e9qZ1MZ>W|W@^Yz%`=^idi|eEnZ}$shoj3I'

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
