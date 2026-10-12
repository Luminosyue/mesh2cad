import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26406, -0.23852, 0.65286), normal=(-0.23256, 0.00054, 0.97258), xDir=(0.0, 1.0, -0.00056))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12984, 0.52903)
loop_1 = loop_1.lineTo(-0.20171, 0.52836)
loop_1 = loop_1.lineTo(-0.16605, 0.52576)
loop_1 = loop_1.threePointArc((-0.14575, 0.52321), (-0.12962, 0.52119))
loop_1 = loop_1.threePointArc((-0.11225, 0.51966), (-0.09794, 0.51827))
loop_1 = loop_1.threePointArc((-0.03748, 0.50832), (0.01611, 0.50003))
loop_1 = loop_1.lineTo(0.04305, 0.49758)
loop_1 = loop_1.threePointArc((0.07137, 0.49382), (0.09559, 0.49113))
loop_1 = loop_1.lineTo(0.12993, 0.48707)
loop_1 = loop_1.lineTo(0.12985, 0.52495)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_23_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_23_interval_1.stl')