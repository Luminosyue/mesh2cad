import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.18026, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.882, 0.14461)
loop_1 = loop_1.lineTo(-0.88492, 0.11618)
loop_1 = loop_1.lineTo(-0.8865, 0.10326)
loop_1 = loop_1.threePointArc((-0.88725, 0.06202), (-0.88847, 0.01922))
loop_1 = loop_1.threePointArc((-0.89065, -0.01533), (-0.89252, -0.03909))
loop_1 = loop_1.lineTo(-0.89398, -0.06878)
loop_1 = loop_1.lineTo(-0.89338, 0.14461)
loop_1 = loop_1.lineTo(-0.88215, 0.14461)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_45_interval_0.stl')