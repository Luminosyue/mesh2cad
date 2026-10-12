import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05333, 0.54334, -0.17161), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.90546, -0.0214)
loop_1 = loop_1.lineTo(-0.89537, -0.02178)
loop_1 = loop_1.lineTo(-0.80148, -0.02234)
loop_1 = loop_1.lineTo(-0.77656, -0.01098)
loop_1 = loop_1.lineTo(-0.92203, -0.01098)
loop_1 = loop_1.lineTo(-0.90546, -0.0214)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_22_interval_0.stl')