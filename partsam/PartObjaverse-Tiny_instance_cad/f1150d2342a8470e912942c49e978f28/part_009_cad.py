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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_009.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_009.stl', 'source_sha256': '90cba3abdc4552842b1e2bbd07988f8bdb7a7384b8f7f46d043331115b1d3412', 'input_faces': 26, 'input_vertices': 45, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4831106960773468, -0.49210217595100403, -0.4542471170425415], [0.41818687319755554, 0.2864585220813751, 0.3277859687805176]]}
GEOMETRY_BASE85 = 'c$}q`O=uHA6vrnY)wX`5rm0qq&DL7C)mTNVs3_?{gc8&x8c`HX+HA0*ZQYcBin@6477F!bK#T_w#DlgTdh3?rL2awXDx_k~RrDgL2T#74d0ThK6+|ced2fEad3pP0XI6=NyaB>TBN@pK<VL-OP%S0_l2x^Vo^CbM*4ux<MQRwQ!?ZUJ#t$gRT_j5`$tg9{t;xG3c~5$$9G2vCpEjT+dr$RgDV6g5$+H<1c;<AnUxj%~`}VN3tu-uNmi~2ALkUvnr@1j|k6fK)Ha<5wX5q$R&Pmia<ircHk$Vvf*OBYeiK3O0^z<_pFXY!%&N~j-^P5~(?D>rp#$$d%`TCyD6K0(&W3R2;j5q2zCujEY=e+MOu{>RV7H4wf?q^n?j$BXOnsUl-axuTr*87C5i{$2P^&s!~GR6CV@rhXAfm6K6#dy6^&a-%b_#u0qi_xNu*CN+`%-Hx$=Of4XH^{~KbD?3@_u)D_-?Vpx&I`M?@Os`|zZP-o5Axso@BKCyaq2&EvHy}sdduSTS3a=$i@~Q>PNeAxw*IBSPX=$Z`~ok;<NUpR#kqcGyhP{an>>GFb5|~6;d+SYFErY@(ZIQ$REkzkj`9C31nu!8hV=;XWvs{W+2f_7oR<?kz9T<ba_Y0m#XgsZCT1BI&Z)`8b2`t3b2p#IdhQh4t@rqOscO^(w;HGlZoPEUdgZxzm}#A_yq@;Iy7IQ}`0p!Ef*OLXY_2BIS`_uyf!3pKM%#pbGx{ME^&8MOqThi28ni+5mx5|QKD5iwUkzFXT7<S5{d$m0w;62<`fiX1v;gfw^y#22_M)voe*>r$6h^xd{YpYVQFOz&U4lN{RzGM3s1{TQS`Jd8E_cB5r%&Clp|gFqe)z<d_SeO_@;l_3e|eN>1$!<x{LX{@$YwtQsbs)~'

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
