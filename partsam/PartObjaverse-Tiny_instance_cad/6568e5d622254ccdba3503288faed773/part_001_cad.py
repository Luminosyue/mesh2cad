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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6568e5d622254ccdba3503288faed773/part_001.stl', 'relative_path': '6568e5d622254ccdba3503288faed773/part_001.stl', 'source_sha256': '0a14f40d647046ecd576f158f6ccba729c6852a00811ec5306de2b64941bf8c4', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18427865207195282, -0.31295502185821533, 0.02633681893348694], [-0.16655173897743225, 0.07179105281829834, 0.348408579826355]]}
GEOMETRY_BASE85 = 'c$}q`d2CEk6vpq&bkTNHRT<i9U$xCxsx&RCQ5{8zE~XJnk(i-VN)^*0)=Y?hB#0#<blMlx5{WL>61*yEYod#Wf7&UHs3o>YEU~=%-D9bc2sb(TzWbYV&pq$X%YEilom&7CBaEdazu)NR#uyJh3t%g3_QKqGwu0#VrK>c|51fy0x-(;Hx;ab3R<Je3Y+J!RyD>pBj>?HQMoGq;CH6wQHGj?$d$x`96l-3AP2~j(tV?a`ynk$bloUH4N?IrV>+n`vuq@kMdr4JCp=T3U=KXGO5}$`}0hgWA?|{chGUu!*51h@Mbrb8d(vEVjWK9-4ZPyj9mPvQZId>(-fh#!^FN*x*CpotiOJd)SkD~tkm1n>|2ZFm^HJ(77n`6&%Zfens`orGb!tZ|L&msSwR@Ct?JAi&uD$a8*?|XZV&rQ#VL*)rOE`UeB#+*H}RHE-{--}$ORnG*Mw%VZaE#R((CxQ>0DW2aLcnSS{X$7~0ol@|8wV4X)hujwX^{hM%{^VRW_?{|Jr*!iX^tIBb2Isu3LiBlXMm>IC?gW=#90ONEr-?of>8^k;7M!(ya9~}lUhtYDf;UH^PkBNjxa;I$a93$k9rD+i!P$oSqW;4))VDlnxsH9ZZKBSgh!WIEcfW!Bxd|e_Y9ab`UGTq+bJ#yZ^gp@|^_8-5;I6U=QO6!sjJ&5sbvWlz!Ii$rl_Jjxu4J}fMgGEDPMk}Op&t7`ZUa}^;*l>K27{aIS4IB%k=R#0G^7D_A}@>lL1V;u7N>*DpJb7Le+%lH8df*rx$l=y9qU@Gi`fM3+T;Xx1Vv+CHf1lk<JD}DpHN<eybtYnQUA;=!Q(pcezMS);EvhTML$!+QO8taXohaj6!}dZc>f(!(wdXZoo<tR;}^9J)iTDzOTA5UtUp~P9P;r^e}9$a#{Jz@GW@@<l1R0Oa5X|m`;zC{n|ug)18D$x19?9R?%hc}$um+7sV8|2c`XI^I#Mt4T)UFjk$0ou-h<SaJlAgIJ;-+<^(WtjyblHUdeR=`_2j)NxbIHdi+p$TJt?>kB<(|<YY_QB^1-B`<b%nFQE(qY!F@kciM%;gqYcpg>C^RNIQRi~`jGv)vh!>D^U4gh*7ujzoa)ZcQvH*(Y?-Q6n0*D9n~<~'

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
