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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_004.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_004.stl', 'source_sha256': '2c98d5cc68e0dd6c54d9456b0e563e47d5e2a6ca38c5d78192b276f793678a1d', 'input_faces': 28, 'input_vertices': 30, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.26654791831970215, -0.4670180678367615, 0.09260231256484985], [0.32928287982940674, -0.4110511243343353, 0.15533730387687683]]}
GEOMETRY_BASE85 = 'c$^FHW@Zs#fB;1Xn<jIo0A>aT5awYJVJJ&2D#=VvE!N8`sAOai0E>eFjGpWl>KhQr$WX>mt)7xvoLr=CrJ!z;W}&X5pq`drR8o|f7oT60k_r-cOUx-w1&SAEBo?Fs`5MLsIts>`ItsN4<N_{`8|3*f+5@Qr7y54R2l1Oc_JQ~gN0h+g2~W@60gLYn1B)}1sG_KM5VJoBR_|?rqP}6CA&PjzO21pk;s>N^A?D0~d>3rK><ozcdnTfqBfDxBSiE~bioFL4ejkFk=L}ff0p`wocTmI=p!UMV9Zp<Fv9}>(`fjlL<hDyF;zu{_1dH=-xrAb`_@l#Mb7pV9glzADv%65lVfMnr57cK}MhQ<5<{il5u<(J2H*n=$Mv0e`TegGwyLVkiwzpw_|6yctn7uG@hKhqI<{Ze~3K3r(dIcq%KkwU#EDnz^sCYw9(iLQL8pN9*>hmUCLAKYSBpnj|OXs7iw{HZCAGr4t)%=s9d%@z1|DdR6IP+@{*qpTgDC!y1CLRFue+XSg@t5_C1NH$Zxv}=(&kYwC85lsA6PO#*5|OeZNDu^IH1@2RX+l(1G_s&LD++<49+cdmG!K-`3uSXaX?7@^1IlKGVi21Nh*_XCCzNJ~vN@q_J}AutW%EJV!cbZS$`*#QC7`q<lq~^e%Rp&aC|d@~mV(mKP_`75Ee55<p=>cITL6kdY(Xe33S|pI+5FHbWdmYRbg@EdE-1|gWphE<+&~=Q&B!FejH_ryfCg~<BNx=@I#H7mvd%uBS@1*^;LQrM8yM(J423{?Cdicx0LxWe!2'

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
