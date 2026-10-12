import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31235, 0.91072, 0.319), normal=(0.28698, -0.95793, 0.00292), xDir=(-0.95794, -0.28698, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23654, 0.28078)
loop_1 = loop_1.lineTo(0.17665, 0.24496)
loop_1 = loop_1.lineTo(0.21605, 0.23798)
loop_1 = loop_1.lineTo(0.23328, 0.23348)
loop_1 = loop_1.lineTo(0.23655, 0.28077)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_18_interval_0.stl')