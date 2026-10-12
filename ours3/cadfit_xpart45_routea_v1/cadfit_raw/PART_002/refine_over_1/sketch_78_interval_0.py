import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.18041, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07817, -0.89503)
loop_1 = loop_1.lineTo(0.13122, -0.89157)
loop_1 = loop_1.lineTo(0.20006, -0.88659)
loop_1 = loop_1.threePointArc((0.21654, -0.88569), (0.23213, -0.88426))
loop_1 = loop_1.lineTo(0.26, -0.88151)
loop_1 = loop_1.lineTo(0.2598, -0.89809)
loop_1 = loop_1.lineTo(-0.00012, -0.89779)
loop_1 = loop_1.threePointArc((0.01396, -0.89734), (0.02843, -0.89731))
loop_1 = loop_1.threePointArc((0.05382, -0.8965), (0.07797, -0.89506))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_78_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_78_interval_0.stl')