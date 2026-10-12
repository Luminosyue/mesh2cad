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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_007.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_007.stl', 'source_sha256': 'a7466e8c058b096a87791470f2917521e6ac45211ae03c97a141c0168a470934', 'input_faces': 32, 'input_vertices': 41, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04808453097939491, 0.19624066352844238, -0.10064177215099335], [0.1263389140367508, 0.44661593437194824, 0.10172321647405624]]}
GEOMETRY_BASE85 = 'c$}q`{Yz6(7{|}vY`UeDOU*gEYHmgnmHrSCY^Dh@j1d$`VH<8EBh<DbrldD2=!Kxvl2l@7px7k+p=I@hs|ZRcNa#g0y!{;X@)y)O&waMey)1~j@bG<}&(3|$_nvciuE(v@TZnv>5M$2Qq9b}jSeS{0bOu6^)|Nncdt1jD4Os`AT}d4{aH!GKq#>Q8$KelzTSAT+!LcW}+fgYvg6*M5$k%qfJ>(BC-rzeG4p1IG;p+&{x}th#rBJoCQaCI8>y<?<2$%0n&NDA3i(fgJChU8edK=zMFrGMne}UDK?eh%iJ|&MfkIt~#HCflsR5T6BeO}6aNbRv3z`MqQC-TO|n2IhHA1W9FA43;K;0Hg+eHO4!(BBL5jC=<!8qSRX_ba(~xOo`-#SafSIX_Zv_PCSh*x%*0j)Fc^ju!?mfS(k{@sis(0{)OE*G;-hW*L|2$|jtgACe*a6zY{+x-I*Zin=EF{^X<lyy6Fa%*m~fkT0*Bq~cy&H}Ps$jQ3BLu}^RR11Gm%u3~u~y{p?2Q1?X^Vf?!<wLDMQuK<@ki!lZN_5`@F`gD%xQn&Rz^tskIosN4iWjzKz>i*a3WAi-6{@$P6b39M=fBhqtmZSe9CpA4wyw4QZO)v4!mE_{ov!!%>#O~Q;@RQLKSMVKmE5I}B@4^2-<tH)u{LwtelYWxV6;=Deb%?6wjoPc@3Xbze_s6FceU9E-N%{9EP9^C@Q#sMnltv~!m4ZI*NP-^-Noo2cskQpAj-;wx|9vFc*q+hYOe2rRCK~ye7ht`SMj;IwY7ypE%nLCu!#WS|DL}Ph&gLn_xmaF-^%fcq8s(VVxw-<!mLp?zG4?1yEybLjubDK~pz1NtVB1c^h-$#xOv6MY2XzDHMjT^CHDOM7kL1$GMqQ7&0k_kHx)yUbzXs>j;I`}VJ_~yExHVdf?oXez-<Jpt_z#@=PUUOI-+7DnO1*?0w}Gt(9i=6wslJ8k7eE?}q5'

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
