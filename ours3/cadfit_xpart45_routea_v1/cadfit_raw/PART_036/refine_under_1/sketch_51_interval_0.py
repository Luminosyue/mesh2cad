import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.20678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12506, 0.13432)
loop_1 = loop_1.lineTo(-0.16053, 0.13309)
loop_1 = loop_1.lineTo(-0.15975, 0.10797)
loop_1 = loop_1.threePointArc((-0.15954, 0.09655), (-0.15938, 0.0907))
loop_1 = loop_1.lineTo(-0.15825, 0.07741)
loop_1 = loop_1.lineTo(-0.11848, 0.07754)
loop_1 = loop_1.lineTo(-0.1186, 0.12365)
loop_1 = loop_1.threePointArc((-0.12458, 0.12966), (-0.12507, 0.13425))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_51_interval_0.stl')