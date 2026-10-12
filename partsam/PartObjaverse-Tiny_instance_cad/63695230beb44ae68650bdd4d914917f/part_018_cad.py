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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_018.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_018.stl', 'source_sha256': 'd46d921b6aff7067d98e65a5bae32bb979958932c87a35611fd04126a3a2f555', 'input_faces': 24, 'input_vertices': 24, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10084982216358185, 0.22999727725982666, -0.23678602278232574], [-0.016624096781015396, 0.4143369793891907, -0.08677123486995697]]}
GEOMETRY_BASE85 = 'c$~ddTS!z<6g{J(mQIe3QS-~&hm1p0^bpZdoPPQltugc?q?$p;94fUL69y}95g~y@)~_L^g(V{NQkwD>q4v<Sva+JApa+D6q!vVU_L^;tQ9pfjV6)a<?6dB^=WLF{9<Dcu;94RASByDYm=F{OVG?z2Z>^`y?OR?|<JXBe=(OhW*!q$}$0nVq6ZPhDx3A1=UZa?EE3(a2#avPCt@XO9wpM$~-K4K`?eMv!?yGdwxMiNPD$}a0wpf+D%D=8?*@DeJ+SgCLG}R2}OHgzhMkrVFnxU)K#>ddx%WohrI^IiYi%NY$x~=2&b>vqIplk1zK^G@xu2DYGIC}~E79WDHP3E9ptIvn71*V{@ADdAxUc9}C`pqlH;XmT(hyS*A=-SSVQPL-Ld3TV%{ColXCYyux1`F!dY5jTNOyN`X<8Q(LD8}dKpdabEOL}Y3SNMqT%g}8psqj|<(a_c6ebBY3!w=AB+KOA0J9lRX>l+TjUptwF{*(ew5B4>r--l1>E7VW;P2JG5ddJXzQ}F<NJBH7~XXDg8(w&2Cx6#k1gih#V)9}#@T{q#gW&AYs#K?!JKeK%Z^<Unc0uHPV`j@rBUoFY&fWGG&?ok}rkMkEpX>IUH?}WbyRKnls?`y%nS<55*ujv`?-S$4>DA4W1ch%CY!G6cQ>Hm=1wX{_yk5tA&IsFx`kkKcR)*SwM^gWsXYxHAf5AiY*WF#^sa}ZDAAfCh+&zvxpc@pzD4&u>_G0X*H6k`nY7_N)rAZ}nxU~XV;4C&R#n9Q8e#GH<oUKhQL2*w41E+mMHIEY6w>X}C}50~Mv>%vUoe|y?~Efx0}`q2HpbN*O_?))yjeh!Jl9zoxi&4-Cy633|%@dLw-C#w'

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
