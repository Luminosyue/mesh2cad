import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01652, 0.08029, -0.03694), normal=(-0.49219, 0.00036, 0.87049), xDir=(0.00073, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9783, 0.03261)
loop_1 = loop_1.threePointArc((-0.98518, 0.03231), (-0.99179, 0.03189))
loop_1 = loop_1.lineTo(-1.00433, 0.03069)
loop_1 = loop_1.lineTo(-1.02817, 0.0297)
loop_1 = loop_1.lineTo(-1.07496, 0.0209)
loop_1 = loop_1.threePointArc((-1.0773, 0.00933), (-1.07935, -0.0018))
loop_1 = loop_1.lineTo(-1.07025, -0.04632)
loop_1 = loop_1.lineTo(-1.05875, -0.04772)
loop_1 = loop_1.lineTo(-1.03575, -0.04435)
loop_1 = loop_1.threePointArc((-1.02442, -0.04337), (-1.01572, -0.04249))
loop_1 = loop_1.lineTo(-0.98471, -0.04072)
loop_1 = loop_1.lineTo(-0.91744, -0.02149)
loop_1 = loop_1.lineTo(-0.90627, -0.0218)
loop_1 = loop_1.lineTo(-0.9551, 0.02122)
loop_1 = loop_1.lineTo(-0.96679, 0.02835)
loop_1 = loop_1.lineTo(-0.9783, 0.03261)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_7_interval_0.stl')