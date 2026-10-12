import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0187, 0.21376, 0.10574), normal=(-0.43912, 4e-05, -0.89843), xDir=(9e-05, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95916, 0.03706)
loop_1 = loop_1.threePointArc((-0.94876, 0.03693), (-0.93794, 0.03632))
loop_1 = loop_1.lineTo(-0.97502, -0.01505)
loop_1 = loop_1.threePointArc((-0.97813, -0.00643), (-0.98121, 0.0018))
loop_1 = loop_1.threePointArc((-0.98347, 0.01118), (-0.98445, 0.01623))
loop_1 = loop_1.lineTo(-0.95916, 0.03706)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_3_interval_0.stl')