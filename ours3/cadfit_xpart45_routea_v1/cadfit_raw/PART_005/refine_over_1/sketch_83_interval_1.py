import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19529, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.83394, 0.1374)
loop_1 = loop_1.lineTo(-0.82643, 0.09873)
loop_1 = loop_1.lineTo(-0.80433, 0.04742)
loop_1 = loop_1.lineTo(-0.75618, 0.0003)
loop_1 = loop_1.lineTo(-0.7613, -0.05574)
loop_1 = loop_1.lineTo(-0.79974, -0.07566)
loop_1 = loop_1.lineTo(-0.81023, -0.0848)
loop_1 = loop_1.lineTo(-0.82873, -0.10785)
loop_1 = loop_1.lineTo(-0.83394, -0.14881)
loop_1 = loop_1.lineTo(-0.83394, 0.13719)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_83_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_83_interval_1.stl')