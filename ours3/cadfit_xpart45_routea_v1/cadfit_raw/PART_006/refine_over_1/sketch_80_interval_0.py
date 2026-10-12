import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52271), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18494, -0.96028)
loop_1 = loop_1.threePointArc((0.23339, -0.94907), (0.27969, -0.93746))
loop_1 = loop_1.threePointArc((0.30793, -0.92665), (0.33455, -0.91589))
loop_1 = loop_1.lineTo(0.38511, -0.89103)
loop_1 = loop_1.lineTo(0.3894, -0.9939)
loop_1 = loop_1.lineTo(0.00835, -0.99329)
loop_1 = loop_1.lineTo(0.06981, -0.98399)
loop_1 = loop_1.lineTo(0.13965, -0.97056)
loop_1 = loop_1.threePointArc((0.16184, -0.96554), (0.18466, -0.96039))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_80_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_80_interval_0.stl')