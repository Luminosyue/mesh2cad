import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.82783, -0.26227, -0.00585), normal=(-0.98753, 0.15743, 0.00282), xDir=(0.15743, 0.98753, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2825, 0.14347)
loop_1 = loop_1.lineTo(-0.28314, 0.06556)
loop_1 = loop_1.threePointArc((-0.27951, 0.08139), (-0.27581, 0.09675))
loop_1 = loop_1.threePointArc((-0.26345, 0.1136), (-0.25391, 0.12292))
loop_1 = loop_1.lineTo(-0.24145, 0.13535)
loop_1 = loop_1.lineTo(-0.28141, 0.14347)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_18_interval_0.stl')