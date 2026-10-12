import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.10348, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02958, 0.0212)
loop_1 = loop_1.lineTo(-0.04332, 0.01965)
loop_1 = loop_1.lineTo(-0.0519, 0.00871)
loop_1 = loop_1.lineTo(-0.05702, -0.00227)
loop_1 = loop_1.lineTo(-0.05692, -0.01828)
loop_1 = loop_1.lineTo(-0.0479, -0.03315)
loop_1 = loop_1.lineTo(-0.03738, -0.04602)
loop_1 = loop_1.threePointArc((-0.02625, -0.05539), (-0.02324, -0.05569))
loop_1 = loop_1.lineTo(-0.00588, -0.04515)
loop_1 = loop_1.lineTo(6e-05, -0.03111)
loop_1 = loop_1.lineTo(0.00256, -0.01782)
loop_1 = loop_1.lineTo(0.00049, -0.00427)
loop_1 = loop_1.lineTo(-0.00724, 0.00919)
loop_1 = loop_1.lineTo(-0.02952, 0.02117)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_30_interval_0.stl')