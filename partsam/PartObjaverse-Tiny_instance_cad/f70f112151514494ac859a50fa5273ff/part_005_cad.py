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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f70f112151514494ac859a50fa5273ff/part_005.stl', 'relative_path': 'f70f112151514494ac859a50fa5273ff/part_005.stl', 'source_sha256': 'ffda9123959fbfc1c31b57a01c9d6f4fc313dfe3b50a02ce4a64e5d6741d254b', 'input_faces': 22, 'input_vertices': 28, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3473949432373047, 0.31298667192459106, -0.03716743364930153], [0.3899323344230652, 0.4081656336784363, 0.0597180500626564]]}
GEOMETRY_BASE85 = 'c$}q_T}TvB6vywnyKcK`nr>+pG(E&7EtX~=t<pkhg{7;pg<$2b&XQ%i&5D#F%|nrWyo4earMrG+Ne|J7J(L?*QIJ$>Srn-cQPBs8NI?(Xd(N@eD2Tdn_@DXB|DJp1&fIb2Xmw_WV<|gXTTvrv850r7%&b~gs>(`aUvh=_poYZ&7h^^na-CZog&J1PYAvO*uSBt|l`I*abc<E8cq)}D#Z|GZQYn=M&vupjWX^rNU0#`AFHcRkN~@EsQl0d#!z6m>vproWw6kSIsH!{)^m7gN6d_NW9u*pF&-BCnZEoQ94JV!pmE1}j+;{E;9&|5x0etdI2l!0^;HvZy>Pu%0?V>&_xQ}%PUJt{(^2SzJ_sJ;wdnbU~n?}w-A0L)I6Y8JNgMR!G`YzyotAML@o6&!BunFosumP7&<zju~+eXkkn~>iPLLIg;vIph|3b2kY1^Q&`$Nf;Jxd{EQqM?rT@IXEAEI0bU!~kd0M-RjLL&)tn)<7M9{a`Cx=gY{y8o*yHUC4tvmn(q>4Jo*vhgdK8u8ja6yV`>OOiwfH+xBtvuV@24HkH)`>%WV_=b3b2pUoM^g<pLchx>J_1ot6n_z3t$6M)<A6$1BP59EWt$O>Fdap5`>-@3uS)r-95JoeR5a1r>PZme&6jQc<E=``?tSAdVb`HauKqu~<pq4(&QRa`f@_!z9yHHGzWd$CTq&Drmmb-ETiH)hvs7!zUSr_19CIa&gWF{8gfT4iZ}ceGOf`)G+a#Q8GtSU?(2YN9-z@`V&4kKv&u4I?#CE>uJLTpr;(Vo8mZCy*wRnki4Dd=cq<%42D+V9~^*NX?X+$uq-+FOD>l@_9Vw@Q9$-rQ@OJ;mFa1nYDlVMgANrytmLF=C3nnzy8pfJ9(`iAA=)DFZP3PQW)DWCW<cDcXvuH1^'

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
