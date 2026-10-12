import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3445, -0.10282, 0.0596), normal=(-0.0365, 0.8948, 0.44498), xDir=(0.99917, 0.04075, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10092, 0.01959)
loop_1 = loop_1.lineTo(-0.07043, -0.00382)
loop_1 = loop_1.threePointArc((-0.06295, -0.00725), (-0.05798, -0.00865))
loop_1 = loop_1.lineTo(-0.02963, -0.01186)
loop_1 = loop_1.lineTo(-0.01957, -0.01201)
loop_1 = loop_1.lineTo(-0.0172, 0.00537)
loop_1 = loop_1.threePointArc((-0.01657, 0.0128), (-0.01609, 0.01887))
loop_1 = loop_1.lineTo(-0.04799, 0.01383)
loop_1 = loop_1.lineTo(-0.05865, 0.01451)
loop_1 = loop_1.lineTo(-0.10092, 0.01959)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_7_interval_0.stl')