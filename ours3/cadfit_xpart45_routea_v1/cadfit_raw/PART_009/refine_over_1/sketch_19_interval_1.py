import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06177, -0.86659, -0.08837), normal=(0.10613, -0.99435, -0.0002), xDir=(-0.99435, -0.10613, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12801, -0.17144)
loop_1 = loop_1.lineTo(0.12969, -0.00268)
loop_1 = loop_1.lineTo(0.09458, -0.16866)
loop_1 = loop_1.lineTo(0.12653, -0.17131)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_19_interval_1.stl')