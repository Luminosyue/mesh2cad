import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05097, -0.10074, 0.06446), normal=(-0.0, -0.54698, 0.83714), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13557, -0.05695)
loop_1 = loop_1.lineTo(0.13263, -0.06797)
loop_1 = loop_1.lineTo(0.11769, -0.06828)
loop_1 = loop_1.lineTo(0.1058, -0.07124)
loop_1 = loop_1.lineTo(0.09509, -0.0797)
loop_1 = loop_1.threePointArc((0.08575, -0.09576), (0.08315, -0.10231))
loop_1 = loop_1.lineTo(0.0808, -0.11948)
loop_1 = loop_1.lineTo(0.07731, -0.13524)
loop_1 = loop_1.lineTo(0.146, -0.13026)
loop_1 = loop_1.lineTo(0.14201, -0.11948)
loop_1 = loop_1.lineTo(0.14171, -0.1049)
loop_1 = loop_1.lineTo(0.13702, -0.08514)
loop_1 = loop_1.lineTo(0.13557, -0.05695)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_35_interval_0.stl')