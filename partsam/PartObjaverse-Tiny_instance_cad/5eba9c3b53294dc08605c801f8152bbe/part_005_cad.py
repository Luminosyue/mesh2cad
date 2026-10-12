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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_005.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_005.stl', 'source_sha256': 'f80bf7ca3e25dff941f6f75203c34e866ed4278028fa84d828409276d3574022', 'input_faces': 24, 'input_vertices': 30, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25957170128822327, 0.28232628107070923, -0.11456182599067688], [0.19444620609283447, 0.4653688073158264, 0.21051819622516632]]}
GEOMETRY_BASE85 = 'c$}q_X=oEc6vrn`dRTiKwP~%c2u2}D=^<K$#Pdt3F4S5?#l&VyL#0Qy1P_X<AN-=&N~=gwOo9}IV1<AcN!>+yS|b|JHi`%OL7`ejKWP!1dGo5NtROn@`2Xj(bG&`Cvtp&uWG1{VC&8M|ouZKt78%4$e3G}#Qzyx5np%z+NDgq;X0>ZaO_jLEKz!tw)h)?&UTcM5-B`cQY7?yW&E7VztLZ?q*DW!=-E~NoD3=>tEfVdoDlN7NrK@d1yYR0qou=TAU3#ce)h1FW?X2H*HK6KnVb|UO(^scAaULF-V0~wEXGqoI!eCX1sq$_70pp6h;W>=&3lG9N+0iKQgG+&H=R?DGsA9!^;7zfoFuzbNfprU304G~I;*2|XOJO~(kgZ{OevSawrY(>^F<ptM3Ec6KbK!b>1m=AjABXYI<FGGjQ-i7w*GhdsSbtlX^OStpS6eyNuj+8}XsjRhiLM=k=jj^ktGursP!qU@T)R**0D7@^7~U(doadSUU4!#6`GG5iC;7gHUZ|T;bW{Ugz5g-P`E}zE<oR_ya7WK5uX8Q0r*rzH3jD1MoRr4{dR+U`!OuND!|V617V6+{vEPN~%Nl_z-TR&a4~e&6J@4&n@Sd$?lApIc2Kh{#P=TM3AWz4s7x!TNhCA?nWTyKG@S8^XP8>ISMnHqPF<5`|XFmS&n^D-m_ygyMBSUs^&TWhYEVAD~AJLdcZ)3eH;VLr7+N|ndMNipZUB!~J|GtXZge6HxCTbG;O!TR!1U+l>(Wjzch{3!WH3dD>4D@F7i!hi^Lp7jhYDAxgK8r>!jT{>3s9ET<a18S%8p$;BQ5PrpJnS=FfPM*$A{qs#h3E^=TWE-th9tA`Pruq<O@Z@F{PF%ibM9x6IP)xB>*q%zRwlEW(V{1jR;nJBJ^2A~W=);'

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
