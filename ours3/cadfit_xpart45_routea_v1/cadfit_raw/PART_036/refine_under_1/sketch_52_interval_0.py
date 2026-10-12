import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.17678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22912, 0.07741)
loop_1 = loop_1.lineTo(-0.27271, 0.07754)
loop_1 = loop_1.lineTo(-0.27271, 0.11291)
loop_1 = loop_1.lineTo(-0.27264, 0.12677)
loop_1 = loop_1.lineTo(-0.23049, 0.13091)
loop_1 = loop_1.lineTo(-0.22955, 0.10094)
loop_1 = loop_1.threePointArc((-0.22949, 0.09566), (-0.22931, 0.09067))
loop_1 = loop_1.lineTo(-0.22906, 0.07771)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_52_interval_0.stl')