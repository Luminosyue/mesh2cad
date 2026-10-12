import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.62169, -0.01888, -0.37234), normal=(0.20985, -2e-05, 0.97773), xDir=(-0.0, 1.0, 2e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03702, 0.84633)
loop_1 = loop_1.lineTo(0.10356, 0.84633)
loop_1 = loop_1.threePointArc((0.10366, 0.83754), (0.10358, 0.83009))
loop_1 = loop_1.lineTo(0.10098, 0.81182)
loop_1 = loop_1.lineTo(0.09179, 0.79862)
loop_1 = loop_1.lineTo(0.08175, 0.78956)
loop_1 = loop_1.lineTo(0.04766, 0.78834)
loop_1 = loop_1.lineTo(0.0356, 0.79646)
loop_1 = loop_1.lineTo(0.02705, 0.80941)
loop_1 = loop_1.lineTo(0.03012, 0.83629)
loop_1 = loop_1.lineTo(0.03702, 0.84632)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_36_interval_0.stl')