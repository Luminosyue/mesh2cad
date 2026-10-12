import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07602, 0.91475, -0.06846), normal=(4e-05, -0.99993, 0.01141), xDir=(-1.0, -4e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0782, 0.27598)
loop_1 = loop_1.lineTo(-0.11545, 0.27602)
loop_1 = loop_1.threePointArc((-0.1572, 0.27573), (-0.19252, 0.2751))
loop_1 = loop_1.lineTo(-0.20987, 0.27481)
loop_1 = loop_1.threePointArc((-0.23295, 0.27369), (-0.25115, 0.27295))
loop_1 = loop_1.lineTo(-0.28757, 0.26901)
loop_1 = loop_1.lineTo(-0.29803, 0.26613)
loop_1 = loop_1.lineTo(-0.32171, 0.25295)
loop_1 = loop_1.lineTo(-0.34491, 0.24179)
loop_1 = loop_1.lineTo(0.26091, 0.23676)
loop_1 = loop_1.lineTo(0.21769, 0.25833)
loop_1 = loop_1.lineTo(0.16511, 0.26901)
loop_1 = loop_1.threePointArc((0.0959, 0.27341), (0.03587, 0.27403))
loop_1 = loop_1.lineTo(0.01509, 0.27491)
loop_1 = loop_1.threePointArc((-0.00366, 0.27516), (-0.02319, 0.27588))
loop_1 = loop_1.lineTo(-0.05784, 0.27619)
loop_1 = loop_1.lineTo(-0.0782, 0.27598)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.62)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_28_interval_0.stl')