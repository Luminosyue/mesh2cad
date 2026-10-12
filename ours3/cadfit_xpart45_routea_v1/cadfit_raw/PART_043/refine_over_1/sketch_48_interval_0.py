import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.31609, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50521, 0.00616)
loop_1 = loop_1.lineTo(0.03345, 0.0762)
loop_1 = loop_1.threePointArc((0.04495, 0.0759), (0.05508, 0.07725))
loop_1 = loop_1.threePointArc((0.07681, 0.07773), (0.09662, 0.08053))
loop_1 = loop_1.lineTo(0.12389, 0.08542)
loop_1 = loop_1.lineTo(0.14527, 0.09182)
loop_1 = loop_1.threePointArc((0.16031, 0.09541), (0.17432, 0.1002))
loop_1 = loop_1.lineTo(0.18399, 0.12316)
loop_1 = loop_1.lineTo(0.60793, 0.37636)
loop_1 = loop_1.lineTo(-0.10935, 0.14)
loop_1 = loop_1.lineTo(-0.51508, 0.1383)
loop_1 = loop_1.lineTo(-0.51432, 0.00055)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_48_interval_0.stl')