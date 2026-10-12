import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.47266, 0.36319, 0.09245), normal=(-0.0001, -0.33312, -0.94288), xDir=(0.0, -0.94288, 0.33312))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20719, 0.46734)
loop_1 = loop_1.lineTo(-0.25217, 0.4673)
loop_1 = loop_1.lineTo(-0.25218, -0.46828)
loop_1 = loop_1.lineTo(0.19622, 0.37019)
loop_1 = loop_1.lineTo(0.19732, 0.38132)
loop_1 = loop_1.lineTo(0.20721, 0.40001)
loop_1 = loop_1.lineTo(0.20719, 0.4654)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_36_interval_0.stl')