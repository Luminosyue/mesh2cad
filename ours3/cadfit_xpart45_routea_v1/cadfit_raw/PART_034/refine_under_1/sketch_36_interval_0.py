import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.85379, -0.33643, 0.05117), normal=(0.96693, 0.25502, -0.00123), xDir=(0.25502, -0.96694, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28765, -0.18322)
loop_1 = loop_1.lineTo(-0.30727, -0.18322)
loop_1 = loop_1.lineTo(-0.30317, 0.20678)
loop_1 = loop_1.lineTo(0.29109, 0.20678)
loop_1 = loop_1.lineTo(0.28774, -0.17334)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_36_interval_0.stl')