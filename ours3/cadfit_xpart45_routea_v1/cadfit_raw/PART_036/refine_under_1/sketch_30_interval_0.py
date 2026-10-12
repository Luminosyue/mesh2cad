import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.98294, -0.0889, -0.11238), normal=(-0.99971, 0.02147, -0.01116), xDir=(0.02147, 0.99977, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07859, -0.04792)
loop_1 = loop_1.lineTo(0.22684, -0.0479)
loop_1 = loop_1.lineTo(0.23976, -0.04049)
loop_1 = loop_1.lineTo(0.17803, 0.01765)
loop_1 = loop_1.lineTo(0.12057, 0.017)
loop_1 = loop_1.lineTo(0.07941, 0.01663)
loop_1 = loop_1.lineTo(0.07822, 0.00214)
loop_1 = loop_1.lineTo(0.07845, -0.02945)
loop_1 = loop_1.lineTo(0.07859, -0.0479)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_30_interval_0.stl')