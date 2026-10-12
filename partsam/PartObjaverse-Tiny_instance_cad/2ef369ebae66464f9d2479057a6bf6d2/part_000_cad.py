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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2ef369ebae66464f9d2479057a6bf6d2/part_000.stl', 'relative_path': '2ef369ebae66464f9d2479057a6bf6d2/part_000.stl', 'source_sha256': '886f323505ed3c38bae845bd9e92f39d4c25a0b456fef2b4c9575431a6c624d7', 'input_faces': 54, 'input_vertices': 40, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06493720412254333, -0.47120293974876404, -0.2942639887332916], [0.1695462167263031, -0.3776768445968628, -0.22207432985305786]]}
GEOMETRY_BASE85 = 'c$}q`T}YEr7{|{xKc_Cu`91Abv#AXenjj`PgbEUE7Y5Z$8@iz&erzH{6z^5HMcs6lL3PtbrrrdBhDu%N%t2^KP3tzKZluf3v;ODpIbslX;Lr2hkF)bW=iU3B1$!JBZt-i>iYI5fb^;kfQ1XRaOhsao!vm3c%jo!Zn<z|s8miv!yVM)JViQy1hIcR$ABcH73~y(&-Rm>F(XrTMEIfK`EH)S+e=a-{k4PUM3XezR=SF|4&p6%WGj1CHI-Ifv^X0>tE?E~HUp_9#8VYT0EHE!}Cbqa2fwM38{J^`5$-{i;ZcBoDwa&r$*7|Dxn~}6PQ=RE`cFuoZ<v!pm`@p^VpnjHLchPxajeE7e<(CTQwEo}TPI7PcseH06?L)1NpXjsEy}QA^xqWg=^Ov`^`J%r&!M&Pq`ILR0_haVmuX3;Yv3#?8p5GsHZ$$Iz{wN=~y0^sFpKgDj<X)|>yr{7+^ZrA#r!=qnxBPCuHsAE865Ol#%A1demU%zo>%BGZRX@rL*Z4BuuUOC3yxOnwfsT~E{^qkJ_tyH#H}|e+&qKLA!M*i7z?;!NZN9PJp5$K5w|vthZN7N*J;A-z5B%cH+zQ|C^z)}{+^hYjeNa1ne%$#snd6Wv%H+z^CmLo)56Sf9P!B(PhW&qa^tAc^`{*f<JsgoKLx?L7;v$4N7a`6>h;66^U>i6CA<jdHOHj+eCE#NSaXmuZfLZ}=0M{bKRj5VaVws~d)d;Z%AudFSa}eSz)M9WJI2(J<#x=6x)%_`E*R2LufmNTxUQ`d*3qC>5DrzOF2kb$w#Q8F%GA`6|unSy?lw&;ud>kRJLoEf@fol+AH$v=0%?CTdc7#|BVh5@V>;S9#?81Ir=#@CwW3#&*fBFmmJxqGIv_JHN-_&0}{>@u*E$d|r_GHp;D>q;l6SBUhUsU`AV=tZ`'

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
