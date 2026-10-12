import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.42485, -0.14913)
loop_1 = loop_1.lineTo(0.12231, -0.36494)
loop_1 = loop_1.lineTo(0.18872, -0.38248)
loop_1 = loop_1.threePointArc((0.18925, -0.388), (0.18934, -0.39317))
loop_1 = loop_1.lineTo(0.18937, -0.40729)
loop_1 = loop_1.lineTo(0.10591, -0.38139)
loop_1 = loop_1.lineTo(-0.34758, -0.26436)
loop_1 = loop_1.lineTo(-0.35476, -0.25314)
loop_1 = loop_1.lineTo(-0.02446, -0.32657)
loop_1 = loop_1.lineTo(-0.4157, -0.16249)
loop_1 = loop_1.threePointArc((-0.42031, -0.1558), (-0.42468, -0.14936))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_74_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_74_interval_0.stl')