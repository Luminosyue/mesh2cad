import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01542, -0.01803, 0.20034), normal=(-0.00113, -0.28094, -0.95972), xDir=(0.0, -0.95973, 0.28094))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11907, 0.00689)
loop_1 = loop_1.lineTo(-0.10699, 0.00645)
loop_1 = loop_1.lineTo(-0.08554, -0.01992)
loop_1 = loop_1.lineTo(-0.09586, -0.02548)
loop_1 = loop_1.lineTo(-0.11907, 0.00689)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_24_interval_0.stl')