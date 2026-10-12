import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.15442, -0.04257, -0.01878), normal=(0.92918, -0.36963, 0.00122), xDir=(-0.36963, -0.92918, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17685, 0.19809)
loop_1 = loop_1.lineTo(-0.13513, 0.18577)
loop_1 = loop_1.lineTo(-0.13795, 0.15575)
loop_1 = loop_1.lineTo(-0.12023, 0.15888)
loop_1 = loop_1.lineTo(-0.0869, 0.16684)
loop_1 = loop_1.lineTo(-0.0748, 0.16869)
loop_1 = loop_1.lineTo(-0.05958, 0.17031)
loop_1 = loop_1.lineTo(-0.0443, 0.17475)
loop_1 = loop_1.threePointArc((-0.0204, 0.17439), (0.00084, 0.17404))
loop_1 = loop_1.lineTo(0.03211, 0.16926)
loop_1 = loop_1.lineTo(0.08164, 0.16737)
loop_1 = loop_1.lineTo(0.13113, 0.15701)
loop_1 = loop_1.lineTo(0.16359, 0.1524)
loop_1 = loop_1.lineTo(0.18141, 0.148)
loop_1 = loop_1.lineTo(0.1773, 0.19443)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.01)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_19_interval_1.stl')