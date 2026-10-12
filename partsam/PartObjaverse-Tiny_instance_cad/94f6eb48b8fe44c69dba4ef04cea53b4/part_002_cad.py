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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_002.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_002.stl', 'source_sha256': 'a698b5d04a73f63b980c3356f44d3eec58de3080184f97197a032dbcb612bfcd', 'input_faces': 97, 'input_vertices': 65, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11759123206138611, -0.11926977336406708, 0.3392237424850464], [-0.10416270792484283, 0.07636623084545135, 0.4457363486289978]]}
GEOMETRY_BASE85 = 'c$}q|ZA@EL7{^arK$tM06vj3NcM~lyg>AOuO$IeH#)ND((S0z{tj#DXzHGAvj3H(hjc=J|ANBzg4XcZDxNL|U`T+%QT(TtuO$3Kj$h=*$l914eCdT-|cwYXu+|$&==xv_-|NY(5=RW5-=iZz8I&E1FB95Kp@bqxb`#FTL$R`fc9}M^Q91TVqj-7bLLJB!&hoNT<9X{xL+CuutfU_$YIU07hD$cg<W~WPWb{`M-h6Bfr91nK|8GkJBLL^9eBosIiq~EI>_qh~zjZ1k|`LD+&T7ufQZEBjTcjc|C9aNR|=a)N7T>JW6&eb2kxGA`ubJF6z%)a}VzFNq{N!-0?=BmM0uEjEO|JsX7QXc30DCdcxSSGHo4N2qGxn<6yKb>C4#I^VlUXQoWD)N-~yvF(3;F82oe#yB%c}eEKy!<-Pk3OVx4cATQD*BV+9}kQ1>u)X#{?{buXC8fLTFL_+Sbt;Ml!x^F$+<c>Jj_(rs}=?SopbNCfph$P{1EuBB2V7QOH8BjPKm2Gei-3A5sjI-{>;G<`MMbIJ$pgymsx4N^2F`)=K4urQsh~^@j2&-b1^gbR{S=`Ir^E-^|U++cr;ay;L%$jea7c^cV<b-b86@^=kdx#GxrZZ%egoCAs?^xu8KU4Z?Ew4E8oQ={)dCtuP0|QJ|Xz(opIie<avo}^G}VN>rdxK{RSrkkBp1@zek>1VtoJGQ*s``qu^@XyJ+SrxR&@NX6Alya`(EFpIp2;Dc2*o{;A-)ULxh!z}1yGDSs4PNq)fdD?PU-GTqk(CwJPU=SDg=o*St=2FG(l56y}3v!|u|H^rmF(tW3eW&|Ibk?tccbY1Y8Q__8;g}&ij8#^!}j~6_B|7)Qs&Xu3vllGgzy*Hnf_FFVGF_CG%8C-chDeZGLbY&vbep5rEoa^(Wlk#}MRd8cnyrGL?Uf{<18axWl*ViY#)goQb?a$AqZ!{Wt^sUw%Ful?kWQU=dUuiv_fAvahY5L!<v<6y36OD%u%(u{R)9}#P4c!O78-5QBHf1M`9B2uAE@2ZV!~)HMXL=8OK8<ZO3J}Z}BA72jFuxtwwW2Pjo8eg<Hk`NN9P|5W)Y9mH*1>ncH$yAno8cRwrSOgL4@1l0Sr6>Ez8%-zgWgr5mrOUAddqwRG#lQHxp<I=<t>7G;5`__d>f5jG+Lnwd^^s0p{?+2O}3!-OtavtX}D-?g(~p()2Kqvt1#c~_zhc22ZH%xtaSnE+YDa>Erc(Ew?m8J?eI2e9=r|S3eAPj#Wk#$n+x;ag*n$l+u_?WrXIa!J>Lt>g5L|@1l<DP1m6O!glBb@p$Em7PZ|2Hpe_a1WuEPIw&w}-K9j!}-wVjbJyC#pTF`&C9<|U1;cMaRur}qWfoUn(xOYlXC({bk+A;5h*1^{yrxUeTqi^-_HR$sLn4bc_6}l6i=??g6s1w0_33Lb9*qbHjudmZ$b=dyt@4?2QvgSyC7SewyKZ4D_T%fs94`g3wHveZ~rJt8rQT!@@182CmA^'

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
