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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_005.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_005.stl', 'source_sha256': 'a1ffe653de1ea60ce7de8dd3a955a2dda6834a3e6f45e435dad241e62a2bbc59', 'input_faces': 20, 'input_vertices': 30, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2229316234588623, -0.11586761474609375, 0.163628950715065], [0.2752169370651245, 0.04747974872589111, 0.32327815890312195]]}
GEOMETRY_BASE85 = 'c$}q_T}V_>5XaBzt{=JSnx^I|-5%<0rdC>EQn{E|u$5boqy)9NcTq9jc1;oqZd8~RzJwB$l4zh-vM5FLffllstC=4Uf(Ql)5(pZC5j}Kf=2#j9Q3r<q%#XQq=FH(-tHoa%$!Kk0(|IY6tp1FF=~*PJP+a9j1&TYl)LE%v2IR1o^yZP{hpl-UR>7)dyW%cz$?1~3$B`x{O0uKORqnEto+@+M72w&n61T#+yU^xTcx+1DmMEoePLwW4|GHK|4*@j;8K8F$G@&kzzen9TOFXEr8MMbaF^qAoaS$~trxkhJ=Mjw8=MeYg)^u}`=F)r^Z!acpx7@+}w<T1kafJA{Ls;LO@RfMeIPotJE<qi2YbM3s(08akNe<xVnN33&FH{r1+*=R)-qBI&J7kjh!LDlHr*-$KPI@nWH_&z)bgJGnhOzz=adYfL+;?Zy8;I3`Oqxfb_6q8UY|K{|Y{X5CH?V(cW)$O(1tQ<wj{Qttr8$&bN3J$kda%An*N@!SPJF+i3pkU9abK4Iis~5pn}AOZx@bPfhKMIcJi$7-#eEo`n;{-(dWv=IE-%Jov&8e`+px~XTNHc4u%0?^dye<zoA1TAE{66gO>V{fsJ)aoD0t}WPMrVZc{-O-BED;`1?$95(0R6`5$`zh7<kW_EIM!JN#ZZ^u}^cuB+Xf0LHpE|J;VI=X*`#@?;7Q&n>uiwoeJg24aC*9mzW=}cr&akUSqdUo8Z(i1{Ta;qr<lBDFTGGq`!ZPMLYiLDW?4YQ(Vn^fcK~u?L%8yVc_e8`UxNYAOYNhgn=I{G*I|)++ZA0LSuvv8ZP`0xKeImLZgKrCVT_8wcH}O#R~)9D0GeRjlz!=Y7l;`@Ye~A7QWS@@r(5T)35XAQt^J4|44uRa^*EI|FV|X`f=%2iw<VP2k6Jna@`G6WZwbXG%c+'

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
