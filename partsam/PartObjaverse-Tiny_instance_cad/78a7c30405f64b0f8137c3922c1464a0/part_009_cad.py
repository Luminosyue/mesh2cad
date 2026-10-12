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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_009.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_009.stl', 'source_sha256': '74801e38e8b36f74fb958cba4133c40046f494de3be13bde1ceef5484605c5bb', 'input_faces': 60, 'input_vertices': 32, 'input_watertight': True, 'input_winding_consistent': True, 'input_bounds': [[0.06478603184223175, -0.07422766089439392, -0.28307753801345825], [0.22762081027030945, 0.019595980644226074, 0.2830772399902344]]}
GEOMETRY_BASE85 = 'c$}q`Ur19?9LLYy)VVoz)9Zhyw;-l6BD5kR(Wf9Jxi3<JkZW!zh_lUvC}TYYf%KwD^fn`i49PzfLD2TvKTt`CAeb*fg`hq3@1^efo$oyzgCgp{;rl(Geec=1=bRtc>~iMmOtf7rIlO!&<z$R^FVoq0G%+?5i6-}sjGoh&k2r6(PIvblH+wZU&dvu1qRB`ic-ROYi5&`tj9@ID7)yjlPQ?=gQO=Kshm%o@CkMl$QES}P)*3R}nnT8f@vqHeEunLDW}$<x<z)I2*ZxS~N=D^_f*Ys%R!HAP7K!(ty+HYv_SKBaQ-T}K?W<g~+f7Tvw|v*s`6d4%xIKT`{aJ8t&y+g9<htPY{OR@U%fz!UBb49V5P6%kb>g`X8<aObwcID39+*_~k}n7@^RI6_AZ{3O+L!IXT1Mr$M&fKMutv{)3q2I;>7M9N@{;ESxAWQR6HjP7dGnq+zvPz%xAUEMjHhCq1#@a%@;Sj}zU~$A)aKw~MtNV!-wSTPZ|d&sGn(i7fq6AA`B%a1eAfR_@Z9tg&5QGr{0%tHD;4N{PCCPuiQ_&<J_U~Zkez)*oV}f-eX#F?<T=6ReVgC?g66s1x{y)to6T<tPWR2+QN4Svwq7)?%H-W`Rc|b;l&*=AHUC(;L;L@#bPw+P@6xTY)=+EpIw&7kLo499>WcScti$`D#qd6OFVqe1g)f9U;kh~#uVL(f=dHo&^;U0$1{7b3aR9ywS_WSQUk)vSFNZIMdf>ShDZT(>t}eyrVeEp>$NF7Zw+l=|-hrG0@017C;5Fp!Oab<!1bgR!7Qz=I<H4Sn;Y{jrR+Ug4UPq=9c`wFZ{6`t`{P|jF13cf`8tggOI(YluG(sETi?M%h?1K~g<^(H(mcrNIKPqr8ew>>htO^={FUD`B&~kXQOLOSX-+fAdwiI0~^~3t>lRL{;ee$tIWKo-4`TPv519Px5mLB78%YFdV%~F&'

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
