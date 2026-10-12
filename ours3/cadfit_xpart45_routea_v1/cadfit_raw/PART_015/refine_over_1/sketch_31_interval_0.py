import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.67999, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66212, -0.25256)
loop_1 = loop_1.lineTo(0.49872, -0.25708)
loop_1 = loop_1.threePointArc((0.37703, -0.2578), (0.25066, -0.258))
loop_1 = loop_1.threePointArc((0.19674, -0.25928), (0.14096, -0.25891))
loop_1 = loop_1.lineTo(0.12707, -0.26268)
loop_1 = loop_1.lineTo(0.66211, -0.26156)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_31_interval_0.stl')