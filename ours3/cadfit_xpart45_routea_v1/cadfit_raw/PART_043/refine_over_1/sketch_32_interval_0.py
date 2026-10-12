import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13046, 0.18789, -0.22), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.60409, 0.44447)
loop_1 = loop_1.lineTo(-0.81878, 0.69637)
loop_1 = loop_1.lineTo(-0.52514, 0.39852)
loop_1 = loop_1.lineTo(-0.54574, 0.37821)
loop_1 = loop_1.lineTo(-0.58465, 0.42233)
loop_1 = loop_1.lineTo(-0.60108, 0.44105)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_32_interval_0.stl')