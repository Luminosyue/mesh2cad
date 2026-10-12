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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_004.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_004.stl', 'source_sha256': 'df25eb88f4842b48adc15e78a0e9e936e8dbf2a49eaf1f66a0c2c28b97484fec', 'input_faces': 68, 'input_vertices': 47, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14398103952407837, -0.49533572793006897, -0.04969162493944168], [-0.006783921271562576, -0.23823463916778564, 0.044194478541612625]]}
GEOMETRY_BASE85 = 'c$}qHTTEP46g@opfT0wa8DMIK3sabxGK?jn64TiG(Q3@3WQ<YMR$B-RLdtUnYX~X5#b|;AZSBixf?ktW5nDrR`em%6CJmYt(-=QYePB}>(m!Zu_-oJJca7em$HeGKcGkM<?6c3_=am}?XJxyD)ha~Ij?cEtXA41=CtTt{G}hnI5{-wtdj~Q^0qfLKc&zb-osnG`;(!?RwMOGDG2fG#Z);nFFR1z2dSd;t=I(txvDPT*Pd9hQqf(EzH}^*6x4-_0p!R4Ws2$Y)Ys-}>7|UJXeoeVFwp=4jmb9KAoUJ?m4eJ9#GlWK|rR((*mVTw*@_#4aRO)3-Z*rWgx03wb{t?H~-nIP2@m$vRrT5d~tkg}!G4{N7nd7zH<~Raz9?&(*-~4cdb**bMtuFD?>aV!}#dSXtHl^x1GkuZ$hexh++#9=DH@1(nZXEyO4<0{#^z=3w=l8Roy!k5o&%XSM75|Pa&EHravDP!!eIYGQY1K14-{rMathXQfjq^CzXvMkS^Evm=<^0b2#^nUfYfdemx5qIj%#T^0>0@2&9kue$Z#PI!F6LVPyREwPP~WGVcirGQ9-qqd`GE-@f251`CgdYJU)st2?)~TN_39`0OxSf3y79xp>zq$sc+y^%G4{zBj_bL^^K0{iTvt<K%USX_u5IFY$+3oCIevWnFn^z&Gwr$%cTJU^@}K>3@&i?T{pX=^RX)azw@=&SnAk_-yQdP$dZDkZS9^AALbYyUv@D@q=bU?|RQsYoS9eOakNVgnCsq5NY<TR1>YU6jEgV&yEB&p*qpEW#b_~CvI=4n*epq?V`wk7M?uB^m`@sk9Q6%k^{3ZOSK9wZ|S&n=q+nQ}pB#G2gsD2_l>i^Xf`FO+sej-=P9M(#sbaJH8n@QR#X=|XZflfSAS~mKrWk9Qt7L-;6BOU@)f``DXfu-Qp;7;H=a3{C}F<qFa0=xw10C&KjxKCP<v|3;uIN^HmTJX)leDKZSH9$8w;U@56X@%0fKtDM3m&1oJ03JYp4a{qs%ZpsRh*OLF3Cn<fa38P;MtlR%5AH`!8(@Vt|3a)mA!^8j6=Mwu3&7Wd=feuH2IZ*J19XGC;p4%cI#H7oalOz9L%;xd6|fu_053<p)VcCt&z;!sVweMSJJ4SM^nlZu*(j{@NT`7a!7G6egI9u=0v`g8gflW-S^xA)^mjApVx;{btsI&DOxQ<O%ggoGqY(+OqWdT>S*GZtjbq>Yj5+-A'

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
