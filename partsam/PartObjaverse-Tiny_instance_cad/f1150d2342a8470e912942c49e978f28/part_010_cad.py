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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_010.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_010.stl', 'source_sha256': '99961f1b1067b57e3850e4703eb647fbbf097829acffaff5af81807f507cb239', 'input_faces': 32, 'input_vertices': 39, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.46738100051879883, -0.4921022653579712, -0.46202343702316284], [0.4024432897567749, 0.49156084656715393, 0.2861560583114624]]}
GEOMETRY_BASE85 = 'c$}qGO>0v@6utRqHGVW2W3^39r$$YLpkQ5S6_S-GA@UGnBS?L*eZitMHK_q9mA7&yMcrkg32t=h!i|D`MG)&k<5y6yG$0863-8Rk6W<$B5FI$2GiUBQ8D=gME#vct!5$-!Hx{!AKLE!T2t(B<&rMGnl|wVLH$AXT_<Tsde>RuZE_k2{^YJO8GFgs~vG~d2v3Qcji>2~hxiE97RGu=pf2we;VxV8SQkXSxo)|rzWTOX@Y=Qmj*u?j6@7L-QQo43)jk7g2-&}I~?A<HQ?1bAlhi$(;a`{fm;agGLHw)TFrw<cD4>{{f4&-gWKIG1UbGDyWa_YI9m|IFtTlztF4m)rAZQY%tXUDtd)TOWFw8>X<>R%F{y5+Ez?aO-e!B4yX#f>%beJCdK^>OXHI4?SX{q0?Qf8@)1(HE{Zoxa)n{6?I&QV-Hs>eD}-zIN7IwTZ{6E;-UybELn1PTw<ePE?<+m6lUo`l{nAeI<RhPo%HjJM*y?pEJs5?-y5`K2Sb175^gjmEy~M_QCc|>#*?Kr}OrG-)^{kdGFG<UOxXO?z6eFD$b*7iTgDh%fe@8@~*y;zD|CpPh`Ebe>B%C^XN(7D|k^N0{F@l3yvp7EC6)4`x7&L^zWXSBme!xgm4eIE7(E2o%AlmPDGeEM0z)(pVs?njqA<8pHzT81b?@Jh^;ga(t42Axb`7>=@|HH>p}Dodr5n#hU<;Q0pecLdk_PNDDfa^&Jog4(!&I<8G-8|#0FwNafEb)viyWW+M|aw5D$<(fY^_SiB<sEi`YjTBORj}uC<KE8}_aD7xibD{0CisSn8MVwsU@2#H>yeYMCB>c39<w>&Oi;`wjACnQ;'

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
