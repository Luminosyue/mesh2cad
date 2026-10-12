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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_001.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_001.stl', 'source_sha256': 'd33efa886de713b44a7e610cf378957f9b2fc01d5ec00306d9d5d8bf24ca028b', 'input_faces': 70, 'input_vertices': 48, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1078837662935257, 0.15129266679286957, 0.0015982298646122217], [0.11760766804218292, 0.19511090219020844, 0.04541647434234619]]}
GEOMETRY_BASE85 = 'c$}q{%WD%s9LFcG*0w%klh(d7Z4)<X(+61WgJL71mr@Cc2L&;qO|ew^NJ>Df;>ClA9_&Fpw1oQl3lve*g0G5r(xb&3eSmilf-{rvth>LiAUZI7Kl9z$-TD3Ix5Fk!J>DQIwN^IxbMPzk2^4)R3$lDByD&AL$#u`nopCY0@>PQ_9X>jiJmz9~wrEUba^qQJh#SL`14f)1le5`{Y<lM8Y<40e{X^-~xs330r_ys7F^={P#QC0BoS*0a+A75o5(ifvj|eSZJMmm<;fw$Jh=afOAh2Tf3y)e}sOvZ9FF5&y$nb5e&&Q@;N@Ztzjyw7v68CKHz5DHz8t3ivwO@R1pU?Y;*46lieLbd6)>EALq5QSaBwqN%`=xkOS9+hQc-$K*4~ezVl9SJh-esGA<ebVwDqVfa(SP`E)#?|GtED{L8p=EQ3GabBHvjFLQhrv+eE6KsU;g-7jZ^mZXrI&dd|y;~C_J;rtNqlcQoM=FjZYoxhxlgwz^D17zRsuV(|RMmS#R1W`QPLtUhQwHPwMOX)NzshqQ2fQ(<l2yeNN}o`X|0w|Jo<}OMOn`rQZwnNj_;kP=8ZB(C>@*>ibICPS1_K(|p~-nCune^qfpvj!tRHrq%iAoa+0lqqD#FzmLvFv4#dFk9o#q2vN~%p>c36co(z_TrGMS_l0p!5ZC0K8fXk$0}hBT-@8rp5OfDP1a61!1h<1D&;U4qXGRc%jAc8t1-u>Xhqi(J;A&_XTqgP!(RV{Tz+q?<+5wJ&<Irw!9NY!%0e698mgjP48<>Nepe^7ga2>P(TnDa)HiGNH&Cn3I8QcnO2e*O^XasD4JE1Xf46$?~SCz;?2e=zr1+Kz;%@r8;fIFe(;BvfMv(K^~AJ!|?1NI;`%`Qv4F62Whv*d>%f3ms3Zsc0C*OGrP_D5<NI63Na2R(oKh5Fqts+U`TsOX*c<HLIAKJhH`FiDR3%1R4%vw5NW)!biEUbea'

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
