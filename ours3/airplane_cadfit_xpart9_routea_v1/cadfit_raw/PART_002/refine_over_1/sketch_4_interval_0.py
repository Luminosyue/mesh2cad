import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.24572, 0.07972, -0.11578), normal=(-0.02537, -0.89013, 0.45501), xDir=(-0.99959, 0.02849, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82386, -0.07133)
loop_1 = loop_1.lineTo(0.76941, -0.09229)
loop_1 = loop_1.lineTo(0.87004, -0.08598)
loop_1 = loop_1.lineTo(0.84901, -0.07565)
loop_1 = loop_1.lineTo(0.83803, -0.0682)
loop_1 = loop_1.lineTo(0.82386, -0.07133)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_4_interval_0.stl')