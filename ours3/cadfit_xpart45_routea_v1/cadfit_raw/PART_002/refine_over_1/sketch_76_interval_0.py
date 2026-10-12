import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.29041, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.49285, -0.77616)
loop_1 = loop_1.lineTo(-0.48403, -0.81)
loop_1 = loop_1.lineTo(-0.5338, -0.80978)
loop_1 = loop_1.lineTo(-0.53336, -0.50745)
loop_1 = loop_1.lineTo(-0.51095, -0.69432)
loop_1 = loop_1.lineTo(-0.50582, -0.71333)
loop_1 = loop_1.threePointArc((-0.501, -0.73616), (-0.49612, -0.7578))
loop_1 = loop_1.lineTo(-0.49285, -0.77616)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_76_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_76_interval_0.stl')