import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.74, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88603, -0.27711)
loop_1 = loop_1.lineTo(0.88484, -0.28378)
loop_1 = loop_1.threePointArc((0.87552, -0.29387), (0.86402, -0.29988))
loop_1 = loop_1.lineTo(0.82579, -0.31561)
loop_1 = loop_1.threePointArc((0.61254, -0.31852), (0.409, -0.32254))
loop_1 = loop_1.lineTo(0.02443, -0.32061)
loop_1 = loop_1.threePointArc((-0.12472, -0.32094), (-0.27883, -0.31868))
loop_1 = loop_1.threePointArc((-0.44616, -0.31925), (-0.61918, -0.31613))
loop_1 = loop_1.lineTo(-0.83746, -0.31302)
loop_1 = loop_1.threePointArc((-0.85993, -0.29895), (-0.88182, -0.28424))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_54_interval_0.stl')