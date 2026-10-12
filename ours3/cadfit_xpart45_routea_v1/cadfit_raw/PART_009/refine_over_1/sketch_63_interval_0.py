import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.195, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96474, -0.08238)
loop_1 = loop_1.lineTo(0.96509, 0.03081)
loop_1 = loop_1.lineTo(0.98312, 0.52021)
loop_1 = loop_1.lineTo(0.99342, 0.52021)
loop_1 = loop_1.lineTo(0.99252, -0.11213)
loop_1 = loop_1.lineTo(0.98328, -0.09393)
loop_1 = loop_1.lineTo(0.96509, -0.08258)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_63_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_63_interval_0.stl')