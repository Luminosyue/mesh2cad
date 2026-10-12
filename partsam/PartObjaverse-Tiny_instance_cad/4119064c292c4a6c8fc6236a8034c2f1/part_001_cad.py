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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_001.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_001.stl', 'source_sha256': '9795fd8187a388d7987e12897cdf4b66da3fa14a74b220d1e51b5bf1c4913138', 'input_faces': 32, 'input_vertices': 36, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06468062847852707, 0.3762228488922119, -0.07217992097139359], [0.04976075515151024, 0.4864616096019745, 0.08277438580989838]]}
GEOMETRY_BASE85 = 'c$}q`TS$~a6vs!`*3?Y1HS^kd!L{11c9Bs02notAo6$oL*{-=uhGp%Vl@)EEMFf%<fzahMN?BL2J49t4MMgwfFV#cYMnO@~<tZwPX8v=wwkU}D;Bfx)+cRg*oEc{A<)$bLQ(rdo?>WCcXktv-2xegoE>C^UYL|EN`VCtnSR%OmLcVSB@<sL)5v+l2vsSyjt3B2^+*<4|vf8-SUFWIyIM=VL^HjSepXaRgx&-&Gac*#laY5lM8!sGh<2(4jezCHYmn|o+$XYIBJS-K?alWEMj(wE_ebVd2>EOKN)Dby$Y|RJPnv=m<ng5s^bMs&?^2AsaxAp0WU$_`tx7R(E+<5&2@jADF2Nx6%Ngh1uJAwI|-Ug&M5*k%};63v2vz_2<r5o|OH{&??ozH&M^Qso{j;nK#pIyHM&T7gK@5@U<etvg5_Gehz5Ffl~Ifr`h%>j2DQC#cma)NhE1lNYLpI}^ZVL$TDEKq%VdKvj0b3Y!ye!9P?eNW0kJg;gzjdlHs>r?xO!nv<>cRTnJwJ!I43Sj+Z)!=+H)j4fl2mF-kW^lXWju-u>Ft5^RLY+qyH;T*$u<zJ=O_&#oueyPF?NNO*_M=n&yaE;9TicGfrHbpG+#c}u7VzK}%9D2x^=NOFsJik$sQ5EeRX^V;&L>bkA-<~xTtBShjW36`A?|G}xIy)>-h3DMxDFK`RQ=aH^U;64?>IPnuKI6O?M45!<U#6_>c6(O5`AVVinBu1{}9(7q;_I_zw8m#so9Bp#zzixVV_@<z%}dS9-M3DZE)jO1GpplSvStTq|uK)h4Nf$4P3GR^g2Y{oNZ%~LJEr!uY=ne_B7xJ#=iUCKMgfA{_bg*{@+i-2vNgGVe#Y>NRJhkDlCnBI_WH78N$YqNu5bPjdU8tXHrZi<xL<RPd=S=Jn1+xsgud1P9dL4I)(HYGN~=(V@X>`Cy_~=NIs5qBI!|NQjaE|Ogcy25n;LHvq?wLF`B}TQ|cID(ZYt4No^JuMSd9hXwvrbh)9d+Pk${xJ|7kg|D*YJ=FitId}fwd{QD)emk%?mf+N{R;a6bv4TFMkQ~'

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
