import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.86, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.46077, -0.24815)
loop_1 = loop_1.threePointArc((-0.38875, -0.24967), (-0.3196, -0.24926))
loop_1 = loop_1.lineTo(-0.24268, -0.25012)
loop_1 = loop_1.lineTo(0.06325, -0.24967)
loop_1 = loop_1.lineTo(0.31242, -0.24909)
loop_1 = loop_1.threePointArc((0.38468, -0.24952), (0.4534, -0.24824))
loop_1 = loop_1.threePointArc((0.49063, -0.2487), (0.52573, -0.24843))
loop_1 = loop_1.lineTo(-0.46011, -0.24825)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_61_interval_0.stl')