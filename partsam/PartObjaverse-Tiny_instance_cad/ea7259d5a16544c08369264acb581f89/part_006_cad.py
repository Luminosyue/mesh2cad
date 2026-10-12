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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_006.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_006.stl', 'source_sha256': '3b44b52629246c33cf3be8ac45bf3c27158a38692078958cfac6e9b26e127426', 'input_faces': 38, 'input_vertices': 41, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10085277259349823, -0.2025938332080841, -0.011625327169895172], [-0.03768182545900345, -0.17375358939170837, 0.06643998622894287]]}
GEOMETRY_BASE85 = 'c$}q`4@lH!7{}i`J@fBsWo@pspOv1`QD|=1w&u@KBAl}uVQWQn*L9YWWoOGtO@A1h3~I0<Ys=b&Cayo5rnPcRe{G~Ckwhc}A{T{4l8m4zH@3a+_jzueV}r5%;Nkl`AD;L5J@4~-?>(0@A~I3XlPdh#x4bJOg-{kR62%Ume|xFdS22G}d6h*>0#{E+_ZJnv<9gpBc8Hz!^}Y(P-~PI0f3qaV?$GQdTm9Spo-J#)`q%pu&-ZMu@JU{=(Npe|aYlBgLt8l4p?#$N*C$rCVD7qpp<DHm;JysC_17s4W`BBKseWkmic<4~vie-9?qz}Rz?U}lBEP-2T5+>*54id2_o!o3<<x+mFFFTaw;Xkh)3pJ`jXPs!!QYBQe!!b|P;qVDE#i4^AYcD|_$cc5Zi0*aO?a>VRU7&d1O4E7oQXPG>Jf0Ws<s391%t$U3Yzd<Jquhf?4<pEbG%V;{kM6Pzb}#c?`}8-zB>in91eoJ7d%G);{KC%@L!72k2|0t-+k>K@n_x04`xk9eKV%v4C?>v2RFr7v*LkO`NZ$nP(OWdgNvpg+mP3M8(c5bTfn={fQzm<G`HYAaI>MB@{`KYkGW(gxDg)@ZY*}v96FDlR6Lko--^5*2l45Pz>PpDxc)Sq<~%sIA9KjeBR(UC=eFkr_=Y6nzedt|IMuNa-|@kbZxNq}rGC!t{T%OY961fX=xz`CvTgbj`|?DA>wzD@^>^2Nf&8rUQ&|7uF`Aq8YAg0@T@7v=>ZAO-qjY|T-UHWN7MlOZHI#p&i0brTq<z_LfEy#TDgTp9+ShB=Hsoh@oCKfu82N^GGu7$b1#S#IqB_A;s#7xjHP(+FpnldZr}J=ltOdNXlK4*#>HM_1z>TZ5;9^A{aYuR+xF`fS+uLy-^yuA<-~+kfZp&WgPH^+H#Wc^2Pmkxi#@$L?msV63SmiH4T8zAvN<3j#l7je|u>Sp(RGR&-uB3%I|NBZxl|7_LQ|-SXZIZND)`?;MOB^em8s^X9cow!!eiYZTu*R})VLy^JhJBl~IBC(W@nQaCj+MR`=4%`)ox%PDX$f2}f!BxpDI8DX^&x*I$1}N>@~vD;u-e4)NBI$~(d@r0ZMw8+tgnRmb2wHyJIuFptTdhdBx%W9FPYbe{4|c!czwvv;MnD~SQ8`u>96tmW2lcX?vL`XE5{$-@Rjwl)}M#j<+Q2qEQe(k+f?(I*dO=ut%C'

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
