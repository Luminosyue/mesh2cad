import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08188, -0.09446, 0.0013), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12948, -0.18315)
loop_1 = loop_1.lineTo(0.18835, 0.0823)
loop_1 = loop_1.lineTo(0.18809, -0.32911)
loop_1 = loop_1.lineTo(0.18647, -0.30966)
loop_1 = loop_1.lineTo(0.18384, -0.28647)
loop_1 = loop_1.threePointArc((0.18331, -0.27039), (0.18308, -0.25363))
loop_1 = loop_1.lineTo(0.18244, -0.23173)
loop_1 = loop_1.lineTo(0.18069, -0.21937)
loop_1 = loop_1.lineTo(0.17393, -0.2064)
loop_1 = loop_1.lineTo(0.14734, -0.18829)
loop_1 = loop_1.lineTo(0.13676, -0.18506)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_21_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_21_interval_1.stl')