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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_005.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_005.stl', 'source_sha256': '09144ab9927e343ef17a0ba23108065b83a8906ce0941201aff958e619c9dca9', 'input_faces': 22, 'input_vertices': 24, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2211896777153015, 0.06141185760498047, 0.03357745707035065], [-0.21350151300430298, 0.06831151247024536, 0.04001714289188385]]}
GEOMETRY_BASE85 = 'c$}q_L1+_E5QZn4w6*EhrY2Dk#h24sjDk%|TM0Cl;GrS9heoi7ZAdpZM4Dtb6lyIj=)sc+UWx~4tq3APiwJ_0rd}gK(2I&Uy(vW$A%d;@-b{5@6hsFe|G!^mXNH$y)r8v<0E`d})f-o;5&%Ck1Ylaz%ejnZ9GWW5xWFekk1f4+Je5>WxnLS*l?lzr=*khMM6>-$m?_zUUe?o7V+DOe<NR3qoS|9Vm`oQn>v?~7Pnboz!fcNHYj~{@%#SCYuJT#NOZNu3j9y&g3Rj1bw?^;tXLIGe;AU#Tk#DlOTSABWk-vW=^2g^-W1Y_tM;+)bV*c$Aa{pt@KXX!Wi0?t}J+LhD1`cAKy}KQKWBH|<;`e$Gc^eaTSpB--5ZSCb@`sbi_iZ@2Tt@!(D{|%+bz+q`)_>M;aC4=ATwX_hG>7vW5v<erfP6BKymu7y@4l|t@29%yLw@OH&3+H?q!0O875VdT*mwQiqR`4J@{ol0vn*qNc>(#CKEW40RWLt!19?1({NW41;nghi=8WL6J0;`~W{{`O3eNKLSjRJh{LKaI>pQ$Ss5-WPMAqw<T>$*FTHBvZ+g6`L9$WhR)z9_(-RgJ$_v-JmX4q++AZdVnki4IC2YEmFPEsHFPVyb3+sSv3Zzq+>x07!Jeo3faQklG$d<*F|@-5_nl&(?)_YxiMJ)~~(9`a43&E(aDOA5IE^a=YJrf6pWp#A!$^Y6F6xnb4%u?%XWiTAb!m7rwl8lMcl17Jc0m;'

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
