import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.70104, -0.61908, -0.11846), normal=(0.77402, -0.63316, 0.00043), xDir=(-0.63316, -0.77402, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.32824, 0.01684)
loop_1 = loop_1.lineTo(-0.31654, -0.0015)
loop_1 = loop_1.lineTo(-0.30409, -0.01855)
loop_1 = loop_1.threePointArc((-0.27811, -0.03404), (-0.25639, -0.04697))
loop_1 = loop_1.lineTo(-0.23848, -0.05641)
loop_1 = loop_1.lineTo(-0.2062, -0.07038)
loop_1 = loop_1.lineTo(-0.19262, -0.074)
loop_1 = loop_1.lineTo(-0.18779, -0.19085)
loop_1 = loop_1.lineTo(-0.23855, -0.19626)
loop_1 = loop_1.lineTo(-0.25633, -0.20322)
loop_1 = loop_1.lineTo(-0.27239, -0.21352)
loop_1 = loop_1.lineTo(-0.31615, -0.22588)
loop_1 = loop_1.lineTo(-0.32044, -0.23721)
loop_1 = loop_1.lineTo(-0.32863, -0.26455)
loop_1 = loop_1.lineTo(-0.32824, 0.01319)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_39_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_39_interval_1.stl')