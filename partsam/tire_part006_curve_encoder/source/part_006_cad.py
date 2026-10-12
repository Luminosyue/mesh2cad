"""part_006: editable CadQuery reconstruction and optional mesh-preserving BREP.

Install: python -m pip install cadquery==2.8.0 numpy
Run:     python part_006_cad.py
Both:    python part_006_cad.py --faceted
Metres to millimetres: python part_006_cad.py --scale 1000 --faceted

STL has no unit metadata. Default STEP uses mm while preserving STL numeric
coordinates. No physical unit can be inferred from this file alone.
The smooth model is an axisymmetric approximation, not recovered design history.
Edit the control points and radial/height factors below to change its shape.
"""
from pathlib import Path
import argparse
import json
import cadquery as cq

# Original-coordinate location of the fitted axis at the reconstructed base.
ORIGIN = (-0.2409537786, -0.5709710406, 0.2541800557)
RADIAL_FACTOR = 1.0
HEIGHT_FACTOR = 1.0
# Profile coordinates below are 1000 times the source STL coordinates.
# Construction at this larger scale improves geometric-kernel robustness.
# Ordered (radius, height): bottom round -> lower body -> groove -> upper body.
OUTER_PROFILE = [
    (89.1509,2), (90.69825,4), (91.56009,6), (92.41669,9),
    (92.94448,13), (92.88302,20), (93.1179,30), (93.29157,38),
    (93.15282,42), (92.10717,46), (90.43984,50), (87.9931,54),
    (86.26964,57), (86.73893,60), (89.36611,63), (92.14348,66),
    (92.85242,70), (92.98411,76), (92.93757,88), (92.88676,100),
    (92.47951,103), (91.84522,106),
]
# Top rim -> recessed annulus -> central raised tip.
TOP_PROFILE = [
    (89,109.31268), (87,110.57996), (84,111.49261), (80,111.86326),
    (76,111.83402), (72,111.2133), (69,109.8761), (66,107.47571),
    (63,103.36651), (61,99.24598), (59,95.8644), (57,94.32248),
    (54,94.04718), (51,94.78184), (48,95.22437), (45,94.95202),
    (42,94.10495), (39,92.93775), (36,91.57253), (33,90.46245),
    (30,89.94739), (27,90.4585), (24,93.43219), (21,97.31479),
    (18,100.94594), (15,105.25309), (12,107.82303), (9,109.90723),
    (6,111.21396), (3,111.72656), (0,112.07098),
]

def build_smooth(scale=1.0, centered=False):
    """Create a closed revolved BREP; does not require the input mesh."""
    from math import hypot,sqrt
    points=[(r*RADIAL_FACTOR,z*HEIGHT_FACTOR)
            for r,z in [(82,0)]+OUTER_PROFILE+TOP_PROFILE]
    # Divide the profile into features for robust STEP transfer at small scales.
    # Shared unit tangents keep adjacent spline sections tangent-continuous.
    cap_start=len(points)-3
    boundaries=[0,5,8,17,20,27,35,43,cap_start]
    cap_r,cap_z=points[cap_start]
    apex_z=points[-1][1]
    sag=apex_z-cap_z
    sphere_r=(cap_r*cap_r+sag*sag)/(2*sag)
    sphere_z=apex_z-sphere_r
    def tangent(i):
        if i==0: return (1,0)
        if i==cap_start:
            dx,dz=-(cap_z-sphere_z),cap_r
            length=hypot(dx,dz)
            return (dx/length,dz/length)
        dx=points[i+1][0]-points[i-1][0]
        dz=points[i+1][1]-points[i-1][1]
        length=hypot(dx,dz)
        return (dx/length,dz/length)
    profile=cq.Workplane('XZ').moveTo(0,0).lineTo(*points[0])
    for a,b in zip(boundaries[:-1],boundaries[1:]):
        profile=profile.spline(points[a+1:b+1],includeCurrent=True,
                               tangents=[tangent(a),tangent(b)],scale=False)
    # An analytic spherical tip avoids STEP reader failures at a tiny spline pole.
    mid_r=cap_r/2
    mid_z=sphere_z+sqrt(sphere_r*sphere_r-mid_r*mid_r)
    profile=profile.threePointArc((mid_r,mid_z),(0,apex_z)).close()
    shape=profile.revolve(360,(0,0),(0,1)).val().scale(scale/1000)
    if not centered:
        shape=shape.translate(tuple(x*scale for x in ORIGIN))
    return shape

