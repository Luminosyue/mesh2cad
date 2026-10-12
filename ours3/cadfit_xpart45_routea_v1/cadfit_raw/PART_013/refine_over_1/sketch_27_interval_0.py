import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05439, -0.02294, -0.13463), normal=(0.00848, -0.04584, 0.99891), xDir=(-0.0, 0.99895, 0.04584))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81806, -0.43205)
loop_1 = loop_1.lineTo(-0.78892, -0.47425)
loop_1 = loop_1.threePointArc((-0.78091, -0.48644), (-0.77369, -0.49723))
loop_1 = loop_1.lineTo(-0.83514, -0.49964)
loop_1 = loop_1.lineTo(-0.81833, -0.43309)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_27_interval_0.stl')