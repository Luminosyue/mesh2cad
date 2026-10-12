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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_000.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_000.stl', 'source_sha256': '37e41f2577d688aa3851272a1400b358825f891b03269574e54b09543445f096', 'input_faces': 34, 'input_vertices': 30, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1501571238040924, -0.4581805467605591, 0.01472465693950653], [0.150157168507576, -0.1501094251871109, 0.18291699886322021]]}
GEOMETRY_BASE85 = 'c$}q_O=uHA7=~x_)7mtvX%elm7DgznLaIWG#6Mg;cnQiPc!&p^kZv?k(l#kUO_db|5hMl0iyqt-f53w|cxVs)tc_Me5UCYu55n4(D&k48XJ=-=)t#asI`Hwn^Dy)7&X>$8aknRotg#7=)MKX<H$t@hD2$3~ekhw(3tMvorv(&XoDN&B9X@(UNeHNjN>Z;{Nav+pSlW|`Nl`3i`tw8iRIaB#->Xu7Fx6L32``*X4X9+kxodkAcWsH{v-n?!kGz7Mh*kFyHAj|TKP9Ty?y<SejjB|q9DO|Y+{y9R2UC<ALf<5vCxOd1KEI(HUznM2a&vf$@#KkQ#mV*E-=<mqV8w89W4_}B<>u1#Z7%20RFysVa^qts$F&`dC+{a7(zym)s~>q!xm>dHZH~t+uHBuV;MR{?9L;23a{SAuS(cySbI`2Cjo}qJlNQHM_#AmO@{Z+?E%58lSX}Pp^W~hyH8Z3;xqcjSdSYcR=gxW7XLM;B$I-<O)@QBA=g7*!E4F@F;&TkK#&{`xl|9eqZ>|2|>p`9473kZ6y=5oII`qFeRdI52ac+*Szp|5CuYI@rX71<n<!8|6@g$dH+_L(hpCer1ZsX$8&Cc~MglIL9+n7l?t|EnW*!ugcnC<?%tJwYDS5YMI&`xR%DL1GGv>m($d>FI^{94cuXbbod_#kK-_#pTV^!%W$pl#q=!AC$hf{%drfr{XL;G0M_gRX|6-VZ8*7vXGvDCz@_^9P`)_kw!Bd*Ga2DElY3dtndi1yZX>HIixob%AdHzYbIYFTh^vmAK#vyZ`iw|1~taiTmKM+{ynPojc1U>*t?SiF@gLkr#5IL82e%3DFNSfk6f'

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
