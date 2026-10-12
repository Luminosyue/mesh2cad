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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_010.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_010.stl', 'source_sha256': 'c1e9207380e99edf79895d08878cbb09865d93590ff7f47e13b55a1f3ff034b6', 'input_faces': 32, 'input_vertices': 37, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16025054454803467, 0.14292103052139282, -0.17242518067359924], [0.046181902289390564, 0.49999964237213135, 0.17242549359798431]]}
GEOMETRY_BASE85 = 'c$}?OZAep57(SabKbo3rwsPg>l$NxLGP6S4{geF|*`g$jD2Gmz#OY>Ag>^HGKnh7kOAM7VA;tWNzEIa(R#5aqva&A=f20MaAP7-*&bxPZuPlh@z{B&r&pqco=e+0a%xv<LDT${=lQ4JM@QfcJ4056*#a4S!Zl=|-HoxGgge(G|H7{4CrtLJROGq&}uFtYMGVS`UT76RXX1zhH&$ii%?3VmPHhY$p`6-q>hn4z{97}<f#;f8J4choPgSJ%ruPvCZL3P^QPl->ScwuDR;;LaWmpA1CKdJu>^GQ^G3yX=V417*jGXniDareQOp78Xys-J_OV(4OVMnf8W=iB!|9&VkY74pfx-Ua_%>`NAB=u$d_zO(%``20leO~y{udGNU#eZxYZd)#{m@{C=4%3^KkNhhqwdgeCxu4M2>Go}Z?uSjV1?91eW`9_Ypgg&|Acmnx#NA8LGuaAa2T!3Ow=sS098G<}HT#Lw`JnQkxtD8mnldnS^M$J-D9xipwd+<wE-ZBd3{W%N1^IJk2iyOxRFT=PCac`l2kYW(N&sNldukV5SH&(~=06%Q2ggiqBJm>PGxf^(P+bNj$a>*;m^Ih@)=G~JBK1u0>{?4lXo#4w?r^Ehb!>}*sOhXss8Q;N!zjqq)@U{py^tbhv83pGxcfRv{?>X|%+~r0e_rdGWzYjc_u7rFa3c=^5&N;#F7^nsAs{^0ZtD&C!Zh1ZA87~#ji$1^ov-rLp3~Yk<V-5T+xJNxu2TrMP^0hDi%cmxv>(^hs2CT01tjEyVZZwNtjl<oO9FbB<5ky~&Y>VK@fDeSsvF|4%cjMnZ85{n~lfhoEPz2K<$bqOsP%lI<9gG}=IvBMaS&CYYIt;;dII;vaV;Smj)U;A0l43c9n!=xA0Yw0Xf+B)qDT3)06w4@7I4%;$c|FEDWHo9X>KKGZ;A?Q43bl7FjJ3!b)EXSmbSzu}LY5$yRw9^Qj9@y7!fcXAm41Kv%lX}SRwU6M(EO3&YbPAJi57J35}Hl^td6voloV1fgy<LfG<G`'

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
