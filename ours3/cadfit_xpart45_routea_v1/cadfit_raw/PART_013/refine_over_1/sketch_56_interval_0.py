import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21028), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58557, -0.55731)
loop_1 = loop_1.lineTo(0.63228, -0.55719)
loop_1 = loop_1.lineTo(0.63216, -0.50283)
loop_1 = loop_1.lineTo(0.60821, -0.53536)
loop_1 = loop_1.lineTo(0.5868, -0.55606)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_56_interval_0.stl')