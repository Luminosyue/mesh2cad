import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06535, 0.0319, 0.12444), normal=(0.01655, -0.45879, -0.88839), xDir=(-0.99935, -0.03605, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.44554, -0.06568)
loop_1 = loop_1.lineTo(0.52287, -0.06588)
loop_1 = loop_1.lineTo(0.51672, -0.08156)
loop_1 = loop_1.lineTo(0.50987, -0.09658)
loop_1 = loop_1.lineTo(0.4952, -0.11238)
loop_1 = loop_1.lineTo(0.48087, -0.11382)
loop_1 = loop_1.lineTo(0.44554, -0.06568)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_25_interval_0.stl')