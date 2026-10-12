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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_007.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_007.stl', 'source_sha256': 'd1e3231dd9306418c07193a3809e834c8d5e7004188667b64fb55118794ae936', 'input_faces': 24, 'input_vertices': 27, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18066713213920593, -0.0799192488193512, -0.018891338258981705], [0.15585435926914215, 0.17194777727127075, 0.19777071475982666]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;1Xu5B^;9Lx+1Ak4!c!cdl4RFavTTCA5>P|3(302T)U7(Ll9)HfiKk)e#CT0JGTIJrpON<rNw%|cyAK|L+MsH7+{FFwC0B^4y@mY7qV3KTESNGwPN@->Xibrg&>brfn9$OT+LCmfJeIKCg`miQ|x?19vS@|PRzk;EJL@(zIb4)6FjBa1UUp9~g%AhT#6L|^{_uzGX04Io;f-DC$?+>2{JSiR4Ly&yh=^weV@dV%GoePH!TOkh4krTt+r&3qgz&TvE(tiHkC>LA$OUCj{jf`v1{v?$jB6!8yt*Mj*X5OD<!^)9ga(@M91-Q%gZA6cBie#>&Oyy(J1DB|ZccY@u~8*maud_vbQu=y96j-rUWECBNvd?$hZ;h_9|yFC_n!o|_txxm5}98T!|ZCL0E7Do@ChK2@+dbIFVh?oR+AA0y7Fu4s0*Mi$KLE;DOA|~%g7SDr-CvX&OL{T3HNe>PVXzJ0^2~->-oxs$ir4t3t&k*$|<H6yU@Q-D;eE>=>nz&8<$^u4U&;T(fFc+mIB4r_vAPB%{>{%$&gt#nZLU9&i1-gL+h<TwjH<S&cg`jL+C|eMUL2M}~EeT~yK-mI74DuQq5HmqB8`NwN%>!k#K-t_-%mX!#2Wo~8l$M0DIiSJI4#fOG%m>8cKr9BOMW7hO7KPG$P_`(PEeypVHYb$kg0i`wW^+O@hz%;`0=yZSM3`|EkqFQLj!)zQ6I~~2vOw191~dzvNCLcBLE!`pI3|WdkVa4pF#rJPOcam'

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
