import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08156, -0.00245)
loop_1 = loop_1.lineTo(0.00389, -0.03385)
loop_1 = loop_1.lineTo(0.00066, -0.04386)
loop_1 = loop_1.lineTo(-0.00179, -0.05812)
loop_1 = loop_1.lineTo(-0.00036, -0.07315)
loop_1 = loop_1.lineTo(0.00302, -0.08787)
loop_1 = loop_1.lineTo(0.00426, -0.10064)
loop_1 = loop_1.lineTo(0.0144, -0.13185)
loop_1 = loop_1.lineTo(0.08151, -0.00255)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_39_interval_0.stl')