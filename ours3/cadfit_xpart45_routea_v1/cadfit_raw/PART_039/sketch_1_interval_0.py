import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.15935, -0.14249, -0.00242), normal=(-0.00336, -0.99999, 0.00101), xDir=(-0.99999, 0.00336, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77261, 0.05426)
loop_1 = loop_1.lineTo(0.78408, 0.05443)
loop_1 = loop_1.lineTo(0.77317, 0.09311)
loop_1 = loop_1.lineTo(0.77261, 0.05426)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_1_interval_0.stl')