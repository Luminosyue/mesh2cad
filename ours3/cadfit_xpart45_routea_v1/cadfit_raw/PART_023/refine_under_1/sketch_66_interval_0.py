import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.06, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.64499, 0.5366)
loop_1 = loop_1.lineTo(0.64727, 0.52642)
loop_1 = loop_1.threePointArc((0.65402, 0.51092), (0.65798, 0.50151))
loop_1 = loop_1.lineTo(0.66251, 0.48403)
loop_1 = loop_1.lineTo(0.66185, 0.45895)
loop_1 = loop_1.lineTo(0.65093, 0.43266)
loop_1 = loop_1.lineTo(0.64499, 0.41272)
loop_1 = loop_1.lineTo(0.64499, 0.53651)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_66_interval_0.stl')