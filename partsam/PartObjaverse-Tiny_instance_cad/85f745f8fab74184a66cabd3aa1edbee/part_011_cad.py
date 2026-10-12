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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_011.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_011.stl', 'source_sha256': '96cae3d53a781ebf3766468b15a1db90a406344d828b004fe71c7a5be15585d9', 'input_faces': 36, 'input_vertices': 34, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.232768714427948, -0.4999999701976776, -0.19598540663719177], [0.2477806955575943, 0.35562920570373535, 0.061314329504966736]]}
GEOMETRY_BASE85 = 'c$}qGZAep57(SboTGLwF{77>*B3B^Mht;s65oE>s7=2I{(pGMyh}tGXL~x6KSoCSx2LvrGw1^7(p;783({#&9%#t!)zlsR^QB(-A?s@LJx{HFS124~Wp8KBn<J@!Zb=YG@8JRMsusKC{m*0$GjGK-bS%uqMUbw^Un^{t}Tf-(m=OcnA*KAzv$kVV2w#QQ7_U-Umas<mFkJXYTSUjcPa<8joTdB9e&GlSYvCl2*zMZZzw>+OdH#<w1J0nZjEBxyiE0-YV2fJH&Eh$%<IEt0hZH~6It3l{3dyZpnZg1om+MEg9mVNd<&^q(<5*ei&AprmDzFQon_BRJO`q%n8p|_h_pr2@{<^Hz1xOV7|*0dq-nSvXLlli;>&j*h`<LI<MmGHdZ(ZuI$pz#U(j!wRb{8b<C@VU5Uqz&ta`>w$MSg;j(jvfBCd9NC{?p&GBfjAfMA-<$b>Ox<A<%*usGK9Eizg$B7)1E;O<-Z+-p6jVW-M%l-h1`Lc$TyOB0sg(49w1*}UoZS>mz_u7ABv%e!ePV@c@9-^6qa6rF0C{|_n+&>ev5U@ivQqeCI0K}mB`=xH7b6nQ96h?M@BkP&x&r;DQu~(2UaP%WUfYhXU&3Z&|fHe=zS3J*?Q+?r4L1q#JB0*p<i2BxJ#`|Q+trt8M`o`u2Wc0s?>R7Z9v_Zv}6c<`L`YpsQ1C9uf{$&trr67_@aIt_Kocd2cq_QZz}fLSuX_D?<KUj1a*o<`=R@Xnh{^@2;)79nTCfr4?UHSkY~dxoGbsQYnU_tw`Rl}_TnB0%Nrj<pWUmRw{_Ngt&XVMZa!stJWI<Mw|M!sdt9ok&P6^V`1`9~nEiKGeg1!6^%S{=RN2xAClgO6ZX)B{K*qU|jPne_RN@)LClO8{K8g5vGS0`5ajqldJb_S8JdtoBp`Q3e;>m<5#FL4q5vCJQBc4QPBA!G%k<3JS5{T;v4a5!9f23w3^${;y9FBp40&)IL9V45WFqZge*+$8xC5$1iCC&&n#2t2x))@1rU(3%SVuAWc^Xtm!W2#;`EXVqBXdU*^yk5B=E!!ny9%kPG8ApOr'

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
