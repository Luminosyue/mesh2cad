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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_007.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_007.stl', 'source_sha256': '1313cf249df9ed080b51b0cb24c8908d2e6ccf5ff64bcb338b16f29c734e921e', 'input_faces': 40, 'input_vertices': 28, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0009521245956420898, 0.37315019965171814, 0.0037525631487369537], [0.04532179236412048, 0.449736624956131, 0.22769777476787567]]}
GEOMETRY_BASE85 = 'c$}qGOK1~O6n&X|ns0weqgIirA4Vb6Pbw4<;wpk^HK;{JX(zN(ES9uQN>tiNDn^QSVJXsr2%#W?!A0D-korNzAk&r7kGe>^le*|8P{H4OcW&%UjUf8qa86FnyZ6py-Xs{%8(c(Nb!6MFtVPrl!eA#Z5>q1mUF}M=KHPgrM=HT*tH5JNTAG8WbtFaxqz)z89+CEo(t*xK$s<agJ(2!MDBRW)=}?&O4|PWs>POFodKLP4$KFPd=-ufN<Kn+AD-7X1>SH4<jl5@^x>Ymn<NVy=@sErX8UI!A&t8u(mNz|tyzJdR&HLhD7V>0NN&=^wV4wJMb{^^t=2YI#ZC(5TpQU^Pc-WsTnMeP(d^&jp=E$32o?Pv+TI9DlVV-BEnIZ76O^lSx7yPyPp%-H?&z&tWkKB<~c|Z5nqs_DL&;Z=0ME5xO#^aC|g~uxI%k`~Ve#IOI{&5j}@pTjA6N``3B40YG<-g4g!uQ|nZbO}wIOJ2yuhb&{)UcL+K5-eY<HTqR>ZHc!z<+Z^E%M1E+z0Z>8-qIUlu4*-$wFS7yQ%WNyyvZ!e~`Zb{!-gr@G}dukk2%$yf4mwhB?W@sW9;QhI?>-7OJ8C!KY_b-j}VLwfYms`h3Bn)8+NuH_8HyP*~{c>I`v5i<xW{xb)HLYWS<8)v)`&kJbh{!$yi)#Ci(mvCDB2_Il8`95rJrYQ`qiWfV3F2Sp9?It0@d$Trk9*u#NrNA2M1*|B~Z!i4)x*xQD%Vof*pD@U$CU4fZ`@5cUa?9Fr~MKy&1*^HX8fEs@?&^ikCb~I8{Av+OFTafjrtFVU=*?`)})iYrILTw#cT>^S~)E1o6i8DIUGb0PAg8`l3(*Nnzzq%68jQ=B8yR-PQ=6ANzTE8ChV8Ce71{O#k<uB|C$xof68dC'

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
