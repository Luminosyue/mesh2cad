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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_005.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_005.stl', 'source_sha256': 'b7cbfebc364eabddeb152faa463a0eab67ef7b28bc0297ccfbcba9d1f6c95bbd', 'input_faces': 34, 'input_vertices': 36, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.27326077222824097, -0.4501279294490814, 0.09931081533432007], [0.32928287982940674, -0.39416101574897766, 0.1539742648601532]]}
GEOMETRY_BASE85 = 'c$}q`Ur19?9LLY*pE)z9wmF+luSU&a^`b;p;3cAmtQeR`_0Z<rQnGDs!;+A0J@gcoNG16Yw8U320#n<r$*@31rJ|xl1U>X*pg~Ar_x$c}YriOnI^*#DoG-uoyT5aG_+3XsMy8Reqmqq99yWf+V2sZ^W@KHSV7T4w3GMd<x;3l-d_I!ef4b?E<E(~tv1_(gPskm#9TIFuya#P|!RGY`!$Fttf<M^m;r?+~N64f2p*B~*qpYiI4%mg7y>_8T_}7uElptGr-qtHBtko^Ycum%UC|^q>y~LO9ugiQbM<0XltZP>N^G~DcekvY)DKbiYd3G7{h_4oDeA|NwzGiD1G=J$P@l)|he@6E%-52AImrzegAii{^7<}fwMg92bbExxJKlN9Rjzj#$49zcOPecCc1o7F@IOG?b8|R3>rB(CT&Qagr0q<pVy~LOE2h}>q28l0z{iyD1VjO(&Q(_hBjNO5H*wrcU<u|=6kmvF<)qkRyC;QT$RL|{<h4^guBGf5Y@1ya)*cAA#6U3JjU%+R>P2f9|^{hwL^Ss?MpI(n-zNzjv?5FQ_#$UjGE?p<SxX=Rkg!%5yr|(w`UsTVbyPwv%)CYOk&?EZZ`Wx#1Vi=<F;edLd-+!j{zcxW0Ir5$4VY8c)kl(vS;@O@)$Rm9#S|I0tctEaqknV7AWOcYi%NU<}r8{_CX{~{qd?fYvt)ad4?^;9cf42r+Mz%6_sN0Zr$hkN<8&LC+4ag=`BeDtEifTc&B3Gc6B3B@rQHzny$c3l{$c4yxsN0eAkaJM=$T`Rw)J$XzGDF2~4TEzQst#F)XTiBdnLGJCL#;#>kgHI4Ay*-np_U_;As3<UKz1}}w8o4-eR6&diEn~@fPQ_FUdQw&%au*1E~ld*i~s*jtNc0@?S$12<j02^'

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
