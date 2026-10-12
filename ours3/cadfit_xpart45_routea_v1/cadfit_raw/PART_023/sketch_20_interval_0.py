import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.33865, -0.02794, -0.18426), normal=(-0.86274, 0.50566, 0.00027), xDir=(0.50566, 0.86274, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.47573, -0.37755)
loop_1 = loop_1.lineTo(0.45137, -0.37779)
loop_1 = loop_1.lineTo(0.41035, -0.40135)
loop_1 = loop_1.lineTo(0.39244, -0.42308)
loop_1 = loop_1.lineTo(0.38458, -0.44861)
loop_1 = loop_1.threePointArc((0.3888, -0.45863), (0.39222, -0.46681))
loop_1 = loop_1.lineTo(0.42181, -0.48435)
loop_1 = loop_1.lineTo(0.43412, -0.48596)
loop_1 = loop_1.lineTo(0.44501, -0.48424)
loop_1 = loop_1.lineTo(0.47079, -0.4731)
loop_1 = loop_1.lineTo(0.48578, -0.46267)
loop_1 = loop_1.lineTo(0.49832, -0.44861)
loop_1 = loop_1.lineTo(0.51055, -0.426)
loop_1 = loop_1.lineTo(0.51054, -0.4071)
loop_1 = loop_1.lineTo(0.50762, -0.39616)
loop_1 = loop_1.lineTo(0.4979, -0.38565)
loop_1 = loop_1.lineTo(0.48465, -0.37794)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_20_interval_0.stl')