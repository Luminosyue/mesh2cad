import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01821, -0.294, -0.12481), normal=(-0.57108, 0.8209, 0.00186), xDir=(0.8209, 0.57108, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77293, -0.26304)
loop_1 = loop_1.lineTo(0.7731, -0.7279)
loop_1 = loop_1.threePointArc((0.77324, -0.65797), (0.77401, -0.59174))
loop_1 = loop_1.threePointArc((0.77406, -0.56521), (0.77454, -0.54225))
loop_1 = loop_1.lineTo(0.77808, -0.51673)
loop_1 = loop_1.lineTo(0.78251, -0.50343)
loop_1 = loop_1.lineTo(0.78729, -0.48577)
loop_1 = loop_1.lineTo(0.79041, -0.46563)
loop_1 = loop_1.lineTo(0.78773, -0.44741)
loop_1 = loop_1.lineTo(0.78611, -0.43446)
loop_1 = loop_1.lineTo(0.78105, -0.4197)
loop_1 = loop_1.lineTo(0.77466, -0.39103)
loop_1 = loop_1.lineTo(0.77406, -0.3652)
loop_1 = loop_1.lineTo(0.77326, -0.27833)
loop_1 = loop_1.lineTo(0.77297, -0.26526)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_13_interval_0.stl')