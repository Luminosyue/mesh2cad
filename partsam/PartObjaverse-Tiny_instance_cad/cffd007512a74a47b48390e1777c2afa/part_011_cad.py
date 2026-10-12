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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_011.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_011.stl', 'source_sha256': 'b558a5fb3b246b32152ac1c2a87c16054f8d3cffc5fc329ad834cd373fcd6dca', 'input_faces': 34, 'input_vertices': 42, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3702528476715088, 0.15610405802726746, -0.057443905621767044], [0.3914848566055298, 0.17207345366477966, 0.13207219541072845]]}
GEOMETRY_BASE85 = 'c$}q`OK1~O6ozjm58Im7Xk%hcnogVABoY;y&{k2Jl~99a1YL*=jm-p8w24V+5EZf#L<Ap*n-*Q@MllN)ii^?|je-a&3O*XJf})7H>q?8BJNL|F?ifY%!p}YP&7c3A8HO7vZniiHTb<<W&O0Zw7DA}(#7QRP+<1CK&aWTK9yJk%!s$}?3&Xp2NPA3Vf*cDZ<@`u4uvrXjNeu+TVjz{tjpq_$`!cztO!>CNp}Y({e=w1i;W`-Y4U3UbSUe&A>uRDiY`XPw5VqLywH3OHPqXDg9WNJc5A?ja;WqO}=I(Pmc$fJL;YwX@$RVB?#zSxU9M>%4)pLL3^V1(0|M7^;Gdsom4P5hodcpYUF5Yk8s-MigVSW2YIlqx>`BMulr`pBm8@QH#dXeRn`uKbU*YY=Zzf!np<^Ah=6dwER<@wbF^Y?$dSC7ZOJNY@=CmH|XGra%Hb^8{lE6jg=fbUy+%>45r&kOIFfBOMGC;5f>3&Xr$T44U?7kU5IMaGAoDZDt8zByBe$IhR*q331fT23E%t?;j>_`bb@!ef_w6@9*utNAJ~BmX6*no;-_V-E8D#vJ6@oE=S!4?p4OY-?sYlV0BMYGM4{;To5?)5`kr+TK+HAykcUTBQ=Yql!Yh)V=;um5%<^Q5A{)_fgdjGx(IT+1`b9C)V94TCbtc3tA2Gf;#Y;)*j^a+6AJoV<o5+>lGjeh@Oph<SL_k3)b|W4b*^M2i`M-tfaPREuhzq-Ueh=?AeMlw9)sio6&>UB0fU^WWgRLlo|WD(W_>-@%h}?gVsHu5Xg^v5NiQvvSA-T_VS~L){USgpk~lg&@#|+kQ6rwPV?{n0&A;ChvohdjlbkSNBu8LkfnW`Qrt@CgrNm;guVni75NEN0hXi'

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
