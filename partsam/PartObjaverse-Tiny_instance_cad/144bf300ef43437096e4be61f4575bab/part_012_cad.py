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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_012.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_012.stl', 'source_sha256': '52cf62a32fd392a67b2ec7088de5ffdb1708a041cf95dc203d78f15ce889ce29', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30644866824150085, -0.09685730934143066, 0.31406736373901367], [-0.2470785528421402, 0.011042766273021698, 0.4018913507461548]]}
GEOMETRY_BASE85 = 'c$}q`X-HI26vyv4qn74UZcQ$|)+w_+%1UrPlp&H$kY!TlkRxe}HEL0lG*PyEh|-CqmDi$FU<~C_6f_WJE2UYH5ls-5R3t(4q4nMWIa3-1Q5P=f+}}O-f6qPda-StbZ-^As28koJi|>XTgpj?Dh!ksW_R_+owvsWcR<GBIaB$gt)|Htx+p<t6)(VFy-&V5JZknc;QVNnyNs6hU*j{S4u3A!T&$mgQW?fNY(|E};>uQ@e9x*XFNtrk@Nhw$UwFPM@c-s%%zpPnvQ?V+obKm*LshU-dDd5WSF*V>9v%&KgOab@oD?cu+*F6(loSM}NoyNq2(u#8j9)X{J--2=Shb5T*TK7<LrQjO4*<po_`tBpR*ilRICvKg`zI(5O=e<+GoiQzySl65n?%Y~U@gJKvA}_;e;x{)_e0yahZ09x7nO+L+x!H9H`@Ts7_ZWyfqqa9eFTS1f$zBQWt;hm5&sA_Pvo#l7H6DY$>iB|qvvCof>-NqD=w0okd@AOX{`}!pnD2b`0Q!rGo41VIkGyvKQ@m>)ol6&jI+(AxDbFhA)rYsqu{UKMbUd%qNoPhQ<v(l_;?<a`#9Ip~pC@Oi{*Fnc<I<NRt|*7{2}lIbtIwhH*7l<F)(@ooCuHNio;!MQWkoF2r>+5cdTY*79actAor_*H(YpPVe@+PLjL)L);#fz#BZ%T(K1aNF=rgMS<j?nzXHhP=TDBbAD?WjnC(wO!wv-`%<>@PMC4D2}m5NKG^Qo0|zV$zeb(t=zTbb(~-H&M0Q+b=(hWfjAgL^DNr?76%Sj0Qi*AtIvuSK3Wx+s25UvO{us5;D7?gSUR!iaZ7y0Oo=qu|O+^)B+;;6}VSV{A*c^mt9G)0<r5{DhFbxAvM8Si3zX63XVYzkf;!C;i=1GWoxs5`QfR`JM!_4QD@){V=xi><^V!RO>@<R3QdyeW2F$T9;Y|w!PSwHi~@%`~BD|>~krEPRN1@5vp}r&H+4@egylH#qn7BF>GZ_LN^x5*2m+z>4oroF#Ek(FPQzl>`P{38^_$oqFGn&5zBrw>-qMNW<P}IjjR*Pegf~)hhqZR4`x4@_w3JBuCZk3{37*#`gQ$mPFc(zKeAs}_PnOuS7vHjKQ65$!(Zm2eI!4zMza?%`VP5`m#h'

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
