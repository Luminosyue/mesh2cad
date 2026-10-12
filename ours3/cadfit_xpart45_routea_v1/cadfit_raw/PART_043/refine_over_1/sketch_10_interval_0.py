import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02496, 0.10549, 0.10187), normal=(-0.39233, 0.9192, 0.034), xDir=(0.91973, 0.39255, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.4102, 0.31363)
loop_1 = loop_1.lineTo(1.03914, 0.73863)
loop_1 = loop_1.lineTo(0.99877, 0.71983)
loop_1 = loop_1.threePointArc((0.98606, 0.71437), (0.98171, 0.71078))
loop_1 = loop_1.lineTo(0.93189, 0.69041)
loop_1 = loop_1.lineTo(0.9183, 0.68306)
loop_1 = loop_1.threePointArc((0.89456, 0.67408), (0.87376, 0.66564))
loop_1 = loop_1.lineTo(0.41, 0.31467)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_10_interval_0.stl')