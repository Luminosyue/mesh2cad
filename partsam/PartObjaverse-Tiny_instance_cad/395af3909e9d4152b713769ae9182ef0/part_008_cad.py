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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/395af3909e9d4152b713769ae9182ef0/part_008.stl', 'relative_path': '395af3909e9d4152b713769ae9182ef0/part_008.stl', 'source_sha256': 'fae0a97d8bdf6631035d984978b4c4378f362ea1b5fc749b79d1b3922c1bec39', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.05754731222987175, -0.07019370794296265, 0.20709121227264404], [0.13071388006210327, 0.03003743290901184, 0.2804275155067444]]}
GEOMETRY_BASE85 = 'c$}q`X-HI27>3U*W$v1jX;xl0rbt4tMcce76)`5$_9HMI(GexHyoym#-6GnEkTP0q8MQ1+Q`0Op@FJ0xX*)vwaDpHT`eA#C(LL||swoVj4qV>%Jbd>(-#v3UW3?EJCZ>%rHf6CT!OzGTf4rE972Bnv+)R7n)co}ub<7W(kMDXYW#tm<Djh3ko6TAF!c56LOEAyLjx$FK=InJ+k(802zD~-rbG|Smuh6dY!kmotc6B}}HZEF-og6J}5&m^}s4dv~ifa>8Rbo=B+qouQxWnh7l2pf4UTdu3+_v4l7kr;@Jy$mKQv>JD6{+`87Z41tlqMiY_AEe-^7+ZI^+MU22IPfRUgBJwSbY~cquapcs;+v@nf}y0%wt0@Bj-cYMbyUyq90q;a&W~bAN6wo4&*!Q_JWJPCCF#VHOOb3S1%8jZ!>r`qW=BTI`B7#k;6{3gUdagwb%z^HMkgc3)~TO6Zy)DPUMJHDNU$<k%oHq^{Li>$pdg_^GEbAcn^R(wiR5#e&n1!i~SkXtJRB5;9`M<{S-g-U|omK+KlfVdRxJ{LrO(GOREEyYadsF?-aHEz52mzHPSiccLizub@Wx_C>96uA3nnVh#`By<wODfh`Zis-#fch<BxO8u@BF*KAriV*U*>SqB89N{sH_hY{v$0ad7Y?_F>*?)C=)D!Dauv-KhJx{Wfx@b%5K7URAjEZ%a>YL7$e$V_0{3ANmyL&Tj=TOD+X(eW#tzpup?M9g05yO>XW+e@7F+#gRu2V*O=%u&z=W)sDKvTl-PB;5p8%?aWq<S8XbB&2hdARxlqNI*gnoLl1Hr<28P;{0Q{;4b+S8&V!3zN=|}%N1$Gw-KN!tcbq~WFCKI!Sbw=qvbRb}F?z=M<F4K&*%>ZZ35R@q*Ws^{+-ZMzmCX3>t0YS8AyR!JNW;lTkPjmj$a9@YK8$=Q={WMC<R_2@k)J?*Jn0zn<H-k;jwT;Wek`dUd9DHE$C3{r4J02z-bCt8-bCJ))Qh|?c^^_w@;>CfNk@_QChtLNB+pe(p6f{R9^~CgN04_X??$R4??&E0%E((SI=#v8r@yYBL&i(4e`LSE`Rg%teKSSP`f+HjmJz&P^<(s`K-Ct^z5&I@cRc'

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
