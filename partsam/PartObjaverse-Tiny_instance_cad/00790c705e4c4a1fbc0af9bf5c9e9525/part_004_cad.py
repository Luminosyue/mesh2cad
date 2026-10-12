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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_004.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_004.stl', 'source_sha256': '64396eefccebec7df72b83717d9b6e5605622c65af587fc04f015dc40ea79fd6', 'input_faces': 34, 'input_vertices': 36, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15652737021446228, -0.20397891104221344, 0.15791946649551392], [-0.15572169423103333, -0.20274993777275085, 0.15932348370552063]]}
GEOMETRY_BASE85 = 'c$}q`T}V@57{}k8eYrKAA9H@DM<u2rK`CnG+>yYNr3}TWNZityO8K#g5f$vByCeuN>LOuYM`89scu|8!kq`vpMHkh9qN|X~Ci7$3Iq(0mGzy|#IQ;+T$Nznv=bVlAc-&f@jbRnB<lxj@S<9GuS(uHD`U4|<UH;(ifuZvnmdd%hHg&wEz1eeI!$#Q!N4G!N6>#hq9d$jmjtbGyGZ+{N_y#%$1Koa=H~P*5{R$8E`iA_<eQ9NNg;-fuAzl*yb(xhBB6d^siK-74U#J?oUmbNR>UAc8e*%|2)^INM8#xabFC(9*<D9jE%U8Z3AKC|g-M~4UKt9q?&v~c?Tpo*Y&MqE6-&=a*&#rJDo_8U?7d#SMLf@B8)W4(SJT$h-xjfx~IXAT6GjZg5CC=p=#A9omi_Z@te_KG`dGw7mg0o@p$mBZeq&I@sXfS_m0`s2)m&?Ju*VruIcl9uyYi{Ey&rJ)QhfCb3GXXBY+d!S0O_--^opULnL!DR6cn@zA;8D~GEgV5#d5!Z>(8#%T*~58Q1MZ#EgSUapt*e}if*JLlZJb9eE8rT_EanB59xr452@B`)hjz?g9tW?tVxHhJ<PG57L&%Hqqo_Z*g#7C?<lmpbbFIfXkBp;^ybC<M2RwY*hB-?+kdH4SKbH<(3@*vU-`LUD*@^f6=qsM9EQfP%t`GH1;9;Yk-Y4?%voEOAl!yGxDLk+1Gkz~S>acU*($oU#uOcr!?2fuT+fIkRdma7R0%PiBQci~+-<G36h3eYW-yaQqReyIhRQ>nSP^8RIqFjZf#pDag7m$kN3&`h_?j)a2K9@9)d@lKH(j4;H<g-Za<g>_UlG?~;lFuMbC!aw+jWm^f8hI;eGI=Zc6w)2!Q^;FLP2?@)&7?;1X7Wj-dh$u+4WwG~2J$*m4S5}Tfs~Q=xHW=J`=?LN&lTdEwtj$q-MRhmxOHcN()`Dt)8p0~&|F}{iVpL;??0D}Z2'

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
