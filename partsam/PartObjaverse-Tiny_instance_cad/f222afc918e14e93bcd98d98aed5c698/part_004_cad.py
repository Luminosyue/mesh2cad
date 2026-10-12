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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_004.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_004.stl', 'source_sha256': '47414e1f2884753f1ac1b754d82158c29e9e02db2a3cabc7728dc2f44cee1126', 'input_faces': 48, 'input_vertices': 39, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09089994430541992, 0.3977339267730713, 0.18181799352169037], [0.1818263828754425, 0.4204549789428711, 0.27274444699287415]]}
GEOMETRY_BASE85 = 'c$}qG%}X0W6rX$<jWMPg6QgOf8sjR2Ui1(}(2E`#EPH9eLo17JP!P47AczRLd-Uq9_&0dzAuR<DqN0~l58~1PpvQJz{OxA<?FywG7=9o7_U)TDyR%v)6i$h!F(N*GpS+p~3qdn3Qew|A>zivv?e+HVen2E!J`D?x-@aScRsv#A9H{F?ZOv3?6?Lv!R!fRn-7)K?zP-9*t{dbp>032J`n3&x*N}Q*YNn)2O_r2H<zGjPYA7$B%}Z!}xcNz_y!m`F@8d5-Z!i7)hW`87H@-J><Mf+9j_&;OTRzWk`8>ZJkNgX1(QIAcueYB2aJ_i$=PRdmS3F-Y_pN%kZ`I?8XZ7&)a-Zkt>-EI*^?rH0bFJ&-@tbcSn9t)qePF&_C-dz(dAwC8d`};k&+~iwz~fnds}G*_^8Tck&i(h@?YH;E?YH-Z#oPPx<a_ts?eqNJeP{8MUvr%@U*G?_Zw6(EoL%yisp^g+hD;h3`X4cy(|>iuOqc)rh#8eNjLSI)%z+o7M}VW?Ip|?v5uC1Npfm7_$d!YagHJq9dm!fkFzw)D(1b(a1?W6b0Uv_S0t?`I<SPKP;Az}50L+5N<?N9&2n;#+3uwY9coI4e>;aELcL0;%apX$^JHY9T@5ZY`7;x}jXu=410y+ll29H38feG*!@+E*_@P0YzmF)y}IruAR!aneq(EY#^xK;@SQ=#X6vF*`lEzJ4D<#)P28|R%>nalo&v`U0}Cz}`)pCszkaq$P1AbGR'

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
