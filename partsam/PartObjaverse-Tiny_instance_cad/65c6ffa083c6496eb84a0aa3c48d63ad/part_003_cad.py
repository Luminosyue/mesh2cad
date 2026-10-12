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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_003.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_003.stl', 'source_sha256': '77ecefc5f0035574fcbd3a7f13d1efe6faddb2161680444b2ab557bca1581e6c', 'input_faces': 54, 'input_vertices': 56, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2593580484390259, -0.37147778272628784, -0.26220202445983887], [0.26049691438674927, -0.2375171184539795, -0.12966494262218475]]}
GEOMETRY_BASE85 = 'c$}q{TSyd97{|}<y1K5{Z1b8qTDDqhmaB%{wjLysVu^%&(k)jKB5l`%uxJ7cdgw+)8U$Mu5=Ivyq5>T?wM=)nGV4JriXsXudx%JgX3qRqXT}pm9T@(<`7v|&X3jT<ag-TCEJPmZ<Y48INx?{nbVL#hX>_?8YPY*QdAsWO>PRg0(g^0MP30RM6*|&Lnyl3>&vv)9gtM-!S#HhYtTlD+2DfupWu3d)CHYe4PLE6Uo*mA5mw294Sd_yRWan`ExqlsIu>^i|YhaC3(uTelonm_R+@nr~f75ZDdTy+BfaUGyF7+!tDQuSgkNiHRw|~r~p068yp!CAs-Vy0sXg}Yh^2bW3=j&U#m7a55cuwmaz15}k{Pl@pTBj*h<%O;l)K^`&CMbQ?fql=YA8k>2E~MkBbWT3^2UuP^k3HT*z4y+E0L#y)r)ujHdTuEVu)OxUxZ+NF9XZqHXL;@WA(1xfg^G(lrq{e@?*3UiuMoCvh~>5G<xT%g=j9GW4YIs;-AVLmAFF?Yen$U%ukk7S&_3BNukY<IBP=gG8>5~)bPTY(ch#4ErMJJhC;N<^K9#?`NAAPMo4rc!{lLlBzrXQ7HUGp7xetH7>QU91Ttq$pHB;rQoLA&NY`fa6^rSwXdfvE2<%9hxd|IdSLisznKi!}FEU%r1uXa#x51jO~ytW>Ddk^hH;c%j#<+aa6hSyV1BAh;!*S;V7>z8sLrX3$*dF^}Vxn{Y~$<aZU*RB^ozFPKMnjW*fcHPOhlmM%Lf__H-#F_(Bedti_{u77Zj++dGNJqH1``0)XTfZcw5lr^hUu*ljt>5<FTfa`MAr+-dIhRZiiS@{NU_ID?OamLhAxI7!0yZMk!A5W>G6Nh64nxidhk;GV1z;069GM9Y2b+-#!DetIG7B6Djz%s5M}uRLIpA1u95N3a2eu&d!4_~lav3-toQSl66T!*IB5*P|1z8ME0Vg2~!Aal*WC1t<JO{ZHJO?}*xdc2LJPVl%o&}CUE(XVdqmbF)C~ySQ3U-v~^cKUPexarZFEy;{he~^=`twuX`AeK@>SJ`28Kqtm8(L3xi@BCw`x_sES4j'

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
