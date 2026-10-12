import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.51664), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.36646, -0.9186)
loop_1 = loop_1.lineTo(-0.35354, -0.92336)
loop_1 = loop_1.lineTo(-0.31963, -0.9361)
loop_1 = loop_1.lineTo(-0.2668, -0.95108)
loop_1 = loop_1.lineTo(-0.21587, -0.96181)
loop_1 = loop_1.threePointArc((-0.15687, -0.97008), (-0.10038, -0.97652))
loop_1 = loop_1.lineTo(-0.06069, -0.97975)
loop_1 = loop_1.lineTo(-0.48, -0.97881)
loop_1 = loop_1.lineTo(-0.47937, -0.86931)
loop_1 = loop_1.lineTo(-0.36525, -0.91885)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_87_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_87_interval_0.stl')