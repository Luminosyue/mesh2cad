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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_001.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_001.stl', 'source_sha256': '3cb852bbe50444281e8db06f9c56499aa5a619533af78a2fe5ea9d92db5dd1d9', 'input_faces': 36, 'input_vertices': 35, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.013724005781114101, -0.45818057656288147, 0.014724649488925934], [0.150157168507576, -0.1501094400882721, 0.18291699886322021]]}
GEOMETRY_BASE85 = 'c$}q`T}V_x6vt=Rk8-uNbv3`LYXoaxA7qJH((R=eDVE5}9_%i9w}eo4SA;U-MiCJrQoYnm*XV<KS;z-{v2H4*NJJT-55YwVB6=u7pPMuDpS(sv)WG5YpC4z>oI5kjM(WejLrjix_Grgg?L-=56ge!!y39mpYqOc$+SYN_$MOWHq4dU~hJ%qtAM0Y>;TAL5oCw!y;k~h%aHSTGwI@0g(YBNAi58Rif#{i}$$9d0w8P}{imF|eTGi%Ctw;OU5#TMjM@oD5akbhLFP?FADsGL^Tx*cre)nXIxMc=LXs&~6S4*ad>(_h7MIN|5SuOJQ$BlzDcfeWy;%iZ7^5K|R@2KR?p6_pnvv|t!a((dYxX7Q2-xKQ{L!YCcW<>te)|XzceOsImJh0GDb3^5yD}GO0+al{LZruL-R^(rr9u|Fov!1(>pE6QjZbar^3BC~Sqq(c<f06y@F<D=6eL$}34$KdGxpsMz_+Gs$-xl-Zs55Z*gQ!0(zsmr3?#Md&1=)`UuFc4Gt@CrkUT)vNDEq&%P4=nkPs#dvH~IwE+fd(?{jf&x=d!*rB-hozohF&jnrcLSL*);l{sZ)*@)ywO{-CJus(f4KyMbuR%h|`-SyBJmZdw0?x`#5~xhd<|il?w|dR?Dfw?^DAhW&BW{(!6RweY<*xP?Al^r^Vo2M7D0xH=b`&Ly(!6>x*Wy6t|(D6;q~5Q}=A0D?4>{{9JQ-T8M<K=pq=0foGWH9U$D<O`tL@CER>Jo2GAJm?k6<l%#^g!jQSXbxK%<o(cGct3nPG#fr0J_8znCtVGn0iOj8!e_y+;;{mnhaew9kS~G;;fvr)poQ=y@MX|q_%ir)2=b-S0{Bw+wa{F6wWs7Y9vj3JlDZMT9DY5INWIS=O8e7a&eE{x5SIM`{rb!0*VOyVOuq3yFKwhggU*&8lAp!7#>MOhKU7^k'

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
