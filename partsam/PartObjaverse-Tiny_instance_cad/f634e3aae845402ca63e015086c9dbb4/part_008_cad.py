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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_008.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_008.stl', 'source_sha256': 'ae103b1e946dcfd0cdad480e9588020016683649a44c5c926a3d1209675824f2', 'input_faces': 40, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23746424913406372, -0.2004307210445404, -0.3155636191368103], [0.20508897304534912, -0.1902398020029068, -0.04750906303524971]]}
GEOMETRY_BASE85 = 'c$}q`Ye*DP6vyxGYHHf<s$05lyN#Bvud;_wiROGT!6aE&ibSE^bR<E1?1~{KO@v`VDA<SkB1>f23(>ZS3Y>2~f(VR06x0MoeTXP~ff#h}xo34}Fo?Qv`2YRQxp&T<d%feSHpSQoADN_mDV!9FA%sN|v5_t*(AnG|1-G@fcN>TmI2#cisyTGfQ)?hyq{rPT1sekH62V>Cw8vd2xSQGnodJLA(Y8RN#CWB@B`8rIJnnCo=-;`;#f8GIyh5Q@_}8(PmLQi%Po}8)iiT#Hl1rE8nJRm=To@e=13!5Tc&MruxGykqovHk?3OJbw&Olz}h52YMOxFS@ZD)atx_sfi`Drwd<ohh~z?B!AhnfR?o&NN2G+)ji|9J=AtIrSJ9gF6XeDzb1^SZtV<xyNd^_<tA-mm39c0)a~UCTqaCLe<8xIDq@QFUDS%HOMg9s?e!Q*C?=?-drbT<n{N^+g>Q&htLV`uwZ>_xeuMJYw8eb_MoJj8Az6e8H>X>gg$1M;Jd0T+ABg=i#F12I#xwS<UZ~K0=+OB2~l1+q@5YE==-1i2D3**#9{<a51ri@7LmYeoh{9zTBTkA9P%a^g+jcBfJl!Vk>a<Og-lZKJas{<HEVOP$${1<spX`)=|vmnmU!DFT75RmaFv&)G6z@Fk%d^#%1pSuk%gG9OLqlYtVmX$4=NUvAh(x5*P$7tJ$0nmjM@T1AKoM2l@IsuKv0S|EJ2*KF#{1$Ikb+PUP#~8|Cl4KOLU(Xl}Qv7H^-=NLxoEf!=OS{-~>sK{g_~`qkE4{C8K|_W!=xHq#n5(nv>5M$dE|`gj^<8gZy8=;P2EFqmIYV+)O38cx&#^ac3biJF35z&UnQCweF5*ip^s*?nvwthroM(I=ocVlcmfMmCK+8ZOj)^!fPQg_?>!6X#^0y3o5YCj-@jo_(bfX_zpWx1zU_mBBnaCRsGxG#sco=yUM71J#Ot6V6FPb)a`(P8w<=`Za`oRtbrv;i)zlZKgkcdRK<bHc;~+*3Z-)>*$%U=vvE%+*2LP-cL8cNIIx?vr|HT16ozlF#'

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
