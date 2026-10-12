import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.21089, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15678, 0.04626)
loop_1 = loop_1.lineTo(0.17617, 0.03724)
loop_1 = loop_1.lineTo(0.19141, 0.01386)
loop_1 = loop_1.threePointArc((0.15963, 0.01228), (0.12923, 0.01225))
loop_1 = loop_1.lineTo(0.11043, 0.01222)
loop_1 = loop_1.lineTo(0.09351, 0.01138)
loop_1 = loop_1.lineTo(0.1146, 0.03304)
loop_1 = loop_1.lineTo(0.13717, 0.04579)
loop_1 = loop_1.lineTo(0.15656, 0.04621)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_20_interval_0.stl')