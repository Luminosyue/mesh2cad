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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_000.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_000.stl', 'source_sha256': '25ca248648410adde8d40bf5f7710062d4836ad473d28000aa38471373fb7f45', 'input_faces': 74, 'input_vertices': 52, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.19444438815116882, -0.4999999403953552, -0.2916664183139801], [0.36111611127853394, -0.2139057219028473, 0.2916664481163025]]}
GEOMETRY_BASE85 = 'c$}qHOHWfl7@f92Dep(|0fk;F^cE<HfB}q2n`lh5NV<@PD`}ua62qe<M1v$<s5@3}jo?yTyKvRA5QtBziN-euSN;Nb_|5H^GIx4Sj860AoSuI3-EU@2rZ*aK6uDV$w6X`0x3lBLjPa;oZnhXtEKE<tlRYzYH*BoN(D@K}cXaGx^s<dDvL$^oo}5VNr!@Wa)Q}$3^r_jzLLxSEWi~Mx=lZ$WwPc+1<ki?*oW2K6_64>6j-a-z{p%>B7BVY)+aZqo``^;Mr;bO@(vlvAo+3RY>o+}?`I#k;W&ZB)@>fHTt?tPAZ123GuMM%RoUdIkH}u`rZgc*~hcEnlcw}Wq&d>Z@|7g^Cxc(+>p^y8wvZgxF!=#5S^bFOJ_0;Y4cSiq{W2QPn*S^o2`rN&h(;4X@3w@31nEHR5>pL|#{3>msXL=JaOy>eUOnS&lr#hzkS<h>upN0J`Ssx$GJ&*Z*Y@7BW5_oCopEoy5&%Kb-!=E-cO!;SH&n@%MKo|LUJnt?22ED*<LRbAJ>ZpE$Uf?(A1%88G;5U)4`b|7n^_!yS{U++DepB?k-=G)xP0{my6YEv|rs#RUi9S`oDSF;-V*gdYsk-o+sH6G~dV$}>KB#^Z^;N%#eARCvU-nznbUWXB`sC6t2V*>3bURPQq^p^Wd<e9@nx_Z;>S`Vw`0uN^pL#e>aRS%_-VZzqJPdw>;t)k2uov7#QAtsX;JkvO23QNM1g{0}0_xzM6n@O}OEuak0u=2C&O0c&fk9vZocG#*bu?gYVog0*4@Wn+m!ioyz8p4#w}Lx?4sia@YQsDm=6KPY7yWuMzYW288PEw{Pf?9^R7-0rf}Ki$cJLB#4d?;az*~Tg;4R=qKn7k4bOB4iUEs%n8h97Zs1u>%e02QoM{w=~YTz3B@ZoIu8Px%+z#Z6MJJ18(g#B#<GVpSoK|4_FeIw>J0h_^n=%ExS_Mi?u)FY~J4plgxYD5{H$<Ya3&JMib#2Shb4)kjSXFxl6G-9*69e;YII~XZr(eewPI@5gJ$TRO#t^DN^jT9SRveRdtFl*%g2BriuCI'

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
