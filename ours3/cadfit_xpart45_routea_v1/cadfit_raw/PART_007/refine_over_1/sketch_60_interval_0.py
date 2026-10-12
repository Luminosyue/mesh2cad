import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.45723), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.92428, 0.5558)
loop_1 = loop_1.lineTo(-0.94992, 0.54302)
loop_1 = loop_1.lineTo(-0.98233, 0.46283)
loop_1 = loop_1.lineTo(-0.98218, 0.47997)
loop_1 = loop_1.lineTo(-0.9862, 0.45214)
loop_1 = loop_1.lineTo(-0.98974, 0.55582)
loop_1 = loop_1.lineTo(-0.9243, 0.55582)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_60_interval_0.stl')