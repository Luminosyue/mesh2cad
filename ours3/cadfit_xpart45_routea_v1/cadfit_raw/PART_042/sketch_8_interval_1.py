import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.12756, 0.00205, 0.00163), normal=(-0.00025, 1.0, 0.00024), xDir=(1.0, 0.00025, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02565, -0.2939)
loop_1 = loop_1.lineTo(-0.02764, -0.30576)
loop_1 = loop_1.lineTo(-0.02147, -0.33095)
loop_1 = loop_1.lineTo(-0.04135, -0.36927)
loop_1 = loop_1.lineTo(-0.01691, -0.37492)
loop_1 = loop_1.lineTo(-0.00341, -0.37672)
loop_1 = loop_1.lineTo(0.01816, -0.37517)
loop_1 = loop_1.lineTo(0.00834, -0.33232)
loop_1 = loop_1.lineTo(0.00715, -0.31199)
loop_1 = loop_1.lineTo(0.00528, -0.29269)
loop_1 = loop_1.lineTo(-0.00692, -0.29019)
loop_1 = loop_1.lineTo(-0.02565, -0.2939)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_8_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_8_interval_1.stl')