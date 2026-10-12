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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_000.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_000.stl', 'source_sha256': '5a7ae07d4c9cc1ad30afe77617175aec6dab1648eab303a7f4430353eb0e68eb', 'input_faces': 60, 'input_vertices': 32, 'input_watertight': True, 'input_winding_consistent': True, 'input_bounds': [[0.02831900864839554, 0.0413021445274353, -0.17626529932022095], [0.05282513052225113, 0.22811293601989746, 0.17653241753578186]]}
GEOMETRY_BASE85 = 'c$}q`&1(}u7{(_bo94S|nlx?GB-?|el^~jmhzL!f3N<LJkV6Zip-r$LNt={NsX~sPEa)X*D)t~2{R_Nk4%&mI3Lf-Qp%gq+5CsK~I<xak+#RZjF1$R?{&x4BXD4|REoZZb2tS62I`wt8VIzc<mxM^YSY4c(Db@~^=a(!bpmTNzy>l*qR-3YrI$2K67Hc!r<Owx-vUEI|Qj?`hb+K9~U#e7Ri;SNxT&)!;uU#q37wP%PSURPSji%Ha>c1Xt7G?cMYn){n9o}Nv*k0LqwhwQQ9C^VwX$DqxevtE><tNX__u=hUb3;EbXYc8K@4wqL_LsTn-?(@|=j7AdO=BOy8*BW2v2OcXc1^#3D{aazbJ0KZd6M&2X;Xfgch;TW)p=uL&y-*0o&9<9k@Hh~rkpYt{oCJH9_rVt{>MyJkzeBEJ@4PHG&!$xp1F>Fkhr>v{ePKV*Y(zc2fB*>tqBv~*+&2D8P0EWep&RFcn1A5ch5i4xixRfFLRNf^iFf`$eZ%ZypuoU;Lm?4oAS$C<j;KYaQ>}q$}e+0zh;`=rJD<{H9DEBTy%O%1;glS7+LL)qdRx>uSWOS;r|}pAkEN4s|Urrf>*KAvOpDh1@~A`%v)*MpblskJkub&1HPA51lk7;!uP?4p*`?n_z;Tu091ijkd=8qtwCBo=m5Nvun&d(taA0i`*4pJ#e6@lA!rOb03U;oLkHpG@Cg+2QK%n23g1o319e0F@P1@+LtXF@>`?+5H~28l!^juMUd6ydc%K;dXb3D|c-H{-upjD$C-8Q7C(gxZ?}mEdEx6`_y5R|~IiW822=+yMHxf8^fOSKo@D8kHgBN?L<t)~a?RS5rzm5i5-1NsPKWQFg<C9M*=?t}&Q`q|SC9PzE>LmNdlb_-XNY4'

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
