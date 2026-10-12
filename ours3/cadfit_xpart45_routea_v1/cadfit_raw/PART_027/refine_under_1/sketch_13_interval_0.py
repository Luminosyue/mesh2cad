import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30766, 0.40906, -0.12271), normal=(0.00024, -0.99531, -0.09677), xDir=(-1.0, -0.00024, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04419, 0.08554)
loop_1 = loop_1.threePointArc((-0.03249, 0.0844), (-0.02126, 0.08333))
loop_1 = loop_1.lineTo(-0.00537, 0.07951)
loop_1 = loop_1.lineTo(0.04286, 0.06499)
loop_1 = loop_1.lineTo(0.05323, 0.0594)
loop_1 = loop_1.lineTo(0.02532, 0.0556)
loop_1 = loop_1.threePointArc((0.00615, 0.05557), (-0.0107, 0.05527))
loop_1 = loop_1.threePointArc((-0.03449, 0.05559), (-0.05042, 0.05539))
loop_1 = loop_1.threePointArc((-0.06589, 0.05541), (-0.08026, 0.05554))
loop_1 = loop_1.lineTo(-0.08873, 0.06605)
loop_1 = loop_1.lineTo(-0.07286, 0.07673)
loop_1 = loop_1.lineTo(-0.04443, 0.08552)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_13_interval_0.stl')