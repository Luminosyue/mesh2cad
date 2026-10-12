import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33036, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96497, 0.13712)
loop_1 = loop_1.lineTo(0.96459, -0.14092)
loop_1 = loop_1.threePointArc((0.96348, -0.12599), (0.96226, -0.11187))
loop_1 = loop_1.threePointArc((0.94551, -0.09432), (0.92946, -0.07782))
loop_1 = loop_1.lineTo(0.9181, -0.06617)
loop_1 = loop_1.lineTo(0.90389, -0.05959)
loop_1 = loop_1.threePointArc((0.8974, -0.05315), (0.89118, -0.04623))
loop_1 = loop_1.lineTo(0.86627, -0.0188)
loop_1 = loop_1.lineTo(0.86233, -0.00786)
loop_1 = loop_1.threePointArc((0.86733, -0.00173), (0.87289, 0.00405))
loop_1 = loop_1.lineTo(0.91304, 0.04631)
loop_1 = loop_1.threePointArc((0.91834, 0.05287), (0.92267, 0.05946))
loop_1 = loop_1.lineTo(0.94845, 0.09717)
loop_1 = loop_1.lineTo(0.96489, 0.13692)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_62_interval_0.stl')