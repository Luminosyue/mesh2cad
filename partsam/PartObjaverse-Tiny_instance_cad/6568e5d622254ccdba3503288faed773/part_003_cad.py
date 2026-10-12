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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6568e5d622254ccdba3503288faed773/part_003.stl', 'relative_path': '6568e5d622254ccdba3503288faed773/part_003.stl', 'source_sha256': 'ca9cc33012a3e0f20c3879a69472f0aa3decb59a71c58288c02678a603b334aa', 'input_faces': 36, 'input_vertices': 28, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18008020520210266, -0.23282602429389954, 0.10261636227369308], [-0.17008808255195618, 0.03153866529464722, 0.2841583788394928]]}
GEOMETRY_BASE85 = 'c$}q_Ye*DP6vyvAG*{Q!%(oO{Xq#j&Ez`($1IrJKwH6gYl#4rCM){bPjSy?8poc_R1VUPqVQNMTQISG8<~y~Ag!IYX9-opvr4&ijoO6$*Q4n?E@c++m?mhS1!`!jkboxlfM<VmTiM=f77=tjfNahix@}fe~y{x$Oh=!Sv!<f=bo44oLcWIc1RhXTkyHGN(70l~gndVf%>?)DUB}ehz63Hn7-{d&x7FF)v?<f`3=f!E6sX}^6s!%EX>j+g#u#Osg+o6`#9|u4Krj2bDRpl!aJ@9P(kbx@aUVH@H`pu8e1&Q|+P^C9t!TAdY`MjvR50Jla>p))9ikvl^ZNhwq!#a^4YT?}f#f#i;>_Xnz#Q8|FjL*5*$OHEpkp~(qLpZ<Ej@(;X!|Qz2jOQrui`_VX;xw<bdEsMxA9t(=xU#bXxp#hcEADgB(~JA0l<+*xXSZ>mr`!54&sG<&r}2Chs%sp%;uJYwl5`E%=LPj+f9lupJnM(BPQ{lqi1Q26kSpf0K3w<d2J%3~Ql97dYphd_{fb<6q#zf%cC_L9>$yV~>{l|+(|Ya>o@3uB<N;q2&m$#V#X81nkqZsPck3_UxqNlVmHc<z$PWzEVINn<yukUBZ#nn)&S3v?;*ne9N0D1kOx{9m*@B$C96_$s=Rd^!?bXQT>gRm^hOrLJSNjCH^0^<mu&ADYcU8f|m|yDV`yS20zR5S24_oXrZdaBqdVGbJF$jZtyIhWGR|_DFDgFJ`Dq8hdS1Uc^zpqw^TEiR$g>p5KH;@k{ol71xf_y0XFbeQS3h>a9Xwn$c2=Wn>D~1AmECu*DQWJR-)fYzrKAr-60tNWl6yRr(hLC5Z8qyH*8uD6F19=0TQ%eC}M*&_>8b)4EK8VyvKA1F|)JWb)eF>)kKaT=@)U-Z=x7#$@NZp@)<v)iP4m9J({_Dz_pXv0Kd(>P%K3cmi2x?akuVrPb_CxjTJ2jO=GX'

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
