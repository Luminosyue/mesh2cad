import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00507, 0.99045, -0.00519), normal=(0.0033, -0.99999, 0.00312), xDir=(-0.99999, -0.0033, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0042, 0.04492)
loop_1 = loop_1.threePointArc((-0.00913, 0.04412), (-0.01429, 0.04337))
loop_1 = loop_1.lineTo(-0.03832, 0.02687)
loop_1 = loop_1.threePointArc((-0.04218, 0.02186), (-0.04631, 0.01672))
loop_1 = loop_1.threePointArc((-0.04731, 0.01011), (-0.04799, 0.00522))
loop_1 = loop_1.threePointArc((-0.04767, -0.00119), (-0.04752, -0.00628))
loop_1 = loop_1.threePointArc((-0.0451, -0.0127), (-0.04322, -0.01779))
loop_1 = loop_1.lineTo(-0.02451, -0.03593)
loop_1 = loop_1.lineTo(-0.01276, -0.04215)
loop_1 = loop_1.lineTo(-0.00127, -0.04381)
loop_1 = loop_1.lineTo(0.01023, -0.04371)
loop_1 = loop_1.lineTo(0.03172, -0.0358)
loop_1 = loop_1.lineTo(0.04423, -0.02475)
loop_1 = loop_1.lineTo(0.01878, 0.04327)
loop_1 = loop_1.threePointArc((0.01385, 0.04416), (0.00871, 0.04511))
loop_1 = loop_1.lineTo(-0.0042, 0.04492)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_12_interval_0.stl')