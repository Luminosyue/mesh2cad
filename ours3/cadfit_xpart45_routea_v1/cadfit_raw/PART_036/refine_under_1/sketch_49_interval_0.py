import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.18678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98442, 0.15411)
loop_1 = loop_1.lineTo(0.97374, 0.14336)
loop_1 = loop_1.lineTo(0.95061, 0.13953)
loop_1 = loop_1.lineTo(0.93361, 0.15118)
loop_1 = loop_1.lineTo(0.92946, 0.20146)
loop_1 = loop_1.lineTo(0.97844, 0.20134)
loop_1 = loop_1.lineTo(0.98431, 0.18245)
loop_1 = loop_1.lineTo(0.98259, 0.17182)
loop_1 = loop_1.lineTo(0.98441, 0.16045)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_49_interval_0.stl')