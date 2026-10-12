import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.80577, -0.07515, -0.15258), normal=(0.09586, 0.00018, 0.99539), xDir=(0.0, 1.0, -0.00019))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02881, -0.09748)
loop_1 = loop_1.lineTo(0.05116, -0.09795)
loop_1 = loop_1.lineTo(-0.22059, -0.06046)
loop_1 = loop_1.lineTo(-0.20894, -0.06438)
loop_1 = loop_1.lineTo(-0.19642, -0.06783)
loop_1 = loop_1.lineTo(-0.15032, -0.07841)
loop_1 = loop_1.lineTo(-0.13731, -0.08006)
loop_1 = loop_1.lineTo(-0.08894, -0.08716)
loop_1 = loop_1.lineTo(-0.0739, -0.08888)
loop_1 = loop_1.lineTo(-0.05799, -0.09193)
loop_1 = loop_1.threePointArc((-0.03798, -0.09382), (-0.02146, -0.09492))
loop_1 = loop_1.threePointArc((-0.00358, -0.09616), (0.01092, -0.09709))
loop_1 = loop_1.lineTo(0.02588, -0.09741)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_56_interval_0.stl')