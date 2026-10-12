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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_003.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_003.stl', 'source_sha256': 'b2b2da452a2329daa4822b35ecf848c6c1d0c6ce22fd18e65456a5de8376ee30', 'input_faces': 29, 'input_vertices': 31, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1566518098115921, -0.20369955897331238, 0.15788444876670837], [-0.1564525067806244, -0.20274993777275085, 0.1587013304233551]]}
GEOMETRY_BASE85 = 'c$}q_T}V@59LC?Xxw*}$+ghfnaf)bK7MOjQnU21UmNkejx~UD_(6G%m6Dovrp9JAWSHb%3Hnf{4JQv>7t$k2L90(#t&_%6Jwa$5;$C^<P^}^wK_T#_j{l9<Cd!iA0Nl;)d7k3Aa1p4ekSdUi(#c(1s)ZdfHu1gJ`QiM-(Yt8G}{zKi-!-^OdXF|P+Y)>ZCriR*+t)V70luT!aGV#>Wbf!09@!j!(Y{KN(zW89m{N2#f+@!WNHmM`(zb=p2LT+{W)TGsm@$J6UiT0^ZQ?zPuqjgqtBh@CkaDs=YY!77pfllzpUgSLbBJ1@Ft&+#CfybsDvR>=lE_pZ&uHE@0>vIj8CD&)lBv%!;tdC`Pf#<>X!UyE9-2~oEK3b4Gd}AZ_Z3K^<7cxg($v*4Bja%qnErfAiKXWe4;k-Aup-%^My1eM;#U9CxS02n^wgl&L?*M-Yt`%l5&k@WscNN??`yTzDW1pv4pDo2a<2bK6&qu$?dUbp&&Z~fn<CwG20UmqlM*nZ#Nv`FQAASO^+B`B}f7=B<$@;NM?3>z$`HX;zi=SmqY!&ydV*PFAPhkFH&c%AnN4>Ha{XYZORv<_3M~-L)*QW#6*B3?o8uE{LA9NSyX1p#%eh2$J*^T~>f#;a7&7xkv>_q)jzpM`*H1neiZs}Nl=lF9)2<vg1w=@|qx}p}e*1Z1yiuP~#t1G&G%YR?ddb5Wm=2J^uL|;o^L#?E*p|7I4=&R@h)KdBYy`So!_tRHU?erD&WmJW}jNVNZ^lo|&)kg23FQ=B!m(%;GPI@1Gkm{um(pOU#(^u2iQJ2!!(JwQfXhg9E?SJ}w|6H0pQ1Qq7*MBa2rHcP~-OT#&f<+?^Cx&1XCrrI(O;&sduP9Qd'

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
