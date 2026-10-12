import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00184, -0.05134, 0.33899), normal=(0.00157, -0.00963, -0.99995), xDir=(0.0, -0.99995, 0.00963))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87112, 0.10875)
loop_1 = loop_1.lineTo(-0.83839, 0.11464)
loop_1 = loop_1.lineTo(-0.82397, 0.12046)
loop_1 = loop_1.lineTo(-0.77856, 0.10022)
loop_1 = loop_1.lineTo(-0.77501, 0.0791)
loop_1 = loop_1.lineTo(-0.77252, 0.05126)
loop_1 = loop_1.lineTo(-0.79627, 0.02356)
loop_1 = loop_1.lineTo(-0.82397, 0.00613)
loop_1 = loop_1.lineTo(-0.87293, 0.03452)
loop_1 = loop_1.lineTo(-0.88857, 0.05126)
loop_1 = loop_1.lineTo(-0.88599, 0.06432)
loop_1 = loop_1.lineTo(-0.88362, 0.09843)
loop_1 = loop_1.lineTo(-0.87112, 0.10875)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_0_interval_0.stl')