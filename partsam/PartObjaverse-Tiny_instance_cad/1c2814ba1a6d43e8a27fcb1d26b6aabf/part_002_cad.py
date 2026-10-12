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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1c2814ba1a6d43e8a27fcb1d26b6aabf/part_002.stl', 'relative_path': '1c2814ba1a6d43e8a27fcb1d26b6aabf/part_002.stl', 'source_sha256': '2d679516c48308a9407dfa39ce0f9742c42f20b25acbaaecb51e6c216a6ef4fc', 'input_faces': 56, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05278387665748596, -0.4988442659378052, 0.282568097114563], [0.4292749762535095, -0.3414829671382904, 0.42601168155670166]]}
GEOMETRY_BASE85 = 'c$}?OO=}ZT6n&FvzB<WdlBOn6+fI_!Q3!6TQbegJxQUk8xNucNJHdjqb*2=G6!IV3_!mTR;SbQR+_)12Nfdv9J9ln;H=c=;`<@`;3zu`|+>`t6n>X{u@0v4J@oO~2_ip{1Gb02=K~%+I5FYGo1<}Rb{Ubv-W1U8fPdDz}_3s<vP(1OrgJ>)CuDaf}{+icuz5ZT!5cYOA_rmRf^xM5hQ6Tl`VQ)W>*XLK)I_~O)j(hC>>zJh;jx#UbN*FlbzK-$P{D*a&{_fT&so#hiUv&P79{UHCJL|goTxWizKG&K5Wb^${=bz~C4~ETGx_%U$`FTHz&iuR|Md$Tj4nAq?$9n9)`TC8vf37pX(m&UkU+JIgygu)r>&*XPH2kRZPjvWCt{;tb>s55-=j&B;=I85GbY7pWSJ9cDuUFB@?@yg3pMUhTt|<gXUY;iXUg9Vrkw%RAqh#mOUmYcvul$#zgibXBm<Bh%O<)#WAeRD~;1n6;GpI#lLB?4bOTb0&IppSnOW+hm<mbRG^kAV63p(+<jFOBT&<4*SpG)|1s84g%fXxJ7#5JJ{p2b{wL=p28QL6;3ftSF`zy`RDoC7R_m*H`Mb?_#7Xaif|HRKw=Hu#E+Wf^CHr@?6-W^w=0;1;j~Zh^=5yn;QcV9ypXM;kTUm@nonT(>Ycae5sJGEQMVb=-qGG#gk*?3s;yv!N6ByGE*N{^?WwdkpAdoceI{e@?%a$$xIhT9cR5@21DkaZ3IkOMFgGfcOamafkx'

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
