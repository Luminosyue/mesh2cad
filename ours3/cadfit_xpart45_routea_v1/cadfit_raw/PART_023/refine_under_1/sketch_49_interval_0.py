import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.3547, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.64347, -0.96359)
loop_1 = loop_1.lineTo(0.63281, -0.96614)
loop_1 = loop_1.lineTo(0.61044, -0.97315)
loop_1 = loop_1.lineTo(0.58675, -0.97481)
loop_1 = loop_1.lineTo(0.54406, -0.97441)
loop_1 = loop_1.lineTo(0.52641, -0.9741)
loop_1 = loop_1.lineTo(0.50092, -0.9726)
loop_1 = loop_1.lineTo(0.48403, -0.96416)
loop_1 = loop_1.lineTo(0.47305, -0.96)
loop_1 = loop_1.lineTo(0.64989, -0.96)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_49_interval_0.stl')