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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_005.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_005.stl', 'source_sha256': '727920380289b4b5dfec9c87cedad35ab330dc816984bfd7ca90c377d7f1225c', 'input_faces': 34, 'input_vertices': 41, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1204100102186203, -0.14077875018119812, -0.14829370379447937], [0.1797398030757904, -0.10311777144670486, -0.09702110290527344]]}
GEOMETRY_BASE85 = 'c$}qGZAep57(Uzlnprkonp4}=Y*UcvL;E7!tk6obQ3OSlTQ+Us=cav$aQl%^{~`*akF6}r%A%-IS?$cF(NBx|6NP{KA!7KagzB94ysLAgAnL%&^PK0t=Y5}Z?&VxpjUmBI#3&#ecL$$tPauRx8ZnatUVn$L-Wyoh(so!!W`oX098cA5+vM7zBL_&AeXloA@3*f~?5i7A*h>|AL#w~T?`f%P_3!m^y~@)R@G?EH&(r2*^Ww6_rOMKhQl(q@*OAIB&_%DGIk=b4-lq`;>i(WVj?N`BB3xI$41?}$yz!VLEuR40J=qO;q}?W-pR-a;zGvAZ!1FsnS0+BfdbKSJo|6m5sN9#h-#!Gq7zLe<ABTKrYxoIAcQ8K+b;iBIM^gsqW5Jc6lc^GzQ}-<BtAut%HFbPzz;7tj9F_g6doDsg4IKsDncNtK{6k-#0baTw>ZhCqopcro{qlQJC#4^BwS9}&N3UrJ&cP6%;M=hokoGPg($s0aE&N{T1l_GKfjq@gE%0h^NcKaUYaw6hdnf7`K1HB!MK<J*^%-JtK1o*LzqtbP)obOTQ~fK*Cr3^QyuMZF2`^#2+R_90q3fM7xjs4g81_s0kHzGDscjaq-~N*^**^_@0A0B;8k5f_wAKfx+{}Cqx^Y~b+nOAWu9A%rS$E#51DzTZhoE2OAl2yKaw4)G8W_;lchm{Lw<n&<e%ux58a;kKaou?*cNp}fO5vj`9Fg@gy?C#2UA_BgSgubuOoQLhz3E}u4_!YX_Hn;@MBbOPdNZK%;Pi-`PpT$G|L~g;&G)vhSJVsZUdTS_+U97)rMZ=CqrR!RdO~;@*{#&zk**{z@)5`1UrD~Qzq*o^mi_mYl*T+*Sj<GsL(Xr^*(~&kvyd0Cu(Bvdv?Dj+JQJ}1xsgQ{i)2JIa-K5}*K@QX&t_4`&j(RKp2A`di&VsH<nz$84RHZ--Y1_$24XI91B-MPiHIiTdAR=th(*X}u*f0&_ae}OoZvGZVj6M_<`p5%N1l#eO^8<H$>=o+F$1})MyEF${`9N+IaJ<M^W*z<rS@}_SDs<Detev+nnd20y<|OUXZR6j-vOMnq+S'

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
