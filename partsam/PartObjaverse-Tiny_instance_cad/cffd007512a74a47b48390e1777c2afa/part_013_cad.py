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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_013.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_013.stl', 'source_sha256': 'f84260b82431ee4a2d4dd0f0be2f578fe4ea29bff34dbc5296255d2986c46484', 'input_faces': 66, 'input_vertices': 45, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06143379211425781, 0.3313109278678894, 0.12899930775165558], [0.13164949417114258, 0.4619854688644409, 0.1843259036540985]]}
GEOMETRY_BASE85 = 'c$}q{T}YEr7{|}M`LQ-#eyo}wZLgYb%aKqjVTIo0g_7*13qjDS8w%oVGa(`pqUa)svM3>9(2W!nr58#c><vn~h%PewMlXacy6L8iDCm98`+r~ezMUZIz{CHy|DN-l=Nt}ai*(p?JWLx^?8Wp<d@hGEiUQ_g<FVw}P=747b7b_W#EQ62L)Xd9LkA;W5*ug70t2yBe=^W42lmDH1j2G4o=A=*qa!_u<Uox4w&-vwruwPD=x9v+9BgO|%ezBi`MCVA!%01~j@@n{{qpHOX}aKKrbXaqeqLVSpRcC5Kk@d=2U7XRxs1qXAJ1y}j^G`x^WCp`{jY6`$Y*7XPq;Qun*7XELJ|6-H_iEa|JHon*Yn%GcX^+6=XsyK-)9t&zp^%{<+~HJ+;{b9e)sYtk>7iI|6}fZ>gR>|7T?HUI(1LjkHt6oS##beZC&epWjY_LukRQBZ|7t6_59C0raJ81UPa`mhr5J6yQT>1Wa^hSe|AJ$_tNwd-|vk+MdYV@=d}E#XAgw;&EgyP&9?eLc%Lo4ai1?p54p;>_`0&bUyGm7_iN49_iOQ2^!*MkXzQPFnd@78qrNp?uW#{<`dy3MZ%sUZ$<M=kKoR-IIa_?=oLAp)KeMZW`zzPm6_G#DIH<HlOt0R>BU7O(cE%_+sIOi;n)T$7NkdohlQ-1xS5ID3(|<pCwQ3LBc-xxF;2mm&)Tn@#gR79U1-cnri|;~+D$FSdQ_gnOt%g>BNxk3z@@k;f;2Lll)C;b_8eT*>)}p@XS0xXc3(f=QL(9PV;8Lg;>_xp&1aV2$8YR#?aG@F-8U5U8LF`5l7a@p?p@raLunSrMc7dHxH`t9@P6Tl!v>03o-ijc$LtS7y*amfiotRJTV04++2eAa*1eU;ls0Zu^`=Ac61GRim32WKFcBntAPe1nI$2@&szO4QFvg+uy>2A{<4MIcUAh-@e99ARJA=y0kKmC<i9~0D|>5q+drujL@p7~9!Wjqd%j$FD!YST7$Sk<TebbbMqJgI{'

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
