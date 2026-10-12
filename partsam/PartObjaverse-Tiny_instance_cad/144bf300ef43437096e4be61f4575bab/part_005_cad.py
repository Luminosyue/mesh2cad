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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_005.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_005.stl', 'source_sha256': '8672e447a8bcd648c818a4d37c2c9a1c36e5e4b8daf485a5b4ff90657eb9cb86', 'input_faces': 36, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.004070974886417389, -0.030893223360180855, 0.3868545889854431], [0.023909680545330048, 0.019861295819282532, 0.40982240438461304]]}
GEOMETRY_BASE85 = 'c$}q`e@u*V9LJx#E-J-cF8vUme(hq-Y$b{5{!k>fW7vvTM|X2c<vP`sILay`DnDX=9GhVnGZUt{`KL)^Ge2TB{ncm@n-McS-}mQ(GB)GcK6|~tuYI5I^Lf7a?0cpRFO6QJD?$pqyQosDkt9+6l3pse*d4Ytma^%^rB0Qkg%{U%wq`BQG-a!#a;e%-U@2Q;Hzdo3xz;2@oNTa`*d2CrabAhNz#@E_xv0#d__DR;Qj0Q<jZcb`<EO^SHS)h+exir#=SpuXa7_+s6wE(6_#{R6u8Sq`cRo1<jm;kN4_b=F*z>q+>rK4NEAm$!6p69yJaG&@eTaPckWGx;Z?#9^6N8?@r!^G7_elHjoHsG#-yB*EUtNC$^J~7)I?*}sE>jEUd+L*Eeqgg1&yDmxg#KU5B!BsNKIScpIe`8Tgpk*!!@E~?w}OE>@^k0IOH~!?#5ljdlb(CknG3(`@j<M!%s}(qvGB$v-ff^?0{I!iG=H78Nw7ES9<8(U!%ECMm9qzZrSrZSH!a0`rCq4SeVHBPPy41~Y+UT1eO*t!_j4xr#fE*BpS6;&Ys>-r?1i{5I*a%JMy{Z1+Dq#5V?X(|*;cSUcN?C6Je_=Zc%h(i-q2z6-_HHG6G{YSeJJ+Lc<vGTMQ2LEhYfhHM`t2`J7fb`d%YU#@0dltZ;J!_`}r%@_q;Qbf7j*&Z9(voPagRipDOUgrAoZ-SRMJ9o$#Io5&O~SEno8es?F%%*a7d+%psq0A6~K~Z4`9dQsG@)g)Vrn4lCAA9!*}|O}?V41^o|XleaIdgZIzFchdW8um|JaXZL_7UpJwz^HG@Z8Jf}zA30Eu@$6fe@9L~>gWtYlFZ}zyo)puF(<Cp{@nMEq`J$BaRZbJDdDu}RBtAFh?~f8&!rvVwiT{0+L?}H>R%#NL$YIQhoCPOv4&xliCGseyp0l7oXD_CP>Caii*@sKy0H!bJ0M4ViME2$q*^e2_*^l!$=2*_-I7>{e^z#x~%_Xu*sWD6)Q_EQ}h_jCKcxEW)@ti}L;hY6!&VrGgLpV?25;=+)%{hv5j8diym0Iuhr@yYBmrFE0;*adtJ4b$|!|%*e*81_$nlik_@1|^!TH2uS8b;p$d3j_&'

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
