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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_003.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_003.stl', 'source_sha256': '9d12c3c5786ddc7e0217026c6b88c9b3c5db015544778ba65457d4983f7c7618', 'input_faces': 64, 'input_vertices': 51, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0752442479133606, 0.40006396174430847, 0.0007798261940479279], [-0.040717899799346924, 0.4211048185825348, 0.055894047021865845]]}
GEOMETRY_BASE85 = 'c$}q{X-HI26vy8<nmSH7>Qq)PQ)#0)S=wSm;e;fmBtr{iwm9gBMQ$^uSwt6#phYJLBD0A}8fZnU4;r*g3oU-@Ly=+72Ps>=R76-1-Q{nMae}A|hx5O`|9SVG_jvE}9L4%@v!=#WZR3oNQ_CYXO@vW1YfUb9<CY4SC%d-3MW>l07h@zJEm^zLQL59Lv|ZLpm#4yQU1YH?u3BidS*%rc?nbw>c5|J((j|DIbDPJ-xu@D$@8a`}`8hVr+)SHgx8+}lLG&=c;OZ@&{KGx{`C`7a!JAL;;H80p$ZXB$D}uiaoKW@O+PoBJH(ty7;G^}DvlmZPeV@LW;w<uLJ6T`d?<e`)o9AVIW0X92pjYwbQ=2Ky9-MBcxP8Z<pW?yX$8vqvbh}&byDH<ktjnuum3~>f<iUj|#orHYAo*~jm*Om@z(?|ToiwlM4p2N;>AfiL<CsVB?*_GR??Kh)=_1Kr-ubAW&)}wwB)66NNN&7F^Yl}4Usm7SC7;iRLbdO`)gF@H-+5f-kI9nzAL4lyHh3t`ULBG3EZu%l-q#+c>bsY$BzcdymEx>#=1G|^cV3V@x<b|aGfODW-r8lo*0tum;N=;6RsEo;jO4?eZ6ts9fnH}@kuQ`paC^=60LjlRQ_p!(&pG*guDH}X1N+NJ-V$u1IE#t$k^E3O$?dcD1;~2yI@M2ib3k(EC$;a{))gfG;yq0Aw|yNle|>gFzE@dK6+hlmMDo1rhe^J5s3YGo>J&awQQpY(d`lkD{1mQoh8)2HiZPPuBY4ZazdC{!%=_;nIE(i%lSdkl89Z#_(?ZUIj^{BE{zP~}NAie)9|KQl9S=QxJv^bu@G!tPz!Q1`JQK75^E9w@>^IU&Jaing3EG6~;*fRF@yL<LI_Nn(l6cI5PQ^S2EE{?b=DA?Ap>r^|fTcj^Vm^t-6!0nVgf{X>fS&+Q=tLfq;ZKHVL{F*kQ{g3|r=*acvax;&bTV=hbP}#hMm9pHAWuRzLR)!^)x;~Uv>EdZuxZd%%%}6n1kZ#gbS#hY@W;awTKt7X!;gk1v>0LV!{7-W&Lawb6g&+*nc<t^g`=mj=wW(DFR{?$csPo6VP^fGexZI1CSICRKUBY8Ir_5?y>dTa>*pchD2^DTZZJ%1;CZR6{Q<Zm^-B'

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