def build_faceted(stl_path, scale=1.0, centered=False):
    """Sew the original triangles into one solid, preserving every vertex.

    This is a true BREP solid with triangular planar faces. It is useful for
    exact mesh correspondence, but is heavier to edit than the smooth model.
    """
    import numpy as np
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.TopoDS import TopoDS
    dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')])
    with open(stl_path,'rb') as f:
        f.seek(80)
        count=int.from_bytes(f.read(4),'little')
    if Path(stl_path).stat().st_size != 84+count*50:
        raise ValueError('Expected the original binary STL format.')
    triangles=np.fromfile(stl_path,dtype=dtype,offset=84)['vertices'].astype(float)
    triangles=(triangles-np.asarray(ORIGIN))*1000
    sewing=BRepBuilderAPI_Sewing(1e-6,True,True,True,False)
    for tri in triangles:
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in tri],close=True)
        sewing.Add(cq.Face.makeFromWires(wire).wrapped)
    sewing.Perform()
    sewn=cq.Shape.cast(sewing.SewedShape())
    if len(sewn.Shells()) != 1:
        raise ValueError(f'Expected one closed shell, found {len(sewn.Shells())}')
    shape=cq.Solid.makeSolid(cq.Shell(TopoDS.Shell_s(sewn.Shells()[0].wrapped)))
    if shape.Volume()<0:
        shape=cq.Shape.cast(shape.wrapped.Reversed())
    shape=shape.scale(scale/1000)
    if not centered:
        shape=shape.translate(tuple(x*scale for x in ORIGIN))
    return shape

def describe(shape):
    box=shape.BoundingBox()
    return dict(valid=shape.isValid(), solids=len(shape.Solids()),
                faces=len(shape.Faces()), volume=shape.Volume(),
                bounds=[[box.xmin,box.ymin,box.zmin],[box.xmax,box.ymax,box.zmax]])

def main():
    here=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scale',type=float,default=1.0)
    parser.add_argument('--centered',action='store_true',help='Place axis/base at origin')
    parser.add_argument('--faceted',action='store_true')
    parser.add_argument('--mesh',type=Path,default=here/'part_006_source.stl')
    parser.add_argument('--out',type=Path,default=here)
    args=parser.parse_args()
    if args.scale<=0: parser.error('--scale must be positive')
    args.out.mkdir(parents=True,exist_ok=True)
    report={'scale':args.scale,'step_unit':'mm','physical_source_unit':'unknown',
            'position':'centered' if args.centered else 'original'}
    model=build_smooth(args.scale,args.centered)
    report['smooth']=describe(model)
    if not report['smooth']['valid'] or report['smooth']['solids']!=1:
        raise RuntimeError('Smooth CAD validation failed')
    model.exportStep(str(args.out/'part_006_smooth.step'))
    reopened=cq.importers.importStep(str(args.out/'part_006_smooth.step')).val()
    report['smooth_step_reimport']=describe(reopened)
    if not reopened.isValid() or len(reopened.Solids())!=1:
        raise RuntimeError('Exported STEP failed round-trip validation')
    model.exportBrep(str(args.out/'part_006_smooth.brep'))
    print('Smooth CAD exported and reimported:',report['smooth'],flush=True)
    if args.faceted:
        model=build_faceted(args.mesh,args.scale,args.centered)
        report['mesh_preserved']=describe(model)
        if not report['mesh_preserved']['valid'] or report['mesh_preserved']['solids']!=1:
            raise RuntimeError('Mesh-preserving CAD validation failed')
        model.exportStep(str(args.out/'part_006_mesh_preserved.step'))
        print('Mesh-preserving CAD exported:',report['mesh_preserved'],flush=True)
    (args.out/'cad_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
