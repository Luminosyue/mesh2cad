import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0995, -0.06915, 0.09541), normal=(-0.39233, 0.9192, 0.034), xDir=(0.91973, 0.39255, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27353, 0.1061)
loop_1 = loop_1.lineTo(0.27519, -0.00406)
loop_1 = loop_1.lineTo(0.11723, -0.00406)
loop_1 = loop_1.threePointArc((0.11706, 0.00442), (0.11696, 0.01093))
loop_1 = loop_1.threePointArc((0.13173, 0.01977), (0.14471, 0.02792))
loop_1 = loop_1.lineTo(0.15658, 0.03488)
loop_1 = loop_1.lineTo(0.18069, 0.04981)
loop_1 = loop_1.lineTo(0.20279, 0.06436)
loop_1 = loop_1.lineTo(0.21279, 0.06996)
loop_1 = loop_1.lineTo(0.24296, 0.08731)
loop_1 = loop_1.threePointArc((0.25303, 0.09376), (0.26087, 0.09888))
loop_1 = loop_1.lineTo(0.27353, 0.1061)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_13_interval_0.stl')