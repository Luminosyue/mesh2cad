import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.60335, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.80273, 0.05146)
loop_1 = loop_1.lineTo(-0.80268, -0.08125)
loop_1 = loop_1.lineTo(-0.77643, -0.05943)
loop_1 = loop_1.threePointArc((-0.76891, -0.05693), (-0.76183, -0.0544))
loop_1 = loop_1.lineTo(-0.75514, -0.01982)
loop_1 = loop_1.lineTo(-0.7506, -0.00237)
loop_1 = loop_1.lineTo(-0.79088, 0.03749)
loop_1 = loop_1.lineTo(-0.80168, 0.04947)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_54_interval_0.stl')