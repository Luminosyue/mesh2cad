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

PART_NAME = 'part_023'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_023.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_023.stl', 'source_sha256': 'fbbe31feaea653de8527ff12998cefc17ae8147e38e5c96dd5ba7956a8138240', 'input_faces': 44, 'input_vertices': 56, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.004288971424102783, -0.13153164088726044, -0.1787557750940323], [0.3941783010959625, 0.07822401821613312, 0.19283427298069]]}
GEOMETRY_BASE85 = 'c$}q{ZAep57{|{x-*u&B_M+J>t7$GvH#KDFvZz3+eThnfw)FZ!;man&ipBjB5kx2vK?GfdzWEXwHjLP%k<7{wmSs>jp)Y;157EcyoO7RJcZU;19e8;D=f`vY_uS{+on23pB_$u}V=KyQp0#SJ2$9G^`6wv+`#M|XKt)&2MH9-UoD7z49XoN<bJ~Q0=(4R<4z&1fb&}21w$EmlY;E2CKEJQ)Y`4EvCj5}^LO{km(BbQm@w~LU#x6O^>{3Yj*O5i`;2G?V;N*T*Fh#P|zcd{YaPRBGNnFu%o+v*u-5}uFo24W!y|so#{*3ef-Z`D~{){t!%@r7I5bU4l%%5?7|2*gY`Tg^p_viP|bLKBKdudksMn~zqc<#B8yF+P@==}p%!kv2ko!JqR6IaehMO^tbPwNv-Md!i$y8nT3%GHT$I=}sq)=QVJM@3vQPttnt)8UxWN1M7D6>;XT6;8%P{yb;?TKGlG*az*i92IfaAIACqB!0}tME&78>yPvx@QTh|!D0FwXY1+xtCkSu-t>1G;c9<#%*fHh{So>;yc|vD8&8hV=X;}ZTEr2nR|oa$J_*t5s<AWrd$M>>=Xa0OdbRzWkW1fgQXefti;H}u_L;cIhvzFkmc_WJ5AMdVaZw)_=lih2xjyim^&#>7%L3ik!t!H!-HwAp5d%-W2Y#x4$XKt=yCw)%xOy*eH`J@Obsy+`4M<_5KjUu3xq9B8@g#pw(&<08Jl;ECMu<cvKK<K#hNGWAGFTQL{hiLgI{KZ?|33PQ@E&q;knL|Fj|Imj(8VxckE0OB2FOLA^I+{}$VH&n;aG#C0P<SUb{xBDi}bt=^mZJ(aM(caf%y*dKHw;YTn>6CjuNOZfi*T*L)Ml-t^mCkhZ9E?<QmXbpdFBFL07^W2jnWy4ydVwTn#!6M>>vGkXM5y|Et+J%#bah&7jjDryF!O%(KCV=`5IMfj7}sL_RMNN`;&P+N8f)_~p|_2Ix%CR>(O9jbQF+GMV!&fBKa9JrsHo<A)8uGWlm<T=^4wt^6oFO{wJGaZ}8w7v~wen_rZWB9H'

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
