import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05641, -0.49, 0.13142), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.94493, 0.66079)
loop_1 = loop_1.lineTo(-0.92806, 0.68514)
loop_1 = loop_1.lineTo(-0.92194, 0.69547)
loop_1 = loop_1.lineTo(-0.89799, 0.71163)
loop_1 = loop_1.lineTo(-0.85546, 0.71923)
loop_1 = loop_1.lineTo(-0.89934, 0.71949)
loop_1 = loop_1.lineTo(-0.91554, 0.72007)
loop_1 = loop_1.lineTo(-0.94967, 0.65206)
loop_1 = loop_1.lineTo(-0.9632, 0.65206)
loop_1 = loop_1.lineTo(-0.9632, 0.58118)
loop_1 = loop_1.lineTo(-0.96238, 0.59146)
loop_1 = loop_1.threePointArc((-0.95813, 0.61804), (-0.95397, 0.64346))
loop_1 = loop_1.lineTo(-0.94493, 0.66079)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.89)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_3_interval_0.stl')