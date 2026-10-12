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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_000.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_000.stl', 'source_sha256': '32a4b13a88a3fb60d66065fa5e235d491b8330cf82695162ed130a216a7ed6d9', 'input_faces': 116, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.36556383967399597, 0.03689754009246826, -0.0487360879778862], [0.44773054122924805, 0.13910993933677673, 0.053476300090551376]]}
GEOMETRY_BASE85 = 'c$}q|U1(cX0LM?-q#tR!);9hAy6abxHci*1O=qpEFUnYPgbhK3p)pH!BHK)6hsaz&hxni<g@F&1x!QG8_AnnDI@rxXR);tc9|ZLwh%XAV!4T$)c+d5BliZUdh~9Ac{qpDJ<nV9rJtVPI?G1>(ukFI0{A@K>BZM4{A|O`Mnd663>1_1Kv6nrf#m?pBaCP5fk0ze*h!ycl@K8FN$^_?);KK5*V8jS6AI%)kB#%6GG;=5|^GA{|WYbojeJ*({ZM_f0XCg){95GHB|Ml`)TPUQ{-!00${PFd9$-?|da<M#5ow^{Ie}3yNQ<EECL{?q%r}kg6^V<j3OieCM-8x%7KR5dDCw6}3<hrTJbN%NwT=Uo7_|#ti&*+A!$@8ZVY`W%Oy7{?wee#O+ucoi*_V48C{`2oVo7eT@<Z3_pU%$<l_bm3@`M$h=@mnh8%IW!`SLf{Y)!aC^vg(>o&xLypYo;d8E!{m^KEK%W&BxbGUEXzL!!_UOdD_2WYVtzv#HMS$)3dt1ldJ2~v$}sLSNHGqtoBpvU+Kr`-|6}3?7<)G_X|It)8?=J^r6l0d+(aMd@Fm#HQ)R8NA~xI_I_aM@)K9q%jf65I(^yR|Ha?Wo0{CX_sm7te5e20cQ2Tlys$g@v1@+qn^(2#lUJ<&&6cU#e=%3~pZ{{-bzMKjT<ItO<gM$j|MT}Zf7JC~%$5Eta@H^AO8*r(`*(7+e>HddDdtN5YVP!3%$5GtykdQ&|B77MzuJFAuJq&TKjAvPUW&gycE=}#9QD@ewVW(Fx@0IXhx()I@XWtDx~8Y&|MTqf&slqjTVoc^;InuP?!;sGG(-9hYcyM<$r{@j(i>p|E?JK^;(mtoI#`QK`tUluh9TVxt8qyW?!~JZ9{xNr_Pw1U-GDoA10RAr@gaN!&fp{X7>wg%cnI#oL-;tH$H(yqT)-oE6z;~O_!L~kr|?PmAU=stzz6UNJPhy0!*~$R;X!;9&f=r^FpS|bx*ldozmFlk1sZq@-U^5CRy+Vl@BrQc$M6ok3x@D6ya$fsJ$N6C;C=W2jN$|MAe_Pn@qRdo_v5{A0`JAUVHoemJ7Ey-#M|L0-j27yVSJdb+n@*c@Ls?cQM#m8!B$bakEDBHK$Pw^={2xJl<rgMb+Aj6?q%tI*dt2M0qKpfPn4b&(zn3@QF_iuZ-#?-Gu{OI@g}?h_TmkAJ?zHo@mko4*Wy0dj{ERx*oHe@OHV9$ssh#j^i!vF<?IJm`41oUlkQ`t{FB$LwTg#MV##O!N~*G6FIxP?{+7Q0LXlRw'

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
